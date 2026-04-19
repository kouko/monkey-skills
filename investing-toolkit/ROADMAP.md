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

## v1.8.0 — Korea-macro catalogue + structural refactor + Tier-B expansion

**Scope**: Three-phase korea-macro upgrade — document the full BOK ECOS
KEYSTAT catalogue (mirror of the v1.6.0 NBS tree work for CN), refactor
the `sentiment` group, and add 15 Tier-B presets across 5 existing
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

### Phase 3 — Tier-B expansion (+15 presets, 28 → 43 indicators)
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

- **Full BOK ECOS API integration** — would unlock the remaining Tier-B
  candidates (identified in `docs/bok-ecos-keystat-catalog.md` as
  `candidate` rows) plus the lagging CI (후행지수순환변동치) not
  exposed via KEYSTAT. Requires free API key registration at
  https://ecos.bok.or.kr/api/#/AuthKeyApply.

---

## v1.8.1 — Korea industry activity layer

**Scope**: Closes the KR sector-activity coverage gap (identified as
`candidate` in v1.8.0 catalogue) — adds the monthly K201-K217 경제활동
cluster as a new `industry` group. Parallels JP `activity` group and
TW `production` group; completes cross-market parity for monthly
sector pulse.

### Phase 1 — New `industry` group (+11 presets, 43 → 54 indicators)
- [x] Manufacturing trio: `manufacturing-inventory` (K202),
  `manufacturing-shipment` (K203), `manufacturing-operating-rate` (K204)
- [x] Services + retail: `services-production` (K205),
  `retail-sales` (K206), `wholesale-retail` (K207),
  `credit-card-usage` (K210)
- [x] Capex cycle: `machinery-orders` (K213),
  `capital-goods-output` (K215)
- [x] Construction cycle: `construction-completion` (K216),
  `construction-orders` (K217)

### Phase 2 — Documentation
- [x] `skills/korea-macro/references/indicators-industry.md` (new, bilingual)
- [x] `skills/korea-macro/SKILL.md` — new group section + Step 1/2 fetch
  batches + lag table entries
- [x] `skills/korea-macro/README.md` — counts 43 → 54, group list 12 → 13
- [x] `skills/korea-macro/references/indicator-index.md` — 11 new rows +
  `industry (11)` group row
- [x] `skills/korea-macro/docs/bok-ecos-keystat-catalog.md` — 11 rows
  flipped `candidate` → `v1.8.1`
- [x] `skills/using-investing-toolkit/SKILL.md` + plugin-level `README.md`
  counts updated

### Deferred
- v1.10.0+: full BOK ECOS API integration (lagging CI + ~10K series,
  requires free API key; originally scoped as v1.9.0, re-deferred when
  macro-regime refresh took v1.9.0 slot)

---

## v1.9.0 — macro-regime-snapshot multi-country + LSEG real-rate block

**Scope**: Rewrite `macro-regime-snapshot` to cover **all 5 country
macro skills** (US/JP/TW/KR/CN) using the v1.7.0 monthly GDP proxies,
and absorb the LSEG `macro-rates-monitor` dashboard pattern — new
5-block output (Macro Summary / Yield Curve / Real Rate / IC+GIP /
Asset-Class Tilts) with signal-label semantics
(Expansion/Contraction, Accommodative/Restrictive). Adds US real-rate
block via 4 new FRED series; IC + GIP framework unchanged.

### Phase 1 — us-macro `real-rates` group (+4 FRED series, 25 → 29 total)
- [x] `scripts/` — no change (fred_client.py is a generic CSV fetcher)
- [x] `skills/us-macro/SKILL.md` — new `real-rates` group section + Step 1/2 updates
- [x] `skills/us-macro/references/us-macro-indicators.md` — new Real Rates
  section (T5YIE, T10YIE, DFII5, DFII10) with threshold framing

### Phase 2 — macro-regime-snapshot rewrite
- [x] `skills/macro-regime-snapshot/SKILL.md` — complete rewrite:
  - `region` expanded 3 → 9 values (us / japan / taiwan / korea / china /
    global / asia-pac / all / free-form list)
  - Per-country proxy routing (use v1.7.0 monthly GDP proxies, not raw IPI)
  - New Step 4: real-rate decomposition block (US only)
  - New Step 5: 5-block dashboard output format
- [x] `skills/macro-regime-snapshot/references/investment-clock-cheatsheet.md`
  — extended with per-country proxy mapping, real-rate thresholds
  section, signal-label glossary (LSEG absorption)

