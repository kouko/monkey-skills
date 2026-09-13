"""Adversarial abuse and boundary probes for the Claude reviewer runner.

Every probe stubs the subprocess boundary, so no Claude process is ever
spawned and no credential is ever read. The stub records each spawn
attempt, which lets a probe assert that a rejected profile never reaches
the process boundary at all.
"""

from __future__ import annotations

import io
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[5]
SCRIPTS = ROOT / "loom-code" / "scripts"
HELP_CAPTURE = (
    ROOT
    / "docs"
    / "loom"
    / "2026-09-04-adversary-three-way-attribution-measured"
    / "evidence"
    / "claude-p-help-2026-09-05.txt"
)
sys.path.insert(0, str(SCRIPTS))

import claude_reviewer  # noqa: E402


TAIL_FLAGS = ["--output-format", "text", "--no-session-persistence"]


class SpawnRecorder:
    """Stand in for ``subprocess.run`` and record every spawn attempt."""

    def __init__(self, returncode: int = 0, stdout: str = "verdict: PASS\n", stderr: str = "") -> None:
        self.calls: list[tuple[list[str], dict]] = []
        self._returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    def __call__(self, argv, **kwargs):
        self.calls.append((argv, kwargs))
        return subprocess.CompletedProcess(
            argv, self._returncode, stdout=self._stdout, stderr=self._stderr,
        )


@pytest.fixture
def recorder(monkeypatch) -> SpawnRecorder:
    spawn = SpawnRecorder()
    monkeypatch.setattr(claude_reviewer.subprocess, "run", spawn)
    return spawn


@pytest.mark.parametrize("argv", (["--model", "opus"], ["--effort", "medium"]))
def test_cli_partial_override_pair_never_reaches_process_boundary(recorder, argv) -> None:
    """A half-supplied override pair is rejected before any process spawn."""
    err = io.StringIO()
    out = io.StringIO()

    rc = claude_reviewer.main(argv, stdin=io.StringIO("review"), out=out, err=err)

    assert rc == 2
    assert recorder.calls == []
    assert out.getvalue() == ""
    diagnostic = json.loads(err.getvalue())
    assert diagnostic["kind"] == "input-error"
    assert diagnostic["exit_code"] == 2


@pytest.mark.parametrize(
    "effort",
    (
        "MEDIUM",
        "Medium",
        " medium",
        "medium ",
        "medium\n",
        "med",
        "ultra",
        "",
        "low,medium",
        "0",
        "høy",
        "高",
        "medium; rm -rf /",
        "x" * 4096,
    ),
)
def test_cli_ungrounded_effort_value_never_reaches_process_boundary(recorder, effort) -> None:
    """An effort outside the grounded five-value set is rejected unspawned."""
    err = io.StringIO()

    rc = claude_reviewer.main(
        ["--model", "opus", "--effort", effort], stdin=io.StringIO("review"), err=err,
    )

    assert rc == 2
    assert recorder.calls == []
    assert json.loads(err.getvalue())["kind"] == "input-error"


def test_effort_set_matches_the_checked_in_help_capture() -> None:
    """The accepted effort set equals the values the vendor help capture lists."""
    line = next(
        part
        for part in HELP_CAPTURE.read_text(encoding="utf-8").splitlines()
        if "(low, medium, high, xhigh, max)" in part
    )
    grounded = set(re.search(r"\(([^)]*)\)", line).group(1).replace(" ", "").split(","))

    assert claude_reviewer.CLAUDE_EFFORTS == grounded


@pytest.mark.parametrize("model", ("opus", "sonnet", "haiku", "claude-fable-5", "モデル"))
@pytest.mark.parametrize("effort", sorted(claude_reviewer.CLAUDE_EFFORTS))
def test_argv_accepted_pair_never_emits_a_lone_override(model, effort) -> None:
    """Every accepted pair emits both override flags or neither, never one."""
    argv = claude_reviewer._argv("claude", model, effort)

    assert argv.count("--model") == argv.count("--effort") == 1
    assert argv[argv.index("--model") + 1] == model
    assert argv[argv.index("--effort") + 1] == effort
    assert argv[:2] == ["claude", "-p"]
    assert argv[-3:] == TAIL_FLAGS


@pytest.mark.parametrize("pair", (("opus", None), (None, "medium"), ("", None), (None, "")))
def test_argv_unvalidated_partial_pair_emits_no_override_flag(monkeypatch, pair) -> None:
    """With validation disabled, argv construction still emits no lone override."""
    monkeypatch.setattr(claude_reviewer, "_validate_profile", lambda model, effort: None)

    argv = claude_reviewer._argv("claude", *pair)

    assert "--model" not in argv
    assert "--effort" not in argv
    assert argv == ["claude", "-p"] + TAIL_FLAGS


def test_argv_absent_pair_emits_no_override_flag() -> None:
    """An absent pair emits neither override flag and keeps the tail contract."""
    argv = claude_reviewer._argv("claude", None, None)

    assert "--model" not in argv
    assert "--effort" not in argv
    assert argv == ["claude", "-p"] + TAIL_FLAGS


@pytest.mark.parametrize(
    "model",
    (
        "--dangerously-skip-permissions",
        "--output-format json",
        "; rm -rf /",
        "$(id)",
        "`id`",
        "opus\n--effort max",
        "opus --no-session-persistence",
    ),
)
def test_argv_hostile_model_value_stays_one_inert_argument(recorder, model) -> None:
    """A flag-shaped or shell-shaped model value stays a single argv element."""
    claude_reviewer.run_attempt("claude", model, "medium", "review", 600)

    (argv, kwargs), = recorder.calls
    assert argv.count(model) == 1
    assert argv[argv.index("--model") + 1] == model
    assert argv[-3:] == TAIL_FLAGS
    assert kwargs.get("shell", False) is False
    assert isinstance(argv, list)


