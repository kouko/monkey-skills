---
name: sec-companyfacts-frames-api-omits-dimensional-members
description: SEC's companyfacts / frames REST API returns only default-axis (total) facts — dimensional/segment members are not reliably present, so multi-year DIMENSIONAL XBRL history must iterate individual filings, not one API call
type: gotcha
origin: multi-filing historical fetch scope A (feat-multifiling-historical-fetch, investing-toolkit 2.21.0, 2026-07-16)
---

The SEC EDGAR `data.sec.gov` REST APIs (`companyfacts`, `companyconcept`,
`frames`) aggregate a concept's history in ONE call, but they surface only the
DEFAULT-axis facts — the top-level totals. The dimensional breakdown members
(segment / product / geography, i.e. non-default axis members) are NOT reliably
present in those responses ("all numbers coming in are overarching figures",
live-reported). So the tempting single-HTTP-call path CANNOT feed a capability
that keys on the full dimensional signature — it silently loses the very
breakdowns the analysis depends on.

**Why:** the REST aggregation endpoints are built for headline-figure time
series, not for the per-context dimensional facts that live in each filing's
raw XBRL instance. A fact without an explicit axis member carries an implicit
default member; the aggregation keeps those and drops the explicit-member
slices. Nothing errors — you just get totals where you expected segments.

**How to apply:** to build a multi-year series of DIMENSIONAL facts (any
segment/product/geography breakdown), ITERATE the individual filings and parse
each one's XBRL instance (e.g. edgartools `filing.xbrl().facts.to_dataframe()`
per accession), preserving each fact's full `dim_<axis>` signature — do NOT
reach for companyfacts/frames as a shortcut. The per-filing iteration is the
cost of dimensional fidelity; a shared cache amortizes the repeated fetches.
Relates to [[match-kpi-on-full-dimensional-signature-not-one-axis]] and
[[edgartools-fiscal-year-column-unreliable]].
