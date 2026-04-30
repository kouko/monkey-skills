---
name: 4dx-d3-scoreboard
description: |
  [Topic-router] for D3 scoreboard queries when role (solo / leader-designer / member-reader) is unclear. Activates on ambiguous "scoreboard" / "dashboard" / "tracking display" queries that don't yet name *who builds and who consumes*. After ONE Socratic disambiguation question, routes to: `4dx-d3-personal-scoreboard` (solo: design own scoreboard), `4dx-d3-team-lead-scoreboard-design` (leader: design multi-stakeholder team scoreboard), or `4dx-d3-member-scoreboard-reading` (member: read inherited team scoreboard + locate own contribution). EN: "Help me with the scoreboard", "How should I track this?", "Dashboard advice". JP: 「scoreboard を設計したい」「どう可視化すれば」. ZH: 「幫我搞 scoreboard」「怎麼追蹤」. Do NOT activate when role is explicit, when WIG / lead measures are not yet set (use D1 / D2 first), when query is about cadence (use `4dx-d4-cadence`), or for enterprise BI dashboards (out of 4DX scope).
source_book: The 4 Disciplines of Execution (2nd ed., 2021) — McChesney/Covey/Huling/Thele/Walker
source_chapter: Chapter 4, Chapter 14 (D3 fundamentals + frontline application across roles)
source_language: en
tags: [topic-router, scoreboard, role-triage, d3, 4dx]
related_skills:
  - 4dx-d3-personal-scoreboard
  - 4dx-d3-team-lead-scoreboard-design
  - 4dx-d3-member-scoreboard-reading
  - using-four-dx-coach
---

# 4dx-d3-scoreboard — Topic-router for D3 scoreboard across roles

## Mission

Catch ambiguous scoreboard queries where the user has not yet signaled their **role** (solo designer / team-leader designer / member reader). Ask ONE Socratic question to surface role + verb (build vs read), then route. The 3 atomic skills routed share the players' scoreboard 5-second-test grammar but differ in *who designs*, *who consumes*, and *what the visibility surface is* (private vs public).

## When this router activates

### Multilingual trigger phrasings

- **EN**: "Help me with the scoreboard", "How should I track this?", "Dashboard advice", "Build a scoreboard", "Players' scoreboard"
- **JP**: 「scoreboard を設計したい」「どう可視化すれば」「ダッシュボードの相談」「players' scoreboard」
- **ZH**: 「幫我搞 scoreboard」「怎麼追蹤」「儀表板要怎麼設計」「球員視角記分板」

### Non-activation signals (DO NOT fire when…)

- Role + verb explicit — "*my* personal scoreboard" → personal; "design *our team's* scoreboard" → team-design; "read *the* team scoreboard" → member-reading
- WIG / lead measures not yet set → run D1 / D2 first; D3 has nothing to display
- Query is about cadence / WIG Session → `4dx-d4-cadence`
- Enterprise BI / KPI dashboards (Tableau / PowerBI / Looker enterprise) → out of 4DX; `using-four-dx-coach`
- Multi-team aggregated rollups → out of plugin; hand off
- Out-of-4DX dashboards (agile burndown / OKR check-in dashboard / status report) → hand off

## Indexed atomic skills

| Slug | Role | Verb | Returns |
|---|---|---|---|
| [`4dx-d3-personal-scoreboard`](../4dx-d3-personal-scoreboard/) | Solo | **Design own** | Glance-readable personal scoreboard (≤4 elements; lead+lag+pacing; 5-second test) |
| [`4dx-d3-team-lead-scoreboard-design`](../4dx-d3-team-lead-scoreboard-design/) | Team-leader | **Facilitate team-built** | Team scoreboard built BY the team (veto-not-dictate); public; multi-stakeholder legible |
| [`4dx-d3-member-scoreboard-reading`](../4dx-d3-member-scoreboard-reading/) | Team-member | **Read + locate** | Member's read of the team scoreboard + own contribution location + escalation if scoreboard is broken |

## Routing logic (Socratic decision tree)

When this router activates, do NOT run any D3 protocol. Disambiguate first:

1. **Detect implicit role + verb**:
   - "My scoreboard / private tracker / for myself" → **personal-design**
   - "Our team's board / I lead the team / facilitate scoreboard build / public display" → **team-lead-design**
   - "The team's board / read / look at / interpret what I see / 上から見せられた / 我們 team 的板子" → **member-reading**
   - If signal strong → skip to step 3.

2. **If ambiguous, ask ONE question**:
   > "Quick check — what's your role with respect to the scoreboard: **designing your own private one** (solo), **facilitating your team to build a public one** (leader), or **reading the one your team already has** (member)? I'll route to the right protocol."
   > 日本語: 「scoreboard に対する role を確認 —— **自分専用のものを design**（solo）、**team が public な scoreboard を build するのを facilitate**（leader）、**既に team が持っているものを read**（member）のどれ？」
   > 中文: 「先確認 —— 你跟 scoreboard 的關係：**設計自己用的**（solo）、**帶 team 一起 build 公用的**（leader）、**讀 team 已經有的**（member）？我幫你導到對的 protocol。」

3. **Hand off**:
   - solo → `4dx-d3-personal-scoreboard`
   - team-leader → `4dx-d3-team-lead-scoreboard-design`
   - team-member → `4dx-d3-member-scoreboard-reading`

4. **Edge cases**:
   - "WIG / leads not set" → run D1 / D2 first; D3 cannot precede them
   - "Multi-team aggregated dashboard" → out of 4DX; hand off via `using-four-dx-coach`
   - "Member sees broken scoreboard, wants to redesign" → fire `4dx-d3-member-scoreboard-reading` (which has escalation script for this); member shouldn't redesign unilaterally

## Hand-off scripts (when none of the 3 D3 skills fit)

| User signal | Hand-off |
|---|---|
| "No WIG / lead measures yet" | `4dx-d1-wig-formulation` / `4dx-d2-lead-measures` |
| "Weekly review / WIG Session" | `4dx-d4-cadence` |
| "Tableau / PowerBI / enterprise BI" | Out of 4DX — `using-four-dx-coach` |
| "Agile burndown / sprint chart" | Out of 4DX — `using-four-dx-coach` |
| "Status report dashboard for execs" | Out of 4DX — different tool |
| "Multi-team rolled-up dashboard" | Out of plugin — read book Part 2 |

## Boundary

### Do NOT activate this router when…

- Role + verb both explicit → fire atomic skill directly
- D3 prerequisite missing — no WIG / no leads → D1 / D2 first
- Query is about D4 / sustain — wrong stage
- User mid-flow inside an active D3 atomic skill — don't interrupt

### Common confusions

- **Personal vs team scoreboard**: not a scale difference — a different artifact (private vs public, single-stakeholder vs multi-stakeholder, designer-builder vs facilitator-built).
- **Member reads vs designs**: members do NOT design the team scoreboard. If they think it should be different, they escalate to the leader (or use `4dx-d3-member-scoreboard-reading` step that surfaces the broken-scoreboard signal).
- **4DX scoreboard vs BI dashboard**: 4DX is purpose-isolated (one WIG / one team / glance-test). BI dashboards are database-style multi-purpose displays. Different breeds — don't conflate.
- **Topic-router vs plugin-router**: `using-four-dx-coach` triages cold-start and out-of-4DX. This router operates only within the D3 scoreboard topic.

## Related skills

- `4dx-d3-personal-scoreboard` — composes-with — downstream after solo determined
- `4dx-d3-team-lead-scoreboard-design` — composes-with — downstream after team-leader determined
- `4dx-d3-member-scoreboard-reading` — composes-with — downstream after member determined
- `4dx-d2-lead-measures` — depends-on — D2 must precede D3 (need leads to display)
- `4dx-d1-wig-formulation` — depends-on — D1 must precede D2/D3
- `4dx-d4-cadence` — composes-with — D4 reviews scoreboard weekly
- `using-four-dx-coach` — composes-with — plugin-level router

## Audit metadata

- **Skill type**: topic-router (no V1/V2/V3 — meta-skill)
- **Routing precision target**: ≥90% — disambiguation must reliably surface role + verb
- **Test pass rate**: see `test-prompts.json`
- **Created at**: 2026-04-30
- **Output language**: body — English; description + decision-tree prompts — multilingual EN/JP/zh-TW
