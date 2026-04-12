---
title: research-team 投資分析 canon 拡張 — Hedgeye GIP / MMT / RAI / Taleb Barbell / Fama-French
date: 2026-04-12
team: research-team
refactor_version: v4.11.0
tags: [research, domain-teams, research-team, grounding, investment, macro, factor, portfolio]
---

# research-team v4.11.0 grounding research

> [!info] 研究背景
> v4.11.0 將 v4.9.0 完成的 `standards/investment-analysis-canon.md` 拆成 4 個按
> **分析尺度（analytical scale）** 切分的 standards 檔案，並補入 5 個 NEW frameworks：
>
> - **L1 Macro** — `investment-macro-regime.md`
>   - 既存：Investment Clock (Greetham 2004) / Dalio Debt Cycle / Koo Balance Sheet Recession
>   - **NEW**: Hedgeye GIP 4-Quadrant、MMT (Modern Monetary Theory)、RAI (Risk Appetite Index)
> - **L2 Sector / Factor** — `investment-sector-industry.md`
>   - 既存：Porter 5 Forces cross-reference
>   - **NEW**: Fama-French Factor Investing (FF3 1993 + FF5 2015 + Carhart 1997 + AQR QMJ 2019 + BAB 2014)
>   - 新含：sector rotation 對應 L1 regime 的 mapping
> - **L3 Security / Valuation** — `investment-security-valuation.md`
>   - 既存：Damodaran 3-framework / Graham & Dodd / CAPE
> - **Portfolio** — `investment-portfolio-construction.md`
>   - **NEW**: Taleb Barbell（Antifragile 2012 Ch 11）+ Risk Parity（Bridgewater All Weather）
>
> 為避免 v4.9.0 既存 canon 中 Greetham/Hedgeye/Wilmot 的歸屬漂移再現（v4.9.0 已修正
> 過 4-phase naming），本研究 phase 對 5 個 NEW frameworks 各跑一個 parallel grounding
> agent，並把 42 個 Critical Attribution Corrections 全部 surface 到 standards
> 檔案的 anti-drift 段落。
>
> **研究方法**: 5 個 parallel `general-purpose` grounding agents，每個 agent 同時做
> EN + JP web search、cross-verify 多重 secondary 描述、把 primary-source URL 對齊
> 章節 / 卷號 / DOI / 年份。Agent 輸出本研究 note 從會話 transcript 提取後合成。
>
> **本 phase 的任務**:
> (a) 確認 5 個 NEW frameworks 的 canonical primary source 存在且年份/版本/作者正確
> (b) 確認 primary source 實際包含 standards 檔案需要的 load-bearing claim
> (c) 列出每個 framework 的 Critical Attribution Corrections（anti-drift guardrails）
> (d) 決定每個 framework 的 tier 與 body depth（line budget）
> (e) 決定 JP 整合策略（每個 framework 各自評估）
> (f) 產出 4 份 standards 檔案的 draft plan（content 大綱、citation stack、anti-drift list）

## TL;DR

| Framework | Layer | Canonical primary | Tier | Body depth | JP integration |
|-----------|-------|---|---|---|---|
| **Hedgeye GIP 4-Quadrant** | L1 Macro | McCullough, K. & Dale, D. (2008–present) Hedgeye Risk Management. White paper: Hedgeye GIP Model Risk Management Process. Author text: McCullough (2024) *Master The Market* (Hedgeye ebook) | **Tier 2** (grey literature) | 60–100 lines | None — US firm only |
| **Modern Monetary Theory (MMT)** | L1 Macro | Mosler 1996 *Soft Currency Economics* (origin) + Wray 2012 *Modern Money Theory: A Primer* Palgrave (academic canonical) + Kelton 2020 *The Deficit Myth* PublicAffairs (popular canonical) | **Tier 2** (heterodox, must pair with mainstream critique) | 120–180 lines | High — Japan is the most cited case study |
| **RAI (Risk Appetite Index)** | L1 Macro | Kumar, M. & Persaud, A. (2002) *International Finance* 5(3): 401–436 (academic origin) + Illing & Aaron (2005) Bank of Canada FSR (survey anchor) + Wilmot et al. (2004) CSFB *Market Focus* (practitioner brand) | **Tier 2** (mixed academic + grey) | 80–120 lines | None public — BoJ heat map analogue only |
| **Taleb Barbell Strategy** | Portfolio | Taleb (2012) *Antifragile* Ch 11 (primary) + Taleb (2007) *The Black Swan* Ch 13 (first mention) + Geman, Geman & Taleb (2015) *Entropy* 17(6) (mathematical anchor) | **Tier 2** | 60–80 lines | None — JP "バーベル戦略" means duration ladder, NOT Taleb |
| **Fama-French Factor Investing** | L2 Sector/Factor | Fama & French (1993) *JFE* 33(1) [FF3] + Fama & French (2015) *JFE* 116(1) [FF5] + Carhart (1997) *JoF* 52(1) [momentum] + Asness-Frazzini-Pedersen (2019) RAS 24(1) [QMJ] + Frazzini-Pedersen (2014) *JFE* 111(1) [BAB] | **Tier 2** | 200–280 lines | Load-bearing — Kubota-Takehara 2018 + Asness 2011 are essential for any JP claim |

| Critical Attribution Correction (across 5 frameworks) | Count |
|---|---:|
| Hedgeye GIP cluster | 7 |
| MMT cluster | 7 |
| RAI cluster | 10 |
| Taleb Barbell cluster | 7 |
| Fama-French cluster | 11 |
| **Total Critical Attribution Corrections surfaced** | **42** |
| **Misattributions prevented before standards-file authoring** | **11+** |

---

# Research Questions Status

Phase 1 提出的 5 個 NEW-framework 研究問題，Phase 2 grounding 結果：

| # | Question | Status | Key sources verified |
|---|---|---|---|
| Q-Hedgeye-GIP | Canonical author / framework definition / lineage relative to Greetham IC and Dalio All Weather | ✓ verified | McCullough (2024) *Master The Market* (Hedgeye ebook); Hedgeye GIP white paper docs3.hedgeye.com; MacroVoices #738 transcript; Fidenza Macro independent description; Bridgewater "All Weather Story" for lineage |
| Q-MMT-Canon | Origin (Mosler 1996) vs academic (Wray 2012) vs popular (Kelton 2020); intellectual ancestors; mainstream critique | ✓ verified | Mosler 1996 *Soft Currency Economics*; Wray 2012/2015/2024 *Modern Money Theory: A Primer*; Kelton 2020 *Deficit Myth*; Knapp 1905 + Lerner 1943 + Mitchell-Innes 1913/14 ancestors; Krugman/Rogoff/Summers/Blanchard/Mankiw/Palley critique stack |
| Q-RAI-Canon | Disambiguation across Credit Suisse/Goldman/Citi/State Street variants; identify true academic origin | ✓ verified | Kumar & Persaud (2002) *International Finance* 5(3) is true academic origin; Illing & Aaron (2005) BoC FSR is survey anchor; Wilmot et al. (2004) CSFB *Market Focus* is practitioner extension; Froot & O'Connell NBER WP 10157 (NOT 8226) for State Street ICI |
| Q-Taleb-Barbell | Primary source 確定 — Antifragile 2012 vs Black Swan 2007; mathematical formalization | ✓ verified | Taleb (2012) *Antifragile* Ch 11 "Never Marry the Rock Star" is primary source (NOT Black Swan 2007 Ch 13, which is first-mention only); Geman-Geman-Taleb (2015) *Entropy* 17(6): 3724–3737 DOI 10.3390/e17063724 is mathematical anchor; Spitznagel 2013 *Dao of Capital* + 2021 *Safe Haven* for practitioner companion |
| Q-Fama-French-Canon | FF3 (1993) vs FF5 (2015) vs Carhart 4-factor (1997) disambiguation; momentum/quality/low-vol non-FF attributions; JP exception | ✓ verified | Fama & French 1992 JoF 47(2) (empirical foundation); Fama & French 1993 JFE 33(1) (operational FF3); Fama & French 2015 JFE 116(1) (FF5); Carhart 1997 JoF 52(1) (momentum factor); Jegadeesh & Titman 1993 JoF 48(1) (momentum anomaly); Asness-Frazzini-Pedersen 2019 RAS 24(1) (QMJ); Frazzini-Pedersen 2014 JFE 111(1) (BAB); Kubota & Takehara 2018 IRF 18(1) for Japan FF5 failure; Asness 2011 JPM 37(4) for JP momentum-as-hedge |

**Unverified / deferred**:
- Hedgeye 內部 quadrant threshold 規則（subscriber-only，open literature 不可重現）
- Universa BSPP 完整 historical performance（Bloomberg paywalled，僅 2008/2020 case studies 可驗證）
- BoJ Financial System Report ヒートマップ 與 RAI 形式對應的具體閾值
- 古典 *International Finance* 5(3) Kumar-Persaud 全文 PDF 未直接抓到（透過 Illing-Aaron 2005 + Uhlenbrock 2009 二次引用 cross-verified）

---

# Cluster A — L1 Macro Regime: Hedgeye GIP 4-Quadrant Model

## Q1. Hedgeye Growth-Inflation-Policy (GIP) framework

### 書誌（已驗證）

- **作者**: Keith R. McCullough (Founder/CEO, Hedgeye Risk Management LLC) **+ Darius Dale**（co-architect, ex-Hedgeye Partner / Macro Sector Head, 現為 42 Macro 創辦人）
- **canonical author text**: McCullough, K. (2024). *Master The Market: A Hedge Fund Manager's Guide to Process and Profit*. Hedgeye Risk Management / Hedgeye Gear（自出版 ebook，2024-10-18 release，52 pages）。
- **canonical white paper**: Hedgeye Risk Management. *An Introduction to the Hedgeye Macro Growth/Inflation/Policy (GIP) Model Risk Management Process*. https://docs3.hedgeye.com/macroria/Hedgeye_GIP_Model_Risk_Management_Process.pdf — Hedgeye 自家技術描述。
- **Periodic GIP summary**: Hedgeye Risk Management. *U.S. GIP Model Summary*. https://docs3.hedgeye.com/macroria/Hedgeye_U.S._GIP_Model_Summary.pdf
- **作者本人解釋**: McCullough, K. *"How I Front-Run Policy With My GIP Model."* Hedgeye Insights. https://app.hedgeye.com/insights/98877-mccullough-how-i-front-run-policy-with-my-gip-model — 直接 author statement。
- **MacroVoices podcast transcript #738 (2019)**: *"Keith McCullough: Inflation Accelerating"* https://www.macrovoices.com/podcast-transcripts/738-keith-mccullough-inflation-accelerating — McCullough 用自己的話說「rate of change / second derivative」定義。
- **Darius Dale 在自家 podcast**: *"Understanding Our Macro Process: 1-on-1 with Darius Dale"* https://app.hedgeye.com/insights/77860-podcast-understanding-the-marco-process-1-on-1-with-darius-dale — Dale 走 GIP 「top-left = Quad 1」的構造。
- **CMC Markets / Opto interview (2024)**: https://www.cmcmarkets.com/en-gb/opto/keith-mccullough-on-using-growth-and-inflation-quads-and-debunking-old-wall-misinformation — McCullough 給出 quadrant labels 和三個 time horizons。

### Type / Tier

- **Type**: Grey literature, firm-proprietary practitioner framework（非 peer-reviewed、非學術；獨立第三方 validation 不存在於 open literature）
- **Tier**: **Tier 2 (SHOULD cite)** — practitioner framework with clearly identified author + public firm + consistent multi-year exposition in open Hedgeye content。但 backtest 不可重現、沒有 academic replication。

### 核心定義

**The 2-axis framework.** GIP 追蹤一個 economy 的：

1. **Real GDP growth** 的 year-over-year **rate of change**（second derivative — 即 YoY 是否在加速 vs 上一期）
2. **Headline CPI inflation**（CPI index，非 core）的 year-over-year **rate of change**

兩個軸各 2 個狀態 → **4 quadrants**。McCullough 的方法論承諾：用 second derivatives，不用 absolute level vs trend（與 Greetham IC 不同）。

| Quad | Real Growth | Inflation | Hedgeye Label | 預設央行立場 |
|------|-------------|-----------|---------------|--------------|
| **Quad 1** | Accelerating ↑ | Decelerating ↓ | "Goldilocks" | Neutral |
| **Quad 2** | Accelerating ↑ | Accelerating ↑ | "Reflation" / "White-hot" | Hawkish |
| **Quad 3** | Decelerating ↓ | Accelerating ↑ | "Stagflation" | "In-a-box"（既不能放鬆也不能緊縮）|
| **Quad 4** | Decelerating ↓ | Decelerating ↓ | "Slowdown" / "Deflationary" | Dovish |

**Cross-verified** in Hedgeye GIP chart post + CMC/Opto interview + Fidenza Macro 第三方描述（後者用稍不同的同義 label）。

### 「Policy」如何運作 — 最關鍵的 anti-drift 點

GIP 的 "P" (Policy) **不是獨立的輸入變數**。GIP 不要求分析師獨立 classify Fed stance。Policy 是從 Growth / Inflation quadrant 1-to-1 mapping 出來的 **derived expected response**：

- Quad 1 → Neutral（Fed 沒有理由動 — disinflationary growth 對 Fed 是好事）
- Quad 2 → Hawkish（Fed 升息 — 通膨接近 / 超過 2% 目標）
- Quad 3 → In-a-box（Fed 既不能放鬆也不能升息 — stagflation 困局）
- Quad 4 → Dovish（Fed 降息 / QE — growth + inflation 都在減速）

McCullough 的原話: *"If I get the Growth and Inflation right, I'm front-running the policy move."* Policy 是 **forward-looking anticipation layer**，不是獨立 measure 的 dimension。

### Critical architectural implication

> **GIP 是 2-axis 框架 + 1-to-1 expected Fed response overlay，不是 3-axis model.**
>
> 把 GIP 描述為「3-dimensional / 3-factor」是技術上錯誤的，因為 Policy 是從 Growth/Inflation
> 算出來的 reaction function，不是獨立 measurement。Hedgeye 自家行銷文有時也會誤導性地說
> 「3 dimensions」— 嚴謹定義要參考 McCullough 自己的 operational description。

### Time horizons (per CMC/Opto interview)

- **Immediate-term TRADE** ≤ 3 weeks
- **Intermediate-term TREND** ≥ 3 months（典型 1 quarter）— Quads 主要是 TREND 維度框架
- **Long-term TAIL** within ~3 years

### Asset-allocation playbook by Quad

| Quad | 最佳 sector / asset | 最差 | Style factor 偏好 | Currency / commodity |
|---|---|---|---|---|
| **Quad 1 (Goldilocks)** | Tech, Cons Disc, Materials, Industrials, Telecom/Communication Services | Utilities, REITs, Cons Staples, Energy | High Beta, Momentum, High Leverage, Secular Growth, Mid Caps | USD neutral-to-weak; broad commodities mixed |
| **Quad 2 (Reflation)** | Tech, Cons Disc, Industrials, Energy, Financials | Telecom, Utilities, REITs, Cons Staples, Health Care | Cyclical, nominal-growth | Energy/oil ↑; bonds + gold ↓ |
| **Quad 3 (Stagflation)** | Gold, broad commodities (CRB), Energy (XLE), long-duration UST (later in quad) | High-beta equity, credit spreads widen | Defensive | USD inverse to commodities (USD↔CRB ≈ −0.97 per Hedgeye 2010s data) |
| **Quad 4 (Slowdown)** | USD (UUP), long-duration UST, Gold (safe haven), Cons Staples, Utilities | High-beta Tech, Momentum, Russell 2000 Growth, crypto, broad commodities, HY credit | High Dividend Yield, Low Beta, Min Vol, Quality | USD ↑（reserve-currency demand）|

**Backtest claim**: Hedgeye 自稱「grounded in over 27 years of back-tested history」(~1998–present for U.S. GIP)。**這是 firm-published claim，不是 independently audited**。Hedgeye 沒在 open materials 公開：asset universe / rebalancing frequency / transaction cost / regime transition handling / data revision treatment。完整 backtest 在 subscription product 內。

### 與 Greetham Investment Clock & Bridgewater 4-Box 的關係

| Dimension | ML Investment Clock (Greetham 2004) | Bridgewater 4-Box (Dalio 1996) | Hedgeye GIP (McCullough/Dale 2008+) |
|---|---|---|---|
| **Origin** | Trevor Greetham & Michael Hartnett, Merrill Lynch internal report 2004-11-10 | Ray Dalio / Bridgewater, 1996（先給 Dalio family trust，後成為 All Weather 商品）| Keith McCullough + Darius Dale, Hedgeye Risk Management |
| **Venue** | Sell-side bank research | Hedge fund internal → commercialized | Independent research firm (subscription) |
| **Axes** | Growth (vs trend) × Inflation (vs trend) — 2 軸 | Growth expectations × Inflation expectations — 2 軸 | Growth ROC × Inflation ROC — 2 軸 + derived Policy overlay |
| **Measurement** | Absolute level vs long-run trend | Expectations (market-implied + fundamental) | **Second derivative** of YoY rates |
| **Regime label** | Reflation → Recovery → Overheat → Stagflation（順時針 clock）| Rising/Falling Growth × Rising/Falling Inflation（4 boxes）| Quad 1/2/3/4（編號 + 暱稱）|
| **Asset map** | Reflation→Bonds, Recovery→Stocks, Overheat→Commodities, Stagflation→Cash | Risk-parity 在 4 boxes 之間平衡（**diversify**）| Active rotation：concentrate 在當下 quad 的 winners |
| **Intended use** | Sell-side rotation 啟發 | 平衡 risk parity 配置 | Active tactical rotation |

### 關鍵架構觀察

