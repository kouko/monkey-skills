#!/usr/bin/env python3
"""Recoverable schema-v3 ticket close-and-rechart operation.

This module owns only REQ-84's ordered close operation.  The broader
read-set conflict and filesystem-assumption contract belongs to REQ-87.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
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


def _before_terminalize() -> None:
    """Test seam immediately before the final, terminal ticket write."""


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


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
    if len({(route.destination, route.text, route.ticket_slug) for route in unknowns}) != len(unknowns):
        raise CloseTransactionError("duplicate unknown route in one close request")
    for route in unknowns:
        if not route.text.strip():
            raise CloseTransactionError("unknown route text must not be empty")
        if route.destination not in {"fog", "ticket", "out-of-scope"}:
            raise CloseTransactionError(
                "unknown destination must be fog, ticket, or out-of-scope"
            )
        if route.destination == "ticket":
            if not route.ticket_slug or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", route.ticket_slug):
                raise CloseTransactionError("ticket route requires a safe ticket_slug")
            if route.ticket_type not in map_store.V3_TICKET_TYPES:
                raise CloseTransactionError(
                    "ticket route requires grilling, research, prototype, or delivery"
                )
        elif route.ticket_slug is not None or route.ticket_type is not None:
            raise CloseTransactionError(
                "only a ticket route may carry ticket_slug or ticket_type"
            )


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
    _atomic_write(journal, json.dumps(prepared, indent=2, sort_keys=True) + "\n")
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
    text = map_path.read_text(encoding="utf-8")
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
                _atomic_write(ticket_path, expected)
    if map_path.read_text(encoding="utf-8") != text:
        _atomic_write(map_path, text)


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
    if doc.fog_entries:
        return False
    tickets = [map_store.read_ticket(path) for path in sorted((map_dir / "tickets").glob("*.md"))]
    if any(ticket.frontmatter.status not in {"closed", "withdrawn"} for ticket in tickets):
        return False
    acceptance = [
        [part.strip() for part in line.split("|")]
        for line in doc.sections["Destination"].splitlines()
        if line.strip().startswith("acceptance:")
    ]
    return bool(acceptance) and all(
        len(parts) == 3 and parts[1] == "satisfied" and bool(parts[2])
        for parts in acceptance
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
    map_doc = map_store.read_map(map_dir)
    if map_doc.frontmatter.schema_version != 3 or map_doc.frontmatter.state != "active":
        raise CloseTransactionError("close-and-rechart requires an active schema-v3 map")
    ticket_path = map_dir / "tickets" / f"{ticket_slug}.md"
    ticket = map_store.read_ticket(ticket_path)
    terminal: str | None = None
    if ticket.frontmatter.status == "claimed":
        terminal = _terminal_text(ticket_path.read_text(encoding="utf-8"), resolution)
        _validate_terminal_candidate(ticket_path, terminal)
    elif ticket.frontmatter.status != "closed":
        raise CloseTransactionError("source ticket must be claimed before close")

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
    _atomic_write(ticket_path, terminal)
    return CloseResult(len(unknowns), _assess_clear(map_dir))
