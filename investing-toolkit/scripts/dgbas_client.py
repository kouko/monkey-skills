#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.32.3", "xlrd==2.0.1"]
# ///
"""
dgbas_client.py — investing-toolkit DGBAS (主計總處) Excel adapter
Downloads and parses .xls files from the Directorate-General of Budget,
Accounting and Statistics of Taiwan.

Usage:
  uv run dgbas_client.py --preset cpi                   # Consumer Price Index
  uv run dgbas_client.py --preset cpi,core-cpi,ppi      # Multiple presets
  uv run dgbas_client.py --preset all                    # All presets
  uv run dgbas_client.py --preset cpi --no-cache         # Force fresh fetch

Auth: None required.
Cache: $INVESTING_TOOLKIT_CACHE/dgbas/{filename}.json  TTL: 24h
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
Source: https://ws.dgbas.gov.tw/001/Upload/463/relfile/10315/2649/
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import urllib3
import requests as _requests
import xlrd

# Suppress InsecureRequestWarning — DGBAS server has a known SSL certificate
# issue (unable to get local issuer certificate). verify=False is required.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DGBAS_PRICE_BASE = "https://ws.dgbas.gov.tw/001/Upload/463/relfile/10315/2649"
_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(Path.home() / ".cache" / "investing-toolkit")
CACHE_DIR = Path(_CACHE_BASE) / "dgbas"
CACHE_TTL_SECONDS = 86400  # 24 hours
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0

# ---------------------------------------------------------------------------
# Preset aliases: preset -> (filename, sheet_name, description)
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict] = {
    "cpi": {
        "url": f"{DGBAS_PRICE_BASE}/cpispl.xls",
        "sheet": "CPI",
        "name": "Consumer Price Index YoY% (消費者物價指數年增率)",
    },
    "core-cpi": {
        "url": f"{DGBAS_PRICE_BASE}/cpisplexvfe.xls",
        "sheet": "CPI",
        "name": "Core CPI YoY% (核心CPI 不含蔬果及能源)",
    },
    "cpi-sa": {
        "url": f"{DGBAS_PRICE_BASE}/cpisplsa.xls",
        "sheet": "CPI",
        "name": "CPI Seasonally Adjusted (季調CPI)",
    },
    "ppi": {
        "url": f"{DGBAS_PRICE_BASE}/ppispl.xls",
        "sheet": "PPI",
        "name": "Producer Price Index YoY% (躉售物價指數年增率)",
    },
    "import-pi": {
        "url": f"{DGBAS_PRICE_BASE}/ipispl.xls",
        "sheet": "IPI",
        "name": "Import Price Index YoY% (進口物價指數年增率)",
    },
    "export-pi": {
        "url": f"{DGBAS_PRICE_BASE}/epispl.xls",
        "sheet": "EPI",
        "name": "Export Price Index YoY% (出口物價指數年增率)",
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
# Provenance helpers
# ---------------------------------------------------------------------------

def _compute_staleness(latest_date_str: str | None) -> int | None:
    if not latest_date_str:
        return None
    try:
        clean = latest_date_str.replace("-", "")
        if len(clean) == 6:
            clean += "01"
        ref = datetime.strptime(clean[:8], "%Y%m%d").replace(tzinfo=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        return (now - ref).days
    except (ValueError, TypeError):
        return None


def _make_provenance(result: dict, url: str) -> dict:
    latest = result.get("latest")
    ref_period = latest["date"] if latest else None
    return {
        "source": f"DGBAS Excel ({url})",
        "source_authority": "Directorate-General of Budget, Accounting and Statistics (行政院主計總處)",
        "data_type": "official_government_statistics",
        "update_cycle": "monthly",
        "typical_lag": "3-4 weeks after reference month",
        "fetched_at": result.get("fetched_at"),
        "reference_period": ref_period,
        "staleness_days": _compute_staleness(ref_period),
    }


# ---------------------------------------------------------------------------
# Download Excel
# ---------------------------------------------------------------------------

def _download_xls(url: str) -> bytes | dict:
    """Download an .xls file, returning raw bytes or error dict."""
    headers = {
        "User-Agent": "investing-toolkit/1.4.0",
        "Accept-Encoding": "gzip",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = _requests.get(url, timeout=30, headers=headers, verify=False)

            if resp.status_code == 429 and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue

            if resp.status_code != 200:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                return {"error": f"DGBAS HTTP {resp.status_code}", "url": url}

            return resp.content

        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": "DGBAS request timed out", "url": url}
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": f"DGBAS connection error: {e}", "url": url}
        except Exception as e:
            return {"error": str(e), "url": url}

    return {"error": "Max retries exceeded", "url": url}


# ---------------------------------------------------------------------------
# Parse Excel → observations
# ---------------------------------------------------------------------------

def _parse_xls(content: bytes, sheet_hint: str) -> list[dict]:
    """Parse a DGBAS .xls file into observations.

    DGBAS Excel structure (price indices):
    - Row 0-1: Title/header rows
    - Row 2: Column headers — first column is 民國年 (ROC year), then 1月~12月
    - Row 3+: Data rows — ROC year in first column, monthly values in columns 1-12

    ROC year conversion: 民國年 + 1911 = 西元年
    """
    try:
        wb = xlrd.open_workbook(file_contents=content)
    except Exception as e:
        return []

    # Find the target sheet
    sheet = None
    for name in wb.sheet_names():
        if sheet_hint.upper() in name.upper():
            sheet = wb.sheet_by_name(name)
            break
    if sheet is None:
        # Fallback: use first sheet
        sheet = wb.sheet_by_index(0)

    observations: list[dict] = []

    # Find the header row (contains month labels)
    header_row_idx = _find_header_row(sheet)
    if header_row_idx is None:
        return observations

    # Parse data rows starting after header
    for row_idx in range(header_row_idx + 1, sheet.nrows):
        row = sheet.row(row_idx)
        if len(row) < 2:
            continue

        # First column: ROC year (民國年)
        roc_year_raw = row[0].value
        try:
            roc_year = int(float(roc_year_raw))
        except (ValueError, TypeError):
            continue

        # Skip invalid years
        if roc_year < 1 or roc_year > 200:
            continue

        ad_year = roc_year + 1911

        # Columns 1-12 correspond to months 1-12
        for month_idx in range(1, min(13, len(row))):
            cell = row[month_idx]
            if cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                continue
            if cell.value == "" or cell.value is None:
                continue

            try:
                value = float(cell.value)
            except (ValueError, TypeError):
                continue

            date = f"{ad_year}{month_idx:02d}"
            observations.append({"date": date, "value": value})

    observations.sort(key=lambda o: o["date"])
    return observations


def _find_header_row(sheet: xlrd.sheet.Sheet) -> int | None:
    """Find the row that contains month column headers (1月 or January or 1)."""
    for row_idx in range(min(10, sheet.nrows)):
        row = sheet.row(row_idx)
        if len(row) < 3:
            continue

        # Check if columns 1-3 look like month headers
        values = [str(cell.value).strip() for cell in row[1:4]]
        # Look for patterns like "1月", "1", "Jan", "January"
        if any(v in ("1月", "1", "1.0", "Jan", "January") for v in values):
            return row_idx
        # Also check for "一月"
        if any("一" in v for v in values):
            return row_idx

    # Fallback: row 2 (common in DGBAS files)
    return 2


# ---------------------------------------------------------------------------
# Unified fetch: cache + download + parse
# ---------------------------------------------------------------------------

def fetch_preset(preset: str, use_cache: bool = True) -> dict:
    """Fetch a DGBAS preset with caching."""
    config = PRESETS.get(preset)
    if not config:
        return {"error": f"Unknown preset: {preset}", "available_presets": list(PRESETS.keys())}

    cache_path = get_cache_path(preset)

    if use_cache:
        cached = load_cache(cache_path)
        if cached is not None:
            cached["_cache"] = "hit"
            if "_provenance" not in cached:
                cached["_provenance"] = _make_provenance(cached, config["url"])
            return cached

    content = _download_xls(config["url"])
    if isinstance(content, dict):
        return content  # error dict

    observations = _parse_xls(content, config.get("sheet", ""))

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
        "_source": "dgbas",
        "observations": observations,
        "latest": latest,
        "prior": prior,
        "direction": direction,
        "count": len(observations),
    }
    result["_provenance"] = _make_provenance(result, config["url"])

    if "error" not in result and observations:
        save_cache(cache_path, result)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="DGBAS (主計總處) Excel adapter for investing-toolkit",
    )
    parser.add_argument(
        "--preset", required=True,
        help="Preset alias(es), comma-separated (e.g. cpi,core-cpi,ppi) or 'all'",
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Bypass cache and force fresh fetch",
    )

    args = parser.parse_args()

    # Resolve presets
    if args.preset.strip().lower() == "all":
        presets = list(PRESETS.keys())
    else:
        presets = [p.strip() for p in args.preset.split(",") if p.strip()]

    if not presets:
        print(json.dumps({"error": "No presets specified"}, indent=2))
        sys.exit(1)

    # Clear cache if requested
    if args.no_cache:
        for preset in presets:
            cache_path = get_cache_path(preset)
            if cache_path.exists():
                cache_path.unlink()

    # Fetch
    if len(presets) == 1:
        result = fetch_preset(presets[0], use_cache=not args.no_cache)
    else:
        result = {
            "fetched_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "_source": "dgbas",
            "indicators": {},
        }
        for preset in presets:
            data = fetch_preset(preset, use_cache=not args.no_cache)
            result["indicators"][preset] = data

    print(json.dumps(result, default=str, indent=2, ensure_ascii=False))

    # Determine exit code
    if len(presets) == 1:
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
