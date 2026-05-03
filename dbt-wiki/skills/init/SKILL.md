---
name: init
description: |
  First-time setup for dbt-wiki: scaffold .dbt-wiki/ knowledge base from
  target/manifest.json (model / source / macro / seed / snapshot / test /
  exposure metadata, ref/source dependencies, schema.yml columns and
  tests), plus target/compiled/<project>/**/*.sql parsed via sqlglot for
  column-level lineage, plus dbt/models/**/*.sql raw files parsed via
  regex for inline SQL/jinja comments. Generates one markdown page per
  resource, plus index.md (grouped by tier / materialization / tag /
  group), lineage.md (ASCII DAG + adjacency list), log.md, SCHEMA.md,
  and an idempotent CLAUDE.md drop-in. Re-runnable: refreshes
  manifest-derived fields, archives orphans, preserves user-owned body
  sections.
  Pre-condition: dbt parse && dbt compile must be run first (init
  checks for target/manifest.json and target/compiled/), and sqlglot
  must be installed (pip install sqlglot).
  Triggers on "init dbt-wiki", "set up dbt-wiki", "scaffold dbt
  knowledge base", "seed dbt model wiki", "build dbt-wiki from
  manifest", "first-time dbt knowledge", "/dbt-wiki:init",
  "初始化 dbt-wiki", "建立 dbt 知識庫", "從 manifest 建立 dbt wiki",
  "dbt-wiki 第一次", "scaffold dbt knowledge", "dbt-wiki セットアップ".
  Do NOT trigger for: incremental updates after dbt parse (use
  /dbt-wiki:refresh), adding user context / tribal knowledge (use
  /dbt-wiki:ingest), answering questions (use /dbt-wiki:query),
  running dbt itself (use dbt CLI).
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

### Step 0pre: Resolve `.dbt-wiki/` write location, then `cd` there

`.dbt-wiki/` co-locates with `.git/` (git repo root) so it's stable
regardless of where the user invoked `/dbt-wiki:init` from. After this
step, all subsequent `.dbt-wiki/...` paths in this SKILL resolve
correctly via cwd. Matches the location of the CLAUDE.md drop-in
written in Step 2 (also at git repo root).

```bash
# WIKI_DIR = git repo root (preferred); fallback to current $PWD if not in a git repo.
WIKI_DIR=$(git rev-parse --show-toplevel 2>/dev/null) || WIKI_DIR="$PWD"
cd "$WIKI_DIR" || { echo "Cannot cd to $WIKI_DIR"; exit 1; }
echo "✓ .dbt-wiki/ location: $WIKI_DIR/.dbt-wiki/"
```

If user is NOT in a git repo and ran from an unrelated cwd, `.dbt-wiki/`
will land at `$PWD`. That's the same constraint as v1.1.0 — only git
mode benefits from auto-relocation. Most dbt projects are git-tracked
so this covers the typical case.

### Step 0a: Resolve dbt project root (5-tier detection)

Try in priority order; first match wins.

