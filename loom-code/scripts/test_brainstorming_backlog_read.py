"""Prose-pin test for the brainstorming Axis 0 backlog-read moment.

Pins the `**Backlog ready check**` paragraph (pinned text N1) inserted
into brainstorming/SKILL.md §Axis 0, directly after the paragraph
beginning `**Negative guard (silent skip)**`: the ready-query command,
the N/A-silent clause, and the never-hijacks sentence.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_MD = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "brainstorming"
    / "SKILL.md"
)

LEAD_PHRASE = "**Backlog ready check**"
READY_COMMAND = "python3 scripts/backlog_index.py --ready"
# Cascade wording (ship-progress-tooling Task 2): the script now also
# ships in the loom-code plugin, so the silent skip fires only when
# NEITHER the repo-root copy nor the plugin-shipped copy resolves.
NA_SILENT_CLAUSE = "no store, or neither copy of `backlog_index.py` → skip silently, N/A"
NEVER_HIJACKS = "it never hijacks it"
INDEPENDENT_OF_NEGATIVE_GUARD = "independent of the Negative guard"

NEGATIVE_GUARD_PHRASE = "**Negative guard (silent skip)**"


def _normalized_text() -> str:
    """Whitespace-normalized SKILL.md text (collapses hard wraps so a
    contiguous-phrase match doesn't depend on line breaks)."""
    text = SKILL_MD.read_text(encoding="utf-8")
    return " ".join(text.split())


def test_negative_guard_paragraph_present():
    """Positive-fact control: the pre-existing Axis 0 negative-guard
    paragraph is present — proves the pins below are not vacuous
    (i.e. the file is actually being read/matched, not a stub)."""
    assert NEGATIVE_GUARD_PHRASE in _normalized_text()


def test_backlog_ready_check_lead_phrase_present():
    """N1's lead phrase exists in the file."""
    assert LEAD_PHRASE in _normalized_text()


def test_backlog_ready_check_follows_negative_guard():
    """N1 is inserted after the negative-guard paragraph, per the
    plan's placement anchor."""
    normalized = _normalized_text()
    guard_idx = normalized.find(NEGATIVE_GUARD_PHRASE)
    lead_idx = normalized.find(LEAD_PHRASE)
    assert guard_idx != -1
    assert lead_idx != -1
    assert guard_idx < lead_idx


def test_ready_command_string_present():
    """The exact ready-query command string is pinned."""
    assert READY_COMMAND in _normalized_text()


def test_na_silent_clause_present():
    """The no-store case skips silently as N/A — pinned verbatim."""
    assert NA_SILENT_CLAUSE in _normalized_text()


def test_never_hijacks_sentence_present():
    """The queue informs the arc decision but never hijacks it —
    the user's seed idea stays the default subject."""
    assert NEVER_HIJACKS in _normalized_text()


def test_independent_of_negative_guard_sentence_present():
    """Fix round 1: the ready check is independent of the Negative
    guard above it — a bug-fix/refactor arc that skips the rest of
    Axis 0 still runs the ready check."""
    assert INDEPENDENT_OF_NEGATIVE_GUARD in _normalized_text()


def test_negative_guard_paragraph_announces_ready_check_runs_regardless():
    """Fix round 2: the guard paragraph itself (not just the later
    ready-check paragraph) must announce the exception it carves out —
    a reader stopping at the guard's own skip sentence must see that
    the Backlog ready check runs regardless of this skip. Scoped to the
    guard paragraph itself (bounded by its own closing sentence, not by
    LEAD_PHRASE's first occurrence — the exception sentence itself now
    mentions the Backlog ready check by name, so LEAD_PHRASE can occur
    inside the guard paragraph too), so a "runs regardless" phrase
    living elsewhere in the file cannot pass this test vacuously."""
    normalized = _normalized_text()
    guard_idx = normalized.find(NEGATIVE_GUARD_PHRASE)
    guard_end_marker = "multi-state new work."
    guard_end_idx = normalized.find(guard_end_marker, guard_idx)
    assert guard_idx != -1
    assert guard_end_idx != -1
    guard_paragraph = normalized[guard_idx : guard_end_idx + len(guard_end_marker)]
    assert "runs regardless" in guard_paragraph, guard_paragraph


BLOCK_END_MARKER = "exactly bug-fix shaped)."


# --- loom-init offer branch (loom-init scaffold, Task 2) ---
#
# Third state of the ready check: no docs/loom/backlog/ store → offer
# scaffolding it via loom_init.py ONCE, then proceed either way. Lives
# in its OWN paragraph directly after the ready-check paragraph — the
# pinned sentences above (NA_SILENT_CLAUSE et al.) survive byte-intact.

LOOM_INIT_OFFER_LEAD = "**No queue layer yet**"
# T2 review 🟡 (2026-08-10): the repo-root first tier was dead in ALL
# repos — a bootstrap verb's precondition is the repo lacking the layer,
# so no repo-root copy can exist. Single plugin-shipped command only;
# the pin below asserts the dead tier's ABSENCE so it cannot creep back.
LOOM_INIT_PLUGIN_COMMAND = 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/loom_init.py"'
LOOM_INIT_DEAD_TIER = "Repo-root `scripts/loom_init.py` when"
LOOM_INIT_LOAD_TIME_NOTE = "load-time substitution"
LOOM_INIT_PARA_END = "no offer to make."
ON_RAMP_PARA_LEAD = "If a criteria row triggers"


def _loom_init_paragraph() -> str:
    """The offer paragraph, bounded by its own lead phrase and closing
    sentence, so presence assertions below cannot pass vacuously off
    phrases living elsewhere in the file (e.g. the on-ramp paragraph
    also says "Design-side on-ramp")."""
    normalized = _normalized_text()
    lead_idx = normalized.find(LOOM_INIT_OFFER_LEAD)
    assert lead_idx != -1, "loom-init offer paragraph lead missing"
    end_idx = normalized.find(LOOM_INIT_PARA_END, lead_idx)
    assert end_idx != -1, "loom-init offer paragraph closing sentence missing"
    return normalized[lead_idx : end_idx + len(LOOM_INIT_PARA_END)]


def test_loom_init_offer_paragraph_present():
    """The ready-check section gains the third state: an offer paragraph
    with its own lead phrase."""
    assert LOOM_INIT_OFFER_LEAD in _normalized_text()


def test_loom_init_offer_command_with_plugin_fallback_same_paragraph():
    """The offer names the SINGLE plugin-shipped command in the
    paragraph-unit with the load-time-substitution note; the dead
    repo-root tier (T2 review 🟡 — structurally unreachable for a
    bootstrap verb) must stay absent."""
    para = _loom_init_paragraph()
    assert LOOM_INIT_PLUGIN_COMMAND in para, para
    assert LOOM_INIT_LOAD_TIME_NOTE in para, para
    assert LOOM_INIT_DEAD_TIER not in para, (
        "the dead repo-root tier crept back into the offer:\n" + para
    )


def test_loom_init_offer_recommend_once_and_records_choice():
    """Decline / no engagement → proceed silently, choice recorded in
    the brief's Design-side on-ramp line, never re-raised — the same
    recommend-once rule as the Axis 0 on-ramp recommendation."""
    para = _loom_init_paragraph()
    assert "ONCE" in para, para
    assert "Design-side on-ramp" in para, para
    assert "never re-raise" in para, para


def test_loom_init_offer_sits_between_ready_check_block_and_on_ramp():
    """Placement: the offer paragraph follows the ready-check paragraph
    (after its closing sentence) and precedes the on-ramp criteria
    paragraph — inside the ready-check section, not elsewhere."""
    normalized = _normalized_text()
    block_end_idx = normalized.find(BLOCK_END_MARKER)
    lead_idx = normalized.find(LOOM_INIT_OFFER_LEAD)
    on_ramp_idx = normalized.find(ON_RAMP_PARA_LEAD)
    assert block_end_idx != -1
    assert lead_idx != -1
    assert on_ramp_idx != -1
    assert block_end_idx < lead_idx < on_ramp_idx


def test_loom_init_offer_keeps_na_state_for_missing_script_copies():
    """Third state ≠ second state: when neither copy of
    `backlog_index.py` resolves, the ready check stays N/A as today —
    the offer paragraph itself must carve that out."""
    para = _loom_init_paragraph()
    assert "neither copy" in para, para
