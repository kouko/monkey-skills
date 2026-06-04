# Changelog

All notable changes to the `dbt-wiki` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.5.0] — 2026-06-04

### Added — recall pack: SCHEMA v2.1 (additive-optional; v2.0 pages remain valid)

Four optional frontmatter keys added to the page contract; existing pages require
no changes.

- **`aliases`** — list of project-language synonyms, GL codes, and abbreviations
  for a model or entity (e.g. `[ARR, MRR, 月次経常収益]`). Distill agents
  auto-emit this field by extracting un-bridgeable project terms from page
  bodies; no human gate required. Index lines surface aliases so tiered query
  matches project-language terms directly.
- **`title_local`** — project-language title for the model or entity (parallel to
  the English `title`). Auto-emitted alongside `aliases`; fully automatic.
- **`reviewed_by`** / **`reviewed_at`** — review lifecycle markers (reviewer
  identity + ISO date). Workflow is deferred; keys are reserved in the schema now
  so pages written today are forward-compatible.

### Added — value-domain provenance marker

Value-domain lists now carry a `(via: accepted_values | distinct | inferred)`
provenance tag so text-to-SQL consumers can distinguish ground-truth enums
(sourced from dbt `accepted_values` tests or a live `DISTINCT` query) from
inferred values (extracted heuristically from column descriptions or sample rows).

### Changed — value-domain rule relaxed to permit-but-tag

The previous rule ("list only production values; omit hypotheticals") is relaxed
in both `SCHEMA.md` and `distill-entities.md §3.4`: inferred values are now
**allowed** when tagged `(via: inferred)`. Ground-truth values continue to be
preferred; the tag makes the epistemic status explicit rather than silently
excluding uncertain-but-useful entries.

## [2.4.0] — 2026-06-03

### Added — `pack`: export the knowledge base as a portable analytics skill

dbt-wiki is repositioned as a **knowledge / context layer**, not a query
engine. Real-data dogfood + an industry scan (Vanna, Wren AI, dbt MCP +
MetricFlow, dbt-labs' own agent skills) confirmed the differentiator is not
another NL→SQL engine but **portable curated knowledge** an agent can carry to
wherever it already has warehouse access. The new `/dbt-wiki:pack` skill freezes
the distilled `.dbt-wiki/` knowledge into a self-contained, portable Agent Skill
folder (`<project>-analytics/`) that a downstream agent uses **with its own
warehouse-connect tool** to ground, generate, execute, and iterate on SQL.

**New skill — `skills/pack/`** (owner-run packager):
- `SKILL.md` — 8-step packager: locate `.dbt-wiki/` → create the flat
  `<project>-analytics/` bundle → **freeze** the knowledge layer into a flat
  `knowledge/` (flatten-on-freeze: source nests, bundle stays flat) → copy the
  generation guidance → instantiate the bundle `SKILL.md` from the template →
  reserve `examples/` → write the snapshot annotation (source `manifest_sha` +
  build date + rebuild pointer) → verify the emitted folder is a flat valid skill.
- `references/bundle-format.md` — spec for the emitted bundle (flat-skill
  constraint, portability into `~/.claude/skills/`, on-demand knowledge, the
  snapshot-annotation block).
- `references/generation-guidance.md` — the to-sql semantic guardrails
  (aggregate form · join-grain / fan-out · value-grounding · source
  disambiguation · temporal) + schema-linking, **reframed for a
  warehouse-connected agent**: generate → execute via your own tool → inspect →
  iterate. **Execution is the only gate** — there is deliberately no static
  existence check (see Removed below for why).
- `assets/bundle-skill-template.md` — the emitted bundle's `SKILL.md` template
  (tool-agnostic 4-step consumption procedure; names no specific warehouse tool).

### Removed — the `to-sql` runtime shell (BREAKING)

`skills/to-sql/` is retired. Its never-execute, in-repo NL2SQL design was a half
solution (a generator that can't run its own output can't catch the semantic
errors that only execution reveals). Its semantic guardrails are preserved in
`pack/references/generation-guidance.md`. `/dbt-wiki:to-sql` no longer exists;
use `/dbt-wiki:pack` to export an analytics bundle and run SQL through your own
warehouse tool. README Skills tables (en / ja / zh-TW) updated; two stale
cross-references repointed (`SCHEMA.md`, `distill-entities.md`).

**The static SQL validator was dropped, not carried forward.** A synthetic
end-to-end pack dogfood surfaced that a static existence check (parse SQL → look
up tables/columns in a frozen schema) has no coherent home in a portable
**snapshot** bundle: the live warehouse drifts (columns added / renamed /
dropped) and the bundle does not auto-update, so a frozen check gives false
confidence (a dropped column still "exists" in the snapshot) or false errors (a
new column the snapshot never saw). It also could not see the dangerous
errors — semantically-valid wrong-number bugs — which only execution reveals.
The validator (`validate_sql.py` + its 16-case test, a relic of the
never-execute `to-sql` design) was therefore removed; `knowledge/` **grounds**
generation, execution **gates** it.

Pure spec/markdown; no warehouse driver in dbt-wiki itself (warehouse-agnostic
by design); all examples synthetic.

### Deferred (noted, not in this release)

- **Gold-example generation** into the bundle's reserved `examples/` slot.
- **`init` catalog.json / connect value_domain enrichment** (OQ-A mechanism).
- **A synthetic `acme-analytics/` demo bundle** (must live OUTSIDE `skills/` to
  avoid skill-in-skill nesting).

## [2.3.0] — 2026-06-02

### Added — to-sql semantic correctness guardrails (dogfood-driven)

Real-data dogfood (5 axes on a live warehouse) showed the to-sql static
validator (sqlglot parse + manifest existence) catches syntax + hallucination
but **not** semantic errors — valid SQL that returns the wrong number, which a
non-SQL user can't detect. Observed: aggregation form (avg-order-value 3x
divergence between `SUM/SUM` and `AVG(row-ratio)`), join-grain fan-out (84x row
inflation from a partial join key), value-grounding (a region/city filter using
the user's term instead of the stored code → 0 rows), and source ambiguity (the
same business term answerable by two tables with different figures). This
release closes those gaps in two layers.

**Prompt guardrails — `to-sql/references/prompt-assembly.md`** (added as §4
sub-sections; no renumber of §5–§8):
- **§4e Aggregate Semantics** — derived ratios/averages default to aggregate-level
  `SUM(num)/SUM(denom)`, never `AVG(row-ratio)`; prefer the metric page's
  `## Calculation` form; state the form used (§8i).
