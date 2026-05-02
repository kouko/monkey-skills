---
name: init
description: |
  Use when: setting up repo-wiki for the first time in a repository,
  or re-seeding the knowledge base from scratch. Triggers on
  "init repo-wiki", "set up knowledge base", "seed from git history",
  "/repo-wiki:init", "初始化 repo-wiki", "建立知識庫".
  Do NOT trigger for: incremental updates after changes (use
  /repo-wiki:ingest), answering questions (use /repo-wiki:query).
---

# Repo Wiki — Init Workflow

One-time bootstrap that seeds the knowledge base from the last 90 days
of git history. After init, use `/repo-wiki:ingest` for incremental updates.

The `.repo-wiki/` directory is owned entirely by repo-wiki skills.
Source layer (`src/**`) is immutable — never modify code files.

## Step 1: Sanity Check

```bash
test -d .git || { echo "Not a git repo. Aborting."; exit 1; }
```

If `.repo-wiki/` already exists, ask the user:

> `.repo-wiki/` already exists. Re-running init will:
>  - Add a new init entry to log.md
>  - Append additional source pages from the scan window
>  - Refresh entity stubs (overwriting earlier auto-generated stubs)
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
- `templates/SCHEMA.md` → `.repo-wiki/SCHEMA.md`
- `templates/index.md` → `.repo-wiki/index.md`
- `templates/log.md` → `.repo-wiki/log.md`
- `templates/overview.md` → `.repo-wiki/overview.md`

(Resolve template path relative to this SKILL.md location:
`../../templates/<file>.md`.)

## Step 3: CLAUDE.md Drop-in

Read or create `CLAUDE.md` in the repo root. The drop-in block (also
available as `templates/claude-md-snippet.md`):

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

## Step 4: Bounded Git Scan

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

Capture for each commit:
- SHA, ISO date, author, subject (the WHY signal)
- Body (additional WHY)
- Changed paths (with insertions/deletions)

If git log is empty (brand-new repo): skip Steps 5-7, write a log entry
noting "no history to seed", and finish.

## Step 5: Logical Batching

### Initial grouping
Group commits into batches by:
- **Branch boundary**: merge commits act as separators (the merge
  commit itself goes into the batch with the larger side)
- **Time gap**: >3 days idle between consecutive commits = new batch
- **File overlap**: consecutive commits sharing >50% of changed paths
  belong to the same batch (Jaccard similarity on path sets)

### Hard cap: 15 source pages per init

Init MUST NOT produce more than 15 source pages in a single run. If
initial grouping yields >15 batches, downsample in this order:

1. Widen time gap: try 7-day threshold instead of 3-day. Re-group.
2. Widen further: try 14-day threshold. Re-group.
3. Hard truncate: if still >15 after 14-day threshold, keep the 15
   batches with the most total lines changed (insertions+deletions).
   Other batches' commits are summarized in a single
   `YYYY-MM-DD-init-overflow.md` source page noting:
   > "<N> additional batches were observed but not individually
   > documented; re-run /repo-wiki:ingest after browsing to capture
   > specific decisions."

### Edge cases
- **Empty git history**: skip Steps 5-7 entirely; log "no history to seed"
- **Only one commit**: produce exactly one source page
- **Only merge commits** (rare): treat the entire merge graph as one batch
- **Single-batch widen**: if all commits fall into one batch even with
  3-day threshold, accept the single batch — don't artificially split

### Source page format

For each batch, write `.repo-wiki/sources/YYYY-MM-DD-<slug>.md`:

```markdown
---
title: "<Short description, derived from leading commit subject>"
type: source
origin: git
date: <date of latest commit in batch>
commits: ["<sha>", "<sha>", ...]
modules_affected: ["<top-level-path>", ...]
---

## What Changed
2-4 sentences synthesizing the batch (from commit subjects + bodies).

## Key Decisions
- Decision and reason (extract from commit message bodies; if absent,
  state "WHY not captured in commit messages — consider /repo-wiki:ingest
  with context to add")

## Connections
- [EntityName](../entities/EntityName.md) — how this batch affected this module

## Notes
- Generated by /repo-wiki:init seed pass; refine via future /repo-wiki:ingest
```

## Step 6: Entity Stub Derivation

Count how many batches touched each top-level module. For modules
appearing in 3+ batches, create an entity stub.

**Critical**: every entity MUST have `paths:` frontmatter — query uses
this for verification. Populate from git stat: list the top 1-3
most-touched paths for this module.

