#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
pack.py — data-cn Layer 1 facade for investing-toolkit v2.0.0 three-layer.

Composes multi-source pulls into 5 pack types:

  --pack snapshot         Quick overview card (yfinance info + price)
  --pack memo-fetch       Equity memo full data (yfinance financials; CN
                          primary-source disclosure not in scope)
  --pack comps-multiples  Multiples-only (yfinance), single or batch
  --pack screener-batch   Lightweight batch fields (yfinance batch)
  --pack regime-pack      NBS macro (21 presets) + akshare PBOC/Caixin (8) + FRED USDCNY

Tier routing (data-cn):
  - NBS new-SPA API (primary, 21 indicators): nbs_client.py
  - PBOC + SHIBOR + Caixin PMI (aggregator, 8 indicators): akshare_client.py
  - USDCNY cross-rate + FX reserves: fred_client.py
  - .SS (Shanghai) / .SZ (Shenzhen) / .HK individual stocks: yfinance_client.py
    (auto-suffix appended if user passes bare 6-digit code or HK 4-digit code)

Single + batch:
  pack.py --ticker 600519.SS --pack snapshot
  pack.py --tickers 600519.SS,000858.SZ --pack screener-batch
  pack.py --pack regime-pack

Examples:
  uv run pack.py --ticker 600519 --pack snapshot          # auto -> 600519.SS
  uv run pack.py --ticker 000858 --pack snapshot          # auto -> 000858.SZ
  uv run pack.py --ticker 0700 --pack snapshot            # auto -> 0700.HK
  uv run pack.py --ticker 600519.SS --pack comps-multiples
  uv run pack.py --pack regime-pack
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# NBS preset list (21 indicators across 9 groups — see SKILL.md)
NBS_PRESETS = [
    # inflation
    "cpi-yoy", "core-cpi", "ppi-yoy",
    # growth
    "gdp-yoy", "industrial-yoy", "retail-yoy", "fai-yoy",
    # trade
    "exports-yoy", "imports-yoy", "trade-balance",
    # labor
    "urban-unemployment",
    # pmi (NBS official)
    "pmi-manufacturing", "pmi-non-manufacturing", "pmi-composite",
    # money
    "m2-yoy", "m1-yoy",
    # realestate
    "realestate-investment-yoy", "housing-sales-area-yoy",
    "housing-sales-value-yoy", "realestate-funding-yoy",
    # services
    "services-production-yoy",
]

# akshare preset list (8 indicators: PBOC rates + credit + Caixin PMI)
AKSHARE_PRESETS = [
    "lpr-1y", "lpr-5y", "rrr-major", "shibor-3m",
    "shrzgm", "new-loans",
    "caixin-mfg-pmi", "caixin-svc-pmi",
]

# FRED series for CN cross-rate + FX reserves
FRED_SERIES = ["DEXCHUS", "TRESEGCNM052N"]

# Macro market indices (overlay, optional in regime-pack)
MARKET_TICKERS = ["000300.SS", "000001.SS", "399006.SZ", "^HSI", "^HSCE"]


# ---------------------------------------------------------------------------
# Ticker normalisation (.SS / .SZ / .HK auto-suffix)
# ---------------------------------------------------------------------------

def _normalise_ticker(t: str) -> str:
    """Append exchange suffix if a bare numeric code is passed.

    Heuristic (CN/HK convention):
      - already has '.' suffix     -> unchanged
      - starts with '6' or '9' (6-digit) -> .SS  (Shanghai: 600/601/603/605/688/900)
      - starts with '0', '2', '3' (6-digit) -> .SZ  (Shenzhen: 000/002/300/301)
      - 4 digits (e.g. '0700', '9988') -> .HK  (Hong Kong)
      - otherwise unchanged (caller responsibility)
    """
    t = t.strip().upper()
    if "." in t or t.startswith("^"):
        return t
    if not t.isdigit():
        return t
    if len(t) == 4:
        return f"{t}.HK"
    if len(t) == 6:
        first = t[0]
        if first in ("6", "9"):
            return f"{t}.SS"
        if first in ("0", "2", "3"):
            return f"{t}.SZ"
    return t


def _normalise_ticker_list(csv: str) -> list[str]:
    return [_normalise_ticker(t) for t in csv.split(",") if t.strip()]


