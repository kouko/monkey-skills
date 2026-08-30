#!/usr/bin/env python3
"""Recoverable schema-v3 Map transactions.

REQ-84 defines ordered close-and-rechart. REQ-87 extends the same atomic
primitives with full-read-set conflicts, idempotent retries, and safe recovery.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import map_store


class CloseTransactionError(ValueError):
    """The requested close conflicts with the authoritative map state."""


@dataclass(frozen=True)
class UnknownRoute:
    text: str
    destination: str
    ticket_slug: str | None = None
    ticket_type: str | None = None


@dataclass(frozen=True)
class CloseResult:
    routed: int
    map_clear_eligible: bool


@dataclass(frozen=True)
class StoreRevision:
    entries: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class MutationResult:
    applied: bool
    reused: bool


def _before_terminalize() -> None:
    """Test seam immediately before the final, terminal ticket write."""


def _before_retirement_stability_check() -> None:
    """Test seam after retirement validation and before snapshot comparison."""


def _before_retirement_transition() -> None:
    """Test seam between readiness preparation and transition commit."""


def _before_archive_state_replace() -> None:
    """Test seam immediately before the archive commit-boundary check."""


def _after_archive_state_replace() -> None:
    """Test seam before post-write validation and possible MAP rollback."""


def _before_retirement_replace() -> None:
    """Test seam immediately before the MAP compare-and-swap write."""


def capture_revision(map_dir: Path) -> StoreRevision:
    """Digest the complete Map-and-Ticket topology read set."""
    map_dir = Path(map_dir)
    paths = [map_dir / "MAP.md"]
    tickets_dir = map_dir / "tickets"
    try:
        tickets_mode = tickets_dir.lstat().st_mode
    except OSError as exc:
        raise CloseTransactionError(
            f"cannot read transaction revision for {tickets_dir}: {exc}"
        ) from exc
    if not stat.S_ISDIR(tickets_mode):
        raise CloseTransactionError(
            f"transaction read set contains a non-regular tickets directory: "
            f"{tickets_dir}"
        )
    paths.extend(sorted(tickets_dir.glob("*.md")))
    entries: list[tuple[str, str]] = []
    for path in paths:
        try:
            mode = path.lstat().st_mode
            if not stat.S_ISREG(mode):
                raise CloseTransactionError(
                    f"transaction read set contains a non-regular file: {path}"
                )
            payload = path.read_bytes()
        except OSError as exc:
            raise CloseTransactionError(
                f"cannot read transaction revision for {path}: {exc}"
            ) from exc
        entries.append(
            (
                path.relative_to(map_dir).as_posix(),
                hashlib.sha256(payload).hexdigest(),
            )
        )
    return StoreRevision(tuple(entries))


def _require_revision(map_dir: Path, expected: StoreRevision) -> None:
    if capture_revision(map_dir) != expected:
        raise CloseTransactionError(
            "transaction conflict: the authoritative Map or Ticket read set "
            "changed; re-read before retry"
        )


def _assert_supported_filesystem(directory: Path) -> None:
    """Probe the same directory's atomic exchange before artifact mutation."""
    descriptors: list[int] = []
    paths: list[Path] = []
    try:
        for prefix in (".map-cas-probe-a.", ".map-cas-probe-b."):
            descriptor, name = tempfile.mkstemp(prefix=prefix, dir=directory)
            descriptors.append(descriptor)
            paths.append(Path(name))
        for descriptor in descriptors:
            os.close(descriptor)
        descriptors.clear()
        map_store._exchange_paths(paths[0], paths[1])
        map_store._fsync_directory(directory)
    except (OSError, map_store.SchemaViolation) as exc:
        raise CloseTransactionError(
            f"unsupported atomic-replacement assumption for {directory}: {exc}"
        ) from exc
    finally:
        for descriptor in descriptors:
            try:
                os.close(descriptor)
            except OSError:
                pass
        for path in paths:
            try:
                path.unlink()
            except FileNotFoundError:
                pass


def _exclusive_write(path: Path, text: str) -> None:
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        map_store._fsync_directory(path.parent)
    except FileExistsError as exc:
        raise CloseTransactionError(
            f"transaction conflict: {path} already exists; re-read before retry"
        ) from exc
    except OSError as exc:
        raise CloseTransactionError(
            f"cannot create transaction artifact {path}: {exc}"
        ) from exc


