---
name: data-sources-and-fixtures
description: Data provenance contract, fixture handoff format, and out-of-band fetching discipline for investing-team workers
tier: 2
layer: data
---

# Data Sources and Fixtures

Tier 2 standard covering the **data provenance layer** of every
investing-team deliverable: which sources are canonical for which
data types, how user-provided fixtures are ingested, when the worker
is permitted to fetch data autonomously versus when it must block,
and how staleness is flagged. Every quantitative claim in an
investing-team memo must be traceable to a provenance record in
this format.

Tier 2 because this is a **process discipline standard**, not a
domain-knowledge standard. The hallucination risk here is not about
facts per se but about **data laundering** — presenting a number
as if it came from an authoritative source when it was hallucinated,
or treating a stale figure as current. The provenance contract
prevents both failure modes.

**Scope**: sourcing discipline for all investing-team memos —
financial statements, price data, macro series, institutional flows,
user-provided fixtures. This standard applies to every worker
producing a quantitative investing artifact. Data interpretation
and analysis belong to `investment-security-valuation.md`,
`investment-macro-regime.md`, and related standards.

## Primary Sources

- **The Twelve-Factor App** (Adam Wiggins et al., 2012). https://12factor.net/. Factor III (Config) and Factor X (Dev/prod parity). The canonical argument that credentials belong in environment variables, not code — and that the same discipline governs all external inputs. Applied here: data provenance requires the same rigor as config management. A number embedded in a memo without a declared source is the data equivalent of a hardcoded credential.
- **TWSE / MOPS** (2024). *公開資訊觀測站 (Market Observation Post System)*. https://mops.twse.com.tw/. Taiwan statutory filing portal — canonical for 月營收 (monthly revenue disclosures), quarterly and annual financial statements, insider holdings, and material events. Operated by Taiwan Stock Exchange Corporation. Fresher than any third-party aggregator; filings appear on MOPS before syndication to Bloomberg / Refinitiv.
- **U.S. Securities and Exchange Commission** (2024). *EDGAR Full-Text Search*. https://efts.sec.gov/EFTS/ and https://www.sec.gov/cgi-bin/browse-edgar. Canonical source for all US public company filings: 10-K (annual), 10-Q (quarterly), 8-K (current material events), 13-F (institutional holdings, quarterly), DEF 14A (proxy / compensation). Free, no authentication required.
- **Federal Reserve Bank of St. Louis** (2024). *FRED Economic Data*. https://fred.stlouisfed.org/. Canonical macro series database: DGS10 (10-year Treasury yield), T10Y2Y (yield-curve spread), CPIAUCSL (CPI all-items urban), UNRATE (unemployment rate), FEDFUNDS (federal funds effective rate). Free API with FRED_API_KEY (registration required, free).
- **yfinance** (Ran Aroussi, ongoing). GitHub: ranaroussi/yfinance. Unofficial Yahoo Finance Python wrapper. Provides historical OHLCV prices and basic company metadata. NOT a primary source for financial statement data — use SEC EDGAR for those. Suitable for price history and technical calculations only. Wrapper stability varies; always note version used.

## Critical Attribution Corrections

### MOPS is a filing portal, not a data vendor

MOPS (mops.twse.com.tw) is a **statutory disclosure portal**
operated by TWSE under Taiwan's Securities and Exchange Act. It is
not a data vendor or API service. Data retrieval requires parsing
HTML tables or using TWSE's unofficial JSON endpoints. Third-party
aggregators (e.g., Goodinfo, CMoney) re-publish MOPS data with
latency and occasional transcription errors. For any Taiwan company
financial figure cited in an investing-team memo, the canonical
source is MOPS directly, not a downstream aggregator.

### yfinance is not a financial data provider

yfinance is a **scraper wrapper** for Yahoo Finance's undocumented
internal APIs. Yahoo Finance itself is an aggregator, not a primary
source. Financial statement figures from yfinance may lag official
filings, carry transcription errors from Yahoo's data vendors, and
may omit restatements. Do NOT cite "yfinance" or "Yahoo Finance" as
the source for earnings, revenue, or balance-sheet figures. Cite the
underlying statutory filing (SEC EDGAR for US; MOPS for Taiwan).
yfinance is appropriate for: adjusted close prices, volume, dividend
history, and basic split history.

### FRED series codes are version-specific

FRED series IDs (DGS10, T10Y2Y, CPIAUCSL, etc.) correspond to
**specific methodological vintages**. When the BLS or Federal Reserve
revises the methodology of a series, FRED may create a new series ID
rather than revising the existing one. Always cite the specific
series ID (e.g., CPIAUCSL, not "CPI") and record the observation
date. FRED's default API response includes the series ID, frequency,
and vintage — capture all three.

