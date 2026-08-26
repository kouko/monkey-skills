import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ("git", "-C", str(repo), *args),
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _manifest_sha256(manifest_path: Path) -> str:
    return hashlib.sha256(manifest_path.read_bytes()).hexdigest()


def test_exported_baseline_is_revision_bound_and_drift_refuses(tmp_path: Path) -> None:
    """Ground the Git surfaces used by export_baseline.

    This session verified `git rev-parse -h`, `git cat-file -h`, and
    `git archive -h`; their durable references are
    https://git-scm.com/docs/git-rev-parse,
    https://git-scm.com/docs/git-cat-file, and
    https://git-scm.com/docs/git-archive.
    """
    from package_gate import export_baseline, verify_baseline

    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_bytes(b"---\nname: demo\n---\n\nOriginal\n")
    (skill_dir / "resource.txt").write_bytes(b"immutable resource\n")
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "baseline")
    commit = _git(repo, "rev-parse", "HEAD")

    manifest_path = export_baseline(repo, tmp_path / "workspace", "skills/demo", commit)
    manifest_sha256 = _manifest_sha256(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["resolved_commit"] == commit
    assert manifest["skill_tree"] == _git(repo, "rev-parse", f"{commit}:skills/demo")
    assert manifest["files"] == {
        "SKILL.md": {
            "sha256": hashlib.sha256(b"---\nname: demo\n---\n\nOriginal\n").hexdigest(),
            "executable": False,
        },
        "resource.txt": {
            "sha256": hashlib.sha256(b"immutable resource\n").hexdigest(),
            "executable": False,
        },
    }

    exported_file = manifest_path.parent / "skill" / "SKILL.md"
    exported_file.write_bytes(b"drifted bytes\n")

    result = verify_baseline(manifest_path, manifest_sha256)

    assert result["verdict"] == "REFUSED"
    assert "drift" in result["reason"]
    assert exported_file.read_bytes() == b"drifted bytes\n"


def test_baseline_fingerprint_includes_executable_mode(tmp_path: Path) -> None:
    from package_gate import export_baseline, verify_baseline

    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("skill\n", encoding="utf-8")
    executable = skill_dir / "run.sh"
    executable.write_bytes(b"#!/bin/sh\n")
    executable.chmod(0o755)
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "baseline")

    manifest_path = export_baseline(repo, tmp_path / "workspace", "skills/demo", "HEAD")
    manifest_sha256 = _manifest_sha256(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["files"]["run.sh"] == {
        "sha256": hashlib.sha256(b"#!/bin/sh\n").hexdigest(),
        "executable": True,
    }

    (manifest_path.parent / "skill" / "run.sh").chmod(0o644)

    assert verify_baseline(manifest_path, manifest_sha256)["verdict"] == "REFUSED"


def test_baseline_verification_reanchors_a_mutated_manifest_to_git(tmp_path: Path) -> None:
    from package_gate import export_baseline, verify_baseline

    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    original = b"---\nname: demo\n---\n\nOriginal\n"
    (skill_dir / "SKILL.md").write_bytes(original)
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "baseline")
    manifest_path = export_baseline(repo, tmp_path / "workspace", "skills/demo", "HEAD")
    manifest_sha256 = _manifest_sha256(manifest_path)

    drifted = b"---\nname: demo\n---\n\nDrifted\n"
    (manifest_path.parent / "skill" / "SKILL.md").write_bytes(drifted)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"]["SKILL.md"]["sha256"] = hashlib.sha256(drifted).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = verify_baseline(manifest_path, manifest_sha256)

    assert result["verdict"] == "REFUSED"
    assert "manifest digest" in result["reason"]


