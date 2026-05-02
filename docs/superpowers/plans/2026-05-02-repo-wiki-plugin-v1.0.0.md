# repo-wiki Plugin v1.0.0 Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal**: Build and publish a Claude Code plugin that applies the Karpathy LLM Wiki Pattern to code repos — seed and grow a persistent `.repo-wiki/` directory from git changes (and ad-hoc context), query it with natural language.

**Spec reference**: [../specs/2026-05-02-repo-wiki-plugin-design.md](../specs/2026-05-02-repo-wiki-plugin-design.md)

**Distribution**: monkey-skills sub-plugin (10th sibling alongside dev-workflow, obsidian, etc.)
**Plugin namespace**: `repo-wiki`
**Skills delivered**: `/repo-wiki:init`, `/repo-wiki:ingest`, `/repo-wiki:query`

---

## Phase 1 — Plugin Skeleton

- [ ] Create `monkey-skills/repo-wiki/` directory
- [ ] Create `monkey-skills/repo-wiki/.claude-plugin/plugin.json`:
  ```json
  {
    "name": "repo-wiki",
    "version": "1.0.0",
    "description": "LLM Wiki pattern for code repos. Seed a persistent knowledge base from git history (init), grow it incrementally from changes or conversational context (ingest), and query it with natural language (query). Zero external dependencies — knowledge lives as plain markdown committed into your repo.",
    "author": { "name": "kouko", "url": "https://github.com/kouko" },
    "homepage": "https://github.com/kouko/monkey-skills/tree/main/repo-wiki",
    "repository": "https://github.com/kouko/monkey-skills",
    "license": "MIT",
    "keywords": [
      "repo-knowledge",
      "knowledge-base",
      "llm-wiki",
      "code-wiki",
      "git-aware",
      "documentation",
      "tribal-knowledge"
    ]
  }
  ```
- [ ] Create directories: `skills/init/`, `skills/ingest/`, `skills/query/`, `templates/`
- [ ] Update [.claude-plugin/marketplace.json](../../../.claude-plugin/marketplace.json) — add `{ "name": "repo-wiki", "source": "./repo-wiki/" }` to the plugins array

### Done when
- Plugin directory exists with correct structure
- `plugin.json` validates against Claude Code plugin schema
- marketplace.json includes repo-wiki and lists 10 plugins total
- `git status` shows the new plugin tree, but no SKILL.md content yet

---

## Phase 2 — Write SKILL.md Files

### init skill (`skills/init/SKILL.md`)

Full design: [../../docs/superpowers/research/2026-05-02-repo-wiki-skill-init.md](../research/2026-05-02-repo-wiki-skill-init.md)

Key requirements:

- [ ] YAML frontmatter: `name: init`, description triggers on "first time setup", "seed knowledge base", "init repo-wiki", "/repo-wiki:init"; explicitly NOT for incremental updates (use ingest)
- [ ] Step 1: Sanity check — abort if cwd has no `.git/`; warn + ask to confirm if `.repo-wiki/` already exists
- [ ] Step 2: Scaffold — `mkdir -p .repo-wiki/{sources,entities,concepts,syntheses}` + copy `templates/{SCHEMA,index,log,overview}.md` into .repo-wiki/
- [ ] Step 3: CLAUDE.md drop-in — write/update `<!-- repo-wiki:start --> ... <!-- repo-wiki:end -->` block in repo root CLAUDE.md (idempotent: replace existing block, append if absent, create file if missing)
- [ ] Step 4: Bounded git scan — `git log --since='90 days ago' --pretty=fuller --name-only --stat`, capped at 50 commits or 90d (whichever hits first); user can override window via natural-language arg ("init from last year", "init last 100 commits")
- [ ] Step 5: Logical batching — group commits by time (3d gap) + branch boundary + file overlap (>50% Jaccard) into batches; one source page per batch in `.repo-wiki/sources/YYYY-MM-DD-<slug>.md` with `origin: git`. **Hard cap: max 15 source pages per init**; if exceeded, downsample by widening time gap (3d → 7d → 14d); if still >15, keep top 15 by total LOC changed and write overflow note. (Full algorithm + edge cases in init SKILL design Step 5.)
- [ ] Step 6: Entity stub derivation — for paths appearing in 3+ batches, create `.repo-wiki/entities/<EntityName>.md` stub using **Entity Name Normalization Rule** in SCHEMA.md (strip src/lib/app/ prefix → split on / - _ → PascalCase concat). **`paths:` frontmatter MUST be populated** (top 1-3 most-touched paths from git stat) — query verification depends on it (Decision 13). Responsibility derived from commit messages + path; gotchas/dependencies left as TODO.
- [ ] Step 7: Overview synthesis — write `.repo-wiki/overview.md` from git log + top-level directory structure (and README excerpt if present)
- [ ] Step 8: Update index.md + write first log entry `## [YYYY-MM-DD] init | seeded from last 90d (N commits)`
- [ ] Step 9: Print summary + next-step hint ("Run /repo-wiki:ingest after your next feature")
- [ ] Hard rules: NEVER modify `src/**`; entity stubs are skeletal (no fabricated WHY); only one CLAUDE.md drop-in block

