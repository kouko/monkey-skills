# 4dx-d4-cadence (Topic Router)

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Topic-router for D4 weekly-cadence queries when role (solo / leader / member) and timing (before / during / after the session) are unclear.

## What this router does

Catches ambiguous "help with my WIG Session" / "weekly cadence" queries. Asks ONE Socratic question on (role, timing), then routes to one of four atomic D4 skills. Does NOT run any session protocol itself.

## When this router activates

- "Help with my WIG Session" / "Weekly cadence advice" / "WIG Session prep" / "Set up the cadence"
- 「WIG Session のこと」「weekly cadence の運営」「毎週の WIG ミーティング」「週次レビューの相談」
- 「WIG Session 怎麼跑」「每週節奏」「WIG 週會」「每週 review」「weekly 開會」
- Any cadence query without a clear role + timing

## When NOT to use

| Situation | Where to go instead |
|---|---|
| "I'm running my own solo session" | `4dx-d4-personal-wig-session` directly |
| "I'm facilitating my team's session" | `4dx-d4-team-wig-session-lead` directly |
| "Prep my commitment for tomorrow" | `4dx-d4-member-commitment-prep` directly |
| "Just had session, missed my commit" | `4dx-d4-member-account-debrief` directly |
| Cadence broken multiple weeks | `4dx-sustain-personal-momentum-rescue` (rescue precedes restart) |
| No WIG / lead / scoreboard yet | D1 / D2 / D3 first; D4 has nothing to operate on |
| Sprint review / OKR check-in / 1-on-1 | Out of 4DX — `using-four-dx-coach` |

## Indexed atomic skills

| Slug | Role | Timing | Returns |
|---|---|---|---|
| `4dx-d4-personal-wig-session` | Solo (agent = peer-witness) | During | 20-30 min Account → Review → Plan with self-chosen 1-2 commitments |
| `4dx-d4-team-wig-session-lead` | Team-leader (facilitator) | During | Agenda + Socratic prompts under commitments-not-assignments + veto-not-dictate |
| `4dx-d4-member-commitment-prep` | Team-member | Before | Specific, influenceable, single-step commitment ready to state aloud |
| `4dx-d4-member-account-debrief` | Team-member | After | Honest self-account: kept / partial / missed + diagnosis feeding next prep |

## See also

- [`SKILL.md`](SKILL.md) for full routing logic + Socratic decision tree + hand-off scripts
- Plugin router [`using-four-dx-coach`](../using-four-dx-coach/) for cold-start / out-of-4DX queries
