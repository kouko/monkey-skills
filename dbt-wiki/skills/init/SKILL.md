---
name: init
description: |
  First-time setup: scaffold .dbt-wiki/ from manifest.json + compiled SQL (sqlglot column lineage) + inline comments — pages, index, lineage DAG, CLAUDE.md. Needs dbt parse && compile first. Use for 'init dbt-wiki' or '初始化'. Later updates→refresh.
---

# dbt-wiki — Init Workflow (v2.0)

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

### Step 0c: v1.x layout guard (one-time warning only)

If `.dbt-wiki/` exists AND it contains a top-level `models/` directory
(v1.x layout — evidence was not yet under `_evidence/`) AND any page
inside it contains a `## User Notes` section:

```bash
if [ -d ".dbt-wiki/models" ] && grep -rl "^## User Notes" .dbt-wiki/models/ 2>/dev/null | grep -q .; then
  cat <<'WARN'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WARNING: v1.x dbt-wiki detected with User Notes present.

dbt-wiki v2.0 is a clean-break rebuild — it does NOT migrate, copy,
or preserve any content from the v1.x layout.  The existing
.dbt-wiki/ directory will be rebuilt from scratch under the new
layout (_evidence/, entities/, metrics/, concepts/).

Your ## User Notes sections will be LOST if you continue.

ACTION REQUIRED: back up your User Notes before proceeding.
  Example: cp -r .dbt-wiki/ .dbt-wiki-v1-backup/

Continuing will rebuild from current manifest.json.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WARN
fi
```

This warning fires once and then proceeds — it is **not** a migration.
No content is preserved. The user must back up manually before
re-running if they want to keep their User Notes.

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
# Knowledge layer
mkdir -p .dbt-wiki/entities
mkdir -p .dbt-wiki/metrics
mkdir -p .dbt-wiki/concepts

# Evidence layer (demoted from top-level in v1.x)
mkdir -p .dbt-wiki/_evidence/models
mkdir -p .dbt-wiki/_evidence/sources
mkdir -p .dbt-wiki/_evidence/macros
mkdir -p .dbt-wiki/_evidence/seeds
mkdir -p .dbt-wiki/_evidence/snapshots
mkdir -p .dbt-wiki/_evidence/tests
mkdir -p .dbt-wiki/_evidence/exposures

mkdir -p .dbt-wiki/_archive
mkdir -p .dbt-wiki/syntheses
```

**Mark `_internal/` as a rebuildable cache (do not commit it).** The
`_internal/` scripts are mechanical, copied verbatim from the plugin's
`assets/`, and re-derivable on demand — `init` writes them and `refresh`
self-heals them from the same plugin source (see refresh Step 0). Committing
them just duplicates the installed plugin and drifts on plugin upgrade. Emit a
`.dbt-wiki/.gitignore` (idempotent — skip if it already exists) so they stay out
of git:

```bash
test -f .dbt-wiki/.gitignore || cat > .dbt-wiki/.gitignore <<'GITIGNORE'
# Rebuildable mechanical cache — re-created by /dbt-wiki:init and self-healed
# by /dbt-wiki:refresh from the installed plugin. Not part of the knowledge state.
_internal/
**/__pycache__/
GITIGNORE
```

The committed knowledge state is everything else under `.dbt-wiki/`
(`entities/`, `metrics/`, `concepts/`, `_evidence/`, `index.md`, `log.md`, …);
`_internal/` is tooling, not knowledge.

> **Already committed `_internal/` from an earlier init?** `.gitignore` does not
> untrack files git already tracks. On a re-run, if `_internal/` is tracked,
> stop tracking it (keeps it on disk): `git rm -r --cached .dbt-wiki/_internal`.
> Detect with `git ls-files .dbt-wiki/_internal | head -1` — non-empty ⇒ run it.

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
to extract per-column source references from compiled dbt SQL. Copy the
**production** scripts (not the `*_test.py`) from the plugin's assets to the
project's `.dbt-wiki/_internal/` — `_internal/` is a rebuildable cache, so the
one-shot smoke tests stay in the plugin and run in-place from there (Steps 4c /
4g), never landing in the user's repo:

```bash
mkdir -p .dbt-wiki/_internal
for f in extract_column_lineage extract_sql_comments \
         extract_recursive_column_lineage format_lineage_diagram \
         detect_source_language lint_schema_divergence build_evidence_pages \
         build_index_knowledge reconcile; do
  cp "<SKILL_DIR>/assets/$f.py" .dbt-wiki/_internal/
