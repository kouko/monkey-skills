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


def test_membership_candidate_carries_unit_hint():
    module = _load_module()

    candidates = module.propose(str(_FIXTURE), _ACCESSION)

    membership = [c for c in candidates if c["value"] == "301.63"]
    assert len(membership) == 1
    candidate = membership[0]

    # ADVISORY unit_hint: the table-level caption copied VERBATIM (parallel to
    # period_hint). It is a source SIGNAL for the LLM's `unit` proposal, NOT a
    # mechanically-stamped unit — the caption does not apply per-row (Revenue =
    # $millions, this membership row = millions-of-count).
    assert candidate["unit_hint"] == "(in millions except per share data)"

    # unit_hint does NOT change the trust model: `unit` stays the LLM-filled
    # semantic slot (null here), and unit_hint is NOT one of needs_semantic.
    assert candidate["unit"] is None
    assert candidate["needs_semantic"] == ["kpi_id", "unit", "period"]
    assert "unit_hint" not in candidate["needs_semantic"]


def test_unit_caption_matches_common_sec_prefixes_but_not_footnotes():
    """The caption matcher covers the common SEC prefixed shapes, not just the
    bare `(in millions)` — while still rejecting footnote markers and prose."""
    module = _load_module()
    find = module._find_unit_caption

    def cap(text):  # one-cell table
        return find([{"row": 0, "col": 0, "text": text}])

    # Common SEC caption prefixes — all SHOULD surface as the verbatim hint.
    assert cap("(in millions except per share data)") == "(in millions except per share data)"
    assert cap("(Dollars in millions)") == "(Dollars in millions)"
    assert cap("(Amounts in thousands)") == "(Amounts in thousands)"
    assert cap("(U.S. dollars in millions)") == "(U.S. dollars in millions)"
    assert cap("$ in millions") == "$ in millions"
    # Must NOT match: a footnote marker, or "in millions" mid-prose with no anchor.
    assert cap("(1) revenues later restated") is None
    assert cap("results are presented in millions of dollars") is None
