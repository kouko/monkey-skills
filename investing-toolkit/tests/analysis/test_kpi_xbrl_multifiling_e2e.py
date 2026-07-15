"""test_kpi_xbrl_multifiling_e2e.py — OFFLINE end-to-end seam probe across
the data -> analysis boundary (Task 5,
docs/loom/plans/2026-07-15-multi-filing-historical-fetch.md).

WHY (loom-memory `cross-module-field-contracts-execute-probes`): per-module
tests stay green while a producer/consumer field-contract mismatch hides at
the seam between `sec_edgar_client.extract_dimensional_revenue`'s fact
shape and `kpi_xbrl.resolve_binding`'s consumer expectations. Only running
REAL captured data across the full chain (fact-builder -> resolve_binding ->
build_series_with_break) exposes that class of bug; this file is that probe,
not a unit test of either module.

Fixture composition (no fabricated values — both fixtures are machine-
captured, see their own `_provenance`/`_comment` fields):

  - tests/data/fixtures/xbrl_multifiling_aapl.json — RAW edgartools fact
    rows (`dim_<axis>` columns, `fact_key`, etc.) captured from 3 real AAPL
    10-Ks (FY2019/FY2021/FY2023 accessions), i.e. the data-LAYER shape
    `extract_dimensional_revenue` consumes internally, BEFORE its two pure
    fact-builder helpers (`_is_dimensional_revenue_fact`,
    `_build_dimensional_revenue_fact` — sec_edgar_client.py:1922,:1939) turn
    each row into the analysis-shaped fact `resolve_binding` expects. This
    file drives the raw rows through those exact two helpers (no network,
    no `edgar` import needed — they are pure dict->dict/bool functions),
    which is precisely the seam the brief calls out: "the concatenated flat
    facts list flows through resolve_binding -> build_series_with_break
    as-is". The 3 filings' ProductOrService=ProductMember rows span fiscal
    years 2017-2023 (comparatives overlap at 2019 and 2021 across adjacent
    filings with IDENTICAL values — this exercises resolve_binding's
    cross-filing DEDUPE branch, not the restatement branch).

  - tests/analysis/fixtures/xbrl_restatement_factpack.json — already
    analysis-shaped (2 real INTC ClientComputingGroup FY2020 facts, same
    signature, DIFFERENT values, DIFFERENT accessions/filed dates) — used
    as-is for the restatement half; this is the existing oracle fixture
    Task 4 (fdc0a3b4/3971e7c8) validated policy C against.

Both fact sets are combined into ONE fact_pack and resolved via a SINGLE
`resolve_binding` call whose binding declares 2 sources (the AAPL
ProductOrService signature and the INTC ClientComputingGroup signature) —
same `concept` string in both real fixtures
(`us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`), different
`dimensions`, so resolve_binding's per-source matching never collides
(no ambiguous-binding raise). This composes the two acceptance halves (a
>3-year multi-filing span, a DQC-flagged restatement point) into the one
chain run the plan's acceptance criteria describes, without hand-typing any
fact value.

No `@req` tags: this dispatch's plan (docs/loom/plans/2026-07-15-
multi-filing-historical-fetch.md) traces work by named plan Tasks, NOT by
registered loom-spec REQ-ids — so `@req` is omitted per the implementer
contract.
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from conftest import FIXTURES, KPI_XBRL_SCRIPT, ROOT, SKILLS

MARKETS_SCRIPTS = SKILLS / "data-markets" / "scripts"
DATA_FIXTURES = ROOT / "tests" / "data" / "fixtures"

_REVENUE_CONCEPT = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"


@pytest.fixture(scope="module")
def kpi_xbrl_module():
    spec = importlib.util.spec_from_file_location("kpi_xbrl_multifiling_e2e", KPI_XBRL_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_xbrl_multifiling_e2e"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def sec_edgar_helpers():
    """Import sec_edgar_client's PURE fact-builder helpers only — no
    `edgar`/network stubbing needed since this file never calls
    `extract_dimensional_revenue` itself, only `_is_dimensional_revenue_fact`
    and `_build_dimensional_revenue_fact` (mirrors
    tests/data/test_sec_edgar_dimensional.py's `_load_helpers` convention)."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    return importlib.import_module("sec_edgar_client")


@pytest.fixture
def aapl_multifiling_raw() -> dict:
    return json.loads((DATA_FIXTURES / "xbrl_multifiling_aapl.json").read_text(encoding="utf-8"))


@pytest.fixture
def restatement_fact_pack() -> dict:
    return json.loads((FIXTURES / "xbrl_restatement_factpack.json").read_text(encoding="utf-8"))


def _aapl_product_facts(sec_edgar_helpers, aapl_multifiling_raw: dict) -> list[dict]:
    """Drive every raw fact row across the 3 real AAPL filings through the
    extractor's own fact-builder pair, keeping only the
    ProductOrService=ProductMember signature (the top-line product-revenue
    breakdown) — mirrors exactly what `extract_dimensional_revenue` does
    internally per filing (sec_edgar_client.py:2112-2122)."""
    built = []
    for filing in aapl_multifiling_raw["filings"]:
        accession = filing["accession"]
        filed = filing["filing_date"]
        for raw in filing["raw_facts"]:
            if not sec_edgar_helpers._is_dimensional_revenue_fact(raw):
                continue
            fact = sec_edgar_helpers._build_dimensional_revenue_fact(raw, "AAPL", accession, filed)
            built.append(fact)
    return [
        f for f in built
        if f["dimensions"] == {"ProductOrService": "ProductMember"} and f["consolidation"] is None
    ]


def test_multifiling_chain_produces_multiyear_series_with_dqc(
    kpi_xbrl_module, sec_edgar_helpers, aapl_multifiling_raw, restatement_fact_pack,
):
    aapl_facts = _aapl_product_facts(sec_edgar_helpers, aapl_multifiling_raw)
    # Sanity on the composed input: real multi-filing overlap across 2019 and
    # 2021 comparatives (2 filings each report those years) — proves this is
    # genuinely multi-filing input, not a single filing's facts.
    assert len(aapl_facts) == 9
    aapl_periods = {f["period_end"][:4] for f in aapl_facts}
    assert aapl_periods == {"2017", "2018", "2019", "2020", "2021", "2022", "2023"}

    restatement_facts = restatement_fact_pack["facts"]
    assert len(restatement_facts) == 2  # the real INTC cross-accession pair

    fact_pack = {
        "company": "MULTI",
        "facts": aapl_facts + restatement_facts,
    }
    binding = {
        "kpi_id": "revenue_multifiling_probe",
        "sources": [
            {
                "concept": _REVENUE_CONCEPT,
                "dimensions": {"ProductOrService": "ProductMember"},
                "source_kind": "xbrl:dimensional",
            },
            {
                "concept": _REVENUE_CONCEPT,
                "dimensions": {"StatementBusinessSegments": "ClientComputingGroupMember"},
                "source_kind": "xbrl:dimensional",
            },
        ],
    }

    points = kpi_xbrl_module.resolve_binding(fact_pack, binding, "MULTI")

    # Cross-filing dedupe: 7 distinct AAPL product years (2019/2021
    # duplicates across adjacent filings collapse to 1 point each, since
    # they AGREE on value) + 1 restated INTC CCG point for 2020.
    periods = [p["period"] for p in points]
    assert len(points) == 8
    assert len(periods) == len(set(periods)) + 1  # one shared period (2020) across the 2 sources

    aapl_years = sorted(int(y) for y in aapl_periods)
    assert max(aapl_years) - min(aapl_years) > 3  # >3-year multi-filing span, per acceptance

    dqc_points = [p for p in points if p.get("dqc")]
    assert len(dqc_points) == 1
    dqc_point = dqc_points[0]
    assert dqc_point["period"] == "2020"
    assert dqc_point["dqc"] == {
        "type": "restatement",
        "old": 40057000000.0,
        "new": 40535000000.0,
        "superseded_accession": "0000050863-22-000007",
        "kept_accession": "0000050863-23-000006",
    }

    # Chain to build_series_with_break (Task 3/4's identity-key + policy C
    # logic is otherwise UNCHANGED downstream, per the plan's Notes) — a
    # break period outside the fixture's real range keeps every point
    # as_reported so this assertion is purely "the seam does not crash and
    # the dqc flag survives the split", not a break-semantics test (that is
    # already covered by T3/T4's own suites).
    series = kpi_xbrl_module.build_series_with_break(points, break_at_period="9999")

    assert series["recast"] == []
    assert len(series["as_reported"]) == 8
    series_years = sorted(int(p["period"]) for p in series["as_reported"] if p["period"] != "2020")
    assert max(series_years) - min(series_years) > 3

    series_dqc = [p for p in series["as_reported"] if p.get("dqc")]
    assert len(series_dqc) == 1
    assert series_dqc[0]["dqc"]["type"] == "restatement"
