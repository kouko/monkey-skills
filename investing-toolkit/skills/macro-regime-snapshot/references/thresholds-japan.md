# Japan / 日本 — Macro Regime Thresholds & Calibration

**Authority**: 日本銀行 (Bank of Japan, BOJ) | **Currency**: JPY |
**Calibration vintage**: 2026-Q1

## Grounding Status (as of 2026-04-18)

**Last full verification**: 2026-04-18 via `../research/grounding-v1.9.0.md`
(5-country parallel grounding note; JP section).

**Verified (✅)**: 2013-01-22 2% 目標採用日、2026-02 完全失業率 2.6%、
Williams-like 定性語言。

**Corrected (🔴 in prior draft → fixed below)**:
1. **BOJ 政策利率 0.75%** — 2025-12 升息至 30 年來最高（prior draft
   wrote 0.5%）
2. **JILPT 均衡失業率 2.80%** (2026-02 latest) — NOT 3.5-3.6%.
   需要不足失業率 -0.17%。Current unemp 2.6% 是**軽度タイト only**，
   not "~1 pp below NAIRU".
3. **BOJ 展望 2025-10 FY 見通し**: FY2025/26/27 = 2.7% / 1.8% / 2.0%
   (prior draft wrote FY2024/25/26 = 2.5/1.9/1.9 — wrong by 1 year
   AND wrong 0.8 pp on FY2025).
4. **野村 森田京平 main scenario**: ターミナル 1.50% via 3 hikes
   (2026-06, 2026-12, 2027-06); prior draft wrote 2 hikes to 1.0%.
5. **10Y JP real yield -0.386% 数値削除** — 伊藤忠 2024-04 コラム
   本文不含此数値 (unverifiable fabrication risk).

**Partial (⚠️)**: WP24-J-09 r\* "mean -0.25%" → refined as **range
midpoint derivation**, not原典表述。

**New primary sources added**: BOJ 日銀レビュー rev26j05 (2026-03-27 —
最新官方 r\* 見解), lab18j02 (1980 年代以来 r\* 下降 4 pp 分解).

**Next recalibration**: April 2026 (BOJ 展望 Q1 release).

---

---

## Inflation Target / 物価安定の目標

- **Official target**: **2% CPI YoY** (headline 全国CPI, set 2013-01)
- **Tolerance band**: **none published** — BOJ uses qualitative
  "概ね整合的な水準" ("roughly consistent level") rather than a
  numerical band. Academic proposals (Canada-style 1-3%) exist but
  not adopted.
- **Current outlook**: Core CPI (除生鮮食品) FY2026 見通し中央値 +1.8%,
  FY2027 +2.0% (2025-10 展望レポート, 政策委員中央値)。FY2025 は +2.7%
  と輸入インフレ・米価押上げ等でオーバーシュート状態。
- **FY outlook (BOJ 展望レポート 2025-10, 政策委員中央値)**:
  - Core CPI (除生鮮食品): FY2025 **+2.7%** / FY2026 **+1.8%** / FY2027 **+2.0%**
  - 実質 GDP: FY2025 +0.7% / FY2026 +0.7% / FY2027 +1.0%
  - Projection horizon 末尾: 「物価安定の目標と概ね整合的な水準」
