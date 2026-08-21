---
name: a-number-in-prose-needs-a-test-that-recomputes-it
description: A count written into prose goes stale at the next commit that changes what it counts, and correcting the number just resets the clock — when the repo already ships the function that computes it, pin the number with a test that recomputes it AND reads the document quoting it, failing when the two drift apart; the general rule reviewers converged on is "when a file ships a metric and prose quoting that metric, run the metric"
type: practice
origin: north-star-serves-link / dissolve-direction-layer (2026-08-21) — a backlog entry filed to be an honest debt ledger said "three exempt scripts are leaky by the contract's own metric"; two round-8 reviewers independently imported that metric, ran it, and got fourteen
---

The number was measured, then the same commit widened the metric's
recogniser set, and the number was never re-run. It shipped in three
places: the test file's `EXEMPT` comment, the plan's Decision Log, and the
backlog entry filed specifically to be the honest ledger for that debt.

It was operational, not cosmetic. The entry's `start:` trigger named the
three files it believed leaky, so an arc touching any of the other eleven
would never have woken the debt.

Both reviewers found it the same way, and both said the same thing about
method:

> Seven rounds cited that function; none executed it against its own
> claim. The useful instruction is not "look harder" but **execute every
> number this branch's prose states**.

**Why:** a hand-written count is a snapshot of a computation, stored where
nothing recomputes it. Every edit to what it counts silently invalidates
it, and the document reads exactly as confidently as before. Correcting it
produces a fresh snapshot with the same defect.

**How to apply:** where the computation exists in-repo, import it in a test
and assert the count, with a message naming every document that must move
with it. Go one step further and have the test READ those documents —
`assert str(COUNT) in ledger` catches the case where someone updates the
constant and forgets the prose. Where no computation exists, prefer a
qualitative claim over a quantitative one ("several", "most") rather than a
number nothing maintains. Related:
[[prose-shipped-with-a-mechanism-describes-the-road-not-taken]],
[[a-cap-raised-at-every-touch-is-not-a-cap]].
