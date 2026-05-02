---
name: init
description: |
  First-time setup for dbt-wiki: scaffold .dbt-wiki/ knowledge base
  from target/manifest.json + target/compiled/**/*.sql (parsed via
  sqlglot for column-level lineage). Generates one markdown page per
  model / source / macro / seed / snapshot, plus index + lineage DAG.
  Pre-condition: user must have run `dbt parse && dbt compile` first.
  Triggers on "init dbt-wiki", "set up dbt-wiki", "scaffold dbt model
  knowledge base", "/dbt-wiki:init", "初始化 dbt-wiki", "建立 dbt 知識庫".
  Do NOT trigger for: incremental updates after dbt parse (use
  /dbt-wiki:refresh), answering questions (use /dbt-wiki:query).
---

# dbt-wiki — Init Workflow (v1.0)

Init is **idempotent and re-runnable**. Default mode reads `manifest.json`
+ all `compiled/*.sql` files, generates per-model entity pages with
column-level lineage from sqlglot, plus index/lineage. Re-run merges:
preserves cross-references to `.repo-wiki/`, refreshes manifest-derived
fields, and archives orphaned models.

The `.dbt-wiki/` directory is owned entirely by dbt-wiki skills.
Source layer (`dbt/**` + `target/**`) is immutable — never modify
input files. Init **reads** manifest.json + compiled SQL; it does NOT
modify any dbt project file.

## Pre-condition Check (Step 0)

```bash
# Resolve dbt project root from common locations
DBT_DIR=""
for candidate in "dbt" "."; do
  if [ -f "$candidate/dbt_project.yml" ]; then
    DBT_DIR="$candidate"
    break
  fi
done

if [ -z "$DBT_DIR" ]; then
  echo "Cannot find dbt_project.yml. Looked in: dbt/, ./"
  echo "If your dbt project is elsewhere, run init from inside the dbt project root."
  exit 1
fi

# Verify required artifacts
test -f "$DBT_DIR/target/manifest.json" || {
  echo "Missing $DBT_DIR/target/manifest.json"
  echo "Run: cd $DBT_DIR && dbt parse"
  exit 1
}

test -d "$DBT_DIR/target/compiled" || {
  echo "Missing $DBT_DIR/target/compiled/"
  echo "Run: cd $DBT_DIR && dbt compile"
  exit 1
}

# Verify sqlglot installed
python3 -c "import sqlglot; print('sqlglot', sqlglot.__version__)" || {
  echo "sqlglot not installed. Run: pip install sqlglot"
  exit 1
}
```

If any check fails, print the error and exit. Do not proceed.

If `.dbt-wiki/` already exists, set `is_rerun = true` and prompt:

> `.dbt-wiki/` already exists. Re-running init will:
>  - **Preserve** `log.md` (append a new init entry)
>  - **Refresh** all model / source / macro pages from current manifest
>  - **Archive** orphaned models (those no longer in manifest) to `.dbt-wiki/_archive/<date>/`
>  - **Regenerate** `index.md` and `lineage.md`
>  - **Overwrite** `SCHEMA.md` (frozen schema; plugin-controlled)
>  - **Never touch** any cross-references you've added to model bodies under custom sections
>
>  Continue? (yes/no)

Abort on "no". Proceed only if "yes" or fresh install.

## Step 1: Scaffold Directory

`mkdir -p` is always safe (no-op if dirs exist):

```bash
mkdir -p .dbt-wiki/models
mkdir -p .dbt-wiki/sources
mkdir -p .dbt-wiki/macros
mkdir -p .dbt-wiki/seeds
mkdir -p .dbt-wiki/snapshots
mkdir -p .dbt-wiki/tests
mkdir -p .dbt-wiki/exposures
mkdir -p .dbt-wiki/_archive
```

Copy plugin templates with **conditional rules**:

| Target | First-run | Re-run |
|---|---|---|
| `.dbt-wiki/SCHEMA.md` | Copy from `assets/SCHEMA.md` | **Always overwrite** (frozen schema) |
| `.dbt-wiki/index.md` | Copy from `assets/index.md` | Step 6 regenerates from current node listing |
| `.dbt-wiki/lineage.md` | Copy from `assets/lineage.md` | Step 5 regenerates from current manifest |
| `.dbt-wiki/log.md` | Copy from `assets/log.md` | **Skip if exists** (Step 7 appends new init entry) |

(Resolve asset paths relative to this SKILL.md location: `assets/<file>.md`.)

## Step 2: CLAUDE.md Drop-in

