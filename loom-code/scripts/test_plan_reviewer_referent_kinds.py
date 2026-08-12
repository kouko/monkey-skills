"""Structural row-scoped test for Task 10 of
`docs/loom/plans/2026-08-13-brief-item-addressability.md`.

`plan-document-reviewer-prompt.md` is a prompt/contract artifact, not
executable code: nothing importable observes whether a reviewer applies
Check 3 or Check 9. This file IS the instruction that reviewer reads, so
its correctness condition is the PRESENCE of the load-bearing phrases —
same convention as `test_check16_prose_row.py` /
`test_plan_document_reviewer_check17.py`.

Every assertion slices the check's OWN table row (`| 3 | … |`, `| 9 | … |`)
rather than searching the whole document — the prompt is long, and a
whole-file grep would stay green if the added text migrated into a
neighbouring check's row, which is exactly the edit that silently
un-teaches the check that needed it. Row-slicing precedent:
`test_plan_obligation_sweep.py`'s `^\\|\\s*8\\s*\\|` slice.

Stdlib only (pathlib + re).
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PROMPT_MD = (
    REPO_ROOT
    / "loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md"
)


def _cells(check_number: int) -> tuple[str, str]:
    """Return (check_cell, failure_cell) of one numbered checks-table row.

    Splitting on `|` is safe: the checks table's cells carry no pipes.
    """
    text = PROMPT_MD.read_text(encoding="utf-8")
    match = re.search(rf"^\|\s*{check_number}\s*\|.*$", text, re.MULTILINE)
    assert match, (
        f"expected a Check {check_number} row (`| {check_number} | … |`) in "
        f"the checks table of {PROMPT_MD}"
    )
    parts = [c.strip() for c in match.group(0).strip().strip("|").split("|")]
    assert len(parts) == 3, (
        f"Check {check_number} row does not have exactly 3 cells "
        f"(number / check / failure); got {len(parts)}"
    )
    return parts[1], parts[2]


def test_checks_accept_the_bi_referent_and_the_none_value():
    """Check 3 must enumerate referent kind (c) — the `BI-<n>` identifier —
    alongside (a) and (b), and Check 9 must state that the no-requirement
    value `none — <reason>` satisfies it while a bare `none` or an empty
    reason still fails. Both point at `plan-format.md` as the SSOT for the
    grammar rather than restating it.
    """
    check3, _fail3 = _cells(3)

    # --- Check 3: kind (c) is enumerated in Check 3's OWN row --------------
    assert "(a)" in check3 and "(b)" in check3 and "(c)" in check3, (
        "Check 3 must enumerate all three referent kinds (a), (b) and (c) — "
        f"found: {check3!r}"
    )
    assert "BI-<n>" in check3, (
        "Check 3 must name the `BI-<n>` identifier as referent kind (c); a "
        "reviewer reading only this row would otherwise gap a task that "
        "cites one"
    )
    assert "plan-format.md" in check3, (
        "Check 3 must point at `plan-format.md` as the SSOT for the referent "
        "kinds instead of being the second place the grammar is defined"
    )

    check9, fail9 = _cells(9)

    # --- Check 9: the no-requirement value satisfies the check ------------
    assert "none — <reason>" in check9, (
        "Check 9 must name the no-requirement value `none — <reason>` as "
        "satisfying it — a task delivering no brief outcome is not an orphan"
    )
    assert "plan-format.md" in check9, (
        "Check 9 must point at `plan-format.md` as the SSOT for the value "
        "rather than restating its grammar"
    )
    assert "not an orphan" in check9, (
        "Check 9 must say in its own row that a task carrying the "
        "no-requirement value is NOT an orphan — the check's whole verdict "
        "for that task turns on this"
    )

    # --- the reason stays mandatory: the old gap class is not deleted -----
    assert "mandatory" in check9 and "non-empty reason" in check9, (
        "Check 9 must state that the reason is mandatory and non-empty — a "
        "reason-optional reading turns the value into a silent opt-out from "
        "brief traceability"
    )
    assert "bare `none`" in check9 and "whitespace-only" in check9, (
        "Check 9's own row must still reject a bare `none`, an empty reason "
        "and a whitespace-only reason"
    )
    assert "bare `none`" in fail9, (
        "Check 9's FAILURE cell must still fail a bare `none`; accepting any "
        "non-empty value would delete a real gap class"
    )
    assert "no brief traceability" in fail9, (
        "Check 9's failure cell must keep its original condition — a task "
        "whose field references nothing still fails"
    )
