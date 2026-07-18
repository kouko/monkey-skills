"""Tests for analysis-kpi/scripts/kpi_memo_feed.py — the memo-feed contract
assembly (operational-kpi capability, slice 8, final offline slice).

Task 1 ships the module scaffold + `build_memo_feed(company, schema_version,
kpi_series, generated_at)`: a PURE-ASSEMBLY function (mirrors kpi_validate.py
— no `_store_fs`, no store-dir resolution, no file locking/writing) that
reuses `kpi_gate.is_trusted` (slice 5's reliability gate, same-skill import)
for the trust verdict and takes the series data as a caller-supplied
argument rather than querying `kpi_store` directly.

The store dir is redirected to a tmp path via the `KPI_STORE_DIR` env
override (shared by kpi_store/review_queue/kpi_schema/kpi_gate/kpi_memo_feed
— same durable DATA dir kpi_gate.is_trusted reads its gate record from).

No `@req` tags: this dispatch's plan/spec trace work by named change-folder
Requirements (operational-kpi / "Memo-feed contract is an explicit
artifact"), NOT by registered loom-spec REQ-ids — so `@req` is omitted per
the implementer contract (mirrors test_kpi_gate.py's rationale).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

from conftest import KPI_GATE_SCRIPT, KPI_MEMO_FEED_SCRIPT

import pytest


def _load_kpi_memo_feed_module():
    """Load kpi_memo_feed.py as an importable module.

    Its same-dir import shim does a plain `import kpi_gate`, which must
    resolve to THE SAME `kpi_gate` module object this test uses to set up
    gate state (add_labels/evaluate) — so we first ensure the scripts dir
    is on sys.path and a real "kpi_gate" module is imported/cached under
    its real name before loading kpi_memo_feed, rather than loading kpi_gate
    under a test-only alias (mirrors test_kpi_gate.py's fixture, but keeps
    the two modules' view of KPI_STORE_DIR-backed state consistent).
    """
    scripts_dir = str(KPI_GATE_SCRIPT.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    sys.modules.pop("kpi_gate", None)
    import kpi_gate  # noqa: E402

    sys.modules.pop("kpi_memo_feed_test", None)
    spec = importlib.util.spec_from_file_location("kpi_memo_feed_test", KPI_MEMO_FEED_SCRIPT)
    assert spec is not None and spec.loader is not None
    kpi_memo_feed = importlib.util.module_from_spec(spec)
    sys.modules["kpi_memo_feed_test"] = kpi_memo_feed
    spec.loader.exec_module(kpi_memo_feed)
    return kpi_memo_feed, kpi_gate


def test_build_memo_feed_trusted_vs_withheld(tmp_path, monkeypatch):
    """build_memo_feed must fail-closed on the reliability gate:

    (a) a company with a recorded TRUSTED verdict (set up via kpi_gate.
        add_labels + evaluate, mirroring test_kpi_gate.py's TRUSTED case)
        -> status TRUSTED, kpi_feeds bundles the supplied kpi_series
        verbatim, no withheld_reason.
    (b) a never-evaluated company -> status WITHHELD, kpi_feeds == [] (NO
        series values leaked), and withheld_reason carries kpi_gate's own
        fail-closed verdict string.

    Why this matters: the memo-feed contract is the last gate before an
    LLM-authored narrative sees extracted figures — if a below-bar or
    never-evaluated company's numbers leaked through anyway, the whole
    point of the reliability gate (slice 5) would be silently bypassed at
    the one seam that actually reaches the memo.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    kpi_memo_feed, kpi_gate = _load_kpi_memo_feed_module()

    # --- (a) TRUSTED setup, mirroring test_kpi_gate.py's TRUSTED case ---
    labels = [
        {"kpi_id": f"kpi_{i}", "period": "2024-Q1", "value": 100 + i}
        for i in range(5)
    ]
    kpi_gate.add_labels("MEMOCO", labels)
    kpi_gate.evaluate(
        "MEMOCO", "v1", [dict(label) for label in labels],
        threshold=0.95, min_samples=5, evaluated_at="2026-07-14T00:00:00Z",
    )
    assert kpi_gate.is_trusted("MEMOCO", "v1") is True, (
        "test setup sanity: MEMOCO/v1 must be TRUSTED before exercising build_memo_feed"
    )

    kpi_series = [
        {
            "kpi_id": "kpi_0",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                "source_cell_ref": "r5c2",
            }],
            "provenance": {"source_accession": "0000320193-24-000123"},
        },
    ]
    trusted_feed = kpi_memo_feed.build_memo_feed(
        "MEMOCO", "v1", kpi_series, generated_at="2026-07-14T00:00:00Z",
    )
    assert trusted_feed["_memo_feed_schema_version"] == "1.0"
    assert trusted_feed["company"] == "MEMOCO"
    assert trusted_feed["schema_version"] == "v1"
    assert trusted_feed["status"] == "TRUSTED"
    assert trusted_feed["kpi_feeds"] == kpi_series
    assert trusted_feed["generated_at"] == "2026-07-14T00:00:00Z"
    assert "withheld_reason" not in trusted_feed

    # --- (b) never-evaluated company -> WITHHELD, no series values ---
    withheld_feed = kpi_memo_feed.build_memo_feed(
        "NEVERCO", "v1", kpi_series, generated_at="2026-07-14T00:00:00Z",
    )
    assert withheld_feed["_memo_feed_schema_version"] == "1.0"
    assert withheld_feed["company"] == "NEVERCO"
    assert withheld_feed["schema_version"] == "v1"
    assert withheld_feed["status"] == "WITHHELD"
    assert withheld_feed["kpi_feeds"] == [], (
        "a WITHHELD feed must carry NO series values"
    )
    assert withheld_feed["withheld_reason"] == "WITHHELD"
    assert withheld_feed["generated_at"] == "2026-07-14T00:00:00Z"


