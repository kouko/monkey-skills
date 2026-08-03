"""Tests for review_scope — the freshness verdict Task 2 builds.

Each test builds a THROWAWAY pair of git repos under tmp_path: an
`upstream` repo (plays the role of the remote) and a `repo` clone of it
(plays the role of the branch under review). No dependency on the outer
repo. Commits are made directly in `upstream`'s own working tree — never
via `git push` into it — so `upstream` can stay a normal (non-bare) repo.

External-surface grounding (source a — live verification): the git
invocations `check_freshness` depends on — `fetch <remote> <branch>`,
`rev-parse <ref>`, and `merge-base HEAD <ref>` — are exercised LIVE by
this suite against the throwaway repos above, both the stale-base and
the fresh-base paths, so a flag regression in the installed git surfaces
here, not via belief.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import review_scope


def _git(repo: Path, *args: str) -> str:
    """Run a git command in `repo`, return stdout (stripped)."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _init_upstream(tmp_path: Path) -> Path:
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _git(upstream, "init", "-q")
    _git(upstream, "config", "user.email", "test@example.com")
    _git(upstream, "config", "user.name", "Test User")
    _git(upstream, "commit", "--allow-empty", "-m", "init")
    return upstream


def _clone(tmp_path: Path, upstream: Path) -> Path:
    repo = tmp_path / "repo"
    subprocess.run(
        ["git", "clone", "-q", str(upstream), str(repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    return repo


def test_stale_base_is_not_fresh(tmp_path):
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    base_sha = _head(repo)

    # Branch off the base BEFORE a new commit lands on upstream's default
    # branch — the base then predates a commit already on the default
    # branch, which is the stale scenario.
    _git(repo, "checkout", "-q", "-b", "feature")
    _git(upstream, "commit", "--allow-empty", "-m", "already on default branch")

    result = review_scope.check_freshness(repo)

    assert result.fresh is False
    assert result.base_sha == base_sha


def test_fresh_base_reports_fresh(tmp_path):
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    base_sha = _head(repo)

    # Branch off the base with nothing new pushed to upstream afterward —
    # the branch's base IS the current remote tip.
    _git(repo, "checkout", "-q", "-b", "feature")

    result = review_scope.check_freshness(repo)

    assert result.fresh is True
    assert result.base_sha == base_sha
    assert result.remote_sha == base_sha


def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD")


def test_split_fetch_target_splits_on_first_slash_only():
    # ref.partition("/") must split on the FIRST separator only, so a
    # branch name that itself contains a slash (e.g. "release/2.0")
    # survives intact as the branch component rather than being cut at
    # the last slash — a later "fix" to rsplit/split("/") would break
    # this real-world branch-name shape while every slash-free test
    # still passed.
    assert review_scope.split_fetch_target("origin/release/2.0") == (
        "origin",
        "release/2.0",
    )


def test_split_fetch_target_returns_none_for_bare_local_ref():
    # A bare local ref ("main" / "master", no remote component) is the
    # LOCAL-ONLY hazard named in §Pinned local-ref rule: it cannot be
    # fetched, so split_fetch_target must signal that with None rather
    # than a fabricated split.
    assert review_scope.split_fetch_target("main") is None
