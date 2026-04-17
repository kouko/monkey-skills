#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.32.3", "beautifulsoup4==4.13.4"]
# ///
"""
statgov_client.py — investing-toolkit stat.gov.tw chart data adapter
Extracts economic indicator data from the hidden Highcharts JSON field
on stat.gov.tw indicator pages.

Usage:
  uv run statgov_client.py --preset export-orders           # 外銷訂單 (百萬USD)
  uv run statgov_client.py --preset exports,imports          # 出口+進口金額
  uv run statgov_client.py --preset all                      # All presets
  uv run statgov_client.py --preset export-orders --no-cache

Auth: None required. Pure GET request, no Cloudflare.
Cache: $INVESTING_TOOLKIT_CACHE/statgov/{preset}.json  TTL: 24h
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
Source: https://www.stat.gov.tw/Point.aspx?sid=t.{N}
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import urllib3
import requests as _requests
from bs4 import BeautifulSoup

# Suppress InsecureRequestWarning for government sites with SSL issues
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

STATGOV_BASE = "https://www.stat.gov.tw/Point.aspx"
_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(Path.home() / ".cache" / "investing-toolkit")
CACHE_DIR = Path(_CACHE_BASE) / "statgov"
CACHE_TTL_SECONDS = 86400  # 24 hours
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0

# ---------------------------------------------------------------------------
# Preset definitions: preset -> (sid, chart_title_match)
#
# Each page (sid) contains multiple charts. We match by Title substring.
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict] = {
    # --- Trade (t.5 / t.7 / t.8) ---
    "export-orders": {
        "sid": "t.5", "n": "3584",
        "match": "外銷訂單",
        "name": "Export Orders (外銷訂單 百萬USD)",
    },
    "exports": {
        "sid": "t.8", "n": "3587",
        "match": "出口金額",
        "name": "Exports (出口金額 億USD)",
    },
    "imports": {
        "sid": "t.8", "n": "3587",
        "match": "進口金額",
        "name": "Imports (進口金額 億USD)",
    },
    "exports-yoy": {
        "sid": "t.8", "n": "3587",
        "match": "出口年增率",
        "name": "Exports YoY% (出口年增率)",
    },
    "imports-yoy": {
        "sid": "t.8", "n": "3587",
        "match": "進口年增率",
        "name": "Imports YoY% (進口年增率)",
    },
    # --- Production (t.5) ---
    "ipi": {
        "sid": "t.5", "n": "3584",
        "match": "工業生產指數年增率",
        "name": "Industrial Production YoY% (工業生產指數年增率)",
    },
    "manufacturing-yoy": {
        "sid": "t.5", "n": "3584",
        "match": "製造業生產指數年增率",
        "name": "Manufacturing Production YoY% (製造業生產指數年增率)",
    },
    "retail-yoy": {
        "sid": "t.5", "n": "3584",
        "match": "零售業營業額年增率",
        "name": "Retail Sales YoY% (零售業營業額年增率)",
    },
    # --- GDP (t.1) ---
    "gdp-yoy": {
        "sid": "t.1", "n": "3580",
        "match": "經濟成長率(yoy)",
        "name": "GDP Growth YoY% (經濟成長率 季)",
        "pick_first": True,  # first match = quarterly, second = annual
    },
    # --- Labor (t.3) ---
    "unemployment": {
        "sid": "t.3", "n": "3582",
        "match": "失業率",
        "match_exact": True,  # exact title match to avoid matching 季調
        "name": "Unemployment Rate % (失業率)",
    },
    "unemployment-sa": {
        "sid": "t.3", "n": "3582",
        "match": "失業率(經季節調整後)",
        "name": "Unemployment Rate SA % (季調失業率)",
    },
    # --- Finance (t.10) ---
    "fx-reserves": {
        "sid": "t.10", "n": "3589",
        "match": "外匯存底",
        "name": "FX Reserves (外匯存底 十億USD)",
    },
    "taiex": {
        "sid": "t.10", "n": "3589",
        "match": "集中市場發行量加權股價指數",
        "match_exact": True,
        "name": "TAIEX Monthly Average (加權股價指數)",
    },
    "m2-yoy": {
        "sid": "t.10", "n": "3589",
        "match": "M2)年增率",
        "name": "M2 YoY% (貨幣總計數M2年增率)",
    },
    # --- Business Cycle (t.11) ---
    "leading-index": {
        "sid": "t.11", "n": "3590",
        "match": "景氣領先指標",
        "name": "Leading Index ex-trend (景氣領先指標不含趨勢)",
    },
    "coincident-index": {
        "sid": "t.11", "n": "3590",
        "match": "景氣同時指標",
        "name": "Coincident Index ex-trend (景氣同時指標不含趨勢)",
    },
    "signal-score": {
        "sid": "t.11", "n": "3590",
        "match": "景氣對策信號",
        "name": "Business Cycle Signal Score (景氣對策信號)",
    },
}

# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def get_cache_path(preset: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{preset}.json"


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
# Provenance
# ---------------------------------------------------------------------------

def _compute_staleness(latest_date_str: str | None) -> int | None:
    if not latest_date_str:
        return None
    try:
        clean = latest_date_str.replace("-", "").replace("/", "")
        if len(clean) == 6:
            clean += "01"
        ref = datetime.strptime(clean[:8], "%Y%m%d").replace(tzinfo=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        return (now - ref).days
    except (ValueError, TypeError):
        return None


def _make_provenance(result: dict) -> dict:
    latest = result.get("latest")
    ref_period = latest["date"] if latest else None
    return {
        "source": "National Statistics R.O.C. (stat.gov.tw)",
        "source_authority": "Directorate-General of Budget, Accounting and Statistics (行政院主計總處)",
        "data_type": "official_government_statistics",
        "update_cycle": "monthly",
        "fetched_at": result.get("fetched_at"),
        "reference_period": ref_period,
        "staleness_days": _compute_staleness(ref_period),
    }


# ---------------------------------------------------------------------------
# Fetch + parse
# ---------------------------------------------------------------------------

# In-memory page cache to avoid re-downloading same sid page
_page_cache: dict[str, list] = {}


def _fetch_page_charts(sid: str, n: str) -> list[dict] | dict:
    """Fetch a stat.gov.tw page and extract chart data from hidden field."""
    cache_key = f"{sid}_{n}"
    if cache_key in _page_cache:
        return _page_cache[cache_key]

    params = {"sid": sid, "n": n, "sms": "11480"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = _requests.get(
                STATGOV_BASE, params=params, timeout=30, headers=headers,
                verify=False,
            )
            if resp.status_code == 429 and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            if resp.status_code != 200:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                return {"error": f"stat.gov.tw HTTP {resp.status_code}"}

            soup = BeautifulSoup(resp.text, "html.parser")
            hidden = soup.find("input", {"id": "ContentPlaceHolder1_hidChartData"})
            if not hidden or not hidden.get("value"):
                return {"error": "Hidden chart data field not found"}

            charts = json.loads(hidden["value"])
            _page_cache[cache_key] = charts
            return charts

        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": "stat.gov.tw request timed out"}
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": f"stat.gov.tw connection error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    return {"error": "Max retries exceeded"}


def _normalize_date(raw: str) -> str | None:
    """Normalize stat.gov.tw date format (YYYY/M/D) to YYYYMM."""
    if not raw:
        return None
    parts = raw.strip().split("/")
    if len(parts) >= 2:
        year = parts[0]
        month = parts[1].zfill(2)
        if year.isdigit() and month.isdigit():
            return f"{year}{month}"
    return None


def _extract_chart(charts: list[dict], match: str, pick_first: bool = False, match_exact: bool = False) -> list[dict]:
    """Find the matching chart and convert to observations."""
    found = None
    for chart in charts:
        title = chart.get("Title", "")
        if match_exact:
            if title == match:
                found = chart
                break
        elif match in title:
            found = chart
            if pick_first:
                break  # take first match

    if not found:
        return []

    observations: list[dict] = []
    for point in found.get("data", []):
        date = _normalize_date(point.get("Date", ""))
        raw_value = point.get("Value", "")
        if not date or not raw_value:
            continue

        # Remove commas from numbers
        clean_val = str(raw_value).replace(",", "").strip()
        if clean_val in ("-", "…", ""):
            continue

        try:
            value = float(clean_val)
        except ValueError:
            continue

        observations.append({"date": date, "value": value})

    # stat.gov.tw returns newest first — reverse to chronological
    observations.reverse()
    return observations


# ---------------------------------------------------------------------------
# Unified fetch
# ---------------------------------------------------------------------------

def fetch_preset(preset: str, use_cache: bool = True) -> dict:
    config = PRESETS.get(preset)
    if not config:
        return {"error": f"Unknown preset: {preset}", "available_presets": list(PRESETS.keys())}

    cache_path = get_cache_path(preset)
    if use_cache:
        cached = load_cache(cache_path)
        if cached is not None:
            cached["_cache"] = "hit"
            return cached

    charts = _fetch_page_charts(config["sid"], config["n"])
    if isinstance(charts, dict) and "error" in charts:
        return charts

    observations = _extract_chart(
        charts, config["match"],
        pick_first=config.get("pick_first", False),
        match_exact=config.get("match_exact", False),
    )

    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    latest = observations[-1] if observations else None
    prior = observations[-2] if len(observations) >= 2 else None

    direction = None
    if latest and prior:
        if latest["value"] > prior["value"]:
            direction = "Rising"
        elif latest["value"] < prior["value"]:
            direction = "Falling"
        else:
            direction = "Flat"

    result: dict = {
        "preset": preset,
        "name": config["name"],
        "fetched_at": now,
        "_cache": "miss",
        "_source": "statgov",
        "observations": observations,
        "latest": latest,
        "prior": prior,
        "direction": direction,
        "count": len(observations),
    }
    result["_provenance"] = _make_provenance(result)

    if "error" not in result and observations:
        save_cache(cache_path, result)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="stat.gov.tw chart data adapter for investing-toolkit",
    )
    parser.add_argument(
        "--preset", required=True,
        help="Preset(s), comma-separated, or 'all'",
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Bypass cache and force fresh fetch",
    )

    args = parser.parse_args()

    if args.preset.strip().lower() == "all":
        presets = list(PRESETS.keys())
    else:
        presets = [p.strip() for p in args.preset.split(",") if p.strip()]

    if not presets:
        print(json.dumps({"error": "No presets specified"}, indent=2))
        sys.exit(1)

    if args.no_cache:
        for preset in presets:
            cache_path = get_cache_path(preset)
            if cache_path.exists():
                cache_path.unlink()

    if len(presets) == 1:
        result = fetch_preset(presets[0], use_cache=not args.no_cache)
    else:
        result = {
            "fetched_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "_source": "statgov",
            "indicators": {},
        }
        for preset in presets:
            data = fetch_preset(preset, use_cache=not args.no_cache)
            result["indicators"][preset] = data

    print(json.dumps(result, default=str, indent=2, ensure_ascii=False))

    if len(presets) == 1:
        has_error = "error" in result
    else:
        has_error = any(
            "error" in v for v in result.get("indicators", {}).values()
            if isinstance(v, dict)
        )

    if has_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
