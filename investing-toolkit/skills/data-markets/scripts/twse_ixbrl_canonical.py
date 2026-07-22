"""twse_ixbrl_canonical.py — canonical three-statement mapper for TW
MOPS iXBRL facts (industrial `-ci` filers, Task 3; financial-holding
`-fh` filers, Task 5; standalone-bank / bills-finance `-basi` filers,
Task 6; broker-dealer `-bd` filers, Task 7).

Maps a flat fact-record list (twse_ixbrl_parser.parse_ixbrl_facts
output, Task 1) into the toolkit's canonical shape — the same shape
pack_tw.py's `_build_canonical_from_yf_financials_tw` (:205-311)
produces: three top-level keys `income_statement` / `balance_sheet` /
`cash_flow`, each a value-list (most-recent-first) plus a per-line
`_meta` (`source_label`, `concept`, `accounting_standard="tifrs"`,
`unit="TWD"`).

Scope: industrial (一般行業, "-ci"), financial-holding (金融控股,
"-fh"), standalone-bank/bills-finance (銀行/票券金融, "-basi"), and
broker-dealer/securities (證券, "-bd") filers. The remaining financial
family (insurance, "-ins") uses a statement taxonomy entirely of its
own (a deferred sub-arc per docs/loom/plans/2026-07-19-tw-ixbrl-
ingestion.md Decision Log) — a fact set from that family returns an
explicit unsupported marker instead of a wrong/crashing mapping.

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


def _unsupported_financial(tag: str) -> dict[str, Any]:
    """The marker returned for any financial taxonomy family (basi/bd/ins,
    or any future tag) that has no canonical builder registered yet.
    Mapping financial concepts through the -ci concept map would silently
    emit an empty/wrong canonical shape rather than failing loud, so an
    explicit unsupported marker is returned instead. The marker is
    family-accurate (`financial-<tag>`) rather than hard-coded, so it stays
    correct as builders land for some families but not others. A fresh
    dict per call avoids callers mutating a shared constant.
    """
    return {
        "unsupported": f"financial-{tag}",
        "reason": (
            f"the '{tag}' financial taxonomy family uses a different "
            "statement taxonomy than industrial (-ci) filers; its "
            "canonical mapping is a deferred sub-arc (see docs/loom/plans/"
            "2026-07-19-tw-ixbrl-ingestion.md Decision Log) until a "
            "dedicated builder is registered"
        ),
    }


def _index_by_concept(facts: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """Index base-context (undimensioned) facts by concept -> context_ref
    -> fact. Shared by every canonical builder (ci, fh, ...)."""
    by_concept: dict[str, dict[str, dict[str, Any]]] = {}
    for fact in facts:
        concept = fact.get("concept")
        context_ref = fact.get("context_ref")
        if not concept or not context_ref or not _BASE_CONTEXT_RE.match(context_ref):
            continue
        if fact.get("raw_value") is None:
            continue
        by_concept.setdefault(concept, {})[context_ref] = fact
    return by_concept


def _build_ci_canonical(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Map an industrial (-ci) fact set into the canonical three-statement
    shape (income_statement / balance_sheet / cash_flow + per-line _meta)."""
    by_concept = _index_by_concept(facts)

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


# -fh (financial-holding) concept map — simple 1:1 concepts (no summing).
# DCF-trigger fields (revenue/ebit/fcf/capex/total_debt) are deliberately
# absent: an FHC's statement shape has no such lines and DCF must fail loud
# on their absence rather than silently compute against a zero.
_FH_CONCEPT_MAP: dict[str, dict[str, str]] = {
    "balance_sheet": {
        "total_assets": "ifrs-full:Assets",
        "total_equity": "ifrs-full:Equity",
        "cash": "ifrs-full:CashAndCashEquivalents",
    },
    "income_statement": {
        "net_interest_income": "tifrs-bsci-fh:NetInterestIncomeExpense",
        # Keys net_income/eps_basic (not profit/eps) to match the -ci
        # _CONCEPT_MAP convention (:59,:60) — pack_tw.py reads exactly
        # these key names (grepped: net_income/eps_basic, ~:194,242,273,278);
        # a different key name would make pack_tw silently drop the FHC's
        # net income, the same wrong-answer class as the total_debt-
        # defaults-to-0 bug the -ci arc hit.
        #
        # Concept choice is still deliberately
        # ifrs-full:ProfitLossAttributableToOwnersOfParent (the
        # consolidated attributable-to-owners bottom line) — NOT
        # tifrs-bsci-fh:NetIncomeLoss, which is a different, larger
        # pre-elimination subtotal that does not match this figure (measured
        # on 2882 2026Q1: 31,593,811,000 vs 72,538,053,000; see
        # scratchpad/fh-measurement.md §2882).
        "net_income": "ifrs-full:ProfitLossAttributableToOwnersOfParent",
        "eps_basic": "ifrs-full:BasicEarningsLossPerShare",
    },
}

