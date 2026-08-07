#!/usr/bin/env python3
"""Fail a loom-memory store that violates its own §Index invariants.

`docs/loom/memory/README.md` documents (§Format, §Index) five invariants that
keep the index the durable retrieval surface for the store's body files. They
were prose-only and already drifted once: PR #592 landed 2 orphan body files
with no index line, uncaught, because nothing mechanical checked it. This gate
mechanizes the same five invariants — the "mechanize the prose invariant"
pattern already used by check_version_bump.py.

The five invariants, all checked against `--store` (default
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

Default (no flags) is validate-only: this script never edits the store. It
prints every offender plus which invariant it broke and exits 1; exits 0
when the store is clean.

`--write` and `--check` (this addition) generate the §Index section instead
of validating it, mirroring `scripts/backlog_index.py`'s trio semantics:
entries are built from every body file's frontmatter (`name`, `description`),
sorted by name, and spliced into the `## Index` section between its heading
and the next `## ` heading or EOF — every other line (prose above the
entries, any section after) is left untouched. `--write` writes the result
back to `--store`'s README.md; `--check` rebuilds the same text in memory and
diffs it against the committed README.md without writing, exiting 1 on
drift. Both are pure functions of the body files' frontmatter text, which is
what makes two `--write` runs over unchanged input byte-identical.

Usage:
    python3 scripts/check_loom_memory_integrity.py [--store docs/loom/memory]
    python3 scripts/check_loom_memory_integrity.py --write [--store docs/loom/memory]
    python3 scripts/check_loom_memory_integrity.py --check [--store docs/loom/memory]

Exit codes: 0 = clean/written/matches, 1 = at least one invariant violation
(default validate mode) or drift / a build error (--write, --check).
"""

from __future__ import annotations

import argparse
import difflib
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


def build_entries(store: Path) -> list[IndexEntry]:
    """Every body file's frontmatter, as `IndexEntry`s, sorted by name.

    Raises ValueError — never falls back to the filename stem or an empty
    string — when a body file's frontmatter is missing `name`, has a `name`
    that disagrees with its own filename stem, or is missing `description`
    (invariants c/d). A silent fallback here would let `--write`/`--check`
    launder broken frontmatter into a clean-looking index (the store failing
    `--validate` while `--write` reports success); the caller's existing
    `except ValueError` handling in `_run_write`/`_run_check` turns this into
    a loud, non-writing failure that names the offending file.
    """
    body_files = sorted(p for p in store.glob("*.md") if p.name != "README.md")
    entries = []
    for path in body_files:
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        name = frontmatter.get("name")
        stem = path.stem
        if name is None:
            raise ValueError(f"{path.name}: frontmatter missing 'name' key; refusing to render a stem fallback")
        if name != stem:
            raise ValueError(
                f"{path.name}: frontmatter name {name!r} != filename stem {stem!r}; refusing to render a mismatched name"
            )
        description = frontmatter.get("description")
        if description is None:
            raise ValueError(f"{path.name}: frontmatter missing 'description' key; refusing to render a blank description")
        entries.append(IndexEntry(name=name, file=path.name, description=description))
    entries.sort(key=lambda entry: entry.name)
    return entries


def _format_index_line(entry: IndexEntry) -> str:
    return f"[{entry.name}]({entry.file}) — {entry.description}"


