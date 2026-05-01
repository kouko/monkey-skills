#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
report-portfolio-review — pure formatting (Layer 3).

Reads:
    --portfolio <path>  JSON output of analysis-portfolio
                        ({positions, totals, _provenance})
    --regime <path>     (optional) JSON output of analysis-macro-regime
                        ({countries, cross_country_consensus, _provenance})

Renders Markdown to stdout — portfolio summary, position table, concentration
analysis, optional macro regime overlay, provenance footer.

NO network I/O. NO subprocess. NO compute beyond Markdown rendering and
display formatting (e.g., fractional ratios → percentage strings).

Ratio convention: analysis-portfolio emits fractional ratios (0.0–1.0).
Display as `pnl_ratio * 100` percentage with 2 decimals.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------- #
# i18n                                                                        #
# --------------------------------------------------------------------------- #

LANGS = ("en", "zh-TW", "ja")

LABELS: dict[str, dict[str, str]] = {
    "en": {
        "header": "Portfolio Review",
        "summary": "Summary",
        "total_cost": "Total Cost",
        "total_market_value": "Market Value",
        "total_pnl": "P&L",
        "position_count": "Positions",
        "positions": "Positions",
        "col_ticker": "Ticker",
        "col_quantity": "Qty",
        "col_cost_basis": "Cost",
        "col_current_price": "Price",
        "col_market_value": "Value",
        "col_pnl_abs": "P&L $",
        "col_pnl_pct": "P&L %",
        "col_weight": "Weight",
        "col_contribution": "Contrib",
        "concentration": "Concentration",
        "max_weight": "Largest position",
        "top3_weight": "Top-3 weight",
        "concentrated_flag": "⚠ Concentrated (>30%)",
        "regime_section": "Macro Regime Overlay",
        "regime_country": "Country",
        "regime_growth": "Growth",
        "regime_inflation": "Inflation",
        "regime_quadrant": "IC Phase",
        "regime_confidence": "Confidence",
        "regime_consensus": "Cross-country",
        "missing_prices": "Missing prices",
        "provenance": "Data Sources",
        "portfolio_source": "Portfolio compute",
        "regime_source": "Regime classifier",
        "computed_at": "Computed at",
    },
    "zh-TW": {
        "header": "投資組合回顧",
        "summary": "概要",
        "total_cost": "總成本",
        "total_market_value": "市值",
        "total_pnl": "損益",
        "position_count": "持倉數",
        "positions": "持倉明細",
        "col_ticker": "代號",
        "col_quantity": "股數",
        "col_cost_basis": "成本",
        "col_current_price": "現價",
        "col_market_value": "市值",
        "col_pnl_abs": "損益 $",
        "col_pnl_pct": "損益 %",
        "col_weight": "權重",
        "col_contribution": "貢獻",
        "concentration": "集中度",
        "max_weight": "最大持倉",
        "top3_weight": "前三大權重",
        "concentrated_flag": "⚠ 集中度警示 (>30%)",
        "regime_section": "總經 Regime Overlay",
        "regime_country": "國家",
        "regime_growth": "成長",
        "regime_inflation": "通膨",
        "regime_quadrant": "投資時鐘",
        "regime_confidence": "信心度",
        "regime_consensus": "跨國共識",
        "missing_prices": "缺價標的",
        "provenance": "資料來源",
        "portfolio_source": "持倉計算",
        "regime_source": "Regime 分類器",
        "computed_at": "計算時間",
    },
    "ja": {
        "header": "ポートフォリオレビュー",
        "summary": "サマリー",
        "total_cost": "総取得コスト",
        "total_market_value": "時価評価額",
        "total_pnl": "損益",
        "position_count": "保有銘柄数",
        "positions": "保有明細",
        "col_ticker": "銘柄",
        "col_quantity": "株数",
        "col_cost_basis": "取得単価",
        "col_current_price": "現在値",
        "col_market_value": "評価額",
        "col_pnl_abs": "損益額",
        "col_pnl_pct": "損益率",
        "col_weight": "比率",
        "col_contribution": "寄与",
        "concentration": "集中度",
        "max_weight": "最大ポジション",
        "top3_weight": "上位3銘柄比率",
        "concentrated_flag": "⚠ 集中度警告 (>30%)",
        "regime_section": "マクロレジーム",
        "regime_country": "国",
        "regime_growth": "成長",
        "regime_inflation": "インフレ",
        "regime_quadrant": "Investment Clock",
        "regime_confidence": "確信度",
        "regime_consensus": "クロスカントリー",
        "missing_prices": "価格欠落銘柄",
        "provenance": "データソース",
        "portfolio_source": "ポートフォリオ計算",
        "regime_source": "Regime 分類器",
        "computed_at": "計算時刻",
    },
}


