---
name: japan-macro
description: >-
  Fetch Japan macroeconomic indicators via BOJ Time-Series API and
  Statistics Dashboard (統計ダッシュボード) API. Data layer only — no analysis
  or regime mapping. Returns structured JSON with latest values and direction
  for rates, inflation, growth, tankan, forex, money, and balance indicator
  groups. Designed for handoff to macro-regime-snapshot or
  domain-teams:investing-team. 日本マクロ指標取得（日銀API＋統計DB）。
  日本總經指標擷取（BOJ + 統計Dashboard）。
---

# Japan Macro

Fetches Japan macroeconomic indicators from two government data sources and
outputs structured JSON:

- **BOJ Time-Series Statistics** (`boj_client.py`) — Bank of Japan data
  (rates, CGPI, money stock, TANKAN, forex, balance of payments)
- **Statistics Dashboard / 統計ダッシュボード** (`estat_client.py`) — e-Stat
  data (CPI, unemployment, industrial production, GDP, JGB yields)

This skill is **data-only** — it does not analyze, map to regimes, or generate
investment verdicts. The output is designed for immediate handoff to
`macro-regime-snapshot` for IC/GIP regime mapping, or to
`domain-teams:investing-team` for full analysis.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `--indicators` | no | `all` | Comma-separated group names: `rates`, `inflation`, `growth`, `labor`, `consumption`, `tankan`, `forex`, `money`, `balance`, or `all` |

---

## Indicator Groups

### rates

| Source | DB/Preset | Code/ID | Name | Frequency |
|--------|-----------|---------|------|-----------|
| BOJ | FM01 | STRDCLUCON | 無担保コールO/N物レート | Daily |
| 統計DB | jgb10y | 0702020300000010020 | 新発10年国債利回り | Monthly |

### inflation

| Source | DB/Preset | Code/ID | Name | Frequency |
|--------|-----------|---------|------|-----------|
| BOJ | PR01 | (discover via getMetadata) | 企業物価指数 CGPI | Monthly |
| 統計DB | cpi | 0703010501010030000 | 消費者物価指数 CPI | Monthly |
| 統計DB | core-cpi | 0703010501010030010 | コアCPI | Monthly |

### growth

| Source | DB/Preset | Code/ID | Name | Frequency |
|--------|-----------|---------|------|-----------|
| 統計DB | ip | 0502070301000090010 | 鉱工業生産指数 | Monthly |
| 統計DB | unemployment | 0301010000020020010 | 完全失業率 | Monthly |
| 統計DB | gdp | (discover via search) | GDP | Quarterly (use `--cycle quarterly`) |
| 統計DB | coincident-index | 0706010500000090010 | 景気動向指数 CI 一致指数 (**monthly GDP proxy**) | Monthly |
| 統計DB | leading-index | 0706010500000090020 | 景気動向指数 CI 先行指数 | Monthly |
| 統計DB | lagging-index | 0706010500000090030 | 景気動向指数 CI 遅行指数 | Monthly |
| 統計DB | machine-orders | 0701030000000010010 | 機械受注額 | Monthly |
| 統計DB | tertiary-index | 0603100300000090010 | 第3次産業活動指数 | Monthly |

### labor

| Source | DB/Preset | Code/ID | Name | Frequency |
|--------|-----------|---------|------|-----------|
| 統計DB | real-wages | 0302030201010090010 | 実質賃金指数 | Monthly |
| 統計DB | job-ratio | 0301020001000010020 | 有効求人倍率 | Fiscal-year (use `--cycle fiscal-year`) |

### consumption

| Source | DB/Preset | Code/ID | Name | Frequency |
|--------|-----------|---------|------|-----------|
| 統計DB | retail-sales | 0601010201010010000 | 小売業販売額 | Monthly |
| 統計DB | service-sales | 0603010200000010000 | サービス産業売上高 | Monthly |

### money

| Source | DB/Preset | Code/ID | Name | Frequency |
|--------|-----------|---------|------|-----------|
| BOJ | MD02 | (discover via getMetadata) | マネーストック M2 | Monthly |

### tankan

| Source | DB/Preset | Code/ID | Name | Frequency |
|--------|-----------|---------|------|-----------|
| BOJ | CO | (discover via getMetadata) | 短観 業況判断DI | Quarterly |

### forex