### Phase 3 — Plugin-level docs
- [x] `commands/invest-macro.md` — `--region` enum updated to 9 values +
  examples + Real-Rate block note
- [x] `skills/using-investing-toolkit/SKILL.md` — rows for us-macro
  (+ real-rates) and macro-regime-snapshot (5-country + LSEG dashboard)
- [x] `README.md` — Skills table counts + Version Highlights entry
- [x] `ROADMAP.md` — this v1.9.0 entry
- [x] `.claude-plugin/plugin.json` — 1.8.1 → 1.9.0

### Phase 4 — Per-country threshold calibration (Option B hybrid)
- [x] `references/thresholds-{us,japan,taiwan,korea,china}.md` (5 new
  files, consistent 8-section template) — per-country inflation target,
  NAIRU, r* estimate, real-rate block status, structural regime notes,
  asset-class tilt calibration, primary-source URLs, native-language sources
- [x] `references/recalibration-protocol.md` — triggers, cadence,
  source tiers (A/B/C/D), native-language priority, escalation rules
- [x] SKILL.md Step 1 — per-country threshold-file routing + explicit
  "do NOT apply US thresholds to non-US countries" guardrail

### Phase 5 — Primary-source grounding audit (following domain-teams convention)
- [x] `research/grounding-v1.9.0.md` — **consolidated audit trail**
  (5 parallel native-language research agents, 2026-04-18). Fixed
  **19 🔴 + 16 ⚠️ corrections** across 5 countries (critical vintage
  errors in BOJ展望/JILPT NAIRU/Fed FAIT-retired/PBOC-CPI-target-
  reduced/KOSPI-concentration/TSMC-weight). 20-year trajectory
  research (2005-2026) per country. Includes JP integration decision
  (full native-language priority), fabrication-risk warnings
  (3 unverifiable citations removed).
- [x] Threshold files updated with "Grounding Status" blocks at top
  (per-file corrections audit + next-recalibration date).
- [x] Cheatsheet "Threshold provenance" updated with revised r*
  estimates (HLW 0.75%, LM 1.68%, not prior 1.42% / 2.15%).

### LSEG absorption summary

Pattern ported from Anthropic's `financial-services-plugins/partner-built/lseg/skills/macro-rates-monitor` (paid MCP → free FRED data):

| LSEG pattern | Our port |
|--------------|----------|
| 4-block dashboard (Macro / Curve / Real Rate / Swap) | 5-block (added IC + GIP + Asset Tilts) |
| Real-rate decomposition (nominal − breakeven) | US-only via T5YIE/T10YIE/DFII5/DFII10 |
| Signal labels (Expansion/Restrictive/etc.) | Added to Block 1 + glossary in cheatsheet |
| Yield-curve slope + shape | Preserved (Block 2) |
| Swap-spread block | **Deferred to v1.10.0+** (needs more FRED series) |

### Deferred to v1.10.0+
- JP JGBi real-rate (MoF XLS scraper) — **delivered in v1.10.0 as C+D+E multi-source**
- KR KTBi real-rate (needs BOK ECOS API key) — still deferred
- ISM PMI via FRED NAPM — still deferred (FRED relicensing not available)
- TW / KR local PMI (製造業採購經理人指數 / 기업경기실사) — still deferred
- Swap-spread block — **delivered in v1.10.0 as Treasury-SOFR 3M proxy**
- Full BOK ECOS API (lagging CI 후행지수 + 10K series; re-deferred from v1.9.0)

---

## v1.10.0 — PMI + JP real rates + swap spread (current)

**Scope**: Closes three data-coverage gaps from v1.9.0 deferred list —
ISM-substitute PMI in us-macro (OECD CLI proxy), full JP real-rate
support via C+D+E multi-source framework, and US swap-spread block
via Treasury-SOFR 3M proxy. `macro-regime-snapshot` Block 3 renamed
"Rate Stress Dashboard" to absorb the new JP real-rate and US
swap-spread sub-blocks.

### Phase 1 — us-macro `pmi` group (OECD CLI fallback)
- [x] `skills/us-macro/SKILL.md` — new `pmi` group section (single series
  USALOLITOAASTSAM, already fetched under `nowcast`; reused as PMI proxy
  with threshold documentation). ISM / S&P Global PMI removed from FRED
  in 2016 (St. Louis Fed blog citation in `references/us-macro-indicators.md`
  "PMI" section). USALOLITOAASTSAM counted once in the 31-series total.
