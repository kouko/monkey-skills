#!/usr/bin/env python3
"""Betting-moment checker: every live `COMMITTED-NEXT` backlog entry
must carry a well-formed `serves:` line, checked against
`docs/loom/PURPOSE.md` — same family and exit-code contract as
`check_onramp_choice.py` / `check_direction_freshness.py`.

Grammar SSOT: `backlog_index._is_well_formed_serves` — this script
imports it rather than re-implementing it, so the two-form grammar
(`serves: <text>` / `serves: unrelated — <reason>`) never drifts across
the two checkers that enforce it (plan Task 1's `--validate` path, and
this betting-moment path).

`PURPOSE.md` is a FOUNDATIONAL artifact (the arc's Decision), not an
optional one: a repo with live COMMITTED-NEXT entries but no
`PURPOSE.md` is not silently exempt — it is asked to write one. A
fresh repo with nothing committed yet is never blocked, so absence of
the file is only checked once a live entry exists. This script treats the file's body as wholly opaque — it never parses
for any bold sub-label sketched elsewhere in the convention (Why /
Done-when / Goal / Success). Those labels are advisory only, by
design: no convention for the file's internal structure is
mechanically enforced here or in loom-design's validator. A checker
keying on them would break on the second repo that adopts this
convention with a different sub-structure.

Exit codes:

    0 — every live COMMITTED-NEXT entry has a well-formed `serves:`
        line and `docs/loom/PURPOSE.md` exists, OR there are no live
        COMMITTED-NEXT entries at all (nothing to bet on yet).
    1 — the given backlog store path does not exist or is not a
        readable directory.
    2 — either of two distinct causes, distinguishable by message:
        (a) a live COMMITTED-NEXT entry exists but `PURPOSE.md` is
            absent — stderr asks the user to write one;
        (b) a live COMMITTED-NEXT entry lacks a well-formed `serves:`
            line — stderr names the offending entry and the question
            the user must answer.

Stdlib only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from backlog_index import _entry_files, _is_well_formed_serves, _purpose_path_for, parse_frontmatter


def find_committed_next_entries(store: Path) -> list[tuple[str, dict[str, str]]]:
    """Every live COMMITTED-NEXT entry (in `_entry_files()` order) as
    `(display_name, frontmatter)`. Archived entries are never checked —
    a closed entry cannot be re-bet."""
    entries = []
    for path, is_archived in _entry_files(store):
        if is_archived:
            continue
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        if frontmatter.get("status") != "COMMITTED-NEXT":
            continue
        name = frontmatter.get("name", path.stem)
        entries.append((name, frontmatter))
    return entries


def find_offending_entry(
    entries: list[tuple[str, dict[str, str]]]
) -> tuple[str, str | None] | None:
    """The first entry (in `entries` order) whose `serves` field is
    missing or malformed, as `(display_name, serves_value)`, or None if
    every entry is well-formed."""
    for name, frontmatter in entries:
        serves = frontmatter.get("serves")
        if serves is None or not _is_well_formed_serves(serves):
            return (name, serves)
    return None


def build_purpose_missing_question(purpose_path: Path) -> str:
    """The exact user-facing question when `PURPOSE.md` is absent but a
    live COMMITTED-NEXT entry exists — shared by `main()`'s stderr
    message."""
    return (
        f"no {purpose_path} found, but a COMMITTED-NEXT backlog entry "
        "exists. What is this repo's purpose? Write it to "
        f"{purpose_path} before betting on this entry."
    )


def build_serves_question(name: str, purpose_path: Path) -> str:
    """The exact user-facing question for an offending entry — shared
    by `main()`'s stderr message."""
    return (
        f"backlog entry '{name}' is COMMITTED-NEXT but has no well-formed "
        f"'serves' line. How does it serve the purpose recorded in "
        f"{purpose_path}? Record the answer as 'serves: <how this "
        "serves the purpose>' or 'serves: unrelated — <reason>'."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check every live COMMITTED-NEXT backlog entry "
                    "carries a well-formed 'serves:' line against "
                    "docs/loom/PURPOSE.md."
    )
    parser.add_argument("store_path", help="path to the backlog store directory")
    args = parser.parse_args(argv)

    store = Path(args.store_path)
    try:
        if not store.is_dir():
            print(f"Error: backlog store not found at {store}.", file=sys.stderr)
            return 1
    except OSError as exc:
        print(f"Error: backlog store at {store} is unreadable ({exc}).", file=sys.stderr)
        return 1

    try:
        entries = find_committed_next_entries(store)
    except OSError as exc:
        print(f"Error: backlog store at {store} is unreadable ({exc}).", file=sys.stderr)
        return 1

    if not entries:
        print(
            "North-star link check: OK — no live COMMITTED-NEXT backlog "
            "entries to check yet."
        )
        return 0

    purpose_path = _purpose_path_for(store)
    if not purpose_path.is_file():
        print(f"Error: {build_purpose_missing_question(purpose_path)}", file=sys.stderr)
        return 2

    offending = find_offending_entry(entries)
    if offending is None:
        print(
            "North-star link check: OK — every live COMMITTED-NEXT entry "
            "carries a well-formed 'serves' line."
        )
        return 0

    name, _serves = offending
    print(f"Error: {build_serves_question(name, purpose_path)}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
