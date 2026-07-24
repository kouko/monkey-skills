"""Whole-seam probe: real dimensional fact-pack -> `kpi_xbrl_ingest.py ingest`
-> `kpi_store.py dump` -> `tearsheet_format.py` render (plan tasks T1-T3 are
already shipped; this is the cross-module behavioral probe per
docs/loom/memory/cross-module-field-contracts-execute-probes.md).

`tests/test_tearsheet_integration.py::test_store_to_tearsheet_end_to_end`
already crosses the store<->tearsheet seam, but it hand-builds `append`
points directly -- it never exercises `kpi_xbrl_ingest.py`/`kpi_xbrl.py`, so
a field-contract drift between the data-markets fact shape and the store's
point shape (the layer THIS module's `facts_to_points`/`derive_kpi_id`
bridges) would slip past it silently. This test closes that gap: it drives
the SAME real 2-vintage INTC restatement fact-pack `test_kpi_xbrl_ingest.py`
uses, through the full chain, and asserts the rendered Markdown carries the
disagreement dagger (U+2020) plus both vintages in `## Revisions`.

All store writes land in an isolated tmp `KPI_STORE_DIR`; the durable store
is never touched. Read-only on tearsheet_format.py and kpi_store.py -- no
production code changes in this task.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from conftest import FIXTURES, KPI_STORE_SCRIPT, SKILLS

INGEST_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_xbrl_ingest.py"
TEARSHEET_SCRIPT = SKILLS / "report-kpi-tearsheet" / "scripts" / "tearsheet_format.py"
RESTATEMENT_FIXTURE = FIXTURES / "xbrl_restatement_factpack.json"

# INTC FY2020 was a 52-week fiscal year ending 2020-12-26 -> it began
# 2019-12-29. Both 10-K vintages report the SAME window, so both facts carry
# the same period_start -- this is what lets the store's `same_period` group
# the two vintages into ONE period entry (the restatement dagger). Mirrors
# test_kpi_xbrl_ingest.py's `_real_shaped_pack` augmentation exactly.
_FY2020_PERIOD_START = "2019-12-29"


def _real_shaped_pack() -> dict:
    """Load the REAL 2-vintage restatement fixture (never hand-typed) and add
    the producer's `period_start` (Task 1) to every fact -- a real-shaped
    derivative, values/accessions/dimensions untouched.
    """
    pack = json.loads(RESTATEMENT_FIXTURE.read_text(encoding="utf-8"))
    for fact in pack["facts"]:
        fact["period_start"] = _FY2020_PERIOD_START
    return pack


def test_xbrl_to_tearsheet_e2e_restatement(tmp_path):
    """Real fact-pack -> `ingest` -> `dump` -> `tearsheet_format` renders the
    restated period's cell with a trailing dagger and a `## Revisions` block
    listing BOTH vintages (value + as_of + accession), end-to-end through the
    shipped CLIs -- no chain logic re-implemented in the test.
    """
    store_dir = tmp_path / "store"
    env = {
        **os.environ,
        "KPI_STORE_DIR": str(store_dir),
        # Explicit so a standalone run cannot write __pycache__ into skill
        # dirs (kpi_store.py / kpi_xbrl_ingest.py import same-dir modules).
        "PYTHONDONTWRITEBYTECODE": "1",
    }

    pack_path = tmp_path / "pack.json"
    pack_path.write_text(json.dumps(_real_shaped_pack()), encoding="utf-8")

    ingest_result = subprocess.run(
        ["uv", "run", "--script", str(INGEST_SCRIPT), "ingest", "--pack", str(pack_path)],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    assert ingest_result.returncode == 0, (
        f"ingest failed: stdout={ingest_result.stdout!r} stderr={ingest_result.stderr!r}"
    )
    ingest_summary = json.loads(ingest_result.stdout)
    assert ingest_summary["appended"] == 2, (
        f"expected both vintages appended as store points, got {ingest_summary}"
    )
    assert len(ingest_summary["kpi_ids"]) == 1, (
        f"the two vintages share ONE dimensional signature -> ONE kpi_id, "
        f"got {ingest_summary['kpi_ids']}"
    )
    kpi_id = ingest_summary["kpi_ids"][0]

    # Writes landed ONLY in the tmp store dir -- the durable store is never
    # touched (KPI_STORE_DIR is the only store-dir override honored).
    assert store_dir.exists(), "ingest did not write to the tmp KPI_STORE_DIR"
    assert list(store_dir.glob("*.json")), "no series file written to tmp store"

    dump_result = subprocess.run(
        ["uv", "run", "--script", str(KPI_STORE_SCRIPT), "dump", "--company", "INTC"],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    assert dump_result.returncode == 0, (
        f"dump failed: stdout={dump_result.stdout!r} stderr={dump_result.stderr!r}"
    )

    dump_path = tmp_path / "intc-kpi-dump.json"
    dump_path.write_text(dump_result.stdout, encoding="utf-8")

    render_result = subprocess.run(
        [
            sys.executable, str(TEARSHEET_SCRIPT),
            "--in", str(dump_path),
            "--as-of", "2023-06-01",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert render_result.returncode == 0, render_result.stderr
    out = render_result.stdout

    # The rendered row is keyed by the SAME kpi_id the ingest chain derived.
    assert kpi_id in out, out

    # Disagreement marker on the restated cell -- latest vintage (max as_of
    # is the 2023-01-27 filing) is 40,535,000,000; the earlier 40,057,000,000
    # vintage must NOT itself carry the marker (only the cell's latest value
    # does).
    assert "40,535,000,000†" in out, out
    assert "40,057,000,000†" not in out

    assert "## Revisions" in out, out
    revisions_block = out[out.index("## Revisions"):]
    assert (
        "40,057,000,000 — recorded 2022-01-27 — 0000050863-22-000007"
        in revisions_block
    ), revisions_block
    assert (
        "40,535,000,000 — recorded 2023-01-27 — 0000050863-23-000006"
        in revisions_block
    ), revisions_block
