#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""snapshot_format.py — Pure formatter for report-stock-snapshot.

Reads a snapshot pack JSON (output of any data-{us|jp|tw|kr|cn}/scripts/pack.py
--pack snapshot) and renders a single-page Markdown card to stdout.

PURE FUNCTION — no HTTP, no subprocess, no env access. Input is the pre-fetched
JSON path; output goes to stdout.

The 5 country pack shapes differ:
  - data-us:  { pack, ticker, fetched_at, company_info, price_history }
  - data-jp:  { pack, ticker, yf_ticker, fetched_at, info, price_history,
                timely_disclosures, _provenance }
  - data-tw:  { _pack, _ticker, _normalized, yfinance{info,history},
                mops{company_basic,balance_sheet,income_statement},
                twse{daily_price,pe_pb_yield,margin_balance},
                finmind{three_investor_flow}, _partial }
  - data-kr:  { pack, country, ticker, info, history, _provenance }
  - data-cn:  { pack, ticker, country, yfinance_info, yfinance_history }

The formatter detects the shape via the `pack`/`_pack` key + characteristic
sub-keys, normalizes into a unified Card model, then renders.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any


# --------------------------------------------------------------------------- #
# Unified card model
# --------------------------------------------------------------------------- #


@dataclass
class Card:
    ticker: str = "?"
    country: str = "?"
    name: str = "N/A"
    exchange: str = "N/A"
    sector: str = "N/A"
    currency: str = ""
    close: Any = None
    fifty_two_w_low: Any = None
    fifty_two_w_high: Any = None
    pe: Any = None
    forward_pe: Any = None
    pb: Any = None
    market_cap: Any = None
    enterprise_value: Any = None
    beta: Any = None
    div_yield: Any = None  # raw fraction (0.025 == 2.5%)
    one_year_return: Any = None  # percent
    fetched_at: str = ""
    disclosures: list[dict[str, Any]] = field(default_factory=list)  # country-specific list
    disclosures_kind: str = ""  # "sec" | "tdnet" | "mops" | ""
    tier_footer: str = ""
    warnings: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Utilities
# --------------------------------------------------------------------------- #


def _fmt_num(v: Any, digits: int = 2) -> str:
    """Format a number with thousands separator, fall back to N/A."""
    if v is None or v == "":
        return "N/A"
    try:
        f = float(v)
        if f == 0:
            return f"{0:.{digits}f}"
        if abs(f) >= 1000:
            return f"{f:,.{digits}f}"
        return f"{f:.{digits}f}"
    except (TypeError, ValueError):
        return str(v) if v else "N/A"


def _fmt_pct(v: Any, digits: int = 2, *, already_pct: bool = False) -> str:
    """Format as percent. `v` may be a fraction (0.025) or already-percent (2.5)."""
    if v is None or v == "":
        return "N/A"
    try:
        f = float(v)
        if not already_pct:
            f *= 100
        return f"{f:.{digits}f}%"
    except (TypeError, ValueError):
        return "N/A"


def _fmt_billions(v: Any, currency: str = "") -> str:
    if v is None or v == "":
        return "N/A"
    try:
        f = float(v)
        return f"{currency}{f / 1e9:,.2f}B"
    except (TypeError, ValueError):
        return "N/A"


def _safe(d: Any, *keys: str, default: Any = None) -> Any:
    """Walk nested dict with default fallback."""
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def _vs_52w_high_pct(close: Any, high: Any) -> str:
    if close in (None, "") or high in (None, ""):
        return "N/A"
    try:
        c = float(close)
        h = float(high)
        if h == 0:
            return "N/A"
        return f"{(c - h) / h * 100:+.2f}%"
    except (TypeError, ValueError):
        return "N/A"