### ingest skill (`skills/ingest/SKILL.md`)

Full design: [../research/2026-05-02-repo-wiki-skill-ingest.md](../research/2026-05-02-repo-wiki-skill-ingest.md)

Key requirements:

- [ ] YAML frontmatter: `name: ingest`, description triggers on "update knowledge", "ingest changes", "capture context", "/repo-wiki:ingest"; explicitly NOT for answering questions (use query)
- [ ] Step 0: Mode dispatch using **exact algorithm**: no arg → git; explicit import marker (e.g. "import doc:", "讀取", "匯入") + valid path → doc-import; otherwise → context (default; mentioning a path without marker is NOT doc-import). Full marker list (EN/JP/ZH) and path extraction rules in ingest SKILL design Step 0.
- [ ] Step 1 (git mode): Read `.repo-wiki/log.md` for last ingest/init SHA → `git log <last_sha>..HEAD --oneline --stat`; if empty, exit with "No new commits since last ingest"
- [ ] Step 1 (context mode): Treat arg as the input payload
- [ ] Step 1 (doc-import mode): Read the referenced file
- [ ] Step 2: Read `.repo-wiki/index.md` + `.repo-wiki/overview.md` for current state
- [ ] Step 3: Create source page — filename varies by mode (`<date>-<slug>.md` / `<date>-manual-<slug>.md` / `<date>-doc-<slug>.md`); frontmatter includes `origin: git | manual | doc-import` and (for doc-import) `source_path`
- [ ] Step 4: Update/create entity pages — descriptive heuristic (no numeric threshold); only create if module is meaningfully load-bearing across multiple sources. Apply **Entity Name Normalization Rule** in SCHEMA.md to derive entity name from primary path — same rule as init, ensures no duplicate entities. Before creating new entity, check by normalized name; if exists → update, don't duplicate. Detect collisions (different paths normalizing to same name) and add prefix-derived disambiguator. **`paths:` maintenance**: git mode appends new paths from added files, updates renamed paths from `git log --diff-filter=R --name-status`, removes deleted paths. Context/doc-import modes ask before adding new paths.
- [ ] Step 5: Update/create concept pages — same descriptive heuristic for cross-cutting patterns
- [ ] Step 6: Update `.repo-wiki/index.md` + append to `.repo-wiki/log.md` (`## [date] ingest:<mode> | <description>` format) + update `.repo-wiki/overview.md` if architecture-level change
- [ ] Step 7: Validate — every link added today points to a page in index.md; print summary
- [ ] Hard rules: NEVER modify `src/**`; NEVER delete pages; write WHY not WHAT; standard markdown links only (not `[[wikilinks]]`); NEVER auto-ingest without user invocation

### query skill (`skills/query/SKILL.md`)

Full design: [../research/2026-05-02-repo-wiki-skill-query.md](../research/2026-05-02-repo-wiki-skill-query.md)

Key requirements:

- [ ] YAML frontmatter: `name: query`, description triggers on architecture / "why" / "how does X work" / "現在怎麼" questions, "/repo-wiki:query"; explicitly NOT for new code or debugging
- [ ] Step 1: Read `.repo-wiki/index.md`
- [ ] Step 2: Identify relevant pages (entity / concept / sources / syntheses); load ONLY those
- [ ] Step 3: Draft answer from .repo-wiki/ — classify each claim as current-behavior / past-decision / pointer
- [ ] Step 3.5: **Verification trigger evaluation (Decision 13)** — evaluate T1 (last_updated > 60d, mechanical), T2 (current-state keywords, lexical EN/JP/ZH list), T3 (action-imperative keywords OR recent Edit/Write tool calls in session), T4 (TODO/subject-to-change/待確認 grep on loaded page bodies), T5 (focused LLM-judgment contradiction check restricted to loaded pages), T7 (explicit verification keywords). Eager policy: any positive trigger → read entity's `paths:` frontmatter and verify current-behavior claims against src/. T6 (pure decision question — historical keywords AND no T2 AND no T3) is a negative trigger that skips verification. Detection priority: T7 > T6 > {T1-T5}. **Full detection rules (keyword lists, positive/negative examples, edge cases) MUST be embedded in the shipped SKILL.md body** — see [query SKILL design](../research/2026-05-02-repo-wiki-skill-query.md) Trigger Detection Specification section.
- [ ] Step 3.6: **Stale feedback loop** — when verification finds discrepancy, suggest concrete `/repo-wiki:ingest "<correction>"` after presenting the answer
- [ ] Step 4: Present answer — segmented format (Verified Claims / Unverified Claims / Discrepancies Found) when ANY trigger fired; standard inline-citation format when NO trigger fired (T6 only)
- [ ] Step 5: Offer to save answer to `.repo-wiki/syntheses/<question-slug>.md`; saved synthesis preserves verification markers + records `verification_run` and `verified_paths` frontmatter; append log entry regardless of save decision
- [ ] Gap handling: when no relevant page exists, say so explicitly; offer (a) read src/ directly with no save, (b) suggest /repo-wiki:ingest with scope for git-mode capture, or (c) suggest /repo-wiki:ingest with context arg
- [ ] `paths:` fallback: when loaded entity has no `paths:` frontmatter, fall back to grep-based src/ discovery + log warning ("entity malformed, paths missing")
- [ ] Hard rules: NEVER hallucinate; NEVER present current-behavior claims as authoritative without running triggers; NEVER auto-ingest from query (only suggest); standard markdown links only

### Done when
- Three SKILL.md files exist with the structure above
- Each frontmatter validates (name matches directory; description includes triggers and "do NOT" guards)
- Bash blocks in each SKILL.md are syntactically correct
- All inter-skill references use the namespaced form (`/repo-wiki:init`, etc.) consistently

---

## Phase 3 — Templates

- [ ] Create `templates/SCHEMA.md` (full design: [../research/2026-05-02-repo-wiki-schema-design.md](../research/2026-05-02-repo-wiki-schema-design.md)):
  - Three-layer architecture definition + **Positioning Statement** (.repo-wiki/ is implementation cache, src/ is current-state authority)
  - Page type rules (when to create source/entity/concept/synthesis), descriptive heuristics not numeric
  - **Entity required frontmatter `paths: [...]`** with example
  - Naming conventions (PascalCase entities/concepts, YYYY-MM-DD-kebab sources)
  - **Entity Name Normalization Rule** (path-derived names, prefix stripping, examples table, collision handling) — shared between init and ingest
  - source page `origin` field spec (git / manual / doc-import)
  - index.md and log.md format specs (log entries use `ingest:<mode>` form)
  - "Standard markdown links only" rule with examples
  - **Verification Triggers (T1-T7) table** referencing query SKILL behavior
  - Health check criteria (deferred to /repo-wiki:lint in v2 — v1 SCHEMA mentions this only as future-facing)
  - "What .repo-wiki/ does NOT contain" list
  - Schema freeze notice ("frozen until v2.0")
