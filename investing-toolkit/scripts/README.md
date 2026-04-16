# investing-toolkit Scripts

Python data adapters for fetching market and macro data.

## Setup

```bash
pip install -r requirements.txt
```

Or with uv (recommended):

```bash
uv pip install -r requirements.txt
# or as an inline script dependency — see individual script headers
```

## Scripts

### yfinance_client.py

Fetches US stock price history and company info via yfinance (unofficial).

**Auth**: None required.  
**Cache**: `~/.cache/investing-toolkit/yfinance/` — 1h TTL.

```bash
# OHLCV price history
python3 yfinance_client.py --ticker AAPL --period 1y
python3 yfinance_client.py --ticker NVDA --period 6mo --interval 1wk

# Company info (PE, PB, market cap, EV — NOT financials)
python3 yfinance_client.py --ticker MSFT --action info

# Bypass cache
python3 yfinance_client.py --ticker TSLA --period 1y --no-cache
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
python3 fred_client.py --series T10Y2Y --periods 24

# Multiple series (comma-separated)
python3 fred_client.py --series DGS10,DGS2,CPIAUCSL,GDPC1 --periods 12

# Bypass cache
python3 fred_client.py --series FEDFUNDS --periods 24 --no-cache
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

## Planned (v1.1.0)

- `finmind_client.py` — Taiwan financial data (三大法人, 月營收, 融資融券, 董監持股)
  - Auth: `FINMIND_API_TOKEN` env var (optional; anonymous = 300 req/hr)
