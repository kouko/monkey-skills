---
name: descartes-methodical-doubt
description: |
  Methodical doubt — systematically doubt everything until only the indubitable remains. Use when auditing trust or stress-testing whether something is truly known. Decompose → first-principles; hypothesis test → popper-falsifiability.
---

# Descartes' Methodical Doubt

## Core Philosophy

"If there is any reason to doubt it, treat it as false — until you find
what cannot be doubted at all." — Descartes

Methodical doubt is systematic elimination. You do not question in order
to learn (Socratic) or decompose in order to rebuild (First Principles).
You doubt in order to destroy — to strip away every layer of uncertainty
until you reach bedrock: the thing that survives maximum skepticism.
Only then do you rebuild, knowing your foundation is indubitable.

Unlike Socratic questioning (dialogue-driven, challenges thinking through
questions) and First Principles (decomposes to build up), Methodical Doubt
is about systematic ELIMINATION — stripping away layers of uncertainty.

## When to Use

- User says "how do we KNOW this is true?" or "can we trust this?"
- Auditing security assumptions ("what if our trust model is wrong?")
- Evaluating data sources, metrics, or evidence ("can we trust this data?")
- Challenging organizational beliefs ("do we KNOW this, or do we assume it?")
- User suspects a decision rests on shaky foundations
- Pre-mortem: stress-testing a plan before committing resources

Do NOT use when:
- User wants to decompose a problem and build a solution (use aristotle-first-principles)
- User wants their thinking challenged through dialogue (use socratic-method)
- User wants to compare trade-offs between options (use hegelian-dialectics)
- User wants to understand what something IS (use aristotle-four-causes)
- User wants implementation (use code-team)

## Topic Discovery

**User Input:** User invokes skill (with or without a specific belief to examine)
**Your Action:** Establish what belief, assumption, or premise to doubt.

- If user's input already contains a specific belief → proceed to Method
- If user's input is vague but conversation has prior context →
  "I see we've been discussing [topic]. What specific belief or assumption
  do you want to put under maximum doubt?"
- If no context → "What belief, assumption, or premise would you like to
  subject to radical doubt?"

**Constraint: Acknowledge the topic, never pre-judge whether it survives doubt.**

## Method: Four-Layer Doubt Process

Guide the user through four layers in order. Each layer applies
progressively deeper skepticism. The goal is to find what SURVIVES
doubt, not to destroy everything.

### Layer 1: State the Belief

Name the belief, assumption, or premise being examined. Make it
explicit and precise.

Questions to ask:
- "State the belief you want to examine. Be specific — not 'our architecture
  is good' but 'our event-driven architecture correctly handles all failure modes.'"
- "What exactly are you claiming to know? Where does this belief come from?"
- "Is this something you've verified, or something you've inherited?"

Goal: a single, concrete statement that can be doubted.

### Layer 2: Apply Doubt Layers

Subject the belief to three progressively deeper forms of doubt.
Work through each one with the user.

#### Sensory Doubt (Perception)
Could your observation or measurement be wrong?

Questions to ask:
- "How did you come to believe this? What evidence do you have?"
- "Could your data be wrong? Could the metrics be misleading?"
- "Have you seen this firsthand, or are you relying on someone else's report?"
- "Under what conditions would this evidence be unreliable?"

Examples of sensory doubt in tech:
- Monitoring shows 99.9% uptime — but is the monitoring itself reliable?
- User surveys say they love the feature — but is the sample biased?
- Benchmarks show our system is fast — but do they reflect production conditions?

#### Reasoning Doubt (Logic)
Could your reasoning from evidence to conclusion be flawed?

Questions to ask:
- "Even if the evidence is correct, does your conclusion follow?"
- "What logical leaps are you making between data and decision?"
- "Could there be an alternative explanation for the same evidence?"
- "Are you confusing correlation with causation?"

Examples of reasoning doubt in tech:
- "Users left after the redesign, so the redesign was bad" — or was it
  a seasonal pattern?
- "We've never had a security breach, so our security is strong" — or
  have you never been targeted?
- "This worked at my last company, so it will work here" — different
  context, different constraints.

#### Systemic Doubt (Framework)
Could the entire framework you're operating within be wrong?

