#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Pure-compute 3-stage DCF (Damodaran 2012, Investment Valuation Ch.12).

This script is Layer 2 (Analysis) under the v2.0.0 three-layer design:
- NO I/O: it does NOT fetch data from any network/file source other than
  the single --input JSON path supplied by the caller.
- Caller (data-{country}/pack.py --pack memo-fetch) is responsible for
  pre-fetching SEC EDGAR XBRL facts (US) or MOPS rows (TW) and shaping
  them into the input contract documented below.

Output: intrinsic value JSON with 3-case range, 3x3 WACC x g sensitivity
table, full assumptions echo, and provenance.

Input JSON contract (minimum required fields)
---------------------------------------------
{
  "ticker": "AAPL",
  "income_statement": {
    "revenue": [r_t0, r_t-1, r_t-2, ...],         # most-recent-first, $M
    "net_income": [...],                          # optional, used for margin fallback
    "ebit": [...]                                 # optional, preferred over net_income
  },
  "cash_flow": {
    "fcf": [fcf_t0, fcf_t-1, ...],                # optional; preferred for FCF base
    "capex": [...],                               # optional
    "operating_cash_flow": [...]                  # optional
  },
  "balance_sheet": {
    "total_debt": [td_t0, ...],
    "cash": [cash_t0, ...]
  },
  "shares_outstanding": 15_728_000_000,           # absolute count, not millions
  "current_price": 175.0                          # optional; for verdict thresholds
}

The script tolerates the data-us pack.py memo-fetch shape (sec_edgar XBRL
facts pre-shaped into income_statement/cash_flow/balance_sheet arrays) and
also tolerates the data-tw mops shape with the same outer keys.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_get_series(d: dict, key: str) -> list[float]:
    """Return a list of floats for d[key], or [] if missing/empty/non-numeric."""
    v = d.get(key)
    if not isinstance(v, list) or not v:
        return []
    out: list[float] = []
    for x in v:
        try:
            out.append(float(x))
        except (TypeError, ValueError):
            continue
    return out


def _cagr(series_recent_first: list[float]) -> float | None:
    """CAGR from oldest to most recent. Series is most-recent-first."""
    s = [x for x in series_recent_first if x and x > 0]
    if len(s) < 2:
        return None
    most_recent = s[0]
    oldest = s[-1]
    n = len(s) - 1
    if oldest <= 0:
        return None
    return (most_recent / oldest) ** (1.0 / n) - 1.0


def _project_revenue(base: float, growth_yr_1_5: float, growth_yr_6_10: float) -> list[float]:
    revs = []
    cur = base
    for _ in range(5):
        cur *= (1.0 + growth_yr_1_5)
        revs.append(cur)
    for _ in range(5):
        cur *= (1.0 + growth_yr_6_10)
        revs.append(cur)
    return revs  # length 10, year 1..10


def _intrinsic_per_share(
    base_revenue: float,
    growth_1_5: float,
    growth_6_10: float,
    ebit_margin: float,
    tax_rate: float,
    reinvestment_rate: float,
    wacc: float,
    terminal_g: float,
    net_debt: float,
    shares_outstanding: float,
) -> dict[str, Any]:
    """Single-scenario DCF. Returns equity value + per-share intrinsic."""
    if wacc <= terminal_g:
        # Degenerate; clamp to avoid div-by-zero. Caller can detect via _warning.
        wacc = terminal_g + 0.0025

    revs = _project_revenue(base_revenue, growth_1_5, growth_6_10)
    pv_fcf_sum = 0.0
    fcf_year10 = 0.0
    fcf_series = []
    for t, rev in enumerate(revs, start=1):
        ebit = rev * ebit_margin
        fcf = ebit * (1.0 - tax_rate) * (1.0 - reinvestment_rate)
        pv = fcf / ((1.0 + wacc) ** t)
        pv_fcf_sum += pv
        fcf_series.append(fcf)
        if t == 10:
            fcf_year10 = fcf

    tv = fcf_year10 * (1.0 + terminal_g) / (wacc - terminal_g)
    pv_tv = tv / ((1.0 + wacc) ** 10)

    equity_value = pv_fcf_sum + pv_tv - net_debt  # in $M (revenue input is $M)
    # Unit-normalisation: revenue / FCF / debt / cash inputs are in $M (the
    # SEC EDGAR XBRL + MOPS pack convention). Shares outstanding is absolute
    # count (yfinance / EDGAR convention). To get $/share, convert equity
    # from $M to $ before dividing.
    if shares_outstanding > 0:
        # Heuristic: if shares < 1e7, caller passed shares in millions (older
        # interactive convention); else absolute count.
        if shares_outstanding < 1e7:
            per_share = equity_value / shares_outstanding  # $M / Mshares = $/share
        else:
            per_share = (equity_value * 1_000_000) / shares_outstanding  # $ / shares
    else:
        per_share = 0.0

    return {
        "equity_value": equity_value,
        "per_share": per_share,
        "pv_fcf_sum": pv_fcf_sum,
        "pv_tv": pv_tv,
        "fcf_year10": fcf_year10,
        "fcf_projection": fcf_series,
    }


