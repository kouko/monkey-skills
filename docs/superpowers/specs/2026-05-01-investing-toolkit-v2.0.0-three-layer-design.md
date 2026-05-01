# Design Spec: investing-toolkit v2.0.0 — Three-Layer Refactor + Comps Analysis

**Date**: 2026-05-01
**Previous release**: investing-toolkit v1.16.4 (PR #103) — empirical-first design rule
**Cross-plugin**: domain-teams unchanged; investing-toolkit refactor + 1 new skill
**Breaking change**: skill renames break slash-command routing → major version bump v2.0.0

---

## 1. Goal

Two coupled objectives:

**A. Architectural refactor** — split investing-toolkit's 15 skills into a clean three-layer architecture (Data / Analysis / Report) by country bundling, addressing:
- 50+ duplicate `*_client.py` files across skill `scripts/` directories (e.g. `yfinance_client.py` × 9)
- Mixed concerns: every "snapshot" / "memo-writer" skill currently does fetch + compute + format

**B. Comps Analysis** — add `analysis-comps` (multiples comparable analysis), the gap identified vs Anthropic Financial Services (Comps is one of two estimation pillars; investing-toolkit currently has DCF only).

The refactor lays the foundation; Comps lands cleanly in the new structure.

---

## 2. Context

### 2.1 Anthropic Financial Services comparison (2026-05-01 research)

Comparing investing-toolkit vs `anthropics/financial-services-plugins` (Anthropic's first vertical product, released 2026-07):

- **Anthropic positioning**: sell-side IBD/ER/PE/WM workflows, vendor-data integration (LSEG / FactSet / S&P Capital IQ), 6 named skills (Comps, DCF, Initiating Coverage, Strip Profile, DD Data Pack, Earnings Analysis).
- **investing-toolkit positioning**: buy-side primary-source equity research memo, government-data sources (SEC EDGAR / EDINET / TWSE / FRED / BOJ / NBS), 5-country macro coverage.

Three gaps identified vs Anthropic baseline:

| Gap | Triage |
|---|---|
| Comps Analysis | **KEEP** — GROUNDED + ESSENTIAL; estimation pair half is missing |
| Earnings Analysis | **DEFER** — consensus data behind paywall, conflicts with primary-source principle |
| 3-statement model | **DROP** — sell-side IBD artifact, philosophy mismatch |

(See `proposal-critique` triage on 2026-05-01 for full analysis.)

### 2.2 Script duplication audit (2026-05-01)

Plugin currently has 15 skills sharing identical client scripts via copy:

| Client | Copies | MD5 |
|---|---|---|
| `yfinance_client.py` | 9 | identical |
| `fred_client.py` | 6 | identical |
| `sec_edgar_client.py`, `mops_client.py`, `twse_openapi_client.py`, `finmind_client.py`, `edinet_client.py` | 4 each | identical |
| `tdnet_client.py`, `ta_client.py` | 3 each | identical |
| `statgov_client.py`, `ndc_client.py`, `nbs_client.py`, `fdr_client.py`, `estat_client.py`, `ecb_client.py` | 2 each | identical |

Total: **~50 duplicate client file instances**. All MD5-identical (pure copies, no version drift).

Cause: `${CLAUDE_SKILL_DIR}/scripts/...` invocation convention requires each skill's `scripts/` to be self-contained per Anthropic's rule "skill-bundled files live inside the skill folder". Plugin-level shared `scripts/` directory exists at `investing-toolkit/scripts/` but is treated as canonical staging only — not referenced by SKILL.md (which all use `${CLAUDE_SKILL_DIR}` path).

### 2.3 Mixed concerns in current skills

Concrete examples:

- `us-stock-snapshot/SKILL.md` — fetches via yfinance + SEC EDGAR + composes snapshot card → mixes fetch + format
- `investment-memo-writer/SKILL.md` — orchestrates fetch + analysis + delegation → ambiguous if it's a "writer" or an "orchestrator"
- `invest-portfolio/SKILL.md` — parses holdings + fetches prices + computes P&L + overlays regime → 4 concerns in 1 skill
- `dcf-valuation/SKILL.md` — interactive 3-stage DCF model → mostly compute, but description says "auto-sources via us-stock-snapshot" coupling fetch into compute boundary

User feedback (2026-05-01): "我主要的目的還是想分離 資料取得 與 資料分析（以及最終的報告製作）".

---

## 3. Architecture: Way B Three-Layer

### 3.1 Layer definitions (ADR-0001 to be written)

| Layer | Prefix | Responsibility | I/O Rule | Cross-skill calls |
|---|---|---|---|---|
| **Data** | `data-` | Fetch + tier-routing + cache, by country | Pure I/O — fetch only, output structured JSON | Does NOT call other skills |
| **Analysis** | `analysis-` | Compute / score / classify | Pure compute — input JSON, output JSON, no I/O | Does NOT call other skills (exception: `analysis-screener` may dispatch `data-{country}` fetch as pragmatic concession) |
| **Report** | `report-` | Orchestration + formatting | Orchestrates data-* + analysis-* + cross-plugin delegation; produces human-readable Markdown | May call `data-*`, `analysis-*`, and delegate to `domain-teams:investing-team` / `domain-teams:docs-team` |

### 3.2 Cross-skill data passing

No skill-to-skill direct invocation. **Main agent orchestrates** via Bash subprocess + temp files (the same pattern documented for cross-plugin delegation in `CLAUDE.md`):

```bash
# main agent reads report-equity-memo SKILL.md, executes:
uv run skills/data-us/scripts/pack.py --ticker AAPL --pack memo-fetch \
     > /tmp/aapl-data.json
uv run skills/analysis-dcf/scripts/dcf_compute.py --input /tmp/aapl-data.json \
     > /tmp/aapl-dcf.json
uv run skills/analysis-comps/scripts/comps_compute.py \
     --anchor /tmp/aapl-data.json --peers /tmp/peers.json \
     > /tmp/aapl-comps.json
# delegate to domain-teams:investing-team with paths to JSONs
```

Zero sub-agent overhead — main agent is the orchestrator (existing pattern).

### 3.3 Anthropic rule compliance

Each script file lives inside some skill's `scripts/` directory. Cross-skill invocation via Bash is allowed because Anthropic's rule governs **bundled file ownership**, not execution permission. This matches the documented `domain-teams:investing-team` cross-plugin delegation contract: "delegation = pass paths, not file content".

Acceptable script duplication (CI-enforced sync):
- `yfinance_client.py` × 5 (one per `data-{country}`)
- `fred_client.py` × 2 (`data-us`, `data-cn`)
- `ta_client.py` canonical in `analysis-technical/`, copied to other analysis skills using TA

CI MD5 check enforces all copies stay identical.

---

## 4. Final Skill List (15 → 15)

### 4.1 Skill mapping table

| # | New Skill | Layer | Source(s) | Migration |
|---|---|---|---|---|
| 1 | `data-us` | Data | `us-macro` + `us-stock-snapshot` (fetch part) | Merge |
| 2 | `data-jp` | Data | `japan-macro` + `japan-stock-snapshot` (fetch part) | Merge |
| 3 | `data-tw` | Data | `taiwan-macro` + `taiwan-stock-snapshot` (fetch part) | Merge |
| 4 | `data-kr` | Data | `korea-macro` | Rename |
| 5 | `data-cn` | Data | `china-macro` | Rename |
| 6 | `analysis-dcf` | Analysis | `dcf-valuation` | Rename |
| 7 | **`analysis-comps`** | Analysis | — | **NEW** |
| 8 | `analysis-screener` | Analysis | `stock-screener` | Rename (allowed pragmatic exception: dispatches own data-* fetch) |
| 9 | `analysis-technical` | Analysis | `technical-snapshot` | Rename + remove fetch (becomes pure compute) |
| 10 | `analysis-portfolio` | Analysis | `invest-portfolio` (compute part) | Split |
| 11 | `analysis-macro-regime` | Analysis | `macro-regime-snapshot` | Rename |
| 12 | `report-equity-memo` | Report | `investment-memo-writer` | Rename |
| 13 | `report-stock-snapshot` | Report | `us/jp/taiwan-stock-snapshot` (compose part) | 3-into-1 merge with country auto-routing |
| 14 | `report-portfolio-review` | Report | `invest-portfolio` (orchestration part) | Split |
| 15 | `using-investing-toolkit` | Router | same | Update routing table |

### 4.2 Layer 1 — Data skills (5)

Each `data-{country}` skill bundles:
- All clients needed for that country
- A `pack.py` facade with `--pack {snapshot|memo-fetch|comps-multiples|...}` modes that compose multi-source pulls
- Tier-routing logic (e.g. EDINET-key check for JP)

| Skill | Clients | Notes |
|---|---|---|
| `data-us` | yfinance, sec_edgar, fred | SEC EDGAR Tier A primary |
| `data-jp` | yfinance, edinet, tdnet, boj, estat, ecb | EDINET-key tier routing inside pack.py |
| `data-tw` | yfinance, mops, twse_openapi, finmind, cbc, dgbas, ndc, statgov | MOPS + TWSE Tier A; FinMind Tier 2 fallback |
| `data-kr` | yfinance, fdr | FDR via BOK ECOS-KEYSTAT |
| `data-cn` | yfinance, nbs, akshare, fred | NBS new-SPA API |

### 4.3 Layer 2 — Analysis skills (6)

| Skill | Compute | Output |
|---|---|---|
| `analysis-dcf` | 3-stage DCF + 3×3 sensitivity | intrinsic value range JSON |
| `analysis-comps` (**NEW**) | Peer multiples median/mean/quartile + anchor delta | comps table JSON |
| `analysis-screener` | Filter + composite score + ranking | top-N JSON (pragmatic exception: includes data-* fetch dispatch) |
| `analysis-technical` | RSI / MACD / BB / ATR / SMA | indicators JSON (pure compute, no I/O) |
| `analysis-portfolio` | Position P&L + holdings stats | review JSON |
| `analysis-macro-regime` | IC + GIP regime classification | regime card JSON |

### 4.4 Layer 3 — Report skills (3 in v2.0.0)

| Skill | Orchestration | Final Output |
|---|---|---|
| `report-equity-memo` | data → analysis-* → delegate to domain-teams:investing-team → optional docs-team | Full investment memo (Markdown) |
| `report-stock-snapshot` | data-{country} (auto-detect via ticker suffix) → format card | Snapshot card (Markdown) |
| `report-portfolio-review` | data-* (per position) → analysis-portfolio → analysis-macro-regime overlay → format | Portfolio review document (Markdown) |

### 4.5 Future Layer 3 expansion (not v2.0.0)

| Future | Trigger |
|---|---|
| `report-comps-tearsheet` | After memo integration validates Comps; v2.1+ |
| `report-earnings-update` | When earnings analysis lands (DEFERRED, requires consensus data source) |
| `report-screener-list` | If splitting analysis-screener proves valuable |
| `analysis-sector-rollup` | If cross-peer industry comparison demand emerges |
| `analysis-backtest` | Roadmap v2.x |

---

## 5. analysis-comps Specification (v2.0.0)

### 5.1 Scope

**v1.0 = `analysis-comps` only** (pure compute layer). Tearsheet report deferred to v2.1+.

Used by:
- `report-equity-memo` (embedded as Relative Valuation section)
- Future `report-comps-tearsheet` (independent 1-pager) — not in v2.0.0

### 5.2 Inputs

| Parameter | Required | Notes |
|---|---|---|
| `--anchor` | yes | Path to anchor ticker's data JSON (from `data-{country}/pack.py --pack comps-multiples`) |
| `--peers` | yes | Path(s) to peer ticker data JSONs (comma-separated) |
| `--mode` | no | `direct` (use multiples in JSON) / `compute` (recompute from base financials). Default: `direct` |

### 5.3 Multiples set (v2.0.0)

Classic 5:
- Trailing P/E
- Forward P/E
- EV/EBITDA
- P/S (price-to-sales)
- P/B (price-to-book)

Sector-adjusted multiples (banks: P/B + ROE; REITs: P/AFFO; tech: EV/Revenue) **deferred to v2.1+**.

### 5.4 Outputs (JSON schema, draft)

```json
{
  "anchor": {
    "ticker": "AAPL",
    "multiples": {"trailingPE": 28.5, "forwardPE": 25.1, "evEbitda": 21.3, "priceToSales": 7.2, "priceToBook": 35.4}
  },
  "peers": [
    {"ticker": "MSFT", "multiples": {...}, "rationale": "Direct big-tech competitor in cloud / productivity"},
    {"ticker": "GOOGL", "multiples": {...}, "rationale": "..."}
  ],
  "statistics": {
    "trailingPE": {"median": 26.1, "mean": 27.3, "q1": 22.0, "q3": 30.5, "min": 18.5, "max": 35.2},
    "forwardPE": {...},
    "evEbitda": {...},
    "priceToSales": {...},
    "priceToBook": {...}
  },
  "anchor_delta": {
    "trailingPE": {"value": 28.5, "vs_median_pct": 9.2, "percentile": 0.65},
    "forwardPE": {...}
  },
  "ranking": [
    {"ticker": "MSFT", "composite_rank": 1, "trailingPE_rank": 2, ...},
    {"ticker": "AAPL", "composite_rank": 3, ...}
  ],
  "_provenance": {
    "anchor_data_source": "data-us/pack.py --pack comps-multiples",
    "peer_data_sources": [...],
    "computed_at": "2026-05-01T12:00:00Z"
  }
}
```

### 5.5 Peer-discovery (handled UPSTREAM by report layer)

`analysis-comps` itself does NOT discover peers — it consumes pre-fetched peer data. Discovery is the **report layer's** responsibility.

When `report-equity-memo` (or future `report-comps-tearsheet`) runs:

| Mode | Behavior |
|---|---|
| `--peers <list>` | User-provided. Skip discovery. Direct fetch + analyze. |
| `--anchor <ticker>` (no peers) | **Spawn research agent at runtime**. Agent does WebSearch + competitor research. Returns peer list (5–8 tickers) + per-peer rationale + source URLs. |

Default behavior (configurable):

| Context | Discovery flow |
|---|---|
| Standalone CLI usage | **Interactive** — agent finds peers → presents list + rationale → user `/proceed` confirms or edits → analysis runs |
| Pipeline (called from report-equity-memo) | **Auto** — agent finds peers → analysis runs immediately → peer list + rationale visible in process logs and final report |

`--interactive` flag toggles for power users.

### 5.6 Provenance transparency requirement

Peer list + per-peer rationale + source URLs visible at three points:

1. **During execution** — main agent logs `Using peers: X (reason), Y (reason), Z (reason)` before fetch starts
2. **In analysis JSON** — `_provenance.peer_data_sources` lists each peer + how it was selected
3. **In final report** — Comps section header explicitly lists peers + 1-line rationale per peer

The reader never wonders "Comps against whom?"

### 5.7 Research-agent contract

Spawn `general-purpose` agent (or `domain-teams:research-team` quick mode if higher rigor needed). Prompt template:

```
Find 5–8 publicly-traded competitor tickers for {anchor_ticker} ({company_name}).

Selection criteria (in order):
1. Direct business-line competitor (same products/services)
2. Comparable scale tier (market cap within 0.3x–3x range)
3. Same primary geography or comparable geographic mix
4. Listed on major exchanges (US/JP/TW/KR/CN/HK/Europe)

For each peer, provide:
- Ticker symbol (with exchange suffix if non-US: .T, .TW, .KS, etc.)
- 1-line rationale explaining why it's a comp
- Source URL (corporate disclosure, industry report, or competitor analysis)

Output as JSON:
{"peers": [{"ticker": "MSFT", "rationale": "...", "source": "https://..."}]}

Cap: 250 words total. No industry-rollup commentary — just the peer list.
```

---

## 6. Migration Plan

### 6.1 PR strategy (3 PRs)

**PR 1 — Three-layer refactor (v2.0.0-rc.1)**
- Add ADR-0001 (data/analysis/report convention)
- Rename / merge / split 14 existing skills (no new functionality)
- Update `using-investing-toolkit` router
- Add CI MD5 sync check for duplicated clients
- Migration guide in CHANGELOG

**PR 2 — analysis-comps + research-agent peer-discovery (v2.0.0-rc.2)**
- Add `analysis-comps/` skill (pure compute)
- Wire peer-discovery into `report-equity-memo` SKILL.md
- Update `data-{country}/pack.py` to expose `--pack comps-multiples` mode
- Tests + dogfood: AAPL vs FAANG, TSMC vs Intel/Samsung

**PR 3 — Documentation + polish (v2.0.0)**
- Update `using-investing-toolkit` router with new skill names
- Update `docs/design-principles.md` to reference three-layer ADR
- README + i18n updates (en/zh-TW/ja per repo convention)
- Final smoke tests

### 6.2 Parallel agent execution (per user request)

Where work is independent, dispatch agents in parallel:

**PR 1 parallel batches:**

```
Batch A (5 agents in parallel) — Data skill creation:
  - data-us (merge us-macro + us-stock-snapshot fetch)
  - data-jp (merge japan-macro + japan-stock-snapshot fetch)
  - data-tw (merge taiwan-macro + taiwan-stock-snapshot fetch)
  - data-kr (rename from korea-macro)
  - data-cn (rename from china-macro)

Batch B (6 agents in parallel) — Analysis skill creation/rename:
  - analysis-dcf (rename + decouple from snapshot)
  - analysis-screener (rename, retain fetch dispatch as exception)
  - analysis-technical (rename + remove fetch)
  - analysis-portfolio (extract compute from invest-portfolio)
  - analysis-macro-regime (rename)
  - (analysis-comps deferred to PR 2)

Batch C (3 agents sequential after A+B) — Report skill creation:
  - report-equity-memo (rename, update orchestration)
  - report-stock-snapshot (3-into-1 merge with country routing)
  - report-portfolio-review (extract orchestration from invest-portfolio)

Batch D (1 agent, parallel with all) — Convention/docs:
  - ADR-0001 + CI sync check + router update
```

Total: ~10 agents in parallel for the bulk work.

**PR 2 parallel batches:**

```
Batch A (2 agents in parallel):
  - analysis-comps SKILL.md + comps_compute.py
  - data-{country}/pack.py --pack comps-multiples mode (5 packs in parallel sub-agents)

Batch B (1 agent after A) — integration:
  - report-equity-memo SKILL.md update for peer-discovery + Comps section
```

### 6.3 Backward compatibility

**Breaking** — slash commands change:
- `/macro-us` → `/data-us-fetch` (or similar; finalized in PR 1)
- `/dcf` → `/analysis-dcf` (or similar)
- `/memo` → `/report-equity-memo`

CHANGELOG provides full rename map. No alias shim (would defeat purpose of clean rename).

Version bump: **v1.16.4 → v2.0.0** (major, due to skill rename = breaking).

---

## 7. Open Questions / Future Work

### Deferred

- **Sector-adjusted multiples** (Banks P/B+ROE; REITs P/AFFO; Tech EV/Revenue+Rule-of-40) — v2.1+
- **`report-comps-tearsheet`** independent 1-pager — v2.1+ once memo embedding validates
- **Earnings Analysis** — needs free consensus data source (Estimize public API verification, etc.) or accumulated user demand
- **3-statement model** — DROPPED (sell-side artifact, philosophy mismatch)
- **DCF extended projection inputs** (revenue/margin/capex paths) — separate v2.x enhancement

### Verifications needed during implementation

- Confirm `${CLAUDE_SKILL_DIR}` resolves correctly in renamed/merged skills
- Confirm MCP tool registrations don't break with skill renames (mcp.json paths)
- Confirm Cowork sandbox URL allowlist still works (per `docs/mcp-setup.md`)
- Validate `pack.py` facade can compose multi-client pulls without timeout (especially `data-tw` with 8 sources)

### Risks

- **Slash command rename** breaks user muscle memory and any external scripts. Mitigate via prominent CHANGELOG + announcement.
- **MCP tool registration** may need updates per skill rename. Audit mcp.json before merge.
- **research-agent peer-discovery** non-determinism — different runs = different peers. Mitigate via provenance transparency (always show peer list + rationale) and `--peers` override.

---

## 8. Acceptance Criteria

For v2.0.0 release:

- [ ] 15 skills present (5 data + 6 analysis + 3 report + 1 router)
- [ ] All 15 SKILL.md files use `${CLAUDE_SKILL_DIR}/scripts/` convention
- [ ] CI MD5 sync check passing for all duplicated clients (yfinance × 5, fred × 2, ta × N)
- [ ] ADR-0001 committed to `docs/adr/`
- [ ] `analysis-comps` produces structured JSON for AAPL vs MSFT/GOOGL/META/AMZN dogfood case
- [ ] `report-equity-memo` end-to-end run for AAPL succeeds with peer-discovery agent
- [ ] All existing memo dogfood tickers still produce valid memos (regression check)
- [ ] `using-investing-toolkit` router updated; routes correctly to new skill names
- [ ] README + zh-TW + ja translations updated per repo convention
