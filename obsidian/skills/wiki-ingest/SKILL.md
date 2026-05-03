---
name: wiki-ingest
description: Ingest Obsidian vault notes into wiki/ with SHA-256 delta tracking; owns page format spec. Use after new notes land in references/research/lab/. Do NOT use for repo-wiki:ingest or dbt-wiki:ingest. Wiki知識蒸留。Wiki 知識萃取・增量同步。
---

# Wiki Ingest — Source Notes → Wiki Pages

Reads source notes from configured folders (via `.env`), distills knowledge, writes structured wiki pages following [page-format.md](references/page-format.md), and tracks changes via [delta-tracking.md](references/delta-tracking.md).

## Pre-flight (eager)

Read these BEFORE STEP 1:

1. **`.env`** at vault root — must contain `OBSIDIAN_VAULT_PATH`, `OBSIDIAN_EXCLUDE_DIRS`. If missing, instruct user to run `/wiki-setup` and exit.
2. **`wiki/.manifest.json`** — for delta detection. If missing, treat as empty `{}` (likely first ingest after wiki-setup).

## References (lazy — read only when needed)

These are spec references; load them at the moment you need them, not at pre-flight. This keeps small / scoped ingests fast:

| Reference | When to load |
|---|---|
| [references/delta-tracking.md](references/delta-tracking.md) | Before STEP 2 (scan and hash) — defines the manifest update contract |
| [references/category-routing.md](references/category-routing.md) | Before STEP 3b (decide category) — decision tree for entities vs concepts |
| [references/page-format.md](references/page-format.md) | Before STEP 3c (generate page) — authoritative output spec; reread before EVERY new page generation |

**Why lazy**: a delta-only run with 0 NEW / 0 MODIFIED sources never needs page-format.md or category-routing.md. Eager loading wastes context on the common no-op path.

## Source scope

`wiki-ingest` scans the **entire vault** for `.md` files, with two blacklist layers:

- **System always-excluded**: `wiki/`, `.obsidian/`, `.trash/`, `.git/`, `node_modules/`, `_raw/`
- **User-configured**: `OBSIDIAN_EXCLUDE_DIRS` from `.env` (default `daily,inbox`)

**Match rule**: top-level only — only the first path segment is compared, case-sensitive. Nested directories with the same name (`projects/old/daily/`) are NOT excluded.

For the full contract, edge cases, and rationale, see [references/source-scope.md](references/source-scope.md).

## STEP 1 — Determine ingest scope

Use `AskUserQuestion`:

```
Question: "What should I ingest?"
Options:
1. "Whole vault, delta only" — scan entire vault minus excluded dirs, skip unchanged via manifest
2. "Specific path" — user types a vault-relative file or folder
3. "Research notes only" — limit to research/ (typical after wiki-auto-research)
```

Respect `OBSIDIAN_MAX_PAGES_PER_INGEST` (default 15). If scope exceeds it, ask user to confirm or batch.

For option 1, invoke the bundled scan script (POSIX-portable, reads `OBSIDIAN_EXCLUDE_DIRS` from env, emits one absolute path per line):

```sh
set -a; . .env; set +a              # export .env vars
bash <skill-root>/scripts/scan-vault.sh "$VAULT_ROOT" > /tmp/wiki-ingest-candidates.txt
```

See [scripts/scan-vault.sh](scripts/scan-vault.sh) for implementation. Don't hand-roll a `find` command — the script handles top-level pruning, system exclusions, and edge cases (loose root .md files, normalization). For options 2 and 3, scan the user-specified path directly via `Read` / `Bash find`.

## STEP 2 — Scan and hash

For each candidate source file:

1. Compute SHA-256 (`shasum -a 256`)
2. Compare to `.manifest.json`
3. Bucket into NEW / MODIFIED / UNCHANGED

Show user a summary table before processing:

```
Found 47 source files:
  NEW:        12  ← will be ingested
  MODIFIED:    3  ← will re-ingest, preserve User Notes
  UNCHANGED:  32  ← skipped via manifest

Cap: 15 pages per run (configurable in .env)
Proceed?
```

## STEP 3 — Per-source ingest loop

For each NEW or MODIFIED source, in this order:

### 3a. Read source content

Use `Read`. Capture frontmatter + body. Note any existing `wikilinks` for connection inference.

**Auto-research gate** (per the wiki-auto-research output contract):

- If `frontmatter.generated_by == "wiki-auto-research"`:
  - If `frontmatter.status == "reviewed-accept"` → ingest normally
  - If `frontmatter.status` is `"pending-review"` or `"reviewed-reject"` or missing → **skip**, log to `wiki/log.md` as `skipped-pending-review`, continue to next source

This decouples the user-review gate from auto-research. Manually-written research notes (no `generated_by` field) are always ingested without status check.

