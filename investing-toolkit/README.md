# investing-toolkit

**Version**: 1.15.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

Investing research toolkit — **5-country macro data** (US / JP / TW / KR / CN),
stock snapshots (US / TW / JP), technical indicators, DCF valuation, stock screener,
portfolio review, and full investment memo pipeline via
`domain-teams:investing-team`.

Data-only layer: this toolkit fetches and structures data. Analysis, regime
judgement, quality-gated memos happen in `domain-teams:investing-team`.

## Monthly GDP Proxy Framework

As of v1.7.3, all five country-macro skills share a consistent monthly
GDP proxy convention:

| Market | Proxy type | Indicators |
|--------|-----------|------------|
| US | Pre-aggregated Fed nowcasts | `nowcast` group: `GDPNOW`, `CFNAI`, `WEI`, `USALOLITOAASTSAM` (OECD CLI) |
| JP | Pre-aggregated 内閣府 composite | 景気動向指数 CI trio: `coincident-index` (the proxy), `leading-index`, `lagging-index` |
| TW | Pre-aggregated NDC + DGBAS | `signal` (五色景氣燈號 — Taiwan 特色), `leading-index`, `coincident-index` |
| KR | Pre-aggregated BOK ECOS | `cycle` group: `coincident-cycle` K253 (the proxy), `leading-cycle` K254 (lagging not in KEYSTAT) |
| CN | Raw components (no consensus composite) | 三大数据: `industrial-yoy`, `retail-yoy`, `fai-yoy` + `services-production-yoy` |

US / JP / TW / KR all serve **pre-aggregated** values from the respective
statistical authorities (Fed / 内閣府 / NDC+DGBAS / BOK ECOS). China keeps
components raw because no market consensus exists on a synthesized
composite (Li Keqiang Index is obsolete, SF Fed CAT is quarterly,
Goldman / Bloomberg are proprietary). Composite synthesis belongs in
`domain-teams:investing-team` where methodology choice has analytical
accountability.

## Slash Commands

| Command | What it does | Status |
|---------|-------------|--------|
| `/invest` | Route to the right skill | v1.0.0 |
| `/invest-macro [--region us\|japan\|global]` | IC + FRED/BOJ regime call | v1.0.0 |
| `/invest-memo {ticker} [--scope deep\|quick]` | Full memo pipeline → investing-team | v1.0.0 |
| `/invest-screen {tickers} [--pe-max N] [--above-sma200]` | Batch screener + composite rank | v1.2.0 |
| `/invest-portfolio [holdings.csv]` | Portfolio review + rebalance | v1.2.0 |

## Skills

Skills are organised in three layers (mirroring `using-investing-toolkit`
router):

- **data** — fetch raw time-series from external sources, no analysis
- **aggregation** — combine / score / transform data into a single-purpose output
- **delegation** — bridge to `domain-teams:investing-team` for full research

