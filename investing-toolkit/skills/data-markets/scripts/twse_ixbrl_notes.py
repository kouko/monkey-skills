"""twse_ixbrl_notes.py — curated high-value note-field extraction (Layer B).

Pulls a small NAMED-concept set (4 categories: financial instruments by
measurement category, Mainland-China investment, related-party balances +
flows, employee-benefit expense + net liability) directly from the flat
fact-record list produced by twse_ixbrl_parser.parse_ixbrl_facts. This is
deliberately NOT a general note-table-reconstruction engine: an annual
verification pass across real filings falsified the "notes are a
machine-readable goldmine at scale" thesis (docs/loom/specs/2026-07-19-tw-
ixbrl-ingestion.md §Annual verification), so scope was cut down to this
curated set. A concept absent from a given filing's facts is OMITTED from
the result dict, never zero-filled.

Endorsement/guarantee and other per-counterparty ix:tuple-structured
disclosures are deferred to the note-table-reconstruction sub-arc (brief
§Annual verification / §Out of Scope) — they have no clean aggregate leaf
fact (e.g. LimitOfTotalGuaranteeEndorsementAmount repeats 4x under one
contextRef, one row per counterparty, with no single "total" fact to pick).

Usage (library import only — no CLI; composed by twse_ixbrl.py, Task 5):
    import twse_ixbrl_notes
    notes = twse_ixbrl_notes.extract_curated_notes(facts)
"""
from __future__ import annotations

import sys
from datetime import date
from typing import Any

_LOG_TAG = "twse-ixbrl-notes"


def _log(stage: str, msg: str = "") -> None:
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


# field name -> "ns:localname" concept, as it appears on the parsed fact
# record's "concept" key. Grouped by the 4 curated categories.
_CURATED_CONCEPTS: dict[str, str] = {
    # financial instruments by measurement category (current + non-current)
    "financial_assets_fvoci": (
        "ifrs-full:CurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"
    ),
    "financial_assets_fvoci_noncurrent": (
        "ifrs-full:NoncurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"
    ),
    "financial_assets_fvtpl": "ifrs-full:CurrentFinancialAssetsAtFairValueThroughProfitOrLoss",
    "financial_assets_fvtpl_noncurrent": (
        "ifrs-full:NoncurrentFinancialAssetsAtFairValueThroughProfitOrLoss"
    ),
    "financial_liabilities_fvtpl": (
        "ifrs-full:CurrentFinancialLiabilitiesAtFairValueThroughProfitOrLoss"
    ),
    "financial_assets_amortized_cost": "ifrs-full:CurrentFinancialAssetsAtAmortisedCost",
    "financial_assets_amortized_cost_noncurrent": (
        "ifrs-full:NoncurrentFinancialAssetsAtAmortisedCost"
    ),
    # Mainland-China investment
    "mainland_china_accumulated_investment": (
        "tifrs-notes:AccumulatedInvestmentInMainlandChinaAtTheEndOfThePeriod"
    ),
    "mainland_china_moea_ceiling": (
        "tifrs-notes:UpperLimitOnInvestmentInMainlandChinaImposedByTheInvestmentCommissionOfMOEA"
    ),
    # related-party total balances + aggregate purchase flow
    "related_party_receivable": "tifrs-notes:TotalAmountsReceivableFromRelatedParties",
    "related_party_payable": "tifrs-notes:TotalAmountsPayableToRelatedParties",
    "related_party_purchases": "tifrs-notes:TotalPurchasesOfGoods",
    # employee-benefit short-term expense + defined-benefit net liability
    "employee_benefit_short_term_expense": "tifrs-notes:ShortTermEmployeeBenefits",
    "employee_benefit_defined_benefit_net_liability": (
        "ifrs-full:NoncurrentRecognisedLiabilitiesDefinedBenefitPlan"
    ),
}


def _duration_days(start: str | None, end: str | None) -> int:
    if not start or not end:
        return 0
    try:
        return (date.fromisoformat(end) - date.fromisoformat(start)).days
    except ValueError:
        return 0


def _period_sort_key(period: dict[str, Any] | None) -> tuple[str, int]:
    """Sort key favoring the most recent, then the longest, period.

    Instant periods sort by the instant date. Duration periods sort by
    end date, then by duration length — so on an end-date tie (e.g. a
    quarterly vs. YTD cut of the same concept, both ending the same
    day) the longer/aggregate period wins over the shorter one.
    """
    if not period:
        return ("", 0)
    if period.get("type") == "instant":
        return (period.get("instant") or "", 0)
    end = period.get("end") or ""
    return (end, _duration_days(period.get("start"), end))


def _select_current_fact(facts_for_concept: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [f for f in facts_for_concept if f.get("raw_value") is not None]
    if not candidates:
        return None
    return max(candidates, key=lambda f: _period_sort_key(f.get("period")))


def extract_curated_notes(facts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Extract the curated named-concept fields from parsed fact records.

    Returns `{field: {"value": ..., "concept": ..., "period": ...}}`.
    A curated field whose concept is absent from `facts` is omitted
    entirely — never emitted with a zero-filled value.
    """
    by_concept: dict[str, list[dict[str, Any]]] = {}
    for fact in facts:
        concept = fact.get("concept")
        if concept:
            by_concept.setdefault(concept, []).append(fact)

    notes: dict[str, dict[str, Any]] = {}
    for field, concept in _CURATED_CONCEPTS.items():
        chosen = _select_current_fact(by_concept.get(concept, []))
        if chosen is None:
            continue
        notes[field] = {
            "value": chosen["raw_value"],
            "concept": concept,
            "period": chosen["period"],
        }

    missing = len(_CURATED_CONCEPTS) - len(notes)
    if missing:
        _log("curated notes partial", f"{len(notes)}/{len(_CURATED_CONCEPTS)} concepts present")

    return notes
