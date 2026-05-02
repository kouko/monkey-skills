---
name: init
description: |
  Use when: setting up repo-wiki for the first time in a repository,
  or re-seeding the knowledge base from scratch. Default mode scans
  the entire src/ tree to build complete entity coverage and pulls
  per-module recent commits (N=5). Use "init full-history" for an
  era-grouped backfill of the complete git history. Triggers on
  "init repo-wiki", "set up knowledge base", "seed from git history",
  "/repo-wiki:init", "初始化 repo-wiki", "建立知識庫".
  Do NOT trigger for: incremental updates after changes (use
  /repo-wiki:ingest), answering questions (use /repo-wiki:query).
---

# Repo Wiki — Init Workflow (v1.1)

Init has three coverage phases:

| Phase | Always runs? | Answers |
|---|---|---|
| **Phase 1** — src/ scan + per-module last-N commits | Yes | "What modules exist? What's recent for each?" |
| **Phase 2** — Bounded global git scan (90d) | Yes | "What major cross-module changes happened recently?" |
| **Phase 3** — Era-grouped full history backfill | Only on `init full-history` | "What were the historical major decisions?" |

The `.repo-wiki/` directory is owned entirely by repo-wiki skills.
Source layer (`src/**`) is immutable — never modify code files. Init
**reads only path metadata + git log**; it does NOT open or summarize
src/ file contents (this preserves WHY-not-WHAT — see Decision 14).

## Step 1: Sanity Check

```bash
test -d .git || { echo "Not a git repo. Aborting."; exit 1; }
```

If `.repo-wiki/` already exists, ask the user:

> `.repo-wiki/` already exists. Re-running init will:
>  - Add a new init entry to log.md
>  - Re-scan src/ and refresh entity stubs (overwriting earlier
>    auto-generated stubs but preserving any human-edited sections)
>  - Append additional source pages from the global scan window
>
>  Continue? (yes/no)

Abort on "no".

## Step 2: Scaffold Directory Structure

```bash
mkdir -p .repo-wiki/sources
mkdir -p .repo-wiki/entities
mkdir -p .repo-wiki/concepts
mkdir -p .repo-wiki/syntheses
```

Copy plugin templates into `.repo-wiki/`:
- `assets/SCHEMA.md` → `.repo-wiki/SCHEMA.md`
- `assets/index.md` → `.repo-wiki/index.md`
- `assets/log.md` → `.repo-wiki/log.md`
- `assets/overview.md` → `.repo-wiki/overview.md`

(Resolve asset path relative to this SKILL.md location: `assets/<file>.md`.)

## Step 3: CLAUDE.md Drop-in

Read or create `CLAUDE.md` in the repo root. The drop-in block (also
available as `assets/claude-md-snippet.md`):

```markdown
<!-- repo-wiki:start -->
## .repo-wiki/ Directory

`.repo-wiki/` is managed by the repo-wiki plugin.

- Do NOT edit files in `.repo-wiki/` directly — run `/repo-wiki:ingest`
- To query the codebase: `/repo-wiki:query "<question>"`
- To re-seed from git history: `/repo-wiki:init`

Schema rules: `.repo-wiki/SCHEMA.md`
<!-- repo-wiki:end -->
```

Write rules (idempotent):
- If `CLAUDE.md` doesn't exist: create it with just this block
- If `CLAUDE.md` exists but has no `<!-- repo-wiki:start -->` marker: append the block
- If `CLAUDE.md` exists and has the markers: replace the block between
  `<!-- repo-wiki:start -->` and `<!-- repo-wiki:end -->`

Never touch `CLAUDE.md` content outside the marked block.

## Step 4: Mode Dispatch

Detect mode from user's invocation:

- **No arg / typical args** ("init from last year", "init last 100 commits") → **default mode** (Phase 1 + Phase 2)
- **Arg contains "full-history" / "full backfill" / "完整歷史" / "全歷史"** → **full-history mode** (Phase 1 + Phase 2 + Phase 3)

