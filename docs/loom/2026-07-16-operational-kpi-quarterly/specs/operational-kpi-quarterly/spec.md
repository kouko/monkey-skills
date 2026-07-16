# operational-kpi-quarterly

## ADDED Requirements

### Requirement: Period duration is emitted per fact
The data layer MUST emit each dimensional fact's period DURATION in months (derived from the
XBRL context period_start→period_end span), so the analysis layer can distinguish a
single-quarter fact from a year-to-date cumulative that shares the same period_end.

#### Scenario: 10-Q carries both a 3-month and a YTD context
- GIVEN a Q3 10-Q reporting a concept+dimensions for both "3 months ended 9/30" and "9 months ended 9/30"
- WHEN the data layer extracts its dimensional facts
- THEN it emits TWO facts for that concept+dimensions+period_end, one with duration_months=3 and one with duration_months=9

#### Scenario: annual fact keeps a 12-month duration
- GIVEN a 10-K fact whose context spans 12 months
- WHEN the data layer extracts it
- THEN the emitted fact carries duration_months=12

#### Scenario: instant (balance) context is excluded from the revenue flow
- GIVEN a fact whose XBRL context is an instant (point-in-time, no start date)
- WHEN the data layer extracts revenue (a duration flow)
- THEN the instant fact is excluded from the duration-flow output (not assigned a duration_months)

#### Scenario: missing period_start fails loud
- GIVEN a duration-context fact whose period_start is missing or malformed
- WHEN the data layer attempts to derive duration_months
- THEN it raises a distinct error naming the fact, and never emits a fabricated or defaulted duration

### Requirement: Period type is classified from duration and the fiscal calendar
The analysis layer MUST classify each fact's period_type (Q1/Q2/Q3/Q4/FY) and cumulative flag
from its duration_months and where its period_end falls in the company's fiscal calendar,
deriving the period from period_end (never the edgartools fiscal_year column).

#### Scenario: 3-month fact at a fiscal quarter end
- GIVEN a 3-month fact whose period_end equals the company's fiscal Q1 end
- WHEN it is classified
- THEN its period_type is Q1 and its cumulative flag is false (single-quarter)

#### Scenario: non-December fiscal year end shifts the quarter boundaries
- GIVEN a company with a late-September fiscal-year end and a 3-month fact ending in late December
- WHEN it is classified
- THEN it is Q1 of that fiscal year (quarter boundaries follow the fiscal calendar, not calendar quarters)

#### Scenario: a 9-month fact is a YTD cumulative, not a single quarter
- GIVEN a 9-month fact ending at the fiscal Q3 end
- WHEN it is classified
- THEN its duration_class is 9mo-YTD and its cumulative flag is true (never labeled a single quarter)

#### Scenario: a 6-month fact is an H1 YTD cumulative (critic-found)
- GIVEN a 6-month fact ending at the fiscal Q2 end (every Q2 10-Q carries one)
- WHEN it is classified
- THEN its duration_class is 6mo-YTD and its cumulative flag is true, distinct from any 3-month Q2 single-quarter fact at the same period_end

#### Scenario: a transition or unclassifiable period is surfaced, not guessed
- GIVEN a fact whose duration/period_end does not map to any standard quarter (a stub/transition period)
- WHEN it is classified
- THEN it is flagged unclassifiable and surfaced, and the system does not guess a period_type

### Requirement: The identity key de-conflates single-quarter from year-to-date
The dedup/identity key MUST include the duration class so that a single-quarter fact and a
YTD cumulative fact sharing the same signature and period_end resolve to DISTINCT series
points and are never deduped, conflated, or raised against each other.

#### Scenario: single-quarter and YTD at the same period_end stay distinct
- GIVEN a 3-month fact and a 9-month fact for the same signature ending 9/30
- WHEN resolve_binding keys and dedups them
- THEN they produce two distinct series points and neither triggers the >1-distinct-value RAISE against the other

#### Scenario: the same single quarter reported in two filings dedupes
- GIVEN the same Q3 single-quarter value reported in a 10-Q and again as a comparative in a later 10-Q, identical value, different accession
- WHEN resolve_binding dedups them on the duration-qualified key
- THEN they collapse to one point (scope-A identical-duplicate dedupe, now duration-qualified)

#### Scenario: a restated quarter across filings applies policy C
- GIVEN the same Q3 single-quarter for one signature reported with different values across two filings (a restatement), different accessions
- WHEN resolve_binding resolves the duration-qualified group
- THEN it keeps the most-recently-filed value and emits a restatement DQC flag (scope-A policy C, per the duration-qualified key)

### Requirement: A series carries a single granularity
Series construction MUST keep annual (FY) and quarterly points in separate, granularity-labeled
series, and MUST NOT silently mix a quarterly point into an annual trend.

#### Scenario: a quarterly request returns only sub-annual points
- GIVEN a request for a company's quarterly KPI series
- WHEN the series is built
- THEN it contains only single-quarter (and, if enabled, derived-Q4) points, not FY totals

#### Scenario: mixing granularities is rejected
- GIVEN a set of points containing both FY and single-quarter period_types for the same fiscal year
- WHEN a single-granularity series is requested
- THEN the off-granularity points are excluded (or the mix is rejected), never silently averaged or concatenated

