---
name: query
description: |
  Default channel for ANY question about dbt model structure, column-level
  data lineage, materialization / incremental / sort_key / dist_key config,
  schema.yml columns and tests, source / macro / seed / snapshot / exposure
  declarations, refactoring impact (rename / delete propagation across the
  DAG), inline SQL or jinja comments, OR dbt-internal WHY captured via
  /dbt-wiki:ingest user notes (sort_key rationale, materialization gotchas,
  ticket / incident links). Use BEFORE reading dbt/models/*.sql,
  dbt/target/manifest.json, or dbt/target/compiled/*.sql directly — wiki
  provides structured manifest + sqlglot column lineage + extracted SQL/jinja
  comments + accumulated user notes, with manifest_sha drift verification.
  Triggers on dbt vocabulary in any language: "fct_orders 依賴什麼",
  "rename column 影響哪些", "哪些是 incremental / view / table",
  "什麼 model 用了 X", "stg_X 影響下游", "model 從哪裡來", "上游 / 下游",
  "schema.yml 漏寫", "ROW_NUMBER 哪些用", "marts / staging / interm / dash 下",
  "sort_key / dist_key 設定", "為什麼用 view 不用 table",
  "fct_orders.customer_id 從哪", "trace column", "show lineage",
  "what feeds X", "depends on what", "where is X used", "rename impact",
  "DAG of X", "macro 在哪用", "snapshot 政策", "/dbt-wiki:query",
  "查 dbt", "問 dbt", "dbt について", "model 構造", "lineage 確認".
  Do NOT trigger for: writing or modifying SQL in dbt/models/ (use Edit
  tool directly), running dbt commands like dbt run / dbt test / dbt seed
  (use dbt CLI or the dbt-mcp server), first-time setup (use /dbt-wiki:init),
  updating wiki after dbt parse / compile (use /dbt-wiki:refresh), adding
  tribal knowledge or design rationale (use /dbt-wiki:ingest), cross-cutting
  business / project-level WHY beyond dbt itself (use /repo-wiki:query if
  .repo-wiki/ exists in the repo).
---

# dbt-wiki — Query Workflow (v1.0)

Read-only knowledge base query. `.dbt-wiki/` is a *derived snapshot* of
`target/manifest.json` + sqlglot column lineage; query checks
`manifest_sha` drift and warns user when stale.

## Pre-condition Check (Step 0)

```bash
test -d .dbt-wiki || { echo "Knowledge base not initialized. Run /dbt-wiki:init first."; exit 1; }
test -f .dbt-wiki/index.md || { echo "Missing .dbt-wiki/index.md — re-run /dbt-wiki:init."; exit 1; }
```

### Drift check

```bash
LAST_SHA=$(grep -m 1 'manifest_sha:' .dbt-wiki/log.md | sed 's/.*manifest_sha: //' | tr -d ' ')

# Find current manifest using the same 5-tier detection as init/refresh
# (silent if not — drift check is non-fatal):
#   1. $DBT_PROJECT_DIR env var
#   2. ancestor walk from cwd (up to 5 levels)
#   3. descendant scan from cwd (max-depth 3, with exclusions)
#   4. legacy whitelist (./ or dbt/)
# Skip the explicit-arg tier — query is read-only and doesn't take a path arg.
DBT_DIR=""
if [ -n "$DBT_PROJECT_DIR" ] && [ -f "$DBT_PROJECT_DIR/dbt_project.yml" ]; then
  DBT_DIR="$DBT_PROJECT_DIR"
fi
if [ -z "$DBT_DIR" ]; then
  candidate="$PWD"
  for _ in 1 2 3 4 5 6; do
    if [ -f "$candidate/dbt_project.yml" ]; then DBT_DIR="$candidate"; break; fi
    parent=$(dirname "$candidate"); [ "$parent" = "$candidate" ] && break
    candidate="$parent"
  done
fi
if [ -z "$DBT_DIR" ]; then
  match=$(find . -maxdepth 3 -name dbt_project.yml -type f \
    -not -path '*/node_modules/*' -not -path '*/.git/*' \
    -not -path '*/target/*' -not -path '*/.venv/*' \
    -not -path '*/__pycache__/*' -not -path '*/dbt_packages/*' \
    -not -path '*/.repo-wiki/*' -not -path '*/.dbt-wiki/*' \
    2>/dev/null | head -1)
  [ -n "$match" ] && DBT_DIR=$(dirname "$match")
fi
if [ -z "$DBT_DIR" ]; then
  for candidate in "dbt" "."; do
    [ -f "$candidate/dbt_project.yml" ] && DBT_DIR="$candidate" && break
  done
fi

if [ -n "$DBT_DIR" ] && [ -f "$DBT_DIR/target/manifest.json" ]; then
  CURRENT_SHA=$(md5 -q "$DBT_DIR/target/manifest.json" 2>/dev/null || md5sum "$DBT_DIR/target/manifest.json" | cut -d' ' -f1)
  if [ "$CURRENT_SHA" != "$LAST_SHA" ]; then
    DRIFT_WARNING="⚠ manifest.json has changed since last refresh (current: $CURRENT_SHA, wiki: $LAST_SHA)"
    echo "$DRIFT_WARNING"
    echo "  Answer based on possibly-stale wiki. Run /dbt-wiki:refresh for up-to-date answers."
  fi
fi
```

Drift warning is non-fatal — query proceeds with the cached state and
prepends the warning to the final answer.

## Step 1: Read Index

Load `.dbt-wiki/index.md` to see all available models / sources / macros
/ seeds / snapshots / tests / exposures.

## Step 2: Identify Question Type

Match the user's question to a query class. Each class has a different
load pattern:

| Class | Trigger keywords | What to load |
|---|---|---|
| **C1 — Model lookup** | "<model_name> 是什麼", "describe X", "X 的 description" | One model page |
| **C2 — Upstream lineage** | "依賴什麼", "depends on", "上游", "feeds X", "X comes from" | Model page + walk `depends_on` (1-2 levels deep) |
| **C3 — Downstream lineage** | "影響哪些", "feeds into", "下游", "depend on X", "downstream of X" | Model page + walk `feeds_into` (1-2 levels deep) |
| **C4 — Column-level lineage** | "X.col 從哪來", "rename Y 影響什麼", "column lineage", "X 欄位來源", "trace column" | Single model page's `## Column Lineage Chains` body section (precomputed recursive ancestors + descendants — full chain to source / leaf). Single page load answers full DAG question. |
| **C5 — Materialization filter** | "哪些是 table / view / incremental", "incremental in X tier" | index.md "Models by Materialization" section |
| **C6 — Tag / Group filter** | "tag X", "group Y", "marts_msd 下" | index.md "Models by Tag/Group/Tier" |
| **C7 — Test coverage** | "X 有什麼 test", "什麼 test 失敗" | Model page `tests` + (Phase 2) run_results.json |
| **C8 — Source attribution** | "X 從哪個 source", "source freshness" | source pages + model `depends_on.sources` |
| **C9 — Macro usage** | "X macro 在哪用", "用了 dbt_utils.X 的有哪些" | macro page `used_by_models` |
| **C10 — Refactoring impact** | "rename X 影響什麼", "刪掉 X 會壞什麼" | Model page + recursive `feeds_into` (full subtree) |
| **C11 — Schema gaps** | "schema.yml 漏寫的 column", "沒 description 的 model" | Filter all model pages by `declared_in_schema_yml: false` or empty description |

## Step 3: Load Relevant Pages

Load **only the pages needed for the question class**. Never load all of `models/`.

For C1: load 1 page.
For C2/C3: load target + 1 hop upstream/downstream (typically 3-10 pages).
For C4: load target + ALL ancestors in upstream chain (potentially 5-20 pages).
For C5/C6: load index.md only (sections are self-contained).
For C7/C8: load 1-3 pages.
For C9: load 1 macro page.
For C10: load target + full downstream subtree (could be 20+ pages — warn if >30).
For C11: load index.md statistics + scan all model frontmatter (don't load bodies).

If load count > 30 pages, ask user to narrow the scope before proceeding:
> Question would require loading <N> pages. Narrow scope by tier (e.g., "in marts/")
> or specific model name? (Or type "yes" to load all.)

## Step 4: Synthesize Answer with Citations

For each claim in the answer, cite the source `.dbt-wiki/...` page using
markdown links: `[fct_orders](.dbt-wiki/models/fct_orders.md)`.

For column lineage answers (C4), present in chain form:
```
fct_orders.customer_id ← stg_orders.customer_id ← raw_data.orders_raw.customer_id
                       ← stg_customers.id (COALESCE — see fct_orders.md SQL Preview)
```

For refactoring impact (C10), present as tree:
```
Renaming stg_customers.email affects:
├── int_customer_enriched (column: contact_email)
│   ├── fct_orders (column: customer_email)
│   │   └── mart_finance_daily
│   └── dim_customers
└── exposure: customer_dashboard
```

## Step 5: Verification (Optional, T-trigger style)

Same Eager verification model as repo-wiki, adapted for dbt:

| Trigger | Action |
|---|---|
| **DT1** | Page `last_updated > 30 days` (dbt projects move fast) → warn "wiki may be stale; re-refresh" |
| **DT2** | Question contains current-state keyword ("currently", "now", "目前") → also read `target/manifest.json` directly to verify model still exists |
| **DT3** | Question is about column existence ("does X have column Y") → cross-check both wiki page AND grep compiled SQL for Y |
| **DT4** | drift_warning fired in Step 0 → automatically inject "Verified Against Cache" caveat in output |

If any trigger fires, prepend to answer:

```
## ⚠ Verification Notes
- Wiki manifest_sha: <wiki_sha> (current: <current_sha if differs>)
- Pages older than 30 days: <list>
- Recommend: /dbt-wiki:refresh before relying on this answer
```

## Step 6: Present Answer

Standard format:

```
[Direct answer in 1-3 sentences.]

[Detailed breakdown if needed: list, tree, or column-chain notation.]

**Sources consulted**:
- [<page_name>](.dbt-wiki/<type>/<file>.md)
- ...
```

For drift-warned answers, prepend the verification notes block from Step 5.

## Step 7: Append Query Log

```
## [<date>] query | <question-slug>
- Class: <C1-C11>
- Pages loaded: <list, max 10 shown>
- Verification triggered: <DT1/DT2/DT3/DT4 list, or "none">
- Drift warning: <yes/no>
```

## Cross-skill Integration

If `.repo-wiki/` also exists in this repo:

- For questions about WHY (decisions, refactor reasoning), suggest `/repo-wiki:query` instead
- For questions blending STRUCTURE + WHY (e.g., "為什麼 fct_orders 用 incremental，現在依賴什麼"), answer the structure part from dbt-wiki and suggest user follow up with `/repo-wiki:query` for the why
- Cross-link in answer: `Decision context: see [.repo-wiki/sources/...](../.repo-wiki/sources/...)`

## Gap Handling

If no relevant pages exist for the question (e.g., model name not found):

> No model named "X" found in dbt-wiki.
>
> - Did you mean: <fuzzy-matched suggestions from index.md>?
> - If "X" was just added to dbt: run `/dbt-wiki:refresh`
> - If "X" was renamed: search `.dbt-wiki/_archive/` for the old name

For partial answers (e.g., column lineage extraction failed for the
target model), explicitly mark:

> Column-level lineage for fct_orders is unavailable (sqlglot parse failed
> on this model — see .dbt-wiki/log.md). Model-level dependencies are
> still answerable: fct_orders depends on [stg_orders, stg_customers, ...].

## Rules

NEVER:
- Hallucinate model / column names not present in `.dbt-wiki/` pages
- Connect to dbt Cloud or warehouse
- Modify any `.dbt-wiki/` page (query is read-only)
- Skip the drift check (Step 0) — silent stale answers are the worst failure mode
- Load > 30 pages without asking user to narrow scope first
- Use `[[wikilinks]]` — only standard markdown links

ALWAYS:
- Cite every claim with markdown link to `.dbt-wiki/<page>`
- Identify question class (C1-C11) before loading pages — minimizes load
- Include drift warning in output if Step 0 detected mismatch
- For column-lineage questions, traverse `columns[].sources` chains
- For refactoring-impact questions, traverse `feeds_into` recursively
- Suggest `/dbt-wiki:refresh` when wiki is stale, not just in errors
- Cross-link to `.repo-wiki/` for WHY questions if both plugins installed
- Append to log.md every query (even no-match ones)
