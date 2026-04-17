#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.32.3"]
# ///
"""
estat_client.py — investing-toolkit e-Stat Dashboard API adapter
Fetches Japan's Statistics Dashboard (統計ダッシュボード) macro data.

Usage:
  uv run estat_client.py --indicator 0703010501010030000
  uv run estat_client.py --indicator 0703010501010030000,0301010000020020010
  uv run estat_client.py --preset cpi
  uv run estat_client.py --preset cpi,unemployment,jgb10y
  uv run estat_client.py --search "Consumer Price Index"
  uv run estat_client.py --preset cpi --cycle quarterly --no-cache

Auth: None required. Free API.
Cache: ~/.cache/investing-toolkit/estat/{indicator}_{cycle}.json  TTL: 24h
API docs: https://dashboard.e-stat.go.jp
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

ESTAT_DATA_BASE = "https://dashboard.e-stat.go.jp/api/1.0/Json/getData"
ESTAT_SEARCH_BASE = "https://dashboard.e-stat.go.jp/api/1.0/Json/getIndicatorInfo"
CACHE_DIR = Path.home() / ".cache" / "investing-toolkit" / "estat"
CACHE_TTL_SECONDS = 86400  # 24 hours
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0

# ---------------------------------------------------------------------------
# Preset aliases
# ---------------------------------------------------------------------------

PRESETS: dict[str, str] = {
    "cpi": "0703010501010030000",
    "core-cpi": "0703010501010030010",
    "core-core-cpi": "0703010501010030020",
    "unemployment": "0301010000020020010",
    "ip": "0502070301000090010",
    "jgb10y": "0702020300000010020",
}

INDICATOR_NAMES: dict[str, str] = {
    "0703010501010030000": "CPI (All items) YoY%",
    "0703010501010030010": "Core CPI (less fresh food) YoY%",
    "0703010501010030020": "Core-core CPI YoY%",
    "0301010000020020010": "Unemployment Rate",
    "0502070301000090010": "Industrial Production Index 2020 base",
    "0702020300000010020": "10Y JGB Yield (month-end)",
}

CYCLE_MAP: dict[str, str] = {
    "monthly": "1",
    "quarterly": "2",
    "yearly": "3",
}


# ---------------------------------------------------------------------------
# Cache helpers (same pattern as fred_client.py / boj_client.py)
# ---------------------------------------------------------------------------

def get_cache_path(indicator: str, cycle: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{indicator}_{cycle}.json"


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
# Time normalization
# ---------------------------------------------------------------------------

def normalize_time(raw_time: str) -> str:
    """Normalize @time format: YYYYMMDD or YYYYMM00 -> YYYYMM."""
    # Strip any non-digit characters
    digits = "".join(c for c in raw_time if c.isdigit())
    if len(digits) >= 6:
        return digits[:6]
    return digits


# ---------------------------------------------------------------------------
# API fetch with retry
# ---------------------------------------------------------------------------

def _fetch_data(indicator: str, cycle: str) -> dict:
    """Fetch a single indicator from the e-Stat Dashboard API."""
    params: dict = {
        "Lang": "EN",
        "IndicatorCode": indicator,
        "RegionalRank": "2",
        "Cycle": cycle,
        "IsSeasonalAdjustment": "1",
        "MetaGetFlg": "Y",
    }

    headers = {
        "User-Agent": "investing-toolkit/1.3.0",
        "Accept-Encoding": "gzip",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = _requests.get(
                ESTAT_DATA_BASE, params=params, timeout=30, headers=headers,
            )

            if resp.status_code == 429 and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue

            if resp.status_code != 200:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                return {"error": f"e-Stat API HTTP {resp.status_code}", "indicator": indicator}

            return resp.json()

        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": "e-Stat API request timed out", "indicator": indicator}
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": f"e-Stat API connection error: {e}", "indicator": indicator}
        except Exception as e:
            return {"error": str(e), "indicator": indicator}

    return {"error": "Max retries exceeded", "indicator": indicator}


def _parse_observations(body: dict) -> list[dict]:
    """Parse DATA_OBJ[].VALUE (@time -> date, $ -> value) from API response."""
    try:
        data_objs = (
            body
            .get("GET_STATS", {})
            .get("STATISTICAL_DATA", {})
            .get("DATA_INF", {})
            .get("DATA_OBJ", [])
        )
    except (AttributeError, TypeError):
        return []

    observations: list[dict] = []
    for obj in data_objs:
        value_block = obj.get("VALUE", {})
        if not isinstance(value_block, dict):
            continue

        raw_time = value_block.get("@time", "")
        raw_value = value_block.get("$", "")

        if not raw_time or raw_value in ("", None):
            continue

        date = normalize_time(raw_time)
        try:
            observations.append({
                "date": date,
                "value": float(raw_value),
            })
        except (ValueError, TypeError):
            continue

    # Sort chronologically (oldest first)
    observations.sort(key=lambda o: o["date"])
    return observations


# ---------------------------------------------------------------------------
# Search mode
# ---------------------------------------------------------------------------

def _fetch_all_indicators() -> dict:
    """Fetch the full indicator catalog from getIndicatorInfo (no search param).

    The e-Stat Dashboard API does not support server-side keyword search.
    We fetch the full catalog, cache it, and filter client-side.
    """
    cache_path = CACHE_DIR / "_indicator_catalog.json"
    cached = load_cache(cache_path)
    if cached is not None:
        return cached

    params: dict = {"Lang": "EN"}
    headers = {
        "User-Agent": "investing-toolkit/1.3.0",
        "Accept-Encoding": "gzip",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = _requests.get(
                ESTAT_SEARCH_BASE, params=params, timeout=60, headers=headers,
            )

            if resp.status_code == 429 and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue

            if resp.status_code != 200:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                return {"error": f"e-Stat catalog HTTP {resp.status_code}"}

            body = resp.json()
            # Parse into lightweight list and cache
            catalog = _parse_indicator_catalog(body)
            catalog_data = {"indicators": catalog}
            save_cache(cache_path, catalog_data)
            return catalog_data

        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": "e-Stat catalog request timed out"}
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": f"e-Stat catalog connection error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    return {"error": "Max retries exceeded"}


def _parse_indicator_catalog(body: dict) -> list[dict]:
    """Parse getIndicatorInfo response into a list of {code, name} dicts."""
    try:
        class_objs = (
            body
            .get("GET_META_INDICATOR_INF", {})
            .get("METADATA_INF", {})
            .get("CLASS_INF", {})
            .get("CLASS_OBJ", [])
        )
    except (AttributeError, TypeError):
        return []

    # Normalize: API may return a single dict instead of a list
    if isinstance(class_objs, dict):
        class_objs = [class_objs]

    results: list[dict] = []
    for obj in class_objs:
        code = obj.get("@code", "")
        name = obj.get("@name", "")
        if code:
            results.append({"code": code, "name": name})

    return results


# ---------------------------------------------------------------------------
# Unified fetch: cache + fetch + parse
# ---------------------------------------------------------------------------

def _resolve_preset(key: str) -> str | None:
    """Resolve a preset alias to an indicator code, or return None."""
    return PRESETS.get(key.lower().strip())


def _indicator_name(code: str, preset: str | None) -> str:
    """Look up a human-readable name for an indicator code."""
    return INDICATOR_NAMES.get(code, preset or code)


def fetch_indicator(indicator: str, cycle: str, use_cache: bool = True, preset: str | None = None) -> dict:
    """Fetch a single indicator with caching."""
    cache_path = get_cache_path(indicator, cycle)

    if use_cache:
        cached = load_cache(cache_path)
        if cached is not None:
            cached["_cache"] = "hit"
            return cached

    body = _fetch_data(indicator, cycle)
    if "error" in body:
        return body

    observations = _parse_observations(body)

    name = _indicator_name(indicator, preset)
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    latest = observations[-1] if observations else None

    result: dict = {
        "indicator": indicator,
    }
    if preset:
        result["preset"] = preset
    result.update({
        "name": name,
        "fetched_at": now,
        "_cache": "miss",
        "_source": "estat_dashboard",
        "observations": observations,
        "latest": latest,
        "count": len(observations),
    })

    if "error" not in result:
        save_cache(cache_path, result)

    return result


def search_indicators(query: str) -> dict:
    """Search for indicators by keyword (client-side filter on full catalog)."""
    catalog_data = _fetch_all_indicators()
    if "error" in catalog_data:
        return catalog_data

    all_indicators = catalog_data.get("indicators", [])
    query_lower = query.lower()
    keywords = query_lower.split()

    # Match indicators where ALL keywords appear in the name
    results = [
        ind for ind in all_indicators
        if all(kw in ind.get("name", "").lower() for kw in keywords)
    ]

    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "query": query,
        "fetched_at": now,
        "_source": "estat_dashboard",
        "results": results,
        "count": len(results),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="e-Stat Dashboard (統計ダッシュボード) adapter for investing-toolkit",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--indicator",
        help="Indicator code(s), comma-separated (e.g. 0703010501010030000)",
    )
    group.add_argument(
        "--preset",
        help="Preset alias(es), comma-separated (e.g. cpi,unemployment,jgb10y)",
    )
    group.add_argument(
        "--search",
        help="Search for indicators by keyword (no data fetch)",
    )

    parser.add_argument(
        "--cycle", default="monthly",
        choices=["monthly", "quarterly", "yearly"],
        help="Data frequency (default: monthly)",
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Bypass cache and force fresh fetch",
    )

    args = parser.parse_args()

    # --search mode: search and exit
    if args.search:
        result = search_indicators(args.search)
        print(json.dumps(result, default=str, indent=2, ensure_ascii=False))
        if "error" in result:
            sys.exit(1)
        return

    cycle = CYCLE_MAP[args.cycle]

    # Resolve indicators from --preset or --indicator
    # Each entry: (indicator_code, preset_alias_or_None)
    targets: list[tuple[str, str | None]] = []

    if args.preset:
        for alias in args.preset.split(","):
            alias = alias.strip()
            if not alias:
                continue
            code = _resolve_preset(alias)
            if code is None:
                print(
                    json.dumps(
                        {"error": f"Unknown preset: {alias}", "available_presets": list(PRESETS.keys())},
                        indent=2,
                    )
                )
                sys.exit(1)
            targets.append((code, alias))
    else:
        for code in args.indicator.split(","):
            code = code.strip()
            if not code:
                continue
            # Reverse-lookup preset alias
            alias = next((k for k, v in PRESETS.items() if v == code), None)
            targets.append((code, alias))

    if not targets:
        print(json.dumps({"error": "No indicators specified"}, indent=2))
        sys.exit(1)

    # Clear cache if requested
    if args.no_cache:
        for indicator, _ in targets:
            cache_path = get_cache_path(indicator, cycle)
            if cache_path.exists():
                cache_path.unlink()

    # Fetch
    if len(targets) == 1:
        indicator, preset = targets[0]
        result = fetch_indicator(indicator, cycle, use_cache=not args.no_cache, preset=preset)
    else:
        result = {
            "fetched_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "_source": "estat_dashboard",
            "indicators": {},
        }
        for indicator, preset in targets:
            key = preset if preset else indicator
            data = fetch_indicator(indicator, cycle, use_cache=not args.no_cache, preset=preset)
            result["indicators"][key] = data

    print(json.dumps(result, default=str, indent=2, ensure_ascii=False))

    # Determine exit code
    if len(targets) == 1:
        has_error = "error" in result
    else:
        has_error = any(
            "error" in v
            for v in result.get("indicators", {}).values()
            if isinstance(v, dict)
        )

    if has_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
