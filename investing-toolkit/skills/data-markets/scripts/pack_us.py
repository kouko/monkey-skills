#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
pack_us.py — investing-toolkit US market pack builder

Composes multi-source US data pulls (yfinance + SEC EDGAR + FRED) into
structured JSON bundles. Pure I/O / fetch layer — no analysis.

This module carries the pack-building logic migrated from
data-us/scripts/pack.py, minus the CLI shell: the unified
data-markets/scripts/pack.py facade (T4) owns argument parsing, market
auto-detection, and the exit-code contract. This module exposes
`SUPPORTED_PACKS` + `build_pack(pack_name, tickers) -> dict` for that
facade to call.

Pack types:
  - snapshot         single ticker, yfinance info + 2y price
  - memo-fetch       single ticker, yfinance + SEC EDGAR (10-K/10-Q/8-K + facts)
  - comps-multiples  single OR batch, yfinance multiples-only fields
  - screener-batch   batch, yfinance lightweight fields (REQUIRES >=2 tickers)
  - regime-pack      no ticker dimension, FRED macro series only

Environment:
  INVESTING_TOOLKIT_CACHE   passed through to underlying clients (yfinance / sec / fred)
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
YF = SCRIPT_DIR / "yfinance_client.py"
SEC = SCRIPT_DIR / "sec_edgar_client.py"
FRED = SCRIPT_DIR / "fred_client.py"


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "pack-us"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


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
    # v2.2.0-c: sector/industry needed by analysis-comps sector_classifier
    # to dispatch the per-sector multiples schema. Falling back to
    # unknown_sector (default schema) when these are absent defeats
    # sector-aware compute mode for production users.
    "sector",
    "industry",
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
    _log("snapshot start", ticker)
    t0 = time.monotonic()
    _log("pack [info]", ticker)
    info = run_client(YF, ["--ticker", ticker, "--action", "info"])
    _log("pack [history 2y]", ticker)
    history = run_client(YF, ["--ticker", ticker, "--period", "2y"])
    _log("snapshot done", f"{ticker} in {time.monotonic() - t0:.1f}s")
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
    all_concepts = [c for chain in DCF_CONCEPT_MAPPING.values() for c in chain]
    unique_concepts = list(dict.fromkeys(all_concepts))
    total = len(unique_concepts)
    for chain in DCF_CONCEPT_MAPPING.values():
        for concept in chain:
            if concept in seen:
                continue
            seen.add(concept)
            _log(f"pack [dcf-concept {len(seen)}/{total}]", f"{ticker} {concept}")
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


def _classify_narrative_entry(
    role: str, quarter: str | None, accession: str | None, narrative: dict,
) -> tuple[bool, bool, list[dict]]:
    """Classify ONE selected filing's `--action narrative` result into
    ``(succeeded, is_partial, failed_item_entries)`` — the per-row bucketing
    logic `_fetch_sec_narrative`'s loop applies to every selected filing,
    split out so that loop body stays short and does one thing (read the
    subprocess result, decide succeeded/failed, hoist any section-level
    failures).

    A wholesale failure (subprocess `error`, or the producer's own
    `narrative_status: "failed"`) yields ``(False, False, [<one failed_items
    entry>])``. A clean success yields ``(True, False, [])``. A `"partial"`
    success (the filing was fetched but >=1 of its sections failed) yields
    ``(True, True, [<one failed_items entry per failed section>])`` — the
    depth-1 hoisting `_fetch_sec_narrative`'s own docstring documents (brief
    Fork A: `pack.py`'s `_classify_result` cannot see into the list-valued
    `sections` sub-field, so this hoist is what makes the degradation
    structurally visible at depth 1)."""
    if "error" in narrative or narrative.get("narrative_status") == "failed":
        return False, False, [{
            "role": role,
            "quarter": quarter,
            "accession": accession,
            "error": narrative.get("error")
            or f"narrative_status={narrative.get('narrative_status')!r} — all sections failed",
            "error_class": narrative.get("error_class", "narrative_failed"),
        }]

    if narrative.get("narrative_status") != "partial":
        return True, False, []

    sections_by_item = {
        s.get("item"): s for s in narrative.get("sections", []) if isinstance(s, dict)
    }
    failed_item_entries = [
        {
            "role": role,
            "quarter": quarter,
            "accession": accession,
            "item": item_id,
            "error": sections_by_item.get(item_id, {}).get(
                "error", f"section {item_id!r} failed"
            ),
            "error_class": sections_by_item.get(item_id, {}).get("error_class", "unknown"),
        }
        for item_id in narrative.get("failed_items", [])
    ]
    return True, True, failed_item_entries


