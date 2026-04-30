---
name: 4dx-d1-wig-formulation
description: |
  [Topic-router] for D1 WIG-formulation queries when scope (personal vs team-leader vs team-member) is unclear. Activates on ambiguous "help me with my WIG" / "how to set a WIG" queries that don't yet name an actor or whether the WIG is being defined / selected / inherited. After ONE Socratic disambiguation, routes to: `4dx-d1-personal-wig-defining` (solo: define From X to Y by When), `4dx-d1-team-primary-wig-selection` (leader: pick org Primary WIG via Battles 2x2), or `4dx-d1-member-team-wig-comprehension` (member: comprehend an inherited team WIG). EN: "Help me with my WIG", "How do I set a WIG?", "WIG selection", "WIG planning". JP: 「WIG を決めたい」「WIG の作り方」「WIG をどう選ぶ」. ZH: 「幫我搞 WIG」「怎麼設 WIG」「怎麼選 WIG」. Do NOT activate when scope already clear, for whirlwind audit (use `4dx-d1-personal-whirlwind-triage`), for cascading downward to subordinate teams (use `4dx-d1-team-wig-cascade`), or for lead measures / scoreboard / cadence (route to D2 / D3 / D4 respectively).
source_book: The 4 Disciplines of Execution (2nd ed., 2021) — McChesney/Covey/Huling/Thele/Walker
source_chapter: Chapter 2, Chapter 6, Chapter 12 (WIG-formulation foundations across scopes)
source_language: en
tags: [topic-router, wig, scope-triage, d1, 4dx]
related_skills:
  - 4dx-d1-personal-wig-defining
  - 4dx-d1-team-primary-wig-selection
  - 4dx-d1-member-team-wig-comprehension
  - using-four-dx-coach
---

# 4dx-d1-wig-formulation — Topic-router for D1 WIG-formulation across scopes

## Mission

Catch ambiguous WIG-related queries where the user has not yet signaled (a) who owns the WIG and (b) whether it's being newly defined, selected from candidates, or inherited from above. Ask ONE Socratic question to surface scope + verb, then route. The 3 atomic skills it routes to share the From-X-to-Y-by-When grammar but differ in *who acts* and *what action they take*.

## When this router activates

### Multilingual trigger phrasings

- **EN**: "Help me with my WIG", "How do I set a WIG?", "WIG selection", "WIG planning", "Pick the right goal", "Define my WIG"
- **JP**: 「WIG を決めたい」「WIG の作り方」「WIG をどう選ぶ」「目標 (WIG) の作成」「Goal を絞りたい」
- **ZH**: 「幫我搞 WIG」「怎麼設 WIG」「怎麼選 WIG」「WIG 怎麼定」「目標太多怎麼挑」

### Non-activation signals (DO NOT fire when…)

- Scope explicit — "*my* WIG" + solo context → personal-wig-defining; "our org WIG" → team-primary-wig-selection; "the WIG my manager assigned" → member-team-wig-comprehension
- Whirlwind / time-audit query → `4dx-d1-personal-whirlwind-triage` (D1 prereq, different topic)
- Cascading down to N teams → `4dx-d1-team-wig-cascade` (different verb: translate, not select)
- Lead measure / daily action query → `4dx-d2-personal-lead-measure-discovery`
- Scoreboard / tracking query → `4dx-d3-personal-scoreboard`
- WIG Session / weekly cadence → D4 routes (`4dx-d4-cadence` topic-router or atomic skills)

## Indexed atomic skills

| Slug | Scope | Verb | Returns |
|---|---|---|---|
| [`4dx-d1-personal-wig-defining`](../4dx-d1-personal-wig-defining/) | Personal (solo) | **Define** | One personal WIG in From-X-to-Y-by-When form, screened against three pitfalls (whirlwind smuggling / vanity / partner-dependent) |
| [`4dx-d1-team-primary-wig-selection`](../4dx-d1-team-primary-wig-selection/) | Team-leader | **Select** | Org-level Primary WIG via Battles 2x2 (importance × feasibility) |
| [`4dx-d1-member-team-wig-comprehension`](../4dx-d1-member-team-wig-comprehension/) | Team-member | **Comprehend / inherit** | Member's understanding of how the inherited team WIG ladders to their daily slice |

## Routing logic (Socratic decision tree)

When this router activates, do NOT run any WIG protocol. Disambiguate first:

1. **Detect implicit scope + verb from context**:
   - "My WIG / for myself / solo goal" → **personal-define**
   - "Our team's WIG / I'm picking for the team / 2x2 / Battles / Primary WIG" → **team-select**
   - "The WIG my boss / manager / leader gave me / inherited / handed down / 上から / 老闆訂的" → **member-comprehend**
   - If signal strong → skip to step 3.

2. **If ambiguous, ask ONE question**:
   > "Two quick checks: (a) **who is the WIG for** — yourself solo, your team (you lead), or you-as-team-member? (b) **are you defining a new WIG, selecting from options, or making sense of one given to you?** I'll route to the right protocol."
   > 日本語: 「2 点確認: (a) **WIG は誰のため** — 自分一人、率いる team、それとも所属 team の member として？ (b) **新規定義 / 候補から選定 / 既に降りてきた WIG の把握** のどれ？適切な protocol に振り分けます。」
   > 中文: 「兩個快速確認：(a) **WIG 是給誰的** — 你自己（solo）、你帶的 team、還是你所在的 team（別人定的）？(b) **要新訂、要從候選裡挑、還是要搞懂上面給的**？我幫你導到對的 protocol。」

3. **Hand off**:
   - solo + define → `4dx-d1-personal-wig-defining`
   - team + select → `4dx-d1-team-primary-wig-selection`
   - team + member + comprehend → `4dx-d1-member-team-wig-comprehension`

4. **Edge cases**:
   - "Solo + select from options" → use personal-wig-defining (it handles candidate evaluation internally; selection is sub-step of defining)
   - "Leader + cascade to 3-7 sub-teams" → fire `4dx-d1-team-wig-cascade` directly (different topic; not in this router's scope)
   - "Member + redefine an inherited WIG" → bad fit; the member doesn't redefine. Route to `4dx-d1-member-team-wig-comprehension` to first understand the WIG, then upward the conversation to the leader if change needed.
   - "Multi-team rollout / Leader-of-Leaders" → out of plugin scope; hand off via `using-four-dx-coach`.

## Hand-off scripts (when none of the 3 D1-WIG skills fit)

| User signal | Hand-off |
|---|---|
| "Whirlwind audit / how do I find time" | `4dx-d1-personal-whirlwind-triage` |
| "Cascade WIG to my N sub-teams" | `4dx-d1-team-wig-cascade` |
| "Lead measures / what daily action" | `4dx-d2-personal-lead-measure-discovery` |
| "Scoreboard design" | `4dx-d3-personal-scoreboard` |
| "Weekly review / WIG Session" | `4dx-d4-cadence` (topic-router) or D4 atomic skills |
| "I haven't decided whether 4DX fits" | `4dx-meta-strategy-triage` (topic-router) |
| "Habit / OKR / agile / portfolio" | Hand off via `using-four-dx-coach` |

## Boundary

### Do NOT activate this router when…

- Scope + verb both explicit → fire the precise atomic skill directly
- Query is about D1 prerequisite (whirlwind audit) — different topic, single scope (personal)
- Query is about D1 cascade (translation downward) — single scope (team-leader), single skill
- Query is about D2 / D3 / D4 — wrong stage
- User mid-flow inside an active WIG-formulation skill — don't interrupt

### Common confusions

- **Router vs. atomic**: if user says "help me write my personal WIG with X→Y→When", fire personal-wig-defining directly. This router is a fallback for *ambiguous* queries.
- **Topic-router vs. plugin-router**: `using-four-dx-coach` triages cold-start and out-of-4DX queries. This router only operates *within* the D1 WIG-formulation topic.
- **Verb confusion**: "select" vs "define" — when a personal user is "selecting" between several candidate goals, that's still personal-wig-defining (the protocol includes candidate evaluation). "Select" only routes to team-primary-wig-selection when N candidates exist at *org level* with Battles 2x2.

## Related skills

- `4dx-d1-personal-wig-defining` — composes-with — downstream after personal+define determined
- `4dx-d1-team-primary-wig-selection` — composes-with — downstream after team+select determined
- `4dx-d1-member-team-wig-comprehension` — composes-with — downstream after member+comprehend determined
- `4dx-meta-strategy-triage` — depends-on — triage usually precedes WIG formulation
- `using-four-dx-coach` — composes-with — plugin-level router complements this

## Audit metadata

- **Skill type**: topic-router (no V1/V2/V3 verification — meta-skill)
- **Routing precision target**: ≥90% — disambiguation must reliably surface (scope, verb)
- **Test pass rate**: see `test-prompts.json`
- **Created at**: 2026-04-30
- **Output language**: body — English; description + decision-tree prompts — multilingual EN/JP/zh-TW
