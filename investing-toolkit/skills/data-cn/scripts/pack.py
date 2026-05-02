#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
pack.py — data-cn Layer 1 facade for investing-toolkit v2.0.0 three-layer.

Composes multi-source pulls into 5 pack types:

  --pack snapshot         Quick overview card (yfinance info + price)
  --pack memo-fetch       Equity memo full data (yfinance financials; CN
                          primary-source disclosure not in scope)
  --pack comps-multiples  Multiples-only (yfinance), single or batch
  --pack screener-batch   Lightweight batch fields (yfinance batch)
  --pack regime-pack      NBS macro (21 presets) + akshare PBOC/Caixin (8) + FRED USDCNY

Tier routing (data-cn):
  - NBS new-SPA API (primary, 21 indicators): nbs_client.py
  - PBOC + SHIBOR + Caixin PMI (aggregator, 8 indicators): akshare_client.py
  - USDCNY cross-rate + FX reserves: fred_client.py
  - .SS (Shanghai) / .SZ (Shenzhen) / .HK individual stocks: yfinance_client.py
    (auto-suffix appended if user passes bare 6-digit code or HK 4-digit code)

Single + batch:
  pack.py --ticker 600519.SS --pack snapshot
  pack.py --tickers 600519.SS,000858.SZ --pack screener-batch
  pack.py --pack regime-pack

Examples:
  uv run pack.py --ticker 600519 --pack snapshot          # auto -> 600519.SS
  uv run pack.py --ticker 000858 --pack snapshot          # auto -> 000858.SZ
  uv run pack.py --ticker 0700 --pack snapshot            # auto -> 0700.HK
  uv run pack.py --ticker 600519.SS --pack comps-multiples
  uv run pack.py --pack regime-pack
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# NBS preset list (21 indicators across 9 groups — see SKILL.md)
NBS_PRESETS = [
    # inflation
    "cpi-yoy", "core-cpi", "ppi-yoy",
    # growth
    "gdp-yoy", "industrial-yoy", "retail-yoy", "fai-yoy",
    # trade
    "exports-yoy", "imports-yoy", "trade-balance",
    # labor
    "urban-unemployment",
    # pmi (NBS official)
    "pmi-manufacturing", "pmi-non-manufacturing", "pmi-composite",
    # money
    "m2-yoy", "m1-yoy",
    # realestate
    "realestate-investment-yoy", "housing-sales-area-yoy",
    "housing-sales-value-yoy", "realestate-funding-yoy",
    # services
    "services-production-yoy",
]

# akshare preset list (8 indicators: PBOC rates + credit + Caixin PMI)
AKSHARE_PRESETS = [
    "lpr-1y", "lpr-5y", "rrr-major", "shibor-3m",
    "shrzgm", "new-loans",
    "caixin-mfg-pmi", "caixin-svc-pmi",
]

# FRED series for CN cross-rate + FX reserves
FRED_SERIES = ["DEXCHUS", "TRESEGCNM052N"]

# Macro market indices (overlay, optional in regime-pack)
MARKET_TICKERS = ["000300.SS", "000001.SS", "399006.SZ", "^HSI", "^HSCE"]


# ---------------------------------------------------------------------------
# Ticker normalisation (.SS / .SZ / .HK auto-suffix)
# ---------------------------------------------------------------------------

