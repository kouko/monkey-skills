"""Structural grep-test guarding the spec→code seam wiring in writing-plans.

writing-plans/SKILL.md is a prompt artifact, not executable code. Its
correctness is the PRESENCE of a SECOND input contract: a validated loom-spec
change-folder (`docs/loom/<change-id>/`, `validate_spec_output.py`-clean) may be
consumed instead of a brainstorming brief. The section must state how a
`#### Scenario:` (GIVEN/WHEN/THEN) maps to one task's `Acceptance: RED/GREEN`,
must POINT (not copy) the source `### Requirement:` / `#### Scenario:` names via
the stable join key, must carve out the fact-vs-interpretation verbatim-copy
rule (THEN observable / magic values / signatures are facts → copied verbatim;
narrative + rationale are interpretation → linked), and must declare the
consumer read-only on the producer's change-folder (loom-spec stays SSOT).

These checks assert on the load-bearing PHRASES (intent), tolerant of wording
variation, so the test guards meaning without being brittle.

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "writing-plans" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def test_writing_plans_documents_changefolder_input():
    """The change-folder input contract must be present as a second input
    contract alongside the brief, with the scenario→RED/GREEN mapping,
    point-don't-copy / link-back, the fact-vs-interpretation verbatim carve-out,
    and the consumer read-only rule."""
    text = _text()
    low = text.lower()

    # 1. the section exists.
    assert "Consuming a loom-spec change-folder" in text, \
        "missing the 'Consuming a loom-spec change-folder' section heading"

    # 2. it is a SECOND input contract alongside the brief, taking a validated
    #    change-folder as the alternative input.
    assert "change-folder" in low, "must name the change-folder input"
    assert "validate_spec_output" in text, \
        "must name the validate_spec_output.py-clean precondition"

    # 3. the scenario → RED/GREEN mapping.
    assert "#### Scenario:" in text, \
        "must reference the producer's '#### Scenario:' marker"
    assert "RED" in text, "must map to an Acceptance RED"
    assert "GREEN" in text, "must map to an Acceptance GREEN"

    # 4. point-don't-copy / link back to the source names.
    assert "point-don't-copy" in low or "point-dont-copy" in low \
        or "link back" in low or "link-back" in low, \
        "must state the point-don't-copy / link-back rule"
    assert "### Requirement:" in text, \
        "must reference the source '### Requirement:' name to link back to"

    # 5. the fact-vs-interpretation verbatim-copy carve-out: the THEN observable
    #    / magic values / signatures are FACTS copied verbatim; narrative +
    #    rationale are interpretation, linked not copied.
    assert "verbatim" in low, \
        "must state the verbatim-copy carve-out for facts"
    assert "then" in low, "carve-out must name the THEN observable as a fact"

    # 6. consumer read-only on the change-folder (loom-spec stays SSOT).
    assert "read-only" in low or "read only" in low \
        or "must not modify" in low or "must not edit" in low, \
        "must declare the consumer read-only on the change-folder"
