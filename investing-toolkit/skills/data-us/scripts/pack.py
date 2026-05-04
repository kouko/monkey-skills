#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
pack.py — investing-toolkit data-us facade

Composes multi-source US data pulls (yfinance + SEC EDGAR + FRED) into
structured JSON bundles. Pure I/O / fetch layer — no analysis.

Pack types:
  - snapshot         single ticker, yfinance info + 2y price
  - memo-fetch       single ticker, yfinance + SEC EDGAR (10-K/10-Q/8-K + facts)
  - comps-multiples  single OR batch, yfinance multiples-only fields
  - screener-batch   batch, yfinance lightweight fields (REQUIRES --tickers)
  - regime-pack      no ticker dimension, FRED macro series only

Usage:
  uv run pack.py --ticker AAPL --pack snapshot
  uv run pack.py --ticker NVDA --pack memo-fetch
  uv run pack.py --ticker AAPL --pack comps-multiples
  uv run pack.py --tickers AAPL,MSFT,GOOGL --pack comps-multiples
  uv run pack.py --tickers AAPL,MSFT,GOOGL,META,AMZN --pack screener-batch
  uv run pack.py --pack regime-pack

Environment:
  INVESTING_TOOLKIT_CACHE   passed through to underlying clients (yfinance / sec / fred)

Output: JSON to stdout. Exit 0 on success, non-zero on argparse / shell-out error.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
YF = SCRIPT_DIR / "yfinance_client.py"
SEC = SCRIPT_DIR / "sec_edgar_client.py"
FRED = SCRIPT_DIR / "fred_client.py"


# ---------------------------------------------------------------------------
# Multiples + screener field whitelists
# ---------------------------------------------------------------------------

MULTIPLES_FIELDS = [
    "trailingPE",
    "forwardPE",
    "priceToSales",
    "priceToBook",
    "enterpriseToEbitda",
    "enterpriseToRevenue",
    "marketCap",
    "enterpriseValue",
]

SCREENER_FIELDS = [
    "trailingPE",
    "priceToBook",
    "marketCap",
    "dividendYield",
    "beta",
    "fiftyTwoWeekHigh",
    "fiftyTwoWeekLow",
    "regularMarketPrice",
    "sector",
    "industry",
    "shortName",
]


# ---------------------------------------------------------------------------
# Default FRED series for regime-pack (mirror us-macro core groups)
# ---------------------------------------------------------------------------

REGIME_SERIES_GROUPS = {
    "rates":         ("T10Y2Y,DGS10,DGS2,FEDFUNDS",          24),
    "inflation":     ("CPIAUCSL,CPILFESL",                    24),
    "growth":        ("GDPC1,INDPRO",                         12),
    "nowcast":       ("GDPNOW,CFNAI,USALOLITOAASTSAM",        24),
    "wei":           ("WEI",                                  52),
    "real_rates":    ("T5YIE,T10YIE,DFII5,DFII10",            24),
    "swap_spreads":  ("DGS3MO,SOFR30DAYAVG",                  24),
}


# ---------------------------------------------------------------------------
# T3 DCF concept mapping — see ADR-0003
# Each canonical field maps to an ordered list of us-gaap concept names
# (fallback chain). First non-empty wins; provenance recorded in _meta.
# ---------------------------------------------------------------------------

DCF_CONCEPT_MAPPING: dict[str, list[str]] = {
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenue",
        "SalesRevenueNet",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
    ],
    "net_income": [
        "NetIncomeLoss",
        "ProfitLoss",
    ],
    "gross_profit": [
        "GrossProfit",
    ],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
    ],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ],
    "depreciation_amortization": [
        "DepreciationDepletionAndAmortization",
        "DepreciationAndAmortization",
        "Depreciation",
    ],
    "stock_based_compensation": [
        "ShareBasedCompensation",
        "AllocatedShareBasedCompensationExpense",
    ],
    "long_term_debt": [
        "LongTermDebt",
        "LongTermDebtNoncurrent",
    ],
    "short_term_debt": [
        "DebtCurrent",
        "ShortTermBorrowings",
    ],
    "cash_and_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue",
        "Cash",
    ],
    "total_stockholders_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "intangible_assets": [
        "IntangibleAssetsNetExcludingGoodwill",
        "FiniteLivedIntangibleAssetsNet",
        "IntangibleAssetsNet",
    ],
    "goodwill": [
        "Goodwill",
    ],
}

