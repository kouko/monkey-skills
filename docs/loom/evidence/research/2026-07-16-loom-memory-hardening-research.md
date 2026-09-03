# loom memory mechanism — hardening research + options

**Date:** 2026-07-16 · **Trigger:** PR #574's squash merge left the commit-trailer carrier un-retrievable (`memory-grep --verify HEAD` → exit 4) despite a pre-push gate passing; the lesson survived only because the `docs/loom/memory/` file store landed on main. This is the 2nd recurrence of the `gotcha_pr_body_squash_memory_needs_raw_trailer_footer_too` memory. Research: 4 parallel EN+JA web scans, then loom-specific options.

**Update 2026-07-16 (deep-dive):** a full deep-deep-research pass on git-based memory now backs two of the options below with harder evidence — see `2026-07-16-git-based-memory-viewpoints-and-comparison.md`. Net effect: **O4 is now evidence-grounded (not just doctrine)** and **O6 is upgraded from "deferred" to a recognized strategic gap** (see the revised entries + recommendation).

## Industry findings (cited)

### A. Decision-record storage (ADRs)
- **In-repo markdown files dominate** (`docs/adr/NNNN-title.md`) — co-located PR review, version-controlled history, survives wiki/DB rot. Commit-message-only is explicitly called out as **not browsable/indexable enough** for decision retrieval. (EN: adr.github.io, AWS Arch Blog)
- Standard = numbered files + YAML status lifecycle (proposed→accepted→superseded) + **generated index** (Log4brains auto-builds a searchable site; MADR = de-facto template). (EN: adr/madr, thomvaill/log4brains)
- Failure modes: orphaned ownership, **missing supersession** (new decision ships without marking the old one invalid), and 形骸化 — recording everything until it's noise. Survivors keep scope to *costly-to-reverse* decisions + an owner + supersession links. (EN: rickpollick; JA: qiita/making111, zenn/miyan — JA adds "documentation culture is a precondition")

