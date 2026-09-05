---
name: a-failed-call-is-a-non-observation-not-a-wrong-answer
description: A measurement that scores model answers must carry each run's status next to its body and score only runs that produced an answer; a failed or timed-out call folded into the scored set adds a wrong answer on every item at once, which is exactly the shape a "systematic error" threshold fires on, so infrastructure failure reads as a finding about the contract
type: practice
origin: 2026-09-04-adversary-three-way-attribution-measured — wave-end:1 rounds 1–3 and the third-round design re-look (2026-09-05)
---

The cold-read runner first recorded a non-zero exit as status `ok`; the
first fix marked it `error` but still appended the body to the list
`score()` received, so an authentication failure counted as one run
where every item was `unparsed`, that is, wrong. With the plan's rule
"an item wrong in ≥50% of runs with the same wrong label is systematic",
five failed calls out of ten would have flagged all eight items as
systematic and sent the change down the rewrite-the-wording arm. Two
readers disagreed on whether the first fix was enough; the third-round
design re-look named the shape defect: `score()` took `list[str]` with no
status channel.

**Why:** a threshold over a distribution is only as good as the
population it is computed on. A non-observation is not a bad
observation; letting it into the denominator and the numerator turns
an operational failure into a claim about the thing measured.

**How to apply:** give every run a status (`ok`, `resumed`, `error`,
`timeout`), pass only the observed ones to the scorer, report `n` as the
scored count next to `attempted_runs` and `failed_runs`, write
`complete: false` and exit non-zero when any run failed so a partial
batch cannot be committed by a green command, and never resume a
transcript whose status is not `ok`. The adversary-checkable invariant:
injecting one failing run into a batch changes only the status fields
and the exit code, never a scored number. Related:
[[a-prompt-that-may-start-with-a-dash-goes-on-stdin]],
[[one-sample-cannot-tell-wording-bias-from-sampling-noise]].