- **§4f Join Grain / Fan-out** — JOINs must use the full/compound grain key from
  the relationship edge's `note`; warn on grain mismatch; never `SUM` over
  fanned-out rows (§8j).
- **§4g Value Grounding** — categorical filters use the knowledge page's
  `value_domain` enum if present, else don't assume user-term = stored-value
  (`ILIKE`/assumption); record the mapping (§8g).
- **§4h Source Disambiguation** — when ≥2 sources answer the same term, surface
  both with their basis instead of silently picking (§8h).
- Wired into the §6 prompt template; §8 output contract gains assumption
  surfaces §8g–§8j (joining the existing §8e temporal / §8f NULL-ordering).

**Knowledge-layer capture (so the guardrails have authoritative data)**:
- `assets/SCHEMA.md` — Relationships spec now requires the edge `note` to record
  the **compound join key** (all key columns); knowledge-entity gains optional
  **`value_domain` capture** (body annotation, ≤20-distinct threshold) for small
  categorical columns.
- `init/references/distill-metrics.md` §5 — derived-ratio metrics MUST define
  their aggregation form (aggregate-level vs avg-of-row-ratios).
- `init/references/distill-entities.md` §3.4 — `## Fields` distillation captures
  `value_domain` for small categorical columns, aligned with SCHEMA.

Pure spec/markdown; no warehouse/execution; all examples synthetic. The static
validator itself also gained two same-family false-positive fixes earlier on
this line (SELECT-alias and CTE-name exclusion) with a regression-lock test set.

## [2.2.0] — 2026-06-02

### Added — `to-sql`: natural-language → SQL skill (NL2SQL part 1, zero-shot)

The first consumer skill that turns the knowledge base into actual queries.
`/dbt-wiki:to-sql` takes a natural-language **business question** and generates
a **runnable SQL query** grounded in the distilled knowledge — distinct from
`/dbt-wiki:query`, which *explains* the data (meaning + lineage). This is
part 1 (the in-repo runtime consumer) of the NL2SQL effort; a portable
packager that exports a standalone skill is a planned follow-up.

Architecture reuses what the knowledge base already provides — the schema is
already decomposed into semantic entities with summaries + a typed relationship
graph, so retrieval reuses `query`'s tiered loading rather than standing up a
vector store. Research backing (dbt Semantic Layer benchmark, RASL / SAFE-SQL):
business-vocabulary→physical-column mapping is the dominant NL→SQL accuracy
lever; the metric **column cards** (v2.1.0) feed this directly.

