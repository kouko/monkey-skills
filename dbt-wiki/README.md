# dbt-wiki

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Local-only LLM-queryable knowledge base for dbt projects. A **two-layer** system: a **knowledge layer** (`entities/`, `metrics/`, `concepts/`) of LLM-distilled business meaning, supported by an **evidence layer** (`_evidence/`) of mechanical extractions from `target/manifest.json` + [sqlglot](https://github.com/tobymao/sqlglot) column-level lineage. Query answers semantic questions ("what does churn mean?", "which entities relate to revenue?") alongside structural lineage questions — without dbt Cloud, without leaving your machine.

**Version**: 2.4.0 · **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) · **License**: MIT

## Background

dbt has excellent first-party docs (`dbt docs generate` → static HTML site) and an ecosystem of paid tools (dbt Cloud Discovery API, third-party lineage platforms). But for **understanding what the data means** — in business language, without reading 200 models' SQL — there's a deeper gap:

- **dbt Cloud Discovery API** — structural metadata + lineage, but paid subscription required; no business-meaning distillation
- **dbt docs serve** — HTML for humans; surfaces resource structure, not semantic knowledge
- **`target/manifest.json`** — the structured truth, but 1-50 MB raw; no query interface; no business semantics
- **dbt-mcp without Discovery** — only exposes CLI tools; LLM has to parse `dbt list` stdout
- **General-purpose code search (Greptile, Cursor @Codebase)** — code-aware, not dbt-aware; misses lineage and column relationships
- **Business glossaries / data catalogs** (Atlan, DataHub) — auto-crawl metadata well, but semantic layer stays shallow (structure, not meaning)

`dbt-wiki` fills the gap: a **local-only**, **two-layer knowledge base** derived from dbt artifacts your project already produces (no warehouse calls, no Cloud subscription). The **knowledge layer** (`entities/`, `metrics/`, `concepts/`) is LLM-distilled business meaning — answering "what does churn mean?", "which entities relate to revenue?", "how is MRR calculated?" The **evidence layer** (`_evidence/`) is the unchanged mechanical pipeline (manifest + sqlglot column lineage) that the knowledge layer is distilled from and cites.

## Skills

| Skill | When | Primary input |
|---|---|---|
| [`/dbt-wiki:init`](skills/init/) | Once per project (idempotent re-run safe) | `target/manifest.json` + `target/compiled/**/*.sql` (sqlglot column lineage) + `dbt/models/**/*.sql` (raw — for inline SQL/jinja comments) |
| [`/dbt-wiki:refresh`](skills/refresh/) | After `dbt parse` / `dbt compile` / `dbt run` when models changed | Diff against last `manifest_sha`; updates only changed pages; preserves user-owned `## User Notes` sections |
| [`/dbt-wiki:ingest`](skills/ingest/) | Whenever you want to capture context that's NOT in manifest.json or schema.yml (gotchas, design rationale, ticket links) | Free-form text arg; auto-attaches to mentioned model / source / macro |
| [`/dbt-wiki:query`](skills/query/) | Whenever asking semantic questions ("what does churn mean?", "which entities relate to revenue?") or structural lineage questions ("what does fct_orders depend on?", "which columns does stg_customers.email feed?") | `.dbt-wiki/index.md` + relevant knowledge and evidence pages; with optional drift verification |
| [`/dbt-wiki:pack`](skills/pack/) | When you want to **package the distilled knowledge base into a portable Agent Skill bundle** (`<project>-analytics/`) that another agent uses with its own warehouse-connect tool to ground + generate + execute SQL. Run by the project owner; the emitted bundle drops into any Skills-compatible agent. | The frozen `.dbt-wiki/` knowledge layer (entities / metrics / concepts + column cards + relationships + value domains); emits a flat skill folder (SKILL.md + knowledge/ + references/ + examples/) with a snapshot annotation |

## Quick start

