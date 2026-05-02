---
name: ingest
description: |
  Use when: updating the knowledge base after code changes, capturing
  tribal knowledge, or importing external design documents. Triggers
  on "update knowledge", "ingest changes", "capture context",
  "remember that <X>", "import this doc", "/repo-wiki:ingest",
  "更新知識庫", "把這個記下來", "匯入這份設計".
  Do NOT trigger for: first-time setup (use /repo-wiki:init),
  answering questions (use /repo-wiki:query).
---

# Repo Wiki — Ingest Workflow

Polymorphic input dispatch into the knowledge base. The `.repo-wiki/`
directory is owned entirely by repo-wiki skills. Source layer (`src/**`)
is immutable — never modify code files.

## Prerequisite Check

Read `.repo-wiki/index.md`. If it does not exist:
> Knowledge base not initialized. Run `/repo-wiki:init` first.

Exit cleanly.

## Step 0: Mode Dispatch

Detect input mode from the user's invocation using this **exact dispatch
algorithm** — do not infer mode from heuristics outside this list:

### Dispatch algorithm

1. **No argument** → `git` mode
2. **Explicit import marker present** AND **valid path resolvable** → `doc-import` mode
3. **Otherwise** → `context` mode (default for any non-git arg, even if
   the arg mentions a path)

### Explicit import markers (case-insensitive)

doc-import mode requires one of these markers in the argument. Without
a marker, even an argument containing a real path is treated as context.

| Lang | Markers |
|---|---|
| EN | `import`, `import doc`, `import the doc at`, `from file`, `from this doc`, `read this doc`, `ingest doc`, `ingest the doc at`, `the doc at` |
| JP | `読み込んで`, `インポート`, `この doc を取り込んで`, `この設計書を` |
| ZH | `匯入`, `讀取`, `import`, `這個文件`, `這份設計`, `把這個文件` |

### Path extraction

When an import marker is present, extract the path:

1. Look for tokens after the marker (e.g., `import doc: <path>`)
2. Path token criteria: contains `/` OR ends in known doc extension
   (`.md`, `.txt`, `.rst`, `.adoc`, `.pdf`, `.org`)
3. Verify path exists on disk
4. If verification fails → ask user:
   > I see an import marker but couldn't find the file at `<extracted-path>`. Did you mean a different path?

### Examples

**doc-import mode** (marker present + valid path):
- `/repo-wiki:ingest "import design doc: docs/postgres.md"` → ✓
- `/repo-wiki:ingest "讀取 docs/auth-design.md 做為設計參考"` → ✓
- `/repo-wiki:ingest "import the doc at /Users/kouko/notes/foo.md"` → ✓

**context mode** (no marker, even when path mentioned):
- `/repo-wiki:ingest "AuthModule's gotcha is documented in /Users/x/notes/foo.md"` → context
- `/repo-wiki:ingest "remember that auth.ts has a comment saying X"` → context
- `/repo-wiki:ingest "the file src/auth/jwt.ts handles validation"` → context

**git mode**:
- `/repo-wiki:ingest` (no arg) → git

**Ambiguous → ask user**:
- Marker present but multiple candidate paths in arg → ask which one
- Marker present but no path token found → ask for path

### Why explicit-marker required

Without a marker, mentioning a path is not the same as importing it.
Defaulting to context mode for path-mentioning text avoids accidental
file reads. Users intending doc-import learn the marker once; users
intending context capture never trip into doc-import unintentionally.

## Step 1: Gather Input

### Git mode
- Read `.repo-wiki/log.md`, find the last `init` or `ingest:git` entry
- Extract the recorded `Last commit SHA`
- Run `git log <last_sha>..HEAD --oneline --stat`
- If empty: print `No new commits since last ingest` and exit
- If present: capture commits + paths for downstream processing

### Context mode
- The argument text IS the input payload
- If the note is short and ambiguous, optionally prompt the user for
  one round of expansion (which module / which decision / when)

