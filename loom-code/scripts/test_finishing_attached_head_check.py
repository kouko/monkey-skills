"""Prose-pin test for the finishing Step 8 attached-HEAD check.

Pins the pre-commit tree-state bullet in
finishing-a-development-branch/SKILL.md Step 8: `git symbolic-ref -q
HEAD` must resolve to the branch being finished before the close-out
commit; a detached HEAD is a STOP, never a commit base. Added after a
live incident: a subagent detached the orchestrator's main tree
mid-arc and the 0.55.0 close-out commit landed on a detached HEAD.
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


def test_attached_head_bullet_lead_present():
    """The bullet's lead phrase exists in the file."""
    assert "Attached-HEAD check:" in _normalized_text()


def test_attached_head_bullet_names_the_command():
    """The bullet names the exact command that decides the check."""
    assert "`git symbolic-ref -q HEAD`" in _normalized_text()


def test_attached_head_bullet_closing_absolute_present():
    """The bullet ends on the absolute: no close-out commit on a
    detached HEAD."""
    assert (
        "never commit the close-out on a detached HEAD"
        in _normalized_text()
    )


def test_attached_head_check_precedes_status_bullet():
    """The check sits in Step 8's hygiene list before the
    `git status --short` bullet — it is a pre-commit tree-state check,
    same family as its siblings."""
    normalized = _normalized_text()
    check_idx = normalized.find("Attached-HEAD check:")
    status_idx = normalized.find("Run `git status --short` to confirm")
    assert check_idx != -1
    assert status_idx != -1
    assert check_idx < status_idx