def splice_index_section(readme_text: str, entries: list[IndexEntry]) -> str:
    """Regenerate the `## Index` section's entry lines from `entries`.

    Every other line — prose above the entries, any section before or after
    — is left untouched. The entry-line block is the maximal contiguous run
    of lines matching `INDEX_LINE_RE` inside the section (real usage: they
    run straight to the section's end with no interleaved prose); when none
    are found (an empty index), the generated entries are inserted at the
    section's end, right after whatever prose is already there.

    Raises ValueError when `readme_text` has no `## Index` heading — there
    is nothing to splice into — or when the entry-line block it would
    replace (`entries_start` through `section_end`) contains any line that
    is NOT a recognized entry line. That region is wholly overwritten below;
    silently proceeding would drop trailing prose sitting between the last
    entry and EOF/the next heading. Legitimate preamble prose (between the
    heading and the first entry line, outside this region) is unaffected
    and always preserved verbatim.
    """
    lines = readme_text.splitlines()
    try:
        heading_idx = next(i for i, line in enumerate(lines) if line.strip() == INDEX_HEADING)
    except StopIteration:
        raise ValueError(f"README.md has no {INDEX_HEADING!r} heading to splice into")

    section_start = heading_idx + 1
    section_end = len(lines)
    for i in range(section_start, len(lines)):
        if lines[i].startswith("## "):
            section_end = i
            break

    entries_start = section_end
    for i in range(section_start, section_end):
        if INDEX_LINE_RE.match(lines[i]):
            entries_start = i
            break

    unrecognized = [(i + 1, lines[i]) for i in range(entries_start, section_end) if not INDEX_LINE_RE.match(lines[i])]
    if unrecognized:
        detail = "; ".join(f"line {lineno}: {content!r}" for lineno, content in unrecognized)
        raise ValueError(
            "README.md has unrecognized non-entry content inside the §Index entry "
            f"region that --write would otherwise silently drop: {detail}"
        )

    new_lines = lines[:entries_start] + [_format_index_line(entry) for entry in entries] + lines[section_end:]
    return "\n".join(new_lines) + "\n"


def _run_validate(store: Path) -> int:
    """The original, byte-untouched default (no-flag) behavior."""
    violations = find_violations(store)
    if not violations:
        print("check_loom_memory_integrity: OK — every invariant holds.")
        return 0

    print("check_loom_memory_integrity: FAIL — the store's §Index invariants are violated.\n")
    for violation in sorted(violations, key=lambda v: (v.file, v.invariant)):
        print(f"  [{violation.invariant}] {violation.file}: {violation.detail}")
    return 1


def _run_write(store: Path) -> int:
    readme = store / "README.md"
    readme_text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    try:
        new_text = splice_index_section(readme_text, build_entries(store))
    except ValueError as exc:
        print(f"check_loom_memory_integrity --write: FAIL — {exc}")
        return 1
    readme.write_text(new_text, encoding="utf-8")
    print(f"check_loom_memory_integrity --write: wrote {readme}")
    return 0


def _run_check(store: Path) -> int:
    readme = store / "README.md"
    if not readme.is_file():
        print(f"check_loom_memory_integrity --check: FAIL — {readme} does not exist; run --write first")
        return 1
    committed = readme.read_text(encoding="utf-8")
    try:
        generated = splice_index_section(committed, build_entries(store))
    except ValueError as exc:
        print(f"check_loom_memory_integrity --check: FAIL — {exc}")
        return 1

    if committed != generated:
        print(
            "check_loom_memory_integrity --check: FAIL — the committed §Index "
            f"has drifted from body-file frontmatter (compare against {readme}).\n"
        )
        diff = difflib.unified_diff(
            committed.splitlines(keepends=True),
            generated.splitlines(keepends=True),
            fromfile=f"{readme} (committed)",
            tofile="<regenerated from body-file frontmatter>",
        )
        sys.stdout.writelines(diff)
        return 1

    print(f"check_loom_memory_integrity --check: OK — {readme} matches body-file frontmatter.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--store",
        default="docs/loom/memory",
        help="loom-memory store directory (default: docs/loom/memory)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate the ## Index section from body-file frontmatter and write README.md",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate the ## Index section in memory and diff it against the committed "
        "README.md without writing; exit 1 on drift",
    )
    args = parser.parse_args()

    store = Path(args.store)
    if args.write:
        return _run_write(store)
    if args.check:
        return _run_check(store)
    return _run_validate(store)


if __name__ == "__main__":
    sys.exit(main())
