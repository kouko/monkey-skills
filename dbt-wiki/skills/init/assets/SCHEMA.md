# dbt-wiki Schema (v1.0 — frozen for v1.x)

This schema is **frozen for the v1.x line**. Frontmatter shape, page
types, and naming conventions will not change within v1.x patches; only
wording clarifications are allowed. Major schema changes ship in v2.0
with a migration script.

## Architecture

This knowledge base has three layers:

- **`dbt/` (or wherever `DBT_PROJECT_DIR` points)** — Source layer. Immutable.
  Never modified by skills. **Always the authoritative source of current behavior.**
  Includes: `models/**/*.sql`, `models/**/schema.yml`, `models/**/sources.yml`,
  `dbt_project.yml`, `packages.yml`.
- **`<dbt-project>/target/`** — Compilation artifacts produced by `dbt parse` /
  `dbt compile` / `dbt docs generate`. Read-only inputs to dbt-wiki:
  - `manifest.json` — Required. Source of model metadata, ref/source lineage, schema.yml claims.
  - `compiled/<project>/**/*.sql` — Required. Jinja-expanded SQL for sqlglot parsing.
  - `catalog.json` — Optional (Phase 2+). Real warehouse column types, row counts.
  - `run_results.json` — Optional (Phase 2+). Last test pass/fail.
- **`.dbt-wiki/`** — Wiki layer. Owned entirely by dbt-wiki skills. Records
  derived structure (per-model entity, lineage graph, column-level dependencies).
  Acts as a *best-effort structural cache*. Humans read via `/dbt-wiki:query`.
  Do not edit directly. (Enforced by repo-root CLAUDE.md drop-in.)
- **`.dbt-wiki/SCHEMA.md`** — Schema layer (this file).

### Coexistence with `.repo-wiki/`

If `.repo-wiki/` exists in the same repo, both directories are independent:

- **dbt-wiki** = STRUCTURE + COLUMN LINEAGE (derived from manifest.json + sqlglot)
- **repo-wiki** = WHY (decisions, refactor history, tribal knowledge)

Cross-link freely: `[fct_orders](.dbt-wiki/models/fct_orders.md)` from a
repo-wiki entity, `[FSD report decision](../.repo-wiki/sources/2026-04-29-fsd...md)`
from a dbt-wiki model.

### Positioning Statement

`.dbt-wiki/` is a derived snapshot of `target/manifest.json` + parsed compiled SQL.
It can drift if `dbt parse` / `dbt compile` is re-run after changes — query workflow
checks `manifest_sha` mtime against the snapshot and warns if drift detected.
For column-level lineage authority, run `/dbt-wiki:refresh` after every `dbt parse`.

## Directory Layout

```
.dbt-wiki/
  SCHEMA.md          # This file
  index.md           # Master catalog of all model/source/macro pages
  log.md             # Append-only operation log
  lineage.md         # Full DAG (model-to-model) visualization
  models/            # One page per dbt model
  sources/           # One page per declared dbt source
  macros/            # One page per macro (only those used by ≥1 model)
  seeds/             # One page per seed
  snapshots/         # One page per snapshot
  tests/             # One page per generic test (singular tests only — schema.yml tests inline in model page)
  exposures/         # One page per declared exposure (optional)
```

## Page Types

### model
File: `.dbt-wiki/models/<model_name>.md`

Filename: `model_name` from `manifest.json` (no path prefix; collisions
disambiguated with `<package>__<model>` form).

Frontmatter:

