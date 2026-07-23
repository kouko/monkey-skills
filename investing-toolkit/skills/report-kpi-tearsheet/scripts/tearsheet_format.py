#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""tearsheet_format.py -- Pure formatter for report-kpi-tearsheet.

Reads a `kpi_store.py dump --company <C>` payload (PINNED schema --
docs/loom/plans/2026-07-23-kpi-tearsheet.md ## Notes, transcribed verbatim)
and renders a single Markdown KPI x period tearsheet to stdout.

PURE FUNCTION -- no HTTP, no subprocess, no env access beyond argparse/stdin
(snapshot_format.py precedent).

`render_tearsheet(dump: dict) -> str` expects `dump` to carry the pinned
`company` / `series` / `warnings` fields PLUS an `as_of` key -- the CLI's
required `--as-of` render date, merged into the payload by `main()` before
calling this function. `as_of` is NOT part of the store's dump payload; it
is a rendering-only addition (no wall-clock default -- the CLI's `--as-of`
is required, per the plan's rendering commitments).

Column layout: periods become table columns, unified across the company's
KPIs by period identity `(period_start, period_end)` -- the store's own
`same_period` raw date-pair identity (labels are display-only per the pin).
Columns sort newest-left; each column's header is the SHORTEST label seen
for that identity (tie-break: first-seen order across the walk). Rows are
one per `kpi_id` (series order -- already sorted by kpi_id per the pin). A
cell renders the period's `latest.canonical_value` with thousands
separators (+ `unit` when present, no B/M compaction -- kickoff decision,
plan ## Notes); a KPI with no period at that identity renders `N/A`.

A period whose `disagreement` flag is true renders its cell as the latest
canonical value suffixed `†`. Composition order is fixed: value, then
`unit` (when present), then `†` last -- e.g. "93,775,000,000 USD†", never
"93,775,000,000†USD". A trailing `## Revisions` block then lists,
per flagged (kpi, period), every observation as `<canonical_value> --
recorded <as_of> -- <source_accession>` in as_of order (pin guarantees
`observations` is already as_of-ascending). No flagged periods -> no
`## Revisions` heading at all.

Empty `series` renders a "No KPI records for <company>." card instead of an
empty table. The footer ALWAYS renders a provenance line ("Rendered <as_of>
from <n> series", plus a `(store: <dir>)` label when the CLI's optional
`--store-dir` flag is passed); a non-empty `warnings` list renders a
trailing `## Warnings` block echoing each warning verbatim. The CLI's
optional `--out <path>` flag writes the identical Markdown to that path
instead of stdout.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from typing import Any

PeriodKey = tuple[Any, Any]


def _period_key(period: dict[str, Any]) -> PeriodKey:
    return (period.get("period_start"), period.get("period_end"))


def _period_sort_key(key: PeriodKey) -> tuple[str, str]:
    """Newest-left sort key: descending by period_end, then period_start.

    A missing (None) bound sorts as "" -- an undated period identity falls
    to the oldest (rightmost) side of the newest-left axis.
    """
    start, end = key
    return (end or "", start or "")


def _shortest_label(labels: list[str]) -> str:
    """Shortest label wins; ties broken by first-seen order in `labels`."""
    best = labels[0]
    for label in labels[1:]:
        if len(label) < len(best):
            best = label
    return best


def _build_period_axis(series: list[dict[str, Any]]) -> list[tuple[PeriodKey, str]]:
    """Union of period identities across all KPIs, newest-left, each paired
    with its column header.

    Labels are collected in series order (already kpi_id-sorted per the
    pin), then within-period label order -- so "first-seen" for the tie-
    break is well-defined across the whole axis-building walk, not just
    within one KPI's period entry.
    """
    labels_by_key: dict[PeriodKey, list[str]] = {}
    for entry in series:
        for period in entry.get("periods", []):
            key = _period_key(period)
            seen = labels_by_key.setdefault(key, [])
            for label in period.get("period_labels", []):
                if label not in seen:
                    seen.append(label)
    ordered_keys = sorted(labels_by_key, key=_period_sort_key, reverse=True)
    return [(key, _shortest_label(labels_by_key[key])) for key in ordered_keys]


def _fmt_cell_value(latest: dict[str, Any]) -> str:
    """canonical_value with thousands separators, verbatim-faithful (no B/M
    compaction), `unit` appended when present -- kickoff decision, plan
    ## Notes."""
    value = latest.get("canonical_value")
    if value is None:
        return "N/A"
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        return str(value)
    formatted = f"{amount:,}"
    unit = latest.get("unit")
    if unit:
        formatted = f"{formatted} {unit}"
    return formatted


def _fmt_amount(value: Any) -> str:
    """canonical_value with thousands separators, no unit -- used for the
    Revisions block's per-vintage lines (the pin's `<canonical_value> --
    recorded <as_of> -- <source_accession>` shape carries no unit field)."""
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        return str(value)
    return f"{amount:,}"


def _revisions_block(series: list[dict[str, Any]], axis_labels: dict[PeriodKey, str]) -> list[str]:
    """Per flagged (kpi, period): a heading plus every observation line, in
    the as_of order the pin guarantees `observations` already carries."""
    lines: list[str] = []
    for entry in series:
        kpi_id = entry.get("kpi_id", "")
        for period in entry.get("periods", []):
            if not period.get("disagreement"):
                continue
            label = axis_labels.get(_period_key(period), "")
            lines.append(f"### {kpi_id} — {label}")
            lines.append("")
            for obs in period.get("observations", []):
                value = _fmt_amount(obs.get("canonical_value"))
                as_of = obs.get("as_of", "")
                accession = obs.get("source_accession", "")
                lines.append(f"- {value} — recorded {as_of} — {accession}")
            lines.append("")
    return lines


def render_tearsheet(dump: dict[str, Any]) -> str:
    company = dump.get("company", "")
    as_of = dump.get("as_of", "")
    series = dump.get("series", [])
    warnings = dump.get("warnings", [])
    store_dir = dump.get("store_dir")

    out: list[str] = [f"# KPI Tearsheet — {company}", "", f"As of: {as_of}", ""]

    if not series:
        out.append(f"No KPI records for {company}.")
    else:
        axis = _build_period_axis(series)
        header_cells = ["kpi_id"] + [label for _, label in axis]
        out.append("| " + " | ".join(header_cells) + " |")
        out.append("|" + "|".join(["---"] * len(header_cells)) + "|")

        for entry in series:
            kpi_id = entry.get("kpi_id", "")
            periods_by_key = {_period_key(p): p for p in entry.get("periods", [])}
            row_cells = [kpi_id]
            for key, _label in axis:
                period = periods_by_key.get(key)
                if period is None:
                    row_cells.append("N/A")
                else:
                    cell = _fmt_cell_value(period.get("latest", {}))
                    if period.get("disagreement"):
                        cell += "†"
                    row_cells.append(cell)
            out.append("| " + " | ".join(row_cells) + " |")

        revisions_lines = _revisions_block(series, dict(axis))
        if revisions_lines:
            out.append("")
            out.append("## Revisions")
            out.append("")
            out.extend(revisions_lines)

    out.append("")
    provenance = f"Rendered {as_of} from {len(series)} series"
    if store_dir:
        provenance += f" (store: {store_dir})"
    out.append(provenance + ".")

    if warnings:
        out.append("")
        out.append("## Warnings")
        out.append("")
        out.extend(f"- {warning}" for warning in warnings)

    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Format a kpi_store.py `dump --company` payload into a Markdown "
            "KPI tearsheet. Pure formatter -- no I/O beyond input + stdout."
        ),
    )
    parser.add_argument(
        "--in",
        dest="in_path",
        default=None,
        help="Path to the kpi_store.py `dump --company` JSON payload. Omit to read from stdin.",
    )
    parser.add_argument(
        "--as-of",
        dest="as_of",
        required=True,
        help="Render date to stamp the tearsheet header with (required -- no wall-clock default).",
    )
    parser.add_argument(
        "--store-dir",
        dest="store_dir",
        default=None,
        help="Optional store directory label surfaced in the footer's provenance line.",
    )
    parser.add_argument(
        "--out",
        dest="out_path",
        default=None,
        help="Optional path to write the rendered Markdown to. Omit to print to stdout.",
    )
    args = parser.parse_args()

    if args.in_path:
        try:
            with open(args.in_path, "r", encoding="utf-8") as f:
                dump = json.load(f)
        except FileNotFoundError:
            print(f"error: input file not found: {args.in_path}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as e:
            print(f"error: invalid JSON in {args.in_path}: {e}", file=sys.stderr)
            return 1
    else:
        try:
            sys.stdin.reconfigure(encoding="utf-8")
            dump = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"error: invalid JSON on stdin: {e}", file=sys.stderr)
            return 1

    if not isinstance(dump, dict):
        print(f"error: top-level dump JSON must be an object, got {type(dump).__name__}", file=sys.stderr)
        return 1

    dump["as_of"] = args.as_of
    if args.store_dir:
        dump["store_dir"] = args.store_dir

    rendered = render_tearsheet(dump)

    if args.out_path:
        try:
            with open(args.out_path, "w", encoding="utf-8") as f:
                f.write(rendered)
        except (FileNotFoundError, PermissionError, OSError) as e:
            print(f"error: cannot write to {args.out_path}: {e}", file=sys.stderr)
            return 1
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
