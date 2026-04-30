# 4dx-meta-strategy-triage (Topic Router)

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Topic-router for 4DX-fit triage when the user's scope (personal vs team) is not yet clear.

## What this router does

Catches ambiguous "should X use 4DX?" queries that don't yet name an actor. Asks ONE Socratic question to surface scope, then hands off to the scope-specific triage skill. This router does NOT run the triage itself.

## When this router activates

- "Is 4DX a good fit?" / "Should we use 4DX?" / "Is 4DX overkill?"
- 「4DX 適してる？」「4DX 使うべき？」「4DX 合ってる？」
- 「4DX 適合嗎？」「我/我們該用 4DX 嗎？」「4DX 會不會太重？」
- Any methodology-fit query without a clear actor (no "I personally" / "our team" anchor)

## When NOT to use

| Situation | Where to go instead |
|---|---|
| User says "for myself" / 自分 / 我自己 | `4dx-meta-personal-strategy-triage` directly |
| User says "for our team / org" / うちの team / 我們團隊 | `4dx-meta-team-strategy-triage` directly |
| User is past triage and wants to start | `4dx-d1-personal-whirlwind-triage` or `4dx-d1-wig-formulation` |
| User is a member receiving an inherited WIG | `4dx-d1-member-team-wig-comprehension` |
| Topic is lead measures / scoreboard / cadence | D2 / D3 / D4 atomic skills (wrong topic for this router) |

## Indexed atomic skills

| Slug | Scope | Returns |
|---|---|---|
| `4dx-meta-personal-strategy-triage` | Personal (solo) | One of 6 verdicts: APPLICABLE / habit / portfolio-bet / emergency / creative / no-time-sovereignty |
| `4dx-meta-team-strategy-triage` | Team-leader | Team-fit verdict + leader-readiness check |

(Member scope intentionally absent — members do not triage methodology fit; they inherit the WIG.)

## See also

- [`SKILL.md`](SKILL.md) for full routing logic + Socratic decision tree + hand-off scripts
- Plugin router [`using-four-dx-coach`](../using-four-dx-coach/) for cold-start / out-of-4DX queries
