# Changelog

All notable changes to the `repo-wiki` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — v1.2.0 precision fusion

Three independent precision improvements inspired by SourceAtlas's
information-theory analysis discipline (Article I — high-entropy priority,
scan-ratio bounds), adapted to repo-wiki's three skills along three
different axes. Schema-zero — no v1.x freeze break.

### Added — `BENCHMARK.md` baseline schema

- New top-level `BENCHMARK.md` establishes the measurement harness:
  5 public repos (fastapi, hono, loki, rails, Signal-Android) × 3 skills
  (init, ingest, query) with reproducible methodology.
- Measurement cells start as `TBD`; v1.2 PRs append delta columns.
- Establishes ground-truth conventions (author-declared module list,
  hand-labelled architectural commits, sealed reference query answers).

### Changed — `/repo-wiki:query` adds verification scan budget + coverage reporting

- Step 3.5 gains a **Verification Budget** subsection with formula
  `budget = max(1, min(10, ceil(0.05 × total_paths)))` so a single query
  never opens more than 10 `src/` files. T7 (explicit verify) keeps the
  same cap; uncovered claims surface in Unverified.
- Deterministic file selection: claim-mentioned → entry points →
  most-recently-modified → stop when budget exhausted.
- Step 4 segmented format gains mandatory `## Verification Coverage`
  section reporting triggers fired, files-read / total-paths, selection
  rationale, and uncovered paths in scope. Makes verification depth a
  first-class output instead of a hidden side-effect.
- Synthesis frontmatter gains optional `verification_budget` and
  `verification_coverage_pct`; `log.md` query entry gains
  `Verification: N/M (P%)` line when triggers fired.

### Changed — `/repo-wiki:init` adds high-entropy author-boundary pre-scan to Phase 1

- New **Step 4a-pre — High-Entropy Author-Boundary Pre-Scan** runs
  before `git ls-files` heuristics. Reads structural fields only (NOT
  source code) from root configs to extract author-declared module
  boundaries: `package.json` workspaces, `pnpm-workspace.yaml`,
  `lerna.json`, `nx.json` + `project.json`, `tsconfig.json` paths,
  `go.mod` module + replace, `pyproject.toml` packages, `setup.py`,
  `Cargo.toml` workspace + lib/bin paths, `Gemfile` + gemspecs,
  `composer.json` autoload.psr-4, `pom.xml` / `build.gradle` modules,
  root `README.md` H2 titles.
- Step 4a's depth rule gains an **author-declared boundary override**:
  author-declared paths always become entities (depth rule overridden);
  declared name wins over path-normalized name; author paths shadow
  heuristic paths on overlap. Heuristic depth-1/2 modules fill the gaps.
- `log.md` init entry gains `Modules discovered: N (author-declared: A,
  heuristic: H)` and `Boundary configs scanned: <list>`.
- Single-package repos with no matching configs see zero behavior change.

### Changed — `/repo-wiki:ingest` adds entropy-weighted commit sampling for large git-mode batches

- New **Step 1.5 — Entropy-Weighted Classification (Git Mode Only)**
  runs when `commits_count >= 5`. Below 5 commits, classification is
  skipped — v1.1 single-page behavior preserved for typical post-feature
  ingests.
- Three weight classes, observable git metadata only (no file content reads):
  - **HIGH**: touches root config (Step 4a-pre whitelist), 3+ entities,
    Common Entry Point, `feat(...)` / `refactor(...)` / `BREAKING CHANGE`,
    new top-level dir, or tagged release → own source page
  - **MEDIUM**: touches 2 entities, `fix(...)` with body, or new file in
    existing module → file-overlap-batched (Jaccard >50%)
  - **LOW**: test-only, docs-only, `chore` / `style` / `format`, or
    single-file non-config non-entry → roll-up; log-only if <3 LOW commits
- Source-page budget `min(15, ceil(commits/5))`. HIGH-first allocation;
  overflow HIGH commits go into one noted overflow page (never silently
  dropped).
- `log.md` ingest entry gains `Classification: H/M/L (skipped: K)` and
  `Sources created (budget: used/budget)` lines when classification ran.

### Schema impact

Zero. SCHEMA.md unchanged. New optional frontmatter keys
(`verification_budget`, `verification_coverage_pct`) are additive — old
syntheses parse unchanged. v1.x freeze respected.

### Migration notes

- v1.1 → v1.2: re-running `/repo-wiki:init` on an existing knowledge base
  re-detects author-declared boundaries; existing entity stubs are
  preserved per the v1.1 idempotency contract.
- v1.1 → v1.2: existing syntheses without `verification_budget` continue
  to work; new queries write the new fields.
- v1.1 → v1.2: ingest behavior unchanged for any ingest with <5 commits.

---

## [1.1.0] — 2026-05-02

