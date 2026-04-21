---
name: investment-memo-writer
description: Full investment memo pipeline. Orchestrates data-fetcher (yfinance + FRED) → macro-regime-snapshot → domain-teams:investing-team (Deep Equity Research Memo protocol + all gates) → optional docs-team formatting. This is the primary cross-plugin delegation skill in the repo.
---

# investment-memo-writer

> **Dual-mode execution (v1.14.0+, corrected v1.16.1)**: The `uv run ${CLAUDE_SKILL_DIR}/scripts/...` commands below are canonical. Matching `investing-toolkit` MCP tools are registered alongside (`investing-toolkit:*` namespace) — Claude may call either path; both return identical JSON. ⚠️ **Cowork limitation**: MCP does NOT bypass Cowork sandbox URL allowlist (v1.14.0 premise was wrong, confirmed v1.16.1) — both paths equally blocked in Cowork. Use Claude Code CLI for this skill. Full MCP tool catalog: [`docs/mcp-setup.md`](../../docs/mcp-setup.md).

Orchestrate a full investment memo from raw ticker to polished document. This skill
coordinates three subsystems: data fetching (investing-toolkit), regime context
(macro-regime-snapshot), and analysis + gates (domain-teams:investing-team). Optionally
pass the finished memo to docs-team for polished formatting.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | e.g. AAPL, NVDA, 2330.TW |
| `scope` | no | `deep` | `deep` = full memo; `quick` = summary snapshot |
| `output_language` | no | detect from user | Set to `zh-TW` for .TW/.TWO tickers automatically |

**Taiwan detection**: If the ticker ends in `.TW` or `.TWO`, output_language defaults
to `zh-TW` and the investing-team Taiwan Local Rigor gate (MAY level) is
auto-enabled. Phase 1 will launch the MOPS + TWSE OpenAPI Tier 1 pipeline
(公司揭露 + 交易) with FinMind as Tier 2 auto-fallback + T86 gap-fill (per
`taiwan-stock-snapshot` v1.13.0 architecture).

---

## Pipeline

### Phase 1 — Data Fetch (data-fetcher agent)

Launch the data-fetcher agent (haiku, low cost). Commands differ by ticker market:

**US ticker** (e.g. AAPL, NVDA, MSFT):
```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --period 2y
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --action info
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series T10Y2Y,DGS10,CPIAUCSL,GDPC1 --periods 12
# v1.13.0: SEC EDGAR primary-source (filings index + XBRL structured facts)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/sec_edgar_client.py --ticker {ticker} --action filings --forms 10-K,10-Q,8-K,4 --limit 8
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/sec_edgar_client.py --ticker {ticker} --action facts
```

**Japan ticker** (4-digit code, optionally ending in `.T` or `.TO`) — v1.15.0:
Dual-mode fundamentals. With `EDINET_API_KEY` set → Tier A primary-source
(金融庁 有報 / 四半期 / 臨時 / 大量保有); without key → yfinance Tier 2
scraper fallback (provenance explicitly labelled). TDnet Yanoshin index
always available for 決算短信 + material events, same-day. See
`../japan-stock-snapshot/SKILL.md` for full tier-routing rationale.

```
# Shared (price context + macro). yfinance .T works for JP snapshot.
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker4}.T --period 2y
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker4}.T --action info
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series T10Y2Y,DGS10,CPIAUCSL,GDPC1 --periods 12

# Tier A path (IF EDINET_API_KEY is set) — 金融庁 primary-source
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/edinet_client.py --action filing-summary --ticker {ticker4} --days 365
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/edinet_client.py --action list-filings --ticker {ticker4} --forms 180,220,350 --days 180 --limit 15

# Tier 2 fallback (ELSE — surface degraded provenance prominently)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker4}.T --action financials --period annual
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker4}.T --action financials --period quarterly

# TDnet same-day index (no key) — always run
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/tdnet_client.py --ticker {ticker4} --limit 20
```

`{ticker4}` = 4-digit 証券コード (e.g. `7203` for Toyota, `6758` for Sony).

**Taiwan ticker** (ticker ends in `.TW` or `.TWO`) — v1.13.0 restructure:
MOPS + TWSE OpenAPI are Tier 1 primary (金管會法定揭露 + 交易所公開資料);
FinMind retained as Tier 2 auto-fallback + T86 per-stock flow gap-fill.

```
# Shared (price context + macro)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --period 2y
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/yfinance_client.py --ticker {ticker} --action info
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/fred_client.py --series T10Y2Y,DGS10,CPIAUCSL,GDPC1 --periods 12

# Tier 1 Primary: MOPS (公司揭露 — 公司基本 + IFRS 財報 + 月營收 + 持股 + 股利)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action company-basic
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action balance-sheet --year {current_roc} --season {last_reported_q}
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action income-statement --year {current_roc} --season {last_reported_q}
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action cash-flow --year {current_roc} --season {last_reported_q}
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action monthly-revenue --year {current_roc} --month {current_month}
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action director-holdings --year {current_roc} --month {current_month}
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/mops_client.py --ticker {ticker_code} --action dividends --first-year {roc_minus_5} --last-year {current_roc}

# Tier 1 Primary: TWSE OpenAPI (交易 — 日行情 + 融資融券)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/twse_openapi_client.py --action daily-price --ticker {ticker_code}
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/twse_openapi_client.py --action margin-balance --ticker {ticker_code}

# Tier 2 Fallback (auto-triggered on Tier 1 5xx/timeout; also fills Tier 1 gap
# for daily T86 三大法人 per-stock flow which TWSE OpenAPI does not expose)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run ${CLAUDE_SKILL_DIR}/scripts/finmind_client.py --ticker {ticker_code} --dataset TaiwanStockInstitutionalInvestorsBuySell --date-start {date_start_3mo}
```

