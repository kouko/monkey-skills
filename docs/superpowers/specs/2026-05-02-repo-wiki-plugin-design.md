# repo-wiki Plugin Design

**Date**: 2026-05-02
**Status**: Draft (decisions locked, ready for implementation)
**Author**: kouko + Claude Sonnet 4.5
**Plan reference**: [../plans/2026-05-02-repo-wiki-plugin-v1.0.0.md](../plans/2026-05-02-repo-wiki-plugin-v1.0.0.md)

---

## Context & Motivation

### The Problem

AI coding tools (Claude Code, Cursor, Copilot) understand a codebase only within a single session. Once the session ends, all that understanding is lost — the next session starts from zero again.

Existing solutions fall into two categories, each with fundamental limitations:

| Category | Examples | Problem |
|---|---|---|
| SaaS semantic search | Greptile, DeepWiki, Cursor @Codebase | Code leaves the machine; no offline; knowledge not in repo |
| Flat Markdown context | CLAUDE.md, AGENTS.md, Memory Bank | Full-text injection; token cost explodes with repo size; no persistent synthesis |

The gap: no tool provides **persistent, repo-committed, synthesized knowledge** that an AI agent can query without full-text injection — and without a SaaS dependency.

### Research Findings (2026-04-30)

A deep-mode research session ([26 primary sources](https://github.com/kouko/kouko-obsidian-vault)) surfaced:

1. Industry has **fragments, not a complete solution** — Repowise (closest, but missing multi-person workflow), Code-Index-MCP (query only), RepoAgent (auto-update pipeline only)
2. **LLM Wiki Pattern** (Karpathy 2024) is the best conceptual fit: synthesize at ingest time, not query time
3. Existing SKILL.md implementations of this pattern ([llmrix/llm-wiki-skill](https://github.com/llmrix/llm-wiki-skill), [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent)) handle general documents — **none handle code repos + git changes**
4. Multi-person collaboration requires: CI-proposes, humans-approve (never auto-merge knowledge)
5. Tool diversity in teams requires vendor-neutral distribution (Ruler pattern)

### Key Insight

The `raw/ → wiki/` pattern from llm-wiki-agent maps cleanly to code repos:

```
raw/           (general wiki)    →   src/**          (code repo)
wiki/          (general wiki)    →   .repo-wiki/      (code repo)
/wiki-ingest   (general wiki)    →   /repo-wiki:ingest (code repo)
/wiki-query    (general wiki)    →   /repo-wiki:query  (code repo)
```

The only adaptation needed: ingest reads `git log` + `git diff` instead of `raw/` documents — and ingest can also accept ad-hoc context arguments to capture knowledge that lives outside git (see Decision 8).

---

## Architecture

### Distribution: monkey-skills sub-plugin

`repo-wiki` ships as the 10th sibling plugin inside the [monkey-skills](https://github.com/kouko/monkey-skills) marketplace, alongside [dev-workflow](../../../dev-workflow/), [obsidian](../../../obsidian/), etc. Users install it via the existing monkey-skills marketplace; no separate GitHub repo or marketplace submission is required for v1.0.0. (Standalone repo graduation is a v2 consideration.)

### Three-Layer Structure

```
Layer 1 — Sources (immutable)
  src/**           Code files — never modified by skills
  git log/diff     Change history — read-only input to ingest
  external docs    Optional input via /repo-wiki:ingest <path-or-text>

Layer 2 — Wiki (AI-owned)
  .repo-wiki/       Entirely owned by repo-wiki skills
                   Humans read via /repo-wiki:query
                   Humans do NOT directly edit (enforced via CLAUDE.md drop-in)

Layer 3 — Schema
  .repo-wiki/SCHEMA.md    Structure rules (frozen until v2.0)
  CLAUDE.md drop-in      Repo-level rule reminding any AI session
                         not to edit .repo-wiki/ directly
```

### Plugin File Structure

```
monkey-skills/
└── repo-wiki/
    ├── .claude-plugin/
    │   └── plugin.json              # name, version, description, keywords
    ├── skills/
    │   ├── init/
    │   │   ├── SKILL.md             # /repo-wiki:init  (one-time seed)
    │   │   └── assets/              # init-owned bundled resources
    │   │       ├── SCHEMA.md        # .repo-wiki/SCHEMA.md starter
    │   │       ├── index.md         # .repo-wiki/index.md skeleton
    │   │       ├── log.md           # .repo-wiki/log.md skeleton
    │   │       ├── overview.md      # .repo-wiki/overview.md skeleton
    │   │       └── claude-md-snippet.md  # CLAUDE.md drop-in for init
    │   ├── ingest/
    │   │   └── SKILL.md             # /repo-wiki:ingest (incremental)
    │   └── query/
    │       └── SKILL.md             # /repo-wiki:query  (read)
    ├── README.md
    ├── README.ja.md
    ├── README.zh-TW.md
    └── CHANGELOG.md
```

### .repo-wiki/ Directory (installed in target repos)

```
.repo-wiki/
  SCHEMA.md        Rules and conventions (from plugin assets/)
  index.md         Master catalog — updated on every ingest
  log.md           Append-only operation record
  overview.md      Living synthesis of the full codebase
  sources/         One page per significant commit batch OR per manual context capture
  entities/        One page per module / service / subsystem
  concepts/        One page per pattern / ADR / convention
  syntheses/       Saved query answers
```

---

## Page Types

### source — change or context summary
- File: `.repo-wiki/sources/YYYY-MM-DD-<slug>.md` (git mode) or `YYYY-MM-DD-manual-<slug>.md` / `YYYY-MM-DD-doc-<slug>.md` (other modes)
- Created when: a meaningful feature/refactor/architectural change lands (git mode), or user supplies ad-hoc context (context/doc-import modes)
- Contents: **what changed/known** + **why decided**
- Frontmatter `origin` field distinguishes the three input modes (see Decision 8)
- Threshold: one source page per logical unit (not per commit)

### entity — module / service knowledge
- File: `.repo-wiki/entities/<ModuleName>.md` (PascalCase)
- Created when: a module is meaningfully load-bearing across multiple sources (descriptive heuristic, see Decision 9)
- Required frontmatter: `paths: [...]` listing directories/files comprising the entity (verification target — see Decision 13)
- Contents: responsibility boundary, gotchas, non-obvious design, common entry points, dependencies, recorded decisions
- **Rule**: write WHY first; WHAT is allowed as best-effort cache, but src/ is authoritative and query verifies at key moments (Decision 13)

### concept — pattern / ADR
- File: `.repo-wiki/concepts/<ConceptName>.md` (PascalCase)
- Created when: pattern is meaningfully cross-cutting across the codebase (descriptive heuristic)
- Contents: summary, when to apply, canonical example, known violations

### synthesis — saved query answers
- File: `.repo-wiki/syntheses/<question-slug>.md`
- Created when: user asks to save a query answer for future reuse
- Value: same question answered faster next time — no re-analysis needed

---

## Skill Surface

Three skills, each with a single primary responsibility:

| Skill | When | Primary input | Frequency |
|---|---|---|---|
| `/repo-wiki:init` | Once per repo | Last 90 days of git history (bounded) | One-time seed; rarely re-run |
| `/repo-wiki:ingest` | After meaningful changes OR to capture context | Git diff since last ingest, OR text arg, OR file path | Often (per feature / per discussion) |
| `/repo-wiki:query` | Whenever asking about codebase | .repo-wiki/index.md + relevant pages | Frequent |

Full SKILL.md content for each:
- `init` ([design](../research/2026-05-02-repo-wiki-skill-init.md)): scaffold .repo-wiki/ + CLAUDE.md drop-in + bounded git-history seed of the last ~90 days
- `ingest` ([design](../research/2026-05-02-repo-wiki-skill-ingest.md)): polymorphic input dispatch (git / context / doc-import) → write/update sources, entities, concepts
- `query` ([design](../research/2026-05-02-repo-wiki-skill-query.md)): read index → load relevant pages → synthesize answer with citations → offer to save synthesis
- SCHEMA.md template ([design](../research/2026-05-02-repo-wiki-schema-design.md)): three-layer architecture, page-type rules, naming conventions
- Project overview ([notes](../research/2026-05-02-repo-wiki-project-overview.md)): philosophy, tool comparison, daily workflow

Behavioral rules shared by all skills:

```
NEVER modify src/**
NEVER delete .repo-wiki/ pages (only update or append)
ALWAYS update .repo-wiki/log.md on every operation
ALWAYS cite with standard markdown links (see Decision 7)
```

---

## Design Decisions

### Decision 1: WHY over WHAT (and src/ remains the source of truth)

Entity pages explain **why** a module is designed this way and provide pointers into where it lives. They may also include implementation description (Responsibility, Architecture Snapshot, Dependencies) as a *best-effort cache*, but those descriptions are NEVER authoritative — `src/**` is the source of truth for current behavior. See Decision 13 for the verification mechanism that operationalizes this fence.

*Rejected alternative*: auto-generating docstrings or API summaries — those duplicate information already in code AND make .repo-wiki/ falsely look authoritative.

### Decision 2: Gap as feedback

When `/repo-wiki:query` cannot find an answer, it must say so explicitly. This is a feature, not a failure. An explicit gap tells the engineer to run `/repo-wiki:ingest` for that module next time.

*Rejected alternative*: falling back to reading `src/` directly without flagging — produces an answer but hides the gap from the ingest cycle.

### Decision 3: Synthesize at ingest time, not query time

Knowledge is extracted and synthesized when ingest runs. Query only reads and presents — it does not re-analyze the codebase on demand. This is the core Karpathy LLM Wiki insight applied to code.

*Rejected alternative*: RAG / semantic search on demand (Code-Index-MCP, Greptile) — produces answers but cannot capture WHY or tribal knowledge.

### Decision 4: .repo-wiki/ is AI-owned

Humans do not directly edit files in `.repo-wiki/`. All changes go through `/repo-wiki:ingest` or `/repo-wiki:init`. This prevents knowledge drift from human edits that bypass the structured workflow.

*Enforcement*: `/repo-wiki:init` writes a drop-in block into the repo's root `CLAUDE.md` (idempotent via `<!-- repo-wiki:start --> ... <!-- repo-wiki:end -->` markers) so any future Claude session sees the rule even when no skill is explicitly invoked. See Decision 5.

*Analogy*: same rule as the Obsidian `wiki/` layer in the Karpathy wiki pattern.

### Decision 5: CLAUDE.md drop-in enforces the AI-owned rule

The ".repo-wiki/ is AI-owned" rule cannot live only inside SKILL.md, because SKILL.md is loaded only when the skill is explicitly invoked. To prevent silent edits during normal Claude sessions, `/repo-wiki:init` injects a ~12-line block into the repo's root `CLAUDE.md`:

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

The markers make re-running init idempotent (replace the block, don't append). If CLAUDE.md doesn't exist, init creates it.

*Rejected alternatives*:
- `.repo-wiki/CLAUDE.md` — Claude Code only auto-injects the cwd-level CLAUDE.md, so subdirectory ones don't reach the most common edit scenarios.
- `SCHEMA.md` opening rule — Claude doesn't read SCHEMA.md before editing .repo-wiki/ files.
- Doing nothing — Decision 4 becomes empty rhetoric.

### Decision 6: v1 ships single-developer; multi-person CI is v2

The original research surfaced "AI proposes, humans approve" as the right pattern for multi-person teams. v1.0.0 deliberately scopes to single-developer use and does NOT ship a CI workflow. Multi-person concerns (PR-based knowledge proposals, conflict resolution, accountability) move to v2 backlog.

*Why scope this way*: shipping a multi-person workflow without first validating the single-developer loop risks designing the wrong CI integration. v1 establishes the core ingest/query value; v2 builds on validated foundations.

### Decision 7: Standard markdown links, not wikilinks

.repo-wiki/ pages reference each other with standard markdown links (`[AuthModule](entities/AuthModule.md)`), not Obsidian wikilinks (`[[AuthModule]]`).

*Why*: .repo-wiki/ is committed into the repo and read on GitHub, in IDEs, and in terminal markdown viewers — none of which render `[[X]]`. Standard links work everywhere. Losing Obsidian's graph view is acceptable; v2 may add a `/repo-wiki:graph` skill that builds a graph from standard markdown links.

*Convention*:
- Same-directory: `[Name](OtherEntity.md)`
- Cross-directory: `[Name](../entities/AuthModule.md)`, `[Name](../sources/2026-04-20-jwt-refactor.md)`
- Link text uses the page title (no path, no `.md` suffix)

### Decision 8: ingest accepts polymorphic input (git / context / doc-import)

The default input channel is git, but a lot of valuable knowledge — tribal lore, rejected designs, external design docs, post-mortems — never makes it into commit messages. v1 addresses this by making ingest polymorphic on its argument:

| Mode | Invocation | Source page filename | `origin` |
|---|---|---|---|
| **git** (default) | `/repo-wiki:ingest` | `YYYY-MM-DD-<slug>.md` | `git` |
| **context** | `/repo-wiki:ingest "AuthModule naming dates to 2020 migration..."` | `YYYY-MM-DD-manual-<slug>.md` | `manual` |
| **doc-import** | `/repo-wiki:ingest "import design doc: docs/architecture/postgres.md"` (or path detected in arg) | `YYYY-MM-DD-doc-<slug>.md` | `doc-import` |

All three modes share the same downstream pipeline: write a source page → propagate to entity / concept pages → update index + log.

*Why this and not a separate `/repo-wiki:capture` skill*: the conceptual operation ("synthesize new info into .repo-wiki/") is the same; only the input source differs. A separate skill duplicates the pipeline.

*Why this and not a `.repo-wiki/inputs/` human-editable zone*: the inputs/ directory is a cleaner separation but adds a new ownership zone, complicates the CLAUDE.md drop-in rule, and is heavier UX. v1 keeps the conversational path; inputs/ is a v2 candidate (see backlog).

### Decision 9: Page-creation thresholds are descriptive, not numeric

The original draft specified "create entity page when module appears in 2+ source pages" / "create concept page when pattern appears in 3+ places". These numeric thresholds are not executable in practice — the LLM would need to grep all source pages and decide what counts as the "same module".

v1 uses descriptive heuristics instead:
- Entity: create when the module is meaningfully load-bearing across multiple changes
- Concept: create when a pattern is meaningfully cross-cutting

This trades pseudo-precision for honest judgment.

**v1.1 update — entity threshold removed for init Phase 1**:

Init's earlier soft threshold ("modules appearing in 3+ batches → entity stub") was dropped after dogfood feedback. Init Phase 1 now creates an entity stub for **every detected module** in src/, regardless of git-log activity. This addresses the v1.0 gap where old-but-stable modules had no entity at all.

The descriptive "meaningfully load-bearing" threshold still applies to:
- ingest creating new entities for emergent modules outside the init src/ scope
- concept creation in any context

Init's broad threshold is justified because completeness is the seed pass's main value; selectivity comes later via ingest as gotchas / decisions accumulate. See Decision 14 for why this doesn't violate Decision 1's WHY-not-WHAT principle.

### Decision 10: Stale-page check is `last_updated > 60d` (and triggers verification, see Decision 13)

query flags pages where `last_updated > 60 days` AND treats this as **verification trigger T1** (Decision 13) — query reads the entity's `paths:` to spot-check current-behavior claims. v1 does NOT do per-query `git log` cross-check (that requires git history scan); the full git-aware staleness sweep ships as `/repo-wiki:lint` in v2.

### Decision 11: SCHEMA.md is frozen until v2.0

SCHEMA.md structural rules will not change within the v1.x line. v1.x patches may clarify wording but cannot add page types, change frontmatter shape, or alter naming conventions. Major schema changes ship in v2.0 with a migration script.

*Why*: schema drift across .repo-wiki/ instances is a hard bug to detect and fix. A frozen schema gives v1 users a stability guarantee.

### Decision 12: ingest is idempotent via log.md

ingest's first step (in git mode) reads `.repo-wiki/log.md` to find the most recent ingest's last commit SHA, then runs `git log <sha>..HEAD`. If no new commits, ingest exits with "no new commits since last ingest". This prevents duplicate source pages on accidental re-runs.

For context and doc-import modes, idempotency is the user's responsibility — re-running with the same arg will write a new source page (timestamped). This is the right default because context-mode runs are intentional captures.

### Decision 13: .repo-wiki/ is implementation cache; src/ is current-state authority; query verifies at key moments

.repo-wiki/ pages may describe implementation (Responsibility, Architecture Snapshot, Dependencies) as a *best-effort cache* — but `src/**` is always the authoritative source of current behavior. To operationalize this fence without making every query slow, query runs an Eager verification pipeline that reads src/ at key moments and presents results in a Segmented format.

#### Verification triggers

Query evaluates these triggers in Step 3.5 of its workflow. Any positive trigger initiates `src/` verification of current-behavior claims in the answer.

| ID | Trigger | Verification action |
|---|---|---|
| **T1** | A loaded page has `last_updated > 60 days` | Read files listed in the entity's `paths:` frontmatter; spot-check claims about current behavior |
| **T2** | Question contains "currently", "now", "today", "still", "現在", "目前", "還有沒有" (or equivalents) | Spot-check current-behavior claims against `src/` |
| **T3** | Answer will inform code that user is about to write or modify (high-stakes context) | Verify entry-point files mentioned in the answer still exist + match described shape |
| **T4** | A loaded source page contains TODO or "subject to change" / "待確認" markers | Read corresponding `src/` area and update the answer with current state |
| **T5** | Multiple loaded pages contradict each other on a fact (e.g., entity says X is the entry point, source page says Y) | Read `src/` to arbitrate; flag the inconsistency in the answer; suggest `/repo-wiki:ingest` to fix |
| **T6** | Question is purely about past decisions ("why did we", "rejected alternatives") | **Negative trigger** — do NOT verify; trust .repo-wiki/ (decisions don't change retroactively) |
| **T7** | User explicitly requests verification ("verify against current src/", "make sure this is still true") | Verify every claim against `src/` |

#### Segmented output format (B from design discussion)

When any trigger fires, query presents the answer in three explicit sections:

```markdown
## Verified Claims (against src/)
- [Claim] — verified at src/<path>:<line> on <date>

## Unverified Claims (from .repo-wiki/ cache)
- [Claim] — sourced from .repo-wiki/<page>; not verified this query

## Discrepancies Found
- .repo-wiki/<page> says X but src/<path> shows Y
  → Suggest: /repo-wiki:ingest "<correction context>"
```

When NO trigger fires (e.g., a pure "why" question hitting T6), query uses the standard answer format with inline citations — no segmented output, no slowdown.

#### Why Eager (over Lazy)

Lazy verification (only T2/T3/T7) saves time when .repo-wiki/ is fresh, but the highest-value verification is exactly when .repo-wiki/ is stale (T1) or self-inconsistent (T5). Eager guarantees the user catches drift; the speed cost is worst exactly where it matters most. Users who want speed-over-correctness for a specific query can phrase it as a pure "why" question (T6).

#### Detection rules (executable)

Trigger detection is mechanical for T1/T4 (date arithmetic, grep), lexical for T2/T6/T7 (keyword lists across EN/JP/ZH), contextual for T3 (action keywords + recent Edit/Write tool history), and bounded LLM-judgment for T5 (focused contradiction check on loaded pages only). Full keyword lists, positive/negative examples, edge cases, and short-circuit ordering are specified in the [query SKILL design](../research/2026-05-02-repo-wiki-skill-query.md) under "Trigger Detection Specification". The detection rules ship as part of the SKILL.md body so the LLM has them in context every query.

Detection priority: **T7 > T6 > {T1, T2, T3, T4, T5}**. T7 (user explicit) overrides everything; T6 (pure decision) blocks verification when no T2/T3 keyword is present; otherwise any positive T1-T5 triggers segmented output.

#### Required schema support

For verification to know where to read, entity frontmatter MUST include `paths: [...]` listing the directories or files that comprise the entity. init populates this from `git ls-files` (Phase 1, v1.1) — every detected module's directory tree. ingest updates it when commits move files. If `paths:` is missing on an entity loaded for verification, query falls back to grep-based path discovery and warns the user that the entity is malformed.

### Decision 14: init reads path metadata, not file contents

**Added in v1.1.** Distinguishing repo-wiki from Greptile/DeepWiki-style code summarizers requires a clear fence: init never opens src/ files to summarize their contents.

Allowed inputs to init:
- `git ls-files` output — paths only
- Entry-point file paths (`index.*`, `__init__.py`, `main.go`, `mod.rs`, `package.json`, `README.md`) — paths recorded; **contents NOT read**
- One exception: `package.json`'s `name` field — metadata, not implementation
- `git log` output — commit messages, dates, SHAs, file paths

Forbidden:
- Opening any source file under src/ (or wherever the source root is detected) and reading its contents
- Asking the LLM to summarize what code does based on AST or function signatures
- Generating "Responsibility" / "Architecture Snapshot" content from path names alone — those sections remain `TODO` after init and fill via ingest

Why this matters:
- Preserves Decision 1 (WHY first; entity content fills via ingest with real WHY signal, not init guessing from paths)
- Keeps repo-wiki distinct from Greptile/DeepWiki SaaS code summarizers (the comparison table below depends on this)
- Bounds init's token cost to O(N paths) instead of O(N file contents); 5000-file repo costs ~50KB of context, not several MB

The Phase 1 src/ scan (added in v1.1) is consistent with this rule because it consumes only path metadata. Each module's `Common Entry Points` section lists file paths, not file content summaries.

### Decision 15: full-history backfill is opt-in via explicit `init full-history`

**Added in v1.1.** Default `/repo-wiki:init` does Phase 1 (src/ scan + per-module last-5 commits) + Phase 2 (90d global scan, 15-source-page cap). It does NOT walk the entire git history into era-grouped source pages.

Phase 3 era backfill triggers only when the user explicitly invokes:
- `/repo-wiki:init full-history`
- `/repo-wiki:init "full backfill"`
- `/repo-wiki:init "完整歷史"` / `"全歷史"`

When triggered, Phase 3 runs `git log --all` (no time bound), groups by 6-month era, identifies major commits per era (50+ files OR cross-module merge OR conventional-commit major change OR tagged release), and writes one source page per era. Era pages are exempt from the 15-page Phase 2 cap (which still applies to Phase 2 batches).

Why opt-in:
- Most repos don't need historical era backfill on first init — recent activity (Phase 2) plus per-module last-5 commits (Phase 1) cover the practical 80%
- Phase 3 cost scales with history length; a 5-year repo could produce 10 era pages and significantly more LLM-write effort
- Keeping Phase 3 explicit lets users decide whether the cost is justified for their repo

---

## Comparison with Existing Tools

| Tool | Gap |
|---|---|
| SamurAIGPT/llm-wiki-agent | General documents only; no git / code awareness |
| Roo Memory Bank | Full-text injection; no page types; no WHY synthesis |
| RepoAgent | Auto-commits knowledge updates; no query skill |
| Code-Index-MCP | Semantic search only; no WHY synthesis; not a wiki |
| Greptile | SaaS; code leaves machine |

repo-wiki's unique combination: **git-aware ingest + polymorphic context capture + structured WHY knowledge + AI-owned wiki + verification-fenced reads (.repo-wiki/ is cache, src/ is authority) + pure SKILL.md (zero external deps)**

---

## Open Questions (deferred to v2 design)

- Monorepo support — one `.repo-wiki/` at root, or per-app subdirectories?
- `.repo-wiki/inputs/` zone — should v2 introduce a human-editable input directory for accumulating external context (see Decision 8 alternative)?
- Multi-person CI workflow — what shape should the AI-proposes-humans-approve flow take (PR comments? draft commits? separate proposal branch)?
- Ruler / AGENTS.md drop-in — auto-distribute the AI-owned rule to vendor-neutral agent files alongside CLAUDE.md?
- `/repo-wiki:lint` — full health-check suite (broken links, stale entities with git cross-check, modules missing entity pages)?
- `/repo-wiki:graph` — build wikilink/markdown-link graph from .repo-wiki/ → JSON + HTML visualization?
