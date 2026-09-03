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
