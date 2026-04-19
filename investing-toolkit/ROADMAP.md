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

## v1.10.0 — PMI + JP real rates + swap spread

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

### Deferred → partially delivered in v1.11.0

- CN Caixin PMI via akshare (eastmoney-backed) + NBS PMI via `nbs_client`
  **delivered** in v1.11.0 `china-macro.pmi` group (5 presets)
- TW Manufacturing PMI + NMI **delivered** in v1.11.0 `taiwan-macro.pmi`
  group via NDC 政府資料開放 dataset 6100 (free-tier access discovered
  during APAC probe)

---

## v1.16.2 — mops_fetch required-param validation (current)

**Scope**: User-reported bug fix. `mops_fetch(action=..., ticker=...)` without
required year/month/season args used to crash with the cryptic Python error
`unsupported format string passed to NoneType.__format__` (f-string format
spec on None value from `types.SimpleNamespace` defaulting). Now returns a
friendly `{"error": "action '...' requires: --year, --month. ...", "action":
"..."}` dict.

### Commits
- [x] Commit 1: `scripts/mops_client.py` — `_REQUIRED_PARAMS` table +
      `_validate_action_params()` helper called at top of `_run_action()`;
      updated `mops_fetch` docstring with explicit `[required, params]`
      notation per action.
- [x] Commit 2: `tests/test_mcp_equivalence_auto.py` — 6 parametrized
      negative-case regression tests.
- [x] Commit 3: plugin sync 1.16.1 → 1.16.2.

### Root cause

`mops_client.py` is the only dispatcher-pattern MCP client in the plugin (16
actions funneled through `_run_action` via `types.SimpleNamespace`). All
other clients (twse/edinet/sec_edgar/etc.) either register separate tools per
action (JSONSchema `required` enforces params) or raise `SystemExit`
per-branch before any None-on-format. mops lacked top-level validation.

### Deferred
- Split `mops_fetch` into 16 individual MCP tools (would eliminate the
  dispatcher vulnerability architecturally) — ~2.2K token overhead, rejected
  for budget reasons in v1.14.0 plan review. Revisit if Anthropic raises
  session token budget OR core/extras MCP split ships.

---

## v1.16.1 — Cowork sandbox retrospective + maintenance automation

**Scope**: v1.14.0 premise failure correction + CI automation to make
keeping MCP cheap.

### Retrospective (confirmed empirically 2026-04-19)

Plugin-installed stdio MCP servers run INSIDE the Claude Desktop
Cowork sandbox, subject to the same URL allowlist as plugin-subprocess
scripts. v1.14.0 shipped MCP infrastructure believing MCP spawned
outside the sandbox — this was wrong. Anthropic's own plugins
(knowledge-work-plugins, financial-services-plugins) exclusively use
remote `type: http` MCP for exactly this reason.

**Decision**: keep MCP infrastructure (works fine in Code CLI,
preserves optionality for future remote-MCP pivot, rollback cost >
keeping cost), correct all documentation, add CI automation to reduce
recurring maintenance cost.

### Commits
- [x] Commit 1: `docs/mcp-setup.md` — honest retrospective at top;
      "What actually works where" table; token/latency trade-off;
      opt-out guidance.
- [x] Commit 2: 9 SKILL.md blockquotes changed from "MCP-prefer" to
      neutral dual-mode + explicit Cowork caveat; per-skill tool
      enumeration moved to `docs/mcp-setup.md` (single authoritative
      catalog).
- [x] Commit 3: `tests/test_mcp_equivalence_auto.py` — parameterized
      MCP↔CLI drift guard; 14 fixtures covering all public-tier
      clients. Runtime ~6 s warm / 30 s cold.
- [x] Commit 4: `tests/test_skill_md_sync.py` (canonical-phrase check
      + stale-tool-ref check) + `tools/validate_mcp_tools.py`
      (schema + description linter, all 29 tools pass).
- [x] Commit 5: plugin.json / README / ROADMAP sync 1.16.0 → 1.16.1.

### Maintenance cost reduction (estimated)

