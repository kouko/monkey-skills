# China macro — research frameworks + indicator-sourcing gaps

Reference note for how the financial industry analyses Chinese
macroeconomic data, what `china-macro` covers today, and which
indicators remain unsolved after the 2026-04-18 scoping exercise.

Captured from a 3-language literature synthesis (简体中文, 日本語,
English — see sources at the bottom).

---

## 1. Three parallel frameworks

All three converge on the same baseline indicator set. They differ
in how they frame what matters and which composite they cite first.

### 1a. 三驾马车 (CN / JP)

The foundational GDP-side framework: **消费 + 投资 + 净出口 = GDP**
by expenditure. NBS publishes quarterly contribution rates for each
leg. The Chinese reform narrative has migrated toward "新三驾马车":
consumption upgrade + technology investment + green exports.

Japanese analysts (大和総研, 日本総研) inherited this verbatim as
三駕馬車 (投資・消費・純輸出), especially when explaining growth
quality shifts.

**Mapping to our skill**:
- 消费: `retail-yoy` (社会消费品零售总额)
- 投资: `fai-yoy` (固定资产投资, coming in nbs_client.py)
- 净出口: `exports-yoy` – `imports-yoy` (计算 derived)

### 1b. 三大数据 (CN)

On or around the 15th of each month, NBS releases 工业增加值 + 社会
消费品零售总额 + 固定资产投资 **simultaneously**. These three move
CSI 300 together and every Chinese macro headline calls them the
"三大数据" package.

Missing this release in a market-close recap is the signature of a
non-serious analyst.

**Mapping**: the three Tier-A presets `industrial-yoy`, `retail-yoy`,
`fai-yoy` should be treated as one logical release — they will always
have the same reference month.

### 1c. Credit Impulse (EN / JP)

Popularised by Goldman Sachs and Morgan Stanley since ~2018 as the
single most important cyclical indicator for China. Definition:

```
credit_impulse(t) = Δ(TSF_flow(t) / GDP(t)) over 12 months
                  = (TSF_flow(t) / GDP(t)) − (TSF_flow(t-12) / GDP(t-12))
```

Interpretation: positive credit impulse = easing; negative = tightening.
Leads growth by 6-12 months. The related Japanese term 信用インパルス
matches this exactly.

**Mapping to our skill**: can be derived from `shrzgm` (monthly flow)
÷ `gdp` (quarterly) once both are NBS-sourced. **Not implemented as a
preset today.** Deferred until there's demand.

### 1d. Li Keqiang Index (EN / CN)

Popularised by a 2010 Wikileaks cable. The original formula:

```
Li Keqiang Index = 0.40 × YoY(electricity consumption)
                 + 0.40 × YoY(outstanding bank loans)
                 + 0.20 × YoY(rail freight volume)
```

Used as a sanity-check against official GDP, especially during periods
when GDP numbers are suspected of smoothing. The "new" Li Keqiang Index
updates this for China's services-heavy 2020s economy by adding
services-sector proxies.

**Component status in our catalog** (cids from `nbs-tree-monthly.md`):

| Component | NBS source | Available? |
|---|---|---|
| Electricity consumption YoY | 月度 → 能源 → 能源产品产量 (电力) | ✅ leaf exists |
| Rail freight volume YoY | 月度 → 交通运输 (1 of 7 leaves) | ✅ leaf exists |
| Outstanding RMB loans YoY | `macro_china_new_financial_credit` 累计-同比增长 | ✅ via akshare |

**Status**: all three components available. Composite preset
`li-keqiang-index` deliberately **deferred** (not in v1 nbs_client.py)
— the individual components can be fetched today and the composite
arithmetic is trivial. Revisit if users ask for the unified index.

---

## 2. Release calendar watched across languages

| Date in month | Release | Agency | In skill? |
|---|---|---|---|
| ~1st business day | 官方 PMI 制造 + 非制造 | NBS | ✅ |
| ~3rd business day | Caixin 制造业 PMI (~500 SMEs) | Caixin/S&P | ❌ excluded (stale mirror, see SKILL.md) |
| ~5th business day | Caixin 服务业 PMI | Caixin/S&P | ❌ same reason |
| ~9th | CPI + PPI | NBS | ✅ |
| ~10-15th | 进出口 (preliminary) | GAC | ✅ (stale mirror, Tier-1 NBS upgrade incoming) |
| ~15th | **三大数据**: 工业增加值 + 零售 + FAI | NBS | ✅ partial (FAI missing — Tier-1 NBS add) |
| ~15-20th | M2 + 社融 + 新增贷款 | PBOC | ✅ |
| ~20th | LPR | NIFC/PBOC | ✅ |
| ~25th | 规上工业企业利润 | NBS | ❌ Tier C |
| Quarter end +20 | GDP | NBS | ✅ |
| Quarterly | 70城住宅销售价格 (monthly) | NBS | ❌ Tier B NBS upgrade incoming |

---

## 3. Sourcing gaps — known limitations

Indicators the industry watches but `china-macro` cannot serve
cleanly given free / no-auth constraints.

### 3a. 社融存量 同比增长率 (TSF stock YoY)

**Why it matters**: canonical credit-impulse numerator input. The
headline number Chinese media cite every month: "11月末社会融资规模
存量同比增长 8.5%".

**Sources checked**:
- NBS new SPA — only 货币供应量 (M0/M1/M2) under 月度→金融.
- akshare — `macro_china_shrzgm` provides the **flow** (增量), not
  the stock. `macro_china_new_financial_credit` has RMB loans
  cumulative YoY (~5-6% range) but that covers only ~65% of TSF.
