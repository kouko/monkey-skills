#!/usr/bin/env python3
"""
data-tw / pack.py — Layer 1 facade for Taiwan equity + macro fetches.

Composes 8 underlying clients into 5 pack types:
  - snapshot         : yfinance + MOPS basic disclosure + TWSE trade data + FinMind T86 (single ticker)
  - memo-fetch       : snapshot + MOPS financial statements + 月營收 + 重大訊息 (heavy, single ticker)
  - comps-multiples  : yfinance multiples (single or batch)
  - screener-batch   : yfinance batch + minimal MOPS valuation fields (batch only)
  - regime-pack      : CBC + DGBAS + NDC 五色景氣燈號 + statgov + CIER PMI (no ticker dimension)

Tier policy:
  - MOPS + TWSE OpenAPI = Tier A primary
  - FinMind = by-design gap supplier — NOT automatic Tier A → 2 retry
    (per-stock T86 三大法人 daily flow; price history for .TWO; split-adjusted OHLCV)
    Tier A errors surface as per-source `_error` + top-level `_partial: true`;
    consumers inspect `_tier`/`_partial` to decide escalation.
  - yfinance = Tier 2 cross-source (price/info/multiples) — convenient batch & multiples

Output: structured JSON to stdout.
- Each underlying client output is wrapped in {tier, source, action, data, _error?}.
- Per-source failures degrade to `_partial: true` rather than aborting the pack.

Ticker conventions:
  - .TW → TWSE listed (sii market)
  - .TWO → TPEx listed (otc market)
  - bare numeric (e.g. 2330) → assumed sii (.TW); explicit suffix preferred

Cache: honors $INVESTING_TOOLKIT_CACHE if set.

Examples:
  pack.py --ticker 2330.TW --pack snapshot
  pack.py --ticker 2330.TW --pack memo-fetch
  pack.py --tickers 2330.TW,2454.TW --pack screener-batch
  pack.py --tickers 2330.TW,2454.TW --pack comps-multiples
  pack.py --pack regime-pack
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

_UTCNOW = lambda: datetime.now(timezone.utc).replace(tzinfo=None)
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PACK_TYPES = {"snapshot", "memo-fetch", "comps-multiples", "screener-batch", "regime-pack"}


# ----------------------------- ticker helpers -----------------------------

def normalize_ticker(raw: str) -> dict[str, str]:
    """Return {ticker_yf, ticker_code, market} for a TW ticker.

    .TW → market=sii (TWSE)
    .TWO → market=otc (TPEx)
    bare numeric → assume sii / .TW
    """
    raw = raw.strip().upper()
    if raw.endswith(".TW"):
        return {"ticker_yf": raw, "ticker_code": raw[:-3], "market": "sii"}
    if raw.endswith(".TWO"):
        return {"ticker_yf": raw, "ticker_code": raw[:-4], "market": "otc"}
    # bare → assume sii
    return {"ticker_yf": f"{raw}.TW", "ticker_code": raw, "market": "sii"}


def latest_roc_quarter(today: datetime | None = None) -> tuple[int, int]:
    """Return (roc_year, season) for the most recently-reported quarter.

    TW quarterly statements are filed:
      Q4 (consolidated 年報): by Mar 31 of next year → safe Apr+
      Q1: by May 15 → safe Jun+
      Q2 (半年報): by Aug 14 → safe Sep+
      Q3: by Nov 14 → safe Dec+
    Use a conservative shift: subtract one quarter from the calendar quarter
    so we always request a quarter likely to be filed.
    """
    today = today or _UTCNOW()
    # Conservative: report the most recently-COMPLETED quarter that's likely filed.
    # Calendar Q = (month-1)//3 + 1. Filed quarter typically lags 1-2 quarters.
    # Use simple rule: the quarter from 4 months ago.
    target = today - timedelta(days=120)
    season = (target.month - 1) // 3 + 1
    roc_year = target.year - 1911
    return roc_year, season


def latest_revenue_month(today: datetime | None = None) -> tuple[int, int]:
    """Return (roc_year, month) for the most recently-published 月營收.

    月營收 published by the 10th of the following month → use 2 months ago
    to be safe.
    """
    today = today or _UTCNOW()
    if today.day < 12:
        # last month not yet published; go 2 back
        ref = today - timedelta(days=40)
    else:
        ref = today - timedelta(days=15)
    return ref.year - 1911, ref.month


# ----------------------------- subprocess runner -----------------------------

def run_client(script: str, args: list[str], timeout: int = 60) -> dict[str, Any]:
    """Run a client script and return parsed JSON, or an error envelope."""
    cmd = ["uv", "run", str(SCRIPT_DIR / script), *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ},
        )
    except subprocess.TimeoutExpired:
        return {"_error": "timeout", "_cmd": " ".join(cmd)}
    except Exception as exc:
        return {"_error": f"exec_failed: {exc}", "_cmd": " ".join(cmd)}

    if result.returncode != 0:
        return {
            "_error": f"exit_{result.returncode}",
            "_stderr": (result.stderr or "")[:600],
            "_cmd": " ".join(cmd),
        }
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {
            "_error": f"json_decode: {exc}",
            "_stdout_head": result.stdout[:300],
            "_cmd": " ".join(cmd),
        }


def wrap(tier: str, source: str, action: str, data: Any) -> dict[str, Any]:
    """Wrap a client output with provenance metadata."""
    out: dict[str, Any] = {
        "_tier": tier,
        "_source": source,
        "_action": action,
    }
    if isinstance(data, dict) and "_error" in data:
        out["_error"] = data["_error"]
        for k, v in data.items():
            if k.startswith("_") and k != "_error":
                out[k] = v
    else:
        out["data"] = data
    return out


# ----------------------------- pack: snapshot -----------------------------

def pack_snapshot(ticker: str, period: str = "1y") -> dict[str, Any]:
    norm = normalize_ticker(ticker)
    yf_ticker = norm["ticker_yf"]
    code = norm["ticker_code"]
    market = norm["market"]
    roc_year, season = latest_roc_quarter()
    rev_year, rev_month = latest_revenue_month()
    date_3mo = (_UTCNOW() - timedelta(days=90)).strftime("%Y-%m-%d")

    out: dict[str, Any] = {
        "_pack": "snapshot",
        "_ticker": yf_ticker,
        "_normalized": norm,
        "yfinance": {},
        "mops": {},
        "twse": {},
        "finmind": {},
        "_partial": False,
    }

    # yfinance — Tier 2 (price snapshot)
    out["yfinance"]["info"] = wrap("2", "yfinance", "info",
        run_client("yfinance_client.py", ["--ticker", yf_ticker, "--action", "info"]))
    out["yfinance"]["history"] = wrap("2", "yfinance", "history",
        run_client("yfinance_client.py", ["--ticker", yf_ticker, "--action", "history", "--period", period]))

    # MOPS — Tier A primary
    out["mops"]["company_basic"] = wrap("A", "mops", "company-basic",
        run_client("mops_client.py", ["--ticker", code, "--action", "company-basic"]))
    out["mops"]["balance_sheet"] = wrap("A", "mops", "balance-sheet",
        run_client("mops_client.py", ["--ticker", code, "--action", "balance-sheet",
                                       "--year", str(roc_year), "--season", str(season)]))
    out["mops"]["income_statement"] = wrap("A", "mops", "income-statement",
        run_client("mops_client.py", ["--ticker", code, "--action", "income-statement",
                                       "--year", str(roc_year), "--season", str(season)]))

    # TWSE OpenAPI — Tier A primary
    out["twse"]["daily_price"] = wrap("A", "twse_openapi", "daily-price",
        run_client("twse_openapi_client.py", ["--ticker", code, "--action", "daily-price"]))
    out["twse"]["pe_pb_yield"] = wrap("A", "twse_openapi", "pe-pb-yield",
        run_client("twse_openapi_client.py", ["--ticker", code, "--action", "pe-pb-yield"]))
    out["twse"]["margin_balance"] = wrap("A", "twse_openapi", "margin-balance",
        run_client("twse_openapi_client.py", ["--ticker", code, "--action", "margin-balance"]))

    # FinMind — Tier 2 by-design (T86 daily 三大法人 flow is a Tier A gap)
    out["finmind"]["three_investor_flow"] = wrap("2-gap", "finmind", "T86",
        run_client("finmind_client.py",
                   ["--ticker", code, "--dataset", "TaiwanStockInstitutionalInvestorsBuySell",
                    "--date-start", date_3mo]))

    # mark partial if any tier-A errored
    for src in ("mops", "twse"):
        for entry in out[src].values():
            if "_error" in entry:
                out["_partial"] = True
                break
    return out


# ----------------------------- pack: memo-fetch -----------------------------

def pack_memo_fetch(ticker: str, period: str = "2y") -> dict[str, Any]:
    """Snapshot + financial statements + 月營收 12m + 重大訊息. Heavy, single ticker."""
    norm = normalize_ticker(ticker)
    code = norm["ticker_code"]
    market = norm["market"]
    roc_year, season = latest_roc_quarter()
    rev_year, rev_month = latest_revenue_month()
    roc_5y_ago = roc_year - 5
    date_3mo = (_UTCNOW() - timedelta(days=90)).strftime("%Y-%m-%d")

    out = pack_snapshot(ticker, period=period)
    out["_pack"] = "memo-fetch"

    # Cash flow + monthly revenue + dividends + announcements + insider/director — Tier A
    out["mops"]["cash_flow"] = wrap("A", "mops", "cash-flow",
        run_client("mops_client.py", ["--ticker", code, "--action", "cash-flow",
                                       "--year", str(roc_year), "--season", str(season)]))
    out["mops"]["monthly_revenue"] = wrap("A", "mops", "monthly-revenue",
        run_client("mops_client.py", ["--ticker", code, "--action", "monthly-revenue",
                                       "--year", str(rev_year), "--month", str(rev_month)]))
    out["mops"]["dividends"] = wrap("A", "mops", "dividends",
        run_client("mops_client.py", ["--ticker", code, "--action", "dividends",
                                       "--first-year", str(roc_5y_ago), "--last-year", str(roc_year)]))
    out["mops"]["director_holdings"] = wrap("A", "mops", "director-holdings",
        run_client("mops_client.py", ["--ticker", code, "--action", "director-holdings"]))
    out["mops"]["insider_trades"] = wrap("A", "mops", "insider-trades",
        run_client("mops_client.py", ["--ticker", code, "--action", "insider-trades"]))
    out["mops"]["announcements"] = wrap("A", "mops", "realtime-announcements",
        run_client("mops_client.py", ["--action", "realtime-announcements",
                                       "--market", market, "--count", "10"]))

    # TWSE three_investor (snapshot) — Tier A
    out["twse"]["three_investor"] = wrap("A", "twse_openapi", "three-investor",
        run_client("twse_openapi_client.py", ["--ticker", code, "--action", "three-investor"]))

    # TWSE /rwd/ raw OHLCV history (Tier A primary) for sii listings
    if market == "sii":
        months = 24 if period in ("2y",) else (12 if period in ("1y",) else 6)
        out["twse"]["stock_day_history"] = wrap("A", "twse_openapi", "stock-day-history",
            run_client("twse_openapi_client.py",
                       ["--ticker", code, "--action", "stock-day-history",
                        "--months", str(months)]))
    else:
        # .TWO has no /rwd/; fall through to FinMind TaiwanStockPrice
        date_start = (_UTCNOW() - timedelta(days=730 if period == "2y" else 365)).strftime("%Y-%m-%d")
        out["finmind"]["price_history"] = wrap("2", "finmind", "TaiwanStockPrice",
            run_client("finmind_client.py",
                       ["--ticker", code, "--dataset", "TaiwanStockPrice", "--date-start", date_start]))

    # FinMind margin time series — Tier 2 by-design
    out["finmind"]["margin_history"] = wrap("2-gap", "finmind", "TaiwanStockMarginPurchaseShortSale",
        run_client("finmind_client.py",
                   ["--ticker", code, "--dataset", "TaiwanStockMarginPurchaseShortSale",
                    "--date-start", date_3mo]))
    return out


# ----------------------------- pack: comps-multiples -----------------------------

def pack_comps_multiples(tickers: list[str]) -> dict[str, Any]:
    """yfinance info (multiples-only) for one or many tickers."""
    out: dict[str, Any] = {"_pack": "comps-multiples", "_tickers": [], "tickers": {}}
    for t in tickers:
        norm = normalize_ticker(t)
        yf_t = norm["ticker_yf"]
        out["_tickers"].append(yf_t)
        info = run_client("yfinance_client.py", ["--ticker", yf_t, "--action", "info"])
        # extract just the multiples block if present
        multiples_keys = ["trailingPE", "forwardPE", "priceToSalesTrailing12Months",
                          "priceToBook", "enterpriseToEbitda", "enterpriseToRevenue",
                          "marketCap", "enterpriseValue"]
        multiples = {}
        if isinstance(info, dict) and "_error" not in info:
            for k in multiples_keys:
                if k in info:
                    multiples[k] = info[k]
        out["tickers"][yf_t] = wrap("2", "yfinance", "info-multiples",
                                     {"multiples": multiples, "raw_info": info if "_error" in info else {"_omitted": True}})
        if "_error" in info:
            out["tickers"][yf_t]["data"] = info  # surface error
    return out


# ----------------------------- pack: screener-batch -----------------------------

def pack_screener_batch(tickers: list[str], period: str = "1y") -> dict[str, Any]:
    """yfinance batch info+history + minimal MOPS company_basic per ticker."""
    out: dict[str, Any] = {"_pack": "screener-batch", "_tickers": [], "yfinance": {}, "mops": {}}
    yf_list = []
    for t in tickers:
        norm = normalize_ticker(t)
        yf_list.append(norm["ticker_yf"])
        out["_tickers"].append(norm["ticker_yf"])

    # yfinance batch — single subprocess
    batch_info = run_client("yfinance_client.py",
                             ["--tickers", ",".join(yf_list), "--action", "info"])
    batch_hist = run_client("yfinance_client.py",
                             ["--tickers", ",".join(yf_list), "--action", "history", "--period", period])
    out["yfinance"]["info_batch"] = wrap("2", "yfinance", "info-batch", batch_info)
    out["yfinance"]["history_batch"] = wrap("2", "yfinance", "history-batch", batch_hist)

    # minimal MOPS — company_basic for each ticker (Tier A)
    for t in tickers:
        norm = normalize_ticker(t)
        code = norm["ticker_code"]
        out["mops"][norm["ticker_yf"]] = wrap("A", "mops", "company-basic",
            run_client("mops_client.py", ["--ticker", code, "--action", "company-basic"]))
    return out


# ----------------------------- pack: regime-pack -----------------------------

def pack_regime() -> dict[str, Any]:
    """Macro regime indicators: CBC + DGBAS + NDC 五色景氣燈號 + statgov + CIER PMI."""
    out: dict[str, Any] = {"_pack": "regime-pack", "cbc": {}, "dgbas": {},
                           "ndc": {}, "statgov": {}, "_partial": False}

    # CBC — rates / forex / money
    out["cbc"]["macro"] = wrap("A", "cbc", "preset-bundle",
        run_client("cbc_client.py", ["--preset", "rediscount-rate,twdusd,m2,reserve-money"]))
    # DGBAS — inflation
    out["dgbas"]["inflation"] = wrap("A", "dgbas", "preset-bundle",
        run_client("dgbas_client.py", ["--preset", "cpi,core-cpi,ppi,import-pi,export-pi"]))
    # NDC — 五色景氣燈號 + components
    out["ndc"]["signal"] = wrap("A", "ndc", "signal",
        run_client("ndc_client.py", ["--preset", "signal,signal-components"]))
    # NDC PMI / NMI (CIER via data.gov.tw 6100)
    out["ndc"]["pmi"] = wrap("A", "ndc", "pmi",
        run_client("ndc_client.py", ["--preset", "pmi-mfg,pmi-nmi"]))
    # statgov — growth / labor / trade / leading-coincident CI
    out["statgov"]["growth"] = wrap("A", "statgov", "preset-growth",
        run_client("statgov_client.py",
                   ["--preset", "gdp-yoy,ipi,manufacturing-yoy,retail-yoy"]))
    out["statgov"]["trade"] = wrap("A", "statgov", "preset-trade",
        run_client("statgov_client.py",
                   ["--preset", "export-orders,exports,imports,exports-yoy,imports-yoy"]))
    out["statgov"]["labor_cycle_other"] = wrap("A", "statgov", "preset-bundle",
        run_client("statgov_client.py",
                   ["--preset",
                    "unemployment,unemployment-sa,leading-index,coincident-index,fx-reserves,taiex,m2-yoy"]))

    # Mark partial on any error
    for group in (out["cbc"], out["dgbas"], out["ndc"], out["statgov"]):
        for entry in group.values():
            if "_error" in entry:
                out["_partial"] = True
                break
    return out


# ----------------------------- main -----------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="data-tw / pack.py — Layer 1 facade for TW equity + macro fetches"
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--ticker", help="Single TW ticker (e.g. 2330.TW, 2330.TWO, 2330)")
    g.add_argument("--tickers", help="Comma-separated tickers for batch packs")
    parser.add_argument("--pack", required=True, choices=sorted(PACK_TYPES))
    parser.add_argument("--period", default="1y",
                        help="History lookback for snapshot/memo-fetch/screener-batch")
    args = parser.parse_args()

    if args.pack == "snapshot":
        if not args.ticker:
            parser.error("--pack snapshot requires --ticker")
        result = pack_snapshot(args.ticker, period=args.period)
    elif args.pack == "memo-fetch":
        if not args.ticker:
            parser.error("--pack memo-fetch requires --ticker")
        result = pack_memo_fetch(args.ticker, period=args.period)
    elif args.pack == "comps-multiples":
        tickers = []
        if args.ticker:
            tickers = [args.ticker]
        elif args.tickers:
            tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
        else:
            parser.error("--pack comps-multiples requires --ticker or --tickers")
        result = pack_comps_multiples(tickers)
    elif args.pack == "screener-batch":
        if not args.tickers:
            parser.error("--pack screener-batch requires --tickers")
        tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
        result = pack_screener_batch(tickers, period=args.period)
    elif args.pack == "regime-pack":
        result = pack_regime()
    else:
        parser.error(f"unknown pack {args.pack}")
        return 2

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
