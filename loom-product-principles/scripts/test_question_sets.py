"""Structural grep-test guarding references/question-sets.md — the graduated
question-set content the product-principles construction flow's SKILL.md
(a later task) will reference instead of inlining question text.

Content SSOT is `docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/
instrument-v0.1.md` (frozen, not touched by this task): facts/question texts
verbatim, structure adapted to a reference file. Checks assert on
load-bearing PHRASES (intent), tolerant of wording variation, per the
existing test style in test_product_principles_skill.py.

Stdlib only (pathlib + re). Resolve the reference file relative to this
test file.
"""

import re
from pathlib import Path

QUESTION_SETS = (
    Path(__file__).parents[1]
    / "skills"
    / "product-principles"
    / "references"
    / "question-sets.md"
)


def _text() -> str:
    assert QUESTION_SETS.is_file(), f"question-sets.md is absent at {QUESTION_SETS}"
    return QUESTION_SETS.read_text(encoding="utf-8")


# --- Product question set (Q1-Q8) -------------------------------------------

def test_product_question_set_has_eight_numbered_questions():
    text = _text()
    for n in range(1, 9):
        assert re.search(rf"(?m)^\s*{n}\.\s", text), \
            f"Product question set must carry numbered question {n}"


def test_q4_carries_replaces_x_capability_annotation():
    """FINDING-02: if the answer is phrased as 'replaces X', enumerate X's
    capability set and force an explicit in/out classification per
    capability — a replacement target smuggles in scope."""
    text = _text()
    assert "replaces X" in text, \
        "Q4 must carry the literal 'replaces X' annotation phrasing"
    low = text.lower()
    assert "capability" in low, \
        "Q4 annotation must mention capability enumeration"
    assert "in/out" in low or ("in " in low and "out" in low and "classif" in low), \
        "Q4 annotation must force an explicit in/out classification per capability"


def test_q8_covers_lifecycle_and_scale():
    """FINDING-01: how long does the content/core object live, how large does
    the collection grow, and a declared scale ceiling is a legitimate
    falsifiable answer."""
    text = _text()
    low = text.lower()
    assert "lifecycle" in low, "Q8 must name lifecycle"
    assert "scale" in low, "Q8 must name scale"
    assert "grow" in low, "Q8 must ask how large the collection grows"
    assert "scale ceiling" in low, \
        "Q8 must name the declared scale ceiling as a legitimate falsifiable answer"


# --- Design section — expert lane --------------------------------------------

def test_design_section_is_expert_lane_no_fixed_question_set():
    text = _text()
    low = text.lower()
    assert "expert lane" in low or "expert-lane" in low, \
        "Design section must be framed as the expert lane"
    assert "no fixed question set" in low, \
        "Design section must state there is no fixed question set"
    assert "design stance" in low, \
        "Design section must invite the user to state their design stance " \
        "in their own words"


# --- Engineering section — 5 stance questions with stakes --------------------

def test_engineering_has_five_stance_questions():
    text = _text()
    eng_idx = text.find("Engineering")
    assert eng_idx != -1, "must have an Engineering section"
    eng_text = text[eng_idx:]
    titles = [
        "Iteration vs robustness",
        "Reversibility posture",
        "Cost posture",
        "Data & privacy posture",
        "Escalation appetite",
    ]
    for title in titles:
        assert title in eng_text, \
            f"Engineering section must carry the stance question '{title}'"


def test_engineering_questions_carry_stakes_lines():
    """Each stance question is delivered as a mini-briefing: plain-language
    stakes first, then options, then a recommendation."""
    text = _text()
    stakes_count = len(re.findall(r"stakes:", text))
    assert stakes_count >= 5, \
        f"expected >=5 'stakes:' lines (one per stance question), found {stakes_count}"


def test_q5_stakes_line_is_provenance_marked_as_editorial_addition():
    """The plan requires 5 stance questions with stakes lines, but Q5's
    stakes clause ("how often the agent interrupts you vs how much drifts
    without your sign-off") does NOT exist in the content SSOT
    (instrument-v0.1.md Q5 has no stakes clause). Since the acceptance
    criterion still requires it, it must be honestly marked as an
    editorial addition naming its real source (the architecture doc §2),
    not passed off as SSOT content."""
    text = _text()
    eng_idx = text.find("Escalation appetite")
    assert eng_idx != -1, "must have the Escalation appetite question"
    q5_text = text[eng_idx:eng_idx + 500]
    low = q5_text.lower()
    assert "editorial addition" in low, \
        "Q5's stakes line must be marked as an editorial addition"
    assert "designer-pm-loop-architecture" in q5_text and "§2" in q5_text, \
        "Q5's provenance note must name the architecture doc §2 as source"
    assert "not in instrument v0.1" in low or "not from instrument v0.1" in low, \
        "Q5's provenance note must state it is not from instrument v0.1"


def test_tech_stack_slot_uses_derivation_for_confirmation_pattern():
    """FINDING-08: when the stack is already determined by the principles,
    present it as a derivation for confirmation, not an open ask."""
    text = _text()
    low = text.lower()
    assert "tech-stack declaration slot" in low or "tech stack declaration slot" in low, \
        "must name the tech-stack declaration slot"
    assert "derivation for confirmation" in low or "derivation-for-confirmation" in low, \
        "tech-stack slot must name the derivation-for-confirmation pattern"
    assert "not an open" in low or "not open" in low, \
        "must state the slot is not an open-ended ask"
