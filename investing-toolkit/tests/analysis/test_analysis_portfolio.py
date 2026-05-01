"""Tests for analysis-portfolio/scripts/portfolio_compute.py.

CRITICAL test: bare 4-digit JP ticker `7203` resolves against `7203.T` price.
This is the regression guard from Phase 2 — pre-fix, the position was wrongly
listed in missing_prices.
"""
from __future__ import annotations

import json

import pytest

from conftest import PORTFOLIO_SCRIPT, run_script


def test_help_runs(runner):
    res = runner(PORTFOLIO_SCRIPT, "--help")
    assert res.returncode == 0


def test_smoke(runner, fixtures_dir):
    res = runner(
        PORTFOLIO_SCRIPT,
        "--holdings", str(fixtures_dir / "holdings_simple.csv"),
        "--prices", str(fixtures_dir / "prices_simple.json"),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert "positions" in payload
    assert "totals" in payload


def test_schema(runner, fixtures_dir):
    res = runner(
        PORTFOLIO_SCRIPT,
        "--holdings", str(fixtures_dir / "holdings_simple.csv"),
        "--prices", str(fixtures_dir / "prices_simple.json"),
    )
    payload = json.loads(res.stdout)
    for key in ("positions", "totals", "_provenance"):
        assert key in payload
    totals = payload["totals"]
    for key in (
        "total_cost", "total_market_value", "total_pnl_abs", "total_pnl_ratio",
        "position_count", "max_weight", "max_weight_ticker", "top3_weight",
    ):
        assert key in totals, f"missing totals key: {key}"
    # Provenance
    prov = payload["_provenance"]
    assert prov["skill"] == "analysis-portfolio"
    assert "ticker_resolutions" in prov
    assert "missing_prices" in prov


def test_missing_holdings_file(runner, fixtures_dir, tmp_path):
    res = runner(
        PORTFOLIO_SCRIPT,
        "--holdings", str(tmp_path / "missing.csv"),
        "--prices", str(fixtures_dir / "prices_simple.json"),
    )
    assert res.returncode != 0


def test_missing_prices_file(runner, fixtures_dir, tmp_path):
    res = runner(
        PORTFOLIO_SCRIPT,
        "--holdings", str(fixtures_dir / "holdings_simple.csv"),
        "--prices", str(tmp_path / "missing.json"),
    )
    assert res.returncode != 0


def test_malformed_prices_json(runner, fixtures_dir, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    res = runner(
        PORTFOLIO_SCRIPT,
        "--holdings", str(fixtures_dir / "holdings_simple.csv"),
        "--prices", str(bad),
    )
    assert res.returncode != 0


# ---------------------------------------------------------------------------
# CRITICAL: JP/KR bare-ticker resolution (Phase 2 regression guard)
# ---------------------------------------------------------------------------


def test_jp_bare_ticker_resolves_against_T_suffix(runner, fixtures_dir):
    """Bare 4-digit JP ticker `7203` MUST resolve against `7203.T` price.

    This is the most important regression guard from Phase 2. Pre-fix, `7203`
    would land in missing_prices because the resolver only did exact-match.
    """
    res = runner(
        PORTFOLIO_SCRIPT,
        "--holdings", str(fixtures_dir / "holdings_jp_bare.csv"),
        "--prices", str(fixtures_dir / "prices_jp_with_suffix.json"),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)

    # 7203 must NOT be in missing_prices
    missing = payload["_provenance"]["missing_prices"]
    assert "7203" not in missing, f"7203 should resolve via .T suffix, but it's in missing: {missing}"

    # 7203 must be a position
    tickers = [p["ticker"] for p in payload["positions"]]
    assert "7203" in tickers

    # ticker_resolutions must log the rewrite
    resolutions = payload["_provenance"]["ticker_resolutions"]
    jp_resolution = next(
        (r for r in resolutions if r["input"] == "7203"), None
    )
    assert jp_resolution is not None
    assert jp_resolution["resolved"] == "7203.T"


def test_kr_bare_ticker_resolves_against_KS_suffix(runner, fixtures_dir):
    """Bare 6-digit KR ticker `005930` resolves against `005930.KS`."""
    res = runner(
        PORTFOLIO_SCRIPT,
        "--holdings", str(fixtures_dir / "holdings_jp_bare.csv"),
        "--prices", str(fixtures_dir / "prices_jp_with_suffix.json"),
    )
    payload = json.loads(res.stdout)
    resolutions = payload["_provenance"]["ticker_resolutions"]
    kr_res = next((r for r in resolutions if r["input"] == "005930"), None)
    assert kr_res is not None
    assert kr_res["resolved"] == "005930.KS"


# ---------------------------------------------------------------------------
# Skill-specific
# ---------------------------------------------------------------------------


def test_missing_price_excludes_from_totals(runner, fixtures_dir):
    """ZZZ_MISSING in holdings has no price → in missing_prices, excluded from totals."""
    res = runner(
        PORTFOLIO_SCRIPT,
        "--holdings", str(fixtures_dir / "holdings_simple.csv"),
        "--prices", str(fixtures_dir / "prices_simple.json"),
    )
    payload = json.loads(res.stdout)
    assert "ZZZ_MISSING" in payload["_provenance"]["missing_prices"]
    tickers = [p["ticker"] for p in payload["positions"]]
    assert "ZZZ_MISSING" not in tickers


def test_pnl_ratio_is_fractional(runner, fixtures_dir):
    """pnl_ratio MUST be in fractional form (0.0–1.0), NOT percent (0–100)."""
    res = runner(
        PORTFOLIO_SCRIPT,
        "--holdings", str(fixtures_dir / "holdings_simple.csv"),
        "--prices", str(fixtures_dir / "prices_simple.json"),
    )
    payload = json.loads(res.stdout)
    # AAPL: cost 150, price 175 → pnl_ratio = 25/150 ≈ 0.1667 (NOT 16.67)
    aapl = next(p for p in payload["positions"] if p["ticker"] == "AAPL")
    assert 0.15 < aapl["pnl_ratio"] < 0.20, (
        f"pnl_ratio {aapl['pnl_ratio']} suggests percent form, expected fractional ~0.1667"
    )
    # totals should also be fractional
    assert -1.0 <= payload["totals"]["total_pnl_ratio"] <= 5.0


def test_top3_weight_in_totals(runner, fixtures_dir):
    res = runner(
        PORTFOLIO_SCRIPT,
        "--holdings", str(fixtures_dir / "holdings_simple.csv"),
        "--prices", str(fixtures_dir / "prices_simple.json"),
    )
    payload = json.loads(res.stdout)
    assert "top3_weight" in payload["totals"]
    assert isinstance(payload["totals"]["top3_weight"], (int, float))


def test_csv_column_aliases(runner, fixtures_dir):
    """CSV columns `shares` / `avg_cost` / `acquired_at` are aliases for
    quantity / cost_basis / purchase_date — holdings_jp_bare.csv uses them."""
    res = runner(
        PORTFOLIO_SCRIPT,
        "--holdings", str(fixtures_dir / "holdings_jp_bare.csv"),
        "--prices", str(fixtures_dir / "prices_jp_with_suffix.json"),
    )
    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    # All 3 holdings should be parsed (none should be dropped due to "missing" cols)
    assert payload["totals"]["position_count"] == 3
    # purchase_date alias survived
    aapl = next((p for p in payload["positions"] if p["ticker"] == "AAPL"), None)
    assert aapl is not None
    assert aapl.get("purchase_date") == "2024-03-10"
