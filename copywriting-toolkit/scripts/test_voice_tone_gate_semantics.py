"""Pins for copywriting-voice-tone-stage's Voice Consistency SHOULD gate
verdict passage: contract-class semantics (declared tone-target violations
gate; tone nuance is craft, recorded only).

Window discipline (docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md):
presence assertions are scoped to the "## Gate — SHOULD (Voice Consistency)"
section by its unique heading anchor — never whole-file. The whole-file
assertion is the ABSENCE pin (retired "≤2 WARNINGS" / "≥3 WARNINGS" count-based
accumulation rule must not survive anywhere in this file).

No registered REQ-ids in this dispatch — @req tags intentionally omitted.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / "skills" / "copywriting-voice-tone-stage" / "SKILL.md"

GATE_HEADING = "## Gate — SHOULD (Voice Consistency)"


def _skill() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _gate_window() -> str:
    """The gate section: from its unique heading to the next H2."""
    text = _skill()
    start = text.find(GATE_HEADING)
    assert start != -1, f"heading {GATE_HEADING!r} absent from voice-tone SKILL.md"
    nxt = text.find("\n## ", start + len(GATE_HEADING))
    return text[start:nxt] if nxt != -1 else text[start:]


def test_gate_verdict_pointer_to_claude_md_vocabulary():
    # WHY: contract/craft semantics are canonical in CLAUDE.md; this gate
    # must point at it, not restate a local definition (single SSOT).
    window = _gate_window()
    assert "../../CLAUDE.md" in window and "Gate Convergence Vocabulary" in window, (
        "verdict handling must pointer-cite CLAUDE.md §Gate Convergence Vocabulary"
    )


def test_gate_verdict_contract_craft_split_present():
    # WHY: the task's rule — declared tone-target violations (against this
    # gate's stated target) are contract-class and gate; tone nuance is
    # craft and is recorded but never gates.
    window = _gate_window()
    assert re.search(r"declared tone[- ]target", window), (
        "declared tone-target contract definition missing from gate verdict handling"
    )
    assert "craft" in window and "never gate" in window, (
        "craft-class tone-nuance carve-out (recorded, never gates) missing"
    )


def test_old_warning_count_accumulation_rule_absent():
    # WHY: absence pin (whole-file on purpose) — the retired count-based
    # "≤2 WARNINGS" / "≥3 WARNINGS" accumulation rule must not survive
    # anywhere in this file.
    text = _skill()
    assert not re.search(r"≤\s*2\s*WARNINGS", text), "retired ≤2 WARNINGS rule present"
    assert not re.search(r"≥\s*3\s*WARNINGS", text), "retired ≥3 WARNINGS rule present"