def test_trusted_feed_refuses_provenanceless_point(tmp_path, monkeypatch):
    """Task 2: in the TRUSTED path, build_memo_feed must REFUSE loud
    (ValueError naming the missing field + kpi_id) if ANY series-point in
    the supplied kpi_series lacks complete provenance
    (source_accession/source_table_id/source_cell_ref — absent/None/empty
    any counts as missing). A fully-provenanced TRUSTED series still
    builds fine.

    Why this matters: the memo-feed contract is the last seam before an
    LLM-authored narrative sees extracted figures — an unattributed value
    bundled into a TRUSTED feed would be untraceable to its source cell,
    defeating the whole point of primary-source anchoring at the one
    boundary the memo actually reads from.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    kpi_memo_feed, kpi_gate = _load_kpi_memo_feed_module()

    labels = [
        {"kpi_id": f"kpi_{i}", "period": "2024-Q1", "value": 100 + i}
        for i in range(5)
    ]
    kpi_gate.add_labels("PROVCO", labels)
    kpi_gate.evaluate(
        "PROVCO", "v1", [dict(label) for label in labels],
        threshold=0.95, min_samples=5, evaluated_at="2026-07-14T00:00:00Z",
    )
    assert kpi_gate.is_trusted("PROVCO", "v1") is True, (
        "test setup sanity: PROVCO/v1 must be TRUSTED before exercising build_memo_feed"
    )

    provenanceless_series = [
        {
            "kpi_id": "kpi_0",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                # source_cell_ref missing entirely
            }],
        },
    ]
    with pytest.raises(ValueError) as excinfo:
        kpi_memo_feed.build_memo_feed(
            "PROVCO", "v1", provenanceless_series, generated_at="2026-07-14T00:00:00Z",
        )
    assert "source_cell_ref" in str(excinfo.value)
    assert "kpi_0" in str(excinfo.value)

    # An empty-string cell ref must also count as missing (not just absent).
    empty_cell_ref_series = [
        {
            "kpi_id": "kpi_1",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                "source_cell_ref": "",
            }],
        },
    ]
    with pytest.raises(ValueError):
        kpi_memo_feed.build_memo_feed(
            "PROVCO", "v1", empty_cell_ref_series, generated_at="2026-07-14T00:00:00Z",
        )

    # A WHITESPACE-ONLY provenance value is also rejected — a blank-looking
    # cite is effectively unattributed (same class as the whitespace-identity
    # bypass; `not x` alone would wrongly let "   " through).
    whitespace_ref_series = [
        {
            "kpi_id": "kpi_1",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                "source_cell_ref": "   ",
            }],
        },
    ]
    with pytest.raises(ValueError):
        kpi_memo_feed.build_memo_feed(
            "PROVCO", "v1", whitespace_ref_series, generated_at="2026-07-14T00:00:00Z",
        )

    # A fully-provenanced TRUSTED series builds fine.
    good_series = [
        {
            "kpi_id": "kpi_0",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                "source_cell_ref": "r5c2",
            }],
        },
    ]
    good_feed = kpi_memo_feed.build_memo_feed(
        "PROVCO", "v1", good_series, generated_at="2026-07-14T00:00:00Z",
    )
    assert good_feed["status"] == "TRUSTED"
    assert good_feed["kpi_feeds"] == good_series


def test_cli_build_memo_feed_roundtrip(tmp_path):
    """Task 3: the kpi_memo_feed.py CLI's `build` subcommand is a thin
    wrapper over build_memo_feed, exercised via real `uv run --script`
    subprocess invocations (mirrors test_kpi_gate.py's CLI roundtrip).

    Sets up a TRUSTED gate via kpi_gate's own CLI (same KPI_STORE_DIR),
    then drives kpi_memo_feed.py build:
      (a) a provenanced kpi_series for the TRUSTED company -> status
          TRUSTED feed on stdout, exit 0.
      (b) a never-evaluated company -> status WITHHELD, exit 0 (a validly-
          withheld company is not a CLI error).
      (c) a provenance-less TRUSTED point -> exit 1 (ValueError).
      (d) malformed JSON -> exit 2, no raw traceback.
      (e) --help lists `build`.
    """
    env = {**os.environ, "KPI_STORE_DIR": str(tmp_path)}

    labels = [
        {"kpi_id": f"kpi_{i}", "period": "2024-Q1", "value": 100 + i}
        for i in range(5)
    ]
    add_labels_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_GATE_SCRIPT), "add-labels",
            "--company", "CLIMEMOCO",
        ],
        input=json.dumps(labels),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert add_labels_result.returncode == 0, (
        f"add-labels setup failed: stdout={add_labels_result.stdout!r} "
        f"stderr={add_labels_result.stderr!r}"
    )

    evaluate_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_GATE_SCRIPT), "evaluate",
            "--company", "CLIMEMOCO", "--schema-version", "v1",
            "--threshold", "0.95", "--at", "2026-07-14T00:00:00Z",
        ],
        input=json.dumps([dict(label) for label in labels]),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert evaluate_result.returncode == 0, (
        f"evaluate setup failed: stdout={evaluate_result.stdout!r} "
        f"stderr={evaluate_result.stderr!r}"
    )
    assert json.loads(evaluate_result.stdout)["verdict"] == "TRUSTED"

    good_series = [
        {
            "kpi_id": "kpi_0",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                "source_cell_ref": "r5c2",
            }],
        },
    ]

    # (a) TRUSTED company + provenanced series -> status TRUSTED, exit 0.
    trusted_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT), "build",
            "--company", "CLIMEMOCO", "--schema-version", "v1",
            "--generated-at", "2026-07-14T00:00:00Z",
        ],
        input=json.dumps(good_series),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert trusted_result.returncode == 0, (
        f"build (TRUSTED) failed: stdout={trusted_result.stdout!r} "
        f"stderr={trusted_result.stderr!r}"
    )
    trusted_feed = json.loads(trusted_result.stdout)
    assert trusted_feed["status"] == "TRUSTED"
    assert trusted_feed["kpi_feeds"] == good_series

    # (b) never-evaluated company -> status WITHHELD, exit 0 (not an error).
    withheld_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT), "build",
            "--company", "CLINEVERCO", "--schema-version", "v1",
            "--generated-at", "2026-07-14T00:00:00Z",
        ],
        input=json.dumps(good_series),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert withheld_result.returncode == 0, (
        f"build (WITHHELD) must exit 0, not error: stdout={withheld_result.stdout!r} "
        f"stderr={withheld_result.stderr!r}"
    )
    withheld_feed = json.loads(withheld_result.stdout)
    assert withheld_feed["status"] == "WITHHELD"
    assert withheld_feed["kpi_feeds"] == []

    # (c) provenance-less TRUSTED point -> exit 1.
    bad_series = [
        {
            "kpi_id": "kpi_0",
            "points": [{
                "period": "2024-Q1", "value": 100,
                "source_accession": "0000320193-24-000123",
                "source_table_id": "ex99-1-operating-summary",
                # source_cell_ref missing
            }],
        },
    ]
    provenance_fail_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT), "build",
            "--company", "CLIMEMOCO", "--schema-version", "v1",
            "--generated-at", "2026-07-14T00:00:00Z",
        ],
        input=json.dumps(bad_series),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert provenance_fail_result.returncode == 1, provenance_fail_result.stderr
    assert "source_cell_ref" in provenance_fail_result.stderr

    # (d) malformed JSON -> exit 2, no raw traceback.
    malformed_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT), "build",
            "--company", "CLIMEMOCO", "--schema-version", "v1",
        ],
        input="{not valid json",
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert malformed_result.returncode == 2, malformed_result.stderr
    assert "Traceback" not in malformed_result.stderr, (
        "malformed build input must fail cleanly, not with a raw traceback"
    )

    # (e) --help lists the `build` subcommand.
    help_result = subprocess.run(
        ["uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert help_result.returncode == 0
    assert "build" in help_result.stdout


# ---------------------------------------------------------------------------
# Quarterly/XBRL arm (memo quarterly-KPI wiring slice — plan Task 3,
# docs/loom/plans/2026-07-18-memo-quarterly-kpi-wiring.md).
#
# The payloads below mirror the REAL `quarterly-series` CLI output shape
# (kpi_xbrl.build_quarterly_series run over the committed fixtures
# xbrl_quarterly_nvda_factpack.json / xbrl_q4_derive.json): exact field
# names captured from a live run; VALUES are synthetic (obviously fake
# round numbers) — never hand-typed XBRL figures presented as real.
# ---------------------------------------------------------------------------


def _quarterly_reported_point(**overrides) -> dict:
    """One reported point with the exact key set the T2 series emits."""
    point = {
        "company": "QTRCO",
        "kpi_id": "us-gaap:Revenues|ProductOrService=WidgetMember",
        "period_type": "Q1",
        "cumulative": False,
        "duration_class": "3mo",
        "period": "2026",
        "calendar_year": 2025,
        "calendar_quarter": "Q2",
        "period_end": "2025-04-30",
        "as_of": "2025-05-30",
        "value": 1000.0,
        "source_accession": "0000000000-25-000001",
        "source_form": "10-Q",
        "source_table_id": "xbrl:dimensional",
        "source_cell_ref": "us-gaap:Revenues|ProductOrService=WidgetMember",
        "source_kind": "xbrl-dimensional",
    }
    point.update(overrides)
    return point


def _quarterly_derived_point(**overrides) -> dict:
    """One derived-Q4 point with the exact key set the T2 series emits
    (plural source_accessions/source_forms + derived marker + dqc note)."""
    point = {
        "company": "QTRCO",
        "kpi_id": "us-gaap:Revenues|ProductOrService=WidgetMember",
        "period_type": "Q4",
        "cumulative": False,
        "duration_class": "3mo",
        "period": "2025",
        "calendar_year": 2025,
        "calendar_quarter": "Q3",
        "period_start": "2025-07-01",
        "period_end": "2025-09-30",
        "as_of": "2025-10-31",
        "value": 4000.0,
        "source_accessions": ["0000000000-25-000002", "0000000000-25-000001"],
        "source_forms": ["10-K", "10-Q"],
        "source_table_id": "xbrl:dimensional",
        "source_cell_ref": "us-gaap:Revenues|ProductOrService=WidgetMember",
        "source_kind": "xbrl-dimensional",
        "derived": True,
        "dqc": {
            "type": "derived_q4",
            "old": {"fy_total": 10000.0, "ytd9": 6000.0},
            "new": 4000.0,
            "accessions": ["0000000000-25-000002", "0000000000-25-000001"],
            "reason": "untagged Q4 derived as FY total minus 9mo-YTD",
        },
    }
    point.update(overrides)
    return point


def _quarterly_signature() -> dict:
    return {
        "concept": "us-gaap:Revenues",
        "dimensions": {"ProductOrService": "WidgetMember"},
        "consolidation": "OperatingSegmentsMember",
    }


def _quarterly_series_payload(**overrides) -> dict:
    """A minimal well-formed `quarterly-series` output payload."""
    payload = {
        "series": [
            {
                "signature": _quarterly_signature(),
                "points": [_quarterly_reported_point()],
                "derived_points": [_quarterly_derived_point()],
                "gaps": [],
            },
        ],
        "coverage_flags": [
            {
                "type": "dimension_quarterly_absence",
                "old": None,
                "new": None,
                "accessions": ["0000000000-25-000002"],
                "reason": "dimension absent from quarterly filings",
            },
        ],
    }
    payload.update(overrides)
    return payload


def test_build_quarterly_memo_feed_trusted_envelope(tmp_path, monkeypatch):
    """Plan Task 3 RED (a): a well-formed quarterly series payload yields a
    schema-1.1 TRUSTED envelope with series + coverage_flags passed through
    VERBATIM — and WITHOUT consulting the store gate: KPI_STORE_DIR points
    at an EMPTY store (no company was ever evaluated), so the tier-① gate
    would say WITHHELD; the quarterly/XBRL arm must return TRUSTED anyway,
    because its admission is machine-verified provenance completeness +
    DQC-schema'd coverage flags, NOT `kpi_gate.is_trusted` (user-ratified
    XBRL-lane trust ruling, plan §Decision Log 2026-07-18).

    Why this matters: if the quarterly arm silently consulted the store
    gate, every XBRL-sourced series would be blanket-WITHHELD (no store
    record exists for them) and the memo would never see machine-anchored
    quarterly KPIs at all.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))  # empty store — never evaluated
    kpi_memo_feed, _ = _load_kpi_memo_feed_module()

    payload = _quarterly_series_payload()
    feed = kpi_memo_feed.build_quarterly_memo_feed(
        "QTRCO", payload, generated_at="2026-07-18T00:00:00Z",
    )
    assert feed["_memo_feed_schema_version"] == "1.1"
    assert feed["company"] == "QTRCO"
    assert feed["status"] == "TRUSTED"
    assert feed["series"] == payload["series"]
    assert feed["coverage_flags"] == payload["coverage_flags"]
    assert feed["generated_at"] == "2026-07-18T00:00:00Z"
    assert "withheld_reason" not in feed


