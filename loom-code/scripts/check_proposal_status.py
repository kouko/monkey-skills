#!/usr/bin/env python3
"""Refuse a plan whose source proposal carries a non-ratified `Status:`
line (repair R2) — a small intake checker so a proposal like `Status:
exploration` cannot ship as a major version with nothing opposing it.

Mirrors `check_onramp_choice.py`'s CLI shape: a single positional path
argument, three exit codes, one stderr line naming the path and the
question to put to the user.

Grammar: the proposal's first `Status:` line resolves only when it
reads exactly:

    Status: ratified — <name>, <YYYY-MM-DD>

Any other value (`exploration`, `draft`, or anything else) is
unresolved, and so is a missing `Status:` line entirely.

Exit codes:

    0 — ratified.
    1 — the proposal file does not exist, or exists but is unreadable.
    2 — unresolved (non-ratified `Status:` value, or no `Status:` line
        found). Stderr names the proposal path and the exact question.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_STATUS_LINE = re.compile(r"^Status:\s*(?P<value>.*)$")
_RATIFIED = re.compile(r"^ratified\s*—\s*.+,\s*\d{4}-\d{2}-\d{2}\s*$")


def find_status_value(proposal_text: str) -> str | None:
    """The first `Status:` line's value (stripped), or None if the
    proposal has no such line."""
    for line in proposal_text.splitlines():
        match = _STATUS_LINE.match(line)
        if match is not None:
            return match.group("value").strip()
    return None


def is_ratified(status_value: str | None) -> bool:
    """Whether a `Status:` value resolves per the grammar above."""
    if status_value is None:
        return False
    return bool(_RATIFIED.match(status_value))


def build_question(proposal_path: Path, status_value: str | None) -> str:
    """The exact user-facing question for a non-ratified/missing status."""
    if status_value is None:
        found = "no 'Status:' line found"
    else:
        found = f"found 'Status: {status_value}'"
    return (
        f"{proposal_path}: {found} — a proposal must carry "
        "'Status: ratified — <name>, <YYYY-MM-DD>' before a plan can be "
        "drafted from it. Ratify it first, or point the plan at a "
        "different, already-ratified proposal."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check a proposal's 'Status:' line; exit 2 while it "
                    "is not recorded as ratified."
    )
    parser.add_argument("proposal_path", help="path to the proposal file")
    args = parser.parse_args(argv)

    proposal_path = Path(args.proposal_path)
    try:
        proposal_present = proposal_path.is_file()
    except OSError as exc:
        print(
            f"Error: proposal at {proposal_path} is unreadable ({exc}).",
            file=sys.stderr,
        )
        return 1
    if not proposal_present:
        print(f"Error: proposal file not found at {proposal_path}.", file=sys.stderr)
        return 1
    try:
        proposal_text = proposal_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(
            f"Error: proposal at {proposal_path} is unreadable ({exc}).",
            file=sys.stderr,
        )
        return 1

    status_value = find_status_value(proposal_text)
    if is_ratified(status_value):
        print(f"Proposal status in {proposal_path} is resolved (ratified).")
        return 0

    print(f"Error: {build_question(proposal_path, status_value)}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