- **Signal (using BOJ 2% anchor)**:
  - `> 2.2%` Above target
  - `1.8% ≤ x ≤ 2.2%` At target (this IS BOJ's goal state)
  - `< 1.8%` Below target (historically Japan's default regime)

### Important framing caveat

Japan's **decades-long deflation legacy** means the 2% target is a
**policy goal** rather than an ambient equilibrium. A reading of 1.9%
should be treated as **success** (not "below target"), not as
disinflationary concern — context matters. The regime call for Japan
should give more weight to **direction of change** (rate-of-change) than
level-vs-target gap.

---

## Labor Market Tightness (NAIRU / 均衡失業率)

- **NAIRU proxy (JILPT 均衡失業率)**: **~2.80%** (2026-02 latest;
  2025Q4 = 2.78%); 需要不足失業率 -0.17% で労働需給は**充足状態**
- **Current unemployment** (労働力調査 2026-02): **2.6%** (季調;
  2026-01 は 2.7%)
- **Implication**: unemployment は均衡失業率を **~0.2 pp 下回る** →
  労働需給充足から**軽度タイト**。post-2015 の構造的タイト化は継続
  しているが、prior draft の "1 pp 下回る Tight" は過大評価。
- **Bands (JILPT 均衡失業率 ± 0.3 pp, 絶対値が低い JP 特性を反映)**:
  - `unemp < 2.5%` → Tight (overheating 兆候)
  - `2.5% ≤ unemp ≤ 3.1%` → Balanced (現在 2.6% はこのバンド)
  - `unemp > 3.1%` → Slack
- **春闘 wage signal**: since 2024 春闘, Japan transitioning from
  "tight-no-wage-gain" to genuine wage growth — watch spring round
  results as second labor-tightness dimension.
- **Wage-inflation signal**: since 2024 春闘 wage rounds, Japan
  transitioning from "tight-but-no-wage-gain" to genuine wage growth —
  watch spring round results as a second labor-tightness dimension.

---

## Policy Rate Neutrality

- **Current BOJ policy rate**: **0.75%** (post-YCC end 2024-03 →
  2024-07 0.25% → 2025-01 0.50% → 2025-12 **0.75% (30 年ぶり水準)**;
  2026-01-23 会合で据え置き、1 名が 1.0% 提案も否決)
- **Nominal neutral rate estimate**: ~**1.0-1.75%** (市場コンセンサス
  + 野村メインシナリオターミナル 1.50% を包含). BOJ themselves do not
  publish a neutral rate.
- **Real r\* (BOJ Working Paper 24-J-09 2024-08 + 日銀レビュー rev26j05 2026-03)**:
  - Range estimates: **-1.0% to +0.5%** (複数モデルの幅; 原典が「相当な
    ばらつきがある」と明記)
  - Range 中点: ~**-0.25%** (単一推計値ではなく派生; "mean" 一語は
    原典表現でないため避ける)
  - 長期トレンド: 1980 年代から約 **4 pp 低下** (lab18j02 分解: 技術進歩
    ~2 pp + 金融仲介機能 ~1 pp + 人口動態)
  - 日本の r\* は G7 最低水準; 長寿化・生産性鈍化・銀行危機傷跡が主因
  - 2026-03 rev26j05 は WP24-J-09 を GDP 基準改定後に再推計した BOJ 最新公式見解
- **Nominal hiking path (野村 森田京平 2026-01-26 メインシナリオ 60%)**:
  - 2026-06 +25 bp → 1.00%、2026-12 +25 bp → 1.25%、2027-06 +25 bp → 1.50%
  - **ターミナルレート: 1.50%**
  - リスクシナリオ (円安圧力継続, 40%): 2026-04/10, 2027-04/10
    各 +25 bp → ターミナル **1.75%**

---

## Real Rate Decomposition

**Not available** in free data layer for v1.9.0.

**Why**: Japan has JGBi (物価連動国債, inflation-linked bonds) but:
1. BOJ/e-Stat API does not expose clean daily breakeven/TIPS-equivalent
   series in ECOS-like form
2. Would require MoF XLS scraper (月次 発行実績 + 流通市場データ)
3. Market structure differs — JGBi less liquid, BOJ still holds
   substantial inventory

**Current 10Y JP real yield**: 2026-Q1 時点で G7 の中で相対的に低く
(負圏の可能性あり)。prior draft の "-0.386%" 出典（伊藤忠総研 2024-04
コラム) は本文に該当数値を含まないため**削除**。v1.10.0 で MoF JGBi
(物価連動国債) scraper 実装時に検証可能なスナップショットへ差替え。

**Deferred to v1.10.0+**: MoF JGBi scraper + thresholds calibrated to
JP r* estimate (probably `< -0.5%` Accommodative / `-0.5% to 0.5%`
Neutral / `> 0.5%` Restrictive — roughly HLW-JP ± 50 bp).

---

## Structural Regime Notes

- **Post-deflation transition** (since 2022-2024): Japan is leaving
  the "2% is aspirational" regime into "2% is achieved". This shifts
  the IC mapping:
  - Pre-2022: Japan was almost always **Phase 4 Reflation** (falling
    growth + falling inflation below target)
  - 2024-2026: first sustained **Phase 2 Overheat** (rising both) in
    decades; regime identification should acknowledge this rare shift.
- **BOJ YCC ended 2024-03**: pre-2024 JGB 10Y curve was artificially
  pinned; post-2024 readings more market-driven.
- **Demographic overhang**: aging population + shrinking workforce
  → structurally low r*, low trend growth (~0.5% real). This
  **caps sustainable policy rate ceiling**.
- **JPY regime**: Japan is a creditor nation with massive FX reserves
  + overseas assets (~3x GDP). JPY appreciation in risk-off is a
  regime-cross-check signal.

---

## Asset-Class Tilt Calibration

- **Equity index**: TOPIX (broad, ~2,100 names) preferred for regime
  mapping over Nikkei 225 (price-weighted, 225 names). Sector
  structure more balanced than KOSPI/TAIEX. Tech weight ~15-20%
  (vs TW ~65%).
- **Corporate governance reform**: post-2023 TSE reform driving P/B
  rerating — **structural re-rating can dominate regime signal** for
  JP equities.
- **Fixed income**: JGB curve post-YCC → finally market-priced;
  10Y yield ~1.5% (2026-Q1). Real yield negative → JGB expensive in
  real terms but defensive.
- **Commodities**: Japan is major commodity importer — commodity
  strength = terms-of-trade drag. Energy (crude) especially critical
  (not self-sufficient).
- **FX**: JPY weakness drives imported inflation directly (Japan CPI
  reacts ~0.4% per 10% JPY depreciation). JPY direction often a
  regime factor, not just a consequence.

### Sector Tilts (JP-specific adjustments to IC cheatsheet)

| IC Phase | JP-specific Overweight | JP-specific Underweight |
|----------|------------------------|--------------------------|
| Recovery | Financials (banks benefit from positive rates), automakers, tech-value | Utilities, defensive staples |
| Overheat | Trading houses (商社), commodity-linked, shippers | Import-heavy consumer, JGB |
| Stagflation | JPY cash, energy, healthcare | Real estate, consumer discretionary |
| Reflation | JGB, REITs (J-REIT), telecoms | Automakers, export-oriented |

---

## Primary-Source Verification URLs

- 日銀 物価安定の目標: https://www.boj.or.jp/mopo/outline/target.htm
- 日銀 経済・物価情勢の展望: https://www.boj.or.jp/mopo/outlook/
- 日銀 WP 自然利子率 WP24-J-09: https://www.boj.or.jp/research/wps_rev/wps_2024/wp24j09.htm
- JILPT 均衡失業率・需要不足失業率: https://www.jil.go.jp/kokunai/statistics/topics/uv/uv.html
- 労働力調査 (e-Stat): https://www.e-stat.go.jp/stat-search/files?tclass=000001226526

## Sources (citations)

Primary (原典, 日本語):
- BOJ 物価安定の目標 (2013-01-22 共同声明)
- BOJ 経済・物価情勢の展望 2025-10 (展望レポート本文 + ハイライト)
- **BOJ Working Paper WP24-J-09 (2024-08, 杉岡・中野・山本)** — 自然利子率の計測をめぐる近年の動向
- **BOJ 日銀レビュー rev26j05 (2026-03-27, 企画局)** — 自然利子率の動向と金融緩和度合いの評価 (最新 BOJ 公式 r\* 見解)
- **BOJ リサーチラボ lab18j02 (2018-06, 須藤・岡崎・瀧塚)** — わが国の自然利子率の決定要因 (r\* 下降 4pp 分解)
- BOJ WP03-J-05 (2003-10, 小田・村永) — 自然利子率 分析原点
- BOJ 総裁記者会見 (2026-01-23 kk260126a.pdf)
- JILPT UV 分析 (均衡失業率 2026-02 最新)
- 総務省統計局 労働力調査
- 日経 参議院 Research Note 2024-12 — 物価安定の目標をめぐる経緯と論点

Secondary (日本語):
- 野村ウェルスタイル 0571 (2026-01-26, 森田京平) — 日銀利上げシナリオ (main ターミナル 1.50%)
- NRI 木内登英 2025-12-16 コラム — 政府のデフレ完全克服と日銀の2％物価安定
- 第一ライフ資産運用経済研究所 熊野英生 0.75% 利上げコラム
- JST 資金運用本部 Research Note 42 (2026-01-29) — 中立金利とタームプレミアム
- 日経 2025-12-19 — 日銀 0.75% 利上げ決定 (30 年ぶり水準)

Removed (unverifiable):
- ~~伊藤忠総研 2024-04 コラム「自然利子率r\*に振り回される日米金融市場」数値引用~~
  (-0.386% / G7 比較 数値が本文に不含; 出典無効)
