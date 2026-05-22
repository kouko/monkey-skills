---
name: refresh
description: |
  Incremental update for dbt-wiki AFTER user runs dbt parse / dbt compile
  / dbt run. Compares current target/manifest.json md5 against the
  last-recorded manifest_sha; processes only added / modified / removed
  models / sources / macros / seeds / snapshots / exposures. Re-runs
  sqlglot column-lineage extraction AND inline-comment extraction on
  changed files only. Removed resources are archived to
  .dbt-wiki/_archive/<date>/, never hard-deleted. Preserves user-owned
  ## User Notes body sections verbatim (managed by /dbt-wiki:ingest).
  Always regenerates derived files: index.md and lineage.md. Asks user
  to confirm diff summary before writing.
  Triggers when user says "I just ran dbt parse / dbt compile / dbt run",
  "model 改了", "新增了 model", "刪了 model", "renamed a model",
  "refresh dbt-wiki", "update dbt knowledge", "after dbt parse",
  "dbt model changed", "manifest changed", "/dbt-wiki:refresh",
  "更新 dbt-wiki", "重新生 dbt 知識庫", "dbt parse 跑完了",
  "dbt 改完之後", "dbt model 更新後", "dbt-wiki 更新".
  Do NOT trigger for: first-time setup (use /dbt-wiki:init), adding
  user context that isn't a code change (use /dbt-wiki:ingest), querying
  the wiki (use /dbt-wiki:query), running dbt itself (use dbt CLI).
---

# dbt-wiki — Refresh Workflow (v1.0)

Refresh is the **daily / per-feature update** path. It assumes init has
already run (so `.dbt-wiki/` + `SCHEMA.md` + `_internal/` exist) and only
processes diffs against the last manifest_sha.

If `.dbt-wiki/` doesn't exist, refresh refuses and points to `/dbt-wiki:init`.

## Step 0: Pre-condition Check

```bash
# WIKI_DIR = git repo root (where .dbt-wiki/ lives); fallback to current $PWD.
# Same logic as init Step 0pre — refresh must look at the SAME location
# init wrote to, regardless of where the user invoked refresh from.
WIKI_DIR=$(git rev-parse --show-toplevel 2>/dev/null) || WIKI_DIR="$PWD"
cd "$WIKI_DIR" || { echo "Cannot cd to $WIKI_DIR"; exit 1; }

test -d .dbt-wiki || { echo "Knowledge base not initialized at $WIKI_DIR/.dbt-wiki/. Run /dbt-wiki:init first."; exit 1; }
test -f .dbt-wiki/log.md || { echo ".dbt-wiki/log.md missing. Re-run /dbt-wiki:init."; exit 1; }
test -f .dbt-wiki/_internal/extract_column_lineage.py || {
  echo "Column lineage script missing. Re-run /dbt-wiki:init to restore."
  exit 1
}

# Resolve dbt project root using the 5-tier detection from init Step 0a:
#   1. /dbt-wiki:refresh <path> arg
#   2. $DBT_PROJECT_DIR env var (dbt-mcp / dbt CLI convention)
#   3. ancestor walk from cwd (up to 5 levels)
#   4. descendant scan from cwd (max-depth 3, excludes node_modules / .git /
#      target / .venv / __pycache__ / dbt_packages / .repo-wiki / .dbt-wiki)
#   5. legacy whitelist (./ or dbt/)
DBT_DIR=""
DBT_DIR_SOURCE=""
if [ -n "$SKILL_ARG" ] && [ -f "$SKILL_ARG/dbt_project.yml" ]; then
  DBT_DIR="$SKILL_ARG"; DBT_DIR_SOURCE="explicit arg"
fi
if [ -z "$DBT_DIR" ] && [ -n "$DBT_PROJECT_DIR" ] && [ -f "$DBT_PROJECT_DIR/dbt_project.yml" ]; then
  DBT_DIR="$DBT_PROJECT_DIR"; DBT_DIR_SOURCE="\$DBT_PROJECT_DIR"
fi
if [ -z "$DBT_DIR" ]; then
  candidate="$PWD"
  for _ in 1 2 3 4 5 6; do
    if [ -f "$candidate/dbt_project.yml" ]; then
      DBT_DIR="$candidate"; DBT_DIR_SOURCE="ancestor walk"; break
    fi
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
  [ -n "$match" ] && { DBT_DIR=$(dirname "$match"); DBT_DIR_SOURCE="downward scan"; }
fi
if [ -z "$DBT_DIR" ]; then
  for candidate in "dbt" "."; do
    [ -f "$candidate/dbt_project.yml" ] && { DBT_DIR="$candidate"; DBT_DIR_SOURCE="legacy whitelist"; break; }
  done
fi
test -n "$DBT_DIR" || {
  echo "Cannot find dbt_project.yml. Pass path as arg, set \$DBT_PROJECT_DIR, or cd to project root."
  exit 1
}
DBT_DIR=$(cd "$DBT_DIR" && pwd)
echo "✓ dbt project root: $DBT_DIR  (via: $DBT_DIR_SOURCE)"

test -f "$DBT_DIR/target/manifest.json" || {
  echo "Missing $DBT_DIR/target/manifest.json — run: cd $DBT_DIR && dbt parse"
  exit 1
}
test -d "$DBT_DIR/target/compiled" || {
  echo "Missing $DBT_DIR/target/compiled — run: cd $DBT_DIR && dbt compile"
  exit 1
}

# Detect Python execution mode (same as init Step 0 — uv preferred)
PY_RUNNER=""
if command -v uv >/dev/null 2>&1; then
  PY_RUNNER="uv run"
elif python3 -c "import sqlglot" 2>/dev/null; then
  PY_RUNNER="python3"
else
  echo "Need either uv (recommended) or pip-installed sqlglot."
  echo "  brew install uv     # or: curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "  OR"
  echo "  pip install 'sqlglot>=25.0'"
  exit 1
fi
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
   $PY_RUNNER .dbt-wiki/_internal/extract_column_lineage.py \
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
unique_id: model.example_dbt_project.deprecated_model
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

## Step 6.5: Mark stale syntheses (do NOT regenerate, just flag)

Syntheses (saved query answers from `/dbt-wiki:query` Step 6.5) capture
point-in-time answers + diagrams. When the manifest changes, those
answers may become inaccurate — but we don't auto-regenerate (LLM
cost + answer wording would drift each refresh, breaking git diff
stability). Instead: mark them stale, let the user decide whether to
re-query.

```python
# Pseudocode for refresh's stale-detection logic:
import yaml, glob
from pathlib import Path

