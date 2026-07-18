"""Tests for analysis-kpi/scripts/kpi_xbrl.py — XBRL fact -> kpi_store
point adapter (operational-kpi tier-② XBRL pilot, Task 1).

kpi_xbrl.py is PURE-COMPUTE (stdlib only) — it does NOT import `_store_fs`,
resolve a store dir, lock, or persist anything, and does NOT touch the
network or an LLM. No `KPI_STORE_DIR` fixture is needed.

The library function is exercised by loading `kpi_xbrl.py` via importlib
(same convention as test_kpi_parse.py's `kpi_parse_module` fixture),
against the REAL captured fixture `fixtures/xbrl_aapl_factpack.json`.

No `@req` tags: this dispatch's plan (docs/loom/plans/2026-07-14-
operational-kpi-companyfacts-pilot.md) traces work by named plan Tasks,
NOT by registered loom-spec REQ-ids — so `@req` is omitted per the
implementer contract.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys

from conftest import FIXTURES, KPI_XBRL_SCRIPT

import pytest


@pytest.fixture(scope="module")
def kpi_xbrl_module():
    spec = importlib.util.spec_from_file_location("kpi_xbrl_test", KPI_XBRL_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_xbrl_test"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def fact_pack():
    return json.loads((FIXTURES / "xbrl_aapl_factpack.json").read_text(encoding="utf-8"))


@pytest.fixture
def signature_fact_pack():
    return json.loads(
        (FIXTURES / "xbrl_signature_factpack.json").read_text(encoding="utf-8")
    )


@pytest.fixture
def restatement_fact_pack():
    return json.loads(
        (FIXTURES / "xbrl_restatement_factpack.json").read_text(encoding="utf-8")
    )


NEW_IPHONE_MATCH = {
    "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
    "axis": "srt:ProductOrServiceAxis",
    "member": "aapl:IPhoneMember",
}

# NOTE: test_facts_to_points_maps_provenance_and_fails_loud (OLD axis/member
# shape) was DELETED (Task 7) — its provenance-mapping + fail-loud coverage
# is REPLACED by test_facts_to_points_fails_loud_new_shape below, which
# exercises the same anti-fabrication guards on the NEW full-signature
# `dimensions`-map shape against the real signature_fact_pack fixture.


def test_facts_to_points_rejects_raw_column_shape_never_calendar_keyed(kpi_xbrl_module, fact_pack):
    """UPDATED for Task 5 (was test_facts_to_points_period_derives_from_
    period_end_not_fiscal_year — that test asserted `period == period_end[:4]`,
    the CALENDAR year, ruled a latent bug at the 2026-07-18 re-plan:
    rebuild-findings §RESOLVED (b)). Its historical intent — never trust
    edgartools' raw `fiscal_year` COLUMN, which mislabels prior-year
    comparatives — is PRESERVED, re-encoded for the migrated keying: a fact
    stripped down to the old raw-column shape (bare `fiscal_year`, no
    emitted fiscal_quarter/duration_months group) is surfaced
    UNCLASSIFIABLE — never silently keyed from the raw column, and never
    silently re-keyed from period_end[:4] either."""
    mutated = json.loads(json.dumps(fact_pack))
    for fact in mutated["facts"]:
        if fact["concept"] == NEW_IPHONE_MATCH["concept"] and fact.get("member") == "aapl:IPhoneMember" and fact["period_end"] == "2025-09-27":
            # Strip the emitted label group back to the pre-schema raw-column
            # shape: fiscal_year survives as a bare int (the untrusted
            # edgartools dataframe column), the group's other fields go.
            for field in ("fiscal_quarter", "duration_months",
                          "calendar_year", "calendar_quarter",
                          "derivation_basis"):
                fact.pop(field, None)

    with pytest.raises(ValueError, match="unclassifiable"):
        kpi_xbrl_module.facts_to_points(
            mutated, "iphone_revenue", NEW_IPHONE_MATCH, "AAPL", "xbrl-dimensional"
        )

    # The intact producer-labeled pack still keys on the emitted fiscal
    # label (which coincides with 2025 for this real annual AAPL fact).
    points = kpi_xbrl_module.facts_to_points(
        fact_pack, "iphone_revenue", NEW_IPHONE_MATCH, "AAPL", "xbrl-dimensional"
    )
    matched = [p for p in points if p["value"] == 209586000000]
    assert len(matched) == 1
    assert matched[0]["period"] == "2025"


def test_facts_to_points_missing_period_end_raises(kpi_xbrl_module, fact_pack):
    """A fact missing period_end RAISES naming period_end — never a
    fabricated period "None" (this closes the code-quality 🟡 finding)."""
    mutated = json.loads(json.dumps(fact_pack))
    for fact in mutated["facts"]:
        if fact["concept"] == NEW_IPHONE_MATCH["concept"] and fact.get("member") == "aapl:IPhoneMember":
            del fact["period_end"]
    with pytest.raises(ValueError, match="period_end"):
        kpi_xbrl_module.facts_to_points(
            mutated, "iphone_revenue", NEW_IPHONE_MATCH, "AAPL", "xbrl-dimensional"
        )


def test_facts_to_points_malformed_period_end_raises(kpi_xbrl_module, fact_pack):
    """A fact with a non-YYYY-MM-DD period_end RAISES naming period_end."""
    mutated = json.loads(json.dumps(fact_pack))
    for fact in mutated["facts"]:
        if fact["concept"] == NEW_IPHONE_MATCH["concept"] and fact.get("member") == "aapl:IPhoneMember":
            fact["period_end"] = "not-a-date"
    with pytest.raises(ValueError, match="period_end"):
        kpi_xbrl_module.facts_to_points(
            mutated, "iphone_revenue", NEW_IPHONE_MATCH, "AAPL", "xbrl-dimensional"
        )


IPHONE_REVENUE_BINDING = {
    "kpi_id": "iphone_revenue",
    "sources": [
        {
            "concept": "us-gaap:SalesRevenueNet",
            "axis": "us-gaap:ProductOrServiceAxis",
            "member": "aapl:AppleIphoneMember",
            "fy_min": 2007,
            "fy_max": 2017,
            "source_kind": "xbrl-dimensional",
        },
        {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "axis": "srt:ProductOrServiceAxis",
            "member": "aapl:IPhoneMember",
            "fy_min": 2018,
            "fy_max": 2099,
            "source_kind": "xbrl-dimensional",
        },
    ],
}


IPHONE_REVENUE_FULL_SIGNATURE_BINDING = {
    "kpi_id": "iphone_revenue",
    "sources": [
        {
            "concept": "us-gaap:SalesRevenueNet",
            "dimensions": {"ProductOrService": "AppleIphoneMember"},
            "source_kind": "xbrl-dimensional",
        },
        {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "dimensions": {"ProductOrService": "IPhoneMember"},
            "source_kind": "xbrl-dimensional",
        },
    ],
}


def test_resolve_binding_stitches_two_eras_into_one_kpi_id(kpi_xbrl_module, signature_fact_pack):
    """Task 7 GREEN (migrated from the OLD axis/member shape): the
    iphone_revenue binding's two full-signature sources (OLD:
    SalesRevenueNet + {ProductOrService: AppleIphoneMember}; NEW:
    RevenueFromContract... + {ProductOrService: IPhoneMember}) resolve ALL
    6 iPhone facts in the fixture (3 OLD-era FY2014-2016 + 3 NEW-era
    FY2023-2025) under one kpi_id "iphone_revenue" — the concept+member
    signature alone is the era discriminant; no fy_min/fy_max ranges
    needed anymore.
    """
    points = kpi_xbrl_module.resolve_binding(
        signature_fact_pack, IPHONE_REVENUE_FULL_SIGNATURE_BINDING, "AAPL"
    )

    assert len(points) == 6
    assert all(p["kpi_id"] == "iphone_revenue" for p in points)
    periods = sorted(p["period"] for p in points)
    assert periods == ["2014", "2015", "2016", "2023", "2024", "2025"]

    by_period = {p["period"]: p for p in points}
    assert by_period["2014"]["value"] == 101991000000
    assert by_period["2014"]["source_cell_ref"] == (
        "us-gaap:SalesRevenueNet|ProductOrService=AppleIphoneMember"
    )
    assert by_period["2015"]["value"] == 155041000000
    assert by_period["2016"]["value"] == 136700000000
    assert by_period["2023"]["value"] == 200583000000
    assert by_period["2024"]["value"] == 201183000000
    assert by_period["2025"]["value"] == 209586000000
    assert by_period["2025"]["source_cell_ref"] == (
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
        "|ProductOrService=IPhoneMember"
    )


def test_build_series_with_break_splits_stitched_era_both_segments(
    kpi_xbrl_module, signature_fact_pack
):
    """Task 7 GREEN: the offline complement to the live e2e's recast-only
    reach. The full-signature era-stitched iphone_revenue points (3
    OLD-era FY2014-2016 + 3 NEW-era FY2023-2025, from the REAL committed
    fixture) split at the 2018 tagging-regime break into BOTH segments
    populated: as_reported holds FY2014-2016, recast holds FY2023-2025 —
    a single live 10-K's XBRL never carries pre-2018 comparatives, so
    only this offline test (against the committed fixture) can prove the
    as_reported segment is non-empty.
    """
    points = kpi_xbrl_module.resolve_binding(
        signature_fact_pack, IPHONE_REVENUE_FULL_SIGNATURE_BINDING, "AAPL"
    )
    assert len(points) == 6

    result = kpi_xbrl_module.build_series_with_break(points, "2018")

    as_reported_periods = sorted(p["period"] for p in result["as_reported"])
    recast_periods = sorted(p["period"] for p in result["recast"])
    assert as_reported_periods == ["2014", "2015", "2016"]
    assert recast_periods == ["2023", "2024", "2025"]

    # nothing dropped, nothing duplicated across the two partitions
    all_periods = sorted(
        p["period"] for p in result["as_reported"] + result["recast"]
    )
    assert all_periods == ["2014", "2015", "2016", "2023", "2024", "2025"]
    assert result["break_markers"] == [{"break_period": "2018"}]


AMBIGUOUS_OVERLAPPING_BINDING = {
    "kpi_id": "iphone_revenue",
    "sources": [
        {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "axis": "srt:ProductOrServiceAxis",
            "member": "aapl:IPhoneMember",
            "fy_min": 2018,
            "fy_max": 2099,
            "source_kind": "xbrl-dimensional",
        },
        {
            # Same concept+axis+member as the source above, with an
            # OVERLAPPING fy range — any NEW-era iPhone fact (e.g. the
            # fixture's FY2025 fact) falls inside both [2018,2099] and
            # [2020,2099], so it matches two sources at once.
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "axis": "srt:ProductOrServiceAxis",
            "member": "aapl:IPhoneMember",
            "fy_min": 2020,
            "fy_max": 2099,
            "source_kind": "xbrl-dimensional",
        },
    ],
}


def test_resolve_binding_raises_on_ambiguous_multi_source_match(kpi_xbrl_module, fact_pack):
    """The >1-source-match RAISE branch is the anti-fabrication guard: a
    fact matching two sources at once must never be resolved to one of
    them arbitrarily. Two sources here share concept+axis+member with
    OVERLAPPING fy ranges, so the fixture's real FY2025 iPhone fact
    matches both — resolve_binding MUST raise, not silently pick one.
    """
    with pytest.raises(ValueError, match="ambiguous"):
        kpi_xbrl_module.resolve_binding(fact_pack, AMBIGUOUS_OVERLAPPING_BINDING, "AAPL")


STREAMING_TOTAL_BINDING = {
    "kpi_id": "streaming_revenue",
    "sources": [
        {
            "concept": "us-gaap:Revenues",
            "dimensions": {"ProductOrService": "StreamingMember"},
            "source_kind": "xbrl-dimensional",
        },
    ],
}

STREAMING_US_CANADA_BINDING = {
    "kpi_id": "streaming_revenue_us_canada",
    "sources": [
        {
            "concept": "us-gaap:Revenues",
            "dimensions": {
                "ProductOrService": "StreamingMember",
                "StatementGeographical": "UnitedStatesAndCanadaMember",
            },
            "source_kind": "xbrl-dimensional",
        },
    ],
}


def test_resolve_binding_exact_signature_deconflates(kpi_xbrl_module, signature_fact_pack):
    """Task 1 GREEN: resolve_binding EXACT-matches a source's full `dimensions`
    signature against a fact's `dimensions` dict — a binding with dimensions
    {"ProductOrService": "StreamingMember"} resolves ONLY the 3 NFLX total
    facts (one per period), NOT the 12 region-slice facts that also carry
    ProductOrService=StreamingMember plus an extra StatementGeographical axis
    (dict equality rejects the extra key). A binding naming BOTH axes
    resolves ONLY the matching region slice. Every point carries full
    provenance (source_accession/source_table_id/source_cell_ref).
    """
    total_points = kpi_xbrl_module.resolve_binding(
        signature_fact_pack, STREAMING_TOTAL_BINDING, "NFLX"
    )
    assert len(total_points) == 3
    assert all(p["kpi_id"] == "streaming_revenue" for p in total_points)
    assert sorted(p["value"] for p in total_points) == sorted(
        [45183036000, 39000966000, 33640458000]
    )
    assert sorted(p["period"] for p in total_points) == ["2023", "2024", "2025"]
    for p in total_points:
        assert p["source_accession"] == "0001065280-26-000034"
        assert p["source_table_id"]
        assert p["source_cell_ref"]

    us_points = kpi_xbrl_module.resolve_binding(
        signature_fact_pack, STREAMING_US_CANADA_BINDING, "NFLX"
    )
    assert len(us_points) == 3
    by_period = {p["period"]: p for p in us_points}
    assert by_period["2025"]["value"] == 19957152000
    for p in us_points:
        assert p["source_accession"] == "0001065280-26-000034"
        assert p["source_table_id"]
        assert p["source_cell_ref"]


def test_resolve_binding_raises_on_ambiguous_signature_period(kpi_xbrl_module, signature_fact_pack):
    """Task 2 GREEN: a bound signature that matches TWO facts for the SAME
    period with DIFFERENT values RAISES ValueError naming the period — the
    anti-fabrication guard extended to the full-signature era (never
    silently pick one of the conflicting values). The signature's clean
    periods (single fact each) still resolve fine on the unmutated pack.
    """
    mutated = json.loads(json.dumps(signature_fact_pack))
    duplicate_2025_total = next(
        f
        for f in mutated["facts"]
        if f["concept"] == "us-gaap:Revenues"
        and f["dimensions"] == {"ProductOrService": "StreamingMember"}
        and f["period_end"] == "2025-12-31"
    )
    conflicting_fact = json.loads(json.dumps(duplicate_2025_total))
    conflicting_fact["value"] = 45000000000  # differs from the real 45183036000
    mutated["facts"].append(conflicting_fact)

    with pytest.raises(ValueError, match="2025"):
        kpi_xbrl_module.resolve_binding(mutated, STREAMING_TOTAL_BINDING, "NFLX")

    # single-value signature+period (unmutated pack) still resolves cleanly.
    clean_points = kpi_xbrl_module.resolve_binding(
        signature_fact_pack, STREAMING_TOTAL_BINDING, "NFLX"
    )
    assert len(clean_points) == 3
    by_period = {p["period"]: p for p in clean_points}
    assert by_period["2025"]["value"] == 45183036000


def test_resolve_binding_dedupes_identical_duplicate(kpi_xbrl_module, signature_fact_pack):
    """REVISION (code-quality 🟡): two facts sharing the SAME dimensional
    signature AND the SAME period AND the SAME value must resolve to
    exactly ONE point — never two identical points (which would silently
    double-count downstream). Dedupe on agreement; a genuine value
    conflict (test_resolve_binding_raises_on_ambiguous_signature_period)
    still RAISES.
    """
    mutated = json.loads(json.dumps(signature_fact_pack))
    duplicate_2025_total = next(
        f
        for f in mutated["facts"]
        if f["concept"] == "us-gaap:Revenues"
        and f["dimensions"] == {"ProductOrService": "StreamingMember"}
        and f["period_end"] == "2025-12-31"
    )
    identical_duplicate = json.loads(json.dumps(duplicate_2025_total))  # SAME value
    mutated["facts"].append(identical_duplicate)

    points = kpi_xbrl_module.resolve_binding(mutated, STREAMING_TOTAL_BINDING, "NFLX")

    # still exactly 3 points (2023, 2024, 2025) — the duplicate collapsed
    # to ONE point for 2025, not two.
    assert len(points) == 3
    periods = sorted(p["period"] for p in points)
    assert periods == ["2023", "2024", "2025"]
    by_period = {p["period"]: p for p in points}
    assert by_period["2025"]["value"] == 45183036000


def test_resolve_binding_identity_key_carries_period_type_fy(
    kpi_xbrl_module, signature_fact_pack
):
    """Task 3 GREEN: the anti-fabrication identity/dedup key extends from
    (signature, period) to (signature, period_type, period) — scope A
    always sets period_type to the constant "FY" (scope B, quarterly, owns
    the real enumeration later; see Decision Log). Every emitted point
    carries period_type == "FY", and an identical-value duplicate (same
    signature, same period) still dedupes to exactly ONE point under the
    extended key — annual grouping is unchanged since every scope-A point
    is FY.
    """
    points = kpi_xbrl_module.resolve_binding(
        signature_fact_pack, STREAMING_TOTAL_BINDING, "NFLX"
    )
    assert len(points) == 3
    assert all(p["period_type"] == "FY" for p in points)

    mutated = json.loads(json.dumps(signature_fact_pack))
    duplicate_2025_total = next(
        f
        for f in mutated["facts"]
        if f["concept"] == "us-gaap:Revenues"
        and f["dimensions"] == {"ProductOrService": "StreamingMember"}
        and f["period_end"] == "2025-12-31"
    )
    identical_duplicate = json.loads(json.dumps(duplicate_2025_total))  # SAME value
    mutated["facts"].append(identical_duplicate)

    deduped_points = kpi_xbrl_module.resolve_binding(
        mutated, STREAMING_TOTAL_BINDING, "NFLX"
    )
    assert len(deduped_points) == 3
    by_period = {p["period"]: p for p in deduped_points}
    assert by_period["2025"]["value"] == 45183036000
    assert by_period["2025"]["period_type"] == "FY"


CCG_SEGMENT_BINDING = {
    "kpi_id": "ccg_segment_revenue",
    "sources": [
        {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "dimensions": {"StatementBusinessSegments": "ClientComputingGroupMember"},
            "source_kind": "xbrl-dimensional",
        },
    ],
}


def test_resolve_binding_restatement_newest_wins_with_dqc_flag(
    kpi_xbrl_module, restatement_fact_pack
):
    """Task 4 (overlap policy C): over a multi-filing span the SAME
    (signature, FY, period) is reported by two ADJACENT 10-Ks with a
    RESTATED value (different accession). Rather than aborting the whole
    series with the intra-filing ValueError, resolve_binding keeps the
    value from the most-recently-FILED 10-K and surfaces a machine-readable
    restatement DQC flag on the emitted point — never silently averaging or
    dropping. The REAL captured fixture is INTC's ClientComputingGroup
    FY2020 segment revenue, recast between the FY2021 10-K
    (0000050863-22-000007, filed 2022-01-27, 40057000000.0) and the FY2022
    10-K (0000050863-23-000006, filed 2023-01-27, 40535000000.0).
    """
    points = kpi_xbrl_module.resolve_binding(
        restatement_fact_pack, CCG_SEGMENT_BINDING, "INTC"
    )

    # cross-filing restatement is NOT a fatal conflict — exactly one point.
    assert len(points) == 1
    point = points[0]
    assert point["period"] == "2020"
    # newest-FILED 10-K wins.
    assert point["value"] == 40535000000.0
    assert point["source_accession"] == "0000050863-23-000006"

    dqc = point["dqc"]
    assert dqc["type"] == "restatement"
    assert dqc["old"] == 40057000000.0
    assert dqc["new"] == 40535000000.0
    assert dqc["superseded_accession"] == "0000050863-22-000007"
    assert dqc["kept_accession"] == "0000050863-23-000006"


def test_resolve_binding_same_accession_value_conflict_still_raises(
    kpi_xbrl_module, restatement_fact_pack
):
    """The intra-filing discriminator is UNCHANGED by policy C: two facts
    sharing the SAME signature AND period AND the SAME accession but
    DIFFERENT values are a genuine INTRA-filing ambiguity (one 10-K
    reporting a KPI twice with conflicting numbers) — that must still RAISE,
    never be silently resolved as a "restatement". Force both real
    restatement facts onto one accession (same filing) -> RAISE naming the
    period; only a CROSS-accession disagreement is a restatement.
    """
    mutated = json.loads(json.dumps(restatement_fact_pack))
    for fact in mutated["facts"]:
        fact["accession"] = "0000050863-22-000007"
        fact["filed"] = "2022-01-27"

    with pytest.raises(ValueError, match="2020"):
        kpi_xbrl_module.resolve_binding(mutated, CCG_SEGMENT_BINDING, "INTC")


AMERICAS_SEGMENT_BINDING = {
    "kpi_id": "americas_segment_revenue",
    "sources": [
        {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "dimensions": {"StatementBusinessSegments": "AmericasSegmentMember"},
            "source_kind": "xbrl-dimensional",
        },
    ],
}


def test_resolve_binding_consolidation_qualifier_operating_segments(
    kpi_xbrl_module, signature_fact_pack
):
    """Task 3 GREEN: `consolidation` (srt:ConsolidationItemsAxis member) is a
    reconciliation QUALIFIER, never a breakdown axis. resolve_binding matches
    a fact's (defaulted) `consolidation` against the source's (defaulted)
    `consolidation` — default "OperatingSegmentsMember" on both sides, so a
    segment binding with no `consolidation` key still resolves the
    operating-segments view without treating ConsolidationItems as a second
    breakdown axis (no false cross-dim rejection).
    """
    # (1) real fixture: AmericasSegmentMember segment binding resolves the
    # OperatingSegmentsMember-qualified FY2025 fact — exactly one clean point.
    points = kpi_xbrl_module.resolve_binding(
        signature_fact_pack, AMERICAS_SEGMENT_BINDING, "AAPL"
    )
    fy2025 = [p for p in points if p["period"] == "2025"]
    assert len(fy2025) == 1
    assert fy2025[0]["value"] == 178353000000

    # (2) synthetic pack: two facts share the SAME dimensions + period but
    # differ in `consolidation` (OperatingSegmentsMember vs an eliminations
    # view) — these are different consolidation VIEWS, not a value conflict
    # on the same signature. The default-OperatingSegments binding resolves
    # ONLY the operating-segments fact and must NOT raise.
    op_seg_fact = {
        "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "dimensions": {"StatementBusinessSegments": "AmericasSegmentMember"},
        "consolidation": "OperatingSegmentsMember",
        "value": 178353000000,
        "period_end": "2025-09-27",
        # Task 5: the producer now emits the full parallel-label group on
        # every fact — this synthetic fact mirrors that shape (annual 10-K
        # fact: 12mo → FY), per fixtures-mirror-producer-shape.
        "duration_months": 12,
        "calendar_year": 2025,
        "calendar_quarter": "Q3",
        "fiscal_year": 2025,
        "fiscal_quarter": "FY",
        "derivation_basis": "dei-declared",
        "accession": "0000320193-25-000079",
        "filed": "2025-10-31",
    }
    elimination_fact = {
        **op_seg_fact,
        "consolidation": "IntersegmentEliminationMember",
        "value": -5000000000,
    }
    synthetic_pack = {"company": "AAPL", "facts": [op_seg_fact, elimination_fact]}

    synthetic_points = kpi_xbrl_module.resolve_binding(
        synthetic_pack, AMERICAS_SEGMENT_BINDING, "AAPL"
    )
    assert len(synthetic_points) == 1
    assert synthetic_points[0]["value"] == 178353000000


ELIMINATIONS_SEGMENT_BINDING = {
    "kpi_id": "americas_segment_elimination",
    "sources": [
        {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "dimensions": {"StatementBusinessSegments": "AmericasSegmentMember"},
            "consolidation": "IntersegmentEliminationMember",
            "source_kind": "xbrl-dimensional",
        },
    ],
}


def test_resolve_binding_explicit_nondefault_consolidation(kpi_xbrl_module):
    """REVISION (code-quality 🔴): resolve_binding's first pass correctly
    groups a fact under a source whose `consolidation` explicitly names a
    NON-default view (e.g. "IntersegmentEliminationMember"), but the second
    pass (the per-source facts_to_points call) previously rebuilt its
    selector from only {concept, dimensions} — dropping `consolidation` —
    so facts_to_points re-filtered with the DEFAULT
    "OperatingSegmentsMember" and silently dropped the very fact the first
    pass just matched, returning [] instead of the eliminations point. A
    binding naming `consolidation="IntersegmentEliminationMember"` against a
    pack holding both an OperatingSegmentsMember fact and an
    IntersegmentEliminationMember fact (same dimensions+period, different
    values) must resolve ONLY the eliminations fact — exactly one point.
    """
    op_seg_fact = {
        "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "dimensions": {"StatementBusinessSegments": "AmericasSegmentMember"},
        "consolidation": "OperatingSegmentsMember",
        "value": 178353000000,
        "period_end": "2025-09-27",
        # Task 5: the producer now emits the full parallel-label group on
        # every fact — this synthetic fact mirrors that shape (annual 10-K
        # fact: 12mo → FY), per fixtures-mirror-producer-shape.
        "duration_months": 12,
        "calendar_year": 2025,
        "calendar_quarter": "Q3",
        "fiscal_year": 2025,
        "fiscal_quarter": "FY",
        "derivation_basis": "dei-declared",
        "accession": "0000320193-25-000079",
        "filed": "2025-10-31",
    }
    elimination_fact = {
        **op_seg_fact,
        "consolidation": "IntersegmentEliminationMember",
        "value": -5000000000,
    }
    synthetic_pack = {"company": "AAPL", "facts": [op_seg_fact, elimination_fact]}

    points = kpi_xbrl_module.resolve_binding(
        synthetic_pack, ELIMINATIONS_SEGMENT_BINDING, "AAPL"
    )
    assert len(points) == 1
    assert points[0]["value"] == -5000000000
    assert points[0]["kpi_id"] == "americas_segment_elimination"


def test_facts_to_points_fails_loud_new_shape(kpi_xbrl_module, signature_fact_pack):
    """REVISION (code-quality 🔴): the anti-fabrication guards were only
    exercised via the OLD axis/member shape (inside a now-xfailed test) —
    prove they fire on the NEW full-signature `dimensions`-map shape too.
    Each case isolates a single REAL NFLX streaming-total fact (dimensions=
    {"ProductOrService": "StreamingMember"}, FY2025) in its own one-fact
    pack with ONLY the tested field removed, so facts_to_points's ordered
    checks (value -> accession -> filed -> period_end) reach exactly that
    RAISE — the other three required fields stay intact, so no earlier
    check aborts first.
    """
    match = {
        "concept": "us-gaap:Revenues",
        "dimensions": {"ProductOrService": "StreamingMember"},
    }
    total_fact = next(
        f
        for f in signature_fact_pack["facts"]
        if f["concept"] == match["concept"]
        and f.get("dimensions") == match["dimensions"]
        and f["period_end"] == "2025-12-31"
    )

    def _pack_missing(field):
        fact = json.loads(json.dumps(total_fact))
        del fact[field]
        return {"company": "NFLX", "facts": [fact]}

    with pytest.raises(ValueError, match="value"):
        kpi_xbrl_module.facts_to_points(
            _pack_missing("value"), "streaming_revenue", match, "NFLX", "xbrl-dimensional"
        )
    with pytest.raises(ValueError, match="accession"):
        kpi_xbrl_module.facts_to_points(
            _pack_missing("accession"), "streaming_revenue", match, "NFLX", "xbrl-dimensional"
        )
    with pytest.raises(ValueError, match="filed"):
        kpi_xbrl_module.facts_to_points(
            _pack_missing("filed"), "streaming_revenue", match, "NFLX", "xbrl-dimensional"
        )
    with pytest.raises(ValueError, match="period_end"):
        kpi_xbrl_module.facts_to_points(
            _pack_missing("period_end"), "streaming_revenue", match, "NFLX", "xbrl-dimensional"
        )

    # malformed (non-YYYY-MM-DD) period_end — never fabricated as period "None"
    malformed = json.loads(json.dumps(total_fact))
    malformed["period_end"] = "not-a-date"
    with pytest.raises(ValueError, match="period_end"):
        kpi_xbrl_module.facts_to_points(
            {"company": "NFLX", "facts": [malformed]},
            "streaming_revenue", match, "NFLX", "xbrl-dimensional",
        )


def test_declared_break_splits_series_not_concat(kpi_xbrl_module, fact_pack):
    """Task 3 GREEN: the resolved iphone_revenue points (FY2016 old-tagged,
    FY2024/FY2025 new-tagged) run through build_series_with_break(points,
    "2018") and land in split_series's as_reported/recast partition by
    period — NOT a single concatenated run. FY2016 (period "2016" < "2018")
    -> as_reported; FY2024/FY2025 (period >= "2018") -> recast. All 3
    points accounted for exactly once (nothing dropped, nothing duplicated).
    """
    points = kpi_xbrl_module.resolve_binding(fact_pack, IPHONE_REVENUE_BINDING, "AAPL")
    assert len(points) == 3

    result = kpi_xbrl_module.build_series_with_break(points, "2018")

    as_reported_periods = sorted(p["period"] for p in result["as_reported"])
    recast_periods = sorted(p["period"] for p in result["recast"])
    assert as_reported_periods == ["2016"]
    assert recast_periods == ["2024", "2025"]

    # nothing dropped, nothing duplicated across the two partitions
    all_periods = sorted(
        p["period"] for p in result["as_reported"] + result["recast"]
    )
    assert all_periods == ["2016", "2024", "2025"]
    assert result["break_markers"] == [{"break_period": "2018"}]


# ---------------------------------------------------------------------------
# Task 5 (docs/loom/plans/2026-07-16-operational-kpi-quarterly.md) — classify
# period_type from the data layer's EMITTED labels; migrate period keying to
# the fiscal basis. Fixtures are PRODUCER-GENERATED (the real
# sec_edgar_client extraction/fact-builder ran over machine-captured raw
# rows — see each fixture's _provenance), per
# docs/loom/memory/fixtures-mirror-producer-shape.md.
# No `@req` tags: this dispatch traces work by named plan Tasks, not
# registered loom-spec REQ-ids (same convention as the module header note).
# ---------------------------------------------------------------------------

NVDA_COMPUTE_MATCH = {
    "concept": "us-gaap:Revenues",
    "dimensions": {"ProductOrService": "ComputeMember"},
}

AAPL_IPHONE_QUARTERLY_MATCH = {
    "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
    "dimensions": {"ProductOrService": "IPhoneMember"},
}


@pytest.fixture
def nvda_quarterly_pack():
    return json.loads(
        (FIXTURES / "xbrl_quarterly_nvda_factpack.json").read_text(encoding="utf-8")
    )


@pytest.fixture
def aapl_quarterly_pack():
    return json.loads(
        (FIXTURES / "xbrl_quarterly_aapl_labeled_factpack.json").read_text(encoding="utf-8")
    )


def test_classify_period_type(kpi_xbrl_module, nvda_quarterly_pack, aapl_quarterly_pack):
    """Task 5 RED: the analysis layer classifies each fact's period_type
    (Q1/Q2/Q3/Q4/FY) + cumulative flag + duration_class CONSUMING the data
    layer's emitted labels (fiscal_quarter + duration_months) — it never
    re-derives fiscal geometry (rebuild-findings §RESOLVED: data layer
    derives, analysis consumes). Cases per the plan's acceptance:
    3mo at fiscal Q1 end → Q1/single; a Sep-FYE filer's 3mo ending
    late-Dec → Q1; 9mo → 9mo-YTD cumulative; 6mo → 6mo-YTD cumulative;
    a comparative classified from its OWN labels; a stub/unclassifiable
    (pre-schema shape, no label group) surfaced — never guessed."""
    # NVDA (late-January FYE): 3-month fact at the fiscal Q1 end → Q1 single.
    nvda_points = kpi_xbrl_module.facts_to_points(
        nvda_quarterly_pack, "compute_revenue", NVDA_COMPUTE_MATCH,
        "NVDA", "xbrl-dimensional",
    )
    assert len(nvda_points) == 3
    nvda_q1 = next(p for p in nvda_points if p["value"] == 34155000000.0)
    assert nvda_q1["period_type"] == "Q1"
    assert nvda_q1["cumulative"] is False
    assert nvda_q1["duration_class"] == "3mo"

    # AAPL (late-September FYE) quarterly facts, producer-labeled.
    aapl_points = kpi_xbrl_module.facts_to_points(
        aapl_quarterly_pack, "iphone_revenue", AAPL_IPHONE_QUARTERLY_MATCH,
        "AAPL", "xbrl-dimensional",
    )
    assert len(aapl_points) == 5
    by_value = {p["value"]: p for p in aapl_points}

    # Sep-FYE 3mo ending late December → fiscal Q1 (of the NEXT-named FY).
    q1 = by_value[1000.0]
    assert (q1["period_type"], q1["cumulative"], q1["duration_class"]) == (
        "Q1", False, "3mo",
    )
    assert q1["period"] == "2025"  # FY2025 despite calendar_year 2024
    # 6-month H1 → 6mo-YTD cumulative, distinct from the 3mo Q2 single.
    h1 = by_value[3000.0]
    assert (h1["period_type"], h1["cumulative"], h1["duration_class"]) == (
        "Q2", True, "6mo-YTD",
    )
    # 9-month YTD → 9mo-YTD cumulative, never a single quarter.
    ytd9 = by_value[4000.0]
    assert (ytd9["period_type"], ytd9["cumulative"], ytd9["duration_class"]) == (
        "Q3", True, "9mo-YTD",
    )
    # Prior-year comparative classified from its OWN labels (FY2024-Q2),
    # never the carrying filing's Q2/FY2025 focus stamped.
    comparative = by_value[1500.0]
    assert comparative["period"] == "2024"
    assert (comparative["period_type"], comparative["duration_class"]) == (
        "Q2", "3mo",
    )

    # Stub/unclassifiable: a pre-schema fact (bare edgartools-column
    # fiscal_year, NO emitted label group) is SURFACED via a distinct
    # raise — period_type is never guessed from period_end/calendar.
    stub_fact = {
        "concept": "us-gaap:Revenues",
        "dimensions": {"ProductOrService": "ComputeMember"},
        "value": 999.0,
        "period_end": "2025-10-26",
        "fiscal_year": 2025,  # the raw dataframe column, NOT our label group
        "accession": "0001045810-25-000230",
        "filed": "2025-11-19",
    }
    with pytest.raises(ValueError, match="unclassifiable"):
        kpi_xbrl_module.facts_to_points(
            {"company": "NVDA", "facts": [stub_fact]},
            "compute_revenue", NVDA_COMPUTE_MATCH, "NVDA", "xbrl-dimensional",
        )


def test_classify_uses_filing_dei_focus_not_calendar(kpi_xbrl_module, aapl_quarterly_pack):
    """Task 5 RED — the spec's Q2 scenario asserted LITERALLY (spec.md
    'non-December fiscal-year-end classifies by the filing's dei calendar'):
    GIVEN a company whose dei:CurrentFiscalYearEndDate is late September and
    a 10-Q with dei:DocumentFiscalPeriodFocus=Q2 for a fact ending in late
    March, WHEN the fact is classified THEN it is fiscal-Q2 (per the
    filing's dei calendar), not calendar-Q1."""
    # Ground the GIVEN in the pack's own per-filing dei calendar.
    q2_calendar = aapl_quarterly_pack["fiscal_calendars"]["0000320193-25-000057"]
    assert q2_calendar["fiscal_year_end"] == "--09-27"  # late September
    assert q2_calendar["fiscal_period_focus"] == "Q2"

    points = kpi_xbrl_module.facts_to_points(
        aapl_quarterly_pack, "iphone_revenue", AAPL_IPHONE_QUARTERLY_MATCH,
        "AAPL", "xbrl-dimensional",
    )
    # The 3-month fact ending 2025-03-29 (late March).
    q2_single = next(p for p in points if p["value"] == 2000.0)
    assert q2_single["period_type"] == "Q2"        # fiscal-Q2 per dei calendar
    assert q2_single["calendar_quarter"] == "Q1"   # NOT its calendar position
    assert q2_single["cumulative"] is False


def test_period_key_is_fiscal_not_calendar(kpi_xbrl_module, nvda_quarterly_pack):
    """Task 5 RED: series keying migrates off `period_end[:4]` (the ruled
    latent bug — calendar year) onto the EMITTED fiscal_year: the real NVDA
    FY2026-Q3 fact (period_end 2025-10-26, fiscal_year 2026) keys under
    "2026", never "2025" — while the calendar pair stays available on the
    point (the calendarization basis, rebuild-findings §RESOLVED (b))."""
    points = kpi_xbrl_module.facts_to_points(
        nvda_quarterly_pack, "compute_revenue", NVDA_COMPUTE_MATCH,
        "NVDA", "xbrl-dimensional",
    )
    q3 = next(p for p in points if p["value"] == 43028000000.0)
    assert q3["period"] == "2026"
    # The calendar basis remains available on the point, honestly named.
    assert q3["calendar_year"] == 2025
    assert q3["calendar_quarter"] == "Q4"


def test_fact_pack_na_slot_is_not_read_as_empty_series(kpi_xbrl_module):
    """Task 5 RED (Wave-1 review findings, plan Decision Log 2026-07-17):
    (a) a foreign-private-issuer N/A slot (T4's error_class, which
    deliberately omits `facts`) is branched on BEFORE
    `fact_pack.get("facts", [])` at BOTH read sites — it must RAISE loudly,
    never be consumed as a real empty series; (b) a `None` per-filing
    calendar routes to the surfaced-unclassifiable path, never a calendar
    default."""
    # Producer-shaped N/A slot (mirrors _foreign_private_issuer_na_slot).
    na_slot = {
        "error": (
            "SEC EDGAR dimensional-revenue extraction failed for 'TSM' "
            "(10-Q): submissions form history has 20-F + 6-K but no 10-Q"
        ),
        "error_class": "foreign_private_issuer_no_quarterly_xbrl",
        "identifier": "TSM",
        "reason": "submissions form history has 20-F + 6-K but no 10-Q",
    }
    with pytest.raises(ValueError, match="foreign_private_issuer_no_quarterly_xbrl"):
        kpi_xbrl_module.facts_to_points(
            na_slot, "compute_revenue", NVDA_COMPUTE_MATCH, "TSM", "xbrl-dimensional",
        )
    with pytest.raises(ValueError, match="foreign_private_issuer_no_quarterly_xbrl"):
        kpi_xbrl_module.resolve_binding(
            na_slot,
            {"kpi_id": "compute_revenue", "sources": [
                {**NVDA_COMPUTE_MATCH, "source_kind": "xbrl-dimensional"},
            ]},
            "TSM",
        )

    # A None per-filing calendar (T3's unreadable-calendar shape): the
    # filing's facts carry no derivable label group — surfaced
    # unclassifiable, NEVER silently keyed by the calendar year.
    none_calendar_pack = {
        "company": "NVDA",
        "facts": [{
            "concept": "us-gaap:Revenues",
            "dimensions": {"ProductOrService": "ComputeMember"},
            "value": 123.0,
            "period_end": "2025-10-26",
            "accession": "0001045810-25-000230",
            "filed": "2025-11-19",
        }],
        "fiscal_calendars": {"0001045810-25-000230": None},
    }
    with pytest.raises(ValueError, match="unclassifiable"):
        kpi_xbrl_module.facts_to_points(
            none_calendar_pack, "compute_revenue", NVDA_COMPUTE_MATCH,
            "NVDA", "xbrl-dimensional",
        )


def test_cli_build_resolves_binding_and_prints_points(tmp_path):
    """Task 6 GREEN: the `build` subcommand reads a fact-pack JSON from
    stdin and a binding JSON from --binding, resolves it via
    resolve_binding, and prints the points list. Mirrors
    kpi_memo_feed.py's CLI + exit-code convention: 0 success, 1 on a
    resolve ValueError (e.g. ambiguous binding), 2 on malformed/non-object
    fact-pack JSON — no raw traceback either way.
    """
    fact_pack = json.loads((FIXTURES / "xbrl_aapl_factpack.json").read_text(encoding="utf-8"))
    binding_path = tmp_path / "binding.json"
    binding_path.write_text(json.dumps(IPHONE_REVENUE_BINDING), encoding="utf-8")

    # (a) success: fact-pack via stdin, binding via --binding -> exit 0.
    ok_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_XBRL_SCRIPT), "build",
            "--company", "AAPL", "--binding", str(binding_path),
        ],
        input=json.dumps(fact_pack),
        capture_output=True, text=True, timeout=60,
    )
    assert ok_result.returncode == 0, ok_result.stderr
    points = json.loads(ok_result.stdout)
    assert len(points) == 3
    assert all(p["kpi_id"] == "iphone_revenue" for p in points)

    # (b) ambiguous binding -> resolve_binding ValueError -> exit 1.
    ambiguous_path = tmp_path / "ambiguous.json"
    ambiguous_path.write_text(json.dumps(AMBIGUOUS_OVERLAPPING_BINDING), encoding="utf-8")
    ambiguous_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_XBRL_SCRIPT), "build",
            "--company", "AAPL", "--binding", str(ambiguous_path),
        ],
        input=json.dumps(fact_pack),
        capture_output=True, text=True, timeout=60,
    )
    assert ambiguous_result.returncode == 1, ambiguous_result.stderr
    assert "ambiguous" in ambiguous_result.stderr
    assert "Traceback" not in ambiguous_result.stderr

    # (c) malformed fact-pack JSON on stdin -> exit 2, no raw traceback.
    malformed_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_XBRL_SCRIPT), "build",
            "--company", "AAPL", "--binding", str(binding_path),
        ],
        input="{not valid json",
        capture_output=True, text=True, timeout=60,
    )
    assert malformed_result.returncode == 2, malformed_result.stderr
    assert "Traceback" not in malformed_result.stderr

    # (d) non-object fact-pack JSON (a JSON array) -> exit 2.
    non_object_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_XBRL_SCRIPT), "build",
            "--company", "AAPL", "--binding", str(binding_path),
        ],
        input="[]",
        capture_output=True, text=True, timeout=60,
    )
    assert non_object_result.returncode == 2, non_object_result.stderr

    # (e) --help lists the `build` subcommand.
    help_result = subprocess.run(
        ["uv", "run", "--script", str(KPI_XBRL_SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert help_result.returncode == 0
    assert "build" in help_result.stdout
