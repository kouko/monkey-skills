"""Tests for the bounded, deterministic post-PR CI waiter.

Grounding: `gh pr view --help` exposes JSON field `headRefOid`; `gh pr
checks --help` exposes `bucket,name,link,state,workflow`, buckets `pass`,
`fail`, `pending`, `skipping`, and `cancel`, plus exit code 8 for pending
checks. GitHub CLI v2.88.1's tag-pinned
https://github.com/cli/cli/blob/v2.88.1/pkg/cmd/pr/checks/checks.go grounds
the exact no-check stderr literal exercised below. Captured locally on
2026-08-23.
"""

import json
import subprocess
import sys
from pathlib import Path

import post_pr_ci


PASSING = [{"bucket": "pass", "name": "unit", "state": "SUCCESS"}]
FAILING = [{"bucket": "fail", "name": "unit", "state": "FAILURE"}]
PENDING = [{"bucket": "pending", "name": "unit", "state": "IN_PROGRESS"}]
CANCELLED = [{"bucket": "cancel", "name": "unit", "state": "CANCELLED"}]


def _wait(heads, check_responses, *, timeout=10, grace=3, error_at=None,
          timeout_error_at=None):
    clock = [0.0]
    head_values = iter(heads)
    last_head = [None]
    checks = iter(check_responses)
    calls = []

    def run(command, timeout=None):
        calls.append(command)
        if timeout_error_at is not None and len(calls) == timeout_error_at:
            raise subprocess.TimeoutExpired(command, timeout)
        if error_at is not None and len(calls) == error_at:
            return subprocess.CompletedProcess(command, 1, "", "gh unavailable")
        if command[2:4] == ["view", "17"]:
            try:
                last_head[0] = next(head_values)
            except StopIteration:
                assert last_head[0] is not None
            return subprocess.CompletedProcess(
                command, 0, json.dumps({"headRefOid": last_head[0]}), ""
            )
        assert command[2:4] == ["checks", "17"]
        return subprocess.CompletedProcess(command, 0, json.dumps(next(checks)), "")

    result = post_pr_ci.wait_for_checks(
        "17",
        "expected",
        timeout_seconds=timeout,
        poll_interval_seconds=1,
        no_check_grace_seconds=grace,
        run=run,
        now=lambda: clock[0],
        sleep=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )
    return result, calls


def test_wait_passes_when_all_checks_pass():
    result, _ = _wait(["expected"], [PASSING])

    assert result["status"] == "pass"
    assert result["exit_code"] == post_pr_ci.EXIT_PASS


def test_wait_pending_then_passes():
    result, calls = _wait(["expected", "expected"], [PENDING, PASSING])

    assert result["status"] == "pass"
    assert len([call for call in calls if call[2] == "checks"]) == 2


def test_wait_accepts_gh_pending_exit_eight_then_passes():
    clock = [0.0]
    checks = iter([PENDING, PASSING])

    def run(command, timeout=None):
        if command[2] == "view":
            return subprocess.CompletedProcess(
                command, 0, json.dumps({"headRefOid": "expected"}), ""
            )
        return subprocess.CompletedProcess(command, 8 if clock[0] == 0 else 0,
                                            json.dumps(next(checks)), "")

    result = post_pr_ci.wait_for_checks(
        "17", "expected", poll_interval_seconds=1, run=run,
        now=lambda: clock[0],
        sleep=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )

    assert result["status"] == "pass"


def test_wait_normalizes_known_gh_no_checks_error_into_grace_period():
    clock = [0.0]
    calls = [0]

    def run(command, timeout=None):
        if command[2] == "view":
            return subprocess.CompletedProcess(
                command, 0, json.dumps({"headRefOid": "expected"}), ""
            )
        calls[0] += 1
        if calls[0] == 1:
            return subprocess.CompletedProcess(
                command, 1, "", "no checks reported on the 'feature' branch\n"
            )
        return subprocess.CompletedProcess(command, 0, json.dumps(PASSING), "")

    result = post_pr_ci.wait_for_checks(
        "17", "expected", no_check_grace_seconds=2, poll_interval_seconds=1,
        run=run, now=lambda: clock[0],
        sleep=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )

    assert result["status"] == "pass"


def test_wait_stops_immediately_for_no_checks_when_grace_is_zero():
    result, _ = _wait(["expected", "expected"], [[]], grace=0)

    assert result["status"] == "no_checks"