Before: ~3.5-6.5 h / 6 months for MCP maintenance (drift checks,
SKILL.md sync, scaffolding). After: <1 h / 6 months. Break-even on
the ~1 day automation investment: ~2 months.

### Known open items (deferred to v1.16.x+)

- MCP equivalence coverage expansion (14 → 18+ fixtures):
  sec_edgar_facts, sec_edgar_narrative, finmind, boj_fetch (generic),
  ecb_series. All require either API keys or stable public fixtures.
- `tools/scaffold_mcp_tool.py` for new-script bootstrapping (deferred
  — save ~15 min per future script, current ROI uncertain).
- Nightly URL probe for setup.sh external deps (uv install URL,
  Homebrew formula) — current `Scraper dependency freshness` CI
  partially covers this already.

### Long-term: would need to pivot strategy for real Cowork support
- Anthropic allowlists our data-source URLs (no ETA).
- We host investing-toolkit as remote-HTTP MCP (requires $5-20/mo
  infra, privacy consideration, out of scope for solo OSS plugin).

---

## v1.16.0 — Complete MCP tool surface

**Scope**: Wrap the 8 remaining data-fetching scripts deferred from
v1.14.0 plan so Cowork users are not blocked on macro / regime work
(`/invest-macro`, `macro-regime-snapshot`, country-macro skills).

### Phase 1 — Macro register_mcp_tools (Commits 1-3)
- [x] `boj_client.py`: boj_fetch + boj_tankan_inflation_outlook
- [x] `ecb_client.py`: ecb_series
- [x] `estat_client.py`: estat_fetch + estat_search
- [x] `cbc_client.py`: cbc_fetch
- [x] `dgbas_client.py`: dgbas_fetch
- [x] `ndc_client.py`: ndc_fetch
- [x] `statgov_client.py`: statgov_fetch
- [x] `fdr_client.py`: fdr_fetch

### Phase 2 — Central registry + plugin sync (Commits 4-5)
- [x] `servers/mcp_server.py`: 10 → 18 clients, 19 → 29 tools
- [x] Contract tests: `tools=29`, expected names set extended
- [x] Plugin sync 1.15.0 → 1.16.0 (auto-invalidates .mcp_ready marker)

### Deliberately NOT wrapped
- `ta_client.py` — transforms local OHLCV into RSI/MACD/Bollinger/ATR/SMA;
  not a data fetcher. Compose via MCP `yfinance_history` →
  local subprocess `ta_client.py` if needed from Cowork.

### Deferred to v1.16.x+ (budget review trigger)
- Session token cost 4.4K now (29 × ~150 tok); v1.14.0 plan flagged
  5K as split threshold. Next additions (dcf-jp, korea-stock-snapshot,
  sector-etf) may push over → investigate core/extras MCP server split.

---

## v1.15.0 — Japan individual-stock skill

**Scope**: Path γ stacked-PR carry-over from v1.13.0 — Japan joins US + TW
as the third market with a dedicated individual-stock data skill. Primary-
source Tier A (EDINET + TDnet + yfinance .T) with dual-mode tier routing
(Tier A if EDINET_API_KEY set, Tier 2 yfinance financials fallback else).

### Phase 1 — Data adapters (Commits 1-3)
- [x] `scripts/edinet_client.py` — EDINET v2 REST API; 7 forms
      (120/140/160/180/220/350 + 訂正版); type=5 CSV parsed into
      canonical key_metrics; ticker→EDINET code via public ZIP; PDL 1.0
- [x] `scripts/tdnet_client.py` — Yanoshin WEB-API index wrapper;
      決算短信 / 業績予想 / 株主総会 / 役員 / 自己株 classifier
- [x] `scripts/yfinance_client.py --action financials` — Tier 2 BS/PL/CF
      fallback; data_tier provenance label; Toyota FY2025 equivalence
      check vs EDINET passes (revenue/operating/net/OCF match exactly)

### Phase 2 — Skill + orchestration (Commits 4-6)
- [x] `skills/japan-stock-snapshot/SKILL.md` — dual-mode routing;
      upgrade-path footer for Tier 2 users; known gaps documented
