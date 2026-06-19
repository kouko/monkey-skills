---
name: wiki-setup
description: |
  Scaffold an LLM wiki layer in an Obsidian vault — 6 type folders + index/log/hot/manifest + .obsidian-wiki.config. Use to init wiki/ first-time or rebuild. Not repo-wiki:init / dbt-wiki:init; full vault setup → obsidian-vault-setup.
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
  • Writes .obsidian-wiki.config with OBSIDIAN_WIKI_VAULT_PATH and OBSIDIAN_WIKI_EXCLUDE_DIRS

What this skill doesn't do:
  • It does NOT ingest your notes — that's /wiki-ingest (after setup)
  • It does NOT touch existing vault notes
  • It does NOT install Obsidian or open the vault

How we'll proceed:
  1. I'll verify CWD is the vault root (look for .obsidian/, etc.)
  2. Ask 2 quick questions: where wiki/ lives, which folders to exclude
  3. Show a preview tree, wait for "build it" confirmation
  4. Create files / dirs / .obsidian-wiki.config

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

### Step 0 — Detect legacy `.env` config (migration path)

If `<vault-root>/.env` exists AND contains `OBSIDIAN_VAULT_PATH=` line:

This is a v3.7.0-or-earlier config. Offer migration:

```
Detected legacy wiki config in .env (v3.7.0 or earlier).

In v3.8.0 the config moved to .obsidian-wiki.config to avoid:
  - Claude permission rules that block .env reads
  - Anti-secret tooling false positives
  - .gitignore default patterns
  - Naming collision with other tools' .env files

I can migrate by:
  1. Reading OBSIDIAN_VAULT_PATH, OBSIDIAN_EXCLUDE_DIRS, OBSIDIAN_RAW_DIR,
     OBSIDIAN_MAX_PAGES_PER_INGEST, OBSIDIAN_CATEGORIES, LINT_SCHEDULE from .env
  2. Renaming each key to OBSIDIAN_WIKI_*
  3. Writing to .obsidian-wiki.config (multi-line values for arrays)
  4. Adding a deprecation comment in .env (not deleting — you may have
     other unrelated env vars there)

Proceed with migration? [Y/n]
```

If user accepts → migrate then continue with normal flow (Step 1 may be skipped if the migrated config is complete).

If user declines → continue with normal flow (will write fresh `.obsidian-wiki.config`; legacy `.env` stays untouched but ignored).

### Step 1 — Identify the vault

Then verify:

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
> Values written to `.obsidian-wiki.config` MUST be bare directory names or **shell globs** (no leading/trailing slashes).
>
> Glob patterns supported:
> - `daily` — literal exact match
> - `_*` — any name starting with underscore
> - `temp?` — single-char wildcard
> - `[Aa]rchive` — case-variant char class
>
> Each pattern is on its own line within the multi-line value (see Step 3b).
> Multi-line format means patterns may contain commas, spaces, and CJK characters
> without escaping — only newlines are forbidden (which filesystems disallow anyway).
>
> When normalizing user input from CSV form, strip surrounding whitespace and trailing `/`.
> Example: user types "daily/, inbox/, _*" → write each on its own line in the config file.

> [!note] Always-excluded system paths (NOT user-configurable, hardcoded in `wiki-ingest`)
>
> **DIR blacklist** (top-level match):
> - `wiki/` itself (the output — would otherwise loop)
> - `.*` (any top-level dir starting with `.`) — catches `.obsidian`, `.trash`, `.git`, `.github`, `.vscode`, `.idea`, `.claude`, `.cursor`, `.codex`, `.windsurf`, `.devcontainer`, `.husky`, `.changeset`, etc. by Unix convention
> - `node_modules/`, `_raw/` (system noise)
>
> **FILE blacklist** (any-depth match) — NEW in v3.9.0:
> - `CLAUDE.md`, `AGENT.md`, `AGENTS.md`, `MEMORY.md` — universal agent-config filenames
>
> **Root-level hidden files** like `.notes.md` are also auto-excluded (mirrors the `.*` dir rule).
>
> User exclusions in `.obsidian-wiki.config` (`OBSIDIAN_WIKI_EXCLUDE_DIRS` and `OBSIDIAN_WIKI_EXCLUDE_FILES`) are **additional** to these.

Do not prompt for `MAX_PAGES_PER_INGEST`, `LINT_SCHEDULE`, etc. — defaults are sane.

## STEP 2 — Show planned structure, wait for confirmation

```
I'll create:

📁 [vault-root]
├── .obsidian-wiki.config    ← wiki config (shell-sourceable, dot-hidden)
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
    - DIR (system, top-level): wiki/, .* (all dot-dirs — .obsidian, .git, .claude, etc.), node_modules/, _raw/
    - FILE (system, any depth): CLAUDE.md, AGENT.md, AGENTS.md, MEMORY.md
    - Root-level hidden .md files (.notes.md style) auto-excluded

Type "build it" to create, or tell me what to change.
```

