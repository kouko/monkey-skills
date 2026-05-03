"""test_data_kr.py — contract tests for skills/data-kr/scripts/pack.py.

Coverage:
  * Pure-logic: normalize_ticker() auto-suffix rules (NO network)
  * 5 pack types against 005930.KS (Samsung) — network
  * BOK ECOS-KEYSTAT regime-pack via FinanceDataReader

Pure-logic tests for ticker auto-suffix do not need network and are
unmarked so they run in offline CI.

Network tests honor $INVESTING_TOOLKIT_CACHE.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = ROOT / "skills" / "data-kr" / "scripts"
PACK = SKILL_SCRIPTS / "pack.py"

TICKER = "005930.KS"  # Samsung Electronics
PEER_TICKERS = "005930.KS,000660.KS"
SCREENER_TICKERS = "005930.KS,000660.KS,005380.KS,051910.KS,068270.KS"


def _load_pack_module():
    spec = importlib.util.spec_from_file_location("data_kr_pack", PACK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Pure-logic: normalize_ticker auto-suffix
# ---------------------------------------------------------------------------


def test_kr_normalize_bare_six_digit_appends_ks():
    """Bare 6-digit numeric ticker → .KS (KOSPI default)."""
    pack = _load_pack_module()
    assert pack.normalize_ticker("005930") == "005930.KS"


def test_kr_normalize_kosdaq_flag_appends_kq():
    """--kosdaq flag → .KQ instead of .KS."""
    pack = _load_pack_module()
    assert pack.normalize_ticker("005930", force_kosdaq=True) == "005930.KQ"


def test_kr_normalize_already_suffixed_passthrough():
    """Already-suffixed ticker → unchanged (uppercase preserved)."""
    pack = _load_pack_module()
    assert pack.normalize_ticker("005930.KS") == "005930.KS"
    assert pack.normalize_ticker("068270.KQ") == "068270.KQ"
    # lowercase normalises to uppercase
    assert pack.normalize_ticker("005930.ks") == "005930.KS"


# ---------------------------------------------------------------------------
# Network — pack contract
# ---------------------------------------------------------------------------


def _run_pack(args: list[str], timeout: int = 600) -> dict:
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


@pytest.mark.network
def test_kr_snapshot_samsung():
    """Snapshot returns the raw yfinance envelope under `price_history`
    (dict) AND a T1-canonical OHLCV list under `history` (list of
    `{date, open, high, low, close, volume}` records). The latter is the
    cross-country symmetric alias used by analysis-* skills; it changed
    from dict to list when data-kr/pack.py adopted the data-us / data-jp
    canonical-OHLCV convention. Fixed per ROADMAP §v2.1.x-g.
    """
    out = _run_pack(["--ticker", TICKER, "--pack", "snapshot"])
    assert out["pack"] == "snapshot"
    assert out["country"] == "kr"
    assert out["ticker"] == TICKER
    assert isinstance(out.get("info"), dict)
    assert isinstance(out.get("price_history"), dict), (
        f"snapshot missing price_history (raw yfinance envelope); "
        f"top keys: {sorted(out.keys())}"
    )
    history = out.get("history")
    assert isinstance(history, list), (
        f"snapshot.history must be a list of OHLCV records "
        f"(cross-country symmetric T1 alias), got {type(history).__name__}"
    )
    assert history, "snapshot.history is empty"
    first = history[0]
    for field in ("date", "open", "high", "low", "close", "volume"):
        assert field in first, (
            f"history[0] missing field {field!r}; got keys {sorted(first.keys())}"
        )
    prov = out.get("_provenance", {})
    assert "Tier 2" in prov.get("tier", "")  # yfinance Tier 2 by design


@pytest.mark.network
def test_kr_memo_fetch_samsung_tier_2():
    """Korea memo-fetch is Tier 2 only (DART deferred)."""
    out = _run_pack(["--ticker", TICKER, "--pack", "memo-fetch"])
    assert out["pack"] == "memo-fetch"
    assert out["tier"] == "Tier 2 only"
    assert "financials_annual" in out
    assert "financials_quarterly" in out
    prov = out.get("_provenance", {})
    assert prov.get("primary_source_status") == "deferred"


@pytest.mark.network
def test_kr_comps_multiples_single():
    out = _run_pack(["--ticker", TICKER, "--pack", "comps-multiples"])
    assert out["pack"] == "comps-multiples"
    info = out.get("info", {})
    assert TICKER in info, f"comps-multiples missing ticker {TICKER}"


@pytest.mark.network
def test_kr_screener_batch():
    out = _run_pack(["--tickers", SCREENER_TICKERS, "--pack", "screener-batch"])
    assert out["pack"] == "screener-batch"
    assert set(out["tickers"]) == set(SCREENER_TICKERS.split(","))
    assert "batch" in out


@pytest.mark.network
def test_kr_regime_pack():
    """BOK ECOS-KEYSTAT via fdr_client across configured groups."""
    out = _run_pack(["--pack", "regime-pack", "--indicators", "rates,inflation"])
    assert out["pack"] == "regime-pack"
    assert out["country"] == "kr"
    assert set(out["groups_requested"]) == {"rates", "inflation"}
    data = out.get("data", {})
    assert "rates" in data
    assert "inflation" in data
    prov = out.get("_provenance", {})
    assert prov.get("primary_source_status") == "available"