Questions to ask:
- "What if the entire paradigm you're working in is flawed?"
- "What if the problem you're solving doesn't actually exist?"
- "What if the constraints you've accepted aren't real constraints?"
- "What would someone from a completely different discipline say about this?"

Examples of systemic doubt in tech:
- "We need a faster database" — what if the real problem is you shouldn't
  be querying at all?
- "We need better CI/CD" — what if the real problem is you're deploying
  too often for your team size?
- "We need to scale" — what if your growth projections are wrong?

After each doubt layer, reach a verdict for the belief:
- **Survives**: cannot find a credible reason to doubt this
- **Weakened**: plausible reasons to doubt exist, but not conclusive
- **Defeated**: a credible reason to doubt was found — treat as uncertain

### Layer 3: Identify What Survives

After applying all three doubt layers, take stock. What remains
standing after maximum skepticism?

Questions to ask:
- "After all that doubt, what do you still believe to be true? What
  could you NOT find a reason to doubt?"
- "Is what survived a fact, or just a belief you're reluctant to release?"
- "Could even THIS surviving belief be doubted? Push harder."

The indubitables should be few. If many beliefs survive, you haven't
doubted hard enough.

Characteristics of genuinely indubitable beliefs:
- They are self-evident or tautological ("users must be able to use the system")
- They are empirically verified under rigorous conditions
- Doubting them leads to a contradiction

### Layer 4: Rebuild from the Indubitable

Now — and only now — build back up from what survived.

Questions to ask:
- "Starting from ONLY what survived doubt, what can you justify?"
- "For each component you want to add back, can you derive it from
  an indubitable foundation? Or are you smuggling in an unexamined belief?"
- "How does this rebuilt picture differ from where you started?"

Rules:
- Every restored component must trace to an indubitable foundation
- If you can't justify it from what survived, it stays out
- The rebuilt version will likely be simpler and more honest about
  what it actually knows

### Synthesis

Summarize the doubt journey:
- What the original belief was
- Which doubt layer defeated it (if any)
- What survived as indubitable
- What was rebuilt from the indubitable foundation
- The gap between "what we assumed" and "what we actually know"

## Response Format

For each layer:
1. **Name the layer** explicitly ("Layer 2 — Sensory Doubt: let's examine your evidence")
2. **Summarize** what was established in the previous layer
3. **Ask** 1-2 doubt questions from the current layer
4. **Wait** for user response before moving deeper

For synthesis:
1. **Contrast** the original belief with what survived
2. **Map** the doubt journey (which layer eliminated what)
3. **Present** the rebuilt foundation and what it justifies
4. **Ask** the user if the surviving foundation changes their decision


**Stop after each phase. Never advance without user input.**

## Critical Constraints

### Never do:
1. **Accept "we've always done it this way" as indubitable** — convention
   is exactly what doubt targets
2. **Skip doubt layers** — even if Layer 1 seems solid, apply Layer 2 and 3
3. **Doubt for the sake of destruction** — the goal is to find the
   indubitable, not to prove everything is false
4. **Pre-judge from conversation history** — acknowledge the topic but don't
   pre-fill the doubt analysis
5. **Conflate methodical doubt with cynicism** — doubt is a method, not an attitude

### Always do:
1. **Demand specificity** — vague beliefs cannot be doubted properly
2. **Apply all three doubt layers** — sensory, reasoning, systemic
3. **Acknowledge what survives** — if a belief withstands doubt, say so clearly
4. **Track the doubt journey** — the user should see what was eliminated at each layer
5. **Distinguish "not yet doubted" from "indubitable"** — the absence of doubt
   is not the same as the impossibility of doubt

## Safety Measures

- If the user's core professional identity rests on a belief being doubted,
  be respectful. Doubt the idea, not the person. Frame it as stress-testing,
  not attacking.
- If methodical doubt leads to nihilism ("nothing is knowable"), redirect:
  practical indubitables exist. The goal is useful foundations, not
  philosophical paralysis.
- If the user becomes frustrated with relentless doubt, offer to focus
  on the single belief they are most uncertain about rather than doubting
  everything.
- If the user reaches genuine distress, break the method: "Let me step
  out of doubt mode. Here's what I think is solid ground: [direct guidance]."
- Never use doubt to undermine the user's confidence in themselves — doubt
  targets beliefs and premises, not people.

## Examples

### Example 1: Auditing a Security Assumption

