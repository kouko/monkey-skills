"""RED/GREEN gate: writing-plans/SKILL.md must declare the
proposal-status intake gate (R2) as its own paragraph, naming the
shipped `check_proposal_status.py` script and binding its exit codes to
their actual meaning, alongside the on-ramp/queue-relation intake gates.
"""

import pathlib
import re

SKILL_MD = (
    pathlib.Path(__file__).resolve().parents[2]
    / "loom-code"
    / "skills"
    / "writing-plans"
    / "SKILL.md"
)

_ONRAMP_GATE_LEAD = "**On-ramp choice gate"
_QUEUE_GATE_LEAD = "**Queue-relation gate"
_PROPOSAL_GATE_LEAD = "**Proposal-status intake gate"


def _skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _gate_paragraph(text: str) -> str:
    match = re.search(
        r"\*\*Proposal-status intake gate.*?(?=\n\n)", text, re.DOTALL
    )
    assert match, (
        "Proposal-status intake gate paragraph not found in "
        "writing-plans/SKILL.md"
    )
    return match.group(0)


def test_proposal_status_gate_named_alongside_onramp_and_queue_gates():
    text = _skill_text()

    assert _ONRAMP_GATE_LEAD in text
    assert _QUEUE_GATE_LEAD in text
    assert _PROPOSAL_GATE_LEAD in text, (
        "SKILL.md must carry a '**Proposal-status intake gate' paragraph "
        "alongside the on-ramp/queue-relation intake gates"
    )

    onramp_idx = text.index(_ONRAMP_GATE_LEAD)
    proposal_idx = text.index(_PROPOSAL_GATE_LEAD)
    assert proposal_idx > onramp_idx, (
        "the Proposal-status intake gate paragraph must be positioned "
        "after the On-ramp choice gate paragraph"
    )


def test_proposal_status_gate_paragraph_names_script_and_exit_codes():
    para = _gate_paragraph(_skill_text())

    assert "python3 loom-code/scripts/check_proposal_status.py" in para
    assert "STOP" in para

    exit_0_clause = re.search(r"[Ee]xit 0[^.]*\.", para)
    assert exit_0_clause is None or "ratified" in exit_0_clause.group(0)

    exit_2_clause = re.search(r"[Ee]xit 2[^.]*\.", para)
    assert exit_2_clause, "exit 2 not stated as its own clause"
    assert "ratified" in exit_2_clause.group(0) or "not" in exit_2_clause.group(0)

    exit_1_clause = re.search(r"[Ee]xit 1[^.]*\.", para)
    assert exit_1_clause, "exit 1 not stated as its own clause"
