"""Prose-pin test for the finishing Step 8 backlog-close check.

Pins the backlog-close bullet in
finishing-a-development-branch/SKILL.md Step 8 (flip a shipped or
superseded backlog entry's status in the same close-out commit,
regenerate the index, silent skip without a hit or a store) and the
Step 13 queue-tail report line ("backlog next: <name>"). Added by the
backlog ready-verb-and-close-loop arc: 90 entries filed, zero ever
closed, because no flow ever read or closed the store.
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


def test_step8_hygiene_control_phrase_present():
    """Positive-fact control: a pre-existing Step 8 hygiene phrase is
    present — proves the assertions below run against the real file,
    not a stub."""
    assert "Run `git status --short` to confirm" in _normalized_text()


def test_backlog_close_bullet_lead_present():
    """The bullet's lead phrase exists in the file."""
    assert "Backlog-close check" in _normalized_text()


def test_backlog_close_flip_vocabulary_present():
    """The bullet names the exact status-flip vocabulary."""
    assert "SHIPPED (or CLOSED — SUPERSEDED)" in _normalized_text()


def test_backlog_close_same_commit_duty_present():
    """The flip and the index regen land in the same close-out
    commit — the close moment, not a follow-up chore."""
    assert "in the same close-out commit" in _normalized_text()


def test_backlog_close_names_regenerate_command():
    """The bullet names the exact index-regeneration command."""
    assert (
        "`python3 scripts/backlog_index.py --write`"
        in _normalized_text()
    )


def test_backlog_close_silent_skip_clause_present():
    """No hit, or no store, skips silently — auditable from the diff,
    same posture as the memory-store bullet."""
    assert "No hit, or no store → skip silently" in _normalized_text()


def test_backlog_close_follows_memory_store_integrity_bullet():
    """The bullet sits in Step 8's hygiene list directly after the
    Memory-store integrity bullet (which ends on 'the same miss
    shipped twice') and before the Attached-HEAD check."""
    normalized = _normalized_text()
    memory_end_idx = normalized.find("the same miss shipped twice")
    close_idx = normalized.find("Backlog-close check")
    head_idx = normalized.find("Attached-HEAD check:")
    assert memory_end_idx != -1
    assert close_idx != -1
    assert head_idx != -1
    assert memory_end_idx < close_idx < head_idx


def test_step13_queue_tail_phrase_present():
    """Step 13's report ends naming the top of the remaining
    COMMITTED-NEXT queue."""
    assert '"backlog next: <name>"' in _normalized_text()
