# Changelog

All notable changes to the `dbt-wiki` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

Plan validation against `/Users/kouko/DataspellProjects/iCHEF-dbt-pipeline` (real dbt-on-Redshift project, ~200+ models across 8 tiers — staging/interm/marts/marts_msd/marts_qlr/dash/expt/export_to_googlesheets):
- ✅ dbt project layout matches dbt-wiki's expectations (`dbt/dbt_project.yml`, `dbt/models/<tier>/`, `dbt/target/`)
- ✅ User already has dbt CLI (`dbt-redshift` conda env)
- ⏳ sqlglot install required (`pip install sqlglot` in dbt-redshift env) — pre-condition
- ⏳ Real-world dogfood scheduled post-merge: `/dbt-wiki:init` against iCHEF-dbt-pipeline → measure model count, sqlglot failure rate, lineage depth, query response quality

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
