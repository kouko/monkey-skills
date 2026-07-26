"""Tests for analysis-kpi/scripts/kpi_us_statement_check.py — verifying every
declared sum in `Decimal` (plan Task 4),
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md.

FIXTURE PROVENANCE, stated per fixture and never in bulk (the convention this
arc's sibling suites already carry):

  COMMITTED   — read from tests/data/fixtures/
                us_statement_reconstruction_2026-07-26.json, the live capture
                made for plan Task 3. Verbatim rows; no verdict of ours is
                stored in it, so every status below is recomputed here.
  CONSTRUCTED — a `Line` written by hand. Used where the case under test is
                not in the committed capture. Each says at its own site what
                part of it is grounded and what part was written.

The suite makes no network call.

No `@req` tags: this dispatch carries no registered loom-spec REQ-ids (the work
is tracked by named plan Task 4), so `@req` is omitted per the implementer
contract.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from decimal import Decimal

import pytest
from conftest import SKILLS

STATEMENT_CHECK_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_check.py"
STATEMENT_SHAPE_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_shape.py"


def _load(name: str, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def check():
    return _load("kpi_us_statement_check_test", STATEMENT_CHECK_SCRIPT)


@pytest.fixture(scope="module")
def shape():
    """Task 3's assembly module. Its `Line` and `Statements` are the INPUT
    contract this module verifies, so the tests build their inputs out of the
    real dataclasses rather than a look-alike — a stand-in would keep agreeing
    with a field name that had since been renamed."""
    return _load("kpi_us_statement_shape_for_check_test", STATEMENT_SHAPE_SCRIPT)


def _line(shape, concept, *, weight, parent, values, label=None, level=5,
          decimals=None, balance=None):
    return shape.Line(
        label=label if label is not None else concept.split("_", 1)[-1],
        concept=concept,
        level=level,
        weight=weight,
        calculation_parent=parent,
        values=values,
        # DEFAULTS TO None, the taxonomy's commonest answer (349 of the 455
        # captured rows) and the one that means "nothing is claimed".
        balance=balance,
        # DEFAULTS TO EMPTY, which means "the filer declared no precision" and
        # is read as "compare exactly" — so every fixture that says nothing
        # about precision keeps the exact comparison Task 4 was written under.
        decimals=decimals if decimals is not None else {},
    )


def _statements(shape, kind, lines):
    return shape.Statements(
        by_kind={kind: list(lines)},
        roles={kind: ("http://example.test/role/OnlyRoleForThisFixture",)},
        unrecognised_dimension_keys=(),
    )


# --- the RED test: the arithmetic must not run on binary float --------------


def test_sum_check_uses_decimal_not_binary_float(check, shape):
    """CONSTRUCTED — per-share amounts at three decimal places, chosen to be
    float-HOSTILE.

    docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md:
    "any cross-layer arithmetic on money/count values goes through `Decimal`,
    never binary float — and a test value must be chosen to be float-*hostile*
    (a non-terminating binary fraction), or a green suite proves nothing."

    WHY NOT THE MEMORY'S LITERAL `1.005 x 1e9`, stated because the plan's
    acceptance names that case: that hazard is a value-x-SCALE multiply, and
    this module has no scale multiply. Its only multiply is child x weight, and
    every weighted row in the committed capture carries weight 1.0 or -1.0
    (188 of 188), both of which are float-EXACT — a test built on that multiply
    would pass under a binary-float implementation and prove nothing. So the
    memory's hostile fraction `1.005` is kept and the hostility is put where
    this module's float exposure actually is: the accumulation.

    The first assertion pins that premise. If a future runtime made this pair
    float-benign, the test would silently stop testing anything, which is the
    exact failure mode the memory names.
    """
    period = "duration_2017-01-01_2017-12-31"
    assert 1.005 + 0.005 != 1.01, (
        "premise gone: this test only distinguishes Decimal from binary float "
        "while the pair is float-hostile"
    )

    statements = _statements(shape, "income", [
        _line(
            shape, "us-gaap_IncomeLossFromContinuingOperationsPerBasicShare",
            weight=1.0, parent="us-gaap_EarningsPerShareBasic",
            values={period: 1.005},
        ),
        _line(
            shape, "us-gaap_IncomeLossFromDiscontinuedOperationsNetOfTaxPerBasicShare",
            weight=1.0, parent="us-gaap_EarningsPerShareBasic",
            values={period: 0.005},
        ),
        _line(
            shape, "us-gaap_EarningsPerShareBasic",
            weight=None, parent=None, values={period: 1.01},
        ),
    ])

    (result,) = check.verify(statements)

    assert result.status == "agrees", (
        f"the filer's own arithmetic reconciles exactly; got {result.status} "
        f"with computed={result.computed} reported={result.reported}"
    )
    assert result.computed == result.reported
    assert result.difference == 0


# --- the GREEN acceptance: NEE's declared double-count ----------------------


NEE_OPERATING = "us-gaap_NetCashProvidedByUsedInOperatingActivities"


def test_nee_operating_cash_flow_double_count_disagrees_with_both_figures_visible(
    check, shape,
):
    """The DECLARATION SHAPE is OBSERVED, the ROW VALUES are CONSTRUCTED, and
    the two must not be read as one label.

    OBSERVED (brief §Decision, docs/loom/specs/
    2026-07-26-as-filed-statement-reconstruction.md, measured across the
    56-filer verification universe): NEE declares BOTH `ProfitLoss` and
    `NetIncomeLoss` as children of operating cash flow, and its 5,378M
    discrepancy is exactly its net income counted twice — one of 3 genuine
    filer-declaration quirks in 509 declared subtotals.

    CONSTRUCTED: the row-level figures. NEE is NOT in the committed capture
    (which holds KO x2, IBM, O, DUK), and plan Task 4 may not add a filing to
    it, so the group is written to the diagnosis above: two net-income children
    of 5,378M each and one ordinary adjustment, against a parent reporting the
    total that counts net income ONCE. What is therefore NOT tested here is
    that NEE's filing really carries these rows — only that a group shaped the
    way the brief measured is reported the way the plan requires. A committed
    NEE capture would upgrade this fixture from CONSTRUCTED to COMMITTED.

    The plan's GREEN: reported as `disagrees` with both figures visible, never
    silently summed and never auto-corrected (auto-correction is an OPEN
    QUESTION in the brief, deliberately not decided here).
    """
    period = "duration_2018-01-01_2018-12-31"
    net_income = 5_378_000_000
    statements = _statements(shape, "cash_flow", [
        _line(shape, "us-gaap_ProfitLoss", weight=1.0, parent=NEE_OPERATING,
              values={period: net_income}, label="Net income"),
        _line(shape, "us-gaap_NetIncomeLoss", weight=1.0, parent=NEE_OPERATING,
              values={period: net_income}, label="Net income attributable to NEE"),
        _line(shape, "us-gaap_DepreciationDepletionAndAmortization", weight=1.0,
              parent=NEE_OPERATING, values={period: 4_000_000_000}),
        _line(shape, NEE_OPERATING, weight=1.0, parent=None,
              values={period: 9_378_000_000},
              label="Net cash provided by operating activities"),
    ])

    (result,) = check.verify(statements)

    assert result.status == "disagrees"
    # BOTH figures visible — the filer's own reported total and the sum its own
    # declaration produces. A report showing only one of them cannot be argued
    # with by a reader holding the filing.
    assert result.reported == 9_378_000_000
    assert result.computed == 14_756_000_000
    assert result.difference == net_income, (
        "the discrepancy IS the net income, counted twice; anything else means "
        "the double-count was partly absorbed somewhere"
    )
    # Neither net-income concept was silently merged away by de-duplication:
    # they are DIFFERENT concepts carrying the same figure, which is the whole
    # quirk. Both must remain readable in the report.
    contributions = {term.concept: term.value for term in result.terms}
    assert contributions["us-gaap_ProfitLoss"] == net_income
    assert contributions["us-gaap_NetIncomeLoss"] == net_income
    # NOT auto-corrected: `computed` is the declaration's own arithmetic.
    assert result.computed != result.reported


# --- the committed capture: real filings, recomputed every run --------------


@pytest.fixture(scope="module")
def capture():
    """COMMITTED — tests/data/fixtures/us_statement_reconstruction_2026-07-26.json,
    captured live for plan Task 3. It stores no verdict of ours, so every
    status asserted below is recomputed from the filing's own rows."""
    fixture = (
        SKILLS.parent / "tests" / "data" / "fixtures"
        / "us_statement_reconstruction_2026-07-26.json"
    )
    return json.loads(fixture.read_text(encoding="utf-8"))


