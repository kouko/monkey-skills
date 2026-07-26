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

FOUR STATUSES, AND THE LAST TWO ARE THE POINT:

  `agrees`         — the children sum to the parent's own reported figure,
                     exactly.
  `within_rounding`— they differ, but by less than the precision the FILER
                     declared permits. Not a filer error, and not exact
                     agreement either; saying either would be a lie in one
                     direction or the other.
  `disagrees`      — they differ by more than that. The filer's declaration and
                     the filer's numbers contradict each other — SUBJECT TO
                     LIMIT 2 below, which this module cannot see past.
  `incomplete`     — the comparison could not be made: some child has no usable
                     value for that period, or the parent has none. A MISSING
                     CHILD IS NOT A WRONG SUM. Collapsing the two would make the
                     report worthless exactly where a filer's tagging is thin,
                     which is where a reader most needs to be told the
                     difference.

`RECONCILES` names the two statuses that mean the declared arithmetic held, so
a consumer never spells that judgement out for itself.

Nothing is ever auto-corrected. `computed` is what the filer's own declaration
produces, even when that is visibly wrong — whether the three known cash-flow
declaration quirks should ever be corrected is an OPEN QUESTION in the brief
(§Open Questions) and is deliberately not decided here.

TWO LIMITS OF THIS CHECK, both measured, both stated here because a status read
without them will be over-trusted:

  1. CLOSED 2026-07-26 (plan Task 8) — RECORDED, NOT DELETED, because the
     number it explains is what makes the second limit legible. This module
     used to compare EXACTLY, since `Line` carried no `decimals`. MEASURED on
     the committed capture (KO FY2017 + IBM FY2025, 96 checkable
     group-periods): 27 came out `disagrees`, of which 24 were inside the
     filers' own declared rounding interval — a ~8x overstatement of broken
     filer arithmetic, which would not have reproduced the brief's measured
     98.4% reconciliation rate. `Line.decimals` (added by Task 8, whose
     `Files touched` was widened for it) now carries the filer's own claimed
     precision, `_rounding_tolerance` applies it, and those 24 report as
     `within_rounding`. What SURVIVES of this limit: the interval is the
     filer's claim, not a proof of correctness — a group inside it has not been
     shown right, only not shown wrong.
  2. IT SEES PRESENTED LINES ONLY. The calculation linkbase may declare a child
     the filer never puts on the face of the statement; that child is invisible
     here, and its absence looks like a disagreement rather than a gap. OBSERVED
     in the capture: IBM FY2025 declares `...WeightedAverageNumberOfShares
     OutstandingBasic` as the only PRESENTED child of `...NumberOfDiluted
     SharesOutstanding`, so the check falls 10-16M shares short in each of three
     years and reports `disagrees` — a false positive. Separating it from a real
     disagreement requires the calculation linkbase, which `verify(statements)`
     does not receive.

TWO FUNCTIONS, TWO SCOPES. `verify` answers one question per declared group
and period. `resolution_report` (plan Task 8) aggregates a whole run of
filings into how many statements resolved and how many did not, BROKEN DOWN BY
FILING ERA, with the reason each unresolved one failed — see its own docstring
for what "resolved" means and, more importantly, what it does not mean.

WHAT IS DELIBERATELY NOT HERE: the cell taxonomy (Task 5). Nothing is stored.

PURE FUNCTION, NO I/O, STDLIB ONLY. `verify` is a pure function of its input,
in keeping with the plan's kickoff decision that the reconstruction is
RECOMPUTED and never persisted.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

AGREES = "agrees"
WITHIN_ROUNDING = "within_rounding"
DISAGREES = "disagrees"
INCOMPLETE = "incomplete"

