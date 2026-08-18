#!/usr/bin/env python3
"""Parse a handoff brief's `## Design-side on-ramp` line and exit
non-zero while the on-ramp fired but was resolved by anything other
than an explicit user (or standing) choice.

Grammar (SSOT: `loom-code/skills/brainstorming/references/
handoff-brief-format.md` `### `## Design-side on-ramp``) — exactly one
of these four canonical forms is well-formed:

    not fired — <reason>
    fired: rows <n,...> — user chose <detour|direct>
    fired: rows <n,...> — standing <detour|direct> (DIRECTION.md)
    pending

Any other wording — including lookalikes such as `offered — direct per
repo precedent` or a missing line entirely — is *unresolved*: lookalike
wording never resolves the gate (see
`docs/loom/memory/section-gate-must-flag-entry-lookalikes-not-just-
matches.md`). The `standing` form additionally requires every cited row
to be named in the caller's `standing` mapping (DIRECTION.md wiring
lands in a later task; this script's CLI always passes an empty
mapping today).

The on-ramp line may appear either as a `## Design-side on-ramp`
heading followed by its value on the next non-blank line, or inline —
`Design-side on-ramp: <value>`, optionally bulleted, bolded, and/or
blockquoted (`> **Design-side on-ramp**: <value>`). Both forms are
accepted for LOCATING the line; the VALUE grammar above is strict
regardless of which form located it.

Exit codes:

    0 — `resolved` or `not_fired`.
    1 — the brief file does not exist.
    2 — `unresolved` (fired but not recorded as an explicit choice, a
        pending answer, or a missing/malformed line). Stderr names the
        brief path and the exact question to put to the user.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- line location -----------------------------------------------------

_HEADING_LINE = re.compile(r"^##\s+Design-side on-ramp\s*$")

# Inline form: optional blockquote `>`, optional bullet `-`, optional
# bold `**...**` around the label, then `:` and the value. Covers every
# corpus spelling seen: `Design-side on-ramp: ...`,
# `- Design-side on-ramp: ...`, `**Design-side on-ramp**: ...`,
# `> Design-side on-ramp: ...`, `> **Design-side on-ramp**: ...`.
_INLINE_LINE = re.compile(
    r"^(?:>\s*)?(?:-\s*)?\*{0,2}Design-side on-ramp\*{0,2}\s*:\s*(?P<value>.*)$"
)


def _find_onramp_value_line(brief_text: str) -> str | None:
    """The on-ramp line's value (stripped), from whichever corpus form
    is found first in document order, or None if neither form is
    present."""
    lines = brief_text.splitlines()
    for i, raw in enumerate(lines):
        inline = _INLINE_LINE.match(raw)
        if inline is not None:
            return inline.group("value").strip()
        if _HEADING_LINE.match(raw):
            for nxt in lines[i + 1:]:
                if nxt.strip():
                    return nxt.strip()
            return None
    return None


# --- value grammar -------------------------------------------------------

_NOT_FIRED = re.compile(r"^not fired\s*—\s*.+$")
_ROWS = r"(?P<rows>\d+(?:\s*,\s*\d+)*)"
_FIRED_USER = re.compile(
    rf"^fired:\s*rows\s*{_ROWS}\s*—\s*user chose (?:detour|direct)\s*$"
)
_FIRED_STANDING = re.compile(
    rf"^fired:\s*rows\s*{_ROWS}\s*—\s*standing (?:detour|direct) "
    r"\(DIRECTION\.md\)\s*$"
)
_FIRED_ROWS_PREFIX = re.compile(rf"^fired:\s*rows\s*{_ROWS}\b")


def _parse_rows(rows_text: str) -> list[int]:
    return [int(part.strip()) for part in rows_text.split(",")]


@dataclass
class Result:
    status: str  # "resolved" | "unresolved" | "not_fired"
    rows: list[int] = field(default_factory=list)
    message: str = ""


def resolve(brief_text: str, standing: dict[int, str]) -> Result:
    """Resolve a brief's on-ramp line against the canonical grammar.

    `standing` maps row number -> chosen value, per DIRECTION.md's
    `## On-ramp standing choices` section (wired by a later task); the
    `fired: rows <n> — standing <detour|direct> (DIRECTION.md)` form is
    resolved only when every cited row is present in this mapping."""
    value = _find_onramp_value_line(brief_text)
    if value is None:
        return Result(
            "unresolved", [],
            "no '## Design-side on-ramp' line found in the brief",
        )

    if _NOT_FIRED.match(value):
        return Result("not_fired", [], value)

    if _FIRED_USER.match(value):
        rows = _parse_rows(_FIRED_USER.match(value).group("rows"))
        return Result("resolved", rows, value)

    standing_match = _FIRED_STANDING.match(value)
    if standing_match is not None:
        rows = _parse_rows(standing_match.group("rows"))
        if all(row in standing for row in rows):
            return Result("resolved", rows, value)
        return Result("unresolved", rows, value)

    # `pending`, a malformed `fired:` line, or any other wording — all
    # unresolved. If it at least names rows (a `fired: rows <n> ...`
    # attempt that just isn't the well-formed user/standing form), keep
    # them for a more specific CLI message; otherwise rows stay empty.
    rows_prefix = _FIRED_ROWS_PREFIX.match(value)
    rows = _parse_rows(rows_prefix.group("rows")) if rows_prefix else []
    return Result("unresolved", rows, value)


# --- CLI -------------------------------------------------------------


def _resolve_repo_root(explicit: str | None, brief_dir: Path) -> Path:
    if explicit is not None:
        return Path(explicit)
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=brief_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return Path.cwd()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check a handoff brief's '## Design-side on-ramp' "
                    "line; exit 2 while it fired but was not recorded "
                    "as an explicit user (or standing) choice."
    )
    parser.add_argument("brief_path", help="path to the handoff brief file")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="repo root for future DIRECTION.md resolution (default: "
             "`git rev-parse --show-toplevel` of the brief's directory, "
             "falling back to cwd)",
    )
    args = parser.parse_args(argv)

    brief_path = Path(args.brief_path)
    if not brief_path.is_file():
        print(f"Error: brief file not found at {brief_path}.", file=sys.stderr)
        return 1
    brief_text = brief_path.read_text(encoding="utf-8")

    # Resolved but unused beyond this point in this task — DIRECTION.md
    # standing-choices wiring (which consumes it) lands in a later task
    # of this same plan; computing it here keeps the CLI shape stable.
    _resolve_repo_root(args.repo_root, brief_path.resolve().parent)

    result = resolve(brief_text, {})

    if result.status in ("resolved", "not_fired"):
        print(
            f"Design-side on-ramp in {brief_path} is resolved "
            f"({result.status})."
        )
        return 0

    if result.rows:
        rows_str = ",".join(str(row) for row in result.rows)
        question = (
            f"Design-side on-ramp: rows {rows_str} fired — detour into "
            "loom-design first, or go direct? Record the answer as "
            f"`fired: rows {rows_str} — user chose <detour|direct>`"
        )
    else:
        question = (
            "Design-side on-ramp fired — detour into loom-design first, "
            "or go direct? Record the answer as `fired: rows <n> — user "
            "chose <detour|direct>`"
        )
    print(f"Error: {brief_path}: {question}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
