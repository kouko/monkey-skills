---
name: wiki-ingest
description: Ingest Obsidian vault notes into wiki/ with SHA-256 delta tracking; owns page format spec. Use after new notes land in references/research/lab/. Do NOT use for repo-wiki:ingest or dbt-wiki:ingest. Obsidian wiki 知識蒸留・增量取込・知識萃取。
---

# Wiki Ingest — Source Notes → Wiki Pages

Reads source notes from configured folders (via `.obsidian-wiki.config`), distills knowledge, writes structured wiki pages following [page-format.md](references/page-format.md), and tracks changes via [delta-tracking.md](references/delta-tracking.md).

## Pre-flight (eager)

Read these BEFORE STEP 1:

1. **`.obsidian-wiki.config`** at vault root — must contain `OBSIDIAN_WIKI_VAULT_PATH`, `OBSIDIAN_WIKI_EXCLUDE_DIRS`. May also set `OBSIDIAN_WIKI_EXCLUDE_FILES` (any-depth basename glob list, defaults empty), `OBSIDIAN_WIKI_BATCH_ORDER` (`oldest-first` or `newest-first`, defaults `oldest-first` if absent — backward-compatible), `OBSIDIAN_WIKI_PRIMARY_LANGUAGE` (BCP-47 tag, e.g. `zh-TW`; defaults empty — no language enforcement), `OBSIDIAN_WIKI_LANGUAGE_POLICY` (`enabled` or absent; activates language resolution in STEP 4c when set to `enabled`), and `OBSIDIAN_WIKI_PRESERVE_TERMS_FILE` (vault-relative path to a no-translate term list; only consulted when `OBSIDIAN_WIKI_LANGUAGE_POLICY=enabled`). If missing but legacy `.env` (containing `OBSIDIAN_VAULT_PATH=`) exists, instruct user to run `/wiki-setup` to migrate. If neither exists, instruct user to run `/wiki-setup`.
2. **`wiki/.manifest.json`** — for delta detection. If missing, treat as empty `{}` (likely first ingest after wiki-setup).

## References (lazy — read only when needed)

These are spec references; load them at the moment you need them, not at pre-flight. This keeps small / scoped ingests fast:

| Reference | When to load |
|---|---|
| [references/delta-tracking.md](references/delta-tracking.md) | Before STEP 2 (scan and hash) — defines the manifest update contract |
| [references/batching-policy.md](references/batching-policy.md) | Before STEP 3 (select batch) — cap + order override matrix |
| [references/category-routing.md](references/category-routing.md) | Before STEP 4b (decide category) — decision tree for entities vs concepts |
| [references/page-format.md](references/page-format.md) | Before STEP 4c (generate page) — authoritative output spec; reread before EVERY new page generation |
| [references/language-policy.md](references/language-policy.md) | Before STEP 4c — only when LANGUAGE_POLICY=enabled |

**Why lazy**: a delta-only run with 0 NEW / 0 MODIFIED sources never needs page-format.md or category-routing.md. Eager loading wastes context on the common no-op path.

## Source scope

`wiki-ingest` scans the **entire vault** for `.md` files, with two parallel blacklists — a **DIR blacklist** (top-level match) and a **FILE blacklist** (any-depth basename match) — each with system + user-configurable layers.

**DIR blacklist (top-level match):**
- *System*: `wiki/`, `.*` (any top-level dot-prefix dir — covers `.obsidian`, `.trash`, `.git`, `.github`, `.vscode`, `.idea`, `.claude`, `.cursor`, `.codex`, `.windsurf`, `.devcontainer`, `.husky`, `.changeset`, etc. by Unix convention), `node_modules/`, `_raw/`
- *User-configured*: `OBSIDIAN_WIKI_EXCLUDE_DIRS` from `.obsidian-wiki.config` (default `daily,inbox`; multi-line, one shell-glob pattern per line)

**FILE blacklist (any-depth basename match):**
- *System*: `CLAUDE.md`, `AGENT.md`, `AGENTS.md`, `MEMORY.md` (universal agent-config filenames; excluded wherever they sit). Root-level hidden `.md` files (`.notes.md` style) are also auto-excluded.
- *User-configured*: `OBSIDIAN_WIKI_EXCLUDE_FILES` (multi-line basename globs, defaults empty; common additions: `README.md`, `TODO.md`, `CHANGELOG.md`, `LICENSE.md`, `*.draft.md`)

