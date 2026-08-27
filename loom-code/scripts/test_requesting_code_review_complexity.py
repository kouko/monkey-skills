"""Contract test for the branch-review implementation complexity lens."""

from pathlib import Path


ROOT = Path(__file__).parent.parent
SKILL = ROOT / "skills" / "requesting-code-review" / "SKILL.md"
EVIDENCE = ROOT / "skills" / "requesting-code-review" / "references" / "design-evidence.md"
REVIEWER = ROOT / "agents" / "code-reviewer.md"
LENS = ROOT / "skills" / "requesting-code-review" / "references" / "implementation-complexity-lens.md"


def test_deletion_first_compares_actual_and_planned_complexity():
    skill = SKILL.read_text(encoding="utf-8")
    evidence = EVIDENCE.read_text(encoding="utf-8")
    reviewer = REVIEWER.read_text(encoding="utf-8")
    lens = LENS.read_text(encoding="utf-8")
    flat_lens = " ".join(lens.split())

    assert "references/implementation-complexity-lens.md" in skill
    assert "Implementation complexity lens" in evidence
    assert "actual additions" in flat_lens and "planned complexity evidence" in flat_lens
    assert "landed deletions" in flat_lens and "simpler alternative" in flat_lens
    assert "downstream operational risk" in lens
    assert "independent local assessment" in lens
    assert "preserves the required outcome" in lens.lower()
    assert "scope trade-off" in lens.lower()
    assert "implementation complexity lens" in reviewer.lower()
