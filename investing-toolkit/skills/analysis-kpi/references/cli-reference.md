# analysis-kpi — CLI reference

Per-subcommand CLI detail for the operational-KPI scripts under
`scripts/`. Extracted from `SKILL.md` (which keeps the routing summary +
a one-line-per-CLI index). The Route-B `kpi_8k_candidates` 3-layer
intake contract stays in `SKILL.md` (always-loaded) and is **not**
duplicated here.

## CLI (kpi_store)

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

## CLI (kpi_parse)

`scripts/kpi_parse.py` — the deterministic cell parser (slice 9). PURE-
COMPUTE: stdlib only, no `_store_fs`/durable dir/locking — text in, number
out. FAIL-LOUD: an unparseable/missing cell RAISES (`UnparseableCell`),
never coerces to 0; a true `0`/`0.0` still parses to 0.0 (a real value).

```
# parse: reads the cell text from --cell (or stdin when omitted)
echo '$1,234' | uv run scripts/kpi_parse.py parse

uv run scripts/kpi_parse.py parse --cell '(123)'
```

| Subcommand | Flag     | Required | Notes                                                    |
|------------|----------|----------|-----------------------------------------------------------|
| `parse`    | `--cell` | no       | The cell text to parse (default: read stdin)               |

`parse` prints the parsed number to stdout and exits **0** on success. A
genuinely-unparseable cell (`UnparseableCell` — NM, n/a, dash-as-NA, blank/
whitespace-only, or other non-numeric junk) is a normal fail-loud outcome,
NOT a bug: it prints a clean message to stderr (no raw traceback) and exits
**1**. A malformed invocation (e.g. no subcommand) is handled by argparse
itself and exits **2**.

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

## CLI (kpi_break)

`scripts/kpi_break.py` — break-event detection + human adjudication
lifecycle (slice 6). Reuses `_store_fs.resolve_store_dir` for the durable
dir (`KPI_STORE_DIR` env override applies here too), and routes
`confirm`/`dismiss` through `review_queue`'s human-confirm seam.

```
# detect: reads {"prev": {...}, "curr": {...}} (two consecutive-period KPI
# summaries) from stdin (or --file PATH); PURE COMPUTE, no persistence
echo '{"prev": {"segments": ["iPhone"], "kpi_labels": {}}, \
  "curr": {"segments": ["iPhone", "Wearables"], "kpi_labels": {}}}' \
  | uv run scripts/kpi_break.py detect

# flag: reads ONE candidate ({"trigger": ..., "detail": ...}) as JSON from
# stdin (or --file PATH); persists a FLAGGED break-event + enqueues its
# review-item
echo '{"trigger": "resegmentation", \
  "detail": {"prev_segments": ["iPhone"], "curr_segments": ["iPhone", "Wearables"]}}' \
  | uv run scripts/kpi_break.py flag \
      --company AAPL --schema-version v1 --review-item-id ri-break-0001

# confirm: reads the mapping (old->new correspondence) as JSON from stdin
# (or --file PATH); adjudicates the break's review-item through the
# review-queue human-confirm seam, then flips it CONFIRMED
echo '{"iPhone": "iPhone", "Wearables": "Wearables (new)"}' \
  | uv run scripts/kpi_break.py confirm \
      --company AAPL --break-id AAPL:v1:0 --by alice

# dismiss: no request body; adjudicates through the same seam, flips
# the break DISMISSED
uv run scripts/kpi_break.py dismiss --company AAPL --break-id AAPL:v1:1 --by alice

# list: print all break-event records for a company as a JSON array
uv run scripts/kpi_break.py list --company AAPL
```

| Subcommand | Flag                | Required | Notes                                                        |
|------------|---------------------|----------|-----------------------------------------------------------------|
| `detect`   | `--file`            | no       | Path to a JSON file holding `{prev, curr}` summaries (default: stdin) |
| `flag`     | `--company`         | yes      | Company identifier                                               |
| `flag`     | `--schema-version`  | yes      | Schema version the candidate was detected under                   |
| `flag`     | `--review-item-id`  | yes      | Id for the review-item enqueued to gate this break-event           |
| `flag`     | `--file`            | no       | Path to a JSON file holding the candidate (default: stdin)         |
| `confirm`  | `--company`         | yes      | Company identifier                                                |
| `confirm`  | `--break-id`        | yes      | The `break_id` to confirm                                          |
| `confirm`  | `--by`              | yes      | Human adjudicator identity (`adjudicated_by`) — never empty        |
| `confirm`  | `--at`              | no       | Caller-supplied `adjudicated_at` timestamp                         |
| `confirm`  | `--file`            | no       | Path to a JSON file holding the mapping (default: stdin)           |
| `dismiss`  | `--company`         | yes      | Company identifier                                                |
| `dismiss`  | `--break-id`        | yes      | The `break_id` to dismiss                                          |
| `dismiss`  | `--by`              | yes      | Human adjudicator identity (`adjudicated_by`) — never empty        |
| `dismiss`  | `--at`              | no       | Caller-supplied `adjudicated_at` timestamp                         |
| `list`     | `--company`         | yes      | Company identifier                                                |

