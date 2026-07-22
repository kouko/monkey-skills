"""Tests for analysis-dcf/scripts/dcf_compute.py (Layer 2 pure compute)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import DCF_SCRIPT, run_script


# ---------------------------------------------------------------------------
# Smoke
# ---------------------------------------------------------------------------


def test_help_runs(runner):
    res = runner(DCF_SCRIPT, "--help")
    assert res.returncode == 0
    assert "DCF" in res.stdout or "dcf" in res.stdout.lower() or "input" in res.stdout.lower()


def test_smoke_aapl(runner, fixtures_dir):
    res = runner(DCF_SCRIPT, "--input", str(fixtures_dir / "aapl_memo_fetch.json"))
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["ticker"] == "AAPL"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_schema_top_level_keys(runner, fixtures_dir):
    res = runner(DCF_SCRIPT, "--input", str(fixtures_dir / "aapl_memo_fetch.json"))
    payload = json.loads(res.stdout)
    for key in (
        "ticker",
        "intrinsic_value",
        "sensitivity_table",
        "verdict_thresholds",
        "assumptions",
        "warnings",
        "_provenance",
    ):
        assert key in payload, f"missing top-level key: {key}"
    iv = payload["intrinsic_value"]
    assert {"low", "mid", "high"} <= set(iv.keys())
    # Bear ≤ mid ≤ bull (with the synthetic AAPL fixture in the normal regime)
    assert iv["low"] <= iv["mid"] <= iv["high"]
    # Provenance shape
    prov = payload["_provenance"]
    for key in ("input_path", "computed_at", "framework", "layer"):
        assert key in prov
    # Types
    assert isinstance(payload["warnings"], list)
    assert isinstance(payload["assumptions"], dict)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_missing_input_file(runner, tmp_path):
    res = runner(DCF_SCRIPT, "--input", str(tmp_path / "does_not_exist.json"))
    assert res.returncode != 0
    # Error reported on stderr as JSON
    assert "not found" in res.stderr.lower() or "error" in res.stderr.lower()


def test_malformed_json(runner, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json")
    res = runner(DCF_SCRIPT, "--input", str(bad))
    assert res.returncode != 0
    assert "json" in res.stderr.lower() or "error" in res.stderr.lower()


def test_short_revenue_series_does_not_crash(runner, fixtures_dir):
    """< 3 revenue points: CAGR returns None → falls through to fallback. No crash."""
    res = runner(DCF_SCRIPT, "--input", str(fixtures_dir / "dcf_short_revenue.json"))
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert "intrinsic_value" in payload


# ---------------------------------------------------------------------------
# Skill-specific assertions
# ---------------------------------------------------------------------------


def test_brk_a_low_shares_warning(runner, fixtures_dir):
    """BRK.A-style ~550K shares → emits low-shares warning, NOT 1e6× misclassification."""
    res = runner(DCF_SCRIPT, "--input", str(fixtures_dir / "brk_a_low_shares.json"))
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    warnings = " ".join(payload.get("warnings", []))
    assert "shares_outstanding looks suspiciously small" in warnings
    # Sanity: per-share intrinsic should be in the 100K-10M $ range, not 1e3 (mis-classified-as-millions).
    mid = payload["intrinsic_value"]["mid"]
    assert mid > 50_000, f"intrinsic mid {mid} suspiciously low — possible 1e6× misclassification"


def test_degenerate_wacc_terminal_g_warning(runner, fixtures_dir):
    """WACC ≤ terminal_g → degenerate warning fires."""
    res = runner(
        DCF_SCRIPT,
        "--input", str(fixtures_dir / "aapl_memo_fetch.json"),
        "--wacc", "0.03",
        "--terminal-g", "0.04",
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    warnings = " ".join(payload.get("warnings", []))
    assert "terminal_g" in warnings.lower() and "wacc" in warnings.lower()


def test_terminal_g_exceeds_4pct_warning(runner, fixtures_dir):
    res = runner(
        DCF_SCRIPT,
        "--input", str(fixtures_dir / "aapl_memo_fetch.json"),
        "--terminal-g", "0.05",
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    warnings = " ".join(payload.get("warnings", []))
    assert "terminal_g > 4%" in warnings or "double-counting" in warnings


def test_high_growth_warning(runner, fixtures_dir):
    res = runner(
        DCF_SCRIPT,
        "--input", str(fixtures_dir / "aapl_memo_fetch.json"),
        "--growth-1-5", "0.25",
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    warnings = " ".join(payload.get("warnings", []))
    assert "growth_1_5 > 20%" in warnings or "ROIC" in warnings


def test_per_share_sane_magnitude_absolute_currency_input(runner, fixtures_dir):
    """data-markets emits absolute-currency financials (not $M) — see
    pack_tw.py:264 `"unit": "TWD"` absolute, verified across all 5 markets.
    dcf_compute.py must NOT apply a $M->$ conversion factor on top of an
    already-absolute input, or per-share intrinsic value comes out ~1e6x
    too high (2330.TW repro: mid=1,685,938,388.84 instead of ~1685.94).
    """
    res = runner(DCF_SCRIPT, "--input", str(fixtures_dir / "dcf_tw_absolute_currency.json"))
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    mid = payload["intrinsic_value"]["mid"]
    assert 50 <= mid <= 20000, (
        f"intrinsic mid {mid} outside plausible per-share band — "
        "likely a $M->$ unit-conversion bug on already-absolute-currency input"
    )


def test_sensitivity_grid_is_3x3(runner, fixtures_dir):
    res = runner(DCF_SCRIPT, "--input", str(fixtures_dir / "aapl_memo_fetch.json"))
    payload = json.loads(res.stdout)
    sens = payload["sensitivity_table"]
    assert len(sens["wacc_axis"]) == 3
    assert len(sens["terminal_g_axis"]) == 3
    assert len(sens["table"]) == 3
    for row in sens["table"]:
        assert len(row) == 3
    # 9 cells total
    flat = [c for row in sens["table"] for c in row]
    assert len(flat) == 9


# ---------------------------------------------------------------------------
# rule_verdict — mechanical BUY/HOLD/SELL application (moved out of the
# downstream memo-writing LLM's hands and into deterministic code)
# ---------------------------------------------------------------------------


def test_rule_verdict_sell_when_price_above_sell_threshold(runner, fixtures_dir):
    """AAPL fixture: current_price 175.0 > sell_threshold 165.02 -> SELL."""
    res = runner(DCF_SCRIPT, "--input", str(fixtures_dir / "aapl_memo_fetch.json"))
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    vt = payload["verdict_thresholds"]
    assert vt["rule_verdict"] == "SELL"
    assert vt["rule_verdict_basis"]["price"] == payload["current_price"]
    assert vt["rule_verdict_basis"]["compared_to"]["sell_threshold"] == vt["sell_threshold"]
    assert vt["rule_verdict_basis"]["compared_to"]["buy_threshold_grade_a"] == vt["buy_threshold_grade_a"]


def test_rule_verdict_hold_when_price_between_buy_a_and_hold_threshold(runner, fixtures_dir):
    """current_price 150.0 falls between buy_threshold_grade_a (100.45) and
    hold_threshold (165.02) -> HOLD."""
    res = runner(DCF_SCRIPT, "--input", str(fixtures_dir / "dcf_rule_verdict_hold.json"))
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    vt = payload["verdict_thresholds"]
    assert vt["buy_threshold_grade_a"] < payload["current_price"] <= vt["hold_threshold"]
    assert vt["rule_verdict"] == "HOLD"


def test_rule_verdict_buy_when_price_at_or_below_buy_threshold_grade_a(runner, fixtures_dir):
    """current_price 90.0 <= buy_threshold_grade_a (100.45) -> BUY string,
    grading left to the analyst per the existing `rule` text."""
    res = runner(DCF_SCRIPT, "--input", str(fixtures_dir / "dcf_rule_verdict_buy.json"))
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    vt = payload["verdict_thresholds"]
    assert payload["current_price"] <= vt["buy_threshold_grade_a"]
    assert vt["rule_verdict"] == "BUY (grade per analyst conviction)"


# ---------------------------------------------------------------------------
# Financial-sector refusal guard — sector_class="financial" canonical (fh/basi/
# bd/ins) omits revenue/total_debt on purpose; DCF must refuse cleanly instead
# of raising ValueError, so the memo's Phase-3 dcf.json artifact gate is met.
# ---------------------------------------------------------------------------


def test_financial_sector_emits_not_applicable_clean_exit(runner, fixtures_dir):
    """sector_class=financial + no income_statement.revenue -> structured
    not_applicable result, exit 0 (NOT a ValueError crash)."""
    res = runner(DCF_SCRIPT, "--input", str(fixtures_dir / "dcf_financial_sector.json"))
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload.get("not_applicable") == "financial-sector"
    assert isinstance(payload.get("reason"), str) and payload["reason"]


def test_rule_verdict_null_when_current_price_absent(runner, fixtures_dir):
    """No current_price in input -> rule_verdict must be null, never guessed."""
    res = runner(DCF_SCRIPT, "--input", str(fixtures_dir / "dcf_rule_verdict_no_price.json"))
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    vt = payload["verdict_thresholds"]
    assert payload["current_price"] is None
    assert vt["rule_verdict"] is None
    assert vt.get("rule_verdict_basis") is None