1. **三者都是 2-axis growth × inflation 框架**。「3-axis GIP」說法不成立。
2. **Dalio/Bridgewater 4-box 是更早的 progenitor**。Bridgewater 的 4-box 框架 1996 年就有；Hedgeye GIP 是 **refinement**，不是 invention。Fidenza Macro 獨立 write-up 明確 credits Dalio 為原創普及者。
3. **GIP 的 novelty 是 rate-of-change + process discipline**，不是新軸：(a) 用 second derivative，(b) codify rules-based playbook of sector/factor/asset winners per Quad。
4. **Intended-use divergence is the biggest practical difference.** Dalio All Weather: 「你預測不出 Quad，所以橫跨 4 個 box 用 risk parity 配置」。Hedgeye GIP: 「你 *可以* 用 ROC 數據預測 Quad，所以集中在當下 Quad」。哲學上完全相反，但用同一個 2×2 diagnostic。
5. **GIP vs Greetham 是 sibling，not parent/child**。Hedgeye 從來沒 cite Greetham & Hartnett；GIP 的 lineage 透過 Dalio/Bridgewater (via Darius Dale，他公開 acknowledge)。

### Critical Attribution Corrections (Hedgeye GIP cluster — 7 items)

1. **GIP ≠ Merrill Lynch Investment Clock**。不同作者（McCullough/Dale vs Greetham/Hartnett）、不同公司（Hedgeye vs Merrill）、不同年份（2008+ vs 2004）、不同 measurement（second derivative vs absolute level vs trend）、不同 regime label。是 cousin，不是 parent/child。

2. **GIP 不是「最早」的 4-quadrant macro 框架**。Ray Dalio / Bridgewater 至少早 12 年（1996 All Weather）就有 4-box growth × inflation 框架。「Keith McCullough invented the 4-quadrant macro model」是歷史錯誤。

3. **GIP 是 2-axis with derived Policy，不是 3-axis**。Popular summary（含部分 Hedgeye 行銷文）會說 GIP 有 3 個獨立變數。但 McCullough 自己的 operational 描述清楚 — Policy 是 **forward-looking reaction function map**，不是獨立 measurement。

4. **Darius Dale 是 co-author，不是 user**。把 GIP 完全歸給 McCullough 抹除了 Dale 的分析貢獻。Hedgeye 自家 podcast credit Dale「instrumental in creating Hedgeye's GIP Model quad-based economic outlooks」。Honest attribution: **「McCullough, Dale et al., Hedgeye Risk Management」**。

5. **「Quad 1 / Quad 2 / Quad 3 / Quad 4」是 Hedgeye-specific 命名**。Bridgewater 用「Rising/Falling Growth × Rising/Falling Inflation」；Greetham 用「Reflation → Recovery → Overheat → Stagflation」。**不要用「Quad 1」描述任何其他 4-box 框架**。

6. **「27 年 backtest history」是 firm-published，不是 independently audited**。沒有 peer-reviewed / 第三方 reproduction 存在於 open literature。Cite 時要說「Hedgeye states ...」，不要當 validated finding。

7. **「Macro regime model」是 generic term**。許多框架都把 macro 切成 regime（Greetham IC、Bridgewater 4-box、Hedgeye GIP、Ned Davis Research、Fidelity AART 等）。不要把「macro regime model」用作 GIP 的同義詞 — GIP 是其中一個 specific firm-branded implementation。

### JP integration

**None.** Hedgeye 是 US (Stamford CT) firm，研究主賣 US/EU institutional subscribers。日語 search 「ヘッジアイ GIP クアッド マクロ」只回傳 Hedgeye 自家英文頁的索引 + 不相關的 generic「macro arbitrage」書目。沒有日語學術 / 媒體 corpus 描述 GIP。

對 v4.11.0 standards：
- **不要** 加 GIP 的日語 primary source — they don't exist
- 在 standards 注明「GIP is a US English-language grey-literature primary with no Japanese integration path」
- 對日語讀者：Bank of Japan 與 JP sell-side 有自家 regime 框架（多以 BoJ reaction function + business-cycle dating 為主），但這些 **不是 GIP**，不要 conflate

### 對 `investment-macro-regime.md` 的應用

**Body depth**: 60–100 lines

**Recommended section structure**（給 v4.11.0 drafter）:

```
### Hedgeye GIP 4-Quadrant Model (McCullough, Dale, Hedgeye 2008+)

- What it is: Rate-of-change 2-axis regime framework (growth × inflation second
  derivative) with derived policy overlay, producing 4 numbered Quads.
- Quadrants table (with labels + typical Fed posture)
- Asset-allocation playbook summary (compressed table of all 4 Quads)
- Why it matters: 廣為引用的 practitioner framework；對 2010s–2020s hedge fund
  community 的 active tactical asset allocation 影響顯著
- Provenance honest statement: sibling to Greetham IC (parallel, not derived);
  descendant lineage of Bridgewater 4-box (Dalio 1996)
- Citation format examples
```

**Anti-drift guardrails 內嵌 body 的 6 條**（從 7 條 corrections 中精選）:

1. 「GIP is a 2-axis rate-of-change framework with a derived policy overlay; it is not a 3-dimensional model in the independent-variable sense.」
2. 「Hedgeye did not originate the 4-quadrant growth × inflation framework; Bridgewater / Dalio's 4-box dates from 1996, approximately 12 years earlier.」
3. 「GIP and Greetham's Investment Clock are sibling frameworks, not parent and child. They share a 2-axis growth × inflation diagnostic but differ in measurement, intended use, and authorial lineage.」
4. 「GIP is proprietary grey literature. The '27 years of backtest' claim is firm-published, not independently audited. Cite as 'Hedgeye states' rather than as validated empirical fact.」
5. 「Darius Dale is a co-architect of GIP, not a user. Canonical attribution: McCullough, Dale et al., Hedgeye Risk Management.」
6. 「'Quad 1 / Quad 2 / Quad 3 / Quad 4' is Hedgeye-specific nomenclature. Do not use it to label other 4-quadrant frameworks.」

**Citation template**:

```
McCullough, K., Dale, D., et al. (2008–present). Hedgeye Growth–Inflation–Policy
(GIP) Model. Hedgeye Risk Management, LLC. Canonical author text: McCullough, K.
(2024), Master The Market: A Hedge Fund Manager's Guide to Process and Profit
(Hedgeye ebook, self-published). Technical white paper:
https://docs3.hedgeye.com/macroria/Hedgeye_GIP_Model_Risk_Management_Process.pdf

Type: Grey literature, firm-proprietary practitioner framework.
Lineage: Refinement of Bridgewater/Dalio 1996 4-box environment framework.
Sibling (not descendant) to Merrill Lynch / Greetham Investment Clock (2004).
Status: Widely cited in practitioner macro community; no peer-reviewed validation;
backtest methodology not publicly reproducible.
```

### Open questions / gaps

1. 實際 quadrant threshold（second derivative 的精確 decision rule）— Hedgeye 沒公開
2. Backtest methodology details（universe / rebalancing / transaction cost / data revision）
3. Out-of-sample performance — open literature 無 independent audit
4. 國際 GIP coverage 細節（Hedgeye 宣稱跑 ~50 個經濟體 ~90% global GDP）— EM CPI/GDP 資料品質下的方法論未公開
5. McCullough vs Dale 的 authorship split — 沒有 documented；Dale 的 42 Macro 自家 framework 已成為 partial fork
6. *Master The Market* (2024 ebook) 是否算 reliable author text — 自出版 promotional ebook，無 ISBN registry / academic review，但是最接近 canonical author text 的東西。Cite 時要明確 self-published 標籤。

---

# Cluster B — L1 Macro Regime: Modern Monetary Theory (MMT)

## Q2. MMT canonical sources & critique stack

### 書誌（已驗證）— MMT primary canon

**Tier 1: Foundational originators**

- **Warren Mosler (1996)** *Soft Currency Economics*. 自出版，moslereconomics.com 公開分發。**MMT 起源文件**。Mosler 是前 hedge fund manager (Illinois Income Investors)，框架源自實務 trading。核心 insight 來自 1992 年 Italian bond trade — 市場在 price Italian sovereign default risk 但 Mosler 推理：Italy（當時還是 lira issuer）總是可以 credit bank reserves 來付 lira-denominated debt。Mosler 找 Italian Treasury 官員 Luigi Spaventa 確認 operational mechanics 後做 large long position，~$100M for clients。後 2012 年出 expanded edition *Soft Currency Economics II: The Origin of Modern Monetary Theory* (ISBN 9781482735437)。
- **L. Randall Wray** (2012, 2nd ed 2015, 3rd ed 2024) *Modern Money Theory: A Primer on Macroeconomics for Sovereign Monetary Systems*. Palgrave Macmillan / Springer Nature.
  - 1st ed ISBN 9780230368880
  - 2nd ed ISBN 9781137539908
  - 3rd ed (2024, Springer) DOI 10.1007/978-3-031-47884-0
  - **MMT 的 canonical academic treatment**。Wray (University of Missouri-Kansas City; Senior Scholar, Levy Economics Institute of Bard College) 是 Hyman Minsky 的學生。
- **Stephanie Kelton (2020)** *The Deficit Myth: Modern Monetary Theory and the Birth of the People's Economy*. PublicAffairs / Hachette, 325 pages, ISBN 9781541736184. **Popular canonical** + 學術之外的文化 entry point。Kelton (Stony Brook University; ex-Chief Economist, Senate Budget Committee Democratic Minority Staff under Bernie Sanders 2015; Sanders 2016/2020 campaign advisor)。Instant NYT bestseller。

**Tier 2: Other MMT primary works (supporting canon)**

- **Mitchell, W., Wray, L.R., Watts, M. (2019)** *Macroeconomics*. Red Globe Press / Macmillan, ISBN 9781137610669. **第一本完整 MMT textbook**。Bill Mitchell (University of Newcastle Australia; founder/director CofFEE) 被 credit **「Modern Monetary Theory」這個 term 的創造者**，typology 對應 Keynes 「至少 4000 年來 money 是 a creature of the state」的說法。Mitchell blog (billmitchell.org) 是 day-to-day MMT exposition 的 major primary。
- **Pavlina R. Tcherneva (2020)** *The Case for a Job Guarantee*. Polity Press, ISBN 9781509542109. Tcherneva (Bard College / Levy) 是 MMT 對 **Job Guarantee (JG)** proposal 的 leading theorist。
- **Mitchell & Mosler (2023)** *Modern Monetary Theory: Bill and Warren's Excellent Adventure*. Joint exposition.
- **Scott Fullwiler** — extensive technical work on monetary operations and Fed plumbing from MMT perspective; "Modern Money Theory: A Response to Critics" (with Bell, Wray, SSRN WP)

### 書誌（已驗證）— Intellectual ancestors

MMT 明確 synthesize 5 個既有 traditions。Cite MMT 時要 acknowledge lineage，不要當 MMT 是憑空生出來的。

- **Georg Friedrich Knapp (1905)** *Staatliche Theorie des Geldes*（英譯 *The State Theory of Money*, trans Lucas & Bonar 1924, Royal Economic Society）。**Chartalism 的創始人**。Knapp thesis: "money is a creature of law"（不是 commodity）。State currency 的 value 來自 public pay office 接受度（即還稅的能力）。Wray 明確稱 MMT 為 **neo-chartalism**。Keynes 在 1930 *Treatise on Money* 開頭引 Knapp。
- **Alfred Mitchell-Innes (1913, 1914)** "What is Money?" 與 "The Credit Theory of Money"，*The Banking Law Journal*。反對 barter-origin story；money is fundamentally **credit**（debt relationships enforced by law，tally sticks / ledgers 早於 coinage）。Keynes 1914 寫 favourable review。MMT 繼承這個 **credit view of money** 與 Knapp's chartalism 結合。
- **Abba P. Lerner (1943)** "Functional Finance and the Federal Debt." *Social Research: An International Quarterly* Vol 10 No 1, pp 38–51。**MMT policy framework 的直接知識祖先**。Lerner 的 functional finance: fiscal policy 應該以 real-economy outcomes（employment / inflation / growth）判斷，不是 balance-sheet metrics（deficit / debt level）。政府預算不是用 household 比喻來評估。Lerner 的「two laws」: (1) government 保持 total spending 在 full-employment level，調整 taxes 或 spending；(2) government 借錢 / 還錢只為了達到 target interest rate。
- **Hyman P. Minsky (1986, reissued 2008)** *Stabilizing an Unstable Economy*. McGraw-Hill. Minsky 是 Wray 在 Washington University in St Louis 的 dissertation advisor。貢獻 **financial instability hypothesis** + **employer of last resort** proposal（MMT JG 的基礎）。
- **Wynne Godley (1996, 2007)** Sectoral balances framework. Godley & Lavoie (2007) *Monetary Economics: An Integrated Approach to Credit, Money, Income, Production and Wealth*. Palgrave Macmillan. MMT 的 macro accounting 建立在 Godley **三部門 balances identity**: (Private surplus) + (Government surplus) + (Foreign surplus) = 0。政府 deficit 在會計上 = non-government surplus。

### 書誌（已驗證）— Mainstream critique（**MUST 一同 cite**）

research-team neutral framing discipline 要求每個 MMT citation 至少 pair 一個 mainstream-critique citation。

- **Paul Krugman (2019)** "Running on MMT" (NYT Opinion + blog). 反對：MMT 忽視 fiscal-monetary tradeoff via interest rates。Kelton 直接回應 in "Paul Krugman Asked Me About Modern Monetary Theory. Here Are 4 Answers" (2019-02, stephaniekelton.com)。
- **Kenneth S. Rogoff (2019+)** Multiple Project Syndicate columns including "Modern Monetary Nonsense" (2019-03)、"Central Banks' New-Old Inflationary Bias" (2024-05)。Rogoff (Harvard, *This Time Is Different* 2009 co-author) 稱 MMT 為 **"recipe for hyperinflation"**。歷史比較組: Weimar Germany / 戰間期 Austria-Hungary-Poland (per Sargent 1982) / Zimbabwe 2007–2009 / Venezuela post-2014。
- **Lawrence H. Summers (2019)** "The Left's Embrace of Modern Monetary Theory Is a Recipe for Disaster." *Washington Post* opinion 2019-03-05. Summers (前美財長 1999–2001, 哈佛 President Emeritus) 稱 MMT 為 **"the supply-side economics of our time"** + **"voodoo economics"**（直接 echo George H.W. Bush 1980 用來罵 Reagan supply-side 的 term）。
- **Olivier Blanchard (2019)** "Public Debt and Low Interest Rates." AEA Presidential Address 2019-01；published *AER* 109(4): 1197–1229 (2019-04)。Blanchard (2023) *Fiscal Policy under Low Interest Rates*. MIT Press, ISBN 9780262544870。**這是 partial endorsement of one MMT conclusion，不是 endorsement of MMT itself**。Blanchard argument: 當 r < g 為 extended period（戰後常見）時，debt rollover 不需要 eventual tax increase，public debt 的 welfare cost 低。**廣為被誤讀為 MMT endorsement**；不是。Blanchard 仍保留 multiple-equilibrium risk concerns + 拒絕 MMT operational framework。
- **N. Gregory Mankiw (2020)** "A Skeptic's Guide to Modern Monetary Theory." NBER Working Paper 26650 (2020-01). Published *AEA Papers and Proceedings* 110: 141–144 (2020-05). DOI 10.3386/w26650. Mankiw (Harvard) 承認 MMT 含「kernels of truth」about monetary operations，但 novel policy prescriptions 不能 cogently follow from premises。**最 even-handed 的 mainstream critique，是 neutral citation 的理想 entry point**。
- **Thomas I. Palley (2015)** "Money, Fiscal Policy, and Interest Rates: A Critique of Modern Monetary Theory." *Review of Political Economy* 27(1): 1–23。**這是 Post-Keynesian 內部的 critique，不是 mainstream 的**。Palley argument: MMT 是「a restatement of established Keynesian monetary macroeconomics」，過度簡化（忽視 Phillips curve / real-and-financial-sector stability / open-economy constraints）。Cite Palley 顯示 MMT 在自己 heterodox neighborhood 內也有 critic，不只是 orthodoxy 反對。
- **Jerome H. Powell (2019)** Senate Banking Committee testimony, 2019-02。Powell (Fed Chair) 原話: **"The idea that deficits don't matter for countries that can borrow in their own currency I think is just wrong"** + 沒見過 carefully worked out description of MMT。**這是 Fed 官方 informal-but-on-record 立場**。
- **Marc Lavoie** — Post-Keynesian; argues MMT 依賴 **consolidating Treasury + central bank balance sheet**，他稱 analytically "confusing"。
- **Scott Sumner (Market Monetarism)** — Sumner (Bentley / Mercatus) critique MMT 對「saving」的非標準定義，主張 monetary policy not fiscal policy 是 nominal GDP management 正確工具。Econlib "Understanding MMT" (2019, 2021)。
- **Noah Smith** — Bloomberg Opinion / Noahpinion blog; 主要反對：MMT inflation-control mechanism (raise taxes when inflation 升) 在 democratic politics 下 operationally implausible。

### 7 個 Core MMT propositions（精確複述用，**不是 worker 自己的聲音**）

1. **Operational sovereignty**: 自發行 fiat、只借自家貨幣、float exchange rate 的政府（US、Japan、UK、Canada、Australia、Sweden 符合；Eurozone members 與 dollarized economies **不符合**）**不會被迫 default** 在 domestic-currency 義務上。Default 永遠是政治選擇，不是 financial necessity。[Wray 2012 Ch 1-3; Kelton 2020 Ch 1]

2. **Binding constraint is inflation, not debt-to-GDP**: 支出變問題是當 aggregate demand 超出經濟 real-resource capacity（labor / materials / productive capital）。Debt-to-GDP ratio 是 accounting artifact；relevant metric 是新支出是否與 private sector 競爭已用 real resources。[Kelton 2020 Ch 2]

3. **Taxes drive money, not fund spending**: MMT 觀點下 operational sequence 是 spend-first-then-tax，不是 tax-first-then-spend。Tax liabilities denominated in state currency 創造 currency demand。Taxes drain reserves；不 "finance" government。[Wray 2012 Ch 2; Mosler 1996]

4. **Deficits = non-government surplus (accounting identity)**: 從 Godley sectoral balances，government deficit 在定義上是某處 surplus（private domestic net savings + current account surplus）。**「Balanced budget」強制 private-sector deficit 或 current account surplus**。[Godley & Lavoie 2007]

5. **Functional finance**: Fiscal policy 應 target real outcomes (employment / capacity utilization / inflation)，不是 balance-sheet metrics。直接繼承 Lerner 1943。[Lerner 1943; Wray 2012 Ch 6]

