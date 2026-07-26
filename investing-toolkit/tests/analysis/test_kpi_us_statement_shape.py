"""Tests for analysis-kpi/scripts/kpi_us_statement_shape.py — role -> statement
kind classification (pure-compute, plan Task 2,
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md).

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

The suite makes no network call: these are string literals.

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
import sys

import pytest
from conftest import SKILLS

STATEMENT_SHAPE_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_shape.py"


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


# --- CONSTRUCTED-CONVENTIONAL fixtures --------------------------------------
#
# NOT OBSERVED. Every role URI below this line was written by hand to a filer's
# conventional naming, because no role in the 2026-07-26 observation exercises
# the rule it pins. Each is here because deleting the rule it pins would be
# destructive, not because the URI is evidence of anything. Do not cite these
# as measurements, and replace any of them with an observed role on sight.


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
