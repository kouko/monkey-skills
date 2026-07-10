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
  6. `## Anchors` is optional: absent valid; present = well-formed table
     (header row + GFM separator row + >=1 data row with a non-empty
     version/edition cell); present-but-empty table invalid.
  7. `## Deviation Ledger` is optional: absent valid; present = >=1
     ordered-list entry, every entry carrying both `— reason:` and
     `— principle:` markers on the same line; present-but-empty invalid.

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


def test_optional_section_count_and_marker_problems_both_reported(tmp_path):
    # 8 entries (over the 7-ceiling), NONE carrying the `— check:` marker.
    # The required-section pair (_check_principles_count +
    # _check_every_principle_has_check) reports both a count problem and a
    # marker problem via separate registered functions; the optional-section
    # check must report the same completeness, not short-circuit on count.
    heading = "## Design Principles"
    lines = [f"{heading}\n", "\n"]
    for i in range(1, 9):
        lines.append(f"{i}. Clause without the marker at all, number {i}.\n")
    doc = _valid_doc(3) + "\n" + "".join(lines)
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("8" in m and "7" in m for m in problems), (
        f"expected a count problem, got: {problems}"
    )
    assert any("check" in m for m in problems), (
        f"expected marker problems too (not short-circuited), got: {problems}"
    )


def test_optional_section_seven_entries_marked_is_ok(tmp_path):
    # Ceiling case: exactly 7 marked entries in an optional section -> valid.
    p = tmp_path / "PRINCIPLES.md"
    doc = _valid_doc(3) + "\n" + _optional_section("## Engineering Principles", 7)
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert ok, f"7 marked entries in an optional section should pass, got: {problems}"


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


# --- Anchors optional section (enforce-when-present) ------------------------

def _anchors_table(rows: list[tuple[str, str]]) -> str:
    """`## Anchors` with a well-formed table: header row, GFM separator row,
    one data row per (canon, version) pair."""
    lines = [
        "## Anchors\n",
        "\n",
        "| Canon | Pinned version/edition |\n",
        "| --- | --- |\n",
    ]
    for canon, version in rows:
        lines.append(f"| {canon} | {version} |\n")
    return "".join(lines)


def test_anchors_absent_is_valid(tmp_path):
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(_valid_doc(3), encoding="utf-8")
    ok, problems = validate(p)
    assert ok, f"absent '## Anchors' should not affect validity, got: {problems}"


