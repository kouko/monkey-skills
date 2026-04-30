---
name: 4dx-d2-lead-measures
description: |
  [Topic-router] for D2 lead-measure queries when role (solo / leader-facilitator / member-influencer) is unclear from the user's query. Activates on ambiguous "lead measure" / "daily action driver" queries that don't yet name *who is doing what with the leads*. After ONE Socratic disambiguation question, routes to: `4dx-d2-personal-lead-measure-discovery` (solo: pick own leads), `4dx-d2-team-lead-measure-facilitation` (leader: facilitate team picking leads), or `4dx-d2-member-lead-measure-influence` (member: identify personal sphere on inherited leads). EN: "Help me with lead measures", "How do I find lead measures?", "Daily action that drives the goal". JP: 「lead measure を決めたい」「lead measure の探し方」. ZH: 「幫我找 lead measure」「怎麼挑領先指標」. Do NOT activate when role is explicit, when WIG is not yet defined (use `4dx-d1-wig-formulation` first), when the question is about scoreboard/visualization (use `4dx-d3-scoreboard`), or when query is about cadence/WIG-Session (use `4dx-d4-cadence`).
source_book: The 4 Disciplines of Execution (2nd ed., 2021) — McChesney/Covey/Huling/Thele/Walker
source_chapter: Chapter 3, Chapter 13 (D2 fundamentals + frontline application across roles)
source_language: en
tags: [topic-router, lead-measure, role-triage, d2, 4dx]
related_skills:
  - 4dx-d2-personal-lead-measure-discovery
  - 4dx-d2-team-lead-measure-facilitation
  - 4dx-d2-member-lead-measure-influence
  - using-four-dx-coach
---

# 4dx-d2-lead-measures — Topic-router for D2 lead-measure across roles

## Mission

Catch ambiguous lead-measure queries where the user has not yet signaled their **role** with respect to the lead measures (solo picker / team facilitator / member receiving inherited leads). Ask ONE Socratic question to surface role, then route. The 3 atomic skills routed share the predictive-AND-influenceable two-axis test but differ in *who picks*, *who facilitates*, and *who works with what's already given*.

## When this router activates

### Multilingual trigger phrasings

- **EN**: "Help me with lead measures", "How do I find lead measures?", "Daily action that drives the goal", "Pick lead indicators", "Lead measure advice"
- **JP**: 「lead measure を決めたい」「lead measure の探し方」「先行指標の選び方」「日常行動に落としたい」
- **ZH**: 「幫我找 lead measure」「怎麼挑領先指標」「先行指標怎麼設」「每天該做什麼才會推動目標」

### Non-activation signals (DO NOT fire when…)

- Role explicit — "*my* lead measure for *my* goal" → personal-discovery; "facilitate *our team* picking leads" → team-facilitation; "the lead measure *my manager set*" → member-influence
- WIG not yet defined → `4dx-d1-wig-formulation` first; D2 has nothing to operate on without a WIG
- Query about scoreboard / visualization → `4dx-d3-scoreboard` topic-router
- Query about WIG Session / weekly cadence → `4dx-d4-cadence` topic-router
- Query about cascade or selection at org level → `4dx-d1-team-wig-cascade` / `4dx-d1-team-primary-wig-selection`
- Out-of-4DX (OKR KRs, agile sprint goals, KPIs without 4DX context) → `using-four-dx-coach`

## Indexed atomic skills

| Slug | Role | Verb | Returns |
|---|---|---|---|
| [`4dx-d2-personal-lead-measure-discovery`](../4dx-d2-personal-lead-measure-discovery/) | Solo | **Discover** | 2-3 personal lead measures, predictive-AND-influenceable, with Goodhart self-check |
| [`4dx-d2-team-lead-measure-facilitation`](../4dx-d2-team-lead-measure-facilitation/) | Team-leader | **Facilitate** | Team-owned 2-3 lead measures (veto-not-dictate), aligned to team WIG, with team buy-in |
| [`4dx-d2-member-lead-measure-influence`](../4dx-d2-member-lead-measure-influence/) | Team-member | **Influence-map** | Personal sphere of influence on each inherited lead + 1-2 focus leads + escalation script if no influence exists |

