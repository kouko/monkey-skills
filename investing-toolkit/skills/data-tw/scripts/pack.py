#!/usr/bin/env python3
"""
data-tw / pack.py — Layer 1 facade for Taiwan equity + macro fetches.

Composes 8 underlying clients into 5 pack types:
  - snapshot         : yfinance + MOPS basic disclosure + TWSE trade data + FinMind T86 (single ticker)
  - memo-fetch       : snapshot + MOPS financial statements + 月營收 + 重大訊息 (heavy, single ticker)
  - comps-multiples  : yfinance multiples (single or batch)
  - screener-batch   : yfinance batch + minimal MOPS valuation fields (batch only)
  - regime-pack      : CBC + DGBAS + NDC 五色景氣燈號 + statgov + CIER PMI (no ticker dimension)

Tier policy:
  - MOPS + TWSE OpenAPI = Tier A primary
  - FinMind = by-design gap supplier — NOT automatic Tier A → 2 retry
    (per-stock T86 三大法人 daily flow; price history for .TWO; split-adjusted OHLCV)
    Tier A errors surface as per-source `_error` + top-level `_partial: true`;
    consumers inspect `_tier`/`_partial` to decide escalation.
  - yfinance = Tier 2 cross-source (price/info/multiples) — convenient batch & multiples

Output: structured JSON to stdout.
- Each underlying client output is wrapped in {tier, source, action, data, _error?}.
- Per-source failures degrade to `_partial: true` rather than aborting the pack.

Ticker conventions:
  - .TW → TWSE listed (sii market)
  - .TWO → TPEx listed (otc market)
  - bare numeric (e.g. 2330) → assumed sii (.TW); explicit suffix preferred

Cache: honors $INVESTING_TOOLKIT_CACHE if set.

Examples:
  pack.py --ticker 2330.TW --pack snapshot
  pack.py --ticker 2330.TW --pack memo-fetch
  pack.py --tickers 2330.TW,2454.TW --pack screener-batch
  pack.py --tickers 2330.TW,2454.TW --pack comps-multiples
  pack.py --pack regime-pack
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

_UTCNOW = lambda: datetime.now(timezone.utc).replace(tzinfo=None)
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PACK_TYPES = {"snapshot", "memo-fetch", "comps-multiples", "screener-batch", "regime-pack"}


# ----------------------------- ticker helpers -----------------------------

def normalize_ticker(raw: str) -> dict[str, str]:
    """Return {ticker_yf, ticker_code, market} for a TW ticker.

    .TW → market=sii (TWSE)
    .TWO → market=otc (TPEx)
    bare numeric → assume sii / .TW
    """
    raw = raw.strip().upper()
    if raw.endswith(".TW"):
        return {"ticker_yf": raw, "ticker_code": raw[:-3], "market": "sii"}
    if raw.endswith(".TWO"):
        return {"ticker_yf": raw, "ticker_code": raw[:-4], "market": "otc"}
    # bare → assume sii
    return {"ticker_yf": f"{raw}.TW", "ticker_code": raw, "market": "sii"}


def latest_roc_quarter(today: datetime | None = None) -> tuple[int, int]:
    """Return (roc_year, season) for the most recently-FILED quarter.

    TW quarterly statements filing deadlines (TWSE/TPEx-listed, consolidated):
      Q4 (年報): by Mar 31 of next year → safe Apr 1+
      Q1:       by May 15              → safe May 16+
      Q2 (半年報): by Aug 14            → safe Aug 15+
      Q3:       by Nov 14              → safe Nov 15+

    Filing-aware logic: use buffered deadlines (one day after the deadline) so
    we never request a quarter whose deadline has not yet passed (which would
    cause MOPS to return an empty result / error).
    """
    today = today or _UTCNOW()
    month, day = today.month, today.day
    if (month, day) >= (11, 15):
        season, year = 3, today.year
    elif (month, day) >= (8, 15):
        season, year = 2, today.year
    elif (month, day) >= (5, 16):
        season, year = 1, today.year
    elif (month, day) >= (4, 1):
        season, year = 4, today.year - 1
    else:
        # Jan 1 – Mar 31: previous year's Q4 not yet filed → fall back to Q3
        season, year = 3, today.year - 1
    return year - 1911, season


def latest_revenue_month(today: datetime | None = None) -> tuple[int, int]:
    """Return (roc_year, month) for the most recently-published 月營收.

    月營收 published by the 10th of the following month. Use a 5-day buffer
    (day < 15) before treating last month's number as available — disclosures
    occasionally trickle in past the 10th.
    """
    today = today or _UTCNOW()
    if today.day < 15:
        # last month not yet (reliably) published; go 2 back
        ref = today - timedelta(days=40)
    else:
        ref = today - timedelta(days=15)
    return ref.year - 1911, ref.month


# ----------------------------- subprocess runner -----------------------------

def run_client(script: str, args: list[str], timeout: int = 60) -> dict[str, Any]:
    """Run a client script and return parsed JSON, or an error envelope."""
    cmd = ["uv", "run", str(SCRIPT_DIR / script), *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ},
        )
    except subprocess.TimeoutExpired:
        return {"_error": "timeout", "_cmd": " ".join(cmd)}
    except Exception as exc:
        return {"_error": f"exec_failed: {exc}", "_cmd": " ".join(cmd)}

    if result.returncode != 0:
        return {
            "_error": f"exit_{result.returncode}",
            "_stderr": (result.stderr or "")[:600],
            "_cmd": " ".join(cmd),
        }
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {
            "_error": f"json_decode: {exc}",
            "_stdout_head": result.stdout[:300],
            "_cmd": " ".join(cmd),
        }


def wrap(tier: str, source: str, action: str, data: Any) -> dict[str, Any]:
    """Wrap a client output with provenance metadata."""
    out: dict[str, Any] = {
        "_tier": tier,
        "_source": source,
        "_action": action,
    }
    if isinstance(data, dict) and "_error" in data:
        out["_error"] = data["_error"]
        for k, v in data.items():
            if k.startswith("_") and k != "_error":
                out[k] = v
    else:
        out["data"] = data
    return out


# ----------------------------- pack: snapshot -----------------------------

_YF_LABEL_MAP_TW = {
    "revenue": ["Total Revenue", "Operating Revenue"],
    "operating_income": ["Operating Income", "Total Operating Income As Reported"],
    "net_income": ["Net Income", "Net Income Common Stockholders"],
    "operating_cash_flow": ["Operating Cash Flow"],
    "capex": ["Capital Expenditure"],
    "free_cash_flow": ["Free Cash Flow"],
    "long_term_debt": ["Long Term Debt"],
    "short_term_debt": ["Current Debt"],
    "total_debt": ["Total Debt"],
    "cash": ["Cash And Cash Equivalents"],
}


def _build_canonical_from_yf_financials_tw(financials: dict) -> dict:
    """T3 (yfinance Tier 2 fallback for TW) — extract canonical from
    yfinance --action financials annual. Per ADR-0003.

    Note: MOPS Tier A canonical extraction (中文 t164sb04/05/03 → flat
    income_statement) is deferred to a future PR — see tw_specific block.
    Most-recent-first, depth 5.
    """
    if not isinstance(financials, dict):
        financials = {}
    income = financials.get("income_statement") or {}
    balance = financials.get("balance_sheet") or {}
    cashflow = financials.get("cash_flow") or {}
    periods = sorted(set(income) | set(balance) | set(cashflow), reverse=True)[:5]

    def _extract(src: dict, canonical: str) -> tuple[list[float], str | None]:
        labels = _YF_LABEL_MAP_TW.get(canonical, [])
        used_label: str | None = None
        out: list[float] = []
        for p in periods:
            row = src.get(p, {})
            v = None
            for label in labels:
                if label in row and row[label] is not None:
                    v = row[label]
                    if used_label is None:
                        used_label = label
                    break
            if v is not None:
                try:
                    out.append(float(v))
                except (TypeError, ValueError):
                    pass
        return out, used_label

    revenue, rev_label = _extract(income, "revenue")
    operating_income, op_label = _extract(income, "operating_income")
    net_income, ni_label = _extract(income, "net_income")
    ocf, ocf_label = _extract(cashflow, "operating_cash_flow")
    capex_raw, capex_label = _extract(cashflow, "capex")
    fcf, fcf_label = _extract(cashflow, "free_cash_flow")
    long_term_debt, ltd_label = _extract(balance, "long_term_debt")
    short_term_debt, std_label = _extract(balance, "short_term_debt")
    total_debt_raw, td_label = _extract(balance, "total_debt")
    cash, cash_label = _extract(balance, "cash")

    capex = [abs(v) for v in capex_raw]
    total_debt = total_debt_raw if total_debt_raw else [
        (long_term_debt[i] if i < len(long_term_debt) else 0.0)
        + (short_term_debt[i] if i < len(short_term_debt) else 0.0)
        for i in range(max(len(long_term_debt), len(short_term_debt)))
    ]

    def _meta(canonical: str, label: str | None, periods_used: list[str]) -> dict:
        return {
            "source_label": label,
            "source_labels_tried": _YF_LABEL_MAP_TW.get(canonical, []),
            "fiscal_year_ends": periods_used[: len(periods_used)],
            "accounting_standard": "tifrs",  # Taiwan IFRS (slight variance from international IFRS)
            "unit": "TWD",
            "tier": "Tier 2 (yfinance scraper — MOPS t164sb04/05/03 Tier A T3 deferred)",
        }

    return {
        "income_statement": {
            "revenue": revenue,
            "operating_income": operating_income,
            "ebit": operating_income,
            "net_income": net_income,
            "_meta": {
                "revenue": _meta("revenue", rev_label, periods[: len(revenue)]),
                "operating_income": _meta("operating_income", op_label, periods[: len(operating_income)]),
                "ebit": {**_meta("operating_income", op_label, periods[: len(operating_income)]), "note": "alias of operating_income"},
                "net_income": _meta("net_income", ni_label, periods[: len(net_income)]),
            },
        },
        "cash_flow": {
            "operating_cash_flow": ocf,
            "capex": capex,
            "fcf": fcf,
            "_meta": {
                "operating_cash_flow": _meta("operating_cash_flow", ocf_label, periods[: len(ocf)]),
                "capex": {**_meta("capex", capex_label, periods[: len(capex)]), "note": "absolute value"},
                "fcf": _meta("free_cash_flow", fcf_label, periods[: len(fcf)]),
            },
        },
        "balance_sheet": {
            "long_term_debt": long_term_debt,
            "short_term_debt": short_term_debt,
            "total_debt": total_debt,
            "cash": cash,
            "_meta": {
                "long_term_debt": _meta("long_term_debt", ltd_label, periods[: len(long_term_debt)]),
                "short_term_debt": _meta("short_term_debt", std_label, periods[: len(short_term_debt)]),
                "total_debt": (
                    _meta("total_debt", td_label, periods[: len(total_debt)])
                    if total_debt_raw
                    else {
                        "source_label": None,
                        "derivation": "long_term_debt + short_term_debt",
                        "components": {"long_term_debt": ltd_label, "short_term_debt": std_label},
                    }
                ),
                "cash": _meta("cash_and_equivalents", cash_label, periods[: len(cash)]),
            },
        },
    }


def _extract_ohlcv_rows_from_tw_yf(yf_history_wrapped: dict) -> list[dict]:
    """Unwrap data-tw's nested yfinance history envelope to the OHLCV
    rows list. Handles the {_tier, _source, _action, data: {data: [...]}}
    wrapper shape that data-tw uses (uniquely among 5 country packs).
    """
    if not isinstance(yf_history_wrapped, dict):
        return []
    inner = yf_history_wrapped.get("data")
    if not isinstance(inner, dict):
        return []
    rows = inner.get("data")
    return rows if isinstance(rows, list) else []


def pack_snapshot(ticker: str, period: str = "1y") -> dict[str, Any]:
    norm = normalize_ticker(ticker)
    yf_ticker = norm["ticker_yf"]
    code = norm["ticker_code"]
    market = norm["market"]
    roc_year, season = latest_roc_quarter()
    rev_year, rev_month = latest_revenue_month()
    date_3mo = (_UTCNOW() - timedelta(days=90)).strftime("%Y-%m-%d")

    out: dict[str, Any] = {
        "_pack": "snapshot",
        "_ticker": yf_ticker,
        "_normalized": norm,
        "yfinance": {},
        "mops": {},
        "twse": {},
        "finmind": {},
        "_partial": False,
    }

    # yfinance — Tier 2 (price snapshot)
    out["yfinance"]["info"] = wrap("2", "yfinance", "info",
        run_client("yfinance_client.py", ["--ticker", yf_ticker, "--action", "info"]))
    out["yfinance"]["history"] = wrap("2", "yfinance", "history",
        run_client("yfinance_client.py", ["--ticker", yf_ticker, "--action", "history", "--period", period]))

    # MOPS — Tier A primary
    out["mops"]["company_basic"] = wrap("A", "mops", "company-basic",
        run_client("mops_client.py", ["--ticker", code, "--action", "company-basic"]))
    out["mops"]["balance_sheet"] = wrap("A", "mops", "balance-sheet",
        run_client("mops_client.py", ["--ticker", code, "--action", "balance-sheet",
                                       "--year", str(roc_year), "--season", str(season)]))
    out["mops"]["income_statement"] = wrap("A", "mops", "income-statement",
        run_client("mops_client.py", ["--ticker", code, "--action", "income-statement",
                                       "--year", str(roc_year), "--season", str(season)]))

    # TWSE OpenAPI — Tier A primary
    out["twse"]["daily_price"] = wrap("A", "twse_openapi", "daily-price",
        run_client("twse_openapi_client.py", ["--ticker", code, "--action", "daily-price"]))
    out["twse"]["pe_pb_yield"] = wrap("A", "twse_openapi", "pe-pb-yield",
        run_client("twse_openapi_client.py", ["--ticker", code, "--action", "pe-pb-yield"]))
    out["twse"]["margin_balance"] = wrap("A", "twse_openapi", "margin-balance",
        run_client("twse_openapi_client.py", ["--ticker", code, "--action", "margin-balance"]))

    # FinMind — Tier 2 by-design (T86 daily 三大法人 flow is a Tier A gap)
    out["finmind"]["three_investor_flow"] = wrap("2-gap", "finmind", "T86",
        run_client("finmind_client.py",
                   ["--ticker", code, "--dataset", "TaiwanStockInstitutionalInvestorsBuySell",
                    "--date-start", date_3mo]))

    # mark partial if any tier-A errored
    for src in ("mops", "twse"):
        for entry in out[src].values():
            if "_error" in entry:
                out["_partial"] = True
                break
    # T1 canonical OHLCV alias — flatten yfinance.history wrapper to top-level
    out["history"] = _extract_ohlcv_rows_from_tw_yf(out["yfinance"]["history"])
    return out


# ----------------------------- pack: memo-fetch -----------------------------

def pack_memo_fetch(ticker: str, period: str = "2y") -> dict[str, Any]:
    """Snapshot + financial statements + 月營收 12m + 重大訊息. Heavy, single ticker."""
    norm = normalize_ticker(ticker)
    code = norm["ticker_code"]
    market = norm["market"]
    roc_year, season = latest_roc_quarter()
    rev_year, rev_month = latest_revenue_month()
    roc_5y_ago = roc_year - 5
    date_3mo = (_UTCNOW() - timedelta(days=90)).strftime("%Y-%m-%d")

    out = pack_snapshot(ticker, period=period)
    out["_pack"] = "memo-fetch"

    # Cash flow + monthly revenue + dividends + announcements + insider/director — Tier A
    out["mops"]["cash_flow"] = wrap("A", "mops", "cash-flow",
        run_client("mops_client.py", ["--ticker", code, "--action", "cash-flow",
                                       "--year", str(roc_year), "--season", str(season)]))
    out["mops"]["monthly_revenue"] = wrap("A", "mops", "monthly-revenue",
        run_client("mops_client.py", ["--ticker", code, "--action", "monthly-revenue",
                                       "--year", str(rev_year), "--month", str(rev_month)]))
    out["mops"]["dividends"] = wrap("A", "mops", "dividends",
        run_client("mops_client.py", ["--ticker", code, "--action", "dividends",
                                       "--first-year", str(roc_5y_ago), "--last-year", str(roc_year)]))
    out["mops"]["director_holdings"] = wrap("A", "mops", "director-holdings",
        run_client("mops_client.py", ["--ticker", code, "--action", "director-holdings"]))
    out["mops"]["insider_trades"] = wrap("A", "mops", "insider-trades",
        run_client("mops_client.py", ["--ticker", code, "--action", "insider-trades"]))
    out["mops"]["announcements"] = wrap("A", "mops", "realtime-announcements",
        run_client("mops_client.py", ["--action", "realtime-announcements",
                                       "--market", market, "--count", "10"]))

    # TWSE three_investor (snapshot) — Tier A
    out["twse"]["three_investor"] = wrap("A", "twse_openapi", "three-investor",
        run_client("twse_openapi_client.py", ["--ticker", code, "--action", "three-investor"]))

    # TWSE /rwd/ raw OHLCV history (Tier A primary) for sii listings
    if market == "sii":
        months = 24 if period in ("2y",) else (12 if period in ("1y",) else 6)
        out["twse"]["stock_day_history"] = wrap("A", "twse_openapi", "stock-day-history",
            run_client("twse_openapi_client.py",
                       ["--ticker", code, "--action", "stock-day-history",
                        "--months", str(months)]))
    else:
        # .TWO has no /rwd/; fall through to FinMind TaiwanStockPrice
        date_start = (_UTCNOW() - timedelta(days=730 if period == "2y" else 365)).strftime("%Y-%m-%d")
        out["finmind"]["price_history"] = wrap("2", "finmind", "TaiwanStockPrice",
            run_client("finmind_client.py",
                       ["--ticker", code, "--dataset", "TaiwanStockPrice", "--date-start", date_start]))

    # FinMind margin time series — Tier 2 by-design
    out["finmind"]["margin_history"] = wrap("2-gap", "finmind", "TaiwanStockMarginPurchaseShortSale",
        run_client("finmind_client.py",
                   ["--ticker", code, "--dataset", "TaiwanStockMarginPurchaseShortSale",
                    "--date-start", date_3mo]))

    # Re-walk every Tier A entry (snapshot only checked its own subset; memo-fetch
    # added 8 more A-tier fetches). Flip _partial=True if any Tier A entry errored.
    if not out.get("_partial"):
        for group in (out.get("yfinance", {}), out.get("mops", {}),
                       out.get("twse", {}), out.get("finmind", {})):
            for entry in group.values():
                if isinstance(entry, dict) and entry.get("_tier") == "A" and "_error" in entry:
                    out["_partial"] = True
                    break
            if out["_partial"]:
                break

    # T3 canonical staging — yfinance Tier 2 fallback per ADR-0003.
    # MOPS Tier A canonical extraction (中文 t164sb04/05/03 → flat) is deferred.
    yf_ticker = norm["ticker_yf"]
    yf_fin = run_client(
        "yfinance_client.py",
        ["--ticker", yf_ticker, "--action", "financials", "--period", "annual"],
    )
    canonical = _build_canonical_from_yf_financials_tw(yf_fin)
    out["yfinance"]["financials_annual"] = wrap("2", "yfinance", "financials-annual", yf_fin)
    out["income_statement"] = canonical["income_statement"]
    out["cash_flow"] = canonical["cash_flow"]
    out["balance_sheet"] = canonical["balance_sheet"]

    # shares_outstanding / current_price from yfinance.info (already fetched in snapshot)
    yf_info_wrapped = out.get("yfinance", {}).get("info") or {}
    yf_info_data = yf_info_wrapped.get("data") if isinstance(yf_info_wrapped, dict) else None
    if isinstance(yf_info_data, dict):
        out["shares_outstanding"] = yf_info_data.get("sharesOutstanding")
        out["current_price"] = yf_info_data.get("regularMarketPrice")
    else:
        out["shares_outstanding"] = None
        out["current_price"] = None

    out["tw_specific"] = {
        "monthly_revenue_note": "TW-unique: 上市公司每月強制公告月營收 (mops/monthly-revenue is Tier A primary). NOT in canonical income_statement (5-country LCD). See out.mops.monthly_revenue raw block.",
        "report_basis_note": "yfinance reports consolidated (合併) statements. MOPS exposes both 母公司 (parent-only) and 合併 — see out.mops raw block. Canonical defaults to 合併.",
        "primary_source_status": "MOPS Tier A available for raw (out.mops.income_statement / balance_sheet / cash_flow are 中文 ROC-dated structured). T3 normalize from MOPS into canonical 5-year arrays is deferred to a follow-up PR.",
        "three_investor_flow_note": "TW-unique: out.finmind.three_investor_flow / out.twse.three_investor.",
        "margin_trading_note": "TW-unique: out.twse.margin_balance / out.finmind.margin_history.",
    }
    return out


# ----------------------------- pack: comps-multiples -----------------------------

def pack_comps_multiples(tickers: list[str]) -> dict[str, Any]:
    """yfinance info (multiples-only) for one or many tickers."""
    out: dict[str, Any] = {"_pack": "comps-multiples", "_tickers": [], "tickers": {}}
    info_alias: dict[str, dict] = {}  # T1 canonical: pack.info[ticker] → multiples
    for t in tickers:
        norm = normalize_ticker(t)
        yf_t = norm["ticker_yf"]
        out["_tickers"].append(yf_t)
        info = run_client("yfinance_client.py", ["--ticker", yf_t, "--action", "info"])
        if isinstance(info, dict) and "_error" in info:
            # let wrap() surface the error envelope
            out["tickers"][yf_t] = wrap("2", "yfinance", "info-multiples", info)
            continue
        # extract just the multiples block
        multiples_keys = ["trailingPE", "forwardPE", "priceToSalesTrailing12Months",
                          "priceToBook", "enterpriseToEbitda", "enterpriseToRevenue",
                          "marketCap", "enterpriseValue"]
        multiples = {k: info[k] for k in multiples_keys if isinstance(info, dict) and k in info}
        out["tickers"][yf_t] = wrap("2", "yfinance", "info-multiples", {"multiples": multiples})
        if multiples:
            info_alias[yf_t] = multiples
    # T1 canonical multiples alias — analysis-comps reads pack.info[ticker]
    out["info"] = info_alias
    return out


# ----------------------------- pack: screener-batch -----------------------------

def pack_screener_batch(tickers: list[str], period: str = "1y") -> dict[str, Any]:
    """yfinance batch info+history + minimal MOPS company_basic per ticker."""
    out: dict[str, Any] = {"_pack": "screener-batch", "_tickers": [], "yfinance": {}, "mops": {}}
    yf_list = []
    for t in tickers:
        norm = normalize_ticker(t)
        yf_list.append(norm["ticker_yf"])
        out["_tickers"].append(norm["ticker_yf"])

    # yfinance batch — single subprocess
    batch_info = run_client("yfinance_client.py",
                             ["--tickers", ",".join(yf_list), "--action", "info"])
    batch_hist = run_client("yfinance_client.py",
                             ["--tickers", ",".join(yf_list), "--action", "history", "--period", period])
    out["yfinance"]["info_batch"] = wrap("2", "yfinance", "info-batch", batch_info)
    out["yfinance"]["history_batch"] = wrap("2", "yfinance", "history-batch", batch_hist)

    # minimal MOPS — company_basic for each ticker (Tier A)
    for t in tickers:
        norm = normalize_ticker(t)
        code = norm["ticker_code"]
        out["mops"][norm["ticker_yf"]] = wrap("A", "mops", "company-basic",
            run_client("mops_client.py", ["--ticker", code, "--action", "company-basic"]))
    return out


# ----------------------------- pack: regime-pack -----------------------------

def _flatten_regime_to_series(root: dict) -> dict:
    """T2 canonical (per ADR-0002) — walk regime-pack root and emit flat
    `series: {indicator_id: [floats]}` block for analysis-macro-regime.
    Identical helper to data-kr / data-jp / data-cn.

    For data-tw the root contains source-named blocks (cbc / dgbas / ndc /
    statgov) where each leaf is wrapped via pack.wrap() into
    `{_tier, _source, _action, data: {...}}` envelope. The walker recurses
    into `data` automatically; `_tier`/`_source`/`_action` are strings so
    skipped. Underscored keys are skipped.
    """
    flat: dict[str, list[float]] = {}

    def visit(node, path):
        if not isinstance(node, dict):
            return
        obs = node.get("observations")
        if isinstance(obs, list):
            values = []
            for o in obs:
                if isinstance(o, dict) and o.get("value") is not None:
                    try:
                        values.append(float(o["value"]))
                    except (TypeError, ValueError):
                        pass
            if not values:
                return
            preset = node.get("preset")
            series_field = node.get("series")
            if isinstance(preset, str):
                primary = preset
            elif isinstance(series_field, str):
                primary = series_field
            elif path:
                primary = path[-1]
            else:
                return
            if primary not in flat:
                flat[primary] = values
            if len(path) >= 2 and isinstance(path[0], str):
                key = f"{path[0]}.{primary}"
                if key not in flat:
                    flat[key] = values
            return
        for k, v in node.items():
            if isinstance(k, str) and k.startswith("_"):
                continue
            if isinstance(v, dict):
                visit(v, path + (k,))

    for k, v in root.items():
        if isinstance(k, str) and k.startswith("_"):
            continue
        if isinstance(v, dict):
            visit(v, (k,))
    return flat


def pack_regime() -> dict[str, Any]:
    """Macro regime indicators: CBC + DGBAS + NDC 五色景氣燈號 + statgov + CIER PMI."""
    out: dict[str, Any] = {"_pack": "regime-pack", "cbc": {}, "dgbas": {},
                           "ndc": {}, "statgov": {}, "_partial": False}

    # CBC — rates / forex / money
    out["cbc"]["macro"] = wrap("A", "cbc", "preset-bundle",
        run_client("cbc_client.py", ["--preset", "rediscount-rate,twdusd,m2,reserve-money"]))
    # DGBAS — inflation
    out["dgbas"]["inflation"] = wrap("A", "dgbas", "preset-bundle",
        run_client("dgbas_client.py", ["--preset", "cpi,cpi-yoy,core-cpi,ppi,import-pi,export-pi"]))
    # NDC — 五色景氣燈號 + components
    out["ndc"]["signal"] = wrap("A", "ndc", "signal",
        run_client("ndc_client.py", ["--preset", "signal,signal-components"]))
    # NDC PMI / NMI (CIER via data.gov.tw 6100)
    out["ndc"]["pmi"] = wrap("A", "ndc", "pmi",
        run_client("ndc_client.py", ["--preset", "pmi-mfg,pmi-nmi"]))
    # statgov — growth / labor / trade / leading-coincident CI
    out["statgov"]["growth"] = wrap("A", "statgov", "preset-growth",
        run_client("statgov_client.py",
                   ["--preset", "gdp-yoy,ipi,manufacturing-yoy,retail-yoy"]))
    out["statgov"]["trade"] = wrap("A", "statgov", "preset-trade",
        run_client("statgov_client.py",
                   ["--preset", "export-orders,exports,imports,exports-yoy,imports-yoy"]))
    out["statgov"]["labor_cycle_other"] = wrap("A", "statgov", "preset-bundle",
        run_client("statgov_client.py",
                   ["--preset",
                    "unemployment,unemployment-sa,leading-index,coincident-index,fx-reserves,taiex,m2-yoy"]))

    # Mark partial on any error
    for group in (out["cbc"], out["dgbas"], out["ndc"], out["statgov"]):
        for entry in group.values():
            if "_error" in entry:
                out["_partial"] = True
                break
    # T2 canonical flat series alias per ADR-0002
    out["series"] = _flatten_regime_to_series(out)
    return out


# ----------------------------- main -----------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="data-tw / pack.py — Layer 1 facade for TW equity + macro fetches"
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--ticker", help="Single TW ticker (e.g. 2330.TW, 2330.TWO, 2330)")
    g.add_argument("--tickers", help="Comma-separated tickers for batch packs")
    parser.add_argument("--pack", required=True, choices=sorted(PACK_TYPES))
    parser.add_argument("--period", default="1y",
                        help="History lookback for snapshot/memo-fetch/screener-batch")
    args = parser.parse_args()

    if args.pack == "snapshot":
        if not args.ticker:
            parser.error("--pack snapshot requires --ticker")
        result = pack_snapshot(args.ticker, period=args.period)
    elif args.pack == "memo-fetch":
        if not args.ticker:
            parser.error("--pack memo-fetch requires --ticker")
        result = pack_memo_fetch(args.ticker, period=args.period)
    elif args.pack == "comps-multiples":
        tickers = []
        if args.ticker:
            tickers = [args.ticker]
        elif args.tickers:
            tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
        else:
            parser.error("--pack comps-multiples requires --ticker or --tickers")
        result = pack_comps_multiples(tickers)
    elif args.pack == "screener-batch":
        if not args.tickers:
            parser.error("--pack screener-batch requires --tickers")
        tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
        result = pack_screener_batch(tickers, period=args.period)
    elif args.pack == "regime-pack":
        result = pack_regime()
    else:
        parser.error(f"unknown pack {args.pack}")
        return 2

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
