from __future__ import annotations

import json
import os
import subprocess
from io import StringIO
from pathlib import Path

import loom_checker


def trusted_executable(name: str) -> str:
    return "/usr/bin/git" if name == "git" else "/usr/local/bin/gh"


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
    def __init__(
        self, head: str, existing_pr: str | None = None, *, draft: bool = False
    ) -> None:
        self.head = head
        self.remote_head: str | None = None
        self.existing_pr = existing_pr
        self.move_remote_on_pr_list = False
        self.cross_repository_pr = False
        self.fail_create_once = False
        self.fail_update = False
        self.fail_ready = False
        self.existing_pr_draft = draft
        self.move_head_on_update = False
        self.move_remote_on_update = False
        self.move_head_on_ready = False
        self.move_remote_on_ready = False
        self.change_pushurl_on_ready = False
        self.change_pushurl_on_remote_read = False
        self.switch_branch_on_remote_read = False
        self.change_pushurl_on_pr_list = False
        self.change_uploadpack_on_final_remote_read = False
        self.remote_reads = 0
        self.required_checks = [[{"name": "gate", "state": "SUCCESS", "bucket": "pass"}]]
        self.required_check_returncodes: list[int] = []
        self.calls: list[list[str]] = []

    def __call__(self, argv, **kwargs):
        argv = [str(value) for value in argv]
        self.calls.append(argv)
        if "repo" in argv and "view" in argv:
            return subprocess.CompletedProcess(argv, 0, "main\n", "")
        if "ls-remote" in argv:
            self.remote_reads += 1
            if self.remote_reads == 1 and self.change_pushurl_on_remote_read:
                git(Path(kwargs["cwd"]), "config", "remote.origin.pushurl",
                    "git@github.com:attacker/project.git")
            if self.remote_reads == 1 and self.switch_branch_on_remote_read:
                git(Path(kwargs["cwd"]), "switch", "-q", "-c", "alternate")
            if self.remote_reads == 3 and self.change_uploadpack_on_final_remote_read:
                git(Path(kwargs["cwd"]), "config", "remote.origin.uploadpack",
                    "/tmp/attacker-upload-pack")
            output = f"{self.remote_head}\trefs/heads/feature\n" if self.remote_head else ""
            return subprocess.CompletedProcess(argv, 0, output, "")
        if "push" in argv:
            self.remote_head = self.head
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "api" in argv and any("/pulls?" in token for token in argv):
            if self.change_pushurl_on_pr_list:
                git(Path(kwargs["cwd"]), "config", "remote.origin.pushurl",
                    "git@github.com:attacker/project.git")
            if self.move_remote_on_pr_list:
                self.remote_head = "e" * 40
            prs = []
            if self.existing_pr:
                full_name = "attacker/project" if self.cross_repository_pr else "example/project"
                prs.append({
                    "html_url": self.existing_pr,
                    "draft": self.existing_pr_draft,
                    "head": {"sha": self.head, "repo": {"full_name": full_name}},
                    "base": {"ref": "main", "repo": {"full_name": "example/project"}},
                })
            output = json.dumps(prs)
            return subprocess.CompletedProcess(argv, 0, output, "")
        if "pr" in argv and "create" in argv:
            if self.fail_create_once:
                self.fail_create_once = False
                return subprocess.CompletedProcess(argv, 1, "", "temporary failure")
            self.existing_pr = "https://github.com/example/project/pull/1"
            return subprocess.CompletedProcess(argv, 0, f"{self.existing_pr}\n", "")
        if "pr" in argv and "edit" in argv:
            if self.fail_update:
                return subprocess.CompletedProcess(argv, 1, "", "update failed")
            if self.move_head_on_update:
                git(Path(kwargs["cwd"]), "commit", "--allow-empty", "-q", "-m", "moved")
            if self.move_remote_on_update:
                self.remote_head = "d" * 40
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "pr" in argv and "ready" in argv:
            if self.fail_ready:
                return subprocess.CompletedProcess(argv, 1, "", "ready failed")
            if self.move_head_on_ready:
                git(Path(kwargs["cwd"]), "commit", "--allow-empty", "-q", "-m", "moved")
            if self.move_remote_on_ready:
                self.remote_head = "c" * 40
            if self.change_pushurl_on_ready:
                git(Path(kwargs["cwd"]), "config", "remote.origin.pushurl",
                    "git@github.com:attacker/project.git")
            self.existing_pr_draft = False
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "pr" in argv and "checks" in argv:
            snapshot = self.required_checks.pop(0)
            return subprocess.CompletedProcess(
                argv,
                self.required_check_returncodes.pop(0)
                if self.required_check_returncodes else 0,
                snapshot if isinstance(snapshot, str) else json.dumps(snapshot),
                "CI observation failed",
            )
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
        loom_checker, "resolve_publish_executable",
        trusted_executable,
    )
    out, err = StringIO(), StringIO()
    argv = [
        "--confirm-authorized", "--title", "feat(loom): publish safely",
        "--body-file", str(body), *extra,
    ]
    rc = loom_checker.cmd_publish(argv, out, err)
    return repo, rc, out.getvalue(), err.getvalue()


