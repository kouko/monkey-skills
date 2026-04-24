---
title: research-team v5.3.0 — Deep-Mode Hooks (multi-perspective + self-critique + parallel-fanout) industry survey
date: 2026-04-24
team: research-team
refactor_version: v5.3.0
tags: [research, domain-teams, research-team, grounding, hooks, multi-agent, deep-research]
---

# research-team v5.3.0 grounding research

> [!info] 研究背景
> v5.3.0 為 deep mode 補三個業界普遍存在、目前缺失的執行機制：
> **多角度（multi-perspective）**、**自省（self-critique）**、**並行（parallel fan-out）**。
> 本研究 phase 涵蓋 14 個業界 reference system 的對位，並為每個機制選擇
> **最小破壞性（minimum-disruption）** 的精簡版本——而非引入完整 reference 實作——以
> 控制 token 成本 + 維持 SKILL.md line budget + 不增加既有 protocol/standard/agent/gate 的數量。
>
> **研究方法**: 1 個 Explore agent 盤點現況 + 1 個 general-purpose agent 平行搜尋業界 14 樣本
> （EN + JP），交叉比對 Anthropic 官方、Claude Code 社群、通用 deep-research 框架、學術 canon。
> 結果用 trade-off 表 + 拆檔 vs 嵌入的 token 計算落地為三個 hook 檔。

## TL;DR

| Hook | Inspiration | 完整版 (omitted) | 採用 (minimum-disruption) | Token impact |
|---|---|---|---|---|
| **multi-perspective** | Stanford STORM (Shao et al. 2024) | perspective mining + simulated expert-writer dialog + outline curation | perspective-mining seed only (≥3 distinct) at end of Phase 0 | quick: 0; deep: +~100 |
| **self-critique** | LangGraph `open_deep_research` `think_tool` (LangChain 2024) | critique → revise iteration loop (multi-pass) | disclosure-only `## Self-Critique` block at end of Phase 3 (no rewrite) | quick: 0; deep: +~500–800 |
| **parallel-fanout** | Anthropic Multi-Agent Research System (Anthropic Engineering 2024) | dedicated lead/coordinator + N orchestrated sub-agents + CitationAgent post-pass | main agent self-coordinates; ≤4 isolated sub-workers with subset-only standards; no separate CitationAgent | quick: 0; deep: ±0 (isolated context offsets fan-out cost) |

| File-organization decision | Rationale |
|---|---|
| Lazy-loaded flat `protocols/hook-*.md` files (vs embedded into protocols) | Quick mode (~80% of usage) avoids reading deep-only dead text — net token win even though file Read overhead exists for deep mode |
| One central trigger map in `protocols/research.md` §Deep-Mode Hooks | 4 specialized protocols inherit via 1-line pointer — no duplication |

---

# Industry Survey (14 systems)

Sample categorized by what they contribute to the design choice. Full URLs preserved for primary-source verification.

## A. Anthropic-official + Claude Code ecosystem

| # | System | URL | Distinctive |
|---|---|---|---|
| 1 | Anthropic Multi-Agent Research System (Claude.ai Research) | https://www.anthropic.com/engineering/multi-agent-research-system | Lead Opus + parallel Sonnet workers + dedicated CitationAgent post-pass; +90.2% accuracy vs single-agent at 15× token cost |
| 2 | anthropic-cookbook research_subagent.md | https://github.com/anthropics/anthropic-cookbook/blob/main/patterns/agents/prompts/research_subagent.md | 5-phase OODA loop + `<source_quality>` rubric (peer-reviewed > industry primary > reputable secondary > tertiary); no numeric confidence |
| 3 | Anthropic Skills repo + using_sub_agents.ipynb | https://github.com/anthropics/skills | Established SKILL.md + bundled-resources progressive-disclosure spec (monkey-skills baseline) |
| 4 | Claude Code built-in Explore/Plan subagent | https://code.claude.com/docs/en/sub-agents | Read-only retrieval helper; no methodology guardrails |

## B. Community Claude Code subagents

