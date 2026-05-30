# distill-sessions v0.3 — brainstorming brief

> **Status**: 5-axis exploration complete. Locks v0.3 scope (`#2 + #5 + dual-dispatch`); defers `#1 context overflow` to a separate v0.4 brief after v0.3 dogfood. Ready for [`code-toolkit:writing-plans`](../../../code-toolkit/skills/writing-plans/SKILL.md).
>
> **Author**: kouko + Claude session, 2026-05-25.
>
> **Consumes**:
> - [`2026-05-22-skill-log-mining-v0.1-brief.md`](2026-05-22-skill-log-mining-v0.1-brief.md) — v0.1 brief (parent; Q1-Q6 locked decisions still apply)
> - [`distill-sessions-v0-1-first-real-dogfood`](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_1_first_real_dogfood.md) memory — 5 findings origin
> - [`distill-sessions-v0-2-narrow-hotfix`](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_2_narrow_hotfix.md) memory — v0.2 shipped #3+#4
> - [`kind-classifier-facet-outcome-dominates`](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/feedback_kind_classifier_facet_outcome_dominates.md) memory — dual-dispatch context
>
> **Produces**: structured v0.3 brief consumed by `writing-plans` to split into ~6-8 atomic tasks.

---

## Problem

**JTBD (Klement format)**: *When I dogfood `dev-workflow:distill-sessions` against real multi-hour `code-toolkit:*` sessions, I want Memory Items that are (a) routed to the skill that actually owned the friction (not the alphabetic-top in `top_skills`), (b) backed by evidence from N≥2 sessions (not anecdotal "this session exemplifies"), and (c) emitted from high-friction-but-succeeded sessions as failure-analysis too (not just success-analysis), so the output is shippable into SKILL.md without me mentally re-routing or filtering single-session noise.*

The 3 inputs share one underlying job: **make the Memory Items trustworthy enough to apply directly**. v0.1+v0.2 made the pipeline mechanically work and the gates honest; v0.3 makes the output analytically credible.

Out of scope (Axis 5): Finding #1 context overflow is also a real blocker but separated into a v0.4 brief — see [§Scope split decision](#scope-split-decision-option-b).

## Users

Primary user is still **kouko as skill maintainer** (per v0.1 brief §Users) running `/distill-sessions` after multi-PR `code-toolkit:*` cycles.

New v0.3-specific user constraint: **kouko has now done one real dogfood run** (2026-05-25, see memory). The findings are no longer speculative — they're observed pipeline behaviors. v0.3 ships fixes that close the gap between "mechanically works" (v0.1+v0.2 state) and "analytically trustworthy" (v0.3 goal).

Secondary user (other monkey-skills users at v0.4+) and tertiary user (cross-agent at v1.0+) inherit v0.1 brief unchanged.

## Smallest End State

**One paragraph**: After v0.3 ships, when a `/distill-sessions` run on `code-toolkit:*` produces multiple subagent outputs per target skill, the orchestrator (a) routes each Memory Item to the skill whose friction signals fired most in that session (not the lexically-first skill in `top_skills`), (b) clusters Memory Items across subagents and promotes only items supported by N≥2 sessions to `## Proposed additions` / `## Proposed modifications`; single-session items route to a new `## Cross-session evidence pending` bucket with their per-session anchor preserved, (c) when a session classifies as high-friction-but-succeeded (`friction_level=high` AND `facet.outcome ∈ success-strings`), `_build_subagent_entries` emits TWO `subagent_payload[]` entries with distinct `trajectory_id` — one routed to `prompt-failure-analysis.md`, one to `prompt-success-analysis.md`. `--max-trajectories-per-skill` counts both dispatches.

### What v0.3 does NOT touch

- **Finding #1 context overflow** — deferred to v0.4 brief. v0.3 inherits v0.1's implicit "operator filters oversized trajectories at preview-confirm" workaround. Surfaces are independent — Stage 4 clustering operates on whatever subagent output exists, even N=1 trajectories.
- **References file write-back** — still `false` per v0.1 Q4 (SKILL.md only).
- **Persistent cross-run ledger** — still v0.2 backlog (within-run fingerprint only).
- **New-skill discovery / `CLAUDE.md` rule extraction** — broad-scope `skill-log-mining` v1.0 territory; out of distill-sessions entirely.