```yaml
---
unique_id: model.iCHEF_dbt_pipline.fct_orders     # manifest.json node id
type: model
package: iCHEF_dbt_pipline
path: dbt/models/marts/fct_orders.sql              # repo-relative
materialization: table                              # view | table | incremental | ephemeral | snapshot
schema: dbt_marts                                   # target schema
database: redshift_prod                             # target database (optional)
tags: ["finance", "daily"]                          # from dbt_project.yml or {{ config(tags=...) }}
group: finance                                      # from groups.yml
access: protected                                   # public | protected | private
contract_enforced: false                            # if model contract is enforced
last_updated: 2026-05-02
manifest_sha: <md5 of manifest.json at parse time>
columns_extracted_via: sqlglot                     # sqlglot | schema_yml_only | failed
columns:                                            # union of schema.yml + sqlglot SELECT
  - name: order_id
    type: bigint                                    # null if no catalog.json; else real warehouse type
    description: "primary key — Shopify line item id"
    declared_in_schema_yml: true                    # false = sqlglot-discovered, schema.yml missed it
    tests:                                          # only schema.yml column-level tests
      - not_null
      - unique
    sources:                                        # column-level lineage from sqlglot
      - "stg_orders.order_id"
  - name: customer_id
    type: bigint
    description: "FK to dim_customers"
    declared_in_schema_yml: true
    tests: [not_null]
    sources:
      - "stg_orders.customer_id"
      - "stg_customers.id"                          # COALESCE / CASE WHEN multi-source
depends_on:                                         # model-level (from manifest)
  refs:
    - stg_orders
    - stg_customers
  sources:
    - "raw_data.orders_raw"
  macros:
    - dbt_utils.surrogate_key
feeds_into:                                         # reverse lookup (init computes)
  - dim_orders_summary
  - mart_finance_daily
generic_tests:                                      # model-level tests (not column-level)
  - dbt_utils.unique_combination_of_columns
recorded_decisions: []                              # cross-link to .repo-wiki/sources/ (optional)
---
```