| # | System | URL | Distinctive |
|---|---|---|---|
| 5 | wshobson/agents | https://github.com/wshobson/agents | 50+ subagents but no dedicated research; established `model: haiku\|sonnet\|opus` tier convention |
| 6 | VoltAgent/awesome-claude-code-subagents `10-research-analysis/` | https://github.com/VoltAgent/awesome-claude-code-subagents/tree/main/categories/10-research-analysis | 5 persona-style research subagents; **no gates, no rubrics, no academic canon** — the "industry default" |
| 7 | affaan-m/everything-claude-code | https://github.com/affaan-m/everything-claude-code | "Research-first" branding; doc-thin |
| 8 | SIOS tech-lab `/research` Skill × Sub-agent (JP) | https://tech-lab.sios.jp/archives/51233 | Skill = query design + critique; Worker = retrieval only — same separation as research-team |

## C. Generic deep-research frameworks

| # | System | URL | Distinctive |
|---|---|---|---|
| 9 | OpenAI Deep Research (Agents SDK) | https://cookbook.openai.com/examples/deep_research_api/introduction_to_deep_research_api_agents | Triage → **Clarification** → Instruction → Research; only system that interrogates user before research |
| 10 | LangGraph open_deep_research | https://github.com/langchain-ai/open_deep_research | Supervisor + parallel researchers + isolated context + explicit `think_tool` reflection (LLM critiques own draft) |
| 11 | GPT Researcher (assafelovic, 25.7k★) | https://github.com/assafelovic/gpt-researcher | ~20 crawler agents fan-out; explicit cross-referencing as anti-hallucination |
| 12 | Stanford STORM / Co-STORM | https://github.com/stanford-oval/storm | Two-stage pre-writing: perspective mining → multi-persona expert↔writer dialog → curate outline; +25% organization / +10% breadth vs RAG baseline (FreshWiki eval) |
| 13 | Perplexity Deep Research | https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research | Retrieve→reason→refine 3–5 sequential passes + explicit failure handling (paywalled / irrelevant → reroute) |
| 14 | Manus AI | https://manus.im/blog/manus-1.5-release | Plan-as-pseudocode injected into context + transparent side-panel; transparency strong, methodology weak |

## D. Academic canon (already grounded in research-team — no v5.3.0 changes)

PRISMA 2020, Cochrane Handbook v6.5, IPCC AR5 Mastrandrea 2010, Kent 1964, Tetlock 2015 are already grounded in `standards/`. Future v5.4.0 candidates (deferred): GRADE 5-domain certainty rating, ICD-203 confidence words ladder, Tetlock 10 Commandments + Brier scoring.

---

# Where research-team Stood Before v5.3.0

| Pattern | Industry prevalence | research-team status (pre-v5.3.0) | v5.3.0 verdict |
|---|---|---|---|
| Lead orchestrator + parallel sub-agents + isolated context | ★★★★★ | △ main agent serial decision | **ADD** (parallel-fanout hook) |
| Plan-then-execute separation | ★★★★ | ✅ Phase 0–3 structure | unchanged |
| Iterative retrieve→reason→refine + reflection | ★★★★ | △ SHOULD gate is evaluator-side | **ADD** (self-critique hook, disclosure-only) |
| Post-hoc CitationAgent | ★★★ | ✅ inline citation discipline | unchanged (different mechanism, same effect) |
| Persona bullet-list (no gate / rubric) | ★★★★★ (community default) | ✅ surpassed | unchanged |
| Academic canon (PRISMA / GRADE / ICD-203 / Tetlock) | ★ (industry rarely does this) | **★★★★★ moat** | unchanged (extensions deferred to v5.4.0) |
| Multi-perspective pre-writing (STORM) | ★ | ❌ missing | **ADD** (multi-perspective hook, mining-only) |
| Clarification gate (interrogate user before research) | ★ | △ scope_clarity is hint not gate | deferred (out of v5.3.0 scope) |
| Self-reflection-on-draft loop | ★★ | △ SELF check is worker self-claim | covered by self-critique hook (disclosure variant) |
| Cost-aware modes | ★★ | ✅ quick/deep + post-hoc escalation | unchanged |
| JP information infrastructure | ★ (industry no equivalent) | **★★★★★ moat** | unchanged |
| Visibility Convention (TaskUpdate heartbeat) | ★ (industry no equivalent) | ✅ v5.2.0 | unchanged |
| Attribution audit (42 corrections in v4.11.0) | ★ (industry no equivalent) | ✅ ongoing record | extended (this note adds 14 system-level citations) |