def test_wait_rechecks_head_before_immediate_no_checks_result():
    views = iter(["expected", "different"])

    def run(command, timeout=None):
        if command[2] == "view":
            return subprocess.CompletedProcess(
                command, 0, json.dumps({"headRefOid": next(views)}), ""
            )
        return subprocess.CompletedProcess(command, 0, "[]", "")

    result = post_pr_ci.wait_for_checks(
        "17", "expected", no_check_grace_seconds=0, run=run,
    )

    assert result["status"] == "head_drift"


def test_wait_rechecks_head_before_expired_no_checks_result():
    clock = [0.0]
    views = iter(["expected", "expected", "different"])

    def run(command, timeout=None):
        if command[2] == "view":
            return subprocess.CompletedProcess(
                command, 0, json.dumps({"headRefOid": next(views)}), ""
            )
        return subprocess.CompletedProcess(command, 0, "[]", "")

    result = post_pr_ci.wait_for_checks(
        "17", "expected", no_check_grace_seconds=1, poll_interval_seconds=1,
        run=run, now=lambda: clock[0],
        sleep=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )

    assert result["status"] == "head_drift"


def test_wait_prefers_cancelled_over_failed_when_buckets_are_mixed():
    result, _ = _wait(["expected"], [FAILING + CANCELLED])

    assert result["status"] == "cancelled"


def test_wait_rechecks_head_after_terminal_checks_before_reporting_pass():
    views = iter(["expected", "different"])

    def run(command, timeout=None):
        if command[2] == "view":
            return subprocess.CompletedProcess(
                command, 0, json.dumps({"headRefOid": next(views)}), ""
            )
        return subprocess.CompletedProcess(command, 0, json.dumps(PASSING), "")

    result = post_pr_ci.wait_for_checks("17", "expected", run=run)

    assert result["status"] == "head_drift"
    assert result["observed_head"] == "different"


def test_wait_normalizes_terminal_head_recheck_timeout():
    views = iter(["expected"])

    def run(command, timeout=None):
        if command[2] == "view":
            try:
                head = next(views)
            except StopIteration:
                raise subprocess.TimeoutExpired(command, timeout)
            return subprocess.CompletedProcess(
                command, 0, json.dumps({"headRefOid": head}), ""
            )
        return subprocess.CompletedProcess(command, 0, json.dumps(PASSING), "")

    result = post_pr_ci.wait_for_checks("17", "expected", run=run)

    assert result["status"] == "timeout"


def test_wait_reports_operational_error_for_missing_terminal_head_oid():
    views = iter([{"headRefOid": "expected"}, {}])

    def run(command, timeout=None):
        if command[2] == "view":
            return subprocess.CompletedProcess(command, 0, json.dumps(next(views)), "")
        return subprocess.CompletedProcess(command, 0, json.dumps(PASSING), "")

    result = post_pr_ci.wait_for_checks("17", "expected", run=run)

    assert result["status"] == "operational_error"


def test_wait_reports_operational_error_for_malformed_terminal_head_json():
    views = iter([json.dumps({"headRefOid": "expected"}), "not-json"])

    def run(command, timeout=None):
        if command[2] == "view":
            return subprocess.CompletedProcess(command, 0, next(views), "")
        return subprocess.CompletedProcess(command, 0, json.dumps(PASSING), "")

    result = post_pr_ci.wait_for_checks("17", "expected", run=run)

    assert result["status"] == "operational_error"


def test_wait_recomputes_remaining_before_checks_after_slow_head_lookup():
    clock = [0.0]
    check_timeouts = []

    def run(command, timeout=None):
        if command[2] == "view":
            clock[0] = 9.0
            return subprocess.CompletedProcess(
                command, 0, json.dumps({"headRefOid": "expected"}), ""
            )
        check_timeouts.append(timeout)
        return subprocess.CompletedProcess(command, 0, json.dumps(PASSING), "")

    result = post_pr_ci.wait_for_checks(
        "17", "expected", timeout_seconds=10, run=run,
        now=lambda: clock[0], sleep=lambda _: None,
    )

    assert result["status"] == "pass"
    assert check_timeouts == [1.0]


