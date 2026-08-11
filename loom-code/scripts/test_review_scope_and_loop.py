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

DOCS_REVIEWER_AGENT = (
    Path(__file__).resolve().parent.parent / "agents" / "docs-reviewer.md"
)


def _rcr_text() -> str:
    return RCR_SKILL_MD.read_text(encoding="utf-8")


def _docs_reviewer_text() -> str:
    return DOCS_REVIEWER_AGENT.read_text(encoding="utf-8")


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


def test_docs_reviewer_scope_and_confirmation():
    """docs-reviewer.md (Task 7) must carry: (a) the scope contract --
    the SAME glob literal as rcr SKILL.md's SSOT heading (byte-equal;
    Task 13's cross-file lockstep assertion pins the two against each
    other later), plus the record-class N/A-loudly duty; (b) the NEW
    delta-confirmation duty -- after a gating NEEDS_REVISION verdict,
    a delta-scoped CONFIRMED_RESOLVED / STILL_BLOCKING verdict returned
    via SendMessage, never a fresh whole-corpus re-sample."""
    text = _docs_reviewer_text()

    # (a) scope contract: glob literal byte-equal to rcr's SSOT
    assert "<plugin>/skills/**/*.md" in text
    assert "<plugin>/agents/*.md" in text
    assert "<plugin>/hooks/*.md" in text
    assert "<plugin>/scripts/*.md" in text
    assert "README*" in text
    assert "CHANGELOG*" in text
    assert "record-class" in text and "docs/**" in text

    # rcr heading cited as SSOT, not re-derived
    assert "Classification: contract-class vs record-class" in text
    assert "SSOT" in text

    # record-class OUT of jurisdiction: N/A per file, loudly
    assert "N/A" in text
    assert "loudly" in text
    assert "contract-class remainder" in text

    # (b) NEW delta-confirmation duty
    assert "SendMessage" in text
    assert "CONFIRMED_RESOLVED" in text
    assert "STILL_BLOCKING" in text
    assert "whole-corpus re-sample" in text
