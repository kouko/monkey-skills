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

    # Both bounds re-baselined in the #740 follow-up. They were calibrated on
    # the premise that the compaction was lossless; it was not — the
    # "Version / semver work in implementer tasks" rule and its NEEDS_REVISION
    # consequence had been dropped by accident and are restored here. The
    # package total below now lands at 8.9% under the 4,504-word baseline, a
    # documented 5-10% weak win rather than the >=10% target. The weak-win
    # disposition is the user's to make; kouko ratified it on the
    # fix/740-compaction-followups review, the shortfall being restored
    # content that should never have left.
    assert 3063 <= words <= 3300, (
        "the entrypoint must stay compact after counting extracted prose; "
        f"measured {words} words"
    )
    assert words + reference_words <= 4110, (
        "SKILL.md plus the extracted reference must stay at or below the "
        "re-baselined 4,110-word bound; the current pair measures 8.9% under "
        "the 4,504-word baseline, a documented weak win (see the comment "
        f"above); measured {words + reference_words} words"
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