- [ ] Create `templates/index.md` (skeleton with section headers: Overview / Sources / Entities / Concepts / Syntheses)
- [ ] Create `templates/log.md` (empty body + comment noting `## [YYYY-MM-DD] <op>:<mode> | <title>` format)
- [ ] Create `templates/overview.md` (skeleton with TODO sections that init will fill)
- [ ] Create `templates/claude-md-snippet.md` (the exact `<!-- repo-wiki:start --> ... <!-- repo-wiki:end -->` block init injects into the user's repo CLAUDE.md)

### Done when
- 5 template files exist
- SCHEMA.md compiles to valid markdown and is consistent with the SKILL.md page-type contracts
- claude-md-snippet.md content matches the spec Decision 5 example verbatim
- No `.repo-wiki/` directory inside the plugin itself (templates are copy sources, not runtime data)

---

## Phase 4 — Test

### Setup
- [ ] Create `test-repo/`: `mkdir test-repo && cd test-repo && git init && git commit --allow-empty -m "initial commit"`
- [ ] Add fake `src/` files and ~10 commits across 2-3 fake modules to give init something to chew on
- [ ] Load plugin: `claude --plugin-dir ../monkey-skills/repo-wiki` (or via marketplace if installed)
- [ ] Verify skills appear: `/help` shows `/repo-wiki:init`, `/repo-wiki:ingest`, `/repo-wiki:query`

### init tests
- [ ] Run `/repo-wiki:init` — verify:
  - .repo-wiki/ directory created with all subdirs + SCHEMA.md / index.md / log.md / overview.md
  - CLAUDE.md created (or appended) with `<!-- repo-wiki:start/end -->` block
  - Source pages created for the fake commit batches
  - Entity stubs for the 2-3 fake modules
  - overview.md has actual content (not just template skeleton)
  - log.md first entry format: `## [date] init | seeded from last 90d (N commits)`
  - Does NOT touch src/
- [ ] Re-run `/repo-wiki:init` — verify warning + idempotent CLAUDE.md (no duplicate block)
- [ ] Run `/repo-wiki:init` in non-git directory — verify abort with clear error

### ingest tests
- [ ] Make a new fake commit, run `/repo-wiki:ingest` — verify:
  - Reads log.md, finds last init SHA, picks up only the new commit
  - Creates new source page (`origin: git`)
  - Updates relevant entity page (or creates new one)
  - log.md entry: `## [date] ingest:git | <description>`
- [ ] Re-run `/repo-wiki:ingest` immediately — verify exits with "No new commits since last ingest"
- [ ] Run `/repo-wiki:ingest "AuthModule has weird naming because of legacy migration"` (context mode) — verify:
  - Source page `YYYY-MM-DD-manual-<slug>.md` with `origin: manual`
  - AuthModule entity page Gotchas section updated
  - log.md entry: `## [date] ingest:manual | <description>`
- [ ] Create a fake design doc `docs/postgres-decision.md` and run `/repo-wiki:ingest "import design doc: docs/postgres-decision.md"` — verify:
  - Source page `YYYY-MM-DD-doc-<slug>.md` with `origin: doc-import` and `source_path: docs/postgres-decision.md`
  - Concept page created if doc describes a pattern

### query tests
- [ ] Run `/repo-wiki:query "why did we choose X over Y for FakeModule"` (T6 — pure decision question) — verify:
  - Standard inline-citation format (NO segmented output)
  - No src/ verification reads happen
  - Sources listed with `[Name](path)` markdown links
  - Offers to save synthesis
- [ ] Run `/repo-wiki:query "how does FakeModule currently work"` (T2 — current-state keyword) — verify:
  - Segmented output appears (Verified / Unverified / Discrepancies)
  - At least one verification read against entity's `paths:` files
  - Verified claims marked with `src/<path>:<line>` reference
- [ ] Manually set an entity page's `last_updated` to 90 days ago, run any query that loads it (T1) — verify segmented output triggered, verification ran
- [ ] Manually edit a fake src/ file to make it diverge from entity page description, run a current-state query (T1+T2) — verify Discrepancies section appears with concrete `/repo-wiki:ingest "..."` suggestion
- [ ] Add T4 marker ("TODO: subject to change") to a source page, query about that area — verify verification triggered
- [ ] Create two pages with contradictory facts about same module (T5), query — verify verification triggered, arbitration done, suggestion to /repo-wiki:ingest the correction
- [ ] Run `/repo-wiki:query "verify auth handling against current code"` (T7 explicit) — verify all claims segmented as verified
- [ ] Delete `paths:` frontmatter from an entity, run query — verify warning + grep fallback works, answer still valid
- [ ] Run `/repo-wiki:query "<question about a module without an entity page>"` — verify explicit gap message + offer (a)/(b)/(c)
- [ ] Save a synthesis after segmented-format answer — verify `verification_run: yes` and `verified_paths: [...]` frontmatter present

### Edge cases
- [ ] Run `/repo-wiki:ingest` in a brand-new repo with no commits since init — verify graceful exit
- [ ] Run `/repo-wiki:query "any question"` before init — verify clear "knowledge base not initialized; run /repo-wiki:init"
- [ ] **G2 batching cap**: create test repo with 80+ commits across many independent topics over 90 days; run init — verify ≤15 source pages produced + downsampling note in log if applicable + overflow source page if hard truncation happened
- [ ] **G3 mode dispatch**: test all 3 modes — bare `/repo-wiki:ingest`, `/repo-wiki:ingest "context with src/auth/jwt.ts mention"` (must be context not doc-import), `/repo-wiki:ingest "import doc: docs/postgres.md"` (must be doc-import); verify each gets correct treatment
- [ ] **G3 ambiguous**: `/repo-wiki:ingest "import design doc: nonexistent.md"` — verify ask-user prompt for correct path
- [ ] **G4 naming consistency**: init creates `Auth.md` from `src/auth/`; later ingest a commit touching `src/auth/` — verify ingest updates same `Auth.md`, does NOT create `AuthModule.md` or any duplicate
- [ ] **G4 collision**: create test repo with both `src/auth/` and `lib/auth/`; run init — verify entities named `Auth` and `LibAuth` (or similar disambiguation), not collision
- [ ] Test on monkey-skills repo itself (dogfood) — back up CLAUDE.md first; decide whether produced `.repo-wiki/` is committed (note in plan: defaulting to committed as reference)

### Done when
- All happy-path tests pass
- All edge cases produce graceful errors with actionable messages
- .repo-wiki/ output is human-readable on GitHub (links resolve, no `[[wikilink]]` artifacts)
- No regression in monkey-skills marketplace loading

---

## Phase 5 — README and Release

- [ ] Write `repo-wiki/README.md` (English, primary):
  - One-paragraph what + why
  - Visual: mermaid showing init / ingest / query flow
  - Installation: via monkey-skills marketplace
  - Quick start: `/repo-wiki:init` → `/repo-wiki:ingest` → `/repo-wiki:query` example
  - The three modes of ingest (git / context / doc-import) with examples
  - ".repo-wiki/ is AI-owned" rule + CLAUDE.md drop-in note
  - Comparison table (vs Greptile / Memory Bank / RepoAgent / etc.) — pulled from spec
  - Failure modes: first-run with no .repo-wiki/, ingest with no new commits, query with empty KB
  - Philosophy section (3 principles): WHY over WHAT, gap as feedback, synthesize at ingest
- [ ] Write `repo-wiki/README.ja.md` (Japanese mirror — match other monkey-skills sub-plugins' i18n style)
- [ ] Write `repo-wiki/README.zh-TW.md` (Traditional Chinese mirror)
- [ ] Write `repo-wiki/CHANGELOG.md`:
  - `## [1.0.0] - 2026-05-02` initial release
  - Lists three skills, key design decisions
- [ ] Update root [README.md](../../../README.md), [README.ja.md](../../../README.ja.md), [README.zh-TW.md](../../../README.zh-TW.md) plugin lists to mention repo-wiki
- [ ] Update [ATTRIBUTION.md](../../../ATTRIBUTION.md) — credit llm-wiki-skill, llm-wiki-agent, Karpathy LLM Wiki Pattern
- [ ] Open PR `feat/repo-wiki-v1.0.0` → main; reference this plan + spec in PR description

### Done when
- All four README/CHANGELOG files exist and are consistent
- Root marketplace metadata updated
- ATTRIBUTION.md credits prior art
- PR opened, CI passes, ready for self-review

---

## v2 Backlog (out of scope for v1.0.0)

Tracked here so v1 reviewers know what was deliberately deferred:

- **`.repo-wiki/inputs/` zone** — formal human-editable input directory as alternative/supplement to ingest's context mode (Decision 8 alternative)
- **Multi-person CI workflow** — `.github/workflows/repo-wiki-proposal.yml` template for AI-proposes-humans-approve flow on PRs (Decision 6 deferred)
- **`/repo-wiki:lint`** — health check skill: broken links, stale entities with git cross-check (Decision 10), modules missing entity pages, orphan concepts
- **`/repo-wiki:graph`** — build navigation graph from .repo-wiki/ standard-markdown-link references → JSON + HTML visualization
- **SCHEMA migration script** — when v2.0 changes SCHEMA, ship migration tool (Decision 11 freeze ends)
- **Monorepo support** — per-app `.repo-wiki/` subdirectories, query skill knows how to choose
- **Ruler / AGENTS.md drop-in** — vendor-neutral distribution of the AI-owned rule alongside CLAUDE.md
- **Standalone repo graduation** — fork to `kouko/repo-wiki` when v1.x is validated, submit to Anthropic plugin marketplace

---

## Key Design Constraints (do not regress)

1. **Zero external dependencies** — no MCP servers, no vector stores, no Python scripts required
2. **.repo-wiki/ is AI-owned** — humans never directly edit; CLAUDE.md drop-in enforces this beyond skill scope
3. **WHY first; WHAT is best-effort cache** — entity/concept pages may include implementation description but it's never authoritative
4. **src/ is the current-state authority** — query verifies current-behavior claims at key moments (Decision 13); never present cached descriptions as authoritative
5. **Eager verification + segmented output** — when triggers T1-T5/T7 fire, query reads src/ and presents Verified / Unverified / Discrepancies sections
6. **Entity `paths:` is required** — verification depends on it; init populates from git stat, ingest maintains it
7. **Gap is a feature** — when query finds no page, it says so explicitly; this drives ingest coverage
8. **Never touch src/** — all skills read code as input; none write back to source files
9. **Standard markdown links only** — no `[[wikilinks]]`; .repo-wiki/ must render correctly on GitHub
10. **SCHEMA frozen** — v1.x cannot change page types or frontmatter shape; ship schema changes in v2.0
11. **Three skills, single responsibilities** — init seeds, ingest grows, query reads; resist merging
