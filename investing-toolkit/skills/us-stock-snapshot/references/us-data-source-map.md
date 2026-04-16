# US Data Source Map

## Price & Market Data

| Data | Source | Script | Notes |
|------|--------|--------|-------|
| OHLCV (daily/weekly/monthly) | yfinance | `yfinance_client.py --ticker AAPL --period 1y` | Unofficial; price-only |
| Intraday quotes | yfinance | `--period 1d --interval 5m` | Rate-limited; best-effort |
| Market cap, PE, PB, EV/EBITDA | yfinance `info` | `--action info` | Stale by ≤1 day |
| 52-week high/low | yfinance `info` | `--action info` | — |
| Short interest | yfinance `info` | `--action info` | — |

**Warning**: yfinance does NOT provide financial statements (income statement, balance sheet, cash flow). Use SEC EDGAR for financials.

## Financial Statements

| Data | Source | Notes |
|------|--------|-------|
| 10-K (annual report) | SEC EDGAR | `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` |
| 10-Q (quarterly report) | SEC EDGAR | Same XBRL endpoint |
| CIK lookup | EDGAR company search | `https://efts.sec.gov/LATEST/search-index?q={ticker}&dateRange=custom` |
| DEF 14A (proxy, exec comp) | SEC EDGAR full-text search | — |
| 8-K (material events) | SEC EDGAR full-text search | — |

## Macro & Economic Data (FRED)

| Series | FRED ID | Frequency | Notes |
|--------|---------|-----------|-------|
| 10-Year Treasury yield | DGS10 | Daily | Risk-free rate proxy |
| 2-Year Treasury yield | DGS2 | Daily | — |
| 10Y–2Y spread | T10Y2Y | Daily | Yield curve inversion signal |
| Fed Funds Rate | FEDFUNDS | Monthly | Policy rate |
| CPI (all urban) | CPIAUCSL | Monthly | Inflation; ~2-3 week publication lag |
| Core CPI | CPILFESL | Monthly | Excludes food & energy |
| Real GDP (QoQ SAAR) | GDPC1 | Quarterly | ~1 month publication lag |
| Industrial Production | INDPRO | Monthly | Leading growth indicator |
| Unemployment Rate | UNRATE | Monthly | Lagging indicator |
| S&P 500 P/E (Shiller CAPE) | MULTPL series | Monthly | Via external source; FRED has raw data |

**FRED API key**: Set `FRED_API_KEY` env var. Without key, API returns 429 after ~100 requests/day.

## Equity Research Databases

| Source | Access | Best For |
|--------|--------|---------|
| SEC EDGAR | Free, unlimited | US filings, financials |
| FRED | Free, API key optional | Macro, rates, economic data |
| Alpha Vantage | Free (25 req/day), $49.99/mo+ | Technical indicators, adjusted prices |
| Finnhub | Free (60 req/min), paid | Real-time quotes, news sentiment, analyst ratings |
| Morningstar | $17,500/yr | Fund ratings, deep financials (not practical for personal use) |

## Script Usage Examples

```bash
# Price history
python3 scripts/yfinance_client.py --ticker NVDA --period 1y

# Company info (PE, PB, market cap)
python3 scripts/yfinance_client.py --ticker AAPL --action info

# FRED yield curve
python3 scripts/fred_client.py --series T10Y2Y --periods 24

# Multiple FRED series for regime snapshot
python3 scripts/fred_client.py --series DGS10,DGS2,CPIAUCSL,GDPC1 --periods 8
```
