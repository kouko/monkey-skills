"""Prose-pin test for the finishing Step 8 backlog-close check.

Pins the Backlog-close check row in finishing-a-development-branch/
SKILL.md Step 8's close-out sub-checks table (flip a shipped or
superseded backlog entry's status in the same close-out commit,
regenerate the index, silent skip without a hit or a store) and the
Step 13 queue-tail report line ("next bet: <name>"). Added by the
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
BACKLOG_CHARTER = REPO_ROOT / "docs" / "loom" / "backlog" / "README.md"


def _normalized_text() -> str:
    """Whitespace-normalized SKILL.md text (collapses hard wraps so a
    contiguous-phrase match doesn't depend on line breaks)."""
    text = SKILL_MD.read_text(encoding="utf-8")
    return " ".join(text.split())


def _normalized_charter_text() -> str:
    """Whitespace-normalized backlog charter text."""
    return " ".join(BACKLOG_CHARTER.read_text(encoding="utf-8").split())


def test_step8_hygiene_control_phrase_present():
    """Positive-fact control: a pre-existing Step 8 hygiene phrase is
    present — proves the assertions below run against the real file,
    not a stub."""
    assert "Run `git status --short` to confirm" in _normalized_text()


def test_backlog_close_bullet_lead_present():
    """The bullet's lead phrase exists in the file."""
    assert "Backlog-close check" in _normalized_text()


def test_backlog_close_flip_vocabulary_present():
    """The bullet names the exact status-flip vocabulary (dissolve-
    direction-layer arc: seven legacy words collapsed to `closed`)."""
    assert "Flip the entry's `status:` to `closed`" in _normalized_text()


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
    """Step 13's report ends naming the top of the remaining bet
    queue."""
    assert '"next bet: <name>"' in _normalized_text()


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
    """Fix round 2 (fix 5a) pinned the repo-root-relative path; the
    ship-progress-tooling arc (Task 2) rewrote the clause to cascade
    wording — the script also ships in the loom-code plugin, so the
    skip fires only when neither copy resolves."""
    assert (
        "no backlog store or neither copy of `backlog_index.py`"
        in _normalized_text()
    )


def test_step13_queue_empty_alternative_phrase_present():
    """Step 13's report line has two renderings depending on queue
    state: 'next bet: <name>' when non-empty, or this literal
    string when the bet queue has nothing in it."""
    assert '"bet queue empty"' in _normalized_text()


def _backlog_close_row_text() -> str:
    """The Backlog-close row's own window (this row's cells only) — so
    the betting-duty pins below can't accidentally match wording that
    lives in a neighboring row."""
    normalized = _normalized_text()
    close_idx = normalized.find("Backlog-close check")
    head_idx = normalized.find("Attached-HEAD check:")
    assert close_idx != -1
    assert head_idx != -1
    return normalized[close_idx:head_idx]


def test_zero_live_bets_are_reported_without_a_user_prompt():
    """An empty bet queue is visible in the close-out report, but it
    must not turn close-out into a user-decision stop."""
    row = _backlog_close_row_text()
    assert "bet queue empty" in row
    assert "do not ask" in row
    assert "surface a betting prompt to the user" not in row


def test_backlog_close_never_auto_promotes():
    """An empty queue does not authorize an agent to choose the next
    bet; agents never auto-promote candidates."""
    assert "agents never auto-promote" in _backlog_close_row_text()


def test_close_out_row_reports_empty_store_without_direction():
    """The queue status depends on zero live bets, without the retired
    direction-write verb or a prompt-based promotion flow."""
    row = _backlog_close_row_text()
    assert "zero live `bet` entries" in row
    assert "--direction-write" not in row
    assert "agents never auto-promote — promotion is never a silent default" in row


def test_backlog_charter_and_close_out_agree_on_empty_queue_authority():
    """Both sources keep an empty queue notification-only; promotion
    starts only when the user explicitly asks to choose or promote."""
    assert "do not ask" in _backlog_close_row_text()
    charter = _normalized_charter_text()
    assert "only by an explicit user request to choose or promote" in charter
    assert "never because close-out found an empty `bet` queue" in charter
    assert "**user-only**; agents never promote" in charter
