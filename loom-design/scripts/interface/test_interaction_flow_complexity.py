"""Contract tests for interaction-flows' stage-owned complexity lens."""

from pathlib import Path


ROOT = Path(__file__).parents[2]
SKILL = ROOT / "skills" / "interaction-flows" / "SKILL.md"
CHECKLIST = ROOT / "skills" / "interaction-flows" / "references" / "ux-flow-checklist.md"
LENS = ROOT / "skills" / "interaction-flows" / "references" / "interaction-complexity-lens.md"


def _complexity_handoff_paragraph(skill: str) -> str:
    """The paragraph governing `## Complexity handoff`'s status ("After the
    seven dimensions ... never a behavioral gate ..."), up to the next blank
    line -- narrower than the whole SKILL.md so this phrase's presence can't
    be satisfied by an incidental mention elsewhere in the file.
    """
    start = skill.find("After the seven dimensions")
    assert start != -1, (
        "SKILL.md must carry the 'After the seven dimensions' paragraph "
        "that governs `## Complexity handoff`'s status"
    )
    end = skill.find("\n\n", start)
    return skill[start : end if end != -1 else None]


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

    # Scope-boundary control phrase: the lens is evidence, never a gate.
    # Narrowed to the governing paragraph, not the whole file, so an
    # incidental mention elsewhere could not keep this green after the
    # boundary itself was deleted or inverted.
    assert "does not author behavioral guards" in _complexity_handoff_paragraph(skill)