def _compute_1y_return(history: dict[str, Any]) -> Any:
    """Best-effort 1Y return from a history payload — return percent or None."""
    if not isinstance(history, dict):
        return None
    # data-jp / data-us / data-kr / data-cn yfinance_client history shape may carry
    # a "rows" / "data" list of OHLCV dicts. Try a couple of shapes.
    rows = history.get("rows") or history.get("data")
    if isinstance(history.get("history"), list):
        rows = history["history"]
    if not rows or not isinstance(rows, list):
        return None
    try:
        first = rows[0]
        last = rows[-1]
        # field names vary: "Close" / "close" / "adjclose"
        def _close(r: dict) -> Any:
            for k in ("Close", "close", "adjclose", "Adj Close"):
                if k in r:
                    return r[k]
            return None
        c0 = _close(first) if isinstance(first, dict) else None
        c1 = _close(last) if isinstance(last, dict) else None
        if c0 in (None, 0) or c1 in (None,):
            return None
        return (float(c1) - float(c0)) / float(c0) * 100
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Per-country adapters
# --------------------------------------------------------------------------- #


def _adapt_us(pack: dict[str, Any]) -> Card:
    info = pack.get("company_info") or {}
    history = pack.get("price_history") or {}
    card = Card(
        ticker=pack.get("ticker", "?"),
        country="US",
        fetched_at=pack.get("fetched_at", ""),
        currency="$",
    )
    card.name = info.get("longName") or info.get("shortName") or "N/A"
    card.exchange = info.get("exchange") or info.get("fullExchangeName") or "NYSE/NASDAQ"
    card.sector = info.get("sector") or "N/A"
    card.close = info.get("regularMarketPrice") or info.get("currentPrice") \
        or _safe(history, "latest_close")
    card.fifty_two_w_low = info.get("fiftyTwoWeekLow")
    card.fifty_two_w_high = info.get("fiftyTwoWeekHigh")
    card.pe = info.get("trailingPE")
    card.forward_pe = info.get("forwardPE")
    card.pb = info.get("priceToBook")
    card.market_cap = info.get("marketCap")
    card.enterprise_value = info.get("enterpriseValue")
    card.beta = info.get("beta")
    card.div_yield = info.get("dividendYield")
    card.one_year_return = _compute_1y_return(history)
    card.disclosures_kind = "sec"
    card.disclosures = []  # snapshot pack does not carry SEC filings
    card.tier_footer = (
        "yfinance Tier 2 (price + valuation). "
        "For SEC filings (10-K / 10-Q / 8-K) and XBRL facts, run report-equity-memo "
        "or data-us --pack memo-fetch."
    )
    return card


def _adapt_jp(pack: dict[str, Any]) -> Card:
    info_env = pack.get("info") or {}
    info = info_env.get("data") if isinstance(info_env, dict) and "data" in info_env else info_env
    history_env = pack.get("price_history") or {}
    history = history_env.get("data") if isinstance(history_env, dict) and "data" in history_env else history_env
    tdnet_env = pack.get("timely_disclosures") or {}
    tdnet = tdnet_env.get("data") if isinstance(tdnet_env, dict) and "data" in tdnet_env else tdnet_env

    card = Card(
        ticker=pack.get("yf_ticker") or pack.get("ticker", "?"),
        country="JP",
        fetched_at=pack.get("fetched_at", ""),
        currency="¥",
    )
    if isinstance(info, dict):
        card.name = info.get("longName") or info.get("shortName") or "N/A"
        card.exchange = info.get("exchange") or "TSE"
        card.sector = info.get("sector") or "N/A"
        card.close = info.get("regularMarketPrice") or info.get("currentPrice")
        card.fifty_two_w_low = info.get("fiftyTwoWeekLow")
        card.fifty_two_w_high = info.get("fiftyTwoWeekHigh")
        card.pe = info.get("trailingPE")
        card.forward_pe = info.get("forwardPE")
        card.pb = info.get("priceToBook")
        card.market_cap = info.get("marketCap")
        card.enterprise_value = info.get("enterpriseValue")
        card.beta = info.get("beta")
        card.div_yield = info.get("dividendYield")
    card.one_year_return = _compute_1y_return(history if isinstance(history, dict) else {})

    # TDnet disclosures (top 5 by date)
    disc_list: list[dict[str, Any]] = []
    if isinstance(tdnet, dict):
        items = tdnet.get("disclosures") or tdnet.get("items") or tdnet.get("results") or []
    elif isinstance(tdnet, list):
        items = tdnet
    else:
        items = []
    for item in items[:5] if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        disc_list.append({
            "date": item.get("pubdate") or item.get("date") or item.get("disclosure_date") or "",
            "type": item.get("disclosure_type") or item.get("type") or "",
            "title": item.get("title") or "",
        })
    card.disclosures = disc_list
    card.disclosures_kind = "tdnet"

    prov = pack.get("_provenance") or {}
    upgrade = prov.get("upgrade_hint")
    if upgrade:
        card.warnings.append(str(upgrade))
    tier_label = prov.get("tier_label") or "Tier 1 (yfinance + TDnet)"
    card.tier_footer = (
        f"yfinance .T + TDnet ({tier_label}). "
        "For full EDINET 有報 / 四半期 fundamentals, run report-equity-memo "
        "or data-jp --pack memo-fetch (set EDINET_API_KEY for Tier A primary)."
    )
    return card


