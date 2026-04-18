---
name: taiwan-macro
description: >-
  Fetch Taiwan macroeconomic indicators via stat.gov.tw, CBC API, DGBAS Excel,
  and NDC business cycle data. Data layer only — no analysis or regime mapping.
  Returns structured JSON with latest values and direction for rates, inflation,
  growth, labor, trade, cycle, forex, and money indicator groups.
  台灣總經指標擷取（stat.gov.tw＋央行＋主計總處＋國發會）。
  台湾マクロ指標取得（stat.gov.tw＋CBC＋DGBAS＋NDC）。
---

# Taiwan Macro

Fetches Taiwan macroeconomic indicators from four government data sources:

- **stat.gov.tw** (`statgov_client.py`) — National Statistics hidden chart
  data: export orders, exports/imports, GDP, unemployment, IPI, TAIEX,
  FX reserves (17 presets, pure GET, no auth)
- **CBC API** (`cbc_client.py`) — Central Bank: rediscount rate, M2,
  TWD/USD, reserve money (5 presets)
- **DGBAS Excel** (`dgbas_client.py`) — Price indices: CPI, core CPI,
  PPI, import/export price indices (6 presets)
- **NDC ZIP** (`ndc_client.py`) — Business cycle: 景氣燈號 score + color,
  9 signal components, leading/coincident/lagging indices, unemployment
  (6 presets)

This skill is **data-only**. The output is designed for handoff to
`macro-regime-snapshot` or `domain-teams:investing-team`.

**Monthly GDP proxy note**: Taiwan's official GDP is quarterly. The
**景氣對策信號 + CI pair** (`signal` + `leading-index` + `coincident-index`),
published monthly by NDC and stat.gov.tw, collectively proxy monthly GDP
momentum — parallel to us-macro's `nowcast` group, japan-macro's 景気
動向指数 CI trio, and china-macro's 三大数据. NDC/DGBAS already publish
pre-aggregated CI values so no synthesis is needed. Uniquely, Taiwan
also provides the **五色景氣燈號** dashboard (紅/黃紅/綠/黃藍/藍) via
`signal` — a NDC特色 not found in other markets.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `--indicators` | no | `all` | Comma-separated: `rates`, `inflation`, `growth`, `labor`, `trade`, `cycle`, `forex`, `money`, or `all` |

---

## Indicator Groups

### rates

| Source | Preset | Name | Frequency |
|--------|--------|------|-----------|
| CBC | rediscount-rate | 重貼現率 Rediscount Rate | Monthly |
| CBC | rates-daily | 央行利率 CBC Interest Rates | Daily |

### inflation

| Source | Preset | Name | Frequency |
|--------|--------|------|-----------|
| DGBAS Excel | cpi | 消費者物價指數 CPI | Monthly |
| DGBAS Excel | core-cpi | 核心CPI (不含蔬果及能源) | Monthly |
| DGBAS Excel | ppi | 躉售物價指數 PPI | Monthly |

### growth

| Source | Preset | Name | Frequency |
|--------|--------|------|-----------|
| statgov | gdp-yoy | 經濟成長率 GDP Growth YoY% | Quarterly |
| statgov | ipi | 工業生產指數年增率 IPI YoY% | Monthly |
| statgov | manufacturing-yoy | 製造業生產指數年增率 | Monthly |
| statgov | retail-yoy | 零售業營業額年增率 | Monthly |

### labor

| Source | Preset | Name | Frequency |
|--------|--------|------|-----------|
| statgov | unemployment | 失業率 Unemployment Rate % | Monthly |
| statgov | unemployment-sa | 季調失業率 SA Unemployment % | Monthly |

### trade

| Source | Preset | Name | Frequency |
|--------|--------|------|-----------|
| statgov | export-orders | 外銷訂單 Export Orders (百萬USD) | Monthly |
| statgov | exports | 出口金額 Exports (億USD) | Monthly |
| statgov | imports | 進口金額 Imports (億USD) | Monthly |
| statgov | exports-yoy | 出口年增率 Exports YoY% | Monthly |
| statgov | imports-yoy | 進口年增率 Imports YoY% | Monthly |
| DGBAS Excel | import-pi | 進口物價指數 Import PI | Monthly |
| DGBAS Excel | export-pi | 出口物價指數 Export PI | Monthly |

### cycle — monthly GDP proxy components

