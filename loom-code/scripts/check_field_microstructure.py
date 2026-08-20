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

`check_goal` (Task 2) additionally flags a header `Goal:` line: any of
its raw continuation lines shaped as a nested bullet or a table row
(read separately from the `_header_value` fold, because the fold
discards the shape distinction that rule needs). Sentence counting is
not re-derived here either — BI-2 dropped "one sentence" from the
mechanical check before this task was dispatched, for the same reason
BI-1 abandoned it above.

`Goal:` carries NO length ceiling, unlike `Description`/`RED`/`GREEN`.
Dropped 2026-08-19 (see the field-value-microstructure plan's Decision
Log): plan-format.md:32-36 freezes `Goal:` "at plan time... never
edited afterward", so a length cap on a frozen field can only be
satisfied by an edit the freeze rule forbids — demonstrated concretely
when two of the five plans T14 reshaped needed genuinely restorative
edits (320 and 390 characters) that still exceeded 300. The
no-nested-body rule survives because it has its own, independent
justification (`plan_card.py` folding indented content into the
card's single line) and never required editing a frozen value.

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

# Exit code for a structurally empty input — see docs/loom/memory/
# a-mechanical-check-can-go-green-by-skipping.md: a check that can
# only find a match or find nothing looks identical to a check that
# never had anything to find. Zero '## Task' blocks (plan mode) or
# zero '## ' sections (--brief mode) means every check below iterates
# an empty sequence and returns [] — a clean exit 0 indistinguishable
# from "nothing violated". Reporting that as exit 2, distinct from
# both exit 0 (clean) and exit 1 (violation found), makes the
# distinction visible to the caller instead of silently agreeing.
_EXIT_STRUCTURALLY_EMPTY = 2

_NESTED_BULLET_LINE = re.compile(r"^\s+[-*+]\s")
_TABLE_LINE = re.compile(r"^\s*\|")

# --- brief-paragraph rule (Task 3) ----------------------------------

_HEADING_LINE = re.compile(r"^\s*#{1,6}\s")
_LIST_ITEM_LINE = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s)")
_TABLE_ROW_LINE = re.compile(r"^\s*\|")
_BLOCKQUOTE_LINE = re.compile(r"^\s*>")
_NARRATIVE_DECLARATION = re.compile(r"^\s*<!--\s*narrative:\s*(.*?)\s*-->\s*$")
_LINE_TERMINATOR = re.compile(r"\r\n|\r|\n")

_PARAGRAPH_MAX_CHARS = 600
_BRIEF_EXEMPT_SECTIONS = frozenset({"Current State Evidence", "Alternatives Considered"})


# A trailing parenthetical decoration — ASCII `(...)` or CJK `（...）`
# — plus any whitespace directly before it, anchored at the end of the
# string. Only a SUFFIX is stripped, never a prefix or infix: this is
# deliberately narrower than a fuzzy match so
# `## Alternatives Considered And Rejected Approaches` (a genuinely
# different section that merely starts with the same words) keeps its
# full text and stays un-exempt.
_TRAILING_PARENTHETICAL = re.compile(r"\s*[(（][^()（）]*[)）]\s*$")


def _normalize_heading(heading: str) -> str:
    """Casefolded, internal-whitespace-collapsed form of a heading's
    BASE text (its trailing parenthetical decoration, if any, is
    stripped first), so `_BRIEF_EXEMPT_SECTIONS` membership survives a
    case difference, a doubled space, or a decoration like `(Axis 4 —
    research-grounded)` without widening into a fuzzy or prefix match
    that would start exempting sections nobody meant to exempt."""
    folded = " ".join(heading.split()).casefold()
    while True:
        stripped = _TRAILING_PARENTHETICAL.sub("", folded)
        if stripped == folded:
            return folded
        folded = stripped


_BRIEF_EXEMPT_SECTIONS_NORMALIZED = frozenset(
    _normalize_heading(section) for section in _BRIEF_EXEMPT_SECTIONS
)


