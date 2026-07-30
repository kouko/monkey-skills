"""Structural grep-window test guarding the `Review-weight: prose` addition to
`subagent-driven-development/SKILL.md`, adjacent to the existing
`Review-weight: mechanical` block (Task 5 of
`docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md`).

SKILL.md is a prompt/contract artifact, not executable code: nothing
importable observes whether the orchestrator actually substitutes the
docs-reviewer agent for code-quality-reviewer on a declared task. This file
IS the instruction the orchestrator reads before dispatching, so its
correctness condition is the PRESENCE of the load-bearing phrases that make
the substitution executable by that reader -- same convention as
`test_docs_review_mode.py`.

Scope: the guard isolates the ADDED "Prose review-weight substitution"
paragraph rather than grepping the whole file, so an incidental match
elsewhere in SKILL.md cannot keep this test green after the addition is
deleted (docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md).

Polarity: `test_spec_reviewer_stays_polarity_guard` proves the "spec-reviewer
stays" assertion is sensitive to the regression it exists to catch --
flipping the text to say spec-reviewer is *also* replaced must fail the same
check that passes on the real text.

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SKILL_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "subagent-driven-development"
    / "SKILL.md"
)


def _text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def _prose_section(text: str) -> str:
    """Isolate the "Prose review-weight substitution" paragraph.

    Runs from the line naming "review-weight: prose" to the next bold
    paragraph heading (a line starting with `**` that opens a new
    house-style bold-lead-in paragraph, e.g. "**Progress ledger" or
    "**Decision Log"), or end of file if none follows.
    """
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if "review-weight: prose" in line.lower():
            start = i
            break
    assert start is not None, (
        "subagent-driven-development/SKILL.md carries no 'Review-weight: "
        "prose' text -- Task 5's amendment must be a findable section, "
        "not absent"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\*\*[A-Z]", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _assert_spec_reviewer_stays(low: str) -> None:
    """Raise AssertionError unless `low` states spec-reviewer STAYS and
    does NOT state spec-reviewer is replaced/substituted."""
    assert "spec-reviewer" in low, "must mention spec-reviewer at all"
    assert (
        "spec-reviewer" in low
        and ("stay" in low or "keeps" in low or "kept" in low)
    ), "must state the implementer + spec-reviewer dispatches stay"
    # Polarity: the text must never claim spec-reviewer itself is
    # replaced/substituted -- only code-quality-reviewer is.
    assert not re.search(
        r"replaces? the spec-reviewer|substitutes? the spec-reviewer|"
        r"spec-reviewer.{0,40}(is replaced|gets replaced)",
        low,
    ), "must NOT say spec-reviewer is replaced -- only code-quality-reviewer is"


def test_sdd_carries_review_weight_prose():
    """The prose review-weight paragraph names the declaration syntax, the
    reviewer substitution (code-quality-reviewer -> docs-reviewer,
    spec-reviewer stays), the all-`.md` authored-prose eligibility rule,
    the fail-closed sentence, and the upstream Check 16 gating note."""
    text = _text()
    low = _norm(_prose_section(text)).lower()

    # declaration syntax
    assert "`review-weight: prose`" in low, (
        "must name the exact declaration syntax `Review-weight: prose`"
    )

    # substitution: code-quality-reviewer -> docs-reviewer
    assert "code-quality-reviewer" in low, (
        "must name the arm being replaced: code-quality-reviewer"
    )
    assert "docs-reviewer" in low, (
        "must name the replacement agent: docs-reviewer"
    )
    assert re.search(
        r"replac\w* (the )?code-quality-reviewer.{0,80}docs-reviewer", low
    ) or re.search(
        r"docs-reviewer.{0,80}replac\w* (the )?code-quality-reviewer", low
    ), (
        "must state the substitution direction: docs-reviewer replaces "
        "code-quality-reviewer"
    )

    # spec-reviewer stays (+ polarity, see dedicated test below)
    _assert_spec_reviewer_stays(low)

    # implementer stays too
    assert "implementer" in low, (
        "must state the implementer dispatch stays"
    )

    # eligibility: all Files touched are .md authored prose
    assert "files touched" in low, (
        "must reference the task's declared Files touched field"
    )
    assert "`.md`" in low, "must name the `.md` file-extension eligibility test"
    assert "authored prose" in low, (
        "must qualify eligibility as authored prose (not generated/sync "
        "output, not code, not config)"
    )
    assert re.search(r"\ball\b.{0,60}`\.md`|`\.md`.{0,60}\ball\b", low), (
        "must state ALL files touched must be .md, not merely some"
    )

    # fail-closed sentence, mirroring mechanical's fail-closed rule
    assert "fail" in low and "clos" in low, (
        "must state the fail-closed disposition"
    )
    assert "full triad" in low, (
        "must name the fallback: the full triad (spec-reviewer + "
        "code-quality-reviewer)"
    )
    assert "mechanical" in low and (
        "mirror" in low or "mirroring" in low
    ), (
        "must state this mirrors the mechanical exemption's fail-closed "
        "rule"
    )

    # non-.md file anywhere (Files touched OR actual diff) trips fail-closed
    assert "diff" in low, (
        "must extend the fail-closed check to the actual diff, not just "
        "the declared Files touched list (a task could under-declare)"
    )

    # upstream gating note: plan-declared, validated by Check 16, not
    # re-validated here -- same trust model as mechanical
    assert "check 16" in low, (
        "must cite plan-document-reviewer Check 16 as the upstream gate"
    )
    assert "plan-document-reviewer" in low, (
        "must name plan-document-reviewer as the upstream validator"
    )
    assert "same trust model" in low or (
        "trust" in low and "mechanical" in low
    ), (
        "must state this shares mechanical's trust model: SDD does not "
        "re-validate the marker's eligibility, plan-document-reviewer "
        "already did"
    )


def test_prose_substitution_still_uses_verdict_resolution_table():
    """Unlike the mechanical exemption (which bypasses §Verdict
    resolution entirely -- see the earlier paragraph in this same file),
    the prose substitution still resolves through that table: the
    docs-reviewer's verdict substitutes into the table's
    code-quality-reviewer column, spec-reviewer's column unchanged (T5
    quality review, architecture finding)."""
    text = _text()
    low = _norm(_prose_section(text)).lower()
    assert "verdict resolution" in low, (
        "must reference the §Verdict resolution table"
    )
    assert "still applies" in low, (
        "must state the table still applies on this path -- unlike the "
        "mechanical exemption, which bypasses it entirely"
    )
    assert "code-quality-reviewer" in low and "column" in low, (
        "must state the docs-reviewer's verdict substitutes into the "
        "table's code-quality-reviewer column"
    )
    assert "mechanical" in low, (
        "must contrast this path with the mechanical exemption, which "
        "bypasses the table entirely"
    )


def test_spec_reviewer_stays_polarity_guard():
    """Inverting the "spec-reviewer stays" text to claim spec-reviewer is
    ALSO replaced must fail the same check that passes on the real
    text -- proves the polarity assertion is sensitive to the regression
    it exists to catch, not just to the section's absence."""
    text = _text()
    low = _norm(_prose_section(text)).lower()

    # sanity: the real text passes.
    _assert_spec_reviewer_stays(low)

    # Mutate: find the "stay"/"keeps"/"kept" verb near spec-reviewer and
    # replace the whole sentence's meaning with an explicit false claim.
    mutated = low + " the orchestrator replaces the spec-reviewer with docs-reviewer too."

    with pytest.raises(AssertionError):
        _assert_spec_reviewer_stays(mutated)