# The statuses that mean "the filer's declared arithmetic held". ONE SITE, so a
# consumer never re-derives it: `status == AGREES` was the whole answer before
# `within_rounding` existed, and every such test silently became wrong the
# moment it stopped being. `incomplete` is deliberately absent — a comparison
# that could not be made is not a comparison that passed.
RECONCILES = (AGREES, WITHIN_ROUNDING)


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

    `tolerance` is how far `difference` was allowed to stray before the status
    became `disagrees` — the filers' OWN declared precision, never a constant
    of ours (see `_rounding_tolerance`). It is `Decimal(0)` when the filer
    declared no precision, which is the exact comparison this module was born
    with. Carried on the result rather than kept private because a reader
    holding the filing must be able to argue with the interval, not just with
    the verdict.
    """

    kind: str
    period: str
    parent: str
    status: str
    reported: Decimal | None
    computed: Decimal | None
    difference: Decimal | None
    tolerance: Decimal
    terms: tuple[Term, ...]
    unsummable_children: tuple[str, ...]


def verify(statements) -> list[SumCheck]:
    """Every sum `statements` declares, checked against the filer's own figures.

    `statements` need only expose `by_kind` — the mapping Task 3's `Statements`
    carries, from statement kind to its lines in presentation order — where
    each line exposes `concept`, `label`, `weight`, `calculation_parent`,
    `values` and `decimals`. That attribute surface is the whole input
    contract. `decimals` joined it with plan Task 8 and is read directly rather
    than through a `getattr` default: a line without it is an integration
    break, and defaulting one in would silently restore the exact comparison
    for every filer that did declare a precision.

    The result is one `SumCheck` per (declared parent, period), ordered by
    statement, then by where the group's first child appears on the statement,
    then by period. Deterministic: two runs over one filing never disagree.

    BLAST RADIUS OF THE TWO RAISES (a row with a parent but no usable weight,
    and two rows of one concept that disagree): both abort this call, and since
    `resolution_report` calls `verify` per filing, one such row aborts the whole
    batch rather than marking one filing unresolved. That is deliberate for an
    oracle — both shapes mean the row vocabulary moved, so every other verdict
    in the run is suspect too — but it is a stop, not a skip, and a caller
    running 56 filers should expect to lose the run and not one statement.
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
        children = groups.setdefault(line.calculation_parent, {})
        kept = children.get(line.concept)
        if kept is None:
            children[line.concept] = line
        else:
            _refuse_disagreeing_duplicate(kept, line)

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
    tolerance = _rounding_tolerance(parent_line, children.values(), period, len(terms))

    if computed is None or reported is None:
        status, difference = INCOMPLETE, None
    else:
        difference = computed - reported
        if difference == 0:
            status = AGREES
        elif abs(difference) <= tolerance:
            status = WITHIN_ROUNDING
        else:
            status = DISAGREES

    return SumCheck(
        kind=kind,
        period=period,
        parent=parent,
        status=status,
        reported=reported,
        computed=computed,
        difference=difference,
        tolerance=tolerance,
        terms=tuple(terms),
        unsummable_children=tuple(unsummable),
    )


def _rounding_tolerance(parent_line, children, period, n_terms) -> Decimal:
    """How far this group's sum may miss the parent WITHOUT either being wrong.

    XBRL's `decimals` states how precisely each fact was reported, and filers
    round each fact INDEPENDENTLY. Rounding n children and their parent to the
    same place therefore admits an error of half a unit each — (n+1)/2 units at
    the LEAST precise declaration in the group, which is the XBRL 2.1 §5.2.5.2
    calculation-consistency reading. Least precise, not most: a group is only
    as well stated as its coarsest member.

    ZERO WHEN ANY DECLARATION IS MISSING, deliberately fail-closed. A filer who
    declared nothing has claimed nothing, and inventing a precision for them
    would start absorbing real disagreements into silence — strictly worse than
    the overstatement this function removes, because an overstatement is
    visible in the report and an absorbed error is not.

    OBSERVED in the committed capture: 1,016 of 1,065 declarations are -6
    (millions), 34 are 2 (per-share cents), 10 are 0 and 5 are -8. Applying
    this turns 24 of the module's 27 exact-comparison disagreements into
    `within_rounding`, which is the ~8x overstatement the plan's Decision Log
    (Task 4 -> Task 8) requires closed before any resolution rate is reported.

    STATED LIMIT: `decimals` may legally be `INF` (the fact is exact), which is
    NOT observed anywhere in the capture and is treated here as a missing
    declaration — so a group MIXING `INF` with a coarse declaration compares
    exactly rather than at the coarse interval. That is the strict direction,
    and strict here means "may report a rounding residue as a disagreement",
    the very overstatement above. Left unhandled rather than guessed because
    the case is unobserved; the fix is one branch in `_declared_decimals` the
    day a filing shows it.
    """
    declared = [_declared_decimals(line, period) for line in children]
    if parent_line is not None:
        declared.append(_declared_decimals(parent_line, period))
    if not declared or any(value is None for value in declared):
        return Decimal(0)
    return (Decimal(10) ** -min(declared)) * (n_terms + 1) / 2


