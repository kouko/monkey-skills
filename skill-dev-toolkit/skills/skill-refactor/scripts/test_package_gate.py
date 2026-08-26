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