**Match rule asymmetry**: DIR rules only fire on the top-level segment (`projects/old/daily/` is NOT excluded by `daily/`) because directory semantics are location-sensitive; FILE rules fire at any depth because filename conventions are location-independent.

For the full contract, edge cases, and rationale, see [references/source-scope.md](references/source-scope.md).

## STEP 1 — Determine ingest scope

Read the user's most recent message and apply the decision table below. No `AskUserQuestion` is issued; Claude resolves scope and order autonomously, then prints the one-line summary and proceeds.

### Decision table

| Prompt pattern | scope | order |
|---|---|---|
| Plain `/wiki-ingest` (no arguments) | `whole_vault` | from config (default `oldest-first`) |
| Path token containing `/` and not ending `.md` (e.g. `research/`, `investing/2026/`) | `path:<p>` | from config |
| Single-file token ending `.md` (path or bare basename) | `single_file:<f>` | n/a (not batched) |
| Time keyword: `latest` / `recent` / `newest` / `最新` / `近期` | `whole_vault` | `newest-first` (prompt override) |
| Time keyword: `oldest` / `backfill` / `最舊` / `從頭` / `舊筆記` | `whole_vault` | `oldest-first` (prompt override) |
| Topic word (no `/`, no `.md`, no time-keyword, non-empty token) | `whole_vault` + `topic_filter:<t>` | from config |

### Classification rules

- **Path**: token contains `/` AND does not end with `.md`
- **Single-file**: token ends with `.md` (whether a full path or bare basename)
- **Time keyword**: case-insensitive substring match for ASCII keywords; exact equality for CJK keywords (no case concept)
- **Topic word**: any non-empty token not matched by the above three rules — activates `topic_filter`. Claude passes `TOPIC_FILTER=<topic>` env var to `select-batch.py`; the script applies case-insensitive ASCII substring match on basename AND exact match on frontmatter `tags` / `aliases` values. Scope = `whole_vault` + topic filter (only matching files proceed past STEP 3).

### STEP 1 summary line

After resolving scope and order, print **one line** and continue (user can Ctrl+C to abort):

```
Scope: <whole_vault | path:<p> | single_file:<f>>  (filtered by topic '<t>' if any)
Order: <oldest-first | newest-first>
Source: <config | prompt hint | default>
```

**Config note**: `OBSIDIAN_WIKI_BATCH_ORDER` in `.obsidian-wiki.config` sets the persistent default order (defaults `oldest-first` if absent). Claude reads this value at pre-flight and passes it as `BATCH_ORDER=<value>` to `select-batch.py`; a time-keyword in the prompt overrides it for that run only. When the prompt contains a topic word, Claude additionally passes `TOPIC_FILTER=<topic>` to `select-batch.py` — the script filters candidates to those whose basename contains the topic substring (case-insensitive) OR whose frontmatter `tags` / `aliases` exactly match it.

### Vault scan

Invoke the bundled scan script (POSIX-portable; auto-sources `.obsidian-wiki.config` from the vault root, emits vault-relative paths one per line):

```sh
bash <skill-root>/scripts/scan-vault.sh "$VAULT_ROOT"
```

The script handles top-level pruning, system exclusions, multi-line value parsing, and edge cases. See [scripts/scan-vault.sh](scripts/scan-vault.sh). Do not hand-roll a `find` command. For `path:<p>` or `single_file:<f>` scopes, pass the user-specified path directly to the scan (or use `Read` / `Bash find` for single files).

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

Cap: 15 pages per run (configurable in .obsidian-wiki.config)
```

## STEP 3 — Select batch

Pipe the NEW + MODIFIED paths from STEP 2 into `scripts/select-batch.py`:

```sh
printf '%s\n' "${new_and_modified_paths[@]}" \
  | BATCH_ORDER="${OBSIDIAN_WIKI_BATCH_ORDER:-oldest-first}" \
    BATCH_CAP="${OBSIDIAN_WIKI_MAX_PAGES_PER_INGEST:-15}" \
    MANIFEST_PATH="$VAULT_ROOT/wiki/.manifest.json" \
    VAULT_ROOT="$VAULT_ROOT" \
    ${TOPIC_FILTER:+TOPIC_FILTER="$TOPIC_FILTER"} \
    python3 <skill-root>/scripts/select-batch.py
