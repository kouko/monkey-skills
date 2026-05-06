"""Tests for scripts/lib/gate_s1_backtrans.py — S1 back-translation gate.

Covers Task E2 of translation-toolkit v0.1.0 plan (lines 1827-1922).

Key invariants enforced:

- **Blindness**: when ``subagent_dispatch`` is provided, the prompt it
  receives MUST contain ``translated_v2`` and MUST NOT contain
  ``original_source`` (Decision #16).
- **Graceful skip**: when ``subagent_dispatch is None``, verdict is
  ``SKIPPED`` with an audit-trail flag — the gate never fakes a verdict.
- **Mode-conditional threshold**: 0.85 faithful, 0.70 transcreation
  (Decision #4 / verification-gates.md §S1).
- **Audit-mode escalation**: WARN → FAIL when ``is_audit_mode=True``
  (Decision #17 / translation-audit per-skill matrix).
"""
from __future__ import annotations

import sys
from pathlib import Path

# tests/ -> scripts/ -> translation-toolkit/ -> repo root
SCRIPTS_DIR = Path(__file__).resolve().parent.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.gate_s1_backtrans import (  # noqa: E402
    make_blind_prompt,
    s1_check,
)


# --------------------------------------------------------------------------- #
# Subagent dispatch + blindness                                                #
# --------------------------------------------------------------------------- #


def test_s1_dispatch_with_subagent_capability():
    """When subagent_dispatch is provided, S1 calls it with blind context."""
    captured: dict[str, str] = {}

    def fake_subagent(prompt: str) -> str:
        captured["prompt"] = prompt
        return "Hello world"  # back-translation

    result = s1_check(
        original_source="Hello world",
        translated_v2="你好世界",
        source_lang="en-US",
        subagent_dispatch=fake_subagent,
        threshold=0.85,
    )
    assert result["verdict"] in ("PASS", "WARN", "FAIL")
    assert "你好世界" in captured["prompt"]
    # Blindness invariant: the original source MUST NOT leak into the
    # subagent prompt.
    assert "Hello world" not in captured["prompt"]


def test_s1_skip_when_no_subagent_capability():
    """When subagent_dispatch=None, S1 returns SKIPPED with audit-trail flag."""
    result = s1_check(
        original_source="Hello world",
        translated_v2="你好世界",
        source_lang="en-US",
        subagent_dispatch=None,
    )
    assert result["verdict"] == "SKIPPED"
    assert result["diff"] is None
    assert "no isolation" in result["details"]["reason"].lower()


# --------------------------------------------------------------------------- #
# Threshold + verdict logic                                                    #
# --------------------------------------------------------------------------- #


def test_s1_pass_in_faithful_mode_when_similarity_above_threshold():
    """Stub similarity = 0.9, default threshold = 0.85 → PASS."""
    result = s1_check(
        original_source="Hello",
        translated_v2="你好",
        source_lang="en-US",
        subagent_dispatch=lambda p: "Hello",
    )
    assert result["verdict"] == "PASS"
    assert result["details"]["similarity"] == 0.9
    assert result["details"]["threshold"] == 0.85
    assert result["diff"] is None


def test_s1_warn_in_faithful_mode_below_threshold():
    """When similarity below threshold (faithful mode), verdict is WARN.

    Empty source/target forces stub similarity = 0.0, which is below
    every meaningful threshold without needing to monkey-patch.
    """
    result = s1_check(
        original_source="",
        translated_v2="",
        source_lang="en-US",
        subagent_dispatch=lambda p: "anything",
    )
    assert result["verdict"] == "WARN"
    assert result["details"]["similarity"] == 0.0
    assert "similarity 0.00" in result["diff"]
    assert "threshold 0.85" in result["diff"]


def test_s1_transcreation_uses_lower_threshold_and_fails_below_it():
    """Transcreation uses 0.70 threshold AND verdict is FAIL (not WARN) when below.

    Per Decision #4 + verification-gates.md §S1 line 145: in transcreation
    mode S1 is promoted from SHOULD to MUST. A below-threshold similarity
    is HARD failure because S1 is the primary semantic-fidelity anchor
    when surface deviation is expected.
    """
    result = s1_check(
        original_source="",
        translated_v2="",
        source_lang="en-US",
        subagent_dispatch=lambda p: "anything",
        is_transcreation=True,
    )
    assert result["details"]["threshold"] == 0.70
    assert result["details"]["similarity"] == 0.0
    assert result["verdict"] == "FAIL"


def test_s1_transcreation_passes_when_above_lower_threshold():
    """Stub similarity 0.9 ≥ transcreation threshold 0.70 → PASS."""
    result = s1_check(
        original_source="x",
        translated_v2="y",
        source_lang="en-US",
        subagent_dispatch=lambda p: "z",
        is_transcreation=True,
    )
    assert result["details"]["threshold"] == 0.70
    assert result["details"]["similarity"] == 0.9
    assert result["verdict"] == "PASS"


def test_s1_faithful_mode_below_threshold_is_warn_not_fail():
    """Lock the SHOULD vs MUST split: faithful + below threshold + audit_mode=False
    must stay WARN (NOT FAIL). Guards against accidental escalation of
    SHOULD-tier failures when neither audit nor transcreation flips apply.
    """
    result = s1_check(
        original_source="",
        translated_v2="",
        source_lang="en-US",
        subagent_dispatch=lambda p: "anything",
        is_transcreation=False,
        is_audit_mode=False,
    )
    assert result["verdict"] == "WARN"


def test_s1_audit_mode_upgrades_warn_to_fail():
    """In audit mode, below-threshold similarity is FAIL not WARN."""
    result = s1_check(
        original_source="",
        translated_v2="",
        source_lang="en-US",
        subagent_dispatch=lambda p: "anything",
        is_audit_mode=True,
    )
    assert result["verdict"] == "FAIL"
    assert result["details"]["similarity"] == 0.0


def test_s1_audit_mode_pass_still_passes():
    """Audit-mode escalation only flips WARN → FAIL, not PASS → FAIL."""
    result = s1_check(
        original_source="Hello",
        translated_v2="你好",
        source_lang="en-US",
        subagent_dispatch=lambda p: "Hello",
        is_audit_mode=True,
    )
    assert result["verdict"] == "PASS"


# --------------------------------------------------------------------------- #
# Blind-prompt helper                                                          #
# --------------------------------------------------------------------------- #


def test_s1_blind_prompt_contains_target_only():
    """Blind prompt must contain v2 but NOT original source."""
    prompt = make_blind_prompt("你好世界", "en-US")
    assert "你好世界" in prompt
    assert "Hello world" not in prompt
    assert "en-US" in prompt


def test_s1_blind_prompt_instructs_translation_only():
    """Prompt must instruct subagent to output translation only — no
    commentary that would inflate similarity comparison noise."""
    prompt = make_blind_prompt("hello", "ja-JP")
    assert "ONLY" in prompt
    assert "ja-JP" in prompt


# --------------------------------------------------------------------------- #
# Back-translation captured in details                                         #
# --------------------------------------------------------------------------- #


def test_s1_back_translation_recorded_in_details():
    """The subagent's output must be recorded for audit-trail review."""
    result = s1_check(
        original_source="Hello",
        translated_v2="你好",
        source_lang="en-US",
        subagent_dispatch=lambda p: "Greetings",
    )
    assert result["details"]["back_translation"] == "Greetings"
