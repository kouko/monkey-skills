---
name: china-macro
description: >-
  Fetch China macroeconomic indicators from NBS (primary-source via
  reverse-engineered new-SPA API), PBOC (via akshare — LPR/RRR/SHIBOR/社融/
  new loans), FRED (CNY/USD + FX reserves), and yfinance (CSI300/SSEC/
  ChiNext/HSI/HSCEI). Data layer only — no analysis. Returns structured
  JSON with latest values and direction for inflation, growth, trade,
  labor, sentiment, rates, money, credit, real estate, services, markets,
  and FX groups.
  中国宏观经济指标取数 (NBS 直抓 + PBOC)。
  中國宏觀經濟資料擷取（國家統計局直抓 + 人民銀行）。
---

# China Macro

Fetches 34 Chinese macroeconomic indicators from four sources, prioritising
primary-source freshness. No API key required.

| Script | Source | # presets | Role |
|---|---|---|---|
| **`nbs_client.py`** | **NBS new-SPA API** (`data.stats.gov.cn/dg/website/publicrelease/web/external/*`) | **21** | Primary source for all NBS-published indicators: CPI/PPI/GDP/industrial/retail/FAI/trade/labor/PMI/money/real-estate/services |
| `akshare_client.py` | PBOC via chinamoney / SHIBOR via shibor.org | 6 | PBOC-only data not in NBS: LPR×2, RRR, SHIBOR, 社融增量, new loans |
| `fred_client.py` | FRED CSV | 2 | CNY/USD (`DEXCHUS`), FX reserves (`TRESEGCNM052N`) |
| `yfinance_client.py` | Yahoo Finance | 5 | Market indices: CSI 300, SSEC, ChiNext, HSI, HSCEI |

**Primary-source design**: `nbs_client.py` calls NBS's own API directly
(verified reachable from TW + Anthropic IPs). Replaces earlier
stale-mirror dependencies (investing.com calendar feed was 8 months
behind on industrial/trade). See `docs/nbs-indicator-catalog.md` for
full API docs + `docs/china-macro-research-frameworks.md` for the
3-language industry synthesis that drove preset selection.

This skill is **data-only**. Output is designed for handoff to
`macro-regime-snapshot` or `domain-teams:investing-team`.

**Monthly GDP proxy note**: China publishes official GDP quarterly
(`gdp-yoy`). The **三大数据 monthly trio** (`industrial-yoy` +
`retail-yoy` + `fai-yoy`) plus `services-production-yoy` collectively
**proxy monthly GDP momentum**, parallel to us-macro's `nowcast` group
and japan-macro's 景気動向指数 CI trio. Unlike US/JP where Fed / 内閣府
publish pre-aggregated nowcasts (GDPNow, 一致指数), NBS does not publish
a single-number composite. Proposed aggregators (Li Keqiang Index,
SF Fed CAT, Goldman CAI, academic DFM) have no market consensus, so
this skill intentionally keeps the 4 components raw — synthesis belongs
in analysis layer (investing-team). See
`docs/china-macro-research-frameworks.md §1d` for the methodology
discussion and deferred options.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `--indicators` | no | `all` | Comma-separated: `inflation`, `growth`, `trade`, `labor`, `sentiment`, `rates`, `money`, `credit`, `realestate`, `services`, `markets`, `fx`, or `all` |

---

## Indicator Groups

### inflation (NBS)

| Preset | Source | Name | Frequency |
|--------|--------|------|-----------|
| cpi-yoy | nbs_client | CPI YoY / 居民消费价格指数 同比 | Monthly |
| core-cpi | nbs_client | Core CPI / 不包括食品和能源 CPI | Monthly |
| ppi-yoy | nbs_client | PPI YoY / 工业生产者出厂价格指数 | Monthly |

### growth (NBS, 三大数据 — monthly GDP proxy components)

| Preset | Source | Name | Frequency |
|--------|--------|------|-----------|
| gdp-yoy | nbs_client | GDP YoY / 国内生产总值指数 同比 | Quarterly |
| industrial-yoy | nbs_client | Industrial Production YoY / 规上工业增加值 同比 (**monthly GDP proxy component**) | Monthly |
| retail-yoy | nbs_client | Retail Sales YoY / 社会消费品零售总额 同比 (**monthly GDP proxy component**) | Monthly |
| fai-yoy | nbs_client | FAI YoY (累计) / 固定资产投资 累计同比 (**monthly GDP proxy component**) | Monthly |

### trade (NBS, GAC via NBS)

| Preset | Source | Name | Frequency |
|--------|--------|------|-----------|
| exports-yoy | nbs_client | Exports YoY USD / 出口总值 同比 | Monthly |
| imports-yoy | nbs_client | Imports YoY USD / 进口总值 同比 | Monthly |
| trade-balance | nbs_client | Trade Balance USD / 进出口差额 当期值 | Monthly |

### labor (NBS)

