---
name: grep-the-implementation-before-ranking-a-remediation-candidate
description: A list of unadjudicated remediation candidates goes stale the moment any later arc ships one of them, and nothing in the list announces that — so re-verify each candidate against the implementation before ranking, costing, or recommending it; ranking an already-built mechanism is indistinguishable from ranking an open one until someone greps
type: process
origin: 2026-08-03, completing the §8 candidate backtest (`docs/loom/audits/2026-08-03-remediation-candidate-status-and-live-population.md`) — three of six candidates had shipped while two downstream documents still ranked them as open options
---

An audit that ends in a list of unadjudicated remediation candidates is a snapshot,
not a standing menu. The next arc can ship any of them, and when it does,
**nothing edits the list** — the candidate table keeps reading as open.
Two downstream documents ranked, costed and recommended candidates that had
already shipped, one of them four days after the fact, because both asked
"which candidate would catch which defect" and neither asked "is this
candidate already built".

The failure is silent in the worst way: a ranking of built mechanisms is
formally identical to a ranking of open ones. Nothing in the output looks
wrong. The only detector is opening the implementation.

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
