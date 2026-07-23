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

import re
import sys
from collections.abc import Callable, Iterator
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


def _select_current_fact(
    facts_for_concept: list[dict[str, Any]], label: str | None = None
) -> dict[str, Any] | None:
    """Pick the most-current fact by `_period_sort_key`.

    Tie-break when 2+ candidates share an identical period (e.g. a
    filing that mistakenly tags its 本期/去年同期 columns with the same
    contextRef — observed in the 2890 fixture's NPL table): `max()`
    returns the FIRST candidate in input/document order. That is a
    real rule this function relies on (first-in-document-order ==
    current, per the 本期-before-去年同期 column emission order), not
    an accident — when `label` is given, an ambiguous tie is logged so
    it's observable instead of silently depending on emission order.
    """
    candidates = [f for f in facts_for_concept if f.get("raw_value") is not None]
    if not candidates:
        return None
    chosen = max(candidates, key=lambda f: _period_sort_key(f.get("period")))
    if label is not None:
        chosen_key = _period_sort_key(chosen.get("period"))
        ties = [
            f
            for f in candidates
            if f is not chosen and _period_sort_key(f.get("period")) == chosen_key
        ]
        if ties:
            _log(
                "ambiguous period tie",
                f"{label}: {len(ties) + 1} candidates share period "
                f"{chosen.get('period')!r} — first-in-document-order wins",
            )
    return chosen


def _group_and_select_current(
    facts: list[dict[str, Any]],
    concept_map: dict[str, str],
    label_for: Callable[[str], str] | None = None,
) -> Iterator[tuple[str, str, dict[str, Any]]]:
    """Group `facts` by concept, then pick each mapped concept's current fact.

    Yields `(field, concept, chosen)` for every `concept_map` entry
    whose concept has a selectable fact in `facts`; an absent concept
    yields nothing (the never-zero-fill rule shared by all three
    extractors). `label_for` maps a field name to the tie-log label
    passed to `_select_current_fact` — `None` disables tie logging
    (the extract_curated_notes behavior).
    """
    by_concept: dict[str, list[dict[str, Any]]] = {}
    for fact in facts:
        concept = fact.get("concept")
        if concept:
            by_concept.setdefault(concept, []).append(fact)

    for field, concept in concept_map.items():
        chosen = _select_current_fact(
            by_concept.get(concept, []),
            label=label_for(field) if label_for is not None else None,
        )
        if chosen is None:
            continue
        yield field, concept, chosen


