#!/usr/bin/env python3
"""Validate + (later) generate the loom family backlog store's index.

`docs/loom/backlog/README.md` is the store's format SSOT (charter). This
script's `--validate` mode enforces the six invariants the charter's
frontmatter contract implies, over every entry file under `--store`
(default `docs/loom/backlog`, both the live tier and its `archive/`
subdirectory):

  (i)   filename stem == frontmatter `name`.
  (ii)  `status` is a member of the closed status vocabulary — exactly
        `open`, `bet`, `closed` (docs/loom/plans/2026-08-21-dissolve-
        direction-layer.md Task 1 collapsed the prior seven-word
        vocabulary, including the separate `archived` status, to these
        three).
  (iii) an entry under `archive/` carries `status: closed` — the archive
        tier is a plain destination folder now (former invariants iii/iv,
        the `status: archived` agreement plus the separate `archived:`
        date-field check, collapse to this one rule; archive-tier entries
        are excluded from the generated index listing, so no rendered
        date is needed).
  (iv)  `blocked: <reason>` is legal only on an `open` entry — it records
        why an otherwise-actionable entry cannot be picked right now
        (`--ready` is its only reader; see `build_ready`).
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

`--write` mode regenerates `docs/loom/BACKLOG.md` from the entry files:
live entries are grouped by status into one section each, in the fixed
order `bet` -> `open` -> `closed`, empty sections omitted. Archive-tier
entries are excluded from the listing entirely (brief BI-10 — the
archive tier is a plain destination whose entries are `closed` by
construction). `build_index()` is a pure function of the entry files'
frontmatter text — no filesystem writes, no git shell-outs — which is
what makes two `--write` runs over unchanged input produce byte-identical
output.

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
it prints the actionable queue — `## bet` entries first, then `## open`
entries, each section in filename order (filenames start YYYY-MM-DD, so
filename order is file-date order) — one `- <name> — <description>` line
per entry, plus an indented `  start: <value>` second line for an entry
whose frontmatter carries `start:`. `closed` entries, archive-tier
entries, and `open` entries carrying a `blocked:` field are excluded
from the listing and only tallied in the closing
`ready: N bet / M open / K excluded by status` line.

`--direction-write <path>` / `--direction-check <path>` (direction-layer
arc, plan docs/loom/plans/2026-08-07-loom-direction-layer.md Task 1) are
the DIRECTION.md counterparts of --write/--check: `--direction-write`
regenerates the given DIRECTION.md's `## Now` section — one
`- <name> — <description>` line per `bet` entry in filename
(= file-date) order, or exactly `_(queue empty — bet at the next
close-out)_` when the queue is empty — replacing the section body
wholesale (it is machine-owned per DIRECTION.md's charter — SSOT
`loom-code/hooks/direction-charter.md`) and
leaving every other line untouched. It refuses loudly (exit 1, no write)
when the file lacks a `## Now` heading or an entry's frontmatter is
malformed (status outside the closed vocabulary). `--direction-check` is
self-confirmation — the generator confirming itself (arc-3 lesson): it
re-runs the generator in memory and diffs against the committed file,
exit 1 on drift or a missing file, never writing.

The validate mode (which a FLAGLESS invocation now defaults to,
mirroring check_loom_memory_integrity.py's trio shape) additionally
checks the direction file at `<store>/../DIRECTION.md` — the
convention's fixed location — ONLY when it exists; an absent file is
silently valid (the direction layer is opt-in per repo). Its three
independent checks: `## Now` content matches the `bet` entry
files; `## Now`/`## Next` headings present (`## Later` is optional —
tolerated if present, never required); and no date-like token
(`20\\d\\d[-/年.]` or `Q[1-4]`) anywhere OUTSIDE the generated `## Now`
body — the charter's no-dates rule as a checked invariant. The `## Now`
body is exempt from the date scan because entry NAMES are date-prefixed
by store convention; the now-matches-entries check is what keeps that
exemption safe (nothing but generator output can live there).

Usage:
    python3 scripts/backlog_index.py [--store docs/loom/backlog]
    python3 scripts/backlog_index.py --validate [--store docs/loom/backlog]
    python3 scripts/backlog_index.py --write [--store docs/loom/backlog] [--output docs/loom/BACKLOG.md]
    python3 scripts/backlog_index.py --check [--store docs/loom/backlog] [--output docs/loom/BACKLOG.md]
    python3 scripts/backlog_index.py --ready [--store docs/loom/backlog]
    python3 scripts/backlog_index.py --direction-write docs/loom/DIRECTION.md [--store docs/loom/backlog]
    python3 scripts/backlog_index.py --direction-check docs/loom/DIRECTION.md [--store docs/loom/backlog]

Exit codes: 0 = clean/written/matches, 1 = at least one invariant violation
(--validate, flagless), a build error (--write, --check, --ready,
--direction-write, --direction-check), or drift / a missing committed file
(--check, --direction-check).
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

# Collapsed vocabulary (plan docs/loom/plans/2026-08-21-dissolve-
# direction-layer.md Task 1, brief BI-2): exactly three words. The prior
# seven-word vocabulary (COMMITTED-NEXT / OPEN / PARKED / UPSTREAM /
# SHIPPED / CLOSED — SUPERSEDED / archived) is retired — the "live but not
# actionable" distinction moved to the optional `blocked:` field.
CLOSED_STATUS_VOCABULARY = [
    "open",
    "bet",
    "closed",
]

# Kickoff decision (plan ## Notes, "index section order is fixed by
# urgency"): hard contract, not alphabetical. Any other order makes
# Task 4's --check report false drift.
STATUS_SECTION_ORDER = [
    "bet",
    "open",
    "closed",
]


@dataclass(frozen=True)
class Violation:
    kind: str  # "name" | "status" | "archive-tier" | "blocked" | "description" | "field-agreement" | "serves"
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
    for field in ("Origin", "Start", "Serves")
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
    """(iii) an entry under archive/ carries status: closed. One-directional
    — a LIVE entry carrying status: closed is legal (SHIPPED/CLOSED —
    SUPERSEDED migrated there without being archived)."""
    if status is None:
        return []
    if is_archived and status != "closed":
        return [
            Violation(
                "archive-tier",
                display,
                f"entry is under archive/ but status is '{status}', not 'closed'",
            )
        ]
    return []


def _check_blocked(display: str, frontmatter: dict[str, str], status: str | None) -> list[Violation]:
    """(iv) `blocked: <reason>` is legal only on an `open` entry."""
    if "blocked" in frontmatter and status != "open":
        return [
            Violation(
                "blocked",
                display,
                f"'blocked' field is only legal on 'open' entries, not '{status}'",
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


def _purpose_path_for(store: Path) -> Path:
    """Where the `serves` gate looks for the north-star document: the
    store's parent directory, mirroring `_direction_path_for`'s convention
    (docs/loom/PURPOSE.md beside docs/loom/backlog/). Its mere presence
    or absence is the gate — content is never read here. PRINCIPLES.md
    (the field's original 1fe7b2c1 target) holds design/engineering
    principles only and is deliberately NOT probed here."""
    return store.parent / "PURPOSE.md"


_SERVES_UNRELATED_RE = re.compile(r"^unrelated\s*—\s*\S.*$")


def _is_well_formed_serves(value: str) -> bool:
    """Closed two-form grammar (plan Task 1): either `unrelated — <reason>`
    (reason clause mandatory) or any other non-empty text (the link
    prose). A bare `unrelated` with no reason clause is malformed."""
    value = value.strip()
    if not value:
        return False
    if value == "unrelated" or value.startswith("unrelated ") or value.startswith("unrelated—"):
        return bool(_SERVES_UNRELATED_RE.match(value))
    return True


def _check_serves(
    display: str, frontmatter: dict[str, str], status: str | None, store: Path
) -> list[Violation]:
    """`serves:` is required only when status is `bet` AND the repo has
    docs/loom/PURPOSE.md (plan Task 1, retargeted by Task 3, re-keyed from
    COMMITTED-NEXT by docs/loom/plans/2026-08-21-dissolve-direction-layer.md
    Task 1 — the gate is load-bearing: monkey-skills' own store has no
    PURPOSE.md by standing choice and must stay unaffected)."""
    if status != "bet":
        return []
    if not _purpose_path_for(store).is_file():
        return []
    serves = frontmatter.get("serves")
    if serves is None:
        return [
            Violation(
                "serves",
                display,
                "'bet' entry missing required 'serves' field",
            )
        ]
    if not _is_well_formed_serves(serves):
        return [
            Violation(
                "serves",
                display,
                f"'serves: {serves}' is not well-formed — use 'serves: <how this "
                "serves the north star>' or 'serves: unrelated — <reason>'",
            )
        ]
    return []


def _check_field_agreement(display: str, frontmatter: dict[str, str], body: str) -> list[Violation]:
    """(v) frontmatter <-> body-bullet agreement, only when both are present
    (revision-round-1 DECISION — see module docstring)."""
    violations: list[Violation] = []
    for field_key, field_label in (("origin", "Origin"), ("start", "Start"), ("serves", "Serves")):
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
        violations.extend(_check_blocked(display, frontmatter, status))
        violations.extend(_check_description(display, frontmatter))
        violations.extend(_check_serves(display, frontmatter, status, store))
        violations.extend(_check_field_agreement(display, frontmatter, _body_text(text)))

    return violations


def _bucket_entry(
    path: Path,
    by_status: dict[str, list[tuple[str, str]]],
) -> None:
    """Classify one LIVE entry file into `by_status` in place. Raises
    ValueError (see `_collect_index_entries()`'s docstring for the
    condition) rather than mutating the collection on a bad entry."""
    frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
    name = frontmatter.get("name", path.stem)

    status = frontmatter.get("status")
    if status not in by_status:
        raise ValueError(
            f"{path.name}: live entry has status {status!r}, outside the "
            "closed vocabulary of live statuses"
        )
    description = frontmatter.get("description", "")
    by_status[status].append((name, description))


def _collect_index_entries(store: Path) -> dict[str, list[tuple[str, str]]]:
    """Walk `store`'s LIVE entry files and bucket them for `build_index()`'s
    render step. Archive-tier entries are excluded entirely (brief BI-10 —
    the archive tier is a plain destination whose entries are `closed` by
    construction and are never listed). Each group comes back sorted by
    name.

    Raises ValueError (never exits the process itself — the caller decides
    exit codes) when a live entry's status falls outside the closed
    vocabulary.
    """
    by_status: dict[str, list[tuple[str, str]]] = {status: [] for status in STATUS_SECTION_ORDER}

    for path, is_archived in _entry_files(store):
        if is_archived:
            continue
        _bucket_entry(path, by_status)

    for entries in by_status.values():
        entries.sort(key=lambda item: item[0])

    return by_status


def build_index(store: Path) -> str:
    """Regenerate the index text per the plan's §Pinned index shape.

    Pure function of the entry files' frontmatter text: no filesystem
    writes, no git shell-outs, no wall-clock reads. That purity is what
    keeps two --write runs over unchanged input byte-identical.

    Raises ValueError (never exits the process itself — the caller
    decides exit codes) when a live entry's status falls outside the
    closed vocabulary. See `_collect_index_entries()` for the
    collection/validation step.

    Note the division of labor with `find_violations()`: this function
    does NOT re-check `name` (it falls back to `path.stem`) or re-check
    that an archive-tier entry's `status` is actually `closed` — those
    are `--validate`'s job. Run `--validate` before `--write` if those
    invariants have not already been checked.
    """
    by_status = _collect_index_entries(store)

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

    return "\n".join(lines) + "\n"


# The two statuses --ready treats as actionable, in render order.
READY_STATUSES = ("bet", "open")


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
    same as `_bucket_entry()`. An `open` entry carrying a `blocked:` field
    is excluded too (brief BI-2 — that is what the field is for).
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
        blocked = "blocked" in frontmatter
        if is_archived or status not in READY_STATUSES or blocked:
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
        f"ready: {counts['bet']} bet / {counts['open']} open "
        f"/ {excluded} excluded by status"
    )
    return "\n".join(lines) + "\n"


# The exact line an empty `bet` queue renders into `## Now`
# (pinned by the plan; the betting prompt at close-out is what refills it).
DIRECTION_EMPTY_QUEUE_LINE = "_(queue empty — bet at the next close-out)_"

DIRECTION_NOW_HEADING = "## Now"

# The charter's no-dates rule as a checked invariant (plan Task 1):
# calendar-year tokens (2026-, 2026/, 2026年, 2026.) and quarter tokens
# (Q1-Q4). Scanned over everything OUTSIDE the generated `## Now` body.
DIRECTION_DATE_TOKEN_RE = re.compile(r"20\d\d[-/年.]|Q[1-4]")

# User-ratified exemption: a `## Next`/`## Later` line may point at a
# backlog-entry FILENAME (the charter permits this pointer pattern), which
# necessarily carries a date-like token by store convention. Matched
# substrings are stripped from the line before the date scan below runs,
# so a bare date token elsewhere on the same line is still caught.
DIRECTION_ENTRY_FILENAME_RE = re.compile(r"20\d\d-\d\d-\d\d-[A-Za-z0-9_-]+\.md")

# Second user-ratified exemption: a well-formed `## On-ramp standing
# choices` entry carries a trailing `(YYYY-MM-DD)` by design — grammar
# SSOT is check_onramp_choice.py's `_STANDING_ENTRY` / family-reception.md
# §On-ramp standing choices. Kept semantically IDENTICAL to
# `_STANDING_ENTRY` (same quantifiers/character classes; the only
# difference is the added `date` capture group, needed here to strip
# just that span before the date scan) — deliberately not imported
# (this module must not depend on the checker CLI), so
# test_standing_entry_regex_matches_check_onramp_choice pins the two
# against drift. Only the trailing date group is stripped before the
# date scan, so a malformed line, or a date anywhere else on a
# well-formed line, is still caught.
DIRECTION_STANDING_ENTRY_RE = re.compile(
    r"^-\s*row\s+(?P<row>\d+)\s*\([^)]*\):\s*standing\s+"
    r"(?P<choice>direct|detour)\s*—\s*.+(?P<date>\(\d{4}-\d{2}-\d{2}\))\s*$"
)
DIRECTION_STANDING_HEADING = "## On-ramp standing choices"


def _direction_path_for(store: Path) -> Path:
    """Where the validate mode looks for the direction file: the store's
    parent directory (the convention fixes both locations together —
    docs/loom/DIRECTION.md beside docs/loom/backlog/)."""
    return store.parent / "DIRECTION.md"


def build_direction_now(store: Path) -> list[str]:
    """The generated `## Now` section body: one `- <name> — <description>`
    line per live `bet` entry, in `_entry_files()` order (sorted
    by filename = file-date order), or exactly the empty-queue line.

    Same purity contract as `build_index()`/`build_ready()`. Raises
    ValueError (caller decides exit codes) on a status outside the closed
    vocabulary — malformed frontmatter must fail loudly, never be silently
    dropped from the queue it might belong to.
    """
    lines: list[str] = []
    for path, is_archived in _entry_files(store):
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        status = frontmatter.get("status")
        if status not in CLOSED_STATUS_VOCABULARY:
            raise ValueError(
                f"{path.name}: entry has status {status!r}, outside the "
                "closed status vocabulary"
            )
        if is_archived or status != "bet":
            continue
        name = frontmatter.get("name", path.stem)
        description = frontmatter.get("description", "")
        lines.append(f"- {name} — {description}")
    return lines or [DIRECTION_EMPTY_QUEUE_LINE]


def _direction_section_bounds(
    lines: list[str], heading: str
) -> tuple[int, int] | None:
    """(heading index, section end) of the `heading` section in `lines`,
    or None when the heading is absent. The section body runs from the
    line after the heading to the next `## ` heading or EOF. Shared by
    every direction-file section scan so the two readers of DIRECTION.md
    cannot disagree on where a section starts and ends."""
    for i, line in enumerate(lines):
        if line.strip() == heading:
            section_end = len(lines)
            for j in range(i + 1, len(lines)):
                if lines[j].lstrip().startswith("## "):
                    section_end = j
                    break
            return i, section_end
    return None


def splice_direction_now(direction_text: str, now_lines: list[str]) -> str:
    """Replace the `## Now` section body WHOLESALE with `now_lines`
    (blank-line padded). Unlike the memory checker's splice, no in-section
    prose survives — the section is machine-owned per DIRECTION.md's
    charter (`loom-code/hooks/family-reception.md` §DIRECTION.md
    charter). Every line outside the section is left untouched.

    Raises ValueError when `direction_text` has no `## Now` heading —
    there is nothing to regenerate into, and writing one in would invent
    file structure the human owns.
    """
    lines = direction_text.splitlines()
    bounds = _direction_section_bounds(lines, DIRECTION_NOW_HEADING)
    if bounds is None:
        raise ValueError(
            f"the direction file has no {DIRECTION_NOW_HEADING!r} heading "
            "to regenerate into"
        )
    heading_idx, section_end = bounds
    new_lines = lines[: heading_idx + 1] + [""] + now_lines + [""] + lines[section_end:]
    return "\n".join(new_lines) + "\n"


def find_direction_violations(direction_path: Path, store: Path) -> list[Violation]:
    """The validate mode's independent DIRECTION.md checks (see the module
    docstring). Absent file = no violations — the direction layer is
    opt-in per repo, mirroring the stations' silent-skip posture."""
    if not direction_path.is_file():
        return []
    display = direction_path.name
    text = direction_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    violations: list[Violation] = []

    for heading in ("## Now", "## Next"):
        if not any(line.strip() == heading for line in lines):
            violations.append(
                Violation("direction-heading", display, f"missing required '{heading}' heading")
            )

    bounds = _direction_section_bounds(lines, DIRECTION_NOW_HEADING)
    if bounds is not None:
        try:
            regenerated = splice_direction_now(text, build_direction_now(store))
        except ValueError as exc:
            violations.append(Violation("direction-now", display, str(exc)))
        else:
            if regenerated != text:
                violations.append(
                    Violation(
                        "direction-now",
                        display,
                        "'## Now' does not match the 'bet' entry "
                        "files; regenerate with --direction-write",
                    )
                )

    now_body = range(bounds[0] + 1, bounds[1]) if bounds is not None else range(0)
    standing_bounds = _direction_section_bounds(lines, DIRECTION_STANDING_HEADING)
    standing_body = (
        range(standing_bounds[0] + 1, standing_bounds[1])
        if standing_bounds is not None
        else range(0)
    )

    for lineno, line in enumerate(lines):
        if lineno in now_body:
            continue  # generated body: entry names are date-prefixed by convention
        scan_source = line
        if lineno in standing_body:
            # Match the STRIPPED line, as check_onramp_choice.load_standing
            # does — otherwise a CommonMark-legal indented entry the checker
            # honours as a standing choice would be flagged here.
            entry = line.strip()
            standing_match = DIRECTION_STANDING_ENTRY_RE.match(entry)
            if standing_match is not None:
                # Strip only the trailing (YYYY-MM-DD) group — a date
                # elsewhere on a well-formed line is still caught. Offsets
                # are into `entry`, so the surviving text comes from it too.
                start, end = standing_match.span("date")
                scan_source = entry[:start] + entry[end:]
        scan_line = DIRECTION_ENTRY_FILENAME_RE.sub("", scan_source)
        match = DIRECTION_DATE_TOKEN_RE.search(scan_line)
        if match:
            violations.append(
                Violation(
                    "direction-date",
                    display,
                    f"line {lineno + 1} carries date-like token "
                    f"{match.group(0)!r} — the charter bans dates in this file",
                )
            )
    return violations


