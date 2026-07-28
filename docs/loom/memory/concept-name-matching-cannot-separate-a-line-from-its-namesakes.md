---
name: concept-name-matching-cannot-separate-a-line-from-its-namesakes
description: Finding a financial line by matching CONCEPT NAMES returns the line's namesakes too — a case-insensitive `revenue|sales` sweep over 46 filers' companyfacts ranked CostOfRevenue (18 filers / 784 rows), DeferredRevenueCurrent and available-for-sale-securities concepts above the one genuine candidate, and reported 42 of 46 filers as carrying an unlisted revenue-shaped concept when the filers with any real gap number between 2 and 4 (two sweeps disagreed; the low figure is the one that favoured abandoning the fix); worse, a name cannot tell a filer's TOTAL from its COMPONENT, because the same concept is the total for one filer and a component for another
type: gotcha
origin: 2026-07-28 revenue chain-membership audit, offline over the local companyfacts cache — the sweep that killed a planned chain-widening fix; full measurement in docs/loom/audits/2026-07-28-revenue-chain-and-hierarchy-audit.md §2
---

Asked "which revenue concepts is our fetch list missing?", the honest method is a
name pattern over every concept the filer actually carries — precisely because a
hand-picked list reproduces the omission that caused the gap. That method works,
and its output is mostly garbage:

- `CostOfRevenue` — 18 filers, 784 10-K rows. Name matches; it is the opposite
  side of the income statement.
- `DeferredRevenueCurrent`, `RevenueRemainingPerformanceObligation`,
  `ContractWithCustomerLiabilityRevenueRecognized` — liabilities and disclosures.
- A large class of available-for-sale-securities balance-sheet, OCI and cash-flow
  concepts, dominating the ranked table by both filer count and row count.

Read as a headline, "42 of 46 filers carry an unlisted revenue-family concept"
says the coverage hole is everywhere. Measured properly the number is **between
two and four** — the span-growth sweep found 2 (KO, AMD), the components-only
sweep found 4 (adding MRK and PFE), the two were never reconciled and the raw
output is gone. The count is not wrong; it answers a different question than the
one it appears to answer. **Cite the range, not the low end**: the low figure is
the one that supported abandoning the fix, so quoting it alone reproduces the
bias. Full measurement and the unreconciled note:
`docs/loom/audits/2026-07-28-revenue-chain-and-hierarchy-audit.md` §2-§3.

The sharper half is not noise at all. `SalesRevenueGoodsNet` is a legitimate
revenue line — and it is KO's TOTAL revenue (a beverage filer) while being a
COMPONENT for AMZN, CSCO, BA, GE, HON, IBM, ORCL, MSFT, TSLA, VZ and UNH, which
report goods and services separately under a separate total. **No property of the
name distinguishes those two cases**, and neither does magnitude — one filer's
component exceeds another's total.

**Why:** the relation "this line rolls up into that one" lives in the filing's
calculation linkbase, not in the concept name. SEC's `companyfacts` aggregate
drops that linkbase, so a pipeline reading it has names and numbers and no
structure — every discriminator it can build is therefore a proxy, and each proxy
fails on a different filer. Summing components instead of naming them does not
rescue it: measured over 148 filer-years where both a total and its components
exist, the identity held exactly 61 times, within 0.5% never, and the SAME FILER
flips between holding and failing across adjacent years.

**How to apply:** use a name sweep to DISCOVER candidates, never to DECIDE. The
decision needs the filer's own declared hierarchy — read it from the filing
(presentation/calculation linkbases), not from the flattened aggregate; if the
lane cannot reach the hierarchy, the honest output is a named unresolved
candidate, not a value. And when reporting a name-derived count, state what it
excludes before stating the number, or it will be read as a measurement of the
thing it merely resembles.

Bounds [[same-economic-fact-different-concept-string-needs-first-present-fallback]]:
a first-present candidate list is right when the candidates are SYNONYMS for one
economic item, and wrong when they are DIFFERENT MEASURES — total vs component is
the second case, and first-present silently hands a component the total's slot in
any period the total is absent. Ask which of the two you have before reaching for
that pattern. Sibling from the same sweep:
[[latest-filed-row-is-not-a-safe-tiebreak]].
