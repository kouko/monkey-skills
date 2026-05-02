#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
_helpers.py — shared compute helpers for per-country regime classifiers.

Used by classify_{us,jp,tw,kr,cn}.py modules. Provides:

  - Series resolution (`resolve_series`) for multi-key lookup tolerance
  - Direction classification (`classify_direction`) — latest vs trailing 3-mo
    average ±0.5σ band, with `normalised` mode for indices like CFNAI / K253
  - IC 2x2 quadrant mapping (`map_ic_quadrant`) — used by classifiers that
    emit `ic_quadrant_legacy` / `ic_quadrant` for backward-compat parity
  - Hedgeye GIP refinement mapping (`map_gip_quad`)
  - US-specific Fisher real-rate decomposition (`compute_us_real_rate`)
  - CN-specific 4-component dispersion overlay (`cn_component_overlay`)
  - Per-country GROWTH_KEYS / INFLATION_KEYS lookup tables

Pure stdlib (statistics, typing). No I/O.

Migrated from `_legacy_ic.py` in Phase 1 PR-7 (ADR-0004) — the v1.9.0
unified `classify_country()` was removed once all 5 per-country
classifiers shipped. The helpers themselves remain useful and shared.
"""

from __future__ import annotations

import statistics
from typing import Any

# Country-specific series resolvers — multiple naming conventions tolerated.
GROWTH_KEYS: dict[str, list[str]] = {
    "us": ["nowcast.CFNAI", "CFNAI", "WEI", "GDPC1", "growth.gdp", "gdp"],
    "jp": ["coincident-index", "growth.coincident-index", "ci", "gdp"],
    "tw": [
        "coincident-index",       # statgov.coincident-index also alias-emitted
        "signal-score",           # NDC 五色燈號 9-45 composite
        "ndc.signal-score",
        "leading-index",
        "cycle.signal", "signal", "ndc-signal", "gdp",
    ],
    "kr": ["coincident-cycle", "K253", "cycle.coincident-cycle", "gdp"],
    "cn": [
        "growth.industrial-yoy",
        "industrial-yoy",
        "industrial_yoy",
        "industrial",
        "gdp",
    ],
}

INFLATION_KEYS: dict[str, list[str]] = {
    "us": ["inflation.CPIAUCSL", "CPIAUCSL", "cpi", "cpi-yoy"],
    "jp": ["inflation.cpi-all-items", "cpi-all-items", "cpi", "cpi-yoy"],
    "tw": ["inflation.cpi-yoy", "cpi-yoy", "cpi"],
    "kr": ["inflation.K401", "K401", "cpi", "cpi-yoy"],
    "cn": ["inflation.cpi-yoy", "cpi-yoy", "cpi"],
}

# CN component overlay — flagged if components disagree > 2pp
CN_COMPONENT_KEYS = [
    "industrial-yoy",
    "retail-yoy",
    "fai-yoy",
    "services-production-yoy",
]

# Direction thresholds (fraction of stdev)
DIRECTION_BAND_STDEV = 0.5
NORMALISED_BAND = 0.1
CN_COMPONENT_DISAGREE_PP = 2.0


def resolve_series(series: dict[str, Any], candidate_keys: list[str]) -> list[float] | None:
    """Find first matching key in series dict; return list of floats or None."""
    for key in candidate_keys:
        if key in series:
            raw = series[key]
            if isinstance(raw, list) and len(raw) >= 2:
                try:
                    return [float(x) for x in raw if x is not None]
                except (TypeError, ValueError):
                    continue
    return None


def classify_direction(values: list[float], normalised: bool = False) -> str:
    """Compare latest reading to prior 3-month average."""
    if values is None or len(values) < 2:
        return "flat"
    latest = values[-1]
    prior = values[-4:-1] if len(values) >= 4 else values[:-1]
    if not prior:
        return "flat"
    prior_avg = statistics.fmean(prior)
    delta = latest - prior_avg

    if len(values) >= 4:
        try:
            stdev = statistics.stdev(values[-12:] if len(values) >= 12 else values)
        except statistics.StatisticsError:
            stdev = 0.0
    else:
        stdev = 0.0

    band = max(NORMALISED_BAND, DIRECTION_BAND_STDEV * stdev) if normalised else DIRECTION_BAND_STDEV * stdev
    if band == 0.0:
        band = NORMALISED_BAND if normalised else 0.05

    if delta > band:
        return "rising"
    elif delta < -band:
        return "falling"
    return "flat"


def map_ic_quadrant(growth: str, inflation: str) -> str:
    """IC 2x2 mapping with 'flat' lean conventions (see investment-clock-cheatsheet.md)."""
    g_up = growth in {"rising", "flat"}
    i_up = inflation == "rising"
    if g_up and i_up:
        return "2-overheat"
    if g_up and not i_up:
        return "1-recovery"
    if (not g_up) and i_up:
        return "3-stagflation"
    return "4-reflation"


def map_gip_quad(ic_quadrant: str) -> str:
    """v2.0.0 mapping: Hedgeye Quad N == IC Phase N."""
    return {
        "1-recovery": "quad1",
        "2-overheat": "quad2",
        "3-stagflation": "quad3",
        "4-reflation": "quad4",
    }.get(ic_quadrant, "quad4")


def compute_us_real_rate(series: dict[str, Any]) -> dict[str, Any] | None:
    """US real-rate decomposition: nominal − breakeven = real (Fisher).

    Used by classify_us.py. Kept here for now because it's pure compute
    and country-coupled lookup logic.
    """
    nominal_keys = ["DGS10", "rates.DGS10", "nominal-10y"]
    breakeven_keys = ["T10YIE", "real-rates.T10YIE", "breakeven-10y"]
    tips_keys = ["DFII10", "real-rates.DFII10", "real-10y"]

    nom = resolve_series(series, nominal_keys)
    be = resolve_series(series, breakeven_keys)
    tips = resolve_series(series, tips_keys)

    if nom is None or be is None:
        return None

    nominal_10y = nom[-1]
    breakeven_10y = be[-1]
    real_10y = tips[-1] if tips else (nominal_10y - breakeven_10y)

    identity_check = None
    if tips:
        residual_bp = abs((nominal_10y - breakeven_10y - tips[-1]) * 100)
        identity_check = {
            "residual_bp": round(residual_bp, 2),
            "ok": residual_bp <= 5.0,
        }

    if real_10y < 0.0:
        signal = "accommodative"
    elif real_10y < 1.0:
        signal = "neutral"
    elif real_10y < 1.75:
        signal = "moderately-restrictive"
    else:
        signal = "clearly-restrictive"

    out = {
        "nominal_10y": round(nominal_10y, 4),
        "breakeven_10y": round(breakeven_10y, 4),
        "real_10y": round(real_10y, 4),
        "signal": signal,
    }
    if identity_check is not None:
        out["identity_check"] = identity_check
    return out


def cn_component_overlay(series: dict[str, Any]) -> dict[str, Any] | None:
    """Check CN 4-component agreement; flag if spread > 2pp."""
    components = {}
    for key in CN_COMPONENT_KEYS:
        for variant in (key, f"growth.{key}"):
            if variant in series:
                raw = series[variant]
                if isinstance(raw, list) and len(raw) >= 1:
                    try:
                        components[key] = float(raw[-1])
                    except (TypeError, ValueError):
                        pass
                break
    if len(components) < 2:
        return None

    spread_pp = max(components.values()) - min(components.values())
    return {
        "components": components,
        "spread_pp": round(spread_pp, 2),
        "disagreement_flag": spread_pp > CN_COMPONENT_DISAGREE_PP,
    }


def normalised_country(country: str) -> bool:
    """CFNAI (US) and K253 (KR) cycle indices are normalised — apply NORMALISED_BAND."""
    return country in {"us", "kr"}