def _declared_decimals(line, period) -> int | None:
    """The precision the filer declared for this line in this period, or `None`.

    Accepts the integer the reconstruction capture carries and the numeric
    STRING the repo's sibling `companyconcept` lane carries (`"-6"`), because
    the same attribute reaches this repo in both spellings and a silent `None`
    on one of them would quietly restore the exact comparison for a filer who
    did declare a precision. Anything else — absent, empty, `INF`, non-numeric
    — is `None`: no claim was made that this can read.
    """
    value = line.decimals.get(period)
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _refuse_disagreeing_duplicate(kept, dropped) -> None:
    """Raise unless the duplicate row about to be DROPPED says the same thing
    as the one already kept.

    De-duplication keeps the first row of a concept, which is only sound while
    the discarded row agrees with it. In the committed capture the single
    duplicate pair does agree — KO's `CashAndCashEquivalentsAtCarryingValue`
    renders twice, "Balance at beginning of year" and "Balance at end of year",
    with identical values, weight and decimals — but that is one observation,
    not a property of the shape. A pair that disagreed would silently change
    both `computed` and the group's period set with nothing marking that a row
    had been dropped, which is the one thing this module otherwise never does:
    `_weight_of`, `_era` and the unresolved-statement reason codes all refuse
    to resolve an unobserved shape by quietly picking.

    Values are compared as `Decimal`, not as the floats they arrive as, so two
    rows stating one figure are not split by a representation difference.
    """
    if _weight_of(kept) == _weight_of(dropped) and _comparable(kept.values) == _comparable(dropped.values):
        return
    raise ValueError(
        f"{dropped.concept} is presented twice under calculation parent "
        f"{dropped.calculation_parent} ({kept.label!r}, {dropped.label!r}) with "
        f"values/weight that DISAGREE: kept weight={kept.weight!r} "
        f"values={kept.values!r}; dropped weight={dropped.weight!r} "
        f"values={dropped.values!r}. De-duplication keeps the first row, so "
        "one of these figures would vanish from the check; refusing to pick"
    )


def _comparable(values) -> dict:
    """`values` keyed as given, with each value normalised through `_number` so
    two rows are compared as figures rather than as float spellings. An
    unusable value keeps its place as `None`, so a row stating `''` where the
    other states a number still counts as a disagreement."""
    return {period: _number(value) for period, value in values.items()}


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


# =====================================================================
# PER-ERA RESOLUTION RATE (plan Task 8)
# =====================================================================
#
# THE ERAS ARE A MEASUREMENT WINDOW, NOT AN ACCOUNTING EPOCH. The brief's
# structural rule resolved 63 of 65 filers, and that was measured on filings
# FILED 2016-2018 ONLY (brief §"A limit this brief must not overclaim"). A
# 10-year reconstruction spans years nobody sampled, and the brief's own
# expectation is that early years resolve worse: DUK's calculation tree yields
# 2-3 candidate totals for every filing from 2013 through 2017 and resolves
# cleanly only from 2018 — 5 of its 14 years. So the boundaries below are the
# edges of the evidence, and the report exists to stop the sampled window's
# rate being read as the whole decade's.
SAMPLE_FIRST_YEAR = 2016
SAMPLE_LAST_YEAR = 2018

ERA_BEFORE_SAMPLE = "pre_2016"
ERA_SAMPLED = "sampled_2016_2018"
ERA_AFTER_SAMPLE = "post_2018"

