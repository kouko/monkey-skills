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


def _argv(claude_bin: str, model: str) -> list[str]:
    return [
        claude_bin,
        "-p",
        "--model",
        model,
        "--output-format",
        "text",
        "--no-session-persistence",
    ]


def run_attempt(claude_bin: str, model: str, prompt: str, timeout: int) -> Attempt:
    """Execute Claude once; never retry or interpret reviewer content."""
    argv = _argv(claude_bin, model)
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

    elapsed = time.monotonic() - started
    if completed.returncode != 0:
        return Attempt(
            kind="process-error",
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
            elapsed_seconds=elapsed,
            exit_code=completed.returncode or 1,
        )
    if not completed.stdout.strip():
        return Attempt(
            kind="empty-output",
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
            elapsed_seconds=elapsed,
            exit_code=3,
        )
    return Attempt(
        kind="success",
        stdout=completed.stdout,
        stderr=completed.stderr,
        returncode=completed.returncode,
        elapsed_seconds=elapsed,
        exit_code=0,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--model", default="sonnet")
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
    attempt = run_attempt(
        args.claude_bin,
        args.model,
        stdin.read(),
        args.timeout_seconds,
    )
    if attempt.kind == "success":
        out.write(attempt.stdout)
        return 0
    print(json.dumps(asdict(attempt), ensure_ascii=False, sort_keys=True), file=err)
    return attempt.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