### Changed — `/repo-wiki:init` now provides complete src/ coverage

Init reframed from "bounded recent activity" to "complete current state +
recent decisions" based on dogfood feedback that v1.0 missed old-but-stable
modules entirely.

**New Phase 1 — src/ scan + per-module history (always runs)**:
- Discover all modules via `git ls-files` (no file content reads); auto-detect
  source root (`src/`/`lib/`/`app/`/`packages/*/src/`/`cmd/`/`internal/`/`pkg/`)
- Depth rule: top-level + depth-2 each become entities; deeper paths aggregate
  into parent's `paths:`
- Entry-point detection (`index.*`, `__init__.py`, `main.go`, `mod.rs`, etc.) —
  path only, contents not read
- Per-module history pull: `git log --max-count=5 -- <module-paths>` regardless
  of time — a 5-year-old stable module still gets 5 entries
- **Every detected module gets an entity stub** (no `3+ batches` threshold);
  stubs carry `paths:`, `Common Entry Points`, last 5 commits in `Recorded
  Decisions`; `Responsibility` / `Architecture` / `Gotchas` remain TODO

**Phase 2 (formerly the only phase) — bounded global git scan**:
- Same 90d / 50 commits / 15 source pages cap as v1.0
- Source pages now backfill entity `Recorded Decisions` and `sources:`
  cross-references rather than creating new entities

**New Phase 3 — era-grouped full-history backfill (opt-in)**:
- Triggered by `/repo-wiki:init full-history` (or "full backfill" / "完整歷史")
- `git log --all` no time bound; group commits by 6-month era (e.g., 2024-H2)
- Major-commit heuristic: 50+ files OR cross-module merge OR conventional-commit
  major change indicator OR tagged release
- Era pages exempt from 15-page cap; one page per era with major activity

**Mode dispatch (Step 4)**: arg containing `full-history` / `full backfill` /
`完整歷史` / `全歷史` switches to full-history mode; otherwise default
(Phase 1 + Phase 2 only).

### Design decisions added

- **Decision 9 (revised)**: entity creation threshold for init drops the
  "3+ batches" rule — every detected module gets a stub. Concept threshold
  unchanged.
- **Decision 14 (new)**: init reads path metadata (`git ls-files`,
  entry-point file paths) and `git log` output; init NEVER opens or reads
  src/ file contents. This preserves WHY-not-WHAT (Decision 1) and keeps
  repo-wiki distinct from Greptile/DeepWiki-style code summarizers.
