"""Behavioral essence guard for the SDD entrypoint compaction."""

from pathlib import Path
import subprocess


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
    words = int(subprocess.check_output(("wc", "-w", str(SKILL)), text=True).split()[0])
    reference_words = int(
        subprocess.check_output(
            ("wc", "-w", str(CONDITIONAL_OPERATIONS)), text=True
        ).split()[0]
    )

    assert 3063 <= words <= 3241, (
        "the entrypoint must stay compact after counting extracted prose; "
        f"measured {words} words"
    )
    assert words + reference_words <= 4053, (
        "SKILL.md plus the extracted reference must reduce the 4,504-word "
        f"baseline by at least 10%; measured {words + reference_words} words"
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
