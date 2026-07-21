#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
exhibit_tables.py — investing-toolkit Route B MECHANICAL table extractor.

Turns a raw 8-K earnings-exhibit HTML document (e.g. a Netflix / Workiva-
generated EX-99.1 shareholder letter) into a JSON-serializable list of tables.
Each cell carries {table_index, row, col, text} AFTER rowspan/colspan
resolution + duplicate-cell cleanup, and each table carries a per-row label
path (the leading label cells of the row). Pure stdlib `html.parser` — NO
pandas/lxml: coordinate fidelity across the Workiva colspan/duplicate-cell
artifact (each logical cell rendered as 2-3 `<td>`s — a value plus trailing
empty/separator cells) requires a custom walker, not a DataFrame reader.

This is the MECHANICAL layer: values + coordinates + verbatim row labels ONLY.
It performs ZERO semantic interpretation — no kpi_id, no unit, no normalized
period. Values are the exact printed strings (nbsp/whitespace stripped, never
parsed to float) so the filed precision is preserved for the downstream
anti-fabrication confirm gate.

Usage:
  uv run exhibit_tables.py --html path/to/ex991.htm --out tables.json

Output (tables.json): a JSON list of table objects:
  [
    {
      "table_index": 0,
      "n_rows": 18,
      "cells": [{"table_index": 0, "row": 2, "col": 5, "text": "301.63"}, ...],
      "row_label_paths": [["..."], ["Global Streaming Paid Memberships"], ...]
    },
    ...
  ]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

_CELL_TAGS = ("td", "th")

# A cell whose cleaned text looks like a printed number ($, digits, commas, a
# decimal, %, parentheses for negatives). Used only to find where a row's
# leading LABEL cells end — never to reinterpret the value itself.
_NUMERIC_RE = re.compile(r"^[\$\(]?[-+]?[\d,]*\.?\d+%?\)?$")


def _normalize(text: str) -> str:
    """Strip nbsp (\\xa0, from `&#160;`) + surrounding whitespace and collapse
    internal runs of whitespace to a single space. `convert_charrefs` (default
    True on HTMLParser) has already decoded char refs into unicode."""
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def _is_numeric(text: str) -> bool:
    return bool(_NUMERIC_RE.match(text))


class _TableWalker(HTMLParser):
    """Collect every `<table>` in document order as a list of rows; each row is
    a list of raw cells `{"text", "colspan", "rowspan"}`. Handles nested tables
    via a stack so an inner table's cells never leak into the outer table."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        # tables: list of {"rows": [...]} in `<table>` document (open) order.
        self.tables: list[dict] = []
        # Stack of table indices currently open (supports nesting).
        self._open_tables: list[int] = []
        self._cur_row: list[dict] | None = None
        self._cur_cell: dict | None = None
        self._cell_text: list[str] = []

    # -- tag dispatch -----------------------------------------------------
    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables.append({"rows": []})
            self._open_tables.append(len(self.tables) - 1)
        elif tag == "tr" and self._open_tables:
            self._cur_row = []
        elif tag in _CELL_TAGS and self._cur_row is not None:
            # A new cell closes any unterminated previous one (defensive).
            if self._cur_cell is not None:
                self._end_cell()
            a = dict(attrs)
            self._cur_cell = {
                "colspan": _span(a.get("colspan")),
                "rowspan": _span(a.get("rowspan")),
            }
            self._cell_text = []

    def handle_data(self, data):
        if self._cur_cell is not None:
            self._cell_text.append(data)

    def handle_endtag(self, tag):
        if tag in _CELL_TAGS:
            self._end_cell()
        elif tag == "tr":
            if self._cur_cell is not None:  # unterminated cell defensive close
                self._end_cell()
            if self._cur_row is not None and self._open_tables:
                self.tables[self._open_tables[-1]]["rows"].append(self._cur_row)
            self._cur_row = None
        elif tag == "table" and self._open_tables:
            self._open_tables.pop()

    # -- helpers ----------------------------------------------------------
    def _end_cell(self):
        if self._cur_cell is None:
            return
        self._cur_cell["text"] = _normalize("".join(self._cell_text))
        if self._cur_row is not None:
            self._cur_row.append(self._cur_cell)
        self._cur_cell = None
        self._cell_text = []


_MAX_SPAN = 1000  # HTML spec caps colspan at 1000; guards untrusted-HTML DoS


def _span(value) -> int:
    """Parse a colspan/rowspan attribute; default 1, floor 1 on garbage,
    ceiling _MAX_SPAN so a crafted huge span can't blow up the grid."""
    try:
        n = int(str(value).strip())
    except (TypeError, ValueError):
        return 1
    return min(max(n, 1), _MAX_SPAN)


