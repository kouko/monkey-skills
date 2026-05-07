"""Tests for scripts/lib/gate_m3_problem_analyze.py — M3 deterministic linter.

Covers Phase A of translation-toolkit v0.3.0 Tier 2 plan:
docs/superpowers/plans/2026-05-07-translation-toolkit-v0.3.0-tier2.md
§Phase A.

Subrules covered:

- **M3a** HARD residual-source-script — JP→EN target with no JP chars
  PASSes; with 5% JP chars FAILs; with 0.5% JP chars (one stray name)
  PASSes (below 1% threshold).
- **M3b** SHOULD length-ratio — ratio in band PASSes; ratio 0.3 (too
  short) WARNs; ratio 3.0 (too long) WARNs.
- **M3c** SHOULD punctuation — CJK target with fullwidth ，。？！ PASSes;
  CJK target with halfwidth ,.?! WARNs; ASCII target skips (PASSes).

Aggregation invariants:
- any HARD FAIL dominates -> M3 FAIL even if SHOULD subrules WARN
- only SHOULD WARN(s) without HARD FAIL -> M3 WARN
- all PASS -> M3 PASS
"""
from __future__ import annotations

import sys
from pathlib import Path

# tests/ -> scripts/ -> translation-toolkit/ -> repo root
SCRIPTS_DIR = Path(__file__).resolve().parent.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.gate_m3_problem_analyze import (  # noqa: E402
    M3SubruleVerdict,
    M3Verdict,
    evaluate_m3,
)


def _subrule(verdict: M3Verdict, name: str) -> M3SubruleVerdict:
    """Helper: pull the named subrule out of a verdict."""
    matches = [s for s in verdict.subrules if s.subrule == name]
    assert len(matches) == 1, (
        f"expected exactly one {name} subrule, got {len(matches)}"
    )
    return matches[0]


# --------------------------------------------------------------------------- #
# M3a — Residual source-language characters (HARD)                            #
# --------------------------------------------------------------------------- #


def test_m3a_clean_target_passes():
    """JP→EN target with no JP chars at all → M3a PASS."""
    verdict = evaluate_m3(
        source_text="こんにちは、世界。",
        target_text="Hello, world.",
        source_locale="ja-JP",
        target_locale="en-US",
    )
    m3a = _subrule(verdict, "m3a")
    assert m3a.verdict == "PASS"
    assert m3a.tier == "HARD"
    assert m3a.metric == 0.0


def test_m3a_residual_jp_fails():
    """JP→EN target with ~5% JP chars (well above 1% threshold) → M3a FAIL."""
    # 100 non-whitespace ASCII chars + 5 hiragana = ~5/105 ≈ 4.8% > 1%
    body = "a" * 100
    target_text = body + "あいうえお"
    verdict = evaluate_m3(
        source_text="日本語の文章です。",
        target_text=target_text,
        source_locale="ja-JP",
        target_locale="en-US",
    )
    m3a = _subrule(verdict, "m3a")
    assert m3a.verdict == "FAIL"
    assert m3a.tier == "HARD"
    assert m3a.metric > 0.01


def test_m3a_below_threshold_passes():
    """JP→EN target with 0.5% JP chars (one stray katakana name) → M3a PASS.

    A single unmapped Katakana proper name in a long English passage —
    realistic case where a name like ``アキラ`` slips through because the
    glossary did not list it. Below the 1% threshold so M3a still PASSes.
    """
    # 1000 non-whitespace ASCII chars + 3 katakana = 3/1003 ≈ 0.3% < 1%
    body = "a" * 1000
    target_text = body + "アキラ"
    verdict = evaluate_m3(
        source_text="アキラは家に帰った。",
        target_text=target_text,
        source_locale="ja-JP",
        target_locale="en-US",
    )
    m3a = _subrule(verdict, "m3a")
    assert m3a.verdict == "PASS"
    assert m3a.tier == "HARD"
    assert 0 < m3a.metric < 0.01


# --------------------------------------------------------------------------- #
# M3b — Length-ratio sanity (SHOULD)                                          #
# --------------------------------------------------------------------------- #


