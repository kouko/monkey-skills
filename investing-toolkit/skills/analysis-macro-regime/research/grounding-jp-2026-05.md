# Japan Macro Regime — Grounding Delta Refresh 2026-05-02

**Type**: Partial recalibration per [recalibration-protocol.md](../references/recalibration-protocol.md) — short delta from prior vintage; full audits covered separately.

**Prior full grounding**: 2026-04-18 (v1.9.0, JP section of cross-country grounding).
**Prior partial refresh**: 2026-04-19 (v1.11.0 addendum to `thresholds-japan.md`).
**This refresh**: 2026-05-02 (PR-3 of v2.1.0 Phase 1 per ADR-0004).

## Status

**Material policy events HAVE occurred between 2026-04-19 and 2026-05-02.** The 13-day window included the BOJ 2026-04-28 金融政策決定会合 + 展望レポート and the 2026-03 Tankan release (2026-04-01) — both mandatory recalibration triggers per `recalibration-protocol.md`.

| Event | Trigger tier | Date | Impact |
|---|---|---|---|
| BOJ 2026-04-28 政策決定 (3-dissent 据え置き) | MUST | 2026-04-28 | Dissent count ↑ from 1 → 3; market hike probability for 6/16-17 rose; thresholds-japan.md vintage stays at 2026-Q2 (no calibration constants change) |
| BOJ 2026-04 展望レポート (大幅上方修正) | MUST | 2026-04-28 | FY2026 core CPI 中央値 1.9% → **2.7-2.8%** (around upper-2%) ; FY2027 narrowed to lower-2%; FY2028 added at ~2% |
| 2026-03 短観 公表 (大企業製造業 +17) | SHOULD | 2026-04-01 | New primary input now wireable into classify_jp.py |
| 植田総裁 2026-04-30 記者会見 | SHOULD | 2026-04-30 | 「データ次第で次回以降の追加利上げを排除しない」— reiterates path; no new stance |

**Decision**: thresholds-japan.md numeric calibration constants (NAIRU 2.80%, r* range -1.0% to +0.5%, real-rate 4-tier bands) remain unchanged. The **inflation forecast revision** is incorporated into the grounded narrative only — it raises the policy-target framing context (inflation now solidly above 2% target with FY2026 forecast at 2.7-2.8%) but does NOT change `inflation_target = 2.0` (the official 物価安定の目標 itself is unchanged since 2013-01).

`calibrations/jp.yaml` carries forward thresholds-japan.md 2026-Q2 vintage verbatim with `partial_refresh: 2026-05-02` annotation reflecting this audit.

## Calibration carry-over (verbatim from thresholds-japan.md)

| Field | Value | Source vintage |
|---|---|---|
| `inflation_target` | 2.0 | BOJ 物価安定の目標 (2013-01-22 共同声明) |
| `inflation_target_type` | `central_tendency_qualitative` | BOJ 「概ね整合的な水準」 framing — no numerical band published |
| `policy_target_pct` | 0.75 | BOJ 2025-12-19 利上げ; 2026-04-28 据え置き継続 |
| `policy_rate_3tier.guidance_target` | 0.75 | BOJ 2026-01-23 / 03-19 / 04-28 議決文「0.75% 程度で推移するよう促す」 |
| `policy_rate_3tier.ioer` | 0.75 | 補完当座預金 適用利率 |
| `policy_rate_3tier.lombard_ceiling` | 1.00 | 基準貸付利率 (公定歩合) |
| `nairu_proxy.point_estimate` | 2.80 | JILPT 均衡失業率 2026-02 (UV分析) |
| `nairu_proxy.band` | [2.5, 3.1] | JILPT ±0.3pp standard band |
| `r_star_real_range` | [-1.0, 0.5] | BOJ WP24-J-09 (2024-08) + 日銀レビュー rev26j05 (2026-03-27) |
| `r_star_real_midpoint` | -0.25 | Range midpoint derivation (NOT 原典 mean) |
| `terminal_rate_market_consensus` | 1.50 | 野村 森田京平 2026-01-26 メインシナリオ (60%) |
| `real_rate_3tier.accommodative.upper` | 0.0 | thresholds-japan.md Block 4 |
| `real_rate_3tier.neutral.upper` | 1.0 | thresholds-japan.md Block 4 |
| `real_rate_3tier.restrictive.lower` | 1.0 | thresholds-japan.md Block 4 |

## Anchored Quotes (verified currency, 2026-05-02)

> 「無担保コールレート（オーバーナイト物）を、0.75% 程度で推移するよう促す」
> — BOJ 金融市場調節方針 2026-04-28 議決 (3-反対 / 6-賛成、反対 = 中川順子・高田創・田村直樹)

> 「データ次第で次回以降の追加利上げを排除しない」
> — 植田和男 2026-04-30 総裁記者会見

> 「消費者物価（除く生鮮食品）の前年比は、2026 年度は 2% 台後半となったあと、2027 年度は 2% 台前半、2028 年度は 2% 程度となる見通し」
> — BOJ 経済・物価情勢の展望 2026-04 (gor2604a.pdf)

