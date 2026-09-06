"""W1-01: `yaml` must be a lazy import inside `load_manifest`, not a
module-level import, so the non-push hook fast path (run on every Bash
call) never pays its ~8.7ms import cost.

Run directly: `python3 -m pytest <this file> -v`.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"


def _init_git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "a@b.c"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "a"], cwd=repo, check=True)
    (repo / "f.txt").write_text("x\n")
    subprocess.run(["git", "add", "f.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
    return repo


def test_hook_nonpush_no_yaml_import():
    """A1 positive: `-X importtime` on `push --hook` with a non-push
    command payload must show no `yaml` line in the import trace."""
    with tempfile.TemporaryDirectory() as td:
        repo = _init_git_repo(Path(td))
        payload = {"tool_name": "Bash", "tool_input": {"command": "echo hi"}, "cwd": str(repo)}
        result = subprocess.run(
            [sys.executable, "-X", "importtime", str(CHECKER), "push", "--hook"],
            input=json.dumps(payload),
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        yaml_import_lines = [
            ln for ln in result.stderr.splitlines()
            if ln.strip().split(" ")[-1] == "yaml"
        ]
        assert not yaml_import_lines, (
            "expected no `yaml` import on the non-push hook fast path, found:\n"
            + "\n".join(yaml_import_lines)
        )


def test_push_command_still_reaches_load_manifest():
    """Negative: a push-shaped command in a repo with no review.json must
    still reach a real BLOCK/PASS decision via `load_manifest`, not crash
    with ImportError/NameError from a mis-scoped `yaml` reference."""
    with tempfile.TemporaryDirectory() as td:
        repo = _init_git_repo(Path(td))
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "git push origin HEAD"},
            "cwd": str(repo),
        }
        result = subprocess.run(
            [sys.executable, str(CHECKER), "push", "--hook"],
            input=json.dumps(payload),
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert "ImportError" not in result.stderr
        assert "NameError" not in result.stderr
        assert result.returncode in (0, 1, 2), result.stderr
        assert "loom_checker internal error" not in result.stderr, result.stderr
