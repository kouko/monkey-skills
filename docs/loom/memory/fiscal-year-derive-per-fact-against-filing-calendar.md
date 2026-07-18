---
name: fiscal-year-derive-per-fact-against-filing-calendar
description: a fact's fiscal year comes from its OWN period_end measured against the filing's dei calendar — neither period_end[:4] (calendar year) nor the filing's DocumentFiscalYearFocus stamped on every fact is correct
type: gotcha
origin: operational-kpi scope-B quarterly rebuild (feat-operational-kpi-quarterly, 2026-07-17)
---

Labeling an XBRL dimensional-revenue fact with its fiscal year has TWO
opposite traps, and this session hit BOTH — the second while "fixing"
the first:

1. **`period_end[:4]` is the CALENDAR year, not the fiscal year.**
   Correct for an annual (year-end-dated) fact at a filer whose FY is
   named for its end year. WRONG for a sub-annual (quarter-end-dated)
   fact at any non-December-FYE filer: NVDA FY2026-Q3 ends 2025-10-26,
   so `period_end[:4] = 2025` while the fiscal year is 2026. Live: a
   `form="10-Q", since_year=2026, until_year=2026` request selected 0 of
   the 3 real FY2026 quarters and 1 FY2027 quarter, and every fact was
   labelled `fiscal_year: 2025`. Scope A only fetched 10-Ks (where
   calendar == fiscal by convention), so the defect shipped dormant in
   2.21.0 and only bit when scope B reused the primitive for 10-Qs.

2. **The filing's `dei:DocumentFiscalYearFocus` is ONE value per filing;
   stamping it on every fact mislabels prior-year comparatives.** A 10-K
   (and a 10-Q) carries ~3 comparative years. Verified on AAPL's FY2019
   10-K: its FY2017/FY2018/FY2019 facts all collapse to 2019 under a
   filing-level stamp. This is the SAME trap
   [[edgartools-fiscal-year-column-unreliable]] already documents for the
   raw `fiscal_year` column — and a review remediation re-committed it
   anyway, despite that memory being recalled at session start. A
   documented gotcha is only load-bearing if it is re-applied at the
   moment the fix is written, not just read once.

**Why both are the same shape:** each treats the fiscal year as a
property of the FILING or the CALENDAR, when it is a property of the
individual FACT's period.

**How to apply:** derive each fact's fiscal year from its OWN
`period_end` measured against that filing's fiscal calendar
(`dei:CurrentFiscalYearEndDate`, read per-filing, drifts for 52/53-week
filers so never cache it — see [[edgartools-fiscal-year-column-unreliable]]).
`dei:DocumentFiscalYearFocus`/`DocumentFiscalPeriodFocus` are the
filing's OWN answer for the CURRENT-period fact only (live-verified
90/90 exact across 6 filers, 2026-07-17) and are the right authority for
that one fact; comparatives in the same filing must still be classified
from their own period_end. Fail loud when the calendar cannot be read —
never fall back to the calendar year, which is trap #1.

**Process lesson (the reason this took 3 patch rounds + a branch-review
round):** the calendar-vs-fiscal defect had FOUR call sites (selection,
per-fact label, coverage grouping, coverage projection). Fixing them one
symptom at a time made the identical bug resurface on a sibling path
three rounds running — because the root primitive's docstring still
lied ("the fiscal year a filing REPORTS" over `return int(period[:4])`).
When the same error class survives a fix that should have killed it,
fix the primitive and its contract, not the call site. Relates to
[[hand-authored-fixture-is-a-fabrication-risk]] (a hand-typed MSFT-with-
December-FYE fixture hid trap #1 through a full triad, because December
is the one FYE where calendar-year logic accidentally works).
