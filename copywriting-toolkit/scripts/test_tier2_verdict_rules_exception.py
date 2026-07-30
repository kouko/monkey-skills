"""Governance pins for the Tier-2 verdict-rules replacement exception.

WHY: the convergence-modernization arc replaces rubric `## Verdict Rules`
blocks in place (retiring the count-based rule), which the Tier-2
additive-only discipline did not sanction. T3's spec review flagged the
gap: the replacement must be authorized by the governing CLAUDE.md
itself, and every touched rubric's DIVERGED header must cite that
authority — otherwise the headers claim an exception no rule grants.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = ROOT / "CLAUDE.md"
FORM_RUBRIC = (
    ROOT / "skills" / "copywriting-form-check-stage" / "rubrics"
    / "form-appropriate-gate.md"
)
VOICE_RUBRIC = (
    ROOT / "skills" / "copywriting-voice-tone-stage" / "rubrics"
    / "voice-consistency-gate.md"
)

EXCEPTION_TITLE = "Exception — plugin-owned gate verdict rules"


def test_tier2_carries_the_verdict_rules_exception():
    text = CLAUDE_MD.read_text(encoding="utf-8")
    assert EXCEPTION_TITLE in text
    tier2 = text.split("### Tier 2", 1)[1].split("### DIVERGED", 1)[0]
    assert EXCEPTION_TITLE in tier2, (
        "the exception must live inside the Tier-2 section it amends"
    )


def test_form_rubric_header_cites_the_exception():
    text = FORM_RUBRIC.read_text(encoding="utf-8")
    header = text.split("-->", 1)[0]
    assert EXCEPTION_TITLE in header


def test_voice_rubric_has_diverged_header_citing_the_exception():
    text = VOICE_RUBRIC.read_text(encoding="utf-8")
    assert text.lstrip().startswith("<!--"), (
        "voice rubric was modified by this arc and so MUST carry a "
        "DIVERGED header (Tier-2 rule)"
    )
    header = text.split("-->", 1)[0]
    assert "DIVERGED FROM domain-teams:copywriting-team" in header
    assert EXCEPTION_TITLE in header


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
