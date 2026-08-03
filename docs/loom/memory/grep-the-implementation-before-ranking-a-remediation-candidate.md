---
name: grep-the-implementation-before-ranking-a-remediation-candidate
description: A list of unadjudicated remediation candidates goes stale the moment any later arc ships one of them, and nothing in the list announces that — so re-verify each candidate against the implementation before ranking, costing, or recommending it; ranking an already-built mechanism is indistinguishable from ranking an open one until someone greps
type: process
origin: 2026-08-03, completing the §8 candidate backtest (`docs/loom/audits/2026-08-03-remediation-candidate-status-and-live-population.md`) — the ranking pass was handed four candidates to evaluate and found two of them already shipped
---

An audit that ends in a list of unadjudicated remediation candidates is a
snapshot, not a standing menu. The next arc can ship any of them, and when it
does, **nothing edits the list** — the candidate table keeps reading as open.

The instance: the 2026-08-03 pass was asked to evaluate four still-open
candidates and discovered that **two of them had shipped days earlier**, in the
release that landed immediately after the source audit was written. It found
this only because it opened the implementation; every input it was given —
the audit's §8 table, the prior backtest, the task framing — presented them as
live options. The prior backtest (2026-07-31) shows the softer form of the same
miss: it evaluated a candidate whose rule half had already shipped and never
noted the fact.

**What this is NOT** (the first draft of this entry claimed it, and a reviewer
falsified it): it is not that earlier documents *recommended* things already
built. The audit's §8 predates every ship, so it could not have. The 07-31
backtest's headline recommendation was for a candidate that was genuinely open
and that its recommendation then caused to ship
(`docs/loom/backlog/2026-07-27-reuse-adequacy-got-the-gate-it-had-been-missing.md`
credits that backtest as the retarget). The defect is narrower and duller than
the story: **a ranking pass consumed a stale list without checking.**

The failure is silent in the worst way: a ranking of built mechanisms is
formally identical to a ranking of open ones. Nothing in the output looks
wrong. The only detector is opening the implementation.

Dates here are deliberately relative ("days earlier"), not absolute: the
release in question is dated 2026-07-28 by its commit and 2026-07-27 by its
CHANGELOG heading, and nothing in this lesson turns on which is right.

**Why:** the cost of the check is one grep per candidate; the cost of
skipping it is an entire prioritisation round spent on work that exists,
plus the opportunity cost of the genuinely open candidates that ranking
never reached. This generalises the standing "grep the implementation
before claiming a feature is missing" habit to its mirror image — claiming
an *option* is still open is the same unverified assertion, and lists of
options are the surface where nobody thinks to check.

**How to apply:**

1. Before ranking, costing or recommending any candidate from a prior
   audit's list, grep the implementation for each candidate's prescription.
   Record the status per candidate — shipped / partial / open — with the
   file that proves it, in the ranking document itself.
2. A candidate found shipped is not simply deleted from the list. Check
   whether it actually covers the case it was proposed for: shipped ≠
   effective, and the gap between them is a finding.
3. When the re-grep shows an entry's *cited proof* has moved while its
   *conclusion* still holds — a row count, a pinned constant, a line
   number offered as evidence — correct the proof and the conclusion in
   the same edit. Fixing only the stale number leaves a live conclusion
   propped on a citation that no longer supports it; fixing only the
   conclusion leaves the wrong number for the next reader to act on.
   See [[enumerate-every-copy-before-editing-a-claim-and-name-the-leaks]]
   for the sweep that finds the other copies of the same claim.