done
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

**Persist the dialect.** Record the resolved `$DIALECT` in `.dbt-wiki/index.md`
frontmatter as `dialect: <DIALECT>` (alongside `source_language`; see Phase B
step 0 where `source_language` is written — set `dialect` in the same place).
This is the **only** record of the warehouse SQL dialect in `.dbt-wiki/`, and
`dbt-wiki:pack` reads it to tell a repo-less consuming agent which SQL dialect
to generate (pack itself never touches the dbt project, so without this the
dialect is lost). Also add a `dialect:` line to the Step 7 `log.md` init entry.

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

The script ships with a 7-case smoke test. Run once before processing
(from the plugin assets — the `*_test.py` are not copied into `_internal/`):

```bash
$PY_RUNNER <SKILL_DIR>/assets/extract_column_lineage_test.py
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
cp <SKILL_DIR>/assets/format_lineage_diagram.py .dbt-wiki/_internal/
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
$PY_RUNNER <SKILL_DIR>/assets/extract_recursive_column_lineage_test.py
```

Expects "6/6 passed". The test uses synthetic manifest + lineage
(no sqlglot, no real dbt project), so it runs offline.

## Step 5: Write Evidence Pages (Phase A)

All evidence pages write under `.dbt-wiki/_evidence/<type>/` — the
evidence layer is the **unchanged v1.x mechanical pipeline**, relocated.
Do NOT write to top-level `.dbt-wiki/models/` (that was the v1.x layout).

**Do NOT hand-write evidence pages.** Beyond a few dozen models this is
infeasible (real projects have hundreds–thousands of models), and the page
shape is fully derivable from `manifest.json` + the Step 4 JSONL outputs —
so it must be mechanical and reproducible, not authored by hand. dbt-wiki
ships a deterministic, stdlib-only generator — `build_evidence_pages.py`
(copied to `.dbt-wiki/_internal/` in Step 4) — that emits EVERY evidence
page (models / sources / used-macros / seeds / snapshots / singular tests)
plus `index.md` and `lineage.md`, exactly per the SCHEMA.md page contracts.

Invoke it once (use `$PY_RUNNER` from Step 0):

```bash
$PY_RUNNER .dbt-wiki/_internal/build_evidence_pages.py \
    --manifest "$DBT_DIR/target/manifest.json" \
    --wiki-dir .dbt-wiki \
    --dbt-dir "$DBT_DIR" \
    --col-lineage /tmp/dbt-wiki-col-lineage.jsonl \
    --comments /tmp/dbt-wiki-comments.jsonl \
    --recursive-lineage /tmp/dbt-wiki-recursive-lineage.jsonl
    # optional: --project-name NAME (default = manifest metadata.project_name)
    #           --today YYYY-MM-DD  (default = today)
```

It prints a stats JSON (model/source/macro/seed/test counts, column-lineage
success rate, sqlglot failures, DAG depth, leaf count) — capture it for the
Step 7 log entry. What it writes, per the SCHEMA.md evidence page types:

- `.dbt-wiki/_evidence/models/<model_name>.md` (collision → `<package>__<model_name>.md`)
- `.dbt-wiki/_evidence/sources/<source_name>__<table_name>.md` (with `feeds_into`)
- `.dbt-wiki/_evidence/macros/<macro_name>.md` (only macros used by ≥1 model;
  external-package macros use `<package>__<macro_name>.md`)
- `.dbt-wiki/_evidence/{seeds,snapshots,tests}/<name>.md` (tests = singular only;
  generic schema.yml tests are folded inline into their model page)
