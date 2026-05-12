# variance-target-action-template

[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Generic B-loop control template (target ↔ variance ↔ action ↔ actual) + the do-nothing-under-oscillation diagnostic.

## When to use

- A KPI is oscillating around its target with sustained or growing amplitude.
- Ping-pong adjustments: every intervention seems to widen the swing.
- Modeling any management-control mechanism as a balancing loop (quota, OKR, inventory rule, monetary-policy committee, customer-success playbook).

## How to invoke

```
/systems-thinking-toolkit:variance-action
```

## What you get

- A 4-node balancing-loop diagnostic (target, actual, variance, action) with explicit variance direction and S/O link labels.
- A delay-aware recommendation that includes a non-action option when the loop is already converging or over-correction is the failure mode.
- An upward-communication rationale so restraint is not misread as inaction.

## Boundaries

- NOT for reinforcing loops (R-loops) or systems that are genuinely diverging — use `loop-and-link-primitives` instead.
- NOT when oscillation is desired (e.g. designed cyclic behavior) or when detection lag is genuinely zero.
- NOT for one-off, non-recurring decisions with no feedback loop to oscillate.

## More

- Full skill: [SKILL.md](SKILL.md)
- Source: Dennis Sherwood, *Seeing the Forest for the Trees* (2002), Chapter 6 (balancing loops, time delays, oscillation); Chapter 10 (B-loop template per lever).
