# dbt-wiki Schema (v2.0 — frozen for v2.x)

This schema is **frozen for the v2.x line**. Frontmatter shape, page
types, naming conventions, and mandatory body sections will not change
within v2.x patches; only wording clarifications are allowed. *Additive
optional body sections* (sections that appear only under a stated
condition and change no existing required section's semantics) may be
added within v2.x — they neither break existing pages nor alter the
frontmatter/page-type/naming contract.

**Clean break from v1.x — no migration.** v2.0 is a breaking redesign:
dbt object types (model / source / macro / …) are demoted from *the
subject of distillation* to *structural evidence* that supports a new
**knowledge layer** (entities / metrics / concepts). There is **no
migration script**. A v1.x `.dbt-wiki/` is **rebuilt from scratch**,
not migrated — `git mv` relocation, layout sniffing, and cross-location
User-Notes preservation are intentionally **not** implemented (YAGNI;
plugin is early, no loaded deployments). The only guard rail: if `init`
detects a v1.x `.dbt-wiki/` that contains User Notes, it prints **one
warning** (recommending a backup before rebuild) — it does not preserve
or migrate that content.

## Positioning

**dbt-wiki = the semantic *knowledge* about the data (knowledge layer,
LLM-distilled), supported by structural *evidence* (evidence layer,
mechanical — manifest.json + sqlglot).**

The knowledge layer is the subject; structural lineage is its
footnote. An analyst should be able to ask "what does churn mean?",
"which entities relate to revenue?", or "how is this metric
calculated?" in **business language** and get an answer distilled from
the project — without first reading 200 models' SQL. The evidence
layer (the old v1.x mechanical pipeline) is preserved verbatim
underneath `_evidence/` because it is both the existing deterministic
value *and* the best raw material the LLM distills from.

## Architecture

This knowledge base has the following layers:

- **Knowledge layer** (`entities/`, `metrics/`, `concepts/`) — the
  subject. LLM-distilled business meaning. Each page is derived from
  one or more evidence pages (`derived_from:`) and cites them in an
  `## Evidence` section. Non-deterministic; freshness is tracked via
  `derived_from` + `last_changed_by` provenance.
- **Evidence layer** (`_evidence/models/`, `_evidence/sources/`, …) —
  the support. Mechanical extraction (manifest.json + sqlglot +
  `manifest_sha` drift detection). This is the **unchanged v1.x
  pipeline**, only relocated under `_evidence/`. Deterministic.

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
- **`.dbt-wiki/`** — Wiki layer. Owned entirely by dbt-wiki skills. **Located
  at the git repo root** (same level as `.git/` and `CLAUDE.md`), regardless
  of where the dbt project subdir lives or where the user invoked the skill
  from. Falls back to `$PWD` if not in a git repo. Holds both the
  knowledge layer (`entities/`, `metrics/`, `concepts/`) and the
  evidence layer (`_evidence/…`). Humans read via `/dbt-wiki:query`.
  Do not edit directly. (Enforced by repo-root CLAUDE.md drop-in.)
- **`.dbt-wiki/SCHEMA.md`** — Schema layer (this file).

### Coexistence with `.repo-wiki/`

If `.repo-wiki/` exists in the same repo, both directories are independent
and complementary:

- **dbt-wiki** = **WHAT the data *means*** — semantic knowledge
  (entities / metrics / concepts, LLM-distilled) plus the structural
  evidence (manifest.json + sqlglot) that supports it.
- **repo-wiki** = **WHY** — decisions, refactor history, tribal
  knowledge.

The two stay complementary and cross-link freely: a repo-wiki entity
can link to a dbt-wiki knowledge page, and a dbt-wiki page can cite a
repo-wiki decision. Examples:
`[Customer](.dbt-wiki/entities/customer.md)` /
`[fct_orders evidence](.dbt-wiki/_evidence/models/fct_orders.md)` from a
repo-wiki page; `[FSD report decision](../.repo-wiki/sources/2026-04-29-fsd...md)`
from a dbt-wiki page.

Neither directory modifies the other. The dbt-wiki CLAUDE.md drop-in
uses its own markers (`<!-- dbt-wiki:start --> ... <!-- dbt-wiki:end -->`)
so it never collides with a repo-wiki drop-in in the same repo.

### Freshness

The **evidence layer** is a derived snapshot of `target/manifest.json` +
parsed compiled SQL. It can drift if `dbt parse` / `dbt compile` is
re-run after changes — the query workflow checks `manifest_sha` mtime
against the snapshot and warns if drift is detected. Run
`/dbt-wiki:refresh` after every `dbt parse` to refresh evidence and
flag affected knowledge pages stale (via each knowledge page's
`derived_from:` overlap with the changed evidence models — same
mechanism as `syntheses` `affected_models`).

## Directory Layout

The knowledge layer (`entities/`, `metrics/`, `concepts/`) sits at the
top; the evidence layer is demoted under `_evidence/` (it was top-level
in v1.x).

```
.dbt-wiki/
  SCHEMA.md            # This file
  index.md             # Knowledge-first index (by entity / metric; structural grouping demoted)
  log.md               # Append-only operation log
  entities/            # KNOWLEDGE layer (LLM-distilled): one page per business object
  metrics/             #   one page per business measure
  concepts/            #   one page per cross-cutting business rule
  _evidence/           # EVIDENCE layer (mechanical: manifest + sqlglot — demoted, was top-level)
    models/            #   One page per dbt model
    sources/           #   One page per declared dbt source
    macros/            #   One page per macro (only those used by ≥1 model)
    seeds/             #   One page per seed
    snapshots/         #   One page per snapshot
    tests/             #   One page per generic test (singular tests only — schema.yml tests inline in model page)
    exposures/         #   One page per declared exposure (optional)
  lineage.md           # Full DAG (model-to-model) visualization (evidence-derived)
  syntheses/           # Saved query answers (auto-saved by /dbt-wiki:query for lineage classes;
                       #   marked stale by /dbt-wiki:refresh when affected_models change)
  _internal/           # Internal extraction artifacts (e.g. recursive column-lineage JSONL)
  _archive/            # Archived (orphaned) pages — never hard-deleted
```

Note: per Anthropic skill convention the *skill bundle* must stay flat
(no subfolder-of-subfolder). That rule governs the skill source tree;
it does **not** apply to the generated `.dbt-wiki/` output tree in a
user's repo, where `_evidence/models/` (one level of nesting) is the
intended layout.

## Knowledge Page Types

The knowledge layer has **three** page types — `knowledge-entity`,
`knowledge-metric`, `knowledge-concept`. They are the subject of v2.0:
LLM-distilled business meaning, each derived from one or more evidence
pages and citing them. (`domains/` is a deliberate fast-follow, not in
v2.0.)

### Shared provenance frontmatter

All three knowledge page types carry the same provenance fields. These
drive freshness / stale-detection on refresh:

```yaml
---
type: knowledge-entity            # or knowledge-metric | knowledge-concept
title: Customer                   # human-readable business name
status: developing                # lifecycle: seed → developing → mature → archived
summary: "..."                    # ≤200 chars — one-line business meaning (used by tiered query)
updated: 2026-06-01               # YYYY-MM-DD this page was last distilled/edited
derived_from:                     # evidence model unique_ids this page was distilled from.
  - model.example_dbt_project.stg_customers     # refresh diffs these against the changed
  - model.example_dbt_project.dim_customers     # evidence set to detect stale knowledge pages
relationships:                    # typed edges — see "## Relationships spec" below
  - type: depends_on              # edge type
    target: order.md              # relative to THIS page's folder (NO [[wikilinks]])
    note: "shares customer_id join key"
last_changed_by: "PR #123"        # commit SHA or PR that last re-distilled this page (provenance)
tags: ["finance"]
stale: false                      # set true by refresh when a derived_from evidence model changes
stale_at: null                    # YYYY-MM-DD refresh flagged it (else null)
stale_reason: null                # human-readable why (else null)
---
```

- **`status`** lifecycle: `seed` (auto-stub, not yet distilled) →
  `developing` (distilled, needs review) → `mature` (reviewed,
  trusted) → `archived` (entity no longer exists in evidence).
- **`summary`** is capped at **200 chars** so tiered query can read it
  without loading the full body.
- **`derived_from`** is the freshness anchor: on refresh, if any listed
  evidence `unique_id` is in the changed set, this page is flagged
  stale (reusing the `syntheses` `affected_models` overlap logic).
- **`last_changed_by`** records the commit/PR that last re-distilled
  the page — provenance for "why did this page change?".
- **`relationships[].target`** is a relative markdown-link target
  **resolved from the page's own file location**: a sibling knowledge
  page in the *same* folder is a bare slug (`order.md` from an entity
  page); a cross-folder target prefixes `../<folder>/<slug>.md` (e.g.
  `../entities/customer.md` from a metric page — see the
  metrics→entity example under "## Relationships spec"). This keeps
  the convention identical across the entity / metric / concept
  examples so generated links never double a path segment.
- **`stale` / `stale_at` / `stale_reason`** mirror the `synthesis`
  staleness contract — refresh writes these when a `derived_from`
  evidence model changes (T7 writes against this shape).

### knowledge-entity
File: `.dbt-wiki/entities/<entity_slug>.md`

A **business object** (Customer, Order, Subscription) — typically spans
multiple evidence models across `stg → int → mart`.

Frontmatter: the shared provenance block above with
`type: knowledge-entity`.

Body sections:

```markdown
## Summary
<plain-language: what this entity is, in business terms>

## Grain
<what one row represents — e.g. "one customer account">

## Fields
<plain-language column dictionary — what each meaningful field MEANS in
business terms. The glossary lives HERE (not a separate folder): each
row maps a field to its business meaning. Cite evidence columns.>

## Relationships
<typed edges to other knowledge pages — see "## Relationships spec".
Standard markdown links only, NO [[wikilinks]]. e.g.
- depends_on → [Order](order.md) — shares `customer_id` join key>

## Caveats
<data-quality notes: test coverage, known gaps, nullability surprises.
Sourced from the evidence layer's dbt tests (columns[].tests /
generic_tests).>

## Evidence
<cite the _evidence/ pages this entity was distilled from. e.g.
- [stg_customers](../_evidence/models/stg_customers.md)
- [dim_customers](../_evidence/models/dim_customers.md)>
```

### knowledge-metric
File: `.dbt-wiki/metrics/<metric_slug>.md`

A **business measure** (MRR, churn, LTV). If the project has a dbt
Semantic Layer (MetricFlow) definition for this metric, that definition
is the **authoritative input** — ingest it, do not re-derive.

Frontmatter: the shared provenance block with `type: knowledge-metric`.

Body sections:

```markdown
## Definition
<plain-language: what this metric measures and why it matters>

## Calculation
<the algorithm in plain language — how it's computed, the grain it's
computed at, edge cases. Cite the aggregation SQL in evidence.>

## Materialized Columns
_(Optional — include ONLY when the metric's variants are pre-materialized
into mart columns: values are already computed and a consumer can SELECT
the right column directly instead of re-aggregating with GROUP BY.
Omit this section entirely for metrics that still require query-time
aggregation. Does NOT go into frontmatter — body-only by design.
This section enriches the existing single page; it does NOT create a
new page type and does not break the "one metric = one page" principle.)_

A markdown table mapping **period/segment variant → physical `model.column` + grain**:

| Variant | Model | Column | Grain |
|---------|-------|--------|-------|
| <e.g. MTD> | <mart_model> | <column_name> | <e.g. day × store> |
| ... | ... | ... | ... |

When columns follow a regular naming pattern (e.g. `gmv_{period}_{segment}`),
capture the **pattern + allowed dimension values** rather than enumerating
every column. Enumerate individually only when naming is irregular.

See `references/distill-metrics.md` for the production procedure:
materialization detection signals, forest-compression rules, and a
worked example.

## Caveats
<data-quality / coverage caveats, sourced from evidence-layer tests>

## Relationships
<typed edges:
- measures → [Customer](../entities/customer.md) — GROUP BY grain
- depends_on → [Active Customer](../concepts/active-customer.md) — algorithm dependency>

## Evidence
<cite the _evidence/ model(s) this metric is computed in>
```

### knowledge-concept
File: `.dbt-wiki/concepts/<concept_slug>.md`

A **cross-cutting business rule** encoded in SQL but not owned by any
single entity (e.g. "active customer = ordered in last 90 days",
fiscal-year definition, status enumerations).

Frontmatter: the shared provenance block with `type: knowledge-concept`.

Body sections:

```markdown
## Rule
<plain-language definition of the business rule>

## Applies To
<where this rule shows up — which entities / metrics / models encode it>

## Relationships
<typed edges:
- applies_to → [Customer](../entities/customer.md)
- applies_to → [Churn](../metrics/churn.md)>

## Evidence
<cite the _evidence/ pages where the CASE/WHERE logic lives>
```

## Relationships spec (typed-edge ontology)

Knowledge pages form a **lightweight ontology / knowledge graph**: each
page carries typed edges, expressed BOTH as `relationships:` frontmatter
(machine-readable) and as a body `## Relationships` section
(human-readable). The LLM infers edges from lineage + SQL semantics.

**Edges use standard markdown links — `[[wikilinks]]` are banned** in
dbt-wiki (see "What dbt-wiki NEVER does").

Edge types:

| `type` | From → To | Inferred from |
|---|---|---|
| `depends_on` | entity → entity (directional) | the FROM entity holds a FK to the TO entity (child → parent). Emit on the FK-holder side. |
| `joins` | entity ↔ entity (navigational) | a query-time join with no clear ownership direction, OR the parent-side reverse edge of a one-to-many (optional, for graph navigability). **NOT a synonym of `depends_on`** — use `depends_on` whenever an ownership direction is clear. |
| `converts_to` | entity → entity (lifecycle) | the FROM entity transitions INTO the TO entity via a conversion FK (e.g. a Lead's `converted_opportunity_id` — a converted lead *becomes* an opportunity). One-directional and usually conditional (`WHERE is_converted`). |
| `measures` | metric → entity | the GROUP BY grain the metric aggregates over |
| `depends_on` | metric → concept | algorithm dependency (metric uses a rule) |
| `applies_to` | concept → entity / metric | the rule is encoded in that entity/metric |
| `evidence` | any knowledge page → `_evidence/…` | the page was distilled from that evidence |

Frontmatter shape (each edge):

```yaml
relationships:
  - type: measures
    target: ../entities/customer.md     # relative markdown-link target
    note: "GROUP BY customer_id grain"  # optional one-line rationale
```

**Dangling edge targets (FK points to an un-distilled entity).** When an
edge target entity has NO model in the current evidence slice (e.g. a
`converted_contact_id` FK whose Contact entity isn't distilled yet), still
emit the edge AND create a `status: seed` stub page for the target
(`derived_from: []`, a one-line body noting it is an auto-stub) so the
markdown link resolves. The next init/refresh that distills the target
promotes the stub `seed → developing`. Never drop an edge just because its
target page doesn't exist yet.

The `## Evidence` body section is the human-facing rendering of the
`evidence`-type edges; `derived_from:` frontmatter is its machine-facing
twin (and the freshness anchor).

**Do NOT double-encode evidence edges.** The `evidence` edge type lives
ONLY in `derived_from:` (frontmatter) + the `## Evidence` body section —
it is **never** added as a `relationships:` list entry. `relationships:`
carries only knowledge→knowledge edges (`depends_on` / `joins` /
`measures` / `applies_to`). This keeps T3/T4/T5 from emitting the same
evidence link in two places and drifting.

## Evidence Page Types

> These are the **unchanged v1.x** mechanical page types, relocated
> under `_evidence/`. Frontmatter and body specs below are identical to
> v1.x **except the file location** (`.dbt-wiki/models/…` →
> `.dbt-wiki/_evidence/models/…`, and likewise for sources / macros /
> seeds / snapshots / tests / exposures). They are the deterministic
> support for the knowledge layer and the raw material it distills from.

### model
File: `.dbt-wiki/_evidence/models/<model_name>.md`

Filename: `model_name` from `manifest.json` (no path prefix; collisions
disambiguated with `<package>__<model>` form).

Frontmatter:

```yaml
---
unique_id: model.example_dbt_project.fct_orders     # manifest.json node id
type: model
package: example_dbt_project
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

## Column Sources (from sqlglot — direct, single-hop)
- order_id ← stg_orders.order_id
- customer_id ← stg_orders.customer_id, stg_customers.id (COALESCE)

## Column Lineage Chains (recursive, full DAG)
> Auto-generated from `extract_recursive_column_lineage.py`. Each entry
> shows the full ancestor chain (back to source) and descendant chain
> (forward to leaf marts) for every column in this model.

### customer_id
**Ancestors** (where this column comes from, recursively):
- ← stg_orders.customer_id
  - ← raw_data.orders_raw.customer_id  *(source)*
- ← stg_customers.id  *(via COALESCE)*
  - ← raw_data.customers_raw.id  *(source)*

**Descendants** (where this column flows to, recursively):
- → dim_orders_summary.customer_id
  - → mart_finance_daily.customer_id  *(leaf)*

(Resolved nodes appear as `<model_name>.<column>`. Unresolved table
references — CTEs, SQL aliases sqlglot couldn't back-resolve, dbt_utils
macro outputs — appear as `_unresolved::<table>::<column>` and stop
recursion at that point.)

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
Notes, SQL Preview, Inline Comments, Column Sources, Column Lineage Chains,
Tests, Cross-references.

**User-owned sections** (init/refresh PRESERVE verbatim): User Notes,
plus any `##`-level heading the user added that isn't in the standard list.

### source
File: `.dbt-wiki/_evidence/sources/<source_name>__<table_name>.md`

Frontmatter:

```yaml
---
unique_id: source.example_dbt_project.raw_data.orders_raw
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
File: `.dbt-wiki/_evidence/macros/<macro_name>.md`

Only macros referenced by ≥1 model get a page (init filters by usage count).

```yaml
---
unique_id: macro.example_dbt_project.parse_currency
type: macro
package: example_dbt_project                           # or external package name (e.g., dbt_utils)
path: dbt/macros/parse_currency.sql
arguments: [amount, currency_code]                   # from manifest macro signature
description: "..."                                   # from schema.yml or docstring
used_by_models: [fct_orders, fct_revenue, ...]      # init computes
last_updated: 2026-05-02
---
```

### seed / snapshot / test / exposure
Files: `.dbt-wiki/_evidence/seeds/…`, `.dbt-wiki/_evidence/snapshots/…`,
`.dbt-wiki/_evidence/tests/…`, `.dbt-wiki/_evidence/exposures/…`.

Same pattern: one page per resource. Frontmatter mirrors manifest fields,
plus `feeds_into` (for seed/snapshot) or `tests_resource` (for tests) etc.

### synthesis
File: `.dbt-wiki/syntheses/<question-slug>.md`

Auto-saved by `/dbt-wiki:query` for lineage-class queries (C2/C3/C4/C9/C10).
Captures the question, the answer (with inline citations), ASCII tree +
Mermaid diagram, and the manifest_sha + affected_models needed for stale
detection by `/dbt-wiki:refresh`.

Frontmatter (full template in `assets/synthesis_template.md`):

```yaml
---
type: synthesis
question: "<exact question>"             # so re-query is verbatim
slug: <kebab-case slug>
date: <YYYY-MM-DD>
manifest_sha: <sha at time of save>      # used by refresh for stale detection
affected_models:                         # critical: enables PRECISE stale detection
  - <model.proj.X>                       # if any of these change in a future
  - <model.proj.Y>                       # refresh, this synthesis gets marked stale
query_class: <C1-C11 | K1-K3>            # structural (C*) OR knowledge/semantic (K*) class
diagram_included: <yes | no>
sources_consulted:                        # may mix knowledge + evidence pages
  - entities/<name>.md                    # knowledge-layer page (when a K-class query)
  - _evidence/models/<name>.md            # evidence-layer backing page
verification_run: <yes | no>
verified_paths: []
stale: false                             # set true by refresh when affected_models change
stale_at: null
stale_reason: null                       # human-readable why
---
```

Body sections:

```markdown
<!-- IF stale: refresh prepends a banner here so it's the FIRST thing user sees -->

## Question
<verbatim>

## Answer
<synthesized answer with inline citations>

## Lineage Diagrams
### ASCII Tree
\```
<format_lineage_diagram.py output>
\```

### Mermaid (renders in IDE preview / GitHub / Obsidian)
\```mermaid
<format_lineage_diagram.py output>
\```

## Sources Consulted
- [<page>](.dbt-wiki/_evidence/<type>/<page>.md)
```

**Stale lifecycle**: refresh's Step 6.5 checks each non-archived synthesis.
If any `affected_models` overlap the refresh's added/modified/removed
sets, mark `stale: true` + prepend banner. Original answer + diagrams
preserved (non-destructive). User re-runs `/dbt-wiki:query` to regenerate
with fresh content (overwrites synthesis, clears stale flag).

## Index, Lineage, Log

### index.md
**Knowledge-first** catalog. The knowledge layer leads; structural
grouping is demoted into an evidence section. Sections, in order:

Knowledge layer (lead):
- `## Entities` (one line per entity: title + `summary` + status)
- `## Metrics` (one line per metric: title + `summary` + status)
- `## Concepts` (one line per concept: title + `summary` + status)

Evidence layer (demoted — structural grouping):
- `## Evidence: Models` (grouped by tier path: `models/staging/`, `models/marts/`, etc.)
- `## Evidence: Models by Materialization` (table / view / incremental / ephemeral)
- `## Evidence: Models by Tag`
- `## Evidence: Models by Group`
- `## Evidence: Sources`
- `## Evidence: Macros (used)`
- `## Evidence: Seeds / Snapshots / Tests / Exposures`

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

**Evidence pages** (`_evidence/…`) — follow dbt convention (underscores):

- Model file = `<model_name>.md` (no prefix). If two packages have a `customers` model,
  filename becomes `<package>__<model_name>.md` (e.g., `example_dbt_project__customers.md`).
- Source file = `<source_name>__<table_name>.md` (always 2-part, no collision risk).
- Macro file = `<macro_name>.md` for project macros, `<package>__<macro>.md` for external (dbt_utils, etc.).
- Slug rule: lowercase, underscores preserved (matching dbt convention).

**Knowledge pages** (`entities/`, `metrics/`, `concepts/`) — use
**kebab-case** slugs (lowercase, hyphen-separated), deliberately
*different* from evidence-page underscores so a link's casing signals
which layer it points at. The slug derives from the business `title`,
not a dbt object name. Examples: `customer.md`, `active-customer.md`
(the concept page referenced in the metrics→concept example),
`monthly-recurring-revenue.md`.

## Refresh Idempotency Contract

When `/dbt-wiki:refresh` runs:

1. Compare new `manifest_sha` to log.md's most recent `manifest_sha`. Skip if identical.
2. For each model in new manifest:
   - If `unique_id` exists in `.dbt-wiki/_evidence/models/`: diff frontmatter; rewrite if changed.
   - If new: create page.
3. For each model in `.dbt-wiki/_evidence/models/` not in new manifest: append `removed: true`
   to frontmatter, move to `.dbt-wiki/_archive/<date>-<model>.md` (don't hard-delete).
4. Recompute `lineage.md` and `index.md` from scratch.
5. Flag affected knowledge pages stale: for each non-archived page in
   `entities/` / `metrics/` / `concepts/`, if any `derived_from:`
   evidence `unique_id` is in the added/modified/removed set, mark it
   stale (same overlap logic as `syntheses` `affected_models`). v2.0
   MVP only flags; auto re-distill is a fast-follow.
6. Append refresh entry to `log.md`.

## What dbt-wiki NEVER does

- Modify `dbt/`, `target/`, or any source file
- Hard-delete `.dbt-wiki/` pages (always archive)
- Run `dbt parse` / `dbt compile` on user's behalf (user runs explicitly; init checks for output)
- Connect to dbt Cloud, warehouse, or any external API
- Mutate `manifest.json` or any `target/` file
- Use `[[wikilinks]]` — only standard markdown links

## Coexistence with repo-wiki

See "### Coexistence with `.repo-wiki/`" under **Architecture** above
(the WHAT-the-data-means vs WHY split, free cross-linking, independent
non-modification, and the `<!-- dbt-wiki:start ... -->` CLAUDE.md
markers).
