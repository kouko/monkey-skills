"""Structural grep-window test guarding Check 20, added to
`plan-document-reviewer-prompt.md` by Task 4 of
`docs/loom/plans/2026-08-25-seam-contracts.md`.

plan-document-reviewer-prompt.md is a prompt/contract artifact, not
executable code: nothing importable observes whether a weak-tier
reviewer actually applies Check 20. This file IS the instruction that
reviewer reads, so its correctness condition is the PRESENCE of the
load-bearing phrases that make the check applicable by that reader --
same convention as `test_plan_document_reviewer_check19.py`.

The load-bearing claim this file exists to pin: Check 20 must require
that every task whose `Dependencies` is not "none" carries a `Seam`
field with one bullet per incoming edge, payload-bearing bullets
naming owner + probe, and must cite `plan-format.md` `#### Seam` by
POINTING at that heading -- never restating its grammar inline (the
heading is the SSOT; duplicating the grammar here is a second drift
surface).

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

from test_plan_document_reviewer_check17 import (
    _check_id_range_text,
    _needs_revision_range_text,
    _range_list_covers,
)

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


def _check20_row(text: str) -> str:
    """Isolate the Check 20 table row -- the line beginning `| 20 |`."""
    for line in text.splitlines():
        if line.strip().startswith("| 20 |"):
            return line
    raise AssertionError("Check 20 table row (`| 20 |`) not found")


def test_check20_row_present_and_ranges_updated():
    """Check 20 row exists, requires a `Seam` field with one bullet per
    incoming edge (payload-bearing bullets naming owner + probe),
    points at `plan-format.md`'s `#### Seam` heading instead of
    restating the grammar, and both `check_id` ranges in the output
    contract cover check id 20."""
    text = _text()
    row = _check20_row(text)

    assert "Dependencies" in row, (
        "Check 20 row must gate on tasks whose Dependencies is not 'none'"
    )
    assert re.search(r"\bSeam\b", row), (
        "Check 20 row must name the `Seam` field"
    )
    assert re.search(r"owner", row, re.IGNORECASE) and re.search(r"probe", row, re.IGNORECASE), (
        "Check 20 row must require payload-bearing bullets to name owner + probe"
    )
    assert "#### Seam" in row, (
        "Check 20 row must cite the `#### Seam` heading in plan-format.md"
    )
    assert "docs/" not in row, (
        "Check 20 row must not cite this repo's docs/ development records "
        "(cross-repo portability contract)"
    )

    # No grammar restatement: the two bullet forms from plan-format.md's
    # `#### Seam` section must not be reproduced verbatim in the row.
    assert "payload: none" not in row, (
        "Check 20 row must not restate the Seam bullet grammar -- point "
        "at the `#### Seam` heading instead"
    )
    assert "payload: <shape>" not in row, (
        "Check 20 row must not restate the Seam bullet grammar -- point "
        "at the `#### Seam` heading instead"
    )

    check_id_line = next(
        (line for line in text.splitlines() if "check_id:" in line),
        None,
    )
    assert check_id_line is not None, "gaps.check_id line not found"
    assert _range_list_covers(_check_id_range_text(check_id_line), 20), (
        "gaps.check_id range must cover check 20"
    )

    needs_revision_line = next(
        (
            line
            for line in text.splitlines()
            if line.strip().startswith("- **NEEDS_REVISION**")
        ),
        None,
    )
    assert needs_revision_line is not None, "NEEDS_REVISION verdict-mapping line not found"
    assert _range_list_covers(_needs_revision_range_text(needs_revision_line), 20), (
        "verdict mapping's NEEDS_REVISION range must cover check 20"
    )
