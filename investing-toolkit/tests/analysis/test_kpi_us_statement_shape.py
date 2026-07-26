"""Tests for analysis-kpi/scripts/kpi_us_statement_shape.py — role -> statement
kind classification (plan Task 2) and, in the section so headed at the bottom,
assembly of one filing's three statements (plan Task 3),
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md.

`statement_kind(role)` classifies ONE XBRL presentation/calculation role URI
as `"income"` / `"balance_sheet"` / `"cash_flow"`, or `None`. `None` is a
first-class honest answer, not a failure: a filing carries 14-132 roles, most
of them notes, and a MIS-classified role is the expensive outcome — cash-flow
lines landing in the income statement render as plausible lines and silently
fail every downstream arithmetic check.

FIXTURE PROVENANCE, stated per fixture and never in bulk. Every role URI below
carries one of three markers, because an earlier revision of this suite claimed
all of them were observed when most were invented:

  OBSERVED   — fetched live from the filer's 10-K on 2026-07-26.
  COMMITTED  — read from a committed fixture; the file is named at the fixture.
  CONSTRUCTED-CONVENTIONAL — NOT observed. A role URI written to the filer's
               conventional naming, used only where no observed role exercises
               the rule under test. Every one is confined to the clearly
               marked section at the bottom of this module.

The suite makes no network call: the Task 2 fixtures are string literals, and
the Task 3 section reads rows from a committed capture on disk.

WHAT THE 2026-07-26 MEASUREMENT ACTUALLY SHOWED. The combined
income-and-comprehensive-income statement is real, and dropping every role that
mentions comprehensive income does erase such a filer's income statement — but
among the filers checked only Realty Income (O) files it that way. Colgate,
Costco and Microsoft each file income and comprehensive income as SEPARATE
roles. An earlier docstring here named six filers as combined; that was an
inference, not a measurement, and it was wrong.

No `@req` tags: this dispatch carries no registered loom-spec REQ-ids (the
work is tracked by named plan Task 2), so `@req` is omitted per the
implementer contract.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter

import pytest
from conftest import SKILLS

STATEMENT_SHAPE_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_shape.py"
STATEMENT_LINES_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_lines.py"


def _load(name: str, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def shape():
    return _load("kpi_us_statement_shape_test", STATEMENT_SHAPE_SCRIPT)


@pytest.fixture(scope="module")
def lines():
    """Task 1's predicate, which Task 3's assembly composes."""
    return _load("kpi_us_statement_lines_test", STATEMENT_LINES_SCRIPT)


# --- the RED test: the measured trap ---------------------------------------


def test_combined_income_and_comprehensive_role_is_still_income(shape):
    """Realty Income files ONE statement of income and comprehensive income.
    Dropping the role because it mentions comprehensive income leaves that
    filer with no income statement at all — the trap this module exists to
    avoid. OBSERVED 2026-07-26.
    """
    assert shape.statement_kind(
        "http://www.realtyincome.com/role/ConsolidatedStatementsOfIncomeAndComprehensiveIncome"
    ) == "income"


def test_comprehensive_income_only_role_is_not_an_income_statement(shape):
    """The other half of the trap: the fix for the combined role must not swing
    into accepting a comprehensive-income-ONLY role, which is a fourth
    statement and out of scope for this arc. Both OBSERVED 2026-07-26 — and
    both filers ALSO file a separate income statement (pinned below), which is
    what makes the pair meaningful.
    """
    assert shape.statement_kind(
        "http://www.duke-energy.com/role/ConsolidatedStatementsOfComprehensiveIncome"
    ) is None
    assert shape.statement_kind(
        "http://www.microsoft.com/20190630/taxonomy/role/StatementCOMPREHENSIVEINCOMESTATEMENTS"
    ) is None


# --- the three kinds classify from real role URIs ---------------------------


@pytest.mark.parametrize(
    "role",
    [
        # OBSERVED 2026-07-26.
        "http://www.duke-energy.com/role/ConsolidatedStatementsOfOperations",
        "http://www.jpmorganchase.com/role/ConsolidatedStatementsOfIncome",
        "http://www.colgate.com/role/ConsolidatedStatementsOfIncome",
        "http://www.costco.com/role/ConsolidatedStatementsOfIncome",
        # OBSERVED 2026-07-26 — Caterpillar names it with no "statement" word
        # at all, which is why the bare "results of operations" wording has to
        # stand on its own.
        "http://www.cat.com/role/ConsolidatedResultsOfOperations",
        # OBSERVED 2026-07-26 — Microsoft's Statement<ALLCAPS> dialect, noun
        # first and the word "statement" on both ends.
        "http://www.microsoft.com/20190630/taxonomy/role/StatementINCOMESTATEMENTS",
        # OBSERVED 2026-07-26 — IBM titles its income statement "Statement of
        # Earnings"; the sole support for the "earnings" wording.
        "http://www.ibm.com/role/StatementConsolidatedStatementOfEarnings",
        # COMMITTED: xbrl_multifiling_aapl.json, both casings Apple files.
        "http://www.apple.com/role/ConsolidatedStatementsOfOperations",
        "http://www.apple.com/role/CONSOLIDATEDSTATEMENTSOFOPERATIONS",
        # COMMITTED: xbrl_quarterly_nvda_range.json.
        "http://www.nvidia.com/role/CondensedConsolidatedStatementsofIncome",
    ],
)
def test_income_roles_classify_as_income(shape, role):
    assert shape.statement_kind(role) == "income"


@pytest.mark.parametrize(
    "role",
    [
        # OBSERVED 2026-07-26 — three filers, one spelling.
        "http://www.duke-energy.com/role/ConsolidatedBalanceSheets",
        "http://www.jpmorganchase.com/role/ConsolidatedBalanceSheets",
        "http://www.colgate.com/role/ConsolidatedBalanceSheets",
        # OBSERVED 2026-07-26 — the IFRS-style title, with and without the
        # word "statement".
        "http://www.cat.com/role/ConsolidatedFinancialPosition",
        "http://www.ibm.com/role/StatementConsolidatedStatementOfFinancialPosition",
        # OBSERVED 2026-07-26.
        "http://www.microsoft.com/20190630/taxonomy/role/StatementBALANCESHEETS",
    ],
)
def test_balance_sheet_roles_classify_as_balance_sheet(shape, role):
    assert shape.statement_kind(role) == "balance_sheet"


@pytest.mark.parametrize(
    "role",
    [
        # OBSERVED 2026-07-26. Caterpillar singularises both "Statement" and
        # "Flow"; IBM prefixes the segment with a second "Statement".
        "http://www.duke-energy.com/role/ConsolidatedStatementsOfCashFlows",
        "http://www.cat.com/role/ConsolidatedStatementOfCashFlow",
        "http://www.ibm.com/role/StatementConsolidatedStatementOfCashFlows",
    ],
)
def test_cash_flow_roles_classify_as_cash_flow(shape, role):
    assert shape.statement_kind(role) == "cash_flow"


# --- the two-tier gate, pinned in BOTH directions ---------------------------


@pytest.mark.parametrize(
    "role",
    [
        # OBSERVED 2026-07-26.
        "http://www.duke-energy.com/role/ConsolidatedBalanceSheets",
        "http://www.cat.com/role/ConsolidatedFinancialPosition",
    ],
)
def test_balance_sheet_wording_stands_without_the_word_statement(shape, role):
    """Balance-sheet roles mostly carry NO "statement" word, so requiring one
    for this kind would reject the majority of real balance sheets. The
    assertion on the URI is the load-bearing half: it fails loudly if someone
    later swaps in a fixture that happens to contain "statement" and thereby
    lets a gate be added unnoticed.
    """
    assert "statement" not in role.lower()
    assert shape.statement_kind(role) == "balance_sheet"


# --- note and out-of-scope roles return None --------------------------------


@pytest.mark.parametrize(
    "role",
    [
        # OBSERVED 2026-07-26 — Colgate's supplemental NOTE roles repeat the
        # statement's own words. Without a "supplemental" rejection these
        # classify as balance_sheet and income: the WRONG-KIND direction.
        "http://www.colgate.com/role/SupplementalBalanceSheetInformation",
        "http://www.colgate.com/role/SupplementalIncomeStatementInformation",
        "http://www.colgate.com/role/SupplementalIncomeStatementInformationDetails",
        "http://www.realtyincome.com/role/SupplementalDisclosuresOfCashFlowInformation",
        # OBSERVED 2026-07-26 — says "balance sheet" while being a note.
        "http://www.jpmorganchase.com/role/OffBalanceSheetLendingRelatedFinancialInstrumentsGuaranteesAndOtherCommitments",
        # OBSERVED 2026-07-26 — three note roles that quote a statement's full
        # title. Each classifies as a statement without a "details" rejection.
        "http://www.jpmorganchase.com/role/BasisOfPresentationImpactOnConsolidatedStatementsOfIncomeDetails",
        "http://www.jpmorganchase.com/role/DerivativeInstrumentsImpactOnStatementsOfIncomeCashFlowHedgesDetails",
        "http://www.duke-energy.com/role/AcquisitionsAndDispositionsCashFlowStatementDetails",
        # OBSERVED 2026-07-26 — IBM prefixes 163 of its 171 roles `Disclosure`.
        # Exactly these three quote a statement title, one per kind, and all
        # three end in `Details`. They are why the `Disclosure` prefix itself
        # needs no rejection rule: the suffix already carries the roles that
        # would otherwise misclassify, one for each of the three kinds.
        "http://www.ibm.com/role/DisclosureRevenueTransitionDisclosuresStatementOfCashFlowsDetails",
        "http://www.ibm.com/role/DisclosureRevenueTransitionDisclosuresStatementOfEarningsDetails",
        "http://www.ibm.com/role/DisclosureRevenueTransitionDisclosuresStatementOfFinancialPositionDetails",
        # OBSERVED 2026-07-26 — two more cash-flow-titled note roles.
        "http://www.jpmorganchase.com/role/ParentCompanyStatementsOfCashFlowsDetails",
        "http://www.duke-energy.com/role/VariableInterestEntitiesSalesAndCashFlowsDetails",
        # OBSERVED 2026-07-26 — a parenthetical repeats its statement's title
        # verbatim, in two dialects: Duke's `Consolidated...` and Microsoft's
        # all-caps form. Each carries no other marker, so each pins
        # `parenthetical` on its own.
        "http://www.duke-energy.com/role/ConsolidatedStatementsOfOperationsParenthetical",
        "http://www.microsoft.com/20190630/taxonomy/role/StatementBALANCESHEETSParenthetical",
        # OBSERVED 2026-07-26 — JOINT COVERAGE, NOT AN ISOLATED PIN: this role
        # carries BOTH `supplemental` and `tables`, so it returns None even if
        # `tables` were deleted. It is here as evidence that ...Tables note
        # roles quoting a statement's wording are real; it does not prove
        # `tables` is independently required. See that marker's comment in the
        # module for why it is kept anyway.
        "http://www.colgate.com/role/SupplementalIncomeStatementInformationTables",
    ],
)
def test_note_roles_quoting_a_statement_title_are_not_statements(shape, role):
    assert shape.statement_kind(role) is None


def test_singular_detail_suffix_is_rejected_like_the_plural(shape):
    """Microsoft spells the suffix `Detail`, IBM spells it `Details`. OBSERVED
    2026-07-26. Before the marker was changed to the singular stem this role
    escaped the rejection entirely and returned `None` only because it happens
    to carry no "statement" word — a second line of defence, not the intended
    one. The wrong-kind case that exposed it is pinned below.
    """
    assert shape.statement_kind(
        "http://www.microsoft.com/20190630/taxonomy/role/DisclosureGainsLossesRelatedToCashFlowHedgesDetail"
    ) is None


def test_statement_of_equity_is_not_one_of_the_three(shape):
    """A real statement, but the fourth one — out of scope for this arc.

    OBSERVED 2026-07-26. This fixture also pins that only the role's LAST path
    segment is read: the filer's domain is `realtyincome.com`, so a classifier
    matching against the whole URI would find "income" here and mis-serve a
    statement of equity as the income statement.
    """
    role = "http://www.realtyincome.com/role/ConsolidatedStatementsOfEquity"
    assert "income" in role.lower()
    assert shape.statement_kind(role) is None


@pytest.mark.parametrize(
    "role",
    [
        # COMMITTED: xbrl_multifiling_aapl.json, xbrl_quarterly_nvda_range.json.
        # Every filing carries a cover role; it names no statement and so needs
        # no rejection rule to fall through to None.
        "http://www.apple.com/role/CoverPage",
        "http://www.nvidia.com/role/Cover",
    ],
)
def test_unrecognised_roles_return_none_rather_than_a_guess(shape, role):
    assert shape.statement_kind(role) is None


# --- Task 3: assembling one filing's three statements -----------------------
#
# Everything below in this section reads ONE committed fixture,
# `us_statement_reconstruction_2026-07-26.json` — a verbatim capture of
# `XBRL.get_statement(role)` for five 10-K filings across two eras, regenerated
# by `capture_us_statement_reconstruction.py` beside it. COMMITTED, and the
# provenance of every filing is in the fixture's own `_capture` block. No
# network call: the rows are already on disk.


@pytest.fixture(scope="module")
def reconstruction_capture():
    fixture = (
        SKILLS.parent / "tests" / "data" / "fixtures"
        / "us_statement_reconstruction_2026-07-26.json"
    )
    return json.loads(fixture.read_text(encoding="utf-8"))


def _captured_filing(capture, accession: str) -> dict:
    for filing in capture["filings"]:
        if filing["accession"] == accession:
            return filing
    raise AssertionError(f"accession {accession} is not in the capture")


def _captured_rows(shape, capture, accession: str, kind: str) -> list[dict]:
    """The captured rows of the one role that classifies as `kind`.

    The kind is RE-DERIVED here by running the live classifier over the
    captured role URIs. The fixture stores no kind of its own: a stored one
    would be this classifier's verdict frozen at capture time, and a test
    reading it back would keep agreeing with a classifier that had since
    regressed.
    """
    filing = _captured_filing(capture, accession)
    entries = [
        entry for entry in filing["roles_captured"]
        if shape.statement_kind(entry["role"]) == kind
    ]
    assert len(entries) == 1, (
        f"{filing['ticker']} {accession} has {len(entries)} roles classifying "
        f"as {kind}; this helper assumes one and the caller must choose"
    )
    assert entries[0].get("rows") is not None, (
        f"{accession} was captured census-only; re-run the capture script with "
        "with_rows=True for this filing"
    )
    return entries[0]["rows"]


class _CapturedXBRL:
    """The two-attribute slice of `edgar.xbrl.XBRL` that assembly reads.

    Assembly needs a filing's whole role set (to choose among roles) and the
    rows of a chosen role. Everything else edgartools exposes is irrelevant to
    it, so the double offers exactly those two and nothing else: a call to any
    other attribute is an AttributeError here, which is the point — it fails
    loudly rather than letting the offline suite drift away from the live
    surface it stands in for.

    `presentation_roles` is the filing's FULL list — 93 roles for KO, 172 for
    IBM — not just the three that were worth capturing rows for. So the
    offline suite makes assembly reject ~90-170 REAL note roles per filing,
    which is the half of role selection a capture of accepted roles only would
    never have exercised.

    `get_statement` raises `KeyError` for a role whose rows were not captured,
    but that guard is PARTIAL and the limit is worth stating: it fires only
    when a newly-accepted role is the one selection actually picks. Simulated
    against a classifier regressed into accepting KO's income PARENTHETICAL
    role, assembly stayed silent — the real role won the tie-break, so the
    uncaptured one was never fetched. What catches that regression is
    `test_a_filing_declares_one_role_per_kind_in_the_captured_sample`, which
    classifies EVERY role rather than only the selected one; the same
    simulation trips it (income: 2). This one is a backstop, not the guard.
    """

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
    """A `Filing` whose `.xbrl()` serves captured rows. Assembly is specified
    as a pure function of the filing (plan ## Notes kickoff decision: the
    reconstruction is recomputed, never persisted), so a filing that answers
    `.xbrl()` is the whole input contract."""

    def __init__(self, filing_entry: dict):
        self.accession_no = filing_entry["accession"]
        self._xbrl = _CapturedXBRL(filing_entry)

    def xbrl(self):
        return self._xbrl


def test_a_consolidated_line_with_dimensioned_children_is_a_statement_line(
    shape, lines, reconstruction_capture,
):
    """RE-CONFIRMING THE LIVE ROW SHAPE (plan Decision Log, 2026-07-26,
    Task 1 -> Task 3 item 2), which is Task 3's obligation precisely because
    inheriting Task 1's presumption untested is what the Decision Log forbids.

    KO's FY2017 income role carries FOUR keys whose names contain "dim", and
    they do not all mean the same thing about the row carrying them:

      is_dimension / full_dimension_label / dimension_metadata
          this row IS a segment slice — `"Asia Pacific"`, 49 of the 80 rows.
      has_dimension_children
          this row is an ORDINARY CONSOLIDATED LINE whose segment slices
          follow it in document order — 10 of the 80 rows, and they are
          `NET OPERATING REVENUES`, `OPERATING INCOME`, `INCOME BEFORE INCOME
          TAXES`, `CONSOLIDATED NET INCOME` and six more like them.

    `is_statement_line` matches the substring "dim" against a row's KEY NAMES,
    so it reads the second group as slices and rejects them. The row asserted
    here is the filing's own top line, value 35,410M for FY2017 — the first of
    the 26 lines the plan's acceptance names, and the one the whole
    reconstruction is read for.

    Measured on the committed capture, not on this filing alone: the same
    over-rejection lands on all five captured filings, all three statements and
    both eras (`n_rows_with_dimensioned_children` per role in the fixture).
    """
    rows = _captured_rows(shape, reconstruction_capture, "0000021344-18-000008", "income")
    top_line = next(
        row for row in rows
        if row["label"] == "NET OPERATING REVENUES"
        and not row.get("full_dimension_label")
    )
    assert top_line["concept"] == "us-gaap_SalesRevenueGoodsNet"
    assert top_line["has_dimension_children"] is True
    assert top_line["values"]["duration_2017-01-01_2017-12-31"] == 35410000000.0
    # It carries no ROW-level dimension signal: nothing about it is a slice.
    assert not any(
        top_line.get(key)
        for key in ("is_dimension", "full_dimension_label", "dimension_metadata")
    )
    assert lines.is_statement_line(top_line) is True


def test_ko_fy2017_income_statement_is_twenty_six_lines(shape, reconstruction_capture):
    """The plan's RED for Task 3: KO's FY2017 income presentation role carries
    80 rows and must reduce to its 26 real statement lines, in presentation
    order, first line labelled "NET OPERATING REVENUES", including the filer's
    OWN custom concept `ko_UnusualOrInfrequentItemOperating` — which no fixed
    concept list could contain and which this design gets for free by reading
    structure rather than names.

    The 26 excludes the abstract header `us-gaap:IncomeStatementAbstract`:
    80 rows less 49 segment slices less the five abstract rows (the section
    header plus the four `Table`/`Axis`/`Domain`/`LineItems` placeholders)
    is exactly 26, which is what the plan's acceptance counts.

    EPS rows carry `weight=None` and `calculation_parent=None` — they
    participate in no declared sum, and that is a property of the filing, not
    an error: they stay as lines and any arithmetic must leave them alone.
    """
    filing = _CapturedFiling(
        _captured_filing(reconstruction_capture, "0000021344-18-000008")
    )
    assert len(filing.xbrl().get_statement(
        "http://www.thecocacolacompany.com/role/ConsolidatedStatementsOfIncome"
    )) == 80

    statements = shape.statements_for(filing)
    income = statements.by_kind["income"]

    assert len(income) == 26
    assert income[0].label == "NET OPERATING REVENUES"
    assert income[0].concept == "us-gaap_SalesRevenueGoodsNet"
    assert income[0].weight == 1.0
    assert income[0].calculation_parent == "us-gaap_GrossProfit"
    assert income[0].values["duration_2017-01-01_2017-12-31"] == 35410000000.0

    concepts = [line.concept for line in income]
    assert "ko_UnusualOrInfrequentItemOperating" in concepts
    assert not any(line.concept == "us-gaap_IncomeStatementAbstract" for line in income)

    eps = next(line for line in income if line.concept == "us-gaap_EarningsPerShareBasic")
    assert eps.weight is None and eps.calculation_parent is None


def test_a_line_carries_the_precision_the_filer_declared(shape, reconstruction_capture):
    """COMMITTED — the `decimals` a filer states per fact must ride on the
    `Line`, because the consumer that needs it cannot get it anywhere else.

    ADDED FOR PLAN TASK 8 (plan Decision Log, "Task 4 -> Task 8"), which is a
    deliberate widening of Task 8's `Files touched` rather than drift. Task 4's
    `verify` compares EXACTLY and therefore reads 24 of its 27 disagreements
    over this same capture out of filers' own rounding residue — a ~8x
    overstatement of broken filer arithmetic. A per-era resolution report built
    on that count would accuse filers of errors they did not make, so the field
    lands here, on Task 3's `Line`, where the row already carries it.

    Two shapes are asserted because they are the two the capture holds:
    KO's FY2017 top line states -6 (rounded to millions) and its EPS row states
    2 (cents). A `Line` that dropped either would leave `verify` unable to tell
    a 3M rounding residue on a millions-rounded group from a 3M error.

    `decimals` is per PERIOD, not per line: the same line may be stated at
    different precisions in different years, and a scalar would silently pick
    one of them.
    """
    filing = _CapturedFiling(
        _captured_filing(reconstruction_capture, "0000021344-18-000008")
    )
    income = shape.statements_for(filing).by_kind["income"]

    top_line = income[0]
    assert top_line.label == "NET OPERATING REVENUES"
    assert top_line.decimals == {
        "duration_2015-01-01_2015-12-31": -6,
        "duration_2016-01-01_2016-12-31": -6,
        "duration_2017-01-01_2017-12-31": -6,
    }

    eps = next(line for line in income if line.concept == "us-gaap_EarningsPerShareBasic")
    assert eps.decimals["duration_2017-01-01_2017-12-31"] == 2, (
        "per-share amounts are stated to the cent, not to the million; a line "
        "that lost this would be checked against the wrong interval"
    )

    # COPIED, not aliased — the same discipline `values` already carries, and
    # for the same reason: a caller mutating the row must not reach the `Line`.
    rows = _captured_rows(shape, reconstruction_capture, "0000021344-18-000008", "income")
    captured = next(
        row for row in rows
        if row["label"] == "NET OPERATING REVENUES" and not row.get("full_dimension_label")
    )
    assert top_line.decimals is not captured["decimals"]


def test_a_line_carries_the_taxonomys_own_debit_credit_balance(
    shape, reconstruction_capture,
):
    """COMMITTED — the US-GAAP taxonomy's own `balance` for each concept must
    ride on the `Line`.

    ADDED FOR PLAN TASK 8, and it is a SECOND widening of that task's
    `Files touched` beyond the `decimals` one the plan amended in — taken on
    measured grounds and flagged rather than slipped in. Task 8 must name the
    income statement's candidate TOTAL revenue concepts, and a concept's local
    name is not enough to tell revenue from cost: IBM presents
    `us-gaap_CostOfRevenue`, whose name carries the revenue wording. The
    filer's declared weight separates them only where the cost line is
    subtracted directly (IBM: -1.0); where it instead rolls POSITIVELY into a
    costs subtotal — the oil-major shape the brief names for PSX — the sign
    says nothing and the cost line reads as a revenue total.

    `balance` is the taxonomy's own answer and is independent of both
    presentation and the filer's weight choices: revenue concepts are `credit`,
    cost and expense concepts are `debit`. MEASURED on the committed capture:
    55 rows carry `credit`, 51 `debit`, and `us-gaap_Revenues` /
    `us-gaap_SalesRevenueGoodsNet` are `credit` while `us-gaap_CostOfRevenue`
    is `debit`.

    `None` IS THE COMMON CASE and must survive as `None`: 349 of the 455
    captured rows carry no balance at all (abstract headers, per-share and
    share-count rows, and concepts the taxonomy does not classify). A consumer
    must therefore read `None` as "the taxonomy says nothing", never as
    "not revenue" — a filer's OWN custom revenue concept is exactly the case
    that would be discarded by the stricter reading, and the brief holds up
    `ko_UnusualOrInfrequentItemOperating` as the thing this design must not
    lose.
    """
    filing = _CapturedFiling(
        _captured_filing(reconstruction_capture, "0000051143-26-000010")
    )
    income = shape.statements_for(filing).by_kind["income"]

    revenue = next(line for line in income if line.concept == "us-gaap_Revenues")
    cost = next(line for line in income if line.concept == "us-gaap_CostOfRevenue")

    assert revenue.balance == "credit"
    assert cost.balance == "debit", (
        "the two concepts whose LOCAL NAMES both carry the revenue wording "
        "must be separable by something the taxonomy states"
    )

    eps = next(
        line for line in income if line.concept == "us-gaap_EarningsPerShareBasic"
    )
    assert eps.balance is None


def test_a_lines_balance_arrives_case_folded_so_no_consumer_decides(shape):
    """`Line.balance` is normalised WHERE THE LINE IS BUILT, so every consumer
    can compare it against the taxonomy's own lower-case spelling and be right.

    THE DEFECT CLASS THIS CLOSES, which this branch has now hit three times. A
    value read from an upstream and compared for equality by each consumer
    separately diverges the moment one of them folds case and the others do
    not: this branch's parent commit `ca9c9e12` fixed exactly that for an
    Axis/Member suffix, and the same shape reappeared here — one consumer
    comparing `line.balance != "debit"` (a `"Debit"` fails OPEN, admitting a
    cost line as a revenue total) against another comparing
    `str(line.balance or "").casefold() == "debit"` (fails CLOSED). Neither
    reading is wrong on its own; holding both is.

    ONLY CASE IS FOLDED. `normalize_balance` does not trim whitespace, does not
    map synonyms, and does not validate the value against `debit`/`credit` — a
    spelling this repo has not seen is carried through unchanged so it stays
    visible rather than being rounded to one of the two known answers. `None`
    survives as `None`, which is 349 of the 455 captured rows and means "the
    taxonomy says nothing".

    CONSTRUCTED-CONVENTIONAL: no captured row spells the balance any way but
    lower-case, which is why nothing caught the divergence. The pin is against
    a FUTURE upstream — an edgartools version or a taxonomy source that
    capitalises — and it is worth taking because the direction the un-normalised
    consumer failed in was the money path.
    """
    def line(balance):
        return shape.Line(
            label="Net revenues", concept="us-gaap_Revenues", level=3,
            weight=1.0, calculation_parent=None, values={}, balance=balance,
        )

    assert line("Debit").balance == "debit"
    assert line("CREDIT").balance == "credit"
    assert line("debit").balance == "debit"
    assert line(None).balance is None
    assert line("Foreign").balance == "foreign", (
        "an unknown spelling is folded, never rounded to a known answer"
    )
    # And the rule has ONE site, callable by anyone who holds a raw value
    # rather than a `Line`.
    assert shape.normalize_balance("Debit") == "debit"
    assert shape.normalize_balance(None) is None


def test_a_line_whose_filer_declared_no_precision_carries_an_empty_mapping(shape):
    """CONSTRUCTED-CONVENTIONAL — a row with no `decimals` key at all.

    OBSERVED in the capture: rows DO carry `decimals`, and an abstract row
    carries it empty (`{}`). Unobserved is the key being absent entirely, which
    is what a `get_statement` shape from a different edgartools version could
    hand over. The empty mapping is the honest answer for both — it means "this
    filer declared no precision here", which the consumer must read as "compare
    exactly", never as "any precision you like". `None` would push that
    judgement onto every caller.
    """
    line = shape._line({"concept": "us-gaap_Revenues", "label": "Revenue"})

    assert line.decimals == {}


@pytest.mark.parametrize(
    "accession, ticker",
    [
        # COMMITTED, and the pair is the point: one filing from each era, so an
        # era difference cannot pass as a filer difference.
        ("0000021344-18-000008", "KO"),
        ("0000051143-26-000010", "IBM"),
    ],
)
def test_all_three_statements_assemble_in_both_eras(
    shape, reconstruction_capture, accession, ticker,
):
    """The plan's GREEN: all three statements assemble, lines preserve
    presentation order, and each line carries the filer's own label with its
    weight and calculation parent beside it.

    Order is asserted against the captured rows rather than against a
    transcribed expectation, so the assertion stays true for any filing: the
    reconstruction must be the kept rows IN THE ORDER THE FILING PRESENTED
    THEM, never sorted, grouped or re-ranked.

    HOW the order is checked, and what that does not prove: the assembled
    lines must be a SUBSEQUENCE of the captured rows, matched on
    (label, concept, level). Re-deriving the expected list any other way would
    just re-run the filter under test and prove nothing. The subsequence check
    catches any reordering, grouping or sort; it would not catch a swap of two
    rows sharing all three of those fields, which no captured statement
    contains. Line-by-line fidelity against the filed DOCUMENT is a separate
    acceptance and belongs to plan Task 10.
    """
    entry = _captured_filing(reconstruction_capture, accession)
    statements = shape.statements_for(_CapturedFiling(entry))

    assert set(statements.by_kind) == {"income", "balance_sheet", "cash_flow"}
    for kind, lines_out in statements.by_kind.items():
        rows = _captured_rows(shape, reconstruction_capture, accession, kind)
        assert lines_out, f"{ticker} {kind} assembled to nothing"
        assert len(lines_out) < len(rows), (
            f"{ticker} {kind} kept every row — the noise filter did not run"
        )
        remaining = iter(rows)
        for line in lines_out:
            assert any(
                (row.get("label"), row.get("concept"), row.get("level"))
                == (line.label, line.concept, line.level)
                for row in remaining
            ), f"{ticker} {kind}: {line.label!r} is out of presentation order"
        assert all(line.concept for line in lines_out)

    # Every captured filing carries only dimension keys this repo has seen, so
    # the warning channel is silent here — which is what makes a non-empty
    # value in it meaningful.
    assert statements.unrecognised_dimension_keys == ()


def test_a_filing_declares_one_role_per_kind_in_the_captured_sample(
    shape, reconstruction_capture,
):
    """The GROUNDING for role selection, RE-DERIVED rather than read back:
    across all five captured filings — two eras, 694 presentation roles — no
    filing offers more than ONE role per kind, so the multi-role situation the
    preference rule guards was never observed here.

    The count is computed by running the live classifier over every role each
    filing declares, because this number is the whole evidence for calling
    role selection a guard rather than a policy. Were it stored in the fixture
    instead, a classifier that regressed into accepting a second income role
    would leave this test green while the sentence it grounds became false.
    The fixture supplies the roles; the classifier supplies the verdict; the
    test compares them on every run.

    Realty Income is the case that matters most: its ONLY income role is the
    COMBINED income-and-comprehensive-income one. A rule that rejected
    combined roles rather than merely deprioritising them would leave that
    filer with no income statement at all — the trap at the top of this
    module, reached from the other direction.
    """
    total_roles = 0
    for filing in reconstruction_capture["filings"]:
        per_kind = Counter(
            kind for kind in map(shape.statement_kind, filing["presentation_roles"])
            if kind is not None
        )
        total_roles += len(filing["presentation_roles"])
        assert sorted(per_kind) == ["balance_sheet", "cash_flow", "income"], (
            f"{filing['ticker']} {filing['accession']}: {dict(per_kind)}"
        )
        assert all(n == 1 for n in per_kind.values()), (
            f"{filing['ticker']} {filing['accession']}: {dict(per_kind)}"
        )
    assert total_roles == 694  # 93 + 172 + 131 + 130 + 168, an immutable fact

    realty = _captured_filing(reconstruction_capture, "0000726728-26-000011")
    only_income_role = next(
        role for role in realty["presentation_roles"]
        if shape.statement_kind(role) == "income"
    )
    assert only_income_role.endswith(
        "CONSOLIDATEDSTATEMENTSOFINCOMEANDCOMPREHENSIVEINCOME"
    )


def test_a_kind_the_filing_never_declares_is_absent_not_empty(
    shape, reconstruction_capture,
):
    """"This filer files no such statement" and "the statement came back empty"
    are different facts and must not render alike (brief §Every empty cell must
    say which kind of empty it is). A missing kind is therefore absent from
    `by_kind`, never a `[]`.

    CONSTRUCTED-CONVENTIONAL: the roles and rows are KO's own, with the two
    other statements' roles removed. A filing carrying only one of the three
    is not something the capture contains — every 10-K sampled files all
    three. Its ~90 NOTE roles are left in place, so assembly still has real
    roles to reject while the kind is genuinely missing.
    """
    entry = dict(_captured_filing(reconstruction_capture, "0000021344-18-000008"))
    entry["presentation_roles"] = [
        role for role in entry["presentation_roles"]
        if shape.statement_kind(role) in (None, "income")
    ]
    entry["roles_captured"] = [
        captured for captured in entry["roles_captured"]
        if shape.statement_kind(captured["role"]) == "income"
    ]

    statements = shape.statements_for(_CapturedFiling(entry))

    assert set(statements.by_kind) == {"income"}
    assert "balance_sheet" not in statements.by_kind
    assert set(statements.roles) == {"income"}


# --- CONSTRUCTED-CONVENTIONAL fixtures --------------------------------------
#
# NOT OBSERVED. Every fixture below this line was written by hand, because
# nothing in the 2026-07-26 observation exercises the rule it pins. Each is
# here because deleting the rule it pins would be destructive, not because the
# fixture is evidence of anything. Do not cite these as measurements, and
# replace any of them with an observed one on sight.
#
# The Task 2 fixtures here are role URIs written to a filer's conventional
# naming. The two Task 3 fixtures at the end are a filing offering two roles of
# one kind, and a row carrying an invented dimension key — the second CANNOT be
# observed even in principle, since it stands for a spelling nobody has met yet,
# which is the whole reason its handling has to be pinned by construction.


def test_singular_detail_note_quoting_a_statement_title_is_rejected(shape):
    """The wrong-kind case that motivated the singular `detail` stem: a note in
    Microsoft's observed singular-`Detail` dialect that ALSO quotes a statement
    title. No observed role combines those two spellings — Microsoft's real
    singular-`Detail` role carries no statement title, and every observed role
    that does quote one spells the suffix `Details` — so this URI is written to
    demonstrate the hole. Under a plural-only marker it classifies `cash_flow`.
    """
    assert shape.statement_kind(
        "http://www.microsoft.com/20190630/taxonomy/role/DisclosureSomethingStatementOfCashFlowsDetail"
    ) is None


@pytest.mark.parametrize(
    "role",
    [
        # "Income taxes" and "cash flow hedges" are note topics that carry a
        # statement's noun and no "statement" word. JPMorgan's observed
        # `DerivativeInstrumentsImpactOnStatementsOfIncomeCashFlowHedgesDetails`
        # shows the cash-flow-hedges topic is real; this shorter spelling of it
        # is not observed.
        "http://www.ibm.com/role/DisclosureIncomeTaxes",
        "http://www.jpmorganchase.com/role/CashFlowHedges",
    ],
)
def test_income_and_cash_flow_nouns_alone_do_not_name_a_statement(shape, role):
    """The other direction of the gate tested above: for these two kinds the
    bare noun is a note topic as often as a statement title, so it counts only
    with the word "statement" beside it. Deleting that requirement routes note
    lines into a statement.
    """
    assert "statement" not in role.lower()
    assert shape.statement_kind(role) is None


def test_statement_of_retained_earnings_is_not_an_income_statement(shape):
    """Statement of retained earnings is its own statement, out of scope here.
    It reaches the income rule through the bare "earnings" noun, so without a
    rule it is served as the income statement.

    DEFENSIVE AGAINST AN UNOBSERVED CASE, and the distinction is the point.
    Measured absent in BOTH eras of this lane's range (checked 2026-07-26):
    10 filers' 2015-2020 10-Ks (GIS/KMB/SWK/PPG/ADM/SO/ED/NEE/MMM/EMR) and
    12 filers' earliest XBRL-era 2010 10-Ks (those plus KO/PG/JNJ) — 22
    filer-observations, ZERO roles containing "retainedearnings". The
    statement of stockholders' equity occupies this slot at both ends of the
    range (`realtyincome.com/role/ConsolidatedStatementsOfEquity`, observed).

    An earlier version of this note justified the rule by claiming the
    combined "Income and Retained Earnings" title was more common in the
    earlier span. That was an inference, and the 2010 sweep measured it FALSE.
    The rule is kept because it is cheap and guards the wrong-kind direction —
    NOT because the case was ever found. These fixtures are
    CONSTRUCTED-CONVENTIONAL by necessity, not convenience: no observed
    instance exists to use instead.
    """
    assert shape.statement_kind(
        "http://www.generalmills.com/role/ConsolidatedStatementsOfRetainedEarnings"
    ) is None


def test_income_combined_with_retained_earnings_is_still_income(shape):
    """Why the retained-earnings rule REMOVES that wording rather than
    rejecting the role outright: were a filer to combine the two, rejecting
    the role would erase that filer's income statement — the same failure as
    the comprehensive-income trap at the top of this module.

    CONSTRUCTED-CONVENTIONAL, and note the conditional above: unlike the
    comprehensive-income trap, which is grounded in an observed combined role
    (Realty Income), no combined "Income and Retained Earnings" role was found
    in 22 filer-observations across both eras — see the sibling test for the
    measurement. This pins the safer of two designs for a case measured absent,
    not a case observed.
    """
    assert shape.statement_kind(
        "http://www.generalmills.com/role/ConsolidatedStatementsOfIncomeAndRetainedEarnings"
    ) == "income"


def test_an_unseen_dimension_key_is_reported_not_silently_deleted(
    shape, lines, reconstruction_capture,
):
    """The counting half of "exclude fail-closed, count visibly, promote
    deliberately" (docs/loom/memory/
    shared-classifier-over-open-dialects-needs-allowlist.md).

    `is_statement_line` rejects a row for any truthy "dim"-spelled key that is
    not a known child descriptor. That polarity is right — an unknown key
    means an unproven row — but it has a standing cost: were edgartools to
    rename `has_dimension_children`, every consolidated line would start being
    deleted again, exactly as measured on KO FY2017, and a predicate returning
    `bool` cannot say so. Assembly reads every row, so assembly reports it.

    CONSTRUCTED-CONVENTIONAL by necessity: the fixture stands for a spelling
    that has not been observed, and one that had been observed would not test
    this. The row is KO's own captured top line with the invented key added, so
    everything about it except that key is real.
    """
    entry = _captured_filing(reconstruction_capture, "0000021344-18-000008")
    rows = [dict(row) for row in _captured_rows(
        shape, reconstruction_capture, "0000021344-18-000008", "income")]
    top_line = next(
        row for row in rows
        if row["label"] == "NET OPERATING REVENUES" and not row.get("full_dimension_label")
    )
    top_line["has_dimensioned_children"] = True

    # The predicate drops it — fail-closed, and deliberately unchanged here.
    assert lines.is_statement_line(top_line) is False

    entry = {**entry, "roles_captured": [
        {**captured, "rows": rows}
        if shape.statement_kind(captured["role"]) == "income" else captured
        for captured in entry["roles_captured"]
    ]}
    statements = shape.statements_for(_CapturedFiling(entry))

    assert statements.unrecognised_dimension_keys == ("has_dimensioned_children",)
    # And the visible count is not cosmetic: the line really is gone.
    assert len(statements.by_kind["income"]) == 25


def test_a_pure_income_role_is_preferred_over_a_combined_one(
    shape, reconstruction_capture,
):
    """Role selection, which needs a filing's whole role set and so lives in
    assembly rather than in `statement_kind` (plan Decision Log, Task 2 ->
    Task 3).

    CONSTRUCTED-CONVENTIONAL, and the label is load-bearing: NO captured
    filing offers two roles of one kind (see the sibling test that measures
    it), so this pins a guard against a situation never seen, not a policy
    derived from one. What it fixes is that the choice must be DETERMINISTIC
    and must prefer the role carrying fewer out-of-scope lines — never
    "whichever role the filing happened to list first".

    The combined role's LAST PATH SEGMENT sorts before the pure one's, so a
    rule that fell back to the URI order alone would pick the wrong role and
    this test would fail. Precisely: the tie-break compares that segment
    FOLDED (`_fold`), not raw — the two agree for these two fixtures, and this
    sentence says which one is actually compared because "the string the
    tie-break compares" was wrong by one transformation for a round.
    Both roles stay visible on the result; the combined one is deprioritised,
    never rejected.
    """
    entry = _captured_filing(reconstruction_capture, "0000021344-18-000008")
    pure_rows = _captured_rows(shape, reconstruction_capture, "0000021344-18-000008", "income")
    combined_role = "http://www.thecocacolacompany.com/role/AConsolidatedStatementsOfIncomeAndComprehensiveIncome"
    pure_role = next(
        role for role in entry["presentation_roles"]
        if shape.statement_kind(role) == "income"
    )
    assert combined_role.rsplit("/", 1)[-1] < pure_role.rsplit("/", 1)[-1]
    assert shape.statement_kind(combined_role) == "income"

    entry = {
        **entry,
        "presentation_roles": [*entry["presentation_roles"], combined_role],
        "roles_captured": [
            *entry["roles_captured"],
            {"role": combined_role, "rows": [{
                "concept": "us-gaap_ComprehensiveIncomeNetOfTax",
                "label": "TOTAL COMPREHENSIVE INCOME",
                "level": 3, "is_abstract": False, "has_values": True,
                "values": {"duration_2017-01-01_2017-12-31": 1234000000.0},
            }]},
        ],
    }
    statements = shape.statements_for(_CapturedFiling(entry))

    assert statements.roles["income"] == (pure_role, combined_role)
    assert len(statements.by_kind["income"]) == 26
    assert not any(line.label == "TOTAL COMPREHENSIVE INCOME"
                   for line in statements.by_kind["income"])
