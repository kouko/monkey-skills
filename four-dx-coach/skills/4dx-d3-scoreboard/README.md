# 4dx-d3-scoreboard (Topic Router)

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Topic-router for D3 scoreboard queries when role (solo / leader-designer / member-reader) is unclear.

## What this router does

Catches ambiguous "help me with the scoreboard" / "how should I track this?" queries. Asks ONE Socratic question on role + verb (build vs read), then routes to one of three atomic D3 skills. Does NOT run any D3 protocol itself.

## When this router activates

- "Help me with the scoreboard" / "How should I track this?" / "Dashboard advice" / "Players' scoreboard"
- 「scoreboard を設計したい」「どう可視化すれば」「ダッシュボードの相談」
- 「幫我搞 scoreboard」「怎麼追蹤」「儀表板要怎麼設計」「球員視角記分板」
- Any D3 scoreboard query without a clear role + verb

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Role + verb explicit ("my personal scoreboard") | `4dx-d3-scoreboard` directly |
| Role + verb explicit ("design our team's scoreboard") | `4dx-d3-scoreboard` directly |
| Role + verb explicit ("read the team scoreboard") | `4dx-d3-scoreboard` directly |
| WIG / leads not yet set | `4dx-d1-wig-formulation` / `4dx-d2-lead-measures` first |
| Cadence / WIG Session question | `4dx-d4-cadence` topic-router |
| Enterprise BI dashboard (Tableau / PowerBI / multi-team rollup) | Out of 4DX — `using-four-dx-coach` |

## Indexed atomic skills

| Slug | Role | Verb | Returns |
|---|---|---|---|
| `4dx-d3-scoreboard` | Solo | Design own | Glance-readable personal scoreboard (≤4 elements; 5-second test) |
| `4dx-d3-scoreboard` | Team-leader | Facilitate team-built | Public team scoreboard built BY the team (veto-not-dictate) |
| `4dx-d3-scoreboard` | Team-member | Read + locate | Member's read + own contribution location + escalation if broken |

## See also

- [`SKILL.md`](SKILL.md) for full routing logic + Socratic decision tree + hand-off scripts
- Plugin router [`using-four-dx-coach`](../using-four-dx-coach/) for cold-start / out-of-4DX queries
- Sibling topic-router [`4dx-d2-lead-measures`](../4dx-d2-lead-measures/) for D2 lead-measure role-triage
