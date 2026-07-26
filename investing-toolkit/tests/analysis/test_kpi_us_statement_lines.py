"""Tests for analysis-kpi/scripts/kpi_us_statement_lines.py — the structural
predicate separating real statement lines from dimensional noise (pure-compute,
plan Task 1, docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md).

WHY these tests are adversarial rather than illustrative: a leaked dimensional
row does not crash. It renders as a plausible statement line with a plausible
label and silently breaks every arithmetic check downstream. The obvious
implementation — filter on the row's dimension-label key — was MEASURED to fail:
it read `TechnologyServiceMember` as IBM's first income-statement line and
`NaturalGasReservesMember` as Duke Energy's, on every filing from 2019 to 2026,
because from ~2019 filers disaggregate revenue via `srt:ProductOrServiceAxis`
and that axis's DOMAIN MEMBERS appear as presentation rows carrying NO dimension
label. So the suite must pin BOTH eras (a pre-2018 dimension-labelled segment
row AND a 2019+ Member row) and must pin that the fix is not substring matching.

Row shapes below are in-test literals mirroring the keys observed live on
2026-07-26 from `xbrl.get_statement("IncomeStatement")` (KO accession
0000021344-18-000008); no test here touches the network.

No `@req` tags: this dispatch carries no registered loom-spec REQ-ids (the work
is tracked by named plan Task 1), so `@req` is omitted per the implementer
contract.
"""
from __future__ import annotations

import importlib.util
import sys

from conftest import SKILLS

import pytest

KPI_US_STATEMENT_LINES_SCRIPT = (
    SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statement_lines.py"
)


