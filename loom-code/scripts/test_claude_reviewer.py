from __future__ import annotations

import io
import subprocess

import claude_reviewer
import pytest


def test_run_attempt_valid_output_passes_through_once(monkeypatch) -> None:
    calls = []

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, stdout="verdict: PASS\n", stderr="")

    monkeypatch.setattr(claude_reviewer.subprocess, "run", fake_run)

    result = claude_reviewer.run_attempt(
        "claude", "sonnet", "medium", "review this", 600,
    )

    assert result.kind == "success"
    assert result.stdout == "verdict: PASS\n"
    assert result.returncode == 0
    assert len(calls) == 1
    assert calls[0][0] == [
        "claude", "-p", "--model", "sonnet", "--effort", "medium",
        "--output-format", "text",
        "--no-session-persistence",
    ]
    assert calls[0][1]["input"] == "review this"
    assert calls[0][1]["timeout"] == 600


def test_run_attempt_whitespace_output_is_invalid_with_diagnostics(monkeypatch) -> None:
    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout=" \n\t", stderr="provider note")

    monkeypatch.setattr(claude_reviewer.subprocess, "run", fake_run)

    result = claude_reviewer.run_attempt(
        "claude", "sonnet", "medium", "review this", 600,
    )

    assert result.kind == "empty-output"
    assert result.returncode == 0
    assert result.stderr == "provider note"
    assert result.exit_code == 3


def test_run_attempt_unrecognized_model_is_typed_host_rejection(monkeypatch) -> None:
    marker = '[claude-code:unrecognized_model] {"model":"missing"}'

    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr=marker)

    monkeypatch.setattr(claude_reviewer.subprocess, "run", fake_run)

    result = claude_reviewer.run_attempt(
        "claude", "missing", "medium", "review this", 600,
    )

    assert result.kind == "host-rejection"
    assert result.stderr == marker
    assert result.exit_code == 1


def test_run_attempt_other_nonzero_is_process_error(monkeypatch) -> None:
    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="quota exceeded")

    monkeypatch.setattr(claude_reviewer.subprocess, "run", fake_run)

    result = claude_reviewer.run_attempt(
        "claude", "sonnet", "medium", "review this", 600,
    )

    assert result.kind == "process-error"


def test_run_attempt_timeout_is_terminated_with_elapsed_diagnostics(monkeypatch) -> None:
    times = iter((100.0, 107.25))
    monkeypatch.setattr(claude_reviewer.time, "monotonic", lambda: next(times))

    def fake_run(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, kwargs["timeout"], output="partial", stderr="slow")

    monkeypatch.setattr(claude_reviewer.subprocess, "run", fake_run)

    result = claude_reviewer.run_attempt(
        "claude", "sonnet", "medium", "review this", 7,
    )

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
        ["--model", "sonnet", "--effort", "medium", "--timeout-seconds", "600"],
        stdin=io.StringIO("review this"), out=out, err=err,
    )

    assert rc == 3
    assert calls == 1
    assert out.getvalue() == ""
    assert "empty-output" in err.getvalue()
    assert "provider note" in err.getvalue()
    assert "retry" not in err.getvalue().lower()


def test_main_valid_output_preserves_stdout_and_stderr(monkeypatch) -> None:
    monkeypatch.setattr(
        claude_reviewer,
        "run_attempt",
        lambda *args: claude_reviewer.Attempt(
            kind="success", stdout="verdict: PASS\n", stderr="provider note\n",
            returncode=0, elapsed_seconds=2.0, exit_code=0,
        ),
    )
    out = io.StringIO()
    err = io.StringIO()

    rc = claude_reviewer.main([], stdin=io.StringIO("review"), out=out, err=err)

    assert rc == 0
    assert out.getvalue() == "verdict: PASS\n"
    assert err.getvalue() == "provider note\n"


def test_run_attempt_without_overrides_uses_host_defaults(monkeypatch) -> None:
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout="verdict: PASS\n", stderr="")

    monkeypatch.setattr(claude_reviewer.subprocess, "run", fake_run)

    result = claude_reviewer.run_attempt(
        "claude", None, None, "review this", 600,
    )

    assert result.kind == "success"
    assert calls == [[
        "claude", "-p", "--output-format", "text", "--no-session-persistence",
    ]]


@pytest.mark.parametrize(
    "argv", (["--model", "sonnet"], ["--effort", "medium"]),
)
def test_main_rejects_partial_override_before_spawn(monkeypatch, argv) -> None:
    calls = 0

    def fake_attempt(*args):
        nonlocal calls
        calls += 1

    monkeypatch.setattr(claude_reviewer, "run_attempt", fake_attempt)
    err = io.StringIO()

    rc = claude_reviewer.main(argv, stdin=io.StringIO("review"), err=err)

    assert rc == 2
    assert calls == 0
    assert "--model and --effort must be provided together" in err.getvalue()


def test_main_rejects_unknown_effort_before_spawn(monkeypatch) -> None:
    calls = 0

    def fake_attempt(*args):
        nonlocal calls
        calls += 1

    monkeypatch.setattr(claude_reviewer, "run_attempt", fake_attempt)
    err = io.StringIO()

    rc = claude_reviewer.main(
        ["--model", "sonnet", "--effort", "unknown"],
        stdin=io.StringIO("review"), err=err,
    )

    assert rc == 2
    assert calls == 0
    assert '"kind": "host-rejection"' in err.getvalue()


def test_main_timeout_returns_124_with_json_diagnostics(monkeypatch) -> None:
    monkeypatch.setattr(
        claude_reviewer,
        "run_attempt",
        lambda *args: claude_reviewer.Attempt(
            kind="timeout", stdout="partial", stderr="slow",
            returncode=None, elapsed_seconds=600.25, exit_code=124,
        ),
    )
    out = io.StringIO()
    err = io.StringIO()

    rc = claude_reviewer.main([], stdin=io.StringIO("review"), out=out, err=err)

    assert rc == 124
    assert out.getvalue() == ""
    assert '"kind": "timeout"' in err.getvalue()
    assert '"elapsed_seconds": 600.25' in err.getvalue()
    assert '"stderr": "slow"' in err.getvalue()


def test_cli_rejects_an_alternate_executable() -> None:
    with pytest.raises(SystemExit) as exc:
        claude_reviewer.main(["--claude-bin", "/bin/echo"])

    assert exc.value.code == 2
