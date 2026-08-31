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
import subprocess
import tempfile
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import delivery_evidence
import map_lifecycle
import map_lock
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


@dataclass(frozen=True)
class DeliveryClosureInputs:
    """Current authoritative inputs re-evaluated immediately before close."""

    brief_text: str
    plan_text: str
    acceptance_satisfied: bool
    review_head: str
    verification_head: str
    pr: str
    pr_roles: tuple[delivery_evidence.PRRole, ...] | None = None
    pr_owners: dict[str, str] | None = None
    ownership_complete: bool = False
    artifact_probe: delivery_evidence.ArtifactProbeEvidence | None = None
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run


def _before_terminalize() -> None:
    """Test seam immediately before the final, terminal ticket write."""


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


def _require_valid_store(map_dir: Path) -> None:
    code, message = map_store.validate(map_dir)
    if code != 0:
        raise CloseTransactionError(
            f"transaction final validation failed: {message}"
        )


@contextmanager
def _transaction_lock(map_dir: Path):
    """Translate the shared lock's refusal into this operation's domain."""
    try:
        with map_lock.map_writer_lock(map_dir):
            yield
    except map_lock.MapLockError as exc:
        raise CloseTransactionError(str(exc)) from exc


@contextmanager
def serialize_map_mutation(map_dir: Path):
    """Expose the shared writer boundary to map_store topology mutations."""
    with _transaction_lock(map_dir):
        yield


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
    """Claim one unblocked frontier ticket under the Map writer lock."""
    with _transaction_lock(map_dir):
        return _claim_ticket_locked(
            map_dir,
            ticket_slug,
            owner=owner,
            claimed_on=claimed_on,
            operation_id=operation_id,
            expected_revision=expected_revision,
        )


def _claim_ticket_locked(
    map_dir: Path,
    ticket_slug: str,
    *,
    owner: str,
    claimed_on: str,
    operation_id: str,
    expected_revision: StoreRevision,
) -> MutationResult:
    """Claim after the caller acquires the Map writer lock."""
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
            _require_valid_store(map_dir)
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
        _require_revision(map_dir, expected_revision)
    try:
        map_store._atomic_write(ticket_path, updated, expected=original)
    except (OSError, map_store.SchemaViolation) as exc:
        raise CloseTransactionError(str(exc)) from exc
    _require_valid_store(map_dir)
    return MutationResult(True, False)


def update_blockers(
    map_dir: Path,
    ticket_slug: str,
    blockers: list[str],
    *,
    operation_id: str,
    expected_revision: StoreRevision,
) -> MutationResult:
    """Replace blocker edges under the Map writer lock."""
    with _transaction_lock(map_dir):
        return _update_blockers_locked(
            map_dir,
            ticket_slug,
            blockers,
            operation_id=operation_id,
            expected_revision=expected_revision,
        )


def _update_blockers_locked(
    map_dir: Path,
    ticket_slug: str,
    blockers: list[str],
    *,
    operation_id: str,
    expected_revision: StoreRevision,
) -> MutationResult:
    """Replace blocker edges after the caller acquires the writer lock."""
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
            _require_valid_store(map_dir)
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
        _require_revision(map_dir, expected_revision)
    try:
        map_store._atomic_write(ticket_path, updated, expected=original)
    except (OSError, map_store.SchemaViolation) as exc:
        raise CloseTransactionError(str(exc)) from exc
    _require_valid_store(map_dir)
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
    map_lock.assert_no_symlink_components(path, error=CloseTransactionError)


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


def _require_current_delivery_evidence(
    ticket_slug: str,
    ticket: map_store.TicketDocument,
    inputs: DeliveryClosureInputs | None,
) -> None:
    if ticket.frontmatter.type != "delivery":
        return
    if inputs is None:
        raise CloseTransactionError(
            "current delivery policy evidence is required before closure"
        )
    ticket_identity = f"tickets/{ticket_slug}.md"
    readiness = delivery_evidence.evaluate_closure(
        brief_text=inputs.brief_text,
        plan_text=inputs.plan_text,
        acceptance_satisfied=inputs.acceptance_satisfied,
        review_head=inputs.review_head,
        verification_head=inputs.verification_head,
        pr=inputs.pr,
        pr_roles=inputs.pr_roles,
        ticket=ticket_identity,
        pr_owners=inputs.pr_owners,
        ownership_complete=inputs.ownership_complete,
        artifact_probe=inputs.artifact_probe,
        run=inputs.run,
    )
    if not readiness.ready:
        raise CloseTransactionError(
            f"current delivery evidence is {readiness.evidence_state}: "
            f"{readiness.reason}"
        )


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


