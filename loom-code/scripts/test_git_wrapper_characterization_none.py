"""Characterization tests for the three `_git` wrappers' failure paths.

Task 1 of the git-exec-extraction batch: pin `loom_gate_markers._git`,
`review_context._git`, and `review_scope._git` against HEAD before
Tasks 4-6 replace their bodies with a delegation to a shared
`git_exec.run_git`. No existing test in this repo's `scripts/`
directory drives any of these three functions down a non-repo path, a
failing-ref path, a missing-binary path, or `review_scope._git`'s
timeout path -- this file is the first to execute those branches, so
each test below documents the exact return value the current
implementation produces on that branch.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import git_exec
import loom_gate_markers
import review_context
import review_scope


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return repo


# --- loom_gate_markers._git ---


def test_loom_gate_markers_git_nonrepo_returns_none(tmp_path):
    nonrepo = tmp_path / "nonrepo"
    nonrepo.mkdir()
    assert loom_gate_markers._git(nonrepo, "rev-parse", "HEAD") is None


def test_loom_gate_markers_git_failing_ref_returns_none(tmp_path):
    repo = _init_repo(tmp_path)
    assert (
        loom_gate_markers._git(repo, "rev-parse", "--verify", "no-such-ref") is None
    )


def test_loom_gate_markers_git_missing_binary_returns_none(tmp_path, monkeypatch):
    def fake_run(*args, **kwargs):
        raise OSError("git binary not found")

    monkeypatch.setattr(loom_gate_markers.subprocess, "run", fake_run)
    assert loom_gate_markers._git(tmp_path, "rev-parse", "HEAD") is None


def test_loom_gate_markers_git_success_empty_output_returns_empty_string(tmp_path):
    repo = _init_repo(tmp_path)
    # `rev-parse --show-cdup` at the repo root succeeds with an empty line.
    assert loom_gate_markers._git(repo, "rev-parse", "--show-cdup") == ""


# --- review_context._git ---


def test_review_context_git_nonrepo_returns_none(tmp_path):
    nonrepo = tmp_path / "nonrepo"
    nonrepo.mkdir()
    assert review_context._git(nonrepo, "rev-parse", "HEAD") is None


def test_review_context_git_failing_ref_returns_none(tmp_path):
    repo = _init_repo(tmp_path)
    assert review_context._git(repo, "rev-parse", "--verify", "no-such-ref") is None


def test_review_context_git_missing_binary_returns_none(tmp_path, monkeypatch):
    def fake_run(*args, **kwargs):
        raise OSError("git binary not found")

    monkeypatch.setattr(git_exec.subprocess, "run", fake_run)
    assert review_context._git(tmp_path, "rev-parse", "HEAD") is None


def test_review_context_git_success_empty_output_returns_empty_string(tmp_path):
    repo = _init_repo(tmp_path)
    assert review_context._git(repo, "rev-parse", "--show-cdup") == ""


# --- review_scope._git ---


def test_review_scope_git_nonrepo_returns_none(tmp_path):
    nonrepo = tmp_path / "nonrepo"
    nonrepo.mkdir()
    assert review_scope._git(nonrepo, "rev-parse", "HEAD") is None


def test_review_scope_git_failing_ref_returns_none(tmp_path):
    repo = _init_repo(tmp_path)
    assert review_scope._git(repo, "rev-parse", "--verify", "no-such-ref") is None


def test_review_scope_git_missing_binary_returns_none(tmp_path, monkeypatch):
    def fake_run(*args, **kwargs):
        raise OSError("git binary not found")

    monkeypatch.setattr(git_exec.subprocess, "run", fake_run)
    assert review_scope._git(tmp_path, "rev-parse", "HEAD") is None


def test_review_scope_git_success_empty_output_returns_empty_string(tmp_path):
    repo = _init_repo(tmp_path)
    assert review_scope._git(repo, "rev-parse", "--show-cdup") == ""


def test_review_scope_git_timeout_returns_none(tmp_path, monkeypatch):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args, timeout=kwargs.get("timeout") or 0)

    monkeypatch.setattr(git_exec.subprocess, "run", fake_run)
    assert review_scope._git(tmp_path, "rev-parse", "HEAD", timeout=0.01) is None
