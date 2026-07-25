#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""kpi_spine_view.py -- Pure read-time view: as-reported concept series ->
canonical spine fields.

Reads a `kpi_store.py dump --company <C>` payload (PINNED schema -- SSOT
docs/loom/plans/2026-07-23-kpi-tearsheet.md ## Notes) and emits a payload of
the SAME pinned schema whose `series` are the 14 canonical spine fields
(`revenue`, `net_income`, ...) instead of the filer's raw us-gaap concept
ids. So the render pipeline composes as a plain pipe --
`kpi_store dump | kpi_spine_view derive | tearsheet_format` -- and
tearsheet_format.py is not touched.

PURE FUNCTION -- no HTTP, no subprocess, no store access, no env access
beyond argparse/stdin (tearsheet_format.py precedent). It imports no
data-markets module and no store module: its whole input is the dump payload
it is handed.

THE RESOLUTION RULE (the reason this module exists). For each spine field
and each PERIOD, pick the first concept in that field's ordered chain that
has an observation FOR THAT PERIOD. Resolution is per PERIOD, never per
company. That is precisely what the store deliberately does NOT do at write
time: it stores what the filer actually tagged, so a filer who switched tags
mid-history (measured: 24 of 46 filers) yields ONE continuous field series
spanning both eras. A per-company winner -- "first concept that returns ANY
rows" -- keeps only the pre-switch years and silently truncates the history.

Chain ORDER is the same-period tiebreak only. It decides which concept
represents the field in a period where two chain members both reported; it
never elects a winner for the whole company, and the losing concept still
supplies every period the winner does not cover.

HONEST ABSENCE. A field with no chain concept present in a period yields NO
entry for that period, and a field with no chain concept present anywhere
yields no `series` row at all -- never 0, never a derived guess, never a
fabricated placeholder. Measured on the 46-filer probe: 22 filers report no
gross profit at all and 13 never tag a total `Liabilities`. A hole is the
truth about the filing, not a defect in the view.

Period identity across concepts is the store-owned `period_axis_key` --
the same cross-KPI column-alignment identity tearsheet_format joins its
columns on -- never the raw `(period_start, period_end)` pair, which drifts
apart between two filings of one real period. A `null` axis key means "not
proven to be the same period", NOT "no period", so a null-key entry is
resolved against nothing and every one of them survives into the output
(again the store's own doctrine, and what the formatter already renders: one
column each).

`company` and `warnings` ride through verbatim -- a corrupt-file note the
store emitted must still reach the reader after the view.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# The store holds the filer's own qname verbatim, namespace preserved
# (`us-gaap:Revenues`), so the chains below -- transcribed as bare local
# names from the plan's pin -- are qualified with this namespace on lookup.
# Keeping the pin's transcription bare is deliberate: it stays diffable
# against the plan character-for-character.
_US_GAAP = "us-gaap:"

# PINNED spine field chains -- transcribed VERBATIM from
# docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md ## Notes
# ("PIN -- spine field chains"). Ordered first-present chains; order is the
# same-period tiebreak, never a per-company winner.
#
# A tuple of pairs, not a dict literal, because the DECLARED order is the
# statement's reading order (income statement -> balance sheet -> cash flow)
# and it is the order the emitted `series` carries. That is a deliberate
# departure from the store dump's kpi_id sort: alphabetizing the spine would
# scatter the statements ("capex, cash, eps_basic, ...") for no reader gain,
# and tearsheet_format renders `series` in the order it is handed.
SPINE_FIELD_CHAINS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("revenue", (
        "Revenues",
        "RevenuesNetOfInterestExpense",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueNet",
    )),
    ("gross_profit", (
        "GrossProfit",
    )),
    ("operating_income", (
        "OperatingIncomeLoss",
    )),
    ("pretax_income", (
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic",
    )),
    ("net_income", (
        "NetIncomeLoss",
        "ProfitLoss",
    )),
    ("eps_basic", (
        "EarningsPerShareBasic",
        "IncomeLossFromContinuingOperationsPerBasicShare",
    )),
    ("total_assets", (
        "Assets",
    )),
    ("total_liabilities", (
        "Liabilities",
    )),
    ("total_equity", (
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    )),
    ("cash", (
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        "Cash",
    )),
    ("operating_cash_flow", (
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    )),
    ("investing_cash_flow", (
        "NetCashProvidedByUsedInInvestingActivities",
        "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
    )),
    ("financing_cash_flow", (
        "NetCashProvidedByUsedInFinancingActivities",
        "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
    )),
    ("capex", (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
        "PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets",
    )),
)