```bash
DBT_DIR=""
DBT_DIR_SOURCE=""  # for diagnostic output

# Tier 1: explicit arg to /dbt-wiki:init <path>
# (If user invoked the skill with an arg that resolves to a directory
# containing dbt_project.yml, use it.)
if [ -n "$SKILL_ARG" ] && [ -f "$SKILL_ARG/dbt_project.yml" ]; then
  DBT_DIR="$SKILL_ARG"
  DBT_DIR_SOURCE="explicit arg"
fi

# Tier 2: $DBT_PROJECT_DIR env var (dbt-mcp / dbt CLI convention)
if [ -z "$DBT_DIR" ] && [ -n "$DBT_PROJECT_DIR" ] && [ -f "$DBT_PROJECT_DIR/dbt_project.yml" ]; then
  DBT_DIR="$DBT_PROJECT_DIR"
  DBT_DIR_SOURCE="\$DBT_PROJECT_DIR env var"
fi

# Tier 3: walk upward from cwd up to 5 ancestors
# (handles "user is in dbt/models/staging/, project root is 3 levels up")
if [ -z "$DBT_DIR" ]; then
  candidate="$PWD"
  for _ in 1 2 3 4 5 6; do
    if [ -f "$candidate/dbt_project.yml" ]; then
      DBT_DIR="$candidate"
      DBT_DIR_SOURCE="ancestor walk from cwd"
      break
    fi
    parent=$(dirname "$candidate")
    [ "$parent" = "$candidate" ] && break  # hit filesystem root
    candidate="$parent"
  done
fi

# Tier 4: walk downward from cwd up to 3 levels deep
# (handles "user is in repo root, dbt is at ./dbt/ or ./data/dbt-prod/")
# Excludes heavy directories: node_modules, .git, target, .venv, __pycache__,
# dbt_packages (dbt's own deps), .repo-wiki, .dbt-wiki
if [ -z "$DBT_DIR" ]; then
  match=$(find . -maxdepth 3 -name dbt_project.yml -type f \
    -not -path '*/node_modules/*' \
    -not -path '*/.git/*' \
    -not -path '*/target/*' \
    -not -path '*/.venv/*' \
    -not -path '*/__pycache__/*' \
    -not -path '*/dbt_packages/*' \
    -not -path '*/.repo-wiki/*' \
    -not -path '*/.dbt-wiki/*' \
    2>/dev/null | head -1)
  if [ -n "$match" ]; then
    DBT_DIR=$(dirname "$match")
    DBT_DIR_SOURCE="downward scan from cwd (max-depth 3)"
  fi
fi

# Tier 5: legacy whitelist (kept for back-compat with v1.0/v1.1)
if [ -z "$DBT_DIR" ]; then
  for candidate in "dbt" "."; do
    if [ -f "$candidate/dbt_project.yml" ]; then
      DBT_DIR="$candidate"
      DBT_DIR_SOURCE="legacy whitelist (./ or dbt/)"
      break
    fi
  done
fi

if [ -z "$DBT_DIR" ]; then
  cat <<EOF
Cannot find dbt_project.yml. Looked in:
  1. Skill argument (none provided)
  2. \$DBT_PROJECT_DIR env var (\${DBT_PROJECT_DIR:-not set})
  3. cwd ancestors (up to 5 levels): $PWD
  4. cwd descendants (max-depth 3, excluding node_modules / .git / target / etc.)
  5. Legacy whitelist: ./ and ./dbt/

How to fix:
  - Pass the path: /dbt-wiki:init /path/to/your/dbt-project
  - Or set: export DBT_PROJECT_DIR=/path/to/your/dbt-project
  - Or cd into the dbt project root and re-run
EOF
  exit 1
fi

# Normalize to absolute path and report what we found
DBT_DIR=$(cd "$DBT_DIR" && pwd)
echo "✓ dbt project root: $DBT_DIR  (detected via: $DBT_DIR_SOURCE)"
```

### Step 0b: Verify required dbt artifacts + Python runner

```bash
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

# Detect Python execution mode (uv preferred — auto-installs sqlglot via PEP 723)
PY_RUNNER=""
if command -v uv >/dev/null 2>&1; then
  PY_RUNNER="uv run"
  echo "Using uv ($(uv --version)) — sqlglot will be installed automatically via PEP 723"
elif python3 -c "import sqlglot" 2>/dev/null; then
  PY_RUNNER="python3"
  echo "Using python3 with pre-installed sqlglot ($(python3 -c 'import sqlglot; print(sqlglot.__version__)'))"
else
  cat <<EOF
Neither uv nor a Python env with sqlglot was found.

Recommended: install uv (https://github.com/astral-sh/uv) — it auto-handles
the sqlglot dependency without polluting your dbt env:
  brew install uv          # macOS
  curl -LsSf https://astral.sh/uv/install.sh | sh    # Linux/macOS

Or, install sqlglot directly into your current Python env:
  pip install 'sqlglot>=25.0'

Then re-run /dbt-wiki:init.
EOF
  exit 1
fi
```

