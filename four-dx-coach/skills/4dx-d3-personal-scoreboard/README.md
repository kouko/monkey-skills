# 4DX D3 — Personal Scoreboard

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> D3 core — design a glance-readable players' scoreboard for one (≤4 elements, lead + lag + where-you-should-be line, passes the 5-second winning test).

## When this skill activates

- "I built a Notion dashboard / tracker but I don't actually look at it."
- "My fitness app shows me too many things, none of them motivate me."
- "How do I make my progress visible?" / "Should I use a sticky note / whiteboard / app?"
- D1 + D2 done but momentum is fading after 2-4 weeks (often a missing-scoreboard symptom, not willpower)
- Existing tracking artifact is clearly a coach's scoreboard (multi-tab spreadsheet, Gantt chart, project plan)

## What it does (the protocol in brief)

A Socratic design dialogue — output is a scoreboard spec the user commits to *displaying somewhere visible during work today*, not a tracking-philosophy discussion:

1. **Confirm WIG + lead measures are defined** — both in writing; halt and redirect to D1/D2 if missing
2. **Choose a display medium based on the user's actual day** — where eyes naturally land 3-5×/day; reject "an app I'll check"
3. **Design the lead measure visualization** — weekly bars / running streak / checkbox grid / cumulative count, drawable in <30 seconds
4. **Design the lag visualization with a where-you-should-be line** — pacing line / target marker / "goat" is mandatory
5. **Apply the 5-second test** — describe back cold; user must say yes without hedging; ≤4 elements total
6. **Lock display location + update cadence** — one-line statement: "I will post this on [location] and update [lead] daily / [lag] weekly"
7. **Output: spec + immediate physical action today** — print, stick, draw — not "this weekend" (inertia is the failure mode this skill exists to prevent)

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Org-wide BI / KPI dashboard for a team you manage | Coach's scoreboards are valid artifacts — different problem |
| WIG or lead measures not yet defined | `4dx-d1-personal-wig-defining` / `4dx-d2-personal-lead-measure-discovery` first |
| Stroke-of-the-pen goal (just buy / hire / decide) | Nothing to scoreboard |
| Reactive / on-call domain (whirlwind IS strategic value) | Phantom-guilt risk; see `4dx-meta-personal-strategy-triage` |
| High-context-culture team setting (public peer comparison reads as face-loss) | The book's shift-vs-shift examples generalize poorly here |

## Source

Distilled from *The 4 Disciplines of Execution* (2nd ed.), Chapter 4 (Discipline 3: Keep a Compelling Scoreboard) and Chapter 14. Three anchor cases: Northrop Grumman (the blown-down stadium scoreboard analogy), Remote Canadian plant (74 → 94 quality via shift-level visible boards), and fighter-plane developers ("a project plan is not a scoreboard"; the two artifacts coexist).

See [`SKILL.md`](SKILL.md) for the full RIA++ render including coach's-as-players' substitution (CE-08), status-without-trajectory (CE-09), Goodhart / vanity-metric drift, and the manual-update-as-feature design rule.