def _run_direction_write(args: argparse.Namespace) -> int:
    """--direction-write: regenerate the given DIRECTION.md's `## Now`
    section from `bet` entry files and write it back."""
    direction_path = Path(args.direction_write)
    if not direction_path.is_file():
        print(
            f"backlog_index --direction-write: FAIL — {direction_path} does "
            "not exist; create it with its `## Now` / `## Next` sections "
            "first (charter: loom-code/hooks/direction-charter.md)"
        )
        return 1
    try:
        new_text = splice_direction_now(
            direction_path.read_text(encoding="utf-8"),
            build_direction_now(Path(args.store)),
        )
    except ValueError as exc:
        print(f"backlog_index --direction-write: FAIL — {exc}")
        return 1
    direction_path.write_text(new_text, encoding="utf-8")
    print(f"backlog_index --direction-write: wrote {direction_path}")
    return 0


def _run_direction_check(args: argparse.Namespace) -> int:
    """--direction-check: re-run the `## Now` generator in memory and diff
    it against the given DIRECTION.md without writing; exit 1 on drift."""
    direction_path = Path(args.direction_check)
    if not direction_path.is_file():
        print(
            f"backlog_index --direction-check: FAIL — {direction_path} does "
            "not exist; run --direction-write first"
        )
        return 1
    committed_direction = direction_path.read_text(encoding="utf-8")
    try:
        generated_direction = splice_direction_now(
            committed_direction, build_direction_now(Path(args.store))
        )
    except ValueError as exc:
        print(f"backlog_index --direction-check: FAIL — {exc}")
        return 1
    if committed_direction != generated_direction:
        print(
            "backlog_index --direction-check: FAIL — the committed '## Now' "
            f"has drifted from the entry files (compare against {direction_path}).\n"
        )
        diff = difflib.unified_diff(
            committed_direction.splitlines(keepends=True),
            generated_direction.splitlines(keepends=True),
            fromfile=f"{direction_path} (committed)",
            tofile="<regenerated from entry files>",
        )
        sys.stdout.writelines(diff)
        return 1
    print(
        f"backlog_index --direction-check: OK — {direction_path} matches "
        "the entry files."
    )
    return 0