def _tw_unwrap(env: Any) -> Any:
    """Unwrap data-tw's {_tier, _source, _action, data, _error} envelope."""
    if isinstance(env, dict) and "data" in env:
        return env.get("data")
    return env


def _adapt_tw(pack: dict[str, Any]) -> Card:
    yf = pack.get("yfinance") or {}
    mops = pack.get("mops") or {}
    twse = pack.get("twse") or {}
    finmind = pack.get("finmind") or {}

    def _tw_record(env: Any) -> dict[str, Any]:
        """Drill into _tw_unwrap's data, then if the unwrapped object also
        carries a nested 'data' key with the actual record (TWSE pattern), use it."""
        outer = _tw_unwrap(env)
        if isinstance(outer, dict) and "data" in outer and isinstance(outer["data"], dict):
            inner = outer["data"]
            return inner if inner else outer
        return outer if isinstance(outer, dict) else {}

    info = _tw_unwrap(yf.get("info")) or {}
    if isinstance(info, dict) and "data" in info and isinstance(info["data"], dict):
        info = info["data"]  # yfinance_client.py wraps once more
    history = _tw_unwrap(yf.get("history")) or {}
    company_basic = _tw_record(mops.get("company_basic"))
    daily_price = _tw_record(twse.get("daily_price"))
    pe_pb_yield = _tw_record(twse.get("pe_pb_yield"))
    three_inv = _tw_unwrap(finmind.get("three_investor_flow")) or {}

    # data-tw pack lacks a top-level fetched_at; pull from any inner record
    fetched_at = pack.get("fetched_at", "") or ""
    if not fetched_at and isinstance(daily_price, dict):
        fetched_at = daily_price.get("fetched_at", "") or ""
    if not fetched_at and isinstance(info, dict):
        fetched_at = info.get("fetched_at", "") or ""
    card = Card(
        ticker=pack.get("_ticker") or pack.get("ticker", "?"),
        country="TW",
        fetched_at=fetched_at,
        currency="NT$",
    )
    # Prefer MOPS company_basic for name; fall back to yfinance info
    if isinstance(company_basic, dict):
        card.name = (
            company_basic.get("公司名稱")
            or company_basic.get("company_name")
            or company_basic.get("name")
            or (info.get("longName") if isinstance(info, dict) else None)
            or "N/A"
        )
        card.sector = (
            company_basic.get("產業類別")
            or company_basic.get("industry")
            or (info.get("sector") if isinstance(info, dict) else None)
            or "N/A"
        )
    norm = pack.get("_normalized") or {}
    market = norm.get("market") if isinstance(norm, dict) else None
    card.exchange = "TWSE" if market == "sii" else ("TPEx" if market == "otc" else "TWSE/TPEx")

    # Price preference: TWSE daily_price > yfinance info
    if isinstance(daily_price, dict):
        card.close = (
            daily_price.get("ClosingPrice")
            or daily_price.get("closing_price")
            or daily_price.get("close")
        )
    if card.close in (None, "") and isinstance(info, dict):
        card.close = info.get("regularMarketPrice")

    if isinstance(info, dict):
        card.fifty_two_w_low = info.get("fiftyTwoWeekLow")
        card.fifty_two_w_high = info.get("fiftyTwoWeekHigh")
        card.market_cap = info.get("marketCap")
        card.enterprise_value = info.get("enterpriseValue")
        card.beta = info.get("beta")

    # TWSE pe_pb_yield is the authoritative source for P/E / P/B / 殖利率
    if isinstance(pe_pb_yield, dict):
        card.pe = pe_pb_yield.get("PEratio") or pe_pb_yield.get("pe_ratio") or pe_pb_yield.get("pe")
        card.pb = pe_pb_yield.get("PBratio") or pe_pb_yield.get("pb_ratio") or pe_pb_yield.get("pb")
        card.div_yield = pe_pb_yield.get("DividendYield") or pe_pb_yield.get("dividend_yield")
        # TWSE returns this as a number already in percent — flag for renderer
    if card.pe is None and isinstance(info, dict):
        card.pe = info.get("trailingPE")
    if card.pb is None and isinstance(info, dict):
        card.pb = info.get("priceToBook")

    card.one_year_return = _compute_1y_return(history if isinstance(history, dict) else {})

    # 三大法人 30d net flow as the disclosure block.
    # FinMind shape: data.TaiwanStockInstitutionalInvestorsBuySell._processed
    # = {latest_date, foreign, trust, dealer}  (scalar net flows)
    proc: Any = None
    if isinstance(three_inv, dict):
        inner = three_inv.get("TaiwanStockInstitutionalInvestorsBuySell")
        if isinstance(inner, dict):
            proc = inner.get("_processed")
        if proc is None:
            proc = three_inv.get("_processed")
    if isinstance(proc, dict):
        card.disclosures = [
            {"label": "外資", "net": proc.get("foreign")},
            {"label": "投信", "net": proc.get("trust")},
            {"label": "自營", "net": proc.get("dealer")},
        ]
    card.disclosures_kind = "mops"

    if pack.get("_partial"):
        card.warnings.append("Tier A 部分擷取失敗（_partial: true）— 部分欄位可能為 N/A")

    card.tier_footer = (
        "MOPS Tier A (公司揭露) + TWSE/TPEx OpenAPI Tier A (交易) + "
        "FinMind Tier 2-gap (T86 三大法人). For full BS/IS/CF + 月營收 + 重大訊息, "
        "run report-equity-memo or data-tw --pack memo-fetch."
    )
    return card