def extract_curated_notes(facts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Extract the curated named-concept fields from parsed fact records.

    Returns `{field: {"value": ..., "concept": ..., "period": ...}}`.
    A curated field whose concept is absent from `facts` is omitted
    entirely — never emitted with a zero-filled value.
    """
    notes: dict[str, dict[str, Any]] = {}
    for field, concept, chosen in _group_and_select_current(facts, _CURATED_CONCEPTS):
        notes[field] = {
            "value": chosen["raw_value"],
            "concept": concept,
            "period": chosen["period"],
        }

    missing = len(_CURATED_CONCEPTS) - len(notes)
    if missing:
        _log("curated notes partial", f"{len(notes)}/{len(_CURATED_CONCEPTS)} concepts present")

    return notes


# -fh (financial holding) bank-subsidiary NPL/coverage note (Task 9).
#
# field name -> "ns:localname" concept for the TotalLoans (tuple_ref="TL")
# row of the 逾期放款 (non-performing loans) ix:tuple tree. Distinct from
# _CURATED_CONCEPTS: this is -fh-specific and keyed by tuple_ref, not a
# flat concept lookup, so it lives in its own map/function rather than
# overloading extract_curated_notes.
_FH_TOTAL_LOANS_CONCEPTS: dict[str, str] = {
    "npl_amount": "tifrs-notes:AmountOfNon-PerformingLoans",
    "gross_loans": "tifrs-notes:GrossLoans",
    "npl_ratio": "tifrs-notes:Non-PerformingLoansRatio",
    "allowance_for_bad_debts": "tifrs-notes:AllowanceForBadDebts-AssetQualityForBankSubsidiaries",
    "coverage_ratio": "tifrs-notes:CoverageRatio",
}

# npl_ratio/coverage_ratio carry unitRef="Pure" with scale=-2 (e.g. raw
# text "1,031.17" -> parser raw_value 10.3117, the true fraction). This
# extractor presents them as the conventional percentage (x100) — a
# single, well-defined conversion, not a second application of the
# XBRL `scale` attribute.
_FH_PERCENT_FIELDS = {"npl_ratio", "coverage_ratio"}

# A NameOfTheCompany fact whose tuple_ref is a bare "NPL<n>" root marks
# the start of one bank subsidiary's NPL (loans) tuple tree. Siblings
# "NPR<n>" (逾期帳款/receivables tree) and "NPLANPREFRTTCA<n>" (a combined
# total tree) are deliberately excluded by this pattern.
_NPL_ROOT_RE = re.compile(r"^NPL\d+$")


def _fh_npl_tree_segments(
    facts: list[dict[str, Any]],
) -> list[tuple[int, int, str]]:
    """Split `facts` into per-subsidiary (start, end, company_name) spans.

    LOOM-SIMPLIFY: subsidiaries are segmented by DOCUMENT ORDER (the
    span between one NPL<n>-rooted NameOfTheCompany marker and the
    next), not by a parsed ix:tuple nesting hierarchy — the parser
    layer (twse_ixbrl_parser.py) only records a leaf fact's own
    tupleRef, never the wrapping <ix:tuple> elements' tupleID/tupleRef
    chain, so there is no in-band way to confirm which physical tree a
    "TL"-tagged row belongs to other than position. | ceiling: if a
    future fetched -fh filing is ever observed with a subsidiary's NPL
    rows NOT contiguous immediately after its own NameOfTheCompany
    marker (interleaved trees) | upgrade: extend
    twse_ixbrl_parser.parse_ixbrl_facts to also capture <ix:tuple>
    elements' own tupleID/tupleRef so category rows can be matched to
    a subsidiary by explicit tuple-parent chain instead of order |
    ref: 2890 fixture measurement — a post-merger FHC carries
    duplicated parallel NPL tuple trees (one per bank subsidiary),
    each tree's rows contiguous in document order immediately after
    its own NPL<n>-rooted NameOfTheCompany marker.
    """
    boundaries = [
        (i, f["raw_value"])
        for i, f in enumerate(facts)
        if f.get("concept") == "tifrs-notes:NameOfTheCompany"
        and _NPL_ROOT_RE.match(f.get("tuple_ref") or "")
        and f.get("raw_value")
    ]
    return [
        (start, boundaries[idx + 1][0] if idx + 1 < len(boundaries) else len(facts), name)
        for idx, (start, name) in enumerate(boundaries)
    ]


def extract_fh_npl_coverage_notes(facts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Extract the -fh TotalLoans NPL/coverage row, keyed by bank subsidiary.

    Each bank subsidiary's 逾期放款 (non-performing loans) note is an
    ix:tuple tree with 7 loan-category rows sharing one contextRef,
    disambiguated only by the `tuple_ref` attribute; this function
    selects the TotalLoans row (tuple_ref="TL"). A -fh (financial
    holding) filing scopes this note to the ONE banking subsidiary
    (via `tifrs-notes:NameOfTheCompany`), never the FHC group total —
    and a post-merger FHC can carry duplicated parallel trees, one per
    bank subsidiary, so the result is keyed by subsidiary name rather
    than returning a single value.

    Returns `{subsidiary_name: {field: {"value", "concept", "period"}}}`.
    A filing with no NPL tuple tree (non -fh, or the note absent) yields
    `{}`. A field whose concept is absent for a given subsidiary's
    TotalLoans row is omitted, never zero-filled (mirrors
    extract_curated_notes).
    """
    result: dict[str, dict[str, Any]] = {}
    for start, end, company in _fh_npl_tree_segments(facts):
        total_loans_facts = [
            f for f in facts[start:end] if f.get("tuple_ref") == "TL"
        ]
        fields: dict[str, Any] = {}
        # label_for makes an identical-period tie (e.g. the 2890 fixture's
        # 本期/去年同期 columns sharing one contextRef) observable via
        # _log instead of silently depending on document order.
        for field, concept, chosen in _group_and_select_current(
            total_loans_facts,
            _FH_TOTAL_LOANS_CONCEPTS,
            label_for=lambda field: f"{company}/{field}",
        ):
            value = chosen["raw_value"]
            if field in _FH_PERCENT_FIELDS and value is not None:
                value = value * 100
            fields[field] = {
                "value": value,
                "concept": concept,
                "period": chosen["period"],
            }

        if fields:
            result[company] = fields

    return result


# -basi (standalone commercial bank / bills-finance) NPL/coverage note
# (Task 10). Unlike -fh (Task 9), which disambiguates 7 sibling
# loan-category rows via the ix:tuple `tuple_ref` attribute, -basi
# filers encode the loan category in the CONTEXT_REF SUFFIX (e.g.
# "AsOf20260331_TotalLoansMember") together with a "Member"-suffixed
# concept name (e.g. "CoverageRatioMember") — the existing generic
# parser already resolves concept + context_ref, so no tuple metadata
# is needed. Lives in its own map/function (mirrors _FH_TOTAL_LOANS_CONCEPTS)
# rather than overloading extract_curated_notes or
# extract_fh_npl_coverage_notes, since the disambiguation mechanism differs.
_BASI_TOTAL_LOANS_CONCEPTS: dict[str, str] = {
    "npl_amount": "tifrs-notes:AmountOfNon-PerformingLoansMember",
    "gross_loans": "tifrs-notes:GrossLoansMember",
    "npl_ratio": "tifrs-notes:NonPerformingLoansRatioMember",
    "coverage_ratio": "tifrs-notes:CoverageRatioMember",
}

# npl_ratio/coverage_ratio carry unitRef="Pure" with scale=-2, same
# single x100 presentation convention as _FH_PERCENT_FIELDS.
_BASI_PERCENT_FIELDS = {"npl_ratio", "coverage_ratio"}

# A fact's context_ref ending in this suffix scopes it to the TotalLoans
# row of the 逾期放款 (non-performing loans) note (e.g.
# "AsOf20260331_TotalLoansMember").
_BASI_TOTAL_LOANS_CONTEXT_SUFFIX = "_TotalLoansMember"

_BASI_COMPANY_NAME_CONCEPT = "tifrs-notes:NameOfTheCompany"


def extract_basi_npl_coverage_notes(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Extract the -basi TotalLoans NPL/coverage row.

    Standalone banks and bills-finance filers (-basi taxonomy) encode
    the loan category via a context_ref SUFFIX (e.g.
    "AsOf20260331_TotalLoansMember") plus a "Member"-suffixed concept
    name, not ix:tuple attributes (contrast
    extract_fh_npl_coverage_notes) — the existing generic parser
    already captures concept + context_ref on every fact, so no tuple
    parsing is required here.

    Returns `{"npl_amount", "gross_loans", "npl_ratio",
    "coverage_ratio", "company_name": {"value", "concept", "period"}}`.
    A field whose concept is absent for the TotalLoans row is omitted
    (mirrors extract_curated_notes / extract_fh_npl_coverage_notes). A
    filing with no -basi NPL note at all (e.g. bills-finance -basi
    filers, which carry no NPL/coverage concepts whatsoever) yields
    `{}` gracefully — never raises.
    """
    total_loans_facts = [
        f
        for f in facts
        if (f.get("context_ref") or "").endswith(_BASI_TOTAL_LOANS_CONTEXT_SUFFIX)
    ]
    fields: dict[str, Any] = {}
    for field, concept, chosen in _group_and_select_current(
        total_loans_facts,
        _BASI_TOTAL_LOANS_CONCEPTS,
        label_for=lambda field: f"basi/{field}",
    ):
        value = chosen["raw_value"]
        if field in _BASI_PERCENT_FIELDS and value is not None:
            value = value * 100
        fields[field] = {
            "value": value,
            "concept": concept,
            "period": chosen["period"],
        }

    if fields:
        company = _select_current_fact(
            [f for f in facts if f.get("concept") == _BASI_COMPANY_NAME_CONCEPT],
            label="basi/company_name",
        )
        if company is not None:
            fields["company_name"] = {
                "value": company["raw_value"],
                "concept": _BASI_COMPANY_NAME_CONCEPT,
                "period": company["period"],
            }

    return fields
