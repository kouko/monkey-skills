"""test_data_us.py — contract tests for skills/data-us/scripts/pack.py.

Smoke-tests all 5 pack types against AAPL via subprocess.run. Asserts:
  * exit 0
  * stdout is valid JSON
  * required top-level keys (pack, ticker, fetched_at) present
  * pack-shape fields specific to each pack type
  * snapshot has yfinance + sec_edgar provenance markers (memo-fetch carries SEC)
  * regime-pack returns FRED series (rates / inflation / growth groups)

Network: every test in this file hits yfinance / SEC EDGAR / FRED. Marked
@pytest.mark.network and skipped in offline CI.

Cache: honors $INVESTING_TOOLKIT_CACHE for snapshot warming so memo-fetch
re-uses yfinance info. Run with:

    INVESTING_TOOLKIT_CACHE=/tmp/test-cache \
        uv run --with pytest pytest tests/data/test_data_us.py -v -m network
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "skills" / "data-us" / "scripts" / "pack.py"

TICKER = "AAPL"
PEER_TICKERS = "AAPL,MSFT,GOOGL"
SCREENER_TICKERS = "AAPL,MSFT,GOOGL,META,AMZN"


def _run_pack(args: list[str], timeout: int = 600) -> dict:
    """Invoke pack.py and return parsed JSON. Asserts exit 0."""
    cmd = ["uv", "run", str(PACK), *args]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ},
    )
    assert proc.returncode == 0, (
        f"pack.py exit={proc.returncode}\nstderr (tail): {proc.stderr[-1500:]}"
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"non-JSON stdout: {e}\nhead: {proc.stdout[:500]}")


# ---------------------------------------------------------------------------
# Per-pack contract
# ---------------------------------------------------------------------------


@pytest.mark.network
def test_us_snapshot_aapl():
    """snapshot has company_info + price_history; yfinance provenance reachable."""
    out = _run_pack(["--ticker", TICKER, "--pack", "snapshot"])
    assert out["pack"] == "snapshot"
    assert out["ticker"] == TICKER
    assert "fetched_at" in out
    assert isinstance(out.get("company_info"), dict), "snapshot missing company_info"
    assert isinstance(out.get("price_history"), dict), "snapshot missing price_history"
    # yfinance info shape: top-level dict with at least `ticker` key or fields
    info = out["company_info"]
    assert info.get("ticker") or info.get("symbol") or "shortName" in info or "longName" in info, (
        f"company_info missing identifying fields: keys={list(info)[:20]}"
    )


@pytest.mark.network
def test_us_memo_fetch_aapl_has_sec_provenance():
    """memo-fetch should include sec_filings + sec_facts (SEC EDGAR Tier A)."""
    out = _run_pack(["--ticker", TICKER, "--pack", "memo-fetch"])
    assert out["pack"] == "memo-fetch"
    assert out["ticker"] == TICKER
    assert "fetched_at" in out
    # yfinance side
    assert isinstance(out.get("company_info"), dict)
    # SEC EDGAR side — Tier A
    assert "sec_filings" in out, "memo-fetch missing sec_filings"
    assert "sec_facts" in out, "memo-fetch missing sec_facts"
    # Either filings dict has entries OR carries an error envelope (still
    # surfaces the SEC call shape — failure mode should not silently drop
    # the key).
    filings = out["sec_filings"]
    facts = out["sec_facts"]
    assert isinstance(filings, dict), "sec_filings should be a dict"
    assert isinstance(facts, dict), "sec_facts should be a dict"


@pytest.mark.network
def test_us_comps_multiples_single_aapl():
    """comps-multiples (single) returns multiples block under tickers map."""
    out = _run_pack(["--ticker", TICKER, "--pack", "comps-multiples"])
    assert out["pack"] == "comps-multiples"
    tickers = out.get("tickers")
    assert isinstance(tickers, dict)
    assert TICKER in tickers
    block = tickers[TICKER]
    # at least one multiples key should be probed (None allowed if Yahoo
    # didn't return; the key itself must be present per filter_fields contract)
    multiples_keys = {"trailingPE", "forwardPE", "priceToSales", "priceToBook",
                      "enterpriseToEbitda", "enterpriseToRevenue",
                      "marketCap", "enterpriseValue"}
    assert multiples_keys.issubset(block.keys()), (
        f"comps-multiples block missing keys: "
        f"{sorted(multiples_keys - set(block.keys()))}"
    )


@pytest.mark.network
def test_us_screener_batch():
    """screener-batch returns per-ticker lightweight fields."""
    out = _run_pack(["--tickers", SCREENER_TICKERS, "--pack", "screener-batch"])
    assert out["pack"] == "screener-batch"
    tickers = out.get("tickers")
    assert isinstance(tickers, dict)
    # All requested tickers should have an entry (even if individual fields
    # are None due to upstream coverage gaps).
    for t in SCREENER_TICKERS.split(","):
        assert t in tickers, f"screener-batch missing ticker {t}"
    # screener fields whitelist contract
    sample_ticker = next(iter(tickers))
    sample = tickers[sample_ticker]
    expected = {"trailingPE", "priceToBook", "marketCap", "dividendYield",
                "beta", "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
                "regularMarketPrice", "sector", "industry", "shortName"}
    assert expected.issubset(sample.keys()), (
        f"screener fields missing: {sorted(expected - set(sample.keys()))}"
    )


@pytest.mark.network
def test_us_regime_pack_fred_groups():
    """regime-pack returns FRED groups with observation arrays."""
    out = _run_pack(["--pack", "regime-pack"])
    assert out["pack"] == "regime-pack"
    assert out["country"] == "US"
    groups = out.get("groups")
    assert isinstance(groups, dict)
    # Mirrors REGIME_SERIES_GROUPS in pack.py
    expected_groups = {"rates", "inflation", "growth", "nowcast", "wei",
                       "real_rates", "swap_spreads"}
    assert expected_groups.issubset(groups.keys()), (
        f"missing FRED groups: {sorted(expected_groups - set(groups.keys()))}"
    )
    # rates group should hit DGS10 + FEDFUNDS — fred_client returns
    # {"results": {"DGS10": {...}}, ...} or {"observations": [...]} depending
    # on mode. Just assert a dict with non-empty content.
    rates = groups["rates"]
    assert isinstance(rates, dict)
    assert rates, "rates group empty"
