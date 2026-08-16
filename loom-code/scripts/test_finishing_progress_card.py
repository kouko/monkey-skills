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
        "`loom-code/hooks/family-relay.md §(a2) Progress card`"
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


# --- Terminal-state gates arc: Step 8 Stage-flip duty + Stale-scan relay ---
# Two rows added to the close-out sub-checks table: the terminal flip
# (every intermediate stage had a flip duty; the terminal one was
# un-mandated — two merged arcs stranded mid-flight) and the loud
# stale-scan relay surfacing legacy strays at the next close-out.


def _single_row_line(marker: str) -> str:
    """The one physical table-row line containing `marker` — markdown
    table rows are single source lines, so a same-line match proves two
    phrases share a row-unit, not merely a file."""
    lines = [
        line
        for line in SKILL_MD.read_text(encoding="utf-8").splitlines()
        if marker in line
    ]
    assert len(lines) == 1, (
        f"expected exactly one table-row line containing {marker!r}, "
        f"got {len(lines)}"
    )
    return lines[0]


def test_stage_flip_row_binds_set_stage_finishing_with_plugin_fallback():
    """The Stage-flip duty row names the exact terminal-flip command AND
    the plugin-shipped fallback in the SAME row-unit — the two-tier
    resolution idiom the table's other rows use."""
    row = _single_row_line("Stage-flip duty")
    assert '--set-stage "finishing"' in row
    assert '"${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py"' in row
    assert "a load-time substitution, not a run-time shell variable" in row


def test_stage_flip_row_runs_before_commit_and_stages_the_flip():
    """The flip runs BEFORE the close-out commit and the flipped plan
    file is staged into THAT commit — never a follow-up chore."""
    row = _single_row_line("Stage-flip duty")
    assert "BEFORE the close-out commit" in row
    assert "THIS close-out commit" in row


def test_stage_flip_row_na_defers_to_entry_card_skip_rules():
    """No plan, or a statusless old-format plan → silent skip, per the
    Step 1 entry-card rules — the N/A column states it."""
    row = _single_row_line("Stage-flip duty")
    assert "skip silently" in row


def test_stale_scan_row_binds_verb_with_plugin_fallback():
    """The Stale-scan relay row names the scan verb over the plans dir
    AND the plugin-shipped fallback in the SAME row-unit."""
    row = _single_row_line("Stale-scan relay")
    assert "--stale-scan docs/loom/plans" in row
    assert '"${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py"' in row


def test_stale_scan_row_relays_stdout_verbatim_and_loudly():
    """The scan's stdout is relayed VERBATIM and loudly — never
    summarized away, never silently swallowed."""
    row = _single_row_line("Stale-scan relay")
    assert "VERBATIM" in row
    assert "loudly" in row


def test_stale_scan_row_advisory_pass_through_wording():
    """The advisory rationale is written into the row itself so a cold
    reader doesn't harden the scan into a block: all-done at
    review:round-N is a legitimate transient state of a live parallel
    arc — merged-arc candidates get fixed on the spot, live-arc
    candidates are named and passed through."""
    row = _single_row_line("Stale-scan relay")
    assert "legitimate transient state" in row
    assert "never harden" in row
