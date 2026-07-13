"""Tests for analysis-xval/scripts/xval_compute.py (Layer 2 pure compute).

Task 3 (plan: docs/loom/plans/2026-07-13-us-sec-financial-table-xval.md) ships
ONLY the CLI + report-envelope skeleton: `--source-a` (doc-table cells pack)
and `--source-b` (companyfacts pack) resolve to an empty-comparisons report
scaffold. Matching/classification logic lands in later tasks.

Task 4 adds `build_source_b_index` — the Source-B fact index reconstructed
ONLY from a companyfacts pack (independence invariant). Its internal
matching/index-building functions aren't wired into the CLI report yet
(Task 5+), so this module is loaded directly via importlib (same convention
as tests/analysis/test_comps_sector_routing.py's `sector_classifier` fixture)
rather than invoked as a subprocess.
"""
from __future__ import annotations

import importlib.util
import json
import sys

from conftest import XVAL_SCRIPT

import pytest


@pytest.fixture(scope="module")
def xval_module():
    """Load xval_compute.py as an importable module for pure-function unit
    tests of index-building logic not yet surfaced in the CLI's JSON output.
    """
    spec = importlib.util.spec_from_file_location("xval_compute_test", XVAL_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["xval_compute_test"] = module
    spec.loader.exec_module(module)
    return module


def test_cli_emits_report_scaffold(runner, tmp_path):
    source_a = tmp_path / "source_a.json"
    source_b = tmp_path / "source_b.json"
    source_a.write_text("{}", encoding="utf-8")
    source_b.write_text("{}", encoding="utf-8")

    res = runner(XVAL_SCRIPT, "--source-a", str(source_a), "--source-b", str(source_b))

    assert res.returncode == 0, res.stderr
    payload = json.loads(res.stdout)
    assert payload["comparisons"] == []
    assert "high_alerts" in payload
    assert "single_source" in payload
    assert "_provenance" in payload


def test_bad_args_exit_2(runner, tmp_path):
    source_a = tmp_path / "source_a.json"
    source_a.write_text("{}", encoding="utf-8")

    # Missing required --source-b arg.
    res_missing = runner(XVAL_SCRIPT, "--source-a", str(source_a))
    assert res_missing.returncode == 2

    # Unreadable (nonexistent) --source-b path.
    res_unreadable = runner(
        XVAL_SCRIPT,
        "--source-a", str(source_a),
        "--source-b", str(tmp_path / "does_not_exist.json"),
    )
    assert res_unreadable.returncode == 2


def test_source_b_index_from_companyfacts(xval_module, fixtures_dir):
    """Given ONLY a Source-B (companyfacts) fixture — no Source-A input at
    all — the built index exposes each concept's value keyed by
    (concept, period) with dimension=None, sourced purely from the
    companyfacts rows (independence invariant, plan Notes
    §Anti-fabrication invariant).
    """
    with (fixtures_dir / "xval_source_b_aapl.json").open(encoding="utf-8") as f:
        source_b_pack = json.load(f)

    index = xval_module.build_source_b_index(source_b_pack)

    # Instant fact (no `start` on the companyfacts row) -> period.type == "instant".
    instant_key = (
        "us-gaap:AccountsReceivableNetCurrent",
        ("instant", "2025-09-27"),
    )
    assert instant_key in index
    fact = index[instant_key]
    assert fact["concept"] == "us-gaap:AccountsReceivableNetCurrent"
    assert fact["period"] == {"type": "instant", "instant": "2025-09-27"}
    assert fact["dimension"] is None
    assert fact["value"] == 39777000000
    assert fact["accn"] == "0000320193-25-000079"

    # Duration fact (has both `start` and `end`) -> period.type == "duration".
    duration_key = (
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        ("duration", "2024-09-29", "2025-09-27"),
    )
    assert duration_key in index
    dur_fact = index[duration_key]
    assert dur_fact["period"] == {
        "type": "duration",
        "start": "2024-09-29",
        "end": "2025-09-27",
    }
    assert dur_fact["dimension"] is None
    assert dur_fact["value"] == 416161000000
    assert dur_fact["accn"] == "0000320193-25-000079"


def test_source_b_index_rejects_source_a_pack(xval_module):
    """Independence guard: handing build_source_b_index a Source-A
    doc-table-cells pack (identified by its top-level `cells` key) raises
    loudly rather than silently building an index from the wrong source.
    Uses an explicit raise (not a bare `assert`, which `python -O` strips),
    matching comps_compute.py::_load_memo_fetch_pack's wrong-pack convention.
    """
    source_a_pack = {"cells": [{"concept": "us-gaap:Assets"}]}
    with pytest.raises(ValueError, match="Source-B companyfacts pack"):
        xval_module.build_source_b_index(source_a_pack)


def test_match_non_dimensional_by_concept_period(xval_module):
    """A non-dimensional Source-A doc cell pairs with the Source-B fact
    sharing (concept, period), dimension=None both sides — matched on the
    (concept, period) key alone, never by row-label text or table position
    (anti-fabrication invariant, plan Notes).

    Two decoys prove the label/row is never consulted:
    1. Two doc cells share the SAME (concept, period) but carry DIFFERENT
       citation labels ("Total net sales" vs "Net sales (decoy label)") —
       both must resolve to the identical Source-B fact, since changing
       only the label must never change the match.
    2. The Source-B index also holds a same-concept fact for a DIFFERENT
       period with a wildly different value — a label- or
       first-same-concept-hit matcher could wrongly grab it; concept+period
       matching must not.
    """
    correct_period = {"type": "duration", "start": "2023-10-01", "end": "2024-09-28"}

    def _doc_cell(label: str) -> dict:
        return {
            "concept": "us-gaap:Revenues",
            "period": correct_period,
            "dimension": None,
            "value_displayed": "391035000000",
            "numeric_value": 391035000000.0,
            "decimals": "-6",
            "citation": {
                "accession": "0000320193-24-000123",
                "statement_name": "IncomeStatement",
                "row": 5,
                "col": "duration_2023-10-01_2024-09-28",
                "label": label,
                "context_ref": "c-1",
                "fact_id": "f-1",
            },
        }

    source_b_pack = {
        "cik": 320193,
        "facts": {
            "us-gaap": {
                "Revenues": [
                    # Decoy listed FIRST (insertion order = index iteration
                    # order): same concept, DIFFERENT period, wildly different
                    # value. A first-same-concept-hit matcher (ignoring period)
                    # would grab THIS entry and the value assertion below would
                    # fail — so this ordering makes the period-load-bearing
                    # property genuinely testable, not vacuously satisfied.
                    {
                        "start": "2022-09-25",
                        "end": "2023-09-30",
                        "value": 1,
                        "accn": "0000320193-23-000106",
                        "form": "10-K",
                        "fy": 2023,
                        "fp": "FY",
                        "filed": "2023-11-03",
                    },
                    {
                        "start": "2023-10-01",
                        "end": "2024-09-28",
                        "value": 391035000000,
                        "accn": "0000320193-24-000123",
                        "form": "10-K",
                        "fy": 2024,
                        "fp": "FY",
                        "filed": "2024-11-01",
                    },
                ]
            }
        },
    }

    index = xval_module.build_source_b_index(source_b_pack)

    for label in ("Total net sales", "Net sales (decoy label)"):
        match = xval_module.match_cell(_doc_cell(label), index)
        assert match is not None
        assert match["concept"] == "us-gaap:Revenues"
        assert match["period"] == correct_period
        assert match["dimension"] is None
        assert match["value"] == 391035000000
        assert match["accn"] == "0000320193-24-000123"


def test_dimensional_match_requires_member_agreement(xval_module):
    """A dimensional doc cell (concept+period+dimension triple, plan Notes
    §Anti-fabrication invariant) is accepted ONLY when the candidate's
    dimension is the identical {axis, member} dict — never on axis+concept+
    period alone, and never against a consolidated (dimension=None) fact.

    Case 1 (accept) hand-constructs a Source-B index entry directly, rather
    than going through `build_source_b_index` on a companyfacts fixture:
    companyfacts is consolidated-only (`build_source_b_index` always sets
    `dimension=None`; see its docstring), so it can never itself produce a
    dimensional candidate. This is a unit test of the `match_cell` predicate
    in isolation, not a companyfacts-pack fixture — it does not violate
    fixtures-mirror-producer-shape (plan Notes §Fixture discipline).

    Case 3 IS the real production shape: `build_source_b_index` output
    (dimension=None) is what a dimensional doc cell actually meets in
    practice; per the brief's HYBRID note this is expected to miss here and
    route to single-source (Task 7), with member agreement re-checked
    single-source on the iXBRL side — NOT in this matcher.
    """
    concept = "us-gaap:Revenues"
    period = {"type": "duration", "start": "2023-10-01", "end": "2024-09-28"}
    axis = "srt:ProductOrServiceAxis"

    def _dimensional_doc_cell(member: str) -> dict:
        return {
            "concept": concept,
            "period": period,
            "dimension": {"axis": axis, "member": member},
            "value_displayed": "200000000000",
            "numeric_value": 200000000000.0,
            "decimals": "-6",
            "citation": {
                "accession": "0000320193-24-000123",
                "statement_name": "SegmentReporting",
                "row": 12,
                "col": "duration_2023-10-01_2024-09-28",
                "label": "iPhone",
                "context_ref": "c-2",
                "fact_id": "f-2",
            },
        }

    def _index_with_candidate_dimension(candidate_dimension) -> dict:
        return {
            (concept, xval_module._period_key(period)): {
                "concept": concept,
                "period": period,
                "dimension": candidate_dimension,
                "value": 200000000000,
                "accn": "0000320193-24-000123",
            }
        }

    doc_cell = _dimensional_doc_cell("aapl:IPhoneMember")

    # 1. Accept on equal member (hand-constructed candidate — see docstring).
    same_member_index = _index_with_candidate_dimension(
        {"axis": axis, "member": "aapl:IPhoneMember"}
    )
    match = xval_module.match_cell(doc_cell, same_member_index)
    assert match is not None
    assert match["dimension"] == {"axis": axis, "member": "aapl:IPhoneMember"}
    assert match["value"] == 200000000000

    # 2. Reject on a different member (same concept+period, wrong segment).
    diff_member_index = _index_with_candidate_dimension(
        {"axis": axis, "member": "aapl:MacMember"}
    )
    assert xval_module.match_cell(doc_cell, diff_member_index) is None

    # 3. Reject on no member — the real companyfacts case: consolidated-only
    # facts carry dimension=None (build_source_b_index's actual output
    # shape), which must NOT satisfy a dimensional doc cell.
    no_dimension_index = _index_with_candidate_dimension(None)
    assert xval_module.match_cell(doc_cell, no_dimension_index) is None

    # Regression: the Task-5 non-dimensional case still matches unchanged.
    non_dim_doc_cell = dict(doc_cell, dimension=None)
    non_dim_index = _index_with_candidate_dimension(None)
    non_dim_match = xval_module.match_cell(non_dim_doc_cell, non_dim_index)
    assert non_dim_match is not None
    assert non_dim_match["dimension"] is None


def test_non_gaap_not_force_matched(xval_module):
    """Task 11: an adjusted/non-GAAP doc-table row ("Adjusted EBITDA",
    carrying a company-extension concept with no us-gaap counterpart) MUST
    be recorded doc-only/single-source, and MUST NOT be paired with a
    similarly-labeled but conceptually different GAAP fact
    (`us-gaap:OperatingIncomeLoss`) for the SAME period, on label-similarity
    grounds (plan Notes §Anti-fabrication invariant; brief Requirement: Do
    not force-match adjusted or non-GAAP figures to a GAAP tag).

    The temptation fixture: the Source-B index DOES contain
    `us-gaap:OperatingIncomeLoss` for the exact same period as the
    "Adjusted EBITDA" doc cell — a label-based matcher ("Adjusted EBITDA"
    ~ "Operating Income") would be tempted to grab it. `match_cell` keys
    strictly on `(concept, period)` (xval_compute.py:176-183) and never
    reads `doc_cell["citation"]["label"]`, so the company-extension concept
    `aapl:AdjustedEBITDA` simply has no key in the index -> None -> routed
    to single_source by `route_cells`, never paired with the GAAP fact.
    """
    period = {"type": "duration", "start": "2023-10-01", "end": "2024-09-28"}

    non_gaap_cell = {
        "concept": "aapl:AdjustedEBITDA",
        "period": period,
        "dimension": None,
        "value_displayed": "150000000000",
        "numeric_value": 150000000000.0,
        "decimals": "-6",
        "citation": {
            "accession": "0000320193-24-000123",
            "statement_name": "IncomeStatement",
            "row": 9,
            "col": "duration_2023-10-01_2024-09-28",
            "label": "Adjusted EBITDA",
            "context_ref": "c-9",
            "fact_id": "f-9",
        },
    }

    # Tempting decoy: the SAME period's us-gaap:OperatingIncomeLoss fact IS
    # present in Source B, so a label-similarity matcher ("Adjusted EBITDA"
    # ~ "Operating Income") could wrongly grab it.
    source_b_pack = {
        "cik": 320193,
        "facts": {
            "us-gaap": {
                "OperatingIncomeLoss": [
                    {
                        "start": "2023-10-01",
                        "end": "2024-09-28",
                        "value": 123216000000,
                        "accn": "0000320193-24-000123",
                        "form": "10-K",
                        "fy": 2024,
                        "fp": "FY",
                        "filed": "2024-11-01",
                    }
                ]
            }
        },
    }
    index = xval_module.build_source_b_index(source_b_pack)

    # Unit-level check: match_cell itself must reject the label-tempting
    # OperatingIncomeLoss candidate for the non-GAAP concept.
    assert xval_module.match_cell(non_gaap_cell, index) is None

    # Routing-level check: the non-GAAP cell lands in single_source (doc-only),
    # never in matched — and specifically never paired with OperatingIncomeLoss.
    source_a_pack = {"cells": [non_gaap_cell]}
    result = xval_module.route_cells(source_a_pack, index)

    assert result["matched"] == []
    assert len(result["single_source"]) == 1
    assert result["single_source"][0] is non_gaap_cell
    assert result["single_source"][0]["concept"] == "aapl:AdjustedEBITDA"


def _classify_fixture_pair(doc_value: float, xbrl_value: int) -> tuple[dict, dict]:
    """A minimal matched (doc_cell, xbrl_fact) pair — the `route_cells`
    matched-tuple shape — carrying only what Task 8's classifier reads
    (concept/period/dimension identity + the two values to diff).
    """
    period = {"type": "duration", "start": "2023-10-01", "end": "2024-09-28"}
    doc_cell = {
        "concept": "us-gaap:Revenues",
        "period": period,
        "dimension": None,
        "value_displayed": str(doc_value),
        "numeric_value": doc_value,
        "decimals": "-6",
        "citation": {
            "accession": "0000320193-24-000123",
            "statement_name": "IncomeStatement",
            "row": 5,
            "col": "duration_2023-10-01_2024-09-28",
            "label": "Total net sales",
            "context_ref": "c-1",
            "fact_id": "f-1",
        },
    }
    xbrl_fact = {
        "concept": "us-gaap:Revenues",
        "period": period,
        "dimension": None,
        "value": xbrl_value,
        "accn": "0000320193-24-000123",
    }
    return doc_cell, xbrl_fact


@pytest.mark.parametrize(
    "doc_value, xbrl_value, expected_pct, expected_alert",
    [
        pytest.param(100_400_000.0, 100_000_000, 0.4, "low", id="low"),
        pytest.param(108_000_000.0, 100_000_000, 8.0, "high", id="high"),
        # Negative divergence (doc 8% BELOW xbrl): classification is by
        # MAGNITUDE, not sign — a -8% gap is still `high`, never slipped
        # through as `low`. Encodes the load-bearing abs() in the classifier:
        # drop it and `-8.0 <= 1` would wrongly band this `low`, silently
        # hiding a high-alert under-statement. pct_diff keeps its sign.
        pytest.param(92_000_000.0, 100_000_000, -8.0, "high", id="negative_high"),
    ],
)
def test_classify_bands(xval_module, doc_value, xbrl_value, expected_pct, expected_alert):
    """Task 8: classify a matched pair's divergence with xval's OWN 1%/5%
    bands (`XVAL_BAND_LOW`/`XVAL_BAND_HIGH` — NOT comps' 5%/15% bands).
    Classification is sign-agnostic (by magnitude); the signed pct_diff is
    retained. Both values are always retained on the entry (plan Notes §Band
    constants; §Anti-fabrication invariant).
    """
    doc_cell, xbrl_fact = _classify_fixture_pair(doc_value, xbrl_value)

    entry = xval_module.classify_divergence(doc_cell, xbrl_fact)

    assert entry["pct_diff"] == pytest.approx(expected_pct)
    assert entry["alert"] == expected_alert
    # Both values always retained on the entry.
    assert entry["doc_value"] == doc_value
    assert entry["xbrl_value"] == xbrl_value
    assert entry["concept"] == "us-gaap:Revenues"


def test_undefined_divergence_is_na_not_dropped(xval_module):
    """Task 9: an undefined divergence — xbrl_value == 0 (pct_diff
    undefined), or either side None — is classified `alert == "n/a"` with
    an explanatory `note`, and the entry is STILL PRESENT in
    `classify_divergence`'s return value — never silently dropped (plan
    Notes §Anti-fabrication invariant; spec :85-90 "Undefined divergence
    is classified n/a, not dropped"). Both values are always retained on
    the entry, even when one side is None, mirroring comps'
    n/a-never-drop discipline (comps_compute.py `_compute_divergence`
    :968-979).
    """
    # Case 1: xbrl_value == 0 -> pct_diff undefined.
    doc_cell, xbrl_fact = _classify_fixture_pair(100_000_000.0, 0)
    entry = xval_module.classify_divergence(doc_cell, xbrl_fact)
    assert entry is not None
    assert entry["alert"] == "n/a"
    assert entry["note"]
    assert entry["pct_diff"] is None
    assert entry["doc_value"] == 100_000_000.0
    assert entry["xbrl_value"] == 0

    # Case 2: xbrl side None (e.g. companyfacts fact carries no value).
    doc_cell2, xbrl_fact2 = _classify_fixture_pair(100_000_000.0, 100_000_000)
    xbrl_fact2["value"] = None
    entry2 = xval_module.classify_divergence(doc_cell2, xbrl_fact2)
    assert entry2 is not None
    assert entry2["alert"] == "n/a"
    assert entry2["note"]
    assert entry2["pct_diff"] is None
    assert entry2["doc_value"] == 100_000_000.0
    assert entry2["xbrl_value"] is None

    # Case 3: doc side None (e.g. doc cell's numeric_value is missing).
    doc_cell3, xbrl_fact3 = _classify_fixture_pair(100_000_000.0, 100_000_000)
    doc_cell3["numeric_value"] = None
    entry3 = xval_module.classify_divergence(doc_cell3, xbrl_fact3)
    assert entry3 is not None
    assert entry3["alert"] == "n/a"
    assert entry3["note"]
    assert entry3["pct_diff"] is None
    assert entry3["doc_value"] is None
    assert entry3["xbrl_value"] == 100_000_000


def test_within_grain_divergence_annotated_scale_rounding(xval_module):
    """Task 10 (REVISED, two-source tolerance): on a matched (doc_cell,
    xbrl_fact) pair, a NON-ZERO divergence that falls fully within the
    rounding grain implied by the doc cell's `decimals` (e.g. decimals="-6"
    -> grain 10**6, half-grain tolerance 500000) is a benign artifact of the
    doc side's rounding, not a tagging error -> annotated
    `category: "scale/rounding"`, `alert` forced "low",
    `source_mode: "two-source"`, with an explanatory note (plan Notes
    §Scale/rounding grounding correction; brief Requirement: Recognize
    scale/rounding as a legitimate divergence source).

    NEGATIVE (non-vacuous): a divergence BEYOND the grain is a real
    divergence and must NOT be labeled scale/rounding — the classifier's
    normal band stands.
    """
    # Positive: |diff| 200000 <= half-grain 500000 (decimals="-6" -> grain 10**6).
    doc_cell, xbrl_fact = _classify_fixture_pair(1234000000.0, 1233800000)
    entry = xval_module.classify_divergence(doc_cell, xbrl_fact)

    assert entry["category"] == "scale/rounding"
    assert entry["alert"] == "low"
    assert entry["source_mode"] == "two-source"
    assert entry["note"]

    # Negative: |diff| 6200000 > half-grain 500000 -> a real divergence, NOT
    # labeled scale/rounding.
    doc_cell2, xbrl_fact2 = _classify_fixture_pair(1240000000.0, 1233800000)
    entry2 = xval_module.classify_divergence(doc_cell2, xbrl_fact2)

    assert entry2["category"] != "scale/rounding"


def test_scale_rounding_guards_skip_non_rounding_cases(xval_module):
    """Task 10 guard branches: the scale/rounding label must NOT fire when
    (a) there is ZERO divergence (a clean match is not a rounding artifact),
    or (b) the doc cell's `decimals` is missing/malformed (no grain can be
    derived) — in both cases `category` stays unlabeled and no crash occurs.
    """
    # (a) Zero divergence -> not a rounding artifact.
    doc_cell, xbrl_fact = _classify_fixture_pair(1234000000.0, 1234000000)
    entry = xval_module.classify_divergence(doc_cell, xbrl_fact)
    assert entry["category"] != "scale/rounding"

    # (b) Malformed/missing `decimals` -> grain underivable -> skip, no crash.
    doc_cell2, xbrl_fact2 = _classify_fixture_pair(1234000000.0, 1233800000)
    doc_cell2["decimals"] = None
    entry2 = xval_module.classify_divergence(doc_cell2, xbrl_fact2)
    assert entry2["category"] != "scale/rounding"


def test_decimal_disagreement_dqc_241(xval_module):
    """Task 13: XBRL US DQC rule 2.4.1 — a fact's `decimals` attribute
    implies a rounding grain (e.g. decimals="-6" -> grain 10**6); if the
    reported value itself carries NON-ZERO digits below that grain, the
    `decimals` attribute disagrees with the digits actually reported — a
    structural defect in the filing's own tagging, distinct from a doc/XBRL
    value MISMATCH (Task 8's classifier bands) and from Task 10's
    two-source `scale/rounding` label. Single-source: this is a property of
    ONE fact's own (value, decimals) pair — no second source is consulted
    (plan Notes §Declared schemas `source_mode`).
    """
    period = {"type": "duration", "start": "2023-10-01", "end": "2024-09-28"}

    def _doc_cell(value: float, decimals: str) -> dict:
        return {
            "concept": "us-gaap:Revenues",
            "period": period,
            "dimension": None,
            "value_displayed": str(value),
            "numeric_value": value,
            "decimals": decimals,
            "citation": {
                "accession": "0000320193-24-000123",
                "statement_name": "IncomeStatement",
                "row": 5,
                "col": "duration_2023-10-01_2024-09-28",
                "label": "Total net sales",
                "context_ref": "c-1",
                "fact_id": "f-1",
            },
        }

    # POSITIVE: value carries non-zero digits below the decimals="-6" grain
    # (10**6) -> decimals disagrees with the digits actually reported.
    disagreeing_cell = _doc_cell(1233800000.0, "-6")
    entry = xval_module.check_decimal_disagreement(disagreeing_cell)
    assert entry is not None
    assert entry["category"] == "decimal-disagreement (DQC 2.4.1)"
    assert entry["source_mode"] == "single-source"
    assert entry["note"]

    # NEGATIVE/control (non-vacuous): a clean multiple of the grain -> no
    # sub-grain digits -> NOT flagged. Also proves this is a genuinely
    # distinct category from Task 10's two-source `scale/rounding` label —
    # this single-source check never emits that category.
    clean_cell = _doc_cell(1234000000.0, "-6")
    assert xval_module.check_decimal_disagreement(clean_cell) is None

    # POSITIVE-decimals clean multiple (fractional grain, decimals="2" ->
    # grain 0.01): 1_000_000.45 is an exact multiple of 0.01 and must NOT
    # be flagged. This is the regression case for a fixed-absolute-
    # tolerance bug: `value % grain` float noise scales with `value`'s
    # magnitude (not `grain`'s), so a large clean value against a small
    # fractional grain produces modulo noise far above a `grain * 1e-9`
    # tolerance band and false-flags. A magnitude-relative check (scaling
    # to integer space) must not repeat that.
    positive_clean_cell = _doc_cell(1000000.45, "2")
    assert xval_module.check_decimal_disagreement(positive_clean_cell) is None

    # POSITIVE-decimals genuine disagreement: 1_000_000.456 carries a
    # non-zero digit below the decimals="2" grain (0.01) -> flagged.
    positive_disagreeing_cell = _doc_cell(1000000.456, "2")
    entry3 = xval_module.check_decimal_disagreement(positive_disagreeing_cell)
    assert entry3 is not None
    assert entry3["category"] == "decimal-disagreement (DQC 2.4.1)"
    assert entry3["source_mode"] == "single-source"
    assert entry3["note"]


def test_decimal_disagreement_guards_skip_non_evaluable_cases(xval_module):
    """Task 13 guard branches: `check_decimal_disagreement` fails soft
    (`None`, no crash) when the fact cannot be evaluated at all — a
    missing `numeric_value`, or a missing/malformed `decimals` from which
    no grain can be derived.
    """
    period = {"type": "duration", "start": "2023-10-01", "end": "2024-09-28"}

    def _doc_cell(value, decimals) -> dict:
        return {
            "concept": "us-gaap:Revenues",
            "period": period,
            "dimension": None,
            "value_displayed": str(value),
            "numeric_value": value,
            "decimals": decimals,
            "citation": {
                "accession": "0000320193-24-000123",
                "statement_name": "IncomeStatement",
                "row": 5,
                "col": "duration_2023-10-01_2024-09-28",
                "label": "Total net sales",
                "context_ref": "c-1",
                "fact_id": "f-1",
            },
        }

    # (a) numeric_value is None -> underivable -> skip, no crash.
    none_value_cell = _doc_cell(None, "-6")
    assert xval_module.check_decimal_disagreement(none_value_cell) is None

    # (b) decimals is None -> grain underivable -> skip, no crash.
    none_decimals_cell = _doc_cell(1233800000.0, None)
    assert xval_module.check_decimal_disagreement(none_decimals_cell) is None

    # (c) decimals is malformed (non-numeric string) -> grain underivable
    # -> skip, no crash.
    malformed_decimals_cell = _doc_cell(1233800000.0, "not-a-number")
    assert xval_module.check_decimal_disagreement(malformed_decimals_cell) is None


def test_restatement_signal_cites_both_accessions(xval_module):
    """Task 12: a companyfacts (concept, period) tagged with a DIFFERENT
    value under a DIFFERENT `accn` in two filings (e.g. the FY2023 10-K's
    own tagging of FY2023 vs the FY2024 10-K's FY2023 comparative) is
    classified `restatement-signal`, citing BOTH accession numbers and
    retaining both values — NOT a doc-vs-XBRL tagging error (spec :129-136,
    "Prior-year comparative restated in the current filing").

    Built via `build_source_b_accn_groups`, NOT `build_source_b_index` —
    the latter is last-write-wins (Task 4's docstring) and would silently
    drop the earlier filing's row for this same period; restatement
    detection needs BOTH.

    NEGATIVE controls (non-vacuous):
    1. `us-gaap:CostOfRevenue` appears in only ONE filing (single accn) —
       no restatement-signal for it.
    2. `us-gaap:OperatingIncomeLoss` appears in TWO filings but with the
       IDENTICAL value both times — a same-period re-tag with no value
       change is not a restatement either.
    """
    source_b_pack = {
        "cik": 320193,
        "facts": {
            "us-gaap": {
                "Revenues": [
                    # FY2023 10-K's own-year tagging of the FY2023 period.
                    {
                        "start": "2022-10-01",
                        "end": "2023-09-30",
                        "value": 383285000000,
                        "accn": "0000320193-23-000106",
                        "form": "10-K",
                        "fy": 2023,
                        "fp": "FY",
                        "filed": "2023-11-03",
                    },
                    # FY2024 10-K's PRIOR-YEAR comparative for the SAME
                    # FY2023 period — restated to a DIFFERENT value.
                    {
                        "start": "2022-10-01",
                        "end": "2023-09-30",
                        "value": 383800000000,
                        "accn": "0000320193-24-000123",
                        "form": "10-K",
                        "fy": 2024,
                        "fp": "FY",
                        "filed": "2024-11-01",
                    },
                ],
                # Control 1: only ONE filing tags this period at all.
                "CostOfRevenue": [
                    {
                        "start": "2023-10-01",
                        "end": "2024-09-28",
                        "value": 210352000000,
                        "accn": "0000320193-24-000123",
                        "form": "10-K",
                        "fy": 2024,
                        "fp": "FY",
                        "filed": "2024-11-01",
                    },
                ],
                # Control 2: TWO filings, IDENTICAL value both times — not a
                # restatement (no divergence).
                "OperatingIncomeLoss": [
                    {
                        "start": "2022-10-01",
                        "end": "2023-09-30",
                        "value": 114301000000,
                        "accn": "0000320193-23-000106",
                        "form": "10-K",
                        "fy": 2023,
                        "fp": "FY",
                        "filed": "2023-11-03",
                    },
                    {
                        "start": "2022-10-01",
                        "end": "2023-09-30",
                        "value": 114301000000,
                        "accn": "0000320193-24-000123",
                        "form": "10-K",
                        "fy": 2024,
                        "fp": "FY",
                        "filed": "2024-11-01",
                    },
                ],
            }
        },
    }

    signals = xval_module.detect_restatement_signals(source_b_pack)

    assert len(signals) == 1
    signal = signals[0]
    assert signal["concept"] == "us-gaap:Revenues"
    assert signal["category"] == "restatement-signal"
    assert signal["source_mode"] == "single-source"
    assert signal["earlier_accn"] == "0000320193-23-000106"
    assert signal["later_accn"] == "0000320193-24-000123"
    assert signal["earlier_value"] == 383285000000
    assert signal["later_value"] == 383800000000

    # Negative controls: neither the single-filing nor the identical-value
    # concept produces a signal.
    signaled_concepts = {s["concept"] for s in signals}
    assert "us-gaap:CostOfRevenue" not in signaled_concepts
    assert "us-gaap:OperatingIncomeLoss" not in signaled_concepts


def test_restatement_signal_survives_reverted_middle_value(xval_module):
    """Task 12 fix (round 1, code-quality 🟡): a (concept, period) with 3+
    accns where the FIRST and LAST filings happen to report the SAME value
    but a MIDDLE filing diverges (restated, then reverted) must still emit
    a restatement-signal. A naive first-vs-last-only comparison silently
    drops this shape because `earlier["value"] == later["value"]`
    short-circuits even though a genuine divergence occurred. This is NOT
    a rare edge: US SEC income-statement/cash-flow tables routinely carry
    3 years of comparative figures per filing, so 3+ accns tagging one
    (concept, period) is the common case for this data.

    The cited pair must be two accns whose values ACTUALLY DIFFER — never
    the identical first/last pair.
    """
    source_b_pack = {
        "cik": 320193,
        "facts": {
            "us-gaap": {
                # Restated-then-reverted: filed order 100 -> 120 -> 100.
                # First and last values coincide; the middle filing is
                # the genuine divergence.
                "GrossProfit": [
                    {
                        "start": "2021-10-01",
                        "end": "2022-09-24",
                        "value": 100,
                        "accn": "0000320193-22-000100",
                        "form": "10-K",
                        "fy": 2022,
                        "fp": "FY",
                        "filed": "2022-10-28",
                    },
                    {
                        "start": "2021-10-01",
                        "end": "2022-09-24",
                        "value": 120,
                        "accn": "0000320193-23-000106",
                        "form": "10-K",
                        "fy": 2023,
                        "fp": "FY",
                        "filed": "2023-11-03",
                    },
                    {
                        "start": "2021-10-01",
                        "end": "2022-09-24",
                        "value": 100,
                        "accn": "0000320193-24-000123",
                        "form": "10-K",
                        "fy": 2024,
                        "fp": "FY",
                        "filed": "2024-11-01",
                    },
                ],
                # Control: 3 accns, ALL identical values -> no signal.
                "ResearchAndDevelopmentExpense": [
                    {
                        "start": "2021-10-01",
                        "end": "2022-09-24",
                        "value": 26251000000,
                        "accn": "0000320193-22-000100",
                        "form": "10-K",
                        "fy": 2022,
                        "fp": "FY",
                        "filed": "2022-10-28",
                    },
                    {
                        "start": "2021-10-01",
                        "end": "2022-09-24",
                        "value": 26251000000,
                        "accn": "0000320193-23-000106",
                        "form": "10-K",
                        "fy": 2023,
                        "fp": "FY",
                        "filed": "2023-11-03",
                    },
                    {
                        "start": "2021-10-01",
                        "end": "2022-09-24",
                        "value": 26251000000,
                        "accn": "0000320193-24-000123",
                        "form": "10-K",
                        "fy": 2024,
                        "fp": "FY",
                        "filed": "2024-11-01",
                    },
                ],
            }
        },
    }

    signals = xval_module.detect_restatement_signals(source_b_pack)
    signaled = {s["concept"]: s for s in signals}

    assert "us-gaap:GrossProfit" in signaled, (
        "restated-then-reverted (first == last, middle diverges) must still signal"
    )
    signal = signaled["us-gaap:GrossProfit"]
    assert signal["earlier_value"] != signal["later_value"], (
        "cited pair must be two accns whose values actually differ"
    )
    assert signal["earlier_accn"] == "0000320193-23-000106"
    assert signal["earlier_value"] == 120
    assert signal["later_accn"] == "0000320193-24-000123"
    assert signal["later_value"] == 100

    assert "us-gaap:ResearchAndDevelopmentExpense" not in signaled


def test_no_counterpart_routes_to_single_source(xval_module):
    """Task 7: a Source-A doc cell whose (concept, period, dimension) triple
    has NO Source-B counterpart is recorded UNMATCHED and routed to the
    single-source bucket — never paired with an unrelated fact (plan Notes
    §Anti-fabrication invariant). A genuinely-matching cell is included
    alongside it so the partition is actually exercised, not vacuously
    all-unmatched.
    """
    matched_period = {"type": "duration", "start": "2023-10-01", "end": "2024-09-28"}

    def _doc_cell(concept: str, period: dict, label: str) -> dict:
        return {
            "concept": concept,
            "period": period,
            "dimension": None,
            "value_displayed": "391035000000",
            "numeric_value": 391035000000.0,
            "decimals": "-6",
            "citation": {
                "accession": "0000320193-24-000123",
                "statement_name": "IncomeStatement",
                "row": 5,
                "col": "duration_2023-10-01_2024-09-28",
                "label": label,
                "context_ref": "c-1",
                "fact_id": "f-1",
            },
        }

    matched_cell = _doc_cell("us-gaap:Revenues", matched_period, "Total net sales")
    # No Source-B fact exists for this concept at all -> must NOT be paired
    # with the unrelated us-gaap:Revenues fact above (a position/label-based
    # matcher would wrongly grab it).
    unmatched_cell = _doc_cell(
        "us-gaap:ResearchAndDevelopmentExpense", matched_period, "R&D expense"
    )

    source_b_pack = {
        "cik": 320193,
        "facts": {
            "us-gaap": {
                "Revenues": [
                    {
                        "start": "2023-10-01",
                        "end": "2024-09-28",
                        "value": 391035000000,
                        "accn": "0000320193-24-000123",
                        "form": "10-K",
                        "fy": 2024,
                        "fp": "FY",
                        "filed": "2024-11-01",
                    }
                ]
            }
        },
    }
    index = xval_module.build_source_b_index(source_b_pack)
    source_a_pack = {"cells": [matched_cell, unmatched_cell]}

    result = xval_module.route_cells(source_a_pack, index)

    assert len(result["matched"]) == 1
    doc_cell, xbrl_fact = result["matched"][0]
    assert doc_cell["concept"] == "us-gaap:Revenues"
    assert xbrl_fact["value"] == 391035000000

    assert len(result["single_source"]) == 1
    assert result["single_source"][0]["concept"] == "us-gaap:ResearchAndDevelopmentExpense"
    # Never silently paired with the unrelated Revenues fact.
    assert result["single_source"][0] is unmatched_cell
