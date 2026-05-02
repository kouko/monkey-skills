<!-- dbt-wiki:start -->
## .dbt-wiki/ Directory

`.dbt-wiki/` is managed by the dbt-wiki plugin (local-only LLM-queryable
dbt knowledge base derived from `target/manifest.json` + sqlglot column lineage).

- Do NOT edit files in `.dbt-wiki/` directly — run `/dbt-wiki:refresh`
- To query model structure / lineage / columns: `/dbt-wiki:query "<question>"`
- To rebuild from scratch (after major refactor): `/dbt-wiki:init`

Pre-condition: must run `dbt parse && dbt compile` before init/refresh
(generates `target/manifest.json` and `target/compiled/**/*.sql` that
dbt-wiki reads).

Schema rules: `.dbt-wiki/SCHEMA.md`

Coexists with `.repo-wiki/` if present:
- `.dbt-wiki/` = STRUCTURE + COLUMN LINEAGE (auto-derived)
- `.repo-wiki/` = WHY (decisions, refactor history) — manual ingest
<!-- dbt-wiki:end -->
