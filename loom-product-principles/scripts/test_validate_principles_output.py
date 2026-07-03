"""Tests for validate_principles_output.py — PRINCIPLES.md structure + the
load-bearing falsifiable-check rule (Task 5).

The validator checks a single PRINCIPLES.md file against the pinned contract in
`skills/product-principles/references/principles-rules.md`
("Validator contract (summary)" section). Valid iff:
  1. A `## North Star` section exists and is non-empty (>=1 non-whitespace,
     non-heading body line before the next `##`).
  2. A `## Product Principles` section exists with 3-7 entries, where an entry is a
     top-level ordered-list item (line matching `^\\d+\\.\\s`). Unordered
     bullets / nested items / the ✅❌ example lines do NOT count.
  3. Every principle entry carries the literal `— check:` marker (em dash
     U+2014, single space, lowercase `check`, colon) on the same line.
  4. `## Design Principles` / `## Engineering Principles` are optional:
     absent valid; present = 1-7 entries, same marker rules; empty invalid.
  5. No legacy `## Principles` heading (whole-line) — invalid with a
     migration message naming `## Product Principles`.

Each check = a function (text/path) -> list[str] of problems (empty == ok),
mirroring loom-spec/scripts/validate_spec_output.py. CLI:
`python validate_principles_output.py <PRINCIPLES.md>` -> exit 0 valid / 1
invalid.

Synthetic content only; no real brand / company / customer / product names.
Fixtures built INLINE via tmp_path (flat-folder rule: no fixtures/ subdir).
"""

import subprocess
import sys
from pathlib import Path

import pytest

from validate_principles_output import validate


SCRIPT = Path(__file__).with_name("validate_principles_output.py")

EM = "—"  # em dash U+2014


# --- fixture builders (inline; no fixtures/ subdir) -------------------------

def _north_star() -> str:
    return (
        "## North Star\n"
        "\n"
        "**Goal:** Let a solo operator capture a structured note in under five "
        "seconds without leaving the keyboard.\n"
        "\n"
        "**Success:** A first-time user completes capture-to-saved in <=5s "
        "measured on the happy-path flow, keyboard-only, with zero mouse events.\n"
    )


def _principles(n: int, *, marker: str = f" {EM} check:") -> str:
    """`## Product Principles` with n ordered-list entries, each carrying
    `marker`."""
    lines = ["## Product Principles\n", "\n"]
    for i in range(1, n + 1):
        lines.append(
            f"{i}. Principle statement number {i}{marker} testable condition {i} "
            f"observed in the happy-path flow.\n"
        )
    return "".join(lines)


def _valid_doc(n: int = 3) -> str:
    return (
        "# PRINCIPLES\n\n"
        + _north_star()
        + "\n"
        + _principles(n)
    )


# --- North Star section checks ---------------------------------------------

def test_valid_doc_passes(tmp_path):
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(_valid_doc(3), encoding="utf-8")
    ok, problems = validate(p)
    assert ok, f"fully-valid doc should pass, got: {problems}"
    assert problems == []


def test_missing_north_star_flagged(tmp_path):
    doc = "# PRINCIPLES\n\n" + _principles(3)
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("North Star" in m for m in problems), problems