# ---------------------------------------------------------------------------
# Assumption derivation
# ---------------------------------------------------------------------------

def _derive_assumptions(data: dict, args: argparse.Namespace) -> dict[str, Any]:
    """Derive base-case DCF assumptions from input JSON + CLI overrides."""
    inc = data.get("income_statement") or {}
    cf = data.get("cash_flow") or {}
    bs = data.get("balance_sheet") or {}

    revenue = _safe_get_series(inc, "revenue")
    net_income = _safe_get_series(inc, "net_income")
    ebit_series = _safe_get_series(inc, "ebit")
    fcf_series = _safe_get_series(cf, "fcf")

    if not revenue:
        raise ValueError("input JSON missing income_statement.revenue or it is empty")

    base_revenue = revenue[0]

    # Growth — historical CAGR clamped to a sane band.
    historical_cagr = _cagr(revenue)
    if historical_cagr is None:
        historical_cagr = 0.05  # neutral fallback
    historical_cagr = max(min(historical_cagr, 0.25), -0.05)

    growth_1_5 = args.growth_1_5 if args.growth_1_5 is not None else historical_cagr
    growth_6_10 = (
        args.growth_6_10
        if args.growth_6_10 is not None
        else max(growth_1_5 * 0.5, 0.025)  # transition: half of stage-1, floor at 2.5%
    )

    # EBIT margin — prefer reported EBIT/revenue, fallback to NI/revenue.
    if ebit_series and revenue and revenue[0] > 0:
        margin = ebit_series[0] / revenue[0]
    elif net_income and revenue and revenue[0] > 0:
        margin = net_income[0] / revenue[0]
    else:
        margin = 0.15
    margin = max(min(margin, 0.50), 0.02)
    ebit_margin = args.ebit_margin if args.ebit_margin is not None else margin

    tax_rate = args.tax_rate if args.tax_rate is not None else 0.21  # US fed default

    # Reinvestment rate: derive from FCF vs EBIT(1-t) if available; else default.
    reinvestment = None
    if fcf_series and revenue and revenue[0] > 0:
        ebit0 = (ebit_series[0] if ebit_series else net_income[0] if net_income else revenue[0] * ebit_margin)
        ebit_after_tax = ebit0 * (1.0 - tax_rate)
        if ebit_after_tax > 0:
            reinvestment = max(min(1.0 - (fcf_series[0] / ebit_after_tax), 0.80), 0.0)
    if reinvestment is None:
        reinvestment = 0.30
    reinvestment_rate = (
        args.reinvestment_rate if args.reinvestment_rate is not None else reinvestment
    )

    wacc = args.wacc if args.wacc is not None else 0.085  # ~Damodaran US large-cap default
    terminal_g = args.terminal_g if args.terminal_g is not None else 0.025

    total_debt = (_safe_get_series(bs, "total_debt") or [0.0])[0]
    cash = (_safe_get_series(bs, "cash") or [0.0])[0]
    net_debt = total_debt - cash

    shares = float(data.get("shares_outstanding") or 0)
    if shares <= 0:
        raise ValueError("input JSON missing shares_outstanding (must be > 0)")

    return {
        "base_revenue": base_revenue,
        "historical_revenue_cagr": historical_cagr,
        "growth_1_5": growth_1_5,
        "growth_6_10": growth_6_10,
        "ebit_margin": ebit_margin,
        "tax_rate": tax_rate,
        "reinvestment_rate": reinvestment_rate,
        "wacc": wacc,
        "terminal_g": terminal_g,
        "net_debt": net_debt,
        "shares_outstanding": shares,
    }