The detected `$PY_RUNNER` (`uv run` or `python3`) is used in Step 4
to invoke the column-lineage and comment scripts. Either path produces
identical output; uv is preferred because it auto-installs deps in an
ephemeral env (zero pollution of the user's dbt env).

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

dbt-wiki ships a tested Python script that uses sqlglot's `lineage` API
to extract per-column source references from compiled dbt SQL. Copy it
from the plugin's assets to the project's `.dbt-wiki/_internal/`:

```bash
mkdir -p .dbt-wiki/_internal
cp <SKILL_DIR>/assets/extract_column_lineage.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/extract_column_lineage_test.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/extract_sql_comments.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/extract_sql_comments_test.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/extract_recursive_column_lineage.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/extract_recursive_column_lineage_test.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/format_lineage_diagram.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/format_lineage_diagram_test.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/synthesis_template.md .dbt-wiki/_internal/
```

(Resolve `<SKILL_DIR>` as the directory containing this SKILL.md.)

The script CLI (use `$PY_RUNNER` from Step 0 — `uv run` or `python3`):

```bash
# Single file (used during refresh):
$PY_RUNNER .dbt-wiki/_internal/extract_column_lineage.py <compiled_sql_path> [dialect]

# Batch (used during init — much faster than per-file invocation):
$PY_RUNNER .dbt-wiki/_internal/extract_column_lineage.py --batch <compiled_dir> [dialect]
```

The script declares its sqlglot dependency via PEP 723 inline metadata,
so `uv run` auto-installs it in an ephemeral env (no pollution of user's
dbt env). With plain `python3`, sqlglot must be pre-installed via pip.

**Critical**: parse `target/compiled/*.sql`, NOT `raw_code` (jinja-laden by
definition; sqlglot can't parse `{{ ref(...) }}`).

### Step 4a: Determine dialect from dbt_project.yml + profiles.yml

Read `dbt_project.yml`'s `profile:` field, then look up that profile in
`~/.dbt/profiles.yml` (or `$DBT_DIR/profiles.yml` if local) to find `type:`.
Map dbt adapter to sqlglot dialect:

| dbt adapter | sqlglot dialect |
|---|---|
| redshift | redshift |
| postgres | postgres |
| snowflake | snowflake |
| bigquery | bigquery |
| databricks / spark | databricks |
| duckdb | duckdb |
| clickhouse | clickhouse |
| trino / presto | presto |
| (unknown / not found) | postgres (closest neutral default) |

Export as `DIALECT=...` for use in batch invocation below.

### Step 4b: Run batch extraction

```bash
PROJECT_NAME=$(grep -E '^name:' "$DBT_DIR/dbt_project.yml" | head -1 | awk '{print $2}' | tr -d "'\"")
$PY_RUNNER .dbt-wiki/_internal/extract_column_lineage.py \
    --batch "$DBT_DIR/target/compiled/$PROJECT_NAME/" \
    "$DIALECT" > /tmp/dbt-wiki-col-lineage.jsonl
```

Output is JSONL — one record per `.sql` file under compiled/, e.g.:

```json
{"path": "models/marts/fct_orders.sql",
 "result": {"customer_id": ["o.customer_id", "c.id"], "order_id": ["o.order_id"], ...}}
```

If `result` contains `_error`, that model's column lineage failed —
record the failure (Step 4d), still create the model page in Step 5
with empty `sources:` per column.

### Step 4c: (Optional but recommended on first run) Verify the script

The script ships with a 7-case smoke test. Run once before processing:

```bash
$PY_RUNNER .dbt-wiki/_internal/extract_column_lineage_test.py
```

Expects "7/7 passed". If failures appear, sqlglot version mismatch is
likely — request a newer version: `uv tool upgrade sqlglot` (uv users) or
`pip install --upgrade 'sqlglot>=25.0'` (plain python3 users).

### Step 4d: Extract SQL + jinja comments from raw model files

Comments often carry WHY context that schema.yml descriptions and
manifest.json miss. dbt-wiki ships `extract_sql_comments.py` (regex,
no sqlglot dep — works on jinja-laden raw_code). It's already copied
to `.dbt-wiki/_internal/` in Step 4 alongside the lineage script:

```bash
cp <SKILL_DIR>/assets/extract_sql_comments.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/extract_sql_comments_test.py .dbt-wiki/_internal/
```

Batch-extract all model file comments (uses `dbt/models/` raw paths,
NOT `target/compiled/` — we want jinja `{# ... #}` comments which
`dbt compile` strips):

```bash
$PY_RUNNER .dbt-wiki/_internal/extract_sql_comments.py \
    --batch "$DBT_DIR/models/" > /tmp/dbt-wiki-comments.jsonl
```

(extract_sql_comments.py has zero third-party deps — runs identically
under `uv run` or plain `python3`. We use `$PY_RUNNER` for consistency.)

JSONL output, one line per `.sql`:

```json
{"path": "marts/fct_orders.sql",
 "comments": [
   {"line": 1, "kind": "line", "text": "joins Shopify webhook with customer table"},
   {"line": 14, "kind": "jinja", "text": "WARNING: incremental hash must include event_at"},
   {"line": 28, "kind": "block", "text": "see ADR-2024-03 for materialization decision"}
 ]}
```

Comments attach to the model page in Step 5 as `## Inline Comments`
body section (rendered as code block with `[line N] <text>` per entry).

### Step 4e: Reconcile sqlglot output with manifest columns

For each model, merge schema.yml-declared columns with sqlglot-extracted
sources. Iterate the JSONL output from Step 4b, keyed by `path`:

```python
# Load batch output once
sqlglot_by_path = {}
for line in open('/tmp/dbt-wiki-col-lineage.jsonl'):
    rec = json.loads(line)
    sqlglot_by_path[rec['path']] = rec['result']

# Per model: merge
manifest_columns = {c['name']: c for c in model['columns'].values()}  # schema.yml
# original_file_path is e.g. "models/marts/fct_orders.sql"; strip leading "models/"
# so it matches the path key under target/compiled/<project>/models/...
sqlglot_columns = sqlglot_by_path.get(model['original_file_path'], {})

merged = {}
for col_name in set(manifest_columns) | set(sqlglot_columns):
    if col_name in ('_error',):
        continue
    merged[col_name] = {
        'name': col_name,
        'declared_in_schema_yml': col_name in manifest_columns,
        'description': manifest_columns.get(col_name, {}).get('description', ''),
        'type': manifest_columns.get(col_name, {}).get('data_type', None),
        'tests': [t['name'] for t in tests_by_model.get(model['unique_id'], []) if t.get('column') == col_name],
        'sources': sqlglot_columns.get(col_name, []),  # may be empty if sqlglot missed
    }

# Determine extraction status for the model
if '_error' in sqlglot_columns:
    extraction_status = 'failed'  # log the error
elif not sqlglot_columns:
    extraction_status = 'schema_yml_only'  # no compiled SQL or batch missed it
else:
    extraction_status = 'sqlglot'
```

Set frontmatter `columns_extracted_via: <extraction_status>`. The model
page is always created — failures just mean empty `sources:` per column.

### Step 4f: Recursive column-lineage extraction (cross-model DAG walk)

The per-SQL lineage from Step 4b only shows **one hop** within a single
model's SQL (e.g. `fct_orders.customer_id ← stg_orders.customer_id`).
For full chain answers ("where does fct_orders.customer_id come from
all the way back to source?"), we need to walk the manifest's depends_on
DAG and resolve each per-SQL source to its upstream manifest node.

dbt-wiki ships `extract_recursive_column_lineage.py` for this. It's
pure stdlib (no sqlglot needed — consumes the JSONL from Step 4b plus
the manifest). Init copies it alongside the other scripts in Step 4:

```bash
cp <SKILL_DIR>/assets/extract_recursive_column_lineage.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/extract_recursive_column_lineage_test.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/format_lineage_diagram.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/format_lineage_diagram_test.py .dbt-wiki/_internal/
cp <SKILL_DIR>/assets/synthesis_template.md .dbt-wiki/_internal/
```

Run it after Step 4b's per-SQL lineage finishes:

```bash
$PY_RUNNER .dbt-wiki/_internal/extract_recursive_column_lineage.py \
    --manifest "$DBT_DIR/target/manifest.json" \
    --lineage /tmp/dbt-wiki-col-lineage.jsonl \
    > /tmp/dbt-wiki-recursive-lineage.jsonl
```

Output is JSONL — one record per `(model_uid, column)`:

```json
{"model_uid": "model.proj.fct_orders",
 "column": "customer_id",
 "ancestors": {
   "model.proj.stg_orders::customer_id": {
     "source.proj.raw_data.orders_raw::customer_id": {}
   },
   "model.proj.stg_customers::id": {
     "source.proj.raw_data.customers_raw::id": {}
   }
 },
 "descendants": {
   "model.proj.dim_orders_summary::customer_id": {
     "model.proj.mart_finance::customer_id": {}
   }
 }}
```

Tree node keys:
- `<unique_id>::<column>` — resolved manifest node + column
- `_unresolved::<table>::<col>` — sqlglot reported a table we couldn't
  map back to manifest (CTE name, SQL alias, dynamic macro output)
- `_cycle` / `_max_depth` — protection markers

In Step 5, attach the recursive lineage to each model page's body as
the `## Column Lineage Chains` section per SCHEMA.md (renders the
ancestor + descendant tree as nested bullet lists for human readability).

### Step 4g: Verify recursive script (optional, recommended on first run)

```bash
$PY_RUNNER .dbt-wiki/_internal/extract_recursive_column_lineage_test.py
```

Expects "6/6 passed". The test uses synthetic manifest + lineage
(no sqlglot, no real dbt project), so it runs offline.

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
