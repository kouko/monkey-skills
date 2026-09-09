"""Codex publication hook lifecycle regression tests.

The retained hook command must remain useful after its versioned plugin root
has disappeared: a small set of read-only commands stays available, while
everything else fails closed until Codex is restarted.
"""
from __future__ import annotations

import json
import os
import subprocess
import shutil
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CODEX_HOOKS = ROOT / "loom-code/hooks/hooks-codex.json"


def _command() -> str:
    hooks = json.loads(CODEX_HOOKS.read_text(encoding="utf-8"))["hooks"]
    return hooks["PreToolUse"][0]["hooks"][0]["command"]


def _payload(command: str) -> str:
    return json.dumps(
        {
            "cwd": str(ROOT),
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }
    )


def _run(command: str, plugin_root: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, PLUGIN_ROOT=str(plugin_root))
    return subprocess.run(
        _command(),
        shell=True,
        input=_payload(command),
        text=True,
        capture_output=True,
        env=env,
    )


@pytest.mark.parametrize(
    "command",
    [
        "git status --short --branch",
        "git log --max-count=3 --oneline",
        "git diff --check",
        "git show --stat HEAD",
        "git branch --list 'codex/*'",
        "ls loom-code",
        "cat loom-code/hooks/hooks.json",
        "rg -n PLUGIN_ROOT loom-code",
        "find loom-code -maxdepth 2 -type f -print",
    ],
)
def test_codex_hook_missing_root_allows_closed_read_only_set(
    tmp_path: Path, command: str
) -> None:
    missing = tmp_path / "removed-version"
    result = _run(command, missing)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "command",
    [
        "git push origin HEAD",
        "gh pr create --fill",
        "pytest -q",
        "python3 -c 'print(1)'",
        "git fetch origin",
        "git status && git push origin HEAD",
        "find . -exec git push origin HEAD ;",
        "find . -delete",
        "find . -fls /tmp/loom-stale-hook-output",
        "rg --pre 'git push origin HEAD' needle .",
        "rg --pre=bash needle .",
        "rg --pre-glob=* --pre=sh needle .",
        "git log --output=/tmp/log",
        "git branch --list --delete main",
        "./git status",
        "/tmp/cat file",
    ],
)
def test_codex_hook_missing_root_denies_publication_unknown_and_unsafe_reads(
    tmp_path: Path, command: str
) -> None:
    missing = tmp_path / "removed-version"
    result = _run(command, missing)
    assert result.returncode == 2
    assert str(missing / "scripts/loom_checker.py") in result.stderr
    assert "restart Codex" in result.stderr


def test_codex_hook_missing_root_denies_malformed_or_empty_input(tmp_path: Path) -> None:
    missing = tmp_path / "removed-version"
    env = dict(os.environ, PLUGIN_ROOT=str(missing))
    for payload in ("", "not-json", "[]"):
        result = subprocess.run(
            _command(), shell=True, input=payload, text=True,
            capture_output=True, env=env,
        )
        assert result.returncode == 2


@pytest.mark.parametrize(
    "command",
    [
        "git push origin HEAD",
        "gh pr create --fill",
        "gh pr merge 123 --squash",
        "zsh -c 'git push origin HEAD'",
        "eval 'gh pr create --fill'",
        'echo "$(git push origin HEAD)"',
        'echo "$(gh pr create --fill)"',
        'echo "`git push origin HEAD`"',
        'echo "`gh pr create --fill`"',
        "rg -n 'needle|gh pr create",
    ],
)
def test_codex_hook_missing_root_denies_every_checker_publication_corpus_case(
    tmp_path: Path, command: str
) -> None:
    result = _run(command, tmp_path / "removed-version")
    assert result.returncode == 2


def test_codex_hook_present_root_delegates_every_bash_payload(tmp_path: Path) -> None:
    root = tmp_path / "installed"
    script = root / "scripts/loom_checker.py"
    script.parent.mkdir(parents=True)
    script.write_text(
        "import sys\n"
        "data = sys.stdin.read()\n"
        "print('delegated:' + data)\n"
        "raise SystemExit(17)\n",
        encoding="utf-8",
    )
    result = _run("git status", root)
    assert result.returncode == 17
    assert "delegated:" in result.stdout


def test_codex_hook_missing_root_denies_path_poisoning_and_sibling_checker(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "cache" / "2.0.7"
    sibling = tmp_path / "cache" / "2.0.8" / "scripts"
    sibling.mkdir(parents=True)
    marker = tmp_path / "executed"
    (sibling / "loom_checker.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('sibling')\n",
        encoding="utf-8",
    )
    poisoned = tmp_path / "bin"
    poisoned.mkdir()
    fake_git = poisoned / "git"
    fake_git.write_text(f"#!/bin/sh\ntouch {marker}\n", encoding="utf-8")
    fake_git.chmod(0o755)
    env = dict(
        os.environ,
        PLUGIN_ROOT=str(missing),
        PATH=f"{poisoned}:{os.environ.get('PATH', '')}",
    )
    result = subprocess.run(
        _command(), shell=True, input=_payload("git status"), text=True,
        capture_output=True, env=env,
    )
    assert result.returncode == 2
    assert not marker.exists()
    assert shutil.which("git", path=env["PATH"]) == str(fake_git)
