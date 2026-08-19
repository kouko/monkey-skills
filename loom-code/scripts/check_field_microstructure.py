#!/usr/bin/env python3
"""Check a writing-plans plan's `Description` / `RED` / `GREEN` field
values against the plan-field microstructure grammar (SSOT:
`loom-code/skills/writing-plans/references/plan-format.md`).

Task 1 of docs/loom/plans/2026-08-19-field-value-microstructure.md.

Grammar:

- A field's first line (the text after the colon on the bullet's own
  line) violates when it exceeds 300 characters. The same cap applies
  to `Description`, `RED` and `GREEN` — one rule, no per-field branch.
  Two prior review rounds proved sentence-counting (occurrence-based,
  then boundary-heuristic) cannot be made correct here: occurrence
  counting false-positived on `0.89.0`, `e.g.`, `i.e.` and an
  ellipsis; the boundary heuristic that replaced it false-negatived on
  a lowercase-initial third sentence while still false-positiving on
  `e.g. Python`. A character cap has no punctuation edge case to
  enumerate.
- A field's continuation lines (everything after the first line, up to
  the next blank or column-0 line) violate when any indented non-blank
  line is none of three shapes: a nested bullet (`^\\s+[-*+]\\s`), a
  markdown table line (`^\\s*\\|`), or a wrapped continuation of the
  nested bullet above it — a line indented at least as deep as that
  bullet's own text start. Wrapping a long nested bullet across
  physical lines is ordinary markdown; rejecting it is a false
  positive on correct writing, so shape 3 is required, not optional.

Block extraction and bullet-value extraction are NOT reimplemented here
— both are imported from `plan_card.py` (`_task_blocks`, `_bullet_lines`)
so the two scripts never drift on what counts as a task block or a
bullet's raw lines.

This file does not implement the `Goal:` rule (a separate task) or the
brief-paragraph rule (a separate task, `--brief` mode) — plan-only, for
now.

Stdlib only (`re`, `sys`, `pathlib`, `argparse`) plus the intra-repo
import of `plan_card` (resolved off this file's own directory, same
convention as `check_open_questions.py` importing `adjudication_split`).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plan_card import _bullet_lines, _task_blocks  # noqa: E402

_NESTED_BULLET_LINE = re.compile(r"^\s+[-*+]\s")
_TABLE_LINE = re.compile(r"^\s*\|")

# A field's first line may not exceed this many characters.
_FIRST_LINE_MAX_CHARS = 300


def _check_continuations(
    lines: list[str], number: int, name: str, field: str
) -> list[str]:
    """Every indented non-blank line in `lines[1:]` (a field's
    continuation lines) that is none of three legal shapes is a
    violation: a nested bullet, a markdown table row, or a wrapped
    continuation of the nested bullet immediately above it — a line
    indented at least as deep as that bullet's own text start. A line
    indented under a table row (with no governing nested bullet) is
    NOT covered by the wrap exemption; the grammar ties it only to
    nested bullets."""
    problems = []
    bullet_text_indent: int | None = None
    for raw in lines[1:]:
        if not raw.strip():
            continue
        match = _NESTED_BULLET_LINE.match(raw)
        if match:
            bullet_text_indent = len(match.group(0))
            continue
        if _TABLE_LINE.match(raw):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if bullet_text_indent is not None and indent >= bullet_text_indent:
            continue
        problems.append(
            f"Task {number} ({name}): '{field}' continuation line is "
            f"neither a nested bullet nor a table row: {raw.strip()!r}"
        )
    return problems


def _check_first_line(
    lines: list[str], number: int, name: str, field: str
) -> list[str]:
    first = lines[0]
    length = len(first)
    if length <= _FIRST_LINE_MAX_CHARS:
        return []
    return [
        f"Task {number} ({name}): '{field}' first line is {length} "
        f"characters (max {_FIRST_LINE_MAX_CHARS}): {first!r}"
    ]


def _dedent_lines(lines: list[str]) -> list[str]:
    """`lines` with the smallest common leading-space run stripped, so a
    sub-block's bullets (e.g. `Acceptance`'s `RED`/`GREEN` sub-bullets,
    indented under it) can be re-scanned with `_bullet_lines`, which
    only matches a bullet anchored at column 0."""
    indents = [len(line) - len(line.lstrip(" ")) for line in lines if line.strip()]
    if not indents:
        return lines
    n = min(indents)
    return [line[n:] if len(line) >= n else line for line in lines]


def _check_acceptance(block: str, number: int, name: str) -> list[str]:
    acceptance_lines = _bullet_lines(block, "Acceptance")
    if acceptance_lines is None:
        return []
    sub_text = "\n".join(_dedent_lines(acceptance_lines[1:]))

    problems: list[str] = []
    for field in ("RED", "GREEN"):
        sub_lines = _bullet_lines(sub_text, field)
        if sub_lines is None:
            continue
        problems.extend(_check_first_line(sub_lines, number, name, field))
        problems.extend(_check_continuations(sub_lines, number, name, field))
    return problems


def check_plan_fields(text: str) -> list[str]:
    """Every `Description` / `RED` / `GREEN` field-microstructure
    violation across all `## Task <N> —` blocks in `text`, in file
    order. Empty when the plan is clean."""
    problems: list[str] = []
    for number, name, block in _task_blocks(text):
        description_lines = _bullet_lines(block, "Description")
        if description_lines is not None:
            problems.extend(
                _check_first_line(description_lines, number, name, "Description")
            )
            problems.extend(
                _check_continuations(description_lines, number, name, "Description")
            )
        problems.extend(_check_acceptance(block, number, name))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check a writing-plans plan's Description/RED/GREEN "
                    "field values against the plan-field microstructure "
                    "grammar; exit 1 on any violation."
    )
    parser.add_argument("plan_path", help="path to the writing-plans plan file")
    args = parser.parse_args(argv)

    plan_path = Path(args.plan_path)
    if not plan_path.is_file():
        print(f"Error: plan file not found at {plan_path}.", file=sys.stderr)
        return 1
    text = plan_path.read_text(encoding="utf-8")

    problems = check_plan_fields(text)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print(f"Field microstructure in {plan_path} is clean — no violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