def _fetch_sec_narrative(filings_rows: list[dict]) -> dict:
    """Assemble the `sec_narrative` memo-feed contract (brief §Decision):
    management's filed text for the latest 10-K, the latest 10-Q, and the
    earnings 8-K of each of the last N quarters (Task 2's
    `select_narrative_filings` policy). One `--action narrative` subprocess
    per SELECTED accession; the producer's own cache
    (`narrative_sections_{accession}`, immutable TTL) is reused unchanged —
    this introduces no new cache key.

    Failure must be STRUCTURALLY visible, not merely a status string
    (brief Fork A — the researched EN/JA sources agree a status string
    alone is the documented ignored-by-structural-readers failure mode):
    `failed_items` is hoisted to THIS wrapper's OWN top level (depth 1) —
    `pack.py`'s `_classify_result` walks exactly one level and cannot see
    into a list-valued `sections` sub-field, so a per-item failure living
    inside a selected filing's `sections` list would otherwise be
    structurally invisible. The required count triple `{requested,
    succeeded, failed}` turns "is this complete?" into arithmetic
    reconciliation: `requested` is fixed by the selection POLICY (never by
    what came back), and `succeeded + failed == requested` holds by
    construction — every selected filing resolves to exactly one bucket,
    and every selection gap is counted as failed.

    `_status` (ok/partial/failed) is derived from those counts AND each
    producer's own `narrative_status`: a filing that is itself fetched but
    reports `narrative_status: "partial"` still counts as "succeeded" in
    the triple (the FILING was obtained), but its section-level failures
    are surfaced in `failed_items` and force the wrapper's own `_status` to
    "partial" too — Task 4 taught `pack.py` to honor this self-declared
    `_status`, winning over its own dict-shape inference that structurally
    cannot see into `sections` (a list).
    """
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    # Lazy import: sec_edgar_client.py's top-level `import requests` would
    # otherwise force its runtime deps (requests/edgartools) onto every
    # pack type at MODULE-IMPORT time, not just memo-fetch's narrative path
    # — this module's own PEP 723 header stays dependency-free (see the
    # module docstring); only calling this function pays that cost.
    from sec_edgar_client import select_narrative_filings

    selection = select_narrative_filings(filings_rows)
    requested = selection["requested"]

    filings_out: list[dict] = []
    failed_items: list[dict] = []
    succeeded = 0
    failed = 0
    any_partial = False

    for row in selection["selected"]:
        role = row["role"]
        quarter = row.get("quarter")
        accession = row.get("accessionNumber")
        _log(
            "pack [narrative]",
            f"{role}{(' ' + quarter) if quarter else ''} accession={accession}",
        )
        narrative = run_client(SEC, ["--action", "narrative", "--accession", accession])
        entry = {"role": role, **({"quarter": quarter} if quarter else {}), **narrative}
        filings_out.append(entry)

        row_succeeded, row_partial, row_failed_items = _classify_narrative_entry(
            role, quarter, accession, narrative
        )
        if row_succeeded:
            succeeded += 1
            any_partial = any_partial or row_partial
        else:
            failed += 1
        failed_items.extend(row_failed_items)

    for gap in selection["gaps"]:
        failed += 1
        failed_items.append(dict(gap))

    # `requested > 0` guards against the vacuous `failed == requested`
    # when nothing was requested at all (an empty selection: 0 == 0 is
    # true but is NOT a failure) — see
    # test_fetch_sec_narrative_empty_selection_is_not_vacuously_failed.
    if requested > 0 and failed == requested:
        status = "failed"
    elif failed > 0 or any_partial:
        status = "partial"
    else:
        status = "ok"

    return {
        "filings": filings_out,
        "failed_items": failed_items,
        "requested": requested,
        "succeeded": succeeded,
        "failed": failed,
        "_status": status,
    }