def test_wait_sleeps_no_longer_than_fresh_remaining_after_slow_head_lookup():
    clock = [0.0]
    sleeps = []

    def run(command, timeout=None):
        if command[2] == "view":
            clock[0] = 9.0
            return subprocess.CompletedProcess(
                command, 0, json.dumps({"headRefOid": "expected"}), ""
            )
        return subprocess.CompletedProcess(command, 8, json.dumps(PENDING), "")

    def sleep(seconds):
        sleeps.append(seconds)
        clock[0] += seconds

    result = post_pr_ci.wait_for_checks(
        "17", "expected", timeout_seconds=10, poll_interval_seconds=5,
        run=run, now=lambda: clock[0], sleep=sleep,
    )

    assert sleeps == [1.0]
    assert result["status"] == "timeout"


def test_wait_stops_on_failed_check():
    result, _ = _wait(["expected"], [FAILING])

    assert result["status"] == "fail"
    assert result["exit_code"] == post_pr_ci.EXIT_FAIL


def test_wait_stops_on_cancelled_check():
    result, _ = _wait(["expected"], [CANCELLED])

    assert result["status"] == "cancelled"
    assert result["exit_code"] == post_pr_ci.EXIT_CANCELLED


def test_wait_times_out_while_check_is_pending():
    result, _ = _wait(["expected"] * 4, [PENDING] * 4, timeout=2)

    assert result["status"] == "timeout"
    assert result["exit_code"] == post_pr_ci.EXIT_TIMEOUT


def test_wait_stops_after_no_check_grace_period():
    result, _ = _wait(["expected"] * 4, [[]] * 4, grace=2)

    assert result["status"] == "no_checks"
    assert result["exit_code"] == post_pr_ci.EXIT_NO_CHECKS


def test_wait_reports_gh_operational_error():
    result, _ = _wait(["expected"], [PASSING], error_at=1)

    assert result["status"] == "operational_error"
    assert result["exit_code"] == post_pr_ci.EXIT_OPERATIONAL_ERROR
    assert result["error"] == "gh unavailable"


def test_wait_stops_when_pr_head_drifts():
    result, _ = _wait(["different"], [PASSING])

    assert result["status"] == "head_drift"
    assert result["exit_code"] == post_pr_ci.EXIT_HEAD_DRIFT
    assert result["observed_head"] == "different"


def test_wait_timeout_expired_from_gh_is_a_stable_timeout_result():
    result, _ = _wait(["expected"], [PASSING], timeout_error_at=1)

    assert result["status"] == "timeout"
    assert result["exit_code"] == post_pr_ci.EXIT_TIMEOUT


def test_wait_rejects_non_finite_timing_values():
    for keyword, value in (("timeout_seconds", float("nan")),
                           ("poll_interval_seconds", float("inf")),
                           ("no_check_grace_seconds", float("-inf"))):
        try:
            post_pr_ci.wait_for_checks("17", "expected", **{keyword: value})
        except ValueError:
            continue
        raise AssertionError(f"{keyword}={value!r} must be rejected")


def test_cli_help_exits_zero():
    script = Path(__file__).with_name("post_pr_ci.py")
    result = subprocess.run(
        [sys.executable, str(script), "--help"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "--pr" in result.stdout


def test_cli_invalid_timing_emits_one_json_result_with_stable_exit_code():
    script = Path(__file__).with_name("post_pr_ci.py")
    result = subprocess.run(
        [sys.executable, str(script), "--pr", "17", "--expected-head", "x",
         "--timeout-seconds", "nan"],
        capture_output=True, text=True,
    )

    assert result.returncode == post_pr_ci.EXIT_ARGUMENT_ERROR
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "error": "timeout and grace must be non-negative; poll interval must be positive",
        "exit_code": post_pr_ci.EXIT_ARGUMENT_ERROR,
        "status": "argument_error",
    }


def test_cli_malformed_numeric_emits_one_json_result_with_argument_exit_code():
    script = Path(__file__).with_name("post_pr_ci.py")
    result = subprocess.run(
        [sys.executable, str(script), "--pr", "17", "--expected-head", "x",
         "--timeout-seconds", "not-a-number"],
        capture_output=True, text=True,
    )

    assert result.returncode == post_pr_ci.EXIT_ARGUMENT_ERROR
    assert result.stderr == ""
    assert json.loads(result.stdout)["status"] == "argument_error"
