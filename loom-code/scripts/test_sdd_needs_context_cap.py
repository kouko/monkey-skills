"""RED-first test for Task 6 (2026-07-18 loop-convergence-fixes plan).

subagent-driven-development/SKILL.md currently caps NEEDS_REVISION
re-dispatches at 3 rounds (§Verdict resolution) but says nothing about
a cap on NEEDS_CONTEXT re-dispatches for the same task — this test
asserts SKILL.md documents:

  (a) a 2-round cap on NEEDS_CONTEXT re-dispatches per task, with a 3rd
      NEEDS_CONTEXT meaning the spec/plan is missing information and
      the orchestrator must stop and surface to the user (mirroring the
      existing 3-round NEEDS_REVISION escalation wording).
  (b) in the 3-round-cap section, one cross-reference sentence noting
      that continuous mode deliberately halts one round earlier,
      pointing at references/continuous-mode.md.

Source: docs/loom/plans/2026-07-18-loop-convergence-fixes.md Task 6.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SDD_SKILL = REPO_ROOT / "loom-code/skills/subagent-driven-development/SKILL.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_needs_context_has_2_round_cap_and_3rd_round_escalation():
    """
    SKILL.md must document a 2-round cap on NEEDS_CONTEXT re-dispatches
    per task, and that a 3rd NEEDS_CONTEXT means the spec/plan is
    missing information — stop and surface to the user.
    """
    text = _read(SDD_SKILL)
    assert "NEEDS_CONTEXT" in text
    assert "2 rounds" in text or "capped at 2" in text
    assert "3rd" in text
    assert "spec/plan is missing information" in text


def test_3_round_cap_section_cross_references_continuous_mode():
    """
    The 3-round-cap section (§Verdict resolution area) must cross-
    reference continuous-mode.md, noting continuous mode halts one
    round earlier than SDD's cap.
    """
    text = _read(SDD_SKILL)
    assert "continuous-mode.md" in text
    assert "one round earlier" in text