1. Install via the [monkey-skills marketplace](https://github.com/kouko/monkey-skills)
2. Have **either** of the following — init auto-detects and uses whichever is present:
   - **[uv](https://github.com/astral-sh/uv)** (recommended — auto-installs sqlglot in an ephemeral env per script run, zero pollution of your dbt env): `brew install uv` (macOS) or `curl -LsSf https://astral.sh/uv/install.sh | sh` (Linux/macOS)
   - **OR** pip-installed sqlglot in your dbt env: `pip install 'sqlglot>=25.0'`
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
   # Semantic questions (answered from knowledge layer)
   /dbt-wiki:query "what does churn mean in this project?"
   /dbt-wiki:query "which entities relate to revenue?"
   /dbt-wiki:query "how is MRR calculated?"
   /dbt-wiki:query "what business rules apply to active customer?"

   # Structural lineage questions (answered from evidence layer)
   /dbt-wiki:query "fct_orders 依賴什麼？"
   /dbt-wiki:query "rename stg_customers.email 會影響哪些 model？"
   /dbt-wiki:query "marts_msd 下哪些是 incremental？"
   /dbt-wiki:query "fct_orders sort key 為什麼這樣設？"      # answers from ingested context
   ```

## What `init` produces

`init` runs in two phases: **Phase A** builds the evidence layer (mechanical extraction from manifest + sqlglot — deterministic), then **Phase B** distills the knowledge layer (LLM reads the evidence and extracts business meaning — non-deterministic, cited).

```
.dbt-wiki/
  SCHEMA.md              # frozen schema (do not edit)
  index.md               # knowledge-first catalog: entities / metrics / concepts lead;
                         #   structural grouping demoted to evidence section
  log.md                 # append-only operation log
  lineage.md             # full DAG (ASCII tree + adjacency list; evidence-derived)

  # KNOWLEDGE LAYER (LLM-distilled — Phase B)
  entities/<name>.md     # one per business object (Customer, Order, …)
                         #   business meaning, grain, field dictionary, typed relationships
  metrics/<name>.md      # one per business measure (MRR, churn, LTV, …)
                         #   definition, calculation algorithm, caveats
                         #   if dbt Semantic Layer / MetricFlow present: ingests it as authoritative input
  concepts/<name>.md     # one per cross-cutting business rule (active-customer, fiscal-year, …)
                         #   rule definition, where it applies, evidence citations

  # EVIDENCE LAYER (mechanical extraction — Phase A)
  _evidence/models/<name>.md      # one per dbt model: materialization, columns with
                                  #   sqlglot-extracted sources, depends_on, feeds_into, tests
  _evidence/sources/<src>__<table>.md  # one per declared source
  _evidence/macros/<name>.md      # one per macro used by ≥1 model
  _evidence/seeds/, snapshots/, tests/, exposures/   # one per resource

  syntheses/             # saved query answers (auto-saved for lineage + semantic queries)
  _internal/             # extraction helpers (sqlglot, recursive column lineage)
  _archive/<date>/       # orphaned pages from refresh (never hard-deleted)
```

Knowledge pages cite their evidence via `## Evidence` sections (standard markdown links) and `derived_from:` frontmatter. Refresh keeps evidence fresh and flags affected knowledge pages stale for re-distillation.

## Two layers working together

### Knowledge layer (primary) — LLM-distilled business meaning

The knowledge layer is the primary v2.0 addition — business meaning distilled by the LLM, not just a mechanical snapshot. When `init` runs Phase B, the LLM reads the evidence pages (models, columns, lineage, schema.yml descriptions) and distills:

- **`entities/`** — business objects like Customer or Order, spanning multiple dbt models across `stg → int → mart`. Each page includes a plain-language field dictionary (the glossary lives here, not a separate folder) and typed `## Relationships` edges to other knowledge pages — a lightweight ontology / knowledge graph.
- **`metrics/`** — business measures like MRR, churn, or LTV. Includes plain-language definition, calculation algorithm, and caveats. If the project has a dbt Semantic Layer (MetricFlow), that definition is ingested as the authoritative input; dbt-wiki does not re-derive it.
- **`concepts/`** — cross-cutting business rules encoded in SQL but not owned by any single entity (e.g. "active customer = ordered in last 90 days", fiscal-year definition, status enumerations).

Knowledge pages connect to each other via typed `## Relationships` edges (depends_on, joins, measures, applies_to) expressed as standard markdown links — no `[[wikilinks]]`. This typed-link graph is what lets query answer "which entities relate to revenue?" or "what concepts apply to churn?".

### Evidence layer (supporting) — column-level lineage and structural extraction

The evidence layer is the unchanged mechanical pipeline, now living under `_evidence/`. It is both the existing deterministic value and the raw material the knowledge layer distills from.

dbt's `manifest.json` gives model-level lineage (`fct_orders` depends on `stg_orders`) but not column-level lineage. dbt-wiki adds the second by parsing `target/compiled/<project>/**/*.sql` (jinja already expanded by `dbt compile`) with sqlglot in your warehouse's dialect:

```yaml
columns:
  - name: customer_id
    description: "FK to dim_customers"
    tests: [not_null]
    sources:
      - "stg_orders.customer_id"
      - "stg_customers.id"  # via COALESCE
```

This unlocks structural lineage queries the manifest alone can't answer:
- `"fct_orders.customer_id 從哪來？"` → traces back through compiled SQL
- `"rename stg_customers.email 會影響哪些 model 的哪些 column？"` → reverse traversal across `columns[].sources`
- `"哪些 model 用了 ROW_NUMBER() OVER (...)？"` → sqlglot AST scan
- `"schema.yml 漏寫的 column"` → diff sqlglot SELECT list vs schema.yml `columns:`

Knowledge pages cite which `_evidence/` pages they were distilled from. Refresh detects when cited evidence changes and flags the knowledge page stale.

## Coexistence with [`repo-wiki`](../repo-wiki/)

If both plugins are installed in the same repo, they coexist cleanly and complement each other:

- **`.dbt-wiki/`** = **WHAT the data means** — semantic knowledge (entities / metrics / concepts, LLM-distilled) plus the structural evidence (manifest + sqlglot column lineage) that supports it
- **`.repo-wiki/`** = **WHY** — decisions, refactor history, tribal knowledge (manual ingest)

Cross-link freely:
```markdown
<!-- in .dbt-wiki/entities/customer.md (knowledge page) -->
Decision context: see [.repo-wiki/sources/2026-04-29-fsd-management-report-...](../.repo-wiki/sources/...)

<!-- in .dbt-wiki/_evidence/models/fct_orders.md (evidence page) -->
WHY: see [.repo-wiki/sources/2026-04-29-fsd-management-report-...](../.repo-wiki/sources/...)

<!-- in .repo-wiki/entities/DbtModels.md -->
For Customer entity knowledge, see [customer](.dbt-wiki/entities/customer.md)
For current fct_orders evidence, see [fct_orders](.dbt-wiki/_evidence/models/fct_orders.md)
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
| repo-wiki | WHY-first (decisions, history); doesn't do semantic knowledge or column lineage |
| General code search (Greptile, Cursor) | Code-aware, not dbt-aware; no business semantics |

`dbt-wiki`'s unique combination: **local-only + LLM-distilled knowledge layer (entities / metrics / concepts) + manifest.json structural evidence + sqlglot column lineage + semantic + structural queries + zero warehouse calls + works in Claude Code (not just Desktop)**.

## Design principles

1. **Knowledge layer is primary; evidence layer is its support** — analysts query business meaning first; structural lineage is the footnote that backs it
2. **manifest.json + compiled SQL are the evidence source of truth** — never re-derive what dbt already parsed; knowledge is distilled from evidence, not independently invented
3. **Always parse `compiled/*.sql`, never `raw_code`** — jinja must be expanded by dbt first
4. **Local-only** — no Cloud, no warehouse calls (catalog.json optional Phase 2)
5. **Refresh is idempotent** — diff `manifest_sha`, update only changed evidence pages; flag affected knowledge pages stale
6. **Archive, never delete** — orphaned pages go to `.dbt-wiki/_archive/<date>/`
7. **Drift-aware queries** — query checks `manifest_sha` against current evidence; warns if stale
8. **Coexist with repo-wiki** — WHAT-the-data-means here (semantic knowledge), WHY there (decisions); cross-link freely

## Pre-conditions

- **dbt project**: any version supported by your dbt installation (`manifest.json` schema v9+ recommended)
- **`dbt parse && dbt compile`** must run before `init` / `refresh`
- **Python 3.10+** AND either:
  - [uv](https://github.com/astral-sh/uv) (recommended — script self-declares sqlglot via PEP 723 inline metadata; uv auto-installs in ephemeral env), OR
  - pip-installed sqlglot in your active Python env (`pip install 'sqlglot>=25.0'`)
- **Dialect support**: sqlglot supports redshift / postgres / snowflake / bigquery / databricks / clickhouse / duckdb / mysql / oracle / spark / sqlite / tsql — auto-detected from `dbt_project.yml` profile or override

## Schema

`.dbt-wiki/SCHEMA.md` page types, frontmatter shape, and naming conventions are frozen for the v2.x line. v2.0 is a **clean break** from v1.x — there is no migration script; the wiki is rebuilt from scratch. If `init` detects a v1.x `.dbt-wiki/` containing User Notes, it prints one warning recommending a backup before rebuild.

## Backlog (fast-follow after v2.0 MVP)

- **`refresh` auto re-distillation** — when evidence changes, automatically re-distill affected knowledge pages (MVP flags stale; auto re-distill is fast-follow)
- **`ingest` → knowledge pages** — write ingested context directly into knowledge page `## User Notes` in addition to evidence pages
- **`domains/`** — topic-area landscape pages (finance / marketing / product) aggregating entities + metrics + concepts
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
