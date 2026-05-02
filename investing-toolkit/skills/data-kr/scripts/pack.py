#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
pack.py — data-kr Layer 1 facade for Korea (KOSPI / KOSDAQ + macro)

Composes underlying clients into pack-typed bundles (Anthropic v2.0.0
three-layer convention). Stock-side is yfinance only (Tier 2) — Korea has
no primary-source equity client wired in this skill yet (DART deferred).
Regime-pack pulls BOK ECOS-KEYSTAT via FinanceDataReader.

Pack types:
  --pack snapshot          (single ticker; yfinance info + price summary)
  --pack memo-fetch        (single ticker; yfinance financials, Tier 2 only)
  --pack comps-multiples   (single or batch; multiples-only)
  --pack screener-batch    (batch; lightweight screening fields)
  --pack regime-pack       (no ticker; BOK ECOS-KEYSTAT 54-indicator pull)

Usage:
  pack.py --ticker 005930.KS --pack snapshot
  pack.py --ticker 005930   --pack snapshot          # auto-suffix .KS
  pack.py --tickers 005930.KS,000660.KS --pack screener-batch
  pack.py --pack regime-pack
  pack.py --pack regime-pack --indicators rates,inflation

Suffix convention:
  .KS = KOSPI (Korea Stock Exchange — large cap)
  .KQ = KOSDAQ

Auto-suffix rule for tickers:
  - 6-digit numeric ticker without suffix → append .KS by default
  - Tickers already ending in .KS or .KQ pass through unchanged
  - Use --kosdaq flag to force .KQ for ambiguous numeric tickers

Cache: $INVESTING_TOOLKIT_CACHE (inherited from underlying clients)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
YFINANCE = SCRIPT_DIR / "yfinance_client.py"
FDR = SCRIPT_DIR / "fdr_client.py"

# Macro indicator groups (regime-pack) — mirrors korea-macro SKILL.md.
REGIME_GROUPS: dict[str, list[str]] = {
    "rates": [
        "policy-rate", "call-rate", "cd-91d", "koribor-3m",
        "treasury-3y", "treasury-5y", "corp-bond-3y",
    ],
    "inflation": ["cpi", "core-cpi", "ppi", "import-pi", "export-pi"],
    "growth": [
        "gdp-qoq", "gdp-nominal", "ipi", "manufacturing",
        "private-consumption", "equipment-investment", "construction-investment",
    ],
    "industry": [
        "manufacturing-inventory", "manufacturing-shipment",
        "manufacturing-operating-rate", "services-production",
        "retail-sales", "wholesale-retail", "credit-card-usage",
        "machinery-orders", "capital-goods-output",
        "construction-completion", "construction-orders",
    ],
    "labor": ["unemployment", "employment-rate"],
    "trade": ["current-account", "terms-of-trade", "goods-exports"],
    "money": ["m1", "m2", "lf", "household-credit"],
    "sentiment": ["consumer-sentiment", "economic-sentiment"],
    "cycle": ["leading-cycle", "coincident-cycle"],
    "markets": ["kospi", "kosdaq"],
    "fx": ["krw-usd", "krw-jpy", "krw-eur", "krw-cny", "fx-reserves"],
    "realestate": ["housing-price"],
    "demographics": ["population", "aging-ratio", "fertility-rate"],
}

# Lightweight fields for screener-batch (info action returns rich dict; we
# do not subset here — analysis-screener will project. Spec calls for
# "lightweight fields"; yfinance info is already the lightweight surface.)


# ---------------------------------------------------------------------------
# Ticker normalization (.KS / .KQ auto-suffix)
# ---------------------------------------------------------------------------

# Module-level collector for ticker-normalization warnings. Each call to
# normalize_ticker may append a string here; pack functions surface this
# under _provenance.ticker_normalization_warnings so consumers can audit.
TICKER_NORMALIZATION_WARNINGS: list[str] = []