def _adapt_kr(pack: dict[str, Any]) -> Card:
    info = pack.get("info") or {}
    history = pack.get("history") or {}
    card = Card(
        ticker=pack.get("ticker", "?"),
        country="KR",
        fetched_at=pack.get("fetched_at", ""),
        currency="₩",
    )
    if isinstance(info, dict):
        card.name = info.get("longName") or info.get("shortName") or "N/A"
        card.exchange = info.get("exchange") or "KRX"
        card.sector = info.get("sector") or "N/A"
        card.close = info.get("regularMarketPrice") or info.get("currentPrice")
        card.fifty_two_w_low = info.get("fiftyTwoWeekLow")
        card.fifty_two_w_high = info.get("fiftyTwoWeekHigh")
        card.pe = info.get("trailingPE")
        card.forward_pe = info.get("forwardPE")
        card.pb = info.get("priceToBook")
        card.market_cap = info.get("marketCap")
        card.enterprise_value = info.get("enterpriseValue")
        card.beta = info.get("beta")
        card.div_yield = info.get("dividendYield")
    card.one_year_return = _compute_1y_return(history if isinstance(history, dict) else {})
    card.disclosures = []
    card.disclosures_kind = ""
    prov = pack.get("_provenance") or {}
    note = prov.get("primary_source_note") or ""
    card.tier_footer = (
        "yfinance Tier 2 (.KS/.KQ price + valuation). "
        "DART (전자공시시스템) primary-source integration deferred."
    )
    if note:
        card.warnings.append(note)
    return card


