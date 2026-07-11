#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["yfinance==1.3.0", "pandas==3.0.2", "curl_cffi>=0.15"]
# ///
"""
yfinance_client.py — investing-toolkit US stock data adapter
Provides price history and company info via yfinance (unofficial).

Single ticker:
  uv run yfinance_client.py --ticker AAPL --period 1y
  uv run yfinance_client.py --ticker NVDA --action info
  uv run yfinance_client.py --ticker MSFT --period 6mo --interval 1wk

Batch mode (screener / portfolio):
  uv run yfinance_client.py --tickers AAPL,MSFT,NVDA --period 1y
  uv run yfinance_client.py --tickers AAPL,MSFT --action info

Auth: None required.
Cache: $INVESTING_TOOLKIT_CACHE/yfinance/{ticker}_{action}.json  TTL: 1h
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
       (resolved + read/written via cache_util.py — see that module for
       the full precedence ladder and envelope format.)
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone

import cache_util


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script so readers can disambiguate when multiple scripts log to one stream
# (e.g., pack.py orchestrating yfinance + sec_edgar). Inline (not shared
# module) to preserve PEP 723 zero-runtime-dependency design.

_QUIET = False
_LOG_TAG = "yfinance"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------
# Provenance helpers
# ---------------------------------------------------------------------------

def _compute_staleness(latest_date_str: str | None, fetched_at: str) -> int | None:
    """Compute days between reference period and fetch time."""
    if not latest_date_str:
        return None
    try:
        clean = latest_date_str.replace("-", "")
        if len(clean) == 6:
            clean += "01"  # YYYYMM -> YYYYMM01
        ref = datetime.strptime(clean[:8], "%Y%m%d").replace(tzinfo=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        return (now - ref).days
    except (ValueError, TypeError):
        return None


def _make_provenance(result: dict) -> dict:
    """Build _provenance block for a yfinance result."""
    ref_period = result.get("latest_date")
    return {
        "source": "yfinance (unofficial Yahoo Finance scraper)",
        "source_authority": "Yahoo Finance (unofficial, not endorsed)",
        "data_type": "unofficial_scraper",
        "update_cycle": "near-real-time (15 min delay)",
        "typical_lag": "15 minutes (price) / 1 day (fundamentals)",
        "fetched_at": result.get("fetched_at"),
        "reference_period": ref_period,
        "staleness_days": _compute_staleness(ref_period, result.get("fetched_at", "")),
    }


def _yfinance_cache_key(ticker: str, action: str, period: str = "", interval: str = "") -> str:
    """Build the cache_util key for a yfinance request (sanitized further by
    cache_util.cache_path itself)."""
    return f"{ticker.upper()}_{action}_{period}_{interval}".strip("_")


def fetch_with_retry(fn, retries: int = 3, backoff: float = 2.0):
    last_err = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(backoff ** attempt)
    raise last_err

def get_history(ticker: str, period: str, interval: str) -> dict:
    _log("history fetch", f"{ticker} period={period} interval={interval}")
    t0 = time.monotonic()
    cache_path = cache_util.cache_path("yfinance", _yfinance_cache_key(ticker, "history", period, interval))
    cached = cache_util.load_cache(cache_path, cache_util.compute_ttl("event", None))
    if cached:
        cached["_cache"] = "hit"
        if "_provenance" not in cached:
            cached["_provenance"] = _make_provenance(cached)
        _log("history done", f"{ticker} cache hit ({len(cached.get('data', []))} rows)")
        return cached

    import yfinance as yf
    import pandas as pd
    t = yf.Ticker(ticker)
    hist = fetch_with_retry(lambda: t.history(period=period, interval=interval))

    if hist.empty:
        return {"error": f"No price data returned for {ticker}"}

    # yfinance 1.x sometimes returns a trailing placeholder row with NaN OHLC
    # for the current/upcoming session (esp. non-US indices like 000300.SS).
    # Drop rows without a valid Close.
    hist = hist[hist["Close"].notna()]
    if hist.empty:
        return {"error": f"No valid price rows for {ticker} (all Close are NaN)"}

    result = {
        "ticker": ticker.upper(),
        "period": period,
        "interval": interval,
        "fetched_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_cache": "miss",
        "data": [
            {
                "date": str(idx.date()),
                "open": round(float(row["Open"]), 4),
                "high": round(float(row["High"]), 4),
                "low": round(float(row["Low"]), 4),
                "close": round(float(row["Close"]), 4),
                "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0,
            }
            for idx, row in hist.iterrows()
        ],
        "latest_close": round(float(hist["Close"].iloc[-1]), 4),
        "latest_date": str(hist.index[-1].date()),
        "rows": len(hist),
    }
    result["_provenance"] = _make_provenance(result)
    cache_util.save_cache(cache_path, result)
    _log("history done", f"{ticker} {result['rows']} rows in {time.monotonic() - t0:.1f}s")
    return result

def get_info(ticker: str) -> dict:
    _log("info fetch", ticker)
    t0 = time.monotonic()
    cache_path = cache_util.cache_path("yfinance", _yfinance_cache_key(ticker, "info"))
    cached = cache_util.load_cache(cache_path, cache_util.compute_ttl("event", None))
    if cached:
        cached["_cache"] = "hit"
        if "_provenance" not in cached:
            cached["_provenance"] = _make_provenance(cached)
        _log("info done", f"{ticker} cache hit")
        return cached

    import yfinance as yf
    t = yf.Ticker(ticker)
    raw = fetch_with_retry(lambda: t.info)

    if not raw or raw.get("regularMarketPrice") is None:
        return {"error": f"No info returned for {ticker}. Ticker may be invalid."}

    # Extract the most useful fields; yfinance info dict is large and unstable
    fields = [
        "symbol", "shortName", "longName", "sector", "industry",
        "country", "currency", "exchange",
        "regularMarketPrice", "regularMarketPreviousClose",
        "marketCap", "enterpriseValue",
        "trailingPE", "forwardPE", "priceToBook",
        "trailingEps", "forwardEps",
        "dividendYield", "payoutRatio",
        "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
        "fiftyDayAverage", "twoHundredDayAverage",
        "shortRatio", "sharesOutstanding",
        "totalRevenue", "grossMargins", "operatingMargins", "profitMargins",
        "returnOnEquity", "returnOnAssets",
        "totalDebt", "totalCash",
        "beta",
    ]

    result = {
        "ticker": ticker.upper(),
        "fetched_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_cache": "miss",
        "_warning": (
            "yfinance is an unofficial scraper. DO NOT use for financial statements "
            "(income statement, balance sheet, cash flow). Use SEC EDGAR for financials."
        ),
    }
    for f in fields:
        val = raw.get(f)
        if val is not None:
            result[f] = val

    result["_provenance"] = _make_provenance(result)
    cache_util.save_cache(cache_path, result)
    _log("info done", f"{ticker} in {time.monotonic() - t0:.1f}s")
    return result

def get_holdings(ticker: str) -> dict:
    """Fetch top-holdings from yfinance funds_data.

    Returns:
      {
        "ticker": "XLK",
        "holdings": [{"ticker": "AAPL", "weight": 0.0712}, ...],
        "warnings": ["..."],   # only present when issues encountered
        "_provenance": {...},
      }

    For non-fund tickers (no funds_data), returns empty holdings list with a
    `non_fund` warning. For fund tickers, returns top-holdings as exposed
    by yfinance — typically top 10–90 weights summing to 0.5–1.0 (NOT all
    holdings); aggregator records actual weight_coverage_pct.
    """
    import yfinance as yf  # local import — module-level may be lazy-stubbed in tests

    _log("holdings fetch", ticker)
    t0 = time.monotonic()
    cache_path = cache_util.cache_path("yfinance", _yfinance_cache_key(ticker, "holdings"))
    cached = cache_util.load_cache(cache_path, cache_util.compute_ttl("event", None))
    if cached is not None:
        _log("holdings done", f"{ticker} cache hit ({len(cached.get('holdings', []))} holdings)")
        return cached

    t = yf.Ticker(ticker)
    funds_data = getattr(t, "funds_data", None)
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if funds_data is None:
        out = {
            "ticker":   ticker,
            "holdings": [],
            "warnings": [f"non_fund: {ticker} has no yfinance funds_data block"],
            "_provenance": {
                "skill":      "data-us",
                "source":     "yfinance.Ticker.funds_data",
                "fetched_at": fetched_at,
            },
        }
        cache_util.save_cache(cache_path, out)
        _log("holdings done", f"{ticker} non-fund (no funds_data)")
        return out

    df = getattr(funds_data, "top_holdings", None)
    holdings: list[dict] = []
    warnings: list[str] = []
    if df is None:
        warnings.append("yfinance funds_data.top_holdings returned None")
    else:
        try:
            data = df.to_dict()
        except Exception as exc:  # noqa: BLE001 — yfinance shape varies across versions
            warnings.append(f"top_holdings.to_dict() failed: {exc}")
            data = {}
        weights_dict = data.get("Holding Percent") or data.get("holdingPercent") or {}
        for sym, weight in weights_dict.items():
            try:
                holdings.append({"ticker": sym, "weight": float(weight)})
            except (TypeError, ValueError):
                continue

    out = {
        "ticker":   ticker,
        "holdings": holdings,
        "_provenance": {
            "skill":      "data-us",
            "source":     "yfinance.Ticker.funds_data.top_holdings",
            "fetched_at": fetched_at,
        },
    }
    if warnings:
        out["warnings"] = warnings
    cache_util.save_cache(cache_path, out)
    _log("holdings done", f"{ticker} {len(holdings)} holdings in {time.monotonic() - t0:.1f}s")
    return out


# ---------------------------------------------------------------------------
# Financials (Tier 2 fallback for JP / when primary-source unavailable)
# ---------------------------------------------------------------------------
#
# Yahoo Finance is an unofficial scraper — use ONLY when a primary-source
# (SEC EDGAR for US / MOPS for TW / EDINET for JP) is not available or
# the user explicitly opts for Tier 2 data. Intended fallback for JP
# tickers when EDINET_API_KEY is not set; otherwise the japan-stock-snapshot
# skill should route to edinet_client.py.


_FINANCIALS_KEY_METRICS_MAPPING = {
    # yfinance row-label → canonical metric name (matches edinet_client
    # / sec_edgar naming so downstream skills can diff US/TW/JP uniformly).
    "Total Revenue": "revenue",
    "Operating Income": "operating_income",
    "Net Income": "net_income",
    "Net Income Common Stockholders": "net_income",
    "Basic EPS": "eps",
    "Total Assets": "total_assets",
    "Stockholders Equity": "net_assets",
    "Total Equity Gross Minority Interest": "net_assets",
    "Cash And Cash Equivalents": "cash_and_equivalents",
    "Operating Cash Flow": "operating_cash_flow",
    "Cash Flow From Continuing Operating Activities": "operating_cash_flow",
    "Investing Cash Flow": "investing_cash_flow",
    "Financing Cash Flow": "financing_cash_flow",
    "Free Cash Flow": "free_cash_flow",
}


def _df_to_records(df) -> dict:
    """Convert yfinance financial-statement DataFrame (rows=line items,
    columns=period-end dates) to a {period_iso: {metric: value}} dict.
    Also drops all-NaN rows."""
    import pandas as pd

    if df is None or df.empty:
        return {}
    out: dict = {}
    # Columns are Timestamp dates; serialize to YYYY-MM-DD
    for col in df.columns:
        period_key = col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)
        period_dict: dict = {}
        for row_label, val in df[col].items():
            if pd.isna(val):
                continue
            try:
                v = float(val)
            except (TypeError, ValueError):
                continue
            period_dict[str(row_label)] = v
        if period_dict:
            out[period_key] = period_dict
    return out


def _extract_key_metrics_yf(
    income: dict, balance: dict, cashflow: dict,
) -> tuple[str | None, dict]:
    """Pick the latest period that appears in at least one statement,
    then emit a canonical key_metrics dict (shape mirrors edinet_client)."""
    all_periods = sorted(
        set(income) | set(balance) | set(cashflow), reverse=True,
    )
    if not all_periods:
        return None, {}
    latest = all_periods[0]

    key_metrics: dict = {}
    for source_dict in (income.get(latest, {}), balance.get(latest, {}),
                        cashflow.get(latest, {})):
        for raw_label, value in source_dict.items():
            canonical = _FINANCIALS_KEY_METRICS_MAPPING.get(raw_label)
            if canonical and canonical not in key_metrics:
                key_metrics[canonical] = {
                    "value": value,
                    "source_label": raw_label,
                    "period": latest,
                }
    return latest, key_metrics


def get_financials(ticker: str, period: str = "annual") -> dict:
    """Fetch BS/PL/CF for a ticker via Yahoo Finance (Tier 2).

    period: 'annual' (default) or 'quarterly'. Returns income_statement,
    balance_sheet, cash_flow as {period_iso: {row_label: value}} plus
    a canonical key_metrics extract tied to the latest available period.
    """
    import yfinance as yf
    import pandas as pd

    _log("financials fetch", f"{ticker} {period}")
    t0 = time.monotonic()
    cache_path = cache_util.cache_path("yfinance", _yfinance_cache_key(ticker, f"financials_{period}"))
    cached = cache_util.load_cache(cache_path, cache_util.compute_ttl("event", None))
    if cached:
        cached["_cache"] = "hit"
        _log("financials done", f"{ticker} cache hit")
        return cached

    t = yf.Ticker(ticker)
    try:
        if period == "annual":
            income_df = fetch_with_retry(lambda: t.financials)
            _log("financials", "income statement done")
            balance_df = fetch_with_retry(lambda: t.balance_sheet)
            _log("financials", "balance sheet done")
            cashflow_df = fetch_with_retry(lambda: t.cashflow)
            _log("financials", "cash flow done")
        elif period == "quarterly":
            income_df = fetch_with_retry(lambda: t.quarterly_financials)
            _log("financials", "quarterly income statement done")
            balance_df = fetch_with_retry(lambda: t.quarterly_balance_sheet)
            _log("financials", "quarterly balance sheet done")
            cashflow_df = fetch_with_retry(lambda: t.quarterly_cashflow)
            _log("financials", "quarterly cash flow done")
        else:
            return {"error": f"Invalid period '{period}' (use 'annual' or 'quarterly')"}
    except Exception as e:
        return {"error": f"yfinance financials fetch failed: {e}", "ticker": ticker}

    income = _df_to_records(income_df)
    balance = _df_to_records(balance_df)
    cashflow = _df_to_records(cashflow_df)

    if not income and not balance and not cashflow:
        return {
            "error": f"No financial-statement data returned for {ticker} (period={period}). "
                     "Ticker may be invalid, delisted, or Yahoo scraper blocked.",
            "ticker": ticker,
        }

    latest_period, key_metrics = _extract_key_metrics_yf(income, balance, cashflow)

    result = {
        "ticker": ticker.upper(),
        "period": period,
        "fetched_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_cache": "miss",
        "latest_period": latest_period,
        "key_metrics": key_metrics,
        "income_statement": income,
        "balance_sheet": balance,
        "cash_flow": cashflow,
        "_warning": (
            "Yahoo Finance is an unofficial scraper. Financial statements "
            "may be stale, incomplete, or diverge from regulator filings. "
            "For JP tickers (.T), prefer edinet_client.py (primary-source "
            "金融庁 Tier A) when EDINET_API_KEY is set."
        ),
    }
    result["_provenance"] = {
        **_make_provenance(result),
        "data_tier": "tier_2",
        "note": "Unofficial Yahoo scraper; not regulator-filed.",
    }
    cache_util.save_cache(cache_path, result)
    _log("financials done", f"{ticker} {period} in {time.monotonic() - t0:.1f}s")
    return result


def get_batch(tickers: list[str], action: str, period: str, interval: str) -> dict:
    """Fetch data for multiple tickers. Returns {tickers: {AAPL: {...}, MSFT: {...}}}."""
    _log("batch start", f"{len(tickers)} tickers action={action}")
    t0 = time.monotonic()
    results = {}
    has_error = False
    for i, ticker in enumerate(tickers, 1):
        _log(f"batch [{i}/{len(tickers)}]", ticker)
        try:
            if action == "history":
                results[ticker.upper()] = get_history(ticker, period, interval)
            else:
                results[ticker.upper()] = get_info(ticker)
            if "error" in results[ticker.upper()]:
                has_error = True
        except Exception as e:
            results[ticker.upper()] = {"error": str(e), "ticker": ticker.upper()}
            has_error = True

    _log("batch done", f"{len(tickers)} tickers in {time.monotonic() - t0:.1f}s ({'errors' if has_error else 'ok'})")
    return {
        "mode": "batch",
        "action": action,
        "tickers": results,
        "_partial": has_error,
        "_summary": {
            t: "ok" if "error" not in d else f"error: {d['error']}"
            for t, d in results.items()
        },
    }



def main():
    parser = argparse.ArgumentParser(description="yfinance investing-toolkit adapter")
    ticker_group = parser.add_mutually_exclusive_group(required=True)
    ticker_group.add_argument("--ticker", help="Single ticker (e.g. AAPL, 2330.TW)")
    ticker_group.add_argument("--tickers", help="Comma-separated tickers for batch mode (e.g. AAPL,MSFT,NVDA)")
    parser.add_argument("--action", default="history",
                        choices=["history", "info", "financials", "holdings"],
                        help="Data type: history (OHLCV) / info (snapshot) / "
                             "financials (BS+PL+CF, Tier 2 only) / "
                             "holdings (ETF top-holdings via funds_data)")
    parser.add_argument("--period", default="1y",
                        help="Period for history: 1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max. "
                             "For --action financials: 'annual' or 'quarterly'.")
    parser.add_argument("--interval", default="1d",
                        help="Interval for history: 1m 2m 5m 15m 30m 60m 90m 1h 1d 5d 1wk 1mo 3mo")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress logging on stderr (default: verbose)")

    args = parser.parse_args()
    global _QUIET
    _QUIET = args.quiet

    # Batch mode
    if args.tickers:
        ticker_list = [t.strip() for t in args.tickers.split(",") if t.strip()]
        if args.no_cache:
            for t in ticker_list:
                p = cache_util.cache_path("yfinance", _yfinance_cache_key(t, args.action, args.period, args.interval))
                if p.exists():
                    p.unlink()
        result = get_batch(ticker_list, args.action, args.period, args.interval)
        print(json.dumps(result, default=str, indent=2))
        if result.get("_partial"):
            sys.exit(1)
        return

    # Single ticker mode
    if args.no_cache:
        cache_path = cache_util.cache_path("yfinance", _yfinance_cache_key(args.ticker, args.action, args.period, args.interval))
        if cache_path.exists():
            cache_path.unlink()

    try:
        if args.action == "history":
            result = get_history(args.ticker, args.period, args.interval)
        elif args.action == "financials":
            # For financials, --period doubles as annual/quarterly selector.
            fin_period = args.period if args.period in ("annual", "quarterly") else "annual"
            result = get_financials(args.ticker, fin_period)
        elif args.action == "holdings":
            if not args.ticker:
                print("error: --action holdings requires --ticker", file=sys.stderr)
                return 2
            result = get_holdings(args.ticker)
        else:
            result = get_info(args.ticker)
    except Exception as e:
        result = {"error": str(e), "ticker": args.ticker}

    print(json.dumps(result, default=str, indent=2))

    if "error" in result:
        sys.exit(1)

if __name__ == "__main__":
    main()