def test_anchors_well_formed_table_valid(tmp_path):
    doc = _valid_doc(3) + "\n" + _anchors_table(
        [("Material Design", "Material 3, 2024 spec")]
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert ok, f"well-formed Anchors table should pass, got: {problems}"


def test_anchors_row_with_empty_version_flagged(tmp_path):
    # Version/edition cell (second pipe-delimited cell) is empty -> invalid.
    doc = _valid_doc(3) + "\n" + _anchors_table([("Material Design", "")])
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("Anchors" in m for m in problems), problems


def test_anchors_present_but_empty_table_flagged(tmp_path):
    # Header + separator, zero data rows -> invalid; must be omitted, not left
    # empty.
    doc = (
        _valid_doc(3) + "\n"
        "## Anchors\n\n"
        "| Canon | Pinned version/edition |\n"
        "| --- | --- |\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("Anchors" in m for m in problems), problems


def test_anchors_table_with_trailing_prose_valid(tmp_path):
    # A well-formed table followed by trailing prose in the same section is
    # legal — rule 6 constrains the TABLE, not the section's prose after it.
    doc = (
        _valid_doc(3) + "\n"
        "## Anchors\n\n"
        "| Canon | Pinned version/edition |\n"
        "| --- | --- |\n"
        "| Material Design | Material 3 |\n"
        "\n"
        "Note: this anchor was chosen after a design review.\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert ok, f"table + trailing prose should pass, got: {problems}"


def test_anchors_table_with_pipe_in_trailing_prose_valid(tmp_path):
    # Trailing prose containing a literal `|` character must NOT be
    # mistaken for a data row — rule 6 requires a data row to be part of
    # the TABLE (start with `|` after stripping), not merely contain a
    # pipe character anywhere in the line. This sentence's `||` (logical
    # OR) reference splits into an empty middle cell under the naive
    # "contains a pipe" filter, which is exactly the false "empty
    # version cell" flag this test guards against — a line NOT starting
    # with `|` must never reach the version-cell check at all.
    doc = (
        _valid_doc(3) + "\n"
        "## Anchors\n\n"
        "| Canon | Pinned version/edition |\n"
        "| --- | --- |\n"
        "| Material Design | Material 3 |\n"
        "\n"
        "Note: the platform's `||` (logical OR) convention was already "
        "covered under Engineering Principles above.\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert ok, (
        f"table + trailing prose line containing '|' characters "
        f"should pass, got: {problems}"
    )


def test_anchors_missing_separator_row_flagged(tmp_path):
    # No GFM separator row (`^\|[\s:-]+\|`) below the header -> not a
    # well-formed table -> invalid.
    doc = (
        _valid_doc(3) + "\n"
        "## Anchors\n\n"
        "| Canon | Pinned version/edition |\n"
        "| Material Design | Material 3 |\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("Anchors" in m for m in problems), problems


# --- Deviation Ledger optional section (enforce-when-present) --------------

def test_deviation_ledger_absent_is_valid(tmp_path):
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(_valid_doc(3), encoding="utf-8")
    ok, problems = validate(p)
    assert ok, (
        f"absent '## Deviation Ledger' should not affect validity, got: "
        f"{problems}"
    )


def test_deviation_ledger_well_formed_entry_valid(tmp_path):
    doc = (
        _valid_doc(3) + "\n## Deviation Ledger\n\n"
        f"1. Skip the confirmation modal on delete {EM} reason: users act "
        f"20+ times per session {EM} principle: \"<=3-step primary task\"\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert ok, (
        f"well-formed Deviation Ledger entry should pass, got: {problems}"
    )


def test_deviation_ledger_entry_missing_principle_flagged(tmp_path):
    # `— reason:` present, `— principle:` absent -> invalid.
    doc = (
        _valid_doc(3) + "\n## Deviation Ledger\n\n"
        f"1. Skip the confirmation modal on delete {EM} reason: users act "
        f"20+ times per session\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("Deviation Ledger" in m for m in problems), problems


def test_deviation_ledger_present_but_empty_flagged(tmp_path):
    doc = _valid_doc(3) + "\n## Deviation Ledger\n\n"
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("Deviation Ledger" in m for m in problems), problems


def test_deviation_ledger_entry_missing_reason_flagged(tmp_path):
    # `— principle:` present, `— reason:` absent -> invalid.
    doc = (
        _valid_doc(3) + "\n## Deviation Ledger\n\n"
        f"1. Skip the confirmation modal on delete {EM} principle: "
        f"\"<=3-step primary task\"\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("Deviation Ledger" in m for m in problems), problems


def test_deviation_ledger_entry_missing_both_markers_flagged(tmp_path):
    # Neither `— reason:` nor `— principle:` present -> invalid.
    doc = (
        _valid_doc(3) + "\n## Deviation Ledger\n\n"
        "1. Skip the confirmation modal on delete, no markers at all.\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("Deviation Ledger" in m for m in problems), problems


def test_deviation_ledger_hyphen_markers_do_not_satisfy(tmp_path):
    # Hyphen-typo'd `- reason:` / `- principle:` (not em dash) must NOT
    # satisfy rule 7 — falls through to missing-marker, same as the existing
    # `— check:` hyphen-vs-em-dash coverage above.
    doc = (
        _valid_doc(3) + "\n## Deviation Ledger\n\n"
        "1. Skip the confirmation modal on delete - reason: users act "
        "20+ times per session - principle: \"<=3-step primary task\"\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert not ok
    assert any("Deviation Ledger" in m for m in problems), problems


def test_anchors_and_deviation_ledger_combined_valid(tmp_path):
    doc = (
        _valid_doc(3)
        + "\n" + _anchors_table(
            [("Apple Human Interface Guidelines", "2025 edition (iOS 18)")]
        )
        + "\n## Deviation Ledger\n\n"
        f"1. Skip the confirmation modal on delete {EM} reason: users act "
        f"20+ times per session {EM} principle: \"<=3-step primary task\"\n"
    )
    p = tmp_path / "PRINCIPLES.md"
    p.write_text(doc, encoding="utf-8")
    ok, problems = validate(p)
    assert ok, (
        f"Anchors + Deviation Ledger combined should pass, got: {problems}"
    )


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