- [x] `skills/us-macro/references/us-macro-indicators.md` — "PMI" section
  added with OECD CLI methodology + threshold framing (100 = long-run
  avg; ≥100.5 expansion, ≤99.5 contraction).

### Phase 2 — japan-macro `real-rates` group (C+D+E multi-source) + grounding note
- [x] `scripts/ecb_client.py` — new SDMX client for ECB long-term
  monthly ex-post real yields (M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA).
- [x] `scripts/boj_client.py` — extended for Tankan
  1Y/3Y/5Y expected inflation series.
- [x] `skills/japan-macro/SKILL.md` — new `real-rates` group + Step 3b
  (ECB fetch) + multi-source routing table (MoF snapshot anchor + ECB
  monthly + Tankan survey). Presets: 22 → 27; groups: 9 → 10.
- [x] `skills/japan-macro/references/indicators-japan-real-rates.md` —
  new reference; C+D+E framework documentation.
- [x] `research/grounding-v1.10.0.md` — primary-source vetting for 3 new
  data sources (MoF auction history / ECB SDMX / BOJ Tankan) +
  rejection rationale for JSDA (999.999 sentinel confirmed via probe) /
  JBTS paths.

### Phase 3 — us-macro `swap-spreads` group (T-SOFR 3M proxy)
- [x] `skills/us-macro/SKILL.md` — new `swap-spreads` group section
  (DGS3MO − SOFR30DAYAVG proxy). 14-group structure documented.
- [x] `skills/us-macro/references/us-macro-indicators.md` — "Swap Spread /
  Money-Market Stress" section added with post-LIBOR methodology
  explanation (FRED has no clean term swap series after LIBOR wind-down).

### Phase 4 — macro-regime-snapshot integration
- [x] `skills/macro-regime-snapshot/SKILL.md` — Block 1 PMI row per
  country (US fetched live; JP/TW/KR/CN URL-only references pending
  licensed access). Block 3 renamed "Rate Stress Dashboard" with
  JP real-rate sub-block (C+D+E output) and US swap-spread sub-block.
  Step numbering preserves existing 5-block output contract.
- [x] `skills/macro-regime-snapshot/references/investment-clock-cheatsheet.md`
  — Rate Stress Dashboard interpretation guide added.

### Phase 5 — Plugin-level sync
- [x] `skills/using-investing-toolkit/SKILL.md` — us-macro / japan-macro /
  macro-regime-snapshot rows bumped to v1.10.0 with new groups/blocks noted.
- [x] `README.md` — v1.10.0 Version Highlights entry + Skills table
  updates for 3 affected rows.
- [x] `ROADMAP.md` — this v1.10.0 entry; v1.9.0 de-marked as (current).
- [x] `.claude-plugin/plugin.json` — 1.9.0 → 1.10.0.

### Deferred to v1.11.0 (next major candidate)

- **Full MoF 連動係数 + QuantLib CPIBond YTM solver for daily JGBi
  real yield** — Bloomberg-grade ±5bp accuracy, 5-7 working days scope,
  dedicated PR with primary-source grounding audit. v1.10.0 ships the
  C+D+E multi-source anchor; v1.11.0 would upgrade to full indexation-
  ratio-adjusted YTM via QuantLib `CPIBond` class.

### Deferred to v1.11.x / v1.12.0 candidates (carried forward)

- **KR KTBi real-rate** — BOK ECOS API key required (free registration at
  ecos.bok.or.kr/api/#/AuthKeyApply); unlocks lagging CI 후행지수 +
  10K series concurrently
- **JP Jibun Bank PMI** — licensed S&P Global access needed for
  machine-readable feed (URL-only reference in v1.10.0 Block 1)
- **CN Caixin PMI via akshare** — mirror availability pending re-probe
  (2 presets removed in v1.6.0 after 8-month stale window)
- **TW + KR domestic PMI scrapers** — 製造業採購經理人指數 (中經院) /
  기업경기실사 (BOK); custom scraper per source
- **ISM PMI via FRED NAPM** — blocked by 2016 FRED delisting; awaits
  hypothetical relicensing

---

## v2.0.0 — Quantitative Layer (tentative)

**Scope**: Backtesting integration, factor models.

### Ideas
- [ ] Backtesting workflow (integrates with domain-teams:investing-team standards/backtesting-and-robustness-discipline.md)
- [ ] Factor exposure snapshot (Fama-French 5-factor)
- [ ] Alpha Vantage premium adapter (technical indicators)
- [ ] Portfolio optimizer (risk parity / Kelly allocation)