## Current State Evidence

Verified 2026-05-25 against `main` (commit `1bb0f1bc`).

| Dimension | Path / file:line | What's there |
|---|---|---|
| **Forward** (kind classifier touch point) | [`scripts/main.py:137-155`](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L137-L155) `_kind_for_session` returns single `"failure"` / `"success"`; facet.outcome short-circuits before friction_level fallback | dual-dispatch needs `_kind_for_session` → return `list[str]` of dispatch kinds; `_build_subagent_entries` ([`main.py:211-268`](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L211-L268)) loops over the list |
| **Forward** (subagent payload builder) | [`scripts/main.py:211-268`](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L211-L268) `_build_subagent_entries` uses `uuid5(namespace, f"{skill}|{session}|{kind}")` | already kind-aware → dual-dispatch produces distinct `trajectory_id` for free; no namespace bump needed |
| **Forward** (signal weights for routing) | [`scripts/aggregate.py`](../../../dev-workflow/skills/distill-sessions/scripts/aggregate.py) `AggregateRecord.signals` carries severity + per-session counts; `reusability_score()` is per-skill | Finding #2 fix re-uses signal weights at per-session granularity → score `(session, skill)` pairs; route Memory Items to highest-scoring skill in the session |
| **Forward** (Stage 4 absence) | No `cluster.py` / no `merge.py` in `scripts/` | greenfield slot for cross-trajectory clustering |
| **Forward** (propose.py routing) | [`scripts/propose.py`](../../../dev-workflow/skills/distill-sessions/scripts/propose.py) currently routes by `kind` (failure → §Proposed modifications, success → §Proposed additions) + by `requires_new_reference_file` (true → §Marked for v0.2) + by anchor-validity (mismatch → §Anchor mismatch) | adds new §"Cross-session evidence pending" bucket for N=1 items |
| **Reverse** (dogfood evidence) | v0.1 first-real-dogfood memory — 5 trajectories, 3 Memory Items all single-session, all closed with "this session exemplifies" | confirms N=1 is the actual current pattern, not theoretical |
| **Reverse** (dual-dispatch evidence) | 2026-05-24 demo: 12/15 subagent_payload entries tagged `success` because facet.outcome short-circuits friction_level | confirms dual-dispatch will roughly double payload count for high-friction sessions |
| **Data** (test fixtures) | [`scripts/fixture_subagent_results.json`](../../../dev-workflow/skills/distill-sessions/scripts/fixture_subagent_results.json) + [`fixture_sample_skill.md`](../../../dev-workflow/skills/distill-sessions/scripts/fixture_sample_skill.md) + [`fixture_expected_proposals.md`](../../../dev-workflow/skills/distill-sessions/scripts/fixture_expected_proposals.md) | fixtures support 1 session with 1 memory_item; v0.3 needs N≥2 fixture variant for cluster tests |
| **Boundary** (no new dependencies) | `scripts/` is stdlib-lean per v0.1 Q1; pytest is the only dev dep | v0.3 keeps stdlib-only — cluster algorithm = string/title normalization, no embedding API |
| **Boundary** (test infra) | 77 pytest green on main per memory | v0.3 adds: cluster tests, dual-dispatch tests, friction-density-routing tests, propose.py §Cross-session bucket tests |

**Evidence paths appendix**:

- [`dev-workflow/skills/distill-sessions/SKILL.md`](../../../dev-workflow/skills/distill-sessions/SKILL.md) — v0.1.0 SKILL with v0.2 anchor-REQUIRED + memory-leak constraint; §Future already lists dual-dispatch at L404-420
- [`dev-workflow/skills/distill-sessions/scripts/main.py`](../../../dev-workflow/skills/distill-sessions/scripts/main.py) (504 LOC)
- [`dev-workflow/skills/distill-sessions/scripts/propose.py`](../../../dev-workflow/skills/distill-sessions/scripts/propose.py) (664 LOC)
- [`dev-workflow/skills/distill-sessions/scripts/aggregate.py`](../../../dev-workflow/skills/distill-sessions/scripts/aggregate.py) (466 LOC)
- v0.1 brief (`Q1-Q6` decisions still active): [`2026-05-22-skill-log-mining-v0.1-brief.md`](2026-05-22-skill-log-mining-v0.1-brief.md)

## Alternatives Considered (research-grounded)

Per Axis 4 protocol — WebSearch EN + JA on each of the 3 fix domains, 2026-05-25.

### Finding #1 context overflow — DEFERRED to v0.4

Documented here because the deferral decision required cross-finding research. Industry approaches surveyed:

| # | Approach | Source | Fit for our use case |
|---|---|---|---|
| 1 | **Sliding window around friction markers** (agent-side context curation) | JetBrains 2025 "Smarter Context Management for LLM-Powered Agents" (EN) | **Best fit**: main.py already detects markers; just don't include full transcript. Reduces 554K → ~50-100K easily. |
| 2 | **Sonnet 4.6 1M-context fallback** for oversized trajectories | Anthropic pricing docs (EN) — Sonnet 4.6 standard pricing $3/$15 per Mtok vs Haiku 4.5 $1/$5; 3× cost on oversized | Floor fallback when even windowing overflows. |
| 3 | **Pre-summarize via cheaper model first** (Haiku summary → Haiku analysis) | Layer X 2025 「LLMを用いて長文ドキュメントを速く・安く・安全に構造化する試み」(JA) | Adds summary-quality risk; two-step pipeline complexity. |
| 4 | **Recursive Language Models (RLM)** — LLM programmatically decomposes prompt + recursively calls itself | arxiv 2512.24601 (EN) | Over-engineered for our N=5 trajectories; pays off at orders-of-magnitude scale. |
| 5 | **Skip + warn at preview** (informed consent only) | n/a — operator workaround | Already in v0.1 bare-invocation protocol; not a fix. |

**My take (deferred)**: v0.4 brief will choose between **#1 sliding window + #2 Sonnet fallback** (recommended combo) vs **#3 pre-summarize**. Decision needs v0.3 dogfood data on what fraction of high-value friction lives within ±50 events of markers vs spread across the trajectory. See [§Scope split decision](#scope-split-decision-option-b).

### Finding #2 cross-skill conflation