def _normalise_ticker(t: str) -> str:
    """Append exchange suffix if a bare numeric code is passed.

    Heuristic (CN/HK convention):
      - already has '.' suffix     -> unchanged
      - starts with '6' or '9' (6-digit) -> .SS  (Shanghai: 600/601/603/605/688/900)
      - starts with '0', '2', '3' (6-digit) -> .SZ  (Shenzhen: 000/002/300/301)
      - 4 digits (e.g. '0700', '9988') -> .HK  (Hong Kong)
      - 5 digits (e.g. '09988', '02318', '03690') -> .HK  (Hong Kong, leading-zero form)
      - otherwise unchanged + stderr warning. BSE (北京证券交易所, 4xx/8xx)
        and other unsupported formats fall through unchanged.
    """
    t = t.strip().upper()
    if "." in t or t.startswith("^"):
        return t
    if not t.isdigit():
        return t
    if len(t) == 4:
        return f"{t}.HK"
    if len(t) == 5:
        return f"{t}.HK"
    if len(t) == 6:
        first = t[0]
        if first in ("6", "9"):
            return f"{t}.SS"
        if first in ("0", "2", "3"):
            return f"{t}.SZ"
        # 6-digit BSE codes start with 4 or 8 (e.g. 430xxx, 830xxx, 870xxx) —
        # yfinance does not cover BSE; warn and pass through.
        if first in ("4", "8"):
            print(
                f"WARNING: BSE ticker '{t}' detected — yfinance does not cover "
                "Beijing Stock Exchange (北京证券交易所); pack will likely fail. "
                "BSE primary-source disclosure is not in v2.0.0 scope.",
                file=sys.stderr,
            )
            return t
    print(
        f"WARNING: Unrecognized CN ticker format: '{t}' "
        "(expected 4-digit HK / 5-digit HK / 6-digit SSE/SZSE). "
        "Passing through unchanged — yfinance may fail.",
        file=sys.stderr,
    )
    return t


def _normalise_ticker_list(csv: str) -> list[str]:
    return [_normalise_ticker(t) for t in csv.split(",") if t.strip()]


