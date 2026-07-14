#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Dual as-reported/recast series split (operational-kpi capability, slice 7).

Layer 2 (Analysis) PURE-COMPUTE — mirrors kpi_validate.py: stdlib only,
JSON in -> JSON out. This module is NOT a durable store: it does NOT import
`_store_fs`, does NOT resolve a store dir, does NOT lock or write files.
`split_series` takes an already-ordered list of `points` and a list of
`applied_breaks` as plain arguments; persistence and break lifecycle
(CONFIRMED -> APPLIED) live in kpi_break.py, a separate seam this module
never touches.

- `split_series(points, applied_breaks)` — partitions a period-ordered
  series at the EARLIEST applied break's `break_period`: points strictly
  before it go to `as_reported`, points at/after it go to `recast` (the
  break takes effect FROM that period). No applied breaks -> everything
  stays `as_reported`, `recast` and `break_markers` are both empty.
- `series_view(points, applied_breaks, basis)` (slice 7, Task 3) —
  basis-required view over `split_series`'s result: `basis` selects
  "as-reported" (the as_reported list), "recast" (the recast list), or
  "dual" (the full `{as_reported, recast, break_markers}` dict). If
  there IS an applied break and `basis` is None, this REFUSES a naive
  concatenation and raises `ValueError` loud — the caller must pick a
  lineage explicitly. No applied break -> nothing to disambiguate, so
  any basis (including None) returns the flat as_reported series. An
  unrecognized basis string is always rejected loud, break or no break.
- a thin argparse CLI (`apply` / `view`, Task 4) with the same fail-loud
  exit-code convention as `kpi_break.py`'s CLI (0 success / 1 ValueError /
  2 malformed or malshaped input). `apply` is a thin wrapper over
  `kpi_break.apply_break` (imported via the same-dir shim below, NOT
  reimplemented) — this module's own persistence-free contract stands:
  the CLI process, not this module's library surface, is what touches
  `kpi_break`'s store.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Resolve same-dir modules without a package, so `import kpi_break` works
# both under `uv run --script` and under importlib test loading (mirrors
# kpi_break.py's / kpi_gate.py's own same-dir import shim). Only the CLI's
# `apply` subcommand touches kpi_break — the library surface above
# (split_series/series_view) stays pure-compute, no persistence.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import kpi_break  # noqa: E402


def split_series(points: list[dict], applied_breaks: list[dict]) -> dict:
    """Split a period-ordered series into as-reported/recast lineages.

    `points`: period-ordered list of dicts, each with at least `period`.
    `applied_breaks`: list of dicts, each with `break_period`.

    Returns `{"as_reported", "recast", "break_markers"}`. A point whose
    `period` compares >= the EARLIEST break's `break_period` is recast (the
    break takes effect from that period onward); earlier points stay
    as_reported. No applied_breaks -> all points as_reported, recast and
    break_markers both empty. Side-effect-free: reads its inputs, returns a
    new dict.
    """
    if not applied_breaks:
        return {"as_reported": list(points), "recast": [], "break_markers": []}

    earliest_break_period = min(b["break_period"] for b in applied_breaks)

    as_reported = [p for p in points if p["period"] < earliest_break_period]
    recast = [p for p in points if p["period"] >= earliest_break_period]
    break_markers = [{"break_period": b["break_period"]} for b in applied_breaks]

    return {"as_reported": as_reported, "recast": recast, "break_markers": break_markers}


_KNOWN_BASES = {"as-reported", "recast", "dual"}


