"""Create the canonical Brief that starts a claimed schema-v3 delivery."""
from __future__ import annotations

import errno
import os
import secrets
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import delivery_binding
import map_lock
import map_store


class StartDeliveryError(Exception):
    """A structural refusal while entering a delivery arc."""


class _OperationalError(Exception):
    """An unreadable or unavailable filesystem operation."""


def _canonical(value: str, label: str) -> PurePosixPath:
    if not value or value != value.strip() or "\\" in value:
        raise StartDeliveryError(f"{label} must be a non-empty canonical repository-relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {".", ".."} for part in path.parts) or path.as_posix() != value:
        raise StartDeliveryError(f"{label} must be a canonical repository-relative path: {value!r}")
    return path


def _ticket_relative(root: Path, ticket_path: Path) -> PurePosixPath:
    try:
        return _canonical(Path(os.path.abspath(ticket_path)).relative_to(root).as_posix(), "Ticket path")
    except ValueError as exc:
        raise StartDeliveryError(f"Ticket escapes repository: {ticket_path}") from exc


def _open_root(root: Path) -> int:
    try:
        return os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise StartDeliveryError("repository root must not be a symlink") from exc
        raise _OperationalError(f"cannot open repository root {root}: {exc}") from exc


def _open_parent(root_fd: int, relative: PurePosixPath, create: bool) -> tuple[int, str]:
    current = os.dup(root_fd)
    try:
        for part in relative.parts[:-1]:
            try:
                if stat.S_ISLNK(os.stat(part, dir_fd=current, follow_symlinks=False).st_mode):
                    raise StartDeliveryError(f"path contains a symlink component: {relative.as_posix()}")
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
            except FileNotFoundError:
                if not create:
                    raise _OperationalError(f"path is missing: {relative.as_posix()}") from None
                try:
                    os.mkdir(part, dir_fd=current)
                except FileExistsError:
                    pass
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
            except OSError as exc:
                if exc.errno == errno.ELOOP:
                    raise StartDeliveryError(f"path contains a symlink component: {relative.as_posix()}") from exc
                raise _OperationalError(f"cannot open path {relative.as_posix()}: {exc}") from exc
            os.close(current)
            current = next_fd
        return current, relative.name
    except (OSError, StartDeliveryError, _OperationalError):
        os.close(current)
        raise


def _read_file(root: Path, relative: PurePosixPath, *, missing_ok: bool = False) -> str | None:
    root_fd = _open_root(root)
    parent_fd = fd = -1
    try:
        try:
            parent_fd, leaf = _open_parent(root_fd, relative, False)
        except _OperationalError:
            if missing_ok:
                return None
            raise
        try:
            fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
        except FileNotFoundError:
            if missing_ok:
                return None
            raise _OperationalError(f"requested file is missing: {relative.as_posix()}") from None
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise StartDeliveryError(f"path is not a regular file: {relative.as_posix()}")
        with os.fdopen(fd, "r", encoding="utf-8") as stream:
            fd = -1
            return stream.read()
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise StartDeliveryError(f"path contains a symlink component: {relative.as_posix()}") from exc
        raise _OperationalError(f"cannot read {relative.as_posix()}: {exc}") from exc
    finally:
        if fd >= 0:
            os.close(fd)
        if parent_fd >= 0:
            os.close(parent_fd)
        os.close(root_fd)


def _read_snapshot(root: Path, relative: PurePosixPath) -> tuple[str, tuple[int, int]]:
    root_fd = _open_root(root)
    parent_fd = fd = -1
    try:
        parent_fd, leaf = _open_parent(root_fd, relative, False)
        fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise StartDeliveryError(f"path is not a regular file: {relative.as_posix()}")
        with os.fdopen(fd, "r", encoding="utf-8") as stream:
            fd = -1
            return stream.read(), (metadata.st_dev, metadata.st_ino)
    finally:
        if fd >= 0:
            os.close(fd)
        if parent_fd >= 0:
            os.close(parent_fd)
        os.close(root_fd)


def _replace_at(parent_fd: int, leaf: str, text: str) -> None:
    temporary = f".{leaf}.{secrets.token_hex(12)}"
    fd = -1
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent_fd)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            fd = -1
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, leaf, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        os.fsync(parent_fd)
    except OSError:
        if fd >= 0:
            os.close(fd)
        try:
            os.unlink(temporary, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        raise


def _publish_new_at(parent_fd: int, leaf: str, text: str) -> None:
    temporary = f".{leaf}.{secrets.token_hex(12)}"
    _replace_at(parent_fd, temporary, text)
    try:
        os.link(temporary, leaf, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=parent_fd)
        except FileNotFoundError:
            pass


def _same_snapshot(root: Path, relative: PurePosixPath, expected: str) -> None:
    actual = _read_file(root, relative)
    if actual != expected:
        raise StartDeliveryError(f"concurrent change detected for {relative.as_posix()}")


def _same_orphan(prepared: _Prepared) -> None:
    if prepared.orphan_snapshot is not None:
        if _read_snapshot(prepared.root, prepared.brief) != prepared.orphan_snapshot:
            raise StartDeliveryError(f"concurrent change detected for {prepared.brief.as_posix()}")


def _before_brief_write(_parent_fd: int, _leaf: str) -> None:
    """Test seam invoked only after the Brief parent descriptor is held."""


def _before_first_write() -> None:
    """Test seam after the optimistic read-set and before Brief publication."""


def _before_ticket_publish() -> None:
    """Test seam after Brief publication and before Ticket publication."""


def _before_ticket_replace() -> None:
    """Test seam after final validation and before the guarded Ticket write."""


def _brief_text(ticket: PurePosixPath, promised_slice: str) -> str:
    return (f"# {ticket.stem.replace('-', ' ')} — delivery brief\n\n"
            f"## Smallest End State\n\n{promised_slice}\n\n"
            f"## Acceptance\n\n- [ ] Promised slice: {promised_slice}\n\n"
            f"Outcome Map ticket: {ticket.as_posix()}\n\n"
            f"## Delivery closure\n\npolicy: pr-ci\n"
            "review-evidence: required before closure\n"
            "verification-evidence: required before closure\n")


def _ticket_with_brief(ticket_text: str, brief: PurePosixPath) -> str:
    lines = ticket_text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise StartDeliveryError("ticket has invalid frontmatter")
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            lines.insert(index, f"brief: {brief.as_posix()}\n")
            return "".join(lines)
    raise StartDeliveryError("ticket has invalid frontmatter")


def _schema_version(text: str) -> int:
    fields, _ = map_store.parse_frontmatter(text)
    try:
        return int(fields["schema_version"])
    except (KeyError, ValueError) as exc:
        raise StartDeliveryError("governing MAP.md has invalid schema_version") from exc


@dataclass(frozen=True)
class _Prepared:
    root: Path
    ticket: PurePosixPath
    map_path: PurePosixPath
    brief: PurePosixPath
    ticket_text: str
    map_text: str
    brief_text: str
    brief_exists: bool
    already_bound: bool
    orphan_snapshot: tuple[str, tuple[int, int]] | None


def _prepare(ticket_path: Path, brief_path: str, repo_root: Path | None) -> _Prepared:
    root = Path(os.path.abspath(repo_root if repo_root is not None else map_store.resolve_repo_root(None, Path(ticket_path).parent)))
    if not root.is_dir():
        raise _OperationalError(f"repository root is not a directory: {root}")
    ticket = _ticket_relative(root, Path(ticket_path))
    map_path = ticket.parent.parent / "MAP.md"
    brief = _canonical(brief_path, "Brief path")
    ticket_text = _read_file(root, ticket)
    assert ticket_text is not None
    fields, body = map_store.parse_frontmatter(ticket_text)
    map_text = _read_file(root, map_path)
    assert map_text is not None
    if _schema_version(map_text) != 3:
        raise StartDeliveryError("Start delivery requires a schema-v3 ticket")
    map_doc = map_store.parse_map_document(map_text, root / map_path)
    if map_doc.frontmatter.state != "active":
        raise StartDeliveryError("Start delivery requires an active Map")
    if fields.get("type") != "delivery" or fields.get("status") != "claimed":
        raise StartDeliveryError("Start delivery requires a claimed delivery ticket")
    if fields.get("blocked-by", "").strip():
        raise StartDeliveryError("Start delivery refuses a blocked ticket")
    promised_slice = body.strip()
    if not promised_slice:
        raise StartDeliveryError("delivery ticket must describe its promised slice")
    expected = _brief_text(ticket, promised_slice)
    if "brief" in fields:
        if _canonical(fields["brief"], "Ticket brief") != brief:
            raise StartDeliveryError("ticket already has an inconsistent Brief binding")
        code, message = delivery_binding.validate(root / ticket, repo_root=root)
        if code == 1:
            raise _OperationalError(f"ticket binding could not be read: {message}")
        if code != 0:
            raise StartDeliveryError(f"ticket has an inconsistent Brief binding: {message}")
        return _Prepared(root, ticket, map_path, brief, ticket_text, map_text, expected, True, True, None)
    existing = _read_file(root, brief, missing_ok=True)
    if existing is not None and existing != expected:
        raise StartDeliveryError(f"requested Brief path already exists: {brief.as_posix()}")
    orphan = _read_snapshot(root, brief) if existing is not None else None
    if orphan is not None and orphan[0] != expected:
        raise StartDeliveryError(f"requested Brief path already exists: {brief.as_posix()}")
    return _Prepared(root, ticket, map_path, brief, ticket_text, map_text, expected, existing is not None, False, orphan)


def _replace_ticket(prepared: _Prepared, candidate: str) -> None:
    map_store._atomic_write(
        prepared.root / prepared.ticket,
        candidate,
        expected=prepared.ticket_text.encode("utf-8"),
    )


def _rollback(prepared: _Prepared, ticket_replaced: bool,
              ticket_candidate: str) -> list[Exception]:
    errors: list[Exception] = []
    if ticket_replaced:
        try:
            map_store._atomic_write(
                prepared.root / prepared.ticket,
                prepared.ticket_text,
                expected=ticket_candidate.encode("utf-8"),
            )
        except (OSError, map_store.SchemaViolation) as exc:
            errors.append(exc)
    return errors


def _apply(prepared: _Prepared) -> None:
    if prepared.already_bound:
        return
    root_fd = _open_root(prepared.root)
    brief_parent = -1
    ticket_replaced = False
    ticket_candidate = _ticket_with_brief(prepared.ticket_text, prepared.brief)
    try:
        _before_first_write()
        _same_snapshot(prepared.root, prepared.ticket, prepared.ticket_text)
        _same_snapshot(prepared.root, prepared.map_path, prepared.map_text)
        if not prepared.brief_exists:
            brief_parent, brief_leaf = _open_parent(root_fd, prepared.brief, True)
            _before_brief_write(brief_parent, brief_leaf)
            _publish_new_at(brief_parent, brief_leaf, prepared.brief_text)
        _before_ticket_publish()
        _same_snapshot(prepared.root, prepared.ticket, prepared.ticket_text)
        _same_snapshot(prepared.root, prepared.map_path, prepared.map_text)
        _same_orphan(prepared)
        _before_ticket_replace()
        _replace_ticket(prepared, ticket_candidate)
        ticket_replaced = True
        code, message = delivery_binding.validate(prepared.root / prepared.ticket, repo_root=prepared.root)
        if code != 0:
            raise StartDeliveryError(f"created binding did not validate: {message}")
    except (OSError, StartDeliveryError, map_store.SchemaViolation) as exc:
        rollback_errors = _rollback(prepared, ticket_replaced, ticket_candidate)
        if rollback_errors:
            raise _OperationalError(f"Start delivery failed and rollback failed: {rollback_errors[0]}") from exc
        raise _OperationalError(f"Start delivery failed: {exc}") from exc
    finally:
        if brief_parent >= 0:
            os.close(brief_parent)
        os.close(root_fd)


def start_delivery(ticket_path: Path, brief_path: str, repo_root: Path | None = None) -> tuple[int, str]:
    """Create or recover one reciprocal Brief for a claimed v3 delivery."""
    try:
        initial = _prepare(ticket_path, brief_path, repo_root)
        map_dir = initial.root / initial.ticket.parent.parent
        with map_lock.map_writer_lock(map_dir):
            prepared = _prepare(ticket_path, brief_path, repo_root)
            _apply(prepared)
        action = "reused" if prepared.brief_exists else "created"
        return 0, f"Start delivery {action} {prepared.brief.as_posix()}"
    except StartDeliveryError as exc:
        return 2, f"Start delivery refused: {exc}"
    except (
        _OperationalError,
        OSError,
        map_lock.MapLockError,
        map_store.MapStoreError,
        map_store.SchemaViolation,
    ) as exc:
        return 1, f"Start delivery failed: {exc}"