- [x] `sync-scripts.sh` wires edinet/tdnet/yfinance into
      japan-stock-snapshot + investment-memo-writer + dcf-valuation
- [x] `servers/mcp_server.py` registers 10 clients × 19 tools
      (+4 edinet, +1 tdnet, +1 yfinance_financials); contract tests
      updated + all 3 pass
- [x] `investment-memo-writer` Phase 1 JP branch routes 4-digit tickers
      through EDINET (Tier A) or yfinance financials (Tier 2) + TDnet
- [x] Plugin-level sync 1.14.0 → 1.15.0

### Known gaps deferred to v1.15.x
- **信用取引残高 / 空売り per-stock** — J-Quants Standard (paid) only
- **daily 投資部門別 per-stock flow** — genuinely unavailable free
  (JPX publishes weekly aggregate only)
- **EPS via EDINET** — alias coverage incomplete for IFRS
  KeyFinancialData namespace; yfinance `.T` info fills gap
- **Narrative Item extraction from EDINET iXBRL** — CSV is
  table-only; narrative 事業等のリスク / MD&A text lives in iXBRL 本文
- **pre-April-2024 historical filings** — type=5 CSV was added
  2024-04; older filings need iXBRL parser

### Deferred to v1.16.0+ candidates
- J-Quants free tier `/listed/info` for 33業種 (if we need JPX
  industry classification vs yfinance GICS sector)
- `dcf-valuation` JP branch (auto-source EDINET key_metrics)
- Korea individual-stock skill (KRX + DART)
- China individual-stock skill (SZSE + eastmoney)

---

## v1.14.0 — MCP migration infrastructure

**Scope**: Expose all 8 data-fetch scripts as 13 MCP tools, bundled at
plugin level. Unblocks Claude Desktop Cowork users (previously all
`uv run scripts/...` calls blocked by Cowork sandbox URL allowlist);
Claude Code CLI keeps working via the identical-JSON dual-mode path.

### Phase 1 — Per-script register_mcp_tools()
- [x] Commit 1: `yfinance_client.py` / `akshare_client.py` /
      `nbs_client.py` (3 HIGH-risk scripts confirmed failing in sandbox)
- [x] Commit 2: `fred_client.py` / `sec_edgar_client.py` /
      `mops_client.py` / `twse_openapi_client.py` / `finmind_client.py`
      (5 Pattern C scripts)
- [x] 13 tools total; dispatch pattern used for mops (16 actions) and
      twse (10 actions) to keep session token cost manageable.

### Phase 2 — servers/ central registry + entry chain
- [x] Commit 3: `servers/mcp_server.py` + `--self-check` flag for
      setup-time dep warming. Follows official plugins-reference layout
      convention (`servers/` not `scripts/`).
- [x] Commit 4: `.mcp.json` + `servers/mcp_bootstrap.sh` +
      `servers/mcp_wrapper.py` + `servers/setup.sh`. V2 silent-auto
      design (pre-flight P3 probe 2026-04-19 confirmed Claude Desktop
      MCP handshake timeout cliff = 60 s, so synchronous bootstrap
      would fail on first install; background setup + stdlib wrapper
      keeps handshake under the limit).

### Phase 3 — Documentation + tests
- [x] Commit 5: 8 SKILL.md files carry MCP-aware prose blockquote
      (prefer MCP tools if registered, subprocess commands remain
      canonical fallback).
- [x] Commit 6: `docs/mcp-setup.md` — 3 install paths (CLI / Cowork
      Team private fork / Cowork Pro/Max limited) + troubleshooting.
- [x] Commit 7: `tests/test_mcp_contract.py` — 3 contract tests
      (self-check shape, stdio handshake exposes 13 tools, FRED
      MCP=CLI equivalence).

### Deferred to v1.15.0+
- Japan individual stock skill (Path γ carry-over from v1.13.0 plan).
- Wrap remaining 9 macro / reference scripts (boj / ecb / estat /
  cbc / dgbas / ndc / statgov / fdr / ta) as MCP demand surfaces.
- `.mcpb` Desktop Extension packaging (Chat-tab users only, niche).
- Remote HTTP MCP hosting (privacy + cost concerns).

---

