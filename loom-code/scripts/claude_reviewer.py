#!/usr/bin/env python3
"""Run one observable Claude Code reviewer attempt.

The caller owns reviewer prompt construction, verdict validation, and the
Closing Review retry. This module owns only one subprocess boundary so empty
stdout and timeout cannot be mistaken for a successful reviewer result.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from typing import TextIO


CLAUDE_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
UNRECOGNIZED_MODEL_MARKER = "[claude-code:unrecognized_model]"


@dataclass(frozen=True)
class Attempt:
    kind: str
    stdout: str
    stderr: str
    returncode: int | None
    elapsed_seconds: float
    exit_code: int


def _text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _validate_profile(model: str | None, effort: str | None) -> None:
    if (model is None) != (effort is None):
        raise ValueError("--model and --effort must be provided together")
    if effort is not None and effort not in CLAUDE_EFFORTS:
        raise ValueError(f"unsupported --effort value: {effort}")


def _argv(claude_bin: str, model: str | None, effort: str | None) -> list[str]:
    """Build the grounded Claude print-mode invocation.

    External surface grounding: the checked-in ``claude -p --help`` capture at
    ``docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/claude-p-help-2026-09-05.txt``
    defines ``-p``, ``--model``, ``--effort`` and ``--output-format text``.
    Anthropic's
    CLI reference documents ``--no-session-persistence`` as disabling disk
    persistence for print-mode sessions:
    https://code.claude.com/docs/en/cli-usage
    Prompt delivery on stdin follows the empirical contract documented by
    ``coldread_role_split.run_once``.
    """
    _validate_profile(model, effort)
    argv = [claude_bin, "-p"]
    if model is not None and effort is not None:
        argv.extend(["--model", model, "--effort", effort])
    return argv + ["--output-format", "text", "--no-session-persistence"]


def _completed_attempt(completed: subprocess.CompletedProcess[str], elapsed: float) -> Attempt:
    if completed.returncode != 0:
        kind = (
            "host-rejection"
            if UNRECOGNIZED_MODEL_MARKER in completed.stderr
            else "process-error"
        )
        exit_code = 4 if kind == "host-rejection" else 1
        return Attempt(
            kind, completed.stdout, completed.stderr,
            completed.returncode, elapsed, exit_code,
        )
    if not completed.stdout.strip():
        return Attempt(
            "empty-output", completed.stdout, completed.stderr,
            completed.returncode, elapsed, 3,
        )
    return Attempt(
        "success", completed.stdout, completed.stderr,
        completed.returncode, elapsed, 0,
    )


def run_attempt(
    claude_bin: str,
    model: str | None,
    effort: str | None,
    prompt: str,
    timeout: int,
) -> Attempt:
    """Execute Claude once; never retry or interpret reviewer content."""
    argv = _argv(claude_bin, model, effort)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            argv,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return Attempt(
            kind="timeout",
            stdout=_text(exc.stdout or exc.output),
            stderr=_text(exc.stderr),
            returncode=None,
            elapsed_seconds=time.monotonic() - started,
            exit_code=124,
        )
    except OSError as exc:
        return Attempt(
            kind="process-error",
            stdout="",
            stderr=str(exc),
            returncode=None,
            elapsed_seconds=time.monotonic() - started,
            exit_code=1,
        )
    return _completed_attempt(completed, time.monotonic() - started)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model")
    parser.add_argument("--effort")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    return parser


def main(
    argv: list[str] | None = None,
    *,
    stdin: TextIO = sys.stdin,
    out: TextIO = sys.stdout,
    err: TextIO = sys.stderr,
) -> int:
    args = _parser().parse_args(argv)
    if args.timeout_seconds <= 0:
        print("--timeout-seconds must be greater than zero", file=err)
        return 2
    try:
        _validate_profile(args.model, args.effort)
    except ValueError as exc:
        invalid = Attempt(
            kind="input-error",
            stdout="",
            stderr=str(exc),
            returncode=None,
            elapsed_seconds=0.0,
            exit_code=2,
        )
        print(json.dumps(asdict(invalid), ensure_ascii=False, sort_keys=True), file=err)
        return invalid.exit_code
    attempt = run_attempt(
        "claude",
        args.model,
        args.effort,
        stdin.read(),
        args.timeout_seconds,
    )
    if attempt.kind == "success":
        out.write(attempt.stdout)
        err.write(attempt.stderr)
        return 0
    print(json.dumps(asdict(attempt), ensure_ascii=False, sort_keys=True), file=err)
    return attempt.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