class _CapturedXBRL:
    """The two-attribute slice of `edgar.xbrl.XBRL` that Task 3's assembly
    reads — the filing's whole role list, and the rows of one role."""

    def __init__(self, filing_entry: dict):
        self._rows_by_role = {
            entry["role"]: entry["rows"]
            for entry in filing_entry["roles_captured"]
            if entry.get("rows") is not None
        }
        self.presentation_roles = list(filing_entry["presentation_roles"])

    def get_statement(self, role: str) -> list[dict]:
        return self._rows_by_role[role]


class _CapturedFiling:
    def __init__(self, filing_entry: dict):
        self.accession_no = filing_entry["accession"]
        self._xbrl = _CapturedXBRL(filing_entry)

    def xbrl(self):
        return self._xbrl


def _filings_with_rows(capture):
    return [f for f in capture["filings"] if f.get("rows_captured")]


def _filing(capture, accession: str) -> dict:
    for filing in capture["filings"]:
        if filing["accession"] == accession:
            return filing
    raise AssertionError(f"accession {accession} is not in the capture")


def _assembled(shape, capture, accession: str):
    """The filing's three statements, assembled by the LIVE Task 3 code from
    the captured rows — never from a stored assembly result."""
    return shape.statements_for(_CapturedFiling(_filing(capture, accession)))


KO_FY2017 = "0000021344-18-000008"
IBM_FY2025 = "0000051143-26-000010"


def _one(checks, *, kind, parent, period):
    matches = [
        c for c in checks
        if c.kind == kind and c.parent == parent and c.period == period
    ]
    assert len(matches) == 1, (
        f"expected exactly one check for {kind}/{parent}/{period}, got {len(matches)}"
    )
    return matches[0]


def test_ko_fy2017_operating_cash_flow_reconciles(check, shape, capture):
    """COMMITTED — KO FY2017 (0000021344-18-000008) declares eleven children of
    operating cash flow, and they sum EXACTLY to its reported 6,995M.

    This is the oracle working on real filed data, and it is not
    construction-guaranteed: the weights and the parent-child structure come
    from the calculation linkbase while every value comes from the fact table,
    and nothing forces the two to agree
    (docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md).
    """
    checks = check.verify(_assembled(shape, capture, KO_FY2017))
    result = _one(
        checks, kind="cash_flow",
        parent="us-gaap_NetCashProvidedByUsedInOperatingActivities",
        period="duration_2017-01-01_2017-12-31",
    )
    assert result.status == "agrees"
    assert result.reported == 6_995_000_000
    assert result.computed == 6_995_000_000
    assert len(result.terms) == 11


def test_a_partially_tagged_group_is_incomplete_not_a_disagreement(
    check, shape, capture,
):
    """COMMITTED — KO FY2017's balance sheet carries a stub period,
    `instant_2015-06-12`, for which ONE of `us-gaap_Assets`' nine children is
    tagged and the parent itself is not.

    A missing child is not a wrong sum (plan Task 4). Summing what happens to
    be present would report a 95M "total assets" against a filer that reported
    none — a fabricated disagreement of exactly the kind this arc exists to
    remove. The same group in a fully tagged period must still be checked, so
    `incomplete` is a property of the (group, period) pair and not of the
    group.
    """
    checks = check.verify(_assembled(shape, capture, KO_FY2017))

    stub = _one(checks, kind="balance_sheet", parent="us-gaap_Assets",
                period="instant_2015-06-12")
    assert stub.status == "incomplete"
    assert stub.computed is None, "a partial sum must not be presented as a total"
    assert stub.difference is None
    assert stub.reported is None, "the filer reported no total for this period"
    assert "us-gaap_AssetsCurrent" in stub.unsummable_children

    real = _one(checks, kind="balance_sheet", parent="us-gaap_Assets",
                period="instant_2017-12-31")
    assert real.status == "agrees"
    assert real.unsummable_children == ()


