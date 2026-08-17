"""RED-first pin: docs-reviewer's omission dimension row covers
comparison-shaped prose left in a section the artifact's own template
routes to a markdown table (Task 5,
docs/loom/plans/2026-08-17-artifact-table-routing.md, Pin E).

@req: none (dispatch carries no registered REQ-ids for this plan)
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_REVIEWER = REPO_ROOT / "loom-code/agents/docs-reviewer.md"

APPENDED_SENTENCE = (
    "Comparison-shaped content — ≥2 options weighed on shared axes — "
    "left as prose in a section the artifact's own template routes to "
    "a markdown table (fill-or-declare), and an "
    "`N/A — no alternatives found:` declaration whose reason does not "
    "hold against the artifact's own content, are likewise omissions."
)

PIN_PHRASE = (
    "left as prose in a section the artifact's own template routes to "
    "a markdown table"
)

DIAGRAM_SENTENCE_TAIL = "are both omissions."

FINAL_SENTENCE = "Assert only after the full-text read (rule 1)."


def _omission_row() -> str:
    text = DOCS_REVIEWER.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "**omission**" in line:
            return line
    raise AssertionError("no line containing '**omission**' found in docs-reviewer.md")


def test_omission_row_names_table_routed_prose():
    row = _omission_row()
    assert row.count(PIN_PHRASE) == 1, f"pin phrase not exactly once in omission row: {row!r}"
    assert APPENDED_SENTENCE in row, f"Pin E sentence not verbatim in omission row: {row!r}"
    # Ordering: after the existing diagram-slot sentence, before the final sentence.
    assert row.index(DIAGRAM_SENTENCE_TAIL) < row.index(APPENDED_SENTENCE)
    assert row.index(APPENDED_SENTENCE) < row.index(FINAL_SENTENCE)