def normalize_ticker(ticker: str, force_kosdaq: bool = False) -> str:
    """Append .KS (or .KQ if --kosdaq) to bare 6-digit numeric tickers.

    Edge-case handling:
      - 6-digit numeric: auto-suffix .KS (or .KQ with --kosdaq).
      - Already-suffixed (.KS / .KQ): pass through.
      - Bare numeric of any other length (e.g. 4/5/7-digit typo or
        leading-zero strip): pass through unchanged but warn to stderr
        and record under TICKER_NORMALIZATION_WARNINGS.
      - Non-numeric, non-suffixed token: pass through unchanged but warn.
    """
    t = ticker.strip().upper()
    if t.endswith(".KS") or t.endswith(".KQ"):
        return t
    # Bare 6-digit Korean ticker code (e.g. 005930)
    if t.isdigit() and len(t) == 6:
        return f"{t}.KQ" if force_kosdaq else f"{t}.KS"
    # Edge cases: bare numeric of wrong length, or non-numeric token.
    msg = (
        f"Unrecognized KR ticker format: '{ticker}' — expected 6-digit "
        f"(.KS auto-append) or explicit .KS/.KQ suffix; passing through "
        f"unchanged (yfinance lookup will likely fail)."
    )
    print(f"[data-kr WARN] {msg}", file=sys.stderr)
    TICKER_NORMALIZATION_WARNINGS.append(msg)
    return t


def normalize_tickers(tickers: str, force_kosdaq: bool = False) -> str:
    return ",".join(
        normalize_ticker(t, force_kosdaq) for t in tickers.split(",") if t.strip()
    )


def _consume_ticker_warnings() -> list[str]:
    """Drain and return the current ticker-normalization warning list."""
    out = list(TICKER_NORMALIZATION_WARNINGS)
    TICKER_NORMALIZATION_WARNINGS.clear()
    return out


# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> dict:
    """Invoke a client script via uv run, parse stdout JSON, propagate errors."""
    full = ["uv", "run", str(cmd[0])] + cmd[1:]
    try:
        proc = subprocess.run(
            full, capture_output=True, text=True, check=False,
            env=os.environ.copy(),
        )
    except FileNotFoundError as e:
        return {"error": f"uv not found: {e}", "_partial": True}

    out = proc.stdout.strip()
    if not out:
        return {
            "error": f"empty stdout from {cmd[0]}",
            "stderr": proc.stderr[-2000:],
            "returncode": proc.returncode,
            "_partial": True,
        }
    try:
        data = json.loads(out)
    except json.JSONDecodeError as e:
        return {
            "error": f"invalid JSON from {cmd[0]}: {e}",
            "stdout_tail": out[-2000:],
            "stderr": proc.stderr[-2000:],
            "returncode": proc.returncode,
            "_partial": True,
        }
    if proc.returncode != 0 and "error" not in data:
        data["_returncode"] = proc.returncode
    return data


# ---------------------------------------------------------------------------
# Pack implementations
# ---------------------------------------------------------------------------

