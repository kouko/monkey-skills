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
NA_SILENT_CLAUSE = "no store or no `scripts/backlog_index.py` → skip silently, N/A"
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


# --- Task 3: DIRECTION.md read, conditional on the file's presence ---

DIRECTION_CONDITIONAL_LEAD = "When the target repo has `docs/loom/DIRECTION.md`"
DIRECTION_INDEPENDENT_OF_STORE = "with or without a backlog store"
DIRECTION_NOW_NEXT_SECTIONS = "`## Now` and `## Next`"
DIRECTION_NO_FILE_SKIP = "no file → skip silently, same posture as the no-store case"
BLOCK_END_MARKER = "exactly bug-fix shaped)."


def test_direction_md_conditional_lead_present():
    """The new sentence's conditional opener is pinned verbatim — this
    is the phrase a cold reader must see to know the DIRECTION.md read
    is gated on the file's presence, not mandatory."""
    assert DIRECTION_CONDITIONAL_LEAD in _normalized_text()


def test_direction_md_independent_of_backlog_store_present():
    """Fix round 2: the DIRECTION.md read is independent of the
    backlog-store condition on the sentence before it — a repo with
    DIRECTION.md but no backlog store must still fire this read (spec
    §8's portability contract). The old conjunctive wording ("also
    has") made this read as gated on the block's earlier condition;
    this pin fails on that regression and only passes when the
    sentence states the independence explicitly."""
    assert DIRECTION_INDEPENDENT_OF_STORE in _normalized_text()


def test_direction_md_now_next_sections_present():
    """Both sections the ready check must surface when DIRECTION.md
    exists are named."""
    assert DIRECTION_NOW_NEXT_SECTIONS in _normalized_text()


def test_direction_md_no_file_skip_clause_present():
    """Absent-file posture matches the no-store case already pinned
    above (NA_SILENT_CLAUSE) — this is the DIRECTION.md-specific
    restatement of that same silent-skip rule."""
    assert DIRECTION_NO_FILE_SKIP in _normalized_text()


def test_direction_md_sentence_inside_backlog_ready_check_block():
    """The new sentence must land inside the Backlog ready check block
    (between its lead phrase and the block's closing sentence), not
    elsewhere in the file — the plan's placement requirement.

    Fix round 2: the negative-guard paragraph's own exception sentence
    now names "the **Backlog ready check**" too (forward reference), so
    LEAD_PHRASE's FIRST occurrence in the file sits inside that guard
    paragraph, not the block. Anchoring the window on the first
    occurrence would make this test pass even if the new sentence were
    moved wholly into the guard paragraph and deleted from the block
    (a real weakened-pin failure mode, confirmed via probe). Fix:
    start the LEAD_PHRASE search after the guard paragraph's own
    closing sentence, so the window can only anchor on the block's
    actual lead phrase."""
    normalized = _normalized_text()
    guard_end_marker = "multi-state new work."
    guard_end_idx = normalized.find(guard_end_marker)
    assert guard_end_idx != -1
    search_start = guard_end_idx + len(guard_end_marker)
    lead_idx = normalized.find(LEAD_PHRASE, search_start)
    block_end_idx = normalized.find(BLOCK_END_MARKER, lead_idx)
    assert lead_idx != -1
    assert block_end_idx != -1
    block = normalized[lead_idx : block_end_idx + len(BLOCK_END_MARKER)]
    assert DIRECTION_CONDITIONAL_LEAD in block, block