RetirementReadiness = map_lifecycle.RetirementReadiness


def prepare_retirement(map_dir: Path, repo_root: Path) -> RetirementReadiness:
    """Validate retirement through the independent lifecycle orchestrator."""
    try:
        return map_lifecycle.prepare_retirement(map_dir, repo_root)
    except map_lifecycle.LifecycleError as exc:
        raise CloseTransactionError(str(exc)) from exc


def archive_map_transition(map_dir: Path, *, repo_root: Path) -> None:
    """Archive a clear Map through the shared lifecycle orchestrator."""
    try:
        map_lifecycle.archive_map_transition(map_dir, repo_root=repo_root)
    except map_lifecycle.LifecycleError as exc:
        raise CloseTransactionError(str(exc)) from exc


def retire_map(
    map_dir: Path,
    *,
    ratified_by: str,
    ratified_on: str,
    reason: str,
    repo_root: Path,
) -> None:
    """Retire a Map through the shared lifecycle orchestrator."""
    try:
        map_lifecycle.retire_map(
            map_dir,
            ratified_by=ratified_by,
            ratified_on=ratified_on,
            reason=reason,
            repo_root=repo_root,
        )
    except map_lifecycle.LifecycleError as exc:
        raise CloseTransactionError(str(exc)) from exc


def close_and_rechart(
    map_dir: Path,
    ticket_slug: str,
    *,
    gist: str,
    resolution: str,
    unknowns: list[UnknownRoute],
    delivery_closure: DeliveryClosureInputs | None = None,
) -> CloseResult:
    """Close and re-chart under the Map writer lock."""
    with _transaction_lock(map_dir):
        return _close_and_rechart_locked(
            map_dir,
            ticket_slug,
            gist=gist,
            resolution=resolution,
            unknowns=unknowns,
            delivery_closure=delivery_closure,
        )


def _close_and_rechart_locked(
    map_dir: Path,
    ticket_slug: str,
    *,
    gist: str,
    resolution: str,
    unknowns: list[UnknownRoute],
    delivery_closure: DeliveryClosureInputs | None,
) -> CloseResult:
    """Close after the caller acquires the Map writer lock."""
    map_dir = Path(map_dir)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ticket_slug):
        raise CloseTransactionError("ticket_slug is not a safe slug")
    if not gist.strip() or not resolution.strip():
        raise CloseTransactionError("gist and resolution must not be empty")
    _validate_routes(unknowns)
    ticket_path, journal_path = _validate_paths(map_dir, ticket_slug, unknowns)
    observed = capture_revision(map_dir)
    map_doc = map_store.read_map(map_dir)
    if map_doc.frontmatter.schema_version != 3 or map_doc.frontmatter.state != "active":
        raise CloseTransactionError("close-and-rechart requires an active schema-v3 map")
    ticket = map_store.read_ticket(ticket_path)
    ticket_original = ticket_path.read_bytes()
    terminal: str | None = None
    if ticket.frontmatter.status == "claimed":
        code, message = map_store.validate(map_dir)
        if code != 0:
            raise CloseTransactionError(f"cannot close from broken Map: {message}")
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

    _require_current_delivery_evidence(
        ticket_slug, ticket, delivery_closure
    )

    _assert_supported_filesystem(map_dir)
    _require_revision(map_dir, observed)

    _, prepared = _load_or_prepare_intent(
        map_dir, ticket_slug, gist.strip(), resolution.strip(), unknowns, map_doc
    )
    _require_revision(map_dir, observed)
    routes = prepared["routes"]
    assert isinstance(routes, list)
    _apply_map_effects(map_dir, ticket_slug, gist.strip(), routes)

    if ticket.frontmatter.status == "closed":
        expected_resolution = resolution.strip()
        if (ticket.resolution or "").strip() != expected_resolution:
            raise CloseTransactionError("closed source ticket conflicts with retry")
        _require_valid_store(map_dir)
        return CloseResult(len(unknowns), _assess_clear(map_dir))
    assert terminal is not None
    _require_current_delivery_evidence(
        ticket_slug, ticket, delivery_closure
    )
    _before_terminalize()
    _atomic_write(ticket_path, terminal, expected=ticket_original)
    _require_valid_store(map_dir)
    return CloseResult(len(unknowns), _assess_clear(map_dir))