### FRED_API_KEY is required for the API, not for the website

The FRED website (fred.stlouisfed.org) provides free public access
without authentication. The **FRED API** (api.stlouisfed.org) requires
a free FRED_API_KEY registered at https://fred.stlouisfed.org/docs/api/api_key.html.
Do NOT claim that FRED data requires a paid subscription. Do NOT
embed API keys in code or memo text — store as environment variable
per 12-Factor Factor III.

### SEC EDGAR CIK is the stable identifier, not the ticker

Company tickers change (spin-offs, name changes, delistings).
The **Central Index Key (CIK)** is the stable permanent identifier
on EDGAR. When citing an EDGAR filing, record: CIK + form type +
filing date. Example: "NVIDIA Corporation, CIK 0001045810, 10-K for
FY2025, filed 2025-02-26." The ticker NVDA is informational only.

## Data Provenance Contract

Every investing-team memo MUST include a **Provenance Footer**
listing every data input used. The footer is the final section of
the memo, appearing after all analysis.

### Required format

```
## Data Provenance

| Data Item | Source | Endpoint / Filing ID | As-Of Date | Fetched UTC | Staleness |
|---|---|---|---|---|---|
| TSMC Q3 2026 revenue | MOPS | 2330 月營收 Oct-2026 | 2026-10-10 | 2026-10-12T03:15Z | 2 days |
| DGS10 | FRED | series/DGS10 | 2026-10-11 | 2026-10-12T03:16Z | 1 day |
| NVDA 10-K FY2025 | SEC EDGAR | CIK 0001045810, 10-K filed 2025-02-26 | 2025-01-26 | 2026-10-12T03:20Z | 7 months |
| AAPL adj close | yfinance 0.2.x | AAPL historical | 2026-10-11 | 2026-10-12T03:22Z | 1 day |
```

### Column definitions

- **Data Item**: brief human-readable description of the data point (what number, which company, which period)
- **Source**: the originating source — not an aggregator, not the library, but the authoritative publisher (MOPS, SEC EDGAR, FRED, yfinance for prices only)
- **Endpoint / Filing ID**: enough to reconstruct the retrieval — URL path, series ID, CIK + form type + date, or "User-provided fixture"
- **As-Of Date**: the date the data is valid for (e.g., statement period-end date, price date, observation date)
- **Fetched UTC**: the timestamp when the data was retrieved by the worker or provided by the user
- **Staleness**: calendar distance from As-Of Date to Fetched UTC; computed as `Fetched − As-Of`; flag (see rules below) if over threshold

### Minimum provenance record

If space is constrained (quick-screen output), the minimum
acceptable provenance record is:

```
[Data Item] — [Source], [Filing ID or series], as of [As-Of Date], retrieved [date]
```

Full table format is required for all formal memos and
investment thesis documents.

## Fixture Handoff Format

A **fixture** is data provided directly by the user — pasted text,
a CSV extract, a screenshot, a table copied from a terminal or
spreadsheet. Fixtures bypass the normal fetch path. The worker
must:

1. **Acknowledge the fixture explicitly** at the point of first use:
   > "Using user-provided fixture for [data item]: [brief description
   > of what was provided]."

2. **Extract and record key fields**: state which specific numbers
   are being used from the fixture, to make the analytical chain
   auditable.

3. **Record in provenance footer** with:
   - Source = "User-provided fixture"
   - Endpoint = format description (e.g., "CSV paste", "screenshot of TWSE T86 report", "terminal output from yfinance script")
   - As-Of Date = the date embedded in the fixture data (if discernible); otherwise "unknown — as provided"
   - Fetched UTC = current time (when the memo is being written)

4. **Flag data quality issues** if the fixture is ambiguous: unclear
   date, missing units, apparent transcription errors. The worker
   does not reject fixtures — it flags concerns and proceeds, so
   the analyst can decide whether to refetch.

### Example fixture record

```
| TSMC Q2 2026 EPS | User-provided fixture | CSV paste, 4 columns | 2026-07-15 | 2026-10-12T04:00Z | 3 months |
```

## Data Source Taxonomy

| Source Type | Examples | Typical Latency After Event | Auth | Best For |
|---|---|---|---|---|
| Taiwan statutory filings | MOPS (mops.twse.com.tw) | 0–1 day | None | 月營收, financial statements, insider holdings, material events |
| US statutory filings | SEC EDGAR (sec.gov) | 0–1 day | None | 10-K, 10-Q, 8-K, 13-F, proxy statements |
| Macro series | FRED (fred.stlouisfed.org) | Daily (most series) | FRED_API_KEY (free) | Treasury yields, CPI, unemployment, fed funds rate |
| Taiwan institutional flows | TWSE T86 report | End of trading day | None | 三大法人 (foreign, investment trust, proprietary dealer) net buy/sell |
| Equity price history | yfinance, Alpha Vantage | Real-time to 1-day | None (yfinance), API key (Alpha Vantage) | Adjusted OHLCV, dividends, splits — prices ONLY |
| User fixture | Pasted content, uploaded file | As provided | N/A | Quick analysis from user's own data |

