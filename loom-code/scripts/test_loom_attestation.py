from __future__ import annotations

import subprocess
import hashlib
import json
import os
import sys
from pathlib import Path

import loom_checker


CHANGE = "2026-09-08-example"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def commit(repo: Path, message: str) -> str:
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def repo_with_content(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    (repo / "src.py").write_text("VALUE = 1\n", encoding="utf-8")
    commit(repo, "initial")
    return repo


def manifest() -> dict:
    return {"publication_only_paths": ["docs/loom/<change-id>/attestation.json"]}


def test_functional_digest_ignores_declared_publication_paths(tmp_path: Path) -> None:
    repo = repo_with_content(tmp_path)
    before = git(repo, "rev-parse", "HEAD")
    evidence = repo / f"docs/loom/{CHANGE}/attestation.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text('{"content_digest":"old"}\n', encoding="utf-8")
    after = commit(repo, "publication evidence")

    assert loom_checker.functional_content_digest(repo, before, CHANGE, manifest()) == \
        loom_checker.functional_content_digest(repo, after, CHANGE, manifest())


def test_functional_mutation_invalidates_digest(tmp_path: Path) -> None:
    repo = repo_with_content(tmp_path)
    before = git(repo, "rev-parse", "HEAD")
    (repo / "src.py").write_text("VALUE = 2\n", encoding="utf-8")
    after = commit(repo, "functional change")

    assert loom_checker.functional_content_digest(repo, before, CHANGE, manifest()) != \
        loom_checker.functional_content_digest(repo, after, CHANGE, manifest())


def test_another_changes_attestation_is_functional_content(tmp_path: Path) -> None:
    repo = repo_with_content(tmp_path)
    before = git(repo, "rev-parse", "HEAD")
    other = repo / "docs/loom/another-change/attestation.json"
    other.parent.mkdir(parents=True)
    other.write_text("{}\n", encoding="utf-8")
    after = commit(repo, "other evidence")

    assert loom_checker.functional_content_digest(repo, before, CHANGE, manifest()) != \
        loom_checker.functional_content_digest(repo, after, CHANGE, manifest())


def matching_attestation(repo: Path) -> dict:
    command = "python3 -m pytest -q"
    return {
        "schema": "loom-attestation/v1",
        "change_id": CHANGE,
        "content_digest": loom_checker.functional_content_digest(
            repo, git(repo, "rev-parse", "HEAD"), CHANGE, manifest()
        ),
        "executions": [{
            "kind": "package-tests", "command": command, "artifact": "",
            "result": "pass", "command_digest": hashlib.sha256(command.encode()).hexdigest(),
        }],
        "verdicts": [{
            "reviewer": "reviewer-1", "vendor": "openai", "model": "test",
            "lens": "code", "verdict": "PASS", "findings": [],
        }],
        "findings": [],
    }


def test_matching_attestation_validates_without_executing_commands(tmp_path: Path) -> None:
    repo = repo_with_content(tmp_path)
    failures = loom_checker.validate_attestation(
        repo, git(repo, "rev-parse", "HEAD"), CHANGE, matching_attestation(repo), manifest()
    )
    assert failures == []


def test_well_formed_forged_attestation_fails_closed(tmp_path: Path) -> None:
    repo = repo_with_content(tmp_path)
    attestation = matching_attestation(repo)
    attestation["executions"][0]["command_digest"] = "0" * 64
    failures = loom_checker.validate_attestation(
        repo, git(repo, "rev-parse", "HEAD"), CHANGE, attestation, manifest()
    )
    assert any("command digest" in reason for _, reason in failures)


def test_stale_attestation_fails_closed(tmp_path: Path) -> None:
    repo = repo_with_content(tmp_path)
    attestation = matching_attestation(repo)
    (repo / "src.py").write_text("VALUE = 3\n", encoding="utf-8")
    head = commit(repo, "new behavior")
    failures = loom_checker.validate_attestation(repo, head, CHANGE, attestation, manifest())
    assert any("functional content digest" in reason for _, reason in failures)


def test_adversarial_execution_must_name_a_committed_artifact(tmp_path: Path) -> None:
    repo = repo_with_content(tmp_path)
    attestation = matching_attestation(repo)
    command = "python3 missing.py"
    attestation["executions"].append({
        "kind": "adversarial", "command": command, "artifact": "missing.py",
        "result": "pass", "command_digest": hashlib.sha256(command.encode()).hexdigest(),
    })
    failures = loom_checker.validate_attestation(
        repo, git(repo, "rev-parse", "HEAD"), CHANGE, attestation, manifest()
    )
    assert any("committed artifact" in reason for _, reason in failures)


def test_finalize_review_runs_and_writes_matching_attestation(tmp_path: Path) -> None:
    repo = repo_with_content(tmp_path)
    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.parent.mkdir(parents=True)
    kickoff.write_text("- package-tests: python3 -c pass — fixture (2026-09-08)\n")
    commit(repo, "declare tests")
    review_input = tmp_path / "review-input.json"
    review_input.write_text(json.dumps({
        "verdicts": [{
            "reviewer": "reviewer-1", "vendor": "openai", "model": "test",
            "lens": "code", "verdict": "PASS", "findings": [],
        }],
        "findings": [],
        "adversarial": [],
    }), encoding="utf-8")
    checker = Path(loom_checker.__file__)
    result = subprocess.run(
        [sys.executable, str(checker), "finalize-review", CHANGE, "--input", str(review_input)],
        cwd=repo, capture_output=True, text=True, env=os.environ.copy(),
    )
    assert result.returncode == 0, result.stderr
    output = repo / f"docs/loom/{CHANGE}/attestation.json"
    attestation = json.loads(output.read_text(encoding="utf-8"))
    assert loom_checker.validate_attestation(
        repo, git(repo, "rev-parse", "HEAD"), CHANGE, attestation, manifest()
    ) == []
    assert [run["kind"] for run in attestation["executions"]] == ["package-tests"]


def test_push_reuses_matching_attestation_without_subprocesses(
    tmp_path: Path, monkeypatch
) -> None:
    repo = repo_with_content(tmp_path)
    git(repo, "branch", "-M", "main")
    git(repo, "switch", "-q", "-c", "feature")
    (repo / "feature.py").write_text("ENABLED = True\n", encoding="utf-8")
    functional_head = commit(repo, "feature")
    attestation = matching_attestation(repo)
    target = repo / f"docs/loom/{CHANGE}/attestation.json"
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(attestation), encoding="utf-8")
    commit(repo, "generated evidence")

    def forbidden(*args, **kwargs):
        raise AssertionError("publication replayed functional verification")

    monkeypatch.setattr(loom_checker, "check_probes_package_tests", forbidden)
    monkeypatch.setattr(loom_checker, "check_probes_adversarial", forbidden)
    monkeypatch.chdir(repo)
    assert loom_checker._cmd_push([]) == 0
    assert functional_head
