#!/usr/bin/env python3
"""Wait, with a bounded and machine-readable contract, for PR checks."""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import time
from collections.abc import Callable
from typing import Any


EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_TIMEOUT = 2
EXIT_NO_CHECKS = 3
EXIT_OPERATIONAL_ERROR = 4
EXIT_HEAD_DRIFT = 5
EXIT_CANCELLED = 6
EXIT_ARGUMENT_ERROR = 7

_PASS_BUCKETS = {"pass", "skipping"}
_FAIL_BUCKETS = {"fail"}
_PENDING_BUCKETS = {"pending", "queued", "in_progress", "waiting"}
_CANCEL_BUCKETS = {"cancel", "cancelled"}
_NO_CHECKS_ERROR = re.compile(r"no checks reported on the '.+' branch")


def _result(status: str, exit_code: int, expected_head: str, **extra: Any) -> dict[str, Any]:
    return {
        "status": status,
        "exit_code": exit_code,
        "expected_head": expected_head,
        **extra,
    }


def _run_gh(
    run: Callable[..., subprocess.CompletedProcess[str]], command: list[str],
    timeout: float, *, allow_pending_exit: bool = False, allow_no_checks: bool = False,
) -> tuple[Any | None, str | None]:
    try:
        completed = run(command, timeout=timeout)
    except OSError as exc:
        return None, str(exc)
    if completed.returncode != 0 and not (
        allow_pending_exit and completed.returncode == 8
    ):
        if allow_no_checks and _NO_CHECKS_ERROR.fullmatch(completed.stderr.strip()):
            return [], None
        return None, completed.stderr.strip() or f"gh exited {completed.returncode}"
    try:
        return json.loads(completed.stdout), None
    except json.JSONDecodeError as exc:
        return None, f"invalid gh JSON: {exc.msg}"


def _classify_checks(checks: list[Any], expected_head: str) -> dict[str, Any] | None:
    if not all(isinstance(item, dict) and isinstance(item.get("bucket"), str) for item in checks):
        return _result("operational_error", EXIT_OPERATIONAL_ERROR, expected_head, error="gh returned checks without string buckets")
    buckets = {item["bucket"] for item in checks}
    if buckets & _CANCEL_BUCKETS:
        return _result("cancelled", EXIT_CANCELLED, expected_head, checks=checks)
    if buckets & _FAIL_BUCKETS:
        return _result("fail", EXIT_FAIL, expected_head, checks=checks)
    if buckets <= _PASS_BUCKETS:
        return _result("pass", EXIT_PASS, expected_head, checks=checks)
    unknown = buckets - _PASS_BUCKETS - _FAIL_BUCKETS - _PENDING_BUCKETS - _CANCEL_BUCKETS
    if unknown:
        return _result("operational_error", EXIT_OPERATIONAL_ERROR, expected_head, error=f"unknown check buckets: {sorted(unknown)}")
    return None


def _validate_timing(*values: float) -> None:
    if not all(math.isfinite(value) for value in values) or values[0] < 0 or values[1] <= 0 or values[2] < 0:
        raise ValueError("timeout and grace must be non-negative; poll interval must be positive")