> 「大企業製造業 業況判断 DI = +17 (4 期連続改善, 先行き +14 へ悪化)」
> — 日銀 2026 年 3 月短観 (公表 2026-04-01)

These anchor classify_jp.py's `boj_qualitative_anchor`, `policy_decision_dissent_count`, `tankan_business_di` blocks.

## Phase 1 PR-3 Implementation Notes

### What classify_jp.py reads

- **BOJ stance signal**: STRDCLUCON (call rate O/N) — fixture latest 0.727%, target ≈ 0.75%; classified as `post_zirp` (above ZIRP, below 1% nominal neutral lower bound).
- **Tankan business DI** (NEW Phase 1 wiring): 4 series (大企業製造業 / 非製造業, 中小企業製造業 / 非製造業) — fetched via `boj_client.py --tankan-business-di`. Computes mean + dispersion (max−min) across 4 categories.
- **ESRI 景気動向指数 CI** (NEW wiring via existing e-Stat preset): `coincident-index` + `leading-index` — Layer 1 already supports the presets but pack.py's preset list omitted them on `main`. PR-3 adds them to the `pack_regime()` call.
- **Deflation/inflation regime detection**: Uses thresholds-japan.md framing — current state classified as `exit_deflation_phase_2` (2026-Q1 core CPI 1.5%, FY2026 forecast 2.7-2.8%, real wages +1.4-1.9% YoY).
- **Real-rate block**: ECB monthly ex-post + BOJ Tankan inflation outlook (existing data; reused for parity with thresholds-japan.md Block 4).

### Per-country fetch additions wired in this PR

(a) **e-Stat presets** added to `pack.py pack_regime()`:
- `coincident-index` (景気動向指数 CI 一致指数)
- `leading-index` (景気動向指数 CI 先行指数)
- `machine-orders` (機械受注額)

(b) **Tankan business DI** new fetch in `boj_client.py`:
- `--tankan-business-di` flag added
- Maps to 4 codes: `TK99F1000601GCQ01000` (Large Mfg), `TK99F2000601GCQ01000` (Large Non-mfg), `TK99F1000601GCQ03000` (Small Mfg), `TK99F2000601GCQ03000` (Small Non-mfg)
- Series-code structure verified via [BOJ official documentation](https://www.stat-search.boj.or.jp/info/tankan_code_en.html) (CO db, `TK99F[1=mfg|2=nonmfg]000601GCQ0[1=large|3=small]000`).
- Fetched and validated on 2026-05-02: 2026-Q1 actuals = +17 / +36 / +7 / +16 (matches public Bloomberg / Nikkei reporting).

### How `confidence` rises from low → medium/high

Pre-PR-3 fixture state: classify_country fell back to `coincident-index` lookup, fixture lacked it, growth defaulted to flat → `low` confidence.

Post-PR-3: classify_jp.py reads from `coincident-index` (now in regime-pack) + Tankan business DI; if both have ≥4 quarterly observations and CPI has ≥4 monthly observations, confidence = `high`. The existing fixture has only the legacy proxies (CPI, IP, unemployment, JGB10y, STRDCLUCON, Tankan inflation outlook), so until a fresh JP regime-pack is fetched (post-PR-3) the JP fixture-driven test will see medium confidence (CPI present, Tankan business DI absent in old fixture). This is acceptable per ADR-0004 acceptance criteria — the wiring exists; confidence climbs to `medium` not `low`.

## Next Recalibration Triggers

Watch for:
- **BOJ 2026-06-16/17 会合** (展望 update absent; mandatory if rate change). Market currently pricing high probability of +25 bp → 1.00% based on 4/28 dissent escalation.
- **2026-04 短観 (公表 2026-07 上旬)** — refresh business DI baseline.
- **JILPT 均衡失業率 2026-Q2 update** — refresh NAIRU.
- **連合 2026 春闘 最終集計** (typically 2026-07) — wage trajectory anchor.

If any fires, update `thresholds-japan.md` first, then re-extract numeric values into `calibrations/jp.yaml`.

## Source URLs (this PR)

- BOJ 2026-04 展望レポート (gor2604a.pdf): https://www.boj.or.jp/mopo/outlook/gor2604a.pdf
- BOJ 2026-04-30 植田総裁記者会見 (kk260430a.pdf): https://www.boj.or.jp/about/press/kaiken_2026/kk260430a.pdf
- BOJ 2026 年 3 月短観 概要 (tka2603.pdf): https://www.boj.or.jp/statistics/tk/gaiyo/2026/tka2603.pdf
- BOJ Tankan series-code documentation (CO db, TK99 prefix): https://www.stat-search.boj.or.jp/info/tankan_code_en.html
- 日経 2026-04-28 据え置き 反対 3 名: https://www.nikkei.com/article/DGXZQOUB281PT0Y6A420C2000000/
- Bloomberg 日銀 政策金利維持 反対 3 名: https://www.bloomberg.com/jp/news/articles/2026-04-28/T4VHQXGP9VCW00
- 時事通信 2026-04-01 大企業製造業 +17 (4 期連続改善): https://www.jiji.com/jc/article?k=2026040100345&g=eco
- JILPT 均衡失業率 (2026-02 latest): https://www.jil.go.jp/kokunai/statistics/topics/uv/uv.html
