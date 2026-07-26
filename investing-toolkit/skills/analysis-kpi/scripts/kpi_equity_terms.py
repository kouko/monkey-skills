#!/usr/bin/env python3
"""kpi_equity_terms.py — the WHOLE-EQUITY primitives, in the one module both
sides of the as-filed lane import.

WHY THIS MODULE EXISTS. `kpi_spine_view`'s balance-sheet identity and
`kpi_us_statement_cells`'s total-liabilities derivation are the same accounting
question asked of two different inputs (a bitemporal store dump; one filing's
reconstructed statement), and the brief forbids answering it twice: "the
existing `_equity_kind` / mezzanine machinery already resolves whole equity and
must be reused rather than re-derived". Task 5 honoured that by importing
`kpi_spine_view` — correct then, and a CYCLE the moment Task 7 makes
`kpi_spine_view` consume the reconstruction (plan
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md ## Decision Log,
"Task 5 -> Task 7. THE DEPENDENCY IS ABOUT TO INVERT INTO A CYCLE").

THE CYCLE WAS REPRODUCED BEFORE IT WAS BROKEN, by mutation rather than by
reasoning: with `import kpi_us_statement_cells` added to `kpi_spine_view`,
`import kpi_spine_view` raises `AttributeError: partially initialized module
'kpi_spine_view' has no attribute 'SPINE_FIELD_CHAINS'` while
`import kpi_us_statement_cells` still succeeds. The breakage is real and
ORDER-DEPENDENT — which is why it cannot be left to be discovered: whichever
module a future caller imports first decides whether the process starts.
`test_kpi_equity_terms.py` pins the structural cure (the cells module does not
import the spine view at all), not the symptom.

THIS MODULE IMPORTS NEITHER SIDE, and that is the whole property: it is
stdlib-only and leaf, so no import order through it can fail.

NOTHING HERE IS NEW. Every constant and every rule below was moved verbatim
from `kpi_spine_view`, docstrings included, because their prose IS the measured
evidence for the branches (17 of 32 filers on the parent-only branch; 13 of 32
with no tagged `MinorityInterest`, all balancing exactly). The functions keep
their leading underscore even though two modules import them: the Decision Log
requires all eight bindings to survive Task 7 "by name AND by semantics", and a
rename in the same change as a move is how a lift turns into a silent semantic
edit. Renaming them to a public spelling is a separate, reviewable change.

WHAT DID NOT MOVE. `SPINE_FIELD_CHAINS` stays in `kpi_spine_view` — plan Task 11
owns its disposition and asserts against THAT file's source text — so the
`total_equity` pair lives here as `EQUITY_CHAIN` and `kpi_spine_view`'s
import-time `_assert_equity_chain` is what keeps the two from drifting apart.
That guard moves the drift check from "runs whenever either importer loads" to
"runs whenever the spine view loads, plus one test". The check that matters is
unchanged: the chain and the pair can no longer be transcribed independently,
because `kpi_us_statement_cells` now reads the pair from here rather than
copying it out of the chain.
"""
from __future__ import annotations

from typing import Any

# The store holds the filer's own qname verbatim, namespace preserved
# (`us-gaap:Revenues`), so the chains transcribed as bare local names from the
# plan's pin are qualified with this namespace on lookup.
_US_GAAP = "us-gaap:"

# IDENTITY-ONLY chain -- same first-present-per-period semantics as a spine
# field's, but deliberately NOT a member of SPINE_FIELD_CHAINS: it never
# becomes a `series` row (`kpi_spine_view`'s docstring, "WHERE THE MEZZANINE
# COMES FROM"). Transcribed from the pinned block in
# docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md ## Notes.
MEZZANINE_CHAIN: tuple[str, ...] = (
    "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests",
    "RedeemableNoncontrollingInterestEquityCarryingAmount",
)

# The pin's third identity-only concept: the non-controlling interest that
# completes a PARENT-ONLY equity total into whole equity (`kpi_spine_view`'s
# docstring, "THE EQUITY TERM IS WHOLE EQUITY"). Also identity-only -- never a
# `series` row -- and read from the same raw index as the mezzanine.
MINORITY_INTEREST_CHAIN: tuple[str, ...] = (
    "MinorityInterest",
)

# The two `total_equity` chain members BY NAME, because the identity branches
# on WHICH of them a period resolved to. Naming them separately from
# `kpi_spine_view.SPINE_FIELD_CHAINS` keeps that chain's transcription diffable
# against the plan character-for-character; `kpi_spine_view._assert_equity_chain`
# is what stops the two copies from drifting apart silently.
EQUITY_PARENT_ONLY_CONCEPT = "StockholdersEquity"
EQUITY_INCL_NCI_CONCEPT = (
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
)

# The pair AS A CHAIN, parent-only FIRST -- which is the resolution order, not a
# presentation detail: it decides that the majority of periods resolve to the
# parent-only concept and therefore take the minority-interest term
# (`kpi_spine_view`'s docstring measures 17 of 32 checkable filers there).
# Consumers read this rather than re-transcribing the pair or slicing it out of
# `SPINE_FIELD_CHAINS`.
EQUITY_CHAIN: tuple[str, ...] = (
    EQUITY_PARENT_ONLY_CONCEPT,
    EQUITY_INCL_NCI_CONCEPT,
)


def _identity_value(observation: dict[str, Any] | None) -> int | float | None:
    """A component's figure for the identity: ONE observation's
    `canonical_value`, when that is a real number.

    `canonical_value` is the store's BASE-scale figure (the point's `scale`
    already applied), so the components are directly comparable and no
    magnitude is re-derived here. Anything else -- an absent observation, an
    unparseable string value, a bool -- returns None, i.e. uncheckable.

    An OBSERVATION, not a period entry, and that is the whole vintage fix
    (`kpi_spine_view`'s docstring, "ONE VINTAGE, NEVER ACROSS"): a period
    entry's `latest` is per-COMPONENT, so reading it here compared figures from
    different filings.
    """
    if observation is None:
        return None
    value = observation.get("canonical_value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


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
    (`kpi_spine_view`'s docstring, "ONE VINTAGE, NEVER ACROSS"). A caller with
    only ONE filing in hand -- `kpi_us_statement_cells`, reconstructing a
    single statement -- satisfies both arguments from that statement, which
    collapses the distinction without changing the rule.

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
