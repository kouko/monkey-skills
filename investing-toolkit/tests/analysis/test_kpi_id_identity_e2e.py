"""End-to-end test for the injective kpi_id identity arc (plan
docs/loom/plans/2026-07-25-kpi-id-injective-identity.md Task 4): both
measured collision shapes, plus the untouched flat top-line lane, ingest
correctly from ONE `ingest_pack` call over ONE fact-pack.

Tasks 1-3's unit/CLI tests already prove each derivation rule in isolation
(`test_kpi_xbrl_ingest.py`'s `test_derive_kpi_id_discriminates_non_default_
consolidation`, `test_derive_kpi_id_folds_case_and_stays_injective`,
`test_ingest_folds_case_variant_selectors_into_one_series`). This file's
value is the ROUND TRIP those unit tests cannot see: one pack, one
`ingest_pack` call, carrying BOTH shapes at once plus a flat fact, driven
through the real seam `ingest_pack` -> selector grouping -> `facts_to_points`
-> `kpi_store.append` -> a read back off disk.

Fixture: `fixtures/xbrl_kpi_id_identity_factpack.json` — SYNTHETIC (see its
own `_comment`), shaped to mirror the real producer's emitted fields
(mirrors `xbrl_consolidation_variant_factpack.json`'s real field-set), with
member names read off the committed live probe
(`tests/data/fixtures/kpi_id_identity_probe_2026-07-25.json`
`_summary.consolidation_member_domain`: `OperatingSegmentsMember` is the
default, `IntersegmentEliminationMember` is a genuinely observed non-default
member) — never a hand-invented member name.
"""
from __future__ import annotations

import importlib.util
import json
import sys

import pytest

from conftest import FIXTURES, SKILLS

INGEST_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_xbrl_ingest.py"
IDENTITY_FIXTURE = FIXTURES / "xbrl_kpi_id_identity_factpack.json"


