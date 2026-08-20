"""Tests for check_field_microstructure.py — Task 1 of
docs/loom/plans/2026-08-19-field-value-microstructure.md.

`check_plan_fields(text) -> list[str]` walks each `## Task <N> —` block
and flags `Description` / `RED` / `GREEN` field values whose first line
exceeds 300 characters, or whose continuation lines are neither a
nested bullet nor a table row.

The cap is a plain character count — no sentence counting, no
per-field branch. Two prior review rounds proved sentence-counting
(occurrence-based, then boundary-heuristic) cannot be made correct
here, so the punctuation-shape tests below assert that punctuation is
irrelevant under the cap: each shape is accepted at a short length and
at a length just under the cap, and rejected only once the line
exceeds 300 characters.

Exercised by importing `check_plan_fields` directly (same convention as
`test_plan_card.py` importing `plan_card` internals) plus one CLI
subprocess test for `--help`.
"""

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parent / "check_field_microstructure.py"
_PLAN_FORMAT_MD = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-format.md"
)
_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

_spec = importlib.util.spec_from_file_location(
    "check_field_microstructure", _SCRIPT
)
check_field_microstructure = importlib.util.module_from_spec(_spec)
sys.modules["check_field_microstructure"] = check_field_microstructure
_spec.loader.exec_module(check_field_microstructure)

check_plan_fields = check_field_microstructure.check_plan_fields
check_goal = check_field_microstructure.check_goal
check_brief_paragraphs = check_field_microstructure.check_brief_paragraphs

_MAX = 300


def _plan_with_goal(goal_block: str) -> str:
    """`goal_block` is the raw, already-formatted `Goal: ...` header line
    (plus any indented continuation lines), inserted verbatim into a
    minimal plan header followed by one task block."""
    return (
        f"{goal_block}"
        "Stage: sdd:wave-1\n"
        "\n"
        "## Task 1 — foo\n\n"
        "- **Description**: Do the thing.\n"
        "- **Acceptance**:\n"
        "  - **RED**: `test.py::test_foo` — asserts something.\n"
        "  - **GREEN**: it passes.\n"
        "- **Dependencies**: none\n"
        "- **Independent**: true\n"
        "- **Status**: pending\n"
    )


def test_rejects_goal_with_nested_body():
    text = _plan_with_goal(
        "Goal: Ship the thing.\n"
        "  - a nested bullet under Goal, which plan_card folds into the\n"
        "    card's single end-state: line and family-relay pins as verbatim\n"
    )
    problems = check_goal(text)
    assert problems, "expected a non-empty problem list"
    assert any("Goal" in p for p in problems)


def test_goal_violation_message_names_end_state_not_goal_line():
    # Pins the runtime message's claim about which rendered line
    # plan_card folds nested Goal: content into. The card renamed its
    # label from `goal:` to `end-state:`; a message that still says
    # "goal:" teaches the wrong fact to the author reading it at the
    # moment of violation (docs/loom/memory/
    # error-message-text-is-not-the-rules-statement.md).
    text = _plan_with_goal(
        "Goal: Ship the thing.\n"
        "  - a nested bullet under Goal\n"
    )
    problems = check_goal(text)
    assert problems, "expected a non-empty problem list"
    message = problems[0]
    assert "single end-state: line" in message
    assert "single goal: line" not in message


def test_accepts_overlong_goal():
    # `Goal:` carries no length ceiling — plan-format.md:32-36 freezes it
    # at plan time and never edits it afterward, so a cap enforceable
    # only by editing the value is unenforceable against a frozen field.
    # Dropped 2026-08-19 (Decision Log); see check_goal's docstring.
    text = _plan_with_goal(f"Goal: {'x' * 400}\n")
    assert check_goal(text) == []


def test_rejects_goal_with_nested_body_even_when_short():
    # The no-nested-body rule survives the length-ceiling removal: it has
    # its own justification (plan_card folds indented content into the
    # card's single line) independent of the dropped character cap.
    nested_body_problems = check_goal(
        _plan_with_goal(
            "Goal: Ship the thing.\n"
            "  - a nested bullet\n"
        )
    )
    assert nested_body_problems, "expected a non-empty problem list"
    assert any("Goal" in p for p in nested_body_problems)


