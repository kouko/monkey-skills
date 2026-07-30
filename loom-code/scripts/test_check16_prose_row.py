"""Structural grep-window test guarding the `Review-weight: prose` branch
added to Check 16 of `plan-document-reviewer-prompt.md` (Task 6 of
`docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md`).

plan-document-reviewer-prompt.md is a prompt/contract artifact, not
executable code: nothing importable observes whether a weak-tier reviewer
actually applies the prose eligibility test. This file IS the instruction
that reviewer reads, so its correctness condition is the PRESENCE of the
load-bearing phrases that make the branch applicable by that reader --
same convention as `test_review_weight_prose.py` (the SSOT this test's
wording is transcribed FROM, per
docs/loom/memory/prose-contract-mechanism-transcribes-from-code.md).

Scope: isolates the Check 16 table row and the Verdict-mapping N/A
clause separately, rather than grepping the whole file, so an incidental
match elsewhere cannot keep this test green after either addition is
deleted (docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md).

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

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


def _check16_row(text: str) -> str:
    """Isolate the Check 16 table row -- the line beginning `| 16 |`."""
    for line in text.splitlines():
        if line.strip().startswith("| 16 |"):
            return line
    raise AssertionError("Check 16 table row (`| 16 |`) not found")


def _na_clause(text: str) -> str:
    """Isolate the Verdict-mapping sentence stating when Check 16 is N/A --
    runs from 'Check 16 is N/A' to the next period."""
    match = re.search(r"Check 16 is N/A[^.]*\.", text)
    assert match is not None, (
        "Verdict mapping's 'Check 16 is N/A ...' sentence not found"
    )
    return match.group(0)


def test_check16_row_carries_prose_branch():
    """Check 16's row names `prose` alongside `mechanical`, with the
    all-`.md`-authored-prose eligibility test transcribed from SDD's
    shipped 'Prose review-weight substitution' wording, and a matching
    failure-column branch."""
    row = _norm(_check16_row(_text())).lower()

    # prose named alongside mechanical
    assert "`review-weight: mechanical`" in row, "must still name mechanical"
    assert "`review-weight: prose`" in row, (
        "must name the exact declaration syntax `Review-weight: prose`"
    )

    # eligibility test transcribed from SDD SSOT wording
    assert "files touched" in row, (
        "must reference the task's declared Files touched field"
    )
    assert "`.md`" in row, "must name the `.md` file-extension eligibility test"
    assert "authored prose" in row, (
        "must qualify eligibility as authored prose (matching SDD's "
        "'.md authored prose' phrase, not just any markdown file)"
    )
    assert re.search(r"\ball\b.{0,60}`\.md`|`\.md`.{0,60}\ball\b", row), (
        "must state ALL files touched must be .md, not merely some -- "
        "matches SDD's 'this substitution applies only when all files'"
    )
    assert "never code" in row or (
        "never" in row and "code" in row and "config" in row
    ), (
        "must carry SDD's 'never code, never config, never a "
        "generated/sync artifact' exclusion, not invent new vocabulary"
    )

    # failure-column branch for the prose case (row includes both Check
    # and Failure columns as one pipe-delimited line)
    assert "review-weight: prose" in row and (
        "not `.md`" in row or "is not" in row or "non-" in row
    ), (
        "failure column must cover the prose case: Files touched includes "
        "a file that is not .md authored prose"
    )


def _assert_na_clause_covers_both_weights(clause: str) -> None:
    """Raise AssertionError unless `clause` extends Check 16's N/A firing
    condition to both opt-in weights -- mechanical OR prose -- not just
    mechanical. Shared by the real-text test and the mutation guard below
    so both exercise the identical check (docs/loom/memory/
    prose-contract-mechanism-transcribes-from-code.md convention)."""
    assert "`review-weight: mechanical`" in clause, "must still name mechanical"
    assert "`review-weight: prose`" in clause, (
        "must extend the N/A clause to cover `Review-weight: prose` too"
    )
    assert " or " in clause, (
        "must join the two weights with 'or' -- N/A only when NEITHER "
        "is declared by any task"
    )


def test_na_clause_covers_both_weights():
    """The Verdict-mapping N/A clause fires when no task opts into EITHER
    weight -- mechanical OR prose -- not just mechanical."""
    clause = _norm(_na_clause(_text())).lower()
    _assert_na_clause_covers_both_weights(clause)


def test_na_clause_polarity_guard():
    """Reverting the N/A clause to its actual pre-fix, mechanical-only
    wording (a realistic regression, not a blank deletion) must fail
    `_assert_na_clause_covers_both_weights` -- proves the shared helper is
    sensitive to the regression it exists to catch. The prior version of
    this test deleted the exact substring its own assertion checked for,
    so it could never fail regardless of the real clause's semantics
    (vacuous by construction)."""
    clause = _norm(_na_clause(_text())).lower()

    # sanity: real text passes the real check
    _assert_na_clause_covers_both_weights(clause)

    key_phrase = (
        "check 16 is n/a when no task declares `review-weight: mechanical` "
        "or `review-weight: prose` (both opt-in)."
    )
    assert key_phrase in clause, (
        "test fixture assumption broken -- N/A clause wording changed "
        "under this test; update key_phrase to match"
    )

    # Contradicting variant: the actual pre-fix, mechanical-only wording --
    # not a blank deletion -- proves the check catches a REALISTIC
    # regression (the "or prose" carve-out silently dropped), not merely
    # the absence of a string it was told to delete.
    mutated = clause.replace(
        key_phrase,
        "check 16 is n/a when no task declares `review-weight: mechanical`.",
    )

    with pytest.raises(AssertionError):
        _assert_na_clause_covers_both_weights(mutated)
