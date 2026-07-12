---
name: assertion-must-encode-the-property-it-claims
description: A guard whose docstring claims an ORDERING/relational property but whose assertion only tests membership ("before" in text and "candidate round" in text) is vacuous — it passes on the violated state; read each guard's own claim and ask "would this fail if the claimed property broke?"
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
