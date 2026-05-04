#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
Pure-compute peer multiples comparison (Comps Analysis).

Layer 2 (Analysis) under the v2.0.0 three-layer design:
- NO I/O: it does NOT fetch data from any network/file source other than
  the JSON paths supplied via --anchor and --peers (and yaml/json schema
  files bundled under references/).
- Caller (data-{country}/pack.py --pack comps-multiples) is responsible
  for pre-fetching multiples for both anchor and each peer ticker, and
  for shaping them into the input contract documented below.
- Peer-discovery (which tickers count as peers) is the report layer's
  job; this script trusts the supplied peer list verbatim.

Direct mode emits a fixed-5 statistics/ranking surface (legacy v2.0.0
contract). Compute mode (v2.2.0-c) classifies the anchor by sector and
loads the matching schema from references/schema-<id>.json — the schema
defines which multiples are computed, statistics-aggregated, and ranked.

Output: comps table JSON with median / mean / quartile statistics,
anchor delta vs median + percentile, per-multiple and composite rankings,
and a no-I/O provenance stamp.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

# v2.2.0-c sector_classifier import (lives next to this script)
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from sector_classifier import (  # noqa: E402
    KNOWN_SCHEMA_IDS,
    ClassificationResult,
    classify,
    classify_pack,
)

# Direct-mode fixed-5 multiple list (v2.0.0 contract — DO NOT change).
DIRECT_MULTIPLES = ["trailingPE", "forwardPE", "evEbitda", "priceToSales", "priceToBook"]

# Accept yfinance's "enterpriseToEbitda" as an alias for "evEbitda"
ALIASES = {
    "evEbitda":     ["evEbitda", "enterpriseToEbitda"],
    "trailingPE":   ["trailingPE"],
    "forwardPE":    ["forwardPE"],
    "priceToSales": ["priceToSales"],
    "priceToBook":  ["priceToBook"],
    # Schema-driven extras can be passthrough from comps-multiples pack if present.
    "priceToTangibleBook": ["priceToTangibleBook"],
    "priceToFFO":          ["priceToFFO"],
    "evEbitdare":          ["evEbitdare"],
    "priceToCFO":          ["priceToCFO"],
    "evRevenue":           ["evRevenue", "enterpriseToRevenue"],
}

DIVERGENCE_BAND_LOW  = 0.05   # 5%   — boundary inclusive (≤ low)
DIVERGENCE_BAND_HIGH = 0.15   # 15%  — boundary inclusive for medium (high band is strict >)

_REFERENCES_DIR = _SCRIPT_DIR.parent / "references"
_SCHEMA_CACHE: dict[str, dict] = {}


# --- Schema loader ---------------------------------------------------------

def _load_schema(schema_id: str) -> dict:
    """Load and cache a sector schema from references/schema-<id>.json."""
    if schema_id in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[schema_id]
    path = _REFERENCES_DIR / f"schema-{schema_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"sector schema missing: {path}")
    with path.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    _SCHEMA_CACHE[schema_id] = schema
    return schema


def _schema_multiple_ids(schema: dict) -> list[str]:
    """Extract the ordered list of multiple ids from a schema's multiples block."""
    return [m["id"] for m in (schema.get("multiples") or [])]


def _schema_multiple_kinds(schema: dict) -> dict[str, str]:
    """Return {multiple_id: kind} where kind ∈ {compute, passthrough}."""
    return {m["id"]: m.get("kind", "compute") for m in (schema.get("multiples") or [])}


# --- Pack loaders ----------------------------------------------------------

