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

No `@req` tags: this dispatch's plan traces work by named plan Tasks, NOT
by registered loom-spec REQ-ids — so `@req` is omitted per the implementer
contract (same convention as the sibling e2e module).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from unittest import mock

import pytest

from conftest import FIXTURES, KPI_XBRL_SCRIPT


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
