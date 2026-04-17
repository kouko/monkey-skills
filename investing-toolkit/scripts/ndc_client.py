#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.32.3"]
# ///
"""
ndc_client.py — investing-toolkit NDC (國發會) Business Cycle adapter
Downloads the NDC business cycle monitoring ZIP from ws.ndc.gov.tw,
extracts CSVs, and returns structured JSON for signal score, signal color,
and component indicators.

Usage:
  uv run ndc_client.py --preset signal               # 景氣燈號 score + color
  uv run ndc_client.py --preset signal-components     # 9 component indicators
  uv run ndc_client.py --preset leading               # Leading indicator index
  uv run ndc_client.py --preset all                   # Everything
  uv run ndc_client.py --preset signal --no-cache     # Force fresh fetch

Auth: None required.
Cache: ~/.cache/investing-toolkit/ndc/ndc_zip.json  TTL: 24h
Source: ws.ndc.gov.tw (bypasses Cloudflare on index.ndc.gov.tw)
"""

import argparse
import csv
import json
import sys
import time
import zipfile
from datetime import datetime, timezone
from io import BytesIO, StringIO
from pathlib import Path

import urllib3
import requests as _requests

# Suppress InsecureRequestWarning for government APIs with SSL issues
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# This URL serves the NDC business cycle ZIP file. It bypasses the Cloudflare
# protection on index.ndc.gov.tw.
NDC_ZIP_URL = (
    "https://ws.ndc.gov.tw/Download.ashx?"
    "u=LzAwMS9hZG1pbmlzdHJhdG9yLzEwL3JlbGZpbGUvNTc4MS82MzkyL2VhMjM1YmQ5LW"
    "QwNTItNGE2OS1hYmZjLWQ1Yzc4NWQzZDBlMi56aXA%3d"
    "&n=5pmv5rCj5oyH5qiZ5Y%2bK54eI6JmfLnppcA%3d%3d&icon=.zip"
)

CACHE_DIR = Path.home() / ".cache" / "investing-toolkit" / "ndc"
CACHE_TTL_SECONDS = 86400  # 24 hours
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0

# ---------------------------------------------------------------------------
# CSV file mapping inside the ZIP
# ---------------------------------------------------------------------------

# The ZIP contains CSVs with Big5-encoded filenames but UTF-8 content.
# We match files by content pattern rather than filename.
SIGNAL_FILE_PATTERN = "景氣指標與燈號"
COMPONENTS_FILE_PATTERN = "景氣對策信號構成項目"
LEADING_FILE_PATTERN = "領先指標構成項目"
COINCIDENT_FILE_PATTERN = "同時指標構成項目"
LAGGING_FILE_PATTERN = "落後指標構成項目"


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


def _make_provenance(result: dict) -> dict:
    latest = result.get("latest")
    ref_period = latest["date"] if latest else None
    return {
        "source": "NDC Business Cycle Indicators (ws.ndc.gov.tw)",
        "source_authority": "National Development Council (國家發展委員會)",
        "data_type": "official_government_statistics",
        "update_cycle": "monthly",
        "typical_lag": "~6 weeks after reference month",
        "fetched_at": result.get("fetched_at"),
        "reference_period": ref_period,
        "staleness_days": _compute_staleness(ref_period),
    }


# ---------------------------------------------------------------------------
# Download + extract ZIP
# ---------------------------------------------------------------------------

