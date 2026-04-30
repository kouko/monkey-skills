# 4DX D3 — Team Lead Scoreboard Design

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Team-leader scope — facilitate the team to build a public players' scoreboard for the Team WIG + 2-3 leads. ≤4 elements, 5-second test, leader vetoes don't dictates.

## When this skill activates

- "Help me design our team scoreboard"
- "How should our team display the WIG and lead measures?"
- "We have a Team WIG and leads — what should the scoreboard look like?"
- "My team has the goals but the dashboard isn't motivating anyone"
- 「team の scoreboard を設計したい」「チーム全員が見える進捗の出し方」
- 「幫我設計 team 的 scoreboard」「怎麼讓全隊都看得到進度」

## What it does (the protocol in brief)

Socratic facilitation with the leader — agent does NOT design the scoreboard; produces a spec the leader brings back to the team to build.

1. **Confirm Team WIG + 2-3 leads exist** — halt to D1 / D2 if either missing
2. **Confirm leader will let team build it** — name the Step 3 anti-pattern (leader-authored boards die in week 4)
3. **Lock public display location** — wall / TV / pinned channel / 4DX app for dispersed teams
4. **Specify 4 firm rules the leader holds** — ≤4 elements / visible / lead+lag with target lines / 5-second "are we winning?"
5. **Plan the team-build session** — book's 4 steps (Theme → Design → Build → Keep Updated); leader = facilitator, not author
6. **Lock update ritual** — who updates, when posted, ≥ weekly; team performs update, not leader, not pure auto-feed
7. **Output** — spec + agenda + holding-the-line prompts; recommend 7-day window before inertia kills it

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Personal-only / solo scoreboard | `4dx-d3-personal-scoreboard` |
| Member reading inherited team board | `4dx-d3-member-scoreboard-reading` |
| Enterprise BI / multi-team rollup | Coach's-scoreboard / drill-down — out of plugin |
| Team WIG / leads not yet defined | `4dx-d1-team-primary-wig-selection` / `4dx-d2-team-lead-measure-facilitation` |
| Stroke-of-pen team goal | Project plan, not scoreboard |
| Reactive / on-call team where whirlwind IS the strategic work | Phantom-guilt risk — skip |

## Source

Distilled from *The 4 Disciplines of Execution* (2nd ed.), Chapter 4 + Chapter 14. Three anchor cases: Serena's Event Management team (textbook 3-component team scoreboard with WIG/lag + Lead 1 individualized + Lead 2 90% sustained line), juice-bottling shifts (public visibility creates peer accountability without management push), Northrop Grumman / blown-down stadium (visible score is engagement substrate). Industry grounding: Tufte 1983/2001 (data-ink), Few 2006/2013 (dashboard vs database), Macey & Schneider 2008 (state + behavioral engagement from public feedback).

See [`SKILL.md`](SKILL.md) for the full RIA++ render including coach's-as-players' substitution at team scale (CE-08), leader-authored anti-pattern, communication-board drift, dispersed-team excuse, and the high-context-culture comparison-frame caveat.
