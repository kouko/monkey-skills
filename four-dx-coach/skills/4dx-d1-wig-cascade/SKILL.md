---
name: 4dx-d1-wig-cascade
description: |
  Coaches a leader-of-leaders (3+ sub-teams) to translate an org Primary WIG into Team WIGs (Ch.7 four rules). Use when assigning sub-team WIGs unchecked: 'translate Primary WIG down', 'audit our cascade'. Single-team WIG → wig-formulation.
source_book: "The 4 Disciplines of Execution (2nd ed., 2021) — Chris McChesney, Sean Covey, Jim Huling, Scott Thele, Beverly Walker"
source_chapter: "Chapter 7 — Translating Organizational Focus Into Executable Targets"
source_language: en
tags: [d1, wig-cascade, team-wig, leader-of-leaders, key-battles, targets-not-plans, audit-mode, coach-mode, 4dx]
related_skills:
  - 4dx-d1-wig-formulation
  - 4dx-meta-strategy-triage
  - 4dx-meta-team-leader-onboarding
  - 4dx-audit
  - using-four-dx-coach
---

# 4dx-d1-wig-cascade — Translate org Primary WIG into Team WIGs (multi-mode)

## Mission

Coach or audit a **leader-of-leaders** through Discipline 1's cascade
hop: translating an already-set org Primary WIG into Team WIGs across
3-7 subordinate teams via the Ch 7 four-rule operating system —
Targets-not-Plans, Battles-to-win-the-war, Veto-don't-Dictate, one-
WIG-per-individual. Two interaction protocols:

- **Coach-mode** (Socratic, from zero) — leader-of-leaders has the
  Primary WIG and a list of sub-teams; agent walks the 10-step
  cascade-build protocol and outputs a fresh cascade map.
