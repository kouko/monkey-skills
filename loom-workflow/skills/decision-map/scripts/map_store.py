#!/usr/bin/env python3
"""The shared reader for a decision-map store (MAP.md + tickets/).

Grammar SSOT: `loom-workflow/skills/decision-map/references/
map-format.md` — this module is the compatibility facade for the
store's bytes (§Command surface); parsing lives in map_documents
and validation rules live in map_validation.
Every sibling checker
(`check_map_links.py`, `check_map_fog.py`) and
`map_init.py` import this module rather than re-reading MAP.md or a
ticket file itself.

CLI: `map_store.py validate <map-dir> --repo-root <path>` — the sole
check behind map-format.md's §Live-map criterion "checker-valid" half.
Exit 0 clean / 1 operational error / 2 structural violation, the
canonical arg shape shared by every §Command surface script
(`--repo-root` default: `git rev-parse --show-toplevel` of the
target's directory, falling back to cwd — same resolution precedent as
`check_onramp_choice.py`).

Stdlib only.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from enum import Enum
from pathlib import Path

import map_lock
import map_validation
# Keep existing validation imports available through the store facade.
from map_validation import (
    MIN_SUPPORTED_SCHEMA_VERSION,
    SUPPORTED_SCHEMA_VERSION,
    VALID_MAP_STATES,
    LIVE_MAP_STATES,
    V2_TICKET_TYPES,
    V3_TICKET_TYPES,
    HITL_TICKET_TYPES,
    RATIFIED_MAP_STATES,
    V2_TICKET_STATUSES,
    V3_TICKET_STATUSES,
    V3_TICKET_FRONTMATTER_FIELDS,
    REQUIRED_SECTIONS,
    _COMMIT_EVIDENCE,
    _PR_EVIDENCE,
    _ARTIFACT_PATH_EVIDENCE,
    _has_delivery_evidence,
    _SAFE_SLUG,
    _DATED_HUMAN,
    _check_schema_version,
    _has_user_ratified_line,
    _has_resolution_field,
    _has_named_dated_user_ratification,
    _check_v3_ticket_closure_evidence,
    _check_v3_ticket_withdrawal,
    _check_v3_ticket_frontmatter,
    _check_map_structure,
    _da_evidence_is_resolvable,
    _check_destination_acceptance,
    _check_v3_clear_acceptance,
    _check_blocked_by,
)
import map_persistence
from map_persistence import (
    AtomicExchangeUnsupported,
    AtomicExchangeBroken,
    assert_no_symlink_components as _assert_no_symlink_components,
    assert_contained as _assert_contained,
    exchange_paths as _exchange_paths,
    fsync_directory as _fsync_directory,
    _before_atomic_exchange,
    _before_atomic_restore,
)
# Re-export parser objects, including existing private imports, for callers.
from map_documents import (
    _SECTION_HEADING,
    _FOG_ENTRY,
    _DECISION_LINE,
    _DA_ENTRY,
    _DA_SHAPED_BULLET,
    _RETIRED_DA,
    SchemaViolation,
    parse_frontmatter,
    MapFrontmatter,
    FogEntry,
    DecisionLine,
    DestinationAcceptance,
    MapDocument,
    _parse_map_frontmatter,
    _split_sections,
    _parse_fog_entries,
    _parse_decisions,
    _parse_out_of_scope,
    _parse_destination_acceptance,
    _parse_retired_da_ids,
    parse_map_document,
    TicketFrontmatter,
    TicketDocument,
    _null_or,
    _parse_ticket_frontmatter,
    _SECTION_HEADING_TEMPLATE,
    _parse_ticket_section,
    _parse_resolution,
    parse_ticket_document,
)


class LiveMapResult(str, Enum):
    LIVE = "live"
    NOT_PRESENT = "not-present"
    BROKEN = "broken"


class MapStoreError(Exception):
    """Operational error: target missing/unreadable — exit 1."""


def read_map(map_dir: Path) -> MapDocument:
    """Read and parse `<map_dir>/MAP.md`. Raises MapStoreError if the
    map directory or MAP.md is missing/unreadable."""
    map_md = Path(map_dir) / "MAP.md"
    try:
        text = map_md.read_text(encoding="utf-8")
    except OSError as exc:
        raise MapStoreError(f"cannot read {map_md}: {exc}") from exc
    return parse_map_document(text, map_md)


# --- tickets ----------------------------------------------------------


def read_ticket(ticket_path: Path) -> TicketDocument:
    ticket_path = Path(ticket_path)
    try:
        text = ticket_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MapStoreError(f"cannot read {ticket_path}: {exc}") from exc
    return parse_ticket_document(text, ticket_path)


def find_governing_map_md(ticket_path: Path) -> Path:
    """Walk up from a ticket's directory to the MAP.md governing it
    (map-format.md §Schema versioning's walk-up rule). Raises
    MapStoreError if no MAP.md is found above the ticket."""
    current = Path(ticket_path).resolve().parent
    for _ in range(64):
        candidate = current / "MAP.md"
        if candidate.is_file():
            return candidate
        if current.parent == current:
            break
        current = current.parent
    raise MapStoreError(
        f"no governing MAP.md found by walking up from {ticket_path}"
    )


def resolve_schema_version(ticket_path: Path) -> int:
    """The schema_version governing `ticket_path`, resolved by walking
    up to that map's MAP.md and reading its frontmatter — never
    assumed, never required on the ticket itself (map-format.md
    §Schema versioning)."""
    map_md = find_governing_map_md(ticket_path)
    try:
        text = map_md.read_text(encoding="utf-8")
    except OSError as exc:
        raise MapStoreError(f"cannot read {map_md}: {exc}") from exc
    fields, _ = parse_frontmatter(text)
    if "schema_version" not in fields:
        raise SchemaViolation(f"{map_md} frontmatter is missing 'schema_version'")
    try:
        return int(fields["schema_version"])
    except ValueError as exc:
        raise SchemaViolation(
            f"{map_md} 'schema_version' is not an integer: "
            f"{fields['schema_version']!r}"
        ) from exc


# --- repo-root resolution (shared precedent) ----------------------------


def resolve_repo_root(explicit: str | Path | None, start_dir: Path) -> Path:
    """`--repo-root` resolution precedent shared by every §Command
    surface script: the explicit flag if given, else `git rev-parse
    --show-toplevel` of `start_dir`, falling back to cwd
    (check_onramp_choice.py's `_resolve_repo_root`)."""
    if explicit is not None:
        return Path(explicit)
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return Path.cwd()


# --- historical-state operations --------------------------------------


def _atomic_write(path: Path, text: str, *, expected: bytes | None = None) -> None:
    # Keep legacy fault-injection callbacks local to this facade.
    map_persistence.AtomicWriter(
        exchange=_exchange_paths,
        sync_directory=_fsync_directory,
        before_exchange=_before_atomic_exchange,
        before_restore=_before_atomic_restore,
    ).write(path, text, expected=expected)


def atomic_write(path: Path, text: str, *, expected: bytes | None = None) -> None:
    """Public writer bridge retaining the existing monkeypatch boundary."""
    _atomic_write(path, text, expected=expected)


def _append_section_fields(text: str, section: str, fields: list[str]) -> str:
    lines = text.splitlines()
    heading = f"## {section}"
    matches = [index for index, line in enumerate(lines) if line.strip() == heading]
    if len(matches) != 1:
        raise SchemaViolation(f"MAP.md must contain exactly one {heading!r}")
    start = matches[0] + 1
    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    while end > start and not lines[end - 1].strip():
        end -= 1
    insertion = ([] if end == start else [""]) + fields
    lines[end:end] = insertion
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def require_work_mutable(map_dir: Path, operation: str) -> MapDocument:
    """Guard a work-through mutation against immutable historical Maps."""
    if operation not in {
        "add", "claim", "bind", "resolve", "graduate", "close", "clear", "withdraw", "edit"
    }:
        raise SchemaViolation(f"unsupported work mutation: {operation!r}")
    doc = read_map(Path(map_dir))
    if doc.frontmatter.schema_version != 3:
        raise SchemaViolation("historical-state operations require schema_version 3")
    if doc.frontmatter.state == "charting":
        raise SchemaViolation(
            f"cannot {operation} work while Map is charting; ratify and activate "
            "the Destination first"
        )
    if doc.frontmatter.state in {"clear", "archived"}:
        raise SchemaViolation(
            f"cannot {operation} work in immutable {doc.frontmatter.state} Map"
        )
    return doc


def require_ticket_mutable(
    map_dir: Path, ticket_slug: str, operation: str
) -> TicketDocument:
    """Guard one ticket mutation without changing any persisted bytes."""
    map_dir = Path(map_dir)
    if not _SAFE_SLUG.fullmatch(ticket_slug):
        raise SchemaViolation("ticket slug must use lowercase letters, digits, and hyphens")
    ticket_path = map_dir / "tickets" / f"{ticket_slug}.md"
    for path in (map_dir, map_dir / "tickets", ticket_path):
        _assert_no_symlink_components(path)
        try:
            path.resolve(strict=False).relative_to(map_dir.resolve(strict=True))
        except (OSError, ValueError) as exc:
            raise SchemaViolation(f"ticket path escapes Map: {path}") from exc
    ticket = read_ticket(ticket_path)
    if ticket.frontmatter.status in {"closed", "withdrawn"}:
        raise SchemaViolation(
            f"cannot {operation} {ticket.frontmatter.status} ticket; preserve it "
            "byte-identically and record corrections in new fog or a follow-up ticket"
        )
    require_work_mutable(map_dir, operation)
    return ticket


def record_active_regression(
    map_dir: Path,
    closed_delivery_slug: str,
    *,
    summary: str,
    followup_type: str,
    followup_slug: str,
) -> Path:
    """Record an active regression under the shared Map writer lock."""
    try:
        with map_lock.map_writer_lock(map_dir):
            return _record_active_regression_locked(
                map_dir,
                closed_delivery_slug,
                summary=summary,
                followup_type=followup_type,
                followup_slug=followup_slug,
            )
    except map_lock.MapLockError as exc:
        raise SchemaViolation(str(exc)) from exc


def _record_active_regression_locked(
    map_dir: Path,
    closed_delivery_slug: str,
    *,
    summary: str,
    followup_type: str,
    followup_slug: str,
) -> Path:
    """Create the follow-up after the caller acquires the writer lock."""
    map_dir = Path(map_dir)
    doc = require_work_mutable(map_dir, "add")
    if doc.frontmatter.state != "active":
        raise SchemaViolation("regression follow-up requires an active Map")
    if not summary.strip():
        raise SchemaViolation("regression summary must not be empty")
    if followup_type not in V3_TICKET_TYPES:
        raise SchemaViolation(
            f"follow-up type must be one of {sorted(V3_TICKET_TYPES)}"
        )
    if not _SAFE_SLUG.fullmatch(closed_delivery_slug) or not _SAFE_SLUG.fullmatch(
        followup_slug
    ):
        raise SchemaViolation("ticket slugs must use lowercase letters, digits, and hyphens")

    tickets_dir = map_dir / "tickets"
    source_path = tickets_dir / f"{closed_delivery_slug}.md"
    followup_path = tickets_dir / f"{followup_slug}.md"
    for path in (map_dir, tickets_dir, source_path, followup_path):
        _assert_no_symlink_components(path)
        try:
            path.resolve(strict=False).relative_to(map_dir.resolve(strict=True))
        except (OSError, ValueError) as exc:
            raise SchemaViolation(f"ticket path escapes Map: {path}") from exc
    source = read_ticket(source_path)
    if (
        source.frontmatter.type != "delivery"
        or source.frontmatter.status != "closed"
    ):
        raise SchemaViolation("regression source must be a closed delivery ticket")
    if followup_path.exists():
        raise SchemaViolation(f"follow-up ticket already exists: {followup_path.name}")

    ticket_text = (
        "---\n"
        f"type: {followup_type}\n"
        "status: open\n"
        "claim: null\n"
        "graduated-from: null\n"
        "---\n\n"
        f"Regression follow-up to tickets/{closed_delivery_slug}.md.\n\n"
        f"{summary.strip()}\n\n"
        "## Resolution\n\n"
    )
    _atomic_write(followup_path, ticket_text)
    return followup_path


def retirement_candidate(
    text: str,
    *,
    current_state: str,
    ratified_by: str,
    ratified_on: str,
    reason: str,
) -> str:
    """Build the ratified charting/active retirement bytes without writing."""
    if current_state not in {"charting", "active"}:
        raise SchemaViolation("ratified retirement requires charting or active state")
    human_and_date = f"{ratified_by.strip()}, {ratified_on.strip()}"
    if not _DATED_HUMAN.fullmatch(human_and_date):
        raise SchemaViolation("retirement requires a named human and YYYY-MM-DD date")
    if not reason.strip():
        raise SchemaViolation("retirement requires a non-empty reason")
    state_field = f"state: {current_state}"
    if text.count(state_field) != 1:
        raise SchemaViolation("MAP.md must contain exactly one current state field")
    archived = text.replace(state_field, "state: archived", 1)
    return _append_section_fields(
        archived,
        "Notes",
        [
            f"retirement-ratified: {human_and_date}",
            f"retirement-reason: {reason.strip()}",
        ],
    )


def archive_candidate(text: str) -> str:
    """Build the clear-to-archived MAP.md bytes without moving identity."""
    if text.count("state: clear") != 1:
        raise SchemaViolation("MAP.md must contain exactly one clear state field")
    return text.replace("state: clear", "state: archived", 1)


def create_successor_map(
    predecessor_dir: Path,
    successor_map_id: str,
    *,
    reason: str,
    repo_root: Path,
) -> Path:
    """Create new charting work while preserving a clear/archived predecessor."""
    predecessor_dir = Path(predecessor_dir)
    repo_root = Path(repo_root)
    if not _SAFE_SLUG.fullmatch(successor_map_id):
        raise SchemaViolation("successor map-id must be a safe lowercase slug")
    if not reason.strip():
        raise SchemaViolation("successor reason must not be empty")
    code, message = validate(predecessor_dir, repo_root=repo_root)
    if code != 0:
        raise SchemaViolation(f"cannot continue from invalid predecessor: {message}")
    predecessor = read_map(predecessor_dir)
    if predecessor.frontmatter.schema_version != 3 or predecessor.frontmatter.state not in {
        "clear",
        "archived",
    }:
        raise SchemaViolation("successor requires a clear or archived schema-v3 predecessor")

    maps_dir = repo_root / "docs" / "loom" / "maps"
    successor = maps_dir / successor_map_id
    predecessor_map = predecessor_dir / "MAP.md"
    for path in (repo_root, maps_dir, successor, predecessor_map):
        _assert_no_symlink_components(path)
        _assert_contained(repo_root, path)
    if successor.exists():
        raise SchemaViolation(f"successor Map already exists: {successor_map_id}")
    predecessor_ref = predecessor_map.resolve(strict=True).relative_to(
        repo_root.resolve(strict=True)
    ).as_posix()
    map_text = (
        "---\n"
        f"map-id: {successor_map_id}\n"
        "schema_version: 3\n"
        "state: charting\n"
        "---\n\n"
        "## Destination\n\n"
        f"Continue the outcome after renewed work: {reason.strip()}\n\n"
        "## Notes\n\n"
        f"predecessor-map: {predecessor_ref}\n\n"
        "## Decisions-so-far\n\n"
        "## Not-yet-specified (fog)\n\n"
        f"- F-1: {reason.strip()}\n\n"
        "## Out-of-scope\n\n"
    )
    successor.mkdir(parents=False)
    (successor / "tickets").mkdir()
    _atomic_write(successor / "tickets" / ".gitkeep", "")
    _atomic_write(successor / "MAP.md", map_text)
    return successor


# --- validate ---------------------------------------------------------


def _check_tickets(map_dir: Path, state: str, schema_version: int) -> None:
    map_validation._check_tickets(
        map_dir, state, schema_version, read_ticket=read_ticket
    )


def _check_monotonic_relations(map_dir: Path, doc: MapDocument) -> None:
    map_validation._check_monotonic_relations(
        map_dir, doc, read_ticket=read_ticket
    )


def validate(target: Path, repo_root: Path | None = None) -> tuple[int, str]:
    """Validate a decision-map store at `target` (a map directory).

    Returns `(exit_code, message)`: 0 clean, 1 operational error
    (target missing/unreadable), 2 a structural or schema-version
    violation — the exit-code split map-format.md §Command surface
    pins for every checker in the family.

    `repo_root` resolves objective Destination acceptance evidence
    pointers (R3c); when omitted it falls back to `resolve_repo_root`
    from `target`'s directory, the same precedent every other
    §Command surface script uses."""
    map_dir = Path(target)
    if not map_dir.is_dir():
        return 1, f"map directory not found: {map_dir}"
    resolved_repo_root = (
        Path(repo_root) if repo_root is not None else resolve_repo_root(None, map_dir)
    )
    try:
        doc = read_map(map_dir)
    except MapStoreError as exc:
        return 1, str(exc)
    except SchemaViolation as exc:
        return 2, str(exc)

    try:
        map_validation.validate_document(
            map_dir, doc, resolved_repo_root, read_ticket=read_ticket
        )
    except SchemaViolation as exc:
        return 2, str(exc)
    except MapStoreError as exc:
        return 1, str(exc)

    return 0, f"{map_dir} is a valid decision-map store"


def is_live_map(
    target: Path, repo_root: Path | None = None
) -> LiveMapResult:
    """Return the explicit map-format.md §Live-map result.

    Only an absent target is ``not-present``. Any existing target that
    fails validation, or whose valid state is not live, is ``broken``
    so callers cannot silently treat malformed maps as absent.

    `repo_root` is accepted for arg-shape parity with the other
    §Command surface scripts; this function does not use it."""
    if not Path(target).exists():
        return LiveMapResult.NOT_PRESENT
    code, _ = validate(target, repo_root=repo_root)
    if code != 0:
        return LiveMapResult.BROKEN
    doc = read_map(target)
    if doc.frontmatter.state in LIVE_MAP_STATES:
        return LiveMapResult.LIVE
    return LiveMapResult.BROKEN


# --- CLI -------------------------------------------------------------


def _cmd_validate(args: argparse.Namespace) -> int:
    target = Path(args.target)
    repo_root = resolve_repo_root(args.repo_root, target if target.is_dir() else target.parent)
    code, message = validate(target, repo_root=repo_root)
    if code == 0:
        print(message)
    else:
        print(f"Error: {message}", file=sys.stderr)
    return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read/validate a decision-map store (MAP.md + tickets)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate", help="validate a decision-map store"
    )
    validate_parser.add_argument("target", help="path to the map directory")
    validate_parser.add_argument(
        "--repo-root",
        default=None,
        help="repo root (default: git rev-parse --show-toplevel of the "
        "target's directory, falling back to cwd)",
    )
    validate_parser.set_defaults(func=_cmd_validate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
