#!/usr/bin/env python3
"""Parser and checker for the repo store `docs/loom/ATTACK-CATALOGUE.md`
(plan `docs/loom/plans/2026-08-31-adversarial-audit-station.md` Task 2).
This module is the single owner of the store grammar; other tasks quote
its section headings and instance-line shape verbatim rather than
re-deriving them.

Grammar — three level-2 sections, in any order, each required:

    ## Guarded paths
    - <glob>
    - <glob>
    ...

    ## Instances
    - <class> | <target> | reproduced <YYYY-MM-DD> — pinned by <test-name>
    - <class> | <target> | held <YYYY-MM-DD>
    - <class> | <target> | not-applicable — <reason>

    ## Prose temptations
    - <one shortcut per bullet>

Usage:

    check_attack_catalogue.py <store> --repo <root>

Exit codes:

    0 — every section present, `## Guarded paths` non-empty, every
        `reproduced` instance names a `pinned by` test that resolves
        (a `def <name>` in some `test_*.py` under `--repo`, or the name
        appearing inside a `.sh` file under a `tests/` directory under
        `--repo`), every `held` instance carries a date. Prints one
        summary line with counts to stdout.
    1 — any refusal below fires; each prints one line to stderr naming
        the offending line's content and the refusal kind:

        unpinned    — a `reproduced` entry has no `pinned by`
        dangling    — the named test resolves to no `def <name>` in any
                       `test_*.py` under --repo, nor a name inside a
                       `.sh` file under a `tests/` directory
        undated     — a `held` entry has no date
        unguarded   — `## Guarded paths` is empty or absent
        incomplete  — any of the three sections is missing

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_SECTION_NAMES = ("Guarded paths", "Instances", "Prose temptations")

_HEADING_2_LINE = re.compile(r"^##\s+(.*?)\s*$")
_BULLET_LINE = re.compile(r"^-\s*(.+)$")

# One `## Instances` bullet: `<class> | <target> | <status>`.
_INSTANCE_LINE = re.compile(
    r"^(?P<klass>[^|]+?)\s*\|\s*(?P<target>[^|]+?)\s*\|\s*(?P<status>.+)$"
)

_REPRODUCED_STATUS = re.compile(
    r"^reproduced\s+(?P<date>\S+)(?:\s*—\s*pinned by\s*(?P<test>\S+))?\s*$"
)
_HELD_STATUS = re.compile(r"^held(?:\s+(?P<date>\S+))?\s*$")
_NOT_APPLICABLE_STATUS = re.compile(
    r"^not-applicable\s*—\s*(?P<reason>.+)$"
)

_DEF_LINE = re.compile(r"^def\s+(\w+)\s*\(", re.MULTILINE)


@dataclass
class Instance:
    klass: str
    target: str
    verdict: str  # "reproduced" | "held" | "not-applicable"
    line: str  # the raw bullet text, for diagnostics
    date: str | None = None
    pinned_by: str | None = None
    reason: str | None = None


@dataclass
class Store:
    guarded_paths: list[str] = field(default_factory=list)
    instances: list[Instance] = field(default_factory=list)
    prose_temptations: list[str] = field(default_factory=list)
    sections_present: set = field(default_factory=set)


class StoreError(Exception):
    """A refusal: (kind, message) — message names the offending line."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(message)
        self.kind = kind
        self.message = message


def _find_sections(text: str) -> dict[str, list[str]]:
    """Map section name -> list of bullet-content lines. A section
    heading not among `_SECTION_NAMES` is ignored."""
    lines = text.splitlines()
    heading_idxs = []
    for i, line in enumerate(lines):
        m = _HEADING_2_LINE.match(line)
        if m:
            heading_idxs.append((i, m.group(1)))

    sections: dict[str, list[str]] = {}
    for pos, (idx, name) in enumerate(heading_idxs):
        end = heading_idxs[pos + 1][0] if pos + 1 < len(heading_idxs) else len(lines)
        if name not in _SECTION_NAMES:
            continue
        body = lines[idx + 1:end]
        bullets = []
        for line in body:
            m = _BULLET_LINE.match(line.strip())
            if m:
                bullets.append(m.group(1).strip())
        sections[name] = bullets
    return sections


