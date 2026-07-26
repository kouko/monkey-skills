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
dump payload it is handed. It imports no data-markets module, and its ONE
sibling import is `kpi_xbrl`, for `assert_dqc_schema`.

That import is NOT store-free transitively, and the accurate statement is the
one worth having here, because a "imports no store module" line tells the
next reader not to look -- which is exactly how store I/O enters a pure view
unnoticed. The real chain: `kpi_xbrl` imports `kpi_series` (`kpi_xbrl.py:145`)
-> `kpi_break` (`kpi_series.py:54`) -> `_store_fs` AND `review_queue`
(`kpi_break.py:64-65`). So this module's import graph does reach the store's
filesystem module.

Runtime purity nonetheless holds today, for a reason that is CHECKABLE rather
than asserted, and both halves must be re-verified before a second sibling
import is added:
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

# IDENTITY-ONLY chain -- same first-present-per-period semantics as a spine
# field's, but deliberately NOT a member of SPINE_FIELD_CHAINS: it never
# becomes a `series` row (module docstring, "WHERE THE MEZZANINE COMES
# FROM"). Transcribed from the same pinned block in
# docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md ## Notes.
MEZZANINE_CHAIN: tuple[str, ...] = (
    "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests",
    "RedeemableNoncontrollingInterestEquityCarryingAmount",
)

# The pin's third identity-only concept: the non-controlling interest that
# completes a PARENT-ONLY equity total into whole equity (module docstring,
# "THE EQUITY TERM IS WHOLE EQUITY"). Also identity-only -- never a `series`
# row -- and read from the same raw index as the mezzanine.
MINORITY_INTEREST_CHAIN: tuple[str, ...] = (
    "MinorityInterest",
)

# The two `total_equity` chain members BY NAME, because the identity branches
# on WHICH of them a period resolved to. Naming them separately from the
# chain keeps the chain's transcription diffable against the plan
# character-for-character; the guard below is what stops the two copies from
# drifting apart silently.
EQUITY_PARENT_ONLY_CONCEPT = "StockholdersEquity"
EQUITY_INCL_NCI_CONCEPT = (
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
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
    """
    if chain != (EQUITY_PARENT_ONLY_CONCEPT, EQUITY_INCL_NCI_CONCEPT):
        raise RuntimeError(
            "kpi_spine_view: the total_equity chain "
            f"{chain} no longer matches the two concepts the "
            "balance-sheet identity branches on "
            f"({EQUITY_PARENT_ONLY_CONCEPT!r}, {EQUITY_INCL_NCI_CONCEPT!r}) -- "
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


def _identity_value(observation: dict[str, Any] | None) -> int | float | None:
    """A component's figure for the identity: ONE observation's
    `canonical_value`, when that is a real number.

    `canonical_value` is the store's BASE-scale figure (the point's `scale`
    already applied), so the components are directly comparable and no
    magnitude is re-derived here. Anything else -- an absent observation, an
    unparseable string value, a bool -- returns None, i.e. uncheckable.

    An OBSERVATION, not a period entry, and that is the whole vintage fix
    (module docstring, "ONE VINTAGE, NEVER ACROSS"): a period entry's `latest`
    is per-COMPONENT, so reading it here compared figures from different
    filings.
    """
    if observation is None:
        return None
    value = observation.get("canonical_value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


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


def _equity_kind(equity_observation: dict[str, Any] | None) -> str | None:
    """Which `total_equity` chain member the CHECKED filing reported --
    `"parent_only"`, `"incl_NCI"`, or None when it is neither.

    Read from the checked observation's own `kpi_id`, i.e. the concept whose
    amount the identity is about to use, so the branch can never disagree
    with the number it is branching for. None (a `total_equity` entry
    carrying some other concept, only reachable from a hand-fed payload)
    makes the period uncheckable rather than guessed at.
    """
    if equity_observation is None:
        return None
    concept = equity_observation.get("kpi_id")
    if concept == f"{_US_GAAP}{EQUITY_INCL_NCI_CONCEPT}":
        return "incl_NCI"
    if concept == f"{_US_GAAP}{EQUITY_PARENT_ONLY_CONCEPT}":
        return "parent_only"
    return None


def _minority_interest_term(
    equity_kind: str | None,
    minority_interest_period: dict[str, Any] | None,
    minority_interest_observation: dict[str, Any] | None,
    nci_is_asserted: bool,
) -> int | float | None:
    """The amount to ADD to this period's `total_equity` to make it whole
    equity. None means uncheckable.

    On the `incl_NCI` branch the term is 0 by construction -- the resolved
    concept already contains the non-controlling interest, and adding it
    again would double-count.

    On the `parent_only` branch a tagged `MinorityInterest` is the term. An
    UNTAGGED one reads as 0 -- measured, exactly like the mezzanine: of the
    committed probe's 32 checkable filers, 13 resolved parent-only with no
    `MinorityInterest` at that instant (its `parent_plus_MI` branch fired
    ZERO times in-sample) and all 13 balance EXACTLY, which can only hold if
    absence means "no non-controlling interest". Making absence uncheckable
    instead would silence the identity for the single-entity majority.

    UNTAGGED means untagged for the PERIOD, by any filing -- which is why the
    period entry AND the checked filing's observation are separate arguments.
    A period some OTHER filing tagged is a period that demonstrably HAD a
    non-controlling interest, so the checked filing simply not carrying the
    amount is a MISSING AMOUNT (None here), never a zero: zeroing it would
    manufacture a residual equal to the interest and falsely accuse the filer
    (module docstring, "ONE VINTAGE, NEVER ACROSS").

    THE ONE EXCEPTION, and the reason `nci_is_asserted` exists: a filer that
    tags BOTH equity totals for the period is asserting an NCI EXISTS -- it
    is the line between the two subtotals -- so an absent `MinorityInterest`
    there is a MISSING AMOUNT, not a zero, and the period is uncheckable.
    Reading 0 would reproduce the very defect this branch fixes (residual =
    the NCI, filer falsely accused); substituting the incl-NCI figure would
    instead make the flag's own `components.total_equity` disagree with the
    `total_equity` the flag's own `checked_vintage` reported, which no reader
    could reconcile. Uncheckable is the honest third answer.
    """
    if equity_kind == "incl_NCI":
        return 0
    if minority_interest_period is not None:
        # Tagged for this period: the CHECKED filing must supply the amount.
        # A missing or unreadable one stays uncheckable (`_identity_value`
        # returns None) -- never quietly zeroed, same as the mezzanine.
        return _identity_value(minority_interest_observation)
    return None if nci_is_asserted else 0


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
