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

#### Scenario: a cross-filing fiscal-label divergence at dedup is flagged, with a deterministic survivor (critic-found)
- GIVEN identical values for one signature/period_end/duration from two filings whose dei calendars yield different fiscal labels (52/53-week FYE drift or a mid-history FYE change)
- WHEN the duration-qualified dedup collapses them
- THEN the label conflict is flagged (DQC schema, both source calendars recorded) and the surviving label is deterministic (the later-filed filing's) — never an arbitrary pick

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

#### Scenario: a derived Q4 carries the three label groups, grounded in the 10-K's calendar (critic-found)
- GIVEN a Q4 derived from an FY total (10-K, accession X) and a 9-month YTD (10-Q, accession Y)
- WHEN the derived point is emitted
- THEN it carries the raw-window/calendar/fiscal label groups minted from the derived 3-month window measured against the 10-K's dei calendar; and if X and Y declare different fiscal calendars, the basis-mismatch refusal below applies

#### Scenario: Q4 derivation refuses across mismatched restatement vintages or units (critic-found)
- GIVEN an FY total and a 9-month YTD for the same signature/fiscal year that come from filings of different restatement vintages, or carry different XBRL unit/scale
- WHEN Q4 derivation runs
- THEN it either refuses to derive (flag basis-mismatch) or emits a distinct cross-basis/cross-vintage DQC flag — never the same generic "derived" flag as a clean same-basis case, and never a silent subtraction across incompatible bases

### Requirement: The fiscal calendar is read per-filing from dei tags, never cached per ticker
Live evidence (~87 filers) shows the fiscal calendar is DIRECTLY READABLE from each filing's
dei tags — `dei:DocumentFiscalPeriodFocus` (Q1/Q2/Q3/FY, the filing's own focus period) and
`dei:CurrentFiscalYearEndDate` (fiscal-year-end) — so the CLASSIFICATION layer (operating
post-fetch, with the filing in hand) MUST read them per-filing rather than deriving quarter
boundaries from scratch or caching a fiscal-year-end per ticker. Pre-fetch SELECTION is the
sanctioned exception: it runs before any filing is downloaded, has no dei tags available, and
MAY derive candidate fiscal periods from the filings-index metadata (form, `period_of_report`,
filing date) for selection purposes only — classification never inherits a selection-time guess.
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
The coverage report MUST extend scope-A's range-level clamp to per-filing/per-quarter completeness within a covered year, and MUST distinguish a not-yet-filed period from an out-of-requested-range period from an unclassified absence, so a partial year is never silently reported as fully covered. (A gap observed in the filings INDEX alone cannot ground a "retryable fetch error" claim — the index shows what exists, not why a download failed — so `fetch_error` is not an INDEX-absence state. Two OBSERVED states, each grounded by in-hand evidence, complete the classification (critic round 2, 2026-07-18): `attempted-fetch-failed` — a download/XBRL-parse actually raised, retryable, the exception is the ground; and `filed-but-unlabelable` — fetched fine but the fail-loud fiscal derivation rejected the filing, which is quarantined while the run continues. The report's comparison universe is the full filings INDEX, not the selected set — a filing the selection derivation missed surfaces as a selection gap, never as not-yet-filed.)

#### Scenario: a partial year reports which filings are missing
- GIVEN a covered year whose 10-K and Q1/Q2 10-Qs fetched but whose Q3 10-Q is absent
- WHEN the coverage report is produced
- THEN it reports the year as partial (e.g. 3/4 filings, Q3 missing + reason), not as fully covered

#### Scenario: absence states are distinguished
- GIVEN a missing quarter
- WHEN the coverage report classifies it
- THEN it distinguishes not-yet-filed (current in-progress FY) from out-of-requested-range from an unclassified absence (present-range gap with no derivable reason, surfaced as-is) — never collapsing the three into one silent "gap", and never claiming a retryable fetch error from index absence alone

#### Scenario: an actual fetch/parse failure is reported as attempted-and-failed, not an index absence (critic-found)
- GIVEN a Q3 10-Q present in the filings index whose download or XBRL parse raised
- WHEN the coverage report classifies that quarter
- THEN it reports attempted-fetch-failed (retryable, grounded by the in-hand failure) — never "unclassified absence" and never silently covered

#### Scenario: an unlabelable filing is quarantined and the run continues (critic-found)
- GIVEN a multi-year build in which exactly one filing's dei fiscal calendar fails the fail-loud derivation
- WHEN the run completes
- THEN the other filings' series emit normally, the failed filing's facts are excluded from fiscal-labeled output, and coverage reports that quarter filed-but-unlabelable (DQC schema) — one bad filing never aborts the whole run

#### Scenario: a selection-missed filing surfaces as a selection gap (critic-found)
- GIVEN a fiscal-boundary 10-Q present in the filings index that the pre-fetch derivation failed to select
- WHEN the coverage report runs against the index universe
- THEN the quarter is reported as index-visible-but-not-selected, never as not-yet-filed

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
concepts, `RemainingPerformanceObligation` (RPO/backlog), deferred-revenue liabilities,
non-operating collaborative-arrangement revenue (`RevenueFromCollaborativeArrangement*`,
denied via the `CollaborativeArrangement` substring — a bare `CollaborativeRevenue` tag does
not exist), and REIT pro-forma / ladder-schedule artifacts (`BusinessAcquisitionsProFormaRevenue`,
ladder concepts like `pld:NetIncreaseDecreaseToRentalRevenue*` — verification-universe false-positive
class 6); and (c) a $-UNIT guard that rejects any fact whose XBRL unit
is not a currency amount (e.g. a percentage or ratio). This is a scope-A (2.21.0) correctness
defect folded into this change (user decision, 2026-07-16); fixtures come from the verification
universe (CAT=dimensioned CostOfRevenue, BA/HON=percentage, SBUX=deferred, XOM=keep RevenueNotFromContract).

#### Scenario: dimensioned CostOfRevenue is not emitted as revenue
- GIVEN a filer (e.g. CAT) that tags `us-gaap:CostOfRevenue` dimensionally by segment
- WHEN the data layer extracts dimensional revenue
- THEN those COGS facts are excluded (deny-list), not emitted as revenue

#### Scenario: a percentage-named *Revenue* concept is excluded by the deny list
- GIVEN a `*RevenuePercentage`/`*RevenueChangePercent` extension fact (e.g. the BA/HON fixtures from the verification universe)
- WHEN the data layer extracts dimensional revenue
- THEN it is excluded by the `Percent`-substring deny match (the name gate fires before any unit check), never emitted

#### Scenario: the $-unit guard backstops a non-currency fact that passes the name gates
- GIVEN a `*Revenue*` concept that passes the allow/deny NAME gates but whose XBRL unit is not a currency amount (synthetic fixture — no real filer case in the verification universe today)
- WHEN the data layer extracts dimensional revenue
- THEN the $-unit guard rejects it, never emitted with a non-currency "value"

#### Scenario: a legitimate non-RFCC revenue concept is kept
- GIVEN an energy filer (e.g. XOM) tagging dimensional `RevenueNotFromContractWithCustomer`, or a bank tagging `RevenuesNetOfInterestExpense`
- WHEN the data layer extracts dimensional revenue
- THEN the concept is KEPT (allow-list), not dropped as a non-RFCC concept

### Requirement: A foreign private issuer on the 20-F+6-K regime is detected and returned N/A, never silently empty
Live evidence (11 ADR filers) shows foreign private issuers file 20-F + 6-K with no 10-Q (and 6-K interim XBRL is often absent or semi-annual), so a quarterly request for such a ticker MUST be detected and returned as an explicit N/A with a reason, never a silently-empty series.

#### Scenario: a 20-F-only filer returns an explicit quarterly-N/A
- GIVEN a ticker (e.g. TSM) whose submissions history has 20-F + 6-K but no 10-Q
- WHEN a quarterly KPI series is requested
- THEN the system returns an explicit "no quarterly XBRL (foreign 20-F/6-K regime)" N/A with the reason, not an empty or fabricated series

### Requirement: Every fact carries parallel calendar and fiscal period labels, honestly named
Each emitted dimensional fact MUST carry THREE period field groups in parallel, never one
collapsed into another (rebuild design decision, user-ratified 2026-07-17 — mirrors
Compustat DATADATE/DATACQTR/DATAFQTR; full record in `../../rebuild-findings.md` §RESOLVED):
(1) the RAW WINDOW — `period_start`, `period_end`, `duration_months` (already emitted);
(2) a CALENDAR label — `calendar_year` + `calendar_quarter`, mechanically derived from
`period_end` (the calendar quarter containing the period-end date); (3) a FISCAL label —
`fiscal_year` + `fiscal_quarter`, derived from the fact's OWN `period_end` measured against
that filing's dei fiscal calendar, per-fact. The fiscal label MUST fail loud when the
filing's fiscal calendar cannot be read — it MUST NEVER fall back to the calendar year, and
a calendar value MUST NEVER be emitted under a fiscal-named field or vice versa.
Four further constraints bind the fiscal label (critic round 2, 2026-07-18):
(a) `fiscal_quarter` takes values Q1|Q2|Q3|Q4|FY and is derived JOINTLY with duration_class —
a 12-month fact carries FY (never a bare Q4); a YTD fact carries the fiscal quarter its
period_end sits on, with its cumulative duration_class distinguishing it from the
single-quarter point. (b) Boundary matching uses a declared small tolerance (the verified
52/53-week drift is ≤6 days; the exact constant is a plan decision): a period_end within
tolerance of a fiscal-quarter boundary maps to it; beyond tolerance the fact is flagged
unclassifiable — never nearest-guessed. (c) Each fiscal label MUST record its derivation
basis — `dei-declared` (the tag in hand, the authority) or `projected` (a +12-month
projection of the prior declared fiscal-year-end, sanctioned as FALLBACK only) — so an
auditor can separate authority-confirmed labels from projections. (d) The label-schema change MUST NOT alias pre-revision
cached payloads. Implementation recon (2026-07-18) found the labeled-fact layer is UNCACHED —
only schema-independent raw-source caches exist (tickers / facts_{cik} / concept_{cik}_{concept} /
submissions_{cik} / narrative_sections_{accession}) — so the obligation is: no existing cache
may feed the labeled output, and any FUTURE cache of the labeled-fact payload MUST use a
schema-versioned DISTINCT key, never a legacy key.

#### Scenario: a non-December-FYE quarter carries diverging calendar and fiscal labels
- GIVEN NVDA's FY2026-Q3 fact whose period_end is 2025-10-26
- WHEN the fact is emitted
- THEN it carries calendar_year=2025 + calendar_quarter=Q4 AND fiscal_year=2026 + fiscal_quarter=Q3, in parallel

#### Scenario: a prior-year comparative gets its own fiscal label, never the filing's focus stamped
- GIVEN a filing whose `dei:DocumentFiscalYearFocus` is 2019 that also carries FY2017/FY2018 comparative facts (the AAPL FY2019 10-K case)
- WHEN the comparative facts are emitted
- THEN each carries the fiscal label derived from its OWN period_end against the filing's fiscal calendar (2017, 2018 respectively), never the filing focus applied uniformly

#### Scenario: an unreadable fiscal calendar fails loud, never a calendar fallback
- GIVEN a filing whose dei fiscal-calendar tags are absent or malformed
- WHEN the fiscal label is derived for its facts
- THEN a distinct DQC-schema error/flag naming the filing is raised, and `period_end[:4]` (the calendar year) is never emitted as the fiscal_year

#### Scenario: an annual fact is labeled FY, never a bare Q4 (critic-found)
- GIVEN a 12-month 10-K fact whose period_end sits on the fiscal year end
- WHEN its labels are emitted
- THEN fiscal_quarter=FY (with duration_class 12mo-FY), never Q4 — so an annual fact stays distinguishable by construction from any reported or derived Q4 single-quarter point

#### Scenario: an out-of-tolerance period_end is unclassifiable, never nearest-guessed (critic-found)
- GIVEN a readable dei calendar and a fact whose period_end lands beyond the declared tolerance from every fiscal-quarter boundary (e.g. a transition/stub period)
- WHEN the fiscal label is derived
- THEN the fact is flagged unclassifiable (DQC schema), and no nearest-boundary label is guessed

#### Scenario: a projection-grounded label or verdict is marked as such (critic-found)
- GIVEN an in-progress fiscal year whose year-end dei tag does not yet exist, so the fiscal calendar rests on a +12-month projection of the prior declared fiscal-year-end
- WHEN a fiscal label (or a not-yet-filed coverage verdict) is grounded by that projection
- THEN it records derivation basis `projected` — never indistinguishable from a `dei-declared` read

#### Scenario: pre-revision cached payloads are never merged into parallel-label output (critic-found)
- GIVEN every existing raw-source cache key pre-seeded with a pre-rebuild-era payload, including an old-shape labeled-fact dict (calendar-valued `fiscal_year`, no calendar/fiscal pair) planted under each key
- WHEN extract_dimensional_revenue runs after this revision
- THEN every emitted fact is freshly derived (parallel labels present) and no planted old-shape payload reaches the output — the labeled-fact layer stays uncached (verified 2026-07-18); introducing a labeled-fact cache without a schema-versioned distinct key is a spec violation

### Requirement: A fiscal-year range request selects filings by their declared fiscal year
A request for fiscal years `[since_year, until_year]` MUST select filings whose DECLARED
fiscal year falls in the requested range — the filing's own `dei:DocumentFiscalYearFocus`
(post-fetch), or the sanctioned filings-index derivation at pre-fetch selection time — and
MUST NOT select by the calendar year of `period_of_report`. (This is the root-cause defect's
spec home: `period_of_report[:4]` equals the fiscal year only for December-FYE filers.)
Because the pre-fetch index derivation is a GUESS and the dei declaration is the TRUTH,
range membership MUST be re-checked post-fetch against the declared fiscal year; on
disagreement the declaration wins and the correction is surfaced — never silent in either
direction (critic round 2, 2026-07-18).

#### Scenario: a non-December-FYE filer's fiscal-year quarters are selected despite the calendar mismatch
- GIVEN NVDA (fiscal year ends late January; every FY2026 10-Q period_of_report falls in calendar 2025) and a request form=10-Q, since_year=2026, until_year=2026
- WHEN filings are selected
- THEN all three FY2026 10-Qs are selected, and no FY2027 filing (period ending in calendar 2026) is selected

#### Scenario: a December-FYE filer's selection is unchanged (calendar == fiscal)
- GIVEN a fixed-December-FYE filer (not a floating 52/53-week year-end that can cross Dec-31) whose fiscal-year label equals the calendar year its periods end in
- WHEN a fiscal-year range is selected
- THEN the selection equals the previous calendar-year behaviour (the correction is a no-op for fixed December FYEs)

#### Scenario: a selection-time guess is reconciled against the fetched declaration (critic-found)
- GIVEN a filing selected as a candidate for FY2026 by index-metadata derivation whose fetched `dei:DocumentFiscalYearFocus` declares FY2027
- WHEN range membership is finalized
- THEN the filing is excluded from the FY2026 result AND the guess/declaration mismatch is surfaced (DQC-schema flag or coverage line) — never silently kept, never silently dropped

#### Scenario: a filing with an unreadable fiscal-year declaration is flagged, never calendar-bucketed (critic-found)
- GIVEN a fetched filing whose `dei:DocumentFiscalYearFocus` is absent or malformed
- WHEN fiscal-year range membership is decided
- THEN a distinct flag names the filing, and it is never silently dropped nor bucketed by `period_of_report[:4]`

#### Scenario: emitted points are range-filtered by each fact's OWN fiscal label (critic-found)
- GIVEN a fiscal-range request [2026, 2026] and a selected FY2026 10-Q carrying FY2025 comparative facts
- WHEN the series is built
- THEN only facts whose own fiscal label falls in the requested range are emitted as series points (comparatives remain usable internally for dedup/restatement) — filing-level selection never leaks out-of-range facts into the output