def _run_validate(args: argparse.Namespace) -> int:
    """--validate (also the flagless default): check every entry's
    frontmatter against the store's invariants, plus the direction file's
    independent checks when one exists at the store's fixed location."""
    store = Path(args.store)
    violations = find_violations(store)
    violations.extend(find_direction_violations(_direction_path_for(store), store))
    if not violations:
        print("backlog_index --validate: OK — every invariant holds.")
        return 0
    print("backlog_index --validate: FAIL — the store's invariants are violated.\n")
    for violation in sorted(violations, key=lambda v: (v.file, v.kind)):
        print(f"  [{violation.kind}] {violation.file}: {violation.detail}")
    return 1


def _run_write(args: argparse.Namespace) -> int:
    """--write: regenerate the index from the entry files and write it to
    --output."""
    try:
        text = build_index(Path(args.store))
    except ValueError as exc:
        print(f"backlog_index --write: FAIL — {exc}")
        return 1
    Path(args.output).write_text(text, encoding="utf-8")
    print(f"backlog_index --write: wrote {args.output}")
    return 0


def _run_check(args: argparse.Namespace) -> int:
    """--check: regenerate the index in memory and diff it against
    --output without writing; exit 1 on drift or a missing --output file."""
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
    return 0


def _run_ready(args: argparse.Namespace) -> int:
    """--ready: print the actionable queue (bet then open) with
    a closing count line."""
    try:
        ready_text = build_ready(Path(args.store))
    except ValueError as exc:
        print(f"backlog_index --ready: FAIL — {exc}")
        return 1
    sys.stdout.write(ready_text)
    return 0


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
        help="print the actionable queue (bet then open) with a closing count line",
    )
    parser.add_argument(
        "--output",
        default="docs/loom/BACKLOG.md",
        help="path to write (--write) or compare against (--check) the generated index",
    )
    parser.add_argument(
        "--direction-write",
        metavar="PATH",
        help="regenerate the given DIRECTION.md's '## Now' section from "
        "'bet' entry files and write it back",
    )
    parser.add_argument(
        "--direction-check",
        metavar="PATH",
        help="re-run the '## Now' generator in memory and diff it against the "
        "given DIRECTION.md without writing (self-confirmation — the generator "
        "confirming itself; the independent guard is the flagless validate "
        "mode); exit 1 on drift",
    )
    args = parser.parse_args()

    if not any(
        (
            args.validate,
            args.write,
            args.check,
            args.ready,
            args.direction_write,
            args.direction_check,
        )
    ):
        # Flagless invocation defaults to validate, mirroring
        # check_loom_memory_integrity.py's trio shape (direction-layer arc;
        # formerly a "no mode specified" parser error).
        args.validate = True

    if args.validate:
        result = _run_validate(args)
        if result != 0:
            return result

    if args.write:
        result = _run_write(args)
        if result != 0:
            return result

    if args.check:
        result = _run_check(args)
        if result != 0:
            return result

    if args.ready:
        result = _run_ready(args)
        if result != 0:
            return result

    if args.direction_write:
        result = _run_direction_write(args)
        if result != 0:
            return result

    if args.direction_check:
        result = _run_direction_check(args)
        if result != 0:
            return result

    return 0


if __name__ == "__main__":
    sys.exit(main())
