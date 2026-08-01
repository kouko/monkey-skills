---
name: 2026-07-26-investing-toolkit-spine-chain-misses-33-filer-years-of-reported-history
description: investing-toolkit — spine chain misses 33 filer-years of reported history
status: CLOSED — SUPERSEDED
---

  - **What this does NOT cover, stated so the closure is not oversold.** The
    reconstruction is a SECOND entry point; `derive_spine` over the store dump
    still resolves `SPINE_FIELD_CHAINS` and still starts those five filers'
    revenue late. And only `revenue` moved — the other 13 fields resolve by
    chain on both paths (`kpi_spine_view.py`, the disposition block above
    `SPINE_FIELD_CHAINS`), so `net_income`'s 6 TGT filer-years below are
    untouched by the brief.
  - **Kept rather than deleted**, against this file's "completed items are
    deleted" convention: the brief REQUIRES a pointer here, and a deleted entry
    carries none — a future reader who greps for the synonym fix must land on
    the reconstruction rather than on nothing. The measured table below is also
    the artifact the entry was filed to preserve.
- Originally filed 2026-07-26 from the post-PR end-to-end coverage audit of
  PR #619 (branch `feat-us-as-reported-statement-lane`, 2.38.0).
- **What.** The spine chains omit concepts that filers really used, so a field
  starts late rather than showing a hole. Measured over the arc's own 47-filer
  corpus, duration-filtered to annual 10-K rows:

  | field | filers affected | filer-years lost | who |
  |---|---|---|---|
  | `revenue` | 5 / 46 | **27** | KO 2007-2015 (9y), JNJ 2007-2015 (9y), MRK 2011-2015 (5y), AMD 2008-2009 (2y), PFE 2014-2015 (2y) |
  | `net_income` | 1 / 46 | **6** | TGT 2013-2019 |
  | `operating_income`, `capex` | 0 / 46 | 0 | — |

  41 of 46 filers have complete revenue coverage. The dominant cause is one
  missing synonym: those filers tagged early-era revenue
  `SalesRevenueGoodsNet`, and the chain lists only `SalesRevenueNet`.
- **Why it hid.** A missing chain concept does not create a GAP — the field's
  span simply starts later, so a mid-series-hole check (which this arc ran, and
  which found zero holes across five filers) cannot see it. It is only visible
  by comparing the years the CHAIN can serve against the years the filer
  reported the same line under ANY concept. That comparison is the artifact
  this entry exists to preserve.
- **Why it was NOT fixed in the shipping branch.** The chains are the source of
  the store's series identity, so widening one is a durable decision, and the
  candidate list used to MEASURE the gap was hand-picked rather than measured —
  it proves those six filers used those tags, not that adding the tags is safe
  for the other 41. Adding a concept that turns out to mean something narrower
  (a segment, a product line, a net-of-something variant) would write wrong
  values into an append-only store, which is strictly worse than the current
  honest short series.
- **The evidence bar, retained but no longer a work item.** Widening the chains
  is superseded on the as-filed path and NOT recommended on the store path; if
  anyone widens one anyway, this is still the bar it has to clear, in order:
  1. For each candidate concept, check on the filers that DO have full coverage
     whether the candidate is also present and, if so, whether it agrees with
     the chain's own value for the same period. A candidate that disagrees
     anywhere is a different line, not a synonym.
  2. Confirm the candidate is the WHOLE-COMPANY line, not a dimensional or
     segment slice — `companyfacts` carries only default-axis facts, which
     helps, but a filer can still tag a narrower total.
  3. Only then widen, and re-run the coverage audit to confirm the 33 years
     land and nothing else moves.
- **Verification artifact to reuse**: the audit itself
  (`e2e_coverage.py` / `chain_coverage.py` shapes from that session) — coverage
  matrix + independent value check against the `companyconcept` endpoint, which
  is a different API path from the `companyfacts` the lane reads. Note the
  duration filter is load-bearing in both: a 10-K also tags quarterly rows, and
  counting them makes a quarter masquerade as a fiscal year (this bit the audit
  itself once — JNJ FY2009, a 97-day row compared against the annual figure).
- Re-trigger: NONE for the fix — it is superseded. Re-read this entry only if
  the STORE path's short revenue series is reported as a defect (the
  reconstruction does not serve `kpi_store dump | kpi_spine_view derive`), or
  if `net_income`'s 6 TGT filer-years surface, which no shipped change covers.
