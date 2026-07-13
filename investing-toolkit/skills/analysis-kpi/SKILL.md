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

## CLI

*Stub — lands in a later task.* A thin `append` / `query` argparse CLI over
`scripts/kpi_store.py` is declared in a later slice (plan Task 8); this
slice ships the library surface (`append`) only.
