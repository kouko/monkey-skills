---
title: "v1.11.0 cross-country consistency refresh"
date: 2026-04-19
refactor_version: v1.11.0
tags: [research, investing-toolkit, macro-regime-snapshot, grounding, cross-country]
---

# v1.11.0 Grounding Note — Cross-Country Consistency Refresh

## TL;DR

v1.11.0 pivoted from the originally-considered JGBi YTM solver to a
**cross-country consistency refresh** covering 5 countries. Scope:
(1) CN PMI closure via akshare Caixin + NBS, (2) APAC PMI formalization
(TW found free on data.gov.tw; JP/KR licensed URL-only), (3) Mixed
grounding refresh (CN/JP full, US/TW/KR delta), (4) v1.11.0 asymmetry
summary. Total: 16 🔴 + 17 ⚠️ findings across 5 countries. 0 new
scripts, 0 new dependencies (CN via existing `akshare_client` /
`nbs_client`; TW via existing `ndc_client` CSV extension).

## Scope and Methodology

### Why Mixed Strategy (not full 5-parallel)

v1.9.0 grounding audit (2026-04-18) used 5 parallel native-language
agents covering all 5 countries equally. For v1.11.0, we applied
**policy-change-velocity-based triage**:

- **Full re-audit** (CN + JP): Q1 2026 stances visibly shifting —
  CN 2026 Work Report regime + 赤字率 step-up + PPI turning positive;
  JP BOJ hold + 植田 caution speech + 実質賃金 turning positive
- **Delta addenda** (US + TW + KR): lower-velocity jurisdictions
  where Q1 2026 confirmation rather than rewriting is appropriate
  (US FOMC SEP tweak only; TW/KR policy-rate holds)

Result: same research budget, proportionate depth per country,
avoids over-auditing stable policy frameworks.

### Pattern Continuity

- `thresholds-*.md` Grounding Status section — append v1.11.0 block,
  preserve v1.9.0 corrections + v1.10.0 addendum (JP only) as
  historical record
- New primary-source URLs added to each file's "Sources" section
- `grounding-v1.11.0.md` (this file) consolidates audit trail

## CN Full Re-audit Findings

Drawn from Commit 3 (`6053f1f`) CN agent report; 7 🔴 + 5 ⚠️ corrections.

**Key structural shifts captured**:
1. 🔴 2026 政府工作報告 GDP target 4.5-5% range (first time sub-5%);
   previous v1.9.0 captured only "~5%"
2. 🔴 Deficit ratio ~4% (+1pp from 2025 ~3%) — explicit fiscal widening
3. 🔴 PPI turned positive 2026-03 (+0.5% YoY), first positive in
   41 months — ends long-running deflationary pipeline signal
4. 🔴 2025 full-year GDP 5.0% print (NBS final); v1.9.0 only had
   mid-year projection
5. 🔴 PBOC structural tools + 買斷式逆回購 (buyout reverse repo)
   replacing expected broad-based rate cut — policy mix shift
6. 🔴 远期售汇 reserve ratio set to 0 on 2026-03-02 (CNY defence
   signal easing as DXY softens)
7. 🔴 CEWC 2025-12-11 "适度宽松" language re-confirmed for 2026
   (structural continuity captured at v1.9.0 reaffirmed)
8. ⚠️ LPR tiered structure held (1Y / 5Y); 7D OMO 1.40% floor active
9. ⚠️ RRR cut cadence paused in Q1 2026 (prior expectation mis-calibrated)
10. ⚠️ CPI still flirting with 0 / slightly negative; 2% target
    rhetorically de-emphasized in favour of "合理區間"
11. ⚠️ Core CPI vs headline gap narrowed
12. ⚠️ Property-sector deep negative reconfirmed (2026-Q1 70城房價 continues decline)

**Structural frame unchanged (reaffirmed)**: 7D OMO 1.40%, LPR tiered,
RRR, "适度寬鬆" policy language, BIS r* 2-3% real, CSI300 tetrad,
property deep negative.

## JP Full Re-audit Findings

Drawn from Commit 3 (`6053f1f`) JP agent report; 7 🔴 + 4 ⚠️ corrections.

