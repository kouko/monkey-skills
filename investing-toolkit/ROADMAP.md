# investing-toolkit Roadmap

## v1.0.0 — US + Macro Layer (current)

**Scope**: US stocks via yfinance + FRED macro data. Core invest* slash commands.

### Skills
- [x] using-investing-toolkit (router)
- [x] macro-regime-snapshot (IC + yield-curve + FRED)
- [x] us-stock-snapshot (yfinance + SEC EDGAR)
- [x] investment-memo-writer (→ domain-teams:investing-team)
- [x] dcf-valuation (3-stage DCF + sensitivity)

### Commands
- [x] /invest (router)
- [x] /invest-macro (regime call)
- [x] /invest-memo (full memo pipeline)

### Data adapters
- [x] scripts/yfinance_client.py
- [x] scripts/fred_client.py
- [x] agents/data-fetcher.md

---

## v1.1.0 — Taiwan Layer (current)

**Scope**: Taiwan equity data via FinMind. taiwan-stock-snapshot skill.

### New
- [x] scripts/finmind_client.py (FINMIND_API_TOKEN env, anonymous fallback)
- [x] skills/taiwan-stock-snapshot/SKILL.md
- [x] CasualMarket MCP installation guide (in scripts/README.md + taiwan-stock-snapshot)
- [x] investment-memo-writer Phase 1: FinMind commands for .TW/.TWO tickers
- [ ] /invest-screen {ticker} with --universe tw50 support (moved to v1.2.0)

---

## v1.2.0 — Screener + Technical Layer

**Scope**: Technical indicators, batch screener, portfolio review.

### New
- [x] scripts/ta_client.py (RSI/MACD/Bollinger/ATR/SMA from OHLCV, no external API)
- [x] scripts/yfinance_client.py --tickers batch mode
- [x] skills/technical-snapshot/SKILL.md (RSI, MACD, Bollinger, ATR, SMA)
- [x] skills/stock-screener/SKILL.md (valuation + momentum + trend composite score)
- [x] skills/invest-portfolio/SKILL.md (P&L snapshot + regime overlay + investing-team delegation)
- [x] /invest-screen {tickers} [--pe-max] [--above-sma200] [--rsi-min/max]
- [x] /invest-portfolio [holdings.csv | inline-list]

---

## v1.3.0 — Country Macro Skills (current)

**Scope**: Country-specific macro data skills with bilingual indicator references.

### New
- [x] scripts/boj_client.py (BOJ Time-Series API, no auth)
- [x] scripts/estat_client.py (統計ダッシュボード API, no auth)
- [x] skills/us-macro/SKILL.md (FRED 8 indicators + reference doc)
- [x] skills/japan-macro/SKILL.md (BOJ + 統計DB 13 indicators + bilingual reference)
- [x] macro-regime-snapshot: region=japan support
- [x] japan-boj-db-catalog.md (40+ DB bilingual catalog)

---

## v1.4.0 — Taiwan Macro

**Scope**: Taiwan macro indicators from 4 government sources.

### New
- [x] scripts/statgov_client.py (stat.gov.tw hidden chart JSON, 17 presets)
- [x] scripts/cbc_client.py (CBC Open Data API, 5 presets)
- [x] scripts/dgbas_client.py (DGBAS Excel .xls, 6 presets)
- [x] scripts/ndc_client.py (NDC ZIP/CSV, 6 presets)
- [x] skills/taiwan-macro/SKILL.md (30 indicators, 8 groups, trilingual references)

---

## v1.5.0 — Korea Macro

**Scope**: Korea macro indicators via FinanceDataReader (BOK ECOS-KEYSTAT).

### New
- [x] scripts/fdr_client.py (FinanceDataReader ECOS-KEYSTAT, 27 presets + 1 FRED)
- [x] skills/korea-macro/SKILL.md (28 indicators, 10 groups, trilingual references)
- [x] Unified indicator reference format across US/JP/TW/KR (93 indicators)
- [x] Cache migration to $CLAUDE_PLUGIN_DATA convention (10 scripts)

---

## v1.6.0 — China Macro

**Scope**: China macro indicators via akshare (NBS + PBOC + SHIBOR),
FRED fallbacks (CNY/USD, FX reserves), and yfinance market indices.

