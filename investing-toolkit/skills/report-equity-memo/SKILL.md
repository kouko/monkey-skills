---
name: report-equity-memo
description: >-
  Layer 3 (Report) orchestrator producing a full equity investment memo
  (Markdown). Country-routes by ticker suffix to data-{us,jp,tw,kr,cn}
  pack.py memo-fetch + regime-pack, runs analysis-dcf + analysis-macro-regime
  on the pre-fetched JSON, then delegates the Deep Equity Research Memo
  protocol (+ 2 MUST / 4 SHOULD / 1 MAY gates) to domain-teams:investing-team.
  Optional final formatting via domain-teams:docs-team. No data fetching, no
  scoring inside this skill — pure pipeline orchestration over data-* +
  analysis-* + cross-plugin delegation. 株式投資メモの編成層。權益投資備忘錄編排層。
---

# report-equity-memo

Layer 3 orchestrator in the v2.0.0 three-layer architecture
(Data → Analysis → Report). This skill owns **pipeline assembly only** — it
does not fetch data, compute indicators, or render verdicts inline. All
fetching is delegated to Layer 1 (`data-{country}`), all numerical compute
to Layer 2 (`analysis-*`), and all analytical judgement + gates to
`domain-teams:investing-team` per the Cross-Plugin Delegation Contract.

> **Migration note (v2.0.0)**: This skill replaces the v1.x
> `investment-memo-writer`. The legacy skill is preserved during the
> transition window and will be deleted in v2.0.0 Task 5.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | e.g. `AAPL`, `7203` (or `7203.T`), `2330.TW`, `005930.KS`, `600519.SS` |
| `scope` | no | `deep` | `deep` = full memo; `quick` = summary snapshot (per investing-team protocol routing) |
| `output_language` | no | auto-detect | `.TW` / `.TWO` → `zh-TW`; `.T` / `.TO` / 4-digit JP → `ja`; `.KS` / `.KQ` → `ko`; `.SS` / `.SZ` / `.HK` → `zh-CN`; otherwise infer from user message |
| `peers` | no | — | **Deferred to PR 2** (analysis-comps integration). Will accept a comma-separated peer list once PR 2 ships. |

### Country detection

Ticker suffix → `data-{country}` skill (preserves v1.x convention):

| Suffix / pattern | Country | data skill | yfinance ticker rewrite |
|---|---|---|---|
| `.TW`, `.TWO` | Taiwan | `data-tw` | unchanged (e.g. `2330.TW`) |
| `.T`, `.TO`, bare 4-digit (e.g. `7203`) | Japan | `data-jp` | auto-append `.T` (handled inside `data-jp/pack.py`) |
| `.KS`, `.KQ` | Korea | `data-kr` | unchanged |
| `.SS`, `.SZ`, `.HK` | China / HK | `data-cn` | unchanged |
| anything else (e.g. `AAPL`, `NVDA`) | US | `data-us` | unchanged |

Set `${COUNTRY}` accordingly for the rest of the pipeline.

---

## Pipeline

### Phase 1 — Data Fetch

Single subprocess call per ticker. The country-bundled `pack.py --pack memo-fetch`
facade composes all required clients (e.g. SEC EDGAR + yfinance + FRED for US;
EDINET + TDnet + yfinance for JP with Tier-A / Tier-2 routing on `EDINET_API_KEY`;
MOPS + TWSE OpenAPI + FinMind gap-fill for TW; FDR for KR; NBS + akshare for CN).

```bash
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache \
  uv run ${CLAUDE_PLUGIN_ROOT}/skills/data-${COUNTRY}/scripts/pack.py \
    --ticker ${TICKER} --pack memo-fetch \
    > /tmp/${TICKER_SAFE}-fetch.json
```

`${TICKER_SAFE}` strips the suffix (`AAPL`, `7203`, `2330`, `005930`, `600519`) for filesystem safety.

The data layer owns Tier-A / Tier-2 routing; this skill never decides which
client to call — `pack.py` returns a single normalised JSON regardless of
underlying source mix. Provenance labels (e.g. `_provenance.tier_label`) ride
along on the payload and surface in the final memo.

### Phase 2 — Macro Regime

Fetch the macro regime-pack(s) relevant to the ticker. By default fetch the
ticker's home country. For cross-listed exposure or when `scope=deep` and
the user has flagged macro context (e.g. an exporter sensitive to US rates),
fetch additional countries.

```bash
# Per relevant country (always at minimum the ticker's home country)
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache \
  uv run ${CLAUDE_PLUGIN_ROOT}/skills/data-${COUNTRY}/scripts/pack.py \
    --pack regime-pack \
    > /tmp/${COUNTRY}-regime.json
# (repeat for additional countries as needed: us / jp / tw / kr / cn)

# Compose into a regime card
uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-macro-regime/scripts/regime_compose.py \
  --input ${COUNTRY}=/tmp/${COUNTRY}-regime.json[,us=/tmp/us-regime.json,...] \
  > /tmp/regime-card.json
```

`analysis-macro-regime` accepts any subset of `us/jp/tw/kr/cn` so the cross-country
list scales with the memo's scope.

### Phase 3 — Analysis

Run pure-compute analysis skills on the Phase 1 fetch JSON.

```bash
# DCF — 3-stage Damodaran with 3×3 sensitivity
uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-dcf/scripts/dcf_compute.py \
  --input /tmp/${TICKER_SAFE}-fetch.json \
  > /tmp/${TICKER_SAFE}-dcf.json

# [PR 2: insert analysis-comps step here]
# uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-comps/scripts/comps_compute.py \
#   --anchor /tmp/${TICKER_SAFE}-fetch.json \
#   --peers /tmp/peer-1-fetch.json,/tmp/peer-2-fetch.json,... \
#   > /tmp/${TICKER_SAFE}-comps.json
# (peer-discovery research-agent + per-peer comps-multiples fetch lands in PR 2)
```

