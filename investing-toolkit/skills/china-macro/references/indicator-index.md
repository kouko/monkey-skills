# China Macro Indicator Index / 中国宏观指标索引 / 中國總經指標索引

36 indicators across 4 sources. NBS = primary source via reverse-engineered
new-SPA API (2026-04 migration). Caixin PMI added 2026-04-19 via
akshare's `index_pmi_*_cx` endpoint (v1.11.0).

| Preset / Ticker | 中文 | English | Source | Reference file |
|---|---|---|---|---|
| `cpi-yoy` | 居民消费价格指数 同比 | CPI YoY | NBS → `nbs_client` | `indicators-inflation.md` |
| `core-cpi` | 不包括食品和能源 CPI | Core CPI | NBS → `nbs_client` | `indicators-inflation.md` |
| `ppi-yoy` | 工业生产者出厂价格指数 | PPI YoY | NBS → `nbs_client` | `indicators-inflation.md` |
| `gdp-yoy` | 国内生产总值指数 同比 | GDP YoY (quarterly) | NBS → `nbs_client` | `indicators-growth.md` |
| `industrial-yoy` | 规上工业增加值 同比 | Industrial Production YoY (**monthly GDP proxy component**) | NBS → `nbs_client` | `indicators-growth.md` |
| `retail-yoy` | 社会消费品零售总额 同比 | Retail Sales YoY (**monthly GDP proxy component**) | NBS → `nbs_client` | `indicators-growth.md` |
| `fai-yoy` | 固定资产投资 累计同比 | FAI YoY cumulative (**monthly GDP proxy component**) | NBS → `nbs_client` | `indicators-growth.md` |
| `exports-yoy` | 出口总值 同比 | Exports YoY USD | NBS → `nbs_client` | `indicators-trade.md` |
| `imports-yoy` | 进口总值 同比 | Imports YoY USD | NBS → `nbs_client` | `indicators-trade.md` |
| `trade-balance` | 进出口差额 当期值 | Trade Balance USD | NBS → `nbs_client` | `indicators-trade.md` |
| `urban-unemployment` | 全国城镇调查失业率 | Urban Surveyed Unemployment | NBS → `nbs_client` | `indicators-labor.md` |
| `pmi-manufacturing` | 官方制造业PMI | Manufacturing PMI (NBS official) | NBS → `nbs_client` | `indicators-pmi.md` |
| `pmi-non-manufacturing` | 官方非制造业PMI | Non-Manufacturing PMI (NBS official) | NBS → `nbs_client` | `indicators-pmi.md` |
| `pmi-composite` | 综合PMI产出指数 | Composite PMI Output (NBS official) | NBS → `nbs_client` | `indicators-pmi.md` |
| `caixin-mfg-pmi` | 财新制造业PMI | Caixin Manufacturing PMI (S&P Global) | Caixin → `akshare_client` | `indicators-pmi.md` |
| `caixin-svc-pmi` | 财新服务业PMI | Caixin Services PMI (S&P Global) | Caixin → `akshare_client` | `indicators-pmi.md` |
| `m2-yoy` | 广义货币 M2 同比增长 | M2 YoY | NBS → `nbs_client` | `indicators-money.md` |
| `m1-yoy` | 狭义货币 M1 同比增长 | M1 YoY | NBS → `nbs_client` | `indicators-money.md` |
| `lpr-1y` | 贷款市场报价利率 1年期 | Loan Prime Rate 1Y | PBOC → `akshare_client` | `indicators-rates.md` |
| `lpr-5y` | 贷款市场报价利率 5年期 | Loan Prime Rate 5Y | PBOC → `akshare_client` | `indicators-rates.md` |
| `rrr-major` | 大型金融机构 存款准备金率 | RRR Major Banks | PBOC → `akshare_client` | `indicators-rates.md` |
| `shibor-3m` | 上海银行间同业拆放利率 3M | SHIBOR 3-Month | SHIBOR → `akshare_client` | `indicators-rates.md` |
| `shrzgm` | 社会融资规模增量 | Aggregate Financing (flow) | PBOC → `akshare_client` | `indicators-money.md` |
| `new-loans` | 人民币贷款增量 当月 | New RMB Loans | PBOC → `akshare_client` | `indicators-money.md` |
| `realestate-investment-yoy` | 房地产开发投资 累计同比 | Real Estate Investment YoY | NBS → `nbs_client` | `indicators-realestate.md` |
| `housing-sales-area-yoy` | 商品住宅销售面积 累计同比 | Residential Sales Floor Area YoY | NBS → `nbs_client` | `indicators-realestate.md` |
| `housing-sales-value-yoy` | 商品住宅销售额 累计同比 | Residential Sales Value YoY | NBS → `nbs_client` | `indicators-realestate.md` |
| `realestate-funding-yoy` | 房地产投资本年资金来源 累计同比 | Real Estate Funding YoY | NBS → `nbs_client` | `indicators-realestate.md` |
| `services-production-yoy` | 服务业生产指数 当月同比 | Services Production Index YoY (**monthly GDP proxy companion**) | NBS → `nbs_client` | `indicators-services.md` |
| `000300.SS` | 沪深300 | CSI 300 | yfinance | `indicators-markets.md` |
| `000001.SS` | 上证综指 | Shanghai Composite | yfinance | `indicators-markets.md` |
| `399006.SZ` | 创业板指 | ChiNext Index | yfinance | `indicators-markets.md` |
| `^HSI` | 恒生指数 | Hang Seng Index | yfinance | `indicators-markets.md` |
| `^HSCE` | 恒生国企指数 | Hang Seng China Enterprises | yfinance | `indicators-markets.md` |
| `DEXCHUS` | 人民币兑美元汇率 | CNY/USD Exchange Rate | FRED | `indicators-fx.md` |
| `TRESEGCNM052N` | 国家外汇储备 ex-gold | FX Reserves ex-gold | FRED (IMF/SAFE) | `indicators-fx.md` |

## Source distribution

- **NBS (`nbs_client.py`)**: 21 indicators — all NBS-published monthly +
  quarterly data, primary source
- **PBOC + SHIBOR + Caixin (`akshare_client.py`)**: 8 indicators — PBOC-
  only data not redistributed by NBS (6) + Caixin / S&P Global PMI (2)
- **FRED (`fred_client.py`)**: 2 indicators — CNY/USD + FX reserves
- **yfinance (`yfinance_client.py`)**: 5 equity indices

## Migration note (2026-04-18)

13 presets (CPI/PPI/GDP/industrial/retail/exports/imports/trade-balance/
urban-unemployment/PMI-mfg/PMI-non-mfg/M2/M1) migrated from akshare
mirrors to NBS direct. 8 new presets added (core-cpi, fai-yoy,
pmi-composite, 4 real estate, services-production). 2 Caixin PMI
presets dropped (stale investing.com mirror).

Net freshness improvement for trade indicators: **~178 days**
(254d → 76d). See `docs/china-macro-research-frameworks.md` for the
industry-framework synthesis that drove preset selection and
`docs/nbs-indicator-catalog.md` for the full NBS UUID catalog.

## v1.11.0 addition (2026-04-19)

2 Caixin PMI presets restored via a distinct akshare endpoint
(`index_pmi_man_cx` / `index_pmi_ser_cx`, eastmoney-backed — **not**
the stale 2026-04-18-excluded `macro_china_cx_*_pmi_yearly`
investing.com route). Fresh data confirmed through 2026-Q1 at
implementation time. Closes the v1.10.0 Block 1 CN PMI "N/A URL only"
gap for Caixin coverage. See `references/indicators-pmi.md`
§ Caixin vs NBS methodology delta.