def parse_store(text: str) -> Store:
    """Parse the store's raw text into a `Store`. Does not validate — a
    missing section simply leaves the corresponding list empty and its
    name absent from `sections_present`; call `check_store` to enforce
    the refusal rules."""
    sections = _find_sections(text)
    store = Store()
    store.sections_present = set(sections.keys())

    store.guarded_paths = list(sections.get("Guarded paths", []))
    store.prose_temptations = list(sections.get("Prose temptations", []))

    for raw in sections.get("Instances", []):
        m = _INSTANCE_LINE.match(raw)
        if not m:
            # Not a well-formed instance line; skip — malformed lines
            # are not this parser's concern beyond the named refusals.
            continue
        klass = m.group("klass").strip()
        target = m.group("target").strip()
        status = m.group("status").strip()

        rm = _REPRODUCED_STATUS.match(status)
        if rm:
            store.instances.append(
                Instance(
                    klass=klass,
                    target=target,
                    verdict="reproduced",
                    line=raw,
                    date=rm.group("date"),
                    pinned_by=rm.group("test"),
                )
            )
            continue

        hm = _HELD_STATUS.match(status)
        if hm and status.startswith("held"):
            store.instances.append(
                Instance(
                    klass=klass,
                    target=target,
                    verdict="held",
                    line=raw,
                    date=hm.group("date"),
                )
            )
            continue

        nm = _NOT_APPLICABLE_STATUS.match(status)
        if nm:
            store.instances.append(
                Instance(
                    klass=klass,
                    target=target,
                    verdict="not-applicable",
                    line=raw,
                    reason=nm.group("reason").strip(),
                )
            )
            continue

        # Unrecognized status — record as-is with no verdict so the
        # checker can still see it exists; verdict left as raw status.
        store.instances.append(
            Instance(klass=klass, target=target, verdict=status, line=raw)
        )

    return store


def guarded_path_globs(store: Store) -> list[str]:
    """The `## Guarded paths` bullets, in document order."""
    return list(store.guarded_paths)


def _test_name_defined_under_repo(name: str, repo: Path) -> bool:
    for path in repo.rglob("test_*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in _DEF_LINE.finditer(text):
            if m.group(1) == name:
                return True

    for tests_dir in repo.rglob("tests"):
        if not tests_dir.is_dir():
            continue
        for sh_path in tests_dir.glob("*.sh"):
            try:
                text = sh_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if re.search(rf"\b{re.escape(name)}\b", text):
                return True

    return False


def check_store(store: Store, repo: Path) -> list[StoreError]:
    """Every refusal the store fires, in a stable order: `incomplete`
    first (a missing section makes further checks meaningless for that
    section), then `unguarded`, then per-instance checks in document
    order."""
    errors: list[StoreError] = []

    missing = [name for name in _SECTION_NAMES if name not in store.sections_present]
    if missing:
        errors.append(
            StoreError(
                "incomplete",
                "Error: incomplete — missing section(s) "
                + ", ".join(f"'## {n}'" for n in missing),
            )
        )

    if not store.guarded_paths:
        errors.append(
            StoreError(
                "unguarded",
                "Error: unguarded — '## Guarded paths' is empty or absent — "
                "at least one glob is required.",
            )
        )

    for inst in store.instances:
        if inst.verdict == "reproduced":
            if not inst.pinned_by:
                errors.append(
                    StoreError(
                        "unpinned",
                        f"Error: unpinned — reproduced entry has no 'pinned by' "
                        f"— line: '{inst.line}'",
                    )
                )
            elif not _test_name_defined_under_repo(inst.pinned_by, repo):
                errors.append(
                    StoreError(
                        "dangling",
                        f"Error: dangling — test name '{inst.pinned_by}' not found "
                        f"— line: '{inst.line}'",
                    )
                )
        elif inst.verdict == "held":
            if not inst.date:
                errors.append(
                    StoreError(
                        "undated",
                        f"Error: undated — held entry has no date "
                        f"— line: '{inst.line}'",
                    )
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Parse and check the repo attack-catalogue store "
            "(docs/loom/ATTACK-CATALOGUE.md grammar)."
        )
    )
    parser.add_argument("store", type=Path, help="Path to the store markdown file.")
    parser.add_argument(
        "--repo", type=Path, required=True, help="Repo root, for test-name resolution."
    )
    args = parser.parse_args(argv)

    try:
        text = args.store.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error: cannot read store '{args.store}': {exc}", file=sys.stderr)
        return 1

    store = parse_store(text)
    errors = check_store(store, args.repo)

    if errors:
        for err in errors:
            print(err.message, file=sys.stderr)
        return 1

    print(
        f"OK: {len(store.guarded_paths)} guarded path(s), "
        f"{len(store.instances)} instance(s), "
        f"{len(store.prose_temptations)} prose temptation(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
