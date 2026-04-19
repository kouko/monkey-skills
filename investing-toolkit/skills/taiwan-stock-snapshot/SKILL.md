---
name: taiwan-stock-snapshot
description: >-
  TW 個股 snapshot — MOPS JSON API (公司揭露) + TWSE/TPEx OpenAPI (交易)
  Tier A primary; FinMind Tier 2 auto-fallback. Composes a structured snapshot
  card covering company basics, latest BS/IS/CF, 月營收、三大法人 snapshot、
  融資融券、董監持股、股利、重大訊息, and prepares a handoff fixture for
  domain-teams:investing-team Taiwan-Specific Diagnosis.
  台股快照取得。法定揭露・取引データ・機関投資家。
---

# taiwan-stock-snapshot

> **MCP-aware execution (v1.14.0+)**: If `investing-toolkit` MCP tools (`mops_fetch`, `twse_openapi_fetch`, `finmind_fetch`, `yfinance_history`) are registered in your session, prefer them over the `uv run scripts/...` subprocess commands shown below. Identical JSON payloads, faster on repeat calls, bypasses the Claude Desktop Cowork sandbox. Subprocess commands remain the canonical spec and fallback.

Taiwan equity data snapshot from **primary-source Tier A** APIs (MOPS + TWSE/TPEx
OpenAPI), with FinMind as a Tier 2 fallback for coverage gaps and resilience.
Produces a structured card for handoff to `domain-teams:investing-team`
Taiwan-Specific Diagnosis.

This skill is **data-only** — it does not analyze or generate verdicts.

**Requires** (all ship with investing-toolkit v1.13.0):
- `scripts/mops_client.py` — MOPS JSON API (16 actions; 公司揭露)
- `scripts/twse_openapi_client.py` — TWSE + TPEx OpenAPI (交易資料)
- `scripts/finmind_client.py` — FinMind aggregator (Tier 2 fallback)

See `references/data-sources.md` for full endpoint catalog, fallback decision
tree, rate limits, and ROC calendar conventions.

---

## Data Sources (v1.13.0)

| Tier | Source | Script | Coverage |
|------|--------|--------|----------|
| **1 Primary (Tier A)** | MOPS JSON API | `mops_client.py` | 公司基本資料 / 財報 BS-IS-CF / 月營收 / 董監持股 / 內部人 / 股利 / 除權息 / 股東會 / 重大訊息 |
| **1 Primary (Tier A)** | TWSE + TPEx OpenAPI | `twse_openapi_client.py` | 日行情 snapshot / PE-PB-殖利率 / 融資融券 / 三大法人 snapshot / 產業 EPS / 除權息日曆 |
| **2 Fallback** | FinMind | `finmind_client.py` | Auto-triggered on Tier 1 failure; also provides **daily per-stock 三大法人 flow (T86)** which TWSE OpenAPI lacks, plus historical OHLCV time-series |

**Why FinMind stays**: resilience if Tier 1 schema changes, ISQ gate
cross-validation, Taiwan-specific curation, and coverage of known Tier 1 gaps.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | TWSE/OTC code, e.g. `2330`, `2330.TW`, `2454.TWO` (suffix stripped) |
| `period` | no | `1y` | Historical OHLCV lookback: `3mo`, `6mo`, `1y`, `2y` (routes to FinMind) |
| `--source` | no | auto | Pattern B override: `finmind` forces secondary path |
| `--no-fallback` | no | false | Disable auto-fallback; fail loud if Tier 1 fails |
| `--deep` | no | false | Extended fetch (historical financials 20q, ex-dividend 5y, shareholder meetings 3y) |

---

## Default Fetch (on `ticker` = e.g. 2330)

