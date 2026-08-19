---
name: assertion-must-encode-the-property-it-claims
description: A guard whose docstring claims an ORDERING/relational property but whose assertion only tests membership ("before" in text and "candidate round" in text) is vacuous — it passes on the violated state; read each guard's own claim and ask "would this fail if the claimed property broke?" — and the relational predicate you add will over-fire on a valid re-rendering, so decide which residual to keep rather than tightening again: a false alarm is loud and cheap, the hole it guards is silent
type: practice
origin: branch feat-visual-anchor-realignment (2026-07-12) — whole-branch review caught a vacuous ordering pin the SDD triad had passed
---

An implementer's guard carried the docstring *"the derivation must be
ordered BEFORE any canon candidate round"* and asserted:

```python
assert "before" in low and "candidate round" in low
```

Both substrings occur in the file **regardless of order**. Reordering the
flow so the anchor came *after* the canon rounds — the exact regression the
guard names — would still pass green. Its sibling guard, written by a
different implementer for the same property in another file, did it right:

```python
anchor_at = flat.index("3-5 tone & manner adjectives")
rounds_at = flat.index("two axis-typed candidate rounds")
assert anchor_at < rounds_at
```

**Why:** this is a distinct failure from
[[count-only-regression-pins-false-confidence]] (there, the pin is too
*weak*; here, the predicate is **unrelated to the claimed property** —
membership cannot encode order). It also survived the per-task triad:
the task's own spec-reviewer and code-quality-reviewer both passed it,
because the assertion *looks* like it tests the docstring. Only the
whole-branch review — reading the guard against its own claim — caught it.

**How to apply:** for every guard, read its docstring/name as a claim, then
ask **"would this assertion FAIL if that exact property were violated?"**
Relational claims (ordering, containment-within-a-block, exclusivity,
co-occurrence) need relational predicates — `index() <` comparison,
block-scoped slicing, or an absence assertion. A membership check
(`x in text`) can only ever encode existence. Cheapest proof: mentally
apply the regression the docstring forbids, and confirm the assertion
goes RED.

Related: [[grep-tests-scope-to-measured-neighborhood]] (scope the pin to
the block that must carry the phrase, not the whole file — the sibling
discipline that makes co-occurrence claims testable).

**Increment (2026-08-01, branch `docs-reuse-adequacy-brief-and-backlog`).** Two
of that branch's four new or amended guard tests over prose contracts shipped
with *this* hole — a relational property (which slot is the report, whether a
pointer sits beside its neighbour) asserted by membership alone. Two more shipped
the sibling failure this entry's body already distinguishes: a missing
absence assertion, where a reintroduced field or a deleted opt-in bullet left
every check green. A first draft of this paragraph called it "six" and merged the
two kinds; a docs review traced it to four and separated them. Adding the relational
predicate closed each one — and opened a new **over-fire** on a valid
re-rendering: a bolded label, a definition-list form, two paragraphs merged into
one, a locale reordering. Tightening again just swings it back.

Over prose the cycle does not converge, because the valid renderings of a
semantic property are unbounded. So the decision is not "tighten until correct"
— it is **which residual to keep**, and the asymmetry answers it: a false alarm
is loud, self-explaining and cheap (someone restyles a doc, CI complains, they
see why), while the hole it guards is silent and is the defect the guard exists
for. Keep the noisy one, record the over-fire as known debt, and stop swinging.

**Increment (2026-08-19, branch `plan-field-microstructure`) — deletion and
reversal are two different probes, and passing the first proves nothing about
the second.** Four assertions on that branch shipped green against a target
that had been deleted or whose claim had been reversed in place. The arc had
already adopted the standard probe — delete the target, confirm the test goes
RED — and every one of the four passed it. They still could not tell a rule
from its opposite: the assertion matched a heading, a filename, or a
surrounding phrase that survives a reversal untouched, so flipping the rule's
content left it green. One of the four was actively pinning a ceiling the same
arc had already overturned, and it kept the stale wording passing while the
rule it claimed to guard no longer existed.

**Why the deletion probe misses this:** deleting a target removes its
container along with its content, so any assertion anchored anywhere near it
goes RED and looks non-vacuous. Reversing the content leaves the container
intact — which is exactly the state a wrong edit produces. A rule is far more
often *changed into something wrong* than *removed*, so the cheaper probe
tests the rarer failure.

**How to apply:** run both mutations, not one. Delete the target → the
assertion must go RED (non-vacuous). Then restore it and **reverse its claim
in place**, keeping its heading, length and surroundings — negate the
proposition, swap the number for a different one, invert the permitted and
forbidden cases — and the assertion must go RED again. A test that survives
the second mutation pins the target's *location*, not its *meaning*, and must
be rewritten to assert the proposition itself.
