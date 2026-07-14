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

This module ships the CLI + report-envelope (Task 3), the Source-B fact
index (Task 4), full `(concept, period, dimension)` triple matching
(Tasks 5-6), the matched/single-source routing partition (Task 7),
divergence classification incl. scale/rounding + n/a handling (Tasks 8-10),
non-GAAP non-force-matching (Task 11), restatement-signal /
decimal-disagreement structural checks (Tasks 12-13), `build_report`
(Task 14), which assembles all of the above into the populated report and
is wired into `main()` — `comparisons`/`high_alerts`/`single_source` are no
longer empty — and single-source honesty for unmatched doc cells (Task 15):
every `route_cells` unmatched cell is stated `"doc-only, no XBRL
counterpart"` in `single_source`, never gap-filled with a synthesized
XBRL value.

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
import math
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
    the data-markets producer is `sec_edgar_client.py::build_companyfacts_pack`,
    which flattens the raw companyfacts `units.USD` into this exact shape —
    do NOT re-implement that flatten, reuse the producer):
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

    Real companyfacts nesting (handled by the producer): the live SEC endpoint
    nests rows one level deeper — `data["facts"][taxonomy][tag]["units"]["USD"]`
    — and `build_companyfacts_pack` flattens `units.USD` (via `summarize_concept`)
    into the per-tag row list this consumer expects; it never passes the raw
    endpoint dict through. Live-verified end-to-end on AAPL (memo-wiring slice).
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


def build_source_b_accn_groups(source_b_pack: dict) -> dict:
    """Group EVERY companyfacts row by `(concept, period_key)`, preserving
    each filing's own `accn` + `value` — unlike `build_source_b_index`
    (Task 4), which is last-write-wins and silently drops an earlier
    same-period row from a different filing (see that function's docstring).
    Task 12 (restatement-signal) needs BOTH filings' values for the same
    period, so it groups here rather than reusing the last-wins index.

    Same pack shape as `build_source_b_index` (companyfacts-only, no
    Source A — plan Notes §Open question Q2 confirms `accn` is on every
    row): {"cik", "facts": {"<taxonomy>": {"<tag>": [rows]}}}, each row
    {start, end, value, accn, form, fy, fp, filed}.

    Returns: {(concept, period_key): [{concept, period, value, accn,
    filed}, ...]} — a LIST per key (every row kept), not a single
    last-write-wins entry.
    """
    if "cells" in source_b_pack:
        raise ValueError(
            "got a Source-A doc-table-cells pack (has 'cells'); "
            "build_source_b_accn_groups must be built ONLY from a Source-B companyfacts pack"
        )

    facts = source_b_pack.get("facts", {})
    groups: dict = {}
    for taxonomy, tags in facts.items():
        for tag, rows in tags.items():
            concept = f"{taxonomy}:{tag}"
            for row in rows:
                period = _row_period(row)
                key = (concept, _period_key(period))
                groups.setdefault(key, []).append({
                    "concept": concept,
                    "period": period,
                    "value": row.get("value"),
                    "accn": row.get("accn"),
                    "filed": row.get("filed"),
                })
    return groups


def detect_restatement_signals(source_b_pack: dict) -> list[dict]:
    """Task 12: detect a cross-filing comparative divergence — the SAME
    `(concept, period)` tagged with a DIFFERENT value under a DIFFERENT
    `accn` (i.e. the same period as reported in two different filings, e.g.
    the FY2023 10-K's own tagging vs the FY2024 10-K's prior-year
    comparative) — and classify it `restatement-signal`, citing BOTH
    accession numbers, rather than a doc-vs-XBRL tagging error (spec
    :129-136, "Prior-year comparative restated in the current filing").

    Built ONLY off `build_source_b_accn_groups` (accn-preserving), never
    `build_source_b_index` (last-write-wins — would silently drop the
    earlier filing's row for the same period, plan Notes §Anti-fabrication
    invariant / Task 4 docstring).

    `source_mode`: this compares two companyfacts (XBRL) rows across
    filings — it is NOT a doc-vs-companyfacts two-source pair. It is
    labelled `"single-source"` (an XBRL-internal, structural finding, per
    the declared `source_mode` enum — plan Notes §Declared schemas), never
    `"two-source"`, so the label stays honest about what was actually
    compared: two filings of ONE source (XBRL), not two independent
    sources.

    A `(concept, period)` with only ONE distinct `accn`, or with 2+ accns
    all reporting the IDENTICAL value, is NOT a restatement (no divergence
    to signal) and is skipped.

    Ordering of "earlier"/"later" is by each row's `filed` date (ISO
    strings sort chronologically); `accn` is the tiebreaker for a missing
    `filed`. With 3+ accns in a group (the common case — US SEC
    income-statement/cash-flow tables routinely carry 3 years of
    comparative figures per filing), the group is a restatement as soon
    as 2+ distinct values exist anywhere in it; the LAST-filed row is
    always `later`, and `earlier` is the EARLIEST-filed row whose value
    actually differs from `later`'s — never a naive first-vs-last
    comparison, which would silently miss a "restated then reverted"
    shape (e.g. filed order 100 -> 120 -> 100) where the first and last
    values happen to coincide but a genuine mid-series divergence
    occurred.

    Returns a list of entries: {concept, period, dimension: None,
    category: "restatement-signal", source_mode: "single-source",
    earlier_value, earlier_accn, later_value, later_accn, note}. Both
    values and both accns are always retained (plan Notes
    §Anti-fabrication invariant — never silently reconciled).
    """
    groups = build_source_b_accn_groups(source_b_pack)
    signals: list[dict] = []
    for rows in groups.values():
        by_accn: dict = {}
        for row in rows:
            by_accn.setdefault(row["accn"], row)
        if len(by_accn) < 2:
            continue
        distinct_values = {row["value"] for row in by_accn.values()}
        if len(distinct_values) < 2:
            continue

        ordered = sorted(by_accn.values(), key=lambda r: (r.get("filed") or "", r["accn"]))
        later = ordered[-1]
        # `distinct_values` (>= 2) already proved a genuine divergence
        # exists in this group, so some row's value must differ from
        # `later`'s — find the EARLIEST-filed such row. This is never a
        # first-vs-last-only comparison: with 3+ accns a "restated then
        # reverted" middle value (100 -> 120 -> 100) would otherwise be
        # silently dropped even though it diverged.
        earlier = next(row for row in ordered if row["value"] != later["value"])

        signals.append({
            "concept": earlier["concept"],
            "period": earlier["period"],
            "dimension": None,
            "category": "restatement-signal",
            "source_mode": "single-source",
            "earlier_value": earlier["value"],
            "earlier_accn": earlier["accn"],
            "later_value": later["value"],
            "later_accn": later["accn"],
            "note": (
                f"{earlier['concept']} for this period diverges across filings "
                f"({earlier['accn']} -> {later['accn']}) — a restatement signal, "
                "not a doc-vs-XBRL tagging error"
            ),
        })
    return signals


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


