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

## CLI (review_queue)

`scripts/review_queue.py` — the review-item queue + human-confirm seam
(slice 2). Reuses `kpi_store.resolve_store_dir` for the durable dir
(`KPI_STORE_DIR` env override applies here too).

```
# enqueue: reads ONE review-item as JSON from stdin (or --file PATH)
echo '{"review_item_id": "rev-0001", "subject_type": "kpi_point", \
  "subject_id": "AAPL:iphone_units:FY2024", \
  "reason": "value deviates >20% from prior as_of", \
  "created_at": "2026-07-14T09:00:00Z"}' \
  | uv run scripts/review_queue.py enqueue

# list: print the OPEN items as a JSON array
uv run scripts/review_queue.py list

# adjudicate: resolve an OPEN item
uv run scripts/review_queue.py adjudicate \
    --id rev-0001 --decision approve --by alice \
    --resolution "confirmed correct against 10-K"
```

| Subcommand   | Flag          | Required | Notes                                                        |
|--------------|---------------|----------|---------------------------------------------------------------|
| `enqueue`    | `--file`      | no       | Path to a JSON file holding the item (default: read stdin)    |
| `adjudicate` | `--id`        | yes      | The `review_item_id` to resolve                               |
| `adjudicate` | `--decision`  | yes      | One of `approve` / `reject` / `edit`                           |
| `adjudicate` | `--by`        | yes      | Human adjudicator identity (`adjudicated_by`) — never empty    |
| `adjudicate` | `--resolution`| no       | Free-text resolution note                                      |
| `adjudicate` | `--at`        | no       | Caller-supplied `adjudicated_at` timestamp                     |

`enqueue` exits **0** on success; a rejection (ValueError) exits **1**;
malformed JSON or a non-object item exits **2** — same fail-loud contract as
`kpi_store append`. `list` prints the OPEN items as a JSON array to stdout
and exits **0**. `adjudicate` exits **0** on success; an unknown id, an
illegal transition (item not OPEN), or the confirm-seam auth guard (empty/
pipeline `adjudicated_by`) rejects loud and exits **1**; a missing required
flag is handled by argparse itself and exits **2**.

## CLI (kpi_schema)

`scripts/kpi_schema.py` — the KPI schema propose-then-confirm lifecycle
(slice 3). Reuses `_store_fs.resolve_store_dir` for the durable dir
(`KPI_STORE_DIR` env override applies here too), and routes `confirm`
through `review_queue`'s human-confirm seam.

```
# propose: reads kpi_defs as a JSON ARRAY from stdin (or --file PATH)
echo '[{"kpi_id": "iphone_units", "label": "iPhone units sold", \
  "unit": "units", "locate_hint": "Segment Information table"}]' \
  | uv run scripts/kpi_schema.py propose \
      --company AAPL --review-item-id rev-schema-0001

# confirm: adjudicates the latest PROPOSED version through the
# review-queue human-confirm seam, then flips it CONFIRMED
uv run scripts/kpi_schema.py confirm \
    --company AAPL --by alice --at 2024-01-01

# status: print the company's schema versions + confirmed_kpi_ids
uv run scripts/kpi_schema.py status --company AAPL
```

| Subcommand | Flag               | Required | Notes                                                        |
|------------|--------------------|----------|-----------------------------------------------------------------|
| `propose`  | `--company`        | yes      | Company identifier                                               |
| `propose`  | `--review-item-id` | yes      | Id for the review-item enqueued to gate this proposal             |
| `propose`  | `--file`           | no       | Path to a JSON file holding the kpi_defs array (default: stdin)   |
| `confirm`  | `--company`        | yes      | Company identifier                                                |
| `confirm`  | `--by`             | yes      | Human adjudicator identity (`adjudicated_by`) — never empty       |
| `confirm`  | `--at`             | no       | Caller-supplied `adjudicated_at` timestamp                        |
| `status`   | `--company`        | yes      | Company identifier                                                |

`propose` exits **0** on success, printing the new version record as JSON;
malformed JSON or a non-array `kpi_defs` body exits **2** (nothing written);
a rejection (ValueError) exits **1**. `confirm` exits **0** on success,
printing the now-CONFIRMED version record; every fail-loud guard (no
PROPOSED schema for the company, an already-CONFIRMED head, or a rejected
identity from the reused human-confirm seam) is a ValueError and exits
**1**; a missing required flag is handled by argparse itself and exits
**2**. `status` always exits **0**, printing `{company, versions:
[{version, status}, ...], confirmed_kpi_ids}` — a company with no schema
proposed yet reads as `{"versions": [], "confirmed_kpi_ids": []}` rather
than an error.

