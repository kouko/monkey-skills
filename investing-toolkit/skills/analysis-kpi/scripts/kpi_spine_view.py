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
beyond argparse/stdin (tearsheet_format.py precedent): its whole input is the
payload it is handed. It imports no data-markets module, and its THREE sibling
imports are `kpi_xbrl`, for `assert_dqc_schema`; `kpi_equity_terms`, for the
whole-equity primitives the balance-sheet identity branches on; and
`kpi_us_statement_cells`, for the four-state cell taxonomy the as-filed view
reports (both added by plan Task 7).

ONLY THE FIRST OF THE THREE CHANGES THE SCOPE OF THAT CLAIM, which is why the
count is stated with what each one costs rather than as a number. Verified by
walking their top-level statements, not by reading their docstrings:
`kpi_equity_terms` is stdlib-only and imports nothing sibling;
`kpi_us_statement_cells` imports exactly one sibling, `kpi_equity_terms`; and
neither does I/O at import time. So the store reach described below is still
`kpi_xbrl`'s alone, and the two additions do not widen it.

That import is NOT store-free transitively, and the accurate statement is the
one worth having here, because a "imports no store module" line tells the
next reader not to look -- which is exactly how store I/O enters a pure view
unnoticed. The real chain: `kpi_xbrl` imports `kpi_series` (`kpi_xbrl.py:145`)
-> `kpi_break` (`kpi_series.py:54`) -> `_store_fs` AND `review_queue`
(`kpi_break.py:64-65`). So this module's import graph does reach the store's
filesystem module.

