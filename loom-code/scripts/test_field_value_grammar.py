"""Prose-pin test for Task 7 (field-value grammar replaces `one-assertion`).

Plan: docs/loom/plans/2026-08-19-field-value-microstructure.md, Task 7.
Brief: docs/loom/specs/2026-08-19-field-value-microstructure.md, BI-7, BI-8.

plan-format.md is a prompt/contract artifact, not executable code — the
correctness condition is PRESENCE of the load-bearing phrases a plan
author/reviewer would read, same convention as the sibling pin tests on
this file (test_plan_diagram_slot.py, test_plan_format_prose_weight.py).

Round 2: BI-1 was amended a second time — sentence counting (both the
occurrence-based and boundary-heuristic attempts) was abandoned for a
plain 300-character cap on a field's first line, applied identically to
`Description`, `RED` and `GREEN`. This file's pins were updated to match;
the SSOT for the rule itself is `loom-code/scripts/check_field_microstructure.py`.

Round 3: the checker (as of `e43e973e`) caps TWO units at 300 characters,
not one — the field's own first line, AND each nested bullet's folded
text (its own line plus every wrapped continuation joined). This file's
wording used to describe nested bullets as pure overflow destination
with no length limit of their own; that was drift from the checker.
Pin 1 below is widened to require BOTH units stated under one number.

Round 4: the retired-phrase pin (BI-8) resolved only `plan-format.md`
(the SSOT) and stayed green while the retired phrase still shipped in
`writing-plans/SKILL.md`'s template — the surface a plan author actually
copies. The pin now runs against both files.

Pins:
  1. The character-cap rule is stated for `Description`, `RED` and
     `GREEN` alike — one 300-character ceiling that governs BOTH the
     first line AND each nested bullet's folded text, no per-field
     branch and no per-bullet exemption.
  2. The `Fails today because ...` grounding-clause teaching still
     appears (it now illustrates what fits inside the RED/GREEN first
     line, not a second sentence-counting rule).
  3. The `Goal:` header rule — carries no length ceiling (dropped
     2026-08-19, see the field-value-microstructure plan's Decision
     Log), admits no nested body, naming `plan_card.py`'s fold as the
     reason — is stated.
  4. A before/after worked example lives under `## Worked example`.
  5. BI-8: the retired phrase `one-assertion unit of work` is gone, and
     no reworded restatement of "write one assertion" survives either.
  6. No sentence-counting vocabulary (`exactly one sentence`, `one
     assertion sentence`, `one optional grounding clause`) survives —
     that rule was retired for the character cap, not merely renamed.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_FORMAT_MD = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-format.md"
)
WRITING_PLANS_SKILL_MD = (
    REPO_ROOT / "loom-code" / "skills" / "writing-plans" / "SKILL.md"
)
RETIRED_PHRASE_TARGETS = (PLAN_FORMAT_MD, WRITING_PLANS_SKILL_MD)

RETIRED_PHRASE = "one-assertion unit of work"
GOAL_NO_CEILING_PHRASE = "Carries no length ceiling"
FAILS_TODAY_PHRASE = "Fails today because"
WORKED_EXAMPLE_HEADING = "## Worked example"
FIRST_LINE_CAP_PHRASE = "300-character ceiling"
NO_PER_BULLET_EXEMPTION_PHRASE = "no per-bullet exemption"
FOLDED_UNIT_PHRASE = "folded across"


def _text() -> str:
    assert PLAN_FORMAT_MD.is_file(), f"plan-format.md is absent at {PLAN_FORMAT_MD}"
    return PLAN_FORMAT_MD.read_text(encoding="utf-8")


def test_plan_format_states_character_cap_rule():
    """The rule as it now stands: a field's first line violates when it
    exceeds 300 characters — the SAME cap for Description, RED and
    GREEN, no per-field branch, no sentence counting."""
    text = _text()

    assert RETIRED_PHRASE not in text, (
        f"retired phrase {RETIRED_PHRASE!r} still present — BI-8 not done"
    )
    # Description / RED / GREEN: first line stays within a 300-character
    # ceiling; overflow routes into a nested bullet or a markdown table.
    assert FIRST_LINE_CAP_PHRASE in text
    assert "nested bullet or a markdown table" in text
    assert "no per-field branch" in " ".join(text.split())
    # The Fails-today-because grounding-clause teaching still exists —
    # it now illustrates what fits inside the RED/GREEN first line.
    assert FAILS_TODAY_PHRASE in text
    # Goal: carries no length ceiling, admits no nested body, naming
    # plan_card.py's fold as the reason.
    assert GOAL_NO_CEILING_PHRASE in text
    assert "plan_card.py" in text
    # Before/after worked example lives under the existing `## Worked
    # example` section.
    assert WORKED_EXAMPLE_HEADING in text
    assert "before/after" in text.lower()


def test_plan_format_states_the_cap_governs_nested_bullets_too():
    """Round 3: `check_field_microstructure.py` caps BOTH the field's
    first line AND each nested bullet's folded text (its own line plus
    every wrapped continuation joined) at 300 characters — the same
    number, no second threshold. plan-format.md must state the duty
    for both units, not describe the nested bullet as an unlimited
    overflow destination."""
    text = _text()
    normalized = " ".join(text.split())

    assert NO_PER_BULLET_EXEMPTION_PHRASE in normalized
    assert FOLDED_UNIT_PHRASE in normalized


def test_no_reworded_restatement_of_one_assertion_survives():
    """Mechanical leg of the GREEN's second assertion: grep for the
    retired phrase and its closest paraphrases returns zero hits. The
    judgment leg (a reviewer confirming no OTHER reworded restatement
    survives) is not machine-checkable and is not asserted here.

    Runs against BOTH the SSOT (plan-format.md) and the functional copy
    a plan author actually copies from (writing-plans/SKILL.md's
    template) — resolving only the SSOT let the retired phrase survive
    in the template while this test stayed green."""
    for target in RETIRED_PHRASE_TARGETS:
        assert target.is_file(), f"{target} is absent"
        text = target.read_text(encoding="utf-8")
        lowered = text.lower()

        assert "one-assertion unit of work" not in text, target
        assert "one assertion unit of work" not in lowered, target
        assert "write one assertion" not in lowered, target


def test_no_sentence_counting_vocabulary_survives_in_field_grammar():
    """Round 2: sentence counting (both prior attempts) was abandoned
    for the character cap. The specific sentence-counting phrasings
    this section used to state must be gone, not merely relocated."""
    text = _text()

    assert "first line is exactly one sentence" not in text
    assert "one assertion sentence" not in text
    assert "one optional grounding clause" not in text
