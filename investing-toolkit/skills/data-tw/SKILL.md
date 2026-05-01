---
name: data-tw
description: >-
  Layer 1 (Data) skill for Taiwan equities + macro. Bundles 8 clients
  (yfinance, MOPS, TWSE/TPEx OpenAPI, FinMind, CBC, DGBAS, NDC, stat.gov.tw)
  behind a `pack.py` facade with 5 pack types — snapshot, memo-fetch,
  comps-multiples, screener-batch, regime-pack. MOPS + TWSE OpenAPI are Tier A
  primary; FinMind is Tier 2 fallback / by-design gap supplier
  (per-stock T86 三大法人 daily flow, .TWO price history). Pure I/O — no
  analysis. Single-ticker (`--ticker`) and batch (`--tickers`) modes.
  台股資料層（公開觀測站＋證交所 OpenAPI＋總經，Tier A 為主，FinMind 補位）。
  台湾データ層（MOPS／TWSE／マクロ統合、Tier A 中心）。
---

# data-tw

**Layer 1 — Data** in the investing-toolkit three-layer architecture
(Data → Analysis → Report). This skill is **pure I/O**: it fetches Taiwan
equity disclosures, trade data, and macro indicators, and emits a structured
JSON envelope. It does not analyze, score, or compose any report.

Output is consumed by Layer 2 (`analysis-*`) and Layer 3 (`report-*`) skills,
typically via main-agent orchestration:

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker 2330.TW --pack memo-fetch \
     > /tmp/2330-data.json