def _operation_path(map_dir: Path, operation_id: str) -> Path:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", operation_id):
        raise CloseTransactionError("operation_id must be a safe lowercase slug")
    path = map_dir / ".transactions" / f"{operation_id}.json"
    _assert_no_symlink_components(path)
    _assert_contained(map_dir, path)
    return path


def _load_operation(path: Path, intent: dict[str, object]) -> bool:
    if not path.exists():
        return False
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CloseTransactionError(f"cannot recover operation record: {exc}") from exc
    if saved != intent:
        raise CloseTransactionError(
            "operation retry conflicts with the authoritative operation record"
        )
    return True


def _replace_frontmatter_field(
    text: str, field: str, value: str | None
) -> str:
    lines = text.splitlines()
    try:
        end = lines[1:].index("---") + 1
    except ValueError as exc:
        raise CloseTransactionError("ticket has invalid frontmatter") from exc
    matches = [index for index in range(1, end) if lines[index].startswith(f"{field}:")]
    if len(matches) > 1:
        raise CloseTransactionError(f"ticket has duplicate {field!r} frontmatter")
    replacement = f"{field}: {value}" if value is not None else None
    if matches and replacement is None:
        lines.pop(matches[0])
    elif matches:
        assert replacement is not None
        lines[matches[0]] = replacement
    elif replacement is not None:
        lines.insert(end, replacement)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def _prepare_mutation(
    map_dir: Path,
    operation_id: str,
    intent: dict[str, object],
    expected_revision: StoreRevision,
) -> tuple[Path, bool]:
    _require_revision(map_dir, expected_revision)
    _assert_supported_filesystem(map_dir)
    operation = _operation_path(map_dir, operation_id)
    if _load_operation(operation, intent):
        return operation, True
    operation.parent.mkdir(mode=0o700, exist_ok=True)
    _require_revision(map_dir, expected_revision)
    _exclusive_write(operation, json.dumps(intent, indent=2, sort_keys=True) + "\n")
    return operation, False


def claim_ticket(
    map_dir: Path,
    ticket_slug: str,
    *,
    owner: str,
    claimed_on: str,
    operation_id: str,
    expected_revision: StoreRevision,
) -> MutationResult:
    """Claim one unblocked frontier ticket against a full store revision."""
    map_dir = Path(map_dir)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ticket_slug):
        raise CloseTransactionError("ticket_slug is not a safe slug")
    if (
        not owner.strip()
        or "," in owner
        or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", claimed_on)
    ):
        raise CloseTransactionError("claim requires an owner and YYYY-MM-DD date")
    intent = {
        "version": 1,
        "kind": "claim",
        "ticket_slug": ticket_slug,
        "owner": owner.strip(),
        "claimed_on": claimed_on,
    }
    operation = _operation_path(map_dir, operation_id)
    ticket_path = map_dir / "tickets" / f"{ticket_slug}.md"
    operation_prepared = _load_operation(operation, intent)
    if operation_prepared:
        ticket = map_store.read_ticket(ticket_path)
        desired = f"{owner.strip()}, {claimed_on}"
        if ticket.frontmatter.status == "claimed" and ticket.frontmatter.claim == desired:
            return MutationResult(False, True)
    _require_revision(map_dir, expected_revision)
    try:
        ticket = map_store.require_ticket_mutable(map_dir, ticket_slug, "claim")
        code, message = map_store.validate(map_dir)
    except (map_store.MapStoreError, map_store.SchemaViolation) as exc:
        raise CloseTransactionError(str(exc)) from exc
    if code != 0:
        raise CloseTransactionError(f"cannot claim from broken Map: {message}")
    if ticket.frontmatter.status != "open":
        raise CloseTransactionError("ticket must be open before claim")
    statuses = {
        path.stem: map_store.read_ticket(path).frontmatter.status
        for path in sorted((map_dir / "tickets").glob("*.md"))
    }
    unclosed = [
        slug for slug in ticket.frontmatter.blocked_by if statuses.get(slug) != "closed"
    ]
    if unclosed:
        raise CloseTransactionError("ticket is blocked by " + ", ".join(unclosed))
    original = ticket_path.read_bytes()
    updated = _replace_frontmatter_field(original.decode("utf-8"), "status", "claimed")
    updated = _replace_frontmatter_field(
        updated, "claim", f"{owner.strip()}, {claimed_on}"
    )
    if operation_prepared:
        _assert_supported_filesystem(map_dir)
        _require_revision(map_dir, expected_revision)
    else:
        _prepare_mutation(map_dir, operation_id, intent, expected_revision)
    try:
        map_store._atomic_write(ticket_path, updated, expected=original)
    except (OSError, map_store.SchemaViolation) as exc:
        raise CloseTransactionError(str(exc)) from exc
    return MutationResult(True, False)


