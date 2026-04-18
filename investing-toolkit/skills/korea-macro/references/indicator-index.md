# Korea Macro Indicator Index / 한국 매크로 지표 색인 / 韓國總經指標索引

54 indicators across 13 groups. 53 via BOK ECOS KEYSTAT (`fdr_client`) +
1 via FRED (`krw-usd` DEXKOUS).

| Preset | 한국어 | English | Code | File |
|--------|--------|---------|------|------|
| `policy-rate` | 기준금리 | BOK Base Rate | K051 | `indicators-rates.md` |
| `call-rate` | 콜금리 1일 | Call Rate Overnight | K052 | `indicators-rates.md` |
| `cd-91d` | CD 91일 | CD 91-Day Rate | K053 | `indicators-rates.md` |
| `koribor-3m` | KORIBOR 3개월 | KORIBOR 3-Month | K063 | `indicators-rates.md` |
| `treasury-3y` | 국고채 3년 | Treasury Bond 3Y | K056 | `indicators-rates.md` |
| `treasury-5y` | 국고채 5년 | Treasury Bond 5Y | K062 | `indicators-rates.md` |
| `corp-bond-3y` | 회사채 AA- 3년 | Corporate Bond 3Y AA- | K057 | `indicators-rates.md` |
| `cpi` | 소비자물가 총지수 | CPI Total Index | K401 | `indicators-inflation.md` |
| `core-cpi` | 근원 CPI | Core CPI | K405 | `indicators-inflation.md` |
| `ppi` | 생산자물가 총지수 | PPI Total Index | K402 | `indicators-inflation.md` |
| `import-pi` | 수입물가 총지수 | Import Price Index | K403 | `indicators-inflation.md` |
| `export-pi` | 수출물가 총지수 | Export Price Index | K404 | `indicators-inflation.md` |
| `gdp-qoq` | GDP 실질 전기비 | GDP Real QoQ SA% | K258 | `indicators-growth.md` |
| `gdp-nominal` | GDP 명목 | GDP Nominal | K257 | `indicators-growth.md` |
| `ipi` | 전산업생산지수 | All-Industry Production | K220 | `indicators-growth.md` |
| `manufacturing` | 제조업 생산지수 | Manufacturing Production | K201 | `indicators-growth.md` |
| `private-consumption` | 민간소비 | Private Consumption | K259 | `indicators-growth.md` |
| `equipment-investment` | 설비투자 | Equipment Investment | K260 | `indicators-growth.md` |
| `construction-investment` | 건설투자 | Construction Investment | K261 | `indicators-growth.md` |
| `manufacturing-inventory` | 제조업 재고지수 | Manufacturing Inventory Index | K202 | `indicators-industry.md` |
| `manufacturing-shipment` | 제조업 출하지수 | Manufacturing Shipment Index | K203 | `indicators-industry.md` |
| `manufacturing-operating-rate` | 제조업 가동률지수 | Manufacturing Operating Rate | K204 | `indicators-industry.md` |
| `services-production` | 서비스업 생산지수 | Services Production Index | K205 | `indicators-industry.md` |
| `retail-sales` | 소매판매액지수 | Retail Sales Index | K206 | `indicators-industry.md` |
| `wholesale-retail` | 도매 및 소매업 생산 | Wholesale & Retail Production | K207 | `indicators-industry.md` |
| `credit-card-usage` | 개인카드 이용금액 | Credit Card Individual Usage | K210 | `indicators-industry.md` |
| `machinery-orders` | 국내기계수주(선박제외) | Machinery Orders ex-Ship | K213 | `indicators-industry.md` |
| `capital-goods-output` | 기계설비류 생산(선박제외) | Capital Goods Output ex-Ship | K215 | `indicators-industry.md` |
| `construction-completion` | 건설기성액 | Construction Completion Value | K216 | `indicators-industry.md` |
| `construction-orders` | 건설수주액 | Construction Orders Value | K217 | `indicators-industry.md` |
| `unemployment` | 실업률 | Unemployment Rate | K303 | `indicators-labor.md` |
| `employment-rate` | 고용률 | Employment Rate | K304 | `indicators-labor.md` |
| `current-account` | 경상수지 | Current Account (M USD) | K351 | `indicators-trade.md` |
| `terms-of-trade` | 순상품교역조건지수 | Terms of Trade Index | K360 | `indicators-trade.md` |
| `goods-exports` | 재화수출 | Goods Exports (national accounts) | K462 | `indicators-trade.md` |
| `m1` | 협의통화 M1 | M1 Narrow Money | K002 | `indicators-other.md` |
| `m2` | 광의통화 M2 | M2 Broad Money | K003 | `indicators-other.md` |
| `lf` | Lf 금융기관유동성 | Financial Institution Liquidity | K004 | `indicators-other.md` |
| `household-credit` | 가계신용 | Household Credit | K007 | `indicators-other.md` |
| `consumer-sentiment` | 소비자심리지수 | Consumer Sentiment Index | K252 | `indicators-sentiment.md` |
| `economic-sentiment` | 경제심리지수 | Economic Sentiment Index | K269 | `indicators-sentiment.md` |
| `leading-cycle` | 선행지수순환변동치 | Leading CI Cyclical (**monthly GDP proxy leading**) | K254 | `indicators-cycle.md` |
| `coincident-cycle` | 동행지수순환변동치 | Coincident CI Cyclical (**monthly GDP proxy**) | K253 | `indicators-cycle.md` |
| `kospi` | 코스피지수 | KOSPI Index | K101 | `indicators-other.md` |
| `kosdaq` | 코스닥지수 | KOSDAQ Index | K102 | `indicators-other.md` |
| `krw-usd` | 원달러 환율 | KRW/USD Rate | DEXKOUS | `indicators-other.md` |
| `krw-jpy` | 원/일본엔 | KRW/JPY per 100 yen | K153 | `indicators-other.md` |
| `krw-eur` | 원/유로 | KRW/EUR | K154 | `indicators-other.md` |
| `krw-cny` | 원/위안 | KRW/CNY | K156 | `indicators-other.md` |
| `fx-reserves` | 외환보유액 | FX Reserves Total | K155 | `indicators-other.md` |
| `housing-price` | 주택매매가격지수 | Housing Price Index | K407 | `indicators-other.md` |
| `population` | 추계인구 | Estimated Population | K451 | `indicators-demographics.md` |
| `aging-ratio` | 고령인구비율 | Elderly Ratio ≥65 | K460 | `indicators-demographics.md` |
| `fertility-rate` | 합계출산율 | Total Fertility Rate | K461 | `indicators-demographics.md` |