def publication_intent(repo: Path, *, automatic: bool, change_id: str = "change") -> Path:
    intent = repo / "docs" / "loom" / "intent" / f"{change_id}.md"
    intent.parent.mkdir(parents=True, exist_ok=True)
    outcome = (
        "Confirmation of the intent authorizes Loom to publish the completed "
        "branch automatically."
        if automatic
        else "Publish the completed branch after a separate Ship decision."
    )
    intent.write_text(
        "# Change\nstatus: confirmed 2026-09-09\n\n"
        f"## Proposed outcome\n{outcome}\n",
        encoding="utf-8",
    )
    return intent


def attestation(repo: Path, change_id: str = "change") -> Path:
    target = repo / "docs" / "loom" / change_id / "attestation.json"
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({"change_id": change_id}), encoding="utf-8")
    return target


def test_confirmed_current_intent_publishes_without_ship_reask(
    tmp_path: Path, monkeypatch
) -> None:
    calls = ExternalCalls("")
    repo = repository(tmp_path)
    git(repo, "branch", "main")
    intent = publication_intent(repo, automatic=True)
    attestation(repo)
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "authorize publication")
    body = tmp_path / "body.md"
    body.write_text("body\n", encoding="utf-8")
    calls.head = git(repo, "rev-parse", "HEAD")
    monkeypatch.chdir(repo)
    monkeypatch.setattr(loom_checker, "run_publish_external", calls)
    monkeypatch.setattr(loom_checker, "_cmd_push", lambda *args, **kwargs: 0)
    monkeypatch.setattr(loom_checker, "resolve_publish_executable", trusted_executable)

    err = StringIO()
    rc = loom_checker.cmd_publish([
        "--intent", str(intent), "--title", "feat(loom): safe",
        "--body-file", str(body),
    ], StringIO(), err)

    assert rc == 0, err.getvalue()
    assert any("push" in call for call in calls.calls)
    assert any("pr" in call and "create" in call for call in calls.calls)
    assert not any("merge" in call for call in calls.calls)


def test_legacy_intent_requires_one_publication_decision(
    tmp_path: Path, monkeypatch
) -> None:
    calls = ExternalCalls("")
    repo = repository(tmp_path)
    git(repo, "branch", "main")
    intent = publication_intent(repo, automatic=False)
    attestation(repo)
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "legacy evidence")
    body = tmp_path / "body.md"
    body.write_text("body\n", encoding="utf-8")
    calls.head = git(repo, "rev-parse", "HEAD")
    monkeypatch.chdir(repo)
    monkeypatch.setattr(loom_checker, "run_publish_external", calls)
    monkeypatch.setattr(loom_checker, "_cmd_push", lambda *args, **kwargs: 0)
    monkeypatch.setattr(loom_checker, "resolve_publish_executable", trusted_executable)

    err = StringIO()
    rc = loom_checker.cmd_publish([
        "--intent", str(intent), "--title", "feat(loom): safe",
        "--body-file", str(body),
    ], StringIO(), err)

    assert rc == 2
    assert "publication decision" in err.getvalue()
    assert calls.calls == []