def test_a_group_whose_parent_line_is_absent_is_incomplete(check, shape, capture):
    """COMMITTED — KO FY2017's CASH-FLOW statement presents two children of
    `us-gaap_CashCashEquivalentsAndShortTermInvestments`, but never presents
    that parent as a line of its own (it is a balance-sheet line).

    There is nothing to compare against, so there is no verdict to give. The
    children are all tagged, so the sum IS computable and is reported — what is
    missing is the filer's own figure, and `reported is None` is how the report
    says so rather than inventing one.
    """
    checks = check.verify(_assembled(shape, capture, KO_FY2017))
    result = _one(
        checks, kind="cash_flow",
        parent="us-gaap_CashCashEquivalentsAndShortTermInvestments",
        period="instant_2017-12-31",
    )
    assert result.status == "incomplete"
    assert result.reported is None
    assert result.computed == 6_006_000_000
    assert result.difference is None
    assert result.unsummable_children == ()


def test_the_same_fact_rendered_twice_contributes_once(check, shape, capture):
    """COMMITTED — KO FY2017's cash-flow statement renders
    `us-gaap_CashAndCashEquivalentsAtCarryingValue` on TWO rows, "Balance at
    beginning of year" and "Balance at end of year", carrying identical values,
    the same weight and the same calculation parent (verified identical in the
    capture).

    They are one fact shown twice, not two children: a calculation arc is
    declared between CONCEPTS, so the same concept cannot be two children of
    one parent. Counting both would double 6,006M into 12,012M and manufacture
    a disagreement out of a presentation choice.
    """
    checks = check.verify(_assembled(shape, capture, KO_FY2017))
    result = _one(
        checks, kind="cash_flow",
        parent="us-gaap_CashCashEquivalentsAndShortTermInvestments",
        period="instant_2017-12-31",
    )
    concepts = [term.concept for term in result.terms]
    assert concepts.count("us-gaap_CashAndCashEquivalentsAtCarryingValue") == 1
    assert result.computed == 6_006_000_000


DUPLICATE_PARENT = "us-gaap_CashCashEquivalentsAndShortTermInvestments"
DUPLICATE_CHILD = "us-gaap_CashAndCashEquivalentsAtCarryingValue"


@pytest.mark.parametrize("second_row", [
    pytest.param({"weight": 1.0, "values": {"instant_2017-12-31": 6_006_000_001}},
                 id="different-value"),
    pytest.param({"weight": -1.0, "values": {"instant_2017-12-31": 6_006_000_000}},
                 id="different-weight"),
    pytest.param({"weight": 1.0, "values": {"instant_2016-12-31": 6_006_000_000}},
                 id="different-period-key"),
])
def test_two_rows_of_one_concept_that_disagree_fail_loudly(check, shape, second_row):
    """CONSTRUCTED, and UNOBSERVED — which is the whole reason it raises.

    De-duplication keeps the FIRST row of a concept. That is only sound while
    the rows it discards say the same thing, and in the committed capture they
    do: the one duplicate pair (KO's cash-flow
    `CashAndCashEquivalentsAtCarryingValue`, rendered as "Balance at beginning
    of year" and "Balance at end of year") carries identical values, weight and
    decimals. Safe today, unobserved tomorrow.

    Left as a silent first-wins pick, a future pair whose rows disagreed would
    change `computed` AND the group's period set with nothing marking that a
    row was dropped — the one place in this module that resolved an unobserved
    shape by quietly choosing, while `_weight_of`, `_era` and the unresolved-
    statement reason codes all fail loud. The three cases below are the three
    ways a discarded row can differ: its value, its weight, its period keys.
    """
    period = "instant_2017-12-31"
    statements = _statements(shape, "cash_flow", [
        _line(shape, DUPLICATE_CHILD, weight=1.0, parent=DUPLICATE_PARENT,
              values={period: 6_006_000_000}, label="Balance at beginning of year"),
        _line(shape, DUPLICATE_CHILD, parent=DUPLICATE_PARENT,
              label="Balance at end of year", **second_row),
        _line(shape, DUPLICATE_PARENT, weight=1.0, parent=None,
              values={period: 6_006_000_000}),
    ])

    with pytest.raises(ValueError, match=DUPLICATE_CHILD):
        check.verify(statements)


def test_two_rows_of_one_concept_that_agree_are_still_one_child(check, shape):
    """The other half: the guard above must not reject the shape the capture
    actually holds. Two rows, two labels, one fact — one child."""
    period = "instant_2017-12-31"
    statements = _statements(shape, "cash_flow", [
        _line(shape, DUPLICATE_CHILD, weight=1.0, parent=DUPLICATE_PARENT,
              values={period: 6_006_000_000}, label="Balance at beginning of year"),
        _line(shape, DUPLICATE_CHILD, weight=1.0, parent=DUPLICATE_PARENT,
              values={period: 6_006_000_000}, label="Balance at end of year"),
        _line(shape, DUPLICATE_PARENT, weight=1.0, parent=None,
              values={period: 6_006_000_000}),
    ])

    (result,) = check.verify(statements)
    assert len(result.terms) == 1
    assert result.status == check.AGREES


def test_a_non_numeric_child_value_is_incomplete_not_a_wrong_sum(check, shape):
    """CONSTRUCTED from an OBSERVED value class. IBM's FY2025 balance sheet
    carries `us-gaap_CommitmentsAndContingencies` with the value `''` for both
    instants in the committed capture — a presented line with no number. That
    concept declares no calculation parent, so no captured GROUP contains one;
    the group here is written to put that observed value class where it would
    do damage.

    The brief records the cost of getting this wrong: 5 of the probe's 8
    reconciliation failures were "a probe artifact (a non-numeric child)" —
    i.e. a fabricated disagreement. An unusable value is a gap in the data, so
    the group is `incomplete`.
    """
    period = "instant_2025-12-31"
    statements = _statements(shape, "balance_sheet", [
        _line(shape, "us-gaap_LiabilitiesCurrent", weight=1.0,
              parent="us-gaap_Liabilities", values={period: 33_142_000_000}),
        _line(shape, "us-gaap_CommitmentsAndContingencies", weight=1.0,
              parent="us-gaap_Liabilities", values={period: ""}),
        _line(shape, "us-gaap_Liabilities", weight=1.0, parent=None,
              values={period: 119_139_000_000}),
    ])

    (result,) = check.verify(statements)

    assert result.status == "incomplete"
    assert result.computed is None
    assert result.unsummable_children == ("us-gaap_CommitmentsAndContingencies",)


