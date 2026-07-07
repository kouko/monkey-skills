"""Mechanical marker-grep tests for the SDD review-weight exemption.

Task 1 (this file) is the RED-first predecessor for Tasks 2-4. All three
tests below are expected to FAIL right now — the target files don't
carry the `Review-weight: mechanical` markers yet. Each test's docstring
names the exact substring(s) a later task must add, verbatim, to flip
it green.

Source: docs/loom/plans/2026-07-08-sdd-mechanical-review-weight-tasks.md
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PLAN_FORMAT = REPO_ROOT / "loom-code/skills/writing-plans/references/plan-format.md"
PLAN_DOCUMENT_REVIEWER_PROMPT = REPO_ROOT / "loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md"
SDD_SKILL = REPO_ROOT / "loom-code/skills/subagent-driven-development/SKILL.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_format_has_review_weight_field():
    """
    Task 2 adds to loom-code/skills/writing-plans/references/plan-format.md:
      - the literal field name "Review-weight: mechanical"
      - the co-condition phrase "identical or near-identical edit"
    """
    text = _read(PLAN_FORMAT)
    assert "Review-weight: mechanical" in text
    assert "identical or near-identical edit" in text


def test_plan_document_reviewer_has_check_16():
    """
    loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md carries:
      - a "Check 16" row (Review-weight: mechanical)
      - the field name "Review-weight: mechanical" (referenced by the check)
      - the current applicable-checks denominator "<14>" — Check 5 (time-box,
        retired when writing-plans dropped the time criterion) and Check 15
        (advisory) are both excluded from the 16-check total, leaving 14
        checks that can actually fail.
    """
    text = _read(PLAN_DOCUMENT_REVIEWER_PROMPT)
    assert "Check 16" in text
    assert "Review-weight: mechanical" in text
    assert "<14>" in text


def test_sdd_skill_has_mechanical_skip_branch():
    """
    Task 4 adds to loom-code/skills/subagent-driven-development/SKILL.md:
      - the literal field name "Review-weight: mechanical"
      - "skip" (the reviewer-dispatch skip behavior)
      - "self-check" (the deterministic self-check procedure)
    Case-sensitive, matching production's consistent capitalization
    (same convention as the other two marker tests in this file).
    """
    text = _read(SDD_SKILL)
    assert "Review-weight: mechanical" in text
    assert "skip" in text
    assert "self-check" in text
