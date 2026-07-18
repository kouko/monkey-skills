"""test_memo_feed_chain.py — OFFLINE end-to-end memo-feed toolkit chain
(Task 7, docs/loom/plans/2026-07-18-memo-quarterly-kpi-wiring.md).

WHY: T2 (`quarterly-series` on kpi_xbrl.py) and T3 (`build-quarterly` on
kpi_memo_feed.py) each carry their own suites, but the memo pipeline runs
them as ONE chain: fact-pack JSON -> quarterly-series CLI -> series JSON ->
build-quarterly CLI -> memo-feed 1.1 JSON. This file drives that whole
chain on one committed fixture and asserts the 2.22.0 anti-fabrication
guarantees SURVIVE into the final feed (brief §Decision, machine-checkable
half): derived-lane tagging + PLURAL provenance, parallel calendar/fiscal
labels, verbatim coverage_flags, and the fail-closed refusal (poisoned
derived point -> exit 1, field named on stderr).

Fixture (committed, machine-captured — never hand-typed, docs/loom/memory/
fixtures-mirror-producer-shape.md): tests/analysis/fixtures/
xbrl_q4_derive.json `aapl_q4_derive` — real AAPL FY2025 filing windows:
three 10-Q single quarters (1000.0 / 2000.0 / 4100.0), the 9mo-YTD
(11100.0) and the 10-K FY total (14100.0), so Q4 derivation genuinely
fires (Q4 = 14100.0 − 11100.0 = 3000.0) with dual accessions. The
poisoned payload is DERIVED from the real quarterly-series CLI output
with the single field `source_accessions` stripped — no constructed XBRL
values anywhere.

Invocation choice (documented per the task constraints):
  - Stage 1 `quarterly-series` runs IN-PROCESS (kpi_xbrl.main() with
    patched argv), NOT via subprocess: kpi_xbrl.py declares PEP 723
    `dependencies = []` but its coverage-flag path lazily imports
    sec_edgar_client, whose MODULE-LEVEL `import requests` crashes a bare
    `uv run --script` subprocess in the offline env. The sys.modules
    stubs (`stub_data_layer_deps`, mirroring test_kpi_xbrl.py's
    convention and docs/loom/memory/
    importing-a-module-runs-its-module-level-imports.md) can only reach
    an in-process call — same ruling as
    test_kpi_xbrl.py::test_cli_quarterly_series_full_signature_groups.
  - Stage 2 `build-quarterly` runs as a REAL `uv run --script` subprocess
    (kpi_memo_feed.py is stdlib-only end-to-end), matching this
    directory's chain-test convention (test_cross_layer_chains.py) and
    giving a true process exit code for the fail-closed assertion.

No `@req` tags: this dispatch's plan traces work by named plan Tasks, NOT
by registered loom-spec REQ-ids — so `@req` is omitted per the
implementer contract (same convention as test_kpi_xbrl_quarterly_e2e.py).
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills"
ANALYSIS_FIXTURES = ROOT / "tests" / "analysis" / "fixtures"
KPI_XBRL_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_xbrl.py"
KPI_MEMO_FEED_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_memo_feed.py"

FACT_PACK_FIXTURE = ANALYSIS_FIXTURES / "xbrl_q4_derive.json"
COMPANY = "AAPL"  # the fixture pack's own `company` stamp (asserted below)


@pytest.fixture(scope="module")
def kpi_xbrl_module():
    spec = importlib.util.spec_from_file_location(
        "kpi_xbrl_memo_feed_chain", KPI_XBRL_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_xbrl_memo_feed_chain"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def stub_data_layer_deps():
    """Stub `requests` + `edgar` in sys.modules around the in-process
    quarterly-series call: its coverage path lazily imports
    sec_edgar_client (module-level `import requests`), neither installed
    in the offline suite env. Only the PURE `_dimension_quarterly_absence`
    helper is exercised — the stubs are never touched. Mirrors
    test_kpi_xbrl.py's `stub_data_layer_deps`."""
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


@pytest.fixture
def series_payload(
    kpi_xbrl_module, stub_data_layer_deps, tmp_path, monkeypatch, capsys
) -> dict:
    """Stage 1: run the REAL `quarterly-series` CLI in-process on the
    committed fact-pack fixture and return its parsed series JSON — the
    exact artifact the memo pipeline hands to `build-quarterly`."""
    pack = json.loads(FACT_PACK_FIXTURE.read_text(encoding="utf-8"))[
        "aapl_q4_derive"
    ]
    assert pack["company"] == COMPANY  # provenance sanity, not a hand-typed value
    pack_path = tmp_path / "factpack.json"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")

    monkeypatch.setattr(
        sys, "argv",
        ["kpi_xbrl.py", "quarterly-series", "--file", str(pack_path)],
    )
    rc = kpi_xbrl_module.main()
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)

    # Chain precondition: the fixture's 10-Q quarters + FY basis made the
    # Q4 derivation genuinely fire — otherwise the derived-lane survival
    # assertions (and the poison test) would be vacuous.
    assert payload["series"], "quarterly-series emitted no signature groups"
    assert payload["series"][0]["derived_points"], (
        "Q4 derivation did not fire — the fixture must supply both 10-Q "
        "quarters and an FY basis"
    )
    return payload