# The primary financial statements Source-A extracts cells from, per the
# latest 10-K -- these are the `statement_name` values edgartools'
# `get_statement`/`facts.to_dataframe()["statement_type"]` recognize. ALL
# FOUR are live-confirmed (not merely API-familiarity assumed) by
# test_data_markets_live.py::test_xval_primary_statements_names_live_confirmed
# (2026-07-13, AAPL FY2025 10-K accession 0000320193-25-000079) -- that test
# is the citation, not sec_edgar_client.py:1645's module-header note, which
# only demonstrates BalanceSheet/IncomeStatement.
XVAL_PRIMARY_STATEMENTS = (
    "BalanceSheet", "IncomeStatement", "CashFlowStatement", "StatementOfEquity",
)


def _latest_10k_accession(filings_rows: list[dict]) -> str | None:
    """Latest 10-K `accessionNumber` from already-fetched `sec_filings` rows
    -- mirrors `sec_edgar_client._latest_filing`'s own form+filingDate
    selection (sec_edgar_client.py:451), reused here rather than re-running
    `select_narrative_filings` (which also selects 10-Q/8-K rows this
    producer does not need)."""
    rows = [r for r in filings_rows if r.get("form") == "10-K" and r.get("filingDate")]
    if not rows:
        return None
    return max(rows, key=lambda r: r["filingDate"]).get("accessionNumber")


def _fetch_xval_source_a(filings_rows: list[dict]) -> dict:
    """Assemble the `xval_source_a` memo-feed contract (Task 2): the latest
    10-K's primary financial-statement cells, one per
    `XVAL_PRIMARY_STATEMENTS` entry, mirroring `_fetch_sec_narrative`'s own
    depth-1 status discipline (:603) -- `requested`/`succeeded`/`failed`
    reconcile by construction and `_status` (ok/partial/failed) is derived
    from the counts, so completeness never requires walking into a nested
    `statements` list.

    `extract_statement_cells` returns a BARE `list[dict]` of cells on
    success or a loud error `dict` on failure (`StatementNotFound` or an
    unrecognized statement variant, sec_edgar_client.py:1645) -- the two
    are discriminated via `isinstance(result, dict)`, the same
    success/failure discriminator `_acquire_raw_filing`'s callers use. A
    successful statement's bare list is WRAPPED into the Source-A pack
    envelope `{accession, statement_name, cells}` (defusing the documented
    envelope seam); a failed statement is recorded as a per-statement
    entry in `failed_items`, never a crash and never a fabricated
    `statements` entry.

    A missing 10-K (no matching row in `filings_rows`) still reaches
    `_acquire_raw_filing(None)`, which already returns a loud resolution
    error slot for any accession it cannot resolve -- no separate guard
    is needed here to avoid a crash.
    """
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    # Lazy import: mirrors `_fetch_sec_narrative`'s own pattern above (keeps
    # sec_edgar_client's top-level `import requests` off this module's
    # import-time cost for other pack types).
    from sec_edgar_client import _acquire_raw_filing, extract_statement_cells

    requested = len(XVAL_PRIMARY_STATEMENTS)
    accession = _latest_10k_accession(filings_rows)

    _log("pack [xval source-a]", f"accession={accession}")
    filing = _acquire_raw_filing(accession)
    filing_error = filing if isinstance(filing, dict) and "error" in filing else None

    statements_out: list[dict] = []
    failed_items: list[dict] = []
    succeeded = 0
    failed = 0

    for statement_name in XVAL_PRIMARY_STATEMENTS:
        if filing_error is not None:
            failed += 1
            failed_items.append({
                "accession": accession,
                "statement_name": statement_name,
                "error": filing_error.get("error"),
                "error_class": filing_error.get("error_class", "acquisition_failed"),
            })
            continue

        result = extract_statement_cells(filing, statement_name)
        if isinstance(result, dict):
            failed += 1
            failed_items.append({
                "accession": accession,
                "statement_name": statement_name,
                "error": result.get("error"),
                "error_class": result.get("error_class", "statement_not_found"),
            })
            continue

        succeeded += 1
        statements_out.append({
            "accession": accession,
            "statement_name": statement_name,
            "cells": result,
        })

    if requested > 0 and failed == requested:
        status = "failed"
    elif failed > 0:
        status = "partial"
    else:
        status = "ok"

    return {
        "statements": statements_out,
        "failed_items": failed_items,
        "requested": requested,
        "succeeded": succeeded,
        "failed": failed,
        "_status": status,
    }


