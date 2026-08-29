"""Mechanical marker-grep tests for the SDD review-weight exemption.

Task 1 (this file) is the RED-first predecessor for Tasks 2-4. All three
tests below are expected to FAIL right now — the target files don't
carry the `Review-weight: mechanical` markers yet. Each test's docstring
names the exact substring(s) a later task must add, verbatim, to flip
it green.

Source: docs/loom/plans/2026-07-08-sdd-mechanical-review-weight-tasks.md
"""

from pathlib import Path

from heading_window import line_leading as _line_leading

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
      - the `Review-weight` reference section (pinned by its heading
        anchor) AND, inside that section, the eligibility bar the marker
        gates on -- the exemption's scope, not its prose.
    """
    text = _read(PLAN_FORMAT)
    assert "Review-weight: mechanical" in text
    heading = "#### `Review-weight` (v0.11.0+, optional)"
    assert heading in text
    # The section existing is not the invariant -- the BAR it states is.
    # `mechanical` skips two reviewer arms, so a section that kept the
    # heading but loosened (or lost) its eligibility test would silently
    # widen a review exemption. Pinned as the bar's rule-carrying tokens
    # inside the section window, not as a full sentence.
    # Anchor at a line start so a same-named heading at a different level
    # earlier in the file can't retarget this window.
    start = _line_leading(text, heading)
    assert start != -1, f"expected {heading!r} heading"
    end = text.index("\n#### ", start + len(heading))
    section = text[start:end]
    assert "ONLY be set" in section
    assert "reproducible from an exact spec" in section
    assert "never for logic, heuristic, hook, or security-surface" in section


def test_plan_document_reviewer_has_check_16():
    """
    loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md carries:
      - a "Check 16" row (Review-weight: mechanical)
      - the field name "Review-weight: mechanical" (referenced by the check)
      - the current applicable-checks denominator "<20>" — Check 5 (time-box,
        retired when writing-plans dropped the time criterion) and Check 15
        (advisory) are both excluded from the 22-check total, leaving 20
        checks that can actually fail. (Bumped from <18> to <19> when
        Check 21 (complexity assessment) shipped, and from <19> to <20>
        when Check 22 (Goal-line direction clause) shipped; the
        table-derived total is independently re-checked by
        test_plan_reviewer_output_contract_count.py, which does not
        hardcode this number.)
    """
    text = _read(PLAN_DOCUMENT_REVIEWER_PROMPT)
    assert "Check 16" in text
    assert "Review-weight: mechanical" in text
    assert "<20>" in text


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