Read or create `CLAUDE.md` in the **repo root** (not the dbt project subdir).
The drop-in block is in `assets/claude-md-snippet.md`.

Write rules (idempotent):
- If `CLAUDE.md` doesn't exist: create it with just the dbt-wiki block
- If `CLAUDE.md` exists but has no `<!-- dbt-wiki:start -->` marker: append the block
- If `CLAUDE.md` exists with the markers: replace the block between
  `<!-- dbt-wiki:start -->` and `<!-- dbt-wiki:end -->`

Never touch `CLAUDE.md` content outside the dbt-wiki marked block.
(Note: this preserves any existing `<!-- repo-wiki:start --> ... <!-- repo-wiki:end -->`
block if both plugins are installed.)

## Step 3: Parse manifest.json

```bash
MANIFEST="$DBT_DIR/target/manifest.json"
MANIFEST_SHA=$(md5 -q "$MANIFEST" 2>/dev/null || md5sum "$MANIFEST" | cut -d' ' -f1)
```

Use `jq` to extract structured data:

```bash
# Count nodes by type for sanity log
jq '.nodes | to_entries | map(.value.resource_type) | group_by(.) | map({type: .[0], count: length})' "$MANIFEST"
```

Expected resource_types: `model`, `seed`, `snapshot`, `test`, `analysis`, `operation`.
Sources are under `.sources`, macros under `.macros`, exposures under `.exposures`.

For each `model` node, capture:
- `unique_id`, `name`, `package_name`, `path`, `original_file_path`
- `config.materialized`, `config.tags`, `config.schema`, `config.database`, `config.alias`
- `config.contract.enforced`
- `group`, `access`
- `description`, `columns` (with `name`, `description`, `data_type`, `meta`)
- `depends_on.nodes` (refs to other models / seeds / snapshots) and `depends_on.macros`
- `sources` references inferred from depends_on (those starting with `source.`)
- `raw_code` (for SQL preview)
- `tests` (extracted from depends_on of test nodes that target this model — see Step 3a)

### Step 3a: Test attachment

Tests in dbt's manifest are separate `test` nodes. To attach tests to
their target model, scan all `test` nodes and check `attached_node` (or
fall back to `depends_on.nodes` containing exactly one model id):

```python
# Pseudocode
tests_by_model = {}
for test_id, test_node in manifest['nodes'].items():
    if test_node.get('resource_type') != 'test':
        continue
    target = test_node.get('attached_node')
    if not target:
        # Fallback: find single model in depends_on
        model_deps = [d for d in test_node['depends_on']['nodes'] if d.startswith('model.')]
        if len(model_deps) == 1:
            target = model_deps[0]
    if target:
        tests_by_model.setdefault(target, []).append({
            'name': test_node['name'],
            'column': test_node.get('column_name'),  # null for model-level tests
            'test_metadata': test_node.get('test_metadata', {}),  # generic test details
        })
```

### Step 3b: feeds_into reverse lookup

For each model in manifest, build `feeds_into` by inverting `depends_on`:

```python
feeds_into = {}
for node_id, node in manifest['nodes'].items():
    if node.get('resource_type') not in ('model', 'snapshot'):
        continue
    for dep in node['depends_on']['nodes']:
        feeds_into.setdefault(dep, []).append(node['name'])
```

## Step 4: Column-Level Lineage via sqlglot

For each model, parse its compiled SQL with sqlglot to extract per-column
sources. **Critical**: parse `compiled/*.sql`, NOT `raw_code` (jinja-laden).

```bash
# Find compiled file for a model
COMPILED_PATH="$DBT_DIR/target/compiled/$PROJECT_NAME/${original_file_path}"
# original_file_path is from manifest, e.g., "models/marts/fct_orders.sql"
```

Use the following Python script (invoke once per model via Bash, or batch):