- `.dbt-wiki/index.md` and `.dbt-wiki/lineage.md` (Step 6 documents their shape;
  the generator follows it. Phase B later regenerates only the `index.md`
  knowledge sections — Entities / Metrics / Concepts.)

Verify the generator first (optional, recommended on first run):
`$PY_RUNNER <SKILL_DIR>/assets/build_evidence_pages_test.py` → expects "6/6 passed".

**Exposures** (if any are declared) are the one node type the generator does
not emit; write `.dbt-wiki/_evidence/exposures/<exposure_name>.md` per SCHEMA's
`exposure` type for each (exposures are rare and low-volume).

### Re-run merge behavior

When `is_rerun = true` and an evidence model page already exists:

1. Read existing frontmatter and body
2. Build new frontmatter from current manifest + sqlglot
3. Detect custom body sections (anything outside the standard sections defined in SCHEMA.md):
   - Standard: `## Description`, `## Materialization Notes`, `## SQL Preview`,
     `## Inline Comments (from raw_code)`, `## Column Sources (from sqlglot)`,
     `## Column Lineage Chains`, `## Tests`, `## Cross-references`
   - Custom (user-owned): `## User Notes` and any other `##` section the user added
4. Write new file: new frontmatter + standard sections regenerated +
   custom sections preserved verbatim at the end
5. If new manifest doesn't contain a model previously documented:
   move `.dbt-wiki/_evidence/models/<orphaned>.md` to
   `.dbt-wiki/_archive/<today>/<orphaned>.md`, don't hard-delete

## Step 6: Generate index.md and lineage.md

> `build_evidence_pages.py` (Step 5) **already wrote** `index.md` and
> `lineage.md` following the shapes specified below — this section is the
> contract the generator implements (and the shape Phase B regenerates the
> `index.md` knowledge sections against after distillation). You normally do
> not hand-write these; the spec below is for understanding / verification.

### index.md

Regenerate as a **knowledge-first** catalog. The knowledge layer leads;
structural grouping is demoted into an evidence sub-section. Sections
in order:

**Knowledge layer (lead):**

Canonical line shape for every entry in `## Entities`, `## Metrics`,
and `## Concepts`:
```
- [<title>｜<title_local>](<folder>/<slug>.md) `<status>` — <summary> 〔aka: <alias1>, <alias2>, …〕
```
Omission rules:
- The `｜<title_local>` segment is **omitted** when `title_local` is absent (or null).
- The `〔aka: …〕` clause is **omitted** when `aliases` is empty.

- `## Entities` — one line per page in `entities/` using the canonical
  line shape above. If no entity pages exist yet (Phase B has not run),
  emit a stub: `(none yet — run Phase B to distill entities from the
  evidence layer)`.
- `## Metrics` — same canonical line shape for `metrics/` pages.
- `## Concepts` — same canonical line shape for `concepts/` pages.

**Evidence layer (demoted — structural grouping):**
- `## Evidence: Models` — grouped by tier path (`models/staging/` →
  Staging, `models/marts/` → Marts, etc.). Links to
  `.dbt-wiki/_evidence/models/<name>.md`.
- `## Evidence: Models by Materialization` (table / view / incremental / ephemeral)
- `## Evidence: Models by Tag`
- `## Evidence: Models by Group`
- `## Evidence: Sources` — links to `_evidence/sources/`.
- `## Evidence: Macros (used)` — links to `_evidence/macros/`.
- `## Evidence: Seeds / Snapshots / Tests / Exposures` — links to
  corresponding `_evidence/` subdirs.

Statistics block at end:
- Total evidence pages by type (models, sources, macros, seeds, etc.)
- Column lineage extraction success rate (count + percent)
- sqlglot parse failures (count, link to log.md)
- Knowledge pages: entity count, metric count, concept count

### lineage.md

For each declared source/seed (root nodes), do depth-first traversal
producing ASCII tree. Mark first-occurrence with `→`, repeats with `↺`.

For each model, add an adjacency list entry: depends_on (refs / sources / macros)
+ feeds_into.