def test_a_child_declaring_a_parent_but_no_weight_fails_loudly(check, shape):
    """CONSTRUCTED — and UNOBSERVED, which is why it raises rather than
    guesses. In the committed capture every one of the 175 rows carrying a
    `calculation_parent` also carries a weight (1.0 or -1.0); zero carry a
    parent without one.

    Defaulting the weight to 1.0 would put a plausible number in the report
    with no sign that anything was assumed — the silent-corruption direction
    this arc exists to close. If the row shape ever changes, this raises with
    the concept named.
    """
    period = "duration_2017-01-01_2017-12-31"
    statements = _statements(shape, "income", [
        _line(shape, "us-gaap_CostOfGoodsSold", weight=None,
              parent="us-gaap_GrossProfit", values={period: 13_256_000_000}),
        _line(shape, "us-gaap_GrossProfit", weight=1.0, parent=None,
              values={period: 22_154_000_000}),
    ])

    with pytest.raises(ValueError, match="us-gaap_CostOfGoodsSold"):
        check.verify(statements)


def test_a_rounding_interval_is_read_from_the_filers_own_decimals(check, shape):
    """CONSTRUCTED, and deliberately hand-checkable: the interval rule itself,
    pinned in BOTH directions on figures a reader can verify without a runner.

    OBSERVED, and what makes the rule necessary: 1,016 of the 1,065 declared
    precisions in the committed capture are -6 — filers state these figures
    rounded to the million and round each fact INDEPENDENTLY, so a sum of them
    can miss the parent by a million without anyone being wrong.

    Two children plus the parent at -6 gives an interval of (2+1)/2 x 1,000,000
    = 1,500,000. A 1,000,000 miss is inside it and is NOT a filer error; a
    2,000,000 miss is outside it and stays `disagrees`. The second half is the
    load-bearing one: an interval that swallowed everything would make this
    module's whole `disagrees` status unreachable, which is the failure mode a
    precision-aware comparison invites.

    `within_rounding` is its own status and NOT `agrees`: the figures do
    differ, and a report that called this exact agreement would be overstating
    the filer's arithmetic in the opposite direction.
    """
    period = "duration_2017-01-01_2017-12-31"
    millions = {period: -6}

    def group(reported):
        return _statements(shape, "income", [
            _line(shape, "us-gaap_CostOfGoodsSold", weight=1.0,
                  parent="us-gaap_GrossProfit", values={period: 20_000_000},
                  decimals=millions),
            _line(shape, "us-gaap_SellingGeneralAndAdministrativeExpense",
                  weight=1.0, parent="us-gaap_GrossProfit",
                  values={period: 15_000_000}, decimals=millions),
            _line(shape, "us-gaap_GrossProfit", weight=1.0, parent=None,
                  values={period: reported}, decimals=millions),
        ])

    (inside,) = check.verify(group(34_000_000))
    assert inside.status == check.WITHIN_ROUNDING
    assert inside.status != check.AGREES, "the figures differ; do not call it exact"
    assert inside.difference == 1_000_000
    assert inside.tolerance == 1_500_000, (
        "the interval must be the filer's own: (n+1)/2 units at the least "
        "precise declared `decimals` among the parent and its children"
    )

    (outside,) = check.verify(group(33_000_000))
    assert outside.status == check.DISAGREES, (
        "a difference beyond the filer's own declared precision is a real "
        "disagreement; an interval that absorbed it would make `disagrees` "
        "unreachable"
    )
    assert outside.difference == 2_000_000

    # Both statuses mean "the declared arithmetic held" only for the first one,
    # and the module must say which is which in ONE place rather than leaving
    # every consumer to re-derive it.
    assert check.WITHIN_ROUNDING in check.RECONCILES
    assert check.AGREES in check.RECONCILES
    assert check.DISAGREES not in check.RECONCILES
    assert check.INCOMPLETE not in check.RECONCILES


def test_an_undeclared_precision_still_compares_exactly(check, shape):
    """CONSTRUCTED — the same group with NO `decimals` anywhere must keep
    Task 4's exact comparison.

    This is the fail-CLOSED direction of the new field. An implementation that
    guessed a precision when the filer declared none would invent a tolerance
    out of nothing and start absorbing real disagreements silently — which is
    strictly worse than the overstatement the field exists to fix, because an
    overstatement is visible and an absorbed error is not.
    """
    period = "duration_2017-01-01_2017-12-31"
    statements = _statements(shape, "income", [
        _line(shape, "us-gaap_CostOfGoodsSold", weight=1.0,
              parent="us-gaap_GrossProfit", values={period: 20_000_000}),
        _line(shape, "us-gaap_GrossProfit", weight=1.0, parent=None,
              values={period: 19_999_999}),
    ])

    (result,) = check.verify(statements)

    assert result.status == check.DISAGREES
    assert result.tolerance == 0


