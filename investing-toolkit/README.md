# investing-toolkit

**Version**: 1.10.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

Investing research toolkit — **5-country macro data** (US / JP / TW / KR / CN),
stock snapshots (US / TW), technical indicators, DCF valuation, stock screener,
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
| `taiwan-macro` | data | Taiwan macro via stat.gov.tw + CBC + DGBAS + NDC (30 indicators) | v1.4.0 |
| `korea-macro` | data | Korea macro via FinanceDataReader BOK ECOS-KEYSTAT (**54 indicators, 13 groups** incl. monthly `industry` activity layer; full 98-code catalogue in `docs/`) | v1.8.1 |
| `china-macro` | data | China macro via NBS new-SPA API + PBOC + FRED + yfinance (34 indicators) | v1.7.1 |
| `us-stock-snapshot` | data | yfinance price + info for US tickers | v1.0.0 |
| `taiwan-stock-snapshot` | data | FinMind Taiwan data (三大法人, 月營收, 融資融券, 董監持股) | v1.1.0 |
| `technical-snapshot` | data | RSI / MACD / Bollinger / ATR / SMA via `ta_client.py` | v1.2.0 |
| `macro-regime-snapshot` | aggregation | 5-country IC + GIP (US/JP/TW/KR/CN) + Rate Stress Dashboard (US real-rate + JP real-rate C+D+E + US swap spread, all tagged v1.10.0) | v1.10.0 |
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
