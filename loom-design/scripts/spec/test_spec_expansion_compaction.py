"""Compaction guard for the spec-expansion progressive-disclosure split."""

from pathlib import Path


SKILL = Path(__file__).parents[2] / "skills" / "spec-expansion" / "SKILL.md"
DETAILS = SKILL.parent / "references" / "execution-details.md"


def test_entrypoint_preserves_gates():
    text = SKILL.read_text(encoding="utf-8")

    assert DETAILS.is_file(), "phase-conditional execution detail needs a focused reference"
    assert "references/execution-details.md" in text
    assert "Seed-adequacy pre-flight" in text
    assert "mint_critic_verdict.py" in text and "exit 2" in text and "exit 4" in text
    assert "references/domain-tag-triage.md" in text
    assert "pairwise.py" in text and "≥4" in text
    assert "## ADDED Requirements" in text and "#### Scenario:" in text
    assert "validate_spec_output.py" in text
    assert "unresolved" in text and "SHAPING-class" in text
