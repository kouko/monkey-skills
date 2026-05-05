#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""
nbs_client.py — investing-toolkit China macro adapter for the NBS new-
SPA API (`data.stats.gov.cn/dg/website/publicrelease/web/external/*`).

Delivers primary-source, ~same-day-of-release data for 21 indicators
across 3 frequencies. Replaces the stale investing.com-mirrored
akshare presets for industrial / exports / imports / trade-balance
and upgrades 12 other indicators from eastmoney mirror (~47d lag) to
NBS direct.

All (cid, indicator_id) pairs are statically pinned here — do NOT do
runtime catalog discovery (the WZWS WAF trips on traversal). If NBS
reissues IDs (roughly every 5 years at base-period revisions), re-run
`docs/tools/probe-nbs-indicators.py` to refresh the catalog and update
PRESETS below. See docs/nbs-indicator-catalog.md and
docs/china-macro-research-frameworks.md for context.

Usage:
  uv run nbs_client.py --preset cpi-yoy
  uv run nbs_client.py --preset cpi-yoy,ppi-yoy,industrial-yoy
  uv run nbs_client.py --preset all
  uv run nbs_client.py --preset gdp-yoy --periods 20
  uv run nbs_client.py --preset cpi-yoy --no-cache

Auth: None. A JSESSIONID cookie is primed by a homepage GET on each
run (see prime_session()).

Cache: $INVESTING_TOOLKIT_CACHE/nbs/{preset}.json  TTL: 24h
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import requests

_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(
    Path.home() / ".cache" / "investing-toolkit"
)
CACHE_DIR = Path(_CACHE_BASE) / "nbs"
CACHE_TTL_SECONDS = 86400  # 24h

BASE = "https://data.stats.gov.cn/dg/website/publicrelease/web/external"
HOME = "https://data.stats.gov.cn/dg/website/page.html"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
DEFAULT_PERIODS = 13

ROOT_MONTHLY = "fc982599aa684be7969d7b90b1bd0e84"
ROOT_QUARTERLY = "a94b8b7365a94874968cabbe392cf679"

