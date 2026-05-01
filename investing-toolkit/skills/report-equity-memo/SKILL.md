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
> `investment-memo-writer`, which was deleted in v2.0.0. The slash command
> `/invest-memo` continues to route here.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | e.g. `AAPL`, `7203` (or `7203.T`), `2330.TW`, `005930.KS`, `600519.SS` |
| `scope` | no | `deep` | `deep` = full memo; `quick` = summary snapshot (skips Phase 2 regime fan-out + Phase 3 DCF; uses snapshot data only). investing-team protocol routing decides depth from this value. |
| `output_language` | no | auto-detect | `.TW` / `.TWO` → `zh-TW`; `.T` / `.TO` / 4-digit JP → `ja`; `.KS` / `.KQ` → `ko`; `.SS` / `.SZ` / `.HK` → `zh-CN`; otherwise infer from user message |
| `peers` | no | auto-discovery via runtime research agent | Comma-separated peer list (e.g., `MSFT,GOOGL,META,AMZN`); skips runtime peer-discovery if provided. |
| `--interactive` | no | `false` (auto mode) | When `true`, peer-discovery agent's output is presented for user confirmation before Comps fetch + analysis. |

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

> **`scope=quick` note**: quick mode runs Phase 1 only (snapshot data) and skips Phase 2 (regime) + Phase 2.5 (comps) + Phase 3 DCF. The pipeline jumps straight to Phase 4 with snapshot-only inputs; investing-team protocol routing handles the lighter analysis depth.

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

Fetch the macro regime-pack(s) relevant to the ticker.

**Deterministic default rule:**

> Default: fetch home country only. When `scope=deep`, also fetch US (for any
> non-US ticker, since US rates dominate global liquidity). Cross-listed
> exposure or sector-specific macro flags can be handled by the orchestrator's
> main agent — but the canonical default is home + (US if non-US ticker AND
> deep).

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

### Phase 2.5 — Peer Discovery + Comps Multiples

**If `--peers` provided** (manual override): skip discovery, use the list verbatim.

**Else** spawn research agent for peer-discovery at runtime:

Use `general-purpose` subagent with this prompt template:

> Find 5–8 publicly-traded competitor tickers for {anchor_ticker} ({company_name}).
>
> Selection criteria (in order):
> 1. Direct business-line competitor (same products/services)
> 2. Comparable scale tier (market cap within 0.3x–3x range)
> 3. Same primary geography or comparable geographic mix
> 4. Listed on major exchanges (US/JP/TW/KR/CN/HK/Europe)
>
> For each peer, provide:
> - Ticker symbol (with exchange suffix if non-US: .T, .TW, .KS, etc.)
> - 1-line rationale explaining why it's a comp
> - Source URL (corporate disclosure, industry report, or competitor analysis)
>
> Output as JSON:
> {"peers": [{"ticker": "MSFT", "rationale": "...", "source": "https://..."}]}
>
> Cap: 250 words total. No industry-rollup commentary — just the peer list.

**Default behavior** (configurable):

| Context | Discovery flow |
|---|---|
| Pipeline mode (called by orchestrator / memo automation) | **Auto** — agent finds peers → analysis runs immediately → peer list + rationale visible in process logs and final report |
| CLI mode (`--interactive`) | **Interactive** — agent finds peers → presents list + rationale → user `/proceed` confirms or edits → analysis runs |

**Provenance transparency requirement** (per Spec §5.6 — peer list visible at three points):

1. **During execution**: main agent logs `Using peers: X (reason), Y (reason), Z (reason)` before fetch starts
2. **In analysis JSON**: `_provenance.peer_data_sources` lists each peer + how it was selected
3. **In final memo**: Comps section header explicitly lists peers + 1-line rationale per peer

The reader never wonders "Comps against whom?"

**Then fetch + analyze**:

