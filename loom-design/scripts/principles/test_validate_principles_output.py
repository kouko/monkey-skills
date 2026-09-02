"""Tests for validate_principles_output.py — the loom 1.0 PRINCIPLES.md
structure check (Who / Non-negotiables >=3 / Won't do / Failure we must
avoid / Fixed choices, plus a well-formed 'ratified-by:' line when
present).
"""

from pathlib import Path

import pytest

from validate_principles_output import validate

_VALID = """\
# Product principles
ratified-by: Alex Rivera 2026-09-02
## Who
Solo developers tracking personal tasks.
## Non-negotiables (ordered)
1. Offline-first: saving works with the network off (bad: "feels fast").
2. No accounts: never require sign-up (bad: "sign-up is optional").
3. Single file storage: one plain-text file holds all data.
## Won't do
- Team features.
## Failure we must avoid
Silent data loss on crash.
## Fixed choices
- CLI only, no GUI planned.
"""


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "PRINCIPLES.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_valid_file_with_three_non_negotiables_passes(tmp_path):
    ok, problems = validate(_write(tmp_path, _VALID))
    assert ok, problems
    assert problems == []


def test_missing_file_fails(tmp_path):
    ok, problems = validate(tmp_path / "does-not-exist.md")
    assert not ok
    assert any("does not exist" in p for p in problems)


@pytest.mark.parametrize("section", [
    "## Who", "## Non-negotiables", "## Won't do",
    "## Failure we must avoid", "## Fixed choices",
])
def test_missing_any_required_section_fails(tmp_path, section):
    text = _VALID.replace(section, "## Renamed")
    ok, problems = validate(_write(tmp_path, text))
    assert not ok
    assert any("missing required section" in p for p in problems)


def test_two_non_negotiables_fails(tmp_path):
    text = _VALID.replace(
        '3. Single file storage: one plain-text file holds all data.\n', ""
    )
    ok, problems = validate(_write(tmp_path, text))
    assert not ok
    assert any("Non-negotiables" in p and "2 list item" in p for p in problems)


def test_three_non_negotiables_as_bullets_passes(tmp_path):
    text = _VALID.replace(
        "1. Offline-first: saving works with the network off "
        '(bad: "feels fast").\n'
        '2. No accounts: never require sign-up (bad: "sign-up is optional").\n'
        "3. Single file storage: one plain-text file holds all data.\n",
        "- Offline-first: saving works with the network off "
        '(bad: "feels fast").\n'
        '- No accounts: never require sign-up (bad: "sign-up is optional").\n'
        "- Single file storage: one plain-text file holds all data.\n",
    )
    ok, problems = validate(_write(tmp_path, text))
    assert ok, problems


def test_missing_ratified_by_is_valid_draft(tmp_path):
    text = _VALID.replace("ratified-by: Alex Rivera 2026-09-02\n", "")
    ok, problems = validate(_write(tmp_path, text))
    assert ok, problems


@pytest.mark.parametrize("bad_line", [
    "ratified-by: Alex Rivera\n",          # no date
    "ratified-by: 2026-09-02\n",           # no name
    "ratified-by: Alex Rivera 09-02-2026\n",  # wrong date shape
    "ratified-by:\n",                       # empty
])
def test_malformed_ratified_by_fails(tmp_path, bad_line):
    text = _VALID.replace("ratified-by: Alex Rivera 2026-09-02\n", bad_line)
    ok, problems = validate(_write(tmp_path, text))
    assert not ok
    assert any("malformed" in p for p in problems)


# --- W2 F5: the date in ratified-by must be a date, not a shape ------------


@pytest.mark.parametrize("bad_date", ["2026-13-45", "2026-02-30", "2026-00-10"])
def test_an_impossible_ratified_by_date_fails(tmp_path, bad_date):
    text = _VALID.replace("2026-09-02", bad_date)
    ok, problems = validate(_write(tmp_path, text))
    assert not ok
    assert any("not a real date" in p for p in problems)


def test_a_leap_day_that_exists_is_accepted(tmp_path):
    text = _VALID.replace("ratified-by: Alex Rivera 2026-09-02",
                          "ratified-by: Alex Rivera 2028-02-29")
    ok, problems = validate(_write(tmp_path, text))
    assert ok, problems


# --- W2 P04: three non-negotiables means three substantive, distinct ones --


def _with_non_negotiables(items: list[str]) -> str:
    return _VALID.replace(
        "1. Offline-first: saving works with the network off "
        '(bad: "feels fast").\n'
        '2. No accounts: never require sign-up (bad: "sign-up is optional").\n'
        "3. Single file storage: one plain-text file holds all data.\n",
        "".join(f"- {item}\n" for item in items),
    )


def test_three_identical_non_negotiables_fail(tmp_path):
    text = _with_non_negotiables(["it must be fast"] * 3)
    ok, problems = validate(_write(tmp_path, text))
    assert not ok
    assert any("Non-negotiables" in p for p in problems)


def test_items_differing_only_in_case_and_punctuation_are_not_distinct(tmp_path):
    text = _with_non_negotiables(["It must be fast.", "it must be fast", "IT MUST BE FAST!"])
    ok, problems = validate(_write(tmp_path, text))
    assert not ok


def test_one_word_slogans_do_not_count(tmp_path):
    text = _with_non_negotiables(["x", "y", "z"])
    ok, problems = validate(_write(tmp_path, text))
    assert not ok


def test_three_distinct_substantive_items_pass(tmp_path):
    text = _with_non_negotiables([
        "saving works with the network off",
        "never require a sign-up",
        "one plain-text file holds everything",
    ])
    ok, problems = validate(_write(tmp_path, text))
    assert ok, problems
