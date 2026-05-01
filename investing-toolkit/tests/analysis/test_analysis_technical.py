"""Tests for analysis-technical/scripts/ta_compute.py."""
from __future__ import annotations

import json

import pytest

from conftest import TA_SCRIPT, run_script


def test_help_runs(runner):
    res = runner(TA_SCRIPT, "--help")
    assert res.returncode == 0


def test_smoke_full_history(runner, fixtures_dir):
    res = runner(TA_SCRIPT, "--input", str(fixtures_dir / "ohlcv_full.json"))
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["ticker"] == "TEST"


def test_schema_all_indicators_present(runner, fixtures_dir):
    """All 5 indicators (RSI-14, MACD, BB, ATR-14, SMA) present with full 251-row history."""
    res = runner(TA_SCRIPT, "--input", str(fixtures_dir / "ohlcv_full.json"))
    payload = json.loads(res.stdout)
    ind = payload["indicators"]
    assert "rsi_14" in ind
    assert "macd" in ind and {"line", "signal", "histogram"} <= set(ind["macd"].keys())
    assert "bollinger" in ind and {"upper", "mid", "lower"} <= set(ind["bollinger"].keys())
    assert "atr_14" in ind
    assert "atr_pct" in ind
    assert "sma" in ind and {"20", "50", "200"} <= set(ind["sma"].keys())
    # Provenance
    prov = payload["_provenance"]
    for key in ("skill", "ta_client_version", "rows_consumed", "warnings"):
        assert key in prov
    assert prov["skill"] == "analysis-technical"


def test_signal_vocabulary_lowercase_snake_case(runner, fixtures_dir):
    res = runner(TA_SCRIPT, "--input", str(fixtures_dir / "ohlcv_full.json"))
    payload = json.loads(res.stdout)
    signals = payload["signals"]
    assert signals["rsi_signal"] in {"oversold", "neutral", "overbought", "n/a"}
    assert signals["macd_crossover"] in {"bullish", "bearish", "n/a"}
    assert signals["bb_signal"] in {"above_upper", "below_lower", "upper_half", "lower_half", "n/a"}
    assert signals["price_vs_sma200"] in {"above", "below", "n/a"}
    assert signals["trend_alignment"] in {
        "strong_bullish", "bullish", "neutral", "bearish", "strong_bearish", "n/a",
    }


def test_short_history_sma200_null_with_warning(runner, fixtures_dir):
    """50-row OHLCV: SMA-200 should be null, warning logged in _provenance.warnings."""
    res = runner(TA_SCRIPT, "--input", str(fixtures_dir / "ohlcv_short.json"))
    assert res.returncode == 0
    payload = json.loads(res.stdout)
    assert payload["indicators"]["sma"]["200"] is None
    warnings = " ".join(payload["_provenance"]["warnings"])
    assert "sma_200" in warnings


def test_atr_pct_in_output(runner, fixtures_dir):
    res = runner(TA_SCRIPT, "--input", str(fixtures_dir / "ohlcv_full.json"))
    payload = json.loads(res.stdout)
    assert "atr_pct" in payload["indicators"]
    if payload["indicators"]["atr_pct"] is not None:
        assert isinstance(payload["indicators"]["atr_pct"], (int, float))


def test_missing_input(runner, tmp_path):
    res = runner(TA_SCRIPT, "--input", str(tmp_path / "missing.json"))
    assert res.returncode != 0


def test_malformed_json(runner, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    res = runner(TA_SCRIPT, "--input", str(bad))
    assert res.returncode != 0


def test_empty_history(runner, tmp_path):
    """Empty rows → returns error in JSON, not crash."""
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"ticker": "X", "history": []}))
    res = runner(TA_SCRIPT, "--input", str(empty))
    # Script prints error JSON but should still terminate normally
    payload = json.loads(res.stdout)
    assert "error" in payload or payload.get("indicators") in (None, {})


def test_indicator_subset(runner, fixtures_dir):
    """--indicators rsi,macd should only emit those two."""
    res = runner(
        TA_SCRIPT,
        "--input", str(fixtures_dir / "ohlcv_full.json"),
        "--indicators", "rsi,macd",
    )
    payload = json.loads(res.stdout)
    ind = payload["indicators"]
    assert "rsi_14" in ind
    assert "macd" in ind
    assert "bollinger" not in ind
    assert "atr_14" not in ind
    assert "sma" not in ind
