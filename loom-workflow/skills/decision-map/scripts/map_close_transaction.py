"""Close/rechart effects and evidence checks inside the caller-owned writer lock.

The facade supplies shared safety primitives and fault-injection seams explicitly;
this module never imports the facade at runtime.
"""

from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING

import delivery_evidence
import map_store

if TYPE_CHECKING:
    from map_transaction import UnknownRoute, CloseResult, DeliveryClosureInputs


def _section_bounds(
    transaction: ModuleType, lines: list[str], name: str
) -> tuple[int, int]:
    heading = f"## {name}"
    matches = [index for index, line in enumerate(lines) if line.strip() == heading]
    if len(matches) != 1:
        raise transaction.CloseTransactionError(f"MAP.md must contain exactly one {heading!r}")
    start = matches[0] + 1
    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return start, end


def _append_section_line(
    transaction: ModuleType, text: str, section: str, line: str
) -> str:
    lines = text.splitlines()
    start, end = _section_bounds(transaction, lines, section)
    if line in (candidate.strip() for candidate in lines[start:end]):
        return text
    while end > start and not lines[end - 1].strip():
        end -= 1
    lines[end:end] = ([""] if end == start else []) + [line]
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def _validate_routes(transaction: ModuleType, unknowns: list[UnknownRoute]) -> None:
    route_keys = {
        (route.destination, route.text, route.ticket_slug) for route in unknowns
    }
    if len(route_keys) != len(unknowns):
        raise transaction.CloseTransactionError("duplicate unknown route in one close request")
    ticket_slugs = [
        route.ticket_slug for route in unknowns if route.destination == "ticket"
    ]
    if len(set(ticket_slugs)) != len(ticket_slugs):
        raise transaction.CloseTransactionError(
            "duplicate ticket_slug in one close request"
        )
    for route in unknowns:
        if not route.text.strip():
            raise transaction.CloseTransactionError("unknown route text must not be empty")
        if route.destination not in {"fog", "ticket", "out-of-scope"}:
            raise transaction.CloseTransactionError(
                "unknown destination must be fog, ticket, or out-of-scope"
            )
        if route.destination == "ticket":
            if not route.ticket_slug or not re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*", route.ticket_slug
            ):
                raise transaction.CloseTransactionError("ticket route requires a safe ticket_slug")
            if route.ticket_type not in map_store.V3_TICKET_TYPES:
                raise transaction.CloseTransactionError(
                    "ticket route requires grilling, research, prototype, or delivery"
                )
        elif route.ticket_slug is not None or route.ticket_type is not None:
            raise transaction.CloseTransactionError(
                "only a ticket route may carry ticket_slug or ticket_type"
            )


def _validate_paths(
    transaction: ModuleType,
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
        transaction._assert_no_symlink_components(candidate)
        transaction._assert_contained(map_dir, candidate)
    return source, journal


def _validate_authoritative_ticket(
    transaction: ModuleType,
    ticket: map_store.TicketDocument, *, closed: bool
) -> None:
    expected_status = "closed" if closed else "claimed"
    if ticket.frontmatter.type not in map_store.V3_TICKET_TYPES:
        raise transaction.CloseTransactionError(
            "source is not an allowed schema-v3 ticket type"
        )
    if ticket.frontmatter.status != expected_status:
        raise transaction.CloseTransactionError(
            f"source ticket must be {expected_status}"
        )
    try:
        map_store._check_v3_ticket_frontmatter(ticket)
        if closed:
            map_store._check_v3_ticket_closure_evidence(ticket)
    except map_store.SchemaViolation as exc:
        raise transaction.CloseTransactionError(
            f"invalid authoritative schema-v3 source: {exc}"
        ) from exc


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
    transaction: ModuleType,
    map_dir: Path,
    ticket_slug: str,
    gist: str,
    routes: list[dict[str, object]],
) -> None:
    map_path = map_dir / "MAP.md"
    original = map_path.read_bytes()
    text = original.decode("utf-8")
    decision = f"- {gist} (tickets/{ticket_slug}.md)"
    text = _append_section_line(transaction, text, "Decisions-so-far", decision)
    for route in routes:
        destination = route["destination"]
        if destination == "fog":
            line = f"- {route['fog_id']}: {route['text']}"
            text = _append_section_line(transaction, text, "Not-yet-specified (fog)", line)
        elif destination == "out-of-scope":
            text = _append_section_line(
                transaction, text, "Out-of-scope", f"- {route['text']}"
            )
        else:
            ticket_path = map_dir / "tickets" / f"{route['ticket_slug']}.md"
            expected = _open_ticket_text(route)
            if ticket_path.exists():
                if ticket_path.read_text(encoding="utf-8") != expected:
                    raise transaction.CloseTransactionError(
                        f"ticket route conflicts with existing {ticket_path.name}"
                    )
            else:
                transaction._exclusive_write(ticket_path, expected)
    if original.decode("utf-8") != text:
        transaction._atomic_write(map_path, text, expected=original)