**Key structural shifts captured**:
1. 🔴 BOJ held 0.75% at 2026-01-23 + 2026-03-19 (8-1 dissent; 高田創
   voted for 1.0%); 野村 2026-Q2 hike scenario OIS probability
   60% → 33% after hold + 植田 caution speech
2. 🔴 10Y JGB nominal ~2.41-2.45% (28-year high), up from
   ~1.5% v1.9.0 snapshot — structural regime shift in JP term structure
3. 🔴 実質賃金 positive 2026-01 +1.4% / 2026-02 +1.9% (previously
   negative for most of 2024-2025)
4. 🔴 FY2026 BOJ 展望リポート core-CPI forecast revised 1.8% → 1.9%;
   GDP 0.7% → 1.0%
5. 🔴 2026 春闘 第3回集計 5.09% (vs 2025 最終 5.25% — slight moderation
   but still above 5% for 3rd consecutive year)
6. 🔴 BOJ 国債買入 reduction pace 緩和 2026-04+ (4000億 → 2000億/quarter)
7. 🔴 JP Investment Clock phase shifts to confirmed **Phase 2 Overheat**
   given real-wage positive + core-CPI ≥ 1.9% + JGB 10Y above historic
   natural range
8. ⚠️ BOJ 5年度展望 "2%持続的·安定的" achievement assessment tightened
9. ⚠️ Tankan 2026-Q1 大企業製造業 DI stronger than consensus
10. ⚠️ 輸入物価 JPY-base flipped back positive
11. ⚠️ 家計インフレ期待 UoM-style survey 2-3 year above 2%

**Implications**: JP real-rate interpretation needs JGB 2Y/10Y normalisation
lens rather than YCC-exit continuity lens; regime-snapshot Block 4
v1.10.0 C+D+E framework remains fit-for-purpose — no framework rebuild
needed, only calibration shift.

## US Delta Findings

From Commit 4 (`31f7ec8`) US delta; 2 🔴 + 2 ⚠️.

1. 🔴 FOMC 2026-03 SEP longer-run nominal 3.0% → 3.1% (real ~1.0% → ~1.1%);
   Powell press-conference rationale cited AI productivity / data-center
   buildout
2. 🔴 QT officially ended 2025-12-01 (Fed now in active reserve
   management regime, not runoff)
3. ⚠️ Powell term expires 2026-05-15; Warsh nomination stalled;
   acting-chair scenario now a live risk for regime-watchers
4. ⚠️ HLW r* ~1.0% latest (up from v1.9.0 ~0.75% estimate);
   Richmond Fed LM r* 1.68% unchanged

## TW Delta Findings

From Commit 4 (`31f7ec8`) TW delta; 0 🔴 + 3 ⚠️.

1. ⚠️ CBC 2026-03-19 held 2.00% unanimously; 2026 GDP projection 3.67%,
   CPI forecast < 2% — holds regime "neutral-hawkish with AI tailwind"
2. ⚠️ 景氣燈號 2026-02 = 紅燈 40 分 (third consecutive month red);
   AI buildout driving 加班工時 component → triggers 紅燈 scoring
3. ⚠️ TSMC TAIEX weight ~40-45% (range — official 2026-04-30 TWSE
   concentration disclosure not yet published; monitor for next update)

## KR Delta Findings

From Commit 4 (`31f7ec8`) KR delta; 0 🔴 + 3 ⚠️.

1. ⚠️ BOK 7-consecutive hold at 2.50% (v1.9.0 captured 5 holds; added
   2026-02-26 + 2026-04-10); 中東 supply-shock cited; 完화 deferred to 2026-H2
2. ⚠️ 삼성전자 + SK하이닉스 combined KOSPI weight ~40%+ sustained
   via HBM / AI rally (no single-source official print; aggregated)
3. ⚠️ 가계부채/GDP BIS 2025-Q1 89.5%; BOK Q3 2025 92.3% — downward
   trend confirmed (peaked 2022 ~104%)

## CN PMI Source Vetting (new v1.11.0 data)

Documented primary sources for newly-added CN `pmi` group.

