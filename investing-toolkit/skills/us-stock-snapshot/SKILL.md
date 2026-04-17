---
name: us-stock-snapshot
description: >-
  Fetch US stock price and company info via yfinance and compose a structured
  snapshot card. Returns price history, 52-week range, valuation multiples,
  market cap, beta, and dividend yield as a fixture ready for handoff to
  domain-teams:investing-team. Data layer only — no analysis or verdict.
  米国株スナップショット取得。美股快照擷取。
---

# US Stock Snapshot

Fetches US equity data and outputs a structured snapshot card. This skill is
**data-only** — it does not analyze, score, or generate investment verdicts.
The card is designed for immediate handoff to `domain-teams:investing-team`
for full analysis.

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | e.g. AAPL, NVDA, MSFT |
| `period` | no | `1y` | yfinance period: 1mo, 3mo, 6mo, 1y, 2y, 5y |

## How It Works

### Step 1 — Launch data-fetcher agent

Launch `../../agents/data-fetcher.md` with two parallel fetch requests:

```
### Task
Fetch stock price history and company info for {ticker}. Return structured JSON.
Do not analyze or interpret.

### Scripts
base_path: {absolute path to investing-toolkit/scripts/}

### Fetch Requests
- uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --period {period}
- uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --action info

### Output Format
{
  "price_history": {...},
  "company_info": {...}
}
```

### Step 2 — Compose snapshot card

Extract from data-fetcher JSON and render the card below.

**Field mapping:**

| Card field | JSON path |
|------------|-----------|
| close | `price_history.latest_close` |
| date | `price_history.latest_date` |
| 52W low | `price_history` min of `low` column over period |
| 52W high | `price_history` max of `high` column over period |
| vs 52W High % | `(close - 52W_high) / 52W_high × 100` |
| P/E | `company_info.trailingPE` |
| P/B | `company_info.priceToBook` |
| market cap | `company_info.marketCap / 1e9` (billions) |
| shares out | `company_info.sharesOutstanding / 1e6` (millions) |
| beta | `company_info.beta` |
| div yield | `company_info.dividendYield × 100` |

If a field is absent in JSON, render `N/A`.

## Output Format

```
## {TICKER} Snapshot — {date}

**Price**: ${close} | 52W: ${low}–${high} | vs 52W High: {pct}%
**Valuation**: P/E {pe} | P/B {pb} | EV/EBITDA (N/A — use SEC EDGAR for financials)
**Market Cap**: ${mcap}B | Shares Out: {shares}M
**Beta**: {beta} | Div Yield: {div}%

_Fetched via yfinance (unofficial). For financial statements, use SEC EDGAR._
```

**Example:**

```
## AAPL Snapshot — 2026-04-15

**Price**: $195.42 | 52W: $164.08–$237.23 | vs 52W High: -17.6%
**Valuation**: P/E 28.4 | P/B 45.2 | EV/EBITDA (N/A — use SEC EDGAR for financials)
**Market Cap**: $3,000B | Shares Out: 15,350M
**Beta**: 1.21 | Div Yield: 0.55%

_Fetched via yfinance (unofficial). For financial statements, use SEC EDGAR._
```

## Warnings

### yfinance does NOT provide financial statements

yfinance is an unofficial scraper. It returns price/quote fields but does NOT
provide income statement, balance sheet, or cash flow data.

For financial statements, use **SEC EDGAR** (free, official):

```
https://data.sec.gov/api/xbrl/companyfacts/{CIK}.json
```

XBRL company facts endpoint returns full GAAP financials in JSON — revenue,
net income, total assets, long-term debt, operating cash flow.

### Taiwan tickers — price/info only

For tickers with `.TW` or `.TWO` suffix, yfinance returns price history and
basic quote fields only. Financial statements for Taiwan-listed companies are
not available via yfinance or SEC EDGAR.

For full Taiwan financial data (income statement, balance sheet, cash flow),
use **FinMind** — planned in `v1.1.0`. Until then, this skill returns price
and info fields only for Taiwan tickers, with a note in the card:

```
_Taiwan ticker: price/info only. For financial statements, use FinMind (v1.1.0)._
```

## Cross-Plugin Handoff

After the snapshot card is produced, pass it to `domain-teams:investing-team`
as the data fixture for full analysis:

```
Workflow: us-stock-snapshot → macro-regime-snapshot → investment-memo-writer
```

1. `us-stock-snapshot` (this skill) — equity price + valuation fixture
2. `macro-regime-snapshot` — macro regime diagnosis (yield curve, CPI, GDP)
3. `domain-teams:investing-team` → `investment-memo-writer` — variant perception
   thesis, pre-mortem, conviction grade, full investment memo

Pass the snapshot card verbatim as the `### Input` section when launching the
next skill.
