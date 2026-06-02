---
name: to-sql
description: |
  Turn a natural-language business question into a runnable SQL query
  grounded in the dbt-wiki knowledge base. Use this skill when you want
  SQL generated for you — not when you want to understand what data
  means or how models relate.

  **Distinction from `query`**: `query` explains what the data means —
  it answers questions about model structure, column lineage, materialization
  config, and the WHY behind dbt design decisions. `to-sql` generates the
  SQL to answer a business question — it resolves business terms to physical
  columns, assembles join paths, and validates the generated SQL statically.
  When in doubt: if your question is "what does X mean / where does column Y
  come from?" → use `query`. If your question is "write me the SQL that gives
  me X" → use `to-sql`.

  Trigger phrases (EN): "give me the SQL for…", "write a query that…",
  "how do I query…", "SQL to get…", "generate a SELECT for…",
  "write SQL to find…", "/dbt-wiki:to-sql".
  Trigger phrases (zh-TW): "寫個 SQL 查…", "幫我寫查詢…", "給我查 X 的 SQL",
  "怎麼查…", "用 SQL 找出…", "產生 SQL", "to-sql".
  Trigger phrases (ja): "SQLを書いて…", "クエリを生成して…", "〇〇のSQLは？",
  "SQLで取得したい…", "クエリを作って".

  Do NOT trigger for: reading or modifying dbt/models/*.sql directly
  (use Edit tool); running dbt commands (use dbt CLI); understanding
  what a model contains or where a column comes from (use `query`);
  refreshing the wiki (use `refresh`); ingesting business context
  (use `ingest`).

  **Hard boundary**: `to-sql` generates SQL but NEVER executes it and
  NEVER connects to a data warehouse. Validation is static only
  (sqlglot parse + manifest existence check).
---

# dbt-wiki — to-sql Workflow (v1.0)

NL business question → statically-validated SQL, grounded in the
dbt-wiki knowledge base. The pipeline: pre-condition + drift check →
retrieve schema context → assemble generation prompt → generate SQL →
static-validate → present.

This skill uses the same `.dbt-wiki/` knowledge base that `query` reads.
It adds a SQL generation + static validation pass. It is strictly
read-only — it never writes to `.dbt-wiki/` and never executes SQL.

## Step 0: Pre-condition + Drift Check

```bash
# WIKI_DIR = git repo root (same convention as query/SKILL.md Step 0).
WIKI_DIR=$(git rev-parse --show-toplevel 2>/dev/null) || WIKI_DIR="$PWD"
cd "$WIKI_DIR" || { echo "Cannot cd to $WIKI_DIR"; exit 1; }

test -d .dbt-wiki || {
  echo "Knowledge base not initialized at $WIKI_DIR/.dbt-wiki/. Run /dbt-wiki:init first."
  exit 1
}
test -f .dbt-wiki/index.md || {
  echo "Missing .dbt-wiki/index.md — re-run /dbt-wiki:init."
  exit 1
}
```

### Drift check

Same 5-tier manifest detection as `query/SKILL.md` §Step 0. Non-fatal —
if drift is detected, proceed and include a Drift Notice in the output
(see Step 5).

```bash
LAST_SHA=$(grep -m 1 'manifest_sha:' .dbt-wiki/log.md | sed 's/.*manifest_sha: //' | tr -d ' ')

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

DRIFT_WARNING=""
if [ -n "$DBT_DIR" ] && [ -f "$DBT_DIR/target/manifest.json" ]; then
  CURRENT_SHA=$(md5 -q "$DBT_DIR/target/manifest.json" 2>/dev/null \
    || md5sum "$DBT_DIR/target/manifest.json" | cut -d' ' -f1)
  MANIFEST_PATH="$DBT_DIR/target/manifest.json"
  CATALOG_PATH="$DBT_DIR/target/catalog.json"
  if [ "$CURRENT_SHA" != "$LAST_SHA" ]; then
    DRIFT_WARNING="manifest.json changed since last refresh (current: $CURRENT_SHA, wiki: $LAST_SHA)"
  fi
fi
```

Record `$MANIFEST_PATH` and `$CATALOG_PATH` (if exists) — needed for
Step 4 static validation. Drift is non-fatal; surface it in Step 5 if
set.

## Step 1: Retrieve Schema Context

Follow `references/retrieval.md` to gather the schema context needed
for this question.

Key operations (detailed spec in `references/retrieval.md`):

1. **Tier-1 scan** — load `summary:` frontmatter lines from
   `.dbt-wiki/index.md` knowledge sections to identify relevant entity,
   metric, and concept pages without loading full bodies.
2. **Tier-2 load** — for each page identified as relevant, load the
   full body: `entities/<slug>.md` (§ Fields + relationships),
   `metrics/<slug>.md` (§ Materialized Columns if present, § Calculation,
   relationships), `concepts/<slug>.md` (rule body).
3. **Evidence grounding** — load the `_evidence/models/<model>.md`
   pages named in each knowledge page's `## Evidence` section to confirm
   physical column names exist.
4. **Join-path extraction** — derive join paths from `relationships:`
   `joins` edges; do not invent foreign-key names.
5. **Exception handling** — not-found, ambiguous, and too-broad cases
   are handled per `references/retrieval.md` §§5.1–5.3 (stop, ask for
   disambiguation, or request narrowing before proceeding).

Output: a `retrieval_context` bundle (entities, metrics, concepts,
join_paths, evidence_models, pages_consulted) as the sole input to
Step 2.

## Step 2: Assemble Generation Prompt

Follow `references/prompt-assembly.md` to build the SQL generation
prompt from the retrieval context.

Key operations (detailed spec in `references/prompt-assembly.md`):

(Section references below cite prompt-assembly.md by **name and number**;
trust the name if a future renumber makes the number stale.)

1. **Schema-linking** (§1 Schema-Linking) — resolve each business term in
   the question to a physical `model.column` via entity `## Fields` tables,
   confirmed in evidence pages. Do not use a column name not present in an
   evidence page.
2. **Column-card use** (§2 Column-Card Use) — if the metric has
   `## Materialized Columns`, prefer `SELECT <pre-materialized column>`
   over re-aggregating.
3. **Join-path assembly** (§3 Join-Path Assembly) — translate `joins`
   edges into explicit `JOIN ... ON ...` clauses; every JOIN must have an
   ON condition from the knowledge base.
4. **Temporal grounding** (§4 Temporal Grounding) — resolve relative time
   ("last month" / "上個月") against `CURRENT_DATE`; do **not** assume
   `MAX(date_column)` is the latest *actual* period (recognition / forecast
   / amortization tables carry forward-dated rows); honor any date-semantics
   caveat on the knowledge page and surface the temporal assumption made.
5. **Few-shot slot** (§5 Few-Shot Slot) — v1 ships zero-shot; the prompt
   includes an empty `<!-- EXAMPLES START --> <!-- EXAMPLES END -->` block
   reserved for the gold-example increment.
6. **Dialect rule** (§7 Dialect Rule) — read `metadata.adapter_type` from
   `manifest.json`; pass to sqlglot; state in the prompt.

Assemble the prompt per the template in `references/prompt-assembly.md`
§6 (Prompt Template) and pass it to the model.

## Step 3: Generate SQL

Submit the assembled prompt to the model. The model returns a single
SQL query conforming to the output requirements in
`references/prompt-assembly.md` §6 Prompt Template (`## Output Requirements` block):

- Returns only valid SQL (no markdown fences in the raw output).
- References only schema context provided.
- Uses `-- UNRESOLVED: <term>` comments for any term that could not
  be schema-linked.

Capture the raw SQL string for Step 4.

## Step 4: Static Validate

Run `assets/validate_sql.py` against the generated SQL and the current
manifest. This step is **mandatory** — do not present SQL that has not
been validated.

**Invocation (as Python module):**

```python
import sys
sys.path.insert(0, "<skill_dir>/assets")  # absolute path to to-sql/assets/
from validate_sql import extract_refs, check_refs_against_manifest

sql = "<generated SQL from Step 3>"
dialect = "<adapter_type from manifest, or None>"

refs = extract_refs(sql, dialect=dialect)
if not refs["ok"]:
    # sqlglot parse failed — surface error, ask user to clarify question
    validation_result = {"status": "FAIL", "parse": refs["error"],
                         "missing_tables": [], "missing_columns": []}
else:
    manifest_check = check_refs_against_manifest(
        refs,
        manifest_path="<MANIFEST_PATH>",
        catalog_path="<CATALOG_PATH if exists, else None>",
    )
    status = "PASS" if manifest_check["ok"] else "PARTIAL"
    validation_result = {
        "status": status,
        "parse": "OK",
        "missing_tables": manifest_check["missing_tables"],
        "missing_columns": manifest_check["missing_columns"],
    }
```

**If `missing_tables` or `missing_columns` are non-empty**: do not
present the SQL as-is. Surface the missing references, identify which
schema-linking step produced the erroneous column/table name, revise
the SQL to remove hallucinated references or replace with
`-- UNRESOLVED: <term>`, and re-run validation. Only present SQL after
at least one revision pass.

**If parse fails**: return the parse error in the output and ask the
user to clarify the question rather than presenting broken SQL.

## Step 5: Present

Return the result per the output contract in
`references/prompt-assembly.md` §8 Output Contract. All required fields:

```
## SQL
```sql
<the validated SQL>
```

## Sources
- [<page title>](.dbt-wiki/entities/<file>.md)
- [<page title>](.dbt-wiki/metrics/<file>.md)
- [<page title>](.dbt-wiki/_evidence/models/<file>.md)
- ...

## Validation
Status: PASS | PARTIAL | FAIL
Parse: OK | <sqlglot error message>
Missing tables: <list or "none">
Missing columns: <list of model.column pairs or "none">
```

If drift was detected in Step 0, append:

```
## Drift Notice
The wiki was last refreshed against manifest sha <WIKI_SHA>.
The current manifest sha is <CURRENT_SHA>.
Static validation ran against the CURRENT manifest, but schema-linking
used knowledge pages that may reflect an older model structure.
Run /dbt-wiki:refresh to re-sync the knowledge base.
```

## Boundary

`to-sql` **NEVER**:
- Executes SQL or connects to any data warehouse.
- Validates SQL by running it (static parse + manifest check only).
- Writes to `.dbt-wiki/` (read-only consumer).
- Presents SQL that has not passed Step 4 static validation.
- Invents table names, column names, or join keys not present in a
  `.dbt-wiki/` knowledge or evidence page.

If a business term cannot be grounded to the knowledge base, stop and
report rather than guessing.

## Cross-skill Notes

- Use `query` before `to-sql` if you need to understand the data model
  first (e.g., "what entity represents a paid order?" → `query`;
  "give me the SQL for paid orders by store" → `to-sql`).
- If `.repo-wiki/` exists in the repo, cross-link decision context for
  WHY questions per `query/SKILL.md §Cross-skill Integration`.
