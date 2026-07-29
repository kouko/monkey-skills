"""Structural grep-window test guarding the finding-class taxonomy added to
`requesting-code-review/SKILL.md`'s docs-only dispatch mode (Task 1 of
`docs/loom/plans/2026-07-30-docs-review-blocking-class.md`).

SKILL.md is a prompt/contract artifact: nothing importable observes
whether a dispatched reviewer actually tags a finding `class: instruction
| evidence`. This file IS the instruction the orchestrator and the
dispatched reviewers read, so its correctness condition is the PRESENCE
of the load-bearing phrases that make the class taxonomy executable by
that reader -- same convention as `test_docs_review_mode.py`.

Scope: two measured neighbourhood windows, per
`docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md` --
whole-file substring greps go false-green when the asserted phrase
pre-exists elsewhere (e.g. "evidence" already appears once in this file's
prose at the §Asking the user boundary note, well outside either window
below).

1. The "Docs-only dispatch mode" sub-bullet under Process Step 1 (same
   section `test_docs_review_mode.py` isolates) -- covers both class
   names, both worked examples, and the fail-closed sentence.
2. The `findings:` YAML key in §Verdict structure -- covers the new
   `class:` line and its docs-mode-only marker comment.

Both windows are proven RED against the pre-change file via
`git show HEAD:loom-code/skills/requesting-code-review/SKILL.md` before
the SKILL.md edit landed (see implementer report) -- a green suite alone
never demonstrates a grep test is load-bearing.

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
    0), or end of file if none follows. Mirrors
    `test_docs_review_mode.py::_docs_mode_section`.
    """
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if "docs-only dispatch mode" in line.lower():
            start = i
            break
    assert start is not None, (
        "requesting-code-review/SKILL.md carries no 'Docs-only dispatch "
        "mode' text -- this section must be findable, not absent"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\d+\.\s", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def _findings_block(text: str) -> str:
    """Isolate the `findings:` YAML key in §Verdict structure.

    Runs from the line `findings:` (column 0, inside the fenced verdict
    schema) to the next top-level YAML key at column 0 (e.g.
    `simplification_ledger:`), or end of file if none follows.
    """
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "findings:":
            start = i
            break
    assert start is not None, (
        "requesting-code-review/SKILL.md carries no top-level `findings:` "
        "key in §Verdict structure"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^[A-Za-z_][\w-]*:", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def test_docs_dispatch_defines_finding_classes():
    """The docs-only dispatch mode's clause (d) names both finding
    classes with inline definitions, one worked example per class drawn
    from the source audit, and the fail-closed default; the
    `findings:` block in §Verdict structure documents the same `class:`
    key as present for docs-mode dispatches only."""
    text = _text()

    # --- window 1: the docs-only dispatch mode sub-bullet ---
    dispatch_low = _norm(_docs_mode_section(text)).lower()

    assert "class: instruction | evidence" in dispatch_low, (
        "clause (d) must state the tag literally as `class: instruction "
        "| evidence`"
    )

    # instruction class: named, defined, and one worked example from
    # audit §2 (kpi_id derived from a canonical field slug vs. shipped
    # code doing the opposite).
    assert "instruction" in dispatch_low and (
        "text a reader or executor will act on" in dispatch_low
    ), (
        "instruction must be named and defined inline (text a reader or "
        "executor will act on)"
    )
    assert (
        "kpi_id" in dispatch_low and "canonical field slug" in dispatch_low
    ), (
        "instruction's worked example must be the audit §2 finding: a "
        "bullet instructing an implementer to derive `kpi_id` from a "
        "canonical field slug while the shipped code does the opposite"
    )
    assert "audit §2" in dispatch_low, (
        "instruction's worked example must cite its source, audit §2"
    )

    # evidence class: named, defined, and one worked example from audit
    # §4.3 (a claim attributed to a source section that does not state
    # it -- the audit attributed a variant to the brief's §Users, which
    # says "three comparative years" with no statement-type distinction).
    assert "evidence" in dispatch_low and (
        "narrative claim about what happened or is true" in dispatch_low
    ), (
        "evidence must be named and defined inline (a narrative claim "
        "about what happened or is true)"
    )
    assert "audit §4.3" in dispatch_low, (
        "evidence's worked example must cite its source, audit §4.3"
    )
    assert "attributed" in dispatch_low and (
        "§users" in dispatch_low or "attribution was wrong" in dispatch_low
    ), (
        "evidence's worked example must be a claim attributed to a "
        "source section that does not state it"
    )

    # fail-closed default.
    assert "is tagged `instruction`" in dispatch_low or (
        "tagged instruction" in dispatch_low
    ), (
        "a finding whose class is unclear must be tagged `instruction` "
        "(fail closed)"
    )
    assert "fail closed" in dispatch_low, (
        "the fail-closed rationale must be stated explicitly"
    )

    # --- window 2: the `findings:` block in §Verdict structure ---
    findings_low = _norm(_findings_block(text)).lower()

    assert "class: instruction | evidence" in findings_low, (
        "the `findings:` block must document `class: instruction | "
        "evidence` as a key, in the same shape as the existing `where:` "
        "key's inline comment"
    )
    assert "docs-mode" in findings_low and (
        "only" in findings_low
    ), (
        "the `class:` line's comment must mark it present for docs-mode "
        "dispatches only"
    )


def test_finding_class_window_excludes_unrelated_evidence_mention():
    """Sanity guard: window 1 and window 2 do not accidentally swallow
    the pre-existing, unrelated use of the word 'evidence' in this
    file's §Asking the user boundary note -- proves the windows are
    narrow, not whole-file greps in disguise."""
    text = _text()
    unrelated_anchor = "MUST stay machine-precise and keep every evidence citation"
    assert unrelated_anchor in text, (
        "test fixture assumption broken -- the unrelated 'evidence' "
        "mention this test checks for moved or was reworded"
    )
    assert unrelated_anchor not in _docs_mode_section(text)
    assert unrelated_anchor not in _findings_block(text)