---

# Per-Hook Trade-Off Audit

## Hook 1: multi-perspective (STORM-inspired mining only)

**STORM full implementation** (Shao, Y. et al. 2024 *Stanford OVAL Lab*):
1. Discover diverse perspectives via Wikipedia category mining
2. Simulate multi-persona expert ↔ writer dialog grounded on retrieved sources
3. Curate outline from dialog transcripts
4. Generate article from outline

**v5.3.0 picks step 1 only**. Steps 2–4 omitted because:
- Step 2 (simulated dialog) requires multiple LLM passes per perspective — would balloon deep-mode token cost beyond ±5% bound
- Steps 3–4 are STORM's article-generation pipeline, not relevant to research-team (which produces analysis reports, not Wikipedia-style articles)

**Empirical justification for picking step 1 alone**: STORM's ablation in §4.3 shows perspective-aware question generation is the largest contributor to the +25% organization gain; the simulated-conversation refinement contributes a smaller marginal lift.

**Failure-mode handling**: hook explicitly allows worker to fall back to single-frame research with `scope too narrow for multi-perspective` note when 3 distinct perspectives don't exist (e.g., narrow factual lookup masquerading as deep). Prevents cosmetic-perspective padding.

## Hook 2: self-critique (LangGraph `think_tool`-inspired disclosure)

**LangGraph `open_deep_research` full implementation** (LangChain 2024):
1. Worker writes draft
2. Worker invokes `think_tool` to critique own draft (separate LLM call)
3. Worker revises draft based on critique
4. (Optionally repeat)

**v5.3.0 picks disclosure only — worker writes critique into the artifact, does NOT revise**. Steps 3–4 omitted because:
- Step 3 (revise) requires a second LLM pass — token cost roughly doubles per worker invocation
- Disclosure alone gives evaluator a stronger signal than a revised-but-opaque draft: evaluator sees what worker considers thin, can probe specifically

**Trade-off acknowledgment**: a worker that genuinely sees no weakness will write a vacuous critique. Hook makes vacuity itself a Fatal flag in the SHOULD gate's new Self-Critique Honesty dimension. This converts a silent failure (overconfidence) into a loud one.

**Comparison to existing SELF check**: SELF check (in SKILL.md) is "list 3-5 things that would make this output unacceptable, fix them" — happens before delivery, results invisible. Self-critique hook adds a complementary post-delivery disclosure visible to evaluator and end user.

## Hook 3: parallel-fanout (Anthropic Multi-Agent without coordinator agent)

**Anthropic Multi-Agent Research System full implementation**:
1. Lead Opus orchestrator decomposes query
2. Spawns N parallel Sonnet sub-agents with isolated context
3. Each sub-agent runs research independently
4. Lead integrates outputs
5. Dedicated CitationAgent post-processes inline citations

**v5.3.0 picks steps 1–4 with main agent as coordinator (no dedicated lead Opus orchestrator), and skips step 5 entirely**. Reasons:
- Step 5 (CitationAgent post-pass): research-team already enforces inline citation discipline at worker time via `standards/citation-standards.md`. Adding a post-pass agent adds latency + token cost without changing output quality.
- Dedicated orchestrator agent: main agent already plays this role; adding a separate Opus orchestrator would double the supervisory cost.

**Token economics inversion**: parallel-fanout often *reduces* total token cost because each sub-worker loads only its perspective-relevant standards subset (e.g., 1 of 4 additional standards), versus a single sequential worker loading all 4. The 10–20% savings offsets the multi-perspective + self-critique overheads, yielding net ±5%.

