---
name: korea-macro
description: >-
  Fetch Korea macroeconomic indicators via FinanceDataReader (BOK ECOS-KEYSTAT).
  Data layer only — no analysis or regime mapping.
  Returns structured JSON with latest values and direction for rates, inflation,
  growth, labor, trade, money, sentiment, markets, fx, and real estate groups.
  한국 매크로 지표 취득 (한국은행 ECOS-KEYSTAT via FinanceDataReader).
  韓國總經指標擷取（韓國銀行 ECOS-KEYSTAT）。
---

# Korea Macro

Fetches Korea macroeconomic indicators from the Bank of Korea (BOK) Economic
Statistics System (ECOS) via FinanceDataReader. Single script, single source,
no API key required.

- **FinanceDataReader** (`fdr_client.py`) — BOK ECOS-KEYSTAT integration:
  rates, inflation, growth, labor, trade, money, sentiment, markets, FX,
  real estate (27 presets via ECOS-KEYSTAT, 1 via FRED CSV)

This skill is **data-only**. The output is designed for handoff to
`macro-regime-snapshot` or `domain-teams:investing-team`.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `--indicators` | no | `all` | Comma-separated: `rates`, `inflation`, `growth`, `labor`, `trade`, `money`, `sentiment`, `markets`, `fx`, `realestate`, or `all` |

---

## Indicator Groups

### rates

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| policy-rate | K051 | BOK Base Rate (기준금리) | Daily |
| call-rate | K052 | Call Rate Overnight (콜금리 1일) | Daily |
| cd-91d | K053 | CD 91-Day Rate (CD 91일) | Daily |
| treasury-3y | K056 | Treasury Bond 3Y (국고채 3년) | Daily |
| treasury-5y | K062 | Treasury Bond 5Y (국고채 5년) | Daily |
| corp-bond-3y | K057 | Corporate Bond 3Y AA- (회사채 AA-) | Daily |

### inflation

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| cpi | K401 | CPI Total Index (소비자물가 총지수) | Monthly |
| core-cpi | K405 | Core CPI excl. food & energy (농산물및석유류제외) | Monthly |
| ppi | K402 | PPI Total Index (생산자물가 총지수) | Monthly |
| import-pi | K403 | Import Price Index (수입물가 총지수) | Monthly |
| export-pi | K404 | Export Price Index (수출물가 총지수) | Monthly |

### growth

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| gdp-qoq | K258 | GDP Real QoQ SA% (실질 전기비) | Quarterly |
| gdp-nominal | K257 | GDP Nominal (명목 시장가격) | Quarterly |
| ipi | K220 | All-Industry Production Index (전산업생산지수) | Monthly |
| manufacturing | K201 | Manufacturing Production Index (제조업 생산지수) | Monthly |

### labor

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| unemployment | K303 | Unemployment Rate % (실업률) | Monthly |
| employment-rate | K304 | Employment Rate % (고용률) | Monthly |

### trade

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| current-account | K351 | Current Account (경상수지 백만USD) | Monthly |
| terms-of-trade | K360 | Terms of Trade Index (순상품교역조건지수) | Monthly |

### money

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| m2 | K003 | M2 Broad Money (광의통화 M2 평잔) | Monthly |
| household-credit | K007 | Household Credit (가계신용) | Quarterly |

### sentiment

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| consumer-sentiment | K252 | Consumer Sentiment Index (소비자심리지수) | Monthly |
| economic-sentiment | K269 | Economic Sentiment Index (경제심리지수) | Monthly |
| leading-cycle | K254 | Leading CI Cyclical Component (선행지수순환변동치) | Monthly |
| coincident-cycle | K253 | Coincident CI Cyclical Component (동행지수순환변동치) | Monthly |

### markets

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| kospi | K101 | KOSPI Index (코스피지수) | Daily |
| kosdaq | K102 | KOSDAQ Index (코스닥지수) | Daily |

### fx

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| krw-usd | DEXKOUS | KRW/USD Exchange Rate (원달러 환율) | Daily (via FRED) |

### realestate

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| housing-price | K407 | Housing Price Index (주택매매가격지수) | Monthly |

---

## How It Works

### Step 1 — Resolve series list

