"""W0-01 — dev requirements declared once; CI installs from them.

Before this task, the CI workflow's `Install test deps` step hardcoded
its dependency list inline (`pip install pytest pyyaml`) and repo-root
`requirements-dev.txt` did not exist. That meant a local run of the
same suite (e.g. one that needs `pytest-xdist` for `-n auto`, added in
W0-02) had no single declared source to install from. This test
recomputes both halves: the requirements file actually declares
`pytest-xdist`, and the CI workflow's install step actually installs
from that file rather than a separate hardcoded list.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REQUIREMENTS_DEV = REPO / "requirements-dev.txt"
CI_WORKFLOW = REPO / ".github" / "workflows" / "loom-code-ci.yml"


def test_dev_requirements_declare_xdist_and_ci_installs_from_them() -> None:
    requirements_text = REQUIREMENTS_DEV.read_text(encoding="utf-8")
    assert "pytest-xdist" in requirements_text

    workflow_text = CI_WORKFLOW.read_text(encoding="utf-8")
    install_step_start = workflow_text.index("Install test deps")
    # The step's `run:` line is the next non-comment line after the step name.
    install_step_run_line = next(
        line
        for line in workflow_text[install_step_start:].splitlines()
        if "run:" in line
    )
    assert "-r requirements-dev.txt" in install_step_run_line


KICKOFF_DEFAULTS = REPO / "docs" / "loom" / "KICKOFF-DEFAULTS.md"


def test_kickoff_and_ci_run_the_same_parallel_command() -> None:
    """W0-02 — KICKOFF-DEFAULTS' package-tests value and the CI pytest step
    must both run with `-n auto`, and otherwise be the same command."""
    kickoff_text = KICKOFF_DEFAULTS.read_text(encoding="utf-8")
    kickoff_line = next(
        line
        for line in kickoff_text.splitlines()
        if line.startswith("- package-tests:")
    )
    kickoff_value = kickoff_line[len("- package-tests:") :]
    # Drop the trailing " — <reason> (<date>)" comment.
    kickoff_command = kickoff_value.split("—")[0].strip()
    assert "-n auto" in kickoff_command

    workflow_text = CI_WORKFLOW.read_text(encoding="utf-8")
    ci_run_line = next(
        line
        for line in workflow_text.splitlines()
        if "run:" in line and "pytest" in line and "loom-code/scripts/" in line
    )
    assert "-n auto" in ci_run_line
    ci_command = ci_run_line.split("run:", 1)[1].strip()

    def tokens(command: str, exclude: set[str]) -> list[str]:
        return [tok for tok in command.split() if tok not in exclude]

    kickoff_tokens = tokens(kickoff_command, {"-q"})
    ci_tokens = tokens(ci_command, {"-v"})
    assert kickoff_tokens == ci_tokens