# main agent then chains analysis-* / report-* against /tmp/2330-data.json
```

---

## Bundled clients (8)

| Client | Tier | Coverage |
|---|---|---|
| `mops_client.py` | **A primary** | 公司基本資料、財報 BS/IS/CF、月營收、董監持股、內部人申報、股利、除權息、重大訊息 (16 actions) |
| `twse_openapi_client.py` | **A primary** | TWSE/TPEx OpenAPI: 日行情 snapshot、PE/PB/殖利率、融資融券、三大法人 snapshot、產業 EPS、除權息日曆、`/rwd/` 歷史 OHLCV (sii only) |
| `finmind_client.py` | **2 by-design gap** | 提供 Tier A 缺的資料：日 per-stock T86 三大法人、`.TWO` OHLCV、split-adjusted 價格、融資融券時序。**非** Tier A 失敗自動 fallback — Tier A 出錯時 pack 會回 `_partial: true` + 各 source `_error`，由 consumer (analysis / report layer) 決定是否升級 |
| `yfinance_client.py` | **2 cross-source** | 價格 / info / multiples / batch 取得（`.TW` / `.TWO` 自動分發） |
| `cbc_client.py` | **A primary** | 央行：重貼現率、TWD/USD、M2、準備貨幣 |
| `dgbas_client.py` | **A primary** | 主計總處 Excel：CPI / 核心 CPI / PPI / 進出口物價 |
| `ndc_client.py` | **A primary** | 國發會：景氣對策信號 五色燈號＋構成項目、領先/同時指標、台灣 PMI/NMI（CIER via data.gov.tw 6100） |
| `statgov_client.py` | **A primary** | stat.gov.tw 隱藏 chart data：GDP、IPI、失業率、出口、外匯、TAIEX 等 17 個 preset |

All 8 client scripts are **MD5-identical copies** of the canonical files at
`investing-toolkit/scripts/`. CI enforces sync (see `sync-check.sh`).

---

## Tier policy (TW-specific)

```
Tier A primary  : MOPS + TWSE/TPEx OpenAPI + CBC + DGBAS + NDC + stat.gov.tw
Tier 2 by-gap   : FinMind  (.TWO price / T86 daily flow / 融資融券時序 — Tier A 缺項由 FinMind 補)
Tier 2 cross-src: yfinance (price snapshot, multiples, batch convenience)
```

**No automatic Tier A → 2 fallback**. When a Tier A source errors, pack.py records
the error in the wrapped output's `_error` field and flips top-level `_partial: true`.
Downstream analysis / report skills inspect `_tier` + `_partial` + `_error` to decide
whether to escalate (e.g. retry, request a different action, or surface the gap to user).

Provenance labels are embedded in every wrapped output:

```jsonc
{
  "_tier": "A" | "2" | "2-gap",
  "_source": "mops" | "twse_openapi" | "finmind" | "yfinance" | "cbc" | "dgbas" | "ndc" | "statgov",
  "_action": "<client action>",
  "data": { ... } // or "_error": "...", "_stderr": "..."
}
```

`_tier: "2-gap"` marks the **known Tier A gap** cases (T86 daily 三大法人, `.TWO` history)
where FinMind is the **by-design** source — not a fallback.

---

## Ticker conventions

| Suffix | Market | Routing |
|---|---|---|
| `2330.TW` | TWSE listed (sii) | MOPS + TWSE OpenAPI primary; yfinance `.TW` |
| `2330.TWO` | TPEx listed (otc) | MOPS + TWSE OpenAPI primary; **price history via FinMind** (TPEx has no `/rwd/`); yfinance `.TWO` |
| `2330` (bare) | assumed sii | normalized to `2330.TW` internally |

`pack.py` performs normalization automatically; downstream callers may pass
any of the three forms.

---

## Pack types

`pack.py` exposes 5 pack types matching the v2.0.0 contract (spec §4.2):

| Pack | Mode | Use case | Heaviness |
|---|---|---|---|
| `snapshot` | `--ticker` | Quick overview card (price + valuation + latest financials + T86 3mo) | light |
| `memo-fetch` | `--ticker` | Full equity-memo data (snapshot + 12m 月營收 + 5y 股利 + 重訊 + 融資融券時序 + 歷史 OHLCV) | heavy |
| `comps-multiples` | `--ticker` or `--tickers` | yfinance multiples-only (anchor + peers); for `analysis-comps` | light |
| `screener-batch` | `--tickers` (required) | yfinance batch info+history + minimal MOPS company_basic per ticker | medium |
| `regime-pack` | (no ticker) | Macro indicators only — CBC + DGBAS + NDC 五色燈號 + 統計總處 + CIER PMI | medium |

### Pack composition

| Pack | yfinance | mops | twse_openapi | finmind | cbc | dgbas | ndc | statgov |
|---|---|---|---|---|---|---|---|---|
| `snapshot` | info, history(period) | company_basic, balance_sheet, income_statement | daily_price, pe_pb_yield, margin_balance | T86 3mo | – | – | – | – |
| `memo-fetch` | info, history(2y) | + cash_flow, monthly_revenue, dividends 5y, director_holdings, insider_trades, announcements | + three_investor, stock_day_history (sii only) | T86 3mo, margin_history 3mo, price_history (.TWO only) | – | – | – | – |
| `comps-multiples` | info (multiples extracted) | – | – | – | – | – | – | – |
| `screener-batch` | info batch, history batch | company_basic per ticker | – | – | – | – | – | – |
| `regime-pack` | – | – | – | – | rediscount-rate, twdusd, m2, reserve-money | cpi, core-cpi, ppi, import-pi, export-pi | signal, signal-components, pmi-mfg, pmi-nmi | growth, trade, labor, leading/coincident CI, fx-reserves, taiex, m2-yoy |

### CLI

```bash
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker 2330.TW --pack snapshot
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker 2330.TW --pack memo-fetch
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --tickers 2330.TW,2454.TW --pack comps-multiples
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --tickers 2330.TW,2454.TW,2308.TW --pack screener-batch
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --pack regime-pack
```

Common args:

| Arg | Required | Notes |
|---|---|---|
| `--ticker` | for snapshot / memo-fetch (also accepted by comps-multiples for n=1) | One of `2330`, `2330.TW`, `2330.TWO` |
| `--tickers` | for screener-batch (required) and comps-multiples (batch) | Comma-separated; mixed `.TW` + `.TWO` allowed |
| `--pack` | yes | One of `snapshot`, `memo-fetch`, `comps-multiples`, `screener-batch`, `regime-pack` |
| `--period` | optional | `1y` (default snapshot), `2y` (default memo-fetch); accepts any yfinance period string |

---

## Output envelope

```jsonc
{
  "_pack": "memo-fetch",
  "_ticker": "2330.TW",
  "_normalized": {"ticker_yf": "2330.TW", "ticker_code": "2330", "market": "sii"},
  "_partial": false,           // true if any Tier A fetch errored
  "yfinance": {
    "info":    {"_tier": "2", "_source": "yfinance", "_action": "info",    "data": {...}},
    "history": {"_tier": "2", "_source": "yfinance", "_action": "history", "data": {...}}
  },
  "mops": {
    "company_basic":     {"_tier": "A", ...},
    "balance_sheet":     {"_tier": "A", ...},
    "income_statement":  {"_tier": "A", ...},
    "cash_flow":         {"_tier": "A", ...},
    "monthly_revenue":   {"_tier": "A", ...},
    "dividends":         {"_tier": "A", ...},
    "director_holdings": {"_tier": "A", ...},
    "insider_trades":    {"_tier": "A", ...},
    "announcements":     {"_tier": "A", ...}
  },
  "twse": {
    "daily_price":       {"_tier": "A", ...},
    "pe_pb_yield":       {"_tier": "A", ...},
    "margin_balance":    {"_tier": "A", ...},
    "three_investor":    {"_tier": "A", ...},
    "stock_day_history": {"_tier": "A", ...}    // sii only
  },
  "finmind": {
    "three_investor_flow": {"_tier": "2-gap", "_source": "finmind", ...},
    "margin_history":      {"_tier": "2-gap", ...},
    "price_history":       {"_tier": "2", ...}  // only when ticker is .TWO
  }
}
```

---

## Calendar conversion (built-in)

`pack.py` converts Gregorian → ROC year automatically. Callers do **not**
need to compute `roc_year` / `season` / `month` themselves.

- ROC year = Gregorian year − 1911
- Latest filed quarter: 4-month conservative shift (Q4 filed by Mar 31; Q1 by May 15; etc.)
- Latest 月營收 month: 月10日 publication rule + 5-day buffer

---

## How this differs from v1.x skills

| v1.x | v2.0.0 |
|---|---|
| `taiwan-macro/SKILL.md` (macro fetch + reference docs) | merged into `data-tw/SKILL.md` `regime-pack` |
| `taiwan-stock-snapshot/SKILL.md` (fetch + compose card) | **fetch part** → `data-tw/{snapshot,memo-fetch}`; **card composition** → `report-stock-snapshot` (Layer 3) |
| 8 individual client invocations from SKILL.md prose | 1 `pack.py` facade with 5 modes |
| ROC date arithmetic embedded in SKILL.md prose | handled inside `pack.py` |

The two v1 skills (`taiwan-macro/`, `taiwan-stock-snapshot/`) remain in-place
during the v2.0.0-rc.1 rollout window and are removed once `report-*` skills
are wired to `data-tw`.

---

## Cache

Honors `$INVESTING_TOOLKIT_CACHE` env var. Per-source TTLs are managed inside
each underlying client (`mops_client.py`, `twse_openapi_client.py`, etc.) — no
caching layer added at the `pack.py` level.

---

## Cross-skill / cross-plugin handoff

`data-tw` does **not** call other skills (Layer 1 invariant). Downstream:

```
data-tw  →  analysis-{dcf,comps,technical,screener,macro-regime}  →  report-{equity-memo,stock-snapshot,screener-list,portfolio-review}
                                                                  ↘  domain-teams:investing-team (gates, verdicts)