### New
- [x] scripts/akshare_client.py (19 presets: inflation/growth/trade/labor/sentiment/rates/money/credit — 2 Caixin PMI presets removed 2026-04-18, mirror ran 8mo stale)
- [x] skills/china-macro/SKILL.md (26 indicators total: 19 akshare + 2 FRED + 5 yfinance, trilingual references)
- [x] NBS WAF workaround — akshare mirrors (eastmoney, investing.com, chinamoney, shibor.org) remain reachable when `data.stats.gov.cn` blocks foreign IPs
- [x] 10 reference files including 119 indicator sections across US/JP/TW/KR/CN (unified format)
- [x] NBS new-SPA API reverse-engineered (`docs/nbs-indicator-catalog.md`): 2908-leaf indicator tree captured for future `nbs_client.py` work

---

## v1.7.0 — Monthly GDP Proxies for US + JP

**Scope**: Cross-market symmetric monthly GDP tracking. US and Japan gain
the monthly-GDP-proxy indicator packages that china-macro already provides
via 三大數據 + services-production.

**Background**: No major economy publishes official monthly GDP (UK and
Canada are exceptions). For US, the Fed family of nowcasts (GDPNow, CFNAI,
WEI) plus OECD CLI are the industry-standard proxies. For Japan, the
内閣府 景気動向指数 CI trio (先行/一致/遅行) is the canonical proxy, with
一致指数 treated as the definitive "current GDP feel".

### New
- [x] us-macro: +4 presets under new `nowcast` group — `GDPNOW` (Atlanta Fed), `CFNAI` (Chicago Fed), `WEI` (NY Fed), `USALOLITOAASTSAM` (OECD CLI, replacing discontinued USSLIND). 21 → 25 series.
- [x] japan-macro: +2 presets `leading-index` + `lagging-index` completing the 景気動向指数 CI trio. 14 → 16 active indicators.
- [x] references/indicators-growth.md expanded in both skills with full monthly-GDP-proxy documentation.

---

## v1.7.1 — China monthly GDP proxy tagging

**Scope**: Tier 2 symmetry with us-macro / japan-macro. Explicitly tag
三大数据 + `services-production-yoy` as monthly GDP proxy components
in china-macro documentation so all three country skills share the
same proxy-labelling convention.

### New
- [x] china-macro SKILL.md: Monthly GDP proxy callout in Overview; `growth` group re-titled as "三大数据 — monthly GDP proxy components"; 4 indicator rows tagged with bold proxy labels
- [x] china-macro README.md: cross-market parity Overview note
- [x] references/indicator-index.md: 4 indicators tagged `(**monthly GDP proxy component/companion**)`
- [x] references/indicators-growth.md: new 三大数据 monthly trio preamble explaining cross-market parallel + why Tier 3 synthesis is deferred
- [x] references/indicators-services.md: `services-production-yoy` annotated as 2017-introduced services-gap filler in the proxy package

### Deliberately NOT done — Tier 3 (synthesised single-number proxy)

Research finding: no market consensus across Li Keqiang Index (obsolete
post-2012 services shift), SF Fed China CAT (quarterly + standard-deviation
units, not monthly %YoY), Goldman CAI / Bloomberg China Monthly GDP
(proprietary), academic DFM nowcasts (each paper uses a different
variable set). Picking any single methodology would embed an analytical
choice in the data layer, violating the toolkit/analysis separation in
`CLAUDE.md` cross-plugin contract. Synthesis belongs in `investing-team`
analysis layer. See `docs/china-macro-research-frameworks.md §1d` for
deferred methodology options if requirements change.

---

## v1.7.2 — Router sync + Layer column

**Scope**: Documentation-only. Update `using-investing-toolkit/SKILL.md`
to reflect post-v1.6.0 indicator counts, the v1.7.0/v1.7.1 Monthly GDP
Proxy framework, and a new `Layer` column distinguishing data /
aggregation / delegation skills.

### New
- [x] using-investing-toolkit skill table synced: us-macro 21→25 series, japan-macro 20→22 presets, china-macro 28→34 indicators
- [x] Skill versions updated: us-macro / japan-macro → v1.7.0, china-macro → v1.7.1
- [x] Cross-market Monthly GDP Proxy Framework section added — summarises US nowcast / JP CI trio / CN 三大数据 parity + why CN stays Tier 2
- [x] `Layer` column added to Available Skills table (data / aggregation / delegation); skills re-sorted by layer for easier discovery

---

## v1.7.3 — Taiwan + Korea monthly GDP proxy tagging

**Scope**: Extend the cross-market Monthly GDP Proxy Framework from 3 to 5
markets. TW and KR already had CI-family indicators in their skills; v1.7.3
adds the Tier 2 tagging + framework row + references preamble.

### New

