#!/usr/bin/env python3
"""
fred_client.py — investing-toolkit FRED macro data adapter
Fetches Federal Reserve Economic Data series.

Usage:
  python3 fred_client.py --series T10Y2Y --periods 24
  python3 fred_client.py --series DGS10,DGS2,CPIAUCSL --periods 12
  python3 fred_client.py --series GDPC1 --periods 8

Auth: Set FRED_API_KEY env var (optional; without key: ~100 requests/day before 429).
      Free API key: https://fred.stlouisfed.org/docs/api/api_key.html
Cache: ~/.cache/investing-toolkit/fred/{series}_{periods}.json  TTL: 24h
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
CACHE_DIR = Path.home() / ".cache" / "investing-toolkit" / "fred"
CACHE_TTL_SECONDS = 86400  # 24 hours

def get_cache_path(series: str, periods: int) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{series.upper()}_{periods}.json"

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
        pass

def fetch_series(series: str, periods: int, api_key: str | None) -> dict:
    """Fetch a single FRED series, returning last `periods` observations."""
    cache_path = get_cache_path(series, periods)
    cached = load_cache(cache_path)
    if cached:
        cached["_cache"] = "hit"
        return cached

    params = {
        "series_id": series.upper(),
        "sort_order": "desc",
        "limit": str(periods),
        "file_type": "json",
    }
    if api_key:
        params["api_key"] = api_key
    else:
        params["api_key"] = "anonymous"  # FRED accepts this for low-volume use

    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{FRED_BASE}?{query}"

    for attempt in range(3):
        try:
            req = Request(url, headers={"User-Agent": "investing-toolkit/1.0.0"})
            with urlopen(req, timeout=15) as resp:
                raw = json.loads(resp.read())
            break
        except HTTPError as e:
            if e.code == 429:
                if attempt < 2:
                    time.sleep(2 ** attempt * 5)
                    continue
                return {
                    "error": "FRED rate limit (429). Set FRED_API_KEY env var for higher limits.",
                    "series": series,
                }
            return {"error": f"FRED HTTP {e.code}: {e.reason}", "series": series}
        except URLError as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return {"error": f"FRED network error: {e.reason}", "series": series}
        except Exception as e:
            return {"error": str(e), "series": series}

    observations = raw.get("observations", [])
    # Filter out missing values (FRED uses "." for missing)
    valid = [o for o in observations if o.get("value") not in (".", None, "")]

    result = {
        "series": series.upper(),
        "periods_requested": periods,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "_cache": "miss",
        "_warning": (
            f"FRED series {series} has publication lag — latest value may be "
            "1-4 weeks behind real-world data depending on release schedule."
        ),
        "observations": [
            {"date": o["date"], "value": float(o["value"])}
            for o in valid
        ],
        "latest": {"date": valid[0]["date"], "value": float(valid[0]["value"])} if valid else None,
        "count": len(valid),
    }
    save_cache(cache_path, result)
    return result

def main():
    parser = argparse.ArgumentParser(description="FRED macro data adapter for investing-toolkit")
    parser.add_argument("--series", required=True,
                        help="FRED series ID(s), comma-separated (e.g. T10Y2Y,DGS10,CPIAUCSL)")
    parser.add_argument("--periods", type=int, default=24,
                        help="Number of most-recent observations to return (default: 24)")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache")

    args = parser.parse_args()
    api_key = os.environ.get("FRED_API_KEY")

    series_list = [s.strip().upper() for s in args.series.split(",") if s.strip()]

    if args.no_cache:
        for s in series_list:
            path = get_cache_path(s, args.periods)
            if path.exists():
                path.unlink()

    if len(series_list) == 1:
        result = fetch_series(series_list[0], args.periods, api_key)
    else:
        result = {
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "series": {},
        }
        for s in series_list:
            data = fetch_series(s, args.periods, api_key)
            result["series"][s] = data

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
