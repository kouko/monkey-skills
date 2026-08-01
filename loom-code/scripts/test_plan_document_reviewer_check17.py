"""Structural grep-window test guarding Check 17, added to
`plan-document-reviewer-prompt.md` by Task 3 of
`docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md`.

plan-document-reviewer-prompt.md is a prompt/contract artifact, not
executable code: nothing importable observes whether a weak-tier
reviewer actually applies Check 17. This file IS the instruction that
reviewer reads, so its correctness condition is the PRESENCE of the
load-bearing phrases that make the check applicable by that reader --
same convention as `test_check16_prose_row.py`.

The load-bearing claim this file exists to pin (source brief
§Smallest End State + §Measured): a reuse whose semantics do not carry
over to the new call path is a `gaps` entry, NEVER a `notes` entry,
even when the plan is internally consistent and every existing test
passes. A weak-tier reviewer that files this as a note and returns
PASS is exactly the failure the brief measured (haiku, Check 17 (c2)
cell, fabricated "disagreements are recorded with reason" and answered
"adequate" on the defect material).

Scope: isolates the Check 17 table row and the three output-contract
lines (checks_passed denominator, check_id range, verdict mapping)
separately, rather than grepping the whole file, so an incidental
match elsewhere cannot keep this test green after either is deleted
(docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md).

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

PROMPT_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-document-reviewer-prompt.md"
)

SDD_SKILL_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "subagent-driven-development"
    / "SKILL.md"
)

# The three marker tokens, transcribed VERBATIM from the plan's ## Notes PIN
# (docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md), the
# same source Task 1 already transcribed from into plan-format.md.
MARKER_READ = "read <repo-relative-path>:<line>"
MARKER_DOCSTRING = "inferred from docstring"
MARKER_UNVERIFIED = "unverified assumption — <what would settle it>"


def _text() -> str:
    assert PROMPT_MD.is_file(), f"plan-document-reviewer-prompt.md is absent at {PROMPT_MD}"
    return PROMPT_MD.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _check17_row(text: str) -> str:
    """Isolate the Check 17 table row -- the line beginning `| 17 |`."""
    for line in text.splitlines():
        if line.strip().startswith("| 17 |"):
            return line
    raise AssertionError("Check 17 table row (`| 17 |`) not found")


def test_check17_row_has_four_graded_parts_and_marker_vocabulary():
    """Check 17 names all four graded parts -- (a) presence, (b) marker,
    (c1) cross-read, (c2) adequacy -- and the (b) part carries the three
    marker tokens verbatim from the plan's ## Notes PIN."""
    row = _norm(_check17_row(_text()))

    for label in ("(a)", "(b)", "(c1)", "(c2)"):
        assert label in row, f"Check 17 row must name graded part {label}"

    assert "presence" in row.lower(), "(a) must be labeled presence"
    assert "marker" in row.lower(), "(b) must be labeled marker"
    assert "cross-read" in row.lower(), "(c1) must be labeled cross-read"
    assert "adequacy" in row.lower(), "(c2) must be labeled adequacy"

    for token in (MARKER_READ, MARKER_DOCSTRING, MARKER_UNVERIFIED):
        assert token in row, (
            f"Check 17 row must transcribe the marker token {token!r} "
            "verbatim from the plan's ## Notes PIN"
        )


def test_check17_adequacy_failure_is_a_gap_not_a_note():
    """(c2)'s consequence must state, without relying on inference, that a
    reuse whose semantics do not carry over is a `gaps` entry and NEVER a
    `notes` entry -- and that this holds even when the plan is internally
    consistent and every existing test passes. This is the load-bearing
    sentence the brief measured: a weak reviewer files exactly this kind
    of finding as a note and returns PASS when the consequence is left to
    inference."""
    row = _norm(_check17_row(_text()))
    lower = row.lower()

    assert "`gaps`" in row.lower() or "gaps" in lower, (
        "(c2) must name the `gaps` entry outcome"
    )
    assert re.search(r"never.{0,20}notes|notes.{0,20}never", lower), (
        "(c2) must state the gaps-vs-notes consequence as a direct "
        "never-notes rule, not merely mention both words separately"
    )
    assert "internally consistent" in lower, (
        "(c2) must state the consequence holds even when the plan is "
        "internally consistent"
    )
    assert (
        "every existing test passes" in lower
        or "existing test passes" in lower
    ), (
        "(c2) must state the consequence holds even when every existing "
        "test passes -- this exact combination is how the defect class ships"
    )


def test_check17_c2_carries_the_tier_floor_others_do_not():
    """(c2) states the tier floor and this row is its SSOT; (a), (b), (c1)
    carry no floor (source brief: '(c2) carries a tier floor; (a), (b) and
    (c1) do not.')."""
    row = _norm(_check17_row(_text()))
    lower = row.lower()

    assert "tier floor" in lower, "Check 17 must state the (c2) tier floor"
    assert "sonnet" in lower, "the tier floor must name the sonnet-or-above bar"
    assert "ssot" in lower, (
        "Check 17 must state it is the SSOT for the tier floor "
        "(SDD's SKILL.md points here rather than restating it)"
    )
    assert "carry no floor" in lower or "carries no floor" in lower or (
        "no floor" in lower
    ), "Check 17 must state (a), (b), (c1) carry no floor"