def test_unrelated_intent_cannot_authorize_attested_change(
    tmp_path: Path, monkeypatch
) -> None:
    calls = ExternalCalls("")
    repo = repository(tmp_path)
    git(repo, "branch", "main")
    publication_intent(repo, automatic=False)
    unrelated = publication_intent(repo, automatic=True, change_id="unrelated")
    attestation(repo)
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "attest change")
    body = tmp_path / "body.md"
    body.write_text("body\n", encoding="utf-8")
    monkeypatch.chdir(repo)
    monkeypatch.setattr(loom_checker, "resolve_publish_executable", trusted_executable)
    monkeypatch.setattr(loom_checker, "run_publish_external", calls)

    err = StringIO()
    rc = loom_checker.cmd_publish([
        "--intent", str(unrelated), "--title", "feat(loom): safe",
        "--body-file", str(body),
    ], StringIO(), err)

    assert rc == 2
    assert "attested change" in err.getvalue()
    assert calls.calls == []


def test_untracked_or_mutated_intent_cannot_authorize(
    tmp_path: Path, monkeypatch
) -> None:
    for state in ("untracked", "mutated"):
        case = tmp_path / state
        case.mkdir()
        calls = ExternalCalls("")
        repo = repository(case)
        git(repo, "branch", "main")
        if state == "mutated":
            publication_intent(repo, automatic=False)
        attestation(repo)
        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", "attest change")
        intent = publication_intent(repo, automatic=True)
        body = case / "body.md"
        body.write_text("body\n", encoding="utf-8")
        monkeypatch.chdir(repo)
        monkeypatch.setattr(loom_checker, "resolve_publish_executable", trusted_executable)
        monkeypatch.setattr(loom_checker, "run_publish_external", calls)

        err = StringIO()
        rc = loom_checker.cmd_publish([
            "--intent", str(intent), "--title", "feat(loom): safe",
            "--body-file", str(body),
        ], StringIO(), err)

        assert rc == 2, state
        assert "committed intent" in err.getvalue(), state
        assert calls.calls == [], state


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
    assert f"Attestation validated for {head}" in out
    assert "Publication target: github.com/example/project base main" in out


def test_publish_reuses_existing_pr_and_replaces_title_and_body(tmp_path: Path, monkeypatch) -> None:
    """Ground gh pr edit URL, --title, and --body-file.

    https://cli.github.com/manual/gh_pr_edit
    """
    calls = ExternalCalls("", "https://github.com/example/project/pull/7")
    repo = repository(tmp_path)
    calls.head = git(repo, "rev-parse", "HEAD")
    calls.remote_head = calls.head
    body = tmp_path / "body.md"
    body.write_text("body\n", encoding="utf-8")
    monkeypatch.chdir(repo)
    monkeypatch.setattr(loom_checker, "run_publish_external", calls)
    monkeypatch.setattr(loom_checker, "_cmd_push", lambda *args, **kwargs: 0)
    monkeypatch.setattr(loom_checker, "resolve_publish_executable", trusted_executable)
    out, err = StringIO(), StringIO()
    rc = loom_checker.cmd_publish([
        "--confirm-authorized", "--title", "feat(loom): safe",
        "--body-file", str(body),
    ], out, err)
    assert rc == 0, err.getvalue()
    assert not any("push" in call for call in calls.calls)
    assert not any("create" in call for call in calls.calls)
    edit = next(call for call in calls.calls if "edit" in call)
    assert edit[edit.index("--title") + 1] == "feat(loom): safe"
    assert edit[edit.index("--body-file") + 1] == str(body)
    assert sum("checks" in call for call in calls.calls) == 1
    assert "pull/7" in out.getvalue()


def test_publish_marks_matching_draft_ready_after_context_update(
    tmp_path: Path, monkeypatch
) -> None:
    """Ground gh pr ready <url>.

    https://cli.github.com/manual/gh_pr_ready
    """
    calls = ExternalCalls(
        "", "https://github.com/example/project/pull/7", draft=True
    )

    _, rc, _, err = invoke(tmp_path, monkeypatch, calls)

    assert rc == 0, err
    edit_index = next(i for i, call in enumerate(calls.calls) if "edit" in call)
    ready_index = next(i for i, call in enumerate(calls.calls) if "ready" in call)
    checks_index = next(i for i, call in enumerate(calls.calls) if "checks" in call)
    assert edit_index < ready_index < checks_index


