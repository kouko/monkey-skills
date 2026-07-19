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
from typing import Any

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

# Debt-bearing concepts observed (or defensively anticipated, see below) in
# the -ci (industrial) taxonomy for balance_sheet.total_debt (dcf_compute.py
# :220-222 requires this). Summed per matching AsOf date across whichever
# of these are present in the fact set — a filer need not carry all of them.
#
# Short-term/current interest-bearing components (ShorttermBorrowings /
# CurrentPortionOfNoncurrentBondsIssued / CurrentFinanceLeaseLiabilities)
# were added by whole-branch-review remediation (long-term-only total_debt
# understated net_debt -> overstated DCF equity value). The committed 2330
# fixture (TSMC, cash-rich) carries none of these — confirmed absent by
# grep -a over the raw fixture bytes for Shortterm*/Current*Borrowing*/
# Bond*/Lease* — so their concrete concept names are chosen symmetrically
# with the confirmed long-term siblings above (Longterm -> Shortterm,
# NoncurrentPortionOf... -> CurrentPortionOf..., Noncurrent... ->
# Current...) rather than traced against a real fact; a filer that does
# carry one will still be summed in correctly since the concept is present
# in _DEBT_CONCEPTS. See test_canonical_ci_total_debt_sums_short_term_debt_when_present
# for the synthetic-fact proof.
#
# LOOM-SIMPLIFY: excludes tifrs-bsci-ci:LongtermLiabilitiesCurrentPortion
#   (the "current portion of long-term liabilities" line) — that concept is
#   an unsplit grab-bag (could bundle non-debt long-term items, not proven
#   debt-only from the fixture alone). It remains the ONLY exclusion from
#   total_debt among clearly debt-shaped concepts observed so far.
# ceiling: before extending TW iXBRL canonical mapping to a second -ci
#   fixture/filer (next real fixture added to tests/data/fixtures/).
# upgrade: split/verify LongtermLiabilitiesCurrentPortion's composition
#   against that filer's notes and fold the debt-only portion into
#   _DEBT_CONCEPTS if confirmed; also confirm/correct the short-term concept
#   names above against that filer's actual facts.
# ref: docs/loom/plans/2026-07-19-tw-ixbrl-ingestion.md Task 6 round-2 review.
_DEBT_CONCEPTS: tuple[str, ...] = (
    "ifrs-full:LongtermBorrowings",
    "ifrs-full:NoncurrentPortionOfNoncurrentBondsIssued",
    "ifrs-full:NoncurrentFinanceLeaseLiabilities",
    "ifrs-full:ShorttermBorrowings",
    "ifrs-full:CurrentPortionOfNoncurrentBondsIssued",
    "ifrs-full:CurrentFinanceLeaseLiabilities",
)


def _is_fh_taxonomy(facts: list[dict[str, Any]]) -> bool:
    """Financial-holding filers use a "-fh" namespace token in place of
    the industrial "-ci"/"-SCF" tokens (e.g. "tifrs-bsci-fh"). Detect by
    namespace-prefix token, not full-string match, so it survives the
    company/statement-suffix variations across the -fh taxonomy family.
    """
    for fact in facts:
        concept = fact.get("concept") or ""
        namespace = concept.split(":", 1)[0]
        if "fh" in namespace.split("-"):
            return True
    return False


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


def build_canonical(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Map parsed iXBRL facts into the canonical three-statement shape.

    Industrial (-ci) filers only. A -fh (financial holding) fact set
    returns {"unsupported": "financial-fh", ...} instead of a mapping —
    the -fh statement taxonomy is a deferred sub-arc, and mapping
    -fh concepts through the -ci concept map would silently emit an
    empty/wrong canonical shape rather than failing loud.
    """
    if _is_fh_taxonomy(facts):
        return {
            "unsupported": "financial-fh",
            "reason": (
                "financial-holding (-fh) filers use a different statement "
                "taxonomy than industrial (-ci) filers; -fh canonical "
                "mapping is a deferred sub-arc (see docs/loom/plans/"
                "2026-07-19-tw-ixbrl-ingestion.md Decision Log)"
            ),
        }

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
