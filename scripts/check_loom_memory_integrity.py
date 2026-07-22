#!/usr/bin/env python3
"""Fail a loom-memory store that violates its own §Index invariants.

`docs/loom/memory/README.md` documents (§Format, §Index) four invariants that
keep the index the durable retrieval surface for the store's body files. They
were prose-only and already drifted once: PR #592 landed 2 orphan body files
with no index line, uncaught, because nothing mechanical checked it. This gate
mechanizes the same four invariants — the "mechanize the prose invariant"
pattern already used by check_version_bump.py.

The four invariants, all checked against `--store` (default
`docs/loom/memory`):

  (a) every body file (`<store>/*.md` except README.md) has an index line in
      README.md's §Index section.
  (b) every index line points to an existing body file.
  (c) filename (minus `.md`) == the file's frontmatter `name`.
  (d) the index-line description == the file's frontmatter `description`,
      byte-identical (both sides compared after `.strip()` — a bare
      leading/trailing space is not the invisible-byte drift this check
      exists to catch; see character-encoding hazards below).
  (e) no two index lines point at the same body file (a stale duplicate
      entry would otherwise be silently shadowed by `index_by_file`).

Frontmatter is a `---`-delimited `key: value` block, hand-parsed with stdlib
only (no PyYAML — third-party parsing here would fail external-surface-
grounding review for a format this small and store-local).

Validate-only: this script never edits the store. It prints every offender
plus which invariant it broke and exits 1; exits 0 when the store is clean.

Usage:
    python3 scripts/check_loom_memory_integrity.py [--store docs/loom/memory]

Exit codes: 0 = clean, 1 = at least one invariant violation.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

INDEX_HEADING = "## Index"
# `[name](file.md) — description` — the em dash (U+2014) is the documented
# separator (README.md §Index), not a hyphen.
# Assumes one index entry per line (README.md §Format's contract); a
# soft-wrapped multiline entry is out of scope and will simply not match.
INDEX_LINE_RE = re.compile(r"^\[([^\]]+)\]\(([^)]+)\)\s+—\s+(.*)$")


@dataclass(frozen=True)
class IndexEntry:
    name: str
    file: str
    description: str


@dataclass(frozen=True)
class Violation:
    invariant: str  # "a" | "b" | "c" | "d" | "e"
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


def parse_index_lines(readme_text: str) -> list[IndexEntry]:
    """Entries under `## Index`, up to the next `## ` heading or EOF."""
    lines = readme_text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == INDEX_HEADING) + 1
    except StopIteration:
        return []
    entries = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        match = INDEX_LINE_RE.match(line)
        if match:
            entries.append(IndexEntry(name=match.group(1), file=match.group(2), description=match.group(3)))
    return entries


def find_violations(store: Path) -> list[Violation]:
    readme = store / "README.md"
    readme_text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    index_entries = parse_index_lines(readme_text)
    index_by_file = {entry.file: entry for entry in index_entries}

    body_files = sorted(p for p in store.glob("*.md") if p.name != "README.md")
    body_names = {p.name for p in body_files}

    violations: list[Violation] = []

    # (a) every body file has an index line
    for path in body_files:
        if path.name not in index_by_file:
            violations.append(Violation("a", path.name, "no index line in README.md §Index"))

    # (b) every index line points to an existing body file
    for entry in index_entries:
        if entry.file not in body_names:
            violations.append(
                Violation("b", entry.file, f"index line '{entry.name}' points to a missing file")
            )

    # (c) filename == frontmatter name; (d) index description == frontmatter description
    for path in body_files:
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        stem = path.stem

        if name is None:
            violations.append(Violation("c", path.name, "frontmatter missing 'name' key"))
        elif name != stem:
            violations.append(
                Violation("c", path.name, f"frontmatter name '{name}' != filename stem '{stem}'")
            )

        entry = index_by_file.get(path.name)
        if entry is None:
            continue  # already reported under (a); nothing to compare descriptions against
        if description is None:
            violations.append(Violation("d", path.name, "frontmatter missing 'description' key"))
        else:
            # Strip BOTH sides: `description` (frontmatter) is already
            # `.strip()`ed in parse_frontmatter; the index side must match or
            # a bare trailing/leading space trips a spurious violation.
            index_desc = entry.description.strip()
            if index_desc != description:
                violations.append(
                    Violation(
                        "d",
                        path.name,
                        f"index desc {index_desc!r} != frontmatter desc {description!r}",
                    )
                )

    # (e) no two index lines point at the same body file
    file_counts = Counter(entry.file for entry in index_entries)
    for file, count in sorted(file_counts.items()):
        if count > 1:
            violations.append(Violation("e", file, f"appears in {count} index lines"))

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--store",
        default="docs/loom/memory",
        help="loom-memory store directory (default: docs/loom/memory)",
    )
    args = parser.parse_args()

    violations = find_violations(Path(args.store))
    if not violations:
        print("check_loom_memory_integrity: OK — every invariant holds.")
        return 0

    print("check_loom_memory_integrity: FAIL — the store's §Index invariants are violated.\n")
    for violation in sorted(violations, key=lambda v: (v.file, v.invariant)):
        print(f"  [{violation.invariant}] {violation.file}: {violation.detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
