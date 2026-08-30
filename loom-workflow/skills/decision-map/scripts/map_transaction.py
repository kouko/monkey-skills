#!/usr/bin/env python3
"""Recoverable schema-v3 ticket close-and-rechart operation.

This module owns only REQ-84's ordered close operation.  The broader
read-set conflict and filesystem-assumption contract belongs to REQ-87.
"""

from __future__ import annotations

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
    candidates = [map_dir, map_dir / "MAP.md", tickets_dir, source,
                  map_dir / ".transactions", journal]
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
    _atomic_write(map_path, candidate)
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
        _atomic_write(map_path, original)
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