- **`skills/to-sql/SKILL.md`** — pipeline: pre-condition + `manifest_sha` drift
  check (reuses `query` Step 0) → retrieve schema context → assemble prompt →
  generate SQL (project's adapter dialect) → **static-validate** → present
  (SQL + cited knowledge pages + validation result + drift caveat).
- **`skills/to-sql/assets/validate_sql.py`** (+ test) — static validator:
  sqlglot parse + referenced table/column extraction (with SQL-alias→model
  resolution), checked for existence against `manifest.json` (optional
  `catalog.json` enrichment). Missing tables/columns are surfaced so a
  hallucinated column is caught before the SQL is presented. Manifest-load
  failure returns a structured error rather than raising. 9/9 tests pass.
- **`skills/to-sql/references/retrieval.md`** — what to pull (entities + field
  dictionaries, metrics incl. `## Materialized Columns` cards, concepts,
  `relationships` join-paths, `_evidence/` backing columns) and how to handle
  not-found / ambiguous / too-broad.
- **`skills/to-sql/references/prompt-assembly.md`** — schema-linking, column-card
  preference (SELECT the pre-built column, don't re-aggregate), join-path
  assembly, an explicit **empty few-shot slot** (v1 is zero-shot; gold examples
  are a planned increment), output contract, and the dialect rule.

**Boundary (unchanged hard rule):** `to-sql` **generates** SQL but **never
executes it and never connects to a warehouse** — validation is static only
(parse + manifest existence).

Zero changes to `init` / `query` / `refresh` core logic; `to-sql` is additive.
READMEs (en/ja/zh-TW) gain a `to-sql` row disambiguating it from `query`.

## [2.1.0] — 2026-06-02

### Added — metric column cards (materialized-metric mapping)

Completes the v2.0 minimal-state knowledge layer (knowledge layer + relationship
graph were already shipped; this is the last piece). Many dbt projects
pre-materialize a metric into mart columns — a "column forest" such as monthly
GMV exposed as `gmv_mtd` / `gmv_qtd` / `gmv_ytd` / `gmv_mom` / `gmv_yoy` plus
channel-segment variants. For text-to-SQL, the value is the **mapping**
(business variant → physical `model.column`), not a formula — the consumer
SELECTs the pre-built column rather than synthesizing a `GROUP BY`. This is the
strongest schema-linking lever for NL→SQL accuracy on projects without a
MetricFlow / dbt Semantic Layer definition.

- **SCHEMA `knowledge-metric`** — new **optional** `## Materialized Columns`
  body section (Variant | Model | Column | Grain). Appears only when a metric's
  variants are pre-materialized into mart columns; body-only (no frontmatter
  block); does not break "one metric = one page". The v2.x freeze header is
  clarified to permit additive optional body sections (no change to frontmatter
  shape / page types / naming / mandatory sections).
- **`distill-metrics.md` §3c — Materialization detection** — a front-gate in the
  SQL-derivation branch: anchor signal (column forest **or** pre-aggregated
  one-row-per-grain) routes the metric to the column-card output; mart-layer +
  schema.yml description alone are corroborating, not sufficient. Non-materialized
  metrics keep the existing formula / no-formula-fallback path (paths disjoint).
- **`distill-metrics.md` §5b — Materialized Columns Output** — producer spec for
  the card: the Variant|Model|Column|Grain table, plus a **forest-compression
  rule** — for regular naming (`gmv_{period}_{segment}`) capture the pattern +
  enumerated dimension values rather than enumerating ~100 rows; enumerate
  per-variant only when naming is irregular. Includes a `## Calculation`
  reconciliation note (materialized → SELECT pre-built column, no aggregation).
- **Worked example (§10b)** — a fully synthetic pre-aggregated Store GMV metric
  page (dimension-level compressed mapping table), plus a §11 decision-rule row
  making the materialized-vs-formula split explicit.

Artifact-only refinement of the v2.0 distill spec; zero warehouse / log / external
calls. `init` / `query` / `refresh` consume the new section generically (no
hardcoded body-section allowlist) — no changes required there.

## [2.0.0] — 2026-06-01

### BREAKING — Knowledge-centric redesign

dbt-wiki v2.0 shifts its purpose from **dbt resource structure distillation**
to **data knowledge distillation**: help users understand and analyze the
DATA (business entities, metrics, concepts), not just the shape of dbt objects.

#### Architecture: dual-layer model

**Knowledge layer (new, LLM-distilled)** — lives at the top of `.dbt-wiki/`:

- `entities/` — business objects (Customer, Order, Subscription) spanning
  multiple stg→int→mart models; each page includes a plain-language field
  glossary (no separate glossary directory)
- `metrics/` — business metrics (MRR, churn, LTV): definition, calculation
  rationale, caveats, source models; if the project has MetricFlow metrics,
  those are ingested as the authoritative input rather than re-derived
- `concepts/` — cross-cutting business rules encoded in SQL but belonging to
  no single entity ("active customer = order in last 90 days", fiscal year
  definitions, status enumerations)

Each knowledge page carries a `## Relationships` section with typed links
(entity↔entity, metric→entity, metric→concept, concept→entity/metric,
knowledge→`_evidence/`) derived from lineage and SQL semantics — a
lightweight knowledge graph without a graph database.

**Evidence layer (demoted, mechanical)** — existing manifest+sqlglot output
relocated under `_evidence/`:

- `_evidence/models/`, `_evidence/sources/`, `_evidence/macros/`, etc.
- All manifest+sqlglot extraction, column lineage, `manifest_sha` drift
  detection, and `syntheses/` stale tracking are fully preserved — these
  remain the distillation inputs and the authoritative structural truth.
- `lineage.md` and `syntheses/` stay at `.dbt-wiki/` root.

#### init: two-phase pipeline

- **Phase A** (mechanical, unchanged logic) — builds evidence layer under
  `_evidence/`, same sqlglot + manifest pipeline as v1.x.
- **Phase B** (new) — LLM-distills knowledge layer (`entities/`, `metrics/`,
  `concepts/`) reading Phase A output; each knowledge page records
  `derived_from: [evidence model uids]` for freshness tracking.

v1.x detection: if init finds an existing `.dbt-wiki/` containing pages with
`## User Notes`, it prints a one-time warning recommending backup before
proceeding. No migration is attempted (clean break).

#### query: semantic question classes

`/dbt-wiki:query` gains three new semantic question classes alongside the
existing structural ones:

- **K1** — entity lookup ("what is a Customer in this project?")
- **K2** — metric explanation ("how is MRR calculated?", "what are the caveats?")
- **K3** — cross-cutting concept ("what counts as an active subscription?")

Structural classes (C1–C11) are preserved; they now read from the evidence
layer directly.

#### refresh: thin evidence refresh + knowledge stale-flagging

`/dbt-wiki:refresh` refreshes the evidence layer (unchanged core logic) and
flags knowledge pages stale via `derived_from` when their source evidence
models change — reusing the existing `syntheses` stale mechanism. Auto
re-distillation of stale knowledge pages is a documented fast-follow, NOT
included in this release; user re-runs `/dbt-wiki:query` or init Phase B
to regenerate individual pages.

#### SCHEMA frozen at v2.0

`SCHEMA.md` is re-versioned and frozen at v2.0. All page-type definitions
(knowledge layer + evidence layer) are documented there. Future breaking
changes require v3.0+.

### Migration

**Clean break — no migration script.** v1.x `.dbt-wiki/` is rebuilt from
scratch by re-running `/dbt-wiki:init`. v1.x User Notes are NOT automatically
preserved (init warns once on detection; back up manually before re-init if
needed). The evidence layer's structural content (lineage, column data) is
fully regenerated from manifest+sqlglot.

---

## [1.3.0] — 2026-05-03

### Added — Lineage diagrams (ASCII + Mermaid) + auto-saved syntheses with stale detection

Two coupled features make `/dbt-wiki:query` answers richer AND
trustable over time.

#### 1. Lineage diagrams in query answers

For C2 (upstream) / C3 (downstream) / C4 (column-level) / C10
(refactoring impact) classes, query answers now include both:

- **ASCII tree** — renders in Claude Code chat output, any terminal,
  any markdown viewer. Always shown immediately.
- **Mermaid graph LR** — renders in IDE Markdown preview (Dataspell,
  VS Code, Cursor, JetBrains family), GitHub web view, Obsidian,
  mermaid.live. Saved into the synthesis page so user can re-open
  in their IDE for visual exploration.

New asset `format_lineage_diagram.py` (~360 lines, pure stdlib + PEP
723) generates both formats. Two modes:

```
column mode: consumes recursive_column_lineage.py JSONL
              + (model_uid, column) → ASCII tree + Mermaid (column nodes)
model mode:  consumes manifest.json directly
              + model_uid + direction (ancestors / descendants / both)
              → ASCII tree + Mermaid (model nodes)
```

Truncation policy: max 30 nodes per diagram (configurable via
`--max-nodes`); above that, append `truncated["⚠..."]` node and refer
user to full `lineage.md`. Node IDs use full-uid hash suffix to avoid
collisions when names are long; self-loops + duplicate edges deduped.

5/5 tests pass (column ancestors+descendants / ancestors-only / model
both / missing record / mermaid node-id safety). Real-world verified
on example mart_customer__dimension (38 upstream models, truncates
cleanly).

#### 2. Auto-saved syntheses with precise stale detection

`/dbt-wiki:query` now auto-saves answers to `.dbt-wiki/syntheses/<slug>.md`
for lineage / decision classes (C2/C3/C4/C9/C10). Information-only
classes (C1/C5/C6/C7/C8/C11) ask user before saving (default no).

Synthesis frontmatter records:
- `manifest_sha` at save time
- `affected_models` — the EXACT model uids the answer depends on
  (target model + every model in the rendered diagram tree)
- `query_class`, `sources_consulted`, `verification_run`, `verified_paths`

`/dbt-wiki:refresh` Step 6.5 uses `affected_models` for **precise**
stale detection: only mark stale when one of THOSE models actually
changed in this refresh's added / modified / removed sets — not just
"manifest_sha drifted" (which would mark everything stale on every
refresh).

When marked stale, refresh:
- Sets `stale: true`, `stale_at: <today>`, `stale_reason: <which models changed>`
- Prepends a banner to the synthesis body so the user sees it as the
  FIRST thing when opening the .md file in their IDE
- Does **NOT** regenerate the answer (preserves original; user controls
  when to re-query — avoids LLM cost + answer-wording drift on every refresh)

User re-runs `/dbt-wiki:query "<original question>"` → fresh answer
overwrites the synthesis, clears the stale flag.

### Files added

- **`assets/format_lineage_diagram.py`** (~360 lines, pure stdlib, PEP 723)
- **`assets/format_lineage_diagram_test.py`** (~190 lines, 5 cases pass)
- **`assets/synthesis_template.md`** — markdown shape with full frontmatter

### Files changed

- **`skills/init/SKILL.md`** — Step 4 cp block extends with 3 new files
  (diagram script + test + synthesis template) → `.dbt-wiki/_internal/`
- **`skills/query/SKILL.md`**:
  - New Step 4.5 — diagram generation (when + how to invoke
    `format_lineage_diagram.py` for each query class; ASCII always in
    chat, Mermaid always in synthesis)
  - New Step 6.5 — auto-save synthesis with full frontmatter
    (manifest_sha + affected_models for precise stale detection)
  - Step 7 log entry gains `Synthesis saved: <path>` line
- **`skills/refresh/SKILL.md`**:
  - New Step 6.5 — synthesis stale-detection logic (~50 lines bash + Python
    pseudocode). Non-destructive: marks `stale: true` + prepends banner
    to body; original answer + diagrams preserved.
  - Step 7 log entry gains `Syntheses marked stale: N` line
- **`skills/init/assets/SCHEMA.md`**:
  - Directory layout adds `syntheses/` with one-line description
  - New `### synthesis` page-type definition with full frontmatter
    template + body section spec + stale lifecycle explanation
- **`.claude-plugin/plugin.json`** — 1.2.0 → 1.3.0 (minor — new capability,
  fully backward compatible)

### Backward compatibility

**Zero break**:
- Lineage diagrams are STRICTLY additive to query output (ASCII + Mermaid
  appended after the text answer)
- Auto-save synthesis only kicks in for new queries; existing
  `.dbt-wiki/syntheses/` (none in v1.0–v1.2 since query never auto-saved)
  are unaffected
- Stale detection: synthesis WITHOUT `affected_models` field (none yet —
  this is v1.3 introducing it) falls back to `manifest_sha` drift
  comparison (less precise but always works)

### Real-world impact preview (example-dbt-pipeline)

After re-running `/dbt-wiki:init` (or just `/dbt-wiki:refresh`):
- `format_lineage_diagram.py` becomes available in `.dbt-wiki/_internal/`
- Next `/dbt-wiki:query "mart_customer__dimension 上游"` → answer includes
  ASCII tree (15 nodes, terminal-readable) + Mermaid block (renders in
  Dataspell preview)
- Answer auto-saved to `.dbt-wiki/syntheses/mart-customer-dimension-upstream.md`
- Future refresh after `int_ms_cd__store_name` changes → that synthesis
  marked stale with banner: "affected_models changed: int_ms_cd__store_name"

### Decision rationale

- **Why both ASCII + Mermaid**: ASCII covers the lowest common denominator
  (terminal output, any markdown viewer); Mermaid adds rich rendering
  where supported. User pays nothing for having both.
- **Why precise stale detection (vs full re-query)**: re-querying every
  refresh costs LLM tokens + introduces answer-wording drift (breaks
  git diff stability). Mark-stale-with-banner is honest about
  uncertainty without forcing regeneration.
- **Why script not LLM-generated diagrams**: deterministic, testable,
  consistent output across queries; LLM doesn't need to remember
  Mermaid syntax.

---

## [1.2.0] — 2026-05-03

### Added — `SELECT * FROM <final_cte>` wrapper-pattern unwrap

dbt projects very commonly end models with the convention:

```sql
WITH staging AS (...),
     enriched AS (...),
     final AS (
         SELECT col1, col2, calculation AS col3 FROM enriched
     )
SELECT * FROM final
```

In v1.0–v1.1.2, sqlglot saw only the outer `SELECT *` and reported a
single column named `*`. Models authored with this convention lost all
per-column information. On the example-dbt-pipeline dogfood, this hit
**71% of models** (860/1209), making column-level lineage queries
mostly useless for marts/dash tiers.

v1.2.0 adds an unwrap fallback in `extract_column_lineage.py`. When
the script detects a top-level `SELECT * FROM <single_table>` AND the
referenced table is a CTE in the same SQL's WITH clause, it walks into
the CTE and uses ITS projections as the model's columns. Recursive up
to depth 5 (handles `cte_a = SELECT * FROM cte_b = SELECT * FROM cte_c`).

For each unwrapped column, sources are extracted from direct column
references in the inner CTE's expression. If the inner CTE has a
single FROM table (the typical `final AS (SELECT ... FROM merge_data)`
pattern), unqualified column references are auto-resolved to that
table — so a single-CTE wrapper produces clean `merge_data.col1` style
sources.

### Real-world impact (example-dbt-pipeline, 1209 model files)

| Metric | v1.1 | v1.2 | Δ |
|---|---|---|---|
| Models with real column names | 349 (28.9%) | 1209 (100%) | **+860 / +247%** |
| Models stuck at just `*` | 860 | 0 | **−860** |
| Avg columns per model (real) | 1 | 12 | **+12×** |
| Total column entries unlocked | ~349 | ~14,500 | **+41×** |

### Files changed

- **`dbt-wiki/skills/init/assets/extract_column_lineage.py`**:
  new helper `_expand_star_via_cte()` (~80 lines). Detects `SELECT *
  FROM <cte>` pattern, recursively walks nested wrappers (max_depth=5),
  resolves unqualified column refs against the inner CTE's single FROM
  table when applicable. Hooked into `extract_lineage()` BEFORE the
  per-projection loop — if unwrap succeeds, use it; otherwise fall
  through to existing logic (preserves all v1.1 behavior for non-wrapper
  SQL).
- **`dbt-wiki/skills/init/assets/extract_column_lineage_test.py`**:
  - 2 new test cases (Cases 8 + 9): single-level wrapper + nested
    wrapper. Both pass.
  - Test runner switched to `uv run` first (fall back to plain python3
    if uv not installed). Previously ran via `sys.executable` which
    couldn't honor PEP 723 metadata, so all sqlglot-dependent tests
    silently skipped on machines without manually pip-installed
    sqlglot.
- **`.claude-plugin/plugin.json`**: 1.1.2 → 1.2.0 (minor bump — new
  capability, fully backward compatible).

### Backward compatibility

**Zero break**. The unwrap is a strictly additive fallback:
- If your SQL doesn't use the `SELECT * FROM <cte>` pattern, code path
  is identical to v1.1.x
- If your SQL DOES use the pattern but the CTE isn't found / FROM has
  joins / nested too deep — fall through to v1.1's behavior (Star → `*`)
- All 7 v1.1 test cases still pass

### Limitations (v1.2.0)

- Only handles single-table FROM in the outer `SELECT *`. If outer is
  `SELECT * FROM cte_a JOIN cte_b ON ...`, no unwrap (could be added
  in v1.3 by merging projections from both CTEs).
- For unqualified column refs inside the CTE, only resolves to a single
  default table — if the CTE itself has joins, references stay as
  `<unqualified>` (the recursive-lineage extractor can still resolve
  these via downstream chain).
- max_depth=5 should cover all realistic dbt wrapper chains; if you
  somehow have `cte1 → cte2 → cte3 → cte4 → cte5 → cte6`, deepest one
  is skipped.

### Migration

Re-run `/dbt-wiki:init` to regenerate model pages with full column
lineage. Existing v1.1.x `.dbt-wiki/` pages will be overwritten by
init's re-run (same idempotency contract); user-owned `## User Notes`
sections are preserved.

---

## [1.1.2] — 2026-05-03

### Fixed — `.dbt-wiki/` now writes to git repo root, not cwd

v1.0–v1.1.1 used relative paths like `mkdir -p .dbt-wiki/models`, which
resolved to `$PWD` at invocation time. Combined with v1.1.1's smart
dbt project detection (which lets the user run init from anywhere),
this meant `.dbt-wiki/` would land wherever the user happened to be:

- Run from `~/repo/`        → `~/repo/.dbt-wiki/`        ✓
- Run from `~/repo/dbt/`    → `~/repo/dbt/.dbt-wiki/`    ✗
- Run from `~/repo/dbt/models/staging/` → 4 levels deep ✗✗

This was inconsistent with the CLAUDE.md drop-in (Step 2 of init),
which already wrote to **git repo root**. Two output locations for the
same plugin = bad UX. Also broke refresh / query when the user changed
cwd between init and subsequent invocations.

### Fix

All three skills (init / refresh / query) now perform a single
**Step 0pre**: detect git repo root via `git rev-parse --show-toplevel`,
fall back to `$PWD` if not in a git repo, then `cd "$WIKI_DIR"`. After
that, every existing `.dbt-wiki/...` path in the SKILL.md auto-resolves
to the right place — no bulk path rewrites needed.

Result:

- `.dbt-wiki/` always lives at the git repo root
- Co-located with `.git/`, `CLAUDE.md` drop-in, and (if installed) `.repo-wiki/`
- init / refresh / query can be run from ANY cwd within the repo and
  always read/write the same `.dbt-wiki/`

### Files changed

- **`skills/init/SKILL.md`** — new Step 0pre (4-line bash) inserted before
  Step 0a; everything below works unchanged.
- **`skills/refresh/SKILL.md`** — same Step 0pre prepended to existing
  pre-condition check; error message now includes `$WIKI_DIR` for clarity.
- **`skills/query/SKILL.md`** — same Step 0pre prepended.
- **`skills/init/assets/SCHEMA.md`** — Architecture section clarifies
  `.dbt-wiki/` location ("at git repo root, same level as .git/ and CLAUDE.md").
- **`.claude-plugin/plugin.json`** — 1.1.1 → 1.1.2 (patch — bug fix, no
  behavior change for users who already ran from git repo root).

### Backward compatibility

**Pre-existing `.dbt-wiki/` directories at non-root locations** (created
by v1.0–v1.1.1 when user ran from a subfolder) are NOT auto-migrated.
After upgrading to v1.1.2, the next `/dbt-wiki:init` will create a NEW
`.dbt-wiki/` at the git repo root, leaving the old one orphaned.
Migration: manually `mv <old-location>/.dbt-wiki <repo-root>/.dbt-wiki`,
or delete the old one and re-run init from scratch.

### Edge cases

- **Not in a git repo**: `git rev-parse` fails silently; WIKI_DIR
  falls back to `$PWD`. User must invoke from a sensible location
  (typically the project root). Same constraint as v1.1.0.
- **Submodules**: `git rev-parse --show-toplevel` returns the
  submodule's root, not the parent repo. This is correct: each
  submodule with its own dbt project gets its own `.dbt-wiki/`.

---

## [1.1.1] — 2026-05-03

### Changed — 5-tier dbt project root detection

v1.0/v1.1 only checked two hardcoded locations relative to cwd:
`./dbt/dbt_project.yml` and `./dbt_project.yml`. Anyone with a
non-standard layout (e.g. dbt under `data/dbt-prod/`) or running init
from inside a subdirectory (e.g. `models/staging/`) hit "Cannot find
dbt_project.yml" and had to cd to the right place.

v1.1.1 introduces a **5-tier resolver**, tried in priority order:

1. **Explicit arg**: `/dbt-wiki:init <path>` — pass the directory
2. **`$DBT_PROJECT_DIR` env var** — matches dbt CLI / dbt-mcp convention
3. **Ancestor walk from cwd** — up to 5 levels up (handles `models/staging/...`)
4. **Descendant scan from cwd** — `find -maxdepth 3` with exclusions
   (`node_modules`, `.git`, `target`, `.venv`, `__pycache__`,
   `dbt_packages`, `.repo-wiki`, `.dbt-wiki`)
5. **Legacy whitelist** (`./` and `dbt/`) — kept for back-compat

First match wins. Output reports which tier resolved (e.g. `detected
via: ancestor walk from cwd`) so user can debug if it picked the wrong
project (rare, but possible in monorepos with multiple dbt projects).

**Files changed**:
- `dbt-wiki/skills/init/SKILL.md` — Step 0 split into 0a (resolver,
  ~70 lines bash) + 0b (artifact + Python runner verification). Failure
  message lists every tier checked with actionable hints.
- `dbt-wiki/skills/refresh/SKILL.md` — same resolver inlined (refresh
  needs identical detection; can't rely on init having stored the path
  since user might run refresh from a different cwd).
- `dbt-wiki/skills/query/SKILL.md` — drift check uses the same resolver
  minus the explicit-arg tier (query doesn't take a path arg).
- `dbt-wiki/.claude-plugin/plugin.json` — 1.1.0 → 1.1.1.

**Coverage matrix**:

| User's cwd | dbt at | v1.1.0 | v1.1.1 |
|---|---|---|---|
| repo root | `./dbt/` (example style) | ✅ | ✅ |
| repo root | `./` | ✅ | ✅ |
| `models/staging/` | `../../dbt_project.yml` | ❌ | ✅ (ancestor walk) |
| any cwd, `$DBT_PROJECT_DIR` set | (env-pointed) | ❌ | ✅ (env var) |
| repo root with `data/dbt-prod/` | non-standard subdir | ❌ | ✅ (downward scan) |
| explicit `/dbt-wiki:init ./other/` | wherever | ❌ | ✅ (arg) |
| Multi-dbt monorepo | multiple matches | ❌ | ⚠️ first match wins (disambiguate via arg or env var) |

**Backward compatibility**: zero break. Tier 5 is the exact v1.0/v1.1
behavior. Existing users see no change.

---

## [1.1.0] — 2026-05-03

### Added — recursive cross-model column lineage

dbt-wiki v1.0.0's column lineage was **single-hop** (within one
compiled SQL): `fct_orders.customer_id ← stg_orders.customer_id`. To
trace back to source you'd manually walk the chain across model pages.

v1.1.0 ships **precomputed recursive lineage** that walks the dbt DAG
bidirectionally (ancestors back to source + descendants forward to
leaf marts) and stores it in each model page's
`## Column Lineage Chains` body section. Now `/dbt-wiki:query` can
answer "fct_orders.customer_id 從哪一路來?" or "rename
stg_customers.email 會影響哪些 model 的哪些 column?" by loading a
single page.

This is the recursive lineage capability comparable to [canva-public/dbt-column-lineage-extractor](https://github.com/canva-public/dbt-column-lineage-extractor),
implemented inside dbt-wiki without an additional pip dependency.
Same sqlglot under the hood (via existing `extract_column_lineage.py`);
the new script `extract_recursive_column_lineage.py` is pure stdlib.

**Files added**:
- `dbt-wiki/skills/init/assets/extract_recursive_column_lineage.py`
  (382 lines): consumes per-SQL JSONL from `extract_column_lineage.py
  --batch` plus `target/manifest.json`. Builds an alias-map (model name
  / alias / schema-qualified / fully-qualified all map to manifest
  unique_id) and a feeds_into reverse-DAG. Recursively walks ancestors
  (via the alias-map) and descendants (via feeds_into matched against
  downstream models' per-SQL sources). Cycle + max-depth protection.
  Output is JSONL — one record per `(model_uid, column)` with
  `ancestors` and `descendants` as nested dict trees.
- `dbt-wiki/skills/init/assets/extract_recursive_column_lineage_test.py`
  (260 lines): synthetic 4-model dbt project with COALESCE multi-source.
  6 cases: 1) full ancestor chain back to source through stg, 2) negative
  descendant test (different column), 3) positive descendant chain
  through fct to mart (2 hops), 4) single-hop ancestor, 5) 2-hop
  descendant via intermediate, 6) whole-project mode produces 1 record
  per (model, column). All 6 pass on pure stdlib (no sqlglot needed
  for test).