## v1.13.0 — Individual stock fundamentals (US + TW)

**Scope**: Closes Pattern C NVDA demo 4 data gaps for US + TW markets.
Primary-source Tier A across all new fetchers.

### Phase 1 — SEC EDGAR (US)
- [x] `scripts/sec_edgar_client.py` (7 form types, XBRL + narrative)
- [x] `us-stock-snapshot` SKILL.md integration
- [x] `references/sec-edgar-guide.md` (new reference doc)

### Phase 2 — MOPS (TW 公司揭露)
- [x] `scripts/mops_client.py` (16 endpoints)
- [x] MOPS JSON API confirmed via 2-round probe (zero-auth, no cookie)
- [x] Historical depth: IFRS 財報 ROC 102-115 (13 yr); 重大訊息 ROC 85+ (30 yr)

### Phase 3 — TWSE OpenAPI (TW 交易)
- [x] `scripts/twse_openapi_client.py` (日行情 / 融資融券 / 三大法人
      snapshot / 產業 EPS / 除權息日曆)
- [x] TPEx bonus endpoint added (tpex-margin-balance)
- [x] Known gaps documented (daily T86 per-stock flow not in OpenAPI)

### Phase 4 — taiwan-stock-snapshot rebuild
- [x] SKILL.md rewrite: MOPS + TWSE OpenAPI Tier 1 primary; FinMind
      Tier 2 auto-fallback (Pattern A+B combo)
- [x] `references/data-sources.md` new reference doc (10 sections)

### Phase 5 — DCF + memo-writer integration
- [x] `dcf-valuation` SKILL.md — financial statements now available
- [x] `investment-memo-writer` Phase 1 — SEC EDGAR + MOPS + TWSE OpenAPI
      commands added

### Phase 6 — Plugin-level sync
- [x] plugin.json 1.12.0 → 1.13.0
- [x] README v1.13.0 Version Highlights prepended
- [x] ROADMAP this entry; v1.12.0 de-marked as (current)

### Deferred to v1.14.0+ candidates

- **v1.14.0 (stacked)**: `japan-stock-snapshot` skill (yfinance .T +
  evaluate EDINET XBRL for primary-source-grade)
- **v1.13.x patches**: analyst consensus (finnhub / alphavantage),
  market-wide MOPS t146sb10 broader coverage
- **v1.15.0+**: `korea-stock-snapshot` (FDR + DART), `china-stock-snapshot`
  (akshare extended)
- **軸 3 phase-split** (from v1.12.0 Pattern C UX) — if 軸 1+2 proves
  insufficient in practice
- **Full 5-parallel grounding re-audit** (~2026-Q3)

---

## v1.12.0 — Pattern C UX (file-write + visibility)

**Scope**: Fixes 3 UX issues exposed by v1.11.0 NVDA Pattern C demo:
(1) no file-write default (2500-word memo lived only in chat
transcript); (2) skill drift — investing-team reference should route
to research-team; (3) ~2 min agent silence during Phase 3 dispatch.

Cross-plugin: investing-toolkit (1.11.0 → 1.12.0) + domain-teams
(5.1.0 → 5.2.0).

### Phase 1 — investment-memo-writer file-write + narration + target fix
- [x] Phase 5 rewrite — default path
  `$CLAUDE_PLUGIN_DATA/memos/{YYYY-MM-DD}_{ticker}_{mode}_memo.md`
  (deep vs quick mode-separated filenames; overwrite on same-mode
  re-run); Obsidian mode auto-detect (env var → vault probe → vault
  CLAUDE.md folder convention → obsidian:obsidian-markdown skill)
- [x] Chat delivery — executive summary + gate verdicts + file link
  only; full memo stays in file (not repeated in chat)
- [x] Phase 3 target fix — `domain-teams:investing-team` →
  `domain-teams:research-team` (historical note preserved)
- [x] Narration Convention (軸 1) — pre-dispatch expectation-setting
  pattern documented

### Phase 2 — domain-teams Visibility Convention (v5.2.0)
- [x] `skill-team/SKILL.md` — new §Visibility Convention requiring
  `TaskUpdate` emission at 3 levels: phase transitions, milestones,
  heartbeat (≤60s max silence)
