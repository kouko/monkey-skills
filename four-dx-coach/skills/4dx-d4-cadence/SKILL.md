---
name: 4dx-d4-cadence
description: |
  [Topic-router] for D4 weekly-cadence queries when role (solo / leader / member-prep / member-debrief) is unclear from context. Activates on ambiguous "WIG Session" / "weekly cadence" / "weekly review" queries that don't yet name *who runs what*. After ONE Socratic disambiguation, routes to: `4dx-d4-personal-wig-session` (solo runs own session, agent = peer-witness), `4dx-d4-team-wig-session-lead` (leader facilitates team session), `4dx-d4-member-commitment-prep` (member preps own commitment before session), or `4dx-d4-member-account-debrief` (member self-accounts after session). EN: "Help with my WIG Session", "Weekly cadence advice", "WIG Session prep". JP: 「WIG Session のこと」「weekly cadence の運営」. ZH: 「WIG Session 怎麼跑」「每週節奏」. Do NOT activate when role is explicit, when cadence has already broken (use `4dx-sustain-personal-momentum-rescue`), for non-4DX weekly reviews (PI planning / OKR check-in / 1-on-1 / status report), or before D1-D3 are set.
source_book: The 4 Disciplines of Execution (2nd ed., 2021) — McChesney/Covey/Huling/Thele/Walker
source_chapter: Chapter 5, Chapter 15 (D4 cadence shared across solo / leader / member roles)
source_language: en
tags: [topic-router, wig-session, cadence, role-triage, d4, 4dx]
related_skills:
  - 4dx-d4-personal-wig-session
  - 4dx-d4-team-wig-session-lead
  - 4dx-d4-member-commitment-prep
  - 4dx-d4-member-account-debrief
  - 4dx-sustain-personal-momentum-rescue
  - using-four-dx-coach
---

# 4dx-d4-cadence — Topic-router for D4 weekly-cadence across roles

## Mission

Catch ambiguous WIG-Session / weekly-cadence queries where the user has not yet signaled their *role at the session* (solo participant, team facilitator, or member preparing/debriefing). Ask ONE Socratic question to surface role + timing (before / during / after), then route. The 4 atomic skills routed share the Account / Review / Plan three-segment grammar but differ in *who facilitates* and *which segment the user is preparing for*.

## When this router activates

### Multilingual trigger phrasings

- **EN**: "Help with my WIG Session", "Weekly cadence advice", "WIG Session prep", "Run my weekly review", "Set up the cadence"
- **JP**: 「WIG Session のこと」「weekly cadence の運営」「毎週の WIG ミーティング」「週次レビューの相談」
- **ZH**: 「WIG Session 怎麼跑」「每週節奏」「WIG 週會」「每週 review」「weekly 開會」

### Non-activation signals (DO NOT fire when…)

- Role explicit — "I'm running my own solo session" → personal-wig-session; "I'm facilitating my team's session" → team-wig-session-lead; "preparing my commitment for tomorrow's session" → member-commitment-prep; "the session just ended, I missed my commitment" → member-account-debrief
- Cadence has already broken (multiple skipped weeks) → `4dx-sustain-personal-momentum-rescue`; rescue first, then resume cadence
- Not yet at D4 — no WIG / no lead measure / no scoreboard → route to D1 / D2 / D3 first
- Non-4DX cadence — agile sprint review / PI planning / OKR check-in / 1-on-1 / engineering retro → out of plugin scope, hand off via `using-four-dx-coach`

## Indexed atomic skills

| Slug | Role | Timing | Returns |
|---|---|---|---|
| [`4dx-d4-personal-wig-session`](../4dx-d4-personal-wig-session/) | Solo participant (agent = peer-witness) | During session | 20-30 min Account → Review scoreboard → Plan dialogue with self-chosen 1-2 commitments |
| [`4dx-d4-team-wig-session-lead`](../4dx-d4-team-wig-session-lead/) | Team-leader (facilitator) | During session | Agenda + Socratic prompts to run a team WIG Session under commitments-not-assignments + veto-not-dictate rules |
| [`4dx-d4-member-commitment-prep`](../4dx-d4-member-commitment-prep/) | Team-member | **Before** session | Specific, influenceable, single-step commitment that ladders to the team WIG, ready to state aloud |
| [`4dx-d4-member-account-debrief`](../4dx-d4-member-account-debrief/) | Team-member | **After** session | Honest self-account: kept / partial / missed + diagnosis (commitment-shape / whirlwind / capacity / motivation) feeding next prep |

## Routing logic (Socratic decision tree)

When this router activates, do NOT run any session protocol. Disambiguate first:

1. **Detect implicit role + timing**:
   - "My session" + solo context → **personal-wig-session**
   - "Facilitate / run / lead a team session" / 「team の session を主催 / 進行」 / 「主持團隊」→ **team-wig-session-lead**
   - "Prep / write my commitment / what should I commit to" / 「commitment を準備」 / 「準備我的 commitment」→ **member-commitment-prep**
   - "Just had session / how did I do / honest reflection on my last commitment" / 「先週 commit したのを振り返る」 / 「上週承諾達成沒」 → **member-account-debrief**
   - If signal strong → skip to step 3.