| Skill | Layer | Purpose | Status |
|-------|-------|---------|--------|
| `us-macro` | data | US macro via FRED (~31 series, 14 groups incl. new `pmi` [OECD CLI] + new `swap-spreads` [T-SOFR 3M]) | v1.10.0 |
| `japan-macro` | data | Japan macro via BOJ + e-Stat + ECB + MoF auction (27 presets / 10 groups incl. new `real-rates` group, C+D+E multi-source) | v1.10.0 |
| `taiwan-macro` | data | Taiwan macro via stat.gov.tw + CBC + DGBAS + NDC (32 indicators incl. new `pmi` group — CIER PMI/NMI via NDC 政府資料開放 dataset 6100) | v1.11.0 |
| `korea-macro` | data | Korea macro via FinanceDataReader BOK ECOS-KEYSTAT (**54 indicators, 13 groups** incl. monthly `industry` activity layer; full 98-code catalogue in `docs/`) | v1.8.1 |
| `china-macro` | data | China macro via NBS new-SPA API + PBOC + FRED + yfinance (36 indicators incl. new `pmi` group — Caixin mfg/svc via akshare + NBS mfg/non-mfg/composite via nbs_client; primary-source preferred) | v1.11.0 |
| `us-stock-snapshot` | data | yfinance price + info + **SEC EDGAR Tier A fundamentals** (XBRL + Item sections) | v1.13.0 |
| `taiwan-stock-snapshot` | data | **MOPS + TWSE/TPEx OpenAPI Tier A primary** (公司揭露 + 交易); FinMind Tier 2 fallback | v1.13.0 |
| `japan-stock-snapshot` | data | **EDINET v2 Tier A fundamentals** (有報/四半期/臨時/大量保有) + TDnet same-day index + yfinance Tier 2 fallback — dual-mode routing by `EDINET_API_KEY` | v1.15.0 |
| `technical-snapshot` | data | RSI / MACD / Bollinger / ATR / SMA via `ta_client.py` | v1.2.0 |
| `macro-regime-snapshot` | aggregation | 5-country IC + GIP (US/JP/TW/KR/CN) + Rate Stress Dashboard + v1.11.0 cross-country consistency refresh (Block 1 PMI 3/5 live; 5×9 coverage grid; 2026-Q2 grounding) | v1.11.0 |
| `stock-screener` | aggregation | Batch screener — valuation + momentum + trend composite score | v1.2.0 |
| `dcf-valuation` | aggregation | 3-stage DCF + sensitivity table | v1.0.0 |
| `invest-portfolio` | aggregation | Portfolio review — P&L + regime overlay + rebalance | v1.2.0 |
| `investment-memo-writer` | delegation | Full memo pipeline — delegates to `domain-teams:investing-team` | v1.0.0 |
| `using-investing-toolkit` | router | Entry-point skill for routing | v1.0.0 |

## Architecture

```
investing-toolkit/
├── README.md
├── ROADMAP.md
├── scripts/                        # Source of truth (edit here only)
│   ├── yfinance_client.py          #   US + global equity snapshots
│   ├── fred_client.py              #   US macro + China FX fallbacks
│   ├── finmind_client.py           #   Taiwan stocks (FinMind)
│   ├── ta_client.py                #   Technical indicators
│   ├── boj_client.py               #   Japan macro (BOJ Time-Series)
│   ├── estat_client.py             #   Japan macro (統計ダッシュボード)
│   ├── statgov_client.py           #   Taiwan macro (stat.gov.tw)
│   ├── cbc_client.py               #   Taiwan (CBC Open Data API)
│   ├── dgbas_client.py             #   Taiwan (DGBAS Excel)
│   ├── ndc_client.py               #   Taiwan (NDC CSV)
│   ├── fdr_client.py               #   Korea (FinanceDataReader BOK ECOS)
│   ├── nbs_client.py               #   China (NBS new-SPA API, direct)
│   ├── akshare_client.py           #   China (PBOC + SHIBOR via akshare)
│   ├── sync-scripts.sh             #   Copy source → skill dirs
│   └── sync-check.sh               #   CI: verify copies match
├── agents/data-fetcher.md          # Shared I/O agent spec
├── skills/
│   ├── us-macro/                   # data layer
│   ├── japan-macro/
│   ├── taiwan-macro/
│   ├── korea-macro/
│   ├── china-macro/
│   ├── us-stock-snapshot/
│   ├── taiwan-stock-snapshot/
│   ├── technical-snapshot/
│   ├── macro-regime-snapshot/      # aggregation layer
│   ├── stock-screener/
│   ├── dcf-valuation/
│   ├── invest-portfolio/
│   ├── investment-memo-writer/     # delegation layer
│   │   └──→ domain-teams:investing-team (analysis + quality gates + ISQ)
│   │   └──→ domain-teams:docs-team (formatting, optional)
│   └── using-investing-toolkit/    # router
└── commands/                       # /invest-* slash commands
```

Each skill is **self-contained** with its own `scripts/` and `references/`.
The plugin-level `scripts/` directory is the single source of truth —
run `sync-scripts.sh` after editing, `sync-check.sh` to verify.

## Setup

```bash
# Step 1 — install uv (Homebrew first, curl fallback, skip if already installed)
sh investing-toolkit/scripts/setup.sh

# Step 2 (optional) — FRED API key for higher rate limits (free)
# https://fred.stlouisfed.org/docs/api/api_key.html
export FRED_API_KEY=your_key_here

# Step 3 (optional) — FinMind token for Taiwan stocks (free registration)
# https://finmindtrade.com
export FINMIND_API_TOKEN=your_token_here
```

