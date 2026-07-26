"""Tests for analysis-kpi/scripts/kpi_us_statement_series.py — joining N
filings of ONE company into a multi-year series keyed on the FILER'S OWN
CONCEPT (plan Task 6,
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md).

THE TWO MEASURED FACTS this suite exists to hold (brief §"Series identity
across a decade — concept, never label", measured over 14 filings each for
KO / DUK / IBM on 2026-07-26):

  * the filer's own CONCEPT is a near-stable series key — 0-1 transitions per
    decade, so a transition is an enumerable EVENT, not a per-period inference;
  * the filer's own LABEL is NOT a key — IBM held one concept for 14 years
    while its label moved six times, because it embeds a note cross-reference
    that renumbers.

FIXTURE PROVENANCE, stated per fixture and never in bulk:

  COMMITTED — read from tests/data/fixtures/us_statement_reconstruction_
      2026-07-26.json, the Task 3 capture. Real rows of real filings.
  OBSERVED — a fact measured live on 2026-07-26 and recorded in the brief's
      table (IBM's six revenue labels over one unchanged concept; KO's single
      2019 concept transition `SalesRevenueGoodsNet` -> `Revenues`). The rows
      carrying such a fact here are constructed; the concepts and labels in
      them are transcribed, not invented.
  CONSTRUCTED-FROM-COMMITTED — rows derived from the committed capture by a
      transformation named at its own site.
  CONSTRUCTED-CONVENTIONAL — written to shape, exercising a rule no captured
      filing exercises.

WHY NO NEW CAPTURE. The multi-vintage case needs 6-14 filings PER FILER; the
committed capture holds rows for exactly one KO filing and one IBM filing, and
this task's `Files touched` is two files — adding a capture is not in it, and
the suite must run offline either way. So the multi-vintage fixtures are
constructed, and every one of them states which of its parts is a measured
fact and which is scaffolding. A fixture whose values were invented is never
what an assertion turns on.

No `@req` tags: this dispatch carries no registered loom-spec REQ-ids (the
work is tracked by named plan Task 6), so `@req` is omitted per the
implementer contract — the same convention as the Task 2/3 suite beside this
one.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import date
from decimal import Decimal

import pytest
from conftest import SKILLS

SERIES_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_series.py"
SPINE_VIEW_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_spine_view.py"
RECONSTRUCTION_CAPTURE = (
    SKILLS.parent / "tests" / "data" / "fixtures"
    / "us_statement_reconstruction_2026-07-26.json"
)


def _load(name: str, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def series():
    return _load("kpi_us_statement_series_test", SERIES_SCRIPT)


@pytest.fixture(scope="module")
def spine_view():
    """The module that owns the store's newest-filed vintage rule
    (`_identity_vintage`), loaded so this suite can check agreement with it
    rather than restate it."""
    return _load("kpi_spine_view_series_test", SPINE_VIEW_SCRIPT)


@pytest.fixture(scope="module")
def capture():
    return json.loads(RECONSTRUCTION_CAPTURE.read_text(encoding="utf-8"))


# --- the filing double ------------------------------------------------------


class _XBRL:
    """The two-attribute slice of `edgar.xbrl.XBRL` that assembly reads —
    mirroring the Task 3 suite's double, because assembly's input contract is
    what it is regardless of who calls it. `get_statement` raises `KeyError`
    for a role whose rows are absent, so a selection regression is loud."""

    def __init__(self, rows_by_role: dict, presentation_roles=None):
        self._rows_by_role = dict(rows_by_role)
        self.presentation_roles = list(
            rows_by_role if presentation_roles is None else presentation_roles
        )

    def get_statement(self, role: str) -> list:
        return self._rows_by_role[role]


class _Filing:
    """The three-member slice of `edgar.Filing` the series reads: `.xbrl()`
    (Task 3's whole input contract) plus `.accession_no` and `.filing_date`,
    which together are the vintage.

    `filing_date` is a `datetime.date` on the live surface, NOT a string —
    documented at sec_edgar_client.py:865 and the reason the Task 3 capture
    stores `str(filing.filing_date)` (capture_us_statement_reconstruction.py
    :223). One fixture below hands over a real `date` for exactly that reason.
    """

    def __init__(self, accession, filing_date, rows_by_role, presentation_roles=None):
        self.accession_no = accession
        self.filing_date = filing_date
        self._xbrl = _XBRL(rows_by_role, presentation_roles)

    def xbrl(self):
        return self._xbrl


def _captured_filing(capture, accession: str) -> dict:
    for filing in capture["filings"]:
        if filing["accession"] == accession:
            return filing
    raise AssertionError(f"accession {accession} is not in the capture")


def _rows_by_role(filing_entry: dict) -> dict:
    return {
        entry["role"]: entry["rows"]
        for entry in filing_entry["roles_captured"]
        if entry.get("rows") is not None
    }


# --- the RED: label churn must not split a series ---------------------------

# OBSERVED 2026-07-26 (brief §Series identity): IBM's revenue label over its
# 2013-2026 10-Ks, in order. The concept underneath never moved.
_IBM_REVENUE_LABELS = (
    "Total revenue",
    "Total revenue (Note T)",
    "Revenue (Note O)",
    "Revenue (Note C)",
    "Revenue (Note D)",
    "Revenue",
)
# COMMITTED: the concept and role IBM's income statement actually carries, read
# from the capture's IBM filing 0000051143-26-000010.
_IBM_REVENUE_CONCEPT = "us-gaap_Revenues"
_IBM_INCOME_ROLE = "http://www.ibm.com/role/CONSOLIDATEDINCOMESTATEMENT"
# CONSTRUCTED: six filing years, each 10-K carrying three comparative years, so
# EVERY adjacent pair of vintages overlaps by one period and is therefore
# actually compared. Placement is scaffolding; the label sequence above is not.
_IBM_FILING_YEARS = (2013, 2015, 2017, 2019, 2021, 2023)


def _duration(year: int) -> str:
    """A calendar-year duration period key in the shape edgartools emits —
    COMMITTED: `duration_2017-01-01_2017-12-31` is verbatim from the capture's
    KO income rows."""
    return f"duration_{year}-01-01_{year}-12-31"


def _line_row(concept: str, label: str, values: dict) -> dict:
    """A presentation row carrying only the keys assembly reads.
    CONSTRUCTED-CONVENTIONAL scaffolding; the concept, label and values a test
    asserts on are supplied by the caller and marked at the call site."""
    return {
        "concept": concept,
        "label": label,
        "level": 4,
        "weight": 1.0,
        "calculation_parent": "us-gaap_GrossProfit",
        "is_abstract": False,
        "values": dict(values),
    }


def _ibm_filings() -> list:
    filings = []
    for index, (filed_year, label) in enumerate(
        zip(_IBM_FILING_YEARS, _IBM_REVENUE_LABELS)
    ):
        values = {
            _duration(year): 60_000_000_000.0 + index
            for year in range(filed_year - 3, filed_year)
        }
        filings.append(_Filing(
            f"0000051143-{filed_year % 100:02d}-00000{index}",
            f"{filed_year}-02-24",
            {_IBM_INCOME_ROLE: [_line_row(_IBM_REVENUE_CONCEPT, label, values)]},
        ))
    return filings


def test_label_churn_does_not_split_a_series(series):
    """THE PLAN'S RED. IBM held ONE concept for 14 years while its label moved
    `Total revenue` -> `Total revenue (Note T)` -> `Revenue (Note O)` ->
    `Revenue (Note C)` -> `Revenue (Note D)` -> `Revenue`, because the label
    embeds a note cross-reference that RENUMBERS every time the notes are
    reordered. A label-keyed join reads that as six unrelated revenue series
    and hands the reader six one-to-three-year fragments instead of a decade.

    So: ONE series, keyed on the concept; the six labels ride along as display
    data; and no concept transition is recorded, because none happened — the
    label moving is not an event.
    """
    joined = series.series_for(_ibm_filings())

    assert list(joined.by_concept) == [("income", _IBM_REVENUE_CONCEPT)], (
        "label churn split the series: expected one concept-keyed series, got "
        f"{sorted(joined.by_concept)}"
    )

    revenue = joined.by_concept[("income", _IBM_REVENUE_CONCEPT)]
    assert revenue.labels == _IBM_REVENUE_LABELS
    assert joined.transitions == (), (
        "a label change is not a concept transition and must not be recorded "
        f"as one: {joined.transitions}"
    )

    # 2010-2022: six 10-Ks x three comparative years, overlapping — the decade
    # the join exists to produce.
    periods = [point.period for point in revenue.points]
    assert periods == [_duration(year) for year in range(2010, 2023)]


# --- the GREEN: KO's one concept transition is one recorded event ------------

_KO_FY2017_ACCESSION = "0000021344-18-000008"
_KO_FY2017_FILED = date(2018, 2, 23)          # COMMITTED (capture `filing_date`)
_KO_INCOME_ROLE = "http://www.thecocacolacompany.com/role/ConsolidatedStatementsOfIncome"
_KO_OLD_REVENUE_CONCEPT = "us-gaap_SalesRevenueGoodsNet"   # COMMITTED
_KO_NEW_REVENUE_CONCEPT = "us-gaap_Revenues"               # OBSERVED (brief: 2019, ASC 606)
_KO_FY2017_REVENUE = 35_410_000_000.0                      # COMMITTED


def _shift_years(key: str, years: int) -> str:
    """A period key with every four-digit year moved by `years` — the one
    transformation used to build a LATER filing of the same filer out of an
    earlier one's captured rows.

    Digit lookaround, NOT `\\b`: `_` is a word character, so `\\b(19|20)\\d{2}`
    never fires inside `duration_2015-...` and the transformation silently
    returned the key unchanged — which made the "later" filing report the same
    three years as the earlier one. Caught by the two tests below failing;
    recorded because a fixture transformation that quietly does nothing is the
    shape of bug that makes a suite green for the wrong reason.
    """
    return re.sub(
        r"(?<!\d)(?:19|20)\d{2}(?!\d)",
        lambda match: str(int(match.group(0)) + years),
        key,
    )


def _later_ko_filing(capture, *, accession: str, filed: str) -> _Filing:
    """CONSTRUCTED-FROM-COMMITTED: KO's captured FY2017 filing with (a) each
    row's two older comparative periods dropped and two later ones appended, so
    the newer filing's three comparative years are 2017-2019 and it OVERLAPS
    the captured one on FY2017 alone, and (b) the income statement's top-line
    concept re-tagged
    `SalesRevenueGoodsNet` -> `Revenues`, which is the transition the brief
    measured at KO's 2019 ASC 606 adoption.

    Deriving the later filing from the earlier one is deliberate: it holds the
    OTHER 25 income lines identical, which is what makes "exactly one
    transition" a real question rather than an arithmetic accident of two
    unrelated statements. What the construction guarantees is the INPUT (one
    concept differs); what the test asserts is the OUTPUT (one event, both
    concepts and both values on it, both series intact), and that is not
    construction-guaranteed
    (docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md).

    Each row's LATEST captured period keeps its own captured amount, so the
    overlapping FY2017 figure is KO's real one and is carried across the re-tag
    UNCHANGED — a re-tag is not a restatement. This fixture claims nothing
    about KO's real 2018/2019 figures: the two appended periods reuse the
    FY2017 amount as an openly constructed placeholder, and no assertion here
    reads them.
    """
    rows_by_role = {}
    for role, rows in _rows_by_role(_captured_filing(capture, _KO_FY2017_ACCESSION)).items():
        later = []
        for row in rows:
            captured = row.get("values") or {}
            values = {}
            if captured:
                latest = max(captured)
                values = {
                    _shift_years(latest, ahead): captured[latest]
                    for ahead in (0, 1, 2)
                }
            concept = row.get("concept")
            if role == _KO_INCOME_ROLE and concept == _KO_OLD_REVENUE_CONCEPT:
                concept = _KO_NEW_REVENUE_CONCEPT
            later.append({**row, "concept": concept, "values": values})
        rows_by_role[role] = later
    return _Filing(accession, filed, rows_by_role)


@pytest.fixture(scope="module")
def ko_two_vintages(capture):
    older = _captured_filing(capture, _KO_FY2017_ACCESSION)
    return [
        _Filing(
            _KO_FY2017_ACCESSION,
            _KO_FY2017_FILED,
            _rows_by_role(older),
            presentation_roles=older["presentation_roles"],
        ),
        _later_ko_filing(capture, accession="0000021344-20-000006", filed="2020-02-24"),
    ]


def test_ko_concept_transition_is_one_recorded_event(series, ko_two_vintages):
    """THE PLAN'S GREEN. KO's single 2019 concept transition must surface as
    ONE recorded event — not as two unrelated series (which is what keying on
    the concept alone and reporting nothing would give) and not as a silent
    merge (which is what a join that quietly rewrote the old concept to the new
    one would give, destroying the evidence that anything changed).

    The two filings share exactly one period, FY2017, and differ in exactly one
    concept across 26 income lines. The event carries BOTH concepts and BOTH
    values, each naming the vintage it came from, so a reviewer can adjudicate
    it side by side — the brief's "enumerable EVENT, not a per-period
    inference".
    """
    joined = series.series_for(ko_two_vintages)

    assert len(joined.transitions) == 1, (
        "expected exactly one transition across 26 income lines, three "
        f"statements and two vintages; got {joined.transitions}"
    )
    event = joined.transitions[0]
    assert event.kind == "income"
    assert event.gone == (_KO_OLD_REVENUE_CONCEPT,)
    assert event.arrived == (_KO_NEW_REVENUE_CONCEPT,)
    assert event.from_vintage == ("2018-02-23", _KO_FY2017_ACCESSION)
    assert event.to_vintage == ("2020-02-24", "0000021344-20-000006")

    # BOTH concepts and BOTH values, each with its own provenance, reading
    # FROM -> TO.
    assert [(v.period, v.concept, v.value, v.vintage) for v in event.values] == [
        (_duration(2017), _KO_OLD_REVENUE_CONCEPT, _KO_FY2017_REVENUE,
         ("2018-02-23", _KO_FY2017_ACCESSION)),
        (_duration(2017), _KO_NEW_REVENUE_CONCEPT, _KO_FY2017_REVENUE,
         ("2020-02-24", "0000021344-20-000006")),
    ]

    # NOT A SILENT MERGE: both series survive under their own concepts, and the
    # old one still reports the years only it covers.
    old = joined.by_concept[("income", _KO_OLD_REVENUE_CONCEPT)]
    new = joined.by_concept[("income", _KO_NEW_REVENUE_CONCEPT)]
    assert [point.period for point in old.points] == [
        _duration(2015), _duration(2016), _duration(2017),
    ]
    assert [point.period for point in new.points] == [
        _duration(2017), _duration(2018), _duration(2019),
    ]
    # NOT TWO UNRELATED SERIES: the event names exactly these two keys.
    assert (event.kind, event.gone[0]) in joined.by_concept
    assert (event.kind, event.arrived[0]) in joined.by_concept


def test_a_line_the_newer_filing_kept_produces_no_transition(series, ko_two_vintages):
    """The other half of the GREEN, and the reason the event is discriminating
    rather than noise: KO's 25 OTHER income lines, its 38 balance-sheet lines
    and its 36 cash-flow lines all cross the same vintage boundary unchanged
    and produce nothing. A detector that fired on those would report ~99
    "transitions" per filing pair and be unreadable — which is the failure mode
    of inferring identity per period instead of enumerating events.
    """
    joined = series.series_for(ko_two_vintages)
    assert [event.kind for event in joined.transitions] == ["income"]
    cogs = joined.by_concept[("income", "us-gaap_CostOfGoodsSold")]
    assert [point.period for point in cogs.points] == [
        _duration(year) for year in (2015, 2016, 2017, 2018, 2019)
    ]


# --- vintage resolution: the store's rule, not a second one -----------------

_RESTATED_ROLE = "http://example.com/role/ConsolidatedStatementsOfIncome"


def _restatement_filings(older_value, newer_value) -> list:
    """CONSTRUCTED-CONVENTIONAL: two filings of one filer reporting the SAME
    period under the SAME concept with different amounts — a restatement, the
    case the store's vintage policy exists for.

    TWO concepts, not one: a one-concept payload cannot tell a sorted key
    order from an arrival order, so the determinism assertion would pass on an
    implementation that has none. `CostOfGoodsSold` sorts before `Revenues`,
    the reverse of the order they are written in here.
    """
    def rows(revenue):
        return [
            _line_row("us-gaap_Revenues", "Revenue", {_duration(2018): revenue}),
            _line_row("us-gaap_CostOfGoodsSold", "Cost of goods sold",
                      {_duration(2018): 12_000_000_000.0}),
        ]
    return [
        _Filing("0000000000-19-000001", "2019-02-20", {_RESTATED_ROLE: rows(older_value)}),
        _Filing("0000000000-20-000001", "2020-02-20", {_RESTATED_ROLE: rows(newer_value)}),
    ]


def test_overlapping_vintages_resolve_newest_filed(series):
    """Two filings report FY2018; the NEWEST-FILED one supplies the point, and
    the point names the vintage it came from so the choice is auditable rather
    than implicit. This is the store's existing policy
    (`kpi_spine_view._identity_vintage`, kpi_spine_view.py:496-522; the same
    max-on-`as_of` rule as `kpi_store.query_latest`, kpi_store.py:433-440),
    reused — not a second policy invented here.
    """
    joined = series.series_for(_restatement_filings(31_856_000_000.0, 34_300_000_000.0))
    point = joined.by_concept[("income", "us-gaap_Revenues")].points[0]

    assert point.value == 34_300_000_000.0
    assert point.vintage == ("2020-02-20", "0000000000-20-000001")


def test_a_newer_filing_with_a_smaller_accession_still_wins(series):
    """THE ACCESSION IS NOT A CLOCK, and this is the only test that proves the
    ordering reads `as_of` at all: replace the vintage key with the accession
    alone and every OTHER fixture in this module stays green, because in each
    of them the accession happens to sort the same direction as the date. This
    one fails.

    An accession's first ten digits are the CIK of whoever TRANSMITTED the
    filing — the issuer or its filing agent — so it changes when a filer
    switches agent and orders by issuer prefix, not by time (the argument
    `kpi_spine_view._vintage_key` makes in its own prose, kpi_spine_view.py
    :456). That the prefix really does move across one filer's decade is
    COMMITTED, not supposed: the capture holds KO's own
    `0000021344-18-000008` (2018) and the agent-transmitted
    `0001628280-26-010047` (2026). CONSTRUCTED here is only the DIRECTION —
    those two observed prefixes paired so the newer filing carries the
    smaller accession, which is the switch an issuer makes when it brings
    filing in-house.
    """
    concept = "us-gaap_Revenues"
    joined = series.series_for([
        _Filing("0001628280-19-000001", "2019-02-21", {_RESTATED_ROLE: [
            _line_row(concept, "Revenue", {_duration(2018): 31_856_000_000.0}),
        ]}),
        _Filing("0000021344-20-000006", "2020-02-24", {_RESTATED_ROLE: [
            _line_row(concept, "Revenue", {_duration(2018): 34_300_000_000.0}),
        ]}),
    ])
    point = joined.by_concept[("income", concept)].points[0]

    assert point.vintage == ("2020-02-24", "0000021344-20-000006"), (
        "the 2020 filing is newer but its accession sorts SMALLER; picking "
        f"{point.vintage} means the ordering read the accession, not the date"
    )
    assert point.value == 34_300_000_000.0


def test_input_order_does_not_change_the_answer(series):
    """The filings arrive in whatever order a caller enumerated accessions in.
    Newest-filed must be a property of the FILINGS, never of the argument
    order — the same defect the store's own grouping calls out (`kpi_store.
    _group_period_entries`: same data, different result on file-glob order).

    `Series.__eq__` ALONE CANNOT SAY THIS. `by_concept` is a `dict`, and dict
    equality ignores insertion order, so an implementation that emitted its
    keys in whatever order the filings arrived would satisfy `==` and leave
    the module's own "ordered by that key, so two runs never disagree"
    untested. The KEY ORDER is therefore asserted separately, on a fixture
    with two concepts — with one, every order is sorted.
    """
    filings = _restatement_filings(31_856_000_000.0, 34_300_000_000.0)
    forward = series.series_for(filings)
    backward = series.series_for(list(reversed(filings)))

    assert forward == backward
    assert list(forward.by_concept) == list(backward.by_concept)
    assert list(forward.by_concept) == [
        ("income", "us-gaap_CostOfGoodsSold"), ("income", "us-gaap_Revenues"),
    ]


def _conformance_pair(older, newer) -> list:
    """Two filings differing only in vintage, for the store-agreement oracle.
    Each is `(as_of, accession)`."""
    return [
        _Filing(accession, as_of, {_RESTATED_ROLE: [
            _line_row("us-gaap_Revenues", "Revenue", {_duration(2018): value}),
        ]})
        for value, (as_of, accession) in enumerate((older, newer), start=1)
    ]


@pytest.mark.parametrize("filings", [
    pytest.param(
        _conformance_pair(("2020-02-20", "0000000000-20-000001"),
                          ("2020-02-20", "0000000000-20-000002")),
        id="same-day-tie-broken-by-accession",
    ),
    pytest.param(
        _conformance_pair(("2019-02-21", "0001628280-19-000001"),
                          ("2020-02-24", "0000021344-20-000006")),
        id="differing-as-of-outranks-a-smaller-accession",
    ),
])
def test_the_newest_filed_rule_agrees_with_the_store(series, spine_view, filings):
    """CONFORMANCE, not a copy: the vintage this module picks is checked
    against the STORE's own `_identity_vintage` fed the equivalent
    observations. If the store ever reorders vintages differently — a third
    key component, a different tie rule — this fails instead of the two
    silently drifting apart. `_identity_vintage` is private to its module and
    is read here only as an oracle, never called by production code.

    BOTH HALVES OF THE STORE'S RULE ARE PINNED, in two parametrized cases,
    because they are two different claims and a tie-only oracle pins only one:

      same-day  — `as_of` cannot separate them and the accession decides,
                  which is why the store's key is the PAIR
                  `(as_of, source_accession)` (kpi_spine_view.py:443-464);
      differing — `as_of` decides and the accession must not, which is the
                  ORDERING half. Its accessions run counter to its dates for
                  the reason `test_a_newer_filing_with_a_smaller_accession_
                  still_wins` gives, so an oracle that agreed by coincidence
                  of sort direction cannot agree here.
    """
    joined = series.series_for(filings)
    picked = joined.by_concept[("income", "us-gaap_Revenues")].points[0].vintage

    store_period = {"observations": [
        {"as_of": filing.filing_date, "source_accession": filing.accession_no}
        for filing in filings
    ]}
    assert picked == spine_view._identity_vintage(store_period)


# --- what the departure-AND-arrival rule does and does not see --------------
#
# Every fixture in this section is CONSTRUCTED-CONVENTIONAL: it exercises a
# re-tag shape, and no captured filing pair exercises any of them (the capture
# holds rows for one filing per filer). The shapes themselves are not invented
# — the two silent-miss cases below are how ASC 606 was adopted, the same
# standard KO's measured transition came from.


def _filing_tagging(accession: str, filed: str, tagged: dict) -> _Filing:
    """One filing whose income statement tags exactly
    `{concept: {period: value}}`, one row per concept."""
    return _Filing(accession, filed, {_RESTATED_ROLE: [
        _line_row(concept, concept.split("_")[-1], values)
        for concept, values in tagged.items()
    ]})


def test_several_concepts_moving_at_once_ride_one_event(series):
    """The `len(gone) > 1` branch, which both module docstrings specify and
    nothing exercised. Two concepts leave and two arrive across one shared
    period: ONE event carries all four, and this module declines to say which
    became which. Pairing them 1-to-1 — by order, by position, by label
    similarity — is precisely the silent merge the design forbids, so the
    ambiguity is handed to the reader intact.
    """
    joined = series.series_for([
        _filing_tagging("0000000000-19-000001", "2019-02-20", {
            "us-gaap_SalesRevenueGoodsNet": {_duration(2018): 1.0},
            "us-gaap_SalesRevenueServicesNet": {_duration(2018): 2.0},
        }),
        _filing_tagging("0000000000-20-000001", "2020-02-20", {
            "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax":
                {_duration(2018): 3.0},
            "us-gaap_RevenueFromContractWithCustomerIncludingAssessedTax":
                {_duration(2018): 4.0},
        }),
    ])

    assert len(joined.transitions) == 1
    event = joined.transitions[0]
    assert event.gone == (
        "us-gaap_SalesRevenueGoodsNet", "us-gaap_SalesRevenueServicesNet",
    )
    assert event.arrived == (
        "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax",
        "us-gaap_RevenueFromContractWithCustomerIncludingAssessedTax",
    )
    assert [value.value for value in event.values] == [1.0, 2.0, 3.0, 4.0]


def test_an_unrelated_drop_and_add_is_recorded_like_a_retag(series):
    """THE FALSE POSITIVE, pinned deliberately. A filer that stops reporting
    one line and starts reporting an unrelated other one in the same period
    pair produces `gone=(X,), arrived=(Y,)` — byte-identical in shape to a real
    re-tag, because nothing structural separates them.

    Current behaviour: it IS recorded. That is the intended direction — an
    event is a CANDIDATE for review carrying both concepts and both values,
    never a verdict that X became Y, and the reviewer who reads this one
    dismisses it in a second. Suppressing it would need a similarity judgement
    this module has no grounds to make. Pinned so the choice is a decision on
    the record rather than an accident.
    """
    joined = series.series_for([
        _filing_tagging("0000000000-19-000001", "2019-02-20", {
            "us-gaap_Revenues": {_duration(2018): 100.0},
            "us-gaap_IncomeLossFromDiscontinuedOperationsNetOfTax":
                {_duration(2018): 5.0},
        }),
        _filing_tagging("0000000000-20-000001", "2020-02-20", {
            "us-gaap_Revenues": {_duration(2018): 100.0},
            "us-gaap_RestructuringCharges": {_duration(2018): 7.0},
        }),
    ])

    assert len(joined.transitions) == 1
    event = joined.transitions[0]
    assert event.gone == ("us-gaap_IncomeLossFromDiscontinuedOperationsNetOfTax",)
    assert event.arrived == ("us-gaap_RestructuringCharges",)


def test_a_modified_retrospective_adoption_records_no_event(series):
    """BLIND SPOT 1, pinned at its CURRENT no-event behaviour so lifting it
    later forces this test to change.

    Under modified-retrospective adoption — the transition method most ASC 606
    filers chose, and the standard KO's own measured transition came from — the
    filer tags the NEW concept for the adoption year only and leaves the
    comparative years under the OLD one. Every period the two filings SHARE
    therefore reads `{A} -> {A}`: no departure, no arrival, no event. The
    re-tag is real and this rule cannot see it, because the only period that
    would show it is the one period the older filing never reported.

    What a reader gets instead is two series that abut rather than overlap —
    visible in `by_concept`, unexplained by `transitions`. That is a MISS, not
    a wrong answer, and the module's docstrings now say so.
    """
    joined = series.series_for([
        _filing_tagging("0000000000-19-000001", "2019-02-20", {
            "us-gaap_SalesRevenueGoodsNet": {
                _duration(2016): 1.0, _duration(2017): 2.0, _duration(2018): 3.0,
            },
        }),
        _filing_tagging("0000000000-20-000001", "2020-02-20", {
            "us-gaap_SalesRevenueGoodsNet": {
                _duration(2017): 2.0, _duration(2018): 3.0,
            },
            "us-gaap_Revenues": {_duration(2019): 4.0},
        }),
    ])

    assert joined.transitions == ()
    assert sorted(joined.by_concept) == [
        ("income", "us-gaap_Revenues"),
        ("income", "us-gaap_SalesRevenueGoodsNet"),
    ]


def test_dual_tagging_in_the_transition_year_records_no_event(series):
    """BLIND SPOT 2, same pin. A filer that tags BOTH concepts in the
    transition year gives `{A} -> {A, B}` on the shared period: an arrival with
    no departure, which the departure-AND-arrival rule declines by design
    (an arrival alone is an ordinary new line). The re-tag is again real and
    again invisible here.

    Both blind spots share one root: the rule reads a re-tag as a SUBSTITUTION
    within one period, and a filer that phases the change in over two filings
    never presents one.
    """
    joined = series.series_for([
        _filing_tagging("0000000000-19-000001", "2019-02-20", {
            "us-gaap_SalesRevenueGoodsNet": {
                _duration(2017): 1.0, _duration(2018): 2.0,
            },
        }),
        _filing_tagging("0000000000-20-000001", "2020-02-20", {
            "us-gaap_SalesRevenueGoodsNet": {
                _duration(2018): 2.0, _duration(2019): 3.0,
            },
            "us-gaap_Revenues": {_duration(2018): 2.0, _duration(2019): 3.0},
        }),
    ])

    assert joined.transitions == ()


# --- what this module must never do to a number -----------------------------


def test_values_are_carried_verbatim_never_through_binary_float(series):
    """This module SELECTS values; it never computes with them, and a value it
    emits must be the object the filing supplied.

    The test value is float-HOSTILE on purpose: `1.005e9` is a non-terminating
    binary fraction, and the same module family has already manufactured a
    false restatement out of exactly it (docs/loom/memory/
    construction-guaranteed-invariant-proves-nothing.md, "binary float is the
    same shape"). Any normalisation on the way through — `float(value)`,
    `value * 1`, a round-trip through JSON — corrupts it here and the
    assertion fails; a green run means no arithmetic happened, which is the
    property this module claims. A test value like `301.63e6` is float-exact
    and would pass while the code was wrong.
    """
    exact = Decimal("1.005E+9")
    filing = _Filing("0000000000-20-000003", "2020-02-20", {_RESTATED_ROLE: [
        _line_row("us-gaap_Revenues", "Revenue", {_duration(2018): exact}),
    ]})
    point = series.series_for([filing]).by_concept[
        ("income", "us-gaap_Revenues")].points[0]

    assert point.value is exact
    assert isinstance(point.value, Decimal)


# --- fail loud --------------------------------------------------------------


@pytest.mark.parametrize("filing", [
    _Filing(None, "2020-02-20", {}),
    _Filing("0000000000-20-000004", None, {}),
])
def test_a_filing_without_provenance_fails_loud(series, filing):
    """A filing carrying no accession or no filing date has no vintage, and a
    missing half read as `""` would silently sort it OLDEST — quietly losing to
    every real filing on the newest-filed rule. The store tolerates that for a
    hand-fed payload; a reconstruction reading real filings must not."""
    with pytest.raises(ValueError, match="vintage"):
        series.series_for([filing])


def test_one_vintage_tagging_two_amounts_for_one_period_fails_loud(series):
    """A single filing tagging one concept twice for one period with DIFFERENT
    amounts is a contradiction this module cannot resolve, and picking one
    silently is the "system disguises its own failure as data" mode the whole
    arc exists to remove. It raises, naming both amounts.

    Not hypothetical in shape: the captured KO and IBM cash-flow statements
    each carry one concept on TWO rows (`Balance at beginning of year` /
    `...end of year`) — the next test pins that the AGREEING case, which is
    what real filings actually do, still joins.
    """
    concept = "us-gaap_Revenues"
    filing = _Filing("0000000000-20-000005", "2020-02-20", {_RESTATED_ROLE: [
        _line_row(concept, "Revenue", {_duration(2018): 1.0}),
        _line_row(concept, "Revenue, restated", {_duration(2018): 2.0}),
    ]})
    with pytest.raises(ValueError, match="two amounts"):
        series.series_for([filing])


def test_a_concept_on_two_rows_with_one_amount_still_joins(series, capture):
    """OBSERVED via COMMITTED rows: KO's captured cash-flow statement puts
    `CashAndCashEquivalentsAtCarryingValue` on two rows — the opening and
    closing balance lines — and edgartools gives BOTH rows the same four
    instant values. One concept, two labels, no contradiction: the series keeps
    both labels (display) and one point per period (identity).
    """
    entry = _captured_filing(capture, _KO_FY2017_ACCESSION)
    filing = _Filing(
        _KO_FY2017_ACCESSION, _KO_FY2017_FILED, _rows_by_role(entry),
        presentation_roles=entry["presentation_roles"],
    )
    cash = series.series_for([filing]).by_concept[
        ("cash_flow", "us-gaap_CashAndCashEquivalentsAtCarryingValue")]

    assert cash.labels == ("Balance at beginning of year", "Balance at end of year")
    assert [point.period for point in cash.points] == [
        f"instant_{year}-12-31" for year in (2014, 2015, 2016, 2017)
    ]


# --- the documented limit of the period key ---------------------------------


def test_a_period_key_is_matched_verbatim_across_vintages(series):
    """PINS THE `LOOM-SIMPLIFY` CEILING marked inside
    `kpi_us_statement_series._tagged_amounts`: two vintages join on a period
    only when the filer spells the period key IDENTICALLY. Calendar-year filers
    (KO, IBM, DUK — every filer in this arc's measured set) do.
    A 52/53-week filer does NOT: its fiscal year
    ends on a weekday, so FY2017 is `...2017-09-30` in one filing and
    `...2017-10-01` in another, and this join reads that as two periods.

    Asserted, not merely commented, so the day the ceiling is lifted this test
    is what has to change — the upgrade path is the store's own
    `same_period` / `_snap_month_end` (kpi_store.py), which exists for this.
    """
    concept = "us-gaap_Revenues"
    drifting = [
        _Filing("0000000000-18-000001", "2018-11-05", {_RESTATED_ROLE: [
            _line_row(concept, "Net sales",
                      {"duration_2016-09-25_2017-09-30": 229_234_000_000.0}),
        ]}),
        _Filing("0000000000-19-000002", "2019-10-31", {_RESTATED_ROLE: [
            _line_row(concept, "Net sales",
                      {"duration_2016-09-25_2017-10-01": 229_234_000_000.0}),
        ]}),
    ]
    points = series.series_for(drifting).by_concept[("income", concept)].points
    assert [point.period for point in points] == [
        "duration_2016-09-25_2017-09-30", "duration_2016-09-25_2017-10-01",
    ], "the verbatim period key now joins across a drifting fiscal year-end"
