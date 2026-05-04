"""Unit tests for etf_aggregator — no network. Uses fixture holdings + fixture
memo-fetch packs to drive deterministic compute.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "analysis-comps" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def etf_aggregator(monkeypatch):
    """Import etf_aggregator and patch fetch_holdings + fetch_memo_fetch to
    return fixture-backed data."""
    if "etf_aggregator" in sys.modules:
        del sys.modules["etf_aggregator"]
    mod = importlib.import_module("etf_aggregator")

    holdings_fixture = json.loads((FIXTURES / "etf_xlk_holdings_minimal.json").read_text())
    aapl_memo = json.loads((FIXTURES / "memo_fetch_aapl_minimal.json").read_text())
    msft_memo = json.loads((FIXTURES / "memo_fetch_msft_minimal.json").read_text())

    def _fake_holdings(etf):
        assert etf == "XLK"
        return holdings_fixture

    def _fake_memo(ticker):
        return {"AAPL": aapl_memo, "MSFT": msft_memo}[ticker]

    monkeypatch.setattr(mod, "fetch_holdings", _fake_holdings)
    monkeypatch.setattr(mod, "fetch_memo_fetch", _fake_memo)
    return mod


def test_aggregate_etf_returns_required_keys(etf_aggregator):
    out = etf_aggregator.aggregate_etf("XLK")
    assert out["etf"] == "XLK"
    assert out["schema_id"] == "tech-saas"  # XLK→tech-saas per etf-schema-map
    assert isinstance(out.get("as_of"), str)
    assert isinstance(out["multiples"], dict)
    assert isinstance(out["indicators"], dict)
    assert "_meta" in out
    assert out["_meta"]["holdings_count"] == 2
    assert out["_meta"]["weight_coverage_pct"] == pytest.approx(100.0)


def test_aggregate_etf_weighted_average_multiples(etf_aggregator):
    """priceToSales = marketCap / revenue[0]. (XLK→tech-saas schema; P/B excluded
    by design — intangibles-heavy SaaS books don't reflect economic value.)

    AAPL: 3e12 / 4e11 = 7.5
    MSFT: 2.5e12 / 2.3e11 ≈ 10.870
    Weighted (0.6 AAPL + 0.4 MSFT): 0.6*7.5 + 0.4*10.870 ≈ 8.848
    """
    out = etf_aggregator.aggregate_etf("XLK")
    ps = out["multiples"].get("priceToSales")
    assert ps is not None
    assert ps == pytest.approx(0.6 * (3e12 / 4e11) + 0.4 * (2.5e12 / 2.3e11), rel=1e-3)


@pytest.fixture
def xlf_aggregator(monkeypatch):
    if "etf_aggregator" in sys.modules:
        del sys.modules["etf_aggregator"]
    mod = importlib.import_module("etf_aggregator")
    holdings = json.loads((FIXTURES / "etf_xlf_holdings_minimal.json").read_text())
    memos = {
        "JPM": json.loads((FIXTURES / "memo_fetch_jpm_minimal.json").read_text()),
        "MET": json.loads((FIXTURES / "memo_fetch_met_minimal.json").read_text()),
        "BLK": json.loads((FIXTURES / "memo_fetch_blk_minimal.json").read_text()),
    }
    monkeypatch.setattr(mod, "fetch_holdings", lambda etf: holdings)
    monkeypatch.setattr(mod, "fetch_memo_fetch", lambda t: memos[t])
    return mod


def test_xlf_aggregate_uses_bank_schema(xlf_aggregator):
    """XLF maps to bank schema; aggregate exposes bank schema's multiples + indicators."""
    out = xlf_aggregator.aggregate_etf("XLF")
    assert out["schema_id"] == "bank"
    # bank schema multiples: trailingPE, forwardPE, priceToBook, priceToTangibleBook
    assert set(out["multiples"].keys()) == {"trailingPE", "forwardPE", "priceToBook", "priceToTangibleBook"}
    # bank schema indicators: ROE (only)
    assert set(out["indicators"].keys()) == {"ROE"}


def test_xlf_per_holding_schema_dispatch(xlf_aggregator):
    """JPM→bank, MET→insurance, BLK→asset-manager — verify per-holding schema
    dispatch counts surface in `_meta.schema_dispatch`. The ETF aggregate output
    is keyed by XLF's mapped schema (bank), so multiples like `priceToBook` are
    averaged across whichever holdings' own schemas also include `priceToBook`
    (all 3 financial-services schemas do)."""
    out = xlf_aggregator.aggregate_etf("XLF")
    dispatch = out["_meta"]["schema_dispatch"]
    assert dispatch["bank"] == 1            # JPM
    assert dispatch["insurance"] == 1       # MET
    assert dispatch["asset-manager"] == 1   # BLK
    # priceToBook averaged over all 3 (every holding's schema includes it).
    assert out["multiples"]["priceToBook"] is not None


def test_outlier_drop_high_value(monkeypatch):
    """Holding with priceToSales = 250000 (way out of [0, 200]) → dropped from
    aggregate; `_meta.outliers_dropped` records the count.

    (XLK→tech-saas schema includes priceToSales but excludes priceToBook by
    design — intangibles-heavy SaaS books don't reflect economic value. So we
    exercise the outlier-drop code path against priceToSales.)
    """
    if "etf_aggregator" in sys.modules:
        del sys.modules["etf_aggregator"]
    mod = importlib.import_module("etf_aggregator")
    holdings = {"holdings": [
        {"ticker": "AAPL", "weight": 0.5},
        {"ticker": "MSFT", "weight": 0.5},
    ]}
    aapl_memo = json.loads((FIXTURES / "memo_fetch_aapl_minimal.json").read_text())
    # Cook MSFT to produce P/S > 200: tiny revenue inflates P/S.
    msft_memo = json.loads((FIXTURES / "memo_fetch_msft_minimal.json").read_text())
    msft_memo["income_statement"]["revenue"] = [10_000_000]  # 10M only
    monkeypatch.setattr(mod, "fetch_holdings", lambda etf: holdings)
    monkeypatch.setattr(mod, "fetch_memo_fetch",
                        lambda t: {"AAPL": aapl_memo, "MSFT": msft_memo}[t])
    out = mod.aggregate_etf("XLK")
    # AAPL P/S = 3e12 / 4e11 = 7.5; MSFT P/S = 2.5e12 / 1e7 = 250000 → dropped
    assert out["_meta"]["outliers_dropped"].get("priceToSales") == 1
    # priceToSales average is now AAPL only → 7.5 (weight normalizes over survivors)
    assert out["multiples"]["priceToSales"] == pytest.approx(3e12 / 4e11, rel=1e-3)


def test_weight_coverage_partial_when_holding_skipped(monkeypatch):
    """When a holding fetch raises, it's logged into skipped_holdings;
    weight_coverage_pct reflects only successfully-fetched weight."""
    if "etf_aggregator" in sys.modules:
        del sys.modules["etf_aggregator"]
    mod = importlib.import_module("etf_aggregator")
    holdings = {"holdings": [
        {"ticker": "AAPL", "weight": 0.6},
        {"ticker": "MSFT", "weight": 0.4},
    ]}
    aapl_memo = json.loads((FIXTURES / "memo_fetch_aapl_minimal.json").read_text())

    def _fake_memo(t):
        if t == "MSFT":
            raise RuntimeError("simulated fetch failure")
        return aapl_memo

    monkeypatch.setattr(mod, "fetch_holdings", lambda etf: holdings)
    monkeypatch.setattr(mod, "fetch_memo_fetch", _fake_memo)
    out = mod.aggregate_etf("XLK")
    assert out["_meta"]["weight_coverage_pct"] == pytest.approx(60.0)  # AAPL only
    assert any(s["ticker"] == "MSFT" for s in out["_meta"]["skipped_holdings"])
