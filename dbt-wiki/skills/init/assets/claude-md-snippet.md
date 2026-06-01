<!-- dbt-wiki:start -->
## .dbt-wiki/ Directory

`.dbt-wiki/` is managed by the dbt-wiki plugin — a two-layer knowledge
base for your dbt project. Do NOT edit its files directly.

**Two layers:**

- **Knowledge layer** (`entities/`, `metrics/`, `concepts/`) — LLM-distilled
  business meaning. One page per business object, measure, or cross-cutting
  rule. Pages are connected via typed `## Relationships` edges and cite the
  evidence they were distilled from.
- **Evidence layer** (`_evidence/models/`, `_evidence/sources/`,
  `_evidence/macros/`, …) — mechanical extraction from
  `target/manifest.json` + sqlglot column lineage. Deterministic;
  rebuilt by init/refresh.

**Usage:**
- Query in business language: `/dbt-wiki:query "<question>"`
- Rebuild evidence + flag stale knowledge after `dbt parse`: `/dbt-wiki:refresh`
- Full rebuild from scratch: `/dbt-wiki:init`

Pre-condition: run `dbt parse && dbt compile` before init/refresh
(generates `target/manifest.json` and compiled SQL that dbt-wiki reads).

Schema rules: `.dbt-wiki/SCHEMA.md`

Coexists with `.repo-wiki/` if present:
- `.dbt-wiki/` = WHAT the data means (knowledge layer) + structural evidence
- `.repo-wiki/` = WHY (decisions, refactor history) — manual ingest
<!-- dbt-wiki:end -->
