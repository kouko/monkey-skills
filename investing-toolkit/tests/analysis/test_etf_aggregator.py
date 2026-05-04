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
