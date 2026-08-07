"""Prose-pin test for the finishing Step 8 backlog-close check.

Pins the Backlog-close check row in finishing-a-development-branch/
SKILL.md Step 8's close-out sub-checks table (flip a shipped or
superseded backlog entry's status in the same close-out commit,
regenerate the index, silent skip without a hit or a store) and the
Step 13 queue-tail report line ("backlog next: <name>"). Added by the
backlog ready-verb-and-close-loop arc: 90 entries filed, zero ever
closed, because no flow ever read or closed the store. The five Step 8
ONCE-per-branch bullets collapsed into one table in loom arc 4b; these
pins now land in that table's cells.
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


def test_backlog_close_follows_memory_store_integrity_row():
    """The row sits in Step 8's close-out sub-checks table directly
    after the Memory-store integrity row (whose Action cell ends on
    'the same miss shipped twice') and before the Attached-HEAD
    check."""
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


def test_backlog_close_script_absent_na_string_present():
    """Fix round 2: the script-existence check now gates only the
    index regeneration, not the whole close-out (fix 2's condition
    split) — the N/A phrasing changed accordingly from a whole-bullet
    N/A to a scoped 'index not regenerated' statement."""
    assert (
        "backlog-close: index not regenerated — "
        "backlog_index.py not present" in _normalized_text()
    )


def test_step13_skip_clause_names_the_script_path():
    """Fix round 2 (fix 5a, path-consistency ride-along): Step 13's
    own skip clause names the script by its repo-root-relative path,
    matching the Backlog-close bullet's own `scripts/backlog_index.py`
    references rather than the bare module name."""
    assert (
        "no backlog store or no `scripts/backlog_index.py`"
        in _normalized_text()
    )


def test_step13_queue_empty_alternative_phrase_present():
    """Step 13's report line has two renderings depending on queue
    state: 'backlog next: <name>' when non-empty, or this literal
    string when the COMMITTED-NEXT queue has nothing in it."""
    assert '"COMMITTED-NEXT queue empty"' in _normalized_text()