| Input | Presets |
|-------|--------|
| `rates` | policy-rate, call-rate, cd-91d, treasury-3y, treasury-5y, corp-bond-3y |
| `inflation` | cpi, core-cpi, ppi, import-pi, export-pi |
| `growth` | gdp-qoq, gdp-nominal, ipi, manufacturing |
| `labor` | unemployment, employment-rate |
| `trade` | current-account, terms-of-trade |
| `money` | m2, household-credit |
| `sentiment` | consumer-sentiment, economic-sentiment, leading-cycle, coincident-cycle |
| `markets` | kospi, kosdaq |
| `fx` | krw-usd |
| `realestate` | housing-price |

### Step 2 — Launch data-fetcher agents

```
### Fetch Requests (rates batch)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fdr_client.py --preset policy-rate,call-rate,cd-91d,treasury-3y,treasury-5y,corp-bond-3y

### Fetch Requests (inflation batch)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fdr_client.py --preset cpi,core-cpi,ppi,import-pi,export-pi

### Fetch Requests (growth + labor)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fdr_client.py --preset gdp-qoq,gdp-nominal,ipi,manufacturing,unemployment,employment-rate

### Fetch Requests (trade + money + sentiment)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fdr_client.py --preset current-account,terms-of-trade,m2,household-credit,consumer-sentiment,economic-sentiment,leading-cycle,coincident-cycle

### Fetch Requests (markets + fx + real estate)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fdr_client.py --preset kospi,kosdaq,krw-usd,housing-price
```

### Step 3 — Merge into unified output

All data points retain `_source`: `"fdr_ecos"` (or `"fred"` for krw-usd).

---

## Reference

- `references/indicator-index.md` — Quick lookup (trilingual)
- `references/indicators-rates.md` — 금리 Rates
- `references/indicators-inflation.md` — 물가 Inflation
- `references/indicators-growth.md` — 성장 Growth
- `references/indicators-labor.md` — 고용 Labor
- `references/indicators-trade.md` — 무역 Trade
- `references/indicators-sentiment.md` — 경기 Sentiment / Cycle
- `references/indicators-other.md` — Markets, FX, Money, Real Estate
- `references/sources.md` — Primary sources

---

## Limitations

### Publication lags

| Series | Typical lag |
|--------|-------------|
| BOK Base Rate (K051) | 1 business day (daily) |
| Call Rate, CD, Bonds (K052-K062) | 1 business day (daily) |
| KOSPI, KOSDAQ (K101-K102) | 1 business day (daily) |
| KRW/USD via FRED (DEXKOUS) | 1-2 business days |
| CPI, Core CPI (K401, K405) | ~3-4 weeks after month-end |
| PPI (K402) | ~4 weeks after month-end |
| Import/Export PI (K403, K404) | ~3-4 weeks after month-end |
| IPI, Manufacturing (K220, K201) | ~5-6 weeks after month-end |
| Unemployment (K303) | ~3 weeks after month-end |
| Current Account (K351) | ~6 weeks after month-end |
| GDP (K257, K258) | ~8 weeks after quarter-end |
| M2 (K003) | ~4 weeks after month-end |
| Household Credit (K007) | ~6 weeks after quarter-end |
| Consumer/Economic Sentiment (K252, K269) | ~1 week after month-end |
| Leading/Coincident CI (K254, K253) | ~5-6 weeks after month-end |
| Housing Price Index (K407) | ~4 weeks after month-end |

### FinanceDataReader dependency

`fdr_client.py` uses `finance-datareader==0.9.90` which accesses BOK ECOS
via an internal endpoint (`ecos.bok.or.kr/serviceEndpoint`). This is not a
documented public API — it works because FinanceDataReader uses the same
endpoint as the ECOS website itself. A BOK infrastructure change could break
this. The library has 1.5k GitHub stars and is actively maintained.

### KRW/USD via FRED

The `krw-usd` preset uses FRED CSV (`fred.stlouisfed.org`) instead of
ECOS-KEYSTAT because ECOS does not provide a clean KRW/USD series via
KEYSTAT codes. FRED's DEXKOUS series is sourced from the Federal Reserve
Board and covers 2000-present at daily frequency.

---

## Cross-Plugin Handoff

```
korea-macro (this skill) -> macro-regime-snapshot -> domain-teams:investing-team
```
