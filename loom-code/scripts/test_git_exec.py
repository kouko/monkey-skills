"""Executable contract for `git_exec.run_git` -- the single git-invocation
body Tasks 4-9 delegate to (six pre-existing copies collapse into this
one). Encoding rationale (argv-as-UTF-8-bytes, `encoding="utf-8",
errors="surrogateescape"` under `text=True`) is transcribed from
`batch_review_cli._run_subprocess`'s docstring, not restated here.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

import git_exec


def _init_git_repo(repo_root: Path) -> None:
    repo_root.mkdir(parents=True)
    subprocess.run(["git", "-C", str(repo_root), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(repo_root), "config", "user.email", "t@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo_root), "config", "user.name", "T"], check=True,
    )


def _git_commit_file(repo_root: Path, rel_path: str, content: bytes) -> str:
    path = repo_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    subprocess.run(["git", "-C", str(repo_root), "add", rel_path], check=True)
    subprocess.run(
        ["git", "-C", str(repo_root), "commit", "-q", "-m", f"add {rel_path}"],
        check=True,
    )
    return subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def test_run_git_hands_utf8_bytes_argv_and_utf8_decoding(monkeypatch, tmp_path) -> None:
    captured: dict[str, object] = {}

    def _capture(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(git_exec.subprocess, "run", _capture)
    git_exec.run_git(tmp_path, "show", "HEAD:src/日本.py")

    argv = captured["argv"]
    assert all(isinstance(item, bytes) for item in argv), argv
    assert argv[-1] == "HEAD:src/日本.py".encode("utf-8")
    kwargs = captured["kwargs"]
    assert kwargs["encoding"] == "utf-8"
    assert kwargs["errors"] == "surrogateescape"


def test_run_git_check_false_returns_none_on_non_repo(tmp_path) -> None:
    non_repo = tmp_path / "not_a_repo"
    non_repo.mkdir()
    assert git_exec.run_git(non_repo, "status") is None


def test_run_git_check_false_returns_none_on_bad_ref(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _init_git_repo(repo_root)
    _git_commit_file(repo_root, "a.txt", b"a")
    assert git_exec.run_git(repo_root, "show", "not-a-ref") is None


def test_run_git_check_false_returns_none_on_oserror(monkeypatch, tmp_path) -> None:
    def _raise(*args, **kwargs):
        raise OSError("git binary missing")

    monkeypatch.setattr(git_exec.subprocess, "run", _raise)
    assert git_exec.run_git(tmp_path, "status") is None


def test_run_git_check_false_returns_none_on_timeout(monkeypatch, tmp_path) -> None:
    def _raise(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="git", timeout=1)

    monkeypatch.setattr(git_exec.subprocess, "run", _raise)
    assert git_exec.run_git(tmp_path, "status", timeout=1) is None


def test_run_git_check_true_raises_calledprocesserror_on_bad_ref(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _init_git_repo(repo_root)
    _git_commit_file(repo_root, "a.txt", b"a")
    with pytest.raises(subprocess.CalledProcessError):
        git_exec.run_git(repo_root, "show", "not-a-ref", check=True)


def test_run_git_check_true_propagates_oserror(monkeypatch, tmp_path) -> None:
    def _raise(*args, **kwargs):
        raise OSError("git binary missing")

    monkeypatch.setattr(git_exec.subprocess, "run", _raise)
    with pytest.raises(OSError):
        git_exec.run_git(tmp_path, "status", check=True)


def test_run_git_text_false_returns_bytes(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _init_git_repo(repo_root)
    sha = _git_commit_file(repo_root, "a.txt", b"hello")
    result = git_exec.run_git(repo_root, "show", f"{sha}:a.txt", text=False)
    assert result == b"hello"


def test_run_git_strip_false_keeps_trailing_whitespace(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _init_git_repo(repo_root)
    _git_commit_file(repo_root, "a.txt", b"a")
    result = git_exec.run_git(repo_root, "log", "-1", "--format=%H%n", strip=False)
    assert result.endswith("\n")


def test_run_git_under_c_locale_decodes_non_ascii_path(tmp_path) -> None:
    """Same technique as
    `test_batch_review_cli.py::test_packet_seals_non_ascii_path_under_c_locale`:
    a real OS subprocess (its own interpreter startup locale) is required
    to reproduce the decode -- an in-process call runs under pytest's
    already-fixed locale. The non-ASCII path is written into the runner
    script's UTF-8 source, not passed as an OS argv item to the outer
    `sys.executable` invocation, so only the inner `run_git` call (via
    `git_exec`) exercises the argv-encode / stdout-decode path under
    C-locale pressure.
    """
    repo_root = tmp_path / "repo"
    _init_git_repo(repo_root)
    _git_commit_file(repo_root, "src/日本.py", b"member")

    scripts_dir = Path(__file__).resolve().parent
    runner = tmp_path / "runner.py"
    runner.write_text(
        "import sys\n"
        f"sys.path.insert(0, {str(scripts_dir)!r})\n"
        "import git_exec\n"
        f"result = git_exec.run_git({str(repo_root)!r}, 'show', 'HEAD:src/日本.py')\n"
        "print(result)\n",
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    env["PYTHONUTF8"] = "0"
    env["PYTHONCOERCECLOCALE"] = "0"
    result = subprocess.run(
        [sys.executable, str(runner)],
        capture_output=True, text=True, env=env,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "member"
