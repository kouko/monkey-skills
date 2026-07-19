#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
kpi_8k_candidates.py — investing-toolkit Route B MECHANICAL candidate producer.

Turns a raw 8-K earnings-exhibit HTML document into RAW KPI candidate points and
writes them to a candidates JSON file. It is the layer BELOW the LLM: it emits
the exact printed value + source coordinates + verbatim labels ONLY, and it
NEVER invents a `kpi_id`, a `unit` ("millions"), or a normalized `period` — those
SEMANTIC slots are emitted as explicit `null` with a `needs_semantic` list, to be
filled by the LLM layer (analysis-kpi SKILL.md workflow) and then ratified by the
human confirm-all gate. Values + coordinates never pass through an LLM.

Producer seam (layer boundary):
  The exhibit HTML is machine-parsed by data-markets `exhibit_tables.py`, invoked
  by SUBPROCESS (`uv run exhibit_tables.py --html ... --out ...`), NOT imported —
  analysis-* skills reach data-markets by process, never across the skill boundary
  (see docs/loom/memory/durable-store-mirrors-cache-util-not-imports-it.md; same
  subprocess convention as analysis-comps/scripts/etf_aggregator.py -> pack.py).

Candidate shape -> kpi_schema.propose() contract mapping (transcribed from
kpi_schema.py BEHAVIOR, not its comments): kpi_schema.propose stores each kpi_def
as `{kpi_id, label, unit, locate_hint}` verbatim, where kpi_id/unit are the
LLM-produced-upstream slots and label/locate_hint are the mechanical descriptors.
This module emits exactly those halves separated by provenance:
  - `label` (verbatim row-label path)      -> kpi_schema `label`      (mechanical)
  - `source_*` coordinates                 -> kpi_schema `locate_hint` (mechanical)
  - `kpi_id`, `unit`                       -> kpi_schema `kpi_id`/`unit` (null here;
                                              the LLM fills them before confirm)
`period`/`period_hint` have no kpi_schema slot — they carry the reporting period
through to the tier-1 store's `period` field at commit time (Task 4).

Usage:
  uv run kpi_8k_candidates.py propose --html ex991.htm \\
      --accession 0001065280-25-000033 --out candidates.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
# analysis-kpi/scripts -> analysis-kpi -> skills -> data-markets/scripts.
_EXHIBIT_TABLES = (
    _SCRIPT_DIR.parent.parent / "data-markets" / "scripts" / "exhibit_tables.py"
)

# Explicit list so a downstream reader knows exactly which slots the LLM layer
# must fill before the human confirm-all gate will let the point commit.
_SEMANTIC_FIELDS = ["kpi_id", "unit", "period"]


def run_exhibit_tables(html_path: str) -> list[dict]:
    """Subprocess data-markets `exhibit_tables.py` on `html_path`, returning its
    parsed table list. SUBPROCESS not import: the analysis->data-markets layer
    boundary is crossed by process (mirrors etf_aggregator.py -> pack.py). The
    producer writes JSON to a `--out` file (its only output mode), so we hand it
    a temp path and read it back.
    """
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "tables.json"
        proc = subprocess.run(
            ["uv", "run", str(_EXHIBIT_TABLES),
             "--html", str(html_path), "--out", str(out_path)],
            capture_output=True, text=True, timeout=120,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"exhibit_tables.py failed for {html_path!r}: {proc.stderr[:300]}"
            )
        return json.loads(out_path.read_text(encoding="utf-8"))


def _looks_like_value(text: str) -> bool:
    """A cell is a candidate VALUE only if it carries at least one digit. This
    drops the `$`/empty separator cells that exhibit_tables keeps as their own
    columns (a lone `$` is non-empty but not a value) without re-parsing the
    number itself — the exact printed string is preserved for the anti-fabrication
    confirm gate.
    """
    return any(ch.isdigit() for ch in text)


def _find_header_row(cells_by_row: dict[int, list[dict]],
                     row_label_paths: list[list[str]]) -> int | None:
    """The first row that supplies COLUMN headers: a multi-cell row whose every
    cell is a leading label (no value cell past the label boundary). In the NFLX
    exhibit that is the `Q4'23 ... Q1'25 Forecast` period row.
    """
    for r in sorted(cells_by_row):
        label_path = row_label_paths[r] if r < len(row_label_paths) else []
        if len(label_path) < 2:
            continue
        boundary = len(label_path)
        has_value_cell = any(c["col"] >= boundary for c in cells_by_row[r])
        if not has_value_cell:
            return r
    return None


