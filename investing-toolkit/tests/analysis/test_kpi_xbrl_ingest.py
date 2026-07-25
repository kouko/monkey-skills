"""Tests for analysis-kpi/scripts/kpi_xbrl_ingest.py — the store-feed driver
that wires the pure-compute `kpi_xbrl.facts_to_points` output into the durable
`kpi_store` (plan Task 3: store-feed driver — append each vintage, no collapse).

Two lanes:
  - RED 1 (`test_ingest_appends_each_vintage`): a real 2-vintage restatement
    fact-pack ingests as TWO store points under ONE kpi_id; the store's
    `dump` groups them into one period entry carrying BOTH observations with
    `disagreement=True` (the bitemporal † survives — no collapse). Exercised
    end-to-end through the `ingest` CLI subprocess, store redirected to a tmp
    dir via `KPI_STORE_DIR` (the durable ~/.local/share store is never
    touched).
  - RED 2 (`test_ingest_kpi_id_derivation`): the deterministic, injective
    kpi_id derivation from the FULL dimensional signature — distinct
    signatures → distinct ids, same signature → same id, a ConsolidationItems
    qualifier never changes the id, and the id is a readable stripped-member
    slug (never a human-authored string).

The real fixture is `tests/analysis/fixtures/xbrl_restatement_factpack.json`
(INTC CCG FY2020, two 10-Ks, same period, differing accession/value). It is
loaded and augmented with the producer's `period_start` field (Task 1 emits
it; the captured fixture predates it) — a real-shaped derivative, never a
hand-typed pack.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

from conftest import FIXTURES, KPI_STORE_SCRIPT, SKILLS

import pytest

INGEST_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_xbrl_ingest.py"
RESTATEMENT_FIXTURE = FIXTURES / "xbrl_restatement_factpack.json"

# INTC FY2020 was a 52-week fiscal year ending 2020-12-26 → it began
# 2019-12-29. Both 10-K vintages report the SAME window, so both facts carry
# the same period_start — this is what lets the store's `same_period` group
# the two vintages into ONE period entry (the restatement †).
_FY2020_PERIOD_START = "2019-12-29"


@pytest.fixture(scope="module")
def ingest_module():
    """Load kpi_xbrl_ingest.py as an importable module for unit tests of its
    pure derivation surface (mirrors test_kpi_store.py's importlib pattern).
    """
    spec = importlib.util.spec_from_file_location("kpi_xbrl_ingest_test", INGEST_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_xbrl_ingest_test"] = module
    spec.loader.exec_module(module)
    return module


def _real_shaped_pack() -> dict:
    """Load the REAL 2-vintage restatement fixture and add the producer's
    `period_start` (Task 1) to every fact — a real-shaped derivative, never a
    hand-typed pack. Values / accessions / dimensions are untouched.
    """
    pack = json.loads(RESTATEMENT_FIXTURE.read_text(encoding="utf-8"))
    for fact in pack["facts"]:
        fact["period_start"] = _FY2020_PERIOD_START
    return pack


def _run_ingest(pack_path, env) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(INGEST_SCRIPT), "ingest", "--pack", str(pack_path)],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def _run_dump(company, env) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "--script", str(KPI_STORE_SCRIPT), "dump", "--company", company],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def test_ingest_appends_each_vintage(tmp_path):
    """The real 2-vintage restatement pack (ONE dimensional signature) ingests
    as TWO store points under ONE kpi_id. `kpi_store dump` groups them into a
    single period entry holding BOTH observations with disagreement=True —
    the non-collapsing path preserves the restatement †. All store writes land
    under the tmp KPI_STORE_DIR; the durable store is never touched.
    """
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    pack_path = tmp_path / "pack.json"
    pack_path.write_text(json.dumps(_real_shaped_pack()), encoding="utf-8")

    result = _run_ingest(pack_path, env)
    assert result.returncode == 0, (
        f"ingest failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )

    # Writes landed ONLY in the tmp store dir (durable store untouched).
    assert store_dir.exists(), "ingest did not write to the tmp KPI_STORE_DIR"
    assert list(store_dir.glob("*.json")), "no series file written to tmp store"

    dump = _run_dump("INTC", env)
    assert dump.returncode == 0, (
        f"dump failed: stdout={dump.stdout!r} stderr={dump.stderr!r}"
    )
    payload = json.loads(dump.stdout)

    assert len(payload["series"]) == 1, (
        f"expected exactly ONE kpi_id, got {[s['kpi_id'] for s in payload['series']]}"
    )
    series = payload["series"][0]
    periods = series["periods"]
    assert len(periods) == 1, (
        f"expected the two vintages to GROUP into one period entry, got {len(periods)}"
    )
    entry = periods[0]
    values = sorted(obs["value"] for obs in entry["observations"])
    assert values == [40057000000.0, 40535000000.0], (
        f"both vintages must survive as observations (no collapse); got {values}"
    )
    assert entry["disagreement"] is True, (
        "two distinct vintages of one period must flag disagreement (the †)"
    )


def _collision_pack() -> dict:
    """SYNTHETIC collision probe — NOT a real filing. Built from the real
    fixture's fact shape (accession/fiscal_calendars untouched), varying
    ONLY the dimension member's namespace prefix (`ns1:` vs `ns2:`) so two
    DISTINCT dimensional signatures collapse to the SAME `derive_kpi_id`
    slug (both strip to local-name `product`). Real us-gaap/srt taxonomies
    never actually collide this way — this fixture exists solely to force
    the fail-loud guard's raise path.
    """
    pack = _real_shaped_pack()
    base = pack["facts"][0]
    fact_a = dict(base)
    fact_a["dimensions"] = {"StatementBusinessSegments": "ns1:ProductMember"}
    fact_a["accession"] = "0000050863-22-000007"
    fact_b = dict(base)
    fact_b["dimensions"] = {"StatementBusinessSegments": "ns2:ProductMember"}
    fact_b["accession"] = "0000050863-23-000006"
    fact_b["value"] = 999.0
    pack["facts"] = [fact_a, fact_b]
    return pack


def test_ingest_raises_on_kpi_id_collision(tmp_path):
    """Two facts with DISTINCT dimensional signatures (`ns1:ProductMember`
    vs `ns2:ProductMember` — different values, so different `_signature_key`
    tuples) whose `derive_kpi_id` slugs COLLAPSE to the same `kpi_id` (both
    strip to `product`) must be rejected loudly — a silent collision would
    merge two DIFFERENT segments' revenues into one store series (a false
    restatement †). Regression (same test, so both directions stay coupled):
    the real 2-vintage SAME-signature pack — where multiple vintages
    legitimately share one kpi_id — must NOT raise; the guard fires only on
    distinct-signature collisions, never on expected vintage grouping.
    """
    store_dir = tmp_path / "store"
    env = {**os.environ, "KPI_STORE_DIR": str(store_dir)}

    collision_path = tmp_path / "collision_pack.json"
    collision_path.write_text(json.dumps(_collision_pack()), encoding="utf-8")
    collision_result = _run_ingest(collision_path, env)
    assert collision_result.returncode != 0, (
        "distinct-signature kpi_id collision must be rejected, not silently "
        f"merged: stdout={collision_result.stdout!r}"
    )
    assert "collision" in collision_result.stderr.lower(), (
        f"rejection must name the collision: stderr={collision_result.stderr!r}"
    )
    assert "product" in collision_result.stderr, (
        f"rejection must name the colliding kpi_id: stderr={collision_result.stderr!r}"
    )

    # Regression: the real SAME-signature 2-vintage pack must NOT trip the
    # guard — vintage grouping under one kpi_id is expected, not a collision.
    vintage_path = tmp_path / "vintage_pack.json"
    vintage_path.write_text(json.dumps(_real_shaped_pack()), encoding="utf-8")
    vintage_result = _run_ingest(vintage_path, env)
    assert vintage_result.returncode == 0, (
        "SAME-signature vintages must still ingest without raising: "
        f"stdout={vintage_result.stdout!r} stderr={vintage_result.stderr!r}"
    )


def test_ingest_kpi_id_derivation(ingest_module):
    """kpi_id is derived deterministically and INJECTIVELY from the FULL
    dimensional signature (concept + sorted breakdown axis:member local-names,
    Member/Axis stripped, lowercased):

      - two DISTINCT signatures → DISTINCT ids (injective);
      - the SAME signature → the SAME id (groups vintages);
      - a signature differing ONLY in srt:ConsolidationItemsAxis → the SAME id
        (it is a reconciliation qualifier, never a breakdown axis — memory
        `match-kpi-on-full-dimensional-signature-not-one-axis`);
      - the id is a readable stripped-member slug, never a human string.
    """
    derive = ingest_module.derive_kpi_id
    concept = "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"

    ccg = derive(concept, {"StatementBusinessSegments": "ClientComputingGroupMember"})
    dcg = derive(concept, {"StatementBusinessSegments": "DataCenterGroupMember"})

    # Distinct signatures → distinct ids (injective).
    assert ccg != dcg

    # Same signature (fresh dict instance) → same id (so vintages group).
    ccg_again = derive(
        concept, {"StatementBusinessSegments": "ClientComputingGroupMember"}
    )
    assert ccg == ccg_again

    # A ConsolidationItems qualifier does NOT change the id — it is a separate
    # reconciliation axis, not a breakdown axis (else every segment filer looks
    # falsely cross-dimensioned).
    ccg_with_consol = derive(
        concept,
        {
            "StatementBusinessSegments": "ClientComputingGroupMember",
            "srt:ConsolidationItemsAxis": "OperatingSegmentsMember",
        },
    )
    assert ccg_with_consol == ccg

    # A readable slug from stripped member local-name(s): the Member suffix is
    # gone, it is lowercased, and it is signature-faithful (not a human name).
    assert "clientcomputinggroup" in ccg
    assert "member" not in ccg
    assert "datacentergroup" in dcg
