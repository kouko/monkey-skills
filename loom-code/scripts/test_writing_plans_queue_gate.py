"""RED/GREEN gate: writing-plans/SKILL.md must declare the queue-relation
intake gate as its own paragraph (not spliced into the on-ramp gate's
sentence), naming the shipped `check_queue_relation.py` script, binding
each of its three exits to its actual meaning in one clause, and stating
the exit-2 stop/relay/wait/record duty. It must not name the deleted
predecessor script (renamed away in ab36dc47) or the deleted per-run
advisory.
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


def test_gate_paragraph_names_queue_relation_script():
    # No @req tag: this task's dispatch carries no registered REQ-ids.
    para = _gate_paragraph()

    assert "check_queue_relation.py" in para
    # Composed to dodge the arc sweep pattern's own token match on the
    # deleted predecessor script's name (this is a negative assertion,
    # not a live reference).
    deleted_script_name = "check_direc" + "tion_freshness.py"
    assert deleted_script_name not in para

    # `resolv` alone also matches inside `unresolved`, so an exit-0 clause
    # saying the opposite would pass. Assert the positive word AND the
    # absence of its negation in the same clause.
    exit_0_clause = re.search(r"[Ee]xit 0[^.]*\.", para)
    assert exit_0_clause, "exit 0 not stated as its own clause"
    assert "resolves" in exit_0_clause.group(0), "exit 0 not bound to 'resolves' in one clause"
    assert "unresolved" not in exit_0_clause.group(0), "exit 0's clause says 'unresolved' — the meanings are swapped"
    # No-queue-layer posture: exit 0 also covers the loud N/A report.
    assert "N/A" in exit_0_clause.group(0), "exit 0 clause omits the no-queue-layer N/A posture"

    exit_1_clause = re.search(r"[Ee]xit 1[^.]*\.", para)
    assert exit_1_clause, "exit 1 not stated as its own clause"
    assert "unreadable" in exit_1_clause.group(0), "exit 1 not bound to 'unreadable path' in one clause"
    # Exit 1 now has two real causes (unreadable brief path, or a store
    # entry's status outside the closed vocabulary) — the paragraph must
    # not claim it means only one thing.
    assert "vocabulary" in exit_1_clause.group(0), "exit 1 clause omits the second cause (status outside the closed vocabulary)"

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

    # The deleted advisory (and its "prints on every run" sentence) must
    # not survive the rewrite.
    assert "prints on every run" not in para
    assert "unlanded-direction-change advisory" not in para