Body sections (all optional, init populates what's available):

```markdown
## Description
<from schema.yml description; or "No description in schema.yml">

## Materialization Notes
<from {{ config(...) }} block: incremental_strategy, partition_by, sort_key, etc.>

## SQL Preview
```sql
<first 30 lines of raw_code from manifest.json (with jinja); link to full file>
```

## Inline Comments (from raw_code)
```
[line 1]  -- joins Shopify webhook with normalized customer table
[line 8]  /* see ADR-2024-03 for materialization decision */
[line 14] {# WARNING: incremental hash must include event_at — incident 2025-08 #}
[line 35] -- status mapping per ticket FOO-1234
```
(Auto-extracted from `dbt/models/<path>.sql`. Empty section means no
comments in source. Refresh re-extracts.)

## Column Sources (from sqlglot)
- order_id ← stg_orders.order_id
- customer_id ← stg_orders.customer_id, stg_customers.id (COALESCE)

## Tests
- Column-level: <count>; see frontmatter `columns[].tests`
- Model-level: <count>; see frontmatter `generic_tests`
- Singular tests: <list of tests in tests/*.sql that reference this model>

## User Notes
(Populated by `/dbt-wiki:ingest`. Format: `### YYYY-MM-DD <slug>` per
entry, free-form prose body. Refresh PRESERVES this section verbatim
— it is user content, not derived. Examples:)

### 2026-05-02 redshift-permission-gotcha
prod_marts_readonly_group must be granted before each incremental run;
hook in dbt_project.yml handles this. See incident #4521.

## Cross-references
- WHY (decisions): [<linked source pages from .repo-wiki/, if any>]
- Upstream models: [stg_orders](stg_orders.md), [stg_customers](stg_customers.md)
- Downstream models: [dim_orders_summary](dim_orders_summary.md), ...
```

**Standard sections** (init/refresh regenerate): Description, Materialization
Notes, SQL Preview, Inline Comments, Column Sources, Tests, Cross-references.

**User-owned sections** (init/refresh PRESERVE verbatim): User Notes,
plus any `##`-level heading the user added that isn't in the standard list.

### source
File: `.dbt-wiki/sources/<source_name>__<table_name>.md`

Frontmatter:

```yaml
---
unique_id: source.iCHEF_dbt_pipline.raw_data.orders_raw
type: source
source_name: raw_data
table_name: orders_raw
schema: raw_data
database: redshift_raw
loaded_at_field: _etl_loaded_at                     # optional
freshness:                                          # optional
  warn_after: { count: 12, period: hour }
  error_after: { count: 24, period: hour }
columns:
  - name: order_id
    description: "..."
    tests: [not_null, unique]
fed_by:                                             # external loader info (free-form)
  - "Fivetran connector: shopify_orders"
feeds_into:                                          # which models depend on this source
  - stg_orders
last_updated: 2026-05-02
---
```

### macro
File: `.dbt-wiki/macros/<macro_name>.md`

Only macros referenced by ≥1 model get a page (init filters by usage count).

```yaml
---
unique_id: macro.iCHEF_dbt_pipline.parse_currency
type: macro
package: iCHEF_dbt_pipline                           # or external package name (e.g., dbt_utils)
path: dbt/macros/parse_currency.sql
arguments: [amount, currency_code]                   # from manifest macro signature
description: "..."                                   # from schema.yml or docstring
used_by_models: [fct_orders, fct_revenue, ...]      # init computes
last_updated: 2026-05-02
---
```

### seed / snapshot / test / exposure

Same pattern: one page per resource. Frontmatter mirrors manifest fields,
plus `feeds_into` (for seed/snapshot) or `tests_resource` (for tests) etc.

## Index, Lineage, Log

### index.md
Catalog of all pages. Sections:
- `## Models` (grouped by tier path: `models/staging/`, `models/marts/`, etc.)
- `## Models by Materialization` (table / view / incremental / ephemeral)
- `## Models by Tag`
- `## Models by Group`
- `## Sources`
- `## Macros (used)`
- `## Seeds / Snapshots / Tests / Exposures`

### lineage.md
Full DAG. Two views:
- `## ASCII Tree` (per top-level seed/source: traverse downward, indent each level)
- `## Adjacency List` (one section per model: `### <model>`, then `**depends on**: ...` and `**feeds into**: ...`)

For huge projects (>500 nodes), ASCII tree degrades to "tier-aggregated" view
(group all `staging/*` models under one Staging node), with `## Detail by Tier` subsections.

### log.md
Append-only operation log. Entries:

```
## [YYYY-MM-DD] init | <N> models, <M> sources, <K> macros
- manifest_sha: <md5>
- compiled_files_parsed: <count>
- sqlglot_failures: <count> (failed model names listed below)
  - <model_name>: <reason>
- column_lineage_extracted: <count>
- Pages created: <models created>/<sources>/<macros>
- Pages updated: <count>
- Pages removed (orphaned): <count>

## [YYYY-MM-DD] refresh | <N> changed (added: <a>, modified: <m>, removed: <r>)
- manifest_sha: <md5>
- Models added: <list>
- Models modified: <list>
- Models removed (marked, not deleted): <list>

## [YYYY-MM-DD] query | <question-slug>
- Pages consulted: <list>
- Verification triggered: <yes/no>
- Synthesis saved: <path or "not saved">
```

## Naming Rules

- Model file = `<model_name>.md` (no prefix). If two packages have a `customers` model,
  filename becomes `<package>__<model_name>.md` (e.g., `iCHEF_dbt_pipline__customers.md`).
- Source file = `<source_name>__<table_name>.md` (always 2-part, no collision risk).
- Macro file = `<macro_name>.md` for project macros, `<package>__<macro>.md` for external (dbt_utils, etc.).
- Slug rule: lowercase, underscores preserved (matching dbt convention).

## Refresh Idempotency Contract

When `/dbt-wiki:refresh` runs:

1. Compare new `manifest_sha` to log.md's most recent `manifest_sha`. Skip if identical.
2. For each model in new manifest:
   - If `unique_id` exists in `.dbt-wiki/models/`: diff frontmatter; rewrite if changed.
   - If new: create page.
3. For each model in `.dbt-wiki/models/` not in new manifest: append `removed: true` to frontmatter,
   move to `.dbt-wiki/_archive/<date>-<model>.md` (don't hard-delete).
4. Recompute `lineage.md` and `index.md` from scratch.
5. Append refresh entry to `log.md`.

## What dbt-wiki NEVER does

- Modify `dbt/`, `target/`, or any source file
- Hard-delete `.dbt-wiki/` pages (always archive)
- Run `dbt parse` / `dbt compile` on user's behalf (user runs explicitly; init checks for output)
- Connect to dbt Cloud, warehouse, or any external API
- Mutate `manifest.json` or any `target/` file
- Use `[[wikilinks]]` — only standard markdown links

## Coexistence with repo-wiki

- Both can exist in same repo (`.repo-wiki/` + `.dbt-wiki/`)
- Neither modifies the other
- CLAUDE.md drop-in for dbt-wiki uses different markers: `<!-- dbt-wiki:start --> ... <!-- dbt-wiki:end -->`
