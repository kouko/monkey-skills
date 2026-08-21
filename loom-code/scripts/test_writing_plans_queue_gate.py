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
    # The three canonical forms don't all resolve the same way: `unqueued`
    # resolves with zero live bets (the only form any brief can use while
    # the store holds no `status: bet` entries), while `in-queue:`/
    # `displaces:` need a matching live bet entry. The clause must say so,
    # not claim a single condition for all three.
    assert "unconditionally" in exit_0_clause.group(0), "exit 0 clause doesn't distinguish unqueued's unconditional resolution from in-queue/displaces needing a live bet match"
    assert "in-queue" in exit_0_clause.group(0) and "displaces" in exit_0_clause.group(0), "exit 0 clause doesn't name the two forms that need a live bet match"

    exit_1_clause = re.search(r"[Ee]xit 1[^.]*\.", para)
    assert exit_1_clause, "exit 1 not stated as its own clause"
    # Exit 1 has FOUR causes. Two of them are new as of the round-3
    # whole-branch fix that guarded `main()`'s store and brief reads —
    # before it, this assertion read `"unreadable" not in ...` with the
    # comment "it never attempts to open an existing-but-unreadable
    # file", which was true then and false the moment the guards landed.
    # A pin that states a fact rather than a duty goes stale with the
    # code; both words are asserted PRESENT now, and the store-absent
    # distinction with them, because an unreadable store must never be
    # read as an absent one (absence exits 0).
    assert "not found" in exit_1_clause.group(0), "exit 1 not bound to 'not found' in one clause"
    assert "unreadable" in exit_1_clause.group(0), "exit 1 clause omits the unreadable-path causes the guards added"
    assert "NOT the store-absent case" in exit_1_clause.group(0), "exit 1 clause does not separate an unreadable store from an absent one (absent exits 0)"
    # The paragraph must not claim exit 1 means only one thing, and must
    # give each cause its own remedy so a reader can tell them apart.
    assert "vocabulary" in exit_1_clause.group(0), "exit 1 clause omits the second cause (status outside the closed vocabulary)"
    assert "fix the path" in exit_1_clause.group(0), "exit 1 clause omits the remedy for a missing brief path"
    assert "frontmatter" in exit_1_clause.group(0), "exit 1 clause omits the remedy for a bad-status backlog entry"

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
