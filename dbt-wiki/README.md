# dbt-wiki

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Local-only LLM-queryable knowledge base for dbt projects. Init reads `target/manifest.json` (model metadata, ref/source lineage, schema.yml columns, tests) plus `target/compiled/**/*.sql` parsed via [sqlglot](https://github.com/tobymao/sqlglot) for column-level lineage. Generates one markdown page per model / source / macro under `.dbt-wiki/`. Query answers natural-language questions about model structure, column-level data flow, materialization config, test coverage, and refactoring impact — without dbt Cloud, without leaving your machine.

**Version**: 1.0.0 · **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) · **License**: MIT

## Background

dbt has excellent first-party docs (`dbt docs generate` → static HTML site) and an ecosystem of paid tools (dbt Cloud Discovery API, third-party lineage platforms). But for **conversational LLM queries against your dbt project structure**, there's a gap:

- **dbt Cloud Discovery API** — has the metadata, but requires a paid subscription
- **dbt docs serve** — HTML for humans, not machine-queryable
- **`target/manifest.json`** — the structured truth, but 1-50 MB raw; no query interface
- **dbt-mcp without Discovery** — only exposes CLI tools; LLM has to parse `dbt list` stdout
- **General-purpose code search (Greptile, Cursor @Codebase)** — code-aware, not dbt-aware; misses lineage and column relationships

`dbt-wiki` fills the gap: a **local-only**, **LLM-queryable**, **column-lineage-aware** snapshot of your dbt project, derived from artifacts dbt already produces (no warehouse calls, no Cloud subscription).

## Skills

| Skill | When | Primary input |
|---|---|---|
| [`/dbt-wiki:init`](skills/init/) | Once per project (idempotent re-run safe) | `target/manifest.json` + `target/compiled/**/*.sql` (sqlglot column lineage) + `dbt/models/**/*.sql` (raw — for inline SQL/jinja comments) |
| [`/dbt-wiki:refresh`](skills/refresh/) | After `dbt parse` / `dbt compile` / `dbt run` when models changed | Diff against last `manifest_sha`; updates only changed pages; preserves user-owned `## User Notes` sections |
| [`/dbt-wiki:ingest`](skills/ingest/) | Whenever you want to capture context that's NOT in manifest.json or schema.yml (gotchas, design rationale, ticket links) | Free-form text arg; auto-attaches to mentioned model / source / macro |
| [`/dbt-wiki:query`](skills/query/) | Whenever asking about dbt model structure / lineage / columns / tribal knowledge | `.dbt-wiki/index.md` + relevant model pages; with optional drift verification |

## Quick start

