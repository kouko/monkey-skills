"""Pin test: writing-plans wires to the adjudication-view protocol.

Task 8 of docs/loom/plans/2026-08-12-adjudication-view-japanese.md — asserts
both plan-presentation-moment pointers to the adjudication-view protocol exist
in SKILL.md (kickoff briefing + post-PASS progress-card relay).
"""

import pathlib

SKILL_PATH = pathlib.Path(__file__).parent.parent / "skills" / "writing-plans" / "SKILL.md"


def test_writing_plans_pointers_present():
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert skill_text.count("protocols/adjudication-view.md") >= 2, (
        "SKILL.md missing one or both pointers to adjudication-view.md"
    )


DEFERRAL_MARKER = "firing conditions"


def test_writing_plans_pointers_defer_to_protocol():
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert "not English" not in skill_text, (
        "SKILL.md still restates the firing condition instead of "
        "deferring to the protocol's own §Firing conditions"
    )
    occurrences = skill_text.count(DEFERRAL_MARKER)
    assert occurrences >= 2, (
        f"expected both pointer sites to cite the protocol's own {DEFERRAL_MARKER}, "
        f"found {occurrences}"
    )
