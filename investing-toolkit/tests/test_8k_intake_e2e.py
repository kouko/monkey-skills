"""End-to-end offline test for the FULL Route B 8-K KPI intake lane (Task 5).

Chains every seam of Route B for the real NFLX Q4'24 exhibit, proving the
mechanical -> semantic -> confirm -> store roundtrip connects end to end with no
network and no LLM:

  fixture exhibit HTML (T2, committed bytes from NFLX 8-K)
    -> exhibit_tables.py            (data-markets table walker, via subprocess)
    -> kpi_8k_candidates.propose    (T3 mechanical producer -> raw candidates)
    -> [SIMULATED LLM + human step]  the TEST fills kpi_id/unit/period on the
       membership candidate and flips `confirmed: true` (standing in for the
       analysis-kpi SKILL.md LLM layer + human ratification -- there is no LLM
       in the test)
    -> kpi_8k_candidates.commit     (T4 confirm gate -> tier-① store)
    -> ASSERT the stored point       value/unit/period/provenance/as_of.

This is an INTEGRATION test that proves the seams connect; T1-T4 already ship
their units, so it may pass on first write. If it does, that is the correct
outcome for a seam-connection test (see the module note in the SDD report) --
the value it adds is proving the four scripts compose across the
analysis->data-markets subprocess boundary and the confirm->store boundary, not
re-testing a single unit.

No `@req` tag: this dispatch's plan (docs/loom/plans/2026-07-19-8k-earnings-kpi-
intake.md) binds tasks by "Brief item covered", not registered loom-spec
REQ-ids, so there is no id in the living-spec namespace to bind to (same
rationale as the T3 propose + T4 commit tests).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPT = (
    _TESTS_DIR.parent
    / "skills"
    / "analysis-kpi"
    / "scripts"
    / "kpi_8k_candidates.py"
)
_FIXTURE = _TESTS_DIR / "fixtures" / "nflx_q4_2024_ex991.html"

# Real NFLX 8-K accession (same provenance as the T2 fixture bytes). Supplied to
# the producer as filing metadata -- never derived from the HTML. The store's
# `as_of` is derived from this accession's embedded year (2025).
_ACCESSION = "0001065280-25-000033"

# The verbatim filed membership value -- the anti-fabrication anchor. An
# independent expected literal, NOT re-read from producer output, so the value
# assertion compares producer output to a known-good constant (no same-operand
# assertion).
_MEMBERSHIP_VALUE = "301.63"


def _load_module():
    spec = importlib.util.spec_from_file_location("kpi_8k_intake_e2e", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_8k_intake_e2e"] = module
    spec.loader.exec_module(module)
    return module


def test_fixture_exhibit_to_store_roundtrip(tmp_path, monkeypatch):
    """Full Route B lane, offline: propose from the committed fixture, simulate
    the LLM+human confirm step on the membership candidate, commit, then assert
    the stored point carries the verbatim value, the human-filled unit/period,
    full provenance, and an accession-derived as_of.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    # -- 1-3. Fixture HTML -> exhibit_tables.py (subprocess) -> raw candidates.
    candidates = module.propose(str(_FIXTURE), _ACCESSION)

    # The mechanical producer transcribes the filed value verbatim and leaves
    # every semantic slot null (compare producer output to independent literals).
    membership = [c for c in candidates if c["value"] == _MEMBERSHIP_VALUE]
    assert len(membership) == 1, (
        f"expected exactly one raw candidate with the verbatim membership value "
        f"{_MEMBERSHIP_VALUE!r}; got {[c['value'] for c in membership]}"
    )
    candidate = membership[0]
    assert candidate["confirmed"] is False
    assert candidate["kpi_id"] is None
    assert candidate["unit"] is None
    assert candidate["period"] is None

    # -- 4. SIMULATED LLM + human ratification: fill the semantic slots and flip
    # confirmed. This stands in for the SKILL.md LLM layer + human confirm-all
    # gate; the mechanical value + source coordinates are left UNTOUCHED.
    candidate["kpi_id"] = "paid_memberships"
    candidate["unit"] = "millions"
    candidate["period"] = "Q4-2024"
    candidate["confirmed"] = True

    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(json.dumps(candidates), encoding="utf-8")

    # -- 5. Confirm gate -> tier-① store. Every OTHER raw candidate stays
    # unconfirmed and is skipped, so exactly the membership point lands.
    summary = module.commit(str(candidates_path), company="NFLX")

    assert summary["committed"] == 1, summary
    assert summary["refused_incomplete"] == 0, summary
    assert summary["skipped_unconfirmed"] == len(candidates) - 1, summary

    # -- 6. ASSERT the stored point. Exactly one series file, one point.
    store_files = list(store_dir.rglob("*.json")) if store_dir.exists() else []
    assert len(store_files) == 1, (
        f"expected exactly one stored series file, found {store_files}"
    )
    envelope = json.loads(store_files[0].read_text(encoding="utf-8"))
    assert len(envelope["points"]) == 1, envelope
    point = envelope["points"][0]

    # Value transcribed verbatim end to end -- never re-parsed to float.
    assert point["value"] == "301.63"
    assert point["company"] == "NFLX"
    # Human-filled semantic slots survived the confirm->store hop verbatim.
    assert point["kpi_id"] == "paid_memberships"
    assert point["unit"] == "millions"
    assert point["period"] == "Q4-2024"
    # All three provenance fields present + carried through. The integer table
    # index 0 is rendered truthy as `table:0` (a bare 0 is falsy and the store's
    # provenance guard would mis-read it as missing).
    assert point["source_accession"] == "0001065280-25-000033"
    assert point["source_table_id"] == "table:0"
    assert point["source_cell_ref"] == {"row": 9, "col": 5}
    # as_of DERIVED from the accession's embedded year (2025), not wall-clock.
    assert point["as_of"].startswith("2025"), point["as_of"]
    assert not point.get("as_of_is_wallclock")
