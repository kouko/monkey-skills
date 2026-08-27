"""Structural contract for the business-owned complexity checkpoint."""

from pathlib import Path


SKILL_DIR = Path(__file__).parents[2] / "skills" / "business-value"
SKILL = SKILL_DIR / "SKILL.md"
TEMPLATE = SKILL_DIR / "assets" / "business-value-template.md"
LENS = SKILL_DIR / "references" / "business-complexity-lens.md"


def test_business_checkpoint_records_commitment_complexity():
    # Why: a worth-it decision must leave the durable business burden explicit
    # without replacing its existing value axes or verdict.
    skill = SKILL.read_text(encoding="utf-8").lower()
    template = TEMPLATE.read_text(encoding="utf-8").lower()

    assert LENS.is_file(), "business-value must own a local complexity lens"
    assert "references/business-complexity-lens.md" in skill
    for axis in ("why now", "why me", "opportunity cost"):
        assert axis in template, f"complexity must preserve the {axis} axis"
    assert "business complexity" in template
    for meaning in ("burden", "worth", "avoid", "downstream risk"):
        assert meaning in template, f"template must record {meaning}"
    assert "reasoned n/a" in template
