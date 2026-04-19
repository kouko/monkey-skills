# SEC EDGAR Guide

Reference for the `sec_edgar_client.py` fundamental-layer adapter.
Covers API endpoints, form coverage, XBRL taxonomy, narrative Item-section
parsing, rate-limit compliance, and CLI invocations.

## 1. API Overview

**Host**: `data.sec.gov` (JSON) + `www.sec.gov/Archives` (HTML filings)
**Auth**: none — SEC EDGAR is free public infrastructure.
**Rate limit**: ≤10 requests/second per client (SEC Fair Access policy).
**User-Agent**: **mandatory** — requests without an identified UA return `403`.

### 1.1 User-Agent format

SEC mandates an identified string of the form:

```
User-Agent: <name or org> <email>
```

`sec_edgar_client.py` sets this to:

```
kouko investing-toolkit <noreply@anthropic.com>
```

See SEC's official guidance:
<https://www.sec.gov/os/accessing-edgar-data>

### 1.2 Endpoint map

| Purpose | Endpoint | Cache TTL |
|---------|----------|-----------|
| Ticker → CIK map | `https://www.sec.gov/files/company_tickers.json` | 7 days |
| Company full XBRL facts | `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json` | 24 hrs |
| Single us-gaap concept | `https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/{concept}.json` | 24 hrs |
| Recent filings index | `https://data.sec.gov/submissions/CIK{cik:010d}.json` | 24 hrs |
| Filing HTML | `https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodash}/{primary}.htm` | permanent |

The tiered cache matches the update cadence: filings are immutable once
accepted by EDGAR, XBRL facts and submissions indexes change at filing
frequency, and the ticker → CIK map changes only on new listings / delistings.

### 1.3 429 retry pattern

`sec_edgar_client.py` enforces a `0.1s` inter-request throttle (≤10 req/sec)
and on `429 Too Many Requests` performs up to 3 retries with exponential
backoff (`2s, 4s, 8s`). Large batches should still stay under ~8 req/sec
average to leave headroom for shared infrastructure.

## 2. Form Coverage

The client supports filter-by-form via `--forms` (comma-separated). Seven
form families cover the bulk of fundamental analysis needs:

### 2.1 10-K — Annual report (deep dive)

Annual audited disclosure. Primary document for fundamental analysis.
Sections of interest (parsed by Item regex — see §4):

- **Item 1 Business** — segments, geography, products, customer concentration
- **Item 1A Risk Factors** — management-disclosed risks; compare YoY for new risks
- **Item 7 MD&A** — revenue drivers, margin commentary, liquidity
- **Item 7A Quantitative & Qualitative Disclosures about Market Risk** — rate / FX / commodity sensitivity
- **Item 8 Financial Statements & Supplementary Data** — full BS/IS/CF + notes (see §4 caveat)

Filing cadence: within 60/75/90 days of fiscal year end (large-accelerated / accelerated / non-accelerated filer).

### 2.2 10-Q — Quarterly report

Unaudited interim disclosure. Updated financials + MD&A for non-fiscal-year-end
quarters. Relevant Items:

- **Item 1 Financial Statements** — unaudited BS/IS/CF
- **Item 2 MD&A** — quarterly variance commentary

Filing cadence: within 40/45 days of quarter end.

### 2.3 8-K — Current report (material events)

Event-driven filings. Triggers include:

- Item 1.01 Material Definitive Agreement (e.g. M&A announcements)
- Item 2.02 Results of Operations (earnings release)
- Item 5.02 Departure/Appointment of Officers & Directors (管理層異動)
- Item 7.01 Regulation FD Disclosure (盈餘警告 / guidance pre-announcement)
- Item 8.01 Other Events

Filing cadence: within 4 business days of the triggering event.

### 2.4 Form 4 — Insider transactions

Statement of changes in beneficial ownership. Filed by officers, directors,
and >10% beneficial owners. **2-business-day filing deadline** after the
transaction — near real-time insider flow signal.

Useful for tracking cluster buying/selling by insiders ahead of material news.

### 2.5 13F-HR — Institutional ownership

Quarterly holdings report from institutional investment managers with
≥$100M in §13(f) securities. **45-day lag** after quarter-end. Useful for
long-only fund flow tracking (Berkshire, Scion, Citadel, etc.).

### 2.6 S-1 / S-3 — Registration statements

- **S-1** — initial registration (IPO or first public offering of new securities)
- **S-3** — shelf registration for seasoned issuers (secondary offerings, ATM programs)

Dilution signal for existing holders; contains offering terms and use of proceeds.

### 2.7 DEF 14A — Definitive proxy statement

Annual proxy filed ahead of the shareholder meeting. Contents:

- Director nominees + committee structure (governance)
- Executive compensation tables (薪酬, Say-on-Pay vote)
- Related-party transactions
- Shareholder proposals + board recommendations

Cadence: annually, ~30-40 days before the shareholder meeting.

## 3. XBRL Fact Taxonomy Basics

XBRL (eXtensible Business Reporting Language) tags every number in a filing
with a machine-readable concept. The `us-gaap` taxonomy is the dominant
namespace for US issuers.

### 3.1 Common concepts

