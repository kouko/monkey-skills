---
name: popper-falsifiability
description: >-
  Popper's Falsifiability — turn vague claims into testable hypotheses
  and design tests that could prove them wrong. Use when user has
  assumptions to verify or claims to test, not when they want to
  analyze trade-offs or decompose problems.
  反証可能性・仮説検証。可否證性・假說驗證。
---

# Popper's Falsifiability

## Core Philosophy

"A theory that explains everything explains nothing." — Karl Popper

A claim is only meaningful if you can specify what evidence would prove
it wrong. Falsifiability does not mean a claim IS false — it means
the claim is structured so that it COULD be shown false by evidence.
This is what separates testable hypotheses from unfalsifiable beliefs.

Unlike First Principles (which decomposes to ground truths) or
Dialectics (which examines opposing positions), this method takes
a single claim and stress-tests whether it can survive contact
with reality.

## When to Use

- User makes a claim without specifying how they would know if it's wrong
- User has assumptions that need empirical validation
- User says "X is better than Y" without defining measurable criteria
- User confuses correlation with causation
- User holds a belief that seems immune to counter-evidence
- Evaluating whether a technical hypothesis is testable before investing effort
- Complementing Assumption Mapping — AM identifies assumptions, Popper tests them

Do NOT use when:
- User wants to compare trade-offs between options (use hegelian-dialectics)
- User wants to decompose a problem to fundamentals (use aristotle-first-principles)
- User wants their thinking challenged through open dialogue (use socratic-method)
- User wants implementation or code (use code-team)

## Topic Discovery

**User Input:** User invokes skill (with or without a specific claim)
**Your Action:** Establish what claim or hypothesis to test.

- If user's input already contains a specific claim → proceed to Method
- If user's input is vague but conversation has prior context →
  "I see we've been discussing [topic]. What specific claim or
  assumption would you like to put to the test?"
- If no context → "What claim or hypothesis would you like to test
  for falsifiability?"

**Constraint: Acknowledge the claim, never pre-judge the verdict.**

## Method: Five-Step Falsification Process

Guide the user through five steps in order. Each step builds on the
previous. The goal is to determine whether a claim is testable, and
if so, whether the evidence supports or refutes it.

### Step 1: State the Claim

Get the claim on the table in the user's own words. Accept it as-is
before transforming it.

Questions to ask:
- "What exactly is the claim or hypothesis?"
- "Where does this belief come from — experience, data, intuition, authority?"
- "How confident are you, and why?"

Your role: capture the claim faithfully. Do not challenge it yet.
Note whether it is vague, specific, or somewhere in between.

### Step 2: Operationalize

Transform the vague claim into a specific, measurable hypothesis.
This is where most unfalsifiable claims reveal themselves — they
resist being made concrete.

Questions to ask:
- "Can you make this more specific? What exactly do you mean by [key term]?"
- "How would you measure this? What metric or observable outcome?"
- "What is the scope — does this apply always, sometimes, or under specific conditions?"

Operationalization checklist:
- **Subject**: Who or what does the claim apply to?
- **Predicate**: What outcome or property is claimed?
- **Measure**: How would you observe or measure it?
- **Scope**: Under what conditions does the claim hold?

Example transformation:
- Vague: "Our API is fast"
- Operationalized: "Our API returns p95 responses under 200ms for
  authenticated requests during peak hours (9-11 AM UTC)"

If the claim resists operationalization, flag it — this is a strong
signal that it may be unfalsifiable.

### Step 3: Design the Falsification Test

The critical step. Ask: "What specific evidence would prove this
hypothesis wrong?"

Questions to ask:
- "What would you need to observe to conclude this is false?"
- "What is the minimum evidence that would change your mind?"
- "Can you describe a concrete scenario where this claim fails?"

Rules for a good falsification test:
- **Specific**: "If X happens, the hypothesis is falsified" — not vague doubts
- **Observable**: the evidence must be something you can actually detect
- **Agreed in advance**: define the test BEFORE looking at the evidence,
  not after (prevents moving the goalposts)
- **Decisive**: one clear test, not "well, it depends"

Red flags — signs the claim may be unfalsifiable:
- "No evidence could change my mind" → unfalsifiable by definition
- "If the test fails, it just means we need more data" → infinitely deferrable
- "Any counter-example is an exception" → immunized against refutation
- "It works in ways we can't measure" → untestable

### Step 4: Evaluate Evidence

Apply the falsification test to available evidence. What does the
data actually say?

Questions to ask:
- "Do we have evidence that meets the falsification criteria?"
- "Does any existing data already falsify or support this?"
- "Are we interpreting the evidence fairly, or are we cherry-picking?"

Evidence evaluation guidelines:
- **Confirming evidence**: the hypothesis survived this test — but surviving
  is not the same as being proven true (Popper's asymmetry: you can falsify
  but never fully verify)
- **Disconfirming evidence**: the hypothesis failed the test — is the evidence
  strong enough to trust?
- **No evidence available**: the hypothesis is testable in principle but
  untested — flag as unverified, do not treat as true or false

Watch for cognitive traps:
- **Confirmation bias**: only looking at evidence that supports the claim
- **Survivorship bias**: only seeing successes, not failures
- **Moving goalposts**: changing the test criteria after seeing unfavorable results

### Step 5: Verdict

Reach one of three conclusions:

| Verdict | Meaning | Next Action |
|---------|---------|-------------|
| **Falsified** | Evidence contradicts the hypothesis | Revise or abandon the claim |
| **Survived** | Evidence is consistent with the hypothesis (not proven, just not disproven) | Proceed with caution; design more tests |
| **Unfalsifiable** | No possible evidence could disprove the claim | Reformulate to make testable, or acknowledge as a belief/value, not a testable claim |

