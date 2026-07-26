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
  - kpi-quarterly    single ticker, SEC EDGAR dimensional-revenue fact-pack
                     (10-Q quarterly facts + 10-K FY totals; US-only —
                     the facade refuses it for any other market)
  - kpi-topline-backfill  single ticker, SEC EDGAR companyconcept
                     annual-only top-line (total) revenue backfill —
                     Lane A of the two-lane top-line revenue arc
                     (docs/loom/plans/2026-07-25-company-total-revenue.md)
  - statement-backfill    single ticker, SEC EDGAR companyfacts as-reported
                     annual statement backfill (US-only; docs/loom/plans/
                     2026-07-26-us-as-reported-statement-lane.md)
  - reconstruct      single ticker, the three statements AS THE FILER
                     DECLARED THEM (own labels, own concepts, own order)
                     across the last 8 annual filings — US-only; recomputed
                     per run, never persisted (docs/loom/plans/
                     2026-07-26-as-filed-statement-reconstruction.md)

Environment:
  INVESTING_TOOLKIT_CACHE   passed through to underlying clients (yfinance / sec / fred)
"""

import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
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


def _wrap_xval_source_b(cik: int | None) -> dict:
    """Assemble the `xval_source_b` memo-feed contract (Task 3): wraps
    `build_companyfacts_pack` (Task 1) in a depth-1 `_status` envelope with
    the `{requested, succeeded, failed}` count-triple, mirroring
    `_fetch_sec_narrative`'s (:603) and `_fetch_xval_source_a`'s (:725) own
    status discipline -- so pack_inventory (Task 4) and the memo can read
    completeness at depth 1 without walking into the nested `facts` field.

    `requested` is always 1 (a single companyfacts fetch). `cik` is REUSED
    from the CIK already resolved earlier in `pack_memo_fetch` (via the
    `sec_facts` fetch) -- never re-resolved here. A missing `cik` (the
    upstream facts fetch itself failed to resolve one) and a
    `build_companyfacts_pack` error slot are both treated as a depth-1
    `_status: "failed"` -- never a fabricated or silently empty Source-B
    pack.
    """
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    # Lazy import: mirrors `_fetch_sec_narrative`'s/`_fetch_xval_source_a`'s
    # own pattern above (keeps sec_edgar_client's top-level `import requests`
    # off this module's import-time cost for other pack types).
    from sec_edgar_client import build_companyfacts_pack

    if cik is None:
        return {
            "error": "no CIK resolved for companyfacts fetch (upstream sec_facts fetch failed)",
            "error_class": "cik_unresolved",
            "requested": 1,
            "succeeded": 0,
            "failed": 1,
            "_status": "failed",
        }

    pack = build_companyfacts_pack(cik)
    if "error" in pack:
        return {
            **pack,
            "requested": 1,
            "succeeded": 0,
            "failed": 1,
            "_status": "failed",
        }

    return {
        **pack,
        "requested": 1,
        "succeeded": 1,
        "failed": 0,
        "_status": "ok",
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
    _log("pack [xval source-a]", ticker)
    xval_source_a = _fetch_xval_source_a(filings_rows)
    # Reuse the CIK already resolved by the `sec_facts` fetch above -- never
    # re-resolve it (Task 3's own design note; `resolve_cik` is a second SEC
    # request `_wrap_xval_source_b` must not duplicate).
    cik = facts.get("cik") if isinstance(facts, dict) else None
    _log("pack [xval source-b]", f"{ticker} cik={cik}")
    xval_source_b = _wrap_xval_source_b(cik)
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
        "xval_source_a": xval_source_a,
        "xval_source_b": xval_source_b,
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


# kpi-quarterly fiscal-year lookback. The memo's Operating-KPI trend table
# needs the last 8 reported quarters (plan 2026-07-18-memo-quarterly-kpi-
# wiring, Task 5); a 3-calendar-year lower bound spans >=3 full fiscal years
# even for filers whose fiscal year runs AHEAD of the calendar year (NVDA's
# FY2026 10-Qs are filed in calendar 2025), i.e. >=9 reported quarters plus
# the FY totals the derived-Q4 lane (FY − ΣQ1-3) needs. Policy-derived date
# window, not a CLI knob — same convention as memo-fetch's
# narrative_filings_window_days.
KPI_QUARTERLY_LOOKBACK_YEARS = 3


def pack_kpi_quarterly(ticker: str) -> dict:
    """US-only dimensional-revenue fact-pack for the quarterly KPI chain
    (plan 2026-07-18-memo-quarterly-kpi-wiring, Task 1).

    Two `extract_dimensional_revenue` arms over ONE shared fiscal-year
    window (`KPI_QUARTERLY_LOOKBACK_YEARS`):

      - 10-Q — the quarterly facts the series build consumes;
      - 10-K — the FY totals that are the derived-Q4 basis (FY − ΣQ1-3;
        `kpi_xbrl.derive_q4_points` needs both in one facts list, the same
        merge shape tests/analysis/test_kpi_xbrl_quarterly_e2e.py wires).

    Output: `{pack, ticker, fetched_at, company, facts, fiscal_calendars,
    coverage}` — facts + per-accession fiscal calendars merged across the
    two arms (accessions never collide across forms), `coverage` carrying
    each arm's report verbatim plus a self-declared `_status`
    (pack.py's Task-4 section convention).

    Failure honesty (never a silent skip, never a fabricated pack):
      - 10-Q arm error slot -> returned verbatim under the pack envelope
        with NO facts key (facade classifies "failed", exit 1);
      - 10-K arm error slot -> quarterly facts still emitted; the slot is
        surfaced as `coverage.annual` and `coverage._status = "partial"`
        (facade exit 2 — Q4 stays underivable and says so).
    """
    _log("kpi-quarterly start", ticker)
    t0 = time.monotonic()
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    # Lazy import: same pattern as pack_memo_fetch above (sec_edgar_client's
    # top-level `import requests` must not become a module-import-time cost
    # for other pack types).
    from sec_edgar_client import extract_dimensional_revenue

    since_year = datetime.now(timezone.utc).year - KPI_QUARTERLY_LOOKBACK_YEARS
    envelope = {
        "pack": "kpi-quarterly",
        "ticker": ticker.upper(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    _log("pack [10-Q dimensional facts]", f"{ticker} since_year={since_year}")
    quarterly = extract_dimensional_revenue(
        ticker, form="10-Q", since_year=since_year
    )
    if "error" in quarterly:
        _log("kpi-quarterly done", f"{ticker} FAILED in {time.monotonic() - t0:.1f}s")
        return {**envelope, **quarterly}

    _log("pack [10-K dimensional facts]", f"{ticker} since_year={since_year}")
    annual = extract_dimensional_revenue(
        ticker, form="10-K", since_year=since_year
    )
    annual_failed = "error" in annual

    facts = quarterly["facts"] + ([] if annual_failed else annual["facts"])
    fiscal_calendars = {
        **quarterly["fiscal_calendars"],
        **({} if annual_failed else annual["fiscal_calendars"]),
    }
    coverage = {
        # Self-declared section status (pack.py Task-4 convention): the
        # annual arm's failure lives INSIDE this section, invisible to the
        # facade's structural walk — so the producer says so directly.
        "_status": "partial" if annual_failed else "ok",
        "quarterly": quarterly["coverage"],
        "annual": annual if annual_failed else annual["coverage"],
    }
    _log(
        "kpi-quarterly done",
        f"{ticker} {len(facts)} facts in {time.monotonic() - t0:.1f}s"
        + (" (annual arm FAILED)" if annual_failed else ""),
    )
    return {
        **envelope,
        "company": quarterly["company"],
        "facts": facts,
        "fiscal_calendars": fiscal_calendars,
        "coverage": coverage,
    }


def pack_kpi_topline_backfill(ticker: str) -> dict:
    """US-only annual-only `companyconcept` top-line (total) revenue
    backfill pack — Lane A of the two-lane top-line revenue arc (plan
    docs/loom/plans/2026-07-25-company-total-revenue.md, Task 4). Pure
    I/O orchestration: calls `build_top_line_backfill` for `ticker` and
    shapes its return into the standard pack envelope
    `pack_kpi_quarterly` emits; no analysis/filtering/relabeling here.

    The envelope carries the mandatory top-level `"source_kind"` key set
    to the exact literal `"xbrl-companyfacts"` (plan §Notes envelope
    provenance contract) — `kpi_xbrl_ingest.ingest_pack` reads this
    literal to assign the correct durable provenance label to Lane A's
    points; without it every point would inherit the ingest default
    `"xbrl-dimensional"`, a factually wrong label for a companyconcept
    backfill.

    Failure honesty (mirrors `pack_kpi_quarterly`): a loud error slot
    from the producer rides through the envelope verbatim, with NO
    `facts` key — never a fabricated/empty-but-successful pack.
    """
    _log("kpi-topline-backfill start", ticker)
    t0 = time.monotonic()
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    # Lazy import: same pattern as pack_kpi_quarterly above (sec_edgar_
    # client's top-level `import requests` must not become a module-
    # import-time cost for other pack types).
    from sec_edgar_client import build_top_line_backfill

    envelope = {
        "pack": "kpi-topline-backfill",
        "ticker": ticker.upper(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source_kind": "xbrl-companyfacts",
    }

    _log("pack [companyconcept annual backfill]", ticker)
    result = build_top_line_backfill(ticker)
    if "error" in result:
        _log(
            "kpi-topline-backfill done",
            f"{ticker} FAILED in {time.monotonic() - t0:.1f}s",
        )
        return {**envelope, **result}

    _log(
        "kpi-topline-backfill done",
        f"{ticker} {len(result['facts'])} facts in "
        f"{time.monotonic() - t0:.1f}s",
    )
    return {
        **envelope,
        "company": result["company"],
        "facts": result["facts"],
        "coverage": result["coverage"],
        # Task 3 + seam fix 18fc47fd: `kpi_xbrl.facts_to_points` derives
        # every point's `source_form` from `fiscal_calendars[accession]`
        # on the ENVELOPE (`_require_source_form`, which raises rather
        # than guess). Dropping
        # the producer's map here rejects 100% of Lane A's facts at ingest —
        # the defect the two-lane e2e caught, invisible to any test that
        # hand-builds its own envelope.
        "fiscal_calendars": result["fiscal_calendars"],
    }


def pack_statement_backfill(ticker: str) -> dict:
    """US-only as-reported ANNUAL statement pack (Task 8, plan
    docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md). Pure I/O
    orchestration mirroring `pack_kpi_topline_backfill`: calls the producer
    (`build_statement_backfill`) and shapes its return into the standard
    pack envelope; no analysis/filtering/relabeling here.

    The envelope carries the mandatory top-level `"source_kind"` key set to
    the exact literal `"xbrl-companyfacts"` (plan §PIN — statement pack
    envelope). This lane's driver is `kpi_us_statements_ingest`, NOT
    `kpi_xbrl_ingest`, and there this key is a TRUST GATE: the driver
    rejects an envelope whose declared kind is outside
    `kpi_gate.TRUSTED_SOURCE_KINDS` before it builds a single point, so an
    untrusted label can never ride into the durable store. The label
    actually STAMPED on each point comes from the fixed
    `kpi_us_statements._SOURCE_KIND` constant, not from this envelope —
    which is why the success branch below keeps the wrapper's own literal
    rather than letting a producer's value win.
    (An earlier revision of this docstring credited
    `kpi_xbrl_ingest.ingest_pack` here; that is the DIMENSIONAL lane's
    driver and never sees this pack. A maintainer following it would have
    edited the wrong module.)

    Failure honesty (mirrors `pack_kpi_topline_backfill`): ANY producer
    error slot rides through the envelope verbatim, with NO `facts` key —
    never a fabricated/empty-but-successful pack. This passes error slots
    through STRUCTURALLY (dict merge), not by enumerating known error
    classes, so a new error shape (e.g. the concurrently-landing CIK-
    history guard) is handled unchanged rather than silently dropped.
    """
    _log("statement-backfill start", ticker)
    t0 = time.monotonic()
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    # Lazy import: same pattern as pack_kpi_topline_backfill above (sec_
    # edgar_client's top-level `import requests` must not become a module-
    # import-time cost for other pack types).
    from sec_edgar_client import build_statement_backfill

    envelope = {
        "pack": "statement-backfill",
        "ticker": ticker.upper(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source_kind": "xbrl-companyfacts",
    }

    _log("pack [companyfacts statement backfill]", ticker)
    result = build_statement_backfill(ticker)
    if "error" in result:
        _log(
            "statement-backfill done",
            f"{ticker} FAILED in {time.monotonic() - t0:.1f}s",
        )
        return {**envelope, **result}

    _log(
        "statement-backfill done",
        f"{ticker} {len(result['facts'])} facts in "
        f"{time.monotonic() - t0:.1f}s",
    )
    # Whitelist the success-branch fields, like `pack_kpi_topline_backfill`
    # and `pack_kpi_quarterly` both do -- a wholesale `{**envelope, **result}`
    # would let the producer's dict win on EVERY key, including `pack` /
    # `ticker` / `source_kind`. `source_kind` in particular is the key
    # `kpi_xbrl_ingest.ingest_pack` reads to stamp durable provenance on
    # every point; the WRAPPER, not the producer, is this lane's single
    # source of truth for that literal (this producer has exactly one
    # companyfacts code path and no legitimate reason to disagree, so a
    # divergent value can only be a producer bug -- silently normalizing
    # it here is the same convention `pack_kpi_topline_backfill` already
    # uses, where the producer doesn't even set `source_kind`).
    # `fetched_at` is the one deliberate exception: `result` carries the
    # producer's own cache-aware fetch time (the actual fetch time on a
    # cache hit, not this wrapper's `now()`), which is genuinely better
    # information than the envelope's timestamp.
    return {
        **envelope,
        "company": result["company"],
        "facts": result["facts"],
        "coverage": result["coverage"],
        "fetched_at": result["fetched_at"],
    }


# How many annual filings one `reconstruct` run reads, to satisfy the brief's
# "10+ years" (§Smallest End State).
#
# EIGHT, and the brief's own estimate of FOUR is REFUTED, measured 2026-07-26
# on a live KO run: four 10-Ks yielded SIX distinct annual periods (2020-2025),
# not ten. Consecutive 10-Ks OVERLAP by their two comparative years, so N
# filings yield N+2 distinct years, not 3N. The brief (§Users, "Ten years is ~4
# filings (each 10-K carries three comparative years)") multiplies where it
# should overlap, and the plan's cost line inherits the same error. Recorded
# here rather than quietly satisfied, because the arithmetic is load-bearing
# for anyone sizing a run.
#
# Cost, on the plan's own measurement (## Notes: ~10.7s cold / ~1.3s warm per
# filing): ~85s cold, ~10s warm. The brief expects "minutes, not hours" and
# budgets for it (§Open Questions), so the honest constant is the one that
# meets the requirement, not the one that meets the estimate.
RECONSTRUCT_ANNUAL_FILINGS = 8

# Where the as-filed reconstruction itself lives. THIS IS A LAYER INVERSION AND
# IT IS DELIBERATE, so it is named rather than buried: `pack_us` is Layer 1
# (pure I/O) and `kpi_us_statement_shape` is Layer 2 (analysis), and this repo's
# standing convention is the OPPOSITE direction -- analysis-* reaches
# data-markets, and crosses BY SUBPROCESS, never by import
# (`analysis-kpi/scripts/kpi_8k_candidates.py:117`). Three facts decided it:
#
#   * The plan assigns this verb to `pack_us.py` (Task 9, `Module:`), and the
#     reconstruction to `analysis-kpi` (Task 3). A dependency between them is
#     therefore forced by the plan, not chosen here.
#   * The subprocess crossing is not available: `statements_for` takes a LIVE
#     edgartools `Filing` (its input contract is `.xbrl()` ->
#     `presentation_roles` + `get_statement`), which does not survive a JSON
#     process boundary, and `kpi_us_statement_shape` exposes no CLI.
#   * The import is cheap: the module is stdlib-only, and it is imported
#     LAZILY inside the one function that needs it, so no other pack type pays
#     for it at import time. LAZINESS BUYS COST, NOT ACYCLICITY -- an earlier
#     revision of this comment credited it with preventing a cycle, which it
#     does not; a lazy import closing a cycle merely fails later. What actually
#     keeps this acyclic is the SIBLING CONVENTION that the reconstruction
#     modules import no data-markets module at all ("does NOT import any
#     data-markets module", `analysis-kpi/scripts/kpi_us_statements.py:10`).
#     That convention is prose, enforced by no test — so it is the assumption
#     this inversion actually rests on, and the thing to re-check before
#     letting analysis-kpi reach back this way.
#
# One more consequence of reaching across by path: `sys.path.insert(0, ...)`
# below PREPENDS analysis-kpi's scripts dir ahead of data-markets' for the rest
# of the process. No basename collides between the two dirs today, but a future
# one would shadow silently and resolve to the analysis-kpi copy.
#
# Flagged for the reviewer rather than settled unilaterally: the honest fix is
# probably that this verb belongs in analysis-kpi with data-markets supplying
# only the acquisition, which would be a plan change, not an implementation
# choice.
_ANALYSIS_KPI_SCRIPTS = SCRIPT_DIR.parent.parent / "analysis-kpi" / "scripts"


def _ensure_analysis_kpi_importable() -> None:
    """Put analysis-kpi's scripts dir on `sys.path`, idempotently.

    Every function here that reaches across the layer calls this itself rather
    than relying on an earlier caller having done it: a helper whose imports
    only resolve when someone else prepared the path is a coupling nothing
    declares and nothing checks. See the layer note above for why the crossing
    exists at all, and for the shadowing consequence of PREPENDING.
    """
    if str(_ANALYSIS_KPI_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(_ANALYSIS_KPI_SCRIPTS))


def _reconstruction_payload(statements) -> dict:
    """One filing's `Statements` projected onto plain JSON.

    `statements_for` returns FROZEN DATACLASSES (`Statements`, `Line`), and
    this pack's last act is `json.dumps` in the facade -- which raises on a
    dataclass. The projection is therefore load-bearing, not cosmetic, and
    `test_pack_reconstruct_emits_per_accession_statements_with_status` asserts
    the result actually serializes.

    `by_kind` carries only the kinds the filing declares a role for, and that
    absence is preserved here: a kind this filer does not file is ABSENT, never
    an empty list, so "files no such statement" stays distinguishable from
    "the statement came back empty" (the brief's whole empty-cell doctrine
    depends on that distinction surviving every layer).
    """
    return {
        "statements": {
            kind: [asdict(line) for line in lines]
            for kind, lines in statements.by_kind.items()
        },
        "roles": {kind: list(roles) for kind, roles in statements.roles.items()},
        "unrecognised_dimension_keys": list(statements.unrecognised_dimension_keys),
    }


def _decimal_text(value) -> str | None:
    """One `Decimal` money figure as EXACT TEXT, or `None`.

    `str(Decimal)` is digit-for-digit lossless and keeps the scale the
    arithmetic produced. The two alternatives both lose:

      * `float(value)` routes an exact decimal back through the binary
        representation this whole module family bans on money — the mode that
        already manufactured a false restatement signal here once
        (docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md);
      * leaving the `Decimal` in place makes the payload depend on the facade's
        `json.dumps(..., default=str)` fallback (pack.py). That fallback would
        do the right thing TODAY and would equally happily serialize a float,
        so the projection is made explicit here and pinned by a bare
        `json.dumps` in the test rather than inherited.
    """
    return None if value is None else str(value)


def _sum_check_payload(check) -> dict:
    """One `SumCheck` projected onto JSON, WITHOUT its `terms`.

    The four figures ride together because they are one argument: the filer
    reports `reported`, its own declaration produces `computed`, they differ by
    `difference`, and `tolerance` is how far its own declared precision said
    they may. A verdict without the interval cannot be argued with, only
    believed.

    `terms` is dropped deliberately — one entry per child per period per group,
    over 8 filings, is the bulk of the reconstruction repeated inside its own
    verification, and every figure in it is already on the statement lines this
    envelope ships. `parent` + `period` is the join key back to them.
    """
    return {
        "kind": check.kind,
        "period": check.period,
        "parent": check.parent,
        "status": check.status,
        "reported": _decimal_text(check.reported),
        "computed": _decimal_text(check.computed),
        "difference": _decimal_text(check.difference),
        "tolerance": _decimal_text(check.tolerance),
    }


def _verification_payload(reconstructions) -> dict:
    """What the run's own arithmetic says about itself, as JSON.

    `reconstructions` is the list of `(filing_date, Statements)` pairs
    `resolution_report` takes — one per successfully reconstructed filing.

    WHY THIS EXISTS AT ALL. The typing layer this arc built was unreachable:
    `resolution_report` had no reference outside its own module, so a reader
    holding this verb's output could not tell a pipeline defect from an
    accounting fact — the brief's whole reason for existing (§Problem, "It
    cannot say WHY a cell is empty"). Shipping the machinery with no exit is
    shipping the arc's cost without its benefit.

    THREE PARTS, AND WHY EACH IS SEPARATE:

      `by_era`      resolved/unresolved per FILING era. Never one run-wide
                    rate: the 63-of-65 was measured on filings filed 2016-2018
                    only and a 10-year run spans years nobody sampled (brief
                    §"A limit this brief must not overclaim"). An era with no
                    filings is ABSENT rather than zeroed — `_tallies`' own
                    rule, preserved here — because a row of zeroes reads as a
                    measurement that was made and came out empty.
      `statements`  one entry per filing per statement, carrying the reason
                    codes and the detail naming the group. This is what a
                    reader investigates; `by_era` is only the summary.
      `sum_checks`  the four-way status census, plus the disagreements in full.

    THE CENSUS IS FIXED-KEY, and that is the OPPOSITE rule to `by_era`'s on
    purpose: the four statuses are an exhaustive enumeration of what one check
    can be, so a zero IS a measurement ("nothing disagreed") rather than an
    absence, and a consumer reading `by_status["within_rounding"]` must never
    have to tell "none" from "this pack forgot to count it". A status outside
    the four still gets counted under its own name rather than dropped — the
    vocabulary moving must be visible, not lossy.

    ONLY `disagrees` IS LISTED IN FULL. `within_rounding` is deliberately NOT
    folded in with it: 24 of the committed capture's 27 exact-comparison
    disagreements are rounding residue inside the filers' own declared
    interval, so collapsing the two overstates broken filer arithmetic ~8x
    (plan Decision Log, Task 4 -> Task 8). `incomplete` is not listed either —
    a comparison that could not be made is a third fact, counted here and
    already carried per statement as `groups_incomplete`.

    AND WHAT `disagrees` STILL DOES NOT MEAN: not "the filer is wrong".
    `verify` sees PRESENTED lines only, so a calculation child the filer never
    puts on the face of the statement leaves the sum short and reads as a
    disagreement it structurally cannot separate from a real one (measured: 3
    of the capture's 3 remaining disagreements, all IBM's diluted-share group).
    `resolution_report`'s own docstring is the long form.

    `verify` RUNS TWICE — once inside `resolution_report`, once here for the
    census — because `resolution_report` returns only its aggregate and
    `kpi_us_statement_check` is not this task's to widen. Both calls are pure
    stdlib arithmetic over already-parsed lines, against a ~10s-per-filing
    acquisition and parse; the cost is not where this verb's time goes.
    """
    _ensure_analysis_kpi_importable()
    from kpi_us_statement_check import (
        AGREES, DISAGREES, INCOMPLETE, WITHIN_ROUNDING, resolution_report,
        verify,
    )

    report = resolution_report(reconstructions)
    checks = [
        check
        for _filing_date, statements in reconstructions
        for check in verify(statements)
    ]

    by_status = {status: 0 for status in (AGREES, WITHIN_ROUNDING, DISAGREES, INCOMPLETE)}
    for check in checks:
        by_status[check.status] = by_status.get(check.status, 0) + 1

    return {
        "by_era": [
            {
                "era": tally.era,
                "resolved": tally.resolved,
                "unresolved": tally.unresolved,
                # Pairs become named fields: `["ambiguous_total", 3]` needs a
                # reader to know which slot is which, and the era tallies are
                # the numbers most likely to be quoted out of context.
                "reasons": [
                    {"reason": reason, "count": count}
                    for reason, count in tally.reasons
                ],
            }
            for tally in report.by_era
        ],
        "statements": [
            {
                "filing_date": statement.filing_date,
                "era": statement.era,
                "kind": statement.kind,
                "resolved": statement.resolved,
                "reasons": [
                    {"reason": entry.reason, "detail": entry.detail}
                    for entry in statement.reasons
                ],
                "groups_checked": statement.groups_checked,
                "groups_incomplete": statement.groups_incomplete,
            }
            for statement in report.statements
        ],
        "sum_checks": {
            "by_status": by_status,
            "disagreements": [
                _sum_check_payload(check)
                for check in checks
                if check.status == DISAGREES
            ],
        },
    }


def pack_reconstruct(ticker: str) -> dict:
    """US-only AS-FILED reconstruction pack (Task 9, plan
    docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md): one
    company's three statements, as the filer declared them, for its most recent
    `RECONSTRUCT_ANNUAL_FILINGS` annual filings.

    Orchestration only -- acquisition comes from `sec_edgar_client`, the
    reconstruction from `kpi_us_statement_shape.statements_for` (see the layer
    note above); nothing is decided here.

    NOTHING IS PERSISTED. The reconstruction is RECOMPUTED per run and no point
    reaches `kpi_store` (plan ## Notes kickoff decision: filings are immutable,
    so the correct cache-invalidation trigger is OUR OWN CODE CHANGING, and a
    naive TTL cache would serve a stale reconstruction after a logic fix -- the
    "system disguises its own failure as data" mode this arc exists to remove).
    Consequently the envelope carries NO `source_kind`: that key is the ingest
    trust gate (`kpi_gate.TRUSTED_SOURCE_KINDS`), and a pack that never ingests
    declaring one would be an unearned claim on a store this verb never writes.

    Failure honesty, mirroring `_fetch_xval_source_a`: a per-accession
    acquisition failure is a LOUD skip recorded in `failed_items`, never a
    fabricated statements entry and never a silent drop. The depth-1
    `{requested, succeeded, failed}` triple plus `_status` let the facade's
    one-level structural walk see degradation without descending into
    `filings` (pack.py `_section_status`).

    THE RESULT IS NESTED UNDER ONE `reconstruction` SECTION, not spread across
    the pack's top level, and that placement is load-bearing rather than
    stylistic. A live KO run (2026-07-26) reconstructed 4 of 4 filings and was
    still reported `partial`/exit 2, for two reasons this shape fixes:
    `_list_section_status` reads an empty top-level list as `"failed"` (correct
    for a ticker fan-out, wrong for a `failed_items: []` that MEANS success),
    and `main()` overwrites any top-level `_status` with its own block before
    a reader sees it. On a section, the self-declared `_status` is what
    `_section_status` honours -- the same placement `sec_narrative` and
    `xval_source_a` already use.

    THE SECTION CARRIES ITS OWN VERIFICATION (`verification`): the per-era
    resolved/unresolved counts with a reason per unresolved statement, and the
    sum-check census in which `within_rounding` stays distinct from `disagrees`
    and `incomplete`. Without it the arc's typing layer shipped nowhere -- the
    library separated the three kinds of empty and the only output surface
    emitted raw `Line`s, so the reader was handed back the undifferentiated
    blank the brief exists to remove. See `_verification_payload` for what each
    part does and does NOT license a reader to conclude.

    WHAT THIS ENVELOPE DELIBERATELY DOES NOT CARRY: per-cell typing. There is
    no `cell_state` here, and its absence is a judgement rather than an
    oversight. This envelope's contract is the filer's OWN line set, and
    against that set the four states collapse: every line present IS presented,
    so `not_presented` is unaskable; `not_tagged` is already visible as a
    period missing from a line's `values` (that is the whole reading rule --
    an absent period key means the line exists and that period carries no
    undimensioned value); and `derived` would have to ADD a line the filer
    never filed, corrupting the one fidelity promise this pack makes. The
    states earn their keep against a FIXED grid, where a cell must exist
    whether or not the filer filed it -- which is `kpi_spine_view
    .derive_spine_as_filed`'s 14-field view, a read-side concern over this
    payload, not this payload. A consumer wanting the four-way taxonomy calls
    that; it is not silently missing here.
    """
    _log("reconstruct start", ticker)
    t0 = time.monotonic()
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    _ensure_analysis_kpi_importable()
    # Lazy imports: same pattern as every other SEC pack above -- neither
    # sec_edgar_client's top-level `import requests` nor the cross-layer
    # reconstruction module may become an import-time cost for other packs.
    import sec_edgar_client
    from kpi_us_statement_shape import statements_for

    envelope = {
        "pack": "reconstruct",
        "ticker": ticker.upper(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    resolved = sec_edgar_client.resolve_cik(ticker)
    if "error" in resolved:
        _log("reconstruct done", f"{ticker} FAILED in {time.monotonic() - t0:.1f}s")
        return {**envelope, **resolved}

    rows = sec_edgar_client.list_filings(
        resolved["cik"], ["10-K"], RECONSTRUCT_ANNUAL_FILINGS
    )
    selected = [row for row in rows if row.get("accessionNumber")]

    filings: list[dict] = []
    failed_items: list[dict] = []
    # The assembled `Statements` kept alongside their projection, because
    # verification reads the dataclasses and `filings` holds only plain JSON.
    reconstructions: list[tuple] = []
    for row in selected:
        accession = row["accessionNumber"]
        _log("pack [acquire + reconstruct]", accession)
        filing = sec_edgar_client._acquire_raw_filing(accession)
        if isinstance(filing, dict) and "error" in filing:
            failed_items.append({"accession": accession, **filing})
            continue
        assembled = statements_for(filing)
        reconstructions.append((row.get("filingDate"), assembled))
        filings.append({
            "accession": accession,
            "form": row.get("form"),
            "filingDate": row.get("filingDate"),
            **_reconstruction_payload(assembled),
        })

    # THE VERIFICATION LAYER MAY NOT TAKE THE STATEMENTS DOWN WITH IT.
    # `kpi_us_statement_check` refuses rather than guessing -- a concept
    # presented twice under one parent with disagreeing figures, a filing date
    # with no readable year -- and its own docstring says such a row "aborts
    # the whole batch rather than marking one filing unresolved". That is the
    # right posture for an ORACLE and the wrong one for this pack to inherit:
    # the reconstruction of every filing has already succeeded by this line, so
    # letting the exception out would trade the whole ~85s run for a traceback
    # and make verification a REGRESSION in a verb that worked without it.
    # Contained to its own section instead, and made loud there.
    #
    # `Exception`, not the `ValueError` the two known refusals raise: what is
    # being contained is a LAYER BOUNDARY, and narrowing it to today's classes
    # would let tomorrow's refusal through to do exactly the damage this
    # guards against. The message rides along verbatim -- a bare flag would
    # tell a reader something refused and not which row.
    try:
        verification = _verification_payload(reconstructions)
    except Exception as exc:  # noqa: BLE001 - deliberate; see above
        verification = {
            "error": f"as-filed verification refused this run: {exc}",
            "error_class": "verification",
        }

    requested = len(selected)
    failed = len(failed_items)

    # Self-declared section status, per pack.py's `_section_status` convention.
    # `requested == 0` is NOT vacuously "failed" -- nothing was asked for, so
    # nothing failed (the exact trap
    # `test_fetch_sec_narrative_empty_selection_is_not_vacuously_failed` pins
    # for the narrative lane).
    status = (
        "failed" if requested and failed == requested
        else "partial" if failed
        else "ok"
    )
    # A REFUSED VERIFICATION IS A DEGRADED RUN, and it has to be said HERE.
    # `_section_status` honours this section's own `_status` and then never
    # descends, so the error marker inside `verification` is structurally
    # invisible to the facade: without this fold, the reader gets exit 0 over a
    # run whose arithmetic was never checked. It cannot promote a fully failed
    # acquisition back down -- a run with no statements at all is worse news
    # than one with unchecked statements.
    if "error" in verification and status != "failed":
        status = "partial"

    _log(
        "reconstruct done",
        f"{ticker} {len(filings)}/{requested} filings in "
        f"{time.monotonic() - t0:.1f}s",
    )
    return {
        **envelope,
        "cik": resolved["cik"],
        "company": resolved.get("title"),
        "reconstruction": {
            "filings": filings,
            "verification": verification,
            "failed_items": failed_items,
            "requested": requested,
            "succeeded": len(filings),
            "failed": failed,
            "_status": status,
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
    "kpi-quarterly",
    "kpi-topline-backfill",
    "statement-backfill",
    "reconstruct",
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
    if pack_name == "kpi-quarterly":
        if len(ticker_list) != 1:
            raise ValueError(
                "pack kpi-quarterly requires exactly one ticker (single, heavy)"
            )
        return pack_kpi_quarterly(ticker_list[0])
    if pack_name == "kpi-topline-backfill":
        if len(ticker_list) != 1:
            raise ValueError(
                "pack kpi-topline-backfill requires exactly one ticker (single, heavy)"
            )
        return pack_kpi_topline_backfill(ticker_list[0])
    if pack_name == "statement-backfill":
        if len(ticker_list) != 1:
            raise ValueError(
                "pack statement-backfill requires exactly one ticker (single, heavy)"
            )
        return pack_statement_backfill(ticker_list[0])
    if pack_name == "reconstruct":
        if len(ticker_list) != 1:
            raise ValueError(
                "pack reconstruct requires exactly one ticker (single, heavy)"
            )
        return pack_reconstruct(ticker_list[0])
    # regime-pack: no ticker dimension
    return pack_regime()
