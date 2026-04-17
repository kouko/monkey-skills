#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.32.3"]
# ///
"""
boj_client.py — investing-toolkit BOJ Time-Series Data Search adapter
Fetches Bank of Japan statistical time-series data.

Usage:
  uv run boj_client.py --db FM01 --code STRDCLUCON --start-date 202501
  uv run boj_client.py --db FM01 --code STRDCLUCON,STRDCLUCONH --start-date 202501
  uv run boj_client.py --db FM01 --code STRDCLUCON --start-date 202501 --end-date 202504
  uv run boj_client.py --db FM01 --code STRDCLUCON --no-cache

Auth: None required.
Cache: ~/.cache/investing-toolkit/boj/{db}_{code}_{start}_{end}.json  TTL: 24h
API docs: https://www.stat-search.boj.or.jp/info/api_guide_en.html
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests as _requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BOJ_API_BASE = "https://www.stat-search.boj.or.jp/api/v1/getDataCode"
CACHE_DIR = Path.home() / ".cache" / "investing-toolkit" / "boj"
CACHE_TTL_SECONDS = 86400  # 24 hours
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0


# ---------------------------------------------------------------------------
# Cache helpers (same pattern as fred_client.py)
# ---------------------------------------------------------------------------

def get_cache_path(db: str, code: str, start_date: str, end_date: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe_code = code.replace(",", "_")
    return CACHE_DIR / f"{db}_{safe_code}_{start_date}_{end_date}.json"


def load_cache(path: Path) -> dict | None:
    if not path.exists():
        return None
    if time.time() - path.stat().st_mtime > CACHE_TTL_SECONDS:
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def save_cache(path: Path, data: dict) -> None:
    try:
        path.write_text(json.dumps(data, default=str, indent=2))
    except Exception:
        pass


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
        if next_pos is None:
            break
        position = int(next_pos)

    return {"RESULTSET": all_resultsets}


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
    cache_path = get_cache_path(db, code, start_date, end_date)

    if use_cache:
        cached = load_cache(cache_path)
        if cached is not None:
            cached["_cache"] = "hit"
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

        result["db"] = db.upper()
        result["fetched_at"] = now
        result["_cache"] = "miss"
        result["_source"] = "boj"
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
                result["series"][sc] = entry
            else:
                result["series"][sc] = {
                    "error": f"No data returned for {sc}",
                    "series": sc,
                }

    if "error" not in result:
        save_cache(cache_path, result)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="BOJ Time-Series Data Search adapter for investing-toolkit"
    )
    parser.add_argument(
        "--db", required=True,
        help="BOJ database name (e.g. FM01, PR01, CO, MD02)",
    )
    parser.add_argument(
        "--code", required=True,
        help="Series code(s), comma-separated (e.g. STRDCLUCON or STRDCLUCON,STRDCLUCONH). NO DB prefix.",
    )
    parser.add_argument(
        "--start-date", required=True,
        help="Start date in YYYYMM format (e.g. 202501)",
    )
    parser.add_argument(
        "--end-date", default="",
        help="End date in YYYYMM format (optional, defaults to latest)",
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Bypass cache and force fresh fetch",
    )

    args = parser.parse_args()

    db = args.db.upper()
    code = args.code.strip()
    start_date = args.start_date.strip()
    end_date = args.end_date.strip()

    if args.no_cache:
        cache_path = get_cache_path(db, code, start_date, end_date)
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