1. Install via the [monkey-skills marketplace](https://github.com/kouko/monkey-skills)
2. Install sqlglot in your dbt env: `pip install sqlglot`
3. In your dbt project root:
   ```bash
   dbt parse        # generates target/manifest.json
   dbt compile      # generates target/compiled/**/*.sql (jinja-expanded; sqlglot needs this)
   ```
4. Then in Claude Code:
   ```
   /dbt-wiki:init
   ```
5. After your next dbt change:
   ```bash
   dbt parse && dbt compile
   ```
   then
   ```
   /dbt-wiki:refresh
   ```
6. (Optional) Capture tribal knowledge that's not in manifest.json or schema.yml:
   ```
   /dbt-wiki:ingest "fct_orders sort_key is (order_date, customer_id) because Tableau extract joins on these — see incident #4521"
   /dbt-wiki:ingest "marts_msd needs prod_marts_readonly_group permission grant before incremental run"
   ```
7. Ask anything:
   ```
   /dbt-wiki:query "fct_orders 依賴什麼？"
   /dbt-wiki:query "rename stg_customers.email 會影響哪些 model？"
   /dbt-wiki:query "marts_msd 下哪些是 incremental？"
   /dbt-wiki:query "fct_orders sort key 為什麼這樣設？"      # answers from ingested context
   ```

## What `init` produces

```
.dbt-wiki/
  SCHEMA.md              # frozen schema (do not edit)
  index.md               # catalog: by tier / materialization / tag / group
  log.md                 # append-only operation log
  lineage.md             # full DAG (ASCII tree + adjacency list)
  models/<name>.md       # one per model: frontmatter (materialization, columns
                         #   with sqlglot-extracted sources, depends_on, feeds_into,
                         #   tests) + body (description, SQL preview, inline SQL/jinja
                         #   comments with line numbers, column chains, user notes)
  sources/<src>__<table>.md  # one per declared source
  macros/<name>.md       # one per macro used by ≥1 model
  seeds/, snapshots/, tests/, exposures/   # one per resource
  _internal/extract_column_lineage.py      # sqlglot helper (init copies from plugin)
  _internal/extract_sql_comments.py        # regex helper for inline SQL/jinja comments
  _archive/<date>/       # orphaned models from refresh (never hard-deleted)
```

## Column-level lineage (the distinguishing feature)

dbt's `manifest.json` gives you **model-level** lineage (`fct_orders` depends on `stg_orders`) but not **column-level** lineage (`fct_orders.customer_id` comes from `stg_orders.customer_id`).

dbt-wiki adds the second by parsing `target/compiled/<project>/**/*.sql` (jinja already expanded by `dbt compile`) with sqlglot in your warehouse's dialect:

```yaml
columns:
  - name: customer_id
    description: "FK to dim_customers"
    tests: [not_null]
    sources:
      - "stg_orders.customer_id"
      - "stg_customers.id"  # via COALESCE
```

This unlocks queries dbt's manifest alone can't answer:
- `"fct_orders.customer_id 從哪來？"` → traces back through compiled SQL
- `"rename stg_customers.email 會影響哪些 model 的哪些 column？"` → reverse traversal across `columns[].sources`
- `"哪些 model 用了 ROW_NUMBER() OVER (...)？"` → sqlglot AST scan
- `"schema.yml 漏寫的 column"` → diff sqlglot SELECT list vs schema.yml `columns:`

## Coexistence with [`repo-wiki`](../repo-wiki/)

If both plugins are installed in the same repo, they coexist cleanly:

- **`.dbt-wiki/`** = STRUCTURE + COLUMN LINEAGE (auto-derived from manifest + sqlglot)
- **`.repo-wiki/`** = WHY (decisions, refactor history, tribal knowledge — manual ingest)

Cross-link freely:
```markdown
<!-- in .dbt-wiki/models/fct_orders.md -->
WHY: see [.repo-wiki/sources/2026-04-29-fsd-management-report-...](../.repo-wiki/sources/...)

<!-- in .repo-wiki/entities/DbtModels.md -->
For current dependencies of fct_orders, see [fct_orders](.dbt-wiki/models/fct_orders.md)
```

CLAUDE.md drop-ins use distinct markers (`<!-- dbt-wiki:start --> ... <!-- dbt-wiki:end -->` vs `<!-- repo-wiki:start --> ... <!-- repo-wiki:end -->`) so neither overwrites the other.

## Why not other tools

| Tool | Gap |
|---|---|
| dbt Cloud Discovery API | Paid subscription required |
| dbt docs generate + serve | HTML, not LLM-queryable |
| dbt-mcp + CLI only | LLM parses `dbt list` stdout; no structured query |
| dbt-mcp + Discovery | Requires dbt Cloud (paid) |
| dbt-osmosis / dbt-coves | Code generation, not query |
| Direct manifest.json read | 1-50 MB; no query interface; no column lineage |
| repo-wiki | WHY-first; doesn't do per-model WHAT or column lineage |
| General code search (Greptile, Cursor) | Code-aware, not dbt-aware |

`dbt-wiki`'s unique combination: **local-only + manifest.json structured truth + sqlglot column lineage + LLM-queryable + zero warehouse calls + works in Claude Code (not just Desktop)**.

## Design principles

1. **manifest.json + compiled SQL are source of truth** — never re-derive what dbt already parsed
2. **Always parse `compiled/*.sql`, never `raw_code`** — jinja must be expanded by dbt first
3. **Local-only** — no Cloud, no warehouse calls (catalog.json optional Phase 2)
4. **Refresh is idempotent** — diff `manifest_sha`, update only changed pages
5. **Archive, never delete** — orphaned models go to `.dbt-wiki/_archive/<date>/`
6. **Drift-aware queries** — query checks `manifest_sha` against current; warns if stale
7. **Coexist with repo-wiki** — STRUCTURE here, WHY there; cross-link freely

## Pre-conditions

- **dbt project**: any version supported by your dbt installation (`manifest.json` schema v9+ recommended)
- **`dbt parse && dbt compile`** must run before `init` / `refresh`
- **Python 3.x** + **sqlglot** (`pip install sqlglot`) — for column lineage extraction
- **Dialect support**: sqlglot supports redshift / postgres / snowflake / bigquery / databricks / clickhouse / duckdb / mysql / oracle / spark / sqlite / tsql — auto-detected from `dbt_project.yml` profile or override

## Schema is frozen until v2.0

`.dbt-wiki/SCHEMA.md` page types, frontmatter shape, and naming conventions will not change within the v1.x line. Major schema changes ship in v2.0 with a migration script.

## v2 backlog

- `catalog.json` integration (real warehouse column types, row counts) — opt-in Phase 2 read
- `run_results.json` integration (test pass/fail status, last-run timing)
- Dialect-specific edge case handling (Redshift late-binding views, Snowflake special functions)
- Cross-project lineage (when `packages.yml` pulls dbt-utils etc., trace into their macros)
- `/dbt-wiki:diff <ref>` — compare DAG between git refs (refactor review)
- Alternative parsers (sqlfluff, dbt-column-lineage adapter) when sqlglot fails

## Inspiration & credits

- [dbt-labs/dbt-core](https://github.com/dbt-labs/dbt-core) — manifest.json schema is the canonical structured truth
- [tobymao/sqlglot](https://github.com/tobymao/sqlglot) — column-lineage extraction wouldn't be feasible without it
- [`repo-wiki`](../repo-wiki/) — sibling plugin; SKILL.md / SCHEMA.md / log.md conventions reused
