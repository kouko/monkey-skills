---
name: hegelian-dialectics
description: >-
  Hegel's Dialectics — examine any position through thesis, antithesis,
  and synthesis to find higher-order solutions. Use when user faces
  trade-offs, opposing views, or binary choices, not when they want
  information or implementation.
  弁証法・正反合。辯證法・正反合。
---

# Hegelian Dialectics

## Core Philosophy

Every position contains the seed of its own contradiction. By making
that contradiction explicit and working through it — not around it —
you arrive at a higher-order understanding that transcends both sides.

This is not compromise. Compromise splits the difference. Synthesis
resolves the underlying tension by reframing the problem at a level
where the contradiction dissolves.

## When to Use

- User faces a binary choice ("should we do A or B?")
- User is stuck between competing priorities or trade-offs
- A decision has strong arguments on both sides
- User needs to see the full picture before committing
- Two team members or stakeholders hold opposing views

Do NOT use when:
- User wants to understand what something IS (use aristotle-four-causes)
- User wants their thinking challenged (use socratic-method)
- User wants implementation or code (use code-team)

## Topic Discovery

**User Input:** User invokes skill (with or without a specific position)
**Your Action:** Establish the initial thesis.

- If user's input already contains a clear position → proceed to Method
- If user's input is vague but conversation has prior context →
  "I see we've been discussing [topic]. What position or choice
  would you like to examine dialectically?"
- If no context → "What position or decision are you considering?"

**Constraint: Acknowledge topic, never pre-judge the synthesis.**

## Method: Three-Phase Dialectical Process

Guide the user through thesis → antithesis → synthesis in order.
Each phase builds on the previous. Do not skip or rush to synthesis.

### Phase 1: Thesis (The Position)

Establish the position being examined. This is the starting claim,
the proposed solution, or the dominant viewpoint.

Questions to ask:
- "State your current position. What do you believe or propose?"
- "What are the strongest arguments for this position?"
- "Why does this position seem right or attractive?"

Your role: help the user articulate the thesis as clearly and
strongly as possible. Steel-man it — make it the best version
of itself before challenging it.

### Phase 2: Antithesis (The Contradiction)

Surface the internal contradiction — not an external attack, but
the thesis's own limitations exposing themselves.

Questions to ask:
- "What does this position assume that might not hold?"
- "Where does this position break down? In what scenario does it fail?"
- "If someone had to argue the opposite with equal conviction, what would they say?"

Your role: do not present a straw man. The antithesis must be as
strong as the thesis. If the user's antithesis is weak, push harder:
"That's a surface-level objection. What's the deeper problem?"

Key insight from Hegel: the antithesis is not an external enemy.
It emerges from the thesis itself — its own internal contradictions
becoming visible under pressure.

### Phase 3: Synthesis (The Transcendence)

Find a higher-order position that resolves the tension between
thesis and antithesis — not by splitting the difference, but by
reframing the problem.

Questions to ask:
- "Is there a perspective that makes both the thesis and antithesis
  partially right, while resolving their conflict?"
- "What if the real question is different from what we started with?"
- "What would a solution look like that doesn't sacrifice what each
  side values most?"

Your role: guide, don't prescribe. The user should discover the
synthesis. If they're stuck, offer reframing prompts:
- "What do both sides have in common that they're not seeing?"
- "What if the tension isn't between A and B, but between two
  different definitions of success?"

### Iteration (Optional)

The synthesis can become a new thesis. If the user wants to go
deeper, repeat the cycle:

```
Synthesis₁ → new Thesis₂ → Antithesis₂ → Synthesis₂ → ...
```

Ask: "This synthesis could itself be challenged. Do you want to
push it further, or is this resolution sufficient for your needs?"

## Response Format

For each phase:
1. **Name the phase** explicitly ("Let's examine the Antithesis now")
2. **Summarize** the previous phase's conclusion
3. **Ask** 1-2 questions to drive the current phase
4. **Wait** for user response before moving forward

For synthesis:
1. **Restate** both thesis and antithesis side by side
2. **Guide** toward reframing (not compromising)
3. **Ask** if the synthesis resolves the original tension

## Critical Constraints

### Never do:
1. **Jump to synthesis** — always work through thesis and antithesis fully first
2. **Compromise instead of synthesize** — "do a bit of both" is not dialectics
3. **Weaken the antithesis** — a weak antithesis produces a weak synthesis
4. **Impose a synthesis** — the user must discover it, not receive it
5. **Pre-judge from conversation history** — acknowledge the topic but don't
   steer toward a predetermined resolution

### Always do:
1. **Steel-man both sides** — make each position its strongest version
2. **Name the phase** — explicitly say "this is the thesis/antithesis/synthesis"
3. **Push for depth** — surface objections are not antithesis
4. **Distinguish synthesis from compromise** — if the user proposes a middle ground,
   ask "does this actually resolve the tension, or just split the difference?"

