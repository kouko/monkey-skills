---
name: china-macro
description: >-
  Fetch China macroeconomic indicators via akshare (NBS + PBOC + SHIBOR)
  with FRED fallbacks for CNY/USD and FX reserves, plus yfinance for
  CSI300/SSEC/ChiNext/HSI/HSCEI indices. Data layer only — no analysis.
  Returns structured JSON with latest values and direction for inflation,
  growth, trade, labor, sentiment, rates, money, credit, markets, and FX.
  中国宏观经济指标取数 (NBS + PBOC via akshare)。
  中國宏觀經濟指標擷取（國家統計局 + 人民銀行，經 akshare）。
---

# China Macro

Fetches China macroeconomic indicators via akshare (aggregates from NBS,
PBOC, SHIBOR, and chinamoney mirrors), plus FRED for FX reserves and
CNY/USD, and yfinance for market indices. No API key required.

- **akshare** (`akshare_client.py`) — 19 presets across inflation, growth,
  trade, labor, sentiment, rates, money & credit groups
- **FRED** (`fred_client.py`) — CNY/USD (`DEXCHUS`) and FX reserves
  (`TRESEGCNM052N`) — delegated because akshare's SAFE mirror is unreliable
- **yfinance** (`yfinance_client.py`) — CSI 300, Shanghai Composite, ChiNext,
  Hang Seng, Hang Seng China Enterprises

**Why not NBS directly?** NBS `data.stats.gov.cn` WAF (UrlACL) returns 403
for non-mainland IPs. akshare aggregates equivalent data from mirrors
(eastmoney for NBS pass-through, investing.com, chinamoney, shibor.org)
which remain reachable.

This skill is **data-only**. Output is designed for handoff to
`macro-regime-snapshot` or `domain-teams:investing-team`.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `--indicators` | no | `all` | Comma-separated: `inflation`, `growth`, `trade`, `labor`, `sentiment`, `rates`, `money`, `credit`, `markets`, `fx`, or `all` |

---

## Indicator Groups

### inflation

| Preset | Function | Name | Frequency |
|--------|----------|------|-----------|
| cpi-yoy | macro_china_cpi | CPI YoY / 消费者物价指数 同比 | Monthly |
| ppi-yoy | macro_china_ppi | PPI YoY / 生产者物价指数 同比 | Monthly |

### growth

| Preset | Function | Name | Frequency |
|--------|----------|------|-----------|
| gdp-yoy | macro_china_gdp | GDP YoY / 国内生产总值 同比 | Quarterly |
| industrial-yoy | macro_china_industrial_production_yoy | Industrial Production YoY / 规模以上工业增加值 同比 | Monthly |
| retail-yoy | macro_china_consumer_goods_retail | Retail Sales YoY / 社会消费品零售总额 同比 | Monthly |

### trade

| Preset | Function | Name | Frequency |
|--------|----------|------|-----------|
| exports-yoy | macro_china_exports_yoy | Exports YoY USD / 以美元计算出口 同比 | Monthly |
| imports-yoy | macro_china_imports_yoy | Imports YoY USD / 以美元计算进口 同比 | Monthly |
| trade-balance | macro_china_trade_balance | Trade Balance USD / 贸易帐 | Monthly |

### labor

| Preset | Function | Name | Frequency |
|--------|----------|------|-----------|
| urban-unemployment | macro_china_urban_unemployment | Urban Surveyed Unemployment / 全国城镇调查失业率 | Monthly |

### sentiment

| Preset | Function | Name | Frequency |
|--------|----------|------|-----------|
| pmi-manufacturing | macro_china_pmi | Manufacturing PMI (official) / 官方制造业PMI | Monthly |
| pmi-non-manufacturing | macro_china_pmi | Non-Manufacturing PMI (official) / 官方非制造业PMI | Monthly |

### rates

