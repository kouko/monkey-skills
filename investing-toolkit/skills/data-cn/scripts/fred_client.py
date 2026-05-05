#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""
fred_client.py — investing-toolkit FRED macro data adapter
Fetches Federal Reserve Economic Data series.

Default: CSV endpoint (no API key required).
Optional: JSON API endpoint (requires FRED_API_KEY, more flexible).

Usage:
  uv run fred_client.py --series T10Y2Y --periods 24
  uv run fred_client.py --series DGS10,DGS2,CPIAUCSL --periods 12
  uv run fred_client.py --series GDPC1 --periods 8
  uv run fred_client.py --series DGS10 --periods 12 --use-api   # force JSON API

Auth: FRED_API_KEY env var is optional. CSV endpoint works without it.
      Set API key for JSON API access: https://fred.stlouisfed.org/docs/api/api_key.html
Cache: $INVESTING_TOOLKIT_CACHE/fred/{series}_{periods}.json  TTL: 24h
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
"""

import argparse
import csv
import io
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import requests as _requests

FRED_CSV_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv"
FRED_API_BASE = "https://api.stlouisfed.org/fred/series/observations"
_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(Path.home() / ".cache" / "investing-toolkit")
CACHE_DIR = Path(_CACHE_BASE) / "fred"
CACHE_TTL_SECONDS = 86400  # 24 hours
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "fred-cn"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


def get_cache_path(series: str, periods: int) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{series.upper()}_{periods}.json"


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
    """Build _provenance block for a FRED result."""
    latest = result.get("latest")
    ref_period = latest["date"] if latest else None
    return {
        "source": "FRED CSV (fred.stlouisfed.org)",
        "source_authority": "Federal Reserve Bank of St. Louis",
        "data_type": "official_government_statistics",
        "update_cycle": "varies by series",
        "typical_lag": "0 days (daily) to 4 weeks (CPI/GDP)",
        "fetched_at": result.get("fetched_at"),
        "reference_period": ref_period,
        "staleness_days": _compute_staleness(ref_period, result.get("fetched_at", "")),
    }


def _build_result(series: str, periods: int, observations: list[dict], source: str) -> dict:
    valid = [o for o in observations if o.get("value") is not None]
    latest_n = valid[-periods:] if len(valid) > periods else valid
    result = {
        "series": series.upper(),
        "periods_requested": periods,
        "fetched_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_cache": "miss",
        "_source": source,
        "_warning": (
            f"FRED series {series} has publication lag — latest value may be "
            "1-4 weeks behind real-world data depending on release schedule."
        ),
        "observations": [
            {"date": o["date"], "value": o["value"]}
            for o in latest_n
        ],
        "latest": {"date": latest_n[-1]["date"], "value": latest_n[-1]["value"]} if latest_n else None,
        "count": len(latest_n),
    }
    result["_provenance"] = _make_provenance(result)
    return result


# ---------------------------------------------------------------------------
# CSV endpoint (default, no API key)
# ---------------------------------------------------------------------------

def fetch_series_csv(series: str, periods: int) -> dict:
    """Fetch via CSV endpoint. No API key required."""
    url = f"{FRED_CSV_BASE}?id={series.upper()}"

    for attempt in range(MAX_RETRIES):
        try:
            # Use requests library default UA (python-requests/X.Y.Z) — FRED's
            # bot filter blocks "Mozilla/*" and several custom UAs (verified 2026-05),
            # but accepts default python-requests + curl UAs. Don't override.
            resp = _requests.get(url, timeout=30)
            if resp.status_code == 429 and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            if resp.status_code != 200:
                return {"error": f"FRED CSV HTTP {resp.status_code}", "series": series}
            raw_csv = resp.text
            break
        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": "FRED CSV request timed out", "series": series}
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": f"FRED CSV connection error: {e}", "series": series}
        except Exception as e:
            return {"error": str(e), "series": series}

    reader = csv.reader(io.StringIO(raw_csv))
    header = next(reader, None)
    if not header:
        return {"error": f"Empty CSV response for {series}", "series": series}

    observations = []
    for row in reader:
        if len(row) >= 2:
            date_str, value_str = row[0], row[1]
            if value_str in (".", "", "N/A"):
                continue
            try:
                observations.append({"date": date_str, "value": float(value_str)})
            except ValueError:
                continue

    return _build_result(series, periods, observations, "csv")


# ---------------------------------------------------------------------------
# JSON API endpoint (requires FRED_API_KEY)
# ---------------------------------------------------------------------------

def fetch_series_api(series: str, periods: int, api_key: str) -> dict:
    """Fetch via JSON API. Requires FRED_API_KEY."""
    params = {
        "series_id": series.upper(),
        "sort_order": "desc",
        "limit": str(periods),
        "file_type": "json",
        "api_key": api_key,
    }

    for attempt in range(MAX_RETRIES):
        try:
            # Default requests UA accepted by FRED API endpoint — see CSV
            # endpoint comment in fetch_series_csv() for filter rationale.
            resp = _requests.get(
                FRED_API_BASE, params=params, timeout=15,
            )
            if resp.status_code == 429 and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt) * 2)
                continue
            if resp.status_code != 200:
                return {"error": f"FRED API HTTP {resp.status_code}", "series": series}
            raw = resp.json()
            break
        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": "FRED API request timed out", "series": series}
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": f"FRED API connection error: {e}", "series": series}
        except Exception as e:
            return {"error": str(e), "series": series}

    raw_obs = raw.get("observations", [])
    observations = []
    for o in raw_obs:
        if o.get("value") in (".", None, ""):
            continue
        try:
            observations.append({"date": o["date"], "value": float(o["value"])})
        except (ValueError, KeyError):
            continue

    observations.reverse()
    return _build_result(series, periods, observations, "api")


# ---------------------------------------------------------------------------
# Unified fetch: CSV default, API if key available and --use-api
# ---------------------------------------------------------------------------

def fetch_series(series: str, periods: int, api_key: str | None, use_api: bool) -> dict:
    _log("series fetch", f"{series} periods={periods}")
    t0 = time.monotonic()
    cache_path = get_cache_path(series, periods)
    cached = load_cache(cache_path)
    if cached:
        cached["_cache"] = "hit"
        if "_provenance" not in cached:
            cached["_provenance"] = _make_provenance(cached)
        _log("series done", f"{series} cache hit")
        return cached

    if use_api and api_key:
        result = fetch_series_api(series, periods, api_key)
    elif use_api and not api_key:
        result = fetch_series_csv(series, periods)
        result["_note"] = "--use-api requested but FRED_API_KEY not set; fell back to CSV"
    else:
        result = fetch_series_csv(series, periods)

    if "error" not in result:
        save_cache(cache_path, result)

    if "error" in result:
        _log("series done", f"{series} error in {time.monotonic() - t0:.1f}s")
    else:
        _log("series done", f"{series} {result.get('count', 0)} obs in {time.monotonic() - t0:.1f}s")
    return result



def main():
    parser = argparse.ArgumentParser(description="FRED macro data adapter for investing-toolkit")
    parser.add_argument("--series", required=True,
                        help="FRED series ID(s), comma-separated (e.g. T10Y2Y,DGS10,CPIAUCSL)")
    parser.add_argument("--periods", type=int, default=24,
                        help="Number of most-recent observations to return (default: 24)")
    parser.add_argument("--use-api", action="store_true",
                        help="Use JSON API instead of CSV (requires FRED_API_KEY)")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress logging on stderr (default: verbose)")

    args = parser.parse_args()
    global _QUIET
    _QUIET = args.quiet
    api_key = os.environ.get("FRED_API_KEY")

    series_list = [s.strip().upper() for s in args.series.split(",") if s.strip()]

    if args.no_cache:
        for s in series_list:
            path = get_cache_path(s, args.periods)
            if path.exists():
                path.unlink()

    if len(series_list) == 1:
        result = fetch_series(series_list[0], args.periods, api_key, args.use_api)
    else:
        # Multi-series: fetch concurrently to avoid cumulative latency on N-series
        # regime-pack workloads. FRED public CSV endpoint has no documented
        # concurrency limit; ~120 req/min rate limit shared across all callers
        # of an IP. Default 8 workers stays comfortably under (max ~60 req/min).
        # Override via FRED_MAX_WORKERS env var (set to 1 to force serial).
        max_workers = max(1, int(os.environ.get("FRED_MAX_WORKERS", "8")))
        _log("batch start", f"{len(series_list)} series workers={max_workers}")
        t_batch = time.monotonic()
        result = {
            "fetched_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "series": {},
        }
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {
                ex.submit(fetch_series, s, args.periods, api_key, args.use_api): s
                for s in series_list
            }
            for fut in as_completed(futures):
                sid = futures[fut]
                try:
                    result["series"][sid] = fut.result()
                except Exception as e:
                    result["series"][sid] = {"error": f"fetch_failed: {e}", "series": sid}
        _log("batch done", f"{len(series_list)} series in {time.monotonic() - t_batch:.1f}s")

    print(json.dumps(result, default=str, indent=2))

    has_error = (
        "error" in result
        if len(series_list) == 1
        else any("error" in v for v in result.get("series", {}).values())
    )
    if has_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
