# 4DX D2 — Lead Measure Discovery

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> D2 core — discover 2-3 lead measures that are BOTH predictive of the WIG AND directly influenceable day-to-day.

## When this skill activates

- "I have the goal but I don't know what to do every day."
- "What should I track to know I'm on the right path?" / "What's a leading indicator for [goal]?"
- "I'm working hard but nothing's moving — what am I missing?"
- About to install a tracking dashboard with 20+ metrics
- Lead measures named so far are actually lag-on-a-shorter-clock (weekly weight, monthly revenue) or non-influenceable (market direction)

## What it does (the protocol in brief)

Socratic discovery — agent never invents leads on the user's behalf. Both axes must be true:

1. **WIG gate check** — user states the WIG in one sentence (X → Y by When); halt and redirect to D1 if vague
2. **Brainstorm candidate behaviors** — list 5-10, pushing for counter-intuitive options ("equivalent of measure-children's-feet for your goal")
3. **Two-axis scoring (1-5 × 1-5)** — predictive + influenceable, each with a one-sentence causal chain
4. **Drop anything ≤3 on either axis** — ≤3 predictive = noise; ≤3 influenceable = rainfall-class
5. **Select 2-3, prefer one frequency + one quality** — frequency-based (do X N times per week) + quality-based (each X meets standard Y)
6. **Operational definition** — for each lead, what counts as "done", how/when logged, weekly target — explicit enough another person could apply it
7. **Predict the causal chain in writing** — one paragraph: "If I hit my lead targets weekly for 6 weeks, I expect the lag to have moved by [Y] because…"
8. **Output** — 2-3 named leads + operational definitions + weekly targets; hand off to D3 (display) and D4 (review)

## When NOT to use

| Situation | Where to go instead |
|---|---|
| No defined WIG yet | `4dx-d1-personal-wig-defining` first — leads built on a vague WIG are noise |
| Stroke-of-pen goal (single decision suffices) | Lead measures don't apply |
| Lag is structurally unmeasurable on a weekly clock (drug discovery, novel-writing) | Weekly leads become theatrical; consider milestone-based tracking |
| User wants display / scoreboard advice | `4dx-d3-personal-scoreboard` |
| Leads exist but lag isn't moving after 4+ weeks | `4dx-sustain-personal-momentum-rescue` (five optimizing questions) |

## Source

Distilled from *The 4 Disciplines of Execution* (2nd ed.), Chapter 3 (Discipline 2: Act on the Lead Measures) and Chapter 13. Three anchor cases: shoe retailer (4,500 stores; "measure children's feet" as the counter-intuitive lead), Younger Brothers Construction (safety: 57 → 12 incidents/yr via observable behaviors), and Towne Park valet (retrieval-time lead).

See [`SKILL.md`](SKILL.md) for the full RIA++ render including the lag-masquerading-as-lead trap, the lead-data-too-hard-so-skipped warning, and the Goodhart / measure-gaming defense (paired frequency + quality leads + 4-week causal-chain check).