T3_ANNUAL_DEPTH = 5


# ---------------------------------------------------------------------------
# Subprocess helper — invoke a client script with current env
# ---------------------------------------------------------------------------

CLIENT_TIMEOUT_SECONDS = 300


def run_client(script: Path, extra_args: list[str], timeout: int = CLIENT_TIMEOUT_SECONDS) -> dict:
    """Run a client script with `uv run`, return parsed JSON.

    Returns a structured error dict on non-zero exit, JSON parse failure, or timeout.
    """
    cmd = ["uv", "run", str(script)] + extra_args
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "error": f"client timeout after {timeout}s",
            "_cmd": cmd,
            "_returncode": -1,
        }
    if proc.returncode != 0:
        return {
            "error": "client_failed",
            "script": script.name,
            "args": extra_args,
            "returncode": proc.returncode,
            "stderr": proc.stderr.strip()[-2000:],
        }
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return {
            "error": "invalid_json",
            "script": script.name,
            "args": extra_args,
            "detail": str(e),
            "stdout_head": proc.stdout[:500],
        }


def filter_fields(info_obj: dict, fields: list[str]) -> dict:
    """Return only whitelisted fields from an info dict (preserve missing as None)."""
    if not isinstance(info_obj, dict):
        return {}
    out = {f: info_obj.get(f) for f in fields}
    # Preserve identifying / provenance keys if present
    for k in ("ticker", "_provenance", "error"):
        if k in info_obj:
            out[k] = info_obj[k]
    return out


# ---------------------------------------------------------------------------
# Pack implementations
# ---------------------------------------------------------------------------

