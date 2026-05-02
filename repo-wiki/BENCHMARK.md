## repo-wiki Benchmark

Reproducible measurements of `/repo-wiki:init`, `/repo-wiki:ingest`, and `/repo-wiki:query` against public open-source repositories. Establishes baseline for v1.2 changes (query scan-budget, init high-entropy pre-scan, ingest entropy-weighted sampling).

**Status**: Schema established · Baseline runs **TBD**
**Last updated**: _(filled when first run completes)_
**Tested version**: 1.1.0

---

## Why this exists

repo-wiki has shipped two versions without quantitative evidence that init coverage, ingest selection, or query verification actually work as designed. Before introducing v1.2 changes inspired by SourceAtlas (high-entropy prioritization, scan budgets), we need a baseline so each PR can show measurable before/after.

This benchmark is **not** a marketing exercise. It's an internal regression harness: each v1.2 PR re-runs the same matrix and records deltas in its CHANGELOG entry.

## Methodology

### What gets measured

`init` (default mode, no `full-history`):
- **Wall-clock time** — from skill invocation to "init complete" message
- **Entities created** — count of files in `.repo-wiki/entities/`
- **Source pages created** — count of files in `.repo-wiki/sources/` after Phase 2
- **Module hit rate** — entities created vs. ground-truth module list (manually labelled — see "Ground truth" below)
- **Phase 2 commit budget consumed** — N/50
- **Phase 2 page budget consumed** — N/15

`ingest` (git mode, simulated 30-commit backlog):
- **Wall-clock time**
- **Source pages created** for the 30 commits
- **Architectural commit capture rate** — of N commits manually labelled "architectural", how many became dedicated source pages vs. log-only entries

`query` (3 fixed prompts per repo, run separately):
- **Verification triggered?** — which T-trigger fired (T1-T7)
- **src/ files read during verification** — count
- **Verification segment present in answer?** — yes/no
- **Answer cited file:line** — yes/no

### Ground truth