- FRED — no clean series. `CRDQCNAPABIS` measures private-sector
  credit from BIS, different definition from PBOC TSF.
- TradingEconomics / MacroMicro — have it, behind paywalls / scraping.
- PBOC press release — fragile HTML scraping; release format changes
  occasionally.

**Decision (2026-04-18)**: skip. Document the gap. The existing
`shrzgm` preset (monthly increment) remains as the closest available
credit-flow proxy. If a stable free source emerges, revisit with a
dedicated `pboc_client.py` — in the same spirit as the existing
Caixin exclusion.

**Workaround for users who need the exact number**:
1. PBOC press release on the 10th-15th of each month lists it
   directly (e.g. "社会融资规模存量同比增长 8.5%").
2. `macro_rmb_loan` from akshare gives RMB-only equivalent (累计
   人民币贷款 同比) — correlated but not identical.

### 3b. 电力消费 / 鐵路货运量 (Li Keqiang components)

Available in NBS under 月度 → 能源 and 月度 → 交通运输. Not
implemented as presets because the use case is the composite Li
Keqiang Index, which itself is deferred.

### 3c. Caixin Mfg / Services PMI

Dropped 2026-04-18. See SKILL.md "Deliberately excluded indicators"
for rationale. No reliable free source for fresh readings.

### 3d. CNH (offshore RMB)

FRED has onshore `DEXCHUS` (CNY/USD). CNH-CNY spread is a stress
indicator during FX pressure but no clean free source. Deferred.

### 3e. China equity single-stock fundamentals

Out of scope — `china-macro` is macro-only. A future
`china-stock-snapshot` skill would cover this.

---

## 4. Industry-analyst dashboard reconstruction

If we were to mimic what a Goldman Sachs / Morgan Stanley / 大和総研
China macro dashboard looks like, our target coverage would be:

| Section | Coverage after nbs_client.py | Gap |
|---|---|---|
| Growth & activity | CPI, PPI, GDP, industrial, retail, FAI, unemployment, PMI × 3, services-production | 工业企业利润 (Tier C) |
| Trade | exports, imports, trade balance | FDI (Tier C) |
| Monetary | M1, M2, LPR × 2, RRR, SHIBOR, new loans, shrzgm-flow | **社融存量同比 (gap 3a)** |
| Real estate | 70城 × 2, 房地产 invest + 4 sales/funding | 分城 drill-down (Tier C) |
| Markets | CSI 300, SSEC, ChiNext, HSI, HSCEI | CGB yields, A-share sector indices (future) |
| FX | DEXCHUS, FX reserves | **CNH offshore (gap 3d)** |
| Composite | (none — Li Keqiang Index deferred) | Li Keqiang Index (gap 3b) |

**Coverage level after Tier A + B migration**: roughly 80% of the
content in a typical China-dedicated analyst monthly. The main
missing pieces are the credit-impulse numerator (社融存量) and
derived composites (Li Keqiang Index).

---

## Sources

### English
- [Li Keqiang Index — Wikipedia](https://en.wikipedia.org/wiki/Li_Keqiang_index)
- [China Credit Impulse — HL Hunt Financial](https://www.hlhunt.org/uncategorized/china-credit-impulse-global-growth-transmission-and-investment-implications-hl-hunt-financial/)
- [China Outlook 2026-27 — UBS](https://www.ubs.com/global/en/investment-bank/insights-and-data/articles/china-outlook.html)
- [The BEAT — Morgan Stanley](https://www.morganstanley.com/im/publication/insights/articles/article_thebeatmay2025.pdf)
- [MERICS Economic Indicators](https://merics.org/en/merics-economic-indicators-0)
- [Measurement Muddle: China's GDP Growth Data and Potential Proxies — Big Data China (CSIS)](https://bigdatachina.csis.org/measurement-muddle-chinas-gdp-growth-data-and-potential-proxies/)

### 日本語
- [中国経済 2026年見通し — 大和総研](https://www.dir.co.jp/report/research/economics/china/20251223_025484.html)
- [中国経済展望 — 日本総研](https://www.jri.co.jp/report/medium/china/)
- [70都市住宅価格指数は過熱気味 — 三井住友DSアセットマネジメント](https://www.smd-am.co.jp/market/daily/keyword/archives/china/key160519ch/)
- [中国経済：2026～27年の見通し — ニッセイ基礎研究所](https://www.nli-research.co.jp/report/detail/id=84768?site=nli)
- [中国、底堅い年初の主要経済指標と今後の注意点 — Pictet](https://www.pictet.co.jp/investment-information/market/today/20260316.html)

### 简体中文
- [「三驾马车」定义 — 国家统计局](https://www.stats.gov.cn/zs/tjws/tjzb/202301/t20230101_1903947.html)
- [「先行 / 同步 / 滞后 指标」— 国家统计局](https://www.stats.gov.cn/zs/tjws/tjzb/202301/t20230101_1940241.html)
- [11月社融存量同比增 8.5% — 新华网](https://www.news.cn/money/20251215/9714d1a58754468595f5dc02367099de/c.html)
- [「三大数据」解读 — 证券之星 (2026-03)](https://stock.stockstar.com/JC2026032000010336.shtml)
- [宏观经济10大分类体系 — 前瞻数据库](https://d.qianzhan.com/xdata/list/xCxlxvHxv.html)
