# 4DX D1 — Whirlwind Triage

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> D1 prerequisite — surface BAU vs WIG capacity through a 7-day time audit *before* writing the WIG.

## When this skill activates

- "I'm always firefighting / I want to do X but I never have time."
- "Every week the important stuff gets pushed."
- "My day job eats my whole week."
- A previous WIG died and the user wonders if 4DX is broken or if they need to "try harder."
- About to invoke `4dx-d1-wig-formulation` but has never made the whirlwind / WIG distinction explicit.

## What it does (the protocol in brief)

1. **Set up a 7-day time audit log** — track every 30-min block, tag as `WHIRLWIND` / `WIG` / `NEITHER`. Completion: 7 consecutive days, ≥80% of waking blocks tagged.
2. **Compute the ratio** — sum hours by tag, write down WHIRLWIND% / WIG% / NEITHER% + a one-sentence reaction comparing expected vs found.
3. **Audit the whirlwind for theater** — re-tag every WHIRLWIND block as `BAU-real` (operation breaks without it) vs `BAU-theater` (only your image breaks).
4. **Decide your minimum WIG allocation** — the book's anchor is ~20% (8h on a 40h week); name a numeric N + concrete calendar blocks + a named protector.
5. **Hand off (or terminate)** — proceed to `4dx-d1-wig-formulation`, OR explicitly drop 4DX if step 1 revealed a genuinely reactive role.

## When NOT to use

| Situation | Where to go instead |
|---|---|
| Burnout / sustained overwhelm / depression | Coaching / clinical support — do NOT run a time audit |
| Genuinely reactive roles (on-call SRE, ER, infant care) | The whirlwind IS the strategic value — `4dx-meta-strategy-triage` (CE-26) |
| Stroke-of-pen / one-off task ("file my taxes") | Doesn't need 4DX at all |
| Productivity-tool shopping (Notion vs Sunsama) | Tool selection, not capacity diagnosis |

## Source

Distilled from *The 4 Disciplines of Execution* (2nd ed., 2021), Chapter 1 — The Real Problem with Execution. Two anchor cases: Plant Manager of the Year (twelve priorities to one) and Towne Park Miami (the concrete wall on a Saturday).

See [`SKILL.md`](SKILL.md) for the full RIA++ render including the Parkinson's-Law devouring trap and the most-important-confusion warning that feeds D1-wig-defining downstream.
