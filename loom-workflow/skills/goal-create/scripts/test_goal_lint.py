"""Tests for the goal-create mechanical lint floor (Task 3).

Three tests:
  1. test_floor_fails_structure_and_warns_on_judgment — the floor itself:
     a structurally complete goal passes; each of the three hard failures
     is exercised as its own single-violation mutant; a judgment-flavoured
     issue warns without failing the run; a well-formed English stop
     clause that a marker word list would have rejected still passes.
  2. test_field_parsing_treats_quoted_labels_as_content — a label-shaped
     line inside a *balanced* fenced code block is content belonging to
     the open field, not a new field boundary.
  3. test_field_labels_match_the_shape_reference — cross-seam probe: the
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

    # --- Hard failure 2: no backticked command inside Verification. ---
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
    assert not any(f.code == "length-limit" for f in result.errors)

    # --- Hard failure 3: text over the 4,000-character limit. ---
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

    # --- No hard failure ever fires for Stop-when's content: a marker-word
    # list would reject this well-formed English clause because it lacks
    # the literal substring "stop"; the floor must not reject it either. ---
    no_marker_word_stop_clause = """\
Outcome: The signup form submits with zero client-side validation errors.
Constraints: Do not touch the payment module.
Verification: Run `pytest tests/test_signup.py` and paste the output.
Stop-when: Halt after 20 turns regardless of outcome.
"""
    result = goal_lint.lint_text(no_marker_word_stop_clause)
    assert result.errors == []
    assert result.exit_code == 0


def test_field_parsing_treats_quoted_labels_as_content():
    # A label-shaped line inside a fenced code block is content, not a
    # boundary — Verification's real backticked command must still be
    # seen even though a fake "Outcome:" line sits between the label and
    # the real command.
    fenced_quote_goal = """\
Outcome: The signup form works.
Constraints: none
Verification: Example of a bad report format to avoid:
```
Outcome: this is not a real field
```
Now run `pytest tests/test_signup.py` and paste the output.
Stop-when: The outcome is reached, or stop after 20 turns.
"""
    result = goal_lint.lint_text(fenced_quote_goal)
    assert not any(f.code == "no-backtick-command" for f in result.errors)
    assert not any(f.code == "missing-field" for f in result.errors)
    assert result.exit_code == 0
    fields = goal_lint.parse_fields(fenced_quote_goal)
    assert "this is not a real field" in fields["Verification"]
    assert "pytest tests/test_signup.py" in fields["Verification"]


def test_unmatched_fence_does_not_swallow_the_rest_of_the_document():
    # An opening fence with no matching close is not a delimiter at all —
    # the text after it, including the real Stop-when label, is ordinary
    # content and must still be found.
    unmatched_fence_goal = """\
Outcome: The signup form submits with zero client-side validation errors.
Constraints: Do not touch the payment module.
Verification: Run `pytest tests/test_signup.py`, output shaped like:
```
(forgot to close the fence)
Stop-when: The outcome is reached, or stop after 20 turns.
"""
    result = goal_lint.lint_text(unmatched_fence_goal)
    assert not any(f.code == "missing-field" for f in result.errors)
    fields = goal_lint.parse_fields(unmatched_fence_goal)
    assert "Stop-when" in fields


def test_odd_backtick_count_does_not_swallow_the_rest_of_the_document():
    # A line with an odd number of backticks (a stray/typo'd backtick) is
    # not a delimiter with no match — the real Stop-when label after it
    # must still be found.
    stray_backtick_goal = """\
Outcome: The signup form submits with zero client-side validation errors.
Constraints: Do not touch the payment module.
Verification: Run `pytest tests/test_signup.py` and check the user`s config
Stop-when: The outcome is reached, or stop after 20 turns.
"""
    result = goal_lint.lint_text(stray_backtick_goal)
    assert not any(f.code == "missing-field" for f in result.errors)
    fields = goal_lint.parse_fields(stray_backtick_goal)
    assert "Stop-when" in fields


def test_two_independent_stray_backticks_do_not_pair_across_fields():
    # Two independently unpaired backticks (one on the Outcome line, and
    # a three-backtick Verification line — a balanced span plus a typo'd
    # apostrophe) must never pair with each other across a field
    # boundary. A stray backtick is just a character; it masks nothing.
    two_stray_backticks_goal = """\
Outcome: text with a stray backtick here `
Constraints: none
Verification: Run `pytest x` and check the user`s config
Stop-when: stop after 20 turns
"""
    result = goal_lint.lint_text(two_stray_backticks_goal)
    assert not any(f.code == "missing-field" for f in result.errors)
    fields = goal_lint.parse_fields(two_stray_backticks_goal)
    assert "Outcome" in fields
    assert "Constraints" in fields
    assert "Verification" in fields
    assert "Stop-when" in fields


def test_cross_line_stray_backticks_do_not_pair_as_a_command_span():
    # _BACKTICK_SPAN_RE excludes newlines (`[^`\n]+`) precisely so two
    # independent stray backticks on DIFFERENT lines of the same field
    # can never be read as one command span crossing the line break.
    # Here both backticks are apostrophe typos ("user`s", "report`s")
    # and there is no real backticked command anywhere in Verification —
    # this must fail with no-backtick-command. A mutant regex that
    # allows the span to cross lines (`[^`]+`) would instead pair these
    # two backticks together and wrongly accept this as a command.
    cross_line_stray_backticks_goal = """\
Outcome: The signup form submits with zero client-side validation errors.
Constraints: Do not touch the payment module.
Verification: Just paste the user`s config and then run the tests
and check the report`s summary.
Stop-when: The outcome is reached, or stop after 20 turns.
"""
    result = goal_lint.lint_text(cross_line_stray_backticks_goal)
    assert any(f.code == "no-backtick-command" for f in result.errors)


def test_field_labels_match_the_shape_reference():
    shape_text = GOAL_SHAPE.read_text(encoding="utf-8")
    labels = re.findall(r"^\d+\.\s+`([^`]+)`$", shape_text, re.MULTILINE)
    assert labels, "expected the numbered field list in goal-shape.md to be parseable"
    assert list(goal_lint.FIELD_LABELS) == labels


def test_stop_when_without_a_numeric_bound_warns_but_never_fails():
    # A syntactic digit check, not a word list: Stop-when with no digit
    # anywhere warns advisory-only; it must never raise exit_code above 0.
    no_number_goal = """\
Outcome: The signup form submits with zero client-side validation errors.
Constraints: Do not touch the payment module.
Verification: Run `pytest tests/test_signup.py` and paste the output.
Stop-when: Stop when the work is done.
"""
    result = goal_lint.lint_text(no_number_goal)
    assert result.errors == []
    assert result.exit_code == 0
    assert [f.code for f in result.warnings].count("no-numeric-bound") == 1

    # An ASCII digit inside CJK text must not trigger the warning (the check
    # is deliberately syntactic: a digit anywhere; Han numerals such as 六
    # DO warn, by design).
    cjk_bound_goal = """\
Outcome: The signup form submits with zero client-side validation errors.
Constraints: Do not touch the payment module.
Verification: Run `pytest tests/test_signup.py` and paste the output.
Stop-when: 6 輪到達且已回報——視為完成
"""
    result = goal_lint.lint_text(cjk_bound_goal)
    assert not any(f.code == "no-numeric-bound" for f in result.warnings)

    # The existing English 20-turn fixture must also stay warning-free.
    result = goal_lint.lint_text(COMPLETE_GOAL)
    assert not any(f.code == "no-numeric-bound" for f in result.warnings)
