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

### Requirement: Q4 single-quarter is derived by subtraction, guarded, and segregated
The analysis layer MUST derive an untagged Q4 single-quarter as (FY total − 9-month YTD)
— live evidence (~50 filers) confirms Q4 is NEVER directly XBRL-tagged, so derivation is the
only path to a Q4 point — and it MUST (a) flag the point as computed (a DQC flag), (b) keep
derived points in a SEGREGATED lane distinguishable from directly-reported points so a
consumer can request reported-only, and (c) skip rather than fabricate when an input is
absent or the inputs are basis/vintage/unit-incompatible. A derived value MUST NEVER
masquerade as a directly-reported value. (User governance decision A, 2026-07-16.)

#### Scenario: Q4 derived when both inputs exist, and segregated
- GIVEN an FY total and a 9-month YTD for the same signature and fiscal year, and no directly-tagged Q4 3-month fact
- WHEN Q4 derivation runs
- THEN it emits a Q4 point equal to FY minus 9-month YTD, flagged as derived (computed, not reported) and marked so a reported-only request excludes it

#### Scenario: a reported-only request excludes derived Q4
- GIVEN a quarterly series containing directly-reported Q1–Q3 and a derived Q4
- WHEN the caller requests reported-only points
- THEN the derived Q4 is excluded, and the reported Q1–Q3 remain

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

### Requirement: The fiscal calendar is read per-filing from dei tags, never cached per ticker
Live evidence (~87 filers) shows the fiscal calendar is DIRECTLY READABLE from each filing's
dei tags — `dei:DocumentFiscalPeriodFocus` (Q1/Q2/Q3/FY, the filing's own focus period) and
`dei:CurrentFiscalYearEndDate` (fiscal-year-end) — so the system MUST read them per-filing
rather than deriving quarter boundaries from scratch or caching a fiscal-year-end per ticker.
It MUST NOT cache/hardcode the fiscal-year-end per company (it DRIFTS across filings for
52/53-week filers — e.g. NVDA `--01-31` vs `--01-25`) and MUST treat it as NOMINAL for
floating-calendar filers, deriving the actual period boundaries from each fact's own
`period_start`/`period_end`. The `fiscal_period` dataframe column is NOT relied upon (it is
absent from some 10-Qs, e.g. COST) — period_type is derived from `period_end`/`period_start`,
cross-checked against the dei focus, never from the unreliable `fiscal_year`/`fiscal_period`
columns.

#### Scenario: non-December fiscal-year-end classifies by the filing's dei calendar
- GIVEN a company whose `dei:CurrentFiscalYearEndDate` is late September and a 10-Q with `dei:DocumentFiscalPeriodFocus=Q2` for a fact ending in late March
- WHEN the fact is classified
- THEN it is fiscal-Q2 (per the filing's dei calendar), not calendar-Q1

#### Scenario: fiscal-year-end is read per-filing, not cached
- GIVEN two filings from the same 52/53-week filer whose `dei:CurrentFiscalYearEndDate` differs (`--01-31` vs `--01-25`)
- WHEN each filing's facts are classified
- THEN each uses that filing's own dei value, and a mid-history fiscal-year-end change is handled naturally by the per-filing read — never a single cached value applied uniformly

#### Scenario: a prior-year comparative fact is classified from its own period, not the filing focus
- GIVEN a 10-Q whose `DocumentFiscalPeriodFocus=Q3` that also carries prior-year comparative facts
- WHEN a comparative fact is classified
- THEN its period_type is derived from its OWN period_start/period_end + the fiscal-year-end (the focus applies only to the filing's current-period facts, not comparatives)

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

### Requirement: Revenue-concept matching is an allow/deny + $-unit gate, not a substring (folds a scope-A fix)
Live evidence (~87 filers) shows the shipped `_is_revenue_concept` substring test is too
permissive across sectors, so the data layer MUST replace it with: (a) an ALLOW of legitimate
operating-revenue concepts beyond `RevenueFromContractWithCustomer*` — at least `us-gaap:Revenues`,
`RevenuesNetOfInterestExpense` (banks), `RevenueNotFromContractWithCustomer` (energy/utilities),
`RevenueFromContractWithCustomerIncludingAssessedTax` (utilities), and recognized company-extension
revenue concepts; (b) a DENY of `*Revenue*`-substring concepts that are NOT operating revenue —
`CostOfRevenue`/COGS (incl. `OtherCostOfOperatingRevenue`), `*Percentage`/`*ChangePercent` ratio
concepts, `RemainingPerformanceObligation` (RPO/backlog), deferred-revenue liabilities, and
non-operating `CollaborativeRevenue`; and (c) a $-UNIT guard that rejects any fact whose XBRL unit
is not a currency amount (e.g. a percentage or ratio). This is a scope-A (2.21.0) correctness
defect folded into this change (user decision, 2026-07-16); fixtures come from the verification
universe (CAT=dimensioned CostOfRevenue, BA/HON=percentage, SBUX=deferred, XOM=keep RevenueNotFromContract).

#### Scenario: dimensioned CostOfRevenue is not emitted as revenue
- GIVEN a filer (e.g. CAT) that tags `us-gaap:CostOfRevenue` dimensionally by segment
- WHEN the data layer extracts dimensional revenue
- THEN those COGS facts are excluded (deny-list), not emitted as revenue

#### Scenario: a percentage-valued *Revenue* concept is rejected by the unit guard
- GIVEN a `*RevenuePercentage`/`*RevenueChangePercent` extension fact whose unit is a ratio, not a currency
- WHEN the data layer extracts dimensional revenue
- THEN it is rejected by the $-unit guard, never emitted with a percentage as its "value"

#### Scenario: a legitimate non-RFCC revenue concept is kept
- GIVEN an energy filer (e.g. XOM) tagging dimensional `RevenueNotFromContractWithCustomer`, or a bank tagging `RevenuesNetOfInterestExpense`
- WHEN the data layer extracts dimensional revenue
- THEN the concept is KEPT (allow-list), not dropped as a non-RFCC concept

### Requirement: A foreign/ADR filer with no 10-Q is detected and returned N/A, never silently empty
Live evidence (11 ADR filers) shows foreign private issuers file 20-F + 6-K with no 10-Q (and 6-K interim XBRL is often absent or semi-annual), so a quarterly request for such a ticker MUST be detected and returned as an explicit N/A with a reason, never a silently-empty series.

#### Scenario: a 20-F-only filer returns an explicit quarterly-N/A
- GIVEN a ticker (e.g. TSM) whose submissions history has 20-F + 6-K but no 10-Q
- WHEN a quarterly KPI series is requested
- THEN the system returns an explicit "no quarterly XBRL (foreign 20-F/6-K regime)" N/A with the reason, not an empty or fabricated series