**Naming**: apply the **Entity Name Normalization Rule** from
`.repo-wiki/SCHEMA.md` exactly. Examples:
- `src/auth/` → `Auth.md`
- `src/auth/middleware/` → `AuthMiddleware.md`
- `src/utils/jwt-handler/` → `UtilsJwtHandler.md`
- `lib/email/` → `Email.md`

Init never adds suffixes like `Module` / `Service` — name is
path-derived so init and ingest produce the same name for the same
path. Detect collisions (different paths normalizing to same name) and
add a prefix-derived disambiguator (e.g., `Auth` from `src/auth/`,
`LibAuth` from `lib/auth/`).

### Entity stub format

```markdown
---
title: "<EntityName>"
type: entity
tags: []
sources: ["<source-slug-1>", "<source-slug-2>", ...]
last_updated: <today>
paths:
  - <most-touched-path-1>
  - <most-touched-path-2>
---

## Responsibility
<Derived from path name + commit subjects. Mark uncertain claims with TODO.
Note: this is a best-effort cache. src/ is authoritative for current
behavior — query verifies at key moments per Decision 13.>

## Architecture Snapshot
TODO — refine via /repo-wiki:ingest after working with this module.

## Gotchas & Non-Obvious Design
TODO — these surface during real work; capture via
/repo-wiki:ingest "<observation>".

## Common Entry Points
<List 1-3 most-touched files in this module from git stat output.>

## Dependencies
TODO

## Related Decisions
<Link to source pages where this module was central.>
```

Stubs are intentionally skeletal — they are seeds, not complete entities.
The next `/repo-wiki:ingest` cycle (or context-mode capture) fills them
in. The `paths:` field, however, must be populated immediately —
without it, query verification falls back to slow grep-based discovery.

## Step 7: Overview Synthesis

Write `.repo-wiki/overview.md`:

```markdown
---
title: Codebase Overview
type: overview
last_updated: <today>
seeded_from: "git log --since='90 days ago' (N commits)"
---

# Codebase Overview

## Repository
<One paragraph: pull from README.md if present; otherwise describe from
top-level directory structure.>

## Active Modules (last 90 days)
<List entity stubs created in Step 6, with one-line descriptions.>

## Recent Themes
<2-4 themes synthesized from source pages — what kinds of changes have
been happening.>

## What Lives Where
- .repo-wiki/sources/ — change history (with WHY)
- .repo-wiki/entities/ — module knowledge (currently mostly stubs)
- .repo-wiki/concepts/ — patterns / ADRs (empty after init; grows via ingest)
- .repo-wiki/syntheses/ — saved query answers (empty after init)
```

## Step 8: Index + Log

Update `.repo-wiki/index.md` to list all created pages under their
respective sections (Sources / Entities / Concepts / Syntheses).

Append to `.repo-wiki/log.md`:

```
## [<date>] init | seeded from last 90d
- Window: 90 days, max 50 commits (override: <if user customized>)
- Last commit SHA: <HEAD sha at scan time>
- Source pages created: N
- Entity stubs created: M
- Overview written: yes
- CLAUDE.md drop-in: <created | appended | replaced>
```

**Recording the "Last commit SHA" is critical** — `/repo-wiki:ingest`
uses this to know where to start incrementally.

## Step 9: Summary Report

Print to user:

```
✓ Knowledge base initialized at .repo-wiki/

  Created:
    - N source pages (.repo-wiki/sources/)
    - M entity stubs (.repo-wiki/entities/)
    - overview.md, index.md, log.md, SCHEMA.md
    - CLAUDE.md drop-in (<created/appended/replaced>)

  Next steps:
    1. Skim .repo-wiki/overview.md and entity stubs
    2. Capture tribal knowledge:
       /repo-wiki:ingest "<something WHY-related>"
    3. After your next feature, run /repo-wiki:ingest

  Entity stubs are skeletal — they fill in via real work, not by guessing.
```

## Rules

NEVER:
- Modify any file under `src/` or anywhere outside `.repo-wiki/` and `CLAUDE.md`
- Write content into entity stubs that the LLM cannot ground in commit
  messages or path structure (don't fabricate WHY)
- Touch `CLAUDE.md` content outside the `<!-- repo-wiki:start/end -->` block
- Use `[[wikilinks]]` — only standard markdown links
- Add naming suffixes like `Module` / `Service` — name comes from
  Entity Name Normalization Rule

ALWAYS:
- Bound the scan (90d / 50 commits default; respect user overrides)
- Mark uncertain entity claims with TODO
- Record the last commit SHA in log.md (ingest depends on it)
- Make CLAUDE.md drop-in idempotent
- Apply Entity Name Normalization Rule for all entity filenames