- [x] 7 workflow skills gain compliance block: research-team /
  code-team / design-team / docs-team / devops-team / qa-team /
  planning-team
- [x] Probabilistic vs structural guarantee trade-off documented;
  phase-split architecture (軸 3) deferred to v5.3.0+

### Phase 3 — Plugin-level sync
- [x] `investing-toolkit/.claude-plugin/plugin.json` — 1.11.0 → 1.12.0
- [x] `domain-teams/.claude-plugin/plugin.json` — 5.1.0 → 5.2.0
- [x] `investing-toolkit/README.md` — v1.12.0 Version Highlights
  prepended
- [x] `ROADMAP.md` — this v1.12.0 entry; v1.11.0 de-marked as (current)

### Deferred to v1.13.0+ candidates

- **軸 3 phase-split orchestration** — if 軸 1+2 prove insufficient
  in practice (structural guarantee for 60s max silence at cost of
  context-fragmentation between dispatches)
- **File-write convention extension** — apply file-persistence pattern
  to `stock-screener`, `dcf-valuation`, `invest-portfolio` outputs
- **Sector ETF cross-plugin workflow** — needs japan / korea /
  china stock-snapshot skills first (per v1.11.0 sector ETF audit)
- **KR KTBi via BOK ECOS API key** — carried from v1.9.0+ deferred
- **Full 5-parallel grounding re-audit** — target ~2026-Q3
- **JGBi YTM solver** — REJECTED per v1.11.0 brainstorm (architectural
  consistency; would make JP the only bond-math country among 5
  country-macro skills)

---

## v1.11.0 — Cross-country consistency refresh

**Scope**: Addresses v1.10.0 PMI asymmetry (1 / 5 countries live) +
grounding vintage drift (v1.9.0 baseline 2026-04-18 needed 2026-Q2
refresh for CN Work Report + BOJ 2026-01/03 holds). Closes Block 1
PMI row gap for CN + TW via free-tier sources; formalises JP + KR
URL-only status (both S&P Global licensed, no free path).

### Phase 1 — china-macro `pmi` group (Caixin + NBS)
- [x] `scripts/akshare_client.py` — `caixin-mfg-pmi` + `caixin-svc-pmi`
  via `index_pmi_man_cx` / `index_pmi_ser_cx` (eastmoney-backed; fresh
  endpoint distinct from 2026-04-18 excluded investing.com route)
- [x] `china-macro` new `pmi` group: 5 presets (2 Caixin via akshare +
  3 NBS `pmi-manufacturing` / `pmi-non-manufacturing` / `pmi-composite`
  via existing nbs_client, regrouped from legacy `sentiment`)
- [x] `references/indicators-pmi.md` — NBS ≥3000 incl. SOE vs Caixin ~430
  SME/民企 methodology contrast + 1-2mo Caixin-leads-NBS lag around
  turning points + 2015/2020-02/2022-04/2024-25 regime-shift sampling
- [x] Indicator count 34 → 36; akshare preset count 6 → 8

### Phase 2 — APAC PMI probes (TW live; JP/KR URL-only)
- [x] `taiwan-macro` new `pmi` group — `pmi-mfg` + `pmi-nmi` via
  `ndc_client.py` dedicated CSV endpoint (NDC 政府資料開放平臺 dataset
  6100, 政府資料開放授權條款第1版 CC BY-equivalent). Indicator count
  30 → 32. New `references/indicators-pmi.md`.
- [x] `japan-macro` — "PMI (URL reference only)" subsection added
  linking to S&P Global press releases; BOJ Tankan 業況判断DI noted
  as closest free sentiment proxy
- [x] `korea-macro` — "PMI (URL reference only)" subsection added
  linking to S&P Global Korea press release; CSI (K252) + ESI (K269)
  + business-cycle CI (K253/K254) noted as closest free proxies

### Phase 3 — CN + JP full grounding refresh (2026-Q2 vintage)
- [x] `thresholds-china.md` — 2026 Work Report GDP 4.5-5% range;
  LPR-1Y/5Y vintage refresh; 16 🔴 + 9 ⚠️ CN+JP corrections