`{ticker_code}` = ticker with `.TW`/`.TWO` suffix stripped (e.g. `2330`).
`{current_roc}` = ROC year (Gregorian − 1911). `{last_reported_q}` ∈ {1,2,3,4}.

Reference: `../../agents/data-fetcher.md`

Expected output keys:
- All tickers: `price_history`, `company_info`, `macro`
- US (v1.13.0+): `sec_filings`, `sec_facts`
- Taiwan (v1.13.0 restructured): `mops_company_basic`,
  `mops_balance_sheet`, `mops_income_statement`, `mops_cash_flow`,
  `mops_monthly_revenue`, `mops_director_holdings`, `mops_dividends`,
  `twse_daily_price`, `twse_margin_balance`, `finmind_institutional`
  (fallback + T86 gap-fill)

The fixture is the seed context passed to Phase 3.

**Data gap — US (REDUCED in v1.13.0)**: SEC EDGAR now provides all financial
statements (XBRL structured facts) + narrative (10-K / 10-Q / 8-K / Form 4
filings). yfinance remains snapshot-only. Analyst consensus + forward
guidance still external (deferred to v1.13.x patches — finnhub /
alphavantage candidates).

**Data gap — Taiwan (ADDRESSED in v1.13.0)**: MOPS provides all 3 IFRS
statements (t164sb03/04/05) + 月營收 + 持股 + 股利 as Tier A primary source
(金管會法定揭露). FinMind retained as Tier 2 fallback + T86 per-stock flow.

---

### Phase 2 — Regime Context (macro-regime-snapshot skill)

Launch `macro-regime-snapshot` skill to get:
- IC (Investment Clock) phase
- GIP (Growth-Inflation-Policy) quadrant
- Yield curve status (T10Y2Y)

Pass the `macro` key from the Phase 1 fixture as pre-fetched data to avoid a duplicate
FRED call.

---

### Phase 3 — Full Memo (domain-teams:investing-team)

Launch `domain-teams:investing-team` with the **Deep Equity Research Memo**
protocol (`protocols/deep-equity-research-memo.md`).

**History note (v1.16.5, correcting v1.12.0 stale routing)**: v1.12.0
wrongly retargeted Phase 3 from `investing-team` → `research-team` under
the premise that investing-team was "v5.0.0-v5.1.0 transient". That
premise was false — investing-team was created at v5.0.0 as a
permanent team (12 standards, 5 protocols, 5 rubrics, ISQ gate at
v5.1.0, Visibility Convention at v5.2.0) and has been the canonical
investment-analysis target since. research-team's own SKILL.md
(since v5.0.0) explicitly redirects investment work back to
investing-team. v1.16.5 restores the canonical route per CLAUDE.md
§Cross-Plugin Delegation Contract.

**Agent launch note**: Pass the data fixture from Phase 1 and the regime
call from Phase 2 as `### Input` seed context. The investing-team worker
runs the full Deep Equity Research Memo protocol. Do not summarize or
pre-analyze the data yourself — pass it raw.

**Visibility requirement**: The agent prompt sent to investing-team
MUST include the skill-team Visibility Convention clause requiring
TaskUpdate emission at 3 levels (phase transitions / milestones /
heartbeat ≤60s). See `domain-teams:skill-team` SKILL.md §Visibility
Convention and this skill's §Narration Convention below.

**Gates that run** (investing-team canonical gate stack):

| Gate | Level | Source |
|------|-------|--------|
| Primary-Source Citation Compliance | **MUST** | `checklists/primary-source-citation-compliance.md` |
| Investment Thesis Soundness | **MUST** | `checklists/investment-thesis-soundness-checklist.md` |
| Scenario Stress-Test | SHOULD | `rubrics/scenario-stress-test-gate.md` |
| Position-Sizing Rationale | SHOULD | `rubrics/position-sizing-rationale-gate.md` |
| Market-Regime Consistency | SHOULD | `rubrics/market-regime-consistency-gate.md` |
| Signal Quality (ISQ) | SHOULD | `rubrics/signal-quality-assessment-gate.md` |
| Taiwan Local Rigor | MAY | `rubrics/taiwan-local-rigor-gate.md` (auto-triggered for .TW/.TWO) |

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

> "Starting Phase 3 — dispatching investing-team for deep equity memo
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
3. The investing-team worker owns analysis quality; this skill owns data assembly
4. Gate verdicts are produced by investing-team evaluator agents — not by this skill

**What this skill does**: assemble + pipeline
**What investing-team does**: analyze + evaluate + gate (via the
Deep Equity Research Memo protocol + 2 MUST + 4 SHOULD + 1 MAY gates)

---

## Limitations

- **US financial statements**: auto-sourced via SEC EDGAR (v1.13.0+). yfinance
  remains snapshot-only. Analyst consensus + forward guidance still external.
- **Taiwan financial statements**: auto-sourced via MOPS (v1.13.0+ — t164sb03
  資產負債表 / t164sb04 綜合損益表 / t164sb05 現金流量表). FinMind retained
  as Tier 2 fallback.
- yfinance is an unofficial scraper. Data may lag or be temporarily unavailable.
- SEC EDGAR requires `User-Agent` header compliance + 10 req/sec rate limit
  (built into `sec_edgar_client.py`).
- MOPS JSON API is zero-auth but back-end is `mops.twse.com.tw` — respect
  client-side throttle (no parallel burst).
- FinMind anonymous limit: 300 req/hr. Set `FINMIND_API_TOKEN` env var for 600 req/hr.
- FRED without API key: ~100 requests/day. Set `FRED_API_KEY` env var for higher limits.
  See `investing-toolkit/scripts/README.md`.
