#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
regime_compose.py — analysis-macro-regime classifier (Layer 2, pure compute)

Classifies each provided country into an Investment Clock (IC) phase +
Hedgeye GIP quadrant from pre-fetched macro indicator JSONs. NO I/O —
all data is read from the input files, never fetched.

Usage:
  uv run regime_compose.py \\
    --input us=/tmp/us-regime.json,jp=/tmp/jp-regime.json

  Each country=path pair points to a regime-pack JSON emitted by
  `data-{country}/pack.py --pack regime-pack`. Country codes:
  us / jp / tw / kr / cn. Any subset is allowed (1-5 countries).

Input JSON shape (per country):
  {
    "country": "us",
    "series": {
      "GDPC1":    [..., 2.4, 2.5],   // growth proxy (latest last)
      "CPIAUCSL": [..., 3.0, 2.8],   // inflation proxy
      "DGS10":    [..., 4.3, 4.2],   // nominal 10Y (US/JP)
      "T10YIE":   [..., 2.3, 2.2]    // breakeven (US — for real rate)
    },
    "_provenance": { ... }
  }

Output JSON: regime card with per-country IC phase + GIP quad +
US real-rate decomposition + cross-country consensus block.

Pure compute — imports only stdlib (argparse / json / sys / statistics /
datetime). No network clients of any kind.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from typing import Any

