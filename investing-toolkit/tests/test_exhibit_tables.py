"""test_exhibit_tables.py — Route B MECHANICAL table extractor (exhibit_tables.py).

Offline unit tests for `exhibit_tables.extract_tables`, the stdlib
`html.parser`-based walker that turns a raw 8-K earnings-exhibit HTML document
into a JSON-serializable list of tables. Each cell carries
`{table_index, row, col, text}` AFTER rowspan/colspan resolution + duplicate-
cell cleanup, and each table carries a per-row label path (the leading label
cells of the row). This is the MECHANICAL layer — coordinates + verbatim values
only, ZERO semantic interpretation (no kpi_id / unit / period; that is T3/T8).

No pandas/lxml: coordinate fidelity across the Workiva colspan/duplicate-cell
artifact (each logical cell rendered as 2-3 `<td>`s — a value + trailing
empty/`%` separators) requires a custom stdlib walker, not a DataFrame reader.

Fixture: tests/fixtures/nflx_q4_2024_ex991.html — REAL verbatim bytes of the
NFLX Q4'24 EX-99.1 summary `<table>` (accession 0001065280-25-000033, verified
live 2026-07-19), only the surrounding letter prose trimmed. Values are NOT
hand-authored — they are the real filed bytes, cross-checked against the live
spike extraction (scratchpad/route-b-inventory-spike.md): "Global Streaming
Paid Memberships" Q4'24 = 301.63. Per
docs/loom/memory/hand-authored-fixture-is-a-fabrication-risk.md, a fabricated
fixture would false-green an anti-fabrication feature — so the fixture is the
filed source, byte-for-byte.

@req: this dispatch's plan (docs/loom/plans/2026-07-19-8k-earnings-kpi-intake.md,
Task 2) traces work by "Brief item covered", NOT registered loom-spec REQ-ids,
so per the implementer contract @req tags are omitted on every test here (see
report). No id is minted to fill the gap. Mirrors sibling test_exhibit_fetch.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "nflx_q4_2024_ex991.html"

if str(MARKETS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MARKETS_SCRIPTS))


def _load_fixture_html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def _find_cells(tables, text):
    """All cells across all tables whose text == text (exact, post-cleanup)."""
    hits = []
    for table in tables:
        for cell in table["cells"]:
            if cell["text"] == text:
                hits.append(cell)
    return hits


def test_nflx_q4_2024_membership_cell_located():
    # No living-spec REQ-id: this plan traces tasks by Brief item, not REQ-ids.
    import exhibit_tables

    html = _load_fixture_html()
    tables = exhibit_tables.extract_tables(html)

    # The walker returns a JSON-serializable list of tables.
    assert isinstance(tables, list) and tables, "expected a non-empty list of tables"

    # 301.63 (the real filed Q4'24 Global Streaming Paid Memberships value) is
    # located at exactly ONE stable coordinate — nbsp/whitespace stripped, the
    # colspan-split + empty separator `<td>`s cleaned away so the value is one cell.
    hits = _find_cells(tables, "301.63")
    assert len(hits) == 1, (
        f"expected exactly one cell with text '301.63', got {len(hits)}: {hits!r}"
    )
    cell = hits[0]

    # Coordinate is a fully-defined integer triple {table_index, row, col}.
    assert isinstance(cell["table_index"], int)
    assert isinstance(cell["row"], int)
    assert isinstance(cell["col"], int)
    coord = (cell["table_index"], cell["row"], cell["col"])

    # STABLE: re-parsing the same bytes yields the identical coordinate
    # (deterministic walker — the coordinate is not run-order dependent).
    tables2 = exhibit_tables.extract_tables(html)
    hits2 = _find_cells(tables2, "301.63")
    assert len(hits2) == 1
    coord2 = (hits2[0]["table_index"], hits2[0]["row"], hits2[0]["col"])
    assert coord == coord2, f"coordinate not stable across parses: {coord} vs {coord2}"

    # That cell's ROW-LABEL PATH contains "Paid Memberships" — the leading label
    # cell of its row is "Global Streaming Paid Memberships".
    table = tables[cell["table_index"]]
    label_path = table["row_label_paths"][cell["row"]]
    assert isinstance(label_path, list)
    joined = " ".join(label_path)
    assert "Paid Memberships" in joined, (
        f"row-label path must contain 'Paid Memberships', got {label_path!r}"
    )

    # MECHANICAL layer: the value is the VERBATIM printed string, not a float —
    # no normalization/rounding that would drop filed precision.
    assert cell["text"] == "301.63"
    assert not isinstance(cell["text"], float)


def test_value_cell_has_no_semantic_fields():
    # No living-spec REQ-id: this plan traces tasks by Brief item, not REQ-ids.
    # Guard the layer boundary: the mechanical walker emits coordinates + text
    # ONLY. It must NOT invent kpi_id / unit / period (that is the T3/T8 semantic
    # layer). A cell dict carries exactly the four mechanical keys.
    import exhibit_tables

    tables = exhibit_tables.extract_tables(_load_fixture_html())
    cell = _find_cells(tables, "301.63")[0]
    assert set(cell) == {"table_index", "row", "col", "text"}, (
        f"cell must carry only mechanical keys, got {sorted(cell)}"
    )
