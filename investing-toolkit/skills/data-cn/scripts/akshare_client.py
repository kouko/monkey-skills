#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["akshare==1.18.55", "pandas==3.0.2", "requests==2.33.1"]
# ///
"""
akshare_client.py — investing-toolkit China macro adapter via akshare.

Fetches China macro indicators (NBS + PBOC + chinamoney + SAFE) via akshare's
macro_china_* functions. akshare aggregates from mirrors (eastmoney,
investing.com, chinamoney, shibor.org) which remain reachable from foreign
IPs even when NBS data.stats.gov.cn WAF blocks direct access.

Usage:
  uv run akshare_client.py --preset cpi-yoy                    # CPI YoY
  uv run akshare_client.py --preset cpi-yoy,ppi-yoy,gdp-yoy    # Multiple
  uv run akshare_client.py --preset all                        # All presets
  uv run akshare_client.py --preset lpr-1y --no-cache

Auth: None required.
Cache: $INVESTING_TOOLKIT_CACHE/akshare/{preset}.json  TTL: 24h
       Falls back to ~/.cache/investing-toolkit/ if env var not set.
Sources:
  - PBOC (via chinamoney + akshare): LPR, RRR, 社融, new loans
  - SHIBOR (via shibor.org): 3M interbank rate
  - Caixin / S&P Global (via eastmoney mirror, index_pmi_*_cx): Caixin PMI
    (manufacturing + services); fresh source distinct from the 2026-04-18
    removed investing.com mirror.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(
    Path.home() / ".cache" / "investing-toolkit"
)
CACHE_DIR = Path(_CACHE_BASE) / "akshare"
CACHE_TTL_SECONDS = 86400  # 24h

# ---------------------------------------------------------------------------
# Preset definitions
#
# Keys:
#   fn            — akshare function name
#   name          — bilingual label
#   date_col      — column with timestamp
#   value_col     — column with value
#   date_format   — iso / chinese / chinese_month / chinese_quarter / yyyymm / yyyy.m
#   unit          — unit label
#   freq          — daily / monthly / quarterly / event
#   filter_col    — optional: column to filter rows on
#   filter_val    — optional: value required in filter_col (whitespace-stripped)
#   source        — provenance string
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict] = {
    # NOTE: CPI / PPI / GDP / industrial / retail / exports / imports /
    # trade-balance / urban-unemployment / PMI-mfg / PMI-non-mfg / M2 / M1
    # were migrated to `nbs_client.py` on 2026-04-18. NBS new-SPA API is
    # primary source (no mirror lag, ~30-75d freshness vs 47-254d via
    # akshare mirrors). akshare_client.py now serves PBOC-published data
    # (LPR/RRR/SHIBOR/社融/new loans) that NBS does not redistribute in
    # its monthly 金融 subtree, plus Caixin/S&P Global PMI via the
    # eastmoney-backed `index_pmi_*_cx` functions (re-added 2026-04-19,
    # v1.11.0 — distinct endpoint from the stale investing.com-backed
    # `macro_china_cx_*_pmi_yearly` removed 2026-04-18). See
    # docs/nbs-indicator-catalog.md for the migration rationale.

    # --- Sentiment (Caixin / S&P Global via eastmoney) ---
    "caixin-mfg-pmi": {
        "fn": "index_pmi_man_cx",
        "name": "Caixin Manufacturing PMI / 财新制造业 PMI",
        "date_col": "日期", "value_col": "制造业PMI",
        "date_format": "iso", "unit": "index", "freq": "monthly",
        "source": "Caixin / S&P Global via eastmoney",
    },
    "caixin-svc-pmi": {
        "fn": "index_pmi_ser_cx",
        "name": "Caixin Services PMI / 财新服务业 PMI",
        "date_col": "日期", "value_col": "服务业PMI",
        "date_format": "iso", "unit": "index", "freq": "monthly",
        "source": "Caixin / S&P Global via eastmoney",
    },

    # --- Rates (PBOC) ---
    "lpr-1y": {
        "fn": "macro_china_lpr",
        "name": "Loan Prime Rate 1Y / 贷款市场报价利率 1年期",
        "date_col": "TRADE_DATE", "value_col": "LPR1Y",
        "date_format": "iso", "unit": "%", "freq": "monthly",
        "source": "PBOC via chinamoney",
    },
    "lpr-5y": {
        "fn": "macro_china_lpr",
        "name": "Loan Prime Rate 5Y / 贷款市场报价利率 5年期",
        "date_col": "TRADE_DATE", "value_col": "LPR5Y",
        "date_format": "iso", "unit": "%", "freq": "monthly",
        "source": "PBOC via chinamoney",
    },
    "rrr-major": {
        "fn": "macro_china_reserve_requirement_ratio",
        "name": "RRR Major Banks / 大型金融机构 存款准备金率",
        "date_col": "生效时间", "value_col": "大型金融机构-调整后",
        "date_format": "chinese", "unit": "%", "freq": "event",
        "source": "PBOC via akshare",
    },
    "shibor-3m": {
        "fn": "macro_china_shibor_all",
        "name": "SHIBOR 3-Month / 上海银行间同业拆放利率 3个月",
        "date_col": "日期", "value_col": "3M-定价",
        "date_format": "iso", "unit": "%", "freq": "daily",
        "source": "SHIBOR via shibor.org",
    },

    # --- Credit (PBOC-only; M1/M2 migrated to nbs_client.py 2026-04-18) ---
    "shrzgm": {
        "fn": "macro_china_shrzgm",
        "name": "Aggregate Financing / 社会融资规模增量",
        "date_col": "月份", "value_col": "社会融资规模增量",
        "date_format": "yyyymm", "unit": "亿元", "freq": "monthly",
        "source": "PBOC via akshare",
    },
    "new-loans": {
        "fn": "macro_china_new_financial_credit",
        "name": "New RMB Loans / 人民币贷款增量",
        "date_col": "月份", "value_col": "当月",
        "date_format": "chinese_month", "unit": "亿元", "freq": "monthly",
        "source": "PBOC via akshare",
    },

    # NOTE: FX reserves intentionally delegated to fred_client.py
    # (akshare macro_china_foreign_exchange_gold upstream is unreliable).
    # Use: fred_client.py --series TRESEGCNM052N
    # CNY/USD rate: fred_client.py --series DEXCHUS
}

# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "akshare-cn"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


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
# Date parsers
# ---------------------------------------------------------------------------

_CN_QUARTER_MONTH = {"1": "01", "2": "04", "3": "07", "4": "10"}


def _parse_date(raw, fmt: str) -> str | None:
    """Normalize a date cell into YYYYMMDD string."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or s.lower() in ("nan", "none", "nat"):
        return None
    try:
        if fmt == "iso":
            # "2025-09-10" → "20250910"
            return s.replace("-", "").replace("/", "")[:8]
        if fmt == "chinese":
            # "2007年02月25日" → "20070225"
            s2 = s.replace("年", "").replace("月", "").replace("日", "")
            return s2[:8].ljust(8, "0")
        if fmt == "chinese_month":
            # "2025年08月份" → "20250801"
            s2 = s.replace("年", "").replace("月", "").replace("份", "")
            digits = "".join(c for c in s2 if c.isdigit())
            return digits[:6] + "01" if len(digits) >= 6 else None
        if fmt == "chinese_quarter":
            # "2026年第1季度" → "20260101";
            # "2025年第1-4季度" (annual rollup) → skip
            if "-" in s:
                return None
            digits = "".join(c for c in s if c.isdigit())
            if len(digits) < 5:
                return None
            year = digits[:4]
            q = digits[4]
            mm = _CN_QUARTER_MONTH.get(q)
            return f"{year}{mm}01" if mm else None
        if fmt == "yyyymm":
            # "201801" → "20180101"
            digits = "".join(c for c in s if c.isdigit())
            return digits[:6] + "01" if len(digits) >= 6 else None
        if fmt == "yyyy.m":
            # "2026.3" → "20260301"
            if "." in s:
                y, m = s.split(".", 1)
                return f"{int(y):04d}{int(m):02d}01"
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
        clean = latest_date_str.replace("-", "")
        if len(clean) == 6:
            clean += "01"
        ref = datetime.strptime(clean[:8], "%Y%m%d").replace(tzinfo=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        return (now - ref).days
    except (ValueError, TypeError):
        return None


def _make_provenance(result: dict, config: dict) -> dict:
    latest = result.get("latest")
    ref = latest["date"] if latest else None
    return {
        "source": f"akshare:{config['fn']}",
        "source_authority": config["source"],
        "data_type": "official_government_statistics",
        "fetched_at": result.get("fetched_at"),
        "reference_period": ref,
        "staleness_days": _compute_staleness(ref),
    }


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------


def fetch_preset(preset: str, use_cache: bool = True) -> dict:
    _log("preset fetch", preset)
    t0 = time.monotonic()
    config = PRESETS.get(preset)
    if not config:
        return {
            "error": f"Unknown preset: {preset}",
            "available_presets": list(PRESETS.keys()),
        }

    cache_path = get_cache_path(preset)
    if use_cache:
        cached = load_cache(cache_path)
        if cached is not None:
            cached["_cache"] = "hit"
            _log("preset done", f"{preset} cache hit")
            return cached

    import akshare as ak

    try:
        df = getattr(ak, config["fn"])()
    except Exception as e:
        return {"error": f"akshare fetch error: {e}", "preset": preset}

    if df is None or len(df) == 0:
        return {"error": f"No data returned for {preset}", "preset": preset}

    # Optional row filter (e.g. urban_unemployment has multiple series in
    # one DataFrame keyed by an 'item' column)
    filter_col = config.get("filter_col")
    filter_val = config.get("filter_val")
    if filter_col and filter_val is not None:
        if filter_col not in df.columns:
            return {"error": f"filter_col missing: {filter_col}", "preset": preset}
        df = df[df[filter_col].astype(str).str.strip() == filter_val].copy()
        if len(df) == 0:
            return {"error": f"No rows matched {filter_col}={filter_val}", "preset": preset}

    date_col = config["date_col"]
    value_col = config["value_col"]
    date_format = config["date_format"]

    if date_col not in df.columns or value_col not in df.columns:
        return {
            "error": f"Expected columns missing — got {list(df.columns)}",
            "preset": preset,
        }

    observations: list[dict] = []
    for _, row in df.iterrows():
        date_str = _parse_date(row[date_col], date_format)
        if date_str is None:
            continue
        try:
            val = float(row[value_col])
        except (TypeError, ValueError):
            continue
        if val != val:  # NaN
            continue
        observations.append({"date": date_str, "value": val})

    observations.sort(key=lambda r: r["date"])
    dedup: dict[str, dict] = {}
    for o in observations:
        dedup[o["date"]] = o
    observations = list(dedup.values())

    if not observations:
        return {
            "error": f"No numeric observations (all NaN/forecast?) for {preset}",
            "preset": preset,
        }

    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    latest = observations[-1]
    prior = observations[-2] if len(observations) >= 2 else None

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
        "fn": config["fn"],
        "unit": config["unit"],
        "freq": config["freq"],
        "fetched_at": now,
        "_cache": "miss",
        "_source": "akshare",
        "observations": observations,
        "latest": latest,
        "prior": prior,
        "direction": direction,
        "count": len(observations),
    }
    result["_provenance"] = _make_provenance(result, config)

    save_cache(cache_path, result)
    _log("preset done", f"{preset} {len(observations)} obs in {time.monotonic() - t0:.1f}s")
    return result

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="akshare China macro adapter for investing-toolkit",
    )
    parser.add_argument(
        "--preset", required=True,
        help="Preset(s), comma-separated, or 'all'",
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
            "_source": "akshare",
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
