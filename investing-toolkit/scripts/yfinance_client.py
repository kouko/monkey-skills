#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["yfinance==0.2.54", "pandas==2.2.3"]
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
Cache: ~/.cache/investing-toolkit/yfinance/{ticker}_{action}.json  TTL: 1h
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "investing-toolkit" / "yfinance"
CACHE_TTL_SECONDS = 3600  # 1 hour

def get_cache_path(ticker: str, action: str, period: str = "", interval: str = "") -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = f"{ticker.upper()}_{action}_{period}_{interval}".strip("_")
    return CACHE_DIR / f"{key}.json"

def load_cache(path: Path) -> dict | None:
    if not path.exists():
        return None
    mtime = path.stat().st_mtime
    if time.time() - mtime > CACHE_TTL_SECONDS:
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None

def save_cache(path: Path, data: dict) -> None:
    try:
        path.write_text(json.dumps(data, default=str, indent=2))
    except Exception:
        pass  # Cache write failure is non-fatal

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
    cache_path = get_cache_path(ticker, "history", period, interval)
    cached = load_cache(cache_path)
    if cached:
        cached["_cache"] = "hit"
        return cached

    import yfinance as yf
    t = yf.Ticker(ticker)
    hist = fetch_with_retry(lambda: t.history(period=period, interval=interval))

    if hist.empty:
        return {"error": f"No price data returned for {ticker}"}

    result = {
        "ticker": ticker.upper(),
        "period": period,
        "interval": interval,
        "fetched_at": datetime.now(tz=__import__('datetime').timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_cache": "miss",
        "data": [
            {
                "date": str(idx.date()),
                "open": round(float(row["Open"]), 4),
                "high": round(float(row["High"]), 4),
                "low": round(float(row["Low"]), 4),
                "close": round(float(row["Close"]), 4),
                "volume": int(row["Volume"]),
            }
            for idx, row in hist.iterrows()
        ],
        "latest_close": round(float(hist["Close"].iloc[-1]), 4),
        "latest_date": str(hist.index[-1].date()),
        "rows": len(hist),
    }
    save_cache(cache_path, result)
    return result

def get_info(ticker: str) -> dict:
    cache_path = get_cache_path(ticker, "info")
    cached = load_cache(cache_path)
    if cached:
        cached["_cache"] = "hit"
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
        "fetched_at": datetime.now(tz=__import__('datetime').timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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

    save_cache(cache_path, result)
    return result

def get_batch(tickers: list[str], action: str, period: str, interval: str) -> dict:
    """Fetch data for multiple tickers. Returns {tickers: {AAPL: {...}, MSFT: {...}}}."""
    results = {}
    has_error = False
    for ticker in tickers:
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
                        choices=["history", "info"],
                        help="Data type: history (OHLCV) or info (fundamentals)")
    parser.add_argument("--period", default="1y",
                        help="Period for history: 1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max")
    parser.add_argument("--interval", default="1d",
                        help="Interval for history: 1m 2m 5m 15m 30m 60m 90m 1h 1d 5d 1wk 1mo 3mo")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache")

    args = parser.parse_args()

    # Batch mode
    if args.tickers:
        ticker_list = [t.strip() for t in args.tickers.split(",") if t.strip()]
        if args.no_cache:
            for t in ticker_list:
                p = get_cache_path(t, args.action, args.period, args.interval)
                if p.exists():
                    p.unlink()
        result = get_batch(ticker_list, args.action, args.period, args.interval)
        print(json.dumps(result, default=str, indent=2))
        if result.get("_partial"):
            sys.exit(1)
        return

    # Single ticker mode
    if args.no_cache:
        cache_path = get_cache_path(args.ticker, args.action, args.period, args.interval)
        if cache_path.exists():
            cache_path.unlink()

    try:
        if args.action == "history":
            result = get_history(args.ticker, args.period, args.interval)
        else:
            result = get_info(args.ticker)
    except Exception as e:
        result = {"error": str(e), "ticker": args.ticker}

    print(json.dumps(result, default=str, indent=2))

    if "error" in result:
        sys.exit(1)

if __name__ == "__main__":
    main()
