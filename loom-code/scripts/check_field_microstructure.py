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

`check_goal` (Task 2) additionally flags a header `Goal:` line: its
`_header_value`-folded value over 300 characters, or any of its raw
continuation lines shaped as a nested bullet or a table row (checked
separately from the fold, because the fold discards the shape
distinction that rule needs). Sentence counting is not re-derived here
either — BI-2 dropped "one sentence" from the mechanical check before
this task was dispatched, for the same reason BI-1 abandoned it above.

`check_brief_paragraphs` (Task 3) additionally checks a brief document
(SSOT: `loom-code/skills/brainstorming/references/handoff-brief-format.md`
§Paragraph length), exposed by the `--brief <path>` CLI mode instead of
the plan mode above: a blank-line-delimited block of prose whose lines
are none of heading/list-item/table-row/blockquote, and that is not
inside a fenced code block, is a "paragraph"; one over 600 characters
violates unless it carries the declaration line `<!-- narrative:
<reason> -->` directly beneath it, with a non-blank reason. No
classification of "is this really narrative" happens anywhere here —
presence of the exact declaration string is the only thing checked,
per that file's explicit "no checker classifies a paragraph as
narrative" sentence. `## Current State Evidence` and `## Alternatives
Considered` are exempt sections. Fence tracking reuses
`adjudication_split.iter_lines_outside_fences` (via `split_document`
for section boundaries too) rather than a second fence tracker.

Stdlib only (`re`, `sys`, `pathlib`, `argparse`) plus the intra-repo
imports of `plan_card` and `adjudication_split` (resolved off this
file's own directory, same convention as `check_open_questions.py`
importing `adjudication_split`).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adjudication_split import iter_lines_outside_fences, split_document  # noqa: E402
from plan_card import _bullet_lines, _header_value, _task_blocks  # noqa: E402

_NESTED_BULLET_LINE = re.compile(r"^\s+[-*+]\s")
_TABLE_LINE = re.compile(r"^\s*\|")

# --- brief-paragraph rule (Task 3) ----------------------------------

_HEADING_LINE = re.compile(r"^\s*#{1,6}\s")
_LIST_ITEM_LINE = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s)")
_TABLE_ROW_LINE = re.compile(r"^\s*\|")
_BLOCKQUOTE_LINE = re.compile(r"^\s*>")
_NARRATIVE_DECLARATION = re.compile(r"^\s*<!--\s*narrative:\s*(.*?)\s*-->\s*$")

_PARAGRAPH_MAX_CHARS = 600
_BRIEF_EXEMPT_SECTIONS = frozenset({"Current State Evidence", "Alternatives Considered"})


def _iter_paragraph_blocks(text: str) -> list[list[tuple[int, str]]]:
    """Every blank-line-delimited block of `text`'s lines that lie
    outside a fenced code block, as a list of (offset, content) pairs
    per block. A fence silently closes whatever block preceded it —
    `iter_lines_outside_fences` never yields the fenced lines
    themselves, so without this gap check a paragraph directly above a
    fence would be merged with unrelated content directly below it
    (no blank line ever separated them in the filtered stream)."""
    blocks: list[list[tuple[int, str]]] = []
    block: list[tuple[int, str]] = []
    prev_end: int | None = None
    for offset, content in iter_lines_outside_fences(text):
        gap = prev_end is not None and offset != prev_end
        if not content.strip() or gap:
            if block:
                blocks.append(block)
            block = []
        if content.strip():
            block.append((offset, content))
        prev_end = offset + len(content) + 1
    if block:
        blocks.append(block)
    return blocks


def _is_paragraph(block: list[tuple[int, str]]) -> bool:
    """A block is a "paragraph" only when none of its lines is a
    heading, list item, table row, or blockquote — the grammar pinned
    in handoff-brief-format.md §Paragraph length."""
    return not any(
        _HEADING_LINE.match(content)
        or _LIST_ITEM_LINE.match(content)
        or _TABLE_ROW_LINE.match(content)
        or _BLOCKQUOTE_LINE.match(content)
        for _, content in block
    )


def check_brief_paragraphs(text: str) -> list[str]:
    """Every over-600-character prose paragraph in `text` that lacks a
    valid `<!-- narrative: <reason> --> ` declaration directly beneath
    it, one problem string per violation naming its `## ` section.
    `## Current State Evidence` and `## Alternatives Considered` are
    skipped entirely. Empty when the brief is clean.

    A paragraph never gets classified as narrative or not — presence
    of the declaration line (with a non-blank reason) is the only
    thing checked, matching handoff-brief-format.md's own "no checker
    classifies a paragraph as narrative" statement."""
    problems: list[str] = []
    for unit in split_document(text):
        heading = unit["heading"]
        if heading in _BRIEF_EXEMPT_SECTIONS:
            continue
        for block in _iter_paragraph_blocks(unit["source_text"]):
            if not _is_paragraph(block):
                continue
            prose_lines = block
            declaration_reason: str | None = None
            decl_match = _NARRATIVE_DECLARATION.match(block[-1][1])
            if decl_match:
                declaration_reason = decl_match.group(1)
                prose_lines = block[:-1]
            if not prose_lines:
                continue
            folded = " ".join(content.strip() for _, content in prose_lines)
            if len(folded) <= _PARAGRAPH_MAX_CHARS:
                continue
            if declaration_reason is not None and declaration_reason.strip():
                continue
            problems.append(
                f"'{heading}' section: paragraph is {len(folded)} "
                f"characters (max {_PARAGRAPH_MAX_CHARS}), no narrative "
                f"declaration: {folded!r}"
            )
    return problems