def _adapt_cn(pack: dict[str, Any]) -> Card:
    info = pack.get("yfinance_info") or {}
    history = pack.get("yfinance_history") or {}
    card = Card(
        ticker=pack.get("ticker", "?"),
        country="CN",
        fetched_at=pack.get("fetched_at", ""),
        currency="¥",  # CNY default; HK uses HK$
    )
    t = card.ticker.upper()
    if t.endswith(".HK"):
        card.currency = "HK$"
    if isinstance(info, dict):
        card.name = info.get("longName") or info.get("shortName") or "N/A"
        card.exchange = info.get("exchange") or (
            "HKEX" if t.endswith(".HK") else ("SSE" if t.endswith(".SS") else "SZSE")
        )
        card.sector = info.get("sector") or "N/A"
        card.close = info.get("regularMarketPrice") or info.get("currentPrice")
        card.fifty_two_w_low = info.get("fiftyTwoWeekLow")
        card.fifty_two_w_high = info.get("fiftyTwoWeekHigh")
        card.pe = info.get("trailingPE")
        card.forward_pe = info.get("forwardPE")
        card.pb = info.get("priceToBook")
        card.market_cap = info.get("marketCap")
        card.enterprise_value = info.get("enterpriseValue")
        card.beta = info.get("beta")
        card.div_yield = info.get("dividendYield")
    card.one_year_return = _compute_1y_return(history if isinstance(history, dict) else {})
    card.disclosures = []
    card.disclosures_kind = ""
    card.tier_footer = (
        "yfinance Tier 2 (.SS/.SZ/.HK price + valuation). "
        "cninfo (CSRC) / HKEX primary-source integration deferred."
    )
    return card


# --------------------------------------------------------------------------- #
# Pack-shape detection
# --------------------------------------------------------------------------- #


def detect_country(pack: dict[str, Any]) -> str:
    """Identify the source country bundle by characteristic keys."""
    # data-tw uses _pack/_ticker prefix
    if pack.get("_pack") and "yfinance" in pack and "mops" in pack and "twse" in pack:
        return "TW"
    # data-cn uses yfinance_info / country: "CN"
    if pack.get("country") in ("CN", "cn") or "yfinance_info" in pack:
        return "CN"
    # data-kr uses country: "kr"
    if pack.get("country") in ("KR", "kr"):
        return "KR"
    # data-jp has yf_ticker + timely_disclosures
    if pack.get("yf_ticker") or "timely_disclosures" in pack:
        return "JP"
    # data-us has company_info + price_history + ticker (no country key)
    if "company_info" in pack and "price_history" in pack:
        return "US"
    return "US"  # fallback


# --------------------------------------------------------------------------- #
# Renderer
# --------------------------------------------------------------------------- #