def test_accepts_short_single_sentence_goal():
    text = _plan_with_goal("Goal: Ship the thing.\n")
    assert check_goal(text) == []


def _plan_with_description(description_value: str) -> str:
    return (
        "## Task 1 — foo\n\n"
        f"- **Description**: {description_value}\n"
        "- **Acceptance**:\n"
        "  - **RED**: `test.py::test_foo` — asserts something.\n"
        "  - **GREEN**: it passes.\n"
        "- **Dependencies**: none\n"
        "- **Independent**: true\n"
        "- **Status**: pending\n"
    )


def _plan_with_red(red_value: str) -> str:
    return (
        "## Task 1 — foo\n\n"
        "- **Description**: Do the thing.\n"
        "- **Acceptance**:\n"
        f"  - **RED**: {red_value}\n"
        "  - **GREEN**: it passes.\n"
        "- **Dependencies**: none\n"
        "- **Independent**: true\n"
        "- **Status**: pending\n"
    )


def _pad_to(text: str, length: int, filler: str = "x") -> str:
    """`text` padded with `filler` to exactly `length` characters, by
    appending before the trailing period so the padded string still
    reads as prose ending in `.`."""
    assert text.endswith(".")
    assert length >= len(text)
    body, _, _ = text.rpartition(".")
    pad_needed = length - len(text)
    return body + (filler * pad_needed) + "."


def test_rejects_over_cap_description():
    text = _plan_with_description("x" * 301)
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_accepts_first_line_plus_nested_bullets():
    text = (
        "## Task 1 — foo\n\n"
        "- **Description**: Do the thing.\n"
        "  - detail one\n"
        "  - detail two\n"
        "  | col1 | col2 |\n"
        "  | --- | --- |\n"
        "- **Acceptance**:\n"
        "  - **RED**: `test.py::test_foo` — asserts something.\n"
        "  - **GREEN**: it passes.\n"
        "- **Dependencies**: none\n"
        "- **Independent**: true\n"
        "- **Status**: pending\n"
    )
    assert check_plan_fields(text) == []


def test_red_accepts_at_300_rejects_at_301():
    prefix = "`test.py::test_foo` "
    at_cap_value = prefix + ("a" * (_MAX - len(prefix)))
    assert len(at_cap_value) == _MAX
    assert check_plan_fields(_plan_with_red(at_cap_value)) == []

    over_cap_value = at_cap_value + "a"
    problems = check_plan_fields(_plan_with_red(over_cap_value))
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "RED" in p for p in problems)


def test_accepts_300_char_first_line():
    text = _plan_with_description("x" * 300)
    assert check_plan_fields(text) == []


def test_rejects_301_char_first_line():
    text = _plan_with_description("x" * 301)
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_version_number_accepted_short_and_near_cap():
    short = "Bump the version to 0.89.0."
    assert check_plan_fields(_plan_with_description(short)) == []

    near_cap = _pad_to(short, _MAX)
    assert check_plan_fields(_plan_with_description(near_cap)) == []

    over_cap = _pad_to(short, _MAX + 1)
    problems = check_plan_fields(_plan_with_description(over_cap))
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_eg_abbreviation_accepted_short_and_near_cap():
    short = "Fetch data from the API, e.g. the users endpoint, and cache it."
    assert check_plan_fields(_plan_with_description(short)) == []

    near_cap = _pad_to(short, _MAX)
    assert check_plan_fields(_plan_with_description(near_cap)) == []

    over_cap = _pad_to(short, _MAX + 1)
    problems = check_plan_fields(_plan_with_description(over_cap))
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_ie_abbreviation_accepted_short_and_near_cap():
    short = "Use the flag, i.e. pass --json, to enable it."
    assert check_plan_fields(_plan_with_description(short)) == []

    near_cap = _pad_to(short, _MAX)
    assert check_plan_fields(_plan_with_description(near_cap)) == []

    over_cap = _pad_to(short, _MAX + 1)
    problems = check_plan_fields(_plan_with_description(over_cap))
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_ellipsis_accepted_short_and_near_cap():
    short = "The scan runs long... eventually finishing."
    assert check_plan_fields(_plan_with_description(short)) == []

    near_cap = _pad_to(short, _MAX)
    assert check_plan_fields(_plan_with_description(near_cap)) == []

    over_cap = _pad_to(short, _MAX + 1)
    problems = check_plan_fields(_plan_with_description(over_cap))
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_multi_sentence_description_accepted_under_cap():
    # Round-1's rule rejected this outright (>1 sentence-terminal mark).
    # Under a character cap it is accepted as long as it fits.
    text = _plan_with_description("Do the first thing. Do the second thing.")
    assert check_plan_fields(text) == []


