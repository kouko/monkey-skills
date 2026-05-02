# Changelog

All notable changes to the `repo-wiki` plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