def test_publish_blocks_existing_pr_update_and_ready_failures(
    tmp_path: Path, monkeypatch
) -> None:
    for failure in ("fail_update", "fail_ready"):
        case = tmp_path / failure
        case.mkdir()
        calls = ExternalCalls(
            "", "https://github.com/example/project/pull/7", draft=True
        )
        setattr(calls, failure, True)

        _, rc, out, err = invoke(case, monkeypatch, calls)

        assert rc == 1, failure
        assert failure.removeprefix("fail_") in err, failure
        assert "Required CI passed" not in out, failure
        assert not any("checks" in call for call in calls.calls), failure


def test_publish_revalidates_live_head_and_remote_after_existing_pr_update(
    tmp_path: Path, monkeypatch
) -> None:
    cases = {
        "move_head_on_update": "live HEAD moved after PR update",
        "move_remote_on_update": "remote branch moved after PR update",
    }
    for mutation, message in cases.items():
        case = tmp_path / mutation
        case.mkdir()
        calls = ExternalCalls(
            "", "https://github.com/example/project/pull/7", draft=True
        )
        setattr(calls, mutation, True)

        _, rc, _, err = invoke(case, monkeypatch, calls)

        assert rc == 1, mutation
        assert message in err, mutation
        assert not any("ready" in call or "checks" in call for call in calls.calls)


def test_publish_revalidates_head_remote_and_identity_after_draft_ready(
    tmp_path: Path, monkeypatch
) -> None:
    cases = {
        "move_head_on_ready": "live HEAD moved after PR readiness",
        "move_remote_on_ready": "remote branch moved after PR readiness",
        "change_pushurl_on_ready": "publication identity changed after PR readiness",
    }
    for mutation, message in cases.items():
        case = tmp_path / mutation
        case.mkdir()
        calls = ExternalCalls(
            "", "https://github.com/example/project/pull/7", draft=True
        )
        setattr(calls, mutation, True)

        _, rc, _, err = invoke(case, monkeypatch, calls)

        assert rc == 1, mutation
        assert message in err, mutation
        assert not any("checks" in call for call in calls.calls)


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


