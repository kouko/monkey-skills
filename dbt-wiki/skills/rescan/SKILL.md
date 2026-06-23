---
name: rescan
description: |
  Cheap mechanical half: re-scan .dbt-wiki/ evidence after dbt parse/compile — diff manifest md5, reprocess only changed resources, re-run sqlglot lineage, preserve User Notes, flag stale knowledge pages (0 LLM). Use for 'I just ran dbt parse', 'model 改了', 'rescan dbt-wiki', 'update evidence'. Re-distill stale knowledge→redistill; evidence+knowledge in one shot→sync; setup→init; add notes→ingest.
---

# dbt-wiki — Rescan Workflow (v2.0)

Rescan is the **daily / per-feature update** path. It assumes init has
already run (so `.dbt-wiki/` + `SCHEMA.md` + `_internal/` exist) and only
processes diffs against the last manifest_sha.

If `.dbt-wiki/` doesn't exist, rescan refuses and points to `/dbt-wiki:init`.

## Step 0: Pre-condition Check

```bash
# WIKI_DIR = git repo root (where .dbt-wiki/ lives); fallback to current $PWD.
# Same logic as init Step 0pre — rescan must look at the SAME location
# init wrote to, regardless of where the user invoked rescan from.
WIKI_DIR=$(git rev-parse --show-toplevel 2>/dev/null) || WIKI_DIR="$PWD"
cd "$WIKI_DIR" || { echo "Cannot cd to $WIKI_DIR"; exit 1; }

test -d .dbt-wiki || { echo "Knowledge base not initialized at $WIKI_DIR/.dbt-wiki/. Run /dbt-wiki:init first."; exit 1; }
test -f .dbt-wiki/log.md || { echo ".dbt-wiki/log.md missing. Re-run /dbt-wiki:init."; exit 1; }
# `_internal/` is a rebuildable cache (init may gitignore it), so a fresh clone
# can legitimately lack it. Self-heal from the plugin's init assets instead of
# erroring. `<INIT_ASSETS>` = the init skill's assets dir, a sibling of this
# skill: resolve it as `<SKILL_DIR>/../init/assets` (this SKILL.md lives in
# `.../skills/rescan/`; init's assets are in `.../skills/init/assets/`).
if [ ! -f .dbt-wiki/_internal/extract_column_lineage.py ]; then
  mkdir -p .dbt-wiki/_internal
  # copy every production script + template the cache needs (NOT the *_test.py)
  for f in extract_column_lineage extract_sql_comments extract_recursive_column_lineage \
           format_lineage_diagram detect_source_language lint_schema_divergence \
           lint_identifier_fidelity build_evidence_pages build_index_knowledge reconcile; do
    cp "<INIT_ASSETS>/$f.py" .dbt-wiki/_internal/
  done
  cp "<INIT_ASSETS>/synthesis_template.md" .dbt-wiki/_internal/
  echo "Restored .dbt-wiki/_internal/ from the plugin (rebuildable cache)."
fi
test -f .dbt-wiki/_internal/extract_column_lineage.py || {
  echo "Could not restore _internal/ from <INIT_ASSETS>. Re-run /dbt-wiki:init."
  exit 1
}

# Resolve dbt project root using the 5-tier detection from init Step 0a:
#   1. /dbt-wiki:rescan <path> arg
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
  echo "No manifest changes since last init/rescan (sha: $NEW_SHA)."
  echo "If you only changed SQL inside a model and re-ran dbt compile, manifest"
  echo "may be unchanged. To force rescan, delete the manifest_sha line from log.md."
  exit 0
fi
```

## Step 2: Diff models

Read both old (cached) and new manifest. Build three lists:

```python
import json

new_manifest = json.load(open(f"{DBT_DIR}/target/manifest.json"))
new_models = {nid: n for nid, n in new_manifest['nodes'].items() if n.get('resource_type') == 'model'}

# Read existing model pages from .dbt-wiki/_evidence/models/*.md
import glob, os
existing_pages = {}
for path in glob.glob('.dbt-wiki/_evidence/models/*.md'):
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
Rescan diff summary (vs last manifest sha: <last>):
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
3. Write `.dbt-wiki/_evidence/models/<model_name>.md` per SCHEMA's `model` page type
4. (Same for sources → `.dbt-wiki/_evidence/sources/`, macros → `.dbt-wiki/_evidence/macros/`, etc.)

## Step 4: Process modifications

For each model in `modified`:

1. Read existing page from `.dbt-wiki/_evidence/models/<model_name>.md`; preserve
   **custom body sections** (anything outside the standard sections defined in SCHEMA.md):
   - Standard: `## Description`, `## Materialization Notes`, `## SQL Preview`,
     `## Column Sources (from sqlglot)`, `## Tests`, `## Cross-references`
   - Custom: any other `##` heading the user added → preserve verbatim at end