Default mode is the right choice for almost all initial setup. Only
trigger Phase 3 when user explicitly asks for historical decision
backfill — it produces era pages and increases token cost.

---

## Phase 1 — Source Tree Scan + Per-Module History (always runs)

This phase ensures **every module in src/ becomes a knowledge entity**,
not just modules that happened to change in the last 90 days.

### Step 4a — Discover Modules

```bash
git ls-files
```

Use the output to build a tree of currently tracked paths. Identify
the source root using these heuristics in order:

1. If `src/` exists → use `src/`
2. Else if `lib/` exists → use `lib/`
3. Else if `app/` exists → use `app/`
4. Else if `packages/*/src/` pattern → use those (monorepo case)
5. Else if `cmd/`, `internal/`, `pkg/` exist (Go convention) → use them
6. Else → fallback to repo root, but exclude these top-level dirs:
   `.git/`, `node_modules/`, `dist/`, `build/`, `vendor/`,
   `.repo-wiki/`, `.claude/`, `__pycache__/`, `target/`, `out/`

**Depth rule**: a module = directory at depth-1 OR depth-2 from the
source root. Subdirectories deeper than depth-2 are aggregated into
their parent module's `paths:` (not split into separate entities).

Examples:
- `src/auth/` → module `Auth`
- `src/auth/middleware/` → module `AuthMiddleware`
- `src/auth/middleware/jwt/handler.ts` → its path goes into
  `AuthMiddleware`'s `paths:`, no separate entity

Apply the **Entity Name Normalization Rule** in `.repo-wiki/SCHEMA.md`
to derive entity names — strip prefix (`src/`, `lib/`, etc.), split on
`/`/`-`/`_`, PascalCase concat. This is the same rule ingest uses, so
init and ingest produce identical names for the same module.

### Step 4b — Entry-Point Detection

For each discovered module, look for entry-point files (top 3 by
priority):

| Language / framework | Entry-point file patterns |
|---|---|
| TS / JS | `index.ts`, `index.tsx`, `index.js`, `index.jsx` |
| Python | `__init__.py`, `main.py`, `__main__.py` |
| Go | `main.go`, `mod.go`, files in `cmd/` |
| Rust | `lib.rs`, `main.rs`, `mod.rs` |
| Java / Kotlin | `Main.java`, `Application.kt` |
| Generic | `README.md`, `package.json` (read only the `name` field) |