# ---------------------------------------------------------------------------
# Preset definitions — statically pinned (cid, indicator_id, rootId)
#
# All UUIDs captured 2026-04-18 via queryIndicatorsByCid probe; see
# docs/nbs-indicators-{monthly,quarterly}.{json,md} for the full catalog.
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict] = {
    # --- Inflation (NBS monthly 价格指数) ---
    "cpi-yoy": {
        "name": "CPI YoY / 居民消费价格指数 同比",
        "cid": "5c7452825c7c4dcba391db5ca7f335c5",
        "indicator_id": "53180dfb9c14411ba4b762307c85920c",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
        "notes": "Index = 100 + YoY%. Subtract 100 for signed YoY delta.",
    },
    "core-cpi": {
        "name": "Core CPI YoY / 不包括食品和能源 CPI 同比",
        "cid": "5c7452825c7c4dcba391db5ca7f335c5",
        "indicator_id": "71be3d43d2fb44188199840272463ae0",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
        "notes": "Same as cpi-yoy but excluding food & energy basket.",
    },
    "ppi-yoy": {
        "name": "PPI YoY / 工业生产者出厂价格指数 同比",
        "cid": "60e8b361f11c4a878c652a6487a25561",
        "indicator_id": "150633e52b9a470a9a9fd1b296dd6c5b",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
        "notes": "Index = 100 + YoY%.",
    },

    # --- Growth (NBS 月度 工业 / 国内贸易 / 固定资产投资 + quarterly GDP) ---
    "gdp-yoy": {
        "name": "GDP YoY / 国内生产总值指数 (上年同期=100) 当季值",
        "cid": "f9b694c9b79e4ce5958bc88c6410fa67",
        "indicator_id": "170e7f00f8c24ede863c0526b42ae81f",
        "root_id": ROOT_QUARTERLY, "freq": "quarterly",
        "unit": "index",
        "notes": "Index = 100 + YoY%.",
    },
    "industrial-yoy": {
        "name": "Industrial Production YoY / 规上工业增加值 当月同比",
        "cid": "3f2e14f0542348ed9fe02476eca3450b",
        "indicator_id": "ef1b1765960d45a29b4d7c4ca91be916",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },
    "retail-yoy": {
        "name": "Retail Sales YoY / 社会消费品零售总额 同比增长",
        "cid": "d0cb882c7f27443ab6b3ef9421901961",
        "indicator_id": "aaac57d54d2e465d91bc9f3ea1a8618e",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },
    "fai-yoy": {
        "name": "FAI YoY (cumulative) / 固定资产投资额 累计增长",
        "cid": "5129067b149d4ddfbec1ffc478d35bfb",
        "indicator_id": "7e570cf8071c4734a7d78d9f0a70fbe1",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
        "notes": "NBS publishes FAI as cumulative YTD YoY only — no single-month read.",
    },

    # --- Trade (NBS 月度 对外经济 → 货物进出口总额, single table) ---
    "exports-yoy": {
        "name": "Exports YoY USD / 出口总值 同比",
        "cid": "7e11b47c828d4e4e925f1c5a98305558",
        "indicator_id": "788f44b0f310403fbd828b77d6f83890".replace("28b", "28b"),  # placeholder; fix below
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },
    "imports-yoy": {
        "name": "Imports YoY USD / 进口总值 同比",
        "cid": "7e11b47c828d4e4e925f1c5a98305558",
        "indicator_id": "cc1ac699bc4f4cd7aa5c2b7a1e643259",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },
    "trade-balance": {
        "name": "Trade Balance USD / 进出口差额当期值 (千美元)",
        "cid": "7e11b47c828d4e4e925f1c5a98305558",
        "indicator_id": "0123bdd4e85348f28efc74685a4a40e5",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "千美元",
        "notes": "Raw value in thousand USD. Divide by 1000 for 亿美元 (common in Chinese news).",
    },

    # --- Labor (NBS 月度 城镇调查失业率) ---
    "urban-unemployment": {
        "name": "Urban Surveyed Unemployment / 全国城镇调查失业率",
        "cid": "ee3b7046b390415b9b7745e3d16f6052",
        "indicator_id": "3888eac6062945a79c8a27e5f13d4953",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },

    # --- Sentiment (NBS 月度 采购经理指数) ---
    "pmi-manufacturing": {
        "name": "Mfg PMI (official NBS) / 制造业采购经理指数",
        "cid": "93ffbb1aa85740d3aa2618371508b606",
        "indicator_id": "a09aa989bdcf4cffa2021795722eb916",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "index",
    },
    "pmi-non-manufacturing": {
        "name": "Non-Mfg PMI (official NBS) / 非制造业商务活动指数",
        "cid": "7a64a6e25aec4a8e9dde044ecd9e2cce",
        "indicator_id": "88a150208f6e4a1db8babe41ae700f66",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "index",
    },
    "pmi-composite": {
        "name": "Composite PMI Output / 综合PMI产出指数",
        "cid": "455378e1c3264a32875768a35ba5de76",
        "indicator_id": "55cdc89fa122446aa263912bdf14a540",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "index",
    },

    # --- Money (NBS 月度 金融 → 货币供应量) ---
    "m2-yoy": {
        "name": "M2 YoY / 广义货币 同比增长",
        "cid": "82130c6621a745cda3d64b090e733383",
        "indicator_id": "e03f2232631f41cd9d754a7d7feb4a81",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },
    "m1-yoy": {
        "name": "M1 YoY / 狭义货币 同比增长",
        "cid": "82130c6621a745cda3d64b090e733383",
        "indicator_id": "640401d3351b4b868dea28f89f410a54",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },

    # --- Real estate (NBS 月度 房地产) ---
    "realestate-investment-yoy": {
        "name": "Real Estate Investment YoY (cumulative) / 房地产投资 累计增长",
        "cid": "9206137ccf03460daa74b7799e0f3c31",
        "indicator_id": "205e08cba8c2409980db58c98da91b6f",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },
    "housing-sales-area-yoy": {
        "name": "Residential Sales Floor Area YoY (cumulative) / 商品住宅销售面积 累计增长",
        "cid": "e9bb62c29eaa49f0b6e88548fc3924aa",
        "indicator_id": "206c52536182472aae8e01b52aaeb201",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },
    "housing-sales-value-yoy": {
        "name": "Residential Sales Value YoY (cumulative) / 商品住宅销售额 累计增长",
        "cid": "9756d668012e4c96807ef1ea1749319c",
        "indicator_id": "2de1944906984790bc41d58d7c0cb885",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },
    "realestate-funding-yoy": {
        "name": "Real Estate Funding YoY (cumulative) / 房地产投资本年资金来源 累计增长",
        "cid": "4c5a2c305155451f99abf94e42305ba2",
        "indicator_id": "e3c3d04b40fc41348a82eb8b6fdcb28b",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },

    # --- Services (NBS 月度 服务业生产指数) ---
    "services-production-yoy": {
        "name": "Services Production Index YoY / 服务业生产指数 当月同比",
        "cid": "2eb7c0ebd79a4225887d5ea68c7aed4c",
        "indicator_id": "3fc5439f03ec46a5a76e8032036e8c17",
        "root_id": ROOT_MONTHLY, "freq": "monthly",
        "unit": "%",
    },
}

