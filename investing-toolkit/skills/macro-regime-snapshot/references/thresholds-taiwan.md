# Taiwan / 台灣 — Macro Regime Thresholds & Calibration

**Authority**: 中央銀行 (CBC) + 國家發展委員會 (NDC) + 主計總處 (DGBAS) |
**Currency**: TWD | **Calibration vintage**: 2026-Q1

---

## Inflation Target / 物價穩定定義

- **No explicit numeric target.** CBC explicitly rejects rigid 2%
  targeting, citing "小型開放經濟體" (small open economy) context —
  uses **"具彈性的物價穩定定義"** (flexible price-stability definition).
- **Informal watchline**: **2%** is commonly cited as 警戒線 (alert
  level) in commentary but is **not binding** on CBC.
- **Recent readings (2026-Q1)**:
  - 2026-01 CPI YoY: **0.69%** (9 consecutive months below 2%)
  - 2026-02: **1.75%**
  - 2026-03: **1.2%**
- **CBC's 2026 outlook**: CPI 將降至 2% 左右 (implicit ~2% as central
  anchor despite flexibility language)
- **Signal (with flexible anchor)**:
  - `> 2.5%` Above watchline (CBC attention)
  - `1.5% ≤ x ≤ 2.5%` Near watchline (normal range)
  - `< 1.5%` Below watchline (disinflation risk)

### Important framing caveat

Unlike Fed/BOJ/BOK's 2% formal target, TW CPI moves are often
**supply-side / imported inflation driven** (energy, food) more than
demand-pull. CBC's flexibility language acknowledges this. Don't
reflexively map TW inflation-above-2% to Phase 2 Overheat without
checking whether it's demand or supply.

---

## Labor Market Tightness (NAIRU)

- **No official NAIRU publication** from 中央銀行 / 主計總處. Academic
  estimates + historical structural rate: **~3.5-4.0%**.
- **Recent unemployment** (主計總處 DGBAS):
  - 2026-Q1: **~3.4%** (low end of post-1990 structural range)
  - Historic range: 3.4-6.1% (2009 GFC peak)
- **Bands (using ~3.7% structural anchor ± 0.4 pp)**:
  - `unemp < 3.3%` → Tight
  - `3.3% ≤ unemp ≤ 4.1%` → Balanced
  - `unemp > 4.1%` → Slack
- **Caveat**: Taiwan unemp also masked by **hidden under-employment**
  (part-time, informal sector) + large youth unemployment differential
  (youth 15-24: ~12%).

---

## 景氣對策信號 (NDC Business Cycle Signal) — Taiwan-specific

Taiwan has a **unique pre-aggregated regime indicator**: 五色景氣燈號
(5-color business cycle signal) published monthly by NDC 國家發展委員會.
This IS the official Taiwanese monthly GDP proxy.

**Construction**: 9 indicators × 1-5 分/指標 → composite **9-45 分**

**Signal thresholds (NDC official)**:

| 分數 | 燈號 | Signal semantic | Phase mapping |
|------|------|-----------------|----------------|
| 38-45 | 🔴 紅燈 | 景氣過熱 (overheated) | Phase 2 Overheat |
| 32-37 | 🟠 黃紅燈 | 景氣熱絡 (warm) | Phase 2 entering / Phase 1 late |
| 23-31 | 🟢 綠燈 | 景氣穩定 (stable) | Phase 1 Recovery (mid) |
| 17-22 | 🔵 黃藍燈 | 景氣欠佳 (caution / cooling) | Phase 3 early / Phase 4 |
| 9-16 | 🔷 藍燈 | 景氣低迷 (recession) | Phase 4 Reflation / deep slowdown |

**For the `Direction` column in Block 1** (Growth axis):
- Score ≥ 32 + MoM rising → **Rising** / Expansion
- Score 23-31 → **Flat** / Stagnation (unless 3-month directional trend)
- Score < 23 → **Falling** / Contraction

**For the `Signal` column**: use the color name directly (紅燈 /
黃紅燈 / 綠燈 / 黃藍燈 / 藍燈) — readers in Chinese-speaking markets
recognise these as canonical.

