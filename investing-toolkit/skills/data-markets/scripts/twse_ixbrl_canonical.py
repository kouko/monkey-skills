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
        "pretax_income": "ifrs-full:ProfitLossBeforeTax",
        "net_income": "ifrs-full:ProfitLossAttributableToOwnersOfParent",
        "eps_basic": "ifrs-full:BasicEarningsLossPerShare",
    },
    "balance_sheet": {
        "total_assets": "ifrs-full:Assets",
        "total_liabilities": "ifrs-full:Liabilities",
        "total_equity": "ifrs-full:Equity",
    },
    "cash_flow": {
        "operating_cash_flow": "ifrs-full:CashFlowsFromUsedInOperatingActivities",
        "investing_cash_flow": "tifrs-SCF:NetCashFlowsFromUsedInInvestingActivities",
        "financing_cash_flow": "tifrs-SCF:CashFlowsFromUsedInFinancingActivities",
    },
}

_LABELS: dict[str, str] = {
    "revenue": "Revenue",
    "gross_profit": "Gross Profit",
    "operating_income": "Profit (Loss) from Operating Activities",
    "pretax_income": "Profit (Loss) before Tax",
    "net_income": "Profit (Loss) Attributable to Owners of Parent",
    "eps_basic": "Basic Earnings (Loss) per Share",
    "total_assets": "Assets",
    "total_liabilities": "Liabilities",
    "total_equity": "Equity",
    "operating_cash_flow": "Cash Flows from (used in) Operating Activities",
    "investing_cash_flow": "Net Cash Flows from (used in) Investing Activities",
    "financing_cash_flow": "Cash Flows from (used in) Financing Activities",
}


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

    return canonical
