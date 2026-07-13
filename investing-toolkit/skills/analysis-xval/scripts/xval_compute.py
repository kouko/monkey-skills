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

This module currently ships the CLI + report-envelope skeleton (Task 3),
the Source-B fact index (Task 4), full `(concept, period, dimension)`
triple matching (Tasks 5-6), and the matched/single-source routing
partition (Task 7) — classification is not yet wired into the CLI.
`comparisons` is still always empty for now.

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


def match_cell(doc_cell: dict, source_b_index: dict) -> dict | None:
    """Match a Source-A doc-table cell to its Source-B fact by the FULL
    `(concept, period, dimension)` triple (plan Notes §Anti-fabrication
    invariant) — NEVER by table position, row-label text, or label
    similarity. `doc_cell["citation"]["label"]` is never read here.

    Concept is already like-for-like colon-form on both sides (Source A:
    edgartools `"taxonomy:tag"`; Source B index: built by
    `build_source_b_index`'s own `"<taxonomy>:<tag>"` join) — no extra
    normalization needed here. Period is compared via `_period_key`, the
    same hashable-key helper Task 4 uses to build the index.

    Dimension (Task 6): after a (concept, period) candidate is found, it is
    accepted ONLY if its `dimension` equals `doc_cell["dimension"]` exactly
    — both `None` (non-dimensional, Task 5's case), or both the identical
    `{axis, member}` dict. A same-concept/same-period candidate under a
    DIFFERENT member, or with NO member at all, is a dimension mismatch and
    is rejected (returns `None`) rather than silently accepted — matching a
    segment number against a differently-segmented or consolidated fact
    would silently cross-validate the wrong number.

    HYBRID reality: companyfacts (Source B) is consolidated-only, so
    `build_source_b_index` sets `dimension=None` on EVERY entry (there is no
    real dimensional companyfacts fact). Consequence: in production a
    dimensional doc cell will find at most a `dimension=None` candidate ->
    dimension mismatch -> `None` -> routed to single-source (Task 7); its
    member agreement is then checked single-source on the iXBRL side (per
    the brief's HYBRID model), NOT here.

    Returns the matched Source-B index entry, or `None` when the
    `(concept, period)` key has no counterpart, or when a counterpart
    exists but its dimension does not match (both cases route to Task 7's
    single-source handling).
    """
    concept = doc_cell["concept"]
    period_key = _period_key(doc_cell["period"])
    candidate = source_b_index.get((concept, period_key))
    if candidate is None:
        return None
    if candidate["dimension"] != doc_cell.get("dimension"):
        return None
    return candidate


def route_cells(source_a_pack: dict, source_b_index: dict) -> dict:
    """Partition every Source-A cell into a matched bucket or a single-source
    (unmatched) bucket via `match_cell` (Task 7; plan Notes
    §Anti-fabrication invariant) — this is the routing seam Task 8
    (classify matched pairs), Task 14 (high-alert surfacing), and Task 15
    (single-source honesty output) build on.

    Reads `source_a_pack["cells"]` (the declared Source-A pack shape,
    plan Notes §Declared schemas). For each cell, `match_cell` returns
    either the Source-B counterpart or `None`; a `None` result means NO
    counterpart exists for that cell's (concept, period, dimension) triple
    -> the cell is recorded unmatched and routed to single-source, never
    paired with an unrelated fact. `citation.label` is never consulted here
    (already true of `match_cell`).

    Returns: {"matched": [(doc_cell, xbrl_fact), ...],
    "single_source": [doc_cell, ...]} — plain data; no report-entry
    shaping (classification, citations envelope) happens here, that is
    later tasks' job.
    """
    matched: list[tuple[dict, dict]] = []
    single_source: list[dict] = []
    for cell in source_a_pack.get("cells", []):
        fact = match_cell(cell, source_b_index)
        if fact is None:
            single_source.append(cell)
        else:
            matched.append((cell, fact))
    return {"matched": matched, "single_source": single_source}


def _classify_divergence_alert(pct_diff: float) -> str:
    """Mirrors analysis-comps' `_classify_divergence_alert` structure
    (comps_compute.py:946) but off xval's OWN bands (plan Notes §Band
    constants) — NOT comps' `DIVERGENCE_BAND_LOW`/`_HIGH` (5%/15%, different
    tuning). `pct_diff` is percent-scaled input (e.g. 8.0 means 8%); bands
    are fraction-scaled, so compared ×100 (same convention as comps).
    """
    abs_pct = abs(pct_diff)
    if abs_pct <= XVAL_BAND_LOW * 100:
        return "low"
    if abs_pct <= XVAL_BAND_HIGH * 100:
        return "medium"
    return "high"


