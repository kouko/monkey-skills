"""Contract tests for the review-batch proposer (module rule, cap 4)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).with_name("propose_review_batches.py")
REPO = Path(__file__).resolve().parents[2]
US_SEC_PLAN = REPO / "docs/loom/plans/2026-07-13-us-sec-financial-table-xval.md"
_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=_ENV,
        cwd=REPO,
    )


def _propose(plan_text: str, tmp_path: Path) -> dict:
    plan = tmp_path / "plan.md"
    plan.write_text(plan_text, encoding="utf-8")
    result = _run(str(plan))
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _task(
    number: int,
    *,
    dependencies: str = "none",
    module: str | None = "`pkg/core.py`",
    review_weight: str | None = None,
) -> str:
    module_line = f"- **Module**: {module}\n" if module is not None else ""
    weight_line = (
        f"- **Review-weight**: {review_weight}\n" if review_weight is not None else ""
    )
    return f"""\
## Task {number} — Task {number}

- **Description**: Implement Task {number}.
{module_line}- **Files touched**: `module_{number}.py`
- **Dependencies**: {dependencies}
{weight_line}- **Review disposition**: individual
- **Status**: pending

"""


def _plan(*tasks: str) -> str:
    return "# Plan\n\n" + "".join(tasks) + "## Review Batches\n\nnone\n"


def _member_lists(proposal: dict) -> list[list[int]]:
    return [batch["members"] for batch in proposal["batches"]]


def test_propose_reproduces_simulation_on_us_sec_xval_plan():
    # Oracle value: docs/loom/dogfood/2026-08-31-batch-knob-simulation-per-plan.csv
    # column fanouts_c_module_cap4 for this plan is 5.
    result = _run(str(US_SEC_PLAN))
    assert result.returncode == 0, result.stderr
    proposal = json.loads(result.stdout)
    assert len(proposal["batches"]) + len(proposal["singletons"]) == 5


def test_same_module_component_of_five_splits_four_plus_one_in_dependency_order(tmp_path):
    # A batch may never hold a task whose dependency sits in a LATER batch;
    # the tail task is the one with the deepest dependency.
    proposal = _propose(
        _plan(
            _task(1, dependencies="Task 2 completes first"),
            _task(2, dependencies="Task 3 completes first"),
            _task(3),
            _task(4, dependencies="Task 3 completes first"),
            _task(5, dependencies="Task 4 completes first"),
        ),
        tmp_path,
    )
    members = _member_lists(proposal)
    assert [len(batch) for batch in members] == [4, 1]
    assert proposal["singletons"] == []
    position = {
        task: index for index, batch in enumerate(members) for task in batch
    }
    for later, earlier in ((1, 2), (2, 3), (4, 3), (5, 4)):
        assert position[earlier] <= position[later]
    assert proposal["batches"][0]["reason"] == "module:pkg/core.py"
    assert proposal["batches"][0]["lane"] == "full"


def test_mechanical_tasks_are_excluded_from_batches_and_singletons(tmp_path):
    proposal = _propose(
        _plan(
            _task(1),
            _task(2, review_weight="mechanical"),
            _task(3, dependencies="Task 2 completes first"),
        ),
        tmp_path,
    )
    assert _member_lists(proposal) == [[1, 3]]
    assert proposal["singletons"] == []


def test_tasks_in_different_lanes_never_share_a_batch(tmp_path):
    proposal = _propose(
        _plan(
            _task(1),
            _task(2, dependencies="Task 1 completes first", review_weight="prose"),
        ),
        tmp_path,
    )
    assert proposal["batches"] == []
    assert proposal["singletons"] == [1, 2]


def test_plan_without_module_lines_clusters_by_dependency_edges(tmp_path):
    proposal = _propose(
        _plan(
            _task(1, module=None),
            _task(2, module=None, dependencies="Task 1 completes first"),
            _task(3, module=None),
        ),
        tmp_path,
    )
    assert _member_lists(proposal) == [[1, 2]]
    assert proposal["batches"][0]["reason"] == "dependency"
    assert proposal["singletons"] == [3]


def test_structural_oracle_errors_refuse_with_named_errors(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(
        _plan(_task(1, dependencies="after Task 2 lands")), encoding="utf-8"
    )
    result = _run(str(plan))
    assert result.returncode != 0
    assert "Task 1 Dependencies" in result.stderr
    assert result.stdout == ""


@pytest.mark.parametrize("args", [(), ("a.md", "b.md")])
def test_usage_error_on_wrong_argument_count(args):
    result = _run(*args)
    assert result.returncode == 2