def _terminal_text(transaction: ModuleType, text: str, resolution: str) -> str:
    if text.count("status: claimed") != 1:
        raise transaction.CloseTransactionError("source ticket must be claimed before close")
    closed = text.replace("status: claimed", "status: closed", 1)
    return closed.rstrip() + "\n\n## Resolution\n\n" + resolution.strip() + "\n"


def _validate_terminal_candidate(
    transaction: ModuleType, ticket_path: Path, text: str
) -> None:
    try:
        candidate = map_store.parse_ticket_document(text, ticket_path)
        map_store._check_v3_ticket_closure_evidence(candidate)
    except map_store.SchemaViolation as exc:
        raise transaction.CloseTransactionError(f"invalid closure evidence: {exc}") from exc


def _require_current_delivery_evidence(
    transaction: ModuleType,
    ticket_slug: str,
    ticket: map_store.TicketDocument,
    inputs: DeliveryClosureInputs | None,
) -> None:
    if ticket.frontmatter.type != "delivery":
        return
    if inputs is None:
        raise transaction.CloseTransactionError(
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
        raise transaction.CloseTransactionError(
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


def _close_and_rechart_locked(
    transaction: ModuleType,
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
        raise transaction.CloseTransactionError("ticket_slug is not a safe slug")
    if not gist.strip() or not resolution.strip():
        raise transaction.CloseTransactionError("gist and resolution must not be empty")
    _validate_routes(transaction, unknowns)
    ticket_path, journal_path = _validate_paths(transaction, map_dir, ticket_slug, unknowns)
    observed = transaction.capture_revision(map_dir)
    map_doc = map_store.read_map(map_dir)
    if map_doc.frontmatter.schema_version != 3 or map_doc.frontmatter.state != "active":
        raise transaction.CloseTransactionError("close-and-rechart requires an active schema-v3 map")
    ticket = map_store.read_ticket(ticket_path)
    ticket_original = ticket_path.read_bytes()
    terminal: str | None = None
    if ticket.frontmatter.status == "claimed":
        code, message = map_store.validate(map_dir)
        if code != 0:
            raise transaction.CloseTransactionError(f"cannot close from broken Map: {message}")
        _validate_authoritative_ticket(transaction, ticket, closed=False)
        terminal = _terminal_text(transaction, ticket_path.read_text(encoding="utf-8"), resolution)
        _validate_terminal_candidate(transaction, ticket_path, terminal)
    elif ticket.frontmatter.status == "closed":
        if not journal_path.is_file():
            raise transaction.CloseTransactionError(
                "closed source may resume only from an existing prepared journal"
            )
        _validate_authoritative_ticket(transaction, ticket, closed=True)
        if (ticket.resolution or "").strip() != resolution.strip():
            raise transaction.CloseTransactionError(
                "closed source resolution conflicts with the prepared request"
            )
    else:
        raise transaction.CloseTransactionError("source ticket must be claimed before close")

    _require_current_delivery_evidence(
        transaction,
        ticket_slug, ticket, delivery_closure
    )

    transaction._assert_supported_filesystem(map_dir)
    transaction._require_revision(map_dir, observed)

    _, prepared = transaction._load_or_prepare_intent(
        map_dir, ticket_slug, gist.strip(), resolution.strip(), unknowns, map_doc
    )
    transaction._require_revision(map_dir, observed)
    routes = prepared["routes"]
    assert isinstance(routes, list)
    _apply_map_effects(transaction, map_dir, ticket_slug, gist.strip(), routes)

    if ticket.frontmatter.status == "closed":
        expected_resolution = resolution.strip()
        if (ticket.resolution or "").strip() != expected_resolution:
            raise transaction.CloseTransactionError("closed source ticket conflicts with retry")
        transaction._require_valid_store(map_dir)
        return transaction.CloseResult(len(unknowns), _assess_clear(map_dir))
    assert terminal is not None
    _require_current_delivery_evidence(
        transaction,
        ticket_slug, ticket, delivery_closure
    )
    transaction._before_terminalize()
    transaction._atomic_write(ticket_path, terminal, expected=ticket_original)
    transaction._require_valid_store(map_dir)
    return transaction.CloseResult(len(unknowns), _assess_clear(map_dir))