def test_argv_empty_model_string_still_reaches_the_process_boundary(recorder) -> None:
    """An empty model string is accepted and emitted as a valueless override."""
    claude_reviewer.run_attempt("claude", "", "medium", "review", 600)

    (argv, _), = recorder.calls
    assert argv[argv.index("--model") + 1] == ""
    assert "" in argv


def test_classification_failure_modes_stay_pairwise_distinguishable(monkeypatch) -> None:
    """Empty output, timeout, host rejection, and process error stay distinct."""
    observed: dict[str, int] = {}

    def _classify(returncode: int, stdout: str, stderr: str) -> claude_reviewer.Attempt:
        monkeypatch.setattr(
            claude_reviewer.subprocess,
            "run",
            SpawnRecorder(returncode=returncode, stdout=stdout, stderr=stderr),
        )
        return claude_reviewer.run_attempt("claude", "opus", "medium", "review", 600)

    for label, args in {
        "success": (0, "verdict: PASS\n", ""),
        "empty-output": (0, "   \n\t", "note"),
        "host-rejection": (1, "", claude_reviewer.UNRECOGNIZED_MODEL_MARKER + " {}"),
        "process-error": (7, "", "quota exceeded"),
    }.items():
        attempt = _classify(*args)
        assert attempt.kind == label
        observed[attempt.kind] = attempt.exit_code

    def _raise(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, kwargs["timeout"], output="", stderr="")

    monkeypatch.setattr(claude_reviewer.subprocess, "run", _raise)
    timed_out = claude_reviewer.run_attempt("claude", "opus", "medium", "review", 600)
    observed[timed_out.kind] = timed_out.exit_code

    err = io.StringIO()
    rejected = claude_reviewer.main(["--effort", "medium"], stdin=io.StringIO("r"), err=err)
    observed["input-error"] = rejected

    assert observed == {
        "success": 0,
        "process-error": 1,
        "input-error": 2,
        "empty-output": 3,
        "host-rejection": 4,
        "timeout": 124,
    }
    assert len(set(observed.values())) == len(observed)


def test_classification_marker_echoed_from_the_prompt_is_read_as_host_rejection(monkeypatch) -> None:
    """A failure that echoes a marker-bearing prompt is typed as host rejection."""
    prompt = f"Review this diff: UNRECOGNIZED_MODEL_MARKER = {claude_reviewer.UNRECOGNIZED_MODEL_MARKER!r}"
    spawn = SpawnRecorder(returncode=1, stdout="", stderr=f"usage error near input: {prompt}")
    monkeypatch.setattr(claude_reviewer.subprocess, "run", spawn)

    attempt = claude_reviewer.run_attempt("claude", "opus", "medium", prompt, 600)

    assert attempt.kind == "host-rejection"
    assert attempt.exit_code == 4


def test_classification_marker_in_stdout_alone_stays_a_process_error(monkeypatch) -> None:
    """Reviewer output carrying the marker does not become a host rejection."""
    spawn = SpawnRecorder(
        returncode=1, stdout=claude_reviewer.UNRECOGNIZED_MODEL_MARKER, stderr="quota exceeded",
    )
    monkeypatch.setattr(claude_reviewer.subprocess, "run", spawn)

    attempt = claude_reviewer.run_attempt("claude", "opus", "medium", "review", 600)

    assert attempt.kind == "process-error"
    assert attempt.exit_code == 1


def test_classification_zero_width_output_is_accepted_as_a_success(monkeypatch) -> None:
    """Output made only of zero-width characters passes the empty-output guard."""
    monkeypatch.setattr(
        claude_reviewer.subprocess, "run", SpawnRecorder(returncode=0, stdout="​﻿"),
    )

    attempt = claude_reviewer.run_attempt("claude", "opus", "medium", "review", 600)

    assert attempt.kind == "success"
    assert attempt.exit_code == 0


@pytest.mark.parametrize("seconds", ("0", "-1", "-86400"))
def test_cli_nonpositive_timeout_is_rejected_without_a_json_diagnostic(recorder, seconds) -> None:
    """A non-positive timeout exits 2 with prose where input errors emit JSON."""
    err = io.StringIO()

    rc = claude_reviewer.main(
        ["--timeout-seconds", seconds], stdin=io.StringIO("review"), err=err,
    )

    assert rc == 2
    assert recorder.calls == []
    assert "--timeout-seconds" in err.getvalue()
    with pytest.raises(json.JSONDecodeError):
        json.loads(err.getvalue())


def test_cli_unparsable_timeout_exits_two_without_a_diagnostic_body(recorder) -> None:
    """A non-integer timeout exits 2 through argparse without a JSON body."""
    with pytest.raises(SystemExit) as exc:
        claude_reviewer.main(["--timeout-seconds", "10s"], stdin=io.StringIO("review"))

    assert exc.value.code == 2
    assert recorder.calls == []


def test_cli_non_ascii_input_error_serialises_as_readable_json(recorder) -> None:
    """A non-ASCII rejected effort is echoed unescaped in the JSON diagnostic."""
    err = io.StringIO()

    rc = claude_reviewer.main(
        ["--model", "opus", "--effort", "中"], stdin=io.StringIO("review"), err=err,
    )

    assert rc == 2
    assert recorder.calls == []
    assert "中" in err.getvalue()
    assert json.loads(err.getvalue())["stderr"].endswith("中")