def _load_pack(path: Path) -> dict:
    """Load a comps-multiples pack JSON. No network access."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_memo_fetch_pack(path: Path, expected_ticker: str) -> dict:
    """Load and validate a memo-fetch pack. Layer-1 input contract — no I/O beyond this read."""
    with path.open("r", encoding="utf-8") as f:
        pack = json.load(f)
    if pack.get("pack") != "memo-fetch":
        raise ValueError(
            f"--anchor-base must be a memo-fetch pack; got pack={pack.get('pack')!r}"
        )
    if pack.get("ticker") != expected_ticker:
        raise ValueError(
            f"--anchor-base ticker {pack.get('ticker')!r} does not match "
            f"--anchor ticker {expected_ticker!r}"
        )
    return pack


def _resolve_ticker(pack: dict, fallback: str) -> str:
    """Find the ticker symbol used as the info{} key."""
    if isinstance(pack.get("ticker"), str) and pack["ticker"]:
        return pack["ticker"]
    info = pack.get("info") or {}
    if len(info) == 1:
        return next(iter(info.keys()))
    return fallback


def _extract_multiples(pack: dict, ticker: str, multiple_ids: list[str]) -> dict:
    """Pull the requested multiples out of pack.info[ticker], normalising aliases.
    Missing values become None.
    """
    info = (pack.get("info") or {}).get(ticker) or {}
    out: dict[str, float | None] = {}
    for canonical in multiple_ids:
        aliases = ALIASES.get(canonical, [canonical])
        value = None
        for alias in aliases:
            if alias in info and info[alias] is not None:
                try:
                    value = float(info[alias])
                except (TypeError, ValueError):
                    value = None
                break
        out[canonical] = value
    return out


# --- Memo-fetch helpers ----------------------------------------------------

def _safe_first(arr, default=None):
    """First element of a list, or default if empty/non-list."""
    return arr[0] if isinstance(arr, list) and arr else default


def _safe_first_or_zero_for_immaterial(arr) -> tuple[float, bool]:
    """Per v2.2.0-l immaterial-empty convention: empty `[]` → (0.0, True).

    Returns (value, was_substituted_zero). Used for goodwill / intangibles
    where empty arrays mean "concept not tagged → immaterial → zero".
    """
    if isinstance(arr, list) and not arr:
        return (0.0, True)
    if isinstance(arr, list) and arr:
        return (float(arr[0]), False)
    return (0.0, True)  # absent block → also immaterial-zero (consistent with v2.2.0-l)


def _concept_meta(stmt: dict, concept: str) -> dict:
    """Return the per-concept _meta block from a financial statement section."""
    return ((stmt.get("_meta") or {}).get(concept) or {})


def _concept_fy_end(stmt: dict, concept: str) -> str | None:
    return _safe_first(_concept_meta(stmt, concept).get("fiscal_year_ends") or [])


def _concept_filings(stmt: dict, concept: str) -> list[str]:
    filings = _concept_meta(stmt, concept).get("filings_used") or []
    return [filings[0]] if filings else []


# Backward-compat aliases for IS / BS / CF helpers used by tests / other modules.
def _bs_concept_fy_end(bs: dict, concept: str) -> str | None:
    return _concept_fy_end(bs, concept)


def _bs_concept_filings(bs: dict, concept: str) -> list[str]:
    return _concept_filings(bs, concept)


def _cf_concept_fy_end(cf: dict, concept: str) -> str | None:
    return _concept_fy_end(cf, concept)


def _cf_concept_filings(cf: dict, concept: str) -> list[str]:
    return _concept_filings(cf, concept)


# --- Per-formula dispatch --------------------------------------------------

# Each formula returns (value: float|None, provenance: dict, warnings: list[str]).
# Signatures take memo_fetch and direct_multiples; passthrough handled separately.

def _f_trailingPE(memo: dict, direct: dict) -> tuple[float | None, dict, list[str]]:
    inc = memo.get("income_statement") or {}
    ci = memo.get("company_info") or {}
    price = memo.get("current_price") or ci.get("regularMarketPrice")
    shares = memo.get("shares_outstanding") or ci.get("sharesOutstanding")
    net_income_fy = _safe_first(inc.get("net_income"))
    fy_end = _concept_fy_end(inc, "net_income")
    filings = _concept_filings(inc, "net_income")

    if price is None or net_income_fy is None or not shares:
        prov = {
            "computed": False,
            "note": "compute skipped — current_price / net_income[0] / shares_outstanding required",
        }
        warns: list[str] = []
        if price is None:
            warns.append("price-based compute skipped: current_price missing")
        elif net_income_fy is None:
            warns.append("trailingPE compute skipped: net_income FY array empty")
        elif not shares:
            warns.append("trailingPE compute skipped: shares_outstanding missing")
        return None, prov, warns
    eps_fy = net_income_fy / shares
    value = price / eps_fy if eps_fy != 0 else None
    return value, {
        "numerator_source":   "memo-fetch.current_price",
        "denominator_source": "memo-fetch.income_statement.net_income[0] / memo-fetch.shares_outstanding",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
        "note":               "FY-trailing, not TTM — see ROADMAP §v2.2.0-b §7.3",
    }, []


def _f_priceToSales(memo: dict, direct: dict) -> tuple[float | None, dict, list[str]]:
    inc = memo.get("income_statement") or {}
    ci = memo.get("company_info") or {}
    market_cap = ci.get("marketCap")
    revenue_fy = _safe_first(inc.get("revenue"))
    fy_end = _concept_fy_end(inc, "revenue")
    filings = _concept_filings(inc, "revenue")
    if market_cap is None or revenue_fy is None:
        warns = []
        if market_cap is None:
            warns.append("priceToSales compute skipped: marketCap missing")
        elif revenue_fy is None:
            warns.append("priceToSales compute skipped: revenue FY array empty")
        return None, {
            "computed": False,
            "note": "compute skipped — marketCap / revenue[0] required",
        }, warns
    return market_cap / revenue_fy, {
        "numerator_source":   "memo-fetch.company_info.marketCap",
        "denominator_source": "memo-fetch.income_statement.revenue[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
    }, []


def _f_priceToBook(memo: dict, direct: dict) -> tuple[float | None, dict, list[str]]:
    bs = memo.get("balance_sheet") or {}
    ci = memo.get("company_info") or {}
    market_cap = ci.get("marketCap")
    equity_fy = _safe_first(bs.get("total_stockholders_equity"))
    fy_end = _concept_fy_end(bs, "total_stockholders_equity")
    filings = _concept_filings(bs, "total_stockholders_equity")
    if market_cap is None or equity_fy is None or equity_fy == 0:
        warns = []
        if market_cap is None:
            warns.append("priceToBook compute skipped: marketCap missing")
        elif equity_fy is None:
            warns.append("priceToBook compute skipped: total_stockholders_equity FY array empty")
        elif equity_fy == 0:
            warns.append("priceToBook compute skipped: total_stockholders_equity[0] is zero")
        return None, {
            "computed": False,
            "note": "compute skipped — marketCap / total_stockholders_equity[0] required (and non-zero)",
        }, warns
    return market_cap / equity_fy, {
        "numerator_source":   "memo-fetch.company_info.marketCap",
        "denominator_source": "memo-fetch.balance_sheet.total_stockholders_equity[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
        "note":               "FY-trailing book value, not most-recent-quarter — see ROADMAP §v2.2.0-l",
    }, []


def _ev_components(memo: dict) -> tuple[float | None, list[str]]:
    """Compute Enterprise Value = marketCap + total_debt[0] - cash[0].
    Returns (ev, missing_input_names)."""
    bs = memo.get("balance_sheet") or {}
    ci = memo.get("company_info") or {}
    market_cap = ci.get("marketCap")
    total_debt_fy = _safe_first(bs.get("total_debt"))
    cash_fy = _safe_first(bs.get("cash"))
    missing = []
    if market_cap is None: missing.append("marketCap")
    if total_debt_fy is None: missing.append("total_debt[0]")
    if cash_fy is None: missing.append("cash[0]")
    if missing:
        return None, missing
    return market_cap + total_debt_fy - cash_fy, []


def _ebitda_components(memo: dict) -> tuple[float | None, list[str], str | None, list[str]]:
    """Compute EBITDA = operating_income[0] + depreciation_amortization[0].
    Returns (ebitda, missing_input_names, fy_end, filings)."""
    inc = memo.get("income_statement") or {}
    cf = memo.get("cash_flow") or {}
    operating_income_fy = _safe_first(inc.get("operating_income"))
    da_fy = _safe_first(cf.get("depreciation_amortization"))
    fy_end = _concept_fy_end(cf, "depreciation_amortization")
    filings = _concept_filings(cf, "depreciation_amortization")
    missing = []
    if operating_income_fy is None: missing.append("operating_income[0]")
    if da_fy is None: missing.append("depreciation_amortization[0]")
    if missing:
        return None, missing, fy_end, filings
    return operating_income_fy + da_fy, [], fy_end, filings


def _f_evEbitda(memo: dict, direct: dict) -> tuple[float | None, dict, list[str]]:
    ev, ev_missing = _ev_components(memo)
    ebitda, ebitda_missing, fy_end, filings = _ebitda_components(memo)
    missing = ev_missing + ebitda_missing
    if missing:
        return None, {
            "computed": False,
            "note": f"compute skipped — missing: {', '.join(missing)}",
        }, [f"evEbitda compute skipped: {', '.join(missing)} missing"]
    if ebitda == 0:
        return None, {
            "computed": False,
            "note": "compute skipped — EBITDA (EBIT[0] + D&A[0]) is zero",
        }, ["evEbitda compute skipped: EBITDA is zero"]
    return ev / ebitda, {
        "numerator_source":   "memo-fetch.company_info.marketCap + balance_sheet.total_debt[0] - balance_sheet.cash[0]",
        "denominator_source": "memo-fetch.income_statement.operating_income[0] + cash_flow.depreciation_amortization[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
        "note":               "EV/EBITDA FY-trailing (EBIT + D&A); not LTM-EBITDA — see ROADMAP §v2.2.0-l",
    }, []


def _f_priceToTangibleBook(memo: dict, direct: dict) -> tuple[float | None, dict, list[str]]:
    bs = memo.get("balance_sheet") or {}
    ci = memo.get("company_info") or {}
    market_cap = ci.get("marketCap")
    equity_fy = _safe_first(bs.get("total_stockholders_equity"))
    fy_end = _concept_fy_end(bs, "total_stockholders_equity")
    filings = _concept_filings(bs, "total_stockholders_equity")
    if market_cap is None or equity_fy is None:
        warns = []
        if market_cap is None: warns.append("priceToTangibleBook compute skipped: marketCap missing")
        elif equity_fy is None: warns.append("priceToTangibleBook compute skipped: total_stockholders_equity FY array empty")
        return None, {
            "computed": False,
            "note": "compute skipped — marketCap / equity[0] required",
        }, warns
    goodwill_fy, goodwill_substituted = _safe_first_or_zero_for_immaterial(bs.get("goodwill"))
    intangibles_fy, intangibles_substituted = _safe_first_or_zero_for_immaterial(bs.get("intangible_assets"))
    tangible_book = equity_fy - goodwill_fy - intangibles_fy
    notes_parts: list[str] = []
    if goodwill_substituted or intangibles_substituted:
        sub_fields = []
        if goodwill_substituted: sub_fields.append("goodwill")
        if intangibles_substituted: sub_fields.append("intangibles")
        notes_parts.append(f"{'/'.join(sub_fields)} immaterial → substituted 0 (v2.2.0-l convention)")
    if tangible_book <= 0:
        notes_parts.append("tangible book non-positive (over-amortized intangibles or goodwill > equity)")
        return None, {
            "computed": False,
            "note": "; ".join(notes_parts),
        }, [
            f"priceToTangibleBook compute skipped: tangible book non-positive (equity={equity_fy} - goodwill={goodwill_fy} - intangibles={intangibles_fy})"
        ]
    notes_parts.append("intangibles + goodwill from FY balance sheet")
    return market_cap / tangible_book, {
        "numerator_source":   "memo-fetch.company_info.marketCap",
        "denominator_source": "memo-fetch.balance_sheet.total_stockholders_equity[0] - goodwill[0] - intangible_assets[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
        "note":               "; ".join(notes_parts),
    }, []


def _f_priceToFFO(memo: dict, direct: dict) -> tuple[float | None, dict, list[str]]:
    inc = memo.get("income_statement") or {}
    cf = memo.get("cash_flow") or {}
    ci = memo.get("company_info") or {}
    market_cap = ci.get("marketCap")
    net_income_fy = _safe_first(inc.get("net_income"))
    da_fy = _safe_first(cf.get("depreciation_amortization"))
    fy_end = _concept_fy_end(cf, "depreciation_amortization")
    filings = _concept_filings(cf, "depreciation_amortization")
    missing = []
    if market_cap is None: missing.append("marketCap")
    if net_income_fy is None: missing.append("net_income[0]")
    if da_fy is None: missing.append("depreciation_amortization[0]")
    if missing:
        return None, {
            "computed": False,
            "note": f"compute skipped — missing: {', '.join(missing)}",
        }, [f"priceToFFO compute skipped: {', '.join(missing)} missing"]
    ffo = net_income_fy + da_fy
    if ffo == 0:
        return None, {
            "computed": False,
            "note": "compute skipped — FFO (NI + D&A) is zero",
        }, ["priceToFFO compute skipped: FFO is zero"]
    return market_cap / ffo, {
        "numerator_source":   "memo-fetch.company_info.marketCap",
        "denominator_source": "memo-fetch.income_statement.net_income[0] + cash_flow.depreciation_amortization[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
        "note":               "FFO ≈ NI + D&A; gains_on_sale not subtracted (XBRL gap)",
    }, []


def _f_evEbitdare(memo: dict, direct: dict) -> tuple[float | None, dict, list[str]]:
    ev, ev_missing = _ev_components(memo)
    ebitda, ebitda_missing, fy_end, filings = _ebitda_components(memo)
    missing = ev_missing + ebitda_missing
    if missing:
        return None, {
            "computed": False,
            "note": f"compute skipped — missing: {', '.join(missing)}",
        }, [f"evEbitdare compute skipped: {', '.join(missing)} missing"]
    if ebitda == 0:
        return None, {
            "computed": False,
            "note": "compute skipped — EBITDA (EBIT[0] + D&A[0]) is zero",
        }, ["evEbitdare compute skipped: EBITDA is zero"]
    return ev / ebitda, {
        "numerator_source":   "memo-fetch.company_info.marketCap + balance_sheet.total_debt[0] - balance_sheet.cash[0]",
        "denominator_source": "memo-fetch.income_statement.operating_income[0] + cash_flow.depreciation_amortization[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
        "note":               "EBITDAre ≈ EBITDA; impairment/gains_on_sale not added back (XBRL gap)",
    }, []


def _f_priceToCFO(memo: dict, direct: dict) -> tuple[float | None, dict, list[str]]:
    cf = memo.get("cash_flow") or {}
    ci = memo.get("company_info") or {}
    market_cap = ci.get("marketCap")
    ocf_fy = _safe_first(cf.get("operating_cash_flow"))
    fy_end = _concept_fy_end(cf, "operating_cash_flow")
    filings = _concept_filings(cf, "operating_cash_flow")
    if market_cap is None or ocf_fy is None:
        warns = []
        if market_cap is None: warns.append("priceToCFO compute skipped: marketCap missing")
        elif ocf_fy is None: warns.append("priceToCFO compute skipped: operating_cash_flow FY array empty")
        return None, {
            "computed": False,
            "note": "compute skipped — marketCap / operating_cash_flow[0] required",
        }, warns
    if ocf_fy == 0:
        return None, {
            "computed": False,
            "note": "compute skipped — operating_cash_flow[0] is zero",
        }, ["priceToCFO compute skipped: operating_cash_flow is zero"]
    return market_cap / ocf_fy, {
        "numerator_source":   "memo-fetch.company_info.marketCap",
        "denominator_source": "memo-fetch.cash_flow.operating_cash_flow[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
    }, []


def _f_evRevenue(memo: dict, direct: dict) -> tuple[float | None, dict, list[str]]:
    inc = memo.get("income_statement") or {}
    revenue_fy = _safe_first(inc.get("revenue"))
    fy_end = _concept_fy_end(inc, "revenue")
    filings = _concept_filings(inc, "revenue")
    ev, ev_missing = _ev_components(memo)
    missing = list(ev_missing)
    if revenue_fy is None: missing.append("revenue[0]")
    if missing:
        return None, {
            "computed": False,
            "note": f"compute skipped — missing: {', '.join(missing)}",
        }, [f"evRevenue compute skipped: {', '.join(missing)} missing"]
    if revenue_fy == 0:
        return None, {
            "computed": False,
            "note": "compute skipped — revenue[0] is zero",
        }, ["evRevenue compute skipped: revenue is zero"]
    return ev / revenue_fy, {
        "numerator_source":   "memo-fetch.company_info.marketCap + balance_sheet.total_debt[0] - balance_sheet.cash[0]",
        "denominator_source": "memo-fetch.income_statement.revenue[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
    }, []


# Dispatch table: formula_id → callable returning (value, prov, warnings).
MULTIPLE_FORMULAS: dict[str, callable] = {
    "trailingPE_FY":          _f_trailingPE,
    "priceToSales_FY":        _f_priceToSales,
    "priceToBook_FY":         _f_priceToBook,
    "evEbitda_FY":            _f_evEbitda,
    "priceToTangibleBook_FY": _f_priceToTangibleBook,
    "priceToFFO_FY":          _f_priceToFFO,
    "evEbitdare_FY":          _f_evEbitdare,
    "priceToCFO_FY":          _f_priceToCFO,
    "evRevenue_FY":           _f_evRevenue,
}


# --- Indicator formulas (v2.2.0-c) -----------------------------------------
#
# Each indicator returns (value: float|None, provenance: dict, warnings: list[str]).
# Values are PERCENTAGES (e.g. 16.2, not 0.162); unit is added by the caller.
# Provenance shape mirrors multiple-provenance: numerator_source /
# denominator_source / accession_basis / fiscal_year_end / computed / [note].

def _i_ROE(memo: dict) -> tuple[float | None, dict, list[str]]:
    inc = memo.get("income_statement") or {}
    bs = memo.get("balance_sheet") or {}
    net_income_fy = _safe_first(inc.get("net_income"))
    equity_fy = _safe_first(bs.get("total_stockholders_equity"))
    fy_end = _concept_fy_end(bs, "total_stockholders_equity")
    filings = _concept_filings(bs, "total_stockholders_equity")
    if net_income_fy is None or equity_fy is None or equity_fy <= 0:
        warns: list[str] = []
        if net_income_fy is None:
            warns.append("ROE compute skipped: net_income FY array empty")
        elif equity_fy is None:
            warns.append("ROE compute skipped: total_stockholders_equity FY array empty")
        elif equity_fy <= 0:
            warns.append("ROE compute skipped: total_stockholders_equity[0] non-positive")
        return None, {
            "computed": False,
            "note": "compute skipped — net_income[0] and equity[0] (>0) required",
        }, warns
    return (net_income_fy / equity_fy) * 100.0, {
        "numerator_source":   "memo-fetch.income_statement.net_income[0]",
        "denominator_source": "memo-fetch.balance_sheet.total_stockholders_equity[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
    }, []


def _i_book_value_growth(memo: dict) -> tuple[float | None, dict, list[str]]:
    bs = memo.get("balance_sheet") or {}
    equity_arr = bs.get("total_stockholders_equity") or []
    fy_end = _concept_fy_end(bs, "total_stockholders_equity")
    filings = _concept_filings(bs, "total_stockholders_equity")
    if not isinstance(equity_arr, list) or len(equity_arr) < 2:
        return None, {
            "computed": False,
            "note": "compute skipped — equity FY-1 array entry missing",
        }, ["book_value_growth compute skipped: equity FY-1 missing"]
    e0, e1 = equity_arr[0], equity_arr[1]
    if e0 is None or e1 is None or e1 == 0:
        return None, {
            "computed": False,
            "note": "compute skipped — equity[1] missing or zero",
        }, ["book_value_growth compute skipped: equity[1] missing or zero"]
    return ((e0 - e1) / e1) * 100.0, {
        "numerator_source":   "memo-fetch.balance_sheet.total_stockholders_equity[0] - [1]",
        "denominator_source": "memo-fetch.balance_sheet.total_stockholders_equity[1]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
    }, []


def _i_gross_margin(memo: dict) -> tuple[float | None, dict, list[str]]:
    inc = memo.get("income_statement") or {}
    revenue_fy = _safe_first(inc.get("revenue"))
    gross_arr = inc.get("gross_profit")
    fy_end = _concept_fy_end(inc, "gross_profit") or _concept_fy_end(inc, "revenue")
    filings = _concept_filings(inc, "gross_profit") or _concept_filings(inc, "revenue")
    # Per spec §6.3: gross_profit empty array → null + note (different from
    # goodwill/intangibles which substitute 0; gross_profit absent means
    # undisclosed, not 0).
    if not isinstance(gross_arr, list) or not gross_arr:
        return None, {
            "computed": False,
            "note": "compute skipped — gross_profit not disclosed (empty array; treat as undisclosed not zero)",
        }, ["gross_margin compute skipped: gross_profit FY array empty (undisclosed)"]
    gross_fy = gross_arr[0]
    if revenue_fy is None or revenue_fy == 0 or gross_fy is None:
        warns = []
        if revenue_fy is None:
            warns.append("gross_margin compute skipped: revenue FY array empty")
        elif revenue_fy == 0:
            warns.append("gross_margin compute skipped: revenue[0] is zero")
        elif gross_fy is None:
            warns.append("gross_margin compute skipped: gross_profit[0] is null")
        return None, {
            "computed": False,
            "note": "compute skipped — revenue[0] (non-zero) and gross_profit[0] required",
        }, warns
    return (gross_fy / revenue_fy) * 100.0, {
        "numerator_source":   "memo-fetch.income_statement.gross_profit[0]",
        "denominator_source": "memo-fetch.income_statement.revenue[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
    }, []


def _i_operating_margin(memo: dict) -> tuple[float | None, dict, list[str]]:
    inc = memo.get("income_statement") or {}
    revenue_fy = _safe_first(inc.get("revenue"))
    op_fy = _safe_first(inc.get("operating_income"))
    fy_end = _concept_fy_end(inc, "operating_income") or _concept_fy_end(inc, "revenue")
    filings = _concept_filings(inc, "operating_income") or _concept_filings(inc, "revenue")
    if revenue_fy is None or revenue_fy == 0 or op_fy is None:
        warns = []
        if revenue_fy is None:
            warns.append("operating_margin compute skipped: revenue FY array empty")
        elif revenue_fy == 0:
            warns.append("operating_margin compute skipped: revenue[0] is zero")
        elif op_fy is None:
            warns.append("operating_margin compute skipped: operating_income FY array empty")
        return None, {
            "computed": False,
            "note": "compute skipped — revenue[0] (non-zero) and operating_income[0] required",
        }, warns
    return (op_fy / revenue_fy) * 100.0, {
        "numerator_source":   "memo-fetch.income_statement.operating_income[0]",
        "denominator_source": "memo-fetch.income_statement.revenue[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
    }, []


def _i_FCF_yield(memo: dict) -> tuple[float | None, dict, list[str]]:
    cf = memo.get("cash_flow") or {}
    ci = memo.get("company_info") or {}
    market_cap = ci.get("marketCap")
    ocf_fy = _safe_first(cf.get("operating_cash_flow"))
    capex_fy = _safe_first(cf.get("capex"))
    fy_end = _concept_fy_end(cf, "operating_cash_flow") or _concept_fy_end(cf, "capex")
    filings = _concept_filings(cf, "operating_cash_flow") or _concept_filings(cf, "capex")
    if market_cap is None or ocf_fy is None or capex_fy is None:
        warns = []
        if market_cap is None:
            warns.append("FCF_yield compute skipped: marketCap missing")
        elif ocf_fy is None:
            warns.append("FCF_yield compute skipped: operating_cash_flow FY array empty")
        elif capex_fy is None:
            warns.append("FCF_yield compute skipped: capex FY array empty")
        return None, {
            "computed": False,
            "note": "compute skipped — marketCap / operating_cash_flow[0] / capex[0] required",
        }, warns
    if market_cap == 0:
        return None, {
            "computed": False,
            "note": "compute skipped — marketCap is zero",
        }, ["FCF_yield compute skipped: marketCap is zero"]
    fcf = ocf_fy - capex_fy
    return (fcf / market_cap) * 100.0, {
        "numerator_source":   "memo-fetch.cash_flow.operating_cash_flow[0] - capex[0]",
        "denominator_source": "memo-fetch.company_info.marketCap",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
    }, []


def _i_FCF_margin(memo: dict) -> tuple[float | None, dict, list[str]]:
    cf = memo.get("cash_flow") or {}
    inc = memo.get("income_statement") or {}
    revenue_fy = _safe_first(inc.get("revenue"))
    ocf_fy = _safe_first(cf.get("operating_cash_flow"))
    capex_fy = _safe_first(cf.get("capex"))
    fy_end = _concept_fy_end(cf, "operating_cash_flow") or _concept_fy_end(cf, "capex")
    filings = _concept_filings(cf, "operating_cash_flow") or _concept_filings(cf, "capex")
    if revenue_fy is None or revenue_fy == 0 or ocf_fy is None or capex_fy is None:
        warns = []
        if revenue_fy is None:
            warns.append("FCF_margin compute skipped: revenue FY array empty")
        elif revenue_fy == 0:
            warns.append("FCF_margin compute skipped: revenue[0] is zero")
        elif ocf_fy is None:
            warns.append("FCF_margin compute skipped: operating_cash_flow FY array empty")
        elif capex_fy is None:
            warns.append("FCF_margin compute skipped: capex FY array empty")
        return None, {
            "computed": False,
            "note": "compute skipped — revenue[0] (non-zero) / operating_cash_flow[0] / capex[0] required",
        }, warns
    fcf = ocf_fy - capex_fy
    return (fcf / revenue_fy) * 100.0, {
        "numerator_source":   "memo-fetch.cash_flow.operating_cash_flow[0] - capex[0]",
        "denominator_source": "memo-fetch.income_statement.revenue[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
    }, []


def _i_debt_to_equity(memo: dict) -> tuple[float | None, dict, list[str]]:
    """debt_to_equity = (long_term_debt[0] + short_term_debt[0]) / equity[0] × 100.

    Per spec §6.2: total_debt = long_term_debt[0] + short_term_debt[0]; treat
    None as 0 only if at least one component present, else null.
    """
    bs = memo.get("balance_sheet") or {}
    lt_arr = bs.get("long_term_debt")
    st_arr = bs.get("short_term_debt")
    equity_fy = _safe_first(bs.get("total_stockholders_equity"))
    fy_end = _concept_fy_end(bs, "total_stockholders_equity")
    filings = _concept_filings(bs, "total_stockholders_equity")
    lt_fy = _safe_first(lt_arr) if isinstance(lt_arr, list) else None
    st_fy = _safe_first(st_arr) if isinstance(st_arr, list) else None
    has_lt = isinstance(lt_arr, list) and len(lt_arr) > 0 and lt_fy is not None
    has_st = isinstance(st_arr, list) and len(st_arr) > 0 and st_fy is not None
    if not has_lt and not has_st:
        return None, {
            "computed": False,
            "note": "compute skipped — neither long_term_debt[0] nor short_term_debt[0] disclosed",
        }, ["debt_to_equity compute skipped: neither long_term_debt nor short_term_debt disclosed"]
    if equity_fy is None or equity_fy <= 0:
        warns = []
        if equity_fy is None:
            warns.append("debt_to_equity compute skipped: total_stockholders_equity FY array empty")
        else:
            warns.append("debt_to_equity compute skipped: total_stockholders_equity[0] non-positive")
        return None, {
            "computed": False,
            "note": "compute skipped — equity[0] (>0) required",
        }, warns
    total_debt = (lt_fy if has_lt else 0.0) + (st_fy if has_st else 0.0)
    note_parts: list[str] = []
    if not has_lt:
        note_parts.append("long_term_debt absent → treated as 0")
    if not has_st:
        note_parts.append("short_term_debt absent → treated as 0")
    prov = {
        "numerator_source":   "memo-fetch.balance_sheet.long_term_debt[0] + short_term_debt[0]",
        "denominator_source": "memo-fetch.balance_sheet.total_stockholders_equity[0]",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
    }
    if note_parts:
        prov["note"] = "; ".join(note_parts)
    return (total_debt / equity_fy) * 100.0, prov, []


def _i_rule_of_40(memo: dict) -> tuple[float | None, dict, list[str]]:
    """rule_of_40 = revenue_growth_yoy + operating_margin (sum of two pcts).

    revenue_growth_yoy = (revenue[0] - revenue[1]) / revenue[1] × 100.
    """
    inc = memo.get("income_statement") or {}
    rev_arr = inc.get("revenue") or []
    op_fy = _safe_first(inc.get("operating_income"))
    fy_end = _concept_fy_end(inc, "revenue")
    filings = _concept_filings(inc, "revenue")
    if not isinstance(rev_arr, list) or len(rev_arr) < 2:
        return None, {
            "computed": False,
            "note": "compute skipped — revenue FY-1 array entry missing",
        }, ["rule_of_40 compute skipped: revenue FY-1 missing"]
    r0, r1 = rev_arr[0], rev_arr[1]
    if r0 is None or r1 is None or r1 == 0:
        return None, {
            "computed": False,
            "note": "compute skipped — revenue[1] missing or zero",
        }, ["rule_of_40 compute skipped: revenue[1] missing or zero"]
    if op_fy is None or r0 == 0:
        warns = []
        if op_fy is None:
            warns.append("rule_of_40 compute skipped: operating_income FY array empty")
        elif r0 == 0:
            warns.append("rule_of_40 compute skipped: revenue[0] is zero")
        return None, {
            "computed": False,
            "note": "compute skipped — operating_income[0] and revenue[0] (non-zero) required",
        }, warns
    revenue_growth_yoy = ((r0 - r1) / r1) * 100.0
    operating_margin = (op_fy / r0) * 100.0
    return revenue_growth_yoy + operating_margin, {
        "numerator_source":   "(memo-fetch.income_statement.revenue[0] - revenue[1]) / revenue[1] + operating_income[0] / revenue[0]",
        "denominator_source": "n/a (sum of two ratios, both expressed as pct)",
        "accession_basis":    filings,
        "fiscal_year_end":    fy_end,
        "computed":           True,
        "note":               "rule_of_40 = revenue_growth_yoy + operating_margin (both pct)",
    }, []


# Dispatch table for indicators: formula_id → callable.
INDICATOR_FORMULAS: dict[str, callable] = {
    "ROE_FY":               _i_ROE,
    "book_value_growth_FY": _i_book_value_growth,
    "gross_margin_FY":      _i_gross_margin,
    "operating_margin_FY":  _i_operating_margin,
    "FCF_yield_FY":         _i_FCF_yield,
    "FCF_margin_FY":        _i_FCF_margin,
    "debt_to_equity_FY":    _i_debt_to_equity,
    "rule_of_40_FY":        _i_rule_of_40,
}


def _compute_indicators_from_memo_fetch(
    memo_fetch: dict,
    schema: dict,
) -> tuple[dict, dict, list[str]]:
    """Compute the schema's indicators from a memo-fetch pack.

    Returns (indicators_dict, indicator_provenance_dict, warnings_list) where:
      indicators_dict[indicator_id] = {"value": float|None, "unit": "pct"}
      indicator_provenance_dict[indicator_id] = {numerator_source, ...}
        — same shape as multiple compute_provenance.
    """
    out_indicators: dict[str, dict] = {}
    out_prov: dict[str, dict] = {}
    warnings: list[str] = []
    for entry in schema.get("indicators") or []:
        iid = entry["id"]
        formula_id = entry.get("formula_id")
        formula = INDICATOR_FORMULAS.get(formula_id)
        if formula is None:
            out_indicators[iid] = {"value": None, "unit": "pct"}
            out_prov[iid] = {
                "computed": False,
                "note": f"compute skipped — unknown indicator formula_id={formula_id!r}",
            }
            warnings.append(f"{iid} compute skipped: unknown formula_id={formula_id!r}")
            continue
        value, prov, warns = formula(memo_fetch)
        out_indicators[iid] = {"value": value, "unit": "pct"}
        out_prov[iid] = prov
        warnings.extend(warns)
    return out_indicators, out_prov, warnings


def _compute_multiples_from_memo_fetch(
    memo_fetch: dict,
    direct_multiples: dict,
    schema: dict,
) -> tuple[dict, dict, list[str]]:
    """Recompute the schema's multiples from a memo-fetch pack.

    Returns (multiples_compute, compute_provenance, warnings).
    Iterates the schema's `multiples` list — kind=passthrough copies from
    direct_multiples; kind=compute dispatches via MULTIPLE_FORMULAS.
    """
    warnings: list[str] = [
        "trailingPE compute uses latest FY (not TTM); systematic divergence vs yfinance TTM expected during fiscal year"
    ]
    out_compute: dict[str, float | None] = {}
    out_prov: dict[str, dict] = {}

    for entry in schema.get("multiples") or []:
        mid = entry["id"]
        kind = entry.get("kind", "compute")
        if kind == "passthrough":
            out_compute[mid] = direct_multiples.get(mid)
            out_prov[mid] = {
                "computed": False,
                "note": "pass-through from comps-multiples pack (consensus EPS has no primary source)"
                if mid == "forwardPE"
                else "pass-through from comps-multiples pack",
            }
            continue
        formula_id = entry.get("formula_id")
        formula = MULTIPLE_FORMULAS.get(formula_id)
        if formula is None:
            out_compute[mid] = None
            out_prov[mid] = {
                "computed": False,
                "note": f"compute skipped — unknown formula_id={formula_id!r}",
            }
            warnings.append(f"{mid} compute skipped: unknown formula_id={formula_id!r}")
            continue
        value, prov, warns = formula(memo_fetch, direct_multiples)
        out_compute[mid] = value
        out_prov[mid] = prov
        warnings.extend(warns)

    return out_compute, out_prov, warnings


def _classify_divergence_alert(pct_diff: float) -> str:
    abs_pct = abs(pct_diff)
    if abs_pct <= DIVERGENCE_BAND_LOW * 100:
        return "low"
    if abs_pct <= DIVERGENCE_BAND_HIGH * 100:
        return "medium"
    return "high"


def _compute_divergence(
    direct: dict,
    compute: dict,
    prov: dict,
    multiple_ids: list[str],
    passthrough_ids: set[str] | None = None,
) -> dict[str, dict]:
    """For each multiple in `multiple_ids`, compute abs/pct diff between direct and compute."""
    passthrough_ids = passthrough_ids or set()
    out: dict[str, dict] = {}
    for m in multiple_ids:
        d_val = direct.get(m)
        c_val = compute.get(m)
        if d_val is None or c_val is None:
            note = (prov.get(m) or {}).get("note") or "compute null; cannot diff"
            out[m] = {"abs_diff": None, "pct_diff": None, "alert": "n/a", "note": note}
            continue
        abs_diff = c_val - d_val
        if d_val == 0:
            out[m] = {"abs_diff": abs_diff, "pct_diff": None, "alert": "n/a", "note": "direct value zero — pct_diff undefined"}
            continue
        pct_diff = (abs_diff / d_val) * 100.0
        if m in passthrough_ids:
            out[m] = {"abs_diff": 0.0, "pct_diff": 0.0, "alert": "n/a", "note": "pass-through"}
            continue
        out[m] = {
            "abs_diff": abs_diff,
            "pct_diff": pct_diff,
            "alert":    _classify_divergence_alert(pct_diff),
        }
    return out


def _provenance_label(pack: dict, fallback_path: Path) -> str:
    prov = pack.get("_provenance") or {}
    skill = prov.get("skill")
    source = prov.get("source")
    if skill and source:
        return f"{skill}/{source}"
    if skill:
        return f"{skill}/pack.py --pack comps-multiples"
    return str(fallback_path)


def _percentiles(values: list[float]) -> tuple[float, float]:
    if len(values) < 2:
        v = values[0] if values else 0.0
        return (v, v)
    qs = statistics.quantiles(values, n=4, method="inclusive")
    return (qs[0], qs[2])


def _empirical_percentile(value: float, all_values: list[float]) -> float:
    if not all_values:
        return 0.5
    leq = sum(1 for v in all_values if v <= value)
    return leq / len(all_values)


def _stat_block(peer_values: list[float], anchor_value: float | None) -> dict:
    n = len(peer_values)
    if n == 0:
        v = anchor_value if anchor_value is not None else 0.0
        return {
            "median": v, "mean": v, "q1": v, "q3": v, "min": v, "max": v, "n": 0,
        }
    q1, q3 = _percentiles(peer_values)
    return {
        "median": statistics.median(peer_values),
        "mean":   statistics.fmean(peer_values),
        "q1":     q1,
        "q3":     q3,
        "min":    min(peer_values),
        "max":    max(peer_values),
        "n":      n,
    }


def _anchor_delta(anchor_value: float | None, peer_values: list[float]) -> dict | None:
    if anchor_value is None:
        return None
    if not peer_values:
        return {"value": anchor_value, "vs_median_pct": 0.0, "percentile": 0.5}
    median = statistics.median(peer_values)
    vs_median_pct = 0.0 if median == 0 else ((anchor_value - median) / median) * 100.0
    pct = _empirical_percentile(anchor_value, peer_values + [anchor_value])
    return {
        "value":         anchor_value,
        "vs_median_pct": vs_median_pct,
        "percentile":    pct,
    }


def _rank_ascending(pairs: list[tuple[str, float]]) -> dict[str, int]:
    sorted_pairs = sorted(pairs, key=lambda kv: kv[1])
    ranks: dict[str, int] = {}
    last_value = None
    last_rank = 0
    for idx, (ticker, value) in enumerate(sorted_pairs, start=1):
        if last_value is not None and value == last_value:
            ranks[ticker] = last_rank
        else:
            ranks[ticker] = idx
            last_rank = idx
            last_value = value
    return ranks


def _build_ranking(
    anchor_ticker: str,
    anchor_multiples: dict,
    peers: list[dict],
    multiple_ids: list[str],
) -> list[dict]:
    """Per-multiple ranks + composite rank for anchor + peers."""
    all_entries: list[tuple[str, dict]] = [(anchor_ticker, anchor_multiples)]
    all_entries.extend((p["ticker"], p["multiples"]) for p in peers)

    per_multiple_ranks: dict[str, dict[str, int | None]] = {m: {} for m in multiple_ids}
    for m in multiple_ids:
        valid = [(t, mults[m]) for t, mults in all_entries if mults.get(m) is not None]
        ranks = _rank_ascending(valid)
        for t, _mults in all_entries:
            per_multiple_ranks[m][t] = ranks.get(t)

    ranking: list[dict] = []
    for ticker, _mults in all_entries:
        rank_values = [
            per_multiple_ranks[m][ticker]
            for m in multiple_ids
            if per_multiple_ranks[m][ticker] is not None
        ]
        composite = sum(rank_values) / len(rank_values) if rank_values else float("inf")
        entry: dict = {"ticker": ticker, "composite_rank_avg": composite}
        for m in multiple_ids:
            entry[f"{m}_rank"] = per_multiple_ranks[m][ticker]
        ranking.append(entry)

    ranking.sort(key=lambda r: r["composite_rank_avg"])
    for idx, entry in enumerate(ranking, start=1):
        entry["composite_rank"] = idx
    cleaned: list[dict] = []
    for entry in ranking:
        ordered = {
            "ticker": entry["ticker"],
            "composite_rank": entry["composite_rank"],
            "composite_rank_avg": round(entry["composite_rank_avg"], 4)
                if entry["composite_rank_avg"] != float("inf") else None,
        }
        for m in multiple_ids:
            ordered[f"{m}_rank"] = entry[f"{m}_rank"]
        cleaned.append(ordered)
    return cleaned


def _parse_peer_paths(arg: str) -> list[Path]:
    paths = [Path(p.strip()) for p in arg.split(",") if p.strip()]
    if not paths:
        raise ValueError("--peers must contain at least one path")
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pure-compute peer multiples comparison (Layer 2)."
    )
    parser.add_argument(
        "--anchor", required=True, type=Path,
        help="Path to anchor ticker's comps-multiples pack JSON",
    )
    parser.add_argument(
        "--peers", required=True, type=str,
        help="Comma-separated peer comps-multiples pack JSON paths",
    )
    parser.add_argument(
        "--mode", choices=["direct", "compute"], default="direct",
        help="direct = use multiples in JSON (v2.0.0 only mode); compute = recompute from base financials",
    )
    parser.add_argument(
        "--rationale-map", type=Path, default=None,
        help="Optional JSON file mapping ticker -> rationale string",
    )
    parser.add_argument(
        "--anchor-base", type=Path, default=None,
        help="Path to anchor's memo-fetch pack JSON (REQUIRED for --mode compute)",
    )
    parser.add_argument(
        "--sector-override", type=str, default=None,
        help=(
            "Force a schema_id (debug; bypasses sector-routing.yaml + sector-overrides.yaml). "
            f"Must be one of: {', '.join(KNOWN_SCHEMA_IDS)}"
        ),
    )
    parser.add_argument(
        "--show-routing", action="store_true",
        help="Stderr: print resolved schema_id + source + matched_rule for the anchor.",
    )
    args = parser.parse_args()

    if args.mode == "compute" and args.anchor_base is None:
        parser.error("--mode compute requires --anchor-base")
    if args.mode == "direct" and args.anchor_base is not None:
        sys.stderr.write(
            "[analysis-comps WARN] --anchor-base ignored in --mode direct\n"
        )
    if args.sector_override is not None and args.sector_override not in KNOWN_SCHEMA_IDS:
        sys.stderr.write(
            f"[analysis-comps ERROR] --sector-override {args.sector_override!r} "
            f"is not a known schema_id. Must be one of: {', '.join(KNOWN_SCHEMA_IDS)}\n"
        )
        return 2

    warnings: list[str] = []

    requested_mode = args.mode
    effective_mode = args.mode

    # Load anchor
    anchor_pack = _load_pack(args.anchor)
    anchor_ticker = _resolve_ticker(anchor_pack, fallback=args.anchor.stem.upper())
    anchor_source = _provenance_label(anchor_pack, args.anchor)

    # In direct mode, the multiple set is fixed-5 (legacy v2.0.0 contract).
    # In compute mode, the multiple set comes from the anchor's sector schema.
    if effective_mode == "direct":
        anchor_multiple_ids = list(DIRECT_MULTIPLES)
        anchor_multiples = _extract_multiples(anchor_pack, anchor_ticker, anchor_multiple_ids)
        anchor_classification: ClassificationResult | None = None
        anchor_schema: dict | None = None
    else:
        # Compute mode — classify (or honour --sector-override).
        if args.sector_override is not None:
            anchor_classification = ClassificationResult(
                schema_id=args.sector_override,
                source="cli_override",
                matched_rule=f"--sector-override:{args.sector_override}",
            )
        else:
            anchor_classification = classify_pack(anchor_pack)
        try:
            anchor_schema = _load_schema(anchor_classification.schema_id)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            sys.stderr.write(f"[analysis-comps ERROR] {exc}\n")
            return 1
        anchor_multiple_ids = _schema_multiple_ids(anchor_schema)
        anchor_multiples = _extract_multiples(anchor_pack, anchor_ticker, anchor_multiple_ids)
        if args.show_routing:
            sys.stderr.write(
                f"[analysis-comps routing] anchor={anchor_ticker} "
                f"schema_id={anchor_classification.schema_id} "
                f"source={anchor_classification.source} "
                f"matched_rule={anchor_classification.matched_rule}\n"
            )

    # Compute mode: load + validate memo-fetch pack
    anchor_base = None
    if effective_mode == "compute":
        try:
            anchor_base = _load_memo_fetch_pack(args.anchor_base, anchor_ticker)
        except (json.JSONDecodeError, ValueError) as exc:
            sys.stderr.write(f"[analysis-comps ERROR] {exc}\n")
            return 1

    # Load peers
    peer_paths = _parse_peer_paths(args.peers)
    # peer_packs entries: (ticker, multiples, source_label, classification|None, raw_pack)
    peer_packs: list[tuple[str, dict, str, ClassificationResult | None, dict]] = []
    for p in peer_paths:
        pack = _load_pack(p)
        ticker = _resolve_ticker(pack, fallback=p.stem.upper())
        if ticker == anchor_ticker:
            warnings.append(f"Peer file {p} resolves to anchor ticker {ticker}; skipped")
            continue
        mults = _extract_multiples(pack, ticker, anchor_multiple_ids)
        peer_class: ClassificationResult | None = None
        if effective_mode == "compute":
            peer_class = classify_pack(pack)
            if (
                anchor_classification is not None
                and peer_class.schema_id != anchor_classification.schema_id
            ):
                warnings.append(
                    f"Peer {ticker} classified as schema {peer_class.schema_id}; "
                    f"anchor schema is {anchor_classification.schema_id}. "
                    f"Statistics may be misleading; recommend per-sector peer set."
                )
        peer_packs.append((ticker, mults, _provenance_label(pack, p), peer_class, pack))

    if not peer_packs:
        warnings.append("No peers supplied or all peers de-duplicated against anchor; statistics use anchor-only fallback")

    # Optional rationale map
    rationale_map: dict[str, str | None] = {}
    if args.rationale_map is not None:
        try:
            with args.rationale_map.open("r", encoding="utf-8") as f:
                rationale_map = json.load(f)
            if not isinstance(rationale_map, dict):
                warnings.append(f"--rationale-map {args.rationale_map} is not a JSON object; ignored")
                rationale_map = {}
        except (OSError, json.JSONDecodeError) as exc:
            warnings.append(f"--rationale-map {args.rationale_map} unreadable ({exc}); ignored")
            rationale_map = {}

    # Build peers payload
    peers_out: list[dict] = []
    for ticker, mults, _src, peer_class, _pack in peer_packs:
        entry: dict = {
            "ticker": ticker,
            "multiples": mults,
            "rationale": rationale_map.get(ticker),
        }
        if peer_class is not None:
            entry["schema_id"] = peer_class.schema_id
        peers_out.append(entry)

    # Statistics + anchor delta per multiple (peers only for stats, anchor excluded)
    stats: dict[str, dict] = {}
    anchor_delta: dict[str, dict | None] = {}
    for m in anchor_multiple_ids:
        peer_values = [
            mults[m] for _t, mults, _s, _c, _p in peer_packs if mults.get(m) is not None
        ]
        stats[m] = _stat_block(peer_values, anchor_multiples.get(m))
        anchor_delta[m] = _anchor_delta(anchor_multiples.get(m), peer_values)

    # Ranking across anchor + peers
    ranking = _build_ranking(anchor_ticker, anchor_multiples, peers_out, anchor_multiple_ids)

    # ---- Anchor block --------------------------------------------------
    anchor_block: dict = {"ticker": anchor_ticker}

    if effective_mode == "compute":
        # Per spec §8: emit sector / industry / schema_id / schema_routing_source
        anchor_info = (anchor_pack.get("info") or {}).get(anchor_ticker) or {}
        anchor_block["sector"] = anchor_info.get("sector")
        anchor_block["industry"] = anchor_info.get("industry")
        anchor_block["schema_id"] = anchor_classification.schema_id if anchor_classification else None
        anchor_block["schema_routing_source"] = anchor_classification.source if anchor_classification else None

    anchor_block["multiples_direct"] = anchor_multiples

    if effective_mode == "compute":
        multiples_compute, compute_provenance, compute_warnings = (
            _compute_multiples_from_memo_fetch(anchor_base, anchor_multiples, anchor_schema)
        )
        warnings.extend(compute_warnings)
        kinds = _schema_multiple_kinds(anchor_schema)
        passthrough_ids = {mid for mid, kind in kinds.items() if kind == "passthrough"}
        divergence = _compute_divergence(
            anchor_multiples, multiples_compute, compute_provenance,
            anchor_multiple_ids, passthrough_ids,
        )
        anchor_block["multiples_compute"] = multiples_compute
        anchor_block["divergence"] = divergence
        # Indicators (v2.2.0-c) — schema-driven; emit `{}` when schema has no
        # indicators (e.g. REIT). Provenance entries co-exist with multiples
        # provenance under the same compute_provenance dict, keyed by
        # indicator_id (no key collisions because indicator ids are distinct
        # from multiple ids per schema design).
        indicators, indicator_prov, indicator_warnings = (
            _compute_indicators_from_memo_fetch(anchor_base, anchor_schema)
        )
        warnings.extend(indicator_warnings)
        anchor_block["indicators"] = indicators
        compute_provenance.update(indicator_prov)
        anchor_block["compute_provenance"] = compute_provenance

    # ---- Provenance ----------------------------------------------------
    provenance: dict = {
        "skill":              "analysis-comps",
        "anchor_data_source": anchor_source,
    }
    if effective_mode == "compute":
        provenance["anchor_base_source"] = _provenance_label(anchor_base, args.anchor_base)
    provenance["peer_data_sources"] = [src for _t, _m, src, _c, _p in peer_packs]
    provenance["computed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    provenance["io"] = "none"
    provenance["mode"] = effective_mode
    provenance["requested_mode"] = requested_mode
    if effective_mode == "compute" and anchor_classification is not None and anchor_schema is not None:
        provenance["schema_id"] = anchor_classification.schema_id
        provenance["schema_version"] = anchor_schema.get("version")
        provenance["schema_routing_source"] = anchor_classification.source
    provenance["warnings"] = warnings

    payload = {
        "anchor":       anchor_block,
        "peers":        peers_out,
        "statistics":   stats,
        "anchor_delta": anchor_delta,
        "ranking":      ranking,
        "_provenance":  provenance,
    }

    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