def test_baseline_verification_refuses_full_provenance_repoint(tmp_path: Path) -> None:
    from package_gate import export_baseline, verify_baseline

    original_repo = tmp_path / "original-repo"
    original_skill = original_repo / "skills" / "demo"
    original_skill.mkdir(parents=True)
    (original_skill / "SKILL.md").write_text("original\n", encoding="utf-8")
    _git(original_repo, "init", "-q")
    _git(original_repo, "add", ".")
    _git(original_repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "original")
    manifest_path = export_baseline(
        original_repo, tmp_path / "workspace", "skills/demo", "HEAD"
    )
    manifest_sha256 = _manifest_sha256(manifest_path)

    replacement_repo = tmp_path / "replacement-repo"
    replacement_skill = replacement_repo / "skills" / "demo"
    replacement_skill.mkdir(parents=True)
    replacement_bytes = b"replacement\n"
    (replacement_skill / "SKILL.md").write_bytes(replacement_bytes)
    _git(replacement_repo, "init", "-q")
    _git(replacement_repo, "add", ".")
    _git(replacement_repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "replacement")
    replacement_commit = _git(replacement_repo, "rev-parse", "HEAD")

    (manifest_path.parent / "skill" / "SKILL.md").write_bytes(replacement_bytes)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        repository=str(replacement_repo.resolve()),
        resolved_commit=replacement_commit,
        skill_tree=_git(
            replacement_repo, "rev-parse", f"{replacement_commit}:skills/demo"
        ),
    )
    manifest["files"]["SKILL.md"]["sha256"] = hashlib.sha256(
        replacement_bytes
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert verify_baseline(manifest_path, manifest_sha256) == {
        "verdict": "REFUSED",
        "reason": "manifest digest mismatch",
    }


def test_baseline_verification_refuses_manifest_path_alias(tmp_path: Path) -> None:
    from package_gate import export_baseline, verify_baseline

    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("original\n", encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "baseline")
    manifest_path = export_baseline(repo, tmp_path / "workspace", "skills/demo", "HEAD")
    manifest_sha256 = _manifest_sha256(manifest_path)

    alias = tmp_path / "manifest-alias.json"
    alias.symlink_to(manifest_path)

    assert verify_baseline(alias, manifest_sha256) == {
        "verdict": "REFUSED",
        "reason": "manifest path is not canonical",
    }


def test_accounting_uses_the_verified_baseline_snapshot(
    tmp_path: Path, monkeypatch
) -> None:
    import package_gate

    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("one two\n", encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "baseline")
    manifest_path = package_gate.export_baseline(
        repo, tmp_path / "workspace", "skills/demo", "HEAD"
    )
    manifest_sha256 = _manifest_sha256(manifest_path)
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "SKILL.md").write_text("one\n", encoding="utf-8")

    original_verify = package_gate.verify_baseline

    def mutate_after_verification(path: Path, digest: str):
        verdict = original_verify(path, digest)
        (path.parent / "skill" / "SKILL.md").write_text(
            "attacker controlled baseline words\n", encoding="utf-8"
        )
        return verdict

    monkeypatch.setattr(package_gate, "verify_baseline", mutate_after_verification)

    result = package_gate.account_package(
        manifest_path, manifest_sha256, candidate, "SKILL.md"
    )

    assert result["verdict"] == "PASS"
    assert result["package"]["words"]["baseline"] == 2


def test_accounting_counts_moved_words_in_package_total(tmp_path: Path) -> None:
    from package_gate import account_package, export_baseline

    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_bytes(b"keep moved words\n")
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "baseline")
    manifest_path = export_baseline(repo, tmp_path / "workspace", "skills/demo", "HEAD")
    manifest_sha256 = _manifest_sha256(manifest_path)

    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "SKILL.md").write_bytes(b"keep ")
    (candidate / "reference.md").write_bytes(b"moved words\n")

    result = account_package(manifest_path, manifest_sha256, candidate, "SKILL.md")

    assert result == {
        "verdict": "PASS",
        "target": {
            "words": {"baseline": 3, "candidate": 1, "delta": -2},
            "bytes": {"baseline": 17, "candidate": 5, "delta": -12},
        },
        "package": {
            "words": {"baseline": 3, "candidate": 3, "delta": 0},
            "bytes": {"baseline": 17, "candidate": 17, "delta": 0},
        },
    }

    (manifest_path.parent / "skill" / "SKILL.md").write_bytes(b"drifted\n")

    assert account_package(manifest_path, manifest_sha256, candidate, "SKILL.md") == {
        "verdict": "REFUSED",
        "reason": "baseline drift detected",
    }


