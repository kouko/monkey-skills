---
name: investment-memo-writer
description: Full investment memo pipeline. Orchestrates data-fetcher (yfinance + FRED) → macro-regime-snapshot → domain-teams:research-team (Deep Equity Research Memo workflow + all gates) → optional docs-team formatting. This is the primary cross-plugin delegation skill in the repo.
---

# investment-memo-writer

Orchestrate a full investment memo from raw ticker to polished document. This skill
coordinates three subsystems: data fetching (investing-toolkit), regime context
(macro-regime-snapshot), and analysis + gates (domain-teams:research-team). Optionally
pass the finished memo to docs-team for polished formatting.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | e.g. AAPL, NVDA, 2330.TW |
| `scope` | no | `deep` | `deep` = full memo; `quick` = summary snapshot |
| `output_language` | no | detect from user | Set to `zh-TW` for .TW/.TWO tickers automatically |

**Taiwan detection**: If the ticker ends in `.TW` or `.TWO`, output_language defaults
to `zh-TW` and the research-team Taiwan-Specific Diagnosis gate (MAY level) is
auto-enabled. Phase 1 will also launch FinMind fetches for 三大法人, 月營收,
融資融券, and 董監持股.

---

## Pipeline

### Phase 1 — Data Fetch (data-fetcher agent)

Launch the data-fetcher agent (haiku, low cost). Commands differ by ticker market:

**US ticker** (e.g. AAPL, NVDA, MSFT):
```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --period 2y
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --action info
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series T10Y2Y,DGS10,CPIAUCSL,GDPC1 --periods 12
```

**Taiwan ticker** (ticker ends in `.TW` or `.TWO`):
```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --period 2y
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --action info
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series T10Y2Y,DGS10,CPIAUCSL,GDPC1 --periods 12
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockInstitutionalInvestorsBuySell --date-start {date_start_3mo}
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockMonthRevenue --date-start {date_start_1y}
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockHoldingSharesPer --date-start {date_start_1y}
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockMarginPurchaseShortSale --date-start {date_start_3mo}
```

`{ticker_code}` = ticker with `.TW`/`.TWO` suffix stripped (e.g. `2330`).

Reference: `../../agents/data-fetcher.md`

Expected output keys:
- `price_history`, `company_info`, `macro` (all tickers)
- `institutional`, `revenue`, `holding`, `margin` (Taiwan tickers only)

The fixture is the seed context passed to Phase 3.

**Data gap warning (US)**: yfinance does not provide financial statements (income
statement, balance sheet, cash flow). The research-team worker will note missing
financials and may prompt for SEC EDGAR data manually. Do not block — proceed with
available data.

**Data gap warning (Taiwan)**: yfinance does not provide Taiwan financial statements.
FinMind `TaiwanStockFinancialStatements` is available but not fetched by default —
request explicitly if SEC EDGAR-equivalent financials are needed.

---

### Phase 2 — Regime Context (macro-regime-snapshot skill)

Launch `macro-regime-snapshot` skill to get:
- IC (Investment Clock) phase
- GIP (Growth-Inflation-Policy) quadrant
- Yield curve status (T10Y2Y)

Pass the `macro` key from the Phase 1 fixture as pre-fetched data to avoid a duplicate
FRED call.

---

### Phase 3 — Full Memo (domain-teams:research-team)

Launch `domain-teams:research-team` with the **Deep Equity Research Memo** workflow.

**History note (v1.12.0)**: This phase previously targeted
`domain-teams:investing-team` (v5.0.0-v5.1.0 transient team). As of v1.12.0
the skill routes to `domain-teams:research-team`, whose description explicitly
covers "investment or macro analysis (valuation, asset allocation,
Investment Clock regime diagnosis)". research-team applies the same
primary-source-grounding + gate discipline with the full investment analysis
workflow.

**Agent launch note**: Pass the data fixture from Phase 1 and the regime call from
Phase 2 as `### Input` seed context. The research-team worker will run the full
6-phase Deep Equity Research Memo protocol. Do not summarize or pre-analyze the data
yourself — pass it raw.

**Visibility requirement (v1.12.0)**: The agent prompt sent to research-team
MUST include the skill-team Visibility Convention clause requiring
TaskUpdate emission at 3 levels (phase transitions / milestones /
heartbeat ≤60s). See `domain-teams:skill-team` SKILL.md §Visibility
Convention and this skill's §Narration Convention below.

**Gates that run** (all handled by research-team):

| Gate | Level | Description |
|------|-------|-------------|
| Data completeness check | MUST | Flags missing financials, stale data |
| Framework consistency check | MUST | IC/GIP alignment with thesis |
| Bull/bear/base scenario coverage | SHOULD | All three scenarios present |
| Valuation cross-check | SHOULD | Multiple methods reconciled |
| Risk factor completeness | SHOULD | Macro + idiosyncratic risks |
| ISQ (Investment Signal Quality) | SHOULD | Analysis credibility; PASS / PASS_WITH_NOTES / NEEDS_REVISION |
| Taiwan-Specific Diagnosis | MAY | Auto-triggered for .TW/.TWO tickers |

