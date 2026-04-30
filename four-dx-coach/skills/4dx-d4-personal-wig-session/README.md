# 4DX D4 — WIG Session

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> D4 core — run a 20-30 minute weekly WIG Session for one solo user. Three-segment Socratic agenda: Account → Review → Plan. Agent serves as peer-witness.

## When this skill activates

- "I want a weekly review for my [goal / WIG / project]."
- "Help me stay on track with my goal each week."
- "I have lead measures and a scoreboard but I keep not acting on them."
- "I keep losing momentum on my goal — how do I keep it alive?"
- "Run my WIG Session with me." / "Walk me through this week's check-in."

## What it does (the protocol in brief)

A single 20-30 min weekly session. The agent acts as **peer-witness** (not boss, coach, or status-checker):

1. **Frame & open the session (≤2 min)** — state WIG verbatim, name the three segments, confirm time-box
2. **Segment 1 — Account (~5-7 min)** — for each prior commitment: kept / partially / not kept; ask once "what got in the way", do not problem-solve mid-segment
3. **Segment 2 — Review the scoreboard (~5-7 min)** — lead trend, lag trend, user interprets *first*; if lead green + lag flat ≥3 weeks → flag P-50 and route to sustain-rescue
4. **Segment 3 — Plan (~8-10 min)** — "what are the **one or two** most important things you can do **this week** to move your **lead measure**?"; both filters: specific deliverable + directly moves the lead; reject dependency commitments
5. **Confirm & log (~1-2 min)** — user states 1-2 commitments verbatim; agent echoes and logs for next Account segment
6. **Close & schedule (~1 min)** — same time next week; cancel-and-reschedule, never skip
7. **Whirlwind-creep redirect (any segment)** — interrupt politely, hold the agenda

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Team facilitation (manager running team meeting) | This skill is solo-personal-scope; book Chapters 5 + 15 directly |
| Daily standups, status meetings, 1:1s, project reviews | Don't conflate with WIG Session's specific architecture |
| User has no WIG yet | `4dx-d1-personal-wig-defining` first |
| Cadence has already broken (skipped 2+ weeks) | `4dx-sustain-personal-momentum-rescue` first, then resume here |
| Annual / quarterly retrospectives | Wrong cadence scope |
| Reactive / on-call / emergency-response work | `4dx-meta-personal-strategy-triage` (CE-26) |

## Source

Distilled from *The 4 Disciplines of Execution* (2nd ed., 2021), Chapter 5 (Discipline 4: Create a Cadence of Accountability) and Chapter 15. Three anchor cases: MICARE (7-year mining results from cadence concentration), Cystic Fibrosis Center (clinical knowledge work with long feedback loops), Store 334 (D1-D3 dying without D4; adding the cadence rescued the stack).

See [`SKILL.md`](SKILL.md) for the full RIA++ render including the compliance-commitments / vague-intents (CE-12) trap, whirlwind-invasion (CE-10) defense, the cancel-and-reschedule rule, and the solo-cadence-with-no-peer compensation pattern.