def test_empty_north_star_flagged(tmp_path):
    # Heading present but no body line before the next `##`.
    doc = (
        "# PRINCIPLES\n\n"
        "## North Star\n"
        "\n"
        + _principles(3)
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("North Star" in m for m in problems), problems


# --- Principles section + count checks -------------------------------------

def test_missing_principles_flagged(tmp_path):
    doc = "# PRINCIPLES\n\n" + _north_star()
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("Principles" in m for m in problems), problems


def test_two_principles_count_too_low_flagged(tmp_path):
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(_valid_doc(2), encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("3" in m and "7" in m for m in problems), problems


def test_eight_principles_count_too_high_flagged(tmp_path):
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(_valid_doc(8), encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("3" in m and "7" in m for m in problems), problems


def test_seven_principles_count_ok(tmp_path):
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(_valid_doc(7), encoding="utf-8")
    ok, problems = validate(p)
    assert ok, f"7 principles is within 3-7, got: {problems}"


def test_unordered_bullets_do_not_count_as_entries(tmp_path):
    # Bullets and nested items are NOT ordered-list entries -> count 0 -> too low.
    doc = (
        "# PRINCIPLES\n\n"
        + _north_star()
        + "\n## Product Principles\n\n"
        f"- A bullet statement {EM} check: not an ordered entry\n"
        f"   1. A nested ordered item {EM} check: indented, not top-level\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("3" in m and "7" in m for m in problems), problems


def test_example_lines_do_not_count_as_entries(tmp_path):
    # The ✅/❌ example bullet lines must not be counted as principle entries.
    doc = (
        "# PRINCIPLES\n\n"
        + _north_star()
        + "\n## Product Principles\n\n"
        f"- ✅ `Primary task completes in <=3 steps {EM} check: count steps`\n"
        "- ❌ `Be delightful` — no check.\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("3" in m and "7" in m for m in problems), problems


# --- falsifiable-check marker (THE load-bearing rule) ----------------------

def test_principle_without_check_flagged(tmp_path):
    # One entry uses a hyphen instead of the em-dash `— check:` marker.
    doc = (
        "# PRINCIPLES\n\n"
        + _north_star()
        + "\n## Product Principles\n\n"
        f"1. First principle{EM} check: testable condition in the flow.\n"
        f"2. Second principle{EM} check: another testable condition.\n"
        "3. Third principle - check: a hyphen, not an em dash, so no marker.\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("check" in m for m in problems), problems


def test_hyphen_marker_does_not_satisfy(tmp_path):
    # Every entry uses `-- check:` (double hyphen) — none satisfies the marker.
    doc = (
        "# PRINCIPLES\n\n"
        + _north_star()
        + "\n## Product Principles\n\n"
        "1. First principle -- check: condition one.\n"
        "2. Second principle -- check: condition two.\n"
        "3. Third principle -- check: condition three.\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("check" in m for m in problems), problems


def test_wrong_case_check_does_not_satisfy(tmp_path):
    # `— Check:` (capital C) must NOT satisfy the lowercase-`check` marker.
    doc = (
        "# PRINCIPLES\n\n"
        + _north_star()
        + "\n## Product Principles\n\n"
        f"1. First principle{EM} Check: capital C does not satisfy.\n"
        f"2. Second principle{EM} check: lowercase ok here.\n"
        f"3. Third principle{EM} check: lowercase ok here too.\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("check" in m for m in problems), problems


def test_accepts_product_principles_heading(tmp_path):
    # The renamed required heading (`## Product Principles`) must be accepted
    # with the same 3-7-entries + marker rules as the legacy `## Principles`.
    doc = (
        "# PRINCIPLES\n\n"
        + _north_star()
        + "\n## Product Principles\n\n"
        f"1. First principle{EM} check: testable condition one.\n"
        f"2. Second principle{EM} check: testable condition two.\n"
        f"3. Third principle{EM} check: testable condition three.\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert ok, (
        f"'## Product Principles' heading with 3 marked entries should pass, "
        f"got: {problems}"
    )


# --- legacy heading migration message ---------------------------------------

def test_legacy_heading_gets_migration_message(tmp_path):
    # A file still using the legacy `## Principles` heading is invalid, and
    # the migration message names `## Product Principles` as the rename target.
    doc = (
        "# PRINCIPLES\n\n"
        + _north_star()
        + "\n## Principles\n\n"
        f"1. First principle{EM} check: testable condition one.\n"
        f"2. Second principle{EM} check: testable condition two.\n"
        f"3. Third principle{EM} check: testable condition three.\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    # Must be an actionable RENAME message (legacy heading detected), not the
    # generic "missing section" message that _check_principles_count would
    # emit on its own.
    assert any(
        "legacy" in m.lower() and "## Product Principles" in m
        for m in problems
    ), problems


def test_valid_doc_emits_no_legacy_warning(tmp_path):
    # A file already using the renamed `## Product Principles` heading must
    # NOT trip the legacy-heading check.
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(_valid_doc(3), encoding="utf-8")
    ok, problems = validate(p)
    assert ok, f"renamed heading should not trigger legacy warning: {problems}"
    assert not any("legacy" in m.lower() for m in problems), problems


# --- optional jurisdiction sections (Design/Engineering Principles) --------

_OPTIONAL_HEADINGS = ["## Design Principles", "## Engineering Principles"]


def _optional_section(heading: str, n: int, *, marker: str = f" {EM} check:") -> str:
    """`<heading>` with n ordered-list entries, each carrying `marker`."""
    lines = [f"{heading}\n", "\n"]
    for i in range(1, n + 1):
        lines.append(
            f"{i}. Clause statement number {i}{marker} testable condition {i} "
            f"observed in the happy-path flow.\n"
        )
    return "".join(lines)


@pytest.mark.parametrize("heading", _OPTIONAL_HEADINGS)
@pytest.mark.parametrize(
    "case",
    ["absent", "one_marked_entry", "eight_entries", "zero_entries", "missing_marker"],
)
def test_optional_jurisdiction_section_rules(tmp_path, heading, case):
    base = _valid_doc(3)
    if case == "absent":
        # No mention of the optional heading at all -> valid.
        doc = base
        expect_ok = True
    elif case == "one_marked_entry":
        # Floor of 1 marked entry -> valid.
        doc = base + "\n" + _optional_section(heading, 1)
        expect_ok = True
    elif case == "eight_entries":
        # Exceeds the 7-entry ceiling -> invalid.
        doc = base + "\n" + _optional_section(heading, 8)
        expect_ok = False
    elif case == "zero_entries":
        # Heading present, no entries -> invalid: a present-but-empty section
        # must be omitted, not left empty.
        doc = base + "\n" + f"{heading}\n\n"
        expect_ok = False
    else:  # missing_marker
        # An entry missing the literal `— check:` marker -> invalid.
        doc = (
            base + "\n" + f"{heading}\n\n"
            + "1. Clause without the marker at all.\n"
        )
        expect_ok = False

    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)

    if expect_ok:
        assert ok, f"case={case!r} heading={heading!r} should pass, got: {problems}"
        return

    assert not ok, f"case={case!r} heading={heading!r} should fail, got no problems"
    name = heading.removeprefix("## ")
    if case == "zero_entries":
        assert any(name in m and "omit" in m.lower() for m in problems), problems
    elif case == "missing_marker":
        assert any("check" in m for m in problems), problems
    else:  # eight_entries
        assert any(name in m for m in problems), problems


def test_all_three_sections_combined_validates_ok(tmp_path):
    # North Star + Product Principles + both optional sections together.
    doc = (
        _valid_doc(3)
        + "\n" + _optional_section("## Design Principles", 2)
        + "\n" + _optional_section("## Engineering Principles", 1)
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert ok, f"all three sections combined should validate OK, got: {problems}"


# --- CLI contract (thin __main__) ------------------------------------------

def _run_cli(target: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True, text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": ""},
    )


def test_cli_exit_zero_on_valid(tmp_path):
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(_valid_doc(3), encoding="utf-8")
    proc = _run_cli(p)
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_cli_nonzero_with_actionable_message_on_invalid(tmp_path):
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(_valid_doc(2), encoding="utf-8")  # count<3
    proc = _run_cli(p)
    assert proc.returncode != 0
    combined = proc.stdout + proc.stderr
    assert "Principles" in combined, combined