# Localized labels for the card. Keep the structure minimal — one block per
# language, all keys identical.
LABELS: dict[str, dict[str, str]] = {
    "en": {
        "snapshot": "Snapshot",
        "price": "Price",
        "valuation": "Valuation",
        "returns": "Returns / Dividends",
        "1y_return": "1Y return",
        "beta": "Beta",
        "div_yield": "Div Yield",
        "mcap": "Market Cap",
        "ev": "EV",
        "vs_52w": "vs 52W High",
        "fifty_two_w": "52W",
        "disclosures_sec": "Recent Disclosures (SEC EDGAR)",
        "disclosures_tdnet": "Recent Disclosures (TDnet)",
        "disclosures_mops": "三大法人 30d Net Flow",
        "disclosures_none": "Recent Disclosures",
        "no_disclosures": "Snapshot pack does not include disclosure listings — use --pack memo-fetch via report-equity-memo for SEC / EDINET / MOPS filings.",
        "data": "Data",
        "warning": "⚠ Notice",
    },
    "zh-TW": {
        "snapshot": "快照",
        "price": "股價",
        "valuation": "估值",
        "returns": "報酬 / 股利",
        "1y_return": "1Y 報酬",
        "beta": "Beta",
        "div_yield": "殖利率",
        "mcap": "市值",
        "ev": "企業價值",
        "vs_52w": "距 52W 高",
        "fifty_two_w": "52W",
        "disclosures_sec": "近期揭露（SEC EDGAR）",
        "disclosures_tdnet": "近期適時揭露（TDnet）",
        "disclosures_mops": "三大法人 30 日累計買賣超",
        "disclosures_none": "近期揭露",
        "no_disclosures": "Snapshot pack 不含揭露清單 — 完整揭露請改走 report-equity-memo（--pack memo-fetch）。",
        "data": "資料來源",
        "warning": "⚠ 注意",
    },
    "ja": {
        "snapshot": "スナップショット",
        "price": "株価",
        "valuation": "バリュエーション",
        "returns": "リターン / 配当",
        "1y_return": "1Y リターン",
        "beta": "ベータ",
        "div_yield": "配当利回り",
        "mcap": "時価総額",
        "ev": "EV",
        "vs_52w": "52W 高値比",
        "fifty_two_w": "52W",
        "disclosures_sec": "最近の開示（SEC EDGAR）",
        "disclosures_tdnet": "最近の適時開示（TDnet）",
        "disclosures_mops": "三大法人 30日累計買越/売越",
        "disclosures_none": "最近の開示",
        "no_disclosures": "Snapshot パックには開示一覧が含まれません — 完全な開示は report-equity-memo（--pack memo-fetch）を使用してください。",
        "data": "データ",
        "warning": "⚠ 注意",
    },
}


def _auto_lang(card: Card) -> str:
    t = (card.ticker or "").upper()
    if t.endswith(".TW") or t.endswith(".TWO"):
        return "zh-TW"
    if t.endswith(".T") or t.endswith(".TO"):
        return "ja"
    if card.country == "JP":
        return "ja"
    if card.country == "TW":
        return "zh-TW"
    if t.endswith(".HK") or t.endswith(".SS") or t.endswith(".SZ"):
        return "zh-TW"
    return "en"


