# Per-Market Disclosure-Period Granularity — US / JP / TW / KR / CN

Research date: 2026-07-24. Method: three parallel research agents, each searching
in the market's OWN language (JA for Japan, ZH-TW for Taiwan, KO/ZH-CN/EN for
Korea-China-US) over regulator and exchange primary sources (FSA/JPX, FSC/TWSE/
TPEx, SEC, 자본시장법, CSRC), plus one local probe of this repo's own period
classifier. Purpose: the KPI tearsheet (shipped 2.32.0) renders any period it is
given as one flat date-sorted column, which is wrong across granularities — and
"annual + quarterly" turned out to be a US-centric assumption that does not hold
in four of the five markets this toolkit supports.

## Bottom line

Period granularity is **not a global design choice — it is a per-market
disclosure regime**, and there is a **second axis nobody designs for**: whether
the filed number is a discrete single period or a year-to-date cumulative, which
also varies by market. Two structural facts fall out that simplify the design
(no market files a standalone Q4; three of five have no standalone Q2), and one
gap falls out that blocks Taiwan entirely: **this repo's period classifier
cannot represent a MONTHLY period at all** (probe below), and monthly revenue is
Taiwan's headline mandatory series.

## The granularity matrix

| Market | Monthly | Quarterly | Half-year | Annual | Filed value: discrete or cumulative |
|---|---|---|---|---|---|
| **US** | ✗ (voluntary, sector-specific: retail same-store sales, airline traffic, auto units) | Q1–Q3 (10-Q); Q4 absorbed into 10-K | ✗ | ✅ 10-K | **BOTH natively** — the 10-Q income statement carries "Three Months Ended" AND "Nine Months Ended" columns side by side |
| **JP** | ~8% of listed names, voluntary (consumer retail / apparel / food / restaurant chains) | Q1/Q3 only, via 四半期決算短信 — **exchange rule (TSE 上場規程404条), no longer law**; auditor review now 原則任意 | ✅ **半期報告書** — since 2024 the ONLY legally mandated interim filing (FIEA, 3 months after H1-end) | ✅ 有価証券報告書 | **CUMULATIVE only** (累計期間) for J-GAAP filers; discrete 3-month figures are **derived by subtraction** (四季報オンライン does exactly this). IFRS filers under 作成基準5条1/2項 must also disclose 3か月情報 |
| **TW** | ✅ **MANDATORY** — 證交法 §36, by the 10th of each month, consolidated basis, self-reported/unaudited (自結數) | Q1–Q3, each 45 days after quarter-end; **no standalone Q4** | ✗ | ✅ 年報, 75–90 days depending on company size | **BOTH natively** — the IFRS 期中財務報告 income statement shows 當季 and 累計 columns side by side with prior-year comparatives |
| **KR** | ✗ | 분기보고서 covers Q1 (3mo) and through-Q3 (9mo cumulative) only; no standalone Q2/Q4 | ✅ 반기보고서 (45 days) | ✅ 사업보고서 (90 days) | Q1 discrete = cumulative trivially; **Q3 cumulative-only** → discrete Q3 must be derived (9mo − 6mo) |
| **CN** | ✗ (NEV/auto makers and some developers publish monthly sales voluntarily — sector practice, not a CSRC periodic-reporting rule) | 一季报 + 三季报; no standalone Q2/Q4 | ✅ 半年报 (by Aug 31) | ✅ 年报, audited (by Apr 30) | **CUMULATIVE only** (年初至报告期末) per CSRC 编报规则第13号; balance sheet is point-in-time. Discrete quarter must be derived |

### Three cross-market regularities

1. **No market files a standalone Q4.** All five absorb it into the annual
   report. A "FY column adjacent to a confusing Q4 column" is therefore not a
   real-world scenario — it only appeared in our own hand-fed demo.
2. **Q2 does not exist standalone in JP / KR / CN** — subsumed by the half-year
   filing. Only US and TW have a full Q1–Q3 quarterly series.
3. **Half-year is a first-class period in JP / KR / CN and absent in US / TW.**
   In Japan it is now the *only* legally mandated interim filing.

## The second axis: discrete vs cumulative

The filed number for a "quarter" is not the same object across markets:

- **Natively both** (US, TW): the filing itself carries the discrete-period
  column and the YTD-cumulative column — ingest both, derive nothing.
- **Cumulative only** (JP J-GAAP, CN, KR-through-Q3): the discrete quarter is a
  DERIVED figure (this period's cumulative − prior period's cumulative). Vendors
  do this derivation themselves; the regulator never publishes it.

Consequence for any store: a "Q3 value" is ambiguous until you know which axis
it sits on, and a market-blind ingest that assumes discrete will silently record
a 9-month figure as a 3-month one.

## What this repo already gets right

The store's period identity is the **raw `(period_start, period_end)` pair**
(decided in `docs/loom/specs/2026-07-20-kpi-observation-history.md`, the
observation-history brief), so
a cumulative Q3 (`2024-01-01 → 2024-09-30`) and a discrete Q3
(`2024-07-01 → 2024-09-30`) are already DIFFERENT periods with different
`period_axis_key`s (`2024-09-30|q3` vs `2024-09-30|q1`) — verified by probe.
The label-blind date-pair identity holds up under the hardest cross-market case
without modification. What is missing is not the identity; it is (a) sub-quarter
spans and (b) telling the reader which axis a column is on.

