#!/usr/bin/env python3
"""Parse a handoff brief's `## Design-side on-ramp` line and exit
non-zero while the on-ramp fired but was resolved by anything other
than an explicit user (or standing) choice.

Grammar (SSOT: `loom-code/skills/brainstorming/references/
handoff-brief-format.md` `### `## Design-side on-ramp``) — exactly one
of these four canonical forms is well-formed:

    not fired — <reason>
    fired: rows <n,...> — user chose <detour|direct>
    fired: rows <n,...> — standing <detour|direct> (KICKOFF-DEFAULTS.md)
    pending

Any other wording — including lookalikes such as `offered — direct per
repo precedent` or a missing line entirely — is *unresolved*: lookalike
wording never resolves the gate (see
`docs/loom/memory/section-gate-must-flag-entry-lookalikes-not-just-
matches.md`). The `standing` form additionally requires every cited row
to be named in the caller's `standing` mapping — the CLI loads this
mapping from `<repo-root>/docs/loom/KICKOFF-DEFAULTS.md`'s `## On-ramp
standing choices` section via `load_standing()`.

The on-ramp line may appear either as a `## Design-side on-ramp`
heading followed by its value on the next non-blank line, or inline —
`Design-side on-ramp: <value>`, optionally bulleted, bolded, and/or
blockquoted (`> **Design-side on-ramp**: <value>`). Both forms are
accepted for LOCATING the line; the VALUE grammar above is strict
regardless of which form located it.

Exit codes:

    0 — `resolved` or `not_fired`.
    1 — the brief file does not exist, or the brief or `docs/loom/KICKOFF-DEFAULTS.md` exists but is unreadable.
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

# A blockquote continuation line that starts a NEW labelled field (a
# bolded `**Label**:` field, or a heading) rather than continuing the
# on-ramp value's own soft-wrap — joining must stop there.
_BLOCKQUOTE_FIELD_START = re.compile(r"^(?:#{1,6}\s|\*\*[^*\n]+\*\*\s*:)")


def _join_blockquote_continuation(lines: list[str], start_idx: int, value: str) -> str:
    """Join subsequent `>`-prefixed lines onto `value` while they are
    plain continuation text — CommonMark lets a blockquote's own
    paragraph soft-wrap across physical lines, and the corpus does
    this for on-ramp values (see docs/loom/specs/2026-08-18-onramp-
    explicit-choice-gate.md's own `not fired — ...` line)."""
    parts = [value]
    for nxt in lines[start_idx + 1:]:
        stripped = nxt.lstrip()
        if not stripped.startswith(">"):
            break
        content = stripped[1:].strip()
        if not content or _BLOCKQUOTE_FIELD_START.match(content):
            break
        parts.append(content)
    return " ".join(parts)


def _find_onramp_value_line(brief_text: str) -> str | None:
    """The on-ramp line's value (stripped), from whichever corpus form
    is found first in document order, or None if neither form is
    present. A blockquote-form value's soft-wrapped continuation lines
    (subsequent `>` lines) are joined in before the grammar is applied,
    so a multi-line value is not silently truncated."""
    lines = brief_text.splitlines()
    for i, raw in enumerate(lines):
        inline = _INLINE_LINE.match(raw)
        if inline is not None:
            value = inline.group("value").strip()
            if raw.lstrip().startswith(">"):
                value = _join_blockquote_continuation(lines, i, value)
            return value.strip()
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
    r"\(KICKOFF-DEFAULTS\.md\)\s*$"
)
_FIRED_ROWS_PREFIX = re.compile(rf"^fired:\s*rows\s*{_ROWS}\b")

# --- KICKOFF-DEFAULTS.md standing-choices section ------------------------

# Exact-line heading match: the section is machine-parsed, so its
# heading is a fixed string, not a pattern.
STANDING_CHOICES_HEADING = "## On-ramp standing choices"

# Entry grammar SSOT: loom-code/hooks/family-reception.md
# `### On-ramp standing choices`.
_STANDING_ENTRY = re.compile(
    r"^-\s*row\s+(?P<row>\d+)\s*\([^)]*\):\s*standing\s+"
    r"(?P<choice>direct|detour)\s*—\s*.+\(\d{4}-\d{2}-\d{2}\)\s*$"
)


def load_standing(repo_root: Path) -> dict[int, str]:
    """Parse `<repo_root>/docs/loom/KICKOFF-DEFAULTS.md`'s `## On-ramp
    standing choices` section into `{row: "direct"|"detour"}`. A missing
    file or a missing section is not an error — it just means no row has
    a standing choice recorded yet, which the `standing` form's row check
    already treats as unresolved."""
    kickoff_defaults_path = repo_root / "docs" / "loom" / "KICKOFF-DEFAULTS.md"
    if not kickoff_defaults_path.is_file():
        return {}
    lines = kickoff_defaults_path.read_text(encoding="utf-8").splitlines()

    heading_idx = None
    for i, line in enumerate(lines):
        if line.strip() == STANDING_CHOICES_HEADING:
            heading_idx = i
            break
    if heading_idx is None:
        return {}

    standing: dict[int, str] = {}
    for line in lines[heading_idx + 1:]:
        if line.lstrip().startswith("## "):
            break
        match = _STANDING_ENTRY.match(line.strip())
        if match is not None:
            standing[int(match.group("row"))] = match.group("choice")
    return standing


