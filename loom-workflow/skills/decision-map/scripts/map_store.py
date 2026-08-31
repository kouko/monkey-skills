#!/usr/bin/env python3
"""The shared reader for a decision-map store (MAP.md + tickets/).

Grammar SSOT: `loom-workflow/skills/decision-map/references/
map-format.md` — this module is the ONLY sanctioned parser of the
store's bytes (§Command surface); every sibling checker
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
import ctypes
import errno
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import map_lock

MIN_SUPPORTED_SCHEMA_VERSION = 3
SUPPORTED_SCHEMA_VERSION = 3

VALID_MAP_STATES = {"charting", "active", "clear", "archived"}
LIVE_MAP_STATES = {"charting", "active"}
V2_TICKET_TYPES = {"grilling", "research", "task", "prototype"}
V3_TICKET_TYPES = {"grilling", "research", "prototype", "delivery"}
HITL_TICKET_TYPES = {"grilling", "prototype"}
RATIFIED_MAP_STATES = {"active", "clear"}
V2_TICKET_STATUSES = {"open", "claimed", "closed"}
V3_TICKET_STATUSES = {"open", "claimed", "closed", "withdrawn"}
V3_TICKET_FRONTMATTER_FIELDS = {
    "type",
    "status",
    "claim",
    "graduated-from",
    "blocked-by",
    "ratification",
    "withdrawn-from",
    "brief",
}


class LiveMapResult(str, Enum):
    LIVE = "live"
    NOT_PRESENT = "not-present"
    BROKEN = "broken"

REQUIRED_SECTIONS = [
    "Destination",
    "Notes",
    "Decisions-so-far",
    "Not-yet-specified (fog)",
    "Out-of-scope",
]

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


class MapStoreError(Exception):
    """Operational error: target missing/unreadable — exit 1."""


class SchemaViolation(Exception):
    """Structural/schema-version violation — exit 2."""


class AtomicExchangeUnsupported(SchemaViolation):
    """The local filesystem cannot provide an atomic pathname exchange."""


class AtomicExchangeBroken(SchemaViolation):
    """An exchanged target could not be restored after a CAS mismatch."""


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
_COMMIT_EVIDENCE = re.compile(r"(?:commit\s+)?[0-9a-fA-F]{7,40}")
_PR_EVIDENCE = re.compile(
    r"(?:PR\s*)?#\d+|(?:PR\s+)?https?://\S+/pull/\d+",
    re.IGNORECASE,
)
_ARTIFACT_PATH_EVIDENCE = re.compile(
    r"(?:\.{1,2}/|/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+"
)


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


def _has_delivery_evidence(text: str) -> bool:
    """Recognize the three delivery-evidence shapes pinned by the
    ticket contract: commit SHA, PR reference, or artifact path."""
    for line in text.splitlines():
        key, separator, value = line.strip().partition(":")
        if separator != ":" or key != "delivery-evidence":
            continue
        evidence = value.strip()
        if any(
            pattern.fullmatch(evidence)
            for pattern in (
                _COMMIT_EVIDENCE,
                _PR_EVIDENCE,
                _ARTIFACT_PATH_EVIDENCE,
            )
        ):
            return True
    return False


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


_SAFE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DATED_HUMAN = re.compile(r"^[^,\s][^,]*,\s*\d{4}-\d{2}-\d{2}$")


def _assert_no_symlink_components(path: Path) -> None:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            raise SchemaViolation(
                f"refusing mutation through symlink component: {current}"
            )
        if not current.exists():
            break


def _assert_contained(root: Path, candidate: Path) -> None:
    try:
        candidate.resolve(strict=False).relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise SchemaViolation(f"path escapes repository root: {candidate}") from exc


def _before_atomic_exchange(path: Path, temporary: Path) -> None:
    """Test seam immediately before the atomic pathname exchange."""


def _before_atomic_restore(path: Path, temporary: Path) -> None:
    """Test seam after mismatch detection and before the restore exchange."""


def _exchange_paths(first: Path, second: Path) -> None:
    """Atomically exchange two existing same-filesystem pathnames."""
    libc = ctypes.CDLL(None, use_errno=True)
    system = platform.system()
    first_bytes = os.fsencode(first)
    second_bytes = os.fsencode(second)
    if system == "Darwin" and hasattr(libc, "renamex_np"):
        rename = libc.renamex_np
        rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        result = rename(first_bytes, second_bytes, 0x00000002)  # RENAME_SWAP
    elif system == "Linux" and hasattr(libc, "renameat2"):
        rename = libc.renameat2
        rename.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        rename.restype = ctypes.c_int
        result = rename(-100, first_bytes, -100, second_bytes, 0x00000002)
    else:
        raise AtomicExchangeUnsupported(
            f"atomic exchange is unsupported on {system or 'this platform'}"
        )
    if result == 0:
        return
    error = ctypes.get_errno()
    if error in {
        errno.ENOSYS,
        errno.EINVAL,
        errno.EXDEV,
        getattr(errno, "ENOTSUP", errno.EINVAL),
        getattr(errno, "EOPNOTSUPP", errno.EINVAL),
    }:
        raise AtomicExchangeUnsupported(
            f"atomic exchange is unsupported for {first.parent}: {os.strerror(error)}"
        )
    raise OSError(error, os.strerror(error), first)


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _record_exchange_recovery(
    path: Path,
    temporary: Path,
    restore_error: BaseException,
    *,
    retained_role: str,
) -> Path:
    evidence_path = path.parent / f".{path.name}.cas-recovery.json"
    evidence = {
        "action": "recovery-required",
        "candidate_path": str(path),
        "retained_path": str(temporary),
        "retained_role": retained_role,
        "restore_error": str(restore_error),
        "status": "BROKEN",
    }
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(evidence_path, flags, 0o600)
    try:
        payload = (json.dumps(evidence, indent=2, sort_keys=True) + "\n").encode()
        remaining = memoryview(payload)
        while remaining:
            written = os.write(descriptor, remaining)
            if written == 0:
                raise OSError("short write while recording CAS recovery evidence")
            remaining = remaining[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    _fsync_directory(path.parent)
    return evidence_path


def _recovery_detail(
    path: Path,
    temporary: Path,
    error: BaseException,
    retained_role: str,
) -> str:
    try:
        evidence_path = _record_exchange_recovery(
            path, temporary, error, retained_role=retained_role
        )
    except BaseException as evidence_error:
        return (
            f"retained temp: {temporary}; recovery evidence unavailable: "
            f"{evidence_error}"
        )
    return f"evidence: {evidence_path}"


def _cleanup_exchanged_temporary(path: Path, temporary: Path) -> None:
    try:
        temporary.unlink()
        _fsync_directory(path.parent)
    except OSError:
        pass


def _commit_exchanged_candidate(path: Path, temporary: Path) -> None:
    try:
        _fsync_directory(path.parent)
    except OSError as durability_error:
        try:
            _exchange_paths(temporary, path)
        except BaseException as restore_error:
            detail = _recovery_detail(
                path,
                temporary,
                restore_error,
                "expected authority retained after durability failure",
            )
            raise AtomicExchangeBroken(
                "BROKEN recovery-required: exchange durability failed and "
                "authority could not be restored; " + detail
            ) from restore_error
        restoration_error: BaseException = durability_error
        try:
            _fsync_directory(path.parent)
        except OSError as exc:
            restoration_error = exc
        detail = _recovery_detail(
            path,
            temporary,
            restoration_error,
            "candidate retained after durability failure",
        )
        raise AtomicExchangeBroken(
            "BROKEN recovery-required: exchange durability failed; expected "
            "authority was restored and candidate retained; " + detail
        ) from durability_error
    _cleanup_exchanged_temporary(path, temporary)


def _restore_cas_mismatch(path: Path, temporary: Path, candidate: bytes) -> None:
    _before_atomic_restore(path, temporary)
    try:
        _exchange_paths(temporary, path)
    except BaseException as restore_error:
        detail = _recovery_detail(
            path,
            temporary,
            restore_error,
            "concurrent version retained during restore",
        )
        raise AtomicExchangeBroken(
            "BROKEN recovery-required: atomic CAS restore failed; " + detail
        ) from restore_error
    if temporary.read_bytes() != candidate:
        _handle_restore_interleaving(path, temporary)
    try:
        _fsync_directory(path.parent)
    except OSError as durability_error:
        detail = _recovery_detail(
            path,
            temporary,
            durability_error,
            "candidate retained after mismatch restore",
        )
        raise AtomicExchangeBroken(
            "BROKEN recovery-required: mismatch restore durability failed; " + detail
        ) from durability_error
    _cleanup_exchanged_temporary(path, temporary)
    raise SchemaViolation(f"refusing atomic compare-and-swap because {path} changed")


def _handle_restore_interleaving(path: Path, temporary: Path) -> None:
    try:
        _exchange_paths(temporary, path)
    except BaseException as third_exchange_error:
        detail = _recovery_detail(
            path,
            temporary,
            third_exchange_error,
            "newest concurrent version; restore incomplete",
        )
        raise AtomicExchangeBroken(
            "BROKEN recovery-required: newest concurrent version could not be "
            "returned to target; " + detail
        ) from third_exchange_error
    interleaving = RuntimeError(
        "target changed again between mismatch detection and restore"
    )
    detail = _recovery_detail(
        path,
        temporary,
        interleaving,
        "concurrent version retained during restore",
    )
    raise AtomicExchangeBroken(
        "BROKEN recovery-required: target changed during CAS restore; " + detail
    ) from interleaving


def _atomic_write(
    path: Path, text: str, *, expected: bytes | None = None
) -> None:
    """Replace one regular file without exposing partially written bytes.

    This is the single-file safety floor used by REQ-86 operations.  Full
    multi-artifact conflict detection and recovery remain owned by REQ-87.
    """
    _assert_no_symlink_components(path)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if expected is None:
            os.replace(temporary, path)
            _fsync_directory(path.parent)
            return
        _before_atomic_exchange(path, temporary)
        try:
            _exchange_paths(temporary, path)
        except AtomicExchangeUnsupported:
            raise
        except OSError as exc:
            raise SchemaViolation(
                f"atomic compare-and-swap could not exchange {path}: {exc}"
            ) from exc
        displaced = temporary.read_bytes()
        if displaced == expected:
            _commit_exchanged_candidate(path, temporary)
            return
        _restore_cas_mismatch(path, temporary, text.encode("utf-8"))
    except BaseException as exc:
        if not isinstance(exc, AtomicExchangeBroken):
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
        raise


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


def _check_schema_version(schema_version: int) -> None:
    if schema_version < MIN_SUPPORTED_SCHEMA_VERSION:
        raise SchemaViolation(
            f"schema_version {schema_version} is retired; migrate MAP.md "
            f"to schema_version {MIN_SUPPORTED_SCHEMA_VERSION} or later"
        )
    if schema_version > SUPPORTED_SCHEMA_VERSION:
        raise SchemaViolation(
            f"schema_version {schema_version} is newer than the "
            f"supported ceiling {SUPPORTED_SCHEMA_VERSION} — refusing "
            "to read further"
        )


def _has_user_ratified_line(text: str) -> bool:
    """Whether a `user-ratified:` line carries a non-empty value.

    A bare `user-ratified:` token is not a ratification (R3b): a
    ratified decision must carry a name/date value.
    """
    return any(
        line.strip().partition(":")[0] == "user-ratified"
        and bool(line.strip().partition(":")[2].strip())
        for line in text.splitlines()
    )


def _has_resolution_field(text: str, field: str) -> bool:
    """Whether a Resolution contains a non-empty `field: value` line."""
    return any(
        line.strip().partition(":")[0] == field
        and bool(line.strip().partition(":")[2].strip())
        for line in text.splitlines()
    )


def _has_named_dated_user_ratification(text: str) -> bool:
    return any(
        re.fullmatch(
            r"user-ratified:\s*[^,\s][^,]*,\s*\d{4}-\d{2}-\d{2}",
            line.strip(),
        )
        for line in text.splitlines()
    )


def _check_v3_ticket_closure_evidence(ticket: TicketDocument) -> None:
    """Require each schema-v3 ticket type's distinct closure record."""
    resolution = ticket.resolution or ""
    ticket_type = ticket.frontmatter.type
    requirements = {
        "grilling": (
            ("decision",),
            "a non-empty 'decision:' line and named/date "
            "'user-ratified: <name>, YYYY-MM-DD'",
        ),
        "research": (
            ("factual-answer", "inspectable-evidence"),
            "non-empty 'factual-answer:' and 'inspectable-evidence:' lines",
        ),
        "prototype": (
            ("candidate-artifact", "evaluation"),
            "non-empty 'candidate-artifact:' and 'evaluation:' lines and "
            "named/date 'user-ratified: <name>, YYYY-MM-DD'",
        ),
    }
    if ticket_type == "delivery":
        if not _has_delivery_evidence(resolution):
            raise SchemaViolation(
                f"{ticket.path}: closed delivery ticket requires "
                "'delivery-evidence: <commit SHA | PR | artifact path>'"
            )
        return
    fields, guidance = requirements[ticket_type]
    needs_ratification = ticket_type in HITL_TICKET_TYPES
    if not all(_has_resolution_field(resolution, field) for field in fields) or (
        needs_ratification and not _has_named_dated_user_ratification(resolution)
    ):
        raise SchemaViolation(
            f"{ticket.path}: closed {ticket_type} ticket requires {guidance}"
        )


