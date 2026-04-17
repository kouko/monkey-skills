---
name: taiwan-stock-snapshot
description: >-
  Taiwan equity snapshot via FinMind. Fetches 三大法人買賣超、月營收、融資融券、董監持股
  for TWSE and OTC-listed stocks, composes a structured snapshot card with
  attribution-corrected signal interpretation, and prepares a handoff fixture
  for domain-teams:investing-team Taiwan-Specific Diagnosis.
  台股快照擷取。三大法人・月営収・信用取引・役員持株。
---

# taiwan-stock-snapshot

Taiwan equity data snapshot via FinMind API. Produces a structured card
covering price, institutional flow (三大法人), monthly revenue trend (月營收),
insider ownership (董監持股), and margin/short data (融資融券).

This skill is **data-only** — it does not analyze or generate investment verdicts.
The card is designed for handoff to `domain-teams:investing-team` Taiwan-Specific
Diagnosis workflow.

**Requires**: `scripts/finmind_client.py` (ships with investing-toolkit v1.1.0)

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | TWSE/OTC code, e.g. `2330`, `2330.TW`, `2454.TWO` |
| `period` | no | `1y` | Price lookback: `3mo`, `6mo`, `1y`, `2y` |

Ticker format: 4-digit code, `.TW` or `.TWO` suffix accepted (stripped by script).

---

## How It Works

### Step 1 — Launch data-fetcher agent

Launch `../../agents/data-fetcher.md` (haiku model) with these parallel fetches.
Set `{date_start_1y}` = today minus 1 year, `{date_start_3mo}` = today minus 3
months, all in `YYYY-MM-DD` format.

```
### Task
Fetch Taiwan equity data for {ticker}. Return structured JSON. Do not analyze.

### Scripts
base_path: {absolute path to investing-toolkit/scripts/}

### Fetch Requests
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockPrice --date-start {date_start_1y}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockInstitutionalInvestorsBuySell --date-start {date_start_3mo}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockMonthRevenue --date-start {date_start_1y}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockHoldingSharesPer --date-start {date_start_1y}
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockMarginPurchaseShortSale --date-start {date_start_3mo}

### Output Format
{
  "price": {...},            ← TaiwanStockPrice
  "institutional": {...},   ← TaiwanStockInstitutionalInvestorsBuySell
  "revenue": {...},         ← TaiwanStockMonthRevenue
  "holding": {...},         ← TaiwanStockHoldingSharesPer
  "margin": {...}           ← TaiwanStockMarginPurchaseShortSale
}
```

**Graceful degradation**: If any individual fetch fails, continue with available
data. Set `_partial: true` in the aggregate output.

---

### Step 2 — Compose snapshot card

Extract from data-fetcher output and render the card below. All `N/A` if absent.

**Price fields** (from `price._processed` or `price.data` latest row):

| Card field | Source |
|------------|--------|
| Close | `price.data[-1].close` |
| Date | `price.data[-1].date` |
| 52W Low | min of `low` over data |
| 52W High | max of `high` over data |
| vs 52W High % | `(close - 52W_high) / 52W_high × 100` |
| Volume (shares) | `price.data[-1].Trading_Volume` |

**Institutional flow** (from `institutional._processed`):

| Card field | Source |
|------------|--------|
| Foreign net (千股) | `institutional._processed.foreign.net` |
| Trust net (千股) | `institutional._processed.trust.net` |
| Dealer net (千股) | `institutional._processed.dealer.net` |
| Signal | See attribution rules below |

**Monthly revenue** (from `revenue._processed`):

| Card field | Source |
|------------|--------|
| Latest month revenue (千元) | `revenue._processed.latest.revenue` |
| Reference period | `revenue._processed.latest.revenue_month` |
| MoM change | compute from `revenue._processed.history[0].revenue` vs `history[1].revenue` |

**Insider ownership** (from `holding._processed`):

| Card field | Source |
|------------|--------|
| Holding % | `holding._processed.holding_pct` |
| Pledge % | `holding._processed.pledged_pct` |
| Governance flag | If pledge % > 50 → "⚠ 高質押率（> 50%），治理紅旗" |

**Margin / short** (from `margin._processed`):

| Card field | Source |
|------------|--------|
| 融資餘額 | `margin._processed.margin_purchase_balance` |
| 融券餘額 | `margin._processed.short_sale_balance` |

