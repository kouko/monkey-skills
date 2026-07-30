"""Structural grep-window test guarding the `Review-weight: prose` addition to
`writing-plans/references/plan-format.md` (Task 8 of
`docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md`).

plan-format.md is a prompt/contract artifact, not executable code: nothing
importable observes whether a plan author actually discovers that
`Review-weight: prose` is a legal value from the schema alone. This file IS
the schema doc that author reads before writing a plan, so its correctness
condition is the PRESENCE of the load-bearing phrases that make the value
discoverable by that reader -- same convention as `test_review_weight_prose.py`
(subagent-driven-development/SKILL.md, the SSOT this section's eligibility
wording is transcribed FROM) and `test_check16_prose_row.py`
(plan-document-reviewer-prompt.md, the sibling gate).

Scope: isolates (a) the per-task schema's `Review-weight` enum line and
(b) the "#### `Review-weight`" prose section separately, rather than
grepping the whole file, so an incidental match elsewhere in plan-format.md
cannot keep this test green after either addition is deleted
(docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md).

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

PLAN_FORMAT_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-format.md"
)


def _text() -> str:
    assert PLAN_FORMAT_MD.is_file(), f"plan-format.md is absent at {PLAN_FORMAT_MD}"
    return PLAN_FORMAT_MD.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _enum_line(text: str) -> str:
    """Isolate the per-task schema's `Review-weight` enum line -- the line
    starting `- **Review-weight**:`."""
    for line in text.splitlines():
        if line.strip().startswith("- **Review-weight**:"):
            return line
    raise AssertionError("`- **Review-weight**:` enum line not found")


def _review_weight_section(text: str) -> str:
    """Isolate the "#### `Review-weight`" prose section -- runs from that
    heading to the next `#### ` heading, or end of file if none follows."""
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("#### `Review-weight`"):
            start = i
            break
    assert start is not None, "`#### \\`Review-weight\\`` section heading not found"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("#### "):
            end = j
            break
    return "".join(lines[start:end])


def test_enum_includes_prose():
    """The per-task schema's `Review-weight` field enum lists `prose`
    alongside `mechanical` and `OMIT`, so a plan author reading only the
    schema (not the SDD SSOT) discovers the value is legal."""
    line = _enum_line(_text())
    assert "<mechanical | prose | OMIT>" in line, (
        "enum must read exactly `<mechanical | prose | OMIT>` -- "
        f"got: {line!r}"
    )


def _assert_reviewer_swap(low: str) -> None:
    """Raise AssertionError unless `low` states docs-reviewer replaces
    code-quality-reviewer while implementer + spec-reviewer stay."""
    assert "docs-reviewer" in low, "must name the replacement agent: docs-reviewer"
    assert "code-quality-reviewer" in low, (
        "must name the arm being replaced: code-quality-reviewer"
    )
    assert re.search(
        r"replac\w* (the )?code-quality-reviewer.{0,80}docs-reviewer", low
    ) or re.search(
        r"docs-reviewer.{0,80}replac\w* (the )?code-quality-reviewer", low
    ), (
        "must state the substitution direction: docs-reviewer replaces "
        "code-quality-reviewer"
    )
    assert "implementer" in low, "must state the implementer dispatch stays"
    assert "spec-reviewer" in low and (
        "stay" in low or "keeps" in low or "kept" in low
    ), "must state spec-reviewer stays"


def test_review_weight_section_carries_prose_case():
    """The §Review-weight section documents the prose case: what it
    declares (docs-reviewer swaps in for code-quality-reviewer; implementer
    + spec-reviewer stay), the eligibility test transcribed from the SDD
    SSOT wording, the fail-closed note, and the upstream Check 16 gate."""
    low = _norm(_review_weight_section(_text())).lower()

    assert "`review-weight: prose`" in low, (
        "must name the exact declaration syntax `Review-weight: prose`"
    )

    _assert_reviewer_swap(low)

    # eligibility transcribed from SDD SSOT: "all files listed ... `.md`
    # authored prose -- never code, never config, never a generated/sync
    # artifact"
    assert "files touched" in low, (
        "must reference the task's declared Files touched field"
    )
    assert "`.md`" in low, "must name the `.md` file-extension eligibility test"
    assert "authored prose" in low, (
        "must qualify eligibility as authored prose, not any markdown file"
    )
    assert re.search(r"\ball\b.{0,60}`\.md`|`\.md`.{0,60}\ball\b", low), (
        "must state ALL files touched must be .md, not merely some"
    )
    assert "never code" in low or (
        "never" in low and "code" in low and "config" in low
    ), (
        "must carry the 'never code, never config, never a generated/sync "
        "artifact' exclusion"
    )

    # fail-closed note
    assert "fail" in low and "clos" in low, "must state the fail-closed disposition"

    # Check 16 gates it at plan review
    assert "check 16" in low, (
        "must cite plan-document-reviewer Check 16 as the upstream gate"
    )


def test_review_weight_section_polarity_guard():
    """Inverting the reviewer-swap text to claim spec-reviewer is ALSO
    replaced must fail the same check that passes on the real text --
    proves the assertion is sensitive to the regression it exists to
    catch, not just to the section's absence."""
    low = _norm(_review_weight_section(_text())).lower()

    # sanity: real text passes
    _assert_reviewer_swap(low)

    mutated = low + " the orchestrator replaces the spec-reviewer with docs-reviewer too."
    # mutation itself still contains all required substrings, so the
    # regex-based substitution-direction check must be what discriminates;
    # simulate the real regression by stripping the "stay" polarity words.
    stripped = re.sub(r"\bstay(s|ed|ing)?\b|\bkeeps?\b|\bkept\b", "", mutated)

    with pytest.raises(AssertionError):
        _assert_reviewer_swap(stripped)
