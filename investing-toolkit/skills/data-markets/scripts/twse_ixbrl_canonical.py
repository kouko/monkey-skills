"""twse_ixbrl_canonical.py — canonical three-statement mapper for TW
MOPS iXBRL facts (industrial `-ci` filers only; Task 3).

Maps a flat fact-record list (twse_ixbrl_parser.parse_ixbrl_facts
output, Task 1) into the toolkit's canonical shape — the same shape
pack_tw.py's `_build_canonical_from_yf_financials_tw` (:205-311)
produces: three top-level keys `income_statement` / `balance_sheet` /
`cash_flow`, each a value-list (most-recent-first) plus a per-line
`_meta` (`source_label`, `concept`, `accounting_standard="tifrs"`,
`unit="TWD"`).

Scope: industrial (一般行業, "-ci") filers only. Financial-holding
("-fh") filers use a different statement taxonomy entirely (deferred
sub-arc per docs/loom/plans/2026-07-19-tw-ixbrl-ingestion.md Decision
Log) — an -fh fact set returns an explicit unsupported marker instead
of a wrong/crashing mapping.

Line concepts live mostly in the `ifrs-full` namespace for -ci filers
(the standard IFRS taxonomy); `tifrs-bsci-ci` covers only TW-specific
supplementary line items (not the primary statement totals), and
`tifrs-SCF` covers cash-flow-statement-specific concepts not present
in `ifrs-full`.

Usage (as a library import — no CLI; composed by twse_ixbrl.py, Task 5):
    import twse_ixbrl_canonical
    canonical = twse_ixbrl_canonical.build_canonical(facts)
"""
from __future__ import annotations

import re
import sys
from datetime import date
from typing import Any, Literal

_LOG_TAG = "twse-ixbrl-canonical"


def _log(stage: str, msg: str = "") -> None:
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


# Only "base" (undimensioned) contexts represent statement-total facts;
# axis/member contexts (e.g. "AsOf20240101_OrdinaryShareMember") carry
# equity-roll-forward / component breakdowns, not the line total.
_BASE_CONTEXT_RE = re.compile(r"^(AsOf\d{8}|From\d{8}To\d{8})$")

_CONCEPT_MAP: dict[str, dict[str, str]] = {
    "income_statement": {
        "revenue": "ifrs-full:Revenue",
        "gross_profit": "ifrs-full:GrossProfit",
        "operating_income": "ifrs-full:ProfitLossFromOperatingActivities",
        # ebit is an alias of operating_income (same concept) — analysis-dcf's
        # dcf_compute.py (:171, :193-198) prefers "ebit" over operating_income
        # explicitly; without this key it silently falls back to net_income.
        "ebit": "ifrs-full:ProfitLossFromOperatingActivities",
        "pretax_income": "ifrs-full:ProfitLossBeforeTax",
        "net_income": "ifrs-full:ProfitLossAttributableToOwnersOfParent",
        "eps_basic": "ifrs-full:BasicEarningsLossPerShare",
    },
    "balance_sheet": {
        "total_assets": "ifrs-full:Assets",
        "total_liabilities": "ifrs-full:Liabilities",
        "total_equity": "ifrs-full:Equity",
        # dcf_compute.py (:220-222) requires this to compute net_debt; absent
        # → silently 0.0 → net_debt=0 for every TW ticker (round-2 fix 🔴).
        "cash": "ifrs-full:CashAndCashEquivalents",
    },
    "cash_flow": {
        "operating_cash_flow": "ifrs-full:CashFlowsFromUsedInOperatingActivities",
        "investing_cash_flow": "tifrs-SCF:NetCashFlowsFromUsedInInvestingActivities",
        "financing_cash_flow": "tifrs-SCF:CashFlowsFromUsedInFinancingActivities",
        "capex": "ifrs-full:PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities",
    },
}

