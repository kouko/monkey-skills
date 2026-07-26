#!/usr/bin/env python3
"""kpi_us_statement_series.py — join N filings of ONE company into a
multi-year series keyed on the FILER'S OWN CONCEPT (plan Task 6,
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md).

A 10-K carries three comparative years for income and cash flow and two for
the balance sheet, so ~4 filings cover a decade — but only if the filings can
be joined, and the join needs an identity for "the same line, a year later".

THE IDENTITY IS THE CONCEPT. Measured over 14 filings each for three filers
chosen to span the failure modes (brief §"Series identity across a decade"):
KO changed concept ONCE in 2013-2026 (2019, ASC 606:
`SalesRevenueGoodsNet` -> `Revenues`), DUK never, IBM never. Zero or one
transition per decade makes the concept a near-stable key and makes each
transition an ENUMERABLE EVENT rather than a per-period inference.

THE IDENTITY IS NEVER THE LABEL. Over those same 14 years IBM's revenue label
moved `Total revenue` -> `Total revenue (Note T)` -> `Revenue (Note O)` ->
`Revenue (Note C)` -> `Revenue (Note D)` -> `Revenue`, because it embeds a
note cross-reference that renumbers whenever the notes are reordered. Keying
on it turns one 14-year series into six fragments. Labels ride along on
`ConceptSeries.labels` and on each point, for DISPLAY, and nothing here keys
on them (`Line.label` says the same at its own site).

A TRANSITION IS RECORDED, NEVER RESOLVED. When a filer re-tags a line, this
emits a `ConceptTransition` carrying BOTH concepts and BOTH values, each
naming the vintage it came from, and LEAVES BOTH SERIES STANDING. It never
merges them (which would destroy the evidence that anything changed) and it
never pairs concepts by position or by label — a decade yields a handful of
these, and a handful is reviewable. Where a period shows several departures
and several arrivals at once, ALL of them ride on the one event rather than
being paired 1-to-1 on a guess: the ambiguity is the reader's to adjudicate,
and inventing a pairing is how a silent merge gets in.

WHAT MAKES A TRANSITION VISIBLE is vintage overlap, which is structural: two
filings report the same period, and the newer one tags a concept for it that
the older one did not while dropping one the older one had. Nothing here reads
a line's POSITION or its label to decide identity (brief §Decision) — position
was measured unreliable for meaning, and the label is the thing this module
exists to not trust.

WHAT THAT RULE CANNOT SEE, stated here because a silent miss is worse than a
known one. It reads a re-tag as a SUBSTITUTION INSIDE ONE SHARED PERIOD, so a
filer that phases the change in across two filings never presents one and the
re-tag goes unrecorded. Both shapes are real, and both are how ASC 606 was
adopted — the same standard KO's measured transition came from:

  * MODIFIED-RETROSPECTIVE ADOPTION — the new concept is tagged for the
    adoption year only and the comparatives stay under the old one, so every
    SHARED period reads `{A} -> {A}`. No event.
  * DUAL TAGGING IN THE TRANSITION YEAR — `{A} -> {A, B}` on the shared
    period: an arrival with no departure, which the rule declines by design.

In both, `by_concept` still shows two series that ABUT rather than overlap;
what is missing is the event explaining why. Both are pinned at their current
no-event behaviour (`test_a_modified_retrospective_adoption_records_no_event`,
`test_dual_tagging_in_the_transition_year_records_no_event`) so lifting the
limit forces those tests to change. The INVERSE also holds: an unrelated line
dropped and an unrelated line added in one period pair is shape-identical to a
re-tag and IS recorded — which is why an event is a candidate for review
carrying both sides, never a verdict that one concept became the other.

OVERLAPPING VINTAGES RESOLVE BY THE STORE'S EXISTING POLICY, not a second one:
NEWEST-FILED wins, on the pair `(as_of, accession)` — `as_of` orders,
the accession breaks a same-day tie deterministically. That is
`kpi_spine_view._identity_vintage` (kpi_spine_view.py:496-522) over
`_vintage_key` (:443-464), which is the same max-on-`as_of` rule as
`kpi_store.query_latest` (kpi_store.py:433-440). It is not imported: those
functions read STORE OBSERVATION dicts and a filing is not one, so calling
them would couple this module to a payload shape it never handles. The rule is
instead pinned by conformance —
`test_the_newest_filed_rule_agrees_with_the_store` runs the store's own
`_identity_vintage` on the equivalent observations and fails if the two ever
disagree, which a private copy would not.

WHAT IS AND IS NOT PROVEN ON REAL ROWS. The two measured facts above come from
14 filings per filer; this module's own suite does NOT read 14 filings, because
the committed Task 3 capture holds rows for exactly ONE filing per filer and
this task adds no capture. So the KO transition is proven on a fixture DERIVED
from KO's real FY2017 rows (real concepts, real labels, real amounts, one
concept re-tagged and the comparative window moved), and the IBM label churn on
constructed rows carrying the six OBSERVED labels. What that leaves untested is
the frequency question — how often a real filing pair moves more than one
concept at once — and the first live run over a decade is where that gets
measured. It is stated here rather than left for a reader to discover, because
this module's whole value proposition is a claim about real filings.

The same gap governs the two blind spots above: WHICH transition method a
filer used is not in this arc's measurements. KO's re-tag is recorded as one
concept change in 2013-2026, not as a shape, so whether the detector would
have caught the real KO event — rather than the fixture built from KO's real
rows — is open until a live decade is run. Both blind spots are therefore
DOCUMENTED AND PINNED, not measured as rare.

NO ARITHMETIC HAPPENS HERE. This module SELECTS values; it never adds,
scales or normalises one, so a value it emits is the object the filing
supplied — including a `Decimal`, which any float round-trip would corrupt
(docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md, "binary
float is the same shape": `1.005 x 1e9` in binary float already manufactured a
false restatement in this module family). That is a claim about behaviour, so
it is TESTED with a float-hostile value rather than asserted here.

IMPURE ONLY WHERE TASK 3 IS. `series_for` reads each filing exactly as
`kpi_us_statement_shape.statements_for` does and holds no cache and no state
(plan ## Notes kickoff decision — the reconstruction is RECOMPUTED, never
persisted), so it stays a pure function of (filings, this repo's derivation)
and can be wrapped in a cache later without touching a caller.

WHY `series_for(filings)` AND NOT `series_for(accessions)`. The plan names the
input by what identifies it; an accession STRING can only become a statement
by a network fetch, which would put an acquirer inside a pure function and
make this suite unrunnable offline. Resolving accession -> Filing is already
owned by `sec_edgar_client._acquire_raw_filing`, and Task 3 already takes the
filing itself. So the caller resolves, and this joins. Recorded here rather
than silently, because it is a deviation from the plan's literal signature.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

# Sibling import, mirroring `kpi_us_statement_shape.py`'s shim so the module
# resolves both under `uv run --script` and under importlib test loading.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import kpi_us_statement_shape as statement_shape  # noqa: E402

# One filing on the store's vintage axis: `(as_of, accession)`.
Vintage = tuple[str, str]


@dataclass(frozen=True)
class SeriesPoint:
    """One period of one series, as ONE filing reported it.

    `vintage` is not decoration: it is which filing this number came from, and
    without it the newest-filed choice is implicit and unauditable. `label` is
    that filing's own prose for the line — display only, and it may differ from
    the label of the neighbouring point.
    """

    period: str
    value: Any
    label: str
    vintage: Vintage


@dataclass(frozen=True)
class ConceptSeries:
    """One statement line followed across filings, keyed on `(kind, concept)`.

    `labels` is every distinct label the filer used for this concept, in
    vintage order — six of them for IBM's revenue over 14 years. It is a
    DISPLAY record of the churn, never an identity.

    `points` is one point per period, oldest first, each from the newest filing
    that reported that period. A concept the filer RENDERS but tags no amount
    for produces no point (and, with no points anywhere, no series): typing
    that empty cell is Task 5's job, not this module's.
    """

    kind: str
    concept: str
    labels: tuple[str, ...]
    points: tuple[SeriesPoint, ...]


@dataclass(frozen=True)
class TransitionValue:
    """One side of one period of a transition: what a given filing reported
    for a given concept, with its own provenance. Both sides are always
    present, so the event can be adjudicated without re-reading the filings."""

    period: str
    concept: str
    value: Any
    vintage: Vintage


@dataclass(frozen=True)
class ConceptTransition:
    """A re-tagging, recorded for review — never resolved.

    Two filings overlap on one or more periods; across those periods the older
    tags concepts (`gone`) the newer does not, and the newer tags concepts
    (`arrived`) the older did not. `values` carries both sides for every
    affected period, oldest period first and departures before arrivals, so
    the event reads FROM -> TO.

    ONE EVENT PER VINTAGE PAIR PER STATEMENT, not one per period: KO's 2019
    re-tag shows up on every period the two filings share, and reporting it
    once per period would turn one decision into several and invite a reader
    to treat them as unrelated. `len(gone) == len(arrived) == 1` is the
    unambiguous case; longer tuples mean the filing pair changed several lines
    at once and this module is declining to guess which became which.

    HOW OFTEN EACH SHAPE OCCURS IS NOT MEASURED. What was measured is the
    number of CONCEPT CHANGES per decade (1 / 0 / 0 for KO / DUK / IBM); how
    many concepts move in the SAME filing pair was not, and this detector has
    never been run over a real 14-filing set (see the module docstring's
    ground-truth note). One-to-one is the case the arc has evidence for, not a
    frequency claim.
    """

    kind: str
    from_vintage: Vintage
    to_vintage: Vintage
    gone: tuple[str, ...]
    arrived: tuple[str, ...]
    values: tuple[TransitionValue, ...]


@dataclass(frozen=True)
class Series:
    """One company's statements across N filings.

    `by_concept` is keyed `(kind, concept)` — the same concept can legitimately
    appear in two statements — and is ordered by that key, so two runs over one
    set of filings never disagree.

    `transitions` is empty for a filer that never re-tagged, which is the
    measured majority (DUK and IBM over 14 years each).

    `vintages` is every filing read, oldest first, so a reader can tell an
    absent period from an unread filing.
    """

    by_concept: dict[tuple[str, str], ConceptSeries]
    transitions: tuple[ConceptTransition, ...]
    vintages: tuple[Vintage, ...]


@dataclass(frozen=True)
class _Amount:
    """One tagged amount, flattened out of one filing's statements — the single
    intermediate both the series and the transitions are derived from, so the
    two can never disagree about what a filing tagged."""

    vintage: Vintage
    kind: str
    concept: str
    period: str
    value: Any
    label: str


def series_for(filings: Iterable[Any]) -> Series:
    """Join these filings of ONE company into concept-keyed series.

    Each filing need only answer `.xbrl()` (Task 3's whole input contract),
    `.accession_no` and `.filing_date`. Filings may arrive in any order: they
    are sorted onto the vintage axis here, so the answer is a property of the
    filings and never of the argument order.
    """
    read = sorted(
        ((_vintage(filing), statement_shape.statements_for(filing))
         for filing in filings),
        key=lambda pair: pair[0],
    )
    amounts = _tagged_amounts(read)
    vintages = tuple(vintage for vintage, _ in read)
    return Series(
        by_concept=_series_by_concept(amounts, _labels_by_concept(read)),
        transitions=_transitions(vintages, amounts),
        vintages=vintages,
    )


def _vintage(filing: Any) -> Vintage:
    """This filing on the store's vintage axis: `(as_of, accession)`.

    `filing_date` is a `datetime.date` on the live surface, not a string
    (sec_edgar_client.py:865), so it is stringified to ISO the same way the
    Task 3 capture does (capture_us_statement_reconstruction.py:223) — ISO
    strings compare chronologically, which is what the store's `as_of`
    ordering already relies on.

    A missing half RAISES rather than reading as `""` the way the store
    tolerates for a hand-fed payload: `""` sorts oldest, so a real filing with
    no readable date would silently lose every newest-filed contest and its
    numbers would vanish from the series without a word.
    """
    as_of = getattr(filing, "filing_date", None)
    accession = getattr(filing, "accession_no", None)
    if not as_of or not accession:
        raise ValueError(
            "kpi_us_statement_series: a filing has no vintage — filing_date="
            f"{as_of!r}, accession_no={accession!r}; both are required to "
            "place it on the store's (as_of, accession) axis"
        )
    return (str(as_of), str(accession))


def _labels_by_concept(read: list) -> dict[tuple[str, str], tuple[str, ...]]:
    """Every distinct label each `(kind, concept)` was rendered under, in
    vintage then presentation order.

    Collected from the LINES rather than from the amounts, because a label
    belongs to a line and not to a period: KO's cash-flow statement puts one
    concept on two rows (opening and closing balance) carrying the same four
    instants, and both of its labels are real.
    """
    labels: dict[tuple[str, str], list[str]] = {}
    for _vintage_key, statements in read:
        for kind, lines in statements.by_kind.items():
            for line in lines:
                seen = labels.setdefault((kind, line.concept), [])
                if line.label not in seen:
                    seen.append(line.label)
    return {key: tuple(value) for key, value in labels.items()}


def _tagged_amounts(read: list) -> tuple[_Amount, ...]:
    """Every amount these filings tag, flattened, in vintage order.

    A period whose value is `None` is NOT tagged in that filing and produces
    nothing here — which is what makes "the concepts this filing tags for this
    period" a meaningful set for transition detection. Distinguishing the KINDS
    of empty is Task 5's job; this only needs to know that no amount was
    reported.

    ONE VINTAGE MAY NOT TAG TWO AMOUNTS FOR ONE (concept, period). Where it
    does, this raises: choosing between them would be this module resolving a
    contradiction in silence, and the observed real case (one concept on two
    rows) always agrees, so the agreeing case is kept as one amount and the
    disagreeing one is news.
    """
    amounts: list[_Amount] = []
    seen: dict[tuple[Vintage, str, str, str], Any] = {}
    for vintage, statements in read:
        for kind, lines in statements.by_kind.items():
            for line in lines:
                for period, value in line.values.items():
                    if value is None:
                        continue
                    # LOOM-SIMPLIFY: the period key is matched VERBATIM across
                    # filings | ceiling: a 52/53-week filer, whose fiscal
                    # year-end moves a day between filings, so one real period
                    # reads as two | upgrade: the store's own
                    # `kpi_store.same_period` / `_snap_month_end` / `_qtrs`,
                    # which exist for exactly this and already back
                    # `period_axis_key` | ref: plan Task 6 (its acceptance is
                    # KO/IBM, both calendar-year filers) — pinned by
                    # `test_a_period_key_is_matched_verbatim_across_vintages`
                    key = (vintage, kind, line.concept, period)
                    if key in seen:
                        if seen[key] != value:
                            raise ValueError(
                                "kpi_us_statement_series: filing "
                                f"{vintage[1]} tags two amounts for "
                                f"{line.concept} in {period} ({kind}): "
                                f"{seen[key]!r} and {value!r}"
                            )
                        continue
                    seen[key] = value
                    amounts.append(_Amount(
                        vintage=vintage, kind=kind, concept=line.concept,
                        period=period, value=value, label=line.label,
                    ))
    return tuple(amounts)


def _series_by_concept(
    amounts: tuple[_Amount, ...],
    labels: dict[tuple[str, str], tuple[str, ...]],
) -> dict[tuple[str, str], ConceptSeries]:
    """The amounts folded onto `(kind, concept)` — THE KEY — one point per
    period, from the newest filing that reported it."""
    grouped: dict[tuple[str, str], dict[str, _Amount]] = {}
    for amount in amounts:
        best = grouped.setdefault((amount.kind, amount.concept), {})
        current = best.get(amount.period)
        if current is None or amount.vintage > current.vintage:
            best[amount.period] = amount

    return {
        key: ConceptSeries(
            kind=key[0],
            concept=key[1],
            labels=labels.get(key, ()),
            points=tuple(
                SeriesPoint(
                    period=amount.period, value=amount.value,
                    label=amount.label, vintage=amount.vintage,
                )
                for _period, amount in sorted(grouped[key].items())
            ),
        )
        for key in sorted(grouped)
    }


def _transitions(
    vintages: tuple[Vintage, ...], amounts: tuple[_Amount, ...],
) -> tuple[ConceptTransition, ...]:
    """Each re-tagging between two ADJACENT vintages, as one event per
    statement.

    Adjacent, because that is where a re-tagging is visible: consecutive 10-Ks
    of one filer overlap by two years, and comparing every pair instead would
    report the same event once per pair. A pair sharing no period yields
    nothing, which is honest — nothing about identity is observable there.
    """
    tagged = _tagged_by_period(amounts)
    events: list[ConceptTransition] = []
    for older, newer in zip(vintages, vintages[1:]):
        kinds = {kind for vintage, kind in tagged if vintage == older}
        kinds &= {kind for vintage, kind in tagged if vintage == newer}
        for kind in sorted(kinds):
            event = _transition(
                kind, older, newer, tagged[(older, kind)], tagged[(newer, kind)],
            )
            if event is not None:
                events.append(event)
    return tuple(events)


def _tagged_by_period(
    amounts: tuple[_Amount, ...],
) -> dict[tuple[Vintage, str], dict[str, dict[str, Any]]]:
    """`(vintage, kind) -> period -> concept -> value` — what each filing
    tagged, which is the only thing transition detection reads."""
    index: dict[tuple[Vintage, str], dict[str, dict[str, Any]]] = {}
    for amount in amounts:
        periods = index.setdefault((amount.vintage, amount.kind), {})
        periods.setdefault(amount.period, {})[amount.concept] = amount.value
    return index


def _transition(
    kind: str,
    older: Vintage,
    newer: Vintage,
    older_periods: dict[str, dict[str, Any]],
    newer_periods: dict[str, dict[str, Any]],
) -> ConceptTransition | None:
    """The one event for this statement across this vintage pair, or None.

    A period counts only when it shows BOTH a departure and an arrival. A
    departure alone is a line the filer stopped reporting and an arrival alone
    is one it started — ordinary, and reporting them as transitions would bury
    the handful of real re-taggings under every routine statement edit. That
    asymmetry is the discriminating power here: KO's two filings differ in ONE
    concept out of 26 income lines and yield ONE event.

    IT IS A FILTER, AND A FILTER HAS TWO ERROR DIRECTIONS. Both are real and
    neither is hypothetical (module docstring, "WHAT THAT RULE CANNOT SEE"):

      MISSES a re-tag phased in across two filings, because no shared period
        shows the substitution — `{A} -> {A}` under modified-retrospective
        adoption, `{A} -> {A, B}` under dual tagging in the transition year.
        Both are ASC 606 shapes. Both are pinned at their current no-event
        behaviour by name in the test module.
      ADMITS an unrelated drop plus an unrelated add in one period pair, which
        is shape-identical to a re-tag. Kept: an event carries both concepts
        and both values for a REVIEWER, and suppressing this would need a
        similarity judgement between concepts that nothing here can ground.

    So "no transition recorded" means "no substitution was visible in a shared
    period", NOT "the filer did not re-tag" — the two abutting series are still
    in `by_concept` either way.
    """
    gone: set[str] = set()
    arrived: set[str] = set()
    values: list[TransitionValue] = []
    for period in sorted(set(older_periods) & set(newer_periods)):
        before, after = older_periods[period], newer_periods[period]
        period_gone = sorted(set(before) - set(after))
        period_arrived = sorted(set(after) - set(before))
        if not (period_gone and period_arrived):
            continue
        gone.update(period_gone)
        arrived.update(period_arrived)
        values.extend(
            TransitionValue(period, concept, before[concept], older)
            for concept in period_gone
        )
        values.extend(
            TransitionValue(period, concept, after[concept], newer)
            for concept in period_arrived
        )

    if not values:
        return None
    return ConceptTransition(
        kind=kind, from_vintage=older, to_vintage=newer,
        gone=tuple(sorted(gone)), arrived=tuple(sorted(arrived)),
        values=tuple(values),
    )
