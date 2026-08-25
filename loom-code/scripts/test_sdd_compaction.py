"""Behavioral essence guard for the SDD entrypoint compaction."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "subagent-driven-development"
    / "SKILL.md"
)
CONDITIONAL_OPERATIONS = SKILL.parent / "references" / "conditional-operations.md"


def test_entrypoint_preserves_orchestration_under_word_ceiling() -> None:
    text = SKILL.read_text(encoding="utf-8")
    words = len(text.split())

    assert 3063 <= words <= 3513, (
        "the 4,504-word baseline must shrink by 22-32%; "
        f"measured {words} words"
    )

    required = (
        "### Live-gate receipt (SDD only)",
        "## Asking the user",
        "## Process — per-task triad",
        "unchanged immutable context packet",
        "**Mechanical review-weight exemption.**",
        "**Prose review-weight substitution.**",
        "### Verdict resolution",
        "Up to **3 rounds** then escalate to user",
        "**Progress ledger.**",
        "## Model selection",
        "## Status handling — implementer states",
        "references/conditional-operations.md",
    )
    for marker in required:
        assert marker in text

    assert CONDITIONAL_OPERATIONS.is_file()