def test_three_sentence_red_accepted_under_cap():
    # Round-1's rule rejected this at the third sentence-terminal mark.
    # Under a character cap it is accepted as long as it fits.
    text = _plan_with_red(
        "`test.py::test_foo` asserts something. "
        "Fails today because the module does not exist. "
        "This is a third sentence."
    )
    assert check_plan_fields(text) == []


def test_accepts_reviewer_false_negative_counterexample():
    # This is the exact counterexample the reviewer used to demonstrate
    # round-1's boundary heuristic false-negatived: a third sentence
    # starting with a lowercase token was invisible to the heuristic, so
    # an over-cap field passed clean. Under a character cap it is
    # correctly accepted (it fits inside 300 characters) — for a
    # different reason: there is no sentence machinery to fool.
    text = _plan_with_description(
        "... asserts something. Fails today because the module does not "
        "exist. returns None when clean."
    )
    assert check_plan_fields(text) == []


def test_accepts_reviewer_false_positive_counterexample():
    # This is the exact counterexample the reviewer used to demonstrate
    # round-1's boundary heuristic false-positived: `e.g.` followed by a
    # capitalised proper noun (a library name) still miscounted as a
    # sentence boundary. Under a character cap it is correctly accepted
    # — there is no boundary detection left to trip.
    text = _plan_with_description(
        "Route overflow into a bullet, e.g. Python's textwrap."
    )
    assert check_plan_fields(text) == []


def _plan_with_raw_description_block(description_block: str) -> str:
    """`description_block` is the raw, already-formatted
    `- **Description**: ...` bullet (plus its nested lines), inserted
    verbatim into a full task block."""
    return (
        "## Task 1 — foo\n\n"
        f"{description_block}"
        "- **Acceptance**:\n"
        "  - **RED**: `test.py::test_foo` — asserts something.\n"
        "  - **GREEN**: it passes.\n"
        "- **Dependencies**: none\n"
        "- **Independent**: true\n"
        "- **Status**: pending\n"
    )


def test_accepts_nested_bullet_wrapped_across_two_lines():
    # The defect this round fixes: wrapping a long nested bullet across
    # two physical lines is ordinary markdown and must not be flagged.
    text = _plan_with_raw_description_block(
        "- **Description**: Short first line.\n"
        "  - A nested bullet whose text is long enough that a human wraps it\n"
        "    across two physical lines, which is ordinary markdown.\n"
    )
    assert check_plan_fields(text) == []


def test_accepts_nested_bullet_wrapped_continuation_indented_with_tab():
    # Reproduces the defect: _NESTED_BULLET_LINE matches leading `\s`
    # (tabs included), so a bullet reached via a TAB indent is a legal
    # nested bullet — but its wrapped continuation line's indent was
    # measured with spaces only (`raw.lstrip(" ")`), so a tab-indented
    # continuation always measured as indent 0 and was rejected even
    # though wrapping a long nested bullet across lines is legal.
    text = _plan_with_raw_description_block(
        "- **Description**: Short first line.\n"
        "\t- A nested bullet reached via a tab indent that a human wraps\n"
        "\t  across two physical lines, which is ordinary markdown.\n"
    )
    assert check_plan_fields(text) == []