| Preset | Function | Name | Frequency |
|--------|----------|------|-----------|
| lpr-1y | macro_china_lpr | Loan Prime Rate 1Y / 贷款市场报价利率 1年期 | Monthly |
| lpr-5y | macro_china_lpr | Loan Prime Rate 5Y / 贷款市场报价利率 5年期 | Monthly |
| rrr-major | macro_china_reserve_requirement_ratio | RRR Major Banks / 大型金融机构存款准备金率 | Event |
| shibor-3m | macro_china_shibor_all | SHIBOR 3-Month / 上海银行间同业拆放利率 3M | Daily |

### money

| Preset | Function | Name | Frequency |
|--------|----------|------|-----------|
| m2-yoy | macro_china_money_supply | M2 YoY / 广义货币 同比增长 | Monthly |
| m1-yoy | macro_china_money_supply | M1 YoY / 狭义货币 同比增长 | Monthly |

### credit

| Preset | Function | Name | Frequency |
|--------|----------|------|-----------|
| shrzgm | macro_china_shrzgm | Aggregate Financing / 社会融资规模增量 | Monthly |
| new-loans | macro_china_new_financial_credit | New RMB Loans / 人民币贷款增量 | Monthly |

### markets (via yfinance)

| Ticker | Name | Frequency |
|--------|------|-----------|
| `000300.SS` | CSI 300 / 沪深300 | Daily |
| `000001.SS` | Shanghai Composite / 上证综指 | Daily |
| `399006.SZ` | ChiNext / 创业板指 | Daily |
| `^HSI` | Hang Seng / 恒生指数 | Daily |
| `^HSCE` | Hang Seng China Enterprises / 国企指数 | Daily |

### fx (via FRED)

| Series | Name | Frequency |
|--------|------|-----------|
| `DEXCHUS` | CNY/USD Exchange Rate / 人民币汇率中间价 | Daily |
| `TRESEGCNM052N` | FX Reserves ex-gold / 国家外汇储备 | Monthly |

---

## How It Works

### Step 1 — Resolve indicator list

| Input | Presets / tickers |
|-------|-------------------|
| `inflation` | cpi-yoy, ppi-yoy |
| `growth` | gdp-yoy, industrial-yoy, retail-yoy |
| `trade` | exports-yoy, imports-yoy, trade-balance |
| `labor` | urban-unemployment |
| `sentiment` | pmi-manufacturing, pmi-non-manufacturing |
| `rates` | lpr-1y, lpr-5y, rrr-major, shibor-3m |
| `money` | m2-yoy, m1-yoy |
| `credit` | shrzgm, new-loans |
| `markets` | 000300.SS, 000001.SS, 399006.SZ, ^HSI, ^HSCE |
| `fx` | DEXCHUS, TRESEGCNM052N |

### Step 2 — Launch data-fetcher agents

```
### Fetch Requests (inflation + growth + trade)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/akshare_client.py --preset cpi-yoy,ppi-yoy,gdp-yoy,industrial-yoy,retail-yoy,exports-yoy,imports-yoy,trade-balance

### Fetch Requests (labor + sentiment)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/akshare_client.py --preset urban-unemployment,pmi-manufacturing,pmi-non-manufacturing

### Fetch Requests (rates + money + credit)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/akshare_client.py --preset lpr-1y,lpr-5y,rrr-major,shibor-3m,m2-yoy,m1-yoy,shrzgm,new-loans

### Fetch Requests (markets — yfinance batch)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --tickers "000300.SS,000001.SS,399006.SZ,^HSI,^HSCE"

### Fetch Requests (fx — FRED)
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series DEXCHUS,TRESEGCNM052N --periods 24
```

### Step 3 — Merge into unified output

Each observation retains `_source`:
- `"akshare"` — NBS/PBOC/SHIBOR data
- `"yfinance"` — market indices
- `"fred"` — CNY/USD and FX reserves

---

## Reference

