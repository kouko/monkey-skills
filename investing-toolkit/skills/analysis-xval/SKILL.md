---
name: analysis-xval
description: >-
  Pure-compute cross-validation of US SEC financial-statement doc-table
  cells against XBRL companyfacts. Input: --source-a <doc-table-cells-pack>
  --source-b <companyfacts-pack>. Output: comparisons + high_alerts +
  single_source JSON, classifying each finding two-source vs single-source
  (scale/rounding, DQC 2.4.1 decimal-disagreement, restatement-signal).
  Xval 財報主表逐格對 XBRL 交叉驗證純計算層。
---

# analysis-xval

Pure-compute Layer 2 skill in the v2.0.0 three-layer architecture
(data → analysis → report). Cross-validates a US SEC filing's rendered
financial-statement table cells (Source A) against the same company's
XBRL companyfacts (Source B), surfacing where the two disagree and why.

## Layer 2 Contract — NO I/O

This skill performs **zero network or external file I/O** beyond reading
the `--source-a` and `--source-b` JSON paths. No SEC EDGAR / edgartools
client is imported. Fetching is the responsibility of the caller —
Source A comes from `data-markets/scripts/sec_edgar_client.py::extract_statement_cells`
(one financial statement's rendered table), Source B from the same
client's `summarize_concept` companyfacts shape.

```
data-markets:sec_edgar_client.py (extract_statement_cells → Source A)
data-markets:sec_edgar_client.py (summarize_concept        → Source B)
                                              ↓
                                       analysis-xval (this skill)
                                              ↓
                                comparisons / high_alerts / single_source
```

## Input Contract

`--source-a <path>` and `--source-b <path>` must point to JSON packs with
these shapes (full field-level contract in
[`scripts/xval_compute.py`](scripts/xval_compute.py) module docstring
:6-45 — this section is a reference-level summary, not the SoT):

**Source A** — one doc-table cells pack: `{"cells": [<cell>, ...]}` where
each cell is
`{concept, period:{type:"instant"|"duration", instant?, start?, end?},
dimension: null|{axis, member}, value_displayed:str, numeric_value:float,
decimals:str, citation:{accession, statement_name, row, col, label,
context_ref, fact_id}}`. `concept` uses edgartools colon form (e.g.
`us-gaap:Revenues`).

> **Envelope-wrap seam (for the eventual memo-wiring layer):**
> `data-markets/sec_edgar_client.py::extract_statement_cells` returns a **bare
> `list[dict]` of cells**, NOT this pack. Whoever wires the producer to this
> skill MUST wrap that list into the `{"cells": [...]}` envelope (optionally
> adding `accession`/`statement_name` at the top level) before passing it to
> `--source-a`. Passing the bare list writes a top-level JSON array, and
> `build_report` reads `source_a_pack.get("cells", [])` — a bare list has no
> `.get`, so the wrap is the wiring layer's responsibility, by design (data
> layer stays pure I/O; this compute layer consumes packs).

**Source B** — a companyfacts pack: `{"cik": <int>, "facts":
{"<taxonomy>": {"<tag>": [<row>, ...]}}}` where each row is
`summarize_concept()`'s shape — `{start, end, value:int
(full-magnitude), accn, form, fy, fp, filed}`. No `concept` field on the
row itself (lives in the taxonomy/tag keys); no dimension, scale, or
decimals — companyfacts is consolidated-only.

## CLI

```
uv run scripts/xval_compute.py \
    --source-a <doc-table-cells-pack.json> \
    --source-b <companyfacts-pack.json>
