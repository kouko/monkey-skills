"""Pins for copywriting-voice-quadrant-stage's Gate passage: contract-class
semantics applied to declared-voice-target (quadrant) mismatches, with
positioning nuance carried as craft (recorded, never gates).

Window discipline (docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md):
presence assertions are scoped to the `## Gate` section extracted by its
unique heading anchor — never whole-file — so generic terms elsewhere
cannot false-green a pin. The whole-file assertion is the ABSENCE pin
(retired "2+ 🟡 → NEEDS_REVISION" accumulation rule must not survive
anywhere in this file).

No registered REQ-ids in this dispatch — @req tags intentionally omitted.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = ROOT / "skills" / "copywriting-voice-quadrant-stage" / "SKILL.md"

GATE_HEADING = "## Gate (SHOULD — downstream)"


def _skill() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _gate_window() -> str:
    """The Gate section: from its unique heading to the next H2 heading."""
    text = _skill()
    start = text.find(GATE_HEADING)
    assert start != -1, f"heading {GATE_HEADING!r} absent from SKILL.md"
    nxt = text.find("\n## ", start + len(GATE_HEADING))
    return text[start:nxt] if nxt != -1 else text[start:]


def test_declared_voice_target_mismatch_is_contract_class():
    # WHY: a quadrant mismatch against the declared voice_quadrant target is
    # an objective, checkable referent (the field Phase 5 itself emits) —
    # per the vocabulary's contract definition, this must gate.
    window = _gate_window()
    assert re.search(
        r"declared[- ]voice[- ]target[^\n]*mismatch[^\n]*`contract`"
        r"|quadrant mismatch[^\n]*`contract`",
        window,
    ), "declared-voice-target (quadrant) mismatch not tagged `contract` in the Gate passage"


def test_positioning_nuance_is_craft_recorded_never_gates():
    # WHY: positioning nuance (edge polish, register feel) is qualitative —
    # it must be recorded but must never flip a verdict, per the vocabulary.
    window = _gate_window()
    assert re.search(r"positioning nuance[^\n]*`craft`", window), (
        "positioning nuance not tagged `craft` in the Gate passage"
    )
    assert re.search(r"recorded[^\n]*never gates|never gates[^\n]*recorded", window), (
        "craft-class positioning nuance must be marked recorded-never-gates"
    )


def test_gate_passage_points_at_claude_md_vocabulary_no_restatement():
    # WHY: the Gate passage must POINT at the canonical vocabulary section,
    # not restate its definitions locally (CLAUDE.md § Gate Convergence
    # Vocabulary is the one place `objective checkable referent` etc. live).
    window = _gate_window()
    assert re.search(r"CLAUDE\.md.*Gate Convergence Vocabulary", window), (
        "Gate passage missing a pointer to CLAUDE.md's canonical vocabulary section"
    )
    # no local restatement of the canonical definition prose
    # (case-insensitive — a capitalization-only rephrasing must not
    # false-pass; same fix class as commit 7f13682c)
    assert "objective checkable referent" not in window.lower()
    assert "qualitative observation" not in window.lower()


def test_old_yellow_accumulation_rule_absent():
    # WHY: absence pin (whole-file on purpose) — the retired count-based
    # "2+ 🟡 → NEEDS_REVISION" rule must not survive anywhere in this file.
    text = _skill()
    assert not re.search(r"2\+\s*🟡", text), "retired 2+ 🟡 accumulation rule present"
    assert not re.search(r"two or more 🟡", text)