def test_publish_rejects_git_common_dir_before_network(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("")
    repo = repository(tmp_path)
    body = tmp_path / "body.md"
    body.write_text("body\n", encoding="utf-8")
    monkeypatch.setenv("GIT_COMMON_DIR", str(tmp_path / "other.git"))
    monkeypatch.chdir(repo)
    monkeypatch.setattr(loom_checker, "run_publish_external", calls)
    err_stream = StringIO()
    rc = loom_checker.cmd_publish([
        "--confirm-authorized", "--title", "feat(loom): safe",
        "--body-file", str(body),
    ], StringIO(), err_stream)
    err = err_stream.getvalue()
    assert rc == 2
    assert "GIT_COMMON_DIR" in err
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
    monkeypatch.setattr(loom_checker, "resolve_publish_executable", trusted_executable)
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
    monkeypatch.setattr(loom_checker, "resolve_publish_executable", trusted_executable)
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


def test_publish_rejects_git_config_parameters_before_network(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("")
    monkeypatch.setenv("GIT_CONFIG_PARAMETERS", "'remote.origin.pushurl'='ssh://evil/x/y'")
    _, rc, _, err = invoke(tmp_path, monkeypatch, calls)
    assert rc == 2
    assert "GIT_CONFIG_PARAMETERS" in err
    assert calls.calls == []


def test_publish_rejects_git_redirect_config_before_push(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("")
    repo = repository(tmp_path)
    redirects = {
        "remote.origin.pushurl": "git@github.com:attacker/project.git",
        "core.sshCommand": "/tmp/attacker-ssh",
        "url.https://attacker.example/.pushInsteadOf": "git@github.com:",
        "url.https://attacker.example/.insteadOf": "git@github.com:",
        "remote.origin.vcs": "attacker",
        "remote.origin.receivepack": "/tmp/attacker-receive-pack",
        "remote.origin.uploadpack": "/tmp/attacker-upload-pack",
    }
    body = tmp_path / "body.md"
    body.write_text("body\n", encoding="utf-8")
    for key, value in redirects.items():
        git(repo, "config", key, value)
        calls.head = git(repo, "rev-parse", "HEAD")
        calls.calls.clear()
        monkeypatch.chdir(repo)
        monkeypatch.setattr(loom_checker, "run_publish_external", calls)
        monkeypatch.setattr(loom_checker, "_cmd_push", lambda *args, **kwargs: 0)
        monkeypatch.setattr(loom_checker, "resolve_publish_executable", trusted_executable)
        err = StringIO()
        rc = loom_checker.cmd_publish([
            "--confirm-authorized", "--title", "feat(loom): safe",
            "--body-file", str(body),
        ], StringIO(), err)
        assert rc == 1, key
        assert "configuration" in err.getvalue(), key
        assert not any("push" in call for call in calls.calls), key
        git(repo, "config", "--unset-all", key)


def test_publish_revalidates_origin_and_branch_before_push(tmp_path: Path, monkeypatch) -> None:
    for mutation in ("change_pushurl_on_remote_read", "switch_branch_on_remote_read"):
        case = tmp_path / mutation
        case.mkdir()
        calls = ExternalCalls("")
        setattr(calls, mutation, True)
        _, rc, _, err = invoke(case, monkeypatch, calls)
        assert rc == 1, mutation
        assert "changed before push" in err, mutation
        assert not any("push" in call for call in calls.calls), mutation


def test_publish_revalidates_identity_around_final_remote_read(tmp_path: Path, monkeypatch) -> None:
    for mutation in ("change_pushurl_on_pr_list", "change_uploadpack_on_final_remote_read"):
        case = tmp_path / mutation
        case.mkdir()
        calls = ExternalCalls("")
        setattr(calls, mutation, True)
        _, rc, _, err = invoke(case, monkeypatch, calls)
        assert rc == 1, mutation
        assert "before PR creation" in err, mutation
        assert not any("create" in call for call in calls.calls), mutation


def test_publish_rejects_cross_repository_pr_match(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("", "https://github.com/attacker/project/pull/7")
    calls.cross_repository_pr = True
    _, rc, _, err = invoke(tmp_path, monkeypatch, calls)
    assert rc == 1
    assert "identity" in err
    assert not any("create" in call for call in calls.calls)


def test_publish_uses_origin_bound_api_not_branch_only_pr_list(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("", "https://github.com/example/project/pull/7")
    repo, rc, _, err = invoke(tmp_path, monkeypatch, calls)
    assert rc == 0, err
    assert any("api" in call and any("/pulls?" in token for token in call) for call in calls.calls)
    assert not any("pr" in call and "list" in call for call in calls.calls)
    assert git(repo, "rev-parse", "HEAD") == calls.head


def test_executable_resolution_ignores_path_shadow(tmp_path: Path, monkeypatch) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake = fake_bin / "git"
    fake.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", str(fake_bin))
    resolved = loom_checker.resolve_publish_executable("git")
    assert resolved is None or Path(resolved) != fake.resolve()


def test_retry_after_pr_creation_failure_does_not_repush(tmp_path: Path, monkeypatch) -> None:
    calls = ExternalCalls("")
    calls.fail_create_once = True
    repo, first_rc, _, first_err = invoke(tmp_path, monkeypatch, calls)
    assert first_rc == 1
    assert "temporary failure" in first_err
    first_pushes = sum("push" in call for call in calls.calls)

    body = tmp_path / "body.md"
    monkeypatch.chdir(repo)
    out, err = StringIO(), StringIO()
    second_rc = loom_checker.cmd_publish([
        "--confirm-authorized", "--title", "feat(loom): publish safely",
        "--body-file", str(body),
    ], out, err)
    assert second_rc == 0, err.getvalue()
    assert sum("push" in call for call in calls.calls) == first_pushes
    assert "pull/1" in out.getvalue()


def test_publish_observes_required_ci_immediately_then_every_thirty_seconds(
    tmp_path: Path, monkeypatch
) -> None:
    calls = ExternalCalls("")
    calls.required_checks = [
        [{"name": "gate", "state": "IN_PROGRESS", "bucket": "pending"}],
        [{"name": "gate", "state": "SUCCESS", "bucket": "pass"}],
    ]
    waits: list[int] = []
    monkeypatch.setattr(loom_checker, "wait_publish_interval", waits.append, raising=False)

    _, rc, out, err = invoke(tmp_path, monkeypatch, calls)

    assert rc == 0, err
    checks = [call for call in calls.calls if "checks" in call]
    assert len(checks) == 2
    assert all("--required" in call for call in checks)
    assert waits == [30]
    assert "Required CI passed" in out
    assert "pending" not in out.casefold()


def test_publish_stops_on_required_ci_terminal_blockers(
    tmp_path: Path, monkeypatch
) -> None:
    terminal = {
        "FAILURE": "failed",
        "CANCELLED": "cancelled",
        "ACTION_REQUIRED": "requires user action",
    }
    for state, message in terminal.items():
        case = tmp_path / state.casefold()
        case.mkdir()
        calls = ExternalCalls("")
        calls.required_checks = [
            [{"name": "gate", "state": state, "bucket": "fail"}]
        ]
        waits: list[int] = []
        monkeypatch.setattr(loom_checker, "wait_publish_interval", waits.append, raising=False)

        _, rc, out, err = invoke(case, monkeypatch, calls)

        assert rc == 1, state
        assert message in err.casefold(), state
        assert waits == [], state
        assert "Required CI passed" not in out, state


def test_publish_accepts_gh_pending_exit_code_eight(tmp_path: Path, monkeypatch) -> None:
    """Ground --required, JSON fields, and pending rc=8.

    https://cli.github.com/manual/gh_pr_checks
    """
    calls = ExternalCalls("")
    calls.required_checks = [
        [{"name": "gate", "state": "IN_PROGRESS", "bucket": "pending"}],
        [{"name": "gate", "state": "SUCCESS", "bucket": "pass"}],
    ]
    calls.required_check_returncodes = [8, 0]
    waits: list[int] = []
    monkeypatch.setattr(loom_checker, "wait_publish_interval", waits.append)

    _, rc, _, err = invoke(tmp_path, monkeypatch, calls)

    assert rc == 0, err
    assert waits == [30]


def test_publish_blocks_unexpected_gh_checks_exit_and_malformed_json(
    tmp_path: Path, monkeypatch
) -> None:
    cases = (("exit", "[]", 2, "CI observation failed"),
             ("json", "not-json", 0, "cannot decode"))
    for name, payload, returncode, message in cases:
        case = tmp_path / name
        case.mkdir()
        calls = ExternalCalls("")
        calls.required_checks = [payload]
        calls.required_check_returncodes = [returncode]

        _, rc, _, err = invoke(case, monkeypatch, calls)

        assert rc == 1, name
        assert message.casefold() in err.casefold(), name


def test_publish_rechecks_an_initial_empty_required_set_before_pass(
    tmp_path: Path, monkeypatch
) -> None:
    calls = ExternalCalls("")
    calls.required_checks = [
        [],
        [{"name": "gate", "state": "SUCCESS", "bucket": "pass"}],
    ]
    waits: list[int] = []
    monkeypatch.setattr(loom_checker, "wait_publish_interval", waits.append)

    _, rc, out, err = invoke(tmp_path, monkeypatch, calls)

    assert rc == 0, err
    assert waits == [30]
    assert "Required CI passed" in out


def test_publish_reports_two_empty_required_sets_as_no_checks_registered(
    tmp_path: Path, monkeypatch
) -> None:
    calls = ExternalCalls("")
    calls.required_checks = [[], []]
    waits: list[int] = []
    monkeypatch.setattr(loom_checker, "wait_publish_interval", waits.append)

    _, rc, out, err = invoke(tmp_path, monkeypatch, calls)

    assert rc == 0, err
    assert waits == [30]
    assert "no required checks registered" in out.casefold()
    assert "Required CI passed" not in out


def test_publish_stops_permanent_pending_after_sixty_minutes_without_resume_state(
    tmp_path: Path, monkeypatch
) -> None:
    calls = ExternalCalls("")
    pending = [{"name": "gate", "state": "IN_PROGRESS", "bucket": "pending"}]
    calls.required_checks = [pending] * 121
    waits: list[int] = []
    monkeypatch.setattr(loom_checker, "wait_publish_interval", waits.append)
    before = set(tmp_path.rglob("*"))

    _, rc, out, err = invoke(tmp_path, monkeypatch, calls)

    assert rc == 1
    assert "requires user action" in err.casefold()
    assert "reliable terminal result" in err.casefold()
    assert waits == [30] * 120
    assert "pending" not in out.casefold()
    created = set(tmp_path.rglob("*")) - before
    assert not any(path.name.endswith((".pid", ".state", ".resume")) for path in created)
