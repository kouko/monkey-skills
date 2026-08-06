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