- `references/indicator-index.md` — Quick lookup (trilingual)
- `references/indicators-inflation.md` — CPI, PPI
- `references/indicators-growth.md` — GDP, industrial, retail
- `references/indicators-trade.md` — Exports, imports, trade balance
- `references/indicators-labor.md` — Urban unemployment
- `references/indicators-sentiment.md` — PMI (official manufacturing + non-manufacturing)
- `references/indicators-rates.md` — LPR, RRR, SHIBOR
- `references/indicators-money.md` — M0/M1/M2, 社融, new loans
- `references/indicators-markets.md` — CSI300, SSEC, ChiNext, HSI, HSCEI
- `references/indicators-fx.md` — CNY/USD, FX reserves
- `references/sources.md` — Primary sources and akshare provenance

Developer-facing materials (API reverse-engineering notes, NBS tree catalogs
for future `nbs_client.py` work) live under `docs/` — not loaded by this
skill at runtime. See `docs/README.md`.

---

## Limitations

### Data freshness varies by mirror

| Source | Freshness |
|--------|-----------|
| `macro_china_cpi` / `_ppi` / `_gdp` (eastmoney mirror) | ~1 month lag |
| `macro_china_pmi` / `_consumer_goods_retail` (eastmoney mirror) | ~1 month lag |
| `macro_china_urban_unemployment` (eastmoney mirror) | ~1-2 month lag |
| `macro_china_money_supply` / `_new_financial_credit` (PBOC) | ~1 month lag |
| `macro_china_shrzgm` (PBOC) | ~1-2 month lag |
| `macro_china_lpr` / `_shibor_all` | same-day to 1 business day |
| `macro_china_industrial_production_yoy` / `_exports_yoy` / `_imports_yoy` / `_trade_balance` (investing.com mirror) | **stale — up to 8 months behind**. Use only as backup; prefer NBS English site when accessible. |
| `macro_china_reserve_requirement_ratio` | event-driven (last RRR change date) |

### Deliberately excluded indicators

- **Caixin Manufacturing PMI** and **Caixin Services PMI** were removed
  2026-04-18. The only free akshare path (`macro_china_cx_pmi_yearly` /
  `_cx_services_pmi_yearly`) draws from investing.com's calendar and has
  been running ~8 months stale since mid-2025. A stale PMI defeats the
  purpose (PMI value is timeliness), and surfacing it risks Claude
  treating 2025-09 numbers as current-regime signals. Official NBS
  manufacturing + non-manufacturing PMI remain in the skill at ~47d
  freshness and cover the primary sentiment axis. If a fresh Caixin
  read is needed, see S&P Global's Caixin release page or the Caixin
  Global news feed — a dedicated `caixin_client.py` can be added later
  if that demand materialises.

### NBS WAF blocks foreign IPs

Direct access to `data.stats.gov.cn/english/easyquery.htm` returns HTTP 403
(`reason:UrlACL`) for most non-mainland IPs. This skill uses akshare which
scrapes eastmoney and other reachable mirrors. If NBS relaxes the WAF in the
future, a direct NBS client (nbsc-pattern) would give fresher data for
industrial / trade indicators.

### akshare dependency

`akshare_client.py` uses `akshare==1.18.55`. akshare has 10k+ GitHub stars
and is actively maintained (akfamily/akshare), but it aggregates data by
reverse-engineering public websites — individual endpoints can break when
upstream pages change. `macro_china_foreign_exchange_gold` is currently
broken upstream; the skill routes FX reserves to FRED instead.

### FX reserves via FRED

`TRESEGCNM052N` is FX reserves **ex-gold**, sourced from the IMF/SAFE
pipeline. Units are millions USD (FRED) vs. 亿美元 at SAFE — divide by 100
to compare with Chinese news. For gold reserves separately, there is no
stable no-auth source — note in analysis if relevant.

### CNY/USD via FRED

`DEXCHUS` is CNY per USD daily (Chinese yuan renminbi to one US dollar).
Sourced from Federal Reserve Board. 1-2 business day lag.

---

## Cross-Plugin Handoff

```
china-macro (this skill) -> macro-regime-snapshot -> domain-teams:investing-team
```