| Source | DB/Preset | Code/ID | Name | Frequency |
|--------|-----------|---------|------|-----------|
| BOJ | FM08 | (discover via getMetadata) | USD/JPY 外国為替市況 | Daily |
| BOJ | FM09 | (discover via getMetadata) | 実効為替レート | Monthly |

### balance

| Source | DB/Preset | Code/ID | Name | Frequency |
|--------|-----------|---------|------|-----------|
| BOJ | BP01 | (discover via getMetadata) | 経常収支 | Monthly |

---

## How It Works

### Step 1 — Resolve series list

Map `--indicators` to BOJ and 統計DB series:

| Input | BOJ series | 統計DB presets |
|-------|-----------|---------------|
| `rates` | FM01:STRDCLUCON | jgb10y |
| `inflation` | PR01:(discover) | cpi, core-cpi |
| `growth` | (none) | ip, unemployment, gdp (quarterly), coincident-index, leading-index, lagging-index, machine-orders, tertiary-index |
| `labor` | (none) | real-wages, job-ratio (fiscal-year) |
| `consumption` | (none) | retail-sales, service-sales |
| `money` | MD02:(discover) | (none) |
| `tankan` | CO:(discover) | (none) |
| `forex` | FM08:(discover), FM09:(discover) | (none) |
| `balance` | BP01:(discover) | (none) |
| `all` | All BOJ series above | All presets above |

For BOJ series marked "(discover via getMetadata)", the data-fetcher agent
must first call the BOJ API's `getMetadata` endpoint for the given DB to
identify the correct series code, then fetch data with that code.

### Step 2 — Launch data-fetcher agent for BOJ series

Launch `../../agents/data-fetcher.md` with BOJ fetch requests:

```
### Task
Fetch Japan macro indicators from BOJ. Return structured JSON.
Do not analyze or interpret.

### Scripts
base_path: {absolute path to investing-toolkit/scripts/}

### Fetch Requests
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/boj_client.py --db FM01 --code STRDCLUCON --start-date {YYYYMM}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/boj_client.py --db PR01 --code {discovered} --start-date {YYYYMM}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/boj_client.py --db MD02 --code {discovered} --start-date {YYYYMM}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/boj_client.py --db CO --code {discovered} --start-date {YYYYMM}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/boj_client.py --db FM08 --code {discovered} --start-date {YYYYMM}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/boj_client.py --db FM09 --code {discovered} --start-date {YYYYMM}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/boj_client.py --db BP01 --code {discovered} --start-date {YYYYMM}

### Output Format
Return raw JSON from each fetch request.
```

Only include fetch requests for the resolved indicator groups.

### Step 3 — Launch data-fetcher agent for 統計DB series

Launch `../../agents/data-fetcher.md` with 統計DB fetch requests:

```
### Task
Fetch Japan macro indicators from Statistics Dashboard. Return structured JSON.
Do not analyze or interpret.

### Scripts
base_path: {absolute path to investing-toolkit/scripts/}

### Fetch Requests
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/estat_client.py --preset jgb10y
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/estat_client.py --preset cpi,core-cpi
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/estat_client.py --preset ip,unemployment,coincident-index,leading-index,lagging-index,machine-orders,tertiary-index
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/estat_client.py --preset real-wages
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/estat_client.py --preset job-ratio --cycle fiscal-year
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/estat_client.py --preset retail-sales,service-sales
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/estat_client.py --preset gdp --cycle quarterly

### Output Format
Return raw JSON from each fetch request.
```

Only include fetch requests for the resolved indicator groups. Use
`--cycle quarterly` for GDP.

### Step 4 — Merge into unified output

Combine BOJ and 統計DB results into a single JSON structure grouped by
indicator group. Each data point retains its `"_source"` tag (`"boj"` or
`"estat_dashboard"`).

---

## Output Format

