"""Pin test: brainstorming wires to the adjudication-view protocol.

Task 9 of docs/loom/plans/2026-08-12-adjudication-view.md — asserts the
sign-off checkpoint pointer to the adjudication-view protocol exists in
SKILL.md.
"""

import pathlib

SKILL_PATH = pathlib.Path(__file__).parent.parent / "skills" / "brainstorming" / "SKILL.md"


def test_brainstorming_pointer_present():
    # @req: none (task-scoped wiring pin, not bound to a registered REQ-id)
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert "protocols/adjudication-view.md" in skill_text, (
        "SKILL.md missing pointer to adjudication-view.md"
    )
