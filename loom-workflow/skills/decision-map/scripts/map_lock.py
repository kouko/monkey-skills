#!/usr/bin/env python3
"""Descriptor-safe Map-local serialization shared by all store writers."""

from __future__ import annotations

import errno
import os
import stat
from contextlib import contextmanager
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - exercised only on unsupported hosts
    fcntl = None


class MapLockError(RuntimeError):
    """The host cannot safely establish or verify the Map writer lock."""


def _before_lock_file_open() -> None:
    """Test seam after opening the lock directory by descriptor."""


def assert_no_symlink_components(
    path: Path, error: type[Exception] = MapLockError
) -> None:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            raise error(f"refusing path with symlink component: {current}")
        if not current.exists():
            break


def _assert_no_symlink_components(path: Path) -> None:
    assert_no_symlink_components(path)


def _assert_contained(map_dir: Path, candidate: Path) -> None:
    try:
        candidate.resolve(strict=False).relative_to(map_dir.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise MapLockError(f"path escapes the map directory: {candidate}") from exc


def _open_lock_file(directory_fd: int) -> int:
    flags = os.O_RDWR | os.O_NOFOLLOW
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    for _ in range(3):
        try:
            return os.open(".map.lock", flags, dir_fd=directory_fd)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise
        try:
            return os.open(
                ".map.lock",
                flags | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=directory_fd,
            )
        except FileExistsError:
            continue
    raise OSError(errno.EAGAIN, "transaction lock creation did not stabilize")


def _prepare_lock_directory(map_dir: Path) -> Path:
    transactions = map_dir / ".transactions"
    lock_path = transactions / ".map.lock"
    _assert_no_symlink_components(map_dir)
    try:
        if not stat.S_ISDIR(map_dir.lstat().st_mode):
            raise MapLockError(f"transaction lock Map is not a directory: {map_dir}")
        transactions.mkdir(mode=0o700, exist_ok=True)
        if not stat.S_ISDIR(transactions.lstat().st_mode):
            raise MapLockError(
                f"transaction lock directory is not regular: {transactions}"
            )
    except OSError as exc:
        raise MapLockError(f"cannot prepare transaction lock: {exc}") from exc
    _assert_no_symlink_components(transactions)
    _assert_contained(map_dir, lock_path)
    return transactions


def _open_map_lock(map_dir: Path) -> int:
    if (
        fcntl is None
        or not hasattr(fcntl, "flock")
        or not hasattr(os, "O_NOFOLLOW")
        or not hasattr(os, "O_DIRECTORY")
    ):
        raise MapLockError("transaction lock assumptions are unsupported on this host")
    transactions = _prepare_lock_directory(map_dir)
    directory_fd = -1
    try:
        directory_fd = os.open(
            transactions, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        )
        opened = os.fstat(directory_fd)
        linked = transactions.lstat()
        if (opened.st_dev, opened.st_ino) != (linked.st_dev, linked.st_ino):
            raise MapLockError("transaction lock directory changed")
        _before_lock_file_open()
        linked = transactions.lstat()
        if (opened.st_dev, opened.st_ino) != (linked.st_dev, linked.st_ino):
            raise MapLockError("transaction lock directory changed")
        return _open_lock_file(directory_fd)
    except OSError as exc:
        raise MapLockError(f"cannot open transaction lock: {exc}") from exc
    finally:
        if directory_fd >= 0:
            os.close(directory_fd)


@contextmanager
def map_writer_lock(map_dir: Path):
    """Hold one verified regular Map-local lock across a complete mutation."""
    map_dir = Path(map_dir)
    lock_path = map_dir / ".transactions" / ".map.lock"
    descriptor = _open_map_lock(map_dir)
    try:
        opened = os.fstat(descriptor)
        linked = lock_path.lstat()
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or (opened.st_dev, opened.st_ino) != (linked.st_dev, linked.st_ino)
        ):
            raise MapLockError(
                f"transaction lock is not one contained regular file: {lock_path}"
            )
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
        except OSError as exc:
            raise MapLockError(f"cannot acquire transaction lock: {exc}") from exc
        try:
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
    except OSError as exc:
        raise MapLockError(f"cannot verify transaction lock: {exc}") from exc
    finally:
        os.close(descriptor)
