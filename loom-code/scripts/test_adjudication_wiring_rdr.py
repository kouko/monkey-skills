"""Pin test: requesting-docs-review wires to the adjudication-view protocol.

Task 6 of docs/loom/plans/2026-08-12-adjudication-view-japanese.md — asserts
two additive pointer lines exist in SKILL.md: the hand-to-user moment and the
STILL_BLOCKING stop, each citing ../using-loom-code/protocols/adjudication-view.md,
and that neither pointer restates the protocol's firing condition (the
condition is now the protocol's own §Firing conditions, not a copy here).
"""

import pathlib

SKILL_PATH = pathlib.Path(__file__).parent.parent / "skills" / "requesting-docs-review" / "SKILL.md"


def test_rdr_pointers_present():
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    occurrences = skill_text.count("protocols/adjudication-view.md")
    assert occurrences >= 2, (
        f"expected >=2 pointer lines to protocols/adjudication-view.md, found {occurrences}"
    )


DEFERRAL_MARKER = "§Firing conditions"


def test_rdr_pointers_defer_to_protocol_firing_conditions():
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert "not English" not in skill_text, (
        "pointer restates the protocol's firing condition instead of deferring to "
        "protocols/adjudication-view.md's own §Firing conditions"
    )
    occurrences = skill_text.count(DEFERRAL_MARKER)
    assert occurrences >= 2, (
        f"expected both pointer sites to cite the protocol's own {DEFERRAL_MARKER}, "
        f"found {occurrences}"
    )
