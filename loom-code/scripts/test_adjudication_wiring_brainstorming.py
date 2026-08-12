"""Pin test: brainstorming wires to the adjudication-view protocol.

Task 9 of docs/loom/plans/2026-08-12-adjudication-view.md — asserts the
sign-off checkpoint pointer to the adjudication-view protocol exists in
SKILL.md.
"""

import pathlib

SKILL_PATH = pathlib.Path(__file__).parent.parent / "skills" / "brainstorming" / "SKILL.md"


def test_brainstorming_pointer_present():
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert "protocols/adjudication-view.md" in skill_text, (
        "SKILL.md missing pointer to adjudication-view.md"
    )


DEFERRAL_MARKER = "firing conditions"


def test_brainstorming_pointer_defers_to_protocol():
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert "protocols/adjudication-view.md" in skill_text, (
        "SKILL.md missing pointer to adjudication-view.md"
    )
    assert "not English" not in skill_text, (
        "pointer restates the firing condition instead of deferring to the protocol"
    )
    assert "side-by-side" not in skill_text, (
        "pointer still describes a layout the renderer does not produce"
    )
    assert DEFERRAL_MARKER in skill_text, (
        f"deferral clause missing — must cite the protocol's own {DEFERRAL_MARKER}, "
        "not just point at the file"
    )
