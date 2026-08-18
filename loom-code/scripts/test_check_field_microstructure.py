"""Tests for check_field_microstructure.py — Task 1 of
docs/loom/plans/2026-08-19-field-value-microstructure.md.

`check_plan_fields(text) -> list[str]` walks each `## Task <N> —` block
and flags `Description` / `RED` / `GREEN` field values whose first line
carries more sentence-terminal marks than the field's grammar allows, or
whose continuation lines are neither a nested bullet nor a table row.

`Description` allows exactly one sentence. `RED` / `GREEN` allow one
assertion sentence plus one optional grounding clause (the
`Fails today because ...` clause `plan-format.md` itself teaches), so
they violate only at the third sentence-terminal mark.

Exercised by importing `check_plan_fields` directly (same convention as
`test_plan_card.py` importing `plan_card` internals) plus one CLI
subprocess test for `--help`.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

_SCRIPT = Path(__file__).parent / "check_field_microstructure.py"
_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

_spec = importlib.util.spec_from_file_location(
    "check_field_microstructure", _SCRIPT
)
check_field_microstructure = importlib.util.module_from_spec(_spec)
sys.modules["check_field_microstructure"] = check_field_microstructure
_spec.loader.exec_module(check_field_microstructure)

check_plan_fields = check_field_microstructure.check_plan_fields


def test_rejects_multi_sentence_description():
    text = (
        "## Task 1 — foo\n\n"
        "- **Description**: Do the first thing. Do the second thing.\n"
        "- **Module**: x\n"
        "- **Files touched**: x\n"
        "- **Acceptance**:\n"
        "  - **RED**: `test.py::test_foo` — asserts something.\n"
        "  - **GREEN**: it passes.\n"
        "- **Dependencies**: none\n"
        "- **Independent**: true\n"
        "- **Status**: pending\n"
    )
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


def test_red_allows_one_grounding_clause():
    two_sentence = _plan_with_red(
        "`test.py::test_foo` asserts something. "
        "Fails today because the module does not exist."
    )
    assert check_plan_fields(two_sentence) == []

    three_sentence = _plan_with_red(
        "`test.py::test_foo` asserts something. "
        "Fails today because the module does not exist. "
        "This is a third sentence."
    )
    problems = check_plan_fields(three_sentence)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "RED" in p for p in problems)


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


def test_accepts_unbackticked_version_number():
    text = _plan_with_description("Bump the version to 0.89.0.")
    assert check_plan_fields(text) == []


def test_rejects_unbackticked_version_number_plus_second_sentence():
    text = _plan_with_description("Bump the version to 0.89.0. Then ship it.")
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_accepts_eg_abbreviation():
    text = _plan_with_description(
        "Fetch data from the API, e.g. the users endpoint, and cache it."
    )
    assert check_plan_fields(text) == []


def test_rejects_eg_abbreviation_plus_second_sentence():
    text = _plan_with_description(
        "Fetch data from the API, e.g. the users endpoint. Then cache it."
    )
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_accepts_ie_abbreviation():
    text = _plan_with_description(
        "Use the flag, i.e. pass --json, to enable it."
    )
    assert check_plan_fields(text) == []


def test_rejects_ie_abbreviation_plus_second_sentence():
    text = _plan_with_description(
        "Use the flag, i.e. pass --json. Then run it."
    )
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_accepts_ellipsis_not_starting_new_sentence():
    text = _plan_with_description(
        "The scan runs long... eventually finishing."
    )
    assert check_plan_fields(text) == []


def test_rejects_ellipsis_starting_new_sentence():
    text = _plan_with_description(
        "The scan runs long... Eventually it finishes."
    )
    problems = check_plan_fields(text)
    assert problems, "expected a non-empty problem list"
    assert any("1" in p and "Description" in p for p in problems)


def test_help_exits_zero():
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--help"],
        capture_output=True,
        text=True,
        env=_ENV,
    )
    assert result.returncode == 0, result.stderr