def update_blockers(
    map_dir: Path,
    ticket_slug: str,
    blockers: list[str],
    *,
    operation_id: str,
    expected_revision: StoreRevision,
) -> MutationResult:
    """Replace blocker edges only after validating the current whole graph."""
    map_dir = Path(map_dir)
    intent = {
        "version": 1,
        "kind": "update-blockers",
        "ticket_slug": ticket_slug,
        "blockers": blockers,
    }
    operation = _operation_path(map_dir, operation_id)
    ticket_path = map_dir / "tickets" / f"{ticket_slug}.md"
    desired_value = ", ".join(blockers)
    operation_prepared = _load_operation(operation, intent)
    if operation_prepared:
        current = map_store.read_ticket(ticket_path)
        if current.frontmatter.blocked_by == blockers:
            return MutationResult(False, True)
        _require_revision(map_dir, expected_revision)
    try:
        map_store.require_ticket_mutable(map_dir, ticket_slug, "edit")
    except (map_store.MapStoreError, map_store.SchemaViolation) as exc:
        raise CloseTransactionError(str(exc)) from exc
    graph = {
        path.stem: map_store.read_ticket(path).frontmatter.blocked_by
        for path in sorted((map_dir / "tickets").glob("*.md"))
    }
    graph[ticket_slug] = blockers
    try:
        map_store._check_blocked_by(graph, map_dir / "tickets")
    except map_store.SchemaViolation as exc:
        raise CloseTransactionError(str(exc)) from exc
    statuses = {
        path.stem: map_store.read_ticket(path).frontmatter.status
        for path in sorted((map_dir / "tickets").glob("*.md"))
    }
    if statuses.get(ticket_slug) == "claimed":
        unclosed = [slug for slug in blockers if statuses.get(slug) != "closed"]
        if unclosed:
            raise CloseTransactionError(
                "claimed ticket requires closed blockers: " + ", ".join(unclosed)
            )
    original = ticket_path.read_bytes()
    updated = _replace_frontmatter_field(
        original.decode("utf-8"), "blocked-by", desired_value or None
    )
    if operation_prepared:
        _assert_supported_filesystem(map_dir)
        _require_revision(map_dir, expected_revision)
    else:
        _prepare_mutation(map_dir, operation_id, intent, expected_revision)
    try:
        map_store._atomic_write(ticket_path, updated, expected=original)
    except (OSError, map_store.SchemaViolation) as exc:
        raise CloseTransactionError(str(exc)) from exc
    return MutationResult(True, False)


def _atomic_write(
    path: Path, text: str, *, expected: bytes | None = None
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        map_store._atomic_write(path, text, expected=expected)
    except map_store.SchemaViolation as exc:
        raise CloseTransactionError(str(exc)) from exc


def _section_bounds(lines: list[str], name: str) -> tuple[int, int]:
    heading = f"## {name}"
    matches = [index for index, line in enumerate(lines) if line.strip() == heading]
    if len(matches) != 1:
        raise CloseTransactionError(f"MAP.md must contain exactly one {heading!r}")
    start = matches[0] + 1
    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return start, end


def _append_section_line(text: str, section: str, line: str) -> str:
    lines = text.splitlines()
    start, end = _section_bounds(lines, section)
    if line in (candidate.strip() for candidate in lines[start:end]):
        return text
    while end > start and not lines[end - 1].strip():
        end -= 1
    lines[end:end] = ([""] if end == start else []) + [line]
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def _validate_routes(unknowns: list[UnknownRoute]) -> None:
    route_keys = {
        (route.destination, route.text, route.ticket_slug) for route in unknowns
    }
    if len(route_keys) != len(unknowns):
        raise CloseTransactionError("duplicate unknown route in one close request")
    ticket_slugs = [
        route.ticket_slug for route in unknowns if route.destination == "ticket"
    ]
    if len(set(ticket_slugs)) != len(ticket_slugs):
        raise CloseTransactionError(
            "duplicate ticket_slug in one close request"
        )
    for route in unknowns:
        if not route.text.strip():
            raise CloseTransactionError("unknown route text must not be empty")
        if route.destination not in {"fog", "ticket", "out-of-scope"}:
            raise CloseTransactionError(
                "unknown destination must be fog, ticket, or out-of-scope"
            )
        if route.destination == "ticket":
            if not route.ticket_slug or not re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*", route.ticket_slug
            ):
                raise CloseTransactionError("ticket route requires a safe ticket_slug")
            if route.ticket_type not in map_store.V3_TICKET_TYPES:
                raise CloseTransactionError(
                    "ticket route requires grilling, research, prototype, or delivery"
                )
        elif route.ticket_slug is not None or route.ticket_type is not None:
            raise CloseTransactionError(
                "only a ticket route may carry ticket_slug or ticket_type"
            )