@pytest.fixture(scope="module")
def ingest_module():
    """Load kpi_xbrl_ingest.py as an importable module (mirrors
    test_kpi_xbrl_ingest.py's `ingest_module` fixture) so `ingest_pack` is
    called directly — ONE Python call, no CLI subprocess and no chain logic
    re-implemented here.
    """
    spec = importlib.util.spec_from_file_location(
        "kpi_xbrl_ingest_identity_e2e", INGEST_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_xbrl_ingest_identity_e2e"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    """Point `kpi_store` at a per-test tmp dir via `KPI_STORE_DIR` — the
    durable ~/.local/share store is never touched.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    return store_dir


def _identity_pack() -> dict:
    return json.loads(IDENTITY_FIXTURE.read_text(encoding="utf-8"))


def _stored_points(store_dir) -> list[dict]:
    """Every point durably written under `store_dir`, read straight off disk
    (mirrors test_kpi_xbrl_ingest.py's `_stored_points`)."""
    if not store_dir.exists():
        return []
    points: list[dict] = []
    for path in sorted(store_dir.glob("*.json")):
        points.extend(json.loads(path.read_text(encoding="utf-8"))["points"])
    return points


def test_consolidation_splits_and_case_folds_in_one_ingest(
    ingest_module, isolated_store,
):
    """ONE `ingest_pack` call over a pack carrying all three shapes:

    (a) the consolidation-split signature (`UpstreamMember` under
        `OperatingSegmentsMember` and `IntersegmentEliminationMember`, same
        filing) must land as TWO series — Task 1's non-default-member token.
    (b) the case-drift signature (`DataCenterMember` 10-Q / `DatacenterMember`
        10-K) must land as ONE series holding BOTH its quarterly (3mo) and its
        annual (12mo-FY) point — Task 2's case-folded digest + Task 3's
        case-insensitive claim relaxation.
    (c) the flat fact must still land under the literal `total_revenue` id,
        untouched by this arc — no digest suffix.

    LENGTH-CEILING EXCEPTION (`standards/naming-and-functions.md` 50-line
    limit): this body deliberately runs long because COEXISTENCE is the
    property under test. Splitting (a)/(b)/(c) into three tests would give
    three passing tests that never prove the three rules hold in ONE
    `ingest_pack` run over ONE pack — which is the only thing the unit tests
    in `test_kpi_xbrl_ingest.py` cannot already show.
    """
    pack = _identity_pack()

    result = ingest_module.ingest_pack(pack)

    assert result["appended"] == len(pack["facts"]), (
        f"every fact must be appended exactly once (no drop, no double-emit): "
        f"{result['appended']} appended for {len(pack['facts'])} facts"
    )

    stored = _stored_points(isolated_store)
    by_kpi: dict[str, list[dict]] = {}
    for point in stored:
        by_kpi.setdefault(point["kpi_id"], []).append(point)

    # --- (a) consolidation split: TWO series, one point each -----------
    upstream_series = {
        kpi_id: points
        for kpi_id, points in by_kpi.items()
        if kpi_id.startswith("revenues__statementbusinesssegments-upstream")
    }
    assert len(upstream_series) == 2, (
        f"the two ConsolidationItemsAxis members must mint TWO series; got "
        f"{sorted(upstream_series)}"
    )
    assert all(len(points) == 1 for points in upstream_series.values()), (
        f"each consolidation-split series holds exactly its own one fact; "
        f"got {upstream_series}"
    )
    upstream_values = sorted(
        points[0]["value"] for points in upstream_series.values()
    )
    assert upstream_values == sorted(
        fact["value"] for fact in pack["facts"]
        if fact["dimensions"] == {"StatementBusinessSegments": "UpstreamMember"}
    ), f"both consolidation views' values must survive; got {upstream_values}"
    # Exactly ONE of the two ids carries the non-default member's own token
    # (Task 1) — the other is the untouched default-view id, so the split is
    # discrimination, not a coincidental digest collision.
    non_default_ids = [
        kpi_id for kpi_id in upstream_series if "intersegmentelimination" in kpi_id
    ]
    assert len(non_default_ids) == 1, (
        f"exactly one id must carry the non-default member's token; got "
        f"{sorted(upstream_series)}"
    )

    # --- (b) case drift: ONE series, holding BOTH a quarterly AND an ----
    # --- annual point -----------------------------------------------------
    datacenter_series = {
        kpi_id: points
        for kpi_id, points in by_kpi.items()
        if "datacenter" in kpi_id
    }
    assert len(datacenter_series) == 1, (
        f"both spellings must fold into ONE series; got {sorted(datacenter_series)}"
    )
    (datacenter_kpi_id, datacenter_points), = datacenter_series.items()
    assert len(datacenter_points) == 2, (
        f"the shared series must hold both vintages (one per spelling); got "
        f"{datacenter_points}"
    )
    duration_classes = sorted(p["duration_class"] for p in datacenter_points)
    assert duration_classes == ["12mo-FY", "3mo"], (
        f"the shared series must carry BOTH the quarterly (3mo) and the "
        f"annual (12mo-FY) point; got {duration_classes}"
    )
    datacenter_values = sorted(p["value"] for p in datacenter_points)
    assert datacenter_values == sorted(
        fact["value"] for fact in pack["facts"]
        if fact["dimensions"].get("StatementBusinessSegments", "").lower()
        == "datacenter" + "member"
    ), f"both spellings' values must survive; got {datacenter_values}"

    # --- (c) flat fact: still the literal `total_revenue` id, no digest -
    assert "total_revenue" in by_kpi, (
        f"the flat fact must land under the literal total_revenue id; got "
        f"{sorted(by_kpi)}"
    )
    assert len(by_kpi["total_revenue"]) == 1, by_kpi["total_revenue"]
    flat_fact = next(f for f in pack["facts"] if f["dimensions"] == {})
    assert by_kpi["total_revenue"][0]["value"] == flat_fact["value"], (
        by_kpi["total_revenue"][0]
    )

    # Every kpi_id observed, for the report — no accidental fourth series.
    assert len(by_kpi) == 4, f"expected exactly 4 series; got {sorted(by_kpi)}"
