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


def test_facts_to_points_period_derives_from_period_end_not_fiscal_year(kpi_xbrl_module, fact_pack):
    """period MUST come from period_end[:4] — edgartools' raw fiscal_year
    column is unreliable for prior-year comparatives (AMENDMENT a). Corrupt
    fiscal_year while leaving period_end correct -> period still follows
    period_end, proving the derivation source, not just the output value.
    """
    mutated = json.loads(json.dumps(fact_pack))
    for fact in mutated["facts"]:
        if fact["concept"] == NEW_IPHONE_MATCH["concept"] and fact.get("member") == "aapl:IPhoneMember" and fact["period_end"] == "2025-09-27":
            fact["fiscal_year"] = 1999  # deliberately wrong; period_end is the source of truth

    points = kpi_xbrl_module.facts_to_points(
        mutated, "iphone_revenue", NEW_IPHONE_MATCH, "AAPL", "xbrl-dimensional"
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
        "fiscal_year": 2025,
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
        "fiscal_year": 2025,
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