### B. Git metadata durability across squash
- squash does **not** relocate per-commit trailers intelligently; `PR_BODY` mode preserves the PR description **as plain text** (parseable only if it's already a raw trailer block), `COMMIT_MESSAGES` scatters them, `BLANK` drops all. (EN: github.blog changelog, community/16271)
- Even DCO `Signed-off-by` (the most battle-tested must-survive trailer) is **bypassable at squash** — bots skip, humans delete the textbox lines. (EN: dcoapp/app #126)
- `git log --grep` (fulltext, formatting-fragile) ≠ `%(trailers)`/`interpret-trailers --parse` (needs blank-line separator + density). Community: **don't hand-roll a trailer regex.** (EN: git-scm, alchemists.io)
- Preservation practice: `PR_BODY` mode **+ a PR template that pre-seeds a raw trailer footer** + CI re-checks the final squash commit, or use rebase-merge for trailer-reliant repos.

### C. AI-agent memory architectures (2024–2026)
- Substrates: Letta (tiered core+vector), Mem0 (vector+graph+KV), Zep/Graphiti (bitemporal KG), **Cline memory-bank (committed markdown files), Cursor .cursorrules (in git), GCC (git-like versioned FS, +13% SWE-Bench), Lore/rac (git commit trailers, log-queryable, declines superseded)**. (arxiv 2508.00031; 2603.15566)
- **Pull > push** consensus — preloading dilutes attention + inflates token cost; Mem0 reports ~91% latency / ~90% token savings vs full preload. A single always-loaded MEMORY.md must be an **index of pointers, not a data dump**, or it degrades. (EN+JA converge, no disagreement)
- Staleness handled automatically by leaders: Zep bitemporal invalidation, Mem0 similarity-supersede, Copilot Memory **28-day decay-unless-reused**.

### D. Enforcing + verifying records at merge
- Enforcement is **overwhelmingly pre-merge** (required status checks); PR templates alone are unenforced without a bot (danger.js body-grep, `github-pr-contains-action`). (EN)
- **Documented failure mode (both langs):** squash/rebase doesn't preserve the PR body by default → a pre-merge check validates an artifact that never lands. Open GitHub feature request, unresolved.
- **Post-merge validation pattern exists:** `pull_request_target` workflows validate the *constructed squash commit message* at merge time (check the artifact AFTER the transform); merge queues re-check post-merge context. (EN: zenn/wakamsha, aviator.co)

## loom's current design vs the field

**Verdict: loom already matches or leads the field on the big architectural choices.** File store (`docs/loom/memory/`) + pull retrieval + index-of-pointers = exactly the ADR/agent-memory consensus; git-native (Lore/GCC lineage) is arguably ahead of DB-heavy Mem0/Letta for a solo/small-team repo. The weaknesses are **specific and fixable, not architectural**:

| # | Weakness | Evidence |
|---|---|---|
| W1 | Commit-trailer carrier is fragile across squash — `## Memory` is bold markdown, not a raw trailer; repo is already `PR_BODY` mode but that only preserves text, not parseable trailers | PR #574 exit 4 |
| W2 | Verification is **pre-push only** — blind to the squash transform that runs later | pre-push gate passed, post-squash failed |
| W3 | No automatic staleness/supersede signal — only manual `loom-memory prune` | vs Zep/Mem0/Copilot auto-invalidation |
| W4 | `compose-pr` mandates the human-readable `## Memory` but **not** a raw trailer footer | grep of compose-pr.md |

## Strengthening options (tiered by cost × leverage)

- **O1 — PR_BODY squash mode.** ✅ Already set (`squash_message: PR_BODY`). Necessary but not sufficient (preserves text, not parseable trailers). No action.
- **O2 — [cheap, high leverage] Mechanize the raw trailer footer.** compose-pr.md must require a memory-worthy PR body to END with a blank-line-separated raw block (`Decision: …` / `Learning: …` / `Gotcha: …`, unbolded) in addition to the pretty `## Memory` section. Under PR_BODY mode this lands verbatim + `%(trailers)`-parseable on the squash commit. Mechanizes the gotcha that has now been forgotten twice. (grounding: B)
- **O3 — [medium, closes W2] Post-merge verification.** A GitHub Action on push-to-main that re-runs `%(trailers)`/memory-grep on the ACTUAL squash commit and fails/alerts if a memory-worthy PR landed empty. Survives human merges, not just Claude close-outs; + keep the manual `--verify HEAD` in finishing as the Claude-path fallback. (grounding: D — pull_request_target / merge-queue re-check)
- **O4 — [cheap, addresses W1 at the root, NOW EVIDENCE-BACKED] File store = authoritative; demote trailer-grep.** Make the charter explicit: durable practices/gotchas/processes live in `docs/loom/memory/` (a normal committed file — squash-proof, format-proof, the carrier that survived #574). Commit trailers are commit-BOUND decision capture, best-effort/secondary for durable lessons; never depend on trailer retrieval to recover a durable lesson. **Hard evidence (deep-dive):** CommitDistill (arXiv:2605.18284) measured naive `git log --grep` retrieval at **0.083** vs BM25 0.333 vs a distilled layer 0.750 — lexical commit-history search is a *measurably* weak memory mechanism, not just a squash-fragility inconvenience; and the field (ADRs, Cline memory-bank, Cursor rules, GCC) has converged on git-versioned **files** over commit-message metadata. This elevates O4 from "make the doctrine explicit" to "the retrieval-quality evidence says the file store must be the authoritative path, period."
- **O5 — [cheap, correctness] Retrieve with the git parser, not a regex.** Use `interpret-trailers --parse` / `%(trailers)` for structured repos; on squash rely on O2's raw footer or O4's file store, never fragile `--grep`. (grounding: B)
- **O6 — [UPGRADED: strategic gap, schedule it] Staleness/supersede signal.** loom's only mechanism is manual prune. **Deep-dive evidence reframes this from "defer" to "the industry-recognized primary weakness of git-native memory":** a "zombie ADR" (decision overturned but never marked `Superseded`) cost a real team **~2 weeks of rework** (zenn); the leaders solve it automatically — GitHub Copilot Memory validates each fact's citation against the current branch AND decays unused entries after **28 days**; Zep uses **bitemporal invalidation**. Cheapest in-family fix (no vector/graph infra): enforce a `Supersedes:` link when a new entry contradicts an old one (loom already has the concept — enforce it), + optionally a validation pass / periodic prune-cadence reminder. Still NOT what bit us in #574 (that was W1/W2), so it is not the *incident* fix — but it is now the *strategic* gap to schedule, not indefinitely defer. (grounding: A + C + deep-dive §1 skeptics / §4 staleness)

## Recommendation

The incident was **W1 + W2**. Highest value, most grounded, cheapest:
1. **O4** (file-store authoritative — now evidence-backed, not just doctrine) — the deep-dive's `git log --grep` = 0.083 retrieval score makes this the load-bearing conclusion: the file store MUST be the authoritative durable-lesson path; trailer-grep is a measurably weak retrieval mechanism, not a fallback to lean on.
2. **O2** (mechanical raw footer) — cheap, stops the twice-recurred gotcha, makes the trailer carrier (the *capture* point) at least survive squash.
3. **O3** (post-merge CI) — defense-in-depth so a human merge can't silently drop it.
4. **O5** rides along with O2/O3 (correctness).
5. **O6** (staleness/supersede) — **upgraded from "deferred" to "scheduled strategic gap":** the evidence (zombie-ADR 2-week cost; Copilot citation-validation + 28-day decay; Zep bitemporal) names this as git-native memory's recognized #1 weakness. Not the #574 incident fix, but no longer indefinitely deferred — do it after O2–O4.

**New (deep-dive) — O7: graduation threshold.** rac-core's maintainer thesis — "git-native works for individual use, teams need enforcement" — gives loom an explicit scaling signal: while the store is effectively single-maintainer, files + pull is correct; if `docs/loom/memory/` ever crosses to multiple concurrent contributors, add CI-enforced schema/status (rac-style `validate`/`gate`) BEFORE reaching for a served/DB store. Watch the threshold, don't pre-build.

Each is a separate implementable change (via loom-code); this doc is research + options only, no implementation. Evidence base: `2026-07-16-git-based-memory-viewpoints-and-comparison.md`.