**Files changed**:
- `dbt-wiki/skills/init/SKILL.md`:
  - Step 4 cp block extended to copy the 2 new scripts to
    `.dbt-wiki/_internal/`
  - New Step 4f: invoke recursive script after Step 4b's per-SQL
    extraction; output JSONL piped to `/tmp/dbt-wiki-recursive-lineage.jsonl`
  - New Step 4g: optional verify of recursive script via its smoke test
- `dbt-wiki/skills/init/assets/SCHEMA.md`:
  - New body section `## Column Lineage Chains` with example showing
    nested ancestors + descendants tree
  - Standard sections list updated to include `Column Lineage Chains`
    (so refresh regenerates it like other derived sections)
- `dbt-wiki/skills/query/SKILL.md`:
  - C4 (Column-level lineage) row updated: now loads single model page's
    `## Column Lineage Chains` section (precomputed recursive chain)
    instead of needing to walk multiple upstream pages
- `dbt-wiki/.claude-plugin/plugin.json`: 1.0.0 → 1.1.0

**Relationship to PR #213** (open at time of this PR):
PR #213 adopts PEP 723 + uv for dependency management. This PR (v1.1.0)
adds recursive lineage. The two are orthogonal — both modify
`init/SKILL.md` script invocation but at different points (PR #213
changes WHICH runner; this PR adds WHAT TO RUN). Whichever lands first,
the second needs a small rebase on `plugin.json` version field.

