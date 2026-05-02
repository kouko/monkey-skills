#!/usr/bin/env python3
"""
classify_jp.py — JP per-country regime classifier (per ADR-0004 Phase 1).

Framework:
  BOJ stance + Tankan business sentiment DI + ESRI 景気動向指数 CI
  + deflation/inflation regime detection + real-rate decomposition
  + BOJ qualitative anchor (post-2024 exit-deflation transition).

Reads calibrations/jp.yaml. Produces CountryRegimeCard with rich
native_verdict carrying:
  - growth_direction / inflation_direction (legacy IC dimensions for parity)
  - boj_stance: ZIRP | post_zirp | exit_deflation | normalising
  - boj_call_rate_target_pct (currently 0.75)
  - tankan_business_di: 4 categories + mean + dispersion (omitted on missing)
  - cycle_proxy: latest + trend (rising / falling / flat); source field
    indicates whether ESRI coincident-index or IP fallback drove the read
  - deflation_phase: in_deflation | exit_deflation_phase_1/2 | post_deflation
  - real_rate_block: ECB ex-post real-10y monthly + 4-tier band
  - boj_qualitative_anchor: surfaced when restrictive

Mirrors classify_us.py's reference pattern. Each country owns its
native_verdict shape — JP is deliberately framework-divergent from
the US 4-tier real-rate centric design (JP r* range is structurally
different and deflation framing is JP-specific).
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


# Series-key candidates — multiple naming conventions tolerated
POLICY_RATE_KEYS = [
    "STRDCLUCON", "rates.STRDCLUCON", "call-rate-on", "call_rate_on",
]
ESRI_COINCIDENT_KEYS = [
    "coincident-index", "inflation.coincident-index",
    "growth.coincident-index", "ci",
]
# IP fallback when ESRI CI is unavailable — IP is monthly / similar
# tempo and lives in the e-Stat preset bundle. classify_jp prefers CI
# but accepts IP as a graceful-degradation cycle proxy.
GROWTH_FALLBACK_IP_KEYS = ["ip", "inflation.ip", "growth.ip"]
ESRI_LEADING_KEYS = [
    "leading-index", "inflation.leading-index", "growth.leading-index",
]
REAL_10Y_ECB_KEYS = [
    "M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA",
    "real_rates.M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA",
    "real-10y-monthly", "real-10y",
]
TANKAN_INFL_OUTLOOK_KEYS_1Y = [
    "TK99F0000204HCQ00000",
    "real_rates.TK99F0000204HCQ00000",
]

# Tankan business DI codes (matches calibrations/jp.yaml + boj_client.py)
TANKAN_BUSINESS_DI_CATEGORIES: dict[str, list[str]] = {
    "large_mfg": [
        "TK99F1000601GCQ01000",
        "business_sentiment.TK99F1000601GCQ01000",
    ],
    "large_nonmfg": [
        "TK99F2000601GCQ01000",
        "business_sentiment.TK99F2000601GCQ01000",
    ],
    "small_mfg": [
        "TK99F1000601GCQ03000",
        "business_sentiment.TK99F1000601GCQ03000",
    ],
    "small_nonmfg": [
        "TK99F2000601GCQ03000",
        "business_sentiment.TK99F2000601GCQ03000",
    ],
}


def _classify_boj_stance(latest_call_rate: float | None,
                         calib: dict) -> str:
    """Classify BOJ stance from policy rate level (post-2024 framework).

    ZIRP: <= 0.05% (effectively pinned at zero, includes NIRP era)
    post_zirp: 0.05% < rate < 1.0% (post-YCC normalisation, current 0.75%)
    exit_deflation: rate at or above 1.0% lower neutral bound
    """
    if latest_call_rate is None:
        return "unknown"
    if latest_call_rate <= 0.05:
        return "ZIRP"
    nominal_band = calib.get("policy_rate_neutrality", {}).get(
        "nominal_neutral_estimate_band", [1.0, 1.75])
    lower_neutral = nominal_band[0] if nominal_band else 1.0
    if latest_call_rate < lower_neutral:
        return "post_zirp"
    return "exit_deflation"


def _classify_real_rate_band(real_10y: float | None,
                             calib_4tier: dict) -> str:
    """Classify ECB ex-post real-10y into accommodative / neutral /
    restrictive per calibrations/jp.yaml Block 4 thresholds."""
    if real_10y is None:
        return "unknown"
    if real_10y < calib_4tier.get("accommodative", {}).get("upper", 0.0):
        return "accommodative"
    if real_10y < calib_4tier.get("neutral", {}).get("upper", 1.0):
        return "neutral"
    return "restrictive"


def _classify_unemployment_band(unemp: float | None, calib: dict) -> str:
    bands = calib.get("unemployment_bands", {})
    if unemp is None:
        return "unknown"
    if unemp < bands.get("tight", {}).get("upper", 2.5):
        return "tight"
    if unemp < bands.get("balanced", {}).get("upper", 3.1):
        return "balanced"
    return "slack"


def _trend_from_series(values: list[float] | None) -> str:
    """Latest vs prior 3-mo avg (mirrors _legacy_ic.classify_direction
    with normalised band for cycle-style indices)."""
    if values is None or len(values) < 2:
        return "flat"
    return classify_direction(values, normalised=True)


def _build_tankan_business_di_block(
    series: dict, calib: dict,
) -> tuple[dict | None, list[str]]:
    """Compute Tankan business DI mean + dispersion across 4 categories.
    Returns (block, indicators_used). block=None if no categories resolved.
    """
    block: dict[str, Any] = {}
    indicators_used: list[str] = []
    for category, key_candidates in TANKAN_BUSINESS_DI_CATEGORIES.items():
        values = resolve_series(series, key_candidates)
        if values is None:
            block[category] = None
            continue
        block[category] = round(values[-1], 2)
        # Track only the first match per category for clean indicators_used list
        for k in key_candidates:
            if k in series:
                indicators_used.append(k)
                break

    resolved = [v for v in block.values() if v is not None]
    if not resolved:
        return None, indicators_used

    mean_di = round(sum(resolved) / len(resolved), 2)
    dispersion = round(max(resolved) - min(resolved), 2)

    mean_bands = calib.get("tankan_business_di", {}).get("mean_bands", {})
    if mean_di < mean_bands.get("contraction", {}).get("upper", -5):
        regime = "contraction"
    elif mean_di < mean_bands.get("flat", {}).get("upper", 5):
        regime = "flat"
    else:
        regime = "expansion"

    dispersion_warning = dispersion > calib.get("tankan_business_di", {}).get(
        "dispersion_warning_pp", 20)

    block["mean"] = mean_di
    block["dispersion_pp"] = dispersion
    block["regime"] = regime
    block["dispersion_warning"] = dispersion_warning
    return block, indicators_used


def _build_real_rate_block(series: dict, calib: dict) -> dict | None:
    """Real-rate block — ECB ex-post real-10y monthly + 1Y Tankan ex-ante
    inflation outlook (cross-check). Only ECB is required to populate."""
    real_values = resolve_series(series, REAL_10Y_ECB_KEYS)
    if real_values is None:
        return None
    real_10y = real_values[-1]

    block: dict[str, Any] = {
        "real_10y_ecb_expost_pct": round(real_10y, 4),
        "band": _classify_real_rate_band(
            real_10y, calib.get("real_rate_4tier", {})),
        "source": "ECB Data Portal M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA",
        "construction": "ex-post (nominal − realised CPI), NOT TIPS-style ex-ante",
    }

    # Cross-check: 1Y Tankan ex-ante corporate expectations
    tankan_1y = resolve_series(series, TANKAN_INFL_OUTLOOK_KEYS_1Y)
    if tankan_1y is not None:
        block["tankan_inflation_outlook_1y_pct"] = round(tankan_1y[-1], 2)
        bands = calib.get("tankan_inflation_outlook_bands", {})
        v = tankan_1y[-1]
        if v < bands.get("below_target", {}).get("upper", 1.5):
            block["tankan_outlook_anchor"] = "below_target"
        elif v < bands.get("at_target", {}).get("upper", 2.5):
            block["tankan_outlook_anchor"] = "at_target"
        else:
            block["tankan_outlook_anchor"] = "overshoot"

    return block


def _classify_deflation_phase(
    inflation_values: list[float] | None,
    boj_stance: str,
    tankan_outlook_anchor: str | None,
    calib: dict,
) -> str:
    """Multi-signal deflation/inflation regime detection.

    Source: thresholds-japan.md "Structural Regime Notes" + 2026-Q2 grounding.
    Calibration `current_phase` is treated as the default carry-forward when
    signals don't strongly contradict. Live signals can step the phase.
    """
    default_phase = calib.get("current_phase", "exit_deflation_phase_2")

    if inflation_values is None or not inflation_values:
        return default_phase

    latest_cpi = inflation_values[-1]

    # Deflation regime: ZIRP active OR core CPI < 0.5% sustained
    recent_cpi = inflation_values[-4:] if len(inflation_values) >= 4 else inflation_values
    if boj_stance == "ZIRP" and all(v < 0.5 for v in recent_cpi):
        return "in_deflation"

    # Post-deflation: BOJ has clearly normalised + Tankan anchored at-or-above target
    if (boj_stance == "exit_deflation"
            and tankan_outlook_anchor in {"at_target", "overshoot"}
            and latest_cpi >= 1.5):
        return "post_deflation"

    # Phase 2: real wages positive + above-target overshoot tolerated
    # (signal: latest CPI >= 1.8% AND tankan at_target/overshoot)
    if (latest_cpi >= 1.8
            and tankan_outlook_anchor in {"at_target", "overshoot"}):
        return "exit_deflation_phase_2"

    # Phase 1: first sustained 2% achievement
    if latest_cpi >= 1.5:
        return "exit_deflation_phase_1"

    return default_phase


def classify_jp(regime_pack: dict[str, Any]) -> CountryRegimeCard:
    """Classify JP regime per ADR-0004 Phase 1 native framework."""
    series = regime_pack.get("series", {})
    calib_obj = load_calibration("jp")
    calib = calib_obj.raw

    # ----- Growth + inflation direction (legacy IC dimensions for parity) ---
    # Prefer ESRI coincident-index when available (more direct cycle proxy
    # than IP), fall back to legacy resolve order.
    growth_values = (
        resolve_series(series, ESRI_COINCIDENT_KEYS)
        or resolve_series(series, GROWTH_KEYS["jp"])
        or resolve_series(series, GROWTH_FALLBACK_IP_KEYS)
    )
    growth_proxy_used = (
        "coincident-index" if resolve_series(series, ESRI_COINCIDENT_KEYS) is not None
        else ("ip" if growth_values is not None else None)
    )
    inflation_values = resolve_series(series, INFLATION_KEYS["jp"])

    growth_dir = classify_direction(
        growth_values or [], normalised=True)  # CI 一致指数 ~ around 100 trend
    inflation_dir = classify_direction(inflation_values or [], normalised=False)

    ic_quadrant = map_ic_quadrant(growth_dir, inflation_dir)
    gip_regime = map_gip_quad(ic_quadrant)

    # ----- BOJ stance (policy rate level vs neutral) ------------------------
    policy_rate_values = resolve_series(series, POLICY_RATE_KEYS)
    latest_call_rate = policy_rate_values[-1] if policy_rate_values else None
    boj_stance = _classify_boj_stance(latest_call_rate, calib)

    # ----- ESRI 景気動向指数 CI block ---------------------------------------
    leading_values = resolve_series(series, ESRI_LEADING_KEYS)
    coincident_block: dict[str, Any] | None = None
    if growth_values is not None:
        coincident_block = {
            "value": round(growth_values[-1], 2),
            "trend": _trend_from_series(growth_values),
            "source": growth_proxy_used,    # "coincident-index" or "ip" fallback
            "leading_value": (
                round(leading_values[-1], 2) if leading_values else None
            ),
            "leading_trend": _trend_from_series(leading_values)
                if leading_values else None,
        }

    # ----- Tankan business DI block ----------------------------------------
    tankan_block, tankan_keys = _build_tankan_business_di_block(series, calib)

    # ----- Real-rate block -------------------------------------------------
    real_rate_block = _build_real_rate_block(series, calib)

    # ----- Deflation/inflation phase detection -----------------------------
    tankan_outlook_anchor = (
        real_rate_block.get("tankan_outlook_anchor")
        if real_rate_block else None
    )
    deflation_phase = _classify_deflation_phase(
        inflation_values, boj_stance, tankan_outlook_anchor, calib)

    # ----- Unemployment band -----------------------------------------------
    unemp_values = resolve_series(series, ["unemployment", "inflation.unemployment"])
    unemp_band = _classify_unemployment_band(
        unemp_values[-1] if unemp_values else None, calib)

    # ----- BOJ qualitative anchor (surfaced when stance is restrictive) ----
    boj_anchor = None
    if boj_stance in {"exit_deflation"}:
        # Stance has crossed into the neutral lower-bound band — anchor matters
        boj_anchor = (calib.get("boj_qualitative_anchor", "") or "").strip() or None
    elif boj_stance == "post_zirp" and deflation_phase == "exit_deflation_phase_2":
        # Phase 2 transition is taste-sensitive — surface the anchor for context
        boj_anchor = (calib.get("boj_qualitative_anchor", "") or "").strip() or None

    # ----- Indicators actually used (clean dedup) --------------------------
    indicators_used: list[str] = []

    def _track(key_candidates: list[str]) -> None:
        for k in key_candidates:
            if k in series and k not in indicators_used:
                indicators_used.append(k)
                return

    if growth_values is not None:
        _track(ESRI_COINCIDENT_KEYS + GROWTH_KEYS["jp"] + GROWTH_FALLBACK_IP_KEYS)
    if inflation_values is not None:
        _track(INFLATION_KEYS["jp"])
    if policy_rate_values is not None:
        _track(POLICY_RATE_KEYS)
    if leading_values is not None:
        _track(ESRI_LEADING_KEYS)
    if real_rate_block is not None:
        _track(REAL_10Y_ECB_KEYS)
    for k in tankan_keys:
        if k not in indicators_used:
            indicators_used.append(k)
    if unemp_values is not None:
        _track(["unemployment", "inflation.unemployment"])

    # ----- Confidence heuristic --------------------------------------------
    # JP's framework relies on (a) cycle direction (CI or IP), (b) inflation
    # direction (CPI), (c) BOJ stance (call rate). All three present + ≥ 4
    # readings = high; any 2 of 3 + ≥ 4 readings = medium; else low.
    has_growth = growth_values is not None and len(growth_values) >= 4
    has_infl = inflation_values is not None and len(inflation_values) >= 4
    has_rate = policy_rate_values is not None and len(policy_rate_values) >= 4
    score = sum([has_growth, has_infl, has_rate])
    if score == 3:
        confidence = "high"
    elif score >= 2:
        confidence = "medium"
    elif growth_values is not None or inflation_values is not None:
        confidence = "medium"  # weaker but non-degenerate
    else:
        confidence = "low"

    # ----- Data quality -----------------------------------------------------
    missing = []
    if growth_values is None:
        missing.append("growth_proxy (coincident-index / IP)")
    if inflation_values is None:
        missing.append("inflation_proxy (CPI)")
    if policy_rate_values is None:
        missing.append("policy_rate (STRDCLUCON)")
    if real_rate_block is None:
        missing.append("real_rate_decomposition (ECB ex-post)")
    if tankan_block is None:
        missing.append("tankan_business_di (Tankan 業況判断 4 categories)")
    if leading_values is None:
        missing.append("leading-index")
    if unemp_values is None:
        missing.append("unemployment")

    framework_label = (
        "BOJ stance + Tankan business DI + ESRI 景気動向指数 CI "
        "+ deflation regime + real-rate 4-tier"
    )

    native_verdict: dict[str, Any] = {
        "framework_label": framework_label,
        "boj_stance": boj_stance,
        "boj_call_rate_target_pct": calib.get("boj_call_rate_target_pct", 0.75),
        "policy_rate_market_latest_pct": (
            round(latest_call_rate, 4) if latest_call_rate is not None else None
        ),
        "deflation_phase": deflation_phase,
        "growth_direction": growth_dir,
        "inflation_direction": inflation_dir,
        "ic_quadrant_legacy": ic_quadrant,    # for backward reference, not load-bearing
        "gip_regime_legacy": gip_regime,
        "cycle_proxy": coincident_block,
        "tankan_business_di": tankan_block,
        "unemployment_band": unemp_band,
        "real_rate_block": real_rate_block,
        "boj_qualitative_anchor": boj_anchor,
        "last_decision": calib.get("last_decision"),
        "outlook_anchor": calib.get("outlook_anchor"),
    }

    prov = calib.get("provenance", {}) or {}
    return CountryRegimeCard(
        country="jp",
        framework_used=framework_label,
        native_verdict=native_verdict,
        indicators_used=indicators_used,
        data_quality={
            "missing": missing,
            "stale": [],
        },
        confidence=confidence,
        provenance={
            "calibration_doc": prov.get("calibration_doc", "thresholds-japan.md"),
            "calibration_vintage": prov.get("calibration_vintage", "2026-Q2"),
            "last_grounded": (
                prov.get("this_pr_partial_refresh")
                or prov.get("partial_refresh")
                or prov.get("last_full_grounding", "unknown")
            ),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
    )
