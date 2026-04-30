# 4dx-d1-wig-formulation (Topic Router)

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Topic-router for D1 WIG-formulation queries when scope (personal / team-leader / team-member) and verb (define / select / comprehend) are unclear.

## What this router does

Catches ambiguous "help me with my WIG" / "how do I set a WIG?" queries. Asks ONE Socratic question on (scope, verb), then routes to one of three atomic D1 skills. Does NOT run any WIG protocol itself.

## When this router activates

- "Help me with my WIG" / "How do I set a WIG?" / "WIG selection" / "Pick the right goal"
- 「WIG を決めたい」「WIG の作り方」「WIG をどう選ぶ」「目標 (WIG) の作成」
- 「幫我搞 WIG」「怎麼設 WIG」「怎麼選 WIG」「目標太多怎麼挑」
- Any WIG-formulation query without a clear actor + verb

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Scope + verb explicit ("my personal WIG: From X to Y") | `4dx-d1-wig-formulation` directly |
| "Our org's Primary WIG via Battles 2x2" | `4dx-d1-wig-formulation` directly |
| "The WIG my manager assigned" | `4dx-d1-wig-formulation` directly |
| Whirlwind / time-audit query | `4dx-meta-whirlwind-triage` |
| Cascading downward to N sub-teams | `4dx-d1-wig-cascade` |
| Lead measures / scoreboard / cadence | D2 / D3 / D4 skills |

## Indexed atomic skills

| Slug | Scope | Verb | Returns |
|---|---|---|---|
| `4dx-d1-wig-formulation` | Personal (solo) | Define | One personal WIG in From-X-to-Y-by-When form |
| `4dx-d1-wig-formulation` | Team-leader | Select | Org-level Primary WIG via Battles 2x2 |
| `4dx-d1-wig-formulation` | Team-member | Comprehend | Member's understanding of how the inherited team WIG ladders to their slice |

## See also

- [`SKILL.md`](SKILL.md) for full routing logic + Socratic decision tree + hand-off scripts
- Plugin router [`using-four-dx-coach`](../using-four-dx-coach/) for cold-start / out-of-4DX queries
