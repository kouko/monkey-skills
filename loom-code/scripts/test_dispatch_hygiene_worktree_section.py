"""Prose-pin test for Task 2 (worktree-isolated reviewer dispatch guidance).

Pins the new `## Worktree-isolated reviewer dispatch` section inserted
into dispatch-hygiene-notes.md, directly before `## Worked example`,
with guidance bullets each led by a pinned bolded key phrase (the
BOLDED_PHRASES list below is the count of record).
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTES_MD = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "subagent-driven-development"
    / "references"
    / "dispatch-hygiene-notes.md"
)

SECTION_HEADING = "## Worktree-isolated reviewer dispatch"

BOLDED_PHRASES = [
    "**The worktree may be detached at the default-branch tip**",
    "**Name known environmental test failures in the packet**",
    "**`standards_version` comes from the REVIEWED BRANCH's manifest**",
    "**Never `git checkout` / `git switch` in the orchestrator's main working tree**",
]


def _normalized_text() -> str:
    """Whitespace-normalized dispatch-hygiene-notes.md text (collapses
    hard wraps so a contiguous-phrase match doesn't depend on line
    breaks)."""
    text = NOTES_MD.read_text(encoding="utf-8")
    return " ".join(text.split())


def test_capacity_error_recovery_heading_present():
    """Positive-fact control: the pre-existing §Capacity-error recovery
    heading is present — proves the section test below is not vacuous
    (i.e. the file is actually being read/matched, not a stub)."""
    assert "## Capacity-error recovery" in _normalized_text()


def test_worktree_section_heading_present():
    """Task 2: the new section heading exists in the file."""
    assert SECTION_HEADING in _normalized_text()


def test_worktree_section_precedes_worked_example():
    """Task 2: the new section is inserted directly before
    `## Worked example`, not appended elsewhere."""
    normalized = _normalized_text()
    section_idx = normalized.find(SECTION_HEADING)
    worked_example_idx = normalized.find("## Worked example")
    assert section_idx != -1
    assert worked_example_idx != -1
    assert section_idx < worked_example_idx


def test_worktree_section_bolded_key_phrases_present():
    """All pinned bolded key phrases appear in the file,
    whitespace-normalized."""
    normalized = _normalized_text()
    for phrase in BOLDED_PHRASES:
        assert phrase in normalized, f"missing pinned phrase: {phrase!r}"


def test_orchestrator_tree_bullet_names_both_remedies():
    """The fourth bullet (never checkout in the orchestrator's tree)
    names both permitted routes: `git show` for reading other revisions,
    and the agent's OWN worktree for anything needing a different
    checkout."""
    normalized = _normalized_text()
    assert "Read other revisions via `git show`" in normalized
    assert "inside your OWN worktree" in normalized
