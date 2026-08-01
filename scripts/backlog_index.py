#!/usr/bin/env python3
"""Validate + (later) generate the loom family backlog store's index.

`docs/loom/backlog/README.md` is the store's format SSOT (charter). This
script's `--validate` mode enforces the three invariants the charter's
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

Deliberately narrower than `scripts/check_loom_memory_integrity.py`'s five
invariants: this store's index is *generated* from the entry files (Task 3),
which makes the memory checker's index-line invariants structurally
impossible to violate here. See the plan's "Kickoff decision — generating
the index removes three of the four invariants" note.

Frontmatter is a `---`-delimited `key: value` block, hand-parsed with
stdlib only (no PyYAML), mirroring check_loom_memory_integrity.py's
convention — the format is a small, store-local subset of YAML.

Validate-only in this task: `--write` and `--check` modes land in later
tasks. `--validate` never edits the store.

Usage:
    python3 scripts/backlog_index.py --validate [--store docs/loom/backlog]

Exit codes: 0 = clean, 1 = at least one invariant violation.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

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


@dataclass(frozen=True)
class Violation:
    kind: str  # "name" | "status" | "archive-tier"
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
    archived = sorted(archive_dir.glob("*.md")) if archive_dir.is_dir() else []
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

    return violations


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
    args = parser.parse_args()

    if not args.validate:
        parser.error("no mode specified; pass --validate")

    violations = find_violations(Path(args.store))
    if not violations:
        print("backlog_index --validate: OK — every invariant holds.")
        return 0

    print("backlog_index --validate: FAIL — the store's invariants are violated.\n")
    for violation in sorted(violations, key=lambda v: (v.file, v.kind)):
        print(f"  [{violation.kind}] {violation.file}: {violation.detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
