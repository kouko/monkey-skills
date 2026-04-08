---
name: aristotle-first-principles
description: >-
  First Principles Thinking — decompose problems to fundamental truths
  and rebuild from scratch, rejecting analogy and convention. Use when
  user wants to rethink a problem from zero, not when they want to
  analyze what exists or compare options.
  第一原理思考。第一原理・根本から考え直す。
---

# Aristotle's First Principles

## Core Philosophy

"If you want to understand something, break it down to its most basic
truths — things that cannot be reduced further — and reason upward
from there." — Aristotle

First principles thinking rejects reasoning by analogy ("others do it
this way, so we should too") and instead asks: what do we KNOW to be
true, and what can we build from only those truths?

Unlike Four Causes (which analyzes what exists) or Dialectics (which
examines trade-offs), this method starts from zero and rebuilds.

## When to Use

- User is trapped by "best practices" that may not apply to their context
- User says "everyone does it this way" without questioning why
- User wants to rethink a problem from scratch
- Evaluating whether an architectural decision is truly optimal
- Legacy assumptions are constraining new thinking
- Building something novel where existing patterns may mislead

Do NOT use when:
- User wants to understand what something IS (use aristotle-four-causes)
- User wants to compare trade-offs between options (use hegelian-dialectics)
- User wants their thinking challenged through dialogue (use socratic-method)
- User wants implementation (use code-team)

## Topic Discovery

**User Input:** User invokes skill (with or without a specific problem)
**Your Action:** Establish what problem to decompose.

- If user's input already contains a specific problem → proceed to Method
- If user's input is vague but conversation has prior context →
  "I see we've been discussing [topic]. What assumption or convention
  do you want to challenge from first principles?"
- If no context → "What problem would you like to rethink from scratch?"

**Constraint: Acknowledge topic, never pre-judge the conclusion.**

## Method: Five-Phase Decomposition

Guide the user through five phases in order. Each phase builds on the
previous. The goal is to arrive at a solution built only from verified
truths, not from convention or analogy.

### Phase 1: Problem Essence

Strip the problem to its core. Separate what you're ACTUALLY trying
to achieve from the solution you've assumed.

Questions to ask:
- "What are you actually trying to achieve? State it as an outcome, not a solution."
- "What would success look like if there were no existing solutions to reference?"
- "Are you solving the real problem, or a symptom?"

Trap to avoid: users often state problems as solutions
("we need a database" vs "we need to persist and query structured data").

### Phase 2: Challenge Assumptions

List every assumption — explicit and implicit — then test each one.

Questions to ask:
- "What are you assuming must be true for your current approach to work?"
- "Which of these assumptions come from convention ('everyone does it this way')
  vs evidence ('we tested and confirmed this')?"
- "What would change if this assumption were false?"

Categories of assumptions:
- **Technical**: "we need X technology" — do we really?
- **Business**: "users want Y" — have we verified?
- **Resource**: "we can't afford Z" — based on what cost model?
- **Historical**: "we tried that before" — in what context?

For each assumption, reach a verdict:
- **Confirmed**: evidence supports it → keep as ground truth
- **Unverified**: no evidence either way → flag for testing
- **False**: evidence contradicts it → discard

### Phase 3: Establish Ground Truths

Identify the irreducible facts — things that cannot be broken down
further and cannot be violated.

Questions to ask:
- "After challenging assumptions, what remains true no matter what?"
- "What constraints are physics/math/logic, not convention?"
- "What are the non-negotiable user needs (not wants, needs)?"

Aim for 3-5 ground truths. If you have more than 7, some are
probably derived truths (built on other truths) not fundamental ones.

Examples of ground truths vs false fundamentals:
- Ground truth: "data must persist across sessions"
- False fundamental: "we need a relational database" (one solution, not a truth)
- Ground truth: "users need to find information in under 2 seconds"
- False fundamental: "we need Elasticsearch" (one solution, not a truth)

### Phase 4: Reason Upward

Build a solution from ONLY the ground truths. Add nothing that isn't
justified by a ground truth.

Questions to ask:
- "Given only these ground truths, what is the simplest solution?"
- "For each component in your solution, which ground truth justifies its existence?"
- "What would you remove if you could only keep what's essential?"

Rules:
- Every component must trace to a ground truth
- If you can't justify a component, it's complexity from convention, not necessity
- Start minimal, add only what ground truths demand

### Phase 5: Validate Reasoning

Stress-test the solution. Check for gaps in the reasoning chain.

Questions to ask:
- "Can you trace every decision back to a ground truth?"
- "Where is the weakest link in the reasoning chain?"
- "What could make this solution fail despite starting from first principles?"

Also check for traps:
- **Complexity trap**: did unnecessary complexity sneak back in?
- **Analogy trap**: did you unconsciously copy an existing solution?
- **Legacy trap**: are you maintaining compatibility with something that
  no longer needs to exist?

### Synthesis

Summarize the journey:
- What the problem ACTUALLY is (vs what was assumed)
- Which assumptions were false
- What ground truths remain
- What solution emerges from only those truths
- How it differs from the conventional approach and why

## Response Format

For each phase:
1. **Name the phase** explicitly ("Phase 2: Let's challenge your assumptions")
2. **Summarize** what was established in the previous phase
3. **Ask** 1-2 questions to drive the current phase
4. **Wait** for user response before moving forward

For synthesis:
1. **Contrast** the first-principles solution with the conventional approach
2. **Trace** each component to its ground truth
3. **Ask** if the user sees value in the rebuilt solution vs the original

## Critical Constraints

### Never do:
1. **Accept "best practice" as justification** — always ask "why is this best?"
2. **Skip assumption challenging** — Phase 2 is the most important phase
3. **Build from analogy** — "like Uber for X" is not first principles
4. **Dismiss all existing solutions** — sometimes convention is right, but you
   must verify WHY it's right, not just accept that it is
5. **Pre-judge from conversation history** — acknowledge the topic but don't
   pre-fill the analysis

### Always do:
1. **Demand evidence for every assumption** — "how do you know?"
2. **Separate outcomes from solutions** — users state solutions, you extract outcomes
3. **Count ground truths** — fewer is better, aim for 3-5
4. **Trace components to truths** — every piece of the solution must justify itself
5. **Acknowledge when convention is correct** — first principles sometimes confirms
   the existing approach, and that's a valid outcome

## Safety Measures

- If the user's entire career or team has been built on a convention being
  challenged, be respectful. Question the idea, not the person.
- If first-principles analysis leads to an impractical solution ("build your
  own OS"), acknowledge practical constraints as a type of ground truth.
- If the user gets frustrated with decomposition, offer to focus on the
  assumption they're most uncertain about rather than challenging everything.
- Never use this method to dismiss domain expertise — expertise informs
  which assumptions to challenge first.

## Examples

### Example 1: Rethinking Authentication

```
User: "We need to add OAuth2 to our internal tool."

Agent: "Phase 1 — Problem Essence: let's start from what you're actually
trying to achieve. What outcome do you need? Not the solution, the outcome."

User: "Users need to prove they are who they say they are before accessing
the tool."

Agent: "Authentication — identity verification. Phase 2 — Challenge
Assumptions. What are you assuming by jumping to OAuth2?"

User: "That we need a standard protocol. That we need third-party identity
providers. That we need token-based auth."

Agent: "Let's test each. This is an internal tool — who are the users?"

User: "50 employees, all on our corporate network."

Agent: "So the assumption 'we need third-party identity providers' — is
that true for 50 internal users on a corporate network?"

User: "No... they're already authenticated by the corporate directory."

Agent: "Phase 3 — Ground Truths. What's actually irreducible here?"

User: "Users must be verified. They're already on corporate auth. The tool
must not be accessible to outsiders."

Agent: "Phase 4 — Reason Upward. Given only those truths, what's the
simplest solution?"

User: "Just use the corporate SSO we already have. No OAuth2 needed."

Agent: "Synthesis: the original problem was 'add OAuth2' (a solution).
The actual need was 'verify internal users' (an outcome). The assumption
'we need a third-party protocol' was false for an internal tool with
existing corporate auth. First principles eliminated an entire integration
by questioning why OAuth2 was needed in the first place."
```

### Example 2: Rethinking Data Storage

```
User: "We're choosing between PostgreSQL and MongoDB for our new service."

Agent: "Phase 1 — before choosing between databases, what's the actual
outcome you need?"

User: "Store and retrieve user activity data — events like clicks,
page views, feature usage."

Agent: "Phase 2 — you're assuming you need a general-purpose database.
What are your actual access patterns?"

User: "Mostly writes. Tons of events coming in. Reads are rare — only
when generating weekly reports."

Agent: "Phase 3 — Ground Truths: high write volume, rare reads, event
data (append-only), weekly batch processing. What's irreducible?"

User: "Data must be durable. Writes must not block the application.
Reports need data from the past 90 days."

Agent: "Phase 4 — Given only those truths: high writes, append-only,
rare batch reads, 90-day window. Do you need a database at all?"

User: "Wait... we could just write to log files and process them with
a batch job?"

Agent: "Or an append-only store like S3 + a batch query engine. Synthesis:
the PostgreSQL vs MongoDB debate assumed 'we need a database.' First
principles revealed the access pattern is write-heavy append-only with
rare batch reads — a pattern better served by log storage than a database.
The original framing hid the real question."
```

For additional examples, see `references/first-principles-cases.md`.

## Implementation Checklist

Before every response, verify:
- [ ] Am I questioning solutions, not just comparing them?
- [ ] Have I separated the outcome from the assumed solution?
- [ ] Am I demanding evidence for assumptions, not accepting convention?
- [ ] Is every component in the emerging solution traceable to a ground truth?
- [ ] Am I guiding the user to discover, not imposing my analysis?
