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
from unittest import mock

from conftest import FIXTURES, KPI_STORE_SCRIPT, KPI_XBRL_SCRIPT

import pytest


@pytest.fixture(scope="module")
def kpi_xbrl_module():
    spec = importlib.util.spec_from_file_location("kpi_xbrl_test", KPI_XBRL_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_xbrl_test"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def kpi_store_module():
    """kpi_store.py loaded for its `same_period` predicate — the CONSUMER
    Task 2's store-shaped fields (period_start/period_kind/scale) exist to
    feed. Same importlib convention as `kpi_xbrl_module` above / test_kpi_
    store.py's own `kpi_store_module` fixture."""
    spec = importlib.util.spec_from_file_location("kpi_store_test_via_xbrl", KPI_STORE_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_store_test_via_xbrl"] = module
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
    # T9 schema migration: the ONE DQC schema replaces the pilot's
    # superseded_accession/kept_accession field names — the audit content
    # (both accessions, roles) is preserved as accessions=[superseded,
    # kept] + reason (policy-C parity intact).
    assert dqc["accessions"] == [
        "0000050863-22-000007", "0000050863-23-000006",
    ]
    assert dqc["reason"]


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


def test_facts_to_points_emits_store_period_identity(
    kpi_xbrl_module, kpi_store_module, restatement_fact_pack, monkeypatch,
):
    """Task 2 (docs/loom/plans/2026-07-24-market-period-granularity, arc
    (d)): every emitted point becomes STORE-SHAPED — `period_start` passes
    through from the fact (T1's new sec_edgar_client.py field), `period_kind`
    is synthesized "duration"/"instant" from the point's own `period_type`,
    and `scale` is hardcoded 1 (mirrors kpi_prose_candidates.py's shipped
    shape, ~:695). WHY: kpi_store's `same_period`/`_qtrs` need period_start
    (+ period_kind) to GROUP cross-filing vintages of one annual period into
    a restatement — without them each vintage's period-identity axis is null
    and nothing ever groups.

    Fixture: the REAL captured restatement pack (INTC ClientComputingGroup
    FY2020, two 10-Ks, same period_end 2020-12-26, different accession/
    value — already used by test_resolve_binding_restatement_newest_wins_
    with_dqc_flag above) augmented ONLY with `period_start` (additive
    mutation, same real-fact-mutation convention this file already uses
    elsewhere, e.g. the accession override two tests up) — Intel's real
    FY2020 started 2019-12-29, identical on both vintages since they
    describe the SAME annual period.
    """
    mutated = json.loads(json.dumps(restatement_fact_pack))
    for fact in mutated["facts"]:
        fact["period_start"] = "2019-12-29"

    points = kpi_xbrl_module.facts_to_points(
        mutated, "ccg_segment_revenue", CCG_SEGMENT_BINDING["sources"][0],
        "INTC", "xbrl-dimensional",
    )
    assert len(points) == 2
    for p in points:
        assert p["period_start"] == "2019-12-29"
        assert p["period_kind"] == "duration"  # point's period_type "FY" != "instant"
        assert p["scale"] == 1
        # additive-only: pre-existing fields survive unchanged.
        assert p["period_type"] == "FY"
        assert p["cumulative"] is False
        assert p["duration_class"] == "12mo-FY"
        assert p["period_end"] == "2020-12-26"

    # GREEN load-bearing assertion: the two vintages now GROUP as the same
    # real annual period via kpi_store's own predicate — proving the fields
    # actually unblock grouping, not just presence.
    assert kpi_store_module.same_period(points[0], points[1]) is True

    # The "instant" branch: no producer reaching this module emits an
    # instant-context fact today — extract_dimensional_revenue excludes
    # instant contexts upstream (sec_edgar_client.py's
    # `_build_dimensional_revenue_fact` docstring), so classify_fact_period's
    # real output domain is frozenset {Q1,Q2,Q3,Q4,FY}, never "instant".
    # Force the branch via the module's own classification hook to prove the
    # mapping is correct for a genuinely-instant point — forward-defensive
    # for a future instant-context producer (e.g. balance-sheet KPIs).
    monkeypatch.setattr(
        kpi_xbrl_module, "classify_fact_period",
        lambda fact: {
            "period_type": "instant", "cumulative": False,
            "duration_class": "instant",
        },
    )
    instant_points = kpi_xbrl_module.facts_to_points(
        mutated, "ccg_segment_revenue", CCG_SEGMENT_BINDING["sources"][0],
        "INTC", "xbrl-dimensional",
    )
    assert instant_points[0]["period_kind"] == "instant"


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
    synthetic_pack = {
        "company": "AAPL",
        "facts": [op_seg_fact, elimination_fact],
        # T9: the per-accession calendar channel grounding source_form
        # (producer packs always carry it; mirrored here).
        "fiscal_calendars": {
            "0000320193-25-000079": {
                "fiscal_period_focus": "FY",
                "fiscal_year_end": "--09-27",
                "fiscal_year_focus": "2025",
            },
        },
    }

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
    synthetic_pack = {
        "company": "AAPL",
        "facts": [op_seg_fact, elimination_fact],
        # T9: the per-accession calendar channel grounding source_form
        # (producer packs always carry it; mirrored here).
        "fiscal_calendars": {
            "0000320193-25-000079": {
                "fiscal_period_focus": "FY",
                "fiscal_year_end": "--09-27",
                "fiscal_year_focus": "2025",
            },
        },
    }

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


def test_classify_period_week_lane(kpi_xbrl_module):
    """Task 3 fix round 2 (spec-reviewer NEEDS_REVISION on 111e4530):
    class-lane precedence — the month map is tried FIRST; only when
    `duration_months` misses it (8 not in {3,6,9,12}) does the week lane
    get a chance. The week lane is now a PURE TRANSCRIPTION of the
    producer's OWN `week_lane_band` label (sec_edgar_client's
    `_week_lane_class(span_days)` result) — never re-decided here from
    `duration_weeks` alone. A fact whose producer-emitted `week_lane_band`
    is "YTD-through-Q3" -> "36wk-YTD", cumulative, fiscal_quarter Q3
    (mirrors the shipped "9mo-YTD"/Q3 month-lane pattern). A sibling fact
    with the SAME month-lane miss but no week-lane signal at all (neither
    lane can classify it) still raises unclassifiable — fail-closed
    unchanged, never guessed."""
    week_lane_fact = {
        "concept": "us-gaap:Revenues",
        "period_end": "2026-05-10",
        "fiscal_year": 2026,
        "fiscal_quarter": "Q3",
        "duration_months": 8,
        "duration_weeks": 36,
        "week_lane_band": "YTD-through-Q3",
        "accession": "0000320193-26-000123",
    }
    classification = kpi_xbrl_module.classify_fact_period(week_lane_fact)
    assert classification == {
        "period_type": "Q3",
        "cumulative": True,
        "duration_class": "36wk-YTD",
    }

    no_week_lane_fact = {
        "concept": "us-gaap:Revenues",
        "period_end": "2026-05-10",
        "fiscal_year": 2026,
        "fiscal_quarter": "Q3",
        "duration_months": 8,
        "accession": "0000320193-26-000123",
    }
    with pytest.raises(ValueError, match="unclassifiable"):
        kpi_xbrl_module.classify_fact_period(no_week_lane_fact)


def test_classify_period_week_lane_divergence_producer_out_of_band(kpi_xbrl_module):
    """RED (spec-reviewer NEEDS_REVISION on 111e4530, verbatim counter-
    example): a fact whose `duration_weeks` ROUNDS to 36 (e.g. a 253-day
    span: round(253/7)=36) but whose PRODUCER-emitted `week_lane_band` is
    None — the producer's own `_week_lane_class(253)` rejects it, since
    253 falls outside the tight [251, 252] window for the 36-week
    cluster — must raise unclassifiable, never guess "36wk-YTD" from the
    rounded int alone. This reproduces the shipped-code bug: the old
    int-membership match (`duration_weeks in week_counts`) accepted ANY
    duration_weeks==36 regardless of the producer's tighter day-span
    decision, silently reintroducing the edgartools #816 two-path
    desync the shared `_week_lane_class` primitive exists to prevent."""
    divergent_fact = {
        "concept": "us-gaap:Revenues",
        "period_end": "2026-05-12",
        "fiscal_year": 2026,
        "fiscal_quarter": "Q3",
        "duration_months": 8,
        "duration_weeks": 36,
        "week_lane_band": None,
        "accession": "0000320193-26-000123",
    }
    with pytest.raises(ValueError, match="unclassifiable"):
        kpi_xbrl_module.classify_fact_period(divergent_fact)


def test_classify_period_week_lane_format_branches(kpi_xbrl_module):
    """Quality 🟡 (fix round 2): pin every REACHABLE week-lane format
    branch (plan Notes/docstring: only "week-Q4" and "YTD-through-Q3" are
    ever actually reached in practice, since "quarter"/"H1"/"FY" band
    members already round into the month lane, which has precedence) —
    a 16wk week-Q4 fact -> "16wk" (no suffix), a 17wk week-Q4 fact ->
    "17wk" (same band, other week-count member), and an H1 fact ->
    "24wk-YTD" (the "-YTD" suffix branch), all via `classify_fact_period`
    with month-miss `duration_months` values (4, 4, 5) matching the real
    `_duration_months` rounding for 111d/119d/167d spans."""
    week_q4_16 = {
        "concept": "us-gaap:Revenues",
        "period_end": "2026-06-30",
        "fiscal_year": 2026,
        "fiscal_quarter": "Q4",
        "duration_months": 4,
        "duration_weeks": 16,
        "week_lane_band": "week-Q4",
        "accession": "0000320193-26-000123",
    }
    assert kpi_xbrl_module.classify_fact_period(week_q4_16)["duration_class"] == "16wk"

    week_q4_17 = {
        "concept": "us-gaap:Revenues",
        "period_end": "2026-06-30",
        "fiscal_year": 2026,
        "fiscal_quarter": "Q4",
        "duration_months": 4,
        "duration_weeks": 17,
        "week_lane_band": "week-Q4",
        "accession": "0000320193-26-000123",
    }
    assert kpi_xbrl_module.classify_fact_period(week_q4_17)["duration_class"] == "17wk"

    h1_24 = {
        "concept": "us-gaap:Revenues",
        "period_end": "2026-05-10",
        "fiscal_year": 2026,
        "fiscal_quarter": "Q2",
        "duration_months": 5,
        "duration_weeks": 24,
        "week_lane_band": "H1",
        "accession": "0000320193-26-000123",
    }
    assert kpi_xbrl_module.classify_fact_period(h1_24)["duration_class"] == "24wk-YTD"


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


# ---------------------------------------------------------------------------
# Task 6 (docs/loom/plans/2026-07-16-operational-kpi-quarterly.md) — the
# resolve_binding identity key gains duration_class: single-quarter vs YTD
# de-conflated; cross-filing dedupe + policy C on the duration-qualified
# key; divergent cross-filing fiscal labels flagged with a deterministic
# survivor. Fixture xbrl_quarterly_dualdur.json is PRODUCER-GENERATED (the
# real _build_dimensional_revenue_fact/_derive_fiscal_label ran over raw
# rows — see its _provenance), per
# docs/loom/memory/fixtures-mirror-producer-shape.md.
# No `@req` tags: this dispatch traces work by named plan Tasks, not
# registered loom-spec REQ-ids (same convention as the module header note).
# ---------------------------------------------------------------------------

DUALDUR_IPHONE_BINDING = {
    "kpi_id": "iphone_revenue",
    "sources": [
        {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "dimensions": {"ProductOrService": "IPhoneMember"},
            "source_kind": "xbrl-dimensional",
        },
    ],
}

FYECHG_SEGMENT_BINDING = {
    "kpi_id": "alpha_segment_revenue",
    "sources": [
        {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "dimensions": {"StatementBusinessSegments": "AlphaSegmentMember"},
            "source_kind": "xbrl-dimensional",
        },
    ],
}


@pytest.fixture
def dualdur_fixture():
    return json.loads(
        (FIXTURES / "xbrl_quarterly_dualdur.json").read_text(encoding="utf-8")
    )


def test_identity_key_deconflates_quarter_from_ytd(kpi_xbrl_module, dualdur_fixture):
    """Task 6 RED: the identity/dedup key gains duration_class (spec: 'The
    identity key de-conflates single-quarter from year-to-date').
    (a) De-conflation: the real Q3-10-Q dual-duration collision (3mo AND
    9mo-YTD for one signature at period_end 2025-06-28, same accession,
    different values) resolves to TWO distinct points — never deduped and
    never RAISEd against each other (pre-Task-6 the two collide on the
    (period_type, fiscal_year) key and abort as an intra-filing ambiguity —
    the T5 LOOM-SIMPLIFY ceiling).
    (b) Cross-filing identical single-quarter (FY2025-Q2 3mo, identical
    value, reported in the FY2025 Q2 10-Q and again as a comparative in the
    FY2026 Q2 10-Q) dedupes to ONE point on the duration-qualified key.
    (c) A restated quarter (FY2025-Q1 3mo, different values across the two
    filings) applies policy C on the duration-qualified key: the
    newest-FILED filing's value wins + a restatement DQC flag (scope-A
    parity)."""
    pack = dualdur_fixture["aapl_dualdur"]
    points = kpi_xbrl_module.resolve_binding(pack, DUALDUR_IPHONE_BINDING, "AAPL")

    # 6 facts -> 4 points: Q3 3mo + Q3 9mo-YTD + deduped Q2 + resolved Q1.
    assert len(points) == 4

    # (a) single-quarter and YTD at the same period_end stay DISTINCT.
    q3_points = [p for p in points if p["period_type"] == "Q3"]
    assert len(q3_points) == 2
    by_duration = {p["duration_class"]: p for p in q3_points}
    assert set(by_duration) == {"3mo", "9mo-YTD"}
    assert by_duration["3mo"]["value"] == 4100.0
    assert by_duration["3mo"]["cumulative"] is False
    assert by_duration["9mo-YTD"]["value"] == 11100.0
    assert by_duration["9mo-YTD"]["cumulative"] is True
    assert all(p["period"] == "2025" for p in q3_points)
    # neither carries any conflict flag — they were never raised against
    # each other.
    assert all("dqc" not in p for p in q3_points)

    # (b) identical cross-filing single-quarter dedupes to exactly one.
    q2_points = [p for p in points if p["period_type"] == "Q2"]
    assert len(q2_points) == 1
    assert q2_points[0]["value"] == 2000.0
    assert q2_points[0]["duration_class"] == "3mo"
    assert "dqc" not in q2_points[0]

    # (c) restated quarter -> policy C: newest-filed wins + DQC flag.
    q1_points = [p for p in points if p["period_type"] == "Q1"]
    assert len(q1_points) == 1
    q1 = q1_points[0]
    assert q1["value"] == 1050.0
    assert q1["source_accession"] == "0000320193-26-000006"
    assert q1["dqc"]["type"] == "restatement"
    assert q1["dqc"]["old"] == 1000.0
    assert q1["dqc"]["new"] == 1050.0
    # T9 schema migration: accessions=[superseded, kept] + reason replace
    # the retired superseded_accession/kept_accession names — full audit
    # content (old, new, both accessions) preserved, policy-C parity.
    assert q1["dqc"]["accessions"] == [
        "0000320193-25-000008", "0000320193-26-000006",
    ]
    assert q1["dqc"]["reason"]


def test_dedup_label_conflict_deterministic(kpi_xbrl_module, dualdur_fixture):
    """Task 6 RED (critic round 2 — spec: 'a cross-filing fiscal-label
    divergence at dedup is flagged, with a deterministic survivor'):
    identical values for one signature/period_end/duration from two filings
    whose dei calendars yield DIFFERENT fiscal labels (the fixture's
    FYE-change filer: --06-30 labels the 2024-06-28 3mo window Q4/FY2024,
    --09-30 labels it Q3/FY2024) collapse to ONE point; the label conflict
    is flagged (ONE DQC schema, BOTH source calendars recorded) and the
    surviving label is the LATER-FILED filing's — deterministic, never an
    arbitrary pick and never two duplicate points."""
    pack = dualdur_fixture["fye_change_label_conflict"]
    points = kpi_xbrl_module.resolve_binding(pack, FYECHG_SEGMENT_BINDING, "FYECHG")

    assert len(points) == 1
    point = points[0]
    assert point["value"] == 500.0
    # the LATER-FILED filing's label survives, deterministically.
    assert point["source_accession"] == "0000000000-25-000002"
    assert point["period_type"] == "Q3"
    assert point["period"] == "2024"
    assert point["duration_class"] == "3mo"

    dqc = point["dqc"]
    assert dqc["type"] == "label_conflict"
    # the ONE DQC schema (type, old, new, accessions, reason) — old/new
    # carry the diverging labels WITH both source filings' dei calendars.
    assert dqc["old"]["fiscal_year"] == 2024
    assert dqc["old"]["fiscal_quarter"] == "Q4"
    assert dqc["old"]["accession"] == "0000000000-24-000001"
    assert dqc["old"]["fiscal_calendar"]["fiscal_year_end"] == "--06-30"
    assert dqc["new"]["fiscal_year"] == 2024
    assert dqc["new"]["fiscal_quarter"] == "Q3"
    assert dqc["new"]["accession"] == "0000000000-25-000002"
    assert dqc["new"]["fiscal_calendar"]["fiscal_year_end"] == "--09-30"
    assert dqc["accessions"] == ["0000000000-24-000001", "0000000000-25-000002"]
    assert dqc["reason"]


# ---------------------------------------------------------------------------
# Task 7 (docs/loom/plans/2026-07-16-operational-kpi-quarterly.md) — single-
# granularity series (annual vs quarterly never mixed), the dimension-absent-
# from-quarterlies flag surfaced at the series build (calling the data
# layer's pure `_dimension_quarterly_absence`), and the fiscal-range output
# filter on each fact's OWN fiscal label. Fixtures: the committed
# producer-shaped T5/T6 packs (xbrl_quarterly_aapl_labeled_factpack.json /
# xbrl_quarterly_dualdur.json / xbrl_signature_factpack.json) plus two
# synthetic ANNUAL facts mirroring the producer's emitted label-group shape
# (12mo -> FY), per docs/loom/memory/fixtures-mirror-producer-shape.md.
# No `@req` tags: this dispatch traces work by named plan Tasks, not
# registered loom-spec REQ-ids (same convention as the module header note).
# ---------------------------------------------------------------------------

# Producer-shaped synthetic 10-K facts (annual: 12mo -> fiscal_quarter FY),
# same signature family as the AAPL labeled quarterly pack. The iPhone
# signature IS tagged in that pack's 10-Qs; the Mac signature appears in NO
# 10-Q — the spec's "dimension absent from the quarterlies" case.
ANNUAL_IPHONE_FACT = {
    "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
    "dimensions": {"ProductOrService": "IPhoneMember"},
    "value": 10000.0,
    "period_end": "2025-09-27",
    "duration_months": 12,
    "calendar_year": 2025,
    "calendar_quarter": "Q3",
    "fiscal_year": 2025,
    "fiscal_quarter": "FY",
    "derivation_basis": "dei-declared",
    "accession": "0000320193-25-000079",
    "filed": "2025-10-31",
}

ANNUAL_MAC_FACT = {
    **ANNUAL_IPHONE_FACT,
    "dimensions": {"ProductOrService": "MacMember"},
    "value": 5000.0,
}


@pytest.fixture
def stub_data_layer_deps():
    """build_series_with_break's absence-flag path lazily imports
    sec_edgar_client, which does a MODULE-LEVEL `import requests` (and
    lazily imports `edgar`) — neither installed in the offline suite env —
    so both are stubbed in sys.modules first and restored after (mirrors
    test_kpi_xbrl_multifiling_e2e.sec_edgar_helpers; docs/loom/memory/
    importing-a-module-runs-its-module-level-imports.md). Only the PURE
    `_dimension_quarterly_absence` helper is exercised — the stubs are
    never touched."""
    saved = {name: sys.modules.get(name) for name in ("requests", "edgar")}
    sys.modules["requests"] = mock.MagicMock(name="requests")
    sys.modules["edgar"] = mock.MagicMock(name="edgar")
    try:
        yield
    finally:
        for name, mod in saved.items():
            if mod is not None:
                sys.modules[name] = mod
            else:
                sys.modules.pop(name, None)


def test_series_single_granularity(
    kpi_xbrl_module, signature_fact_pack, aapl_quarterly_pack
):
    """Task 7 RED (spec: 'A series carries a single granularity'): a
    quarterly request returns ONLY single-quarter points — no FY totals
    (and no YTD cumulatives: the spec's quarterly-series scenario admits
    'only single-quarter (and, if enabled, derived-Q4) points'); an annual
    request returns only FY points; and a set mixing FY + single-quarter
    for one fiscal year with NO granularity requested is REJECTED loud —
    never silently averaged or concatenated. The result is
    granularity-labeled."""
    # Real FY points (signature pack, NEW-era iPhone: FY2023-2025) + real
    # quarterly points (labeled pack: FY2025 Q1/Q2/H1/9mo + FY2024-Q2
    # comparative) — fiscal year 2025 carries BOTH an FY total and quarters.
    fy_points = kpi_xbrl_module.facts_to_points(
        signature_fact_pack, "iphone_revenue", AAPL_IPHONE_QUARTERLY_MATCH,
        "AAPL", "xbrl-dimensional",
    )
    assert len(fy_points) == 3
    assert all(p["period_type"] == "FY" for p in fy_points)
    q_points = kpi_xbrl_module.facts_to_points(
        aapl_quarterly_pack, "iphone_revenue", AAPL_IPHONE_QUARTERLY_MATCH,
        "AAPL", "xbrl-dimensional",
    )
    assert len(q_points) == 5
    mixed = fy_points + q_points

    # Quarterly request -> only sub-annual single-quarter points: the three
    # 3mo facts (Q1 1000, Q2 2000, FY2024-Q2 comparative 1500) — the FY
    # totals AND the 6mo/9mo cumulatives are off-granularity, excluded.
    quarterly = kpi_xbrl_module.build_series_with_break(
        mixed, "2018", granularity="quarterly"
    )
    emitted = quarterly["as_reported"] + quarterly["recast"]
    assert sorted(p["value"] for p in emitted) == [1000.0, 1500.0, 2000.0]
    assert all(p["period_type"] in {"Q1", "Q2", "Q3", "Q4"} for p in emitted)
    assert all(p["cumulative"] is False for p in emitted)
    assert quarterly["granularity"] == "quarterly"

    # Annual request -> only the FY totals.
    annual = kpi_xbrl_module.build_series_with_break(
        mixed, "2018", granularity="annual"
    )
    emitted_fy = annual["as_reported"] + annual["recast"]
    assert sorted(p["period"] for p in emitted_fy) == ["2023", "2024", "2025"]
    assert all(p["period_type"] == "FY" for p in emitted_fy)
    assert annual["granularity"] == "annual"

    # No granularity requested + mixed input -> the mix is REJECTED loud.
    with pytest.raises(ValueError, match="granularit"):
        kpi_xbrl_module.build_series_with_break(mixed, "2018")


def test_series_flags_dimension_absent_from_quarterlies(
    kpi_xbrl_module, aapl_quarterly_pack, stub_data_layer_deps
):
    """Task 7 RED (spec: 'a dimension absent from the quarterlies is
    flagged, not zero-filled'; re-homed from old T10 per the plan's
    2026-07-17 Decision Log): a dimensional signature present in the 10-K
    (Mac) but tagged in NO 10-Q of that fiscal year surfaces on the built
    quarterly series as a `no_quarterly_coverage` coverage flag — computed
    by the data layer's pure `_dimension_quarterly_absence`, carrying NO
    `value` key (distinct from a real zero) and a flag naming ONLY missing
    quarterly tagging (distinct from a discontinued segment — that
    judgment stays the caller's). A 10-K signature that IS quarterly-
    tagged (iPhone) is not flagged."""
    q_points = kpi_xbrl_module.facts_to_points(
        aapl_quarterly_pack, "iphone_revenue", AAPL_IPHONE_QUARTERLY_MATCH,
        "AAPL", "xbrl-dimensional",
    )
    facts = aapl_quarterly_pack["facts"] + [ANNUAL_IPHONE_FACT, ANNUAL_MAC_FACT]

    result = kpi_xbrl_module.build_series_with_break(
        q_points, "2018", granularity="quarterly", facts=facts
    )

    # The series points themselves are the quarterly series, unchanged.
    emitted = result["as_reported"] + result["recast"]
    assert sorted(p["value"] for p in emitted) == [1000.0, 1500.0, 2000.0]

    # Exactly ONE coverage flag: the Mac signature — no `value` key (never
    # zero-filled), never a discontinued-segment verdict, covered iPhone
    # not flagged. T9 schema migration: the entry follows the ONE DQC
    # schema (type/old/new/accessions/reason) with the identifying
    # signature riding along as locating fields; `accessions` names the
    # 10-K that DID tag the signature.
    assert result["coverage_flags"] == [{
        "type": "no_quarterly_coverage",
        "old": None,
        "new": None,
        "accessions": ["0000320193-25-000079"],
        "reason": result["coverage_flags"][0]["reason"],
        "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "dimensions": {"ProductOrService": "MacMember"},
        "consolidation": None,
        "fiscal_year": 2025,
    }]
    assert "value" not in result["coverage_flags"][0]
    assert "never zero-filled" in result["coverage_flags"][0]["reason"]


def test_series_range_filtered_by_own_fiscal_label(
    kpi_xbrl_module, aapl_quarterly_pack, dualdur_fixture
):
    """Task 7 RED (critic round 2 — spec: 'emitted points are
    range-filtered by each fact's OWN fiscal label'): with a fiscal-range
    request, only points whose OWN emitted fiscal label falls in-range are
    emitted — a selected FY2025 10-Q's FY2024 comparative is never emitted
    as a series point — while out-of-range-filing comparatives remain
    usable INTERNALLY: the filter applies to emitted points AFTER
    resolve_binding's dedup/restatement, so a restatement carried by a
    later filing's comparative survives."""
    points = kpi_xbrl_module.facts_to_points(
        aapl_quarterly_pack, "iphone_revenue", AAPL_IPHONE_QUARTERLY_MATCH,
        "AAPL", "xbrl-dimensional",
    )
    # the FY2024-Q2 comparative (own fiscal label 2024) is present pre-filter.
    assert any(p["period"] == "2024" for p in points)

    result = kpi_xbrl_module.build_series_with_break(
        points, "2018", fiscal_range=(2025, 2025)
    )
    emitted = result["as_reported"] + result["recast"]
    assert sorted(p["value"] for p in emitted) == [1000.0, 2000.0, 3000.0, 4000.0]
    assert all(p["period"] == "2025" for p in emitted)  # comparative filtered

    # Internal usability: the dualdur restated Q1 (policy C resolved from
    # the FY2026 Q2 10-Q's comparative) keeps its restated value + DQC flag
    # through a [2025, 2025] range build — the range filter never undoes
    # dedup/restatement work done with a later filing's comparatives.
    pack = dualdur_fixture["aapl_dualdur"]
    dd_points = kpi_xbrl_module.resolve_binding(pack, DUALDUR_IPHONE_BINDING, "AAPL")
    dd_result = kpi_xbrl_module.build_series_with_break(
        dd_points, "2018", fiscal_range=(2025, 2025)
    )
    dd_emitted = dd_result["as_reported"] + dd_result["recast"]
    assert len(dd_emitted) == 4
    q1 = next(p for p in dd_emitted if p["period_type"] == "Q1")
    assert q1["value"] == 1050.0
    assert q1["source_accession"] == "0000320193-26-000006"
    assert q1["dqc"]["type"] == "restatement"


# ---------------------------------------------------------------------------
# Task 7 review follow-up (code-quality-reviewer 🟡): five input-validation
# arms in build_series_with_break/_validate_fiscal_range/_point_fiscal_year
# shipped with zero test coverage. Exercised via the PUBLIC
# build_series_with_break entry point (matching this file's own convention
# of never testing the underscore-prefixed helpers directly) with minimal
# synthetic points/facts — none of these arms need a real fact pack.
# ---------------------------------------------------------------------------

def test_validate_fiscal_range_rejects_malformed_shape_and_bounds(kpi_xbrl_module):
    """`_validate_fiscal_range` fail-loud arm: a `fiscal_range` that is not
    unpackable into exactly (since, until), or whose bounds are not plain
    ints (bool included — bool is a python int subclass but explicitly
    rejected), or that is inverted (since > until), never silently emits
    everything — each shape raises naming the specific defect."""
    # not a (since, until) pair — too few elements to unpack.
    with pytest.raises(ValueError, match="pair"):
        kpi_xbrl_module.build_series_with_break([], "2018", fiscal_range=(2020,))
    # not a (since, until) pair — not iterable at all.
    with pytest.raises(ValueError, match="pair"):
        kpi_xbrl_module.build_series_with_break([], "2018", fiscal_range=2020)
    # a non-int bound.
    with pytest.raises(ValueError, match="integers"):
        kpi_xbrl_module.build_series_with_break(
            [], "2018", fiscal_range=(2020, "2025")
        )
    # a bool bound — excluded even though isinstance(True, int) is True.
    with pytest.raises(ValueError, match="integers"):
        kpi_xbrl_module.build_series_with_break([], "2018", fiscal_range=(True, 2025))
    # inverted range.
    with pytest.raises(ValueError, match="inverted"):
        kpi_xbrl_module.build_series_with_break([], "2018", fiscal_range=(2025, 2020))


def test_build_series_rejects_unknown_granularity(kpi_xbrl_module):
    """The `granularity not in _SERIES_GRANULARITIES` guard: a value other
    than "annual"/"quarterly"/None raises naming the unknown value — never
    silently treated as "no granularity requested"."""
    with pytest.raises(ValueError, match="unknown granularity"):
        kpi_xbrl_module.build_series_with_break([], "2018", granularity="monthly")


def test_build_series_rejects_facts_without_quarterly_granularity(kpi_xbrl_module):
    """The `facts is not None and granularity != "quarterly"` guard: the
    no-quarterly-coverage flagging input is defined for the quarterly
    series build only — passing `facts` with no granularity (or with
    granularity="annual") raises rather than silently ignoring `facts` or
    computing flags that don't apply to the requested series."""
    with pytest.raises(ValueError, match="requires granularity"):
        kpi_xbrl_module.build_series_with_break([], "2018", facts=[{"concept": "x"}])
    with pytest.raises(ValueError, match="requires granularity"):
        kpi_xbrl_module.build_series_with_break(
            [], "2018", granularity="annual", facts=[{"concept": "x"}]
        )


def test_point_fiscal_year_rejects_non_int_period(kpi_xbrl_module):
    """`_point_fiscal_year`'s fail-loud arm (only reached once `fiscal_range`
    is set, since that's the only caller): a point whose `period` is not
    int-parseable — a non-numeric string, or the key missing outright — is
    surfaced rather than guessed in or out of the requested range."""
    with pytest.raises(ValueError, match="cannot range-filter"):
        kpi_xbrl_module.build_series_with_break(
            [{"period": "not-a-year", "kpi_id": "x"}],
            "2018", fiscal_range=(2020, 2025),
        )
    with pytest.raises(ValueError, match="cannot range-filter"):
        kpi_xbrl_module.build_series_with_break(
            [{"kpi_id": "x"}],  # no "period" key at all
            "2018", fiscal_range=(2020, 2025),
        )


def test_coverage_flag_kept_when_fiscal_year_not_plain_int(
    kpi_xbrl_module, stub_data_layer_deps
):
    """The coverage-flag range-filter's keep branch (spec comment: 'a flag
    whose fiscal_year is not an int cannot be placed and stays SURFACED,
    never silently dropped'): a `no_quarterly_coverage` flag whose
    `fiscal_year` is a non-int (string) or a bool survives a fiscal_range
    filter that would otherwise exclude it by value — because it can't be
    placed in the range at all, not because it happens to fall inside it.
    `fiscal_range=(2030, 2040)` deliberately excludes both facts' would-be
    numeric year (2025) to prove the keep is unconditional, not coincidental.
    """
    non_int_fy_fact = {
        "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "dimensions": {"ProductOrService": "NonIntFYMember"},
        "consolidation": None,
        "value": 1.0,
        "period_end": "2025-09-27",
        "duration_months": 12,
        "fiscal_year": "2025",  # non-int — always kept, range-independent
        "fiscal_quarter": "FY",
        "accession": "acc-non-int-fy",
        "filed": "2025-10-31",
    }
    bool_fy_fact = {
        **non_int_fy_fact,
        "dimensions": {"ProductOrService": "BoolFYMember"},
        "fiscal_year": True,  # bool — excluded from the "valid year" arm
        "accession": "acc-bool-fy",
    }

    result = kpi_xbrl_module.build_series_with_break(
        [], "2018", granularity="quarterly",
        fiscal_range=(2030, 2040),
        facts=[non_int_fy_fact, bool_fy_fact],
    )

    flagged_dims = {tuple(sorted(f["dimensions"].items())) for f in result["coverage_flags"]}
    assert (("ProductOrService", "NonIntFYMember"),) in flagged_dims
    assert (("ProductOrService", "BoolFYMember"),) in flagged_dims


# ---------------------------------------------------------------------------
# Task 8 (docs/loom/plans/2026-07-16-operational-kpi-quarterly.md) — derive an
# untagged Q4 single-quarter as (FY total − 9mo-YTD), guarded (skip on a
# missing source, refuse on a basis/vintage/unit/calendar mismatch),
# SEGREGATED (computed DQC flag + derived lane a reported-only request
# excludes), dual-accession provenance, and the three label groups minted
# from the derived 3-month window against the 10-K's dei calendar. Fixture
# xbrl_q4_derive.json is producer-shaped per the T5/T6 pattern — real AAPL
# FY2025 windows/accessions/calendars copied from the producer-generated
# dualdur fixture; counterfactual rows (reported Q4, restating FY2026 10-K,
# unit fields, --06-30 calendar) documented in its _provenance
# (docs/loom/memory/fixtures-mirror-producer-shape.md).
# No `@req` tags: this dispatch traces work by named plan Tasks, not
# registered loom-spec REQ-ids (same convention as the module header note).
# ---------------------------------------------------------------------------


@pytest.fixture
def q4_fixture():
    return json.loads(
        (FIXTURES / "xbrl_q4_derive.json").read_text(encoding="utf-8")
    )


def test_q4_derive_guarded_segregated(kpi_xbrl_module, q4_fixture):
    """Task 8 RED (spec: 'Q4 single-quarter is derived by subtraction,
    guarded, and segregated'): (a) with an FY total and a 9mo-YTD in hand
    and NO directly-tagged Q4, derivation emits a Q4 point equal to
    FY − 9mo-YTD, flagged computed (DQC `derived_q4`) with BOTH
    contributing accessions, in a segregated lane; (b) the default
    quarterly series includes it while a reported-only request excludes it
    (reported Q1-Q3 remain); (c) a missing source is skipped AND surfaced —
    never fabricated; (d)/(e) a restatement-vintage or unit/scale mismatch
    between the two inputs REFUSES with `q4_basis_mismatch` — a flag
    DISTINCT from the clean derived flag, never a silent subtraction;
    (f) a directly-tagged Q4 short-circuits derivation — the reported
    fact is used unchanged, no computed flag."""
    # (a) derive when both inputs exist, segregated + dual-accession.
    pack = q4_fixture["aapl_q4_derive"]
    points = kpi_xbrl_module.resolve_binding(pack, DUALDUR_IPHONE_BINDING, "AAPL")
    assert not any(p["period_type"] == "Q4" for p in points)  # Q4 untagged
    result = kpi_xbrl_module.derive_q4_points(
        points, fiscal_calendars=pack["fiscal_calendars"]
    )
    assert len(result["points"]) == 1
    q4 = result["points"][0]
    assert q4["value"] == 3000.0  # 14100.0 FY − 11100.0 9mo-YTD
    assert q4["period_type"] == "Q4"
    assert q4["cumulative"] is False
    assert q4["duration_class"] == "3mo"
    assert q4["period"] == "2025"
    assert q4["derived"] is True  # the segregated lane marker
    assert q4["dqc"]["type"] == "derived_q4"  # computed, never reported
    assert sorted(q4["dqc"]["accessions"]) == [
        "0000320193-25-000073", "0000320193-25-000079",
    ]
    assert q4["source_accessions"] == [
        "0000320193-25-000079", "0000320193-25-000073",
    ]
    assert result["gaps"] == []

    # (b) segregation end-to-end: the quarterly series includes the derived
    # Q4 by default; a reported-only request excludes it, Q1-Q3 remain.
    all_points = points + result["points"]
    quarterly = kpi_xbrl_module.build_series_with_break(
        all_points, "2018", granularity="quarterly"
    )
    emitted = quarterly["as_reported"] + quarterly["recast"]
    assert sorted(p["value"] for p in emitted) == [1000.0, 2000.0, 3000.0, 4100.0]
    reported = kpi_xbrl_module.build_series_with_break(
        all_points, "2018", granularity="quarterly", reported_only=True
    )
    reported_emitted = reported["as_reported"] + reported["recast"]
    assert sorted(p["value"] for p in reported_emitted) == [1000.0, 2000.0, 4100.0]
    assert all(
        p["period_type"] in {"Q1", "Q2", "Q3"} for p in reported_emitted
    )

    # (c) missing 9mo-YTD source -> skip + surface, never fabricate.
    missing = json.loads(json.dumps(pack))
    missing["facts"] = [
        f for f in missing["facts"] if f.get("duration_months") != 9
    ]
    m_points = kpi_xbrl_module.resolve_binding(
        missing, DUALDUR_IPHONE_BINDING, "AAPL"
    )
    m_result = kpi_xbrl_module.derive_q4_points(
        m_points, fiscal_calendars=missing["fiscal_calendars"]
    )
    assert m_result["points"] == []
    assert len(m_result["gaps"]) == 1
    gap = m_result["gaps"][0]
    assert gap["type"] == "q4_source_missing"
    assert gap["period"] == "2025"
    assert gap["accessions"] == ["0000320193-25-000079"]
    assert "9mo-YTD" in gap["reason"]

    # (d) restatement-vintage mismatch -> refusal with a DISTINCT flag.
    v_pack = q4_fixture["q4_vintage_mismatch"]
    v_points = kpi_xbrl_module.resolve_binding(
        v_pack, DUALDUR_IPHONE_BINDING, "AAPL"
    )
    v_fy = next(p for p in v_points if p["period_type"] == "FY")
    assert v_fy["dqc"]["type"] == "restatement"  # policy C ran upstream
    v_result = kpi_xbrl_module.derive_q4_points(
        v_points, fiscal_calendars=v_pack["fiscal_calendars"]
    )
    assert v_result["points"] == []  # never a silent subtraction
    assert len(v_result["gaps"]) == 1
    v_gap = v_result["gaps"][0]
    assert v_gap["type"] == "q4_basis_mismatch"
    assert v_gap["type"] != "derived_q4"  # distinct from the clean flag
    assert "vintage" in v_gap["reason"]
    assert sorted(v_gap["accessions"]) == [
        "0000320193-25-000073", "0000320193-26-000079",
    ]

    # (e) XBRL unit/scale mismatch -> the same refusal lane.
    u_pack = q4_fixture["q4_unit_mismatch"]
    u_points = kpi_xbrl_module.resolve_binding(
        u_pack, DUALDUR_IPHONE_BINDING, "AAPL"
    )
    u_result = kpi_xbrl_module.derive_q4_points(
        u_points, fiscal_calendars=u_pack["fiscal_calendars"]
    )
    assert u_result["points"] == []
    assert len(u_result["gaps"]) == 1
    assert u_result["gaps"][0]["type"] == "q4_basis_mismatch"
    assert "unit" in u_result["gaps"][0]["reason"]

    # (f) a directly-tagged Q4 short-circuits: used as-is, no derivation,
    # no computed flag, no gap.
    r_pack = q4_fixture["q4_reported_shortcircuit"]
    r_points = kpi_xbrl_module.resolve_binding(
        r_pack, DUALDUR_IPHONE_BINDING, "AAPL"
    )
    r_result = kpi_xbrl_module.derive_q4_points(
        r_points, fiscal_calendars=r_pack["fiscal_calendars"]
    )
    assert r_result["points"] == []
    assert r_result["gaps"] == []
    reported_q4 = next(p for p in r_points if p["period_type"] == "Q4")
    assert reported_q4["value"] == 3333.0  # NOT 3000.0 — used unchanged
    assert "dqc" not in reported_q4
    assert not reported_q4.get("derived")


def test_q4_derived_carries_parallel_labels(kpi_xbrl_module, q4_fixture):
    """Task 8 RED (critic round 2 — spec: 'a derived Q4 carries the three
    label groups, grounded in the 10-K's calendar'): the derived point
    carries (1) the RAW WINDOW of the derived 3-month span (day after the
    9mo-YTD end through the FY end), (2) the CALENDAR label mechanically
    minted from that window's period_end, and (3) the FISCAL label
    grounded in the 10-K's dei calendar (fiscal 2025, Q4 by construction
    of the window ending on the fiscal year end). When the two source
    filings declare DIFFERENT fiscal calendars, the basis-mismatch
    refusal applies — labels are never minted across two calendars."""
    pack = q4_fixture["aapl_q4_derive"]
    points = kpi_xbrl_module.resolve_binding(pack, DUALDUR_IPHONE_BINDING, "AAPL")
    result = kpi_xbrl_module.derive_q4_points(
        points, fiscal_calendars=pack["fiscal_calendars"]
    )
    q4 = result["points"][0]
    # (1) raw window — the derived 3-month span.
    assert q4["period_start"] == "2025-06-29"
    assert q4["period_end"] == "2025-09-27"
    assert q4["duration_class"] == "3mo"
    # (2) calendar label — the calendar quarter containing period_end.
    assert q4["calendar_year"] == 2025
    assert q4["calendar_quarter"] == "Q3"
    # (3) fiscal label — grounded in the 10-K's dei calendar (--09-27),
    # never a bare fabrication: period key is the 10-K's fiscal year.
    assert (
        pack["fiscal_calendars"]["0000320193-25-000079"]["fiscal_year_end"]
        == "--09-27"
    )
    assert q4["period"] == "2025"
    assert q4["period_type"] == "Q4"

    # Source filings declaring DIFFERENT fiscal calendars -> the
    # basis-mismatch refusal (spec: 'if X and Y declare different fiscal
    # calendars, the basis-mismatch refusal below applies').
    c_pack = q4_fixture["q4_calendar_mismatch"]
    c_points = kpi_xbrl_module.resolve_binding(
        c_pack, DUALDUR_IPHONE_BINDING, "AAPL"
    )
    c_result = kpi_xbrl_module.derive_q4_points(
        c_points, fiscal_calendars=c_pack["fiscal_calendars"]
    )
    assert c_result["points"] == []
    assert len(c_result["gaps"]) == 1
    assert c_result["gaps"][0]["type"] == "q4_basis_mismatch"
    assert "calendar" in c_result["gaps"][0]["reason"]


# ---------------------------------------------------------------------------
# Task 4 (docs/loom/plans/2026-07-18-52-53-week-filer-support.md) — Q4
# derivation on the week lane: a week-lane-eligible FY point (month-classed
# "12mo-FY" carrying duration_weeks 52/53) minus its matching 36wk-YTD point
# mints a derived Q4 with duration_weeks = FY_weeks - YTD_weeks (16 or 17),
# gated on the WEEK-LANE YTD SIBLING'S PRESENCE — never on the FY point's
# duration_weeks alone (a month-lane 365d calendar-year FY also carries
# duration_weeks 52). Synthetic packs, machine-shaped like the module's
# other week-lane fixtures (test_classify_period_week_lane) and the
# existing derive_q4_points synthetic packs (both_restated_pack above) —
# no hand-typed real XBRL values. No `@req` tags: this dispatch traces work
# by named plan Tasks, not registered loom-spec REQ-ids (same convention as
# the module header note).
# ---------------------------------------------------------------------------

COST_MEMBERSHIP_MATCH = {
    "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
    "dimensions": {"ProductOrService": "MembershipFeesMember"},
}


def _cost_week_lane_fact_pack(*, include_ytd: bool = True) -> dict:
    """A COST-shaped (53-week fiscal year) synthetic fact pack: a 12mo-FY
    fact carrying `duration_weeks=53` and, unless `include_ytd=False`, its
    matching 36wk-YTD sibling (`duration_weeks=36`, producer `week_lane_band`
    "YTD-through-Q3") — full fact shape (concept, dimensions, accession,
    filed, dei fiscal calendar) matching the producer's own emitted shape."""
    fy_fact = {
        "concept": COST_MEMBERSHIP_MATCH["concept"],
        "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
        "consolidation": None,
        "period_end": "2026-08-30",
        "fiscal_year": 2026,
        "fiscal_quarter": "FY",
        "duration_months": 12,
        "duration_weeks": 53,
        "week_lane_band": "FY",
        "accession": "0000909832-26-000123",
        "filed": "2026-10-15",
        "value": 100000.0,
    }
    facts = [fy_fact]
    fiscal_calendars = {
        "0000909832-26-000123": {
            "fiscal_period_focus": "FY", "fiscal_year_end": "--08-30",
        },
    }
    if include_ytd:
        ytd_fact = {
            "concept": COST_MEMBERSHIP_MATCH["concept"],
            "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
            "consolidation": None,
            "period_end": "2026-05-10",
            "fiscal_year": 2026,
            "fiscal_quarter": "Q3",
            "duration_months": 8,
            "duration_weeks": 36,
            "week_lane_band": "YTD-through-Q3",
            "accession": "0000909832-26-000099",
            "filed": "2026-06-05",
            "value": 78000.0,
        }
        facts.append(ytd_fact)
        fiscal_calendars["0000909832-26-000099"] = {
            "fiscal_period_focus": "Q3", "fiscal_year_end": "--08-30",
        }
    return {"company": "COST", "facts": facts, "fiscal_calendars": fiscal_calendars}


def test_q4_derive_week_lane_mint(kpi_xbrl_module):
    """Task 4 RED: a week-lane-eligible FY point (month-classed "12mo-FY"
    carrying duration_weeks=53) minus its matching 36wk-YTD point mints a
    derived Q4 with duration_weeks == 17 (53 - 36), duration_class "17wk"
    (T3's week-Q4 format, transcribed, never invented here), and the 2.23.0
    derived-tagging rules unchanged (derived: True, plural
    source_accessions/source_forms, verbatim dqc transcription)."""
    pack = _cost_week_lane_fact_pack()
    points = kpi_xbrl_module.facts_to_points(
        pack, "membership_fees", COST_MEMBERSHIP_MATCH, "COST", "xbrl-dimensional",
    )
    assert not any(p["period_type"] == "Q4" for p in points)  # Q4 untagged
    result = kpi_xbrl_module.derive_q4_points(
        points, fiscal_calendars=pack["fiscal_calendars"]
    )
    assert result["gaps"] == []
    assert len(result["points"]) == 1
    q4 = result["points"][0]
    assert q4["value"] == 22000.0  # 100000.0 FY - 78000.0 36wk-YTD
    assert q4["period_type"] == "Q4"
    assert q4["cumulative"] is False
    assert q4["duration_class"] == "17wk"
    assert q4["duration_weeks"] == 17
    assert q4["period"] == "2026"
    assert q4["derived"] is True  # the segregated lane marker
    assert q4["dqc"]["type"] == "derived_q4"  # computed, never reported
    assert sorted(q4["dqc"]["accessions"]) == [
        "0000909832-26-000099", "0000909832-26-000123",
    ]
    assert q4["source_accessions"] == [
        "0000909832-26-000123", "0000909832-26-000099",
    ]
    assert q4["source_forms"] == ["10-K", "10-Q"]


def test_q4_derive_week_lane_missing_sibling_refuses(kpi_xbrl_module):
    """Task 4 RED: when the week-lane YTD anchor (36wk-YTD) is absent, the
    EXISTING q4_source_missing refusal fires exactly as today (fail-closed
    unchanged) — the same code path as the month lane's missing-9mo-YTD
    case, never a fabricated week-lane subtraction."""
    pack = _cost_week_lane_fact_pack(include_ytd=False)
    points = kpi_xbrl_module.facts_to_points(
        pack, "membership_fees", COST_MEMBERSHIP_MATCH, "COST", "xbrl-dimensional",
    )
    result = kpi_xbrl_module.derive_q4_points(
        points, fiscal_calendars=pack["fiscal_calendars"]
    )
    assert result["points"] == []
    assert len(result["gaps"]) == 1
    gap = result["gaps"][0]
    assert gap["type"] == "q4_source_missing"
    assert gap["period"] == "2026"


def test_q4_derive_week_lane_not_triggered_by_fy_duration_weeks_alone(
    kpi_xbrl_module,
):
    """Correctness guard (plan Task 4): a month-lane 365-day calendar-year
    FY fact ALSO carries duration_weeks=52 (365/7 rounds to 52) — the
    week-lane derivation must NOT fire off that alone; it is gated on the
    presence of a GENUINE week-lane YTD sibling (36wk-YTD class), never on
    the FY point's duration_weeks. A month-lane FY + 9mo-YTD pair (FY
    carrying duration_weeks=52, no 36wk-YTD sibling in the group) still
    derives the ordinary month-lane "3mo" Q4 — byte-identical to the
    pre-Task-4 behavior."""
    fy_fact = {
        "concept": COST_MEMBERSHIP_MATCH["concept"],
        "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
        "consolidation": None,
        "period_end": "2026-09-27",
        "fiscal_year": 2026,
        "fiscal_quarter": "FY",
        "duration_months": 12,
        "duration_weeks": 52,  # calendar-year FY also carries a week count
        "accession": "acc-fy-cal",
        "filed": "2026-10-30",
        "value": 14100.0,
    }
    ytd9_fact = {
        "concept": COST_MEMBERSHIP_MATCH["concept"],
        "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
        "consolidation": None,
        "period_end": "2026-06-28",
        "fiscal_year": 2026,
        "fiscal_quarter": "Q3",
        "duration_months": 9,
        "accession": "acc-ytd9-cal",
        "filed": "2026-07-30",
        "value": 11100.0,
    }
    pack = {
        "company": "COST", "facts": [fy_fact, ytd9_fact],
        "fiscal_calendars": {
            "acc-fy-cal": {"fiscal_period_focus": "FY",
                           "fiscal_year_end": "--09-27"},
            "acc-ytd9-cal": {"fiscal_period_focus": "Q3",
                              "fiscal_year_end": "--09-27"},
        },
    }
    points = kpi_xbrl_module.facts_to_points(
        pack, "membership_fees", COST_MEMBERSHIP_MATCH, "COST", "xbrl-dimensional",
    )
    result = kpi_xbrl_module.derive_q4_points(
        points, fiscal_calendars=pack["fiscal_calendars"]
    )
    assert result["gaps"] == []
    assert len(result["points"]) == 1
    q4 = result["points"][0]
    assert q4["value"] == 3000.0  # 14100.0 FY - 11100.0 9mo-YTD
    assert q4["duration_class"] == "3mo"  # month lane, NOT a week-lane class
    assert "duration_weeks" not in q4


def test_q4_derive_mixed_lane_ambiguous_refuses(kpi_xbrl_module):
    """Fix round 2 RED (quality-reviewer finding on 1465a8bd): a group
    carrying BOTH a genuine 9mo-YTD candidate AND a genuine 36wk-YTD
    candidate alongside its FY total must REFUSE — never silently prefer
    the week lane and drop the month-lane candidate with no trace. Distinct
    `q4_basis_ambiguous` gap type, never a mint."""
    fy_fact = {
        "concept": COST_MEMBERSHIP_MATCH["concept"],
        "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
        "consolidation": None,
        "period_end": "2026-08-30",
        "fiscal_year": 2026,
        "fiscal_quarter": "FY",
        "duration_months": 12,
        "duration_weeks": 53,
        "week_lane_band": "FY",
        "accession": "acc-fy-mixed",
        "filed": "2026-10-15",
        "value": 100000.0,
    }
    ytd9_fact = {
        "concept": COST_MEMBERSHIP_MATCH["concept"],
        "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
        "consolidation": None,
        "period_end": "2026-05-30",
        "fiscal_year": 2026,
        "fiscal_quarter": "Q3",
        "duration_months": 9,
        "accession": "acc-ytd9-mixed",
        "filed": "2026-06-15",
        "value": 75000.0,
    }
    ytd36wk_fact = {
        "concept": COST_MEMBERSHIP_MATCH["concept"],
        "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
        "consolidation": None,
        "period_end": "2026-05-10",
        "fiscal_year": 2026,
        "fiscal_quarter": "Q3",
        "duration_months": 8,
        "duration_weeks": 36,
        "week_lane_band": "YTD-through-Q3",
        "accession": "acc-ytd36-mixed",
        "filed": "2026-06-05",
        "value": 78000.0,
    }
    pack = {
        "company": "COST",
        "facts": [fy_fact, ytd9_fact, ytd36wk_fact],
        "fiscal_calendars": {
            "acc-fy-mixed": {"fiscal_period_focus": "FY",
                              "fiscal_year_end": "--08-30"},
            "acc-ytd9-mixed": {"fiscal_period_focus": "Q3",
                                "fiscal_year_end": "--08-30"},
            "acc-ytd36-mixed": {"fiscal_period_focus": "Q3",
                                 "fiscal_year_end": "--08-30"},
        },
    }
    points = kpi_xbrl_module.facts_to_points(
        pack, "membership_fees", COST_MEMBERSHIP_MATCH, "COST", "xbrl-dimensional",
    )
    result = kpi_xbrl_module.derive_q4_points(
        points, fiscal_calendars=pack["fiscal_calendars"]
    )
    assert result["points"] == []  # never a silent week-lane (or month-lane) pick
    assert len(result["gaps"]) == 1
    gap = result["gaps"][0]
    assert gap["type"] == "q4_basis_ambiguous"
    assert gap["period"] == "2026"
    assert sorted(gap["accessions"]) == [
        "acc-fy-mixed", "acc-ytd36-mixed", "acc-ytd9-mixed",
    ]


def test_q4_derive_week_lane_mint_16wk(kpi_xbrl_module):
    """Mirror of test_q4_derive_week_lane_mint for the 16wk (52-week fiscal
    year) member of T3's week-Q4 format: FY carrying duration_weeks=52
    minus its 36wk-YTD sibling mints duration_weeks == 16, duration_class
    "16wk"."""
    fy_fact = {
        "concept": COST_MEMBERSHIP_MATCH["concept"],
        "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
        "consolidation": None,
        "period_end": "2026-08-29",
        "fiscal_year": 2026,
        "fiscal_quarter": "FY",
        "duration_months": 12,
        "duration_weeks": 52,
        "week_lane_band": "FY",
        "accession": "0000909832-26-000456",
        "filed": "2026-10-15",
        "value": 90000.0,
    }
    ytd_fact = {
        "concept": COST_MEMBERSHIP_MATCH["concept"],
        "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
        "consolidation": None,
        "period_end": "2026-05-09",
        "fiscal_year": 2026,
        "fiscal_quarter": "Q3",
        "duration_months": 8,
        "duration_weeks": 36,
        "week_lane_band": "YTD-through-Q3",
        "accession": "0000909832-26-000321",
        "filed": "2026-06-05",
        "value": 68000.0,
    }
    pack = {
        "company": "COST",
        "facts": [fy_fact, ytd_fact],
        "fiscal_calendars": {
            "0000909832-26-000456": {"fiscal_period_focus": "FY",
                                      "fiscal_year_end": "--08-29"},
            "0000909832-26-000321": {"fiscal_period_focus": "Q3",
                                      "fiscal_year_end": "--08-29"},
        },
    }
    points = kpi_xbrl_module.facts_to_points(
        pack, "membership_fees", COST_MEMBERSHIP_MATCH, "COST", "xbrl-dimensional",
    )
    result = kpi_xbrl_module.derive_q4_points(
        points, fiscal_calendars=pack["fiscal_calendars"]
    )
    assert result["gaps"] == []
    assert len(result["points"]) == 1
    q4 = result["points"][0]
    assert q4["value"] == 22000.0  # 90000.0 FY - 68000.0 36wk-YTD
    assert q4["duration_class"] == "16wk"
    assert q4["duration_weeks"] == 16


# ---------------------------------------------------------------------------
# Task 5 (docs/loom/plans/2026-07-18-52-53-week-filer-support.md) —
# supplementary week-normalized YoY: when a point's YoY comparator (same
# signature group, same period_type, prior fiscal year) carries a
# DIFFERENT duration_weeks, build_quarterly_series attaches
# `week_normalized_yoy` = (value/weeks) / (prior_value/prior_weeks) - 1 —
# as-reported `value` never touched; a missing comparator, an EQUAL-week
# comparator, or either side missing duration_weeks gets NO supplementary
# field. Fixture built from two fiscal years of the same COST-shaped
# week-lane signature (mirrors _cost_week_lane_fact_pack above) so the
# derived Q4 points land a real, week-mismatched comparator pair. No
# `@req` tags: this dispatch traces work by named plan Tasks, not
# registered loom-spec REQ-ids (same convention as the module header note).
# ---------------------------------------------------------------------------


def _cost_two_year_week_lane_fact_pack(*, fy2025_weeks: int = 52) -> dict:
    """Two fiscal years of COST-shaped week-lane facts in ONE signature
    group: FY2026 (53wk FY, 36wk-YTD -> derived Q4 = 17wk) and FY2025
    (`fy2025_weeks`wk FY, 36wk-YTD -> derived Q4 = fy2025_weeks - 36 wk) —
    a real YoY comparator pair for the supplementary week-normalized YoY.
    `fy2025_weeks=52` (default) gives a DIFFERENT-week Q4 pair (16wk prior
    vs 17wk current); `fy2025_weeks=53` gives an EQUAL-week pair (17wk vs
    17wk) to pin the negative case."""
    facts = [
        {
            "concept": COST_MEMBERSHIP_MATCH["concept"],
            "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
            "consolidation": None,
            "period_end": "2026-08-30",
            "fiscal_year": 2026, "fiscal_quarter": "FY",
            "duration_months": 12, "duration_weeks": 53,
            "week_lane_band": "FY",
            "accession": "acc-fy26", "filed": "2026-10-15",
            "value": 100000.0,
        },
        {
            "concept": COST_MEMBERSHIP_MATCH["concept"],
            "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
            "consolidation": None,
            "period_end": "2026-05-10",
            "fiscal_year": 2026, "fiscal_quarter": "Q3",
            "duration_months": 8, "duration_weeks": 36,
            "week_lane_band": "YTD-through-Q3",
            "accession": "acc-ytd26", "filed": "2026-06-05",
            "value": 78000.0,
        },
        {
            "concept": COST_MEMBERSHIP_MATCH["concept"],
            "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
            "consolidation": None,
            "period_end": "2025-08-31",
            "fiscal_year": 2025, "fiscal_quarter": "FY",
            "duration_months": 12, "duration_weeks": fy2025_weeks,
            "week_lane_band": "FY",
            "accession": "acc-fy25", "filed": "2025-10-15",
            "value": 88000.0,
        },
        {
            "concept": COST_MEMBERSHIP_MATCH["concept"],
            "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
            "consolidation": None,
            "period_end": "2025-05-11",
            "fiscal_year": 2025, "fiscal_quarter": "Q3",
            "duration_months": 8, "duration_weeks": 36,
            "week_lane_band": "YTD-through-Q3",
            "accession": "acc-ytd25", "filed": "2025-06-05",
            "value": 68000.0,
        },
    ]
    fiscal_calendars = {
        "acc-fy26": {"fiscal_period_focus": "FY", "fiscal_year_end": "--08-30"},
        "acc-ytd26": {"fiscal_period_focus": "Q3", "fiscal_year_end": "--08-30"},
        "acc-fy25": {"fiscal_period_focus": "FY", "fiscal_year_end": "--08-31"},
        "acc-ytd25": {"fiscal_period_focus": "Q3", "fiscal_year_end": "--08-31"},
    }
    return {"company": "COST", "facts": facts, "fiscal_calendars": fiscal_calendars}


def test_quarterly_series_attaches_week_normalized_yoy_on_different_week_pair(
    kpi_xbrl_module,
):
    """Task 5 RED: two derived Q4 points a fiscal year apart with DIFFERENT
    duration_weeks (17wk 2026 vs 16wk 2025) get the supplementary
    `week_normalized_yoy` on the CURRENT point, computed as (value/weeks) /
    (prior_value/prior_weeks) - 1; as-reported `value` is untouched, and
    `duration_weeks` rides through onto both points (propagation half of
    Task 5)."""
    pack = _cost_two_year_week_lane_fact_pack(fy2025_weeks=52)
    result = kpi_xbrl_module.build_quarterly_series(pack)
    assert len(result["series"]) == 1
    derived = result["series"][0]["derived_points"]
    by_period = {p["period"]: p for p in derived}
    assert set(by_period) == {"2026", "2025"}

    q4_2026, q4_2025 = by_period["2026"], by_period["2025"]
    assert q4_2026["value"] == 22000.0  # 100000.0 - 78000.0, as-reported untouched
    assert q4_2026["duration_weeks"] == 17
    assert q4_2025["value"] == 20000.0  # 88000.0 - 68000.0, as-reported untouched
    assert q4_2025["duration_weeks"] == 16

    expected = (22000.0 / 17) / (20000.0 / 16) - 1
    assert q4_2026["week_normalized_yoy"] == pytest.approx(expected, rel=1e-9)
    # the comparator's OWN point carries no field looking further back (no
    # FY2024 in this fixture) — never guessed.
    assert "week_normalized_yoy" not in q4_2025


def test_quarterly_series_no_week_normalized_yoy_on_equal_week_pair(
    kpi_xbrl_module,
):
    """Task 5 RED: an EQUAL-week comparator pair (both 17wk, from two
    53-week fiscal years) carries NO supplementary field — never guessed
    when normalization would be a no-op."""
    pack = _cost_two_year_week_lane_fact_pack(fy2025_weeks=53)
    result = kpi_xbrl_module.build_quarterly_series(pack)
    derived = result["series"][0]["derived_points"]
    by_period = {p["period"]: p for p in derived}
    q4_2026, q4_2025 = by_period["2026"], by_period["2025"]
    assert q4_2026["duration_weeks"] == q4_2025["duration_weeks"] == 17
    assert "week_normalized_yoy" not in q4_2026
    assert "week_normalized_yoy" not in q4_2025


def _cost_two_year_week_lane_fact_pack_zero_prior_value() -> dict:
    """Same shape as `_cost_two_year_week_lane_fact_pack` (52wk FY2025 vs
    53wk FY2026 -> DIFFERENT-week derived Q4 pair) but FY2025's FY and
    YTD-through-Q3 values are equal, so derived Q4 2025 (the YoY
    comparator for Q4 2026) works out to a zero VALUE — this used to hit
    an uncaught ZeroDivisionError in `_attach_week_normalized_yoy`
    (normalized_prior = 0.0 / 16 = 0.0, then divided into)."""
    facts = [
        {
            "concept": COST_MEMBERSHIP_MATCH["concept"],
            "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
            "consolidation": None,
            "period_end": "2026-08-30",
            "fiscal_year": 2026, "fiscal_quarter": "FY",
            "duration_months": 12, "duration_weeks": 53,
            "week_lane_band": "FY",
            "accession": "acc-fy26", "filed": "2026-10-15",
            "value": 100000.0,
        },
        {
            "concept": COST_MEMBERSHIP_MATCH["concept"],
            "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
            "consolidation": None,
            "period_end": "2026-05-10",
            "fiscal_year": 2026, "fiscal_quarter": "Q3",
            "duration_months": 8, "duration_weeks": 36,
            "week_lane_band": "YTD-through-Q3",
            "accession": "acc-ytd26", "filed": "2026-06-05",
            "value": 78000.0,
        },
        {
            "concept": COST_MEMBERSHIP_MATCH["concept"],
            "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
            "consolidation": None,
            "period_end": "2025-08-31",
            "fiscal_year": 2025, "fiscal_quarter": "FY",
            "duration_months": 12, "duration_weeks": 52,
            "week_lane_band": "FY",
            "accession": "acc-fy25", "filed": "2025-10-15",
            "value": 68000.0,
        },
        {
            "concept": COST_MEMBERSHIP_MATCH["concept"],
            "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
            "consolidation": None,
            "period_end": "2025-05-11",
            "fiscal_year": 2025, "fiscal_quarter": "Q3",
            "duration_months": 8, "duration_weeks": 36,
            "week_lane_band": "YTD-through-Q3",
            "accession": "acc-ytd25", "filed": "2025-06-05",
            "value": 68000.0,
        },
    ]
    fiscal_calendars = {
        "acc-fy26": {"fiscal_period_focus": "FY", "fiscal_year_end": "--08-30"},
        "acc-ytd26": {"fiscal_period_focus": "Q3", "fiscal_year_end": "--08-30"},
        "acc-fy25": {"fiscal_period_focus": "FY", "fiscal_year_end": "--08-31"},
        "acc-ytd25": {"fiscal_period_focus": "Q3", "fiscal_year_end": "--08-31"},
    }
    return {"company": "COST", "facts": facts, "fiscal_calendars": fiscal_calendars}


def test_quarterly_series_no_week_normalized_yoy_on_zero_value_comparator(
    kpi_xbrl_module,
):
    """Task 5 fix-round-2 RED (reviewer finding #1, e64b6595): a
    DIFFERENT-week YoY comparator whose own VALUE is 0.0 used to hit an
    uncaught, contextless ZeroDivisionError inside
    `_attach_week_normalized_yoy` and kill `build_quarterly_series` over
    this OPTIONAL supplementary field. ORCHESTRATOR RULING: a
    zero-denominator comparator is SKIP — no `week_normalized_yoy` field,
    same silent treatment as no-comparator/equal-weeks (mirrors the
    sibling zero-denominator skip in comps_compute.py's
    `_i_rule_of_40`); never raise."""
    pack = _cost_two_year_week_lane_fact_pack_zero_prior_value()
    result = kpi_xbrl_module.build_quarterly_series(pack)
    derived = result["series"][0]["derived_points"]
    by_period = {p["period"]: p for p in derived}
    q4_2026, q4_2025 = by_period["2026"], by_period["2025"]
    assert q4_2025["value"] == 0.0
    assert q4_2026["duration_weeks"] == 17
    assert q4_2025["duration_weeks"] == 16
    assert "week_normalized_yoy" not in q4_2026
    assert "week_normalized_yoy" not in q4_2025


def _cost_single_year_week_lane_fact_pack() -> dict:
    """One fiscal year (FY2026 only) of COST-shaped week-lane facts — no
    prior-fiscal-year comparator present in the signature group at all,
    pinning the `prior is None` branch directly."""
    facts = [
        {
            "concept": COST_MEMBERSHIP_MATCH["concept"],
            "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
            "consolidation": None,
            "period_end": "2026-08-30",
            "fiscal_year": 2026, "fiscal_quarter": "FY",
            "duration_months": 12, "duration_weeks": 53,
            "week_lane_band": "FY",
            "accession": "acc-fy26", "filed": "2026-10-15",
            "value": 100000.0,
        },
        {
            "concept": COST_MEMBERSHIP_MATCH["concept"],
            "dimensions": COST_MEMBERSHIP_MATCH["dimensions"],
            "consolidation": None,
            "period_end": "2026-05-10",
            "fiscal_year": 2026, "fiscal_quarter": "Q3",
            "duration_months": 8, "duration_weeks": 36,
            "week_lane_band": "YTD-through-Q3",
            "accession": "acc-ytd26", "filed": "2026-06-05",
            "value": 78000.0,
        },
    ]
    fiscal_calendars = {
        "acc-fy26": {"fiscal_period_focus": "FY", "fiscal_year_end": "--08-30"},
        "acc-ytd26": {"fiscal_period_focus": "Q3", "fiscal_year_end": "--08-30"},
    }
    return {"company": "COST", "facts": facts, "fiscal_calendars": fiscal_calendars}


def test_quarterly_series_no_week_normalized_yoy_without_comparator(
    kpi_xbrl_module,
):
    """Task 5 fix-round-2 RED (reviewer finding #2b, pin not new bug): a
    point with NO YoY comparator present in its signature group (single
    fiscal year of week-lane facts) gets no supplementary field — the
    `prior is None` branch, pinned directly."""
    pack = _cost_single_year_week_lane_fact_pack()
    result = kpi_xbrl_module.build_quarterly_series(pack)
    derived = result["series"][0]["derived_points"]
    assert len(derived) == 1
    q4_2026 = derived[0]
    assert q4_2026["period"] == "2026"
    assert "week_normalized_yoy" not in q4_2026


# ---------------------------------------------------------------------------
# Task 2 (docs/loom/plans/2026-07-19-jnj-restatement-axis-signature.md) —
# recast annotation: a pack whose `coverage.axis_exclusions` carries a
# vintage-category entry (srt:RestatementAxis, T1's producer-side accounting)
# surfaces as a memo-visible `period_recast` coverage_flag, aggregated
# pack-wide, carrying the affected accession/period_end/concept context.
# Unknown-category exclusions are pack-level accounting only — no flag.
# ---------------------------------------------------------------------------


def _vintage_exclusion(**overrides) -> dict:
    exclusion = {
        "category": "vintage",
        "axis": "srt:RestatementAxis",
        "member": "RevisionOfPriorPeriodReclassificationAdjustmentMember",
        "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "accession": "0000200406-25-000209",
        "period_end": "2025-06-30",
    }
    exclusion.update(overrides)
    return exclusion


def _nested_coverage(*, quarterly_exclusions=None, annual_exclusions=None, annual_arm=None):
    """Mirror pack_us.py's REAL `pack_kpi_quarterly` envelope
    (pack_us.py:1017-1024): `coverage` is NEVER flat — it nests
    `quarterly`/`annual`, each holding its own `extract_dimensional_revenue`
    `coverage` dict (sec_edgar_client.py:3168-3179, `axis_exclusions` key
    included). `annual_arm` overrides the whole annual sub-dict, for the
    error-slot degenerate case (pack_us.py:1023: on annual-arm failure,
    `coverage["annual"]` is the raw `{"error": ...}` slot, not a
    coverage-shaped dict)."""
    return {
        "_status": "ok",
        "quarterly": {"axis_exclusions": quarterly_exclusions or []},
        "annual": (
            annual_arm if annual_arm is not None
            else {"axis_exclusions": annual_exclusions or []}
        ),
    }


def test_quarterly_series_emits_period_recast_flag_for_vintage_exclusion(
    kpi_xbrl_module,
):
    """Task 2 fix-round-2 RED (both reviewers, converged): the REAL
    production pack (pack_us.py's `pack_kpi_quarterly`) nests
    `coverage.quarterly.axis_exclusions` / `coverage.annual.axis_exclusions`
    — never the flat `coverage.axis_exclusions` the original fixtures used.
    A pack carrying one `category: "vintage"` axis exclusion in EITHER arm
    emits ONE `period_recast` coverage_flag, carrying the exclusion's
    accession/period_end/concept context and passing `assert_dqc_schema`.
    A pack with zero exclusions, and a pack with ONLY unknown-category
    exclusions, emit no such flag — unknown-axis exclusions are pack-level
    accounting only, never a recast statement."""
    vintage_pack = {
        "company": "JNJ",
        "facts": [],
        "coverage": _nested_coverage(quarterly_exclusions=[_vintage_exclusion()]),
    }
    result = kpi_xbrl_module.build_quarterly_series(vintage_pack)
    recast_flags = [f for f in result["coverage_flags"] if f["type"] == "period_recast"]
    assert len(recast_flags) == 1
    flag = recast_flags[0]
    kpi_xbrl_module.assert_dqc_schema(flag)
    assert flag["old"] is None
    assert flag["new"] is None
    assert flag["accessions"] == ["0000200406-25-000209"]
    assert "recast" in flag["reason"] and "prior-published" in flag["reason"]
    assert flag["exclusions"] == [_vintage_exclusion()]

    zero_pack = {"company": "JNJ", "facts": [], "coverage": _nested_coverage()}
    result = kpi_xbrl_module.build_quarterly_series(zero_pack)
    assert not any(f["type"] == "period_recast" for f in result["coverage_flags"])

    no_coverage_pack = {"company": "JNJ", "facts": []}
    result = kpi_xbrl_module.build_quarterly_series(no_coverage_pack)
    assert not any(f["type"] == "period_recast" for f in result["coverage_flags"])

    unknown_only_pack = {
        "company": "JNJ",
        "facts": [],
        "coverage": _nested_coverage(quarterly_exclusions=[
            _vintage_exclusion(
                category="unknown", axis="us-gaap:SomeFutureAxis",
                member="SomeMember",
            ),
        ]),
    }
    result = kpi_xbrl_module.build_quarterly_series(unknown_only_pack)
    assert not any(f["type"] == "period_recast" for f in result["coverage_flags"])


def test_quarterly_series_emits_period_recast_flag_for_annual_arm_only_exclusion(
    kpi_xbrl_module,
):
    """Task 2 fix-round-2: a vintage exclusion living ONLY in the ANNUAL arm
    (`coverage.annual.axis_exclusions`) still fires the flag —
    `build_quarterly_series` derives Q4 from the annual arm's FY facts
    (pack_us.py:964-967), so a vintage exclusion there is equally
    memo-relevant even though the quarterly arm is clean."""
    pack = {
        "company": "JNJ",
        "facts": [],
        "coverage": _nested_coverage(annual_exclusions=[_vintage_exclusion()]),
    }
    result = kpi_xbrl_module.build_quarterly_series(pack)
    recast_flags = [f for f in result["coverage_flags"] if f["type"] == "period_recast"]
    assert len(recast_flags) == 1
    assert recast_flags[0]["exclusions"] == [_vintage_exclusion()]


def test_quarterly_series_period_recast_survives_annual_arm_error_slot(
    kpi_xbrl_module,
):
    """Task 2 fix-round-2: on annual-arm failure, `coverage["annual"]` is
    the RAW `{"error": ...}` slot (pack_us.py:1023), not a coverage-shaped
    dict — no `axis_exclusions` key at all. The getter must tolerate this
    degenerate shape (never crash) and still surface a vintage exclusion
    reported by the quarterly arm."""
    pack = {
        "company": "JNJ",
        "facts": [],
        "coverage": _nested_coverage(
            quarterly_exclusions=[_vintage_exclusion()],
            annual_arm={"error": "SEC EDGAR 404: some filing"},
        ),
    }
    result = kpi_xbrl_module.build_quarterly_series(pack)
    recast_flags = [f for f in result["coverage_flags"] if f["type"] == "period_recast"]
    assert len(recast_flags) == 1
    assert recast_flags[0]["exclusions"] == [_vintage_exclusion()]


# ---------------------------------------------------------------------------
# Task 3 (docs/loom/plans/2026-07-19-jnj-restatement-axis-signature.md) —
# per-signature refusal granularity: a genuine intra-filing (single
# accession, two distinct values for the SAME window) ambiguity in ONE
# signature group must not abort the whole quarterly-series build. Before
# the fix, `build_quarterly_series` raises wholesale and nothing emits
# (pinned as the RED baseline below); after the fix, the loop catches the
# ambiguity PER SIGNATURE GROUP, records a non-fatal `signature_refused`
# coverage_flag carrying the verbatim exception reason, and CONTINUES —
# the clean sibling signature still emits its series untouched.
# ---------------------------------------------------------------------------


def _intra_filing_ambiguous_pack() -> dict:
    """Two signature groups sharing one fiscal window: 'Poisoned' carries
    TWO facts from the SAME accession with DIFFERENT values for the SAME
    (period_end, duration_class) — a genuine intra-filing ambiguity, never
    resolved arbitrarily. 'Clean' is an ordinary single-fact sibling
    signature that must still emit."""
    facts = [
        {
            "concept": "us-gaap:PoisonedConcept",
            "dimensions": {},
            "consolidation": None,
            "period_end": "2026-03-31",
            "fiscal_year": 2026, "fiscal_quarter": "Q1",
            "duration_months": 3,
            "accession": "acc-poison", "filed": "2026-05-01",
            "value": 100.0,
        },
        {
            "concept": "us-gaap:PoisonedConcept",
            "dimensions": {},
            "consolidation": None,
            "period_end": "2026-03-31",
            "fiscal_year": 2026, "fiscal_quarter": "Q1",
            "duration_months": 3,
            "accession": "acc-poison", "filed": "2026-05-01",
            "value": 999.0,
        },
        {
            "concept": "us-gaap:CleanConcept",
            "dimensions": {},
            "consolidation": None,
            "period_end": "2026-03-31",
            "fiscal_year": 2026, "fiscal_quarter": "Q1",
            "duration_months": 3,
            "accession": "acc-clean", "filed": "2026-05-01",
            "value": 500.0,
        },
    ]
    fiscal_calendars = {
        "acc-poison": {"fiscal_period_focus": "Q1"},
        "acc-clean": {"fiscal_period_focus": "Q1"},
    }
    return {"company": "JNJ", "facts": facts, "fiscal_calendars": fiscal_calendars}


def test_quarterly_series_refuses_poisoned_signature_sibling_still_emits(
    kpi_xbrl_module,
):
    """Task 3: the per-group `resolve_binding` call is wrapped so a genuine
    intra-filing ambiguity is caught PER SIGNATURE GROUP — the poisoned
    signature yields exactly ONE non-fatal `signature_refused` coverage_flag
    carrying the verbatim exception reason, and the CLEAN sibling signature
    still emits its series untouched. No whole-ticker abort."""
    pack = _intra_filing_ambiguous_pack()
    result = kpi_xbrl_module.build_quarterly_series(pack)

    # sibling emits — exactly one series entry, the clean signature's.
    assert len(result["series"]) == 1
    clean_entry = result["series"][0]
    assert clean_entry["signature"]["concept"] == "us-gaap:CleanConcept"
    assert [p["value"] for p in clean_entry["points"]] == [500.0]

    # exactly one refusal entry, dqc-schema-compliant, verbatim reason.
    refusals = [
        f for f in result["coverage_flags"] if f["type"] == "signature_refused"
    ]
    assert len(refusals) == 1
    flag = refusals[0]
    kpi_xbrl_module.assert_dqc_schema(flag)
    assert flag["accessions"] == ["acc-poison"]
    assert "intra-filing" in flag["reason"]
    assert "PoisonedConcept" in flag["reason"]
    assert flag["signature"]["concept"] == "us-gaap:PoisonedConcept"


# ---------------------------------------------------------------------------
# Task 9 (docs/loom/plans/2026-07-16-operational-kpi-quarterly.md) — structured
# point + DQC-flag schema provenance: every emitted point carries source
# accession(s) + source form (10-K|10-Q) + duration_class; every analysis-layer
# DQC flag follows the ONE schema (type, old, new, accessions, reason),
# asserted via the module's own conformance helper. The source form threads
# from the pack's per-accession `fiscal_calendars` dei read
# (fiscal_period_focus FY -> 10-K, Q1..Q4 -> 10-Q) — the only per-accession
# channel the pack carries; it is never guessed from a fact's own duration.
# No `@req` tags: this dispatch traces work by named plan Tasks, not
# registered loom-spec REQ-ids (same convention as the module header note).
# ---------------------------------------------------------------------------


def test_point_and_dqc_provenance_schema(
    kpi_xbrl_module, aapl_quarterly_pack, dualdur_fixture, q4_fixture,
    stub_data_layer_deps,
):
    """Task 9 RED (spec: 'Every emitted point and DQC flag carries
    structured provenance'):
    (a) an emitted reported point carries source_accession + source_form
        (10-K|10-Q, threaded from the pack's fiscal_calendars dei focus) +
        duration_class — not only a period label and value;
    (b) a derived Q4 point keeps the T8 anti-masquerade PLURAL shape
        (source_accessions, ratified) and gains the aligned plural
        source_forms — the singular keys never appear on the derived lane;
    (c) the restatement flag records old value, new value, and BOTH
        accessions in the ONE DQC schema (policy-C parity; the old
        superseded_accession/kept_accession field names are retired, their
        audit content preserved as accessions=[superseded, kept] + reason);
    (d) EVERY analysis-layer flag class (restatement, label_conflict,
        derived_q4, q4_source_missing, q4_basis_mismatch,
        no_quarterly_coverage) validates against the one schema via the
        module's own assert_dqc_schema helper, which rejects the retired
        old-shape flag;
    (e) T8 spec-reviewer residual: when BOTH Q4-derivation inputs carry
        restatement DQCs from DIFFERENT restating filings, the basis check
        refuses (two distinct restating filings are two vintages, the same
        declared calendar notwithstanding);
    (f) a pack whose fiscal_calendars cannot ground a fact's source form
        fails loud naming the accession — never emitted formless, never
        guessed."""
    # (a) reported 10-Q points: accession + form + duration_class on every one.
    q_points = kpi_xbrl_module.facts_to_points(
        aapl_quarterly_pack, "iphone_revenue", AAPL_IPHONE_QUARTERLY_MATCH,
        "AAPL", "xbrl-dimensional",
    )
    assert len(q_points) == 5
    for p in q_points:
        assert p["source_accession"]
        assert p["source_form"] == "10-Q"  # every carrying filing is a 10-Q
        assert p["duration_class"] in {"3mo", "6mo-YTD", "9mo-YTD"}
    # a 10-K-carried FY fact maps its dei FY focus to form 10-K.
    q4_pack = q4_fixture["aapl_q4_derive"]
    q4_input_points = kpi_xbrl_module.resolve_binding(
        q4_pack, DUALDUR_IPHONE_BINDING, "AAPL"
    )
    fy_point = next(p for p in q4_input_points if p["period_type"] == "FY")
    assert fy_point["source_accession"] == "0000320193-25-000079"
    assert fy_point["source_form"] == "10-K"
    assert fy_point["duration_class"] == "12mo-FY"

    # (b) derived Q4: plural provenance shape, aligned accessions/forms;
    # the singular reported-lane keys never masquerade on the derived lane.
    derived = kpi_xbrl_module.derive_q4_points(
        q4_input_points, fiscal_calendars=q4_pack["fiscal_calendars"]
    )["points"][0]
    assert derived["source_accessions"] == [
        "0000320193-25-000079", "0000320193-25-000073",
    ]
    assert derived["source_forms"] == ["10-K", "10-Q"]  # aligned pairwise
    assert derived["duration_class"] == "3mo"
    assert "source_accession" not in derived
    assert "source_form" not in derived

    # (c) restatement flag: full audit content in the ONE schema.
    dd_points = kpi_xbrl_module.resolve_binding(
        dualdur_fixture["aapl_dualdur"], DUALDUR_IPHONE_BINDING, "AAPL"
    )
    restatement = next(p for p in dd_points if p["period_type"] == "Q1")["dqc"]
    assert restatement["type"] == "restatement"
    assert restatement["old"] == 1000.0
    assert restatement["new"] == 1050.0
    # accessions order is [superseded, kept] — same old-first convention as
    # label_conflict; the retired field names are gone, content preserved.
    assert restatement["accessions"] == [
        "0000320193-25-000008", "0000320193-26-000006",
    ]
    assert restatement["reason"]
    assert "superseded_accession" not in restatement
    assert "kept_accession" not in restatement

    # (d) every analysis-layer flag class conforms to the ONE schema.
    label_conflict = kpi_xbrl_module.resolve_binding(
        dualdur_fixture["fye_change_label_conflict"], FYECHG_SEGMENT_BINDING,
        "FYECHG",
    )[0]["dqc"]
    missing_pack = json.loads(json.dumps(q4_pack))
    missing_pack["facts"] = [
        f for f in missing_pack["facts"] if f.get("duration_months") != 9
    ]
    q4_source_missing = kpi_xbrl_module.derive_q4_points(
        kpi_xbrl_module.resolve_binding(
            missing_pack, DUALDUR_IPHONE_BINDING, "AAPL"
        ),
        fiscal_calendars=missing_pack["fiscal_calendars"],
    )["gaps"][0]
    u_pack = q4_fixture["q4_unit_mismatch"]
    q4_basis_mismatch = kpi_xbrl_module.derive_q4_points(
        kpi_xbrl_module.resolve_binding(u_pack, DUALDUR_IPHONE_BINDING, "AAPL"),
        fiscal_calendars=u_pack["fiscal_calendars"],
    )["gaps"][0]
    no_quarterly_coverage = kpi_xbrl_module.build_series_with_break(
        q_points, "2018", granularity="quarterly",
        facts=aapl_quarterly_pack["facts"] + [ANNUAL_IPHONE_FACT, ANNUAL_MAC_FACT],
    )["coverage_flags"][0]
    assert no_quarterly_coverage["type"] == "no_quarterly_coverage"
    assert no_quarterly_coverage["accessions"] == ["0000320193-25-000079"]
    assert no_quarterly_coverage["dimensions"] == {"ProductOrService": "MacMember"}
    for flag in (
        restatement, label_conflict, derived["dqc"], q4_source_missing,
        q4_basis_mismatch, no_quarterly_coverage,
    ):
        assert kpi_xbrl_module.assert_dqc_schema(flag) is flag
    # the retired old-shape restatement flag no longer conforms.
    with pytest.raises(ValueError, match="accessions"):
        kpi_xbrl_module.assert_dqc_schema({
            "type": "restatement", "old": 1.0, "new": 2.0,
            "superseded_accession": "a", "kept_accession": "b",
        })
    with pytest.raises(ValueError, match="reason"):
        kpi_xbrl_module.assert_dqc_schema({
            "type": "restatement", "old": 1.0, "new": 2.0,
            "accessions": ["a", "b"], "reason": "",
        })

    # (e) BOTH inputs restated, by DIFFERENT restating filings -> refusal,
    # even though the two kept facts' filings declare the SAME calendar.
    # Producer-shaped synthetic pack: the FY total is restated by the
    # FY2026 10-K, the 9mo-YTD by the FY2026 Q3 10-Q — two vintages.
    base = {
        "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "dimensions": {"ProductOrService": "IPhoneMember"},
        "consolidation": None,
        "derivation_basis": "dei-declared",
    }
    both_restated_pack = {
        "company": "AAPL",
        "facts": [
            {**base, "value": 14100.0, "period_end": "2025-09-27",
             "duration_months": 12, "calendar_year": 2025,
             "calendar_quarter": "Q3", "fiscal_year": 2025,
             "fiscal_quarter": "FY",
             "accession": "0000320193-25-000079", "filed": "2025-10-31"},
            {**base, "value": 14200.0, "period_end": "2025-09-27",
             "duration_months": 12, "calendar_year": 2025,
             "calendar_quarter": "Q3", "fiscal_year": 2025,
             "fiscal_quarter": "FY",
             "accession": "0000320193-26-000079", "filed": "2026-10-30"},
            {**base, "value": 11100.0, "period_end": "2025-06-28",
             "duration_months": 9, "calendar_year": 2025,
             "calendar_quarter": "Q2", "fiscal_year": 2025,
             "fiscal_quarter": "Q3",
             "accession": "0000320193-25-000073", "filed": "2025-08-01"},
            {**base, "value": 11200.0, "period_end": "2025-06-28",
             "duration_months": 9, "calendar_year": 2025,
             "calendar_quarter": "Q2", "fiscal_year": 2025,
             "fiscal_quarter": "Q3",
             "accession": "0000320193-26-000073", "filed": "2026-08-01"},
        ],
        "fiscal_calendars": {
            "0000320193-25-000079": {"fiscal_period_focus": "FY",
                                     "fiscal_year_end": "--09-27",
                                     "fiscal_year_focus": "2025"},
            "0000320193-25-000073": {"fiscal_period_focus": "Q3",
                                     "fiscal_year_end": "--09-27",
                                     "fiscal_year_focus": "2025"},
            # the two RESTATING filings declare the SAME calendar — the
            # refusal must come from the vintage check, not check (3).
            "0000320193-26-000079": {"fiscal_period_focus": "FY",
                                     "fiscal_year_end": "--09-26",
                                     "fiscal_year_focus": "2026"},
            "0000320193-26-000073": {"fiscal_period_focus": "Q3",
                                     "fiscal_year_end": "--09-26",
                                     "fiscal_year_focus": "2026"},
        },
    }
    br_points = kpi_xbrl_module.resolve_binding(
        both_restated_pack, DUALDUR_IPHONE_BINDING, "AAPL"
    )
    assert all(p["dqc"]["type"] == "restatement" for p in br_points)
    br_result = kpi_xbrl_module.derive_q4_points(
        br_points, fiscal_calendars=both_restated_pack["fiscal_calendars"]
    )
    assert br_result["points"] == []  # never a cross-vintage subtraction
    assert len(br_result["gaps"]) == 1
    br_gap = br_result["gaps"][0]
    assert br_gap["type"] == "q4_basis_mismatch"
    assert "restat" in br_gap["reason"]

    # (f) a fact whose source form cannot be grounded (no fiscal_calendars
    # entry for its accession) fails loud naming the accession.
    formless_pack = {
        "company": "AAPL",
        "facts": [{**base, "value": 1000.0, "period_end": "2024-12-28",
                   "duration_months": 3, "calendar_year": 2024,
                   "calendar_quarter": "Q4", "fiscal_year": 2025,
                   "fiscal_quarter": "Q1",
                   "accession": "0000320193-25-000008", "filed": "2025-01-31"}],
    }
    with pytest.raises(ValueError, match="0000320193-25-000008"):
        kpi_xbrl_module.facts_to_points(
            formless_pack, "iphone_revenue", AAPL_IPHONE_QUARTERLY_MATCH,
            "AAPL", "xbrl-dimensional",
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


def test_cli_quarterly_series_full_signature_groups(
    kpi_xbrl_module, stub_data_layer_deps, tmp_path, monkeypatch, capsys
):
    """Task 2 RED (docs/loom/plans/2026-07-18-memo-quarterly-kpi-wiring.md):
    the `quarterly-series` subcommand reads a fact-pack JSON from --file and
    builds, PER full-dimensional-signature group present in the pack (the
    kickoff-bound keying: concept + full `dimensions` map + the
    consolidation QUALIFIER — never one axis member, per docs/loom/memory/
    match-kpi-on-full-dimensional-signature-not-one-axis.md), the quarterly
    series via the EXISTING chain (resolve_binding -> derive_q4_points ->
    build_series_with_break(granularity="quarterly", facts=...)), printing
    `{series: [{signature, points, derived_points, gaps}], coverage_flags}`.

    Runs the CLI IN-PROCESS (main() with patched argv) rather than via
    subprocess like test_cli_build_resolves_binding_and_prints_points: the
    coverage-flag path lazily imports sec_edgar_client (module-level
    `import requests`, absent from the offline env), and the sys.modules
    stubs (`stub_data_layer_deps`) can only reach an in-process call.

    Fails now: the subcommand does not exist (argparse exits 2)."""
    pack = json.loads(
        (FIXTURES / "xbrl_q4_derive.json").read_text(encoding="utf-8")
    )["aapl_q4_derive"]
    pack_path = tmp_path / "factpack.json"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")

    monkeypatch.setattr(
        sys, "argv",
        ["kpi_xbrl.py", "quarterly-series", "--file", str(pack_path)],
    )
    rc = kpi_xbrl_module.main()
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert set(out) == {"series", "coverage_flags"}

    # ONE signature group in the pack (AAPL iPhone), keyed by the FULL
    # signature — concept + whole dimensions map + normalized consolidation
    # qualifier (absent -> the default operating-segments view).
    assert len(out["series"]) == 1
    entry = out["series"][0]
    assert set(entry) == {"signature", "points", "derived_points", "gaps"}
    assert entry["signature"] == {
        "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "dimensions": {"ProductOrService": "IPhoneMember"},
        "consolidation": "OperatingSegmentsMember",
    }

    # Reported lane: the three 3mo quarters only — the 9mo-YTD cumulative
    # and the FY total are off-granularity for a quarterly series.
    assert sorted(p["value"] for p in entry["points"]) == [1000.0, 2000.0, 4100.0]
    assert not any(p.get("derived") for p in entry["points"])
    for p in entry["points"]:
        # Parallel calendar/fiscal labels intact on every point.
        assert isinstance(p["calendar_year"], int)
        assert p["calendar_quarter"] in {"Q1", "Q2", "Q3", "Q4"}
        assert p["period"] == "2025"
        assert p["period_type"] in {"Q1", "Q2", "Q3"}
        assert p["source_form"] == "10-Q"
    # The honest divergent pair: fiscal FY2025-Q1 ends in CALENDAR 2024-Q4.
    q1 = next(p for p in entry["points"] if p["period_type"] == "Q1")
    assert q1["calendar_year"] == 2024
    assert q1["calendar_quarter"] == "Q4"

    # Derived lane: Q4 = FY − 9mo-YTD, segregated + tagged with PLURAL
    # provenance (never the singular reported-point keys).
    assert len(entry["derived_points"]) == 1
    q4 = entry["derived_points"][0]
    assert q4["value"] == 3000.0
    assert q4["derived"] is True
    assert q4["source_accessions"] == [
        "0000320193-25-000079", "0000320193-25-000073",
    ]
    assert q4["source_forms"] == ["10-K", "10-Q"]
    assert "source_accession" not in q4
    assert "source_form" not in q4
    assert q4["period"] == "2025"
    assert q4["period_type"] == "Q4"
    assert q4["calendar_year"] == 2025
    assert q4["calendar_quarter"] == "Q3"
    assert q4["dqc"]["type"] == "derived_q4"

    # Clean derivation -> no gaps; the iPhone signature IS quarterly-tagged
    # -> no coverage flags (the negative case; the positive flag case is
    # test_series_flags_dimension_absent_from_quarterlies).
    assert entry["gaps"] == []
    assert out["coverage_flags"] == []

    # Malformed fact-pack JSON -> exit 2 (nothing computed), mirroring the
    # `build` subcommand's exit-code convention.
    bad_path = tmp_path / "bad.json"
    bad_path.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(
        sys, "argv",
        ["kpi_xbrl.py", "quarterly-series", "--file", str(bad_path)],
    )
    assert kpi_xbrl_module.main() == 2
    assert "quarterly-series" in capsys.readouterr().err