Each repo gets a manually-labelled `_ground-truth.md` (kept out of the repo's `.repo-wiki/`, stored in this BENCHMARK.md as inline tables) containing:
- Author-intended module list (from monorepo config / README structure / docs)
- 5 commits manually classified as "architectural" vs. "incremental" within the test ingest window
- 3 query prompts and a hand-written reference answer

Module hit rate = (entities matching ground-truth modules) / (ground-truth module count). Over-creation of stub entities for non-modules counts against precision separately.

### Reproducibility

Anyone can re-run this benchmark:

```bash
# 1. Clone the target repo at the pinned SHA (see "Test repos" below)
git clone <url> && cd <repo> && git checkout <sha>

# 2. Install repo-wiki via monkey-skills marketplace
# 3. Run the three skills in Claude Code, recording wall-clock between
#    invocation and completion
/repo-wiki:init
/repo-wiki:ingest      # after artificially resetting log.md to a SHA 30 commits back
/repo-wiki:query "<one of the 3 prompts below>"

# 4. Fill in the result row; PR the update
```

Wall-clock is measured by the operator using a stopwatch — there's no built-in instrumentation in v1.1. v1.2+ may add timing emit; for now manual is the contract.

## Test repos

Five public repos chosen for size + language + structure diversity. Pinned SHAs let any future run reproduce against identical state.

| Repo | Language | Files (src) | Pinned SHA | Why chosen |
|---|---|---|---|---|
| [tiangolo/fastapi](https://github.com/tiangolo/fastapi) | Python | ~1,200 | `TBD — pin at first run` | Mid-size, single-package, well-documented modules — easy ground truth |
| [hono](https://github.com/honojs/hono) | TypeScript | ~600 | `TBD` | Small monorepo (`packages/*`), TypeScript path aliases, tests core PR 2 |
| [grafana/loki](https://github.com/grafana/loki) | Go | ~3,500 | `TBD` | Go modules, deep `cmd/` + `pkg/` split, tests Phase 1 entry-point detection |
| [rails/rails](https://github.com/rails/rails) | Ruby | ~5,500 | `TBD` | Classic monorepo with `railties/`, `activerecord/` etc.; tests author-declared boundaries |
| [signalapp/Signal-Android](https://github.com/signalapp/Signal-Android) | Kotlin/Java | ~5,000 | `TBD` | Large mobile codebase, gradle multi-module, stress-tests Phase 2 budget |

Selection rationale:
- **Avoid SourceAtlas's exact list** to prevent overfitting commentary
- **Cover ≥4 languages** to surface language-specific Phase 1 detection bugs
- **Include 2 monorepo-shaped projects** (hono, rails) since PR 2 explicitly targets author-declared boundaries
- **One large repo** (Signal-Android) to verify Phase 2 budget caps trigger as designed

## Results — v1.1.0 baseline

### init (default mode)

| Repo | Wall-clock | Entities | Source pages | Module hit rate | Phase 2 commits / 50 | Phase 2 pages / 15 |
|---|---|---|---|---|---|---|
| fastapi | TBD | TBD | TBD | TBD | TBD | TBD |
| hono | TBD | TBD | TBD | TBD | TBD | TBD |
| loki | TBD | TBD | TBD | TBD | TBD | TBD |
| rails | TBD | TBD | TBD | TBD | TBD | TBD |
| Signal-Android | TBD | TBD | TBD | TBD | TBD | TBD |

### ingest (git mode, 30-commit synthetic backlog)

| Repo | Wall-clock | Source pages | Architectural capture rate |
|---|---|---|---|
| fastapi | TBD | TBD | TBD |
| hono | TBD | TBD | TBD |
| loki | TBD | TBD | TBD |
| rails | TBD | TBD | TBD |
| Signal-Android | TBD | TBD | TBD |

### query (3 prompts per repo)

Prompts and reference answers live in **Appendix A** below. This table summarises behavior:

| Repo | Prompt # | Trigger fired | src/ files read | Verified segment? | Cited file:line? |
|---|---|---|---|---|---|
| fastapi | 1 | TBD | TBD | TBD | TBD |
| fastapi | 2 | TBD | TBD | TBD | TBD |
| fastapi | 3 | TBD | TBD | TBD | TBD |
| _(rows for other 4 repos × 3 prompts each — 12 rows)_ | | | | | |

## Results — v1.2.0 (PR 1 + PR 2 + PR 3 landed)

_Not yet run. Each v1.2 PR appends its own delta column to the relevant table above and explains the delta in its CHANGELOG entry._

Expected deltas after each PR:

- **PR 1 (query scan-budget)**: `src/ files read` capped at `min(10, 5% of loaded entity paths)`; new `## Verification Coverage` line in segmented answers
- **PR 2 (init high-entropy pre-scan)**: `Module hit rate` improves on hono + rails (the two monorepos with explicit author declarations); `Entities` count may go down (fewer false-positive stubs)
- **PR 3 (ingest entropy-weighted)**: `Architectural capture rate` improves on the 30-commit backlog test, especially for repos where a config-touching commit landed mid-window

## Appendix A — Query prompts and reference answers

Three categories per repo (always-the-same per repo so reruns compare apples-to-apples):

1. **Decision question** ("Why does X work this way?") — should NOT trigger verification (T6 negative)
2. **Current-state question** ("How does X currently handle Y?") — SHOULD trigger T2
3. **New-code question** ("I'm adding Z, where should it go?") — SHOULD trigger T3

| Repo | Prompt 1 (decision) | Prompt 2 (current-state) | Prompt 3 (new-code) |
|---|---|---|---|
| fastapi | TBD | TBD | TBD |
| hono | TBD | TBD | TBD |
| loki | TBD | TBD | TBD |
| rails | TBD | TBD | TBD |
| Signal-Android | TBD | TBD | TBD |

Reference answers (1-2 paragraphs each) are filled when the operator runs the prompt manually against the unaided codebase, then sealed before re-running through `/repo-wiki:query`. The reference is the comparison baseline for the query's segmented output.

## Appendix B — Limitations

- **Wall-clock is observer-dependent** until v1.2 adds emit-side timing. Treat times as ±20% accurate.
- **Module hit rate uses author-declared boundaries** as ground truth. Repos without monorepo configs (fastapi, loki) rely on README structure + docs site navigation as the boundary source — judgment call documented per-repo.
- **Architectural capture is hand-labelled** by the operator at benchmark time. Two operators may disagree on borderline commits; flag those in PR review.
- **Query reference answers are operator-written.** They reflect "what a careful human reads from the codebase", not absolute truth. Discrepancies between query and reference go in the PR description for review.
