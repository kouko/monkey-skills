from __future__ import annotations

import os
import subprocess
from io import StringIO
from pathlib import Path

import loom_checker


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def repository(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    (repo / "file.txt").write_text("content\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "initial")
    git(repo, "branch", "-M", "feature")
    git(repo, "remote", "add", "origin", "git@github.com:example/project.git")
    return repo


class ExternalCalls:
    def __init__(self, head: str, existing_pr: str | None = None) -> None:
        self.head = head
        self.remote_head: str | None = None
        self.existing_pr = existing_pr
        self.move_remote_on_pr_list = False
        self.calls: list[list[str]] = []

    def __call__(self, argv, **kwargs):
        argv = [str(value) for value in argv]
        self.calls.append(argv)
        if "repo" in argv and "view" in argv:
            return subprocess.CompletedProcess(argv, 0, "main\n", "")
        if "ls-remote" in argv:
            output = f"{self.remote_head}\trefs/heads/feature\n" if self.remote_head else ""
            return subprocess.CompletedProcess(argv, 0, output, "")
        if "push" in argv:
            self.remote_head = self.head
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "pr" in argv and "list" in argv:
            if self.move_remote_on_pr_list:
                self.remote_head = "e" * 40
            output = f'{self.existing_pr}\n' if self.existing_pr else ""
            return subprocess.CompletedProcess(argv, 0, output, "")
        if "pr" in argv and "create" in argv:
            self.existing_pr = "https://github.com/example/project/pull/1"
            return subprocess.CompletedProcess(argv, 0, f"{self.existing_pr}\n", "")
        raise AssertionError(argv)


def invoke(tmp_path: Path, monkeypatch, calls: ExternalCalls, *extra: str):
    repo = repository(tmp_path)
    body = tmp_path / "body.md"
    body.write_text("## Summary\n", encoding="utf-8")
    calls.head = git(repo, "rev-parse", "HEAD")
    monkeypatch.chdir(repo)
    monkeypatch.setattr(loom_checker, "run_publish_external", calls)
    monkeypatch.setattr(loom_checker, "_cmd_push", lambda *args, **kwargs: 0)
    monkeypatch.setattr(
        loom_checker.shutil,
        "which",
        lambda name: "/usr/bin/git" if name == "git" else "/usr/local/bin/gh",
    )
    out, err = StringIO(), StringIO()
    argv = [
        "--confirm-authorized", "--title", "feat(loom): publish safely",
        "--body-file", str(body), *extra,
    ]
    rc = loom_checker.cmd_publish(argv, out, err)
    return repo, rc, out.getvalue(), err.getvalue()


def test_publish_pushes_exact_head_and_creates_one_pr(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("")
    repo, rc, out, err = invoke(tmp_path, monkeypatch, calls)
    head = git(repo, "rev-parse", "HEAD")
    assert rc == 0, err
    push = next(call for call in calls.calls if "push" in call)
    assert push[-2:] == ["origin", f"{head}:refs/heads/feature"]
    assert "--force" not in push and "--force-with-lease" not in push
    create = next(call for call in calls.calls if call[-2:] != [] and "create" in call)
    assert create[create.index("--base") + 1] == "main"
    assert create[create.index("--head") + 1] == "feature"
    assert "https://github.com/example/project/pull/1" in out


def test_publish_reuses_existing_pr_without_push_or_create(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("", "https://github.com/example/project/pull/7")
    repo = repository(tmp_path)
    calls.head = git(repo, "rev-parse", "HEAD")
    calls.remote_head = calls.head
    body = tmp_path / "body.md"
    body.write_text("body\n", encoding="utf-8")
    monkeypatch.chdir(repo)
    monkeypatch.setattr(loom_checker, "run_publish_external", calls)
    monkeypatch.setattr(loom_checker, "_cmd_push", lambda *args, **kwargs: 0)
    monkeypatch.setattr(loom_checker.shutil, "which", lambda name: f"/trusted/{name}")
    out, err = StringIO(), StringIO()
    rc = loom_checker.cmd_publish([
        "--confirm-authorized", "--title", "feat(loom): safe",
        "--body-file", str(body),
    ], out, err)
    assert rc == 0, err.getvalue()
    assert not any("push" in call for call in calls.calls)
    assert not any("create" in call for call in calls.calls)
    assert "pull/7" in out.getvalue()


def test_publish_requires_authorization_and_absolute_body(tmp_path: Path, monkeypatch) -> None:
    repo = repository(tmp_path)
    monkeypatch.chdir(repo)
    out, err = StringIO(), StringIO()
    assert loom_checker.cmd_publish([], out, err) == 2
    assert loom_checker.cmd_publish([
        "--confirm-authorized", "--title", "feat(loom): safe",
        "--body-file", "relative.md",
    ], out, err) == 2


def test_publish_rejects_repository_redirecting_environment(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("")
    monkeypatch.setenv("GH_REPO", "attacker/target")
    _, rc, _, err = invoke(tmp_path, monkeypatch, calls)
    assert rc == 2
    assert "GH_REPO" in err
    assert calls.calls == []


def test_publish_does_not_replay_functional_executables(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("")
    checked: list[list[str]] = []

    def attestation_only(args, *unused, **kwargs):
        checked.append(args)
        return 0

    repo = repository(tmp_path)
    body = tmp_path / "body.md"
    body.write_text("body\n", encoding="utf-8")
    calls.head = git(repo, "rev-parse", "HEAD")
    monkeypatch.chdir(repo)
    monkeypatch.setattr(loom_checker, "run_publish_external", calls)
    monkeypatch.setattr(loom_checker, "_cmd_push", attestation_only)
    monkeypatch.setattr(loom_checker.shutil, "which", lambda name: f"/trusted/{name}")
    assert loom_checker.cmd_publish([
        "--confirm-authorized", "--title", "feat(loom): safe",
        "--body-file", str(body),
    ]) == 0
    assert checked == [["--head", calls.head, "--require-live-head"]]


def test_publish_rejects_diverged_remote_before_push(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("")
    repo = repository(tmp_path)
    calls.head = git(repo, "rev-parse", "HEAD")
    calls.remote_head = "f" * 40
    body = tmp_path / "body.md"
    body.write_text("body\n", encoding="utf-8")
    monkeypatch.chdir(repo)
    monkeypatch.setattr(loom_checker, "run_publish_external", calls)
    monkeypatch.setattr(loom_checker, "_cmd_push", lambda *args, **kwargs: 0)
    monkeypatch.setattr(loom_checker.shutil, "which", lambda name: f"/trusted/{name}")
    err = StringIO()
    rc = loom_checker.cmd_publish([
        "--confirm-authorized", "--title", "feat(loom): safe",
        "--body-file", str(body),
    ], StringIO(), err)
    assert rc == 1
    assert "remote branch" in err.getvalue()
    assert not any("push" in call for call in calls.calls)


def test_publish_rechecks_remote_head_before_pr_creation(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("")
    calls.move_remote_on_pr_list = True
    _, rc, _, err = invoke(tmp_path, monkeypatch, calls)
    assert rc == 1
    assert "remote branch moved before PR creation" in err
    assert not any("create" in call for call in calls.calls)