def test_every_disagreement_in_the_capture_is_accounted_for(check, shape, capture):
    """The honest census, and the one test that states this module's LIMIT.

    UPDATED FOR PLAN TASK 8. Task 4 wrote this test as a census computed
    ENTIRELY in the test, because `Line` carried no `decimals` and `verify`
    could only compare exactly. Task 8 put `decimals` on `Line` (plan Decision
    Log, "Task 4 -> Task 8"), so the same split is now produced BY THE CODE
    PATH, and this test's own arithmetic — still read from the CAPTURE, not
    from `Line` — became the ORACLE that checks it. The pin `(24, 3)` is
    unchanged and that is the point: the field reproduces the classification
    the test used to compute for itself, group for group, rather than
    approximately.

    The rule, applied on both sides: a difference is rounding residue when it
    is within (n+1)/2 units at the least precise `decimals` among the parent
    and its children — the XBRL 2.1 §5.2.5.2 calculation-consistency reading.
    Every difference must therefore be either
      (a) inside that interval, in which case `verify` must say
          `within_rounding` and NOT `disagrees`, or
      (b) the one named case below.

    WHAT THIS DOES NOT PROVE, stated because a green run here is easy to
    over-read: both sides apply the SAME interval rule, so a wrong rule would
    be wrong in both places and this test would still pass. What it proves is
    that the filer's declared precision reaches `verify` intact through
    Task 3's `Line` and is applied per (group, period) — the plumbing and the
    classification, not the rule. The rule's own grounding is the XBRL
    specification, cited above, and `test_a_rounding_interval_is_read_from_the
    _filers_own_decimals` pins it on a hand-checkable case.

    The named case, IBM FY2025 (COMMITTED): `WeightedAverageNumberOfDiluted
    SharesOutstanding` declares `...SharesOutstandingBasic` as a child, and the
    incremental-dilutive-shares child exists in the calculation linkbase but is
    NOT a presented line, so the sum over presented rows is 10-16M shares
    short. `verify` reads presented lines only and structurally cannot see
    that; it reports `disagrees`, which for this group is a FALSE positive.
    Detecting it needs the calculation linkbase itself, which is outside
    `verify(statements)`' input — recorded here rather than hidden.
    """
    unexplained = []
    misclassified = []
    rounding = 0
    named_case = 0
    for filing in _filings_with_rows(capture):
        declared = {}
        for entry in filing["roles_captured"]:
            for row in entry.get("rows") or []:
                declared.setdefault(row["concept"], row.get("decimals") or {})
        for result in check.verify(_assembled(shape, capture, filing["accession"])):
            if result.status not in (check.DISAGREES, check.WITHIN_ROUNDING):
                continue
            precisions = [
                declared.get(c, {}).get(result.period)
                for c in [result.parent] + [t.concept for t in result.terms]
            ]
            least = min(int(p) for p in precisions) if all(
                isinstance(p, int) for p in precisions
            ) else None
            unit = Decimal(10) ** -least if least is not None else Decimal(0)
            tolerance = unit * (len(result.terms) + 1) / 2
            oracle = (
                check.WITHIN_ROUNDING if abs(result.difference) <= tolerance
                else check.DISAGREES
            )
            if result.status != oracle:
                misclassified.append(
                    (filing["ticker"], result.parent, result.period,
                     result.status, oracle, str(result.difference), str(tolerance))
                )
            if oracle == check.WITHIN_ROUNDING:
                rounding += 1
            elif (filing["ticker"], result.parent) == (
                "IBM", "us-gaap_WeightedAverageNumberOfDilutedSharesOutstanding"
            ):
                named_case += 1
            else:
                unexplained.append(
                    (filing["ticker"], result.kind, result.parent, result.period,
                     str(result.difference))
                )

    assert misclassified == [], (
        "`verify`'s own status disagrees with the interval computed from the "
        "capture — the filer's declared precision is not reaching the check "
        f"intact: {misclassified}"
    )
    assert unexplained == [], (
        "a disagreement this suite cannot account for as filer rounding or as "
        "the one named linkbase-only case — investigate before trusting the "
        f"status: {unexplained}"
    )
    # MEASURED, not designed: pinned so that a change in either number is
    # visible rather than absorbed. Unchanged from Task 4's pin — the split is
    # the same, it is now produced by the code path rather than by this test.
    assert (rounding, named_case) == (24, 3)


# --- Task 8: the per-era resolution rate ------------------------------------
#
# The plan's Task 8: "Emit, per reconstruction run, how many statements
# resolved and how many did not, BROKEN DOWN BY FILING ERA, plus the reason
# each unresolved one failed." The era split is the whole point — the brief's
# 63-of-65 was measured on filings filed 2016-2018 ONLY (brief §"A limit this
# brief must not overclaim"), and a 10-year run spans years never sampled.


def _statements_with_roles(shape, kind, lines, roles):
    """A `Statements` whose `roles` entry is given explicitly — the multi-role
    case `_statements` above cannot express."""
    return shape.Statements(
        by_kind={kind: list(lines)},
        roles={kind: tuple(roles)},
        unrecognised_dimension_keys=(),
    )


DUK_PURE_INCOME_ROLE = (
    "http://www.duke-energy.com/role/ConsolidatedStatementsOfOperations"
)
DUK_COMBINED_INCOME_ROLE = (
    "http://www.duke-energy.com/role/"
    "ConsolidatedStatementsOfOperationsAndComprehensiveIncome"
)


def _duk_income(shape, roles, revenue_concepts=(
    "us-gaap_RegulatedAndUnregulatedOperatingRevenue",
)):
    """DUK's income statement as a group whose declared sum RECONCILES
    EXACTLY, so that nothing but the total-count can be what makes it
    unresolved. `revenue_concepts` are the lines that roll into operating
    income; one of them is the resolved case, two the ambiguous one."""
    period = "duration_2014-01-01_2014-12-31"
    share = 23_925_000_000 // len(revenue_concepts)
    lines = [
        _line(shape, concept, weight=1.0, parent="us-gaap_OperatingIncomeLoss",
              values={period: share}, label="Total operating revenues")
        for concept in revenue_concepts
    ]
    lines += [
        _line(shape, "us-gaap_OperatingExpenses", weight=-1.0,
              parent="us-gaap_OperatingIncomeLoss",
              values={period: 19_000_000_000}, label="Total operating expenses"),
        _line(shape, "us-gaap_OperatingIncomeLoss", weight=None, parent=None,
              values={period: share * len(revenue_concepts) - 19_000_000_000},
              label="Operating Income"),
    ]
    return _statements_with_roles(shape, "income", lines, roles)


def test_unresolved_statements_are_counted_with_a_reason(check, shape):
    """The plan's RED for Task 8: DUK's 2013-2017 filings yield 2-3 candidate
    totals and must be counted as unresolved WITH that reason — never dropped
    silently and never resolved by picking one.

    THE RULE IS REVENUE-SCOPED, which is the arc's own structural rule applied
    to the income calculation tree: among the tree's revenue concepts, the
    candidates are those whose calculation parent is not itself a revenue
    concept. One survivor is the filing's total; two or three is the ambiguity.

    PROVENANCE, split because the halves are grounded differently:

      OBSERVED — the RULE, and that it yields exactly ONE survivor on both
        captured filings (pinned by `test_the_income_statements_in_the_capture
        _resolve_to_one_revenue_total`, which runs it on real filed rows). Also
        OBSERVED, from the brief §"A limit this brief must not overclaim":
        DUK's tree yields 2-3 candidates for every filing 2013 through 2017 and
        resolves cleanly only from 2018 — 5 of its 14 years.
      CONSTRUCTED — these rows. DUK's 2013-2017 filings are genuinely not in
        the committed capture (its one captured filing is from 2018, the era
        that resolves, and was captured census-only), so the ambiguous case
        itself must be written. What is NOT invented any more is the mechanism.

    A ROOT-COUNT READING WAS MEASURED AND REFUTED before this was built, and is
    recorded so nobody re-derives it: counting ALL calculation-tree roots makes
    the phrase meaningless — KO income has 2 roots, KO balance sheet 2, IBM
    income 4, IBM cash flow 1, because `Assets` / `LiabilitiesAndStockholders
    Equity` and the EPS rows are legitimately separate roots, and such a rule
    would report almost every real statement unresolved.

    THE SUMS ALL AGREE, deliberately. Resolution and reconciliation are
    different questions, and a report that conflated them would call this
    statement fine: every declared sum in it reconciles exactly. It is still
    unresolved, because which revenue line is the filer's total was never
    decided.
    """
    statements = _duk_income(shape, [DUK_PURE_INCOME_ROLE], revenue_concepts=(
        "us-gaap_RegulatedAndUnregulatedOperatingRevenue",
        "us-gaap_Revenues",
    ))
    assert [c.status for c in check.verify(statements)] == [check.AGREES], (
        "premise gone: this fixture only distinguishes resolution from "
        "reconciliation while its own sums reconcile"
    )

    report = check.resolution_report([("2014-02-25", statements)])

    (income,) = report.statements
    assert income.resolved is False
    assert income.kind == "income"
    assert [reason.reason for reason in income.reasons] == [check.AMBIGUOUS_TOTAL]
    # BOTH candidates named, and counted. A reason that says "ambiguous"
    # without saying between WHAT cannot be acted on by a reader holding the
    # filing.
    detail = income.reasons[0].detail
    assert "2 candidate totals" in detail
    assert "us-gaap_RegulatedAndUnregulatedOperatingRevenue" in detail
    assert "us-gaap_Revenues" in detail

    # NOT DROPPED: it is counted, in its own era, and the era is the one the
    # brief says was never sampled.
    assert income.era == check.ERA_BEFORE_SAMPLE
    (tally,) = report.by_era
    assert (tally.era, tally.resolved, tally.unresolved) == (
        check.ERA_BEFORE_SAMPLE, 0, 1
    )
    assert dict(tally.reasons) == {check.AMBIGUOUS_TOTAL: 1}


