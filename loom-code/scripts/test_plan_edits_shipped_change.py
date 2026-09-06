"""Permanent tests for the plan-edits shipped-change carve-out (W1-01):
`loom_checker.py plan-edits <change-id>` reports NOT APPLICABLE, at exit
0, when a change's intent is closed and its plan commit is absent --
instead of the ordinary BLOCK `no plan commit found`.

These are written independently of the adversary's RED probes at
docs/loom/2026-09-06-graduated-probes-survive-squash/evidence/probes/
test_abuse_plan_edits_shipped.py -- same interface, own fixtures -- so
the rule stays covered once that evidence file is archived. See that
file's helpers (`test_plan_edits_after_commit.py`'s `seed_plan` /
`edit_plan` shape too) for the pattern this follows.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

CHECKER = Path(__file__).resolve().parent / "loom_checker.py"
CHANGE_ID = "2099-03-03-permanent-shipped-plan-edits-check"

# The literal em dash `STATUS_CLOSED_LITERAL` expects in loom_checker.py --
# spelled out here rather than hand-typed as a hyphen-minus.
EM_DASH = "—"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_plan_edits(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), "plan-edits", CHANGE_ID],
        capture_output=True, text=True, cwd=str(repo),
    )


def plan_path(repo: Path) -> Path:
    return repo / "docs" / "loom" / CHANGE_ID / "plan.md"


def intent_path(repo: Path) -> Path:
    return repo / "docs" / "loom" / "intent" / f"{CHANGE_ID}.md"


def base_plan_text() -> str:
    return "\n".join([
        f"# Permanent shipped-plan-edits check -- {CHANGE_ID}",
        f"intent: {CHANGE_ID}@0000000",
        "charter: 1.0",
        "",
        "## Current State Evidence",
        "- Forward: some/file.py:1 names the gap here.",
        "",
        "## Task DAG",
        "",
        "**W1 First task**  after: --",
        "- Files: x.py, y.py",
        "- Test: the base test passes",
        "- Risk: agent-decided -- low",
        "",
        "## Questions asked",
        f"① {EM_DASH} what {EM_DASH} one recorded question and its answer.",
        "",
        "## Risks",
        f"1. agent-decided {EM_DASH} one bounded risk, one line.",
        "",
    ])


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "perm@example.com")
    git(repo, "config", "user.name", "Permanent")
    return repo


def write_intent(repo: Path, front_status_line: str) -> None:
    """Writes `intent/<change-id>.md` with a real frontmatter `status:`
    line. Not committed here -- a test that needs the closed status to be a
    shipped fact commits it explicitly, because the amnesty (W1-01) reads
    the closed status from committed history reachable from HEAD, not from
    the working tree."""
    path = intent_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join([
            f"# Permanent shipped-plan-edits check -- {CHANGE_ID}",
            "originator: adversary",
            "kind: engineering",
            "needs-design: no -- probe fixture",
            front_status_line,
            "",
            "## Problem",
            "",
            "",
        ]),
        encoding="utf-8",
    )


def write_plan_without_commit(repo: Path, text: str) -> None:
    """Writes `plan.md` without committing anything -- so neither the plan
    nor any staged intent is committed, and `find_plan_commit_sha` finds
    nothing while the working tree stays dirty."""
    path = plan_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def seed_plan_without_commit(repo: Path, text: str) -> None:
    """Commits `plan.md` under an ordinary message -- never `docs(loom):
    plan <change-id>` -- so `find_plan_commit_sha` finds nothing. Note the
    `git add -A` also commits any uncommitted intent staged alongside."""
    path = plan_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: seed plan without the sign-off commit")


def seed_plan_with_commit(repo: Path, text: str) -> None:
    path = plan_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"docs(loom): plan {CHANGE_ID}")


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def combined_output(result: subprocess.CompletedProcess) -> str:
    return result.stdout + result.stderr


def test_closed_intent_missing_commit_reports_not_applicable(tmp_path: Path) -> None:
    """A shipped change (`status: closed ...`) whose plan commit is
    absent exits 0 and names the outcome NOT APPLICABLE."""
    repo = init_repo(tmp_path)
    write_intent(repo, f"status: closed 2026-09-01 {EM_DASH} PR #123")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): close intent")
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 0, result.stderr
    assert re.search(r"not.applicable", combined_output(result), re.I)


def test_uncommitted_closed_status_still_blocks(tmp_path: Path) -> None:
    """An uncommitted working-tree `status: closed` is not a shipped fact
    -- the amnesty requires a committed closed status reachable from HEAD,
    so an in-flight change with a lost plan commit still BLOCKs."""
    repo = init_repo(tmp_path)
    write_intent(repo, f"status: closed 2026-09-01 {EM_DASH} PR #123")
    write_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)
    assert "no plan commit found" in result.stderr


def test_deleted_intent_after_historical_closure_still_blocks(tmp_path: Path) -> None:
    """A current intent deleted after a historical close is in-flight --
    the amnesty requires a parseable current intent, so it still BLOCKs."""
    repo = init_repo(tmp_path)
    write_intent(repo, f"status: closed 2026-09-01 {EM_DASH} PR #123")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): close intent")
    intent_path(repo).unlink()
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_malformed_intent_after_historical_closure_still_blocks(tmp_path: Path) -> None:
    """A current intent whose status line is malformed after a historical
    close is in-flight -- the amnesty requires a parseable current intent,
    so it still BLOCKs."""
    repo = init_repo(tmp_path)
    write_intent(repo, f"status: closed 2026-09-01 {EM_DASH} PR #123")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): close intent")
    write_intent(repo, "status: closed banana -- not a real date or descriptor")
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_unreadable_intent_after_historical_closure_still_blocks(tmp_path: Path) -> None:
    """A current intent that cannot be read after a historical close is
    in-flight -- the amnesty requires a readable current intent, so it
    still BLOCKs. Skipped when running as root, which can read a 000-mode
    file."""
    if os.geteuid() == 0:
        pytest.skip("running as root; a 000-mode file is still readable")
    repo = init_repo(tmp_path)
    write_intent(repo, f"status: closed 2026-09-01 {EM_DASH} PR #123")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): close intent")
    seed_plan_without_commit(repo, base_plan_text())
    intent_path(repo).chmod(0)
    try:
        result = run_plan_edits(repo)
        assert result.returncode == 1
        assert "plan.edits-after-commit" in blocked_rules(result)
        assert "no plan commit found" in result.stderr
    finally:
        intent_path(repo).chmod(0o644)


def test_confirmed_intent_missing_commit_still_blocks(tmp_path: Path) -> None:
    """An in-flight change's missing plan commit is never amnesty on its
    own -- still BLOCKs."""
    repo = init_repo(tmp_path)
    write_intent(repo, "status: confirmed 2026-09-01")
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)
    assert "no plan commit found" in result.stderr


def test_closed_intent_present_commit_tampered_still_blocks(tmp_path: Path) -> None:
    """A closed intent is not a blanket amnesty: with the plan commit
    present, a landed task's Files line edited afterwards still BLOCKs."""
    repo = init_repo(tmp_path)
    write_intent(repo, f"status: closed 2026-09-01 {EM_DASH} PR #123")
    seed_plan_with_commit(repo, base_plan_text())
    marker = repo / "landed-W1.txt"
    marker.write_text("ok\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: land W1\n\nTask: W1")
    tampered = base_plan_text().replace(
        "- Files: x.py, y.py", "- Files: x.py, y.py, z.py"
    )
    plan_path(repo).write_text(tampered, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix(loom): sneak an extra file past a closed intent")
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_absent_intent_file_missing_commit_still_blocks(tmp_path: Path) -> None:
    """No intent file at all is treated as in-flight -- still BLOCKs."""
    repo = init_repo(tmp_path)
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_malformed_status_line_missing_commit_still_blocks(tmp_path: Path) -> None:
    """A status line that fails to parse as closed at all is in-flight --
    still BLOCKs, never crashes, never silently passes."""
    repo = init_repo(tmp_path)
    write_intent(repo, "status: closed banana -- not a real date or descriptor")
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_closed_then_reverted_status_reports_not_applicable(tmp_path: Path) -> None:
    """A `status: closed ...` line committed once, then reverted back to
    `confirmed` in a later commit, still recomputes closed from history
    (mirroring `check_intent_not_reopened`, loom_checker.py:1410) -- a
    reverted status line does not resurrect a live edit window."""
    repo = init_repo(tmp_path)
    write_intent(repo, f"status: closed 2026-09-01 {EM_DASH} PR #123")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): close intent")
    write_intent(repo, "status: confirmed 2026-09-01")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: revert status line back to confirmed")
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 0, result.stderr
    assert re.search(r"not.applicable", combined_output(result), re.I)


def test_not_applicable_output_differs_from_silent_pass(tmp_path: Path) -> None:
    """An ordinary untouched-plan pass is silent; a NOT APPLICABLE outcome
    is also exit 0 but must never be silent in the same way."""
    repo = init_repo(tmp_path)
    write_intent(repo, "status: confirmed 2026-09-01")
    seed_plan_with_commit(repo, base_plan_text())
    silent_pass = run_plan_edits(repo)
    assert silent_pass.returncode == 0
    assert silent_pass.stdout == "" and silent_pass.stderr == ""

    repo2_root = tmp_path / "second"
    repo2_root.mkdir()
    repo2 = init_repo(repo2_root)
    write_intent(repo2, f"status: closed 2026-09-01 {EM_DASH} PR #123")
    git(repo2, "add", "-A")
    git(repo2, "commit", "-q", "-m", "docs(loom): close intent")
    seed_plan_without_commit(repo2, base_plan_text())
    not_applicable = run_plan_edits(repo2)
    assert not_applicable.returncode == 0
    assert combined_output(not_applicable) != ""
