---
name: 2026-08-31-batch-eligibility-should-push-toward-batching
description: Review Batch eligibility only refuses, never nudges — make the planner pay for NOT batching homogeneous tasks, via three escalating knobs (reverse check, default flip, mechanical criterion) evaluated in that order with observed dispatch counts
status: open
origin: 2026-08-31 — kouko, reading the batch-review-hardening plan (one 2-member batch out of 7 tasks) asked whether the loom mechanism itself was the cause; the orchestrator's assessment — enforcement is one-directional, so plans drift toward individual review — became this entry
start: event — F10 (docs/loom/backlog/2026-08-31-batch-cost-numbers-are-declared-not-observed.md) ships harness-emitted dispatch counts, so a change in batching behaviour can be measured rather than declared
---

Task Batch Review (#766) made eligibility fail-closed: same lane, one
end-to-end verdict question, one closable window, and "any doubt →
individual". Every check that exists runs in the refusing direction —
`check_review_batches.py` and plan-document-reviewer Check 22 can reject a
batch, but nothing anywhere says "these tasks could have been one batch and
you did not say why". The "one verdict question" test is a judgement call
with no mechanical proxy, so a planner with any doubt splits, and no plan
header records how many fan-outs it chose to spend. The observed result on
2026-08-31: the hardening plan batched T1+T2 and left T3 (same file, same
lane, same safety claim) and T5 (same claim, different module) individual —
seven tasks, six fan-outs — on risk aversion, not on any rule.

The cost of batching is real and should stay in view: batch members get no
per-task reviewer, only mechanical verification and one aggregate review, so
larger batches mean later feedback. Reopen is owner-scoped, which caps that
cost lower than the rule's caution implies. And the saving batches buy is
the final review layer only; pre-batch revision rounds run either way, so
an arc whose cost is mostly revision will not save much however it batches.

Three knobs, lightest first, to be evaluated in order and not all at once:

1. **Reverse check** — plan-document-reviewer gains a check: tasks that
   share a review lane, are adjacent in the dependency DAG, and have
   overlapping `Files touched` but different dispositions must carry a
   written "not batched because" line; absent line → NEEDS_REVISION. The
   plan header records `review fan-outs: N of M tasks`. No execution-time
   rule changes; "adjacent" and "overlapping" need mechanical definitions
   so the check does not become a second judgement call.
2. **Default flip** — writing-plans' second pass starts from candidate
   clusters (lane × module × dependency chain) and excludes members, rather
   than starting from all-individual and admitting members. Same eligibility
   rule, different starting point; only useful with knob 1 in place, or the
   planner can still dissolve every cluster silently.
3. **Mechanical criterion** — replace "one verdict question" with a
   computable proxy: same lane ∧ dependency-connected ∧ file sets intersect
   or share a directory ∧ no user-decision / external-wait marker ⇒
   eligible. Removes the judgement entirely but will over-merge semantically
   unrelated same-file tasks and degrade aggregate review quality; only
   justified if knobs 1–2 measurably fail to move the fan-out count.

Sequence: knob 1 → F10 lands → measure two or three arcs → decide on 2, then
3. Without observed counts none of the three can be shown to have saved
anything, which is exactly the trap the 2026-08-31 pilot's declared 10→2
fell into.
