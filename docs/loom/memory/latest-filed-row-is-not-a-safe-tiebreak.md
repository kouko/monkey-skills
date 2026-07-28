---
name: latest-filed-row-is-not-a-safe-tiebreak
description: When one (concept, period) carries several filed values, "take the most recently filed" is not a safe tie-break — a tag's MEANING can drift across a filer's filings, so the rows are not always restatements of one fact, and the newest can be the corrupt one; CRM's services-revenue tag for a single period was filed as 181M, then 3,050M (the company TOTAL), then 6,667M, and the newest made components exceed the total by 118%
type: gotcha
origin: 2026-07-28 offline sweep over the local companyfacts cache; found while validating a component-sum rule, not while looking for it. Full measurement in docs/loom/audits/2026-07-28-revenue-chain-and-hierarchy-audit.md §3
---

A bitemporal store keeps every vintage of a fact, and the obvious way to collapse
them for a single-value consumer is "take the row with the newest `filed`". That
rule is safe only under an assumption nobody states: that the several rows are
successive RESTATEMENTS OF THE SAME FACT. They are not always.

Measured on `SalesRevenueServicesNet` for one CRM fiscal period, three filings
carried three values — 181M, then 3,050M, then 6,667M. The middle figure equals
the company's reported TOTAL revenue for that period, so at least one filing used
the services-revenue tag for something other than services revenue. Taking the
newest row and summing the components against the total produced components
exceeding the total by 118%.

A second, cleaner shape from the same sweep: AMD's FY2016/2017 components exceed
the "total" by 1.1-1.4% — here nothing is mistagged, but the total is a
retrospective ASC 606 restatement while the component is the as-originally-filed
figure. Two accounting VINTAGES, not two versions of one number.

**Why:** a tag is a name, and a filer's use of that name is not pinned across
years. Restatement, taxonomy migration, and plain mistagging all produce the same
surface — N rows under one (concept, period) — and only the first of the three
means "the newest is the best". A pipeline that collapses by recency treats all
three identically and cannot report which it just did.

**How to apply:** do not collapse multiple filed rows for one (concept, period)
by recency alone in any path where the value feeds arithmetic (a sum, an
identity, a ratio). Either read every term from ONE pinned vintage — that is
[[a-cross-field-check-over-a-bitemporal-store-must-pin-one-vintage]], the
cross-FIELD twin of this entry, and its rule still stands — or, when collapsing
within a single field is unavoidable, carry a check that the spread across
vintages is plausible and refuse loudly when it is not. A 30x spread is not a
restatement. When a value is used for display only, recency is fine; the failure
is specific to values that enter a computation whose other terms came from
somewhere else.

Relates to [[edgartools-fiscal-year-column-unreliable]] (same family: a field
that looks authoritative per-row and is not) and
[[concept-name-matching-cannot-separate-a-line-from-its-namesakes]] (the sibling
lesson from the same sweep — there the name is wrong across CONCEPTS, here across
FILINGS of one concept).
