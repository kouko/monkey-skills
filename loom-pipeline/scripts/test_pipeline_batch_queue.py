"""Tests for loom-pipeline/scripts/batch_queue.py."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from batch_queue import (
    QueueError,
    _check_circuit_breaker,
    _classify_running_entry,
    _read_wf_terminal_status,
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
    # Form A: the change folder exists, so the validator is the gate.
    (project_path / "docs" / "loom" / "add-export-csv").mkdir(parents=True)

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
    # Form A: the change folder exists, so the validator is the gate.
    (project_path / "docs" / "loom" / "add-export-csv").mkdir(parents=True)

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    eligible, reason = check_frozen(_make_entry(plan_rel), project_path, skills_root)

    assert eligible is True
    assert reason


_PLAN_WITH_PASS = (
    "# Plan: add export csv\n\n"
    "**Plan-document-reviewer verdict**: PASS (2026-07-03, 14/14 checks)\n"
)


def test_check_frozen_accepts_brief_plan_form_when_no_change_folder(tmp_path):
    # Form B (brief+plan): no docs/loom/<id>/ change folder exists; the plan
    # carries a reviewer PASS line. The validator must NOT be consulted —
    # the stub exits 1, so eligibility proves the branch order.
    project_path = tmp_path / "project"
    plan_rel = "docs/loom/plans/2026-07-03-add-export-csv.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(_PLAN_WITH_PASS, encoding="utf-8")

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=1)

    eligible, reason = check_frozen(_make_entry(plan_rel), project_path, skills_root)

    assert eligible is True
    assert "brief+plan" in reason


def test_check_frozen_accepts_brief_plan_form_plain_verdict_line(tmp_path):
    # Regression anchor for the non-bold header form real consumer plans
    # use (observed on komado-Viewfinder): no markdown asterisks.
    project_path = tmp_path / "project"
    plan_rel = "docs/loom/plans/2026-07-03-add-export-csv.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(
        "# Plan: add export csv\n\n"
        "Plan-document-reviewer verdict: PASS (2026-07-03, 14/14 checks)\n",
        encoding="utf-8",
    )

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=1)

    eligible, reason = check_frozen(_make_entry(plan_rel), project_path, skills_root)

    assert eligible is True
    assert "brief+plan" in reason


def test_check_frozen_rejects_brief_plan_form_quoting_the_phrase_in_prose(tmp_path):
    # A plan that merely QUOTES the verdict phrase mid-sentence (docs about
    # the pipeline itself do this) must NOT count as frozen — the gate is a
    # line-anchored header field, not a whole-body substring.
    project_path = tmp_path / "project"
    plan_rel = "docs/loom/plans/2026-07-03-add-export-csv.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(
        "# Plan: add export csv\n\n"
        "The freeze predicate looks for a `Plan-document-reviewer "
        "verdict: PASS` line in the plan header.\n",
        encoding="utf-8",
    )

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    eligible, reason = check_frozen(_make_entry(plan_rel), project_path, skills_root)

    assert eligible is False
    assert "Plan-document-reviewer" in reason


def test_check_frozen_rejects_brief_plan_form_without_reviewer_pass(tmp_path):
    project_path = tmp_path / "project"
    plan_rel = "docs/loom/plans/2026-07-03-add-export-csv.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text("# Plan: add export csv\n\nno verdict line here\n", encoding="utf-8")

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    eligible, reason = check_frozen(_make_entry(plan_rel), project_path, skills_root)

    assert eligible is False
    assert "Plan-document-reviewer" in reason


def test_check_frozen_rejects_brief_plan_form_with_pending_verdict(tmp_path):
    project_path = tmp_path / "project"
    plan_rel = "docs/loom/plans/2026-07-03-add-export-csv.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(
        "# Plan: add export csv\n\n**Plan-document-reviewer verdict**: PENDING\n",
        encoding="utf-8",
    )

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    eligible, reason = check_frozen(_make_entry(plan_rel), project_path, skills_root)

    assert eligible is False
    assert "Plan-document-reviewer" in reason


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


def test_next_emits_workflow_args_and_marks_running(tmp_path, capsys):
    project_path = _make_tmp_git_repo(tmp_path)

    plan_rel = "docs/loom/plans/2026-07-03-add-export-csv.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(_PLAN_WITH_PASS, encoding="utf-8")
    _run_git(["add", plan_rel], project_path)
    _run_git(["commit", "-m", "add plan"], project_path)

    loom_dir = project_path / "docs" / "loom"
    (loom_dir / "QUEUE.toml").write_text(
        '[[change]]\n'
        'id = "add-export-csv"\n'
        f'plan = "{plan_rel}"\n'
        "[change.budgets]\n"
        "run = 200000\n",
        encoding="utf-8",
    )

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    exit_code = main(
        ["next", "--project", str(project_path), "--skills-root", str(skills_root)]
    )

    assert exit_code == 0
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)

    worktree_path = project_path / ".worktrees" / "loom-add-export-csv"
    expected_plan_path = (worktree_path / plan_rel).resolve()

    assert payload == {
        "segment": 3,
        "changeId": "add-export-csv",
        "projectPath": str(worktree_path.resolve()),
        "planPath": str(expected_plan_path),
        "budgets": {"run": 200000},
        "models": {},
        "skillsRoot": str(skills_root.resolve()),
        "branch": "loom/add-export-csv",
    }
    assert expected_plan_path.is_file()

    state = load_state(loom_dir / "queue-state.json")
    assert state["add-export-csv"]["status"] == "RUNNING"
    assert state["add-export-csv"]["branch"] == "loom/add-export-csv"
    assert state["add-export-csv"]["worktree"] == str(worktree_path)


def test_next_reports_done_when_queue_empty(tmp_path, capsys):
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {"status": "DONE"},
            "fix-login-redirect": {"status": "DONE"},
            "add-dark-mode": {"status": "DONE"},
        },
    )
    skills_root = tmp_path / "skills"

    exit_code = main(
        ["next", "--project", str(project_path), "--skills-root", str(skills_root)]
    )

    assert exit_code == 0
    out = capsys.readouterr().out.strip()
    assert json.loads(out) == {"done": True}
    assert not (project_path / ".worktrees").exists()


def test_next_skips_unfrozen_entry_and_advances(tmp_path, capsys):
    project_path = _make_tmp_git_repo(tmp_path)

    # Entry B is eligible: plan committed, validator exit 0.
    plan_rel_b = "docs/loom/plans/2026-07-03-add-export-csv.md"
    plan_path_b = project_path / plan_rel_b
    plan_path_b.parent.mkdir(parents=True)
    plan_path_b.write_text(_PLAN_WITH_PASS, encoding="utf-8")
    _run_git(["add", plan_rel_b], project_path)
    _run_git(["commit", "-m", "add plan b"], project_path)

    loom_dir = project_path / "docs" / "loom"
    (loom_dir / "QUEUE.toml").write_text(
        '[[change]]\n'
        'id = "unfrozen-change"\n'
        'plan = "docs/loom/plans/2026-07-03-unfrozen-change.md"\n'
        "[change.budgets]\n"
        "run = 100000\n"
        "\n"
        "[[change]]\n"
        'id = "add-export-csv"\n'
        f'plan = "{plan_rel_b}"\n'
        "[change.budgets]\n"
        "run = 200000\n",
        encoding="utf-8",
    )

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    exit_code = main(
        ["next", "--project", str(project_path), "--skills-root", str(skills_root)]
    )

    assert exit_code == 0
    out = capsys.readouterr()
    payload = json.loads(out.out.strip())

    worktree_path_b = project_path / ".worktrees" / "loom-add-export-csv"
    assert payload["changeId"] == "add-export-csv"
    assert payload["projectPath"] == str(worktree_path_b.resolve())
    assert payload["branch"] == "loom/add-export-csv"

    assert "unfrozen-change" in out.err
    assert not (project_path / ".worktrees" / "loom-unfrozen-change").exists()

    state = load_state(loom_dir / "queue-state.json")
    assert state["unfrozen-change"]["status"] == "SKIPPED"
    assert "not found" in state["unfrozen-change"]["reason"]
    assert state["add-export-csv"]["status"] == "RUNNING"


def test_next_skips_when_plan_not_in_worktree(tmp_path, capsys):
    project_path = _make_tmp_git_repo(tmp_path)

    plan_rel = "docs/loom/plans/2026-07-03-uncommitted-plan.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(_PLAN_WITH_PASS, encoding="utf-8")
    # Deliberately NOT committed: check_frozen (main checkout) sees the
    # file (and its reviewer PASS line satisfies Form B), but
    # ensure_worktree's worktree (created from HEAD) will not.

    loom_dir = project_path / "docs" / "loom"
    (loom_dir / "QUEUE.toml").write_text(
        '[[change]]\n'
        'id = "uncommitted-plan"\n'
        f'plan = "{plan_rel}"\n'
        "[change.budgets]\n"
        "run = 100000\n",
        encoding="utf-8",
    )

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    exit_code = main(
        ["next", "--project", str(project_path), "--skills-root", str(skills_root)]
    )

    assert exit_code == 0
    out = capsys.readouterr()
    assert json.loads(out.out.strip()) == {"done": True}
    assert "uncommitted-plan" in out.err

    state = load_state(loom_dir / "queue-state.json")
    assert state["uncommitted-plan"]["status"] == "SKIPPED"
    reason = state["uncommitted-plan"]["reason"].lower()
    assert "not" in reason and "worktree" in reason
    # Teardown: the worktree + branch created for this entry are removed on
    # this skip path — SKIPPED has no automatic path back to QUEUED and
    # `status` doesn't surface the worktree field, so a leftover would be
    # undiscoverable; a later re-queue must start clean instead of hitting
    # ensure_worktree's branch-exists-without-worktree conflict.
    assert not (project_path / ".worktrees" / "loom-uncommitted-plan").exists()
    branch_check = subprocess.run(
        [
            "git",
            "-C",
            str(project_path),
            "show-ref",
            "--verify",
            "--quiet",
            "refs/heads/loom/uncommitted-plan",
        ],
        capture_output=True,
        text=True,
    )
    assert branch_check.returncode != 0, "branch loom/uncommitted-plan still exists"


def test_next_halts_after_two_consecutive_failures(tmp_path, capsys):
    # Task 10 circuit breaker (plan §Settled open questions 3): the two
    # most recent terminal (DONE/FAILED) entries are both FAILED and
    # consecutive → refuse before ever touching git/worktrees.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {"status": "FAILED", "reason": "boom"},
            "fix-login-redirect": {"status": "FAILED", "reason": "boom2"},
        },
    )
    skills_root = tmp_path / "skills"

    exit_code = main(
        ["next", "--project", str(project_path), "--skills-root", str(skills_root)]
    )

    assert exit_code == 3
    err = capsys.readouterr().err
    assert "add-export-csv" in err
    assert "fix-login-redirect" in err
    assert "HALT" in err


def test_next_does_not_halt_when_failures_not_consecutive(tmp_path, capsys):
    # Elaboration (in-scope, cheap): FAILED, DONE, FAILED — the two most
    # recent terminal entries are DONE then FAILED, not both FAILED, so the
    # breaker does not fire. All three entries are terminal (no QUEUED
    # left), so `next` reaches its normal empty-queue {"done": true} path.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {"status": "FAILED"},
            "fix-login-redirect": {"status": "DONE"},
            "add-dark-mode": {"status": "FAILED"},
        },
    )
    skills_root = tmp_path / "skills"

    exit_code = main(
        ["next", "--project", str(project_path), "--skills-root", str(skills_root)]
    )

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out.strip()) == {"done": True}


def test_next_override_halt_bypasses_breaker(tmp_path, capsys):
    project_path = _make_tmp_git_repo(tmp_path)

    plan_rel = "docs/loom/plans/2026-07-03-add-dark-mode.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(_PLAN_WITH_PASS, encoding="utf-8")
    _run_git(["add", plan_rel], project_path)
    _run_git(["commit", "-m", "add plan"], project_path)

    loom_dir = project_path / "docs" / "loom"
    (loom_dir / "QUEUE.toml").write_text(QUEUE_TOML, encoding="utf-8")
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {"status": "FAILED", "reason": "boom"},
            "fix-login-redirect": {"status": "FAILED", "reason": "boom2"},
        },
    )
    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    exit_code = main(
        [
            "next",
            "--project",
            str(project_path),
            "--skills-root",
            str(skills_root),
            "--override-halt",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["changeId"] == "add-dark-mode"


def test_next_exits_cleanly_on_queue_error_mid_scan(tmp_path, capsys):
    # Sanctioned addition from Task 9's round-2 quality review: a
    # QueueError raised mid-scan by ensure_worktree must not propagate as a
    # raw traceback — main() catches it and exits 1, like load_queue
    # failures already do.
    project_path = _make_tmp_git_repo(tmp_path)
    _run_git(["branch", "loom/add-export-csv"], project_path)

    plan_rel = "docs/loom/plans/2026-07-03-add-export-csv.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(_PLAN_WITH_PASS, encoding="utf-8")
    _run_git(["add", plan_rel], project_path)
    _run_git(["commit", "-m", "add plan"], project_path)

    loom_dir = project_path / "docs" / "loom"
    (loom_dir / "QUEUE.toml").write_text(
        '[[change]]\n'
        'id = "add-export-csv"\n'
        f'plan = "{plan_rel}"\n'
        "[change.budgets]\n"
        "run = 200000\n",
        encoding="utf-8",
    )

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    exit_code = main(
        ["next", "--project", str(project_path), "--skills-root", str(skills_root)]
    )

    assert exit_code == 1
    err = capsys.readouterr().err
    assert "ensure_worktree" in err
    assert "add-export-csv" in err


def test_mark_concurrent_writes_to_different_entries_both_persist(tmp_path):
    # Task 8: two `mark` invocations racing on the SAME state file but
    # DIFFERENT entries. Each process's read-modify-write is: load_state
    # -> mutate its own entry's record -> save_state (whole dict). Without
    # a lock held across that full span, both processes can read the
    # pre-race state, sleep (widened here via the env-var test hook so the
    # overlap is deterministic instead of a timing coin-flip), then each
    # write back a dict that only contains ITS OWN entry — whichever
    # process's save_state runs last wins and silently drops the other's
    # update (lost-update race). With the fix, one process holds the
    # sidecar `<state>.lock` flock(LOCK_EX) across its entire
    # read-modify-write span, so the second process's read is forced to
    # happen after the first's write completes — both updates survive.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    script_path = Path(__file__).resolve().parent / "batch_queue.py"

    env = dict(os.environ)
    env["LOOM_BATCH_QUEUE_TEST_RMW_SLEEP"] = "0.3"

    proc_a = subprocess.Popen(
        [
            sys.executable,
            str(script_path),
            "mark",
            "add-export-csv",
            "done",
            "--project",
            str(project_path),
            "--run-id",
            "wf_a",
        ],
        env=env,
    )
    proc_b = subprocess.Popen(
        [
            sys.executable,
            str(script_path),
            "mark",
            "fix-login-redirect",
            "failed",
            "--project",
            str(project_path),
            "--reason",
            "boom",
        ],
        env=env,
    )

    assert proc_a.wait(timeout=15) == 0
    assert proc_b.wait(timeout=15) == 0

    state = load_state(loom_dir / "queue-state.json")
    assert state["add-export-csv"]["status"] == "DONE"
    assert state["add-export-csv"]["runId"] == "wf_a"
    assert state["fix-login-redirect"]["status"] == "FAILED"
    assert state["fix-login-redirect"]["reason"] == "boom"


def test_next_records_dispatched_at_iso_timestamp(tmp_path, capsys):
    # Task 9 (design SSOT §4c Fix 1 revised design point 1): _dispatch_entry
    # additionally records a wall-clock ISO-8601 dispatched_at — this CLI is
    # a fresh process each invocation, so it is exempt from Workflow
    # determinism rules.
    project_path = _make_tmp_git_repo(tmp_path)

    plan_rel = "docs/loom/plans/2026-07-03-add-export-csv.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(_PLAN_WITH_PASS, encoding="utf-8")
    _run_git(["add", plan_rel], project_path)
    _run_git(["commit", "-m", "add plan"], project_path)

    loom_dir = project_path / "docs" / "loom"
    (loom_dir / "QUEUE.toml").write_text(
        '[[change]]\n'
        'id = "add-export-csv"\n'
        f'plan = "{plan_rel}"\n'
        "[change.budgets]\n"
        "run = 200000\n",
        encoding="utf-8",
    )

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    before = datetime.now(timezone.utc)
    exit_code = main(
        ["next", "--project", str(project_path), "--skills-root", str(skills_root)]
    )
    after = datetime.now(timezone.utc)

    assert exit_code == 0
    state = load_state(loom_dir / "queue-state.json")
    dispatched_at = state["add-export-csv"]["dispatched_at"]
    parsed = datetime.fromisoformat(dispatched_at)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    assert before <= parsed <= after


def test_mark_running_records_run_id_and_session_dir(tmp_path):
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {
                "status": "RUNNING",
                "branch": "loom/add-export-csv",
                "worktree": str(project_path / ".worktrees" / "loom-add-export-csv"),
                "dispatched_at": "2026-07-18T00:00:00+00:00",
            }
        },
    )

    exit_code = main(
        [
            "mark-running",
            "add-export-csv",
            "--project",
            str(project_path),
            "--run-id",
            "wf_123",
            "--session-dir",
            "/tmp/session-abc/workflows",
        ]
    )

    assert exit_code == 0
    state = load_state(loom_dir / "queue-state.json")
    record = state["add-export-csv"]
    assert record["status"] == "RUNNING"
    assert record["runId"] == "wf_123"
    assert record["sessionDir"] == "/tmp/session-abc/workflows"


def test_mark_running_wrong_state_errors_without_mutation(tmp_path, capsys):
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {"add-export-csv": {"status": "DONE", "runId": "wf_old"}},
    )

    exit_code = main(
        [
            "mark-running",
            "add-export-csv",
            "--project",
            str(project_path),
            "--run-id",
            "wf_new",
            "--session-dir",
            "/tmp/session-abc/workflows",
        ]
    )

    assert exit_code != 0
    assert "add-export-csv" in capsys.readouterr().err
    state = load_state(loom_dir / "queue-state.json")
    assert state["add-export-csv"] == {"status": "DONE", "runId": "wf_old"}


def test_mark_running_fails_loud_on_unknown_change_id(tmp_path, capsys):
    project_path = tmp_path / "project"
    _write_queue(project_path)

    exit_code = main(
        [
            "mark-running",
            "does-not-exist",
            "--project",
            str(project_path),
            "--run-id",
            "wf_1",
            "--session-dir",
            "/tmp/session-abc/workflows",
        ]
    )

    assert exit_code != 0
    assert "does-not-exist" in capsys.readouterr().err


def test_reset_from_running_requeues_increments_attempts_and_appends_audit(tmp_path):
    # Task 10 / design SSOT §4c: reset is allowed from RUNNING -> QUEUED,
    # attempts increments (initialized to 0 when absent), and an
    # append-only audit[] line records {verb, timestamp, reason}.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {
                "status": "RUNNING",
                "branch": "loom/add-export-csv",
                "worktree": str(project_path / ".worktrees" / "loom-add-export-csv"),
            }
        },
    )

    before = datetime.now(timezone.utc)
    exit_code = main(
        ["reset", "add-export-csv", "--project", str(project_path)]
    )
    after = datetime.now(timezone.utc)

    assert exit_code == 0
    state = load_state(loom_dir / "queue-state.json")
    record = state["add-export-csv"]
    assert record["status"] == "QUEUED"
    assert record["attempts"] == 1
    assert len(record["audit"]) == 1
    audit_line = record["audit"][0]
    assert audit_line["verb"] == "reset"
    # schema is {verb, timestamp, reason} uniformly on every line — "reason"
    # must be present even when no --reason was given (empty string, not
    # a dropped key).
    assert audit_line["reason"] == ""
    parsed = datetime.fromisoformat(audit_line["timestamp"])
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    assert before <= parsed <= after


def test_reset_from_running_clears_stale_run_fields(tmp_path):
    # cq finding (round 2): a RUNNING entry carries runId/sessionDir/
    # dispatched_at from the crashed attempt. Task 12's upcoming reconcile
    # runs before the next dispatch, and a stale runId paired with a
    # terminal wf-record would force-FAIL a just-restarted entry — reset
    # must clear these live-run-only fields since a QUEUED entry has no
    # live run.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {
                "status": "RUNNING",
                "branch": "loom/add-export-csv",
                "worktree": str(project_path / ".worktrees" / "loom-add-export-csv"),
                "runId": "wf_stale123",
                "sessionDir": "/tmp/stale-session",
                "dispatched_at": "2026-01-01T00:00:00+00:00",
            }
        },
    )

    exit_code = main(
        ["reset", "add-export-csv", "--project", str(project_path)]
    )

    assert exit_code == 0
    state = load_state(loom_dir / "queue-state.json")
    record = state["add-export-csv"]
    assert "runId" not in record
    assert "sessionDir" not in record
    assert "dispatched_at" not in record


def test_reset_from_failed_requeues_and_initializes_attempts_from_absent(tmp_path):
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {"add-export-csv": {"status": "FAILED", "reason": "boom"}},
    )

    exit_code = main(
        [
            "reset",
            "add-export-csv",
            "--project",
            str(project_path),
            "--reason",
            "operator retry after flaky infra",
        ]
    )

    assert exit_code == 0
    state = load_state(loom_dir / "queue-state.json")
    record = state["add-export-csv"]
    assert record["status"] == "QUEUED"
    assert record["attempts"] == 1
    assert len(record["audit"]) == 1
    assert record["audit"][0]["verb"] == "reset"
    assert record["audit"][0]["reason"] == "operator retry after flaky infra"


def test_reset_wrong_state_errors_without_mutation(tmp_path, capsys):
    # reset is only allowed from RUNNING or FAILED; a DONE entry must be
    # rejected with zero mutation (no state change, no audit line).
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {"add-export-csv": {"status": "DONE", "runId": "wf_1"}},
    )

    exit_code = main(
        ["reset", "add-export-csv", "--project", str(project_path)]
    )

    assert exit_code != 0
    assert "add-export-csv" in capsys.readouterr().err
    state = load_state(loom_dir / "queue-state.json")
    assert state["add-export-csv"] == {"status": "DONE", "runId": "wf_1"}


def test_reset_fails_loud_on_unknown_change_id(tmp_path, capsys):
    project_path = tmp_path / "project"
    _write_queue(project_path)

    exit_code = main(
        ["reset", "does-not-exist", "--project", str(project_path)]
    )

    assert exit_code != 0
    assert "does-not-exist" in capsys.readouterr().err


def test_force_fail_from_running_transitions_and_appends_audit(tmp_path):
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {"add-export-csv": {"status": "RUNNING", "branch": "loom/add-export-csv"}},
    )

    before = datetime.now(timezone.utc)
    exit_code = main(
        [
            "force-fail",
            "add-export-csv",
            "--reason",
            "operator confirmed stuck session",
            "--project",
            str(project_path),
        ]
    )
    after = datetime.now(timezone.utc)

    assert exit_code == 0
    state = load_state(loom_dir / "queue-state.json")
    record = state["add-export-csv"]
    assert record["status"] == "FAILED"
    assert len(record["audit"]) == 1
    audit_line = record["audit"][0]
    assert audit_line["verb"] == "force-fail"
    assert audit_line["reason"] == "operator confirmed stuck session"
    parsed = datetime.fromisoformat(audit_line["timestamp"])
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    assert before <= parsed <= after


def test_force_fail_counts_toward_circuit_breaker(tmp_path):
    # design SSOT §4c: "resulting FAILED counts toward the existing circuit
    # breaker naturally" — verified via the breaker's own predicate against
    # two consecutive force-failed entries (no separate breaker logic).
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {"status": "RUNNING"},
            "fix-login-redirect": {"status": "RUNNING"},
        },
    )

    assert main(
        [
            "force-fail",
            "add-export-csv",
            "--reason",
            "stuck",
            "--project",
            str(project_path),
        ]
    ) == 0
    assert main(
        [
            "force-fail",
            "fix-login-redirect",
            "--reason",
            "stuck-too",
            "--project",
            str(project_path),
        ]
    ) == 0

    entries = load_queue(loom_dir / "QUEUE.toml")
    state = load_state(loom_dir / "queue-state.json")
    merged = effective_entries(entries, state)
    assert _check_circuit_breaker(merged) == ("add-export-csv", "fix-login-redirect")


def test_force_fail_wrong_state_errors_without_mutation(tmp_path, capsys):
    # force-fail is only allowed from RUNNING; an already-FAILED entry must
    # be rejected with zero mutation (no double audit line).
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {"add-export-csv": {"status": "FAILED", "reason": "boom"}},
    )

    exit_code = main(
        [
            "force-fail",
            "add-export-csv",
            "--reason",
            "trying again",
            "--project",
            str(project_path),
        ]
    )

    assert exit_code != 0
    assert "add-export-csv" in capsys.readouterr().err
    state = load_state(loom_dir / "queue-state.json")
    assert state["add-export-csv"] == {"status": "FAILED", "reason": "boom"}


def test_force_fail_fails_loud_on_unknown_change_id(tmp_path, capsys):
    project_path = tmp_path / "project"
    _write_queue(project_path)

    exit_code = main(
        [
            "force-fail",
            "does-not-exist",
            "--reason",
            "gone",
            "--project",
            str(project_path),
        ]
    )

    assert exit_code != 0
    assert "does-not-exist" in capsys.readouterr().err


def test_force_fail_requires_reason_argument(tmp_path, capsys):
    project_path = tmp_path / "project"
    _write_queue(project_path)

    with pytest.raises(SystemExit) as exc_info:
        main(["force-fail", "add-export-csv", "--project", str(project_path)])

    assert exc_info.value.code != 0


# --- _read_wf_terminal_status (Task 11): opportunistic wf-record evidence ---
# reader. The wf_<runId>.json format is UNDOCUMENTED host internals (design
# SSOT §4c) — every non-definitive case (absent/corrupt/invalid-utf8/
# missing-status/unrecognized-status/traversal) must return None, never raise.


@pytest.mark.parametrize("status", ["completed", "failed", "killed"])
def test_read_wf_terminal_status_returns_recognized_terminal_status(tmp_path, status):
    session_dir = tmp_path / "session"
    workflows_dir = session_dir / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "wf_run1.json").write_text(
        json.dumps({"runId": "run1", "status": status}), encoding="utf-8"
    )

    assert _read_wf_terminal_status("run1", session_dir) == status


def test_read_wf_terminal_status_returns_none_when_file_absent(tmp_path):
    session_dir = tmp_path / "session"
    session_dir.mkdir()

    assert _read_wf_terminal_status("missing-run", session_dir) is None


def test_read_wf_terminal_status_returns_none_when_session_dir_absent(tmp_path):
    assert _read_wf_terminal_status("run1", tmp_path / "no-such-session") is None


def test_read_wf_terminal_status_returns_none_on_corrupt_json(tmp_path):
    workflows_dir = tmp_path / "session" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "wf_run2.json").write_text("{not valid json", encoding="utf-8")

    assert _read_wf_terminal_status("run2", tmp_path / "session") is None


def test_read_wf_terminal_status_returns_none_on_non_object_json(tmp_path):
    workflows_dir = tmp_path / "session" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "wf_run6.json").write_text(
        json.dumps(["completed"]), encoding="utf-8"
    )

    assert _read_wf_terminal_status("run6", tmp_path / "session") is None


def test_read_wf_terminal_status_returns_none_on_invalid_utf8(tmp_path):
    workflows_dir = tmp_path / "session" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "wf_run3.json").write_bytes(b"\xff\xfe\xfd")

    assert _read_wf_terminal_status("run3", tmp_path / "session") is None


def test_read_wf_terminal_status_returns_none_when_status_missing(tmp_path):
    workflows_dir = tmp_path / "session" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "wf_run4.json").write_text(
        json.dumps({"runId": "run4"}), encoding="utf-8"
    )

    assert _read_wf_terminal_status("run4", tmp_path / "session") is None


def test_read_wf_terminal_status_returns_none_on_unrecognized_status(tmp_path):
    workflows_dir = tmp_path / "session" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "wf_run5.json").write_text(
        json.dumps({"status": "running"}), encoding="utf-8"
    )

    assert _read_wf_terminal_status("run5", tmp_path / "session") is None


@pytest.mark.parametrize("bad_run_id", ["../escape", "a/b", "a\\b", ".."])
def test_read_wf_terminal_status_rejects_path_traversal_run_id(tmp_path, bad_run_id):
    session_dir = tmp_path / "session"
    (session_dir / "workflows").mkdir(parents=True)

    assert _read_wf_terminal_status(bad_run_id, session_dir) is None


@pytest.mark.parametrize("bad_session_dir", [None, 42, ["a", "b"]])
def test_read_wf_terminal_status_returns_none_on_invalid_session_dir_type(bad_session_dir):
    # Prerequisite fix (Task 12, from Task 11's round-2 review): an entry
    # with a runId but no sessionDir recorded yet (mark-running has not run)
    # must degrade to "no evidence" rather than raising TypeError from
    # Path(None). Task 12's reconcile relies on this to route such entries
    # into its staleness-only path instead of crashing.
    assert _read_wf_terminal_status("run1", bad_session_dir) is None


# --- reconcile (Task 12): auto-FAIL on definitive wf evidence, SUSPECT-COMPLETE
# / SUSPECT flags on ambiguous evidence, never on ``status``. ---


def _write_wf_record(session_dir: Path, run_id: str, status: str) -> None:
    workflows_dir = session_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    (workflows_dir / f"wf_{run_id}.json").write_text(
        json.dumps({"runId": run_id, "status": status}), encoding="utf-8"
    )


def _iso(dt: datetime) -> str:
    return dt.isoformat()


@pytest.mark.parametrize("wf_status", ["failed", "killed"])
def test_reconcile_auto_fails_running_entries_with_terminal_wf_evidence_and_trips_breaker(
    tmp_path, capsys, wf_status
):
    # (a) definitive wf-record evidence (failed/killed) force-transitions
    # RUNNING -> FAILED with an audit line naming the wf status; two such
    # transitions are then visible to _check_circuit_breaker "naturally"
    # (same shape as force-fail's own breaker test).
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    session_dir_a = tmp_path / "session-a"
    session_dir_b = tmp_path / "session-b"
    _write_wf_record(session_dir_a, "wf_a", wf_status)
    _write_wf_record(session_dir_b, "wf_b", "failed")
    now = datetime.now(timezone.utc)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {
                "status": "RUNNING",
                "runId": "wf_a",
                "sessionDir": str(session_dir_a),
                "dispatched_at": _iso(now),
            },
            "fix-login-redirect": {
                "status": "RUNNING",
                "runId": "wf_b",
                "sessionDir": str(session_dir_b),
                "dispatched_at": _iso(now),
            },
        },
    )

    exit_code = main(["reconcile", "--project", str(project_path)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "add-export-csv" in out and "AUTO-FAILED" in out
    assert "fix-login-redirect" in out and "AUTO-FAILED" in out

    state = load_state(loom_dir / "queue-state.json")
    record_a = state["add-export-csv"]
    assert record_a["status"] == "FAILED"
    assert len(record_a["audit"]) == 1
    assert record_a["audit"][0]["verb"] == "reconcile"
    assert wf_status in record_a["audit"][0]["reason"]
    assert state["fix-login-redirect"]["status"] == "FAILED"

    entries = load_queue(loom_dir / "QUEUE.toml")
    merged = effective_entries(entries, state)
    assert _check_circuit_breaker(merged) == ("add-export-csv", "fix-login-redirect")


def test_reconcile_flags_suspect_complete_without_transitioning(tmp_path, capsys):
    # (b) wf-record says "completed" but the entry was never marked done via
    # `mark` — flag SUSPECT-COMPLETE, NO status transition (human confirms).
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    session_dir = tmp_path / "session"
    _write_wf_record(session_dir, "wf_c", "completed")
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {
                "status": "RUNNING",
                "runId": "wf_c",
                "sessionDir": str(session_dir),
                "dispatched_at": _iso(datetime.now(timezone.utc)),
            }
        },
    )

    exit_code = main(["reconcile", "--project", str(project_path)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "add-export-csv" in out and "SUSPECT-COMPLETE" in out

    state = load_state(loom_dir / "queue-state.json")
    assert state["add-export-csv"]["status"] == "RUNNING"
    assert "audit" not in state["add-export-csv"]


def test_reconcile_flags_suspect_on_stale_missing_run_id(tmp_path, capsys):
    # (c) no runId recorded yet (mark-running never ran) and dispatched_at
    # beyond the short 10-minute grace window -> loud SUSPECT, no transition.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    stale_dispatch = datetime.now(timezone.utc) - timedelta(minutes=11)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {
                "status": "RUNNING",
                "dispatched_at": _iso(stale_dispatch),
            }
        },
    )

    exit_code = main(["reconcile", "--project", str(project_path)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "add-export-csv" in out and "SUSPECT" in out
    assert "AUTO-FAILED" not in out and "SUSPECT-COMPLETE" not in out

    state = load_state(loom_dir / "queue-state.json")
    assert state["add-export-csv"]["status"] == "RUNNING"
    assert "audit" not in state["add-export-csv"]


def test_reconcile_flags_suspect_on_stale_no_wf_evidence_with_run_id(tmp_path, capsys):
    # (c) runId + sessionDir recorded, but no wf-record file exists (session
    # died before any record was written) and dispatched_at is beyond the
    # longer 2-hour grace window -> loud SUSPECT, no transition.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    session_dir = tmp_path / "session-dead"
    stale_dispatch = datetime.now(timezone.utc) - timedelta(hours=3)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {
                "status": "RUNNING",
                "runId": "wf_dead",
                "sessionDir": str(session_dir),
                "dispatched_at": _iso(stale_dispatch),
            }
        },
    )

    exit_code = main(["reconcile", "--project", str(project_path)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "add-export-csv" in out and "SUSPECT" in out

    state = load_state(loom_dir / "queue-state.json")
    assert state["add-export-csv"]["status"] == "RUNNING"


def test_reconcile_does_not_flag_fresh_running_entry_with_no_evidence(tmp_path, capsys):
    # A RUNNING entry with no runId yet but freshly dispatched (well inside
    # the 10-minute grace window) is normal in-flight state — no flag, no
    # transition, nothing printed.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {
                "status": "RUNNING",
                "dispatched_at": _iso(datetime.now(timezone.utc)),
            }
        },
    )

    exit_code = main(["reconcile", "--project", str(project_path)])

    assert exit_code == 0
    assert capsys.readouterr().out == ""
    state = load_state(loom_dir / "queue-state.json")
    assert state["add-export-csv"]["status"] == "RUNNING"


def test_reconcile_is_idempotent_across_two_runs(tmp_path, capsys):
    # Reconcile twice with no new evidence in between must reproduce
    # identical on-disk state: the first run's AUTO-FAILED transition gates
    # future runs off (no longer RUNNING), and SUSPECT/SUSPECT-COMPLETE never
    # mutate to begin with.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    session_dir_failed = tmp_path / "session-failed"
    session_dir_completed = tmp_path / "session-completed"
    _write_wf_record(session_dir_failed, "wf_x", "failed")
    _write_wf_record(session_dir_completed, "wf_y", "completed")
    now = datetime.now(timezone.utc)
    stale = now - timedelta(hours=3)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {
                "status": "RUNNING",
                "runId": "wf_x",
                "sessionDir": str(session_dir_failed),
                "dispatched_at": _iso(now),
            },
            "fix-login-redirect": {
                "status": "RUNNING",
                "runId": "wf_y",
                "sessionDir": str(session_dir_completed),
                "dispatched_at": _iso(now),
            },
            "add-dark-mode": {
                "status": "RUNNING",
                "dispatched_at": _iso(stale),
            },
        },
    )

    main(["reconcile", "--project", str(project_path)])
    capsys.readouterr()
    state_after_round1 = load_state(loom_dir / "queue-state.json")

    main(["reconcile", "--project", str(project_path)])
    state_after_round2 = load_state(loom_dir / "queue-state.json")

    assert state_after_round1 == state_after_round2


def test_status_performs_no_reconciliation(tmp_path, capsys):
    # `status` must stay a pure query: a RUNNING entry with definitive
    # failed wf-record evidence (which `reconcile` WOULD force-FAIL) must be
    # left completely untouched by `status`.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    session_dir = tmp_path / "session"
    _write_wf_record(session_dir, "wf_z", "failed")
    state_before = {
        "add-export-csv": {
            "status": "RUNNING",
            "runId": "wf_z",
            "sessionDir": str(session_dir),
            "dispatched_at": _iso(datetime.now(timezone.utc)),
        }
    }
    save_state(loom_dir / "queue-state.json", state_before)

    exit_code = main(["status", "--project", str(project_path)])

    assert exit_code == 0
    state_after = load_state(loom_dir / "queue-state.json")
    assert state_after == state_before


def test_next_reconciles_running_entries_before_normal_scan(tmp_path, capsys):
    # Task 12: `next` runs reconcile's logic first, then proceeds with its
    # normal scan — a stranded RUNNING entry with failed wf-record evidence
    # gets force-FAILED (with a reconcile audit line) in the SAME `next`
    # invocation that goes on to dispatch the next QUEUED entry.
    project_path = _make_tmp_git_repo(tmp_path)

    plan_rel = "docs/loom/plans/2026-07-03-add-dark-mode.md"
    plan_path = project_path / plan_rel
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(_PLAN_WITH_PASS, encoding="utf-8")
    _run_git(["add", plan_rel], project_path)
    _run_git(["commit", "-m", "add plan"], project_path)

    loom_dir = project_path / "docs" / "loom"
    (loom_dir / "QUEUE.toml").write_text(QUEUE_TOML, encoding="utf-8")

    session_dir = tmp_path / "dead-session"
    _write_wf_record(session_dir, "wf_stranded", "killed")
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {
                "status": "RUNNING",
                "runId": "wf_stranded",
                "sessionDir": str(session_dir),
                "dispatched_at": _iso(datetime.now(timezone.utc)),
            }
        },
    )

    skills_root = tmp_path / "skills"
    _write_stub_validator(skills_root, exit_code=0)

    exit_code = main(
        ["next", "--project", str(project_path), "--skills-root", str(skills_root)]
    )

    assert exit_code == 0
    out = capsys.readouterr()
    assert "add-export-csv" in out.err and "AUTO-FAILED" in out.err

    # "fix-login-redirect" has no plan file at all in this fixture (only
    # add-dark-mode's plan was committed), so the normal scan skips it and
    # dispatches add-dark-mode — proving reconcile ran BEFORE, not INSTEAD
    # of, the normal scan.
    payload = json.loads(out.out.strip())
    assert payload["changeId"] == "add-dark-mode"

    state = load_state(loom_dir / "queue-state.json")
    assert state["add-export-csv"]["status"] == "FAILED"
    assert state["add-export-csv"]["audit"][0]["verb"] == "reconcile"
    assert state["fix-login-redirect"]["status"] == "SKIPPED"
    assert state["add-dark-mode"]["status"] == "RUNNING"


# --- Task 13: `next`'s done derivation is `terminal_count == total`; a
# non-terminal remainder (QUEUED/RUNNING) blocks `done: true` and is
# enumerated loudly (id + status + why) in the same stdout payload. ---


def test_next_reports_not_done_when_running_entry_remains(tmp_path, capsys):
    # A stranded RUNNING entry (no runId yet — mark-running hasn't run —
    # dispatched well past the 10-minute no-runId grace window) is neither
    # QUEUED nor terminal: `next` must not claim `done: true` while it is
    # still outstanding, and must enumerate it instead of silently treating
    # the batch as finished.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    stale_dispatch = datetime.now(timezone.utc) - timedelta(minutes=11)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {"status": "DONE"},
            "fix-login-redirect": {
                "status": "RUNNING",
                "dispatched_at": _iso(stale_dispatch),
            },
            "add-dark-mode": {"status": "DONE"},
        },
    )
    skills_root = tmp_path / "skills"

    exit_code = main(
        ["next", "--project", str(project_path), "--skills-root", str(skills_root)]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["done"] is False
    assert len(payload["non_terminal"]) == 1
    blocking = payload["non_terminal"][0]
    assert blocking["id"] == "fix-login-redirect"
    assert blocking["status"] == "RUNNING"
    assert "no runId recorded yet" in blocking["reason"]


def test_next_reports_done_when_all_entries_terminal_including_skipped(tmp_path, capsys):
    # Documents the chosen terminal set for the done check: DONE, FAILED,
    # AND SKIPPED all count as terminal — a SKIPPED entry has no automatic
    # path back to QUEUED (only a human running `reset`, which only accepts
    # RUNNING/FAILED, ever revives one), so it must not keep `done` stuck at
    # false forever. Only QUEUED/RUNNING keep a batch open.
    project_path = tmp_path / "project"
    loom_dir = _write_queue(project_path)
    save_state(
        loom_dir / "queue-state.json",
        {
            "add-export-csv": {"status": "DONE"},
            "fix-login-redirect": {"status": "FAILED"},
            "add-dark-mode": {"status": "SKIPPED", "reason": "unfrozen"},
        },
    )
    skills_root = tmp_path / "skills"

    exit_code = main(
        ["next", "--project", str(project_path), "--skills-root", str(skills_root)]
    )

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out.strip()) == {"done": True}


# --- Sanctioned rider (Task 12 review, same files): _parse_iso_timestamp's
# fail-safe branches (missing / malformed dispatched_at) had no direct test
# — both must classify as SUSPECT without raising or transitioning. ---


def test_classify_running_entry_suspect_when_dispatched_at_missing():
    record = {"status": "RUNNING"}  # dispatched_at absent entirely

    category, evidence = _classify_running_entry(record)

    assert category == "SUSPECT"
    assert "dispatched_at missing/unparseable" in evidence


def test_classify_running_entry_suspect_when_dispatched_at_malformed():
    record = {"status": "RUNNING", "dispatched_at": "not-a-date"}

    category, evidence = _classify_running_entry(record)

    assert category == "SUSPECT"
    assert "dispatched_at missing/unparseable" in evidence
