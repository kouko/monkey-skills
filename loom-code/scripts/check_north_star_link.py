#!/usr/bin/env python3
"""Betting-moment checker: every live `bet` backlog entry
must carry a well-formed `serves:` line, checked against
`docs/loom/PURPOSE.md` — same family and exit-code contract as
`check_onramp_choice.py`.

Grammar SSOT: `backlog_index._is_well_formed_serves` — this script
imports it rather than re-implementing it, so the two-form grammar
(`serves: <text>` / `serves: unrelated — <reason>`) never drifts across
the two checkers that enforce it (plan Task 1's `--validate` path, and
this betting-moment path).

`PURPOSE.md` is a FOUNDATIONAL artifact (the arc's Decision), not an
optional one: a repo with live `bet` entries but no
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

    0 — every live `bet` entry has a well-formed `serves:`
        line and `docs/loom/PURPOSE.md` exists, OR there are no live
        `bet` entries at all (nothing to bet on yet).
    1 — the given backlog store path does not exist or is not a
        readable directory, OR `docs/loom/PURPOSE.md` exists but is
        unreadable (distinct from absent, which is exit 2 — absence is a
        question for the user, unreadability is a permissions fix), OR an
        entry's `status` falls outside the closed status vocabulary (`backlog_index.CLOSED_STATUS_VOCABULARY`)
        — a malformed entry fails loudly rather than being silently
        dropped from the live-bet set it might belong to (mirrors
        `check_queue_relation.py`'s `live_bet_names()` over the same
        bytes).
    2 — one of three distinct causes, distinguishable by message:
        (a) a live `bet` entry exists but `PURPOSE.md` is
            absent — stderr asks the user to write one;
        (b) `PURPOSE.md` exists but is still unanswered — either the
            shipped template's placeholder text is untouched, or the
            file records a bare `not yet` deferral with no reason —
            stderr names the template state and the `not yet — <reason>`
            escape hatch;
        (c) a live `bet` entry lacks a well-formed `serves:`
            line — stderr names the offending entry and the question
            the user must answer.

Cause (b) treats `PURPOSE.md`'s body as opaque prose except for two
narrow, literal probes it is licensed to make: the shipped template's
own placeholder text (loom-code ships that string, so it controls it),
and the phrase `not yet` as a deferral marker — the family's existing
three-state grammar (`serves: unrelated — <reason>`,
`check_onramp_choice.py`'s `not fired — <reason>`), applied here as
`not yet — <reason>`. The `not yet` probe is anchored to the start of
a line (optionally after a generic bold-emphasis prefix) rather than
matched anywhere in the file, so the template's own instructional
sentence explaining the escape hatch ("if the answer is not yet
knowable, replace...") can never be mistaken for the user's answer.
Neither probe keys on any bold sub-label (Why / Done-when / Goal /
Success) sketched elsewhere in the convention — those remain wholly
unenforced, by design.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from backlog_index import (
    _is_well_formed_serves,
    _purpose_path_for,
    live_entries,
)

# The shipped template's own placeholder text (templates/PURPOSE.md) —
# loom-code controls this literal string. Its presence means the file
# was scaffolded but never edited. Deliberately NOT the bold sub-label
# beside it — see module docstring.
_TEMPLATE_PLACEHOLDER = "_(one sentence — why this product exists)_"

# The `not yet` deferral marker, mirroring `serves: unrelated —
# <reason>` / `check_onramp_choice.py`'s `not fired — <reason>`.
# Anchored to the START of a line (optionally after a generic
# `**...:**` bold-emphasis prefix) rather than matched anywhere in the
# file: the shipped template's own instructional prose explains the
# escape hatch mid-sentence ("if the answer is not yet knowable,
# replace the placeholder below with `not yet — <reason>`") and a
# bare "matched anywhere" scan finds THAT occurrence first, which has
# no reason, and never reaches the line the user actually edited. The
# line-start anchor is structural/positional only — it does not key on
# any specific label text ("Why", "Done when", ...), so it stays
# licensed under the same no-bold-label-parsing boundary as the rest
# of this module. A reason is non-empty text after an em-dash or `--`;
# without one, the deferral is bare and does not resolve.
_NOT_YET_RE = re.compile(
    r"^\s*(?:\*\*[^*\n]+\*\*\s*)?not yet\b(?:\s*(?:—|--)\s*(?P<reason>\S.*))?",
    re.MULTILINE,
)


def find_bet_entries(store: Path) -> list[tuple[str, dict[str, str]]]:
    """The live bet entries a caller can check for a `serves:` line.

    Each pair's display name is the entry's frontmatter `name`, or the
    filename stem when absent — see `live_entries()` for why that
    fallback is live rather than defensive. Returned in
    `_entry_files()`'s filename order — `find_offending_entry()` relies
    on it to pick a deterministic "first" offender.

    Archived entries are never checked — a closed entry cannot be
    re-bet.

    Raises ValueError (caller decides exit codes) on a status outside the
    closed status vocabulary — the guard lives once, in
    `backlog_index.iter_validated_entries()`, which `live_entries()`
    walks: malformed frontmatter must fail loudly, never be silently
    dropped as nothing-to-check."""
    return live_entries(store, "bet")


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


def determine_purpose_state(purpose_path: Path) -> str:
    """One of `"absent"` / `"template"` / `"answered"`. `"template"`
    covers both an unedited scaffold and a bare `not yet` deferral with
    no reason — both leave nothing actionable recorded. A `not yet —
    <reason>` deferral (non-empty reason) counts as `"answered"`,
    regardless of whether the template's own placeholder text is still
    present elsewhere in the file — the deferral IS the answer."""
    if not purpose_path.is_file():
        return "absent"
    text = purpose_path.read_text(encoding="utf-8")  # OSError -> main() exit 1
    not_yet = _NOT_YET_RE.search(text)
    if not_yet is not None:
        reason = not_yet.group("reason")
        if reason and reason.strip():
            return "answered"
        return "template"
    if _TEMPLATE_PLACEHOLDER in text:
        return "template"
    return "answered"


def build_purpose_missing_question(purpose_path: Path) -> str:
    """The exact user-facing question when `PURPOSE.md` is absent but a
    live `bet` entry exists — shared by `main()`'s stderr
    message."""
    return (
        f"no {purpose_path} found, but a bet backlog entry "
        "exists. What is this repo's purpose? Write it to "
        f"{purpose_path} before betting on this entry."
    )


def build_purpose_template_question(purpose_path: Path) -> str:
    """The exact user-facing question when `PURPOSE.md` exists but is
    still unanswered (shipped template untouched, or a bare `not yet`
    with no reason) — distinct from the absent-file message so the
    user's next action is clear."""
    return (
        f"{purpose_path} still carries the shipped template's placeholder "
        "text (or an unexplained 'not yet'). What is this repo's purpose? "
        "Write it there, or if you genuinely cannot say yet, record "
        "'not yet — <reason>' in place of the placeholder."
    )