- [x] `thresholds-japan.md` — BOJ held 0.75% 2026-01 + 2026-03;
  JILPT NAIRU refresh; Tankan 2026-Q1 vintage

### Phase 4 — US + TW + KR grounding delta addenda
- [x] `thresholds-us.md` — FOMC SEP long-run real r* 3.0 → 3.1%
- [x] `thresholds-taiwan.md` — CBC held 2.00% 2026-Q1
- [x] `thresholds-korea.md` — BOK 7-consecutive hold confirmation
- [x] 2 🔴 + 8 ⚠️ delta corrections across US/TW/KR

### Phase 5 — Consolidated audit trail
- [x] `skills/macro-regime-snapshot/research/grounding-v1.11.0.md`
  — 299-line consolidated audit trail covering all 5 countries
  (full CN + JP re-audit + US/TW/KR delta); 16 🔴 + 17 ⚠️ total

### Phase 6 — Plugin-level integration + sync
- [x] `skills/macro-regime-snapshot/SKILL.md` — Block 1 PMI row CN + TW
  promoted from N/A → live (citing preset names); Data Source
  Architecture section expanded with 5×9 cross-country coverage grid
  (Growth / Inflation / Policy rate / Yield curve / Real rate / PMI /
  Swap spread / FX / Equity). Consolidated into existing section per
  spec §3.6 Option X (replaces standalone coverage-matrix.md)
- [x] `skills/using-investing-toolkit/SKILL.md` — china-macro /
  taiwan-macro / macro-regime-snapshot rows bumped to v1.11.0
- [x] `README.md` — v1.11.0 Version Highlights prepended; Skills
  table updates
- [x] `ROADMAP.md` — this v1.11.0 entry
- [x] `.claude-plugin/plugin.json` — 1.10.0 → 1.11.0

### Deferred to v1.12.0+ candidates (carried forward)

- **KR KTBi real-rate via BOK ECOS API key** — free registration at
  ecos.bok.or.kr/api/#/AuthKeyApply; unlocks lagging CI 후행지수 +
  10K series concurrently (unchanged from v1.11.0 deferred)
- **JP au Jibun Bank / KR S&P Global Korea PMI licensed access** —
  both S&P Global licensed; no free-tier machine-readable path
  available; formalised as URL-only in v1.11.0
- **Full 5-parallel grounding re-audit (target ~2026-Q3)** — next
  full sweep on the cadence documented in `references/recalibration-
  protocol.md`
- **ISM PMI via FRED NAPM** — still blocked by 2016 FRED delisting;
  awaits hypothetical relicensing

### REJECTED — architecturally inconsistent

- **Full MoF 連動係数 + QuantLib CPIBond YTM solver for daily JGBi
  real yield** — originally deferred from v1.10.0 to v1.11.0 as "next
  major candidate". **Rejected during v1.11.0 brainstorming audit**:
  would make `japan-macro` the only bond-math country among the 5
  country-macro skills (US/JP/TW/KR/CN), violating the explicit
  "country-macro = pure data layer" discipline documented in
  `CLAUDE.md` Cross-Plugin Delegation Contract §3
  ("Data layer stays in toolkit, analysis layer stays in domain-teams").
  Bond-math solvers (YTM, duration-adjusted real-yield inversion) are
  an analysis-layer concern and belong in `domain-teams:investing-team`
  if pursued. v1.10.0 C+D+E multi-source anchor (ECB monthly ex-post +
  BOJ Tankan + MoF JGBi auction) is the permanent JP real-rate shape.
  Preserved here as a historical roadmap entry so the decision is
  discoverable.

---

## v2.0.0 — Quantitative Layer (tentative)

**Scope**: Backtesting integration, factor models.

### Ideas
- [ ] Backtesting workflow (integrates with domain-teams:investing-team standards/backtesting-and-robustness-discipline.md)
- [ ] Factor exposure snapshot (Fama-French 5-factor)
- [ ] Alpha Vantage premium adapter (technical indicators)
- [ ] Portfolio optimizer (risk parity / Kelly allocation)
