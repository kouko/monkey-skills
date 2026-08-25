"""Compaction contract for the user-insights entrypoint."""

from pathlib import Path


SKILL = Path(__file__).parents[2] / "skills" / "user-insights" / "SKILL.md"
TEXT = SKILL.read_text(encoding="utf-8")
LOW = TEXT.lower()
FOLDED = " ".join(LOW.split())
PLAIN = FOLDED.replace("**", "")


def test_entrypoint_preserves_modes_evidence_commitment_and_validation_within_word_range():
    assert "mode 1" in LOW and "mode 2" in LOW
    assert "never interrogate the user for facts that are researchable" in LOW
    assert "agents never self-commit" in LOW
    assert "validate_discovery_artifacts.py" in TEXT
    words = len(TEXT.split())
    assert 925 <= words <= 1056, (
        f"user-insights/SKILL.md is {words} words; expected 925–1,056"
    )


def test_modes_keep_distinct_authorities_and_problem_space_evidence():
    assert "opportunity-space mapping" in LOW and "value commitment" in LOW
    assert "ground truth" in LOW and "keep them separated" in LOW
    assert "problem-space-pure" in LOW and "never states how to solve" in LOW
    assert "job story" in LOW and "every asserted need cites a claim row" in LOW
    assert "a need with no evidence is an open question" in FOLDED


def test_commitment_requires_explicit_recommendation_and_user_ratification():
    for marker in ("Recommend", "Why", "Conditional reversal"):
        assert marker in TEXT
    assert "only after the user ratifies" in LOW
    assert "agents never self-commit" in LOW
    assert "explicit affirmative user reply" in FOLDED


def test_research_routing_preserves_bilingual_fallback_and_evidence_chain():
    assert "more than 3 research questions" in FOLDED
    assert "primary user evidence" in LOW
    assert "research-toolkit:deep-deep-research" in TEXT and "EN + JA" in TEXT
    assert "if live search is unavailable" in LOW
    assert "delegate through the host's heavyweight route" in LOW
    assert "evidence.md (facts)" in LOW and "research/ (reports)" in LOW
    assert "user-insights.md (insights + commitment)" in LOW
    assert "evidence outlives any single report" in LOW


def test_jurisdiction_and_validator_remain_bounded_and_fail_loud():
    assert "may not render investment / worth-it verdicts" in PLAIN
    assert "validate_discovery_artifacts.py" in TEXT
    assert "never through a shell" in LOW and "bounded at 2 attempts" in LOW
    assert "if still non-zero after 2 fix-and-rerun cycles, stop" in FOLDED