All other data sources (NBS, BOJ, e-Stat, stat.gov.tw, CBC, DGBAS, NDC,
PBOC/SHIBOR via akshare, FinanceDataReader BOK ECOS, yfinance) require
**no API key**. Scripts use `uv run` with inline dependencies — no
`pip install` after step 1.

## Data Sources

| Source | Data | Auth | Via |
|--------|------|------|-----|
| yfinance | US + global equity price/info; China/HK indices | None | `yfinance_client.py` |
| FRED | US macro (rates/inflation/GDP/nowcasts); CN FX | Optional | `fred_client.py` |
| SEC EDGAR | US financials (manual URL) | None | — |
| FinMind | Taiwan 三大法人 / 月營收 / 融資融券 / 董監持股 / 財報 | Optional | `finmind_client.py` |
| CasualMarket MCP | Taiwan real-time quotes (optional) | None | MCP |
| BOJ Time-Series API | Japan policy rate, JGB, money, TANKAN, forex | None | `boj_client.py` |
| 統計ダッシュボード (e-Stat) | Japan CPI, GDP, IP, unemployment, 景気動向指数 CI trio | None | `estat_client.py` |
| stat.gov.tw | Taiwan CPI, unemployment, trade, etc. (hidden chart JSON) | None | `statgov_client.py` |
| CBC Open Data API | Taiwan policy rate, FX reserves, M1B/M2 | None | `cbc_client.py` |
| DGBAS | Taiwan GDP, IP, 景氣燈號 (Excel .xls) | None | `dgbas_client.py` |
| NDC | Taiwan 景氣對策信號 + composite index (ZIP/CSV) | None | `ndc_client.py` |
| FinanceDataReader BOK ECOS | Korea 28 indicators (KEYSTAT preset) | None | `fdr_client.py` |
| NBS new-SPA API | China macro direct (`data.stats.gov.cn`) — 21 indicators | None | `nbs_client.py` |
| PBOC (chinamoney) via akshare | China LPR / RRR / 社融增量 / new loans | None | `akshare_client.py` |
| SHIBOR (shibor.org) via akshare | China interbank rates | None | `akshare_client.py` |

## Cross-Plugin Delegation

`investment-memo-writer` is the repo's first cross-plugin delegation skill:

```
investing-toolkit:investment-memo-writer
  ├── data-fetcher agent (I/O)
  ├── macro-regime-snapshot (regime context)
  ├── domain-teams:investing-team (analysis + gates)   ← cross-plugin
  └── domain-teams:docs-team (formatting, optional)    ← cross-plugin
```

See `CLAUDE.md` §Cross-Plugin Delegation Contract for conventions.
Data layer lives in this toolkit; analysis / verdicts / quality gates
live in `domain-teams:investing-team`.

## Cross-country Reference Documents

Plugin-level cross-market references (complement the per-skill references):

- [Industry Indicator Cadence](docs/industry-indicator-cadence.md) — five-country (US/JP/TW/KR/CN) comparison of industry-level indicator coverage, release frequencies (daily → annual tiers), publication lags, and investment-horizon matching guide

## Version Highlights

### v1.15.0 (2026-04-19) — Japan individual-stock skill (Path γ complete)

Closes the stacked-PR carry-over from v1.13.0: Japan joins US + TW as
the third market with a dedicated individual-stock data skill.

- **scripts/edinet_client.py** (739 lines): 金融庁 EDINET v2 REST API
  Tier A primary-source adapter. 7 form types (有報 120 / 四半期 140 /
  半期 160 / 臨時 180 / 自己株買付 220 / 大量保有 350 + 訂正版). CSV
  type=5 (added by FSA 2024-04) as MVP path — parses iXBRL-flattened
  BS/PL/CF into canonical key_metrics dict that mirrors sec_edgar /
  mops shape. Ticker → EDINET code resolution via free public
  Edinetcode.zip download (no key needed). PDL 1.0 license —
  redistribution OK with 出典：金融庁 EDINET attribution.