**Limitations** (documented in script docstring):
- SQL-local aliases like `SELECT f.a FROM stg_orders AS f` require
  sqlglot to back-resolve `f` → `stg_orders` in its lineage output.
  If sqlglot emits `f.a` literally, recursive walker marks
  `_unresolved::f::a` and stops at that branch.
- CTEs inside compiled SQL — same story; sqlglot usually walks through
  them but not always.
- max_depth defaults to 10 (configurable via `--max-depth`); cycles
  marked as `_cycle` (rare in dbt but possible with snapshot models).
- For Redshift specifically: late-binding views work normally.

**Why implement vs. depend on dbt-column-lineage-extractor**:
- Avoid external pip dep (one less thing for users to install)
- Same underlying sqlglot — no quality gap on dialect support
- Output format we control (matches dbt-wiki SCHEMA conventions)
- Reuses existing per-SQL lineage from v1.0.0 (composable, not duplicated)
- 380-line implementation vs. external dependency — net code we own

---

## [1.0.1] — 2026-05-03

### Changed — PEP 723 inline metadata + uv-first execution

Both bundled scripts (`extract_column_lineage.py`, `extract_sql_comments.py`)
now declare their Python and dependency requirements via PEP 723 inline
metadata. With [uv](https://github.com/astral-sh/uv) installed, `uv run`
auto-creates an ephemeral env, installs sqlglot, runs the script, and
cleans up — no manual `pip install sqlglot` required.

**Why**: the original v1.0.0 design required users to manually
`pip install sqlglot` into their dbt Python env. That step was easy to
forget and polluted the dbt env with a tool not used by dbt itself.
PEP 723 + uv removes the step entirely while preserving full
backward-compatibility with plain `python3` (for users without uv).

**Files changed**:
- `dbt-wiki/skills/init/assets/extract_column_lineage.py` — added
  PEP 723 block declaring `sqlglot>=25.0` and `requires-python = ">=3.10"`;
  shebang updated to `#!/usr/bin/env -S uv run --script`; module docstring
  documents both execution modes
- `dbt-wiki/skills/init/assets/extract_sql_comments.py` — added PEP 723
  block with empty `dependencies` list (pure stdlib); same shebang change.
  PEP 723 included for consistency even though no third-party dep
- `dbt-wiki/skills/init/SKILL.md`:
  - Step 0 Pre-condition Check rewritten: detects `uv` first, falls back
    to `python3` with sqlglot. Sets `$PY_RUNNER` for downstream steps.
    Both detection paths produce a clear "next step" hint if neither
    is available.
  - Step 4 column-lineage script invocations changed from `python3 ...`
    to `$PY_RUNNER ...`
  - Step 4d comment-extraction script invocations same change
- `dbt-wiki/skills/refresh/SKILL.md` — same Step 0 detection + invocation
  changes as init
- `dbt-wiki/README.md` / `README.zh-TW.md` / `README.ja.md` — Quick start
  Step 2 + Pre-conditions section updated to present uv as primary,
  pip as fallback (in all three languages)
- `dbt-wiki/.claude-plugin/plugin.json` — version bumped 1.0.0 → 1.0.1;
  description updated to mention PEP 723 + uv

**Backward compatibility**: zero break. Users with sqlglot already
installed via pip continue to work unchanged (init detects this path
in Step 0).

**Test verification** (local):
- `uv run extract_column_lineage.py` on a 4-column SQL with COALESCE +
  JOIN → correct column lineage output (auto-installed sqlglot 30.6
  in 5ms ephemeral env)
- `uv run extract_sql_comments.py` on a 3-comment SQL (line + jinja +
  inline) → all 3 entries with correct line numbers + kind classification

**Decision rationale**: uv is increasingly the Python tooling standard
(used by dbt-coves, modal, duckdb, etc.). PEP 723 inline metadata is
the official Python recommendation for self-contained scripts (PEP
accepted late 2024). Adopting both removes the "manual install"
friction without imposing dependency on a custom installer or vendored
sqlglot copy. Backward fallback to plain `python3 + pip` ensures users
who haven't adopted uv yet still get full functionality.

---

## [1.0.0] — 2026-05-02

### Added — Initial release

Four skills for local-only LLM-queryable dbt knowledge (symmetric with repo-wiki: init / refresh / ingest / query).

**Skills**:
- `/dbt-wiki:init` — first-time setup. Reads `target/manifest.json` (model metadata, refs/sources, schema.yml columns, tests), `target/compiled/<project>/**/*.sql` parsed via [sqlglot](https://github.com/tobymao/sqlglot) for **column-level lineage**, AND `dbt/models/**/*.sql` raw files parsed via regex for **inline SQL/jinja comments** (`-- ...`, `/* ... */`, `{# ... #}`). Plugin ships 4 scripts in `assets/` (flat — Anthropic skill convention forbids nested asset subdirs): `extract_column_lineage.py` + `_test.py` (sqlglot lineage with `--batch` JSONL mode; 7-case smoke test, all passing on sqlglot 30.6) and `extract_sql_comments.py` + `_test.py` (regex comment extractor with `--batch` mode; 6-case smoke test including multibyte/Chinese, all passing). Init copies all 4 to `.dbt-wiki/_internal/`. Generates one markdown page per model / source / macro (used) / seed / snapshot / singular test / exposure under `.dbt-wiki/`. Writes `.dbt-wiki/SCHEMA.md`, `index.md`, `lineage.md`, `log.md`, plus an idempotent CLAUDE.md drop-in. Re-runnable: refreshes manifest-derived fields, archives orphans, preserves custom body sections.
- `/dbt-wiki:refresh` — incremental update. Compares current `manifest.json` md5 against `manifest_sha` in log.md; processes only added / modified / removed models / sources / macros. Re-runs sqlglot lineage AND comment extraction on changed files. Removed models are archived to `.dbt-wiki/_archive/<date>/`, never hard-deleted. **Preserves user-owned `## User Notes` body section verbatim** (managed by /dbt-wiki:ingest). Always regenerates `index.md` and `lineage.md` (derived files). Asks user to confirm diff summary before writing.
- `/dbt-wiki:ingest` — capture user-supplied context that is NOT in manifest.json or schema.yml: gotchas, design rationale, ticket references, incident links. Auto-detects target model / source / macro from message text; appends note as dated entry under `## User Notes` body section on the matched page. Multi-target match resolution (asks user to clarify on no-match or multi-match). Survives `/dbt-wiki:refresh` cycles (refresh treats `## User Notes` as user-owned). Mirrors `/repo-wiki:ingest` context-mode behavior for the dbt-internal scope. Doc-import mode and git-mode are intentionally NOT included (use /dbt-wiki:refresh for manifest snapshots; use /repo-wiki:ingest for cross-cutting WHY).
- `/dbt-wiki:query` — natural-language Q&A. Routes question to one of 11 query classes (C1: model lookup, C2/C3: upstream/downstream lineage, C4: column-level lineage, C5: materialization filter, C6: tag/group/tier filter, C7: test coverage, C8: source attribution, C9: macro usage, C10: refactoring impact, C11: schema gaps). Loads minimum pages for the class. Drift-aware: warns if current `manifest.json` SHA differs from wiki snapshot. Suggests `/dbt-wiki:refresh` when stale. Answers can draw from inline comments AND user notes alongside structured manifest data — gives WHY-aware responses, not just structural ones.

**Schema (frozen at v1.0)**:
- `model` page type with frontmatter: `unique_id`, `materialization`, `tags`, `schema`, `database`, `group`, `access`, `contract_enforced`, `last_updated`, `manifest_sha`, `columns_extracted_via`, `columns[]` (each with `name`/`type`/`description`/`declared_in_schema_yml`/`tests`/`sources` from sqlglot), `depends_on` (refs/sources/macros), `feeds_into`, `generic_tests`, `recorded_decisions` (cross-link to repo-wiki)
- `source` page type with `unique_id`, `source_name`, `table_name`, `schema`, `database`, `loaded_at_field`, `freshness`, `columns`, `fed_by`, `feeds_into`
- `macro` page type with `unique_id`, `package`, `path`, `arguments`, `description`, `used_by_models`
- Same pattern for seed / snapshot / test / exposure
- `index.md` grouped by tier path / materialization / tag / group
- `lineage.md` with ASCII tree (per source) + adjacency list (per model); tier-aggregated view for >500-node projects
- `log.md` append-only with init / refresh / query entries; tracks `manifest_sha` and sqlglot failures

**Coexistence with [`repo-wiki`](../repo-wiki/)**:
- Both plugins write to distinct hidden dirs (`.dbt-wiki/` vs `.repo-wiki/`); neither modifies the other
- CLAUDE.md drop-ins use distinct markers
- dbt-wiki: STRUCTURE + COLUMN LINEAGE (auto-derived from manifest + sqlglot)
- repo-wiki: WHY (decisions, refactor history; manual ingest)
- Cross-link freely from either side

**Pre-conditions**:
- dbt project (manifest.json schema v9+ recommended)
- `dbt parse && dbt compile` must run before init/refresh
- Python 3.x + `sqlglot` (`pip install sqlglot`)
- Dialect support: redshift / postgres / snowflake / bigquery / databricks / clickhouse / duckdb / mysql / oracle / spark / sqlite / tsql

### Design decisions

- **Decision 1**: `manifest.json` + `compiled/*.sql` are source of truth; never re-derive what dbt already parsed. Specifically, init parses `compiled/*.sql` not `raw_code` because dbt's own jinja engine has the most accurate expansion.
- **Decision 2**: sqlglot is a hard dependency for v1.0. The whole point of dbt-wiki vs reading manifest.json directly is column-level lineage — without sqlglot, the value proposition collapses. User installs via `pip install sqlglot` in their dbt env.
- **Decision 3**: Local-only. No dbt Cloud, no warehouse calls. catalog.json (real warehouse types) and run_results.json (test pass/fail) are v2 backlog opt-in reads, not v1 requirements.
- **Decision 4**: Refresh idempotency via `manifest_sha`. If current manifest hash matches log.md's last record, refresh exits without changes. User can force by deleting the manifest_sha line from log.md.
- **Decision 5**: Archive, never hard-delete. Orphaned models go to `.dbt-wiki/_archive/<date>/`. User can restore manually if needed.
- **Decision 6**: Coexist with repo-wiki via distinct hidden dirs and CLAUDE.md drop-in markers. Neither plugin needs to know about the other; cross-links are user-authored.
- **Decision 7**: Macro pages only for macros used by ≥1 model. Filter `manifest.macros` by checking each model's `depends_on.macros`. Avoids spam for unused macros (especially in dbt_utils).
- **Decision 8**: Filename collision: when same `name` exists in different packages, use `<package>__<name>.md` (matches repo-wiki convention).
- **Decision 9**: Drift-aware query (DT4). When `manifest.json` SHA differs from wiki snapshot, query prepends a warning and recommends `/dbt-wiki:refresh`. Stale-but-best-effort answers are better than refusing to answer; explicit warning preserves user trust.
- **Decision 10**: Symmetric command set with repo-wiki (init / refresh / ingest / query). Original draft had only 3 skills (init / refresh / query) on the reasoning that "dbt-wiki is a derivation engine, repo-wiki is an accumulation engine". User pushback during PR review noted that dropping ingest forced users to learn two mental models AND left dbt-wiki standalone-incomplete (no way to add tribal knowledge if repo-wiki not installed). Added `/dbt-wiki:ingest` for context capture; kept `refresh` distinct from `ingest` because they're functionally different (manifest snapshot replacement vs user-input accumulation). End result is more symmetric than repo-wiki's polymorphic ingest (git/context/doc-import all conflated): each verb does one thing.
- **Decision 11**: Inline comment extraction via regex on raw_code, NOT sqlglot on compiled. Reasoning: (a) jinja `{# ... #}` comments are stripped by `dbt compile` — extracting them needs raw_code; (b) sqlglot's comment handling varies by dialect and can drop positional context; (c) regex is dialect-agnostic and preserves source line numbers. The per-model `## Inline Comments` body section displays line-number-prefixed entries so user can locate them in source. Trade-off: regex doesn't classify comments by structural position (header vs pre-CTE vs inline) — line number is sufficient for LLM query.
- **Decision 12**: `## User Notes` is user-owned, refresh preserves verbatim. Same protection model as repo-wiki's ingest-accumulated entity sections (Responsibility / Architecture / etc.). The schema explicitly lists `## User Notes` as user-owned (alongside any other non-standard `##` heading the user adds). Refresh's "preserve custom body sections" rule already covered this; the ingest skill formalizes the use case.

### Pre-trial validation

Plan validation against `<local dbt project>` (real dbt-on-Redshift project, ~200+ models across 8 tiers — staging/interm/marts/marts_msd/marts_qlr/dash/expt/export_to_googlesheets):
- ✅ dbt project layout matches dbt-wiki's expectations (`dbt/dbt_project.yml`, `dbt/models/<tier>/`, `dbt/target/`)
- ✅ User already has dbt CLI (`dbt-redshift` conda env)
- ⏳ sqlglot install required (`pip install sqlglot` in dbt-redshift env) — pre-condition
- ⏳ Real-world dogfood scheduled post-merge: `/dbt-wiki:init` against example-dbt-pipeline → measure model count, sqlglot failure rate, lineage depth, query response quality

### Known limitations (v1.0)

- **Macros with conditional SQL**: sqlglot may fail on extreme jinja edge cases (rare; dbt compile usually resolves). Failed models still get pages, just without `columns[].sources`.
- **Cross-package column lineage**: when a model uses a dbt_utils macro that itself wraps SELECT logic, sqlglot sees the expanded SQL but column names may be macro-generated and not match user expectation.
- **Late-binding views (Redshift)**: sqlglot supports them syntactically; semantic correctness depends on dialect maturity.
- **Singular test attribution**: tests in `tests/*.sql` (not schema.yml) are listed in their own pages; cross-linking to affected models via `depends_on` parsing.
- **No catalog.json / run_results.json yet**: column types in v1 are from schema.yml only (warehouse-real types are v2 backlog).
- **Wall-clock for init**: ~30s-2min for typical 100-300 model projects (sqlglot is single-threaded per file; v2 may parallelize).

### Inspiration & credits

- **[dbt-labs/dbt-core](https://github.com/dbt-labs/dbt-core)** — `manifest.json` schema is the canonical source-of-truth for dbt project structure. v1 leans entirely on dbt's parse output; never re-derives.
- **[tobymao/sqlglot](https://github.com/tobymao/sqlglot)** — column-lineage extraction is impossible without a SQL AST library; sqlglot's multi-dialect support (redshift/snowflake/bigquery/etc.) makes dbt-wiki dialect-agnostic for free. MIT-licensed pure Python, no native deps.
- **[`repo-wiki`](../repo-wiki/)** — sibling plugin in monkey-skills. Conventions reused: SKILL.md structure (Step-by-step workflow + Rules), SCHEMA.md frozen-until-v2.0, log.md append-only operation tracking, CLAUDE.md drop-in idempotency, `_archive/` for safe removal.
- **[lis186/SourceAtlas](https://github.com/lis186/SourceAtlas)** — its information-theory analysis discipline (high-entropy file priority, scan-ratio bounds) inspired repo-wiki v1.2. dbt-wiki doesn't use those directly (manifest.json eliminates the need for heuristic scanning) but shares the spirit of "let the structured truth do the work, don't re-invent parsing."