### Doc-import mode
- Extract the file path from the argument
- Verify file exists; if not, ask for correct path
- Read the full file content as input payload

## Step 1.5: Entropy-Weighted Classification (Git Mode Only)

**When this step runs**: Git mode AND `commits_count >= 5`. Below 5
commits, skip classification — small ingests preserve v1.1 behavior
(one source page covering the batch).

**Why**: when 30 commits accumulate (e.g., user stops for a month),
producing one mega source page dilutes architectural signal. When 3
commits accumulate (typical post-feature ingest), one page is right.
The threshold makes classification volume-triggered, not always-on.

**Classification heuristics** (observable git metadata only — NO file
content reads):

| Weight | Signal (any one matches) | Source page treatment |
|---|---|---|
| **HIGH** | (a) touches root config from Step 4a-pre whitelist (`package.json`, `pnpm-workspace.yaml`, `go.mod`, `pyproject.toml`, `Cargo.toml`, `tsconfig.json`, etc.); (b) touches 3+ entities (cross-module); (c) touches any file listed in an entity's `Common Entry Points`; (d) subject matches `feat(...)` / `refactor(...)` / `arch:` OR body contains `BREAKING CHANGE`; (e) adds new top-level directory under source root; (f) tagged release commit | **Own source page** (one page per HIGH commit) |
| **MEDIUM** | (a) touches 2 entities; (b) subject `fix(...)` with body ≥ 1 line of explanation; (c) adds new file in existing module | **Batched** by file-overlap adjacency (Jaccard >50% on changed paths → same batch); each batch → one source page |
| **LOW** | (a) touches only test files (`**/test*/**`, `**/__tests__/**`, `*test*.{ts,tsx,py,go,rs,kt,rb,java}`); (b) touches only docs (`docs/**`, `*.md`); (c) subject contains `chore` / `style` / `format` / `lint` keyword; (d) single-file change touching neither config nor entry point | **Roll-up** (one combined source page per ingest); skipped (log-only) if <3 LOW commits in this batch |

**Source page budget**:

```
budget = min(15, ceil(commits_count / 5))
```

Examples:
- 5 commits → budget 1 page
- 15 commits → budget 3 pages
- 30 commits → budget 6 pages
- 100 commits → budget 20 → cap → budget 15 pages

**Allocation order** (when classified-page-count > budget):

1. Allocate every HIGH commit a page first
2. If budget remains, allocate MEDIUM batches
3. If budget remains, allocate LOW roll-up
4. If HIGH alone exceeds budget → keep most recent HIGH commits up to budget; remaining HIGH commits go into a single overflow source page noted as "additional architectural commits not individually documented; re-ingest with smaller windows for fuller coverage"

**Output**: pass `(commit, weight, source_page_assignment)` tuples to
Step 3.

## Step 2: Read Current Wiki State

Read `.repo-wiki/index.md` (catalog) and `.repo-wiki/overview.md`
(architecture summary) to ground the new input in existing structure.

## Step 3: Create Source Page

Filename and frontmatter vary by mode. Slug is derived from the
title — kebab-case, ASCII when possible.

**Git mode with classification** (Step 1.5 ran): create one source page
per assigned page from Step 1.5's allocation. HIGH commit pages use the
HIGH commit's subject as the title; MEDIUM batch pages derive title from
the batch's leading commit; LOW roll-up uses
`"Routine commits — <date range>"`. All variants share the same git-mode
frontmatter shape below; multi-commit pages list all commits in the
`commits:` array.

**Git mode without classification** (commits < 5): one source page
covering all commits in the batch — v1.1 behavior.

### Git mode → `.repo-wiki/sources/YYYY-MM-DD-<slug>.md`

