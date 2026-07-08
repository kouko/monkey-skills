"""Tests for prompts — verbatim content assertions + CLI.

Ported from deep-research/tests/test_prompts.py with flat imports
(`from prompts import ...`), plus CLI tests for the new
`python prompts.py {scope|search|fetch|verify|synthesis}` entry point.

TDD RED: the import / CLI tests must fail before scripts/prompts.py exists.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROMPTS_PY = Path(__file__).resolve().parent / "prompts.py"


# ---------------------------------------------------------------------------
# Acceptance test (verbatim markers from spec)
# ---------------------------------------------------------------------------

def test_verbatim_markers():
    """Key verbatim phrases must survive word-for-word from the reference spec."""
    from prompts import verify_prompt, fetch_prompt, scope_prompt

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
    from prompts import scope_prompt
    q = "What is the boiling point of water?"
    result = scope_prompt(q)
    assert q in result
    assert "Structured output only." in result


def test_search_prompt_interpolates_fields():
    from prompts import search_prompt
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
    from prompts import search_prompt
    angle = {"label": "contrarian", "query": "boiling point myth"}
    result = search_prompt(angle=angle, question="Q?")
    assert "contrarian" in result
    assert "Structured output only." in result


def test_fetch_prompt_interpolates_fields():
    from prompts import fetch_prompt
    source = {"url": "https://example.com/paper", "title": "Important Paper"}
    result = fetch_prompt(source=source, angle="recent news", question="Q?")
    assert source["url"] in result
    assert source["title"] in result
    assert "recent news" in result
    assert "Structured output only." in result


def test_verify_prompt_voter_numbering():
    """voter_idx=0 → shows '1/{VOTES_PER_CLAIM}' in the header."""
    from prompts import verify_prompt
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
    from prompts import verify_prompt
    claim = {
        "claim": "Another claim",
        "sourceUrl": "https://source.example",
        "sourceQuality": "blog",
        "quote": "Some quote",
    }
    result = verify_prompt(claim=claim, voter_idx=2, question="Q?")
    assert "voter 3/3" in result


def test_verify_prompt_accepts_url_key_when_sourceurl_missing():
    """claim dicts keyed 'url' (not 'sourceUrl') must not crash — tolerant
    lookup matches the .get(key, default) pattern used in synthesis.py."""
    from prompts import verify_prompt
    claim = {
        "claim": "X",
        "url": "https://source.example",
        "sourceQuality": "primary",
        "quote": "q",
    }
    result = verify_prompt(claim=claim, voter_idx=0, question="Q?")
    assert "https://source.example" in result


def test_synthesis_prompt_interpolates_fields():
    from prompts import synthesis_prompt
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


# ---------------------------------------------------------------------------
# CLI tests — `python prompts.py {sub} ...` prints assembled prompt to stdout
# ---------------------------------------------------------------------------

def _run_cli(*args: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(PROMPTS_PY), *args],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def test_cli_scope():
    out = _run_cli("scope", "--question", "WHAT IS X")
    assert "WHAT IS X" in out
    assert "complementary search angles" in out
    assert "Structured output only." in out


def test_cli_search():
    angle = json.dumps({"label": "academic", "rationale": "peer review", "query": "x query"})
    out = _run_cli("search", "--angle", angle, "--question", "WHAT IS X")
    assert "academic" in out
    assert "peer review" in out
    assert "x query" in out
    assert "WHAT IS X" in out
    assert "Structured output only." in out


def test_cli_fetch():
    source = json.dumps({"url": "https://e.com/p", "title": "Paper Title"})
    out = _run_cli("fetch", "--source", source, "--label", "recent news", "--question", "WHAT IS X")
    assert "https://e.com/p" in out
    assert "Paper Title" in out
    assert "recent news" in out
    assert "WHAT IS X" in out
    assert "Structured output only." in out


def test_cli_verify():
    claim = json.dumps({
        "claim": "C claim",
        "sourceUrl": "https://s.example",
        "sourceQuality": "primary",
        "quote": "the quote",
    })
    out = _run_cli("verify", "--claim", claim, "--voter-idx", "0", "--question", "WHAT IS X")
    assert "voter 1/3" in out
    assert "C claim" in out
    assert "https://s.example" in out
    assert "the quote" in out
    assert "Try to REFUTE" in out
    assert "Structured output only." in out


def test_cli_synthesis():
    out = _run_cli(
        "synthesis",
        "--question", "WHAT IS X",
        "--confirmed-block", "### [1] A claim\n",
        "--killed-block", "## Refuted claims (for transparency)\n",
        "--confirmed-count", "1",
    )
    assert "WHAT IS X" in out
    assert "### [1] A claim" in out
    assert "## Refuted claims" in out
    assert "Structured output only." in out