def test_rejects_wrapped_continuation_under_table_row():
    # A wrapped continuation line is only legal directly under a nested
    # bullet — the grammar does not extend the exemption to table rows.
    # A deep-indented line following a table row with no preceding
    # nested bullet still violates.
    text = _plan_with_raw_description_block(
        "- **Description**: Short first line.\n"
        "  | col1 | col2 |\n"
        "    a wrapped-looking line that is not itself a table row\n"
    )
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_rejects_indented_prose_with_no_preceding_nested_bullet():
    # This is the assertion that stops shape 3 from swallowing the
    # whole rule: an indented prose line under a field with NO
    # preceding nested bullet is still a violation (prose crammed
    # under the field, which the rule exists to catch).
    text = _plan_with_raw_description_block(
        "- **Description**: Short first line.\n"
        "  This is indented prose with no nested bullet above it.\n"
    )
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_continuation_violation_message_names_all_three_shapes():
    # The message an author sees on a rejected continuation line must
    # name all three permitted shapes (nested bullet / table row /
    # wrapped continuation of the nested bullet above) AND state the
    # wrapped-continuation remedy: indent to at least the bullet's own
    # text column. Naming only two shapes tells an author whose bullet
    # wrapped one column too shallow to convert it to a bullet or a
    # table, when the actual fix is to indent deeper.
    text = _plan_with_raw_description_block(
        "- **Description**: Short first line.\n"
        "  This is indented prose with no nested bullet above it.\n"
    )
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    message = next(p for p in problems if "Description" in p)
    assert "nested bullet" in message
    assert "table row" in message
    assert "wrapped continuation" in message
    assert "indent it to at least that bullet's own text column" in message


def test_rejects_crammed_prose_after_table_row_following_earlier_bullet():
    # Round-4 defect: a nested bullet EARLIER in the field must not
    # leak its wrap permission past an intervening table row. A table
    # row ends the preceding bullet's wrap window, so a later
    # deep-indented prose line is still a violation even though a
    # bullet appeared somewhere above it in the same field.
    text = _plan_with_raw_description_block(
        "- **Description**: Short first line.\n"
        "  - A nested bullet with some text here.\n"
        "  | col1 | col2 |\n"
        "    this deep-indented line is crammed prose after a table "
        "row, not a continuation\n"
    )
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any(
        "1" in p and "Description" in p and "crammed prose" in p
        for p in problems
    )


def test_accepts_wrapped_continuation_under_bullet_that_reopens_after_table():
    # Mirror of the round-4 defect: a table row ends the FIRST bullet's
    # wrap window, but a SECOND nested bullet after the table reopens
    # it — a wrap under that second bullet is still ordinary markdown
    # and must be accepted.
    text = _plan_with_raw_description_block(
        "- **Description**: Short first line.\n"
        "  - A nested bullet with some text here.\n"
        "  | col1 | col2 |\n"
        "  - Another nested bullet whose text is long enough that a\n"
        "    human wraps it across two physical lines.\n"
    )
    assert check_plan_fields(text) == []


