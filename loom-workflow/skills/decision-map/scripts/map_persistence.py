"""Filesystem safety and atomic persistence for Decision Map documents."""

from __future__ import annotations

import ctypes
import errno
import json
import os
import platform
import tempfile
from collections.abc import Callable
from pathlib import Path

import map_lock
from map_documents import SchemaViolation


class AtomicExchangeUnsupported(SchemaViolation):
    """The local filesystem cannot provide an atomic pathname exchange."""


class AtomicExchangeBroken(SchemaViolation):
    """An exchanged target could not be restored after a CAS mismatch."""


def assert_no_symlink_components(path: Path) -> None:
    map_lock.assert_no_symlink_components(path, error=SchemaViolation)


def assert_contained(root: Path, candidate: Path) -> None:
    try:
        candidate.resolve(strict=False).relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise SchemaViolation(f"path escapes repository root: {candidate}") from exc


def _before_atomic_exchange(path: Path, temporary: Path) -> None:
    """Test seam immediately before the atomic pathname exchange."""


def _before_atomic_restore(path: Path, temporary: Path) -> None:
    """Test seam after mismatch detection and before the restore exchange."""


def exchange_paths(first: Path, second: Path) -> None:
    """Atomically exchange two existing same-filesystem pathnames."""
    libc = ctypes.CDLL(None, use_errno=True)
    system = platform.system()
    first_bytes = os.fsencode(first)
    second_bytes = os.fsencode(second)
    if system == "Darwin" and hasattr(libc, "renamex_np"):
        rename = libc.renamex_np
        rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        result = rename(first_bytes, second_bytes, 0x00000002)  # RENAME_SWAP
    elif system == "Linux" and hasattr(libc, "renameat2"):
        rename = libc.renameat2
        rename.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        rename.restype = ctypes.c_int
        result = rename(-100, first_bytes, -100, second_bytes, 0x00000002)
    else:
        raise AtomicExchangeUnsupported(
            f"atomic exchange is unsupported on {system or 'this platform'}"
        )
    if result == 0:
        return
    error = ctypes.get_errno()
    if error in {
        errno.ENOSYS,
        errno.EINVAL,
        errno.EXDEV,
        getattr(errno, "ENOTSUP", errno.EINVAL),
        getattr(errno, "EOPNOTSUPP", errno.EINVAL),
    }:
        raise AtomicExchangeUnsupported(
            f"atomic exchange is unsupported for {first.parent}: {os.strerror(error)}"
        )
    raise OSError(error, os.strerror(error), first)


def fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class AtomicWriter:
    """Atomic replacement with explicit callbacks for legacy fault injection."""

    def __init__(
        self,
        *,
        exchange: Callable[[Path, Path], None],
        sync_directory: Callable[[Path], None],
        before_exchange: Callable[[Path, Path], None],
        before_restore: Callable[[Path, Path], None],
    ) -> None:
        self._exchange_paths = exchange
        self._fsync_directory = sync_directory
        self._before_atomic_exchange = before_exchange
        self._before_atomic_restore = before_restore

    def _record_exchange_recovery(
        self,
        path: Path,
        temporary: Path,
        restore_error: BaseException,
        *,
        retained_role: str,
    ) -> Path:
        evidence_path = path.parent / f".{path.name}.cas-recovery.json"
        evidence = {
            "action": "recovery-required",
            "candidate_path": str(path),
            "retained_path": str(temporary),
            "retained_role": retained_role,
            "restore_error": str(restore_error),
            "status": "BROKEN",
        }
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        descriptor = os.open(evidence_path, flags, 0o600)
        try:
            payload = (json.dumps(evidence, indent=2, sort_keys=True) + "\n").encode()
            remaining = memoryview(payload)
            while remaining:
                written = os.write(descriptor, remaining)
                if written == 0:
                    raise OSError("short write while recording CAS recovery evidence")
                remaining = remaining[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self._fsync_directory(path.parent)
        return evidence_path

    def _recovery_detail(
        self,
        path: Path,
        temporary: Path,
        error: BaseException,
        retained_role: str,
    ) -> str:
        try:
            evidence_path = self._record_exchange_recovery(
                path, temporary, error, retained_role=retained_role
            )
        except BaseException as evidence_error:
            return (
                f"retained temp: {temporary}; recovery evidence unavailable: "
                f"{evidence_error}"
            )
        return f"evidence: {evidence_path}"

    def _cleanup_exchanged_temporary(self, path: Path, temporary: Path) -> None:
        try:
            temporary.unlink()
            self._fsync_directory(path.parent)
        except OSError:
            pass

    def _commit_exchanged_candidate(self, path: Path, temporary: Path) -> None:
        try:
            self._fsync_directory(path.parent)
        except OSError as durability_error:
            try:
                self._exchange_paths(temporary, path)
            except BaseException as restore_error:
                detail = self._recovery_detail(
                    path,
                    temporary,
                    restore_error,
                    "expected authority retained after durability failure",
                )
                raise AtomicExchangeBroken(
                    "BROKEN recovery-required: exchange durability failed and "
                    "authority could not be restored; " + detail
                ) from restore_error
            restoration_error: BaseException = durability_error
            try:
                self._fsync_directory(path.parent)
            except OSError as exc:
                restoration_error = exc
            detail = self._recovery_detail(
                path,
                temporary,
                restoration_error,
                "candidate retained after durability failure",
            )
            raise AtomicExchangeBroken(
                "BROKEN recovery-required: exchange durability failed; expected "
                "authority was restored and candidate retained; " + detail
            ) from durability_error
        self._cleanup_exchanged_temporary(path, temporary)

    def _restore_cas_mismatch(self, path: Path, temporary: Path, candidate: bytes) -> None:
        self._before_atomic_restore(path, temporary)
        try:
            self._exchange_paths(temporary, path)
        except BaseException as restore_error:
            detail = self._recovery_detail(
                path,
                temporary,
                restore_error,
                "concurrent version retained during restore",
            )
            raise AtomicExchangeBroken(
                "BROKEN recovery-required: atomic CAS restore failed; " + detail
            ) from restore_error
        if temporary.read_bytes() != candidate:
            self._handle_restore_interleaving(path, temporary)
        try:
            self._fsync_directory(path.parent)
        except OSError as durability_error:
            detail = self._recovery_detail(
                path,
                temporary,
                durability_error,
                "candidate retained after mismatch restore",
            )
            raise AtomicExchangeBroken(
                "BROKEN recovery-required: mismatch restore durability failed; " + detail
            ) from durability_error
        self._cleanup_exchanged_temporary(path, temporary)
        raise SchemaViolation(f"refusing atomic compare-and-swap because {path} changed")

    def _handle_restore_interleaving(self, path: Path, temporary: Path) -> None:
        try:
            self._exchange_paths(temporary, path)
        except BaseException as third_exchange_error:
            detail = self._recovery_detail(
                path,
                temporary,
                third_exchange_error,
                "newest concurrent version; restore incomplete",
            )
            raise AtomicExchangeBroken(
                "BROKEN recovery-required: newest concurrent version could not be "
                "returned to target; " + detail
            ) from third_exchange_error
        interleaving = RuntimeError(
            "target changed again between mismatch detection and restore"
        )
        detail = self._recovery_detail(
            path,
            temporary,
            interleaving,
            "concurrent version retained during restore",
        )
        raise AtomicExchangeBroken(
            "BROKEN recovery-required: target changed during CAS restore; " + detail
        ) from interleaving

    def write(
        self,
        path: Path, text: str, *, expected: bytes | None = None
    ) -> None:
        """Replace one regular file without exposing partially written bytes.

        This is the single-file safety floor used by REQ-86 operations.  Full
        multi-artifact conflict detection and recovery remain owned by REQ-87.
        """
        assert_no_symlink_components(path)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", dir=path.parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            if expected is None:
                os.replace(temporary, path)
                self._fsync_directory(path.parent)
                return
            self._before_atomic_exchange(path, temporary)
            try:
                self._exchange_paths(temporary, path)
            except AtomicExchangeUnsupported:
                raise
            except OSError as exc:
                raise SchemaViolation(
                    f"atomic compare-and-swap could not exchange {path}: {exc}"
                ) from exc
            displaced = temporary.read_bytes()
            if displaced == expected:
                self._commit_exchanged_candidate(path, temporary)
                return
            self._restore_cas_mismatch(path, temporary, text.encode("utf-8"))
        except BaseException as exc:
            if not isinstance(exc, AtomicExchangeBroken):
                try:
                    temporary.unlink()
                except FileNotFoundError:
                    pass
            raise


def atomic_write(path: Path, text: str, *, expected: bytes | None = None) -> None:
    """Atomically replace a document, refusing a stale expected version."""
    AtomicWriter(
        exchange=exchange_paths,
        sync_directory=fsync_directory,
        before_exchange=_before_atomic_exchange,
        before_restore=_before_atomic_restore,
    ).write(path, text, expected=expected)
