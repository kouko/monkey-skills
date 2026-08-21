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
entries, and entries carrying a `blocked:` field are excluded
from the listing and only tallied in the closing
`ready: N bet / M open / P closed / Q blocked` line — two separate
axes, since a `closed`/archive-tier entry and a `blocked` entry
are excluded for different reasons (the former will never be ready as
written; the latter is one `blocked:` line away from it).

The validate mode (which a FLAGLESS invocation now defaults to,
mirroring check_loom_memory_integrity.py's trio shape) checks every
entry's frontmatter against the store's invariants above.

Usage:
    python3 scripts/backlog_index.py [--store docs/loom/backlog]
    python3 scripts/backlog_index.py --validate [--store docs/loom/backlog]
    python3 scripts/backlog_index.py --write [--store docs/loom/backlog] [--output docs/loom/BACKLOG.md]
    python3 scripts/backlog_index.py --check [--store docs/loom/backlog] [--output docs/loom/BACKLOG.md]
    python3 scripts/backlog_index.py --ready [--store docs/loom/backlog]

Exit codes: 0 = clean/written/matches, 1 = at least one invariant violation
(--validate, flagless), a build error (--write, --check, --ready), or
drift / a missing committed file (--check).
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

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
    entries are `store/archive/*.md`, also excluding README.md.

    Returned in filename order, live entries first, then archived —
    filenames start `YYYY-MM-DD`, so this is file-date order. Every
    reader that walks this list (directly or via
    `iter_validated_entries()`) inherits that order; it is what makes
    two `--write` runs over unchanged input produce a byte-identical
    `BACKLOG.md`, and what makes a "first entry" pick by any reader of
    this list deterministic.
    """
    live = sorted(p for p in store.glob("*.md") if p.name != "README.md")
    archive_dir = store / "archive"
    archived = (
        sorted(p for p in archive_dir.glob("*.md") if p.name != "README.md")
        if archive_dir.is_dir()
        else []
    )
    return [(p, False) for p in live] + [(p, True) for p in archived]


def iter_validated_entries(
    store: Path,
) -> list[tuple[Path, bool, dict[str, str]]]:
    """Every entry under `store` as `(path, is_archived, frontmatter)` in
    `_entry_files()` order, raising ValueError (the caller decides exit
    codes) on any LIVE entry whose `status:` falls outside
    `CLOSED_STATUS_VOCABULARY`.

    This is the ONE home of the out-of-vocabulary guard. All four readers
    — `build_ready()` and `_collect_index_entries()` here,
    `check_queue_relation.live_bet_names()`, and
    `check_north_star_link.find_bet_entries()` — each carried a
    hand-copied walk with its own copy of the raise, and the copies
    documented the duplication ("same bytes, same guard") instead of
    removing it. They then drifted exactly as Fowler's Duplicated Code /
    Shotgun Surgery predicts: one whole-branch review round had to patch
    two of them in lockstep, the next round found a third site diverging,
    and the round after that found the fourth.

    **Archive-tier entries are yielded unvalidated, deliberately.** The
    archive tier OVERRIDES an entry's literal status (`build_ready()`
    tallies every archived entry as `closed` "independent of what its
    frontmatter literally says"), so that value is not load-bearing for
    any reader — and `--validate` owns it directly via
    `_check_archive_tier()`. Validating it here would make a repo whose
    archive holds historical retired vocabulary unable to render its own
    index, which is the opposite of the migration posture this vocabulary
    collapse ships. A live entry is the reverse: its status IS what every
    reader routes on, so a malformed one must never be silently dropped by
    a filter that happens to exclude it anyway — validation runs before
    any status filter.
    """
    entries: list[tuple[Path, bool, dict[str, str]]] = []
    for path, is_archived in _entry_files(store):
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        status = frontmatter.get("status")
        if not is_archived and status not in CLOSED_STATUS_VOCABULARY:
            raise ValueError(
                f"{path.name}: entry has status {status!r}, outside the "
                "closed status vocabulary"
            )
        entries.append((path, is_archived, frontmatter))
    return entries


def live_entries(store: Path, status: str) -> list[tuple[str, dict[str, str]]]:
    """The live entries at `status`, as `(display_name, frontmatter)`
    pairs a caller can render or cite.

    `display_name` is the entry's frontmatter `name` when the key is
    present (even a `name` that disagrees with the filename stem — only
    `status` is validated by `iter_validated_entries()`, not the (i)
    name/stem agreement), or the filename stem when the key is absent
    entirely. This is live, not defensive: `check_queue_relation`'s
    callers string-match against this value for `in-queue:`/`displaces:`
    citations, so it is the string an author must cite even from an
    otherwise-invalid store.

    Archived entries are never returned: the archive tier overrides an
    entry's literal status, so a re-bet of an archived entry is not a
    thing this can surface. Raises ValueError via
    `iter_validated_entries()` on an out-of-vocabulary status.

    Returned in `_entry_files()`'s filename order.
    """
    return [
        (frontmatter.get("name", path.stem), frontmatter)
        for path, is_archived, frontmatter in iter_validated_entries(store)
        if not is_archived and frontmatter.get("status") == status
    ]


def _check_name(display: str, frontmatter: dict[str, str], stem: str) -> list[Violation]:
    name = frontmatter.get("name")
    if name is None:
        return [Violation("name", display, "frontmatter missing 'name' key")]
    if name != stem:
        return [Violation("name", display, f"frontmatter name '{name}' != filename stem '{stem}'")]
    return []


def _check_status(display: str, status: str | None) -> list[Violation]:
    if status is None:
        return [Violation("status", display, "frontmatter missing 'status' key")]
    if status not in CLOSED_STATUS_VOCABULARY:
        return [Violation("status", display, f"status '{status}' is not in the closed vocabulary")]
    return []


def _check_archive_tier(display: str, status: str | None, is_archived: bool) -> list[Violation]:
    """(iii) archive-tier agreement is one-directional: a LIVE entry
    carrying `status: closed` is legal (SHIPPED/CLOSED — SUPERSEDED
    migrated there without being archived)."""
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
    store's parent directory (docs/loom/PURPOSE.md beside
    docs/loom/backlog/). Its mere presence
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
    frontmatter: dict[str, str],
    by_status: dict[str, list[tuple[str, str]]],
) -> None:
    """Classify one LIVE entry into `by_status` in place.

    Takes the frontmatter its caller already parsed rather than re-reading
    the file: the vocabulary guard now lives once, upstream in
    `iter_validated_entries()`, so this function no longer re-derives it.
    Its remaining ValueError is a COUPLING GUARD, not a live condition:
    `CLOSED_STATUS_VOCABULARY` and `STATUS_SECTION_ORDER` hold the same
    three words (they differ only in order, which is the documented
    contract above), so every live entry reaching here has already been
    accepted upstream and the raise cannot fire today. It stays because
    the two lists are separate module constants and nothing else would
    notice if a word were added to one and not the other.
    """
    status = frontmatter.get("status")
    if status not in by_status:
        raise ValueError(
            f"{path.name}: live entry has status {status!r}, which has no "
            "section in STATUS_SECTION_ORDER"
        )
    name = frontmatter.get("name", path.stem)
    by_status[status].append((name, frontmatter.get("description", "")))


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

    # Route through the shared walk so this reader agrees with the other
    # three about which LIVE statuses are legal. Archive-tier entries are
    # skipped here and are NOT vocabulary-validated by any reader — the
    # tier overrides the status, and `_check_archive_tier()` owns it in
    # `--validate`. (This comment first shipped stating the opposite: it
    # described the alternative the same commit rejected. Round 5 found it
    # — a design call taken, with the prose beside it written for the road
    # not taken.)
    for path, is_archived, frontmatter in iter_validated_entries(store):
        if is_archived:
            continue
        _bucket_entry(path, frontmatter, by_status)

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

    Raises ValueError (caller decides exit codes) on a LIVE entry whose
    status is outside the closed vocabulary — via
    `iter_validated_entries()`, the one home of that guard. An
    unrecognized LIVE status must not be silently laundered into the
    excluded tally. An unrecognized ARCHIVED status is a different case
    and IS tallied as closed: the tier overrides the status, and
    `--validate` reports it via `_check_archive_tier()`.

    An entry physically under `archive/` is excluded regardless of its
    frontmatter `status:` — the archive tier overrides the status field. A `bet`-or-`open` entry carrying a
    `blocked:` field is excluded too (brief BI-2 — that is what the field is for). These
    are two distinct exclusion axes, tallied separately in the closing
    line: a `closed`/archive-tier entry is not actionable as written; a
    `blocked` entry is otherwise-ready and one `blocked:` line away from
    it. The exclusion is written against `bet`-or-`open` rather than
    `open` alone because it is the CODE's condition; invariant (iv)
    separately makes `blocked:` illegal on a `bet` entry, so the `bet`
    half is a guard against a store that already violates (iv), not a
    supported combination. An archive-tier entry is always tallied as `closed`
    (the archive tier overriding its status is exactly what makes it
    closed for `--ready`'s purposes, independent of what its frontmatter
    literally says).
    """
    entry_lines: dict[str, list[str]] = {status: [] for status in READY_STATUSES}
    counts: dict[str, int] = {status: 0 for status in READY_STATUSES}
    excluded_closed = 0
    excluded_blocked = 0

    for path, is_archived, frontmatter in iter_validated_entries(store):
        status = frontmatter.get("status")
        if is_archived or status not in READY_STATUSES:
            excluded_closed += 1
            continue
        if "blocked" in frontmatter:
            excluded_blocked += 1
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
        f"/ {excluded_closed} closed / {excluded_blocked} blocked"
    )
    return "\n".join(lines) + "\n"


