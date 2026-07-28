"""Structural grep-window test guarding the docs-only dispatch mode added
to `requesting-code-review/SKILL.md` at the diff-scope step (Task 4 of
`docs/loom/plans/2026-07-28-docs-citation-check-and-review-mode.md`).

SKILL.md is a prompt/contract artifact, not executable code: nothing
importable observes whether a dispatched reviewer actually reads a
changed doc whole rather than diff-only. This file IS the instruction
the orchestrator reads before dispatching, so its correctness condition
is the PRESENCE of the load-bearing phrases that make the docs-only mode
executable by that reader -- same convention as
`test_plan_fact_grounding.py`.

Scope: the guard isolates the ADDED section (the "Docs-only dispatch
mode" sub-bullet under Process Step 1) rather than grepping the whole
file, so an incidental match elsewhere in SKILL.md (e.g. the word
"omission" in unrelated prose) cannot keep this test green after the
added section is deleted. Section text is whitespace-normalized before
matching -- the addition is written as one long logical line (the
hard-wrap lesson from `test_plan_fact_grounding.py`), but a future
editor could still re-wrap it, and the guard must survive that.

Polarity: `test_whole_artifact_polarity_guard` proves the whole-artifact
assertion is sensitive to the regression it exists to catch -- inverting
the instruction to "review only the diff" must fail the same check that
passes on the real text.

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SKILL_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "requesting-code-review"
    / "SKILL.md"
)


def _text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def _docs_mode_section(text: str) -> str:
    """Isolate the docs-only dispatch mode sub-bullet under Process Step 1.

    Runs from the line naming "Docs-only dispatch mode" to the next
    top-level Process step (a line starting with `<digit>. ` at column
    0), or end of file if none follows.
    """
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if "docs-only dispatch mode" in line.lower():
            start = i
            break
    assert start is not None, (
        "requesting-code-review/SKILL.md carries no 'Docs-only dispatch "
        "mode' text -- Task 4's amendment must be a findable section, "
        "not absent"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\d+\.\s", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _assert_whole_artifact(low: str) -> None:
    """Raise AssertionError unless `low` instructs whole-artifact reading
    (not diff-only) plus the unchanged-claim question."""
    assert "whole" in low, (
        "must instruct reviewers to read each changed artifact whole"
    )
    assert "diff only as context" in low or "diff as context" in low, (
        "must state the diff is context, not the review boundary"
    )
    assert (
        "does any unchanged claim in this file contradict the change, "
        "or the current code?" in low
    ), (
        "must ask the explicit unchanged-claim question verbatim -- this "
        "is the question that caught rounds 5-7 in the source audit "
        "(docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md "
        "§3.1)"
    )


def test_rcr_carries_docs_only_mode():
    """The docs-only dispatch mode names its trigger, the whole-artifact
    instruction, all five prose defect dimensions with inline
    definitions, and the citation-check invocation."""
    text = _text()
    low = _norm(_docs_mode_section(text)).lower()

    # trigger condition
    assert "git diff main...head --name-only" in low, (
        "must name the exact trigger command -- an orchestrator at any "
        "tier must be able to run this mechanically"
    )
    assert "non-empty" in low, (
        "must state the diff must be non-empty to trigger docs-only mode "
        "(empty diff is vacuously true for 'all files end in .md')"
    )
    assert re.search(r"ends in `?\.md`?", low), (
        "must state the trigger predicate: every changed file ends in "
        "`.md`"
    )
    assert "non-`.md`" in low or "non-.md" in low, (
        "must state the fallback: any non-.md file in the diff keeps "
        "the default code path"
    )

    # (a) whole-artifact scope
    _assert_whole_artifact(low)

    # (b) five prose dimensions, each named AND defined inline
    assert "omission" in low and "obligation or referent" in low, (
        "omission must be named and defined inline (an obligation or "
        "referent the text needs and lacks)"
    )
    assert "ambiguity" in low and "without support" in low, (
        "ambiguity must be named and defined inline (an absolute "
        "without support)"
    )
    for absolute in ("only", "never", "zero"):
        assert absolute in low, (
            f"ambiguity's inline definition must enumerate {absolute!r} "
            f"as an example unsupported absolute"
        )
    assert "inconsistency" in low and "changed-vs-unchanged" in low, (
        "inconsistency must be named and defined inline, including the "
        "changed-vs-unchanged case"
    )
    assert "incorrect-fact" in low and "does not support its claim" in low, (
        "incorrect-fact must be named and defined inline (a citation "
        "that does not support its claim)"
    )
    assert "missing population" in low and (
        "denominator" in low or "scope" in low
    ), (
        "missing population must be named and defined inline (a "
        "measured number without its denominator or scope)"
    )

    # (c) mechanical pre-pass
    assert "check_doc_citations.py" in low, (
        "must invoke the citation-check script by name"
    )
    assert "dispatch packet" in low, (
        "must state that the script's output rides the dispatch packet"
    )


def test_whole_artifact_polarity_guard():
    """Inverting the whole-artifact instruction to 'review only the
    diff' must fail the same check that passes on the real text --
    proves the guard is sensitive to the regression it exists to catch,
    not just to the section's absence."""
    text = _text()
    low = _norm(_docs_mode_section(text)).lower()

    # sanity: the real text passes.
    _assert_whole_artifact(low)

    key_phrase = "reads every changed artifact whole, the diff only as context"
    assert key_phrase in low, (
        "test fixture assumption broken -- SKILL.md wording changed "
        "under this test; update key_phrase to match"
    )
    mutated = low.replace(key_phrase, "reviews only the diff")

    with pytest.raises(AssertionError):
        _assert_whole_artifact(mutated)
