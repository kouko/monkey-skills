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

# dbt-wiki — Query Workflow (v2.0)

Read-only knowledge base query. `.dbt-wiki/` holds two layers: a
**knowledge layer** (`entities/`, `metrics/`, `concepts/` — LLM-distilled
business meaning) and an **evidence layer** (`_evidence/` — mechanical
manifest + sqlglot extraction). Query loads the knowledge layer first;
structural evidence is the backing source. `manifest_sha` drift is checked
and surfaced when the evidence layer may be stale.

## Pre-condition Check (Step 0)

```bash
# WIKI_DIR = git repo root (where .dbt-wiki/ lives); fallback to current $PWD.
# Same logic as init Step 0pre — query must look at the SAME location
# init wrote to, regardless of where the user invoked query from.
WIKI_DIR=$(git rev-parse --show-toplevel 2>/dev/null) || WIKI_DIR="$PWD"
cd "$WIKI_DIR" || { echo "Cannot cd to $WIKI_DIR"; exit 1; }

test -d .dbt-wiki || { echo "Knowledge base not initialized at $WIKI_DIR/.dbt-wiki/. Run /dbt-wiki:init first."; exit 1; }
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

Load `.dbt-wiki/index.md`. The index is **knowledge-first**: it leads with
the `## Entities`, `## Metrics`, and `## Concepts` sections (LLM-distilled
knowledge pages), followed by structural evidence sections (`## Evidence:
Models`, `## Evidence: Sources`, etc.). Prefer answering from the knowledge
layer when the question is about *meaning, definition, or relationships*;
fall back to the evidence layer (`_evidence/`) for structural / lineage
queries (C1–C11).

## Step 2: Identify Question Type

Match the user's question to a query class. **Semantic classes (K1–K3)
are the primary path** — they answer business-language questions from the
knowledge layer. Structural classes (C1–C11) are the secondary path for
DAG / lineage / config questions that require evidence-layer detail.

### Semantic query classes (knowledge layer — answer first from here)

| Class | Trigger keywords | What to load |
|---|---|---|
| **K1 — Knowledge / definition** | "X 是什麼意思", "解釋這個指標", "what does churn mean", "定義", "什麼是 X", "explain X", "什麼是 Customer" | Load the matching `entities/`, `metrics/`, or `concepts/` knowledge page (covers all three knowledge-page types — entity, metric, or concept lookups). If no match, fall back to evidence-layer description. Cite `_evidence/` pages listed in the knowledge page's `## Evidence` section as backing evidence. |
| **K2 — Relationship traversal** | "哪些實體/指標跟 Y 有關", "what metrics relate to Customer", "X 跟哪些指標有關聯", "how is X connected to Y" | Load the matching knowledge page(s) + walk their `## Relationships` typed edges (frontmatter `relationships:` + body section). For each related page, load its `summary` frontmatter (avoid full-body load unless needed). Cite `_evidence/` pages as backing. |
| **K3 — Domain landscape** | "這份資料在講什麼", "give me the landscape of X", "這個專案有哪些業務實體和指標", "overview", "全貌", "domain overview" | Load `index.md` `## Entities` + `## Metrics` + `## Concepts` sections (summary lines only). Then load the 2-3 most relevant knowledge pages for depth. Do NOT load all evidence-layer model pages — knowledge index is self-contained for landscape queries. |

### Structural query classes (evidence layer — for DAG / config / lineage detail)

| Class | Trigger keywords | What to load |
|---|---|---|
| **C1 — Model lookup** | "<model_name> 是什麼", "describe X", "X 的 description" | One evidence model page: `.dbt-wiki/_evidence/models/<name>.md` |
| **C2 — Upstream lineage** | "依賴什麼", "depends on", "上游", "feeds X", "X comes from" | Evidence model page + walk `depends_on` (1-2 levels deep) from `_evidence/models/` |
| **C3 — Downstream lineage** | "影響哪些", "feeds into", "下游", "depend on X", "downstream of X" | Evidence model page + walk `feeds_into` (1-2 levels deep) from `_evidence/models/` |
| **C4 — Column-level lineage** | "X.col 從哪來", "rename Y 影響什麼", "column lineage", "X 欄位來源", "trace column" | Single evidence model page's `## Column Lineage Chains` body section from `.dbt-wiki/_evidence/models/<name>.md` (precomputed recursive ancestors + descendants — full chain to source / leaf). |
| **C5 — Materialization filter** | "哪些是 table / view / incremental", "incremental in X tier" | index.md `## Evidence: Models by Materialization` section |
| **C6 — Tag / Group filter** | "tag X", "group Y", "marts_msd 下" | index.md `## Evidence: Models by Tag/Group/Tier` |
| **C7 — Test coverage** | "X 有什麼 test", "什麼 test 失敗" | Evidence model page `tests` from `_evidence/models/` + (Phase 2) run_results.json |
| **C8 — Source attribution** | "X 從哪個 source", "source freshness" | Evidence source pages from `_evidence/sources/` + model `depends_on.sources` |
| **C9 — Macro usage** | "X macro 在哪用", "用了 dbt_utils.X 的有哪些" | Evidence macro page `used_by_models` from `_evidence/macros/` |
| **C10 — Refactoring impact** | "rename X 影響什麼", "刪掉 X 會壞什麼" | Evidence model page + recursive `feeds_into` (full subtree) from `_evidence/models/` |
| **C11 — Schema gaps** | "schema.yml 漏寫的 column", "沒 description 的 model" | Filter all evidence model pages from `_evidence/models/` by `declared_in_schema_yml: false` or empty description |