# Oldest first, so a reader scans the report the way the years run.
ERA_ORDER = (ERA_BEFORE_SAMPLE, ERA_SAMPLED, ERA_AFTER_SAMPLE)

# WHY EACH UNRESOLVED STATEMENT FAILED. Each is a fact about THIS
# RECONSTRUCTION, never a verdict on the filer — see `resolution_report`. FIVE
# codes, one per DIFFERENT fact, because a reader acts on them differently;
# collapsing any pair would rebuild, one layer up, the undifferentiated blank
# this arc exists to remove.
AMBIGUOUS_TOTAL = "ambiguous_total"
NO_REVENUE_TOTAL = "no_revenue_total"
AMBIGUOUS_STATEMENT_ROLE = "ambiguous_statement_role"
NO_DECLARED_SUMS = "no_declared_sums"
SUMS_DO_NOT_RECONCILE = "sums_do_not_reconcile"

# The wording a revenue concept is NAMED with, matched POSITIVELY against a
# concept's local name — never a denylist of the cost-shaped names that happen
# to contain it
# (docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md).
# It covers every revenue concept the brief measured across sectors:
# `Revenues`, `SalesRevenueGoodsNet`, `SalesRevenueNet`,
# `SalesRevenueServicesNet`, `RegulatedAndUnregulatedOperatingRevenue` (DUK,
# NEE), `RealEstateRevenueNet` (O, PLD), `RevenueMineralSales` (NEM),
# `RevenueFromContractWithCustomerExcludingAssessedTax` (post-ASC-606) and
# `RevenuesAndOtherIncome` (PSX).
_REVENUE_WORDING = "revenue"


@dataclass(frozen=True)
class Unresolved:
    """One reason a statement did not resolve, with enough detail to act on.

    `detail` names the specific roles, groups and periods involved. A reason
    code alone tells a reader that something is wrong and gives them nowhere to
    go; the point of this report is that a reader holding the filing can check
    it.
    """

    reason: str
    detail: str


@dataclass(frozen=True)
class StatementResolution:
    """One filing's one statement, resolved or not.

    `groups_incomplete` is REPORTED BUT NOT DISQUALIFYING, and that is a
    measured judgement rather than a convenience: 9 of the 23 groups in KO's
    FY2017 balance sheet are `incomplete` — a stub period with one child
    tagged, a parent that belongs to another statement — and the brief holds up
    that same filing as the faithful reconstruction (§Decision, "26 real lines
    carrying the company's OWN labels"). A rule that failed a statement for any
    incomplete group would report 0 of 6 statements resolved over the committed
    capture, which tells a reader nothing they can use. The count is carried so
    thin tagging stays VISIBLE instead.
    """

    filing_date: str
    era: str
    kind: str
    resolved: bool
    reasons: tuple[Unresolved, ...]
    groups_checked: int
    groups_incomplete: int


@dataclass(frozen=True)
class EraTally:
    """The counts for one era.

    `reasons` is (code, count) pairs ordered by code, so two runs over one
    input never disagree. THEY DO NOT SUM TO `unresolved`: one statement may
    fail for several reasons at once — a filing with no calculation arcs is
    both `no_declared_sums` and `ambiguous_total` — so the counts total the
    REASONS, not the statements. `resolved` + `unresolved` is the statement
    count; nothing else is.
    """

    era: str
    resolved: int
    unresolved: int
    reasons: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class ResolutionReport:
    """A whole run: every statement, and the per-era counts.

    Both halves are always present. The per-statement list is what a reader
    investigates; the era tallies are the answer to the question the brief says
    must be measured rather than assumed.
    """

    statements: tuple[StatementResolution, ...]
    by_era: tuple[EraTally, ...]


