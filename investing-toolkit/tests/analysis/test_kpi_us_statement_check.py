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


def _line(shape, concept, *, weight, parent, values, label=None, level=5):
    return shape.Line(
        label=label if label is not None else concept.split("_", 1)[-1],
        concept=concept,
        level=level,
        weight=weight,
        calculation_parent=parent,
        values=values,
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


def test_every_disagreement_in_the_capture_is_accounted_for(check, shape, capture):
    """The honest census, and the one test that states this module's LIMIT.

    `verify` compares EXACTLY: the plan says compare Σ(child × weight) to the
    parent's reported value, and `Line` carries no `decimals`, so this module
    has no way to know the precision the filer claimed. Filers round each fact
    independently, so an exactly-equal comparison reports rounding residue as
    `disagrees`. This test measures how much of that there is, using the
    `decimals` the CAPTURE stores (which `verify` never sees), and asserts that
    every disagreement is either
      (a) inside the group's own declared rounding interval — (n+1)/2 units at
          the least precise `decimals` among the parent and its children, the
          XBRL 2.1 §5.2.5.2 calculation-consistency reading — or
      (b) the one named case below.

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
    rounding = 0
    named_case = 0
    for filing in _filings_with_rows(capture):
        declared = {}
        for entry in filing["roles_captured"]:
            for row in entry.get("rows") or []:
                declared.setdefault(row["concept"], row.get("decimals") or {})
        for result in check.verify(_assembled(shape, capture, filing["accession"])):
            if result.status != check.DISAGREES:
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
            if abs(result.difference) <= tolerance:
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

    assert unexplained == [], (
        "a disagreement this suite cannot account for as filer rounding or as "
        "the one named linkbase-only case — investigate before trusting the "
        f"status: {unexplained}"
    )
    # MEASURED, not designed: pinned so that a change in either number is
    # visible rather than absorbed.
    assert (rounding, named_case) == (24, 3)