```

Cross-country batches (e.g. `AAPL,2330.TW,7203.T`) are split by report-layer
skills into per-country `data-{country}/pack.py --tickers ... --pack screener-batch`
calls and concatenated.

---

## Reference

- Spec: `docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md` §4.2
- v1 macro detail: `investing-toolkit/skills/taiwan-macro/references/`
- v1 stock detail: `investing-toolkit/skills/taiwan-stock-snapshot/references/`
- Canonical clients: `investing-toolkit/scripts/`

---

## Limitations

- **stat.gov.tw fragility** — extracts from HTML hidden field
  `#ContentPlaceHolder1_hidChartData`; not a documented API. Page redesign
  could break it.
- **SSL** — All TW gov sites have certificate issues; clients use `verify=False`.
- **Publication lags** — see v1 `taiwan-macro/SKILL.md` table; CI typically
  4–6 weeks behind for 景氣燈號.
- **`.TWO` price history** — TPEx has no `/rwd/` endpoint; `pack.py` falls
  through to FinMind `TaiwanStockPrice` (Tier 2).
- **MOPS 重大訊息** — `realtime-announcements` returns market-wide; per-ticker
  filter is best-effort via `--market sii|otc`.

---

_Layer 1 (Data) skill • investing-toolkit v2.0.0 • 台股資料層 • 台湾データ層_