def resolution_report(reconstructions) -> ResolutionReport:
    """How much of a reconstruction run actually came out usable, per era.

    `reconstructions` is an iterable of `(filing_date, statements)` pairs —
    one pair per filing, `filing_date` an ISO date string as
    `sec_edgar_client.list_filings` and the `reconstruct` pack already carry
    it (`filingDate`), `statements` the `Statements` Task 3 assembles. The
    date is taken from the caller because `Statements` does not carry one, and
    inventing a date here from anything else would be this report's opinion of
    when a filing was filed.

    A statement RESOLVES when all of these hold:

      1. NO MORE THAN ONE role classified as its kind, so which statement was
         read was not a choice this code made silently. Worded as the predicate
         actually behaves: a kind present in `by_kind` with NO entry in `roles`
         passes this condition. That is unreachable through Task 3's assembler,
         which writes both together, but it IS reachable through the duck-typed
         input contract this docstring invites, and claiming "exactly one"
         would be a promise the code does not keep;
      2. it declares at least one calculation group, so "nothing disagreed" is
         not vacuously true of a statement whose arithmetic was never read;
      3. every group it declares came out in `RECONCILES` — `agrees` or
         `within_rounding`;
      4. for the INCOME statement only, exactly one revenue total survives
         `revenue_totals` — the count the brief's era limit is written about.

    `incomplete` groups do NOT disqualify it; see `StatementResolution`.

    CONDITION 4 IS INCOME-ONLY, so "resolved" means something weaker for the
    balance sheet and the cash-flow statement: for those two it says the
    declared arithmetic held, and nothing about a total having been identified.
    Stated rather than smoothed over, because a reader counting 5 of 6 resolved
    would otherwise assume the same question was asked of all six.

    WHAT "UNRESOLVED" DOES NOT MEAN — this is the sentence to read before
    quoting any number out of this report. It is NOT a finding that the filer
    is wrong. `SUMS_DO_NOT_RECONCILE` fires on this module's LIMIT 2 as
    readily as on a real filer defect: `verify` sees PRESENTED lines only, so a
    calculation child the filer never puts on the face of the statement leaves
    the sum short, and IBM FY2025's diluted-share group is exactly that — a
    false positive this module structurally cannot separate from a true one
    (measured: 3 of the committed capture's 3 remaining disagreements). The
    plan's Decision Log (Task 4 -> Task 8) makes this binding: `disagrees` may
    not be read as filer defect. The reason code says what the RECONSTRUCTION
    could not do, and the detail names the group so a reader can decide which
    it is.

    PURE, and no I/O: a function of the pairs handed in.
    """
    statements: list[StatementResolution] = []
    for filing_date, assembled in reconstructions:
        era = _era(filing_date)
        checks_by_kind: dict[str, list[SumCheck]] = {}
        for result in verify(assembled):
            checks_by_kind.setdefault(result.kind, []).append(result)
        for kind, lines in assembled.by_kind.items():
            statements.append(_resolution_for(
                filing_date, era, kind, lines,
                assembled.roles.get(kind, ()),
                checks_by_kind.get(kind, []),
            ))
    return ResolutionReport(
        statements=tuple(statements),
        by_era=_tallies(statements),
    )