# ---------------------------------------------------------------------------
# Sensitivity (3x3 WACC × terminal-g)
# ---------------------------------------------------------------------------

def _sensitivity_grid(a: dict[str, Any], wacc_step: float, g_step: float) -> dict[str, Any]:
    waccs = [a["wacc"] - wacc_step, a["wacc"], a["wacc"] + wacc_step]
    gs = [a["terminal_g"] - g_step, a["terminal_g"], a["terminal_g"] + g_step]
    grid: list[list[float]] = []
    for w in waccs:
        row: list[float] = []
        for g in gs:
            res = _intrinsic_per_share(
                base_revenue=a["base_revenue"],
                growth_1_5=a["growth_1_5"],
                growth_6_10=a["growth_6_10"],
                ebit_margin=a["ebit_margin"],
                tax_rate=a["tax_rate"],
                reinvestment_rate=a["reinvestment_rate"],
                wacc=w,
                terminal_g=g,
                net_debt=a["net_debt"],
                shares_outstanding=a["shares_outstanding"],
            )
            row.append(round(res["per_share"], 2))
        grid.append(row)
    return {
        "wacc_axis": [round(w, 4) for w in waccs],
        "terminal_g_axis": [round(g, 4) for g in gs],
        "table": grid,  # [wacc_idx][g_idx]
    }


# ---------------------------------------------------------------------------
# Verdict thresholds
# ---------------------------------------------------------------------------

def _verdict_thresholds(intrinsic_mid: float) -> dict[str, Any]:
    return {
        "buy_threshold_grade_a": round(intrinsic_mid * (1.0 - 0.30), 2),
        "buy_threshold_grade_b": round(intrinsic_mid * (1.0 - 0.40), 2),
        "buy_threshold_grade_c": round(intrinsic_mid * (1.0 - 0.50), 2),
        "hold_threshold": round(intrinsic_mid * 1.15, 2),
        "sell_threshold": round(intrinsic_mid * 1.15, 2),
        "rule": (
            "BUY if price <= intrinsic * (1 - MoS); HOLD if price <= intrinsic * 1.15; "
            "SELL if price > intrinsic * 1.15. Conviction grade set by analyst."
        ),
    }


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------

