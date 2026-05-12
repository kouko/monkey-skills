[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

# cld-archetypes

Given a Mermaid CLD with R/B annotations, recognize which Sherwood archetype is present (limits-to-growth R+B coupling OR V/T/A B-loop with delay) and apply the matching intervention playbook.

## When to use

- Growth is decelerating despite more spend / more hires, and the team's reflex is to "pedal harder" on the same lever — limits-to-growth diagnosis is needed before doubling the budget.
- A KPI keeps swinging quarter-to-quarter and each intervention seems to widen the swing — V/T/A diagnosis is needed before the next correction.
- A CLD has already been drawn (R/B classified via `loop-and-link-primitives`) and you need to name the archetype before choosing an intervention philosophy.

## How to invoke

`/systems-thinking-toolkit:archetypes` or via the router `/systems-thinking-toolkit:stt`.

## What you get

- A named archetype on the CLD (`limits-to-growth` or `V/T/A`), with the binding constraint identified (limits-to-growth) or the feedback delay estimated (V/T/A).
- The matching intervention rule — "take the brakes off" the binding B-loop, or "do nothing for one full feedback cycle" while the B-loop converges — with cost / timeline / falsifiable prediction attached.
- A downstream pointer (e.g. to `strategy-lever-and-cascade` for which lever to change next, or to `simulation-modeling` for quantitative confirmation) appended below the `%% Archetype: ...` Mermaid comment.

## Boundaries

- NOT for genuinely diverging systems (a vicious R-loop running off to infinity) — "do nothing" applied here is malpractice; route back to `loop-and-link-primitives` R-loop diagnosis.
- NOT a license to "take the brakes off" before confirming which brake binds — relieving the wrong constraint can accelerate collapse (Easter Island ce07 failure mode).
- NOT for pre-PMF systems with no running growth engine, one-off non-recurring decisions, zero-detection-lag real-time control, or random within-control noise (use SPC / control-chart tooling instead).

## Reference

- Full skill specification: [SKILL.md](SKILL.md)

## Source

Dennis Sherwood, *Seeing the Forest for the Trees* — Chapter 6 (balancing loops, time delays, oscillation), Chapter 8 (limits-to-growth + take-the-brakes-off), and Chapter 13 (car-dealership quantitative confirmation).
