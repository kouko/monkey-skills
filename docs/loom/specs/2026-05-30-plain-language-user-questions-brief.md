# code-toolkit plain-language user-questions — brainstorming brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-05-30
> **Author**: kouko + Claude (Opus 4.8) session
>
> **Consumes**:
> - Memory: [[project-code-toolkit-question-plain-language-investigation]] (CLOSED investigation — 608 Qs / 9 projects telemetry, 6 failure modes, 7 grounded rules, cross-project differential, user testimony)
> - Memory: [[feedback_skill_independence_applies_between_sister_skills]] (per-skill placement convention — drives the duplication decision)
> - Memory: [[xml-tag-mode-separation-for-skill-principles]] (structural-enforcer candidate, deferred to v0.2)
> - Sister-plugin precedent: `dev-workflow:recap-state` `plain-language` principle (PR #338/#343/#344) — reuse wording for the "only terms the user introduced" escape hatch + Block-1 "Situation" state-anchor pattern
> - Industry grounding (Axis-4, EN+JA): NN/g Heuristics #1 (visibility of system status) + #2 (match system & real world); ISO 24495-1:2023 Plain Language; NN/g Progressive Disclosure; Curse of Knowledge (Heath / Pinker); UXライティング / マイクロコピー (仲野佑希) + やさしい日本語
>
> **Status**: 5-axis exploration complete (investigation already did the work). 0 blocking Open Questions — placement + scope already locked by user. Ready for `writing-plans`.

## Problem

**JTBD**: When code-toolkit's orchestrator stops to ask me (the human user) a question — a "what next?" hand-off, a "which approach?" decision, a "how to handle these review findings?" choice — I want the question and its options to be **understandable on their own at the moment they appear**, so I can decide without having to mentally decode internal jargon, reconstruct lost context, or bail out entirely.

The failure mode this brief exists to prevent, evidenced across 608 real questions in 9 projects (memory investigation), decomposes into **6 independent modes**:

1. **Jargon leak** — options named by internal mechanism (`SDD` / 「跨」/ `PASS 12/12` / `implementer` / `🟡🟢` / `Wave 1 = T1+T3+T4`), extending even to domain jargon (`saga` / `quorum-based reconciliation`). User testimony: 「你說的那個 saga 跟 offset commit 是什麼意思？可以再講一次嗎」.
2. **Cold-start** — ~20-23% of questions open with a bare decision verb and zero state (「下一步怎麼走？」「M1 要怎麼切？」). User testimony: 「沒頭沒尾的，給我完整脈絡再問我」.
3. **Options invented without research** — 8% of answers were custom-typed because the agent offered made-up options instead of running Axis-4 first; users repeatedly ask 「業界怎麼做」 / 「JetBrains 怎麼做」. Violates the toolkit's own router rule #5.
4. **Unanswerable → ESC** — 6% of questions dismissed outright; 43% of those carried jargon or cold-start.
5. **>4 options → InputValidationError** — agent emitted 5-8 options, hit the tool's hard cap, wasted a turn.
6. **Compound overload** — unrelated decisions crammed into one multi-question ask.

83% of questions already work cleanly — this targets the 17% tail, not a rewrite.

## Users

- **Primary (decision-maker reading the question)**: kouko, mid-code-toolkit-workflow, often after a context-switch or a long subagent run, deciding a next step. Native languages 繁中 / 日 / EN; **not** fluent in code-toolkit's internal vocabulary even though he authored the plugin (curse-of-knowledge cuts both ways — the agent is fluent, the in-the-moment reader is task-loaded).
- **Reader audience = HUMAN, warm-but-interrupted (L3-like)** — opposite of the code-reviewer agent's machine reader. This is the crux: the rules apply to the **orchestrator → user** surface, NOT to the reviewer-agent → orchestrator verdict (which MUST stay technically precise + citation-bearing per its evidence-citation contract). Mixing these layers is the mistake the v0.1-of-this-investigation almost made.
- **Cross-project**: any project using code-toolkit, NOT just monkey-skills. Worst-hit is komado-Refs (an Xcode app, 19 jargon-heavy questions) where the user has zero reason to know SDD vocabulary.
- **Non-goal users**: the reviewer/implementer subagents (they consume structured verdicts, not prose questions — explicitly out of scope).

## Smallest End State

**One-paragraph summary**: Add one **`asking-the-user` principle block** (the 7 rules below) to the two highest-friction skills first — `subagent-driven-development` and `requesting-code-review` — at their existing "surface to user" instruction points. The block instructs the orchestrator: when you stop to ask the user a question or present options, phrase the question + options by these 7 rules. No new tool, no Python, no schema — pure SKILL.md prose, same 0-LOC shape as recap-state. Prove via real dogfood on these 2 skills; only then roll the same block to the other 6 question-emitting skills (NOT a mechanical 8-skill rollout up front — recap-state lesson).

**The 7 rules** (each grounded; full provenance in memory):

| # | Rule | Targets mode | Grounding |
|---|---|---|---|
| 1 | Options describe the **outcome** ("you'll get X"), not the mechanism ("uses SDD dispatch") | 1 | NN/g #2 / Outcome-over-Mechanism |
| 2 | Translate or replace jargon; **exception**: terms the user introduced **this session** are fine | 1 | Plain Language ISO 24495-1 / Curse of Knowledge / recap-state wording |
| 3 | Numbers carry their meaning (`PASS 12/12` → "5 tasks all checked"); mechanism detail sinks to a sub-line | 1 | Progressive Disclosure |
| 4 | Every question opens with a one-line **state anchor** (we just did X; now Y needs deciding) | 2, 4a | NN/g #1 / recap-state Block 1 "Situation" |
| 5 | For design / strategy / tech-stack questions, **research industry practice first** (Axis-4) before inventing options | 3 | router rule #5 (existing, under-enforced) |
| 6 | **≤4 options**; never add an explicit "Other" (auto-injected); for **open** questions end with a free-form invite, for **closed factual** questions don't | 4b, 5 | tool spec + discoverability |
| 7 | Compound asks only when sub-questions share one topic / are jointly judgeable; split unrelated decisions into separate rounds | 6 | cognitive load |

### North-star exemplar (the target style the rule block must show)

Claude Code's **built-in `/recap` away-summary** is the gold-standard plain-language target — it demonstrates rules 1-4 in one breath. The rule block in T1/T2 MUST include this as a `✅ good / ❌ avoid` worked example (same before/after teaching method recap-state used to pin its `plain-language` rule):

```
✅ Standard (built-in recap style — outcome-framed, no jargon, plain status, term-explained-on-use):
   "We're making code-toolkit's questions easier to understand by adding plain-language
    rules to two skills. The brief and plan are done and approved; next is editing the
    actual SKILL.md files."

❌ Avoid (jargon-dense status-report style):
   "Plan v2 PASS round 2, 0 gaps. T1-T4 sequential, Independent:false, 走 SDD 三角審查. DAG 無環."
```

Why it works, mapped to the rules: "easier to understand" = outcome not mechanism (R1); zero internal jargon (R2); "done and approved" = status in plain words not `PASS 4/4` (R3); "running SDD **to actually edit the SKILL.md files**" = names a term but immediately explains it (R2 expand-on-first-use). This single sentence is the calibration target for every question/status the orchestrator surfaces.

## Current State Evidence

Touching existing code — both target skills already have "surface to user" steps but **zero phrasing guidance**; that absence is the gap.

- **Forward (where questions originate)**: `code-toolkit/skills/subagent-driven-development/SKILL.md:51,65,83-85` — `NEEDS_CONTEXT`/`BLOCKED`/4th-retry/`DONE_WITH_CONCERNS` all say "surface to user" with no HOW. The worst real offenders (the「Plan committed (PASS 12/12)。下一步？」hand-offs) emerge from §Continuous execution (`SKILL.md:7-14`) — orchestrator-driven, also unguided.
- **Reverse (review relay)**: `code-toolkit/skills/requesting-code-review/SKILL.md:77,78,89` — "surface findings"/"Print the verdict + findings; let user decide" with no instruction to translate `🔴🟡🟢` + Beck/OWASP citations into plain language for the human.
- **Boundary (what must NOT change)**: `code-toolkit/agents/code-reviewer.md:59-78` (Rule R2 — every finding needs an evidence citation) + `:289-315` (structured YAML verdict). These stay machine-precise; rules apply only to the orchestrator's relay, never to the agent's verdict.
- **Error/Data**: investigation memory holds the quantified telemetry (608 Qs, per-mode %); no code-level data structures change.
- **Existing convention to match**: neither target SKILL.md has a `## Principles` section today; `dev-workflow:recap-state/SKILL.md:141-148` shows the house style for a `plain-language` principle block to mirror.

Evidence paths appendix: `code-toolkit/skills/subagent-driven-development/SKILL.md`, `code-toolkit/skills/requesting-code-review/SKILL.md`, `code-toolkit/agents/code-reviewer.md`, `dev-workflow/skills/recap-state/SKILL.md`.

## Decision

**What we will build**: a `## Asking the user` principle block (7 rules, ~25-35 lines of prose) added to `subagent-driven-development/SKILL.md` and `requesting-code-review/SKILL.md`, positioned next to / referenced from each skill's existing "surface to user" steps. Wording reuses recap-state's `plain-language` escape-hatch + Block-1 state-anchor phrasing for cross-skill consistency. Each skill ships its **own** copy (per-skill placement, locked by user).

**What we will NOT build**: no shared reference file, no router-level central rule, no reviewer-agent change, no Python, no XML-tag structural enforcer (v0.2 candidate), no rollout to the other 6 skills until these 2 dogfood-confirm.

**Why**: the evidence is real and project-independent; the fix is prose-only and low-risk; per-skill duplication honors the 自包含 convention the user re-confirmed; starting with 2 skills (not 8) follows the recap-state "dogfood before mechanical rollout" lesson.

## Alternatives considered

1. **Central rule in the `using-code-toolkit` router** — rejected: user locked per-skill placement; router-as-SSOT conflicts with 自包含 convention (prior user correction in [[feedback_skill_independence_applies_between_sister_skills]]).
2. **Shared `references/asking-the-user.md` referenced by all skills** — rejected for v0.1: introduces a cross-skill file dependency (same convention tension); revisit only if drift across 8 copies becomes painful.
3. **Fix all 8 question-emitting skills at once** — rejected: mechanical rollout before dogfood; recap-state showed in-flight amendments are common, so prove on 2 first.
4. **XML-tag mode separation as structural enforcer** (per [[xml-tag-mode-separation-for-skill-principles]]) — deferred to v0.2; prose principle first, structural enforcement only if dogfood shows the prose rule doesn't hold.

## What becomes obsolete

- The unguided "surface to user" phrasing at the cited line points — superseded by the rule block (update in the same change, don't leave both).
- Nothing else; this is mostly additive, which is itself a mild YAGNI flag — mitigated by the strong dogfood evidence that the 17% tail is real.

## Out of scope

- Reviewer/implementer **agent** output (stays machine-precise + citation-bearing).
- The other 6 question-emitting skills (`brainstorming`, `writing-plans`, `systematic-debugging`, `verification-before-completion`, `dispatching-parallel-agents`, `finishing-a-development-branch`) — v0.2 rollout after dogfood.
- The "agent misframes the problem" adjacent finding ([[feedback_agent_misframes_problem_intent]]) — different family (assessment, not wording); watch-and-confirm.
- Any change to the AskUserQuestion tool itself (harness-level, not ours).

## Open Questions

None blocking. Two minor confirmations for `writing-plans` to surface, not block:
- **OQ1**: rule-block as a new `## Asking the user` section vs folded into each existing "surface to user" bullet? (Lean: dedicated section + cross-reference, matches recap-state house style.)
- **OQ2**: does rule 5 (research-first) belong here as a reminder, or is it purely a re-pointer to router rule #5 to avoid duplicating Axis-4 protocol? (Lean: one-line re-pointer, not a copy — avoids drift with brainstorming's Axis-4.)
