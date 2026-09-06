"""Branch-end adversarial probes for the second, squashed rehearsal shape."""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[5]
SCRIPT = ROOT / "loom-code/scripts/rehearse_probes.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("rehearse_under_attack", SCRIPT)
assert SPEC and SPEC.loader
REHEARSE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REHEARSE)


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def make_repo(tmp_path: Path, name: str = "repo") -> Path:
    repo = tmp_path / name
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "core.autocrlf", "false")
    git(repo, "config", "user.name", "Branch End Adversary")
    git(repo, "config", "user.email", "adversary@example.invalid")
    (repo / "seed.txt").write_text("base\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "base")
    git(repo, "switch", "-q", "-c", "feature")
    return repo


def add_probe(repo: Path, rel: str, body: str = "def test_probe():\n    assert True\n") -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    git(repo, "add", rel)
    git(repo, "commit", "-q", "-m", f"add {rel}")


def run(repo: Path, rel: str, *extra: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), rel, "--repo", str(repo), *extra],
        capture_output=True, text=True, env=env, timeout=120,
    )


def test_rehearsal_detachedhead_runsboth(tmp_path: Path) -> None:
    """A detached source HEAD must still run both rehearsal shapes."""
    repo = make_repo(tmp_path)
    add_probe(repo, "tests/test_probe.py")
    git(repo, "checkout", "-q", "--detach", "HEAD")
    result = run(repo, "tests/test_probe.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SQUASHED SHAPE" in result.stdout


def test_rehearsal_tagtrunk_resolvescommit(tmp_path: Path) -> None:
    """A trunk candidate stored as an annotated tag object must still squash successfully."""
    repo = make_repo(tmp_path)
    base = git(repo, "rev-parse", "main")
    git(repo, "tag", "-a", "trunk-tag", base, "-m", "trunk")
    git(repo, "update-ref", "refs/remotes/origin/main", "refs/tags/trunk-tag")
    add_probe(repo, "tests/test_probe.py")
    result = run(repo, "tests/test_probe.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SQUASHED SHAPE" in result.stdout


def test_rehearsal_symbolictrunk_resolvescommit(tmp_path: Path) -> None:
    """A symbolic origin/main must resolve to the branch commit it names."""
    repo = make_repo(tmp_path)
    git(repo, "symbolic-ref", "refs/remotes/origin/main", "refs/heads/main")
    sha, ref = REHEARSE._resolve_trunk_sha(repo)
    assert sha == git(repo, "rev-parse", "main")
    assert ref == "origin/main"


def test_rehearsal_trunkbehindmergebase_failsloudly(tmp_path: Path) -> None:
    """An origin/main behind the true merge-base must not silently claim a faithful squash."""
    repo = make_repo(tmp_path)
    base = git(repo, "rev-parse", "main")
    git(repo, "checkout", "-q", "main")
    (repo / "later.txt").write_text("later\n", encoding="utf-8")
    git(repo, "add", "later.txt")
    git(repo, "commit", "-q", "-m", "advance main")
    advanced = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "feature")
    git(repo, "merge", "-q", "--no-edit", advanced)
    add_probe(repo, "tests/test_probe.py")
    git(repo, "update-ref", "refs/remotes/origin/main", base)
    result = run(repo, "tests/test_probe.py")
    assert result.returncode != 0
    assert "could not squash" in result.stdout.lower() or "ancestor" in (result.stdout + result.stderr).lower()


def test_rehearsal_trunkaheadofbranch_failsloudly(tmp_path: Path) -> None:
    """An origin/main ahead of and divergent from the branch must fail rather than fabricate a squash."""
    repo = make_repo(tmp_path)
    git(repo, "checkout", "-q", "main")
    (repo / "ahead.txt").write_text("ahead\n", encoding="utf-8")
    git(repo, "add", "ahead.txt")
    git(repo, "commit", "-q", "-m", "advance trunk")
    ahead = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "feature")
    add_probe(repo, "tests/test_probe.py")
    git(repo, "update-ref", "refs/remotes/origin/main", ahead)
    result = run(repo, "tests/test_probe.py")
    assert result.returncode != 0
    assert "could not squash" in result.stdout.lower()


