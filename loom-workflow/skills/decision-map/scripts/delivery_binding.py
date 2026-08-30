#!/usr/bin/env python3
"""Read-only validation for a delivery Ticket's reciprocal Brief binding."""

from __future__ import annotations

import errno
import os
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import map_store


class _OperationalFailure(Exception):
    pass


class _BindingFailure(Exception):
    pass


@dataclass(frozen=True)
class DeliveryMigrationBindingSnapshot:
    """Read-only CAS evidence for a v2 ticket becoming a delivery Ticket.

    The snapshot covers the canonical Brief and every candidate Ticket the
    reciprocal-binding contract consults, so a migration can revalidate the
    same population immediately before it writes.
    """

    texts: dict[str, str]
    ticket_membership: tuple[str, ...]


def _canonical_relative(value: str, label: str) -> PurePosixPath:
    if not value or value != value.strip():
        raise _BindingFailure(f"{label} path must be a non-empty canonical repository-relative path")
    if "\\" in value:
        raise _BindingFailure(f"{label} path must use '/' separators: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise _BindingFailure(f"{label} path must not be absolute or traverse directories: {value!r}")
    if path.as_posix() != value:
        raise _BindingFailure(f"{label} path is not normalized: {value!r}")
    return path


def _open_failure(
    exc: OSError, label: str, relative: PurePosixPath, requested: bool
) -> None:
    if exc.errno == errno.ELOOP:
        raise _BindingFailure(f"{label} path contains a symlink component: {relative.as_posix()}") from exc
    if exc.errno in {errno.ENOENT, errno.ENOTDIR}:
        if requested:
            raise _OperationalFailure(
                f"requested {label} is missing or not a regular file: {relative.as_posix()}"
            ) from exc
        raise _BindingFailure(f"{label} target does not exist or is not a regular file: {relative.as_posix()}") from exc
    raise _OperationalFailure(f"cannot open {label} target {relative.as_posix()}: {exc}") from exc


def _read_repo_file(
    repo_root: Path, relative: PurePosixPath, label: str, requested: bool = False
) -> str:
    """Open a canonical relative regular file without following any symlink."""
    if not hasattr(os, "O_NOFOLLOW"):
        raise _OperationalFailure("platform lacks O_NOFOLLOW; cannot safely validate bindings")
    try:
        directory = os.open(
            repo_root, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_DIRECTORY", 0)
        )
    except OSError as exc:
        if exc.errno == errno.ELOOP or (
            exc.errno == errno.ENOTDIR and stat.S_ISLNK(os.lstat(repo_root).st_mode)
        ):
            raise _BindingFailure("repository root was replaced by a symlink before open") from exc
        raise _OperationalFailure(f"cannot open repository root {repo_root}: {exc}") from exc
    fd = directory
    try:
        for index, part in enumerate(relative.parts):
            flags = os.O_RDONLY | os.O_NOFOLLOW
            if index < len(relative.parts) - 1:
                flags |= getattr(os, "O_DIRECTORY", 0)
            try:
                if stat.S_ISLNK(os.stat(part, dir_fd=fd, follow_symlinks=False).st_mode):
                    raise _BindingFailure(f"{label} path contains a symlink component: {relative.as_posix()}")
                next_fd = os.open(part, flags, dir_fd=fd)
            except OSError as exc:
                _open_failure(exc, label, relative, requested)
            if fd != directory:
                os.close(fd)
            fd = next_fd
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            if requested:
                raise _OperationalFailure(
                    f"requested {label} is not a regular file: {relative.as_posix()}"
                )
            raise _BindingFailure(f"{label} target is not a regular file: {relative.as_posix()}")
        try:
            with os.fdopen(fd, "r", encoding="utf-8") as stream:
                fd = -1
                return stream.read()
        except OSError as exc:
            raise _OperationalFailure(f"cannot read {label} target {relative.as_posix()}: {exc}") from exc
    finally:
        if fd >= 0 and fd != directory:
            os.close(fd)
        os.close(directory)


def _ticket_fields(
    repo_root: Path, relative: PurePosixPath, label: str, requested: bool = False
) -> dict[str, str]:
    try:
        fields, _ = map_store.parse_frontmatter(
            _read_repo_file(repo_root, relative, label, requested)
        )
    except map_store.SchemaViolation as exc:
        raise _BindingFailure(f"{label} {relative.as_posix()} has invalid frontmatter: {exc}") from exc
    missing = [key for key in ("type", "status") if key not in fields]
    if missing:
        raise _BindingFailure(
            f"{label} {relative.as_posix()} frontmatter is missing {', '.join(repr(key) for key in missing)}"
        )
    return fields


def _ticket_relative(repo_root: Path, ticket_path: Path) -> PurePosixPath:
    try:
        raw = Path(os.path.abspath(ticket_path)).relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise _BindingFailure(f"ticket escapes repository: {ticket_path}") from exc
    return _canonical_relative(raw, "Ticket")


def _assert_reciprocal(brief_text: str, brief: PurePosixPath, ticket: PurePosixPath) -> None:
    expected = f"Outcome Map ticket: {ticket.as_posix()}"
    lines = [line for line in brief_text.splitlines() if line.startswith("Outcome Map ticket:")]
    if lines != [expected]:
        raise _BindingFailure(f"Brief {brief.as_posix()} must contain exactly {expected!r}; found {lines!r}")


def _candidate_brief(repo_root: Path, candidate: PurePosixPath) -> PurePosixPath | None:
    fields = _ticket_fields(repo_root, candidate, "candidate ticket", requested=True)
    brief = fields.get("brief")
    if brief is None:
        return None
    if fields["type"] != "delivery":
        raise _BindingFailure(f"candidate ticket {candidate.as_posix()}: only delivery tickets may declare a 'brief' field")
    return _canonical_relative(brief, "candidate Ticket brief")


def _duplicate_owner(repo_root: Path, ticket: PurePosixPath, brief: PurePosixPath) -> PurePosixPath | None:
    maps_root = repo_root / "docs" / "loom" / "maps"
    if not maps_root.is_dir():
        return None
    for path in maps_root.rglob("*.md"):
        if path.parent.name != "tickets":
            continue
        candidate = _canonical_relative(path.relative_to(repo_root).as_posix(), "candidate Ticket")
        if candidate == ticket:
            continue
        candidate_brief = _candidate_brief(repo_root, candidate)
        if candidate_brief == brief:
            return candidate
        if candidate_brief is not None:
            _assert_reciprocal(_read_repo_file(repo_root, candidate_brief, "candidate Brief"), candidate_brief, candidate)
    return None


def snapshot_delivery_migration_binding(
    ticket_path: Path, repo_root: Path | None = None
) -> DeliveryMigrationBindingSnapshot:
    """Validate the existing reciprocal Brief required before migration.

    Unlike :func:`validate`, this accepts a schema-v2 source ticket that is
    *about to become* delivery. It writes nothing and returns every source
    text consulted by the canonical reciprocal-binding and duplicate-owner
    checks, keyed by canonical repository-relative path.
    """
    try:
        root = Path(os.path.abspath(repo_root if repo_root is not None else map_store.resolve_repo_root(None, Path(ticket_path).parent)))
        ticket = _ticket_relative(root, Path(ticket_path))
        texts: dict[str, str] = {}

        def read(relative: PurePosixPath, label: str, requested: bool = False) -> str:
            text = _read_repo_file(root, relative, label, requested)
            texts[relative.as_posix()] = text
            return text

        fields, _ = map_store.parse_frontmatter(read(ticket, "ticket", requested=True))
        brief_value = fields.get("brief")
        if brief_value is None:
            raise _BindingFailure("delivery migration requires an existing 'brief:' field")
        brief = _canonical_relative(brief_value, "Ticket brief")
        _assert_reciprocal(read(brief, "Brief"), brief, ticket)

        maps_root = root / "docs" / "loom" / "maps"
        candidates: list[PurePosixPath] = []
        if maps_root.is_dir():
            for path in maps_root.rglob("*.md"):
                if path.parent.name != "tickets":
                    continue
                candidate = _canonical_relative(
                    path.relative_to(root).as_posix(), "candidate Ticket"
                )
                candidates.append(candidate)
        membership = tuple(sorted(candidate.as_posix() for candidate in candidates))
        for candidate in candidates:
            candidate_fields, _ = map_store.parse_frontmatter(
                read(candidate, "candidate ticket", requested=True)
            )
            candidate_brief_value = candidate_fields.get("brief")
            if candidate == ticket or candidate_brief_value is None:
                continue
            if candidate_fields.get("type") != "delivery":
                raise _BindingFailure(
                    f"candidate ticket {candidate.as_posix()}: only delivery tickets may declare a 'brief' field"
                )
            candidate_brief = _canonical_relative(
                candidate_brief_value, "candidate Ticket brief"
            )
            if candidate_brief == brief:
                raise _BindingFailure(
                    f"Brief {brief.as_posix()} is already owned by another Ticket: {candidate.as_posix()}"
                )
            _assert_reciprocal(
                read(candidate_brief, "candidate Brief"), candidate_brief, candidate
            )
        return DeliveryMigrationBindingSnapshot(texts, membership)
    except _OperationalFailure as exc:
        raise ValueError(str(exc)) from exc
    except _BindingFailure as exc:
        raise ValueError(f"delivery binding invalid: {exc}") from exc


def validate(ticket_path: Path, repo_root: Path | None = None) -> tuple[int, str]:
    """Validate one Ticket's optional, reciprocal delivery Brief binding; writes nothing."""
    try:
        lexical_root = Path(os.path.abspath(repo_root if repo_root is not None else map_store.resolve_repo_root(None, Path(ticket_path).parent)))
        # Keep the caller's lexical root for the descriptor-relative walk.
        # Resolving it here would follow a replaceable root symlink before
        # _read_repo_file gets a chance to enforce O_NOFOLLOW.
        root = lexical_root
        if not root.is_dir():
            raise _OperationalFailure(f"repository root is not a directory: {root}")
        ticket = _ticket_relative(lexical_root, Path(ticket_path))
        fields = _ticket_fields(root, ticket, "ticket", requested=True)
        if fields["type"] != "delivery":
            if "brief" in fields:
                raise _BindingFailure("only delivery tickets may declare a 'brief' field")
            return 0, f"{ticket.as_posix()}: non-delivery ticket has no delivery binding"
        if "brief" not in fields:
            return 0, f"{ticket.as_posix()}: delivery ticket is unbriefed"
        brief = _canonical_relative(fields["brief"], "Ticket brief")
        _assert_reciprocal(_read_repo_file(root, brief, "Brief"), brief, ticket)
        duplicate = _duplicate_owner(root, ticket, brief)
        if duplicate is not None:
            raise _BindingFailure(f"Brief {brief.as_posix()} is already owned by another Ticket: {duplicate.as_posix()}")
        return 0, f"{ticket.as_posix()}: reciprocal delivery binding is valid"
    except _OperationalFailure as exc:
        return 1, str(exc)
    except _BindingFailure as exc:
        return 2, f"delivery binding invalid: {exc}"
    except OSError as exc:
        return 1, f"cannot resolve repository root or ticket: {exc}"
