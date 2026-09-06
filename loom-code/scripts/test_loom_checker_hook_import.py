"""W1-01: `yaml` must be a lazy import inside `load_manifest`, not a
module-level import, so the non-push hook fast path (run on every Bash
call) never pays its ~8.7ms import cost.

Branch-end-05 (2026-09-07): the same fast path must also never pay for
`traceback` -- W1-01 removed the module-level `yaml` import but added a
module-level `import traceback` used only inside `load_manifest`'s
`except ImportError:` branch (a missing `yaml`), which the non-push fast
path never reaches. `traceback` is moved into that branch, same as
`yaml` was.

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
        traceback_import_lines = [
            ln for ln in result.stderr.splitlines()
            if ln.strip().split(" ")[-1] == "traceback"
        ]
        assert not traceback_import_lines, (
            "expected no `traceback` import on the non-push hook fast path, found:\n"
            + "\n".join(traceback_import_lines)
        )


def test_yaml_unimportable_exits_1_with_traceback_not_caught_as_internal_error():
    """The lazy `import yaml` inside `load_manifest` must not be swallowed
    by `main`'s catch-all `except Exception` (which prints `loom_checker
    internal error: ...` and exits 2) -- before the import moved off
    module scope, a missing `yaml` crashed uncaught at Python's default
    exit code 1 with a full traceback on stderr. `load_manifest` must
    re-raise a missing `yaml` as a `SystemExit(1)` (a `BaseException`,
    so `except Exception` does not catch it) with the traceback still
    printed to stderr, restoring that exact failure shape."""
    with tempfile.TemporaryDirectory() as td:
        badlib = Path(td) / "badlib"
        badlib.mkdir()
        (badlib / "yaml.py").write_text(
            "raise ModuleNotFoundError(\"No module named 'yaml'\")\n"
        )
        result = subprocess.run(
            [sys.executable, str(CHECKER), "contract", "--require", "1.0"],
            cwd=str(REPO_ROOT),
            env={"PYTHONPATH": str(badlib), "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1, result.stderr
        assert "Traceback" in result.stderr
        assert "ModuleNotFoundError" in result.stderr
        assert "loom_checker internal error" not in result.stderr


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
