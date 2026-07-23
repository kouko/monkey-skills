"""Producer <-> consumer integration test (tearsheet plan, Task 8).

Closes the pin<->reality seam: Tasks 3-5's `tearsheet_format.py` was built
against fixtures HAND-TRANSCRIBED from the plan's pinned dump schema
(docs/loom/plans/2026-07-23-kpi-tearsheet.md ## Notes); Task 2's
`kpi_store.py dump --company` independently implements that same pin. This
test is the only one in the suite that crosses BOTH subprocess boundaries in
one chain -- real `append` CLI calls build a store on disk, a real `dump`
CLI call reads it back, and the ACTUAL dump bytes (not a fixture) are piped
into a real `tearsheet_format.py` CLI call. If the two producers' pin
transcriptions ever drift from each other, this is the test that fails --
the per-module tests (test_kpi_store_read_cli.py, test_tearsheet_format.py)
cannot catch it because each only ever sees its own hand-built fixtures.

No @req tag: this dispatch's plan (docs/loom/plans/2026-07-23-kpi-
tearsheet.md) binds tasks by "Brief item covered", not registered loom-spec
REQ-ids, so there is no id in the living-spec namespace to bind to (same
convention as test_kpi_store_read_cli.py / test_tearsheet_format.py).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_ROOT = _TESTS_DIR.parent
KPI_STORE_SCRIPT = (
    _ROOT / "skills" / "analysis-kpi" / "scripts" / "kpi_store.py"
)
TEARSHEET_SCRIPT = (
    _ROOT / "skills" / "report-kpi-tearsheet" / "scripts" / "tearsheet_format.py"
)

# A real accession so the store's accession-derived as_of guard passes; the
# store rejects a wall-clock or absent as_of (same convention as
# test_kpi_store_read_cli.py).
_ACCESSION = "0001065280-25-000033"


def _append_via_cli(point: dict, env: dict) -> None:
    result = subprocess.run(
        ["uv", "run", "--script", str(KPI_STORE_SCRIPT), "append"],
        input=json.dumps(point),
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    assert result.returncode == 0, (
        f"append fixture setup failed: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )


def test_store_to_tearsheet_end_to_end(tmp_path):
    """J&J shape: two vintages of one period (FY2021 restated, different
    canonical values -> disagreement) + one other-period point (FY2022),
    appended via the REAL `append` CLI; `dump --company` reads them back via
    a REAL subprocess; the ACTUAL dump stdout (not a hand-built fixture) is
    fed to `tearsheet_format.py --in <file> --as-of <date>` via a REAL
    subprocess. Asserts the rendered Markdown carries the disagreement "dagger"
    (U+2020) marker plus both vintages in ## Revisions -- proving the two
    producers' independent pin transcriptions agree end-to-end.
    """
    env = {
        **os.environ,
        "KPI_STORE_DIR": str(tmp_path),
        # Explicit so a standalone run (outside the wrapper command) cannot
        # write __pycache__ into skill dirs (kpi_store.py imports _store_fs).
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    first_filing = {
        "company": "JNJ",
        "kpi_id": "revenue",
        "period": "FY2021",
        "as_of": "2022-02-15",
        "value": "93,775",
        "scale": 1_000_000,
        "source_accession": _ACCESSION,
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
        "period_start": "2021-01-01",
        "period_end": "2021-12-31",
        "period_kind": "duration",
    }
    restated = {
        "company": "JNJ",
        "kpi_id": "revenue",
        "period": "2021 comparative",
        "as_of": "2024-02-20",
        "value": 78740000000,
        "scale": 1,
        "source_accession": "0001065280-24-000099",
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
        "period_start": "2021-01-01",
        "period_end": "2021-12-31",
        "period_kind": "duration",
    }
    other_period = {
        "company": "JNJ",
        "kpi_id": "revenue",
        "period": "FY2022",
        "as_of": "2023-02-15",
        "value": 94943000000,
        "scale": 1,
        "source_accession": "0001065280-23-000042",
        "source_table_id": "table:0",
        "source_cell_ref": {"row": 1, "col": 1},
        "period_start": "2022-01-01",
        "period_end": "2022-12-31",
        "period_kind": "duration",
    }
    for point in (first_filing, restated, other_period):
        _append_via_cli(point, env)

    dump_result = subprocess.run(
        ["uv", "run", "--script", str(KPI_STORE_SCRIPT), "dump", "--company", "JNJ"],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    assert dump_result.returncode == 0, (
        f"dump failed: stdout={dump_result.stdout!r} stderr={dump_result.stderr!r}"
    )

    dump_path = tmp_path / "jnj-kpi-dump.json"
    dump_path.write_text(dump_result.stdout, encoding="utf-8")

    render_result = subprocess.run(
        [
            sys.executable, str(TEARSHEET_SCRIPT),
            "--in", str(dump_path),
            "--as-of", "2026-07-24",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    assert render_result.returncode == 0, render_result.stderr.decode(
        "utf-8", errors="replace"
    )
    out = render_result.stdout.decode("utf-8")

    # Disagreement marker on the FY2021 cell (latest vintage's canonical
    # value -- max as_of is the 2024-02-20 restatement, 78,740,000,000).
    assert "78,740,000,000†" in out, out
    # The non-disagreement FY2022 cell must NOT carry the marker.
    assert "94,943,000,000" in out and "94,943,000,000†" not in out

    assert "## Revisions" in out
    revisions_block = out[out.index("## Revisions"):]
    # Column header = shortest label for the merged period identity:
    # "FY2021" (6 chars) beats "2021 comparative" (17 chars).
    assert "### revenue — FY2021" in revisions_block
    assert "93,775,000,000 — recorded 2022-02-15 — " + _ACCESSION in revisions_block
    assert (
        "78,740,000,000 — recorded 2024-02-20 — 0001065280-24-000099"
        in revisions_block
    )