def _line_terminator_len(text: str, end_of_content: int) -> int:
    """Length, in characters, of the line terminator (if any) that
    starts at `text[end_of_content]` — 2 for `\\r\\n`, 1 for a bare
    `\\n` or `\\r`, 0 at end of text. Used instead of a hardcoded `+1`
    so the paragraph-block gap check (below) is newline-width agnostic:
    `iter_lines_outside_fences` walks `text.splitlines(keepends=True)`,
    so on CRLF input every physical line is one byte longer than a
    hardcoded LF assumption accounts for."""
    match = _LINE_TERMINATOR.match(text, end_of_content)
    return len(match.group(0)) if match else 0


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
        end_of_content = offset + len(content)
        prev_end = end_of_content + _line_terminator_len(text, end_of_content)
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
        if _normalize_heading(heading) in _BRIEF_EXEMPT_SECTIONS_NORMALIZED:
            continue
        blocks = _iter_paragraph_blocks(unit["source_text"])
        for index, block in enumerate(blocks):
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
            # A declaration line sits in the NEXT block, separated by a
            # blank line. Report that POSITION and nothing more: whether
            # that line was written for this paragraph is unknowable
            # here, and claiming it is would be classifying a block as
            # this paragraph's declaration — the one thing this rule
            # forbids a checker from doing. An author who did misplace
            # theirs learns the requirement; an author whose declaration
            # belongs elsewhere is not told to attach it here.
            next_block = blocks[index + 1] if index + 1 < len(blocks) else None
            if (
                next_block is not None
                and len(next_block) == 1
                and _NARRATIVE_DECLARATION.match(next_block[0][1])
            ):
                clause = (
                    "no narrative declaration (a declaration line does "
                    "follow this block, separated by a blank line; a "
                    "declaration counts only on the line immediately "
                    "below, with no blank line between)"
                )
            else:
                clause = "no narrative declaration"
            problems.append(
                f"'{heading}' section: paragraph is {len(folded)} "
                f"characters (max {_PARAGRAPH_MAX_CHARS}), {clause}: "
                f"{folded!r}"
            )
    return problems

# The one ceiling every prose unit in a plan is measured against: a
# field's first line, and each nested bullet's folded text. The header
# `Goal:` value is NOT measured against this cap (see check_goal's
# docstring) — plan-format.md:32-36 freezes `Goal:` at plan time and
# never edits it afterward, so a cap that can only be satisfied by
# editing the value is unenforceable against a frozen field; the
# no-nested-body rule has its own justification (plan_card folding)
# and does not depend on this constant.
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
        # `_NESTED_BULLET_LINE` recognises a bullet via `\s+` (tabs
        # included) and its indent unit is "count of matched whitespace
        # characters" (`len(match.group(0))`), NOT tab-expanded columns.
        # This measurement must agree with that unit — `lstrip(" ")`
        # (spaces only) would count a tab-indented continuation as 0.
        indent = len(raw) - len(raw.lstrip())
        if bullet_text_indent is not None and indent >= bullet_text_indent:
            bullet_text_parts.append(raw.strip())
            continue
        _flush_bullet()
        bullet_text_indent = None
        problems.append(
            f"Task {number} ({name}): '{field}' continuation line is "
            "none of the three permitted shapes (a nested bullet, a "
            "table row, or a wrapped continuation of the nested "
            "bullet immediately above it — indent it to at least "
            "that bullet's own text column to make it one): "
            f"{raw.strip()!r}"
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
    """Every header `Goal:` violation in `text`: a continuation line
    shaped as a nested bullet or a table row (the no-nested-body rule —
    `plan_card.py` folds any indented content into the card's single
    `end-state:` line, and `family-relay.md` pins that line as one line,
    verbatim). There is no length ceiling on `Goal:` — dropped per the
    2026-08-19 field-value-microstructure Decision Log: `Goal:` is
    "transcribed from the brief's Smallest End State at plan time —
    frozen with the plan... never edited afterward" (plan-format.md:32-
    36), so a cap enforceable only by editing the value is
    unenforceable against a frozen field, while the 300-character
    figure had no justification of its own beyond matching the
    Description/RED/GREEN cap. Empty when the plan has no `Goal:`
    header line, or when it is clean."""
    header, _, _ = text.partition("\n## ")
    value = _header_value(header, "Goal")
    if value is None:
        return []

    problems: list[str] = []
    for raw in _goal_raw_continuation_lines(header):
        if _NESTED_BULLET_LINE.match(raw) or _TABLE_LINE.match(raw):
            problems.append(
                f"Goal: has a nested bullet or table row in its body "
                f"(not allowed — plan_card folds it into the card's "
                f"single end-state: line): {raw.strip()!r}"
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check a writing-plans plan's Description/RED/GREEN "
                    "field values against the plan-field microstructure "
                    "grammar; exit 0 when clean, exit 1 on any violation, "
                    "exit 2 when the plan has no '## Task' headings at all."
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
        if not split_document(text):
            print(
                f"Error: {brief_path} has no '## ' sections — nothing "
                "for the paragraph-length check to scan. This is "
                "reported as an input error, not a clean pass.",
                file=sys.stderr,
            )
            return _EXIT_STRUCTURALLY_EMPTY
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
    if not _task_blocks(text):
        print(
            f"Error: {plan_path} has no '## Task' headings — nothing "
            "for the field-microstructure check to scan. This is "
            "reported as an input error, not a clean pass.",
            file=sys.stderr,
        )
        return _EXIT_STRUCTURALLY_EMPTY

    problems = check_plan_fields(text) + check_goal(text)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print(f"Field microstructure in {plan_path} is clean — no violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
