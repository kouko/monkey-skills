---
name: 2026-07-31-institutionalise-the-implementer-s-refusal-to-work
description: Institutionalise the implementer's refusal to work
status: OPEN
origin: `docs/loom/audits/2026-07-31-a-class-interceptability-backtest.md` §候選 6, proposed there and left unadjudicated.
start: after the `Reuse-adequacy` arc closes, or the next time an implementer returns `NEEDS_CONTEXT` / `BLOCKED` on a plan-fact defect and the refusal reads as a judgment call rather than a contract obligation.
---

- Start: after the `Reuse-adequacy` arc closes, or the next time an implementer
  returns `NEEDS_CONTEXT` / `BLOCKED` on a plan-fact defect and the refusal reads
  as a judgment call rather than a contract obligation.
- Origin: `docs/loom/audits/2026-07-31-a-class-interceptability-backtest.md`
  §候選 6, proposed there and left unadjudicated.
- What: 5 of the 9 plan-layer fact problems in that backtest were stopped by an
  implementer declining to proceed — at the cheapest point, before execution —
  and its reach was **wider** than the PIN-cross-read candidate: it also caught a
  design gap, which cross-reading a source cannot see, because the refusal is not
  "these disagree" but "I cannot build from this". `NEEDS_CONTEXT` / `BLOCKED`
  already exist in the SDD contract; **what should trigger a refusal does not**.
- Read the selection effect before costing it: those 5 are in the record
  *because* refusal surfaced them. Cases refusal missed leave no
  "refusal case" trace, so the backtest has no denominator and does not claim a
  hit rate.
- Needs a design round plus cross-tier behavioural validation (will a weak tier
  fail to refuse when it should?) — the same 2×2 shape as
  `docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md`.
- Overlap note: candidate 6 and candidate 1 are substitutes on 4 of those 5
  cases; candidate 6 and the `Reuse-adequacy` work do **not** overlap.