```

`BATCH_ORDER` is sourced from `OBSIDIAN_WIKI_BATCH_ORDER` read at pre-flight (default `oldest-first`); a time-keyword prompt hint sets it directly per STEP 1 decision table. `TOPIC_FILTER` is included only when Claude detected a topic-word hint in STEP 1 (set to the resolved topic token, casefolded). The script exits `0` on success, `2` on invalid env or unreadable manifest. Consume its JSON output:

| Key | Use |
|---|---|
| `batch` | Ordered list of vault-relative paths to process in STEP 4 (≤ cap) |
| `remaining` | Deferred paths (surfaced in STEP 6 next-batch preview) |
| `skipped_unchanged` | Count of UNCHANGED files (informational) |
| `scope_summary` | Date-range metadata for STEP 6 report |

STEP 4's per-source loop iterates over the `batch` list in the order returned by the script.

**Reference**: load [references/batching-policy.md](references/batching-policy.md) before STEP 3 — defines the full cap + order override matrix.

## STEP 4 — Per-source ingest loop

For each NEW or MODIFIED source, in this order:

### 4a. Read source content

Use `Read`. Capture frontmatter + body. Note any existing `wikilinks` for connection inference.

**Auto-research gate** (per the wiki-auto-research output contract):

- If `frontmatter.generated_by == "wiki-auto-research"`:
  - If `frontmatter.status == "reviewed-accept"` → ingest normally
  - If `frontmatter.status` is `"pending-review"` or `"reviewed-reject"` or missing → **skip**, log to `wiki/log.md` as `skipped-pending-review`, continue to next source

This decouples the user-review gate from auto-research. Manually-written research notes (no `generated_by` field) are always ingested without status check.

### 4b. Decide category (per [category-routing.md](references/category-routing.md))

A single source may contribute to multiple wiki pages (e.g., a paper covering MAB → updates `entities/Thompson-Sampling`, `entities/UCB`, `concepts/exploration-exploitation`). Identify all targets.

### 4c. For each target wiki page

**Language resolution** (only when `OBSIDIAN_WIKI_LANGUAGE_POLICY=enabled`): load
`references/language-policy.md` and resolve body language per its decision tree.
Slug remains ASCII (page-format.md authority); body language follows resolved
policy. If `OBSIDIAN_WIKI_PRESERVE_TERMS_FILE` is set, load it and treat listed
terms as no-translate.

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
- `## Sources` — add link to the per-source reference page (see 4d)
- `frontmatter.sources_count` — increment
- `frontmatter.updated` — today's date
- `frontmatter.summary` — refresh if material changes (≤200 chars)
- `## User Notes` — **preserve verbatim** if present

**Post-write hard check** (run after every page write, BEFORE moving on):

```bash
grep -nE '`[^`]*\[\[[^]]+\]\][^`]*`' <wiki-root>/<category>/<slug>.md
```