def series_view(points: list[dict], applied_breaks: list[dict], basis: str | None) -> object:
    """Basis-required view over `split_series` — refuses a naive
    concatenation across an applied break.

    `basis` must be one of `"as-reported"` (returns the as_reported list),
    `"recast"` (returns the recast list), or `"dual"` (returns the full
    `{as_reported, recast, break_markers}` dict from `split_series`).

    If `applied_breaks` is non-empty (>=1 applied break) and `basis` is
    `None`, raises `ValueError` loud — a series across a break has two
    incompatible lineages, and returning either one implicitly (or
    concatenating them) would silently misrepresent the data, so the
    caller MUST pick a basis explicitly.

    If `applied_breaks` is empty, there is nothing to disambiguate: the
    as_reported and recast lineages are identical (recast is empty), so
    `basis=None` (or any recognized basis) returns the flat series
    (all points) without raising.

    An unrecognized `basis` string is always rejected loud (`ValueError`),
    whether or not there is an applied break.
    """
    if basis is not None and basis not in _KNOWN_BASES:
        raise ValueError(
            f"kpi_series.series_view: unknown basis {basis!r} — expected one "
            f"of {sorted(_KNOWN_BASES)} or None"
        )

    if not applied_breaks:
        return list(points)

    if basis is None:
        raise ValueError(
            "kpi_series.series_view: a series across a break requires an "
            "explicit basis (as-reported|recast|dual); refusing a naive "
            "concatenation"
        )

    split = split_series(points, applied_breaks)
    if basis == "as-reported":
        return split["as_reported"]
    if basis == "recast":
        return split["recast"]
    return split


def _read_json_arg(args) -> object:
    """Read the CLI body from `--file` (or stdin when omitted) and parse it
    as JSON. Raises `json.JSONDecodeError` on malformed input — every
    caller below catches that and exits 2, mirroring
    `kpi_break._read_json_arg`'s exit-code contract.
    """
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    return json.loads(raw)


def _cli_apply(args: argparse.Namespace) -> int:
    """`apply` subcommand: no request body — calls
    `kpi_break.apply_break(company, break_id, break_period)` (thin wrapper,
    not a reimplementation) and prints the updated (now APPLIED) break
    record. Every fail-loud guard in `apply_break` (unknown break_id, a
    break not currently CONFIRMED, an empty break_period) is a ValueError
    -> exit 1; success -> exit 0.
    """
    try:
        record = kpi_break.apply_break(args.company, args.break_id, args.break_period)
    except ValueError as exc:
        print(f"kpi_series apply: {exc}", file=sys.stderr)
        return 1

    json.dump(record, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cli_view(args: argparse.Namespace) -> int:
    """`view` subcommand: read `{"points": [...], "applied_breaks": [...]}`
    as JSON from `--file` (or stdin when omitted), call
    `series_view(points, applied_breaks, basis)` and print the result.
    Malformed JSON, or a body that is not a JSON object, or one missing
    `points`/`applied_breaks` -> exit 2 (nothing to compute). The
    naive-concatenation guard (a break present with no `--basis`) and any
    other `series_view` rejection (unknown basis) are ValueErrors -> exit
    1 — fail-loud, no raw traceback. `--basis` is optional (default None,
    same default `series_view` itself uses).
    """
    try:
        payload = _read_json_arg(args)
    except json.JSONDecodeError as exc:
        print(f"kpi_series view: invalid JSON input: {exc}", file=sys.stderr)
        return 2

    if (
        not isinstance(payload, dict)
        or "points" not in payload
        or "applied_breaks" not in payload
    ):
        print(
            "kpi_series view: expected a JSON object with 'points' and "
            f"'applied_breaks', got {payload!r}",
            file=sys.stderr,
        )
        return 2

    try:
        result = series_view(payload["points"], payload["applied_breaks"], args.basis)
    except ValueError as exc:
        print(f"kpi_series view: {exc}", file=sys.stderr)
        return 1

    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dual as-reported/recast series CLI (apply / view)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    apply_parser = subparsers.add_parser(
        "apply", help="Apply a CONFIRMED break-event (kpi_break.apply_break) and print the updated record."
    )
    apply_parser.add_argument("--company", required=True)
    apply_parser.add_argument("--break-id", required=True, dest="break_id")
    apply_parser.add_argument("--break-period", required=True, dest="break_period")
    apply_parser.set_defaults(func=_cli_apply)

    view_parser = subparsers.add_parser(
        "view", help="Print a basis-required view (as-reported / recast / dual) over a series."
    )
    view_parser.add_argument("--company", required=True)
    view_parser.add_argument("--basis", default=None)
    view_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding {points, applied_breaks} (default: read stdin).",
    )
    view_parser.set_defaults(func=_cli_view)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