def pack_snapshot(ticker: str) -> dict:
    """yfinance info + 1y price history — quick overview card."""
    info = _run([str(YFINANCE), "--ticker", ticker, "--action", "info"])
    history = _run([str(YFINANCE), "--ticker", ticker, "--action", "history",
                    "--period", "1y"])
    provenance: dict = {
        "tier": "Tier 2 (yfinance unofficial)",
        "primary_source_status": "deferred",
        "primary_source_note": (
            "Korea has no primary-source equity client wired in data-kr "
            "yet. Tier A would be DART (전자공시시스템, dart.fss.or.kr) — "
            "integration deferred to a future minor version. Snapshot "
            "fields are yfinance-derived (Tier 2)."
        ),
        "exchange_suffix": ticker.split(".")[-1] if "." in ticker else None,
    }
    warnings = _consume_ticker_warnings()
    if warnings:
        provenance["ticker_normalization_warnings"] = warnings
    rows = history.get("data", []) if isinstance(history, dict) else []
    return {
        "pack": "snapshot",
        "country": "kr",
        "ticker": ticker,
        "info": info,
        "price_history": history,  # raw envelope per Principle 1
        "history": rows,  # T1 canonical OHLCV alias (cross-country symmetric with data-us)
        "_provenance": provenance,
    }


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
    yfinance --action financials annual output. Returns income_statement,
    cash_flow, balance_sheet blocks with `_meta` tracking which raw label
    supplied each value (per ADR-0003 + normalization-contract.md).

    Most-recent-first ordering (matches analysis-dcf input contract).
    Annual depth limited to 5 periods.
    """
    if not isinstance(financials, dict):
        financials = {}
    income = financials.get("income_statement") or {}
    balance = financials.get("balance_sheet") or {}
    cashflow = financials.get("cash_flow") or {}

    # Sort periods most-recent-first, cap at 5
    periods = sorted(
        set(income) | set(balance) | set(cashflow), reverse=True,
    )[:5]

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

    # capex from yfinance is signed negative (cash outflow); take abs for canonical
    capex = [abs(v) for v in capex_raw]

    # Prefer reported total_debt; else sum LTD + STD
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
            "accounting_standard": "k_ifrs",
            "unit": "KRW",
            "tier": "Tier 2 (yfinance scraper — DART deferred)",
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
                "capex": {**_meta("capex", capex_label, periods[: len(capex)]), "note": "absolute value (yfinance reports as negative cash outflow)"},
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
                        "components": {
                            "long_term_debt": ltd_label,
                            "short_term_debt": std_label,
                        },
                    }
                ),
                "cash": _meta("cash_and_equivalents", cash_label, periods[: len(cash)]),
            },
        },
    }


def pack_memo_fetch(ticker: str) -> dict:
    """yfinance financials only. Korean primary-source (DART) deferred."""
    info = _run([str(YFINANCE), "--ticker", ticker, "--action", "info"])
    financials_annual = _run([str(YFINANCE), "--ticker", ticker,
                              "--action", "financials", "--period", "annual"])
    financials_quarterly = _run([str(YFINANCE), "--ticker", ticker,
                                 "--action", "financials", "--period", "quarterly"])
    history = _run([str(YFINANCE), "--ticker", ticker, "--action", "history",
                    "--period", "5y"])
    provenance: dict = {
        "tier": "Tier 2 (yfinance unofficial)",
        "primary_source_status": "deferred",
        "primary_source_note": (
            "Korea has no primary-source equity client wired in data-kr "
            "yet. Tier A would be DART (전자공시시스템, "
            "dart.fss.or.kr) — integration deferred to a future minor "
            "version. Treat all financials below as unverified scraper output."
        ),
    }
    warnings = _consume_ticker_warnings()
    if warnings:
        provenance["ticker_normalization_warnings"] = warnings
    canonical = _build_canonical_from_yf_financials(financials_annual)
    info_dict = info if isinstance(info, dict) else {}
    rows = history.get("data", []) if isinstance(history, dict) else []
    return {
        "pack": "memo-fetch",
        "country": "kr",
        "ticker": ticker,
        "tier": "Tier 2 only",
        "info": info,
        "financials_annual": financials_annual,
        "financials_quarterly": financials_quarterly,
        "price_history": history,  # raw envelope per Principle 1
        "history": rows,  # T1 canonical OHLCV alias
        # T3 canonical (Tier 2 yfinance fallback per ADR-0003)
        "income_statement": canonical["income_statement"],
        "cash_flow": canonical["cash_flow"],
        "balance_sheet": canonical["balance_sheet"],
        "shares_outstanding": info_dict.get("sharesOutstanding"),
        "current_price": info_dict.get("regularMarketPrice"),
        "kr_specific": {
            "primary_source_note": "DART (전자공시시스템, dart.fss.or.kr) integration deferred. All canonical financials are yfinance Tier 2 (K-IFRS via Yahoo). KRW figures.",
            "consolidated_basis_note": "yfinance reports Korean issuers' consolidated (연결) statements by default. 별도 statements not exposed; needs DART for non-consolidated.",
        },
        "_provenance": provenance,
    }


def pack_comps_multiples(tickers: list[str]) -> dict:
    """Multiples-only fetch for anchor + peers. Single or batch.

    Schema is normalized: regardless of single or batch, the result always
    exposes `info` keyed by ticker so analysis-comps consumes one shape:
        {"info": {"005930.KS": {...}, "000660.KS": {...}}}
    """
    if len(tickers) == 1:
        single = _run([str(YFINANCE), "--ticker", tickers[0], "--action", "info"])
        info_by_ticker: dict = {tickers[0]: single}
    else:
        batch = _run([str(YFINANCE), "--tickers", ",".join(tickers),
                      "--action", "info"])
        # yfinance_client batch shape (canonical):
        #   {"mode": "batch", "action": "info", "tickers": {ticker: {...}}, ...}
        # We extract the inner per-ticker dict so consumers always see
        # `info: {ticker: {...}}` regardless of single vs batch.
        if (
            isinstance(batch, dict)
            and isinstance(batch.get("tickers"), dict)
        ):
            info_by_ticker = batch["tickers"]
        elif isinstance(batch, dict) and "results" in batch and isinstance(
            batch["results"], dict
        ):
            info_by_ticker = batch["results"]
        else:
            # Fallback: wrap whole payload under a sentinel so consumer can
            # still inspect it; analysis-comps will treat as partial.
            info_by_ticker = {"_batch_unparsed": batch}
    result: dict = {
        "pack": "comps-multiples",
        "country": "kr",
        "tickers": tickers,
        "info": info_by_ticker,
    }
    provenance: dict = {
        "tier": "Tier 2 (yfinance unofficial)",
        "primary_source_status": "deferred",
        "primary_source_note": (
            "Korea multiples are yfinance-derived. DART (전자공시시스템) "
            "integration deferred. Multiples extraction is downstream "
            "(analysis-comps)."
        ),
        "multiples_set": ["trailingPE", "forwardPE", "evEbitda",
                          "priceToSales", "priceToBook"],
    }
    warnings = _consume_ticker_warnings()
    if warnings:
        provenance["ticker_normalization_warnings"] = warnings
    result["_provenance"] = provenance
    return result


def pack_screener_batch(tickers: list[str]) -> dict:
    """Batch info pull for screener (lightweight fields)."""
    batch = _run([str(YFINANCE), "--tickers", ",".join(tickers),
                  "--action", "info"])
    provenance: dict = {
        "tier": "Tier 2 (yfinance unofficial)",
        "primary_source_status": "deferred",
        "primary_source_note": (
            "Screener batch is yfinance-derived. DART (전자공시시스템) "
            "integration deferred."
        ),
        "ticker_count": len(tickers),
    }
    warnings = _consume_ticker_warnings()
    if warnings:
        provenance["ticker_normalization_warnings"] = warnings
    return {
        "pack": "screener-batch",
        "country": "kr",
        "tickers": tickers,
        "batch": batch,
        "_provenance": provenance,
    }


def _flatten_regime_to_series(root: dict) -> dict:
    """T2 canonical (per ADR-0002) — walk a regime-pack root and emit a flat
    `series: {indicator_id: [floats]}` block for downstream
    analysis-macro-regime / regime_compose.resolve_series().

    Walks any nested dict structure, treats nodes with `observations: [{date, value}]`
    as leaves. Keys observations by leaf's `preset` field (preferred), falling
    back to `series` (when string) or deepest path component.

    Also emits group-prefixed keys (e.g. `inflation.cpi-yoy` alongside `cpi-yoy`)
    so that `resolve_series` chains like `["inflation.cpi-yoy", "cpi-yoy"]` find
    a hit regardless of preferred form. Skips keys starting with `_`.
    """
    flat: dict[str, list[float]] = {}

    def _values_from_observations(obs_list: list) -> list[float]:
        out: list[float] = []
        for o in obs_list:
            if isinstance(o, dict) and o.get("value") is not None:
                try:
                    out.append(float(o["value"]))
                except (TypeError, ValueError):
                    pass
        return out

    def visit(node, path):
        if not isinstance(node, dict):
            return
        obs = node.get("observations")
        if isinstance(obs, list):
            values = _values_from_observations(obs)
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


def pack_regime_pack(indicators: str) -> dict:
    """Macro-regime pull via fdr_client → BOK ECOS-KEYSTAT (54 indicators)."""
    if indicators == "all":
        groups = list(REGIME_GROUPS.keys())
    else:
        groups = [g.strip() for g in indicators.split(",") if g.strip()]
        unknown = [g for g in groups if g not in REGIME_GROUPS]
        if unknown:
            return {
                "error": f"unknown indicator group(s): {unknown}",
                "available": list(REGIME_GROUPS.keys()),
                "_partial": True,
            }

    by_group: dict[str, dict] = {}
    for grp in groups:
        presets = REGIME_GROUPS[grp]
        result = _run([str(FDR), "--preset", ",".join(presets)])
        by_group[grp] = result

    series_flat = _flatten_regime_to_series(by_group)
    return {
        "pack": "regime-pack",
        "country": "kr",
        "groups_requested": groups,
        "data": by_group,
        "series": series_flat,  # T2 canonical flat alias per ADR-0002
        "_provenance": {
            "primary_source_status": "available",
            "primary_source_note": (
                "BOK ECOS-KEYSTAT via FinanceDataReader (Tier A primary). "
                "Secondary fallback: FRED (krw-usd only — DEXKOUS)."
            ),
            "indicator_count_total": sum(len(v) for k, v in REGIME_GROUPS.items()
                                         if k in groups),
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="data-kr pack facade — Korea (KOSPI/KOSDAQ + macro)",
    )
    ticker_group = parser.add_mutually_exclusive_group(required=False)
    ticker_group.add_argument("--ticker", help="Single ticker (e.g. 005930.KS)")
    ticker_group.add_argument("--tickers",
                              help="Comma-separated tickers (e.g. 005930.KS,000660.KS)")
    parser.add_argument("--pack", required=True,
                        choices=["snapshot", "memo-fetch", "comps-multiples",
                                 "screener-batch", "regime-pack"],
                        help="Pack type")
    parser.add_argument("--indicators", default="all",
                        help="(regime-pack only) Comma-separated groups or 'all'")
    parser.add_argument("--kosdaq", action="store_true",
                        help="Treat bare numeric tickers as KOSDAQ (.KQ) instead of KOSPI (.KS)")

    args = parser.parse_args()

    # Validate ticker presence per pack type
    if args.pack in {"snapshot", "memo-fetch"}:
        if not args.ticker:
            parser.error(f"--pack {args.pack} requires --ticker")
        ticker = normalize_ticker(args.ticker, args.kosdaq)
        if args.pack == "snapshot":
            out = pack_snapshot(ticker)
        else:
            out = pack_memo_fetch(ticker)

    elif args.pack == "comps-multiples":
        if not (args.ticker or args.tickers):
            parser.error("--pack comps-multiples requires --ticker or --tickers")
        raw = args.tickers if args.tickers else args.ticker
        tickers = [normalize_ticker(t, args.kosdaq)
                   for t in raw.split(",") if t.strip()]
        out = pack_comps_multiples(tickers)

    elif args.pack == "screener-batch":
        if not args.tickers:
            parser.error("--pack screener-batch requires --tickers")
        tickers = [normalize_ticker(t, args.kosdaq)
                   for t in args.tickers.split(",") if t.strip()]
        out = pack_screener_batch(tickers)

    elif args.pack == "regime-pack":
        out = pack_regime_pack(args.indicators)

    else:
        parser.error(f"unsupported pack: {args.pack}")
        return

    print(json.dumps(out, default=str, indent=2))
    if isinstance(out, dict) and out.get("_partial"):
        sys.exit(1)


if __name__ == "__main__":
    main()