### 3b. Decide category (per [category-routing.md](references/category-routing.md))

A single source may contribute to multiple wiki pages (e.g., a paper covering MAB → updates `entities/Thompson-Sampling`, `entities/UCB`, `concepts/exploration-exploitation`). Identify all targets.

### 3c. For each target wiki page

**Filename uniqueness check** (before creating any new page):

Wikilinks use bare filename (no path), so every page in `wiki/` MUST have a globally unique filename across all 6 subfolders.

Algorithm:
1. Compute candidate slug from topic name (kebab-case, ASCII-safe).
2. Scan `wiki/{entities,concepts,synthesis,skills,journal,references}/<slug>.md` — does any exist?
3. If a same-named file exists in a **different category**:
   - If the existing file is the same conceptual subject → treat as **update**, not new page (re-categorize is a separate user decision)
   - If different subject → disambiguate the new page's slug with a qualifier: `<slug>-<qualifier>.md` (e.g., `qlib.md` already exists as Microsoft's library → new conceptual entry becomes `qlib-language.md`).
4. Surface the disambiguation to the user before writing — do not silently rename.

**If target page does not exist** (after uniqueness check) → create new page following [page-format.md](references/page-format.md). All 8 frontmatter fields. 3 required body sections. Filename in `<wiki-root>/<category>/<slug>.md`.

**If target page exists** → update:
- `## Summary` — re-synthesize incorporating new source
- `## Key Facts` — append new facts; mark provenance correctly (`^[inferred]`, `^[ambiguous]`)
- `## Connections` — add new wikilinks if discovered
- `## Sources` — add link to the per-source reference page (see 3d)
- `frontmatter.sources_count` — increment
- `frontmatter.updated` — today's date
- `frontmatter.summary` — refresh if material changes (≤200 chars)
- `## User Notes` — **preserve verbatim** if present

### 3d. Create/update reference page

Always write `wiki/references/<slug>.md` (one page per source) with:

```yaml
---
title: "Source Title"
type: wiki-reference
source_path: <vault-relative-path-to-original>
date: YYYY-MM-DD                    # source date (frontmatter or filename)
ingested: YYYY-MM-DD                # today
contributes_to:
  - "[[Thompson-Sampling]]"
  - "[[exploration-exploitation]]"
tags:
  - source
summary: "≤200 char single-line description of what this source contributes"
---

## Source Excerpt / TL;DR
2–4 sentence neutral description of what the source argues / measures / claims.

## Key Contributions
- Bullet list — what specifically this source added to the wiki
- Cite which target pages were updated and how
```

Reference pages are append-only over time — re-ingest of the same source updates `ingested`, may extend `contributes_to` and `Key Contributions`.

### 3e. Update `wiki/index.md`

Append the new page link under the appropriate category section. Skip if already present.

### 3f. Update `wiki/.manifest.json`

Per [delta-tracking.md](references/delta-tracking.md): write entry with sha256, ISO timestamp, and union of `wiki_pages`.

### 3g. Append to `wiki/log.md`

```markdown
| YYYY-MM-DD | ingest | <source-path> | <comma-separated wiki page links, marked (new) or (updated)> |
```

## STEP 4 — Update `wiki/hot.md`

Refresh the "Recently touched" section with this run's affected pages. Cap entire section ≤300 chars; truncate oldest first.

## STEP 5 — Report and recommend

```
Ingest complete:
  Sources processed:  N
  Wiki pages created: M
  Wiki pages updated: K
  Reference pages:    R

Recommended next steps:
  /wiki-cross-linker  — strengthen wikilinks across the new pages
  /wiki-lint          — health check (run after large batches)
  /wiki-auto-research — fill Open Questions surfaced this run (if any)
```

## Quality bar (self-check before finalizing each page)

- [ ] All 8 frontmatter fields present and validly typed
- [ ] `summary` ≤200 chars, self-contained, no markdown
- [ ] 3 required body sections present
- [ ] At least 1 [[wikilink]] in `## Connections` with one-line reason
- [ ] `^[inferred]` / `^[ambiguous]` markers used correctly
- [ ] No Mermaid in entity/concept pages
- [ ] Wikilinks use **bare filename only** — no `<subfolder>/` path prefix, no `.md` extension
- [ ] `## User Notes` (if previously present) preserved verbatim
- [ ] `## Sources` block added/updated with reference page link

If any check fails on a generated page, fix before moving to next source.

## Boundaries (what wiki-ingest does NOT do)

- ❌ Does not scan Open Questions for web research (that's `wiki-auto-research`)
- ❌ Does not validate cross-page consistency (that's `wiki-lint`)
- ❌ Does not infer non-cited cross-links (that's `wiki-cross-linker`)
- ❌ Does not invoke web search (purely local source → wiki transformation)
- ❌ Does not modify source files in original location (read-only on sources)