---

### Phase 4 — Format (optional, domain-teams:docs-team)

If the user requests polished document output (e.g., PDF-ready memo, formatted report),
launch `domain-teams:docs-team` with the raw memo from Phase 3 as input.

Skip this phase if the user only needs the analysis text in conversation.

---

### Phase 5 — Persist + Deliver (v1.12.0)

**Default behavior: write memo to file, then deliver summary to chat.**

#### Write path (priority order)

1. **Obsidian mode** — if user invoked with `output=obsidian` or natural-
   language intent ("寫成 Obsidian 筆記" / "save to Obsidian" / "put in
   vault"): resolve vault path via:
   - `$OBSIDIAN_VAULT_PATH` env var (if set)
   - Probe: `~/kouko-obsidian-vault/`, `~/Documents/Obsidian/`,
     `~/iCloud Drive/Obsidian/`
   - Read `{vault}/CLAUDE.md` for folder convention (look for
     patterns like `research/`, `投資/`, etc.). Default: `{vault}/research/`
   - Use `obsidian:obsidian-markdown` skill for frontmatter + Obsidian-
     specific formatting (wikilinks, callouts)
   - Filename: `{YYYY-MM-DD} {ticker} investment memo.md`
   - If no vault detected, fall back to default path (step 2) with a
     chat warning "Obsidian vault not detected"

2. **Default plugin-data path**:
   `$CLAUDE_PLUGIN_DATA/memos/{YYYY-MM-DD}_{ticker}_{mode}_memo.md`
   where `{mode}` ∈ `{deep, quick}` (mode-separated filenames so
   deep + quick re-runs don't overwrite each other; same-mode re-runs
   overwrite by default)

3. **Fallback** (if `$CLAUDE_PLUGIN_DATA` unset, standalone
   invocation): `~/.cache/investing-toolkit/memos/{YYYY-MM-DD}_{ticker}_{mode}_memo.md`

#### Required frontmatter

```yaml
---
title: "{ticker} investment memo"
date: YYYY-MM-DD
ticker: {TICKER}
mode: {deep|quick}
recommendation: {Buy|Hold|Sell}
confidence: {IPCC AR5 scale}
target_base: {$}
target_bull: {$}
target_bear: {$}
stop_loss: {$}
tags: [investment-memo, {ticker-lower}, {sector}, {regime-phase}]
---
```

#### Chat delivery

After file write, chat output contains **only**:
- 📄 File path link at the top
- **Executive summary** (~150 words, memo's §1 verbatim)
- **Gate verdicts table** (from memo's "Gate Results Summary" section)
- Data freshness summary from `_summary` key of data fixture
- Taiwan data gap notice if applicable (v1.0.0 limitation)
- Note: "Full memo at {path} — see for scenarios, risks, valuation detail"

**Do NOT** repeat the full 2000+ word memo in chat. The file is
authoritative; chat is the summary.

---

## Narration Convention (v1.12.0)

Before each Agent dispatch in this pipeline, the controller (Claude)
narrates:
- **Expected duration** of the agent task
- **What's about to happen** (which phase / which agent)
- **Expected TaskUpdate cadence** per skill-team Visibility Convention

Example before Phase 3 dispatch:

> "Starting Phase 3 — dispatching research-team for deep equity memo
> (expected 2-5 min). You will see TaskUpdates at phase transitions,
> milestones, and heartbeats (~60s max silence). If silent > 2 min,
> likely agent stuck — interrupt and I'll investigate."

This narration sets user expectation before any silent period. Combined
with skill-team Visibility Convention (TaskUpdate cadence; see
`domain-teams:skill-team` SKILL.md §Visibility Convention), provides
both expectation-setting (軸 1) and real-time visibility (軸 2).

---

## Cross-Plugin Delegation Contract

This skill is the repo's first cross-plugin delegation pattern
(investing-toolkit → domain-teams).

**Delegation rules**:
1. Pass **file paths** to agents, not raw file content
2. Pass the data fixture as structured seed context in `### Input` — not as analysis
3. The research-team worker owns analysis quality; this skill owns data assembly
4. Gate verdicts are produced by research-team evaluator agents — not by this skill

**What this skill does**: assemble + pipeline  
**What research-team does**: analyze + evaluate + gate

---

## Limitations

- yfinance does not provide financial statements (income statement, balance sheet,
  cash flow). Memo will have fundamental gaps unless the user supplies SEC EDGAR
  (US) or FinMind `TaiwanStockFinancialStatements` (Taiwan) data separately.
- yfinance is an unofficial scraper. Data may lag or be temporarily unavailable.
- FinMind anonymous limit: 300 req/hr. Set `FINMIND_API_TOKEN` env var for 600 req/hr.
- FRED without API key: ~100 requests/day. Set `FRED_API_KEY` env var for higher limits.
  See `investing-toolkit/scripts/README.md`.
