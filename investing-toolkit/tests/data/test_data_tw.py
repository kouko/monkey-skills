"""test_data_tw.py — contract tests for skills/data-tw/scripts/pack.py.

Coverage:
  * Pure-logic: latest_roc_quarter() filing-aware boundary cases (NO network)
  * 5 pack types against 2330.TW (TSMC) — network
  * Wraps yfinance + MOPS + TWSE OpenAPI + FinMind tier envelope contract

Pure-logic tests (ROC quarter math) are NOT marked @pytest.mark.network and
always run, including offline CI.

Network tests honor $INVESTING_TOOLKIT_CACHE.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = ROOT / "skills" / "data-tw" / "scripts"
PACK = SKILL_SCRIPTS / "pack.py"

TICKER = "2330.TW"  # TSMC
PEER_TICKERS = "2330.TW,2454.TW"
SCREENER_TICKERS = "2330.TW,2454.TW,2317.TW,2412.TW,1303.TW"


# ---------------------------------------------------------------------------
# Pure-logic: latest_roc_quarter (no network)
# ---------------------------------------------------------------------------


def _load_pack_module():
    """Import skills/data-tw/scripts/pack.py as a module without invoking CLI."""
    spec = importlib.util.spec_from_file_location("data_tw_pack", PACK)
    module = importlib.util.module_from_spec(spec)
    # pack.py imports with `from __future__ import annotations` and uses
    # only stdlib at import time — safe to exec.
    spec.loader.exec_module(module)
    return module


def test_tw_latest_roc_quarter_boundary_cases():
    """Filing-aware ROC quarter math — exact boundary days the spec calls out.

    Filing deadlines (TWSE/TPEx-listed, consolidated):
      Q4 (年報): by Mar 31 of next year → safe Apr 1+
      Q1:       by May 15 → safe May 16+
      Q2 (半年報): by Aug 14 → safe Aug 15+
      Q3:       by Nov 14 → safe Nov 15+

    Q1 not yet filed on May 1 → fall back to prior-year Q4 (114, 4).
    Q1 filed by May 16 onward → (115, 1).
    Q2 not yet filed on Aug 14 → still (115, 1).
    Q2 filed by Aug 15 onward → (115, 2).
    """
    pack = _load_pack_module()
    fn = pack.latest_roc_quarter

    # 2026 = ROC 115. May 1 is before May 16 buffer → previous-year Q4.
    assert fn(date(2026, 5, 1)) == (114, 4), "Q1 not yet filed → prior-year Q4"

    # May 20 is past May 16 buffer → Q1 filed.
    assert fn(date(2026, 5, 20)) == (115, 1), "Q1 filed by May 16+"

    # Aug 14 still before Aug 15 buffer → Q2 not yet filed (stay at Q1).
    assert fn(date(2026, 8, 14)) == (115, 1), "Q2 not yet filed → stay at Q1"

    # Aug 15 deadline buffer → Q2 filed.
    assert fn(date(2026, 8, 15)) == (115, 2), "Q2 filed by Aug 15+"


# ---------------------------------------------------------------------------
# Network — pack contract tests
# ---------------------------------------------------------------------------


def _run_pack(args: list[str], timeout: int = 900) -> dict:
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
def test_tw_snapshot_tsmc():
    out = _run_pack(["--ticker", TICKER, "--pack", "snapshot"])
    assert out["pack"] == "snapshot"
    assert out["country"] == "TW"
    assert out["ticker"] == TICKER
    norm = out.get("_normalized", {})
    assert norm.get("ticker_code") == "2330"
    assert norm.get("market") == "sii"
    # Multi-source composition — every group dict must exist
    for group in ("yfinance", "mops", "twse", "finmind"):
        assert group in out, f"snapshot missing {group} group"


@pytest.mark.network
def test_tw_memo_fetch_tsmc():
    out = _run_pack(["--ticker", TICKER, "--pack", "memo-fetch"])
    assert out["pack"] == "memo-fetch"
    assert out["country"] == "TW"
    # memo-fetch is snapshot + extra MOPS / TWSE entries
    mops = out.get("mops", {})
    for extra in ("cash_flow", "monthly_revenue", "dividends",
                  "director_holdings", "insider_trades", "announcements"):
        assert extra in mops, f"memo-fetch missing mops.{extra}"
    twse = out.get("twse", {})
    assert "three_investor" in twse
    # SII listing should also have stock_day_history (TWSE /rwd/)
    assert "stock_day_history" in twse, "sii memo-fetch should include TWSE OHLCV"


@pytest.mark.network
def test_tw_comps_multiples_single():
    out = _run_pack(["--ticker", TICKER, "--pack", "comps-multiples"])
    assert out["pack"] == "comps-multiples"
    assert out["country"] == "TW"
    assert TICKER in out.get("tickers", {})
    block = out["tickers"][TICKER]
    assert block.get("_source") == "yfinance"
    assert block.get("_action") == "info-multiples"


@pytest.mark.network
def test_tw_screener_batch():
    out = _run_pack(["--tickers", SCREENER_TICKERS, "--pack", "screener-batch"])
    assert out["pack"] == "screener-batch"
    assert out["country"] == "TW"
    assert isinstance(out.get("yfinance"), dict)
    assert "info_batch" in out["yfinance"]
    assert "history_batch" in out["yfinance"]
    # MOPS company_basic per ticker (Tier A)
    mops = out.get("mops", {})
    for t in SCREENER_TICKERS.split(","):
        assert t in mops, f"screener-batch missing mops.{t}"


@pytest.mark.network
def test_tw_regime_pack():
    out = _run_pack(["--pack", "regime-pack"])
    assert out["pack"] == "regime-pack"
    assert out["country"] == "TW"
    for group in ("cbc", "dgbas", "ndc", "statgov"):
        assert group in out, f"regime-pack missing {group} group"
