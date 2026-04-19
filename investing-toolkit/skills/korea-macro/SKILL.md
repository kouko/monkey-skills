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
  rates, inflation, growth, industry, labor, trade, money, sentiment,
  cycle, markets, FX, real estate, demographics (53 presets via
  ECOS-KEYSTAT, 1 via FRED CSV)

This skill is **data-only**. The output is designed for handoff to
`macro-regime-snapshot` or `domain-teams:investing-team`.

**Monthly GDP proxy note**: Korea's official GDP is quarterly
(`gdp-qoq` / `gdp-nominal`). The **선행-동행 CI pair** (`leading-cycle`
K254 + `coincident-cycle` K253), published monthly by 통계청 (Statistics
Korea) and served via BOK ECOS, collectively proxy monthly GDP momentum
— parallel to us-macro's `nowcast` group, japan-macro's 景気動向指数
CI trio, and china-macro's 三大数据. `coincident-cycle` (동행지수
순환변동치) is the canonical "current GDP feel" read. The lagging CI
(후행지수) exists at Statistics Korea but is not exposed via BOK ECOS
KEYSTAT — deferred.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `--indicators` | no | `all` | Comma-separated: `rates`, `inflation`, `growth`, `industry`, `labor`, `trade`, `money`, `sentiment`, `cycle`, `markets`, `fx`, `realestate`, `demographics`, or `all` |

---

## Indicator Groups

### rates

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| policy-rate | K051 | BOK Base Rate (기준금리) | Daily |
| call-rate | K052 | Call Rate Overnight (콜금리 1일) | Daily |
| cd-91d | K053 | CD 91-Day Rate (CD 91일) | Daily |
| koribor-3m | K063 | KORIBOR 3M (3개월) | Daily |
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
| private-consumption | K259 | Private Consumption (민간소비) | Quarterly |
| equipment-investment | K260 | Equipment Investment (설비투자) | Quarterly |
| construction-investment | K261 | Construction Investment (건설투자) | Quarterly |

### industry (monthly sector activity)

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| manufacturing-inventory | K202 | Manufacturing Inventory Index (제조업 재고지수) | Monthly |
| manufacturing-shipment | K203 | Manufacturing Shipment Index (제조업 출하지수) | Monthly |
| manufacturing-operating-rate | K204 | Manufacturing Operating Rate Index (가동률지수) | Monthly |
| services-production | K205 | Services Production Index (서비스업 생산지수) | Monthly |
| retail-sales | K206 | Retail Sales Index (소매판매액지수) | Monthly |
| wholesale-retail | K207 | Wholesale & Retail Production (도매 및 소매업 생산) | Monthly |
| credit-card-usage | K210 | Credit Card Individual Usage (개인카드 이용금액) | Monthly |
| machinery-orders | K213 | Machinery Orders Domestic ex-Ship (국내기계수주, 선박제외) | Monthly |
| capital-goods-output | K215 | Capital Goods Output ex-Ship (기계설비류 생산, 선박제외) | Monthly |
| construction-completion | K216 | Construction Completion Value (건설기성액) | Monthly |
| construction-orders | K217 | Construction Orders Value (건설수주액) | Monthly |

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
| goods-exports | K462 | Goods Exports (재화수출, national accounts) | Quarterly |

### money

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| m1 | K002 | M1 Narrow Money (협의통화 평잔) | Monthly |
| m2 | K003 | M2 Broad Money (광의통화 M2 평잔) | Monthly |
| lf | K004 | Lf Financial Institution Liquidity (금융기관유동성) | Monthly |
| household-credit | K007 | Household Credit (가계신용) | Quarterly |

### sentiment (survey-based)

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| consumer-sentiment | K252 | Consumer Sentiment Index (소비자심리지수) | Monthly |
| economic-sentiment | K269 | Economic Sentiment Index (경제심리지수) | Monthly |

### cycle (monthly GDP proxy CI pair)

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| leading-cycle | K254 | Leading CI Cyclical Component (선행지수순환변동치) (**monthly GDP proxy leading**) | Monthly |
| coincident-cycle | K253 | Coincident CI Cyclical Component (동행지수순환변동치) (**monthly GDP proxy**) | Monthly |

### markets

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| kospi | K101 | KOSPI Index (코스피지수) | Daily |
| kosdaq | K102 | KOSDAQ Index (코스닥지수) | Daily |

