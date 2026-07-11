#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1", "xlrd==2.0.2"]
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
Cache: $INVESTING_TOOLKIT_CACHE/dgbas/{filename}.json  (envelope schema v2.0)
       TTL is cadence-aware adaptive — see investing-toolkit/docs/cache-policy.md
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
Source: https://ws.dgbas.gov.tw/001/Upload/463/relfile/10315/2649/
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from io import BytesIO

import urllib3
import requests as _requests
import xlrd

import cache_util

# Suppress InsecureRequestWarning — DGBAS server has a known SSL certificate
# issue (unable to get local issuer certificate). verify=False is required.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DGBAS_PRICE_BASE = "https://ws.dgbas.gov.tw/001/Upload/463/relfile/10315/2649"
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0

# ---------------------------------------------------------------------------
# Preset aliases: preset -> (filename, sheet_name, description)
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict] = {
    "cpi": {
        # cpispl.xls has two sheets: "CPI" = INDEX values (民國110=100,
        # base 2021=100), "年增率" = year-on-year %. The `cpi` preset
        # surfaces the INDEX series; for true YoY use the `cpi-yoy`
        # preset (same .xls, sheet="年增率"). Pre-v2.1.x-c this preset
        # was mislabelled "YoY%" while emitting INDEX numbers — fixed
        # 2026-05-02 (ROADMAP §v2.1.x-c).
        "url": f"{DGBAS_PRICE_BASE}/cpispl.xls",
        "sheet": "CPI",
        "name": "Consumer Price Index INDEX (消費者物價指數, 民國110=100)",
        "cadence": "monthly",
    },
    "cpi-yoy": {
        # True YoY% from the 年增率 sheet of cpispl.xls. Downstream
        # consumer: classify_tw resolves CPI_YOY_KEYS = ["cpi-yoy",
        # "inflation.cpi-yoy", "dgbas.cpi-yoy"] for cpi_context.latest_yoy.
        "url": f"{DGBAS_PRICE_BASE}/cpispl.xls",
        "sheet": "年增率",
        "name": "Consumer Price Index YoY% (消費者物價指數年增率, 年增率 sheet)",
        "cadence": "monthly",
    },
    # core-cpi / ppi / import-pi / export-pi each have an INDEX sheet
    # and a 年增率 sheet, mirroring cpispl.xls. Pre-v2.1.1 the legacy
    # presets used ASCII sheet hints ("CPI"/"PPI"/"IPI"/"EPI") that
    # never matched the actual Chinese sheet names — _parse_xls fell
    # back to the first sheet (INDEX) and the YoY% label was a lie.
    # Ported per ROADMAP cleanup follow-up (2026-05-02).
    "core-cpi": {
        "url": f"{DGBAS_PRICE_BASE}/cpisplexvfe.xls",
        "sheet": "不含蔬果",
        "name": "Core CPI INDEX (核心CPI 不含蔬果及能源, 民國110=100)",
        "cadence": "monthly",
    },
    "core-cpi-yoy": {
        "url": f"{DGBAS_PRICE_BASE}/cpisplexvfe.xls",
        "sheet": "年增率",
        "name": "Core CPI YoY% (核心CPI 不含蔬果及能源年增率)",
        "cadence": "monthly",
    },
    "cpi-sa": {
        # cpisplsa.xls — seasonally adjusted CPI series. Single-sheet
        # file labelled "CPI"; emits the seasonally-adjusted index
        # (no YoY companion published).
        "url": f"{DGBAS_PRICE_BASE}/cpisplsa.xls",
        "sheet": "CPI",
        "name": "CPI Seasonally Adjusted (季調CPI 指數)",
        "cadence": "monthly",
    },
    "ppi": {
        "url": f"{DGBAS_PRICE_BASE}/ppispl.xls",
        "sheet": "生產者物價指數",
        "name": "Producer Price Index INDEX (生產者物價指數, 民國105=100)",
        "cadence": "monthly",
    },
    "ppi-yoy": {
        "url": f"{DGBAS_PRICE_BASE}/ppispl.xls",
        "sheet": "年增率",
        "name": "Producer Price Index YoY% (生產者物價指數年增率)",
        "cadence": "monthly",
    },
    # import-pi / export-pi .xls files publish multiple price bases
    # (新臺幣計價 vs 美元計價, plus 進口物價 also has 農工原料 sub-bundle).
    # The presets surface the headline 新臺幣計價 series; future work
    # may add `*-usd` / `*-raw-materials` variants if a downstream
    # consumer needs them.
    "import-pi": {
        "url": f"{DGBAS_PRICE_BASE}/ipispl.xls",
        "sheet": "總指數(新臺幣計價)",
        "name": "Import Price Index INDEX, TWD-priced (進口物價總指數, 新臺幣計價)",
        "cadence": "monthly",
    },
    "import-pi-yoy": {
        "url": f"{DGBAS_PRICE_BASE}/ipispl.xls",
        "sheet": "年增率(新臺幣計價)",
        "name": "Import Price Index YoY%, TWD-priced (進口物價年增率, 新臺幣計價)",
        "cadence": "monthly",
    },
    "export-pi": {
        "url": f"{DGBAS_PRICE_BASE}/epispl.xls",
        "sheet": "指數(新臺幣計價)",
        "name": "Export Price Index INDEX, TWD-priced (出口物價總指數, 新臺幣計價)",
        "cadence": "monthly",
    },
    "export-pi-yoy": {
        "url": f"{DGBAS_PRICE_BASE}/epispl.xls",
        "sheet": "年增率(新臺幣計價)",
        "name": "Export Price Index YoY%, TWD-priced (出口物價年增率, 新臺幣計價)",
        "cadence": "monthly",
    },
    # v2.1.x-e — cpi-sa-yoy: DGBAS publishes only the seasonally-adjusted
    # INDEX in cpisplsa.xls (single sheet). YoY% companion is computed
    # in code via _compute_yoy_from_index. _provenance.computed=true
    # flags the derivation. Removes Lunar New Year base-effect noise
    # vs the headline `cpi-yoy` preset (which uses the published 年增率
    # sheet of cpispl.xls).
    "cpi-sa-yoy": {
        "url": f"{DGBAS_PRICE_BASE}/cpisplsa.xls",
        "sheet": "CPI",
        "name": "CPI Seasonally Adjusted YoY% (季調CPI 年增率, computed from INDEX)",
        "compute": "yoy_from_index",
        "cadence": "monthly",
    },
    # v2.1.x-f — USD-priced + 農工原料 sub-bundles for import-pi /
    # export-pi. The .xls files publish multiple price-base / commodity-
    # subset sheets; PR #209 only surfaced the 新臺幣計價 headlines.
    # These additions complete the matrix for trade-flow analyses
    # (terms-of-trade, raw-materials cost-push).
    "import-pi-usd": {
        "url": f"{DGBAS_PRICE_BASE}/ipispl.xls",
        "sheet": "總指數(美元計價)",
        "name": "Import Price Index INDEX, USD-priced (進口物價總指數, 美元計價)",
        "cadence": "monthly",
    },
    "import-pi-usd-yoy": {
        "url": f"{DGBAS_PRICE_BASE}/ipispl.xls",
        "sheet": "年增率(美元計價)",
        "name": "Import Price Index YoY%, USD-priced (進口物價年增率, 美元計價)",
        "cadence": "monthly",
    },
    "import-pi-raw": {
        "url": f"{DGBAS_PRICE_BASE}/ipispl.xls",
        "sheet": "農工原料指數(新臺幣計價)",
        "name": "Import Price Index INDEX, raw materials TWD (進口物價農工原料指數, 新臺幣計價)",
        "cadence": "monthly",
    },
    "import-pi-raw-yoy": {
        "url": f"{DGBAS_PRICE_BASE}/ipispl.xls",
        "sheet": "農工原料年增率(新臺幣計價)",
        "name": "Import Price Index YoY%, raw materials TWD (進口物價農工原料年增率, 新臺幣計價)",
        "cadence": "monthly",
    },
    "import-pi-raw-usd": {
        "url": f"{DGBAS_PRICE_BASE}/ipispl.xls",
        "sheet": "農工原料指數(美元計價)",
        "name": "Import Price Index INDEX, raw materials USD (進口物價農工原料指數, 美元計價)",
        "cadence": "monthly",
    },
    "import-pi-raw-usd-yoy": {
        "url": f"{DGBAS_PRICE_BASE}/ipispl.xls",
        "sheet": "農工原料年增率(美元計價)",
        "name": "Import Price Index YoY%, raw materials USD (進口物價農工原料年增率, 美元計價)",
        "cadence": "monthly",
    },
    "export-pi-usd": {
        "url": f"{DGBAS_PRICE_BASE}/epispl.xls",
        "sheet": "指數(美元計價)",
        "name": "Export Price Index INDEX, USD-priced (出口物價總指數, 美元計價)",
        "cadence": "monthly",
    },
    "export-pi-usd-yoy": {
        "url": f"{DGBAS_PRICE_BASE}/epispl.xls",
        "sheet": "年增率(美元計價)",
        "name": "Export Price Index YoY%, USD-priced (出口物價年增率, 美元計價)",
        "cadence": "monthly",
    },
}