Runtime purity nonetheless holds today, for a reason that is CHECKABLE rather
than asserted, and both halves must be re-verified before a further sibling
import is added (they were re-verified for Task 7's two):
  1. NOTHING in those four modules does I/O at import time. Module level is
     constants, `Path(__file__).resolve()` sys.path shims, one `re.compile`
     and one `try: import fcntl` fallback -- verified by walking each
     module's top-level statements, not by reading its docstring.
  2. The only thing this module ever CALLS across that boundary is
     `kpi_xbrl.assert_dqc_schema`, a pure dict check that touches no path.

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

BALANCE-SHEET IDENTITY. Per period the view also checks
`total_assets - (total_liabilities + mezzanine + WHOLE equity)` and attaches
a flag when the residual exceeds `BALANCE_IDENTITY_TOLERANCE` RELATIVE to
total assets. The check exists because per-period concept selection is the
thing most likely to go wrong here, and the identity is the only oracle
`companyfacts` alone can supply. It NEVER suppresses, refuses, or alters a
value: an as-reported figure is not wrong because our field selection was.

  - WHY THE MEZZANINE TERM IS REQUIRED, NOT OPTIONAL. Measured over the
    47-filer probe: with it, 30 of 32 checkable filers balance EXACTLY
    (residual 0), and TSLA's entire residual was exactly its redeemable
    non-controlling interest, to the dollar. Drop the term and that filer
    reads as "does not balance" -- a false accusation. Read that 30/32
    carefully, though: it was produced by the PROBE's identity
    (`tests/data/fixtures/capture_us_statement_shapes_probe.py`,
    `_balance_identity`), which is FOUR-term and prefers the incl-NCI equity
    concept. It is evidence for the mezzanine term and for the conditional
    equity term below -- NOT for a flat three-term form.
  - WHERE THE MEZZANINE COMES FROM. Its concepts are deliberately NOT
    members of `SPINE_FIELD_CHAINS` (the plan's pin lists them separately,
    at the end of the same block, because they are identity-only and never
    become a `series` row), so `derive_spine`'s OUTPUT cannot supply them.
    They are read from the RAW dump instead -- specifically from the
    `periods_by_concept` index `derive_spine` already builds, which holds
    every concept the dump carries, spine or not. That is why the check is
    an internal step of `derive_spine` and not a second entry point or an
    extra return channel: the raw periods are already in scope there, and
    keeping it internal is what lets the pipeline stay one plain pipe
    (`kpi_store dump | kpi_spine_view derive | tearsheet_format`).
    `MinorityInterest`, the pin's third identity-only concept, reaches the
    check by that same route.
  - THE EQUITY TERM IS WHOLE EQUITY, AND WHICH CONCEPT SUPPLIES IT IS A
    PER-PERIOD FACT. The identity needs equity INCLUDING the non-controlling
    interest, but the `total_equity` chain puts parent-only
    `StockholdersEquity` FIRST, so what a period resolved to decides the
    term:
      * resolved `StockholdersEquityIncludingPortionAttributableTo
        NoncontrollingInterest` -> already whole; adding `MinorityInterest`
        would DOUBLE-COUNT it.
      * resolved plain `StockholdersEquity` -> parent-only;
        `MinorityInterest` MUST be added for that period, or the residual IS
        the non-controlling interest and the filer is falsely accused.
    The parent-only branch is the MAJORITY case, not an edge case: cross-
    tabbing the committed probe fixture, 17 of 32 checkable filers used the
    incl-NCI concept in the probe while this chain resolves parent-only (BA,
    C, COST, CVX, F, GE, GM, IBM, JNJ, MS, PEP, PFE, PSX, QCOM, TSLA, UNH,
    WFC), and the interest is material for GE, F, GM, UNH, C and MS. The fix
    is the IDENTITY, not the chain: what the spine's `total_equity` field
    should MEAN is a separate product question, and reordering the chain
    here would silently change the figure those 17 filers report.
  - ONE VINTAGE, NEVER ACROSS. The store is BITEMPORAL: a restatement APPENDS
    a new vintage of a period instead of overwriting the old one, and
    different components of one period routinely end up with different numbers
    of vintages. So every amount in the identity is read from ONE filing --
    `_identity_vintage` picks the newest `(as_of, source_accession)` that ALL
    THREE totals share, and `_vintage_observation` reads each component there.
    Reading each component's own `latest` instead is not an accounting
    identity at all, and the live six-filer dogfood measured what that costs:
    four filers flagged (MSFT 2016-06-30 5.73e-02, AAPL 2008-09-27 1.29e-01,
    JPM 2019-12-31 3.36e-04, TSLA 2014-12-31 9.98e-03) and every one was the
    same shape -- MSFT's 2017 filing balances to the dollar
    (193,468 = 121,471 + 71,997) and the residual came entirely from pairing
    it with a 2018-filed equity figure. A check whose job is to catch a wrong
    number was reporting the store working correctly.
      * NEWEST, because that is what a reader sees as the period's current
        figures; a superseded filing's residual is not news, and scanning
        older vintages until one balances would be tuning toward silence.
      * The FLAG names that vintage (`checked_vintage`, and `accessions` is
        now exactly one). It has to: the flag's `components` are that filing's
        figures, which for a restated component is NOT the `latest` the view
        emits for the same period. The two are reconcilable only because the
        flag says which filing it read.
      * A revision BETWEEN vintages is a different claim, and this flag is not
        it -- the store's own `disagreement` and the tearsheet's Revisions
        section carry that. Conflating the two is what produced the defect.
  - UNCHECKABLE IS NOT WRONG. A period missing ANY required component is not
    flagged -- 13 of 46 filers never tag a total `Liabilities` at all, and
    silence there is correct. Since the fix above, a period NO SINGLE FILING
    covers is uncheckable for the same reason. The mezzanine and (on the
    parent-only branch) `MinorityInterest` are the components that read as 0
    when absent; see `_annotate_balance_identity` for why that asymmetry is
    measured rather than assumed, for the ONE case where an absent
    `MinorityInterest` makes the period uncheckable instead, and for why
    "absent" has to mean absent from the PERIOD, not from the checked filing.
  - THE FLAG'S CARRIER is the `total_assets` period entry: the identity's
    subject and its denominator, hence always present whenever the period is
    checkable, and one flag per period rather than three copies of it. The
    flag rides in the ONE DQC schema the repo uses
    (`kpi_xbrl.assert_dqc_schema`), which is self-enforcing at its emission
    site. It is written at the TOP LEVEL of the view's own shallow copy --
    see `_resolve_field` for why nothing nested may ever be touched.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Resolve same-dir modules without a package (mirrors kpi_memo_feed.py's /
# kpi_store.py's own import shim), so `import kpi_xbrl` works both under
# `uv run --script` and under importlib test loading.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
# `assert_dqc_schema` is the ONE thing called across this boundary; the import
# graph behind it does reach `_store_fs` (module docstring, "PURE FUNCTION").
import kpi_xbrl  # noqa: E402

# THE WHOLE-EQUITY PRIMITIVES LIVE IN A LEAF MODULE, not here, so that
# `kpi_us_statement_cells` can read them without importing this module -- which
# is what makes the Task 7 direction (this view consuming the reconstruction) an
# acyclic import instead of an order-dependent failure. See
# `kpi_equity_terms`'s own header for the mutation that reproduced the cycle.
# Re-bound under their historical names so every existing reference to
# `kpi_spine_view._equity_kind` (and its seven siblings) still resolves: the
# plan's Decision Log requires all eight bindings to survive by name AND by
# semantics.
from kpi_equity_terms import (  # noqa: E402
    _US_GAAP,
    _equity_kind,
    _identity_value,
    _minority_interest_term,
    EQUITY_CHAIN,
    EQUITY_INCL_NCI_CONCEPT,
    EQUITY_PARENT_ONLY_CONCEPT,
    MEZZANINE_CHAIN,
    MINORITY_INTEREST_CHAIN,
)

# PINNED spine field chains -- transcribed VERBATIM from
# docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md ## Notes
# ("PIN -- spine field chains"). Ordered first-present chains; order is the
# same-period tiebreak, never a per-company winner.
#
# WHAT THIS CONSTANT IS STILL FOR, now that the as-filed reconstruction ships
# (plan Task 11's disposition; brief
# docs/loom/specs/2026-07-26-as-filed-statement-reconstruction.md
# §What Becomes Obsolete, which requires this list to be either DELETED or its
# remaining role written down here, never left as dead-but-live config). It is
# KEPT, and it is no longer the whole resolution rule:
#   - It declares the 14 FIELD NAMES and their emission order for BOTH entry
#     points -- `derive_spine`, over a store dump, and `derive_spine_as_filed`,
#     over a Task 9 reconstruction payload.
#   - It is still the CONCEPT resolution rule for 13 of those 14 fields, on
#     both entry points. `derive_spine` resolves the chain against what the
#     filer TAGGED in the store; `_chain_concept` resolves the same chain, in
#     the same first-present order, against the lines the filer PRESENTED on
#     the statement. Same concepts, one input each.
#   - `revenue` is the ONE field this list no longer resolves on the as-filed
#     path. `_revenue_total` binds it from the filing's own calculation tree
#     instead -- a revenue line whose calculation parent is also a revenue line
#     is a component, and the one that remains is the filing's total (63 of 65
#     operating filings in the committed verification universe, zero violations
#     against sum reconciliation). It left for a measured reason: revenue is
#     the field whose blanks the brief measured as ALL recoverable, because
#     whole sectors declare a total no chain here lists (KO's
#     `SalesRevenueGoodsNet`, DUK's `RegulatedAndUnregulatedOperatingRevenue`,
#     PLD's `RealEstateRevenueNet`, PSX's `RevenuesAndOtherIncome`).
#   - The other 13 deliberately did NOT follow it, and this is the honest limit
#     of the evidence rather than a half-finished migration. For those fields
#     the chain concept IS the filer's own concept everywhere it was measured,
#     and the two filings this repo holds rows for offline (KO FY2017, IBM
#     FY2025) cannot discriminate a structural rule for them -- inventing one
#     would be unpinned work on the money path. When that evidence arrives the
#     rule goes beside `_revenue_total` and this list serves fewer fields;
#     `test_spine_field_chains_has_a_stated_disposition` measures the split and
#     fails when this paragraph stops matching the code.
#   - SUPERSEDED, and no longer the plan: the BACKLOG entry "spine chain misses
#     33 filer-years" proposed widening these chains with early-era synonyms.
#     The brief above replaces that fix with the reconstruction and the entry
#     is closed against it -- widening `revenue` here to chase early-era
#     coverage would write a hand-picked synonym into an append-only store,
#     which is the risk that entry declined to take.
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

def _assert_equity_chain(chain: tuple[str, ...]) -> None:
    """Fail LOUD when the `total_equity` chain no longer IS the exact pair of
    concepts the balance-sheet identity branches on. Called at import below.

    TUPLE EQUALITY, deliberately -- both order-sensitive and length-sensitive,
    and both halves are load-bearing. Reordering flips which concept the
    majority of periods resolve to (the very defect this guard exists to stop
    recurring), and an EXTRA member is a concept `_equity_kind` cannot name,
    so every period carrying it falls through to "uncheckable" -- a check that
    quietly stops checking. A set or subset comparison would keep the shipped
    chain passing while admitting both; `test_the_equity_chain_drift_guard_
    trips_on_reorder_and_on_extension` pins the two properties separately so
    that loosening breaks a test rather than a filer's flag.

    A function, not a bare module-level `if`, so the raise branch itself is
    reachable from a test: the import-time comparison alone can only be
    exercised by mutating a copy of this file, which leaves no committed
    evidence behind.

    IT NOW GUARDS A CROSS-MODULE PAIR. `EQUITY_CHAIN` lives in
    `kpi_equity_terms`, which `kpi_us_statement_cells` reads directly, so this
    is the one place the SPINE's transcription of the chain and the pair the
    identity branches on are compared. The guard therefore runs whenever this
    module loads -- previously also whenever the cells module loaded, since it
    imported this one. Nothing is left unguarded by that narrowing: the cells
    module no longer transcribes the pair at all, it reads it, so the only
    remaining way for the two to disagree is an edit to `SPINE_FIELD_CHAINS`
    here, which is exactly what this call catches.
    """
    if chain != EQUITY_CHAIN:
        raise RuntimeError(
            "kpi_spine_view: the total_equity chain "
            f"{chain} no longer matches the two concepts the "
            f"balance-sheet identity branches on ({EQUITY_CHAIN}) -- "
            "decide what whole equity means for the new member before shipping"
        )


_assert_equity_chain(dict(SPINE_FIELD_CHAINS)["total_equity"])

# Kickoff decision, brief §Resolved at kickoff #2: the reconciliation
# tolerance is RELATIVE, 1e-5 -- a decision, not a guess. `companyfacts`
# carries NO `decimals` attribute on any component (verified on three
# filers), so an absolute or precision-derived tolerance is not
# constructible. 1e-5 clears the two measured non-exact filers (IBM and
# Procter & Gamble each miss by exactly 1,000,000 against figures reported
# in millions -- 7.99e-06 relative) with about an order of magnitude of
# headroom, and still catches a residual an order of magnitude smaller than
# a real component swap.
BALANCE_IDENTITY_TOLERANCE = 1e-5

# This flag class's `type` within the ONE DQC flag schema
# (`kpi_xbrl.assert_dqc_schema`; the plan's kickoff decision pins "no
# per-class schema variants").
BALANCE_IDENTITY_FLAG_TYPE = "balance_identity_residual"


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


def _chain_periods(
    periods_by_concept: dict[Any, list[dict[str, Any]]],
    chain: tuple[str, ...],
) -> list[list[dict[str, Any]]]:
    """One chain's period lists in CHAIN ORDER, with concepts absent from
    the dump dropped -- exactly the input `_resolve_field` expects. Shared
    by the spine fields and the identity-only mezzanine chain so the two
    resolve by one rule, not two."""
    return [
        periods_by_concept[f"{_US_GAAP}{concept}"]
        for concept in chain
        if periods_by_concept.get(f"{_US_GAAP}{concept}")
    ]


def _by_axis_key(periods: list[dict[str, Any]]) -> dict[Any, dict[str, Any]]:
    """Index resolved period entries by the store's `period_axis_key`,
    DROPPING null-key entries.

    The identity is a cross-CONCEPT claim, so it may only join on the
    store-owned cross-KPI identity -- never on raw dates. A null key means
    "not proven to be the same period as anything else", so a null-key
    period can never be matched to the other components and is therefore
    uncheckable, which is the honest outcome rather than a guess.
    """
    return {
        period["period_axis_key"]: period
        for period in periods
        if period.get("period_axis_key") is not None
    }


def _vintage_key(observation: dict[str, Any]) -> tuple[str, str]:
    """ONE filing's identity on the store's vintage axis:
    `(as_of, source_accession)`.

    BOTH halves, not the accession alone. `as_of` is what ORDERS vintages --
    it is the store's own axis (`observations` are as_of-ascending, `latest`
    is max-`as_of`), and comparing accession strings would order by issuer
    prefix, not by time. The accession is what keeps two filings made on one
    day distinct. A filing supplies both to every point it produced, so the
    pair never splits one filing in two.

    A missing half reads as `""` rather than raising: a hand-fed payload with
    no provenance still groups deterministically here, and an accession-less
    FLAGGED period still leaves by the one documented door
    (`_balance_identity_flag`, "THE ONE PLACE THIS MODULE CAN RAISE").
    """
    as_of = observation.get("as_of")
    accession = observation.get("source_accession")
    return (
        as_of if isinstance(as_of, str) else "",
        accession if isinstance(accession, str) else "",
    )


def _observations(period: dict[str, Any] | None) -> list[dict[str, Any]]:
    """One period entry's vintages, as_of-ascending -- `[]` for an absent
    component or a hand-fed entry carrying no `observations` list, so a
    caller never has to distinguish "no component" from "no vintages"."""
    observations = None if period is None else period.get("observations")
    if not isinstance(observations, list):
        return []
    return [o for o in observations if isinstance(o, dict)]


def _vintage_observation(
    period: dict[str, Any] | None,
    vintage: tuple[str, str],
) -> dict[str, Any] | None:
    """That component's observation FROM ONE filing, or None when the filing
    carries none for this period.

    First match wins, scanning as_of-ascending -- the store's own tie rule
    (`_group_period_entries`'s `latest` is a `max()`, which keeps the
    first-encountered on an equal key). Reachable only when one filing tagged
    the same concept for the same real period under two different period
    LABELS, which the store's grouping merges into one entry.
    """
    return next(
        (o for o in _observations(period) if _vintage_key(o) == vintage),
        None,
    )


def _identity_vintage(
    *periods: dict[str, Any] | None,
) -> tuple[str, str] | None:
    """The NEWEST filing that carries EVERY one of these components for the
    period -- the vintage the identity is evaluated in -- or None when no
    single filing carries them all.

    NEWEST because that is what a reader sees as the period's current
    figures; a superseded filing's residual is not news, and checking every
    vintage until one balances would be tuning the check toward silence.
    Chosen from the INTERSECTION, so the components can only ever be compared
    as one filing asserted them together.

    `max()` over `(as_of, accession)` pairs orders by `as_of` first; the
    accession breaks a same-day tie deterministically rather than by
    dict order (which would make the same store yield different flags).

    None is UNCHECKABLE, not wrong -- the same honest silence the check
    already keeps for a period missing a component outright.
    """
    shared: set[tuple[str, str]] | None = None
    for period in periods:
        keys = {_vintage_key(o) for o in _observations(period)}
        shared = keys if shared is None else shared & keys
        if not shared:
            return None
    return max(shared) if shared else None


def _balance_identity_flag(
    *,
    axis_key: Any,
    period_end: Any,
    vintage: tuple[str, str],
    equity_kind: str,
    components: dict[str, int | float],
    residual: int | float,
    relative_residual: float,
) -> dict[str, Any]:
    """Shape ONE flagged period's residual into the repo's single DQC flag
    schema, and validate it at the emission site.

    Every argument is an already-computed value, KEYWORD-ONLY: this function
    knows nothing about period entries, chains, or how a component was
    resolved, so it cannot reintroduce a resolution decision, and seven
    positional numbers are exactly the call site where two get swapped
    silently.

    ONE VINTAGE IN, ONE ACCESSION OUT. `accessions` is derived HERE from the
    checked vintage rather than accepted as a list, so the flag structurally
    cannot list several filings again: every component of the residual came
    from that one filing, and a reader who pulls it can reproduce the
    arithmetic exactly. The vintage is also emitted whole as
    `checked_vintage`, `as_of` included -- the accession says WHICH filing,
    the `as_of` places it on the store's vintage axis, which is what a reader
    needs to see that a NEWER vintage of some component exists and was
    deliberately not mixed in.

    THE ONE PLACE THIS MODULE CAN RAISE. A flagged period whose checked
    vintage carries no `source_accession` produces `[""]`, which
    `assert_dqc_schema` rejects. That is unreachable from the real producer
    (`kpi_store.append`'s provenance guard requires the field on every stored
    point, so every `dump_company` payload has it), and the loud failure is
    deliberate for the hand-fed case: the alternatives are fabricating an
    accession or dropping a real residual on the floor.
    """
    as_of, accession = vintage
    return kpi_xbrl.assert_dqc_schema({
        "type": BALANCE_IDENTITY_FLAG_TYPE,
        # No old/new pair: this class compares one period against an
        # accounting identity, not one vintage against another. The ONE
        # schema admits None for exactly such a class.
        "old": None,
        "new": None,
        "accessions": [accession],
        "reason": (
            f"balance-sheet identity residual {residual} against total "
            f"assets {components['total_assets']} ({relative_residual:.3e} "
            f"relative) exceeds the {BALANCE_IDENTITY_TOLERANCE:.0e} relative "
            f"tolerance for the period ending {period_end!r} as reported in "
            f"{accession or '(no accession)'} (as_of {as_of or 'unknown'}) -- "
            f"every as-reported figure is unchanged; the residual points at "
            f"this view's per-period concept SELECTION, not at the filer's "
            f"numbers"
        ),
        # Locating extras, which the ONE schema allows on top of the
        # required five.
        "period_axis_key": axis_key,
        "period_end": period_end,
        # The ONE filing every component above was read from -- the identity
        # is evaluated within a vintage, never across (module docstring).
        "checked_vintage": {"as_of": as_of, "source_accession": accession},
        # Which concept carried `total_equity` here, so a reader can tell
        # a `minority_interest` of 0 that means "already inside the
        # equity total" (`incl_NCI`) from one that means "this filer has
        # none" (`parent_only`).
        "equity_kind": equity_kind,
        "components": components,
        "residual": residual,
        "relative_residual": relative_residual,
        "tolerance": BALANCE_IDENTITY_TOLERANCE,
    })


def _annotate_balance_identity(
    resolved_by_field: dict[str, list[dict[str, Any]]],
    periods_by_concept: dict[Any, list[dict[str, Any]]],
) -> None:
    """Attach the balance-identity flag, in place, to every FLAGGED period
    of the derived `total_assets` series (module docstring for the why of
    each choice below).

    Writes ONE top-level key on the view's own shallow copy of the period
    entry. Nothing nested is read-modify-written: the `latest` /
    `observations` / `period_labels` objects are still the caller's, and
    mutating one would rewrite the store's payload silently
    (`_resolve_field`).

    ONE FILING SUPPLIES EVERY AMOUNT. The loop picks the vintage FIRST
    (`_identity_vintage`) and then reads all five components out of it, so a
    restated period is checked against its own restatement instead of a
    mixture (module docstring, "ONE VINTAGE, NEVER ACROSS"). A period no
    single filing covers is passed over in silence.

    A period is checked only when total assets, total liabilities, total
    equity AND the term that completes equity are ALL present and numeric IN
    THAT FILING; otherwise it is passed over in silence. Uncheckable is not
    the same as wrong, and a flag on an uncheckable period would be a false
    accusation about figures the filer reported honestly.

    The mezzanine and the minority interest are the components that default
    to 0 when absent, and that asymmetry is measured rather than assumed: 32
    of 46 probed filers are checkable and 30 of those balance EXACTLY under
    the probe's own four-term identity, which can only hold if an untagged
    mezzanine reads as zero -- almost no filer has redeemable instruments to
    tag (`_minority_interest_term` carries the same measurement for the
    minority interest, plus the one case where its absence is uncheckable
    instead). An absent mezzanine line is the balance sheet asserting there
    are none; an absent `Liabilities` line is a SUBTOTAL the filer never
    tagged while the liabilities themselves plainly exist. A mezzanine that
    IS tagged but unreadable stays uncheckable -- it is never quietly
    zeroed.

    WHICH MAKES "ABSENT" A PROPERTY OF THE PERIOD, NOT OF THE CHECKED FILING,
    and that split is deliberate. The PERIOD (across every filing of it) says
    which terms EXIST -- another filing tagging a mezzanine at that instant is
    proof there was one; the CHECKED FILING supplies every AMOUNT. So a term
    the period carries but the checked filing omits is a missing amount and
    the period is uncheckable, never a zero: zeroing it would manufacture a
    residual equal to the omitted term -- the exact false-accusation failure
    this whole check keeps being burned by. Cross-vintage evidence may only
    ever WIDEN uncheckability (`nci_is_asserted` is the same shape); no
    number that enters the arithmetic ever comes from outside the checked
    filing.

    `_balance_identity_flag` shapes and validates each flag this attaches --
    including the one input that makes this module raise.
    """
    def _identity_only_by_key(chain: tuple[str, ...]) -> dict[Any, dict[str, Any]]:
        """One identity-only chain, resolved by the SAME per-period rule the
        spine fields use and indexed on the store's axis key."""
        return _by_axis_key(_resolve_field(_chain_periods(periods_by_concept, chain)))

    assets_by_key = _by_axis_key(resolved_by_field.get("total_assets", []))
    liabilities_by_key = _by_axis_key(resolved_by_field.get("total_liabilities", []))
    equity_by_key = _by_axis_key(resolved_by_field.get("total_equity", []))
    mezzanine_by_key = _identity_only_by_key(MEZZANINE_CHAIN)
    minority_interest_by_key = _identity_only_by_key(MINORITY_INTEREST_CHAIN)
    # Not a term -- only the evidence that a non-controlling interest EXISTS
    # in a period whose `total_equity` resolved parent-only
    # (`_minority_interest_term`, "THE ONE EXCEPTION").
    equity_incl_nci_by_key = _identity_only_by_key((EQUITY_INCL_NCI_CONCEPT,))

    for axis_key, assets_period in assets_by_key.items():
        liabilities_period = liabilities_by_key.get(axis_key)
        equity_period = equity_by_key.get(axis_key)
        mezzanine_period = mezzanine_by_key.get(axis_key)
        minority_interest_period = minority_interest_by_key.get(axis_key)

        # WHICH FILING first, every amount second. A period no single filing
        # covers has no identity to evaluate -- uncheckable, not flagged.
        vintage = _identity_vintage(assets_period, liabilities_period, equity_period)
        if vintage is None:
            continue

        equity_observation = _vintage_observation(equity_period, vintage)
        total_assets = _identity_value(_vintage_observation(assets_period, vintage))
        total_liabilities = _identity_value(
            _vintage_observation(liabilities_period, vintage)
        )
        total_equity = _identity_value(equity_observation)
        # Absent from the PERIOD is the balance sheet asserting zero; absent
        # from the CHECKED FILING while another filing tagged it is a missing
        # amount (`_minority_interest_term` carries the same distinction).
        mezzanine = (
            0 if mezzanine_period is None
            else _identity_value(_vintage_observation(mezzanine_period, vintage))
        )
        equity_kind = _equity_kind(equity_observation)
        minority_interest = _minority_interest_term(
            equity_kind,
            minority_interest_period,
            _vintage_observation(minority_interest_period, vintage),
            nci_is_asserted=axis_key in equity_incl_nci_by_key,
        )

        components = (
            total_assets, total_liabilities, mezzanine, total_equity, minority_interest,
        )
        if equity_kind is None or any(component is None for component in components):
            continue
        if not total_assets:
            # A relative residual has no denominator at zero total assets,
            # and the pinned tolerance is relative. Not checkable, so not
            # flagged -- the same rule as any other missing component.
            continue

        residual = total_assets - (
            total_liabilities + mezzanine + total_equity + minority_interest
        )
        # Plain arithmetic, not Decimal: every component is already the
        # store's base-scale canonical, binary-float error is ~1e-16
        # relative (eleven orders below the 1e-5 tolerance), and a Decimal
        # would not survive the CLI's json.dump.
        relative_residual = abs(residual) / abs(total_assets)
        if relative_residual <= BALANCE_IDENTITY_TOLERANCE:
            continue

        assets_period["balance_identity"] = _balance_identity_flag(
            axis_key=axis_key,
            period_end=assets_period.get("period_end"),
            # ONE filing behind every component, so there is no longer a list
            # to curate: a component read from another vintage is exactly what
            # this check must never do (`_balance_identity_flag`).
            vintage=vintage,
            equity_kind=equity_kind,
            components={
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "mezzanine": mezzanine,
                "total_equity": total_equity,
                "minority_interest": minority_interest,
            },
            residual=residual,
            relative_residual=relative_residual,
        )


def derive_spine(dump: dict[str, Any]) -> dict[str, Any]:
    """Map a `kpi_store dump --company` payload onto the spine fields,
    resolving each field's concept chain PER PERIOD (see module docstring).

    Returns the same pinned schema -- `{"company", "series", "warnings"}` --
    so the shipped formatter consumes it unchanged. `series` carries one
    entry per spine field that any chain concept covers, in
    `SPINE_FIELD_CHAINS` order; a field no concept covers is absent entirely.
    Stored series that are not a spine concept are simply not part of the
    spine view (they remain in the store, and in the raw dump).

    Balance-sheet identity flags are attached here as a final annotation
    pass, because the terms it needs beyond the spine fields -- the mezzanine
    and the minority interest -- are identity-only concepts that no spine
    field carries. They come from `periods_by_concept`, the RAW per-concept
    index built just below, which this function already has in hand (module
    docstring, "WHERE THE MEZZANINE COMES FROM"); the whole index is handed
    over rather than each chain pre-resolved, so the annotator owns which
    identity-only concepts it reads.
    """
    periods_by_concept = {
        entry.get("kpi_id"): entry.get("periods") or []
        for entry in dump.get("series", [])
    }

    series: list[dict[str, Any]] = []
    resolved_by_field: dict[str, list[dict[str, Any]]] = {}
    for field, chain in SPINE_FIELD_CHAINS:
        chain_periods = _chain_periods(periods_by_concept, chain)
        if not chain_periods:
            continue  # honest absence: no row at all, never an empty placeholder
        resolved_by_field[field] = _resolve_field(chain_periods)
        series.append({"kpi_id": field, "periods": resolved_by_field[field]})

    _annotate_balance_identity(resolved_by_field, periods_by_concept)

    return {
        "company": dump.get("company", ""),
        "series": series,
        "warnings": list(dump.get("warnings", [])),
    }


def _read_json_object(path: str | None, noun: str) -> dict[str, Any] | None:
    """This module's ONE CLI input door: a JSON object read from `path`, or
    from stdin when `path` is None.

    Returns `None` having ALREADY reported the reason as `error: ...` on
    stderr, so the caller's only job is `return 1`. Both subcommands read the
    same way from different payloads, and a second copy of this is how the two
    would drift into reporting the same malformed input differently.

    `noun` names the payload the subcommand expected ("dump",
    "reconstruct payload"), which is the whole value of the type message: a
    caller who piped a store dump into `derive-as-filed` is told WHICH shape
    was wanted, not merely that this one was wrong.

    The three message wordings are transcribed from `tearsheet_format.py`'s own
    CLI door, this repo's house shape for exactly this check -- including the
    `in <path>` / `on stdin` split, which reads as English in both branches.
    """
    try:
        if path:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
        else:
            sys.stdin.reconfigure(encoding="utf-8")
            payload = json.load(sys.stdin)
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return None
    except json.JSONDecodeError as exc:
        where = f"in {path}" if path else "on stdin"
        print(f"error: invalid JSON {where}: {exc}", file=sys.stderr)
        return None

    if not isinstance(payload, dict):
        print(
            f"error: top-level {noun} JSON must be an object, got "
            f"{type(payload).__name__}",
            file=sys.stderr,
        )
        return None
    return payload


def _cli_derive(args: argparse.Namespace) -> int:
    """`derive` subcommand: read the dump payload from `--dump` (or stdin
    when omitted), print the spine payload as JSON to stdout.

    Every malformed input leaves by ONE door -- `error: ...` on stderr, exit
    1 -- including the one that reaches `derive_spine` itself: a flagged
    period whose components carry no `source_accession` (see
    `_balance_identity_flag`, "THE ONE PLACE THIS MODULE CAN RAISE").
    The raise is the right library behaviour and is deliberately kept; the
    CLI is the hand-fed surface, so it reports rather than tracebacks. The
    library caller still sees the exception.
    """
    dump = _read_json_object(args.dump_path, "dump")
    if dump is None:
        return 1

    try:
        spine = derive_spine(dump)
    except ValueError as exc:
        print(f"error: cannot derive the spine: {exc}", file=sys.stderr)
        return 1

    sys.stdout.reconfigure(encoding="utf-8")
    json.dump(spine, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Derive the 14 canonical spine fields. TWO entry points over TWO "
            "inputs, because neither is computable from the other: `derive` "
            "reads a kpi_store.py `dump --company` payload and resolves each "
            "field's concept chain per period; `derive-as-filed` reads a "
            "`pack.py --pack reconstruct` payload and reports each field as "
            "the FILER declared it, typing every cell value/not_presented/"
            "not_tagged/derived. Pure view -- no I/O beyond input + stdout."
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

    # The SECOND entry point, over a different input. Its handler and the
    # reason it cannot be a flag on `derive` live in the as-filed section
    # below -- as does everything else the as-filed view needs, which is why
    # that whole apparatus sits under `main()` rather than above it.
    as_filed_parser = subparsers.add_parser(
        "derive-as-filed",
        help=(
            "Emit the 14 spine fields of each filing in a `pack.py reconstruct` "
            "payload, every cell typed value/not_presented/not_tagged/derived."
        ),
    )
    as_filed_parser.add_argument(
        "--payload",
        dest="payload_path",
        default=None,
        help=(
            "Path to the `pack.py --market us --pack reconstruct` JSON payload. "
            "Omit to read stdin."
        ),
    )
    as_filed_parser.set_defaults(func=_cli_derive_as_filed)

    args = parser.parse_args()
    return args.func(args)


# =====================================================================
# THE AS-FILED VIEW (plan Task 7) — the same 14 fields, over the
# RECONSTRUCTION instead of over the store
# =====================================================================
#
# A SECOND ENTRY POINT, NOT A REPLACEMENT, and the reason is structural rather
# than cautious: a store dump carries no calculation linkbase, so the
# reconstruction is not computable from `derive_spine`'s input AT ALL. "Derive
# the fields from the reconstruction" was never a substitution — it is a
# different function over a different input. `derive_spine` and
# `SPINE_FIELD_CHAINS` keep serving the store path unchanged, which is what
# keeps the shipped tearsheet pipe working.
#
# WHAT THE RECONSTRUCTION ACTUALLY BINDS, AND WHAT IT DOES NOT. Exactly one
# field is bound by the filing's own structure: `revenue`. The other thirteen
# resolve their existing chain against the filer's OWN presented lines instead
# of against the store — same concepts, same first-present order, new input.
# That asymmetry is deliberate and is the honest limit of the evidence:
# `revenue` is the field whose blanks the brief measured as "all recoverable"
# because whole sectors use concepts no chain lists, and it is the only field
# for which a structural rule was validated (63 of 65 operating filings, zero
# violations against sum reconciliation). For every other field the chain
# concept IS the filer's own concept in the measured sample, so a structural
# rule there would be an unpinned invention on the money path — and the two
# filings this repo holds rows for cannot discriminate one. When that evidence
# arrives, this is where the rule goes; until then the chain stays and this
# comment says why.
#
# WHAT THE FOUR CELL STATES BUY THE READER. Resolving against the filer's own
# statement is what lets `kpi_us_statement_cells.cell_state` answer WHICH KIND
# of empty a cell is — `not_presented` (IBM files no operating-income line at
# all) is now distinguishable from `not_tagged` and from a derivation, which is
# the single behavioural addition the brief asks of this view.

import kpi_us_statement_cells as statement_cells  # noqa: E402
# The revenue-total rule lives THERE, not here. Both modules needed it, both
# grew their own copy, and by the time the branch was reviewed as a whole the
# two had diverged in three ways at once — see `_revenue_total`.
import kpi_us_statement_check as statement_check  # noqa: E402

# Which statement carries each field. A LOOKUP, not an inference: every entry
# is where the line sits on any US filer's statements, and none of them is a
# judgement call. `cash` is a balance-sheet instant (the cash-flow statement's
# closing balance is the same figure, and reading the balance sheet keeps the
# field an instant like its `total_*` siblings).
_FIELD_STATEMENT: dict[str, str] = {
    "revenue": "income",
    "gross_profit": "income",
    "operating_income": "income",
    "pretax_income": "income",
    "net_income": "income",
    "eps_basic": "income",
    "total_assets": "balance_sheet",
    "total_liabilities": "balance_sheet",
    "total_equity": "balance_sheet",
    "cash": "balance_sheet",
    "operating_cash_flow": "cash_flow",
    "investing_cash_flow": "cash_flow",
    "financing_cash_flow": "cash_flow",
    "capex": "cash_flow",
}


class _ReconstructedLine:
    """One `Line` back out of Task 9's JSON, with the two attributes
    `cell_state` reads (`concept`, `values`) plus the calculation fields the
    revenue rule needs.

    Rehydrated here rather than by importing `kpi_us_statement_shape.Line`
    deliberately: this view's whole input is a JSON payload that has already
    crossed a process boundary, so the dataclass on the far side is not
    available to it in the first place, and reaching for it would couple this
    module to one it never otherwise needs.
    """

    __slots__ = (
        "label", "concept", "level", "weight", "calculation_parent",
        "balance", "values",
    )

    def __init__(self, row: dict[str, Any]) -> None:
        self.label = row.get("label")
        self.concept = row.get("concept")
        self.level = row.get("level")
        self.weight = row.get("weight")
        self.calculation_parent = row.get("calculation_parent")
        # The taxonomy's own debit/credit classification (`Line.balance`).
        # `.get`, not indexing: a payload produced before that field existed
        # reads as None, which is the fail-open answer anyway.
        self.balance = row.get("balance")
        self.values = dict(row.get("values") or {})


class _ReconstructedStatements:
    """The `.by_kind` surface `cell_state` takes — its whole input contract."""

    __slots__ = ("by_kind",)

    def __init__(self, statements: dict[str, list[dict[str, Any]]]) -> None:
        self.by_kind = {
            kind: [_ReconstructedLine(row) for row in rows]
            for kind, rows in (statements or {}).items()
        }


def _local_name(concept: str | None) -> str:
    """A concept without its namespace, in either spelling (`us-gaap_Assets`
    and `us-gaap:Assets` both give `Assets`)."""
    return (concept or "").replace(":", "_").rpartition("_")[2]


def _revenue_total(lines: list[_ReconstructedLine]) -> tuple[str | None, tuple[str, ...]]:
    """The concept this filing declares as its TOTAL revenue, by its own
    calculation tree — with the candidates it could not choose between.

    THE RULE ITSELF IS NOT HERE. It is `kpi_us_statement_check.revenue_totals`,
    and this function only shapes that module's candidate list into the pair
    this view emits. There used to be a second implementation at this site, and
    the whole-branch review measured the two DIVERGED in three ways at once —
    the wording matched, the test for "my parent is a revenue line", and whether
    a repeated presentation row counted once or twice. Each divergence cost the
    same thing, a filer's revenue blanked into a false `unresolved`:

      * this copy also matched the wording `sales`, which admitted a custom
        `...CostOfSales` line as a second candidate. It bought nothing: every
        revenue dialect the brief measured (`SalesRevenueGoodsNet`,
        `SalesRevenueServicesNet`, `RealEstateRevenueNet`, `RevenueMineralSales`,
        `RegulatedAndUnregulatedOperatingRevenue`, `RevenuesAndOtherIncome`)
        carries `revenue` as well, and the two `sales`-only concepts in the
        committed capture are a divestiture gain and an investments line,
        neither of them on an income statement;
      * this copy asked whether a line's calculation parent was among the
        PRESENTED revenue-worded concepts, so a component rolling into a revenue
        total the filer does not present looked parentless and stood as a rival.
        The check tests the parent BY NAME, which is documented deliberate at
        its own site and covers the unpresented-parent case that this one
        missed. It also dissolves the ordering hazard this copy carried a
        comment about — building the parent set before the sign filter — because
        a name is not drawn from a filtered set at all;
      * this copy did not de-duplicate, so a filing whose presentation repeats
        one revenue row was reported ambiguous between its total and itself.

    Two implementations agreeing would not have made either right, either
    (docs/loom/memory/convergence-is-not-evidence-when-the-sample-is-shared.md);
    what makes this one right is that `revenue_totals` is pinned against the
    filed documents in its own suite. See that function for the structural rule
    — a revenue line whose calculation parent is itself revenue-named is a
    COMPONENT — and for the two signals that separate a revenue line from a cost
    line whose local name also carries the revenue wording.

    WHAT THIS FUNCTION DECIDES, which is only the shape: exactly one surviving
    candidate is the filing's total; anything else is `(None, candidates)`, and
    that is the answer rather than a failure. Kickoff decision 甲 requires a
    VISIBLE TYPED GAP where a filing declares no single total, never a fallback
    to `SPINE_FIELD_CHAINS`, because a silently-low year reads as a downturn on
    a ten-year trend. The measured instance is DUK's 2013-2017 FILED range,
    which yields 2-3 candidate totals; its 2018-filed 10-K resolves cleanly to
    `RegulatedAndUnregulatedOperatingRevenue`.

    `(None, ())` is the different case where the filing presents no revenue line
    at all — an honest `not_presented`, which a bank's income statement reaches
    legitimately (the brief's open question about financial-sector filers).

    The candidates come back SORTED rather than in the presentation order
    `revenue_totals` returns them in. That is this view's own published output
    and is left as it was; both orders are deterministic, so neither can make
    two runs over one filing disagree.
    """
    candidates = statement_check.revenue_totals(lines)
    if len(candidates) == 1:
        return candidates[0], ()
    return None, tuple(sorted(candidates))


def _chain_concept(lines: list[_ReconstructedLine], chain: tuple[str, ...]) -> str | None:
    """The first chain concept this filing PRESENTS, or None when it presents
    none — the same first-present rule `_resolve_field` applies per period on
    the store, asked of one filing's statement instead.

    IT RETURNS THE ROW'S OWN SPELLING, not the chain's re-qualified one. A
    statement row spells the namespace separator `_` and the store's `kpi_id`
    spells it `:`; both reach this payload's `concept` key, and
    `kpi_us_statement_series.series_for` — which this view defers the
    multi-year join to — keys series identity on the filer's own concept. Two
    spellings under one key split one series in two.
    """
    presented = {_local_name(line.concept): line.concept for line in lines}
    return next(
        (presented[concept] for concept in chain if concept in presented),
        None,
    )


def _statement_periods(lines: list[_ReconstructedLine]) -> list[str]:
    """Every period key this statement carries, sorted.

    Taken from the STATEMENT rather than from the resolved line, so a field the
    filing does not present still reports `not_presented` FOR EACH PERIOD the
    statement covers instead of reporting nothing — "no such line" is a claim
    about periods the reader is looking at, and an empty period map would
    render as the same undifferentiated blank this view exists to abolish.
    """
    return sorted({period for line in lines for period in line.values})


def _cells(
    statements: _ReconstructedStatements, kind: str, concept: str,
    periods: list[str],
) -> dict[str, dict[str, Any]]:
    """One field's periods, each typed by `kpi_us_statement_cells.cell_state`.

    `cell_state` DECIDES EVERY CELL, including the ones this view binds no line
    for, and that is not a stylistic preference — it is the fix for a defect
    this function shipped with. Answering `not_presented` here as soon as
    nothing was bound is wrong in exactly the case the arc is built on: KO tags
    `LiabilitiesAndStockholdersEquity` and no `Liabilities` line, so nothing
    binds, and yet the figure is computable from the filer's own footing.
    `cell_state`'s own ranking puts `derived` ABOVE `not_presented` for that
    reason. Short-circuiting printed a blank where the filing gives 68,919M —
    the failure this arc exists to remove, reproduced in its own output.

    So an unbound field is asked under its chain's HEAD concept, which is the
    conventional name for the thing that is absent and is what a derivation
    rule is keyed on. `cell_state` then answers `derived` where a rule applies
    and `not_presented` where none does.

    `derivation` rides along ONLY when there is one, so a consumer branching on
    `state` never has to ask whether a blank was our fault: `derived` is the one
    state that carries provenance, and `kpi_us_statement_cells` builds it.
    """
    cells: dict[str, dict[str, Any]] = {}
    for period in periods:
        cell = statement_cells.cell_state(statements, kind, concept, period)
        entry: dict[str, Any] = {"state": cell.state, "value": cell.value}
        if cell.derivation is not None:
            entry["derivation"] = cell.derivation.formula
        cells[period] = entry
    return cells


def _fields_of(filing: dict[str, Any]) -> list[dict[str, Any]]:
    """The 14 fields of ONE filing, in `SPINE_FIELD_CHAINS` order.

    Every field is emitted, including the ones this filer does not present:
    absence is the answer here, not a reason to omit a row (which is the
    opposite of `derive_spine`'s honest-absence rule over the store, and
    deliberately so — there, a missing row means no filing in a decade tagged
    the concept; here it would hide WHICH of the four empties this filing has).
    """
    statements = _ReconstructedStatements(filing.get("statements") or {})
    fields: list[dict[str, Any]] = []
    for field, chain in SPINE_FIELD_CHAINS:
        kind = _FIELD_STATEMENT[field]
        lines = statements.by_kind.get(kind) or []
        unresolved: tuple[str, ...] = ()
        if field == "revenue":
            concept, unresolved = _revenue_total(lines)
        else:
            concept = _chain_concept(lines, chain)
        entry: dict[str, Any] = {
            "field": field,
            "concept": concept,
            "statement": kind,
            "periods": (
                # The ONE hard gap, and it is decision 甲: an ambiguous total
                # must not be resolved, so there is nothing to ask `cell_state`
                # about. Every other unbound field goes through it under the
                # chain's head, because "nothing bound" is exactly when a
                # derivation can still apply.
                {} if unresolved
                else _cells(
                    statements, kind, concept or f"{_US_GAAP}{chain[0]}",
                    _statement_periods(lines),
                )
            ),
        }
        if unresolved:
            # The typed gap: the candidates are named so a reader can
            # adjudicate, and NO figure rides along -- emitting one would be
            # this view picking a total, which is the decision it just declined.
            entry["unresolved"] = unresolved
        fields.append(entry)
    return fields


def derive_spine_as_filed(payload: dict[str, Any]) -> dict[str, Any]:
    """The 14 spine fields of each filing in a Task 9 `reconstruct` payload,
    as the FILER declared them (plan Task 7).

    Input is `pack_us.pack_reconstruct`'s output — plain JSON, which is what
    makes this offline-testable — and the answer is PER FILING. Joining N
    filings into a ten-year series is `kpi_us_statement_series.series_for`'s
    job, over live filings and by the store's newest-filed rule; reimplementing
    that join here would be a second copy of a vintage policy this repo already
    owns in one place.

    VALUES ARE `Decimal`, carried up from `cell_state` (brief: "arithmetic in
    `Decimal`, never binary float"), so a JSON consumer must project them
    before serializing.

    THIS DOCSTRING USED TO SAY "nothing in this repo serializes this payload
    today" and to recommend `json.dump(..., default=str)`. Both were true only
    while the view was reachable in-process alone. The `derive-as-filed`
    subcommand below is now that consumer, and it does NOT use that fallback:
    it projects explicitly via `_project_money_to_text` and dumps BARE, so a
    value it ever failed to reach raises at the boundary rather than being
    quietly stringified — see that function for why the fallback is the weaker
    of the two. The shipped `derive` CLI is a different entry point over a
    different input and is untouched.
    """
    reconstruction = payload.get("reconstruction") or {}
    view = {
        "company": payload.get("company") or "",
        "filings": [
            {
                "accession": filing.get("accession"),
                "filing_date": filing.get("filingDate"),
                "fields": _fields_of(filing),
            }
            for filing in reconstruction.get("filings") or []
        ],
        # Acquisition failures ride through verbatim: a filing that could not be
        # read is not a filing whose fields are empty, and a reader comparing
        # years must be able to tell the two apart.
        "failed_items": list(reconstruction.get("failed_items") or []),
        "warnings": list(payload.get("warnings") or []),
    }
    # AND SO DOES THE RUN'S OWN VERDICT ON ITSELF, for the same reason and one
    # level up. `pack_reconstruct` contains a refusing verification layer
    # rather than letting it take the whole run down, and says so TWICE -- an
    # `error` + `error_class` marker inside `verification`, and a fold of the
    # section's `_status` to "partial". `references/cli-reference.md`
    # recommends piping that pack straight into this view, so a view that
    # carried the filings and dropped both markers would hand its reader a
    # payload byte-identical to a clean run's: an unreadable blank, which is
    # the exact defect the four cell states exist to remove.
    #
    # NEITHER IS INTERPRETED HERE. `verification` rides whole because its three
    # parts (by_era / statements / sum_checks) are the pack's answer to
    # "was the arithmetic checked, and what did it say", and a summary of it
    # invented at this layer would be a second opinion nobody asked this
    # module for.
    #
    # ABSENT, NEVER EMPTY, on the doctrine `_reconstruction_payload` states for
    # `by_kind`: `{}` would claim a verification that ran and found nothing to
    # say. A payload carrying no marker -- hand-fed, or from a pack older than
    # the verification layer -- leaves the key out.
    status = reconstruction.get("_status")
    if status is not None:
        view["status"] = status
    verification = reconstruction.get("verification")
    if verification is not None:
        view["verification"] = verification
    return view


def _project_money_to_text(view: dict[str, Any]) -> dict[str, Any]:
    """Every cell `value` in `view` as EXACT TEXT, in place.

    `str(Decimal)` is digit-for-digit lossless and keeps the scale the
    arithmetic produced. The two alternatives both lose, and this is the same
    projection `pack_us._decimal_text` makes at the same kind of boundary:

      * `float(value)` routes an exact decimal back through the binary
        representation this module family bans on money -- the mode that
        already manufactured a false restatement signal here once
        (docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md);
      * `json.dump(..., default=str)` would do the right thing TODAY and would
        equally happily serialize a float, so the projection is EXPLICIT here
        and the dump below is BARE. A `Decimal` this function ever failed to
        reach then raises `TypeError` at the boundary instead of being quietly
        stringified by a fallback -- fail loud on our own bug, since a silent
        one is a wrong number wearing a correct-looking label.

    IN PLACE, on the freshly-built dict `derive_spine_as_filed` just returned
    and nothing else references. A copy would be honest too and is not worth
    the walk; a caller reaching this function with a value it still needs as
    `Decimal` would be reaching past the CLI layer this belongs to.
    """
    for filing in view["filings"]:
        for field in filing["fields"]:
            for cell in field["periods"].values():
                if cell["value"] is not None:
                    cell["value"] = str(cell["value"])
    return view


def _cli_derive_as_filed(args: argparse.Namespace) -> int:
    """`derive-as-filed` subcommand: read a `reconstruct` pack payload from
    `--payload` (or stdin when omitted), print the as-filed spine view as JSON
    to stdout.

    A SEPARATE SUBCOMMAND RATHER THAN A FLAG ON `derive`, because the two read
    DIFFERENT INPUTS -- a `kpi_store dump --company` payload and a
    `pack.py --market us --pack reconstruct` payload -- and neither is
    computable from the other (a store dump carries no calculation linkbase;
    see this section's header). A flag would advertise a choice of OUTPUT over
    one input, which is not what is on offer, and `derive` keeps working
    unchanged either way.

    WHAT IT PUTS ON THE COMMAND SURFACE, which is the point of it existing: the
    four cell states. Without this the taxonomy answers the user's actual
    question -- "is this cell empty because the company has no such line, or
    because my pipeline lost it?" -- only to an in-process caller.

    Malformed input leaves by the same door `derive` uses (`_read_json_object`).
    """
    payload = _read_json_object(args.payload_path, "reconstruct payload")
    if payload is None:
        return 1

    try:
        view = derive_spine_as_filed(payload)
    except (AttributeError, TypeError, ValueError) as exc:
        # A hand-fed payload whose `reconstruction` or `filings` is the wrong
        # SHAPE (a string where an object belongs) reaches the view as an
        # attribute or type error, not a `ValueError` -- `derive`'s single
        # `ValueError` catch is narrower because its own producer-shaped raise
        # is the only one it can hit. Reported, not tracebacked, for the same
        # reason: this is the hand-fed surface. The library caller still sees
        # the exception.
        print(f"error: cannot derive the as-filed spine: {exc}", file=sys.stderr)
        return 1

    sys.stdout.reconfigure(encoding="utf-8")
    json.dump(_project_money_to_text(view), sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
