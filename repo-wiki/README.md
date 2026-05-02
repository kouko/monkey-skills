# repo-wiki

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Karpathy's LLM Wiki Pattern, applied to code repos. Seed a hidden `.repo-wiki/` knowledge base by scanning the entire src/ tree (every module gets an entity stub) plus per-module last-5 commits, then a bounded 90-day global git scan. Grow incrementally from changes and conversations; query with natural language. `src/` stays the source of truth — the wiki verifies cached claims at key moments.

**Version**: 1.1.0 · **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) · **License**: MIT

## Background

AI coding tools understand a codebase only within a single session. The next session starts from zero. Existing solutions split into:

- **SaaS semantic search** (Greptile, DeepWiki, Cursor @Codebase) — code leaves the machine; knowledge isn't in the repo.
- **Flat Markdown context** (CLAUDE.md, AGENTS.md, Memory Bank) — full-text injection; token cost explodes with repo size; no synthesized WHY.

`repo-wiki` fills the gap: persistent, repo-committed, synthesized knowledge that an AI agent can query without full-text injection — and without a SaaS dependency.

The architecture maps the [Karpathy LLM Wiki Pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) onto code:

```
raw/      (general wiki)  →  src/**       (code repo)
wiki/     (general wiki)  →  .repo-wiki/  (code repo)
ingest    (general wiki)  →  /repo-wiki:ingest
query     (general wiki)  →  /repo-wiki:query
```

## Skills

| Skill | When | Primary input |
|---|---|---|
| [`/repo-wiki:init`](skills/init/) | Once per repo (idempotent re-run safe) | Phase 1: author-boundary pre-scan (workspaces / TS paths / go.mod / pyproject / README H2) → `git ls-files` (full src/ tree) + per-module last-5 commits. Phase 2: 90d global git scan (bounded: max 50 commits / 15 source pages). Phase 3 (opt-in via `init full-history`): era-grouped full-history backfill. |
| [`/repo-wiki:ingest`](skills/ingest/) | After meaningful changes OR to capture context | Git diff since last ingest, OR text arg, OR file path |
| [`/repo-wiki:query`](skills/query/) | Whenever asking about codebase | `.repo-wiki/index.md` + relevant pages, with `src/` verification at key moments |

## Quick start

