#!/usr/bin/env python3
"""Atomically write one validated live-gate station receipt under ``.git/loom``."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import stat
import subprocess
import sys
from pathlib import Path

from review_context import RESOURCE_RELATIVE_PATHS


PACKET_KEYS = {"target_repo", "reviewed_sha", "plugin_version", "resources"}
STATIONS = {"CODE", "DOCS", "MIXED", "SDD"}
NONCE_PATTERN = re.compile(r"[0-9a-f]{32}")


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return result.stdout.strip()


def _validated_packet(packet_path: Path, plugin_root: Path, repo: Path) -> dict[str, object]:
    if packet_path.is_symlink() or not packet_path.is_file():
        raise ValueError("packet schema: packet must be a regular non-symlink file")
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    if not isinstance(packet, dict) or set(packet) != PACKET_KEYS:
        raise ValueError("packet schema: expected exactly four canonical fields")

    target_repo = packet.get("target_repo")
    reviewed_sha = packet.get("reviewed_sha")
    plugin_version = packet.get("plugin_version")
    resources = packet.get("resources")
    if target_repo != str(repo) or not isinstance(plugin_version, str) or not plugin_version:
        raise ValueError("packet schema: target or plugin version field is invalid")
    if not isinstance(reviewed_sha, str):
        raise ValueError("packet SHA: reviewed_sha must be a string")

    object_format = _git(repo, "rev-parse", "--show-object-format")
    expected_length = {"sha1": 40, "sha256": 64}.get(object_format)
    if (
        expected_length is None
        or len(reviewed_sha) != expected_length
        or re.fullmatch(r"[0-9a-f]+", reviewed_sha) is None
        or _git(repo, "rev-parse", "HEAD") != reviewed_sha
    ):
        raise ValueError("packet SHA: reviewed_sha is not the fixture HEAD")

    try:
        manifest = json.loads(
            (plugin_root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("packet version: candidate manifest is unavailable") from error
    if manifest.get("version") != plugin_version:
        raise ValueError("packet version: plugin_version does not match candidate")

    if not isinstance(resources, dict) or set(resources) != set(RESOURCE_RELATIVE_PATHS):
        raise ValueError("packet resources: resource key set is incomplete")
    for name, relative in RESOURCE_RELATIVE_PATHS.items():
        value = resources.get(name)
        expected = (plugin_root / relative).resolve()
        if (
            not isinstance(value, str)
            or not Path(value).is_absolute()
            or Path(value) != expected
            or not expected.is_file()
            or not expected.is_relative_to(plugin_root)
        ):
            raise ValueError(f"packet resources: {name} does not match candidate")
    return packet


def _open_marker_directory(marker: Path, repo: Path) -> int:
    expected = repo / ".git" / "loom"
    lexical = Path(os.path.abspath(os.fspath(marker)))
    if lexical != expected:
        raise ValueError("unsafe marker: destination is not target .git/loom")
    if expected.is_symlink() or expected.parent.is_symlink():
        raise ValueError("unsafe marker: symlink directory")
    if not expected.is_dir() or not stat.S_ISDIR(expected.lstat().st_mode):
        raise ValueError("unsafe marker: destination is not a directory")
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return os.open(expected, flags)


def _atomic_create(directory_fd: int, final_name: str, payload: bytes) -> None:
    temporary_name = f".{final_name}.{os.getpid()}.{secrets.token_hex(8)}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    temporary_fd: int | None = None
    linked = False
    try:
        temporary_fd = os.open(temporary_name, flags, 0o600, dir_fd=directory_fd)
        view = memoryview(payload)
        while view:
            written = os.write(temporary_fd, view)
            if written <= 0:
                raise OSError("short receipt write")
            view = view[written:]
        os.fsync(temporary_fd)
        os.close(temporary_fd)
        temporary_fd = None
        os.link(
            temporary_name,
            final_name,
            src_dir_fd=directory_fd,
            dst_dir_fd=directory_fd,
            follow_symlinks=False,
        )
        linked = True
        os.fsync(directory_fd)
    finally:
        if temporary_fd is not None:
            os.close(temporary_fd)
        try:
            os.unlink(temporary_name, dir_fd=directory_fd)
        except FileNotFoundError:
            pass
        if linked:
            os.fsync(directory_fd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--plugin-root", type=Path, required=True)
    parser.add_argument("--marker-dir", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--station", required=True)
    parser.add_argument("--nonce", required=True)
    args = parser.parse_args(argv)

    directory_fd: int | None = None
    try:
        plugin_root = args.plugin_root.resolve(strict=True)
        script_root = Path(__file__).resolve().parents[1]
        repo = args.repo.resolve(strict=True)
        if plugin_root != script_root:
            raise ValueError("plugin root does not own this receipt script")
        if not repo.is_dir():
            raise ValueError("target repo is not a directory")
        if args.station not in STATIONS:
            raise ValueError("station is not recognized")
        if NONCE_PATTERN.fullmatch(args.nonce) is None:
            raise ValueError("unsafe marker nonce")

        packet = _validated_packet(args.packet, plugin_root, repo)
        canonical_packet = (
            json.dumps(packet, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("utf-8")
        receipt = {
            "nonce": args.nonce,
            "packet_sha256": hashlib.sha256(canonical_packet).hexdigest(),
            "plugin_root": str(plugin_root),
            "reviewed_sha": packet["reviewed_sha"],
            "station": args.station,
            "target_repo": str(repo),
        }
        payload = (json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )
        directory_fd = _open_marker_directory(args.marker_dir, repo)
        _atomic_create(directory_fd, f"{args.station}-{args.nonce}.json", payload)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(f"receipt: refused: {error}", file=sys.stderr)
        return 1
    finally:
        if directory_fd is not None:
            os.close(directory_fd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
