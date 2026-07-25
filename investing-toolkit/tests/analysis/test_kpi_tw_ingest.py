"""Tests for analysis-kpi/scripts/kpi_tw_ingest.py — TW filing envelope ->
kpi_store driver (TW-market kpi_store producer, Task 3).

Mirrors test_kpi_xbrl_ingest.py: the `ingest` verb is exercised end-to-end
through its CLI subprocess, the durable store redirected to a tmp dir via
KPI_STORE_DIR (the ~/.local/share store is never touched). The TW filing
envelope (canonical + facts + co_id/year/season/report_id) is built from
the real captured 1101 fixture through the production data-markets pipeline
(test scaffolding ONLY — kpi_tw_ingest never imports data-markets; it reads
the canonical + facts it is GIVEN as a JSON file).

kpi_tw_ingest reads a filing envelope the caller already produced because
the run_pipeline output carries `canonical` but NOT the parsed `facts`
(twse_ixbrl.py:156), and `as_of` derivation needs the auth-date fact — so
the envelope pairs the canonical with the facts + the filing coordinates.

No `@req` tags: this dispatch's plan (docs/loom/plans/2026-07-25-tw-kpi-
store-producer.md) traces work by named plan Tasks, NOT registered loom-spec
REQ-ids — so `@req` is omitted per the implementer contract.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

from conftest import KPI_STORE_SCRIPT, ROOT, SKILLS

import pytest

INGEST_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_tw_ingest.py"
TWSE_PARSER_SCRIPT = SKILLS / "data-markets" / "scripts" / "twse_ixbrl_parser.py"
TWSE_CANONICAL_SCRIPT = SKILLS / "data-markets" / "scripts" / "twse_ixbrl_canonical.py"
TWSE_1101_FIXTURE = ROOT / "tests" / "data" / "fixtures" / "twse_ixbrl_1101_2026Q1_C.html"


def _load(name: str, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def filing_1101() -> dict:
    """Build the real-shaped TW filing envelope from the captured 1101 fixture
    through the production data-markets parser + canonical mapper (scaffolding
    only). The envelope is exactly what kpi_tw_ingest consumes: the canonical
    KPI fields + the parsed facts + the filing coordinates.
    """
    parser = _load("twse_ixbrl_parser_ingest_test", TWSE_PARSER_SCRIPT)
    canonical_mod = _load("twse_ixbrl_canonical_ingest_test", TWSE_CANONICAL_SCRIPT)
    doc = parser.decode_ixbrl_document(TWSE_1101_FIXTURE.read_bytes())
    facts = parser.parse_ixbrl_facts(doc)
    canonical = canonical_mod.build_canonical(facts)
    return {
        "canonical": canonical,
        "facts": facts,
        "co_id": "1101",
        "year": 2026,
        "season": 1,
        "report_id": "C",
    }


def _run_ingest(filing_path, env) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(INGEST_SCRIPT), "ingest", "--filing", str(filing_path)],
        capture_output=True,
        text=True,
        timeout=90,
        env=env,
    )


def _run_dump(company, env) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(KPI_STORE_SCRIPT), "dump", "--company", company],
        capture_output=True,
        text=True,
        timeout=90,
        env=env,
    )


def _total_observations(payload: dict) -> int:
    return sum(
        len(entry["observations"])
        for series in payload["series"]
        for entry in series["periods"]
    )


def test_kpi_tw_ingest_appends_points(tmp_path, filing_1101):
    """Ingesting the 1101 filing envelope writes the expected TW points into a
    tmp store (read back via kpi_store dump), and a SECOND ingest of the same
    filing is idempotent — the store's 5-tuple dedup adds no duplicate points.
    """
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    filing_path = tmp_path / "filing.json"
    filing_path.write_text(json.dumps(filing_1101), encoding="utf-8")

    result = _run_ingest(filing_path, env)
    assert result.returncode == 0, (
        f"ingest failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    summary = json.loads(result.stdout)
    assert summary["company"] == "1101"
    assert summary["appended"] > 0

    # Writes landed ONLY in the tmp store dir (durable store untouched).
    assert store_dir.exists(), "ingest did not write to the tmp KPI_STORE_DIR"
    assert list(store_dir.glob("*.json")), "no series file written to tmp store"

    dump = _run_dump("1101", env)
    assert dump.returncode == 0, (
        f"dump failed: stdout={dump.stdout!r} stderr={dump.stderr!r}"
    )
    payload = json.loads(dump.stdout)

    kpi_ids = {s["kpi_id"] for s in payload["series"]}
    assert "revenue__basis-C" in kpi_ids
    assert "total_assets__basis-C" in kpi_ids

    # The current-quarter revenue value survives to the store with its TW
    # provenance derived from the filing coordinates (co_id+year+season+report_id).
    rev = next(s for s in payload["series"] if s["kpi_id"] == "revenue__basis-C")
    rev_obs = [obs for entry in rev["periods"] for obs in entry["observations"]]
    rev_current = next(o for o in rev_obs if o["period_end"] == "2026-03-31")
    assert rev_current["value"] == 33168148000.0
    assert rev_current["source_accession"] == "twse:1101:2026Q1:C"
    assert rev_current["source_table_id"] == "tw:ixbrl"
    assert rev_current["as_of"] == "2026-05-13"

    observations_after_first = _total_observations(payload)
    assert observations_after_first == summary["appended"]

    # Idempotency: a SECOND ingest of the SAME filing adds no duplicate points.
    result2 = _run_ingest(filing_path, env)
    assert result2.returncode == 0, (
        f"second ingest failed: stdout={result2.stdout!r} stderr={result2.stderr!r}"
    )
    dump2 = _run_dump("1101", env)
    payload2 = json.loads(dump2.stdout)
    assert _total_observations(payload2) == observations_after_first, (
        "second ingest of the same filing must be idempotent (no duplicate points)"
    )