_LABELS: dict[str, str] = {
    "revenue": "Revenue",
    "gross_profit": "Gross Profit",
    "operating_income": "Profit (Loss) from Operating Activities",
    "ebit": "Profit (Loss) from Operating Activities",
    "pretax_income": "Profit (Loss) before Tax",
    "net_income": "Profit (Loss) Attributable to Owners of Parent",
    "eps_basic": "Basic Earnings (Loss) per Share",
    "total_assets": "Assets",
    "total_liabilities": "Liabilities",
    "total_equity": "Equity",
    "cash": "Cash and Cash Equivalents",
    "operating_cash_flow": "Cash Flows from (used in) Operating Activities",
    "investing_cash_flow": "Net Cash Flows from (used in) Investing Activities",
    "financing_cash_flow": "Cash Flows from (used in) Financing Activities",
    "capex": "Purchase of Property, Plant and Equipment (Investing Activities)",
}

# Debt-bearing concepts for the -ci (industrial) taxonomy's
# balance_sheet.total_debt (dcf_compute.py :220-222 requires this). Summed
# per matching AsOf date across whichever of these are present in the fact
# set — a filer need not carry all of them.
#
# All 7 concepts below (3 long-term + 4 short-term/current) are verified
# present via grep -a against two real -ci filers' raw fixture bytes:
#   - 2330 (TSMC, 2024Q3 C): carries the 3 long-term concepts only
#     (cash-rich filer, genuinely zero short-term borrowings that quarter).
#   - 1301 (Formosa Plastics, 2024Q3 C): carries all 7 — the debt-heavy
#     filer that proves the short-term components are real concept names,
#     not guesses. See test_canonical_ci_total_debt_formosa_includes_short_term.
#
# The set = every clearly interest-bearing ST + LT debt line observed across
# both filers. The one deliberate, permanent exclusion is the unsplit
# grab-bag tifrs-bsci-ci:LongtermLiabilitiesCurrentPortion — it can bundle
# non-debt long-term items and is not proven debt-only by either fixture,
# so it stays out of total_debt rather than risk overstating it.
# ref: docs/loom/plans/2026-07-19-tw-ixbrl-ingestion.md Task 6 round-2 review.
_DEBT_CONCEPTS: tuple[str, ...] = (
    "ifrs-full:LongtermBorrowings",
    "ifrs-full:NoncurrentPortionOfNoncurrentBondsIssued",
    "ifrs-full:NoncurrentFinanceLeaseLiabilities",
    "ifrs-full:ShorttermBorrowings",
    "ifrs-full:CurrentPortionOfLongtermBorrowings",
    "ifrs-full:CurrentBondsIssuedAndCurrentPortionOfNoncurrentBondsIssued",
    "ifrs-full:CurrentCommercialPapersIssuedAndCurrentPortionOfNoncurrentCommercialPapersIssued",
)


# TW MOPS iXBRL statement taxonomies split by industry family: each filing
# carries exactly one tifrs-bsci-<family> namespace (measured across the
# committed fixtures). "basi" covers standalone banks AND bills-finance.
_BSCI_TAG_PREFIXES: dict[str, str] = {
    "tifrs-bsci-ci": "ci",      # 一般行業 (industrial)
    "tifrs-bsci-fh": "fh",      # 金融控股 (financial holding)
    "tifrs-bsci-basi": "basi",  # 銀行 / 票券金融 (banks & bills-finance)
    "tifrs-bsci-bd": "bd",      # 證券 (securities/broker-dealer)
    "tifrs-bsci-ins": "ins",    # 保險 (insurance)
}

TaxonomyTag = Literal["ci", "fh", "basi", "bd", "ins"]


def classify_taxonomy(facts: list[dict[str, Any]]) -> TaxonomyTag:
    """Classify a fact set by the tifrs-bsci-<family> namespace prefix its
    concepts carry, returning the family tag ("ci"/"fh"/"basi"/"bd"/"ins").

    -ci (industrial) filers put their primary statement totals in the
    ifrs-full namespace and use tifrs-bsci-ci only for TW-specific
    supplementary lines; a fact set with NO recognized tifrs-bsci-* family
    at all is therefore treated as "ci" (the industrial default, and the
    shape synthetic ifrs-full-only fact sets take).

    Tie-break (not observed in measurement — each real filing carries exactly
    one family): if more than one recognized family appears, the more
    specific financial family wins over the industrial "ci" supplementary
    tag; among multiple financial families the sorted-first tag is chosen,
    deterministically, with the anomaly logged.
    """
    found: set[str] = set()
    for fact in facts:
        concept = fact.get("concept") or ""
        prefix = concept.split(":", 1)[0]
        tag = _BSCI_TAG_PREFIXES.get(prefix)
        if tag:
            found.add(tag)

    if not found:
        return "ci"
    if len(found) == 1:
        return next(iter(found))  # type: ignore[return-value]

    _log("multiple bsci families", f"found={sorted(found)}")
    found.discard("ci")
    if not found:
        return "ci"
    return sorted(found)[0]  # type: ignore[return-value]


