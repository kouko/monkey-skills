"""Contract tests for the review-batch proposer (module rule, cap 4)."""

from __future__ import annotations

import importlib.util
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
    disposition: str = "individual",
    not_batched_because: str | None = None,
) -> str:
    module_line = f"- **Module**: {module}\n" if module is not None else ""
    weight_line = (
        f"- **Review-weight**: {review_weight}\n" if review_weight is not None else ""
    )
    reason_line = (
        f"- **Not batched because**: {not_batched_because}\n"
        if not_batched_because is not None
        else ""
    )
    return f"""\
## Task {number} — Task {number}

- **Description**: Implement Task {number}.
{module_line}- **Files touched**: `module_{number}.py`
- **Dependencies**: {dependencies}
{weight_line}- **Review disposition**: {disposition}
{reason_line}- **Status**: pending

"""


def _batch(batch_id: str, members: list[int], *, oversized_because: str | None = None) -> str:
    member_list = ", ".join(f"Task {n}" for n in members)
    reason_line = (
        f"- **Oversized because**: {oversized_because}\n"
        if oversized_because is not None
        else ""
    )
    return f"""\
### Review Batch: {batch_id}
- **Members**: {member_list}
- **Verdict question**: Does batch {batch_id} hold?
- **Review lane**: full
- **Aggregate verification**: run the module's test file
- **Boundary**: capability: {batch_id} surface; exclusions: none; consumable: yes
{reason_line}
"""


def _plan(*tasks: str, batches: str = "none\n") -> str:
    return "# Plan\n\n" + "".join(tasks) + "## Review Batches\n\n" + batches


def _check(plan_text: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    plan = tmp_path / "plan.md"
    plan.write_text(plan_text, encoding="utf-8")
    return _run("--check", str(plan))


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
    # A one-member tail chunk buys nothing for the batch ceremony: it is a
    # singleton, never a `batches[]` entry.
    members = _member_lists(proposal)
    assert [len(batch) for batch in members] == [4]
    assert proposal["singletons"] == [5]
    position = {
        task: index for index, batch in enumerate(members) for task in batch
    }
    position[5] = len(members)
    for later, earlier in ((1, 2), (2, 3), (4, 3), (5, 4)):
        assert position[earlier] <= position[later]
    assert proposal["batches"][0]["reason"] == "module:pkg/core.py"
    assert proposal["batches"][0]["lane"] == "full"


def test_singletons_are_sorted_when_a_tail_chunk_precedes_a_standalone_task(tmp_path):
    # A five-task chain (1,2,4,5,6) yields a tail singleton 6 while the
    # standalone Task 3 is its own component; consumers get one sorted list.
    proposal = _propose(
        _plan(
            _task(1, dependencies="Task 2 completes first"),
            _task(2, dependencies="Task 4 completes first"),
            _task(3, module="pkg/other.py"),
            _task(4),
            _task(5, dependencies="Task 4 completes first"),
            _task(6, dependencies="Task 5 completes first"),
        ),
        tmp_path,
    )
    assert proposal["singletons"] == sorted(proposal["singletons"])
    assert sorted(proposal["singletons"]) == [3, 6]


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


def test_field_name_constants_are_exported():
    # Task 9's prose-contract test imports these names; the strings are the
    # exact plan field names the check reads.
    spec = importlib.util.spec_from_file_location("proposer_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.NOT_BATCHED_FIELD == "Not batched because"
    assert module.OVERSIZED_FIELD == "Oversized because"


def test_propose_review_batches_oracle_keeps_name_and_exception_type(monkeypatch):
    import propose_review_batches

    def _raise_import_error(*args, **kwargs):
        raise ImportError("boom")

    monkeypatch.setattr(propose_review_batches, "load_sibling", _raise_import_error)
    with pytest.raises(ValueError):
        propose_review_batches._oracle()

    monkeypatch.undo()
    sys.modules.pop("propose_review_batch_oracle", None)
    try:
        module = propose_review_batches._oracle()
        assert sys.modules["propose_review_batch_oracle"] is module
    finally:
        sys.modules.pop("propose_review_batch_oracle", None)


def test_check_flags_unbatched_proposed_pair_without_reason(tmp_path):
    # Same lane + same Module -> proposed together; both declared individual
    # with no reason is the silent conservatism the check exists to refuse.
    result = _check(_plan(_task(1), _task(2)), tmp_path)
    assert result.returncode != 0
    assert "Task 2: proposed with Task 1" in result.stdout
    assert "Not batched because" in result.stdout

    # One line per later task, naming every earlier task it was proposed
    # with -- not one line per (earlier, later) pair.
    three = _check(_plan(_task(1), _task(2), _task(3)), tmp_path)
    assert three.returncode != 0
    lines = three.stdout.splitlines()
    assert len(lines) == 2, three.stdout
    assert lines[0].startswith("Task 2: proposed with Task 1 but not declared")
    assert lines[1].startswith("Task 3: proposed with Task 1, Task 2 but not declared")

    with_reason = _check(
        _plan(_task(1), _task(2, not_batched_because="separate release points")),
        tmp_path,
    )
    assert with_reason.returncode == 0, with_reason.stdout + with_reason.stderr


def test_check_flags_oversized_declared_batch_without_reason(tmp_path):
    tasks = [_task(n, disposition="batch(big)") for n in range(1, 6)]
    without = _check(
        _plan(*tasks, batches=_batch("big", [1, 2, 3, 4, 5])), tmp_path
    )
    assert without.returncode != 0
    assert "big" in without.stdout
    assert "Oversized because" in without.stdout

    with_reason = _check(
        _plan(*tasks, batches=_batch("big", [1, 2, 3, 4, 5], oversized_because="one release")),
        tmp_path,
    )
    assert with_reason.returncode == 0, with_reason.stdout + with_reason.stderr


def test_check_passes_when_declared_batches_equal_proposal(tmp_path):
    result = _check(
        _plan(
            _task(1, disposition="batch(pair)"),
            _task(2, disposition="batch(pair)"),
            batches=_batch("pair", [1, 2]),
        ),
        tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