Both analysis skills are pure I/O-free compute (Layer 2 contract). They each
emit a JSON-only payload — no Markdown, no verdict prose. That is investing-team's job.

### Phase 4 — Delegate to `domain-teams:investing-team`

Launch `domain-teams:investing-team` with the **Deep Equity Research Memo** protocol
(`protocols/deep-equity-research-memo.md`) and the canonical gate stack.

**Per Cross-Plugin Delegation Contract (CLAUDE.md §Cross-Plugin Delegation Contract):**

1. Pass **paths** to the Phase 1 / 2 / 3 JSONs as `### Resource Paths` — never file content
2. Pass the ticker, scope, output_language, country code as `### Input` seed context
3. The investing-team worker self-loads its standards / protocols / rubrics and runs the full gate stack
4. Gate verdicts (PASS / NEEDS_REVISION) flow back from investing-team's evaluators — this skill does not produce verdicts
5. Visibility Convention: include the skill-team TaskUpdate cadence clause (phase transitions / milestones / heartbeat ≤60s) so the user sees progress during the multi-minute investing-team run

**Gates that run** (investing-team canonical stack):

| Gate | Level | Source |
|------|-------|--------|
| Primary-Source Citation Compliance | **MUST** | `checklists/primary-source-citation-compliance.md` |
| Investment Thesis Soundness | **MUST** | `checklists/investment-thesis-soundness-checklist.md` |
| Scenario Stress-Test | SHOULD | `rubrics/scenario-stress-test-gate.md` |
| Position-Sizing Rationale | SHOULD | `rubrics/position-sizing-rationale-gate.md` |
| Market-Regime Consistency | SHOULD | `rubrics/market-regime-consistency-gate.md` |
| Signal Quality (ISQ) | SHOULD | `rubrics/signal-quality-assessment-gate.md` |
| Taiwan Local Rigor | MAY | `rubrics/taiwan-local-rigor-gate.md` (auto-triggered for `.TW` / `.TWO`) |

The investing-team output is the memo body (Markdown).

### Phase 5 — Format (optional, `domain-teams:docs-team`)

If the user requests polished document output (PDF-ready memo, formatted
report, vault-ready note), pass the Phase 4 memo as input to
`domain-teams:docs-team`. Skip this phase for in-conversation analysis or
when the memo is already in a target-ready shape.

For Obsidian vault delivery (`output=obsidian` or natural-language intent),
call `obsidian:obsidian-markdown` after docs-team formatting to apply
frontmatter / wikilinks / callouts and write to the resolved vault path.

---

## Cross-Plugin Delegation Contract (recap)

This skill is the canonical example of the contract codified in CLAUDE.md:

- **Data layer stays in toolkit, analysis layer stays in domain-teams** —
  `report-equity-memo` only orchestrates data fetch + pipeline; gate logic
  belongs to `domain-teams:investing-team`.
- **Delegation = pass paths + structured seed context** — never file content,
  never inlined analysis.
- **Gate verdicts flow back** — `PASS` / `NEEDS_REVISION` from investing-team
  evaluators are surfaced in the final memo "Gate Results" section, not
  swallowed by this skill.

---

## Limitations

- **Comps section** (relative valuation) is deferred to **PR 2** —
  `analysis-comps` skill + `data-{country}/pack.py --pack comps-multiples`
  + research-agent peer-discovery wiring. Until PR 2 lands, the memo's
  Relative Valuation section is provided by investing-team prose only,
  without a structured peer table.
- yfinance is an unofficial scraper (Tier 2). Tier A primary-source paths
  are taken automatically when available (SEC EDGAR for US; EDINET for JP
  when `EDINET_API_KEY` set; MOPS + TWSE OpenAPI for TW always).
- Analyst consensus + forward guidance are not in scope (philosophy:
  primary-source equity research). If consensus context is needed, surface
  the data gap in the memo's "Limitations" rather than mocking it.
- `data-{country}/pack.py --pack memo-fetch` is single-ticker by design
  (heavy SEC / EDINET / MOPS calls). Batch memo runs over many tickers
  must be sequenced at the user level.

---

## i18n footer

- 日本語: 株式投資メモの編成層（Layer 3）。ticker suffix で
  `data-{us,jp,tw,kr,cn}` の memo-fetch / regime-pack を country-route し、
  `analysis-dcf` + `analysis-macro-regime` を pure compute で走らせ、Deep
  Equity Research Memo protocol（2 MUST + 4 SHOULD + 1 MAY gate）の実行を
  `domain-teams:investing-team` に委譲。最終整形は任意で
  `domain-teams:docs-team`。
- 繁體中文: 權益投資備忘錄編排層（Layer 3）。依 ticker 後綴路由至
  `data-{us,jp,tw,kr,cn}` 的 memo-fetch / regime-pack，於
  `analysis-dcf` + `analysis-macro-regime` 進行純計算，再將 Deep Equity
  Research Memo protocol（2 MUST + 4 SHOULD + 1 MAY 閘）委派給
  `domain-teams:investing-team`。最終排版可選 `domain-teams:docs-team`。
- English: Layer 3 orchestrator for equity investment memos. Country-routes
  by ticker suffix to `data-{us,jp,tw,kr,cn}` memo-fetch / regime-pack,
  runs `analysis-dcf` + `analysis-macro-regime` (pure compute), delegates
  the Deep Equity Research Memo protocol (2 MUST + 4 SHOULD + 1 MAY gates)
  to `domain-teams:investing-team`, optional final formatting via
  `domain-teams:docs-team`.
