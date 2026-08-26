#!/usr/bin/env python3
"""Freeze and verify a skill-package baseline exported from Git."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ("git", "-C", str(repo), *args),
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _resolved_commit(repo: Path, revision: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(repo), "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"),
        check=False,
        capture_output=True,
        text=True,
    )
    commit = result.stdout.strip()
    if result.returncode or len(commit) != 40:
        raise ValueError(f"invalid Git revision: {revision}")
    return commit


def _skill_path(skill_path: str) -> PurePosixPath:
    path = PurePosixPath(skill_path)
    if path.is_absolute() or not skill_path or ".." in path.parts:
        raise ValueError(f"invalid skill path: {skill_path}")
    return path


def _file_hashes(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"baseline contains symlink: {path.relative_to(root)}")
        if path.is_file():
            files[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def _extract_skill(archive: bytes, destination: Path) -> None:
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        members = tar.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                raise ValueError(f"unsafe baseline archive member: {member.name}")
            if not (member.isdir() or member.isfile()):
                raise ValueError(f"unsupported baseline archive member: {member.name}")
        tar.extractall(destination, members=members, filter="data")


def export_baseline(repo: Path, workspace: Path, skill_path: str, revision: str) -> Path:
    """Export one skill from *revision* and return its immutable manifest path."""
    relative_path = _skill_path(skill_path)
    commit = _resolved_commit(repo, revision)
    tree = _git(repo, "rev-parse", f"{commit}:{relative_path.as_posix()}")
    _git(repo, "cat-file", "-e", f"{commit}:{relative_path.as_posix()}/SKILL.md")

    baseline = workspace / "baseline"
    manifest_path = baseline / "manifest.json"
    skill_root = baseline / "skill"
    if manifest_path.exists() or skill_root.exists():
        raise ValueError("baseline already exists; refusing to replace it")

    archive = subprocess.run(
        ("git", "-C", str(repo), "archive", "--format=tar", f"{commit}:{relative_path.as_posix()}"),
        check=True,
        capture_output=True,
    ).stdout
    baseline.mkdir(parents=True)
    try:
        _extract_skill(archive, skill_root)
        manifest = {
            "resolved_commit": commit,
            "skill_tree": tree,
            "files": _file_hashes(skill_root),
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except Exception:
        if skill_root.exists():
            for path in sorted(skill_root.rglob("*"), reverse=True):
                if path.is_file() or path.is_symlink():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            skill_root.rmdir()
        raise
    return manifest_path


def verify_baseline(manifest_path: Path) -> dict[str, str]:
    """Return PASS when exported bytes match the manifest, otherwise REFUSED."""
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = manifest["files"]
        if not isinstance(expected, dict) or not all(
            isinstance(path, str) and isinstance(digest, str)
            for path, digest in expected.items()
        ):
            raise ValueError("invalid file fingerprint manifest")
        actual = _file_hashes(manifest_path.parent / "skill")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {"verdict": "REFUSED", "reason": f"baseline verification failed: {error}"}

    if actual != expected:
        return {"verdict": "REFUSED", "reason": "baseline drift detected"}
    return {"verdict": "PASS", "reason": "baseline matches manifest"}