- **Audit-mode** (consultant, on existing cascade artifact) — leader-
  of-leaders provides an existing cascade map (often + sub-leader /
  sub-team critique: "imposed on us", "doesn't ladder", "we don't own
  this"); agent runs per-rule verdicts and recommends revisions +
  re-negotiation scripts, without rebuilding from scratch.

The same four Ch 7 rules anchor both protocols; what differs is **whether
the artifact already exists** (audit) or is being built (coach), and the
**agent voice** (consultant-to-leader / consultant-from-artifact).

## When this skill activates

### Multilingual trigger phrasings

**Coach-mode (build cascade from scratch, agent = consultant-to-leader):**
- EN: "How do I translate our Primary WIG to my **3-7 subordinate teams**?", "Cascade our Primary WIG **across direct-report team-leaders**", "Each of my managers leads their own team — how do they each pick a WIG?", "How do I break the company WIG into team WIGs?"
- JP: 「上から降りた WIG を**各チーム**に落とす」「Primary WIG を**各チーム**に翻訳」「直属マネージャー毎の Team WIG をどう決める」
- zh-TW: 「上面定的 WIG，**我下面各個團隊**要怎麼接？」「Primary WIG 怎麼拆給**下面各個團隊**？」「**我帶的各位主管**要有自己的 Team WIG，怎麼選？」

**Audit-mode (diagnose existing cascade artifact, agent = consultant-from-artifact):**
- EN: "Audit our cascade — sub-leaders complaining about it", "Got feedback our cascade map needs work", "Stakeholder wants to revisit how we cascaded the WIG", "Manager flagged the cascade — diagnose", "Boss says cascade is wrong, here's the map", "Here's our cascade map — sub-team-leaders say it's imposed", "Diagnose this cascade against 4DX"
- JP: 「うちの cascade を診断して、下のリーダー達が文句言ってる」「上司にフィードバックされた、cascade 見て」「マネージャーから方向性を直したいと言われた、cascade map チェック」「cascade map 見て何がダメか教えて」「cascade を audit して、現場が押し付けって言ってる」
- zh-TW: 「幫我看 cascade 哪裡有問題，下面的 leader 都在抱怨」「主管覺得 cascade 要調整，幫看哪裡」「review 後想討論 cascade 方向」「上面說 cascade 不對，這是 map」「cascade map 給你看，下面說是硬塞下來的」

### Non-activation signals (DO NOT fire when…)

- Org Primary WIG hasn't been selected yet → `4dx-d1-wig-formulation`. Cascade requires an upstream WIG to translate.
- Leader runs only ONE team (no subordinate team-leaders) → `4dx-d1-wig-formulation` directly; there is no cascade hop.
- Solo / individual goal → `4dx-d1-wig-formulation`. Cascade is a multi-team concept.
- Ambiguous Chinese 「我團隊」/「我們部門」 (could be single-team-leader or leader-of-leaders) → default to `4dx-d1-wig-formulation`; activate cascade only if query explicitly mentions multiple sub-teams or sub-leaders.
- Methodology-fit unclear → `4dx-meta-strategy-triage` first.
- User asking about lead measures / scoreboards / cadence → D2 / D3 / D4 skills.
- **OKR / quarterly objectives / KR cascade** without 4DX framing → `using-four-dx-coach`.
- Cross-layer audit (cascade + lead measures + scoreboard + cadence diagnosed together) → `4dx-audit`. This skill's audit-mode is **D1-cascade-only**.
- Single-team WIG audit (no cascade involved, just one Team WIG to diagnose) → `4dx-d1-wig-formulation` audit-mode.
- Cascade depth >2 layers → rerun this skill at each layer.
- Generic "Cascade plan" / "Cascade rollout" without 4DX context → `using-four-dx-coach`.

## Mode detection

When this skill activates:

1. Determine **interaction mode**: coach-mode (no cascade artifact exists yet, leader wants to build) vs audit-mode (cascade map already drafted / running, leader wants per-rule diagnosis, often + sub-leader critique).
2. **Audit-mode pre-check** — confirm the artifact contains: org Primary WIG + at least one Battle layer (or directly Team WIGs) + at least one named subordinate team / Team WIG. If only the Primary WIG is present (no sub-team commitments yet), route to coach-mode — there is no cascade to audit.
3. Load the matching protocol file from `protocols/`.
4. Follow that protocol's E section step-by-step.

### Mode triage (apply first)

| Signal in user query | Mode |
|---|---|
| User describes a Primary WIG + N sub-teams and asks how to translate / cascade / split / 「翻訳」/「拆給」 | **coach-mode** |
| User pastes / references a cascade map (Primary → Battles → Team WIGs) and asks "what's wrong?" / "diagnose" / "audit" / 「診断」/「哪裡有問題」 | **audit-mode** |
| User pastes a cascade map + sub-leader / sub-team critique ("imposed on us", "doesn't ladder", 「押し付け」, 「硬塞」, 「不接受」) | **audit-mode** |
| Vague / ambiguous on whether cascade artifact exists | ask ONE clarifying question (below) |

If ambiguous after reading the user's query, ask ONE Socratic question:

> EN: "Quick check: do you (a) need to **build the cascade from scratch** (you have a Primary WIG but no Team WIGs proposed yet), or (b) have an **existing cascade map** you want diagnosed (often because sub-leaders are pushing back)? I'll route to the right protocol."
>
> JP: 「確認: (a) **これから cascade を組み立てる**（Primary WIG はあるが Team WIG 未提案）か、(b) **既存の cascade map を診断**したい（下のリーダーから push-back が来ている等）かどちらですか？適切な protocol に振り分けます。」
>
> zh-TW: 「確認一下：(a) **要從頭組 cascade**（有 Primary WIG，下面 Team WIG 還沒提案）還是 (b) **已經有 cascade map 想診斷**（通常下面的 leader 在反彈）？我幫你導到對的 protocol。」

If the signal in the original query is strong, skip the question and load the protocol directly.

## Protocol routing table

| Mode | Detected situation | Load protocol | Agent voice |
|---|---|---|---|
| Coach | No cascade map yet — build from Primary WIG + N teams | `protocols/coach-mode.md` | consultant-to-leader |
| Audit | Cascade map exists (often + sub-leader critique) | `protocols/audit-mode.md` | consultant-from-artifact |

After loading the protocol, follow its E section step-by-step. Each protocol carries its own R / I / A1 / A2 / E / B sections; this orchestrator does not run any cascade content directly.

### Edge-case routing

- **Org Primary WIG not yet set** — both modes require it. Route to `4dx-d1-wig-formulation` first, then return.
- **Single-team-leader misfire** — leader has ONE team and is using cascade vocabulary to push WIGs to individual reports. Cascade does not push individual-level WIGs; route to `4dx-d1-wig-formulation` for the single Team WIG, then to D4 for individual commitments.
- **Cascade map present but only 1 sub-team named** — degenerate cascade; route to `4dx-d1-wig-formulation` for that single Team WIG.
- **Cross-layer audit (cascade + leads + scoreboard + cadence)** — that's `4dx-audit`, not this skill's audit-mode. Audit-mode here is **D1-cascade-only**.
- **Cascade depth >2 layers** — re-run this skill at each layer; do not single-pass deep cascade.
- **OKR cascade audit** — out of 4DX scope; route to `using-four-dx-coach`.
- **Audit request without cascade artifact** — if user asks for an audit but provides no cascade map, ask once for the artifact; if none available, decline audit-mode and route to coach-mode.

## Cross-skill relations

- **Upstream (prerequisite)** — `4dx-d1-wig-formulation` defines the org Primary WIG. Cascade has nothing to translate without it. `4dx-meta-strategy-triage` confirms each subordinate team is 4DX-fit.
- **Compose-with neighbour** — `4dx-meta-team-leader-onboarding` is upstream of each subordinate team-leader receiving their Team WIG; cascade only commits when sub-leaders are onboarded.
- **Downstream (sequels)** — once the cascade map closes, each Team WIG flows into D2 / D3 / D4 inside that team.
- **Compose-with audit** — `4dx-audit` runs full-stack diagnosis (WIG / leads / scoreboard / cadence / substrate); this skill's audit-mode is the D1-cascade slice. If the user's question spans layers, route up.
- **Plugin-router fallback** — `using-four-dx-coach` handles cold-start triage and out-of-4DX queries (OKR cascade, hoshin catchball, balanced-scorecard cascade); not a substitute for this skill.

## Boundary (cross-mode common)

The mode-specific boundary lives in each protocol's B section. The cross-mode common boundary:

- **Cascade is a leader-of-leaders operation** — applies only when a single leader manages 3+ subordinate teams, each with its own team-leader. For solo / single-team-leader scope, both modes are wrong-shaped; route to `4dx-d1-wig-formulation`.
- **Cross-mode disambiguation** — coach-mode is for users *without* a cascade artifact who need Socratic build; audit-mode is for users *with* a cascade artifact who need verdict-style diagnostic. Artifact-rich → audit; vague / cold-start → coach. Never run audit-mode on an absent cascade (no map = nothing to grade); never run coach-mode on a map the user explicitly wants graded.
- **Rule 3 — veto, don't dictate — is load-bearing across both modes.** Coach-mode enforces it during proposal solicitation; audit-mode diagnoses violations of it ("imposed on us" = Rule 3 violation). The agent never authors Team WIGs for sub-leaders.
- **Targets-not-plans across both modes.** Coach-mode rejects plan-shaped proposals; audit-mode flags plan-shaped Team WIGs in the existing map.
- **Cascade depth is single-hop only.** Beyond two cascade layers veto authority degrades into report-out theater. Re-run *this skill* at each layer rather than single-pass deep cascade.
- **2-3 Battles is the typical landing zone.** 5+ Battles is incomplete strategic narrowing; both modes flag it.
- **Authority asymmetry preserved.** This is not bidirectional negotiation (hoshin catchball / OKR consensus). Sub-leaders propose; leader-of-leaders accepts or vetoes. Both modes enforce this asymmetry.

## Audit metadata

- **Skill type**: multi-file orchestrator (path-B refactor 2026-04-30 — coach-mode protocol = original v0.6.1 single-file content; audit-mode protocol added)
- **Verification status**: V1 ✓ for coach-mode (Ch 7 three anchor cases — Opryland / retailer / Sydney accounting firm); V1 ✓ for audit-mode (Ch 7 four rules + Targets-not-Plans + Battles-count rule applied as verdict matrix; sub-leader complaint → rule mapping derived per same convention as `4dx-d1-wig-formulation` audit-mode)
- **Protocols**: `coach-mode.md` (Socratic 10-step cascade build), `audit-mode.md` (consultant verdict on existing cascade)
- **Test pass rate**: see `test-prompts.json`
- **Created / refactored at**: 2026-04-30 (path-B refactor)
- **Output language**: SKILL.md body + protocols in English; description + mode-detection prompts multilingual EN/JP/zh-TW
