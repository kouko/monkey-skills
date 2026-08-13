"""Guards the anti-copy / SSOT-protection rider added to Check 7 of
`plan-document-reviewer-prompt.md` by Task 7 of
`docs/loom/plans/2026-08-13-open-question-dispatch-gate.md`.

Grounding (docs/loom/backlog/2026-07-06-anti-copy-acceptance-greps-pass-
paraphrase-copies.md): a plan's anti-copy GREEN criterion grepped for
verbatim charter-row text; the implementer shipped a complete five-row
PARAPHRASE of the charter's jurisdiction table that passed the
mechanical grep while violating its intent -- only the quality
reviewer's judgment leg caught it. A plan-document-reviewer applying
Check 7 literally, pre-fix, would have accepted a mechanical-only
anti-copy criterion as sufficiently "observable" and passed the plan.

Placement decision: this rider is attached to existing Check 7
(`Acceptance.GREEN` names an observable condition) rather than a new
numbered Check 19. Check 7 already evaluates GREEN-criterion quality;
an anti-copy criterion missing its judgment leg IS a vague/insufficient
GREEN criterion in the same sense Check 7 already polices, so this is
a rider on that check's existing jurisdiction, not a new check. The
task brief itself calls this a "check hint", which leans the same way.
Attaching here also means the Output contract's checks_passed
denominator / check_id range / NEEDS_REVISION mapping (all derived by
test_plan_reviewer_output_contract_count.py) need no change: Check 7
was already applicable and already counted.

plan-document-reviewer-prompt.md is a prompt/contract artifact, not
executable code: nothing importable observes whether a weak-tier
reviewer actually applies this rider. This file IS the instruction
that reviewer reads, so its correctness condition is the PRESENCE of
the load-bearing phrases that make the rider applicable by that
reader -- same convention as test_plan_document_reviewer_check18.py.

Scope: isolates the Check 7 table row's two cells (check-description,
failure-condition) separately, rather than grepping the whole file,
so an incidental match elsewhere cannot keep this test green after
either is deleted or reworded
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


def _text() -> str:
    assert PROMPT_MD.is_file(), f"plan-document-reviewer-prompt.md is absent at {PROMPT_MD}"
    return PROMPT_MD.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _check7_row(text: str) -> str:
    """Isolate the Check 7 table row -- the line beginning `| 7 |`."""
    for line in text.splitlines():
        if line.strip().startswith("| 7 |"):
            return line
    raise AssertionError("Check 7 table row (`| 7 |`) not found")


def _check7_cells(text: str) -> list[str]:
    """Split the Check 7 row into its pipe-delimited cells:
    `['', ' 7 ', <check description>, <failure condition>, '']`. Callers
    that must pin a phrase to a SPECIFIC one of the two prose columns
    slice to the relevant cell, per docs/loom/memory/
    substring-assertions-must-pin-the-phrase-their-message-names.md
    ("count() the token in the guarded scope; more than one occurrence
    means the assertion is pinning an unknown one of them")."""
    row = _check7_row(text)
    cells = row.split("|")
    assert len(cells) == 5, f"Check 7 row must have exactly 3 cells, got {row!r}"
    return cells


def _check7_check_cell(text: str) -> str:
    """The check-description cell (column 2, the requirement a reviewer
    applies) -- normalized and lowercased."""
    return _norm(_check7_cells(text)[2]).lower()


def _check7_failure_cell(text: str) -> str:
    """The failure-condition cell (column 3, what triggers NEEDS_REVISION)
    -- normalized and lowercased."""
    return _norm(_check7_cells(text)[3]).lower()


def test_anticopy_criterion_requires_reviewer_judgment_leg():
    """Named RED test (plan Task 7 Acceptance.RED): fails today because
    the prompt says nothing about anti-copy criteria -- zero occurrences
    of "paraphrase" / "anti-copy" / "reviewer-judgment leg" anywhere in
    the file. Once the rider ships on Check 7, pins:

    (1) the check-description cell names the two-leg requirement --
        BOTH a mechanical verbatim grep AND an explicit reviewer-
        judgment check, quoting the judgment check's own wording
        verbatim ("no paraphrase reproduction of the protected
        content") so a reviewer knows exactly what to write, not just
        that "judgment" is required in the abstract;
    (2) the failure-condition cell states a mechanical-only criterion
        (the judgment leg missing) is itself a gap -- so a reviewer
        who finds only the grep has an actual NEEDS_REVISION trigger,
        not just descriptive prose with no behavioral consequence.

    Each half is pinned in its OWN cell (not a whole-row grep) so a
    mutation that guts one half cannot hide behind the other half's
    surviving text."""
    text = _text()
    check_cell = _check7_check_cell(text)
    failure_cell = _check7_failure_cell(text)

    # (1) the check-description cell: both legs named, judgment leg quoted
    assert check_cell.count("anti-copy") >= 1 or check_cell.count("ssot-protection") >= 1, (
        "Check 7's check-description cell must name the anti-copy / "
        "SSOT-protection criterion kind this rider governs"
    )
    assert check_cell.count("mechanical verbatim grep") == 1, (
        "Check 7's check-description cell must name the mechanical "
        "verbatim-grep leg exactly once"
    )
    assert check_cell.count("explicit reviewer-judgment check") == 1, (
        "Check 7's check-description cell must name the explicit "
        "reviewer-judgment-check leg exactly once -- dropping this "
        "phrase while keeping the mechanical-grep phrase would still "
        "leave a mechanical-only requirement, the exact defect this "
        "rider exists to close"
    )
    assert check_cell.count("no paraphrase reproduction of the protected content") == 1, (
        "Check 7's check-description cell must quote the judgment "
        "check's own wording verbatim -- 'no paraphrase reproduction "
        "of the protected content' -- so a reviewer applying this "
        "literally knows what to write, not merely that a judgment "
        "leg exists"
    )
    assert "both" in check_cell and "and" in check_cell, (
        "Check 7's check-description cell must frame the two legs as "
        "jointly required (BOTH ... AND ...), not either-or"
    )

    # (2) the failure-condition cell: mechanical-only is itself a gap
    assert failure_cell.count("mechanical-only criterion is a gap") == 1, (
        "Check 7's failure-condition cell must state a mechanical-only "
        "anti-copy criterion is itself a gap -- without this the "
        "check-description cell's requirement has no NEEDS_REVISION "
        "trigger and is unenforceable prose"
    )
    assert "reviewer-judgment leg" in failure_cell, (
        "Check 7's failure-condition cell must name the missing "
        "reviewer-judgment leg as the specific defect, not a generic "
        "'is a gap' with no traceable cause"
    )
