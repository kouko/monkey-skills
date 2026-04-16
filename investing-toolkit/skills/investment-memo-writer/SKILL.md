---
name: investment-memo-writer
description: Full investment memo pipeline. Orchestrates data-fetcher (yfinance + FRED) → macro-regime-snapshot → domain-teams:investing-team (Deep Equity Research Memo workflow + all gates) → optional docs-team formatting. This is the primary cross-plugin delegation skill in the repo.
---

# investment-memo-writer

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
to `zh-TW` and the investing-team Taiwan-Specific Diagnosis gate (MAY level) is
auto-enabled. Note: v1.0.0 provides yfinance price/info data only for Taiwan tickers.
Full Taiwan financials (三大法人, 月營收) require **investing-toolkit v1.1.0** (FinMind).

---

## Pipeline

### Phase 1 — Data Fetch (data-fetcher agent)

Launch the data-fetcher agent (haiku, low cost) with these three commands:

```
python3 {base_path}/yfinance_client.py --ticker {ticker} --period 2y
python3 {base_path}/yfinance_client.py --ticker {ticker} --action info
python3 {base_path}/fred_client.py --series T10Y2Y,DGS10,CPIAUCSL,GDPC1 --periods 12
```

Reference: `../../agents/data-fetcher.md`

Expected output: structured JSON fixture with keys `price_history`, `company_info`,
`macro`. The fixture is the seed context passed to Phase 3.

**Data gap warning**: yfinance does not provide financial statements (income statement,
balance sheet, cash flow). The investing-team worker will note missing financials and may
prompt for SEC EDGAR data manually. Do not block on this — proceed with available data.

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

Launch `domain-teams:investing-team` with the **Deep Equity Research Memo** workflow.

**Agent launch note**: Pass the data fixture from Phase 1 and the regime call from
Phase 2 as `### Input` seed context. The investing-team worker will run the full
6-phase Deep Equity Research Memo protocol. Do not summarize or pre-analyze the data
yourself — pass it raw.

**Gates that run** (all handled by investing-team):

| Gate | Level | Description |
|------|-------|-------------|
| Data completeness check | MUST | Flags missing financials, stale data |
| Framework consistency check | MUST | IC/GIP alignment with thesis |
| Bull/bear/base scenario coverage | SHOULD | All three scenarios present |
| Valuation cross-check | SHOULD | Multiple methods reconciled |
| Risk factor completeness | SHOULD | Macro + idiosyncratic risks |
| Taiwan-Specific Diagnosis | MAY | Auto-triggered for .TW/.TWO tickers |

---

### Phase 4 — Format (optional, domain-teams:docs-team)

If the user requests polished document output (e.g., PDF-ready memo, formatted report),
launch `domain-teams:docs-team` with the raw memo from Phase 3 as input.

Skip this phase if the user only needs the analysis text in conversation.

---

### Phase 5 — Deliver

Return the full memo to the user with:
- Gate verdicts (inline from investing-team output)
- Data freshness summary from `_summary` key of data fixture
- Taiwan data gap notice if applicable (v1.0.0 limitation)

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
**What investing-team does**: analyze + evaluate + gate

---

## Limitations

- yfinance does not provide financial statements. Memo will have fundamental gaps
  unless the user supplies SEC EDGAR data separately.
- yfinance is an unofficial scraper. Data may lag or be temporarily unavailable.
- Taiwan tickers in v1.0.0: price + info only. No 三大法人, 月營收, or balance sheet.
  Full Taiwan analysis requires v1.1.0 (FinMind).
- FRED without API key: ~100 requests/day. Set `FRED_API_KEY` env var for higher limits.
  See `../../scripts/README.md`.