### fx

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| krw-usd | DEXKOUS | KRW/USD Exchange Rate (원달러 환율) | Daily (via FRED) |
| krw-jpy | K153 | KRW/JPY Exchange Rate per 100 yen (원/일본엔) | Daily |
| krw-eur | K154 | KRW/EUR Exchange Rate (원/유로) | Daily |
| krw-cny | K156 | KRW/CNY Exchange Rate (원/위안 종가) | Daily |
| fx-reserves | K155 | FX Reserves Total (외환보유액 합계) | Monthly |

### realestate

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| housing-price | K407 | Housing Price Index (주택매매가격지수) | Monthly |

### demographics

| Preset | Code | Name | Frequency |
|--------|------|------|-----------|
| population | K451 | Estimated Population (추계인구) | Annual |
| aging-ratio | K460 | Elderly Population Ratio ≥65 (고령인구비율) | Annual |
| fertility-rate | K461 | Total Fertility Rate (합계출산율) | Annual |

### PMI (URL reference only — licensed, not fetched)

Free-tier PMI data for Korea is **not fetched** by this skill because
the **S&P Global South Korea Manufacturing PMI** (Korea's canonical PMI
series) is compiled and licensed commercially by **S&P Global**:

- Full historic headline and sub-index data require a paid S&P Global
  subscription. S&P Global's data licence prohibits unauthorised scraping
  or redistribution of PMI values.
- BOK ECOS does expose manufacturing BSI (기업경기실사지수) series
  (K255 / K256 / K267), but these are low-cadence (quarterly, ~15 rows
  of history) and structurally differ from S&P Global PMI methodology —
  they were intentionally skipped during the v1.8.1 catalogue build
  (see `docs/bok-ecos-keystat-catalog.md`). A full BSI integration would
  require direct ECOS API access (free API key at
  `ecos.bok.or.kr/api/#/AuthKeyApply`) and remains on the
  deferred-candidates list (see `investing-toolkit/ROADMAP.md`).

Reader can manually cross-reference:

- S&P Global South Korea Manufacturing PMI press release (free headline
  + summary commentary):
  https://www.pmi.spglobal.com/Public/Home/PressRelease/d24db6b6b62745c1970931ac3b4323c5
- S&P Global PMI portal: https://www.pmi.spglobal.com/

Related existing presets in this skill (closest proxy signals — **not
PMI-equivalent**, but survey-based Korean sentiment captured monthly
by BOK via the `sentiment` group):

- `consumer-sentiment` (K252, 소비자심리지수, Consumer Sentiment Index)
- `economic-sentiment` (K269, 경제심리지수, Economic Sentiment Index)

Both are 100-centred composite indicators and do not map 1:1 to a
50-threshold PMI reading — but they are the BOK-published monthly
sentiment signals for Korea and serve as the skill's interim proxy for
manufacturing momentum until S&P Global PMI becomes accessible via a
free primary source.

For cross-country PMI comparison, see CN Caixin + NBS PMI in
`china-macro` skill (v1.11.0 `pmi` group), TW PMI / NMI in
`taiwan-macro` skill (v1.11.0 `pmi` group via NDC open data), and US
OECD CLI in `us-macro` skill (v1.10.0 `pmi` group).

---

## How It Works

### Step 1 — Resolve series list

| Input | Presets |
|-------|--------|
| `rates` | policy-rate, call-rate, cd-91d, koribor-3m, treasury-3y, treasury-5y, corp-bond-3y |
| `inflation` | cpi, core-cpi, ppi, import-pi, export-pi |
| `growth` | gdp-qoq, gdp-nominal, ipi, manufacturing, private-consumption, equipment-investment, construction-investment |
| `industry` | manufacturing-inventory, manufacturing-shipment, manufacturing-operating-rate, services-production, retail-sales, wholesale-retail, credit-card-usage, machinery-orders, capital-goods-output, construction-completion, construction-orders |
| `labor` | unemployment, employment-rate |
| `trade` | current-account, terms-of-trade, goods-exports |
| `money` | m1, m2, lf, household-credit |
| `sentiment` | consumer-sentiment, economic-sentiment |
| `cycle` | leading-cycle, coincident-cycle |
| `markets` | kospi, kosdaq |
| `fx` | krw-usd, krw-jpy, krw-eur, krw-cny, fx-reserves |
| `realestate` | housing-price |
| `demographics` | population, aging-ratio, fertility-rate |