def test_build_quarterly_memo_feed_refuses_incomplete_provenance(
    tmp_path, monkeypatch
):
    """Plan Task 3 RED (b): fail-closed provenance rule on the quarterly
    arm — any violation raises ValueError naming the field + signature
    (mirrors the v1.0 whitespace-rejecting refusal; an unattributed value
    never reaches the memo artifact):

      - reported point: `source_accession` and `kpi_id` (the point-level
        concept identifier in the T2 shape) must be non-blank — absent /
        None / empty / whitespace-only all refuse;
      - derived point: `derived: True` plus non-empty PLURAL
        `source_accessions`/`source_forms` (each element non-blank);
      - a payload without a `series` list refuses (nothing to trust).
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    kpi_memo_feed, _ = _load_kpi_memo_feed_module()

    def expect_refusal(payload, *needles):
        with pytest.raises(ValueError) as excinfo:
            kpi_memo_feed.build_quarterly_memo_feed(
                "QTRCO", payload, generated_at="2026-07-18T00:00:00Z",
            )
        for needle in needles:
            assert needle in str(excinfo.value), (
                f"refusal must name {needle!r}: {excinfo.value}"
            )

    # Reported point: whitespace-only accession is effectively unattributed.
    payload = _quarterly_series_payload()
    payload["series"][0]["points"][0]["source_accession"] = "   "
    expect_refusal(payload, "source_accession", "us-gaap:Revenues")

    # Reported point: missing the concept identifier (kpi_id).
    payload = _quarterly_series_payload()
    del payload["series"][0]["points"][0]["kpi_id"]
    expect_refusal(payload, "kpi_id", "us-gaap:Revenues")

    # Derived point: missing the PLURAL source_accessions.
    payload = _quarterly_series_payload()
    del payload["series"][0]["derived_points"][0]["source_accessions"]
    expect_refusal(payload, "source_accessions", "us-gaap:Revenues")

    # Derived point: empty source_forms list is as unattributed as absent.
    payload = _quarterly_series_payload()
    payload["series"][0]["derived_points"][0]["source_forms"] = []
    expect_refusal(payload, "source_forms", "us-gaap:Revenues")

    # Derived point: derived marker must be literally True — a derived-lane
    # point without its marker could masquerade as reported in the memo.
    payload = _quarterly_series_payload()
    payload["series"][0]["derived_points"][0]["derived"] = False
    expect_refusal(payload, "derived", "us-gaap:Revenues")

    # Structurally broken payload: no `series` list at all.
    expect_refusal({"coverage_flags": []}, "series")


def test_build_quarterly_memo_feed_dqc_gates_coverage_flags(
    tmp_path, monkeypatch
):
    """Plan Task 3: every coverage flag passes `assert_dqc_schema`
    (imported from kpi_xbrl — the ONE DQC schema) BEFORE the verbatim
    passthrough; a flag missing a required key (here `reason`) refuses the
    whole feed. A schema-less flag passed through silently would let a
    malformed coverage story reach the memo unverified.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    kpi_memo_feed, _ = _load_kpi_memo_feed_module()

    payload = _quarterly_series_payload()
    del payload["coverage_flags"][0]["reason"]
    with pytest.raises(ValueError) as excinfo:
        kpi_memo_feed.build_quarterly_memo_feed(
            "QTRCO", payload, generated_at="2026-07-18T00:00:00Z",
        )
    assert "reason" in str(excinfo.value)


