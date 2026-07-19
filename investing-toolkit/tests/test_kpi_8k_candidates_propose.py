"""RED-first test for the mechanical 8-K KPI candidate producer (Task 3).

`kpi_8k_candidates.propose` consumes the committed NFLX Q4'24 exhibit fixture
through `exhibit_tables.py` (the data-markets table walker, called via
SUBPROCESS — the analysis->data-markets layer boundary is crossed by process,
never by import) and emits RAW candidate points. This test pins the mechanical
contract: the value string and source coordinates are transcribed verbatim from
the producer output, and the SEMANTIC fields (kpi_id / unit / period) are left
explicitly null with a `needs_semantic` list — the mechanical layer NEVER
guesses a unit ("millions") or a slug.

No `@req` tag: this dispatch's plan (docs/loom/plans/2026-07-19-8k-earnings-kpi-
intake.md) binds tasks by "Brief item covered", not by registered loom-spec
REQ-ids, so there is no id in the living-spec namespace to bind to.
"""
from __future__ import annotations

import importlib.util
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

# Provenance: the T2 fixture is trimmed real bytes from NFLX 8-K accession
# 0001065280-25-000033 (verified live 2026-07-19). The accession is filing
# metadata supplied to the producer, not derived from the HTML.
_ACCESSION = "0001065280-25-000033"


def _load_module():
    spec = importlib.util.spec_from_file_location("kpi_8k_candidates", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_nflx_membership_raw_candidate_emitted():
    module = _load_module()

    candidates = module.propose(str(_FIXTURE), _ACCESSION)

    membership = [c for c in candidates if c["value"] == "301.63"]
    assert len(membership) == 1, (
        "exactly one candidate should carry the verbatim membership value 301.63"
    )
    candidate = membership[0]

    # Verbatim row-label path, straight from exhibit_tables row_label_paths.
    assert candidate["label"] == ["Global Streaming Paid Memberships"]
    # Exact printed string — never parsed to float, never normalized.
    assert candidate["value"] == "301.63"
    # Verbatim column-header text (a HINT, not a normalized period).
    assert candidate["period_hint"] == "Q4'24"

    # Source coordinates: accession from metadata + producer table/cell ref.
    assert candidate["source_accession"] == "0001065280-25-000033"
    assert candidate["source_table_id"] == 0
    assert candidate["source_cell_ref"] == {"row": 9, "col": 5}

    # Mechanical layer: unconfirmed, and every SEMANTIC slot left null for the
    # LLM layer (T8) + human ratification — no guessed unit/slug/period.
    assert candidate["confirmed"] is False
    assert candidate["kpi_id"] is None
    assert candidate["unit"] is None
    assert candidate["period"] is None
    assert candidate["needs_semantic"] == ["kpi_id", "unit", "period"]