```json
{
  "fetched_at": "2026-04-16T08:50:00Z",
  "groups": {
    "rates": {
      "call_rate_on": { "latest": { "date": "...", "value": ... }, "prior": { "date": "...", "value": ... }, "direction": "...", "_source": "boj" },
      "jgb10y":      { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" }
    },
    "inflation": {
      "cgpi":     { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "boj" },
      "cpi":      { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" },
      "core_cpi": { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" }
    },
    "growth": {
      "ip":              { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" },
      "unemployment":    { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" },
      "gdp":             { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" },
      "coincident_index":{ "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" },
      "leading_index":   { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" },
      "lagging_index":   { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" },
      "machine_orders":  { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" },
      "tertiary_index":  { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" }
    },
    "labor": {
      "real_wages": { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" },
      "job_ratio":  { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" }
    },
    "consumption": {
      "retail_sales":  { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" },
      "service_sales": { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "estat_dashboard" }
    },
    "money": {
      "m2": { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "boj" }
    },
    "tankan": {
      "tankan_di": { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "boj" }
    },
    "forex": {
      "usdjpy": { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "boj" },
      "reer":   { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "boj" }
    },
    "balance": {
      "current_account": { "latest": { ... }, "prior": { ... }, "direction": "...", "_source": "boj" }
    }
  }
}
```

---

## Reference

For detailed documentation on each indicator (units, frequency, publication
lag, interpretation, Japan-specific context, common pitfalls):

- `references/indicator-index.md` — Quick lookup index for all indicators (bilingual)
- `references/indicators-rates.md` — 金利系: Call Rate, Discount Rate, 10Y JGB Yield + Tier 2
- `references/indicators-inflation.md` — 物價系: CPI, CGPI + Tier 2
- `references/indicators-growth.md` — 成長系: GDP, IP, CI 先行/一致/遅行 (monthly GDP proxy trio), Machine Orders, Tertiary Index
- `references/indicators-labor.md` — 雇用系: Unemployment, Real Wages, Job Ratio
- `references/indicators-consumption.md` — 消費系: Retail Sales, Service Industry Sales
- `references/indicators-other.md` — その他: M2, TANKAN, USD/JPY, REER, Current Account + Tier 2
- `references/japan-boj-db-catalog.md` — Complete BOJ DB catalog (Tier 3, bilingual)

---

## Limitations

### Publication lags

| Series | Typical lag |
|--------|-------------|
| Call Rate (FM01) | 1 business day |
| USD/JPY (FM08), REER (FM09) | 1-2 business days |
| CGPI (PR01) | ~2 weeks after reference month |
| CPI, Core CPI (統計DB) | ~3-4 weeks after reference month |
| IP (統計DB) | ~6 weeks after reference month |
| Unemployment (統計DB) | ~4 weeks after reference month |
| Money Stock M2 (MD02) | ~2 weeks after reference month |
| TANKAN (CO) | Quarterly, ~1 week after quarter-end survey |
| Current Account (BP01) | ~6 weeks after reference month |
| GDP (統計DB) | ~6 weeks (1st preliminary), quarterly |
| JGB 10Y Yield (統計DB) | ~1 week after month-end |
| Coincident / Leading / Lagging Index (統計DB) | ~6-8 weeks after reference month (CI trio released together by 内閣府) |
| Machine Orders (統計DB) | ~6 weeks after reference month |
| Real Wages (統計DB) | ~5 weeks after reference month |
| Job Ratio (統計DB) | Fiscal-year data; ~4 weeks after FY-end (original MHLW is monthly) |
| Tertiary Index (統計DB) | ~6 weeks after reference month |
| Retail Sales (統計DB) | ~4 weeks after reference month |
| Service Industry Sales (統計DB) | ~6 weeks after reference month |

Always check the `latest.date` field to confirm the reference period.

### Japan-specific timing

- BOJ data updates at **8:50 AM JST** (23:50 UTC previous day)
- 統計ダッシュボード update schedule varies by indicator and managing agency
- TANKAN is published 4x/year (April, July, October, December survey months)

### BOJ series code discovery

Some BOJ databases have complex code structures that change with base-year
revisions. For series marked "(discover via getMetadata)", the agent must
query the BOJ `getMetadata` API to find the current valid code before
fetching data. This is necessary for PR01, MD02, CO, FM08, FM09, and BP01.

---

## Cross-Plugin Handoff

```
japan-macro (this skill) -> macro-regime-snapshot -> domain-teams:investing-team
```

1. `japan-macro` (this skill) -- fetch BOJ + 統計DB data, return structured JSON
2. `macro-regime-snapshot` -- map to IC phase + GIP quadrant, output regime call
3. `domain-teams:investing-team` -- full analysis, conviction, portfolio implications

Pass the output JSON verbatim as the `### Input` section when launching
`macro-regime-snapshot`.