def _period_identity(period: dict[str, Any]) -> Any:
    """Cross-concept period identity: the store's `period_axis_key` when it
    has one, else this entry's OWN object identity.

    Byte-identical in spirit to `tearsheet_format._column_group_key`, and for
    the same reason: a `null` axis key is the store saying "I could not size
    this span, so I have NOT proven it is the same period as anything else".
    Two null keys must therefore never resolve against each other -- falling
    back to `id(period)` makes each one its own unresolvable period, so both
    filer-reported figures survive instead of one silently winning.
    """
    axis_key = period.get("period_axis_key")
    return axis_key if axis_key is not None else id(period)


def _resolve_field(chain_periods: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """First-present-per-period resolution over ONE field's chain.

    `chain_periods` is the chain's period lists in CHAIN ORDER (concepts
    absent from the dump already dropped). Walking them in that order and
    keeping the first entry seen per period identity IS the rule: an earlier
    concept wins a period it covers, and a later concept still contributes
    every period no earlier one covered.

    Entries are SHALLOW-copied: top-level annotation is safe (a later
    annotator -- the Task 7 balance-identity flag -- may add or overwrite
    top-level keys without touching the caller's dump), but the nested
    `latest` / `observations` / `period_labels` objects are STILL SHARED with
    the caller's payload. Annotate at the top level only; mutating a nested
    object (e.g. `period["latest"][k] = v`) writes back into the store's
    payload silently.

    Sorted ascending by `period_end` (the primary key of the store's own
    `_period_sort_key`), matching the pinned payload's ascending period
    order; a missing end sorts first rather than raising. The store's `qtrs`
    tiebreak is deliberately not reimplemented here -- it would be a second
    copy of store-private logic (a drift surface) for a purely cosmetic
    within-tie order. Note the formatter does not fully re-derive order for
    ties: its `sorted(..., reverse=True)` is stable, so among equal
    `max_end` values this view's order does leak into the rendered column
    order. Cosmetic, but real.
    """
    resolved: dict[Any, dict[str, Any]] = {}
    for periods in chain_periods:
        for period in periods:
            identity = _period_identity(period)
            if identity not in resolved:
                resolved[identity] = dict(period)
    return sorted(resolved.values(), key=lambda p: p.get("period_end") or "")


def derive_spine(dump: dict[str, Any]) -> dict[str, Any]:
    """Map a `kpi_store dump --company` payload onto the spine fields,
    resolving each field's concept chain PER PERIOD (see module docstring).

    Returns the same pinned schema -- `{"company", "series", "warnings"}` --
    so the shipped formatter consumes it unchanged. `series` carries one
    entry per spine field that any chain concept covers, in
    `SPINE_FIELD_CHAINS` order; a field no concept covers is absent entirely.
    Stored series that are not a spine concept are simply not part of the
    spine view (they remain in the store, and in the raw dump).
    """
    periods_by_concept = {
        entry.get("kpi_id"): entry.get("periods") or []
        for entry in dump.get("series", [])
    }

    series: list[dict[str, Any]] = []
    for field, chain in SPINE_FIELD_CHAINS:
        chain_periods = [
            periods_by_concept[f"{_US_GAAP}{concept}"]
            for concept in chain
            if periods_by_concept.get(f"{_US_GAAP}{concept}")
        ]
        if not chain_periods:
            continue  # honest absence: no row at all, never an empty placeholder
        series.append({"kpi_id": field, "periods": _resolve_field(chain_periods)})

    return {
        "company": dump.get("company", ""),
        "series": series,
        "warnings": list(dump.get("warnings", [])),
    }


def _cli_derive(args: argparse.Namespace) -> int:
    """`derive` subcommand: read the dump payload from `--dump` (or stdin
    when omitted), print the spine payload as JSON to stdout.
    """
    if args.dump_path:
        try:
            with open(args.dump_path, "r", encoding="utf-8") as f:
                dump = json.load(f)
        except OSError as exc:
            print(f"error: cannot read {args.dump_path}: {exc}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as exc:
            print(f"error: invalid JSON in {args.dump_path}: {exc}", file=sys.stderr)
            return 1
    else:
        try:
            sys.stdin.reconfigure(encoding="utf-8")
            dump = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            print(f"error: invalid JSON on stdin: {exc}", file=sys.stderr)
            return 1

    if not isinstance(dump, dict):
        print(
            "error: top-level dump JSON must be an object, got "
            f"{type(dump).__name__}",
            file=sys.stderr,
        )
        return 1

    sys.stdout.reconfigure(encoding="utf-8")
    json.dump(derive_spine(dump), sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Derive the canonical spine fields from a kpi_store.py `dump "
            "--company` payload, resolving each field's concept chain per "
            "period. Pure view -- no I/O beyond input + stdout."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    derive_parser = subparsers.add_parser(
        "derive",
        help="Emit the spine-shaped payload for one dump (same pinned schema).",
    )
    derive_parser.add_argument(
        "--dump",
        dest="dump_path",
        default=None,
        help="Path to the kpi_store.py `dump --company` JSON payload. Omit to read stdin.",
    )
    derive_parser.set_defaults(func=_cli_derive)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