| Concept | Meaning | Unit |
|---------|---------|------|
| `Revenues` | Top-line revenue | USD |
| `RevenueFromContractWithCustomerExcludingAssessedTax` | Post-ASC-606 revenue | USD |
| `NetIncomeLoss` | Bottom-line net income | USD |
| `EarningsPerShareBasic` / `EarningsPerShareDiluted` | EPS | USD/share |
| `CashAndCashEquivalentsAtCarryingValue` | Cash & equivalents | USD |
| `Assets` / `Liabilities` / `StockholdersEquity` | Balance sheet totals | USD |
| `PropertyPlantAndEquipmentNet` | Net PP&E | USD |
| `LongTermDebtNoncurrent` | Long-term debt | USD |
| `NetCashProvidedByUsedInOperatingActivities` | Operating cash flow | USD |
| `PaymentsToAcquirePropertyPlantAndEquipment` | Capex | USD |

**Caveat**: concept naming varies across filers and has migrated over time
(pre- and post-ASC-606). Query `--action facts` without `--concept` first to
enumerate what's actually tagged for a given issuer.

### 3.2 Taxonomy reference

Official us-gaap taxonomy documentation:
<https://xbrl.us/xbrl-taxonomy/2024-us-gaap/>

FASB taxonomy index (canonical concept list):
<https://xbrl.fasb.org/>

### 3.3 Fact record shape

A single `companyconcept` response returns a JSON structure like:

```json
{
  "cik": 320193,
  "taxonomy": "us-gaap",
  "tag": "Revenues",
  "units": {
    "USD": [
      {"end": "2024-09-28", "val": 391035000000, "accn": "0000320193-24-000123",
       "fy": 2024, "fp": "FY", "form": "10-K", "filed": "2024-11-01"},
      ...
    ]
  }
}
```

Each fact carries `accn` (accession), `form` (10-K / 10-Q), `fy`/`fp` (fiscal
year / period), and `filed` (filing date) so downstream analysis can
reconstruct the filing-of-record.

## 4. Narrative Item-Section Extraction

XBRL covers the numerics; narrative text (MD&A, Business, Risk Factors)
requires HTML parsing.

### 4.1 Parsing methodology

`sec_edgar_client.py` downloads the filing's primary document and:

1. Strips HTML tags to plain text.
2. Runs regex `^\s*Item\s+(\d+[A-Z]?)\.\s*(.{2,150}?)\s*$` (multiline) to
   locate every `Item N.` or `Item NA.` header.
3. De-duplicates TOC entries vs body bodies by keeping **the longest span**
   per unique Item number (TOC entries are short; body spans long).
4. Emits `{"Item 1. Business": "…", "Item 1A. Risk Factors": "…", …}`.

Cache is permanent (filings don't change once accepted).

### 4.2 10-K sections reliably parsed

- Item 1 Business
- Item 1A Risk Factors
- Item 7 MD&A
- Item 7A Quantitative & Qualitative Disclosures about Market Risk

### 4.3 10-Q sections reliably parsed

- Item 1 Financial Statements
- Item 2 MD&A

### 4.4 Item 8 caveat

**Item 8 (Financial Statements & Supplementary Data) body text is often a
stub** pointing to a separate XBRL exhibit or supplemental document. The
numeric tables themselves live in the XBRL instance document, not the
primary HTML.

**Guidance**: do NOT rely on Item 8 narrative for numbers. Use
`--action facts --concept <us-gaap name>` instead to pull structured values.
The Item 8 text is still useful for audit opinion summary and accounting
policy callouts.

## 5. CLI Reference

All four actions supported by `sec_edgar_client.py`:

### 5.1 `--action cik` — ticker → CIK lookup

```bash
uv run sec_edgar_client.py --ticker NVDA --action cik
# → {"ticker": "NVDA", "cik": 1045810, "name": "NVIDIA CORP"}
```

### 5.2 `--action facts` — XBRL company facts

Full companyfacts (all concepts):

```bash
uv run sec_edgar_client.py --ticker NVDA --action facts
```

Single concept time-series (recommended for targeted pulls):

```bash
uv run sec_edgar_client.py --ticker NVDA --action facts --concept Revenues
uv run sec_edgar_client.py --ticker NVDA --action facts --concept NetIncomeLoss
uv run sec_edgar_client.py --ticker NVDA --action facts --concept PropertyPlantAndEquipmentNet
```

### 5.3 `--action filings` — recent filings index

Default (all forms, default limit):

```bash
uv run sec_edgar_client.py --ticker NVDA --action filings --limit 20
```

Filtered by form family (most common fundamental-analysis slice):

```bash
uv run sec_edgar_client.py --ticker NVDA --action filings --forms 10-K,10-Q,8-K --limit 10
```

Insider + institutional signal:

```bash
uv run sec_edgar_client.py --ticker NVDA --action filings --forms 4,13F-HR --limit 30
```

Governance:

```bash
uv run sec_edgar_client.py --ticker NVDA --action filings --forms "DEF 14A" --limit 5
```

### 5.4 `--action narrative` — parse Item sections

Requires an accession from a prior `--action filings` call:

```bash
uv run sec_edgar_client.py --accession 0001045810-24-000316 --action narrative
```

Returns `{"Item 1. Business": "…", "Item 1A. Risk Factors": "…", …}` keyed
by detected Item header. Cache is permanent.

## 6. Compliance Notes

- Always leave the `User-Agent` in identified form; sharing the client
  implies the email address is real.
- Respect the 10 req/sec ceiling; batch callers should stay around 5–7 req/sec
  average.
- Do not bypass the cache layer — it reduces load on SEC infrastructure and
  satisfies the Fair Access policy's spirit.
- For programmatic pulls exceeding a few hundred filings, consider the
  bulk data endpoint (`/Archives/edgar/Feed/`) instead — not wrapped by this
  client.
