# taiwan-macro

Taiwan macroeconomic data skill for investing-toolkit.
台灣宏觀經濟資料技能。台湾マクロ経済データスキル。

## Overview

Fetches 30 Taiwan macroeconomic indicators from four government data sources
and returns structured JSON grouped by 8 indicator groups: rates, inflation,
growth, labor, trade, cycle, forex, and money.

## Data Sources (4 scripts)

| Script | Source | Indicators | Role |
|--------|--------|-----------|------|
| `statgov_client.py` | stat.gov.tw hidden chart JSON | 17 | **Primary** — trade, growth, labor, finance |
| `cbc_client.py` | CBC Open Data API | 5 | **Primary** — monetary policy, FX |
| `dgbas_client.py` | DGBAS Excel (.xls) | 6 | **Primary** — price indices (CPI/PPI) |
| `ndc_client.py` | NDC ZIP (ws.ndc.gov.tw) | 6 | **Primary** — 景氣燈號, signal components |

### Why This Split?

Each script is primary for indicators the others cannot provide:

| Script | Irreplaceable indicators |
|--------|------------------------|
| statgov | 外銷訂單金額, 出口/進口金額, TAIEX, 外匯存底 |
| CBC | 重貼現率, TWD/USD 日頻, 準備貨幣 |
| DGBAS Excel | CPI/核心CPI 指數值 (非年增率), 進出口物價指數 |
| NDC | 景氣燈號顏色, 9 個構成項目明細, 領先指標構成項目 |

## Indicators (30)

### Core (by group)

| Group | Indicators | Primary Source |
|-------|-----------|---------------|
| rates (2) | 重貼現率, 央行利率 | CBC |
| inflation (3) | CPI, 核心CPI, PPI | DGBAS Excel |
| growth (4) | GDP YoY%, IPI YoY%, 製造業 YoY%, 零售業 YoY% | statgov |
| labor (2) | 失業率, 季調失業率 | statgov |
| trade (7) | 外銷訂單, 出口/進口金額, 出口/進口 YoY%, 進出口物價指數 | statgov + DGBAS |
| cycle (5) | 景氣燈號(分數+顏色), 構成項目, 領先/同時指標 | NDC + statgov |
| forex (2) | TWD/USD, 外匯存底 | CBC + statgov |
| money (4) | M2, 準備貨幣, M2 YoY%, TAIEX | CBC + statgov |

### Stability Note

- **stat.gov.tw**: Extracts from Highcharts hidden field — functional but
  **not a documented API**. Page redesign could break it.
- **CBC API**: Documented official API — **most stable**.
- **DGBAS Excel**: Fixed URLs, stable format — **very stable**.
- **NDC ZIP**: Consistent file structure since 2016 — **stable**.

## Architecture

```
taiwan-macro/
├── SKILL.md
├── README.md
├── scripts/
│   ├── statgov_client.py      ← stat.gov.tw (17 presets)
│   ├── cbc_client.py          ← CBC API (5 presets)
│   ├── dgbas_client.py        ← DGBAS Excel/xlrd (6 presets)
│   ├── ndc_client.py          ← NDC ZIP/CSV (6 presets)
│   └── setup.sh
└── references/
    ├── indicator-index.md     ← 30 indicators trilingual index
    ├── indicators-rates.md
    ├── indicators-inflation.md
    ├── indicators-growth.md
    ├── indicators-labor.md
    ├── indicators-trade.md
    ├── indicators-cycle.md
    ├── indicators-other.md
    └── sources.md
```

## Setup

No API keys needed. All sources are free and unauthenticated.

```bash
uv run scripts/statgov_client.py --preset export-orders
uv run scripts/cbc_client.py --preset rediscount-rate
uv run scripts/dgbas_client.py --preset cpi
uv run scripts/ndc_client.py --preset signal
```

## Verification

```bash
cd investing-toolkit/scripts

# statgov (17)
for p in export-orders exports imports exports-yoy imports-yoy ipi \
  manufacturing-yoy retail-yoy gdp-yoy unemployment unemployment-sa \
  fx-reserves taiex m2-yoy leading-index coincident-index signal-score; do
  uv run statgov_client.py --preset "$p" --no-cache 2>&1 | python3 -c "
import json,sys;p='$p';d=json.load(sys.stdin);l=d.get('latest') or {}
print(f'{p:22} {l.get(\"date\",\"?\")} {str(l.get(\"value\",\"\")):>12}')
"; done

# CBC (5)
for p in rediscount-rate m2 twdusd reserve-money financial-sa; do
  uv run cbc_client.py --preset "$p" --no-cache 2>&1 | python3 -c "
import json,sys;p='$p';d=json.load(sys.stdin);l=d.get('latest') or {}
print(f'{p:22} {l.get(\"date\",\"?\")} {str(l.get(\"value\",\"\")):>12}')
"; done

# DGBAS Excel (6)
for p in cpi core-cpi cpi-sa ppi import-pi export-pi; do
  uv run dgbas_client.py --preset "$p" --no-cache 2>&1 | python3 -c "
import json,sys;p='$p';d=json.load(sys.stdin);l=d.get('latest') or {}
print(f'{p:22} {l.get(\"date\",\"?\")} {str(l.get(\"value\",\"\")):>12}')
"; done

# NDC (signal)
uv run ndc_client.py --preset signal --no-cache 2>&1 | python3 -c "
import json,sys;d=json.load(sys.stdin)
s=d.get('score',{}).get('latest',{});c=d.get('color',{}).get('latest',{})
print(f'signal-score           {s.get(\"date\",\"?\")} {s.get(\"value\",\"?\")}')
print(f'signal-color           {c.get(\"date\",\"?\")} {c.get(\"value\",\"?\")}')
"
```

### Latest verification

**Date**: 2026-04-17 — 30 indicators across 4 sources, all ACTIVE.