| Preset | Source | Name | Frequency |
|--------|--------|------|-----------|
| urban-unemployment | nbs_client | 全国城镇调查失业率 | Monthly |

### sentiment (NBS)

| Preset | Source | Name | Frequency |
|--------|--------|------|-----------|
| pmi-manufacturing | nbs_client | Mfg PMI (官方) / 制造业采购经理指数 | Monthly |
| pmi-non-manufacturing | nbs_client | Non-Mfg PMI / 非制造业商务活动指数 | Monthly |
| pmi-composite | nbs_client | Composite PMI / 综合PMI产出指数 | Monthly |

### money (NBS)

| Preset | Source | Name | Frequency |
|--------|--------|------|-----------|
| m2-yoy | nbs_client | M2 YoY / 广义货币 同比 | Monthly |
| m1-yoy | nbs_client | M1 YoY / 狭义货币 同比 | Monthly |

### rates (PBOC / SHIBOR via akshare)

| Preset | Source | Name | Frequency |
|--------|--------|------|-----------|
| lpr-1y | akshare_client | Loan Prime Rate 1Y / 贷款市场报价利率 1年期 | Monthly |
| lpr-5y | akshare_client | Loan Prime Rate 5Y / 贷款市场报价利率 5年期 | Monthly |
| rrr-major | akshare_client | RRR 大型金融机构 存款准备金率 | Event |
| shibor-3m | akshare_client | SHIBOR 3M / 上海银行间同业拆放利率 | Daily |

### credit (PBOC via akshare)

| Preset | Source | Name | Frequency |
|--------|--------|------|-----------|
| shrzgm | akshare_client | Aggregate Financing / 社会融资规模 增量 | Monthly |
| new-loans | akshare_client | New RMB Loans / 人民币贷款增量 | Monthly |

### realestate (NBS)

| Preset | Source | Name | Frequency |
|--------|--------|------|-----------|
| realestate-investment-yoy | nbs_client | 房地产开发投资 累计同比 | Monthly |
| housing-sales-area-yoy | nbs_client | 商品住宅销售面积 累计同比 | Monthly |
| housing-sales-value-yoy | nbs_client | 商品住宅销售额 累计同比 | Monthly |
| realestate-funding-yoy | nbs_client | 房地产投资本年资金来源 累计同比 | Monthly |

### services (NBS)

| Preset | Source | Name | Frequency |
|--------|--------|------|-----------|
| services-production-yoy | nbs_client | 服务业生产指数 当月同比 (**monthly GDP proxy companion**) | Monthly |

### markets (yfinance)

| Ticker | Name | Frequency |
|--------|------|-----------|
| `000300.SS` | CSI 300 / 沪深300 | Daily |
| `000001.SS` | Shanghai Composite / 上证综指 | Daily |
| `399006.SZ` | ChiNext / 创业板指 | Daily |
| `^HSI` | Hang Seng / 恒生指数 | Daily |
| `^HSCE` | Hang Seng China Enterprises / 国企指数 | Daily |

### fx (FRED)

| Series | Name | Frequency |
|--------|------|-----------|
| `DEXCHUS` | CNY/USD 汇率 | Daily |
| `TRESEGCNM052N` | FX Reserves ex-gold / 国家外汇储备 | Monthly |

---

## How It Works

### Step 1 — Resolve indicator list

| Input | Presets / tickers |
|-------|-------------------|
| `inflation` | cpi-yoy, core-cpi, ppi-yoy |
| `growth` | gdp-yoy, industrial-yoy, retail-yoy, fai-yoy |
| `trade` | exports-yoy, imports-yoy, trade-balance |
| `labor` | urban-unemployment |
| `sentiment` | pmi-manufacturing, pmi-non-manufacturing, pmi-composite |
| `money` | m2-yoy, m1-yoy |
| `rates` | lpr-1y, lpr-5y, rrr-major, shibor-3m |
| `credit` | shrzgm, new-loans |
| `realestate` | realestate-investment-yoy, housing-sales-area-yoy, housing-sales-value-yoy, realestate-funding-yoy |
| `services` | services-production-yoy |
| `markets` | 000300.SS, 000001.SS, 399006.SZ, ^HSI, ^HSCE |
| `fx` | DEXCHUS, TRESEGCNM052N |

### Step 2 — Launch data-fetcher agents

```
### Fetch Requests (NBS — inflation + growth + trade + labor)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/nbs_client.py --preset cpi-yoy,core-cpi,ppi-yoy,gdp-yoy,industrial-yoy,retail-yoy,fai-yoy,exports-yoy,imports-yoy,trade-balance,urban-unemployment

### Fetch Requests (NBS — sentiment + money + real estate + services)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/nbs_client.py --preset pmi-manufacturing,pmi-non-manufacturing,pmi-composite,m2-yoy,m1-yoy,realestate-investment-yoy,housing-sales-area-yoy,housing-sales-value-yoy,realestate-funding-yoy,services-production-yoy

### Fetch Requests (PBOC via akshare — rates + credit)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/akshare_client.py --preset lpr-1y,lpr-5y,rrr-major,shibor-3m,shrzgm,new-loans

### Fetch Requests (markets — yfinance batch)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --tickers "000300.SS,000001.SS,399006.SZ,^HSI,^HSCE"

### Fetch Requests (fx — FRED)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series DEXCHUS,TRESEGCNM052N --periods 24
```