def _period_sort_key(period: dict[str, Any] | None) -> tuple[str, int]:
    """Sort key: (period end/instant date, duration span in days).
    Ties on end date (a quarter-only duration and a YTD-cumulative
    duration both ending on the same filing date) resolve to the
    longer/cumulative span first — TW quarterly filings headline the
    YTD-cumulative figure over the quarter-only one.
    """
    if not period:
        return ("", 0)
    if period.get("type") == "instant":
        return (period.get("instant") or "", 0)
    start = period.get("start") or ""
    end = period.get("end") or ""
    span = 0
    if start and end:
        try:
            span = (date.fromisoformat(end) - date.fromisoformat(start)).days
        except ValueError:
            _log("bad period bounds", f"start={start!r} end={end!r}")
    return (end, span)


def _derive_total_debt(
    by_concept: dict[str, dict[str, dict[str, Any]]],
) -> tuple[list[float], dict[str, Any]] | None:
    """Sum whichever _DEBT_CONCEPTS are present in the fact set, per matching
    AsOf date. Returns None (field stays absent) if none of the debt
    concepts are present at all — an absent field is preferable to a wrong
    total_debt=0.0 fabricated from nothing.
    """
    sums: dict[str, float] = {}
    periods_by_ctx: dict[str, Any] = {}
    concepts_used: list[str] = []
    for concept in _DEBT_CONCEPTS:
        ctx_facts = by_concept.get(concept)
        if not ctx_facts:
            continue
        concepts_used.append(concept)
        for context_ref, fact in ctx_facts.items():
            value = fact.get("raw_value")
            if value is None:
                continue
            sums[context_ref] = sums.get(context_ref, 0.0) + value
            periods_by_ctx[context_ref] = fact.get("period")

    if not concepts_used:
        return None

    ordered_ctx = sorted(
        sums.keys(), key=lambda c: _period_sort_key(periods_by_ctx.get(c)), reverse=True
    )
    values = [sums[c] for c in ordered_ctx]
    meta = {
        "source_label": "Total Debt (sum of components present)",
        "concept": None,
        "accounting_standard": "tifrs",
        "unit": "TWD",
        "periods": [periods_by_ctx.get(c) for c in ordered_ctx],
        "derivation": "sum of " + " + ".join(concepts_used),
        "components": concepts_used,
    }
    return values, meta


def _derive_fcf(cash_flow: dict[str, Any]) -> tuple[list[float], dict[str, Any]] | None:
    """fcf = operating_cash_flow - capex, paired positionally (both series
    are independently sorted most-recent-first by the same period key, so
    index i is the same reporting period on both sides for a normal filing
    that reports both lines for the same period set)."""
    ocf = cash_flow.get("operating_cash_flow")
    capex = cash_flow.get("capex")
    if not ocf or not capex:
        return None

    n = min(len(ocf), len(capex))
    values = [ocf[i] - capex[i] for i in range(n)]
    ocf_periods = cash_flow["_meta"]["operating_cash_flow"]["periods"]
    meta = {
        "source_label": "Free Cash Flow (derived)",
        "concept": None,
        "accounting_standard": "tifrs",
        "unit": "TWD",
        "periods": ocf_periods[:n],
        "derivation": "operating_cash_flow - capex",
        "components": ["operating_cash_flow", "capex"],
    }
    return values, meta