```bash
# 1. Fetch anchor multiples
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run \
  ${CLAUDE_PLUGIN_ROOT}/skills/data-${COUNTRY}/scripts/pack.py \
    --ticker ${ANCHOR} --pack comps-multiples \
    > /tmp/${ANCHOR_SAFE}-anchor-comps.json

# 2. Fetch peer multiples (group peers by country, run per-country batch)
# Per peer country group:
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run \
  ${CLAUDE_PLUGIN_ROOT}/skills/data-${COUNTRY}/scripts/pack.py \
    --tickers ${PEERS_FOR_COUNTRY} --pack comps-multiples \
    > /tmp/${COUNTRY}-peers-comps.json
# Repeat for each country present in the peer list.

# 3. Run analysis-comps
uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-comps/scripts/comps_compute.py \
  --anchor /tmp/${ANCHOR_SAFE}-anchor-comps.json \
  --peers /tmp/<peer1>-comps.json,/tmp/<peer2>-comps.json,... \
  --rationale-map /tmp/peer-rationales.json \
  > /tmp/${ANCHOR_SAFE}-comps.json
```

Pass `/tmp/${ANCHOR_SAFE}-comps.json` to investing-team in Phase 4 alongside `dcf.json` / `regime.json`.

### Phase 3 — Analysis

Run pure-compute analysis skills on the Phase 1 fetch JSON.

```bash
# DCF — 3-stage Damodaran with 3×3 sensitivity
uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-dcf/scripts/dcf_compute.py \
  --input /tmp/${TICKER_SAFE}-fetch.json \
  > /tmp/${TICKER_SAFE}-dcf.json
```

> **Comps note**: relative valuation is computed in **Phase 2.5** (peer
> discovery + `analysis-comps`). The resulting `/tmp/${ANCHOR_SAFE}-comps.json`
> is passed to investing-team in Phase 4 alongside the DCF and regime JSONs,
> so Phase 4's relative-valuation gates run on the structured comps JSON, not
> prose.

Each analysis skill called from Phase 3 is pure compute (Layer 2 contract).
They emit a JSON-only payload — no Markdown, no verdict prose. That is
investing-team's job.

### Phase 4 — Delegate to `domain-teams:investing-team`

Launch `domain-teams:investing-team` with the **Deep Equity Research Memo** protocol
(`protocols/deep-equity-research-memo.md`) and the canonical gate stack.

**Per Cross-Plugin Delegation Contract (CLAUDE.md §Cross-Plugin Delegation Contract):**

1. Pass **paths** to the Phase 1 / 2 / 2.5 / 3 JSONs as `### Resource Paths` — never file content. Specifically: `fetch.json` (Phase 1), `regime-card.json` (Phase 2), `comps.json` (Phase 2.5), `dcf.json` (Phase 3).
2. Pass the ticker, scope, output_language, country code as `### Input` seed context
3. The investing-team worker self-loads its standards / protocols / rubrics and runs the full gate stack — relative-valuation gates consume the structured `comps.json`, not prose
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

### Phase 5a — Format (optional, `domain-teams:docs-team`)

If the user requests polished document output (PDF-ready memo, formatted
report, vault-ready note), pass the Phase 4 memo as input to
`domain-teams:docs-team`. Skip this phase for in-conversation analysis or
when the memo is already in a target-ready shape.

### Phase 5b — Obsidian vault delivery (optional, `obsidian:obsidian-markdown`)

For Obsidian vault delivery (`output=obsidian` or natural-language intent),
call `obsidian:obsidian-markdown` after docs-team formatting to apply
frontmatter / wikilinks / callouts and write to the resolved vault path.

> **Cross-Plugin Contract recap (Phase 5b)**: Pass the docs-team Markdown
> output **path** (not content) as input to obsidian-markdown — same
> paths-not-content discipline as Phase 4.

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

- yfinance is an unofficial scraper (Tier 2). Tier A primary-source paths
  are used per `data-{country}` skill defaults (SEC EDGAR for US; EDINET for
  JP when `EDINET_API_KEY` set; MOPS + TWSE OpenAPI for TW always; FDR /
  BOK ECOS-KEYSTAT for KR; NBS new-SPA + akshare for CN). See each
  `data-*` skill SKILL.md for the per-country tier matrix.
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
