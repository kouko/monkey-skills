# 実質金利系 / Real Rates (Japan)

Japan real-rate and expected-inflation indicators — v1.10.0 multi-source
framework (C + D + E). Part of `japan-macro` skill. See
`indicator-index.md` for full index, `thresholds-japan.md` for regime
signal thresholds.

---

## Why a multi-source framework

Free-tier primary sources cannot replicate a Bloomberg-style daily JGBi
breakeven series, but BOJ's own Outlook Report does not treat a single
market BEI as the definitive signal. Its「複合的な期待インフレ指標」は
market-implied (JGBi BEI) + 家計アンケート + Tankan 企業物価見通し +
QUICK 月次サーベイを組み合わせる (see BOJ 展望レポート
「II.B 物価情勢」 footnotes). v1.10.0 mirrors that composite approach
with three free primary-source paths:

| # | Path | Frequency | Authority | What it measures |
|---|------|-----------|-----------|------------------|
| C | MoF JGBi 落札利回り | quarterly (per re-issuance) | 財務省 | Official real yield at auction (単利, primary anchor) |
| D | ECB JP 10Y real yield | monthly | ECB (SDMX) | Ex-post real yield (nominal − realised CPI), NOT market BEI |
| E | BOJ Tankan 企業物価見通し | quarterly | 日本銀行 | Survey-based corporate inflation expectations, CPI-basis |

**Paths NOT used in v1.10.0** (with rationale, to prevent drift):

- **JSDA daily JGBi CSV** — probed 2026-04; yield fields masked `999.999`
  (JSDA publishes 単価 only). Cannot reconstruct yield without the MoF
  連動係数 + QuantLib YTM solver, which is v1.11.0 scope.
- **JBTS Breakeven** — free HTML page but 利用規約 prohibits
  複製・送信・再配信 (§利用条件).  Not compatible with automated fetch.
- **Bloomberg / LSEG** — paywalled, outside free-tier scope.

---

## C. MoF JGBi auction real yield / 財務省 物価連動国債 落札利回り