def test_the_income_statements_in_the_capture_resolve_to_one_revenue_total(
    check, shape, capture,
):
    """COMMITTED, and this is what makes the rule OBSERVED rather than
    asserted: run it on real filed rows from both eras.

    KO FY2017 declares `us-gaap_SalesRevenueGoodsNet` (into `GrossProfit`) and
    IBM FY2025 declares `us-gaap_Revenues` (also into `GrossProfit`). Each
    yields exactly ONE candidate, which is why neither is reported ambiguous.

    IBM IS THE LOAD-BEARING HALF: it presents `us-gaap_CostOfRevenue` as a
    SIBLING of `us-gaap_Revenues` under the same parent, and its local name
    contains "revenue" too. A rule matching the name alone reads IBM as TWO
    candidates and reports a clean filing as unresolved.

    TWO INDEPENDENT SIGNALS exclude it here, and this test asserts BOTH rather
    than crediting one: the taxonomy classifies `CostOfRevenue` as `debit`
    against `Revenues`' `credit`, and the filer declares it -1.0 against +1.0.
    Either alone would pass this test, which is exactly why the claim must not
    be "the sign is what does it" — on the oil-major shape the sign is +1.0 and
    only the balance separates them
    (`test_a_revenue_line_topping_the_tree_is_deliberately_a_candidate`).
    Both are structural: neither is a denylist of cost-shaped names
    ([[shared-classifier-over-open-dialects-needs-allowlist]]).
    """
    for filing in _filings_with_rows(capture):
        income = _assembled(shape, capture, filing["accession"]).by_kind["income"]
        tops = check.revenue_totals(income)
        assert len(tops) == 1, (
            f"{filing['ticker']} resolves to {len(tops)} candidate totals: {tops}"
        )

    ibm = _assembled(shape, capture, IBM_FY2025).by_kind["income"]
    assert check.revenue_totals(ibm) == ("us-gaap_Revenues",)
    cost = next(line for line in ibm if line.concept == "us-gaap_CostOfRevenue")
    revenue = next(line for line in ibm if line.concept == "us-gaap_Revenues")
    assert (cost.balance, cost.weight) == ("debit", -1.0)
    assert (revenue.balance, revenue.weight) == ("credit", 1.0), (
        "premise gone: this test only proves a deduction is excluded while the "
        "taxonomy and the filer both say it is one"
    )


def test_revenue_components_rolling_into_a_revenue_parent_are_not_candidates(
    check, shape,
):
    """CONSTRUCTED — the post-ASC-606 disaggregation shape: a filer presenting
    product and service revenue lines that roll up into its own total.

    This is the half of the rule the two captured filings cannot exercise —
    each declares a single revenue line, so the parent condition is invisible
    there and would pass every other test in this suite if it were deleted.
    Without it a filer that disaggregates its revenue reads as THREE candidate
    totals and is reported unresolved for doing exactly what the taxonomy asks.

    The parent here is a PRESENTED line; the rule tests the parent by NAME, so
    it also holds when the total is declared in the calculation linkbase but
    never put on the face of the statement.
    """
    period = "duration_2019-01-01_2019-12-31"
    statements = _statements(shape, "income", [
        _line(shape, "us-gaap_ProductRevenue", weight=1.0, parent="us-gaap_Revenues",
              values={period: 60_000_000}),
        _line(shape, "us-gaap_ServiceRevenue", weight=1.0, parent="us-gaap_Revenues",
              values={period: 40_000_000}),
        _line(shape, "us-gaap_Revenues", weight=1.0, parent="us-gaap_GrossProfit",
              values={period: 100_000_000}),
    ])

    assert check.revenue_totals(statements.by_kind["income"]) == ("us-gaap_Revenues",)

    (income,) = check.resolution_report([("2020-02-25", statements)]).statements
    assert [reason.reason for reason in income.reasons] == [], (
        "a filer that disaggregates its revenue must not be reported "
        "unresolved for it"
    )


def test_a_revenue_line_topping_the_tree_is_deliberately_a_candidate(check, shape):
    """CONSTRUCTED from an OBSERVED shape, and the DECISION it pins is the one
    a reviewer asked be made explicit rather than left implicit in the code.

    An unparented revenue line IS a candidate, deliberately. The brief measures
    PSX declaring its own total as `RevenuesAndOtherIncome` (104,622M); a
    filer's total commonly tops the calculation tree and therefore has no
    calculation parent of its own. Excluding unparented lines would drop that
    total, leave zero candidates, and report `NO_REVENUE_TOTAL` on a filing
    whose total is on the face of the statement — the "blames the filer for our
    own structure handling" direction this arc exists to close.

    THIS FIXTURE FOUND A DEFECT, recorded because the finding is the reason the
    `balance` field exists: written first with `CostOfRevenue` rolling
    POSITIVELY into a costs subtotal — the oil-major shape — it failed, because
    the filer's sign excludes a cost only where the cost is subtracted
    DIRECTLY. Here it is added to a costs total that is subtracted higher up,
    so the sign says nothing and the cost line was returned as a second
    candidate total. Only the taxonomy's own `debit` balance separates them.
    """
    period = "duration_2017-01-01_2017-12-31"
    statements = _statements(shape, "income", [
        _line(shape, "us-gaap_RevenuesAndOtherIncome", weight=None, parent=None,
              values={period: 104_622_000_000}, label="Revenues and Other Income",
              balance="credit"),
        # POSITIVE weight, and that is the whole point: it rolls INTO the costs
        # subtotal, which is what gets subtracted.
        _line(shape, "us-gaap_CostOfRevenue", weight=1.0,
              parent="us-gaap_CostsAndExpenses", values={period: 90_000_000_000},
              balance="debit"),
        _line(shape, "us-gaap_CostsAndExpenses", weight=None, parent=None,
              values={period: 90_000_000_000}, balance="debit"),
    ])

    assert check.revenue_totals(statements.by_kind["income"]) == (
        "us-gaap_RevenuesAndOtherIncome",
    )
    (income,) = check.resolution_report([("2018-02-23", statements)]).statements
    assert [reason.reason for reason in income.reasons] == []