# Country-specific series resolvers — multiple naming conventions tolerated
GROWTH_KEYS: dict[str, list[str]] = {
    "us": ["nowcast.CFNAI", "CFNAI", "WEI", "GDPC1", "growth.gdp", "gdp"],
    "jp": ["coincident-index", "growth.coincident-index", "ci", "gdp"],
    "tw": ["cycle.signal", "signal", "ndc-signal", "gdp"],
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

# CN component overlay — flagged if components disagree > 2%
CN_COMPONENT_KEYS = [
    "industrial-yoy",
    "retail-yoy",
    "fai-yoy",
    "services-production-yoy",
]

# Direction thresholds (fraction of stdev)
DIRECTION_BAND_STDEV = 0.5
# Minimum absolute band for normalised indices (CFNAI, K253 cycle)
NORMALISED_BAND = 0.1
# CN component disagreement threshold (percentage points)
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
    """
    Compare latest reading to prior 3-month average.
    Returns 'rising' / 'falling' / 'flat'.
    """
    if values is None or len(values) < 2:
        return "flat"
    latest = values[-1]
    prior = values[-4:-1] if len(values) >= 4 else values[:-1]
    if not prior:
        return "flat"
    prior_avg = statistics.fmean(prior)
    delta = latest - prior_avg

    # Determine band — half a stdev, or NORMALISED_BAND for normalised indices
    if len(values) >= 4:
        try:
            stdev = statistics.stdev(values[-12:] if len(values) >= 12 else values)
        except statistics.StatisticsError:
            stdev = 0.0
    else:
        stdev = 0.0

    band = max(NORMALISED_BAND, DIRECTION_BAND_STDEV * stdev) if normalised else DIRECTION_BAND_STDEV * stdev
    if band == 0.0:
        # Fallback when stdev is zero — use small absolute band
        band = NORMALISED_BAND if normalised else 0.05

    if delta > band:
        return "rising"
    elif delta < -band:
        return "falling"
    return "flat"


def map_ic_quadrant(growth: str, inflation: str) -> str:
    """
    IC 2x2:
                  Inflation Rising    Inflation Falling
    Growth Rising     Phase 2 Overheat       Phase 1 Recovery
    Growth Falling    Phase 3 Stagflation    Phase 4 Reflation

    'flat' handling (regime/policy-context convention):
      - flat growth    → treated as **rising-side** (Recovery/Overheat).
        Rationale: in policy regime context, "flat growth" is the
        neutral state on the expansion side — informs forward-looking
        allocation toward Phase 1/2 rather than Phase 3/4.
      - flat inflation → treated as **falling-side** (Recovery/Reflation).
        Rationale: flat inflation in a 2% target regime leans toward
        the disinflation interpretation rather than overheating.
    These are tagged in `notes` upstream so memo readers see the lean.
    """
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
    """v2.0.0 mapping: Hedgeye Quad N == IC Phase N (simple direction-based)."""
    return {
        "1-recovery": "quad1",
        "2-overheat": "quad2",
        "3-stagflation": "quad3",
        "4-reflation": "quad4",
    }.get(ic_quadrant, "quad4")


def compute_us_real_rate(series: dict[str, Any]) -> dict[str, Any] | None:
    """US real-rate decomposition: nominal − breakeven = real (Fisher)."""
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

    # Identity check (only if TIPS provided)
    identity_check = None
    if tips:
        residual_bp = abs((nominal_10y - breakeven_10y - tips[-1]) * 100)
        identity_check = {
            "residual_bp": round(residual_bp, 2),
            "ok": residual_bp <= 5.0,
        }

    # Four-tier signal threshold (applied to real_10y)
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
        # Try plain key and group-prefixed
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


def classify_country(country: str, regime_pack: dict[str, Any]) -> dict[str, Any]:
    """Classify one country's regime from its regime-pack JSON."""
    series = regime_pack.get("series", {})
    notes: list[str] = []

    growth_values = resolve_series(series, GROWTH_KEYS.get(country, []))
    inflation_values = resolve_series(series, INFLATION_KEYS.get(country, []))

    if growth_values is None:
        notes.append(f"growth proxy missing for {country}; defaulted to flat")
    if inflation_values is None:
        notes.append(f"inflation proxy missing for {country}; defaulted to flat")

    growth_dir = classify_direction(growth_values or [], normalised=normalised_country(country))
    inflation_dir = classify_direction(inflation_values or [], normalised=False)

    # Country-specific structural notes
    if country == "jp" and inflation_values is not None and inflation_values[-1] < 2.0:
        notes.append("JP: inflation below BOJ 2% target — IC applied to direction, not level")
    if country == "tw" and growth_values is not None:
        score = growth_values[-1]
        # NDC 景氣對策信號綜合分數: 9 indicators × 1-5 points each → 9-45 composite
        # (藍燈 9-16 / 黃藍燈 17-22 / 綠燈 23-31 / 黃紅燈 32-37 / 紅燈 38-45)
        if 9 <= score <= 45:
            notes.append(f"TW: NDC 五色景氣燈號 score={score} (9-45 composite scale)")
    if country == "cn":
        overlay = cn_component_overlay(series)
        if overlay and overlay["disagreement_flag"]:
            notes.append(
                f"CN: 4-component spread {overlay['spread_pp']}pp > 2pp — components disagree"
            )

    ic_quadrant = map_ic_quadrant(growth_dir, inflation_dir)
    gip_regime = map_gip_quad(ic_quadrant)

    real_rates: dict[str, Any] | None = None
    if country == "us":
        real_rates = compute_us_real_rate(series)
        if real_rates is None:
            notes.append("US real-rate block: missing DGS10 or T10YIE in regime-pack")

    # Confidence heuristic: high if both proxies present + ≥ 4 readings,
    # medium if both present with < 4 readings, low otherwise.
    has_g = growth_values is not None and len(growth_values) >= 4
    has_i = inflation_values is not None and len(inflation_values) >= 4
    if has_g and has_i:
        confidence = "high"
    elif growth_values is not None and inflation_values is not None:
        confidence = "medium"
    else:
        confidence = "low"

    out = {
        "growth_direction": growth_dir,
        "inflation_direction": inflation_dir,
        "ic_quadrant": ic_quadrant,
        "gip_regime": gip_regime,
        "real_rates": real_rates,
        "confidence": confidence,
        "notes": notes,
    }
    return out


def cross_country_consensus(per_country: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Summarise IC alignment across countries."""
    quadrants = [c["ic_quadrant"] for c in per_country.values()]
    unique = sorted(set(quadrants))
    aligned = len(unique) == 1
    note_parts = []
    for cc, body in per_country.items():
        note_parts.append(f"{cc.upper()} {body['ic_quadrant']}")
    return {
        "ic_alignment": "aligned" if aligned else "divergent",
        "regimes_present": unique,
        "note": " / ".join(note_parts),
    }


def parse_input_arg(arg: str) -> dict[str, str]:
    """Parse 'us=/tmp/a.json,jp=/tmp/b.json' into {'us': '/tmp/a.json', ...}."""
    out: dict[str, str] = {}
    for chunk in arg.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise SystemExit(f"Bad --input fragment '{chunk}' — expected country=path")
        cc, path = chunk.split("=", 1)
        cc = cc.strip().lower()
        path = path.strip()
        if cc not in {"us", "jp", "tw", "kr", "cn"}:
            raise SystemExit(f"Unknown country '{cc}' — expected us/jp/tw/kr/cn")
        out[cc] = path
    if not out:
        raise SystemExit("--input is empty")
    return out


def load_pack(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="analysis-macro-regime classifier (pure compute, no I/O)",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Comma-separated country=path pairs, e.g. us=/tmp/us.json,jp=/tmp/jp.json",
    )
    args = parser.parse_args()

    inputs = parse_input_arg(args.input)
    countries: dict[str, dict[str, Any]] = {}
    for cc, path in inputs.items():
        try:
            pack = load_pack(path)
        except (OSError, json.JSONDecodeError) as e:
            print(f"ERROR loading {cc}={path}: {e}", file=sys.stderr)
            return 2
        countries[cc] = classify_country(cc, pack)

    out: dict[str, Any] = {
        "schema_version": "1.0",
        "countries": countries,
        "_provenance": {
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "input_countries": sorted(inputs.keys()),
            "skill": "analysis-macro-regime",
        },
    }

    if len(countries) > 1:
        out["cross_country_consensus"] = cross_country_consensus(countries)

    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