def test_build_quarterly_memo_feed_carries_week_lane_fields(tmp_path, monkeypatch):
    """Task 5 (docs/loom/plans/2026-07-18-52-53-week-filer-support.md):
    per-point `duration_weeks` and the supplementary `week_normalized_yoy`
    field (both computed upstream by kpi_xbrl.build_quarterly_series) ride
    through the 1.1 feed's VERBATIM passthrough unchanged — never stripped
    by the provenance check, which only inspects its own required fields.
    The additive-field ruling stays visible: the envelope version is NOT
    bumped for these optional per-point additions (see
    MEMO_FEED_QUARTERLY_SCHEMA_VERSION's own comment for the ruling)."""
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))
    kpi_memo_feed, _ = _load_kpi_memo_feed_module()

    payload = _quarterly_series_payload()
    payload["series"][0]["points"][0]["duration_weeks"] = 16
    payload["series"][0]["derived_points"][0]["duration_weeks"] = 17
    payload["series"][0]["derived_points"][0]["week_normalized_yoy"] = 0.125
    original_value = payload["series"][0]["derived_points"][0]["value"]

    feed = kpi_memo_feed.build_quarterly_memo_feed(
        "QTRCO", payload, generated_at="2026-07-18T00:00:00Z",
    )

    assert feed["_memo_feed_schema_version"] == "1.1"
    assert kpi_memo_feed.MEMO_FEED_QUARTERLY_SCHEMA_VERSION == "1.1"
    assert feed["series"][0]["points"][0]["duration_weeks"] == 16
    assert feed["series"][0]["derived_points"][0]["duration_weeks"] == 17
    assert feed["series"][0]["derived_points"][0]["week_normalized_yoy"] == 0.125
    # as-reported value untouched by the supplementary annotation.
    assert feed["series"][0]["derived_points"][0]["value"] == original_value