Wait for confirmation. Do not act before user agreement.

## STEP 3 — Build after confirmation

### 3a. Create directory tree

```bash
mkdir -p wiki/{entities,concepts,synthesis,skills,journal,references}
```

### 3b. Write `.obsidian-wiki.config`

Write to `<vault-root>/.obsidian-wiki.config` (shell-sourceable; NOT `.env` — this avoids Claude permission rules and anti-secret tooling collisions). Multi-line values for arrays — patterns may contain commas, spaces, or CJK without escaping:

```bash
# Obsidian Wiki layer config (managed by /wiki-setup; safe to hand-edit).
# Sourced by all wiki-* skills via: set -a; . .obsidian-wiki.config; set +a
#
# === Required ===

# Path of the wiki output folder, relative to vault root.
# Configurable: rename `wiki/` to `knowledge/`, `kb/`, `.wiki/`, etc.
OBSIDIAN_WIKI_VAULT_PATH=wiki

# Folders to EXCLUDE from wiki ingestion (DIR blacklist, top-level match).
# Multi-line, one shell glob per line. Nested dirs with same name are NOT excluded.
# Always-excluded (hardcoded): wiki/, .* (all dot-dirs), node_modules/, _raw/
# Glob patterns:
#   daily       literal exact match
#   _*          any name starting with underscore (e.g. _raw, _archive)
#   temp?       single-char wildcard
#   [Aa]rchive  case-variant char class
OBSIDIAN_WIKI_EXCLUDE_DIRS="<one pattern per line, derived from Step 1>"

# Files to EXCLUDE from wiki ingestion (FILE blacklist, any-depth match).
# Multi-line, one basename glob per line. Applies to .md files at any depth.
# Common additions: README.md, TODO.md, CHANGELOG.md, LICENSE.md
# Always-excluded (hardcoded): CLAUDE.md, AGENT.md, AGENTS.md, MEMORY.md
# Root-level hidden files (.notes.md style) also always excluded.
OBSIDIAN_WIKI_EXCLUDE_FILES=""

# === Optional ===

# Hard cap per /wiki-ingest run. Consumed by wiki-ingest STEP 1.
OBSIDIAN_WIKI_MAX_PAGES_PER_INGEST=15

# Batch order when NEW + MODIFIED exceeds the cap (oldest-first | newest-first).
# Default is `oldest-first` (backfill posture — recommended for catch-up).
# Override per-run by including 'latest' / 'recent' / 'oldest' / 'backfill' / 最新 / 最舊
# in your /wiki-ingest prompt.
OBSIDIAN_WIKI_BATCH_ORDER=oldest-first

# Vault primary body language for wiki/ pages. BCP-47 codes (zh-TW, ja, en, ko).
# Used as fallback in language-policy.md decision tree.
# Required when LANGUAGE_POLICY=enabled.
OBSIDIAN_WIKI_PRIMARY_LANGUAGE=

# Switch for body language policy. `enabled` runs the decision tree in
# references/language-policy.md. Omit (or empty) → legacy LLM heuristic
# (current v3.10.0 behavior; full backward compat).
OBSIDIAN_WIKI_LANGUAGE_POLICY=

# Optional vault-owned term-preservation list. Terms in this file are
# NEVER translated, regardless of language policy. Vault-relative path.
OBSIDIAN_WIKI_PRESERVE_TERMS_FILE=

# --- Advisory-only keys below (documentation, not consumed by skills) ---
# These reflect current convention; changing them does NOT alter behavior.
# Wiki page categories are fixed at the 6 type folders below; renaming here
# won't make wiki-ingest write to a different folder set.
OBSIDIAN_WIKI_CATEGORIES="concepts
entities
skills
references
synthesis
journal"

# Convention name for raw-dump exclusion. Hardcoded as `_raw` in scan-vault.sh.
OBSIDIAN_WIKI_RAW_DIR=_raw

# Convention only — no scheduler reads this; rerun /wiki-lint manually.
OBSIDIAN_WIKI_LINT_SCHEDULE=weekly
```

**Conversion rule** for the `OBSIDIAN_WIKI_EXCLUDE_DIRS` value:
- User input from Step 1 is comma-separated (e.g. `daily, inbox, _*`)
- Split on commas, trim whitespace and trailing `/`, write one pattern per line inside the multi-line quoted string
- Example output for `daily, inbox, _*`:
  ```
  OBSIDIAN_WIKI_EXCLUDE_DIRS="daily
  inbox
  _*"
  ```

Paths are **vault-relative**, not absolute. Consumer skills resolve them against CWD.

If `.obsidian-wiki.config` already exists, do NOT overwrite. Show diff and ask user.

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
wiki/.manifest.json
```

`.obsidian-wiki.config` is **NOT** added to .gitignore — it's safe to version control (no secrets, just paths and patterns). User may opt to commit it for cross-machine sync.

`hot.md` also stays tracked — it's small and useful in cross-machine sync.

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