```python
#!/usr/bin/env python3
"""sqlglot column lineage extractor for one compiled SQL file."""
import json
import sys
import sqlglot
from sqlglot import exp
from sqlglot.optimizer.scope import build_scope

def extract_column_lineage(sql: str, dialect: str = "redshift") -> dict:
    """Returns {column_name: [list of "table.column" sources]}.

    Handles top-level SELECT, CTEs, and joins. For column expressions
    (CASE WHEN, COALESCE, function calls), all referenced columns become
    sources for the output column.
    """
    try:
        ast = sqlglot.parse_one(sql, dialect=dialect)
    except Exception as e:
        return {"_error": f"parse failed: {e}"}

    # Find the outermost SELECT
    if not isinstance(ast, exp.Select) and not ast.find(exp.Select):
        return {"_error": "no SELECT found"}
    outer = ast if isinstance(ast, exp.Select) else ast.find(exp.Select)

    # Use sqlglot's scope/lineage helper for accurate resolution
    scope = build_scope(ast)
    if not scope:
        return {"_error": "scope build failed"}

    column_sources = {}
    for projection in outer.expressions:
        # Get output column name
        if isinstance(projection, exp.Alias):
            out_name = projection.alias
            expr = projection.this
        elif isinstance(projection, exp.Column):
            out_name = projection.alias_or_name
            expr = projection
        else:
            out_name = projection.alias_or_name or "<unnamed>"
            expr = projection

        # Walk expr to find all Column references
        sources = set()
        for col in expr.find_all(exp.Column):
            table = col.table or "<unqualified>"
            col_name = col.name
            sources.add(f"{table}.{col_name}")

        column_sources[out_name] = sorted(sources)

    return column_sources

if __name__ == "__main__":
    sql = open(sys.argv[1]).read()
    dialect = sys.argv[2] if len(sys.argv) > 2 else "redshift"
    print(json.dumps(extract_column_lineage(sql, dialect), indent=2))
```

**Save this script** as `.dbt-wiki/_internal/extract_column_lineage.py`
(create `_internal/` dir under `.dbt-wiki/`; this is the only place dbt-wiki
puts non-markdown files).

For each model, invoke:

```bash
python3 .dbt-wiki/_internal/extract_column_lineage.py \
    "$DBT_DIR/target/compiled/$PROJECT_NAME/${original_file_path}" \
    redshift > /tmp/col_lineage_$model_name.json
```

(Adjust `redshift` to actual dialect — read from `dbt_project.yml`'s
`profile`, or default to redshift if unknown.)

### Step 4a: Reconcile sqlglot output with manifest columns

For each model:

```python
manifest_columns = {c['name']: c for c in model['columns'].values()}  # from schema.yml
sqlglot_columns = json.load(open(f"/tmp/col_lineage_{model_name}.json"))

merged = {}
for col_name in set(manifest_columns) | set(sqlglot_columns):
    merged[col_name] = {
        'name': col_name,
        'declared_in_schema_yml': col_name in manifest_columns,
        'description': manifest_columns.get(col_name, {}).get('description', ''),
        'type': manifest_columns.get(col_name, {}).get('data_type', None),
        'tests': [t['name'] for t in tests_by_model.get(model['unique_id'], []) if t.get('column') == col_name],
        'sources': sqlglot_columns.get(col_name, []),  # may be empty if sqlglot missed
    }
```

Track failures: if sqlglot returned `_error`, mark model with
`columns_extracted_via: failed` and log reason. The model page still
gets created — just with no `sources:` per column.

## Step 5: Write Model / Source / Macro Pages

For each model, write `.dbt-wiki/models/<model_name>.md` per the SCHEMA.md
`model` page type. Filename collision: if `<model_name>.md` exists from
a different package (different `unique_id`), use `<package>__<model_name>.md`.

For each source (from `manifest.sources`), write
`.dbt-wiki/sources/<source_name>__<table_name>.md` per SCHEMA's `source`
type. Compute `feeds_into` similarly to Step 3b.

