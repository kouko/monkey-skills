"""Compaction guard for the spec-expansion progressive-disclosure split."""

import re
from pathlib import Path


SKILL = Path(__file__).parents[2] / "skills" / "spec-expansion" / "SKILL.md"
DETAILS = SKILL.parent / "references" / "execution-details.md"
BASELINE_WORDS = 4487
MAX_WORDS = int(BASELINE_WORDS * 0.80)


def test_entrypoint_preserves_gates_under_word_ceiling():
    text = SKILL.read_text(encoding="utf-8")
    words = re.findall(r"\S+", text)

    assert len(words) <= MAX_WORDS, (
        f"entrypoint has {len(words)} words; expected at most {MAX_WORDS} "
        f"(20% below the {BASELINE_WORDS}-word baseline)"
    )
    assert DETAILS.is_file(), "phase-conditional execution detail needs a focused reference"
    assert "references/execution-details.md" in text
    assert "Seed-adequacy pre-flight" in text
    assert "mint_critic_verdict.py" in text and "exit 2" in text and "exit 4" in text
    assert "references/domain-tag-triage.md" in text
    assert "pairwise.py" in text and "≥4" in text
    assert "## ADDED Requirements" in text and "#### Scenario:" in text
    assert "validate_spec_output.py" in text
    assert "unresolved" in text and "SHAPING-class" in text