If model count > 500, also produce tier-aggregated view at top.

## Phase B: Knowledge Distillation (runs after Phase A evidence layer is complete)

Phase A (Steps 1–6 above) builds the mechanical evidence layer
deterministically from manifest.json + sqlglot. Phase B runs
**after** the evidence layer is fully written. It is the LLM-driven
knowledge distillation step that produces the knowledge layer
(`entities/`, `metrics/`, `concepts/`).

### Phase B orchestration

0. **Resolve the source language.** Knowledge pages are written in the language
   of the project's model comments (dbt-wiki treats comments as the source of
   truth; translating them loses domain terms) — see each distill spec's §0.
   Run `.dbt-wiki/_internal/detect_source_language.py` (copied from
   `assets/` in Step 4; honours an explicit
   `DBT_WIKI_LANGUAGE` / project setting first, else auto-detects the dominant
   script of the evidence `## Description` + `## Inline Comments`). Record the
   result as `source_language:` in `index.md` frontmatter and pass it into every
   domain agent's brief, so the whole fan-out writes ONE consistent language.
   Slugs, frontmatter keys, identifiers and stored `value_domain` values stay
   ASCII regardless.

1. Confirm Phase A completed — all `_evidence/` subdirs are populated
   and `index.md` has been regenerated with evidence sections.
2. Distill **entities** by following the procedure in
   `references/distill-entities.md`. Each entity page records:
   - `derived_from: [<evidence model unique_ids>]` — the evidence
     pages it was distilled from (used by refresh for stale detection)
   - `last_changed_by: "<commit SHA or PR#>"` — provenance of the
     last distillation pass
3. Distill **metrics** by following the procedure in
   `references/distill-metrics.md`. If the project has MetricFlow
   `semantic_models` / `metrics` in `manifest.json`, ingest them as
   the authoritative input rather than re-deriving from SQL.
   Same `derived_from` + `last_changed_by` provenance fields.
4. Distill **concepts** by following the procedure in
   `references/distill-concepts.md`. Same provenance fields.
5. Regenerate `index.md`'s knowledge sections now that knowledge pages
   exist, so `## Entities` / `## Metrics` / `## Concepts` are populated
   rather than stub placeholders. This is **deterministic** (derived from
   each page's frontmatter — `title` / `title_local` / `status` / `summary`
   / `aliases`), so run the generator rather than hand-transcribing:

   ```bash
   $PY_RUNNER .dbt-wiki/_internal/build_index_knowledge.py .dbt-wiki
   ```

   It replaces the three knowledge sections in the SCHEMA canonical line
   shape and updates the `- Knowledge pages:` stats line, leaving the
   evidence sections untouched. (Optional first-run check:
   `$PY_RUNNER <SKILL_DIR>/assets/build_index_knowledge_test.py` → "8/8 passed".)

### Phase B parallel orchestration (large projects, >~80 models)

This layer is **optional**. Small projects use the sequential Phase B
flow above. When the evidence set is large (typically >~80 models,
or when manual distillation of entities/metrics would exceed a single
context window), Phase B fans out one subagent per **domain** — a
cohesive cluster of models sharing a business purpose (e.g. `billing`,
`sales`, `inventory`).

#### Before fan-out: write `.dbt-wiki/_internal/ownership.json`

Before dispatching domain agents, write `.dbt-wiki/_internal/ownership.json`
with two maps (plus the resolved `source_language` from step 0, so every domain
agent writes the same language):

```json
{
  "source_language": "zh",
  "reserved_entities": {
    "customer": "billing",
    "order":    "sales"
  },
  "domains": {
    "billing":   ["model.example_dbt_project.billing_invoices_v1", "model.example_dbt_project.billing_payments_v1"],
    "sales":     ["model.example_dbt_project.sales_orders_v1", "model.example_dbt_project.sales_order_lines_v1"],
    "inventory": ["model.example_dbt_project.inventory_stock_v1"]
  }
}
```

