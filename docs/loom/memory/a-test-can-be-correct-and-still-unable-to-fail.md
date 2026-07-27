---
name: a-test-can-be-correct-and-still-unable-to-fail
description: A test can call the right function, assert the genuinely correct result, and still be PROVABLY incapable of failing — when its inputs land where the mutation is arithmetically inert; two of three table-grid tests exercised the mutated line and asserted correct coordinates while `c + dc` and `c - dc` could not differ on the shapes chosen
type: practice
origin: 2026-07-27 mutation-testing arc (PR #623) — found by mutation, invisible to review-by-reading
---

`_anchor_cells` reserves a cell's span with `occupied.add((r + dr, c + dc))`.
Two tests were written for it and both were green, correct, and useless
against the mutation `c + dc` → `c - dc`:

- **colspan only** — the column pointer advances by `c += cs` regardless of
  `occupied`, so within a single row the reservation is never read;
- **rowspan only** — `dc` takes only the value `0`, and `c + 0 == c - 0`.

Only a cell spanning **both** axes reserves at `dc > 0` in a row that later
consults `occupied`. That third test kills the mutant; the first two cannot,
on any input they were given.

**Why:** this is a distinct failure from
[[assertion-must-encode-the-property-it-claims]] — there, the predicate is
unrelated to the claimed property (membership cannot encode ordering). Here
the predicate is exactly right and the property is exactly right; the
**input space** is the defect. It is also distinct from
[[count-only-regression-pins-false-confidence]], where the pin is merely too
weak. Nothing in reading the test reveals it: the test names the behaviour,
exercises the mutated line, and asserts the true answer. Coverage tools agree
it is covered.

**How to apply:** for any test written to close a KNOWN gap, mutate the
specific behaviour and confirm red — do not infer discriminating power from
the test exercising the line. When a test cannot be made to fail, say so in
the file rather than deleting it: a characterization test is legitimate, but
it must not be filed under the mutant it does not hold. State that at the
section header a scanner reads, not inside the third test's docstring.
Related: [[same-length-mutation-outlives-its-restore-via-pycache]] — a
harness bug can also report a kill that never happened, so the re-run must
be trustworthy before its verdict is.
