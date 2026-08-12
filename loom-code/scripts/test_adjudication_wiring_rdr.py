"""Pin test: requesting-docs-review wires to the adjudication-view protocol.

Task 8 of docs/loom/plans/2026-08-12-adjudication-view.md — asserts two
additive pointer lines exist in SKILL.md: the hand-to-user moment and the
STILL_BLOCKING stop, each citing ../using-loom-code/protocols/adjudication-view.md.
"""

import pathlib

SKILL_PATH = pathlib.Path(__file__).parent.parent / "skills" / "requesting-docs-review" / "SKILL.md"


def test_rdr_pointers_present():
    # @req: none (task-scoped wiring pin, not bound to a registered REQ-id)
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    occurrences = skill_text.count("protocols/adjudication-view.md")
    assert occurrences >= 2, (
        f"expected >=2 pointer lines to protocols/adjudication-view.md, found {occurrences}"
    )