def build_serves_question(name: str, purpose_path: Path) -> str:
    """The exact user-facing question for an offending entry — shared
    by `main()`'s stderr message."""
    return (
        f"backlog entry '{name}' is a bet but has no well-formed "
        f"'serves' line. How does it serve the purpose recorded in "
        f"{purpose_path}? Record the answer as 'serves: <how this "
        "serves the purpose>' or 'serves: unrelated — <reason>'."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check every live bet backlog entry "
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
        entries = find_bet_entries(store)
    except OSError as exc:
        print(f"Error: backlog store at {store} is unreadable ({exc}).", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not entries:
        print(
            "North-star link check: OK — no live bet backlog "
            "entries to check yet."
        )
        return 0

    purpose_path = _purpose_path_for(store)
    # Same guard as the store read above: an unreadable PURPOSE.md is a
    # different fact from an absent one (absent is a legitimate exit-2
    # question to the user), and neither may surface as a traceback.
    try:
        purpose_state = determine_purpose_state(purpose_path)
    except OSError as exc:
        print(
            f"Error: {purpose_path} is unreadable ({exc}).", file=sys.stderr
        )
        return 1
    if purpose_state == "absent":
        print(f"Error: {build_purpose_missing_question(purpose_path)}", file=sys.stderr)
        return 2
    if purpose_state == "template":
        print(f"Error: {build_purpose_template_question(purpose_path)}", file=sys.stderr)
        return 2

    offending = find_offending_entry(entries)
    if offending is None:
        print(
            "North-star link check: OK — every live bet entry "
            "carries a well-formed 'serves' line."
        )
        return 0

    name, _serves = offending
    print(f"Error: {build_serves_question(name, purpose_path)}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
