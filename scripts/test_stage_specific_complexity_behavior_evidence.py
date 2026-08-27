"""Require reproducible baseline/candidate evidence for complexity behavior."""

import hashlib
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
# The last commit whose instruction surface the live hard cases actually
# observed. Round-4 review fixes landed after it, so the report must either
# match it or enumerate the delta (see test below).
HARD_CASE_COMMIT = "7af88b7053c2076b65b98b69217ff32239ab80f8"
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


def _behavior_paths_at(revision: str, plugin: str) -> list[str]:
    listing = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", "-z", revision,
         f"{plugin}/skills", f"{plugin}/agents"]
    ).decode().split("\0")
    return sorted(
        relative
        for relative in filter(None, listing)
        if relative.endswith(".md")
        and not Path(relative).name.startswith(("README", "CHANGELOG"))
    )


def _behavior_fingerprint_at(revision: str, plugin: str) -> str:
    digest = hashlib.sha256()
    for relative in _behavior_paths_at(revision, plugin):
        blob = subprocess.check_output(
            ["git", "-C", str(ROOT), "show", f"{revision}:{relative}"]
        )
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(blob)
        digest.update(b"\0")
    return digest.hexdigest()


def _instruction_surface_delta() -> list[str]:
    """Behaviour-bearing paths that differ between the hard-case commit and now."""
    changed = subprocess.check_output(
        ["git", "-C", str(ROOT), "diff", "--name-only", HARD_CASE_COMMIT, "--",
         "loom-code/skills", "loom-code/agents",
         "loom-design/skills", "loom-design/agents"]
    ).decode().splitlines()
    return sorted(
        relative
        for relative in changed
        if relative.endswith(".md")
        and not Path(relative).name.startswith(("README", "CHANGELOG"))
    )


def test_report_enumerates_any_post_hard_case_instruction_change():
    """A changed instruction surface must be enumerated, never re-hashed away.

    The candidate fingerprint moves for a version bump, so matching it proves
    nothing about behaviour. This test binds the report to the instruction
    bytes the hard cases actually observed: either nothing has moved since, or
    the report names every file that did — and the list is checked against git,
    so recomputing a hash cannot satisfy it.
    """
    text = REPORT.read_text(encoding="utf-8")
    for plugin in ("loom-design", "loom-code"):
        match = re.search(rf"{plugin} hard-case behavior SHA-256: `([0-9a-f]{{64}})`", text)
        assert match, (
            f"report must record the {plugin} instruction-surface fingerprint the "
            "hard cases ran against"
        )
        assert match.group(1) == _behavior_fingerprint_at(HARD_CASE_COMMIT, plugin)

    delta = _instruction_surface_delta()
    if not delta:
        return
    assert "## Instruction-surface changes after the hard cases" in text, (
        "the instruction surface moved after the hard cases ran; the report must "
        "carry the delta section rather than restate the old results as current"
    )
    for relative in delta:
        assert relative in text, (
            f"{relative} changed after the hard cases ran and is not named in the "
            "report's delta section"
        )


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