6. **Interest rates are a policy variable, not a market-determined price**: MMT 觀點下 central bank 用 operational choice set short rate，也可以 anchor long rate（BoJ 2016–2024 YCC 是 demonstration）。「Bond vigilantes」story 不適用 sovereign currency issuer。[Kelton 2020 Ch 3]

7. **Job Guarantee as automatic stabilizer**: 取代 discretionary fiscal stimulus + monetary policy，MMT 提議 permanent federal job offer at fixed wage，作為 counter-cyclical buffer stock of employed labor。Recession 時擴大、boom 時收縮。Tcherneva 2020 argues 同時是 price-stability mechanism (JG wage anchors floor) + full-employment mechanism。[Tcherneva 2020]

### Mainstream critique（精確複述用 — 與 MMT propositions 並列）

1. **Inflation control in practice 不對稱** (Rogoff/Summers/Mankiw): MMT 提議的 brake 是「inflation 出現時 raise taxes / cut spending」。Mainstream 反對：legislatures 不會 preemptively raise taxes — inflation control 在實務上 devolve 到 central bank，central bank raise rates，重新打開 MMT 否認的 fiscal crowding-out channel。**2022 inflation spike 廣為 cite 為 practical stress test**。

2. **Interest rate effects 被忽略** (Krugman): rate 顯著上升後 fiscal-cost calculus 變化大；debt service 占 budget 比例可快速擴大。

3. **歷史 hyperinflation** (Rogoff / Sargent 1982): Weimar / Austria-Hungary-Poland / Zimbabwe / Venezuela 為 fiscal dominance + 政治壓力 monetization 產生 hyperinflation 的案例。MMT 反駁：每個案例都涉及 real-resource collapse 或 loss of monetary sovereignty (foreign-currency debt)。

4. **Operational-vs-structural confusion** (Summers / Lavoie): MMT 正確描述 Fed 可 credit accounts (operational level)，**但不代表沒有經濟後果 (structural level)**。Currency value / inflation expectations / private-sector behaviour 都會回應 fiscal policy。

5. **Open-economy blindness** (Palley): MMT strongest claims 假設 floating FX + domestic-currency debt。對 import-dependent 經濟（多數 EU 與東亞），fiscal expansion 可壓力 FX，import price 上漲，產生 imported inflation — MMT 對此 underweight。

6. **Consolidated balance sheet fallacy** (Lavoie / Palley): MMT accounting 把 Treasury + central bank 當一個 entity。多數先進經濟法律與 operational 上是分開的，treating-as-one obscures 制度張力。

7. **Fed/Treasury 官方拒絕** (Powell / Kuroda): 美 Fed Chair 與 BoJ Governor 都公開 distance 自己。

8. **2019 IGM Forum poll**: Chicago Booth survey of leading academic economists — **零** respondents agree with MMT 最強的 deficit claims。**最清楚的「MMT 不是 mainstream consensus」 datum**。

### Critical Attribution Corrections (MMT cluster — 7 items)

1. **「MMT = just print money」**— **WRONG**。MMT 明確 identify inflation / real-resource constraint 為支出 binding limit。Kelton *Deficit Myth* Ch 2 整章講這個。把 MMT 說成「unlimited money printing」= 沒讀過 primary source。

2. **「MMT started with Kelton」**— **WRONG**。Mosler 1996 是起源；Wray 2012 是 canonical academic treatment；Kelton 2020 是 popular canonical。Worker 應該 cite 三者 with awareness of distinct roles。Italian bond trade story (1992) 是直觀 origin anecdote。

3. **「Japan proves MMT works」**— **OVERCLAIM**。Kelton cite Japan 為 consistent with MMT；Nersisyan & Wray (Levy WP 985, 2021, "Has Japan Been Following Modern Money Theory Without Recognizing It? No! And Yes") 給 nuanced yes-and-no。Mainstream critic (Takatoshi Ito Project Syndicate 2021-12) 指出日本人口老化改變 intergenerational calculus；2022–2024 yen weakness + BoJ YCC exit 也 complicate「no inflation」story。Worker 必須 cite 兩邊。

4. **「MMT is consensus economics」**— **WRONG**。2019 IGM poll 零 endorsement。MMT 是 **heterodox, contested framework**。

5. **「MMT and fiscal dominance are the same」**— **WRONG BUT RELATED**。「Fiscal dominance」標準 macro 中指 fiscal policy 約束 monetary policy 的狀況。MMT describe 為 **normal state of affairs**；mainstream economics 視為 **pathology** (Sargent & Wallace 1981 "Some Unpleasant Monetarist Arithmetic" 是 classic statement)。兩者交集但不是同義詞。

6. **「Chartalism and MMT are the same」**— **NEARLY BUT NOT QUITE**。MMT 是 neo-chartalism (Wray 用語) — 繼承 Knapp state theory 但加 (a) sectoral balances from Godley、(b) functional finance from Lerner、(c) endogenous money from Post-Keynesians、(d) Job Guarantee from Minsky/Tcherneva、(e) Mosler operational descriptions of central bank plumbing。Chartalism 自己只是「money is state creature」claim；MMT = chartalism + macro framework + policy agenda。

7. **「Summers endorses MMT because Blanchard partially does」**— **WRONG**。兩者 distinct。Blanchard 2019 argues low-r-vs-g environment make debt less costly than orthodox models assumed；sympathetic to one MMT conclusion 但用 mainstream (overlapping generations / welfare) framework 推導，**不是** MMT premises。Summers 一致 hostile to MMT。

### JP integration — **High**（Japan 是 MMT 最廣 cite 的 real-world case，也是最 contested 的）

**The Japan-validates-MMT argument** (Kelton, Mitchell, Wray):
- Debt-to-GDP > 250%（先進國最高）
- 10-year JGB yield ~zero from ~2016 to ~2022（BoJ YCC 2016–2024）
- Average CPI inflation ~zero for ~20 years (pre-2022)
- 沒 insolvency / currency collapse / hyperinflation
- → orthodox prediction (bond vigilantes / crowding out / inflation) 被 case 證偽

**The Japan-does-NOT-validate-MMT arguments**（**Tier 1 JP critique**）:

- **藤巻健史 Takeshi Fujimaki** — 前 Morgan Bank Japan 代表、前參議院議員 (Nippon Ishin no Kai)。Fujimaki argues 日本是 **「MMT 的実験場」** (Bloomberg Japanese 2019-04-10)，最終會 prove MMT wrong via fiscal collapse / hyperinflation。即使 sovereign issuer 法律上不會 default，hyperinflation 摧毀公民 saving 的 real value，產生 **functional default** on social contract。多本警告 BoJ balance sheet expansion + fiscal expansion 是 yen collapse 的倒數。
- **黒田東彦 Haruhiko Kuroda** — BoJ 總裁 2013–2023。在 CEBRA New York 2019-07，Kuroda 公開「**全く同意できない**」(cannot agree at all) MMT。2019-11-13 衆議院 Finance Committee 重申「MMTの議論を裏付けていることは全くない」(does not at all validate MMT arguments)。**這是 BoJ 官方 on-record 立場**。Nikkei coverage 是 JP primary。
- **伊藤隆敏 Takatoshi Ito** — Columbia / GRIPS。在 Project Syndicate "Does Japan Vindicate Modern Monetary Theory?" (2021-12)，Ito argues 日本表面 fiscal success 隱含 **intergenerational transfer**：debt 累積，working-age 人口縮小 → 未來 worker per-capita 負擔加重。「No free lunch」。Ito 預測 MMT 在日本的 experiment 會在 demographic timeline 上失敗。
- **櫻川昌哉 Masaya Sakuragawa** — 慶應大學。論文「長期停滞・低金利下の財政・金融政策 — MMTは経済理論を救うか？」金融経済研究 44 (2021-12)。
- **早川英男 Hideo Hayakawa** — 前日銀理事。批評 MMT 是純「accounting talk」缺乏 price 與 equilibrium 概念。

**Japanese MMT proponents**:

- **藤井聡 Satoshi Fujii** — 京都大学，京都大学レジリエンス実践ユニット長、前 PM 安倍 special advisor。著有 *MMTによる令和「新」経済論：現代貨幣理論の真実* (勁草書房 2019)。**JP 最 leading academic MMT proponent**。
- **中野剛志 Takeshi Nakano** — 公共知識分子、前 METI 官員。稱 MMT 為「Post-Keynesian 經濟學的集大成」，主張批評 MMT 的日本 orthodox 經濟學者是「跟不上時代」。文藝春秋 articles。
- **三橋貴明 Takaaki Mitsuhashi** — 經濟評論家、経世論研究所 founder。日本通俗 MMT advocate。
- **西田昌司 Shoji Nishida** — 自民黨參議員。2020-05 (COVID 中) 公開主張 MMT-based 0% consumption tax，在 Diet 質詢麻生財相 about MMT。自 2013 與 Fujii / Nakano 共同主持 Diet 學習會。

**JP-focused MMT academic paper**: **Yeva Nersisyan & L. Randall Wray (2021)** "Has Japan Been Following Modern Money Theory Without Recognizing It? No! And Yes." Levy Economics Institute Working Paper No. 985. 立場：日本 operational practice (BoJ 與 MOF cooperation / JGB 吸納 / YCC) 是 consistent with MMT 描述 sovereign currency system 如何 actually function（**「yes」**），**但** 日本政策制定者沒有 explicitly adopt MMT framework，仍用 orthodox debt-sustainability rhetoric（**「no」**）。

**2022–2024 inflation stress test 更新**:
- 日本 CPI 2022 年破 2% (數十年首見)；BoJ 維持 YCC 至 2024-03 後 exit
- 日圓對 USD 大幅貶值（140s → 160s 2024），MOF 介入 — partial evidence 顯示 Fujimaki 派 currency-collapse concern 不純是理論
- MMT 派論點：日本通膨是 cost-push (energy / 日圓貶值)，不是 demand-pull from fiscal excess — 所以 inflation constraint 沒被 fiscal triggered
- Critics 反駁：goalpost-moving
- **research-team workers writing about Japan post-2024 必須 cite 兩邊** — case 是 genuinely open

**JP 整合 line budget 配額**: 大約 40–60 lines 在 `investment-macro-regime.md` 的 MMT 段落內專門寫 Japan case。同時 cite Kuroda 拒絕 + Fujii 認可 + Ito intergenerational + Nersisyan-Wray nuanced。

### 對 `investment-macro-regime.md` 的應用

**Tier**: **Tier 2** (primary citation in background theory cluster, **not** Tier 1 core regime model)

**Rationale**: MMT 不是 Dalio 2018 / Hedgeye 4-quad / Damodaran risk-premium 那種 predictive regime model。它是 **descriptive framework for government fiscal behaviour** + sovereign spending real constraint。Investment workers 需要它作為 **background theory** 來解釋 post-2008 macro 環境，不是 trade-signal generator。

**Body depth**: ~120–180 lines

**Anti-drift guardrails to embed in standards file**:

1. **Dual-citation rule**: 每個 MMT claim 必須 alongside 至少 1 個 mainstream-critique citation。No standalone MMT citation without paired critique。
2. **Attribution discipline**: 用「MMT proponents argue...」/「Kelton 2020 claims...」/「Wray 2012 frames...」— 從不用「MMT shows that...」/「MMT proves...」。Worker 不是 MMT advocate。
3. **Banned phrases**: 「just print money」「MMT solves」「Japan proves MMT」「deficits don't matter」「free lunch」（除非 directly quoting critic）
4. **Scope restriction note**（required preamble）: 「MMT's claims apply to sovereign currency issuers with floating exchange rates and domestic-currency debt (US, Japan, UK, Canada, Australia, Sweden). They do NOT apply to Eurozone members, emerging markets with significant USD debt, or dollarized economies.」
5. **Post-2022 inflation caveat**（required）: 「The 2021–2023 inflation episode is the contested empirical test of MMT in the modern record. Workers must present both interpretations.」
6. **IGM Forum one-liner**（required）: 「A 2019 University of Chicago IGM Forum poll of leading academic economists found zero agreement with MMT's strongest deficit-irrelevance claims. MMT is a heterodox, contested framework, not textbook consensus.」
7. **Three-way labeling convention**: 引用 MMT 的 analytical passage 把 source label 為 **[MMT primary]** / **[mainstream critique]** / **[Post-Keynesian internal critique — Palley, Lavoie]**，讓讀者看到 lineage。
8. **Japanese context specifically requires**: cite 兩邊 — Kuroda 拒絕 + Fujii 認可。不要把 Japan 表現為「proof」或「refutation」without acknowledging live debate。

---

# Cluster C — L1 Macro Regime: RAI (Risk Appetite Index)

## Q3. RAI canonical disambiguation (Credit Suisse vs Goldman vs Citi vs State Street)

### Scope statement

「Risk Appetite Index」(RAI) 是 investment bank / central bank / 學術界用來測 markets 處於 risk-on (appetite-for-risk) 還是 risk-off (aversion) 的 sentiment / positioning indicator family。**這個 term 是 genuinely ambiguous** — 2002–2008 之間至少有 8 個不同 methodology 的「RAI」variants 被發表（cross-sectional rank correlation / linear regression / option-implied densities / fund-flow imbalance / composite z-score）。

**Critical disambiguation upfront**: **Kumar & Persaud (2002)，不是 Wilmot，是 cross-sectional RAI class 的真正知識祖先**。Credit Suisse / Wilmot (2004) index 最 best described 為 Kumar-Persaud 的 linear-regression extension（加 multi-asset coverage）。Phase 1 「Credit Suisse Wilmot original (early 2000s)」假設 **partially incorrect**，需要 correction。

### 書誌（已驗證）— Tier A canonical

1. **Kumar, M. and A. Persaud (2002)** "Pure Contagion and Investors' Shifting Risk Appetite: Analytical Issues and Empirical Evidence." *International Finance* **5(3): 401–436**。
   - **Peer-reviewed** journal article in *International Finance* (Wiley/Blackwell)
   - Originated **Global Risk Appetite Index (GRAI)** concept: 任一時點，若 market aggregate risk appetite 變化，risky assets cross-section 的 excess return 與 past volatility 之間應出現顯著 **monotonic relationship**
   - Methodology: Spearman rank correlation between monthly/quarterly excess returns and past volatilities (prior 250 business days to avoid overlap)
   - 原始 application: FX markets + US sector equities
   - 後被 IMF + JPMorgan 用作 internal RAI 基礎 (per Bank of Canada survey)
   - **Tier A** peer-reviewed primary source

