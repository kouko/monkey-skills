"""Prose-pin test for Task 7 (field-value grammar replaces `one-assertion`).

Plan: docs/loom/plans/2026-08-19-field-value-microstructure.md, Task 7.
Brief: docs/loom/specs/2026-08-19-field-value-microstructure.md, BI-7, BI-8.

plan-format.md is a prompt/contract artifact, not executable code — the
correctness condition is PRESENCE of the load-bearing phrases a plan
author/reviewer would read, same convention as the sibling pin tests on
this file (test_plan_diagram_slot.py, test_plan_format_prose_weight.py).

Pins:
  1. The positional rule is stated for `Description` (first line is
     exactly one sentence; every further clause routes into a nested
     bullet or a markdown table).
  2. The positional rule is stated for `Acceptance.RED` / `Acceptance.GREEN`
     (one assertion sentence plus one optional grounding clause on the
     first line — naming the `Fails today because ...` clause this same
     file already teaches as that grounding sentence).
  3. The `Goal:` header rule (one sentence, a 300-character ceiling, no
     nested body, naming `plan_card.py`'s fold as the reason) is stated.
  4. A before/after worked example lives under `## Worked example`.
  5. BI-8: the retired phrase `one-assertion unit of work` is gone, and no
     reworded restatement of "write one assertion" survives either.
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

RETIRED_PHRASE = "one-assertion unit of work"
GOAL_CEILING_PHRASE = "300-character"
FAILS_TODAY_PHRASE = "Fails today because"
WORKED_EXAMPLE_HEADING = "## Worked example"


def _text() -> str:
    assert PLAN_FORMAT_MD.is_file(), f"plan-format.md is absent at {PLAN_FORMAT_MD}"
    return PLAN_FORMAT_MD.read_text(encoding="utf-8")


def test_plan_format_states_positional_rule():
    """Fails today because the old wording is present at plan-format.md:98
    and none of the positional-rule phrases exist yet."""
    text = _text()

    assert RETIRED_PHRASE not in text, (
        f"retired phrase {RETIRED_PHRASE!r} still present — BI-8 not done"
    )
    # Description: first line is exactly one sentence; overflow routes
    # into a nested bullet or a markdown table.
    assert "first line is exactly one sentence" in text
    assert "nested bullet or a markdown table" in text
    # Acceptance.RED / Acceptance.GREEN: one assertion sentence plus one
    # optional grounding clause; the grounding clause is the existing
    # `Fails today because ...` teaching.
    assert "one assertion sentence" in text
    assert "one optional grounding clause" in text
    assert FAILS_TODAY_PHRASE in text
    # Goal: one sentence, 300-character ceiling, no nested body, naming
    # plan_card.py's fold as the reason.
    assert GOAL_CEILING_PHRASE in text
    assert "plan_card.py" in text
    # Before/after worked example lives under the existing `## Worked
    # example` section.
    assert WORKED_EXAMPLE_HEADING in text
    assert "before/after" in text.lower()


def test_no_reworded_restatement_of_one_assertion_survives():
    """Mechanical leg of the GREEN's second assertion: grep for the
    retired phrase and its closest paraphrases returns zero hits. The
    judgment leg (a reviewer confirming no OTHER reworded restatement
    survives) is not machine-checkable and is not asserted here."""
    text = _text()
    lowered = text.lower()

    assert "one-assertion unit of work" not in text
    assert "one assertion unit of work" not in lowered
    assert "write one assertion" not in lowered
