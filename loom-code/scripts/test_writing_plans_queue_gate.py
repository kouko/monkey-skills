"""RED/GREEN gate: writing-plans/SKILL.md must declare the queue-relation
intake gate as its own paragraph (not spliced into the on-ramp gate's
sentence), naming the script, binding each of its three exits to its
meaning in one clause, and stating the exit-2 stop/relay/wait/record duty.
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


def _gate_paragraph() -> str:
    text = SKILL_MD.read_text(encoding="utf-8")
    match = re.search(r"\*\*Queue-relation gate.*?(?=\n\n)", text, re.DOTALL)
    assert match, "Queue-relation gate paragraph not found in writing-plans/SKILL.md"
    return match.group(0)


def test_skill_md_declares_the_queue_gate():
    # No @req tag: this task's dispatch carries no registered REQ-ids.
    para = _gate_paragraph()

    assert "check_direction_freshness.py" in para

    # `resolv` alone also matches inside `unresolved`, so an exit-0 clause
    # saying the opposite would pass. Demonstrated live in review: editing
    # the paragraph to "Exit 0 means ... is unresolved." left this green.
    # Assert the positive word AND the absence of its negation.
    exit_0_clause = re.search(r"[Ee]xit 0[^.]*\.", para)
    assert exit_0_clause, "exit 0 not stated as its own clause"
    assert "resolves" in exit_0_clause.group(0), "exit 0 not bound to 'resolves' in one clause"
    assert "unresolved" not in exit_0_clause.group(0), "exit 0's clause says 'unresolved' — the meanings are swapped"
    assert re.search(r"[Ee]xit 1[^.]*unreadable", para), "exit 1 not bound to 'unreadable path' in one clause"
    assert re.search(r"[Ee]xit 2[^.]*unresolved", para), "exit 2 not bound to 'unresolved' in one clause"

    for duty_phrase in (
        "STOP",
        "do not draft",
        "relay the printed question",
        "wait",
        "write it into the brief",
        "re-run",
    ):
        assert duty_phrase in para, f"missing exit-2 duty phrase: {duty_phrase!r}"

    assert "prints on every run" in para
    assert "not a gate" in para or "not itself a gate" in para
