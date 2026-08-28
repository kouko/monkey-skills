#!/usr/bin/env python3
"""The shared reader for a decision-map store (MAP.md + tickets/).

Grammar SSOT: `loom-workflow/skills/decision-map/references/
map-format.md` — this module is the ONLY sanctioned parser of the
store's bytes (§Command surface); every sibling checker
(`check_map_links.py`, `check_map_fog.py`, `map_parts.py`) and
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
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

SUPPORTED_SCHEMA_VERSION = 1

VALID_MAP_STATES = {"charting", "active", "clear", "archived"}
LIVE_MAP_STATES = {"charting", "active"}
VALID_TICKET_TYPES = {"grilling", "research", "task", "prototype"}
VALID_TICKET_STATUSES = {"open", "claimed", "closed"}

REQUIRED_SECTIONS = [
    "Destination",
    "Notes",
    "Decisions-so-far",
    "Not-yet-specified (fog)",
    "Out-of-scope",
    "Parts",
]

_SECTION_HEADING = re.compile(r"^##\s+(.+?)\s*$")
_FOG_ENTRY = re.compile(r"^-\s*(?P<id>F-(?P<n>\d+))\s*:\s*(?P<text>.*)$")
_DECISION_LINE = re.compile(r"^-\s*(?P<gist>.*)\((?P<link>[^()]*)\)\s*$")
_TABLE_ROW = re.compile(r"^\|(.+)\|\s*$")


class MapStoreError(Exception):
    """Operational error: target missing/unreadable — exit 1."""


class SchemaViolation(Exception):
    """Structural/schema-version violation — exit 2."""


# --- generic frontmatter -----------------------------------------------


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Split `text` into its `key: value` frontmatter block (a simple
    dict — no YAML lib, per map-format.md's "simple key: value" note)
    and the body that follows. Raises SchemaViolation if the leading
    `---` fence is missing or unterminated."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SchemaViolation("missing frontmatter opening '---' fence")
    fields: dict[str, str] = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        if line.strip() and ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
        i += 1
    if i >= len(lines):
        raise SchemaViolation("missing frontmatter closing '---' fence")
    body = "\n".join(lines[i + 1:])
    return fields, body


# --- MAP.md ---------------------------------------------------------------


@dataclass
class MapFrontmatter:
    map_id: str
    schema_version: int
    state: str


@dataclass
class FogEntry:
    id: str
    number: int
    text: str


@dataclass
class DecisionLine:
    gist: str
    ticket_link: str


@dataclass
class PartRow:
    name: str
    join_key: str
    status: str


@dataclass
class MapDocument:
    path: Path
    frontmatter: MapFrontmatter
    sections: dict[str, str] = field(default_factory=dict)
    fog_entries: list[FogEntry] = field(default_factory=list)
    decisions: list[DecisionLine] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)
    parts: list[PartRow] = field(default_factory=list)


def _parse_map_frontmatter(fields: dict[str, str]) -> MapFrontmatter:
    for key in ("map-id", "schema_version", "state"):
        if key not in fields:
            raise SchemaViolation(f"MAP.md frontmatter is missing '{key}'")
    try:
        schema_version = int(fields["schema_version"])
    except ValueError as exc:
        raise SchemaViolation(
            f"MAP.md 'schema_version' is not an integer: {fields['schema_version']!r}"
        ) from exc
    return MapFrontmatter(
        map_id=fields["map-id"],
        schema_version=schema_version,
        state=fields["state"],
    )


def _split_sections(body: str) -> dict[str, str]:
    """Split MAP.md's body on `## <name>` headings into {name: raw
    body-text}. Dict insertion order mirrors document order (Python
    dicts preserve insertion order), which `validate`'s order check
    relies on — the parser stays permissive about which sections may
    appear, but never silently folds a repeated heading (last-wins),
    since that would hide real content under a name a reader would
    assume is unique."""
    lines = body.splitlines()
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in lines:
        match = _SECTION_HEADING.match(line)
        if match:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            name = match.group(1).strip()
            if name in sections:
                raise SchemaViolation(
                    f"MAP.md has a duplicate '## {name}' heading"
                )
            current = name
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def _parse_fog_entries(section_text: str) -> list[FogEntry]:
    entries = []
    for line in section_text.splitlines():
        match = _FOG_ENTRY.match(line.strip())
        if match:
            entries.append(
                FogEntry(
                    id=match.group("id"),
                    number=int(match.group("n")),
                    text=match.group("text").strip(),
                )
            )
    return entries


def _parse_decisions(section_text: str) -> list[DecisionLine]:
    lines = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        match = _DECISION_LINE.match(stripped)
        if match:
            lines.append(
                DecisionLine(
                    gist=match.group("gist").strip().rstrip(".").strip() + ".",
                    ticket_link=match.group("link").strip(),
                )
            )
    return lines


def _parse_out_of_scope(section_text: str) -> list[str]:
    return [
        line.strip()[1:].strip()
        for line in section_text.splitlines()
        if line.strip().startswith("-")
    ]


def _parse_parts(section_text: str) -> list[PartRow]:
    rows = []
    for line in section_text.splitlines():
        match = _TABLE_ROW.match(line.strip())
        if not match:
            continue
        cells = [c.strip() for c in match.group(1).split("|")]
        if len(cells) != 3:
            continue
        name, join_key, status = cells
        if name in ("Part", "") or set(name) <= {"-"}:
            continue  # header / separator row
        join_key = join_key.strip("`").strip()
        rows.append(PartRow(name=name, join_key=join_key, status=status))
    return rows


def parse_map_document(text: str, path: Path) -> MapDocument:
    fields, body = parse_frontmatter(text)
    frontmatter = _parse_map_frontmatter(fields)
    sections = _split_sections(body)
    doc = MapDocument(path=path, frontmatter=frontmatter, sections=sections)
    doc.fog_entries = _parse_fog_entries(
        sections.get("Not-yet-specified (fog)", "")
    )
    doc.decisions = _parse_decisions(sections.get("Decisions-so-far", ""))
    doc.out_of_scope = _parse_out_of_scope(sections.get("Out-of-scope", ""))
    doc.parts = _parse_parts(sections.get("Parts", ""))
    return doc


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


@dataclass
class TicketFrontmatter:
    type: str
    status: str
    claim: str | None
    graduated_from: str | None


@dataclass
class TicketDocument:
    path: Path
    frontmatter: TicketFrontmatter
    resolution: str | None


def _null_or(value: str) -> str | None:
    return None if value.strip().lower() == "null" else value.strip()


def _parse_ticket_frontmatter(fields: dict[str, str]) -> TicketFrontmatter:
    for key in ("type", "status"):
        if key not in fields:
            raise SchemaViolation(f"ticket frontmatter is missing '{key}'")
    return TicketFrontmatter(
        type=fields["type"],
        status=fields["status"],
        claim=_null_or(fields.get("claim", "null")),
        graduated_from=_null_or(fields.get("graduated-from", "null")),
    )


_RESOLUTION_HEADING = re.compile(r"^##\s+Resolution\s*$")


def _parse_resolution(body: str) -> str | None:
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if _RESOLUTION_HEADING.match(line.strip()):
            rest = lines[i + 1:]
            end = len(rest)
            for j, nxt in enumerate(rest):
                if nxt.startswith("## "):
                    end = j
                    break
            text = "\n".join(rest[:end]).strip()
            return text or None
    return None


def parse_ticket_document(text: str, path: Path) -> TicketDocument:
    fields, body = parse_frontmatter(text)
    frontmatter = _parse_ticket_frontmatter(fields)
    resolution = _parse_resolution(body)
    return TicketDocument(path=path, frontmatter=frontmatter, resolution=resolution)


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


# --- validate ---------------------------------------------------------


def _check_schema_version(schema_version: int) -> None:
    if schema_version > SUPPORTED_SCHEMA_VERSION:
        raise SchemaViolation(
            f"schema_version {schema_version} is newer than the "
            f"supported ceiling {SUPPORTED_SCHEMA_VERSION} — refusing "
            "to read further"
        )


def _check_map_structure(doc: MapDocument) -> None:
    if doc.frontmatter.state not in VALID_MAP_STATES:
        raise SchemaViolation(
            f"MAP.md frontmatter 'state' {doc.frontmatter.state!r} is not "
            f"one of {sorted(VALID_MAP_STATES)}"
        )
    missing = [s for s in REQUIRED_SECTIONS if s not in doc.sections]
    if missing:
        raise SchemaViolation(
            f"MAP.md is missing required section(s): {', '.join(missing)}"
        )
    present_order = [name for name in doc.sections if name in REQUIRED_SECTIONS]
    if present_order != REQUIRED_SECTIONS:
        raise SchemaViolation(
            "MAP.md sections are out of order: map-format.md pins "
            f"{REQUIRED_SECTIONS}, found {present_order}"
        )
    seen_fog_ids: set[str] = set()
    for fog in doc.fog_entries:
        if not re.fullmatch(r"F-[0-9]+", fog.id):
            raise SchemaViolation(f"malformed fog id: {fog.id!r}")
        if fog.id in seen_fog_ids:
            raise SchemaViolation(f"duplicate fog id reused: {fog.id!r}")
        seen_fog_ids.add(fog.id)
    for part in doc.parts:
        expected_prefix = f"{doc.frontmatter.map_id} / Part: "
        if not part.join_key.startswith(expected_prefix):
            raise SchemaViolation(
                f"Parts row {part.name!r} join key {part.join_key!r} does "
                f"not match '<map-id> / Part: <name>' for map-id "
                f"{doc.frontmatter.map_id!r}"
            )


def _check_tickets(map_dir: Path) -> None:
    tickets_dir = Path(map_dir) / "tickets"
    if not tickets_dir.is_dir():
        return
    for ticket_path in sorted(tickets_dir.glob("*.md")):
        ticket = read_ticket(ticket_path)
        if ticket.frontmatter.type not in VALID_TICKET_TYPES:
            raise SchemaViolation(
                f"{ticket_path}: type {ticket.frontmatter.type!r} is not "
                f"one of {sorted(VALID_TICKET_TYPES)}"
            )
        if ticket.frontmatter.status not in VALID_TICKET_STATUSES:
            raise SchemaViolation(
                f"{ticket_path}: status {ticket.frontmatter.status!r} is "
                f"not one of {sorted(VALID_TICKET_STATUSES)}"
            )


def validate(target: Path, repo_root: Path | None = None) -> tuple[int, str]:
    """Validate a decision-map store at `target` (a map directory).

    Returns `(exit_code, message)`: 0 clean, 1 operational error
    (target missing/unreadable), 2 a structural or schema-version
    violation — the exit-code split map-format.md §Command surface
    pins for every checker in the family.

    `repo_root` is accepted for arg-shape parity with the other
    §Command surface scripts; this function does not use it in v1."""
    map_dir = Path(target)
    if not map_dir.is_dir():
        return 1, f"map directory not found: {map_dir}"
    try:
        doc = read_map(map_dir)
    except MapStoreError as exc:
        return 1, str(exc)
    except SchemaViolation as exc:
        return 2, str(exc)

    try:
        _check_schema_version(doc.frontmatter.schema_version)
        _check_map_structure(doc)
        _check_tickets(map_dir)
    except SchemaViolation as exc:
        return 2, str(exc)
    except MapStoreError as exc:
        return 1, str(exc)

    return 0, f"{map_dir} is a valid decision-map store"


def is_live_map(target: Path, repo_root: Path | None = None) -> bool:
    """map-format.md §Live-map criterion: checker-valid (validate
    exits 0) AND state in {charting, active}. Never a bare
    directory-existence check.

    `repo_root` is accepted for arg-shape parity with the other
    §Command surface scripts; this function does not use it in v1."""
    code, _ = validate(target, repo_root=repo_root)
    if code != 0:
        return False
    doc = read_map(target)
    return doc.frontmatter.state in LIVE_MAP_STATES


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
