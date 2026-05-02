# Repo Wiki Schema (v1.0 — frozen)

This schema is **frozen for the v1.x line**. Page types, frontmatter
shape, and naming conventions will not change within v1.x patches; only
wording clarifications are allowed. Major schema changes ship in v2.0
with a migration script.

## Architecture

This knowledge base has three layers:

- **src/*** — Source layer. Immutable. Never modified by skills.
  **Always the authoritative source of current behavior.**
- **.repo-wiki/** — Wiki layer. Owned entirely by AI skills.
  Records past decisions and acts as a *best-effort implementation cache*.
  Humans read via `/repo-wiki:query`. Do not edit directly.
  (Enforced by repo-root CLAUDE.md drop-in.)
- **.repo-wiki/SCHEMA.md** — Schema layer. Defines structure and rules.

### Positioning Statement

`.repo-wiki/` describes implementation, but does NOT claim authority over
current behavior. When a query asks about current state (vs past
decisions), `/repo-wiki:query` verifies key claims against `src/` via the
verification triggers (T1–T7) in the query workflow. See SKILL.md for
details.

## Directory Layout

```
.repo-wiki/
  SCHEMA.md      # This file
  index.md       # Master catalog of all pages
  log.md         # Append-only operation log
  overview.md    # Living synthesis of the full codebase
  sources/       # One page per significant change OR per context capture
  entities/      # One page per module / service / subsystem
  concepts/      # One page per pattern / ADR / convention
  syntheses/     # Saved query answers
```

## Page Types

### source
File: `.repo-wiki/sources/<filename>.md`

Filename convention varies by `origin`:
- `origin: git` (Phase 2 batch) → `YYYY-MM-DD-<slug>.md`
- `origin: git` (Phase 3 era) → `era-YYYY-HX.md`
- `origin: manual` → `YYYY-MM-DD-manual-<slug>.md`
- `origin: doc-import` → `YYYY-MM-DD-doc-<slug>.md`

Create when: a meaningful change lands (git mode), user supplies tribal
knowledge (manual mode), or user imports an external design doc
(doc-import mode). Phase 3 era pages are produced only when init runs
in `full-history` mode.

Frontmatter:
- `title`, `type: source`, `origin: git | manual | doc-import`, `date`
- Git Phase 2 mode: `commits: [...]`, `modules_affected: [...]`
- Git Phase 3 mode (era): `era: YYYY-HX`, `commit_count: N`,
  `major_commits: [...]`
- Doc-import mode: `source_path`, `source_mtime`

Contents: what changed/known + key decisions + connections to entities/concepts.

### entity
File: `.repo-wiki/entities/<EntityName>.md` (PascalCase)

Create when: **init creates one for every detected module** in src/
(no threshold — see Decision 9 v1.1 update). ingest creates new ones
for emergent modules outside the original src/ scope.

Required frontmatter:
- `title`, `type: entity`, `last_updated`
- `paths: [...]` — list of directories or files comprising this entity.
  Used by `/repo-wiki:query` for verification (Decision 13). init
  populates from `git ls-files` (current src/ tree). ingest updates
  when commits move files.

Required body sections:
- `## Responsibility` — what this module does and what it does NOT do.
  After init, this is `TODO — fill via /repo-wiki:ingest "<observation>"`
  (init does NOT fabricate responsibility from path names alone).
- `## Common Entry Points` — list of entry-point file paths
  (`index.*`, `__init__.py`, `main.go`, etc.) detected by init.
  Path-only; init does NOT read file contents.
- `## Recorded Decisions` — chronological list of decisions affecting
  this entity. Init seeds with last 5 commits touching the module's
  paths. Subsequent ingest appends.
- `## Architecture Snapshot` — entry points, key classes, relationships.
  TODO after init; fills via ingest.
- `## Gotchas & Non-Obvious Design` — historical constraints, easy
  misuse patterns. TODO after init; fills via ingest.
- `## Dependencies` — what this depends on, what depends on it. TODO
  after init; fills via ingest.

Implementation descriptions in any section are *best-effort cache* —
`src/` remains authoritative. Query verifies current-behavior claims at
key moments (verification triggers T1–T7 in query SKILL.md).

### Entity stub format (init Phase 1 output)

```markdown
---
title: "<EntityName>"
type: entity
last_updated: <today>
paths:
  - <path1>
  - <path2>
sources: []
---

## Responsibility
TODO — fill via /repo-wiki:ingest "<observation>".

(Source layer is `src/`; this entity is a knowledge cache, not authority.)

## Common Entry Points
- <entry-point-path-1>
- <entry-point-path-2>

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

### concept
File: `.repo-wiki/concepts/<ConceptName>.md` (PascalCase)

Create when: the pattern is meaningfully cross-cutting. Same descriptive
heuristic as entity — avoid one-off concept pages.

Contents: summary (what + why), when to apply / when not to, canonical
example, known violations.

### synthesis
File: `.repo-wiki/syntheses/<question-slug>.md`

Create when: user asks `/repo-wiki:query` to save the answer for future reuse.

Contents: original question + full answer with citations + verification
status preserved from the original query.

## Naming Conventions

| Page type           | Format                      | Example                                         |
|---------------------|-----------------------------|-------------------------------------------------|
| entity              | PascalCase.md               | Auth.md, AuthMiddleware.md, PaymentService.md   |
| concept             | PascalCase.md               | OptimisticLocking.md, EventSourcing.md          |
| source (git, Phase 2) | YYYY-MM-DD-kebab.md       | 2026-05-02-add-jwt-auth.md                      |
| source (git, Phase 3 era) | era-YYYY-HX.md        | era-2024-H2.md                                  |
| source (manual)     | YYYY-MM-DD-manual-kebab.md  | 2026-05-02-manual-auth-naming.md                |
| source (doc)        | YYYY-MM-DD-doc-kebab.md     | 2026-05-02-doc-postgres-decision.md             |
| synthesis           | kebab-slug.md               | how-does-auth-flow-work.md                      |

### Entity Name Normalization Rule (shared between init and ingest)

Entity names MUST be derived from `paths:` using this exact algorithm so
that init and ingest never produce two pages for the same module under
different names.

**Algorithm**:

1. Take the entity's primary path (first entry in `paths:`)
2. Strip these leading prefixes if present (in order of specificity):
   - `apps/<name>/src/`
   - `packages/<name>/src/`
   - `src/`
   - `lib/`
   - `app/`
3. Strip trailing `/` and trailing file extension (`.ts`, `.js`, `.py`, `.go`, `.rs`, `.tsx`, `.jsx`, etc.)
4. Split remaining path on `/`, `-`, and `_`
5. Capitalize each segment (PascalCase), no separator
6. The result is the entity name (and the filename: `<name>.md`)

**Examples**:

| Input path                            | Stripped                | Segments                  | Entity name                |
|---------------------------------------|-------------------------|---------------------------|----------------------------|
| `src/auth/`                           | `auth`                  | [auth]                    | `Auth`                     |
| `src/api/`                            | `api`                   | [api]                     | `Api`                      |
| `src/auth/middleware/`                | `auth/middleware`       | [auth, middleware]        | `AuthMiddleware`           |
| `src/utils/jwt-handler/`              | `utils/jwt-handler`     | [utils, jwt, handler]     | `UtilsJwtHandler`          |
| `src/auth/jwt.ts`                     | `auth/jwt`              | [auth, jwt]               | `AuthJwt`                  |
| `lib/email/`                          | `email`                 | [email]                   | `Email`                    |
| `packages/core/src/queue/`            | `queue`                 | [queue]                   | `Queue`                    |
| `apps/web/src/components/Button.tsx`  | `components/Button`     | [components, Button]      | `ComponentsButton`         |
| `services/payment/handler.go`         | `services/payment/handler` | [services, payment, handler] | `ServicesPaymentHandler` |

**Rules**:
- Do NOT add suffixes like `Module`, `Service` — the path itself is the
  identity. (PaymentService entity comes from `src/payment-service/` or
  `src/services/payment/`, not from adding a suffix.)
- If two entities would collapse to the same name (e.g., both `src/auth/`
  and `lib/auth/` produce `Auth`), the second one created should append a
  disambiguator from the original prefix: `Auth` and `LibAuth`. ingest
  should detect collision before writing.
- Single-letter or numeric-only segments are kept as-is: `src/v2/api/` →
  `V2Api`.

## Linking Convention

Use **standard markdown links** — never `[[wikilinks]]`.

- Same directory: `[Name](OtherEntity.md)`
- Cross directory: `[Name](../entities/AuthModule.md)`
- Link text: page title (no path, no `.md` suffix)

Why: `.repo-wiki/` is committed into the repo and read by various tools
(AI agents, IDEs, GitHub UI) — none of which render `[[X]]`. Standard
links work everywhere.

All links must point to pages listed in `.repo-wiki/index.md`.

## index.md Format

```markdown
# .repo-wiki/ Index

## Overview
- [Overview](overview.md) — living codebase synthesis

## Sources (recent → old)
- [YYYY-MM-DD slug](sources/slug.md) — one-line summary

## Entities
- [EntityName](entities/EntityName.md) — one-line description

## Concepts
- [ConceptName](concepts/ConceptName.md) — one-line description

## Syntheses
- [Question slug](syntheses/slug.md) — what question it answers
```

## log.md Format

Each entry: `## [YYYY-MM-DD] <operation>:<mode> | <title>`

Operations / modes:
- `init` (default mode — Phase 1 + Phase 2)
- `init:full-history` — Phase 3 era backfill (only when user runs
  `/repo-wiki:init full-history`)
- `ingest:git` — incremental from git diff
- `ingest:manual` — context capture from user text
- `ingest:doc-import` — external document import
- `query` — read operation

Grep-friendly:
```bash
grep "^## \[" .repo-wiki/log.md | tail -10        # recent activity
grep "ingest:git" .repo-wiki/log.md               # only code changes
grep "ingest:manual" .repo-wiki/log.md            # only context captures
```

The git-mode log entry MUST record the new HEAD SHA — it's the anchor
the next `/repo-wiki:ingest` uses to find new commits.

## Verification Triggers (in /repo-wiki:query)

`.repo-wiki/` is a *best-effort cache* of implementation, not the
authority. Query reads `src/` to verify current-behavior claims when any
of these triggers fires:

| ID | Trigger                                                    | Action                                    |
|----|------------------------------------------------------------|-------------------------------------------|
| T1 | Loaded page `last_updated > 60d`                           | Read entity's `paths:` to spot-check      |
| T2 | Question contains "currently" / "now" / "still" / 「現在」 / 「目前」 | Spot-check current-state claims     |
| T3 | Answer will inform new code being written                  | Verify entry-point files                  |
| T4 | Loaded source page has TODO / "subject to change"          | Read corresponding `src/`                 |
| T5 | Multiple loaded pages contradict each other                | Read `src/` to arbitrate                  |
| T6 | Question is purely about past decisions                    | **No verification** (trust `.repo-wiki/`) |
| T7 | User explicitly requests verification                      | Verify every claim                        |

When any trigger fires, query presents answer in segmented format:
- **Verified Claims** (against `src/`)
- **Unverified Claims** (from `.repo-wiki/` cache)
- **Discrepancies Found** (with `/repo-wiki:ingest` suggestion)

Detection priority: T7 > T6 > {T1, T2, T3, T4, T5}.
Full detection rules in `skills/query/SKILL.md`.

## Health Checks

Routine health checks (broken links, stale entities with git
cross-check, orphan concepts, modules missing entity pages) ship as
`/repo-wiki:lint` in **v2** — out of scope for v1. The query skill does a
basic stale warning based on `last_updated > 60 days` (trigger T1).

## What .repo-wiki/ Does NOT Contain

- Code (describe intent and decisions, not implementation)
- Verbatim commit messages (those live in git log; sources/ summarize them)
- API documentation (belongs in code comments / OpenAPI)
- Anything that changes on every PR (keep knowledge evergreen)
- Personal notes / TODOs (use a separate notes file outside .repo-wiki/)

## Schema Evolution

This schema is frozen until v2.0. Within v1.x:
- Wording in this file may be clarified
- New examples may be added
- BUT: page types, frontmatter shape, naming, and linking conventions
  do not change

When v2.0 lands, the plugin will ship a migration script. v1 users do
not need to plan for migrations within v1.x.
