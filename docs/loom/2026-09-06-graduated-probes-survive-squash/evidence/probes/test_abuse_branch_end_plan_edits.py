"""Branch-end adversarial boundaries for the shipped plan-edits carve-out."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[5]
CHECKER = ROOT / "loom-code/scripts/loom_checker.py"
CHANGE = "2099-05-05-branch-end-plan-edits"


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check:
        assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "core.autocrlf", "false")
    git(repo, "config", "user.name", "Branch End Adversary")
    git(repo, "config", "user.email", "adversary@example.invalid")
    return repo


def intent(repo: Path, status: str, extra: str = "") -> Path:
    path = repo / "docs/loom/intent" / f"{CHANGE}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Intent\noriginator: adversary\nkind: engineering\nneeds-design: no — fixture\n"
        f"{status}\n{extra}\n\n## Problem\nprobe\n",
        encoding="utf-8",
    )
    return path


def plan(repo: Path) -> Path:
    path = repo / "docs/loom" / CHANGE / "plan.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Plan\nintent: {CHANGE}@0000000\ncharter: 1.0\n\n"
        "## Current State Evidence\n- Forward: x.py:1\n\n## Task DAG\n\n"
        "**W1 Task**  after: --\n- Files: x.py\n- Test: pass\n"
        "- Risk: agent-decided -- low\n\n## Questions asked\n"
        "① — what — answered\n\n## Risks\n1. agent-decided — low\n",
        encoding="utf-8",
    )
    return path


def commit_all(repo: Path, message: str) -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)


def run(repo: Path, change: str = CHANGE) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "plan-edits", change],
        cwd=repo, capture_output=True, text=True,
    )


def assert_block(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 1
    assert "BLOCK plan.edits-after-commit: no plan commit found" in result.stderr


def test_planedits_unreachableclosure_blocks(tmp_path: Path) -> None:
    """A closed commit reachable only from an unmerged side branch must not grant amnesty."""
    repo = init_repo(tmp_path)
    intent(repo, "status: confirmed 2099-05-05")
    plan(repo)
    commit_all(repo, "seed confirmed intent")
    git(repo, "switch", "-q", "-c", "closed-side")
    intent(repo, "status: closed 2099-05-05 — PR #9")
    commit_all(repo, "close only on side branch")
    git(repo, "switch", "-q", "main")
    assert_block(run(repo))


def test_planedits_duplicatestatus_blocks(tmp_path: Path) -> None:
    """Two status lines must be malformed rather than letting one closed line grant amnesty."""
    repo = init_repo(tmp_path)
    intent(repo, "status: confirmed 2099-05-05", "status: closed 2099-05-05 — PR #9")
    plan(repo)
    commit_all(repo, "commit duplicate status lines")
    assert_block(run(repo))


def test_planedits_fullwidthdecoration_blocks(tmp_path: Path) -> None:
    """Full-width spaces around the em dash must not impersonate the exact closed grammar."""
    repo = init_repo(tmp_path)
    intent(repo, "status: closed 2099-05-05　—　PR #9")
    plan(repo)
    commit_all(repo, "commit confusable closed status")
    assert_block(run(repo))


def test_planedits_fencedstatus_blocks(tmp_path: Path) -> None:
    """A closed status inside a fenced body example must not grant amnesty."""
    repo = init_repo(tmp_path)
    intent(repo, "status: confirmed 2099-05-05", "\n## Example\n```yaml\nstatus: closed 2099-05-05 — PR #9\n```")
    plan(repo)
    commit_all(repo, "commit fenced example")
    assert_block(run(repo))


def test_planedits_symlinkintent_blocks(tmp_path: Path) -> None:
    """A symlinked intent must fail closed even when its target contains a committed closure."""
    repo = init_repo(tmp_path)
    target = repo / "outside.md"
    target.write_text("# Intent\nstatus: closed 2099-05-05 — PR #9\n", encoding="utf-8")
    path = repo / "docs/loom/intent" / f"{CHANGE}.md"
    path.parent.mkdir(parents=True)
    path.symlink_to(target)
    plan(repo)
    commit_all(repo, "commit symlinked intent")
    assert_block(run(repo))


def test_planedits_traversalchange_refused(tmp_path: Path) -> None:
    """A traversal-bearing change id must be refused without reading an intent outside its store."""
    repo = init_repo(tmp_path)
    intent(repo, "status: confirmed 2099-05-05")
    plan(repo)
    commit_all(repo, "seed ordinary change")
    result = run(repo, "../../outside")
    assert result.returncode != 0
    assert "NOT APPLICABLE" not in result.stdout + result.stderr


def test_planedits_closedlateredit_blocks(tmp_path: Path) -> None:
    """A committed plan baseline plus closure and a later plan edit must still block."""
    repo = init_repo(tmp_path)
    intent(repo, "status: confirmed 2099-05-05")
    plan(repo)
    commit_all(repo, f"docs(loom): plan {CHANGE}")
    intent(repo, "status: closed 2099-05-05 — PR #9")
    commit_all(repo, "close intent")
    p = plan(repo)
    p.write_text(p.read_text(encoding="utf-8").replace("- Files: x.py", "- Files: x.py, y.py"), encoding="utf-8")
    commit_all(repo, "edit plan after closure")
    result = run(repo)
    assert result.returncode == 1
    assert "BLOCK plan.edits-after-commit" in result.stderr


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
