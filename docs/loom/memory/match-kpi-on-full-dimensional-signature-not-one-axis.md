---
name: match-kpi-on-full-dimensional-signature-not-one-axis
description: An XBRL fact's identity is its FULL dimensional signature (all real breakdown axis:member pairs) — key a KPI by the whole signature, not one axis member, or a cross-dimensioned fact conflates a total with its slices; treat ConsolidationItemsAxis as a separate reconciliation qualifier, never a breakdown
type: gotcha
origin: operational-kpi full-dimensional-signature slice (feat-operational-kpi-xbrl-pilot, 2026-07-15)
---

When extracting a KPI series from XBRL dimensional facts, a fact's identity is
its FULL set of dimension members (concept + every real breakdown axis:member),
NOT a single axis/member. Keying a KPI on one member silently CONFLATES a total
with its cross-dimensioned slices: verified live, Netflix's streaming revenue
fact carries `{ProductOrService: Streaming}` alone = the $45B total, but also
`{ProductOrService: Streaming, StatementGeographical: US&Canada}` = a $20B
regional slice — a single-member "Streaming" match collected the total AND every
region (15 points where 3 were meant). A survey of 23 companies found genuine
cross-dimensioned revenue in ~10 (product×geography, product×segment) — this is
the common case for large diversified filers, not an edge case.

**Why:** the XBRL dimensional model gives each fact identity = concept + its full
context (all axis members). A subset/single-axis match is not a faithful key; it
matches the total AND every fact that merely CONTAINS that member.

**How to apply:** capture each fact's FULL signature (a `dimensions` map of all
real breakdown axes: ProductOrService / StatementBusinessSegments /
StatementGeographical / Subsegments, keyed by axis local name from the per-row
`dim_<namespace>_<axis>` columns) and EXACT-match a binding on it (empty map =
the top-level total; add a member = that exact slice). Treat
`srt:ConsolidationItemsAxis` as a SEPARATE reconciliation qualifier (operating-
segments view vs eliminations), NEVER a breakdown axis — else every segment
company (AAPL/JPM/BAC/WMT…) looks falsely cross-dimensioned. Keep the
anti-fabrication floor: an unmatched signature is skipped, a >1-distinct-value
signature+period RAISES, an identical duplicate dedupes — one value per period or
a loud refusal. Relates to
[[hand-authored-fixture-is-a-fabrication-risk]],
[[edgartools-fiscal-year-column-unreliable]].
