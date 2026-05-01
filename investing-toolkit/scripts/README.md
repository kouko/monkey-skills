# investing-toolkit Scripts — canonical client adapters

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Python data adapters for fetching market and macro data.

## Role in v2.0.0 architecture

This `scripts/` directory is the **canonical home** for every shared client adapter (`yfinance_client.py`, `fred_client.py`, `nbs_client.py`, `akshare_client.py`, …). Under the v2.0.0 three-layer architecture, each `data-{country}` skill owns a **functional copy** of the clients it needs inside its own `scripts/` folder. Per Anthropic's skill-folder rule, those copies must physically live inside the consuming skill — but they remain MD5-identical to the canonical here.

- **Canonical SoT (single source of truth)**: `investing-toolkit/scripts/*_client.py`
- **Functional copies**: `investing-toolkit/skills/data-{us,jp,tw,kr,cn}/scripts/*_client.py`
- **Sync helper**: `bash scripts/sync-clients.sh` propagates canonical → all copies; `--check` reports drift and exits 1
- **CI guard**: `.github/workflows/check-script-sync.yml` enforces MD5 equality for the duplicated set; drift is a CI-blocking event in v2.0.0
- **Architecture decision**: [`../docs/adr/0001-data-analysis-report-layers.md`](../docs/adr/0001-data-analysis-report-layers.md) §Acceptable Duplications

If you change a client here, run `bash scripts/sync-clients.sh` before committing. If you add a client consumed by a new `data-{country}` skill, add the skill to the appropriate `*_TARGETS` array in `sync-clients.sh` **and** mirror it in `.github/workflows/check-script-sync.yml`.

## Setup

**Step 1 — Install uv** (one-time, auto-detects Homebrew):

```bash
sh investing-toolkit/scripts/setup.sh
```

That's it. The scripts use `uv run` with inline dependencies — no manual
`pip install` needed.

<details>
<summary>Manual install options</summary>

```bash
# macOS with Homebrew
brew install uv

# macOS / Linux without Homebrew
curl -LsSf https://astral.sh/uv/install.sh | sh
```

</details>

## Scripts

### yfinance_client.py

Fetches US stock price history and company info via yfinance (unofficial).

**Auth**: None required.  
**Cache**: `~/.cache/investing-toolkit/yfinance/` — 1h TTL.

```bash
# OHLCV price history
uv run yfinance_client.py --ticker AAPL --period 1y
uv run yfinance_client.py --ticker NVDA --period 6mo --interval 1wk

# Company info (PE, PB, market cap, EV — NOT financials)
uv run yfinance_client.py --ticker MSFT --action info

# Bypass cache
uv run yfinance_client.py --ticker TSLA --period 1y --no-cache
```

**Warning**: yfinance is an unofficial scraper. It provides **price data only**.
Do NOT use for financial statements (income statement, balance sheet, cash flow).
Use SEC EDGAR directly for US financial filings.

**yfinance does not support Taiwan financial statements**. Use FinMind for Taiwan
financials (available in investing-toolkit v1.1.0).

---

### fred_client.py

Fetches macroeconomic data from Federal Reserve Economic Data (FRED).

**Auth**: Set `FRED_API_KEY` env var for higher rate limits (free API key).  
Without key: ~100 requests/day before 429 throttle.  
**Cache**: `~/.cache/investing-toolkit/fred/` — 24h TTL.

```bash
# Single series
uv run fred_client.py --series T10Y2Y --periods 24

# Multiple series (comma-separated)
uv run fred_client.py --series DGS10,DGS2,CPIAUCSL,GDPC1 --periods 12

# Bypass cache
uv run fred_client.py --series FEDFUNDS --periods 24 --no-cache
```

**Key series for macro regime diagnosis**:

| Series | What it measures |
|--------|-----------------|
| `T10Y2Y` | 10Y–2Y yield spread (inversion signal) |
| `DGS10` | 10-Year Treasury yield |
| `DGS2` | 2-Year Treasury yield |
| `CPIAUCSL` | CPI all urban consumers (YoY for inflation direction) |
| `CPILFESL` | Core CPI (excludes food & energy) |
| `GDPC1` | Real GDP (quarterly) |
| `INDPRO` | Industrial Production Index |
| `FEDFUNDS` | Federal Funds Rate |
| `UNRATE` | Unemployment Rate |

Get your free FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html

---

## Output Format

All scripts output **JSON to stdout**. Errors also output JSON with an `"error"` key
and exit with code 1.

```json
{
  "ticker": "AAPL",
  "period": "1y",
  "fetched_at": "2026-04-16T10:00:00Z",
  "_cache": "miss",
  "latest_close": 195.42,
  "latest_date": "2026-04-15",
  "rows": 252,
  "data": [...]
}
```

## CasualMarket MCP (Taiwan real-time — external)

For Taiwan real-time market data, install CasualMarket separately:

```bash
claude plugin add casualmarket
```

CasualMarket is NOT bundled with investing-toolkit. It runs as an MCP server
and provides live TWSE/OTC quotes, 外資動向, and valuation multiples.
See: https://github.com/sacahan/CasualMarket

---

### finmind_client.py

Fetches Taiwan equity data from the FinMind API.

**Auth**: Set `FINMIND_API_TOKEN` env var for higher rate limits (free registration).  
Without token: 300 req/hr. With token: 600 req/hr.  
**Cache**: `~/.cache/investing-toolkit/finmind/` — 6h TTL.

```bash
# Taiwan stock price (OHLCV daily) — ticker = 4-digit code
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockPrice --date-start 2025-04-01

# 三大法人買賣超 (last 3 months)
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockInstitutionalInvestorsBuySell --date-start 2026-01-01

# 月營收 (last 12 months)
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockMonthRevenue --date-start 2025-01-01

# 董監持股 + 質押率
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockHoldingSharesPer --date-start 2025-01-01

# 融資融券 (last 3 months)
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockMarginPurchaseShortSale --date-start 2026-01-01

# Multiple datasets in one call
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockPrice,TaiwanStockMonthRevenue --date-start 2025-01-01

# Bypass cache
uv run finmind_client.py --ticker 2330 --dataset TaiwanStockPrice --date-start 2025-04-01 --no-cache
```

**Ticker format**: 4-digit code only. `.TW` and `.TWO` suffixes are stripped automatically.

**Supported datasets**:

| Dataset ID | Content | Publication lag |
|-----------|---------|-----------------|
| `TaiwanStockPrice` | OHLCV daily | ~15 min (T+0) |
| `TaiwanStockInstitutionalInvestorsBuySell` | 三大法人買賣超 | T+1 after 18:00 |
| `TaiwanStockMonthRevenue` | 月營收 | Within 10th of following month |
| `TaiwanStockHoldingSharesPer` | 董監持股 + 質押率 | Quarterly |
| `TaiwanStockMarginPurchaseShortSale` | 融資融券餘額 | T+1 after 18:00 |
| `TaiwanStockFinancialStatements` | 財務報表（季頻）| Quarterly |
| `TaiwanStockProfitLossStatement` | 損益表（季頻） | Quarterly |

Get a free FinMind API token: https://finmindtrade.com

---