---

### Step 3 — Render card

```
## {TICKER} 台股快照 — {date}

**Price (TWD)**: {close} | 52W: {low}–{high} | vs 52W High: {pct}%

### 三大法人（{latest_institutional_date}）
| 投資人類型 | 買賣超（千股） | 信號方向 |
|-----------|-------------|--------|
| 外資       | {foreign_net} | ↑外資買超 / ↓外資賣超 |
| 投信       | {trust_net}   | ↑投信買超 / ↓投信賣超 |
| 自營商     | {dealer_net}  | 多為避險，方向參考意義較低 |

### 月營收（{revenue_month}）
- 本月營收：{revenue} 千元
- MoM 變動：{mom_pct}%
- _公布截止：每月10日（曆日）_

### 董監持股（{holding_date}）
- 持股比例：{holding_pct}%
- 質押比例：{pledged_pct}%
{governance_flag}

### 融資融券（{margin_date}）
- 融資餘額：{margin_balance}（↑ 散戶加碼多單）
- 融券餘額：{short_balance}（↑ 放空部位增加）

_資料來源：FinMind API（https://finmindtrade.com）_
_台股代號：上市 {ticker}.TW | 上櫃 {ticker}.TWO_
```

---

## Attribution Corrections

These corrections are embedded in the script's `_processed` output. Reference:
`references/taiwan-data-source-map.md`

1. **月營收截止日是每月10日（曆日）** — 不是月底，不是15日（證交法第36條）
2. **融資 vs 融券方向相反** — 融資↑ = 散戶加碼多單；融券↑ = 放空部位增加。
   不可合併為單一「法人買超」信號。
3. **三大法人特性不同** — 外資：大型趨勢跟隨；投信：較小常逆外資；
   自營商：多為避險，方向參考意義較低。不可合併為單一「法人」信號。
4. **董監持股質押率 > 50% 是治理紅旗** — 高質押率創造壓低股價的誘因（葉銀華 2008）。

---

## Data Availability

| Dataset | FinMind ID | Publication lag | Notes |
|---------|-----------|-----------------|-------|
| 股票日線 | TaiwanStockPrice | ~15 min (T+0) | OHLCV |
| 三大法人 | TaiwanStockInstitutionalInvestorsBuySell | T+1 (after 18:00) | Separate foreign/trust/dealer |
| 月營收 | TaiwanStockMonthRevenue | Within 10th of following month | 截止日：每月10日 |
| 董監持股 | TaiwanStockHoldingSharesPer | Quarterly | Quarterly disclosure |
| 融資融券 | TaiwanStockMarginPurchaseShortSale | T+1 (after 18:00) | Daily balance |

**Financial statements** (損益表, 資產負債表) are available via
`TaiwanStockFinancialStatements` and `TaiwanStockProfitLossStatement` datasets,
but are NOT included in the default snapshot. Request explicitly if needed.

---

## Cross-Plugin Handoff

After the snapshot card is produced, pass it to `domain-teams:investing-team`
Taiwan-Specific Diagnosis workflow:

```
Workflow: taiwan-stock-snapshot → macro-regime-snapshot → domain-teams:investing-team
```

Pass the full data fixture (including `_processed` fields) as `### Input` seed
context. The investing-team Taiwan-Specific Diagnosis gate (MAY level) auto-triggers
for `.TW` / `.TWO` tickers.

---

## FinMind Setup

```bash
# Anonymous (300 req/hr) — no setup needed
python3 finmind_client.py --ticker 2330 --dataset TaiwanStockPrice --date-start 2025-04-01

# With token (600 req/hr) — free registration
export FINMIND_API_TOKEN=your_token_here
python3 finmind_client.py --ticker 2330 --dataset TaiwanStockPrice --date-start 2025-04-01
```

Get a free token: https://finmindtrade.com

---

## CasualMarket MCP (Optional: Real-time Taiwan quotes)

CasualMarket is an external MCP server for live TWSE/OTC quotes, 外資動向,
and real-time valuation multiples. It is NOT bundled with investing-toolkit.

When installed, skills can call it directly for:
- Real-time quotes (延遲15分鐘)
- 外資動向 (live 三大法人)
- Valuation multiples (PE, PB, EV/EBITDA for TWSE/OTC)

```bash
claude plugin add casualmarket
```

See `investing-toolkit/scripts/README.md` for setup notes.
