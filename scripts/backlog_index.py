#!/usr/bin/env python3
"""Validate + (later) generate the loom family backlog store's index.

`docs/loom/backlog/README.md` is the store's format SSOT (charter). This
script's `--validate` mode enforces the six invariants the charter's
frontmatter contract implies, over every entry file under `--store`
(default `docs/loom/backlog`, both the live tier and its `archive/`
subdirectory):

  (i)   filename stem == frontmatter `name`.
  (ii)  `status` is a member of the closed status vocabulary (transcribed
        VERBATIM from the plan's §Pinned frontmatter contract below —
        never re-derived, never imported from the charter or test file).
  (iii) an entry under `archive/` carries `status: archived` and no other
        value; a live entry (directly under `--store`, excluding
        `archive/`) never carries `status: archived`.
  (iv)  every archive-tier entry carries an `archived: <YYYY-MM-DD>` field
        in that exact date shape, and no live entry carries `archived` at
        all (charter, docs/loom/backlog/README.md:20,24-27). This closes
        the gap where a store passed --validate clean and then failed
        loudly at --write (build_index()'s own `archived` check below) —
        the two modes must agree on what "clean" means.
  (v)   when an entry's body carries a `- Origin:`/`- Start:` bullet (any
        parenthetical-qualifier variant, e.g. `- Start (re-trigger):`) AND
        its frontmatter carries the matching `origin`/`start` field, the two
        must agree after normalization (whitespace collapsed to single
        spaces, the bullet's label + optional parenthetical qualifier
        stripped). Revision-round-1 DECISION: this fires only when BOTH
        copies are present — a bullet with no matching frontmatter field at
        all is a migration-completeness gap (GAP 1), not an agreement gap,
        and is deliberately out of this invariant's scope. See
        `_find_body_bullet` for the extraction rule.
  (vi)  `description` is present and non-blank. The charter's frontmatter
        contract (docs/loom/backlog/README.md:16) lists `description` with
        no `<optional; ...>` marker — it is contractual like `name`/
        `status`. Without this check a missing OR blank value passed
        --validate clean, then build_index() rendered a dangling
        `- [name](backlog/name.md) — ` line (em dash, trailing space, no
        text) at --write, and --check regenerated that identical malformed
        string and called it clean — laundering it into the committed
        baseline. Missing and blank are treated identically: both produce
        the same malformed line.

Deliberately narrower than `scripts/check_loom_memory_integrity.py`'s five
invariants: this store's index is *generated* from the entry files (Task 3),
which makes the memory checker's index-line invariants structurally
impossible to violate here. See the plan's "Kickoff decision — generating
the index removes three of the four invariants" note.

Frontmatter is a `---`-delimited `key: value` block, hand-parsed with
stdlib only (no PyYAML), mirroring check_loom_memory_integrity.py's
convention — the format is a small, store-local subset of YAML.

`--write` mode (this task) regenerates `docs/loom/BACKLOG.md` from the
entry files: live entries are grouped by status into one section each,
in the fixed order the plan's Kickoff decision pins (COMMITTED-NEXT ->
OPEN -> PARKED -> UPSTREAM -> SHIPPED -> CLOSED — SUPERSEDED), empty
sections omitted, followed by a compact `## Archived` section (name +
date only, no description). `build_index()` is a pure function of the
entry files' frontmatter text — no filesystem writes, no git shell-outs
— which is what makes two `--write` runs over unchanged input produce
byte-identical output.

Archived-date design decision: the pinned index shape's `## Archived`
line needs a date (`- <name> (archived <YYYY-MM-DD>)`), and the
originally-pinned frontmatter contract has no field for it. This task
adds `archived: <YYYY-MM-DD>` as a new optional frontmatter field,
required on entries under `archive/` and stamped at archive time
(documented in docs/loom/backlog/README.md alongside the pinned
contract). Deriving the date from git history instead was rejected:
it would make the generator depend on the store's git history rather
than being a pure function of the entry files, and it cannot be
exercised by a temp-store test that is not itself a git repository. An
archived entry missing the field fails `--write` loudly (exit 1) rather
than emitting a blank or fabricated date.

`--check` mode (this task) is the doctoc `--dryrun` pattern: regenerate the
index from the entry files in memory (same `build_index()` as --write) and
compare it, byte-for-byte, against the committed `--output` file. Exits 0
when identical, 1 with a unified diff when they differ (a hand-edit to the
committed file, or any drift), 1 if `--output` does not exist yet, and 1 on
the same build errors `--write` rejects. `--check` never calls
`Path.write_text` — it only reads `--output` and compares; the committed
index stays readable by agents, and a hand-edit is blocked rather than
merely discouraged.

`--ready` mode is the store's READ surface (plan
docs/loom/plans/2026-08-06-backlog-ready-verb-and-close-loop.md, Task 1):
it prints the actionable queue — `## COMMITTED-NEXT` entries first, then
`## OPEN` entries, each section in filename order (filenames start
YYYY-MM-DD, so filename order is file-date order) — one
`- <name> — <description>` line per entry, plus an indented
`  start: <value>` second line for an entry whose frontmatter carries
`start:`. Statuses PARKED / UPSTREAM / SHIPPED / CLOSED — SUPERSEDED /
archived are excluded from the listing and only tallied in the closing
`ready: N committed / M open / K excluded by status` line.

Usage:
    python3 scripts/backlog_index.py --validate [--store docs/loom/backlog]
    python3 scripts/backlog_index.py --write [--store docs/loom/backlog] [--output docs/loom/BACKLOG.md]
    python3 scripts/backlog_index.py --check [--store docs/loom/backlog] [--output docs/loom/BACKLOG.md]
    python3 scripts/backlog_index.py --ready [--store docs/loom/backlog]

Exit codes: 0 = clean/written/matches, 1 = at least one invariant violation
(--validate), a build error (--write, --check, --ready), or drift / a
missing committed file (--check).
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

_DATE_SHAPE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _is_valid_date_shape(value: str) -> bool:
    """True when `value` is a real calendar date in YYYY-MM-DD shape.

    Regex alone would accept a calendar-invalid string like 2026-13-40;
    strptime rejects those too, so both must agree.
    """
    if not _DATE_SHAPE.match(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True

# Transcribed VERBATIM from the plan's §Pinned frontmatter contract
# (docs/loom/plans/2026-08-01-backlog-one-entry-per-file.md, ## Notes):
#   status: <COMMITTED-NEXT | OPEN | PARKED | UPSTREAM | SHIPPED |
#            CLOSED — SUPERSEDED | archived>
CLOSED_STATUS_VOCABULARY = [
    "COMMITTED-NEXT",
    "OPEN",
    "PARKED",
    "UPSTREAM",
    "SHIPPED",
    "CLOSED — SUPERSEDED",
    "archived",
]

ARCHIVED_STATUS = "archived"

# Kickoff decision (plan ## Notes, "index section order is fixed by
# urgency"): hard contract, not alphabetical. Any other order makes
# Task 4's --check report false drift.
STATUS_SECTION_ORDER = [
    "COMMITTED-NEXT",
    "OPEN",
    "PARKED",
    "UPSTREAM",
    "SHIPPED",
    "CLOSED — SUPERSEDED",
]


@dataclass(frozen=True)
class Violation:
    kind: str  # "name" | "status" | "archive-tier" | "archived-date" | "description" | "field-agreement"
    file: str
    detail: str


def _body_text(text: str) -> str:
    """Everything after the frontmatter's closing `---` fence.

    Returns the whole text unchanged when it does not open with a `---`
    fence at line 1 (not frontmatter at all), and "" when the fence never
    closes (malformed file) — callers of this function only care about
    entries that already passed the (i)-(iv) frontmatter checks, so a
    malformed file yields "no bullet found" rather than an exception.
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "".join(lines[i + 1:])
    return ""