def test_rehearsal_mergehistory_collapsesonecommit(tmp_path: Path) -> None:
    """Non-linear feature history must rehearse successfully as one commit on trunk."""
    repo = make_repo(tmp_path)
    git(repo, "switch", "-q", "-c", "topic")
    (repo / "topic.txt").write_text("topic\n", encoding="utf-8")
    git(repo, "add", "topic.txt")
    git(repo, "commit", "-q", "-m", "topic")
    git(repo, "switch", "-q", "feature")
    git(repo, "merge", "-q", "--no-ff", "topic", "-m", "merge topic")
    add_probe(repo, "tests/test_probe.py")
    result = run(repo, "tests/test_probe.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SQUASHED SHAPE" in result.stdout


def test_rehearsal_unicodepath_runsboth(tmp_path: Path) -> None:
    """A probe path containing spaces and non-ASCII characters must run in both shapes."""
    repo = make_repo(tmp_path, "來源 repo")
    rel = "tests/有 空格/test_探針.py"
    add_probe(repo, rel)
    result = run(repo, rel)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.count("FAILED (0)") == 2


def test_rehearsal_dirtysource_ignoresworktree(tmp_path: Path) -> None:
    """Dirty source edits must not leak into either clone-backed shape."""
    repo = make_repo(tmp_path)
    rel = "tests/test_probe.py"
    add_probe(repo, rel)
    (repo / rel).write_text("def test_probe():\n    assert False, 'dirty leak'\n", encoding="utf-8")
    result = run(repo, rel)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "dirty leak" not in result.stdout + result.stderr


def test_rehearsal_unwritabletmp_failsloudly(tmp_path: Path) -> None:
    """An unusable TMPDIR must safely fall back and still run the second shape."""
    repo = make_repo(tmp_path)
    add_probe(repo, "tests/test_probe.py")
    env = os.environ.copy()
    env["TMPDIR"] = str(tmp_path / "missing" / "nested")
    env["TMP"] = env["TMPDIR"]
    env["TEMP"] = env["TMPDIR"]
    result = run(repo, "tests/test_probe.py", env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SQUASHED SHAPE" in result.stdout


def test_rehearsal_unsettmp_runsboth(tmp_path: Path) -> None:
    """With every TMPDIR-style variable unset, the platform default must run both shapes."""
    repo = make_repo(tmp_path)
    add_probe(repo, "tests/test_probe.py")
    env = os.environ.copy()
    for name in ("TMPDIR", "TMP", "TEMP"):
        env.pop(name, None)
    result = run(repo, "tests/test_probe.py", env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SQUASHED SHAPE" in result.stdout


def test_rehearsal_keep_preservessquashedclone(tmp_path: Path) -> None:
    """The --keep path must preserve the clone after the second shape has replaced HEAD."""
    repo = make_repo(tmp_path)
    add_probe(repo, "tests/test_probe.py")
    result = run(repo, "tests/test_probe.py", "--keep")
    assert result.returncode == 0, result.stdout + result.stderr
    kept = Path(result.stdout.rsplit("kept the rehearsal clone at: ", 1)[1].splitlines()[0])
    try:
        assert kept.is_dir()
        assert git(kept, "log", "-1", "--format=%s") == "squashed shape (rehearse_probes.py)"
    finally:
        shutil.rmtree(kept)


def test_rehearsal_callermarkers_overwritten(tmp_path: Path) -> None:
    """Caller-supplied marker values must be replaced with the actual clone and shape."""
    repo = make_repo(tmp_path)
    rel = "tests/test_markers.py"
    add_probe(repo, rel, "import os\ndef test_markers():\n    assert os.environ['REHEARSE_PROBES_NESTED'] != 'caller'\n    assert os.environ['REHEARSE_PROBES_SHAPE'] in {'ci-shaped', 'squashed'}\n")
    env = {**os.environ, "REHEARSE_PROBES_NESTED": "caller", "REHEARSE_PROBES_SHAPE": "caller"}
    result = run(repo, rel, env=env)
    assert result.returncode == 0, result.stdout + result.stderr


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