def _run_validate(args: argparse.Namespace) -> int:
    """--validate (also the flagless default): check every entry's
    frontmatter against the store's invariants."""
    store = Path(args.store)
    try:
        violations = find_violations(store)
    except OSError as exc:
        print(f"backlog_index --validate: FAIL — store is unreadable ({exc}).")
        return 1
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
    except OSError as exc:
        print(f"backlog_index --write: FAIL — store is unreadable ({exc}).")
        return 1
    except ValueError as exc:
        print(f"backlog_index --write: FAIL — {exc}")
        return 1
    try:
        Path(args.output).write_text(text, encoding="utf-8")
    except OSError as exc:
        print(f"backlog_index --write: FAIL — {args.output} is unwritable ({exc}).")
        return 1
    # `.resolve()` touches the filesystem and can raise (symlink loops, an
    # unreadable parent). Reporting where the write landed must never be the
    # thing that turns a successful write into a traceback.
    try:
        landed = Path(args.output).resolve()
    except OSError:
        landed = Path(args.output).absolute()
    print(f"backlog_index --write: wrote {landed}")
    return 0


def _run_check(args: argparse.Namespace) -> int:
    """--check: regenerate the index in memory and diff it against
    --output without writing; exit 1 on drift or a missing --output file."""
    try:
        generated = build_index(Path(args.store))
    except OSError as exc:
        print(f"backlog_index --check: FAIL — store is unreadable ({exc}).")
        return 1
    except ValueError as exc:
        print(f"backlog_index --check: FAIL — {exc}")
        return 1

    output_path = Path(args.output)
    try:
        output_present = output_path.is_file()
    except OSError as exc:
        print(f"backlog_index --check: FAIL — {output_path} is unreadable ({exc}).")
        return 1
    if not output_present:
        print(
            f"backlog_index --check: FAIL — {output_path} does not exist; "
            "run --write first"
        )
        return 1

    try:
        committed = output_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"backlog_index --check: FAIL — {output_path} is unreadable ({exc}).")
        return 1
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
    except OSError as exc:
        print(f"backlog_index --ready: FAIL — store is unreadable ({exc}).")
        return 1
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
        default=None,
        help="path to write (--write) or compare against (--check) the "
             "generated index (default: BACKLOG.md beside --store's parent)",
    )
    args = parser.parse_args()

    # The index belongs beside ITS OWN store, not beside whatever directory
    # the process happens to stand in. A cwd-relative default let
    # `--write --store <other-repo>` overwrite the standing repo's
    # BACKLOG.md with another store's contents, silently — found by running
    # the thing, after six review rounds read past it (plan DL-30). For the
    # canonical layout (`--store docs/loom/backlog` from a repo root) the
    # derived path is byte-identical to the old default.
    if args.output is None:
        args.output = str(Path(args.store).parent / "BACKLOG.md")

    # `--store` is the ONLY way to locate the store here (there is no
    # `--repo-root`), so a typo in it used to buy a green validate: glob a
    # directory that is not there, get an empty list, and every invariant
    # holds vacuously. `--ready` reported an empty queue and `--write`
    # generated an empty index. A green bought with a typo is worse than a
    # red one. Absence of a store IS a legitimate state for a repo that
    # never adopted the queue layer — but that is the caller's judgment to
    # make (`check_queue_relation.py` reports a loud N/A at exit 0 for
    # exactly that); a script pointed at a store explicitly and unable to
    # find it has failed. Found by running the thing (plan DL-30), after
    # six review rounds read past it.
    store_path = Path(args.store)
    try:
        store_is_dir = store_path.is_dir()
        store_exists = store_path.exists()
    except OSError as exc:
        print(f"backlog_index: FAIL — store at {store_path} is unreadable ({exc}).")
        return 1
    if not store_is_dir:
        what = "is not a directory" if store_exists else "does not exist"
        print(
            f"backlog_index: FAIL — backlog store {what}: {store_path}. "
            "Check the --store path (it is not resolved against a repo root)."
        )
        return 1

    if not any(
        (
            args.validate,
            args.write,
            args.check,
            args.ready,
        )
    ):
        # Flagless invocation defaults to validate, mirroring
        # check_loom_memory_integrity.py's trio shape (formerly a "no mode
        # specified" parser error).
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

    return 0


if __name__ == "__main__":
    sys.exit(main())
