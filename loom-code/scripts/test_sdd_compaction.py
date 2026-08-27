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


def test_entrypoint_preserves_orchestration() -> None:
    text = SKILL.read_text(encoding="utf-8")

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
        # Restored in the #740 follow-up after the compaction deleted it
        # outright. Pinned so a re-deletion fails instead of going green:
        # the word bounds alone cannot see it leave.
        "**Version / semver work in implementer tasks.**",
        "external-surface-grounding check and returns `NEEDS_REVISION`",
    )
    for marker in required:
        assert marker in text

    assert CONDITIONAL_OPERATIONS.is_file()
