# korea-macro

Korea macroeconomic data skill for investing-toolkit.
한국 매크로 경제 데이터 스킬. 韓國宏觀經濟資料技能。

## Overview

Fetches 28 Korea macroeconomic indicators from the Bank of Korea (BOK)
Economic Statistics System (ECOS) via FinanceDataReader and returns
structured JSON grouped by 10 indicator groups: rates, inflation, growth,
labor, trade, money, sentiment, markets, fx, and real estate.

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
API. All 27 ECOS-KEYSTAT codes go through the same `fdr.DataReader()`
call. Only KRW/USD (`krw-usd`) uses a FRED CSV fallback because ECOS
does not expose a clean FX series via KEYSTAT codes.

## Indicators (28)

### Core (by group)

| Group | Count | Indicators | Frequency |
|-------|-------|-----------|-----------|
| rates (6) | 6 | 기준금리, 콜금리, CD 91일, 국고채 3Y/5Y, 회사채 AA- | Daily |
| inflation (5) | 5 | CPI, Core CPI, PPI, 수입물가, 수출물가 | Monthly |
| growth (4) | 4 | GDP QoQ, GDP 명목, 전산업생산, 제조업생산 | Quarterly/Monthly |
| labor (2) | 2 | 실업률, 고용률 | Monthly |
| trade (2) | 2 | 경상수지, 교역조건 | Monthly |
| money (2) | 2 | M2, 가계신용 | Monthly/Quarterly |
| sentiment (4) | 4 | 소비자심리, 경제심리, 선행순환변동치, 동행순환변동치 | Monthly |
| markets (2) | 2 | KOSPI, KOSDAQ | Daily |
| fx (1) | 1 | KRW/USD (via FRED) | Daily |
| realestate (1) | 1 | 주택매매가격지수 | Monthly |

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
│   ├── fdr_client.py         ← BOK ECOS via FDR (27 presets + 1 FRED)
│   └── setup.sh
└── references/
    ├── indicator-index.md    ← 28 indicators trilingual index
    ├── indicators-rates.md
    ├── indicators-inflation.md
    ├── indicators-growth.md
    ├── indicators-labor.md
    ├── indicators-trade.md
    ├── indicators-sentiment.md
    ├── indicators-other.md
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

# All 28 presets
for p in policy-rate call-rate cd-91d treasury-3y treasury-5y corp-bond-3y \
  cpi core-cpi ppi import-pi export-pi \
  gdp-qoq gdp-nominal ipi manufacturing \
  unemployment employment-rate \
  current-account terms-of-trade \
  m2 household-credit \
  consumer-sentiment economic-sentiment leading-cycle coincident-cycle \
  kospi kosdaq krw-usd housing-price; do
  uv run fdr_client.py --preset "$p" --no-cache 2>&1 | python3 -c "
import json,sys;p='$p';d=json.load(sys.stdin);l=d.get('latest') or {}
print(f'{p:22} {l.get(\"date\",\"?\")} {str(l.get(\"value\",\"\")):>12}')
"; done
```

### Latest verification

**Date**: 2026-04-17 — 28 indicators, all ACTIVE. 20 via ECOS-KEYSTAT
verified in research session, 8 additional presets (treasury-5y, gdp-nominal,
export-pi, import-pi, employment-rate, terms-of-trade, household-credit,
coincident-cycle) verified via same KEYSTAT mechanism.