### Source hierarchy for conflict resolution

When two sources provide conflicting figures for the same data point,
apply this hierarchy: statutory filing > central bank series >
exchange data > third-party aggregator > user fixture (unless the
fixture is the analyst's own primary research). Record the conflict
and the resolution in the provenance footer.

## Out-of-Band Fetching Discipline

The investing-team worker is **analysis-first, not data-first**. The
worker does not autonomously browse the internet or make HTTP requests
outside of explicitly sanctioned paths. This is a behavioral
constraint, not a capability constraint.

### Decision tree

```
Data needed?
    |
    +-- In user-provided fixture?
    |       YES → ingest via fixture contract; record provenance
    |
    +-- Available via installed MCP tool (e.g., CasualMarket, yfinance MCP)?
    |       YES → main agent may fetch before invoking worker;
    |             worker ingests result as fixture
    |
    +-- Available via investing-toolkit/scripts/*_client.py
    |   AND user has explicitly consented to script execution?
    |       YES → worker MAY run targeted fetch;
    |             MUST record in provenance footer
    |
    +-- None of the above?
            → return BLOCKED:
              suggested_action: "fetch [source] for [data item]
              and re-invoke investing-team worker"
```

### BLOCKED status for missing data

When a required data item is not available via any sanctioned path,
the worker outputs:

```json
{
  "status": "BLOCKED",
  "reason": "Required data not available in fixture or via installed MCP",
  "missing_data": "[data item] from [source]",
  "suggested_action": "fetch [endpoint or series] for [data item] and re-invoke"
}
```

Workers do NOT hallucinate numbers to avoid a BLOCKED status. A
memo with hallucinated figures is worse than a BLOCKED status.

### Bash/Python escape hatch

If `investing-toolkit/scripts/*_client.py` scripts are available
(FRED client, EDGAR client, TWSE client) and the user has explicitly
granted consent to run them in this session, the worker may invoke
a targeted fetch. Conditions:

1. The script already exists — the worker does NOT write new fetch
   scripts mid-memo as a workaround.
2. The fetch is targeted: one endpoint, one data item.
3. Each such fetch is recorded in the provenance footer with the
   script name, invocation parameters, and timestamp.

## Staleness Rules

Staleness = `Fetched UTC − As-Of Date`. This measures how old the
data is at the time of analysis, not how recently it was published.

| Data Type | Acceptable Staleness | Stale Action |
|---|---|---|
| Equity prices (daily close) | ≤ 1 trading day | Re-fetch; flag if market closed and delay is expected |
| Taiwan 月營收 | Within same disclosure window (prior month's revenue disclosed by 10th of current month) | Note if pre-announcement; flag if worker is analyzing post-announcement without the latest figure |
| Quarterly financial statements (US 10-Q / Taiwan 季報) | ≤ 2 quarters | Flag if older; note if restatement risk exists |
| Annual financial statements (US 10-K / Taiwan 年報) | ≤ 18 months | Flag if older than 2 fiscal years |
| FRED fast-moving series (DGS10, T10Y2Y, FEDFUNDS) | ≤ 1 week | Re-fetch; yields move daily |
| FRED slow-moving series (CPIAUCSL, UNRATE) | ≤ 6 weeks | Flag if older; monthly series with ~3-week release lag |
| Taiwan 三大法人 institutional flows | ≤ 1 trading day | Re-fetch; flows are directionally time-sensitive |
| SEC 13-F institutional holdings | ≤ 1 quarter + 45-day filing lag | Flag if older; 13-F reflects 45-day-old positions by design |

### Staleness flag format

When data exceeds the acceptable staleness threshold, append
`[STALE — as of [As-Of Date], now [current date]]` to the data
item in the analysis body. Do not suppress the data; flag it and
let the analyst decide whether to update.

### Pre-announcement caveat (Taiwan 月營收)

TWSE regulations require listed companies to disclose prior-month
revenue by the 10th calendar day of the following month. Analysis
conducted between the 1st and 10th before the announcement date
MUST note: "月營收 for [prior month] not yet disclosed as of
[analysis date]; analysis uses [prior prior month] as most
recent available."

## Taiwan-Specific Sourcing Guide

Taiwan-listed securities require sourcing from TWSE/MOPS and
related TWSE infrastructure. This section details the canonical
endpoints for each common Taiwan data type.

### 月營收 (Monthly Revenue)

**Canonical source**: MOPS monthly revenue disclosure pages
under 電子申報資料查詢 → 月營收. Data appears after the 10th
of each month for the prior month.

**Key fields to record**:
- 股票代號 (stock code), e.g., 2330 for TSMC
- 申報月份 (disclosure month)
- 本月營收 (revenue this month), 上月營收 (last month), 去年同月 (same month last year)
- 當月累計 (year-to-date)

**Common error**: citing the 月增率 (MoM growth) or 年增率
(YoY growth) figures from an aggregator without verifying
them against the raw MOPS figures. Aggregators sometimes
compute growth using unrevised prior figures; MOPS is the
authoritative source.

### 三大法人 (Institutional Flows — TWSE T86)

**Canonical source**: TWSE open data portal, T86 report.
https://www.twse.com.tw/rwd/zh/fund/T86

**Three institutions tracked**:
- 外資 (Foreign investors / FINI): net buy/sell in shares
  and NTD value
- 投信 (Investment trusts, domestic funds): net buy/sell
- 自營商 (Proprietary dealers of securities firms): net buy/sell
  split into 自行買賣 (own account) and 避險 (hedging)

**Latency**: T86 is published after each trading session
closes (~6:00–7:00 PM Taipei time). Do not use pre-close
data as if it were final.

**Staleness rule**: for directional flow analysis, T86 data
older than 1 trading day is stale. For cumulative flow
analysis (e.g., 10-day net flows), weekly updates may be
acceptable with explicit staleness notation.

### Insider Holdings (內部人持股)

**Canonical source**: MOPS under 持股申報資料 → 內部人持股.
Monthly disclosures; directors, supervisors, major shareholders
(>10%) are required to report by the 15th of each month for
the prior month's holding changes.

**Key caveat**: MOPS shows reported holdings, not beneficial
ownership through trusts or related parties. Insider holding
figures from MOPS should be treated as minimum disclosures,
not comprehensive ownership pictures.

### Financial Statements (財務報告)

**Canonical source**: MOPS financial reports section.
Taiwan-listed companies file:
- 季報 (quarterly reports): within 45 days after quarter end
  (Q1–Q3); annual within 3 months of fiscal year end
- 年報 (annual reports): filed separately from the audited
  financial statements

**IFRSs adoption**: Taiwan listed companies have used IFRS
(as endorsed by Taiwan's Financial Supervisory Commission)
since 2013. Financial statements before 2013 used Taiwan GAAP;
cross-period comparisons spanning the transition year require
care.

## Anti-Drift Guardrails for Data Claims

### Never cite a third-party aggregator as a primary source

Aggregators (Goodinfo, CMoney, TEJ, Bloomberg, FactSet, etc.)
are useful for discovery and navigation but are **not primary
sources**. They introduce latency, transcription errors, and
methodological choices (e.g., how to handle stock splits,
how to compute adjusted prices). Every financial statement
figure cited in a formal investing-team memo must trace back
to a statutory filing (MOPS or SEC EDGAR) or a central bank
data series (FRED).

### Never claim "real-time" for a pull from yfinance

yfinance pulls from Yahoo Finance, which sources from
multiple delayed data vendors. The actual latency for
"real-time" quotes via yfinance is typically 15 minutes
for US equities and varies for international markets.
Cite as "delayed quote as of approximately [time]" rather
than "real-time."

### Fiscal year vs calendar year ambiguity

Not all companies use December fiscal year ends. When citing
annual results:
- US companies: fiscal year end varies; always state
  "FY[year] ended [month-end date]" (e.g., NVDA FY2025
  ended January 26, 2025).
- Taiwan companies: most large-caps use December year-end
  but some use September or March. Always confirm from MOPS.
- Mismatching fiscal year periods between two companies
  (e.g., comparing NVDA Jan-2025 to TSMC Dec-2024) is a
  common analysis error; flag when comparison periods do not
  align.

## Relationship to Other Standards

- Provenance contract applies to all quantitative inputs in
  `investment-security-valuation.md` memos — P/E ratios, revenue
  figures, and DCF assumptions all require sourcing.
- Price data sourced via this standard feeds into
  `position-sizing-and-risk.md` volatility calculations.
- Macro series (FRED) sourced here feed into
  `investment-macro-regime.md` regime diagnostics.
- Staleness checks are a prerequisite gate before any
  `quick-stock-screen.md` output is presented.
- Taiwan-specific sourcing (MOPS, T86) is required when
  producing memos on Taiwan-listed securities; the T86
  institutional flow data feeds into sector and individual
  stock directional analysis.