def _section(text: str, heading: str) -> str:
    """Return the body of the first Markdown section starting at `heading`
    (a line beginning with that exact heading text), up to the next `## `
    heading or end of file."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == heading), None)
    assert start is not None, f"heading {heading!r} not found"
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    return "\n".join(lines[start:end])


# Task 5 (docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md):
# a pointer, not a restatement -- so the (c2) tier floor value stays SSOT'd
# in the Check 17 row above and is never copied into SDD's SKILL.md.
_TIER_FLOOR_VALUE_PATTERN = re.compile(
    r"sonnet[^.\n]{0,60}tier floor|tier floor[^.\n]{0,60}sonnet",
    re.IGNORECASE,
)


def _model_selection_lines(skill_text: str) -> list[str]:
    return _section(skill_text, "## Model selection").splitlines()


def _pointer_line_index(lines: list[str]) -> int:
    """Isolate the single line carrying the Check-17 pointer sentence --
    the one line naming both `Check 17` and the reviewer-prompt filename
    together -- same isolation convention as `_check17_row` above. A
    mutant that scatters those tokens across separate, unrelated sentences
    has no line satisfying both conditions and fails here, rather than
    passing on section-wide membership."""
    for i, line in enumerate(lines):
        if "Check 17" in line and "plan-document-reviewer-prompt.md" in line:
            return i
    raise AssertionError(
        "no single line in Model selection names both Check 17 and "
        "plan-document-reviewer-prompt.md together -- a pointer scattered "
        "across separate sentences is not a coherent pointer"
    )


def _preceding_nonblank_line(lines: list[str], idx: int) -> str:
    """The last line of the paragraph immediately before `lines[idx]`,
    skipping the blank line(s) Markdown uses as a paragraph separator."""
    for i in range(idx - 1, -1, -1):
        if lines[i].strip():
            return lines[i]
    return ""


def test_sdd_skill_points_at_check17_without_restating_the_floor():
    """SDD's Model selection section must carry a pointer -- beside the
    existing most-capable-tier exception -- naming Check 17 (c2) and the
    plan-document-reviewer prompt as the SSOT for the (c2) tier floor,
    without restating the floor's value (sonnet-or-above) itself.

    The identifying tokens (Check 17, (c2), plan-document-reviewer-
    prompt.md) must co-occur on the pointer's own line -- not merely be
    present somewhere in the section -- and that line's paragraph must sit
    immediately after the paragraph carrying the existing most-capable-tier
    exception. A mutant that scatters the tokens into unrelated sentences
    (tokens present, no coherent pointer) passes a section-wide membership
    check but fails this line-level co-occurrence-plus-adjacency check."""
    assert SDD_SKILL_MD.is_file(), f"SDD SKILL.md is absent at {SDD_SKILL_MD}"
    skill_text = SDD_SKILL_MD.read_text(encoding="utf-8")

    lines = _model_selection_lines(skill_text)
    idx = _pointer_line_index(lines)
    pointer_line = lines[idx]

    assert "(c2)" in pointer_line, (
        "the pointer line must name graded part (c2) specifically -- (a)/(b)/(c1) "
        "carry no floor per Check 17's own row"
    )

    preceding_line = _preceding_nonblank_line(lines, idx)
    assert "most-capable tier" in preceding_line or "most capable tier" in preceding_line, (
        "the pointer's paragraph must sit immediately beside the existing "
        "most-capable-tier exception paragraph, not float elsewhere in the "
        "section"
    )

    # Post-condition: search, don't assume. The tier floor's actual value
    # (the phrase tying "sonnet" to "tier floor") must appear in exactly
    # one of the two files structurally relevant to this point-don't-copy
    # relation -- the Check 17 row is the SSOT, SDD's SKILL.md must not
    # restate it. Scoped to these two named files rather than
    # rglob("*.md") across all of loom-code/, per this module's own
    # isolation convention (see module docstring `Scope`) -- an unrelated
    # third doc mentioning the phrase is not this task's concern and would
    # otherwise fail this test with a message that points nowhere useful.
    #
    # This is a forward regression guard, not a RED-then-GREEN check this
    # task's own TDD cycle exercised: the baseline (worktree of the parent
    # commit 2c7e7f17, same pattern applied) is already 1 hit -- Task 3's
    # Check 17 row -- before Task 5 touches anything, and Task 5's own
    # edit (a pointer, not a restatement) leaves the count at 1. It still
    # does real work going forward: restating the tier value in SDD's
    # SKILL.md flips the count to 2 and this assertion fails.
    hits = [
        md
        for md in (SDD_SKILL_MD, PROMPT_MD)
        if _TIER_FLOOR_VALUE_PATTERN.search(md.read_text(encoding="utf-8"))
    ]
    assert hits == [PROMPT_MD], (
        "the (c2) tier floor value must appear in exactly one of the two "
        f"structurally relevant files (plan-document-reviewer-prompt.md); found in {hits}"
    )


def test_output_contract_names_check_17():
    """checks_passed denominator, the check_id range in the gaps block, and
    the verdict mapping's NEEDS_REVISION range must all account for the new
    Check 17 (it is a normal gating check, not retired/advisory)."""
    text = _text()

    denominator_line = next(
        (line for line in text.splitlines() if line.strip().startswith("checks_passed:")),
        None,
    )
    assert denominator_line is not None, "checks_passed line not found"
    assert "/<15>" in denominator_line, (
        "checks_passed denominator must be 15 (14 prior + Check 17; "
        "Checks 5 and 15 still never count)"
    )

    check_id_line = next(
        (line for line in text.splitlines() if "check_id:" in line),
        None,
    )
    assert check_id_line is not None, "gaps.check_id line not found"
    assert "16-17" in check_id_line or "16–17" in check_id_line, (
        "gaps.check_id range must extend to 17"
    )

    needs_revision_line = next(
        (line for line in text.splitlines() if "NEEDS_REVISION" in line and "applicable check" in line),
        None,
    )
    assert needs_revision_line is not None, "verdict mapping's NEEDS_REVISION sentence not found"
    assert "16–17" in needs_revision_line or "16-17" in needs_revision_line, (
        "verdict mapping's NEEDS_REVISION range must extend to 17"
    )
