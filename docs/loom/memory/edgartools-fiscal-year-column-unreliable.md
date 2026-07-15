---
name: edgartools-fiscal-year-column-unreliable
description: edgartools' facts dataframe `fiscal_year` column mislabels prior-year comparatives — derive the fiscal period from `period_end`, never that column
type: gotcha
origin: operational-kpi tier-② XBRL pilot (feat-operational-kpi-xbrl-pilot, 2026-07-15)
---

The `fiscal_year` column of edgartools' `xbrl().facts.to_dataframe()`
is NOT reliably the fact's own fiscal year for prior-year comparatives
inside a single filing. In Apple's FY2025 10-K, the iPhone-revenue fact
whose `period_end` is `2024-09-28` (Apple FY2024) is column-labeled
`fiscal_year=2025`; a fact ending `2023-09-30` showed `2024`. Trusting
that column tags every prior-year point with the WRONG year — silently
corrupting any multi-year trend (FY2024 revenue would appear under
"2025", and the real 2024 slot would be missing/duplicated).

**Why:** a 10-K carries ~3 comparative years; the raw `fiscal_year`
column appears to track the filing's document-fiscal-year focus (or an
off-by-one artifact), not each fact's own period. It is the year the
value gets MISLABELED to, and nothing errors — the numbers are right,
the years are wrong.

**How to apply:** derive the fiscal period from `period_end` — the year
the fiscal period ENDS (`period_end[:4]` for a Sept fiscal-year end like
Apple), validated (e.g. `datetime.date.fromisoformat`), and FAIL LOUD on
a missing/malformed `period_end` rather than emitting a null/None-dated
fact. Never read the raw `fiscal_year` column for period labeling.
(Caveat: `period_end[:4]` equals the fiscal-year label only when the
fiscal year is named for its END year — true for Apple/most US filers;
a company whose FY is named for its START year needs a fiscal-calendar
map, a later concern.) Relates to
[[hand-authored-fixture-is-a-fabrication-risk]].
