"""Tests for living_spec_gitref.resolve_binding_refs.

Each test builds a THROWAWAY git repo under tmp_path with deterministic
committer dates so body_ts vs binding_ts ordering is unambiguous. No
dependency on the outer repo.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

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