- **`reserved_entities`** — business objects that two or more domains
  reference but exactly one domain owns. Each entry maps a slug to its
  owning domain. Example: `"customer": "billing"` means the `customer`
  entity page is owned by the `billing` agent; all other agents may
  link to it but must not create it.
- **`domains`** — maps each domain slug to the list of evidence
  `unique_id`s it is responsible for distilling. Values are full dbt
  `unique_id`s (`model.<package>.<name>`) — the same shape as
  `derived_from` entries in wiki pages.

#### has_metricflow gate (P2-1)

Before dispatching any metric agent, evaluate:

```python
has_metricflow = bool(manifest.get("semantic_models"))
```

Pass `has_metricflow` into each metric agent's brief. When
`has_metricflow` is `false`, agents skip the MetricFlow branch in
distill-metrics §2 entirely (the detection logic already lives in
that spec; this is the orchestration-level gate that avoids
unnecessary checks across all domain agents).

#### Per-domain fan-out rules

Each domain agent receives:
- Its own slice of evidence `unique_id`s (from `domains` map above).
- The full `reserved_entities` map and the `domains` map for
  cross-domain awareness.
- The `has_metricflow` flag.

Each domain agent **builds only the pages it owns**. When a domain
agent needs to express a relationship to a reserved entity owned by
another domain, it:
1. Emits the relationship edge in the owning page's typed-link
   `Relationships` section with the correct relative path.
2. Does **not** create the target page — leaves a dangling link.

#### Deliverable contract — files on disk, not a return message

A domain agent's deliverable is the set of page **files it writes to
`.dbt-wiki/{entities,metrics,concepts}/`**. Its final/return message is
only a manifest (the slugs it wrote) used for verification — it is
**never** accepted in lieu of files. State this explicitly in every
agent brief: the single most common fan-out failure mode is an agent
that produces polished page *content in its reply* but never calls the
write tool. Two robust dispatch shapes — pick one and make the brief
unambiguous:

- **Write-direct** (default): the agent writes each page with the file
  tool, then returns a manifest of slugs. Cheaper context, but depends
  on the agent actually writing — so the Step 6.6 gate below is
  mandatory.