def _check_v3_ticket_withdrawal(ticket: TicketDocument) -> None:
    """Require a ratified disposition without treating it as closure."""
    if ticket.frontmatter.withdrawn_from not in {"open", "claimed"}:
        raise SchemaViolation(
            f"{ticket.path}: withdrawn ticket must name 'withdrawn-from: open' "
            "or 'withdrawn-from: claimed'"
        )
    withdrawal = ticket.withdrawal or ""
    if ticket.resolution is not None:
        raise SchemaViolation(
            f"{ticket.path}: withdrawn ticket must not carry a Resolution; "
            "withdrawal does not satisfy subtype closure evidence"
        )
    if not _has_named_dated_user_ratification(withdrawal):
        raise SchemaViolation(
            f"{ticket.path}: withdrawn ticket requires named/date "
            "'user-ratified: <name>, YYYY-MM-DD' in its Withdrawal"
        )
    if not _has_resolution_field(withdrawal, "reason"):
        raise SchemaViolation(
            f"{ticket.path}: withdrawn ticket requires a non-empty "
            "'reason:' line in its Withdrawal"
        )


def _check_v3_ticket_frontmatter(ticket: TicketDocument) -> None:
    """Keep v3 progress derived from artifacts, not ticket fields."""
    unknown = sorted(ticket.frontmatter_keys - V3_TICKET_FRONTMATTER_FIELDS)
    if unknown:
        raise SchemaViolation(
            f"{ticket.path}: v3 ticket has unsupported frontmatter field(s) "
            f"{', '.join(unknown)}; persisted progress is derived from owning "
            "artifacts, not ticket fields"
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
    previous_fog_number = 0
    for fog in doc.fog_entries:
        if not re.fullmatch(r"F-[0-9]+", fog.id):
            raise SchemaViolation(f"malformed fog id: {fog.id!r}")
        if fog.id in seen_fog_ids:
            raise SchemaViolation(f"duplicate fog id reused: {fog.id!r}")
        if fog.number <= previous_fog_number:
            raise SchemaViolation("fog ids must be monotonic in document order")
        seen_fog_ids.add(fog.id)
        previous_fog_number = fog.number
    if doc.frontmatter.state in RATIFIED_MAP_STATES and not _has_user_ratified_line(
        doc.sections.get("Destination", "")
    ):
        raise SchemaViolation(
            f"{doc.path}: state {doc.frontmatter.state!r} requires a "
            "non-empty 'user-ratified:' line like "
            "'user-ratified: <name>, YYYY-MM-DD' in the Destination section "
            "(map-format.md §Sections)"
        )
    if doc.frontmatter.state == "clear" and doc.fog_entries:
        raise SchemaViolation(
            f"{doc.path}: clear map has non-empty fog "
            "(map-format.md §Ticket boundary contract)"
        )


def _da_evidence_is_resolvable(evidence: str, repo_root: Path | None) -> bool:
    """A satisfied objective criterion's evidence must be a pointer a
    reviewer can actually open, per R3c: an existing commit SHA, a
    well-formed PR reference, or an artifact path that exists inside
    the repo. A bare non-pointer string ("looks done") is not
    evidence."""
    pr_match = _PR_EVIDENCE.fullmatch(evidence)
    if pr_match is not None:
        return True
    commit_match = _COMMIT_EVIDENCE.fullmatch(evidence)
    if commit_match is not None:
        sha = evidence.split()[-1]
        if repo_root is None:
            return False
        try:
            subprocess.run(
                ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                cwd=repo_root,
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return False
        return True
    if _ARTIFACT_PATH_EVIDENCE.fullmatch(evidence) is not None:
        if repo_root is None:
            return False
        candidate = (repo_root / evidence).resolve()
        try:
            repo_root_resolved = repo_root.resolve()
        except OSError:
            return False
        if repo_root_resolved not in candidate.parents and candidate != repo_root_resolved:
            return False
        return candidate.is_file()
    return False


def _check_destination_acceptance(doc: MapDocument, repo_root: Path | None = None) -> None:
    if doc.frontmatter.schema_version != 3:
        return
    if any(
        line.strip().startswith("acceptance:")
        for line in doc.sections.get("Destination", "").splitlines()
    ):
        raise SchemaViolation(
            "schema-v3 Destination acceptance requires stable DA-<n> entries"
        )
    if doc.frontmatter.state == "active" and not doc.destination_acceptance:
        raise SchemaViolation(
            f"{doc.path}: activation requires a Destination acceptance "
            "criterion (map-format.md §Frontmatter and lifecycle); "
            "add at least one DA-<n> entry before state: active"
        )
    seen: set[str] = set()
    previous = 0
    for criterion in doc.destination_acceptance:
        if criterion.id in seen:
            raise SchemaViolation(
                f"duplicate Destination acceptance id reused: {criterion.id}"
            )
        if criterion.number <= previous:
            raise SchemaViolation(
                "Destination acceptance ids must be monotonic in document order"
            )
        seen.add(criterion.id)
        previous = criterion.number
        if criterion.state not in {"open", "satisfied"}:
            raise SchemaViolation(
                f"Destination acceptance {criterion.id} state must be open or satisfied"
            )
        if criterion.kind not in {"objective", "evaluative"}:
            raise SchemaViolation(
                f"Destination acceptance {criterion.id} kind must be objective or evaluative"
            )
        if criterion.state == "satisfied" and criterion.evidence is None:
            raise SchemaViolation(
                f"satisfied Destination acceptance {criterion.id} requires evidence"
            )
        if (
            criterion.kind == "objective"
            and criterion.state == "satisfied"
            and criterion.evidence is not None
            and not _da_evidence_is_resolvable(criterion.evidence, repo_root)
        ):
            raise SchemaViolation(
                f"satisfied objective Destination acceptance {criterion.id} "
                "requires a resolvable evidence pointer (existing commit SHA, "
                "PR reference, or artifact path within the repo), not "
                f"{criterion.evidence!r}"
            )
        if criterion.kind == "evaluative" and criterion.state == "satisfied":
            if criterion.ratification is None or not _DATED_HUMAN.fullmatch(
                criterion.ratification
            ):
                raise SchemaViolation(
                    f"satisfied evaluative Destination acceptance {criterion.id} "
                    "requires named dated user ratification"
                )
    reused = sorted(seen.intersection(doc.retired_da_ids))
    if reused:
        raise SchemaViolation(
            "Destination acceptance id reused from retirement history: "
            + ", ".join(reused)
        )


def _check_v3_clear_acceptance(doc: MapDocument) -> None:
    """Gate clear on stable, satisfied Destination acceptance criteria."""
    if doc.frontmatter.schema_version != 3 or doc.frontmatter.state != "clear":
        return
    if doc.sections["Not-yet-specified (fog)"].strip():
        raise SchemaViolation(
            f"{doc.path}: clear v3 map requires an empty fog section"
        )
    if not doc.destination_acceptance:
        raise SchemaViolation(
            f"{doc.path}: clear v3 map requires a Destination acceptance criterion"
        )
    unsatisfied = [
        criterion.id
        for criterion in doc.destination_acceptance
        if criterion.state != "satisfied" or criterion.evidence is None
    ]
    if unsatisfied:
        raise SchemaViolation(
            f"{doc.path}: clear map requires every Destination acceptance "
            "criterion satisfied with evidence; open/invalid: "
            + ", ".join(unsatisfied)
        )


def _check_tickets(map_dir: Path, state: str, schema_version: int) -> None:
    tickets_dir = Path(map_dir) / "tickets"
    if not tickets_dir.is_dir():
        return
    valid_ticket_types = (
        V3_TICKET_TYPES if schema_version == 3 else V2_TICKET_TYPES
    )
    valid_ticket_statuses = (
        V3_TICKET_STATUSES if schema_version == 3 else V2_TICKET_STATUSES
    )
    blocked_by_graph: dict[str, list[str]] = {}
    statuses: dict[str, str] = {}
    non_closed: list[str] = []
    for ticket_path in sorted(tickets_dir.glob("*.md")):
        ticket = read_ticket(ticket_path)
        if ticket.frontmatter.type not in valid_ticket_types:
            guidance = (
                "; classify the ticket by its closure evidence as one of "
                f"{sorted(valid_ticket_types)}"
                if schema_version == 3
                else ""
            )
            raise SchemaViolation(
                f"{ticket_path}: type {ticket.frontmatter.type!r} is not "
                f"one of {sorted(valid_ticket_types)}{guidance}"
            )
        if ticket.frontmatter.status not in valid_ticket_statuses:
            raise SchemaViolation(
                f"{ticket_path}: status {ticket.frontmatter.status!r} is "
                f"not one of {sorted(valid_ticket_statuses)}"
            )
        if schema_version == 3:
            _check_v3_ticket_frontmatter(ticket)
        if schema_version == 3 and ticket.frontmatter.status == "closed":
            _check_v3_ticket_closure_evidence(ticket)
        if schema_version == 3 and ticket.frontmatter.status == "withdrawn":
            _check_v3_ticket_withdrawal(ticket)
        if (
            ticket.frontmatter.status == "closed"
            and ticket.frontmatter.type in HITL_TICKET_TYPES
            and not _has_user_ratified_line(ticket.resolution or "")
        ):
            raise SchemaViolation(
                f"{ticket_path}: closed {ticket.frontmatter.type} ticket "
                "is missing a non-empty 'user-ratified: <name>, YYYY-MM-DD' "
                "line in its Resolution "
                "(map-format.md §Ticket schema HITL rule)"
            )
        if (
            ticket.frontmatter.status == "closed"
            and schema_version == 2
            and ticket.frontmatter.type == "task"
            and not _has_delivery_evidence(ticket.resolution or "")
        ):
            raise SchemaViolation(
                f"{ticket_path}: closed task ticket requires a non-empty "
                "Resolution with 'delivery-evidence: <commit SHA | PR | "
                "artifact path>' (map-format.md §Ticket schema)"
            )
        if ticket.frontmatter.status in {"open", "claimed"}:
            non_closed.append(
                f"{ticket_path.name} ({ticket.frontmatter.status})"
            )
        blocked_by_graph[ticket_path.stem] = ticket.frontmatter.blocked_by
        statuses[ticket_path.stem] = ticket.frontmatter.status
    _check_blocked_by(blocked_by_graph, tickets_dir)
    for slug, blockers in blocked_by_graph.items():
        if statuses[slug] != "claimed":
            continue
        unclosed = [blocker for blocker in blockers if statuses[blocker] != "closed"]
        if unclosed:
            raise SchemaViolation(
                f"{tickets_dir / (slug + '.md')}: claimed ticket requires every "
                "blocker closed; still blocking: " + ", ".join(unclosed)
            )
    for slug, status in statuses.items():
        if status != "withdrawn":
            continue
        stranded = [
            dependent
            for dependent, blockers in blocked_by_graph.items()
            if slug in blockers and statuses[dependent] in {"open", "claimed"}
        ]
        if stranded:
            raise SchemaViolation(
                f"{tickets_dir / (slug + '.md')}: withdrawn ticket would strand "
                "nonterminal dependent(s): "
                + ", ".join(f"{dependent}.md" for dependent in stranded)
            )
    if state == "clear" and non_closed:
        raise SchemaViolation(
            "clear map has non-closed ticket(s): " + ", ".join(non_closed)
        )


def _check_blocked_by(
    graph: dict[str, list[str]], tickets_dir: Path
) -> None:
    """map-format.md §Ticket schema's blocked-by bullet: every slug
    names an existing sibling ticket file, and the blocked-by graph is
    acyclic — dangling slugs and cycles exit 2."""
    for slug, blockers in graph.items():
        invalid = [blocker for blocker in blockers if not _SAFE_SLUG.fullmatch(blocker)]
        if invalid:
            raise SchemaViolation(
                f"{tickets_dir / (slug + '.md')}: blocked-by cross-Map or malformed "
                "target(s): " + ", ".join(invalid)
            )
        if slug in blockers:
            raise SchemaViolation(
                f"{tickets_dir / (slug + '.md')}: blocked-by self edge is forbidden"
            )
        duplicates = sorted(
            blocker for blocker in set(blockers) if blockers.count(blocker) > 1
        )
        if duplicates:
            raise SchemaViolation(
                f"{tickets_dir / (slug + '.md')}: duplicate blocked-by edge(s): "
                + ", ".join(duplicates)
            )
        for blocker in blockers:
            if blocker not in graph:
                raise SchemaViolation(
                    f"{tickets_dir / (slug + '.md')}: blocked-by missing target; names "
                    f"{blocker!r}, but no ticket file "
                    f"'{blocker}.md' exists in {tickets_dir}"
                )
    # cycle detection: iterative DFS with three-color marking
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {slug: WHITE for slug in graph}
    for start in sorted(graph):
        if color[start] != WHITE:
            continue
        stack: list[tuple[str, int]] = [(start, 0)]
        path: list[str] = []
        while stack:
            slug, edge_index = stack.pop()
            if edge_index == 0:
                color[slug] = GRAY
                path.append(slug)
            blockers = graph[slug]
            advanced = False
            for i in range(edge_index, len(blockers)):
                nxt = blockers[i]
                if color[nxt] == GRAY:
                    cycle = path[path.index(nxt):] + [nxt]
                    raise SchemaViolation(
                        "blocked-by graph has a cycle: "
                        + " -> ".join(cycle)
                    )
                if color[nxt] == WHITE:
                    stack.append((slug, i + 1))
                    stack.append((nxt, 0))
                    advanced = True
                    break
            if not advanced:
                color[slug] = BLACK
                path.pop()


def _check_monotonic_relations(map_dir: Path, doc: MapDocument) -> None:
    if doc.frontmatter.schema_version != 3:
        return
    out_of_scope_ids = {
        match.group("id")
        for line in doc.out_of_scope
        if (match := re.match(r"^(?P<id>F-[0-9]+)\s*:", line)) is not None
    }
    graduated: dict[str, list[str]] = {}
    closed_tickets: list[str] = []
    for ticket_path in sorted((Path(map_dir) / "tickets").glob("*.md")):
        ticket = read_ticket(ticket_path)
        if ticket.frontmatter.graduated_from:
            graduated.setdefault(ticket.frontmatter.graduated_from, []).append(
                ticket_path.name
            )
        if ticket.frontmatter.status == "closed":
            closed_tickets.append(ticket_path.name)
    current_fog = {entry.id for entry in doc.fog_entries}
    reused_fog = sorted(current_fog.intersection(out_of_scope_ids | set(graduated)))
    if reused_fog:
        raise SchemaViolation(
            "partial fog graduation or fog id reused from graduated or "
            "Out-of-scope history: "
            + ", ".join(reused_fog)
        )
    duplicate_graduations = sorted(
        fog_id for fog_id, tickets in graduated.items() if len(tickets) > 1
    )
    if duplicate_graduations:
        raise SchemaViolation(
            "fog entry graduated more than once: " + ", ".join(duplicate_graduations)
        )
    gist_counts: dict[str, int] = {}
    for decision in doc.decisions:
        gist_counts[decision.ticket_link] = gist_counts.get(decision.ticket_link, 0) + 1
    bad_gists = [
        ticket
        for ticket in closed_tickets
        if gist_counts.get(f"tickets/{ticket}", 0) != 1
    ]
    if bad_gists:
        raise SchemaViolation(
            "every closed ticket requires exactly one Decisions-so-far gist: "
            + ", ".join(bad_gists)
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
        _check_schema_version(doc.frontmatter.schema_version)
        _check_map_structure(doc)
        _check_destination_acceptance(doc, resolved_repo_root)
        _check_v3_clear_acceptance(doc)
        _check_tickets(
            map_dir, doc.frontmatter.state, doc.frontmatter.schema_version
        )
        _check_monotonic_relations(map_dir, doc)
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