### Step 3 — Merge into unified output

Each observation retains `_source`:
- `"nbs_spa"` — NBS direct-API data (primary source, 21 indicators)
- `"akshare"` — PBOC / SHIBOR / chinamoney via akshare (6 indicators)
- `"yfinance"` — Yahoo Finance (5 equity indices)
- `"csv"` — FRED CSV (2 FX-related)

---

## Reference

- `references/indicator-index.md` — Quick lookup (trilingual)
- `references/indicators-inflation.md` — CPI, core CPI, PPI
- `references/indicators-growth.md` — GDP, industrial, retail, FAI
- `references/indicators-trade.md` — Exports, imports, trade balance
- `references/indicators-labor.md` — Urban unemployment
- `references/indicators-sentiment.md` — PMI (mfg / non-mfg / composite)
- `references/indicators-rates.md` — LPR, RRR, SHIBOR
- `references/indicators-money.md` — M1, M2, 社融, new loans
- `references/indicators-realestate.md` — Real estate investment / sales / funding
- `references/indicators-services.md` — Services Production Index
- `references/indicators-markets.md` — CSI300, SSEC, ChiNext, HSI, HSCEI
- `references/indicators-fx.md` — CNY/USD, FX reserves
- `references/sources.md` — Primary sources and provenance

Developer-facing materials (NBS API reverse-engineering, full indicator
UUID catalog, 3-language research synthesis) live under `docs/` — not
loaded at skill runtime. See `docs/README.md`.

---

## Limitations

### Data freshness by source

| Source | Freshness |
|--------|-----------|
| `nbs_client` CPI / PPI / PMI × 3 | **~45-50d** (NBS publishes monthly around 9th-15th) |
| `nbs_client` FAI / Trade / M1 / M2 / urban-unemp / real estate | ~75d (mid-month release for prior month) |
| `nbs_client` industrial / retail / services-production | **~135d in Jan-Feb** (NBS combines Jan-Feb into one 累计 release due to Spring Festival; single-month YoY values appear only from March onwards) |
| `nbs_client` GDP | ~100d (quarterly; released ~Day 20 of first month after quarter end) |
| `akshare_client` LPR / SHIBOR | same-day to 1 business day |
| `akshare_client` RRR | event-driven (latest = last change date) |
| `akshare_client` 社融 / new-loans | ~1-2 month lag |
| FRED DEXCHUS | 1-2 business days |
| FRED TRESEGCNM052N | ~30-60d (SAFE release cadence) |
| yfinance indices | ~real-time (15 min delay) |

### NBS time-window "fences"

NBS publishes CPI, PPI, and some other indicators on a 5-year
base-period revision schedule (e.g. CPI has separate cids for 2026-
and 2021-2025 and 2016-2020 and -2015). `nbs_client.py` pins the
current (2026-) series only; for full historical back-fills, the
client would need to stitch multiple cids. Use case: current-regime
reads are fine; multi-decade back-tests need extension. See
`docs/nbs-indicator-catalog.md` §1a for the syntax.

### Deliberately excluded indicators

**Caixin Manufacturing PMI** and **Caixin Services PMI** were removed
2026-04-18. Only free source (investing.com calendar via akshare) ran
8 months stale; no reliable fresh substitute exists. NBS official
Mfg + Non-Mfg + Composite PMI cover the primary sentiment axis.

**70-city housing price index** — not exposed by NBS's
`queryIndexTreeAsync` API (only published as standalone monthly PDF
via stats.gov.cn/sj/zxfb). Deferred; would require a separate PDF
parser.

**社融存量 同比增长** (TSF stock YoY growth) — canonical credit-
impulse input. Available only in PBOC press release text. akshare's
`shrzgm` gives flow (增量), not stock. Documented in
`docs/china-macro-research-frameworks.md` §3a.

**Li Keqiang Index** — all 3 components (electricity / rail freight /
new loans) are now available individually. Composite preset
deferred. Documented in `docs/china-macro-research-frameworks.md`
§1d.

### FX reserves via FRED

`TRESEGCNM052N` is FX reserves **ex-gold**, IMF/SAFE pipeline. Units
are millions USD (FRED) vs. 亿美元 in Chinese news — divide FRED
by 100 for direct comparison.

### CNY/USD via FRED

`DEXCHUS` is CNY per USD daily from Federal Reserve Board. Onshore
CNY only; CNH (offshore) divergence is a stress indicator not covered.

---

## Cross-Plugin Handoff

```
china-macro (this skill) -> macro-regime-snapshot -> domain-teams:investing-team
```
