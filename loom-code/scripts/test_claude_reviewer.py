from __future__ import annotations

import io
import subprocess

import claude_reviewer


def test_run_attempt_valid_output_passes_through_once(monkeypatch) -> None:
    calls = []

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, stdout="verdict: PASS\n", stderr="")

    monkeypatch.setattr(claude_reviewer.subprocess, "run", fake_run)

    result = claude_reviewer.run_attempt("claude", "sonnet", "review this", 600)

    assert result.kind == "success"
    assert result.stdout == "verdict: PASS\n"
    assert result.returncode == 0
    assert len(calls) == 1
    assert calls[0][0] == [
        "claude", "-p", "--model", "sonnet", "--output-format", "text",
        "--no-session-persistence",
    ]
    assert calls[0][1]["input"] == "review this"
    assert calls[0][1]["timeout"] == 600


def test_run_attempt_whitespace_output_is_invalid_with_diagnostics(monkeypatch) -> None:
    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout=" \n\t", stderr="provider note")

    monkeypatch.setattr(claude_reviewer.subprocess, "run", fake_run)

    result = claude_reviewer.run_attempt("claude", "sonnet", "review this", 600)

    assert result.kind == "empty-output"
    assert result.returncode == 0
    assert result.stderr == "provider note"
    assert result.exit_code == 3


def test_run_attempt_timeout_is_terminated_with_elapsed_diagnostics(monkeypatch) -> None:
    times = iter((100.0, 107.25))
    monkeypatch.setattr(claude_reviewer.time, "monotonic", lambda: next(times))

    def fake_run(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, kwargs["timeout"], output="partial", stderr="slow")

    monkeypatch.setattr(claude_reviewer.subprocess, "run", fake_run)

    result = claude_reviewer.run_attempt("claude", "sonnet", "review this", 7)

    assert result.kind == "timeout"
    assert result.stdout == "partial"
    assert result.stderr == "slow"
    assert result.elapsed_seconds == 7.25
    assert result.exit_code == 124


def test_main_reports_empty_output_without_retrying(monkeypatch) -> None:
    calls = 0

    def fake_attempt(*args):
        nonlocal calls
        calls += 1
        return claude_reviewer.Attempt(
            kind="empty-output", stdout="", stderr="provider note",
            returncode=0, elapsed_seconds=1.5, exit_code=3,
        )

    monkeypatch.setattr(claude_reviewer, "run_attempt", fake_attempt)
    out = io.StringIO()
    err = io.StringIO()

    rc = claude_reviewer.main(
        ["--model", "sonnet", "--timeout-seconds", "600"],
        stdin=io.StringIO("review this"), out=out, err=err,
    )

    assert rc == 3
    assert calls == 1
    assert out.getvalue() == ""
    assert "empty-output" in err.getvalue()
    assert "provider note" in err.getvalue()
    assert "retry" not in err.getvalue().lower()