| Source | Preset | Name | Frequency |
|--------|--------|------|-----------|
| NDC | signal | 景氣對策信號 score + 五色燈號 (**monthly GDP proxy, Taiwan 特色**) | Monthly |
| statgov | leading-index | 景氣領先指標不含趨勢 (**monthly GDP proxy leading**) | Monthly |
| statgov | coincident-index | 景氣同時指標不含趨勢 (**monthly GDP proxy coincident**) | Monthly |
| NDC | signal-components | 9 構成項目 (IPI, M1B, TAIEX...) | Monthly |
| NDC | leading | 領先指標構成項目 | Monthly |

### forex

| Source | Preset | Name | Frequency |
|--------|--------|------|-----------|
| CBC | twdusd | TWD/USD 匯率 | Daily |
| statgov | fx-reserves | 外匯存底 FX Reserves (十億USD) | Monthly |

### money

| Source | Preset | Name | Frequency |
|--------|--------|------|-----------|
| CBC | m2 | 貨幣總計數 M2 | Monthly |
| CBC | reserve-money | 準備貨幣 Reserve Money | Monthly |
| statgov | m2-yoy | M2 年增率 | Monthly |
| statgov | taiex | 加權股價指數 TAIEX (月均) | Monthly |

---

## How It Works

### Step 1 — Resolve series list

| Input | statgov | CBC | DGBAS Excel | NDC |
|-------|---------|-----|-------------|-----|
| `rates` | — | rediscount-rate, rates-daily | — | — |
| `inflation` | — | — | cpi, core-cpi, ppi | — |
| `growth` | gdp-yoy, ipi, manufacturing-yoy, retail-yoy | — | — | — |
| `labor` | unemployment, unemployment-sa | — | — | — |
| `trade` | export-orders, exports, imports | — | import-pi, export-pi | — |
| `cycle` | leading-index, coincident-index | — | — | signal, signal-components |
| `forex` | fx-reserves | twdusd | — | — |
| `money` | m2-yoy, taiex | m2, reserve-money | — | — |

### Step 2 — Launch data-fetcher agents

```
### Fetch Requests (statgov)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/statgov_client.py --preset export-orders,exports,imports
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/statgov_client.py --preset gdp-yoy,ipi,unemployment
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/statgov_client.py --preset fx-reserves,taiex,m2-yoy,leading-index

### Fetch Requests (CBC)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/cbc_client.py --preset rediscount-rate,twdusd,m2,reserve-money

### Fetch Requests (DGBAS Excel)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/dgbas_client.py --preset cpi,core-cpi,ppi,import-pi,export-pi

### Fetch Requests (NDC)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/ndc_client.py --preset signal,signal-components
```

### Step 3 — Merge into unified output

Each data point retains `_source`: `"statgov"`, `"cbc"`, `"dgbas"`, or `"ndc"`.

---

## Reference

- `references/indicator-index.md` — Quick lookup (trilingual)
- `references/indicators-rates.md` — 利率系
- `references/indicators-inflation.md` — 物價系
- `references/indicators-growth.md` — 成長系 (GDP, IPI)
- `references/indicators-labor.md` — 勞動系
- `references/indicators-trade.md` — 貿易系 (export orders, exports/imports)
- `references/indicators-cycle.md` — 景氣系
- `references/indicators-other.md` — 匯率, M2, TAIEX, FX reserves
- `references/sources.md` — Primary sources

---

## Limitations

### Publication lags

| Series | Typical lag |
|--------|-------------|
| TWD/USD (CBC) | 1 business day |
| CBC Interest Rates | 1 business day |
| Rediscount Rate (CBC) | Same day |
| CPI, Core CPI, PPI (DGBAS) | ~3-4 weeks |
| Export Orders (statgov) | ~3 weeks (每月20日) |
| Exports, Imports (statgov) | ~2 weeks |
| IPI, Manufacturing (statgov) | ~4 weeks |
| GDP (statgov) | ~6 weeks, quarterly |
| Unemployment (statgov) | ~4 weeks |
| 景氣燈號 (NDC) | ~6 weeks |
| TAIEX, FX Reserves (statgov) | ~2 weeks |

### SSL certificates

All Taiwan government sites have SSL certificate issues. All scripts use
`verify=False`.

### stat.gov.tw fragility

The `statgov_client.py` extracts data from an HTML hidden field
(`#ContentPlaceHolder1_hidChartData`) that contains Highcharts JSON. This
is **not a documented API** — it works because the server renders the chart
data server-side. A page redesign could break this. CBC API and DGBAS Excel
are more stable as they are documented interfaces.

---

## Cross-Plugin Handoff

```
taiwan-macro (this skill) -> macro-regime-snapshot -> domain-teams:investing-team
```