def revenue_totals(lines) -> tuple[str, ...]:
    """The income statement's candidate TOTAL revenue concepts, in
    presentation order.

    THE ARC'S STRUCTURAL RULE, applied to the income calculation tree: among
    the tree's revenue concepts, a candidate is one whose calculation parent is
    not itself a revenue concept — so a filer's revenue COMPONENTS, which roll
    up into a revenue parent, drop out and the line they roll into survives.
    Exactly one survivor is the filing's own total. Two or three is the
    ambiguity DUK exhibits before 2018 and the brief's era limit is written
    about; zero is a different fact (see `NO_REVENUE_TOTAL`).

    A DEDUCTION IS EXCLUDED BY THE FILER'S OWN SIGN, not by a list of
    cost-shaped names. IBM FY2025 presents `us-gaap_CostOfRevenue` as a SIBLING
    of `us-gaap_Revenues` under `GrossProfit`, and its local name carries the
    revenue wording too — what separates them is that the filer declares one
    +1.0 and the other -1.0. Matching the name alone reads IBM as two
    candidates and reports a clean filing as ambiguous; the sign is structural
    and stays correct for a cost concept nobody thought to list
    (docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md).

    THE PARENT IS TESTED BY NAME ONLY, deliberately: a filer's revenue parent
    need not be a PRESENTED line (its own weight is then unavailable), and a
    component that rolls into an unpresented revenue total must still drop out.

    AN UNPARENTED REVENUE LINE IS A CANDIDATE, and that is a DECISION, not an
    accident of `_names_revenue(None)` being false. A filer's total commonly
    TOPS the calculation tree and so has no calculation parent — the brief's
    PSX declares its own `RevenuesAndOtherIncome` (104,622M) — and excluding
    unparented lines would drop that total, leave zero candidates and report
    `NO_REVENUE_TOTAL` on a filing whose total is on the face of the statement.
    Its COST, stated in the same breath: a filer presenting several revenue
    lines with no calculation arcs between them yields one candidate each and
    is reported ambiguous. That is the correct answer — with no arc declaring
    one the parent of the others, the structure does not say which is the
    total, and the plan forbids picking one — but it is a cost, and
    `test_disaggregated_revenue_with_no_calculation_arcs_is_reported_ambiguous`
    pins it so nobody meets it as a surprise.

    ONE CANDIDATE PER CONCEPT. The presentation may render one fact on two rows
    (KO shows `CashAndCashEquivalentsAtCarryingValue` twice on its cash-flow
    statement), and `_checks_for_statement` already de-duplicates for the same
    reason; a repeated revenue row would otherwise report a filing as ambiguous
    between its total and itself. Unobserved on an income role — a guard, not a
    fix — and taken so the two functions in this module cannot disagree about
    whether a repeated row is one fact.

    ORDER IS PRESENTATION ORDER, so two runs over one filing never disagree.
    """
    candidates = []
    for line in lines:
        if not _is_revenue_line(line) or _names_revenue(line.calculation_parent):
            continue
        if line.concept not in candidates:
            candidates.append(line.concept)
    return tuple(candidates)


def _is_revenue_line(line) -> bool:
    """A line stating revenue: its concept carries the revenue wording, and
    neither the taxonomy nor the filer calls it a deduction.

    TWO INDEPENDENT EXCLUSIONS, because neither alone is enough and the case
    that proves it is `us-gaap_CostOfRevenue`, whose local name carries the
    revenue wording:

      * THE TAXONOMY'S `balance`. A cost concept is `debit`, a revenue concept
        `credit` — the taxonomy's own answer, independent of presentation and
        of the filer's weight choices. OBSERVED: IBM's `Revenues` is `credit`
        and its `CostOfRevenue` `debit`.
      * THE FILER'S OWN SIGN. A line the filer subtracts is a deduction
        whatever the taxonomy says, which also covers a filer's CUSTOM cost
        concept — custom concepts commonly carry no balance at all.

    `balance is None` IS NOT A REJECTION, deliberately fail-open: 349 of the
    455 captured rows carry none, and requiring `credit` would discard a
    filer's own custom revenue concept — precisely what this design promises
    not to lose (brief §Decision, `ko_UnusualOrInfrequentItemOperating`).

    WHY BOTH ARE LOAD-BEARING, measured rather than assumed: IBM subtracts
    `CostOfRevenue` directly (-1.0), so the sign alone excludes it there. But
    where a cost line instead rolls POSITIVELY into a costs subtotal — the
    oil-major shape, `CostOfRevenue` +1.0 into `CostsAndExpenses` — the sign
    says nothing and only `balance` excludes it. That path was found by writing
    the PSX test, not by reading the code.

    NO FALSE-EXCLUSION PATH, settled independently by this task's quality
    reviewer and Task 7's and recorded here so it is not re-litigated: a
    contra-revenue line rolls into a revenue-NAMED parent, so the parent clause
    in `revenue_totals` drops it before either signal here is consulted; where
    its parent is not revenue-named it is a deduction and never the top line.
    """
    weight = _number(line.weight)
    if not _names_revenue(line.concept):
        return False
    if str(line.balance or "").casefold() == "debit":
        return False
    return not (weight is not None and weight < 0)


def _names_revenue(concept) -> bool:
    """Does this concept's LOCAL name carry the revenue wording?

    The namespace is dropped first: a filer's own prefix (`duk_`, `ko_`) says
    nothing about what the concept states, and a filer whose ticker or domain
    contained the wording would otherwise turn every one of its lines into a
    revenue line.
    """
    if not concept:
        return False
    return _REVENUE_WORDING in str(concept).split("_", 1)[-1].casefold()


