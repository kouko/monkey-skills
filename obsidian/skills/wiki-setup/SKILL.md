---
name: wiki-setup
description: Scaffold an LLM wiki layer in an Obsidian vault — 6 type folders, index/log/hot/manifest/.env. Use to init wiki/ first time or rebuild. Do NOT use for repo-wiki:init, dbt-wiki:init, or vault setup (use obsidian-vault-setup). Obsidian wiki 初期化・初始化。
---

# Wiki Setup — One-Time Wiki Layer Initialization

Scaffolds an LLM wiki layer inside an Obsidian vault. Run **once per vault**.

## Surface Orientation (when invoked with empty / sparse prompt)

If the user invokes this skill with no arguments OR a very sparse prompt (e.g. just "set up wiki", "init", "/wiki-setup"), AND none of the following sources already contain an actionable brief:

- prior conversation turns specifying vault path / scope / exclusions
- IDE selection or opened-file context indicating the target vault
- a referenced plan / memory file describing the wiki design

…then **before doing any work**, surface this orientation:

```
I'll set up an LLM wiki layer (knowledge distillation layer) inside an Obsidian vault.

What this skill does:
  • Scaffolds wiki/ with 6 type folders: entities, concepts, synthesis, skills, journal, references
  • Creates index.md, log.md, hot.md (session cache), .manifest.json (delta tracking)
  • Writes .env with OBSIDIAN_VAULT_PATH and OBSIDIAN_EXCLUDE_DIRS

What this skill doesn't do:
  • It does NOT ingest your notes — that's /wiki-ingest (after setup)
  • It does NOT touch existing vault notes
  • It does NOT install Obsidian or open the vault

How we'll proceed:
  1. I'll verify CWD is the vault root (look for .obsidian/, etc.)
  2. Ask 2 quick questions: where wiki/ lives, which folders to exclude
  3. Show a preview tree, wait for "build it" confirmation
  4. Create files / dirs / .env

Helpful before we start:
  • Run me from inside the vault root (cd to the vault first)
  • If wiki/ already exists with content, I'll ask before touching it
  • Have a 1-line answer ready for which folders to exclude (default: daily, inbox)

Ready? Tell me anything specific (e.g. "wiki/ at default, exclude daily/inbox/projects"),
or just say "go" and I'll start with defaults.
```

After orientation, wait for user response — don't proceed to Pre-flight Check until they reply.

**Skip orientation** when current prompt is ≥50 chars with concrete scope ("set up wiki at /Users/me/vault, exclude daily and personal"), OR prior conversation has the brief. Don't trigger orientation just because the *current* turn is short.

## Pre-flight Check

Before doing anything, verify:

1. **CWD is the vault root** (or user explicitly tells you otherwise). Look for hints in priority order:
   - `.obsidian/` directory (strongest signal — Obsidian-managed vault)
   - existing CLAUDE.md mentioning Obsidian
   - vault-shaped folder layout (notes in markdown, no code)

   **If `.obsidian/` is missing**, the vault may be uninitialized. Treat this as one of:
   - User just created the folder and hasn't opened it in Obsidian yet → wiki-setup proceeds; remind user to open the folder in Obsidian afterwards (Obsidian will then create `.obsidian/`)
   - Wrong directory → ask user to confirm or specify the correct vault root
   - Don't auto-create `.obsidian/` ourselves; let Obsidian own that

2. **No existing `wiki/` non-empty content** — if `wiki/` exists with files, ask user: keep / archive / overwrite.

3. **Obsidian convention** — vault-relative paths only; do not write absolute paths into config files.

If CWD is wrong or vault is unclear, ask the user for the vault root path before proceeding.

## STEP 1 — Collect configuration

Use `AskUserQuestion` to confirm the wiki output path and folders to exclude:

```
Question: "Where should the wiki layer live?"
Options:
1. "wiki/" — recommended, vault root subfolder
2. "Custom path" — user types a vault-relative path
```

```
Question: "Which folders should be EXCLUDED from wiki ingestion? (blacklist)"
Options:
1. "daily, inbox" — recommended default (skip flow notes, capture-only zones)
2. "daily, inbox, _*" — also skip any `_`-prefixed dir (Obsidian convention for system / drafts / attachments)
3. "daily, inbox, projects" — also skip in-progress project notes
4. "daily, inbox, personal" — also skip private personal notes
5. "Custom" — user types comma-separated patterns (shell globs supported)
```

> [!important]
> Values written to `.env` MUST be bare directory names or **shell globs** (no leading/trailing slashes).
> Glob patterns supported (NEW in v3.7.0):
> - `daily` — literal exact match
> - `_*` — any name starting with underscore
> - `temp?` — single-char wildcard
> - `[Aa]rchive` — case-variant char class
>
> When normalizing user input, strip surrounding whitespace and trailing `/` before writing.
> Example: user says "daily/, inbox/, _*" → write `OBSIDIAN_EXCLUDE_DIRS=daily,inbox,_*`.

