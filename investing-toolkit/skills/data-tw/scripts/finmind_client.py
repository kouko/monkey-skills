#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""
finmind_client.py — FinMind API adapter for Taiwan equity data

Supported datasets:
  TaiwanStockPrice                        OHLCV daily
  TaiwanStockInstitutionalInvestorsBuySell  三大法人買賣超
  TaiwanStockMonthRevenue                 月營收
  TaiwanStockHoldingSharesPer             董監持股
  TaiwanStockMarginPurchaseShortSale      融資融券
  TaiwanStockFinancialStatements          財務報表（季頻）
  TaiwanStockProfitLossStatement          損益表（季頻）

Auth: FINMIND_API_TOKEN env var (optional)
  - Anonymous: 300 req/hr
  - With token: 600 req/hr (free registration at https://finmindtrade.com)

Cache: $INVESTING_TOOLKIT_CACHE/finmind/, 6h TTL
       Falls back to ~/.cache/investing-toolkit/ if env var not set.

Usage:
  python3 finmind_client.py --ticker 2330 --dataset TaiwanStockPrice --date-start 2025-04-01
  python3 finmind_client.py --ticker 2330 --dataset TaiwanStockInstitutionalInvestorsBuySell --date-start 2026-01-01
  python3 finmind_client.py --ticker 2330 --dataset TaiwanStockMonthRevenue --date-start 2025-01-01
  python3 finmind_client.py --ticker 2330 --dataset TaiwanStockHoldingSharesPer --date-start 2025-01-01
  python3 finmind_client.py --ticker 2330 --dataset TaiwanStockMarginPurchaseShortSale --date-start 2026-01-01

  # Multiple datasets (comma-separated)
  python3 finmind_client.py --ticker 2330 --dataset TaiwanStockPrice,TaiwanStockMonthRevenue --date-start 2025-01-01

  # Bypass cache
  python3 finmind_client.py --ticker 2330 --dataset TaiwanStockPrice --date-start 2025-04-01 --no-cache

Ticker format: 4-digit code only (2330, not 2330.TW or 2330.TWO)
The script strips .TW and .TWO suffixes automatically.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FINMIND_BASE_URL = "https://api.finmindtrade.com/api/v4/data"
_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(Path.home() / ".cache" / "investing-toolkit")
CACHE_DIR = Path(_CACHE_BASE) / "finmind"
CACHE_TTL_SECONDS = 6 * 3600  # 6 hours

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0  # seconds, exponential backoff

KNOWN_DATASETS = {
    "TaiwanStockPrice",
    "TaiwanStockInstitutionalInvestorsBuySell",
    "TaiwanStockMonthRevenue",
    "TaiwanStockHoldingSharesPer",
    "TaiwanStockMarginPurchaseShortSale",
    "TaiwanStockFinancialStatements",
    "TaiwanStockProfitLossStatement",
}

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


def _make_provenance(latest_date: str | None, fetched_at: str | None) -> dict:
    """Build _provenance block for a FinMind result."""
    return {
        "source": "FinMind API (finmindtrade.com)",
        "source_authority": "FinMind (open-source aggregator, data from TWSE/MOPS)",
        "data_type": "open_source_aggregator",
        "update_cycle": "daily (T+1 for most datasets)",
        "typical_lag": "1 business day",
        "fetched_at": fetched_at,
        "reference_period": latest_date,
        "staleness_days": _compute_staleness(latest_date, fetched_at or ""),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_ticker(ticker: str) -> str:
    """Strip .TW / .TWO suffix. '2330.TW' → '2330'."""
    return ticker.replace(".TWO", "").replace(".TW", "")


def cache_key(ticker: str, dataset: str, date_start: str, date_end: str) -> str:
    raw = f"{ticker}|{dataset}|{date_start}|{date_end}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def load_cache(key: str) -> dict | None:
    path = CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > CACHE_TTL_SECONDS:
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def save_cache(key: str, data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{key}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def fetch_dataset(
    ticker: str,
    dataset: str,
    date_start: str,
    date_end: str,
    token: str | None,
    use_cache: bool,
) -> dict:
    """Fetch a single FinMind dataset with retry + cache."""
    key = cache_key(ticker, dataset, date_start, date_end)

    if use_cache:
        cached = load_cache(key)
        if cached is not None:
            cached["_cache"] = "hit"
            if "_provenance" not in cached:
                data_rows = cached.get("data", [])
                latest_date = None
                if data_rows:
                    dates = [r.get("date", "") for r in data_rows if r.get("date")]
                    if dates:
                        latest_date = max(dates)
                cached["_provenance"] = _make_provenance(latest_date, cached.get("fetched_at"))
            return cached

    params: dict = {
        "dataset": dataset,
        "data_id": ticker,
        "start_date": date_start,
        "end_date": date_end,
    }
    if token:
        params["token"] = token

    last_error: str = ""
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(FINMIND_BASE_URL, params=params, timeout=30)

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", RETRY_BASE_DELAY * (2 ** attempt)))
                time.sleep(retry_after)
                last_error = "HTTP 429 rate limit"
                continue

            if resp.status_code != 200:
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue

            body = resp.json()
            if body.get("status") != 200:
                last_error = f"FinMind API error: {body.get('msg', 'unknown')}"
                break  # API-level error, no point retrying

            data_rows = body.get("data", [])
            fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            # Determine latest date from data rows
            latest_date = None
            if data_rows:
                dates = [r.get("date", "") for r in data_rows if r.get("date")]
                if dates:
                    latest_date = max(dates)

            result = {
                "dataset": dataset,
                "ticker": ticker,
                "date_start": date_start,
                "date_end": date_end,
                "fetched_at": fetched_at,
                "_cache": "miss",
                "rows": len(data_rows),
                "data": data_rows,
                "_provenance": _make_provenance(latest_date, fetched_at),
            }

            if use_cache:
                save_cache(key, result)

            return result

        except requests.exceptions.ConnectionError as e:
            last_error = f"ConnectionError: {e}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
        except requests.exceptions.Timeout:
            last_error = "Timeout"
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
        except Exception as e:
            last_error = f"Unexpected error: {e}"
            break

    return {
        "dataset": dataset,
        "ticker": ticker,
        "_cache": "miss",
        "error": last_error or "Max retries exceeded",
    }


# ---------------------------------------------------------------------------
# Dataset-specific post-processing
# ---------------------------------------------------------------------------

def postprocess_institutional(data: list[dict]) -> dict:
    """三大法人: split into foreign / trust / dealer with latest summary."""
    if not data:
        return {"foreign": None, "trust": None, "dealer": None, "latest_date": None}

    latest_date = max(r["date"] for r in data)
    latest = [r for r in data if r["date"] == latest_date]

    summary: dict = {"latest_date": latest_date, "foreign": None, "trust": None, "dealer": None}
    name_map = {
        "外資": "foreign",
        "外資自營商": "foreign",
        "投信": "trust",
        "自營商": "dealer",
        "自營商(自行買賣)": "dealer",
        "自營商(避險)": "dealer",
    }
    for row in latest:
        name = row.get("name", "")
        key = name_map.get(name)
        if key and summary[key] is None:
            summary[key] = {
                "buy": row.get("buy"),
                "sell": row.get("sell"),
                "net": row.get("buy", 0) - row.get("sell", 0),
            }
    return summary


def postprocess_month_revenue(data: list[dict]) -> dict:
    """月營收: latest 12 months + YoY growth."""
    if not data:
        return {"latest": None, "history": []}

    sorted_data = sorted(data, key=lambda r: (r.get("date", ""), r.get("revenue_month", "")), reverse=True)
    latest = sorted_data[0] if sorted_data else None

    return {
        "latest": {
            "date": latest.get("date"),
            "revenue": latest.get("revenue"),
            "revenue_month": latest.get("revenue_month"),
            "revenue_year": latest.get("revenue_year"),
        } if latest else None,
        "history": sorted_data[:12],
    }


def postprocess_holding(data: list[dict]) -> dict:
    """董監持股: latest quarter."""
    if not data:
        return {"latest_date": None, "holding_pct": None, "pledged_pct": None}

    latest = max(data, key=lambda r: r.get("date", ""))
    return {
        "latest_date": latest.get("date"),
        "holding_pct": latest.get("HoldingSharesRatio"),
        "pledged_pct": latest.get("PledgeRatio"),
        "_warning": "董監持股質押率 > 50% 是治理紅旗（葉銀華 2008）",
    }


def postprocess_margin(data: list[dict]) -> dict:
    """融資融券: latest + direction signal."""
    if not data:
        return {"latest_date": None, "margin_balance": None, "short_balance": None}

    latest = max(data, key=lambda r: r.get("date", ""))
    return {
        "latest_date": latest.get("date"),
        "margin_purchase_balance": latest.get("MarginPurchaseBalance"),
        "short_sale_balance": latest.get("ShortSaleBalance"),
        "_note": (
            "融資餘額↑ = 散戶加碼多單（看漲）；融券餘額↑ = 放空部位增加（看跌）。方向相反，不可合併。"
        ),
    }


POSTPROCESSORS = {
    "TaiwanStockInstitutionalInvestorsBuySell": postprocess_institutional,
    "TaiwanStockMonthRevenue": postprocess_month_revenue,
    "TaiwanStockHoldingSharesPer": postprocess_holding,
    "TaiwanStockMarginPurchaseShortSale": postprocess_margin,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# MCP tool registration (v1.14.0+)
# ---------------------------------------------------------------------------


def register_mcp_tools(mcp) -> None:
    """Register FinMind Taiwan equity tool with a FastMCP instance."""

    @mcp.tool()
    def finmind_fetch(
        ticker: str, datasets: list[str], date_start: str,
        date_end: str | None = None,
    ) -> dict:
        """Fetch Taiwan equity data from FinMind API (Tier 2 fallback when
        MOPS/TWSE OpenAPI don't cover needed data — daily 三大法人 per-stock
        flow, historical price history, etc.). FINMIND_API_TOKEN env var
        raises rate limit from 300 to 600 req/hr.

        Supported datasets: TaiwanStockPrice (OHLCV history),
        TaiwanStockInstitutionalInvestorsBuySell (daily 三大法人 flow),
        TaiwanStockMonthRevenue, TaiwanStockHoldingSharesPer,
        TaiwanStockMarginPurchaseShortSale, TaiwanStockFinancialStatements,
        TaiwanStockProfitLossStatement.
        Dates format: YYYY-MM-DD. date_end defaults to today.
        """
        ticker_n = normalize_ticker(ticker)
        token = os.environ.get("FINMIND_API_TOKEN")
        end = date_end or datetime.now(timezone.utc).strftime("%Y-%m-%d")

        output: dict = {
            "_meta": {
                "ticker": ticker_n, "original_ticker": ticker,
                "date_start": date_start, "date_end": end,
                "auth": "token" if token else "anonymous",
            },
            "_summary": {}, "_partial": False,
        }
        has_error = False
        for dataset in datasets:
            result = fetch_dataset(ticker_n, dataset, date_start, end, token, True)
            if "error" in result:
                output["_summary"][dataset] = f"error: {result['error']}"
                output[dataset] = result
                has_error = True
                output["_partial"] = True
            else:
                output["_summary"][dataset] = (
                    f"ok ({result['rows']} rows, cache: {result['_cache']})"
                )
                processor = POSTPROCESSORS.get(dataset)
                if processor:
                    result["_processed"] = processor(result.get("data", []))
                output[dataset] = result
        return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch Taiwan equity data from FinMind API"
    )
    parser.add_argument("--ticker", required=True, help="Taiwan stock code (e.g. 2330 or 2330.TW)")
    parser.add_argument(
        "--dataset",
        required=True,
        help=(
            "FinMind dataset name(s), comma-separated. "
            f"Supported: {', '.join(sorted(KNOWN_DATASETS))}"
        ),
    )
    parser.add_argument("--date-start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument(
        "--date-end",
        default=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        help="End date (YYYY-MM-DD), default: today",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass cache and force fresh fetch",
    )
    args = parser.parse_args()

    ticker = normalize_ticker(args.ticker)
    token = os.environ.get("FINMIND_API_TOKEN")
    use_cache = not args.no_cache

    datasets = [d.strip() for d in args.dataset.split(",") if d.strip()]

    if not datasets:
        print(json.dumps({"error": "No dataset specified"}), file=sys.stderr)
        sys.exit(1)

    output: dict = {
        "_meta": {
            "ticker": ticker,
            "original_ticker": args.ticker,
            "date_start": args.date_start,
            "date_end": args.date_end,
            "auth": "token" if token else "anonymous",
            "_warning": (
                "Anonymous limit: 300 req/hr. Set FINMIND_API_TOKEN env var for 600 req/hr. "
                "Register free at https://finmindtrade.com"
            ),
        },
        "_summary": {},
        "_partial": False,
    }

    has_error = False
    for dataset in datasets:
        result = fetch_dataset(ticker, dataset, args.date_start, args.date_end, token, use_cache)

        if "error" in result:
            output["_summary"][dataset] = f"error: {result['error']}"
            output[dataset] = result
            has_error = True
            output["_partial"] = True
        else:
            output["_summary"][dataset] = f"ok ({result['rows']} rows, cache: {result['_cache']})"

            # Apply dataset-specific postprocessing for summary fields
            processor = POSTPROCESSORS.get(dataset)
            if processor:
                result["_processed"] = processor(result.get("data", []))

            output[dataset] = result

    print(json.dumps(output, ensure_ascii=False, indent=2))
    if has_error and len(datasets) == 1:
        sys.exit(1)


if __name__ == "__main__":
    main()