- [x] taiwan-macro: tag `signal` / `leading-index` / `coincident-index` as
  monthly GDP proxy components; SKILL + README + indicator-index + indicators-cycle
  (4 files) updated with **Taiwan 特色 五色景氣燈號** emphasis
- [x] korea-macro: tag `leading-cycle` (K254) / `coincident-cycle` (K253) as
  monthly GDP proxy leading + proxy; SKILL + README + indicator-index +
  indicators-sentiment (4 files) updated
- [x] Cross-market Monthly GDP Proxy Framework expanded from 3 → 5 markets
  in both `using-investing-toolkit/SKILL.md` and plugin-level `README.md`

### Deliberately NOT done

- **KR lagging CI** (후행지수순환변동치) — probed K255/K256; both map to
  other series (manufacturing-related, 16 rows) rather than Lagging CI
  Cyclical Component. BOK ECOS KEYSTAT does not expose this index.
  Statistics Korea (KOSIS) publishes it but would require a separate
  scraper — deferred to v1.8.0 if demand arises.
- **TW Tier 3 synthesis** — not needed; NDC already publishes pre-aggregated
  composite score + colour via `signal`.
- **KR Tier 3 synthesis** — not needed; BOK ECOS already publishes
  pre-aggregated CI cyclical components.

---

## v1.8.0 — Korea-macro catalogue + structural refactor + Tier-B expansion (current)

**Scope**: Three-phase korea-macro upgrade — document the full BOK ECOS
KEYSTAT catalogue (mirror of the v1.6.0 NBS tree work for CN), refactor
the `sentiment` group, and add 13 Tier-B presets across 5 existing
groups + 1 new `demographics` group.

### Phase 1 — Catalogue
- [x] `skills/korea-macro/docs/bok-ecos-keystat-catalog.md` — 98-code
  human-readable catalogue grouped by category (monetary / rates /
  markets / FX / activity / CI / labor / BoP / prices / demographics)
  with preset status (in-skill / v1.8.0 / candidate / skip)
- [x] `skills/korea-macro/docs/bok-ecos-keystat.json` — machine-readable
  raw probe output
- [x] `skills/korea-macro/docs/tools/probe-keystat.py` — re-probe script
  (sweeps K001-K500)

### Phase 2 — Structural refactor
- [x] Split `sentiment` group into `sentiment` (CSI K252 / ESI K269 —
  survey-based) + `cycle` (CI pair K253/K254 — business cycle indices).
  Fixes the semantic inconsistency inherited from v1.5.0.
- [x] New `references/indicators-cycle.md` (moved CI content out of
  `indicators-sentiment.md`); `indicators-sentiment.md` retains only
  CSI/ESI

### Phase 3 — Tier-B expansion (+13 presets, 28 → 41 indicators)
- [x] `rates`: +`koribor-3m` (K063) — cross-market parallel of JP SHIBOR 3M
- [x] `growth`: +`private-consumption` (K259), +`equipment-investment` (K260),
  +`construction-investment` (K261) — GDP expenditure breakdown
- [x] `trade`: +`goods-exports` (K462) — fills the major gap of
  no-exports-indicator (KR export dependency ~40% of GDP)
- [x] `money`: +`m1` (K002), +`lf` (K004) — cross-market symmetry with JP/CN
- [x] `fx`: +`krw-jpy` (K153), +`krw-eur` (K154), +`krw-cny` (K156),
  +`fx-reserves` (K155)
- [x] **New `demographics` group** (+3 presets): `population` (K451),
  `aging-ratio` (K460), `fertility-rate` (K461) — long-horizon structural
  context (KR leads JP demographic decline by ~15-20 years)
- [x] New `references/indicators-demographics.md`

### Deferred (v1.9.0 candidate)

- **Full BOK ECOS API integration** — would unlock ~50 additional Tier-B
  candidates (identified in `docs/bok-ecos-keystat-catalog.md` as
  `candidate` rows) plus the lagging CI (후행지수순환변동치) not
  exposed via KEYSTAT. Requires free API key registration at
  https://ecos.bok.or.kr/api/#/AuthKeyApply.

---

## v2.0.0 — Quantitative Layer (tentative)

**Scope**: Backtesting integration, factor models.

### Ideas
- [ ] Backtesting workflow (integrates with domain-teams:investing-team standards/backtesting-and-robustness-discipline.md)
- [ ] Factor exposure snapshot (Fama-French 5-factor)
- [ ] Alpha Vantage premium adapter (technical indicators)
- [ ] Portfolio optimizer (risk parity / Kelly allocation)