If this finds any match, you wrote a backtick-wrapped wikilink (e.g. `` `[[Page]]` `` or `` **`[[Page]]`** ``) — Obsidian renders it as inline code, NOT a clickable link. **Do not advance**: edit the file to remove the wrapping backticks, then re-run the check until empty. The Quality bar self-check (below) is advisory; this grep is the enforced gate. Spec rationale in [page-format.md](references/page-format.md#never-wrap-wikilinks-in-backticks-critical).

### 4d. Create/update reference page

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

## Source

[[<source-basename>]]

## Source Excerpt / TL;DR
2–4 sentence neutral description of what the source argues / measures / claims.

## Key Contributions
- Bullet list — what specifically this source added to the wiki
- Cite which target pages were updated and how
```

> [!warning] `## Source` wikilink format — common LLM mistake
>
> The wikilink inside `## Source` must be the source file's **bare basename** — no folder path, no `.md` extension. The `source_path` frontmatter keeps the full machine-readable path; the body wikilink is a separate human-navigation form for Obsidian.
>
> Given `source_path: references/finance/2026-04-20 台積電財報.md`:
>
> ```markdown
> ✅ [[2026-04-20 台積電財報]]
> ❌ [[references/finance/2026-04-20 台積電財報]]      — path prefix forbidden
> ❌ [[references/finance/2026-04-20 台積電財報.md]]   — path + extension forbidden
> ❌ [[2026-04-20 台積電財報.md]]                      — extension forbidden
> ❌ [[finance/2026-04-20 台積電財報]]                 — partial path also forbidden
> ❌ [[<source-basename>]]                            — literal placeholder (substitute the actual basename)
> ```
>
> **Mechanical rule** (4 steps):
> 1. Take the `source_path` frontmatter value
> 2. **Strip surrounding YAML quotes if present** — YAML allows `source_path: "foo.md"` or `source_path: foo.md` (quoting is mandatory only when the value contains special characters); both must produce the same basename
> 3. Apply basename — drop everything up to and including the last `/`
> 4. Strip the trailing `.md` suffix
>
> The result MUST contain no `/`, MUST NOT end with `.md`, MUST NOT contain literal `"` or `'`. This is enforced by `wiki-lint` L14. See [page-format.md §Wikilink resolution](references/page-format.md#wikilink-resolution) for the underlying rule.

Reference pages are append-only over time — re-ingest of the same source updates `ingested`, may extend `contributes_to` and `Key Contributions`. The `## Source` wikilink stays stable unless the source file is renamed (then `source_path` and the wikilink update together; Obsidian auto-tracks the rename).

### 4e. Ensure `wiki/index.md` stale banner

Ensure `wiki/index.md` has a stale-snapshot banner at the very top. If the first non-empty line of `wiki/index.md` already contains `LLM Tier 1 retrieval` (idempotent marker), skip. Otherwise prepend the following banner block (followed by a blank line) above existing content:

```markdown
> [!warning] Historical snapshot — LLM Tier 1 retrieval has moved
> LLM Tier 1 retrieval is now handled by `wiki-query/scripts/query-frontmatter.py` (frontmatter-only index built on demand from `wiki/**/*.md`).
> This `index.md` is preserved as a historical snapshot for Obsidian human navigation only — it is no longer updated by `wiki-ingest` and may drift from the canonical page set.
```

Do not append new page links to category sections — that responsibility is retired. The banner check is the only mutation in this sub-step.

### 4f. Update `wiki/.manifest.json`

Per [delta-tracking.md](references/delta-tracking.md): write entry with sha256, ISO timestamp, and union of `wiki_pages`.

### 4g. Append to `wiki/log.md`

```markdown
| YYYY-MM-DD | ingest | <source-path> | <comma-separated wiki page links, marked (new) or (updated)> |
```

## STEP 5 — Update `wiki/hot.md`

Refresh the "Recently touched" section with this run's affected pages. Cap entire section ≤300 chars; truncate oldest first.

## STEP 6 — Report and recommend

```
Ingest complete:
  Sources processed:  N
  Wiki pages created: M
  Wiki pages updated: K
  Reference pages:    R
```

**Next-batch preview** (from `scope_summary` in STEP 3 output):

- If `scope_summary.remaining_count == 0`:
  ```
  All NEW sources ingested. Wiki is up-to-date with vault.
  ```
- Else:
  ```
  Next batch on next run: <remaining_first_date> → <remaining_last_date> (~<remaining_count> remaining NEW)
  ```

```
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
- [ ] **No backtick-wrapped wikilinks** — `` `[[Page]]` `` and `` **`[[Page]]`** `` render as inline code in Obsidian (NOT clickable). Use plain `[[Page]]`, `**[[Page]]**`, or `*[[Page]]*` instead
- [ ] `## User Notes` (if previously present) preserved verbatim
- [ ] `## Sources` block added/updated with reference page link

If any check fails on a generated page, fix before moving to next source.

## Boundaries (what wiki-ingest does NOT do)

- ❌ Does not scan Open Questions for web research (that's `wiki-auto-research`)
- ❌ Does not validate cross-page consistency (that's `wiki-lint`)
- ❌ Does not infer non-cited cross-links (that's `wiki-cross-linker`)
- ❌ Does not invoke web search (purely local source → wiki transformation)
- ❌ Does not modify source files in original location (read-only on sources)