def test_rejects_decoy_bullet_with_unbounded_folded_prose():
    # Round-4 second leak: a nested bullet's wrap window had no upper
    # bound — a one-word decoy bullet followed by many wrap-shaped
    # prose lines was accepted unconditionally. The bullet's own text
    # PLUS every wrap line folded together must still respect the
    # 300-character cap, same as a field's first line.
    prose_lines = "\n".join(
        f"    crammed prose line {i} that has nothing to do with the "
        "bullet above it and packs unstructured reasoning past the cap."
        for i in range(10)
    )
    text = _plan_with_raw_description_block(
        "- **Description**: Short first line.\n"
        "  - a\n"
        f"{prose_lines}\n"
    )
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_accepts_folded_bullet_text_at_300_rejects_at_301():
    prefix = "A nested bullet whose folded text is exactly at the cap "
    at_cap_text = prefix + ("a" * (_MAX - len(prefix)))
    assert len(at_cap_text) == _MAX
    text = _plan_with_raw_description_block(
        "- **Description**: Short first line.\n"
        f"  - {at_cap_text}\n"
    )
    assert check_plan_fields(text) == []

    over_cap_text = at_cap_text + "a"
    text = _plan_with_raw_description_block(
        "- **Description**: Short first line.\n"
        f"  - {over_cap_text}\n"
    )
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_rejects_single_unwrapped_bullet_over_cap():
    # Pins the (a)-vs-(b) distinction: a bullet that is a SINGLE
    # physical line (no wrap at all) still violates once it exceeds
    # the cap. Every case above this one involves wrapping; without
    # this test nothing stops a future edit from re-scoping the cap to
    # only wrapped bullets (interpretation (a), rejected because it
    # rewards not wrapping — same content, opposite verdict depending
    # on where the author presses Enter).
    single_line = "x" * (_MAX + 50)
    text = _plan_with_raw_description_block(
        "- **Description**: Short first line.\n"
        f"  - {single_line}\n"
    )
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_accepts_plan_format_md_verbatim_after_example():
    # Extract the "after" example from plan-format.md's
    # §Field-value grammar — before/after section verbatim, and prove
    # it is accepted — the example that exists to demonstrate
    # compliance must actually comply.
    text = _PLAN_FORMAT_MD.read_text(encoding="utf-8")
    match = re.search(
        r"### Field-value grammar — before/after\n\n"
        r"Before.*?```markdown\n.*?```\n\n"
        r"After.*?```markdown\n(?P<after>.*?)```\n",
        text,
        re.S,
    )
    assert match, "could not locate the after example in plan-format.md"
    description_block = match.group("after")
    assert description_block.startswith("- **Description**:")
    plan_text = _plan_with_raw_description_block(description_block)
    assert check_plan_fields(plan_text) == []


def test_help_exits_zero():
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--help"],
        capture_output=True,
        text=True,
        env=_ENV,
    )
    assert result.returncode == 0, result.stderr


# --- check_brief_paragraphs (Task 3) --------------------------------
#
# SSOT: loom-code/skills/brainstorming/references/handoff-brief-format.md
# §Paragraph length — 600-character threshold, `<!-- narrative: <reason>
# -->` declaration line directly beneath the paragraph, empty/whitespace
# reason counts as absent, `## Current State Evidence` and
# `## Alternatives Considered` exempt.


def test_flags_long_paragraph_without_declaration():
    text = "## Decision\n\n" + ("a" * 700) + "\n"
    problems = check_brief_paragraphs(text)
    assert len(problems) == 1
    assert "Decision" in problems[0]


def test_declared_narrative_paragraph_passes():
    text = (
        "## Decision\n\n"
        + ("a" * 700)
        + "\n"
        "<!-- narrative: each sentence depends on the one before it -->\n"
    )
    assert check_brief_paragraphs(text) == []


def test_skips_evidence_and_alternatives_sections():
    text = (
        "## Current State Evidence\n\n"
        + ("a" * 700)
        + "\n\n"
        "## Alternatives Considered\n\n"
        + ("b" * 700)
        + "\n"
    )
    assert check_brief_paragraphs(text) == []


def test_empty_declaration_reason_treated_as_absent():
    text = "## Decision\n\n" + ("a" * 700) + "\n" "<!-- narrative:    -->\n"
    problems = check_brief_paragraphs(text)
    assert len(problems) == 1
    assert "Decision" in problems[0]


def test_whitespace_only_declaration_reason_treated_as_absent():
    text = "## Decision\n\n" + ("a" * 700) + "\n" "<!-- narrative: \t -->\n"
    problems = check_brief_paragraphs(text)
    assert len(problems) == 1


def test_fenced_block_content_not_measured_as_paragraph():
    text = "## Decision\n\n" "```mermaid\n" + ("a" * 700) + "\n" "```\n"
    assert check_brief_paragraphs(text) == []


def test_accepts_600_chars_rejects_601():
    text_600 = "## Decision\n\n" + ("a" * 600) + "\n"
    assert check_brief_paragraphs(text_600) == []

    text_601 = "## Decision\n\n" + ("a" * 601) + "\n"
    problems = check_brief_paragraphs(text_601)
    assert len(problems) == 1
    assert "Decision" in problems[0]


