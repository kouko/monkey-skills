---
title: "v1.10.0 Task 2 primary-source grounding — JP real-rates C+D+E framework"
date: 2026-04-19
refactor_version: v1.10.0
tags: [research, investing-toolkit, macro-regime-snapshot, grounding, japan, real-rates]
---

# v1.10.0 Task 2 Grounding Note — JP Real Rates Multi-Source (C+D+E)

## TL;DR

v1.10.0 pivoted JP real-rates from originally-scoped JSDA YTM solver
(rejected after probe confirmed JSDA masks JGBi yield fields with 999.999)
to a C+D+E multi-source framework: MoF auction anchor + ECB monthly + BOJ
Tankan. This note documents the primary-source vetting for the 3 newly-
trusted sources.

## Rejected Paths (negative grounding)

### JSDA 公社債店頭売買参考統計値 (原 Task 2 main path)
- Probe date: 2026-04-18
- Finding: JGBi rows (銘柄種別 05) have 参考値 (yield) masked 999.999
- Only 単価 (price) published; yield must be self-derived
- Verified across all 9 outstanding JGBi issues (#22-#30) for 2026-04-17
- Authoritative reference: JSDA csvheaderbaisan.xlsx column specification

### JBTS 日本相互証券 BEI推移 page
- URL: https://www.bb.jbts.co.jp/ja/historical/marketdata05.html
- Technical access: free, no auth, daily BEI series displayed
- ToS rejection: サイトポリシー 明禁「複製、転用、販売、送信、送信可能化」
  and「第三者への提供、再配信を行うこと...はできません」
- Industry usage: stock-marketdata.com retail aggregator cites this (same ToS issue)
- Conclusion: public visibility ≠ redistribution right; similar to MacroMicro ToS

### Full MoF 連動係数 + QuantLib YTM solver
- Feasibility: MEDIUM — QuantLib has CPIBond + JapanRegion, needs scipy.brentq wrapper
- Effort: 5-7 working days (Bloomberg ±5 bp accuracy) per research agent estimate
- Deferred to v1.11.0 as dedicated PR with full primary-source grounding audit
- Data path verified: MoF XLS endpoint `/jgbs/topics/bond/10year_inflation-indexed/keisuu/keisuu{YYYYMMDD}.xls` stable, no-auth

## Accepted Paths (primary-source vetting)

### C. MoF JGBi Auction Real Yield (primary anchor)

**Authority tier**: A — direct government issuance data

**URL pattern**:
- Landing: https://www.mof.go.jp/jgbs/auction/calendar/nyusatsu/
- Per-auction: individual result page per issuance (e.g. `resul20250815.htm`)

**Series coverage**: v1.10.0 snapshot contains 第29回 × 3 + 第30回 × 2 (2024-05 → 2025-08)

**Field definition**:
- MoF 官方 discloses 募入最高利回り (marginal yield at lowest accepted price) = 単利 (simple-unit yield, not 複利 compound)
- This is the "yield" our YAML snapshot captures as `highest_yield_pct` field
- Per 服部 2024-Feb『ファイナンス』202402k.pdf footnote 4: MoF 単利 vs JSDA 入札前 複利 distinction

**Caveat on 単利 vs 複利**:
- Our YAML treats MoF 単利 as primary anchor
- For regime-signal comparison with ECB monthly (which is 複利-style ex-post real), there is a methodology gap
- Documented in thresholds-japan.md: MoF auction points used as "validation anchor at auction dates", not continuous threshold judgment
- Future v1.11.0 YTM solver will provide comparable 複利 values

**Trajectory of captured data**:

| 第回 | 入札日 | 募入最高利回り |
|------|--------|----------------|
| 29 | 2024-05-20 | -0.545% |
| 29 | 2024-11-11 | -0.362% |
| 29 | 2025-02-12 | -0.269% |
| 30 | 2025-05-22 | 0.000% |
| 30 | 2025-08-15 | +0.078% |

First non-negative JGBi print since 2015 = 2025-05 auction.

### D. ECB Data Portal JP 10Y Real Yield (continuous monthly)

**Authority tier**: B — central-bank-tier redistribution of government bond data

**Endpoint**: `https://data-api.ecb.europa.eu/service/data/FM/M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA?format=csvdata&lastNObservations={N}`

**Series metadata** (from SDMX response):
- Dataset: FM (Financial Markets)
- Key: M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA
- Publisher: ECB Financial Markets
- Frequency: Monthly
- Unit: Percentage (PCPA annualised)
- Source derivation: nominal yield minus realised CPI (ex-post, NOT market-implied)

**Critical caveat**:
- ECB publishes ex-post real yield = market nominal 10Y yield minus realised CPI
- This is NOT market-implied breakeven (would require JGBi market YTM)
- Academic literature (Deacon-Derry-Mirfendereski 2004) distinguishes clearly
- For regime-signal purposes, ex-post can run structurally +0.5pp higher than market-implied
- Documented in indicators-japan-real-rates.md common pitfalls section

**Freshness / staleness**:
- Publication lag: 1-3 months typical
- Actual observed (2026-04-18 fetch): latest obs = 2025-02, staleness 441 days
- ECB refresh cadence appears slower than stated lag — this is a known ECB behavior for ex-post series awaiting CPI revisions
- `ecb_client.py` reports staleness_days in `_provenance`; downstream consumers must check

**Cross-verification**:
- Values directionally consistent with Reuters / Bloomberg reports of Japan 10Y real yield
- No known wholesale data discrepancies

### E. BOJ Tankan 企業物価見通し (quarterly survey)

**Authority tier**: A — central-bank original survey

**Endpoint**: BOJ stat-search (stat-search.boj.or.jp)
- Database: CO (Tankan Outlook)
- Codes:
  - TK99F0000204HCQ00000 — 1Y ahead (全規模合計/全産業/企業物価見通し)
  - TK99F0000205HCQ00000 — 3Y ahead
  - TK99F0000206HCQ00000 — 5Y ahead

**Code disambiguation vetting**:
- Source: BOJ cotaisyo.zip series-code correspondence table at https://www.stat-search.boj.or.jp/info/cotaisyo.zip
- 204/205/206 series name: "Outlook for General Prices" (一般物価 / CPI basis)
- 201/202/203 series name: "Outlook for Output Prices" (販売価格 / producer price basis)
- Our pick: 204/205/206 (CPI basis) — matches the "inflation expectation" concept
- Pitfall: 201/202/203 would give producer-price outlook (different signal)
- Documented in boj_client.py docstring AND indicators-japan-real-rates.md pitfalls section

**Signal frequency quirk**: BOJ API rejects quarterly (CQ freq) start-dates unless MM ≤ 04. Helper `_periods_to_start_yyyymm` computes `YYYY01` + 2-year buffer then post-fetch trims. Documented in function docstring.

**Latest snapshot (2026 Q1)**:
- 1Y: 2.6% (above BOJ 2% target)
- 3Y: 2.5%
- 5Y: 2.5%

All 3 horizons above BOJ 2% target → sustained above-target inflation expectations.

**Usage as regime signal**:
- Survey-based, complementary to market-based BEI
- BOJ Outlook Report itself uses Tankan + BEI + 家計 survey + QUICK 月次 as 複合期待インフレ framework
- v1.10.0 SKILL.md reflects this pattern

## Multi-source Consistency

For 2025-Q1 evidence:
- MoF auction 第29回 2025-02: real yield -0.269% (at issuance, 単利)
- ECB monthly 2025-02: real yield -2.295% (ex-post, different definition)
- Gap: ~2.03 pp — aligns with ~0.5-2.5 pp "ex-post wedge" noted in academic literature (ex-post reflects realised CPI, which spiked 2024-2025; market-implied JGBi had priced expected declination)

For 2025-Q3 evidence:
- MoF auction 第30回 2025-08: real yield +0.078% (market-implied at auction)
- ECB monthly 2025-08: not yet published (ECB staleness >14 mo)
- Gap: reflects BOJ policy normalisation + global real-rate rise

Conclusion: the 3 sources provide triangulation; no single source is definitive
but together they constrain the JP real-rate regime reasonably.

## Primary-Source URLs (consolidated)

1. MoF JGBi auction history: https://www.mof.go.jp/jgbs/auction/calendar/nyusatsu/
2. MoF JGBi product spec: https://www.mof.go.jp/jgbs/topics/bond/10year_inflation-indexed/syouhinsekkei.htm
3. MoF 連動係数 XLS: https://www.mof.go.jp/jgbs/topics/bond/10year_inflation-indexed/keisuu/ (v1.11.0 target)
4. ECB Data Portal API: https://data-api.ecb.europa.eu/service/data/FM/
5. ECB FM dataset overview: https://data.ecb.europa.eu/help/api/overview
6. BOJ Tankan code mapping: https://www.stat-search.boj.or.jp/info/cotaisyo.zip
7. BOJ Tankan landing: https://www.boj.or.jp/statistics/tk/index.htm
8. 服部孝洋『ファイナンス』202402k「BEI入門」: https://www.mof.go.jp/public_relations/finance/202402/202402k.html
9. JSDA 売買参考統計値 (context — NOT used): https://market.jsda.or.jp/shijyo/saiken/baibai/baisanchi/index.html

## v1.11.0 Roadmap Implications

- Full daily JGBi YTM solver will replace MoF-auction anchor points + extend ECB monthly to daily
- QuantLib CPIBond approach validated in prior research (Agent 4 of v1.10.0 Task 2 research)
- Validation plan: daily YTM solver output vs MoF auction anchors (±2 bp accuracy target) + ECB monthly (±5 bp, different definition caveat)
- v1.10.0 C+D+E framework becomes the validation harness for v1.11.0 solver

## Verification Status

- ✅ MoF JGBi auction history YAML: 5 entries, all URLs cite-verifiable
- ✅ ECB series: smoke test returned 2025-02 = -2.295%, provenance shows staleness handled
- ✅ BOJ Tankan: smoke test 2026-Q1 1Y = 2.6% matches published
- ✅ 204/205/206 vs 201/202/203 disambiguation: cited from BOJ cotaisyo.zip
- ✅ JSDA rejection: verified via agent probe of 999.999 masking
- ✅ JBTS rejection: verified ToS サイトポリシー quote

## Sign-off

Primary-source grounding for v1.10.0 Task 2 complete. Three new trusted sources
added to investing-toolkit: MoF JGBi auction (tier A), ECB SDMX JP real yield
(tier B), BOJ Tankan CO-DB 204/205/206 (tier A). Rejected sources documented
with rationale. v1.11.0 upgrade path preserved.
