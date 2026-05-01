"""Tests for analysis-screener/scripts/screener_compute.py."""
from __future__ import annotations

import json

import pytest

from conftest import SCREENER_SCRIPT, run_script


PRESETS = [
    "value", "deep-value", "quality", "high-dividend",
    "growth", "growth-value", "momentum", "balanced",
]


def test_help_runs(runner):
    res = runner(SCREENER_SCRIPT, "--help")
    assert res.returncode == 0


def test_smoke_default(runner, fixtures_dir):
    res = runner(
        SCREENER_SCRIPT, "--input", str(fixtures_dir / "screener_5tickers.json"),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert "ranked" in payload
    assert "preset_used" in payload
    assert payload["preset_used"] == "balanced"  # default


@pytest.mark.parametrize("preset", PRESETS)
def test_all_presets_run(runner, fixtures_dir, preset):
    res = runner(
        SCREENER_SCRIPT,
        "--input", str(fixtures_dir / "screener_5tickers.json"),
        "--preset", preset,
    )
    assert res.returncode == 0, f"preset {preset} failed: {res.stderr}"
    payload = json.loads(res.stdout)
    assert payload["preset_used"] == preset


def test_schema(runner, fixtures_dir):
    res = runner(
        SCREENER_SCRIPT,
        "--input", str(fixtures_dir / "screener_5tickers.json"),
        "--preset", "balanced",
    )
    payload = json.loads(res.stdout)
    for key in ("ranked", "preset_used", "filters_applied", "weights_applied", "_provenance"):
        assert key in payload, f"missing key: {key}"
    assert isinstance(payload["ranked"], list)
    if payload["ranked"]:
        item = payload["ranked"][0]
        for key in ("ticker", "composite_score", "breakdown", "rank"):
            assert key in item


def test_missing_input(runner, tmp_path):
    res = runner(
        SCREENER_SCRIPT, "--input", str(tmp_path / "missing.json"),
    )
    assert res.returncode != 0


def test_malformed_json(runner, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json{")
    res = runner(SCREENER_SCRIPT, "--input", str(bad))
    assert res.returncode != 0


def test_empty_input(runner, tmp_path):
    empty = tmp_path / "empty.json"
    empty.write_text("[]")
    res = runner(SCREENER_SCRIPT, "--input", str(empty))
    assert res.returncode != 0  # script returns 1 for "no records"


# ---------------------------------------------------------------------------
# Skill-specific
# ---------------------------------------------------------------------------


def test_high_roe_does_not_saturate_quality(runner, fixtures_dir):
    """ROE 1.50 (extreme like AAPL) → quality clamped to 1.0 (anchor at ROE/0.30)."""
    res = runner(
        SCREENER_SCRIPT,
        "--input", str(fixtures_dir / "screener_5tickers.json"),
        "--preset", "balanced",
    )
    payload = json.loads(res.stdout)
    aapl = next((r for r in payload["ranked"] if r["ticker"] == "AAPL"), None)
    assert aapl is not None
    # ROE/0.30 = 5.0 → clamped to 1.0
    assert aapl["breakdown"]["quality"] == 1.0


def test_mid_band_roe_differentiated(runner, fixtures_dir):
    """ROE 0.10/0.15/0.25 should produce quality 0.33/0.50/0.83 respectively."""
    res = runner(
        SCREENER_SCRIPT,
        "--input", str(fixtures_dir / "screener_5tickers.json"),
        "--preset", "balanced",
    )
    payload = json.loads(res.stdout)
    by_ticker = {r["ticker"]: r for r in payload["ranked"]}
    # MSFT roe=0.10 → 0.10/0.30 = 0.3333
    if "MSFT" in by_ticker:
        assert abs(by_ticker["MSFT"]["breakdown"]["quality"] - 0.3333) < 0.01
    # MIDQ roe=0.15 → 0.15/0.30 = 0.5
    if "MIDQ" in by_ticker:
        assert abs(by_ticker["MIDQ"]["breakdown"]["quality"] - 0.5) < 0.01
    # MIDQ2 roe=0.25 → 0.25/0.30 = 0.8333
    if "MIDQ2" in by_ticker:
        assert abs(by_ticker["MIDQ2"]["breakdown"]["quality"] - 0.8333) < 0.01


def test_pe_max_filter_override(runner, fixtures_dir):
    """--pe-max 12 should exclude PE > 12 records."""
    res = runner(
        SCREENER_SCRIPT,
        "--input", str(fixtures_dir / "screener_5tickers.json"),
        "--preset", "balanced",
        "--pe-max", "12",
    )
    payload = json.loads(res.stdout)
    assert payload["filters_applied"]["pe_max"] == 12.0
    for item in payload["ranked"]:
        pe = item["metrics"].get("trailingPE")
        if pe is not None:
            assert pe <= 12.0


def test_top_n_limits_output(runner, fixtures_dir):
    res = runner(
        SCREENER_SCRIPT,
        "--input", str(fixtures_dir / "screener_5tickers.json"),
        "--preset", "balanced",
        "--top-n", "2",
    )
    payload = json.loads(res.stdout)
    assert len(payload["ranked"]) <= 2
    assert payload["returned"] <= 2


def test_provenance_block(runner, fixtures_dir):
    res = runner(
        SCREENER_SCRIPT,
        "--input", str(fixtures_dir / "screener_5tickers.json"),
    )
    payload = json.loads(res.stdout)
    prov = payload["_provenance"]
    assert prov["skill"] == "analysis-screener"
    assert prov["io"] == "none"
    assert "computed_at" in prov
