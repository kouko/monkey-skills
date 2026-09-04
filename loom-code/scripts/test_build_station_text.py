"""W1-04 -- build's dispatch-order paragraph widens from gate-only to every
full-lane `code` or `gate` task, small lane keeps implementer-first.

docs/loom/2026-09-04-checker-seams/plan.md W1-04, intent item 8 /
Acceptance #9: the paragraph in loom-code/skills/build/SKILL.md `## 2`
that opens with the adversary-first sentence must name both the `code`
and `gate` artifact types for the full lane, and must say the small lane
(the checker's `change_lane` recompute) keeps the implementer first with
the adversary attacking at the checkpoint instead.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILD_SKILL = REPO / "loom-code" / "skills" / "build" / "SKILL.md"


def _dispatch_order_paragraph() -> str:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    section = text.split("## 2. The dispatch prompt", 1)[1]
    # the paragraph runs up to the next blank-line-delimited block that
    # starts the "Dispatch `loom-code:implementer`" instruction.
    return section.split("Dispatch `loom-code:implementer`", 1)[0]


def test_full_lane_adversary_first_covers_code_and_gate() -> None:
    paragraph = _dispatch_order_paragraph()
    assert "adversary-first" in paragraph
    assert "`code`" in paragraph
    assert "`gate`" in paragraph


def test_small_lane_keeps_implementer_first() -> None:
    paragraph = _dispatch_order_paragraph()
    assert "small lane" in paragraph
    assert "change_lane" in paragraph
    assert "checkpoint" in paragraph


def test_paragraph_states_the_reason() -> None:
    paragraph = _dispatch_order_paragraph()
    # the measured false-pass rate that justifies independent adversarial
    # tests over the implementing agent's own tests.
    assert "one in five" in paragraph or "20%" in paragraph or "19.7%" in paragraph


def test_word_cap_within_soft_bound() -> None:
    text = BUILD_SKILL.read_text(encoding="utf-8")
    word_count = len(text.split())
    assert word_count <= 3750, f"word count {word_count} exceeds soft cap 3750"
