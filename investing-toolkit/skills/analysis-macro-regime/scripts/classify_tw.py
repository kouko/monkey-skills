#!/usr/bin/env python3
"""
classify_tw.py — TW per-country regime classifier (per ADR-0004 Phase 1, PR-4).

Framework:
  NDC 五色景氣燈號 (2024 revision) score-led
  + 9 構成項目 dispersion (with TIER 製造業營業氣候測驗點 overlay when present)
  + leading-index / coincident-index direction
  + CIER PMI (manufacturing + non-manufacturing) regime check
  + TSMC TAIEX concentration overlay (歷史最高)
  + DGBAS CPI YoY in 彈性定義 framing (supply-side vs demand-pull caveat)

Reads calibrations/tw.yaml. Produces CountryRegimeCard with rich
native_verdict carrying:
  - signal_score / signal_color (NDC 五色; primary regime axis)
  - score_band_meaning (semantic + historical context)
  - components_9 (per-component direction + value)
  - tier_manufacturing_climate (TIER subcomponent; None if missing in fixture)
  - leading_index / coincident_index latest values
  - pmi block (manufacturing / non_manufacturing)
  - tsmc_concentration_overlay (TAIEX ≈ TSMC ADR 代理 framing)
  - cpi_context (with cbc_framing = 彈性定義)
  - ic_quadrant_legacy (for backward reference; not the primary axis)

Mirrors PR-2's classify_us.py reference pattern. Reads structured
ndc.signal.data.presets to recover per-component data that is lossy
under the flat-series first-write-wins flatten in pack.py.

Usage (via dispatcher):
  uv run regime_compose.py --input tw=/tmp/tw-regime-pack.json
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from _legacy_ic import (
    GROWTH_KEYS, INFLATION_KEYS,
    classify_direction, map_ic_quadrant, map_gip_quad,
    resolve_series, normalised_country,
)
from _surface import CountryRegimeCard
from calibrations import load_calibration


# Series-key resolution lists (multiple naming conventions tolerated)
SCORE_KEYS = ["signal-score", "ndc.signal-score"]
LEADING_KEYS = ["leading-index", "statgov.leading-index"]
COINCIDENT_KEYS = ["coincident-index", "statgov.coincident-index"]
PMI_MFG_KEYS = ["pmi-mfg", "ndc.pmi-mfg"]
PMI_NMI_KEYS = ["pmi-nmi", "ndc.pmi-nmi"]
CPI_YOY_KEYS = ["cpi-yoy", "inflation.cpi-yoy", "dgbas.cpi-yoy"]

# 9 構成項目 expected names per 2024 revision (Chinese keys; partial-match
# to handle pack-emitted names that include unit suffixes like "(百萬元)"
# or "(Index2021=100)").
COMPONENT_EXPECTED_9 = [
    "貨幣總計數M1B",
    "股價指數",
    "工業生產指數",
    "工業及服務業加班工時",
    "海關出口值",
    "機械及電機設備進口值",
    "製造業銷售量指數",
    "批發、零售及餐飲業營業額",
    "製造業營業氣候測驗點",  # TIER — may be absent in older fixtures
]


def _classify_signal_color(score: float | None, bands: dict) -> tuple[str, str]:
    """Map an NDC signal score (9-45) to (color_zh, color_en) per calibration."""
    if score is None:
        return ("unknown", "unknown")
    for band_name, band_def in bands.items():
        lo = band_def.get("lower", float("-inf"))
        hi = band_def.get("upper", float("inf"))
        if lo <= score <= hi:
            return (band_def.get("color_zh", band_name),
                    band_def.get("color_en", band_name))
    return ("unknown", "unknown")


def _score_band_meaning(score: float | None, calib_ndc: dict) -> str:
    """Generate semantic + historical context for the latest score."""
    if score is None:
        return "score unavailable"
    bands = calib_ndc.get("bands", {})
    color_zh, _ = _classify_signal_color(score, bands)
    historic = calib_ndc.get("historic", {})

    # Locate band entry to read its semantic
    band_semantic = None
    band_phase = None
    for band_def in bands.values():
        lo = band_def.get("lower", float("-inf"))
        hi = band_def.get("upper", float("inf"))
        if lo <= score <= hi:
            band_semantic = band_def.get("semantic", "")
            band_phase = band_def.get("phase", "")
            break

    # Historical context overlays
    if score >= 38 and historic.get("first_red_2024_02"):
        return (
            f"{color_zh}燈 {band_semantic} ({band_phase}); "
            "historical context: 2024-02 首度紅燈 ended 2014-2023 十年無紅燈, "
            "2026-02 三度連續紅燈 (40 分)."
        )
    if score < 17:
        return f"{color_zh}燈 {band_semantic} ({band_phase}); deep slowdown territory."
    return f"{color_zh}燈 {band_semantic} ({band_phase})."


def _read_ndc_signal_block(regime_pack: dict[str, Any]) -> dict[str, Any]:
    """Read structured NDC signal block (preserves color + per-component
    detail that the flat series flatten loses)."""
    out = {
        "score_latest": None,
        "score_history": [],
        "color_latest_zh": None,
        "color_history_zh": [],
        "score_direction": None,
        "components": {},
    }
    ndc_block = regime_pack.get("ndc", {})
    if not isinstance(ndc_block, dict):
        return out
    signal = ndc_block.get("signal", {}) or {}
    data = signal.get("data", {}) or {}
    presets = data.get("presets", {}) or {}

    sig = presets.get("signal", {}) or {}
    score = sig.get("score", {}) or {}
    color = sig.get("color", {}) or {}

    score_obs = score.get("observations", []) or []
    out["score_history"] = [
        float(o["value"]) for o in score_obs
        if isinstance(o, dict) and o.get("value") is not None
    ]
    score_latest = score.get("latest", {}) or {}
    sv = score_latest.get("value")
    if sv is not None:
        try:
            out["score_latest"] = float(sv)
        except (TypeError, ValueError):
            out["score_latest"] = None
    out["score_direction"] = score.get("direction")

    color_obs = color.get("observations", []) or []
    out["color_history_zh"] = [
        o["value"] for o in color_obs
        if isinstance(o, dict) and o.get("value")
    ]
    color_latest = color.get("latest", {}) or {}
    out["color_latest_zh"] = color_latest.get("value")

    components_block = presets.get("signal-components", {}) or {}
    components = components_block.get("components", {}) or {}
    for comp_name, comp_payload in components.items():
        if not isinstance(comp_payload, dict):
            continue
        latest = (comp_payload.get("latest", {}) or {}).get("value")
        prior = (comp_payload.get("prior", {}) or {}).get("value")
        try:
            latest_f = float(latest) if latest is not None else None
        except (TypeError, ValueError):
            latest_f = None
        try:
            prior_f = float(prior) if prior is not None else None
        except (TypeError, ValueError):
            prior_f = None
        out["components"][comp_name] = {
            "latest": latest_f,
            "prior": prior_f,
            "direction": comp_payload.get("direction"),
            "count": comp_payload.get("count"),
        }
    return out


def _match_component(components: dict[str, Any], expected_substring: str) -> tuple[str | None, dict | None]:
    """Find a 9-component entry whose key contains the expected substring
    (handles unit suffixes like '(百萬元)')."""
    for comp_name, payload in components.items():
        if expected_substring in comp_name:
            return comp_name, payload
    return None, None


def _components_9_summary(components: dict[str, Any]) -> dict[str, Any]:
    """Build a 9-slot summary of NDC components keyed by canonical short
    names from COMPONENT_EXPECTED_9. Missing slots are None."""
    summary: dict[str, Any] = {}
    found_count = 0
    rising = 0
    falling = 0
    flat = 0
    for expected in COMPONENT_EXPECTED_9:
        matched_name, payload = _match_component(components, expected)
        if payload is None:
            summary[expected] = None
        else:
            found_count += 1
            direction = payload.get("direction")
            if direction == "Rising":
                rising += 1
            elif direction == "Falling":
                falling += 1
            else:
                flat += 1
            summary[expected] = {
                "matched_name": matched_name,
                "latest": payload.get("latest"),
                "prior": payload.get("prior"),
                "direction": direction,
            }
    summary["_dispersion"] = {
        "components_found": found_count,
        "components_expected": len(COMPONENT_EXPECTED_9),
        "rising": rising,
        "falling": falling,
        "flat_or_unknown": flat,
        "consensus": (
            "rising" if rising >= max(falling + flat, 1) and rising >= 5
            else "falling" if falling >= max(rising + flat, 1) and falling >= 5
            else "mixed"
        ),
    }
    return summary


def _classify_cpi_band(cpi_yoy: float | None, calib_bands: dict) -> str:
    """Classify CPI YoY into 彈性定義 informal bands."""
    if cpi_yoy is None:
        return "unknown"
    above = (calib_bands.get("above_watchline") or {}).get("lower", 2.5)
    near_lo = (calib_bands.get("near_watchline") or {}).get("lower", 1.5)
    if cpi_yoy >= above:
        return "above_watchline"
    if cpi_yoy >= near_lo:
        return "near_watchline"
    return "below_watchline"


def classify_tw(regime_pack: dict[str, Any]) -> CountryRegimeCard:
    """Classify TW regime per ADR-0004 Phase 1 (NDC 五色 + 9 構成 + TSMC overlay)."""
    series = regime_pack.get("series", {})
    calib = load_calibration("tw")
    calib_ndc = calib.get("ndc_signal", {}) or {}
    calib_bands = calib_ndc.get("bands", {}) or {}

    # Structured NDC block (primary regime axis)
    ndc = _read_ndc_signal_block(regime_pack)
    score_latest = ndc["score_latest"]
    color_latest_zh = ndc["color_latest_zh"]

    # Fallback: if structured block missing, resolve from flat series
    if score_latest is None:
        score_series = resolve_series(series, SCORE_KEYS)
        if score_series:
            score_latest = float(score_series[-1])

    # Color resolution: prefer fixture's published 燈號; else compute from
    # score against calibration bands.
    if color_latest_zh:
        color_zh = color_latest_zh
        # Map zh → en via calibration band lookup
        color_en = "unknown"
        for band_def in calib_bands.values():
            if band_def.get("color_zh") == color_zh:
                color_en = band_def.get("color_en", "unknown")
                break
    else:
        color_zh, color_en = _classify_signal_color(score_latest, calib_bands)

    score_band_meaning = _score_band_meaning(score_latest, calib_ndc)

    # 9 構成 components (from structured block)
    components_summary = _components_9_summary(ndc["components"])

    # TIER subcomponent
    tier_payload = components_summary.get("製造業營業氣候測驗點")
    tier_value = (tier_payload or {}).get("latest") if isinstance(tier_payload, dict) else None
    tier_direction = (tier_payload or {}).get("direction") if isinstance(tier_payload, dict) else None

    # Leading + coincident
    leading_series = resolve_series(series, LEADING_KEYS)
    coincident_series = resolve_series(series, COINCIDENT_KEYS)
    leading_latest = leading_series[-1] if leading_series else None
    coincident_latest = coincident_series[-1] if coincident_series else None

    # PMI
    pmi_mfg_series = resolve_series(series, PMI_MFG_KEYS)
    pmi_nmi_series = resolve_series(series, PMI_NMI_KEYS)
    pmi_mfg_latest = pmi_mfg_series[-1] if pmi_mfg_series else None
    pmi_nmi_latest = pmi_nmi_series[-1] if pmi_nmi_series else None

    # CPI
    cpi_yoy_series = resolve_series(series, CPI_YOY_KEYS)
    cpi_yoy_latest = cpi_yoy_series[-1] if cpi_yoy_series else None
    cpi_band = _classify_cpi_band(
        cpi_yoy_latest, calib.get("inflation_signal_bands", {}) or {}
    )

    # IC quadrant (legacy fallback; signal_color is the primary axis)
    growth_values = resolve_series(series, GROWTH_KEYS["tw"])
    inflation_values = resolve_series(series, INFLATION_KEYS["tw"])
    growth_dir = classify_direction(
        growth_values or [], normalised=normalised_country("tw")
    )
    inflation_dir = classify_direction(inflation_values or [], normalised=False)
    ic_quadrant_legacy = map_ic_quadrant(growth_dir, inflation_dir)
    gip_regime_legacy = map_gip_quad(ic_quadrant_legacy)

    # TSMC concentration overlay (static from calibration; no live T1 source in PR-4)
    tsmc = calib.get("tsmc_concentration", {}) or {}
    tsmc_overlay = {
        "weight_pct": tsmc.get("weight_pct"),
        "top_10_pct": tsmc.get("top_10_pct"),
        "tsmc_in_electronics_index_pct": tsmc.get("tsmc_in_electronics_index_pct"),
        "historic_5y_delta_pp": tsmc.get("historic_5y_delta_pp"),
        "as_of": calib.get("provenance", {}).get("calibration_vintage"),
        "note": (tsmc.get("note") or "").strip() or None,
    }

    # Indicators actually used
    indicators_used: list[str] = []
    if ndc["score_history"]:
        indicators_used.append("ndc.signal-score")
    if ndc["color_history_zh"]:
        indicators_used.append("ndc.signal-color")
    if components_summary.get("_dispersion", {}).get("components_found", 0) > 0:
        indicators_used.append("ndc.signal-components")
    if leading_latest is not None:
        indicators_used.append("statgov.leading-index")
    if coincident_latest is not None:
        indicators_used.append("statgov.coincident-index")
    if pmi_mfg_latest is not None:
        indicators_used.append("ndc.pmi-mfg")
    if pmi_nmi_latest is not None:
        indicators_used.append("ndc.pmi-nmi")
    if cpi_yoy_latest is not None:
        indicators_used.append("dgbas.cpi-yoy")

    # Confidence heuristic — TW-specific:
    # high  = score available + ≥ 6 components found + leading & coincident & cpi present
    # medium = score available + components ≥ 4
    # low   = score missing OR components < 4
    found_components = components_summary.get("_dispersion", {}).get("components_found", 0)
    have_leading = leading_latest is not None
    have_coincident = coincident_latest is not None
    have_cpi = cpi_yoy_latest is not None
    if (score_latest is not None and found_components >= 6
            and have_leading and have_coincident and have_cpi):
        confidence = "high"
    elif score_latest is not None and found_components >= 4:
        confidence = "medium"
    else:
        confidence = "low"

    # Data quality
    missing = []
    if score_latest is None:
        missing.append("ndc.signal-score")
    expected_components = len(COMPONENT_EXPECTED_9)
    if found_components < expected_components:
        missing_count = expected_components - found_components
        # Specifically call out TIER if absent (most common gap)
        if tier_value is None:
            missing.append("tier (製造業營業氣候測驗點 — 9th component)")
        if missing_count > 1 or tier_value is not None:
            missing.append(
                f"signal-components (found {found_components}/{expected_components})"
            )
    if leading_latest is None:
        missing.append("leading-index")
    if coincident_latest is None:
        missing.append("coincident-index")
    if cpi_yoy_latest is None:
        missing.append("cpi-yoy")

    framework_label = (
        "NDC 五色景氣燈號 (2024 revision) + 9 構成 dispersion + TIER + "
        "TSMC concentration overlay + DGBAS CPI 彈性定義"
    )

    native_verdict: dict[str, Any] = {
        "framework_label": framework_label,
        "signal_score": score_latest,
        "signal_color": color_zh,
        "signal_color_en": color_en,
        "signal_score_direction": ndc["score_direction"],
        "score_band_meaning": score_band_meaning,
        "components_9": components_summary,
        "tier_manufacturing_climate": {
            "value": tier_value,
            "direction": tier_direction,
            "_note": (
                "TIER (製造業營業氣候測驗點) — 9th component per 2024 revision; "
                "absent in older fixtures predating ndc_client TIER preset."
            ) if tier_value is None else None,
        },
        "leading_index": leading_latest,
        "coincident_index": coincident_latest,
        "pmi": {
            "manufacturing": pmi_mfg_latest,
            "non_manufacturing": pmi_nmi_latest,
            "_note": (
                "CIER PMI: > 50 = expansion, < 50 = contraction"
                if pmi_mfg_latest is not None else None
            ),
        },
        "tsmc_concentration_overlay": tsmc_overlay,
        "cpi_context": {
            "latest_yoy": cpi_yoy_latest,
            "band": cpi_band,
            "cbc_framing": calib.get("cbc_framing", "彈性定義"),
            "cbc_formal_language": calib.get("cbc_formal_language"),
            "supply_vs_demand_caveat": (
                "TW CPI moves often supply-side / imported (energy, food) "
                "more than demand-pull. Don't reflexively map TW CPI > 2% "
                "to Phase 2 Overheat without checking demand vs supply."
            ),
        },
        "policy_rate": {
            "discount_rate": (calib.get("policy_rate") or {}).get("discount_rate"),
            "last_change": str((calib.get("policy_rate") or {}).get("last_change", "")),
            "last_meeting": str((calib.get("policy_rate") or {}).get("last_meeting", "")),
        },
        # Backward-reference IC quadrant — NOT the primary regime axis for TW.
        # Native verdict for TW leads with signal_color; ic_quadrant is kept
        # so downstream consumers expecting the legacy IC field still work.
        "ic_quadrant_legacy": ic_quadrant_legacy,
        "gip_regime_legacy": gip_regime_legacy,
        "growth_direction_legacy": growth_dir,
        "inflation_direction_legacy": inflation_dir,
        # ic_quadrant alias for the test_chain_country_regime_to_macroregime
        # parametrize that asserts "ic_quadrant" key presence on each block.
        "ic_quadrant": ic_quadrant_legacy,
    }

    prov = calib.get("provenance", {}) or {}
    return CountryRegimeCard(
        country="tw",
        framework_used=framework_label,
        native_verdict=native_verdict,
        indicators_used=indicators_used,
        data_quality={
            "missing": missing,
            "stale": [],
        },
        confidence=confidence,
        provenance={
            "calibration_doc": prov.get("calibration_doc", "thresholds-taiwan.md"),
            "calibration_vintage": str(prov.get("calibration_vintage", "2026-Q1")),
            "last_grounded": str(
                prov.get("this_pr_partial_refresh")
                or prov.get("partial_refresh")
                or prov.get("last_full_grounding", "unknown")
            ),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
    )
