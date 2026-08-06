"""Prose-pin test for the finishing entry progress card + gate-STOP clause.

Pins the N4a entry-card sentence appended to Default flow step 1 in
finishing-a-development-branch/SKILL.md (render the card once on entry
via plan_card.py, framed per family-relay §(a2); three-branch
degradation — statusless old-format plan skips silently, rejected
Status VALUES relay the parser's error line loudly, missing
script/family-relay renders the four fields inline) and the N4b
gate-STOP clause appended to the §ASK rationale
paragraph (every gate STOP surfaced to the user leads with the card).
Added by the progress-cards-and-plan-ledger arc.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_MD = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "finishing-a-development-branch"
    / "SKILL.md"
)


def _normalized_text() -> str:
    """Whitespace-normalized SKILL.md text (collapses hard wraps so a
    contiguous-phrase match doesn't depend on line breaks)."""
    text = SKILL_MD.read_text(encoding="utf-8")
    return " ".join(text.split())


def test_default_flow_control_phrase_present():
    """Positive-fact control: a pre-existing Default flow step 1 phrase
    is present — proves the assertions below run against the real file,
    not a stub."""
    assert (
        "Read branch state — git status + git log main..HEAD"
        in _normalized_text()
    )


def test_entry_card_lead_present():
    """N4a's lead phrase exists: the card renders once on entry when
    the branch has a plan carrying the progress headers."""
    assert (
        "When the branch has a plan carrying the progress headers, "
        "render the card once on entry" in _normalized_text()
    )


def test_entry_card_names_render_command():
    """N4a names the exact render command."""
    assert (
        "`python3 scripts/plan_card.py <plan-path>`" in _normalized_text()
    )


def test_entry_card_names_family_relay_a2_pointer():
    """N4a frames the card per the family-relay progress-card variant —
    the §(a2) pointer, not a copied template body."""
    assert (
        "`loom-pipeline/hooks/family-relay.md §(a2) Progress card`"
        in _normalized_text()
    )


def test_entry_card_inline_fallback_field_list_present():
    """Degradation rule: script or family-relay absent → the four
    fields render inline, nothing dropped."""
    assert (
        "render the four fields inline: goal, task table, stage, next"
        in _normalized_text()
    )


def test_gate_stop_clause_leads_with_card():
    """N4b: every gate STOP that surfaces to the user (NEEDS_REVISION,
    privacy BLOCK, probe FAIL) leads with the progress card — the user
    sees where the arc stopped before deciding."""
    assert (
        "Every gate STOP that surfaces to the user (a NEEDS_REVISION, "
        "a privacy BLOCK, a probe FAIL) leads with the progress card"
        in _normalized_text()
    )
def test_entry_card_rejected_status_branch_relays_loudly():
    """The middle degradation branch: rejected Status VALUES (the
    parser's "has status '…', outside" error shape) relay the error
    line loudly — never a silent skip. Keyed on the second error
    shape so it stays disjoint from the statusless old-format branch."""
    normalized = _normalized_text()
    assert "relay that error line loudly, never skip" in normalized
    assert "Status VALUES the parser rejects" in normalized