def _run_build_quarterly(
    series_payload: dict, tmp_path: Path, *, name: str
) -> subprocess.CompletedProcess:
    """Stage 2: run the REAL `build-quarterly` CLI as a subprocess on a
    series-payload file (production wiring passes JSON files between the
    two CLIs)."""
    payload_path = tmp_path / f"{name}.json"
    payload_path.write_text(json.dumps(series_payload), encoding="utf-8")
    env = {
        **os.environ,
        # Point the tier-① store somewhere disposable — the quarterly arm
        # must never consult it, but never risk a real store either.
        "KPI_STORE_DIR": str(tmp_path / "store"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    return subprocess.run(
        [
            "uv", "run", "--script", str(KPI_MEMO_FEED_SCRIPT),
            "build-quarterly", "--company", COMPANY,
            "--generated-at", "2026-07-18T00:00:00Z",
            "--file", str(payload_path),
        ],
        capture_output=True, text=True, timeout=60, env=env,
    )


def test_chain_factpack_to_memo_feed_preserves_guarantees(
    series_payload, tmp_path
):
    """Task 7 acceptance (happy path): fact-pack -> quarterly-series ->
    build-quarterly -> final 1.1 feed, with the anti-fabrication
    guarantees intact end-to-end:

      1. the derived Q4 survives with `derived: True` + PLURAL
         source_accessions/source_forms (never the singular keys);
      2. every reported point still carries the parallel calendar/fiscal
         label pair — including the honestly-divergent fiscal-Q1 /
         calendar-Q4 point;
      3. coverage_flags arrive VERBATIM;
      4. envelope is the quarterly arm's TRUSTED 1.1.
    """
    result = _run_build_quarterly(series_payload, tmp_path, name="series")
    assert result.returncode == 0, (
        f"build-quarterly failed on real quarterly-series output: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    feed = json.loads(result.stdout)

    # (4) Envelope: the quarterly/XBRL arm, admitted fail-closed.
    assert feed["_memo_feed_schema_version"] == "1.1"
    assert feed["status"] == "TRUSTED"
    assert feed["company"] == COMPANY
    assert feed["generated_at"] == "2026-07-18T00:00:00Z"

    # ONE signature group in the pack (AAPL iPhone), passed through whole.
    assert len(feed["series"]) == 1
    entry = feed["series"][0]
    assert entry["signature"]["concept"] == (
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
    )

    # (1) The derived Q4 survives into the FINAL feed, still segregated in
    # the derived lane, still tagged, with PLURAL provenance and never the
    # singular reported-point keys. Values are the fixture's machine-
    # captured figures: Q4 = FY 14100.0 − 9mo-YTD 11100.0.
    assert len(entry["derived_points"]) == 1
    q4 = entry["derived_points"][0]
    assert q4["derived"] is True
    assert q4["value"] == 3000.0
    assert q4["source_accessions"] == [
        "0000320193-25-000079", "0000320193-25-000073",
    ]
    assert q4["source_forms"] == ["10-K", "10-Q"]
    assert "source_accession" not in q4
    assert "source_form" not in q4
    assert q4["dqc"]["type"] == "derived_q4"
    # No derived point leaked into the reported lane.
    assert not any(p.get("derived") for p in entry["points"])

    # (2) Parallel calendar/fiscal pair intact on every reported point in
    # the final feed.
    assert sorted(p["value"] for p in entry["points"]) == [1000.0, 2000.0, 4100.0]
    for p in entry["points"]:
        assert isinstance(p["calendar_year"], int)
        assert p["calendar_quarter"] in {"Q1", "Q2", "Q3", "Q4"}
        assert p["period"] == "2025"  # fiscal label
        assert p["period_type"] in {"Q1", "Q2", "Q3"}
        assert p["source_form"] == "10-Q"
    # The honest divergent pair survives: fiscal FY2025-Q1 ends in
    # CALENDAR 2024-Q4 (late-September AAPL FYE) — the pair the parallel
    # labels exist to keep distinct.
    q1 = next(p for p in entry["points"] if p["period_type"] == "Q1")
    assert q1["calendar_year"] == 2024
    assert q1["calendar_quarter"] == "Q4"

    # (3) coverage_flags survived VERBATIM — and so did the series block
    # (the arm's contract is verbatim passthrough after validation, not
    # reshaping).
    assert feed["coverage_flags"] == series_payload["coverage_flags"]
    assert feed["series"] == series_payload["series"]


def test_chain_poisoned_derived_point_fails_closed(series_payload, tmp_path):
    """Task 7 acceptance (refusal path): the SAME real quarterly-series
    output with ONE field stripped — the derived point's
    `source_accessions` — makes `build-quarterly` exit 1 and name the
    field on stderr (no feed, no raw traceback). This is the fail-closed
    guarantee holding at the chain seam, not just in T3's unit suite."""
    poisoned = copy.deepcopy(series_payload)
    del poisoned["series"][0]["derived_points"][0]["source_accessions"]

    result = _run_build_quarterly(poisoned, tmp_path, name="poisoned")
    assert result.returncode == 1, (
        f"expected fail-closed exit 1, got {result.returncode}: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert result.stdout.strip() == ""  # nothing bundled, nothing leaked
    assert "source_accessions" in result.stderr
    assert "Traceback" not in result.stderr