- **Return-and-materialize** (robust fallback for harnesses where
  spawned/async agents don't reliably persist files): the agent returns
  each page as structured output `{folder, slug, content}` (force it via
  a schema), and the **orchestrator** writes the files. Persistence then
  cannot silently fail. Switch to this when Step 6.6 shows write-direct
  produced zero pages.

Dangling links to cross-domain reserved entities are resolved by the
reconcile pass (Step 6.7 — handled separately; do not add it here).

### Step 6.6: Persistence verification gate (after fan-out, before reconcile)

Fan-out can silently produce **zero files** (an agent that analysed but
never wrote). NEVER proceed to reconcile on faith — verify on disk:

1. Count pages actually written:
   `find .dbt-wiki/entities .dbt-wiki/metrics .dbt-wiki/concepts -name '*.md' | wc -l`.
2. Cross-check per domain: each dispatched domain in `ownership.json`
   should have produced ≥1 page for the objects it owns. If a domain's
   return manifest claims files that are **not on disk**, that domain
   failed to persist.
3. **Retry** each failed domain once with an explicit directive: *"You
   wrote 0 files; your deliverable is files on disk, not your reply —
   write them now with the file tool."* If write-direct keeps failing
   after one retry, switch that domain (or all) to the
   **Return-and-materialize** shape above and have the orchestrator write
   the files.
4. After at most K=2 rounds, if pages are still missing, emit a WARNING
   naming the empty domains and continue — do not let a silent zero pass
   as success.

Proceed to Step 6.7 only once the on-disk page count is non-zero and
covers the dispatched domains.

### Step 6.7: Reconcile pass (after Phase B fan-out)

Run **once** after all domain agents have returned their pages. This
step resolves dangling links and enforces cross-domain provenance
integrity. It is **deterministic** — run the shipped generator rather
than hand-implementing the three sub-passes below:

```bash
$PY_RUNNER .dbt-wiki/_internal/reconcile.py .dbt-wiki
```

It (1) scans every `relationships[].target`, (2) for each missing target
warns on a reserved-entity slug (owner agent should have produced it) or
writes a `status: seed` stub for a genuine dangling reference, and (3)
lints `derived_from` cross-domain contamination using
`_internal/ownership.json`. If `ownership.json` is absent (a small project
that skipped domain fan-out) it degrades gracefully — every dangling ref
becomes a stub and the contamination lint is a no-op. Review its printed
WARNINGs and contamination flags and resolve per the rules below. (Optional
first-run check: `$PY_RUNNER <SKILL_DIR>/assets/reconcile_test.py` → "11/11 passed".)

The three sub-passes below document **what the script does** (and how to
resolve what it surfaces) — read them to act on the output.

#### 6.7.1 Collect all relationship targets

Scan every knowledge page under `entities/`, `metrics/`, and
`concepts/`. Build a set of every `relationships[].target` slug
referenced across all pages.

#### 6.7.2 Resolve missing targets

For each target slug that has **no file on disk**:

1. **Look up `reserved_entities` in `ownership.json`.**

   - **If the slug IS a reserved entity** — check whether the owning
     domain produced a page for it.

     - Owner produced no page → emit a **WARNING** (do NOT silently
       create a stub for a reserved slug):

       ```
       WARNING: reserved entity "<slug>" (owner: "<domain>") has no
       page — owner agent may have failed or skipped it. Resolve
       manually before publishing.
       ```

     - Owner produced a page but the path is wrong → log a path-mismatch
       warning and correct the `relationships[].target` reference.

   - **If the slug is NOT in `reserved_entities`** (genuine dangling
     reference, e.g. a concept referenced in passing) → create a
     seed stub (`status: seed`) so the markdown link resolves:

     ```yaml
     ---
     title: "<slug>"
     status: seed
     derived_from: []
     last_changed_by: "auto-stub (reconcile pass)"
     ---
     <!-- Auto-generated stub. Replace with a real distillation pass. -->
     ```

     Place the stub in the appropriate subdirectory (`entities/`,
     `metrics/`, or `concepts/`) based on the page type that referenced
     it. If ambiguous, place under `concepts/`.

#### 6.7.3 Lint `derived_from` cross-domain contamination

**How owning domain is determined**: there is no per-page `domain:`
frontmatter key. A page's owning domain is inferred from its
`derived_from` uids via the `ownership.json` `domains` reverse-map —
build `uid_to_domain` by inverting `ownership.json["domains"]`
(`{ domain: [uid, ...] }` → `{ uid: domain }`), then map each
`derived_from` uid through it to get the set of domains it touches.

A page is **clean** when all its `derived_from` uids resolve to the
same domain (or none map at all — unmapped uids are ignored).
A page is **contaminated** when its `derived_from` uids resolve to
**more than one** distinct domain.

For each contaminated knowledge page, flag it:

```
LINT ERROR: <page_path> — derived_from spans domains
{<domain_a>, <domain_b>}: uid "<unique_id>" belongs to
domain "<foreign_domain>", not "<majority_domain>".
Cross-domain derived_from entries cause spurious stale-cascades
on refresh (see distill-entities §5.1 cross-entity exclusion rule).
```

Where `<majority_domain>` is the domain whose uids appear most
frequently in the page's `derived_from` list (i.e. the most likely
intended owning domain), and each `<unique_id>` / `<foreign_domain>`
pair names a uid that resolves to a different domain.

Emit all violations before stopping — do not halt on the first one.

A page with cross-domain `derived_from` entries **must not** be
published until the contamination is resolved: either the foreign
uid is moved to the correct owning domain's page or removed.

### Phase B spec files

The three distillation procedures are defined in:
- `references/distill-entities.md` — entity identification,
  field dictionary, typed-link Relationships
- `references/distill-metrics.md` — metric definition, algorithm
  plain-language, MetricFlow-ingest-if-present branch
- `references/distill-concepts.md` — cross-cutting business rules,
  concept vs entity boundary criteria