def pack_memo_fetch(ticker: str) -> dict:
    """Heavy single-ticker bundle for equity memo: yfinance + SEC EDGAR."""
    _log("memo-fetch start", ticker)
    t0 = time.monotonic()
    _log("pack [info]", ticker)
    info = run_client(YF, ["--ticker", ticker, "--action", "info"])
    _log("pack [history 2y]", ticker)
    history = run_client(YF, ["--ticker", ticker, "--period", "2y"])
    # Policy-derived DATE window, not a filing-count `--limit` (Task 8 fix for
    # a live-observed false gap, 2026-07-13 real AAPL run): `--limit 8` capped
    # across ALL forms combined, so 8-K/10-Q volume crowded the once-a-year
    # 10-K out of the returned rows entirely -- `select_narrative_filings`
    # then reported a PHANTOM "no 10-K" gap. A count window drifts with a
    # company's filing frequency; `narrative_filings_window_days` (a single
    # cached submissions call either way, so a deeper window is nearly free)
    # does not. Lazy import mirrors `_fetch_sec_narrative`'s own pattern below
    # (sec_edgar_client's top-level `import requests` must not become a
    # module-import-time cost for other pack types).
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    from sec_edgar_client import narrative_filings_window_days

    since_days = narrative_filings_window_days()
    _log("pack [filings]", f"{ticker} 10-K/10-Q/8-K since_days={since_days}")
    filings = run_client(
        SEC,
        ["--ticker", ticker, "--action", "filings",
         "--forms", "10-K,10-Q,8-K", "--since-days", str(since_days)],
    )
    _log("pack [facts]", ticker)
    facts = run_client(SEC, ["--ticker", ticker, "--action", "facts"])
    _log("pack [dcf-concepts]", f"fetching {len(set(c for chain in DCF_CONCEPT_MAPPING.values() for c in chain))} XBRL concepts")
    raw_concepts = _fetch_dcf_concepts(ticker)
    _log("pack [normalize]", "DCF concept merge")
    canonical = _normalize_dcf(raw_concepts)
    _log("pack [narrative selection]", ticker)
    filings_rows = filings.get("filings", []) if isinstance(filings, dict) else []
    sec_narrative = _fetch_sec_narrative(filings_rows)
    _log("memo-fetch done", f"{ticker} in {time.monotonic() - t0:.1f}s")
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
        "sec_narrative": sec_narrative,
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
            "segment_revenue_note": "Out of scope for T3 v1; future enhancement (us-gaap:RevenuesFromExternalCustomers by segment).",
        },
    }


def pack_comps_multiples(tickers: list[str]) -> dict:
    """Multiples-only fields. Single or batch."""
    _log("comps-multiples start", f"{len(tickers)} ticker(s)")
    t0 = time.monotonic()
    if len(tickers) == 1:
        _log("pack [info]", tickers[0])
        info = run_client(YF, ["--ticker", tickers[0], "--action", "info"])
        per_ticker = {
            tickers[0].upper(): filter_fields(info, MULTIPLES_FIELDS),
        }
        _log("comps-multiples done", f"1 ticker in {time.monotonic() - t0:.1f}s")
        return {
            "pack": "comps-multiples",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tickers": per_ticker,
            "info": per_ticker,  # T1 canonical multiples alias
        }
    # Batch: use yfinance batch action
    _log("pack [batch info]", f"{len(tickers)} tickers")
    batch = run_client(
        YF,
        ["--tickers", ",".join(tickers), "--action", "info"],
    )
    if isinstance(batch, dict) and isinstance(batch.get("tickers"), dict):
        per_ticker = {
            t: filter_fields(d, MULTIPLES_FIELDS)
            for t, d in batch["tickers"].items()
        }
        _log("comps-multiples done", f"{len(tickers)} tickers in {time.monotonic() - t0:.1f}s")
        return {
            "pack": "comps-multiples",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tickers": per_ticker,
            "info": per_ticker,  # T1 canonical multiples alias
        }
    # Batch failure: surface error at top level, keep tickers map clean
    _log("comps-multiples done", f"batch failed in {time.monotonic() - t0:.1f}s")
    return {
        "pack": "comps-multiples",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "tickers": {},
        "info": {},  # T1 canonical alias (empty on error)
        "error": batch,
    }