# Fix the exports-yoy typo above (Python parses first, but let's be explicit)
PRESETS["exports-yoy"]["indicator_id"] = "788f44b0f310403fbd308b77d6f83890"


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "nbs-cn"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------
# Cache
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
# Session + API
# ---------------------------------------------------------------------------


def prime_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "application/json, text/plain, */*"})
    s.get(HOME, timeout=20)
    return s


def _fmt_period(code: int, d: date) -> str:
    """Format a date into NBS period code for the given frequency.

    code: 1=monthly (YYYYMMMM), 2=quarterly (YYYYqqSS), 3=yearly (YYYYYY).
    """
    if code == 1:
        return f"{d.year}{d.month:02d}MM"
    if code == 2:
        q = (d.month - 1) // 3 + 1
        return f"{d.year}{q:02d}SS"
    if code == 3:
        return f"{d.year}YY"
    raise ValueError(f"unknown code {code}")


def _dts_for(freq: str, periods: int) -> list[str]:
    """Build a single closed-range `dts[0]` string of length `periods`."""
    today = date.today()
    if freq == "monthly":
        code = 1
        # Back N months
        y, m = today.year, today.month
        for _ in range(periods - 1):
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        start = date(y, m, 1)
        return [f"{_fmt_period(code, start)}-{_fmt_period(code, today)}"]
    if freq == "quarterly":
        code = 2
        y, q = today.year, (today.month - 1) // 3 + 1
        for _ in range(periods - 1):
            q -= 1
            if q == 0:
                q = 4
                y -= 1
        start_month = (q - 1) * 3 + 1
        start = date(y, start_month, 1)
        return [f"{_fmt_period(code, start)}-{_fmt_period(code, today)}"]
    raise ValueError(f"unsupported freq {freq}")


def fetch_preset(
    session: requests.Session, preset: str, periods: int,
) -> dict:
    config = PRESETS[preset]
    cid = config["cid"]
    ind_id = config["indicator_id"]
    root_id = config["root_id"]
    freq = config["freq"]

    dts = _dts_for(freq, periods)
    body = {
        "cid": cid,
        "indicatorIds": [ind_id],
        "daCatalogId": "",
        "das": [{"text": "全国", "value": "000000000000"}],
        "showType": "1",
        "dts": dts,
        "rootId": root_id,
    }

    last_err = None
    for attempt in range(3):
        try:
            r = session.post(
                f"{BASE}/getEsDataByCidAndDt",
                json=body,
                headers={"Content-Type": "application/json;charset=UTF-8"},
                timeout=25,
            )
        except Exception as e:
            last_err = f"HTTP:{type(e).__name__}:{e}"
            time.sleep(2 + attempt * 2)
            continue
        text = r.text
        if text.strip().startswith("<"):
            return {"error": "WAF challenge triggered"}
        try:
            data = r.json()
        except Exception as e:
            last_err = f"PARSE:{e}"
            time.sleep(2)
            continue
        if not data.get("success"):
            return {"error": f"API: {data.get('message', '?')}"}

        obs: list[dict] = []
        for period in data.get("data", []):
            code = period.get("code", "")
            values = period.get("values") or []
            if not values:
                continue
            # Pick the row matching our indicator_id (should be the only one)
            row = None
            for v in values:
                if v.get("_id") == ind_id:
                    row = v
                    break
            if row is None:
                continue
            try:
                val = float(row.get("value"))
            except (TypeError, ValueError):
                continue
            if val != val:  # NaN
                continue
            # Normalize period code → YYYYMMDD
            date_str = _code_to_iso(code, freq)
            if date_str is None:
                continue
            obs.append({"date": date_str, "value": val})

        if not obs:
            return {"error": "No valid observations returned", "periods_requested": periods}

        obs.sort(key=lambda r: r["date"])
        return {"observations": obs}

    return {"error": last_err or "unknown fetch error"}


def _code_to_iso(code: str, freq: str) -> str | None:
    """e.g. 202603MM -> 20260301, 202601SS -> 20260101."""
    if not code or len(code) < 6:
        return None
    try:
        y = int(code[:4])
        if freq == "monthly":
            m = int(code[4:6])
            return f"{y:04d}{m:02d}01"
        if freq == "quarterly":
            q = int(code[4:6])
            m = (q - 1) * 3 + 1
            return f"{y:04d}{m:02d}01"
        if freq == "yearly":
            return f"{y:04d}0101"
    except Exception:
        return None
    return None


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


