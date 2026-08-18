"""RED test for the writing-plans on-ramp choice gate (Task 9,
docs/loom/plans/2026-08-18-onramp-explicit-choice-gate.md).

Mirrors the pinning discipline of `test_wp_extraction_pointers.py`'s
open-questions-gate test: locate the paragraph by its bold lead-in,
require it sits after the Open-questions gate paragraph, and pin the
exact checker invocation + STOP wording.
"""
import re
from pathlib import Path

SKILL_MD = (
    Path(__file__).resolve().parents[1] / "skills" / "writing-plans" / "SKILL.md"
)

_OPEN_Q_GATE_LEAD = "**Open-questions gate"
_ONRAMP_GATE_LEAD = "**On-ramp choice gate"


def _skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _paragraph(text: str, lead: str) -> str:
    start = text.index(lead)
    end = text.index("\n\n", start)
    return text[start:end]


def test_intake_runs_onramp_choice_gate_before_drafting():
    text = _skill_text()

    assert _ONRAMP_GATE_LEAD in text, (
        "SKILL.md must carry a '**On-ramp choice gate' paragraph"
    )

    open_q_idx = text.index(_OPEN_Q_GATE_LEAD)
    onramp_idx = text.index(_ONRAMP_GATE_LEAD)
    assert onramp_idx > open_q_idx, (
        "the On-ramp choice gate paragraph must be positioned after the "
        "Open-questions gate paragraph"
    )

    para = _paragraph(text, _ONRAMP_GATE_LEAD)
    assert "python3 loom-code/scripts/check_onramp_choice.py" in para
    assert "STOP" in para
