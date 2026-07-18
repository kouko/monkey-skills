"""Structural guard: evidence.md template carries the source-type column.

Plan: docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md, task 4.
The evidence template is prose/config (a tdd-iron-law exemption), so this is
a presence/shape assertion, not iron-law-mandated logic — but per
docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md, a whole-file
substring grep can go false-green when the asserted phrase pre-exists
elsewhere. Assertions here are scoped to a measured neighborhood window
anchored on the evidence table's header row, bounded by the next `##`
heading that is NOT the source-type legend itself — this excludes the
unrelated "## Confidence rubric" / "## Notes" sections from the window.

Load-bearing invariant: evidence typed at intake (craft / domain-convention
/ project-local) must flow downstream so later loom stations know which
authority owns each claim (knowledge-triage three-bucket doctrine). A claim
row with no source-type value, or a legend missing one of the three values,
silently breaks that routing.
"""

from pathlib import Path

TEMPLATE = (
    Path(__file__).parent.parent
    / "skills"
    / "user-insights"
    / "assets"
    / "evidence-template.md"
)

REQUIRED_VALUES = ("craft", "domain-convention", "project-local")


def _neighborhood(text: str) -> str:
    """Window from the evidence-table header row up to (excluding) the next
    '##' heading. Anchored on '| Claim id |' — unique to the evidence table,
    unlike generic terms ('Source', 'Confidence') that recur in sibling
    sections (`## Confidence rubric`, `## Notes`).
    """
    lines = text.splitlines()
    anchor_idx = next(
        i for i, line in enumerate(lines) if line.strip().startswith("| Claim id |")
    )
    end_idx = next(
        (
            i
            for i in range(anchor_idx + 1, len(lines))
            if lines[i].startswith("## ")
            and "source type" not in lines[i].strip().lower()
        ),
        len(lines),
    )
    return "\n".join(lines[anchor_idx:end_idx])


def test_template_exists():
    assert TEMPLATE.exists(), f"evidence-template.md missing at {TEMPLATE}"


def test_table_header_carries_source_type_column():
    window = _neighborhood(TEMPLATE.read_text(encoding="utf-8"))
    header_row = window.splitlines()[0]
    assert "Source type" in header_row, (
        f"evidence table header row missing 'Source type' column: {header_row!r}"
    )


def test_legend_defines_all_three_source_type_values():
    window = _neighborhood(TEMPLATE.read_text(encoding="utf-8"))
    assert "## Source type legend" in window, "source-type legend section missing"
    for value in REQUIRED_VALUES:
        assert value in window, f"source-type legend missing value {value!r}"


def test_table_row_offers_all_three_value_spellings():
    # The C1 example row must show the exact allowed spellings so an author
    # copies them verbatim rather than inventing a variant spelling.
    window = _neighborhood(TEMPLATE.read_text(encoding="utf-8"))
    example_row = next(line for line in window.splitlines() if line.startswith("| C1"))
    for value in REQUIRED_VALUES:
        assert value in example_row, f"C1 example row missing value {value!r}"
