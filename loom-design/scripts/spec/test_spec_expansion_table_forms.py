"""Structural grep-test guarding that spec-expansion SKILL.md's two matrix
sections (Phase ③ `## Path × edge matrix` visible artifact + the
`## Cross-object combinations` additive-richness bullet) specify markdown
table form with pinned N/A lines (Pin C-1 / Pin C-2, docs/loom/plans/
2026-08-17-artifact-table-routing.md §Pinned wording).

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[2] / "skills" / "spec-expansion" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def test_matrix_sections_specify_table_form_and_na_lines():
    text = _text()

    # Pin C-1 — Path × edge matrix column list + N/A line prefix.
    pin_c1_columns = (
        "Backbone step | Object | CTA | State | Lens verdict | "
        "Expected reaction"
    )
    assert pin_c1_columns in text, \
        "Pin C-1's column-list phrase must appear verbatim"
    assert text.count(pin_c1_columns) == 1, \
        "Pin C-1's column-list phrase should appear exactly once " \
        "(load-bearing, not incidental prose)"

    pin_c1_na = "N/A — no surviving path/edge:"
    assert pin_c1_na in text, \
        "Pin C-1's N/A line prefix must appear verbatim"
    assert text.count(pin_c1_na) == 1, \
        "Pin C-1's N/A line prefix should appear exactly once"

    # Pin C-2 — Cross-object combinations column list + N/A line prefix.
    pin_c2_columns = "Stage | Co-active objects | Joint state | Required reaction"
    assert pin_c2_columns in text, \
        "Pin C-2's column-list phrase must appear verbatim"
    assert text.count(pin_c2_columns) == 1, \
        "Pin C-2's column-list phrase should appear exactly once " \
        "(load-bearing, not incidental prose)"

    pin_c2_na = "N/A — no interaction-dense stage:"
    assert pin_c2_na in text, \
        "Pin C-2's N/A line prefix must appear verbatim"
    assert text.count(pin_c2_na) == 1, \
        "Pin C-2's N/A line prefix should appear exactly once"

    # The old prose example clause must be gone — replaced by Pin C-2.
    assert "no interaction-dense stage — combinations N/A" not in text, \
        "the old honest-empty example line must be replaced by Pin C-2, " \
        "not merely supplemented"

    # Section header literals must stay untouched (validator +
    # test_spec_expansion_skill.py pin these whole-line headers).
    assert "## USM backbone" in text
    assert "## OOUX object model" in text
    assert "## Path × edge matrix" in text
    assert "## Cross-object combinations" in text
    assert "## Journey navigation" in text