def test_list_item_block_not_measured_as_paragraph():
    # A block containing a list-item line is not a "paragraph" per the
    # grammar ("none of whose lines is a heading, list item, table row,
    # or blockquote") — never measured, regardless of length.
    text = "## Decision\n\n- " + ("a" * 700) + "\n"
    assert check_brief_paragraphs(text) == []


def test_table_row_block_not_measured_as_paragraph():
    text = "## Decision\n\n| " + ("a" * 700) + " |\n"
    assert check_brief_paragraphs(text) == []


def test_blockquote_block_not_measured_as_paragraph():
    text = "## Decision\n\n> " + ("a" * 700) + "\n"
    assert check_brief_paragraphs(text) == []


def test_heading_line_is_never_a_paragraph():
    # A too-long heading line is not prose; only its own H2 chunking
    # matters, not a length rule on the heading text itself.
    text = "## " + ("a" * 700) + "\n"
    assert check_brief_paragraphs(text) == []


def test_brief_cli_flags_violation(tmp_path):
    brief = tmp_path / "brief.md"
    brief.write_text("## Decision\n\n" + ("a" * 700) + "\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--brief", str(brief)],
        capture_output=True,
        text=True,
        env=_ENV,
    )
    assert result.returncode == 1
    assert "Decision" in result.stderr


def test_brief_cli_clean_exits_zero(tmp_path):
    brief = tmp_path / "brief.md"
    brief.write_text("## Decision\n\nShort paragraph.\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--brief", str(brief)],
        capture_output=True,
        text=True,
        env=_ENV,
    )
    assert result.returncode == 0, result.stderr


# --- revision round 1: CRLF gap-check arithmetic ---------------------
#
# `_iter_paragraph_blocks`'s gap check must be newline-width agnostic:
# `iter_lines_outside_fences` walks `text.splitlines(keepends=True)`,
# so on CRLF input every physical line is one byte longer than a
# hardcoded LF (`+1`) assumption accounts for.


def test_crlf_multiline_paragraph_merges_and_is_flagged():
    # False-negative direction: on the old hardcoded-+1 arithmetic, a
    # CRLF gap fired at every line boundary, so each physical line
    # became its own (short, unflagged) block and a genuinely long
    # paragraph was never measured.
    text = "## Decision\r\n\r\n" + "a" * 250 + "\r\n" + "b" * 250 + "\r\n" + "c" * 250 + "\r\n"
    problems = check_brief_paragraphs(text)
    assert len(problems) == 1
    assert "Decision" in problems[0]


def test_lf_multiline_paragraph_merges_and_is_flagged():
    # LF counterpart of the CRLF case above — guards against a future
    # normalization fix that repairs CRLF but breaks LF.
    text = "## Decision\n\n" + "a" * 250 + "\n" + "b" * 250 + "\n" + "c" * 250 + "\n"
    problems = check_brief_paragraphs(text)
    assert len(problems) == 1
    assert "Decision" in problems[0]


def test_crlf_correctly_placed_declaration_is_recognised():
    # False-positive direction: on the old arithmetic, a correctly
    # placed declaration line was never merged into the paragraph's
    # block (the CRLF gap already split them apart), so the paragraph
    # was flagged despite carrying a valid declaration.
    text = (
        "## Decision\r\n\r\n"
        + "a" * 700
        + "\r\n"
        "<!-- narrative: because reasons -->\r\n"
    )
    assert check_brief_paragraphs(text) == []


def test_lf_correctly_placed_declaration_is_recognised():
    text = (
        "## Decision\n\n"
        + "a" * 700
        + "\n"
        "<!-- narrative: because reasons -->\n"
    )
    assert check_brief_paragraphs(text) == []


# --- revision round 1: exempt-section normalization -------------------


def test_exempt_section_case_variant_is_exempt():
    text = "## current state evidence\n\n" + ("a" * 700) + "\n"
    assert check_brief_paragraphs(text) == []


def test_exempt_section_spacing_variant_is_exempt():
    text = "## Current  State  Evidence\n\n" + ("a" * 700) + "\n"
    assert check_brief_paragraphs(text) == []