| # | Approach | Source | Fit for v0.3 |
|---|---|---|---|
| 1 | **Friction-signal-density scoring per (session, skill)** — re-use existing `Signal.severity` weights, sum per skill in the session, route Memory Items to highest-scoring skill | derived from existing `aggregate.reusability_score` shape | **Recommended**: cheap, no new infrastructure, deterministic |
| 2 | **Include all invoked SKILL.md content in subagent input + let subagent pick target** | Anthropic Agent Skills articles (JA: gihyo.jp 2025, Ledge.ai 2025) | Over-engineered: doubles subagent token cost; defers routing-truth to LLM judgment |
| 3 | **Filter out multi-skill sessions** — mine clean single-skill sessions only | n/a — naïve baseline | Loses richest data (cross-skill friction IS the interesting pattern per Finding #2 dogfood evidence) |
| 4 | **ECHO hierarchical context + cross-validation** | arxiv 2604.22708 (EN), arxiv 2510.04886 (EN) | Over-engineered: built for multi-agent systems with 10s of agents; we have 1-3 skills per session typically |
| 5 | **GraphTracer dependency-graph attribution** | arxiv 2510.10581 (EN) | Same — built for deep search agents with information dependency graphs |

**My take**: **#1 (friction-signal-density)**. Existing signals already weight evidence; aggregating per-session per-skill is ~30 LOC change in `_build_subagent_entries`. Industry literature confirms attribution-by-signal-density is the cheap baseline before reaching for graphs.

### Finding #5 cross-session clustering (Stage 4 promotion)

| # | Approach | Source | Fit for v0.3 |
|---|---|---|---|
| 1 | **Stage 4 cluster + dedup at orchestrator merge** — group Memory Items by normalized title + section_anchor; require N≥2 to promote; N=1 routes to §Cross-session evidence pending | derived from v0.1 brief's deferred Stage 4 promise + RE-TRAC cross-trajectory pattern (arxiv 2602.02486, EN) | **Recommended**: matches v0.1's original promise; stdlib-only (title normalization + bucket) |
| 2 | **Embedding-based semantic clustering** (LLM-MemCluster style) | arxiv 2511.15424 (EN) | Adds embedding API dependency; v0.1 Q1 locked stdlib-only — defer to v0.5+ if title-based clustering proves insufficient |
| 3 | **Subagent-driven Sonnet merge reviewer** — dispatch a Sonnet reviewer per target skill that reads all Memory Items + decides merges | derived from v0.1 brief's "full SDD spec-reviewer + code-quality-reviewer triad" original promise | Heavier; adds 1 Sonnet call per target skill; defer until #1 sliding window lands (Sonnet budget better spent on oversized trajectories) |
| 4 | **Confidence labeling (no filter)** — every item gets `n_supporting_sessions: N` field; let human reviewer decide | derived from Google Antigravity Knowledge Item pattern (JA: Qiita aktsmm 2025) | Honest but doesn't address the original "anecdotal noise floods proposals" problem |
| 5 | **Self-consistency outlier filtering** (Semantic Self-Consistency style) | arxiv 2602.02486 + 2603.29301 (EN) | Same as #2 — requires embeddings; defer |

**My take**: **#1 (title+anchor normalization cluster + N≥2 promotion + N=1 bucket)**. Matches v0.1's original Stage 4 deferred promise; stdlib-only; preserves human-review affordance via the new bucket. If kouko's v0.3 dogfood shows title-collisions miss semantic overlap, v0.5 can promote to embedding-based clustering.

### Dual-dispatch on high-friction-success

Single-option fix per memory `feedback_kind_classifier_facet_outcome_dominates.md`:

- `_kind_for_session` returns `list[str]` instead of `str`:
  - high-friction-success → `["failure", "success"]` (dual dispatch)
  - otherwise → `[<single kind>]` (existing behavior preserved)
- `_build_subagent_entries` iterates over the list
- `uuid5(namespace, f"{skill}|{session}|{kind}")` already includes `kind` → trajectory IDs stay distinct for free
- `--max-trajectories-per-skill` counts both dispatches (one high-friction-success session consumes 2 of the budget)

No industry-research alternatives — this is a local correctness fix derived from observed pipeline behavior (12/15 success bias).

## What Becomes Obsolete

**Same-PR removal on v0.3 ship**:
- §Future block in [SKILL.md L404-420](../../../dev-workflow/skills/distill-sessions/SKILL.md#L404-L420) "Dual-dispatch on high-friction-but-succeeded sessions (v0.2)" — moves from §Future to §Operating notes / §Pipeline §Step 1 inline
- Memory caveat "single-session Memory Items always close with 'this session exemplifies'" stops applying — replaced by §Cross-session evidence pending semantics

**Becomes obsolete on v0.4 ship (NOT this brief)**:
- §Future block "Heading-extraction state machine" remains (orthogonal to v0.3)
- §Future block "v1.0 broad-scope `skill-log-mining` sibling" remains (different scope)
- §Future block "Stage 4 full SDD consolidation" — v0.3 ships a *minimal* Stage 4 (title+anchor cluster); the *full* SDD spec-reviewer + code-quality-reviewer triad version remains v0.5+ if minimal Stage 4 proves insufficient. Update §Future text to reflect "minimal Stage 4 shipped at v0.3 — full SDD triad deferred to v0.5+".

**Not obsoleted (intentional)**:
- Operator-patched "reduce 25 payload entries → 1" preview step — that's Finding #1 territory, v0.4
- v0.1 Q1-Q6 locked decisions — all still apply
- `apply.py` `--approved` gate — v0.3 doesn't touch write-back semantics

## Decision

**Build `dev-workflow:distill-sessions` v0.3** covering Finding #2 (cross-skill friction-density routing) + Finding #5 (minimal Stage 4 cluster + N≥2 promotion + N=1 bucket) + dual-dispatch on high-friction-success. SKILL.md-only outputs (inherits v0.1 Q4). Stdlib-only (inherits v0.1 Q1). Within-run only (inherits v0.1 Q6). Finding #1 context overflow deferred to v0.4 brief after v0.3 dogfood.

### Scope split decision (Option B)

Considered 4 options:

| Option | v0.3 | v0.4 | v0.5 | Why rejected / accepted |
|---|---|---|---|---|
| **A** — single PR | all 4 inputs | n/a | n/a | Mixed architecture levels (sliding window heavy + dual-dispatch 20 LOC); ~12-15 atomic tasks; reviewer fatigue |
| **B** — cheap then arch (chosen) | #2 + #5 + dual | #1 | n/a | Cheap wins ship faster; v0.3 dogfood data informs #1 architecture choice in v0.4 brainstorm |
| **C** — three PRs | dual-dispatch only | #2 + #5 | #1 | Too many ship cycles for kouko bandwidth; dual-dispatch alone is too small to justify own PR |
| **D** — arch first | #1 | #2 + #5 + dual | n/a | Real counter-argument: until #1 lands, only 1/5 trajectories fit Haiku → Stage 4 cluster has only N=1 → can't cluster. **Mitigated in B by**: v0.3 explicitly designs N=1 → §Cross-session evidence pending bucket as a deliberate UX (operator sees "would have clustered; only 1 session — re-run after #1 ships"). This makes B shippable even while #1 is unresolved. |

**Lock**: Option B. v0.4 brief is a separate brainstorm after v0.3 dogfood shows what fraction of friction lives within ±N events of markers.

### Locked Q-decisions for v0.3

**Q-v0.3-1 — Stage 4 cluster: filter or label?**
- **A. Filter (N≥2 promoted, N=1 → §Cross-session evidence pending bucket)** — chosen
- B. Label only (every item gets `n_supporting_sessions: N` field; no filter)
- C. Hybrid (filter as default; `--allow-single-session` opt-in flag)

**Why A**: matches v0.1 brief's original Stage 4 deferred promise; preserves human review affordance via the new bucket (operator can manually re-route a high-confidence N=1 item if they want); aligns with v0.1's "no silent writes" disposition (anecdotal items don't sneak into proposals).

**Q-v0.3-2 — Cross-skill routing: how to score?**
- **A. Highest-friction-signal-density per (session, skill)** — re-use existing `Signal.severity` weights — chosen
- B. Most-mentioned-skill in session
- C. Subagent picks target from list of invoked skills (defers truth to LLM)

**Why A**: re-uses infrastructure (no new scorer); deterministic; industry-grounded (signal-density attribution is the standard cheap baseline). B is naïve (frequency ≠ friction); C adds tokens + LLM judgment risk.

**Q-v0.3-3 — Dual-dispatch budget arithmetic**
- **A. Counts as 2 dispatches** (one high-friction-success session consumes 2 of `--max-trajectories-per-skill`) — chosen
- B. Counts as 1 session (just 2 dispatches; budget is session-counted, not dispatch-counted)

**Why A**: each dispatch is a real API call; the budget exists to cap API spend; counting dispatches matches the budget's intent. Documented in §Pipeline / §Step 1.

## Out of Scope (v0.3)

- **Finding #1 context overflow** — v0.4 brief
- **Full SDD spec-reviewer + code-quality-reviewer triad for Stage 4** — minimal Stage 4 at v0.3; full triad deferred to v0.5+ if minimal insufficient
- **Embedding-based semantic clustering** — v0.5+ if title+anchor normalization proves insufficient
- **Persistent cross-run fingerprint ledger** (SQLite or JSON) — still v0.2 backlog, not v0.3
- **Codex / Gemini / Cline / Cursor adapters** — still v1.0
- **`references/<topic>.md` write-back** — still v0.2 (apply.py refuses; routes to §Marked for v0.2)
- **Auto-trigger** — still on-demand only (v0.1 decision)
- **New-skill discovery / `CLAUDE.md` rule extraction** — v1.0 broad-scope `skill-log-mining`, separate brainstorm
- **Heading-extraction state machine** (skip `## heading-in-code` inside fenced blocks) — orthogonal v0.3+; defer to dedicated micro-PR if real

## Open Questions (surface during writing-plans)

Five sub-decisions surface only as `writing-plans` carves atomic tasks. Not blocking the brief.

1. **Title-normalization algorithm for Stage 4 cluster**: lowercase + strip whitespace + collapse punctuation vs tf-idf-cosine threshold vs SequenceMatcher ratio threshold. Lean: lowercase + strip + collapse (stdlib-only, deterministic, ~10 LOC). Defer to plan-time.
2. **§Cross-session evidence pending render format**: per-item with session_id + anchor + body, vs collapsed-by-title with session_ids appended. Lean: collapsed-by-title (less noise; matches §Anchor mismatch's by-anchor grouping). Defer to plan-time.
3. **Test fixture upgrade scope**: extend existing `fixture_subagent_results.json` with a multi-session multi-target-skill variant, or create new `fixture_subagent_results_v03.json` parallel file. Lean: parallel file (v0.1 fixtures stay golden for regression; v0.3 fixtures additive). Defer to plan-time.
4. **Whether `_kind_for_session` returning `list[str]` is a breaking change for downstream consumers**: grep shows it's only called from `_build_subagent_entries`. Lean: yes-it's-internal, just adapt the call site. Defer to plan-time confirmation.
5. **Friction-density tie-break when 2 skills score equal**: alphabetic (current behavior) vs first-encountered-event. Lean: alphabetic (deterministic, matches existing); flag as v0.4-revisit. Defer to plan-time.

## Plan-time atomic task preview

For `writing-plans` consumption — not a plan, just shape hints. Expect ~6-8 atomic tasks under SDD:

| # | Atomic task (≤5 min) | Files touched | Independent? |
|---|---|---|---|
| 1 | Dual-dispatch: `_kind_for_session` returns `list[str]`; `_build_subagent_entries` iterates; update `test_main.py` | `scripts/main.py`, `scripts/test_main.py` | true (no dependents in this wave) |
| 2 | Friction-density scoring: per-(session, skill) signal weight sum; route Memory Items to highest-scoring skill; new `aggregate.score_skill_in_session(...)` helper | `scripts/aggregate.py`, `scripts/main.py`, `scripts/test_aggregate.py` | true |
| 3 | Multi-session multi-skill fixture for Stage 4 + Finding #2 tests | `scripts/fixture_subagent_results_v03.json` (new), `scripts/fixture_sample_skill.md` (extend if needed) | true |
| 4 | Stage 4 cluster: title+anchor normalization + N≥2 promotion + N=1 bucket; new `scripts/cluster.py` module + tests | `scripts/cluster.py` (new), `scripts/test_cluster.py` (new) | true (after T3 fixture lands) |
| 5 | `propose.py` integration: consume cluster output; render §"Cross-session evidence pending" bucket; update `test_propose.py` | `scripts/propose.py`, `scripts/test_propose.py` | false (depends on T4) |
| 6 | SKILL.md updates: move dual-dispatch + Stage 4 from §Future to §Pipeline + §Operating notes; document `--max-trajectories-per-skill` arithmetic change; document §Cross-session evidence pending bucket | `dev-workflow/skills/distill-sessions/SKILL.md` | false (depends on T1-T5) |
| 7 | README tri-language sync (en/ja/zh-TW) — describe Stage 4 cluster + dual-dispatch + cross-skill routing | `dev-workflow/skills/distill-sessions/README{,.ja,.zh-TW}.md` | false (depends on T6) |
| 8 (conditional) | dev-workflow `plugin.json` + monkey-skills `marketplace.json` version bump v0.1.0 → v0.3.0 + description sync (CI-enforced) | `dev-workflow/.claude-plugin/plugin.json`, `marketplace.json` | false (last) |

**SDD threshold**: 6-8 tasks (>5) → SDD mandatory per [`code-toolkit:writing-plans`](../../../code-toolkit/skills/writing-plans/SKILL.md). T1+T2+T3 are `Independent: true` and have disjoint files — `dispatching-parallel-agents` eligible per [router auto-suggest hook](../../../code-toolkit/skills/using-code-toolkit/SKILL.md).

**Estimated implementer LOC** (rough): T1 ~30 LOC + T2 ~50 LOC + T3 ~100 LOC fixture + T4 ~120 LOC cluster module + T5 ~40 LOC integration + T6 ~80 LOC docs + T7 ~150 LOC tri-lang README = ~570 LOC + tests.

## Handoff to writing-plans

Input ready for [`code-toolkit:writing-plans`](../../../code-toolkit/skills/writing-plans/SKILL.md):

- **Brief**: this file (`docs/code-toolkit/specs/2026-05-25-distill-sessions-v0.3-brief.md`)
- **Parent brief**: [`2026-05-22-skill-log-mining-v0.1-brief.md`](2026-05-22-skill-log-mining-v0.1-brief.md) (Q1-Q6 still active)
- **Touch points verified**: `_kind_for_session` ([main.py:137-155](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L137-L155)), `_build_subagent_entries` ([main.py:211-268](../../../dev-workflow/skills/distill-sessions/scripts/main.py#L211-L268)), `aggregate.py` signal-weight infrastructure, `propose.py` bucket routing
- **Dogfood evidence**: 5 trajectories + 3 Memory Items + 12/15 success bias confirmed in memories

`writing-plans` should produce 6-8 atomic tasks following the preview table above, mark T1-T3 `Independent: true` for parallel-implementer dispatch, and gate the final commit on the v0.3 fixture-based regression suite running green.

---

**Sources cited** (Axis 4 research — 2026-05-25):
- [JetBrains 2025: Smarter Context Management for LLM-Powered Agents](https://blog.jetbrains.com/research/2025/12/efficient-context-management/) (EN) — sliding-window agent context curation
- [arxiv 2602.02486: RE-TRAC cross-trajectory state representation](https://arxiv.org/abs/2602.02486) (EN) — cross-trajectory clustering pattern
- [arxiv 2604.22708: ECHO hierarchical failure attribution](https://arxiv.org/html/2604.22708v1) (EN) — multi-agent attribution literature
- [arxiv 2510.10581: GraphTracer information-dependency-graph attribution](https://arxiv.org/pdf/2510.10581) (EN) — alternative attribution
- [arxiv 2511.15424: LLM-MemCluster dynamic memory clustering](https://arxiv.org/pdf/2511.15424) (EN) — embedding-based clustering alternative
- [Anthropic Claude pricing 2026](https://platform.claude.com/docs/en/about-claude/pricing) (EN) — Sonnet 4.6 1M-context cost trade-off
- [LayerX 2025「長文ドキュメント構造化」](https://tech.layerx.co.jp/entry/2025/12/16/194317) (JA) — pre-summarize pipeline pattern
- [Qiita aktsmm 2025「はじめての Agent Skills 12 選」](https://qiita.com/aktsmm/items/08eef2cdeeb0a32b69a2) (JA) — Google Antigravity Knowledge Item pattern (cross-session memory)
- [Ledge.ai 2025「Anthropic スキル中心アーキテクチャ」](https://ledge.ai/articles/anthropic_ai_agents_build_skills_paradigm) (JA) — multi-skill context window discussion
- [gihyo.jp 2025「Anthropic Agent Skills」](https://gihyo.jp/article/2025/12/agent-skills-to-open-standard) (JA) — Agent Skills as open standard
