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

```
# append: reads ONE point as JSON from stdin (or --file PATH)
echo '{"company": "AAPL", "kpi_id": "iphone_units", "period": "FY2024", \
  "as_of": "2024-11-01", "value": 231000000, \
  "source_accession": "0000320193-24-000123", \
  "source_table_id": "ex99-1-operating-summary", "source_cell_ref": "r5c2"}' \
  | uv run scripts/kpi_store.py append

# query --latest: greatest as_of overall
uv run scripts/kpi_store.py query --latest \
    --company AAPL --kpi-id iphone_units --period FY2024

# query --as-of: point-in-time (greatest as_of <= the given date)
uv run scripts/kpi_store.py query --as-of 2024-12-31 \
    --company AAPL --kpi-id iphone_units --period FY2024
```

| Subcommand | Flag         | Required | Notes                                                        |
|------------|--------------|----------|---------------------------------------------------------------|
| `append`   | `--file`     | no       | Path to a JSON file holding the point (default: read stdin)    |
| `query`    | `--company`  | yes      | Company identifier                                             |
| `query`    | `--kpi-id`   | yes      | KPI identifier                                                  |
| `query`    | `--period`   | yes      | Reporting period                                                |
| `query`    | `--latest`   | one-of   | Return the greatest-as_of record overall                       |
| `query`    | `--as-of`    | one-of   | Return the greatest-as_of record with `as_of <= DATE` (point-in-time) |

`append` exits **0** on success; a rejected point (missing provenance, or
`as_of` absent/wall-clock-flagged) prints the `ValueError` message to stderr
and exits **1** — fail loud, nothing written. `query` prints the matched
record as JSON to stdout (or `null` if none matched) and exits **0**.
`--latest` and `--as-of` are mutually exclusive and one is required.
