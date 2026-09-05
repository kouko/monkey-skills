"""Permanent tests for the `plan.edits-after-commit` rule and its
`loom_checker.py plan-edits <change-id>` sub-command (W1-02).

These are written independently of the adversary's RED probes at
docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/
probes/test_abuse_plan_edits.py -- same interface, different fixtures --
so the rule stays covered once that evidence file is archived.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).resolve().parent / "loom_checker.py"
CHANGE_ID = "2099-02-02-permanent-plan-edits-check"


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


def base_plan_text(*, w1_files: str = "x.py, y.py", w1_test: str = "the base test passes") -> str:
    return "\n".join([
        f"# Permanent plan check -- {CHANGE_ID}",
        f"intent: {CHANGE_ID}@0000000",
        "charter: 1.0",
        "",
        "## Current State Evidence",
        "- Forward: some/file.py:1 names the gap here.",
        "",
        "## Task DAG",
        "",
        "**W1 First task**  after: --",
        f"- Files: {w1_files}",
        f"- Test: {w1_test}",
        "- Risk: agent-decided -- low",
        "",
        "## Questions asked",
        "① — what — one recorded question and its answer.",
        "",
        "## Risks",
        "1. agent-decided -- one bounded risk, one line.",
        "",
    ])


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "perm@example.com")
    git(repo, "config", "user.name", "Permanent")
    return repo


def seed_plan(repo: Path, text: str) -> None:
    path = plan_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"docs(loom): plan {CHANGE_ID}")


def edit_plan(repo: Path, text: str, message: str) -> None:
    plan_path(repo).write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)


def land(repo: Path, task_id: str) -> None:
    marker = repo / f"landed-{task_id}.txt"
    marker.write_text("ok\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"feat: land {task_id}\n\nTask: {task_id}")


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def test_untouched_plan_since_its_commit_passes(tmp_path: Path) -> None:
    """A plan file identical to its own plan commit never blocks."""
    repo = init_repo(tmp_path)
    seed_plan(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 0, result.stderr


def test_claimed_mark_on_unlanded_task_passes(tmp_path: Path) -> None:
    """Appending `claimed(@x)` to a task's title line is allowed."""
    repo = init_repo(tmp_path)
    seed_plan(repo, base_plan_text())
    edited = base_plan_text().replace(
        "**W1 First task**  after: --", "**W1 First task** claimed(@dev)  after: --"
    )
    edit_plan(repo, edited, "chore(loom): claim W1")
    result = run_plan_edits(repo)
    assert result.returncode == 0, result.stderr


def test_appended_memory_task_passes(tmp_path: Path) -> None:
    """A brand new `**W1-memory ...**` task block is always allowed."""
    repo = init_repo(tmp_path)
    seed_plan(repo, base_plan_text())
    memory_block = (
        "\n**W1-memory Memory step**  after: W1\n"
        "- Files: docs/loom/memory/\n"
        "- Test: the memory entry exists\n"
        "- Risk: agent-decided -- none\n"
    )
    edited = base_plan_text().replace(
        "\n## Questions asked", memory_block + "\n## Questions asked"
    )
    edit_plan(repo, edited, "chore(loom): append memory task")
    result = run_plan_edits(repo)
    assert result.returncode == 0, result.stderr


def test_landed_task_files_change_blocks_even_with_reason(tmp_path: Path) -> None:
    """A landed task's Files line changing blocks no matter what the
    commit message says."""
    repo = init_repo(tmp_path)
    seed_plan(repo, base_plan_text())
    land(repo, "W1")
    edited = base_plan_text(w1_files="x.py, y.py, z.py")
    edit_plan(repo, edited, "fix(loom): W1 needed another file, reason given right here")
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_unlanded_task_change_without_id_in_message_blocks(tmp_path: Path) -> None:
    """An un-landed task's Test line changes, but the commit message never
    names the task id -- blocked."""
    repo = init_repo(tmp_path)
    seed_plan(repo, base_plan_text())
    edited = base_plan_text(w1_test="a rewritten test line")
    edit_plan(repo, edited, "chore: general tidy up")
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_unlanded_task_change_with_id_in_message_passes(tmp_path: Path) -> None:
    """Same edit, but the commit message names the task id and the
    reason -- allowed."""
    repo = init_repo(tmp_path)
    seed_plan(repo, base_plan_text())
    edited = base_plan_text(w1_test="a rewritten test line")
    edit_plan(repo, edited, "fix(loom): W1's test line assumed the wrong fixture")
    result = run_plan_edits(repo)
    assert result.returncode == 0, result.stderr


def test_appended_risks_item_blocks_naming_review(tmp_path: Path) -> None:
    """A newly appended `## Risks` item blocks, naming `review` as the
    goes-to artifact per the plan charter's must_not table."""
    repo = init_repo(tmp_path)
    seed_plan(repo, base_plan_text())
    edited = base_plan_text() + "2. a brand-new risk appended after sign-off.\n"
    edit_plan(repo, edited, "chore(loom): add a risk after sign-off")
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)
    assert "review" in result.stderr


def test_no_charter_key_skips_entirely(tmp_path: Path) -> None:
    """A plan with no `charter:` frontmatter key is never checked, even
    when a Risks item is appended after sign-off."""
    repo = init_repo(tmp_path)
    text = base_plan_text().replace("charter: 1.0\n", "")
    seed_plan(repo, text)
    edited = text + "2. a brand-new risk, no charter stamp.\n"
    edit_plan(repo, edited, "chore(loom): add a risk, no charter stamp")
    result = run_plan_edits(repo)
    assert result.returncode == 0, result.stderr


def test_missing_plan_file_exits_two(tmp_path: Path) -> None:
    """A change-id with no plan.md at all exits 2."""
    repo = init_repo(tmp_path)
    git(repo, "commit", "-q", "--allow-empty", "-m", "seed")
    result = subprocess.run(
        [sys.executable, str(CHECKER), "plan-edits", "no-such-change"],
        capture_output=True, text=True, cwd=str(repo),
    )
    assert result.returncode == 2


def test_no_plan_commit_found_blocks_with_exit_one(tmp_path: Path) -> None:
    """No commit carries the exact plan-commit subject -- blocked at exit
    1, naming the reason."""
    repo = init_repo(tmp_path)
    path = plan_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(base_plan_text(), encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): a differently worded commit")
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "no plan commit found" in result.stderr