2. Re-run column lineage extraction (Step 3a above)
3. Build new frontmatter from current manifest + sqlglot output
4. Write merged file back to `.dbt-wiki/_evidence/models/<model_name>.md`:
   new frontmatter + regenerated standard sections + preserved custom

## Step 5: Process removals (archive, don't delete)

For each model in `removed`:

```bash
mkdir -p .dbt-wiki/_archive/<today>/
mv .dbt-wiki/_evidence/models/<orphan>.md .dbt-wiki/_archive/<today>/
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

These two files are derived; regenerate from scratch every rescan:

- `index.md`: **knowledge-first** — the evidence sections come from the
  evidence re-scan; the knowledge sections (`## Entities` / `## Metrics` /
  `## Concepts`) are **deterministically regenerated** from the current
  knowledge pages' frontmatter by the shipped generator:

  ```bash
  $PY_RUNNER .dbt-wiki/_internal/build_index_knowledge.py .dbt-wiki
  ```

  Run it after the evidence-section rebuild so both halves reflect the
  current state. Section order: Entities → Metrics → Concepts → Evidence: Models
  (grouped by tier / materialization / tag / group) → Evidence: Sources → Evidence: Macros (used)
  → Evidence: Seeds / Snapshots / Tests / Exposures.
- **Identifier-fidelity gate** — if any knowledge page was re-distilled or
  edited this rescan (or a column was renamed/dropped upstream), re-run the
  phantom-column gate so no page is left citing a column the manifest no longer
  has: `$PY_RUNNER .dbt-wiki/_internal/lint_identifier_fidelity.py .dbt-wiki`
  (see init Step 6.8). Exit non-zero ⇒ fix the cited identifier before publishing.
- `lineage.md`: from new manifest, build DAG (depends_on / feeds_into),
  produce ASCII tree + adjacency list

## Step 6.4: Pre-stale lint — derived_from domain consistency

**Gate**: if `_internal/ownership.json` does not exist (small or
sequential projects that skipped the fan-out init path), **skip this
step entirely** — `ownership.json` is only written by the domain
fan-out during `init`, so its absence is normal, not an error.

