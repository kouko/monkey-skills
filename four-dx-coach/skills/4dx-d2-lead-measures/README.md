# 4dx-d2-lead-measures (Topic Router)

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Topic-router for D2 lead-measure queries when role (solo / leader-facilitator / member-influencer) is unclear.

## What this router does

Catches ambiguous "help me with lead measures" / "how do I find lead measures?" queries. Asks ONE Socratic question on role, then routes to one of three atomic D2 skills. Does NOT run any D2 protocol itself.

## When this router activates

- "Help me with lead measures" / "How do I find lead measures?" / "Daily action that drives the goal" / "Lead measure advice"
- 「lead measure を決めたい」「lead measure の探し方」「先行指標の選び方」
- 「幫我找 lead measure」「怎麼挑領先指標」「每天該做什麼才會推動目標」
- Any D2 lead-measure query without a clear role

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Role explicit ("my lead for my goal") | `4dx-d2-lead-measures` directly |
| Role explicit ("facilitate our team picking leads") | `4dx-d2-lead-measures` directly |
| Role explicit ("the lead my manager set") | `4dx-d2-lead-measures` directly |
| WIG not yet defined | `4dx-d1-wig-formulation` first |
| Scoreboard / display question | `4dx-d3-scoreboard` topic-router |
| Weekly cadence / WIG Session | `4dx-d4-cadence` topic-router |

## Indexed atomic skills

| Slug | Role | Verb | Returns |
|---|---|---|---|
| `4dx-d2-lead-measures` | Solo | Discover | 2-3 personal leads (predictive AND influenceable, Goodhart self-check) |
| `4dx-d2-lead-measures` | Team-leader | Facilitate | Team-owned 2-3 leads (veto-not-dictate), aligned to team WIG |
| `4dx-d2-lead-measures` | Team-member | Influence-map | Per-lead 0-5 score + 1-2 focus leads + escalation if no influence |

## See also

- [`SKILL.md`](SKILL.md) for full routing logic + Socratic decision tree + hand-off scripts
- Plugin router [`using-four-dx-coach`](../using-four-dx-coach/) for cold-start / out-of-4DX queries
- Sibling topic-router [`4dx-d3-scoreboard`](../4dx-d3-scoreboard/) for D3 scoreboard role-triage
