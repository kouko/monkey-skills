"""RED-first pin: docs-reviewer's omission dimension row covers
diagram-slot fill-or-declare contracts (Task 5,
docs/loom/plans/2026-08-11-visualization-trigger-layer.md).

@req: none (dispatch carries no registered REQ-ids for this plan)
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_REVIEWER = REPO_ROOT / "loom-code/agents/docs-reviewer.md"

APPENDED_SENTENCE = (
    "A diagram slot required by the artifact's own template contract "
    "(fill-or-declare) that is absent, and an "
    "`N/A — no flow/state/architecture-shaped content:` declaration "
    "whose reason does not hold against the artifact's own content, "
    "are both omissions."
)

PIN_PHRASE = "required by the artifact's own template contract (fill-or-declare)"

FINAL_SENTENCE = "Assert only after the full-text read (rule 1)."


def _omission_row() -> str:
    text = DOCS_REVIEWER.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "**omission**" in line:
            return line
    raise AssertionError("no line containing '**omission**' found in docs-reviewer.md")


def test_omission_row_names_diagram_slot_contract():
    row = _omission_row()
    assert PIN_PHRASE in row, f"pin phrase absent from omission row: {row!r}"
    assert row.count(PIN_PHRASE) == 1
    assert APPENDED_SENTENCE in row, f"appended sentence not verbatim in omission row: {row!r}"
    # The appended sentence must sit BEFORE the pre-existing final sentence.
    assert row.index(APPENDED_SENTENCE) < row.index(FINAL_SENTENCE)
