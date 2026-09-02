# Git-based memory for AI agents & teams — viewpoints and a head-to-head comparison

**Date:** 2026-07-16 · **Method:** deep-deep-research pipeline (6 angles → 17 sources fetched → 79 claims → top-25 ranked → adversarial verify: 19 fact claims × 3 refutation voters, 6 opinion claims × attribution; 24/25 survived). Confidence tags follow the pipeline's calibration rules (a finding's confidence = its weakest load-bearing claim; vendor self-reported numbers capped at medium; single-source/one-voter-refuted capped at low). EN + JA sources.

## Summary (calibrated)

The debate is **not** "git vs. not-git" — it splits by **which git-based variant** and **which quality dimension**. Two evidence-backed conclusions hold with **medium-high** confidence: (1) the field is converging on **git-versioned in-repo files** (not commit-message trailers) as the durable substrate, and (2) git-native memory is **state-of-the-art for durability/portability/auditability/zero-infra but a measured liability for retrieval quality and staleness**. Everything past that (which alternative wins, by how much) is **contested** — the comparison numbers are largely vendor-self-reported and mutually disputed, so they are reported as claims-by-source, not settled facts.

## 1. The viewpoint landscape

### Git-native — the case FOR (proponents)
- **Commit-trailer decision records (Lore, arXiv:2603.15566).** Standard commits keep the diff but discard the "Decision Shadow" — constraints, rejected alternatives, forward context; Lore encodes these as native git trailers, **queryable via a CLI with zero infra beyond git, discoverable by any shell-capable agent.** *Confidence: medium — the paper is a protocol spec + comparative argument, not an empirical study (no benchmark numbers).*
- **Git-as-versioned-filesystem (GCC, arXiv:2508.00031).** Applies COMMIT/BRANCH/MERGE/CONTEXT to agent memory as a versioned FS (checkpointing, branch-explore, hierarchical retrieval). Claims **>13% over long-context baselines and >80% on SWE-Bench Verified, beating 26 systems.** *Confidence: LOW on the numbers — single-source, self-reported; an adversarial voter found no independent leaderboard listing or third-party reproduction. The architecture claim (medium) is separable from the unverified numbers.*
- **Practitioner git-native patterns** (JA: orphan branches + worktrees + Entire CLI storing agent sessions as git commits) show the pattern being replicated beyond the papers.

