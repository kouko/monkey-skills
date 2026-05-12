"""Tests for scripts/lib/gate_i1_untranslatability.py — I1 flagging gate.

Covers Task E4 of translation-toolkit v0.1.0 plan (lines 1969-2001).

Key invariants enforced:

- **INFO-only** (per spec line 405-407): I1 never returns WARN/FAIL; at
  most it returns INFO with a flag list for the audit trail.
- **Non-interactive**: the gate does not prompt; decisions are pure
  inference from text presence + parenthesis heuristic.
- **Heuristic decisions**: borrow / explain / approximate / unknown,
  including fullwidth-paren coverage for JP/ZH targets.
- **Graceful skip + pass paths**: ``source_analysis=None`` → SKIPPED;
  empty list → PASS.
"""
from __future__ import annotations

import sys
from pathlib import Path

# tests/ -> scripts/ -> translation-toolkit/ -> repo root
SCRIPTS_DIR = Path(__file__).resolve().parent.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.gate_i1_untranslatability import i1_check  # noqa: E402


# --------------------------------------------------------------------------- #
# Decision detection: borrow / explain / approximate / unknown                #
# --------------------------------------------------------------------------- #


def test_i1_flags_phrases_from_source_analysis():
    """I1 collects untranslatable phrases identified during Layer 2
    source-analysis, records decision per phrase, no user prompt."""
    source_analysis = {
        "untranslatables": [
            {"phrase": "御朱印", "category": "cultural",
             "candidates": ["temple stamp"]}
        ]
    }
    target = "I visited the temple to receive the 御朱印 stamp"  # borrowed
    result = i1_check(source_analysis=source_analysis, target=target)
    assert result["verdict"] == "INFO"
    assert result["details"]["flags"][0]["phrase"] == "御朱印"
    assert result["details"]["flags"][0]["decision"] == "borrow"
    assert result["details"]["flags"][0]["alternatives"] == ["temple stamp"]


def test_i1_detects_explain_when_paren_follows():
    """ASCII paren within 50 chars after the phrase → 'explain' decision."""
    source_analysis = {
        "untranslatables": [{"phrase": "御朱印", "candidates": []}]
    }
    target = "I received a 御朱印 (a temple stamp) at the shrine"
    result = i1_check(source_analysis=source_analysis, target=target)
    assert result["details"]["flags"][0]["decision"] == "explain"


def test_i1_detects_approximate_when_candidate_appears():
    """Phrase absent but candidate present → 'approximate' decision."""
    source_analysis = {
        "untranslatables": [
            {"phrase": "御朱印", "candidates": ["temple stamp"]}
        ]
    }
    target = "I received a temple stamp at the shrine"
    result = i1_check(source_analysis=source_analysis, target=target)
    assert result["details"]["flags"][0]["decision"] == "approximate"
    # Phrase not in target → excerpt empty.
    assert result["details"]["flags"][0]["target_excerpt"] == ""


def test_i1_detects_unknown_when_neither_phrase_nor_candidate():
    """Phrase absent + no candidate matches → 'unknown'."""
    source_analysis = {
        "untranslatables": [
            {"phrase": "御朱印", "candidates": ["temple stamp"]}
        ]
    }
    target = "I had a great time at the shrine"
    result = i1_check(source_analysis=source_analysis, target=target)
    assert result["details"]["flags"][0]["decision"] == "unknown"


def test_i1_handles_fullwidth_paren_for_explain():
    """Japanese fullwidth parenthesis （）counts as 'explain' too."""
    source_analysis = {
        "untranslatables": [{"phrase": "御朱印", "candidates": []}]
    }
    target = "私は御朱印（神社のスタンプ）をもらいました"
    result = i1_check(source_analysis=source_analysis, target=target)
    assert result["details"]["flags"][0]["decision"] == "explain"


# --------------------------------------------------------------------------- #
# Verdict-shape paths                                                         #
# --------------------------------------------------------------------------- #


def test_i1_pass_when_no_untranslatables():
    """Empty untranslatables list → PASS (nothing to flag)."""
    source_analysis = {"untranslatables": []}
    result = i1_check(source_analysis=source_analysis, target="anything")
    assert result["verdict"] == "PASS"
    assert result["details"]["flags"] == []


def test_i1_skip_when_no_source_analysis():
    """source_analysis=None → SKIPPED, never coerced to INFO/PASS."""
    result = i1_check(source_analysis=None, target="anything")
    assert result["verdict"] == "SKIPPED"
    assert result["diff"] is None


# --------------------------------------------------------------------------- #
# Defensive / edge cases                                                      #
# --------------------------------------------------------------------------- #


def test_i1_skips_entries_with_empty_phrase():
    """Degenerate entries (phrase='') are skipped silently to avoid emitting
    flags downstream consumers can't display."""
    source_analysis = {
        "untranslatables": [
            {"phrase": "", "candidates": ["x"]},
            {"phrase": "御朱印", "candidates": []},
        ]
    }
    target = "御朱印"
    result = i1_check(source_analysis=source_analysis, target=target)
    assert len(result["details"]["flags"]) == 1
    assert result["details"]["flags"][0]["phrase"] == "御朱印"


def test_i1_target_excerpt_window_around_phrase():
    """Excerpt should include surrounding context for audit-trail review."""
    source_analysis = {
        "untranslatables": [{"phrase": "御朱印", "candidates": []}]
    }
    target = "今日は朝早く起きて、近所の有名な神社に行って御朱印をもらいました。とても綺麗でした。"
    result = i1_check(source_analysis=source_analysis, target=target)
    excerpt = result["details"]["flags"][0]["target_excerpt"]
    assert "御朱印" in excerpt
    # Window has context on both sides.
    assert excerpt != "御朱印"


def test_i1_paren_gloss_outside_50_char_window_is_borrow_not_explain():
    """Lock the 50-char heuristic: a paren far from the phrase should
    NOT trigger 'explain' (otherwise unrelated parens elsewhere in the
    sentence would always escalate borrow → explain)."""
    source_analysis = {
        "untranslatables": [{"phrase": "御朱印", "candidates": []}]
    }
    # Paren 60+ chars after phrase.
    target = (
        "I received a 御朱印 then walked around the temple grounds for "
        "about an hour before heading home (it was raining)"
    )
    result = i1_check(source_analysis=source_analysis, target=target)
    assert result["details"]["flags"][0]["decision"] == "borrow"
