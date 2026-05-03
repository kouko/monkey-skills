# Changelog

All notable changes to the `dbt-wiki` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
per-column information. On the iCHEF-dbt-pipeline dogfood, this hit
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

### Real-world impact (iCHEF-dbt-pipeline, 1209 model files)

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
| repo root | `./dbt/` (iCHEF style) | ✅ | ✅ |
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
