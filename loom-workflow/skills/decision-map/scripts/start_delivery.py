"""Create the canonical Brief that starts a claimed schema-v3 delivery."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import delivery_binding
import map_store


class StartDeliveryError(Exception):
    """A refusal or operational failure while entering a delivery arc."""


class _StartDeliveryReuse(Exception):
    """An existing reciprocal binding is the idempotent success result."""


def _relative(repo_root: Path, path: Path, label: str) -> PurePosixPath:
    try:
        raw = Path(os.path.abspath(path)).relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise StartDeliveryError(f"{label} escapes repository: {path}") from exc
    try:
        return delivery_binding._canonical_relative(raw, label)
    except delivery_binding._BindingFailure as exc:
        raise StartDeliveryError(str(exc)) from exc


def _assert_safe_existing_path(repo_root: Path, relative: PurePosixPath) -> None:
    """Reject symlink components before writing below the repository root."""
    current = repo_root
    try:
        if os.path.islink(current):
            raise StartDeliveryError("repository root must not be a symlink")
        for part in relative.parts:
            current = current / part
            if current.exists() or current.is_symlink():
                if current.is_symlink():
                    raise StartDeliveryError(
                        f"path contains a symlink component: {relative.as_posix()}"
                    )
    except OSError as exc:
        raise StartDeliveryError(f"cannot inspect path {relative.as_posix()}: {exc}") from exc


def _ensure_safe_parent(repo_root: Path, relative: PurePosixPath) -> Path:
    parent = repo_root
    for part in relative.parts[:-1]:
        parent = parent / part
        if parent.exists() or parent.is_symlink():
            if parent.is_symlink() or not parent.is_dir():
                raise StartDeliveryError(
                    f"Brief parent is not a safe directory: {parent.relative_to(repo_root)}"
                )
            continue
        try:
            parent.mkdir()
        except FileExistsError:
            if parent.is_symlink() or not parent.is_dir():
                raise StartDeliveryError(
                    f"Brief parent is not a safe directory: {parent.relative_to(repo_root)}"
                )
        except OSError as exc:
            raise StartDeliveryError(f"cannot create Brief parent {parent}: {exc}") from exc
    return parent


def _replace_atomically(path: Path, text: str) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    except OSError:
        temporary_path.unlink(missing_ok=True)
        raise


def _brief_text(ticket: PurePosixPath, promised_slice: str) -> str:
    return (
        f"# {ticket.stem.replace('-', ' ')} — delivery brief\n\n"
        "## Smallest End State\n\n"
        f"{promised_slice}\n\n"
        "## Acceptance\n\n"
        f"- [ ] Promised slice: {promised_slice}\n\n"
        f"Outcome Map ticket: {ticket.as_posix()}\n"
    )


def _ticket_with_brief(ticket_text: str, brief: PurePosixPath) -> str:
    lines = ticket_text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise StartDeliveryError("ticket has invalid frontmatter")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            lines.insert(index, f"brief: {brief.as_posix()}\n")
            return "".join(lines)
    raise StartDeliveryError("ticket has invalid frontmatter")


@dataclass(frozen=True)
class _PreparedStart:
    root: Path
    ticket: PurePosixPath
    brief: PurePosixPath
    ticket_file: Path
    brief_file: Path
    ticket_text: str
    promised_slice: str


def _prepare(ticket_path: Path, brief_path: str, repo_root: Path | None) -> _PreparedStart:
    root = Path(os.path.abspath(repo_root if repo_root is not None else map_store.resolve_repo_root(None, Path(ticket_path).parent)))
    if not root.is_dir():
        raise StartDeliveryError(f"repository root is not a directory: {root}")
    ticket = _relative(root, Path(ticket_path), "Ticket")
    brief = delivery_binding._canonical_relative(brief_path, "Brief")
    _assert_safe_existing_path(root, ticket)
    ticket_file = root / ticket
    ticket_text = delivery_binding._read_repo_file(root, ticket, "ticket", requested=True)
    fields, body = map_store.parse_frontmatter(ticket_text)
    if map_store.resolve_schema_version(ticket_file) != 3:
        raise StartDeliveryError("Start delivery requires a schema-v3 ticket")
    if fields.get("type") != "delivery":
        raise StartDeliveryError("Start delivery requires a delivery ticket")
    if fields.get("status") != "claimed":
        raise StartDeliveryError("Start delivery requires a claimed, nonterminal ticket")
    if fields.get("blocked-by", "").strip():
        raise StartDeliveryError("Start delivery refuses a blocked ticket")
    if "brief" in fields:
        _reuse(root, ticket_file, brief, fields["brief"])
        raise _StartDeliveryReuse(brief.as_posix())
    promised_slice = body.strip()
    if not promised_slice:
        raise StartDeliveryError("delivery ticket must describe its promised slice")
    _assert_safe_existing_path(root, brief)
    brief_file = root / brief
    if brief_file.exists() or brief_file.is_symlink():
        raise StartDeliveryError(f"requested Brief path already exists: {brief.as_posix()}")
    _ensure_safe_parent(root, brief)
    return _PreparedStart(root, ticket, brief, ticket_file, brief_file, ticket_text, promised_slice)


def _reuse(root: Path, ticket_file: Path, brief: PurePosixPath, existing: str) -> None:
    existing_brief = delivery_binding._canonical_relative(existing, "Ticket brief")
    if existing_brief != brief:
        raise StartDeliveryError("ticket already has an inconsistent Brief binding")
    code, message = delivery_binding.validate(ticket_file, repo_root=root)
    if code != 0:
        raise StartDeliveryError(f"ticket has an inconsistent Brief binding: {message}")


def _apply(prepared: _PreparedStart) -> None:
    ticket_replaced = False
    try:
        _replace_atomically(
            prepared.brief_file, _brief_text(prepared.ticket, prepared.promised_slice)
        )
        _replace_atomically(
            prepared.ticket_file, _ticket_with_brief(prepared.ticket_text, prepared.brief)
        )
        ticket_replaced = True
        code, message = delivery_binding.validate(prepared.ticket_file, repo_root=prepared.root)
        if code != 0:
            raise StartDeliveryError(f"created binding did not validate: {message}")
    except (OSError, StartDeliveryError) as exc:
        rollback_errors = []
        try:
            prepared.brief_file.unlink(missing_ok=True)
        except OSError as rollback_exc:
            rollback_errors.append(rollback_exc)
        if ticket_replaced:
            try:
                _replace_atomically(prepared.ticket_file, prepared.ticket_text)
            except OSError as rollback_exc:
                rollback_errors.append(rollback_exc)
        if rollback_errors:
            raise StartDeliveryError(
                f"Start delivery failed and rollback failed: {rollback_errors[0]}"
            ) from exc
        raise StartDeliveryError(f"Start delivery failed: {exc}") from exc


def start_delivery(ticket_path: Path, brief_path: str, repo_root: Path | None = None) -> tuple[int, str]:
    """Create one reciprocal Brief for a claimed, unblocked v3 delivery.

    Repeating the same request validates and reuses its existing binding; all
    other pre-existing bindings and target paths refuse without a write.
    """
    try:
        prepared = _prepare(ticket_path, brief_path, repo_root)
        _apply(prepared)
        return 0, f"Start delivery created {prepared.brief.as_posix()}"
    except _StartDeliveryReuse as exc:
        return 0, f"Start delivery reused {exc}"
    except (StartDeliveryError, delivery_binding._BindingFailure) as exc:
        return 2, f"Start delivery refused: {exc}"
    except (OSError, map_store.MapStoreError, map_store.SchemaViolation) as exc:
        return 1, f"Start delivery failed: {exc}"