---

## Policy Rate Neutrality

- **CBC 政策利率 (貼現率)**: **2.00%** (2026-Q1)
- **Nominal neutral estimate**: CBC does not publish an explicit r*
  or neutral rate. Academic + market estimates: **nominal ~1.75-2.0%**,
  implying **real r\* ~0-0.5%**.
- **Context**: Taiwan has consistently run lower policy rates than US
  given structurally lower inflation (export-driven, price-taker
  economy). 2.0% is NOT particularly restrictive in TW historical
  terms — would be ~300 bp below US at 2026-Q1.

---

## Real Rate Decomposition

**Not available** for v1.9.0.

**Why**: Taiwan has **no developed government inflation-linked bond
market**. The only quasi-TIPS equivalent is 通膨連動公債 which has
been issued infrequently and has minimal secondary-market liquidity.

**Deferred**: indefinitely (no clean data path).

---

## Structural Regime Notes

- **Small open economy + export-driven**: semiconductors + ICT
  electronics dominate GDP (~25-30%). **TW macro regime follows
  global tech cycle more than domestic demand**.
- **Very low trend inflation**: 2000-2020 average CPI ~1.0% — 2%
  target doesn't fit Taiwan's actual cost structure.
- **NT$ managed floating**: CBC intervenes aggressively to smooth
  NT$ vs USD — FX dynamics less free-float than US/JP.
- **Semiconductor cycle dominance**: when semi CAPEX + DRAM cycle
  turns, Taiwan GDP pivots months before official GDP prints —
  景氣燈號 (especially M1B + 機電設備 components) lead TAIEX moves.

---

## Asset-Class Tilt Calibration

- **Equity index concentration — EXTREME**:
  - TAIEX is **~65% tech-heavy** (semi + electronics)
  - **TSMC alone ~40%** of weighted index
  - Non-tech sectors (financials, traditional industry) only ~35%
  - → Regime tilts MUST account for **semi cycle = TW equity cycle**
- **Fixed income**: TW government bonds (公債) smaller market than
  TW equities; less useful for regime signal. CBC interventions
  compress yield movements.
- **FX**: NT$/USD the key cross (TW's largest trade partner); NT$/CNY
  secondary (supply chain). NT$/JPY tertiary (tourism + industrial
  capital goods).

### Sector Tilts (TW-specific adjustments to IC cheatsheet)

| IC Phase | TW-specific Overweight | TW-specific Underweight |
|----------|------------------------|--------------------------|
| Recovery | Semi (TSMC, UMC), electronics, shippers (semi inventory rebuild) | Utilities, traditional industry |
| Overheat | Upstream semi, foundry, petrochemicals, real estate | Long-dated bonds |
| Stagflation | Cash, utilities, defensive (telecoms) | Semi, electronics (inventory risk) |
| Reflation | Financials (benefit from higher rates), bonds | Semi, export-oriented |

**Heuristic**: TW Phase 2 Overheat ≈ upside on TSMC; Phase 3
Stagflation ≈ beware chip inventory correction.

---

## Primary-Source Verification URLs

- 中央銀行 CBC: https://www.cbc.gov.tw/
- CBC 彈性定義 policy: https://www.cna.com.tw/news/afe/202406190101.aspx
- 景氣指標查詢系統 NDC: https://index.ndc.gov.tw/n/zh_tw/
- 景氣對策信號簡介: https://www.ndc.gov.tw/nc_335_2236
- 中華民國統計資訊網: https://www.stat.gov.tw/

## Sources (citations)

- CBC 理監事聯席會議新聞稿 (quarterly policy statements)
- CBC 本年國內經濟及通膨展望 (中央銀行季度報告)
- 中央社 CNA 2024-06-19: CPI年增率2%為通膨警戒線？央行：採彈性定義較妥適
- NDC 景氣對策信號 methodology (9 indicator composite, 1-5 point scoring)
- MacroMicro 景氣對策信號 vs TAIEX 歷史對應圖
- StockFeel 股感 景氣燈號 2026-02 解析