> [!note] Always-excluded system paths
> The following are excluded automatically (NOT user-configurable, hardcoded in `wiki-ingest`):
> - `wiki/` itself (the output — would otherwise loop)
> - `.obsidian/` (Obsidian config)
> - `.trash/` (deleted notes)
> - `.git/`, `node_modules/`, `_raw/` (system noise)
>
> User exclusions in `.env` are **additional** to these.

Do not prompt for `MAX_PAGES_PER_INGEST`, `LINT_SCHEDULE`, etc. — defaults are sane.

## STEP 2 — Show planned structure, wait for confirmation

```
I'll create:

📁 [vault-root]
├── .env                     ← wiki config (gitignore'd)
├── wiki/                    ← will be ingested INTO; auto-excluded from sources
│   ├── index.md             ← global page index
│   ├── log.md               ← append-only operation log
│   ├── hot.md               ← session cache (≤300 chars)
│   ├── .manifest.json       ← SHA-256 delta tracking
│   ├── entities/            ← named tools / projects / people / papers
│   ├── concepts/            ← abstract ideas / frameworks
│   ├── synthesis/           ← cross-source analysis
│   ├── skills/              ← procedural how-to knowledge
│   ├── journal/             ← time-stamped observations
│   └── references/          ← per-source citation index (one file per source)

Source scope (what wiki-ingest will read):
  Whole vault, EXCLUDING:
    - <user-listed exclude dirs from Step 1>
    - wiki/, .obsidian/, .trash/, .git/, node_modules/, _raw/ (always excluded)

Type "build it" to create, or tell me what to change.
```

Wait for confirmation. Do not act before user agreement.

## STEP 3 — Build after confirmation

### 3a. Create directory tree

```bash
mkdir -p wiki/{entities,concepts,synthesis,skills,journal,references}
```

### 3b. Write `.env`

Write to `<vault-root>/.env`:

```bash
# === Wiki layer config ===
OBSIDIAN_VAULT_PATH=wiki

# Folders to EXCLUDE from wiki ingestion (blacklist).
# wiki-ingest scans the entire vault recursively for .md files,
# pruning vault-root-level directories matching any pattern in this list.
# Each entry is a SHELL GLOB pattern (not just a literal name):
#   daily       literal exact match
#   _*          any name starting with underscore (e.g. _raw, _archive)
#   temp?       single-char wildcard
#   [Aa]rchive  case-variant char class
# Always-excluded (hardcoded, not configurable): wiki/, .obsidian/, .trash/, .git/, node_modules/, _raw/
OBSIDIAN_EXCLUDE_DIRS=<comma-joined exclude list from Step 1, normalized: stripped slashes>

OBSIDIAN_CATEGORIES=concepts,entities,skills,references,synthesis,journal

# === Optional ===
OBSIDIAN_MAX_PAGES_PER_INGEST=15
OBSIDIAN_RAW_DIR=_raw
LINT_SCHEDULE=weekly
```

Paths are **vault-relative**, not absolute. Consumer skills resolve them against CWD.

If `.env` already exists, do NOT overwrite. Show diff and ask user.

### 3c. Write `wiki/index.md`

```markdown
# Wiki Index

Global index of all wiki pages. Auto-updated by `wiki-ingest`.

## Entities
<!-- entries appended here by wiki-ingest -->

## Concepts
<!-- entries appended here -->

## Synthesis
<!-- entries appended here -->

## Skills
<!-- entries appended here -->

## Journal
<!-- entries appended here -->

## References
<!-- entries appended here -->
```

### 3d. Write `wiki/log.md`

```markdown
# Wiki Operation Log

Append-only log of wiki-ingest, wiki-lint, wiki-auto-research operations.

| Date | Operation | Source / Trigger | Pages affected |
|------|-----------|------------------|----------------|
```

### 3e. Write `wiki/hot.md`

```markdown
# Hot Cache

Session-level summary of recent wiki activity. Updated by `wiki-query` and `wiki-ingest`.
Cap: ≤300 characters in the active section below.

## Recently touched
(none yet)

## Recently queried
(none yet)
```

### 3f. Write `wiki/.manifest.json`

```json
{}
```

This file maps source-file path → SHA-256 hash. `wiki-ingest` uses it to skip unchanged sources.

### 3g. Update `.gitignore` (if `.git/` present)

Append (only if not already present):
```
.env
wiki/.manifest.json
```

`hot.md` stays tracked — it's small and useful in cross-machine sync.

## STEP 4 — Suggest next actions

```
Wiki layer ready.

Next steps:
  /wiki-ingest         — populate from vault notes (whole vault minus excluded folders)
  /wiki-query          — search the wiki
  /wiki-lint           — health check (run weekly)
  /wiki-cross-linker   — strengthen wikilinks (after each ingest batch)
  /wiki-auto-research  — fill knowledge gaps via web search

The page format spec governing wiki/ pages is owned by /wiki-ingest;
run /wiki-ingest first to see it applied to real pages.
```

## Re-initialization

If user explicitly asks to re-init (`wiki-setup --force` or "rebuild wiki"):
1. Confirm destructive intent — list what will be lost
2. Archive `wiki/` to `wiki_backup_<YYYYMMDD>/`
3. Recreate fresh structure
4. Reset `.manifest.json` to `{}`

Never destroy without explicit user confirmation, even on re-init.
