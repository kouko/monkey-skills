"""Tests for .codex/hooks/git-guard-shim.sh — the Codex PreToolUse shim
that forwards to loom-code/hooks/git-guard.py.

Codex's hook payload shape is an UNVERIFIED upstream surface (external
surface, brief item 3 / plan Task 5): the shim must fail OPEN with a
loud, single-line stderr warning whenever the payload can't be parsed
or isn't Claude-Code-shaped (no `tool_input.command`) — never a hard
block of an unrelated command on a shape mismatch.

Each test subprocess-runs the shim exactly as a Codex hook would invoke
it: hook-event JSON (or garbage) on stdin, exit code as the verdict.
The "Claude-shaped, no markers" case is driven against a REAL throwaway
git repo (tmp_path + `git init` + an empty commit) so git-guard.py's
own marker lookup misses naturally, without touching the real repo's
`.git/loom`.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SHIM = REPO_ROOT / ".codex" / "hooks" / "git-guard-shim.sh"


def _iso_env(extra=None):
    """Isolated env: no user git config / git env vars leaking in."""
    env = os.environ.copy()
    env.pop("GIT_DIR", None)
    env.pop("GIT_WORK_TREE", None)
    env["GIT_CONFIG_GLOBAL"] = ""
    env["GIT_CONFIG_SYSTEM"] = ""
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if extra:
        env.update(extra)
    return env


def run_shim(payload, cwd):
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        ["bash", str(SHIM)],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=_iso_env(),
    )


@pytest.fixture
def repo(tmp_path):
    """A real, throwaway git repo — NOT the real repo's .git/loom."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True,
                   env=_iso_env())
    subprocess.run(
        [
            "git", "-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "--allow-empty", "-m", "init", "-q",
        ],
        cwd=tmp_path,
        check=True,
        env=_iso_env(),
    )
    return tmp_path


def test_shim_is_executable():
    assert os.access(SHIM, os.X_OK)


def test_claude_shaped_push_blocked_without_markers(repo):
    # No review-pass.json / verified.json anywhere under repo/.git/loom —
    # git-guard.py's marker gate must block a bare `git push`.
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "git push"},
        "cwd": str(repo),
    }
    res = run_shim(payload, cwd=repo)
    assert res.returncode == 2, res.stderr
    assert not (repo / ".git" / "loom").exists() or not list(
        (repo / ".git" / "loom").glob("*.json")
    )


def test_claude_shaped_wrapper_push_blocked_without_markers(repo):
    # A push behind a known wrapper (env) must still be recognized once
    # the shim forwards the payload to git-guard.py unchanged — proves
    # the wrapper-aware matcher flows through the shim, not just bare
    # `git push`.
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "env git push"},
        "cwd": str(repo),
    }
    res = run_shim(payload, cwd=repo)
    assert res.returncode == 2, res.stderr


def test_malformed_payload_fails_open_with_warning(repo):
    res = run_shim("this is not json {", cwd=repo)
    assert res.returncode == 0
    assert res.stderr.strip() == "codex payload shape unknown — gate inactive"


def test_valid_json_missing_tool_input_command_fails_open_with_warning(repo):
    # Parseable JSON, but not Claude-shaped (no tool_input.command) —
    # same loud fail-open, not a crash and not a silent pass-through.
    res = run_shim({"some_other_shape": True}, cwd=repo)
    assert res.returncode == 0
    assert res.stderr.strip() == "codex payload shape unknown — gate inactive"