`detect` always exits **0**, printing the candidate list (`[]` if no drift);
malformed JSON or a body missing `prev`/`curr` exits **2**. `flag` exits
**0** on success, printing the new FLAGGED record; malformed JSON or a
non-object candidate exits **2** (nothing written); a rejection
(ValueError, or a candidate missing `trigger`/`detail`) exits **1**.
`confirm` exits **0** on success, printing the now-CONFIRMED record;
malformed JSON exits **2**; every fail-loud guard (unknown break_id, a
break not currently FLAGGED, a missing/empty mapping, or a rejected
identity from the reused review-queue human-confirm seam) is a ValueError
and exits **1**. `dismiss` exits **0** on success, printing the now-
DISMISSED record; the same fail-loud guards (minus the mapping check)
apply and exit **1**. `list` always exits **0**, printing all of a
company's break-event records as a JSON array (`[]` if none flagged yet).
A missing required flag on any subcommand is handled by argparse itself
and exits **2**.

## CLI (kpi_series)

`scripts/kpi_series.py` — dual as-reported/recast series split + a
basis-required view (slice 7). PURE-COMPUTE library surface
(`split_series`/`series_view`) — no store dir, no `KPI_STORE_DIR`. The
`apply` subcommand is the one exception: it is a thin wrapper over
`kpi_break.apply_break` (imported via the same-dir shim, reused not
reimplemented), so it DOES touch the durable break-event store
(`KPI_STORE_DIR` env override applies to `apply` only).

```
# apply: no request body; wraps kpi_break.apply_break(company, break_id,
# break_period) — requires the break is already CONFIRMED (slice 6),
# transitions it CONFIRMED -> APPLIED, prints the updated record
uv run scripts/kpi_series.py apply \
    --company AAPL --break-id AAPL:v1:0 --break-period FY2024

# view: reads {"points": [...], "applied_breaks": [...]} as JSON from
# stdin (or --file PATH); --basis selects as-reported/recast/dual. A
# series across an applied break with NO --basis is REJECTED loud (a
# naive concatenation across two incompatible lineages)
echo '{"points": [{"period": "FY2023", "value": 110}, \
  {"period": "FY2024", "value": 120}], \
  "applied_breaks": [{"break_period": "FY2024"}]}' \
  | uv run scripts/kpi_series.py view --company AAPL --basis dual
```

| Subcommand | Flag              | Required | Notes                                                        |
|------------|-------------------|----------|-------------------------------------------------------------------|
| `apply`    | `--company`       | yes      | Company identifier                                                 |
| `apply`    | `--break-id`      | yes      | The `break_id` to apply (must be CONFIRMED)                        |
| `apply`    | `--break-period`  | yes      | The period at/after which the recast lineage begins                |
| `view`     | `--company`       | yes      | Company identifier                                                 |
| `view`     | `--basis`         | no       | `as-reported` \| `recast` \| `dual`; omitted -> `None` (raises if the series has an applied break) |
| `view`     | `--file`          | no       | Path to a JSON file holding `{points, applied_breaks}` (default: stdin) |

`apply` exits **0** on success, printing the now-APPLIED break record;
every fail-loud guard in `kpi_break.apply_break` (unknown break_id, a
break not currently CONFIRMED, an empty break_period) is a ValueError and
exits **1**. `view` exits **0** on success, printing the `series_view`
result (a list for `as-reported`/`recast`, or the full
`{as_reported, recast, break_markers}` dict for `dual`); malformed JSON or
a body missing `points`/`applied_breaks` exits **2** (nothing computed); a
`series_view` rejection — a series with an applied break and no
`--basis`, or an unrecognized `--basis` string — is a ValueError and exits
**1**. A missing required flag on either subcommand is handled by argparse
itself and exits **2**.

