# china-macro

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

China macroeconomic data skill for investing-toolkit.
中国宏观经济数据技能。中國宏觀經濟資料技能。

## Overview

Fetches 34 China macroeconomic indicators from four sources: NBS (direct via
reverse-engineered new-SPA API, 2026-04 migration), PBOC/SHIBOR via akshare,
FRED (CNY/USD + FX reserves), and yfinance (5 equity indices). Returns
structured JSON grouped by 12 indicator groups.

**Monthly GDP proxy**: The 三大数据 (`industrial-yoy` / `retail-yoy` /
`fai-yoy`) + `services-production-yoy` collectively proxy monthly GDP
momentum, parallel to us-macro's `nowcast` group and japan-macro's
景気動向指数 CI trio. China has **no authoritative monthly composite** —
Li Keqiang Index / SF Fed CAT / Goldman CAI / academic DFM methodologies
do not converge. This skill intentionally keeps the 4 components raw;
synthesis is deferred to analysis layer (investing-team).

## Data Sources (4 scripts)

| Script | Source | Indicators | Role |
|--------|--------|-----------|------|
| `nbs_client.py` | NBS new-SPA API (`data.stats.gov.cn/dg/website/publicrelease/web/external/*`) | **21** | **Primary source** — all NBS monthly+quarterly data |
| `akshare_client.py` | PBOC (chinamoney) + SHIBOR (shibor.org) via akshare | 6 | PBOC-only: LPR×2, RRR, SHIBOR, 社融增量, new loans |
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

## Indicators (34)

### Core (by group)

| Group | Count | Indicators | Frequency |
|-------|-------|-----------|-----------|
| inflation | 3 | CPI YoY, Core CPI, PPI YoY | Monthly |
| growth | 4 | GDP YoY, Industrial Production YoY, Retail Sales YoY, FAI YoY | Quarterly/Monthly |
| trade | 3 | Exports YoY, Imports YoY, Trade Balance | Monthly |
| labor | 1 | Urban Surveyed Unemployment | Monthly |
| sentiment | 3 | Mfg / Non-Mfg / Composite PMI (NBS official) | Monthly |
| realestate | 4 | Investment / Sales area / Sales value / Funding | Monthly |
| services | 1 | Services Production Index | Monthly |
| rates | 4 | LPR 1Y, LPR 5Y, RRR, SHIBOR 3M | Daily/Monthly/Event |
| money | 2 | M1 YoY, M2 YoY | Monthly |
| credit | 2 | 社融 (Aggregate Financing), New RMB Loans | Monthly |
| markets | 5 | CSI 300, Shanghai Composite, ChiNext, HSI, HSCEI | Daily |
| fx | 2 | CNY/USD, FX Reserves ex-gold | Daily/Monthly |

### Stability Notes

- **NBS direct via `nbs_client.py`** — primary source. Reachable from
  Taiwan + Anthropic IPs. WAF trips on bulk traversal (100+ requests),
  so all `(cid, indicator_id)` pairs are statically pinned; no runtime
  discovery. Base-period revisions happen every ~5 years and will
  require catalog refresh; see `docs/tools/README.md`.
- **akshare PBOC presets**: backed by chinamoney (CFETS) and shibor.org.
  Fresh to within ~1 month.
- **FRED `DEXCHUS`, `TRESEGCNM052N`**: Official Fed / IMF data — very stable.
- **yfinance**: Standard daily feed.
- **Caixin PMI** presets removed 2026-04-18 (stale mirror, no fresh source).
  See SKILL.md "Deliberately excluded indicators".
- **70-city housing price index** not included — NBS doesn't expose it
  via `queryIndexTreeAsync` (only PDF publication). Deferred.

## Architecture

```
china-macro/
├── SKILL.md
├── README.md
├── scripts/
│   ├── nbs_client.py          ← 21 presets via NBS new-SPA API (PRIMARY)
│   ├── akshare_client.py      ← 6 PBOC presets
│   ├── fred_client.py         ← 2 China FX series
│   ├── yfinance_client.py     ← 5 indices
│   └── setup.sh
├── docs/                       ← developer reference material
│   ├── nbs-indicator-catalog.md
│   ├── china-macro-research-frameworks.md
│   ├── nbs-tree-*.md + nbs-indicators-*.{json,md}
│   └── tools/ (probe scripts)
└── references/
    ├── indicator-index.md     ← 34 indicators trilingual index
    ├── indicators-inflation.md
    ├── indicators-growth.md
    ├── indicators-trade.md
    ├── indicators-labor.md
    ├── indicators-sentiment.md
    ├── indicators-rates.md
    ├── indicators-money.md
    ├── indicators-realestate.md
    ├── indicators-services.md
    ├── indicators-markets.md
    ├── indicators-fx.md
    └── sources.md
```

## Setup

No API keys needed. NBS, FRED, Yahoo Finance, akshare endpoints are all
no-auth.

```bash
# NBS direct (primary source, 21 indicators)
uv run scripts/nbs_client.py --preset cpi-yoy
uv run scripts/nbs_client.py --preset industrial-yoy,exports-yoy,trade-balance
uv run scripts/nbs_client.py --preset all

# PBOC via akshare (6 indicators)
uv run scripts/akshare_client.py --preset lpr-1y,shibor-3m,new-loans
uv run scripts/akshare_client.py --preset all

# FRED (2) + yfinance (5)
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
