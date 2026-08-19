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

_MAX = 300


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
