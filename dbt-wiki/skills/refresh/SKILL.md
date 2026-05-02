---
name: refresh
description: |
  Incremental update for dbt-wiki after dbt parse / dbt compile / dbt run.
  Compares current target/manifest.json against last-recorded
  manifest_sha; updates only changed model / source / macro pages;
  archives orphaned models. Always re-generates index.md and lineage.md.
  Triggers on "refresh dbt-wiki", "update dbt-wiki", "dbt model changed",
  "/dbt-wiki:refresh", "更新 dbt-wiki", "重新生 dbt 知識庫".
  Do NOT trigger for: first-time setup (use /dbt-wiki:init), querying
  (use /dbt-wiki:query).
---

# dbt-wiki — Refresh Workflow (v1.0)

Refresh is the **daily / per-feature update** path. It assumes init has
already run (so `.dbt-wiki/` + `SCHEMA.md` + `_internal/` exist) and only
processes diffs against the last manifest_sha.

If `.dbt-wiki/` doesn't exist, refresh refuses and points to `/dbt-wiki:init`.

## Step 0: Pre-condition Check

```bash
test -d .dbt-wiki || { echo "Knowledge base not initialized. Run /dbt-wiki:init first."; exit 1; }
test -f .dbt-wiki/log.md || { echo ".dbt-wiki/log.md missing. Re-run /dbt-wiki:init."; exit 1; }
test -f .dbt-wiki/_internal/extract_column_lineage.py || {
  echo "Column lineage script missing. Re-run /dbt-wiki:init to restore."
  exit 1
}

# Resolve dbt project root (same as init Step 0)
DBT_DIR=""
for candidate in "dbt" "."; do
  if [ -f "$candidate/dbt_project.yml" ]; then
    DBT_DIR="$candidate"
    break
  fi
done
test -n "$DBT_DIR" || { echo "Cannot find dbt_project.yml"; exit 1; }

test -f "$DBT_DIR/target/manifest.json" || {
  echo "Missing $DBT_DIR/target/manifest.json — run: cd $DBT_DIR && dbt parse"
  exit 1
}
test -d "$DBT_DIR/target/compiled" || {
  echo "Missing $DBT_DIR/target/compiled — run: cd $DBT_DIR && dbt compile"
  exit 1
}

python3 -c "import sqlglot" || { echo "sqlglot not installed: pip install sqlglot"; exit 1; }
```

## Step 1: Detect drift

```bash
NEW_SHA=$(md5 -q "$DBT_DIR/target/manifest.json" 2>/dev/null || md5sum "$DBT_DIR/target/manifest.json" | cut -d' ' -f1)
LAST_SHA=$(grep -m 1 'manifest_sha:' .dbt-wiki/log.md | sed 's/.*manifest_sha: //' | tr -d ' ')

if [ "$NEW_SHA" = "$LAST_SHA" ]; then
  echo "No manifest changes since last init/refresh (sha: $NEW_SHA)."
  echo "If you only changed SQL inside a model and re-ran dbt compile, manifest"
  echo "may be unchanged. To force refresh, delete the manifest_sha line from log.md."
  exit 0
fi
```

## Step 2: Diff models

Read both old (cached) and new manifest. Build three lists:

```python
import json

new_manifest = json.load(open(f"{DBT_DIR}/target/manifest.json"))
new_models = {nid: n for nid, n in new_manifest['nodes'].items() if n.get('resource_type') == 'model'}

# Read existing model pages from .dbt-wiki/models/*.md
import glob, os
existing_pages = {}
for path in glob.glob('.dbt-wiki/models/*.md'):
    with open(path) as f:
        content = f.read()
        # Parse frontmatter to get unique_id
        fm = parse_frontmatter(content)  # standard YAML frontmatter parser
        if fm.get('removed'):
            continue  # skip already-archived
        existing_pages[fm['unique_id']] = path

added = set(new_models) - set(existing_pages)
removed = set(existing_pages) - set(new_models)
common = set(new_models) & set(existing_pages)

# For common, check if model node hash changed (compare a small subset)
modified = []
for uid in common:
    new = new_models[uid]
    existing_fm = parse_frontmatter(open(existing_pages[uid]).read())
    # Compare: materialization, tags, depends_on, columns count, raw_code hash
    if (new['config']['materialized'] != existing_fm.get('materialization')
        or set(new['depends_on']['nodes']) != set(existing_fm.get('depends_on', {}).get('refs', []) +
                                                   [f"source.{s}" for s in existing_fm.get('depends_on', {}).get('sources', [])])
        or len(new['columns']) != len(existing_fm.get('columns', []))
        or md5(new['raw_code']) != existing_fm.get('raw_code_md5')):
        modified.append(uid)
```

(Same logic for sources, macros, seeds, snapshots — compare frontmatter
to detect material change.)