## The blocking gap: monthly periods have no identity (probe, 2026-07-24)

`_qtrs` (`investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py`) returns a
span length in quarters, refusing anything outside 1–4. Probed directly:

| Period | `_qtrs` | resulting `period_axis_key` |
|---|---|---|
| TW monthly revenue 2024-01-01 → 01-31 (30d span) | `None` | `null` |
| TW monthly revenue 2024-02-01 → 02-29 (28d span) | `None` | `null` |
| discrete Q3 (3mo) | `1` | `2024-09-30\|q1` |
| cumulative Q3 (9mo) | `3` | `2024-09-30\|q3` |
| half-year H1 (6mo) | `2` | `2024-06-30\|q2` |

A monthly period is therefore **unclassifiable**, its axis key is null, and per
the shipped null-key rule (2.32.0 whole-branch fix: null keys never merge —
`tearsheet_format.py`'s `id(period)` fallback) every monthly point renders as its
own isolated column that **cannot align across KPIs**. The blast radius is the
cross-KPI union, not one row: a year of monthly data for N KPIs yields 12 × N
columns where a working classifier would yield 12 — every KPI's January sits in
its own column instead of sharing one. This is a data-model gap, not a rendering
preference — and Taiwan's monthly revenue is
a headline, actively-ranked series in local tooling (Goodinfo ranks 單月營收年增率
and 累計營收年增率 market-wide), not a footnote.

## How shipped products separate granularities (layout survey, same date)

A companion search (EN + JA, 2026-07-24) asked how shipped products present
quarterly and annual data together in one compact company view. The answer was
unanimous: **they don't mix them.**

- **US terminals** — stockanalysis.com exposes an explicit `Annual | Quarterly |
  TTM` toggle; selecting Quarterly shows only quarters, flat, newest-left, with
  no FY rows interleaved and no visual year-grouping. Macrotrends follows the
  same pattern (separate annual/quarterly pages, never one merged table), as
  does TIKR per its own explainer.
- **JP** — 四季報's dense 業績欄 carries **annual rows only** (2 actual + 2
  forecast years) plus one interim row; quarters live on a **separate screen** in
  四季報オンライン. Its row order is by **type priority** (本決算 → 中間 → 四半期),
  not by date. 株探's 成長性 tab is likewise a dedicated quarterly-only view.
  (The 業績欄 row-composition detail rests on a practitioner blog, not a Toyo
  Keizai primary spec — lower source tier than the rest of this section.)
- **No surveyed product ships quarters-grouped-under-a-year** with a spanning
  header — the "obvious" fix had no shipped example in either market, within
  this survey's single-round scope (see caveat below).
- **Derived columns that ARE standard**: QoQ / YoY comparisons (near-universal
  both markets — Koyfin's growth-rate documentation is the citation for this
  bullet, not for the tab-separation claim above); TTM/LTM as a distinct rolling
  column or toggle state (US convention — Japan has no standing equivalent term
  and uses 進捗率, progress against forecast, instead).
- **A Q4 column can still exist in a product even though no market files one.**
  US vendors **derive** a discrete Q4 (annual − 9-month cumulative) and show it
  inside the quarterly view; the toggle then keeps it away from the annual view,
  so the two never sit adjacent. Japan historically did not even derive it —
  四季報 showed cumulative and annual only. So the regularity above ("no market
  files a standalone Q4") governs INGEST; a derived-Q4 lane is a separate,
  product-side choice. EN and JA differ in mechanism (UI separation vs never
  computing it) under a convergent outcome.

Scope caveat: this was a single-round search, not an exhaustive product census —
it establishes the convention's direction, not a complete market survey.

## Design implications (for the tearsheet arc's successor)

1. **Extend the classifier below one quarter** so monthly (and any sub-quarter)
   spans get a real identity — prerequisite for TW support, and it belongs in
   the STORE, not the formatter (2.32.0's Decision: the alignment identity is a
   store-owned canonical field, never a formatter recomputation).
2. **Granularity menus are per-market**, not a global annual/quarterly binary:
   US = annual + quarterly; TW = annual + quarterly + **monthly**; JP = annual +
   **half-year** + quarterly (cumulative for J-GAAP filers; IFRS filers under
   作成基準5条1/2項 also disclose discrete 3-month figures); KR/CN = annual +
   half-year + quarterly (cumulative).
3. **Surface the discrete/cumulative axis in the rendered output** — two columns
   that look alike but sit on different axes is exactly the silent-lie class this
   repo keeps getting bitten by.
4. **Do not build Q4/Q2 collision handling for INGEST** — those periods do not
   exist as filings in any of the five markets. A *derived* Q4 lane (annual −
   9-month cumulative, as US vendors compute) is a separate product decision; if
   it is ever built, it belongs beside the derived-discrete lane of implication
   3, not in the ingest path.
5. **Keep granularities in separate views** (a `--granularity` flag or distinct
   sections), never one date-sorted table — see §"How shipped products separate
   granularities" above for the surveyed evidence and its scope caveat.

## Honest gaps (flagged by the agents, not resolved)

- **JP**: the "~8% of listed names publish monthly sales" figure is the agent's
  own division of two separately sourced counts (313 tracked publishers vs
  ~3,850 listed), **not a published statistic**. 株探's cumulative-vs-discrete
  presentation could not be confirmed (fetch 403); the Yahoo!ファイナンス
  cumulative claim is secondary-source only.
- **TW**: the consolidated-basis claim for monthly revenue was cross-checked
  against two secondary sources but no single primary URL; whether 興櫃 monthly
  obligations match 上市/上櫃 line-by-line is **unconfirmed** (the comparison PDF
  fetched corrupted); the scope question for non-listed public companies is open;
  and the 證券發行人財務報告編製準則問答集 PDF backing the discrete-AND-cumulative
  column claim was read by the research agent but its URL did not survive as a
  resolvable link — the claim rests on that reading plus the TPEx statement
  listing, not on a citable primary document.
- **US**: the SEC's optional-semiannual proposal (Form 10-S, proposed
  2026-05-05, comments closed 2026-07-06) is **NOT adopted** — earliest adoption
  ~H1 2027, earliest election ~FY2028. Current quarterly regime stands; re-check
  before relying on this.
