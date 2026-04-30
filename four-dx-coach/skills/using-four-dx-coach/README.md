# using-four-dx-coach (Router)

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Entry-point router for the four-dx-coach plugin. Dispatches generic / vague 4DX queries to the correct atomic skill — or declines if 4DX is the wrong tool.

## When this skill activates

- "I want to start using 4DX" / "where do I begin with 4DX?"
- "Help me apply the 4 Disciplines of Execution" / "I just read 4DX, what do I do?"
- "Use 4DX on my goal of [X]" / "explain 4DX in practice"
- Any vague 4DX query where the user has not yet named a specific discipline

## What it does (the protocol in brief)

A Socratic decision tree that maps the user's signal to one of seven atomic skills:

| # | Signal | Route to |
|---|---|---|
| 1 | Unsure 4DX even fits the goal | `4dx-meta-strategy-triage` (6-verdict gate) |
| 2 | "Day job eats everything; no room for the goal" | `4dx-meta-whirlwind-triage` (7-day audit, 80/20 capacity) |
| 3 | Goal is vague / multi-priority / activity-only | `4dx-d1-wig-formulation` (one *From X to Y by When*) |
| 4 | WIG defined; no idea what to DO daily | `4dx-d2-lead-measures` (predictive + influenceable) |
| 5 | Tracking is noisy / invisible / 30-metric DB | `4dx-d3-scoreboard` (≤4 elements, 5-second test) |
| 6 | D1-D3 in place but cadence is missing | `4dx-d4-cadence` (weekly Account → Review → Plan) |
| 7 | Practice has stalled / lapsed / lost momentum | `4dx-sustain-personal-momentum-rescue` (diagnoses broken layer) |

For users starting fresh, the canonical sequence is 1 → 2 → 3 → 4 → 5 → 6, with 7 invoked when (not if) cadence breaks. The path is sequential, not optional — 4DX is "a matched set, not a menu."

## When NOT to use

| Situation | Where to go instead |
|---|---|
| User names a specific discipline ("how do I write a WIG?") | Route directly to that atomic skill, skip this router |
| Enterprise / multi-team rollout (50+ people, cascading WIGs) | Decline — refer to book Chapters 6-10 (Leader-of-Leaders) |
| Software process queries (agile, scrum, kanban, sprint planning) | Decline — different problem class |
| Habit formation with no breakthrough lag (meditate daily, floss) | Decline — recommend Atomic Habits |
| Portfolio of speculative bets / pre-PMF | Decline — recommend OKR / lean-startup |
| Burnout / depression / clinical exhaustion | Decline — refer to clinical / coaching support |

## Source

Stage-0 BOOK_OVERVIEW + the seven atomic-skill SKILL.md frontmatters of the four-dx-coach plugin. Anchored on *The 4 Disciplines of Execution* (2nd ed., 2021).

See [`SKILL.md`](SKILL.md) for the full router decision tree, hand-off scripts for non-applicable queries (enterprise / habit / OKR / agile / burnout), and explicit non-activation signals.
