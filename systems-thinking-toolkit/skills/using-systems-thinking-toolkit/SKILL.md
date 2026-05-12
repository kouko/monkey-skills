---
name: using-systems-thinking-toolkit
description: >-
  Route to the best systems-thinking skill when intent is unclear. Use
  when something is spiraling, oscillating, hitting a ceiling, stuck in
  a vicious cycle, or you want to map a tangled situation but aren't
  sure which method fits — e.g. 'my team keeps missing deadlines and
  overcompensating', 'this keeps getting worse and I don't know why',
  'we need to plan strategy across multiple timescales'. Do NOT use
  when the user already named a specific method (cld-craft, archetypes,
  overlay, simulation, strategy, team, martian-test, quadrant).
  システム思考の案内。系統思考導引。
---

# Using Systems Thinking Toolkit

Help the user find the right systems-thinking method for their situation.
Ask what they're trying to do, then recommend the best-fit skill.

## Routing Guide

Ask the user ONE question: **"What are you trying to do?"**

Then match their intent to the right skill:

### "I have a tangled situation — I want a logic diagram"

| Situation | Skill | Command |
|---|---|---|
| Translate prose mess into a Mermaid CLD with R/B-classified loops and signed edges; "this keeps getting worse", "we're stuck in a vicious cycle", "death spiral", "boom and bust", "why is X accelerating", "the diagram is too cluttered" | cld-craft | `/systems-thinking-toolkit:cld-craft` |

`cld-craft` is the v0.4 **carry-1** skill — it absorbs the old `loop-and-link-primitives` discipline into Step 11 so a single invocation produces a fully-annotated Mermaid CLD ready for downstream skills.

### "I have a CLD — now what?"

> **Prerequisite for this whole section**: an R/B-classified Mermaid CLD
> already exists (typically from `cld-craft` Step 11). If you have only
> prose / "vicious cycle" intuition / a hand sketch, route to `cld-craft`
> FIRST — these skills consume a classified CLD, not prose. Skipping
> classification breaks the downstream contract.

| Situation | Skill | Command |
|---|---|---|
| Recognize archetype (limits-to-growth OR V/T/A oscillation) on an already-classified CLD + apply intervention playbook | cld-archetypes | `/systems-thinking-toolkit:archetypes` |
| Overlay multiple stakeholder perspectives (each their own classified CLD) on a shared canvas + find a straddle policy | cld-overlay | `/systems-thinking-toolkit:overlay` |
| Translate a classified CLD into stock-and-flow + use simulation for learning (not point forecast) | simulation-modeling | `/systems-thinking-toolkit:simulation` |

### "I'm doing strategy or team work"

| Situation | Skill | Command |
|---|---|---|
| Reframe ambition into lever target settings + 3-timescale cascade + 3×N scenario planning | strategy-lever-and-cascade | `/systems-thinking-toolkit:strategy` |
| Surface team mental models + sustain via measurable leadership-energy proxies | team-mental-model | `/systems-thinking-toolkit:team` |

### "I need scenario / personality tools" (auxiliary)

| Situation | Skill | Command |
|---|---|---|
| Generate alternative futures for strategic-cascade scenario planning | innovaction-martian-test | `/systems-thinking-toolkit:martian-test` |
| Adapt strategy artifacts to executive personality (framing-vs-analysis split) | manager-personality-quadrant | `/systems-thinking-toolkit:quadrant` |

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
3. If still unclear, default to **`cld-craft`** — it's the carry-1
   prose→CLD translation skill that most downstream skills consume.

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

1. **`cld-craft`** — foundational; prose → fully-annotated Mermaid CLD; absorbs old `loop-and-link-primitives` classification discipline
2. **`cld-archetypes`** — depends on (1); recognizes limits-to-growth or V/T/A on a classified CLD + matching intervention
3. **`cld-overlay`** — depends on (1); multi-perspective overlay for stakeholder mediation
4. **`team-mental-model`** — depends on (1); inward team-mental-model + leadership-energy proxies (composes with cld-overlay post-merger)
5. **`strategy-lever-and-cascade`** — depends on (2); 3-timescale cascade + 3×N scenario table + lever reframing
6. **`simulation-modeling`** — depends on (1); precision quantification step (text-only in v0.4; Python companion v0.5+ candidate)

Auxiliary skills (reach for inside `strategy-lever-and-cascade` workflow):

7. **`innovaction-martian-test`** — generates alternative futures
8. **`manager-personality-quadrant`** — adapts presentation to executive style

See `INDEX.md` for the full reference graph (mermaid + topological sort).