## Group membership (v1.8.1)

| Group | Presets |
|-------|---------|
| `rates` (7) | policy-rate, call-rate, cd-91d, koribor-3m, treasury-3y, treasury-5y, corp-bond-3y |
| `inflation` (5) | cpi, core-cpi, ppi, import-pi, export-pi |
| `growth` (7) | gdp-qoq, gdp-nominal, ipi, manufacturing, private-consumption, equipment-investment, construction-investment |
| `industry` (11) | manufacturing-inventory, manufacturing-shipment, manufacturing-operating-rate, services-production, retail-sales, wholesale-retail, credit-card-usage, machinery-orders, capital-goods-output, construction-completion, construction-orders |
| `labor` (2) | unemployment, employment-rate |
| `trade` (3) | current-account, terms-of-trade, goods-exports |
| `money` (4) | m1, m2, lf, household-credit |
| `sentiment` (2) | consumer-sentiment, economic-sentiment |
| `cycle` (2) | leading-cycle, coincident-cycle |
| `markets` (2) | kospi, kosdaq |
| `fx` (5) | krw-usd, krw-jpy, krw-eur, krw-cny, fx-reserves |
| `realestate` (1) | housing-price |
| `demographics` (3) | population, aging-ratio, fertility-rate |

## Catalogue

See `../docs/bok-ecos-keystat-catalog.md` for the full 98-code KEYSTAT
catalogue including Tier-B candidates not yet exposed as presets.
