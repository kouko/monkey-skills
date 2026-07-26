---
name: a-shared-helper-can-be-right-in-one-lane-and-destructive-in-another
description: Reusing a helper across two lanes copies its SEMANTICS, not just its code — a resolver that correctly fails loud on ambiguity in a lane that must emit ONE answer silently destroys data in a lane that stores every alternative separately. The reuse instruction came from the plan, both lanes' own tests passed, and the loss was only visible by running the real producer against a filer that reports two legitimate alternatives.
type: gotcha
origin: US as-reported statement lane (feat-us-as-reported-statement-lane, investing-toolkit 2.38.0, 2026-07-26) — found simultaneously by the live dogfood and the whole-branch reviewer, from opposite ends
---

`_resolve_concept_per_period` was written for the top-line revenue lane,
where the job is to emit THE company's single total: when two concepts of
one chain disagree on a period, guessing would ship a wrong headline, so it
skips the period under both and names the reason. That is correct there and
was reviewed as correct.

The statement lane then reused it — because the plan said to, on the
reasoning that a per-period merge helper is a per-period merge helper. But
that lane's entire thesis is the opposite: it stores every concept under its
own id precisely so nothing is chosen at write time, and the read-side view
resolves per period. In a lane that stores alternatives, "these two
disagree" is not ambiguity to refuse — it is the normal case.

The damage was silent and large:

- Walmart lost revenue, net income and EPS entirely. It tags both a total
  revenue and a contract-revenue-only figure, which are DIFFERENT MEASURES
  and are supposed to differ.
- 17 of 42 filers lost total equity, because the two equity subtotals
  (parent-only vs including non-controlling interest) differ by definition
  whenever an NCI exists. Losing equity also made the branch's balance-sheet
  identity check unreachable in production — the code path its own reviews
  had called "the majority case, not an edge case".

**Why nothing caught it.** Both lanes' unit tests passed: the top-line
lane's conflict tests exercise the rule where skipping is right, and the
statement lane's tests fed hand-built payloads carrying both concepts — an
input its own producer could no longer emit. Ten per-task reviews could not
see it because each task's slice was internally consistent. It took the
whole-branch reviewer (reading the two callers against each other) and a live
run against a filer that actually reports both alternatives, and they landed
on it independently the same afternoon.

**How to apply:** before routing a second caller through a shared helper, ask
what the helper's failure mode MEANS in the new lane, not whether its
signature fits. A helper that refuses on ambiguity belongs only where
ambiguity is genuinely unresolvable at that layer; if the new caller stores
alternatives rather than choosing between them, refusing is data loss wearing
the costume of caution. Two questions separate the cases: does this caller
have to emit exactly one answer? and can the disagreement it sees be
legitimate rather than contradictory? A "no" to the first or a "yes" to the
second means do not reuse. When you do decline the reuse, say so at the
helper — this arc's fix added an explicit "only `build_top_line_backfill` may
call this, and why" line, because the next reader will otherwise re-derive the
same tempting mistake.

Complements [[unifying-a-normalization-has-a-scope]], which is the mirror
failure: there a shared helper did not reach far enough, here it reached into
a lane whose semantics inverted it. Both say the same thing about extraction —
the boundary of a shared rule is a claim you have to earn per call site, not a
property of the function. Related: [[a-data-probe-is-not-a-pipeline-dogfood]]
(the run that surfaced it) and [[per-task-review-misses-duplicated-fallback-fix]]
(the review layer that structurally cannot).
