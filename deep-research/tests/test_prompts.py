"""Tests for deep_research.prompts — verbatim content assertions.

TDD RED: these tests must fail before prompts.py exists.
"""
import pytest


# ---------------------------------------------------------------------------
# Acceptance test (verbatim markers from spec)
# ---------------------------------------------------------------------------

def test_verbatim_markers():
    """Key verbatim phrases must survive word-for-word from the reference spec."""
    from deep_research.prompts import verify_prompt, fetch_prompt, scope_prompt

    verify = verify_prompt(
        claim={
            "claim": "X causes Y",
            "sourceUrl": "https://example.com",
            "sourceQuality": "secondary",
            "quote": "X does indeed cause Y",
        },
        voter_idx=0,
        question="Does X cause Y?",
    )
    assert "Default to refuted=true if uncertain" in verify
    assert "Try to REFUTE" in verify

    fetch = fetch_prompt(
        source={"url": "https://example.com", "title": "Example"},
        angle="academic/technical",
        question="Does X cause Y?",
    )
    assert "FALSIFIABLE" in fetch

    scope = scope_prompt(question="Does X cause Y?")
    assert "complementary search angles" in scope


# ---------------------------------------------------------------------------
# Structural / interpolation tests
# ---------------------------------------------------------------------------

def test_scope_prompt_contains_question():
    from deep_research.prompts import scope_prompt
    q = "What is the boiling point of water?"
    result = scope_prompt(q)
    assert q in result
    assert "Structured output only." in result


def test_search_prompt_interpolates_fields():
    from deep_research.prompts import search_prompt
    angle = {
        "label": "academic/technical",
        "rationale": "Peer-reviewed results",
        "query": "boiling point water peer review",
    }
    result = search_prompt(angle=angle, question="What is the boiling point of water?")
    assert angle["label"] in result
    assert angle["rationale"] in result
    assert angle["query"] in result
    assert "What is the boiling point of water?" in result
    assert "Structured output only." in result


def test_search_prompt_no_rationale():
    """angle.get('rationale', '') — missing key must not crash."""
    from deep_research.prompts import search_prompt
    angle = {"label": "contrarian", "query": "boiling point myth"}
    result = search_prompt(angle=angle, question="Q?")
    assert "contrarian" in result
    assert "Structured output only." in result


def test_fetch_prompt_interpolates_fields():
    from deep_research.prompts import fetch_prompt
    source = {"url": "https://example.com/paper", "title": "Important Paper"}
    result = fetch_prompt(source=source, angle="recent news", question="Q?")
    assert source["url"] in result
    assert source["title"] in result
    assert "recent news" in result
    assert "Structured output only." in result


def test_verify_prompt_voter_numbering():
    """voter_idx=0 → shows '1/{VOTES_PER_CLAIM}' in the header."""
    from deep_research.prompts import verify_prompt
    claim = {
        "claim": "Some claim",
        "sourceUrl": "https://source.example",
        "sourceQuality": "primary",
        "quote": "Direct quote here",
    }
    result = verify_prompt(claim=claim, voter_idx=0, question="Q?")
    # voter 1 of VOTES_PER_CLAIM (3)
    assert "voter 1/3" in result
    assert claim["claim"] in result
    assert claim["sourceUrl"] in result
    assert claim["quote"] in result
    assert "Structured output only." in result


def test_verify_prompt_voter_idx_2():
    """voter_idx=2 → shows '3/3'."""
    from deep_research.prompts import verify_prompt
    claim = {
        "claim": "Another claim",
        "sourceUrl": "https://source.example",
        "sourceQuality": "blog",
        "quote": "Some quote",
    }
    result = verify_prompt(claim=claim, voter_idx=2, question="Q?")
    assert "voter 3/3" in result


def test_synthesis_prompt_interpolates_fields():
    from deep_research.prompts import synthesis_prompt
    result = synthesis_prompt(
        question="What is Q?",
        confirmed_block="### [1] Some claim\nVote: 3-0 · Source: ...\n",
        killed_block="## Refuted claims (for transparency)\n",
        n_confirmed=1,
    )
    assert "What is Q?" in result
    assert "1" in result  # n_confirmed appears in prompt
    assert "Structured output only." in result
    assert "### [1] Some claim" in result
    assert "## Refuted claims" in result
