"""Contract for design-system's stage-owned visual complexity lens."""

from pathlib import Path


ROOT = Path(__file__).parents[2]
SKILL = ROOT / "skills" / "design-system" / "SKILL.md"
SCHEMA = ROOT / "skills" / "design-system" / "references" / "design-md-schema.md"
LENS = ROOT / "skills" / "design-system" / "references" / "visual-complexity-lens.md"
CANONICAL_HEADINGS = (
    "Overview / Brand",
    "Colors",
    "Typography",
    "Layout",
    "Elevation & Depth",
    "Shapes",
    "Components",
    "Do's & Don'ts",
)


def _section(text: str, heading: str, next_heading: str) -> str:
    start = text.index(heading)
    end = text.index(next_heading, start)
    return text[start:end]


def _canonical_headings(schema: str) -> tuple[str, ...]:
    artifact = _section(schema, "## Overview / Brand", "## Generation checklist")
    return tuple(line.removeprefix("## ") for line in artifact.splitlines() if line.startswith("## "))


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
        "intended visual outcome",
    ):
        assert concern in lens

    overview = _section(schema, "## Overview / Brand", "## Colors").lower()
    guardrails = _section(schema, "## Do's & Don'ts", "## Generation checklist").lower()
    assert "visual complexity" in overview
    assert "visual complexity" in guardrails

    assert _canonical_headings(schema) == CANONICAL_HEADINGS
    assert _canonical_headings(
        schema.replace("## Generation checklist", "## Ninth artifact section\n\n## Generation checklist", 1)
    ) != CANONICAL_HEADINGS
