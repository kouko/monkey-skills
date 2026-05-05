#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""
cbc_client.py — investing-toolkit Central Bank of the Republic of China (Taiwan) adapter
Fetches CBC statistical data from cpx.cbc.gov.tw API.

Usage:
  uv run cbc_client.py --item EG2AM01en                          # Rediscount Rate
  uv run cbc_client.py --item EG2AM01en,EF15M01en                # Multiple items
  uv run cbc_client.py --preset rediscount-rate                   # Use preset alias
  uv run cbc_client.py --preset rediscount-rate,m2                # Multiple presets
  uv run cbc_client.py --preset all                               # All presets
  uv run cbc_client.py --item EG2AM01en --no-cache                # Force fresh fetch

Auth: None required.
Cache: $INVESTING_TOOLKIT_CACHE/cbc/{item_code}.json  TTL: 24h
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
API: https://cpx.cbc.gov.tw/API/DataAPI/Get?FileName={ItemCode}
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import urllib3
import requests as _requests

# Suppress InsecureRequestWarning — CBC server has a known SSL certificate
# issue (missing Subject Key Identifier). verify=False is required.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CBC_API_BASE = "https://cpx.cbc.gov.tw/API/DataAPI/Get"
_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(Path.home() / ".cache" / "investing-toolkit")
CACHE_DIR = Path(_CACHE_BASE) / "cbc"
CACHE_TTL_SECONDS = 86400  # 24 hours
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0

# ---------------------------------------------------------------------------
# Preset aliases
# ---------------------------------------------------------------------------

PRESETS: dict[str, str] = {
    "rediscount-rate": "EG2AM01en",       # 重貼現率
    "m2": "EF15M01en",                    # 貨幣總計數 M2
    "m2-factors": "EF21M01en",            # M2 變動因素
    "twdusd": "BP01D01",                  # TWD/USD 匯率 (中文版, daily)
    "reserve-money": "EF11M01en",         # 準備貨幣
    "financial-sa": "EF10M01en",          # 季調金融指標
    "rates-daily": "EG28D01en",           # 央行利率 (daily)
}

INDICATOR_NAMES: dict[str, str] = {
    "EG2AM01en": "Rediscount Rate (重貼現率)",
    "EF15M01en": "Monetary Aggregates M2 (貨幣總計數 M2)",
    "EF21M01en": "Factors Affecting M2 (M2 變動因素)",
    "BP01D01": "TWD/USD Exchange Rate (新臺幣對美元匯率)",
    "EF11M01en": "Reserve Money (準備貨幣)",
    "EF10M01en": "Seasonally Adjusted Financial Indicators (季調金融指標)",
    "EG28D01en": "CBC Interest Rates Daily (央行利率)",
}


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "cbc-tw"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------
# Cache helpers (same pattern as fred_client.py / boj_client.py)
# ---------------------------------------------------------------------------

