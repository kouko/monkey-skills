# china-macro

China macroeconomic data skill for investing-toolkit.
中国宏观经济数据技能。中國宏觀經濟資料技能。

## Overview

Fetches 26 China macroeconomic indicators via akshare (NBS + PBOC + SHIBOR
mirrors), FRED (CNY/USD, FX reserves), and yfinance (CSI300/SSEC/ChiNext/
HSI/HSCEI) and returns structured JSON grouped by 10 indicator groups:
inflation, growth, trade, labor, sentiment, rates, money, credit, markets,
and fx.

## Data Sources (3 scripts)

| Script | Source | Indicators | Role |
|--------|--------|-----------|------|
| `akshare_client.py` | akshare (NBS/PBOC/SHIBOR/chinamoney mirrors) | 19 | **Primary** — macro indicators |
| `fred_client.py` | FRED CSV | 2 | CNY/USD (`DEXCHUS`) + FX reserves (`TRESEGCNM052N`) |
| `yfinance_client.py` | Yahoo Finance | 5 | CSI300, SSEC, ChiNext, HSI, HSCEI |

### Why Three Scripts?

- **akshare** — NBS `data.stats.gov.cn` WAF blocks non-mainland IPs (403
  `reason:UrlACL`). akshare aggregates equivalent data from reachable
  mirrors (eastmoney, investing.com, chinamoney.com.cn, shibor.org).
- **FRED** — akshare's `macro_china_foreign_exchange_gold` is broken
  upstream; FRED `TRESEGCNM052N` provides the same SAFE data via IMF
  pipeline. CNY/USD (`DEXCHUS`) is the standard daily rate from the
  Federal Reserve Board.
- **yfinance** — already a toolkit dependency; covers all 5 China and HK
  benchmark indices with no additional packages.

## Indicators (26)

### Core (by group)

| Group | Count | Indicators | Frequency |
|-------|-------|-----------|-----------|
| inflation | 2 | CPI YoY, PPI YoY | Monthly |
| growth | 3 | GDP YoY, Industrial Production YoY, Retail Sales YoY | Quarterly/Monthly |
| trade | 3 | Exports YoY, Imports YoY, Trade Balance | Monthly |
| labor | 1 | Urban Surveyed Unemployment | Monthly |
| sentiment | 2 | Manufacturing PMI (official), Non-Manufacturing PMI (official) | Monthly |
| rates | 4 | LPR 1Y, LPR 5Y, RRR, SHIBOR 3M | Daily/Monthly/Event |
| money | 2 | M1 YoY, M2 YoY | Monthly |
| credit | 2 | 社融 (Aggregate Financing), New RMB Loans | Monthly |
| markets | 5 | CSI 300, Shanghai Composite, ChiNext, HSI, HSCEI | Daily |
| fx | 2 | CNY/USD, FX Reserves ex-gold | Daily/Monthly |

### Stability Notes

- **akshare macro_china_cpi / _ppi / _gdp / _consumer_goods_retail /
  _pmi / _money_supply / _new_financial_credit / _lpr / _shibor_all**:
  Reliable — backed by eastmoney (a major financial portal), chinamoney
  (CFETS), and shibor.org. Fresh to within ~1 month.
- **akshare macro_china_industrial_production_yoy / _exports_yoy /
  _imports_yoy / _trade_balance**: Sourced from investing.com's free
  calendar feed — can be up to 8 months stale. Use as best-available
  fallback; mark freshness in analysis. (Caixin PMI presets
  `cx_pmi_yearly` / `cx_services_pmi_yearly` were removed 2026-04-18
  for the same staleness reason; see SKILL.md "Deliberately excluded
  indicators".)
- **FRED `DEXCHUS`, `TRESEGCNM052N`**: Official Federal Reserve / IMF data
  — very stable.
- **yfinance Yahoo Finance**: Standard daily feed, widely relied upon. ChiNext
  (`399006.SZ`) sometimes returns only latest close without history.

## Architecture

```
china-macro/
├── SKILL.md
├── README.md
├── scripts/
│   ├── akshare_client.py      ← 21 presets via akshare
│   ├── fred_client.py         ← 2 China series
│   ├── yfinance_client.py     ← 5 indices
│   └── setup.sh
└── references/
    ├── indicator-index.md     ← 28 indicators trilingual index
    ├── indicators-inflation.md
    ├── indicators-growth.md
    ├── indicators-trade.md
    ├── indicators-labor.md
    ├── indicators-sentiment.md
    ├── indicators-rates.md
    ├── indicators-money.md
    ├── indicators-markets.md
    ├── indicators-fx.md
    └── sources.md
```

## Setup

No API keys needed. akshare uses public mirrors; FRED CSV and Yahoo Finance
require no auth.

```bash
uv run scripts/akshare_client.py --preset cpi-yoy
uv run scripts/akshare_client.py --preset lpr-1y,m2-yoy,new-loans
uv run scripts/akshare_client.py --preset all
uv run scripts/fred_client.py --series DEXCHUS,TRESEGCNM052N --periods 12
uv run scripts/yfinance_client.py --tickers "000300.SS,^HSI,^HSCE"
```

## Verification

```bash
cd investing-toolkit/scripts

# All 21 akshare presets
uv run akshare_client.py --preset all --no-cache 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
for k, v in d['indicators'].items():
    if 'error' in v:
        print(f'!!! {k}: {v[\"error\"]}')
    else:
        L = v.get('latest') or {}
        stale = v.get('_provenance',{}).get('staleness_days')
        print(f'OK {k:27s} latest={L.get(\"date\")} = {L.get(\"value\")} stale={stale}d')
"
```

### Latest verification

**Date**: 2026-04-17 — 28 indicators, all ACTIVE. 21 via akshare + 2 via
FRED + 5 via yfinance. Stale indicators (industrial-yoy, exports/imports/
trade-balance, caixin PMIs) flagged in SKILL.md Limitations section.
