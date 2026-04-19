---
name: invest-portfolio
description: >-
  Portfolio review pipeline. Parses holdings (CSV or inline list), batch-fetches
  current prices via yfinance, overlays macro regime, computes position P&L and
  portfolio weights, then delegates to domain-teams:investing-team Portfolio
  Review workflow for rebalance recommendations and Kelly-based sizing.
  ポートフォリオレビュー。組合複盤與再平衡建議。
---

# invest-portfolio

> **MCP-aware execution (v1.14.0+)**: If `investing-toolkit` MCP tools (`yfinance_batch`, `yfinance_history`, `yfinance_info`, `finmind_fetch`) are registered in your session, prefer them over the `uv run scripts/...` subprocess commands shown below. Identical JSON payloads, faster on repeat calls, bypasses the Claude Desktop Cowork sandbox. Subprocess commands remain the canonical spec and fallback.

Full portfolio review pipeline — from holdings input to rebalance recommendations.
This skill handles data assembly; analysis and sizing decisions are delegated to
`domain-teams:investing-team` Portfolio Review workflow.

---

## Inputs

| Format | Example |
|--------|---------|
| CSV file | `holdings.csv` (columns: ticker, shares, avg_cost) |
| Inline list | `AAPL:100:150.00, MSFT:50:280.00, 2330.TW:200:550.00` |

**CSV format**:
```csv
ticker,shares,avg_cost
AAPL,100,150.00
MSFT,50,280.00
NVDA,30,420.00
2330.TW,200,550.00
```

`avg_cost` = average cost per share in the ticker's local currency.

---

## Pipeline

### Step 1 — Parse holdings

Extract ticker list and position data. Detect market from ticker suffix:
- No suffix → US
- `.TW` / `.TWO` → Taiwan (apply FinMind fetches in Step 2b if available)

---

### Step 2a — Batch price + info fetch (US positions)

Launch `../../agents/data-fetcher.md`:

```
### Fetch Requests
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --tickers {us_tickers} --action info
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --tickers {us_tickers} --period 3mo
```

---

### Step 2b — Taiwan positions (if any .TW/.TWO tickers)

```
### Fetch Requests
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --tickers {tw_tickers} --action info
- INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {tw_ticker} --dataset TaiwanStockInstitutionalInvestorsBuySell --date-start {date_start_3mo}
```

*(Run per Taiwan ticker — FinMind does not support batch in v1.1.0)*

---

### Step 3 — Macro regime context

Launch `macro-regime-snapshot` skill to get current IC phase and GIP quadrant.
Pass the macro key from Step 2 if already fetched (avoid duplicate FRED call).

---

### Step 4 — Compute portfolio snapshot

For each position, compute:

| Field | Formula |
|-------|---------|
| Current price | `info.regularMarketPrice` |
| Current value | `shares × current_price` |
| Cost basis | `shares × avg_cost` |
| P&L (amount) | `current_value − cost_basis` |
| P&L (%) | `(current_value / cost_basis − 1) × 100` |
| Weight | `current_value / total_portfolio_value × 100` |

Portfolio-level aggregates:
- Total market value
- Total cost basis
- Total P&L (amount + %)
- Weighted average PE (`Σ weight × PE`)
- Weighted average Beta (`Σ weight × Beta`)
- Largest position weight (concentration flag if > 30%)
- IC regime alignment per position

**IC regime alignment**: tag each position against the current IC phase:
- IC Phase 1 (Recovery): Equities ✓, Bonds ✓, Commodities —
- IC Phase 2 (Overheat): Commodities ✓, Equities —, Bonds —
- IC Phase 3 (Stagflation): Cash ✓, Commodities ✓, Equities —
- IC Phase 4 (Reflation): Bonds ✓, Equities ✓ (late), Commodities —

---

### Step 5 — Delegate to domain-teams:investing-team

Launch `domain-teams:investing-team` with the **Portfolio Review** workflow.

Pass as `### Input` seed context:
1. Portfolio snapshot table (from Step 4)
2. Macro regime call (IC phase + GIP quadrant from Step 3)
3. Raw holdings (ticker, shares, avg_cost, current_price)

The investing-team worker will:
- Assess sector/regime concentration risk
- Identify positions misaligned with current IC phase
- Apply Kelly criterion / risk-budget sizing for rebalance candidates
- Produce rebalance memo with specific action suggestions

**Gates that run** (handled by investing-team):
- MUST: Primary-Source Citation Compliance
- MUST: Investment Thesis Soundness
- SHOULD: Position-Sizing Rationale
- SHOULD: Market-Regime Consistency

---

### Step 6 — Deliver

Return to user:
- Portfolio snapshot table
- Regime overlay summary
- Gate verdicts from investing-team
- Rebalance recommendations (from investing-team)
- Data freshness summary

---

## Output Format (Step 4 snapshot)

```markdown
## Portfolio Snapshot — {date}

**Total Value**: ${total_value} | **Total P&L**: ${pnl} ({pnl_pct}%)
**Weighted PE**: {wt_pe} | **Weighted Beta**: {wt_beta}
**IC Phase**: {phase} ({description})

| Ticker | Shares | Avg Cost | Price | Value | P&L% | Weight | IC Align |
|--------|--------|----------|-------|-------|------|--------|---------|
| AAPL | 100 | $150 | $195 | $19,500 | +30% | 32% | ✓ |
| MSFT | 50 | $280 | $415 | $20,750 | +48% | 34% | ✓ |
| ... |

⚠ Concentration: MSFT weight 34% > 30% threshold
```

---

## Cross-Plugin Delegation Contract

Follows `CLAUDE.md` §Cross-Plugin Delegation Contract:
- This skill handles data assembly + portfolio math
- investing-team handles analysis + rebalance logic + gate enforcement
- Gate verdicts flow back to this skill for delivery

---

## Limitations

- yfinance `regularMarketPrice` may lag by 15–20 minutes (delayed quotes)
- Cost basis is in local currency; multi-currency portfolios (USD + TWD) need
  FX rate for aggregate P&L — skill notes the discrepancy but does not convert
- Taiwan positions: institutional flow data requires FinMind (v1.1.0+)
- No historical performance tracking — point-in-time snapshot only