For each macro that is referenced by ≥1 model (filter `manifest.macros`
by checking which appear in any model's `depends_on.macros`), write
`.dbt-wiki/macros/<macro_name>.md`. Project macros first, then external
package macros (dbt_utils, dbt_expectations, etc.).

For seeds, snapshots, exposures, singular tests: same pattern, one page per
resource, frontmatter from manifest.

### Re-run merge behavior

When `is_rerun = true` and a model page already exists:

1. Read existing frontmatter and body
2. Build new frontmatter from current manifest + sqlglot
3. Detect custom body sections (anything outside the standard sections defined in SCHEMA.md):
   - Standard: `## Description`, `## Materialization Notes`, `## SQL Preview`,
     `## Column Sources (from sqlglot)`, `## Tests`, `## Cross-references`
   - Custom: any other `##` section the user added
4. Write new file: new frontmatter + standard sections regenerated +
   custom sections preserved verbatim at the end
5. If new manifest doesn't contain a model previously documented:
   move `.dbt-wiki/models/<orphaned>.md` to `.dbt-wiki/_archive/<today>/<orphaned>.md`,
   don't hard-delete

## Step 6: Generate index.md and lineage.md

### index.md

Regenerate from current page listing. Group by:
- Tier path (extract from `path`: `models/staging/` → Staging, `models/marts/` → Marts, etc.)
- Materialization (from frontmatter)
- Tags
- Groups
- Then: Sources, Macros (project + external), Seeds, Snapshots, Singular Tests, Exposures

Statistics block at end:
- Total models, sources, macros (used)
- Column lineage extraction success rate (count + percent)
- sqlglot parse failures (count, link to log.md)

### lineage.md

For each declared source/seed (root nodes), do depth-first traversal
producing ASCII tree. Mark first-occurrence with `→`, repeats with `↺`.

For each model, add an adjacency list entry: depends_on (refs / sources / macros)
+ feeds_into.

If model count > 500, also produce tier-aggregated view at top.

## Step 7: Append init entry to log.md

```
## [<date>] init | <N> models, <M> sources, <K> macros (used)
- manifest_sha: <sha>
- compiled_files_parsed: <count>
- sqlglot_failures: <count>
  - <model_name>: <truncated reason>
  - ... (max 10 listed; full list in /tmp/dbt-wiki-init-failures.log if generated)
- column_lineage_extracted: <success_count>/<total_models> (<percent>%)
- Pages created (fresh): <models>/<sources>/<macros>/<seeds>/<snapshots>/<tests>/<exposures>
- Pages updated (re-run): <count>
- Pages archived (orphaned): <count>
- Run type: <fresh | re-run>
```

## Step 8: Summary Report

Print to user:

```
✓ dbt-wiki initialized at .dbt-wiki/

  Manifest: <DBT_DIR>/target/manifest.json (sha: <sha>)
  Compiled SQL: <count> files parsed via sqlglot (<dialect>)

  Generated:
    - <N> model pages (column lineage: <success>/<total>)
    - <N> source pages
    - <N> macro pages (used by ≥1 model)
    - <N> seed / <N> snapshot / <N> singular test / <N> exposure
    - lineage.md (DAG depth: <N>; root sources: <N>; leaves: <N>)
    - index.md (grouped by tier / materialization / tag / group)

  Files updated:
    - .dbt-wiki/{SCHEMA,index,log,lineage}.md
    - .dbt-wiki/{models,sources,macros,seeds,snapshots,tests,exposures}/*.md
    - .dbt-wiki/_internal/extract_column_lineage.py
    - CLAUDE.md drop-in (<created/appended/replaced>)

  Next steps:
    1. Skim .dbt-wiki/index.md to see what was discovered
    2. Try a query: /dbt-wiki:query "fct_orders 依賴什麼？"
    3. After next dbt parse + dbt compile, run /dbt-wiki:refresh
    4. (If installed) repo-wiki and dbt-wiki coexist — use repo-wiki for WHY
```

If sqlglot failures > 0, also print:

```
  ⚠ sqlglot failed to parse <N> models. Common causes:
    - Custom Redshift functions not in sqlglot's grammar
    - Extremely large compiled SQL (>50K lines)
    - Macros with conditional SQL generation (jinja edge cases)

  Failed models still have pages (without column-level sources).
  See .dbt-wiki/log.md for full failure list.
```

## Rules

NEVER:
- Modify any file under `dbt/` or `target/` or anywhere outside `.dbt-wiki/` and `CLAUDE.md`
- Hard-delete pages from `.dbt-wiki/` (always archive to `.dbt-wiki/_archive/`)
- Run `dbt parse` / `dbt compile` on user's behalf (user must run; init only checks output exists)
- Connect to dbt Cloud, warehouse, or any external API
- Mutate `manifest.json` or any `target/` file
- Parse `raw_code` directly with sqlglot (always parse `compiled/*.sql` — jinja must be expanded by dbt first)
- Use `[[wikilinks]]` — only standard markdown links: `[Name](path)`
- Touch `CLAUDE.md` content outside the `<!-- dbt-wiki:start/end -->` block
- Skip the sqlglot install check (Step 0) — runtime failures from missing dep are unhelpful

ALWAYS:
- Verify Step 0 pre-conditions before any other action
- Record `manifest_sha` in log.md so refresh can detect drift
- Preserve custom body sections in model pages on re-run (anything outside SCHEMA.md's standard sections)
- Mark column lineage extraction status per model (`columns_extracted_via: sqlglot | schema_yml_only | failed`)
- Filter macros by usage (don't create pages for unused project macros or unused external package macros)
- Compute `feeds_into` reverse lookup so query can answer "what depends on X" without traversing all models
- Use `<package>__<name>.md` filename when same-name resources exist in different packages