# The one ceiling every prose unit in a plan is measured against: a
# field's first line, each nested bullet's folded text, and the header's
# `Goal:` value. The schema states one number deliberately — see
# plan-format.md §Field-value grammar, "one number, not two independent
# limits that could drift apart". A second literal here would be that
# drift.
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
    nested bullets, and a table row also ends the wrap window of any
    earlier nested bullet, so a later deep-indented line does not
    inherit permission from a bullet a table row has already closed.
    The wrap window itself is bounded: a nested bullet's own text plus
    every line folded into it under shape 3 must together respect the
    same 300-character cap as a field's first line, so a short decoy
    bullet cannot buy an unlimited crammed-prose exemption."""
    problems = []
    bullet_text_indent: int | None = None
    bullet_text_parts: list[str] = []
    bullet_raw: str | None = None

    def _flush_bullet() -> None:
        if bullet_text_indent is None:
            return
        folded = " ".join(bullet_text_parts)
        if len(folded) > _FIRST_LINE_MAX_CHARS:
            problems.append(
                f"Task {number} ({name}): '{field}' nested bullet text "
                f"is {len(folded)} characters (max "
                f"{_FIRST_LINE_MAX_CHARS}): {bullet_raw!r}"
            )

    for raw in lines[1:]:
        if not raw.strip():
            continue
        match = _NESTED_BULLET_LINE.match(raw)
        if match:
            _flush_bullet()
            bullet_text_indent = len(match.group(0))
            bullet_raw = raw.strip()
            bullet_text_parts = [raw[match.end():].strip()]
            continue
        if _TABLE_LINE.match(raw):
            _flush_bullet()
            bullet_text_indent = None
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if bullet_text_indent is not None and indent >= bullet_text_indent:
            bullet_text_parts.append(raw.strip())
            continue
        _flush_bullet()
        bullet_text_indent = None
        problems.append(
            f"Task {number} ({name}): '{field}' continuation line is "
            f"neither a nested bullet nor a table row: {raw.strip()!r}"
        )
    _flush_bullet()
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


def _goal_raw_continuation_lines(header: str) -> list[str]:
    """The raw (unstripped) continuation lines of a header `Goal:` line —
    same walk as `plan_card._header_value`, but returning the lines
    themselves instead of the folded value, so their shape (nested
    bullet / table row / plain wrapped prose) can still be told apart."""
    lines = header.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith("Goal:"):
            continue
        collected = []
        for continuation in lines[i + 1 :]:
            if continuation[:1] in (" ", "\t") and continuation.strip():
                collected.append(continuation)
            else:
                break
        return collected
    return []


def check_goal(text: str) -> list[str]:
    """Every header `Goal:` violation in `text`: the folded value
    exceeding 300 characters, or a continuation line shaped as a nested
    bullet or a table row (the no-nested-body rule — `plan_card.py`
    folds any indented content into the card's single `goal:` line, and
    `family-relay.md` pins that line as one line, verbatim). The two
    grounds are separate violations with separate messages. Empty when
    the plan has no `Goal:` header line, or when it is clean."""
    header, _, _ = text.partition("\n## ")
    value = _header_value(header, "Goal")
    if value is None:
        return []

    problems: list[str] = []
    if len(value) > _FIRST_LINE_MAX_CHARS:
        problems.append(
            f"Goal: value is {len(value)} characters (max "
            f"{_FIRST_LINE_MAX_CHARS}): {value!r}"
        )
    for raw in _goal_raw_continuation_lines(header):
        if _NESTED_BULLET_LINE.match(raw) or _TABLE_LINE.match(raw):
            problems.append(
                f"Goal: has a nested bullet or table row in its body "
                f"(not allowed — plan_card folds it into the card's "
                f"single goal: line): {raw.strip()!r}"
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check a writing-plans plan's Description/RED/GREEN "
                    "field values against the plan-field microstructure "
                    "grammar; exit 1 on any violation."
    )
    parser.add_argument(
        "plan_path",
        nargs="?",
        help="path to the writing-plans plan file (plan mode)",
    )
    parser.add_argument(
        "--brief",
        metavar="PATH",
        help="path to a handoff brief file; runs the brief "
             "paragraph-length check instead of the plan checks",
    )
    args = parser.parse_args(argv)

    if args.brief:
        brief_path = Path(args.brief)
        if not brief_path.is_file():
            print(f"Error: brief file not found at {brief_path}.", file=sys.stderr)
            return 1
        text = brief_path.read_text(encoding="utf-8")
        problems = check_brief_paragraphs(text)
        for problem in problems:
            print(problem, file=sys.stderr)
        if problems:
            return 1
        print(f"Brief paragraph microstructure in {brief_path} is clean — no violations.")
        return 0

    if not args.plan_path:
        parser.error("plan_path is required unless --brief is given")

    plan_path = Path(args.plan_path)
    if not plan_path.is_file():
        print(f"Error: plan file not found at {plan_path}.", file=sys.stderr)
        return 1
    text = plan_path.read_text(encoding="utf-8")

    problems = check_plan_fields(text) + check_goal(text)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print(f"Field microstructure in {plan_path} is clean — no violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