### Git-native — the case AGAINST (skeptics, the strongest evidence in this study)
- **Lexical git retrieval is measurably weak (CommitDistill, arXiv:2605.18284, Microsoft).** On a budget-constrained retrieval benchmark, naive **`git log --grep` scored 0.083 vs BM25 0.333 vs a distilled layer 0.750** — concrete evidence that keyword git-history search alone is a poor memory mechanism. Sharper still: **no retrieval condition (including the authors' own) beat a no-retrieval control** on 200 downstream bug-fixes — better retrieval didn't translate to better outcomes. *Confidence: medium-high (primary paper, PDF-verified).*
- **Static decision records decay structurally, not culturally (JavaCodeGeeks, 2026).** ADRs are point-in-time; **stale docs are worse than none** (false confidence); the update burden falls on whoever has the *least* context; org/team boundaries drift faster than records (Conway's Law). *Confidence: medium (opinion, single high-quality source, attribution confirmed).*
- **Zombie records cost real time (JA, zenn/miyan).** A decision overturned but never marked `Superseded` caused a real incident costing **~2 weeks of rework.** *Confidence: medium.*
- **Squash merge is mechanically lossy (Tyler Cipriani).** Collapses the granular decision trail — the exact fragility loom hit in PR #574. *Confidence: medium.*
- **Size threshold (JA):** ADRs / decision records are the wrong tool for 1–2-person projects — the premise (communicate a decision to *others* later) doesn't hold. *This is the one clear EN/JA nuance: JA sources consistently name a project-size floor below which git-commit-messages-alone suffice; EN sources understate it.*

### Graduation / hybrid (where git-native goes at scale)
- **rac-core (the shipped product of the Lore lineage)** stores decisions as **typed Markdown in git with YAML frontmatter**, enforces quality **pre-merge via CI (`rac validate` / `rac gate`)**, is **air-gapped (no LLM/network calls → deterministic retrieval)**, and is **served read-only over MCP.** The maintainers' explicit thesis: **"a simple git-native store works for individual use, but teams need enforcement"** — the graduation threshold, stated. *Confidence: medium-high (maintainer repo, design directly inspectable).*
- The general "**Markdown files vs MCP servers**" argument (thenewstack): loading one MCP server's tool schema costs **~23k–50k tokens**; a dozen at enterprise scale **200k–400k tokens** before any work — a concrete cost reason to keep stable knowledge in in-repo files, not served tools.

## 2. Head-to-head comparison

Confidence in the *numbers* below is low-medium: most are vendor-self-reported and several are mutually contradicted (see §3). Read the **shape** of the trade-off, not the decimal.

| Dimension | Git-native (files + trailers) | Vector store (Mem0) | Temporal KG (Zep/Graphiti) | Managed/tiered (Copilot Memory, MemGPT) | Always-loaded file (single MEMORY.md) |
|---|---|---|---|---|---|
| Durability / portability | ★★★ travels with clone, no infra | ★ needs DB | ★ needs graph DB | ★ vendor-hosted, per-user | ★★★ but see cost |
| Retrieval quality | ★ lexical/grep weak (0.083 vs 0.75) | ★★★ semantic | ★★★ semantic + temporal | ★★★ managed | ★ no retrieval, dumps all |
| Staleness / supersession | ✗ manual only (zombie ADRs) | ~ similarity-supersede | ★★★ bitemporal invalidation | ★★★ citation-validation + 28-day decay | ✗ decays silently |
| Token / latency cost | ★★★ pull, cheap | ★★ (self-reported 91% ↓p95, >90% tokens vs full-context) | ★★ (self-reported −90% latency) | ★★ managed | ✗ inflates every turn |
| Scale ceiling (solo→org) | solo–small team | team–org | team–org | org (vendor) | solo only |
| Infra dependency | none (git) | vector DB | graph DB | vendor service | none |
| Multi-agent / cross-tool | ★★★ any git reader | via API/MCP | via API/MCP | ★★ one vendor's tools | ★★★ any reader |
| Auditability / review | ★★★ diff-reviewable in PR | ✗ opaque store | ~ graph inspectable | ✗ vendor store | ★★★ diff-reviewable |
| **State-of-the-art at** | durability, audit, zero-infra | semantic recall | temporal/staleness recall | auto-invalidation, cross-tool | nothing (anti-pattern) |
| **Liability at** | retrieval quality, staleness | infra, opacity, cost | infra, opacity | lock-in, per-vendor scope | preload degradation |

**The cost/accuracy nuance that reframes "pull > push" (arXiv:2603.04814, primary):** fact-based memory (Mem0) becomes **cheaper than long-context beyond ~100k tokens** (compresses ~101,600 tokens → ~2,909 retrieved, ~35:1) — but **long-context still beat memory on raw accuracy by 35.2 points on LoCoMo.** So on-demand retrieval is a **cost/scale** win, **not** universally an accuracy win. "Pull > push" is a cost thesis, not an accuracy law.

## 3. Contested / unresolved (reported as tension, not smoothed)

- **The benchmark numbers are vendor-vs-vendor and don't reconcile.** Zep's paper claims DMR 94.8% (vs MemGPT 93.4%) and LongMemEval +18.5%/−90% latency; Mem0's paper claims LOCOMO +26% vs OpenAI and 91%↓p95/>90% tokens. An **independent** eval (Vectorize) put **Zep 63.8% vs Mem0 49.0%** on LongMemEval — **but Vectorize sells a competing product (Hindsight) and rates its own at 94.6%.** Every headline number here has a conflict of interest. **Do not adopt any single benchmark as decisive.**
- **EN/JA nuance:** JA practitioner sources consistently add a **project-size floor** (commit-messages suffice below ~3 people / short-lived projects) and a **"write-gate matters more than retrieval"** design stance (select what enters memory; metadata quality > vector implementation) that EN sources underweight.

## 4. When git-native memory is the RIGHT choice (evidence-backed conditions)

- **Choose git-native FILES (not commit trailers) when:** the knowledge is durable/decision-shaped, the team is solo–small, portability/auditability/zero-infra matter, and retrieval is navigational (you know roughly where to look) rather than fuzzy-semantic. This is the field-converged default (ADRs, Cline memory-bank, Cursor rules, GCC).
- **Keep commit trailers only as a low-friction *capture* point, never the durable store** — lexical grep is measurably weak (0.083) and squash is lossy. Graduate durable lessons into files.
- **Add CI enforcement (rac-style `validate`/`gate`) when you cross into a team** — the maintainer-stated threshold; individual git-native + team CI-enforcement.
- **Add semantic retrieval (vector/graph) only when** the store outgrows keyword search AND you can absorb infra + opacity; treat the vendor benchmarks as contested.
- **The one gap git-native must actively close is staleness** — this is where it measurably trails Copilot Memory (citation-validation + 28-day decay) and Zep (bitemporal invalidation). A `Supersedes:` discipline + a validation pass is the in-family answer; automatic decay/invalidation is the industry-leading answer.

## Caveats
- Most comparison numbers are vendor-self-reported and mutually disputed (§3) — confidence in any single figure is low; confidence in the *direction* of trade-offs is medium-high.
- GCC's SWE-Bench numbers did not survive adversarial scrutiny for independent reproduction (treated as unverified).
- 24/25 ranked claims survived verification; the one killed claim was the MemGPT "OS analogy" framing (an unconfirmed interpretive stance, not a factual loss).
- The top-25 ranking over-weighted high-source-quality official docs (Copilot/MemGPT); the sharper comparison/skeptic claims were pulled from the wider pool and are labeled with their (often single-source) confidence.

## Sources (primary-first)
Lore arXiv:2603.15566 · GCC arXiv:2508.00031 · CommitDistill arXiv:2605.18284 · MemGPT arXiv:2310.08560 · Zep arXiv:2501.13956 · Mem0 arXiv:2504.19413 · "Beyond the Context Window" arXiv:2603.04814 · GitHub Copilot Memory docs + 2026-03-04 changelog · rac-core (github.com/itsthelore/rac-core) · JavaCodeGeeks ADR-staleness (2026-05) · Tyler Cipriani "Git squash is not nice history" · thenewstack "Markdown files vs MCP" · JA: zenn/miyan ADR for-and-against, zenn/proper_willet two-tier memory, Vectorize mem0-vs-zep (conflict-of-interest noted).
