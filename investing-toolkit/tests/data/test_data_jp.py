"""test_data_jp.py — contract tests for skills/data-jp/scripts/pack.py.

Coverage:
  * 5 pack types against 7203 (Toyota)
  * EDINET tier-routing: without EDINET_API_KEY, memo-fetch falls back to
    yfinance financials with `_provenance.tier_label = "Tier 2 fallback"`
    and `upgrade_hint` URL pointing at EDINET registration page.
  * 4-digit ticker (`7203`) auto-appends `.T` for yfinance — the fetched
    snapshot exposes `yf_ticker = "7203.T"` and `ticker = "7203"`.

Network: pack tests hit yfinance / TDnet / BOJ / estat / ECB. Marked
@pytest.mark.network.

Cache: honors $INVESTING_TOOLKIT_CACHE.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "skills" / "data-jp" / "scripts" / "pack.py"

TICKER = "7203"  # Toyota — 4-digit JP code (no suffix)
PEER_TICKERS = "7203,6758,9984"
SCREENER_TICKERS = "7203,6758,9984,8306,7974"


def _run_pack(args: list[str], extra_env: dict | None = None,
              timeout: int = 600) -> tuple[dict, str]:
    """Invoke pack.py and return (parsed JSON, stderr). Asserts exit 0."""
    cmd = ["uv", "run", str(PACK), *args]
    env = {**os.environ}
    if extra_env is not None:
        # Allow tests to set/clear EDINET_API_KEY
        for k, v in extra_env.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    assert proc.returncode == 0, (
        f"pack.py exit={proc.returncode}\nstderr (tail): {proc.stderr[-1500:]}"
    )
    try:
        return json.loads(proc.stdout), proc.stderr
    except json.JSONDecodeError as e:
        pytest.fail(f"non-JSON stdout: {e}\nhead: {proc.stdout[:500]}")


# ---------------------------------------------------------------------------
# Per-pack contract
# ---------------------------------------------------------------------------


@pytest.mark.network
def test_jp_snapshot_toyota_auto_t_suffix():
    """4-digit `7203` auto-appends `.T`; snapshot returns yf_ticker + bare."""
    out, _ = _run_pack(["--ticker", TICKER, "--pack", "snapshot"])
    assert out["pack"] == "snapshot"
    assert out["ticker"] == "7203", "bare ticker should pass through"
    assert out["yf_ticker"] == "7203.T", "yf ticker should auto-append .T"
    assert "fetched_at" in out
    # snapshot composition
    assert isinstance(out.get("info"), dict)
    assert isinstance(out.get("price_history"), dict)
    assert "timely_disclosures" in out  # TDnet — always Tier 1, no key
    prov = out.get("_provenance", {})
    assert prov.get("tier") == "tier_1"


@pytest.mark.network
def test_jp_memo_fetch_no_edinet_key_falls_back_to_tier2():
    """Without EDINET_API_KEY: memo-fetch surfaces Tier 2 fallback envelope."""
    out, _ = _run_pack(
        ["--ticker", TICKER, "--pack", "memo-fetch"],
        extra_env={"EDINET_API_KEY": None},  # explicitly unset
    )
    assert out["pack"] == "memo-fetch"
    assert out["ticker"] == "7203"
    assert out["yf_ticker"] == "7203.T"

    # Tier 2 fallback contract per skills/data-jp/scripts/pack.py
    fundamentals = out.get("fundamentals")
    assert isinstance(fundamentals, dict)
    assert fundamentals.get("tier") == "tier_2"
    assert fundamentals.get("tier_label") == "Tier 2 fallback"
    # yfinance financials annual + quarterly
    assert "annual" in fundamentals
    assert "quarterly" in fundamentals

    prov = out.get("_provenance", {})
    assert prov.get("tier_label") == "Tier 2 fallback"
    upgrade = prov.get("upgrade_hint", "")
    # upgrade_hint should mention EDINET_API_KEY and contain the registration URL
    assert "EDINET_API_KEY" in upgrade
    assert "edinet" in upgrade.lower()
    assert "http" in upgrade  # URL embedded


@pytest.mark.network
def test_jp_comps_multiples_single():
    """comps-multiples returns tickers list with multiples block."""
    out, _ = _run_pack(["--ticker", TICKER, "--pack", "comps-multiples"])
    assert out["pack"] == "comps-multiples"
    tickers = out.get("tickers")
    assert isinstance(tickers, list) and len(tickers) >= 1
    block = tickers[0]
    assert block["ticker"] == "7203"
    assert block["yf_ticker"] == "7203.T"
    assert isinstance(block.get("multiples"), dict)


@pytest.mark.network
def test_jp_screener_batch():
    """screener-batch returns batch info + history."""
    out, _ = _run_pack(["--tickers", SCREENER_TICKERS, "--pack", "screener-batch"])
    assert out["pack"] == "screener-batch"
    assert "info_batch" in out
    assert "history_batch" in out
    assert set(out.get("yf_tickers", [])) == {f"{t}.T" for t in SCREENER_TICKERS.split(",")}


@pytest.mark.network
def test_jp_regime_pack():
    """regime-pack returns BOJ + estat + ECB groups."""
    out, _ = _run_pack(["--pack", "regime-pack"])
    assert out["pack"] == "regime-pack"
    groups = out.get("groups", {})
    assert {"rates", "inflation", "real_rates"}.issubset(groups.keys())
    prov = out.get("_provenance", {})
    assert prov.get("tier") == "tier_a"