def _make_candidate(label_path: list[str], value: str, period_hint: str,
                    accession: str, table_index: int, row: int, col: int) -> dict:
    """Assemble one RAW candidate: mechanical descriptors + provenance filled,
    every semantic slot null. `needs_semantic` names the null slots explicitly so
    Task 4's commit gate can refuse a point whose LLM slot was never filled.
    """
    return {
        "label": list(label_path),
        "value": value,
        "period_hint": period_hint,
        "source_accession": accession,
        "source_table_id": table_index,
        "source_cell_ref": {"row": row, "col": col},
        "confirmed": False,
        "kpi_id": None,
        "unit": None,
        "period": None,
        "needs_semantic": list(_SEMANTIC_FIELDS),
    }


def build_candidates(tables: list[dict], accession: str) -> list[dict]:
    """Pure transform: exhibit-table JSON -> RAW candidate points. For every data
    row, each value cell past the row's label boundary becomes one candidate
    carrying the row's verbatim label path and the column header at the same grid
    column as its `period_hint`.

    LOOM-SIMPLIFY: period_hint uses same-column-index alignment between the
    header row and each data row | ceiling: a $-interleaved (monetary) row is
    proposed, where interleaved `$` separator columns shift value columns out of
    alignment with the header and mislabel the period_hint | upgrade: position-
    aware column mapping that skips separator/`$` columns when pairing a value
    column to its header | ref: docs/loom/plans/2026-07-19-8k-earnings-kpi-intake.md T3. In
    scope for this arc: the non-monetary membership KPI row, which has no `$`
    separators, so its columns align exactly (verified by the propose test).
    """
    candidates: list[dict] = []
    for table in tables:
        table_index = table["table_index"]
        row_label_paths = table["row_label_paths"]

        cells_by_row: dict[int, list[dict]] = {}
        for cell in table["cells"]:
            cells_by_row.setdefault(cell["row"], []).append(cell)

        header_row = _find_header_row(cells_by_row, row_label_paths)
        header_by_col: dict[int, str] = {}
        if header_row is not None:
            header_by_col = {c["col"]: c["text"] for c in cells_by_row[header_row]}

        for row in sorted(cells_by_row):
            if row == header_row:
                continue
            label_path = row_label_paths[row] if row < len(row_label_paths) else []
            boundary = len(label_path)
            for cell in sorted(cells_by_row[row], key=lambda c: c["col"]):
                col = cell["col"]
                if col < boundary or not _looks_like_value(cell["text"]):
                    continue
                candidates.append(_make_candidate(
                    label_path, cell["text"], header_by_col.get(col, ""),
                    accession, table_index, row, col,
                ))
    return candidates


def propose(html_path: str, accession: str) -> list[dict]:
    """Mechanical candidate proposal for one exhibit document: subprocess the
    table walker, then transform its output into RAW candidate points. Returns
    the candidate list (the CLI writes it to a file).
    """
    tables = run_exhibit_tables(html_path)
    return build_candidates(tables, accession)


def _cli_propose(args: argparse.Namespace) -> int:
    """`propose` subcommand: run the mechanical producer and write the candidate
    list as JSON to `--out`. Exit 0 on success, prints a one-line summary.
    """
    candidates = propose(args.html, args.accession)
    Path(args.out).write_text(
        json.dumps(candidates, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"proposed {len(candidates)} raw candidate(s) -> {args.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Mechanical 8-K KPI candidate producer (values + coordinates "
        "+ verbatim labels only; semantic fields left null for the LLM layer)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    propose_parser = subparsers.add_parser(
        "propose", help="Emit RAW KPI candidate points from an exhibit HTML doc."
    )
    propose_parser.add_argument("--html", required=True, help="Path to exhibit HTML")
    propose_parser.add_argument(
        "--accession", required=True, help="Filing accession (source provenance)"
    )
    propose_parser.add_argument("--out", required=True, help="Path to write candidates JSON")
    propose_parser.set_defaults(func=_cli_propose)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