# Build set of model uids that ACTUALLY changed in this refresh
changed_uids = set()
for uid in added | modified | removed:    # from Step 2's diff
    changed_uids.add(uid)

# For each non-archived synthesis, check overlap
for path in glob.glob('.dbt-wiki/syntheses/*.md'):
    content = Path(path).read_text()
    # Parse frontmatter (YAML between first two `---`)
    fm_text = content.split('---')[1] if content.startswith('---') else ''
    fm = yaml.safe_load(fm_text) or {}

    if fm.get('stale'):
        continue   # already marked; skip

    affected = set(fm.get('affected_models', []))
    if not affected:
        # No precise tracking — fall back to manifest_sha drift
        if fm.get('manifest_sha') != new_sha:
            mark_stale(path, fm, reason="manifest_sha drift (no affected_models tracking)")
        continue

    # Precise check: do any of THIS synthesis's affected models appear in this refresh's diff?
    overlap = affected & changed_uids
    if overlap:
        mark_stale(path, fm, reason=f"affected_models changed: {sorted(overlap)}")


def mark_stale(path, fm, reason):
    """Update frontmatter (stale: true, stale_at: today, stale_reason: ...)
    AND prepend a banner to the body so user sees it immediately when opening
    the .md file in their IDE."""
    fm['stale'] = True
    fm['stale_at'] = today
    fm['stale_reason'] = reason
    new_fm = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True)

    body = content.split('---', 2)[2]   # everything after frontmatter
    banner = f"""
> ⚠️ **STALE WARNING** ({today}): {reason}.
> The answer below was correct at the time of saving (manifest_sha:
> `{fm.get('manifest_sha', '?')}`), but underlying models have changed
> since. Re-run to get fresh answer + diagram:
>
> ```
> /dbt-wiki:query "{fm.get('question', '?')}"
> ```

"""
    Path(path).write_text(f'---\n{new_fm}---\n{banner}{body}')
```

Stale detection is **non-destructive**: original answer + diagrams stay
intact (user can still read them, just with full awareness they're
stale). Re-running query overwrites the synthesis with fresh content
and clears the stale flag.

If `affected_models` is missing from a v1.2-or-earlier synthesis,
fall back to `manifest_sha` drift (less precise but always works).

Report stale count in summary (Step 8): "Synthesis stale: N marked".

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
- Syntheses marked stale: <N> (out of <total> non-archived)
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
