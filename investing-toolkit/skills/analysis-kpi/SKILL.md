---
name: analysis-kpi
description: >-
  Append-only bitemporal store for validated operational-KPI series-points
  (US SEC primary-source layer). Persists file-per-series JSON keyed by
  company+kpi_id under a durable DATA dir, keeping full history so a
  restatement appends a superseding record and a point-in-time query sees
  only what was known then. 営業 KPI 二時制追加専用ストア。營運 KPI 雙時態
  唯附加儲存層。
---

# analysis-kpi

Layer 2 (Analysis) internal-persistence skill for the **operational-kpi**
capability of the US SEC primary-source layer. This capability is built
**INCREMENTALLY as a sequence of thin slices** (validated spec:
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`).

**This slice = the append-only bitemporal store** — the keystone every later
slice writes to. Later slices (HTML table extraction, KPI schema, locate/
parse, rule validation, XBRL cross-check, review queue, break-events,
reliability-gate, memo-feed) are NOT part of this slice.

## What it does

`scripts/kpi_store.py` persists a validated KPI series-point to a
**file-per-series JSON** (one file per `company`+`kpi_id`, holding a list of
point records) under a **durable DATA dir** — resolved as `KPI_STORE_DIR`
env override → `$XDG_DATA_HOME/investing-toolkit/kpi-store` →
`~/.local/share/investing-toolkit/kpi-store`. It is durable (NOT the
evictable cache dir): a bitemporal series is irreplaceable history.

A point is a dict:
`{company, kpi_id, period, as_of, value, source_accession, source_table_id,
source_cell_ref}` (+ optional `lineage`, `restates` — persisted verbatim,
not interpreted this slice). Records are wrapped in a versioned
`_kpi_store_meta` envelope so a future record-shape change is a detectable
migration, not a silent misread.

**Append-only:** an existing record is never mutated or deleted; a
restatement/re-extraction appends a superseding record instead.

## Persistence pattern (mirrored, not imported)

The store MIRRORS `data-markets/scripts/cache_util.py`'s key-sanitization
regex + atomic tmp+rename write **pattern**, but does NOT `import cache_util`
(cross-skill import would breach the analysis↔data-markets layer boundary —
analysis skills reach data-markets by subprocess, never by importing its
modules) and does NOT reuse its TTL envelope (a bitemporal series is
immutable append-only, no expiry). Stdlib only.

## CLI reference

Per-subcommand CLI detail (flags, exit codes, worked examples) for the
eleven persistence/compute scripts lives in
[`references/cli-reference.md`](references/cli-reference.md). Index:

- **`kpi_store`** — append-only bitemporal store: `append` a point / `query`
  `--latest` or `--as-of` (point-in-time).
- **`review_queue`** — review-item queue + human-confirm seam: `enqueue` /
  `list` / `adjudicate`.
- **`kpi_schema`** — KPI schema propose-then-confirm lifecycle: `propose` /
  `confirm` / `status`.
- **`kpi_validate`** — pure-compute rule-based value validation: `validate`
  (sign/unit/subtotal/gaap).
- **`kpi_parse`** — deterministic fail-loud cell parser: `parse` (raises on
  an unparseable cell, never coerces to 0).
- **`kpi_gate`** — reliability gate (accuracy -> TRUSTED/WITHHELD):
  `add-labels` / `evaluate` / `verdict`.
- **`kpi_break`** — break-event detection + adjudication: `detect` / `flag` /
  `confirm` / `dismiss` / `list`.
- **`kpi_series`** — dual as-reported/recast split + basis-required view:
  `apply` / `view`.
- **`kpi_memo_feed`** — memo-feed contract assembly (trust-gated): `build`.
- **`kpi_xbrl`** — XBRL fact -> kpi_store point adapter: `build`.
- **`kpi_xbrl_ingest`** — XBRL fact-pack -> kpi_store driver (no collapse):
  `ingest`.

The Route-B `kpi_8k_candidates` intake CLI is documented in full below (it
stays here because its 3-layer contract is load-bearing).

## Workflow: US XBRL -> tearsheet

The end-to-end path from a bare US ticker to a rendered KPI tearsheet is
three steps, in order:

1. **Fetch** the dimensional fact-pack from `data-markets`:
   `pack.py --pack kpi-quarterly --ticker <T> --market us` (US-only pack;
   SEC EDGAR dimensional XBRL, single ticker only — rate-limited 10 req/s).
2. **Ingest** the fact-pack into this skill's store:
   `kpi_xbrl_ingest.py ingest --pack <pack.json>` — derives a `kpi_id` per
   dimensional signature and appends every vintage to `kpi_store` (honors
   `KPI_STORE_DIR`; see [`references/cli-reference.md`](references/cli-reference.md)
   for flags/exit codes).
3. **Render** the tearsheet via `report-kpi-tearsheet`, which reads the
   now-populated store directly.

## CLI (kpi_8k_candidates) — 8-K semi-auto KPI intake (Route B)

`scripts/kpi_8k_candidates.py` — the tier-① intake lane for an 8-K
earnings-release exhibit (US SEC). It is a **THREE-LAYER** workflow;
each layer has a fixed role and **the LLM never produces or alters a
`value` or a `source_*` coordinate — it only proposes semantic labels**
(the value is mechanically produced in Layer 1 and human-ratified in
Layer 3; Layer 2 fills `kpi_id`/`unit`/`period` only).

**Layer 1 — MECHANICAL (`propose`, deterministic code):** subprocesses
data-markets `exhibit_tables.py` on the exhibit HTML, then emits RAW
candidate points — each carrying the verbatim row-label path, the exact
printed `value` string (never re-parsed), a verbatim `period_hint`
(column header) and a verbatim `unit_hint` (the table's own `(in …)`
caption, or `null`) — both ADVISORY, the source coordinates
(`source_accession`, `source_table_id`, `source_cell_ref`), and
`confirmed: false`. The
semantic slots `kpi_id`/`unit`/`period` are emitted as explicit `null`
with a `needs_semantic: ["kpi_id","unit","period"]` list. **This layer
never invents a slug, a unit, or a normalized period** — the value and
its coordinates come straight from the filed bytes to the file.

```
uv run scripts/kpi_8k_candidates.py propose --html ex991.htm \
    --accession 0001065280-25-000033 --out candidates.json
```

**Layer 2 — LLM PROPOSAL (the agent running this skill; prose, not
pytest):** for each candidate, read its verbatim `label` path,
`period_hint`, and `unit_hint` and FILL the three `needs_semantic` slots
as PROPOSALS —
`kpi_id` (a stable slug, e.g. `global_streaming_paid_memberships`),
`unit` (e.g. `millions`), and a normalized `period` (e.g. `2024-Q4`).
Fill ONLY from what the verbatim label/header text says; do NOT alter
`value` or any `source_*` coordinate. These are proposals, not truth —
their consequence is gated by Layer 3 code below, so a wrong guess is
caught at commit, never silently stored. (This layer is prose-instruction,
verified by dogfood, not by a unit test.)

**Layer 3 — HUMAN confirm-all + `commit` (deterministic gate):** the human
ratifies each proposal and flips `confirmed: true`; then `commit
--company <T>` appends into the tier-① store via the EXISTING
`kpi_store.append`. The gate order per candidate: an unconfirmed
candidate is **skipped** (never written); a confirmed candidate still
carrying a null semantic slot is **refused loud** (`_missing_semantic` —
this confirm gate enforces `unit`, which the store never inspects); a
candidate the store's own provenance/`as_of` guard rejects is **refused
loud** (`kpi_store.append`, un-weakened). Only confirmed-and-complete
points land.

```
uv run scripts/kpi_8k_candidates.py commit \
    --candidates candidates.json --company NFLX
```

| Subcommand | Flag           | Required | Notes                                              |
|------------|----------------|----------|----------------------------------------------------|
| `propose`  | `--html`       | yes      | Path to the raw exhibit HTML                        |
| `propose`  | `--accession`  | yes      | Filing accession (source provenance)                |
| `propose`  | `--out`        | yes      | Path to write the candidates JSON                   |
| `commit`   | `--candidates` | yes      | Path to the candidates JSON (propose output)        |
| `commit`   | `--company`    | yes      | Company/ticker key (one filing = one company)       |

`propose` exits **0**, writing the candidate list. `commit` exits **0**
when every confirmed candidate committed, and **non-zero** when ANY
confirmed candidate was refused-incomplete — a silent partial commit
would defeat the fail-loud contract. The store's append-only bitemporal
model and the confirm-all trust gate are **unchanged**: this lane feeds
the SAME `kpi_store.append`, adding only the mechanical/LLM/human split
in front of it.
