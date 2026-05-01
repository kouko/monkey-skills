---
name: data-cn
description: >-
  Layer 1 (Data) skill for China — fetch CN macro indicators and individual
  stock data via NBS new-SPA API (Tier A primary, 21 presets), akshare
  aggregator (PBOC LPR/RRR/SHIBOR + 社融/new loans + Caixin PMI, 8 presets),
  FRED (USDCNY + FX reserves, 2 series), and yfinance (.SS/.SZ/.HK). Pure
  I/O — no analysis, no scoring. Outputs structured JSON via 5 pack types
  (snapshot, memo-fetch, comps-multiples, screener-batch, regime-pack).
  中国データ層 — マクロ + 個別株（.SS/.SZ/.HK）取得。
  中國資料層 — 宏觀 + 個股（.SS/.SZ/.HK）擷取。
---

# data-cn

**Layer 1 — Data (China)** in the investing-toolkit v2.0.0 three-layer
architecture (Data → Analysis → Report). Pure fetch + tier routing +
batch dispatch. Does NOT call analysis or report skills. Does NOT compute,
score, or classify.

| Source | Authority | Coverage |
|---|---|---|
| **NBS new-SPA API** (`data.stats.gov.cn/dg/website/publicrelease/web/external/*`) | **Tier A primary** | 21 presets: CPI/PPI/GDP/industrial/retail/FAI/trade/labor/PMI/money/real-estate/services |
| **akshare aggregator** (PBOC chinamoney + SHIBOR + Caixin via eastmoney) | Tier 2 — only for series NBS does not publish | 8 presets: LPR×2, RRR, SHIBOR-3M, 社融增量, new loans, Caixin Mfg PMI, Caixin Svc PMI |
| **FRED CSV** | Tier A (US Federal Reserve as Chinese FX cross-source) | DEXCHUS (CNY/USD), TRESEGCNM052N (FX reserves ex-gold) |
| **yfinance** (Yahoo Finance, unofficial) | Tier 2 | .SS / .SZ / .HK individual stocks; market indices (CSI300, SSEC, ChiNext, HSI, HSCEI) |

Auth: none required. NBS new-SPA + akshare endpoints are reachable from
TW / US / Anthropic IPs (verified empirically; rationale preserved in git
history pre-v2.0.0 in the deleted `china-macro/docs/` directory).

---

## Ticker convention

| Suffix | Exchange | Example |
|---|---|---|
| `.SS` | Shanghai Stock Exchange | `600519.SS` (Kweichow Moutai), `601318.SS` (Ping An) |
| `.SZ` | Shenzhen Stock Exchange | `000858.SZ` (Wuliangye), `300750.SZ` (CATL) |
| `.HK` (4-digit) | Hong Kong Stock Exchange | `0700.HK` (Tencent), `9988.HK` (Alibaba) |
| `.HK` (5-digit) | Hong Kong Stock Exchange (leading-zero form) | `09988.HK` (Alibaba), `02318.HK` (Ping An H), `03690.HK` (Meituan) |

`pack.py` auto-appends suffix when a bare numeric code is passed
(heuristic: 6-digit starting with `6`/`9` → `.SS`; 6-digit starting with
`0`/`2`/`3` → `.SZ`; 4-digit or 5-digit numeric → `.HK`). Tickers with
explicit suffix or `^`-prefix indices pass through unchanged.

**Not supported:**
- **BSE (北京证券交易所)** — 6-digit codes starting with `4` or `8`
  (e.g. `430xxx`, `830xxx`, `870xxx`). yfinance does not cover BSE;
  `pack.py` emits a stderr warning and passes through unchanged.
  BSE primary-source disclosure is out of v2.0.0 scope.
- Bare numeric codes outside `{4, 5, 6}` digits emit a stderr warning
  ("Unrecognized CN ticker format") and pass through unchanged.

---

## Pack types

`pack.py` exposes 5 pack modes per the v2.0.0 contract:

| Pack | `--ticker` | `--tickers` | Output |
|---|---|---|---|
| `snapshot` | required | optional | yfinance info + 6mo history (quick overview card) |
| `memo-fetch` | required | not supported (N=1) | yfinance info + 2y history + annual + quarterly financials. **Tier 2 only — CN primary-source individual-stock disclosure (cninfo / HKEXnews) not in v2.0.0 scope.** |
| `comps-multiples` | single | batch | yfinance info → 5 multiples (trailingPE, forwardPE, EV/EBITDA, P/S, P/B) per ticker; consumed by `analysis-comps` |
| `screener-batch` | not supported | required | yfinance batch info + history (lightweight fields for 50–500 tickers) |
| `regime-pack` | n/a | n/a | NBS (21) + akshare (8) + FRED USDCNY + market indices — full CN macro snapshot |

---

## Inputs

| Parameter | Required | Notes |
|---|---|---|
| `--pack` | yes | One of `snapshot` / `memo-fetch` / `comps-multiples` / `screener-batch` / `regime-pack` |
| `--ticker` | conditional | Required for `snapshot` / `memo-fetch`; optional for `comps-multiples` |
| `--tickers` | conditional | Required for `screener-batch`; optional for `comps-multiples` |

---

## How It Works

### Single-ticker snapshot

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run \
  ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker 600519.SS --pack snapshot
```

### Batch screener

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run \
  ${CLAUDE_SKILL_DIR}/scripts/pack.py \
  --tickers 600519.SS,000858.SZ,300750.SZ,0700.HK,9988.HK \
  --pack screener-batch
```

### Comps multiples (anchor + peers)

```
# anchor
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run \
  ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker 600519.SS --pack comps-multiples \
  > /tmp/anchor.json

# peers
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run \
  ${CLAUDE_SKILL_DIR}/scripts/pack.py --tickers 000858.SZ,000596.SZ,600809.SS \
  --pack comps-multiples > /tmp/peers.json
```

### Regime pack (macro only — no per-ticker dimension)

```
INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache uv run \
  ${CLAUDE_SKILL_DIR}/scripts/pack.py --pack regime-pack
```

`regime-pack` composes 4 sub-fetches:
1. `nbs_client.py --preset cpi-yoy,core-cpi,...,services-production-yoy` (21 presets)
2. `akshare_client.py --preset lpr-1y,...,caixin-svc-pmi` (8 presets)
3. `fred_client.py --series DEXCHUS,TRESEGCNM052N --periods 24`
4. `yfinance_client.py --tickers 000300.SS,000001.SS,399006.SZ,^HSI,^HSCE --action history`

---

## Tier-routing logic

The `pack.py` facade encodes which client owns which series:

| Series category | Routes to | Reason |
|---|---|---|
| CPI / PPI / GDP / industrial / retail / FAI / trade / labor / PMI (NBS official) / money / real estate / services | `nbs_client.py` | NBS publishes these directly via new-SPA API; akshare's NBS-mirror is stale/lagged |
| LPR / RRR / SHIBOR / 社融 / new loans | `akshare_client.py` | PBOC publishes via chinamoney/SHIBOR endpoints, no NBS series available |
| Caixin Mfg PMI / Caixin Svc PMI | `akshare_client.py` | S&P Global publishes via Caixin partnership; eastmoney mirror is the only stable feed |
| CNY/USD / FX reserves | `fred_client.py` | FRED is canonical for cross-rate; TRESEGCNM052N is IMF/SAFE pipeline |
| Individual stocks / market indices | `yfinance_client.py` | Tier 2 fallback; CN primary-source individual-stock disclosure (cninfo / HKEXnews) deferred |

---

## Indicator coverage

| Group | Indicators | Source |
|---|---|---|
| inflation | cpi-yoy, core-cpi, ppi-yoy | NBS |
| growth | gdp-yoy, industrial-yoy, retail-yoy, fai-yoy (三大数据 — monthly GDP proxy) | NBS |
| trade | exports-yoy, imports-yoy, trade-balance | NBS |
| labor | urban-unemployment | NBS |
| pmi | pmi-manufacturing, pmi-non-manufacturing, pmi-composite (NBS 官方); caixin-mfg-pmi, caixin-svc-pmi | NBS + akshare |
| money | m1-yoy, m2-yoy | NBS |
| rates | lpr-1y, lpr-5y, rrr-major, shibor-3m | akshare (PBOC/SHIBOR) |
| credit | shrzgm, new-loans | akshare (PBOC) |
| realestate | realestate-investment-yoy, housing-sales-area-yoy, housing-sales-value-yoy, realestate-funding-yoy | NBS |
| services | services-production-yoy | NBS |
| markets | 000300.SS, 000001.SS, 399006.SZ, ^HSI, ^HSCE | yfinance |
| fx | DEXCHUS, TRESEGCNM052N | FRED |