| Field | Source | Action / Dataset | Reference Period |
|-------|--------|------------------|------------------|
| `company_info` | mops | `company-basic` (t05st03) | current |
| `balance_sheet_latest` | mops | `balance-sheet` (t164sb03) | latest quarter |
| `income_statement_latest` | mops | `income-statement` (t164sb04) | latest quarter |
| `cash_flow_latest` | mops | `cash-flow` (t164sb05) | latest quarter |
| `monthly_revenue_12m` | mops | `monthly-revenue` (t05st10_ifrs) | past 12 months |
| `director_holdings` | mops | `director-holdings` (stapap1) | latest month |
| `insider_trades_3m` | mops | `insider-trades` (query6_1) | past 3 months |
| `dividends_5y` | mops | `dividends` (t05st09_2) | past 5 years |
| `realtime_announcements` | mops | `realtime-announcements` | last 10 |
| `daily_price_snapshot` | twse-openapi | `daily-price` (STOCK_DAY_ALL) | latest session |
| `pe_pb_yield` | twse-openapi | `pe-pb-yield` (BWIBBU_ALL) | latest session |
| `margin_balance` | twse-openapi | `margin-balance` (MI_MARGN) | latest session |
| `qfiis_holdings_snapshot` | twse-openapi | `three-investor` (MI_QFIIS_sort_20) | latest session |
| `daily_price_history` | **finmind** | TaiwanStockPrice | past `period` (Tier 1 gap — routed to FinMind by default) |
| `three_investor_flow_30d` | **finmind** | TaiwanStockInstitutionalInvestorsBuySell | past 3 months (Tier 1 gap) |
| `margin_balance_history` | **finmind** | TaiwanStockMarginPurchaseShortSale | past 3 months (time-series) |

### Extended (`--deep`)

| Field | Source | Action |
|-------|--------|--------|
| `financials_20q` | mops | `balance-sheet` / `income-statement` / `cash-flow` × 20 quarters |
| `ex_dividend_history_5y` | mops | `ex-dividend` (t108sb19) |
| `shareholder_meetings_3y` | mops | `shareholder-meetings` (t108sb16_q1) |

---

## How It Works

### Step 1 — Launch data-fetcher agent

Launch `../../agents/data-fetcher.md` (haiku model) with parallel fetches.
Set `{date_start_3mo}` = today minus 3 months and `{date_start_period}` based
on `period` arg, all `YYYY-MM-DD`. Convert `{latest_roc_year}` and
`{latest_roc_season}` from today's Gregorian date (ROC year = Gregorian − 1911).

```
### Task
Fetch Taiwan equity data for {ticker}. Return structured JSON. Do not analyze.

### Scripts
base_path: {absolute path to investing-toolkit/scripts/}

### Fetch Requests

# --- Tier 1 PRIMARY: MOPS (公司揭露) ---
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action company-basic
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action balance-sheet --year {latest_roc_year} --season {latest_roc_season}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action income-statement --year {latest_roc_year} --season {latest_roc_season}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action cash-flow --year {latest_roc_year} --season {latest_roc_season}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action monthly-revenue --year {latest_roc_year} --month {latest_month}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action director-holdings
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action insider-trades
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action dividends --first-year {roc_5y_ago} --last-year {latest_roc_year}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --action realtime-announcements --market sii --count 10

# --- Tier 1 PRIMARY: TWSE OpenAPI (交易) ---
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/twse_openapi_client.py --ticker {ticker_code} --action daily-price
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/twse_openapi_client.py --ticker {ticker_code} --action pe-pb-yield
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/twse_openapi_client.py --ticker {ticker_code} --action margin-balance
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/twse_openapi_client.py --ticker {ticker_code} --action three-investor

# --- Tier 2 by-design (Tier 1 gap) or AUTO-FALLBACK target ---
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockPrice --date-start {date_start_period}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockInstitutionalInvestorsBuySell --date-start {date_start_3mo}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockMarginPurchaseShortSale --date-start {date_start_3mo}

### Output Format
{
  "mops": {
    "company_basic": {...}, "balance_sheet": {...}, "income_statement": {...},
    "cash_flow": {...}, "monthly_revenue": {...}, "director_holdings": {...},
    "insider_trades": {...}, "dividends": {...}, "announcements": {...}
  },
  "twse": {
    "daily_price": {...}, "pe_pb_yield": {...},
    "margin_balance": {...}, "qfiis_holdings": {...}
  },
  "finmind": {
    "price_history": {...}, "three_investor_flow": {...}, "margin_history": {...}
  },
  "_partial": false
}
```

