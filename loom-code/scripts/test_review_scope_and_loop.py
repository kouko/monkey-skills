"""Shared pin module for review-scope/loop-shape changes landed by the
2026-08-11 review-cost-reduction plan (docs/loom/plans/2026-08-11-review-
cost-reduction.md). Task 8 adds the first pin function; sibling tasks (7,
9, 10, 11, 12) each add one more pin function to this same module so a
partial cascade (one site updated, another forgotten) fails loudly instead
of passing silently -- plan §Notes "Classification glob SSOT chain".
"""
from pathlib import Path

RCR_SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "requesting-code-review"
    / "SKILL.md"
)


def _rcr_text() -> str:
    return RCR_SKILL_MD.read_text(encoding="utf-8")


def test_rcr_scope_classification():
    """requesting-code-review/SKILL.md must install the contract/record
    classification SSOT (Task 8): the glob rule verbatim, the record-class
    exemption-at-any-mix statement, and the record-only continuity
    mechanism's verb name -- so Task 7's agent copy and Task 14's Python
    encoding have a stable heading + literal to cite."""
    text = _rcr_text()

    # the glob rule, verbatim per the plan's authoring literal (Task 8
    # Description / Task 7 Description, same literal in both)
    assert "<plugin>/skills/**/*.md" in text
    assert "<plugin>/agents/*.md" in text
    assert "<plugin>/hooks/*.md" in text
    assert "<plugin>/scripts/*.md" in text
    assert "README*" in text
    assert "CHANGELOG*" in text
    assert "record-class" in text and "docs/**" in text

    # record-class exemption at any mix (docs arm receives contract-class
    # files ONLY)
    assert "exempt from review at any mix" in text

    # record-only continuity mechanism, named (Task 14's marker verb)
    assert "mint --review-na-record-only" in text