These files are the authoritative specs for Phase B. Read them before
distilling. Do NOT invent distillation procedure that contradicts them.

### Phase B provenance contract

Every knowledge page produced by Phase B MUST carry:

```yaml
derived_from:
  - model.example_dbt_project.stg_customers   # evidence unique_ids
  - model.example_dbt_project.dim_customers
last_changed_by: "PR #123"                     # or commit SHA
title_local: "顧客"                             # project-language title; null if none (always written, never omitted)
aliases:                                        # project-language synonyms/codes; [] if none (always written, never omitted)
  - customer
  - client
```

`title_local` and `aliases` are emitted automatically by the distill
agent (the alias-capture rule in each `references/distill-*.md` spec
populates them). **During distillation the agent always writes both
keys**: `aliases: []` when no aliases were found, `title_local: null`
when no project-language title exists — this lets the index generator
distinguish "distilled but no aliases" from "not yet distilled."
Pre-existing v2.0 pages that omit these keys are still valid; SCHEMA.md
states that missing optional keys parse fine (legacy omission tolerance).

`derived_from` is the freshness anchor: `/dbt-wiki:refresh` uses it
to detect which knowledge pages are stale when evidence models change
(same overlap logic as `syntheses` `affected_models`).

## Step 7: Append init entry to log.md

```
## [<date>] init | <N> models, <M> sources, <K> macros (used)
- manifest_sha: <sha>
- compiled_files_parsed: <count>
- sqlglot_failures: <count>
  - <model_name>: <truncated reason>
  - ... (max 10 listed; full list in /tmp/dbt-wiki-init-failures.log if generated)
- column_lineage_extracted: <success_count>/<total_models> (<percent>%)
- Evidence pages created (fresh): <models>/<sources>/<macros>/<seeds>/<snapshots>/<tests>/<exposures>
- Evidence pages updated (re-run): <count>
- Evidence pages archived (orphaned): <count>
- Knowledge pages created (Phase B): entities/<N>, metrics/<N>, concepts/<N>
- Run type: <fresh | re-run>
```

## Step 8: Summary Report

Print to user:

```
✓ dbt-wiki initialized at .dbt-wiki/

  Manifest: <DBT_DIR>/target/manifest.json (sha: <sha>)
  Compiled SQL: <count> files parsed via sqlglot (<dialect>)

  Phase A — Evidence layer:
    - <N> model pages        → .dbt-wiki/_evidence/models/ (column lineage: <success>/<total>)
    - <N> source pages       → .dbt-wiki/_evidence/sources/
    - <N> macro pages        → .dbt-wiki/_evidence/macros/ (used by ≥1 model)
    - <N> seed / <N> snapshot / <N> singular test / <N> exposure
    - lineage.md (DAG depth: <N>; root sources: <N>; leaves: <N>)
    - index.md (knowledge-first; evidence layer grouped by tier / tag / group)

  Phase B — Knowledge layer:
    - <N> entity pages       → .dbt-wiki/entities/
    - <N> metric pages       → .dbt-wiki/metrics/
    - <N> concept pages      → .dbt-wiki/concepts/

  Files updated:
    - .dbt-wiki/{SCHEMA,index,log,lineage}.md
    - .dbt-wiki/_evidence/{models,sources,macros,seeds,snapshots,tests,exposures}/*.md
    - .dbt-wiki/{entities,metrics,concepts}/*.md
    - .dbt-wiki/_internal/{extract_column_lineage,build_evidence_pages,...}.py
    - CLAUDE.md drop-in (<created/appended/replaced>)

  Next steps:
    1. Skim .dbt-wiki/index.md — entities, metrics, and concepts are at the top
    2. Try a semantic query: /dbt-wiki:query "customer 是什麼？"
    3. Try a structural query: /dbt-wiki:query "fct_orders 依賴什麼？"
    4. After next dbt parse + dbt compile, run /dbt-wiki:refresh
    5. (If installed) repo-wiki and dbt-wiki coexist — use repo-wiki for WHY
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
