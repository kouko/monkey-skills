#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Pure-compute cross-validation of SEC financial-statement doc-table cells
against XBRL companyfacts ("xval").

Layer 2 (Analysis) under the v2.0.0 three-layer design — mirrors the
analysis-comps CLI template:
- NO I/O beyond the two JSON paths supplied via --source-a / --source-b.
- Source A = a doc-table cells pack (edgartools statement extraction,
  produced by data-markets/scripts/sec_edgar_client.py::extract_statement_cells).
- Source B = a companyfacts fact pack (`summarize_concept` shape).

This module currently ships ONLY the CLI + report-envelope skeleton (Task 3
of the financial-table-xval plan) — matching/classification logic lands in
later tasks. `comparisons` is always empty for now.

Declared schemas (plan Notes §Declared schemas — producer/consumer contract):
- Source A cell: {concept, period:{type:"instant"|"duration", instant?,
  start?, end?}, dimension: null|{axis, member}, value_displayed:str,
  numeric_value:float, decimals:str, citation:{accession, statement_name,
  row, col, label, context_ref, fact_id}}
- Source B fact (companyfacts, `summarize_concept` shape under a concept
  key): {concept, period:{start, end}, value:int (full-magnitude), accn,
  form, fy, fp, filed} — no dimension, no scale/decimals.
- Report entry: {concept, period, dimension, doc_value, xbrl_value,
  abs_diff, pct_diff, alert, source_mode:"two-source"|"single-source",
  category: null|"scale/rounding"|"restatement-signal"|
  "decimal-disagreement (DQC 2.4.1)", status?: "doc-only, no XBRL
  counterpart", doc_citation, xbrl_citation, note?}.
- Report envelope: {comparisons:[...], high_alerts:[...],
  single_source:[...], _provenance:{...}}.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# xval's own tolerance bands (do NOT reuse analysis-comps' bands — different
# tuning; see plan Notes §Band constants). Not yet consumed by this skeleton;
# declared here so later tasks share one definition.
XVAL_BAND_LOW = 0.01   # ~1%
XVAL_BAND_HIGH = 0.05  # 5%


def _load_pack(path: Path) -> dict:
    """Load a Source A/B JSON pack. No network access."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _row_period(row: dict) -> dict:
    """Derive a Source-A-shaped period dict from a companyfacts row.

    Mirrors Source A's period shape (plan Notes §Declared schemas) so T5 can
    compare like-for-like: a companyfacts row with no `start` is an instant
    fact (`{type:"instant", instant:<end>}`); a row with both `start` and
    `end` is a duration fact (`{type:"duration", start, end}`).
    """
    if row.get("start") is None:
        return {"type": "instant", "instant": row.get("end")}
    return {"type": "duration", "start": row.get("start"), "end": row.get("end")}


def _period_key(period: dict) -> tuple:
    """Hashable key for a period dict (dicts aren't hashable, tuples are)."""
    if period["type"] == "instant":
        return ("instant", period["instant"])
    return ("duration", period["start"], period["end"])


def build_source_b_index(source_b_pack: dict) -> dict:
    """Build the Source-B fact index, reconstructed ONLY from a companyfacts
    pack — this is the genuinely-independent second source of each fact
    (plan Notes §Anti-fabrication invariant). This function's signature
    takes no Source-A input by construction; it must never be called with,
    or derive facts from, a Source-A doc-table cells pack.

    Source-B pack shape consumed here (declared producer/consumer contract;
    the data-markets side of a full companyfacts-pack fetcher isn't wired
    yet — plan Notes §Open question Q2):
      {"cik": <int>, "facts": {"<taxonomy>": {"<tag>": [<rows>]}}}
    where each row is exactly `sec_edgar_client.py::summarize_concept()`'s
    output shape: {start, end, value, accn, form, fy, fp, filed} — no
    `concept` field on the row itself (the concept lives in the taxonomy/tag
    keys), no dimension/scale/decimals (companyfacts is consolidated-only,
    per live probe).

    Concept-form normalization (flag for T5's matcher): index concept keys
    are joined "<taxonomy>:<tag>" (e.g. "us-gaap:Revenues") to match
    Source-A's edgartools colon-form concept (e.g. "us-gaap:Revenues" from
    `extract_statement_cells`). T5 MUST use this same taxonomy:tag join when
    comparing a Source-A cell's concept against this index's keys.

    Returns: {(concept, period_key): {concept, period, dimension: None,
    value, accn}} — dimension is always None (companyfacts carries no
    dimension).

    Last-write-wins on a duplicate (concept, period) key: a later row for the
    same period silently replaces an earlier one. Task 4's own scope never
    hits this, but Task 12 (restatement-signal, cross-`accn`) needs BOTH
    filings' values for the same period — T12 must key differently (e.g.
    list-per-key or include `accn` in the key), not reuse this last-wins index.

    Q2 (real companyfacts fetcher, not wired yet): the live SEC endpoint nests
    rows one level deeper — `data["facts"][taxonomy][tag]["units"]["USD"]` —
    so whoever builds the producer must flatten `units.USD` into the per-tag
    row list this consumer expects, not pass the raw endpoint dict through.
    """
    if "cells" in source_b_pack:
        raise ValueError(
            "got a Source-A doc-table-cells pack (has 'cells'); "
            "build_source_b_index must be built ONLY from a Source-B companyfacts pack"
        )

    facts = source_b_pack.get("facts", {})
    index: dict = {}
    for taxonomy, tags in facts.items():
        for tag, rows in tags.items():
            concept = f"{taxonomy}:{tag}"
            for row in rows:
                period = _row_period(row)
                index[(concept, _period_key(period))] = {
                    "concept": concept,
                    "period": period,
                    "dimension": None,
                    "value": row.get("value"),
                    "accn": row.get("accn"),
                }
    return index


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pure-compute cross-validation: doc-table cells vs XBRL companyfacts (Layer 2)."
    )
    parser.add_argument(
        "--source-a", required=True, type=Path,
        help="Path to the Source-A doc-table cells pack JSON (edgartools statement extraction)",
    )
    parser.add_argument(
        "--source-b", required=True, type=Path,
        help="Path to the Source-B companyfacts pack JSON (summarize_concept shape)",
    )
    args = parser.parse_args()

    try:
        _load_pack(args.source_a)
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"[analysis-xval ERROR] --source-a {args.source_a}: {exc}\n")
        return 2

    try:
        _load_pack(args.source_b)
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"[analysis-xval ERROR] --source-b {args.source_b}: {exc}\n")
        return 2

    payload = {
        "comparisons": [],
        "high_alerts": [],
        "single_source": [],
        "_provenance": {
            "skill": "analysis-xval",
            "io": "none",
            "computed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }

    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
