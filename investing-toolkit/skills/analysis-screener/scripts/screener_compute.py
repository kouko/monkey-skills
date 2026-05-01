#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
screener_compute.py — analysis-screener pure-compute layer (v2.0.0)

Reads a pre-batched ticker data JSON file (from data-{country}/pack.py
--pack screener-batch, or concatenated multi-country pack), applies a
preset's filters + scoring, ranks tickers, and emits top-N JSON.

No network, no data fetching — Layer 2 pure-compute contract.

Usage:
  uv run screener_compute.py --input <data-pack.json> --preset value
  uv run screener_compute.py --input - --preset momentum --top-n 20
  uv run screener_compute.py --input pack.json --preset value --pe-max 20

Input JSON formats accepted:
  1. Bare list of records:    [{"ticker": ..., "trailingPE": ...}, ...]
  2. Wrapped pack:             {"tickers": [...], "_provenance": [...]}
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Preset definitions (ported from stock-screener v1.x)
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict] = {
    "value": {
        "filters": {"pe_max": 15.0, "pb_max": 1.5, "div_min": 0.02, "roe_min": 0.05},
        "weights": {"valuation": 0.60, "trend": 0.25, "momentum": 0.15, "quality": 0.0},
    },
    "deep-value": {
        "filters": {"pe_max": 8.0, "pb_max": 0.5},
        "weights": {"valuation": 0.70, "trend": 0.20, "momentum": 0.10, "quality": 0.0},
    },
    "quality": {
        "filters": {"pe_max": 15.0, "pb_max": 1.5, "roe_min": 0.15, "div_min": 0.02},
        "weights": {"valuation": 0.40, "quality": 0.35, "trend": 0.25, "momentum": 0.0},
    },
    "high-dividend": {
        "filters": {"div_min": 0.03, "pe_max": 20.0, "roe_min": 0.05},
        "weights": {"valuation": 0.55, "trend": 0.25, "momentum": 0.20, "quality": 0.0},
    },
    "growth": {
        "filters": {"roe_min": 0.15, "rev_growth_min": 0.05, "earnings_growth_min": 0.10},
        "weights": {"momentum": 0.45, "trend": 0.35, "valuation": 0.20, "quality": 0.0},
    },
    "growth-value": {
        "filters": {"pe_max": 20.0, "roe_min": 0.10, "rev_growth_min": 0.05},
        "weights": {"valuation": 0.40, "momentum": 0.35, "trend": 0.25, "quality": 0.0},
    },
    "momentum": {
        "filters": {"rsi_min": 50.0, "rsi_max": 80.0, "above_sma200": True},
        "weights": {"momentum": 0.50, "trend": 0.40, "valuation": 0.10, "quality": 0.0},
    },
    "balanced": {
        "filters": {},
        "weights": {"valuation": 0.40, "momentum": 0.30, "trend": 0.30, "quality": 0.0},
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _get_field(record: dict, *keys, default=None):
    """Look up the first present key from `keys` in record root or
    record['info'] / record['technicals'] sub-dicts."""
    info = record.get("info") or {}
    tech = record.get("technicals") or {}
    for k in keys:
        for src in (record, info, tech):
            if isinstance(src, dict) and k in src and src[k] is not None:
                return src[k]
    return default


def _normalize_records(payload) -> list[dict]:
    """Accept bare list or wrapped pack; return list of records."""
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("tickers"), list):
            return [r for r in payload["tickers"] if isinstance(r, dict)]
        # Some packs return {"tickers": {"AAPL": {...}, "MSFT": {...}}}
        if isinstance(payload.get("tickers"), dict):
            out = []
            for tkr, body in payload["tickers"].items():
                if isinstance(body, dict):
                    body = {**body}
                    body.setdefault("ticker", tkr)
                    out.append(body)
            return out
    return []


def _load_input(path: str) -> list[dict]:
    if path == "-":
        text = sys.stdin.read()
    else:
        text = Path(path).read_text()
    payload = json.loads(text)
    return _normalize_records(payload)


# ---------------------------------------------------------------------------
# Filter application
# ---------------------------------------------------------------------------


def apply_filters(record: dict, filters: dict) -> tuple[bool, str | None]:
    """Return (passes, fail_reason). Soft-pass when data missing."""
    pe = _get_field(record, "trailingPE")
    pb = _get_field(record, "priceToBook")
    div = _get_field(record, "dividendYield")
    roe = _get_field(record, "returnOnEquity")
    rsi = _get_field(record, "rsi_14")
    rev_g = _get_field(record, "revenueGrowth")
    eps_g = _get_field(record, "earningsGrowth")
    above_sma = _get_field(record, "price_vs_sma200")
    price = _get_field(record, "regularMarketPrice", "latest_close")
    sma200 = _get_field(record, "twoHundredDayAverage", "sma_200")
    vol = _get_field(record, "volume")

    if "pe_max" in filters and pe is not None and pe > filters["pe_max"]:
        return False, f"trailingPE {pe:.2f} > pe_max {filters['pe_max']}"
    if "pb_max" in filters and pb is not None and pb > filters["pb_max"]:
        return False, f"priceToBook {pb:.2f} > pb_max {filters['pb_max']}"
    if "div_min" in filters and div is not None and div < filters["div_min"]:
        return False, f"dividendYield {div:.4f} < div_min {filters['div_min']}"
    if "roe_min" in filters and roe is not None and roe < filters["roe_min"]:
        return False, f"returnOnEquity {roe:.4f} < roe_min {filters['roe_min']}"
    if "rsi_min" in filters and rsi is not None and rsi < filters["rsi_min"]:
        return False, f"rsi_14 {rsi:.1f} < rsi_min {filters['rsi_min']}"
    if "rsi_max" in filters and rsi is not None and rsi > filters["rsi_max"]:
        return False, f"rsi_14 {rsi:.1f} > rsi_max {filters['rsi_max']}"
    if "rev_growth_min" in filters and rev_g is not None and rev_g < filters["rev_growth_min"]:
        return False, f"revenueGrowth {rev_g:.4f} < rev_growth_min {filters['rev_growth_min']}"
    if "earnings_growth_min" in filters and eps_g is not None and eps_g < filters["earnings_growth_min"]:
        return False, (
            f"earningsGrowth {eps_g:.4f} < earnings_growth_min "
            f"{filters['earnings_growth_min']}"
        )
    if filters.get("above_sma200"):
        if above_sma is not None:
            if str(above_sma).lower() != "above":
                return False, "price_vs_sma200 != above"
        elif price is not None and sma200 is not None:
            if price <= sma200:
                return False, f"price {price} <= sma200 {sma200}"
    if "min_volume" in filters and vol is not None and vol < filters["min_volume"]:
        return False, f"volume {vol} < min_volume {filters['min_volume']}"
    return True, None


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_record(record: dict, weights: dict) -> tuple[float, dict, list[str]]:
    """Return (composite_score_0_100, breakdown, warnings)."""
    warnings: list[str] = []

    pe = _get_field(record, "trailingPE")
    if pe is None or pe <= 0:
        valuation = 0.20
        warnings.append("trailingPE missing — neutral 0.20")
    else:
        valuation = _clamp(1.0 / max(pe, 1.0), 0.0, 1.0)

    rsi = _get_field(record, "rsi_14")
    if rsi is None:
        momentum = 0.50
        warnings.append("rsi_14 missing — neutral 0.50")
    else:
        momentum = _clamp(rsi / 100.0, 0.0, 1.0)

    above_sma = _get_field(record, "price_vs_sma200")
    macd = _get_field(record, "macd_crossover")
    if above_sma is None:
        price = _get_field(record, "regularMarketPrice", "latest_close")
        sma200 = _get_field(record, "twoHundredDayAverage", "sma_200")
        if price is not None and sma200 is not None:
            above_sma = "above" if price > sma200 else "below"
        else:
            warnings.append("price_vs_sma200 missing — neutral trend 0.5")
    base = 1.0 if (above_sma is not None and str(above_sma).lower() == "above") else 0.5
    bonus = 0.5 if (macd is not None and str(macd).lower() == "bullish") else 0.0
    trend = _clamp(base + bonus, 0.0, 1.0)

    roe = _get_field(record, "returnOnEquity")
    if roe is None:
        quality = 0.50
        warnings.append("returnOnEquity missing — neutral 0.50")
    else:
        quality = _clamp(float(roe), 0.0, 1.0)

    breakdown = {
        "valuation": round(valuation, 4),
        "momentum": round(momentum, 4),
        "trend": round(trend, 4),
        "quality": round(quality, 4),
    }

    w_v = float(weights.get("valuation", 0.0))
    w_m = float(weights.get("momentum", 0.0))
    w_t = float(weights.get("trend", 0.0))
    w_q = float(weights.get("quality", 0.0))
    total_w = w_v + w_m + w_t + w_q
    if total_w <= 0:
        total_w = 1.0
        w_v, w_m, w_t, w_q = 0.4, 0.3, 0.3, 0.0

    # Renormalize so weights sum to 1 (defensive against partial overrides).
    w_v, w_m, w_t, w_q = (w / total_w for w in (w_v, w_m, w_t, w_q))

    composite = (w_v * valuation + w_m * momentum + w_t * trend + w_q * quality) * 100.0
    return round(composite, 2), breakdown, warnings


# ---------------------------------------------------------------------------
# Top-level pipeline
# ---------------------------------------------------------------------------


def run_screener(
    records: list[dict],
    preset: str,
    top_n: int,
    overrides: dict,
) -> dict:
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset '{preset}'. Choices: {sorted(PRESETS)}")

    base = PRESETS[preset]
    filters = {**base["filters"]}
    weights = {**base["weights"]}

    # Apply overrides (only set keys override).
    filter_overrides = {
        "pe_max": overrides.get("pe_max"),
        "pb_max": overrides.get("pb_max"),
        "rsi_min": overrides.get("rsi_min"),
        "rsi_max": overrides.get("rsi_max"),
        "div_min": overrides.get("div_min"),
        "roe_min": overrides.get("roe_min"),
        "min_volume": overrides.get("min_volume"),
    }
    for k, v in filter_overrides.items():
        if v is not None:
            filters[k] = v
    if overrides.get("above_sma200") is True:
        filters["above_sma200"] = True

    weight_overrides = {
        "valuation": overrides.get("w_valuation"),
        "momentum": overrides.get("w_momentum"),
        "trend": overrides.get("w_trend"),
        "quality": overrides.get("w_quality"),
    }
    for k, v in weight_overrides.items():
        if v is not None:
            weights[k] = v

    ranked: list[dict] = []
    filtered_out: list[dict] = []

    for record in records:
        ticker = record.get("ticker") or _get_field(record, "symbol") or "?"
        passes, reason = apply_filters(record, filters)
        if not passes:
            filtered_out.append({"ticker": ticker, "reason": reason})
            continue
        score, breakdown, warns = score_record(record, weights)
        metrics = {
            "trailingPE": _get_field(record, "trailingPE"),
            "priceToBook": _get_field(record, "priceToBook"),
            "dividendYield": _get_field(record, "dividendYield"),
            "returnOnEquity": _get_field(record, "returnOnEquity"),
            "rsi_14": _get_field(record, "rsi_14"),
            "price_vs_sma200": _get_field(record, "price_vs_sma200"),
            "macd_crossover": _get_field(record, "macd_crossover"),
            "regularMarketPrice": _get_field(
                record, "regularMarketPrice", "latest_close"
            ),
        }
        ranked.append({
            "ticker": ticker,
            "composite_score": score,
            "breakdown": breakdown,
            "metrics": metrics,
            "warnings": warns,
        })

    ranked.sort(key=lambda r: r["composite_score"], reverse=True)
    truncated = ranked[: max(top_n, 0)]
    for i, item in enumerate(truncated, start=1):
        item["rank"] = i

    return {
        "preset_used": preset,
        "filters_applied": filters,
        "weights_applied": weights,
        "ranked": truncated,
        "filtered_out": filtered_out,
        "universe_size": len(records),
        "passed": len(ranked),
        "returned": len(truncated),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="analysis-screener pure-compute layer (v2.0.0)"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to pre-batched ticker data JSON (or '-' for stdin).",
    )
    parser.add_argument(
        "--preset", default="balanced", choices=sorted(PRESETS),
        help="Preset strategy. Default: balanced.",
    )
    parser.add_argument("--top-n", type=int, default=10, help="Return top N. Default: 10.")

    parser.add_argument("--pe-max", type=float, dest="pe_max")
    parser.add_argument("--pb-max", type=float, dest="pb_max")
    parser.add_argument("--rsi-min", type=float, dest="rsi_min")
    parser.add_argument("--rsi-max", type=float, dest="rsi_max")
    parser.add_argument("--div-min", type=float, dest="div_min")
    parser.add_argument("--roe-min", type=float, dest="roe_min")
    parser.add_argument("--min-volume", type=float, dest="min_volume")
    parser.add_argument(
        "--above-sma200", action="store_true", dest="above_sma200",
        help="Require price > SMA-200 (overrides preset).",
    )

    parser.add_argument("--w-valuation", type=float, dest="w_valuation")
    parser.add_argument("--w-momentum", type=float, dest="w_momentum")
    parser.add_argument("--w-trend", type=float, dest="w_trend")
    parser.add_argument("--w-quality", type=float, dest="w_quality")

    args = parser.parse_args()

    try:
        records = _load_input(args.input)
    except Exception as e:
        print(json.dumps({"error": f"Failed to read --input: {e}"}, indent=2))
        return 1

    if not records:
        print(json.dumps({
            "error": "No ticker records found in input",
            "input": args.input,
        }, indent=2))
        return 1

    overrides = {
        "pe_max": args.pe_max, "pb_max": args.pb_max,
        "rsi_min": args.rsi_min, "rsi_max": args.rsi_max,
        "div_min": args.div_min, "roe_min": args.roe_min,
        "min_volume": args.min_volume, "above_sma200": args.above_sma200,
        "w_valuation": args.w_valuation, "w_momentum": args.w_momentum,
        "w_trend": args.w_trend, "w_quality": args.w_quality,
    }

    try:
        result = run_screener(records, args.preset, args.top_n, overrides)
    except Exception as e:
        print(json.dumps({"error": f"Screener compute failed: {e}"}, indent=2))
        return 1

    result["_provenance"] = {
        "skill": "analysis-screener",
        "version": "2.0.0",
        "input_path": args.input,
        "computed_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "layer": "2_analysis_pure_compute",
        "io": "none",
    }

    print(json.dumps(result, default=str, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