def pack_snapshot(ticker: str) -> dict:
    """yfinance info + 2y price for a single ticker."""
    info = run_client(YF, ["--ticker", ticker, "--action", "info"])
    history = run_client(YF, ["--ticker", ticker, "--period", "2y"])
    rows = history.get("data", []) if isinstance(history, dict) else []
    return {
        "pack": "snapshot",
        "ticker": ticker.upper(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "company_info": info,
        "price_history": history,
        "history": rows,  # T1 canonical OHLCV alias — see docs/normalization-contract.md
    }


def _fetch_dcf_concepts(ticker: str) -> dict[str, dict]:
    """T3 Stage 1 — fetch raw XBRL time-series for ALL concepts in
    DCF_CONCEPT_MAPPING fallback chains. Returns concept-keyed dict of
    full client output (with `observations` list).

    Per ADR-0003 + Principle 1, raw output is preserved unchanged.
    Multiple chain entries are fetched (not just first non-empty) because
    issuers commonly switch concepts mid-history (e.g. Apple FY18→FY19
    switched from us-gaap:Revenues to RevenueFromContractWithCustomer...
    after ASC 606). Stage 2 (_normalize_dcf) merges per-year provenance.
    """
    raw: dict[str, dict] = {}
    seen: set[str] = set()
    for chain in DCF_CONCEPT_MAPPING.values():
        for concept in chain:
            if concept in seen:
                continue
            seen.add(concept)
            result = run_client(
                SEC,
                ["--ticker", ticker, "--action", "facts", "--concept", concept],
            )
            if isinstance(result, dict) and result.get("observations"):
                raw[concept] = result
    return raw


def _is_annual_window(obs: dict) -> bool:
    """True iff observation covers ~12 months. Apple-style 10-K filings
    include quarterly disaggregation tagged `fp: FY`; we filter those out
    by requiring (end - start) >= 350 days (allows 52-week fiscal years).

    For balance-sheet point-in-time concepts (LongTermDebt, Cash, etc.)
    `start` is None — those observations are kept (no duration check).
    """
    if obs.get("fp") != "FY":
        return False
    start = obs.get("start")
    end = obs.get("end")
    if start is None:
        # Point-in-time concept (balance sheet) — fp == FY is sufficient
        return True
    if end is None:
        return False
    try:
        from datetime import date
        s = date.fromisoformat(start)
        e = date.fromisoformat(end)
        return (e - s).days >= 350
    except (ValueError, TypeError):
        return False


def _select_annual_observations(observations: list[dict], depth: int = T3_ANNUAL_DEPTH) -> tuple[list[dict], list[str]]:
    """Filter to annual (12-month-window observations tagged fp == 'FY'),
    dedup by period end-date keeping the most-recent `filed`, sort
    end-date-desc, cap to `depth` rows. Most-recent-first per
    analysis-dcf input contract.

    Note: SEC EDGAR companyfacts returns the same fiscal year's value
    across multiple filings (retrospective 5-year history in each 10-K).
    Grouping by `end` (period end-date) ensures we keep one row per actual
    fiscal year — and the most-recent `filed` value handles 10-K/A
    amendments + restatements.

    Apple-style 10-Ks also tag quarterly disaggregation as `fp: FY` but
    with shorter (start, end) windows; `_is_annual_window` filters those.
    """
    annuals = [o for o in observations if isinstance(o, dict) and _is_annual_window(o)]
    by_end: dict[str, dict] = {}
    amendments: list[str] = []
    for o in annuals:
        end = o.get("end")
        if end is None:
            continue
        prev = by_end.get(end)
        if prev is None:
            by_end[end] = o
        else:
            prev_filed = prev.get("filed", "")
            this_filed = o.get("filed", "")
            if this_filed > prev_filed:
                # Only count as amendment if values actually differ
                if prev.get("value") != o.get("value"):
                    amendments.append(
                        f"end={end} restated: "
                        f"{prev.get('value')} ({prev.get('form')} filed {prev_filed}) "
                        f"-> {o.get('value')} ({o.get('form')} filed {this_filed})"
                    )
                by_end[end] = o
    selected = sorted(by_end.values(), key=lambda o: o.get("end", ""), reverse=True)
    return selected[:depth], amendments


def _normalize_dcf(raw_concepts: dict[str, dict]) -> dict:
    """T3 Stage 2 — transform raw concept time-series into canonical
    income_statement / cash_flow / balance_sheet blocks per ADR-0003.

    For each canonical field, MERGES annual observations across all
    chain entries (because issuers may switch concepts mid-history —
    e.g. Apple ASC 606 transition switched Revenues -> RevenueFromContract
    in FY19). Per-year provenance records which concept supplied that
    fiscal year's value.

    Most-recent-first array, depth 5. _meta tracks per-year source
    concept + fallback usage + amendments + filings.
    """
    canonical_obs: dict[str, list[dict]] = {}
    canonical_per_year_concept: dict[str, list[str]] = {}
    canonical_amendments: dict[str, list[str]] = {}
    canonical_used_concepts: dict[str, list[str]] = {}

    for canonical, chain in DCF_CONCEPT_MAPPING.items():
        # Merge annual observations across all chain entries, tagging each
        # observation with the concept name it came from. Dedup by end date
        # (most-recent `filed` wins; chain order breaks ties).
        all_annuals: list[tuple[dict, str]] = []
        for concept in chain:
            payload = raw_concepts.get(concept)
            if not payload:
                continue
            annuals_only, _ = _select_annual_observations(
                payload.get("observations") or [],
                depth=10**6,  # no cap at this stage; cap after merge
            )
            for obs in annuals_only:
                all_annuals.append((obs, concept))

        # Dedup by end-date: prefer more recent `filed`; if tied, primary
        # concept (earlier in chain) wins.
        chain_order = {c: i for i, c in enumerate(chain)}
        by_end: dict[str, tuple[dict, str]] = {}
        amendments: list[str] = []
        for obs, concept in all_annuals:
            end = obs.get("end")
            if end is None:
                continue
            existing = by_end.get(end)
            if existing is None:
                by_end[end] = (obs, concept)
                continue
            prev_obs, prev_concept = existing
            prev_filed = prev_obs.get("filed", "")
            this_filed = obs.get("filed", "")
            if (
                this_filed > prev_filed
                or (this_filed == prev_filed and chain_order.get(concept, 999) < chain_order.get(prev_concept, 999))
            ):
                if prev_obs.get("value") != obs.get("value"):
                    amendments.append(
                        f"end={end}: {prev_obs.get('value')} ({prev_concept} {prev_obs.get('form')} filed {prev_filed}) "
                        f"-> {obs.get('value')} ({concept} {obs.get('form')} filed {this_filed})"
                    )
                by_end[end] = (obs, concept)

        merged = sorted(by_end.values(), key=lambda t: t[0].get("end", ""), reverse=True)
        merged = merged[:T3_ANNUAL_DEPTH]

        canonical_obs[canonical] = [t[0] for t in merged]
        canonical_per_year_concept[canonical] = [t[1] for t in merged]
        canonical_amendments[canonical] = amendments
        canonical_used_concepts[canonical] = sorted(set(t[1] for t in merged))

    def _values(canonical: str) -> list[float]:
        return [float(o["value"]) for o in canonical_obs[canonical] if o.get("value") is not None]

    def _meta(canonical: str) -> dict:
        obs = canonical_obs[canonical]
        per_year = canonical_per_year_concept[canonical]
        used = canonical_used_concepts[canonical]
        chain = DCF_CONCEPT_MAPPING[canonical]
        primary_only = used == [chain[0]] if used else False
        return {
            # `source_concept` reflects the primary used; if multiple, signal "mixed"
            "source_concept": (
                used[0] if len(used) == 1
                else "mixed" if used
                else None
            ),
            "concepts_used": used,
            "per_year_concept": per_year,
            "fallback_used": bool(used) and not primary_only,
            "fallback_chain_tried": chain,
            "fiscal_year_ends": [o.get("end") for o in obs],
            "amendments_seen": canonical_amendments[canonical],
            "accounting_standard": "us_gaap",
            "unit": "USD",
            "filings_used": [
                f"{o.get('form')} filed {o.get('filed')}" for o in obs
            ],
        }

    canonical_source = {k: (canonical_used_concepts[k][0] if canonical_used_concepts[k] else None) for k in DCF_CONCEPT_MAPPING}

    revenue = _values("revenue")
    operating_income = _values("operating_income")
    net_income = _values("net_income")
    ocf = _values("operating_cash_flow")
    capex = _values("capex")
    # capex in XBRL is signed positive (cash outflow); align lengths to OCF
    fcf = []
    fcf_pairs = list(zip(ocf, capex))
    fcf = [o - c for o, c in fcf_pairs]
    long_term_debt = _values("long_term_debt")
    short_term_debt = _values("short_term_debt")
    # total_debt: sum LTD + STD per period (align by length, missing components → 0)
    total_debt: list[float] = []
    for i in range(max(len(long_term_debt), len(short_term_debt))):
        ltd = long_term_debt[i] if i < len(long_term_debt) else 0.0
        std = short_term_debt[i] if i < len(short_term_debt) else 0.0
        total_debt.append(ltd + std)
    cash = _values("cash_and_equivalents")
    gross_profit = _values("gross_profit")
    depreciation_amortization = _values("depreciation_amortization")
    stock_based_compensation = _values("stock_based_compensation")
    total_stockholders_equity = _values("total_stockholders_equity")
    intangible_assets = _values("intangible_assets")
    goodwill = _values("goodwill")

    return {
        "income_statement": {
            "revenue": revenue,
            "operating_income": operating_income,
            "ebit": operating_income,  # EBIT alias to operating_income for analysis-dcf
            "net_income": net_income,
            "gross_profit": gross_profit,
            "_meta": {
                "revenue": _meta("revenue"),
                "operating_income": _meta("operating_income"),
                "ebit": {**_meta("operating_income"), "note": "alias of operating_income"},
                "net_income": _meta("net_income"),
                "gross_profit": _meta("gross_profit"),
            },
        },
        "cash_flow": {
            "operating_cash_flow": ocf,
            "capex": capex,
            "fcf": fcf,
            "depreciation_amortization": depreciation_amortization,
            "stock_based_compensation": stock_based_compensation,
            "_meta": {
                "operating_cash_flow": _meta("operating_cash_flow"),
                "capex": _meta("capex"),
                "fcf": {
                    "source_concept": None,
                    "derivation": "operating_cash_flow - capex",
                    "fallback_used": False,
                    "components": {
                        "operating_cash_flow": canonical_source["operating_cash_flow"],
                        "capex": canonical_source["capex"],
                    },
                },
                "depreciation_amortization": _meta("depreciation_amortization"),
                "stock_based_compensation": _meta("stock_based_compensation"),
            },
        },
        "balance_sheet": {
            "long_term_debt": long_term_debt,
            "short_term_debt": short_term_debt,
            "total_debt": total_debt,
            "cash": cash,
            "total_stockholders_equity": total_stockholders_equity,
            "intangible_assets": intangible_assets,
            "goodwill": goodwill,
            "_meta": {
                "long_term_debt": _meta("long_term_debt"),
                "short_term_debt": _meta("short_term_debt"),
                "total_debt": {
                    "source_concept": None,
                    "derivation": "long_term_debt + short_term_debt",
                    "fallback_used": False,
                    "components": {
                        "long_term_debt": canonical_source["long_term_debt"],
                        "short_term_debt": canonical_source["short_term_debt"],
                    },
                },
                "cash": _meta("cash_and_equivalents"),
                "total_stockholders_equity": _meta("total_stockholders_equity"),
                "intangible_assets": _meta("intangible_assets"),
                "goodwill": _meta("goodwill"),
            },
        },
    }


def pack_memo_fetch(ticker: str) -> dict:
    """Heavy single-ticker bundle for equity memo: yfinance + SEC EDGAR."""
    info = run_client(YF, ["--ticker", ticker, "--action", "info"])
    history = run_client(YF, ["--ticker", ticker, "--period", "2y"])
    filings = run_client(
        SEC,
        ["--ticker", ticker, "--action", "filings",
         "--forms", "10-K,10-Q,8-K", "--limit", "8"],
    )
    facts = run_client(SEC, ["--ticker", ticker, "--action", "facts"])
    raw_concepts = _fetch_dcf_concepts(ticker)
    canonical = _normalize_dcf(raw_concepts)
    rows = history.get("data", []) if isinstance(history, dict) else []
    info_dict = info if isinstance(info, dict) else {}
    return {
        "pack": "memo-fetch",
        "ticker": ticker.upper(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "company_info": info,
        "price_history": history,
        "history": rows,  # T1 canonical OHLCV alias
        "sec_filings": filings,
        "sec_facts": {
            **facts,
            "concepts": raw_concepts,  # T3 raw — concept-keyed time-series
        } if isinstance(facts, dict) else facts,
        # T3 canonical staging — see ADR-0003 / docs/normalization-contract.md
        "income_statement": canonical["income_statement"],
        "cash_flow": canonical["cash_flow"],
        "balance_sheet": canonical["balance_sheet"],
        "shares_outstanding": info_dict.get("sharesOutstanding"),
        "current_price": info_dict.get("regularMarketPrice"),
        "us_specific": {
            "non_gaap_eps_note": "Out of scope for T3 v1; lives in 8-K narratives.",
            "segment_revenue_note": "Out of scope for T3 v1; future enhancement (us-gaap:RevenuesFromExternalCustomers by segment).",
        },
    }


def pack_comps_multiples(tickers: list[str]) -> dict:
    """Multiples-only fields. Single or batch."""
    if len(tickers) == 1:
        info = run_client(YF, ["--ticker", tickers[0], "--action", "info"])
        per_ticker = {
            tickers[0].upper(): filter_fields(info, MULTIPLES_FIELDS),
        }
        return {
            "pack": "comps-multiples",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tickers": per_ticker,
            "info": per_ticker,  # T1 canonical multiples alias
        }
    # Batch: use yfinance batch action
    batch = run_client(
        YF,
        ["--tickers", ",".join(tickers), "--action", "info"],
    )
    if isinstance(batch, dict) and isinstance(batch.get("tickers"), dict):
        per_ticker = {
            t: filter_fields(d, MULTIPLES_FIELDS)
            for t, d in batch["tickers"].items()
        }
        return {
            "pack": "comps-multiples",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tickers": per_ticker,
            "info": per_ticker,  # T1 canonical multiples alias
        }
    # Batch failure: surface error at top level, keep tickers map clean
    return {
        "pack": "comps-multiples",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "tickers": {},
        "info": {},  # T1 canonical alias (empty on error)
        "error": batch,
    }


def pack_screener_batch(tickers: list[str]) -> dict:
    """Batch lightweight fields for screener input."""
    batch = run_client(
        YF,
        ["--tickers", ",".join(tickers), "--action", "info"],
    )
    if isinstance(batch, dict) and isinstance(batch.get("tickers"), dict):
        per_ticker = {
            t: filter_fields(d, SCREENER_FIELDS)
            for t, d in batch["tickers"].items()
        }
        return {
            "pack": "screener-batch",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tickers": per_ticker,
        }
    # Batch failure: surface error at top level, keep tickers map clean
    return {
        "pack": "screener-batch",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "tickers": {},
        "error": batch,
    }


def _flatten_regime_series(groups: dict) -> dict:
    """T2 canonical: flatten groups.{group}.series.{fred_id}.observations
    into a flat top-level `series: {fred_id: [float, float, ...]}` block.

    Values are extracted in chronological order (most-recent-last). Missing
    or non-numeric observations are dropped. Empty series (no usable values)
    are omitted from the flat block.

    Per docs/normalization-contract.md Tier 2 — analysis-macro-regime
    (regime_compose.resolve_series) reads `pack.series[fred_id]` directly
    as a list of floats, not the nested fred_client envelope.
    """
    def _extract_values(series_payload: dict) -> list[float]:
        """Extract chronological-order float values from a FRED series payload."""
        if not isinstance(series_payload, dict):
            return []
        obs = series_payload.get("observations") or []
        out: list[float] = []
        for o in obs:
            if not isinstance(o, dict):
                continue
            v = o.get("value")
            if v is None:
                continue
            try:
                out.append(float(v))
            except (TypeError, ValueError):
                continue
        return out

    flat: dict[str, list[float]] = {}
    for group_payload in groups.values():
        if not isinstance(group_payload, dict):
            continue
        nested = group_payload.get("series")
        if isinstance(nested, dict):
            # Multi-series group: {fetched_at, series: {fred_id: payload, ...}}
            for fred_id, series_payload in nested.items():
                values = _extract_values(series_payload)
                if values:
                    flat[fred_id] = values
        elif isinstance(nested, str):
            # Single-series group: the group itself IS the FRED payload, with
            # `series: "WEI"` as the FRED ID and `observations: [...]` alongside.
            fred_id = nested
            values = _extract_values(group_payload)
            if values:
                flat[fred_id] = values
    return flat


def pack_regime() -> dict:
    """FRED macro series only — no ticker dimension."""
    groups: dict[str, dict] = {}
    for group_name, (series_csv, periods) in REGIME_SERIES_GROUPS.items():
        groups[group_name] = run_client(
            FRED,
            ["--series", series_csv, "--periods", str(periods)],
        )
    return {
        "pack": "regime-pack",
        "country": "US",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "groups": groups,
        "series": _flatten_regime_series(groups),  # T2 canonical flat alias
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="data-us pack facade — multi-source US data bundler",
    )
    parser.add_argument("--pack", required=True,
                        choices=["snapshot", "memo-fetch", "comps-multiples",
                                 "screener-batch", "regime-pack"],
                        help="Pack type")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ticker", help="Single US ticker (e.g. AAPL)")
    group.add_argument("--tickers",
                       help="Comma-separated US tickers (e.g. AAPL,MSFT,GOOGL)")
    args = parser.parse_args()

    pack = args.pack
    ticker_list: list[str] = []
    if args.tickers:
        ticker_list = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    elif args.ticker:
        ticker_list = [args.ticker.strip().upper()]

    # Pack-type validation per §4.2 contract
    if pack == "snapshot":
        if len(ticker_list) != 1:
            print("error: --pack snapshot requires --ticker (single)", file=sys.stderr)
            return 2
        result = pack_snapshot(ticker_list[0])
    elif pack == "memo-fetch":
        if len(ticker_list) != 1:
            print("error: --pack memo-fetch requires --ticker (single, heavy)",
                  file=sys.stderr)
            return 2
        result = pack_memo_fetch(ticker_list[0])
    elif pack == "comps-multiples":
        if not ticker_list:
            print("error: --pack comps-multiples requires --ticker or --tickers",
                  file=sys.stderr)
            return 2
        result = pack_comps_multiples(ticker_list)
    elif pack == "screener-batch":
        if len(ticker_list) < 2:
            print("error: --pack screener-batch requires --tickers (>=2)",
                  file=sys.stderr)
            return 2
        result = pack_screener_batch(ticker_list)
    elif pack == "regime-pack":
        if ticker_list:
            print("warning: --pack regime-pack ignores --ticker/--tickers (macro only)",
                  file=sys.stderr)
        result = pack_regime()
    else:
        print(f"error: unknown pack '{pack}'", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
