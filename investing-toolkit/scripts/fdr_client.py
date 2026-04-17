#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["finance-datareader==0.9.90", "requests==2.32.3", "beautifulsoup4==4.13.4", "lxml==5.4.0", "plotly==6.1.0"]
# ///
"""
fdr_client.py — investing-toolkit FinanceDataReader adapter for Korea macro
Fetches Korea economic indicators via FinanceDataReader's ECOS-KEYSTAT
integration. No API key required.

Usage:
  uv run fdr_client.py --preset policy-rate              # 기준금리
  uv run fdr_client.py --preset cpi,unemployment         # Multiple
  uv run fdr_client.py --preset all                      # All presets
  uv run fdr_client.py --preset policy-rate --no-cache
  uv run fdr_client.py --preset krw-usd                  # KRW/USD (via FDR currency)

Auth: None required. FinanceDataReader accesses BOK ECOS internally.
Cache: $INVESTING_TOOLKIT_CACHE/fdr/{preset}.json  TTL: 24h
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
Source: BOK ECOS via FinanceDataReader (ECOS-KEYSTAT codes)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(Path.home() / ".cache" / "investing-toolkit")
CACHE_DIR = Path(_CACHE_BASE) / "fdr"
CACHE_TTL_SECONDS = 86400  # 24 hours

# ---------------------------------------------------------------------------
# Preset definitions: preset -> (ECOS-KEYSTAT code, name, start_year, source_type)
#
# source_type: "keystat" uses ECOS-KEYSTAT:{code}
#              "currency" uses FDR currency pair syntax
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict] = {
    # --- Rates ---
    "policy-rate": {
        "code": "K051", "name": "BOK Base Rate (한국은행 기준금리)",
        "start": "1999", "source": "keystat",
    },
    "call-rate": {
        "code": "K052", "name": "Call Rate Overnight (콜금리 1일)",
        "start": "1999", "source": "keystat",
    },
    "cd-91d": {
        "code": "K053", "name": "CD 91-Day Rate (CD 91일)",
        "start": "1999", "source": "keystat",
    },
    "treasury-3y": {
        "code": "K056", "name": "Treasury Bond 3Y (국고채 3년)",
        "start": "1999", "source": "keystat",
    },
    "treasury-5y": {
        "code": "K062", "name": "Treasury Bond 5Y (국고채 5년)",
        "start": "1999", "source": "keystat",
    },
    "corp-bond-3y": {
        "code": "K057", "name": "Corporate Bond 3Y AA- (회사채 3년 AA-)",
        "start": "1999", "source": "keystat",
    },
    # --- Inflation ---
    "cpi": {
        "code": "K401", "name": "CPI Total Index (소비자물가 총지수)",
        "start": "1965", "source": "keystat",
    },
    "core-cpi": {
        "code": "K405", "name": "Core CPI excl. food & energy (농산물및석유류제외)",
        "start": "1975", "source": "keystat",
    },
    "ppi": {
        "code": "K402", "name": "PPI Total Index (생산자물가 총지수)",
        "start": "1965", "source": "keystat",
    },
    "import-pi": {
        "code": "K403", "name": "Import Price Index (수입물가 총지수)",
        "start": "1965", "source": "keystat",
    },
    "export-pi": {
        "code": "K404", "name": "Export Price Index (수출물가 총지수)",
        "start": "1965", "source": "keystat",
    },
    # --- Growth ---
    "gdp-qoq": {
        "code": "K258", "name": "GDP Real QoQ SA% (국내총생산 실질 전기비)",
        "start": "1960", "source": "keystat",
    },
    "gdp-nominal": {
        "code": "K257", "name": "GDP Nominal (국내총생산 시장가격 명목)",
        "start": "1960", "source": "keystat",
    },
    "ipi": {
        "code": "K220", "name": "All-Industry Production Index (전산업생산지수)",
        "start": "2000", "source": "keystat",
    },
    "manufacturing": {
        "code": "K201", "name": "Manufacturing Production Index (제조업 생산지수)",
        "start": "2000", "source": "keystat",
    },
    # --- Labor ---
    "unemployment": {
        "code": "K303", "name": "Unemployment Rate % (실업률)",
        "start": "1999", "source": "keystat",
    },
    "employment-rate": {
        "code": "K304", "name": "Employment Rate % (고용률)",
        "start": "1999", "source": "keystat",
    },
    # --- Trade ---
    "current-account": {
        "code": "K351", "name": "Current Account (경상수지 백만USD)",
        "start": "1980", "source": "keystat",
    },
    "terms-of-trade": {
        "code": "K360", "name": "Terms of Trade Index (순상품교역조건지수)",
        "start": "1980", "source": "keystat",
    },
    # --- Money ---
    "m2": {
        "code": "K003", "name": "M2 Broad Money (광의통화 M2 평잔)",
        "start": "2003", "source": "keystat",
    },
    "household-credit": {
        "code": "K007", "name": "Household Credit (가계신용)",
        "start": "2002", "source": "keystat",
    },
    # --- Sentiment / Cycle ---
    "consumer-sentiment": {
        "code": "K252", "name": "Consumer Sentiment Index (소비자심리지수)",
        "start": "2008", "source": "keystat",
    },
    "economic-sentiment": {
        "code": "K269", "name": "Economic Sentiment Index (경제심리지수)",
        "start": "2008", "source": "keystat",
    },
    "leading-cycle": {
        "code": "K254", "name": "Leading CI Cyclical Component (선행지수순환변동치)",
        "start": "2000", "source": "keystat",
    },
    "coincident-cycle": {
        "code": "K253", "name": "Coincident CI Cyclical Component (동행지수순환변동치)",
        "start": "2000", "source": "keystat",
    },
    # --- Markets ---
    "kospi": {
        "code": "K101", "name": "KOSPI Index (코스피지수)",
        "start": "1995", "source": "keystat",
    },
    "kosdaq": {
        "code": "K102", "name": "KOSDAQ Index (코스닥지수)",
        "start": "1999", "source": "keystat",
    },
    # --- FX (via FRED CSV, no auth) ---
    "krw-usd": {
        "code": "DEXKOUS", "name": "KRW/USD Exchange Rate (원달러 환율)",
        "start": "2000", "source": "fred",
    },
    # --- Real Estate ---
    "housing-price": {
        "code": "K407", "name": "Housing Price Index (주택매매가격지수)",
        "start": "2021", "source": "keystat",
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
        "source": "BOK ECOS via FinanceDataReader (ECOS-KEYSTAT)",
        "source_authority": "Bank of Korea (한국은행)",
        "data_type": "official_government_statistics",
        "fetched_at": result.get("fetched_at"),
        "reference_period": ref_period,
        "staleness_days": _compute_staleness(ref_period),
    }


# ---------------------------------------------------------------------------
# Fetch via FinanceDataReader
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

    # Lazy import — FinanceDataReader is heavy
    import FinanceDataReader as fdr

    code = config["code"]
    start = config["start"]
    source = config["source"]

    try:
        if source == "keystat":
            df = fdr.DataReader(f"ECOS-KEYSTAT:{code}", start)
        elif source == "fred":
            # Use FRED CSV endpoint directly (no API key, no FDR dependency)
            import requests as _req
            fred_url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}&cosd={start}-01-01"
            resp = _req.get(fred_url, timeout=15)
            if resp.status_code != 200:
                return {"error": f"FRED HTTP {resp.status_code}", "preset": preset}
            import io, csv
            reader = csv.DictReader(io.StringIO(resp.text))
            observations = []
            for row in reader:
                date_val = row.get("observation_date", row.get("DATE", "")).replace("-", "")
                val_str = row.get(code, "").strip()
                if val_str and val_str != "." and date_val:
                    observations.append({"date": date_val, "value": float(val_str)})
            # Skip the FDR DataFrame path — go straight to result building
            df = None
        else:
            return {"error": f"Unknown source type: {source}"}
    except Exception as e:
        return {"error": f"FDR fetch error: {e}", "preset": preset}

    if source != "fred":
        # DataFrame path (keystat)
        if df is None or len(df) == 0:
            return {"error": f"No data returned for {preset}", "preset": preset}

        observations: list[dict] = []
        for idx, row in df.iterrows():
            date = str(idx)[:10].replace("-", "")[:8]
            value = float(row.iloc[0])
            observations.append({"date": date, "value": value})
    # else: observations already built above for FRED path

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
        "code": code,
        "fetched_at": now,
        "_cache": "miss",
        "_source": "fdr_ecos",
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
        description="FinanceDataReader Korea macro adapter for investing-toolkit",
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
            "_source": "fdr_ecos",
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
