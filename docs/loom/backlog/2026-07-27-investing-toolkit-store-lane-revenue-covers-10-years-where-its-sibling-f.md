---
name: 2026-07-27-investing-toolkit-store-lane-revenue-covers-10-years-where-its-sibling-f
description: investing-toolkit — store-lane revenue covers 10 years where its sibling fields cover 18-20
status: open
origin: post-#621 end-to-end run. `KO` through `statement-backfill → kpi_us_statements_ingest → kpi_store dump → kpi_spine_view derive`: `revenue` covers 2016-2025 (10 years) while **eight** fields cover 2007-2025 (19 years: gross_profit, operating_income, net_income, eps_basic, and the cash-flow trio plus capex), `pretax_income` and `total_assets` cover 2008-2025 (18), and `total_equity`/`cash` reach 2006 (20). `total_liabilities` is absent from KO's store lane entirely. The store holds exactly one revenue-family series for KO, `us-gaap:Revenues`.
start: READY. Smallest end state is a chain-membership audit — for each roster filer, which revenue-family concepts appear in its companyfacts and which of those the chain lists — not a new mechanism.
---

- Origin: post-#621 end-to-end run. `KO` through `statement-backfill →
  kpi_us_statements_ingest → kpi_store dump → kpi_spine_view derive`:
  `revenue` covers 2016-2025 (10 years) while **eight** fields cover 2007-2025
  (19 years: gross_profit, operating_income, net_income, eps_basic, and the
  cash-flow trio plus capex), `pretax_income` and `total_assets` cover
  2008-2025 (18), and `total_equity`/`cash` reach 2006 (20).
  `total_liabilities` is absent from KO's store lane entirely. The store holds
  exactly one revenue-family series for KO, `us-gaap:Revenues`.
- Contrast: `JPM`'s store lane carries TWO revenue-family series
  (`Revenues` 19 years, `RevenuesNetOfInterestExpense` 13) and the view
  resolves 19 — so this is filer-shaped, not a lane-wide cap.
- **Cause, measured** from the cached companyfacts payload
  (`facts_0000021344.json`): KO's 2007-2017 revenue is tagged
  `us-gaap:SalesRevenueGoodsNet` — 27 10-K rows — and that concept is **not a
  member of `_STATEMENT_SPINE_CHAINS["revenue"]`**, which holds exactly five
  entries (`Revenues`, `RevenuesNetOfInterestExpense`,
  `RevenueFromContractWithCustomer{Excluding,Including}AssessedTax`,
  `SalesRevenueNet`). KO carries ZERO rows of the ASC 606 concept, so the
  originally-filed hypothesis — an ASC 606 transition stranding old rows — had
  the right shape and the wrong concept. `coverage.skipped_rows` confirms no
  pre-2016 `Revenues` row was fetched-then-dropped.
- Why it matters: revenue is the first field anyone reads on a trend, and this
  is the lane that otherwise reaches 19-20 years. A 10-year revenue series
  beside a 19-year net-income series reads as a gap in the company, not in the
  tool. Note this is the SAME failure mode PR #620 fixed for the as-filed lane
  (a fixed concept chain cannot see a concept nobody listed) surviving in the
  store lane, which #620 did not touch — and the concept is one #620's own
  brief NAMED: `docs/loom/specs/2026-07-26-as-filed-statement-reconstruction.md`
  lists "pharma/beverage (`SalesRevenueGoodsNet`: MRK, PFE, KO)" among the
  sector-shaped revenue blanks. The as-filed lane stopped depending on the
  chain; the store lane still does, and its chain still does not list the
  concept the brief had already identified for this exact filer.
- Start: READY. Smallest end state is a chain-membership audit — for each
  roster filer, which revenue-family concepts appear in its companyfacts and
  which of those the chain lists — not a new mechanism.
