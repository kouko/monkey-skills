# 4DX D1 — WIG Defining

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> D1 core — coach the user from a vague aspiration to one written WIG in *From X to Y by When* form.

## When this skill activates

- "I want to be healthier / get in shape / grow my business / finish my book."
- "I have too many priorities / I have 5 things I want to do this quarter."
- A goal stated as an *activity* rather than an outcome ("exercise more", "study Japanese daily")
- A project tracked as "% complete" that has stalled for months
- User wants to "use 4DX" but hasn't yet expressed any goal in *From X to Y by When* form

## What it does (the protocol in brief)

A Socratic coaching dialogue — the agent extracts the WIG from the user, never writes it for them:

1. **Capture the raw goal** — record the user's own words verbatim
2. **Force lag-measure surfacing** — name a quantifiable downstream lag (kg / revenue / chapters / clients)
3. **Pin X (starting state)** — numeric current value
4. **Pin Y (target state)** — numeric target in same units
5. **Pin *When*** — a fixed calendar date, not "soon" / "this year"
6. **Wildly-important test** — transformation vs incremental; if only incremental, halt (this is whirlwind work, not a WIG)
7. **Count test** — narrow to one (max two if independent and non-conflicting)
8. **Battle-vs-war test** — if war, decompose into smallest set of sub-WIGs and re-run steps 2-7 on each
9. **Project-as-WIG check** — if project, rewrite finish line as deliverables-list + date (reject "% complete")
10. **Output the WIG** — read aloud; user confirms a stranger could tell on the deadline whether they won or lost

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Stroke-of-pen decision (buy a desk, switch CRMs) | Normal decision protocol |
| Pure habit design (meditate daily) — no fixed lag-measurable end | Atomic Habits / habit-stacking |
| Already-well-formed numeric goal (X / Y / When all explicit) | Skip to `4dx-d2-personal-lead-measure-discovery` |
| Reactive / on-call domains where whirlwind IS the strategic work | `4dx-meta-personal-strategy-triage` |
| User is unsure whether 4DX even fits | `4dx-meta-personal-strategy-triage` first |

## Source

Distilled from *The 4 Disciplines of Execution* (2nd ed., 2021), Chapter 2 (Discipline 1: Focus on the Wildly Important), Chapter 6 (Choosing Where to Focus), and Chapter 12. Three anchor cases: NASA moon shot, Tim Cook's Apple ("say no to good ideas"), and Mountain Land Rehab (12-year stalled project rescued by deliverables-list-with-deadline).

See [`SKILL.md`](SKILL.md) for the full RIA++ render including the multi-WIG drift, whole-workload-as-WIG, and percent-complete-as-project-lag failure modes.