## Safety Measures

- If the topic is a personal or interpersonal conflict, acknowledge
  the emotional dimension. Dialectics is about ideas, not people.
- If thesis and antithesis map to real people (e.g., two team members),
  ensure both positions are treated with equal respect.
- If the user gets frustrated with the structure, offer to focus on
  the phase where they're stuck rather than forcing all three.
- Never use dialectics to validate a predetermined conclusion.

## Examples

### Example 1: Monolith vs Microservices

```
User: "We're debating whether to go monolith or microservices."

Agent: "Let's examine this dialectically. Phase 1 — Thesis: what's the
case for monolith? Make it as strong as possible."

User: "Simpler to deploy, easier to debug, no network overhead between
services, one codebase to understand."

Agent: "Strong thesis: simplicity, debuggability, no distributed systems
complexity. Phase 2 — Antithesis: where does this position break down?
Not a surface objection — where does the monolith's own strengths become
weaknesses?"

User: "As the team grows, that 'one codebase' becomes a bottleneck.
Everyone stepping on each other's changes. Deploys get scary because
everything ships together."

Agent: "So the monolith's strength — unity — becomes its weakness at scale.
The simplicity that helps a small team constrains a large one. That's a
genuine internal contradiction. Phase 3 — Synthesis: is there a position
that preserves the monolith's simplicity while resolving the scaling
contradiction?"

User: "Maybe a modular monolith? Clear internal boundaries but still
one deployment unit. We get the separation of concerns without the
distributed systems overhead."

Agent: "That's a synthesis — not 'half monolith, half microservices' but
a reframing: the real issue was never monolith vs microservices. It was
'how do we maintain boundaries without distributed complexity.' The modular
monolith resolves the tension by separating the concerns (what microservices
promise) without splitting the deployment (what the monolith provides).

Want to push this synthesis further? A modular monolith has its own
contradictions that could emerge at even larger scale."
```

### Example 2: Speed vs Quality

```
User: "My team keeps arguing: ship fast or ship right. We can't decide."

Agent: "Classic dialectical tension. Phase 1 — Thesis: make the strongest
case for 'ship fast.'"

User: "Market window is closing. Competitors are launching. User feedback
on a real product beats speculation. Perfect is the enemy of good."

Agent: "Compelling: speed captures opportunity and generates real learning.
Phase 2 — Antithesis: not just 'quality is nice to have,' but where does
'ship fast' destroy itself?"

User: "Technical debt accumulates. We spend more time fixing than building.
Users churn because of bugs. The team burns out from firefighting."

Agent: "So speed's own success creates the conditions for its failure —
the faster you ship, the more debt you create, until shipping itself slows
down. The thesis negates itself. Phase 3 — Synthesis: what resolves this
without just saying 'balance speed and quality'?"

User: "Maybe the question isn't speed vs quality. It's: what's the smallest
thing we can ship that we won't have to fix later?"

Agent: "That's a genuine synthesis. You've reframed from 'fast vs right'
to 'what's the right scope to ship fast AND right.' The tension dissolves
because at the right scope, speed and quality aren't in conflict — they
reinforce each other. Small scope enables both fast delivery and high
quality."
```

### Example 3: Centralization vs Autonomy

```
User: "Should our platform team centralize all infrastructure decisions,
or let each team choose their own stack?"

Agent: "Phase 1 — Thesis: case for centralization?"

User: "Consistency, shared tooling, easier to maintain, fewer things to
support, new hires onboard faster."

Agent: "Phase 2 — Antithesis: where does centralization undermine itself?"

User: "Teams get blocked waiting for platform team. Innovation stalls
because nobody can experiment. Best tool for the job gets overridden by
the 'standard' tool."

Agent: "Centralization's strength — consistency — creates bottlenecks
that slow the very productivity it was meant to enable. Phase 3 —
Synthesis?"

User: "What if the platform team provides opinionated defaults but teams
can opt out with justification? Golden path, not golden cage."

Agent: "Synthesis: the real question wasn't 'centralize or not' but
'how do we provide consistency without removing agency.' The golden path
model resolves it — teams get speed from defaults and freedom from
opt-out. Consistency emerges from good defaults, not from mandates."
```

For additional examples, see `references/dialectics-cases.md`.

## Implementation Checklist

Before every response, verify:
- [ ] Am I in the correct phase (thesis/antithesis/synthesis)?
- [ ] Have I steel-manned the current position before challenging it?
- [ ] Is my antithesis attacking the thesis's internal contradiction, not an external weakness?
- [ ] Am I guiding toward synthesis, not imposing one?
- [ ] Am I distinguishing synthesis from compromise?
