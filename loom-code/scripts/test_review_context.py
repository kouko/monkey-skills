"""Regression coverage for the standalone review-context resolver."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


REVIEWER_CONTRACT_RESOURCES = {
    "live_gate_station_receipt",
    "live_gate_adapter_probe",
    "review_scope",
    "gate_markers",
    "doc_citation_checker",
    "attack_catalogue",
    "reviewer_discipline",
    "code_reviewer",
    "docs_reviewer",
    "code_review_skill",
    "docs_review_skill",
    "quality_rubric",
    "architecture_rubric",
    "security_checklist",
    "spec_consistency_checklist",
    "app_security_standard",
    "character_encoding_security_standard",
    "deliberate_simplification_standard",
    "external_surface_grounding_standard",
    "naming_and_functions_standard",
    "pragmatic_principles_standard",
    "refactoring_standard",
    "solid_principles_standard",
    "tdd_standard",
}


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_review_context_git_hands_utf8_bytes_argv(monkeypatch, tmp_path: Path) -> None:
    """`review_context._git` must delegate to `git_exec.run_git`'s UTF-8-bytes
    argv + `encoding="utf-8"` body, not its own bare-`str` `subprocess.run`."""
    import git_exec
    import review_context

    captured: dict[str, object] = {}

    def _capture(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(git_exec.subprocess, "run", _capture)
    review_context._git(tmp_path, "rev-parse", "HEAD")

    argv = captured["argv"]
    assert all(isinstance(item, bytes) for item in argv), argv
    assert captured["kwargs"]["encoding"] == "utf-8"


def _consumer_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "consumer"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "review@example.test")
    _git(repo, "config", "user.name", "Review Context Test")
    (repo / "README.md").write_text("# Consumer\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "initial")
    return repo


def _make_review_scope_escape(plugin_root: Path, outside: Path) -> None:
    review_scope = plugin_root / "scripts" / "review_scope.py"
    review_scope.unlink()
    review_scope.symlink_to(outside)


def test_context_uses_script_parent_not_consumer_repo(tmp_path: Path) -> None:
    """A copied standalone plugin must not look for consumer/loom-code."""
    installed_root = tmp_path / "plugin-cache" / "loom-code" / "0.100.0"
    installed_root.parent.mkdir(parents=True)
    shutil.copytree(PLUGIN_ROOT, installed_root)
    consumer = _consumer_repo(tmp_path)
    assert not (consumer / "loom-code").exists()

    result = subprocess.run(
        [
            sys.executable,
            str(installed_root / "scripts" / "review_context.py"),
            "--repo",
            str(consumer),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    context = json.loads(result.stdout)

    assert context["target_repo"] == str(consumer.resolve())
    assert context["reviewed_sha"] == _git(consumer, "rev-parse", "HEAD")
    # Read from the manifest, not hardcoded: this test is about WHERE the
    # root is resolved from, not which version ships. A literal here turns
    # every release bump into an unrelated failure in a path-resolution test.
    expected_version = json.loads(
        (installed_root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )["version"]
    assert context["plugin_version"] == expected_version
    assert context["resources"]
    for resource in context["resources"].values():
        resource_path = Path(resource)
        assert resource_path.is_absolute()
        assert resource_path.is_file()
        assert resource_path.is_relative_to(installed_root)


def test_context_includes_all_reviewer_contract_resources(tmp_path: Path) -> None:
    """Every reviewer contract gets an approved absolute plugin resource."""
    installed_root = tmp_path / "plugin-cache" / "loom-code" / "0.100.0"
    installed_root.parent.mkdir(parents=True)
    shutil.copytree(PLUGIN_ROOT, installed_root)
    consumer = _consumer_repo(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(installed_root / "scripts" / "review_context.py"),
            "--repo",
            str(consumer),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    context = json.loads(result.stdout)

    assert set(context["resources"]) == REVIEWER_CONTRACT_RESOURCES
    for resource in context["resources"].values():
        resource_path = Path(resource)
        assert resource_path.is_absolute()
        assert resource_path.is_file()
        assert resource_path.is_relative_to(installed_root)


def test_context_includes_doc_citation_checker_resource(tmp_path: Path) -> None:
    """A copied install approves the docs citation checker from its own root."""
    installed_root = tmp_path / "plugin-cache" / "loom-code" / "0.98.0"
    installed_root.parent.mkdir(parents=True)
    shutil.copytree(PLUGIN_ROOT, installed_root)
    consumer = _consumer_repo(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(installed_root / "scripts" / "review_context.py"),
            "--repo",
            str(consumer),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    resource = Path(json.loads(result.stdout)["resources"]["doc_citation_checker"])

    assert resource == installed_root / "scripts" / "check_doc_citations.py"
    assert resource.is_absolute()
    assert resource.is_file()
    assert resource.is_relative_to(installed_root)


def test_context_includes_attack_catalogue_resource(tmp_path: Path) -> None:
    """code-reviewer.md must reach the attack catalogue via `resources`,
    never by deriving a plugin-relative path itself (docs-arm A3)."""
    installed_root = tmp_path / "plugin-cache" / "loom-code" / "0.108.0"
    installed_root.parent.mkdir(parents=True)
    shutil.copytree(PLUGIN_ROOT, installed_root)
    consumer = _consumer_repo(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(installed_root / "scripts" / "review_context.py"),
            "--repo",
            str(consumer),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    resource = Path(json.loads(result.stdout)["resources"]["attack_catalogue"])

    assert resource == (
        installed_root
        / "skills"
        / "requesting-code-review"
        / "references"
        / "attack-catalogue.md"
    )
    assert resource.is_absolute()
    assert resource.is_file()
    assert resource.is_relative_to(installed_root)


def test_context_refuses_damaged_or_escaping_installed_resources(
    tmp_path: Path,
) -> None:
    """A review packet must not approve missing or out-of-plugin resources."""
    consumer = _consumer_repo(tmp_path)
    for name, damage in (
        ("missing", lambda root: (root / "agents" / "code-reviewer.md").unlink()),
        (
            "escaping",
            lambda root: _make_review_scope_escape(
                root, tmp_path / "outside-plugin.py"
            ),
        ),
    ):
        installed_root = tmp_path / name / "loom-code" / "0.100.0"
        installed_root.parent.mkdir(parents=True)
        shutil.copytree(PLUGIN_ROOT, installed_root)
        (tmp_path / "outside-plugin.py").write_text("# outside\n", encoding="utf-8")
        damage(installed_root)

        result = subprocess.run(
            [
                sys.executable,
                str(installed_root / "scripts" / "review_context.py"),
                "--repo",
                str(consumer),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Traceback" not in result.stderr
        assert "review-context: refused" in result.stderr


def _dispatch_log(repo: Path) -> Path:
    git_dir = Path(_git(repo, "rev-parse", "--git-dir"))
    if not git_dir.is_absolute():
        git_dir = repo / git_dir
    return git_dir / "loom" / "review-dispatches.jsonl"


def test_main_appends_one_dispatch_log_line_per_invocation(
    tmp_path: Path, capsys
) -> None:
    """Every `--repo` packet emission is one reviewer fan-out: log it once."""
    from review_context import main

    consumer = _consumer_repo(tmp_path)
    _git(consumer, "checkout", "-b", "feat/x")
    head = _git(consumer, "rev-parse", "HEAD")
    log = _dispatch_log(consumer)
    assert not log.parent.exists()

    assert main(["--repo", str(consumer)]) == 0
    first_stdout = capsys.readouterr().out
    assert main(["--repo", str(consumer)]) == 0
    assert capsys.readouterr().out == first_stdout

    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    for line in lines:
        entry = json.loads(line)
        assert set(entry) == {
            "schema", "recorded_at", "branch", "reviewed_sha", "plugin_version",
        }
        assert entry["schema"] == "review-dispatch-log/v1"
        assert entry["branch"] == "feat/x"
        assert entry["reviewed_sha"] == head
        assert entry["plugin_version"] == json.loads(first_stdout)["plugin_version"]
        assert entry["recorded_at"].endswith("+00:00")


def test_validate_appends_nothing_and_detached_head_logs_detached(
    tmp_path: Path, capsys
) -> None:
    """`--validate` is not a fan-out; a detached HEAD still records a line."""
    from review_context import main, resolve_context

    consumer = _consumer_repo(tmp_path)
    packet = tmp_path / "packet.json"
    packet.write_text(json.dumps(resolve_context(consumer)), encoding="utf-8")
    log = _dispatch_log(consumer)

    assert main(["--validate", str(packet)]) == 0
    assert not log.exists()

    head = _git(consumer, "rev-parse", "HEAD")
    _git(consumer, "checkout", "--detach", head)
    assert main(["--repo", str(consumer)]) == 0
    capsys.readouterr()
    (entry,) = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()]
    assert entry["branch"] == "DETACHED"
    assert entry["reviewed_sha"] == head


def test_dispatch_log_append_failure_keeps_packet_and_exit_code(
    tmp_path: Path, capsys
) -> None:
    """The packet is the product; a read-only log dir only warns on stderr."""
    import os

    from review_context import main

    if os.geteuid() == 0:  # root ignores directory modes
        import pytest

        pytest.skip("permission bits are not enforced for root")
    consumer = _consumer_repo(tmp_path)
    log = _dispatch_log(consumer)
    log.parent.mkdir(parents=True)
    log.parent.chmod(0o500)
    try:
        assert main(["--repo", str(consumer)]) == 0
    finally:
        log.parent.chmod(0o700)
    captured = capsys.readouterr()
    assert json.loads(captured.out)["reviewed_sha"] == _git(consumer, "rev-parse", "HEAD")
    assert "dispatch log not written" in captured.err
    assert not log.exists()
