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

If `.repo-wiki/` already exists, set `is_rerun = true` and ask the user:

> `.repo-wiki/` already exists. Re-running init will (idempotent merge):
>  - **Preserve** `log.md` (append a new init entry)
>  - **Preserve** `index.md` / `overview.md` (regenerate listings, keep human-edited prose)
>  - **Refresh** entity init-owned sections (`paths`, `Common Entry Points`,
>    seeded `Recorded Decisions`); **preserve** `Responsibility`,
>    `Architecture Snapshot`, `Gotchas & Non-Obvious Design`, `Dependencies`
>    if you've filled them via ingest
>  - **Skip** Phase 2 source pages already covered (read `log.md` last commit SHA)
>  - **Overwrite** `SCHEMA.md` (frozen schema; plugin-controlled)
>  - **Never touch** `concepts/`, `syntheses/`, or any human-content
>
>  Continue? (yes/no)

Abort on "no".

**Re-run safety contract**: every step below has explicit first-run vs
re-run behavior documented. The skill MUST follow these rules — Step 1's
prompt promises preservation; the rest of the workflow MUST deliver it.

## Step 2: Scaffold Directory Structure

`mkdir -p` is always safe (no-op if dirs exist):

```bash
mkdir -p .repo-wiki/sources
mkdir -p .repo-wiki/entities
mkdir -p .repo-wiki/concepts
mkdir -p .repo-wiki/syntheses
```

Copy plugin templates into `.repo-wiki/` with **conditional rules**:

| Target | First-run | Re-run |
|---|---|---|
| `.repo-wiki/SCHEMA.md` | Copy from `assets/SCHEMA.md` | **Always overwrite** (frozen schema; plugin-controlled, user shouldn't edit) |
| `.repo-wiki/index.md` | Copy from `assets/index.md` | **Skip if exists** (Step 9 regenerates from current entity / source listing — preserves any human-readable additions between re-generations) |
| `.repo-wiki/log.md` | Copy from `assets/log.md` | **Skip if exists** (Step 9 appends new init entry; never wipe history) |
| `.repo-wiki/overview.md` | Copy from `assets/overview.md` | **Skip if exists** (Step 8 updates module listings + recent themes; preserves human-edited "Repository" section between markers if any) |

Pseudocode:

```
if not exists(.repo-wiki/SCHEMA.md) or schema_version_outdated:
    copy assets/SCHEMA.md → .repo-wiki/SCHEMA.md
for f in [index.md, log.md, overview.md]:
    if not exists(.repo-wiki/<f>):
        copy assets/<f> → .repo-wiki/<f>
```

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

### Step 4a-pre — High-Entropy Author-Boundary Pre-Scan

Before path-based heuristics, read **structural fields** from root
configuration files to extract **author-declared module boundaries**.
This aligns the entity tree with what the project's maintainers
officially treat as a module — not just what the directory layout
implies. Without this step, monorepo workspaces, TypeScript path
aliases, and README-declared subsystems get treated identically to
incidental directories like `utils/`.

**Allowed reads** (structural metadata only — NOT implementation code):

| File | Field to read | Boundary signal |
|---|---|---|
| `package.json` (root) | `workspaces` array | npm/yarn workspace packages |
| `pnpm-workspace.yaml` | `packages` globs | pnpm workspace packages |
| `lerna.json` | `packages` array | Lerna workspaces |
| `nx.json` + `**/project.json` | `projects` keys + roots | Nx project boundaries |
| `tsconfig.json` (root + nested) | `compilerOptions.paths` keys | TypeScript path aliases |
| `go.mod` | `module` line + `replace` directives | Go module + local replacements |
| `pyproject.toml` | `[tool.poetry.packages]` / `[project]` `packages` | Python package paths |
| `setup.py` | `packages=` / `package_dir=` | Python (legacy) package paths |
| `Cargo.toml` (root) | `[workspace] members` + `[lib]/[bin] path` | Rust crate boundaries |
| `Gemfile` + root `*.gemspec` | gem names + `lib/` paths | Ruby gem boundaries |
| `composer.json` | `autoload.psr-4` keys + paths | PHP namespace roots |
| `pom.xml` / `build.gradle(.kts)` | `<module>` / `include(...)` | Maven/Gradle subprojects |
| `README.md` (root) | `## H2` headings only (titles, not body) | Author-declared subsystem categories |

**Process**:

1. For each present file, parse the named field. Tolerate missing files
   silently — most repos have only 1-3 of these.
2. Build `author_declared_boundaries` = ordered list of
   `(path_or_alias, source_config, declared_name)` tuples.
3. Resolve glob patterns (e.g. `packages/*`) against `git ls-files` to
   get concrete directory paths.
4. README H2 entries that don't map to a path stay as **named-only
   boundaries** — they inform entity grouping in overview.md but don't
   create entities by themselves.

**Why this is allowed under WHY-not-WHAT**: configs are not
implementation. They declare structure. Reading `workspaces: ["packages/*"]`
is metadata equivalent to reading `git ls-files` — it tells you what
exists, not how it works. Code files (`*.ts`, `*.py`, `*.go`) remain
**off-limits** for content reads through every phase.

**If no config files exist**: `author_declared_boundaries = []`. Step 4a
proceeds purely on heuristics, identical to v1.1 behavior. Existing
single-package repos see no behavior change.

**Output**: pass `author_declared_boundaries` to Step 4a as input.

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

**Author-declared boundary override** (consumes Step 4a-pre output):

For each `(path, source_config, declared_name)` in
`author_declared_boundaries`:

- **Always create an entity** at `path`, even if the depth rule wouldn't
  (e.g., `packages/billing/` is depth-2 outside `src/` — heuristic might
  skip; author declaration forces inclusion)
- **Use `declared_name` as the entity name** when it diverges from path
  normalization (e.g., `tsconfig.json paths: { "@auth/*": ["src/auth/*"] }`
  → entity name `Auth` with `aliases: ["@auth"]` recorded in `paths:`)
- **Author-declared paths shadow heuristic ones** if they overlap — only
  one entity gets created, with author name winning

Heuristic depth-1/2 modules fill the **gaps** not covered by author
declarations. Together they form the entity set: author-declared (high
fidelity to maintainer intent) + heuristic (fills the rest).

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

### Step 4d — Write or Merge Entity Stubs

For each discovered module, the behavior depends on whether the entity
file already exists:

**First-run (file does not exist)**: write the full stub from scratch.

**Re-run (file exists)**: merge — **refresh init-owned sections only**,
**preserve all other sections** to keep ingest-accumulated content.

| Section | Init-owned (refresh on re-run) | User/ingest-owned (preserve on re-run) |
|---|---|---|
| frontmatter `paths:` | ✓ refresh from `git ls-files` | — |
| frontmatter `last_updated` | ✓ refresh to today | — |
| frontmatter `sources:` | — | ✓ preserve (ingest manages) |
| `## Common Entry Points` | ✓ refresh from entry-point detection | — |
| `## Recorded Decisions` (only the seeded `<date> — <subject> (<sha>)` entries from per-module git log) | ✓ refresh seeds (replace with current top-5) | ✓ preserve any entries appended by ingest (`<date> — <batch title> (see [<source-slug>](...))`) |
| `## Responsibility` | — | ✓ preserve unless still `TODO` (then re-write `TODO` line) |
| `## Architecture Snapshot` | — | ✓ preserve unless still `TODO` |
| `## Gotchas & Non-Obvious Design` | — | ✓ preserve unless still `TODO` |
| `## Dependencies` | — | ✓ preserve unless still `TODO` |

Re-run merge algorithm:
1. Read existing entity file (parse frontmatter + section markers)
2. Build new frontmatter: take `sources:` from existing; take `last_updated` = today; take `paths:` from current `git ls-files`
3. For `## Common Entry Points`: replace with current detection
4. For `## Recorded Decisions`: split entries by source — keep ingest-appended entries (those with markdown link to source slug) verbatim, replace per-module-git-log seed entries with current top-5
5. For other sections: keep verbatim
6. Write back

**First-run write — full stub format**:

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

**Re-run dedup first**: read `.repo-wiki/log.md` and find the most
recent `init` or `ingest:git` entry that recorded a `Last commit SHA`.
If `is_rerun` and a previous SHA exists, scope the scan to only commits
after that SHA — same idempotency model ingest uses.

```
if is_rerun and exists(prev_last_sha in log.md):
    git_range = "<prev_last_sha>..HEAD"
else:
    git_range = "since 90 days ago, max 50 commits"
```

Default window for fresh init: last 90 days OR last 50 commits,
whichever hits first. User may override via natural-language arg:
- "init from last year" → 365 days
- "init last 100 commits" → 100 commit cap
- "init from 2026-01-01" → date floor

For fresh init:
```bash
git log --since='90 days ago' --max-count=50 \
  --pretty=format:'%H|%ai|%an|%s%n%b%n----' \
  --name-only --stat
```

For re-run incremental:
```bash
git log <prev_last_sha>..HEAD \
  --pretty=format:'%H|%ai|%an|%s%n%b%n----' \
  --name-only --stat
```

If git log is empty (brand-new repo OR re-run with no new commits since
last init): skip Steps 5-7, append a log entry noting the dedup ("no
new commits since previous init at <sha>"), and proceed to Step 8.

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

**Filename collision check**: before writing a source page, check if a
file at `.repo-wiki/sources/<filename>.md` already exists.
- If exists with same `commits:` frontmatter → **skip** (already covered
  by previous init / ingest)
- If exists with different `commits:` → append `-2`, `-3`, ... suffix
  to the slug to avoid collision (rare; happens when same date + topic
  recurs)

For each batch (with no collision), write `.repo-wiki/sources/YYYY-MM-DD-<slug>.md`:

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

**Re-run preservation**: if `.repo-wiki/overview.md` exists and contains
a section between `<!-- repo-wiki:repository:start -->` /
`<!-- repo-wiki:repository:end -->` markers (user-customized "Repository"
section), preserve that block verbatim. Init only regenerates the
`## All Modules`, `## Recent Themes`, and `## What Lives Where` sections.

If the markers don't exist, init writes a default "Repository" paragraph
wrapped in those markers — so future re-runs preserve it once user edits.

Write or update `.repo-wiki/overview.md`:

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

### Index

`.repo-wiki/index.md` is regenerated from current entity / source /
synthesis listings on every init run. It has no human-edited regions —
the catalog is fully derived. Re-run is safe: it produces the same
index.md the first run would, plus any new entries.

(If user has added inline notes outside the standard sections, those are
considered human-content; init should preserve unknown sections rather
than nuking. Default-template sections are: `## Overview`, `## Sources
(recent → old)`, `## Entities`, `## Concepts`, `## Syntheses`. Anything
outside these gets preserved verbatim.)

### Log

`.repo-wiki/log.md` is **append-only** in all phases. Init **never
truncates** the log; even on re-run, history is preserved.

Append a new entry:

```
## [<date>] init | scaffold + per-module history (N modules) + <X>d global scan (M source pages)
- Mode: default
- Run type: <fresh | re-run>
- Source root: <detected root>
- Modules discovered: N (author-declared: A, heuristic: H)
- Boundary configs scanned: <e.g. package.json:workspaces, tsconfig.json:paths, README.md:H2>
  (or "none — pure heuristic" if no config files matched)
- Per-module history: 5 commits each (N total)
- Window: <fresh: 90 days, max 50 commits | re-run: incremental from <prev_sha>>
- Last commit SHA: <HEAD sha at scan time>
- Phase 2 source pages created: M (skipped: K already covered)
- Entity stubs: <N created | N refreshed (preserved K user-edited sections)>
- Overview: <written fresh | regenerated, preserved Repository section>
- CLAUDE.md drop-in: <created | appended | replaced>
```

If `init full-history` was used, follow with the Phase 3 log entry
from Step 7d.

**Recording the "Last commit SHA" is critical** — both `/repo-wiki:ingest`
and future `/repo-wiki:init` re-runs use this to know where to start
incrementally.

## Step 10 — Summary Report

Print to user:

```
✓ Knowledge base initialized at .repo-wiki/

  Phase 1 (src/ scan + per-module history):
    - N modules discovered (A author-declared from <configs>, H heuristic)
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
  entry-point file paths (not contents), `git log` metadata, and
  **structural fields from root configuration files** (Step 4a-pre
  whitelist) are allowed inputs. Reading `*.ts` / `*.py` / `*.go` /
  `*.rs` / etc. source files for content remains forbidden.
- Read configuration file fields **outside the Step 4a-pre whitelist**
  (e.g., reading `package.json` `scripts` or `dependencies` to infer
  module purpose — that's analysis, not boundary metadata)
- Write content into entity stubs that the LLM cannot ground in
  observable facts (paths, commit messages) — don't fabricate WHY
- Touch `CLAUDE.md` content outside the `<!-- repo-wiki:start/end -->` block
- Use `[[wikilinks]]` — only standard markdown links
- Add naming suffixes like `Module` / `Service` — name comes from
  Entity Name Normalization Rule
- Run Phase 3 by default (only when user explicitly says full-history)
- **Truncate `log.md`** — log is append-only across all init runs
- **Overwrite ingest-accumulated entity sections** on re-run (Responsibility,
  Architecture, Gotchas, Dependencies that have been filled past `TODO`)
- **Re-process Phase 2 commits already covered** — read log.md last SHA
  on re-run and only handle new commits

ALWAYS:
- Apply Entity Name Normalization Rule for all entity filenames
- Make CLAUDE.md drop-in idempotent
- Bound Phase 2 with the 15 source page cap (Phase 1 + Phase 3 are
  uncapped because they have natural bounds: # of modules + # of eras)
- Record the last commit SHA in log.md (ingest depends on it; future
  init re-runs depend on it)
- Mark uncertain entity claims with TODO
- For Phase 1, build entity stub for **every** detected module (no threshold)
- **Re-run safety**: every step that touches an existing file must check
  whether the file exists and follow its documented merge / preserve /
  overwrite behavior (Step 1's prompt promises preservation; the rest of
  the workflow MUST honor that promise)

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
