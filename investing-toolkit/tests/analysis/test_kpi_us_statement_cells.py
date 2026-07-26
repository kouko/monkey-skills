"""Tests for analysis-kpi/scripts/kpi_us_statement_cells.py — typing every
cell of a reconstructed statement (plan Task 5),
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md.

`cell_state` answers, for one (statement kind, concept, period), which of four
things the cell is: a reported `value`, `not_presented` (the filer's statement
has no such line), `not_tagged` (the line exists, that period carries no
undimensioned value) or `derived` (not separately tagged, but computable from
the filer's OWN arithmetic). The whole point is that the last three are three
DIFFERENT facts that today all render as one blank, so a reader cannot tell a
pipeline defect from an accounting fact.

FIXTURE PROVENANCE, stated per fixture and never in bulk:

  OBSERVED   — read from the committed live capture
               `tests/data/fixtures/us_statement_reconstruction_2026-07-26.json`
               (five 10-K filings, verbatim `XBRL.get_statement` rows; only KO
               FY2017 and IBM FY2025 were captured WITH rows, the other three
               census-only, so every observed fixture here is one of those two).
  CONSTRUCTED-CONVENTIONAL — NOT observed. Balance-sheet rows written by hand
               to exercise a branch no captured filing reaches. Each one says
               at its own site which branch, and why no observed filing covers
               it. All of them are in the clearly marked section at the bottom.

The suite makes no network call: every row is already on disk or written here.

No `@req` tags: this dispatch carries no registered loom-spec REQ-ids (the work
is tracked by named plan Task 5), so `@req` is omitted per the implementer
contract.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from decimal import Decimal
from types import SimpleNamespace

import pytest
from conftest import SKILLS

CELLS_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_cells.py"
STATEMENT_SHAPE_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_shape.py"

KO_FY2017 = "0000021344-18-000008"
IBM_FY2025 = "0000051143-26-000010"


def _load(name: str, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def cells():
    return _load("kpi_us_statement_cells_test", CELLS_SCRIPT)


@pytest.fixture(scope="module")
def shape():
    """Task 3's assembly. Read here rather than hand-building `Line` objects so
    the cells under test are the ones the real reconstruction produces."""
    return _load("kpi_us_statement_shape_for_cells_test", STATEMENT_SHAPE_SCRIPT)


@pytest.fixture(scope="module")
def capture():
    fixture = (
        SKILLS.parent / "tests" / "data" / "fixtures"
        / "us_statement_reconstruction_2026-07-26.json"
    )
    return json.loads(fixture.read_text(encoding="utf-8"))


class _CapturedFiling:
    """A `Filing` whose `.xbrl()` serves captured rows — the two-call surface
    (`presentation_roles`, `get_statement`) that is assembly's whole input
    contract.

    A near-twin of `test_kpi_us_statement_shape.py`'s double, and the
    duplication is deliberate rather than overlooked: promoting it to
    `conftest.py` would edit a third file, and this task's dispatch confines it
    to two. If a third suite needs it, that is the moment to promote it — the
    Rule of Three, not before.
    """

    def __init__(self, filing_entry: dict):
        self._rows_by_role = {
            entry["role"]: entry["rows"]
            for entry in filing_entry["roles_captured"]
            if entry.get("rows") is not None
        }
        self.presentation_roles = list(filing_entry["presentation_roles"])

    def xbrl(self):
        return self

    def get_statement(self, role: str) -> list[dict]:
        return self._rows_by_role[role]


def _statements(shape, capture, accession: str):
    for filing in capture["filings"]:
        if filing["accession"] == accession:
            return shape.statements_for(_CapturedFiling(filing))
    raise AssertionError(f"accession {accession} is not in the capture")


@pytest.fixture(scope="module")
def ko_fy2017(shape, capture):
    return _statements(shape, capture, KO_FY2017)


@pytest.fixture(scope="module")
def ibm_fy2025(shape, capture):
    return _statements(shape, capture, IBM_FY2025)


# --- the RED test: the whole-equity trap ------------------------------------


def test_derived_total_liabilities_subtracts_whole_equity(cells, ko_fy2017):
    """The plan's RED for Task 5, on an OBSERVED filer.

    KO's FY2017 balance sheet tags `LiabilitiesAndStockholdersEquity` but NO
    total `Liabilities` line — exactly the 21-of-21 derivable shape the plan
    names — and its equity chain resolves to PARENT-ONLY
    `us-gaap_StockholdersEquity` (17,072M) beside a NON-ZERO
    `us-gaap_MinorityInterest` (1,905M). So the two candidate answers differ by
    the whole non-controlling interest:

        whole equity   87,896 - (17,072 + 1,905) = 68,919M   <- correct
        parent-only    87,896 -  17,072          = 70,824M   <- 1,905M of
                                                                minority
                                                                interest
                                                                relabelled as
                                                                a liability

    Both are plausible numbers wearing a correct-looking label, which is why
    this is the task's RED: nothing downstream can tell them apart.

    Asserting the wrong answer is NOT returned, as well as the right one, is
    deliberate — an assertion that only pins the right value would still pass
    if some future change made the right value arrive by luck from a different
    route. MUTATION-VERIFIED 2026-07-26: substituting the parent-only figure
    in `_derive_total_liabilities` fails this test on the 70,824M line, run
    rather than reasoned about.
    """
    cell = cells.cell_state(
        ko_fy2017, "balance_sheet", "us-gaap:Liabilities", "instant_2017-12-31",
    )

    assert cell.state == "derived"
    assert cell.value == Decimal("68919000000")
    assert cell.value != Decimal("70824000000"), (
        "parent-only StockholdersEquity was subtracted: the minority interest "
        "is now being reported as a liability"
    )


# --- the plan's GREEN: four states a consumer can tell apart -----------------


def test_the_four_states_are_distinguishable_by_a_consumer(cells, ko_fy2017, ibm_fy2025):
    """The plan's GREEN, as one assertion: four cells that all render as a
    number-or-blank today must come back as four DIFFERENT states.

    Every one is OBSERVED — three from KO's FY2017 balance sheet, one from
    IBM's FY2025 income statement. This is the test that would fail if any
    future change collapsed two states into one, which is the whole regression
    this task guards against.
    """
    states = [
        cells.cell_state(
            ko_fy2017, "balance_sheet", "us-gaap:Assets", "instant_2017-12-31",
        ).state,
        cells.cell_state(
            ibm_fy2025, "income", "us-gaap:OperatingIncomeLoss",
            "duration_2025-01-01_2025-12-31",
        ).state,
        cells.cell_state(
            ko_fy2017, "balance_sheet", "us-gaap:MinorityInterest",
            "instant_2015-12-31",
        ).state,
        cells.cell_state(
            ko_fy2017, "balance_sheet", "us-gaap:Liabilities", "instant_2017-12-31",
        ).state,
    ]

    assert states == ["value", "not_presented", "not_tagged", "derived"]


def test_a_line_the_filer_never_presents_is_not_presented(cells, ibm_fy2025):
    """IBM's FY2025 income statement declares NO operating income: it runs
    revenue -> cost -> gross profit -> expenses -> income from continuing
    operations before income taxes. OBSERVED in the committed capture.

    NOT the oil major the plan's GREEN names. No oil major is reachable
    offline — of the five captured filings only KO FY2017 and IBM FY2025 were
    captured with rows — so this pins the same structural fact (a filer whose
    statement genuinely has no operating-income line) on the filer that is
    actually observable here. Stated rather than dressed up as the plan's
    example, because "an oil major" is a claim about a filing nobody in this
    suite has read.

    The two guards below matter as much as the state itself: the statement is
    non-empty and it DOES carry the neighbouring subtotal, so `not_presented`
    is the filer's presentation and not our reconstruction having failed.
    """
    income = ibm_fy2025.by_kind["income"]
    assert len(income) > 10
    assert any(line.concept == "us-gaap_GrossProfit" for line in income)
    assert not any(line.concept == "us-gaap_OperatingIncomeLoss" for line in income)

    cell = cells.cell_state(
        ibm_fy2025, "income", "us-gaap:OperatingIncomeLoss",
        "duration_2025-01-01_2025-12-31",
    )

    assert cell.state == "not_presented"
    assert cell.value is None and cell.derivation is None


def test_a_presented_line_with_no_value_for_that_period_is_not_tagged(cells, ko_fy2017):
    """KO PRESENTS `us-gaap_MinorityInterest` on its FY2017 balance sheet and
    tags it at two instants; the equity block reaches back to 2015-12-31, where
    it carries nothing. OBSERVED.

    That is a different fact from IBM's missing operating income and must not
    render the same way: the line is there, the filer simply reported no
    undimensioned figure for that instant. The 2017 assertion is the control —
    the SAME concept on the SAME statement is a plain `value` one instant
    later, so `not_tagged` cannot be this concept being mishandled wholesale.
    """
    absent = cells.cell_state(
        ko_fy2017, "balance_sheet", "us-gaap:MinorityInterest", "instant_2015-12-31",
    )
    present = cells.cell_state(
        ko_fy2017, "balance_sheet", "us-gaap:MinorityInterest", "instant_2017-12-31",
    )

    assert absent.state == "not_tagged"
    assert absent.value is None
    assert present.state == "value"
    assert present.value == Decimal("1905000000")


def test_a_derived_cell_names_the_arithmetic_that_produced_it(cells, ko_fy2017):
    """The plan's GREEN, second half: "every `derived` cell names the
    arithmetic that produced it". A derived number a reader cannot reproduce is
    the same opaque blank in a different costume.

    Reproducing it here from `terms` alone, rather than reading the formula
    string, is the point: the provenance has to be USABLE, not decorative.
    The mezzanine term is present at 0 because KO tags no temporary equity —
    the assumption a reader most needs to be able to challenge is the one that
    was made silently, so it is not omitted.
    """
    cell = cells.cell_state(
        ko_fy2017, "balance_sheet", "us-gaap:Liabilities", "instant_2017-12-31",
    )

    terms = dict(cell.derivation.terms)
    assert terms == {
        "us-gaap:LiabilitiesAndStockholdersEquity": Decimal("87896000000"),
        "us-gaap:StockholdersEquity": Decimal("17072000000"),
        "us-gaap:MinorityInterest": Decimal("1905000000"),
        "us-gaap:TemporaryEquityCarryingAmountIncludingPortionAttributableTo"
        "NoncontrollingInterests": Decimal("0"),
    }
    footing, *subtracted = cell.derivation.terms
    assert footing[1] - sum(amount for _, amount in subtracted) == cell.value
    assert cell.derivation.formula.startswith(
        "us-gaap:Liabilities = us-gaap:LiabilitiesAndStockholdersEquity - "
    )
    assert "us-gaap:StockholdersEquity" in cell.derivation.formula


def test_a_filer_reported_value_is_never_replaced_by_a_derivation(cells, ibm_fy2025):
    """The precedence `cell_state` documents — a tagged value wins over a
    derivation — pinned on the ONE observed filing where the two disagree.

    IBM's FY2025 balance sheet tags `Liabilities` at 2024-12-31 as
    109,783,000,000 while the same statement's footing arithmetic
    (137,175 - 27,307 - 86, all in millions) yields 109,782,000,000. One
    million apart: not enough to look wrong anywhere downstream, which is
    exactly why it has to be pinned. The filer's own reported figure is the
    artifact this arc exists to preserve, and a derived stand-in for it would
    be a plausible wrong number wearing the filer's label.

    UNPINNED UNTIL NOW, and found by a reviewer running the mutation rather
    than arguing it: reordering `cell_state` so `_derive` ran BEFORE the
    tagged-value check left all eleven of the suite's other tests green,
    because every other derived cell in the suite is one no filer tagged. A
    precedence rule no test exercises is a comment, not a rule.

    `derivation is None` is asserted beside the state because that is the half
    a consumer branches on: a `value` cell carrying provenance would mean the
    number had been recomputed, which is the same defect one layer down.
    """
    liabilities = next(
        line for line in ibm_fy2025.by_kind["balance_sheet"]
        if line.concept == "us-gaap_Liabilities"
    )
    assert liabilities.values["instant_2024-12-31"] == 109783000000.0

    cell = cells.cell_state(
        ibm_fy2025, "balance_sheet", "us-gaap:Liabilities", "instant_2024-12-31",
    )

    assert cell.state == "value"
    assert cell.value == Decimal("109783000000")
    assert cell.derivation is None
    assert cell.value != Decimal("109782000000"), (
        "the derivation replaced the figure IBM itself reported"
    )


def test_an_unknown_statement_kind_fails_loud(cells, ko_fy2017):
    """A typo'd kind must RAISE, not answer `not_presented`. Answering would
    return the very undifferentiated blank this module exists to abolish, and
    it would be indistinguishable from a filer that files no such statement.
    """
    with pytest.raises(ValueError, match="not a statement kind"):
        cells.cell_state(
            ko_fy2017, "balance-sheet", "us-gaap:Assets", "instant_2017-12-31",
        )


# --- CONSTRUCTED-CONVENTIONAL fixtures --------------------------------------
#
# Everything below this fence is written by hand, NOT observed. Each test says
# which branch it reaches and why no captured filing reaches it. They are
# balance sheets in the shape `statements_for` produces, built from Task 3's
# own `Line` so a change to that dataclass breaks them rather than letting them
# drift into testing a shape the reconstruction no longer emits.


def _balance_sheet(shape, period: str, concept_values: dict):
    """A one-period constructed balance sheet, as `cell_state` consumes it.

    `by_kind` is the whole input contract (module docstring), so a namespace
    carrying it is a complete stand-in — the same reason Task 3's suite can
    drive assembly from a two-method double.

    A MAPPING rather than `**kwargs`: `TemporaryEquityCarryingAmountIncluding
    PortionAttributableToNoncontrollingInterests` is 85 characters and a
    keyword cannot be split across lines, while a dict key can be written as
    two adjacent string literals.
    """
    lines = [
        shape.Line(
            label=concept, concept=f"us-gaap_{concept}", level=1,
            weight=None, calculation_parent=None, values={period: value},
        )
        for concept, value in concept_values.items()
    ]
    return SimpleNamespace(by_kind={"balance_sheet": lines})


def test_a_custom_concept_keeps_the_underscores_after_its_namespace(cells, shape):
    """CONSTRUCTED-CONVENTIONAL: a filer's own concept carrying underscores in
    its LOCAL name. Unobserved — every custom concept in the capture
    (`ko_UnusualOrInfrequentItemOperating`, `ibm_OtherExpenseAndIncome`) is
    single-underscore CamelCase.

    `_store_qname` folds only the FIRST separator, and its docstring says so.
    Rewriting it as `concept.replace("_", ":")` passes every other test in this
    suite because nothing else distinguishes them — so this pins the claim
    rather than leaving a docstring nobody can break. Under replace-all the
    lookup below yields `ibm:Segment:Revenue:Adjustment` and the line is never
    found, which would report a line the filer DOES present as
    `not_presented`: the taxonomy's worst answer, since it blames the filer for
    our own name handling.
    """
    line = shape.Line(
        label="Segment revenue adjustment", concept="ibm_Segment_Revenue_Adjustment",
        level=1, weight=None, calculation_parent=None,
        values={"duration_2025-01-01_2025-12-31": 12.0},
    )
    statements = SimpleNamespace(by_kind={"income": [line]})

    cell = cells.cell_state(
        statements, "income", "ibm:Segment_Revenue_Adjustment",
        "duration_2025-01-01_2025-12-31",
    )

    assert cell.state == "value"
    assert cell.value == Decimal("12")


def test_derived_arithmetic_is_decimal_not_binary_float(cells, shape):
    """CONSTRUCTED-CONVENTIONAL, and the magnitudes are deliberately NOT a real
    filer's: every captured filing reports whole dollars, where binary float is
    exact, so a fixture that can FAIL when the arithmetic is written in float
    has to be built rather than found.

    226,246.96 - 14,639.91 - 505.95 is exactly 211,101.10 in decimal and
    211,101.09999999998 in binary float. The arc has already shipped a false
    restatement signal from precisely this class
    (docs/loom/memory/construction-guaranteed-invariant-proves-nothing.md,
    `1.005 x 1e9`), and that entry's own conclusion is that a green suite over
    float-FRIENDLY values proves nothing — hence the second assertion, which
    fails if a later edit makes these numbers float-exact and quietly disarms
    the first.
    """
    statements = _balance_sheet(shape, "instant_2025-12-31", {
        "LiabilitiesAndStockholdersEquity": 226246.96,
        "StockholdersEquity": 14639.91,
        "MinorityInterest": 505.95,
    })

    cell = cells.cell_state(
        statements, "balance_sheet", "us-gaap:Liabilities", "instant_2025-12-31",
    )

    assert cell.state == "derived"
    assert cell.value == Decimal("211101.10")
    assert (226246.96 - 14639.91) - 505.95 != 211101.10, (
        "these values are no longer float-hostile, so this test can no longer "
        "fail on a float implementation and proves nothing"
    )


def test_an_incl_nci_equity_total_is_not_double_counted(cells, shape):
    """CONSTRUCTED-CONVENTIONAL: a filer whose ONLY equity total is the
    including-NCI concept, beside a separately tagged `MinorityInterest`.
    Unobserved here — KO tags BOTH totals, and IBM tags a `Liabilities` line so
    nothing is derived for it at all.

    This is the OTHER half of the whole-equity trap, and it fails in the
    opposite direction from the RED: the interest is ALREADY inside the
    including-NCI total, so adding it again would understate liabilities by
    400. Naming the exception in the same breath as the rule is the arc's
    standing discipline — "subtract whole equity" is not "always add the
    minority interest".
    """
    statements = _balance_sheet(shape, "instant_2025-12-31", {
        "LiabilitiesAndStockholdersEquity": 10000.0,
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest":
            3000.0,
        "MinorityInterest": 400.0,
    })

    cell = cells.cell_state(
        statements, "balance_sheet", "us-gaap:Liabilities", "instant_2025-12-31",
    )

    assert cell.state == "derived"
    assert cell.value == Decimal("7000")
    assert "us-gaap:MinorityInterest" not in dict(cell.derivation.terms), (
        "the interest is inside the including-NCI total; listing it as a term "
        "would claim it was subtracted twice"
    )


def test_a_mezzanine_is_not_left_inside_the_derived_liabilities(cells, shape):
    """CONSTRUCTED-CONVENTIONAL: no captured filing tags either mezzanine
    concept, so this branch cannot be observed in this suite.

    Temporary equity is presented BETWEEN liabilities and equity, so a
    `Liabilities` subtotal excludes it; leaving it in the remainder relabels
    600 of redeemable stock as debt — the same class of error as the RED's
    minority interest, by a different term. `kpi_spine_view`'s header records
    TSLA's entire balance-sheet residual being exactly its redeemable
    non-controlling interest, to the dollar, which is why the term is carried
    rather than dropped as unpinned.
    """
    statements = _balance_sheet(shape, "instant_2025-12-31", {
        "LiabilitiesAndStockholdersEquity": 10000.0,
        "StockholdersEquity": 3000.0,
        "MinorityInterest": 400.0,
        "TemporaryEquityCarryingAmountIncludingPortionAttributableTo"
        "NoncontrollingInterests": 600.0,
    })

    cell = cells.cell_state(
        statements, "balance_sheet", "us-gaap:Liabilities", "instant_2025-12-31",
    )

    assert cell.value == Decimal("6000")


def test_a_derived_term_names_the_concept_the_filer_actually_tagged(cells, shape):
    """CONSTRUCTED-CONVENTIONAL: a filer tagging the mezzanine chain's SECOND
    concept, `RedeemableNoncontrollingInterestEquityCarryingAmount`. Unobserved
    — no captured filing tags either.

    Provenance that names a concept the filer never used is provenance a reader
    cannot check against the filing, which is the whole value of carrying it.
    Found by self-review, not by a reviewer: the first version of this module
    labelled the term with the chain's FIRST concept whatever was read, so this
    filer's derivation would have cited a `TemporaryEquity...` line that does
    not exist on its balance sheet — a wrong provenance on a right number, and
    the only cell that lets a reader audit the arithmetic at all.
    """
    statements = _balance_sheet(shape, "instant_2025-12-31", {
        "LiabilitiesAndStockholdersEquity": 10000.0,
        "StockholdersEquity": 3000.0,
        "MinorityInterest": 400.0,
        "RedeemableNoncontrollingInterestEquityCarryingAmount": 600.0,
    })

    cell = cells.cell_state(
        statements, "balance_sheet", "us-gaap:Liabilities", "instant_2025-12-31",
    )

    assert cell.value == Decimal("6000")
    terms = dict(cell.derivation.terms)
    assert terms["us-gaap:RedeemableNoncontrollingInterestEquityCarryingAmount"] == (
        Decimal("600")
    )
    assert not any("TemporaryEquity" in name for name in terms), (
        "the derivation cites a mezzanine concept this filer never tagged"
    )


def test_an_asserted_but_untagged_minority_interest_is_not_derived(cells, shape):
    """CONSTRUCTED-CONVENTIONAL: a filer tagging BOTH equity totals but no
    `MinorityInterest` amount. Unobserved — KO tags all three.

    Tagging both totals ASSERTS a non-controlling interest exists: it is the
    line between the two subtotals. So its absence is a MISSING AMOUNT, not a
    zero, and reading it as zero would emit 7,000 when the true liabilities are
    smaller by the interest — a wrong number wearing a `derived` label, which
    is worse than an honest blank. `kpi_spine_view._minority_interest_term`
    owns this exception and this test proves it survives the reuse.

    The state is `not_presented` because this filer presents no total
    liabilities line either; what the test pins is that it is NOT `derived`.
    """
    statements = _balance_sheet(shape, "instant_2025-12-31", {
        "LiabilitiesAndStockholdersEquity": 10000.0,
        "StockholdersEquity": 3000.0,
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest":
            3400.0,
    })

    cell = cells.cell_state(
        statements, "balance_sheet", "us-gaap:Liabilities", "instant_2025-12-31",
    )

    assert cell.state == "not_presented"
    assert cell.value is None and cell.derivation is None
