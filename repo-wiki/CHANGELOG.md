# Changelog

All notable changes to the `repo-wiki` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