def get_cache_path(item_code: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{item_code}.json"


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
        path.write_text(json.dumps(data, default=str, indent=2, ensure_ascii=False))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Provenance helpers
# ---------------------------------------------------------------------------

def _compute_staleness(latest_date_str: str | None) -> int | None:
    """Compute days between reference period and now."""
    if not latest_date_str:
        return None
    try:
        clean = latest_date_str.replace("-", "").replace("/", "")
        if len(clean) == 6:
            clean += "01"
        if len(clean) == 8:
            ref = datetime.strptime(clean[:8], "%Y%m%d").replace(tzinfo=timezone.utc)
        else:
            return None
        now = datetime.now(tz=timezone.utc)
        return (now - ref).days
    except (ValueError, TypeError):
        return None


def _make_provenance(result: dict) -> dict:
    """Build _provenance block for a CBC result."""
    latest = result.get("latest")
    ref_period = latest["date"] if latest else None
    return {
        "source": "CBC Statistical Data (cpx.cbc.gov.tw)",
        "source_authority": "Central Bank of the Republic of China (Taiwan) (中央銀行)",
        "data_type": "official_government_statistics",
        "update_cycle": "varies by indicator",
        "typical_lag": "1-4 weeks after reference period",
        "fetched_at": result.get("fetched_at"),
        "reference_period": ref_period,
        "staleness_days": _compute_staleness(ref_period),
    }


# ---------------------------------------------------------------------------
# API fetch with retry
# ---------------------------------------------------------------------------

def _fetch_item(item_code: str) -> dict:
    """Fetch a single item from the CBC API."""
    params = {"FileName": item_code}
    headers = {
        "User-Agent": "investing-toolkit/1.4.0",
        "Accept-Encoding": "gzip",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = _requests.get(
                CBC_API_BASE, params=params, timeout=30, headers=headers,
                verify=False,  # CBC SSL cert missing Subject Key Identifier
            )

            if resp.status_code == 429 and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue

            if resp.status_code != 200:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                return {"error": f"CBC API HTTP {resp.status_code}", "item": item_code}

            return resp.json()

        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": "CBC API request timed out", "item": item_code}
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": f"CBC API connection error: {e}", "item": item_code}
        except Exception as e:
            return {"error": str(e), "item": item_code}

    return {"error": "Max retries exceeded", "item": item_code}


# ---------------------------------------------------------------------------
# Parse CBC JSON response
# ---------------------------------------------------------------------------

def _parse_observations(body: dict, item_code: str) -> list[dict]:
    """Parse CBC JSON into a list of {date, value} observations.

    CBC response format:
    {
      "meta": {...},
      "data": {
        "dataSets": [[period, value, ...], ...],
        "structure": {...}
      }
    }

    The dataSets array contains sub-arrays where:
    - Index 0 is typically the period (e.g. "2026M02", "20260331")
    - Index 1 is typically the value
    """
    try:
        data = body.get("data", {})
        datasets = data.get("dataSets", [])
    except (AttributeError, TypeError):
        return []

    observations: list[dict] = []

    for row in datasets:
        if not isinstance(row, list) or len(row) < 2:
            continue

        raw_period = str(row[0])
        raw_value = row[1]

        if raw_value is None or raw_value == "" or raw_value == "null":
            continue

        # Normalize period to YYYYMM or YYYYMMDD
        date = _normalize_period(raw_period)
        if not date:
            continue

        try:
            value = float(raw_value)
        except (ValueError, TypeError):
            continue

        observations.append({"date": date, "value": value})

    # Sort chronologically
    observations.sort(key=lambda o: o["date"])
    return observations


def _normalize_period(raw: str) -> str | None:
    """Normalize CBC period formats to YYYYMM or YYYYMMDD.

    Known formats:
    - "2026M02" -> "202602"
    - "20260331" -> "20260331"
    - "2026-03" -> "202603"
    - "2026Q1" -> "202603" (end of quarter)
    """
    raw = raw.strip()

    # "2026M02" format
    if "M" in raw.upper():
        parts = raw.upper().split("M")
        if len(parts) == 2:
            year = parts[0].strip()
            month = parts[1].strip().zfill(2)
            if year.isdigit() and month.isdigit():
                return f"{year}{month}"

    # "2026Q1" format -> end of quarter month
    if "Q" in raw.upper():
        parts = raw.upper().split("Q")
        if len(parts) == 2:
            year = parts[0].strip()
            quarter = parts[1].strip()
            quarter_end = {"1": "03", "2": "06", "3": "09", "4": "12"}
            if year.isdigit() and quarter in quarter_end:
                return f"{year}{quarter_end[quarter]}"

    # "YYYYMMDD" format (8 digits)
    digits = "".join(c for c in raw if c.isdigit())
    if len(digits) == 8:
        return digits

    # "YYYY-MM" or "YYYYMM" format
    if len(digits) == 6:
        return digits

    # "YYYY" format (annual)
    if len(digits) == 4:
        return f"{digits}12"  # Use December as reference

    return None


# ---------------------------------------------------------------------------
# Unified fetch: cache + fetch + parse
# ---------------------------------------------------------------------------

def fetch_item(item_code: str, use_cache: bool = True, preset: str | None = None) -> dict:
    """Fetch a single CBC item with caching."""
    label = preset or item_code
    _log("item fetch", label)
    t0 = time.monotonic()
    cache_path = get_cache_path(item_code)

    if use_cache:
        cached = load_cache(cache_path)
        if cached is not None:
            cached["_cache"] = "hit"
            if "_provenance" not in cached:
                cached["_provenance"] = _make_provenance(cached)
            _log("item done", f"{label} cache hit")
            return cached

    body = _fetch_item(item_code)
    if "error" in body:
        _log("item done", f"{label} error in {time.monotonic() - t0:.1f}s")
        return body

    observations = _parse_observations(body, item_code)

    name = INDICATOR_NAMES.get(item_code, preset or item_code)
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    latest = observations[-1] if observations else None
    prior = observations[-2] if len(observations) >= 2 else None

    # Compute direction
    direction = None
    if latest and prior:
        if latest["value"] > prior["value"]:
            direction = "Rising"
        elif latest["value"] < prior["value"]:
            direction = "Falling"
        else:
            direction = "Flat"

    result: dict = {
        "item": item_code,
        "preset": preset,
        "name": name,
        "fetched_at": now,
        "_cache": "miss",
        "_source": "cbc",
        "observations": observations,
        "latest": latest,
        "prior": prior,
        "direction": direction,
        "count": len(observations),
    }
    result["_provenance"] = _make_provenance(result)

    if "error" not in result:
        save_cache(cache_path, result)

    _log("item done", f"{label} {len(observations)} obs in {time.monotonic() - t0:.1f}s")
    return result

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="CBC (Central Bank of Taiwan) data adapter for investing-toolkit",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--item",
        help="Item code(s), comma-separated (e.g. EG2AM01en,EF15M01en)",
    )
    group.add_argument(
        "--preset",
        help="Preset alias(es), comma-separated (e.g. rediscount-rate,m2) or 'all'",
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

    # Resolve targets: list of (item_code, preset_alias_or_None)
    targets: list[tuple[str, str | None]] = []

    if args.preset:
        if args.preset.strip().lower() == "all":
            targets = [(code, alias) for alias, code in PRESETS.items()]
        else:
            for alias in args.preset.split(","):
                alias = alias.strip()
                if not alias:
                    continue
                code = PRESETS.get(alias.lower())
                if code is None:
                    print(
                        json.dumps(
                            {"error": f"Unknown preset: {alias}", "available_presets": list(PRESETS.keys())},
                            indent=2, ensure_ascii=False,
                        )
                    )
                    sys.exit(1)
                targets.append((code, alias))
    else:
        for code in args.item.split(","):
            code = code.strip()
            if not code:
                continue
            alias = next((k for k, v in PRESETS.items() if v == code), None)
            targets.append((code, alias))

    if not targets:
        print(json.dumps({"error": "No items specified"}, indent=2))
        sys.exit(1)

    # Clear cache if requested
    if args.no_cache:
        for item_code, _ in targets:
            cache_path = get_cache_path(item_code)
            if cache_path.exists():
                cache_path.unlink()

    # Fetch
    if len(targets) == 1:
        item_code, preset = targets[0]
        result = fetch_item(item_code, use_cache=not args.no_cache, preset=preset)
    else:
        result = {
            "fetched_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "_source": "cbc",
            "items": {},
        }
        _log("batch start", f"{len(targets)} items")
        t_batch = time.monotonic()
        for i, (item_code, preset) in enumerate(targets, 1):
            key = preset if preset else item_code
            _log(f"batch [{i}/{len(targets)}]", key)
            data = fetch_item(item_code, use_cache=not args.no_cache, preset=preset)
            result["items"][key] = data
        _log("batch done", f"{len(targets)} items in {time.monotonic() - t_batch:.1f}s")

    print(json.dumps(result, default=str, indent=2, ensure_ascii=False))

    # Determine exit code
    if len(targets) == 1:
        has_error = "error" in result
    else:
        has_error = any(
            "error" in v
            for v in result.get("items", {}).values()
            if isinstance(v, dict)
        )

    if has_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