**Only record the path**, do NOT open the file content (except
`package.json`'s `name` field, which is metadata not implementation).

If no entry-point matches, list the 1-3 most-touched files in the
module from git stat as fallback.

### Step 4c — Per-Module History Pull

For each module, run:

```bash
git log --max-count=5 --pretty=format:'%h|%ai|%s' -- <module-path-1> <module-path-2> ...
```

This returns the last 5 commits that touched any file in this module's
paths, **regardless of how long ago**. A 5-year-old stable module
still gets 5 entries.

`%h` = short SHA, `%ai` = ISO date, `%s` = subject. Pipe-separated for
easy parsing.

If a module has fewer than 5 commits in its history, capture what's
available (could be just 1-2 entries).

### Step 4d — Write Entity Stubs

For each discovered module, write `.repo-wiki/entities/<EntityName>.md`:

```markdown
---
title: "<EntityName>"
type: entity
last_updated: <today>
paths:
  - <module-path-1>
  - <module-path-2>
sources: []
---

## Responsibility
TODO — fill via /repo-wiki:ingest "<observation>".

(Source layer is `src/`; this entity is a knowledge cache, not authority.
src/ is the source of truth for current behavior. Query verifies cached
claims at key moments via T1-T7 triggers.)

## Common Entry Points
- <entry-point-1>
- <entry-point-2>

## Recorded Decisions

(Seed entries from per-module git log — most recent first; subsequent
/repo-wiki:ingest calls append more.)

- <YYYY-MM-DD> — <commit subject> (`<sha>`)
- <YYYY-MM-DD> — <commit subject> (`<sha>`)
- ... (up to 5 entries)

## Architecture Snapshot
TODO — fill via /repo-wiki:ingest after working with this module.

## Gotchas & Non-Obvious Design
TODO — these surface during real work.

## Dependencies
TODO
```

**Why entity stubs are skeletal**: init seeds *structure* (paths +
entry-points + recent commit log), not *content* (responsibility,
architecture, gotchas). Content fills in via `/repo-wiki:ingest`
during real work — that's where WHY signal is strongest. Init
fabricating WHY from path names alone produces low-quality entries
(violates Decision 1: WHY first).

### Collision handling

If two modules normalize to the same entity name (e.g., `src/auth/`
and `lib/auth/` both → `Auth`), apply the disambiguator from the
stripped prefix:
- First created: `Auth`
- Second: `LibAuth`

Detect collision by checking existing entities before writing.

---

## Phase 2 — Bounded Global Git Scan (always runs)

This phase captures recent **cross-module / large** changes that
deserve their own source page (separate from the per-module history
inlined in Step 4c).

### Step 5 — Scan recent commits

Default window: last 90 days OR last 50 commits, whichever hits first.
User may override via natural-language arg:
- "init from last year" → 365 days
- "init last 100 commits" → 100 commit cap
- "init from 2026-01-01" → date floor

```bash
git log --since='90 days ago' --max-count=50 \
  --pretty=format:'%H|%ai|%an|%s%n%b%n----' \
  --name-only --stat
```

If git log is empty (brand-new repo with only init commit): skip Steps
5-7, write a log entry noting "no recent history to seed beyond per-module
stubs", and finish.

### Step 5a — Logical Batching

Group commits into batches by:
- **Branch boundary**: merge commits act as separators
- **Time gap**: >3 days idle between consecutive commits = new batch
- **File overlap**: consecutive commits sharing >50% of changed paths
  belong to the same batch (Jaccard similarity on path sets)

**Hard cap: 15 source pages per init (Phase 2)**. If initial grouping
yields >15 batches, downsample:

1. Widen time gap: try 7-day threshold. Re-group.
2. Widen further: try 14-day threshold. Re-group.
3. Hard truncate: if still >15, keep top 15 by total LOC changed
   (insertions+deletions). Other commits go into a single
   `YYYY-MM-DD-init-overflow.md` source page noting:
   > "<N> additional batches were observed but not individually
   > documented; re-run /repo-wiki:ingest after browsing to capture
   > specific decisions."

### Step 5b — Edge Cases

- **Empty git history**: skip; log "no recent history beyond per-module stubs"
- **Only one commit**: produce exactly one source page
- **Only merge commits**: treat the entire merge graph as one batch
- **Single-batch widen**: if all commits fall into one batch even with
  3-day threshold, accept the single batch — don't artificially split

### Step 6 — Write Source Pages + Backfill Entity Cross-Refs

For each batch, write `.repo-wiki/sources/YYYY-MM-DD-<slug>.md`:

```markdown
---
title: "<Short description, derived from leading commit subject>"
type: source
origin: git
date: <date of latest commit in batch>
commits: ["<sha>", "<sha>", ...]
modules_affected: ["<entity-name>", ...]
---

## What Changed
2-4 sentences synthesizing the batch (from commit subjects + bodies).

## Key Decisions
- Decision and reason (extract from commit message bodies; if absent,
  state "WHY not captured in commit messages — consider /repo-wiki:ingest
  with context to add")

## Connections
- [EntityName](../entities/EntityName.md) — how this batch affected this entity

## Notes
- Generated by /repo-wiki:init Phase 2 global scan.
```

**Critical — do NOT create new entities here**. Phase 1 already
created entity stubs for every module. If a batch touches a path that
doesn't have an entity yet (e.g., a new file outside any tracked
module), then the path isn't part of an existing module — handle by
either (a) creating a new entity if the path constitutes a new module,
or (b) noting it in the source page without entity backfill.

