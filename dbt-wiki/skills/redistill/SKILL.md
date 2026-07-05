---
name: redistill
description: |
  Re-distill the stale knowledge pages rescan flagged — LLM rewrites entities/metrics/concepts whose derived_from evidence changed, grouped by domain, skipping mature (human-certified) pages. Use for 'redistill', 're-distill stale knowledge', 'knowledge pages are stale', '重蒸餾知識頁'. This is the LLM half; cheap evidence-only update→rescan; evidence+knowledge in one shot→sync; setup→init.
---

# dbt-wiki — Redistill Workflow

Redistill is the **LLM half** of the update path. `rescan` cheaply rebuilds the
evidence layer and flags knowledge pages `stale: true` when their `derived_from`
evidence changed — but never re-distills (that keeps the daily path LLM-free and
deterministic). Redistill consumes those flags: it re-runs init's Phase B
distillation on the stale pages so their semantic prose catches up with the
evidence.

It costs LLM calls and is non-deterministic — so it is **user-triggered**, never
automatic. Run it when you've reviewed the stale flags and want the knowledge
layer realigned. To do rescan + a gated redistill in one command, use
`/dbt-wiki:sync`.

**Scope guarantee**: redistill only **overwrites pages it re-distills**. It skips
`mature` (human-certified) pages by default and never touches evidence pages,
User Notes, or non-stale knowledge.

## Step 0: Pre-condition check

```bash
# WIKI_DIR = git repo root (where .dbt-wiki/ lives); fallback to $PWD.
WIKI_DIR=$(git rev-parse --show-toplevel 2>/dev/null) || WIKI_DIR="$PWD"
cd "$WIKI_DIR" || { echo "Cannot cd to $WIKI_DIR"; exit 1; }

test -d .dbt-wiki || { echo "Knowledge base not initialized. Run /dbt-wiki:init first."; exit 1; }
test -f .dbt-wiki/log.md || { echo ".dbt-wiki/log.md missing. Re-run /dbt-wiki:init."; exit 1; }

# Self-heal the rebuildable _internal/ cache from the plugin's init assets
# (same contract as rescan Step 0). `<INIT_ASSETS>` = this skill's sibling
# init assets dir: `<SKILL_DIR>/../init/assets`.
if [ ! -f .dbt-wiki/_internal/build_index_knowledge.py ]; then
  mkdir -p .dbt-wiki/_internal
  for f in reconcile lint_identifier_fidelity build_index_knowledge detect_source_language; do
    cp "<INIT_ASSETS>/$f.py" .dbt-wiki/_internal/
  done
  echo "Restored .dbt-wiki/_internal/ from the plugin (rebuildable cache)."
fi

# Python runner (uv preferred — same as init/rescan)
PY_RUNNER=""
if command -v uv >/dev/null 2>&1; then PY_RUNNER="uv run";
elif python3 -c "import yaml" 2>/dev/null; then PY_RUNNER="python3";
else echo "Need uv (recommended) or pip-installed pyyaml."; exit 1; fi
```

Parse args: `--force-mature` (also re-distill mature pages), `--dry-run` (list
scope, no LLM, no writes), `--yes` (skip the confirm prompt).

## Step 1: Collect the work-list (deterministic, no LLM)

```bash
$PY_RUNNER <SKILL_DIR>/assets/collect_redistill_worklist.py .dbt-wiki > /tmp/redistill_worklist.json
```

The script (see its header for the full contract) returns:

- `groups` — `{domain: [{slug, path, folder, derived_from}]}` — stale,
  non-mature, non-archived pages **with provenance**, grouped by the domain
  owning the majority of their `derived_from` evidence (from
  `_internal/ownership.json`).
- `fallback: true` — **no `ownership.json`** (small / sequential init had no
  domain fan-out). All selected pages land in one `(all)` group; an
  `(unmapped)` group holds pages whose evidence maps to no known domain.
- `skipped_mature` — stale pages held back because `status: mature`.
- `skipped_no_provenance` — stale pages with no `derived_from` (cannot scope).
- `total_stale`, `total_selected`.

With `--force-mature`, merge `skipped_mature` entries into their domain groups
(compute each one's domain the same way; `(all)` under fallback).

## Step 2: Empty / dry-run gates

- If `total_selected == 0` **and** not `--force-mature`: print "No stale
  developing knowledge pages to re-distill" (list any `skipped_mature` /
  `skipped_no_provenance` for awareness) and **exit 0**. Nothing to spend on.
- If `--dry-run`: print the scope table below and **exit 0** — no LLM, no writes.

Scope table (always print before distilling):

```
Redistill scope (LLM):
  Domains:  <D>   Pages: <total_selected>
  <domain>: <slug>, <slug>, ...
  ...
  Skipped (mature, needs --force-mature): <list or none>
  Skipped (no derived_from, cannot scope): <list or none>
  ownership.json: present | ABSENT → fallback single-group distill
```