def render(card: Card, lang: str = "en") -> str:
    if lang not in LABELS:
        lang = "en"
    L = LABELS[lang]
    out: list[str] = []

    # Header
    out.append(f"## {card.ticker} {L['snapshot']} — {card.fetched_at[:10] if card.fetched_at else ''}")
    out.append("")
    head_bits = [card.name]
    if card.exchange and card.exchange != "N/A":
        head_bits.append(card.exchange)
    if card.sector and card.sector != "N/A":
        head_bits.append(card.sector)
    out.append("**" + "** | **".join(head_bits) + "**" if head_bits else "")

    # Warnings (Tier 2 fallback / partial / KR-CN deferred notes)
    for w in card.warnings:
        out.append("")
        out.append(f"> {L['warning']}: {w}")

    # Price
    out.append("")
    cur = card.currency or ""
    price_line = (
        f"**{L['price']}**: {cur}{_fmt_num(card.close)}"
        f" | {L['fifty_two_w']}: {cur}{_fmt_num(card.fifty_two_w_low)}–{cur}{_fmt_num(card.fifty_two_w_high)}"
        f" | {L['vs_52w']}: {_vs_52w_high_pct(card.close, card.fifty_two_w_high)}"
    )
    out.append(price_line)

    # Valuation
    val_line = (
        f"**{L['valuation']}**: P/E {_fmt_num(card.pe)}"
        f" | P/B {_fmt_num(card.pb)}"
        f" | {L['mcap']}: {_fmt_billions(card.market_cap, cur)}"
        f" | {L['ev']}: {_fmt_billions(card.enterprise_value, cur)}"
    )
    out.append(val_line)

    # Returns / dividends — yfinance changed dividendYield to already-percent
    # (e.g. AAPL 0.38 == 0.38%). TW pe_pb_yield DividendYield is also in pct.
    # Treat all sources uniformly as already-percent unless we see a fraction.
    div_already_pct = True
    # Heuristic safety: if value is between 0 and 1 AND it's a yfinance source,
    # the legacy fraction shape may still appear — auto-detect by magnitude.
    try:
        if card.div_yield is not None and 0 < float(card.div_yield) < 0.001:
            # Implausible as percent (< 0.001%) — must be fraction shape
            div_already_pct = False
    except (TypeError, ValueError):
        pass
    ret_line = (
        f"**{L['returns']}**: {L['1y_return']} {_fmt_pct(card.one_year_return, already_pct=True) if card.one_year_return is not None else 'N/A'}"
        f" | {L['beta']} {_fmt_num(card.beta)}"
        f" | {L['div_yield']} {_fmt_pct(card.div_yield, already_pct=div_already_pct)}"
    )
    out.append(ret_line)

    # Disclosures section
    out.append("")
    if card.disclosures_kind == "tdnet" and card.disclosures:
        out.append(f"### {L['disclosures_tdnet']}")
        out.append("")
        for d in card.disclosures:
            date = d.get("date", "") or ""
            kind = d.get("type", "") or ""
            title = d.get("title", "") or ""
            out.append(f"- {date} | {kind} | {title}")
    elif card.disclosures_kind == "mops" and card.disclosures:
        out.append(f"### {L['disclosures_mops']}")
        out.append("")
        out.append("| 投資人 | 累計買賣超（千股） |")
        out.append("|---|---|")
        for d in card.disclosures:
            label = d.get("label", "") or ""
            raw = d.get("net")
            try:
                net = float(raw) if raw is not None else None
            except (TypeError, ValueError):
                net = None
            if net is None:
                out.append(f"| {label} | N/A |")
            else:
                sign = "↑" if net > 0 else ("↓" if net < 0 else "—")
                out.append(f"| {label} | {sign} {_fmt_num(net, 0)} |")
    elif card.disclosures_kind == "sec":
        out.append(f"### {L['disclosures_sec']}")
        out.append("")
        out.append(L["no_disclosures"])
    else:
        out.append(f"### {L['disclosures_none']}")
        out.append("")
        out.append(L["no_disclosures"])

    # Footer
    out.append("")
    out.append("---")
    out.append("")
    out.append(f"_{L['data']}: {card.tier_footer}_")
    out.append("")

    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Format a snapshot pack JSON into a Markdown card. Pure formatter — no I/O beyond input + stdout.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to snapshot pack JSON (output of data-{us|jp|tw|kr|cn}/scripts/pack.py --pack snapshot).",
    )
    parser.add_argument(
        "--lang",
        choices=["en", "zh-TW", "ja"],
        default=None,
        help="Output language. Default: auto-detect from ticker suffix / country.",
    )
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            pack = json.load(f)
    except FileNotFoundError:
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in {args.input}: {e}", file=sys.stderr)
        return 1

    if not isinstance(pack, dict):
        print(f"error: top-level pack JSON must be an object, got {type(pack).__name__}", file=sys.stderr)
        return 1

    country = detect_country(pack)
    adapters = {
        "US": _adapt_us,
        "JP": _adapt_jp,
        "TW": _adapt_tw,
        "KR": _adapt_kr,
        "CN": _adapt_cn,
    }
    adapter = adapters.get(country, _adapt_us)
    card = adapter(pack)

    lang = args.lang or _auto_lang(card)
    print(render(card, lang=lang))
    return 0


if __name__ == "__main__":
    sys.exit(main())