## CLI (kpi_memo_feed)

`scripts/kpi_memo_feed.py` — the memo-feed contract assembly (slice 8;
consumed by report-equity-memo's quarterly-KPI wiring — its `build-quarterly`
subcommand emits the envelope-1.1 quarterly/XBRL-arm feed, store gate
tier-①-only). PURE-ASSEMBLY: stdlib only, no `_store_fs`/durable
dir/locking — it reuses `kpi_gate.is_trusted` (same-skill import) for the
trust verdict and takes the series data as a caller-supplied argument
rather than querying `kpi_store` directly.

```
# build: reads kpi_series as a JSON ARRAY from stdin (or --file PATH);
# TRUSTED (company, schema_version) -> a feed bundling kpi_series;
# any other verdict -> a WITHHELD feed with NO series values
echo '[{"kpi_id": "iphone_units", "points": [{"period": "2024-Q1", \
  "value": 61600000, "source_accession": "0000320193-24-000123", \
  "source_table_id": "ex99-1-operating-summary", "source_cell_ref": "r5c2"}]}]' \
  | uv run scripts/kpi_memo_feed.py build \
      --company AAPL --schema-version v1 --generated-at 2026-07-14T00:00:00Z
```

| Subcommand | Flag               | Required | Notes                                                        |
|------------|--------------------|----------|-----------------------------------------------------------------|
| `build`    | `--company`        | yes      | Company identifier                                               |
| `build`    | `--schema-version` | yes      | The schema version to check the reliability gate for             |
| `build`    | `--generated-at`   | no       | Caller-supplied `generated_at` timestamp (this module never reads the wall clock) |
| `build`    | `--file`           | no       | Path to a JSON file holding the kpi_series array (default: stdin) |

`build` exits **0** on success, printing the assembled feed — INCLUDING a
WITHHELD feed, since a validly-withheld company is not a CLI error.
Every series-point in a TRUSTED feed must carry complete provenance
(`source_accession`/`source_table_id`/`source_cell_ref`, all three,
directly on the point dict); a point missing any of them is a ValueError
and exits **1** (nothing returned) — an unattributed value is never
bundled into the feed. Malformed JSON or a non-array `kpi_series` body
exits **2** (nothing computed, no raw traceback). A missing required flag
is handled by argparse itself and exits **2**.

## CLI (kpi_xbrl)

`scripts/kpi_xbrl.py` — the XBRL fact -> kpi_store point adapter
(operational-kpi tier-② XBRL pilot). PURE-COMPUTE: stdlib only, no
`_store_fs`/durable dir/locking, no network — it reads an already-fetched
fact-pack (the shape `sec_edgar_client.extract_dimensional_revenue`
emits) and an era-specific binding, and resolves each to kpi_store-shaped
points.

```
# build: reads a fact-pack JSON ({company, facts: [...]}) from stdin (or
# --file PATH); --binding points to a JSON file holding the era-specific
# binding ({kpi_id, sources: [{concept, dimensions, consolidation?,
# source_kind}, ...]} — dimensions is a dict of ALL real breakdown axes,
# e.g. {"ProductOrService": "IPhoneMember"}; consolidation is an optional
# srt:ConsolidationItemsAxis reconciliation qualifier, not a breakdown
# axis); resolves it via resolve_binding and prints the points list
echo '{"company": "AAPL", "facts": [...]}' \
  | uv run scripts/kpi_xbrl.py build \
      --company AAPL --binding /path/to/iphone_revenue_binding.json
```

| Subcommand | Flag         | Required | Notes                                                        |
|------------|--------------|----------|-----------------------------------------------------------------|
| `build`    | `--company`  | yes      | Company identifier passed through to `resolve_binding`            |
| `build`    | `--binding`  | yes      | Path to a JSON file holding the binding                           |
| `build`    | `--file`     | no       | Path to a JSON file holding the fact_pack (default: read stdin)   |

`build` exits **0** on success, printing the resolved points list. A
`resolve_binding` rejection (ValueError — e.g. a fact matching >1 source,
an ambiguous binding) exits **1**. Malformed JSON, or a non-object
fact-pack or `--binding` body, exits **2** (nothing computed, no raw
traceback). A missing required flag is handled by argparse itself and
exits **2**.