- **scripts/tdnet_client.py**: Same-day 適時開示情報 index via
  Yanoshin WEB-API. Covers 決算短信 / 業績予想 / 配当予想 / 自己株
  買付 / 株主総会 / 役員異動 — events EDINET 臨時報告書 surfaces only
  after ~45 days. Index-only pointer pattern; full documents fetched
  from JPX (release.tdnet.info).

- **yfinance_client.py --action financials** (new): Tier 2 BS/PL/CF
  fallback using Yahoo Finance for JP (and cross-market). Provenance
  explicitly labelled `data_tier: "tier_2"` with warning. Verified
  against EDINET on Toyota FY2025-03-31 — revenue / operating / net
  income / total assets / operating CF match to the yen.

- **skills/japan-stock-snapshot/**: Dual-mode tier routing SKILL.md.
  `EDINET_API_KEY` set → Tier A mode; absent → Tier 2 yfinance
  fallback with prominent upgrade-path prompt. Known gaps documented
  (信用取引残高 per-stock / 空売り / daily 投資部門別 — all locked
  behind J-Quants Standard paid tier or genuinely unavailable free).

- **investment-memo-writer**: Phase 1 extended to route 4-digit JP
  tickers (`^\d{4}(\.T|\.TO)?$`) to the new skill. Same output shape
  as US/TW snapshots so `domain-teams:research-team` gets a
  market-agnostic fixture.

- **MCP surface**: 13 → 19 tools (+4 edinet, +1 tdnet, +1
  yfinance_financials). `--self-check` returns 10 clients. Contract
  tests updated; all 3 pass.

### v1.14.0 (2026-04-19) — MCP migration (Claude Desktop Cowork unblock)

Exposes the 8 data-fetch scripts as **13 MCP tools** via a single plugin-
level MCP server. Claude Code and Claude Cowork auto-activate it on
plugin install; the MCP process runs outside the Claude Desktop sandbox,
so URL restrictions that previously blocked every data-fetch call in
Cowork are now bypassed by architecture.

- **servers/mcp_server.py**: FastMCP entry importing all 8 client
  modules. 13 tools total (yfinance × 3, sec_edgar × 4, fred / mops /
  twse_openapi / finmind / akshare_china_macro / nbs_china_macro × 1
  each). `--self-check` flag pre-warms uv cache + deps without
  entering the MCP loop.

- **.mcp.json + servers/mcp_bootstrap.sh**: plugin auto-registration.
  Two-path router: FAST PATH (marker + uv ready → exec real server in
  <3 s), BOOTSTRAP PATH (spawn setup.sh in background, exec stdlib
  wrapper that responds instantly under Claude Desktop's 60 s
  handshake timeout — empirically probed 2026-04-19).

- **servers/setup.sh**: silent-auto tiered install (Homebrew → curl
  astral.sh/uv/install.sh), then `--self-check` pre-warms 66 wheel
  installs, writes plugin-version marker. Non-developer users don't
  need to open Terminal.

- **servers/mcp_wrapper.py**: stdlib JSON-RPC; exposes
  `investing_toolkit_status` during the provisioning window so Claude
  can report live setup progress and ask for restart when ready.

- **Dual-mode scripts**: `register_mcp_tools()` added to all 8 client
  scripts; `uv run scripts/xxx.py` CLI paths remain untouched — MCP
  and CLI return identical JSON (enforced by
  `tests/test_mcp_contract.py`).

- **SKILL.md MCP-aware prose**: 8 skills annotated to prefer MCP tools
  when registered; subprocess commands remain canonical fallback.

- **docs/mcp-setup.md**: user install guide — Claude Code CLI,
  Claude Cowork (Team private fork), Pro/Max limitation notes,
  troubleshooting.

See [`docs/mcp-setup.md`](docs/mcp-setup.md) for install paths.

### v1.13.0 (2026-04-19) — Individual stock fundamentals (US + TW)

Closes Pattern C NVDA demo 4 data gaps (SEC EDGAR missing / forward
guidance / consensus / peer) for US + TW markets:

- **sec_edgar_client.py**: JSON API covering 7 SEC form types (10-K /
  10-Q / 8-K / Form 4 / 13F / S-1 / DEF 14A). XBRL structured facts +
  HTML narrative Item-section parser. User-Agent required, 10 req/sec
  compliance built-in, tiered cache TTL.

- **mops_client.py**: 16 endpoints via new MOPS JSON API (launched
  2025-02 at mops.twse.com.tw). Covers 公司基本資料 + 財報 BS/IS/CF +
  月營收 + 持股 + 股利 + 重大訊息 + 股東會. Historical depth: IFRS
  財報 13 yr (2013+), 歷史重大訊息 30 yr (1996+). No auth/cookie/CSRF.
  Primary-source Tier A (金管會法定揭露).

- **twse_openapi_client.py**: TWSE/TPEx public OpenAPI for 交易資料
  (日行情 / 融資融券 / 三大法人 snapshot / 產業 EPS / 除權息日曆).
  MOPS doesn't cover this — split by design.

- **taiwan-stock-snapshot rebuild**: MOPS + TWSE OpenAPI Tier 1
  primary; FinMind Tier 2 auto-fallback (Pattern A+B). Known Tier 1
  gaps (daily T86 per-stock flow, 歷史 STOCK_DAY) routed to FinMind by
  default with warning log.

- **dcf-valuation enable**: previously structurally crippled by
  missing financial statements; now auto-sources from SEC EDGAR (US)
  or MOPS (TW).

- **investment-memo-writer Phase 1 update**: SEC EDGAR + MOPS + TWSE
  OpenAPI commands added; FinMind retained as Tier 2 fallback path.

JP individual stock skill defers to v1.14.0 stacked PR (Path γ
architecture decision).

Pattern C re-run expectation: ISQ verdict `PASS` (not
`PASS_WITH_NOTES`) for NVDA and 2330.TW after v1.13.0 merge.

### v1.12.0 (2026-04-19) — Pattern C UX (file-write + visibility)

Fixes 3 UX issues exposed by v1.11.0 NVDA Pattern C demo:

- **investment-memo-writer Phase 5**: file-write default —
  `$CLAUDE_PLUGIN_DATA/memos/{YYYY-MM-DD}_{ticker}_{mode}_memo.md`
  with deep/quick mode-separated filenames (overwrite on same-mode
  re-run). Obsidian mode auto-detect: `$OBSIDIAN_VAULT_PATH` env var
  or probe `~/kouko-obsidian-vault/` etc.; reads vault `CLAUDE.md` for
  folder convention; routes via `obsidian:obsidian-markdown` skill.
  Chat delivery shows executive summary + gate verdicts + file link
  only (full memo lives in file, not repeated in chat).

- **investment-memo-writer Phase 3 target fix**: replaces
  `domain-teams:investing-team` references with
  `domain-teams:research-team` (per research-team's "investment or
  macro analysis" scope). Historical note preserved.

- **skill-team Visibility Convention (domain-teams v5.2.0)**: 7
  workflow skills (research / code / design / docs / devops / qa /
  planning) gain compliance block requiring `TaskUpdate` emission at
  3 levels: phase transitions + milestones + heartbeat (≤60 seconds
  max silence). Narration Convention (軸 1) added to
  investment-memo-writer for pre-dispatch expectation-setting.

Architectural alternative (軸 3 phase-split) deferred to v1.13.0+
if 軸 1+2 insufficient. Probabilistic vs structural guarantee
trade-off documented in skill-team SKILL.md §Visibility Convention.

Cross-plugin PR: investing-toolkit (1.11.0 → 1.12.0) + domain-teams
(5.1.0 → 5.2.0). 3-commit stack, ~3.5 days scope.

### v1.11.0 (2026-04-19) — Cross-country consistency refresh

Addresses v1.10.0 PMI asymmetry + grounding vintage drift:
- **china-macro**: new `pmi` group (Caixin mfg/svc via akshare + NBS
  official mfg/non-mfg/composite via existing nbs_client — primary-
  source preferred). Fills Block 1 CN PMI gap.
- **taiwan-macro**: new `pmi` group (PMI/NMI via NDC data.gov.tw CSV —
  unexpected free-tier access found during v1.11.0 APAC probe;
  license: 政府資料開放授權條款-第1版 CC BY equivalent)
- **japan-macro / korea-macro**: PMI URL-only references formalized
  (au Jibun Bank / S&P Global Korea licensed — no free-tier path)
- **macro-regime-snapshot**: Block 1 PMI row coverage improved 1/5 →
  3/5 live (+CN +TW); Data Source Architecture section expanded with
  5×9 cross-country coverage grid
- **grounding refresh**: CN + JP full re-audit to 2026-Q2 vintage
  (CN 2026 Work Report GDP 4.5-5% range; BOJ held 0.75% 2026-01/03);
  US + TW + KR delta addenda (FOMC SEP r* 3.0→3.1%; CBC held 2.00%;
  BOK 7-consecutive hold). 16 🔴 + 17 ⚠️ corrections total.
- **research/grounding-v1.11.0.md**: consolidated 299-line audit trail

JGBi YTM solver (originally considered for v1.11.0) deliberately
rejected for architectural consistency — would make JP the only
bond-math country among 5 country-macro skills, violating
"country-macro = pure data layer" discipline. Reaffirmed via
brainstorming audit.

### v1.10.0 (2026-04-19) — PMI + JP real rates + swap spread

Closes three data-coverage gaps from v1.9.0 deferred list:
- **us-macro**: new `pmi` group (OECD CLI USALOLITOAASTSAM as FRED-available
  proxy — ISM/S&P Global removed from FRED in 2016 per St. Louis Fed blog)
  + new `swap-spreads` group (Treasury-SOFR 3M spread as money-market
  liquidity proxy — post-LIBOR FRED has no clean term swap series)
- **japan-macro**: new `real-rates` group via C+D+E multi-source framework
  (MoF JGBi auction anchor + ECB monthly ex-post + BOJ Tankan 1Y/3Y/5Y
  expected inflation). JSDA YTM solver deferred to v1.11.0 after probe
  confirmed JSDA masks JGBi yields (999.999 sentinel). Added `ecb_client.py`
  and extended `boj_client.py` for Tankan.
- **macro-regime-snapshot**: Block 1 PMI row per country (US fetched;
  JP/TW/KR/CN URL-only). Block 3 renamed "Rate Stress Dashboard" with
  JP real-rate sub-block and US swap spread sub-block.
- **research**: new `grounding-v1.10.0.md` documenting primary-source
  vetting for 3 new JP data sources (MoF auction / ECB SDMX / BOJ Tankan)
  plus rejection rationale for JSDA / JBTS paths.

- **v1.9.0** — macro-regime-snapshot 5-country refresh (US/JP/TW/KR/CN) + LSEG-style 5-block dashboard (Macro Summary / Yield Curve / Real Rate / IC+GIP Regime / Asset-Class Tilts) + new US `real-rates` group in us-macro (T5YIE / T10YIE / DFII5 / DFII10 — real-rate decomposition block). Adds signal-label semantics (Expansion/Contraction, Accommodative/Restrictive, etc.)
- **v1.8.1** — Korea-macro monthly industry activity layer (43 → 54 indicators; new `industry` group: K201-K217 sector activity — manufacturing inventory/shipment/operating-rate, services production, retail sales, wholesale-retail, credit-card usage, machinery orders, capital-goods output, construction completion/orders)
- **v1.8.0** — Korea-macro catalogue + structural refactor + 15 Tier-B presets (28 → 43 indicators)
- **v1.7.3** — Taiwan + Korea monthly GDP proxy tagging (5-market framework complete)
- **v1.7.2** — Router sync + Layer column
- **v1.7.1** — China monthly GDP proxy tagging (Tier 2 parity with US/JP)
- **v1.7.0** — Monthly GDP proxies for US (nowcast group) + JP (CI trio)
- **v1.6.0** — China macro (34 indicators via NBS direct + PBOC + FRED + yfinance)
- **v1.5.0** — Korea macro (28 indicators via FinanceDataReader)
- **v1.4.0** — Taiwan macro (30 indicators, 4 government sources)
- **v1.3.0** — US + Japan macro skills
- **v1.2.0** — stock-screener, technical-snapshot, invest-portfolio
- **v1.1.0** — Taiwan stock data via FinMind
- **v1.0.0** — Core: macro-regime-snapshot, us-stock-snapshot, DCF, memo writer

See [ROADMAP.md](ROADMAP.md) for full history + v2.0.0 Quantitative Layer plans.
