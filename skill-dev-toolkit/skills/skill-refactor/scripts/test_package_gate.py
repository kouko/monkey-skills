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
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["resolved_commit"] == commit
    assert manifest["skill_tree"] == _git(repo, "rev-parse", f"{commit}:skills/demo")
    assert manifest["files"] == {
        "SKILL.md": hashlib.sha256(b"---\nname: demo\n---\n\nOriginal\n").hexdigest(),
        "resource.txt": hashlib.sha256(b"immutable resource\n").hexdigest(),
    }

    exported_file = manifest_path.parent / "skill" / "SKILL.md"
    exported_file.write_bytes(b"drifted bytes\n")

    result = verify_baseline(manifest_path)

    assert result["verdict"] == "REFUSED"
    assert "drift" in result["reason"]
    assert exported_file.read_bytes() == b"drifted bytes\n"


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

    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "SKILL.md").write_bytes(b"keep ")
    (candidate / "reference.md").write_bytes(b"moved words\n")

    result = account_package(manifest_path, candidate, "SKILL.md")

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

    assert account_package(manifest_path, candidate, "SKILL.md") == {
        "verdict": "REFUSED",
        "reason": "baseline drift detected",
    }