**Cap rationale (N≤4)**: Anthropic's blog post notes context fan-out balloons the integrator's work non-linearly; their internal sweet spot was 4–8 sub-agents. We cap at 4 because monkey-skills' main agent has tighter context budgets than a production lead Opus instance.

---

# File-Organization Trade-Off (拆檔 vs 嵌入)

The most-debated design decision was whether to inline hook rules into existing protocols (`research.md` Phase 0/1/3) or split into separate hook files. Decision: **split**.

| Dimension | Embed (rejected) | Split (chosen) |
|---|---|---|
| Quick-mode token cost | +150–200 every read (deep-only dead text loaded) | 0 (hook files lazy-loaded only when `mode=deep`) |
| Deep-mode token cost | hook content embedded in every protocol read | hook content + small file Read overhead (~150–300 tokens) |
| File granularity vs existing convention | matches (no new files) | adds 3 small files (~54–66 lines each) — slight micro-file drift |
| Future evolution | hard (mixed concerns in protocol) | easy (swap / deepen / replace single hook file) |
| Decision-flow complexity | minimal | minimal (worker sees one-line pointer in protocol) |

**Net token math** (per deep-mode research run):
- Embed: protocol baseline + 26L hooks always loaded
- Split: protocol baseline (0L hooks) + 3× lazy-load (~180L hook content) when deep triggers

For quick mode (default, ~80% of usage), split saves ~150–200 tokens per call. For deep mode (~20% of usage at ~30k–150k token scale), the difference rounds out to <±5%. Split wins on quick mode and is neutral on deep mode → split.

**Naming convention — flat `protocols/hook-*.md`** (originally proposed
sub-dir `protocols/hooks/` but blocked by CHK-SKL-012, which forbids
nested subdirectories under any required/optional skill subdir):
- `hook-` prefix preserves the original semantic intent (these are
  protocol-internal flow modifiers, not standalone workflows)
- Stays compatible with the existing flat layout convention all other
  monkey-skills team skills follow
- Future hooks (clarification gate / failure-recovery) colocate via
  prefix, not via sub-dir
- Sorted file listing keeps hooks adjacent (`hook-*` lexicographically
  groups them together within `protocols/`)

---

# What Was Explicitly Out of Scope

| Item | Why deferred |
|---|---|
| GRADE 5-domain certainty rating | Belongs in `standards/systematic-review-methodology.md`; v5.4.0 candidate |
| ICD-203 confidence words ladder | Belongs in `standards/confidence-and-claim-language.md`; v5.4.0 candidate |
| Tetlock 10 Commandments + Brier scoring | Same standard file; v5.4.0 candidate |
| Clarification gate (OpenAI Deep Research-style pre-research interrogation) | Would change worker dispatch contract; needs separate design pass |
| CitationAgent post-pass (Anthropic-style) | Existing inline-citation discipline is sufficient; adds cost without lift |
| Companion hooks (PreToolUse blocking) | Originally deferred from v5.0.0; hook reliability concerns persist |
| `protocols/research-brainstorming.md` perspective integration | Brainstorming protocol already does lateral expansion; multi-perspective hook is for in-protocol deep-mode use, not brainstorming |

---

# Verification

Token-impact verification deferred to first dogfood run. Suggested test:
```
[deep-mode research request, e.g., "deep research framework X vs Y for production backend"]
```
Verify in artifact:
1. Phase 0 surfaces ≥3 distinct stakeholder perspectives
2. Phase 1 main agent shows fan-out decision (parallel or sequential + reason)
3. Phase 3 artifact ends with `## Self-Critique` section (≤200 words, three points)
4. Evaluator verdict references Self-Critique Honesty dimension

Quick-mode verification:
```
[any quick research request]
```
Verify in worker output:
- No perspective listing
- No `## Self-Critique` section
- No fan-out language
- Token usage matches pre-v5.3.0 baseline (within noise)
