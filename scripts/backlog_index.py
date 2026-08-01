#!/usr/bin/env python3
"""Validate + (later) generate the loom family backlog store's index.

`docs/loom/backlog/README.md` is the store's format SSOT (charter). This
script's `--validate` mode enforces the four invariants the charter's
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

`--check` mode lands in a later task.

Usage:
    python3 scripts/backlog_index.py --validate [--store docs/loom/backlog]
    python3 scripts/backlog_index.py --write [--store docs/loom/backlog] [--output docs/loom/BACKLOG.md]

Exit codes: 0 = clean/written, 1 = at least one invariant violation
(--validate) or a build error (--write).
"""

from __future__ import annotations

import argparse
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
    kind: str  # "name" | "status" | "archive-tier" | "archived-date"
    file: str
    detail: str


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


def find_violations(store: Path) -> list[Violation]:
    violations: list[Violation] = []

    for path, is_archived in _entry_files(store):
        display = str(path.relative_to(store))
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        name = frontmatter.get("name")
        status = frontmatter.get("status")
        stem = path.stem

        # (i) filename stem == frontmatter name
        if name is None:
            violations.append(Violation("name", display, "frontmatter missing 'name' key"))
        elif name != stem:
            violations.append(
                Violation("name", display, f"frontmatter name '{name}' != filename stem '{stem}'")
            )

        # (ii) status is a member of the closed vocabulary
        if status is None:
            violations.append(Violation("status", display, "frontmatter missing 'status' key"))
        elif status not in CLOSED_STATUS_VOCABULARY:
            violations.append(
                Violation("status", display, f"status '{status}' is not in the closed vocabulary")
            )

        # (iii) archive-tier <-> status: archived agreement
        if status is not None:
            if is_archived and status != ARCHIVED_STATUS:
                violations.append(
                    Violation(
                        "archive-tier",
                        display,
                        f"entry is under archive/ but status is '{status}', not 'archived'",
                    )
                )
            elif not is_archived and status == ARCHIVED_STATUS:
                violations.append(
                    Violation(
                        "archive-tier",
                        display,
                        "entry carries status: archived but is not under archive/",
                    )
                )

        # (iv) archived: <date> is required (and date-shaped) on every
        # archive-tier entry, and must be absent on every live entry.
        # Charter: docs/loom/backlog/README.md:20,24-27 — "It carries no
        # meaning on a live entry and must not be set on one."
        archived_value = frontmatter.get("archived")
        if is_archived:
            if archived_value is None:
                violations.append(
                    Violation(
                        "archived-date",
                        display,
                        "archive-tier entry missing required 'archived: <YYYY-MM-DD>' field",
                    )
                )
            elif not _is_valid_date_shape(archived_value):
                violations.append(
                    Violation(
                        "archived-date",
                        display,
                        f"'archived' field {archived_value!r} is not a valid YYYY-MM-DD date",
                    )
                )
        elif archived_value is not None:
            violations.append(
                Violation(
                    "archived-date",
                    display,
                    f"live entry carries 'archived: {archived_value}' but must not set it",
                )
            )

    return violations


def build_index(store: Path) -> str:
    """Regenerate the index text per the plan's §Pinned index shape.

    Pure function of the entry files' frontmatter text: no filesystem
    writes, no git shell-outs, no wall-clock reads. That purity is what
    keeps two --write runs over unchanged input byte-identical.

    Raises ValueError (never exits the process itself — the caller
    decides exit codes) when an entry cannot be rendered: a live entry
    whose status falls outside the closed vocabulary, or an archived
    entry missing the `archived: <date>` field its Archived line needs.

    Note the division of labor with `find_violations()`: this function
    does NOT re-check `name` (it falls back to `path.stem`) or re-check
    that an archive-tier entry's `status` is actually `archived` — those
    are `--validate`'s job. Run `--validate` before `--write` if those
    invariants have not already been checked.
    """
    by_status: dict[str, list[tuple[str, str]]] = {status: [] for status in STATUS_SECTION_ORDER}
    archived_entries: list[tuple[str, str]] = []

    for path, is_archived in _entry_files(store):
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
            continue

        status = frontmatter.get("status")
        if status not in by_status:
            raise ValueError(
                f"{path.name}: live entry has status {status!r}, outside the "
                "closed vocabulary of live statuses"
            )
        description = frontmatter.get("description", "")
        by_status[status].append((name, description))

    for entries in by_status.values():
        entries.sort(key=lambda item: item[0])
    archived_entries.sort(key=lambda item: item[0])

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
        "--output",
        default="docs/loom/BACKLOG.md",
        help="path to write the generated index (only used with --write)",
    )
    args = parser.parse_args()

    if not args.validate and not args.write:
        parser.error("no mode specified; pass --validate or --write")

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

    return 0


if __name__ == "__main__":
    sys.exit(main())
