# investing-toolkit

**Version**: 1.8.0
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
| `us-macro` | data | US macro via FRED (25 series incl. `nowcast` group) | v1.7.0 |
| `japan-macro` | data | Japan macro via BOJ + e-Stat (22 presets incl. 景気動向指数 CI trio) | v1.7.0 |
| `taiwan-macro` | data | Taiwan macro via stat.gov.tw + CBC + DGBAS + NDC (30 indicators) | v1.4.0 |
| `korea-macro` | data | Korea macro via FinanceDataReader BOK ECOS-KEYSTAT (**41 indicators, 12 groups**; full 98-code catalogue in `docs/`) | v1.8.0 |
| `china-macro` | data | China macro via NBS new-SPA API + PBOC + FRED + yfinance (34 indicators) | v1.7.1 |
| `us-stock-snapshot` | data | yfinance price + info for US tickers | v1.0.0 |
| `taiwan-stock-snapshot` | data | FinMind Taiwan data (三大法人, 月營收, 融資融券, 董監持股) | v1.1.0 |
| `technical-snapshot` | data | RSI / MACD / Bollinger / ATR / SMA via `ta_client.py` | v1.2.0 |
| `macro-regime-snapshot` | aggregation | Investment Clock phase + GIP quadrant from country macros | v1.0.0 |
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

## Version Highlights

- **v1.8.0** (current) — Korea-macro catalogue + structural refactor + 13 Tier-B presets (28 → 41 indicators)
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