_FH_LABELS: dict[str, str] = {
    "total_assets": "Assets",
    "total_equity": "Equity",
    "cash": "Cash and Cash Equivalents",
    "net_interest_income": "Net Interest Income (Expense)",
    "net_income": "Profit (Loss) Attributable to Owners of Parent",
    "eps_basic": "Basic Earnings (Loss) per Share",
}

# Deposits are kept DISTINCT from interest-bearing borrowings — the two
# concept groups below are summed separately, never merged, so a consumer
# can tell customer/interbank deposits apart from bonds/CP/repo funding.
_DEPOSIT_CONCEPTS: tuple[str, ...] = (
    "ifrs-full:DepositsFromCustomers",
    "ifrs-full:DepositsFromBanks",
)
_BORROWING_CONCEPTS: tuple[str, ...] = (
    "ifrs-full:BondsIssued",
    "ifrs-full:OtherBorrowings",
    "tifrs-bsci-fh:CommercialPapersIssuedNet",
    "tifrs-bsci-fh:SecuritiesSoldUnderRepurchaseAgreements",
)


def _sum_concepts(
    by_concept: dict[str, dict[str, dict[str, Any]]],
    concepts: tuple[str, ...],
    source_label: str,
) -> tuple[list[float], dict[str, Any]] | None:
    """Sum whichever of `concepts` are present in the fact set, per matching
    context_ref (same pattern as _derive_total_debt, generalized for reuse
    by any "sum of components present" field). Returns None (field stays
    absent) if none of the concepts are present at all.
    """
    sums: dict[str, float] = {}
    periods_by_ctx: dict[str, Any] = {}
    concepts_used: list[str] = []
    for concept in concepts:
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
        "source_label": source_label,
        "concept": None,
        "accounting_standard": "tifrs",
        "unit": "TWD",
        "periods": [periods_by_ctx.get(c) for c in ordered_ctx],
        "derivation": "sum of " + " + ".join(concepts_used),
        "components": concepts_used,
    }
    return values, meta


def _build_financial_canonical(
    facts: list[dict[str, Any]],
    *,
    concept_map: dict[str, dict[str, str]],
    labels: dict[str, str],
    borrowing_concepts: tuple[str, ...],
    taxonomy: str,
) -> dict[str, Any]:
    """Shared canonical-builder shape for every financial-family taxonomy
    (-fh, -basi, -bd, ...): same by_concept indexing, same _meta
    construction, same cash_flow.setdefault + deposits/borrowings
    _sum_concepts calls — the three per-family builders below differ only
    in their concept map, labels, and borrowing-concept tuple (Rule-of-
    Three extraction, T6 code-quality review). Deposits always sum the
    fixed _DEPOSIT_CONCEPTS pair; a family with no deposit-taking concepts
    at all (e.g. -bd, brokers take no deposits) degrades gracefully to an
    absent "deposits" key via _sum_concepts' existing missing-concept
    tolerance — no per-family deposits toggle needed.

    Emits sector_class="financial" and taxonomy=<taxonomy> at the top
    level. cash_flow has no measured concepts for any financial family yet,
    so it is emitted empty (consistent envelope shape, no fabricated
    lines). Callers deliberately OMIT the -ci DCF-trigger fields (revenue/
    ebit/fcf/capex/total_debt) from concept_map — a financial filer's
    balance sheet has no such lines, and DCF (analysis-dcf/scripts/
    dcf_compute.py) must fail loud on their absence rather than silently
    compute against a fabricated zero.
    """
    by_concept = _index_by_concept(facts)

    canonical: dict[str, Any] = {"sector_class": "financial", "taxonomy": taxonomy}
    for statement, mapping in concept_map.items():
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
                "source_label": labels.get(canonical_name, canonical_name),
                "concept": concept,
                "accounting_standard": "tifrs",
                "unit": "TWD",
                "periods": [f.get("period") for f in ordered],
            }
        lines["_meta"] = meta
        canonical[statement] = lines

    canonical.setdefault("cash_flow", {"_meta": {}})

    balance_sheet = canonical["balance_sheet"]
    deposits_result = _sum_concepts(
        by_concept, _DEPOSIT_CONCEPTS, "Deposits (sum of components present)"
    )
    if deposits_result:
        values, meta = deposits_result
        balance_sheet["deposits"] = values
        balance_sheet["_meta"]["deposits"] = meta

    borrowings_result = _sum_concepts(
        by_concept, borrowing_concepts, "Borrowings (sum of components present)"
    )
    if borrowings_result:
        values, meta = borrowings_result
        balance_sheet["borrowings"] = values
        balance_sheet["_meta"]["borrowings"] = meta

    return canonical


