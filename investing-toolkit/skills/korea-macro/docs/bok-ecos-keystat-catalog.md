# BOK ECOS KEYSTAT Catalog

Full catalogue of Bank of Korea (한국은행) ECOS **KEYSTAT** codes accessible
via `FinanceDataReader` without any API key. KEYSTAT = BOK's curated
**100대 통계지표** subset; the full ECOS catalogue (thousands of series)
requires an API key (free at
https://ecos.bok.or.kr/api/#/AuthKeyApply) — not covered here.

- **Source**: Probed 2026-04-18 via `ECOS-KEYSTAT:K{001-500}` through
  FinanceDataReader
- **Tool**: `tools/probe-keystat.py`
- **Raw data**: `bok-ecos-keystat.json` (98 accessible codes)
- **Name limitation**: KEYSTAT returns only the first *column* name (often
  a sub-header like `총지수` or `제조업`), not the full table name. Full
  names marked below were identified by cross-reference with the BOK ECOS
  website and common Korean macro terminology. Unidentified codes remain
  marked as `(see ECOS website)`.

## Preset-status legend

- **in-skill**: Already exposed as a preset in `fdr_client.py`
- **v1.8.0**: Added as Tier B expansion in v1.8.0
- **candidate**: Identified but not yet added; possible future expansion
- **skip**: Duplicate, ambiguous, or not meaningful without extra dimension

## Categories

K-codes are grouped by meaning (not by K-code ordinal — BOK's numbering
has gaps and re-uses):

- [K001-K011 — 통화 및 유동성 (Monetary & liquidity)](#k001-k011--통화-및-유동성-monetary--liquidity)
- [K051-K063 — 금리 (Interest rates)](#k051-k063--금리-interest-rates)
- [K101-K108 — 금융시장 (Financial markets)](#k101-k108--금융시장-financial-markets)
- [K152-K156 — 환율 (FX rates)](#k152-k156--환율-fx-rates)
- [K201-K220 — 경제활동 (Economic activity)](#k201-k220--경제활동-economic-activity)
- [K252-K269 — 경기종합지수, 국민계정 (CI & national accounts)](#k252-k269--경기종합지수-국민계정-ci--national-accounts)
- [K301-K308 — 노동, 임금 (Labor & wages)](#k301-k308--노동-임금-labor--wages)
- [K351-K360 — 국제수지 (BoP & external)](#k351-k360--국제수지-bop--external)
- [K401-K409 — 물가, 부동산 (Prices & real estate)](#k401-k409--물가-부동산-prices--real-estate)
- [K451-K469 — 인구, 기타 (Demographics & misc)](#k451-k469--인구-기타-demographics--misc)

---

## K001-K011 — 통화 및 유동성 (Monetary & liquidity)

| K-code | First column | Suggested name (EN) | Rows | Latest | Status |
|--------|--------------|---------------------|------|--------|--------|
| K002 | M1 (평잔, 원계열) | M1 Narrow Money (avg, orig) | 269 | 2026-02 | **v1.8.0** (preset: `m1`) |
| K003 | M2(평잔, 원계열) | M2 Broad Money (avg, orig) | 269 | 2026-02 | in-skill (`m2`) |
| K004 | Lf(금융기관유동성) 상품별 | Lf Financial Institution Liquidity | 269 | 2026-02 | **v1.8.0** (preset: `lf`) |
| K005 | 총예금 | Total deposits | 434 | 2026-02 | candidate |
| K006 | 총대출금 | Total loans | 434 | 2026-02 | candidate |
| K007 | 가계신용 | Household credit | 93 | 2025-10 | in-skill (`household-credit`) |
| K008 | 가계대출 연체율(전체1M) | Household loan delinquency 1M | 74 | 2026-01 | candidate |
| K011 | L (광의 유동성) | L Broad Liquidity | 269 | 2026-02 | candidate |

## K051-K063 — 금리 (Interest rates)

| K-code | First column | Suggested name (EN) | Rows | Latest | Status |
|--------|--------------|---------------------|------|--------|--------|
| K051 | 한국은행 기준금리 | BOK Base Rate (기준금리) | 6723 | 2026-04-16 | in-skill (`policy-rate`) |
| K052 | 콜금리(1일) | Call Rate O/N | 7644 | 2026-04-16 | in-skill (`call-rate`) |
| K053 | CD(91일) | CD 91-Day | 7941 | 2026-04-17 | in-skill (`cd-91d`) |
| K055 | 통안증권(1년) | MSB 1Y (통안채) | 7902 | 2026-04-17 | candidate |
| K056 | 국고채(3년) | Treasury Bond 3Y | 6798 | 2026-04-17 | in-skill (`treasury-3y`) |
| K057 | 회사채(3년, AA-) | Corp Bond 3Y AA- | 7941 | 2026-04-17 | in-skill (`corp-bond-3y`) |
| K058 | 저축성수신 | Savings deposit rate | 362 | 2026-02 | candidate |
| K059 | 대출평균 | Average lending rate | 362 | 2026-02 | candidate |
| K062 | 국고채(5년) | Treasury Bond 5Y | 6509 | 2026-04-17 | in-skill (`treasury-5y`) |
| K063 | KORIBOR(3개월) | KORIBOR 3M | 5132 | 2026-04-17 | **v1.8.0** (preset: `koribor-3m`) |

## K101-K108 — 금융시장 (Financial markets)

| K-code | First column | Suggested name (EN) | Rows | Latest | Status |
|--------|--------------|---------------------|------|--------|--------|
| K101 | KOSPI지수 | KOSPI Index | 7864 | 2026-04-17 | in-skill (`kospi`) |
| K102 | KOSDAQ지수 | KOSDAQ Index | 5750 | 2026-04-17 | in-skill (`kosdaq`) |
| K103 | KOSPI_거래대금 | KOSPI Trading Volume | 254 | 2026-02 | candidate |
| K104 | 합계 | (see ECOS website) | 292 | 2026-04 | candidate |
| K107 | 투자자 예탁금 | Investor deposits | 334 | 2026-03 | candidate |
| K108 | 국고채권 | T-bond issuance | 305 | 2026-02 | candidate |

## K152-K156 — 환율 (FX rates)

| K-code | First column | Suggested name (EN) | Rows | Latest | Status |
|--------|--------------|---------------------|------|--------|--------|
| K152 | 원/달러(종가 15:30) | KRW/USD BOK official close | 8917 | 2026-04-17 | candidate (we use FRED `DEXKOUS`) |
| K153 | 원/일본엔(100엔) | KRW/JPY per 100 yen | 9427 | 2026-04-17 | **v1.8.0** (preset: `krw-jpy`) |
| K154 | 원/유로 | KRW/EUR | 8162 | 2026-04-17 | **v1.8.0** (preset: `krw-eur`) |
| K155 | 합계 | FX reserves 합계 | 435 | 2026-03 | **v1.8.0** (preset: `fx-reserves`) |
| K156 | 원/위안(종가) | KRW/CNY | 2793 | 2026-04-17 | **v1.8.0** (preset: `krw-cny`) |

## K201-K220 — 경제활동 (Economic activity)

Large cluster; 제조업 / 총지수 headings indicate these are typically
sub-series of IPI + business activity. Only the clearest ones are added
to presets.

| K-code | First column | Suggested name (EN) | Rows | Latest | Status |
|--------|--------------|---------------------|------|--------|--------|
| K201 | 제조업 | Manufacturing IPI (전산업생산지수 세부) | 434 | 2026-02 | in-skill (`manufacturing`) |
| K202 | 제조업 | Manufacturing inventory | 434 | 2026-02 | candidate |
| K203 | 제조업 | Manufacturing shipment | 434 | 2026-02 | candidate |
| K204 | 제조업 | Manufacturing operating rate | 434 | 2026-02 | candidate |
| K205 | 총지수 | Services production | 314 | 2026-02 | candidate |
| K206 | 총지수 | Retail sales | 374 | 2026-02 | candidate |
| K207 | 도매 및 소매업 | Wholesale/retail | 314 | 2026-02 | candidate |
| K210 | 개인 이용금액 | Credit card usage | 277 | 2026-01 | candidate |
| K212 | 계절조정지수 | SA index (see ECOS) | 373 | 2026-02 | candidate |
| K213 | 국내수요(선박제외) | Machinery orders ex-ship | 357 | 2026-02 | candidate |
| K215 | 기계설비류(선박제외) | Capital goods output ex-ship | 434 | 2026-02 | candidate |
| K216 | 총기성액 | Construction completion value | 344 | 2026-02 | candidate |
| K217 | 총수주액 | Construction orders value | 434 | 2026-02 | candidate |
| K218 | 구조별 | Housing starts by structure | 86 | 2026-02 | candidate |
| K219 | 연면적 | Housing floor area | 86 | 2026-02 | candidate |
| K220 | 전산업생산지수(농림어업 제외) | All-Industry Production (ex ag/fish) | 314 | 2026-02 | in-skill (`ipi`) |

## K252-K269 — 경기종합지수, 국민계정 (CI & national accounts)

| K-code | First column | Suggested name (EN) | Rows | Latest | Status |
|--------|--------------|---------------------|------|--------|--------|
| K252 | 소비자심리지수 | Consumer Sentiment Index (CSI) | 213 | 2026-03 | in-skill (`consumer-sentiment`) |
| K253 | 동행지수순환변동치 | Coincident CI cyclical component | 434 | 2026-02 | in-skill (`coincident-cycle`) |
| K254 | 선행지수순환변동치 | Leading CI cyclical component | 434 | 2026-02 | in-skill (`leading-cycle`) |
| K255 | C 제조업 | Manufacturing BSI (not Lagging CI) | 16 | 2024-01 | skip (not monthly; not the lagging CI) |
| K256 | C 제조업 | Manufacturing BSI (var) | 16 | 2024-01 | skip (similar) |
| K257 | 국내총생산(시장가격, GDP) | GDP nominal | 144 | 2025-10 | in-skill (`gdp-nominal`) |
| K258 | GDP(실질, 계절조정, 전기비) | Real GDP QoQ SA | 144 | 2025-10 | in-skill (`gdp-qoq`) |
| K259 | 민간소비 | Private consumption | 144 | 2025-10 | **v1.8.0** (preset: `private-consumption`) |
| K260 | 설비투자 | Equipment investment | 144 | 2025-10 | **v1.8.0** (preset: `equipment-investment`) |
| K261 | 건설투자 | Construction investment | 144 | 2025-10 | **v1.8.0** (preset: `construction-investment`) |
| K263 | 1인당 국민총소득 (달러) | GNI per capita USD (annual) | 35 | 2025-01 | candidate |
| K264 | 총저축률 | Gross savings rate | 144 | 2025-10 | candidate |
| K265 | 국내총투자율 | Gross investment rate | 144 | 2025-10 | candidate |
| K266 | 수출입의 대 GNI 비율 | Trade/GNI ratio (annual) | 35 | 2025-01 | candidate |
| K267 | C 제조업 | Manufacturing BSI (not monthly) | 15 | 2024-01 | skip |
| K269 | 경제심리지수(원계열) | Economic Sentiment Index (ESI) | 279 | 2026-03 | in-skill (`economic-sentiment`) |

## K301-K308 — 노동, 임금 (Labor & wages)

| K-code | First column | Suggested name (EN) | Rows | Latest | Status |
|--------|--------------|---------------------|------|--------|--------|
| K301 | 경제활동인구 | Economically active population | 322 | 2026-03 | candidate |
| K302 | 취업자 | Employed | 322 | 2026-03 | candidate |
| K303 | 실업률 | Unemployment rate | 322 | 2026-03 | in-skill (`unemployment`) |
| K304 | 고용률 | Employment rate | 322 | 2026-03 | in-skill (`employment-rate`) |
| K305 | 산업생산기준 | Labor productivity (industrial basis) | 60 | 2025-10 | candidate |
| K306 | 명목 | Nominal wage per worker | 24 | 2024-10 | candidate (annual) |
| K307 | 비농전산업 | Non-farm real wages | 60 | 2025-10 | candidate |
| K308 | 비농전산업 | Non-farm nominal wages | 60 | 2025-10 | candidate |

## K351-K360 — 국제수지 (BoP & external)

| K-code | First column | Suggested name (EN) | Rows | Latest | Status |
|--------|--------------|---------------------|------|--------|--------|
| K351 | 경상수지 | Current account | 434 | 2026-02 | in-skill (`current-account`) |
| K353 | 대외채무 | External debt | 125 | 2025-10 | candidate |
| K356 | 직접투자(자산) | FDI outflow (assets) | 434 | 2026-02 | candidate |
| K357 | 직접투자(부채) | FDI inflow (liabilities) | 434 | 2026-02 | candidate |
| K358 | 총지수 | Export Price Index (total) | 435 | 2026-03 | in-skill (`export-pi`) |
| K359 | 총지수 | Import Price Index — candidate (see K403) | 435 | 2026-03 | skip (K403 is canonical) |
| K360 | 순상품교역조건지수 | Net barter terms of trade | 435 | 2026-03 | in-skill (`terms-of-trade`) |

## K401-K409 — 물가, 부동산 (Prices & real estate)

| K-code | First column | Suggested name (EN) | Rows | Latest | Status |
|--------|--------------|---------------------|------|--------|--------|
| K401 | 총지수 | CPI Total (소비자물가) | 435 | 2026-03 | in-skill (`cpi`) |
| K402 | 총지수 | PPI Total (생산자물가) | 434 | 2026-02 | in-skill (`ppi`) |
| K403 | 총지수 | Import Price Index | 435 | 2026-03 | in-skill (`import-pi`) |
| K404 | 총지수 | Export Price Index | 435 | 2026-03 | in-skill (`export-pi`) |
| K405 | 농산물및석유류제외지수 | Core CPI ex food/energy | 435 | 2026-03 | in-skill (`core-cpi`) |
| K406 | 생활물가지수 | Daily-necessities CPI | 375 | 2026-03 | candidate |
| K407 | 종합 | Housing Price Index 매매 | 56 | 2026-01 | in-skill (`housing-price`) |
| K408 | 종합 | Housing Price Index 전세 | 56 | 2026-01 | candidate |
| K409 | 전국 | Regional CPI (nationwide) | 254 | 2026-02 | candidate |

## K451-K469 — 인구, 기타 (Demographics & misc)

| K-code | First column | Suggested name (EN) | Rows | Latest | Status |
|--------|--------------|---------------------|------|--------|--------|
| K451 | 추계인구 | Estimated population | 36 | 2026-01 | **v1.8.0** (preset: `population`) |
| K453 | 승용차 | Passenger vehicle sales | 374 | 2026-02 | candidate |
| K456 | 처분가능소득 | Disposable income | 14 | 2024-01 | candidate (annual) |
| K460 | 고령인구비율(65세 이상) | Elderly population ratio | 36 | 2026-01 | **v1.8.0** (preset: `aging-ratio`) |
| K461 | 합계출산율 | Total fertility rate | 35 | 2025-01 | **v1.8.0** (preset: `fertility-rate`) |
| K462 | 재화수출 | Goods exports (national accounts) | 144 | 2025-10 | **v1.8.0** (preset: `goods-exports`) |
| K463 | 명목 | Nominal (annual series) | 24 | 2024-10 | candidate |
| K464 | 처분가능소득 | Disposable income (var) | 14 | 2024-01 | candidate |
| K465 | 증권투자(자산) | Portfolio investment outflow | 434 | 2026-02 | candidate |
| K466 | 증권투자(부채) | Portfolio investment inflow | 434 | 2026-02 | candidate |
| K467 | 소득교역조건지수 | Income terms of trade | 435 | 2026-03 | candidate |
| K468 | 대외채권 | External credit | 125 | 2025-10 | candidate |
| K469 | 금 | Gold (FX reserves component) | 411 | 2026-03 | candidate |

---

## Summary

- **Total accessible**: 98 KEYSTAT codes (of 500 probed)
- **In-skill presets (after v1.8.0)**: 27 FDR + 1 FRED = 28 → expanded to
  27 + 13 new = **40 FDR** + 1 FRED = **41 total**
- **Candidates for future expansion**: ~50 codes
- **Skipped**: K255, K256, K267 (BSI with only 15-16 rows, not monthly
  time series despite the K-code suggesting lagging CI)
- **Not covered by KEYSTAT**: Lagging CI (후행지수순환변동치), StatSearch
  detail series, KITA trade data — would require direct ECOS API key
  integration (v1.9.0 roadmap).

## How to refresh

```bash
cd investing-toolkit/skills/korea-macro/docs/tools
uv run probe-keystat.py              # regenerate JSON (K001-K500)
# Then manually update this Markdown file with newly-found codes
```

## Why not the full ECOS catalog?

FinanceDataReader's `ECOS-KEYSTAT:K{NNN}` wrapper only exposes BOK's
curated 100대 통계지표 subset. The full BOK ECOS catalogue (10,000+
series) requires an API key. If needed, the key is free — register at
https://ecos.bok.or.kr/api/#/AuthKeyApply and use the
`StatTableList` + `StatisticSearch` endpoints directly. Deferred to
v1.9.0 pending demand.
