---
name: us-stock-snapshot
description: >-
  Fetch US stock data via yfinance (price/valuation snapshot layer) + SEC EDGAR
  (10-K/10-Q/8-K + XBRL facts + Item-section narrative fundamental layer) and
  compose a structured snapshot card. Returns price history, 52-week range,
  valuation multiples, market cap, beta, dividend yield, plus SEC filing
  references for domain-teams:investing-team handoff. Data layer only — no
  analysis or verdict. 米国株スナップショット取得。美股快照擷取。
---

# US Stock Snapshot

> **Dual-mode execution (v1.14.0+, corrected v1.16.1)**: The `uv run scripts/...` commands below are canonical. Matching MCP tools are registered alongside (`investing-toolkit:*` namespace) — Claude may use either; both return identical JSON. ⚠️ **Cowork limitation**: MCP does NOT bypass Cowork sandbox URL allowlist (v1.14.0 premise was wrong, confirmed v1.16.1). Use Claude Code CLI. Full catalog: [`docs/mcp-setup.md`](../../docs/mcp-setup.md).

Fetches US equity data across **two layers** and outputs a structured snapshot
card. This skill is **data-only** — it does not analyze, score, or generate
investment verdicts. The card is designed for immediate handoff to
`domain-teams:investing-team` for full analysis.

## Data Layers

| Layer | Source | Script | Returns |
|-------|--------|--------|---------|
| **Snapshot** | yfinance (unofficial) | `yfinance_client.py` | Price history, 52W range, PE/PB, market cap, beta, dividend yield |
| **Fundamental** | SEC EDGAR (`data.sec.gov`, official) | `sec_edgar_client.py` | 10-K / 10-Q / 8-K / Form 4 / 13F / S-1 / DEF 14A filings, XBRL us-gaap facts, Item-section narrative |

v1.13.0 adds SEC EDGAR to close Pattern C NVDA demo **data gap #1** (SEC EDGAR
missing). The fundamental layer unlocks revenue-quality, segment-mix,
customer-concentration, insider-flow, and governance analysis downstream.

See `references/sec-edgar-guide.md` for full SEC EDGAR API reference, form
coverage, XBRL taxonomy basics, and rate-limit / compliance guidance.

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | e.g. AAPL, NVDA, MSFT |
| `period` | no | `1y` | yfinance period: 1mo, 3mo, 6mo, 1y, 2y, 5y |
| `forms` | no | `10-K,10-Q,8-K` | SEC EDGAR form filter (see reference doc for full list) |
| `filings_limit` | no | `8` | Recent filings to fetch |

## How It Works

### Step 1 — Launch data-fetcher agent (parallel fetches)

Launch `../../agents/data-fetcher.md` with **snapshot + fundamental** fetch
requests in parallel:

```
### Task
Fetch stock snapshot (yfinance) + SEC EDGAR fundamental layer for {ticker}.
Return structured JSON. Do not analyze or interpret.

### Scripts
base_path: {absolute path to investing-toolkit/scripts/}

### Fetch Requests
# Snapshot layer
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --period {period}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --action info

# Fundamental layer
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/sec_edgar_client.py --ticker {ticker} --action filings --forms {forms} --limit {filings_limit}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/sec_edgar_client.py --ticker {ticker} --action facts

### Output Format
{
  "price_history": {...},
  "company_info": {...},
  "sec_filings": [...],
  "sec_facts": {...}
}
```

For Pattern C deep-dive, optionally add an extra narrative fetch for the most
recent 10-K accession surfaced in `sec_filings`:

```
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/sec_edgar_client.py --accession {10K_accession} --action narrative
```

### Step 2 — Compose snapshot card

Extract from data-fetcher JSON and render the card below.

**Snapshot field mapping:**

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

**Fundamental field mapping (new in v1.13.0):**

| Card field | JSON path |
|------------|-----------|
| latest 10-K | `sec_filings` first entry where `form == "10-K"` → `filingDate`, `accession` |
| latest 10-Q | `sec_filings` first entry where `form == "10-Q"` → `filingDate`, `accession` |
| recent 8-K count | count of `sec_filings` where `form == "8-K"` in last 90 days |
| Revenues (TTM) | `sec_facts.facts.us-gaap.Revenues.units.USD` last 4 quarters sum |
| NetIncomeLoss (TTM) | `sec_facts.facts.us-gaap.NetIncomeLoss.units.USD` last 4 quarters sum |

If a field is absent in JSON, render `N/A`.

## Output Format

```
## {TICKER} Snapshot — {date}

**Price**: ${close} | 52W: ${low}–${high} | vs 52W High: {pct}%
**Valuation**: P/E {pe} | P/B {pb} | Revenue TTM: ${rev_ttm}B | Net Income TTM: ${ni_ttm}B
**Market Cap**: ${mcap}B | Shares Out: {shares}M
**Beta**: {beta} | Div Yield: {div}%

**SEC Filings** (via data.sec.gov):
- Latest 10-K: {10k_date} — accession `{10k_accession}`
- Latest 10-Q: {10q_date} — accession `{10q_accession}`
- Recent 8-K (90d): {count_8k}

_Snapshot via yfinance (unofficial); fundamentals via SEC EDGAR (official)._
```

**Example:**

```
## AAPL Snapshot — 2026-04-15

**Price**: $195.42 | 52W: $164.08–$237.23 | vs 52W High: -17.6%
**Valuation**: P/E 28.4 | P/B 45.2 | Revenue TTM: $391.0B | Net Income TTM: $93.7B
**Market Cap**: $3,000B | Shares Out: 15,350M
**Beta**: 1.21 | Div Yield: 0.55%

**SEC Filings** (via data.sec.gov):
- Latest 10-K: 2025-11-01 — accession `0000320193-25-000123`
- Latest 10-Q: 2026-02-01 — accession `0000320193-26-000045`
- Recent 8-K (90d): 3

_Snapshot via yfinance (unofficial); fundamentals via SEC EDGAR (official)._
```

## Warnings

### yfinance is the snapshot layer; SEC EDGAR is the fundamental layer

yfinance is an unofficial scraper — it returns price/quote fields but does NOT
provide income statement, balance sheet, or cash flow data. For those, use
the **SEC EDGAR fundamental layer** (v1.13.0+):

- **Structured (XBRL facts)** — `sec_edgar_client.py --action facts [--concept Revenues]`
- **Filings index** — `sec_edgar_client.py --action filings --forms 10-K,10-Q,8-K`
- **Narrative (Item sections)** — `sec_edgar_client.py --accession {id} --action narrative`

Full form coverage, XBRL taxonomy, and parsing caveats in
`references/sec-edgar-guide.md`.

### Taiwan tickers — use `taiwan-stock-snapshot`

Tickers with `.TW` or `.TWO` suffix are **not** handled by this skill. Use
`taiwan-stock-snapshot` (MOPS JSON API + TWSE OpenAPI, v1.13.0+).

## Cross-Plugin Handoff

After the snapshot card is produced, pass it to `domain-teams:investing-team`
as the data fixture for full analysis:

```
Workflow: us-stock-snapshot → macro-regime-snapshot → investment-memo-writer
```

1. `us-stock-snapshot` (this skill) — equity snapshot + SEC fundamental fixture
2. `macro-regime-snapshot` — macro regime diagnosis (yield curve, CPI, GDP)
3. `domain-teams:investing-team` → `investment-memo-writer` — variant perception
   thesis, pre-mortem, conviction grade, full investment memo

Pass the snapshot card verbatim as the `### Input` section when launching the
next skill. SEC filing accession IDs carried in the card enable
`investing-team` to request deeper narrative parsing on demand.