### Caixin Manufacturing / Services PMI
- Published: S&P Global + Caixin partnership (since 2015; previously
  HSBC / Markit)
- Sample: ~430 SME / 民企 concentrated (vs NBS ≥3000 incl. SOE)
- Diffusion-index methodology (50 midpoint)
- akshare adapter: `index_pmi_man_cx` / `index_pmi_ser_cx`
  (eastmoney-backed)
- URL: https://www.pmi.spglobal.com/Public/Home/PressRelease/
  (press releases)

### NBS 官方 PMI (Manufacturing + Non-manufacturing + Composite)
- Authority: 国家统计局 (NBS)
- Sample: ≥3000 enterprises (vs Caixin ~430)
- Existing `nbs_client` primary-source path (preserved)
- URL: http://www.stats.gov.cn/sj/zxfb/ (monthly PMI release)

### Caixin vs NBS Methodology Delta (documented)
- Caixin leads NBS ~1-2 months at turning points (SME react faster
  than SOE-heavy sample)
- Sample composition: Caixin SME/民企; NBS includes SOEs
- Historical regime shifts where divergence was diagnostic:
  2015 匯改, 2020-02 COVID, 2022-04 Shanghai lockdown

## APAC PMI Probe Findings

### TW — Unexpected Free Access (added live preset)
- Source: 國發會 (NDC) via data.gov.tw dataset 6100
- License: 政府資料開放授權條款-第1版 (CC BY equivalent) — unambiguous
- Data: PMI + NMI monthly CSV
- Survey compiled by 中華經濟研究院 (CIER) on NDC commission
- Implementation: `ndc_client.py` extended with CSV fetch path; new
  taiwan-macro `pmi` group with `pmi-mfg` + `pmi-nmi` presets
- Coverage: PMI 2012-07+, NMI 2014-08+

### JP — Licensed, URL-only
- Source: S&P Global + au Jibun Bank partnership
- Licensed / paywalled; scraping prohibited per S&P Global ToS
- URL references added to `japan-macro/SKILL.md`
- Existing proxy signal: BOJ 短観 業況判断DI (already in `tankan` group)

### KR — Licensed, URL-only
- Source: S&P Global Korea Manufacturing PMI
- Licensed / paywalled
- URL references added to `korea-macro/SKILL.md`
- BOK ECOS BSI codes (K255 / K256 / K267) structurally different
  (quarterly ~15 rows; v1.8.1 catalogue deliberately skipped)
- Existing proxy signals: `consumer-sentiment` (K252),
  `economic-sentiment` (K269)

## Cross-country Asymmetry Summary (v1.11.0 state)

After v1.11.0:

| Signal              | US                 | JP                    | TW                    | KR                | CN                    |
|---------------------|--------------------|-----------------------|-----------------------|-------------------|-----------------------|
| Growth proxy        | ✅                 | ✅                    | ✅                    | ✅                | ✅                    |
| Inflation           | ✅                 | ✅                    | ✅                    | ✅                | ✅                    |
| Policy rate         | ✅                 | ✅                    | ✅                    | ✅                | ✅                    |
| Real-rate (market)  | ✅ daily           | ⚠️ partial C+D+E      | ❌ no linker          | ❌ deferred KTBi  | ❌ no linker          |
| **PMI**             | ✅ OECD CLI proxy  | ⚠️ URL-only (licensed) | **✅ live CIER via NDC** | ⚠️ URL-only (licensed) | **✅ live (Caixin + NBS)** |
| Swap spread         | ✅ T-SOFR 3M       | ❌                    | ❌                    | ❌                | ❌                    |

**v1.11.0 improvements vs v1.10.0**:
- PMI column: 1/5 → **3/5 live** (+CN, +TW)
- PMI asymmetry cut by 60%
- All 5 thresholds at 2026-Q2 vintage (not 2026-Q1)

**Remaining asymmetries (deferred)**:
- Real-rate: US unique-daily, JP partial, 3 countries N/A —
  structural, not closable
- Swap spread: US-only by design (global USD funding market signal)
- JP/KR PMI: licensed (would require paid S&P Global feed)
- KR KTBi: ECOS API key barrier
- Full 5-parallel grounding re-audit: targeted ~2026-Q3

