"""test_kpi_xbrl_quarterly_e2e.py — OFFLINE end-to-end quarterly seam probe
(Task 11, docs/loom/plans/2026-07-16-operational-kpi-quarterly.md).

WHY (loom-memory `cross-module-field-contracts-execute-probes`, same charter
as test_kpi_xbrl_multifiling_e2e.py): T5-T9's per-function suites stay green
while a producer/consumer field-contract mismatch hides at the seams between
`facts_to_points` (parallel labels + provenance) -> `resolve_binding`
(duration-qualified de-conflation) -> `derive_q4_points` ->
`build_series_with_break` (quarterly granularity + fiscal range). This file
drives ONE assembled fact pack across that whole corrected chain and asserts
the plan's Task 11 acceptance end-to-end; it is a seam probe, not a unit
test of any single stage.

Fixture composition (committed fixtures only — never hand-typed values,
docs/loom/memory/fixtures-mirror-producer-shape.md; each file documents its
own provenance):

  - fixtures/xbrl_quarterly_nvda_factpack.json — PRODUCER-GENERATED (T5):
    the real extractor's verbatim emitted pack over machine-captured NVDA
    FY2026 10-Q rows. Late-January FYE: all three quarterly facts END in
    calendar 2025 but carry fiscal_year 2026 — the fiscal-selected,
    non-December-filer half of the pack.
  - fixtures/xbrl_quarterly_dualdur.json `aapl_dualdur` — PRODUCER-GENERATED
    (T6): real AAPL FY2025/FY2026 filings; supplies the dual-duration
    collision (3mo AND 9mo-YTD at period_end 2025-06-28), a cross-filing
    identical-value dedupe (Q2), and a cross-filing RESTATED quarter (Q1:
    1000.0 -> 1050.0) so a policy-C `restatement` DQC flag rides the chain.
  - fixtures/xbrl_q4_derive.json `aapl_q4_derive` — PRODUCER-SHAPED (T8):
    the same real AAPL FY2025 windows plus the FY 10-K total (14100.0),
    making Q4 derivable as FY − 9mo-YTD = 3000.0.

The three fact lists merge into ONE pack (fiscal_calendars merged by
accession — the shared AAPL accessions carry byte-identical calendars in
both source fixtures) and resolve via a single two-source binding (NVDA
Compute + AAPL iPhone; different concepts, so source matching never
collides). `resolve_binding` drives `facts_to_points` internally — the
chain's first two stages run exactly as production wires them.

Stub note: the quarterly series build passes `facts=` so the
dimension-absence seam (kpi_xbrl's LAZY cross-layer import of
sec_edgar_client) runs too — requests+edgar are stubbed in sys.modules
BEFORE that call per
docs/loom/memory/importing-a-module-runs-its-module-level-imports.md
(mirrors test_kpi_xbrl.py's `stub_data_layer_deps`).

Task 6 addition (docs/loom/plans/2026-07-18-52-53-week-filer-support.md):
two more probes extend this same seam charter onto the week-lane —

  - fixtures/xbrl_quarterly_cost_week_lane_factpack.json — MACHINE-CAPTURED
    (real `pack.py --pack kpi-quarterly` fetch against live SEC EDGAR):
    COST's real FY2024 MembershipMember facts (Q1-Q3 + derived Q4 + an H1
    fact), driving `build_quarterly_series` -> `build_quarterly_memo_feed`
    end-to-end on genuine week-based-filer XBRL.
  - fixtures/xbrl_quarterly_cost_week_lane_yoy_synth.json — the one
    SYNTHETIC fixture in this task (mirrors test_kpi_xbrl.py's already-
    shipped `_cost_two_year_week_lane_fact_pack` factory verbatim): the
    real captured pack's only reachable two-fiscal-year Q4 pair is
    EQUAL-week, so the different-week `week_normalized_yoy` positive case
    is exercised here instead (each fixture's own `_provenance` explains
    why).
  - `test_month_lane_chain_output_pinned_regression` pins a canonical
    fingerprint of the EXISTING month-lane `combined_pack` chain's output
    (Task 6's explicit regression requirement) — proving the week-lane
    additions (T1-T5, same production files) left month-lane classification
    byte-identical.

Task 4 addition (docs/loom/plans/2026-07-19-jnj-restatement-axis-signature.md):

  - fixtures/xbrl_quarterly_jnj_restatement_axis_synth.json — SYNTHETIC
    (models JNJ acc 0000200406-25-000209's Shockwave RestatementAxis
    reclassification pair, post-extraction shape with the nested
    coverage.quarterly/annual `axis_exclusions` envelope): drives the
    period_recast-flag-to-feed chain and the dual-poisoned-group
    `signature_refused` refusal-granularity chain.

No `@req` tags: this dispatch's plan traces work by named plan Tasks, NOT
by registered loom-spec REQ-ids — so `@req` is omitted per the implementer
contract (same convention as the sibling e2e module).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date
from unittest import mock

import pytest

from conftest import FIXTURES, KPI_GATE_SCRIPT, KPI_MEMO_FEED_SCRIPT, KPI_XBRL_SCRIPT


@pytest.fixture(scope="module")
def kpi_xbrl_module():
    spec = importlib.util.spec_from_file_location(
        "kpi_xbrl_quarterly_e2e", KPI_XBRL_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_xbrl_quarterly_e2e"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def kpi_memo_feed_module():
    """Load kpi_memo_feed.py (Task 6: the feed half of the pack->series->feed
    seam). Its same-dir import shim does a plain `import kpi_gate`, which
    must resolve to a real "kpi_gate" module under its own name FIRST
    (mirrors test_kpi_memo_feed.py's `_load_kpi_memo_feed_module` loader) —
    the quarterly arm never touches the store gate itself (module docstring:
    "Fail-closed WITHOUT the store gate"), but the import still runs at
    module-exec time."""
    scripts_dir = str(KPI_GATE_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_gate", None)
    import kpi_gate  # noqa: F401,E402

    spec = importlib.util.spec_from_file_location(
        "kpi_memo_feed_quarterly_e2e", KPI_MEMO_FEED_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_memo_feed_quarterly_e2e"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def stub_data_layer_deps():
    """build_series_with_break's absence-flag path lazily imports
    sec_edgar_client, which does a MODULE-LEVEL `import requests` (and
    lazily imports `edgar`) — neither installed in the offline suite env —
    so both are stubbed in sys.modules first and restored after (docs/loom/
    memory/importing-a-module-runs-its-module-level-imports.md). Only the
    PURE `_dimension_quarterly_absence` helper is exercised — the stubs
    are never touched."""
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


# Two-source binding over the merged pack: concepts differ, so a fact can
# never match both sources (no ambiguous-binding raise) — mirrors
# test_kpi_xbrl.py's NVDA_COMPUTE_MATCH / DUALDUR_IPHONE_BINDING selectors.
QUARTERLY_CHAIN_BINDING = {
    "kpi_id": "quarterly_chain_probe",
    "sources": [
        {
            "concept": "us-gaap:Revenues",
            "dimensions": {"ProductOrService": "ComputeMember"},
            "source_kind": "xbrl-dimensional",
        },
        {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "dimensions": {"ProductOrService": "IPhoneMember"},
            "source_kind": "xbrl-dimensional",
        },
    ],
}


@pytest.fixture
def combined_pack() -> dict:
    nvda = json.loads(
        (FIXTURES / "xbrl_quarterly_nvda_factpack.json").read_text(encoding="utf-8")
    )
    dualdur = json.loads(
        (FIXTURES / "xbrl_quarterly_dualdur.json").read_text(encoding="utf-8")
    )["aapl_dualdur"]
    q4 = json.loads(
        (FIXTURES / "xbrl_q4_derive.json").read_text(encoding="utf-8")
    )["aapl_q4_derive"]
    # The AAPL accessions shared by the two source fixtures carry
    # byte-identical calendars, so merge order is immaterial.
    for accession, calendar in dualdur["fiscal_calendars"].items():
        assert q4["fiscal_calendars"].get(accession, calendar) == calendar
    return {
        "company": "MULTI",
        "facts": nvda["facts"] + dualdur["facts"] + q4["facts"],
        "fiscal_calendars": {
            **nvda["fiscal_calendars"],
            **dualdur["fiscal_calendars"],
            **q4["fiscal_calendars"],
        },
    }


def test_quarterly_chain_deconflates_and_segregates_q4(
    kpi_xbrl_module, combined_pack, stub_data_layer_deps
):
    """Task 11 RED: the assembled chain (fiscal-selected multi-filing
    quarterly facts with a dual-duration collision + a derivable Q4 ->
    parallel labels -> classify -> de-conflate -> derive Q4 -> series)
    yields fiscal-keyed, parallel-labeled, de-conflated points + a
    segregated labeled derived Q4 — with source_form(s) provenance on
    every emitted point and every DQC flag validating against the ONE
    schema."""
    # Sanity on the composed input: genuinely multi-filing (3 NVDA 10-Qs +
    # 6 AAPL filings incl. the FY2026 comparatives-carrying 10-Qs + 10-K).
    assert len(combined_pack["facts"]) == 14
    assert len(combined_pack["fiscal_calendars"]) == 9

    # ---- Stage 1+2: facts_to_points via resolve_binding (production wiring).
    points = kpi_xbrl_module.resolve_binding(
        combined_pack, QUARTERLY_CHAIN_BINDING, "MULTI"
    )
    # 14 facts -> 8 points: 3 NVDA quarters + AAPL {Q1 restated, Q2 deduped,
    # Q3 3mo, Q3 9mo-YTD, FY} (the two fixtures' verbatim-shared AAPL rows
    # dedupe on the duration-qualified identity key).
    assert len(points) == 8

    # Fiscal keying end-to-end: every NVDA fact ENDS in calendar 2025 yet
    # groups under its own fiscal year 2026 — never period_end[:4] — while
    # the parallel calendar labels stay available, honestly named.
    nvda_points = [
        p for p in points
        if p["source_cell_ref"].startswith("us-gaap:Revenues|")
    ]
    assert len(nvda_points) == 3
    assert all(p["period"] == "2026" for p in nvda_points)
    assert all(p["period_end"].startswith("2025-") for p in nvda_points)
    nvda_q3 = next(p for p in nvda_points if p["value"] == 43028000000.0)
    assert nvda_q3["period_type"] == "Q3"
    assert nvda_q3["calendar_year"] == 2025
    assert nvda_q3["calendar_quarter"] == "Q4"

    # Dual-duration de-conflation: the 3mo single quarter and the 9mo YTD
    # at ONE period_end stay DISTINCT points — never conflated, never
    # raised against each other.
    collision = [p for p in points if p["period_end"] == "2025-06-28"]
    assert len(collision) == 2
    by_duration = {p["duration_class"]: p for p in collision}
    assert set(by_duration) == {"3mo", "9mo-YTD"}
    assert by_duration["3mo"]["value"] == 4100.0
    assert by_duration["3mo"]["cumulative"] is False
    assert by_duration["9mo-YTD"]["value"] == 11100.0
    assert by_duration["9mo-YTD"]["cumulative"] is True
    assert all("dqc" not in p for p in collision)

    # The cross-filing restated Q1 resolved per policy C upstream of the
    # series — its restatement DQC flag rides the chain from here on.
    q1 = next(p for p in points if p["period_end"] == "2024-12-28")
    assert q1["value"] == 1050.0
    assert q1["dqc"]["type"] == "restatement"

    # Provenance (T9) present end-to-end on every REPORTED point: singular
    # source_accession + source_form grounded in the filing's dei focus.
    for p in points:
        assert p["source_accession"] in combined_pack["fiscal_calendars"]
        assert p["source_form"] in {"10-K", "10-Q"}
    assert all(p["source_form"] == "10-Q" for p in nvda_points)
    fy_point = next(p for p in points if p["period_type"] == "FY")
    assert fy_point["source_form"] == "10-K"

    # ---- Stage 3: derive_q4_points — segregated, labeled, dual-accession.
    derived = kpi_xbrl_module.derive_q4_points(
        points, fiscal_calendars=combined_pack["fiscal_calendars"]
    )
    # NVDA's FY2026 group has neither an FY total nor a 9mo-YTD in range —
    # no derivation basis at all is NOT a gap; the AAPL pair derives clean.
    assert derived["gaps"] == []
    assert len(derived["points"]) == 1
    q4 = derived["points"][0]
    assert q4["value"] == 3000.0  # 14100.0 FY − 11100.0 9mo-YTD
    assert q4["derived"] is True  # the segregated-lane marker
    # Dual accessions + PLURAL source_forms (never the singular fields).
    assert q4["source_accessions"] == [
        "0000320193-25-000079", "0000320193-25-000073",
    ]
    assert q4["source_forms"] == ["10-K", "10-Q"]
    assert "source_accession" not in q4
    assert "source_form" not in q4
    # The three label groups, grounded in the 10-K's dei calendar:
    assert q4["period_start"] == "2025-06-29"  # raw window
    assert q4["period_end"] == "2025-09-27"
    assert q4["duration_class"] == "3mo"
    assert q4["calendar_year"] == 2025  # calendar label
    assert q4["calendar_quarter"] == "Q3"
    assert q4["period"] == "2025"  # fiscal label
    assert q4["period_type"] == "Q4"
    assert q4["dqc"]["type"] == "derived_q4"
    assert sorted(q4["dqc"]["accessions"]) == [
        "0000320193-25-000073", "0000320193-25-000079",
    ]

    all_points = points + derived["points"]

    # ---- Stage 4: build_series_with_break — quarterly granularity +
    # fiscal range + the dimension-absence seam (facts= -> lazy
    # sec_edgar_client import under the sys.modules stubs).
    fy2025 = kpi_xbrl_module.build_series_with_break(
        all_points, "2018",
        granularity="quarterly",
        fiscal_range=(2025, 2025),
        facts=combined_pack["facts"],
    )
    emitted = fy2025["as_reported"] + fy2025["recast"]
    # Only FY2025 single quarters emit: restated Q1, deduped Q2, Q3, and
    # the derived Q4 flowing through — the 9mo-YTD cumulative and the FY
    # total are off-granularity, NVDA's FY2026 points are out of range.
    assert sorted(p["value"] for p in emitted) == [1050.0, 2000.0, 3000.0, 4100.0]
    assert all(p["period"] == "2025" for p in emitted)
    assert fy2025["granularity"] == "quarterly"
    # The derived Q4 arrives in the FINAL series still segregated+flagged.
    series_q4 = next(p for p in emitted if p.get("derived"))
    assert series_q4["value"] == 3000.0
    assert series_q4["dqc"]["type"] == "derived_q4"
    assert series_q4["source_forms"] == ["10-K", "10-Q"]
    # The restatement flag survives the split too (policy-C audit trail).
    series_q1 = next(p for p in emitted if p["period_type"] == "Q1")
    assert series_q1["dqc"]["type"] == "restatement"
    # Every emitted point carries its form provenance, reported or derived.
    assert all(("source_form" in p) != ("source_forms" in p) for p in emitted)
    # The AAPL iPhone signature IS quarterly-tagged, so the absence seam
    # runs end-to-end and honestly flags NOTHING (the negative case; the
    # positive flag case is T7's own suite).
    assert fy2025["coverage_flags"] == []

    # Fiscal-range keying end-to-end: requesting FY2026 selects exactly the
    # non-December filer's quarters despite their calendar-2025 period_ends.
    fy2026 = kpi_xbrl_module.build_series_with_break(
        all_points, "2018", granularity="quarterly", fiscal_range=(2026, 2026),
    )
    emitted_2026 = fy2026["as_reported"] + fy2026["recast"]
    assert sorted(p["value"] for p in emitted_2026) == sorted(
        p["value"] for p in nvda_points
    )
    assert all(p["period"] == "2026" for p in emitted_2026)
    assert all(p["period_end"].startswith("2025-") for p in emitted_2026)

    # reported_only=True excludes the derived lane wholesale; the reported
    # FY2025 quarters remain.
    reported = kpi_xbrl_module.build_series_with_break(
        all_points, "2018",
        granularity="quarterly",
        fiscal_range=(2025, 2025),
        reported_only=True,
    )
    reported_emitted = reported["as_reported"] + reported["recast"]
    assert sorted(p["value"] for p in reported_emitted) == [1050.0, 2000.0, 4100.0]
    assert not any(p.get("derived") for p in reported_emitted)

    # ---- Every DQC flag in the chain validates via the exported
    # assert_dqc_schema (the ONE schema: type, old, new, accessions,
    # reason) — and the chain genuinely exercised both flag classes.
    flag_types = set()
    for p in all_points + emitted + emitted_2026 + reported_emitted:
        if p.get("dqc"):
            assert kpi_xbrl_module.assert_dqc_schema(p["dqc"]) is p["dqc"]
            flag_types.add(p["dqc"]["type"])
    for gap in derived["gaps"]:
        assert kpi_xbrl_module.assert_dqc_schema(gap) is gap
    for flag in fy2025["coverage_flags"]:
        assert kpi_xbrl_module.assert_dqc_schema(flag) is flag
    assert flag_types == {"restatement", "derived_q4"}


# ---------------------------------------------------------------------------
# Task 6 (docs/loom/plans/2026-07-18-52-53-week-filer-support.md): week-lane
# chain seam probes + the month-lane regression pin.
# ---------------------------------------------------------------------------


def _fingerprint(pts):
    """A stable, sortable snapshot of the facts that matter for the
    month-lane regression pin — period_type/period/duration_class/value/
    derived-flag/dqc-type — deliberately NOT the full point dict (source
    accessions/as_of timestamps are already asserted individually above;
    a fingerprint over EVERY field would be too brittle to be a useful
    pin, catching formatting noise rather than classification/derivation
    regressions)."""
    return sorted(
        (
            p.get("period_type"),
            p.get("period"),
            p.get("duration_class"),
            p.get("value"),
            bool(p.get("derived")),
            p.get("dqc", {}).get("type") if p.get("dqc") else None,
        )
        for p in pts
    )


def test_month_lane_chain_output_pinned_regression(
    kpi_xbrl_module, combined_pack, stub_data_layer_deps
):
    """Task 6 RED->GREEN regression pin: re-runs the SAME month-lane chain
    as `test_quarterly_chain_deconflates_and_segregates_q4` above (same
    `combined_pack` fixture — NVDA + AAPL dualdur + AAPL Q4-derive, all
    month-lane facts, no `duration_weeks`/`week_lane_band` fields at all)
    and asserts a canonical fingerprint of every stage's output.

    WHY this is a DISTINCT assertion from the test above (not a duplicate):
    that test asserts individual fields path-by-path (thorough, but no
    single assertion would catch e.g. a duration_class silently swapped
    between two points, or a stray point appearing/disappearing, since
    each assertion only inspects the fields it names). This test instead
    pins the WHOLE set of (period_type, period, duration_class, value,
    derived, dqc-type) tuples at every stage as ONE canonical snapshot —
    the explicit regression guard Task 6 asks for: proof that landing the
    week-lane classes in `classify_fact_period` (Task 3), the week-lane Q4
    derivation branch (Task 4), and the week-normalized-YoY attachment
    (Task 5) — all landed in the SAME production files
    (sec_edgar_client.py, kpi_xbrl.py) this month-lane chain runs through —
    left month-lane behavior byte-identical. A month-lane fact never
    carries `duration_weeks`/`week_lane_band` (docs/loom/plans/2026-07-18-
    52-53-week-filer-support.md Notes: class-lane precedence tries the
    month map FIRST), so this also proves the week lane is a pure ADDITION,
    never a re-decision of month-lane facts.
    """
    points = kpi_xbrl_module.resolve_binding(
        combined_pack, QUARTERLY_CHAIN_BINDING, "MULTI"
    )
    # None of these real month-lane facts carry the week-lane fields at
    # all — confirms this pin is genuinely exercising the OLD lane, not
    # accidentally routing through the new week-lane branch.
    for fact in combined_pack["facts"]:
        assert "duration_weeks" not in fact
        assert "week_lane_band" not in fact

    derived = kpi_xbrl_module.derive_q4_points(
        points, fiscal_calendars=combined_pack["fiscal_calendars"]
    )
    all_points = points + derived["points"]

    fy2025 = kpi_xbrl_module.build_series_with_break(
        all_points, "2018",
        granularity="quarterly",
        fiscal_range=(2025, 2025),
        facts=combined_pack["facts"],
    )
    emitted = fy2025["as_reported"] + fy2025["recast"]
    fy2026 = kpi_xbrl_module.build_series_with_break(
        all_points, "2018", granularity="quarterly", fiscal_range=(2026, 2026),
    )
    emitted_2026 = fy2026["as_reported"] + fy2026["recast"]
    reported = kpi_xbrl_module.build_series_with_break(
        all_points, "2018",
        granularity="quarterly",
        fiscal_range=(2025, 2025),
        reported_only=True,
    )
    reported_emitted = reported["as_reported"] + reported["recast"]

    assert _fingerprint(all_points) == [
        ("FY", "2025", "12mo-FY", 14100.0, False, None),
        ("Q1", "2025", "3mo", 1050.0, False, "restatement"),
        ("Q1", "2026", "3mo", 34155000000.0, False, None),
        ("Q2", "2025", "3mo", 2000.0, False, None),
        ("Q2", "2026", "3mo", 33844000000.0, False, None),
        ("Q3", "2025", "3mo", 4100.0, False, None),
        ("Q3", "2025", "9mo-YTD", 11100.0, False, None),
        ("Q3", "2026", "3mo", 43028000000.0, False, None),
        ("Q4", "2025", "3mo", 3000.0, True, "derived_q4"),
    ]
    assert _fingerprint(emitted) == [
        ("Q1", "2025", "3mo", 1050.0, False, "restatement"),
        ("Q2", "2025", "3mo", 2000.0, False, None),
        ("Q3", "2025", "3mo", 4100.0, False, None),
        ("Q4", "2025", "3mo", 3000.0, True, "derived_q4"),
    ]
    assert _fingerprint(emitted_2026) == [
        ("Q1", "2026", "3mo", 34155000000.0, False, None),
        ("Q2", "2026", "3mo", 33844000000.0, False, None),
        ("Q3", "2026", "3mo", 43028000000.0, False, None),
    ]
    assert _fingerprint(reported_emitted) == [
        ("Q1", "2025", "3mo", 1050.0, False, "restatement"),
        ("Q2", "2025", "3mo", 2000.0, False, None),
        ("Q3", "2025", "3mo", 4100.0, False, None),
    ]
    assert derived["gaps"] == []
    assert fy2025["coverage_flags"] == []


COST_WEEK_LANE_MATCH = {
    "kpi_id": "cost_membership_fees",
    "sources": [{
        "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "dimensions": {"ProductOrService": "MembershipMember"},
        "source_kind": "xbrl-dimensional",
    }],
}


def test_week_lane_chain_real_cost_pack_to_feed(
    kpi_xbrl_module, kpi_memo_feed_module, stub_data_layer_deps
):
    """Task 6 RED (see module note above the fixture composition for why
    this is a genuine RED against pre-Task-1..5 code): drives the REAL
    machine-captured COST week-lane fact pack (fixtures/
    xbrl_quarterly_cost_week_lane_factpack.json — see its own
    `_provenance`) through `build_quarterly_series` (Gate P/C via
    `classify_fact_period` + week-lane Q4 derivation, production wiring)
    and then `build_quarterly_memo_feed` (the 1.1 feed seam) — asserting
    Gate P's week-boundary label, Gate C's week-lane duration classes, the
    derived Q4's `duration_weeks`, and that the feed carries `duration_weeks`
    through VERBATIM (module docstring: "1.1 verbatim passthrough").

    Why this fails on pre-Task-1..5 code (reasoned, not re-run — the
    dispatch's RED framing): `_DURATION_CLASS_BY_MONTHS` only ever mapped
    {3, 6, 9, 12} -> month classes: the fixture's Q3-YTD fact
    (duration_months=8) and H1 fact (duration_months=5) would have MISSED
    that map and, pre-Task-3, `classify_fact_period` had NO week-lane
    fallback branch at all (`_week_lane_duration_class` did not exist) —
    so `resolve_binding` would raise the `_unclassifiable` ValueError on
    the very first week-lane fact, before `build_quarterly_series` could
    even reach Q4 derivation or the feed. Independently, pre-Task-1 the
    producer never emitted `duration_weeks`/`week_lane_band` on ANY fact at
    all, so even a hypothetical looser consumer would have nothing to key
    off. Both are load-bearing preconditions this test's fixture actually
    carries (every fact below has `duration_weeks` + `week_lane_band` set),
    so the RED is real, not hypothetical.
    """
    pack = json.loads(
        (FIXTURES / "xbrl_quarterly_cost_week_lane_factpack.json").read_text(
            encoding="utf-8"
        )
    )

    # ---- Gate C direct pin: week-lane duration classes on the RAW facts,
    # decoded straight from the producer's own week_lane_band + duration_weeks.
    h1_fact = next(f for f in pack["facts"] if f["duration_months"] == 5)
    assert kpi_xbrl_module.classify_fact_period(h1_fact) == {
        "period_type": "Q2", "cumulative": True, "duration_class": "24wk-YTD",
    }
    q3_ytd_fact = next(
        f for f in pack["facts"]
        if f["fiscal_quarter"] == "Q3" and f["duration_months"] == 8
    )
    assert kpi_xbrl_module.classify_fact_period(q3_ytd_fact) == {
        "period_type": "Q3", "cumulative": True, "duration_class": "36wk-YTD",
    }
    fy_fact = next(f for f in pack["facts"] if f["fiscal_quarter"] == "FY")
    # The month lane KEEPS precedence even though this fact also carries a
    # week-lane-eligible duration_weeks=52 (plan Notes, class-lane
    # precedence) — "12mo-FY", never "52wk-FY".
    assert kpi_xbrl_module.classify_fact_period(fy_fact) == {
        "period_type": "FY", "cumulative": False, "duration_class": "12mo-FY",
    }

    # ---- Gate P direct pin: the Q3 period_end sits EXACTLY 16 weeks
    # before the FILING'S OWN declared fiscal-year-end — the COST-shaped
    # acceptance case from Task 2, on real captured data.
    filing_fye = date.fromisoformat(
        "2024-" + pack["fiscal_calendars"][q3_ytd_fact["accession"]][
            "fiscal_year_end"
        ].lstrip("-")
    )
    q3_period_end = date.fromisoformat(q3_ytd_fact["period_end"])
    assert (filing_fye - q3_period_end).days == 16 * 7

    # ---- Whole chain: pack -> series (production orchestration function).
    result = kpi_xbrl_module.build_quarterly_series(pack)
    assert result["coverage_flags"] == []
    assert len(result["series"]) == 1
    series = result["series"][0]
    assert series["gaps"] == []

    points_by_type = {p["period_type"]: p for p in series["points"]}
    assert set(points_by_type) == {"Q1", "Q2", "Q3"}
    # Reported quarters classify via month-lane precedence ("3mo"), while
    # still carrying the honest week count (duration_weeks propagation,
    # Task 4) regardless of which lane classified them.
    for point in points_by_type.values():
        assert point["duration_class"] == "3mo"
        assert point["duration_weeks"] == 12

    assert len(series["derived_points"]) == 1
    q4 = series["derived_points"][0]
    assert q4["period_type"] == "Q4"
    assert q4["derived"] is True
    assert q4["duration_class"] == "16wk"
    assert q4["duration_weeks"] == 16  # 52wk FY - 36wk YTD
    assert q4["value"] == pytest.approx(4828000000.0 - 3316000000.0)
    assert q4["dqc"]["type"] == "derived_q4"
    assert kpi_xbrl_module.assert_dqc_schema(q4["dqc"]) is q4["dqc"]

    # ---- series -> feed (1.1 verbatim passthrough).
    feed = kpi_memo_feed_module.build_quarterly_memo_feed(
        "COST", result, "2026-07-18T00:00:00"
    )
    assert feed["status"] == "TRUSTED"
    assert feed["_memo_feed_schema_version"] == "1.1"
    feed_series = feed["series"][0]
    feed_q4 = feed_series["derived_points"][0]
    assert feed_q4["duration_weeks"] == 16
    assert feed_q4["duration_class"] == "16wk"
    assert feed_q4["value"] == q4["value"]
    for feed_point in feed_series["points"]:
        assert feed_point["duration_weeks"] == 12


def test_week_lane_yoy_synth_attaches_supplementary_field_through_feed(
    kpi_xbrl_module, kpi_memo_feed_module, stub_data_layer_deps
):
    """Task 6: the different-week `week_normalized_yoy` positive case,
    driven from the one SYNTHETIC fixture in this task (fixtures/
    xbrl_quarterly_cost_week_lane_yoy_synth.json — see its own
    `_provenance` for why real captured data cannot reach this shape
    within the fetch window) — asserting the supplementary field survives
    `build_quarterly_series` -> `build_quarterly_memo_feed` unchanged, the
    as-reported `value` is untouched, and the prior-year comparator (no
    earlier comparator of its own) carries NO supplementary field."""
    pack = json.loads(
        (FIXTURES / "xbrl_quarterly_cost_week_lane_yoy_synth.json").read_text(
            encoding="utf-8"
        )
    )

    result = kpi_xbrl_module.build_quarterly_series(pack)
    derived = result["series"][0]["derived_points"]
    by_period = {p["period"]: p for p in derived}
    assert set(by_period) == {"2026", "2025"}

    q4_2026, q4_2025 = by_period["2026"], by_period["2025"]
    assert q4_2026["duration_weeks"] == 17
    assert q4_2025["duration_weeks"] == 16
    assert q4_2026["value"] == 22000.0  # 100000.0 FY - 78000.0 36wk-YTD, as-reported
    assert q4_2025["value"] == 20000.0  # 88000.0 FY - 68000.0 36wk-YTD, as-reported

    expected_yoy = (22000.0 / 17) / (20000.0 / 16) - 1
    assert q4_2026["week_normalized_yoy"] == pytest.approx(expected_yoy, rel=1e-9)
    assert "week_normalized_yoy" not in q4_2025

    feed = kpi_memo_feed_module.build_quarterly_memo_feed(
        "COST", result, "2026-07-18T00:00:00"
    )
    assert feed["status"] == "TRUSTED"
    feed_by_period = {p["period"]: p for p in feed["series"][0]["derived_points"]}
    assert feed_by_period["2026"]["week_normalized_yoy"] == pytest.approx(
        expected_yoy, rel=1e-9
    )
    assert feed_by_period["2026"]["value"] == 22000.0
    assert "week_normalized_yoy" not in feed_by_period["2025"]


# ---------------------------------------------------------------------------
# Task 4 (docs/loom/plans/2026-07-19-jnj-restatement-axis-signature.md): JNJ-
# shaped e2e seam coverage for T1-T3's shipped contract — a vintage-axis
# exclusion's `period_recast` coverage_flag reaching the feed (T2), and a
# genuine intra-filing ambiguity's per-signature `signature_refused`
# granularity (T3), both driven pack -> build_quarterly_series -> feed.
# Fixture: fixtures/xbrl_quarterly_jnj_restatement_axis_synth.json (see its
# own `_provenance` — extraction is NOT re-run here, so both packs model the
# extractor's OUTPUT shape directly, per this module's docstring).
#
# Reasoned pre-arc RED (not re-run — mirrors the COST week-lane test's own
# framing above): variant (a)'s `period_recast` assertion fails on pre-Task-2
# code because `build_quarterly_series` never read `fact_pack["coverage"]`
# at all — the assembled `coverage_flags` list would simply lack a
# `period_recast` entry, `recast_flags` would be empty, the flag-count
# assertion fails. Variant (b) fails harder: pre-Task-3 code raised the bare
# ambiguous-binding `ValueError` (no `_IntraFilingAmbiguityError` narrow
# subclass, no per-group try/except in `build_quarterly_series`'s loop) on
# the FIRST poisoned group in stable signature order — the whole
# `build_quarterly_series` call aborts, nothing emits, and `resolve_binding`
# is never reached for the clean sibling or the second poisoned group;
# `build_quarterly_memo_feed` is never even called.
# ---------------------------------------------------------------------------


@pytest.fixture
def jnj_restatement_axis_packs() -> dict:
    return json.loads(
        (FIXTURES / "xbrl_quarterly_jnj_restatement_axis_synth.json").read_text(
            encoding="utf-8"
        )
    )


def test_jnj_restatement_pair_excluded_pack_layer_recast_flag_reaches_feed(
    kpi_xbrl_module, kpi_memo_feed_module, jnj_restatement_axis_packs,
    stub_data_layer_deps,
):
    """Task 4 chain variant (a): the JNJ Shockwave RestatementAxis pair is
    already excluded at the pack layer (`coverage.quarterly.axis_exclusions`
    carries both vintage-tagged members — T1's producer-side accounting,
    counted by category); the axis-absent REAL Q1+Q2 facts bind cleanly
    through `resolve_binding` with no false ambiguity (a single fact per
    window — nothing collides); and T2's `period_recast` coverage_flag,
    built from that exclusion accounting, reaches the memo feed with the
    verbatim exclusion payload."""
    pack = jnj_restatement_axis_packs["jnj_clean_bind"]

    result = kpi_xbrl_module.build_quarterly_series(pack)

    # ---- The real fact binds cleanly: exactly one signature group, both
    # real quarters emitted, no ambiguity raised anywhere in the chain.
    assert len(result["series"]) == 1
    entry = result["series"][0]
    assert entry["signature"]["dimensions"] == {
        "ProductOrService": "ShockwaveMedTechMember"
    }
    assert sorted(p["value"] for p in entry["points"]) == [700.0, 720.0]
    assert entry["gaps"] == []

    # ---- The pack-layer exclusion surfaces as ONE period_recast flag,
    # carrying the verbatim two-member exclusion payload from the fixture.
    recast_flags = [
        f for f in result["coverage_flags"] if f["type"] == "period_recast"
    ]
    assert len(recast_flags) == 1
    flag = recast_flags[0]
    kpi_xbrl_module.assert_dqc_schema(flag)
    assert flag["accessions"] == ["0000200406-25-000209"]
    assert flag["exclusions"] == (
        pack["coverage"]["quarterly"]["axis_exclusions"]
    )
    assert {e["member"] for e in flag["exclusions"]} == {
        "PreviouslyReportedMember",
        "RevisionOfPriorPeriodReclassificationAdjustmentMember",
    }

    # ---- series -> feed: the recast flag rides through VERBATIM alongside
    # the real series.
    feed = kpi_memo_feed_module.build_quarterly_memo_feed(
        "JNJ", result, "2026-07-19T00:00:00"
    )
    assert feed["status"] == "TRUSTED"
    feed_recast = [
        f for f in feed["coverage_flags"] if f["type"] == "period_recast"
    ]
    assert feed_recast == recast_flags
    assert sorted(
        p["value"] for p in feed["series"][0]["points"]
    ) == [700.0, 720.0]


def test_jnj_genuine_intra_filing_ambiguity_refuses_per_signature_sibling_emits(
    kpi_xbrl_module, kpi_memo_feed_module, jnj_restatement_axis_packs,
    stub_data_layer_deps,
):
    """Task 4 chain variant (b): a genuine intra-filing ambiguity — TWO
    signature groups each carrying two DIFFERENT-valued facts from the SAME
    accession/window (a real tagging defect, distinct from the vintage-
    restatement scenario above) — refuses per signature (T3) while the
    clean sibling signature still emits, and the feed carries the sibling's
    series plus TWO `signature_refused` flags (multiple-poisoned-groups
    behavior, cheap to assert alongside the single-group case already
    pinned in test_kpi_xbrl.py)."""
    pack = jnj_restatement_axis_packs["jnj_ambiguous_refusal"]

    result = kpi_xbrl_module.build_quarterly_series(pack)

    # ---- Only the clean sibling signature emits — both poisoned groups are
    # skipped, no whole-ticker abort.
    assert len(result["series"]) == 1
    clean_entry = result["series"][0]
    assert clean_entry["signature"]["dimensions"] == {
        "ProductOrService": "ConsumerHealthMember"
    }
    assert [p["value"] for p in clean_entry["points"]] == [500.0]

    # ---- Two poisoned groups -> two refusal entries, each dqc-schema-
    # compliant, each naming its own offending signature.
    refusals = [
        f for f in result["coverage_flags"] if f["type"] == "signature_refused"
    ]
    assert len(refusals) == 2
    refused_dimensions = {
        tuple(sorted(f["signature"]["dimensions"].items())) for f in refusals
    }
    assert refused_dimensions == {
        (("ProductOrService", "ShockwaveMedTechMember"),),
        (("ProductOrService", "DePuySynthesMember"),),
    }
    for flag in refusals:
        kpi_xbrl_module.assert_dqc_schema(flag)
        assert flag["accessions"] == ["0000200406-25-000301"]
        assert "intra-filing" in flag["reason"]

    # ---- series -> feed: the sibling's series plus both refusal flags,
    # verbatim.
    feed = kpi_memo_feed_module.build_quarterly_memo_feed(
        "JNJ", result, "2026-07-19T00:00:00"
    )
    assert feed["status"] == "TRUSTED"
    assert len(feed["series"]) == 1
    assert feed["series"][0]["points"][0]["value"] == 500.0
    feed_refusals = [
        f for f in feed["coverage_flags"] if f["type"] == "signature_refused"
    ]
    assert feed_refusals == refusals