def _build_fh_canonical(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Map a financial-holding (-fh) fact set into the canonical shape via
    the shared _build_financial_canonical helper.

    Mirrors the -ci canonical envelope (income_statement / balance_sheet /
    cash_flow, each a value-list + per-line _meta) where concepts align,
    plus financial-specific fields (deposits/borrowings kept distinct;
    net_interest_income). Emits sector_class="financial" and taxonomy="fh"
    at the top level. cash_flow has no measured -fh concepts yet, so it is
    emitted empty (consistent envelope shape, no fabricated lines).

    Deliberately OMITS the -ci DCF-trigger fields (revenue/ebit/fcf/capex/
    total_debt) — an FHC's balance sheet has no such lines, and DCF
    (analysis-dcf/scripts/dcf_compute.py) must fail loud on their absence
    rather than silently compute against a fabricated zero.
    """
    return _build_financial_canonical(
        facts,
        concept_map=_FH_CONCEPT_MAP,
        labels=_FH_LABELS,
        borrowing_concepts=_BORROWING_CONCEPTS,
        taxonomy="fh",
    )


# -basi (standalone commercial bank / bills-finance) concept map. The
# balance-sheet spine (Assets/Equity/Cash) and net_income/eps_basic concepts
# are IDENTICAL to -fh (measured: same concept names, same values, verbatim
# across both taxonomies — scratchpad/fh-measurement-round2.md §2801). No
# -basi analog of tifrs-bsci-fh:NetInterestIncomeExpense is carried by any
# measured -basi filer, so income_statement stays limited to net_income/
# eps_basic (unlike -fh, which also has net_interest_income).
_BASI_CONCEPT_MAP: dict[str, dict[str, str]] = {
    "balance_sheet": {
        "total_assets": "ifrs-full:Assets",
        "total_equity": "ifrs-full:Equity",
        "cash": "ifrs-full:CashAndCashEquivalents",
    },
    "income_statement": {
        "net_income": "ifrs-full:ProfitLossAttributableToOwnersOfParent",
        "eps_basic": "ifrs-full:BasicEarningsLossPerShare",
    },
}

_BASI_LABELS: dict[str, str] = {
    "total_assets": "Assets",
    "total_equity": "Equity",
    "cash": "Cash and Cash Equivalents",
    "net_income": "Profit (Loss) Attributable to Owners of Parent",
    "eps_basic": "Basic Earnings (Loss) per Share",
}

# -basi's debt-financing concepts are either renamed under tifrs-bsci-basi:*
# or genuinely absent, never the -fh names (round2: "the entire debt-
# financing side is either absent or renamed under tifrs-bsci-basi:*").
# NotesAndBondsIssuedUnderRepurchaseAgreement is -basi's renamed analog of
# -fh's tifrs-bsci-fh:SecuritiesSoldUnderRepurchaseAgreements (confirmed
# present for both standalone banks (2801) and the bills-finance sub-shape
# (2820), where it is the dominant funding line); CommercialPapersPayable is
# -basi's un-netted analog of tifrs-bsci-fh:CommercialPapersIssuedNet
# (round2: observed on 2809 only, not in the committed fixtures, but named
# here as the correct concept per the measurement doc rather than omitted).
_BASI_BORROWING_CONCEPTS: tuple[str, ...] = (
    "tifrs-bsci-basi:NotesAndBondsIssuedUnderRepurchaseAgreement",
    "tifrs-bsci-basi:CommercialPapersPayable",
)


def _build_basi_canonical(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Map a standalone-commercial-bank OR bills-finance (-basi) fact set
    into the canonical shape (Task 6) via the shared
    _build_financial_canonical helper.

    Mirrors _build_fh_canonical's envelope exactly: income_statement /
    balance_sheet / cash_flow (each a value-list + per-line _meta), plus
    deposits/borrowings kept distinct on the balance sheet. Emits
    sector_class="financial" and taxonomy="basi" at the top level.

    Deposits reuse the SAME concept pair as -fh (_DEPOSIT_CONCEPTS:
    DepositsFromCustomers + DepositsFromBanks) — measured verbatim-identical
    across both taxonomies (round2 §2801). Borrowings use -basi's own
    renamed concept set (_BASI_BORROWING_CONCEPTS), never -fh's, since the
    bond/CP/repo concepts are renamed under tifrs-bsci-basi:* for this
    family. _sum_concepts already tolerates whichever subset of either
    tuple is present, so a bills-finance filer with no customer deposits at
    all (round4 §2820: only DepositsFromBanks present, DepositsFromCustomers
    genuinely absent) degrades to a partial sum rather than crashing or
    fabricating a component.

    Deliberately OMITS the -ci DCF-trigger fields (revenue/ebit/fcf/capex/
    total_debt), same rationale as -fh: a bank/bills-finance balance sheet
    has no such lines, and DCF must fail loud on their absence rather than
    silently compute against a fabricated zero.
    """
    return _build_financial_canonical(
        facts,
        concept_map=_BASI_CONCEPT_MAP,
        labels=_BASI_LABELS,
        borrowing_concepts=_BASI_BORROWING_CONCEPTS,
        taxonomy="basi",
    )


# -bd (broker-dealer / securities) concept map (Task 7). Balance-sheet
# spine (Assets/Equity/Cash) is the SAME concept names as -fh/-basi
# (measured stable across 19 financial-sector filers spanning 5 taxonomy
# families — scratchpad/fh-measurement-round3.md). Brokers take no
# customer/interbank deposits (confirmed absent for 6005: neither
# ifrs-full:DepositsFromCustomers nor ifrs-full:DepositsFromBanks appear in
# the fixture at all) and carry no NPL/coverage concepts (not a lending
# institution) — deposits degrades to absent via _sum_concepts' existing
# missing-concept tolerance, no special-casing needed. income_statement
# adds brokerage_fee_income (ifrs-full:BrokerageFeeIncome, the dominant
# -bd-specific revenue line — scratchpad/fh-measurement.md §6005) alongside
# the same net_income/eps_basic concepts -fh/-basi use.
_BD_CONCEPT_MAP: dict[str, dict[str, str]] = {
    "balance_sheet": {
        "total_assets": "ifrs-full:Assets",
        "total_equity": "ifrs-full:Equity",
        "cash": "ifrs-full:CashAndCashEquivalents",
    },
    "income_statement": {
        "brokerage_fee_income": "ifrs-full:BrokerageFeeIncome",
        "net_income": "ifrs-full:ProfitLossAttributableToOwnersOfParent",
        "eps_basic": "ifrs-full:BasicEarningsLossPerShare",
    },
}

_BD_LABELS: dict[str, str] = {
    "total_assets": "Assets",
    "total_equity": "Equity",
    "cash": "Cash and Cash Equivalents",
    "brokerage_fee_income": "Brokerage Fee Income",
    "net_income": "Profit (Loss) Attributable to Owners of Parent",
    "eps_basic": "Basic Earnings (Loss) per Share",
}


def _build_bd_canonical(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Map a broker-dealer/securities (-bd) fact set into the canonical
    shape (Task 7) via the shared _build_financial_canonical helper.

    No -bd-specific borrowing concept set is measured/registered yet (the
    scope for this task is the balance-sheet spine + brokerage income +
    net_income/eps_basic only) — an empty borrowing_concepts tuple means
    "borrowings" simply never appears (no concepts to sum), same
    graceful-absence behavior as a missing component within a non-empty
    tuple. Deliberately OMITS the -ci DCF-trigger fields (revenue/ebit/
    fcf/capex/total_debt), same rationale as -fh/-basi: a broker's balance
    sheet has no such lines, and DCF must fail loud on their absence rather
    than silently compute against a fabricated zero.
    """
    return _build_financial_canonical(
        facts,
        concept_map=_BD_CONCEPT_MAP,
        labels=_BD_LABELS,
        borrowing_concepts=(),
        taxonomy="bd",
    )


# Builder registry: taxonomy tag -> canonical builder callable. "ci", "fh",
# "basi" and now "bd" (Task 7) have builders; the remaining financial
# family ("ins") lands in a later task and registers its builder here. A
# tag with no registered builder falls through to the unsupported marker
# (_unsupported_financial).
_CANONICAL_BUILDERS: dict[str, Any] = {
    "ci": _build_ci_canonical,
    "fh": _build_fh_canonical,
    "basi": _build_basi_canonical,
    "bd": _build_bd_canonical,
}


def build_canonical(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Map parsed iXBRL facts into the canonical three-statement shape by
    routing on the fact set's taxonomy family (classify_taxonomy).

    Industrial (-ci) filers map through _build_ci_canonical; financial-
    holding (-fh) filers map through _build_fh_canonical; standalone-bank/
    bills-finance (-basi) filers map through _build_basi_canonical;
    broker-dealer (-bd) filers map through _build_bd_canonical. The
    remaining financial family (-ins) has no builder registered yet, so it
    returns an explicit unsupported marker instead of a wrong/empty
    mapping — its builder is a deferred sub-arc (see docs/loom/plans/
    2026-07-19-tw-ixbrl-ingestion.md Decision Log).
    """
    tag = classify_taxonomy(facts)
    builder = _CANONICAL_BUILDERS.get(tag)
    if builder is None:
        return _unsupported_financial(tag)
    return builder(facts)
