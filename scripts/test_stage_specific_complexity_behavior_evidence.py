"""Require reproducible baseline/candidate evidence for complexity behavior."""

import io
import re
import runpy
import subprocess
import tarfile
import tempfile
from pathlib import Path

import pytest


REPORT = Path(__file__).parents[1] / "docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md"
ROOT = Path(__file__).parents[1]
FINGERPRINT = runpy.run_path(
    str(ROOT / "loom-code/scripts/loom_firing_harness.py")
)["_plugin_tree_fingerprint"]
BASELINE_COMMIT = "0a7dcde2"
REQUIRED_LENS_EVIDENCE = {
    "business-complexity-lens": "live hard case",
    "visual-complexity-lens": "live hard case",
    "interaction-complexity-lens": "live hard case",
    "behavioral-complexity-lens": "contract test",
    "architecture-complexity-lens": "live hard case",
    "implementation-complexity-lens": "contract test",
}


def _materialize_tracked_file(source: Path, target: Path, git_mode: str) -> None:
    if git_mode == "120000" or source.is_symlink():
        raise AssertionError(f"tracked symlink is not package-safe: {source}")
    if git_mode not in {"100644", "100755"} or not source.is_file():
        raise AssertionError(f"unsupported tracked package entry: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())
    target.chmod(0o755 if git_mode == "100755" else 0o644)


def _normalize_tree_modes(root: Path) -> None:
    root.chmod(0o755)
    for path in root.rglob("*"):
        if path.is_dir():
            path.chmod(0o755)


def _archive_fingerprint(plugin: str, revision: str) -> str:
    archive = subprocess.check_output(
        ["git", "-C", str(ROOT), "archive", "--format=tar", revision, plugin]
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        destination = Path(temp_dir)
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
            for member in bundle.getmembers():
                target = (destination / member.name).resolve()
                if not target.is_relative_to(destination.resolve()):
                    raise AssertionError(f"unsafe archive member: {member.name}")
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source = bundle.extractfile(member)
                    if source is None:
                        raise AssertionError(f"unreadable archive member: {member.name}")
                    target.write_bytes(source.read())
                    target.chmod(0o755 if member.mode & 0o111 else 0o644)
                else:
                    raise AssertionError(f"unsupported archive member: {member.name}")
        _normalize_tree_modes(destination / plugin)
        return FINGERPRINT(destination / plugin)


def _tracked_worktree_fingerprint(plugin: str) -> str:
    tracked = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "--stage", "-z", "--", plugin]
    ).decode().split("\0")
    with tempfile.TemporaryDirectory() as temp_dir:
        destination = Path(temp_dir) / plugin
        for record in filter(None, tracked):
            metadata, relative = record.split("\t", 1)
            git_mode = metadata.split(" ", 1)[0]
            source = ROOT / relative
            target = Path(temp_dir) / relative
            _materialize_tracked_file(source, target, git_mode)
        _normalize_tree_modes(destination)
        return FINGERPRINT(destination)


def test_report_binds_baseline_and_final_candidate():
    """Bind reported bytes to reconstructible Git inputs.

    Grounding (live CLI help, 2026-08-27): `git archive -h` documents
    `--format <fmt>`, `<tree-ish>`, and optional paths; `git ls-files -h`
    documents `--stage`, `-z`, and path arguments. Those are the exact Git
    surfaces used by the reconstruction helpers above.
    """
    text = REPORT.read_text(encoding="utf-8")
    flat_text = " ".join(text.split())
    assert "immutable pre-edit snapshot" in text
    assert "base commit `0a7dcde2`" in text
    assert "final cold-install candidate bytes" in text
    for plugin in ("loom-design", "loom-code"):
        baseline_match = re.search(
            rf"{plugin} baseline SHA-256: `([0-9a-f]{{64}})`", text
        )
        assert baseline_match, f"report must record a full {plugin} baseline fingerprint"
        assert baseline_match.group(1) == _archive_fingerprint(plugin, BASELINE_COMMIT)
        assert f"{plugin} candidate SHA-256" in text
        match = re.search(rf"{plugin} candidate SHA-256: `([0-9a-f]{{64}})`", text)
        assert match, f"report must record a full {plugin} candidate fingerprint"
        assert match.group(1) == _tracked_worktree_fingerprint(plugin)
    for case in ("no-upstream", "misleading-upstream", "trivial-exempt", "over-complex"):
        assert f"`{case}`" in text
    coverage_rows = dict(
        re.findall(r"^\| `([^`]+-complexity-lens)` \| ([^|]+?) \| PASS \|$", text, re.MULTILINE)
    )
    assert coverage_rows == REQUIRED_LENS_EVIDENCE
    assert "purpose preservation" in flat_text.lower()
    assert "scope trade-off" in flat_text.lower()
    assert "Pre-existing invariant result: PASS" in text


def test_tracked_copy_rejects_symlinks(tmp_path):
    real_file = tmp_path / "real.txt"
    real_file.write_text("payload", encoding="utf-8")
    symlink = tmp_path / "link.txt"
    symlink.symlink_to(real_file)

    with pytest.raises(AssertionError, match="symlink"):
        _materialize_tracked_file(symlink, tmp_path / "copy.txt", "120000")


def test_fingerprint_directory_modes_are_umask_independent(tmp_path):
    nested = tmp_path / "plugin" / "skills" / "demo"
    nested.mkdir(parents=True)
    for directory in (tmp_path / "plugin", tmp_path / "plugin/skills", nested):
        directory.chmod(0o700)

    _normalize_tree_modes(tmp_path / "plugin")

    for directory in (tmp_path / "plugin", tmp_path / "plugin/skills", nested):
        assert directory.stat().st_mode & 0o777 == 0o755