def _default_run(command: list[str], *, timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def _timeout(expected_head: str, started: float, now: Callable[[], float]) -> dict[str, Any]:
    return _result("timeout", EXIT_TIMEOUT, expected_head, elapsed_seconds=now() - started)


def _read_current_head(
    run: Callable[..., subprocess.CompletedProcess[str]], pr: str,
    expected_head: str, remaining: float,
) -> dict[str, Any] | None:
    head, error = _run_gh(run, ["gh", "pr", "view", pr, "--json", "headRefOid"], remaining)
    if error:
        return _result("operational_error", EXIT_OPERATIONAL_ERROR, expected_head, error=error)
    observed_head = head.get("headRefOid") if isinstance(head, dict) else None
    if not isinstance(observed_head, str):
        return _result("operational_error", EXIT_OPERATIONAL_ERROR, expected_head, error="gh returned no headRefOid")
    if observed_head != expected_head:
        return _result("head_drift", EXIT_HEAD_DRIFT, expected_head, observed_head=observed_head)
    return None


def _validate_terminal(
    result: dict[str, Any], run: Callable[..., subprocess.CompletedProcess[str]],
    pr: str, expected_head: str, deadline: float, started: float,
    now: Callable[[], float],
) -> dict[str, Any]:
    remaining = deadline - now()
    if remaining <= 0:
        return _timeout(expected_head, started, now)
    try:
        return _read_current_head(run, pr, expected_head, remaining) or result
    except subprocess.TimeoutExpired:
        return _timeout(expected_head, started, now)


class _ArgumentParseError(Exception):
    pass


class _JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _ArgumentParseError(message)


def wait_for_checks(pr: str, expected_head: str, *, timeout_seconds: float = 1800,
                    poll_interval_seconds: float = 10, no_check_grace_seconds: float = 60,
                    run: Callable[..., subprocess.CompletedProcess[str]] | None = None,
                    now: Callable[[], float] = time.monotonic, sleep: Callable[[float], None] = time.sleep) -> dict[str, Any]:
    """Poll checks for `pr`, refusing results once its head changes."""
    _validate_timing(timeout_seconds, poll_interval_seconds, no_check_grace_seconds)
    run = run or _default_run
    started = now()
    deadline = started + timeout_seconds
    no_checks_since: float | None = None

    while True:
        remaining = deadline - now()
        if remaining <= 0:
            return _timeout(expected_head, started, now)
        try:
            head_result = _read_current_head(run, pr, expected_head, remaining)
            if head_result:
                return head_result
            remaining = deadline - now()
            if remaining <= 0:
                return _timeout(expected_head, started, now)
            checks, error = _run_gh(run, ["gh", "pr", "checks", pr, "--json", "bucket,name,link,state,workflow"], remaining, allow_pending_exit=True, allow_no_checks=True)
        except subprocess.TimeoutExpired:
            return _timeout(expected_head, started, now)
        if error:
            return _result("operational_error", EXIT_OPERATIONAL_ERROR, expected_head, error=error)
        if not isinstance(checks, list):
            return _result("operational_error", EXIT_OPERATIONAL_ERROR, expected_head, error="gh returned checks outside a JSON list")
        if checks:
            no_checks_since = None
            result = _classify_checks(checks, expected_head)
            if result:
                return _validate_terminal(result, run, pr, expected_head, deadline, started, now)
        elif no_check_grace_seconds == 0 or (no_checks_since is not None and now() - no_checks_since >= no_check_grace_seconds):
            result = _result("no_checks", EXIT_NO_CHECKS, expected_head, elapsed_seconds=now() - started)
            return _validate_terminal(result, run, pr, expected_head, deadline, started, now)
        else:
            no_checks_since = no_checks_since if no_checks_since is not None else now()
        remaining = deadline - now()
        if remaining <= 0:
            return _timeout(expected_head, started, now)
        sleep(min(poll_interval_seconds, remaining))


def main(argv: list[str] | None = None) -> int:
    parser = _JsonArgumentParser(description=__doc__)
    parser.add_argument("--pr", required=True, help="pull request number or URL")
    parser.add_argument("--expected-head", required=True, help="SHA that must remain current")
    parser.add_argument("--timeout-seconds", type=float, default=1800)
    parser.add_argument("--poll-interval-seconds", type=float, default=10)
    parser.add_argument("--no-check-grace-seconds", type=float, default=60)
    try:
        args = parser.parse_args(argv)
    except _ArgumentParseError as exc:
        result = {"status": "argument_error", "exit_code": EXIT_ARGUMENT_ERROR, "error": str(exc)}
        print(json.dumps(result, sort_keys=True))
        return EXIT_ARGUMENT_ERROR
    try:
        result = wait_for_checks(
            args.pr,
            args.expected_head,
            timeout_seconds=args.timeout_seconds,
            poll_interval_seconds=args.poll_interval_seconds,
            no_check_grace_seconds=args.no_check_grace_seconds,
        )
    except ValueError as exc:
        result = {"status": "argument_error", "exit_code": EXIT_ARGUMENT_ERROR, "error": str(exc)}
    print(json.dumps(result, sort_keys=True))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