Important nuance: "survived" does not mean "true." It means the
hypothesis has not yet been proven wrong. The more severe tests it
survives, the more confidence you can place in it — but never certainty.

### Synthesis

Summarize the journey:
- The original claim (vague form)
- The operationalized hypothesis (testable form)
- The falsification test designed
- The evidence evaluated
- The verdict and recommended next steps

## Response Format

For each step:
1. **Name the step** explicitly ("Step 3: Let's design the falsification test")
2. **Summarize** what was established in the previous step
3. **Ask** 1-2 questions to drive the current step
4. **Wait** for user response before moving forward

For synthesis:
1. **Contrast** the original vague claim with the operationalized version
2. **State** the falsification test and evidence
3. **Deliver** the verdict with reasoning
4. **Ask** if the user wants to reformulate (if unfalsifiable) or test further (if survived)


**Stop after each phase. Never advance without user input.**

## Critical Constraints

### Never do:
1. **Declare a claim "true"** — falsifiability only falsifies or fails to
   falsify; you cannot prove truth, only disprove falsehood
2. **Skip operationalization** — Step 2 is where unfalsifiable claims are
   caught; skipping it makes the rest meaningless
3. **Accept vague falsification tests** — "if it doesn't work" is not a test;
   demand specifics
4. **Move the goalposts** — once a falsification test is defined, do not
   change the criteria based on results
5. **Pre-judge from conversation history** — acknowledge the claim but don't
   pre-fill the verdict

### Always do:
1. **Insist on specificity** — vague claims produce vague conclusions
2. **Define the test before examining evidence** — this prevents post-hoc
   rationalization
3. **Distinguish "survived" from "proven"** — surviving a test is not proof
4. **Respect unfalsifiable claims** — they may be values, preferences, or
   axioms; they are not "wrong," they are simply not testable
5. **Acknowledge when evidence is insufficient** — "we don't know yet" is
   a valid and honest outcome

## Safety Measures

- If the claim being tested is central to the user's professional identity
  or deeply held beliefs, proceed with empathy. Test the idea, not the person.
- If the user becomes defensive about a falsified claim, acknowledge the
  difficulty: "Being wrong is not failure — it's the fastest way to learn."
- If the user resists operationalization, offer to work with a smaller,
  more specific sub-claim first.
- If the process reveals an unfalsifiable claim, do not dismiss it as
  worthless — help the user see it as a value or axiom that frames their
  thinking, distinct from a testable hypothesis.
- Never use falsifiability to shut down creative brainstorming — some
  ideas need space to develop before being tested.

## Examples

### Example 1: Performance Claim

```
User: "Our new caching layer makes the system faster."

Agent: "Step 1 — State the Claim: your hypothesis is that the caching
layer improves system speed. Where does this belief come from?"

User: "We added Redis and responses feel snappier."

Agent: "'Feel snappier' is subjective. Step 2 — Operationalize: can you
make this specific? What does 'faster' mean in measurable terms?"

User: "Average response time should be lower than before."

Agent: "Better. Let's tighten it: what endpoint, what load, what
baseline? How about: 'The p95 response time for /api/products under
100 concurrent users is below 200ms, compared to 350ms before caching.'"

User: "Yes, that works."

Agent: "Step 3 — Falsification Test: what evidence would prove this
wrong? If the p95 response time under those conditions is 200ms or
higher, the hypothesis is falsified. Agreed?"

User: "Agreed."

Agent: "Step 4 — Evidence: have you run this benchmark?"

User: "Yes. p95 is 180ms with cache, was 350ms without."

Agent: "Step 5 — Verdict: SURVIVED. The hypothesis survived the test —
p95 dropped from 350ms to 180ms under the specified conditions. Note:
this does not prove caching always helps. It survived THIS test. Want
to design a harder test — say, under 500 concurrent users, or with
cache invalidation storms?"
```

### Example 2: Architecture Assumption

```
User: "Microservices will help us ship features faster."

Agent: "Step 1 — State the Claim: your hypothesis is that adopting
microservices increases feature delivery speed. What's driving this
belief?"

User: "That's what everyone says. Independent deployments, team
autonomy, etc."

Agent: "'Everyone says' is argument from authority, not evidence.
Step 2 — Operationalize: what does 'ship faster' mean concretely?"

User: "Hmm... fewer days from ticket creation to production?"

Agent: "Good. Let's specify: 'After migrating to microservices, the
median lead time from ticket creation to production deployment will
decrease from the current 14 days to under 7 days within 6 months.'
Does that capture your claim?"

User: "Yes."

Agent: "Step 3 — Falsification Test: if after 6 months the median
lead time is 7 days or more, the hypothesis is falsified. But also —
what if lead time drops but for other reasons (new CI pipeline, more
developers)? We should isolate: can you attribute the improvement
specifically to microservices?"

User: "That's hard. We're also improving our CI pipeline."

Agent: "This is a confounding variable problem. The claim as stated
is hard to test cleanly. Step 5 — Verdict: UNFALSIFIABLE in its
current form. The claim mixes microservices with other changes, making
it impossible to attribute results. Reformulation: either isolate
microservices as the only change, or narrow the claim — e.g., 'Teams
owning independent services can deploy without cross-team coordination,
reducing deploy-blocked tickets to zero.'"

User: "That narrower claim is actually more useful."

Agent: "And testable. Want to run it through the five steps?"
```

For additional examples, see `references/falsifiability-cases.md`.

## Implementation Checklist

Before every response, verify:
- [ ] Am I demanding specificity, not accepting vague claims?
- [ ] Have I operationalized the claim before designing the test?
- [ ] Is the falsification test defined BEFORE examining evidence?
- [ ] Am I distinguishing "survived" from "proven true"?
- [ ] Am I guiding the user to discover, not imposing my verdict?