# ---------------------------------------------------------------------------
# Subprocess helper
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> dict:
    """Run a client script and return parsed JSON (or error dict)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False,
        )
    except FileNotFoundError as e:
        return {"_error": f"command not found: {e}", "_cmd": " ".join(cmd)}

    if result.returncode != 0 and not result.stdout.strip():
        return {
            "_error": f"client exited rc={result.returncode}",
            "_cmd": " ".join(cmd),
            "_stderr": result.stderr.strip()[-500:],
        }

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return {
            "_error": f"invalid JSON from client: {e}",
            "_cmd": " ".join(cmd),
            "_stdout_head": result.stdout[:500],
            "_stderr": result.stderr.strip()[-500:],
        }


def _yf(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "yfinance_client.py"), *args])


def _nbs(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "nbs_client.py"), *args])


def _akshare(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "akshare_client.py"), *args])


def _fred(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "fred_client.py"), *args])


# ---------------------------------------------------------------------------
# Pack builders
# ---------------------------------------------------------------------------

_YF_LABEL_MAP = {
    # yfinance row label → canonical field
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


def _build_canonical_from_yf_financials(financials: dict) -> dict:
    """T3 (yfinance Tier 2 fallback) — extract canonical statements from
    yfinance --action financials annual output. Per ADR-0003.
    Most-recent-first ordering, annual depth 5.
    """
    if not isinstance(financials, dict):
        financials = {}
    income = financials.get("income_statement") or {}
    balance = financials.get("balance_sheet") or {}
    cashflow = financials.get("cash_flow") or {}
    periods = sorted(set(income) | set(balance) | set(cashflow), reverse=True)[:5]

    def _extract(src: dict, canonical: str) -> tuple[list[float], str | None]:
        labels = _YF_LABEL_MAP.get(canonical, [])
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
            "source_labels_tried": _YF_LABEL_MAP.get(canonical, []),
            "fiscal_year_ends": periods_used[: len(periods_used)],
            "accounting_standard": "cas",  # China Accounting Standards (converged-with-IFRS)
            "unit": "CNY",
            "tier": "Tier 2 (yfinance scraper — cninfo/HKEXnews deferred)",
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


def pack_snapshot(ticker: str) -> dict:
    """Quick overview: yfinance info + 6mo price history."""
    t = _normalise_ticker(ticker)
    yfinance_history = _yf(["--ticker", t, "--action", "history",
                            "--period", "6mo", "--interval", "1d"])
    rows = yfinance_history.get("data", []) if isinstance(yfinance_history, dict) else []
    return {
        "pack": "snapshot",
        "ticker": t,
        "country": "CN",
        "yfinance_info": _yf(["--ticker", t, "--action", "info"]),
        "yfinance_history": yfinance_history,  # raw envelope per Principle 1
        "history": rows,  # T1 canonical OHLCV alias (cross-country symmetric)
    }


def pack_memo_fetch(ticker: str) -> dict:
    """Memo data. Tier 2 only — CN primary-source individual-stock
    disclosure (e.g. CSRC-mandated annual reports via cninfo) is not
    yet integrated; yfinance financials is the current floor."""
    t = _normalise_ticker(ticker)
    info = _yf(["--ticker", t, "--action", "info"])
    yfinance_history = _yf(["--ticker", t, "--action", "history",
                            "--period", "2y", "--interval", "1d"])
    fin_annual = _yf(["--ticker", t, "--action", "financials", "--period", "annual"])
    fin_quarterly = _yf(["--ticker", t, "--action", "financials", "--period", "quarterly"])
    rows = yfinance_history.get("data", []) if isinstance(yfinance_history, dict) else []
    canonical = _build_canonical_from_yf_financials(fin_annual)
    info_dict = info if isinstance(info, dict) else {}
    return {
        "pack": "memo-fetch",
        "ticker": t,
        "country": "CN",
        "_provenance": {
            "tier": 2,
            "tier_reason": ("CN primary-source individual-stock disclosure "
                            "not in v2.0.0 scope"),
            "primary_source_status": "deferred",
            "primary_source_candidates": ["cninfo (CSRC)", "HKEXnews"],
        },
        "tier_note": ("Tier 2 only — CN primary-source individual-stock "
                      "disclosure (cninfo / HKEXnews) not in v2.0.0 scope. "
                      "yfinance financials is the current floor."),
        "yfinance_info": info,
        "yfinance_history": yfinance_history,  # raw envelope
        "history": rows,  # T1 canonical OHLCV alias
        "yfinance_financials_annual": fin_annual,  # raw per Principle 1
        "yfinance_financials_quarterly": fin_quarterly,
        # T3 canonical staging (Tier 2 yfinance fallback per ADR-0003)
        "income_statement": canonical["income_statement"],
        "cash_flow": canonical["cash_flow"],
        "balance_sheet": canonical["balance_sheet"],
        "shares_outstanding": info_dict.get("sharesOutstanding"),
        "current_price": info_dict.get("regularMarketPrice"),
        "cn_specific": {
            "primary_source_note": "cninfo (CSRC-mandated annual reports) / HKEXnews integration deferred. All canonical financials are yfinance Tier 2 (CAS / converged-IFRS via Yahoo). CNY for A-shares, HKD for .HK tickers.",
            "consolidated_basis_note": "yfinance reports consolidated (合并) statements. Parent-only (母公司) and segment data not exposed; needs cninfo for full granularity.",
        },
    }


def pack_comps_multiples_single(ticker: str) -> dict:
    """Multiples for one ticker. Used as anchor or per-peer in
    analysis-comps."""
    t = _normalise_ticker(ticker)
    info = _yf(["--ticker", t, "--action", "info"])
    multiples = {}
    # yfinance_client emits info fields at top level of the result dict.
    if isinstance(info, dict):
        for k in ("trailingPE", "forwardPE", "enterpriseToEbitda",
                  "priceToSalesTrailing12Months", "priceToBook"):
            v = info.get(k)
            if v is not None:
                multiples[k] = v
    return {
        "ticker": t,
        "country": "CN",
        "multiples": multiples,
        "_yfinance_info": info,
        # T1 canonical alias: analysis-comps reads pack.info[ticker]
        "info": {t: multiples} if multiples else {},
    }


def pack_comps_multiples_batch(tickers: list[str]) -> dict:
    """Multiples for a list. analysis-comps consumes anchor + peers."""
    out = []
    info_dict: dict = {}
    for t in tickers:
        single = pack_comps_multiples_single(t)
        out.append(single)
        if single.get("multiples"):
            info_dict[single["ticker"]] = single["multiples"]
    return {
        "pack": "comps-multiples",
        "country": "CN",
        "tickers": out,
        "info": info_dict,  # T1 canonical multiples alias (cross-country symmetric)
    }


def pack_screener_batch(tickers: list[str]) -> dict:
    """Lightweight batch fetch via yfinance batch mode.

    Note: tickers are expected to be already normalised by the CLI dispatch
    (mirrors comps-multiples pattern); this function is a no-op on
    already-normalised input.
    """
    csv = ",".join(tickers)
    return {
        "pack": "screener-batch",
        "country": "CN",
        "tickers": tickers,
        "yfinance_info_batch": _yf(["--tickers", csv, "--action", "info"]),
        "yfinance_history_batch": _yf(["--tickers", csv, "--action", "history",
                                       "--period", "6mo", "--interval", "1d"]),
    }


def pack_regime_pack() -> dict:
    """Macro regime data: NBS (21) + akshare PBOC/Caixin (8) + FRED USDCNY."""
    nbs = _nbs(["--preset", ",".join(NBS_PRESETS)])
    akshare = _akshare(["--preset", ",".join(AKSHARE_PRESETS)])
    fred = _fred(["--series", ",".join(FRED_SERIES), "--periods", "24"])
    markets = _yf(["--tickers", ",".join(MARKET_TICKERS),
                   "--action", "history", "--period", "1y", "--interval", "1d"])
    return {
        "pack": "regime-pack",
        "country": "CN",
        "nbs": nbs,
        "akshare": akshare,
        "fred": fred,
        "markets": markets,
        "_provenance": {
            "nbs_indicators": NBS_PRESETS,
            "akshare_indicators": AKSHARE_PRESETS,
            "fred_series": FRED_SERIES,
            "market_tickers": MARKET_TICKERS,
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="data-cn pack facade (Layer 1 — China)",
    )
    parser.add_argument("--pack", required=True,
                        choices=["snapshot", "memo-fetch", "comps-multiples",
                                 "screener-batch", "regime-pack"],
                        help="Pack type")
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--ticker", help="Single ticker (e.g. 600519.SS, 000858.SZ, 0700.HK; "
                                     "bare 6-digit / 4-digit codes auto-suffix)")
    grp.add_argument("--tickers", help="Comma-separated tickers for batch mode")

    args = parser.parse_args()

    if args.pack == "regime-pack":
        out = pack_regime_pack()
    elif args.pack == "snapshot":
        if not args.ticker:
            parser.error("--pack snapshot requires --ticker")
        out = pack_snapshot(args.ticker)
    elif args.pack == "memo-fetch":
        if not args.ticker:
            parser.error("--pack memo-fetch requires --ticker (single only — N=1)")
        out = pack_memo_fetch(args.ticker)
    elif args.pack == "comps-multiples":
        if args.tickers:
            out = pack_comps_multiples_batch(_normalise_ticker_list(args.tickers))
        elif args.ticker:
            out = {
                "pack": "comps-multiples",
                "country": "CN",
                "tickers": [pack_comps_multiples_single(args.ticker)],
            }
        else:
            parser.error("--pack comps-multiples requires --ticker or --tickers")
    elif args.pack == "screener-batch":
        if not args.tickers:
            parser.error("--pack screener-batch requires --tickers")
        out = pack_screener_batch(_normalise_ticker_list(args.tickers))
    else:
        parser.error(f"unhandled pack: {args.pack}")

    print(json.dumps(out, default=str, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