- **Data file**: `references/jgbi-auction-history.yml` (human-curated snapshot)
- **Source**: 財務省 国債入札結果 (
  https://www.mof.go.jp/jgbs/auction/calendar/nyusatsu/)
- **Unit / 単位**: Percent (%) — **単利 (simple yield)** per MoF disclosure
  convention (not 複利); do NOT rebadge as "YTM".
- **Frequency / 頻度**: Irregular, ~4 auctions / year (10-year JGBi
  re-issuance schedule).
- **Publication lag / 公表遅延**: Same day as auction (約 15:00 JST).
- **History**: 第1回 from 2004-03; fresh 10-year re-issuance resumed 2013
  after 2009-2013 暫停. Current on-the-run: 第30回 (first issued 2025-05).

**What it measures / 経済的意味**
(EN) The marginal real yield (募入最高利回り) accepted at each JGBi
auction. This is the official real-yield quote from the Japanese
sovereign issuer itself — the highest-authority primary source for
anchoring any JGBi real-yield model.
(JP) 物価連動国債 (元本が全国CPI除く生鮮食品に連動) の入札における
募入最高利回り。財務省による公式の実質利回りスポット。

**How to interpret / 解読方法**
- Trending **up** (e.g. 2024-05: -0.545% → 2025-08: +0.078%) →
  実質金利が引き締め方向; 金融政策の正常化進展を反映。
- **Trending down** → accommodative real policy; combine with Tankan
  inflation-outlook to separate real-rate compression vs. expected-
  inflation surprise.

**Market significance / 市場重要度**: ⭐⭐⭐⭐ (primary-source anchor)

**When to use / 使用場面**
- Validate monthly ECB ex-post series against quarterly auction spot.
- Primary-source reference point for the IC/GIP Block 4 real-rate
  judgement.
- v1.11.0 QuantLib YTM solver will calibrate against these auction
  prints.

**Japan-specific context / 日本固有の文脈**
JGBi was issued 2004-03–2008-08, paused 2009-2013 (BOJ/MoF 中止 after
GFC demand collapse), and relaunched 2013-10 under Abenomics. BOJ has
been a large on-balance-sheet holder throughout; secondary-market
liquidity is low vs. US TIPS, and BEI signals can compress in illiquid
windows. Always cross-check against Tankan 企業物価見通し (Path E) as
the survey-based anchor.

**Common pitfalls / よくある間違い**
- Labelling "単利 (simple yield)" as "YTM / 複利" — different
  conventions by ~1-2 bp at current yield levels.
- Treating JGBi secondary-market BEI as market-implied expected
  inflation. BOJ itself does not; use as one of multiple signals.
- Re-issuance months differ year-to-year; don't assume a fixed
  schedule.

---

## D. ECB Japan 10Y real yield / ECB 日本 10年実質利回り

- **Series code**: `M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA` (ECB dataset `FM`)
- **Fetcher**: `scripts/ecb_client.py`
- **Source**: European Central Bank Data Portal SDMX CSV endpoint
  (https://data-api.ecb.europa.eu/service/data/FM/...)
- **Unit / 単位**: Percent (%) — real yield, annualised.
- **Frequency / 頻度**: Monthly (period-average, P1M).
- **Publication lag / 公表遅延**: ~1-3 months (ECB re-publishes with CPI
  realisation lag — **ex-post**, not market-implied).
- **History**: From ~1999-01 (monthly).

**What it measures / 経済的意味**
(EN) ECB's ex-post real-yield reconstruction for the Japanese 10-year
benchmark: nominal 10Y yield **minus realised annual CPI**, averaged
over the period. This is **NOT** market-implied breakeven — ECB does
not publish a JGBi-derived market BEI; the "Real" flag here is on the
ex-post side.
(JP) 日本10年物の名目利回りから実現インフレ率を差し引いた事後実質
利回り。市場インプライドBEIではない。欧州中央銀行が国際比較用に計算・
公表している公式系列。

**How to interpret / 解読方法**
- Ex-post real yield **rises** → either nominal yields rose faster
  than realised CPI, or CPI rolled off (base-effect cliff). Read with
  Tankan 企業物価見通し (Path E) to triangulate ex-ante expectations.
- Ex-post real yield **falls** (more negative) → inflation surprise
  or BOJ accommodation vs. CPI realisation.

**Market significance / 市場重要度**: ⭐⭐⭐
Primary source at ECB authority tier, freely available, clean monthly
cadence. Only caveat is the ex-post construction — it tells you where
real yields have been, not where the market prices them today.

**When to use / 使用場面**
- Monthly update for IC/GIP Block 4 Japan real-rate signal.
- Time-series view vs. Tankan expectations (surprise decomposition).
- Cross-country comparison with ECB's US / EA equivalent series.

**Japan-specific context / 日本固有の文脈**
ECB values have been deeply negative through 2023-2024 (-2% to -3%
range) reflecting the combined effect of (a) BOJ YCC keeping nominal
low and (b) the post-2022 inflation spike lifting realised CPI.
As BOJ exits YCC (2024-03) and inflation moderates, the ex-post real
yield should compress toward / above zero — consistent with 2025
JGBi auction prints crossing the zero line.

**Common pitfalls / よくある間違い**
- **Calling this "market BEI"** — it is not. ECB does not publish a
  market-implied JPY breakeven series.
- Using the 1- to 3-month lag as a real-time signal. Pair with JGBi
  auction spot (Path C) for the most-recent anchor.
- Mixing this with US TIPS "real yield" which IS market-implied —
  different construction.

**Dependency note**: ECB dataset `FM` series are formally 欧州の monetary
financial statistics dataset that includes foreign benchmark bonds for
comparison.  Series remains stable across ECB SDMX releases since 2014.

---

## E. BOJ Tankan 企業物価見通し / Corporate Inflation Outlook

- **Series codes** (DB=`CO` in BOJ stat-search):
  - `TK99F0000204HCQ00000` — 1 year ahead (Outlook for General Prices, 1Y)
  - `TK99F0000205HCQ00000` — 3 years ahead (3Y)
  - `TK99F0000206HCQ00000` — 5 years ahead (5Y)
- **Fetcher**: `scripts/boj_client.py --tankan-price-outlook --horizons 1,3,5`
- **Source**: 日本銀行 短観 (Tankan, 全国企業短期経済観測調査)
- **Unit / 単位**: Percent (%) — average expected annual CPI-basis price
  change per responding enterprise.
- **Frequency / 頻度**: Quarterly (March, June, September, December).
- **Publication lag / 公表遅延**: ~1 week after survey quarter-end.
- **History**: Inflation-outlook section from 2014 Q1 (added as Tankan
  enhancement, per BOJ 2013-12 tankan reform announcement).

**What it measures / 経済的意味**
(EN) Survey-based average of corporate 1Y/3Y/5Y expected inflation
("General Prices" basis = CPI proxy, NOT output prices which have a
parallel 201/202/203 code set). Coverage: All Enterprises / All
industries, weighted simple mean. This is the survey-based anchor in
BOJ's composite inflation-expectation framework.
(JP) 短観「企業物価見通し」全規模合計・全産業の平均値 (一般物価ベース)。
日銀が複合期待インフレ指標の一要素として重視する survey-based anchor。

**How to interpret / 解読方法**
- **1Y** moving vs. BOJ 2% target → near-term inflation pass-through
  judgement. Above 2% with rising Tankan DI → demand-driven.
- **3Y / 5Y** → longer-dated inflation anchoring. Post-2022 break
  where JP 5Y Tankan lifted from 1.1% → 2.5% region is a regime
  signal for the "deflationary mindset exit".
- Divergence between Tankan and ECB ex-post real-yield trajectory =
  expectation surprise (market priced differently than corporates).

**Market significance / 市場重要度**: ⭐⭐⭐⭐
BOJ publicly cites Tankan 企業物価見通し in every Outlook Report as a
primary inflation-expectation signal (alongside ESP forecaster survey
and household expectation survey). Used by the BOJ Policy Board in
rate decisions.

**When to use / 使用場面**
- IC/GIP Block 4 expected-inflation side of the real-rate
  decomposition.
- Regime-shift detection: Tankan 5Y crossing 2% sustainably = sign
  of anchored inflation regime.
- Cross-check against 家計 1年先期待インフレ (意識調査) when doing
  full BOJ-methodology replication.

**Japan-specific context / 日本固有の文脈**
Latest observation (2026 Q1): 1Y = 2.6% / 3Y = 2.5% / 5Y = 2.5%. This
reading is ~2.5 pp above the 2014-2020 average (≈0.8% across horizons),
confirming the post-2022 re-anchoring at / above the 2% target.
The survey has an upward bias relative to household / forecaster
surveys (enterprise managers live closer to wholesale price inputs,
which rose sharply 2022-2024) — cross-check with 家計 survey before
policy-path inference.

**Common pitfalls / よくある間違い**
- Confusing with the **201/202/203 codes** (Outlook for Output Prices,
  producer-price basis) — a different concept.
- Using the "large enterprise" subset (dimension `01`) as the
  headline — BOJ itself uses "all enterprises" / `00` in Outlook
  Report charts.
- Treating Tankan expectations as market-priced. They're survey-based
  and update only quarterly.

---

## Signal thresholds (see `thresholds-japan.md` Real Rate Decomposition)

| Signal | Source | Thresholds (Block 4) | Rationale |
|--------|--------|---------------------|-----------|
| `real-10y-monthly` | ECB ex-post | `<0%` Accommodative / `0-1%` Neutral / `≥1%` Restrictive | Calibrated to BOJ r\* ≈ -0.25% (v1.9.0 grounding, BOJ WP24-J-09 + rev26j05) with ±1 pp band for ex-post vs. ex-ante wedge. |
| `real-10y-auction` | MoF JGBi | Validation anchor (not continuous signal) | Quarterly primary-source spot; used to sanity-check the monthly series. |
| `inflation-tankan-1y` | Tankan | `<1.5%` Below target / `1.5-2.5%` At target / `>2.5%` Overshoot | BOJ 2% target ±50 bp band. |
| `inflation-tankan-5y` | Tankan | `<1.5%` De-anchored low / `1.5-2.5%` Anchored / `>2.5%` De-anchored high | Long-dated anchor check. |

v1.10.0 treats the three paths as complementary, NOT a weighted composite
— IC/GIP diagnosis consumes them separately so the analyst can read
each primary-source signal before synthesising.

---

## v1.11.0 upgrade roadmap

- **MoF 連動係数 daily feed** — automated fetch of the daily
  inflation-linkage coefficient table (MoF 月次発行実績 XLS + daily CSV).
- **QuantLib JGBi YTM solver** — given daily 単価 (from JSDA CSV) +
  連動係数 + coupon, solve for real YTM at Bloomberg-grade ±5 bp.
- Adds **daily real yield** as a fourth signal alongside the quarterly
  anchor, monthly ECB, and quarterly Tankan paths here.
- Standalone PR with its own primary-source grounding audit (MoF 仕組み
  書 + JGBi 応募要領 → 単利 / 複利 / 連動係数 semantics fully anchored).
