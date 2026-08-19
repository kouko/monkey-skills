---
name: a-rule-stricter-than-the-corpus-best-human-work-is-miscalibrated
description: When a new gate's threshold is picked by reasoning rather than measured, run it against the best existing human-authored examples you have — if it fails them, the threshold is wrong even though the rule's direction is right. Measured: requiring every load-bearing input to be named passed 1/10 and failed both nodes a human had marked as the good ones; requiring at least one passed exactly those two. A gate that flags the work you would hold up as the model teaches authors that the gate is noise.
type: practice
origin: think-orbit 0.1.4 transparency arc, T1 threshold correction (2026-08-19) — the "every" variant was written into the brief and plan without being measured, and the measurement reversed it
---

The rule's direction was settled and correct: a node body must name an upstream it
stands on. The threshold was written from reasoning — "every load-bearing input" —
because it sounded like the stricter, safer choice. It was never measured before it
went into the brief, the plan, and a task's acceptance criteria.

Measured against the real corpus, three variants:

| threshold | passes | which |
|---|---|---|
| names **every** load-bearing input | 1/10 | one node with zero load-bearing inputs — vacuously true |
| names **at least one** load-bearing input | 2/10 | exactly the two a human had marked as good |
| names at least one input of any kind | 2/10 | the same two |

The "every" variant failed both DECISION nodes that a human checkpoint had already
identified as the ones that genuinely narrate their reasoning. They carry four and
three load-bearing inputs and name only some of them — which is what a person does
when writing prose that stands on several things: they name the ones that carry the
argument. The only node "every" passed was one with no load-bearing inputs at all,
passing on an empty set.

**The calibration target was available the whole time.** The checkpoint had already
recorded, by hand, which nodes narrate and which do not. Any threshold could have
been checked against that reading in one command before it was written down.

The measurement also exposed a boundary the specification never covered: a node with
inputs but none load-bearing can never satisfy a load-bearing-only rule, no matter
what its author writes. Unsatisfiable-for-some-inputs is a shape worth checking for
directly whenever a rule quantifies over a filtered subset.

**How to apply:**
1. Before a threshold ships, run it over the best human-authored examples in the
   corpus. Failing them is disqualifying, not conservative.
2. "Stricter" is not a safe default. A gate that fires on good work is not cautious,
   it is miscalibrated, and it trains authors to route around the gate.
3. When a rule quantifies over a filtered subset (`every X that is Y`), check what
   happens when the subset is empty. Both the vacuous pass and the unsatisfiable
   fail are usually wrong.
4. Write the measured figures into the brief next to the threshold, with their
   denominator. A number in a shipped document is a claim, and the next reader will
   act on it.

Relates to [[lexical-overlap-cannot-separate-narrating-from-sharing-a-topic]] (the
earlier correction on the same rule) and [[a-test-can-pin-behaviour-with-a-false-rationale]]
(a guard whose stated justification is false; here the justification was true and the
threshold derived from it was not).