# ---------------------------------------------------------------------------
# Computed-series helpers (v2.1.x-e)
# ---------------------------------------------------------------------------

def _compute_yoy_from_index(observations: list[dict], period: int = 12) -> list[dict]:
    """Compute YoY% from monthly INDEX observations.

    Used when DGBAS publishes only an INDEX series and no companion 年增率
    sheet (current case: cpisplsa.xls — seasonally-adjusted CPI). Returns
    YoY observations in the same `[{date, value}, ...]` shape, where
    value[t] = (index[t] / index[t-period] - 1) * 100. Drops the first
    `period` entries (no t-period reference).

    Defensive: validates that paired observations are exactly `period`
    months apart (handles potential DGBAS publishing gaps); skips any
    pair that fails the date arithmetic. Avoids divide-by-zero by
    skipping entries where index[t-period] is 0.

    Returns rounded to 2 decimal places (matches DGBAS-published 年增率
    sheet precision elsewhere in this module).
    """
    if not observations or len(observations) <= period:
        return []
    out: list[dict] = []
    for i in range(period, len(observations)):
        cur = observations[i]
        prior = observations[i - period]
        try:
            cy, cm = divmod(int(cur["date"]), 100)
            py, pm = divmod(int(prior["date"]), 100)
        except (KeyError, ValueError, TypeError):
            continue
        if (cy * 12 + cm) - (py * 12 + pm) != period:
            continue  # gap or out-of-order; skip rather than emit garbage
        if not prior["value"]:
            continue  # avoid div-zero on missing/zero base
        yoy = (cur["value"] / prior["value"] - 1.0) * 100.0
        out.append({"date": cur["date"], "value": round(yoy, 2)})
    return out


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "dgbas-tw"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


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
    """Fetch a DGBAS preset with cadence-aware adaptive caching.

    Cache TTL is computed via cache_util.compute_ttl() from the preset's
    `cadence` field. See cache-policy.md §"TTL bands".
    """
    _log("preset fetch", preset)
    t0 = time.monotonic()
    config = PRESETS.get(preset)
    if not config:
        return {"error": f"Unknown preset: {preset}", "available_presets": list(PRESETS.keys())}

    cadence = config.get("cadence", "monthly")
    cache_path = cache_util.cache_path("dgbas", preset)

    if use_cache:
        # LOOM-SIMPLIFY: staleness_days=None (cache-policy.md "overdue"
        # band = shortest/most-conservative TTL) is used for the
        # freshness *check* because cache_util.load_cache(path, ttl)
        # takes a precomputed ttl. Pre-migration, dgbas's own
        # `_compute_ttl` read a frozen `staleness_days_at_fetch` back out
        # of its own envelope meta at load time; cache_util's schema
        # (v2.0, `_cache_meta`) carries no such field, so there is no
        # stored staleness to recompute the adaptive TTL from before the
        # cache is even read. Net effect: dgbas may treat a cache entry
        # as stale slightly earlier than pre-migration — conservative
        # direction, never serves staler data than before. | ceiling: a
        # caller needs the pre-migration frozen-staleness-at-fetch
        # precision back | upgrade: extend cache_util's envelope schema
        # with an optional caller-supplied meta field, or have dgbas peek
        # the raw envelope before deciding ttl | ref: docs/loom/plans/
        # 2026-07-11-investing-toolkit-data-consolidation.md Task 3c
        ttl = cache_util.compute_ttl(cadence, None)
        cached = cache_util.load_cache(cache_path, ttl)
        if cached is not None:
            _log("preset done", f"{preset} cache hit")
            return cached  # already has _cache="hit" + _provenance + _cache_age_seconds

    content = _download_xls(config["url"])
    if isinstance(content, dict):
        _log("preset done", f"{preset} download error in {time.monotonic() - t0:.1f}s")
        return content  # error dict

    observations = _parse_xls(content, config.get("sheet", ""))

    # v2.1.x-e — apply compute step if preset declares one. Currently
    # only `yoy_from_index` is supported (used by `cpi-sa-yoy` to derive
    # YoY from the seasonally-adjusted INDEX since DGBAS publishes no
    # companion 年增率 sheet for cpisplsa.xls).
    compute = config.get("compute")
    if compute == "yoy_from_index":
        observations = _compute_yoy_from_index(observations)

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
    if compute:
        # Tag derived series so downstream consumers can distinguish
        # DGBAS-published values from in-code derivations.
        result["_provenance"]["computed"] = True
        result["_provenance"]["computation"] = (
            f"{compute} (period=12; (idx[t]/idx[t-12] - 1) * 100, "
            f"drops first 12 obs)"
        )

    if "error" not in result and observations:
        cache_util.save_cache(cache_path, result)

    _log("preset done", f"{preset} {len(observations)} obs in {time.monotonic() - t0:.1f}s")
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
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress logging on stderr (default: verbose)")

    args = parser.parse_args()
    global _QUIET
    _QUIET = args.quiet

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
            cache_path = cache_util.cache_path("dgbas", preset)
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
        _log("batch start", f"{len(presets)} presets")
        t_batch = time.monotonic()
        for i, preset in enumerate(presets, 1):
            _log(f"batch [{i}/{len(presets)}]", preset)
            data = fetch_preset(preset, use_cache=not args.no_cache)
            result["indicators"][preset] = data
        _log("batch done", f"{len(presets)} presets in {time.monotonic() - t_batch:.1f}s")

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