def L(lang: str, key: str) -> str:
    return LABELS.get(lang, LABELS["en"]).get(key, key)


# --------------------------------------------------------------------------- #
# Format helpers                                                              #
# --------------------------------------------------------------------------- #


def fmt_money(x: float | None) -> str:
    if x is None:
        return "—"
    sign = "-" if x < 0 else ""
    ax = abs(x)
    return f"{sign}{ax:,.2f}"


def fmt_signed_money(x: float | None) -> str:
    if x is None:
        return "—"
    if x > 0:
        return f"+{x:,.2f}"
    if x < 0:
        return f"{x:,.2f}"
    return "0.00"


def fmt_pct(ratio: float | None) -> str:
    """Fractional ratio (0.2033) → '+20.33%'."""
    if ratio is None:
        return "—"
    pct = ratio * 100.0
    if pct > 0:
        return f"+{pct:.2f}%"
    if pct < 0:
        return f"{pct:.2f}%"
    return "0.00%"


def fmt_weight(ratio: float | None) -> str:
    """Non-signed percentage."""
    if ratio is None:
        return "—"
    return f"{ratio * 100:.2f}%"


def fmt_qty(x: float | None) -> str:
    if x is None:
        return "—"
    if float(x).is_integer():
        return f"{int(x):,}"
    return f"{x:,.4f}".rstrip("0").rstrip(".")


# --------------------------------------------------------------------------- #
# Renderers                                                                   #
# --------------------------------------------------------------------------- #


def render_summary(totals: dict[str, Any], lang: str) -> list[str]:
    lines = [f"## {L(lang, 'summary')}", ""]
    lines.append(
        f"- **{L(lang, 'total_cost')}**: {fmt_money(totals.get('total_cost'))}"
    )
    lines.append(
        f"- **{L(lang, 'total_market_value')}**: {fmt_money(totals.get('total_market_value'))}"
    )
    pnl_abs = totals.get("total_pnl_abs")
    pnl_ratio = totals.get("total_pnl_ratio")
    lines.append(
        f"- **{L(lang, 'total_pnl')}**: {fmt_signed_money(pnl_abs)} ({fmt_pct(pnl_ratio)})"
    )
    lines.append(
        f"- **{L(lang, 'position_count')}**: {totals.get('position_count', 0)}"
    )
    lines.append("")
    return lines


def render_positions_table(positions: list[dict[str, Any]], lang: str) -> list[str]:
    if not positions:
        return [f"## {L(lang, 'positions')}", "", "_(no positions)_", ""]
    lines = [f"## {L(lang, 'positions')}", ""]
    cols = [
        L(lang, "col_ticker"),
        L(lang, "col_quantity"),
        L(lang, "col_cost_basis"),
        L(lang, "col_current_price"),
        L(lang, "col_market_value"),
        L(lang, "col_pnl_abs"),
        L(lang, "col_pnl_pct"),
        L(lang, "col_weight"),
        L(lang, "col_contribution"),
    ]
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "|".join(["---"] * len(cols)) + "|")
    for p in positions:
        row = [
            str(p.get("ticker", "")),
            fmt_qty(p.get("quantity")),
            fmt_money(p.get("cost_basis")),
            fmt_money(p.get("current_price")),
            fmt_money(p.get("market_value")),
            fmt_signed_money(p.get("pnl_abs")),
            fmt_pct(p.get("pnl_ratio")),
            fmt_weight(p.get("weight")),
            fmt_pct(p.get("contribution")),
        ]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return lines


def render_concentration(
    positions: list[dict[str, Any]], totals: dict[str, Any], lang: str
) -> list[str]:
    lines = [f"## {L(lang, 'concentration')}", ""]
    max_w = totals.get("max_weight") or 0.0
    max_t = totals.get("max_weight_ticker") or "—"
    top3_sum = sum((p.get("weight") or 0.0) for p in positions[:3])
    flag = ""
    if max_w > 0.30:
        flag = f" {L(lang, 'concentrated_flag')}"
    lines.append(f"- **{L(lang, 'max_weight')}**: {max_t} {fmt_weight(max_w)}{flag}")
    lines.append(f"- **{L(lang, 'top3_weight')}**: {fmt_weight(top3_sum)}")
    lines.append("")
    return lines


REGIME_QUADRANT_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "1-recovery": "Phase 1 — Recovery",
        "2-overheat": "Phase 2 — Overheat",
        "3-stagflation": "Phase 3 — Stagflation",
        "4-reflation": "Phase 4 — Reflation",
    },
    "zh-TW": {
        "1-recovery": "階段一 — 復甦",
        "2-overheat": "階段二 — 過熱",
        "3-stagflation": "階段三 — 停滯",
        "4-reflation": "階段四 — 再通膨",
    },
    "ja": {
        "1-recovery": "局面1 — 回復",
        "2-overheat": "局面2 — 過熱",
        "3-stagflation": "局面3 — スタグフレーション",
        "4-reflation": "局面4 — リフレーション",
    },
}