def _validate(a: dict[str, Any]) -> list[str]:
    warns: list[str] = []
    if a["terminal_g"] >= a["wacc"]:
        warns.append("terminal_g >= wacc — degenerate; clamped to wacc - 0.0025 internally")
    if a["terminal_g"] > 0.04:
        warns.append("terminal_g > 4% — likely double-counting inflation; verify ≤ risk-free rate")
    if a["growth_1_5"] > 0.20:
        warns.append("growth_1_5 > 20% — verify ROIC × reinvestment supports this")
    if a["reinvestment_rate"] < 0.05 and a["growth_1_5"] > 0.10:
        warns.append("low reinvestment with high growth — implies high ROIC; verify capital-light claim")
    return warns


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(
        description=(
            "Pure-compute 3-stage DCF on pre-fetched JSON (Layer 2 of v2.0.0 "
            "three-layer architecture). NO network I/O; --input must be the path "
            "to a JSON produced by data-{country}/pack.py --pack memo-fetch."
        )
    )
    p.add_argument("--input", required=True, help="Path to pre-fetched JSON")
    # Optional override sliders
    p.add_argument("--wacc", type=float, default=None)
    p.add_argument("--wacc-low", dest="wacc_low", type=float, default=None,
                   help="Sensitivity low-side WACC (default: base - wacc-step)")
    p.add_argument("--wacc-high", dest="wacc_high", type=float, default=None,
                   help="Sensitivity high-side WACC (default: base + wacc-step)")
    p.add_argument("--wacc-step", dest="wacc_step", type=float, default=0.01,
                   help="WACC sensitivity step (default 1pp)")
    p.add_argument("--terminal-g", dest="terminal_g", type=float, default=None)
    p.add_argument("--terminal-g-low", dest="terminal_g_low", type=float, default=None)
    p.add_argument("--terminal-g-high", dest="terminal_g_high", type=float, default=None)
    p.add_argument("--g-step", dest="g_step", type=float, default=0.005,
                   help="Terminal-g sensitivity step (default 0.5pp)")
    p.add_argument("--growth-1-5", dest="growth_1_5", type=float, default=None)
    p.add_argument("--growth-6-10", dest="growth_6_10", type=float, default=None)
    p.add_argument("--ebit-margin", dest="ebit_margin", type=float, default=None)
    p.add_argument("--tax-rate", dest="tax_rate", type=float, default=None)
    p.add_argument("--reinvestment-rate", dest="reinvestment_rate", type=float, default=None)

    args = p.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(json.dumps({"error": f"input file not found: {input_path}"}), file=sys.stderr)
        return 2
    try:
        data = json.loads(input_path.read_text())
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"input not valid JSON: {e}"}), file=sys.stderr)
        return 2

    try:
        a = _derive_assumptions(data, args)
    except ValueError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 2

    base = _intrinsic_per_share(
        base_revenue=a["base_revenue"],
        growth_1_5=a["growth_1_5"],
        growth_6_10=a["growth_6_10"],
        ebit_margin=a["ebit_margin"],
        tax_rate=a["tax_rate"],
        reinvestment_rate=a["reinvestment_rate"],
        wacc=a["wacc"],
        terminal_g=a["terminal_g"],
        net_debt=a["net_debt"],
        shares_outstanding=a["shares_outstanding"],
    )

    sens = _sensitivity_grid(a, args.wacc_step, args.g_step)

    # Bear / mid / bull from corners of the grid (highest WACC + lowest g = bear)
    bear = sens["table"][2][0]
    mid = sens["table"][1][1]
    bull = sens["table"][0][2]

    current_price = data.get("current_price")
    margin_of_safety = None
    if isinstance(current_price, (int, float)) and mid > 0:
        margin_of_safety = round((mid - current_price) / mid, 4)

    out = {
        "ticker": data.get("ticker"),
        "intrinsic_value": {
            "low": bear,    # bear (high WACC, low g)
            "mid": mid,     # base
            "high": bull,   # bull (low WACC, high g)
        },
        "sensitivity_table": sens,
        "verdict_thresholds": _verdict_thresholds(mid),
        "current_price": current_price,
        "margin_of_safety_base": margin_of_safety,
        "assumptions": {
            "base_revenue": a["base_revenue"],
            "historical_revenue_cagr": round(a["historical_revenue_cagr"], 4),
            "growth_1_5": round(a["growth_1_5"], 4),
            "growth_6_10": round(a["growth_6_10"], 4),
            "ebit_margin": round(a["ebit_margin"], 4),
            "tax_rate": round(a["tax_rate"], 4),
            "reinvestment_rate": round(a["reinvestment_rate"], 4),
            "wacc": round(a["wacc"], 4),
            "terminal_g": round(a["terminal_g"], 4),
            "net_debt": round(a["net_debt"], 2),
            "shares_outstanding": a["shares_outstanding"],
        },
        "warnings": _validate(a),
        "_provenance": {
            "input_path": str(input_path),
            "computed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "framework": "Damodaran 2012 Investment Valuation Ch.12 (3-stage DCF)",
            "layer": "analysis (pure compute, no I/O)",
        },
    }

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