def test_m3b_length_ratio_within_range():
    """Ratio ~1.2 (target slightly longer than source) → M3b PASS.

    Use ja-JP -> en-US which has band [0.6, 3.0]; ratio 1.2 sits in.
    """
    src = "あ" * 100  # approx_tokens(100 chars) = 100/3 = 33
    tgt = "a" * 120  # approx_tokens(120 chars) = 120/3 = 40 → ratio 40/33 ≈ 1.21
    verdict = evaluate_m3(
        source_text=src,
        target_text=tgt,
        source_locale="ja-JP",
        target_locale="en-US",
    )
    m3b = _subrule(verdict, "m3b")
    assert m3b.verdict == "PASS"
    assert m3b.tier == "SHOULD"


def test_m3b_length_ratio_too_short():
    """Ratio 0.3 (target ~30% of source length) → M3b WARN."""
    src = "a" * 300  # approx_tokens = 100
    tgt = "b" * 90   # approx_tokens = 30 → ratio 0.3
    # en-US -> de-DE not in pair table → falls back to default [0.5, 2.5]
    verdict = evaluate_m3(
        source_text=src,
        target_text=tgt,
        source_locale="en-US",
        target_locale="de-DE",
    )
    m3b = _subrule(verdict, "m3b")
    assert m3b.verdict == "WARN"
    assert m3b.tier == "SHOULD"
    assert m3b.metric < 0.5


def test_m3b_length_ratio_too_long():
    """Ratio 3.0 (target ~3x source length) → M3b WARN."""
    src = "a" * 100  # approx_tokens = 33
    tgt = "b" * 300  # approx_tokens = 100 → ratio ≈ 3.0
    # en-US -> de-DE not in pair table → falls back to default [0.5, 2.5]
    verdict = evaluate_m3(
        source_text=src,
        target_text=tgt,
        source_locale="en-US",
        target_locale="de-DE",
    )
    m3b = _subrule(verdict, "m3b")
    assert m3b.verdict == "WARN"
    assert m3b.tier == "SHOULD"
    assert m3b.metric > 2.5


# --------------------------------------------------------------------------- #
# M3c — Punctuation convention (SHOULD)                                       #
# --------------------------------------------------------------------------- #


def test_m3c_zh_fullwidth_passes():
    """zh-TW target using fullwidth ，。？！ → M3c PASS."""
    verdict = evaluate_m3(
        source_text="Hello, world. Are you here? Yes!",
        target_text="你好，世界。你在嗎？是的！",
        source_locale="en-US",
        target_locale="zh-TW",
    )
    m3c = _subrule(verdict, "m3c")
    assert m3c.verdict == "PASS"
    assert m3c.tier == "SHOULD"
    assert m3c.metric >= 0.8


def test_m3c_zh_halfwidth_warns():
    """zh-TW target using halfwidth ,.?! → M3c WARN."""
    verdict = evaluate_m3(
        source_text="Hello, world. Are you here? Yes!",
        target_text="你好,世界.你在嗎?是的!",
        source_locale="en-US",
        target_locale="zh-TW",
    )
    m3c = _subrule(verdict, "m3c")
    assert m3c.verdict == "WARN"
    assert m3c.tier == "SHOULD"
    assert m3c.metric < 0.8


def test_m3c_en_target_skips():
    """ASCII (en-US) target → M3c PASS (check skipped)."""
    verdict = evaluate_m3(
        source_text="こんにちは、世界。",
        target_text="Hello, world. How are you?",
        source_locale="ja-JP",
        target_locale="en-US",
    )
    m3c = _subrule(verdict, "m3c")
    assert m3c.verdict == "PASS"
    assert m3c.tier == "SHOULD"
    # detail mentions skip rationale
    assert "not CJK" in m3c.detail or "skipped" in m3c.detail.lower()


# --------------------------------------------------------------------------- #
# Aggregation                                                                 #
# --------------------------------------------------------------------------- #