# ---------------------------------------------------------------------------
# Subprocess helper
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> dict:
    """Run a client script and return parsed JSON (or error dict)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False,
        )
    except FileNotFoundError as e:
        return {"_error": f"command not found: {e}", "_cmd": " ".join(cmd)}

    if result.returncode != 0 and not result.stdout.strip():
        return {
            "_error": f"client exited rc={result.returncode}",
            "_cmd": " ".join(cmd),
            "_stderr": result.stderr.strip()[-500:],
        }

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return {
            "_error": f"invalid JSON from client: {e}",
            "_cmd": " ".join(cmd),
            "_stdout_head": result.stdout[:500],
            "_stderr": result.stderr.strip()[-500:],
        }


def _yf(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "yfinance_client.py"), *args])


def _nbs(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "nbs_client.py"), *args])


def _akshare(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "akshare_client.py"), *args])


def _fred(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "fred_client.py"), *args])


# ---------------------------------------------------------------------------
# Pack builders
# ---------------------------------------------------------------------------

def pack_snapshot(ticker: str) -> dict:
    """Quick overview: yfinance info + 6mo price history."""
    t = _normalise_ticker(ticker)
    return {
        "pack": "snapshot",
        "ticker": t,
        "country": "CN",
        "yfinance_info": _yf(["--ticker", t, "--action", "info"]),
        "yfinance_history": _yf(["--ticker", t, "--action", "history",
                                 "--period", "6mo", "--interval", "1d"]),
    }


def pack_memo_fetch(ticker: str) -> dict:
    """Memo data. Tier 2 only — CN primary-source individual-stock
    disclosure (e.g. CSRC-mandated annual reports via cninfo) is not
    yet integrated; yfinance financials is the current floor."""
    t = _normalise_ticker(ticker)
    return {
        "pack": "memo-fetch",
        "ticker": t,
        "country": "CN",
        "tier_note": ("Tier 2 only — CN primary-source individual-stock "
                      "disclosure (cninfo / HKEXnews) not in v2.0.0 scope; "
                      "see roadmap for analyst follow-up."),
        "yfinance_info": _yf(["--ticker", t, "--action", "info"]),
        "yfinance_history": _yf(["--ticker", t, "--action", "history",
                                 "--period", "2y", "--interval", "1d"]),
        "yfinance_financials_annual": _yf(["--ticker", t, "--action", "financials",
                                           "--period", "annual"]),
        "yfinance_financials_quarterly": _yf(["--ticker", t, "--action", "financials",
                                              "--period", "quarterly"]),
    }


def pack_comps_multiples_single(ticker: str) -> dict:
    """Multiples for one ticker. Used as anchor or per-peer in
    analysis-comps."""
    t = _normalise_ticker(ticker)
    info = _yf(["--ticker", t, "--action", "info"])
    multiples = {}
    # yfinance_client emits info fields at top level of the result dict.
    if isinstance(info, dict):
        for k in ("trailingPE", "forwardPE", "enterpriseToEbitda",
                  "priceToSalesTrailing12Months", "priceToBook"):
            v = info.get(k)
            if v is not None:
                multiples[k] = v
    return {
        "ticker": t,
        "country": "CN",
        "multiples": multiples,
        "_yfinance_info": info,
    }


def pack_comps_multiples_batch(tickers: list[str]) -> dict:
    """Multiples for a list. analysis-comps consumes anchor + peers."""
    out = []
    for t in tickers:
        out.append(pack_comps_multiples_single(t))
    return {"pack": "comps-multiples", "country": "CN", "tickers": out}


def pack_screener_batch(tickers: list[str]) -> dict:
    """Lightweight batch fetch via yfinance batch mode."""
    norm = [_normalise_ticker(t) for t in tickers]
    csv = ",".join(norm)
    return {
        "pack": "screener-batch",
        "country": "CN",
        "tickers": norm,
        "yfinance_info_batch": _yf(["--tickers", csv, "--action", "info"]),
        "yfinance_history_batch": _yf(["--tickers", csv, "--action", "history",
                                       "--period", "6mo", "--interval", "1d"]),
    }


def pack_regime_pack() -> dict:
    """Macro regime data: NBS (21) + akshare PBOC/Caixin (8) + FRED USDCNY."""
    nbs = _nbs(["--preset", ",".join(NBS_PRESETS)])
    akshare = _akshare(["--preset", ",".join(AKSHARE_PRESETS)])
    fred = _fred(["--series", ",".join(FRED_SERIES), "--periods", "24"])
    markets = _yf(["--tickers", ",".join(MARKET_TICKERS),
                   "--action", "history", "--period", "1y", "--interval", "1d"])
    return {
        "pack": "regime-pack",
        "country": "CN",
        "nbs": nbs,
        "akshare": akshare,
        "fred": fred,
        "markets": markets,
        "_provenance": {
            "nbs_indicators": NBS_PRESETS,
            "akshare_indicators": AKSHARE_PRESETS,
            "fred_series": FRED_SERIES,
            "market_tickers": MARKET_TICKERS,
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="data-cn pack facade (Layer 1 — China)",
    )
    parser.add_argument("--pack", required=True,
                        choices=["snapshot", "memo-fetch", "comps-multiples",
                                 "screener-batch", "regime-pack"],
                        help="Pack type")
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--ticker", help="Single ticker (e.g. 600519.SS, 000858.SZ, 0700.HK; "
                                     "bare 6-digit / 4-digit codes auto-suffix)")
    grp.add_argument("--tickers", help="Comma-separated tickers for batch mode")

    args = parser.parse_args()

    if args.pack == "regime-pack":
        out = pack_regime_pack()
    elif args.pack == "snapshot":
        if not args.ticker:
            parser.error("--pack snapshot requires --ticker")
        out = pack_snapshot(args.ticker)
    elif args.pack == "memo-fetch":
        if not args.ticker:
            parser.error("--pack memo-fetch requires --ticker (single only — N=1)")
        out = pack_memo_fetch(args.ticker)
    elif args.pack == "comps-multiples":
        if args.tickers:
            out = pack_comps_multiples_batch(_normalise_ticker_list(args.tickers))
        elif args.ticker:
            out = {
                "pack": "comps-multiples",
                "country": "CN",
                "tickers": [pack_comps_multiples_single(args.ticker)],
            }
        else:
            parser.error("--pack comps-multiples requires --ticker or --tickers")
    elif args.pack == "screener-batch":
        if not args.tickers:
            parser.error("--pack screener-batch requires --tickers")
        out = pack_screener_batch([t.strip() for t in args.tickers.split(",") if t.strip()])
    else:
        parser.error(f"unhandled pack: {args.pack}")

    print(json.dumps(out, default=str, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