## Primary-Source URLs (consolidated)

### CN
- 国家统计局 CPI / PPI: http://www.stats.gov.cn/sj/zxfb/
- PBOC: http://www.pbc.gov.cn/
- 2026 政府工作報告: https://www.gov.cn/yaowen/liebiao/202603/
- CEWC 2025-12-11: https://www.gov.cn/yaowen/liebiao/202512/

### JP
- 日本銀行: https://www.boj.or.jp/
- 財務省: https://www.mof.go.jp/
- 厚生労働省 毎月勤労統計: https://www.mhlw.go.jp/
- JILPT 春闘: https://www.jil.go.jp/
- BOJ 2026-01 展望レポート: https://www.boj.or.jp/mopo/outlook/

### US
- FRED: https://fred.stlouisfed.org/
- FOMC SEP: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- NY Fed Liberty Street HLW: https://libertystreeteconomics.newyorkfed.org/
- Richmond Fed LM: https://www.richmondfed.org/research/national_economy/natural_rate_interest

### TW
- CBC: https://www.cbc.gov.tw/
- NDC 景氣指標: https://index.ndc.gov.tw/
- data.gov.tw PMI / NMI: https://data.gov.tw/dataset/6100

### KR
- BOK 통화정책방향: https://www.bok.or.kr/
- KOSPI 집중도: https://www.krx.co.kr/
- BIS 가계부채: https://www.bis.org/statistics/totcredit.htm

### CN PMI (v1.11.0 new)
- Caixin S&P Global: https://www.pmi.spglobal.com/
- NBS 制造业 PMI: http://www.stats.gov.cn/sj/zxfb/

### TW PMI (v1.11.0 new)
- NDC PMI page: https://index.ndc.gov.tw/n/zh_tw/PMI
- CIER English: https://www.cier.edu.tw/en/eco_cat/pmi-en/
- data.gov.tw dataset 6100: https://data.gov.tw/en/datasets/6100

## Deferred (v1.12.0+)

- KR KTBi via BOK ECOS API key registration (barrier unchanged)
- JP au Jibun Bank / KR S&P Global PMI licensed access (no free path
  unless S&P Global policy change)
- Full 5-parallel grounding re-audit for all 5 countries
  (next target ~2026-Q3)
- JGBi YTM solver (architecturally rejected — would make JP the only
  bond-math country among 5; see v1.11.0 brainstorm conversation for
  full rationale)
- Swap spread expansion to non-US countries (US-only by design; global
  USD funding signal, not domestic liquidity stress)

## Verification Status

- ✅ CN 7 🔴 + 5 ⚠️ findings verified via Commit 3 primary-source URLs
- ✅ JP 7 🔴 + 4 ⚠️ findings verified via Commit 3 primary-source URLs
- ✅ US 2 🔴 + 2 ⚠️ findings verified via Commit 4 (HLW / Richmond Fed /
  FOMC March minutes)
- ✅ TW 0 🔴 + 3 ⚠️ verified via CBC decision + NDC 景氣燈號 publication
- ✅ KR 0 🔴 + 3 ⚠️ verified via BOK 통화정책방향 + BIS credit stats
- ✅ CN PMI akshare integration smoke-tested (Commit 1)
- ✅ TW PMI `ndc_client` CSV fetch smoke-tested (Commit 2)
- ✅ JSDA / JBTS / MoF YTM solver rejection rationale preserved via
  `grounding-v1.10.0.md` cross-reference

## Sign-off

Cross-country consistency refresh complete. PMI coverage improved
1/5 → 3/5 live; thresholds synchronised to 2026-Q2 vintage; mixed
strategy proved policy-velocity-appropriate (CN + JP high velocity
confirmed; US moderate; TW + KR low). country-macro skills preserved
pure data-layer discipline — only `macro-regime-snapshot` aggregation
layer received calibration updates.

v1.10.0 C+D+E framework (JP real-rates multi-source) remains
fit-for-purpose after v1.11.0 JP grounding refresh; no Block 4
framework changes needed. v1.11.0's Block 1 PMI row gains 2 new live
cells (TW + CN) while preserving JP / KR URL-only honesty.
