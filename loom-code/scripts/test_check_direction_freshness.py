"""Tests for check_direction_freshness.find_unlanded_direction_changes.

Each test builds a THROWAWAY git repo under tmp_path — never asserts
against this repo's live branch state, which changes over time.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from check_direction_freshness import find_unlanded_direction_changes


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _commit(repo: Path, message: str, *, date: str) -> str:
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date
    env["GIT_COMMITTER_DATE"] = date
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-q", "-m", message],
        check=True,
        capture_output=True,
        env=env,
    )
    return _git(repo, "rev-parse", "HEAD")


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    return repo


_DIRECTION_WITH_NOW_ENTRY = """# Direction

## Now

- widget-revamp — rescope the widget flow

## Next
"""


def _write_direction(repo: Path, body: str = _DIRECTION_WITH_NOW_ENTRY) -> None:
    (repo / "docs" / "loom").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "loom" / "DIRECTION.md").write_text(body, encoding="utf-8")


def test_reports_unlanded_change_to_a_now_entry(tmp_path: Path) -> None:
    """A side branch edits a ## Now entry's backlog file; the change
    never lands on main. The function must report it — this is the
    exact failure mode (kumiko's nine-day stale ## Now) the gate exists
    to catch."""
    repo = _init_repo(tmp_path)
    _write_direction(repo)
    backlog_dir = repo / "docs" / "loom" / "backlog"
    backlog_dir.mkdir(parents=True, exist_ok=True)
    entry = backlog_dir / "widget-revamp.md"
    entry.write_text("status: OPEN\nname: widget-revamp\n", encoding="utf-8")
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    _git(repo, "checkout", "-q", "-b", "rescope")
    entry.write_text("status: OPEN\nname: widget-revamp\nrescoped: true\n", encoding="utf-8")
    _commit(repo, "rescope widget-revamp", date="2026-01-05T00:00:00 +0000")

    findings = find_unlanded_direction_changes(repo, base_branch="main")

    assert len(findings) == 1
    assert findings[0] == (
        "rescope — docs/loom/backlog/widget-revamp.md (tip 2026-01-05)"
    )


def test_squash_landed_change_yields_empty_list(tmp_path: Path) -> None:
    """A side branch's edit is squash-landed onto main with identical
    final content. Ancestry would call this branch unmerged (its tip is
    not an ancestor of main's new tip) — the intersection test must
    clear it because the file no longer differs from main."""
    repo = _init_repo(tmp_path)
    _write_direction(repo)
    backlog_dir = repo / "docs" / "loom" / "backlog"
    backlog_dir.mkdir(parents=True, exist_ok=True)
    entry = backlog_dir / "widget-revamp.md"
    entry.write_text("status: OPEN\nname: widget-revamp\n", encoding="utf-8")
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    _git(repo, "checkout", "-q", "-b", "rescope")
    entry.write_text("status: OPEN\nname: widget-revamp\nrescoped: true\n", encoding="utf-8")
    _commit(repo, "rescope widget-revamp", date="2026-01-05T00:00:00 +0000")

    _git(repo, "checkout", "-q", "main")
    entry.write_text("status: OPEN\nname: widget-revamp\nrescoped: true\n", encoding="utf-8")
    _commit(repo, "squash-land rescope", date="2026-01-06T00:00:00 +0000")

    findings = find_unlanded_direction_changes(repo, base_branch="main")

    assert findings == []


def test_unrelated_file_change_yields_empty_list(tmp_path: Path) -> None:
    """A side branch changes a file outside the governing set — must
    not be reported."""
    repo = _init_repo(tmp_path)
    _write_direction(repo)
    backlog_dir = repo / "docs" / "loom" / "backlog"
    backlog_dir.mkdir(parents=True, exist_ok=True)
    (backlog_dir / "widget-revamp.md").write_text(
        "status: OPEN\nname: widget-revamp\n", encoding="utf-8"
    )
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    _git(repo, "checkout", "-q", "-b", "unrelated")
    (repo / "README.md").write_text("hello again\n", encoding="utf-8")
    _commit(repo, "edit readme", date="2026-01-05T00:00:00 +0000")

    findings = find_unlanded_direction_changes(repo, base_branch="main")

    assert findings == []


def test_missing_direction_file_yields_empty_list(tmp_path: Path) -> None:
    """No `docs/loom/DIRECTION.md` at all — empty list, not a raise."""
    repo = _init_repo(tmp_path)
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    _git(repo, "checkout", "-q", "-b", "side")
    (repo / "README.md").write_text("hello again\n", encoding="utf-8")
    _commit(repo, "edit readme", date="2026-01-05T00:00:00 +0000")

    findings = find_unlanded_direction_changes(repo, base_branch="main")

    assert findings == []
