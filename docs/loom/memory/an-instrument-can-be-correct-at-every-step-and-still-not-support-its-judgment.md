---
name: an-instrument-can-be-correct-at-every-step-and-still-not-support-its-judgment
description: A measurement mechanism can be correct at every step it performs and still be structurally unable to answer the question it was built for — this one enforced and verified but never collected, sampled only the rounds that found nothing serious (0 of 24 severity-🔴 findings ever reached it), and would have fed a pre-registered stop rule a null result that was the sampling rule restating itself; check the whole chain from defect to conclusion for attrition and bias before shipping, not just each link's correctness
type: process
origin: the finding-origin-attribution arc (loom-code 0.45.0, 2026-08-02) — six shipped tasks, then a user-requested soundness review that re-cut the design and added four more
---

The arc built an `origin:` field: a reviewer names the upstream document
that caused a defect, but only by quoting it verbatim, and a validator greps
the quote. Every piece worked. The grammar refused malformed values, the
quote check read committed content rather than the worktree, the two-stage
matcher handled this repo's hard-wrapped prose, and adversarial review could
not break the security surface. Six tasks shipped and the branch looked done.

Asked whether the mechanism actually addressed the problem, two independent
reviews walked the chain from "a wrong sentence lands in a plan" to "someone
computes a ratio and concludes something", and found it could not:

- **It only ever ran on the rounds that found nothing serious.** The
  `NEEDS_REVISION` path returns before quote verification, and the
  aggregation rule sends every 🔴 there. Measured: **0 of 24** severity-🔴
  findings ever reached it.
- **It never collected.** The only machine-readable output was a marker file
  the next run overwrote, and the human record lived in transcripts that age
  out in a month.
- **The bias ran toward the kill condition.** A pre-registered, deliberately
  uneditable stop rule read an all-`none` result as "delete the field" — and
  the sampling rule guaranteed all-`none` for reasons unrelated to whether
  planning documents cause defects. A null result would have been the
  sampling rule restating itself.

**Why:** correctness of each link says nothing about the survival rate of the
signal across the chain, and nothing at all about whether what survives is
biased. Reviews grade artifacts; nobody was grading the chain. Every per-task
reviewer saw a correct slice, and the whole-branch reviewer saw a correct
branch — the defect was in the space between the mechanism and the judgment
it was built to enable, which is not any single artifact.

**How to apply.** Before shipping a measurement mechanism, write the chain
from the event to the conclusion, one link per line, and mark each with what
fraction survives and whether the loss is random or correlated with the
answer. Two questions carry most of the weight: *which population does this
sample from, and is it the population the conclusion is about?* and *where
does the datum persist between being produced and being counted?* Here the
answers were "the cheap half" and "nowhere", and both were invisible until
the chain was written down. The re-cut that followed moved the value from a
mint-time refusal to a durable append-only ledger written on every round —
enforcement was never the binding constraint, persistence was.

A pre-registered stop rule sharpens this: it is legitimate to fix the start
condition only while no data has landed, so the chain audit has to happen
before the first real use, not after the first surprising number. See
[[a-tool-behaviour-measured-in-one-repo-state-is-not-a-general-fact]] for the
sibling failure inside a single link, and
[[convergence-is-not-evidence-when-the-sample-is-shared]] for the same
population question asked of agreement rather than of counts.
