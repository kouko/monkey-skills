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
