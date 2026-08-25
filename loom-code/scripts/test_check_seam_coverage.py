"""Tests for check_seam_coverage.py — the mechanical checker that compares a
writing-plans plan's `- **Dependencies**:` edges against its `- **Seam**:`
bullets (`loom-code/skills/writing-plans/references/plan-format.md`
`#### Seam (v0.100.0+)`).

Exercised as a CLI subprocess (the actual interface: one positional arg,
exit 0 / exit 1) since the contract this script must honor is the process
boundary, mirroring test_check_scenario_coverage.py's convention.

Stdlib only.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "check_seam_coverage.py"

_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _run(plan_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(plan_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


def _write_plan(tmp_path: Path, body: str) -> Path:
    plan_path = tmp_path / "plan.md"
    plan_path.write_text(body, encoding="utf-8")
    return plan_path


_TASK1 = """\
## Task 1 — First task

- **Description**: do first thing.
- **Module**: `a.py`
- **Files touched**: `a.py`
- **Context paths**:
  - /tmp/a.py
- **Acceptance**:
  - **RED**: `a.test > fails today`
  - **GREEN**: `a.test > passes`
- **Dependencies**: none
- **Independent**: true
- **Status**: pending
"""


def _task2(seam_block: str, dependencies: str = "Task 1 completes first") -> str:
    return f"""\
## Task 2 — Second task

- **Description**: do second thing.
- **Module**: `b.py`
- **Files touched**: `b.py`
- **Context paths**:
  - /tmp/b.py
- **Acceptance**:
  - **RED**: `b.test > fails today`
  - **GREEN**: `b.test > passes`
- **Dependencies**: {dependencies}
{seam_block}- **Independent**: false
- **Status**: pending
"""


def test_missing_seam_field_exits_1(tmp_path: Path) -> None:
    plan = _write_plan(tmp_path, _TASK1 + "\n" + _task2(seam_block=""))
    result = _run(plan)
    assert result.returncode == 1
    assert "Task 2" in result.stderr
    assert "Seam" in result.stderr


def test_undeclared_edge_exits_1(tmp_path: Path) -> None:
    task2 = _task2(
        seam_block="- **Seam**:\n  - from Task 1: payload: none\n",
        dependencies="Tasks 1, 3 complete first",
    )
    task3 = _TASK1.replace("Task 1", "Task 3").replace("## Task 1", "## Task 3")
    plan = _write_plan(tmp_path, task3 + "\n" + task2)
    result = _run(plan)
    assert result.returncode == 1
    assert "Task 2" in result.stderr
    assert "from Task 3" in result.stderr


def test_fully_declared_plan_exits_0(tmp_path: Path) -> None:
    task2 = _task2(seam_block="- **Seam**:\n  - from Task 1: payload: none\n")
    plan = _write_plan(tmp_path, _TASK1 + "\n" + task2)
    result = _run(plan)
    assert result.returncode == 0, result.stderr


def test_payload_missing_probe_exits_1(tmp_path: Path) -> None:
    task2 = _task2(
        seam_block=(
            "- **Seam**:\n"
            "  - from Task 1: payload: CSV string; owner: Task 1\n"
        )
    )
    plan = _write_plan(tmp_path, _TASK1 + "\n" + task2)
    result = _run(plan)
    assert result.returncode == 1
    assert "probe" in result.stderr


def test_probe_not_in_acceptance_exits_1(tmp_path: Path) -> None:
    task2 = _task2(
        seam_block=(
            "- **Seam**:\n"
            "  - from Task 1: payload: CSV string; owner: Task 1; "
            "probe: `some probe nobody wrote`\n"
        )
    )
    plan = _write_plan(tmp_path, _TASK1 + "\n" + task2)
    result = _run(plan)
    assert result.returncode == 1
    assert "some probe nobody wrote" in result.stderr


def test_probe_present_in_acceptance_exits_0(tmp_path: Path) -> None:
    task2 = _task2(
        seam_block=(
            "- **Seam**:\n"
            "  - from Task 1: payload: CSV string; owner: Task 1; "
            "probe: `b.test > passes`\n"
        )
    )
    plan = _write_plan(tmp_path, _TASK1 + "\n" + task2)
    result = _run(plan)
    assert result.returncode == 0, result.stderr


def test_zero_dependent_tasks_exits_0(tmp_path: Path) -> None:
    plan = _write_plan(tmp_path, _TASK1)
    result = _run(plan)
    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(
    os.geteuid() == 0,
    reason="root bypasses mode 000, so the unreadable case cannot be built",
)
def test_unreadable_plan_fails_loud(tmp_path: Path) -> None:
    plan = _write_plan(tmp_path, _TASK1)
    plan.chmod(0o000)
    try:
        result = _run(plan)
    finally:
        plan.chmod(0o644)
    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert plan.name in (result.stdout + result.stderr)


def test_missing_plan_file_fails_loud(tmp_path: Path) -> None:
    plan = tmp_path / "does-not-exist.md"
    result = _run(plan)
    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert plan.name in (result.stdout + result.stderr)