**Purpose**: verify that every `derived_from` unique_id listed in a
knowledge page belongs to the same domain slice that owns the page,
according to `ownership.json`. A unique_id from a *different* domain
is almost always a relationship-only model that was added to
`derived_from` in violation of the cross-entity exclusion rule
(`init/references/distill-entities.md` §5.1 "Cross-entity exclusion
rule"). If left undetected, it will produce a false stale-cascade:
the knowledge page will be flagged stale every time an unrelated
domain changes.

This step is **WARNING-only** — do NOT auto-remove the offending
unique_ids. The uid could be a legitimate cross-domain entity in a
denormalised or shared-dimension pattern; auto-removal would silently
break the freshness anchor. Surface for human review instead.

```python
# Pseudocode — pre-stale derived_from domain-consistency lint
import itertools, json, yaml
from pathlib import Path

wiki = Path(".dbt-wiki")
ownership_path = wiki / "_internal" / "ownership.json"

if not ownership_path.exists():
    # Small/sequential project — no domain fan-out, skip.
    pass
else:
    ownership = json.loads(ownership_path.read_text())
    # ownership.json shape: { "domains": { "<domain>": ["<uid>", ...], ... } }
    # Each uid is a FULL evidence unique_id (e.g. "model.<package>.<name>"),
    # matching the shape stored in derived_from — so uid_to_domain lookup aligns.
    # Build reverse map: uid -> domain (key is full unique_id).
    uid_to_domain = {}
    for domain, uids in ownership["domains"].items():
        for uid in uids:
            uid_to_domain[uid] = domain

    warnings = []
    for page_path in itertools.chain(wiki.glob("entities/*.md"), wiki.glob("metrics/*.md"), wiki.glob("concepts/*.md")):
        raw = page_path.read_text()
        parts = raw.split("---", 2)
        if len(parts) < 3:
            continue
        fm = yaml.safe_load(parts[1]) or {}
        derived = fm.get("derived_from", []) or []
        if not derived:
            continue   # no provenance — nothing to check

        # Map each derived_from uid to its domain via the reverse map.
        # Uids not found in any domain slice are ignored (unmapped).
        mapped_domains = {uid_to_domain[uid] for uid in derived if uid in uid_to_domain}

        if len(mapped_domains) <= 1:
            continue   # all uids resolve to one domain (or none mapped) — clean

        # More than one distinct domain in derived_from → cross-domain contamination.
        # Identify the majority domain and flag the foreign uid(s).
        from collections import Counter
        domain_counts = Counter(uid_to_domain[uid] for uid in derived if uid in uid_to_domain)
        majority_domain = domain_counts.most_common(1)[0][0]
        foreign_uids = [uid for uid in derived
                        if uid in uid_to_domain and uid_to_domain[uid] != majority_domain]
        foreign_details = ", ".join(
            f"{uid} (domain: {uid_to_domain[uid]})" for uid in foreign_uids
        )
        warnings.append(
            f"WARNING {page_path.name}: derived_from spans multiple domains "
            f"(majority: {majority_domain}); foreign uid(s): {foreign_details} "
            f"— likely relationship-only model(s) wrongly added; "
            f"will cause false stale-cascade."
        )

    if warnings:
        log_path = wiki / "log.md"
        existing = log_path.read_text() if log_path.exists() else ""
        log_path.write_text(existing + "\n### Step 6.4 derived_from domain-consistency lint\n\n" +
                            "\n".join(warnings) + "\n")
        # Also surface in the chat so the user sees it immediately.
        print("\n".join(warnings))
```

**No auto-fix.** After emitting warnings, continue to Step 6.5 — the
domain-consistency issue does not block stale detection; it only means
some stale flags may be over-eager.

## Step 6.5: Mark stale syntheses and knowledge pages (do NOT regenerate, just flag)

**Scope boundary**: this step only **flags** stale pages — `rescan`
itself never re-distills (that would re-introduce LLM cost + non-determinism
into the cheap daily path). Re-distillation lives in its sibling skills:
run `/dbt-wiki:redistill` to re-distill the stale knowledge pages, or
`/dbt-wiki:sync` to do this rescan + a gated re-distill in one shot.
This keeps rescan cheap: no LLM calls, purely deterministic.

Syntheses (saved query answers from `/dbt-wiki:query`) and knowledge
pages (`entities/`, `metrics/`, `concepts/`) both capture point-in-time
content. When the manifest changes, that content may become inaccurate —
but we don't auto-regenerate. Instead: mark them stale, let the user
decide whether to re-distill / re-query.

```python
# Pseudocode for rescan's stale-detection logic:
import yaml, glob
from datetime import date
from pathlib import Path

today = date.today().isoformat()          # stale_at stamp


def mark_stale(path, fm, content, reason):
    """Update frontmatter (stale: true, stale_at: today, stale_reason: ...)
    AND prepend a banner to the body so user sees it immediately when opening
    the .md file in their IDE. Reused by both syntheses and knowledge pages.
    Defined before its call sites below (Part A + Part B)."""
    fm['stale'] = True
    fm['stale_at'] = today
    fm['stale_reason'] = reason
    new_fm = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True)

    body = content.split('---', 2)[2]   # everything after frontmatter

    # Banner wording adapts to page type
    is_knowledge = fm.get('type', '').startswith('knowledge-')
    if is_knowledge:
        rerun_hint = (
            f'Re-distill this page after reviewing the changed evidence:\n'
            f'>\n'
            f'> ```\n'
            f'> /dbt-wiki:redistill  # re-distill stale knowledge pages (or /dbt-wiki:sync)\n'
            f'> ```'
        )
    else:
        rerun_hint = (
            f'Re-run to get fresh answer + diagram:\n'
            f'>\n'
            f'> ```\n'
            f'> /dbt-wiki:query "{fm.get("question", "?")}"\n'
            f'> ```'
        )

    banner = f"""
> **STALE WARNING** ({today}): {reason}.
> Original content below was correct at the time it was last generated
> (manifest_sha: `{fm.get('manifest_sha', '?')}`), but underlying
> evidence models have changed since. {rerun_hint}

"""
    Path(path).write_text(f'---\n{new_fm}---\n{banner}{body}')


# Build set of model uids that ACTUALLY changed in this rescan
changed_uids = set()
for uid in added | modified | removed:    # from Step 2's diff
    changed_uids.add(uid)

# --- Part A: Syntheses ---
# For each non-archived synthesis, check overlap via affected_models
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
            mark_stale(path, fm, content, reason="manifest_sha drift (no affected_models tracking)")
        continue

    # Precise check: do any of THIS synthesis's affected models appear in this rescan's diff?
    overlap = affected & changed_uids
    if overlap:
        mark_stale(path, fm, content, reason=f"affected_models changed: {sorted(overlap)}")

