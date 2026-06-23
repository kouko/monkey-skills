"""Tests for living_spec_gitref.resolve_binding_refs.

Each test builds a THROWAWAY git repo under tmp_path with deterministic
committer dates so body_ts vs binding_ts ordering is unambiguous. No
dependency on the outer repo.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from living_spec_gitref import resolve_binding_refs


def _git(repo: Path, *args: str, env: dict | None = None) -> str:
    """Run a git command in `repo`, return stdout (stripped)."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    return repo


def _commit(repo: Path, message: str, *, date: str) -> str:
    """Stage all + commit with a pinned author/committer date; return SHA."""
    import os

    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date
    env["GIT_COMMITTER_DATE"] = date
    _git(repo, "add", "-A", env=env)
    _git(repo, "commit", "-q", "-m", message, env=env)
    return _git(repo, "rev-parse", "HEAD")


def test_resolve_refs_body_touched_after_binding(tmp_path: Path) -> None:
    """Body line modified in a LATER commit => body_ts > binding_ts.

    Encodes the comparator's need (Task 1): the body and the @req
    binding line are resolved to independent commits, so a body change
    after the binding is detectable as drift.
    """
    repo = _init_repo(tmp_path)
    src = repo / "test_thing.py"
    # binding_line = 2 (@req), body line we will later edit = 3.
    src.write_text(
        "def test_thing():\n"
        "    # @req: REQ-1\n"
        "    assert compute() == 1\n",
        encoding="utf-8",
    )
    c1 = _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    # Later commit modifies ONLY the body assertion line (line 3).
    src.write_text(
        "def test_thing():\n"
        "    # @req: REQ-1\n"
        "    assert compute() == 2\n",
        encoding="utf-8",
    )
    c2 = _commit(repo, "tweak body", date="2026-02-01T00:00:00 +0000")

    binding = {
        "test": "test_thing",
        "req": "REQ-1",
        "body_start": 1,
        "body_end": 3,
        "binding_line": 2,
        "file": "test_thing.py",
    }
    enriched = resolve_binding_refs(binding, repo)

    # Original keys preserved.
    assert enriched["test"] == "test_thing"
    assert enriched["req"] == "REQ-1"
    # Body last touched by c2, binding line by c1.
    assert enriched["body_ref"] == c2
    assert enriched["binding_ref"] == c1
    assert enriched["body_ref"] != enriched["binding_ref"]
    assert enriched["body_ts"] > enriched["binding_ts"]


def test_resolve_refs_binding_touched_after_body(tmp_path: Path) -> None:
    """Only the @req binding line modified later => binding_ts >= body_ts.

    The body range here EXCLUDES the @req line so the two ranges are
    genuinely independent — proving the two-separate-calls design: a
    later edit to the binding line alone must not advance body_ts.
    """
    repo = _init_repo(tmp_path)
    src = repo / "test_thing.py"
    # binding_line = 4 (@req), body = lines 1-3 (excludes the @req line).
    src.write_text(
        "def test_thing():\n"
        "    x = setup()\n"
        "    assert compute(x) == 1\n"
        "    # @req: REQ-1\n",
        encoding="utf-8",
    )
    c1 = _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    # Later commit modifies ONLY the @req binding line (line 4).
    src.write_text(
        "def test_thing():\n"
        "    x = setup()\n"
        "    assert compute(x) == 1\n"
        "    # @req: REQ-2\n",
        encoding="utf-8",
    )
    c2 = _commit(repo, "retag req", date="2026-02-01T00:00:00 +0000")

    binding = {
        "test": "test_thing",
        "req": "REQ-2",
        "body_start": 1,
        "body_end": 3,
        "binding_line": 4,
        "file": "test_thing.py",
    }
    enriched = resolve_binding_refs(binding, repo)

    assert enriched["binding_ref"] == c2
    assert enriched["body_ref"] == c1
    assert enriched["body_ref"] != enriched["binding_ref"]
    assert enriched["binding_ts"] >= enriched["body_ts"]


def test_unresolvable_range_returns_none(tmp_path: Path) -> None:
    """A binding with NO committed history is unresolvable, not an error.

    WHY: the everyday local pre-commit workflow has a net-new @req-tagged
    test in the WORKING TREE that has never been committed — its path is
    not in HEAD, so ``git log -L`` exits 128 ("There is no path ... in
    the commit"). That is NOT a git failure: there is simply no committed
    baseline to drift from. The resolver must signal "unresolvable"
    (return None) for THAT case rather than letting CalledProcessError
    propagate and crash the advisory WARN lane. A None binding cannot be
    a drift, so the downstream lane skips it.
    """
    repo = _init_repo(tmp_path)
    committed = repo / "test_committed.py"
    committed.write_text(
        "def test_committed():\n"
        "    # @req: REQ-1\n"
        "    assert compute() == 1\n",
        encoding="utf-8",
    )
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    # A NEW tagged test file staged-or-not but NEVER committed: its range
    # has no committed history => git log -L exits 128.
    uncommitted = repo / "test_new.py"
    uncommitted.write_text(
        "def test_new():\n"
        "    # @req: REQ-2\n"
        "    assert compute() == 2\n",
        encoding="utf-8",
    )
    binding = {
        "test": "test_new",
        "req": "REQ-2",
        "body_start": 1,
        "body_end": 3,
        "binding_line": 2,
        "file": "test_new.py",
    }

    # Unresolvable (no committed baseline) => None, NOT a raise.
    assert resolve_binding_refs(binding, repo) is None


def test_unresolvable_range_via_body_beyond_committed_length(
    tmp_path: Path,
) -> None:
    """A body range beyond HEAD's committed file length is unresolvable.

    WHY: an uncommitted edit can push a test's body range past the
    number of lines the file had at HEAD; ``git log -L`` then exits 128
    ("file ... has only N lines"). Same class as a never-committed path —
    no committed baseline for that range — so it must signal None, not
    crash the WARN lane.
    """
    repo = _init_repo(tmp_path)
    src = repo / "test_thing.py"
    # Committed file is only 3 lines long.
    src.write_text(
        "def test_thing():\n"
        "    # @req: REQ-1\n"
        "    assert compute() == 1\n",
        encoding="utf-8",
    )
    _commit(repo, "initial", date="2026-01-01T00:00:00 +0000")

    # Binding points the body range past the committed file length.
    binding = {
        "test": "test_thing",
        "req": "REQ-1",
        "body_start": 5,
        "body_end": 8,
        "binding_line": 2,
        "file": "test_thing.py",
    }
    assert resolve_binding_refs(binding, repo) is None


def test_genuine_git_error_still_raises(tmp_path: Path) -> None:
    """A GENUINE git failure must still propagate — never be masked.

    WHY: the unresolvable-history skip is surgical, NOT a blanket
    try/except. Pointing the resolver at a directory that is not a git
    repository is a real error (no ``.git``); it must raise
    CalledProcessError so a broken setup fails loud instead of being
    silently swallowed as "unresolvable".
    """
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()
    binding = {
        "test": "test_x",
        "req": "REQ-1",
        "body_start": 1,
        "body_end": 3,
        "binding_line": 2,
        "file": "test_x.py",
    }
    with pytest.raises(subprocess.CalledProcessError):
        resolve_binding_refs(binding, not_a_repo)