def test_disaggregated_revenue_with_no_calculation_arcs_is_reported_ambiguous(
    check, shape,
):
    """CONSTRUCTED, and this pins the OTHER side of the decision above — the
    cost of it, stated rather than discovered later.

    Because an unparented revenue line is a candidate, a filer that presents
    revenue components with NO calculation arcs between them yields one
    candidate per component. That is reported `AMBIGUOUS_TOTAL`, and it is the
    correct answer rather than a false alarm: with no arc declaring one of them
    the parent of the others, the structure does not say which is the total,
    and the plan forbids resolving it by picking one. The reader is told the
    count and the names and can go to the filing.

    NOT the same fact as DUK's, and the report distinguishes them: a statement
    declaring no arcs AT ALL also carries `NO_DECLARED_SUMS`, which DUK's
    ambiguous-but-fully-declared tree does not.

    STATED LIMIT, unobserved and deliberately not guessed at: a filer whose
    real total DOES sit in the tree while its components sit outside it reads
    as several candidates here too. Neither captured filing shows that shape,
    and the report errs toward refusing rather than picking — the direction
    this arc requires when it cannot tell.
    """
    period = "duration_2019-01-01_2019-12-31"
    statements = _statements(shape, "income", [
        _line(shape, "us-gaap_ProductRevenue", weight=None, parent=None,
              values={period: 60_000_000}),
        _line(shape, "us-gaap_ServiceRevenue", weight=None, parent=None,
              values={period: 40_000_000}),
    ])

    (income,) = check.resolution_report([("2020-02-25", statements)]).statements

    assert sorted(reason.reason for reason in income.reasons) == [
        check.AMBIGUOUS_TOTAL, check.NO_DECLARED_SUMS,
    ]
    ambiguity = next(
        r for r in income.reasons if r.reason == check.AMBIGUOUS_TOTAL
    )
    assert "2 candidate totals" in ambiguity.detail
    assert "us-gaap_ProductRevenue" in ambiguity.detail
    assert "us-gaap_ServiceRevenue" in ambiguity.detail


def test_one_revenue_concept_rendered_twice_is_one_candidate(check, shape):
    """CONSTRUCTED from an OBSERVED presentation habit: the same concept on two
    rows.

    KO's cash-flow statement renders `CashAndCashEquivalentsAtCarryingValue`
    twice (opening and closing balance), which is why `_checks_for_statement`
    already counts one child per CONCEPT. An income role repeating its revenue
    concept — a subtotal echoed at the foot of a section — would otherwise
    produce two identical candidates and report a filing with ONE revenue line
    as ambiguous between it and itself.

    Unobserved on an income role, so this is a guard rather than a fix; it is
    taken because the two functions in this module must not disagree about
    whether a repeated row is one fact, and a later reader would read the
    asymmetry as intentional.
    """
    period = "duration_2017-01-01_2017-12-31"
    statements = _statements(shape, "income", [
        _line(shape, "us-gaap_Revenues", weight=1.0, parent="us-gaap_GrossProfit",
              values={period: 100_000_000}, label="Net revenues"),
        _line(shape, "us-gaap_Revenues", weight=1.0, parent="us-gaap_GrossProfit",
              values={period: 100_000_000}, label="Total net revenues"),
        _line(shape, "us-gaap_GrossProfit", weight=None, parent=None,
              values={period: 100_000_000}),
    ])

    assert check.revenue_totals(statements.by_kind["income"]) == ("us-gaap_Revenues",)


def test_an_income_statement_with_no_revenue_total_is_its_own_reason(check, shape):
    """CONSTRUCTED-CONVENTIONAL — an income statement declaring no revenue
    concept at all.

    ZERO CANDIDATES IS NOT AMBIGUITY, and the two must not share a label: one
    says the filer offers several totals and the structure cannot choose, the
    other says it offers none this rule can see. Collapsing them is the same
    error `within_rounding` avoids one layer down.

    UNOBSERVED here and expected in the wild: the brief's own Open Question
    records that a bank's income statement has no single revenue origin BY
    CONSTRUCTION, and 9 of the 79 universe filers are financials. The honest
    report for them is a named gap, not a silent success and not a guess.
    """
    period = "duration_2014-01-01_2014-12-31"
    statements = _statements(shape, "income", [
        _line(shape, "us-gaap_InterestAndDividendIncomeOperating", weight=1.0,
              parent="us-gaap_NetIncomeLoss", values={period: 9_000_000}),
        _line(shape, "us-gaap_NetIncomeLoss", weight=None, parent=None,
              values={period: 9_000_000}),
    ])

    report = check.resolution_report([("2014-02-25", statements)])

    (income,) = report.statements
    assert income.resolved is False
    assert [reason.reason for reason in income.reasons] == [check.NO_REVENUE_TOTAL]
    assert "0 candidate totals" in income.reasons[0].detail


