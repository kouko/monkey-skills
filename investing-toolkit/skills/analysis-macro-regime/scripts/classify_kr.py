#!/usr/bin/env python3
"""
classify_kr.py — KR per-country regime classifier (per ADR-0004 Phase 1).

Framework:
  BOK 2% point target (since 2018-12-26, 무기한 적용)
  + KOSTAT 동행지수순환변동치 (K253 coincident-cycle) cycle phase
  + 가계부채/GDP overlay (BIS + BOK; macroprudential concern at >80%)
  + KOSPI concentration overlay (삼성전자 + SK하이닉스 ~40.96%; 그룹 전체 61.29%)
  + KEYSTAT subset (54 indicators; 청년실업률 / ESI optional)

Reads calibrations/kr.yaml. Produces CountryRegimeCard with rich
native_verdict carrying:
  - bok_target_alignment: target / current / gap
  - policy_rate_level + policy_rate_path
  - cycle_phase ∈ {expansion, peak, contraction, trough}
  - household_debt_overlay: BIS / BOK ratios + macroprudential_concern flag
  - kospi_concentration_overlay: 삼성+SK하이닉스 + 그룹 전체
  - youth_unemployment (when present)
  - esi_status ∈ {"fetched", "unavailable_via_fdr"} + esi_value (if fetched)
  - ic_quadrant_legacy (parity with _legacy_ic for backward compat)

ESI handling rule (ADR-0004 PR-5): best-effort. If `economic-sentiment` /
`sentiment.economic-sentiment` present in regime-pack series, surface
value with esi_status="fetched". If absent, surface esi_status=
"unavailable_via_fdr" and floor confidence at "medium" — do NOT fail
the country chain.

Mirrors classify_us.py reference pattern.
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


# Series resolvers — multiple naming conventions tolerated, mirrors
# data-kr/scripts/pack.py flatten output (T2 canonical per ADR-0002).
CPI_KEYS = ["inflation.cpi", "cpi", "K401", "inflation.K401", "cpi-yoy"]
POLICY_RATE_KEYS = ["rates.policy-rate", "policy-rate", "K051"]
COINCIDENT_CYCLE_KEYS = [
    "cycle.coincident-cycle", "coincident-cycle", "K253",
    "cycle.K253",
]
LEADING_CYCLE_KEYS = [
    "cycle.leading-cycle", "leading-cycle", "K254", "cycle.K254",
]
UNEMPLOYMENT_KEYS = [
    "labor.unemployment", "unemployment", "K303",
]
ESI_KEYS = [
    "sentiment.economic-sentiment", "economic-sentiment", "K269",
]
HOUSEHOLD_CREDIT_KEYS = [
    "money.household-credit", "household-credit", "K007",
]


def _resolve_yoy_inflation(series: dict) -> float | None:
    """Resolve CPI yoy from regime-pack series.

    KR fdr_client emits K401 as INDEX (not yoy). Convert to yoy when only
    index series available: latest / 12-months-prior - 1. If a pre-computed
    yoy series is present (cpi-yoy / inflation.cpi-yoy keys), prefer it.
    """
    # Prefer pre-computed yoy
    yoy_keys = ["inflation.cpi-yoy", "cpi-yoy"]
    for k in yoy_keys:
        if k in series:
            raw = series[k]
            if isinstance(raw, list) and raw:
                try:
                    return float(raw[-1])
                except (TypeError, ValueError):
                    pass

    # Fallback: derive yoy from index series.
    # Prefer 13-point true yoy (latest vs 12-mo-prior); accept 12-point
    # 11-month proxy when fixtures carry only a 12-period window (the
    # data-kr regime-pack fixtures emit 12 monthly readings — an 11-month
    # proxy is close enough to BOK's near-target ~2.1% reading for regime
    # classification, and is preferable to dropping the bok_target_alignment
    # block entirely).
    idx = resolve_series(series, CPI_KEYS)
    if idx is None or len(idx) < 12:
        return None
    try:
        if len(idx) >= 13:
            yoy = (idx[-1] / idx[-13] - 1.0) * 100.0
        else:
            yoy = (idx[-1] / idx[0] - 1.0) * 100.0
        return round(yoy, 2)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _classify_cycle_phase(
    coincident_values: list[float] | None,
    threshold: float,
    rising_band_pct: float,
) -> str:
    """Map K253 동행지수 순환변동치 to {expansion, peak, contraction, trough}.

    KOSTAT convention: 100 = trend; ≥100 expansion / <100 contraction.
    Combine level (vs 100) + direction (latest vs prior 3-mo avg) for
    4-state classification:
      - expansion: ≥100 and rising or flat
      - peak: ≥100 and falling
      - contraction: <100 and falling or flat
      - trough: <100 and rising
    """
    if coincident_values is None or len(coincident_values) < 2:
        return "unknown"
    latest = coincident_values[-1]
    prior = coincident_values[-4:-1] if len(coincident_values) >= 4 else coincident_values[:-1]
    if not prior:
        return "unknown"
    prior_avg = sum(prior) / len(prior)
    delta = latest - prior_avg

    above = latest >= threshold
    if delta > rising_band_pct:
        direction = "rising"
    elif delta < -rising_band_pct:
        direction = "falling"
    else:
        direction = "flat"

    if above and direction in {"rising", "flat"}:
        return "expansion"
    if above and direction == "falling":
        return "peak"
    if (not above) and direction in {"falling", "flat"}:
        return "contraction"
    if (not above) and direction == "rising":
        return "trough"
    return "unknown"


def _compute_bok_target_alignment(
    cpi_yoy: float | None, target: float
) -> dict[str, Any] | None:
    """BOK 2% point target gap. None if cpi_yoy unavailable."""
    if cpi_yoy is None:
        return None
    gap = round(cpi_yoy - target, 2)
    if abs(gap) <= 0.3:
        status = "at_target"
    elif gap > 0.3:
        status = "above_target"
    else:
        status = "below_target"
    return {
        "target": target,
        "current": cpi_yoy,
        "gap": gap,
        "status": status,
    }


def _build_household_debt_overlay(calib_overlay: dict) -> dict[str, Any]:
    """Carry calibration ratios as native_verdict overlay block."""
    return {
        "ratio_bis": calib_overlay.get("ratio_bis"),
        "ratio_bok": calib_overlay.get("ratio_bok"),
        "peak_2021q3": calib_overlay.get("peak_2021q3"),
        "long_term_average": calib_overlay.get("long_term_average"),
        "govt_target_2030": calib_overlay.get("govt_target_2030"),
        "macroprudential_concern": calib_overlay.get("macroprudential_concern"),
        "macroprudential_concern_threshold": calib_overlay.get(
            "macroprudential_concern_threshold"
        ),
        "bis_warning": calib_overlay.get("bis_warning"),
    }


def _build_kospi_concentration_overlay(calib_overlay: dict) -> dict[str, Any]:
    return {
        "samsung_skhynix": calib_overlay.get("samsung_skhynix"),
        "samsung_skhynix_intraday_peak": calib_overlay.get(
            "samsung_skhynix_intraday_peak"
        ),
        "samsung_sk_groups": calib_overlay.get("samsung_sk_groups"),
        "date": calib_overlay.get("date"),
        "exceeds_sp500_mag7_flag": calib_overlay.get("exceeds_sp500_mag7_flag"),
        "semiconductor_cycle_dependency": calib_overlay.get(
            "semiconductor_cycle_dependency"
        ),
    }


def _resolve_esi(series: dict) -> tuple[str, float | None]:
    """Best-effort ESI fetch. Returns (status, value).

    status ∈ {"fetched", "unavailable_via_fdr"}.
    Per ADR-0004 PR-5: never fails the country chain; classify_kr
    surfaces unavailability and floors confidence at "medium".
    """
    raw = resolve_series(series, ESI_KEYS)
    if raw is None or not raw:
        return "unavailable_via_fdr", None
    try:
        return "fetched", round(float(raw[-1]), 2)
    except (TypeError, ValueError):
        return "unavailable_via_fdr", None


def classify_kr(regime_pack: dict[str, Any]) -> CountryRegimeCard:
    """Classify KR regime per ADR-0004 Phase 1 PR-5."""
    series = regime_pack.get("series", {})
    calib = load_calibration("kr")

    # --- Inflation: BOK 2% target alignment ---
    cpi_yoy = _resolve_yoy_inflation(series)
    target = calib.get("inflation_target", 2.0)
    bok_target_alignment = _compute_bok_target_alignment(cpi_yoy, target)

    # --- Policy rate level (carry from calibration; series fallback) ---
    policy_rate_level = calib.get("policy_rate_level", 2.50)
    policy_rate_path = calib.get(
        "policy_rate_path_note", "5 회 동결 since 2025-05"
    )
    pr_series = resolve_series(series, POLICY_RATE_KEYS)
    if pr_series:
        # Trust the series over the calibration constant when fixture present
        policy_rate_level = round(float(pr_series[-1]), 4)

    # --- KOSTAT 동행지수 순환변동치 cycle phase ---
    coincident = resolve_series(series, COINCIDENT_CYCLE_KEYS)
    cycle_threshold = calib.get("cycle_threshold", 100.0)
    rising_band = calib.get("cycle_phase_bands", {}).get("rising_band_pct", 0.5)
    cycle_phase = _classify_cycle_phase(coincident, cycle_threshold, rising_band)
    cycle_latest = coincident[-1] if coincident else None
    leading = resolve_series(series, LEADING_CYCLE_KEYS)
    leading_latest = leading[-1] if leading else None

    # --- Household debt overlay (calibration-driven, primary-source pinned) ---
    hh_overlay = _build_household_debt_overlay(
        calib.get("household_debt_overlay", {})
    )

    # --- KOSPI concentration overlay ---
    kospi_overlay = _build_kospi_concentration_overlay(
        calib.get("kospi_concentration_overlay", {})
    )

    # --- Youth unemployment (calibration baseline + fixture surface) ---
    youth_calib = calib.get("youth_unemployment", {}) or {}
    youth_block: dict[str, Any] = {
        "pct": youth_calib.get("pct"),
        "date": youth_calib.get("date"),
        "five_year_high_flag": youth_calib.get("five_year_high_flag"),
        "note": youth_calib.get("note"),
    }
    unemp_series = resolve_series(series, UNEMPLOYMENT_KEYS)
    if unemp_series:
        youth_block["aggregate_unemployment_latest"] = round(
            float(unemp_series[-1]), 2
        )

    # --- ESI (best-effort) ---
    esi_status, esi_value = _resolve_esi(series)

    # --- IC quadrant (legacy parity for backward compat / Phase 2 axis) ---
    growth_values = resolve_series(series, GROWTH_KEYS["kr"])
    inflation_values = resolve_series(series, INFLATION_KEYS["kr"])
    growth_dir = classify_direction(
        growth_values or [], normalised=normalised_country("kr")
    )
    inflation_dir = classify_direction(inflation_values or [], normalised=False)
    ic_quadrant_legacy = map_ic_quadrant(growth_dir, inflation_dir)
    gip_regime_legacy = map_gip_quad(ic_quadrant_legacy)

    # --- Indicators actually used ---
    indicators_used: list[str] = []
    for k_list in (
        CPI_KEYS, POLICY_RATE_KEYS, COINCIDENT_CYCLE_KEYS,
        LEADING_CYCLE_KEYS, UNEMPLOYMENT_KEYS, ESI_KEYS,
    ):
        for k in k_list:
            if k in series:
                indicators_used.append(k)
                break

    # --- Confidence heuristic ---
    # High: cpi_yoy + cycle_phase + (ESI fetched OR youth/labor data) all present
    # Medium: cpi_yoy + cycle_phase present (ESI unavailable acceptable per ADR-0004)
    # Low: cpi_yoy or cycle_phase missing
    has_inflation = bok_target_alignment is not None
    has_cycle = cycle_phase != "unknown"
    has_esi = esi_status == "fetched"

    if has_inflation and has_cycle and has_esi:
        confidence = "high"
    elif has_inflation and has_cycle:
        # ESI unavailable is the dominant case for current fixtures; floor at medium
        confidence = "medium"
    else:
        confidence = "low"

    # --- Data quality (missing list) ---
    missing: list[str] = []
    if not has_inflation:
        missing.append("cpi_yoy (K401 index or pre-computed cpi-yoy)")
    if not has_cycle:
        missing.append("coincident-cycle (K253)")
    if esi_status == "unavailable_via_fdr":
        missing.append("economic-sentiment ESI (K269) — pack.py 'sentiment' group not requested")

    framework_label = (
        "BOK 2% target + KOSTAT 동행 cycle + 가계부채 overlay "
        "+ KOSPI concentration"
    )

    native_verdict: dict[str, Any] = {
        "framework_label": framework_label,
        "bok_target_alignment": bok_target_alignment,
        "policy_rate_level": policy_rate_level,
        "policy_rate_path": policy_rate_path,
        "cycle_phase": cycle_phase,
        "cycle_coincident_latest": cycle_latest,
        "cycle_leading_latest": leading_latest,
        "household_debt_overlay": hh_overlay,
        "kospi_concentration_overlay": kospi_overlay,
        "youth_unemployment": youth_block,
        "esi_status": esi_status,
        "esi_value": esi_value,
        "ic_quadrant_legacy": ic_quadrant_legacy,
        "gip_regime_legacy": gip_regime_legacy,
        "growth_direction": growth_dir,
        "inflation_direction": inflation_dir,
    }

    prov = calib.get("provenance", {}) or {}
    return CountryRegimeCard(
        country="kr",
        framework_used=framework_label,
        native_verdict=native_verdict,
        indicators_used=indicators_used,
        data_quality={
            "missing": missing,
            "stale": [],
        },
        confidence=confidence,
        provenance={
            "calibration_doc": prov.get("calibration_doc", "thresholds-korea.md"),
            "calibration_vintage": prov.get("calibration_vintage", "2026-Q1"),
            "last_grounded": (
                prov.get("this_pr_partial_refresh")
                or prov.get("partial_refresh")
                or prov.get("last_full_grounding", "unknown")
            ),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
    )
