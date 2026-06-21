---
name: using-systems-thinking-toolkit
description: |
  Route to the best systems-thinking skill when intent is unclear — something spiraling, oscillating, hitting a ceiling, or a tangle to map. Use on 'this keeps getting worse, I don't know why' or 'map a tangled situation'. Named method → that skill.
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
| Translate prose mess into a Mermaid CLD with R/B-classified loops and signed edges. EN: "this keeps getting worse", "stuck in a vicious cycle", "death spiral", "boom and bust", "why is X accelerating", "the diagram is too cluttered". zh-TW: 「做得越多越糟」/「停不下來」/「卡住了」/「下行螺旋」/「越…越…」/「心不在焉」. JA: 「やればやるほど悪化」/「行き詰まり」/「悪循環」/「燃え尽き」/「負のループ」 | cld-craft | `/systems-thinking-toolkit:cld-craft` |

`cld-craft` is the v0.4 **carry-1** skill — it absorbs the old `loop-and-link-primitives` discipline into Step 11 so a single invocation produces a fully-annotated Mermaid CLD ready for downstream skills.

### "I have a CLD — now what?"

> **Prerequisite for this whole section**: an R/B-classified Mermaid CLD
> already exists (typically from `cld-craft` Step 11). If you have only
> prose / "vicious cycle" intuition / a hand sketch, route to `cld-craft`
> FIRST — these skills consume a classified CLD, not prose. Skipping
> classification breaks the downstream contract.

| Situation | Skill | Command |
|---|---|---|
| Recognize archetype (limits-to-growth OR V/T/A oscillation) on an already-classified CLD + apply intervention playbook. EN: "growth decelerating", "diminishing returns", "doubling spend won't move it", "metric keeps swinging". zh-TW: 「撞到天花板」/「增長停滯」/「投得越多越沒效」/「指標一直在擺動」. JA: 「成長の頭打ち」/「打てば打つほど効かない」 | cld-archetypes | `/systems-thinking-toolkit:archetypes` |
| Overlay multiple stakeholder perspectives (each their own classified CLD) on a shared canvas + find a straddle policy | cld-overlay | `/systems-thinking-toolkit:overlay` |
| Translate a classified CLD into stock-and-flow + use simulation for learning (not point forecast) | simulation-modeling | `/systems-thinking-toolkit:simulation` |

### "I'm doing strategy or team work"

| Situation | Skill | Command |
|---|---|---|
| Reframe ambition into lever target settings + 3-timescale cascade + 3×N scenario planning | strategy-lever-and-cascade | `/systems-thinking-toolkit:strategy` |
| Surface team mental models + sustain via measurable leadership-energy proxies | team-mental-model | `/systems-thinking-toolkit:team` |

### "I need personality / framing tools" (auxiliary)

| Situation | Skill | Command |
|---|---|---|
| Adapt strategy artifacts to executive personality (framing-vs-analysis split) — facilitation vocabulary only, NOT a personality measurement instrument | manager-personality-quadrant | `/systems-thinking-toolkit:quadrant` |

> Auxiliary skill is V1-weak per Stage 1.5 verification. See SKILL.md
> Boundary section for prior-art credit (DiSC / Big Five / Hogan /
> Situational Leadership) and "Graduate beyond this skill" cross-refs
> before reaching for it.
>
> **v0.6 note**: scenario-perturbation (formerly `innovaction-martian-test`)
> has been absorbed into `strategy-lever-and-cascade` Step 5. Reach for
> `/strategy-lever-and-cascade` directly when you need Martian-test feature perturbation
> for scenario generation.

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

Auxiliary skill (reach for inside `strategy-lever-and-cascade` workflow):

7. **`manager-personality-quadrant`** — adapts presentation to executive style (V1-weak; facilitation vocabulary only)

> v0.6 absorbed `innovaction-martian-test` (Martian-test feature
> perturbation) into `strategy-lever-and-cascade` Step 5. There is no
> separate skill to reach for; the perturbation procedure runs inline
> in the strategy workflow.

See `INDEX.md` for the full reference graph (mermaid + topological sort).