def _compute_divergence(doc_value: float | None, xbrl_value: int | float | None) -> dict:
    """Diff math mirroring analysis-comps' `_compute_divergence`
    (comps_compute.py:955): `abs_diff = doc_value - xbrl_value`,
    `pct_diff = (abs_diff / xbrl_value) * 100.0` (percent units, xbrl_value
    as divisor per plan Notes §Band constants). Both values are always
    retained by the caller regardless of which branch fires here.

    Edge cases (mirrors comps' n/a-never-drop discipline — full dedicated
    coverage is Task 9's scope, but the math needs these guards to avoid a
    ZeroDivisionError / crash on a None side):
    - either side `None` -> `pct_diff=None`, `alert="n/a"` + note.
    - `xbrl_value == 0` -> `pct_diff` undefined -> `alert="n/a"` + note
      (`abs_diff` still computed where possible).
    """
    if doc_value is None or xbrl_value is None:
        return {
            "abs_diff": None,
            "pct_diff": None,
            "alert": "n/a",
            "note": "doc_value or xbrl_value missing — cannot diff",
        }
    abs_diff = doc_value - xbrl_value
    if xbrl_value == 0:
        return {
            "abs_diff": abs_diff,
            "pct_diff": None,
            "alert": "n/a",
            "note": "xbrl value zero — pct_diff undefined",
        }
    pct_diff = (abs_diff / xbrl_value) * 100.0
    return {
        "abs_diff": abs_diff,
        "pct_diff": pct_diff,
        "alert": _classify_divergence_alert(pct_diff),
    }


def check_scale_rounding(doc_cell: dict, divergence: dict) -> dict | None:
    """Task 10 (REVISED, two-source tolerance — plan Notes §Scale/rounding
    grounding correction): on a matched pair's already-computed divergence
    (both sides full-magnitude, per the live probe that killed the original
    single-source rendered-vs-full framing — `value_displayed ==
    numeric_value` on every real cell), decide whether a NON-ZERO divergence
    is fully explained by the doc cell's rounding grain rather than a real
    tagging error.

    Grain comes ONLY from the doc cell's `decimals` field (e.g. "-6" ->
    `ndigits=-6` -> `grain=10**6`) — NEVER a `scale` field (companyfacts has
    none; Source A has none either) and NEVER an invented rendered-display
    mantissa. Tolerance is half a grain: the maximum two same-underlying
    values can differ once each is rounded to that grain.

    Returns an annotation dict (`category`, `alert`, `source_mode`, `note`)
    to be merged onto the report entry when the divergence qualifies, or
    `None` when it does not — either because the divergence is zero (a
    clean match, not a rounding artifact), beyond tolerance (a real
    divergence — left for the classifier's normal band), undefined
    (`alert == "n/a"` — no valid abs_diff to reason about), or `decimals` is
    missing/malformed (fails soft, never crashes).
    """
    if divergence.get("alert") == "n/a":
        return None
    abs_diff = divergence.get("abs_diff")
    if abs_diff is None or abs_diff == 0:
        return None
    try:
        ndigits = int(doc_cell.get("decimals"))
    except (TypeError, ValueError):
        return None
    grain = 10 ** (-ndigits)
    tolerance = grain / 2
    if abs(abs_diff) > tolerance:
        return None
    return {
        "category": "scale/rounding",
        "alert": "low",
        "source_mode": "two-source",
        "note": (
            f"|abs_diff|={abs(abs_diff)} within half the decimals-implied "
            f"rounding grain ({tolerance} of grain {grain}, decimals="
            f"{doc_cell.get('decimals')!r}) — benign rounding, not a tagging error"
        ),
    }


def classify_divergence(doc_cell: dict, xbrl_fact: dict) -> dict:
    """Build a classified report entry (plan Notes §Declared schemas) for one
    matched `(doc_cell, xbrl_fact)` pair — the output of `route_cells`'s
    `matched` bucket. Diffs the doc cell's full-magnitude `numeric_value`
    against the matched Source-B fact's full-magnitude `value` (both
    full-magnitude per the live probe, so a genuinely-agreeing pair yields
    ~0 pct_diff -> low). A matched pair is always two-source by construction
    (both a doc cell AND its companyfacts counterpart exist), so
    `source_mode` is set here unconditionally; `category` defaults to `None`
    and is only overridden by `check_scale_rounding` (Task 10) when the
    divergence is fully explained by the doc side's rounding grain.

    Both `doc_value` and `xbrl_value` are always retained on the entry,
    regardless of alert level (plan Notes §Anti-fabrication invariant).
    """
    doc_value = doc_cell.get("numeric_value")
    xbrl_value = xbrl_fact.get("value")
    divergence = _compute_divergence(doc_value, xbrl_value)
    entry = {
        "concept": doc_cell["concept"],
        "period": doc_cell["period"],
        "dimension": doc_cell.get("dimension"),
        "doc_value": doc_value,
        "xbrl_value": xbrl_value,
        "source_mode": "two-source",
        "category": None,
        **divergence,
    }
    scale_rounding = check_scale_rounding(doc_cell, divergence)
    if scale_rounding is not None:
        entry.update(scale_rounding)
    return entry


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
