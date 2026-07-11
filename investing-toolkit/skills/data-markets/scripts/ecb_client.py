#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""
ecb_client.py — investing-toolkit ECB Data Portal CSV adapter
Fetches European Central Bank statistical time-series (SDMX, CSV endpoint).

Default: CSV endpoint at data-api.ecb.europa.eu — no API key required.
         This is the public SDMX 2.1 data API published by ECB.

Usage:
  uv run ecb_client.py --series M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA --periods 24
  uv run ecb_client.py --series M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA --dataset FM
  uv run ecb_client.py --series M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA,M.JP.JPY.4F.BB.JP10YT_RR.YLDA --periods 12

Series ID format: SDMX key of the series WITHIN a given dataset (e.g. FM).
                  Leading frequency dimension required (e.g. M. for monthly).

Auth: None required for the public Data Portal CSV endpoint.
Cache: $INVESTING_TOOLKIT_CACHE/ecb/{dataset}_{series}_{periods}.json  TTL: 24h
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
Docs: https://data.ecb.europa.eu/help/api/overview
"""

import argparse
import csv
import io
import json
import sys
import time
from datetime import datetime, timezone

import requests as _requests

import cache_util

ECB_CSV_BASE = "https://data-api.ecb.europa.eu/service/data"
DEFAULT_DATASET = "FM"  # Financial Markets dataset
CACHE_TTL_SECONDS = 86400  # 24 hours
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "ecb-jp"


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

def _safe_name(series: str) -> str:
    return series.replace("/", "_").replace(".", "_")


def _cache_key(dataset: str, series: str, periods: int) -> str:
    return f"{dataset}_{_safe_name(series)}_{periods}"


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


def _make_provenance(result: dict, dataset: str) -> dict:
    """Build _provenance block for an ECB result."""
    latest = result.get("latest")
    ref_period = latest["date"] if latest else None
    return {
        "source": f"ECB Data Portal CSV (data-api.ecb.europa.eu, dataset {dataset})",
        "source_authority": "European Central Bank (ECB)",
        "data_type": "official_supranational_statistics",
        "update_cycle": "monthly (varies by series)",
        "typical_lag": "1-3 months for real-yield / CPI-derived series",
        "fetched_at": result.get("fetched_at"),
        "reference_period": ref_period,
        "staleness_days": _compute_staleness(ref_period, result.get("fetched_at", "")),
    }


# ---------------------------------------------------------------------------
# Parse ECB SDMX CSV
# ---------------------------------------------------------------------------

def _parse_csv(raw_csv: str) -> tuple[list[dict], dict]:
    """Return (observations, metadata) parsed from the ECB CSV body.

    observations: [{'date': 'YYYY-MM' or 'YYYY-Q%d', 'value': float}]
    metadata: {'title': ..., 'unit': ..., 'frequency': ...}
    """
    reader = csv.DictReader(io.StringIO(raw_csv))
    observations: list[dict] = []
    metadata: dict = {}

    for row in reader:
        date_str = row.get("TIME_PERIOD") or ""
        value_str = row.get("OBS_VALUE")
        if value_str in (None, "", "NaN", "."):
            continue
        try:
            value = float(value_str)
        except ValueError:
            continue
        observations.append({"date": date_str, "value": value})
        # Metadata: take from any row (CSV repeats it); prefer last non-empty.
        if row.get("TITLE"):
            metadata["title"] = row["TITLE"]
        if row.get("UNIT"):
            metadata["unit"] = row["UNIT"]
        if row.get("FREQ"):
            metadata["frequency"] = row["FREQ"]

    # ECB CSV is ascending by date already; preserve order.
    return observations, metadata


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def fetch_series_raw(
    dataset: str, series: str, periods: int
) -> tuple[str, str | None]:
    """Fetch raw CSV bytes. Returns (csv_text, error_or_None)."""
    url = f"{ECB_CSV_BASE}/{dataset}/{series}"
    params = {
        "format": "csvdata",
        "lastNObservations": str(periods),
    }
    headers = {
        "User-Agent": "investing-toolkit/1.10.0",
        "Accept": "text/csv",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = _requests.get(url, params=params, headers=headers, timeout=30)
            if resp.status_code == 429 and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            if resp.status_code != 200:
                return "", f"ECB CSV HTTP {resp.status_code}"
            return resp.text, None
        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return "", "ECB CSV request timed out"
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return "", f"ECB CSV connection error: {e}"
        except Exception as e:
            return "", str(e)

    return "", "Max retries exceeded"


def fetch_series(
    dataset: str, series: str, periods: int, use_cache: bool = True
) -> dict:
    """Fetch a single ECB series with caching + provenance."""
    _log("series fetch", f"{dataset}/{series} periods={periods}")
    t0 = time.monotonic()
    cache_path = cache_util.cache_path("ecb", _cache_key(dataset, series, periods))
    if use_cache:
        cached = cache_util.load_cache(cache_path, CACHE_TTL_SECONDS)
        if cached is not None:
            cached["_cache"] = "hit"
            if "_provenance" not in cached:
                cached["_provenance"] = _make_provenance(cached, dataset)
            _log("series done", f"{dataset}/{series} cache hit")
            return cached

    raw, err = fetch_series_raw(dataset, series, periods)
    if err is not None:
        _log("series done", f"{dataset}/{series} error in {time.monotonic() - t0:.1f}s")
        return {"error": err, "series": series, "dataset": dataset}

    observations, metadata = _parse_csv(raw)
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result: dict = {
        "series": series,
        "dataset": dataset,
        "periods_requested": periods,
        "fetched_at": now,
        "_cache": "miss",
        "_source": "ecb_data_portal",
        "observations": observations,
        "latest": observations[-1] if observations else None,
        "count": len(observations),
        "metadata": metadata,
    }
    result["_provenance"] = _make_provenance(result, dataset)

    if observations:
        cache_util.save_cache(cache_path, result)

    _log("series done", f"{dataset}/{series} {len(observations)} obs in {time.monotonic() - t0:.1f}s")
    return result

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ECB Data Portal CSV adapter for investing-toolkit"
    )
    parser.add_argument(
        "--series", required=True,
        help="SDMX series key(s), comma-separated "
             "(e.g. M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA)",
    )
    parser.add_argument(
        "--dataset", default=DEFAULT_DATASET,
        help=f"ECB dataset code (default: {DEFAULT_DATASET})",
    )
    parser.add_argument(
        "--periods", type=int, default=24,
        help="Number of most-recent observations (default: 24)",
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
    dataset = args.dataset.strip().upper()
    series_list = [s.strip() for s in args.series.split(",") if s.strip()]

    if args.no_cache:
        for s in series_list:
            path = cache_util.cache_path("ecb", _cache_key(dataset, s, args.periods))
            if path.exists():
                path.unlink()

    if len(series_list) == 1:
        result = fetch_series(
            dataset, series_list[0], args.periods, use_cache=not args.no_cache
        )
    else:
        now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        result = {
            "fetched_at": now,
            "dataset": dataset,
            "series": {},
        }
        _log("batch start", f"{len(series_list)} series in dataset {dataset}")
        t_batch = time.monotonic()
        for i, s in enumerate(series_list, 1):
            _log(f"batch [{i}/{len(series_list)}]", s)
            result["series"][s] = fetch_series(
                dataset, s, args.periods, use_cache=not args.no_cache
            )
        _log("batch done", f"{len(series_list)} series in {time.monotonic() - t_batch:.1f}s")

    # Mirror fred_client: emit 'data' alias for observations for smoke-test pipes.
    if isinstance(result, dict) and "observations" in result:
        result["data"] = result["observations"]

    print(json.dumps(result, default=str, indent=2))

    has_error = (
        "error" in result
        if "observations" in result or "data" in result
        else any(
            isinstance(v, dict) and "error" in v
            for v in result.get("series", {}).values()
        )
    )
    if has_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