## Routing logic (Socratic decision tree)

When this router activates, do NOT run any D2 protocol. Disambiguate first:

1. **Detect implicit role**:
   - "My lead / for my goal / solo" → **personal-discovery**
   - "Facilitate / our team / I lead the team / picking leads with the team" → **team-facilitation**
   - "Lead my boss / leader / manager set / inherited / 上から / 老闆訂的" → **member-influence**
   - If signal strong → skip to step 3.

2. **If ambiguous, ask ONE question**:
   > "Quick clarification — what's your role with respect to the lead measure: **picking it for yourself** (solo), **facilitating your team** (leader of 3-9 reports), or **working with one your team already has** (member)? I'll route to the right protocol."
   > 日本語: 「先に確認 —— lead measure に対するあなたの役割は: **自分の goal 用に自分で選ぶ**（solo）、**team を率いて選定を facilitate**（leader、3-9 名の direct reports）、それとも **既に team にあるものに対して関わる**（member）？適切な protocol に振り分けます。」
   > 中文: 「先確認一下 —— 你跟 lead measure 的關係：**自己挑給自己用**（solo）、**帶 team 一起挑**（leader，3-9 名 direct report）、還是 **接收 team 已經訂好的**（member）？我幫你導到對的 protocol。」

3. **Hand off**:
   - solo → `4dx-d2-personal-lead-measure-discovery`
   - team-leader → `4dx-d2-team-lead-measure-facilitation`
   - team-member → `4dx-d2-member-lead-measure-influence`

4. **Edge cases**:
   - "WIG not yet set" → fire `4dx-d1-wig-formulation` first; D2 has no anchor
   - "Want to design the scoreboard for these leads" → fire `4dx-d3-scoreboard` topic-router
   - "Multi-team / Leader-of-Leaders cascading leads" → out of plugin scope; hand off via `using-four-dx-coach`

## Hand-off scripts (when none of the 3 D2 skills fit)

| User signal | Hand-off |
|---|---|
| "WIG not yet defined" | `4dx-d1-wig-formulation` |
| "How do I display these leads?" | `4dx-d3-scoreboard` |
| "Weekly review / commitment / WIG Session" | `4dx-d4-cadence` |
| "Habit / atomic habit" | Out of 4DX — `using-four-dx-coach` |
| "OKR KR / sprint goal" | Out of 4DX — `using-four-dx-coach` |
| "Multi-team rollout" | Read book Part 2 directly — `using-four-dx-coach` |

## Boundary

### Do NOT activate this router when…

- Role explicit → fire the precise atomic skill directly
- D2 prerequisite missing — no WIG → D1 first
- Query is about D3 / D4 — wrong stage
- User mid-flow inside an active D2 atomic skill — don't interrupt

### Common confusions

- **Personal-discovery vs member-influence**: a solo user's "discovery" is genuinely picking a lead from blank canvas. A member's "influence" is working with a lead that already exists — different starting condition.
- **Team-facilitation vs personal-discovery**: leader running a facilitation session is NOT the same as the leader thinking about leads alone — facilitation requires team buy-in, conflict resolution, veto-not-dictate.
- **Topic-router vs plugin-router**: `using-four-dx-coach` triages cold-start and out-of-4DX queries. This router operates only within the D2 lead-measure topic.

## Related skills

- `4dx-d2-personal-lead-measure-discovery` — composes-with — downstream after solo determined
- `4dx-d2-team-lead-measure-facilitation` — composes-with — downstream after team-leader determined
- `4dx-d2-member-lead-measure-influence` — composes-with — downstream after member determined
- `4dx-d1-wig-formulation` — depends-on — D1 must precede D2
- `4dx-d3-scoreboard` — composes-with — D3 typically follows D2
- `using-four-dx-coach` — composes-with — plugin-level router for out-of-4DX

## Audit metadata

- **Skill type**: topic-router (no V1/V2/V3 — meta-skill)
- **Routing precision target**: ≥90% — disambiguation must reliably surface role
- **Test pass rate**: see `test-prompts.json`
- **Created at**: 2026-04-30
- **Output language**: body — English; description + decision-tree prompts — multilingual EN/JP/zh-TW