2. **Illing, M. and M. Aaron (2005)** "A Brief Survey of Risk-Appetite Indexes." *Bank of Canada Financial System Review* (June 2005): **37–43**。
   - 央行出版，公開 PDF: https://www.bankofcanada.ca/wp-content/uploads/2012/01/fsr-0605-illing.pdf
   - Survey **十** 個 risk appetite / sentiment indexes:
     - *Atheoretic*: JPMorgan LCVI / UBS Investor Sentiment / Merrill Lynch Financial Stress Index / Westpac RAI
     - *Theory-based*: BIS (Tarashev/Tsatsaronis/Karampatos 2003) / BoE (Gai & Vause 2004) / CSFB (Wilmot/Mielczarski/Sweeney 2004) / Kumar-Persaud GRAI (2002) / State Street ICI (Froot & O'Connell 2003) / Goldman Sachs Risk-Aversion Index
     - 加 VIX 為 quick proxy
   - Key finding: **Indexes don't always tell the same story**。Theory-based measure 之間 correlation 常常小或負；BIS / ICI / GS 都是 equity-based 但 cross-correlation 卻最低。
   - 提供完整 bibliography 給每個 variant — **這是 indispensable bibliography hub**
   - **Tier A** central-bank primary source

3. **Uhlenbrock, B. (Deutsche Bundesbank, 2009)** "Financial markets' appetite for risk – and the challenge of assessing its evolution by risk appetite indicators." IFC Bulletin No. 31, BIS, pp 221–293.
   - Technical reconstruction of GRAI 完整 mathematical framework (CAPM motivation / linear-regression vs rank-correlation variants / factor-extended F-GRAI)
   - **直接 cite Wilmot, Mielczarski, Sweeney (2004) as a linear-regression extension of Kumar-Persaud** — 這是「Wilmot 是 extension 不是 origin」claim 的關鍵 corroboration

4. **Misina, M. (2003)** "What Does the Risk-Appetite Index Measure?" *Bank of Canada Working Paper* No. 2003-23。Critical analysis of what GRAI actually measures。

5. **Gai, P. and N. Vause (2005)** "Measuring Investors' Risk Appetite." *Bank of England Working Paper* No. 283 (2005-11)。Distinguishes "risk appetite" (Arrow-Pratt attitude) from "risk aversion to outcomes"；ratio-of-full-distributions method；reports in *levels* rather than changes。

### 書誌（已驗證）— Variants disclosed as alternatives

| Variant | Author(s) & date | Publication | Method | Notes |
|---|---|---|---|---|
| **Credit Suisse First Boston RAI** ("Wilmot RAI") | Wilmot, J. / Mielczarski, P. / Sweeney, J. (2004-02) | CSFB *Global Strategy Research: Market Focus* (subscription) | Cross-sectional **linear regression** of excess returns on past volatilities; slope = risk appetite | 64 bond+equity indexes, DM+EM, daily. **Grey-literature primary source**（subscription CSFB bulletin）。Methodology 在 Illing-Aaron 2005 + Uhlenbrock 2009 中文獻化。 |
| **Global Risk Appetite Index (GRAI)** | Kumar, M. / Persaud, A. (2002) | *International Finance* 5: 401–436 | Spearman rank correlation excess returns ↔ past vol | **Oldest peer-reviewed**；後被 IMF & JPMorgan 採用 |
| **BIS Risk Appetite Index** | Tarashev, N. / Tsatsaronis, K. / Karampatos, D. (2003-06) | *BIS Quarterly Review*: 57–65 | Ratio of left-tail statistical vs subjective (option-implied) distributions; GARCH + volatility smile | Monthly equity data |
| **Bank of England RAI** | Gai, P. / Vause, N. (2004-12) | *Bank of England Financial Stability Review*: 127–136 | Ratio of full distributions (vs BIS's left-tail ratio) | 2005 expand 為 BoE WP 283 |
| **State Street Investor Confidence Index (ICI)** | Froot, K.A. / O'Connell, P.G.J. (2003-12) | **NBER Working Paper 10157** "The Risk Tolerance of International Investors" (DOI 10.3386/w10157)；State Street Global Markets 2003 launch | Holdings-based: institutional buy/sell imbalance from State Street global custody database | **100 = neutral**。月底前第 2 個 Tuesday 10am ET 公佈。**Note: NBER paper 是 10157，不是 8226 — Phase 1 假設錯**。 |
| **Goldman Sachs Risk-Aversion Index** | GS Economics Research (2003-10) | GS *The Foreign Exchange Market* (subscription) | Standard consumption-CAPM model with time-varying Arrow-Pratt risk-aversion coefficient | Monthly: US per-capita consumption / 3M T-bill / inflation-adjusted SPX。**Risk-Aversion**, not Risk Appetite — inverse semantics。**「GS RAI by Jan Hatzius」是 misattribution** — Hatzius 是 GS Chief Economist 但與 Risk-Aversion Index 不直接連結。 |
| **JPMorgan LCVI** | Kantor, L. / Caglayan, M. (2002) | JPM *Global FX Research: Investment Strategies* No. 7 | Percentile-based composite of spreads / VIX / implied FX vol / GRAI 為 subcomponent | Atheoretic composite |
| **UBS Investor Sentiment Index** | Germanier, B. (2003-09) | UBS *FX Note* | Rolling z-score ("sigma-score") composite of spreads / VIX / gold / high-low risk equity ratio | Atheoretic |
| **Merrill Lynch Financial Stress Index** | Rosenberg, D. (2003-06) | Merrill Lynch *Market Economist* | Rolling z-score composite incl put/call ratio + short interest/open interest | Atheoretic |
| **Westpac RAI** | Franulovich, R. (2004) | Internal | Daily-change composite z-score | Atheoretic |
| **Citi Panic/Euphoria Model ("Levkovich Index")** | Levkovich, T. (Citigroup, 1990s; published Barron's by 2006) | Citi Equity Strategy; widely cited Barron's, Ritholtz 2006/2008 | 9-component composite | **Not in Illing-Aaron survey** — distinct lineage from RAI family。Levkovich 2021 過世；Citi 仍持續發布。 |
| **BofA Global Fund Manager Survey / Bull & Bear Indicator** | Hartnett, M. and team (BofA ML monthly survey, indicator formalized ~2002; B&B Indicator since ~2013) | BofA Global Research (subscription) | 6-component composite (allocations / flows / credit / technicals / breadth / positioning) scaled 0–10 | **「16 sell signals since 2002, right 63% of the time」per 2024 disclosure**。**「BofA Global Investor Confidence Index」這個名稱不存在** — 真正的是 Bull & Bear Indicator。 |

### Canonical selection rationale

**Revised recommendation**: Use **Kumar & Persaud (2002)** as primary citation for cross-sectional RAI concept; **Wilmot/Mielczarski/Sweeney (2004)** as practitioner benchmark; **Illing & Aaron (2005)** as survey-level anchor.

Reasoning:

1. **Longest academic lineage**. Kumar-Persaud (2002) 是 peer-reviewed *International Finance* 文章，比所有 variant 早。每個後續 RAI methodology 都 cite 它；Wilmot et al. (2004) 明確是 Kumar-Persaud 的 linear-regression extension (per Uhlenbrock + Illing-Aaron)。

2. **Credit Suisse / Wilmot RAI is grey literature**。Wilmot/Mielczarski/Sweeney (2004) 在 CSFB *Market Focus* (subscription-only occasional publication)。Methodology 只在 Illing-Aaron (2005) 與 Uhlenbrock (2009) 中 second-hand documented。把它當 *the* canonical cite 會 reproduce v4.9.0 已 flag 過的 Hedgeye/Greetham 同樣問題。

3. **Longest continuous history for "Credit Suisse RAI" branding** — yes, CS 自 2004 起 daily publish；ResearchGate 上有「Credit Suisse RAI 1981-2011」chart 表示 CS 把 series **backfill** 到 1981。但 **index 直到 2004-02 才存在**；pre-2004 是 backfill 重建。標準做法但要 flag。

4. **Canonical practitioner brand vs canonical academic concept**。Practitioner 在 2010–2020 間 cite「risk appetite index」最常引 Credit Suisse / Wilmot brand。但對 investment-macro-regime.md 重視 primary-source rigor，academic-origin citation (Kumar-Persaud 2002) 是 *earlier* + *peer-reviewed*。

5. **Wilmot 約 2017–2018 離開 Credit Suisse**，與 CS 數據科學主管 Aric Whitewood co-found XAI Asset Management / WilmotML。James Sweeney 留 CS。CS 收購為 UBS (2023) 後 RAI continuity 不明。

**Recommended citation stack for `investment-macro-regime.md`**:
- Primary: Kumar & Persaud (2002) *International Finance* 5: 401–436
- Practitioner canonical: Wilmot, Mielczarski, Sweeney (2004) as cited in Illing & Aaron (2005)
- Survey anchor: Illing & Aaron (2005) *Bank of Canada Financial System Review* 37–43
- Variants disclosed: State Street ICI (Froot & O'Connell NBER WP 10157, 2003), BIS (Tarashev et al. 2003), BoE (Gai & Vause 2005), Citi Panic/Euphoria (Levkovich), BofA Bull & Bear (Hartnett)

### Formula / components 速覽

**Kumar-Persaud GRAI (canonical academic)** — 在每個時點 *t*，rank cross-section of *N* risky assets by:
- (a) past-period realized volatility σᵢ (typically prior 250 trading days)
- (b) excess return E(Rᵢ) − R_f over subsequent monthly/quarterly period
- 計算 Spearman rank correlation ρ between (a) (b) across *N* assets。
- Risk appetite **high** when ρ > 0（high-vol assets 跑贏 → investors paying for risk）
- Risk appetite **low** when ρ < 0（low-vol assets 跑贏 → flight to safety）

**Credit Suisse RAI / Wilmot linear-regression version** — 同樣 intuition 但用 **linear regression** of excess returns on past volatilities：
- E(Rᵢ,t+1) − R_f = αₜ + βₜ × σᵢ,ₜ + εᵢ
- Slope coefficient βₜ *is* RAI level
- Universe: **64 indexes**（bonds + equities, DM + EM, daily）；DM 用 local currency；EM 用 USD
- CS 公開為 standardized / z-scored deviation；threshold 在公開域**未** 由 CS 揭露
- Practitioner 慣用 **−3σ ≈ panic** / **+3σ ≈ euphoria**；這是 inferred from chart annotation，**不是** CS-disclosed

**State Street ICI (flow-based, distinct mechanism)** — 基於 State Street proprietary custody database (~15% of global investable assets)：
- 測 institutional investors **actual trades** — risky asset allocation 變化
- **100 = neutral**。> 100 = increasing risk tolerance；< 100 = decreasing
- 每月公佈，每月底前第 2 個 Tuesday 10am ET
- Per Froot & O'Connell: 區別 risk appetite 與 risk *valuation*，因為用 quantities (flows) not prices

**Citi Panic/Euphoria Model (Levkovich)** — 9 components weighted composite:
1. NYSE short interest ratio
2. Margin debt
3. Nasdaq daily volume as % of NYSE
4. Investors Intelligence + AAII bullishness composite
5. Retail money fund balances
6. Put/call ratio
7. CRB futures index
8. Gasoline prices
9. Put/call price-premium ratio
- Calibration (per Advisor Perspectives 2011): **Panic threshold < 0.17**, **Euphoria threshold > 0.38**
- Contrarian: panic = bullish forward signal; euphoria = bearish

**BofA Bull & Bear Indicator (Hartnett)** — 6-component composite, 0–10 scale:
1. Hedge fund equity positioning
2. Global equity / debt fund flows
3. Long-only fund allocations vs history
4. Market breadth
5. Credit technicals
6. Equity technicals
- **Buy signal: < 2.0** (contrarian bullish)
- **Sell signal: > 8.0** (contrarian bearish)
- **Track record: 16 sell signals since 2002, 63% accurate** (per BofA 2024)

### Historical track record 速覽

**Kumar-Persaud GRAI** — 2002 paper 回測：1997 Asian crisis + 1998 Russia crisis 都呈現 sharp rank-correlation break。Illing-Aaron 2005 qualitative test: GRAI 正確 identify 1998 Russia「low risk appetite」+ 2003 rebound「high」；但在 1990s peak / 2000 bear start / 9/11 給 ambiguous 信號。

**Credit Suisse RAI (Wilmot)** — Illing-Aaron qualitative score: CSFB 在 5 次 major episode 中給對 4 次 (1998 Russia, 1990s peak, 2000 bear, 9/11, 2003 bull) — **theory-based measure 中 best-in-class**。Documented panic call: 2012-01 (Eurozone crisis)、2015-08~10 (China devaluation)、2016-01 (oil bottom)、2018-07 (near panic)、2020-03 (presumably COVID — 未 directly documented in retrieved sources)。

**State Street ICI** — 2003 launch；Illing-Aaron score 為 1998 Russia 與 2003 rebound correct，其他 episode 為 neutral / wrong。

**Citi Panic/Euphoria Model** — Levkovich own paper 主張 6–12 月 forward return predictive power。2024 Q1 hit euphoria；2019 early panic 在 2019 rally 之前。

**BofA Bull & Bear** — 「right 63% of the time」per BofA disclosure。2018 / 2021 / 2024 / per 2026 reporting 早 2026 trigger extreme sell。

**Peer-reviewed validation**: Kumar-Persaud 2002 / Misina 2003 BoC WP 2003-23 / Gai & Vause 2005 BoE WP 283 / Coudert & Gex 2006 Banca d'Italia WP 586 / Gonzalez-Hermosillo 2008 IMF WP/08/85 / Bundesbank Uhlenbrock 2009 結論「results of RAI indicators depend on particular specification and input choices」— 沒有單一 RAI definitively validated。

**最 honest 的學術 caveat (Illing-Aaron 2005)**: *"It seems premature to rely on any given index when assessing risk appetite."* **這必須 quote 進 v4.11.0 standards file**。

### Critical Attribution Corrections (RAI cluster — 10 items)

1. **Wilmot 沒有在「early 2000s」publish original RAI**。Kumar & Persaud (2002) 更早，且在 peer-reviewed journal。Wilmot/Mielczarski/Sweeney (2004-02) 在 CSFB *Market Focus* extend 到 linear regression + 64-index multi-asset cross-section。**Phase 1 hypothesis 必須 revise**。

2. **「Credit Suisse RAI 1981-2011」charts 是 backfilled**。實際 live index 始於 2004-02；pre-2004 是 historical reconstruction，標準做法但要 flag。

3. **「Credit Suisse launches Risk Appetite Index」(Wealthbriefing 2008-05)** 指的是 **tradable product**，不是 original index — CS 2008-05 launch 一個 European tracker certificate 用 RAI 為 signal。**不要** 與 index launch 混淆。

4. **Wilmot 的 Credit Suisse tenure**: Chief Global Strategist / Head of Macro Research at CS for > 30 years。離開 ~2017–2018 co-found XAI Asset Management。James Sweeney 留 CS。

5. **RAI ≠ VIX**。Per Illing-Aaron Table 2 correlation: CS RAI 與 VIX 相關 = 66% (positive 表示 negative RAI = high VIX)；CS RAI 與 GRAI (Kumar-Persaud) = **−2%**，effectively zero — 這兩個用相同 theoretical 動機但 capture 不同東西。

6. **RAI 是 positioning / sentiment-based，不是 fundamental**。沒有 RAI variant 用 GDP / earnings / valuation 為 input — 全部 derive from market price / flow / cross-sectional return pattern。

7. **「Goldman Sachs RAI by Jan Hatzius」(Phase 1 hypothesis) 是 misattribution**。Goldman Sachs Risk-*Aversion* Index (注意 inverse semantics) 來自 *The Foreign Exchange Market* (2003-10)，是 GS Economics Research publication。Consumption-CAPM 構造，**不** 與 Hatzius specifically 連結。Hatzius 是 GS Chief Economist (US research)，與 Current Activity Indicator + FCI 連結，不是 Risk-Aversion Index。

8. **「BofA Global Investor Confidence Index」這個 named product 不存在**。BofA 的 sentiment flagship 是 **Bull & Bear Indicator** (Hartnett team) + **Global Fund Manager Survey**。把這個 cite 為「BofA Global Investor Confidence Index」會 conflate BofA 與 State Street ICI。

9. **CSFB vs CS branding**。「CSFB Risk Appetite Index」(Credit Suisse First Boston) 是 2004–2006 正確歷史名；「Credit Suisse Global Risk Appetite Index」/「CS GRAI」是 2006 rebrand 後的名字。**兩個名字 + 同一個 index**。

10. **State Street ICI authors**: Kenneth A. Froot (Harvard Business School Director of Research) + Paul G.J. O'Connell (State Street Associates Director)。Peer-reviewed origin: **NBER Working Paper 10157 (2003-12)**, "The Risk Tolerance of International Investors" — **不是 8226 as Phase 1 hypothesis assumed**。DOI: 10.3386/w10157。

### JP integration assessment

**No Japanese equivalent to RAI class identified in primary sources**。

Findings:
- **Bank of Japan Financial System Report**（半年刊）— 含 financial-cycle heat map，14 個指標 (stock prices / credit-to-GDP / real-estate price 等) green/yellow/red overheating/undercooling。是 macroprudential heat map，**不是** scalar 「risk appetite index」。BoJ 2025-04/10 報告質性描述 risk appetite 但無數值 index。
- **Nomura** — 沒有公開「Nomura Risk Appetite Index」。Nomura Asset Management commentary 用「risk-on」質性描述。
- **Daiwa / Nikko / Mizuho** — 無 documented JP-specific RAI variant。
- **Nikkei / JPX** — 發 price index (Nikkei 225 / TOPIX leverage) 但無 sentiment composite。

**Assessment for v4.11.0**: 若 JP coverage 必要，最 honest option 是 cite **BoJ Financial System Report heat map** 為 closest Japan-official analogue (macroprudential signal rather than trading-desk sentiment)，並 acknowledge 沒有公開 bank-published JP RAI。**不要 fabricate「Nomura RAI」** — 這會 reproduce v4.9.0 試圖避免的 attribution problem。

**Japanese citation suggestion**:
- 日本銀行『金融システムレポート』(BoJ *Financial System Report*, semi-annual)。報告中的「金融活動指標のヒートマップ」(financial-activity heat map) 功能上是 macroprudential risk-appetite proxy。

### 對 `investment-macro-regime.md` 的應用

**Tier**: **Tier 2** (practitioner tool with genuine academic lineage through Kumar-Persaud 2002, but grey-literature practitioner branding through Wilmot/CS)

**Body depth**: ~80–120 lines，formula explicit，threshold spelled out，variants disclosed

**Suggested section structure**（給 v4.11.0 drafter）:

```markdown
### RAI (Risk Appetite Index) — family of sentiment indicators

**Concept lineage**: Kumar & Persaud (2002, *International Finance* 5: 401–436)
originated the cross-sectional Global Risk Appetite Index (GRAI) — at time t,
the Spearman rank correlation between a cross-section of assets' past volatility
and their excess returns measures whether investors are demanding higher returns
for higher risk (risk-on) or bidding up safe assets (risk-off).

**Practitioner canonical**: Credit Suisse Global Risk Appetite Index
(Wilmot, Mielczarski & Sweeney, CSFB *Market Focus*, February 2004) — a linear-
regression extension applied daily to 64 bond+equity indexes across developed
and emerging markets. Grey-literature primary source; methodology documented
second-hand in Illing & Aaron (2005) and Uhlenbrock/Bundesbank (2009).

**Interpretation**: Contrarian signal at extremes.
- "Panic" territory → forward returns tend positive over 3–12 months
- "Euphoria" territory → forward returns tend negative over 3–12 months
- Neutral zone → low informational content

**Known caveats** (Illing & Aaron 2005): "Measurement of risk appetite is highly
sensitive to the chosen methodology. It seems premature to rely on any given
index when assessing risk appetite." The CS RAI has correlation of effectively
zero (−2%) with the Kumar-Persaud GRAI despite similar theoretical motivation.

**Variants in common use**:
- State Street Investor Confidence Index (Froot & O'Connell, NBER WP 10157,
  2003) — flow-based, 100 = neutral, monthly release
- Citi Panic/Euphoria Model (Levkovich, 1990s–present) — 9-component
  composite, panic <0.17, euphoria >0.38 circa 2011 calibration
- BofA Bull & Bear Indicator (Hartnett) — 0-10 scale, buy <2.0, sell >8.0;
  16 sell signals since 2002, 63% accuracy per BofA
- BIS RAI (Tarashev, Tsatsaronis & Karampatos, *BIS Quarterly Review*, June 2003)
- Bank of England RAI (Gai & Vause, BoE WP 283, 2005)

**Not to be confused with**:
- VIX (volatility, not positioning/sentiment)
- Fundamentally-derived indicators (RAI uses only prices/flows/rankings)
- Any single proprietary "RAI" being canonical — the family is heterogeneous

**JP context**: No public JP-specific RAI. Closest analogue is the Bank of Japan
『金融システムレポート』financial-activity heat map.
```

**Key takeaways for v4.11.0 drafter**:

1. **Revise the Phase 1 hypothesis**. Kumar-Persaud (2002) 是 true academic origin；Wilmot (2004) 是 practitioner canonical。Cite 兩個；CS RAI treated 為「practitioner branding on top of a 2002 peer-reviewed concept」。
2. **Illing & Aaron (2005) is single most useful primary source** — central-bank publication catalog 全部 + documents inconsistencies + 提供 bibliography for every variant。
3. **不要 publish numeric panic/euphoria threshold for CS RAI as definitive** — CS 沒揭露。Practitioner ±3σ z-score band 是 inference。
4. **Correct NBER number**: Froot & O'Connell 是 **10157**，不是 8226。
5. **Correct GS attribution**: Goldman Sachs Risk-*Aversion* Index (GS Economics Research, 2003-10)，不是「GS RAI by Jan Hatzius」。
6. **Correct BofA attribution**: 「BofA Bull & Bear Indicator」by Hartnett，不是「BofA Global Investor Confidence Index」。
7. **JP context**: 沒 Nomura/Daiwa 公開 RAI。用 BoJ Financial System Report heat map 或 honestly acknowledge gap。
8. **Cite academic caveat explicitly**: 「Measurement of risk appetite is highly sensitive to chosen methodology」(Illing & Aaron 2005)。**這是整個 RAI 文獻最重要的一句，必須出現在 investment-macro-regime.md**。

---

# Cluster D — Portfolio Construction: Taleb Barbell Strategy

## Q4. Taleb Barbell — primary source disambiguation & operational definition

### Scope statement

Barbell Strategy 是 Nassim Nicholas Taleb 的 portfolio-construction 啟發法：在 risk spectrum 兩個極端 (ultra-safe + ultra-risky) 都極端 allocate，**中間風險完全為零**，用以 cap downside 同時保持 convex upside exposure to positive Black Swans。它是 **antifragility** 在 portfolio 層面的 operational instantiation。Target file: `investment-portfolio-construction.md` v4.11.0 Tier 2，portfolio-layer allocation philosophy 段落。

### 書誌（已驗證）— Primary source identification

| Source | Year | Role | Chapter / Location | Notes |
|---|---|---|---|---|
| Taleb, *Fooled by Randomness* | 2001 (rev 2005) | **Precursor** | N/A (implicit) | 介紹 asymmetric-payoff + convexity 思維；尚無命名為「barbell」的 strategy。Presage 2008 crisis。 |
| Taleb, *The Black Swan: The Impact of the Highly Improbable* | 2007 (2nd ed 2010) | **First formal mention** | **Chapter 13: "Appelles the Painter, or What Do You Do if You Cannot Predict?"** | 推 85–90% 在 T-bills / safest instruments + 10–15% 在極端 speculative bet (deep OTM options)。Brief prescription 在 epistemology chapter 中。Random House, ISBN 978-1400063512。 |
| Taleb, *Antifragile: Things That Gain from Disorder* | 2012 | **Primary elaborated source** | **Book III, Chapter 11: "Never Marry the Rock Star"** — subsections 含 *Seneca's Barbell* / *The Accountant and the Rock Star* / *Away from the Golden Middle* / *The Domestication of Uncertainty* | **完整 philosophical + practical 發展**：barbell as transformation from fragile to antifragile；應用超出 finance (career / diet / writing)。Random House, ISBN 978-1400067824。 |
| Geman, D., Geman, H., & Taleb, N.N. (2015) "Tail Risk Constraints and Maximum Entropy" | 2015 | **Mathematical formalization** | *Entropy* **17(6), 3724–3737**. **DOI: 10.3390/e17063724**. arXiv:1412.7647 | 證明在 VaR + CVaR constraints 加 maximum-entropy criterion 下，barbell-shaped portfolio emerges 為 general setting 的 optimal solution。Argues standard-deviation-based risk measure 不令人滿意因為 truncate upside along with downside。 |
| Spitznagel, M. *The Dao of Capital: Austrian Investing in a Distorted World* | 2013 | **Practitioner companion** | Wiley. Paul Tudor Jones foreword | Austrian-economics framing of similar 「roundabout」strategy；Spitznagel **明確說 Universa 的實作不是 pure Taleb barbell** 因為 OTM convex payoff 太貴 — 他用 targeted tail hedge overlay。 |
| Spitznagel, M. & Taleb (foreword). *Safe Haven: Investing for Financial Storms* | 2021 | **Empirical companion** | Wiley, ISBN 978-1119401797 | 量化 tail hedging cost-benefit；argues「risk mitigation that adds to geometric returns」是 real goal，不是 pure diversification |

**Verification of primary source claim (2012 vs 2007)**: *The Black Swan* Ch 13 是 Taleb 第一次 name barbell + 給 85/15 prescription，但是 epistemology chapter 中 brief tactical footnote。*Antifragile* Ch 11 是 concept **fully developed as a standalone strategy** 帶哲學基礎 (Seneca) + nonlinear payoff theory + cross-domain application 的地方。**對 investment-portfolio-construction.md，cite Antifragile Ch 11 為 primary，Black Swan Ch 13 為 first mention**。2015 Entropy paper 是 mathematical primary source if formal justification 需要。

### Exact Barbell definition

**Taleb 自己的話 (Antifragile Ch 11)**:
> "The barbell (a bar with weights on both ends that weight lifters use) is meant to illustrate the idea of a combination of extremes kept separated, with avoidance of the middle."
>
> "Antifragility is the combination aggressiveness plus paranoia — clip your downside, protect yourself from extreme harm, and let the upside, the positive Black Swans, take care of itself."
>
> The barbell "is not necessarily symmetric: it is just composed of two extremes, with nothing in the center."

**Numerical prescription (Black Swan Ch 13)**:
- **85–90%** in maximally safe instruments: T-bills, short-term Treasuries, inflation-protected cash, gold, "boring" assets with near-zero ruin probability
- **10–15%** spread across many small, highly speculative bets with **convex (unbounded upside, capped downside) payoffs** — prototypically deep OTM put options (crash protection) or deep OTM call options / venture bets (upside)
- **0%** in middle-risk tier: investment-grade corporates, moderately leveraged equity funds, typical balanced mutual funds, anything "medium volatility"

**Philosophy vs fixed ratio**: Taleb treats 85/15–90/10 numbers as **illustrative, not prescriptive**。Philosophy 是 (a) convexity of the risky bucket（more convex → smaller allocation suffices），(b) investor total asset base，(c) time horizon。**不可協商的是 topology**：extremes + zero middle。

**What counts as "safe" (Taleb criteria)**:
1. **No tail risk of total loss** — 排除 leverage / credit risk / counterparty risk beyond sovereign
2. **Transparent pricing** — no mark-to-model / no structured products
3. **Liquid on demand** — not gated
4. **Boring, low-return acceptable** — Taleb 明確接受 negative real return on safe bucket as insurance premium

**What counts as "risky" (Taleb criteria)**:
1. **Convex payoff**: capped downside (only lose premium), uncapped upside
2. **Fat-tailed distribution**: fat right tail preferred；fat-left-tail-exposure 明確禁止
3. **Asymmetric epistemic bet**: exposed to being right about something you cannot forecast exactly
4. Prototypical instruments: **deep OTM options** (canonical Taleb example), early-stage venture, literature/creative optionality bets, cryptocurrency (per later commentary)

**Why zero middle — Taleb argument**:
1. **Epistemic arrogance**: medium-risk assets (corporate bonds / balanced funds) 要求 you correctly estimate their risk — exactly where fat-tailed distributions 破壞 mean-variance estimation
2. **Hidden tail risk**: 「moderately risky」instruments appear safe based on historical volatility 但 fragile to Black Swans (2008 MBS exemplar)
3. **Robustness to estimation error**: Barbell is **robust** because mixture of extremes 給 payoff that is mathematically **insensitive to errors in estimating the middle**。Geman-Geman-Taleb 2015 在 VaR+CVaR constraint 下 formalize 這點。
4. **Convexity asymmetry**: middle-risk assets 有 near-linear payoff；不給 convexity (gain-from-volatility)，這正是 antifragility 的全部意義。

### Relationship to antifragility

**Taleb Triad** (from *Antifragile*):
- **Fragile** — harmed by volatility (concave payoff)
- **Robust** — neutral to volatility (linear payoff)
- **Antifragile** — gains from volatility (convex payoff)

Barbell 是 **portfolio-level transformation device**，把 system 從 fragile → antifragile。Safe bucket 確保 survival (左尾從 catastrophic 變 bounded)；convex risky bucket 確保 participation in positive Black Swans (右尾變 disproportionate gain)。Bounded left tail + unbounded right tail = antifragile。

**Convexity in portfolio terms**: Portfolio 有 positive convexity 當 payoff function f(x) (where x = state variable, e.g. market volatility) 滿足 f''(x) > 0。By Jensen's inequality, E[f(X)] ≥ f(E[X]) 當 f convex — 即 **uncertainty itself is value-creating** for convex payoffs。Deep OTM options 是最純的表達：payoff 在 threshold 之前為 0，之後 nonlinearly accelerate。

**Optionality framing**: Taleb 把整個 barbell 描述為「a portfolio of options」。Safe bucket 是 *the premium you can afford to pay* (因為它不衰減)。Risky bucket 是 *a bundle of optionality contracts*。Taleb prefers **open-ended over closed-ended optionality** — bets where upside is unbounded (venture / early-stage tech / deep OTM calls on unknown catalysts) 大於 bets where upside is capped (short-dated options on known catalysts)。

### Real-world applications

**1. Personal portfolio (Taleb stated approach)**:
Taleb 宣稱他自己的錢就是 barbell-style：majority 在 Treasuries + cash equivalents，minority 在 deep OTM options + venture-like bets。從 ~2001 到現在 interview 都 consistent。

**2. Empirica Capital (1999–2004)**:
- Taleb + Mark Spitznagel co-founded
- Tail-hedging strategy buying OTM put options
- **2004 收盤 due to subpar returns** — 重要 caveat：在 low-volatility 2003–2004 期，constantly paying option premia 產生 drag with no offsetting payoff。**這是 pure barbell 的「bleed」problem**。

**3. Universa Investments (2007–present)**:
- Spitznagel founded；Taleb 是 Distinguished Scientific Advisor
- **Spitznagel 明確說 Universa 不適用 pure Taleb barbell** 因為 OTM convex payoff 「too expensive」獨立 portfolio 用。改用 **tail-hedge overlay** 給 client bolt onto risk-asset core。
- 典型 prescription: client 持 **96.7% S&P 500 + 3.3% Universa tail hedge** (NOT 85/15)。小 allocation 已足夠因為 hedge 在 crash scenario 高 convexity。
- **Critical attribution correction**: 「Universa = Barbell」是 wrong。Universa 是 tail-hedge product，enable client 持 *more* risky exposure safely — closer to「turbocharged 60/40」than Taleb's 85/15。

**4. Performance data**:

| Period | Universa / related | S&P 500 | Notes |
|---|---|---|---|
| 2007–2008 | > 100% returns | −37% (2008) | Empirica-style tail hedge 在 crisis delivered |
| 2008-01-01 to 2019-12-31 | ~105% annualized on invested capital (BSPP life-to-date) | ~9% annualized | Per source close to firm；「invested capital」denominator |
| 2020-03 | +3,612% month / +4,144% YTD | −12.4% (2020-03) | Black Swan Protection Protocol；廣為 Bloomberg/Yahoo report |
| 2008–2018-02 | 96.7% SPX + 3.3% Universa = **12.3% CAGR** | **7.9% CAGR** | Universa 2020 letter |
| 2015 (August flash crash) | ~$1B profit in single week | — | |

**Critical caveat**: 這些 returns 是 *invested capital at risk* in hedge sleeve，不是 total portfolio AUM。3,612% monthly return on a 3.3% sleeve = ~119% on total portfolio in that month。仍 extraordinary，但「4,144%」number 是 headline-inflated，必須 explain denominator。

### Critical Attribution Corrections (Taleb Barbell cluster — 7 items)

1. **Barbell 是 extreme-extreme，NOT middle-of-the-road**。**單一最大誤讀**。「Barbell」在 finance colloquial 有時被用作「a little of stocks and a little of bonds」(diversification) — 這正是 Taleb meaning 的相反。Taleb's barbell **完全 eliminates the middle**。

2. **Barbell 不規定 fixed percentage**。85/15 與 90/10 是 Taleb 在 Black Swan Ch 13 與 interviews 給的 illustrative example，**不是 formula**。Philosophy 是 topology (extremes + zero middle)，不是 split ratio。

3. **Primary source 是 Antifragile (2012) Ch 11，不是 The Black Swan (2007) Ch 13**。Black Swan 是 mention；Antifragile 是 develop。如果只 cite 一個，cite Antifragile。Geman-Geman-Taleb (2015) Entropy 是 mathematical primary source。

4. **Spitznagel Universa 不是 Taleb's Barbell**。哲學 lineage 相似但 operationally 不同：Universa 是 **tail-hedge overlay** 給 client 持 **more** risk asset (96.7% SPX + 3.3% hedge)，**不是** 保守的 85/15 split。Spitznagel 自己在 *The Dao of Capital* + *Safe Haven* 中說。

5. **Barbell 有「bleed」problem**。Empirica Capital 2004 closure 正是因為 low-volatility 環境下 constantly paying option premia 產生 drag。Taleb 承認但 argue insurance premium worth it。2020 + 2008 payoff justify the bleed；2003–2019 bull market 不 justify (除非看 risk-adjusted metric)。

6. **Barbell 不是 mean-variance optimum**。在 Markowitz mean-variance 下，barbell 被 efficient frontier dominate。它 optimal 只在 fat-tailed distribution + VaR/CVaR constraint (Geman-Geman-Taleb 2015) 或 pure ruin-avoidance criterion 下。Standards file 必須 flag — barbell wins 只要你接受 Taleb premise 「historical variance badly underestimates tail risk」。

7. **「Antifragile」≠「Barbell」**。Antifragility 是更廣 concept；barbell 是 one specific instantiation。其他 antifragile strategy 存在 (trial-and-error, optionality harvesting, negative via)。Standards file 應 frame barbell 為 **one portfolio-level instantiation of antifragility**，不是 definition。

### Comparison to other allocation frameworks

| Framework | Core logic | Risk model | Middle exposure | Tail behavior | Bleed cost |
|---|---|---|---|---|---|
| **Taleb Barbell** (2007/2012) | 85–90% safe + 10–15% convex tails；zero middle | Fat tails, unknowable | **Zero** | Capped left, uncapped right | **High** (option decay)；只在 Black Swan 會 pay off |
| **60/40 Traditional** | 60% equities + 40% bonds；diversify via negative correlation | Gaussian / historical vol | Dominant | 暴露在兩尾；2022 顯示 bonds+stocks 可一起跌 | Low but tail-exposed |
| **Risk Parity / All-Weather** (Bridgewater, Dalio) | Equal *risk contribution* across asset classes；leverage up low-vol assets to match | Volatility-targeted, historical cov | High (levered bonds, commodities) | Concave in leverage / correlation shock (2020-03, 2022) | Moderate；leverage cost |
| **Kelly Criterion** | Maximize expected log-growth；sizing via edge/variance | Assumes known edge + known variance | Variable (formula result) | Can blow up if edge over-estimated；「half-Kelly」common | Zero theoretical |
| **Universa Tail Hedge Overlay** (Spitznagel) | ~97% risk asset + ~3% tail hedge | Fat tails, cost-benefit anchored to geometric return | High (~97%) | Capped left via hedge；uncapped right via equity beta | Moderate；hedge 是 the bleed |

**Barbell vs 60/40**: Taleb 視 60/40 為「middle everywhere」 — medium-risk equities + medium-risk bonds。**2022 (equities −19%, long bonds −31%) 是 Taleb 的 vindication case**：所謂 negative correlation 在最需要時崩潰。Barbell 的 T-bills + OTM puts 會 produce large positive return。

**Barbell vs Risk Parity**: **Taleb–Asness / AQR feud** 是 primary-source artifact。Taleb 公開批評 AQR papers (argue risk parity outperforms tail hedging)，稱「BS in the risk-premia space」。Asness response defending risk parity Sharpe 並 note tail-hedge cost drag。**兩邊都部分對**: AQR critique 適用 if horizon 夠長 amortize option bleed + utility 是 quadratic；Taleb critique 適用 if ruin path-dependent + fat tails materially worse than Gaussian。Standards file 應 present 兩邊。

**Barbell vs Kelly**: Kelly 與 Barbell **正交**。Kelly 是 *sizing* rule (how much to bet given known edge)；Barbell 是 *allocation topology* (what structure of bets)。Kelly 假設你 know distribution parameters — Taleb reject 的假設。Kelly bettor with Taleb fat-tail skepticism 最終 end up at half-Kelly 或 quarter-Kelly，operationally barbell-like。

**Why Taleb 認為 Barbell 在 fat-tailed risk 下 superior**:
- **Robust to model error** — 不需要 correctly estimate middle-risk asset
- **Path-dependent ruin avoidance** — 85–90% in safes 保證 survival regardless of middle-tier performance
- **Jensen's inequality captures** — convex bucket benefits from volatility
- **Operationally simple** — no factor model, no covariance estimation

### Empirical validation

**2008 GFC**: Empirica-style + early Universa tail hedging delivered the canonical win。Universa report > 100% returns 2007–2008。

**2020-03 COVID crash**: Universa BSPP +3,612% month / +4,144% YTD (Bloomberg, Yahoo Finance)。Caveat as noted: 這些 returns 是 invested capital in hedge sleeve，not total portfolio AUM。

**2022 stock+bond double decline**: 沒有 widely-published Universa number，但這 conceptually 是 60/40 失敗 + barbell-style (cash + small convex upside bets) 應 outperform 的 scenario。60/40 total return 2022 ≈ −16% (SPX −19%, US Agg −13%)。Pure Taleb 90/10 barbell in T-bills 應賺 ~3% (T-bill yield) − option-sleeve decay ≈ flat to slightly positive。

**Long-term compounded performance (2008–2018, Universa-reported)**: 96.7% SPX + 3.3% Universa = **12.3% CAGR** vs S&P 500 **7.9% CAGR**。**最強的「barbell-style wins」case in public record**，但來自 Universa own disclosure。

**Peer-reviewed validation**: Geman–Geman–Taleb (2015) *Entropy* paper 是最接近 academic proof — 在 VaR + CVaR constraint with maximum-entropy prior (即 distributional parameters uncertain) 下，optimal portfolio converge to barbell topology。**這是 optimality-under-uncertainty result，不是 empirical backtest**。

**Counter-evidence**: AQR papers (Asness, Israelov, Moskowitz et al.) argue tail hedging underperformed risk parity net of cost over post-crisis cycle。Empirica Capital 2004 closure 也 support「bleed dominates in low-vol regime」critique。

### JP integration assessment

**Finding: Barbell 在日本投資思維 minimal traction**。

日語 search 結果 (Nomura / Daiwa / SMBC Nikko / Mitsui-Sumitomo DS Asset Management glossaries) 用「**バーベル戦略** (bābēru senryaku)」主要意指 **bond-ladder sense** — short-duration + long-duration bonds with no intermediate maturities barbell。**這是傳統 fixed-income 用法，先於 Taleb 存在，與他的 antifragility framing 無關**。Cite Taleb 的日本零售 blog (note.com / TeamHackers / Motley Fool Japan) 是西方 conversation 的翻譯，不是獨立 JP scholarship。

**沒有 identifiable 的日語 primary source / academic paper / institutional framework extend or critique Taleb's Barbell**。日本 institutional investing (GPIF, life insurers) 由 ALM-based strategic asset allocation 主導，沒大規模 adopt tail-hedge overlay。最接近的 JP intellectual parallel 是 Dalio All-Weather (因為它 frame regime-based allocation) — 但那是 Risk Parity，barbell 的對立框架。

**Note the absence honestly in standards file**。**不要 invent JP parallel**。Flag JP usage of「バーベル戦略」= 固定收益 duration barbell，**不是** Taleb antifragile barbell — 這是 **terminology trap**。

### 對 `investment-portfolio-construction.md` 的應用

**Tier**: **Tier 2** — Barbell 與 Risk Parity 並列為兩個 primary portfolio-layer framework。

**Body depth**: ~60–80 lines

**Section 結構** (覆蓋):
- (a) 哲學 (extreme-extreme + zero middle)
- (b) Antifragile Ch 11 primary citation + Black Swan Ch 13 first mention + Geman-Geman-Taleb 2015 mathematical anchor
- (c) Convexity / optionality 解釋
- (d) **anti-drift corrections** (not middle / not fixed % / not Universa-equivalent)
- (e) Practitioner variants (Taleb personal vs Spitznagel tail-overlay)
- (f) Comparison row in framework table
- (g) Empirical evidence including bleed problem

**Anti-drift callouts standards file MUST include** (6 條 + JP terminology trap):

1. Barbell ≠「a little of everything」。It eliminates the middle。
2. 85/15 與 90/10 是 illustrative，not prescriptive。
3. Primary source 是 Antifragile (2012) Ch 11；Black Swan (2007) Ch 13 是 first mention。
4. Universa 的 operational model **不是** Taleb 的 85/15 barbell — 是 tail-hedge overlay enable 更高 risk-asset holding。
5. Barbell 在 low-volatility regime 有 bleed cost (Empirica 2004 closure 為 primary evidence)。
6. JP 「バーベル戦略」= bond duration barbell，**不是** Taleb antifragile barbell。Terminology trap。

**Canonical citations to lock in**:
- Taleb, N.N. (2012). *Antifragile: Things That Gain from Disorder*. Random House. ISBN 978-1400067824. Chapter 11: "Never Marry the Rock Star".
- Taleb, N.N. (2007/2010). *The Black Swan: The Impact of the Highly Improbable*. Random House. ISBN 978-1400063512. Chapter 13.
- Geman, D., Geman, H., & Taleb, N.N. (2015). "Tail Risk Constraints and Maximum Entropy." *Entropy* 17(6), 3724–3737. DOI: 10.3390/e17063724. arXiv: 1412.7647.
- Spitznagel, M. (2013). *The Dao of Capital: Austrian Investing in a Distorted World*. Wiley.
- Spitznagel, M. (2021). *Safe Haven: Investing for Financial Storms*. Wiley. ISBN 978-1119401797.

**Pair-with-Risk-Parity framing**: Standards file 應 present Barbell 與 Risk Parity 為 portfolio-layer thinking 的兩極 — Barbell =「fat tails 不可知，買 convex insurance + 求 survival」; Risk Parity =「risks 可估，equalize contribution for balanced outcome」。沒有 universally correct，選擇 depends on investor prior about distributional knowability。

### Research completeness notes

- 主要書籍 chapter reference 透過 book-notes 二次來源 (grahammann.net, studylib, supersummary) **verified**。Direct PDF of *Antifragile* 已 indexed 但未 fetched (避免 license issue)；chapter title + subsection 在 3 個 independent summary 中 cross-check。
- *Entropy* 2015 paper citation **完全 verified** (DOI / volume / pages / arXiv ID 在 MDPI、ADS、Semantic Scholar 一致)。
- Empirica Capital 2004 closure **verified** via Wikipedia + finews + Institutional Investor secondary sources。
- Universa 2020-03 numbers **verified** via Bloomberg + Yahoo Finance；flagged denominator caveat。
- AQR–Taleb feud **confirmed** as real primary-source artifact (Asness response to Taleb tweets documented in BSIC + Advisor Perspectives coverage)。
- JP source check **complete**: Nomura + Daiwa + SMBC-DS glossaries 確認 JP usage 是 bond-duration barbell，not Taleb concept。
- **Not fetched directly** (access/format)：Taleb Twitter/X threads / Taleb own copies of *Antifragile*/*Black Swan* PDFs / Bloomberg paywalled articles。Chapter reference 依賴 summary-site triangulation。如最高 fidelity chapter verification 需要，physical copy of *Antifragile* 應該 cross-check Chapter 11 subsection title before v4.11.0 final publication。

---

# Cluster E — L2 Sector / Factor: Fama-French Factor Investing

## Q5. Fama-French canon — disambiguation across 1992 / 1993 / 1997 / 2014 / 2015 / 2019

### Scope statement

This cluster 為 Fama-French factor-investing canon 提供 primary-source grounding，涵蓋 operational 3-factor model (1993)、5-factor extension (2015)、related practitioner factors (Momentum / Low-Vol / BAB / Quality / QMJ)、Japanese factor-model evidence、L2-to-L1 regime-to-factor bridge。它是 `standards/investment-sector-industry.md` 「cross-sectional equity style」layer 的 core anchor (Tier 2)。

**Factor investing 為什麼放在 L2**: factor 是 **cross-sectional attribute used to group asset** — 在 L3 industry-classification (GICS / sector) 與 L1 regime-rotation (Investment Clock / debt cycle) 之間，是 practitioner 把 L1 regime view 轉成 equity portfolio 的 primary mechanism。

**Hallucination hazard moderate**。Paper 都 well-indexed + Nobel-adjacent，但：
- LLM 把 3-factor (1993) 與 5-factor (2015) 混淆，cite「Fama-French」沒指明哪個
- Momentum 經常被誤歸 Fama-French；屬於 Carhart 1997 (built on Jegadeesh-Titman 1993)
- Quality factor 經常被誤歸 Fama-French RMW；practitioner canon 是 AQR Asness-Frazzini-Pedersen 2019 QMJ
- Low-volatility anomaly 經常被歸給「Fama-French」或「behavioral finance generally」；canonical 是 Frazzini-Pedersen 2014 BAB
- Fama-French 經常 conflate with Ross APT (1976)；兩者是 distinct mathematical foundation
- 日本 factor evidence 經常被忽略；**Kubota & Takehara (2018) 證明 FF5 在日本不 work**，**Asness (2011) 證明日本 momentum 在孤立看來像壞的**。兩者對 JP-facing portfolio claim 都是 load-bearing。

### 書誌（已驗證）— FF3 (1992, 1993)

- **Fama, E.F. & French, K.R. (1992)** "The Cross-Section of Expected Stock Returns." *Journal of Finance* **47(2): 427–465**. DOI: 10.1111/j.1540-6261.1992.tb04398.x. Wiley: https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1992.tb04398.x。**第一篇 empirical paper** 顯示 size 與 book-to-market 捕捉 cross-section of expected stock return，且 **當允許 β variation unrelated to size，market-β slope is flat** — 直接挑戰 CAPM。**這是殺死 single-factor CAPM as empirical claim 的 paper**。**尚未** present operational 3-factor model with SMB and HML 為 tradable factor portfolio。
- **Fama, E.F. & French, K.R. (1993)** "Common Risk Factors in the Returns on Stocks and Bonds." *Journal of Financial Economics* **33(1): 3–56**. RePEc: https://ideas.repec.org/a/eee/jfinec/v33y1993i1p3-56.html. PDF: https://www.bauer.uh.edu/rsusmel/phd/Fama-French_JFE93.pdf。**The operational 3-factor model**，introduces **SMB (Small Minus Big)** + **HML (High Minus Low)** as mimicking portfolios traded against **Mkt-Rf** market excess return。Paper 也 identify 兩個 bond factor (term + default)。**Practitioner 說「Fama-French three-factor model」時，正確 cite 是這篇 1993 JFE，不是 1992 JoF**。

### 書誌（已驗證）— FF5 (2015) + 國際因子 (2012)

- **Fama, E.F. & French, K.R. (2015)** "A Five-Factor Asset Pricing Model." *Journal of Financial Economics* **116(1): 1–22**. DOI: 10.1016/j.jfineco.2014.10.010. ScienceDirect: https://www.sciencedirect.com/science/article/abs/pii/S0304405X14002323. PDF: https://tevgeniou.github.io/EquityRiskFactors/bibliography/FiveFactor.pdf。**Adds RMW (Robust Minus Weak)** for operating profitability + **CMA (Conservative Minus Aggressive)** for asset-growth / investment，based on dividend-discount model decomposition linking expected return 到 profitability + investment at constant B/M。Fama and French note: **once RMW + CMA included, HML becomes redundant** (其 mean return 被 absorbed)，但 retain HML for consistency。**Notably, momentum is NOT added**；2015 paper 明確把 momentum 排除在 model 外。
- **Fama, E.F. & French, K.R. (2012)** "Size, Value, and Momentum in International Stock Returns." *Journal of Financial Economics* **105(3): 457–472**. RePEc: https://ideas.repec.org/a/eee/jfinec/v105y2012i3p457-472.html. PDF: https://www.johnhcochrane.com/s/Fama_French_size_value_momentum_JFE.pdf。Test 3-factor framework + momentum across 4 regions (North America / Europe / Japan / Asia Pacific)。**Key finding for JP portfolios: value premia exist in all four regions, but "except for Japan, there is return momentum everywhere"** — 日本是 momentum anomaly 的明確例外。Also: 「Integrated pricing across regions does not get strong support」；**local factor model outperforms global ones for NA / Europe / Japan**。

### 書誌（已驗證）— Related factors (NOT FF proper)

- **Jegadeesh, N. & Titman, S. (1993)** "Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency." *Journal of Finance* **48(1): 65–91**. DOI: 10.1111/j.1540-6261.1993.tb04702.x. PDF: https://www.bauer.uh.edu/rsusmel/phd/jegadeesh-titman93.pdf。**Momentum anomaly 的 original empirical discovery**：strategy buying prior 3–12 month winners + shorting prior 3–12 month losers 在 3–12 month holding 產生 significant positive returns，not explained by systematic risk。**Carhart 1997 把這 packaged 為 factor portfolio**。
- **Carhart, M.M. (1997)** "On Persistence in Mutual Fund Performance." *Journal of Finance* **52(1): 57–82**. DOI: 10.1111/j.1540-6261.1997.tb03808.x. PDF: https://finance.martinsewell.com/fund-performance/Carhart1997.pdf。**Momentum factor canonical citation as addition to FF framework**。「Carhart 4-factor model」= FF3 + WML/UMD (Winners Minus Losers = Up Minus Down)，momentum leg built from Jegadeesh-Titman anomaly。Paper core claim: fund「hot hands」persistence 是被 momentum factor driven，不是 manager skill。
- **Frazzini, A. & Pedersen, L.H. (2014)** "Betting Against Beta." *Journal of Financial Economics* **111(1): 1–25**. DOI: 10.1016/j.jfineco.2013.10.005. NBER WP 16601: https://www.nber.org/system/files/working_papers/w16601/w16601.pdf。**Low-volatility / low-beta anomaly as tradable factor 的 canonical primary source**。**BAB (Betting Against Beta) factor** = long leveraged low-β assets, short deleveraged high-β assets；US stocks 1926–2012 Sharpe ~0.78（roughly 2× value premium Sharpe + ~40% above momentum）。Theoretical mechanism: funding/leverage constraint。Cite 「low volatility anomaly」for factor-ETF discussion 時 cite Frazzini-Pedersen 2014 為 primary。
- **Asness, C.S., Frazzini, A. & Pedersen, L.H. (2019)** "Quality Minus Junk." *Review of Accounting Studies* **24(1): 34–112**. DOI: 10.1007/s11142-018-9470-2. Springer: https://link.springer.com/article/10.1007/s11142-018-9470-2。**Quality factor as implemented by AQR + adopted by practitioner factor ETFs 的 canonical primary source**。Quality 定義為 profitability + growth + safety 的複合；QMJ factor 在 US + 24 個國際市場賺 significant risk-adjusted return。**QMJ ≠ FF RMW**。兩者 capture profitability，但 QMJ 加 growth + safety leg (earnings stability / low leverage / low volatility) + 用 rank-composite construction。Practitioner Quality factor 引用 (iShares QUAL, MSCI USA Quality) 對齊 QMJ，不是 RMW。

### 書誌（已驗證）— Nobel & overview

- **Fama, E.F. (2013)** "Two Pillars of Asset Pricing." Prize Lecture, Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel, 2013-12-08, Aula Magna, Stockholm University. Nobel: https://www.nobelprize.org/prizes/economic-sciences/2013/fama/lecture/. PDF: https://www.nobelprize.org/uploads/2018/06/fama-lecture.pdf。Nobel 是 **jointly** awarded to **Fama, Lars Peter Hansen, and Robert J. Shiller**「for their empirical analysis of asset prices」。Fama 把 life work frame 為 two pillars: (1) efficient capital markets; (2) developing and testing asset pricing models。**單一 best author-authored summary of factor-model development arc** — 適合 grand-arc narrative cite，不是 operational-formula citation。
- **Fama, E.F. & French, K.R. (2021)** "The Value Premium." *Review of Asset Pricing Studies* **11(1): 105–121**. SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3525096。Current author-authored review of value premium，address「is value dead?」debate after 2010s HML underperformance。**Note journal 是 RAPS，不是 JFE** — common misattribution。
- **Cochrane, J.H. (2011)** "Presidential Address: Discount Rates." *Journal of Finance* **66(4): 1047–1108**. DOI: 10.1111/j.1540-6261.2011.01671.x. NBER WP 16972。**Most-cited meta-review of factor proliferation**，著名 coined「**zoo of new factors**」描述 post-FF characteristic-based factor explosion。Use 為 canonical citation for「有數百個 published factors，多數 spurious」+ parsimony argument in favor of FF3/FF5。
- **Ross, S.A. (1976)** "The Arbitrage Theory of Capital Asset Pricing." *Journal of Economic Theory* **13(3): 341–360**. DOI: 10.1016/0022-0531(76)90046-6。**Included only for APT-vs-FF disambiguation** — see Critical Attribution Corrections below。

### Factor 定義（exact formulas — Kenneth French data library construction）

**Source**: Kenneth French Data Library, "Description of Fama/French 5 Factors (2x3)", http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5developed.html — **definitive operational reference**。Ken French 維護 + 發佈每月 factor return，每個 academic test + 多數 practitioner factor-tilt portfolio 都用。

**Market factor — Mkt-Rf** (CAPM origin)
- Value-weight return on market portfolio − 1-month T-bill risk-free rate
- 是 CAPM single factor；FF3 / FF5 preserve 為第一個 factor。**不是 long-short portfolio，是 direct market excess return**。

**Size factor — SMB (Small Minus Big)**
- Average return on small-cap portfolio − average return on large-cap portfolio
- FF3 (1993): 透過 **2×3 sort** 構造 — 用 market-cap median (Small/Big) × B/M tercile 30/70 NYSE breakpoint (Growth/Neutral/Value)，產生 6 portfolio；SMB = average of 3 small portfolios − average of 3 big portfolios
- FF5 (2015): SMB averaged across **三個 2×3 sort** — 一個 on B/M、一個 on OP (operating profitability)、一個 on INV (investment / asset growth) — to remove loading on HML, RMW, CMA。Specifically: SMB = ⅓·SMB(B/M) + ⅓·SMB(OP) + ⅓·SMB(INV)
- Breakpoint: big = top 90% of June market cap, small = bottom 10% (Developed dataset)；US Research Factors 用 NYSE median 為 size breakpoint
- Interpretation: long small-caps, short large-caps, approximately dollar-neutral within size quintile

**Value factor — HML (High Minus Low)**
- Average return on high B/M (value) portfolios − average return on low B/M (growth) portfolios
- 2×3 construction: HML = ½·(Small Value + Big Value) − ½·(Small Growth + Big Growth)，Value = top 30% B/M + Growth = bottom 30% B/M within each size group, NYSE breakpoint for big stocks
- Book equity 用 prior-year-end accounting data lagged 6 months（match July-of-year-t return via December-of-year-(t-1) book equity）

**Profitability factor — RMW (Robust Minus Weak) [FF5 only]**
- Average return on high operating-profitability portfolios − average return on low operating-profitability portfolios
- 2×3 construction: RMW = ½·(Small Robust + Big Robust) − ½·(Small Weak + Big Weak)
- "Operating profitability" = (revenues − COGS − SG&A − interest expense) ÷ book equity，從最近 fiscal year ending before July of year t computed
- Robust = top 30% OP；Weak = bottom 30% OP；breakpoint from big-stock sample
- Economic interpretation: capture gross-profitability anomaly (Novy-Marx 2013)

**Investment factor — CMA (Conservative Minus Aggressive) [FF5 only]**
- Average return on low-asset-growth (conservative) portfolios − average return on high-asset-growth (aggressive) portfolios
- 2×3 construction: CMA = ½·(Small Conservative + Big Conservative) − ½·(Small Aggressive + Big Aggressive)
- "Investment" = asset growth = (total_assetsₜ − total_assets_{t-1}) / total_assets_{t-1}
- Conservative = bottom 30% asset growth; Aggressive = top 30%
- Economic interpretation: 「asset growth anomaly」(Cooper, Gulen, Schill 2008)

**Momentum factor — WML / UMD (Winners Minus Losers / Up Minus Down) [Carhart, NOT FF]**
- Average return on high prior-12-month-return portfolios − average return on low prior-12-month-return portfolios
- Ranking window: months t−12 through t−2 (**skipping month t−1** to avoid short-term reversal)
- French library 用 2×3 sort on size × prior-12-2 return；Winners = top 30% prior return, Losers = bottom 30%
- 注意: 這個 factor 在 Kenneth French data library 上 hosted，雖然不是 FF3/FF5 一部份，是因為 Carhart 用了 French factor construction convention

**Low-volatility / Betting-Against-Beta factor — BAB [Frazzini-Pedersen, NOT FF]**
- BAB = long leveraged low-β portfolio + short deleveraged high-β portfolio，constructed so long + short legs each have β = 1 at formation
- Rank stocks by estimated β；long bottom half (low-β) leveraged up；short top half (high-β) deleveraged down
- 與 MSCI USA Min Vol 不同：MSCI 用 optimization (minimize total portfolio variance subject to diversification constraint)，不是 β-sort

**Quality factor — QMJ [Asness-Frazzini-Pedersen, NOT FF]**
- QMJ = long top-quality tercile, short bottom-quality tercile，Quality 是三個 sub-score 的 rank-composite:
  - **Profitability**: gross profits / assets, ROE, ROA, cash-flow-to-assets, gross margin, accruals
  - **Growth**: prior 5-year growth in profitability measures
  - **Safety**: low β, low leverage, low earnings volatility, low bankruptcy risk (Altman Z, Ohlson O)
- Weighted composite ranked within market；long-short constructed size-neutral

### Factor-regime mapping (L2 to L1 bridge) — 載心內容

**這是讓 L2 factor investing 在 L1-regime-aware framework 裡有用的 key content**。Academic / practitioner consensus 把 factor 對應 cycle phase 如下。

**Primary citations**:

- **Polk, C., Haghbin, M., de Longis, A. (2020)** "Time-Series Variation in Factor Premia: The Influence of the Business Cycle." *Journal of Investment Management* **18(1)**. SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3377677. Invesco PDF: https://www.invesco.com/content/dam/invesco/emea/en/pdf/joim_time_series_variation_in_factor_premia.pdf。**Factor-cycle dynamics 的 canonical academic reference**：value / momentum / size / quality / low-volatility factors 對 macro regime state 有 different sensitivity；regime-based dynamic rotation 跑贏 static equal-weight factor blending net of transaction cost。

- **MSCI (Bender et al.)** "Foundations of Factor Investing" + "Adaptive Multi-Factor Allocation" research notes. https://www.msci.com/documents/1296102/1336482/Foundations_of_Factor_Investing.pdf, https://www.msci.com/documents/10199/239004/Research_Insight_Adaptive_Multi-Factor_Allocation.pdf。**Canonical practitioner reference**：MSCI classify factors 為 **pro-cyclical** (value / size / momentum) 與 **defensive** (quality / low-volatility / high-dividend-yield) — 「risk-on」state 旋轉 pro-cyclical factor，「risk-off」state 旋轉 defensive factor。

#### Factor-by-factor regime mapping

(synthesis of Polk-Haghbin-de Longis 2020 + MSCI Bender et al. + OSAM 2016 "Economic Cycle: A Factor Investor's Perspective")

| Factor | Pro/Defensive | Best phase | Worst phase | Mechanism |
|---|---|---|---|---|
| **Value (HML)** | Pro-cyclical | **Recovery → Reflation** (early cycle, rising growth, depressed price) | Stagflation, late-cycle overheat | Cheap stocks re-rate when growth restarts；value 是 economic normalization 的賭注 |
| **Size (SMB)** | Pro-cyclical | **Recovery** (early cycle) | Contraction, slowdown | Small-caps 對 domestic credit condition 更敏感；recovery 中 lever up |
| **Momentum (UMD)** | Pro-cyclical (different) | **Expansion / steady regime** (trends persist) | **Regime inflection point** (sharp reversal — 2009, 2020 crash the factor) | Momentum 是 trend-following；當 macro regime 變化快於 look-back window 時 fail |
| **Quality (QMJ)** | Defensive | **Contraction / late-cycle slowdown** (flight to safety) | Early cycle / reflation (junk rally dominate) | High-profitability + low-leverage firms 撐過 credit crunch；underperform 在「trash rally」 |
| **Low-Vol (BAB/USMV)** | Defensive | **Stagflation, contraction** (downside protection) | Strong reflation / recovery (beta rallies) | Funding-constraint premium + lower downside capture；bull regime drag |
| **Profitability (RMW)** | Mildly defensive | **Late cycle / contraction** | Early reflation | Mechanism 與 QMJ 相似但 narrower in construction |
| **Investment (CMA)** | Mildly defensive | **Late cycle / slowdown** | Early recovery | Conservative-investment firms 在 capex animal-spirits cycle dominate 時 underperform |

#### Mapping 到 Investment Clock 4 phases (Greetham & Hartnett 2004 vocabulary)

Cross-referencing with L1 Investment Clock phases from `standards/investment-analysis-canon.md`:

- **Reflation** (falling growth, falling inflation → Bonds leadership): defensive factors (Quality / Low-Vol) outperform；Value 弱因為 recovery 還沒開始
- **Recovery** (rising growth, falling inflation → Stocks leadership): **Value + Size outperform** (pro-cyclical factor lead)；Quality lag
- **Overheat** (rising growth, rising inflation → Commodities leadership): **Momentum continues**；Value plateau；Quality + Low-Vol 開始 rebuild
- **Stagflation** (falling growth, rising inflation → Cash leadership): **Quality + Low-Vol outperform**；Momentum break at inflection；Value underperform

**這是 load-bearing L2-to-L1 bridge**: factor 是 L2 vehicle，把 L1 regime view 轉成 actionable equity-portfolio tilt。

#### Ray Dalio debt-cycle mapping (less established)

Dalio 6 debt-cycle phase 在 published research 較少 mapped to factor (Polk et al. 用 NBER-style 4 phase)。合理 translation:

- **Early cycle** → Value + Size (analogous to Recovery)
- **Bubble** → Momentum (trend persistence dominate)
- **Top** → Quality 開始 outperform (late-cycle flight to safety)
- **Depression** → Quality + Low-Vol strongly lead；Value + Size crash
- **Beautiful deleveraging** → Value + Size return as growth normalize
- **Pushing on a string** → Quality / Low-Vol 再 lead (stagnation regime)

**Flag**: 這 mapping 是 **synthesis**，**不是 direct Dalio claim**。Dalio 不寫 factor investing。Cite 為「inferred parallel」。

### Critical Attribution Corrections (Fama-French cluster — 11 items)

#### 3-factor (1993) vs 5-factor (2015) vs Carhart 4-factor — distinguish when citing

1. **「Fama-French 3-factor」** ≡ **Fama & French 1993 JFE 33(1)** = {Mkt-Rf, SMB, HML}。

2. **「Fama-French 5-factor」** ≡ **Fama & French 2015 JFE 116(1)** = {Mkt-Rf, SMB, HML, RMW, CMA}。**不是 simple addition** — 2015 paper respecify SMB 為 orthogonal to new factors，並 note HML 在加入 RMW + CMA 後 statistically redundant。

3. **「Carhart 4-factor」** ≡ **FF3 + UMD**，from **Carhart 1997 JoF 52(1)**。**Not a Fama-French paper**。常被誤 cite 為「Fama-French-Carhart」但 Fama and French 不是 4-factor construction 的 author。

4. **FF5 不含 momentum**。2015 paper Fama 與 French 明確排除 momentum；他們的立場 (restated in Fama & French 2016 "Dissecting Anomalies with a Five-Factor Model") 是 momentum 是「lethal challenge」behavioral pattern，不是 rational asset-pricing model 的 integral part。**如要 momentum 模型，用 Carhart 4-factor 或「FF5 + UMD」**。

#### Momentum: Carhart 1997, ultimately Jegadeesh-Titman 1993

5. **Empirical anomaly** belongs to **Jegadeesh & Titman 1993 JoF 48(1)**。
   **Factor-portfolio construction** (UMD/WML) belongs to **Carhart 1997 JoF 52(1)**。
   **兩者皆非 Fama-French paper**。Cite momentum as factor → Carhart 1997；cite momentum anomaly → Jegadeesh-Titman 1993。

#### Quality: Asness-Frazzini-Pedersen 2019 QMJ, NOT FF RMW

6. **RMW** (Fama-French 2015) capture only operating profitability (single metric)。
   **QMJ** (AQR 2019) capture profitability + growth + safety (composite rank)。
   Practitioner Quality ETF (iShares QUAL, MSCI USA Quality) 在 construction 上更接近 QMJ。
   **不要 cite Fama-French 為「Quality factor」source** — cite Asness-Frazzini-Pedersen 2019 RAS 24(1): 34-112。

#### Low Volatility: Frazzini-Pedersen 2014 BAB, NOT Fama-French

7. **沒有 Fama-French paper 定義 low-volatility factor**。
   Canonical source 是 **Frazzini & Pedersen 2014 JFE 111(1)**。
   Practitioner Min-Vol ETF (iShares USMV) 用 MSCI minimum-variance optimization — 與 BAB construction 不同但 exploit 同樣 leverage-constraint premium。

#### Fama-French ≠ CAPM

8. CAPM (Sharpe 1964, Lintner 1965) = single-factor model with market risk only。
   FF3 **subsumes CAPM** as Mkt-Rf component，then add SMB + HML to capture cross-section variation unexplained by β。
   Fama & French 1992 empirically show β alone is **insufficient** — when size is controlled for, β-return slope is flat。
   **正確 framing**: FF 是 multi-factor extension of CAPM，**不是 replacement**；market factor preserved。

#### Fama-French ≠ APT (Ross 1976)

9. **APT (Ross 1976 JET 13(3))** 是 theoretical no-arbitrage argument that asset returns can be expressed as linear combinations of **unspecified** systematic factors。
   APT 提供 **mathematical foundation** (factor structure + no-arbitrage → linear factor pricing) 但 **不指明** 用哪些 factors。
   **FF 是 empirical factor-pricing model** — specify SMB / HML / RMW / CMA based on characteristic sort，**沒有** theoretical argument 為什麼這些應 priced。
   **正確 framing**: 「APT 是 theoretical umbrella；FF 是 one empirical specification of that umbrella」。但 FF 不是 literal APT test，FF paper 也不 cite APT 為 foundation — 它們 cite CAPM literature + build empirically。
   **不要說「Fama-French is a specific case of APT」** as primary claim — sloppy。說「APT 與 FF 都是 multi-factor framework；APT theoretical, FF empirical」。

#### Nobel credit

10. 2013 Nobel **jointly** awarded to **Fama, Hansen, and Shiller**「for their empirical analysis of asset prices」。
    Nobel citation 含 FF3/FF5 也含 Fama 早期 efficient-markets work (Fama 1970 JoF review) + tests of CAPM。
    **不要 claim「Fama won the Nobel for the 3-factor model」** — Nobel press release credit 是 body of empirical asset-pricing work，factor model 是其中 one strand。

#### Practitioner vs academic factor

11. **Long-only vs long-short**: academic FF factor 是 long-short (SMB, HML)。Practitioner ETF (iShares MTUM, VLUE, QUAL) 是 **long-only tilt** — rank stocks by characteristic + weight toward top half，沒 short leg。即 practitioner factor return 含 market beta，不是 pure factor premium。**Sector-neutral vs sector-loaded**: MSCI Quality / Enhanced Value 用 sector-neutral；academic FF 不用。**Construction differences**: MSCI value 用 composite (P/B, P/E, EV/CFO)，不是 B/M alone；MSCI momentum 用 6m+12m risk-adjusted return + half-yearly rebalancing，不是 French 2-12 month window。**Fee drag**: practitioner factor ETF 收 15–30 bps，吃掉 thin factor premia 的有意義 fraction。

### JP integration assessment — **Load-bearing**

#### Japanese factor-model evidence (primary sources)

- **Kubota, K. & Takehara, H. (2018)** "Does the Fama and French Five-Factor Model Work Well in Japan?" *International Review of Finance* **18(1): 137–146**. DOI: 10.1111/irfi.12126. RePEc: https://ideas.repec.org/a/bla/irvfin/v18y2018i1p137-146.html。**JP 因子模型測試的 canonical primary source**。Test FF5 on 1978–2014 Japanese stock data，發現 **RMW 與 CMA 在 GMM tests with Hansen-Jagannathan distance metrics 下不 statistically significant**。**結論: original FF5 不是日本資料的 best benchmark pricing model**。**這對任何 JP-equity factor-tilt claim 是 load-bearing**。**不要假設 FF5 transfer 到 Japan**。

- **Fama, E.F. & French, K.R. (2012)** (already cited above)。**Fama and French own evidence that Japan is the exception**: value premium 在日本存在，但 **momentum 不存在** — 「except for Japan, there is return momentum everywhere」。

- **Asness, C.S. (2011)** "Momentum in Japan: The Exception That Proves the Rule." *Journal of Portfolio Management* **37(4): 67–75**. SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1776123. AQR PDF: https://images.aqr.com/-/media/AQR/Documents/Journal-Articles/JPM-Momentum-in-Japan---The-Exception-That-Proves-the-Rule.pdf。**「Momentum 在日本死了」claim 的 canonical practitioner rebuttal**。Asness argue **value 與 momentum 在日本強負相關 (ρ ≈ −0.55)**，所以 zero-Sharpe momentum leg with strong negative correlation to positive-Sharpe value leg 是 valuable hedge，不是 broken factor。Asness 結論：momentum 在日本當 part of value-momentum system 分析時「works」。**這是處理「為什麼 JP factor investing 仍 use momentum 雖然 raw return ~0」的正確 cite**。

#### JP synthesis for `standards/investment-sector-industry.md`

When file discusses factor investing in Japanese context, text 必須:

1. **Cite Kubota & Takehara 2018** for FF5 RMW + CMA 在日本 not statistically reliable 的發現。Recommend FF3 或 Carhart 4-factor (with domestic factor data from Nomura / Daiwa) 為 JP equities base pricing model。
2. **Cite Fama & French 2012** for Japan-as-momentum-exception + recommendation to use **local factor model** rather than global one。
3. **Cite Asness 2011** for rationale to retain momentum in JP factor-tilt portfolio despite raw-return failure — 作為 value hedge within combined value+momentum sleeve。
4. **Note value premium 在日本存活** even when momentum 不 — 與 US post-2010 pattern 相反 (value 苦戰 + momentum lead)。

### Factor ETF industry adoption (practitioner context)

實務 reach evidence 讓 L2 factor analysis actionable:

- **iShares MSCI USA Min Vol Factor ETF (USMV)**: launch **2011-10-18**, BlackRock issuer, benchmark MSCI USA Minimum Volatility Index。**第一波 factor ETF**。
- **iShares MSCI USA Momentum Factor ETF (MTUM)**: launch **2013-04-16**, benchmark MSCI USA Momentum Index (selection on 6m + 12m risk-adjusted price momentum, volatility-adjusted)。
- **iShares MSCI USA Value Factor ETF (VLUE)**: launch **2013-04-16**, benchmark MSCI USA Enhanced Value Index (composite of P/B, P/E-forward, EV/CFO)。
- **iShares MSCI USA Quality Factor ETF (QUAL)**: launch 2013 (same Apr 16 cohort per BlackRock factsheet), benchmark MSCI USA Sector Neutral Quality Index (ROE, debt/equity, earnings variability)。
- **iShares MSCI USA Size Factor ETF (SIZE)**: launch 2013 (same cohort)。

**Aggregate market size**:
- **Smart-beta ETF AUM (ETFGI 2024-02)**: US$1.56 trillion globally (up from $1.49T end-2023, +5% YTD)
- **BlackRock 2016 projection**: $1T by 2020 (achieved), $2.4T by 2025 (achieved within few years of target)
- **Broader ETF industry**: $19.4T+ globally end-2025 (ETFGI)，factor/smart-beta ~8% of total ETF AUM

**Practitioner vs academic factor — key difference**：使用 factor ETF to express L1-regime view 時，要明確 **practitioner factor ETF 不是 pure FF factor**；它們是 sector-neutral long-only tilt with own construction choices。Regime mapping table 對兩者 directionally apply，但 magnitude 會不同。

### 對 `investment-sector-industry.md` 的應用

**Tier**: **Tier 2** (not Tier 3)。Fama-French 是 academic canon with well-indexed papers；hallucination risk 來自 **mis-specification across 3/4/5-factor variants，不是 paper existence**。Tier-2 treatment with explicit disambiguation 足夠。

**Body depth**: 200–280 lines 含 factor formula from French library (2×3 construction) + 3-vs-5 disambiguation + Carhart/AQR/BAB side-factors with explicit「not FF」tag + factor-regime mapping table 為 L2-to-L1 bridge。

**Must-include load-bearing content**:
- FF3 (1993 JFE) vs FF5 (2015 JFE) citation discipline
- Momentum = Carhart 1997 + Jegadeesh-Titman 1993，**NOT FF**
- Quality = AQR QMJ 2019，**NOT FF RMW** (practitioner conflation risk)
- Low-Vol = Frazzini-Pedersen BAB 2014，**NOT FF**
- FF ≠ APT，FF subsumes CAPM
- **JP exception**: Kubota-Takehara 2018 (FF5 fails in Japan) / Fama-French 2012 (JP momentum = 0 raw) / Asness 2011 (momentum still useful as value hedge in Japan)
- Factor-regime mapping table anchored to Polk-Haghbin-de Longis 2020 + MSCI classification
- iShares factor ETF launch cohort 2011-2013 + practitioner-vs-academic construction difference

**Out of scope for this file**: 完整「factor zoo」(300+ published factors) / p-hacking critique beyond Cochrane 2011 one-line coinage / machine-learning factor literature (Gu-Kelly-Xiu 2020 et seq.)。這些屬於另一個 Tier-3 quantitative-investing standard if ever added。

**Cross-references needed from `investment-macro-regime.md`**: Investment Clock 4-phase rotation 應有「see also: factor-regime mapping in investment-sector-industry.md」pointer，讓 reader working from L1 regime analysis 能找到 L2 factor tilt without re-research。

---

# Cluster F — Master List: 42 Critical Attribution Corrections

> 把 5 個 cluster 的 attribution corrections 全部列在一起，供 standards file drafter
> 在每個 file 中 selectively embed 為 anti-drift guardrail。total = 42。

## Hedgeye GIP (7)

1. GIP ≠ Merrill Lynch Investment Clock — different authors / firms / years / measurement / labels；sibling not parent/child
2. GIP 不是「最早」的 4-quadrant macro framework — Bridgewater/Dalio 1996 早 12 年
3. GIP 是 2-axis with derived Policy，不是 3-axis — Policy 是 reaction function map，不是 independent measurement
4. Darius Dale 是 co-author，not user — canonical attribution 「McCullough, Dale et al., Hedgeye Risk Management」
5. 「Quad 1/2/3/4」是 Hedgeye-specific nomenclature — 不要用於其他 4-box framework
6. 「27 年 backtest」是 firm-published，不是 independently audited — cite as「Hedgeye states」
7. 「Macro regime model」是 generic term — GIP 是其中 one specific firm-branded implementation

## MMT (7)

1. 「MMT = just print money」WRONG — MMT 明確 identify inflation / real-resource 為 binding constraint
2. 「MMT started with Kelton」WRONG — Mosler 1996 是 origin / Wray 2012 academic / Kelton 2020 popular
3. 「Japan proves MMT works」OVERCLAIM — Nersisyan & Wray 2021 Levy WP 985 是「No and Yes」；Kuroda + Fujimaki + Ito 都 contest
4. 「MMT is consensus economics」WRONG — 2019 IGM Forum poll zero endorsement
5. 「MMT and fiscal dominance are the same」WRONG BUT RELATED — MMT view 為 normal state, mainstream view 為 pathology (Sargent-Wallace 1981)
6. 「Chartalism and MMT are the same」NEARLY BUT NOT QUITE — MMT 是 neo-chartalism (Wray) = Knapp + Godley sectoral balances + Lerner functional finance + Post-Keynesian endogenous money + Minsky/Tcherneva JG + Mosler operational
7. 「Summers endorses MMT because Blanchard partially does」WRONG — distinct positions；Blanchard sympathetic to one MMT conclusion but uses mainstream framework not MMT premises

## RAI (10)

1. Wilmot 沒在「early 2000s」publish original RAI — Kumar & Persaud (2002) *International Finance* 5(3) 更早 + peer-reviewed
2. 「Credit Suisse RAI 1981-2011」charts 是 backfilled — 實 live index 始於 2004-02；pre-2004 historical reconstruction
3. Credit Suisse 2008-05 launch 的是 tradable product (European tracker certificate)，**不是** original index launch
4. Wilmot 約 2017–2018 離開 CS co-found XAI/WilmotML；James Sweeney 留 CS
5. RAI ≠ VIX — Illing-Aaron Table 2: CS RAI vs GRAI = −2% (effectively zero) 雖 theoretical 動機相同
6. RAI 是 positioning/sentiment-based，不是 fundamental — 沒 variant 用 GDP / earnings / valuation
7. 「Goldman Sachs RAI by Jan Hatzius」是 misattribution — GS Risk-*Aversion* Index (注意 inverse semantics) 來自 GS Economics Research 2003-10，與 Hatzius 不直接連結
8. 「BofA Global Investor Confidence Index」這個 named product 不存在 — 真正是 Bull & Bear Indicator (Hartnett team) + Global Fund Manager Survey
9. CSFB vs CS branding：CSFB Risk Appetite Index (2004–2006) = CS Global Risk Appetite Index (2006 後 rebrand)，**同一 index**
10. State Street ICI 是 NBER WP **10157**，不是 8226；author Froot (HBS) + O'Connell (State Street Associates)

## Taleb Barbell (7)

1. Barbell 是 extreme-extreme，**NOT middle-of-the-road** — colloquial「a little of stocks and a little of bonds」是相反的意義
2. Barbell 不規定 fixed percentage — 85/15 與 90/10 是 illustrative example，不是 formula
3. Primary source 是 *Antifragile* (2012) Ch 11，**not** *The Black Swan* (2007) Ch 13；Black Swan 是 first mention only
4. Spitznagel Universa 不是 Taleb's Barbell — Universa 是 tail-hedge overlay (96.7% SPX + 3.3% hedge)，enable 更高 risk-asset holding
5. Barbell 有「bleed」problem — Empirica Capital 2004 closure 為 primary evidence；low-volatility regime 中 option premia 產生 drag
6. Barbell 不是 mean-variance optimum — optimal 只在 fat-tailed distribution + VaR/CVaR constraint (Geman-Geman-Taleb 2015) 或 pure ruin-avoidance criterion 下
7. 「Antifragile」≠「Barbell」 — antifragility 是廣 concept；barbell 是 one specific instantiation

## Fama-French (11)

1. **「FF 3-factor」** ≡ FF 1993 JFE 33(1) = {Mkt-Rf, SMB, HML}
2. **「FF 5-factor」** ≡ FF 2015 JFE 116(1) = {Mkt-Rf, SMB, HML, RMW, CMA}；**not simple addition**；HML 變 redundant 在加 RMW + CMA 後
3. **「Carhart 4-factor」** ≡ FF3 + UMD from Carhart 1997 JoF 52(1)；**Not a Fama-French paper**；不要 cite「Fama-French-Carhart」
4. **FF5 不含 momentum** — Fama & French 2015/2016 explicit exclude；用 Carhart 4-factor 或「FF5 + UMD」如要 momentum
5. **Momentum**: 經驗 anomaly = Jegadeesh-Titman 1993 JoF 48(1)；factor construction = Carhart 1997 JoF 52(1)；**兩者皆非 FF**
6. **Quality factor**: AQR Asness-Frazzini-Pedersen 2019 QMJ RAS 24(1)；**not FF RMW**；practitioner ETF (iShares QUAL) 對齊 QMJ
7. **Low-Vol factor**: Frazzini-Pedersen 2014 BAB JFE 111(1)；**no Fama-French paper defines low-vol factor**；iShares USMV 用 MSCI minimum-variance optimization (不同 construction 但同 leverage-constraint premium)
8. **Fama-French ≠ CAPM** — FF subsume CAPM，不是 replace；market factor preserved
9. **Fama-French ≠ APT** — APT (Ross 1976 JET 13(3)) 是 theoretical no-arbitrage；FF 是 empirical specification；**不要說「FF is a specific case of APT」**
10. **Nobel credit**: 2013 Nobel jointly awarded Fama / Hansen / Shiller for empirical analysis of asset prices；**不是「for the 3-factor model」**
11. **JP exception load-bearing**: Kubota-Takehara 2018 IRF 18(1) (FF5 fails in Japan, RMW + CMA 不顯著) + Fama-French 2012 JFE 105(3) (Japan = momentum exception, 「except for Japan, there is return momentum everywhere」) + Asness 2011 JPM 37(4) (momentum 在日本當 value hedge work — value-momentum 強負相關 ρ ≈ −0.55) — 任何 JP-facing claim 都需要這 3 個 cite

---

# Cluster G — Integration Plan: 4 New Standards Files

## File 1: `standards/investment-macro-regime.md` (L1)

**Existing content from `investment-analysis-canon.md`** (carry forward):
- Merrill Lynch Investment Clock (Greetham & Hartnett 2004)
- Dalio Debt Cycle (Dalio 2018)
- Koo Balance Sheet Recession (Koo 2008)

**NEW content from this grounding**:
1. **Hedgeye GIP** (Cluster A) — 60–100 lines
2. **MMT** (Cluster B) — 120–180 lines (含 ~40–60 lines JP case study)
3. **RAI** (Cluster C) — 80–120 lines

**Total estimated body**: ~600–800 lines (含既存 Investment Clock / Dalio / Koo)

**Anti-drift section structure** (在每個 framework 下):
- 6 條 GIP guardrail
- 8 條 MMT guardrail (含 dual-citation rule)
- 8 條 RAI guardrail (含 Illing-Aaron honest caveat)

**Cross-reference**: Investment Clock 4-phase 加 「see also: factor-regime mapping in `investment-sector-industry.md`」pointer。

## File 2: `standards/investment-sector-industry.md` (L2)

**Existing content** (cross-reference from `investment-analysis-canon.md`):
- Porter 5 Forces (cross-ref to general strategic-frameworks)

**NEW content**:
1. **Fama-French Factor Investing** (Cluster E) — 200–280 lines
   - FF3 (1993) + FF5 (2015) + Carhart 4-factor (1997) disambiguation
   - QMJ + BAB 為 non-FF practitioner factors
   - Factor formula from Kenneth French data library
   - Factor-regime mapping table (L2 to L1 bridge)
   - JP exception (Kubota-Takehara + Asness 2011 + FF 2012)
2. **Sector rotation** mapping to L1 regime — ~50 lines
   - 對應 Investment Clock + Hedgeye Quad + MMT regime
   - Pro-cyclical (Tech / Cons Disc / Industrials / Materials) vs defensive (Cons Staples / Utilities / Healthcare)

**Total estimated body**: ~280–340 lines

**Anti-drift section**: 11 條 Fama-French guardrail + JP exception 強制 cite。

## File 3: `standards/investment-security-valuation.md` (L3)

**Existing content from `investment-analysis-canon.md`** (carry forward):
- Damodaran 3-framework (Investment Valuation 3rd ed 2012 + Dark Side of Valuation 3rd ed 2018)
- Graham & Dodd (Security Analysis 6th ed 2008)
- CAPE / Shiller P/E

**NEW content**: None for v4.11.0。L3 file 主要工作是把 v4.9.0 既存內容 carry over 並加 L3-explicit 段落 anchor。

**Total estimated body**: ~200–250 lines (mostly carry-forward)

## File 4: `standards/investment-portfolio-construction.md` (Portfolio)

**NEW file** — v4.11.0 全新建立。

**NEW content**:
1. **Taleb Barbell** (Cluster D) — 60–80 lines
2. **Risk Parity** (既存 framework，補 grounding) — 60–80 lines
   - Bridgewater All Weather (Dalio 1996+, "All Weather Story" Bridgewater white paper)
   - Concept lineage: Edward Qian (PanAgora) 2005 「Risk Parity Portfolios」white paper
   - 對比 Taleb Barbell 為 portfolio-layer thinking 的兩極

**Total estimated body**: ~150–200 lines

**Anti-drift section**: 7 條 Taleb guardrail（含 JP terminology trap） + Risk Parity 的 1996 vs 2005 attribution 問題。

**Pair-with framing**: 兩個 framework 並列 — Barbell =「fat tails 不可知」/ Risk Parity =「risks 可估」。

---

# Cluster H — Open Questions / Deferred

以下 question 在這個 grounding pass 中無法 fully resolve，作為 caveat surface 給 standards file drafter:

## Hedgeye GIP

1. **Exact quadrant threshold** — Hedgeye 沒公開（subscriber-only）；GIP 從 open source 不可重現
2. **Backtest methodology details** — universe / rebalancing frequency / transaction cost / regime transition handling / data revision treatment 都未公開
3. **Out-of-sample performance** — open literature 無 independent audit
4. **International GIP** — Hedgeye 跑 ~50 個 economy；EM CPI/GDP 資料品質下的方法論未公開
5. **McCullough vs Dale authorship split** — undocumented；Dale 的 42 Macro 自己 framework 已成為 partial fork
6. **Master The Market (2024 ebook)** — self-published promotional ebook；無 ISBN registry 驗證 / 無 academic review；最接近 canonical author text 但要 explicit「self-published」label

## MMT

1. **2022–2024 inflation episode 是否「證偽」MMT** — case 為 genuinely open；workers must present both interpretations
2. **MMT 在 dollarized economies 的 applicability** — MMT 自己 acknowledge scope-limited，但 **多大程度的 partial sovereignty 仍 qualify** 是 grey area
3. **政治 economy operability of MMT inflation control** — Kelton 2020 的 tax-raising mechanism 在 democratic politics 下是否 plausible 是 contested empirical question
4. **JP fiscal sustainability post-2024 BoJ exit** — yen weakness + YCC exit 是 evolving；2025–2026 update 需要 standards file 在 publication 後 active monitor

## RAI

1. **CS RAI 在 CS 收為 UBS 後的 continuity** — post-2023 publication status 不明
2. **CS RAI panic threshold 數值** — CS 沒 disclose；practitioner ±3σ 是 inference
3. **單一 RAI 是否 outperform composite** — Bundesbank 2009 conclude no single RAI definitively validated
4. **JP RAI** — 沒 Nomura/Daiwa 公開 variant；BoJ FSR heat map 是 closest analogue 但 functionally different (macroprudential not trading sentiment)

## Taleb Barbell

1. **Antifragile Ch 11 subsection title** — 透過 3 個 secondary summary cross-check 但未直接 PDF verify；physical book check 建議 before publication
2. **Universa 完整 historical performance 1999–2026** — Bloomberg paywall；只 2008 + 2020 + 2015 episode publicly verifiable
3. **AQR–Taleb feud 在 academic literature 的 status** — Asness response 未在 peer-reviewed journal published；只在 blog + tweets

## Fama-French

1. **Quality factor 在不同 region 的 transferability** — AQR QMJ 2019 paper 涵蓋 24 markets but Japan-specific calibration 未深入
2. **Factor-regime mapping 的 statistical robustness** — Polk-Haghbin-de Longis 2020 是 single SSRN paper；replication 不多
3. **Practitioner ETF construction 的 fee-after Sharpe** — 與 academic FF factor 比的 net-of-cost performance 在 multi-decade window 是 contested
4. **Machine-learning factor literature** — Gu-Kelly-Xiu 2020 + 後續 — 不在 v4.11.0 scope 但 future Tier-3 quantitative standard 需要

---

# Summary

**Phase 2 verified primary sources**: 50+ across 5 framework clusters。

| Cluster | Framework | Primary sources verified | Status |
|---|---|---:|---|
| **A** | Hedgeye GIP | 5 author-attributable + 2 backbone (Bridgewater + Greetham lineage) | ✓ verified；grey literature 充分 documented |
| **B** | MMT | 6 MMT primary + 5 ancestor + 9 mainstream critic + 5 JP critic + 4 JP proponent + 1 Levy WP 985 (Nersisyan-Wray) | ✓ all verified |
| **C** | RAI | 5 Tier-A canonical + 11 variant disclosures + BoJ FSR heat map | ✓ all verified；NBER number corrected 10157 |
| **D** | Taleb Barbell | 6 Taleb / Spitznagel primary works + Geman-Geman-Taleb 2015 mathematical anchor | ✓ all verified；Antifragile Ch 11 confirmed via secondary triangulation |
| **E** | Fama-French | 4 FF (1992/1993/2012/2015/2021) + Carhart 1997 + Jegadeesh-Titman 1993 + Frazzini-Pedersen 2014 + Asness-Frazzini-Pedersen 2019 + 3 JP exception (Kubota-Takehara 2018 + Asness 2011 + FF 2012) + Cochrane 2011 + Polk-Haghbin-de Longis 2020 + MSCI Bender et al. + Kenneth French data library | ✓ all verified |

**42 Critical Attribution Corrections** identified (7 / 7 / 10 / 7 / 11)。

**11+ misattributions prevented** before standards-file authoring:
- GIP 不是 IC 的 descendant（cross-attribution）
- GIP 不是 3-axis（dimensionality drift）
- MMT 不是「started with Kelton」（origin drift）
- MMT 不是 fiscal dominance（concept conflation）
- Wilmot 不是 RAI origin（temporal drift）
- NBER WP 8226 → 10157 (numeric drift)
- 「GS RAI by Jan Hatzius」(non-existent attribution)
- 「BofA Global Investor Confidence Index」(non-existent product name)
- Antifragile vs Black Swan primary source selection
- Universa ≠ pure Taleb Barbell (operational drift)
- Carhart 1997 ≠ Fama-French paper
- FF5 ≠ FF3 + momentum
- Quality factor source (AQR QMJ ≠ FF RMW)
- Low-Vol factor source (Frazzini-Pedersen BAB ≠ FF)
- FF ≠ APT (theoretical conflation)
- Nobel credit framing

**JP integration matrix**:

| Framework | JP integration level | Reason |
|---|---|---|
| Hedgeye GIP | None | US firm only；no JP corpus |
| MMT | **High** | Japan 是最 cited case study；Kuroda + Fujii + Ito + Fujimaki + Sakuragawa 等多角立場 |
| RAI | None public | BoJ FSR heat map 是 closest analogue 但 macroprudential not trading sentiment；不要 fabricate Nomura/Daiwa RAI |
| Taleb Barbell | None | JP「バーベル戦略」= bond duration ladder ≠ Taleb；terminology trap |
| Fama-French | **Load-bearing** | Kubota-Takehara 2018 + Asness 2011 + FF 2012 對任何 JP factor claim 都是必要 |

**Tier distribution** (across 4 new files):
- All 5 NEW frameworks: **Tier 2** — practitioner / heterodox / mixed academic-grey；none 達到 Tier 1 (peer-reviewed consensus core regime model)
- MMT 特殊處理: dual-citation rule (每個 MMT claim 必須 paired with mainstream critique citation)
- Fama-French 特殊處理: JP exception 是 load-bearing，不能 omit

**Phase 3 actions** (next):
1. Write `## Grounding Plan for research-team v4.11.0` output file per protocol
2. Pass tier classification + primary source list + 42 corrections forward to Phase 4
3. Flag 11+ misattribution-prevention items as standards-file body content (not just frontmatter)

**Phase 4 deliverables** (after this grounding):
- 4 standards files (3 modified + 1 new)
  - `investment-macro-regime.md` — NEW (含 Hedgeye GIP + MMT + RAI + carry-forward Investment Clock + Dalio + Koo)
  - `investment-sector-industry.md` — NEW (含 Fama-French canon + sector rotation + L2-to-L1 bridge)
  - `investment-security-valuation.md` — NEW (carry-forward Damodaran + Graham&Dodd + CAPE)
  - `investment-portfolio-construction.md` — NEW (含 Taleb Barbell + Risk Parity)
- All with `tier: 2` frontmatter declaration
- All with `## Critical Attribution Corrections` section embedding the 42 items selectively

**Total estimated standards line count**:
- `investment-macro-regime.md`: 600–800
- `investment-sector-industry.md`: 280–340
- `investment-security-valuation.md`: 200–250 (mostly carry-forward)
- `investment-portfolio-construction.md`: 150–200
- **Sum**: ~1230–1590 lines (vs single-file `investment-analysis-canon.md` ~280 lines)

**Worker BLOCKED reasons avoided**: All 5 NEW framework primary sources verified; no source unavailable to web search。Open questions (見 Cluster H) 都是 evolving / paywalled / methodological — 不 block standards file authoring，只需 transparent caveat。

---
