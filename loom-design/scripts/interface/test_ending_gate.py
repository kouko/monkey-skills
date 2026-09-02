"""Ending-gate card in interaction-flows: an imperative,
action-moment-anchored line stating that ending a run without the artifact
file on disk is a FAILED run (docs/loom/memory/
imperative-trigger-cards-beat-descriptive-preloads.md — imperative cards
flip weak-model behavior where buried procedure steps do not; incident:
2026-07-18 dogfood, a haiku run narrated its analysis and ended without
writing ui-flows.md, never reaching the validate step).

Neighborhood scoping per docs/loom/memory/
grep-tests-scope-to-measured-neighborhood.md: assertions anchor on the
card's own unique phrase and check its required co-phrases within the
card's line, not the whole file.

design-system's ending-gate card was removed for loom 1.0 (W2-03): the
station-shaped modality/ending-gate vocabulary does not carry over to the
new interview -> DESIGN.md -> ratify -> commit tool shape, so this file no
longer guards design-system/SKILL.md.
"""
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2] / "skills"
_FLOWS = _ROOT / "interaction-flows" / "SKILL.md"

_ANCHOR = "Ending gate"


def _card_line(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    assert _ANCHOR in text, f"{path} carries no ending-gate card"
    idx = text.index(_ANCHOR)
    line_start = text.rfind("\n", 0, idx) + 1
    # the card is one paragraph: ends at the first blank line after it
    para_end = text.find("\n\n", idx)
    return text[line_start:para_end if para_end != -1 else len(text)]


def test_flows_ending_gate_names_artifact_and_failed_run():
    card = _card_line(_FLOWS)
    assert "ui-flows.md" in card
    assert "exists on disk" in card
    assert "FAILED run" in card
    assert "before you end" in card.lower()


def test_cards_point_at_their_validate_steps():
    assert "validator" in _card_line(_FLOWS).lower()