```markdown
---
title: "<Short description of change>"
type: source
origin: git
date: YYYY-MM-DD
commits: ["<sha>", "<sha>"]
modules_affected: ["auth", "api"]
---

## What Changed
2-4 sentences synthesizing the batch.

## Key Decisions
- Decision and reason (extract from commit message bodies)
- Alternative considered, if any

## Connections
- [EntityName](../entities/EntityName.md) — how this change affected this module
- [ConceptName](../concepts/ConceptName.md) — pattern this implements/changes

## Contradictions / Breaks
- (Optional) Breaks [ConceptName](../concepts/ConceptName.md)'s assumption about X
```

### Context mode → `.repo-wiki/sources/YYYY-MM-DD-manual-<slug>.md`

```markdown
---
title: "<Topic of context capture>"
type: source
origin: manual
date: YYYY-MM-DD
captured_via: ingest-context-mode
---

## Context
<The user-supplied text, lightly cleaned but preserving wording>

## Why This Matters
<1-2 sentences: where this knowledge belongs in the codebase>

## Connections
- [EntityName](../entities/EntityName.md) — entity this context refines
- [ConceptName](../concepts/ConceptName.md) — pattern this context illuminates
```

### Doc-import mode → `.repo-wiki/sources/YYYY-MM-DD-doc-<slug>.md`

```markdown
---
title: "<Document title>"
type: source
origin: doc-import
date: YYYY-MM-DD
source_path: <path/to/imported/file>
source_mtime: <file mtime>
---

## Summary
2-4 sentences capturing the document's main thesis.

## Key Decisions / Claims
- Decisions or claims relevant to the codebase

## Connections
- [EntityName](../entities/EntityName.md) — entity affected by this doc
- [ConceptName](../concepts/ConceptName.md) — pattern this doc establishes
```

## Step 4: Update or Create Entity Pages

For each module/service the input touches:

- If entity page exists at the normalized name (see Naming below):
  update relevant sections (Gotchas, Dependencies, Recorded Decisions).
  Update `last_updated`, append the new source slug to `sources`
  frontmatter, and append a dated entry to "Recorded Decisions" if the
  input introduced one.
- If entity page does NOT exist: create one ONLY IF the module is
  meaningfully load-bearing across multiple sources. Use judgment, not
  a hard count — but err toward not creating skeletal pages from a
  single isolated change.

### Entity name derivation

Apply the **Entity Name Normalization Rule** in `.repo-wiki/SCHEMA.md`
exactly. Examples:
- `src/auth/` → `Auth.md`
- `src/auth/middleware/` → `AuthMiddleware.md`
- `lib/email/` → `Email.md`

This MUST match what `/repo-wiki:init` produces — using the same rule
guarantees no duplicate-named entities for the same module.

Before creating a new entity, check whether one with the normalized
name already exists. If yes → update that one, do NOT create a new
file. If two distinct paths would normalize to the same name
(collision), append a disambiguator from the stripped prefix:
`Auth` from `src/auth/`, `LibAuth` from `lib/auth/`.

### `paths:` maintenance (critical for query verification)

- **Git mode**: if commits in this batch added new files in this
  module's area, append the new path to `paths:`. If commits
  renamed/moved a tracked path (`git log --diff-filter=R --name-status`),
  update `paths:` accordingly. If a path was deleted, remove it from
  `paths:`.
- **Context / doc-import modes**: if user input mentions a specific
  src/ path that doesn't appear in `paths:`, ask:
  > Should I add `<path>` to `<EntityName>`'s paths?

  Add only on confirmation.

### Entity page format

```markdown
---
title: "<EntityName>"
type: entity
tags: []
sources: ["<source-slug-1>", "<source-slug-2>"]
last_updated: YYYY-MM-DD
paths:
  - src/auth/
  - src/middleware/auth.ts
---

## Responsibility
What this module does and — critically — what it does NOT do.
(Best-effort cache; src/ is authoritative — query verifies at key moments.)

## Architecture Snapshot
Key classes / services / entry points and their relationships.
Write WHY, not WHAT. Code speaks for itself; docs explain intent.

## Gotchas & Non-Obvious Design
- Why X is named Y (if confusing)
- Historical constraints that still apply
- Easy misuse patterns

## Common Entry Points
Functions / classes that an LLM will most often need to find.

## Dependencies
- Depends on: [OtherModule](OtherModule.md)
- Depended on by: [AnotherModule](AnotherModule.md)

## Recorded Decisions
- YYYY-MM-DD — Decision summary; see [source-slug](../sources/source-slug.md)
```