Install via the [monkey-skills marketplace](https://github.com/kouko/monkey-skills), then:

```bash
# In your repo's root, first time:
/repo-wiki:init

# After your next feature:
/repo-wiki:ingest

# Ask anything about the codebase:
/repo-wiki:query "how does AuthModule work"
```

`init` scaffolds `.repo-wiki/` with `SCHEMA.md` + `index.md` + `log.md` + `overview.md`, scans the entire src/ tree to build complete entity coverage (every detected module gets a stub with `paths` + `Common Entry Points` + last 5 commits as `Recorded Decisions`), then runs a bounded 90-day global git scan for cross-module change source pages. It also writes a small idempotent block into `CLAUDE.md` so any future session knows `.repo-wiki/` is AI-owned.

`init` is **safe to re-run**: it preserves `log.md` history, ingest-accumulated entity sections (`Responsibility`, `Architecture Snapshot`, `Gotchas`, `Dependencies`), and any `## Repository` section you customized in `overview.md`. Re-run only refreshes init-owned data (paths, entry points, seeded recent commits) and processes new commits incrementally via `log.md`'s last commit SHA.

**Default mode** (`/repo-wiki:init`) covers the practical 80%: complete current state + recent activity. **Full-history mode** (`/repo-wiki:init full-history`, also `"full backfill"` / `"完整歷史"`) adds Phase 3: era-grouped (6-month) backfill of major historical commits. Era pages are exempt from the 15-page Phase 2 cap.

**What init never reads**: src/ file contents. It uses only `git ls-files` paths, entry-point file paths, and `git log` metadata. This preserves the WHY-not-WHAT principle and keeps repo-wiki distinct from Greptile/DeepWiki-style code summarizers.

## ingest is polymorphic

The same skill handles three input modes — picked from the argument:

```bash
# Git mode (default) — incremental from last ingest's commit SHA
/repo-wiki:ingest

# Context mode — capture tribal knowledge that never made it into commits
/repo-wiki:ingest "AuthModule's naming dates to 2020 migration from old-auth-service"

# Doc-import mode — absorb an external design doc (explicit marker required)
/repo-wiki:ingest "import design doc: docs/architecture/postgres-decision.md"
```

Mentioning a path *without* an explicit import marker (`import`, `import doc`, `讀取`, `匯入`, `読み込んで`, etc.) stays in context mode — this avoids accidental file reads.

## `.repo-wiki/` is AI-owned, but `src/` remains authoritative

The most important design decision: **`.repo-wiki/` is a best-effort cache, not a source of truth**. Implementation descriptions in entity pages may go stale. To keep this honest, `/repo-wiki:query` runs an **Eager verification** pipeline:

When any of these triggers fires, query reads `src/` to spot-check current-behavior claims:

| ID | Trigger |
|---|---|
| T1 | Loaded page `last_updated > 60 days` |
| T2 | Question contains "currently" / "now" / "still" / 「現在」 / 「目前」 |
| T3 | Answer will inform new code being written (action verbs OR recent Edit/Write) |
| T4 | Loaded source page has TODO / "subject to change" / 「待確認」 |
| T5 | Multiple loaded pages contradict each other |
| T6 | Question is purely about past decisions (negative trigger — skips verification) |
| T7 | User explicitly requests verification |

When triggered, the answer is **segmented**:

```markdown
## Verified Claims (against src/)
- AuthModule uses jose for JWT signing — verified at src/auth/jwt.ts:12

## Unverified Claims (from .repo-wiki/ cache)
- AuthModule depends on SessionStore — sourced from AuthModule.md; not verified

## Discrepancies Found
- entity says "throws AuthError" but src/auth/jwt.ts:42 throws JwtError
  → Suggest: /repo-wiki:ingest "AuthError was renamed to JwtError"
```

Pure decision questions ("why did we choose Postgres") don't trigger verification — past decisions are immune to staleness.

## Daily workflow

```
1. Done with a feature → /repo-wiki:ingest
   AI reads git log + diff
   → writes sources/2026-05-02-add-payment.md (origin: git)
   → updates entities/PaymentService.md
   → maybe creates concepts/IdempotencyKey.md
   → updates index.md + log.md

2. Got tribal knowledge → /repo-wiki:ingest "PaymentService retries are 5x because of <reason>"
   → writes sources/2026-05-02-manual-payment-retries.md (origin: manual)
   → updates entities/PaymentService.md gotchas

3. Have a question → /repo-wiki:query "how does PaymentService handle errors"
   → reads index.md → loads PaymentService entity + recent sources
   → triggers verification (T2 if "current"; T1 if stale; etc.)
   → presents segmented answer with src/ pointers
   → offers to save synthesis
```

## Why not other tools

| Tool | Gap |
|---|---|
| Greptile / DeepWiki | SaaS, code leaves machine, no offline |
| Code-Index-MCP | Semantic search good, no WHY synthesis |
| Roo Memory Bank | Full-text injection, no page types, no verification |
| RepoAgent | Auto-commits knowledge updates (multi-person risk) |
| SamurAIGPT/llm-wiki-agent | General documents, not git/code-aware |
| `dev-workflow:git-memory` | Captures decision context **at commit time**; `repo-wiki` covers the **cross-commit architectural picture** — complementary, not competing |

`repo-wiki`'s unique combination: **git-aware ingest + polymorphic context capture + structured WHY knowledge + AI-owned wiki + verification-fenced reads + zero external dependencies**.

## Design philosophy

Five principles that drive every decision:

1. **Synthesize at ingest time, not query time** — knowledge is organized when ingest runs; query just reads
2. **WHY first, WHAT is best-effort cache** — implementation descriptions allowed but never authoritative
3. **Verify at key moments** — query reads `src/` when triggers fire; segmented output makes uncertainty explicit
4. **Gap is feedback** — when query finds no page or discovers stale info, it suggests a concrete `/repo-wiki:ingest`
5. **Multi-source input** — git is the default channel, but conversational context and external docs flow through the same ingest pipeline

## Schema is frozen until v2.0

`.repo-wiki/SCHEMA.md` page types, frontmatter shape, and naming conventions will not change within the v1.x line. Major schema changes ship in v2.0 with a migration script. v1 users do not need to plan for migrations within v1.x.

## v2 backlog

- `knowledge/inputs/` — formal human-editable input directory
- Multi-person CI workflow (AI proposes, humans approve via PR comments)
- `/repo-wiki:lint` — health checks (broken links, git-aware staleness, orphan concepts)
- `/repo-wiki:graph` — knowledge graph from markdown link references
- Monorepo support (per-app `.repo-wiki/` subdirectories)
- AGENTS.md drop-in (vendor-neutral distribution)
- Standalone repo graduation when v1.x stabilizes

## Inspiration & credits

- [Karpathy LLM Wiki Pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the conceptual root
- [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) — `raw/ → wiki/` architecture reference
- [llmrix/llm-wiki-skill](https://github.com/llmrix/llm-wiki-skill) — SKILL.md implementation reference