## CLI (kpi_validate)

`scripts/kpi_validate.py` — rule-based operational-KPI value validation
(slice 4). PURE-COMPUTE: stdlib only, no `_store_fs`/durable dir/locking —
it reads an already-parsed value + a kpi_def and returns a rule verdict.

```
# validate: reads {value_record, kpi_def} JSON from stdin (or --file PATH)
echo '{"value_record": {"value": 231000000, "unit": "units", \
  "segments": [100000000, 131000000], "total": 231000000}, \
  "kpi_def": {"sign": "non-negative", "unit": "units"}}' \
  | uv run scripts/kpi_validate.py validate
```

| Subcommand | Flag     | Required | Notes                                                    |
|------------|----------|----------|-----------------------------------------------------------|
| `validate` | `--file` | no       | Path to a JSON file holding `{value_record, kpi_def}` (default: read stdin) |

`validate` runs every applicable rule (sign/unit/subtotal/gaap — a rule
whose precondition isn't met returns N/A and is skipped, never a failure)
and prints `{"eligible": bool, "failures": [{"rule","detail"}, ...]}` to
stdout. It exits **0** on ANY valid verdict — INCLUDING `eligible: false`,
since a validly-rejected value is not a CLI error — and exits **2** on
malformed JSON or a non-object payload (nothing computed, no raw
traceback).

## CLI (kpi_gate)

`scripts/kpi_gate.py` — the reliability gate: a ground-truth label-set
store + accuracy-based TRUSTED/WITHHELD/NOT_EVALUATED verdict per
(company, schema_version) (slice 5). Reuses `_store_fs.resolve_store_dir`
for the durable dir (`KPI_STORE_DIR` env override applies here too).

```
# add-labels: reads a JSON ARRAY of {kpi_id, period, value} entries from
# stdin (or --file PATH); APPENDS to the company's accumulated label set
echo '[{"kpi_id": "iphone_units", "period": "2024-Q1", "value": 61600000}]' \
  | uv run scripts/kpi_gate.py add-labels --company AAPL

# evaluate: reads extracted_values (a JSON array shaped like labels, or a
# {kpi_id: {period: value}} object) from stdin (or --file PATH); computes
# cell-level accuracy against the company's labels and persists a gate
# record keyed by (company, schema_version)
echo '[{"kpi_id": "iphone_units", "period": "2024-Q1", "value": 61600000}]' \
  | uv run scripts/kpi_gate.py evaluate \
      --company AAPL --schema-version v1 --threshold 0.95 --min-samples 5 \
      --at 2026-07-14T00:00:00Z

# verdict: print the recorded verdict + trust for (company, schema_version)
uv run scripts/kpi_gate.py verdict --company AAPL --schema-version v1
```

| Subcommand   | Flag              | Required | Notes                                                        |
|--------------|-------------------|----------|-----------------------------------------------------------------|
| `add-labels` | `--company`       | yes      | Company identifier                                               |
| `add-labels` | `--file`          | no       | Path to a JSON file holding the labels array (default: stdin)    |
| `evaluate`   | `--company`       | yes      | Company identifier                                               |
| `evaluate`   | `--schema-version`| yes      | The schema version this evaluation is scoped to                  |
| `evaluate`   | `--threshold`     | no       | Accuracy bar (inclusive); omitted/unset -> never TRUSTED (deferred calibration) |
| `evaluate`   | `--min-samples`   | no       | Minimum labeled cells required for a verdict (default 5)         |
| `evaluate`   | `--at`            | no       | Caller-supplied `evaluated_at` timestamp                         |
| `evaluate`   | `--file`          | no       | Path to a JSON file holding extracted_values (default: stdin)    |
| `verdict`    | `--company`       | yes      | Company identifier                                               |
| `verdict`    | `--schema-version`| yes      | The schema version to look up                                    |

`add-labels` exits **0** on success, printing the company's full
accumulated label list; malformed JSON or a non-array body exits **2**
(nothing written); a rejection (ValueError) exits **1**. `evaluate` exits
**0** on success, printing the gate record (`{company, schema_version,
metric, sample_size, verdict, evaluated_at}`); malformed JSON or a body
that is neither a JSON array nor object exits **2** (nothing persisted); a
rejection (ValueError) exits **1**. `verdict` always exits **0**, printing
`{"verdict": ..., "trusted": bool}` — a (company, schema_version) pair with
NO gate record reads `{"verdict": "WITHHELD", "trusted": false}` (fail-closed:
never trusted by omission), never an error. A missing required flag on any
subcommand is handled by argparse itself and exits **2**.
