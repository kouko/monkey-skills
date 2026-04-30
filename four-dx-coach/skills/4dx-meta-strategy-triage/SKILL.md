---
name: 4dx-meta-strategy-triage
description: |
  [Topic-router] for the 4DX strategy-triage decision when scope (personal vs team) is unclear from the user's query. Activates on ambiguous "should X use 4DX?" queries that don't yet name an actor. After ONE Socratic disambiguation question, routes to either `4dx-meta-personal-strategy-triage` (solo individual goal) or `4dx-meta-team-strategy-triage` (a team / leader adopting it). EN: "Is 4DX right for this?", "Should we use 4DX?", "Is 4DX a good fit?". JP: 「4DX 適してる？」「4DX 使うべき？」「4DX 合ってる？」. ZH: 「4DX 適合嗎？」「我/我們該用 4DX 嗎？」「4DX 適合這個嗎？」. Do NOT activate when the user's scope is already explicit ("for myself" → fire personal directly; "for our team" → fire team directly), when user already past triage and asks how to start (route to whirlwind-triage / primary-wig-selection), or when user is a team-member receiving an existing WIG (members inherit; they don't triage methodology fit).
source_book: The 4 Disciplines of Execution (2nd ed., 2021) — McChesney/Covey/Huling/Thele/Walker
source_chapter: Chapter 1, Chapter 6 (foundational triage logic shared across scopes)
source_language: en
tags: [topic-router, scope-triage, methodology-fit, 4dx, meta-gate]
related_skills:
  - 4dx-meta-personal-strategy-triage
  - 4dx-meta-team-strategy-triage
  - using-four-dx-coach
---

# 4dx-meta-strategy-triage — Topic-router for 4DX-fit triage

## Mission

Catch ambiguous "should X use 4DX?" queries that don't name an actor, ask ONE disambiguating question to surface scope, then route. A topic-router skill — does not run the triage itself; delegates to the scope-specific triage skill once scope is clear.

## When this router activates

### Multilingual trigger phrasings

- **EN**: "Is 4DX right for this?", "Should we use 4DX?", "Is 4DX a good fit?", "Does 4DX work here?", "Is 4DX overkill?"
- **JP**: 「4DX 適してる？」「4DX 使うべき？」「4DX 合ってる？」「4DX で大丈夫？」
- **ZH**: 「4DX 適合嗎？」「我/我們該用 4DX 嗎？」「4DX 適合這個嗎？」「4DX 會不會太重？」

### Non-activation signals (DO NOT fire when…)

- User explicitly says "for myself" / 「自分のため」 / 「我自己」 → fire `4dx-meta-personal-strategy-triage` directly
- User explicitly says "for our team / company / org" / 「うちの team」 / 「我們團隊」 → fire `4dx-meta-team-strategy-triage` directly
- User has already passed triage and asks how to start → route to D1 skills (whirlwind-triage / primary-wig-selection)
- User is a team-member who inherits a WIG already chosen by a leader → use member skills; member doesn't triage methodology fit
- User asks about non-4DX methodologies (OKR / agile / habit stacking) → router (`using-four-dx-coach`) handles hand-off

## Indexed atomic skills

| Slug | Scope | Canonical activation signal | Returns |
|---|---|---|---|
| [`4dx-meta-personal-strategy-triage`](../4dx-meta-personal-strategy-triage/) | Personal (solo) | "Is 4DX right for *my* goal?" / 「自分の目標に 4DX は？」 / 「我的目標適合 4DX 嗎？」 | One of 6 verdicts: APPLICABLE / habit / portfolio-bet / emergency / creative / no-time-sovereignty |
| [`4dx-meta-team-strategy-triage`](../4dx-meta-team-strategy-triage/) | Team-leader | "Should *our team* adopt 4DX?" / 「うちの team で 4DX を回す？」 / 「我們團隊要不要導入 4DX？」 | Team-fit verdict + leader-readiness check |

(Member scope intentionally absent — members do not triage methodology fit; they inherit the WIG.)

## Routing logic (Socratic decision tree)

When this router activates, do NOT run the triage. Run scope disambiguation:

1. **Detect implicit scope from context** — re-read the user's query for any of:
   - First-person singular ("I" / 「私」 / 「我」 alone) → **probable personal**
   - First-person plural with team context ("we" + "team / department / org" / 「うち」 / 「我們團隊」) → **probable team**
   - Past tense "I was given X by my manager" / 「上司に渡された WIG」 / 「上面說要做 ...」 → **member** — STOP, route differently (see step 4).
   - If signal is strong, skip to step 3.

2. **If scope is genuinely ambiguous, ask ONE question**:
   > "Quick clarification — are you thinking about this for **yourself as an individual** (one person, one goal), or for **a team you lead / are part of**? I'll route to the right triage."
   > 日本語: 「先に確認 —— **自分一人の目標**（一人、一つのゴール）として 4DX を検討中ですか？それとも **率いる / 所属する team** として？適切な triage に振り分けます。」
   > 中文: 「先確認一下 —— 你是想用 4DX 解決 **個人一個目標**（一人、一目標），還是 **團隊**（你帶或你在）的事？我幫你導到對的 triage。」

3. **Hand off to the scope-specific triage skill**:
   - "Personal" / 個人 / 個人 → fire `4dx-meta-personal-strategy-triage`
   - "Team" / 団体 / 團隊 → fire `4dx-meta-team-strategy-triage`

4. **If user identifies as a member** ("my manager already picked the WIG" / 「上司が WIG を決めた」 / 「老闆已經訂好 WIG」):
   - Triage is moot. Route directly to `4dx-d1-member-team-wig-comprehension` to make sense of the inherited WIG, OR to plugin router `using-four-dx-coach` if they're unsure where to start.

5. **If user wants something 4DX is wrong for** (habit, portfolio, agile, OKR):
   - Hand off via plugin router `using-four-dx-coach`. Don't pretend triage applies.

## Hand-off scripts (when neither personal nor team fits)

| User signal | Hand-off |
|---|---|
| "I want to build a meditation habit" | "4DX is overkill for habit formation. Try `atomic-habits` / habit stacking instead." |
| "We have 3 startups in a portfolio" | "4DX assumes one bet. Use OKR or lean experimentation for portfolio betting." |
| "I'm a member, the WIG is already chosen" | Route to `4dx-d1-member-team-wig-comprehension`. |
| "We're rolling 4DX out across 50 teams" | "Multi-team rollout — read book Part 2 (Ch 6-10) directly or contact FranklinCovey." |
| "Sprint planning / OKR check-in" | Different methodology — hand off via `using-four-dx-coach`. |

## Boundary

### Do NOT activate this router when…

- **Scope is explicit** — direct activation of personal or team triage is precise; this router adds friction.
- **User is a member** — members don't triage; they comprehend their inherited WIG.
- **Goal already passed triage** — user wants to start, not assess. Route to D1.
- **Non-4DX methodologies** — habit, OKR, agile, scrum, kanban, sprint planning — hand off to plugin router.
- **In the middle of an active triage session** — do not re-route mid-flow; the active triage skill should complete its verdict first.

### Common confusions

- **Router-vs-atomic competition**: if the user's query already names "myself" or "our team", the atomic strategy-triage skill should fire first. This router is an explicit fallback, not a default gate.
- **Topic-router vs plugin-router**: `using-four-dx-coach` triages all 18 skills across all stages; this router only triages within the meta-strategy-triage topic. If user query is generic ("I want to start 4DX"), `using-four-dx-coach` should fire, not this.

## Related skills

- `4dx-meta-personal-strategy-triage` — composes-with — downstream after personal scope determined
- `4dx-meta-team-strategy-triage` — composes-with — downstream after team scope determined
- `using-four-dx-coach` — composes-with — plugin-level router; complements this topic-router (different granularity)
- `4dx-d1-member-team-wig-comprehension` — composes-with — fall-through if user is a member, not a triager

## Audit metadata

- **Skill type**: topic-router (no V1/V2/V3 verification — meta-skill)
- **Routing precision target**: ≥90% — disambiguation question must reliably surface scope
- **Test pass rate**: see `test-prompts.json`
- **Created at**: 2026-04-30
- **Output language**: body — English; description + decision-tree prompts — multilingual EN/JP/zh-TW