**Graceful degradation**: If an individual Tier 1 fetch fails (HTTP 5xx /
timeout / schema error), the data-fetcher logs a warning and retries via
the FinMind equivalent (see `references/data-sources.md` fallback table).
If both fail, set `_partial: true` and continue with remaining fields.

### Step 2 — Compose snapshot card

Extract the fields below. Use `N/A` for absent values. Prefer Tier 1 primary
when both present; use FinMind fields only where Tier 1 lacks coverage
(price history, daily 三大法人 flow, margin time-series).

| Card field | Preferred source |
|------------|------------------|
| 公司名稱 / 產業 | `mops.company_basic` |
| Close / 52W high-low / vs 52W High % | `finmind.price_history` (computed over `period`) |
| Latest session snapshot | `twse.daily_price` |
| P/E / P/B / 殖利率 | `twse.pe_pb_yield` |
| 外資/投信/自營 net flow (30d) | `finmind.three_investor_flow._processed` |
| 外資持股 snapshot | `twse.qfiis_holdings` |
| 月營收 (MoM / YoY) | `mops.monthly_revenue` |
| BS / IS / CF highlights | `mops.balance_sheet` / `income_statement` / `cash_flow` |
| 董監持股 / 質押 % | `mops.director_holdings` |
| 融資 / 融券 餘額 | `twse.margin_balance` + `finmind.margin_history` |
| 股利 5y | `mops.dividends` |
| 重大訊息 (recent) | `mops.announcements` |

### Step 3 — Render card

```
## {TICKER} {company_name} 台股快照 — {date}

**Price (TWD)**: {close} | 52W: {low}–{high} | vs 52W High: {pct}%
**Valuation**: P/E {pe} | P/B {pb} | 殖利率 {yield}% | 市值 {mcap_b}B TWD

### 最新財報（{roc_year}Q{season}）— MOPS
- 營收：{revenue} 千元 | 毛利率：{gm}% | 營益率：{om}%
- EPS：{eps} | ROE：{roe}% | 淨負債比：{net_debt}%

### 月營收（{revenue_month} 公布）— MOPS
- 本月營收：{revenue} 千元 | MoM {mom}% | YoY {yoy}%
- _公布截止：每月10日（曆日，證交法第36條）_

### 三大法人（{latest_flow_date}，30d cum）— FinMind
| 投資人 | 累計買賣超（千股） | 方向 |
|-------|-----------------|------|
| 外資   | {foreign_net}   | ↑買超 / ↓賣超 |
| 投信   | {trust_net}     | ↑買超 / ↓賣超 |
| 自營   | {dealer_net}    | 多為避險，參考意義較低 |

外資持股 snapshot（TWSE OpenAPI）：{qfiis_pct}%

### 董監持股（{holding_date}）— MOPS
- 持股比例：{holding_pct}% | 質押比例：{pledged_pct}%
{governance_flag}

### 融資融券（{margin_date}）— TWSE OpenAPI
- 融資餘額：{margin_balance}（↑ 散戶加碼多單）
- 融券餘額：{short_balance}（↑ 放空部位增加）

### 股利 5y / 重大訊息 — MOPS
- 最近配息：{latest_dividend} | 5y 平均：{avg_dividend}
- 近期重訊：{recent_announcements_summary}

_資料來源：MOPS JSON API（Tier A primary）+ TWSE/TPEx OpenAPI（Tier A primary）
+ FinMind（Tier 2 fallback / coverage gap）. 台股代號：上市 {ticker}.TW | 上櫃 {ticker}.TWO_
```

