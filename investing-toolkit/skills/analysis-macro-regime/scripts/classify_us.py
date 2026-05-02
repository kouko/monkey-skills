#!/usr/bin/env python3
"""
classify_us.py — US per-country regime classifier (per ADR-0004 Phase 1).

Framework:
  Investment Clock 2x2 + Hedgeye GIP refinement
  + Fed FIT (post-FAIT 2025) policy framework
  + 4-tier real-rate decomposition (HLW / LM / SEP / NY Fed composite)
  + yield curve overlay (T10Y2Y)

Reads calibrations/us.yaml. Produces CountryRegimeCard with rich
native_verdict carrying:
  - growth_direction / inflation_direction (legacy IC dimensions)
  - ic_quadrant + gip_regime
  - real_rate_decomposition: dfii10 + 4-tier band + Fed qualitative anchor
  - yield_curve: t10y2y + state (inverted / flat / normal / steep)
  - policy_framework: FIT
  - inflation_target_pct: 2.0

This is the **reference pattern** for PR-3-6 (JP/TW/KR/CN). Subsequent
country classifiers should mirror this module's structure: signature
`def classify_{country}(regime_pack) -> CountryRegimeCard`, native_verdict
with `framework_label` as first key, indicators_used populated from
actually-read series, confidence heuristic mirroring (high if both
proxies have ≥4 readings).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from _helpers import (
    GROWTH_KEYS, INFLATION_KEYS,
    classify_direction, map_ic_quadrant, map_gip_quad,
    resolve_series, normalised_country,
)
from _surface import CountryRegimeCard
from calibrations import load_calibration


# Real-rate input series — try multiple naming conventions
REAL_RATE_NOMINAL_KEYS = ["DGS10", "rates.DGS10", "nominal-10y"]
REAL_RATE_BREAKEVEN_KEYS = ["T10YIE", "real-rates.T10YIE", "breakeven-10y"]
REAL_RATE_TIPS_KEYS = ["DFII10", "real-rates.DFII10", "real-10y"]
YIELD_CURVE_KEYS = ["T10Y2Y", "rates.T10Y2Y", "yield-spread-10y-2y"]


def _classify_real_rate_band(dfii10: float | None, calib_4tier: dict) -> str:
    """Classify real rate into 4-tier band per calibration."""
    if dfii10 is None:
        return "unknown"
    if dfii10 < calib_4tier.get("accommodative", {}).get("upper", 0.0):
        return "accommodative"
    if dfii10 < calib_4tier.get("neutral", {}).get("upper", 1.0):
        return "neutral"
    if dfii10 < calib_4tier.get("moderately_restrictive", {}).get("upper", 1.75):
        return "moderately_restrictive"
    return "clearly_restrictive"


def _classify_yield_curve(t10y2y: float | None, calib_4tier: dict) -> str:
    """Classify yield curve into 4-state band per calibration."""
    if t10y2y is None:
        return "unknown"
    if t10y2y < calib_4tier.get("inverted", {}).get("upper", -0.10):
        return "inverted"
    if t10y2y < calib_4tier.get("flat", {}).get("upper", 0.20):
        return "flat"
    if t10y2y < calib_4tier.get("normal", {}).get("upper", 1.50):
        return "normal"
    return "steep"


def _compute_real_rate_block(series: dict, calib_4tier: dict) -> dict | None:
    """Real-rate decomposition: nominal − breakeven = real (Fisher)."""
    nom = resolve_series(series, REAL_RATE_NOMINAL_KEYS)
    be = resolve_series(series, REAL_RATE_BREAKEVEN_KEYS)
    tips = resolve_series(series, REAL_RATE_TIPS_KEYS)

    if nom is None or be is None:
        return None

    nominal_10y = nom[-1]
    breakeven_10y = be[-1]
    real_10y = tips[-1] if tips else (nominal_10y - breakeven_10y)

    block: dict[str, Any] = {
        "nominal_10y": round(nominal_10y, 4),
        "breakeven_10y": round(breakeven_10y, 4),
        "real_10y": round(real_10y, 4),
        "band": _classify_real_rate_band(real_10y, calib_4tier),
    }
    if tips:
        residual_bp = abs((nominal_10y - breakeven_10y - tips[-1]) * 100)
        block["fisher_identity_check"] = {
            "residual_bp": round(residual_bp, 2),
            "ok": residual_bp <= 5.0,
        }
    return block


def classify_us(regime_pack: dict[str, Any]) -> CountryRegimeCard:
    """Classify US regime per ADR-0004 Phase 1 reference pattern."""
    series = regime_pack.get("series", {})
    calib = load_calibration("us")

    # Growth + inflation direction (mirrors legacy IC)
    growth_values = resolve_series(series, GROWTH_KEYS["us"])
    inflation_values = resolve_series(series, INFLATION_KEYS["us"])
    growth_dir = classify_direction(
        growth_values or [], normalised=normalised_country("us"))
    inflation_dir = classify_direction(inflation_values or [], normalised=False)

    ic_quadrant = map_ic_quadrant(growth_dir, inflation_dir)
    gip_regime = map_gip_quad(ic_quadrant)

    # Real-rate overlay
    real_rate_block = _compute_real_rate_block(
        series, calib.get("real_rate_4tier", {}))

    # Yield curve overlay
    yield_curve_series = resolve_series(series, YIELD_CURVE_KEYS)
    yield_curve_latest = yield_curve_series[-1] if yield_curve_series else None
    yield_curve_state = _classify_yield_curve(
        yield_curve_latest, calib.get("yield_curve_4tier", {}))

    # Fed qualitative anchor — surfaced when real-rate is restrictive
    fed_anchor = None
    if real_rate_block and real_rate_block["band"] in (
            "moderately_restrictive", "clearly_restrictive"):
        fed_anchor = calib.get("fed_qualitative_anchor", "").strip() or None

    # Indicators actually used
    indicators_used: list[str] = []
    if growth_values:
        for k in GROWTH_KEYS["us"]:
            if k in series:
                indicators_used.append(k)
                break
    if inflation_values:
        for k in INFLATION_KEYS["us"]:
            if k in series:
                indicators_used.append(k)
                break
    for k in REAL_RATE_NOMINAL_KEYS + REAL_RATE_BREAKEVEN_KEYS + REAL_RATE_TIPS_KEYS:
        if k in series and k not in indicators_used:
            indicators_used.append(k)
            break  # one per category
    for k in YIELD_CURVE_KEYS:
        if k in series and k not in indicators_used:
            indicators_used.append(k)
            break

    # Confidence heuristic (mirrors legacy IC for parity)
    has_g = growth_values is not None and len(growth_values) >= 4
    has_i = inflation_values is not None and len(inflation_values) >= 4
    if has_g and has_i:
        confidence = "high"
    elif growth_values is not None and inflation_values is not None:
        confidence = "medium"
    else:
        confidence = "low"

    # Data quality
    missing = []
    if not growth_values:
        missing.append("growth_proxy")
    if not inflation_values:
        missing.append("inflation_proxy")
    if real_rate_block is None:
        missing.append("real_rate_decomposition (DGS10 / T10YIE)")
    if yield_curve_latest is None:
        missing.append("yield_curve (T10Y2Y)")

    framework_label = (
        "IC + Hedgeye GIP + Fed FIT + 4-tier real-rate + yield curve"
    )

    native_verdict: dict[str, Any] = {
        "framework_label": framework_label,
        "growth_direction": growth_dir,
        "inflation_direction": inflation_dir,
        "ic_quadrant": ic_quadrant,
        "gip_regime": gip_regime,
        "real_rate_decomposition": real_rate_block,
        "yield_curve": {
            "t10y2y": yield_curve_latest,
            "state": yield_curve_state,
        },
        "fed_qualitative_anchor": fed_anchor,
        "policy_framework": calib.get("inflation_target_framework", "FIT"),
        "inflation_target_pct": calib.get("inflation_target", 2.0),
    }

    prov = calib.get("provenance", {}) or {}
    return CountryRegimeCard(
        country="us",
        framework_used=framework_label,
        native_verdict=native_verdict,
        indicators_used=indicators_used,
        data_quality={
            "missing": missing,
            "stale": [],
        },
        confidence=confidence,
        provenance={
            "calibration_doc": prov.get("calibration_doc", "thresholds-us.md"),
            "calibration_vintage": prov.get("calibration_vintage", "2026-Q1"),
            "last_grounded": (
                prov.get("this_pr_partial_refresh")
                or prov.get("partial_refresh")
                or prov.get("last_full_grounding", "unknown")
            ),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
    )