## Step 3: Load Relevant Pages

Load **only the pages needed for the question class**.

**Knowledge-layer classes (K1–K3):**
For K1: load 1 knowledge page from `entities/`, `metrics/`, or `concepts/`. If the
  knowledge page has an `## Evidence` section, note those `_evidence/` pages as
  backing — load them only if the user asks for structural detail.
For K2: load the target knowledge page + summary frontmatter of directly linked
  knowledge pages (via `relationships:`). Typically 2-5 pages total.
For K3: load `index.md` knowledge sections only (no evidence model pages).
  Optionally load 2-3 full knowledge pages for depth.

**Evidence-layer classes (C1–C11):** Never load all of `_evidence/models/`.
For C1: load 1 page from `_evidence/models/`.
For C2/C3: load target + 1 hop upstream/downstream from `_evidence/models/`
  (typically 3-10 pages).
For C4: load target + ALL ancestors in upstream chain from `_evidence/models/`
  (potentially 5-20 pages).
For C5/C6: load index.md evidence sections only (self-contained).
For C7/C8: load 1-3 pages from `_evidence/models/` and/or `_evidence/sources/`.
For C9: load 1 macro page from `_evidence/macros/`.
For C10: load target + full downstream subtree from `_evidence/models/`
  (could be 20+ pages — warn if >30).
