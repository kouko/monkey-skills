---
name: changing-what-a-token-is-defeats-downstream-guards
description: Changing a shared primitive's SHAPE (what counts as a token, a record, an id) silently defeats every guard written against the old shape — and the per-task review triad is structurally blind to it, because the task that CHANGED the shape never reads the guard, and the guard's own task was reviewed against the old shape.
type: practice
origin: branch feat-prose-kpi-part-2 (2026-07-20) — one task's change to token shape defeated two separate guards shipped in the prior part; only whole-branch review saw it
---

Part 2's Task 1 made the number locator absorb a trailing magnitude word,
so `"3.56 billion"` became ONE token instead of `"3.56"`. Correct in
itself, fully reviewed, tests green. It then silently defeated two guards
shipped in Part 1:

- **the period-label filter** gated on `_YEAR_RE.fullmatch(token)`. A year
  followed by a magnitude word no longer fullmatches, so
  `"fiscal 2026 billion-dollar program"` sailed through as
  2,026,000,000,000 — the filter existed *specifically* to stop that.
- **the block separator**: the surface walker inserts `\n` at block
  boundaries to stop cross-block fusion (its comment says exactly that).
  The absorption pattern's `\s+` matched that `\n`, fusing text across
  block boundaries and even across an excised table.

**Why the triad could not catch it.** Task 1's reviewers read Task 1 —
they had no reason to open the period filter. The period filter's own
reviewers read it against the *pre-change* token shape, where it was
correct. Neither review was wrong; the defect lives in the **seam**, and
per-task review has no seam lens. The whole-branch reviewer found all of
them, and after being told "assume there is another and look again" found
two more.

**How to apply:**

1. When a task changes a shared primitive's shape, treat "what was written
   against the old shape?" as a required search, not an afterthought —
   grep every consumer of that primitive and re-read each one's guard
   against the NEW shape. Enumerate the blast radius in the task report.
2. Prefer guards that are robust to shape change (strip the new affix
   before testing) over guards that assume a shape, even when the shape
   fix alone would close today's bug. Defense in depth here is cheap: the
   next shape change is coming.
3. Ask the whole-branch reviewer explicitly to hunt the seam, and when it
   finds one, **assume there is another** — that instruction alone turned
   up instances 3 through 6 on this branch.
4. A structural pin is worth more than the guards: a lockstep test across
   the two constant tables that could not import each other (subprocess
   boundary) is what kept the magnitude vocabulary from drifting.

Related: [[construction-guaranteed-invariant-proves-nothing]] (what these
defects all looked like once shipped),
[[per-task-review-misses-duplicated-fallback-fix]] (the same per-task
blind spot in a different shape).