---

## Attribution Corrections

Embedded in `_processed` output of the Tier 2 FinMind script and respected in
card rendering. Reference: `references/data-sources.md` §Attribution.

1. **月營收截止日是每月10日（曆日）** — 證交法第36條。不是月底，不是15日。
2. **融資 vs 融券方向相反** — 融資↑ = 散戶加碼多單；融券↑ = 放空部位增加。
   不可合併為單一信號。
3. **三大法人特性不同** — 外資（大型趨勢跟隨）、投信（較小常逆外資）、
   自營商（多為避險，方向參考意義較低）。不可合併為單一「法人」信號。
4. **董監持股質押率 > 50% 是治理紅旗** — 高質押率創造壓低股價誘因（葉銀華 2008）。

---

## Fallback Behavior (Pattern A + B)

### Pattern A — Auto-fallback (default)

On Tier 1 failure (HTTP 5xx / network error / timeout > 30s / schema drift):
1. Log warning: `"primary {source}.{action} failed ({reason}); falling back to FinMind"`
2. Retry via FinMind equivalent (see decision table in `references/data-sources.md`)
3. Set `_meta.fallback_used = true` in that field's envelope
4. Request continues without user intervention

### Pattern B — Manual control

- `--no-fallback`: disable auto-fallback; Tier 1-only mode (fails loud)
- `--source finmind`: force FinMind path (bypass Tier 1; useful for
  cross-validation or testing)

### Known Tier 1 gaps → FinMind by default (not a "fallback", by design)

| Gap | FinMind endpoint |
|-----|------------------|
| 日 per-stock 三大法人 flow | `TaiwanStockInstitutionalInvestorsBuySell` (T86 equivalent) |
| 歷史 OHLCV by ticker (TWSE OpenAPI only returns latest snapshot) | `TaiwanStockPrice` |
| 市場合計三大法人 BFI82U (TWSE returns HTML) | `TaiwanStockTotalInstitutionalInvestors` or skip |

---

## Calendar Convention

- **MOPS** uses ROC calendar (民國年 = Gregorian − 1911). 2024 = ROC 113;
  2026 = ROC 115. `mops_client.py` accepts ROC year directly; no auto-conversion
  — callers MUST convert before invocation.
- **TWSE OpenAPI** uses Gregorian `YYYYMMDD`.
- **FinMind** uses Gregorian `YYYY-MM-DD`.
- Skill renderer converts all dates to Gregorian for display.

---

## Cache

Per-source cache directories under `$INVESTING_TOOLKIT_CACHE`:

- `$CACHE/mops/` — company disclosures (TTL: 24h for current quarter,
  permanent for historical)
- `$CACHE/twse_openapi/` — trading snapshots (TTL: 24h for daily, 7d for
  listed-companies metadata)
- `$CACHE/finmind/` — Tier 2 fallback cache (TTL: 24h)

---

## Cross-Plugin Handoff

After the snapshot card is produced, pass it to `domain-teams:investing-team`
Taiwan-Specific Diagnosis workflow:

```
Workflow: taiwan-stock-snapshot → macro-regime-snapshot → domain-teams:investing-team
```

Pass the full data fixture (including `mops.*`, `twse.*`, `finmind.*` and any
`_meta.fallback_used` flags) as `### Input` seed context. The investing-team
Taiwan-Specific Diagnosis gate (MAY level) auto-triggers for `.TW` / `.TWO`
tickers and leverages the primary-source disclosures for ISQ gate
cross-validation.

---

## CasualMarket MCP (Optional: Real-time Taiwan quotes)

CasualMarket is an external MCP server for live TWSE/OTC quotes, 外資動向,
and real-time valuation multiples. It is NOT bundled with investing-toolkit.
Install separately via `claude plugin add casualmarket` to enable real-time
quotes (延遲15分鐘) and live 三大法人 fetches alongside the Tier 1/2
primary-source layers above.
