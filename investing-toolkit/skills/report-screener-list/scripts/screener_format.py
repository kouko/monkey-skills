#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
screener_format.py — report-screener-list pure formatter (v2.0.0)

Reads the JSON output of `analysis-screener/scripts/screener_compute.py`
and emits a Markdown top-N table report. Pure formatting — no network,
no scoring, no fetch. Layer 3 contract.

Usage:
  uv run screener_format.py --input /tmp/screener-ranked.json
  uv run screener_format.py --input /tmp/screener-ranked.json --lang ja
  uv run screener_format.py --input - --lang zh-TW   # stdin
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Localized labels
# ---------------------------------------------------------------------------

LABELS: dict[str, dict[str, str]] = {
    "en": {
        "title": "Stock Screener — Ranked Results",
        "preset": "Preset",
        "universe": "Universe",
        "passed": "Passed filters",
        "returned": "Top",
        "filters": "Filters applied",
        "weights": "Scoring weights",
        "rank": "Rank",
        "ticker": "Ticker",
        "score": "Score",
        "valuation": "Valuation",
        "momentum": "Momentum",
        "trend": "Trend",
        "quality": "Quality",
        "pe": "P/E",
        "pb": "P/B",
        "div": "Div %",
        "roe": "ROE",
        "rsi": "RSI",
        "sma200": "vs SMA200",
        "macd": "MACD",
        "price": "Price",
        "filtered_out": "Filtered Out",
        "filtered_count": "tickers excluded",
        "filtered_reason": "Reason",
        "no_passed": "No tickers passed the active filters.",
        "warnings_section": "Per-ticker warnings",
        "warnings_intro": "Some ranked tickers carry data-quality warnings:",
        "no_warnings": "No data-quality warnings.",
        "footer_data": (
            "Data via `data-{country}/pack.py --pack screener-batch` "
            "(yfinance lightweight info batch)."
        ),
        "footer_compute": (
            "Filtering / composite scoring / ranking via `analysis-screener` "
            "(pure compute, no I/O)."
        ),
        "footer_disclaimer": (
            "Composite score is **relative within the screened universe**, "
            "not absolute. Not investment advice."
        ),
        "footer_route": (
            "For deeper analysis route top candidates to "
            "`report-stock-snapshot` or `report-equity-memo`."
        ),
        "asof": "As of",
        "and_more": "and {n} more",
    },
    "zh-TW": {
        "title": "個股篩選 — 排名結果",
        "preset": "策略",
        "universe": "篩選池",
        "passed": "通過過濾",
        "returned": "前",
        "filters": "套用過濾條件",
        "weights": "評分權重",
        "rank": "排名",
        "ticker": "代號",
        "score": "分數",
        "valuation": "估值",
        "momentum": "動能",
        "trend": "趨勢",
        "quality": "品質",
        "pe": "本益比",
        "pb": "股價淨值比",
        "div": "殖利率",
        "roe": "ROE",
        "rsi": "RSI",
        "sma200": "vs SMA200",
        "macd": "MACD",
        "price": "股價",
        "filtered_out": "被排除個股",
        "filtered_count": "檔被排除",
        "filtered_reason": "原因",
        "no_passed": "沒有個股通過目前的過濾條件。",
        "warnings_section": "個別警示",
        "warnings_intro": "部分排名個股有資料品質警示：",
        "no_warnings": "無資料品質警示。",
        "footer_data": (
            "資料來源：`data-{country}/pack.py --pack screener-batch`"
            "（yfinance 精簡欄位批次擷取）。"
        ),
        "footer_compute": (
            "過濾／複合評分／排序由 `analysis-screener` 處理（純計算、無 I/O）。"
        ),
        "footer_disclaimer": (
            "複合評分為**篩選池內相對排名**，並非絕對指標。本表非投資建議。"
        ),
        "footer_route": (
            "如需深入分析，可將前段個股交給 `report-stock-snapshot` 或 "
            "`report-equity-memo`。"
        ),
        "asof": "更新時間",
        "and_more": "以及其他 {n} 檔",
    },
    "ja": {
        "title": "個別銘柄スクリーナー — ランキング結果",
        "preset": "プリセット",
        "universe": "対象銘柄数",
        "passed": "フィルタ通過",
        "returned": "トップ",
        "filters": "適用フィルタ",
        "weights": "スコアリング重み",
        "rank": "順位",
        "ticker": "ティッカー",
        "score": "スコア",
        "valuation": "バリュエーション",
        "momentum": "モメンタム",
        "trend": "トレンド",
        "quality": "クオリティ",
        "pe": "PER",
        "pb": "PBR",
        "div": "配当利回り",
        "roe": "ROE",
        "rsi": "RSI",
        "sma200": "vs SMA200",
        "macd": "MACD",
        "price": "株価",
        "filtered_out": "除外銘柄",
        "filtered_count": "銘柄が除外",
        "filtered_reason": "理由",
        "no_passed": "フィルタを通過した銘柄はありません。",
        "warnings_section": "銘柄ごとの警告",
        "warnings_intro": "ランキング内の一部銘柄にデータ品質の警告があります：",
        "no_warnings": "データ品質の警告はありません。",
        "footer_data": (
            "データ取得：`data-{country}/pack.py --pack screener-batch` "
            "（yfinance 軽量フィールドのバッチ取得）。"
        ),
        "footer_compute": (
            "フィルタリング・複合スコア・ランキングは `analysis-screener` "
            "（純計算、I/O なし）で実行。"
        ),
        "footer_disclaimer": (
            "複合スコアは**スクリーニング対象内の相対順位**であり、"
            "絶対指標ではありません。投資助言ではありません。"
        ),
        "footer_route": (
            "詳細分析が必要な場合は上位銘柄を `report-stock-snapshot` や "
            "`report-equity-memo` にルーティングしてください。"
        ),
        "asof": "更新日時",
        "and_more": "他 {n} 銘柄",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fmt_float(x, digits: int = 2, missing: str = "—") -> str:
    if x is None:
        return missing
    try:
        return f"{float(x):.{digits}f}"
    except (TypeError, ValueError):
        return str(x)


def _fmt_pct(x, digits: int = 2, missing: str = "—") -> str:
    """yfinance dividendYield is already a percentage value (e.g. 0.38 = 0.38%
    for AAPL). returnOnEquity is a decimal (e.g. 1.5 = 150%). The
    analysis-screener output preserves source units. Render the raw number with
    a `%` suffix for fields known to be percent-like."""
    if x is None:
        return missing
    try:
        return f"{float(x):.{digits}f}%"
    except (TypeError, ValueError):
        return str(x)


def _fmt_decimal_pct(x, digits: int = 1, missing: str = "—") -> str:
    """For decimal-fraction fields like ROE (0.25 = 25%)."""
    if x is None:
        return missing
    try:
        return f"{float(x) * 100:.{digits}f}%"
    except (TypeError, ValueError):
        return str(x)


def _fmt_sma_arrow(price_vs_sma200) -> str:
    if price_vs_sma200 is None:
        return "—"
    s = str(price_vs_sma200).lower()
    if s == "above":
        return "above ↑"
    if s == "below":
        return "below ↓"
    return s


def _trunc_reason(reason: str, max_len: int = 80) -> str:
    if reason is None:
        return "—"
    s = str(reason)
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def render_header(payload: dict, L: dict) -> list[str]:
    out: list[str] = []
    out.append(f"# {L['title']}")
    out.append("")
    preset = payload.get("preset_used") or "balanced"
    universe = payload.get("universe_size", 0)
    passed = payload.get("passed", 0)
    returned = payload.get("returned", 0)

    out.append(
        f"**{L['preset']}**: `{preset}` | "
        f"**{L['universe']}**: {universe} | "
        f"**{L['passed']}**: {passed} | "
        f"**{L['returned']} {returned}**"
    )
    out.append("")

    filters = payload.get("filters_applied") or {}
    if filters:
        parts = [f"`{k}={v}`" for k, v in filters.items()]
        out.append(f"**{L['filters']}**: {', '.join(parts)}")
    weights = payload.get("weights_applied") or {}
    if weights:
        wparts = [f"{k}={float(v):.2f}" for k, v in weights.items()]
        out.append(f"**{L['weights']}**: {', '.join(wparts)}")
    out.append("")
    return out


def render_ranked_table(payload: dict, L: dict) -> list[str]:
    ranked = payload.get("ranked") or []
    if not ranked:
        return [f"_{L['no_passed']}_", ""]

    # Header row — compact but informative.
    headers = [
        L["rank"], L["ticker"], L["score"],
        L["valuation"], L["momentum"], L["trend"], L["quality"],
        L["pe"], L["pb"], L["div"], L["rsi"],
        L["sma200"], L["macd"], L["price"],
    ]
    sep = ["---:" if h in (L["rank"],) else
           "---:" if h in (L["score"], L["pe"], L["pb"], L["div"],
                            L["rsi"], L["price"]) else
           "---" for h in headers]

    out: list[str] = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(sep) + " |")

    for r in ranked:
        rank = r.get("rank", "?")
        ticker = r.get("ticker", "?")
        score = r.get("composite_score")
        bd = r.get("breakdown") or {}
        m = r.get("metrics") or {}
        warn_marker = " ⚠️" if r.get("warnings") else ""

        row = [
            str(rank),
            f"`{ticker}`{warn_marker}",
            _fmt_float(score, 2),
            _fmt_float(bd.get("valuation"), 2),
            _fmt_float(bd.get("momentum"), 2),
            _fmt_float(bd.get("trend"), 2),
            _fmt_float(bd.get("quality"), 2),
            _fmt_float(m.get("trailingPE"), 2),
            _fmt_float(m.get("priceToBook"), 2),
            _fmt_pct(m.get("dividendYield"), 2),
            _fmt_float(m.get("rsi_14"), 1),
            _fmt_sma_arrow(m.get("price_vs_sma200")),
            str(m.get("macd_crossover") or "—"),
            _fmt_float(m.get("regularMarketPrice"), 2),
        ]
        out.append("| " + " | ".join(row) + " |")
    out.append("")
    return out


def render_filtered_out(payload: dict, L: dict) -> list[str]:
    filtered = payload.get("filtered_out") or []
    if not filtered:
        return []
    out: list[str] = []
    out.append(f"## {L['filtered_out']}")
    out.append(f"_{len(filtered)} {L['filtered_count']}_")
    out.append("")
    out.append(f"| {L['ticker']} | {L['filtered_reason']} |")
    out.append("| --- | --- |")
    for item in filtered[:3]:
        out.append(
            f"| `{item.get('ticker', '?')}` | "
            f"{_trunc_reason(item.get('reason'))} |"
        )
    if len(filtered) > 3:
        out.append(f"| … | _{L['and_more'].format(n=len(filtered) - 3)}_ |")
    out.append("")
    return out


def render_warnings(payload: dict, L: dict) -> list[str]:
    """Collapsed Markdown <details> block listing per-ticker warnings."""
    ranked = payload.get("ranked") or []
    with_warnings = [
        (r.get("ticker"), r.get("warnings") or [])
        for r in ranked
        if r.get("warnings")
    ]
    out: list[str] = []
    out.append(f"## {L['warnings_section']}")
    if not with_warnings:
        out.append(f"_{L['no_warnings']}_")
        out.append("")
        return out

    out.append("<details>")
    out.append(f"<summary>{L['warnings_intro']}</summary>")
    out.append("")
    for ticker, warns in with_warnings:
        for w in warns:
            out.append(f"- `{ticker}` — {w}")
    out.append("")
    out.append("</details>")
    out.append("")
    return out


def render_footer(payload: dict, L: dict) -> list[str]:
    prov = payload.get("_provenance") or {}
    asof = prov.get("computed_at") or datetime.now(tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    out: list[str] = []
    out.append("---")
    out.append("")
    out.append(f"_{L['footer_data']}_")
    out.append("")
    out.append(f"_{L['footer_compute']}_")
    out.append("")
    out.append(f"_{L['footer_disclaimer']}_")
    out.append("")
    out.append(f"_{L['footer_route']}_")
    out.append("")
    out.append(f"_{L['asof']}: {asof}_")
    return out


def render(payload: dict, lang: str) -> str:
    L = LABELS.get(lang) or LABELS["en"]
    sections: list[str] = []
    sections += render_header(payload, L)
    sections += render_ranked_table(payload, L)
    sections += render_filtered_out(payload, L)
    sections += render_warnings(payload, L)
    sections += render_footer(payload, L)
    return "\n".join(sections) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _load(path: str) -> dict:
    if path == "-":
        text = sys.stdin.read()
    else:
        text = Path(path).read_text()
    return json.loads(text)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="report-screener-list Markdown formatter (v2.0.0, pure)",
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to ranked JSON (analysis-screener output) or '-' for stdin.",
    )
    parser.add_argument(
        "--lang", default="en",
        choices=sorted(LABELS.keys()),
        help="Output language (en / zh-TW / ja). Default: en.",
    )
    args = parser.parse_args()

    try:
        payload = _load(args.input)
    except Exception as e:
        print(f"<!-- error: failed to read --input: {e} -->", file=sys.stderr)
        return 1

    if "error" in payload and "ranked" not in payload:
        print(
            f"<!-- upstream error in analysis-screener output: "
            f"{payload['error']} -->",
            file=sys.stderr,
        )
        return 1

    sys.stdout.write(render(payload, args.lang))
    return 0


if __name__ == "__main__":
    sys.exit(main())
