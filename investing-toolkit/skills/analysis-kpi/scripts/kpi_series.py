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
"""
from __future__ import annotations


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
