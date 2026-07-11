#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""
boj_client.py — investing-toolkit BOJ Time-Series Data Search adapter
Fetches Bank of Japan statistical time-series data.

Usage:
  uv run boj_client.py --db FM01 --code STRDCLUCON --start-date 202501
  uv run boj_client.py --db FM01 --code STRDCLUCON,STRDCLUCONH --start-date 202501
  uv run boj_client.py --db FM01 --code STRDCLUCON --start-date 202501 --end-date 202504
  uv run boj_client.py --db FM01 --code STRDCLUCON --no-cache

Convenience preset — Tankan 企業物価見通し (Average Inflation Outlook, CPI-based):
  uv run boj_client.py --tankan-price-outlook --horizons 1,3,5 --periods 8
  uv run boj_client.py --tankan-price-outlook                       # 1Y/3Y/5Y, 8 quarters

  Maps to DB=CO codes:
    TK99F0000204HCQ00000  Outlook for General Prices / 1 year ahead
    TK99F0000205HCQ00000  Outlook for General Prices / 3 years ahead
    TK99F0000206HCQ00000  Outlook for General Prices / 5 years ahead
  All: All Enterprises / All industries / Average of Enterprises' Inflation Outlook.

Convenience preset — Tankan 業況判断 DI (Business Conditions Diffusion Index):
  uv run boj_client.py --tankan-business-di --periods 8

  Maps to DB=CO codes (Simple aggregate / Actual / Ordinary figures):
    TK99F1000601GCQ01000  Large Enterprises / Manufacturing
    TK99F2000601GCQ01000  Large Enterprises / Non-manufacturing
    TK99F1000601GCQ03000  Small Enterprises / Manufacturing
    TK99F2000601GCQ03000  Small Enterprises / Non-manufacturing
  Series-code structure verified via stat-search.boj.or.jp/info/tankan_code_en.html.
  Used by analysis-macro-regime/classify_jp.py for native business-sentiment overlay.

Auth: None required.
Cache: $INVESTING_TOOLKIT_CACHE/boj/{db}_{code}_{start}_{end}.json  TTL: 24h
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
API docs: https://www.stat-search.boj.or.jp/info/api_guide_en.html
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import requests as _requests

import cache_util

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BOJ_API_BASE = "https://www.stat-search.boj.or.jp/api/v1/getDataCode"
CACHE_TTL_SECONDS = 86400  # 24 hours
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "boj-jp"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------
# Cache helpers — lazy cache_util usage (no import-time filesystem side
# effects; directory/path resolution happens only when a fetch actually runs).
# ---------------------------------------------------------------------------

def _cache_key(db: str, code: str, start_date: str, end_date: str) -> str:
    safe_code = "_".join(sorted(c.strip() for c in code.split(",") if c.strip()))
    return f"{db}_{safe_code}_{start_date}_{end_date}"


# ---------------------------------------------------------------------------
# API fetch with retry + pagination
# ---------------------------------------------------------------------------