Unless `--yes`, ask: **"Re-distill these <N> pages across <D> domain(s)? This
calls the LLM. (yes/no)"**. Abort on no.

## Step 3: Re-distill, one domain group at a time

For each domain group, re-distill **only the listed pages** by following init's
Phase B specs — do **not** reimplement distillation here (single source of
truth lives in init):

- Entities → `../init/references/distill-entities.md`
- Metrics  → `../init/references/distill-metrics.md`
- Concepts → `../init/references/distill-concepts.md`

Per group:

1. **Resolve source language** once (so rewrites match the rest of the vault):
   `$PY_RUNNER .dbt-wiki/_internal/detect_source_language.py` (or read
   `source_language` from `index.md` / `ownership.json`).
2. **Gather the evidence context** for the group: read each listed page's
   `derived_from` evidence pages under `.dbt-wiki/_evidence/`, plus the existing
   knowledge page (for its relationships / aliases / User-authored intent).
3. **Re-distill each listed page** per the matching spec above, writing the page
   in place. Preserve: `relationships`, `aliases`, any `## User Notes` or other
   user-authored sections, and the page `title`/`slug`. Refresh the semantic
   prose (Description / Fields / Rule / Definition / Calculation / Caveats) from
   the **current** evidence.
   - Honour the cross-entity exclusion rule (distill-entities §5.1): a page's
     `derived_from` stays scoped to its own domain's evidence.
   - **Large groups** (a domain with many pages, or >1 context window) MAY fan
     out one subagent per domain exactly as init Phase B does — same
     deliverable contract (files on disk, not a reply); concrete per-host
     dispatch call shape: `../init/references/claude-code-tools.md` /
     `../init/references/codex-tools.md`. Sequential is the
     default for the typical handful-of-pages redistill.

## Step 4: Clear stale flags + stamp provenance (only on rewritten pages)

For each page actually re-distilled, update its frontmatter:

- Remove `stale`, `stale_at`, `stale_reason` (and strip the rescan STALE banner
  from the body top, if present).
- Set `updated: <today>` and `last_changed_by: "redistill-<today>"` (or the
  commit SHA / PR if available).
- Set `manifest_sha:` to the current manifest sha recorded in `log.md`.

Never clear stale on a page you did not rewrite (e.g. skipped mature without
`--force-mature`) — it must stay flagged.

## Step 5: Reconcile + fidelity + index (deterministic post-pass)

Run in order (all ship in `_internal/`):

```bash
$PY_RUNNER .dbt-wiki/_internal/reconcile.py .dbt-wiki            # 0 dangling relationship targets
$PY_RUNNER .dbt-wiki/_internal/lint_identifier_fidelity.py .dbt-wiki  # no phantom-column citations
$PY_RUNNER .dbt-wiki/_internal/build_index_knowledge.py .dbt-wiki     # regenerate index knowledge sections
```

- `reconcile.py` must report **0 dangling** — a redistilled page may have
  changed a relationship target's title. If it surfaces dangling links, fix the
  link (do not delete the anchor) before finishing.
- `lint_identifier_fidelity.py` must exit 0 — no page may cite a column the
  manifest no longer has. Fix the cited identifier if it fails.

## Step 6: Append a log entry

```
## [<date>] redistill | <total_selected> pages, <D> domains
- pages: <domain>:<slug>, ...
- skipped_mature: <list or none>   (re-run with --force-mature to include)
- fallback (no ownership.json): yes | no
- reconcile: 0 dangling | <fixed>   lint_identifier_fidelity: pass
```

## Step 7: Summary

```
✓ dbt-wiki redistill complete.
  Re-distilled: <total_selected> knowledge pages across <D> domain(s)
    <domain>: <slug>, ...
  Stale flags cleared on re-distilled pages; index knowledge sections regenerated.
  Skipped (still stale): <mature count> mature pages (use --force-mature),
    <no-provenance count> without derived_from.
  Next: /dbt-wiki:query "<question>"  ·  /dbt-wiki:review to certify pages mature
```

## Rules

NEVER:
- Touch evidence pages, `## User Notes`, or non-stale knowledge pages.
- Re-distill a `mature` page unless `--force-mature` was passed.
- Clear a stale flag on a page you did not rewrite.
- Reimplement distillation — always follow init's `references/distill-*.md`.
- Run `dbt parse` / `dbt compile`, or connect to a warehouse / dbt Cloud.
- Hard-delete anything.

ALWAYS:
- Verify `.dbt-wiki/` exists before any work (Step 0).
- Print the scope table and confirm before spending on the LLM (unless `--yes`).
- Run reconcile + lint_identifier_fidelity + build_index_knowledge after distilling.
- Write knowledge pages in the project's `source_language`; keep slugs /
  frontmatter keys / identifiers ASCII.