def _resolution_for(
    filing_date, era, kind, lines, roles, checks,
) -> StatementResolution:
    reasons: list[Unresolved] = []

    if len(roles) > 1:
        # ASSEMBLY PICKED ONE to read (deterministically, preferring the purer
        # role) and that pick is not a resolution: which role is the filer's
        # statement was decided by our tie-break, not by the filing. Reporting
        # the read one as resolved would launder the choice into a fact. It is
        # a DIFFERENT fact from an ambiguous revenue total — a statement can
        # have either without the other — so it carries its own code.
        reasons.append(Unresolved(
            AMBIGUOUS_STATEMENT_ROLE,
            f"{len(roles)} roles classify as {kind} and only the first was "
            f"read: {', '.join(roles)}",
        ))

    if kind == "income":
        tops = revenue_totals(lines)
        if len(tops) != 1:
            reasons.append(Unresolved(
                AMBIGUOUS_TOTAL if tops else NO_REVENUE_TOTAL,
                f"{len(tops)} candidate totals among the income statement's "
                f"revenue concepts"
                + (f": {', '.join(tops)}" if tops else
                   " — no line states revenue, so this reconstruction cannot "
                   "name the filer's top line"),
            ))

    if not checks:
        reasons.append(Unresolved(
            NO_DECLARED_SUMS,
            f"the {kind} statement declares no calculation group, so no "
            "declared arithmetic was checked",
        ))

    broken = [result for result in checks if result.status == DISAGREES]
    if broken:
        reasons.append(Unresolved(
            SUMS_DO_NOT_RECONCILE,
            "; ".join(
                f"{result.parent} in {result.period}: the filer reports "
                f"{result.reported} and its own declaration produces "
                f"{result.computed} (difference {result.difference}, beyond "
                f"the {result.tolerance} its declared precision permits)"
                for result in broken
            ),
        ))

    return StatementResolution(
        filing_date=filing_date,
        era=era,
        kind=kind,
        resolved=not reasons,
        reasons=tuple(reasons),
        groups_checked=len(checks),
        groups_incomplete=sum(
            1 for result in checks if result.status == INCOMPLETE
        ),
    )


def _tallies(statements) -> tuple[EraTally, ...]:
    """One tally per era PRESENT in the run, oldest first.

    Eras with no filings are left out rather than emitted as zeroes: a run of
    eight modern 10-Ks has nothing to say about 2013, and a row of zeroes reads
    as a measurement that was made and came out empty.
    """
    tallies = []
    for era in ERA_ORDER:
        rows = [s for s in statements if s.era == era]
        if not rows:
            continue
        reasons: dict[str, int] = {}
        for row in rows:
            for entry in row.reasons:
                reasons[entry.reason] = reasons.get(entry.reason, 0) + 1
        tallies.append(EraTally(
            era=era,
            resolved=sum(1 for row in rows if row.resolved),
            unresolved=sum(1 for row in rows if not row.resolved),
            reasons=tuple(sorted(reasons.items())),
        ))
    return tuple(tallies)


def _era(filing_date) -> str:
    """Which measurement era a filing date falls in, or a loud failure.

    REFUSES rather than defaulting. The era split is this report's entire
    purpose, so a filing that cannot be placed in one must not be silently
    bucketed: dropping it overstates the rate of the era it belonged to, and a
    catch-all era understates another's. Same posture as `_weight_of` above,
    for the same reason.
    """
    year = str(filing_date)[:4]
    if not year.isdigit():
        raise ValueError(
            f"filing date {filing_date!r} carries no readable four-digit year, "
            "so this filing cannot be placed in an era; refusing to guess one"
        )
    year = int(year)
    if year < SAMPLE_FIRST_YEAR:
        return ERA_BEFORE_SAMPLE
    if year <= SAMPLE_LAST_YEAR:
        return ERA_SAMPLED
    return ERA_AFTER_SAMPLE