## Step 5: Update or Create Concept Pages

Same descriptive heuristic: if input introduces / modifies / violates a
pattern that is meaningfully cross-cutting, update or create the
concept page. Avoid creating concepts for one-off decisions.

```markdown
---
title: "<PatternName>"
type: concept
tags: []
sources: ["<source-slug>"]
last_updated: YYYY-MM-DD
---

## Summary
One paragraph: what this pattern/decision is and why it exists.

## When to Apply
- Apply when: ...
- Do NOT apply when: ...

## Canonical Example
[EntityName](../entities/EntityName.md) — implements this pattern in X way.

## Known Violations / Exceptions
- [EntityName](../entities/EntityName.md) violates this because of legacy constraint Y
```

## Step 6: Update Index, Log, Overview

### index.md

Append any newly created pages under the right section.

### log.md

Append a new entry. Mode is encoded in the operation name:

```
## [YYYY-MM-DD] ingest:git | <description>
- Commits: <sha range> (<count> total)
- Classification: <H> HIGH / <M> MEDIUM / <L> LOW (skipped log-only: <K>)
  (omit line if commits < 5 — classification did not run)
- Last commit SHA: <new HEAD sha>   ← critical for next ingest
- Sources created: <list of slugs> (budget: <used>/<budget>)
- Entities updated: <list>
- Concepts updated: <list>
```

```
## [YYYY-MM-DD] ingest:manual | <topic>
- Source: .repo-wiki/sources/<slug>.md
- Entities updated: <list>
- Concepts updated: <list>
```

```
## [YYYY-MM-DD] ingest:doc-import | <doc title>
- Imported from: <source_path>
- Source: .repo-wiki/sources/<slug>.md
- Entities updated: <list>
- Concepts updated: <list>
```

### overview.md

Update only if the input changed something architecture-level (new
module added, major refactor, removed subsystem). Routine ingests do
NOT touch overview.md.

## Step 7: Validation + Summary

Before finishing:
- Verify every link added today points to a page listed in `index.md`
- Print summary:

```
✓ Ingest (mode: <git|manual|doc-import>) complete.
  - Source page: <path>
  - Entities updated: <list>
  - Concepts updated: <list>
  - Overview updated: <yes|no>
```

## Rules

NEVER:
- Modify any file under `src/` or anywhere outside `.repo-wiki/`
- Delete pages under `.repo-wiki/` (only update or append)
- Auto-ingest without explicit user invocation
- Copy-paste code into knowledge pages (describe intent, not implementation)
- Use `[[wikilinks]]` — only standard markdown links: `[Name](path)`
- Forget to record the new HEAD SHA in `log.md` (git mode) — it breaks
  the next ingest's idempotency
- Add naming suffixes like `Module` / `Service` — apply Entity Name
  Normalization Rule strictly

ALWAYS:
- Write WHY not WHAT (code speaks WHAT for itself)
- Update `log.md` on every operation, with mode-specific entry format
- Keep entity pages module-bounded (one module = one entity page)
- Use descriptive judgment for page creation, not numeric thresholds
  (the entropy classification in Step 1.5 is a budget allocator, not a
  page-content quality gate — page content still requires judgment)
- Maintain `paths:` frontmatter on entity updates (verification depends on it)
- Run Step 1.5 classification when git-mode commit count ≥ 5; skip it
  for smaller ingests (preserves single-page behavior for typical
  post-feature use)
- Respect the source-page budget `min(15, ceil(commits/5))` — overflow
  HIGH commits go into a noted single page, never silently dropped