def test_two_roles_for_one_kind_is_a_different_reason_than_two_totals(check, shape):
    """A filing offering TWO roles for one statement is a REAL and DIFFERENT
    ambiguity, and it gets its own code.

    `_roles_in_preference_order` picks the first deterministically today
    (preferring the purer role) and says nothing about having chosen. That pick
    is not a resolution: which role is the filer's statement was decided by our
    tie-break, not by the filing. But it is not the revenue-total ambiguity
    either — this statement resolves to exactly one revenue total, and would
    still be unresolved. Two distinct facts, two codes.

    CONSTRUCTED, and UNOBSERVED: across the five captured filings every kind
    had exactly one role (`test_a_filing_declares_one_role_per_kind_in_the
    _captured_sample` re-derives that by classifying all 694 stored role URIs).
    The condition is kept because the silent pick is real in the code today.
    """
    statements = _duk_income(
        shape, [DUK_PURE_INCOME_ROLE, DUK_COMBINED_INCOME_ROLE]
    )

    report = check.resolution_report([("2014-02-25", statements)])

    (income,) = report.statements
    assert income.resolved is False
    assert [reason.reason for reason in income.reasons] == [
        check.AMBIGUOUS_STATEMENT_ROLE
    ]
    detail = income.reasons[0].detail
    assert DUK_PURE_INCOME_ROLE in detail and DUK_COMBINED_INCOME_ROLE in detail
    # The revenue total itself is NOT ambiguous here — that is the point.
    assert len(check.revenue_totals(statements.by_kind["income"])) == 1


def test_a_statement_declaring_no_sums_is_not_vacuously_resolved(check, shape):
    """CONSTRUCTED-CONVENTIONAL — a statement whose lines declare no
    calculation parent at all.

    UNOBSERVED: all six statements in the committed capture declare sums. This
    is a fail-CLOSED guard on the direction that would otherwise be silent — a
    resolution rule phrased as "no group disagreed" is VACUOUSLY TRUE for a
    statement with no groups, so a filing whose calculation linkbase this
    reconstruction could not read at all would be reported as a clean success.
    That is the "system disguises its own failure as data" mode the plan's
    kickoff decision names, arriving through the report rather than through a
    cache.

    A CASH-FLOW statement, so the fact under test is isolated: the revenue-total
    rule is income-only, and an income fixture here would trip it too.
    """
    period = "duration_2014-01-01_2014-12-31"
    statements = _statements(shape, "cash_flow", [
        _line(shape, "us-gaap_CashAndCashEquivalentsAtCarryingValue", weight=None,
              parent=None, values={period: 1_000_000}),
    ])

    report = check.resolution_report([("2014-02-25", statements)])

    (cash_flow,) = report.statements
    assert cash_flow.resolved is False
    assert [reason.reason for reason in cash_flow.reasons] == [check.NO_DECLARED_SUMS]
    assert cash_flow.groups_checked == 0


def test_a_run_in_which_every_statement_resolves_still_emits_the_counts(check, shape):
    """The plan's GREEN, second half: a run in which every statement resolves
    still emits the counts rather than staying silent.

    A report that spoke up only on failure would leave a reader unable to tell
    "everything resolved" from "the report never ran" — and the whole reason
    this report exists is that the resolution rate must be MEASURED per era
    rather than assumed from the sampled window.
    """
    statements = _duk_income(shape, [DUK_PURE_INCOME_ROLE])

    report = check.resolution_report([("2018-02-23", statements)])

    (income,) = report.statements
    assert income.resolved is True
    assert income.reasons == ()
    (tally,) = report.by_era
    assert (tally.era, tally.resolved, tally.unresolved) == (check.ERA_SAMPLED, 1, 0)
    assert tally.reasons == ()


def test_the_capture_resolves_worse_outside_the_sampled_window(check, shape, capture):
    """COMMITTED, and the plan's GREEN, first half: the report SEPARATES ERAS.

    The two filings that carry rows sit either side of the measured window —
    KO filed 2018-02-23 (inside the 2016-2018 sample) and IBM filed 2026-02-24
    (eight years outside it) — so this is the era split on real filed data
    rather than on a fixture written to produce one.

    MEASURED, and it is the brief's own expectation confirmed rather than
    assumed: KO resolves 3 of 3, IBM 2 of 3. What the report must NOT claim is
    that IBM's income statement is a filer error. It is this module's LIMIT 2:
    IBM declares a calculation child that is not on the face of the statement,
    so the check runs 10-16M shares short and reports `disagrees` for a group
    that is not wrong. The reason code therefore says the sums do not
    reconcile — a fact about this reconstruction — and never that the filer is
    wrong. Two filings is far too small a sample to generalise the direction;
    what the test pins is that the report SPLITS them, which is what makes the
    question answerable at all.
    """
    runs = [
        (filing["filing_date"], _assembled(shape, capture, filing["accession"]))
        for filing in _filings_with_rows(capture)
    ]

    report = check.resolution_report(runs)

    by_era = {tally.era: tally for tally in report.by_era}
    assert (by_era[check.ERA_SAMPLED].resolved, by_era[check.ERA_SAMPLED].unresolved) \
        == (3, 0)
    assert (by_era[check.ERA_AFTER_SAMPLE].resolved,
            by_era[check.ERA_AFTER_SAMPLE].unresolved) == (2, 1)
    assert dict(by_era[check.ERA_AFTER_SAMPLE].reasons) == {
        check.SUMS_DO_NOT_RECONCILE: 1
    }

    # The eras are ordered oldest-first, so a reader scans the report the way
    # the years run.
    assert [tally.era for tally in report.by_era] == [
        check.ERA_SAMPLED, check.ERA_AFTER_SAMPLE
    ]

    unresolved = [s for s in report.statements if not s.resolved]
    assert [(s.era, s.kind) for s in unresolved] == [
        (check.ERA_AFTER_SAMPLE, "income")
    ]
    # The reason NAMES the group, so the reader can go to the filing and argue.
    assert "us-gaap_WeightedAverageNumberOfDilutedSharesOutstanding" in \
        unresolved[0].reasons[0].detail
    # Incomplete groups are COUNTED, not counted against: KO's balance sheet
    # carries 9 of them and the brief calls that reconstruction faithful.
    ko_balance = next(
        s for s in report.statements
        if s.era == check.ERA_SAMPLED and s.kind == "balance_sheet"
    )
    assert ko_balance.resolved is True
    assert ko_balance.groups_incomplete == 9


def test_a_filing_with_no_readable_date_fails_loudly(check, shape):
    """CONSTRUCTED — a run item whose filing date cannot be read as a year.

    The era is the entire point of this report, so a filing that cannot be
    placed in one must not be quietly bucketed anywhere: an item silently
    dropped would overstate the resolution rate of whichever era it belonged
    to, and an item dumped into a default era would understate another's. The
    module's own `_weight_of` already sets this precedent — refuse rather than
    assume.
    """
    statements = _duk_income(shape, [DUK_PURE_INCOME_ROLE])

    with pytest.raises(ValueError, match="not-a-date"):
        check.resolution_report([("not-a-date", statements)])