def test_genuinely_different_heading_is_not_exempt():
    text = "## Current State Overview\n\n" + ("a" * 700) + "\n"
    problems = check_brief_paragraphs(text)
    assert len(problems) == 1
    assert "Current State Overview" in problems[0]


# --- revision round 2: parenthetical-suffix normalization -------------
#
# Task 15 measured the corpus: 63 of 171 real
# `## Alternatives Considered` headings carry a trailing parenthetical
# decoration and silently lost their exemption. Forms below are pulled
# verbatim from docs/loom/specs/*.md.


@pytest.mark.parametrize(
    "heading",
    [
        "## Alternatives Considered (Axis 4)",
        "## Alternatives Considered (Axis 4 — research-grounded)",
        "## Alternatives Considered (research-grounded)",
        "## Alternatives Considered (Axis 4 — research-grounded, EN + JA)",
        "## Alternatives Considered (settled earlier this session; cited, not reopened)",
        "## Alternatives Considered（Axis 4 — 已研究）",
        "## Alternatives Considered（Axis 4 — 本 session 已研究）",
        "## Alternatives Considered（Axis 4 — 已搜，EN + JA）",
    ],
)
def test_decorated_alternatives_considered_heading_is_exempt(heading):
    text = heading + "\n\n" + ("a" * 700) + "\n"
    assert check_brief_paragraphs(text) == []


def test_current_state_evidence_brownfield_suffix_is_exempt():
    text = "## Current State Evidence (brownfield)\n\n" + ("a" * 700) + "\n"
    assert check_brief_paragraphs(text) == []


def test_heading_that_merely_starts_with_exempt_words_is_not_exempt():
    # Must NOT widen into a prefix match: a genuinely different section
    # whose name happens to start with "Alternatives Considered" is a
    # different section, not a decorated exempt one.
    text = "## Alternatives Considered And Rejected Approaches\n\n" + ("a" * 700) + "\n"
    problems = check_brief_paragraphs(text)
    assert len(problems) == 1
    assert "Alternatives Considered And Rejected Approaches" in problems[0]


# --- revision round 1: missing-vs-misplaced declaration message -------


def test_misplaced_declaration_message_names_requirement():
    # A blank line between the paragraph and the declaration is still
    # a violation (SSOT requires "directly beneath"), but the message
    # must name the requirement instead of reading identically to the
    # no-declaration-at-all case.
    text = (
        "## Decision\n\n"
        + ("a" * 700)
        + "\n\n"
        "<!-- narrative: because reasons -->\n"
    )
    problems = check_brief_paragraphs(text)
    assert len(problems) == 1
    assert "immediately below" in problems[0]
    assert "no blank line" in problems[0]


def test_no_declaration_at_all_message_unchanged():
    text = "## Decision\n\n" + ("a" * 700) + "\n"
    problems = check_brief_paragraphs(text)
    assert len(problems) == 1
    assert "no narrative declaration" in problems[0]
    assert "immediately below" not in problems[0]


# --- revision round 1, fix 4: fence-adjacent gap check must not merge
# two independent paragraphs into one block --------------------------
#
# Reproduces the spec-reviewer's finding: without the gap check, a
# paragraph immediately above a fence and a paragraph immediately
# below it (no blank line separating either from the fence) collapse
# into a single block and get measured/declaration-checked together.
# Each paragraph here is comfortably under 600 chars on its own but
# their concatenation exceeds it, so a merge is visible as a spurious
# violation rather than an incidental count difference.


def test_lf_paragraphs_around_fence_are_not_merged():
    text = (
        "## Decision\n\n"
        + ("a" * 400)
        + "\n```\nfence content\n```\n"
        + ("b" * 400)
        + "\n"
    )
    assert check_brief_paragraphs(text) == []


def test_crlf_paragraphs_around_fence_are_not_merged():
    text = (
        "## Decision\r\n\r\n"
        + ("a" * 400)
        + "\r\n```\r\nfence content\r\n```\r\n"
        + ("b" * 400)
        + "\r\n"
    )
    assert check_brief_paragraphs(text) == []