For each entity referenced in the batch:
- Append the new source slug to entity's `sources:` frontmatter array
- Append to entity's `## Recorded Decisions`:
  ```
  - <date> — <batch title> (see [<source-slug>](../sources/<source-slug>.md))
  ```

---

## Phase 3 — Era-Grouped Full History Backfill (only on `init full-history`)

User-explicit only. Triggers when arg contains "full-history",
"full backfill", "完整歷史", or "全歷史".

### Step 7a — Full git log

```bash
git log --all --pretty=format:'%H|%ai|%s' --name-only
```

No time bound. Captures everything since repo init.

### Step 7b — Era grouping

Group commits by 6-month era based on commit date:
- 2020-H1 (Jan-Jun 2020), 2020-H2 (Jul-Dec 2020), 2021-H1, ...

For each era, identify **major commits** using these heuristics:

- 50+ files changed in a single commit
- Cross-module merge commit (touches 3+ entities from Phase 1)
- PR title with conventional-commit major change indicator: `feat(...)`,
  `refactor(...)`, `BREAKING CHANGE:` (in body)
- Tagged release commits

Other commits in the era are summarized in a one-line aggregate stat
("N additional commits across M files").

### Step 7c — Era source pages

For each era with at least one major commit, write
`.repo-wiki/sources/era-YYYY-HX.md`:

```markdown
---
title: "Era YYYY-HX — <leading theme>"
type: source
origin: git
era: YYYY-HX
date: <last commit date in era>
commit_count: <total commits in era>
major_commits: ["<sha>", ...]
---

## Era Summary
<1-2 sentences synthesizing what happened this era.>

## Major Decisions
- <date> <subject> (`<sha>`) — <module(s) affected, why>
- ...

## Aggregate Stats
- N total commits
- M unique authors
- K files touched

## Notes
- Generated by /repo-wiki:init Phase 3 (full-history mode).
- For module-level history, see entity pages.
```

**Era pages are EXEMPT from the 15-source-page hard cap** (Phase 2's
limit applies only to default-mode batches). A 5-year-old repo could
generate 10 era pages.

For each era page, also backfill entity `Recorded Decisions`:
- For each major commit in the era that touched a known entity, append
  to that entity's `## Recorded Decisions`

### Step 7d — log.md entry for Phase 3

```
## [<date>] init:full-history | era backfill (N eras, M major commits)
- Phase: full-history
- Era pages created: N
- Entities updated: M
```

---

## Step 8 — Overview Synthesis

Write `.repo-wiki/overview.md`:

```markdown
---
title: Codebase Overview
type: overview
last_updated: <today>
seeded_from: "Phase 1 (src/ scan) + Phase 2 (90d scan) [+ Phase 3 (full history) if applicable]"
---

# Codebase Overview

## Repository
<One paragraph: pull from README.md if present; otherwise describe from
top-level directory structure.>

## All Modules (N total)

### Recently active (touched in scan window)
- [EntityName1](entities/EntityName1.md) — paths: src/auth/
- [EntityName2](entities/EntityName2.md) — paths: src/api/

### Stable (older history, still in src/)
- [EntityName3](entities/EntityName3.md) — paths: src/legacy-utils/
- ...

## Recent Themes (last 90 days)
<2-4 themes synthesized from Phase 2 source pages — what kinds of
changes have been happening.>

## What Lives Where
- .repo-wiki/sources/ — change history (with WHY)
- .repo-wiki/entities/ — module knowledge (skeletal stubs after init; fills via ingest)
- .repo-wiki/concepts/ — patterns / ADRs (empty after init; grows via ingest)
- .repo-wiki/syntheses/ — saved query answers (empty after init; grows via query)
```

## Step 9 — Index + Log

Update `.repo-wiki/index.md` to list all created pages.

