"""Contract test for spec-expansion's behavioral complexity lens."""

from pathlib import Path


ROOT = Path(__file__).parents[2]
SKILL = ROOT / "skills" / "spec-expansion" / "SKILL.md"
DETAILS = ROOT / "skills" / "spec-expansion" / "references" / "execution-details.md"
LENS = ROOT / "skills" / "spec-expansion" / "references" / "behavioral-complexity-lens.md"


def test_pruning_reports_retained_behavioral_complexity():
    """Pruning records local behavioral burden without adding an artifact schema."""
    skill = SKILL.read_text(encoding="utf-8")
    details = DETAILS.read_text(encoding="utf-8")
    lens = LENS.read_text(encoding="utf-8")
    flat_lens = " ".join(lens.split())

    assert "references/behavioral-complexity-lens.md" in skill
    assert "Behavioral complexity lens" in details
    assert "objects, roles, states, paths, NFRs, and obligations" in lens
    assert "KEEP" in lens and "FLAG" in lens and "DROP" in lens
    assert "retained and justified" in flat_lens
    assert "redundant, impossible, or speculative" in flat_lens
    assert "deletions" in lens and "downstream risks" in lens
    assert "No upstream complexity note is required" in lens
    assert "eighth proposal section" in lens
    assert "required user or system outcome" in lens.lower()