def render_regime_section(regime: dict[str, Any], lang: str) -> list[str]:
    lines = [f"## {L(lang, 'regime_section')}", ""]
    countries = regime.get("countries") or {}
    if not countries:
        lines.append("_(no regime data)_")
        lines.append("")
        return lines
    cols = [
        L(lang, "regime_country"),
        L(lang, "regime_growth"),
        L(lang, "regime_inflation"),
        L(lang, "regime_quadrant"),
        L(lang, "regime_confidence"),
    ]
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "|".join(["---"] * len(cols)) + "|")
    quad_map = REGIME_QUADRANT_LABELS.get(lang, REGIME_QUADRANT_LABELS["en"])
    for code, c in countries.items():
        if not isinstance(c, dict):
            continue
        quad_key = c.get("ic_quadrant", "")
        quad_label = quad_map.get(quad_key, quad_key or "—")
        row = [
            code.upper(),
            c.get("growth_direction", "—"),
            c.get("inflation_direction", "—"),
            quad_label,
            c.get("confidence", "—"),
        ]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    consensus = regime.get("cross_country_consensus")
    if isinstance(consensus, dict):
        align = consensus.get("ic_alignment", "—")
        note = consensus.get("note", "")
        lines.append(f"**{L(lang, 'regime_consensus')}**: {align}")
        if note:
            lines.append(f"  - {note}")
        lines.append("")
    return lines


def render_provenance(
    portfolio: dict[str, Any], regime: dict[str, Any] | None, lang: str
) -> list[str]:
    lines = [f"## {L(lang, 'provenance')}", ""]
    pp = portfolio.get("_provenance") or {}
    lines.append(
        f"- **{L(lang, 'portfolio_source')}**: {pp.get('skill', 'analysis-portfolio')}"
        f" ({L(lang, 'computed_at')}: {pp.get('computed_at', '—')})"
    )
    missing = pp.get("missing_prices") or []
    if missing:
        lines.append(
            f"- **{L(lang, 'missing_prices')}**: {', '.join(missing)}"
        )
    if regime is not None:
        rp = regime.get("_provenance") or {}
        countries = rp.get("input_countries") or list((regime.get("countries") or {}).keys())
        lines.append(
            f"- **{L(lang, 'regime_source')}**: {rp.get('skill', 'analysis-macro-regime')}"
            f" ({L(lang, 'computed_at')}: {rp.get('computed_at', '—')};"
            f" {', '.join(countries) if countries else '—'})"
        )
    lines.append("")
    return lines


# --------------------------------------------------------------------------- #
# Main                                                                        #
# --------------------------------------------------------------------------- #


def render(
    portfolio: dict[str, Any],
    regime: dict[str, Any] | None,
    lang: str,
) -> str:
    positions = portfolio.get("positions") or []
    totals = portfolio.get("totals") or {}
    out: list[str] = [f"# {L(lang, 'header')}", ""]
    out += render_summary(totals, lang)
    out += render_positions_table(positions, lang)
    out += render_concentration(positions, totals, lang)
    if regime is not None:
        out += render_regime_section(regime, lang)
    out += render_provenance(portfolio, regime, lang)
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="report-portfolio-review — pure Markdown formatter (Layer 3)"
    )
    parser.add_argument(
        "--portfolio",
        required=True,
        help="Path to analysis-portfolio JSON output",
    )
    parser.add_argument(
        "--regime",
        required=False,
        default=None,
        help="(Optional) Path to analysis-macro-regime regime-card JSON",
    )
    parser.add_argument(
        "--lang",
        choices=LANGS,
        default="en",
        help="Output language (en / zh-TW / ja); default en",
    )
    args = parser.parse_args(argv)

    portfolio_path = Path(args.portfolio)
    if not portfolio_path.exists():
        print(f"error: portfolio file not found: {portfolio_path}", file=sys.stderr)
        return 2
    try:
        portfolio = json.loads(portfolio_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: portfolio JSON parse: {exc}", file=sys.stderr)
        return 1

    regime: dict[str, Any] | None = None
    if args.regime:
        regime_path = Path(args.regime)
        if not regime_path.exists():
            print(f"error: regime file not found: {regime_path}", file=sys.stderr)
            return 2
        try:
            regime = json.loads(regime_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"error: regime JSON parse: {exc}", file=sys.stderr)
            return 1

    sys.stdout.write(render(portfolio, regime, args.lang))
    return 0


if __name__ == "__main__":
    sys.exit(main())