### Step 2 — Launch data-fetcher agents

```
### Fetch Requests (rates batch)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fdr_client.py --preset policy-rate,call-rate,cd-91d,koribor-3m,treasury-3y,treasury-5y,corp-bond-3y

### Fetch Requests (inflation batch)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fdr_client.py --preset cpi,core-cpi,ppi,import-pi,export-pi

### Fetch Requests (growth + labor)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fdr_client.py --preset gdp-qoq,gdp-nominal,ipi,manufacturing,private-consumption,equipment-investment,construction-investment,unemployment,employment-rate

### Fetch Requests (industry batch)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fdr_client.py --preset manufacturing-inventory,manufacturing-shipment,manufacturing-operating-rate,services-production,retail-sales,wholesale-retail,credit-card-usage,machinery-orders,capital-goods-output,construction-completion,construction-orders

### Fetch Requests (trade + money + sentiment + cycle)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fdr_client.py --preset current-account,terms-of-trade,goods-exports,m1,m2,lf,household-credit,consumer-sentiment,economic-sentiment,leading-cycle,coincident-cycle

### Fetch Requests (markets + fx + real estate + demographics)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fdr_client.py --preset kospi,kosdaq,krw-usd,krw-jpy,krw-eur,krw-cny,fx-reserves,housing-price,population,aging-ratio,fertility-rate
```

### Step 3 — Merge into unified output

All data points retain `_source`: `"fdr_ecos"` (or `"fred"` for krw-usd).

---

## Reference

- `references/indicator-index.md` — Quick lookup (trilingual)
- `references/indicators-rates.md` — 금리 Rates
- `references/indicators-inflation.md` — 물가 Inflation
- `references/indicators-growth.md` — 성장 Growth (quarterly national accounts)
- `references/indicators-industry.md` — 산업 Industry (monthly sector activity)
- `references/indicators-labor.md` — 고용 Labor
- `references/indicators-trade.md` — 무역 Trade
- `references/indicators-sentiment.md` — 센티먼트 Sentiment (CSI/ESI, survey-based)
- `references/indicators-cycle.md` — 경기종합지수 Cycle CI pair (monthly GDP proxy)
- `references/indicators-demographics.md` — 인구 Demographics
- `references/indicators-other.md` — Markets, FX, Money, Real Estate
- `references/sources.md` — Primary sources
- `docs/bok-ecos-keystat-catalog.md` — Full 98-code KEYSTAT catalogue

---

## Limitations

### Publication lags

| Series | Typical lag |
|--------|-------------|
| BOK Base Rate (K051) | 1 business day (daily) |
| Call Rate, CD, KORIBOR, Bonds (K052-K063) | 1 business day (daily) |
| KRW/JPY, KRW/EUR, KRW/CNY (K153-K156) | 1 business day (daily) |
| FX Reserves (K155) | ~1 week after month-end |
| Private Consumption, Investment (K259-K261) | ~8 weeks after quarter-end |
| Goods Exports (K462) | ~8 weeks after quarter-end |
| Population / Aging / Fertility (K451/K460/K461) | ~6 months (annual series) |
| M1, Lf (K002, K004) | ~4 weeks after month-end |
| KOSPI, KOSDAQ (K101-K102) | 1 business day (daily) |
| KRW/USD via FRED (DEXKOUS) | 1-2 business days |
| CPI, Core CPI (K401, K405) | ~3-4 weeks after month-end |
| PPI (K402) | ~4 weeks after month-end |
| Import/Export PI (K403, K404) | ~3-4 weeks after month-end |
| IPI, Manufacturing (K220, K201) | ~5-6 weeks after month-end |
| Manufacturing Inventory / Shipment / Operating-Rate (K202-K204) | ~5-6 weeks after month-end |
| Services Production, Retail Sales, Wholesale-Retail (K205-K207) | ~5-6 weeks after month-end |
| Credit Card Usage (K210) | ~6 weeks after month-end |
| Capital Goods Output (K215) | ~5-6 weeks after month-end |
| Machinery Orders, Construction Completion / Orders (K213, K216-K217) | ~6-7 weeks after month-end |
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
