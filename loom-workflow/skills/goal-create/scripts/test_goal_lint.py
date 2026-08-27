"""Tests for the goal-create mechanical lint floor (Task 3).

Two tests:
  1. test_floor_fails_structure_and_warns_on_judgment — the floor itself:
     a structurally complete goal passes; each of the four hard failures
     is exercised as its own single-violation mutant; a judgment-flavoured
     issue warns without failing the run.
  2. test_field_labels_match_the_shape_reference — cross-seam probe: the
     field labels goal_lint.py checks for must match the labels defined in
     references/goal-shape.md, so a rename upstream fails here instead of
     drifting silently.
"""

import re
from pathlib import Path

import goal_lint

SKILL_DIR = Path(__file__).parent.parent
GOAL_SHAPE = SKILL_DIR / "references" / "goal-shape.md"

COMPLETE_GOAL = """\
Outcome: The signup form submits with zero client-side validation errors.
Constraints: Do not touch the payment module.
Verification: Run `pytest tests/test_signup.py` and paste the output.
Stop-when: The outcome is reached, or stop after 20 turns.
"""


def test_floor_fails_structure_and_warns_on_judgment():
    # A structurally complete goal exits 0 with no hard errors.
    result = goal_lint.lint_text(COMPLETE_GOAL)
    assert result.errors == []
    assert result.exit_code == 0

    # --- Hard failure 1: a missing/empty field label. ---
    missing_field = """\
Outcome: The signup form submits with zero client-side validation errors.
Constraints: Do not touch the payment module.
Verification: Run `pytest tests/test_signup.py` and paste the output.
"""
    result = goal_lint.lint_text(missing_field)
    assert result.exit_code != 0
    assert any(f.code == "missing-field" for f in result.errors)
    assert not any(f.code == "no-stop-clause" for f in result.errors)
    assert not any(f.code == "no-backtick-command" for f in result.errors)
    assert not any(f.code == "length-limit" for f in result.errors)

    empty_field = """\
Outcome: The signup form submits with zero client-side validation errors.
Constraints:
Verification: Run `pytest tests/test_signup.py` and paste the output.
Stop-when: The outcome is reached, or stop after 20 turns.
"""
    result = goal_lint.lint_text(empty_field)
    assert result.exit_code != 0
    assert any(f.code == "missing-field" and "Constraints" in f.message for f in result.errors)

    # --- Hard failure 2: no stop clause (Stop-when present but empty of a clause). ---
    no_stop_clause = """\
Outcome: The signup form submits with zero client-side validation errors.
Constraints: Do not touch the payment module.
Verification: Run `pytest tests/test_signup.py` and paste the output.
Stop-when: The outcome is reached.
"""
    result = goal_lint.lint_text(no_stop_clause)
    assert result.exit_code != 0
    assert any(f.code == "no-stop-clause" for f in result.errors)
    assert not any(f.code == "missing-field" for f in result.errors)
    assert not any(f.code == "no-backtick-command" for f in result.errors)
    assert not any(f.code == "length-limit" for f in result.errors)

    # --- Hard failure 3: no backticked command inside Verification. ---
    no_backtick = """\
Outcome: The signup form submits with zero client-side validation errors.
Constraints: Do not touch the payment module.
Verification: Run pytest tests/test_signup.py and paste the output.
Stop-when: The outcome is reached, or stop after 20 turns.
"""
    result = goal_lint.lint_text(no_backtick)
    assert result.exit_code != 0
    assert any(f.code == "no-backtick-command" for f in result.errors)
    assert not any(f.code == "missing-field" for f in result.errors)
    assert not any(f.code == "no-stop-clause" for f in result.errors)
    assert not any(f.code == "length-limit" for f in result.errors)

    # --- Hard failure 4: text over the 4,000-character limit. ---
    too_long = (
        "Outcome: " + ("x" * 4000) + "\n"
        "Constraints: Do not touch the payment module.\n"
        "Verification: Run `pytest tests/test_signup.py` and paste the output.\n"
        "Stop-when: The outcome is reached, or stop after 20 turns.\n"
    )
    result = goal_lint.lint_text(too_long)
    assert result.exit_code != 0
    assert any(f.code == "length-limit" for f in result.errors)
    assert not any(f.code == "missing-field" for f in result.errors)
    assert not any(f.code == "no-stop-clause" for f in result.errors)
    assert not any(f.code == "no-backtick-command" for f in result.errors)

    # --- Characters, not bytes: CJK text must not trip the limit early. ---
    cjk_goal = (
        "Outcome: " + ("目" * 100) + "\n"
        "Constraints: Do not touch the payment module.\n"
        "Verification: Run `pytest tests/test_signup.py` and paste the output.\n"
        "Stop-when: The outcome is reached, or stop after 20 turns.\n"
    )
    result = goal_lint.lint_text(cjk_goal)
    assert not any(f.code == "length-limit" for f in result.errors)

    # --- Judgment-flavoured issue: warns but still exits 0. ---
    judgment_goal = """\
Outcome: The signup form works properly and looks nice.
Constraints: Do not touch the payment module.
Verification: Run `pytest tests/test_signup.py` and paste the output.
Stop-when: The outcome is reached, or stop after 20 turns.
"""
    result = goal_lint.lint_text(judgment_goal)
    assert result.errors == []
    assert result.exit_code == 0
    assert any(w.code == "undecidable-wording" for w in result.warnings)


def test_field_labels_match_the_shape_reference():
    shape_text = GOAL_SHAPE.read_text(encoding="utf-8")
    labels = re.findall(r"^\d+\.\s+`([^`]+)`$", shape_text, re.MULTILINE)
    assert labels, "expected the numbered field list in goal-shape.md to be parseable"
    assert list(goal_lint.FIELD_LABELS) == labels