def check_decimal_disagreement(doc_cell: dict) -> dict | None:
    """Task 13 (single-source, distinct category — plan Notes §Declared
    schemas): detect XBRL US DQC rule 2.4.1 on ONE Source-A doc cell's own
    (`numeric_value`, `decimals`) pair — no second source consulted
    (`source_mode: "single-source"`).

    `decimals` states the precision the value is reported to: decimals=-6
    means the value is accurate to the nearest 10**6 (millions), so its
    digits below that grain SHOULD be zero. If the reported value carries
    NON-ZERO digits below the grain implied by its own `decimals`, the
    `decimals` attribute disagrees with the digits actually reported — a
    structural tagging defect in the filing itself, distinct from a
    doc/XBRL value MISMATCH (Task 8's classifier bands) and from Task 10's
    two-source `scale/rounding` tolerance label (that compares doc vs xbrl
    across sources; this compares a fact against its OWN claimed precision,
    single-source).

    Rule: `ndigits = int(decimals)`; `grain = 10 ** (-ndigits)` (mirrors
    `check_scale_rounding`'s grain derivation, generalizes to a positive
    `decimals` too, e.g. `"2"` -> `grain = 0.01`, fractional precision).
    Flag when `value` is not a clean multiple of `grain`. The clean-multiple
    test is done in SCALED integer space (`value * 10**ndigits` should be
    an integer), not via `value % grain` float modulo — modulo noise scales
    with `value`'s magnitude, not `grain`'s, so a fixed absolute tolerance
    misfires for a fractional (positive-decimals) grain against a large,
    genuinely-clean value (e.g. 1_000_000.45 at decimals="2" false-flags
    under `%`). `math.isclose` with a magnitude-relative tolerance on the
    scaled value avoids this. Missing/None `numeric_value`, or a
    missing/malformed `decimals`, fails soft (`None`), never crashes.

    Returns an annotation dict (`category`, `source_mode`, `note`) when the
    fact disagrees with its own claimed precision, or `None` when it is
    consistent (or the check cannot be evaluated).
    """
    value = doc_cell.get("numeric_value")
    if value is None:
        return None
    try:
        ndigits = int(doc_cell.get("decimals"))
    except (TypeError, ValueError):
        return None
    grain = 10 ** (-ndigits)
    scaled = value * (10 ** ndigits)
    nearest = round(scaled)
    if math.isclose(scaled, nearest, rel_tol=1e-9, abs_tol=1e-6):
        return None
    return {
        "category": "decimal-disagreement (DQC 2.4.1)",
        "source_mode": "single-source",
        "note": (
            f"value {value} carries sub-grain precision inconsistent with "
            f"its own decimals={doc_cell.get('decimals')!r} (grain {grain}) "
            "— DQC 2.4.1 decimal-disagreement, not a doc/XBRL value mismatch"
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


def build_report(source_a_pack: dict, source_b_pack: dict) -> dict:
    """Task 14: assemble the full xval report — wires `route_cells` (T5-T7),
    `classify_divergence` (T8-T10), `check_decimal_disagreement` (T13), and
    `detect_restatement_signals` (T12) into the declared report envelope
    (plan Notes §Declared schemas): `{comparisons, single_source,
    high_alerts}` (caller adds `_provenance`).

    `comparisons`: every matched `(doc_cell, xbrl_fact)` pair, classified via
    `classify_divergence`, with BOTH provenance citations attached —
    `doc_citation` (the doc cell's own citation dict: accession + statement
    name + cell location) and `xbrl_citation` (`{concept, accn}` from the
    matched companyfacts fact) — never dropped, never overwritten (plan
    Notes §Anti-fabrication invariant).

    `high_alerts`: every `comparisons` entry classified `alert == "high"`
    ALSO appears here — the SAME dict (doc_value, xbrl_value, pct_diff, both
    citations all present, untouched) — surfaced loudly, never silently
    reconciled (Task 14's own requirement). Nothing is picked, discarded, or
    averaged; both sides of a high divergence are always visible together.

    `single_source`: a documented HETEROGENEOUS bucket of single-source-mode
    structural findings, discriminated by `category` — deliberately NOT
    forced into the doc-vs-xbrl `comparisons` shape (Task 12 code-quality
    reviewer flag: a restatement signal's `earlier_value`/`later_value`/
    `earlier_accn`/`later_accn` fields are never renamed to `doc_value`/
    `xbrl_value` — that would misrepresent a cross-filing XBRL-vs-XBRL signal
    as a doc-vs-XBRL pair, an honesty violation of `source_mode`):
      - decimal-disagreement (DQC 2.4.1) entries, one per Source-A cell that
        `check_decimal_disagreement` flags. ALL cells are checked regardless
        of match status — a cell's own value/decimals precision consistency
        is a structural property of that one fact, independent of whether a
        companyfacts counterpart exists.
      - restatement-signal entries, verbatim from
        `detect_restatement_signals` (its own earlier/later shape, unchanged).
      - doc-only entries (Task 15), one per `routed["single_source"]` cell —
        every Source-A cell `route_cells` (T7) could NOT pair with a
        companyfacts counterpart, per the `(concept, period, dimension)`
        triple match (plan Notes §Anti-fabrication invariant). Each carries
        `status: "doc-only, no XBRL counterpart"`, the doc `doc_value` +
        `doc_citation`, and `source_mode: "single-source"` (the cell WAS
        checked against companyfacts and found no match — a genuine
        single-source finding, not an unattempted lookup). No `xbrl_value`
        or `xbrl_citation` is ever set on this entry — never a synthesized
        counterpart invented to fill the gap. An unmatched cell that is ALSO
        flagged by `check_decimal_disagreement` legitimately produces TWO
        independent single_source entries (doc-only + DQC) — neither
        collapses the other, same never-drop discipline as the two-bucket
        case in `test_matched_cell_with_decimal_disagreement_surfaces_in_both_buckets`.
    Each shape's own fields plus `category`/`status`/`source_mode` let a
    consumer tell them apart without guessing.
    """
    source_b_index = build_source_b_index(source_b_pack)
    routed = route_cells(source_a_pack, source_b_index)

    comparisons: list[dict] = []
    high_alerts: list[dict] = []
    for doc_cell, xbrl_fact in routed["matched"]:
        entry = classify_divergence(doc_cell, xbrl_fact)
        entry["doc_citation"] = doc_cell.get("citation")
        # context_ref is the real iXBRL context reference for this SAME
        # matched fact, pulled from Source A's XBRL instance via the doc
        # cell's own citation — not fabricated. Companyfacts (Source B)
        # itself carries no context_ref field, only accn (the filing
        # reference), which is kept alongside it.
        entry["xbrl_citation"] = {
            "concept": xbrl_fact.get("concept"),
            "context_ref": doc_cell["citation"].get("context_ref"),
            "accn": xbrl_fact.get("accn"),
        }
        comparisons.append(entry)
        if entry.get("alert") == "high":
            high_alerts.append(entry)

    single_source: list[dict] = []
    for cell in source_a_pack.get("cells", []):
        disagreement = check_decimal_disagreement(cell)
        if disagreement is not None:
            single_source.append({
                "concept": cell.get("concept"),
                "period": cell.get("period"),
                "dimension": cell.get("dimension"),
                "doc_citation": cell.get("citation"),
                **disagreement,
            })
    single_source.extend(detect_restatement_signals(source_b_pack))

    for cell in routed["single_source"]:
        single_source.append({
            "concept": cell.get("concept"),
            "period": cell.get("period"),
            "dimension": cell.get("dimension"),
            "doc_value": cell.get("numeric_value"),
            "status": "doc-only, no XBRL counterpart",
            "source_mode": "single-source",
            "doc_citation": cell.get("citation"),
        })

    return {
        "comparisons": comparisons,
        "high_alerts": high_alerts,
        "single_source": single_source,
    }


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
        source_a_pack = _load_pack(args.source_a)
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"[analysis-xval ERROR] --source-a {args.source_a}: {exc}\n")
        return 2

    try:
        source_b_pack = _load_pack(args.source_b)
    except (OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"[analysis-xval ERROR] --source-b {args.source_b}: {exc}\n")
        return 2

    report = build_report(source_a_pack, source_b_pack)
    payload = {
        **report,
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