For C11: load index.md statistics + scan frontmatter of `_evidence/models/`
  pages (don't load bodies).

If load count > 30 pages, ask user to narrow the scope before proceeding:
> Question would require loading <N> pages. Narrow scope by tier (e.g., "in marts/")
> or specific model name? (Or type "yes" to load all.)

## Step 4: Synthesize Answer with Citations

For each claim in the answer, cite the source `.dbt-wiki/...` page using
markdown links.

**Knowledge-layer answers (K1–K3):** cite the knowledge page as primary source,
then cite the `_evidence/` backing pages listed in its `## Evidence` section:
- Primary: `[Customer](.dbt-wiki/entities/customer.md)`
- Backing evidence: `[stg_customers](.dbt-wiki/_evidence/models/stg_customers.md)`

**Evidence-layer answers (C1–C11):** cite directly from `_evidence/`:
- `[fct_orders](.dbt-wiki/_evidence/models/fct_orders.md)`
- `[raw_data.orders_raw](.dbt-wiki/_evidence/sources/raw_data__orders_raw.md)`

For column lineage answers (C4), present in chain form:
```
fct_orders.customer_id ← stg_orders.customer_id ← raw_data.orders_raw.customer_id
                       ← stg_customers.id (COALESCE — see _evidence/models/fct_orders.md SQL Preview)
```

For refactoring impact (C10), present as tree (or use Step 4.5 diagrams).

## Step 4.5: Generate Lineage Diagrams (lineage-class queries only)

For C2 (upstream model), C3 (downstream model), C4 (column lineage), and
C10 (refactoring impact) classes, generate ASCII tree + Mermaid graph
via the `format_lineage_diagram.py` helper. Other classes (C1 / C5–C9 /
C11) skip this step — pure text answer is appropriate.

Invocation depends on class:

```bash
# C4 / C10 (column-level): consumes recursive lineage JSONL produced at init
$PY_RUNNER .dbt-wiki/_internal/format_lineage_diagram.py column \
    --recursive-jsonl /tmp/dbt-wiki-recursive-lineage.jsonl \
    --model <model_uid> --column <column_name> \
    --direction <ancestors|descendants|both> \
    --max-nodes 30

# C2 / C3 (model-level): consumes manifest.json directly
$PY_RUNNER .dbt-wiki/_internal/format_lineage_diagram.py model \
    --manifest "$DBT_DIR/target/manifest.json" \
    --model <model_uid> \
    --direction <ancestors|descendants|both> \
    --max-depth 3 --max-nodes 30
```

Output is JSON with `ascii`, `mermaid`, `node_count`, `truncated` keys.

**Inclusion rules in the answer**:

- ASCII tree → ALWAYS include in the chat answer (renders in any terminal)
- Mermaid block → include in synthesis save (Step 5) and mention in chat
  with note: "Mermaid diagram saved to `.dbt-wiki/syntheses/<slug>.md` —
  open in your IDE (Dataspell / VS Code / Cursor / Obsidian) or on
  GitHub for rendered preview"
- If `truncated: true` (>30 nodes), prepend a note in the answer:
  "Diagram truncated to 30 nodes; see [full lineage](.dbt-wiki/lineage.md)
  for complete DAG"

`/tmp/dbt-wiki-recursive-lineage.jsonl` is generated at init time and
refreshed by `/dbt-wiki:refresh`. If missing, fall back to model-level
diagram only (C2/C3 still work; C4/C10 emit the chain form from Step 4).

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
- [<page_name>](.dbt-wiki/entities/<file>.md)       ← knowledge layer
- [<page_name>](.dbt-wiki/_evidence/models/<file>.md)  ← evidence layer backing
- ...
```

For drift-warned answers, prepend the verification notes block from Step 5.

## Step 6.5: Auto-save synthesis (lineage / decision queries)

For K2 (relationship traversal) and C2/C3/C4/C9/C10 (queries about lineage,
macro usage, or refactoring impact — answers that have lasting value),
auto-save the answer to `.dbt-wiki/syntheses/<slug>.md` so it can be
re-opened in the IDE for the rendered Mermaid diagram + serve as a future
reference.

For K1/K3 (definition, landscape) and C1/C5/C6/C7/C8/C11 (model lookup,
materialization filters, schema gaps — short-lived informational queries),
do NOT auto-save unless user explicitly asks: ask
`Save this answer to .dbt-wiki/syntheses/? (y/n)`.

Slug = first 6-8 words of the question, kebab-case, lowercase. Collisions
appended with `-2`, `-3`, …

Use `assets/synthesis_template.md` (copied to `.dbt-wiki/_internal/` at
init time) as the markdown shape. Frontmatter required fields:

```yaml
---
type: synthesis
question: "<exact question>"
slug: <slug>
date: <YYYY-MM-DD>
manifest_sha: <current sha — used by refresh for stale detection>
affected_models:                 # critical for stale detection
  - <model.proj.X>
  - <model.proj.Y>
query_class: <K1-K3 or C1-C11>
diagram_included: <yes | no>
sources_consulted:
  - entities/<name>.md
  - _evidence/models/<name>.md
verification_run: <yes | no>
verified_paths: []
stale: false                     # refresh sets to true when affected_models change
stale_at: null
---
```

`affected_models` is the union of:
- For K1/K2/K3: the `derived_from` evidence `unique_id` values listed in
  each consulted knowledge page's frontmatter
- For C4 column-lineage answers: target model + every model touched
  in the recursive ancestor + descendant trees
- For C2/C3 model-lineage answers: target model + every model in the
  rendered ASCII / Mermaid

This list lets `/dbt-wiki:refresh` (Step 7) precisely detect stale
syntheses without false positives from unrelated manifest changes.

## Step 7: Append Query Log

```
## [<date>] query | <question-slug>
- Class: <K1-K3 or C1-C11>
- Pages loaded: <list, max 10 shown>
- Verification triggered: <DT1/DT2/DT3/DT4 list, or "none">
- Drift warning: <yes/no>
- Synthesis saved: .dbt-wiki/syntheses/<slug>.md  (or "no")
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
- Cite structural evidence paths as `.dbt-wiki/models/<name>.md` — always use
  `.dbt-wiki/_evidence/models/<name>.md` (v2.0 layout)

ALWAYS:
- Cite every claim with markdown link to `.dbt-wiki/<page>`
- Identify question class (K1–K3 or C1–C11) before loading pages — minimizes load
- Try knowledge layer (K1–K3) first for definition / relationship / landscape
  questions; fall back to evidence layer only if no knowledge page matches
- For knowledge-layer answers, cite `_evidence/` pages as backing evidence
  (sourced from the knowledge page's `## Evidence` / `derived_from` frontmatter)
- Include drift warning in output if Step 0 detected mismatch
- For column-lineage questions, traverse `columns[].sources` chains in
  `_evidence/models/`
- For refactoring-impact questions, traverse `feeds_into` recursively in
  `_evidence/models/`
- Suggest `/dbt-wiki:refresh` when wiki is stale, not just in errors
- Cross-link to `.repo-wiki/` for WHY questions if both plugins installed
- Append to log.md every query (even no-match ones)
