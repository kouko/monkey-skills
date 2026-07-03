"""Tests for loom-pipeline/scripts/batch_queue.py."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from batch_queue import (
    QueueError,
    check_frozen,
    effective_entries,
    ensure_worktree,
    load_queue,
    load_state,
    main,
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


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def _make_tmp_git_repo(tmp_path: Path) -> Path:
    """Build a tmp git repo with one commit — stand-in for a real project."""
    project_path = tmp_path / "project"
    project_path.mkdir()
    _run_git(["init"], project_path)
    _run_git(["config", "user.email", "test@example.com"], project_path)
    _run_git(["config", "user.name", "Test"], project_path)
    (project_path / "README.md").write_text("hello\n", encoding="utf-8")
    _run_git(["add", "README.md"], project_path)
    _run_git(["commit", "-m", "initial commit"], project_path)
    return project_path


def test_ensure_worktree_creates_branch_and_path(tmp_path):
    project_path = _make_tmp_git_repo(tmp_path)

    worktree_path, branch = ensure_worktree(project_path, "add-export-csv")

    assert branch == "loom/add-export-csv"
    assert worktree_path == project_path / ".worktrees" / "loom-add-export-csv"
    assert worktree_path.is_dir()
    head = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], worktree_path)
    assert head.stdout.strip() == "loom/add-export-csv"

    # idempotent: second call returns the same path without error
    worktree_path_2, branch_2 = ensure_worktree(project_path, "add-export-csv")
    assert worktree_path_2 == worktree_path
    assert branch_2 == branch


def test_ensure_worktree_fails_loud_when_branch_exists_without_worktree(tmp_path):
    project_path = _make_tmp_git_repo(tmp_path)
    _run_git(["branch", "loom/add-export-csv"], project_path)

    with pytest.raises(QueueError) as exc_info:
        ensure_worktree(project_path, "add-export-csv")

    assert "loom/add-export-csv" in str(exc_info.value)
    assert "ensure_worktree" in str(exc_info.value)


def test_ensure_worktree_fails_loud_when_path_exists_on_wrong_branch(tmp_path):
    project_path = _make_tmp_git_repo(tmp_path)
    conflict_path = project_path / ".worktrees" / "loom-add-export-csv"
    conflict_path.mkdir(parents=True)
    (conflict_path / "placeholder.txt").write_text("not a worktree\n", encoding="utf-8")

    with pytest.raises(QueueError) as exc_info:
        ensure_worktree(project_path, "add-export-csv")

    assert str(conflict_path) in str(exc_info.value)
    assert "ensure_worktree" in str(exc_info.value)


def test_ensure_worktree_fails_loud_on_git_command_failure(tmp_path):
    # project_path is not a git repo at all — `git -C <path> worktree add`
    # fails, and the failure must surface git's own stderr.
    project_path = tmp_path / "not-a-repo"
    project_path.mkdir()

    with pytest.raises(QueueError) as exc_info:
        ensure_worktree(project_path, "add-export-csv")

    assert "ensure_worktree" in str(exc_info.value)


def test_check_frozen_rejects_invalid_change_id(tmp_path):
    # Sanctioned debt closure (Task 6): check_frozen trusts entry["id"] by
    # contract (load_queue already validated it) — re-assert the allow-list
    # at the trust boundary instead of leaving it emergent.
    project_path = tmp_path / "project"
    project_path.mkdir()
    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)
    entry = {"id": "bad id!", "plan": "plan.md", "budgets": {"run": 1}}

    with pytest.raises(QueueError) as exc_info:
        check_frozen(entry, project_path, skills_root)

    assert "check_frozen" in str(exc_info.value)
    assert "bad id!" in str(exc_info.value)


def test_ensure_worktree_rejects_invalid_change_id(tmp_path):
    # Sanctioned debt closure (Task 6): ensure_worktree trusts change_id by
    # contract — re-assert the allow-list at the trust boundary.
    project_path = _make_tmp_git_repo(tmp_path)

    with pytest.raises(QueueError) as exc_info:
        ensure_worktree(project_path, "bad id!")

    assert "ensure_worktree" in str(exc_info.value)
    assert "bad id!" in str(exc_info.value)


def _write_queue(project_path: Path) -> Path:
    loom_dir = project_path / "docs" / "loom"
    loom_dir.mkdir(parents=True)
    (loom_dir / "QUEUE.toml").write_text(QUEUE_TOML, encoding="utf-8")
    return loom_dir


def test_mark_writes_status_and_run_id(tmp_path):
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)

    exit_code = main(
        [
            "mark",
            "add-export-csv",
            "done",
            "--project",
            str(project_path),
            "--run-id",
            "wf_1",
        ]
    )

    assert exit_code == 0
    state = load_state(loom_dir / "queue-state.json")
    assert state["add-export-csv"]["status"] == "DONE"
    assert state["add-export-csv"]["runId"] == "wf_1"


def test_mark_records_reason_for_failed(tmp_path):
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)

    exit_code = main(
        [
            "mark",
            "fix-login-redirect",
            "failed",
            "--project",
            str(project_path),
            "--reason",
            "validator exit 1",
        ]
    )

    assert exit_code == 0
    state = load_state(loom_dir / "queue-state.json")
    assert state["fix-login-redirect"]["status"] == "FAILED"
    assert state["fix-login-redirect"]["reason"] == "validator exit 1"


def test_mark_fails_loud_on_unknown_change_id(tmp_path, capsys):
    project_path = tmp_path / "project"
    _write_queue(project_path)

    exit_code = main(
        ["mark", "does-not-exist", "done", "--project", str(project_path)]
    )

    assert exit_code != 0
    assert "does-not-exist" in capsys.readouterr().err


def test_mark_rejects_invalid_status_choice(tmp_path, capsys):
    project_path = tmp_path / "project"
    _write_queue(project_path)

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "mark",
                "add-export-csv",
                "bogus-status",
                "--project",
                str(project_path),
            ]
        )

    assert exc_info.value.code != 0
    assert "bogus-status" in capsys.readouterr().err


def test_status_lists_every_entry_with_effective_status(tmp_path, capsys):
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {"status": "DONE", "runId": "wf_1"},
            "fix-login-redirect": {"status": "FAILED", "reason": "validator exit 1"},
        },
    )

    exit_code = main(["status", "--project", str(project_path)])

    assert exit_code == 0
    lines = capsys.readouterr().out.strip().splitlines()

    # one line per queue entry, in queue order (QUEUE_TOML order above)
    assert "add-export-csv" in lines[0]
    assert "DONE" in lines[0]
    assert "wf_1" in lines[0]

    assert "fix-login-redirect" in lines[1]
    assert "FAILED" in lines[1]
    assert "validator exit 1" in lines[1]

    assert "add-dark-mode" in lines[2]
    assert "QUEUED" in lines[2]

    # final totals line, counts per status
    totals_line = lines[-1]
    assert "DONE=1" in totals_line
    assert "FAILED=1" in totals_line
    assert "QUEUED=1" in totals_line
