"""Pin test: writing-plans wires to the adjudication-view protocol.

Task 10 of docs/loom/plans/2026-08-12-adjudication-view.md — asserts both
plan-presentation-moment pointers to the adjudication-view protocol exist
in SKILL.md (kickoff briefing + post-PASS progress-card relay).
"""

import pathlib

SKILL_PATH = pathlib.Path(__file__).parent.parent / "skills" / "writing-plans" / "SKILL.md"


def test_writing_plans_pointers_present():
    # @req: none (task-scoped wiring pin, not bound to a registered REQ-id)
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert skill_text.count("protocols/adjudication-view.md") >= 2, (
        "SKILL.md missing one or both pointers to adjudication-view.md"
    )
