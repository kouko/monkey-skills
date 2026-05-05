"""Tests for runtime --sector-benchmark flag (v2.2.0-c-bench).

Uses offline fixtures for both the anchor pack and a stand-in
sector-etf-aggregate-XLK.json placed under references/. Network-free.
"""
from __future__ import annotations

import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "analysis-comps" / "scripts"
COMPS_SCRIPT = SCRIPTS / "comps_compute.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
REFERENCES = ROOT / "skills" / "analysis-comps" / "references"

ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def _run(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT), *args],
        capture_output=True, text=True, timeout=timeout, env=ENV, cwd=str(ROOT),
    )


def test_sector_benchmark_flag_accepted(tmp_path):
    """Flag parses; no error path. Behavior tested in later tasks."""
    anchor = FIXTURES / "comps_anchor_aapl.json"
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    proc = _run([
        "--mode", "compute",
        "--anchor", str(anchor), "--anchor-base", str(base), "--peers", str(peer),
        "--sector-benchmark",
    ])
    # The flag is parsed; either the run succeeds (block emitted with stub) OR
    # it returns 0/0-output without error. We only assert the flag did not
    # cause a parse error (rc != 2).
    assert proc.returncode != 2, f"--sector-benchmark not recognized: {proc.stderr}"


# ---------------------------------------------------------------------------
# T7 — Block emission, divergence, banding
# ---------------------------------------------------------------------------

@pytest.fixture
def stub_xlk_aggregate(tmp_path):
    """Override the references/ aggregate path so test uses fixture, not real
    weekly file. Patches an env var the comps_compute reader honors."""
    sample = FIXTURES / "sector-etf-aggregate-xlk-sample.json"
    target = tmp_path / "sector-etf-aggregate-XLK.json"
    shutil.copy(sample, target)
    yield tmp_path


def test_etf_benchmark_block_emitted_when_flag(stub_xlk_aggregate):
    # Use the with_sector variant so AAPL routes to tech-saas → XLK (per
    # etf-schema-map.json inverse). Without sector/industry the anchor would
    # fall back to schema_id=default → XLB (alphabetical first), which would
    # not match the XLK aggregate we stage.
    anchor = FIXTURES / "comps_anchor_aapl_with_sector.json"
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    env = {**ENV, "INVESTING_TOOLKIT_AGGREGATES_DIR": str(stub_xlk_aggregate)}
    proc = subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute", "--anchor", str(anchor), "--anchor-base", str(base),
         "--peers", str(peer), "--sector-benchmark"],
        capture_output=True, text=True, timeout=60, env=env, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    bench = payload["anchor"]["etf_benchmark"]
    assert bench["etf"] == "XLK"   # AAPL → tech-saas schema → maps to XLK
    assert bench["schema_id"] == "tech-saas"
    assert "as_of" in bench
    # multiples: priceToSales present in both → banded; forwardPE null on
    # aggregate → band n/a (per Drift A: tech-saas schema has no trailingPE).
    assert bench["multiples"]["priceToSales"]["band"] in {"in_line", "notable", "extreme"}
    assert bench["multiples"]["forwardPE"]["band"] == "n/a"
    assert bench["multiples"]["forwardPE"]["delta_pct"] is None


def test_no_etf_benchmark_block_without_flag(stub_xlk_aggregate):
    anchor = FIXTURES / "comps_anchor_aapl_with_sector.json"
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    proc = subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute", "--anchor", str(anchor), "--anchor-base", str(base),
         "--peers", str(peer)],   # no --sector-benchmark
        capture_output=True, text=True, timeout=60, env=ENV, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert "etf_benchmark" not in payload["anchor"], (
        "etf_benchmark must not appear without --sector-benchmark"
    )


@pytest.mark.parametrize("anchor_v,etf_v,expected_band", [
    (24.0, 24.1, "in_line"),    # 0.4% → in_line
    (28.0, 24.1, "in_line"),    # 16.2% → in_line
    (30.0, 24.1, "notable"),    # 24.5% → notable
    (50.0, 24.1, "extreme"),    # 107% → extreme
])
def test_band_classification(anchor_v, etf_v, expected_band):
    """Direct unit-test of the band function (skip subprocess)."""
    sys.path.insert(0, str(SCRIPTS))
    from comps_compute import _classify_etf_benchmark_band
    delta_pct = ((anchor_v - etf_v) / etf_v) * 100
    assert _classify_etf_benchmark_band(delta_pct) == expected_band


# ---------------------------------------------------------------------------
# T8 — Graceful-fallback paths: non-US ticker skip + stale-aggregate warning
# ---------------------------------------------------------------------------

def test_non_us_ticker_skipped(tmp_path):
    """7203.T (Toyota) → etf_benchmark.status == 'skipped' with non-US reason.

    The is_us heuristic in comps_compute treats any ticker containing '.' as
    non-US (e.g. .T / .JP / .TW / .HK / .KS suffixes), so the etf_benchmark
    block short-circuits before any aggregate lookup.
    """
    anchor = FIXTURES / "comps_anchor_7203_jp.json"
    base = FIXTURES / "comps_anchor_7203_jp_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"  # any peer; not under test
    proc = subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute", "--anchor", str(anchor), "--anchor-base", str(base),
         "--peers", str(peer), "--sector-benchmark"],
        capture_output=True, text=True, timeout=60, env=ENV, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    bench = payload["anchor"]["etf_benchmark"]
    assert bench.get("status") == "skipped"
    assert "non-US" in bench.get("reason", "")


def test_stale_aggregate_emits_warning(tmp_path):
    """When sector-etf-aggregate-XLK.json is older than 14 days,
    etf_benchmark.warnings includes 'aggregate stale'."""
    sample = json.loads((FIXTURES / "sector-etf-aggregate-xlk-sample.json").read_text())
    stale_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=20)).strftime("%Y-%m-%d")
    sample["as_of"] = stale_date
    target = tmp_path / "sector-etf-aggregate-XLK.json"
    target.write_text(json.dumps(sample, indent=2), encoding="utf-8")

    anchor = FIXTURES / "comps_anchor_aapl_with_sector.json"
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    env = {**ENV, "INVESTING_TOOLKIT_AGGREGATES_DIR": str(tmp_path)}
    proc = subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute", "--anchor", str(anchor), "--anchor-base", str(base),
         "--peers", str(peer), "--sector-benchmark"],
        capture_output=True, text=True, timeout=60, env=env, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    bench = payload["anchor"]["etf_benchmark"]
    assert any("aggregate stale" in w for w in bench.get("warnings", [])), bench.get("warnings")


def test_etf_benchmark_output_validates_against_schema(stub_xlk_aggregate):
    """jsonschema validation of compute output with etf_benchmark block present."""
    try:
        import jsonschema
    except ImportError:
        pytest.skip("jsonschema not installed in test env")

    schema = json.loads((REFERENCES / "schema-compute-output.json").read_text())
    anchor = FIXTURES / "comps_anchor_aapl.json"
    base = FIXTURES / "comps_anchor_aapl_memo_fetch.json"
    peer = FIXTURES / "comps_peer_msft.json"
    env = {**ENV, "INVESTING_TOOLKIT_AGGREGATES_DIR": str(stub_xlk_aggregate)}
    proc = subprocess.run(
        ["uv", "run", str(COMPS_SCRIPT),
         "--mode", "compute", "--anchor", str(anchor), "--anchor-base", str(base),
         "--peers", str(peer), "--sector-benchmark"],
        capture_output=True, text=True, timeout=60, env=env, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    jsonschema.validate(payload, schema)
