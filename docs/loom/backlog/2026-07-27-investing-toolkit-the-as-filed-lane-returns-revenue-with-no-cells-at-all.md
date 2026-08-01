---
name: 2026-07-27-investing-toolkit-the-as-filed-lane-returns-revenue-with-no-cells-at-all
description: investing-toolkit — the as-filed lane returns revenue with no cells at all for banks
status: OPEN
origin: `pack.py --pack reconstruct --ticker JPM` → `kpi_spine_view derive-as-filed`. The `revenue` field comes back with **zero periods** — not one typed cell — while `gross_profit`, `cash` and `capex` in the same payload correctly carry `not_presented`.
start: READY. The roster census this would normally need is already in `post/sweep.jsonl` (the `ambiguous_total` and `revenue_concept: null` counts above came from it), so the open question is only whether to add a cell state or to reuse `not_presented` with a reason.
---

- Origin: `pack.py --pack reconstruct --ticker JPM` →
  `kpi_spine_view derive-as-filed`. The `revenue` field comes back with
  **zero periods** — not one typed cell — while `gross_profit`, `cash` and
  `capex` in the same payload correctly carry `not_presented`.
- The data is present: JPM's income statement DOES carry
  `us-gaap_RevenuesNetOfInterestExpense` labelled "Total net revenue". The
  structural rule declines it because `revenue_totals` finds **three surviving
  candidates** (`InvestmentBankingRevenue`, `PrincipalTransactionsRevenue`,
  `RevenuesNetOfInterestExpense`) and refuses to pick when the count ≠ 1
  (`kpi_spine_view.py:1102-1105`); the payload's `verification` section reports
  `ambiguous_total` ×8. **Declining is correct** (user decision 「甲」,
  2026-07-26: a visible typed gap, never a chain fallback).
- **The calculation tree is NOT the problem** — recorded because the first
  draft of this entry said it was, and that would have sent someone hunting a
  missing linkbase: 195 of 239 income-statement lines across the 8 filings
  carry a `calculation_parent`, and `RevenuesNetOfInterestExpense` is itself
  the declared parent of `NoninterestIncome`.
- The defect is the SHAPE of the decline, and it is narrower than "no typing":
  the payload DOES name the candidates in an `unresolved` key
  (`kpi_spine_view.py:1210-1214`, deliberately — "the typed gap: the candidates
  are named"). What is missing is per-PERIOD typing: a consumer iterating
  `periods` gets an empty dict and must know to look elsewhere, while every
  other empty field hands it `not_presented` in the same loop. A fifth cell
  state, or `not_presented` carrying the reason, would close it.
- Blast radius, measured from `post/sweep.jsonl` rather than assumed — **3 of
  71**, and it is not "the banking sector": `ambiguous_total` fires for 5
  filers (BAC, BX, C, JPM, WFC) but BAC and BX still RESOLVE revenue, so the
  exact defect (unresolved revenue, zero fill, via `ambiguous_total`) is JPM,
  WFC and C. Separately, `revenue_concept: null` covers **8** filers (BLK, C,
  JPM, MO, NOW, PGR, WFC, XOM — 7 excluding XOM, whose null is the
  silent-empty case above rather than a resolution failure), and **four of
  those are non-banks** (MO, NOW, PGR, BLK), so the null-revenue population
  and the bank population are different sets. PR #621 moved JPM/BAC/C from 3
  annual periods to 10 and WFC from 4 to 12.
- The store lane is unaffected: JPM's `revenue` spans 19 years there
  (2007-2025 per `JPM_spine.json`), so this is an as-filed-lane presentation
  gap, not data loss.
- Start: READY. The roster census this would normally need is already in
  `post/sweep.jsonl` (the `ambiguous_total` and `revenue_concept: null`
  counts above came from it), so the open question is only whether to add a
  cell state or to reuse `not_presented` with a reason.