def pack_screener_batch(tickers: list[str]) -> dict:
    """Batch lightweight fields for screener input."""
    _log("screener-batch start", f"{len(tickers)} tickers")
    t0 = time.monotonic()
    batch = run_client(
        YF,
        ["--tickers", ",".join(tickers), "--action", "info"],
    )
    if isinstance(batch, dict) and isinstance(batch.get("tickers"), dict):
        per_ticker = {
            t: filter_fields(d, SCREENER_FIELDS)
            for t, d in batch["tickers"].items()
        }
        _log("screener-batch done", f"{len(tickers)} tickers in {time.monotonic() - t0:.1f}s")
        return {
            "pack": "screener-batch",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "tickers": per_ticker,
        }
    # Batch failure: surface error at top level, keep tickers map clean
    _log("screener-batch done", f"batch failed in {time.monotonic() - t0:.1f}s")
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
    _log("regime-pack start", f"{len(REGIME_SERIES_GROUPS)} FRED groups")
    t0 = time.monotonic()
    groups: dict[str, dict] = {}
    for i, (group_name, (series_csv, periods)) in enumerate(REGIME_SERIES_GROUPS.items(), 1):
        _log(f"pack [fred {i}/{len(REGIME_SERIES_GROUPS)}]", f"{group_name} ({series_csv})")
        groups[group_name] = run_client(
            FRED,
            ["--series", series_csv, "--periods", str(periods)],
        )
    _log("regime-pack done", f"in {time.monotonic() - t0:.1f}s")
    return {
        "pack": "regime-pack",
        "country": "US",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "groups": groups,
        "series": _flatten_regime_series(groups),  # T2 canonical flat alias
    }


# ---------------------------------------------------------------------------
# T4 facade contract
# ---------------------------------------------------------------------------

SUPPORTED_PACKS: tuple[str, ...] = (
    "snapshot",
    "memo-fetch",
    "comps-multiples",
    "screener-batch",
    "regime-pack",
)


def build_pack(pack_name: str, tickers: list[str]) -> dict:
    """Build a US data pack. Mirrors data-us/scripts/pack.py's CLI dispatch
    (pack-type -> ticker-count validation, section assembly) minus
    argparse/sys.exit handling — the unified pack.py facade (T4) owns
    argument parsing and the exit-code contract.

    Raises ValueError on an unsupported pack name or a ticker-count/pack-type
    mismatch (parity with the original CLI's `return 2` validation paths,
    without sys.exit).
    """
    if pack_name not in SUPPORTED_PACKS:
        raise ValueError(f"unknown pack '{pack_name}'")

    ticker_list = [t.strip().upper() for t in tickers if t and t.strip()]

    if pack_name == "snapshot":
        if len(ticker_list) != 1:
            raise ValueError("pack snapshot requires exactly one ticker")
        return pack_snapshot(ticker_list[0])
    if pack_name == "memo-fetch":
        if len(ticker_list) != 1:
            raise ValueError("pack memo-fetch requires exactly one ticker (single, heavy)")
        return pack_memo_fetch(ticker_list[0])
    if pack_name == "comps-multiples":
        if not ticker_list:
            raise ValueError("pack comps-multiples requires at least one ticker")
        return pack_comps_multiples(ticker_list)
    if pack_name == "screener-batch":
        if len(ticker_list) < 2:
            raise ValueError("pack screener-batch requires at least two tickers")
        return pack_screener_batch(ticker_list)
    # regime-pack: no ticker dimension
    return pack_regime()