def _assert_no_symlink_components(path: Path) -> None:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            raise CloseTransactionError(
                f"refusing path with symlink component: {current}"
            )
        if not current.exists():
            break


def _assert_contained(map_dir: Path, candidate: Path) -> None:
    try:
        candidate.resolve(strict=False).relative_to(map_dir.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise CloseTransactionError(
            f"path escapes the map directory: {candidate}"
        ) from exc


def _validate_paths(
    map_dir: Path, ticket_slug: str, unknowns: list[UnknownRoute]
) -> tuple[Path, Path]:
    tickets_dir = map_dir / "tickets"
    source = tickets_dir / f"{ticket_slug}.md"
    journal = map_dir / ".transactions" / f"close-{ticket_slug}.json"
    candidates = [
        map_dir,
        map_dir / "MAP.md",
        tickets_dir,
        source,
        map_dir / ".transactions",
        journal,
    ]
    candidates.extend(
        tickets_dir / f"{route.ticket_slug}.md"
        for route in unknowns
        if route.destination == "ticket"
    )
    for candidate in candidates:
        _assert_no_symlink_components(candidate)
        _assert_contained(map_dir, candidate)
    return source, journal


def _validate_authoritative_ticket(
    ticket: map_store.TicketDocument, *, closed: bool
) -> None:
    expected_status = "closed" if closed else "claimed"
    if ticket.frontmatter.type not in map_store.V3_TICKET_TYPES:
        raise CloseTransactionError(
            "source is not an allowed schema-v3 ticket type"
        )
    if ticket.frontmatter.status != expected_status:
        raise CloseTransactionError(
            f"source ticket must be {expected_status}"
        )
    try:
        map_store._check_v3_ticket_frontmatter(ticket)
        if closed:
            map_store._check_v3_ticket_closure_evidence(ticket)
    except map_store.SchemaViolation as exc:
        raise CloseTransactionError(
            f"invalid authoritative schema-v3 source: {exc}"
        ) from exc


def _intent(
    ticket_slug: str,
    gist: str,
    resolution: str,
    unknowns: list[UnknownRoute],
    fog_ids: list[str | None],
) -> dict[str, object]:
    routes = []
    for route, fog_id in zip(unknowns, fog_ids, strict=True):
        item = asdict(route)
        item["fog_id"] = fog_id
        routes.append(item)
    return {
        "version": 1,
        "ticket_slug": ticket_slug,
        "gist": gist,
        "resolution": resolution,
        "routes": routes,
        "prepared": True,
    }


def _load_or_prepare_intent(
    map_dir: Path,
    ticket_slug: str,
    gist: str,
    resolution: str,
    unknowns: list[UnknownRoute],
    map_doc: map_store.MapDocument,
) -> tuple[Path, dict[str, object]]:
    journal = map_dir / ".transactions" / f"close-{ticket_slug}.json"
    if journal.exists():
        try:
            saved = json.loads(journal.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CloseTransactionError(f"cannot recover close operation: {exc}") from exc
        saved_fog_ids = [route.get("fog_id") for route in saved.get("routes", [])]
        expected = _intent(ticket_slug, gist, resolution, unknowns, saved_fog_ids)
        if saved != expected:
            raise CloseTransactionError(
                "close retry conflicts with the prepared operation record"
            )
        return journal, saved

    next_fog = max((entry.number for entry in map_doc.fog_entries), default=0) + 1
    fog_ids: list[str | None] = []
    for route in unknowns:
        if route.destination == "fog":
            fog_ids.append(f"F-{next_fog}")
            next_fog += 1
        else:
            fog_ids.append(None)
    prepared = _intent(ticket_slug, gist, resolution, unknowns, fog_ids)
    journal.parent.mkdir(mode=0o700, exist_ok=True)
    _exclusive_write(
        journal, json.dumps(prepared, indent=2, sort_keys=True) + "\n"
    )
    return journal, prepared


def _open_ticket_text(route: dict[str, object]) -> str:
    return (
        "---\n"
        f"type: {route['ticket_type']}\n"
        "status: open\n"
        "claim: null\n"
        "graduated-from: null\n"
        "---\n\n"
        f"{route['text']}\n"
    )


def _apply_map_effects(
    map_dir: Path,
    ticket_slug: str,
    gist: str,
    routes: list[dict[str, object]],
) -> None:
    map_path = map_dir / "MAP.md"
    original = map_path.read_bytes()
    text = original.decode("utf-8")
    decision = f"- {gist} (tickets/{ticket_slug}.md)"
    text = _append_section_line(text, "Decisions-so-far", decision)
    for route in routes:
        destination = route["destination"]
        if destination == "fog":
            line = f"- {route['fog_id']}: {route['text']}"
            text = _append_section_line(text, "Not-yet-specified (fog)", line)
        elif destination == "out-of-scope":
            text = _append_section_line(
                text, "Out-of-scope", f"- {route['text']}"
            )
        else:
            ticket_path = map_dir / "tickets" / f"{route['ticket_slug']}.md"
            expected = _open_ticket_text(route)
            if ticket_path.exists():
                if ticket_path.read_text(encoding="utf-8") != expected:
                    raise CloseTransactionError(
                        f"ticket route conflicts with existing {ticket_path.name}"
                    )
            else:
                _exclusive_write(ticket_path, expected)
    if original.decode("utf-8") != text:
        _atomic_write(map_path, text, expected=original)


def _terminal_text(text: str, resolution: str) -> str:
    if text.count("status: claimed") != 1:
        raise CloseTransactionError("source ticket must be claimed before close")
    closed = text.replace("status: claimed", "status: closed", 1)
    return closed.rstrip() + "\n\n## Resolution\n\n" + resolution.strip() + "\n"


def _validate_terminal_candidate(ticket_path: Path, text: str) -> None:
    try:
        candidate = map_store.parse_ticket_document(text, ticket_path)
        map_store._check_v3_ticket_closure_evidence(candidate)
    except map_store.SchemaViolation as exc:
        raise CloseTransactionError(f"invalid closure evidence: {exc}") from exc


def _assess_clear(map_dir: Path) -> bool:
    doc = map_store.read_map(map_dir)
    candidate = replace(
        doc,
        frontmatter=replace(doc.frontmatter, state="clear"),
    )
    try:
        map_store._check_map_structure(candidate)
        map_store._check_v3_clear_acceptance(candidate)
        map_store._check_tickets(
            map_dir,
            state="clear",
            schema_version=candidate.frontmatter.schema_version,
        )
    except (map_store.SchemaViolation, map_store.MapStoreError):
        return False
    return True


def _store_snapshot(map_dir: Path) -> dict[str, bytes]:
    """Read every regular descendant without accepting filesystem aliases."""
    snapshot: dict[str, bytes] = {}
    for root, directories, files in os.walk(map_dir, followlinks=False):
        root_path = Path(root)
        for name in list(directories):
            candidate = root_path / name
            if stat.S_ISLNK(candidate.lstat().st_mode):
                raise CloseTransactionError(
                    f"retirement read set contains a symlink: {candidate}"
                )
        for name in files:
            candidate = root_path / name
            mode = candidate.lstat().st_mode
            if not stat.S_ISREG(mode):
                raise CloseTransactionError(
                    f"retirement read set contains a non-regular file: {candidate}"
                )
            snapshot[candidate.relative_to(map_dir).as_posix()] = candidate.read_bytes()
    return snapshot


def _retirement_snapshot(map_dir: Path, repo_root: Path) -> dict[str, bytes]:
    """Snapshot Map descendants plus reciprocal Briefs in the validation read set."""
    snapshot = {
        str((map_dir / relative).resolve(strict=False)): content
        for relative, content in _store_snapshot(map_dir).items()
    }
    tickets_dir = map_dir / "tickets"
    for ticket_path in sorted(tickets_dir.glob("*.md")):
        try:
            fields, _ = map_store.parse_frontmatter(
                ticket_path.read_text(encoding="utf-8")
            )
        except (OSError, map_store.SchemaViolation) as exc:
            raise CloseTransactionError(f"cannot snapshot ticket binding: {exc}") from exc
        brief = fields.get("brief")
        if brief is None:
            continue
        brief_path = repo_root / brief
        try:
            map_store._assert_no_symlink_components(brief_path)
            map_store._assert_contained(repo_root, brief_path)
            snapshot[str(brief_path.resolve(strict=True))] = brief_path.read_bytes()
        except (OSError, map_store.SchemaViolation) as exc:
            raise CloseTransactionError(f"cannot snapshot reciprocal Brief: {exc}") from exc
    return snapshot


def _close_journal_is_complete(map_dir: Path, journal: Path) -> bool:
    """Return whether a retained close journal's complete effects are visible."""
    try:
        intent = json.loads(journal.read_text(encoding="utf-8"))
        if intent.get("kind") == "claim":
            ticket = map_store.read_ticket(
                map_dir / "tickets" / f"{intent['ticket_slug']}.md"
            )
            return (
                intent.get("version") == 1
                and ticket.frontmatter.status == "claimed"
                and ticket.frontmatter.claim
                == f"{intent['owner']}, {intent['claimed_on']}"
            )
        if intent.get("kind") == "update-blockers":
            ticket = map_store.read_ticket(
                map_dir / "tickets" / f"{intent['ticket_slug']}.md"
            )
            return (
                intent.get("version") == 1
                and ticket.frontmatter.blocked_by == intent.get("blockers")
            )
        slug = intent["ticket_slug"]
        gist = intent["gist"]
        resolution = intent["resolution"]
        routes = intent["routes"]
        if (
            intent.get("version") != 1
            or intent.get("prepared") is not True
            or not isinstance(slug, str)
            or not isinstance(gist, str)
            or not isinstance(resolution, str)
            or not isinstance(routes, list)
            or journal.name != f"close-{slug}.json"
        ):
            return False
        ticket = map_store.read_ticket(map_dir / "tickets" / f"{slug}.md")
        if ticket.frontmatter.status != "closed" or (
            ticket.resolution or ""
        ).strip() != resolution.strip():
            return False
        map_text = (map_dir / "MAP.md").read_text(encoding="utf-8")
        if f"- {gist.strip()} (tickets/{slug}.md)" not in map_text:
            return False
        for route in routes:
            if not isinstance(route, dict):
                return False
            destination = route.get("destination")
            text = route.get("text")
            if not isinstance(text, str):
                return False
            if destination == "fog":
                if f"- {route.get('fog_id')}: {text}" not in map_text:
                    return False
            elif destination == "out-of-scope":
                if f"- {text}" not in map_text:
                    return False
            elif destination == "ticket":
                routed = map_dir / "tickets" / f"{route.get('ticket_slug')}.md"
                if not routed.is_file() or routed.read_text(encoding="utf-8") != _open_ticket_text(route):
                    return False
            else:
                return False
        return True
    except (KeyError, OSError, json.JSONDecodeError, map_store.MapStoreError, map_store.SchemaViolation):
        return False


def _validate_retirement_snapshot(map_dir: Path, repo_root: Path) -> None:
    """Apply all currently public store invariants to one retirement read set."""
    import check_map_links
    import delivery_binding

    transaction_dir = map_dir / ".transactions"
    if transaction_dir.exists():
        incomplete = [
            path.name
            for path in sorted(transaction_dir.iterdir())
            if not path.is_file() or not _close_journal_is_complete(map_dir, path)
        ]
        if incomplete:
            raise CloseTransactionError(
                "retirement refuses incomplete recoverable operation(s) "
                + ", ".join(incomplete)
                + "; repair them first"
            )
    code, message = map_store.validate(map_dir, repo_root=repo_root)
    if code != 0:
        raise CloseTransactionError(f"retirement refuses broken Map invariants: {message}")
    link_code, link_message = check_map_links.check_links(map_dir)
    if link_code != 0:
        raise CloseTransactionError(
            f"retirement refuses broken gist relationships: {link_message}"
        )

    doc = map_store.read_map(map_dir)
    fog_ids = {entry.id for entry in doc.fog_entries}
    graduated: dict[str, list[str]] = {}
    closed_links: dict[str, int] = {}
    for decision in doc.decisions:
        closed_links[decision.ticket_link] = closed_links.get(decision.ticket_link, 0) + 1
    for ticket_path in sorted((map_dir / "tickets").glob("*.md")):
        ticket = map_store.read_ticket(ticket_path)
        if ticket.frontmatter.graduated_from:
            graduated.setdefault(ticket.frontmatter.graduated_from, []).append(
                ticket_path.name
            )
        if ticket.frontmatter.status == "closed":
            link = f"tickets/{ticket_path.name}"
            if closed_links.get(link, 0) != 1:
                raise CloseTransactionError(
                    f"retirement requires exactly one gist for closed ticket {ticket_path.name}"
                )
        if ticket.frontmatter.type == "delivery":
            binding_code, binding_message = delivery_binding.validate(
                ticket_path, repo_root=repo_root
            )
            if binding_code != 0:
                raise CloseTransactionError(
                    f"retirement refuses broken delivery binding: {binding_message}"
                )
    overlap = sorted(fog_ids.intersection(graduated))
    if overlap:
        raise CloseTransactionError(
            "retirement refuses partial fog graduation for " + ", ".join(overlap)
        )
    duplicates = sorted(key for key, owners in graduated.items() if len(owners) != 1)
    if duplicates:
        raise CloseTransactionError(
            "retirement refuses duplicated fog graduation for "
            + ", ".join(duplicates)
        )


@dataclass(frozen=True)
class RetirementReadiness:
    """Validated immutable read-set token for one archive transition."""

    map_dir: Path
    repo_root: Path
    snapshot: tuple[tuple[str, bytes], ...]


def prepare_retirement(map_dir: Path, repo_root: Path) -> RetirementReadiness:
    """Validate all retirement invariants and bind them to one stable read set."""
    map_dir = Path(map_dir)
    repo_root = Path(repo_root)
    for path in (repo_root, map_dir, map_dir / "MAP.md", map_dir / "tickets"):
        _assert_no_symlink_components(path)
        try:
            path.resolve(strict=False).relative_to(repo_root.resolve(strict=True))
        except (OSError, ValueError) as exc:
            raise CloseTransactionError(
                f"retirement path escapes repository: {path}"
            ) from exc
    initial = _retirement_snapshot(map_dir, repo_root)
    _validate_retirement_snapshot(map_dir, repo_root)
    _before_retirement_stability_check()
    if _retirement_snapshot(map_dir, repo_root) != initial:
        raise CloseTransactionError(
            "retirement requires one stable snapshot; a read-set file changed"
        )
    return RetirementReadiness(map_dir, repo_root, tuple(sorted(initial.items())))


def _commit_retirement(
    readiness: RetirementReadiness,
    *,
    ratified_by: str | None,
    ratified_on: str | None,
    reason: str | None,
) -> None:
    map_dir = readiness.map_dir
    repo_root = readiness.repo_root
    _before_retirement_transition()
    doc = map_store.read_map(map_dir)
    if doc.frontmatter.state == "clear":
        _before_archive_state_replace()
    expected = dict(readiness.snapshot)
    if _retirement_snapshot(map_dir, repo_root) != expected:
        raise CloseTransactionError(
            "retirement requires one stable snapshot at the transition boundary"
        )

    map_path = map_dir / "MAP.md"
    original = map_path.read_text(encoding="utf-8")
    try:
        if doc.frontmatter.state == "clear":
            candidate = map_store.archive_candidate(original)
        else:
            candidate = map_store.retirement_candidate(
                original,
                current_state=doc.frontmatter.state,
                ratified_by=ratified_by or "",
                ratified_on=ratified_on or "",
                reason=reason or "",
            )
    except map_store.SchemaViolation as exc:
        raise CloseTransactionError(str(exc)) from exc
    _before_retirement_replace()
    _atomic_write(map_path, candidate, expected=original.encode("utf-8"))
    try:
        if doc.frontmatter.state == "clear":
            _after_archive_state_replace()
        committed = dict(readiness.snapshot)
        committed[str(map_path.resolve(strict=True))] = candidate.encode("utf-8")
        if _retirement_snapshot(map_dir, repo_root) != committed:
            raise CloseTransactionError(
                "retirement read set changed during state replacement"
            )
        _validate_retirement_snapshot(map_dir, repo_root)
    except Exception as exc:
        try:
            _atomic_write(
                map_path,
                original,
                expected=candidate.encode("utf-8"),
            )
        except Exception as rollback_exc:
            evidence = {
                "action": "recovery-required",
                "cause": str(exc),
                "map_path": "MAP.md",
                "rollback_error": str(rollback_exc),
                "status": "BROKEN",
            }
            evidence_path = map_dir / ".transactions" / "retirement-recovery.json"
            evidence_error: str | None = None
            try:
                map_store._atomic_write(
                    evidence_path,
                    json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                )
            except Exception as evidence_exc:
                evidence_error = str(evidence_exc)
            suffix = (
                f"; durable evidence unavailable: {evidence_error}"
                if evidence_error is not None
                else f"; evidence: {evidence_path}"
            )
            raise CloseTransactionError(
                "BROKEN recovery-required: archive state could not be rolled back"
                + suffix
            ) from rollback_exc
        if isinstance(exc, CloseTransactionError):
            raise
        raise CloseTransactionError(
            f"archive post-write validation failed; MAP state restored: {exc}"
        ) from exc


def archive_map_transition(map_dir: Path, *, repo_root: Path) -> None:
    """Archive a clear Map through the same stable-readiness transaction."""
    readiness = prepare_retirement(map_dir, repo_root)
    if map_store.read_map(map_dir).frontmatter.state != "clear":
        raise CloseTransactionError("archive transition requires a clear schema-v3 Map")
    _commit_retirement(
        readiness, ratified_by=None, ratified_on=None, reason=None
    )


def retire_map(
    map_dir: Path,
    *,
    ratified_by: str,
    ratified_on: str,
    reason: str,
    repo_root: Path,
) -> None:
    """Retire one Map only if its complete validated read set stays stable."""
    readiness = prepare_retirement(map_dir, repo_root)
    _commit_retirement(
        readiness,
        ratified_by=ratified_by,
        ratified_on=ratified_on,
        reason=reason,
    )


def close_and_rechart(
    map_dir: Path,
    ticket_slug: str,
    *,
    gist: str,
    resolution: str,
    unknowns: list[UnknownRoute],
) -> CloseResult:
    """Close one claimed v3 ticket after making all chart effects recoverable."""
    map_dir = Path(map_dir)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ticket_slug):
        raise CloseTransactionError("ticket_slug is not a safe slug")
    if not gist.strip() or not resolution.strip():
        raise CloseTransactionError("gist and resolution must not be empty")
    _validate_routes(unknowns)
    ticket_path, journal_path = _validate_paths(map_dir, ticket_slug, unknowns)
    map_doc = map_store.read_map(map_dir)
    if map_doc.frontmatter.schema_version != 3 or map_doc.frontmatter.state != "active":
        raise CloseTransactionError("close-and-rechart requires an active schema-v3 map")
    ticket = map_store.read_ticket(ticket_path)
    ticket_original = ticket_path.read_bytes()
    terminal: str | None = None
    if ticket.frontmatter.status == "claimed":
        _validate_authoritative_ticket(ticket, closed=False)
        terminal = _terminal_text(ticket_path.read_text(encoding="utf-8"), resolution)
        _validate_terminal_candidate(ticket_path, terminal)
    elif ticket.frontmatter.status == "closed":
        if not journal_path.is_file():
            raise CloseTransactionError(
                "closed source may resume only from an existing prepared journal"
            )
        _validate_authoritative_ticket(ticket, closed=True)
        if (ticket.resolution or "").strip() != resolution.strip():
            raise CloseTransactionError(
                "closed source resolution conflicts with the prepared request"
            )
    else:
        raise CloseTransactionError("source ticket must be claimed before close")

    new_operation = not journal_path.exists()
    observed = capture_revision(map_dir) if new_operation else None
    _assert_supported_filesystem(map_dir)
    if observed is not None:
        _require_revision(map_dir, observed)

    _, prepared = _load_or_prepare_intent(
        map_dir, ticket_slug, gist.strip(), resolution.strip(), unknowns, map_doc
    )
    routes = prepared["routes"]
    assert isinstance(routes, list)
    _apply_map_effects(map_dir, ticket_slug, gist.strip(), routes)

    if ticket.frontmatter.status == "closed":
        expected_resolution = resolution.strip()
        if (ticket.resolution or "").strip() != expected_resolution:
            raise CloseTransactionError("closed source ticket conflicts with retry")
        return CloseResult(len(unknowns), _assess_clear(map_dir))
    assert terminal is not None
    _before_terminalize()
    _atomic_write(ticket_path, terminal, expected=ticket_original)
    return CloseResult(len(unknowns), _assess_clear(map_dir))