# --- Part B: Knowledge pages (entities/, metrics/, concepts/) ---
# Uses the SAME mark_stale mechanism. No LLM calls — purely frontmatter + file writes.
knowledge_stale_count = 0
for pattern in ['.dbt-wiki/entities/*.md', '.dbt-wiki/metrics/*.md', '.dbt-wiki/concepts/*.md']:
    for path in glob.glob(pattern):
        content = Path(path).read_text()
        fm_text = content.split('---')[1] if content.startswith('---') else ''
        fm = yaml.safe_load(fm_text) or {}

        if fm.get('stale') or fm.get('status') == 'archived':
            continue   # already marked or archived; skip

        # derived_from: list of evidence model unique_ids this page was distilled from.
        # Intersect with changed_uids to determine if any source evidence changed.
        derived = set(fm.get('derived_from', []))
        if not derived:
            continue   # no provenance recorded — cannot detect stale; skip

        overlap = derived & changed_uids
        if overlap:
            mark_stale(path, fm, content,
                       reason=f"derived_from evidence changed: {sorted(overlap)}")
            knowledge_stale_count += 1

# Store knowledge_stale_count for Step 7 log and Step 8 summary.
# (mark_stale is defined at the top of this block, before Part A.)
```

Stale detection is **non-destructive**: original content (answer /
diagrams / distilled knowledge) stays intact — user can still read it
with full awareness it may be outdated. For syntheses, re-running the
query overwrites with fresh content and clears the stale flag. For
knowledge pages, re-distillation (user-triggered) clears the flag.

If a knowledge page has no `derived_from` list, it cannot be
precisely stale-detected and is skipped (no false positives).

If `affected_models` is missing from a v1.x synthesis, fall back to
`manifest_sha` drift (less precise but always works).

Report stale counts in summary (Step 8): "Syntheses stale: N marked.
Knowledge pages stale: M marked (entities: X, metrics: Y, concepts: Z)."

## Step 7: Append rescan entry to log.md

```
## [<date>] rescan | <added>+<modified>-<removed> changed
- manifest_sha: <new_sha> (was: <old_sha>)
- Models added: <list>
- Models modified: <list>
- Models removed (archived to _archive/<date>/): <list>
- Sources added/modified/removed: <a>/<m>/<r>
- Macros added/modified/removed: <a>/<m>/<r>
- sqlglot_failures: <count> (only counted for added/modified)
- column_lineage_extracted: <count>/<total updated> (<percent>%)
- Syntheses marked stale: <N> (out of <total> non-archived)
- Knowledge pages marked stale: <M> (entities: <X>, metrics: <Y>, concepts: <Z>)
  (stale = flagged only; re-distill is user-triggered)
```

## Step 8: Summary Report

```
✓ dbt-wiki rescan complete.

  Diff vs last manifest:
    - Models: +<a> ~<m> -<r>
    - Sources: +<a> ~<m> -<r>
    - Macros: +<a> ~<m> -<r>

  Updated:
    - .dbt-wiki/_evidence/models/*.md, _evidence/sources/*.md,
      _evidence/macros/*.md (changed pages only)
    - .dbt-wiki/lineage.md (regenerated)
    - .dbt-wiki/index.md (regenerated, knowledge-first)
    - .dbt-wiki/log.md (rescan entry appended)

  Archived (in .dbt-wiki/_archive/<today>/): <removed_count> pages
    (recoverable — never hard-deleted)

  Stale flags set (no content modified — original content preserved):
    - Syntheses:      <N> marked stale (of <total> non-archived)
    - Knowledge pages: <M> marked stale
        entities: <X>  metrics: <Y>  concepts: <Z>
    NOTE: Knowledge pages are flagged only. Re-distillation is
    user-triggered (not automatic). This keeps rescan free of LLM calls.
    To re-distill the stale knowledge pages, run:
      /dbt-wiki:redistill   # re-distill stale (developing) pages, skips mature
      /dbt-wiki:sync        # or: rescan + gated re-distill in one shot

  Next steps:
    - Re-distill stale knowledge: /dbt-wiki:redistill (or /dbt-wiki:sync next time)
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
- Update `manifest_sha` in log.md after successful rescan
- Re-generate index.md and lineage.md from scratch (they're derived; never partial-update)
- Re-run sqlglot column lineage for added + modified models (skip for unchanged)
- Use the same dialect as init (read from log.md or dbt_project.yml profile)
