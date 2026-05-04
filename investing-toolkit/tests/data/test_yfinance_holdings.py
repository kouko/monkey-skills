"""Unit tests for yfinance_client.get_holdings — no network."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "skills" / "data-us" / "scripts"


def _import_yf_client(monkeypatch):
    """Re-import yfinance_client with a fake yfinance module so no network is touched."""
    fake_yf = MagicMock(name="yfinance_module")
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    if "yfinance_client" in sys.modules:
        del sys.modules["yfinance_client"]
    return importlib.import_module("yfinance_client"), fake_yf


def test_get_holdings_returns_holdings_weights_for_etf(monkeypatch, tmp_path):
    yf_client, fake_yf = _import_yf_client(monkeypatch)
    monkeypatch.setattr(yf_client, "get_cache_path",
                        lambda *a, **kw: tmp_path / "holdings.json")

    ticker_mock = MagicMock(name="Ticker")
    holdings_mock = MagicMock(name="funds_data")
    holdings_df = MagicMock(name="top_holdings_df")
    holdings_df.to_dict.return_value = {
        "Holding Percent": {"AAPL": 0.0712, "MSFT": 0.0654, "NVDA": 0.0432},
    }
    holdings_mock.top_holdings = holdings_df
    ticker_mock.funds_data = holdings_mock
    fake_yf.Ticker.return_value = ticker_mock

    out = yf_client.get_holdings("XLK")
    assert out["ticker"] == "XLK"
    assert {h["ticker"] for h in out["holdings"]} == {"AAPL", "MSFT", "NVDA"}
    aapl = next(h for h in out["holdings"] if h["ticker"] == "AAPL")
    assert aapl["weight"] == pytest.approx(0.0712)


def test_get_holdings_non_etf_returns_empty_list(monkeypatch, tmp_path):
    yf_client, fake_yf = _import_yf_client(monkeypatch)
    monkeypatch.setattr(yf_client, "get_cache_path",
                        lambda *a, **kw: tmp_path / "holdings.json")
    ticker_mock = MagicMock(name="Ticker")
    ticker_mock.funds_data = None  # non-fund tickers expose no funds_data
    fake_yf.Ticker.return_value = ticker_mock
    out = yf_client.get_holdings("AAPL")
    assert out["ticker"] == "AAPL"
    assert out["holdings"] == []
    assert "non_fund" in (out.get("warnings") or [""])[0]