### Requirement: Q4 single-quarter may be derived by subtraction and MUST be flagged [deferred]
The analysis layer MAY derive an untagged Q4 single-quarter as (FY total − 9-month YTD), and
when it does it MUST flag the point as computed (a DQC flag), never presenting a derived value
as directly reported; when the inputs to derive it are absent it MUST skip rather than fabricate.

#### Scenario: Q4 derived when both inputs exist
- GIVEN an FY total and a 9-month YTD for the same signature and fiscal year, and no directly-tagged Q4 3-month fact
- WHEN Q4 derivation runs
- THEN it emits a Q4 point equal to FY minus 9-month YTD, flagged as derived (computed, not reported)

#### Scenario: Q4 not derived when a source is missing
- GIVEN an FY total but no 9-month YTD for that signature and fiscal year
- WHEN Q4 derivation runs
- THEN it skips Q4 for that year and surfaces the gap, never fabricating a value

#### Scenario: a directly-tagged Q4 is used as-is
- GIVEN a directly XBRL-tagged Q4 3-month fact
- WHEN the quarterly series is built
- THEN the reported Q4 is used and no derivation occurs

#### Scenario: Q4 derivation refuses across mismatched restatement vintages or units (critic-found)
- GIVEN an FY total and a 9-month YTD for the same signature/fiscal year that come from filings of different restatement vintages, or carry different XBRL unit/scale
- WHEN Q4 derivation runs
- THEN it either refuses to derive (flag basis-mismatch) or emits a distinct cross-basis/cross-vintage DQC flag — never the same generic "derived" flag as a clean same-basis case, and never a silent subtraction across incompatible bases

### Requirement: The fiscal calendar is a sourced, time-versioned per-company object (critic-found)
The system MUST treat each company's fiscal calendar (fiscal-year-end + quarter-end boundaries) as a first-class object with a recorded source and effective-date versioning, and MUST establish it before classifying that company's facts (a two-pass collect-then-classify order), so a mid-history fiscal-year-end change does not misclassify facts by ingestion order.

#### Scenario: non-December fiscal-year-end classifies by the company calendar
- GIVEN a company whose fiscal year ends June 30 and a 10-Q for "3 months ended 12/31"
- WHEN the fact is classified
- THEN the fiscal calendar (from its recorded source) yields fiscal-Q2, not calendar-Q4

#### Scenario: a mid-history fiscal-year-end change is versioned
- GIVEN a company that changed its fiscal-year-end partway through the requested history
- WHEN facts before and after the change are classified
- THEN each is classified against the fiscal-calendar version effective for its period_end, and the transition is recorded, never applied uniformly

#### Scenario: classification is deferred until the calendar is established
- GIVEN a streaming multi-year fetch where a company's fiscal calendar is inferred from its own period_end sequence
- WHEN facts arrive before the full sequence (and any FYE change) is known
- THEN classification does not commit a period_type until the calendar is established (collect-then-classify), never guessing from a partial sequence

### Requirement: Every emitted point and DQC flag carries structured provenance (critic-found)
Every emitted series point MUST carry its source accession(s), source form (10-K \| 10-Q), and duration_class; and every DQC flag MUST follow one defined schema (flag type, old value, new value, contributing accession(s), reason), so a downstream consumer or auditor can trace and filter any point.

#### Scenario: a series point is traceable to its source filing
- GIVEN a built quarterly series point
- WHEN it is emitted
- THEN it carries the source accession(s), the source form, and the duration_class it was built from — not only a period label and value

#### Scenario: a restatement DQC flag carries the full audit content (parity with scope-A policy C)
- GIVEN a restated single-quarter value resolved by policy C (accessions A→B, old→new value)
- WHEN the DQC flag is emitted
- THEN it records the old value, the new value, and both accessions A and B (the same content scope-A's annual policy C requires)

#### Scenario: a derived Q4 records both contributing accessions
- GIVEN a Q4 derived from an FY total (accession X) and a 9-month YTD (accession Y)
- WHEN the derived point is emitted
- THEN its DQC flag records the derived type plus both accession X and accession Y

### Requirement: Coverage honesty extends to per-filing completeness (critic-found)
The coverage report MUST extend scope-A's range-level clamp to per-filing/per-quarter completeness within a covered year, and MUST distinguish a not-yet-filed period from a fetch failure from an out-of-range period, so a partial year is never silently reported as fully covered.

#### Scenario: a partial year reports which filings are missing
- GIVEN a covered year whose 10-K and Q1/Q2 10-Qs fetched but whose Q3 10-Q is absent
- WHEN the coverage report is produced
- THEN it reports the year as partial (e.g. 3/4 filings, Q3 missing + reason), not as fully covered

#### Scenario: fetch-failure states are distinguished
- GIVEN a missing quarter
- WHEN the coverage report classifies it
- THEN it distinguishes not-yet-filed (current in-progress FY) from a fetch error (retryable) from out-of-requested-range — never collapsing all three into one silent "gap"

#### Scenario: a dimension absent from the quarterlies is flagged, not zero-filled
- GIVEN a dimensional signature present in a company's 10-K but not tagged in any of that year's 10-Qs
- WHEN the quarterly series is built for that dimension
- THEN it is reported as "no quarterly coverage for this dimension", distinct from a real zero and from a discontinued segment — never silently zero-filled or dropped