def _fetch_page(
    db: str, code: str, start_date: str, end_date: str, start_position: int | None = None,
) -> dict:
    """Fetch a single page from the BOJ API. Returns raw JSON response."""
    params: dict = {
        "format": "json",
        "lang": "en",
        "db": db.upper(),
        "code": code,
        "startDate": start_date,
    }
    if end_date:
        params["endDate"] = end_date
    if start_position is not None:
        params["startPosition"] = str(start_position)

    headers = {
        "User-Agent": "investing-toolkit/1.3.0",
        "Accept-Encoding": "gzip",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = _requests.get(BOJ_API_BASE, params=params, timeout=30, headers=headers)

            if resp.status_code == 429 and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue

            if resp.status_code != 200:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                return {"error": f"BOJ API HTTP {resp.status_code}", "code": code}

            body = resp.json()

            # BOJ API-level error handling
            status = body.get("STATUS")
            if status and status != 200:
                msg = body.get("MESSAGE", "Unknown API error")
                return {"error": f"BOJ API STATUS {status}: {msg}", "code": code}

            return body

        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": "BOJ API request timed out", "code": code}
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": f"BOJ API connection error: {e}", "code": code}
        except Exception as e:
            return {"error": str(e), "code": code}

    return {"error": "Max retries exceeded", "code": code}


def fetch_all_pages(
    db: str, code: str, start_date: str, end_date: str,
) -> dict:
    """Fetch all pages, auto-paginating when NEXTPOSITION is not null."""
    all_resultsets: list[dict] = []
    position: int | None = None

    while True:
        body = _fetch_page(db, code, start_date, end_date, start_position=position)
        if "error" in body:
            return body

        resultset = body.get("RESULTSET", [])
        all_resultsets.extend(resultset)

        next_pos = body.get("NEXTPOSITION")
        if not next_pos or str(next_pos) == "null":
            break
        position = int(next_pos)

    return {"RESULTSET": all_resultsets}


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
    """Build _provenance block for a BOJ result."""
    latest = result.get("latest")
    ref_period = latest["date"] if latest else None
    return {
        "source": "BOJ Time-Series Data Search (stat-search.boj.or.jp)",
        "source_authority": "Bank of Japan (日本銀行)",
        "data_type": "official_government_statistics",
        "update_cycle": "daily",  # BOJ updates at 8:50 AM JST
        "typical_lag": "0-1 business days",
        "fetched_at": result.get("fetched_at"),
        "reference_period": ref_period,
        "staleness_days": _compute_staleness(ref_period, result.get("fetched_at", "")),
    }


# ---------------------------------------------------------------------------
# Parse RESULTSET into observations
# ---------------------------------------------------------------------------

def _parse_series(series_entry: dict) -> dict:
    """Parse a single RESULTSET entry into the output contract format."""
    code = series_entry.get("SERIES_CODE", "")
    name = series_entry.get("NAME_OF_TIME_SERIES", "")
    unit = series_entry.get("UNIT", "")
    frequency = series_entry.get("FREQUENCY", "")

    values_block = series_entry.get("VALUES", {})
    survey_dates = values_block.get("SURVEY_DATES", [])
    raw_values = values_block.get("VALUES", [])

    observations: list[dict] = []
    for date_val, val in zip(survey_dates, raw_values):
        # Skip null/missing values (BOJ uses "null" string or None)
        if val is None or val == "null" or val == "":
            continue
        try:
            observations.append({
                "date": str(date_val),
                "value": float(val),
            })
        except (ValueError, TypeError):
            continue

    latest = observations[-1] if observations else None

    return {
        "series": code,
        "name": name,
        "unit": unit,
        "frequency": frequency,
        "observations": observations,
        "latest": latest,
        "count": len(observations),
    }


# ---------------------------------------------------------------------------
# Main fetch: cache + fetch + parse
# ---------------------------------------------------------------------------

def fetch_series(
    db: str, code: str, start_date: str, end_date: str, use_cache: bool = True,
) -> dict:
    """Fetch BOJ series with caching."""
    _log("series fetch", f"db={db} code={code} start={start_date}")
    t0 = time.monotonic()
    cache_path = cache_util.cache_path("boj", _cache_key(db, code, start_date, end_date))

    if use_cache:
        cached = cache_util.load_cache(cache_path, CACHE_TTL_SECONDS)
        if cached is not None:
            cached["_cache"] = "hit"
            # Patch per-entry _cache for multi-series responses
            if isinstance(cached.get("series"), dict):
                for v in cached["series"].values():
                    if isinstance(v, dict):
                        v["_cache"] = "hit"
                        if "_provenance" not in v:
                            v["_provenance"] = _make_provenance(v)
            else:
                if "_provenance" not in cached:
                    cached["_provenance"] = _make_provenance(cached)
            _log("series done", f"db={db} code={code} cache hit")
            return cached

    body = fetch_all_pages(db, code, start_date, end_date)
    if "error" in body:
        body["series"] = code
        return body

    resultset = body.get("RESULTSET", [])

    # Build a mapping of series code -> parsed data
    series_map: dict[str, dict] = {}
    for entry in resultset:
        parsed = _parse_series(entry)
        sc = parsed["series"]
        if sc in series_map:
            # Merge observations from paginated results for the same series
            series_map[sc]["observations"].extend(parsed["observations"])
            series_map[sc]["count"] = len(series_map[sc]["observations"])
            if parsed["latest"]:
                series_map[sc]["latest"] = parsed["latest"]
        else:
            series_map[sc] = parsed

    codes_requested = [c.strip() for c in code.split(",") if c.strip()]

    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if len(codes_requested) == 1:
        sc = codes_requested[0]
        if sc in series_map:
            result = series_map[sc]
        else:
            # Try to find by matching (API may return different casing)
            found = next(iter(series_map.values()), None)
            if found:
                result = found
            else:
                return {"error": f"No data returned for {sc}", "series": sc}

        # Always overwrite series with requested code (API may omit SERIES_CODE)
        result["series"] = sc
        result["db"] = db.upper()
        result["fetched_at"] = now
        result["_cache"] = "miss"
        result["_source"] = "boj"
        result["_provenance"] = _make_provenance(result)
    else:
        # Multi-series: wrap in {"series": {...}}
        result = {
            "fetched_at": now,
            "_cache": "miss",
            "_source": "boj",
            "db": db.upper(),
            "series": {},
        }
        for sc in codes_requested:
            if sc in series_map:
                entry = series_map[sc]
                entry["db"] = db.upper()
                entry["fetched_at"] = now
                entry["_cache"] = "miss"
                entry["_source"] = "boj"
                entry["_provenance"] = _make_provenance(entry)
                result["series"][sc] = entry
            else:
                result["series"][sc] = {
                    "error": f"No data returned for {sc}",
                    "series": sc,
                }

    if "error" not in result:
        cache_util.save_cache(cache_path, result)

    _log("series done", f"db={db} code={code} in {time.monotonic() - t0:.1f}s")
    return result


# ---------------------------------------------------------------------------
# Tankan 企業物価見通し — CPI-based expected inflation preset
# ---------------------------------------------------------------------------
#
# Series key: "Outlook for General Prices / N year(s) ahead /
#              The Average of Enterprises' Inflation Outlook /
#              All Enterprises / All industries" (unit: %-change, quarterly)
# Source: BOJ Tankan (短観) — stat-search DB "CO".
# Reference period dimension uses CQ (calendar-quarter, 20XXQQ).

TANKAN_PRICE_OUTLOOK_CODES: dict[int, str] = {
    1: "TK99F0000204HCQ00000",   # 1Y ahead
    3: "TK99F0000205HCQ00000",   # 3Y ahead
    5: "TK99F0000206HCQ00000",   # 5Y ahead
}

# ---------------------------------------------------------------------------
# Tankan 業況判断 DI — Business Conditions Diffusion Index preset
# ---------------------------------------------------------------------------
#
# Series-code structure (per stat-search.boj.or.jp/info/tankan_code_en.html):
#   CO db, prefix TK99 + F (simple aggregate) + industry (1=mfg, 2=nonmfg)
#   + 000 + 601 (Business Conditions DI) + G (DI) + CQ (quarterly) + 0
#   (actual) + size (1=large, 3=small) + 000 (ordinary figure).
# Categories surveyed by classify_jp.py:
TANKAN_BUSINESS_DI_CODES: dict[str, str] = {
    "large_mfg": "TK99F1000601GCQ01000",
    "large_nonmfg": "TK99F2000601GCQ01000",
    "small_mfg": "TK99F1000601GCQ03000",
    "small_nonmfg": "TK99F2000601GCQ03000",
}


def _periods_to_start_yyyymm(periods: int, freq: str = "quarterly") -> str:
    """Rough backward calendar offset from today for --periods semantics.

    The BOJ API uses calendar dates, not an N-most-recent filter, so we
    translate --periods (quarters for Tankan) into a conservative start
    date that is guaranteed to cover `periods` most-recent observations.

    For quarterly series (CQ freq) the "MM" segment must be a valid
    quarter number 01-04 (not a month), so we always return YYYY01 with
    a year offset that covers `periods` quarters + a safety buffer.
    """
    today = datetime.now(tz=timezone.utc)
    if freq == "quarterly":
        years_back = (periods // 4) + 2  # +2 years safety margin
        year = today.year - years_back
        return f"{year:04d}01"
    months_back = periods + 2
    year = today.year
    month = today.month - months_back
    while month <= 0:
        month += 12
        year -= 1
    return f"{year:04d}{month:02d}"

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="BOJ Time-Series Data Search adapter for investing-toolkit"
    )
    parser.add_argument(
        "--db", default=None,
        help="BOJ database name (e.g. FM01, PR01, CO, MD02)",
    )
    parser.add_argument(
        "--code", default=None,
        help="Series code(s), comma-separated (e.g. STRDCLUCON or STRDCLUCON,STRDCLUCONH). NO DB prefix.",
    )
    parser.add_argument(
        "--start-date", default=None,
        help="Start date in YYYYMM format (e.g. 202501)",
    )
    parser.add_argument(
        "--end-date", default="",
        help="End date in YYYYMM format (optional, defaults to latest)",
    )
    parser.add_argument(
        "--tankan-price-outlook", action="store_true",
        help="Fetch Tankan 企業物価見通し (Average Inflation Outlook, CPI-based). "
             "Pairs with --horizons and --periods.",
    )
    parser.add_argument(
        "--tankan-business-di", action="store_true",
        help="Fetch Tankan 業況判断 DI (Business Conditions DI) across 4 "
             "categories (large/small × mfg/non-mfg). Pairs with --periods.",
    )
    parser.add_argument(
        "--horizons", default="1,3,5",
        help="Comma-separated horizons in years for --tankan-price-outlook "
             "(default: 1,3,5). Valid: 1, 3, 5.",
    )
    parser.add_argument(
        "--periods", type=int, default=8,
        help="Number of most-recent quarterly observations to retain "
             "for --tankan-price-outlook (default: 8).",
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Bypass cache and force fresh fetch",
    )
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress logging on stderr (default: verbose)")

    args = parser.parse_args()
    global _QUIET
    _QUIET = args.quiet

    # ---- Tankan business DI preset path -------------------------------------
    if args.tankan_business_di:
        db = "CO"
        codes = ",".join(TANKAN_BUSINESS_DI_CODES.values())
        start_date = _periods_to_start_yyyymm(args.periods, freq="quarterly")
        end_date = ""

        if args.no_cache:
            cache_path = cache_util.cache_path("boj", _cache_key(db, codes, start_date, end_date))
            if cache_path.exists():
                cache_path.unlink()

        raw = fetch_series(db, codes, start_date, end_date, use_cache=not args.no_cache)

        category_by_code = {v: k for k, v in TANKAN_BUSINESS_DI_CODES.items()}
        if "series" in raw and isinstance(raw["series"], dict):
            for sc, entry in raw["series"].items():
                if isinstance(entry, dict) and "observations" in entry:
                    obs = entry["observations"][-args.periods:]
                    entry["observations"] = obs
                    entry["count"] = len(obs)
                    entry["latest"] = obs[-1] if obs else None
                    entry["category"] = category_by_code.get(sc)
                    entry["indicator"] = "tankan_business_di"

        raw["_preset"] = "tankan-business-di"
        print(json.dumps(raw, default=str, indent=2))

        if "error" in raw:
            sys.exit(1)
        if "series" in raw and isinstance(raw["series"], dict):
            if any("error" in v for v in raw["series"].values() if isinstance(v, dict)):
                sys.exit(1)
        return

    # ---- Tankan price outlook preset path -----------------------------------
    if args.tankan_price_outlook:
        try:
            horizons = [int(h.strip()) for h in args.horizons.split(",") if h.strip()]
        except ValueError:
            print(json.dumps({"error": "Invalid --horizons; expected integers."}))
            sys.exit(2)
        bad = [h for h in horizons if h not in TANKAN_PRICE_OUTLOOK_CODES]
        if bad:
            print(json.dumps({
                "error": f"Unsupported horizons {bad}. Valid: {sorted(TANKAN_PRICE_OUTLOOK_CODES)}.",
            }))
            sys.exit(2)

        db = "CO"
        codes = ",".join(TANKAN_PRICE_OUTLOOK_CODES[h] for h in horizons)
        start_date = _periods_to_start_yyyymm(args.periods, freq="quarterly")
        end_date = ""

        if args.no_cache:
            cache_path = cache_util.cache_path("boj", _cache_key(db, codes, start_date, end_date))
            if cache_path.exists():
                cache_path.unlink()

        raw = fetch_series(db, codes, start_date, end_date, use_cache=not args.no_cache)

        # Trim each series to last N observations and add horizon tag.
        horizon_by_code = {TANKAN_PRICE_OUTLOOK_CODES[h]: h for h in horizons}
        if "series" in raw and isinstance(raw["series"], dict):
            for sc, entry in raw["series"].items():
                if isinstance(entry, dict) and "observations" in entry:
                    obs = entry["observations"][-args.periods:]
                    entry["observations"] = obs
                    entry["count"] = len(obs)
                    entry["latest"] = obs[-1] if obs else None
                    entry["horizon_years"] = horizon_by_code.get(sc)
                    entry["indicator"] = "tankan_inflation_outlook"
        elif "observations" in raw:
            # Single-horizon case.
            obs = raw["observations"][-args.periods:]
            raw["observations"] = obs
            raw["count"] = len(obs)
            raw["latest"] = obs[-1] if obs else None
            raw["horizon_years"] = horizon_by_code.get(raw.get("series", ""))
            raw["indicator"] = "tankan_inflation_outlook"

        raw["_preset"] = "tankan-price-outlook"
        print(json.dumps(raw, default=str, indent=2))

        if "error" in raw:
            sys.exit(1)
        if "series" in raw and isinstance(raw["series"], dict):
            if any("error" in v for v in raw["series"].values() if isinstance(v, dict)):
                sys.exit(1)
        return

    # ---- Generic path -------------------------------------------------------
    if not args.db or not args.code or not args.start_date:
        parser.error("--db, --code, and --start-date are required "
                     "(or use --tankan-price-outlook / --tankan-business-di).")

    db = args.db.upper()
    code = args.code.strip()
    start_date = args.start_date.strip()
    end_date = args.end_date.strip()

    if args.no_cache:
        cache_path = cache_util.cache_path("boj", _cache_key(db, code, start_date, end_date))
        if cache_path.exists():
            cache_path.unlink()

    result = fetch_series(db, code, start_date, end_date, use_cache=not args.no_cache)

    print(json.dumps(result, default=str, indent=2))

    # Determine exit code
    codes_requested = [c.strip() for c in code.split(",") if c.strip()]
    if len(codes_requested) == 1:
        has_error = "error" in result
    else:
        has_error = any(
            "error" in v
            for v in result.get("series", {}).values()
            if isinstance(v, dict)
        )

    if has_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
