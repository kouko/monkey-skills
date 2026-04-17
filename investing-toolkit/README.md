# investing-toolkit

**Version**: 1.3.0  
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

Investing research toolkit — macro regime diagnosis, country-specific macro data
(US + Japan), DCF valuation, US equity snapshots, and full investment memo
pipeline via `domain-teams:investing-team`.

## Slash Commands

| Command | What it does | Status |
|---------|-------------|--------|
| `/invest` | Route to the right skill | ✅ v1.0.0 |
| `/invest-macro [--region us\|japan\|global]` | IC + FRED/BOJ regime call | ✅ v1.0.0 |
| `/invest-memo {ticker} [--scope deep\|quick]` | Full memo pipeline → investing-team | ✅ v1.0.0 |
| `/invest-screen {tickers} [--pe-max N] [--above-sma200]` | Batch screener + composite rank | ✅ v1.2.0 |
| `/invest-portfolio [holdings.csv]` | Portfolio review + rebalance | ✅ v1.2.0 |

## Skills

| Skill | Purpose | Status |
|-------|---------|--------|
| `using-investing-toolkit` | Router | ✅ v1.0.0 |
| `macro-regime-snapshot` | Investment Clock + FRED | ✅ v1.0.0 |
| `us-stock-snapshot` | yfinance price + info | ✅ v1.0.0 |
| `investment-memo-writer` | Full memo orchestration | ✅ v1.0.0 |
| `dcf-valuation` | 3-stage DCF + sensitivity | ✅ v1.0.0 |
| `taiwan-stock-snapshot` | FinMind Taiwan data (三大法人, 月營收, 融資融券, 董監持股) | ✅ v1.1.0 |
| `stock-screener` | Batch screener — composite score | ✅ v1.2.0 |
| `technical-snapshot` | RSI / MACD / Bollinger / ATR / SMA | ✅ v1.2.0 |
| `invest-portfolio` | Portfolio review + rebalance | ✅ v1.2.0 |
| `us-macro` | US macro indicators via FRED (8 series) | ✅ v1.3.0 |
| `japan-macro` | Japan macro indicators via BOJ + e-Stat (13 series, bilingual) | ✅ v1.3.0 |

## Architecture

```
investing-toolkit/
├── scripts/                          # Source of truth (edit here only)
│   ├── yfinance_client.py           #   → synced to skill dirs via sync-scripts.sh
│   ├── fred_client.py               #   → synced to skill dirs
│   ├── finmind_client.py            #   → synced to skill dirs
│   ├── ta_client.py                 #   → synced to skill dirs
│   ├── boj_client.py                #   → synced to japan-macro
│   ├── estat_client.py              #   → synced to japan-macro
│   ├── sync-scripts.sh              # Copy source → skill dirs
│   └── sync-check.sh               # CI: verify all copies match
├── agents/data-fetcher.md           # Shared I/O agent spec
├── skills/
│   ├── us-macro/                    # US FRED indicators (v1.3.0)
│   ├── japan-macro/                 # BOJ + e-Stat indicators (v1.3.0)
│   ├── macro-regime-snapshot/       # IC regime → consumes us-macro / japan-macro
│   ├── {each-skill}/
│   │   ├── SKILL.md
│   │   ├── scripts/                 # Self-contained: synced copies
│   │   │   └── yfinance_client.py   #   from scripts/ source of truth
│   │   └── references/              # Self-contained: skill-specific docs
│   └── ...
│
│   investment-memo-writer/ ──→  domain-teams:investing-team
│                                  (analysis + quality gates + ISQ)
│                            ──→  domain-teams:docs-team
│                                  (optional formatting)
└── commands/                        # /invest-* slash commands
```

Each skill is self-contained with its own `scripts/` and `references/`.
Plugin-level `scripts/` is the single source of truth — run `sync-scripts.sh`
after editing, `sync-check.sh` to verify.

## Setup

```bash
# Step 1 — install uv (Homebrew first, curl fallback, skip if already installed)
sh investing-toolkit/scripts/setup.sh

# Step 2 (optional) — FRED API key for higher rate limits (free)
# https://fred.stlouisfed.org/docs/api/api_key.html
export FRED_API_KEY=your_key_here

# Step 3 (optional) — FinMind token for Taiwan data (free registration)
# https://finmindtrade.com
export FINMIND_API_TOKEN=your_token_here
```

Scripts use `uv run` with inline dependencies — no `pip install` needed after step 1.

## Taiwan Stocks

v1.1.0 adds full Taiwan equity data via FinMind:
- `scripts/finmind_client.py` — 三大法人, 月營收, 融資融券, 董監持股
- `taiwan-stock-snapshot` skill — structured snapshot card + cross-plugin handoff
- **CasualMarket MCP** (optional, real-time quotes) — see `scripts/README.md`

## Data Sources

| Source | Data | Auth |
|--------|------|------|
| yfinance | US price, basic info | None |
| FRED | Macro: yield curve, CPI, GDP, Fed Funds | Optional API key |
| SEC EDGAR | US financials (via manual URL) | None |
| FinMind | Taiwan: 三大法人, 月營收, 融資融券, 董監持股, 財報 | Optional token |
| CasualMarket MCP | Taiwan real-time quotes | None |
| BOJ Time-Series API | Japan: policy rate, JGB yields, monetary base | None |
| 統計ダッシュボード (e-Stat) | Japan: CPI, GDP, industrial production, unemployment | None |

## Cross-Plugin Delegation

`investment-memo-writer` is the repo's first cross-plugin delegation skill:

```
investing-toolkit:investment-memo-writer
  → data-fetcher (I/O)
  → macro-regime-snapshot (regime context)
  → domain-teams:investing-team (analysis + gates)  ← cross-plugin
  → domain-teams:docs-team (formatting, optional)   ← cross-plugin
```

See `CLAUDE.md` §Cross-Plugin Delegation Contract for conventions.

## Roadmap

See [ROADMAP.md](ROADMAP.md).
