"""Contract for design-system's stage-owned visual complexity lens."""

from pathlib import Path


ROOT = Path(__file__).parents[2]
SKILL = ROOT / "skills" / "design-system" / "SKILL.md"
SCHEMA = ROOT / "skills" / "design-system" / "references" / "design-md-schema.md"
LENS = ROOT / "skills" / "design-system" / "references" / "visual-complexity-lens.md"


def _section(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start)
    return text[start:end]


def test_visual_lens_preserves_canonical_eight_sections():
    """Visual burden stays in DESIGN.md's existing prose slots, not a ninth section."""
    assert LENS.is_file(), "design-system needs its own visual-complexity lens"

    skill = SKILL.read_text(encoding="utf-8")
    schema = SCHEMA.read_text(encoding="utf-8")
    lens = LENS.read_text(encoding="utf-8").lower()

    assert "references/visual-complexity-lens.md" in skill
    for concern in (
        "new vocabulary",
        "justified variants",
        "deleted or avoided exceptions",
        "downstream component risk",
        "reasoned n/a",
    ):
        assert concern in lens

    overview = _section(schema, "## Overview / Brand", "## Colors").lower()
    guardrails = _section(schema, "## Do's & Don'ts", "## Generation checklist").lower()
    assert "visual complexity" in overview
    assert "visual complexity" in guardrails

    canonical = schema.split("## The 8 canonical sections (in order)", 1)[1].split(
        "## Overview / Brand", 1
    )[0]
    assert canonical.count("## ") == 0
    assert "eight `##` sections" in canonical