Total: 21 NBS + 8 akshare + 2 FRED + 5 markets = **36 macro/market series** plus per-ticker individual-stock pulls.

---

## Output contract

All packs emit structured JSON to stdout. Each observation carries
`_source` provenance (`"nbs_spa"` / `"akshare"` / `"csv"` / `"yfinance"`)
inherited from the underlying client. Cross-skill pipelines are expected
to read JSON from a temp file:

```
# main agent orchestrator pattern (see CLAUDE.md cross-plugin contract)
uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --pack regime-pack > /tmp/cn-regime.json
uv run skills/analysis-macro-regime/scripts/regime_compute.py --input /tmp/cn-regime.json
```

---

## Limitations

### Data freshness

| Source | Freshness |
|---|---|
| NBS CPI / PPI / PMI | ~45–50d (monthly, around 9th–15th of next month) |
| NBS FAI / Trade / M1 / M2 / unemployment / real estate | ~75d |
| NBS industrial / retail / services-production | **~135d in Jan-Feb** (combined Jan-Feb release; single-month YoY only from March) |
| NBS GDP | ~100d (quarterly, ~Day 20 of first month after quarter end) |
| akshare LPR / SHIBOR | same-day to 1 BD |
| akshare RRR | event-driven |
| akshare 社融 / new-loans | ~1–2mo lag |
| akshare Caixin Mfg PMI | ~20–30d (1st BD after month-end) |
| akshare Caixin Svc PMI | ~30–50d (3rd BD after month-end) |
| FRED DEXCHUS | 1–2 BD |
| FRED TRESEGCNM052N | ~30–60d (SAFE cadence) |
| yfinance | ~real-time (15 min delay) |

### Deliberately excluded

- **CSRC / cninfo individual-stock disclosure** (Tier A primary for CN
  equities) — not yet integrated. memo-fetch falls back to yfinance
  Tier 2 only.
- **HKEXnews** (Tier A for .HK equities) — not integrated.
- **70-city housing price index** — NBS publishes only as standalone
  monthly PDF; would require a separate parser.
- **社融存量 同比增长** (TSF stock YoY growth) — only in PBOC press
  release text; akshare gives flow (增量) only.
- **Li Keqiang Index composite** — components (electricity / rail
  freight / new loans) available individually; composite preset deferred
  pending market-consensus methodology.

---

## Cross-Skill Handoff (v2.0.0 three-layer)

```
data-cn (this skill, Layer 1)
  -> analysis-{dcf,comps,screener,technical,portfolio,macro-regime} (Layer 2 — pure compute)
  -> report-{equity-memo,stock-snapshot,portfolio-review,screener-list} (Layer 3 — orchestration + format)
  -> domain-teams:investing-team (cross-plugin gate verdict)
```

`data-cn` does NOT directly invoke any analysis or report skill. The
**main agent** (or a report skill in subprocess mode) reads `pack.py`
output via temp files and dispatches the next layer.

---

## Reference

- Spec: `docs/superpowers/specs/2026-05-01-investing-toolkit-v2.0.0-three-layer-design.md` §4.2
- ADR: `investing-toolkit/docs/adr/0001-data-analysis-report-layers.md`
- Canonical clients: `investing-toolkit/scripts/`
- v1.x source skill `china-macro` was deleted in v2.0.0; full NBS UUID catalog,
  3-language industry research synthesis, and akshare endpoint docs preserved
  in git history (pre-v2.0.0 commits)

---

## i18n

Description front-matter carries en + zh-TW + ja one-liners per repo
i18n convention. Detailed multilingual READMEs are deferred to PR 3
(documentation polish).
