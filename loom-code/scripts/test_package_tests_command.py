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

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REQUIREMENTS_DEV = REPO / "requirements-dev.txt"
CI_WORKFLOW = REPO / ".github" / "workflows" / "loom-code-ci.yml"


def test_dev_requirements_declare_xdist_and_ci_installs_from_them() -> None:
    requirements_text = REQUIREMENTS_DEV.read_text(encoding="utf-8")
    active_requirement_names = {
        re.split(r"[<>=!~\[; ]", line)[0]
        for line in (raw_line.strip() for raw_line in requirements_text.splitlines())
        if line and not line.startswith("#")
    }
    assert "pytest-xdist" in active_requirement_names

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


def test_kickoff_and_ci_use_the_same_loom_family_inventory() -> None:
    """Closing Review runs all Loom groups; CI selects from that inventory."""
    kickoff_text = KICKOFF_DEFAULTS.read_text(encoding="utf-8")
    kickoff_line = next(
        line
        for line in kickoff_text.splitlines()
        if line.startswith("- package-tests:")
    )
    kickoff_value = kickoff_line[len("- package-tests:") :]
    # Drop the trailing " — <reason> (<date>)" comment.
    kickoff_command = kickoff_value.split("—")[0].strip()
    assert "scripts/run_package_tests.py --loom-family" in kickoff_command
    assert "--only" not in kickoff_command

    workflow_text = CI_WORKFLOW.read_text(encoding="utf-8")
    ci_run_line = next(
        line for line in workflow_text.splitlines()
        if "run:" in line and "scripts/run_package_tests.py --loom-family" in line
    )
    assert "--only code" in ci_run_line
