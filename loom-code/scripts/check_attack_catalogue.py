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
                       `test_*.py` under --repo (module-level or a
                       class-body method, resolved by parsing the AST —
                       a `def` sitting inside a docstring or comment
                       never counts), nor a name on a real command line
                       in a `.sh` file under a `tests/` directory (a
                       `.sh` line is comment-stripped first — a name
                       appearing only after `#`, or on a line whose
                       first non-space character is `#`, never counts)
        undated     — a `held` entry has no date
        unguarded   — `## Guarded paths` is empty or absent
        incomplete  — any of the three sections is missing
        malformed   — an `## Instances` status starts with `reproduced`
                       / `held` / `not-applicable` but does not fully
                       match that status's grammar (e.g. `pinned by`
                       with no name after it), or matches none of the
                       three tokens at all

A `pinned by` name resolving to a real, collected test proves only that
the name EXISTS somewhere a runner would find it — this module never
checks whether that test actually exercises the named vector. That
relevance judgment is out of scope for a machine check; the
spec-reviewer judges it by reading the test body against the vector.

Stdlib only.
"""

from __future__ import annotations

import argparse
import ast
import datetime
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
    r"^reproduced\s+(?P<date>\S+)(?:\s*—\s*pinned by\s*(?P<test>\S*))?\s*$"
)
_HELD_STATUS = re.compile(r"^held(?:\s+(?P<date>\S+))?\s*$")
_NOT_APPLICABLE_STATUS = re.compile(
    r"^not-applicable\s*—\s*(?P<reason>.+)$"
)



@dataclass
class Instance:
    klass: str
    target: str
    verdict: str  # "reproduced" | "held" | "not-applicable" | "malformed"
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
    heading not among `_SECTION_NAMES` is ignored.

    Raises `StoreError("malformed", …)` if any of `_SECTION_NAMES`
    appears as a `## ` heading more than once — a dict-assignment
    `sections[name] = bullets` would otherwise let the later heading
    silently replace the earlier one's bullets rather than refusing."""
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
        if name in sections:
            raise StoreError(
                "malformed",
                f"Error: malformed — duplicate '## {name}' section heading "
                f"— a later '## {name}' would silently replace the earlier "
                f"one's bullets.",
            )
        body = lines[idx + 1:end]
        bullets = []
        for line in body:
            m = _BULLET_LINE.match(line.strip())
            if m:
                bullets.append(m.group(1).strip())
        sections[name] = bullets
    return sections


def _is_iso_date(value: str) -> bool:
    """True only for a real ISO calendar date (`YYYY-MM-DD`, no
    out-of-range month/day) — `\\S+` in `_REPRODUCED_STATUS` /
    `_HELD_STATUS` would otherwise accept any non-space token."""
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


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
            # Not a well-formed `<class> | <target> | <status>` line at
            # all — no status to classify, so it cannot be "malformed"
            # in the sense check_store reports; skip as before.
            continue
        klass = m.group("klass").strip()
        target = m.group("target").strip()
        status = m.group("status").strip()

        if status.startswith("reproduced"):
            rm = _REPRODUCED_STATUS.match(status)
            # `test` is None when "— pinned by" was never attempted (the
            # legal unpinned case check_store flags separately), "" when
            # "pinned by" was attempted but named nothing (a bypass CQ-2
            # closes: that must never resolve as a legal unpinned entry),
            # and a real value otherwise.
            if rm is None or rm.group("test") == "" or not _is_iso_date(rm.group("date")):
                store.instances.append(
                    Instance(klass=klass, target=target, verdict="malformed", line=raw)
                )
            else:
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

        if status.startswith("held"):
            hm = _HELD_STATUS.match(status)
            if hm is None or (hm.group("date") is not None and not _is_iso_date(hm.group("date"))):
                store.instances.append(
                    Instance(klass=klass, target=target, verdict="malformed", line=raw)
                )
            else:
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

        if status.startswith("not-applicable"):
            nm = _NOT_APPLICABLE_STATUS.match(status)
            if nm is None:
                store.instances.append(
                    Instance(klass=klass, target=target, verdict="malformed", line=raw)
                )
            else:
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

        # Status names none of the three tokens at all.
        store.instances.append(
            Instance(klass=klass, target=target, verdict="malformed", line=raw)
        )

    return store


def guarded_path_globs(store: Store) -> list[str]:
    """The `## Guarded paths` bullets, in document order."""
    return list(store.guarded_paths)


def _defined_function_names(path: Path) -> set[str]:
    """Every `def`/`async def` name at module level or inside a class
    body in `path`, resolved by parsing the AST — so a `def` sitting
    inside a docstring, a comment, or any other string literal can never
    satisfy a `pinned by` claim the way a raw-text scan would. Unreadable
    or unparsable files resolve to no names rather than raising."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()

    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
    return names


def _strip_sh_comments(text: str) -> str:
    """A simple line-based comment strip for a `.sh` file: a line whose
    first non-space character is `#` is dropped entirely, and the `#…`
    tail of any other line is dropped too. Not a shell parser — it does
    not know about `#` inside a quoted string — but good enough to keep
    a name that appears only in a comment from grounding a `pinned by`
    claim, which is the only thing this search needs."""
    kept_lines = []
    for line in text.splitlines():
        if line.strip().startswith("#"):
            continue
        kept_lines.append(line.split("#", 1)[0])
    return "\n".join(kept_lines)


# Path components a runner never collects tests from — a pin resolved
# only under one of these (or any hidden dir, "." prefix) is dangling
# even when the `def`/name literally exists on disk.
_EXCLUDED_DIR_NAMES = {
    "vendor",
    "node_modules",
    ".git",
    "__pycache__",
    "site-packages",
    ".venv",
    "venv",
    "build",
    "dist",
}


def _under_excluded_dir(path: Path, repo: Path) -> bool:
    try:
        rel_dir_parts = path.relative_to(repo).parts[:-1]
    except ValueError:
        rel_dir_parts = path.parts[:-1]
    return any(
        part.lower() in _EXCLUDED_DIR_NAMES or part.startswith(".")
        for part in rel_dir_parts
    )


def _test_name_defined_under_repo(name: str, repo: Path) -> bool:
    for path in repo.rglob("test_*.py"):
        if _under_excluded_dir(path, repo):
            continue
        if name in _defined_function_names(path):
            return True

    for tests_dir in repo.rglob("tests"):
        if not tests_dir.is_dir():
            continue
        if _under_excluded_dir(tests_dir / "x", repo):
            continue
        for sh_path in tests_dir.glob("*.sh"):
            try:
                text = sh_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if re.search(rf"\b{re.escape(name)}\b", _strip_sh_comments(text)):
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
        if inst.verdict == "malformed":
            errors.append(
                StoreError(
                    "malformed",
                    f"Error: malformed — status does not match the "
                    f"reproduced/held/not-applicable grammar "
                    f"— line: '{inst.line}'",
                )
            )
        elif inst.verdict == "reproduced":
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

    try:
        store = parse_store(text)
    except StoreError as exc:
        print(exc.message, file=sys.stderr)
        return 1

    try:
        errors = check_store(store, args.repo)
    except OSError as exc:
        print(f"Error: cannot scan repo '{args.repo}': {exc}", file=sys.stderr)
        return 1

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
