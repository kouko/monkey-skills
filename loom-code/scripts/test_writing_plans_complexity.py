"""Contract test for writing-plans' architecture complexity assessment."""

from pathlib import Path


ROOT = Path(__file__).parent.parent
SKILL = ROOT / "skills" / "writing-plans" / "SKILL.md"
FORMAT = ROOT / "skills" / "writing-plans" / "references" / "plan-format.md"
REVIEWER = ROOT / "skills" / "writing-plans" / "references" / "plan-document-reviewer-prompt.md"
LENS = ROOT / "skills" / "writing-plans" / "references" / "architecture-complexity-lens.md"


def test_non_mechanical_plan_carries_architecture_complexity():
    """Non-mechanical plans record local architecture burden before SDD."""
    skill = SKILL.read_text(encoding="utf-8")
    plan_format = FORMAT.read_text(encoding="utf-8")
    reviewer = REVIEWER.read_text(encoding="utf-8")
    lens = LENS.read_text(encoding="utf-8")
    flat_lens = " ".join(lens.split())
    low_lens = lens.lower()
    low_flat_lens = flat_lens.lower()

    assert "references/architecture-complexity-lens.md" in skill
    assert "Complexity assessment" in plan_format
    assert "boundaries, dependencies, migrations, configuration" in flat_lens
    assert "operational duties, reuse, and deletion" in flat_lens
    assert "added complexity" in low_lens
    assert "why it is worthwhile" in low_lens
    assert "removed or avoided complexity" in low_lens
    assert "downstream risk" in low_lens
    assert "mechanical edit" in low_lens and "reasoned exemption" in low_lens
    assert "upstream evidence is absent" in low_flat_lens
    assert "required end state" in low_flat_lens
    assert "Complexity assessment" in reviewer
    assert "checks_passed: <N>/<19>" in reviewer
