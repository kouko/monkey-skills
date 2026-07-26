#!/usr/bin/env python3
"""kpi_us_statement_check.py — check every sum the FILER DECLARED against the
filer's OWN reported numbers (plan Task 4),
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md.

THIS IS THE ARC'S INDEPENDENT ORACLE, and it is worth saying exactly why it
counts as one. The structure claims "these are the parts of that one"; this
makes the filer's numbers answer. The two sides come from DIFFERENT places —
the parent-child hierarchy and the weights come from the calculation linkbase,
every value comes from the fact table — and nothing forces them to agree. So it
is not the empty kind of check that holds by construction
(docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md).

ARITHMETIC IS `Decimal`, NEVER BINARY FLOAT — same memory, second half. The
values arrive as Python floats and are converted through their STRING form, so
`1.005` stays `1.005` instead of becoming `1.00499999999999989…`. Measured on a
three-decimal-place group: the binary-float version of this module reported
`1.005 + 0.005` against a filer-reported `1.01` as a DISAGREEMENT
(`computed=1.0099999999999998`) — a fabricated finding on data that reconciles
exactly. `test_sum_check_uses_decimal_not_binary_float` pins it, and pins its
own float-hostility premise so it cannot quietly stop testing anything.

THREE STATUSES, AND THE THIRD IS THE POINT:

  `agrees`     — the children sum to the parent's own reported figure.
  `disagrees`  — they do not. The filer's declaration and the filer's numbers
                 contradict each other.
  `incomplete` — the comparison could not be made: some child has no usable
                 value for that period, or the parent has none. A MISSING CHILD
                 IS NOT A WRONG SUM. Collapsing the two would make the report
                 worthless exactly where a filer's tagging is thin, which is
                 where a reader most needs to be told the difference.

Nothing is ever auto-corrected. `computed` is what the filer's own declaration
produces, even when that is visibly wrong — whether the three known cash-flow
declaration quirks should ever be corrected is an OPEN QUESTION in the brief
(§Open Questions) and is deliberately not decided here.

TWO LIMITS OF THIS CHECK, both measured, both stated here because a status read
without them will be over-trusted:

  1. THE COMPARISON IS EXACT, AND FILERS ROUND. A `decimals` attribute says how
     precisely each fact was stated; filers round each fact independently, so
     the sum of n independently-rounded children can miss the parent by up to
     n/2 units in the last place without either being wrong. `Line` (Task 3)
     does not carry `decimals`, so this module cannot see the claimed
     precision and compares exactly. MEASURED on the committed capture (KO
     FY2017 + IBM FY2025, 96 checkable group-periods): 27 come out
     `disagrees`, of which 24 are inside the filers' own declared rounding
     interval and would be `agrees` to a precision-aware comparison. Treating
     the raw `disagrees` count as "the filer's arithmetic is wrong" therefore
     overstates it by roughly 8x on this sample, and would not reproduce the
     brief's measured 98.4% reconciliation rate. Closing this needs one field
     (`decimals`) on `Line`, which is Task 3's module and outside this task.
     `test_every_disagreement_in_the_capture_is_accounted_for` measures the
     split on every run so the gap cannot be forgotten.
  2. IT SEES PRESENTED LINES ONLY. The calculation linkbase may declare a child
     the filer never puts on the face of the statement; that child is invisible
     here, and its absence looks like a disagreement rather than a gap. OBSERVED
     in the capture: IBM FY2025 declares `...WeightedAverageNumberOfShares
     OutstandingBasic` as the only PRESENTED child of `...NumberOfDiluted
     SharesOutstanding`, so the check falls 10-16M shares short in each of three
     years and reports `disagrees` — a false positive. Separating it from a real
     disagreement requires the calculation linkbase, which `verify(statements)`
     does not receive.

WHAT IS DELIBERATELY NOT HERE: per-era resolution-rate reporting (plan Task 8,
which lands in this module next) and the cell taxonomy (Task 5). This module
answers one question per declared group and period, and stores nothing.

PURE FUNCTION, NO I/O, STDLIB ONLY. `verify` is a pure function of its input,
in keeping with the plan's kickoff decision that the reconstruction is
RECOMPUTED and never persisted.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

AGREES = "agrees"
DISAGREES = "disagrees"
INCOMPLETE = "incomplete"


@dataclass(frozen=True)
class Term:
    """One child of a declared sum, with what it contributed for one period.

    `value` is `None` when that period carries no usable number for this child;
    the child is still listed, because a report that silently drops the child it
    could not read tells the reader nothing about why the group is incomplete.
    """

    concept: str
    label: str
    weight: Decimal
    value: Decimal | None


@dataclass(frozen=True)
class SumCheck:
    """One declared calculation parent, checked for ONE period.

    `reported` is the parent's OWN figure and is `None` when the filer states
    none for that period — including when the parent is not presented as a line
    of this statement at all (KO presents two children of
    `CashCashEquivalentsAndShortTermInvestments` on its cash-flow statement and
    never that parent). `None` is the honest answer there; a substitute figure
    would be this code's opinion wearing the filer's name.

    `computed` is Σ(child × weight) over the DISTINCT child concepts, and is
    `None` when any child is unusable — a partial sum presented as a total is a
    fabricated number, which is the failure mode this whole arc exists to
    remove.

    `difference` is `computed - reported`, and is `None` unless both exist. It
    is the figure a reader argues with: for the NEE case the plan names, it is
    exactly the net income that got counted twice.
    """

    kind: str
    period: str
    parent: str
    status: str
    reported: Decimal | None
    computed: Decimal | None
    difference: Decimal | None
    terms: tuple[Term, ...]
    unsummable_children: tuple[str, ...]


def verify(statements) -> list[SumCheck]:
    """Every sum `statements` declares, checked against the filer's own figures.

    `statements` need only expose `by_kind` — the mapping Task 3's `Statements`
    carries, from statement kind to its lines in presentation order — where
    each line exposes `concept`, `label`, `weight`, `calculation_parent` and
    `values`. That attribute surface is the whole input contract.

    The result is one `SumCheck` per (declared parent, period), ordered by
    statement, then by where the group's first child appears on the statement,
    then by period. Deterministic: two runs over one filing never disagree.
    """
    checks: list[SumCheck] = []
    for kind, lines in statements.by_kind.items():
        checks.extend(_checks_for_statement(kind, lines))
    return checks


def _checks_for_statement(kind: str, lines) -> list[SumCheck]:
    first_line_of: dict[str, object] = {}
    for line in lines:
        first_line_of.setdefault(line.concept, line)

    groups: dict[str, dict[str, object]] = {}
    for line in lines:
        if not line.calculation_parent:
            continue
        _weight_of(line)  # fail loud here, before any arithmetic is attempted
        # ONE CHILD PER CONCEPT. A calculation arc is declared between
        # CONCEPTS, so one concept cannot be two children of one parent, while
        # the PRESENTATION may well render the same fact on two rows — KO shows
        # `CashAndCashEquivalentsAtCarryingValue` as both "Balance at beginning
        # of year" and "Balance at end of year", with identical values, weight
        # and parent. Counting both would double that child and manufacture a
        # disagreement out of a layout choice.
        groups.setdefault(line.calculation_parent, {}).setdefault(line.concept, line)

    checks: list[SumCheck] = []
    for parent, children in groups.items():
        parent_line = first_line_of.get(parent)
        # The parent's OWN periods are included, not just the children's: a
        # filer that reports a total for a period in which it presents no
        # components is a group this must report as `incomplete`, not one it
        # should never mention.
        periods = {period for child in children.values() for period in child.values}
        if parent_line is not None:
            periods |= set(parent_line.values)
        for period in sorted(periods):
            checks.append(_check_one(kind, parent, parent_line, children, period))
    return checks


def _check_one(kind, parent, parent_line, children, period) -> SumCheck:
    terms = []
    unsummable = []
    for child in children.values():
        value = _number(child.values.get(period))
        if value is None:
            unsummable.append(child.concept)
        terms.append(Term(
            concept=child.concept,
            label=child.label,
            weight=_weight_of(child),
            value=value,
        ))

    computed = None
    if not unsummable:
        computed = sum((term.value * term.weight for term in terms), Decimal(0))
    reported = _number(parent_line.values.get(period)) if parent_line else None

    if computed is None or reported is None:
        status, difference = INCOMPLETE, None
    else:
        difference = computed - reported
        status = AGREES if difference == 0 else DISAGREES

    return SumCheck(
        kind=kind,
        period=period,
        parent=parent,
        status=status,
        reported=reported,
        computed=computed,
        difference=difference,
        terms=tuple(terms),
        unsummable_children=tuple(unsummable),
    )


def _weight_of(line) -> Decimal:
    """The line's calculation weight, or a loud failure.

    A row that declares a calculation parent and no usable weight is a shape
    this repo has never seen: all 175 rows carrying a `calculation_parent` in
    the committed capture carry a weight, and every observed weight is 1.0 or
    -1.0. Assuming 1.0 for a missing one would put a plausible number in the
    report with nothing marking it as assumed — so it raises instead, naming
    the row, because the alternative is silent corruption.
    """
    weight = _number(line.weight)
    if weight is None:
        raise ValueError(
            f"{line.concept} declares calculation parent "
            f"{line.calculation_parent} but weight {line.weight!r}, which is "
            "not a usable number; refusing to assume a weight"
        )
    return weight


def _number(value) -> Decimal | None:
    """`value` as an exact `Decimal`, or `None` when it is not a usable number.

    THROUGH THE STRING FORM, deliberately: `Decimal(str(1.005))` is
    `Decimal("1.005")`, while `Decimal(1.005)` is the binary double's true
    value `1.00499999999999989…` — which carries in the very error the
    conversion exists to leave behind.

    `None` covers a value that is absent, empty, non-numeric, or a float NaN /
    infinity. OBSERVED in the committed capture: IBM presents
    `us-gaap_CommitmentsAndContingencies` with the value `''` — a line with no
    number. The brief records what happens when such a value reaches the
    arithmetic: 5 of the reconciliation probe's 8 failures were "a probe
    artifact (a non-numeric child)", i.e. fabricated disagreements. `bool` is
    excluded although Python calls it an `int`: `True` is not a reported figure.
    """
    if value is None or isinstance(value, bool):
        return None
    if not isinstance(value, (int, float, str, Decimal)):
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return number if number.is_finite() else None