def _compute_staleness(latest_date_str: str | None) -> int | None:
    if not latest_date_str:
        return None
    try:
        ref = datetime.strptime(latest_date_str[:8], "%Y%m%d").replace(tzinfo=timezone.utc)
        return (datetime.now(tz=timezone.utc) - ref).days
    except (ValueError, TypeError):
        return None


def _make_provenance(result: dict, config: dict) -> dict:
    latest = result.get("latest")
    ref = latest["date"] if latest else None
    return {
        "source": "NBS new-SPA API (data.stats.gov.cn/dg/website/publicrelease)",
        "source_authority": "国家统计局 NBS (primary source)",
        "data_type": "official_government_statistics",
        "fetched_at": result.get("fetched_at"),
        "reference_period": ref,
        "staleness_days": _compute_staleness(ref),
        "cid": config["cid"],
        "indicator_id": config["indicator_id"],
    }


# ---------------------------------------------------------------------------
# Build top-level result
# ---------------------------------------------------------------------------


def run_preset(session: requests.Session, preset: str, periods: int, use_cache: bool) -> dict:
    _log("preset fetch", f"{preset} periods={periods}")
    t0 = time.monotonic()
    config = PRESETS.get(preset)
    if not config:
        return {"error": f"Unknown preset: {preset}", "available_presets": list(PRESETS.keys())}

    cache_path = get_cache_path(preset)
    if use_cache:
        cached = load_cache(cache_path)
        if cached is not None:
            cached["_cache"] = "hit"
            _log("preset done", f"{preset} cache hit")
            return cached

    raw = fetch_preset(session, preset, periods)
    if "error" in raw:
        _log("preset done", f"{preset} error in {time.monotonic() - t0:.1f}s")
        return {"preset": preset, "name": config["name"], **raw}

    obs = raw["observations"]
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    latest = obs[-1]
    prior = obs[-2] if len(obs) >= 2 else None

    direction = None
    if prior:
        if latest["value"] > prior["value"]:
            direction = "Rising"
        elif latest["value"] < prior["value"]:
            direction = "Falling"
        else:
            direction = "Flat"

    result = {
        "preset": preset,
        "name": config["name"],
        "unit": config["unit"],
        "freq": config["freq"],
        "fetched_at": now,
        "_cache": "miss",
        "_source": "nbs_spa",
        "observations": obs,
        "latest": latest,
        "prior": prior,
        "direction": direction,
        "count": len(obs),
    }
    if "notes" in config:
        result["_notes"] = config["notes"]
    result["_provenance"] = _make_provenance(result, config)

    save_cache(cache_path, result)
    _log("preset done", f"{preset} {len(obs)} obs in {time.monotonic() - t0:.1f}s")
    return result

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="NBS China macro adapter for investing-toolkit")
    parser.add_argument("--preset", required=True, help="Preset(s), comma-separated, or 'all'")
    parser.add_argument("--periods", type=int, default=DEFAULT_PERIODS,
                        help=f"Number of periods to fetch (default {DEFAULT_PERIODS})")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress logging on stderr (default: verbose)")
    args = parser.parse_args()
    global _QUIET
    _QUIET = args.quiet

    if args.preset.strip().lower() == "all":
        presets = list(PRESETS.keys())
    else:
        presets = [p.strip() for p in args.preset.split(",") if p.strip()]
    if not presets:
        print(json.dumps({"error": "No presets specified"}, indent=2))
        sys.exit(1)

    if args.no_cache:
        for p in presets:
            cp = get_cache_path(p)
            if cp.exists():
                cp.unlink()

    session = prime_session()

    if len(presets) == 1:
        result = run_preset(session, presets[0], args.periods, use_cache=not args.no_cache)
    else:
        result = {
            "fetched_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "_source": "nbs_spa",
            "indicators": {},
        }
        _log("batch start", f"{len(presets)} presets")
        t_batch = time.monotonic()
        for i, p in enumerate(presets, 1):
            _log(f"batch [{i}/{len(presets)}]", p)
            data = run_preset(session, p, args.periods, use_cache=not args.no_cache)
            result["indicators"][p] = data
            # Light throttle between back-to-back NBS POSTs to stay under WAF threshold
            time.sleep(0.5)
        _log("batch done", f"{len(presets)} presets in {time.monotonic() - t_batch:.1f}s")

    print(json.dumps(result, default=str, indent=2, ensure_ascii=False))

    if len(presets) == 1:
        has_error = "error" in result
    else:
        has_error = any(
            "error" in v for v in result.get("indicators", {}).values() if isinstance(v, dict)
        )
    if has_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