# A top-level body bullet naming one of these fields, in any of the
# corpus's observed shapes: `- Origin: ...`, `- Start (re-trigger): ...`,
# `- **Origin**: ...`, `- Start: (calc-linkbase) ...`. Captures everything
# after the (label + optional parenthetical qualifier + colon) up to the
# FIRST of: a blank line, the next column-0 `- ` bullet, or end of string.
# The blank-line stop is what keeps ordinary prose that follows the bullet
# (the store charter's own escape hatch for a value too long for one
# bullet) OUT of the captured value; the no-next-bullet/no-blank-line case
# is what lets the captured group still span a bullet that line-wraps
# across several indented continuation lines with no blank line between
# them, exactly the shape the migrated entries use.
_FIELD_BULLET_PATTERNS = {
    field: re.compile(
        rf"^-\s*\**{field}\**\s*(?:\([^)]*\))?\s*:\s*(.*?)(?=\n[ \t]*\n|\n-\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for field in ("Origin", "Start")
}


def _normalize_field_text(value: str) -> str:
    """Collapse all whitespace (including the newlines of a wrapped body
    bullet) to single spaces and strip. This is what makes a multi-line body
    bullet comparable to its single-line frontmatter counterpart."""
    return " ".join(value.split())


def _find_body_bullet(body: str, field_label: str) -> str | None:
    """The normalized value of a `- <field_label>[ (qualifier)]: ...`
    top-level bullet in `body`, or None if no such bullet exists.

    `field_label` is "Origin" or "Start" (matches `_FIELD_BULLET_PATTERNS`).
    """
    match = _FIELD_BULLET_PATTERNS[field_label].search(body)
    if match is None:
        return None
    return _normalize_field_text(match.group(1))


def parse_frontmatter(text: str) -> dict[str, str]:
    """Hand-parsed `---`-delimited `key: value` block. Stdlib only, no PyYAML."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    frontmatter: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        frontmatter[key.strip()] = value.strip()
    return frontmatter


def _entry_files(store: Path) -> list[tuple[Path, bool]]:
    """Every entry file under `store`, paired with whether it is archived.

    Live entries are `store/*.md` excluding README.md and excluding
    `archive/` itself (a directory, never matched by `*.md`). Archived
    entries are `store/archive/*.md`.
    """
    live = sorted(p for p in store.glob("*.md") if p.name != "README.md")
    archive_dir = store / "archive"
    archived = (
        sorted(p for p in archive_dir.glob("*.md") if p.name != "README.md")
        if archive_dir.is_dir()
        else []
    )
    return [(p, False) for p in live] + [(p, True) for p in archived]


def _check_name(display: str, frontmatter: dict[str, str], stem: str) -> list[Violation]:
    """(i) filename stem == frontmatter name."""
    name = frontmatter.get("name")
    if name is None:
        return [Violation("name", display, "frontmatter missing 'name' key")]
    if name != stem:
        return [Violation("name", display, f"frontmatter name '{name}' != filename stem '{stem}'")]
    return []


def _check_status(display: str, status: str | None) -> list[Violation]:
    """(ii) status is a member of the closed vocabulary."""
    if status is None:
        return [Violation("status", display, "frontmatter missing 'status' key")]
    if status not in CLOSED_STATUS_VOCABULARY:
        return [Violation("status", display, f"status '{status}' is not in the closed vocabulary")]
    return []


def _check_archive_tier(display: str, status: str | None, is_archived: bool) -> list[Violation]:
    """(iii) archive-tier <-> status: archived agreement."""
    if status is None:
        return []
    if is_archived and status != ARCHIVED_STATUS:
        return [
            Violation(
                "archive-tier",
                display,
                f"entry is under archive/ but status is '{status}', not 'archived'",
            )
        ]
    if not is_archived and status == ARCHIVED_STATUS:
        return [
            Violation(
                "archive-tier",
                display,
                "entry carries status: archived but is not under archive/",
            )
        ]
    return []


def _check_archived_date(
    display: str, frontmatter: dict[str, str], is_archived: bool
) -> list[Violation]:
    """(iv) archived: <date> is required (and date-shaped) on every
    archive-tier entry, and must be absent on every live entry. Charter:
    docs/loom/backlog/README.md:20,24-27 — "It carries no meaning on a live
    entry and must not be set on one."
    """
    archived_value = frontmatter.get("archived")
    if is_archived:
        if archived_value is None:
            return [
                Violation(
                    "archived-date",
                    display,
                    "archive-tier entry missing required 'archived: <YYYY-MM-DD>' field",
                )
            ]
        if not _is_valid_date_shape(archived_value):
            return [
                Violation(
                    "archived-date",
                    display,
                    f"'archived' field {archived_value!r} is not a valid YYYY-MM-DD date",
                )
            ]
        return []
    if archived_value is not None:
        return [
            Violation(
                "archived-date",
                display,
                f"live entry carries 'archived: {archived_value}' but must not set it",
            )
        ]
    return []


def _check_description(display: str, frontmatter: dict[str, str]) -> list[Violation]:
    """(vi) description is a required, non-blank field (charter:
    docs/loom/backlog/README.md:16 lists it with no <optional; ...> marker).
    Missing and blank are both violations — they render the identical
    dangling-em-dash line in build_index() (module docstring point (vi))."""
    description = frontmatter.get("description")
    if description is None:
        return [Violation("description", display, "frontmatter missing 'description' key")]
    if not description:
        return [Violation("description", display, "frontmatter 'description' field is blank")]
    return []


def _check_field_agreement(display: str, frontmatter: dict[str, str], body: str) -> list[Violation]:
    """(v) frontmatter <-> body-bullet agreement, only when both are present
    (revision-round-1 DECISION — see module docstring)."""
    violations: list[Violation] = []
    for field_key, field_label in (("origin", "Origin"), ("start", "Start")):
        fm_value = frontmatter.get(field_key)
        if fm_value is None:
            continue
        bullet_value = _find_body_bullet(body, field_label)
        if bullet_value is None:
            continue
        if _normalize_field_text(fm_value) != bullet_value:
            violations.append(
                Violation(
                    "field-agreement",
                    display,
                    f"frontmatter '{field_key}' disagrees with the body's "
                    f"'- {field_label}' bullet after normalization",
                )
            )
    return violations


def find_violations(store: Path) -> list[Violation]:
    violations: list[Violation] = []

    for path, is_archived in _entry_files(store):
        display = str(path.relative_to(store))
        text = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        status = frontmatter.get("status")

        violations.extend(_check_name(display, frontmatter, path.stem))
        violations.extend(_check_status(display, status))
        violations.extend(_check_archive_tier(display, status, is_archived))
        violations.extend(_check_archived_date(display, frontmatter, is_archived))
        violations.extend(_check_description(display, frontmatter))
        violations.extend(_check_field_agreement(display, frontmatter, _body_text(text)))

    return violations


def _bucket_entry(
    path: Path,
    is_archived: bool,
    by_status: dict[str, list[tuple[str, str]]],
    archived_entries: list[tuple[str, str]],
) -> None:
    """Classify one entry file into `by_status` (live) or `archived_entries`
    (archive-tier) in place. Raises ValueError (see
    `_collect_index_entries()`'s docstring for the conditions) rather than
    mutating either collection on a bad entry."""
    frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
    name = frontmatter.get("name", path.stem)

    if is_archived:
        archived_date = frontmatter.get("archived")
        if not archived_date:
            raise ValueError(
                f"{path.name}: archived entry has no 'archived: <date>' "
                "frontmatter field; cannot render its Archived line"
            )
        # Shape, not just presence. `--write` is documented as usable on
        # its own, so a malformed value reaching here would be rendered
        # verbatim into the committed index — and `--check` would then
        # regenerate the same bogus string and call the file clean, making
        # the laundered value the new baseline. Reject at the writer.
        if not _is_valid_date_shape(archived_date):
            raise ValueError(
                f"{path.name}: archived entry's 'archived: {archived_date}' "
                "is not a real YYYY-MM-DD date; refusing to render it"
            )
        archived_entries.append((name, archived_date))
        return

    status = frontmatter.get("status")
    if status not in by_status:
        raise ValueError(
            f"{path.name}: live entry has status {status!r}, outside the "
            "closed vocabulary of live statuses"
        )
    description = frontmatter.get("description", "")
    by_status[status].append((name, description))


def _collect_index_entries(
    store: Path,
) -> tuple[dict[str, list[tuple[str, str]]], list[tuple[str, str]]]:
    """Walk `store`'s entry files and bucket them for `build_index()`'s
    render step: live entries grouped by status, archive-tier entries as
    (name, archived-date) pairs. Both live groups and the archived list
    come back sorted by name.

    Raises ValueError (never exits the process itself — the caller decides
    exit codes) when an entry cannot be rendered: a live entry whose status
    falls outside the closed vocabulary, or an archived entry missing (or
    carrying a malformed) `archived: <date>` field its Archived line needs.
    """
    by_status: dict[str, list[tuple[str, str]]] = {status: [] for status in STATUS_SECTION_ORDER}
    archived_entries: list[tuple[str, str]] = []

    for path, is_archived in _entry_files(store):
        _bucket_entry(path, is_archived, by_status, archived_entries)

    for entries in by_status.values():
        entries.sort(key=lambda item: item[0])
    archived_entries.sort(key=lambda item: item[0])

    return by_status, archived_entries


def build_index(store: Path) -> str:
    """Regenerate the index text per the plan's §Pinned index shape.

    Pure function of the entry files' frontmatter text: no filesystem
    writes, no git shell-outs, no wall-clock reads. That purity is what
    keeps two --write runs over unchanged input byte-identical.

    Raises ValueError (never exits the process itself — the caller
    decides exit codes) when an entry cannot be rendered: a live entry
    whose status falls outside the closed vocabulary, or an archived
    entry missing the `archived: <date>` field its Archived line needs.
    See `_collect_index_entries()` for the collection/validation step.

    Note the division of labor with `find_violations()`: this function
    does NOT re-check `name` (it falls back to `path.stem`) or re-check
    that an archive-tier entry's `status` is actually `archived` — those
    are `--validate`'s job. Run `--validate` before `--write` if those
    invariants have not already been checked.
    """
    by_status, archived_entries = _collect_index_entries(store)

    lines = [
        "# loom family backlog",
        "",
        "<!-- GENERATED by scripts/backlog_index.py — do not edit by hand. -->",
    ]
    for status in STATUS_SECTION_ORDER:
        entries = by_status[status]
        if not entries:
            continue
        lines.append("")
        lines.append(f"## {status}")
        for name, description in entries:
            lines.append(f"- [{name}](backlog/{name}.md) — {description}")

    if archived_entries:
        lines.append("")
        lines.append("## Archived")
        for name, archived_date in archived_entries:
            lines.append(f"- {name} (archived {archived_date})")

    return "\n".join(lines) + "\n"


# The two statuses --ready treats as actionable, in render order.
READY_STATUSES = ("COMMITTED-NEXT", "OPEN")


def build_ready(store: Path) -> str:
    """The store's READ surface: the actionable queue as prose (see the
    module docstring's `--ready` paragraph for the pinned format).

    Same purity contract as `build_index()`: a pure function of the entry
    files' frontmatter text. Entries render in `_entry_files()` order,
    which is sorted-by-filename per tier — i.e. file-date order.

    Raises ValueError (caller decides exit codes) on a status outside the
    closed vocabulary, mirroring `_bucket_entry()` — an unrecognized
    status must not be silently laundered into the excluded tally.

    An entry physically under `archive/` is excluded regardless of its
    frontmatter `status:` — the archive tier overrides the status field,
    same as `_bucket_entry()`.
    """
    entry_lines: dict[str, list[str]] = {status: [] for status in READY_STATUSES}
    counts: dict[str, int] = {status: 0 for status in READY_STATUSES}
    excluded = 0

    for path, is_archived in _entry_files(store):
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        status = frontmatter.get("status")
        if status not in CLOSED_STATUS_VOCABULARY:
            raise ValueError(
                f"{path.name}: entry has status {status!r}, outside the "
                "closed status vocabulary"
            )
        if is_archived or status not in READY_STATUSES:
            excluded += 1
            continue
        counts[status] += 1
        name = frontmatter.get("name", path.stem)
        description = frontmatter.get("description", "")
        entry_lines[status].append(f"- {name} — {description}")
        start = frontmatter.get("start")
        if start:
            entry_lines[status].append(f"  start: {start}")

    lines: list[str] = []
    for status in READY_STATUSES:
        if not entry_lines[status]:
            continue
        if lines:
            lines.append("")
        lines.append(f"## {status}")
        lines.extend(entry_lines[status])

    if lines:
        lines.append("")
    lines.append(
        f"ready: {counts['COMMITTED-NEXT']} committed / {counts['OPEN']} open "
        f"/ {excluded} excluded by status"
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--store",
        default="docs/loom/backlog",
        help="backlog store directory (default: docs/loom/backlog)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="check every entry's frontmatter against the store's invariants",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate the index and write it to --output",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate the index and compare it to --output without writing; exit 1 on drift",
    )
    parser.add_argument(
        "--ready",
        action="store_true",
        help="print the actionable queue (COMMITTED-NEXT then OPEN) with a closing count line",
    )
    parser.add_argument(
        "--output",
        default="docs/loom/BACKLOG.md",
        help="path to write (--write) or compare against (--check) the generated index",
    )
    args = parser.parse_args()

    if not args.validate and not args.write and not args.check and not args.ready:
        parser.error("no mode specified; pass --validate, --write, --check, or --ready")

    if args.validate:
        violations = find_violations(Path(args.store))
        if not violations:
            print("backlog_index --validate: OK — every invariant holds.")
        else:
            print("backlog_index --validate: FAIL — the store's invariants are violated.\n")
            for violation in sorted(violations, key=lambda v: (v.file, v.kind)):
                print(f"  [{violation.kind}] {violation.file}: {violation.detail}")
            return 1

    if args.write:
        try:
            text = build_index(Path(args.store))
        except ValueError as exc:
            print(f"backlog_index --write: FAIL — {exc}")
            return 1
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"backlog_index --write: wrote {args.output}")

    if args.check:
        try:
            generated = build_index(Path(args.store))
        except ValueError as exc:
            print(f"backlog_index --check: FAIL — {exc}")
            return 1

        output_path = Path(args.output)
        if not output_path.is_file():
            print(
                f"backlog_index --check: FAIL — {output_path} does not exist; "
                "run --write first"
            )
            return 1

        committed = output_path.read_text(encoding="utf-8")
        if committed != generated:
            print(
                "backlog_index --check: FAIL — the committed index has "
                f"drifted from the entry files (compare against {output_path}).\n"
            )
            diff = difflib.unified_diff(
                committed.splitlines(keepends=True),
                generated.splitlines(keepends=True),
                fromfile=f"{output_path} (committed)",
                tofile="<regenerated from entry files>",
            )
            sys.stdout.writelines(diff)
            return 1

        print(f"backlog_index --check: OK — {output_path} matches the entry files.")

    if args.ready:
        try:
            ready_text = build_ready(Path(args.store))
        except ValueError as exc:
            print(f"backlog_index --ready: FAIL — {exc}")
            return 1
        sys.stdout.write(ready_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
