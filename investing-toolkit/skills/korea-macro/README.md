# korea-macro

Korea macroeconomic data skill for investing-toolkit.
한국 매크로 경제 데이터 스킬. 韓國宏觀經濟資料技能。

## Overview

Fetches **43 Korea macroeconomic indicators** from the Bank of Korea (BOK)
Economic Statistics System (ECOS) via FinanceDataReader and returns
structured JSON grouped by **12 indicator groups**: rates, inflation,
growth, labor, trade, money, sentiment, cycle, markets, fx, realestate,
and demographics.

**Catalogue**: See `docs/bok-ecos-keystat-catalog.md` for the complete
98-code BOK ECOS KEYSTAT catalogue (43 as presets + ~50 Tier-B candidates
+ 7 skipped). The full BOK ECOS catalogue (10,000+ series) requires an
API key — deferred to v1.9.0.

**Monthly GDP proxy**: The `coincident-cycle` (K253, 동행지수순환변동치)
+ `leading-cycle` (K254, 선행지수순환변동치) pair collectively proxies
monthly GDP momentum, parallel to us-macro's `nowcast` group, japan-macro's
景気動향指数 CI trio, and china-macro's 三大数据. Statistics Korea
(통계청) publishes pre-aggregated CI values via BOK ECOS — no synthesis
needed. The lagging CI (후행지수) exists at Statistics Korea but is not
exposed via BOK ECOS KEYSTAT (probed K255/K256 — both map to other series).

## Data Source (1 script)

| Script | Source | Indicators | Role |
|--------|--------|-----------|------|
| `fdr_client.py` | BOK ECOS-KEYSTAT via FinanceDataReader | 27 (+ 1 FRED) | **Primary** — all macro indicators |

### Why Single Script?

FinanceDataReader wraps BOK ECOS's internal endpoint in a clean Python
API. All 42 ECOS-KEYSTAT codes go through the same `fdr.DataReader()`
call. Only KRW/USD (`krw-usd`) uses a FRED CSV fallback for symmetry with
other country skills (K152 is the BOK official KRW/USD alternative; see
catalogue).

## Indicators (43, v1.8.0)

### Core (by group)

| Group | Count | Indicators | Frequency |
|-------|-------|-----------|-----------|
| rates | 7 | 기준금리, 콜금리, CD 91일, KORIBOR 3M, 국고채 3Y/5Y, 회사채 AA- | Daily |
| inflation | 5 | CPI, Core CPI, PPI, 수입물가, 수출물가 | Monthly |
| growth | 7 | GDP QoQ + 명목, 전산업/제조업 생산, 민간소비, 설비/건설투자 | Quarterly/Monthly |
| labor | 2 | 실업률, 고용률 | Monthly |
| trade | 3 | 경상수지, 교역조건, 재화수출 (national accounts) | Monthly/Quarterly |
| money | 4 | M1, M2, Lf, 가계신용 | Monthly/Quarterly |
| sentiment | 2 | 소비자심리지수, 경제심리지수 | Monthly |
| cycle | 2 | 선행 / 동행 순환변동치 (monthly GDP proxy CI pair) | Monthly |
| markets | 2 | KOSPI, KOSDAQ | Daily |
| fx | 5 | KRW/USD (FRED), KRW/JPY/EUR/CNY, 외환보유액 | Daily/Monthly |
| realestate | 1 | 주택매매가격지수 | Monthly |
| demographics | 3 | 추계인구, 고령인구비율, 합계출산율 | Annual |

### Stability Note

- **FinanceDataReader + ECOS-KEYSTAT**: Uses BOK's internal endpoint
  (`ecos.bok.or.kr/serviceEndpoint`). Not a documented public API, but
  FinanceDataReader (1.5k GitHub stars) is actively maintained and widely
  used in Korean finance/data science community.
- **FRED CSV (krw-usd only)**: Official Federal Reserve data — **very stable**.

## Architecture

```
korea-macro/
├── SKILL.md
├── README.md
├── scripts/
│   ├── fdr_client.py                      ← BOK ECOS via FDR (42 presets + 1 FRED)
│   └── setup.sh
├── docs/                                   ← developer reference material (v1.8.0)
│   ├── README.md
│   ├── bok-ecos-keystat-catalog.md        ← full 98-code KEYSTAT catalogue
│   ├── bok-ecos-keystat.json              ← raw probe output
│   └── tools/probe-keystat.py             ← re-probe script
└── references/
    ├── indicator-index.md                 ← 43 indicators trilingual index
    ├── indicators-rates.md
    ├── indicators-inflation.md
    ├── indicators-growth.md
    ├── indicators-labor.md
    ├── indicators-trade.md
    ├── indicators-sentiment.md            ← CSI / ESI (survey-based)
    ├── indicators-cycle.md                ← CI pair (monthly GDP proxy)
    ├── indicators-demographics.md         ← population / aging / fertility
    ├── indicators-other.md                ← markets / FX / money / real estate
    └── sources.md
```

## Setup

No API keys needed. FinanceDataReader accesses BOK ECOS internally.

```bash
uv run scripts/fdr_client.py --preset policy-rate
uv run scripts/fdr_client.py --preset cpi,unemployment
uv run scripts/fdr_client.py --preset all
```

## Verification

```bash
cd investing-toolkit/scripts

# All 43 presets
for p in policy-rate call-rate cd-91d koribor-3m treasury-3y treasury-5y corp-bond-3y \
  cpi core-cpi ppi import-pi export-pi \
  gdp-qoq gdp-nominal ipi manufacturing private-consumption equipment-investment construction-investment \
  unemployment employment-rate \
  current-account terms-of-trade goods-exports \
  m1 m2 lf household-credit \
  consumer-sentiment economic-sentiment leading-cycle coincident-cycle \
  kospi kosdaq \
  krw-usd krw-jpy krw-eur krw-cny fx-reserves \
  housing-price \
  population aging-ratio fertility-rate; do
  uv run fdr_client.py --preset "$p" --no-cache 2>&1 | python3 -c "
import json,sys;p='$p';d=json.load(sys.stdin);l=d.get('latest') or {}
print(f'{p:25} {l.get(\"date\",\"?\")} {str(l.get(\"value\",\"\")):>12}')
"; done
```

### Latest verification

**Date**: 2026-04-18 — **43 indicators**, all ACTIVE. 42 via
ECOS-KEYSTAT + 1 via FRED DEXKOUS.

**v1.7.3 additions** (2 tagged): `leading-cycle` + `coincident-cycle`
tagged as monthly GDP proxy components.

**v1.8.0 additions** (13 new presets): `koribor-3m`, `private-consumption`,
`equipment-investment`, `construction-investment`, `goods-exports`, `m1`,
`lf`, `krw-jpy`, `krw-eur`, `krw-cny`, `fx-reserves`, `population`,
`aging-ratio`, `fertility-rate`. Plus **structural refactor**: `sentiment`
group split into `sentiment` (CSI/ESI) + `cycle` (CI pair) + new
`demographics` group.

**v1.9.0 candidate**: Full BOK ECOS API integration (requires free API
key registration) — would unlock ~50 additional Tier-B candidates
identified in `docs/bok-ecos-keystat-catalogue.md` plus the lagging CI
(후행지수).