2. **If ambiguous, ask ONE question**:
   > "Two quick checks: (a) **what's your role at this session** — solo (just you), facilitator (you lead a team), or member (your team has a leader)? (b) **what timing** — before the session (prep), during (agenda), or after (debrief)? I'll route to the right protocol."
   > 日本語: 「2 点確認: (a) **session での役割** — solo（自分のみ）、facilitator（team を率いる側）、member（leader がいる team の参加者）のどれ？ (b) **タイミング** — 前（prep）、最中（agenda）、後（debrief）のどれ？適切な protocol に振り分けます。」
   > 中文: 「兩個快速確認：(a) **你在 session 的角色** — solo（只有你自己）、facilitator（你帶 team）、member（team 有 leader）？ (b) **時機** — 開會前（prep）、開會中（agenda）、還是開會後（debrief）？我幫你導到對的 protocol。」

3. **Hand off**:
   - solo + during → `4dx-d4-personal-wig-session`
   - facilitator + during → `4dx-d4-team-wig-session-lead`
   - member + before → `4dx-d4-member-commitment-prep`
   - member + after → `4dx-d4-member-account-debrief`

4. **Edge cases**:
   - "Member + during session" → member doesn't have a separate during-session skill; surface that the leader runs the agenda. Suggest member-commitment-prep ahead of next session, OR member-account-debrief for the just-ended one.
   - "Solo + before / after" → personal-wig-session protocol is single-skill (covers prep + agenda + close internally); fire it directly.
   - "Facilitator + before / after" → team-wig-session-lead handles full lifecycle within its protocol; fire it directly.
   - "Cadence broken multiple weeks" → fire `4dx-sustain-personal-momentum-rescue` first; do NOT pretend a fresh cadence works on top of broken one.
   - "WIG / lead measure / scoreboard not yet set" → fire D1 / D2 / D3 skills first; D4 has nothing to operate on without upstream.

## Hand-off scripts (when none of the 4 D4 skills fit)

| User signal | Hand-off |
|---|---|
| "Cadence broke / skipped weeks / lost momentum" | `4dx-sustain-personal-momentum-rescue` |
| "No WIG yet" | `4dx-d1-wig-formulation` (topic-router) or atomic D1 |
| "No lead measures yet" | `4dx-d2-personal-lead-measure-discovery` |
| "No scoreboard yet" | `4dx-d3-personal-scoreboard` |
| "Sprint review / PI planning / OKR check-in / 1-on-1 / status report" | Out of 4DX — hand off via `using-four-dx-coach` |
| "Audit our team's 4DX execution practice" | `4dx-meta-team-xps-evaluation` |
| "Onboard direct reports onto 4DX" | `4dx-meta-team-leader-onboarding` |

## Boundary

### Do NOT activate this router when…

- Role + timing both explicit → fire the precise atomic skill directly
- Cadence already broken — rescue precedes restart
- Pre-D4 skills (D1 / D2 / D3) not yet completed — D4 is downstream
- Non-4DX cadence — different methodology — hand off via plugin router
- User mid-flow inside an active D4 atomic skill — don't interrupt

### Common confusions

- **Router vs atomic**: this router fires only on *ambiguous* role + timing; explicit queries should hit atomic skills directly.
- **Member prep vs solo session**: a member's "prep" is preparing what to commit to in someone else's facilitated session. A solo user's "prep" is part of the session itself. Don't conflate.
- **Member debrief vs sustain-rescue**: debrief = honest self-account on one commitment. Sustain-rescue = systemic cadence has broken across weeks. Different scopes.
- **Topic-router vs plugin-router**: `using-four-dx-coach` triages cold-start and out-of-4DX. This router operates only within the D4-cadence topic.

## Related skills

- `4dx-d4-personal-wig-session` — composes-with — downstream after solo + during determined
- `4dx-d4-team-wig-session-lead` — composes-with — downstream after facilitator + during determined
- `4dx-d4-member-commitment-prep` — composes-with — downstream after member + before determined
- `4dx-d4-member-account-debrief` — composes-with — downstream after member + after determined
- `4dx-sustain-personal-momentum-rescue` — contrasts-with — different skill when cadence already broken
- `using-four-dx-coach` — composes-with — plugin-level router for out-of-4DX queries

## Audit metadata

- **Skill type**: topic-router (no V1/V2/V3 verification — meta-skill)
- **Routing precision target**: ≥90% — disambiguation must reliably surface (role, timing)
- **Test pass rate**: see `test-prompts.json`
- **Created at**: 2026-04-30
- **Output language**: body — English; description + decision-tree prompts — multilingual EN/JP/zh-TW