Append to `.repo-wiki/log.md`:

```
## [<date>] init | scaffold + per-module history (N modules) + 90d global scan (M source pages)
- Mode: default
- Source root: <detected root>
- Modules discovered: N
- Per-module history: 5 commits each (N total)
- Window: 90 days, max 50 commits (override: <if user customized>)
- Last commit SHA: <HEAD sha at scan time>
- Phase 2 source pages created: M (cap: 15)
- Entity stubs created: N
- Overview written: yes
- CLAUDE.md drop-in: <created | appended | replaced>
```

If `init full-history` was used, follow with the Phase 3 log entry
from Step 7d.

**Recording the "Last commit SHA" is critical** — `/repo-wiki:ingest`
uses this to know where to start incrementally.

## Step 10 — Summary Report

Print to user:

```
✓ Knowledge base initialized at .repo-wiki/

  Phase 1 (src/ scan + per-module history):
    - N modules discovered
    - N entity stubs (paths + Common Entry Points + last 5 commits each)

  Phase 2 (recent global git scan):
    - M source pages (covering last 90d / 50 commits)
    - Entity Recorded Decisions backfilled with cross-references

  [If full-history]
  Phase 3 (era backfill):
    - K era pages
    - L entities updated with historical decisions

  Files updated:
    - .repo-wiki/{SCHEMA,index,log,overview}.md
    - .repo-wiki/entities/*.md (N files)
    - .repo-wiki/sources/*.md (M files)
    - CLAUDE.md drop-in (<created/appended/replaced>)

  Next steps:
    1. Skim .repo-wiki/overview.md to see All Modules
    2. Capture tribal knowledge:
       /repo-wiki:ingest "<observation>"
    3. After your next feature, run /repo-wiki:ingest
    4. Ask questions: /repo-wiki:query "<question>"

  Entity Responsibility / Architecture / Gotchas are TODO — they fill
  in via real work, not by guessing from path names.
```

## Rules

NEVER:
- Modify any file under `src/` or anywhere outside `.repo-wiki/` and `CLAUDE.md`
- **Open and read src/ file contents** — only `git ls-files` paths,
  entry-point file paths (not contents), and `git log` metadata are
  allowed inputs
- Write content into entity stubs that the LLM cannot ground in
  observable facts (paths, commit messages) — don't fabricate WHY
- Touch `CLAUDE.md` content outside the `<!-- repo-wiki:start/end -->` block
- Use `[[wikilinks]]` — only standard markdown links
- Add naming suffixes like `Module` / `Service` — name comes from
  Entity Name Normalization Rule
- Run Phase 3 by default (only when user explicitly says full-history)

ALWAYS:
- Apply Entity Name Normalization Rule for all entity filenames
- Make CLAUDE.md drop-in idempotent
- Bound Phase 2 with the 15 source page cap (Phase 1 + Phase 3 are
  uncapped because they have natural bounds: # of modules + # of eras)
- Record the last commit SHA in log.md (ingest depends on it)
- Mark uncertain entity claims with TODO
- For Phase 1, build entity stub for **every** detected module (no threshold)

## Why this design (rationale anchored in spec Decisions)

- **Decision 1 (WHY first)**: preserved. Init never reads src/ file
  contents; entity Responsibility is explicitly TODO.
- **Decision 9 (descriptive thresholds)**: relaxed for Phase 1 entities —
  every module gets a stub because completeness matters more than
  selectivity for the seed pass. Concept threshold unchanged.
- **Decision 13 (src/ is authority)**: strengthened. Phase 1 derives
  paths from `git ls-files`, so `paths:` frontmatter is 100% accurate
  to current src/ state.
- **Decision 14 (init reads path metadata, not file contents)**: new.
  Init's src/ scan is metadata-only, distinct from Greptile/DeepWiki
  which read code to write summaries.
- **Decision 15 (full-history is opt-in)**: new. Default init bounds
  source-page generation to recent activity; full history is explicit.
