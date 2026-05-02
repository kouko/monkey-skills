# investing-toolkit

> Read this in: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Cross-country investing plugin for Claude Code — three-layer architecture (Data / Analysis / Report) across 5 markets (US/JP/TW/KR/CN). 16 skills enforce strict separation: country-bundled `data-*` skills do pure I/O, `analysis-*` skills do pure compute, `report-*` skills orchestrate and delegate analysis to `domain-teams:investing-team`.

## Cowork compatibility

⚠️ **Claude Code CLI only.** Claude Desktop Cowork's sandbox URL allowlist blocks both subprocess and plugin-installed MCP HTTP requests, so external data fetches (yfinance, FRED, NBS, EDINET, etc.) cannot reach their providers from inside Cowork. Empirically confirmed in v1.16.1 — see [`docs/mcp-setup.md`](docs/mcp-setup.md) for the retrospective and the "what works where" matrix.

## Version and part-of

- Version: 2.0.0
- Part of: [`monkey-skills`](https://github.com/kouko/monkey-skills) plugin marketplace
- License: MIT

## Migrating from v1.x?

v2.0.0 is a breaking change: every skill was renamed under the three-layer prefix convention (`data-*` / `analysis-*` / `report-*`) and slash commands moved with them. There is **no alias shim**. See [`docs/migration-v2.0.0.md`](docs/migration-v2.0.0.md) for the full v1.x → v2.0.0 rename map and migration walkthrough, and [`docs/adr/0001-data-analysis-report-layers.md`](docs/adr/0001-data-analysis-report-layers.md) for the architectural decision record.

## Background

investing-toolkit is the **toolkit layer** for cross-country investing research. It owns three concerns — fetching primary-source data, computing mechanical aggregates, and orchestrating delivery — and keeps each in its own layer. The toolkit never embeds investment judgement: BUY/HOLD/SELL verdicts, gate enforcement, and primary-source anchoring all live in `domain-teams:investing-team`, which `report-equity-memo` delegates to. See the [Cross-Plugin Delegation Contract](#cross-plugin-delegation) below.

## Architecture: three-layer + router

```
┌─ Layer 1: Data (5 skills, country-bundled, pure I/O) ────┐
│  data-us  data-jp  data-tw  data-kr  data-cn             │
└──────────────────────────────────────────────────────────┘
        ↓ pack.py outputs JSON (5 pack types: snapshot /
        ↓ memo-fetch / comps-multiples / screener-batch /
        ↓ regime-pack)
┌─ Layer 2: Analysis (6 skills, pure compute) ─────────────┐
│  analysis-dcf       analysis-comps     analysis-screener │
│  analysis-technical analysis-portfolio analysis-macro-regime │
└──────────────────────────────────────────────────────────┘
        ↓ compute scripts output analysis JSON
┌─ Layer 3: Report (4 skills, orchestrators) ──────────────┐
│  report-equity-memo       report-stock-snapshot          │
│  report-portfolio-review  report-screener-list           │
└──────────────────────────────────────────────────────────┘
        ↓ Markdown output

Router: using-investing-toolkit
```

**Layer rules** (ADR-0001):

| Layer | Owns | Forbidden | Cross-skill calls |
|-------|------|-----------|-------------------|
| Data (`data-*`) | Network I/O, tier routing, cache, single + batch fetch (`pack.py --ticker` / `--tickers`). 1 skill = 1 country = all clients for that country. | Computing indicators, formatting Markdown | none |
| Analysis (`analysis-*`) | Pure functions: input JSON → output JSON. RSI/MACD/BB compute, DCF iteration, comps multiples, screener filter+score+rank, portfolio P&L, regime classification. | Network I/O, sub-agent dispatch — **zero exceptions** | none |
| Report (`report-*`) | Orchestration via Bash + temp file (`data-X/scripts/pack.py > /tmp/data.json` then `analysis-Y/scripts/compute.py --in /tmp/data.json`), country routing by ticker suffix, Markdown formatting. May delegate to `domain-teams:investing-team` / `domain-teams:docs-team`. | Re-implementing a multiple, hand-rolling RSI inline, calling yfinance directly | yes (cross-plugin) |

Layer-to-layer hand-off uses subprocess + temp file — deterministic, observable, replayable. Sub-agent dispatch is reserved for autonomy-required work like the `domain-teams:investing-team` Worker / Evaluator agents.

## Slash commands

| Command | Routes to | Description |
|---------|-----------|-------------|
| `/invest` | `using-investing-toolkit` | Router — describe your goal, get dispatched |
| `/invest-macro` | `analysis-macro-regime` | 5-block regime dashboard (`--region us|japan|taiwan|korea|china|global|asia-pac|all|<comma-list>`) |
| `/invest-memo {ticker}` | `report-equity-memo` | Full memo pipeline → `domain-teams:investing-team` |
| `/invest-screen {tickers}` | `report-screener-list` | Cross-country grouped screen with composite ranking |
| `/invest-portfolio` | `report-portfolio-review` | P&L snapshot + regime overlay + rebalance |
| `/invest-snapshot {ticker}` | `report-stock-snapshot` | Snapshot card; auto-routes by ticker suffix to `data-{country}` |

## Skill catalog (16)

### Layer 1: Data (5 skills)

Each `data-{country}/scripts/pack.py` exposes 5 pack modes — `snapshot` / `memo-fetch` / `comps-multiples` / `screener-batch` / `regime-pack` — and supports both `--ticker` (single) and `--tickers` (batch) modes.

| Skill | Clients bundled | Notes |
|-------|----------------|-------|
| `data-us` | yfinance, sec_edgar, fred | SEC EDGAR Tier A primary; yfinance batch native |
| `data-jp` | yfinance, edinet, tdnet, boj, estat, ecb | EDINET-key tier routing inside `pack.py` |
| `data-tw` | yfinance, mops, twse_openapi, finmind, cbc, dgbas, ndc, statgov | MOPS + TWSE Tier A; FinMind Tier 2 fallback |
| `data-kr` | yfinance, fdr | FDR via BOK ECOS-KEYSTAT |
| `data-cn` | yfinance, nbs, akshare, fred | NBS new-SPA API |

### Layer 2: Analysis (6 skills, pure compute)

| Skill | Compute | Output |
|-------|---------|--------|
| `analysis-dcf` | 3-stage DCF (Damodaran 2012 Ch.12) + 3×3 sensitivity | Intrinsic value range JSON |
| `analysis-comps` | Peer multiples median/mean/quartile + anchor delta (Trailing P/E, Forward P/E, EV/EBITDA, P/S, P/B) | Comps table JSON |
| `analysis-screener` | Filter + composite score + ranking (8 presets: value / deep-value / quality / high-dividend / growth / growth-value / momentum / balanced) | Top-N JSON |
| `analysis-technical` | RSI-14 / MACD-12-26-9 / Bollinger-20 / ATR-14 / SMA-20-50-200 from OHLCV | Indicators JSON |
| `analysis-portfolio` | Position P&L + holdings statistics | Review JSON |
| `analysis-macro-regime` | 5-country IC + Hedgeye GIP regime call + Rate Stress Dashboard | Regime card JSON |

### Layer 3: Report (4 skills, orchestrators)

| Skill | Orchestration | Final output |
|-------|---------------|--------------|
| `report-equity-memo` | data → analysis-* → delegate to `domain-teams:investing-team` (Deep Equity Research Memo + 2 MUST + 4 SHOULD + 1 MAY gates) → optional `domain-teams:docs-team` | Investment memo (Markdown) |
| `report-stock-snapshot` | Auto-detects country via ticker suffix → `data-{country}/pack.py --pack snapshot` → format card | Snapshot card (Markdown) |
| `report-portfolio-review` | Per position → batch `data-{country}` per country → `analysis-portfolio` → `analysis-macro-regime` overlay → format | Portfolio review (Markdown) |
| `report-screener-list` | Parse list → group by country → parallel `data-{country} --pack screener-batch` → concatenate → `analysis-screener` → format top-N | Screener result table (Markdown) |

### Router

| Skill | Description |
|-------|-------------|
| `using-investing-toolkit` | Entry point — intent routing for the 15 skills above |

## Quick start examples

```bash
# Equity memo for AAPL — orchestrates data-us → analysis-dcf + analysis-comps + analysis-technical → investing-team
/invest-memo AAPL

# Cross-country screener over a mixed list
/invest-screen AAPL,MSFT,2330.TW,7203.T --preset quality

# Snapshot card; ticker suffix auto-routes to data-tw
/invest-snapshot 2330.TW

# Macro regime dashboard for Asia-Pac
/invest-macro --region asia-pac

# Portfolio review (CSV path or inline list)
/invest-portfolio --holdings my-holdings.csv
```

## Setup

The plugin self-bootstraps on first install. Manual setup is rarely needed.

```bash
# Inside Claude Code CLI
/plugin marketplace add kouko/monkey-skills
/plugin install investing-toolkit
```

On first launch, the MCP bootstrap (`servers/mcp_bootstrap.sh`) detaches `setup.sh` to install [`uv`](https://docs.astral.sh/uv/) (preferring Homebrew, falling back to Astral's installer) and pre-warm the Python 3.11 + ~66-wheel cache. Quit and reopen once `~/.cache/investing-toolkit/.mcp_ready` exists.

Optional API keys (set in shell env or `~/.claude.json`):

| Variable | Required for | How to get |
|----------|-------------|------------|
| `FRED_API_KEY` | Higher US rate limits (anonymous works) | [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html) |
| `FINMIND_API_TOKEN` | Higher Taiwan rate limits (anonymous works) | [finmindtrade.com](https://finmindtrade.com/) |
| `EDINET_API_KEY` | JP Tier A fundamentals (yfinance financials Tier 2 fallback works without) | [disclosure2dl.edinet-fsa.go.jp](https://disclosure2dl.edinet-fsa.go.jp/) — free 5-min self-service |

Full troubleshooting and the Cowork retrospective: [`docs/mcp-setup.md`](docs/mcp-setup.md).

## Data sources

Adapters live in [`scripts/`](scripts/) as the **canonical home**. Each `data-{country}/scripts/` folder receives MD5-locked copies; CI fails any drift. See [`scripts/README.md`](scripts/README.md) and [`docs/adr/0001-data-analysis-report-layers.md`](docs/adr/0001-data-analysis-report-layers.md) §Acceptable Duplications.

| Region | Adapter | Source |
|--------|---------|--------|
| Cross-market | `yfinance_client.py` | Yahoo Finance (price + info + financials, unofficial scraper) |
| Cross-market | `ta_client.py` | Local OHLCV → indicators (no external API) |
| US | `fred_client.py` | Federal Reserve Economic Data (FRED) CSV |
| US | `sec_edgar_client.py` | SEC EDGAR (`data.sec.gov`) |
| JP | `boj_client.py` | Bank of Japan Time-Series Statistics + Tankan |
| JP | `estat_client.py` | e-Stat 統計ダッシュボード API |
| JP | `edinet_client.py` | 金融庁 EDINET v2 REST API |
| JP | `tdnet_client.py` | TDnet via Yanoshin WEB-API |
| JP / EU | `ecb_client.py` | ECB Data Portal SDMX |
| TW | `mops_client.py` | MOPS 公開資訊觀測站 JSON API (16 endpoints) |
| TW | `twse_openapi_client.py` | TWSE + TPEx OpenAPI (10+ actions) |
| TW | `finmind_client.py` | FinMind aggregator (Tier 2 / T86 fill) |
| TW | `statgov_client.py` | stat.gov.tw National Statistics chart JSON |
| TW | `cbc_client.py` | Central Bank of the Republic of China Open Data |
| TW | `dgbas_client.py` | 主計總處 (DGBAS) Excel |
| TW | `ndc_client.py` | 國發會 (NDC) ZIP/CSV + 政府資料開放 dataset 6100 |
| KR | `fdr_client.py` | FinanceDataReader → BOK ECOS-KEYSTAT |
| CN | `nbs_client.py` | 國家統計局 (NBS) new-SPA API |
| CN | `akshare_client.py` | akshare (PBOC / SHIBOR / Caixin via eastmoney) |

## Cross-plugin delegation

investing-toolkit owns data fetch + mechanical compute + orchestration. Investment **analysis** lives in `domain-teams:investing-team`. The bridge is `report-equity-memo` — it gathers JSON outputs from Layer 1 + Layer 2 and delegates to `investing-team`, passing **paths** (not file content) and structured seed context. The target skill enforces its own gates.

```
investing-toolkit                              domain-teams:investing-team
  report-equity-memo                ───→       Deep Equity Research Memo protocol
    Layer 1: data-{country}/pack.py              2 MUST gates
    Layer 2: analysis-dcf + analysis-comps       4 SHOULD gates
             + analysis-technical                1 MAY gate (Taiwan Local Rigor)
                                               verdict: BUY / HOLD / SELL  ───→ back to caller
                                                 ↓ (optional)
                                               domain-teams:docs-team
                                                 polished formatting
```

The contract is documented at [`monkey-skills/CLAUDE.md`](../CLAUDE.md) §Cross-Plugin Delegation Contract. Toolkit skills do not duplicate `investing-team` standards, do not run gate logic locally, and pass path references rather than file content.

## Cross-country reference docs

- [`docs/adr/0001-data-analysis-report-layers.md`](docs/adr/0001-data-analysis-report-layers.md) — three-layer architecture decision record
- [`docs/adr/0002-layer-1-staging-tier-normalization.md`](docs/adr/0002-layer-1-staging-tier-normalization.md) — Layer 1 staging-tier normalization decision (raw + canonical view; addresses 4 broken cross-layer chains found post-v2.0.1)
- [`docs/adr/0003-t3-financial-statement-normalization.md`](docs/adr/0003-t3-financial-statement-normalization.md) — Tier 3 financial statement normalization (per-concept fetch + transform; per-country mapping table)
- [`docs/normalization-contract.md`](docs/normalization-contract.md) — **developer-facing contract** for Layer 1 normalization (must follow when extending `data-*/scripts/pack.py`)
- [`docs/migration-v2.0.0.md`](docs/migration-v2.0.0.md) — v1.x → v2.0.0 rename map and migration walkthrough
- [`docs/design-principles.md`](docs/design-principles.md) — empirical-first design rule (lessons from v1.14.0 + v1.16.3 hypothesis-vs-reality misses)
- [`docs/industry-indicator-cadence.md`](docs/industry-indicator-cadence.md) — sector coverage + release cadence comparison across 5 markets
- [`docs/mcp-setup.md`](docs/mcp-setup.md) — install, troubleshooting, Cowork sandbox retrospective, MCP vs subprocess token/latency trade-off

## Version history

See [`ROADMAP.md`](ROADMAP.md) for full version history (v1.0.0 → v2.1.0). Recent: v2.1.0 (`analysis-macro-regime` Phase 1 per-country classifiers per [ADR-0004](docs/adr/0004-analysis-macro-regime-phase1-per-country-classifiers.md)), v2.0.0 (three-layer refactor + `analysis-comps`), v1.16.5 (Phase 3 retarget to investing-team).

## Contributing

- Bug reports and PRs: [github.com/kouko/monkey-skills/issues](https://github.com/kouko/monkey-skills/issues)
- For Cowork-related issues, please check [`docs/mcp-setup.md`](docs/mcp-setup.md) first — it is almost certainly the documented sandbox limitation, not a plugin bug
- New data adapter PRs welcome; please follow the existing `*_client.py` pattern (`register_mcp_tools()` + subprocess CLI + cache TTL header) and add a contract test fixture. Place the adapter in `scripts/` (canonical) and add the consuming `data-{country}` skill to `scripts/sync-clients.sh`

## License

MIT — see [LICENSE](../LICENSE) at the repository root.
