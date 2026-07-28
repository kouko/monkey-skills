---
name: aggregate-fp-rate-across-checks-with-different-grammars-misleads
description: Gating a tool on ONE false-positive rate aggregated across checks with different grammars produces verdicts that move opposite to quality — fixing one check's entire FP class RAISED the aggregate from 79.7% to 96.8% because the denominator shrank faster than the numerator, and a later round's "improvement" to 0% was actually descoping the noisy check, not fixing anything. Split the measurement per check BEFORE comparing anything to a threshold; a reversal condition written against an aggregate can trip on strict improvements and stay silent on real regressions.
type: gotcha
origin: feat-docs-citation-check-review-mode (loom-code 0.40.0), citation-checker corpus rounds 1-4 — docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md
---

A citation checker carried two checks with different grammars — `path:line`
bounds resolution and `§N` heading anchors — and its brief's reversal condition
was written against one aggregate false-positive rate (~10%). Across four
measured corpus rounds the aggregate moved 79.7% → 96.8% → 33.3% → 0%, and at
every step the aggregate told the wrong story:

- Round 2 **eliminated an entire FP class** (629 findings → 0, structurally
  impossible afterwards) and the aggregate **rose** to 96.8% — the fix shrank
  the denominator faster than the numerator, because the untouched sibling
  check now dominated a smaller findings set.
- Round 4's fall to 0% was not a fix at all — it was **descoping** the sibling
  check behind an opt-in flag. Per-check, the shipped check had already been
  at 0% since round 2.

**Why:** checks with different grammars have independent FP populations. An
aggregate couples them through the denominator, so any scope change in one
check masquerades as a quality change in the other. A threshold gate written
against the aggregate then fires on strict improvements (round 2) and can stay
silent while a genuinely noisy check hides inside a large clean sibling.

**How to apply:** when a tool carries more than one check, measure and gate
each check against the threshold **separately**, and write the brief's
reversal condition per check — "FP above X% for any single check" — never
against the pooled rate. When reporting a trajectory across rounds, state per
round which checks the denominator includes; a series whose population
changes mid-stream is two series wearing one arrow. Same failure shape at the
data layer: [[doc-wide-concept-sum-conflates-sibling-tables]] (pooling
suppresses the structure that carries the answer). On honest scope changes,
say "descoped", not "fixed" — the distinction is what lets the next reader
trust the 0%.
