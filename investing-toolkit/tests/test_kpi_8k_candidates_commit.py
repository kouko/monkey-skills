"""RED-first tests for the 8-K KPI candidate COMMIT gate (Task 4).

`kpi_8k_candidates.commit` reads a candidates JSON (T3 `propose` output, after a
human/LLM step has filled kpi_id/unit/period and flipped `confirmed: true`) and
appends ONLY human-confirmed, semantically-complete candidates into the tier-①
store via the EXISTING `kpi_store.append(point)`. It NEVER writes an unconfirmed
entry; a confirmed-but-incomplete entry (a null kpi_id/unit/period) or one the
store rejects for missing provenance/as_of is counted refused-incomplete and
written NOWHERE. kpi_store/kpi_validate are left untouched — the refusal of
incomplete points is the trust guarantee, not a loosened check.

No `@req` tag: this dispatch's plan (docs/loom/plans/2026-07-19-8k-earnings-kpi-
intake.md) binds tasks by "Brief item covered", not registered loom-spec
REQ-ids, so there is no id in the living-spec namespace to bind to (same as the
T3 propose test).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
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

# Real NFLX 8-K accession (same provenance as the T2/T3 fixture). The store's
# `as_of` must be DERIVED from this accession's embedded year (2025), never
# wall-clock — the store rejects a wall-clock as_of.
_ACCESSION = "0001065280-25-000033"


def _load_module():
    spec = importlib.util.spec_from_file_location("kpi_8k_candidates_commit", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_8k_candidates_commit"] = module
    spec.loader.exec_module(module)
    return module


def _confirmed_complete_candidate() -> dict:
    """A candidate the human has ratified: `confirmed: true` with every semantic
    slot filled (kpi_id/unit/period), mirroring the T3 propose shape otherwise.
    """
    return {
        "label": ["Global Streaming Paid Memberships"],
        "value": "301.63",
        "period_hint": "Q4'24",
        "source_accession": _ACCESSION,
        "source_table_id": 0,
        "source_cell_ref": {"row": 9, "col": 5},
        "confirmed": True,
        "kpi_id": "paid_memberships",
        "unit": "millions",
        "period": "Q4-2024",
        "needs_semantic": ["kpi_id", "unit", "period"],
    }


def test_unconfirmed_candidates_never_land(tmp_path, monkeypatch):
    """One confirmed+complete entry + one UNCONFIRMED entry commits EXACTLY the
    confirmed one: the store ends with a single point carrying full provenance +
    an accession-derived as_of, and the unconfirmed entry's value (999.99) is
    nowhere in the store.
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    unconfirmed = {
        **_confirmed_complete_candidate(),
        "value": "999.99",
        "confirmed": False,
        "kpi_id": None,
        "unit": None,
        "period": None,
    }
    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(
        json.dumps([_confirmed_complete_candidate(), unconfirmed]),
        encoding="utf-8",
    )

    summary = module.commit(str(candidates_path), company="NFLX")

    assert summary["committed"] == 1
    assert summary["skipped_unconfirmed"] == 1
    assert summary["refused_incomplete"] == 0

    store_files = list(store_dir.rglob("*.json")) if store_dir.exists() else []
    assert len(store_files) == 1, (
        f"expected exactly one store series file, found {store_files}"
    )

    envelope = json.loads(store_files[0].read_text(encoding="utf-8"))
    assert len(envelope["points"]) == 1
    point = envelope["points"][0]

    # EXACTLY the confirmed candidate — never the unconfirmed 999.99.
    assert point["value"] == "301.63"
    assert point["company"] == "NFLX"
    assert point["kpi_id"] == "paid_memberships"
    assert point["unit"] == "millions"
    assert point["period"] == "Q4-2024"
    # Full provenance flows to the store per its required-field contract: the
    # accession + cell ref pass through verbatim; the integer table INDEX 0 is
    # rendered as a truthy `table:0` token (a bare 0 is falsy and the store's
    # provenance guard would mis-read it as "missing" — the store is un-weakened).
    assert point["source_accession"] == _ACCESSION
    assert point["source_table_id"] == "table:0"
    assert point["source_cell_ref"] == {"row": 9, "col": 5}
    # as_of DERIVED from the accession's embedded year (2025), not wall-clock.
    assert point["as_of"].startswith("2025"), point["as_of"]
    assert not point.get("as_of_is_wallclock")


def test_absent_provenance_refused_by_unweakened_store(tmp_path, monkeypatch):
    """The store's OWN un-weakened provenance guard is the third gate: a
    confirmed + semantically-complete candidate whose `source_table_id` is
    genuinely absent (None, not integer 0) must be REFUSED by kpi_store's
    `if not point.get(field)` check — never masked into the store. This guards
    the trust claim that the truthy `table:0` rendering hardens integer-0
    WITHOUT weakening the store for a real None (the confirm gate passes it —
    None is a filled semantic slot's sibling provenance field, not a semantic
    field — so the refusal here can ONLY come from the store itself).
    """
    store_dir = tmp_path / "store"
    monkeypatch.setenv("KPI_STORE_DIR", str(store_dir))
    module = _load_module()

    candidate = {**_confirmed_complete_candidate(), "source_table_id": None}
    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(json.dumps([candidate]), encoding="utf-8")

    summary = module.commit(str(candidates_path), company="NFLX")

    assert summary["committed"] == 0
    assert summary["refused_incomplete"] == 1
    store_files = list(store_dir.rglob("*.json")) if store_dir.exists() else []
    assert store_files == [], (
        f"an absent-provenance point must reach the store's guard and be "
        f"refused, writing nothing; found {store_files}"
    )


def test_missing_unit_refused(tmp_path):
    """A `confirmed: true` candidate whose `unit` was never filled (null) is
    REFUSED as incomplete: the commit CLI exits non-zero with a loud message and
    the store stays empty. The confirm gate never lets an incomplete point land,
    and kpi_store/kpi_validate are not weakened to admit it.
    """
    store_dir = tmp_path / "store"
    env = {
        **os.environ,
        "KPI_STORE_DIR": str(store_dir),
        "PYTHONDONTWRITEBYTECODE": "1",
    }

    candidate = {**_confirmed_complete_candidate(), "unit": None}  # never filled
    candidates_path = tmp_path / "candidates.json"
    candidates_path.write_text(json.dumps([candidate]), encoding="utf-8")

    result = subprocess.run(
        ["uv", "run", "--script", str(_SCRIPT), "commit",
         "--candidates", str(candidates_path), "--company", "NFLX"],
        capture_output=True, text=True, timeout=120, env=env,
    )

    assert result.returncode != 0, (
        f"a confirmed-but-incomplete candidate must exit non-zero; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert result.stderr.strip(), "a refusal must explain itself loudly on stderr"
    assert "unit" in (result.stderr + result.stdout).lower(), (
        "the refusal must name the missing semantic field (unit)"
    )

    store_files = list(store_dir.rglob("*.json")) if store_dir.exists() else []
    assert store_files == [], (
        f"a refused commit must write nothing to the store, found {store_files}"
    )