def test_cli_build_quarterly_roundtrip(tmp_path):
    """Plan Task 3: the `build-quarterly` subcommand wraps
    build_quarterly_memo_feed with the same fail-loud exit-code contract as
    `build` (real `uv run --script` subprocess invocations):

      (a) well-formed payload -> schema-1.1 TRUSTED feed on stdout, exit 0
          — with an EMPTY store (no gate record), proving the arm never
          consults kpi_gate;
      (b) poisoned payload (derived point stripped of source_accessions)
          -> exit 1, stderr names the field, no raw traceback;
      (c) malformed JSON -> exit 2;
      (d) a JSON array (not the series-payload object) -> exit 2;
      (e) --help lists `build-quarterly`.
    """
    env = {**os.environ, "KPI_STORE_DIR": str(tmp_path)}
    payload = _quarterly_series_payload()

    # (a) well-formed payload -> TRUSTED 1.1 feed, exit 0.
    ok_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT),
            "build-quarterly", "--company", "QTRCO",
            "--generated-at", "2026-07-18T00:00:00Z",
        ],
        input=json.dumps(payload),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert ok_result.returncode == 0, (
        f"build-quarterly (TRUSTED) failed: stdout={ok_result.stdout!r} "
        f"stderr={ok_result.stderr!r}"
    )
    feed = json.loads(ok_result.stdout)
    assert feed["_memo_feed_schema_version"] == "1.1"
    assert feed["status"] == "TRUSTED"
    assert feed["series"] == payload["series"]
    assert feed["coverage_flags"] == payload["coverage_flags"]
    assert feed["generated_at"] == "2026-07-18T00:00:00Z"

    # (b) poisoned derived point -> exit 1, field named, clean stderr.
    poisoned = _quarterly_series_payload()
    del poisoned["series"][0]["derived_points"][0]["source_accessions"]
    poisoned_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT),
            "build-quarterly", "--company", "QTRCO",
        ],
        input=json.dumps(poisoned),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert poisoned_result.returncode == 1, poisoned_result.stderr
    assert "source_accessions" in poisoned_result.stderr
    assert "Traceback" not in poisoned_result.stderr

    # (c) malformed JSON -> exit 2, no raw traceback.
    malformed_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT),
            "build-quarterly", "--company", "QTRCO",
        ],
        input="{not valid json",
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert malformed_result.returncode == 2, malformed_result.stderr
    assert "Traceback" not in malformed_result.stderr

    # (d) a JSON array is not a series payload -> exit 2 (nothing computed).
    array_result = subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT),
            "build-quarterly", "--company", "QTRCO",
        ],
        input=json.dumps([]),
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert array_result.returncode == 2, array_result.stderr

    # (e) --help lists the new subcommand.
    help_result = subprocess.run(
        ["uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60, env=env,
    )
    assert help_result.returncode == 0
    assert "build-quarterly" in help_result.stdout
