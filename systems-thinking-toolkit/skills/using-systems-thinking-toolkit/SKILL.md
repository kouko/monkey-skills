---
name: using-systems-thinking-toolkit
description: >-
  Route to the best systems-thinking skill when intent is unclear. Use
  when something is spiraling, oscillating, hitting a ceiling, stuck in
  a vicious cycle, or you want to map a complex system but aren't sure
  which method fits — e.g. 'my team keeps missing deadlines and
  overcompensating', 'this keeps getting worse and I don't know why',
  'we need to plan strategy across multiple timescales'. Do NOT use
  when the user already named a specific method (CLD, limits-to-growth,
  stock-and-flow, scenario planning, stakeholder mapping).
  システム思考の案内。系統思考導引。
---

# Using Systems Thinking Toolkit

Help the user find the right systems-thinking method for their situation.
Ask what they're trying to do, then recommend the best-fit skill.

## Routing Guide

Ask the user ONE question: **"What are you trying to do?"**

Then match their intent to the right skill:

### "I see a feedback loop or pattern"

| Situation | Skill | Command |
|---|---|---|
| Diagnose R vs B loop (vicious cycle, spiraling, boom/bust) | loop-and-link-primitives | `/systems-thinking-toolkit:link-primitives` |
| Draw a CLD with discipline (12 rules + fuzzy variables) | cld-craft | `/systems-thinking-toolkit:cld-craft` |
| R-loop is decelerating — find the brake | limits-to-growth-take-the-brakes-off | `/systems-thinking-toolkit:limits-to-growth` |
| Oscillation around a target — diagnose the cycle | variance-target-action-template | `/systems-thinking-toolkit:variance-action` |

### "I'm doing strategy"

| Situation | Skill | Command |
|---|---|---|
| Reframe strategy as lever-vs-outcome + multi-timescale cascade + 3×N scenario planning | strategy-lever-and-cascade | `/systems-thinking-toolkit:strategy` |

### "I'm dealing with multiple stakeholders or team dynamics"

| Situation | Skill | Command |
|---|---|---|
| Overlay multiple stakeholder CLDs + mental-model harmony | stakeholder-and-team-thinking | `/systems-thinking-toolkit:stakeholder` |

### "I need to quantify or simulate"

| Situation | Skill | Command |
|---|---|---|
| Translate a CLD into stock-and-flow + learn from simulation (not point-forecast) | simulation-modeling | `/systems-thinking-toolkit:simulation` |

### "I need facilitation / scenario tools" (auxiliary)

| Situation | Skill | Command |
|---|---|---|
| Generate alternative futures for strategic-cascade scenario planning | innovaction-martian-test | `/systems-thinking-toolkit:martian-test` |
| Adapt strategy artifacts to executive personality | manager-personality-quadrant | `/systems-thinking-toolkit:quadrant` |

> Both auxiliary skills are V1-weak per Stage 1.5 verification. See
> each SKILL.md Boundary section for prior-art credit (TRIZ /
> morphological analysis for `innovaction-martian-test`;
> DiSC / MBTI / Hogan / Situational Leadership for
> `manager-personality-quadrant`) before reaching for them.

### "I'm not sure"

If the user can't articulate their need, ask these narrowing questions
one at a time:

1. "Are you trying to *understand* a pattern, *decide* an intervention,
   *plan* strategy, or *quantify* something?"
2. Based on the answer, use the tables above to narrow further.
3. If still unclear, default to **`loop-and-link-primitives`** — it's
   the foundational ontology that most other skills depend on.

## After Routing

Once you've identified the right skill:

1. Tell the user which method you recommend and why (one sentence)
2. Invoke the skill immediately — do NOT explain the method yourself

## Rules

- Do NOT explain systems-thinking methods in detail — let the skill do that
- Do NOT combine multiple methods — recommend ONE, let the user decide
  if they want another afterward
- If the user already knows which method they want, skip routing and
  invoke directly
- If none of the methods fit, say so honestly — not every problem
  needs a systems-thinking framework

## Recommended learning order (for users new to systems thinking)

1. **`loop-and-link-primitives`** — foundational; no prerequisites
2. **`cld-craft`** — depends on (1); workshop drawing craft
3. **`limits-to-growth-take-the-brakes-off`** — depends on (1); composes with (2)
4. **`variance-target-action-template`** — depends on (1)+(2); contrasts with (3)
5. **`strategy-lever-and-cascade`** — depends on (4); composes with (8) + (9)
6. **`stakeholder-and-team-thinking`** — depends on (1)+(2); stakeholder-aware
7. **`simulation-modeling`** — depends on (2); precision step

Auxiliary skills (reach for inside `strategy-lever-and-cascade` workflow):
8. **`innovaction-martian-test`** — generates alternative futures
9. **`manager-personality-quadrant`** — adapts presentation to executive style

See `INDEX.md` for the full reference graph (mermaid + topological sort).