- **Decision 15 (new)**: full-history backfill is opt-in via explicit
  `init full-history` arg. Default init bounds source-page generation to
  recent activity (Phase 2's 90d/15-page cap); historical era backfill
  must be requested explicitly.

### Re-run idempotency (init can now safely run more than once)

The v1.0 / early-v1.1 design had a Step 1 prompt promising "preserve
human-edited sections" on re-run, but the workflow steps did not
implement this — re-running init would truncate `log.md`, overwrite
ingest-accumulated entity sections (`Responsibility`, `Architecture
Snapshot`, `Gotchas`, `Dependencies`), and re-process the same Phase 2
commits as duplicates. This release fixes the gap so init's prompt and
behavior agree.

Changes:
- **Step 2 (Scaffold)**: conditional template copy. `SCHEMA.md` always
  overwrites (frozen, plugin-controlled); `index.md` / `log.md` /
  `overview.md` skip if file exists (regenerate or append in later
  steps).
- **Step 4d (Entity stubs)**: re-run merges instead of overwriting.
  Init-owned sections (`paths` frontmatter, `Common Entry Points`,
  seeded `Recorded Decisions`) refresh; user/ingest-owned sections
  (`Responsibility` / `Architecture Snapshot` / `Gotchas & Non-Obvious
  Design` / `Dependencies` if non-`TODO`, plus ingest-appended
  `Recorded Decisions` entries) are preserved verbatim.
- **Step 5 (Phase 2 scan)**: re-run reads `log.md`'s most recent
  `Last commit SHA` and scopes the git scan to new commits only —
  same idempotency model `/repo-wiki:ingest` already uses.
- **Step 6 (Source pages)**: filename collision check — skip if
  identical batch already exists, append `-2`/`-3` suffix if
  different commits collide on same date+slug.
- **Step 8 (Overview)**: re-run regenerates `## All Modules` /
  `## Recent Themes` / `## What Lives Where`; preserves
  `## Repository` section if user edited it (within new
  `<!-- repo-wiki:repository:start/end -->` markers).
- **Step 9 (Log)**: `log.md` is **append-only across all init runs**.
  Never truncated. Re-run records `Run type: re-run` plus
  `Window: incremental from <prev_sha>` for clarity.
- **Hard rules**: `## Rules` section adds three NEVER clauses
  (truncate log, overwrite ingest-filled sections, re-process covered
  commits) and one ALWAYS clause (re-run safety contract: prompt
  promises must be honored by the workflow).

User-facing impact: init can now be safely re-run after ingest has
populated entity content. No data loss. The Step 1 prompt is also
rewritten to honestly describe what re-run does (preserve / refresh /
skip per file).

### Plugin layout: templates/ → skills/init/assets/

To comply with Anthropic's plugin-conventions ("bundled resources live
inside the skill folder, referenced via paths relative to the skill
directory"), the `templates/` directory is moved from plugin root to
`skills/init/assets/`. init owns these files (it copies them at
runtime); ingest/query never touch them (they read the user-repo's
`.repo-wiki/` instead).

Path references in init SKILL.md change from `../../templates/<file>.md`
to `assets/<file>.md`. No user-facing impact — init still produces the
same `.repo-wiki/` output.

### Schema (frozen, only additive)

- Source page `origin: git` filename pattern adds `era-YYYY-HX.md` for Phase 3
- Source page (Phase 3 era) frontmatter adds `era`, `commit_count`, `major_commits`
- log.md operations table adds `init:full-history` mode
- Entity body required sections clarified: `Responsibility`, `Common Entry
  Points`, `Recorded Decisions`, `Architecture Snapshot`, `Gotchas &
  Non-Obvious Design`, `Dependencies`

No breaking changes to v1.0 schema — all v1.0 entity / source / log files
remain valid under v1.1.

### Unchanged

- `/repo-wiki:ingest` workflow — no changes
- `/repo-wiki:query` workflow including T1-T7 verification triggers — no changes
- CLAUDE.md drop-in template — no changes
- Entity Name Normalization Rule — no changes
- ingest idempotency via `log.md last_sha` — no changes

## [1.0.0] — 2026-05-02

### Added — Initial release

Three skills + 5 templates for the LLM Wiki Pattern applied to code repos.

**Skills**:
- `/repo-wiki:init` — one-time bootstrap. Scaffolds `.repo-wiki/` directory, writes idempotent CLAUDE.md drop-in (markers `<!-- repo-wiki:start --> ... <!-- repo-wiki:end -->`), and seeds source pages + entity stubs from the last 90 days of git history (bounded: max 50 commits / 15 source pages with `3d → 7d → 14d` downsampling).
- `/repo-wiki:ingest` — polymorphic incremental update. Three modes:
  - `git` (no arg, default) — reads `last commit SHA` from `log.md`, processes new commits since
  - `context` (free-form text arg) — captures tribal knowledge that never made it into commits
  - `doc-import` (explicit marker + valid path) — absorbs external design docs
- `/repo-wiki:query` — read with **Eager verification**. Triggers T1-T7 evaluate cache freshness; positive triggers cause `src/` reads with **segmented output** (Verified Claims / Unverified Claims / Discrepancies Found). T6 (pure decision questions) is a negative trigger and skips verification.

**Templates** (copied into target repo on init):
- `SCHEMA.md` — frozen v1.0 schema (page types, frontmatter, naming, linking)
- `index.md` — empty catalog skeleton
- `log.md` — append-only operation log skeleton
- `overview.md` — codebase overview skeleton
- `claude-md-snippet.md` — drop-in block for repo-root CLAUDE.md

### Design decisions (locked for v1.x)

The following 13 decisions are stable across the v1.x line. Changes ship in v2.0 with a migration script:

1. WHY-first; WHAT is best-effort cache (Decision 1)
2. Gap is feedback (Decision 2)
3. Synthesize at ingest, not query (Decision 3)
4. `.repo-wiki/` is AI-owned (Decision 4)
5. CLAUDE.md drop-in enforces AI-owned rule (Decision 5)
6. v1 ships single-developer; multi-person CI is v2 backlog (Decision 6)
7. Standard markdown links, not `[[wikilinks]]` (Decision 7)
8. ingest accepts polymorphic input — git / context / doc-import (Decision 8)
9. Page-creation thresholds are descriptive, not numeric (Decision 9)
10. Stale-page check is `last_updated > 60d` (trigger T1) (Decision 10)
11. SCHEMA frozen until v2.0 (Decision 11)
12. ingest is idempotent via `log.md` last commit SHA (Decision 12)
13. `.repo-wiki/` is implementation cache; `src/` is current-state authority; query verifies at key moments (Decision 13)

### Distribution

Ships as the 10th sibling plugin in the [monkey-skills](https://github.com/kouko/monkey-skills) marketplace. Standalone repo graduation is a v2 consideration.

### Inspiration

- [Karpathy LLM Wiki Pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — conceptual root
- [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) — `raw/ → wiki/` architecture reference
- [llmrix/llm-wiki-skill](https://github.com/llmrix/llm-wiki-skill) — SKILL.md implementation reference