Print summary before writing:

```
Refresh diff summary (vs last manifest sha: <last>):
  Added:    <N> models, <M> sources, <K> macros
  Modified: <N> models, <M> sources, <K> macros
  Removed:  <N> models, <M> sources, <K> macros (will be archived)

Continue? (yes/no)
```

If `yes`, proceed. Otherwise abort.

## Step 3: Process additions

For each model in `added`:

1. Run column lineage extraction (same as init Step 4):
   ```bash
   python3 .dbt-wiki/_internal/extract_column_lineage.py \
       "$DBT_DIR/target/compiled/$PROJECT/${original_file_path}" redshift > /tmp/cl.json
   ```
2. Reconcile sqlglot output with schema.yml columns
3. Write `.dbt-wiki/models/<model_name>.md` per SCHEMA's `model` page type
4. (Same for sources, macros, etc.)

## Step 4: Process modifications

For each model in `modified`:

1. Read existing page; preserve **custom body sections** (anything outside
   the standard sections defined in SCHEMA.md):
   - Standard: `## Description`, `## Materialization Notes`, `## SQL Preview`,
     `## Column Sources (from sqlglot)`, `## Tests`, `## Cross-references`
   - Custom: any other `##` heading the user added → preserve verbatim at end
2. Re-run column lineage extraction (Step 3a above)
3. Build new frontmatter from current manifest + sqlglot output
4. Write merged file: new frontmatter + regenerated standard sections + preserved custom

## Step 5: Process removals (archive, don't delete)

For each model in `removed`:

```bash
mkdir -p .dbt-wiki/_archive/<today>/
mv .dbt-wiki/models/<orphan>.md .dbt-wiki/_archive/<today>/
```

Add a comment line in the moved file's frontmatter:

```yaml
---
unique_id: model.iCHEF_dbt_pipline.deprecated_model
removed: true
removed_at: 2026-05-02
removed_reason: "no longer in manifest after dbt parse"
# ... (rest of original frontmatter preserved)
---
```

Never hard-delete. User can restore from `_archive/` if needed.

## Step 6: Always re-generate index.md and lineage.md

These two files are derived; regenerate from scratch every refresh:

- `index.md`: re-scan `.dbt-wiki/{models,sources,macros,...}/*.md` (skip `_archive/`),
  group by tier / materialization / tag / group, write
- `lineage.md`: from new manifest, build DAG (depends_on / feeds_into),
  produce ASCII tree + adjacency list

## Step 7: Append refresh entry to log.md

```
## [<date>] refresh | <added>+<modified>-<removed> changed
- manifest_sha: <new_sha> (was: <old_sha>)
- Models added: <list>
- Models modified: <list>
- Models removed (archived to _archive/<date>/): <list>
- Sources added/modified/removed: <a>/<m>/<r>
- Macros added/modified/removed: <a>/<m>/<r>
- sqlglot_failures: <count> (only counted for added/modified)
- column_lineage_extracted: <count>/<total updated> (<percent>%)
```

## Step 8: Summary Report

```
✓ dbt-wiki refresh complete.

  Diff vs last manifest:
    - Models: +<a> ~<m> -<r>
    - Sources: +<a> ~<m> -<r>
    - Macros: +<a> ~<m> -<r>

  Updated:
    - .dbt-wiki/models/*.md, sources/*.md, macros/*.md (changed pages only)
    - .dbt-wiki/lineage.md (regenerated)
    - .dbt-wiki/index.md (regenerated)
    - .dbt-wiki/log.md (refresh entry appended)

  Archived (in .dbt-wiki/_archive/<today>/): <removed_count> pages
    (recoverable — never hard-deleted)

  Next steps:
    - Query: /dbt-wiki:query "<question>"
    - For major refactor (e.g., 50+ model change), consider /dbt-wiki:init for clean rebuild
```

## Rules

NEVER:
- Modify any file under `dbt/` or `target/` or anywhere outside `.dbt-wiki/` and `CLAUDE.md`
- Hard-delete pages (always archive to `.dbt-wiki/_archive/<date>/`)
- Run `dbt parse` / `dbt compile` on user's behalf
- Connect to dbt Cloud or warehouse
- Skip the manifest_sha drift check (Step 1) — it's the basis of incrementality
- Overwrite custom body sections in model pages on modification (preserve verbatim)
- Touch any `.repo-wiki/` content (separate plugin)

ALWAYS:
- Verify `.dbt-wiki/` exists before any work
- Print diff summary and ask user to confirm before writing changes (unless `--yes` arg)
- Update `manifest_sha` in log.md after successful refresh
- Re-generate index.md and lineage.md from scratch (they're derived; never partial-update)
- Re-run sqlglot column lineage for added + modified models (skip for unchanged)
- Use the same dialect as init (read from log.md or dbt_project.yml profile)
