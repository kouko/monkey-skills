"""Pure document models and parsers for Decision Map store bytes.

The public map_store facade re-exports these objects for existing callers.
This module performs no filesystem operations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_SECTION_HEADING = re.compile(r"^##\s+(.+?)\s*$")


_FOG_ENTRY = re.compile(r"^-\s*(?P<id>F-(?P<n>\d+))\s*:\s*(?P<text>.*)$")


_DECISION_LINE = re.compile(r"^-\s*(?P<gist>.*)\((?P<link>[^()]*)\)\s*$")


_DA_ENTRY = re.compile(
    r"^-\s*(?P<id>DA-(?P<n>[0-9]+))\s*:\s*(?P<body>.*)$"
)


_DA_SHAPED_BULLET = re.compile(
    r"^[-*+]\s*DA(?:-[^\s:]*|[0-9][^\s:]*|\s+[^\s:]+)?\s*:"
)


_RETIRED_DA = re.compile(r"^retired-da:\s*(?P<id>DA-[0-9]+)\s*\|")


class SchemaViolation(Exception):
    """Structural/schema-version violation — exit 2."""


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
        if line.strip():
            match = re.fullmatch(
                r"(?P<key>[A-Za-z0-9][A-Za-z0-9_-]*):\s*(?P<value>.*)", line
            )
            if match is None:
                raise SchemaViolation(f"malformed frontmatter line: {line!r}")
            key = match.group("key")
            if key in fields:
                raise SchemaViolation(f"duplicate frontmatter key: {key!r}")
            fields[key] = match.group("value").strip()
        i += 1
    if i >= len(lines):
        raise SchemaViolation("missing frontmatter closing '---' fence")
    body = "\n".join(lines[i + 1:])
    return fields, body


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
class DestinationAcceptance:
    id: str
    number: int
    text: str
    state: str
    kind: str
    evidence: str | None
    ratification: str | None


@dataclass
class MapDocument:
    path: Path
    frontmatter: MapFrontmatter
    sections: dict[str, str] = field(default_factory=dict)
    fog_entries: list[FogEntry] = field(default_factory=list)
    decisions: list[DecisionLine] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)
    destination_acceptance: list[DestinationAcceptance] = field(
        default_factory=list
    )
    retired_da_ids: set[str] = field(default_factory=set)


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


def _parse_destination_acceptance(
    section_text: str,
) -> list[DestinationAcceptance]:
    criteria: list[DestinationAcceptance] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not _DA_SHAPED_BULLET.match(stripped):
            continue
        match = _DA_ENTRY.fullmatch(stripped)
        if match is None:
            raise SchemaViolation(
                f"malformed Destination acceptance entry: {stripped!r}"
            )
        parts = [part.strip() for part in match.group("body").split("|")]
        if not parts or not parts[0]:
            raise SchemaViolation(
                f"Destination acceptance {match.group('id')} has empty criterion text"
            )
        values: dict[str, str] = {}
        for part in parts[1:]:
            key, separator, value = part.partition(":")
            key = key.strip()
            value = value.strip()
            if separator != ":" or key not in {
                "state",
                "kind",
                "evidence",
                "user-ratified",
            }:
                raise SchemaViolation(
                    f"Destination acceptance {match.group('id')} has "
                    f"unsupported field {part!r}"
                )
            if key in values:
                raise SchemaViolation(
                    f"Destination acceptance {match.group('id')} has duplicate "
                    f"field {key!r}"
                )
            if key == "user-ratified" and not value:
                raise SchemaViolation(
                    f"Destination acceptance {match.group('id')} user-ratified "
                    "field requires a non-empty value like "
                    "'user-ratified: <name>, YYYY-MM-DD'"
                )
            values[key] = value
        criteria.append(
            DestinationAcceptance(
                id=match.group("id"),
                number=int(match.group("n")),
                text=parts[0],
                state=values.get("state", ""),
                kind=values.get("kind", ""),
                evidence=values.get("evidence") or None,
                ratification=values.get("user-ratified") or None,
            )
        )
    return criteria


def _parse_retired_da_ids(notes: str) -> set[str]:
    return {
        match.group("id")
        for line in notes.splitlines()
        if (match := _RETIRED_DA.match(line.strip())) is not None
    }


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
    doc.destination_acceptance = _parse_destination_acceptance(
        sections.get("Destination", "")
    )
    doc.retired_da_ids = _parse_retired_da_ids(sections.get("Notes", ""))
    return doc


@dataclass
class TicketFrontmatter:
    type: str
    status: str
    claim: str | None
    graduated_from: str | None
    withdrawn_from: str | None
    blocked_by: list[str] = field(default_factory=list)
    ratification: str | None = None


@dataclass
class TicketDocument:
    path: Path
    frontmatter: TicketFrontmatter
    frontmatter_keys: set[str]
    resolution: str | None
    withdrawal: str | None


def _null_or(value: str) -> str | None:
    return None if value.strip().lower() == "null" else value.strip()


def _parse_ticket_frontmatter(fields: dict[str, str]) -> TicketFrontmatter:
    for key in ("type", "status"):
        if key not in fields:
            raise SchemaViolation(f"ticket frontmatter is missing '{key}'")
    # `blocked-by` is one line of comma-separated sibling ticket slugs
    # (map-format.md §Ticket schema — frontmatter has no YAML lists);
    # absent means no blockers, exactly the pre-field behavior.
    blocked_by = [
        slug.strip()
        for slug in fields.get("blocked-by", "").split(",")
        if slug.strip()
    ]
    return TicketFrontmatter(
        type=fields["type"],
        status=fields["status"],
        claim=_null_or(fields.get("claim", "null")),
        graduated_from=_null_or(fields.get("graduated-from", "null")),
        withdrawn_from=_null_or(fields.get("withdrawn-from", "null")),
        blocked_by=blocked_by,
        ratification=_null_or(fields.get("ratification", "null")),
    )


_SECTION_HEADING_TEMPLATE = r"^##\s+{name}\s*$"


def _parse_ticket_section(body: str, name: str) -> str | None:
    heading = re.compile(_SECTION_HEADING_TEMPLATE.format(name=re.escape(name)))
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if heading.match(line.strip()):
            rest = lines[i + 1:]
            end = len(rest)
            for j, nxt in enumerate(rest):
                if nxt.startswith("## "):
                    end = j
                    break
            text = "\n".join(rest[:end]).strip()
            return text or None
    return None


def _parse_resolution(body: str) -> str | None:
    return _parse_ticket_section(body, "Resolution")


def parse_ticket_document(text: str, path: Path) -> TicketDocument:
    fields, body = parse_frontmatter(text)
    frontmatter = _parse_ticket_frontmatter(fields)
    resolution = _parse_resolution(body)
    withdrawal = _parse_ticket_section(body, "Withdrawal")
    return TicketDocument(
        path=path,
        frontmatter=frontmatter,
        frontmatter_keys=set(fields),
        resolution=resolution,
        withdrawal=withdrawal,
    )