def _unsupported_financial() -> dict[str, Any]:
    """The marker returned for any financial taxonomy (fh/basi/bd/ins) that
    has no canonical builder registered yet — those builders land in later
    tasks (T5-T8). Mapping financial concepts through the -ci concept map
    would silently emit an empty/wrong canonical shape rather than failing
    loud, so an explicit unsupported marker is returned instead. A fresh
    dict per call avoids callers mutating a shared constant.
    """
    return {
        "unsupported": "financial-fh",
        "reason": (
            "financial-holding (-fh) filers use a different statement "
            "taxonomy than industrial (-ci) filers; -fh canonical "
            "mapping is a deferred sub-arc (see docs/loom/plans/"
            "2026-07-19-tw-ixbrl-ingestion.md Decision Log)"
        ),
    }


def _build_ci_canonical(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Map an industrial (-ci) fact set into the canonical three-statement
    shape (income_statement / balance_sheet / cash_flow + per-line _meta)."""
    by_concept: dict[str, dict[str, dict[str, Any]]] = {}
    for fact in facts:
        concept = fact.get("concept")
        context_ref = fact.get("context_ref")
        if not concept or not context_ref or not _BASE_CONTEXT_RE.match(context_ref):
            continue
        if fact.get("raw_value") is None:
            continue
        by_concept.setdefault(concept, {})[context_ref] = fact

    canonical: dict[str, Any] = {}
    for statement, mapping in _CONCEPT_MAP.items():
        lines: dict[str, Any] = {}
        meta: dict[str, Any] = {}
        for canonical_name, concept in mapping.items():
            ctx_facts = by_concept.get(concept)
            if not ctx_facts:
                continue
            ordered = sorted(
                ctx_facts.values(),
                key=lambda f: _period_sort_key(f.get("period")),
                reverse=True,
            )
            lines[canonical_name] = [f["raw_value"] for f in ordered]
            meta[canonical_name] = {
                "source_label": _LABELS.get(canonical_name, canonical_name),
                "concept": concept,
                "accounting_standard": "tifrs",
                "unit": "TWD",
                "periods": [f.get("period") for f in ordered],
            }
        lines["_meta"] = meta
        canonical[statement] = lines

    # capex's raw fact is signed negative (cash outflow, sign="-" in the
    # fixture); canonical convention across every market's pack.py
    # (pack_us/jp/kr/cn) stores capex as an absolute value.
    cash_flow = canonical.get("cash_flow", {})
    if cash_flow.get("capex"):
        cash_flow["capex"] = [abs(v) for v in cash_flow["capex"]]
        cash_flow["_meta"]["capex"]["note"] = "absolute value (fixture raw sign is negative cash outflow)"

    income_statement = canonical.get("income_statement", {})
    if income_statement.get("ebit"):
        income_statement["_meta"]["ebit"]["note"] = "alias of operating_income"

    fcf_result = _derive_fcf(cash_flow)
    if fcf_result:
        values, meta = fcf_result
        cash_flow["fcf"] = values
        cash_flow["_meta"]["fcf"] = meta

    balance_sheet = canonical.get("balance_sheet", {})
    debt_result = _derive_total_debt(by_concept)
    if debt_result:
        values, meta = debt_result
        balance_sheet["total_debt"] = values
        balance_sheet["_meta"]["total_debt"] = meta

    return canonical


# Builder registry: taxonomy tag -> canonical builder callable. Only "ci"
# has a builder today; the financial families (fh/basi/bd/ins) land in later
# tasks (T5-T8) and register their builders here. A tag with no registered
# builder falls through to the unsupported marker (_unsupported_financial).
_CANONICAL_BUILDERS: dict[str, Any] = {
    "ci": _build_ci_canonical,
}


def build_canonical(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Map parsed iXBRL facts into the canonical three-statement shape by
    routing on the fact set's taxonomy family (classify_taxonomy).

    Industrial (-ci) filers map through _build_ci_canonical. Financial
    families (fh/basi/bd/ins) have no builder registered yet, so they return
    an explicit unsupported marker instead of a wrong/empty mapping — their
    builders are a deferred sub-arc (T5-T8, see docs/loom/plans/
    2026-07-19-tw-ixbrl-ingestion.md Decision Log).
    """
    tag = classify_taxonomy(facts)
    builder = _CANONICAL_BUILDERS.get(tag)
    if builder is None:
        return _unsupported_financial()
    return builder(facts)
