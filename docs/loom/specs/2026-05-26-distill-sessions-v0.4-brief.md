# distill-sessions v0.4 — brainstorming brief

> **Status**: 5-axis exploration complete. Locks v0.4 scope (Finding #1 context overflow — **A' Sonnet-1M-only radical simplification**). Reverses the inline Haiku-only model lock from v0.1 brief §172 + [SKILL.md L414-417](../../../dev-workflow/skills/distill-sessions/SKILL.md#L414-L417). Ready for [`code-toolkit:writing-plans`](../../../code-toolkit/skills/writing-plans/SKILL.md).
>
> **Author**: kouko + Claude session, 2026-05-26.
>
> **Consumes**:
> - [`2026-05-22-skill-log-mining-v0.1-brief.md`](2026-05-22-skill-log-mining-v0.1-brief.md) — parent brief (Q1, Q3-Q6 still apply; the inline Haiku-only model lock is what v0.4 reverses)
> - [`2026-05-25-distill-sessions-v0.3-brief.md`](2026-05-25-distill-sessions-v0.3-brief.md) — predecessor brief (§Alternatives Considered Finding #1 enumerated the 5 industry options surveyed; this brief picks from that menu + 2 new freshness options + 1 complexity-critique candidate)
> - [`distill-sessions-v0-3-post-ship-dogfood`](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_3_post_ship_dogfood.md) memory — overflow rate 7/12 = 58%, top overflow 559K = 3× Haiku cap
> - [`distill-sessions-v0-1-first-real-dogfood`](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_1_first_real_dogfood.md) memory — earlier overflow rate 4/5 = 80% (different dataset)
>
> **Produces**: structured v0.4 brief consumed by `writing-plans` to split into ~3-5 atomic tasks (small because architecture is ~5 LOC + cascade documentation updates).

---

## Problem

**JTBD (Klement format)**: *When I dogfood `dev-workflow:distill-sessions` against real multi-hour `code-toolkit:*` sessions, I want every dispatched trajectory analyzed in full — not have the 58% of sessions that overflow Haiku's 200K cap silently skipped — so the Memory Items output reflects the full dataset (especially the longest = messiest = highest-friction sessions that are the most learning-rich), and Stage 4 cluster's N≥2 promotion has enough survived candidates to actually fire (not always fall through to §Cross-session evidence pending).*

The v0.3 post-ship dogfood quantified the cost of the current "skip + warn" floor: **7/12 trajectories overflowed** (top overflow 559K = 3× cap). The skipped sessions are systematically the longest, which correlates with highest friction count, which is exactly the signal distill-sessions is built to surface. The Stage 4 cluster N≥2 promotion shipped in v0.3 also degrades silently: with 5/12 fit-trajectories spread across multiple target skills, no skill accumulated N≥2 items in the dogfood run — all 15 items routed to §pending bucket. Fix overflow → unlock Stage 4 promotion as a second-order effect.

## Users

Primary user is still **kouko as skill maintainer** running `/distill-sessions` after multi-PR `code-toolkit:*` cycles. v0.4-specific constraint surfaced during this brainstorm:

- **Cadence locked: 2-5×/week** (post-PR cycle). Cost-sensitive but not extreme; ~$20-60/month at 3× Sonnet 1M pricing is acceptable as ship-cost-of-doing-business.
- Operator workflow unchanged: preview at orchestrator → confirm → SDD dispatch via Agent tool. v0.4 only changes the model literal embedded in each dispatch entry.

Secondary user (other monkey-skills users at v0.5+) and tertiary user (cross-agent at v1.0+) inherit v0.1 brief unchanged.

## Smallest End State

**One paragraph**: After v0.4 ships, `_build_subagent_entries` populates `subagent_payload[].model` with `claude-sonnet-4-6` (1M-context standard) instead of `claude-haiku-4-5-20251001`. The SKILL.md bare-invocation protocol's "context overflow → skip + warn" block updates to reflect the new 1M cap (overflow now only fires for trajectories >1M tokens — a theoretical floor that the v0.3 dataset never approached; max observed was 559K). The `HAIKU_MODEL_ID` constant in [`scripts/main.py:55-56`](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L55-L56) renames to `SUBAGENT_MODEL_ID` (no functional code change beyond the literal value). All existing tests that assert on the model literal in payload entries update to expect the Sonnet ID. **Coverage rises from 5/12 → 12/12** on the same dogfood dataset. Stage 4 cluster N≥2 candidates rise accordingly; some items previously stuck in §pending bucket get promoted on next v0.4 dogfood run.

### What v0.4 does NOT touch

- **Sliding-window curation around friction markers** — eliminated in Axis 3 (over-engineering for the actual cost delta; see §Alternatives Considered).
- **Tier-fallback dispatcher** (Haiku-then-Sonnet logic) — eliminated for same reason; flat Sonnet is simpler.
- **Map-reduce chunked Haiku** — eliminated; cross-chunk friction-pattern fragmentation risk doesn't justify saving 3× cost at this cadence.
- **Prompt caching for repeated content** (target SKILL.md content + agent role prompt are identical across the N subagents in a single run) — flagged as Open Question for v0.4.1 if cost exceeds budget under real cadence.
- **Batch API for async dispatch** (50% Anthropic batch discount) — Agent tool dispatch shape is sync; would require orchestrator-pattern rework. Defer to v0.5+ if cost becomes binding.
- **Operator `--model haiku` override flag** for known-fits runs — YAGNI; users can override at orchestration time per existing SKILL.md L414-417 pattern.
- **Friction event position distribution probe** (would have informed sliding-window calibration) — moot since Architecture A' doesn't need windowing.
- **Stage 4 semantic clustering** — still v0.5+ per v0.3 brief Finding #5 #2 (embedding-based; deferred until title+anchor proves insufficient).
- **References file write-back** — still `false` per v0.1 Q4 (SKILL.md only).
- **`apply.py --approved` gate** — unchanged.

## Current State Evidence

Verified 2026-05-26 against `main` (commit `fc220a0c`, post-v0.3 trilogy + v2.7.1 hotfix).

| Dimension | Path / file:line | What's there |
|---|---|---|
| **Forward** (model literal definition) | [`scripts/main.py:55-56`](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L55-L56) `HAIKU_MODEL_ID = "claude-haiku-4-5-20251001"` with comment "Locked Haiku model literal for per-trajectory subagent dispatch." | Rename to `SUBAGENT_MODEL_ID` + replace value with Sonnet 4.6 literal. Update comment to reflect why (1M context > Haiku 200K; see this brief). |
| **Forward** (payload emitter) | [`scripts/main.py:320`](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L320) `"model": HAIKU_MODEL_ID,` inside `_build_subagent_entries` | One-token reference update if the rename happens; otherwise just literal value change. |
| **Reverse** (callers + tests) | `grep -rn HAIKU_MODEL_ID dev-workflow/skills/distill-sessions/scripts/` → [main.py:55,320] + test_main.py + test_main_e2e.py assertions | Tests that hardcode the Haiku literal need flipping to Sonnet. ~5-10 assertion sites estimated; grep at plan time for exact count. |
| **Error** (skip+warn floor doc) | [SKILL.md L78-90](../../../dev-workflow/skills/distill-sessions/SKILL.md#L78-L90) bare-invocation protocol "context overflow → skip + warn" | Update prose: 200K → 1M cap; reframe overflow as theoretical floor (max observed 559K in v0.3 dogfood). |
| **Error** (locked Haiku model literal doc) | [SKILL.md L414-417](../../../dev-workflow/skills/distill-sessions/SKILL.md#L414-L417) §"Locked Haiku model literal" — explicitly anticipates v0.4 swap | Replace the §Future block with §Operating notes describing the v0.4 model choice + cost note. |
| **Data** (overflow evidence) | [`memory/project_distill_sessions_v0_3_post_ship_dogfood.md:48-59`](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_3_post_ship_dogfood.md) — 7/12 = 58% overflow table | Use as v0.4 dogfood baseline: re-run same skills should produce 12/12 = 100% coverage. |
| **Boundary** (SKILL.md prose driving dispatch) | [SKILL.md L142-155](../../../dev-workflow/skills/distill-sessions/SKILL.md#L142-L155) Pipeline diagram lines "model: claude-haiku-4-5-20251001" | ASCII diagram literal updates to Sonnet. |
| **Boundary** (v0.1 brief inline model note) | [`2026-05-22-skill-log-mining-v0.1-brief.md` §172](2026-05-22-skill-log-mining-v0.1-brief.md) "Lean Haiku + Sonnet. Defer." | Historical record; don't edit. v0.4 brief is the structured reversal as anticipated. |

**Evidence paths appendix**:
- `dev-workflow/skills/distill-sessions/scripts/main.py` (569 LOC; the entire file is small enough to audit; only ~3-5 lines change)
- `dev-workflow/skills/distill-sessions/SKILL.md` (509 lines; ~3 prose blocks update)
- `dev-workflow/skills/distill-sessions/scripts/test_main.py` + `test_main_e2e.py` (~5-10 assertion updates)
- v0.3 dogfood overflow table = quantitative baseline for v0.4 acceptance test

## Decision

**Build `dev-workflow:distill-sessions` v0.4** covering Finding #1 context overflow via **Architecture A' (Sonnet-4.6 1M-context only)**. Replace the Haiku model literal in `_build_subagent_entries` payload + update SKILL.md + tests + ASCII diagrams. ~5 LOC functional change + ~30-40 LOC documentation/test updates. v0.1 Q1 (stdlib-only) preserved. v0.1 Q3-Q6 preserved. v0.3 features (cross-skill routing, Stage 4 cluster, dual-dispatch, target-filter) preserved.

**Lock**: A' over A (sliding-window + Sonnet tier-fallback) over B (chunked Haiku). The complexity-critique math wins: 5 LOC trumps 80-120 LOC trumps 150-200 LOC at the same coverage outcome, and the 3× cost premium ($20-60/month at locked cadence) is small enough that it doesn't pay for the engineering work to optimize it. The brief's predecessor "my take" (A) was correct as a research finding but loses to A' under complexity-critique once the dogfood quantified cadence and the freshness check confirmed Sonnet 1M at standard pricing (no premium tier).

### Locked Q-decisions for v0.4

**Q-v0.4-1 — Subagent model: Haiku locked / Sonnet 1M / per-tier / operator-choice?**
- A. Haiku 4.5 locked (status quo from v0.1)
- **B. Sonnet 4.6 1M-context (chosen)** — covers all observed trajectory sizes (max 559K vs 1M cap); flat 3× cost acceptable at locked cadence
- C. Per-tier (Haiku for fit, Sonnet for overflow) — A from §Alternatives Considered; eliminated for engineering cost vs marginal $ savings
- D. Operator-choice flag — YAGNI

**Why B**: 100% coverage at ~5 LOC ship cost; sidesteps window-size calibration; sidesteps tier-dispatcher logic; unlocks Stage 4 cluster N≥2 promotion as second-order win. The 3× per-token cost premium × ~$3-10/run × 2-5 runs/week = ~$20-60/month is acceptable cost-of-doing-business for the operator-experience win.

**Q-v0.4-2 — Constant name: `HAIKU_MODEL_ID` keep or rename?**
- A. Keep `HAIKU_MODEL_ID` (misleading post-v0.4 but minimal diff)
- **B. Rename to `SUBAGENT_MODEL_ID` (chosen)** — accurate; one-token diff in caller; cheap to do at the same time
- C. Rename to `SONNET_MODEL_ID` (still model-specific; future model change would re-rename)

**Why B**: future-proof for v0.5+ if model changes again; small additional cost; ergonomic clarity for readers.

**Q-v0.4-3 — Prompt caching for `target_skill_md_content`?**
- A. Add `cache_control` to the cached portion of the payload (~10-20% input cost reduction)
- **B. Defer (chosen)** — Agent tool dispatch shape needs verification for cache_control passthrough; v0.4 is a 5-LOC ship; cost reduction is below the engineering threshold
- C. Add to v0.5 backlog explicitly

**Why B**: Out of scope for v0.4 minimum ship. Lands as Open Question for v0.4.1 if real cadence cost exceeds the $60/month estimate.

**Q-v0.4-4 — Test strategy for 1M-context capability?**
- A. Real Sonnet 1M-context smoke test in CI (~$0.30 per CI run; non-zero ongoing cost)
- **B. Unit-test model literal in payload + manual dogfood validation (chosen)** — same pattern as v0.1+v0.2+v0.3
- C. Mock the Agent tool dispatch + assert model literal threaded through

**Why B**: Consistent with existing test pattern; v0.4 isn't testing the model's capability (that's Anthropic's problem), it's testing that the right literal lands in the payload. Capability validation is the operator-dogfood step per v0.1 bare-invocation protocol.

## Out of Scope

- Sliding-window curation around friction markers (eliminated; over-engineering vs flat Sonnet)
- Tier-fallback dispatcher (eliminated; ditto)
- Map-reduce chunked Haiku (eliminated; cross-chunk pattern fragmentation risk)
- ACON guideline-optimized compression (newly surfaced in Axis 4 refresh; designed for multi-turn agent histories, over-engineered for one-shot transcript analysis)
- RLM recursive language models (over-engineered for N≈12 trajectories)
- Pre-summarize via cheaper model (collapses into Sonnet 1M because pass-1 itself needs to read 559K)
- Prompt caching (deferred to v0.4.1 if cost binds)
- Batch API async dispatch (deferred to v0.5+; Agent tool shape rework)
- Operator `--model haiku` override flag (YAGNI; existing SKILL.md L414-417 pattern preserved)
- Friction event position distribution probe (moot at A')
- Stage 4 semantic embedding clustering (still v0.5+ per v0.3 brief)
- Anthropic Claude API direct dispatch (instead of Agent tool) (v0.5+ if batch API ever lands)
- `~/.codex/sessions/*.jsonl` Codex adapter (v0.5+ per v0.1 §481)

## Alternatives Considered (research-grounded)

Per Axis 4 protocol — refresh WebSearch EN + JA on 2026-05-26 (1 day delta from v0.3 brief search).

### Freshness delta from v0.3 brief Finding #1 menu

| Topic | v0.3 brief 2026-05-25 | v0.4 refresh 2026-05-26 | Material change? |
|---|---|---|---|
| Haiku 4.5 long-context | 200K cap | Still 200K; no extended variant shipped | No |
| Sonnet 4.6 1M-context pricing | $3/$15 (3× Haiku), 1M context implied | **Confirmed: 1M at standard pricing, NO long-context premium tier**. Brief's premise holds; clarification on the no-tier point | Slight clarification (de-risks A') |
| Sliding-window pattern (JetBrains 2025-12) | Present | Still present, no displacing pattern | No |
| **NEW: ACON compression** | Not surfaced | arxiv 2510.00615 (2026-10) — guideline-optimized compression, 26-54% peak token reduction; designed for multi-turn agent histories | Adds Option 6; eliminated as over-engineered for one-shot transcript analysis |
| **NEW: Industry context-compaction patterns** | Not surfaced | morphllm Compact + general 2026 "Principle of Least Context" / map-reduce articles | Confirms B (chunked Haiku) is an industry pattern but not displacing for our use case |

### Candidate compression (5 brief options + 2 new + 1 complexity-critique → 3 real candidates)

| # | Approach | Source | Verdict |
|---|---|---|---|
| 1 | **Sliding-window around friction markers** | JetBrains 2025 (EN) | ❌ Eliminated. 80-120 LOC vs 5 LOC for A'; window-size needs calibration (no data); marginal cost savings (~$15-50/mo) below engineering threshold |
| 2 | **Sonnet 4.6 1M-context fallback** | Anthropic pricing 2026 (EN) | ✅ Promoted from "fallback" to "primary" (A'). Becomes the entire architecture; eliminates tier-dispatcher engineering |
| 3 | **Pre-summarize via cheaper model first** | LayerX 2025 (JA) | ❌ Eliminated. Pass-1 itself needs to read 559K → pass-1 needs Sonnet 1M anyway → collapses into A' |
| 4 | **Recursive Language Models (RLM)** | arxiv 2512.24601 (EN) | ❌ Eliminated (v0.3 verdict reaffirmed). Over-engineered for N≈12 trajectories |
| 5 | **Skip + warn** | n/a — v0.1 workaround | ❌ Eliminated as primary; preserved as theoretical floor for >1M trajectories (never observed in v0.3 dogfood, max 559K) |
| 6 | **ACON compression (NEW)** | arxiv 2510.00615 (EN), morphllm Compact (EN) | ❌ Eliminated. Designed for long-horizon multi-turn agents; guideline-optimization infrastructure is over-engineered for one-shot transcript analysis; 26-54% reduction is below the gap (3× = 200%+) |
| 7 | **Map-reduce chunked Haiku (NEW)** | morphllm Compact (EN), 2026 "Principle of Least Context" articles (EN) | ❌ Eliminated (option B in lock question). 150-200 LOC; cross-chunk friction-pattern fragmentation risk; N× per-call overhead vs 1× per-session at A' |
| 8 | **Sonnet-1M-only flat (NEW; complexity-critique)** | Derived from §dev-workflow:complexity-critique YAGNI default | ✅ **Chosen as A'**. 5 LOC vs 80-200 LOC at same 100% coverage. 3× cost premium acceptable at locked cadence. Reverses v0.1 inline Haiku-only lock as anticipated by SKILL.md L414-417 |

**Sources cited** (Axis 4 refresh — 2026-05-26):
- [Context windows — Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/context-windows) (EN) — Haiku 4.5 still 200K
- [Claude API Pricing 2026: Full Anthropic Cost Breakdown](https://www.metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration) (EN) — Sonnet 4.6 $3/$15 confirmed
- [Claude Sonnet 4.6 in Production: Capability, Safety, and Cost Explained — Caylent](https://caylent.com/blog/claude-sonnet-4-6-in-production-capability-safety-and-cost-explained) (EN) — 1M at standard pricing confirmed; no separate long-context premium
- [ACON: Optimizing Context Compression for Long-horizon LLM Agents — arxiv 2510.00615](https://arxiv.org/pdf/2510.00615) (EN) — 2026 compression baseline; not displacing
- [Compact — State-of-the-Art Context Compaction for AI Agents (morphllm)](https://www.morphllm.com/products/compact) (EN) — industry compaction productization
- [The Mental Framework for Unlocking Agentic Workflows — DEV Community](https://dev.to/somedood/the-mental-framework-for-unlocking-agentic-workflows-cg1) (EN) — Principle of Least Context discussion
- [AIエージェント実装完全ガイド2026 — Zenn](https://zenn.dev/ai_nexus/articles/ai-agents-design-patterns) (JA) — agent design patterns 2026 baseline
- [コンテキストエンジニアリング — Elasticsearch Labs](https://www.elastic.co/search-labs/jp/blog/context-engineering-llm-evolution-agentic-ai) (JA) — context-engineering as emerging discipline name
- [【2026年】LLMのコンテキストウィンドウとは？— 株式会社AX](https://a-x.inc/blog/llm-context-window/) (JA) — 2026 context-window comparison; confirms Sonnet 1M tier
- v0.3 brief's full citation list ([2026-05-25-distill-sessions-v0.3-brief.md §Sources cited](2026-05-25-distill-sessions-v0.3-brief.md)) carries over unchanged for the other 5 candidates surveyed

## What Becomes Obsolete

**Same-PR removal on v0.4 ship**:

- [`scripts/main.py:55-56`](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L55-L56) `HAIKU_MODEL_ID = "claude-haiku-4-5-20251001"` constant + comment "Locked Haiku model literal" → replaced with `SUBAGENT_MODEL_ID = "claude-sonnet-4-6"` (verify exact literal at plan time) + updated comment explaining v0.4 reversal
- [SKILL.md L414-417](../../../dev-workflow/skills/distill-sessions/SKILL.md#L414-L417) §"Locked Haiku model literal" §Future block → replace with §Operating notes describing v0.4 model choice + cost note + cadence assumption (2-5×/week post-PR cycle)
- [SKILL.md L78-90](../../../dev-workflow/skills/distill-sessions/SKILL.md#L78-L90) bare-invocation protocol "context overflow → skip + warn" 200K-cap prose → 1M-cap prose; reframe overflow as theoretical floor (max observed 559K)
- [SKILL.md L142-155](../../../dev-workflow/skills/distill-sessions/SKILL.md#L142-L155) ASCII pipeline diagram `model: claude-haiku-4-5-20251001` → Sonnet literal
- Test fixtures / assertions hardcoding `claude-haiku-4-5-20251001` literal (grep at plan time; ~5-10 sites expected in `test_main.py` + `test_main_e2e.py`)
- v0.3 §Future block reference "v0.4 brief: Finding #1 context overflow" → marked done; cross-link to this brief

**Becomes obsolete on v0.4 ship (NOT this brief but affected)**:

- [`memory/project_distill_sessions_v0_3_post_ship_dogfood.md` "Finding #1 context overflow — quantified" table](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_3_post_ship_dogfood.md) — the 7/12 overflow line becomes historical baseline; do not edit the memory (timeline integrity), but cross-link in next dogfood memory as "fixed at v0.4"
- v0.1 inline §172 "Lean Haiku + Sonnet. Defer." — historical record; don't edit. v0.4 brief is the structured reversal.

**Not obsoleted (intentional)**:

- v0.3 features (cross-skill routing / Stage 4 cluster / dual-dispatch / target-filter) — orthogonal; preserved
- v0.1 Q1 (stdlib-only) / Q3 (read-only) / Q4 (SKILL.md only) / Q5 (Q5-baked thresholds) / Q6 (within-run only) — all preserved
- Friction Signal detection — orthogonal
- §Cross-session evidence pending bucket — still relevant for genuinely unique titles (just gets less use as N≥2 promotion becomes more common)
- `apply.py --approved` gate — unchanged
- §Future block "Heading-extraction state machine" — orthogonal
- §Future block "v1.0 broad-scope `skill-log-mining` sibling" — orthogonal

## Open Questions

1. **Exact Sonnet 4.6 model literal**: `claude-sonnet-4-6` vs `claude-sonnet-4-6-<date>`? Anthropic's convention varies. Verify at plan time via Anthropic model docs OR existing `claude-api` skill references. v0.4 plan T1 grounds this.
2. **Cost monitoring**: should v0.4 add a stderr line `# estimated cost: ~$N at Sonnet 4.6 rates` to the orchestrator preview so operator sees the bill before confirming? Cheap to add (~5 LOC); pairs naturally with the model swap. Decide at plan time.
3. **v0.4.1 prompt-caching follow-up**: if real cadence post-ship pushes monthly cost above ~$60, revisit Q-v0.4-3 with cache_control passthrough verified for Agent tool dispatch. Pre-budget signal: monthly cost > $60 → file v0.4.1 brief.
4. **v0.5+ Stage 4 promotion verification**: after v0.4 ships, re-run the same v0.3 dogfood dataset; expect ≥1 cluster to fire on the writing-plans Memory Items (3d998518 + b4cb3d6e + a83bdc52 had semantically-related titles per [[distill-sessions-v0-3-post-ship-dogfood]]). If 0 clusters fire even at full 12/12 coverage, the title+anchor exact-match cluster mechanic is the next bottleneck (escalate to v0.5+ embedding clustering).
5. **Backward-compat consideration**: any caller code that imports `HAIKU_MODEL_ID` directly (not via the payload)? Grep at plan time; if 0 external references, free rename. If any external reference, decide rename vs alias-with-deprecation.

## Handoff to writing-plans

Input ready for [`code-toolkit:writing-plans`](../../../code-toolkit/skills/writing-plans/SKILL.md):

- **Brief**: this file (`docs/loom/specs/2026-05-26-distill-sessions-v0.4-brief.md`)
- **Predecessor brief**: [`2026-05-25-distill-sessions-v0.3-brief.md`](2026-05-25-distill-sessions-v0.3-brief.md) (v0.3 features preserved)
- **Parent brief**: [`2026-05-22-skill-log-mining-v0.1-brief.md`](2026-05-22-skill-log-mining-v0.1-brief.md) (Q1, Q3-Q6 still active; inline Haiku-only model lock reversed by this brief)
- **Touch points verified**: `HAIKU_MODEL_ID` constant ([main.py:55-56](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L55-L56)), payload emitter ([main.py:320](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L320)), SKILL.md prose blocks ([L78-90](../../../dev-workflow/skills/distill-sessions/SKILL.md#L78-L90), [L142-155](../../../dev-workflow/skills/distill-sessions/SKILL.md#L142-L155), [L414-417](../../../dev-workflow/skills/distill-sessions/SKILL.md#L414-L417)), test assertions (`grep HAIKU_MODEL_ID dev-workflow/skills/distill-sessions/scripts/test_*.py`)
- **Dogfood baseline**: v0.3 post-ship dogfood — 7/12 = 58% overflow becomes v0.4 acceptance target of 12/12 = 100% coverage on the same dataset

`writing-plans` should produce **~3-5 atomic tasks** (small plan; mostly mechanical edits):

| Task (preview) | Scope |
|---|---|
| T1 | Resolve exact Sonnet 4.6 model literal via Anthropic docs (Open Q #1); decide constant rename name (Q-v0.4-2 → `SUBAGENT_MODEL_ID`) |
| T2 | Update [main.py:55-56](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L55-L56) constant + [main.py:320](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L320) reference; update tests asserting the literal (TDD: RED on Sonnet literal first, then constant change makes it GREEN) |
| T3 | Update SKILL.md prose blocks (L78-90 cap doc / L142-155 ASCII diagram / L414-417 §Future → §Operating notes) |
| T4 | Optional: stderr cost-estimate preview line (Open Q #2) |
| T5 | Dogfood: re-run same v0.3 dataset → verify 12/12 coverage + Stage 4 cluster behavior; write `project_distill_sessions_v0_4_first_dogfood.md` memory |

T1 is `Independent: false` (wave leader; T2-T4 depend on the constant decision); T2 + T3 can be `Independent: true` after T1; T4 + T5 sequential after T3.

---

**Brief complete.** Next step: invoke [`code-toolkit:writing-plans`](../../../code-toolkit/skills/writing-plans/SKILL.md) with this brief path as the consumed input.