def _download_zip() -> bytes | dict:
    """Download the NDC business cycle ZIP file."""
    headers = {
        "User-Agent": "investing-toolkit/1.4.0",
        "Accept-Encoding": "gzip",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = _requests.get(
                NDC_ZIP_URL, timeout=30, headers=headers, verify=False,
            )

            if resp.status_code == 429 and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue

            if resp.status_code != 200:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                return {"error": f"NDC HTTP {resp.status_code}"}

            return resp.content

        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": "NDC request timed out"}
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": f"NDC connection error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    return {"error": "Max retries exceeded"}


def _extract_csvs(zip_bytes: bytes) -> dict[str, str]:
    """Extract CSV content from the ZIP, keyed by decoded filename pattern."""
    result: dict[str, str] = {}

    with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
        for info in zf.infolist():
            # Try to decode the filename (Big5 encoded as cp437)
            try:
                decoded_name = info.filename.encode("cp437").decode("big5")
            except (UnicodeDecodeError, UnicodeEncodeError):
                decoded_name = info.filename

            # Skip non-CSV files and schema files
            if not decoded_name.endswith(".csv"):
                continue
            if "schema" in decoded_name.lower():
                continue

            # Read content as UTF-8
            try:
                content = zf.read(info).decode("utf-8-sig")
            except UnicodeDecodeError:
                try:
                    content = zf.read(info).decode("big5")
                except UnicodeDecodeError:
                    continue

            # Map to known patterns
            for pattern in [SIGNAL_FILE_PATTERN, COMPONENTS_FILE_PATTERN,
                            LEADING_FILE_PATTERN, COINCIDENT_FILE_PATTERN,
                            LAGGING_FILE_PATTERN]:
                if pattern in decoded_name:
                    result[pattern] = content
                    break

    return result


# ---------------------------------------------------------------------------
# Parse CSV → observations
# ---------------------------------------------------------------------------

def _normalize_date(raw: str) -> str | None:
    """Normalize NDC date format (YYYY-MM) to YYYYMM."""
    raw = raw.strip()
    if not raw:
        return None
    clean = raw.replace("-", "").replace("/", "")
    if len(clean) == 6 and clean.isdigit():
        return clean
    # Try YYYY-MM format
    parts = raw.split("-")
    if len(parts) == 2:
        year, month = parts
        if year.isdigit() and month.isdigit():
            return f"{year}{month.zfill(2)}"
    return None


def _parse_signal_csv(content: str) -> dict:
    """Parse 景氣指標與燈號.csv into signal score + color observations."""
    reader = csv.DictReader(StringIO(content))

    score_obs: list[dict] = []
    color_obs: list[dict] = []

    for row in reader:
        date = _normalize_date(row.get("Date", row.get("年月", row.get("西元年月", ""))))
        if not date:
            continue

        # Signal score
        score_raw = row.get("景氣對策信號綜合分數", "").strip()
        if score_raw:
            try:
                score_obs.append({"date": date, "value": float(score_raw)})
            except ValueError:
                pass

        # Signal color
        color = row.get("景氣對策信號", "").strip()
        if color:
            color_obs.append({"date": date, "value": color})

    score_obs.sort(key=lambda o: o["date"])
    color_obs.sort(key=lambda o: o["date"])

    return {"score": score_obs, "color": color_obs}


def _parse_components_csv(content: str) -> dict[str, list[dict]]:
    """Parse 景氣對策信號構成項目.csv into per-component observations."""
    reader = csv.DictReader(StringIO(content))

    # Collect all columns that look like indicator data
    components: dict[str, list[dict]] = {}

    for row in reader:
        date = _normalize_date(row.get("Date", row.get("年月", row.get("西元年月", ""))))
        if not date:
            continue

        for key, val in row.items():
            if key in ("Date", "年月", "西元年月", ""):
                continue
            val = val.strip()
            if not val or val == "…" or val == "-":
                continue
            try:
                value = float(val)
            except ValueError:
                continue

            if key not in components:
                components[key] = []
            components[key].append({"date": date, "value": value})

    # Sort each component
    for obs_list in components.values():
        obs_list.sort(key=lambda o: o["date"])

    return components


def _parse_index_csv(content: str) -> dict[str, list[dict]]:
    """Parse leading/coincident/lagging index CSV into observations."""
    reader = csv.DictReader(StringIO(content))

    indices: dict[str, list[dict]] = {}

    for row in reader:
        date = _normalize_date(row.get("Date", row.get("年月", row.get("西元年月", ""))))
        if not date:
            continue

        for key, val in row.items():
            if key in ("Date", "年月", "西元年月", ""):
                continue
            val = val.strip()
            if not val or val == "…" or val == "-":
                continue
            try:
                value = float(val)
            except ValueError:
                continue

            if key not in indices:
                indices[key] = []
            indices[key].append({"date": date, "value": value})

    for obs_list in indices.values():
        obs_list.sort(key=lambda o: o["date"])

    return indices


# ---------------------------------------------------------------------------
# Unified fetch
# ---------------------------------------------------------------------------

def _build_result(name: str, preset: str, observations: list[dict]) -> dict:
    """Build a standard result dict from observations."""
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    latest = observations[-1] if observations else None
    prior = observations[-2] if len(observations) >= 2 else None

    direction = None
    if latest and prior:
        try:
            lv = float(latest["value"])
            pv = float(prior["value"])
            if lv > pv:
                direction = "Rising"
            elif lv < pv:
                direction = "Falling"
            else:
                direction = "Flat"
        except (ValueError, TypeError):
            pass

    result: dict = {
        "preset": preset,
        "name": name,
        "fetched_at": now,
        "_cache": "miss",
        "_source": "ndc",
        "observations": observations,
        "latest": latest,
        "prior": prior,
        "direction": direction,
        "count": len(observations),
    }
    result["_provenance"] = _make_provenance(result)
    return result


def fetch_preset(preset: str, use_cache: bool = True) -> dict:
    """Fetch an NDC preset with caching."""
    cache_path = get_cache_path(preset)

    if use_cache:
        cached = load_cache(cache_path)
        if cached is not None:
            cached["_cache"] = "hit"
            return cached

    # Download and extract ZIP
    zip_bytes = _download_zip()
    if isinstance(zip_bytes, dict):
        return zip_bytes  # error

    csvs = _extract_csvs(zip_bytes)
    if not csvs:
        return {"error": "No CSV files found in NDC ZIP"}

    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if preset == "signal":
        content = csvs.get(SIGNAL_FILE_PATTERN)
        if not content:
            return {"error": f"CSV '{SIGNAL_FILE_PATTERN}' not found in ZIP"}
        parsed = _parse_signal_csv(content)
        result = {
            "preset": preset,
            "name": "Business Cycle Signal (景氣對策信號)",
            "fetched_at": now,
            "_cache": "miss",
            "_source": "ndc",
            "score": _build_result("Signal Score (綜合分數)", "signal-score", parsed["score"]),
            "color": _build_result("Signal Color (燈號)", "signal-color", parsed["color"]),
        }
        result["_provenance"] = _make_provenance(result["score"])

    elif preset == "signal-components":
        content = csvs.get(COMPONENTS_FILE_PATTERN)
        if not content:
            return {"error": f"CSV '{COMPONENTS_FILE_PATTERN}' not found in ZIP"}
        components = _parse_components_csv(content)
        result = {
            "preset": preset,
            "name": "Signal Components (對策信號構成項目)",
            "fetched_at": now,
            "_cache": "miss",
            "_source": "ndc",
            "components": {},
        }
        for comp_name, obs in components.items():
            result["components"][comp_name] = _build_result(comp_name, preset, obs)
        # Use first component for provenance
        first = next(iter(result["components"].values()), {})
        result["_provenance"] = first.get("_provenance", {})

    elif preset == "leading":
        content = csvs.get(LEADING_FILE_PATTERN)
        if not content:
            return {"error": f"CSV '{LEADING_FILE_PATTERN}' not found in ZIP"}
        indices = _parse_index_csv(content)
        result = {
            "preset": preset,
            "name": "Leading Indicator Components (領先指標構成項目)",
            "fetched_at": now,
            "_cache": "miss",
            "_source": "ndc",
            "indices": {},
        }
        for idx_name, obs in indices.items():
            result["indices"][idx_name] = _build_result(idx_name, preset, obs)
        first = next(iter(result["indices"].values()), {})
        result["_provenance"] = first.get("_provenance", {})

    elif preset == "coincident":
        content = csvs.get(COINCIDENT_FILE_PATTERN)
        if not content:
            return {"error": f"CSV '{COINCIDENT_FILE_PATTERN}' not found in ZIP"}
        indices = _parse_index_csv(content)
        result = {
            "preset": preset,
            "name": "Coincident Indicator Components (同時指標構成項目)",
            "fetched_at": now,
            "_cache": "miss",
            "_source": "ndc",
            "indices": {},
        }
        for idx_name, obs in indices.items():
            result["indices"][idx_name] = _build_result(idx_name, preset, obs)
        first = next(iter(result["indices"].values()), {})
        result["_provenance"] = first.get("_provenance", {})

    elif preset == "lagging":
        content = csvs.get(LAGGING_FILE_PATTERN)
        if not content:
            return {"error": f"CSV '{LAGGING_FILE_PATTERN}' not found in ZIP"}
        indices = _parse_index_csv(content)
        result = {
            "preset": preset,
            "name": "Lagging Indicator Components (落後指標構成項目)",
            "fetched_at": now,
            "_cache": "miss",
            "_source": "ndc",
            "indices": {},
        }
        for idx_name, obs in indices.items():
            result["indices"][idx_name] = _build_result(idx_name, preset, obs)
        first = next(iter(result["indices"].values()), {})
        result["_provenance"] = first.get("_provenance", {})

    elif preset == "unemployment":
        content = csvs.get(LAGGING_FILE_PATTERN)
        if not content:
            return {"error": f"CSV '{LAGGING_FILE_PATTERN}' not found in ZIP"}
        indices = _parse_index_csv(content)
        # Extract the unemployment rate column
        unemp_obs: list[dict] = []
        for col_name, obs in indices.items():
            if "失業率" in col_name:
                unemp_obs = obs
                break
        result = _build_result("Unemployment Rate % (失業率)", preset, unemp_obs)

    else:
        return {"error": f"Unknown preset: {preset}",
                "available_presets": ["signal", "signal-components", "leading", "coincident", "lagging", "unemployment", "all"]}

    if "error" not in result:
        save_cache(cache_path, result)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="NDC (國發會) Business Cycle adapter for investing-toolkit",
    )
    parser.add_argument(
        "--preset", required=True,
        help="Preset: signal, signal-components, leading, coincident, or all",
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Bypass cache and force fresh fetch",
    )

    args = parser.parse_args()

    if args.preset.strip().lower() == "all":
        presets = ["signal", "signal-components", "leading", "coincident", "lagging", "unemployment"]
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
            "_source": "ndc",
            "presets": {},
        }
        for preset in presets:
            data = fetch_preset(preset, use_cache=not args.no_cache)
            result["presets"][preset] = data

    print(json.dumps(result, default=str, indent=2, ensure_ascii=False))

    # Exit code
    if len(presets) == 1:
        has_error = "error" in result
    else:
        has_error = any(
            "error" in v for v in result.get("presets", {}).values()
            if isinstance(v, dict)
        )

    if has_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