```

| Flag         | Required | Notes                                                      |
|--------------|----------|-------------------------------------------------------------|
| `--source-a` | yes      | Path to the Source-A doc-table cells pack JSON              |
| `--source-b` | yes      | Path to the Source-B companyfacts pack JSON                 |

Prints the report JSON to stdout, then exits. A missing path or invalid
JSON on either flag exits **2** with a `[analysis-xval ERROR] --source-a/-b
<path>: <error>` stderr message — no partial report is emitted.

## Matching

A Source-A cell and a Source-B fact pair only when their
`(concept, period, dimension)` triple matches exactly — same concept,
same instant/duration period, and (since companyfacts carries no
dimension) only a `dimension: null` doc cell can match at all. A
dimensioned doc cell (e.g. a segment breakout) and any non-GAAP concept
absent from the taxonomy never force-match a companyfacts row; both
route to `single_source` instead of being silently paired with an
unrelated fact.

## Output Contract

Report envelope (full field-level contract in `xval_compute.py`
`build_report()` docstring :543-593):

```json
{
  "comparisons": [
    {
      "concept": "us-gaap:Revenues",
      "period": { "type": "duration", "start": "2023-10-01", "end": "2024-09-28" },
      "dimension": null,
      "doc_value": 391035000000,
      "xbrl_value": 391035000000,
      "source_mode": "two-source",
      "category": null,
      "abs_diff": 0, "pct_diff": 0.0, "alert": "low",
      "doc_citation": { "accession": "...", "statement_name": "...", "row": 0, "col": 0, "label": "...", "context_ref": "...", "fact_id": "..." },
      "xbrl_citation": { "concept": "us-gaap:Revenues", "context_ref": "...", "accn": "..." }
    }
  ],
  "high_alerts": [ "... same shape as a comparisons entry, alert==\"high\" only ..." ],
  "single_source": [
    { "...": "doc-only, decimal-disagreement, or restatement-signal entries — see below" }
  ],
  "_provenance": { "skill": "analysis-xval", "io": "none", "computed_at": "..." }
}
```

- **`comparisons`** — every matched `(doc_cell, xbrl_fact)` pair, always
  carrying BOTH `doc_value` and `xbrl_value` plus both citations
  (`doc_citation`, `xbrl_citation`), regardless of alert level.
  `source_mode: "two-source"` unconditionally (a matched pair by
  construction has both sides). `alert` ∈ `{low, medium, high, n/a}` —
  own tolerance bands (`XVAL_BAND_LOW`=1%, `XVAL_BAND_HIGH`=5%; **not**
  analysis-comps' 5%/15% bands — different tuning; do not conflate).
  `n/a` when either side is missing or `xbrl_value == 0` (`pct_diff`
  undefined, never a crash).
- **`high_alerts`** — the same entry object for every `comparisons` item
  with `alert == "high"`, surfaced a second time here, verbatim —
  never silently reconciled, never averaged away.
- **`single_source`** — a heterogeneous bucket, discriminated by
  `category`/`status`/`source_mode` (three shapes, never renamed into
  each other):
  - **doc-only** (`status: "doc-only, no XBRL counterpart"`,
    `source_mode: "single-source"`) — a Source-A cell that
    `route_cells` could not pair to any companyfacts fact. Carries only
    `doc_value` + `doc_citation`; `xbrl_value`/`xbrl_citation` are never
    set — never a synthesized counterpart invented to fill the gap.
  - **`decimal-disagreement (DQC 2.4.1)`** (`source_mode:
    "single-source"`) — a Source-A cell whose reported `numeric_value`
    carries non-zero digits below the precision grain its own
    `decimals` field claims (XBRL US DQC rule 2.4.1). Checked on
    **every** cell regardless of match status — a fact's internal
    precision consistency doesn't depend on having a companyfacts
    counterpart. Distinct from a doc/XBRL value mismatch.
  - **`restatement-signal`** (`source_mode: "single-source"`) — the SAME
    `(concept, period)` reported with a DIFFERENT value under a
    DIFFERENT `accn` across companyfacts filings (comparative restated
    in a later filing). Carries `earlier_value`/`earlier_accn`/
    `later_value`/`later_accn` — **never** renamed to `doc_value`/
    `xbrl_value`, since this is an XBRL-vs-XBRL cross-filing comparison,
    not a doc-vs-XBRL pair. Labelled `single-source` even though two
    companyfacts rows are involved — both rows come from one source
    (XBRL), not two independent sources.

  An unmatched cell that is ALSO decimal-disagreement produces TWO
  independent `single_source` entries — neither collapses the other.

- **`scale/rounding`** (`category` on a `comparisons` entry, `alert:
  "low"`, `source_mode: "two-source"`) — a matched pair's non-zero
  divergence that is fully explained by the doc cell's own `decimals`-
  implied rounding grain (tolerance = half a grain). Grain comes ONLY
  from `decimals` — never an invented rendered-display value (a live
  probe found no retrievable scaled display value on any edgartools
  structured surface; `value_displayed == numeric_value` always). A
  beyond-grain divergence is left as a real divergence in the normal
  alert bands, not mislabelled scale/rounding.

### Anti-fabrication invariants

- Never synthesize a value on either side — a missing counterpart is
  reported as missing (`doc-only`), not filled in.
- Never silently reconcile a `high` alert — it is surfaced in
  `high_alerts`, not averaged, dropped, or downgraded.
- Match only by the exact `(concept, period, dimension)` triple — no
  fuzzy/partial matching, no forcing a dimensioned or non-GAAP cell onto
  an unrelated companyfacts row.
- A doc-only cell is stated honestly as unmatched (`status: "doc-only,
  no XBRL counterpart"`), never presented as if XBRL agreement were
  checked and passed.

## Cross-Plugin Handoff

This skill outputs JSON only. Memo composition and narrative belong
upstream:

```
data-markets:sec_edgar_client.py (extract_statement_cells + summarize_concept)
  → analysis-xval (this skill, pure compute)
  → report-equity-memo (orchestrates the xval findings into the memo narrative)
       → domain-teams:investing-team (variant perception, conviction)
       → domain-teams:docs-team (formatting, optional)
```

This skill never delegates and never writes files; it prints JSON to
stdout and returns.

---

## i18n footer

- 日本語: 米国 SEC 財務諸表本表のセル（Source A）と XBRL companyfacts
  （Source B）を突合し、乖離を two-source（一致度・scale/rounding）と
  single-source（DQC 2.4.1 桁不整合・restatement-signal・doc-only）に
  分類して純計算する Layer 2 スキル。**ネットワーク・外部 I/O 一切なし**。
  値の合成・高乖離の黙示的整合は一切行わない。
- 繁體中文: 對美國 SEC 財報本表儲存格（Source A）與 XBRL companyfacts
  （Source B）逐格交叉驗證，將差異分類為 two-source（一致/scale-
  rounding）與 single-source（DQC 2.4.1 小數位不一致／restatement-
  signal／doc-only）純計算的 Layer 2 skill。**無任何網路 / 外部 I/O**。
  絕不捏造數值，絕不悄悄調和高乖離。
- English: Pure-compute Layer 2 cross-validation of US SEC
  financial-statement doc-table cells against XBRL companyfacts.
  Classifies every finding as two-source (matched, incl. scale/rounding
  tolerance) or single-source (DQC 2.4.1 decimal-disagreement,
  restatement-signal, doc-only). **No network or external file I/O.**
  Never synthesizes a value; never silently reconciles a high alert.