def _parse_rows(rows_text: str) -> list[int]:
    return [int(part.strip()) for part in rows_text.split(",")]


@dataclass
class Result:
    status: str  # "resolved" | "unresolved" | "not_fired"
    rows: list[int] = field(default_factory=list)
    message: str = ""
    missing_rows: list[int] = field(default_factory=list)


def resolve(brief_text: str, standing: dict[int, str]) -> Result:
    """Resolve a brief's on-ramp line against the canonical grammar.

    `standing` maps row number -> chosen value, per KICKOFF-DEFAULTS.md's
    `## On-ramp standing choices` section — the CLI loads this via
    `load_standing()`; the `fired: rows <n> — standing <detour|direct>
    (KICKOFF-DEFAULTS.md)` form is resolved only when every cited row is
    present in this mapping. For an unresolved `standing` form,
    `missing_rows` names exactly the cited rows absent from `standing`
    (empty for every other form)."""
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
        missing = [row for row in rows if row not in standing]
        if not missing:
            return Result("resolved", rows, value)
        return Result("unresolved", rows, value, missing_rows=missing)

    # `pending`, a malformed `fired:` line, or any other wording — all
    # unresolved. If it at least names rows (a `fired: rows <n> ...`
    # attempt that just isn't the well-formed user/standing form), keep
    # them for a more specific CLI message; otherwise rows stay empty.
    rows_prefix = _FIRED_ROWS_PREFIX.match(value)
    rows = _parse_rows(rows_prefix.group("rows")) if rows_prefix else []
    return Result("unresolved", rows, value)


def build_question(result: Result) -> str:
    """The exact user-facing question for an `unresolved` `Result` —
    shared by `main()`'s stderr message so the missing-standing-row
    wording lives in one importable place (git-guard.py's
    `_gate_commit_plans` reuses it)."""
    if result.missing_rows:
        rows_str = ",".join(str(row) for row in result.rows)
        missing_str = ",".join(str(row) for row in result.missing_rows)
        return (
            f"Design-side on-ramp: rows {missing_str} cite a standing "
            f"choice, but KICKOFF-DEFAULTS.md's '{STANDING_CHOICES_HEADING}' "
            f"has no entry for row {missing_str}. Add one there, or "
            "record the answer as `fired: rows "
            f"{rows_str} — user chose <detour|direct>`"
        )
    if result.rows:
        rows_str = ",".join(str(row) for row in result.rows)
        return (
            f"Design-side on-ramp: rows {rows_str} fired — detour into "
            "loom-design first, or go direct? Record the answer as "
            f"`fired: rows {rows_str} — user chose <detour|direct>`"
        )
    return (
        "Design-side on-ramp fired — detour into loom-design first, "
        "or go direct? Record the answer as `fired: rows <n> — user "
        "chose <detour|direct>`"
    )


# --- CLI -------------------------------------------------------------


def _resolve_repo_root(explicit: str | None, brief_dir: Path) -> Path:
    # Called by main() to locate KICKOFF-DEFAULTS.md for `load_standing()`.
    if explicit is not None:
        return Path(explicit)
    try:
        # grounding: in-repo precedent loom_init.py:108 (same flag) +
        # `git rev-parse --help`
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
        help="repo root used to locate docs/loom/KICKOFF-DEFAULTS.md for "
             "standing-choice resolution (default: `git rev-parse "
             "--show-toplevel` of the brief's directory, falling back "
             "to cwd)",
    )
    args = parser.parse_args(argv)

    brief_path = Path(args.brief_path)
    try:
        brief_present = brief_path.is_file()
    except OSError as exc:
        print(
            f"Error: brief at {brief_path} is unreadable ({exc}).", file=sys.stderr
        )
        return 1
    if not brief_present:
        print(f"Error: brief file not found at {brief_path}.", file=sys.stderr)
        return 1
    # Both reads are guarded for the same reason its two siblings are
    # (`check_queue_relation.py`, `check_north_star_link.py`): a gate owes
    # its operator one actionable line, never a raw traceback. This script
    # was the third sibling of that family and stayed bare through two
    # rounds that fixed the other two; the contract is now pinned
    # mechanically by test_gate_scripts_fail_loud_on_unreadable_input.py.
    try:
        brief_text = brief_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error: brief at {brief_path} is unreadable ({exc}).", file=sys.stderr)
        return 1

    repo_root = _resolve_repo_root(args.repo_root, brief_path.parent)
    try:
        standing = load_standing(repo_root)
    except OSError as exc:
        print(
            f"Error: {repo_root / 'docs' / 'loom' / 'KICKOFF-DEFAULTS.md'} "
            f"is unreadable ({exc}).",
            file=sys.stderr,
        )
        return 1

    result = resolve(brief_text, standing)

    if result.status in ("resolved", "not_fired"):
        print(
            f"Design-side on-ramp in {brief_path} is resolved "
            f"({result.status})."
        )
        return 0

    question = build_question(result)
    print(f"Error: {brief_path}: {question}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