def test_aggregate_hard_fail_dominates():
    """m3a FAIL + m3b WARN → M3 FAIL (HARD dominates)."""
    # JP→EN with 5% residual JP chars (m3a FAIL) and ratio 0.3 (m3b WARN
    # under default band — but ja-JP -> en-US uses [0.6, 3.0]).
    # source ja-JP -> target en-US length ratio:
    # source = 100 ja chars (approx_tokens = 33), target = 16 chars
    # (approx_tokens = 5) → ratio = 5/33 ≈ 0.15 < 0.6 → WARN
    src = "あ" * 100
    tgt = "abc " + "あいうえお" * 1  # very short + has JP chars (heavy ratio)
    # tgt non-ws chars: "abc" (3) + 5 hiragana = 8 total, 5 JP = 62.5% ≫ 1%
    verdict = evaluate_m3(
        source_text=src,
        target_text=tgt,
        source_locale="ja-JP",
        target_locale="en-US",
    )
    assert verdict.verdict == "FAIL"
    m3a = _subrule(verdict, "m3a")
    assert m3a.verdict == "FAIL"
    # m3b should also have flagged WARN, but FAIL dominates aggregation
    m3b = _subrule(verdict, "m3b")
    assert m3b.verdict == "WARN"


def test_aggregate_warn_only():
    """m3a PASS + m3b WARN + m3c PASS → M3 WARN."""
    # en-US → de-DE clean target, default ratio band [0.5, 2.5], ratio 3.0
    src = "a" * 100  # 33 tokens
    tgt = "b" * 300  # 100 tokens → ratio ≈ 3.0
    verdict = evaluate_m3(
        source_text=src,
        target_text=tgt,
        source_locale="en-US",
        target_locale="de-DE",
    )
    assert verdict.verdict == "WARN"
    assert _subrule(verdict, "m3a").verdict == "PASS"
    assert _subrule(verdict, "m3b").verdict == "WARN"
    assert _subrule(verdict, "m3c").verdict == "PASS"  # non-CJK, skipped → PASS


def test_aggregate_all_pass():
    """All three subrules PASS → M3 PASS.

    en-US -> zh-TW band is [0.4, 2.0]. Pad the source so the
    target/source token ratio sits comfortably in that band, leaving
    M3a (no JP residue), M3b (in-band), M3c (fullwidth punct) all green.
    """
    # source = 60 ASCII chars (~20 tokens), target = 18 zh chars
    # (~6 tokens) → ratio 6/20 = 0.30 — too low. Bump target to ~30 chars
    # → ratio 10/20 = 0.5 — comfortably in [0.4, 2.0].
    src = "Hello, world. How are you doing today my dear friend? Hi!"
    tgt = "你好，世界。今天你過得怎麼樣，我親愛的朋友？嗨！"
    verdict = evaluate_m3(
        source_text=src,
        target_text=tgt,
        source_locale="en-US",
        target_locale="zh-TW",
    )
    assert verdict.verdict == "PASS", (
        f"expected PASS, got {verdict.verdict}; "
        f"subrules={[(s.subrule, s.verdict, s.metric) for s in verdict.subrules]}"
    )
    assert _subrule(verdict, "m3a").verdict == "PASS"
    assert _subrule(verdict, "m3b").verdict == "PASS"
    assert _subrule(verdict, "m3c").verdict == "PASS"


def test_aggregate_empty_target_fails():
    """Non-empty source with empty target is M3 aggregate FAIL via synthetic m3a."""
    verdict = evaluate_m3(
        source_text="メロスは激怒した。",
        target_text="",
        source_locale="ja-JP",
        target_locale="en-US",
    )
    assert verdict.verdict == "FAIL"
    m3a = next(s for s in verdict.subrules if s.subrule == "m3a")
    assert m3a.verdict == "FAIL"
    assert "empty target" in m3a.detail


def test_aggregate_empty_source_passes():
    """Empty source is degenerate; all subrules PASS by convention."""
    verdict = evaluate_m3(
        source_text="",
        target_text="",
        source_locale="ja-JP",
        target_locale="en-US",
    )
    assert verdict.verdict == "PASS"
