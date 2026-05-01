"""test_data_cn.py — contract tests for skills/data-cn/scripts/pack.py.

Coverage:
  * Pure-logic: _normalise_ticker() auto-suffix heuristic (NO network)
    - 6-digit /6: .SS  (Shanghai 600/601/603/605/688)
    - 6-digit /0: .SZ  (Shenzhen 000/002)
    - 4-digit:   .HK
    - 5-digit:   .HK   (NEW v2.0.0 — leading-zero HK form, e.g. 09988)
    - already-suffixed: passthrough
    - BSE 6-digit /8: stderr warning + passthrough (yfinance has no BSE)
  * 5 pack types against 600519.SS (Kweichow Moutai) — network
  * NBS macro + akshare PBOC/Caixin + FRED USDCNY composition

Pure-logic auto-suffix tests are unmarked (always run, including offline CI).
Network tests honor $INVESTING_TOOLKIT_CACHE.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
from contextlib import redirect_stderr
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = ROOT / "skills" / "data-cn" / "scripts"
PACK = SKILL_SCRIPTS / "pack.py"

TICKER = "600519.SS"  # Kweichow Moutai
PEER_TICKERS = "600519.SS,000858.SZ"
SCREENER_TICKERS = "600519.SS,000858.SZ,601318.SS,000333.SZ,300750.SZ"


def _load_pack_module():
    spec = importlib.util.spec_from_file_location("data_cn_pack", PACK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Pure-logic: _normalise_ticker auto-suffix heuristic
# ---------------------------------------------------------------------------


def test_cn_normalise_six_digit_starting_with_6_appends_ss():
    pack = _load_pack_module()
    assert pack._normalise_ticker("600519") == "600519.SS"
    assert pack._normalise_ticker("601318") == "601318.SS"
    assert pack._normalise_ticker("603259") == "603259.SS"
    assert pack._normalise_ticker("688981") == "688981.SS"


def test_cn_normalise_six_digit_starting_with_0_appends_sz():
    pack = _load_pack_module()
    assert pack._normalise_ticker("000858") == "000858.SZ"
    assert pack._normalise_ticker("000001") == "000001.SZ"
    assert pack._normalise_ticker("002594") == "002594.SZ"
    assert pack._normalise_ticker("300750") == "300750.SZ"


def test_cn_normalise_four_digit_appends_hk():
    pack = _load_pack_module()
    assert pack._normalise_ticker("0700") == "0700.HK"
    assert pack._normalise_ticker("0005") == "0005.HK"


def test_cn_normalise_five_digit_appends_hk():
    """NEW v2.0.0 capability — 5-digit HK leading-zero form (e.g. 09988)."""
    pack = _load_pack_module()
    assert pack._normalise_ticker("09988") == "09988.HK"
    assert pack._normalise_ticker("02318") == "02318.HK"
    assert pack._normalise_ticker("03690") == "03690.HK"


def test_cn_normalise_already_suffixed_passthrough():
    pack = _load_pack_module()
    assert pack._normalise_ticker("600519.SS") == "600519.SS"
    assert pack._normalise_ticker("000858.SZ") == "000858.SZ"
    assert pack._normalise_ticker("0700.HK") == "0700.HK"
    # lowercase → uppercase
    assert pack._normalise_ticker("600519.ss") == "600519.SS"


def test_cn_normalise_bse_six_digit_warns_and_passthrough():
    """BSE codes (4xx/8xx 6-digit) — yfinance has no BSE; warn + passthrough."""
    pack = _load_pack_module()
    buf = io.StringIO()
    with redirect_stderr(buf):
        out = pack._normalise_ticker("830799")
    assert out == "830799", "BSE ticker should pass through unchanged"
    assert "BSE" in buf.getvalue(), "expected stderr warning to mention BSE"


# ---------------------------------------------------------------------------
# Network — pack contract
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
def test_cn_snapshot_moutai():
    out = _run_pack(["--ticker", TICKER, "--pack", "snapshot"])
    assert out["pack"] == "snapshot"
    assert out["country"] == "CN"
    assert out["ticker"] == TICKER
    assert "yfinance_info" in out
    assert "yfinance_history" in out


@pytest.mark.network
def test_cn_memo_fetch_moutai_tier_2():
    out = _run_pack(["--ticker", TICKER, "--pack", "memo-fetch"])
    assert out["pack"] == "memo-fetch"
    prov = out.get("_provenance", {})
    assert prov.get("tier") == 2
    assert prov.get("primary_source_status") == "deferred"
    assert "yfinance_financials_annual" in out
    assert "yfinance_financials_quarterly" in out


@pytest.mark.network
def test_cn_comps_multiples_single():
    out = _run_pack(["--ticker", TICKER, "--pack", "comps-multiples"])
    assert out["pack"] == "comps-multiples"
    tickers = out.get("tickers", [])
    assert isinstance(tickers, list) and len(tickers) >= 1
    block = tickers[0]
    assert block["ticker"] == TICKER
    assert "multiples" in block


@pytest.mark.network
def test_cn_screener_batch():
    out = _run_pack(["--tickers", SCREENER_TICKERS, "--pack", "screener-batch"])
    assert out["pack"] == "screener-batch"
    assert set(out["tickers"]) == set(SCREENER_TICKERS.split(","))
    assert "yfinance_info_batch" in out
    assert "yfinance_history_batch" in out


@pytest.mark.network
def test_cn_regime_pack():
    """NBS (21) + akshare PBOC/Caixin (8) + FRED USDCNY composition."""
    out = _run_pack(["--pack", "regime-pack"])
    assert out["pack"] == "regime-pack"
    assert out["country"] == "CN"
    for source in ("nbs", "akshare", "fred", "markets"):
        assert source in out, f"regime-pack missing {source} source"
    prov = out.get("_provenance", {})
    assert isinstance(prov.get("nbs_indicators"), list)
    assert isinstance(prov.get("akshare_indicators"), list)
    assert isinstance(prov.get("fred_series"), list)
