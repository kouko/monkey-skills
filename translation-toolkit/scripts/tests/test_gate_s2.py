"""Tests for scripts/lib/gate_s2_register.py — S2 register preservation gate.

Covers Task E3 of translation-toolkit v0.1.0 plan (lines 1926-1965).

Key invariants enforced:

- **PASS on register match**: judge returns intake register → verdict PASS.
- **WARN on mismatch (normal modes)**: SHOULD-tier — output proceeds.
- **FAIL on mismatch (audit mode)**: Decision #17 escalates SHOULD → HARD.
- **Graceful skip**: ``llm_judge=None`` → SKIPPED with reason; never fakes
  a verdict.
- **Skip on bad inputs**: unknown intake register or unparseable judge
  response → SKIPPED rather than WARN/FAIL (avoids false negatives).
"""
from __future__ import annotations

import sys
from pathlib import Path

# tests/ -> scripts/ -> translation-toolkit/ -> repo root
SCRIPTS_DIR = Path(__file__).resolve().parent.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.gate_s2_register import REGISTERS, s2_check  # noqa: E402


# --------------------------------------------------------------------------- #
# Match / mismatch verdict logic                                              #
# --------------------------------------------------------------------------- #


def test_s2_register_match():
    """S2 PASS when target register matches intake register."""
    result = s2_check(
        original_source="Could you please review this?",
        translated_v2="ご確認いただけますでしょうか",
        intake_register="formal",
        llm_judge=lambda p: "formal",
    )
    assert result["verdict"] == "PASS"
    assert result["details"]["actual_register"] == "formal"
    assert result["details"]["expected_register"] == "formal"
    assert result["diff"] is None


def test_s2_register_mismatch_warn_in_normal_mode():
    """SHOULD-tier mismatch → WARN; output proceeds."""
    result = s2_check(
        original_source="Could you please review this?",
        translated_v2="見て",
        intake_register="formal",
        llm_judge=lambda p: "playful",
    )
    assert result["verdict"] == "WARN"
    assert "formal" in result["diff"]
    assert "playful" in result["diff"]


def test_s2_register_mismatch_fail_in_audit_mode():
    """Decision #17: audit-mode promotes SHOULD → HARD, so mismatch → FAIL."""
    result = s2_check(
        original_source="Could you please review this?",
        translated_v2="見て",
        intake_register="formal",
        llm_judge=lambda p: "playful",
        is_audit_mode=True,
    )
    assert result["verdict"] == "FAIL"
    assert "formal" in result["diff"]
    assert "playful" in result["diff"]


def test_s2_audit_mode_pass_still_passes():
    """Audit-mode escalation only flips WARN → FAIL, not PASS → FAIL."""
    result = s2_check(
        original_source="x",
        translated_v2="y",
        intake_register="formal",
        llm_judge=lambda p: "formal",
        is_audit_mode=True,
    )
    assert result["verdict"] == "PASS"


# --------------------------------------------------------------------------- #
# Graceful skip paths                                                         #
# --------------------------------------------------------------------------- #


def test_s2_skip_when_no_judge():
    """No LLM judge available → SKIPPED, never WARN/FAIL."""
    result = s2_check(
        original_source="x",
        translated_v2="y",
        intake_register="formal",
        llm_judge=None,
    )
    assert result["verdict"] == "SKIPPED"
    assert result["diff"] is None
    assert "judge" in result["details"]["reason"].lower()


def test_s2_skip_when_unknown_intake_register():
    """Unknown intake register → SKIPPED with explanatory reason."""
    result = s2_check(
        original_source="x",
        translated_v2="y",
        intake_register="bogus",
        llm_judge=lambda p: "formal",
    )
    assert result["verdict"] == "SKIPPED"
    assert "bogus" in result["details"]["reason"]


def test_s2_skip_when_judge_returns_garbage():
    """Unparseable judge response → SKIPPED, never coerced to WARN/FAIL."""
    result = s2_check(
        original_source="x",
        translated_v2="y",
        intake_register="formal",
        llm_judge=lambda p: "incoherent garbage",
    )
    assert result["verdict"] == "SKIPPED"


# --------------------------------------------------------------------------- #
# Judge response normalization                                                #
# --------------------------------------------------------------------------- #


def test_s2_judge_response_is_normalized():
    """Whitespace + casing in judge response should not block a match."""
    result = s2_check(
        original_source="x",
        translated_v2="y",
        intake_register="warm",
        llm_judge=lambda p: "  Warm  \n",
    )
    assert result["verdict"] == "PASS"
    assert result["details"]["actual_register"] == "warm"


def test_s2_registers_constant_is_complete():
    """Lock the canonical 4-register vocabulary so additions are deliberate."""
    assert REGISTERS == ["formal", "neutral", "warm", "playful"]
