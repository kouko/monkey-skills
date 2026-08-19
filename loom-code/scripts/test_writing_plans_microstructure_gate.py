"""RED test for the writing-plans field-microstructure gate (Task 11,
docs/loom/plans/2026-08-19-field-value-microstructure.md).

Mirrors the pinning discipline of the open-questions-gate and
on-ramp-choice-gate tests: locate the paragraph by its bold lead-in,
require it sits in the same §Self-review gate list as the
open-questions gate, and pin both invocation modes plus the
blocking-on-non-zero-exit rule.
"""
from pathlib import Path

SKILL_MD = (
    Path(__file__).resolve().parents[1] / "skills" / "writing-plans" / "SKILL.md"
)

_OPEN_Q_GATE_LEAD = "**Open-questions gate"
_MICROSTRUCTURE_GATE_LEAD = "**Field-microstructure gate"


def _skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _paragraph(text: str, lead: str) -> str:
    start = text.index(lead)
    end = text.index("\n\n", start)
    return text[start:end]


def test_skill_md_declares_microstructure_gate():
    text = _skill_text()

    assert _MICROSTRUCTURE_GATE_LEAD in text, (
        "SKILL.md must carry a '**Field-microstructure gate' paragraph"
    )

    open_q_idx = text.index(_OPEN_Q_GATE_LEAD)
    microstructure_idx = text.index(_MICROSTRUCTURE_GATE_LEAD)
    assert microstructure_idx > open_q_idx, (
        "the Field-microstructure gate paragraph must sit after the "
        "Open-questions gate paragraph, in the same §Self-review gate list"
    )

    para = _paragraph(text, _MICROSTRUCTURE_GATE_LEAD)
    assert "python3 loom-code/scripts/check_field_microstructure.py" in para
    assert "<plan-path>" in para
    assert "--brief <brief-path>" in para
    # Verbatim spans, not bare keywords: "blocks" alone survives inside a
    # negated rewrite ("never blocks ...") — these two full clauses do not.
    assert "a non-zero exit blocks drafting" in para
    assert "a non-zero exit blocks the plan-document-reviewer dispatch" in para
    # Timing clause: brief mode fires at intake, before Task 1 is drafted —
    # not after. A rewrite claiming the opposite order must go RED.
    assert "brief mode fires at intake, before drafting Task 1" in para
    # Exit-code routing: pin number and meaning TOGETHER as one clause each,
    # so swapping which number gets which meaning (Exit 1 <-> Exit 2 content)
    # breaks both assertions, not just the paragraph's mere presence.
    assert "Exit 1: fix the flagged field or paragraph, re-run." in para
    assert (
        "Exit 2: structurally empty (no `## Task` headings, or no `## ` "
        "sections) — supply the missing structure, not a field fix."
    ) in para