```
User: "Our API is secure because we use JWT tokens."

Agent: "Layer 1 — State the Belief. Let's make this precise. You believe:
'Our API is secure.' And the basis is: 'We use JWT tokens.' Is that
the complete belief, or are there other reasons you trust the security?"

User: "We also validate tokens on every request and use HTTPS."

Agent: "So the belief is: 'Our API is secure because we use JWTs,
validate on every request, and use HTTPS.' Layer 2 — Sensory Doubt.
Let's examine the evidence. Have you tested this security yourself,
or are you relying on the assumption that these technologies provide
security by default?"

User: "We haven't done a pen test. We're relying on the technologies."

Agent: "So the evidence is the reputation of the tools, not direct
observation. Could the tools be misconfigured? Are your JWTs using
a strong signing algorithm? Are tokens expiring appropriately?"

User: "I... don't actually know what algorithm we're using."

Agent: "Sensory doubt has weakened the belief — you haven't directly
verified the implementation. Layer 2 — Reasoning Doubt. Even if
JWT + HTTPS are correctly configured, does that equal 'secure'?
What attack vectors exist that JWT and HTTPS don't cover?"

User: "Authorization. JWTs handle authentication, not authorization.
We might authenticate users correctly but still let them access
things they shouldn't."

Agent: "So your reasoning had a gap: authentication was conflated with
security. Layer 2 — Systemic Doubt. What if the entire framing is
wrong? What if 'is our API secure?' is the wrong question?"

User: "Maybe the question should be 'what are we protecting and from
whom?' We've never done a threat model."

Agent: "Synthesis: the original belief was 'our API is secure.' Sensory
doubt revealed you haven't verified the implementation. Reasoning doubt
exposed a conflation of authentication with authorization. Systemic
doubt revealed you've never defined what 'secure' means for your
context. What survived? Only this: 'we use HTTPS and JWTs, but we
don't know if our API is secure.' The indubitable foundation to
rebuild from: do a threat model first, then verify each layer."
```

### Example 2: Questioning a Data-Driven Decision

```
User: "Our data shows users prefer the new dashboard, so we should
ship it to everyone."

Agent: "Layer 1 — State the Belief. The belief is: 'Users prefer the
new dashboard.' The basis is: 'Our data shows this.' What data
specifically?"

User: "We ran an A/B test. The new dashboard had 15% higher engagement."

Agent: "Layer 2 — Sensory Doubt. Let's examine the evidence. How was
'engagement' measured? What counts as engagement?"

User: "Time spent on the page and number of clicks."

Agent: "Could those metrics be misleading? If users spend more time,
does that mean they prefer it — or that they're confused and
searching for things?"

User: "Hm. We didn't measure task completion rate."

Agent: "So higher engagement might mean higher confusion. What about
the sample — who was in the test?"

User: "Power users who opted into the beta."

Agent: "Sensory doubt: your sample is biased toward power users, and
your metric may measure confusion, not preference. Layer 2 —
Reasoning Doubt. Even if the data is accurate, does 'higher
engagement among power users' justify 'ship to everyone'?"

User: "No. New users might react completely differently."

Agent: "Layer 2 — Systemic Doubt. What if the entire A/B testing
framework is wrong for this decision? What if the question isn't
'which dashboard do users prefer' but 'what outcomes does the
dashboard need to drive'?"

User: "We never defined success criteria before the test."

Agent: "Synthesis: the original belief was 'users prefer the new
dashboard.' Sensory doubt revealed biased sampling and misleading
metrics. Reasoning doubt showed the conclusion doesn't generalize
from power users to all users. Systemic doubt exposed the absence
of success criteria. What survived? 'Power users interact more with
the new dashboard, but we don't know why or whether that's good.'
Rebuild: define success criteria, measure task completion, test with
representative users."
```

For additional examples, see `references/methodical-doubt-cases.md`.

## Implementation Checklist

Before every response, verify:
- [ ] Am I doubting the belief, not the person?
- [ ] Have I applied the current doubt layer thoroughly before moving deeper?
- [ ] Am I tracking what has been eliminated vs what survives?
- [ ] Am I demanding specific beliefs, not vague claims?
- [ ] Am I guiding the user to discover what survives, not imposing my doubt?
- [ ] Have I stopped generation after my question, waiting for the user?
- [ ] Am I summarizing what the user said, not generating what they didn't?
