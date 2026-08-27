"""Contract tests for interaction-flows' stage-owned complexity lens."""

from pathlib import Path


ROOT = Path(__file__).parents[2]
SKILL = ROOT / "skills" / "interaction-flows" / "SKILL.md"
CHECKLIST = ROOT / "skills" / "interaction-flows" / "references" / "ux-flow-checklist.md"
LENS = ROOT / "skills" / "interaction-flows" / "references" / "interaction-complexity-lens.md"


def test_flow_lens_emits_stage_native_handoff():
    """Flow complexity stays local, is addressable, and never becomes a spec gate."""
    skill = SKILL.read_text(encoding="utf-8")
    checklist = CHECKLIST.read_text(encoding="utf-8")
    lens = LENS.read_text(encoding="utf-8")

    assert "references/interaction-complexity-lens.md" in skill
    assert "seven dimensions" in skill.lower()
    assert "Complexity handoff" in checklist
    assert "added decisions, states, branches" in lens
    assert "why each survivor matters" in lens
    assert "collapsed or avoided paths" in lens
    assert "downstream ambiguity" in lens
    assert "static surface" in lens.lower() and "reasoned N/A" in lens
    assert "optional evidence" in lens
    assert "required user or operator outcome" in lens.lower()
    assert "does not author behavioral guards" in skill