def _load(name: str, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def lines_module():
    return _load("kpi_us_statement_lines_test", KPI_US_STATEMENT_LINES_SCRIPT)


def _row(concept: str, label: str, **extra):
    """A presentation row carrying the keys edgartools was observed to emit.

    Only `concept`/`label` vary per case; `extra` adds the era-specific signal
    under test (e.g. `full_dimension_label` for a pre-2018 segment row).
    """
    row = {
        "concept": concept,
        "label": label,
        "name": concept,
        "all_names": [concept],
        "level": 1,
        "is_abstract": False,
        "has_values": True,
        "values": {"2017": 1000},
        "children": [],
        "calculation_parent": None,
        "weight": 1.0,
        "units": "USD",
    }
    row.update(extra)
    return row


def test_axis_domain_members_are_not_statement_lines(lines_module):
    """The measured 2019-2026 failure: an axis domain member surfaced as a
    presentation row with NO dimension label must still be rejected, while a
    same-era genuine line is kept. Filtering on the dimension label alone
    passes the second assertion and fails the first — which is the bug.
    """
    ibm_member = _row("us-gaap:TechnologyServiceMember", "Technology services")
    duke_member = _row("us-gaap:NaturalGasReservesMember", "Natural gas")
    genuine_line = _row("us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                        "Revenue")

    assert lines_module.is_statement_line(ibm_member) is False
    assert lines_module.is_statement_line(duke_member) is False
    assert lines_module.is_statement_line(genuine_line) is True


def test_pre_2018_dimension_labelled_segment_row_is_not_a_statement_line(lines_module):
    """The other era: KO FY2017's income role interleaves segment breakdowns
    that DO carry a dimension label, on an otherwise ordinary revenue concept.
    The concept alone cannot tell them apart — the dimension signal must.
    """
    segment_row = _row(
        "us-gaap:SalesRevenueGoodsNet",
        "Asia Pacific",
        full_dimension_label="us-gaap:StatementBusinessSegmentsAxis: Asia Pacific",
    )
    consolidated_row = _row("us-gaap:SalesRevenueGoodsNet", "NET OPERATING REVENUES")

    assert lines_module.is_statement_line(segment_row) is False
    assert lines_module.is_statement_line(consolidated_row) is True


def test_the_dim_axis_column_spelling_is_also_a_dimension_signal(lines_module):
    """The dimension key is not spelled one way. edgartools ALSO emits per-axis
    columns named `dim_<namespace>_<AxisLocalName>` — live-verified and recorded
    at data-markets/scripts/sec_edgar_client.py:2277-2288 (`dim_srt_
    ProductOrServiceAxis`, `dim_us-gaap_StatementBusinessSegmentsAxis`). That
    spelling carries no "dimension" substring, so a predicate matching only
    `dimension` admits KO's segment slices: their concept is the ordinary
    `SalesRevenueGoodsNet`, which carries no structural suffix and is therefore
    kept by every other signal this module has.
    """
    product_slice = _row(
        "us-gaap:SalesRevenueGoodsNet",
        "Sparkling soft drinks",
        dim_srt_ProductOrServiceAxis="ko:SparklingSoftDrinksMember",
    )
    geographic_slice = _row(
        "us-gaap:SalesRevenueGoodsNet",
        "Asia Pacific",
        **{"dim_us-gaap_StatementBusinessSegmentsAxis": "ko:AsiaPacificMember"},
    )
    unpopulated_axis_column = _row(
        "us-gaap:SalesRevenueGoodsNet",
        "NET OPERATING REVENUES",
        dim_srt_ProductOrServiceAxis=None,
    )

    assert lines_module.is_statement_line(product_slice) is False
    assert lines_module.is_statement_line(geographic_slice) is False
    assert lines_module.is_statement_line(unpopulated_axis_column) is True


def test_a_consolidated_row_with_dimensioned_children_is_kept(lines_module):
    """A key naming a dimension does not always mean "this row IS a slice", and
    reading it that way DELETED the top line of every statement that discloses
    segments. `get_statement` emits FOUR keys containing "dim" in two groups
    that mean OPPOSITE things (live, KO accession 0000021344-18-000008):

      is_dimension / full_dimension_label / dimension_metadata
          the row IS a segment slice — 49 of KO's 80 income rows.
      has_dimension_children
          the row is an ordinary CONSOLIDATED line that HAS slices beneath it —
          10 rows, among them `NET OPERATING REVENUES` (35,410M, the filing's
          own top line), `OPERATING INCOME` and `INCOME BEFORE INCOME TAXES`.

    Measured damage from conflating them: KO FY2017 income kept 17 of 26 lines,
    DUK FY2017 income 18 of 52, and Realty Income FY2025 lost `Total assets`,
    `Total liabilities` and `Total equity`. Silent deletion of a filer's
    headline figures — the corruption direction opposite to a leak, and the one
    a substring match on the key name cannot distinguish.

    Both directions are pinned here because either alone is satisfiable by a
    degenerate predicate: rejecting nothing passes the first assertion,
    rejecting everything passes the rest.
    """
    consolidated_with_slices_below = _row(
        "us-gaap:SalesRevenueGoodsNet",
        "NET OPERATING REVENUES",
        has_dimension_children=True,
        is_dimension=None,
        full_dimension_label=None,
        dimension_metadata=None,
    )
    slice_by_is_dimension = _row(
        "us-gaap:SalesRevenueGoodsNet",
        "Bottling Investments",
        is_dimension=True,
        has_dimension_children=None,
    )
    slice_by_metadata = _row(
        "us-gaap:SalesRevenueGoodsNet",
        "Bottling Investments",
        dimension_metadata=[
            {"dimension": "us-gaap:StatementBusinessSegmentsAxis",
             "member": "ko:BottlingInvestmentsMember"}
        ],
        has_dimension_children=None,
    )
    slice_that_also_has_children = _row(
        "us-gaap:SalesRevenueGoodsNet",
        "Bottling Investments",
        is_dimension=True,
        has_dimension_children=True,
    )

    assert lines_module.is_statement_line(consolidated_with_slices_below) is True
    assert lines_module.is_statement_line(slice_by_is_dimension) is False
    assert lines_module.is_statement_line(slice_by_metadata) is False
    assert lines_module.is_statement_line(slice_that_also_has_children) is False


def test_a_real_line_containing_member_is_kept(lines_module):
    """Substring matching would reject these. They are real statement lines:
    `Member`/`Domain` occur inside ordinary English element names, and only the
    XBRL structural SUFFIX marks a placeholder.
    """
    membership_revenue = _row(
        "us-gaap:MembershipDuesRevenueOnGoingOperations", "Membership fees"
    )
    members_equity = _row("us-gaap:MembersEquity", "Members' equity")
    domestic_line = _row("us-gaap:DomainNameIntangibleAssets", "Domain names")

    assert lines_module.is_statement_line(membership_revenue) is True
    assert lines_module.is_statement_line(members_equity) is True
    assert lines_module.is_statement_line(domestic_line) is True


def test_every_xbrl_structural_placeholder_suffix_is_rejected(lines_module):
    """`Member` is one of a closed set of suffixes the XBRL naming convention
    reserves for structure. A filer that discloses through an axis this repo has
    never sampled must be excluded WITHOUT that axis's name being listed
    anywhere — that is the allowlist property
    (docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md).

    The suffix match must also be CASE-INSENSITIVE. A filer spelling the suffix
    in caps is not hypothetical: `kpi_xbrl_ingest._strip_axis_member_suffix`
    records the MEASURED 10-Q variant `DataCenterMEMBER`, and a raw
    `.endswith()` missed it there (docs/loom/memory/
    unifying-a-normalization-has-a-scope.md, instance 2). Here the same defect
    admits the placeholder instead of splitting an id — the leak direction this
    module exists to prevent.
    """
    placeholders = [
        "srt:ProductOrServiceAxis",
        "srt:ProductsAndServicesDomain",
        "us-gaap:IncomeStatementTable",
        "us-gaap:IncomeStatementLineItems",
        "duk:NeverBeforeSampledWidgetMember",
        "ko:SomeInventedFutureAxis",
        "duk:NeverBeforeSampledMEMBER",
        "srt:ProductOrServiceAXIS",
        "us-gaap:IncomeStatementLINEITEMS",
    ]
    for concept in placeholders:
        assert lines_module.is_statement_line(_row(concept, "whatever")) is False, concept


def test_a_filers_own_custom_concept_is_a_statement_line(lines_module):
    """KO's FY2017 income statement carries `ko_UnusualOrInfrequentItemOperating`
    — a custom concept in edgartools' underscore-separated spelling. Custom
    namespace is normal; it must not be read as noise, and the underscore
    spelling must resolve the same local name as the colon spelling.

    The local-name claim is asserted on `local_name` DIRECTLY: routing both
    spellings through `is_statement_line` alone cannot detect the prefix
    stripping regressing, because both spellings reach the same suffix verdict
    with or without it.
    """
    assert (
        lines_module.local_name("ko_UnusualOrInfrequentItemOperating")
        == "UnusualOrInfrequentItemOperating"
    )
    assert (
        lines_module.local_name("ko:UnusualOrInfrequentItemOperating")
        == "UnusualOrInfrequentItemOperating"
    )

    underscore = _row("ko_UnusualOrInfrequentItemOperating", "Other operating charges")
    colon = _row("ko:UnusualOrInfrequentItemOperating", "Other operating charges")
    underscore_member = _row("duk_NaturalGasReservesMember", "Natural gas")

    assert lines_module.is_statement_line(underscore) is True
    assert lines_module.is_statement_line(colon) is True
    assert lines_module.is_statement_line(underscore_member) is False


def test_a_row_that_cannot_be_proven_a_statement_line_is_rejected(lines_module):
    """Fail-closed direction. A row with no usable concept, or one carrying an
    unrecognized dimension-bearing key, is NOT provably an undimensioned line,
    so it is excluded rather than admitted by default — the polarity the
    allowlist memory exists to enforce.
    """
    assert lines_module.is_statement_line(_row("", "Revenue")) is False
    assert lines_module.is_statement_line({"label": "Revenue"}) is False
    null_concept = _row("us-gaap:Revenues", "Revenue")
    null_concept["concept"] = None
    assert lines_module.is_statement_line(null_concept) is False
    assert (
        lines_module.is_statement_line(
            _row("us-gaap:Revenues", "Revenue", dimension_label="Asia Pacific")
        )
        is False
    )
