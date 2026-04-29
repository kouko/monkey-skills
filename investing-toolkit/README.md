# investing-toolkit

> Read this in: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Cross-country investing data plugin for Claude Code — five-market macro coverage (US/JP/TW/KR/CN), individual stock snapshots, DCF and screening workflows, and a delegating memo pipeline that hands analysis off to `domain-teams:investing-team`.

## Cowork compatibility

⚠️ **Claude Code CLI only.** Claude Desktop Cowork's sandbox URL allowlist blocks both subprocess and plugin-installed MCP HTTP requests, so external data fetches (yfinance, FRED, NBS, EDINET, etc.) cannot reach their providers from inside Cowork. Empirically confirmed in v1.16.1 — see [`docs/mcp-setup.md`](docs/mcp-setup.md) for the retrospective and the "what works where" matrix.

## Version and part-of

- Version: 1.16.5
- Part of: [`monkey-skills`](https://github.com/kouko/monkey-skills) plugin marketplace
- License: MIT

## Background

investing-toolkit is the **data layer** for cross-country investing research. It fetches primary-source macro and equity data from 14+ public providers, computes mechanical aggregates (regime calls, screens, DCF, P&L), and hands structured fixtures to `domain-teams:investing-team` for the actual analysis, gate enforcement, and BUY/HOLD/SELL verdicts. The plugin keeps `data ↔ analysis` strictly separated — toolkit code never embeds investment judgement, and domain-team code never reaches out to data sources directly. See the [Cross-Plugin Delegation Contract](#cross-plugin-delegation) below.

## Monthly GDP proxy framework

All five country macros expose a consistent **monthly GDP proxy** so cross-market regime calls can compare like-for-like. Most major economies publish official GDP only quarterly — the proxy framework fills the monthly gap with the canonical pre-aggregated series each statistical authority already publishes.

| Market | Proxy type | Indicators |
|--------|-----------|------------|
| US | Pre-aggregated Fed nowcasts | `nowcast` group: GDPNow, CFNAI, WEI, OECD CLI |
| JP | Pre-aggregated 内閣府 composite | 景気動向指数 CI trio: 一致 (proxy), 先行, 遅行 |
| TW | Pre-aggregated NDC + DGBAS | `signal` (五色景氣燈號 — Taiwan-only), 領先指標, 同時指標 |
| KR | Pre-aggregated BOK ECOS | 동행지수순환변동치 (proxy) + 선행지수순환변동치 |
| CN | Raw components (no consensus aggregator) | 三大数据: industrial-yoy, retail-yoy, fai-yoy + services-production-yoy |

US/JP/TW/KR ship **pre-aggregated** values from the relevant statistical authority. CN keeps components raw — no market-consensus monthly composite exists (Li Keqiang Index is obsolete post-2012; SF Fed CAT is quarterly; Goldman / Bloomberg are proprietary), so synthesis lives in the analysis layer where methodology choice has accountability.

For sector-level (industry) cadence detail, see [`docs/industry-indicator-cadence.md`](docs/industry-indicator-cadence.md).

## Slash commands

| Command | Routes to | Description |
|---------|-----------|-------------|
| `/invest` | `using-investing-toolkit` | Router — describe your goal, get dispatched |
| `/invest-macro` | `macro-regime-snapshot` | 5-block regime dashboard (`--region us|japan|taiwan|korea|china|global|asia-pac|all|<comma-list>`) |
| `/invest-memo {ticker}` | `investment-memo-writer` | Full memo pipeline → `domain-teams:investing-team` |
| `/invest-screen {tickers}` | `stock-screener` | Multi-criteria screen with composite ranking |
| `/invest-portfolio` | `invest-portfolio` | P&L snapshot + regime overlay + rebalance |

## Skills

15 skills, organised in three layers + a router.

### Data layer

| Skill | Description |
|-------|-------------|
| `us-macro` | FRED CSV — 31 series across 14 groups (rates / inflation / growth / nowcast / real-rates / pmi / swap-spreads + 7 sector groups mapped to ETFs) |
| `japan-macro` | BOJ + 統計ダッシュボード + ECB SDMX + MoF JGBi auction snapshot — 27 presets, 10 groups including `real-rates` C+D+E multi-source |
| `taiwan-macro` | stat.gov.tw + CBC + DGBAS + NDC — 32 indicators including 五色景氣燈號 + CIER PMI/NMI |
| `korea-macro` | FinanceDataReader BOK ECOS-KEYSTAT — 54 indicators / 13 groups including monthly industry activity layer |
| `china-macro` | NBS new-SPA API + PBOC/Caixin via akshare + FRED + yfinance — 36 indicators including Caixin + NBS PMI dual-source |
| `us-stock-snapshot` | yfinance price/valuation + SEC EDGAR 10-K/10-Q/8-K + XBRL facts + Item-section narrative |
| `taiwan-stock-snapshot` | MOPS JSON + TWSE/TPEx OpenAPI Tier A primary, FinMind Tier 2 fallback (三大法人 / 月營收 / 融資融券 / 董監持股 / 重大訊息) |
| `japan-stock-snapshot` | EDINET v2 + TDnet (Yanoshin) + yfinance `.T` — dual-mode (Tier A with `EDINET_API_KEY`, Tier 2 yfinance financials without) |
| `technical-snapshot` | RSI-14 / MACD-12-26-9 / Bollinger-20 / ATR-14 / SMA-20-50-200 from OHLCV |

### Aggregation layer

| Skill | Description |
|-------|-------------|
| `macro-regime-snapshot` | 5-country IC + Hedgeye GIP regime call + Rate Stress Dashboard (real rate + swap spread); 5×9 cross-country coverage grid |
| `stock-screener` | Composite-score screener over user-supplied ticker list (8 presets: value / deep-value / quality / high-dividend / growth / growth-value / momentum / balanced) |
| `dcf-valuation` | 3-stage DCF (Damodaran 2012 Ch.12) + 3×3 sensitivity table + Graham/Klarman verdict |
| `invest-portfolio` | Holdings parser + batch price fetch + macro overlay + position P&L |

### Delegation layer

| Skill | Description |
|-------|-------------|
| `investment-memo-writer` | Full memo pipeline: data-fetcher agent → macro-regime-snapshot → `domain-teams:investing-team` (Deep Equity Research Memo + 2 MUST + 4 SHOULD + 1 MAY gates) → optional `domain-teams:docs-team` |

### Router

| Skill | Description |
|-------|-------------|
| `using-investing-toolkit` | Entry point — intent routing for the 14 skills above |

## Architecture

```
slash command           skill                       agent / delegate           data source
─────────────           ─────                       ────────────────           ───────────
/invest-memo NVDA   →   investment-memo-writer  →   data-fetcher (haiku)   →   yfinance, FRED, ...
                                                ↘   macro-regime-snapshot
                                                ↘   domain-teams:investing-team   (analysis + gates)
                                                ↘   domain-teams:docs-team        (optional)
```

Single source of truth for adapters lives in [`scripts/`](scripts/). Each `*_client.py` is callable three ways: as a `uv run` subprocess from any skill, as an MCP tool registered in [`servers/mcp_server.py`](servers/mcp_server.py) (29 tools across 18 clients), or directly as a Python module. Both subprocess and MCP paths return byte-identical JSON; a CI guard (`tests/test_mcp_equivalence_auto.py`) keeps them in lockstep.

Skill-local copies under `skills/*/scripts/` are kept in sync from the canonical `scripts/` via [`sync-scripts.sh`](scripts/sync-scripts.sh) and verified by [`sync-check.sh`](scripts/sync-check.sh) in CI.

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

Adapters in [`scripts/`](scripts/) — primary-source where available, free-tier only.

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

investing-toolkit is the data layer; analysis lives in `domain-teams:investing-team`. Delegation passes paths and structured seed context — never file contents — and lets the target skill enforce its own gates.

```
investing-toolkit                    domain-teams:investing-team
  investment-memo-writer    ───→     Deep Equity Research Memo protocol
                                       2 MUST gates
                                       4 SHOULD gates
                                       1 MAY gate (Taiwan Local Rigor)
                                     verdict: BUY / HOLD / SELL  ───→ back to caller
                                       ↓ (optional)
                                     domain-teams:docs-team
                                       polished formatting
```

The contract is documented at [`monkey-skills/CLAUDE.md`](../CLAUDE.md) §Cross-Plugin Delegation Contract. Toolkit skills do not duplicate `investing-team` standards, do not run gate logic locally, and pass path references rather than file content. The `data-fetcher` agent is I/O only and never analyses.

## Cross-country reference docs

- [`docs/design-principles.md`](docs/design-principles.md) — empirical-first design rule (lessons from v1.14.0 + v1.16.3 hypothesis-vs-reality misses)
- [`docs/industry-indicator-cadence.md`](docs/industry-indicator-cadence.md) — sector coverage + release cadence comparison across 5 markets
- [`docs/mcp-setup.md`](docs/mcp-setup.md) — install, troubleshooting, Cowork sandbox retrospective, MCP vs subprocess token/latency trade-off
- Per-country deep references inside each skill: `skills/{country}-macro/references/`, `skills/{country}-macro/docs/` (BOK ECOS catalogue, NBS 2908-leaf tree, JGBi auction history, etc.)

## Version history

See [`ROADMAP.md`](ROADMAP.md) for full version history (v1.0.0 → v1.16.5) and roadmap toward v2.0.0 (backtesting + factor models). Recent releases: v1.16.5 (Phase 3 retarget to investing-team), v1.16.4 (TWSE `/rwd/` wiring + design-principles doc), v1.16.3 (empirical yfinance validation).

## Contributing

- Bug reports and PRs: [github.com/kouko/monkey-skills/issues](https://github.com/kouko/monkey-skills/issues)
- For Cowork-related issues, please check [`docs/mcp-setup.md`](docs/mcp-setup.md) first — it is almost certainly the documented sandbox limitation, not a plugin bug
- New data adapter PRs welcome; please follow the existing `*_client.py` pattern (`register_mcp_tools()` + subprocess CLI + cache TTL header) and add a contract test fixture

## License

MIT — see [LICENSE](../LICENSE) at the repository root.