def test_accounting_refuses_candidate_executable_mode_drift(tmp_path: Path) -> None:
    from package_gate import account_package, export_baseline

    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("skill\n", encoding="utf-8")
    executable = skill_dir / "run.sh"
    executable.write_bytes(b"#!/bin/sh\n")
    executable.chmod(0o755)
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "baseline")
    manifest_path = export_baseline(repo, tmp_path / "workspace", "skills/demo", "HEAD")
    manifest_sha256 = _manifest_sha256(manifest_path)

    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "SKILL.md").write_text("skill\n", encoding="utf-8")
    candidate_script = candidate / "run.sh"
    candidate_script.write_bytes(b"#!/bin/sh\n")
    candidate_script.chmod(0o644)

    assert account_package(manifest_path, manifest_sha256, candidate, "SKILL.md") == {
        "verdict": "REFUSED",
        "reason": "candidate executable mode drift detected: run.sh",
    }


def test_dual_host_error_is_ungradeable_and_blocks_package_pass() -> None:
    """A host failure is missing behavioral evidence, never a passing replay."""
    from package_gate import reduce_package_evidence

    accounting = {
        "verdict": "PASS",
        "target": {"words": {"baseline": 10, "candidate": 8, "delta": -2}},
        "package": {"words": {"baseline": 20, "candidate": 18, "delta": -2}},
    }
    result = reduce_package_evidence(
        {
            "resource": [{"verdict": "PASS"}],
            "owning-skill": [{"verdict": "PASS"}],
            "package": [{"verdict": "PASS"}],
            "host_evidence": [
                {"host": "claude", "replicate": 0, "verdict": "PASS"},
                {"host": "claude", "replicate": 1, "verdict": "PASS"},
                {"host": "codex", "replicate": 0, "verdict": "PASS"},
                {"host": "codex", "replicate": 1, "error": "host exited with status 1"},
            ],
            "accounting": accounting,
        },
        dual_host=True,
    )

    assert result["verdict"] == "UNGRADABLE"
    assert [layer["layer"] for layer in result["layers"]] == [
        "resource",
        "owning-skill",
        "package",
    ]
    assert result["layers"][-1]["accounting"] == accounting
    assert result["host_evidence"][-1]["verdict"] == "UNGRADABLE"


def test_cli_drives_export_verify_and_account(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("original words\n", encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "baseline")

    script = SCRIPTS_DIR / "package_gate.py"
    export = subprocess.run(
        [
            sys.executable, str(script), "export", "--repo", str(repo),
            "--workspace", str(tmp_path / "workspace"), "--skill-path", "skills/demo",
            "--revision", "HEAD",
        ],
        check=True, capture_output=True, text=True,
    )
    export_result = json.loads(export.stdout)
    manifest = Path(export_result["manifest"])
    manifest_sha256 = export_result["manifest_sha256"]

    verify = subprocess.run(
        [
            sys.executable, str(script), "verify", "--manifest", str(manifest),
            "--manifest-sha256", manifest_sha256,
        ],
        check=True, capture_output=True, text=True,
    )
    assert json.loads(verify.stdout)["verdict"] == "PASS"

    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "SKILL.md").write_text("smaller\n", encoding="utf-8")
    account = subprocess.run(
        [
            sys.executable, str(script), "account", "--manifest", str(manifest),
            "--manifest-sha256", manifest_sha256,
            "--candidate-root", str(candidate), "--target-file", "SKILL.md",
        ],
        check=True, capture_output=True, text=True,
    )
    assert json.loads(account.stdout)["package"]["words"]["delta"] == -1
