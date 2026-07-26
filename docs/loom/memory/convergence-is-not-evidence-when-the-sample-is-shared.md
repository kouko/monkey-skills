---
name: convergence-is-not-evidence-when-the-sample-is-shared
description: Two independent implementers reaching the same rule is NOT evidence the rule is right when both read the same sample — the agreement measures the sample, not the world; a sign-based filter converged on by two tasks was wrong for every oil major and survived two review rounds precisely because the convergence read as corroboration
type: gotcha
origin: branch feat-spine-chain-coverage (as-filed statement reconstruction, 2026-07-26) — the sign-vs-balance revenue filter
---

Two tasks independently needed to exclude cost concepts from the set of
candidate revenue totals. Both reached the same rule: exclude a line whose
declared WEIGHT is negative. The orchestrator relayed that convergence to a
reviewer as "a side-proof that the rule is right", and it survived two rounds of
review on that footing.

It was wrong for an entire industry. `us-gaap_CostOfRevenue` rolling
**positively** into its own cost subtotal — the refiner layout, which every oil
major uses — is not excluded by weight at all. The sign only works where the
cost is subtracted directly from revenue, which is what IBM does. Both
implementers had the same two filings in the committed capture, one of which was
IBM; neither had a refiner. **The convergence measured the sample.**

What exposed it was not review and not the convergence being questioned. An
implementer building a fixture for an unrelated pin constructed a refiner-shaped
statement, and it failed for a reason it did not expect — a false INCLUSION.

The fix needed a second, independent signal: the taxonomy's own `balance`
(credit/debit). Mutations then proved neither filter is redundant — dropping
`balance` kills the refiner case, dropping the sign kills the case whose cost
line carries no balance at all (349 of 455 captured rows carry none).

**Why:** independent agreement is only evidence when the inputs are independent.
Two agents reading one corpus are one observation reported twice, and the
agreement is strongest exactly where the corpus is thinnest — a shape the corpus
never contains cannot make them disagree. Worse, convergence FEELS like the
strongest possible evidence, so it suppresses the question that would have found
the gap. The orchestrator here wrote "a shared blind spot would be invisible to
convergence" into a review packet and then, one message later, cited the same
convergence as proof.

**How to apply:**

1. Before treating agreement between two implementers as corroboration, ask what
   corpus each read. Same corpus → the agreement is ONE observation. Say so in
   the report rather than counting it twice.
2. A rule derived from a sample must name the sample at its own site, with what
   the sample does NOT contain. "Measured on IBM and KO" is a scope; "measured"
   alone is a claim.
3. Where two signals could each decide a case, keep both and mutate each away
   separately. If dropping one kills no test, it is either redundant or its
   discriminating case is not in the corpus — and those two look identical until
   you construct the missing shape.
4. A stricter rule can destroy the feature. Requiring `balance == credit` would
   have been more precise and would have discarded 349 of 455 rows including
   every filer-custom revenue concept — the exact class the fixed concept chains
   were failing to keep. Check what a tightening EXCLUDES before adopting it.

Related: [[unifying-a-normalization-has-a-scope]] (a claim written wider than
what the code earned — the same failure one layer up, in prose rather than in
sampling) and [[a-data-probe-is-not-a-pipeline-dogfood]] (check the oracle's own
filter before believing its verdict).