def _anchor_cells(rows: list[list[dict]]) -> list[tuple[int, int, str]]:
    """Place each logical cell onto the HTML table grid honoring colspan +
    rowspan, returning (grid_row, grid_col_start, text) anchors. Rowspans
    reserve cells in later rows so those rows' cells shift right correctly —
    this is the 'rowspan/colspan resolution' that keeps column coordinates
    faithful to the rendered grid."""
    occupied: set[tuple[int, int]] = set()
    anchors: list[tuple[int, int, str]] = []
    for r, row in enumerate(rows):
        c = 0
        for cell in row:
            while (r, c) in occupied:
                c += 1
            cs, rs = cell["colspan"], cell["rowspan"]
            anchors.append((r, c, cell["text"]))
            for dr in range(rs):
                for dc in range(cs):
                    occupied.add((r + dr, c + dc))
            c += cs
    return anchors


def _build_table(table_index: int, rows: list[list[dict]]) -> dict:
    """Grid-resolve one table, then clean duplicate/empty cells into stable
    per-row logical coordinates and derive each row's leading-label path."""
    anchors = _anchor_cells(rows)
    by_row: dict[int, list[tuple[int, str]]] = {}
    for r, c, text in anchors:
        by_row.setdefault(r, []).append((c, text))

    cells: list[dict] = []
    row_label_paths: list[list[str]] = []
    n_rows = (max(by_row) + 1) if by_row else 0
    for r in range(n_rows):
        ordered = sorted(by_row.get(r, []), key=lambda x: x[0])
        # Duplicate-cell cleanup: drop EMPTY separator `<td>`s so each surviving
        # logical value/label gets a stable sequential column index. Note a lone
        # `$` cell survives as its own column (it is non-empty) — the semantic
        # layer, not this mechanical walker, is where `$`/label association lives.
        nonempty = [text for _, text in ordered if text]
        labels: list[str] = []
        collecting_labels = True
        for col, text in enumerate(nonempty):
            cells.append(
                {"table_index": table_index, "row": r, "col": col, "text": text}
            )
            if collecting_labels:
                if _is_numeric(text):
                    collecting_labels = False
                else:
                    labels.append(text)
        row_label_paths.append(labels)

    return {
        "table_index": table_index,
        "n_rows": n_rows,
        "cells": cells,
        "row_label_paths": row_label_paths,
    }


def extract_tables(html: str) -> list[dict]:
    """Parse raw exhibit HTML → list of table objects (see module docstring).

    Deterministic: tables are indexed in `<table>` document order and every
    coordinate derives only from the input bytes, so re-parsing the same HTML
    yields identical coordinates."""
    walker = _TableWalker()
    walker.feed(html)
    walker.close()
    return [_build_table(i, t["rows"]) for i, t in enumerate(walker.tables)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract tables (coordinates + verbatim cells) from raw "
        "8-K exhibit HTML — mechanical layer, no semantic interpretation."
    )
    parser.add_argument("--html", required=True, help="Path to raw exhibit HTML")
    parser.add_argument("--out", required=True, help="Path to write tables JSON")
    args = parser.parse_args(argv)

    html = Path(args.html).read_text(encoding="utf-8")
    tables = extract_tables(html)
    Path(args.out).write_text(
        json.dumps(tables, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"extracted {len(tables)} table(s), "
        f"{sum(len(t['cells']) for t in tables)} cell(s) -> {args.out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
