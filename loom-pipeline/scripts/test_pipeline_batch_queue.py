"""Tests for loom-pipeline/scripts/batch_queue.py."""
from __future__ import annotations

from pathlib import Path

import pytest

from batch_queue import (
    QueueError,
    check_frozen,
    effective_entries,
    load_queue,
    load_state,
    save_state,
)

QUEUE_TOML = """\
[[change]]
id = "add-export-csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
models = { code = "sonnet", review = "sonnet" }
[change.budgets]
run = 200000
perStation = { code = 40000, review = 20000 }

[[change]]
id = "fix-login-redirect"
plan = "docs/loom/plans/2026-07-03-fix-login-redirect.md"
[change.budgets]
run = 150000

[[change]]
id = "add-dark-mode"
plan = "docs/loom/plans/2026-07-03-add-dark-mode.md"
[change.budgets]
run = 180000
"""


def test_load_queue_returns_entries_in_file_order(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(QUEUE_TOML, encoding="utf-8")

    entries = load_queue(queue_path)

    assert len(entries) == 3
    assert [e["id"] for e in entries] == [
        "add-export-csv",
        "fix-login-redirect",
        "add-dark-mode",
    ]
    assert entries[0]["plan"] == "docs/loom/plans/2026-07-03-add-export-csv.md"
    assert entries[0]["budgets"]["run"] == 200000
    assert entries[0]["models"] == {"code": "sonnet", "review": "sonnet"}
    assert entries[1]["id"] == "fix-login-redirect"
    assert entries[1]["budgets"]["run"] == 150000
    assert entries[2]["id"] == "add-dark-mode"
    assert entries[2]["budgets"]["run"] == 180000


MISSING_FIELD_CASES = [
    pytest.param(
        """\
[[change]]
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
run = 200000
""",
        "id",
        id="missing-id",
    ),
    pytest.param(
        """\
[[change]]
id = "add-export-csv"
[change.budgets]
run = 200000
""",
        "plan",
        id="missing-plan",
    ),
    pytest.param(
        """\
[[change]]
id = "add-export-csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
perStation = { code = 40000 }
""",
        "budgets.run",
        id="missing-budgets-run",
    ),
]


@pytest.mark.parametrize("toml_text,missing_field", MISSING_FIELD_CASES)
def test_load_queue_fails_loud_on_missing_required_field(tmp_path, toml_text, missing_field):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(toml_text, encoding="utf-8")

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert missing_field in str(exc_info.value)


def test_load_queue_fails_loud_on_invalid_id_pattern(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(
        """\
[[change]]
id = "add export csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
run = 200000
""",
        encoding="utf-8",
    )

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert "add export csv" in str(exc_info.value)


def test_load_queue_fails_loud_on_non_string_id(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(
        """\
[[change]]
id = 42
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
run = 200000
""",
        encoding="utf-8",
    )

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert "42" in str(exc_info.value)
    assert "index 0" in str(exc_info.value)


def test_load_queue_fails_loud_on_id_containing_dotdot(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(
        """\
[[change]]
id = "a..b"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
run = 200000
""",
        encoding="utf-8",
    )

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert "a..b" in str(exc_info.value)


def test_load_queue_fails_loud_on_duplicate_ids(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text(
        """\
[[change]]
id = "add-export-csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv.md"
[change.budgets]
run = 200000

[[change]]
id = "add-export-csv"
plan = "docs/loom/plans/2026-07-03-add-export-csv-2.md"
[change.budgets]
run = 150000
""",
        encoding="utf-8",
    )

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert "add-export-csv" in str(exc_info.value)


def test_load_queue_fails_loud_on_missing_file(tmp_path):
    queue_path = tmp_path / "does-not-exist.toml"

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert str(queue_path) in str(exc_info.value)


def test_load_queue_fails_loud_on_invalid_toml(tmp_path):
    queue_path = tmp_path / "QUEUE.toml"
    queue_path.write_text("this is not [ valid toml", encoding="utf-8")

    with pytest.raises(QueueError) as exc_info:
        load_queue(queue_path)

    assert str(queue_path) in str(exc_info.value)


def test_effective_entries_defaults_absent_ids_to_queued():
    entries = [
        {"id": "add-export-csv", "plan": "p1", "budgets": {"run": 1}},
        {"id": "fix-login-redirect", "plan": "p2", "budgets": {"run": 1}},
    ]
    state = {"add-export-csv": {"status": "DONE", "runId": "wf_1"}}

    merged = effective_entries(entries, state)

    assert merged[0]["status"] == "DONE"
    assert merged[0]["runId"] == "wf_1"
    assert merged[1]["status"] == "QUEUED"
    assert "runId" not in merged[1]


def test_effective_entries_merges_full_record_fields():
    entries = [{"id": "add-export-csv", "plan": "p1", "budgets": {"run": 1}}]
    state = {
        "add-export-csv": {
            "status": "SKIPPED",
            "reason": "validator exit 1",
            "branch": "loom/add-export-csv",
            "worktree": "/tmp/wt/add-export-csv",
        }
    }

    merged = effective_entries(entries, state)

    assert merged[0]["status"] == "SKIPPED"
    assert merged[0]["reason"] == "validator exit 1"
    assert merged[0]["branch"] == "loom/add-export-csv"
    assert merged[0]["worktree"] == "/tmp/wt/add-export-csv"


def test_load_state_returns_empty_state_when_file_missing(tmp_path):
    state_path = tmp_path / "queue-state.json"

    assert load_state(state_path) == {}


def test_save_state_then_load_state_round_trips_records(tmp_path):
    state_path = tmp_path / "queue-state.json"
    state = {
        "add-export-csv": {
            "status": "RUNNING",
            "runId": "wf_1",
            "branch": "loom/add-export-csv",
            "worktree": "/tmp/wt/add-export-csv",
        },
        "fix-login-redirect": {"status": "FAILED", "reason": "validator exit 1"},
    }

    save_state(state_path, state)
    loaded = load_state(state_path)

    assert loaded == state
    # atomic write: no leftover tmp file beside the final state file
    assert [p.name for p in tmp_path.iterdir()] == [state_path.name]


def test_load_state_fails_loud_on_malformed_json(tmp_path):
    state_path = tmp_path / "queue-state.json"
    state_path.write_text("not json", encoding="utf-8")

    with pytest.raises(QueueError) as exc_info:
        load_state(state_path)

    assert "load_state" in str(exc_info.value)
    assert str(state_path) in str(exc_info.value)


def test_load_state_fails_loud_on_non_dict_json(tmp_path):
    # valid JSON but wrong shape (top level must be an object keyed by id) —
    # without the guard this leaks through and explodes later in
    # effective_entries with a raw AttributeError.
    state_path = tmp_path / "queue-state.json"
    state_path.write_text("[]", encoding="utf-8")

    with pytest.raises(QueueError) as exc_info:
        load_state(state_path)

    assert "load_state" in str(exc_info.value)
    assert str(state_path) in str(exc_info.value)
    assert "list" in str(exc_info.value)


def _write_stub_validator(skills_root: Path, exit_code: int) -> None:
    """Write a stub loom-spec validator under skills_root that exits exit_code.

    Stands in for the real ``loom-spec/scripts/validate_spec_output.py`` so
    tests never invoke the real validator (host convention: stub, don't
    shell out to sibling-team scripts from unit tests).
    """
    validator_path = skills_root / "loom-spec" / "scripts" / "validate_spec_output.py"
    validator_path.parent.mkdir(parents=True, exist_ok=True)
    validator_path.write_text(f"import sys\nsys.exit({exit_code})\n", encoding="utf-8")


def _make_entry(plan_rel: str) -> dict:
    return {"id": "add-export-csv", "plan": plan_rel, "budgets": {"run": 1}}


def test_check_frozen_rejects_when_validator_nonzero(tmp_path):
    project_path = tmp_path / "project"
    plan_rel = "docs/loom/plans/2026-07-03-add-export-csv.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text("plan\n", encoding="utf-8")

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=1)

    eligible, reason = check_frozen(_make_entry(plan_rel), project_path, skills_root)

    assert eligible is False
    assert "1" in reason


def test_check_frozen_accepts_when_validator_zero_and_plan_present(tmp_path):
    project_path = tmp_path / "project"
    plan_rel = "docs/loom/plans/2026-07-03-add-export-csv.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text("plan\n", encoding="utf-8")

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    eligible, reason = check_frozen(_make_entry(plan_rel), project_path, skills_root)

    assert eligible is True
    assert reason


def test_check_frozen_rejects_when_plan_missing(tmp_path):
    project_path = tmp_path / "project"
    project_path.mkdir()
    plan_rel = "docs/loom/plans/2026-07-03-missing.md"

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    eligible, reason = check_frozen(_make_entry(plan_rel), project_path, skills_root)

    assert eligible is False
    assert "not found" in reason


def test_check_frozen_rejects_path_traversal_in_plan(tmp_path):
    project_path = tmp_path / "project"
    project_path.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("secret\n", encoding="utf-8")

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    eligible, reason = check_frozen(
        _make_entry("../outside.md"), project_path, skills_root
    )

    assert eligible is False
    assert "traversal" in reason.lower()


def test_check_frozen_rejects_absolute_path_escaping_project(tmp_path):
    project_path = tmp_path / "project"
    project_path.mkdir()
    outside = tmp_path / "etc-passwd-stand-in.md"
    outside.write_text("secret\n", encoding="utf-8")

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    eligible, reason = check_frozen(
        _make_entry(str(outside)), project_path, skills_root
    )

    assert eligible is False
    assert "traversal" in reason.lower()
