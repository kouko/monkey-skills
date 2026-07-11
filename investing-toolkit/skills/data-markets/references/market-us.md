# Market reference — US

Distilled from the pre-migration `data-us` skill's `SKILL.md`. All clients
below are byte-identical migrations (cache-layer only) — see
`references/migration-grounding.md` for the external-surface grounding.

## Sources + authority tiers

| Source | Tier | Client | Returns |
|---|---|---|---|
| yfinance (unofficial) | Tier 2 | `yfinance_client.py` | OHLCV history, `info` dict (PE/PB/marketCap/beta/dividendYield/sector) |
| SEC EDGAR (`data.sec.gov`) | **Tier A primary** | `sec_edgar_client.py` | 10-K/10-Q/8-K filing index, XBRL us-gaap facts, Item-section narrative |
| FRED (CSV + keyless `fredgraph` fallback) | Tier A | `fred_client.py` | Rates / inflation / growth / nowcast / real-rates / swap-spreads time series |

US is the one market in this skill with a real Tier-A equity-financials
source (SEC EDGAR XBRL) — do not use yfinance `financials` for
verdict-grade memos; always route through `memo-fetch` for the SEC path.

## API keys + rate limits

| Env var | Required? | Effect |
|---|---|---|
| `FRED_API_KEY` | optional | CSV endpoint works keyless; key only unlocks the JSON API. |

SEC EDGAR is rate-limited (`memo-fetch` sequences its 4 fetches rather
than parallelizing, ~10 req/s ceiling); a 429 surfaces as
`{"error": "SEC EDGAR rate-limited (429) after retries"}`. FRED has a
shared ~120 req/min limit across all callers.

## Caveats

- yfinance financials (income statement / balance sheet / cash flow) are
  explicitly NOT to be used for verdict-grade memos — SEC EDGAR is the
  Tier-A source for that.
- FRED series carry publication lags: 1 day (Treasury yields), 2–3 weeks
  (CPI/RSAFS), 1–2 months (GDP/CSUSHPISA). Check `latest.date` downstream.
- `memo-fetch` is heavy (4 sequential fetches) and single-ticker only by
  design.

## Error dialect

US fails **per-section**: a client failure surfaces as `{"error": ...,
"script": ..., "stderr": ...}` nested directly under the top-level
section key it replaces (`company_info`, `sec_filings`, etc.), or for
batch packs, as an empty `tickers: {}` map plus a top-level `error`
field — the `tickers` map itself never contains an `_error` sentinel, so
consumers may iterate `tickers.items()` safely. Subprocess timeouts
report `{"error": "client timeout after 300s", "_cmd": [...],
"_returncode": -1}`.

## Regime-pack FRED groups

`rates` (T10Y2Y, DGS10, DGS2, FEDFUNDS) · `inflation` (CPIAUCSL,
CPILFESL) · `growth` (GDPC1, INDPRO) · `nowcast` (GDPNOW, CFNAI,
USALOLITOAASTSAM) · `wei` (WEI) · `real_rates` (T5YIE, T10YIE, DFII5,
DFII10) · `swap_spreads` (DGS3MO, SOFR30DAYAVG).