- **CN**: sector monthly sales bulletins are documented practice but were not
  verified as a codified nationwide rule.
- **Layout survey**: single-round search, not a product census; it establishes
  the direction of the convention (never mix granularities in one view), not
  that no counter-example exists anywhere.

## Sources

JP: [JPX FAQ 四半期決算短信](https://faq.jpx.co.jp/disclo/tse/web/knowledge7994.html) ·
[AMT 令和5年改正解説](https://www.amt-law.com/asset/pdf/bulletins10_pdf/231130.pdf) ·
[KPMG 2024 四半期開示](https://kpmg.com/jp/ja/insights/2024/05/accounting-ppa.html) ·
[四季報オンライン 四半期業績](https://help.toyokeizai.net/hc/ja/articles/46330201398681) ·
[kabubiz 月次売上](https://kabubiz.com/getuji/).
TW: [金管會法規 證交法§36](https://law.fsc.gov.tw/LawContent.aspx?id=FL007009) ·
[MOPS 公開資訊觀測站](https://mops.twse.com.tw) ·
[TPEx 財務報表查詢](https://www.tpex.org.tw/web/regular_emerging/statistics/financial/list.php) ·
[Goodinfo 月營收趨勢](https://goodinfo.tw/StockInfo/ShowSaleMonChart.asp?STOCK_ID=2455).
(The 證券發行人財務報告編製準則問答集 PDF backing the discrete/cumulative column
claim did not survive as a resolvable link — see the TW bullet in Honest gaps.)
US: [SEC 半年報提案 Federal Register](https://www.federalregister.gov/documents/2026/05/07/2026-09095/semiannual-reporting) ·
[SEC press release 2026-42](https://www.sec.gov/newsroom/press-releases/2026-42-sec-proposes-amendments-permit-optional-semiannual-reporting-public-companies) ·
[SEC EDGAR 10-Q 實例](https://www.sec.gov/Archives/edgar/data/51434/000005143420000042/ip-20200930.htm).
KR: [자본시장법 제160조](https://casenote.kr/%EB%B2%95%EB%A0%B9/%EC%9E%90%EB%B3%B8%EC%8B%9C%EC%9E%A5%EA%B3%BC_%EA%B8%88%EC%9C%B5%ED%88%AC%EC%9E%90%EC%97%85%EC%97%90_%EA%B4%80%ED%95%9C_%EB%B2%95%EB%A5%A0/%EC%A0%9C160%EC%A1%B0) ·
[Easylaw 정기공시](https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=1701&ccfNo=1&cciNo=3&cnpClsNo=1).
CN: [CSRC 编报规则第13号](http://www.csrc.gov.cn/csrc/c101954/c7547588/content.shtml).
Layout survey: [stockanalysis.com financials](https://stockanalysis.com/stocks/googl/financials/) ·
[Macrotrends](https://www.macrotrends.net/stocks/charts/META/meta-platforms/financial-statements) ·
[Koyfin growth rates](https://www.koyfin.com/help/how-to-look-at-growth-rates-on-koyfin/) (backs the QoQ/YoY bullet) ·
[TIKR explainer](https://www.tikr.com/blog/how-to-start-analyzing-stocks-even-if-youre-not-a-financial-expert) ·
[四季報オンライン 四半期業績](https://help.toyokeizai.net/hc/ja/articles/46330201398681) ·
[株探 成長性タブ](https://support.kabutan.jp/hc/ja/articles/16245921254553) ·
[四季報 業績欄の見方](https://okanenimatuwaru.com/sikihou-11/).
Local probe: `investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py` `_qtrs`
/ `_snap_month_end`, executed 2026-07-24 and independently reproduced by the
branch reviewer.
