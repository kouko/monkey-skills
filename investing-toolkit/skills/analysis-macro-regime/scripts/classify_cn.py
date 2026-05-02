#!/usr/bin/env python3
"""
classify_cn.py — China per-country regime classifier (per ADR-0004 Phase 1).

Framework:
  PBOC reaction (7天逆回购 primary, 2024-07 框架) +
  credit impulse (CICC TSF stock yoy 12-month change convention) +
  4-component growth dispersion (industrial / retail / FAI / services) +
  property cycle overlay (deleveraging phase, single-side drag) +
  CPI framing (central-tendency 2.0 target, NOT ceiling — 2025 起首次)

Reads calibrations/cn.yaml. Produces CountryRegimeCard with rich
native_verdict carrying:
  - growth_direction / inflation_direction (legacy IC dimensions)
  - ic_quadrant_legacy + gip_regime (parity with legacy classifier)
  - pboc_stance: 适度宽松 etc. (current 2026-Q1)
  - policy_rate_primary: 7D 逆回购 1.40%
  - policy_rate_quantitative_tools: MLF / LPR / RRR
  - cpi_framing: target 2.0 + current + gap + policy_stance enum
  - credit_impulse: value, trend, methodology
  - 4_component_dispersion: industrial/retail/fai/services + spread + alarm
  - property_overlay: GDP shares + deleveraging phase

Key CN-specific design choice: cpi_framing.policy_stance enum captures
"PBOC wants inflation up; rising inflation in disinflation regime = good
news, not stagflation warning". This is what makes the CN classifier
non-trivial vs. the legacy IC quadrant. Specifically the
`supportive_recovery_below_target` value fires when current < 1.5 AND
inflation_direction == "rising" — bullish-recovery framing in a regime
that legacy IC would print as 1-recovery or 4-reflation depending on
growth direction.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from _legacy_ic import (
    GROWTH_KEYS, INFLATION_KEYS,
    classify_direction, map_ic_quadrant, map_gip_quad,
    resolve_series, normalised_country, cn_component_overlay,
)
from _surface import CountryRegimeCard
from calibrations import load_calibration


# Series resolvers — multiple naming conventions tolerated, mirroring _legacy_ic
PBOC_7D_RR_KEYS = ["7d-reverse-repo", "7d_reverse_repo", "akshare.7d-reverse-repo"]
LPR_1Y_KEYS = ["lpr-1y", "akshare.lpr-1y", "lpr_1y"]
LPR_5Y_KEYS = ["lpr-5y", "akshare.lpr-5y", "lpr_5y"]
RRR_KEYS = ["rrr-major", "akshare.rrr-major", "rrr_major"]
TSF_FLOW_KEYS = ["shrzgm", "akshare.shrzgm", "tsf-flow", "tsf_flow_monthly"]
TSF_STOCK_YOY_KEYS = ["tsf-stock-yoy", "tsf_stock_yoy", "shrzck-yoy"]
M2_YOY_KEYS = ["m2-yoy", "nbs.m2-yoy", "m2_yoy"]
CREDIT_IMPULSE_KEYS = ["credit_impulse", "cn.credit_impulse"]


def _normalise_cpi(values: list[float]) -> list[float]:
    """NBS publishes CPI as «上年同月=100» index (e.g. 101.0 = +1.0% YoY).
    Convert to plain YoY % so thresholds (target 2.0, gap calc) work.

    Heuristic: if all observations sit in [95, 110] it's the index form;
    otherwise assume already in YoY % form.
    """
    if not values:
        return values
    if all(95.0 <= v <= 110.0 for v in values):
        return [v - 100.0 for v in values]
    return values


def _classify_cpi_framing(current: float | None,
                          direction: str,
                          calib: dict) -> dict[str, Any]:
    """CN-specific CPI framing. Target = 2.0 central tendency (2025 起).

    policy_stance enum (key insight: rising inflation in disinflation
    regime = supportive recovery, NOT overheat):

      - supportive_recovery_below_target: current < 1.5 AND rising
      - near_target_balanced: |current − 2.0| < 0.5
      - below_target_persistent: 0.0 < current < 1.5 AND not rising
      - deflation_risk: 0.0 ≤ current < 0.5 (regardless of direction)
      - deflation_confirmed: current < 0.0
      - above_target_concern: current > 2.5
    """
    target = float(calib.get("inflation_target", 2.0))
    framing_calib = calib.get("cpi_framing", {}) or {}
    near_band = framing_calib.get("near_target_band", [1.5, 2.5])
    deflation_floor = framing_calib.get("deflation_confirmed_below", 0.0)
    deflation_risk_band = framing_calib.get("deflation_risk_band", [0.0, 0.5])
    above_target_above = framing_calib.get("above_target_above", 2.5)

    if current is None:
        return {
            "target": target,
            "current": None,
            "gap": None,
            "policy_stance": "unknown",
            "framing_note": "current CPI YoY unavailable",
        }

    gap = round(current - target, 3)

    if current < deflation_floor:
        stance = "deflation_confirmed"
    elif deflation_risk_band[0] <= current < deflation_risk_band[1]:
        stance = "deflation_risk"
    elif current > above_target_above:
        stance = "above_target_concern"
    elif near_band[0] <= current <= near_band[1]:
        stance = "near_target_balanced"
    elif current < near_band[0]:
        # Below target but not at deflation risk; check direction
        if direction == "rising":
            stance = "supportive_recovery_below_target"
        else:
            stance = "below_target_persistent"
    else:
        stance = "near_target_balanced"  # fallback (band edge cases)

    return {
        "target": target,
        "current": round(current, 3),
        "gap": gap,
        "policy_stance": stance,
        "framing_note": (
            "CN target is central-tendency (2025 起 from ceiling). "
            "Rising inflation in disinflation regime = supportive."
        ),
    }


def _compute_4_component_dispersion(series: dict, calib: dict) -> dict[str, Any]:
    """4-component panel: industrial / retail / FAI / services.

    Reuses legacy `cn_component_overlay` for the spread computation, then
    augments with calibration-aware alarm threshold + per-component values.
    """
    overlay = cn_component_overlay(series) or {}
    components = overlay.get("components", {})
    spread = overlay.get("spread_pp")
    alarm_threshold = float(calib.get("growth_components", {})
                            .get("dispersion_alarm_pp", 2.0))
    return {
        "industrial": components.get("industrial-yoy"),
        "retail": components.get("retail-yoy"),
        "fai": components.get("fai-yoy"),
        "services": components.get("services-production-yoy"),
        "spread_pp": spread,
        "alarm_threshold_pp": alarm_threshold,
        "alarm": (spread is not None and spread > alarm_threshold),
        "components_present": len(components),
    }


def _classify_credit_impulse(series: dict, calib: dict) -> dict[str, Any] | None:
    """Credit impulse — prefer pre-computed cn_specific block, then derive
    from TSF stock yoy or fall back to TSF flow → trailing-12m-sum-yoy
    proxy or M2 yoy.

    Convention per `references/credit-impulse-methodology.md`: TSF stock
    yoy 12-month change (CICC middle-flavor; 6-9mo lead vs growth).
    """
    ci_calib = calib.get("credit_impulse", {}) or {}
    threshold = float(ci_calib.get("primary_pp_threshold", 0.5))

    def _trend(impulse_pp: float) -> str:
        if impulse_pp > threshold:
            return "expanding"
        if impulse_pp < -threshold:
            return "contracting"
        return "neutral"

    # Path 1: pre-computed credit_impulse block (preferred — comes from
    # data-cn/pack.py:_compute_credit_impulse() if upstream provided it).
    pre = resolve_series(series, CREDIT_IMPULSE_KEYS)
    if pre and len(pre) >= 1:
        impulse = pre[-1]
        return {
            "value": round(impulse, 3),
            "trend": _trend(impulse),
            "threshold_pp": threshold,
            "methodology": (
                "pre-computed by data-cn/pack._compute_credit_impulse()"
            ),
            "source": "regime_pack.cn_specific.credit_impulse",
        }

    # Path 2: TSF stock yoy (if data layer ever publishes it directly)
    stock_yoy = resolve_series(series, TSF_STOCK_YOY_KEYS)
    if stock_yoy and len(stock_yoy) >= 13:
        impulse = stock_yoy[-1] - stock_yoy[-13]
        return {
            "value": round(impulse, 3),
            "trend": _trend(impulse),
            "threshold_pp": threshold,
            "methodology": "TSF stock yoy 12-month change (CICC convention)",
            "source": "regime_pack.series.tsf-stock-yoy",
        }

    # Path 3: TSF monthly flow (akshare shrzgm) → derive stock-yoy proxy
    # via trailing-12m sum.
    flow = resolve_series(series, TSF_FLOW_KEYS)
    if flow and len(flow) >= 25:
        # Compute trailing-12m sums and stock-yoy from those.
        recent_sum = sum(flow[-12:])
        prior_sum_t12 = sum(flow[-24:-12])
        if prior_sum_t12 != 0:
            stock_yoy_now = (recent_sum - prior_sum_t12) / prior_sum_t12 * 100
        else:
            stock_yoy_now = None
        # 12-mo prior stock-yoy
        if len(flow) >= 37:
            prior_recent = sum(flow[-24:-12])
            prior_prior = sum(flow[-36:-24])
            stock_yoy_prior = (
                (prior_recent - prior_prior) / prior_prior * 100
                if prior_prior != 0 else None
            )
        else:
            stock_yoy_prior = None
        if stock_yoy_now is not None and stock_yoy_prior is not None:
            impulse = stock_yoy_now - stock_yoy_prior
            return {
                "value": round(impulse, 3),
                "trend": _trend(impulse),
                "threshold_pp": threshold,
                "methodology": (
                    "TSF flow → trailing-12m-sum YoY → 12-month change. "
                    "Flow-yoy second-derivative, NOT stock-yoy (PBOC stock "
                    "series unavailable in akshare). Trend direction "
                    "(expanding/contracting) is the load-bearing signal; "
                    "magnitude runs 5-20pp larger than true stock-yoy."
                ),
                "source": "regime_pack.series.shrzgm (akshare)",
                "tsf_flow_yoy_now": round(stock_yoy_now, 3),
                "tsf_flow_yoy_12mo_prior": round(stock_yoy_prior, 3),
            }
        if stock_yoy_now is not None:
            # Have current proxy but not enough history for 12-mo prior;
            # report stock-yoy level instead of impulse.
            return {
                "value": None,
                "trend": "neutral",
                "threshold_pp": threshold,
                "methodology": (
                    "TSF flow → trailing-12m-sum yoy proxy. Insufficient "
                    "history (need ≥37 monthly flow obs) for 12mo Δ."
                ),
                "source": "regime_pack.series.shrzgm (akshare)",
                "tsf_stock_yoy_proxy_now": round(stock_yoy_now, 3),
                "tsf_stock_yoy_proxy_12mo_prior": None,
            }

    # Path 4: M2 fallback
    m2 = resolve_series(series, M2_YOY_KEYS)
    if m2 and len(m2) >= 13:
        impulse = m2[-1] - m2[-13]
        return {
            "value": round(impulse, 3),
            "trend": _trend(impulse),
            "threshold_pp": threshold,
            "methodology": (
                "M2 yoy 12-month change (TSF unavailable fallback; less "
                "precise — M2 ↔ credit linkage weakened by 2024-2025 "
                "re-categorization)"
            ),
            "source": "regime_pack.series.m2-yoy",
        }

    return None


def _scalar_or_none(values: list[float] | None) -> float | None:
    if values:
        try:
            return float(values[-1])
        except (TypeError, ValueError):
            return None
    return None


def classify_cn(regime_pack: dict[str, Any]) -> CountryRegimeCard:
    """Classify CN regime per ADR-0004 Phase 1 native framework."""
    series = regime_pack.get("series", {})
    calib_obj = load_calibration("cn")
    calib = calib_obj.raw

    # Growth + inflation direction (mirrors legacy IC dimensions for parity)
    growth_values = resolve_series(series, GROWTH_KEYS["cn"])
    raw_inflation = resolve_series(series, INFLATION_KEYS["cn"])
    inflation_values = _normalise_cpi(raw_inflation) if raw_inflation else raw_inflation

    growth_dir = classify_direction(
        growth_values or [], normalised=normalised_country("cn"))
    inflation_dir = classify_direction(inflation_values or [], normalised=False)

    ic_quadrant_legacy = map_ic_quadrant(growth_dir, inflation_dir)
    gip_regime = map_gip_quad(ic_quadrant_legacy)

    # CPI framing (CN-specific central-tendency framework)
    cpi_current = _scalar_or_none(inflation_values)
    cpi_framing = _classify_cpi_framing(cpi_current, inflation_dir, calib)

    # Credit impulse (CICC convention)
    credit_impulse = _classify_credit_impulse(series, calib)

    # 4-component growth dispersion
    dispersion = _compute_4_component_dispersion(series, calib)

    # PBOC stance + policy rate block (calibration-driven; current 适度宽松)
    pboc_stance = calib.get("current_stance", "稳健")
    policy_rate_calib = calib.get("policy_rate", {}) or {}
    primary_block = policy_rate_calib.get("primary", {}) or {}
    quant_block = policy_rate_calib.get("quantitative_tools", {}) or {}
    structural_block = policy_rate_calib.get("structural_easing", {}) or {}
    fx_macro_block = policy_rate_calib.get("fx_macroprudential", {}) or {}

    # Try resolving live policy rates from regime_pack series; fall back to
    # calibration values if missing. This makes the verdict reflect actual
    # regime_pack data while still surfacing the calibrated anchor.
    lpr_1y_live = _scalar_or_none(resolve_series(series, LPR_1Y_KEYS))
    lpr_5y_live = _scalar_or_none(resolve_series(series, LPR_5Y_KEYS))
    rrr_live = _scalar_or_none(resolve_series(series, RRR_KEYS))

    policy_rate_primary = {
        "name": primary_block.get("name", "7-day reverse repo / 7天逆回购"),
        "rate": primary_block.get("rate", 1.40),
        "last_change": primary_block.get("last_change", "2025-09"),
        "moved_2025_09": True,
        "source": primary_block.get("source", "PBOC 公开市场业务"),
    }
    policy_rate_quantitative = {
        "mlf_1y": quant_block.get("mlf_1y", 2.0),
        "lpr_1y": lpr_1y_live if lpr_1y_live is not None else quant_block.get("lpr_1y", 3.0),
        "lpr_5y": lpr_5y_live if lpr_5y_live is not None else quant_block.get("lpr_5y", 3.5),
        "rrr_large_bank": rrr_live if rrr_live is not None else quant_block.get("rrr_large_bank", 9.0),
        "rrr_weighted": quant_block.get("rrr_weighted", 6.2),
        "rrr_average": quant_block.get("rrr_average", 6.3),
        "_note": "MLF is 数量工具 since 2024-07, NOT a policy rate anchor.",
    }

    # Property overlay (structural)
    prop_calib = calib.get("property_overlay", {}) or {}
    property_overlay = {
        "gdp_share_direct": prop_calib.get("gdp_share_direct", 0.236),
        "gdp_share_incl_infra": prop_calib.get("gdp_share_incl_infra", 0.31),
        "gdp_share_nbs_narrow": prop_calib.get("gdp_share_nbs_narrow", 0.063),
        "deleveraging_phase": prop_calib.get("deleveraging_phase", True),
        "q1_2026_property_investment_yoy": prop_calib.get(
            "q1_2026_property_investment_yoy", -11.2),
        "q1_2026_residential_sales_value_yoy": prop_calib.get(
            "q1_2026_residential_sales_value_yoy", -16.7),
    }

    # Indicators actually used (one per category)
    indicators_used: list[str] = []
    if growth_values:
        for k in GROWTH_KEYS["cn"]:
            if k in series:
                indicators_used.append(k)
                break
    if inflation_values:
        for k in INFLATION_KEYS["cn"]:
            if k in series:
                indicators_used.append(k)
                break
    if dispersion["components_present"] > 0:
        for k in ("industrial-yoy", "retail-yoy", "fai-yoy",
                  "services-production-yoy"):
            if k in series and k not in indicators_used:
                indicators_used.append(k)
    if credit_impulse:
        # Tag the source series name(s)
        src = credit_impulse.get("source", "")
        for tag in ("shrzgm", "tsf-stock-yoy", "m2-yoy", "credit_impulse"):
            if tag in src and tag not in indicators_used:
                indicators_used.append(tag)
                break
    for k in (LPR_1Y_KEYS + RRR_KEYS):
        if k in series and k not in indicators_used:
            indicators_used.append(k)
            break

    # Confidence heuristic (mirrors legacy IC for parity)
    has_g = growth_values is not None and len(growth_values) >= 4
    has_i = inflation_values is not None and len(inflation_values) >= 4
    if has_g and has_i and credit_impulse and credit_impulse.get("value") is not None:
        confidence = "high"
    elif growth_values is not None and inflation_values is not None:
        confidence = "medium"
    else:
        confidence = "low"

    # Data quality
    missing = []
    if not growth_values:
        missing.append("growth_proxy (industrial-yoy)")
    if not inflation_values:
        missing.append("inflation_proxy (cpi-yoy)")
    if dispersion["components_present"] < 4:
        missing.append(
            f"4-component panel ({4 - dispersion['components_present']} of 4 missing)"
        )
    if credit_impulse is None:
        missing.append("credit_impulse (TSF + M2 both unavailable)")

    framework_label = (
        "PBOC reaction (7D OMO primary) + credit impulse + 4-comp dispersion"
        " + property overlay + CPI framing (central-tendency 2.0)"
    )

    native_verdict: dict[str, Any] = {
        "framework_label": framework_label,
        "growth_direction": growth_dir,
        "inflation_direction": inflation_dir,
        "ic_quadrant_legacy": ic_quadrant_legacy,
        "gip_regime": gip_regime,
        "pboc_stance": pboc_stance,
        "pboc_stance_ladder": calib.get("pboc_stance_ladder", []),
        "policy_rate_primary": policy_rate_primary,
        "policy_rate_quantitative_tools": policy_rate_quantitative,
        "structural_easing": structural_block or None,
        "fx_macroprudential": fx_macro_block or None,
        "cpi_framing": cpi_framing,
        "credit_impulse": credit_impulse,
        "4_component_dispersion": dispersion,
        "property_overlay": property_overlay,
        "policy_framework": calib.get(
            "inflation_target_framework", "multi_objective"),
        "policy_target_pct": calib.get("inflation_target", 2.0),
    }

    prov = calib.get("provenance", {}) or {}
    return CountryRegimeCard(
        country="cn",
        framework_used=framework_label,
        native_verdict=native_verdict,
        indicators_used=indicators_used,
        data_quality={
            "missing": missing,
            "stale": [],
        },
        confidence=confidence,
        provenance={
            "calibration_doc": prov.get("calibration_doc", "thresholds-china.md"),
            "calibration_vintage": prov.get("calibration_vintage", "2026-Q2"),
            "last_grounded": (
                prov.get("this_pr_partial_refresh")
                or prov.get("partial_refresh")
                or prov.get("last_full_grounding", "unknown")
            ),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
    )
