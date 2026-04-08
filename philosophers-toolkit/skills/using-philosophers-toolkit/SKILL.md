---
name: using-philosophers-toolkit
description: >-
  Route to the best philosophical thinking method. Use when user wants
  to think deeper, clarify a problem, or analyze a decision but isn't
  sure which method to use. Do NOT use when user already knows which
  method they want.
  哲学的思考の案内。哲學思考導引。
---

# Using Philosophers Toolkit

Help the user find the right philosophical method for their situation.
Ask what they're trying to do, then recommend the best-fit skill.

## Routing Guide

Ask the user ONE question: **"What are you trying to do?"**

Then match their intent to the right skill:

### "I want to understand something deeply"

| Situation | Skill | Command |
|-----------|-------|---------|
| Understand what something IS (essence, structure, purpose) | Aristotle's Four Causes | `/philosophers-toolkit:four-causes` |
| Rethink from scratch, reject convention | First Principles | `/philosophers-toolkit:first-principles` |
| Assess my mastery level for a skill/technology | 守破離 | `/philosophers-toolkit:shu-ha-ri` |

### "I need to make a decision"

| Situation | Skill | Command |
|-----------|-------|---------|
| Choosing between two opposing options (A vs B) | Hegelian Dialectics | `/philosophers-toolkit:dialectics` |
| Testing a specific claim or hypothesis | Popper's Falsifiability | `/philosophers-toolkit:falsify` |
| Doubting whether ANY of my premises are trustworthy | Descartes' Methodical Doubt | `/philosophers-toolkit:doubt` |
| Evaluating if a project/product has real purpose | 生き甲斐 (Ikigai) | `/philosophers-toolkit:ikigai` |

### "I want to improve something"

| Situation | Skill | Command |
|-----------|-------|---------|
| Small, incremental improvement to existing process | 改善 (Kaizen) | `/philosophers-toolkit:kaizen` |
| Judging "good enough" vs over-engineering | 侘寂 (Wabi-Sabi) | `/philosophers-toolkit:wabi-sabi` |

### "I want to reflect or learn"

| Situation | Skill | Command |
|-----------|-------|---------|
| Reflect on what went wrong (blame-free) | 反省 (Hansei) | `/philosophers-toolkit:hansei` |
| Challenge my own thinking through open dialogue | Socratic Method | `/philosophers-toolkit:socratic` |

### "I'm not sure"

If the user can't articulate their need, ask these narrowing questions
(one at a time):

1. "Are you trying to understand something, decide something, improve
   something, or reflect on something?"
2. Based on answer, use the tables above to narrow further.
3. If still unclear, default to **Socratic Method** — it's the most
   general tool and will help clarify what the user actually needs.

## After Routing

Once you've identified the right skill:
1. Tell the user which method you recommend and why (one sentence)
2. Invoke the skill immediately — do NOT explain the method yourself

## Rules

- Do NOT explain philosophical methods in detail — let the skill do that
- Do NOT combine multiple methods — recommend ONE, let the user decide
  if they want another afterward
- If the user already knows which method they want, skip routing and
  invoke directly
- If none of the methods fit, say so honestly — not every problem
  needs a philosophical framework
