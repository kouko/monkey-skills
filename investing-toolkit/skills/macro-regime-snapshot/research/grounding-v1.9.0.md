---
title: macro-regime-snapshot 再設計研究 — 5 國 primary-source grounding + 20 年歷史軌跡
date: 2026-04-18
team: macro-regime-snapshot (investing-toolkit)
refactor_version: v1.9.0
tags: [research, investing-toolkit, macro-regime-snapshot, grounding, cross-country, r-star, nairu, inflation-target]
---

# macro-regime-snapshot Grounding Research — 5 國 threshold calibration 綜合

> **Backfill note**: 本文件是 `investing-toolkit/skills/macro-regime-snapshot`
> 的 v1.9.0 Option B 實作（per-country threshold files）之後的 **原典
> grounding audit trail**，模仿 `domain-teams` 團隊的 `research/grounding-v*.md`
> 慣例（見 `domain-teams/skills/skill-team/protocols/grounding-research.md`）。
>
> 五個國家 (US / JP / TW / KR / CN) 的 threshold 檔案
> `thresholds-{country}.md` 初稿是基於 2026-04-18 的網路搜尋合成，
> 本檔紀錄 **原典驗證階段** 的發現 + 修正。

## TL;DR — 核心發現

> [!important] Grounding 找出 25+ critical errors across 5 countries
>
> 每個國家的 r\* / NAIRU / 政策利率 / 集中度 / 通膨目標都有數字錯誤。
> 最震撼的 4 項：
>
> 1. **US**: FAIT (2020-2025) **已在 2025-08 Jackson Hole 退役**，改回 FIT
>    (Flexible Inflation Targeting)。初稿仍寫「FAIT 現行」
> 2. **JP**: BOJ 政策利率已 **0.75%**（2025-12 升息至 30 年新高）。初稿寫 0.5%
> 3. **CN**: CPI 目標 **已降至 2% 左右**（2025、2026 連續兩年），
>    2004 年以來首次低於 3%。初稿整份 "3% ceiling" 假設作廢
> 4. **KR**: KOSPI 삼성+SK하이닉스 = **39.88%**（2026-02）→ 40.90%
>    （2026-04 中旬），兩集團合計 **61.29%**（超越 S&P Mag-7 的 33.41%）。
>    初稿寫 ~30%

> [!important] 20-年歷史軌跡顯示各國 r\* 有結構性差異
>
> | 國家 | 2005-2007 r\* real | 2026 r\* real | 結構變化 |
> |------|--------------------|---------------|----------|
> | US | 2.0-2.5% | 0.75-1.68%（模型分歧）| GFC 後大幅下降、post-COVID 爭論中 |
> | JP | 0-1% | -1.0% ~ +0.5% | 80 年代以來下降 4pp，生產率 + 銀行危機 + 人口 |
> | TW | N/A 無官方 | N/A 無官方 | 小型開放經濟，政策利率歷史區間 1.125-3.625% |
> | KR | 推估 1-2% | ~0-1%（BOK 內部）| 人口高齡化 + 房市 + US r\* spillover |
> | CN | 推估 3-4% | 2-3%（BIS WP 949）| 增速下降貢獻 2/3（Rees & Sun 2021）|

> [!important] 各國都獨立發展自己的 regime 框架 — 不能機械套用
>
> - **US**: Fed 雙目標、Fed r\* 三家模型（HLW / LM / NY Fed composite）
>   ± SEP dot plot，最發達
> - **JP**: 1980 年代以來獨自 r\* 研究系列（WP03 → lab18 → WP24 →
>   rev26），唯一 r\* < 0 的先進國。獨特的 YCC/QQE post-deflation 制度轉換
> - **TW**: CBC 用「具彈性的物價穩定定義」 + NDC 五色景氣燈號（9 指標
>   綜合，獨有 regime indicator）。不存在 Fed-style formal target
> - **KR**: BOK 2018-12-26 將目標體制簡化為 "2% 無期限 point target"，
>   triple-mandate（物價+金融穩定+環率），宏觀審慎政策領先貨幣政策
> - **CN**: PBOC 多目標，2024 利率走廊改革（7D OMO 取代 MLF 為政策錨）、
>   2025 首次「適度寬鬆」語言（GFC 以來第一次）、CPI 目標 2025 首次下調至 2%

---

## 驗證方法論

### Phase 1（各國母語原典驗證）

本研究透過 5 個 `general-purpose` agent 並行執行，每個 agent：

- 負責**單一國家**（US / JP / TW / KR / CN）
- 使用該國**母語搜尋 + WebFetch** 原典（BOJ、CBC、BOK、PBOC、NBS、Fed、CBO、
  日銀 WP、KDI、中証指數等官網）
- 驗證初稿 `thresholds-{country}.md` 的每個具體主張
- 建構 **2005-2026（20 年）** 歷史軌跡

狀態 label：
- ✅ **已驗證**（主張與原典一致）
- ⚠️ **部分驗證**（接近但需修正）
- ❌ **無法驗證**（找不到原典）
- 🔴 **錯誤**（原典明確否定）

### Phase 2（本文件綜合 audit trail）

Phase 1 的 5 個 agent output 合成本文件。每個國家一節。最後總結
「跨國 grounding 原則」+「recalibration 指導」。

---

## US — Grounding 驗證結果

### Agent source

`grounding-us` agent（2026-04-18，~3100 words，~48 tool uses）

### 關鍵修正（7 個 claim）

| # | 初稿主張 | 實際 | 狀態 |
|---|----------|------|------|
| 1 | FAIT 2020 reaffirmed | **FAIT 於 2025-08 Jackson Hole 退役**，改回 FIT (Flexible Inflation Targeting) | 🔴 Wrong |
| 2 | CBO 2026 失業率預測 4.5-4.6% | **4.6%**（CBO Feb 2026 Outlook 61882；下降到 2028-29 的 4.4%，然後穩定 4.2%）| ⚠️ Partial |
| 3 | HLW r\* = 1.42% real | **~0.75% real**（2025-Q4 NY Fed HLW，Williams 維持 r\* 未顯著上升）| 🔴 Wrong（1.42 可能是 LW-closure） |
| 4 | Lubik-Matthes r\* = 2.15% real | **1.68% real**（2025-Q4，Richmond Fed 2026-03-10 最新）| 🔴 Wrong |
| 5 | FOMC Dec 2025 long-run dots real = 0.6-1.9% | ✅ 範圍正確。Median real 1.0%、central tendency 0.8-1.5%、full range 0.6-1.9%（19 dots）| ✅ Verified |
| 6 | DFII5 = 1.31% / DFII10 = 1.93% | ✅ Fed H.15 2026-04-17 release 精確匹配 | ✅ Verified |
| 7 | Williams Dec 2025 + Jan 2026 "modestly restrictive" | ✅ BIS review r251216h + r260203n 精確引用 | ✅ Verified |

### 20-年軌跡（r\* real, US）

| 期間 | HLW | Lubik-Matthes | FOMC SEP long-run real | 背景 |
|------|-----|---------------|------------------------|------|
| 2005-2007 (pre-GFC) | 2.0-2.5% | 2.0-2.5% | n/a | "Great Moderation" |
| 2008-2009 (GFC) | 2.0→0.5%（1 年降 1.5 pp）| 相同 | - | ZLB Dec 2008 |
| 2010-2015 (ZLB) | ~0.5% stable | 1.0-1.5% | 2012 implicit ~2.25% | QE1-3 + Summers secular stagnation |
| 2016-2019 (normalization) | 0.5-0.6% | 0.5-1.0% | 2019 0.5% real（大幅下修）| Fed funds 0→2.50% |
| 2020-2021 (COVID) | 暫升 ~1.1% | 類似暫升 | 2020 unchanged 0.5% | ZLB Mar 2020、FAIT Aug 2020 |
| 2022-2023 (hiking) | 回落 0.7-0.8% | 上升 1.5-2.0% | 2023 unchanged 0.5% | Fed funds 0→5.25% 18 months |
| **2024-2025** | ~0.75% | 1.42-1.68% | Dec 2025: **1.0% median, 0.8-1.5% CT, 0.6-1.9% range** | SEP drift up ~50 bp from 2019 trough |
| **2026-Q1** | ~0.75% | 1.68% | 1.0% real | Framework 從 FAIT → FIT |

### 歷史視角歸納（US）

1. **HLW-LM 發散 ~1 pp post-2020**：NY Fed 堅持 r\* 未顯著上升，Richmond Fed
   Lubik-Matthes 說已上升。學界未解。
2. **SEP long-run dot 20 年漂移**：2012 real 2.25% → 2019 0.5% → 2025 1.0%。
   Dec 2025 代表自 2019 谷底 **回升 ~50 bp**，但仍比 pre-GFC 錨低 125 bp。
3. **pre-GFC 基準顛覆當前閾值**：2006 的 "Clearly Restrictive" 閾值（DFII ≥ 1.75%）
   當時會是 **Neutral**。4-tier bands 隱含 post-GFC 低 r\* 為新常態。
4. **GFC r\* 衝擊**：2008-2009 一年下降 1.5 pp 是歷史最大 1-年變化。當 r\*
   發生 step-change 時，閾值必須重新校準（不只是加新數據）。
5. **FAIT → FIT 轉換 (2025-08)**：通膨目標帶解釋改變。FAIT 容忍 2% 溫和
   overshoot；FIT 對稱，2% 上下偏離同等對待。

### US 主要 sources

- [Fed FOMC 2012-01-25 Statement](https://www.federalreserve.gov/newsevents/pressreleases/monetary20120125c.htm) — 2% PCE target 採用
- [Powell Jackson Hole 2025-08-22](https://www.federalreserve.gov/newsevents/speech/powell20250822a.htm) — **Framework review: FAIT → FIT**
- [FOMC SEP Dec 10 2025](https://www.federalreserve.gov/monetarypolicy/files/fomcprojtabl20251210.pdf) — long-run median 3.0% / real 1.0%
- [Fed H.15 2026-04-17](https://www.federalreserve.gov/releases/h15/) — DFII5 1.31% / DFII10 1.93%
- [NY Fed HLW Research Page](https://www.newyorkfed.org/research/policy/rstar)
- [Richmond Fed Lubik-Matthes](https://www.richmondfed.org/research/national_economy/natural_rate_interest) — 1.68% 2025-Q4
- [Williams "Resilience" 2025-12-15 (BIS)](https://www.bis.org/review/r251216h.htm)
- [Williams "A Few Words for the New Year" 2026-01-12 (BIS)](https://www.bis.org/review/r260203n.htm)
- [CBO Budget & Economic Outlook 2026-2036 (62105)](https://www.cbo.gov/publication/62105)
- [Liberty Street Economics 2025-08](https://libertystreeteconomics.newyorkfed.org/2025/08/are-financial-markets-good-predictors-of-r-star/)

---

## JP — Grounding 驗證結果

### Agent source

`grounding-japan` agent（2026-04-18，~3900 words，~30 tool uses）

### 關鍵修正（9 個 claim）

| # | 初稿主張 | 實際 | 狀態 |
|---|----------|------|------|
| 1 | BOJ 2% 目標 2013-01-22 採用 | ✅ 原文一致 | ✅ Verified |
| 2 | 容認帶不存在，"概ね整合的"用語 | ⚠️ 用語正確，但出現於展望レポート本文而非 FAQ 頁。出典修正 | ⚠️ Partial |
| 3 | BOJ 展望 2025-10 CPI: **FY2024 2.5% / FY2025 1.9% / FY2026 1.9%** | **FY2025 2.7% / FY2026 1.8% / FY2027 2.0%**（年度全錯一年、FY2025 差 0.8 pp）| 🔴 Wrong |
| 4 | WP24-J-09 r\* range -1.0% to +0.5%、mean -0.25% | range -1.0% to +0.5% ✅；"mean -0.25%"**是 range 中點的派生值**，非原典表述，應避免 "mean" 一詞 | ⚠️ Partial |
| 5 | JILPT 均衡失業率 = 3.5-3.6% | **2.80%**（2026-02 最新；2025Q4 = 2.78%），需要不足失業率 -0.17%。差 0.8 pp | 🔴 Wrong |
| 6 | 失業率 2026-01 2.7% / 2026-02 2.6% | ✅ 2026-02 = 2.6%（労働力調査）| ✅ Verified |
| 7 | BOJ 政策利率 ~0.5%（post-YCC）| **0.75%**（2025-12 升息至 30 年新高；2026-01-23 維持）| 🔴 Wrong |
| 8 | 野村 森田京平 2026 main scenario: 2 hikes to 1.0% by 2026 末 / 1.25% 2027H1 | **main (60%): 3 hikes to ターミナル 1.50%** by 2027-06（2026-06, 2026-12, 2027-06 各 +25bp）；risk (40%): ターミナル 1.75% | 🔴 Wrong |
| 9 | 10Y JP real yield -0.386%（G7 唯一負）| 伊藤忠コラム本文**不含此數值**；出典無效，應刪除 | ❌ Unverified |

### 新發現的 BOJ 原典（初稿未引用）

- **BOJ 日銀レビュー rev26j05 (2026-03-27)**: 企画局發布。WP24-J-09 2024 年
  推計在 GDP 基準改定後**再推計**。**這是 BOJ 最新官方 r\* 見解**，取代
  WP24-J-09 作為正式參考。「推計値には相當なばらつきがある」明文
- **BOJ リサーチラボ lab18j02 (2018-06)**: 須藤直・岡崎陽介・瀧塚寧孝。
  DSGE + OLG(80 世代) 分解 1980 年代以來 r\* 下降 ~4 pp：
  - 技術進歩率 ~2 pp
  - 銀行危機（1990s半ば～2000s 初頭）~1 pp
  - 人口動態殘差
- **BOJ WP03-J-05 (2003-10)**: 小田信之・村永淳。日本 r\* 分析原點；
  首次示唆「1997 年以降負圏の可能性」

### 20-年軌跡（r\* real, JP）

| 期間 | 代表值 | Paper |
|------|--------|-------|
| 1980s | ~3-4% | - |
| 1990s | ~2-3% | - |
| 2000s | 0-1% | WP03-J-05 顯示 1997 後可能負 |
| 2010s | 0% 前後 | lab18j02 "概ね 0% 程度"、WP18-E-06 |
| 2020s early | -0.5% 前後 | - |
| 2024-2026 | **-1.0% to +0.5% レンジ** | WP24-J-09 (2024-08) + rev26j05 (2026-03) |

### 歷史視角歸納（JP）

1. **日本 r\* 在 2000 年代早已 0-1%**，當前 -1.0% ~ +0.5% 不是「異常低」，
   是 1990 年代銀行危機以來結構下降的終點。r\* 回升到 +1% 的蓋然性低
   （人口、生產率趨勢不易反轉）。
2. **2013-2023 年 JP 長期金利 YCC 下人為抑制**。2024-03 之後才是市場主導，
   歷史上首次與 2006-2012（YCC 前）+ 2013-2023（QQE 期）皆不同 regime。
   閾值校準應以 2024-04 後 sample 重學習。
3. **2% 通膨目標「達成」是 2023-2024 首次**。30 年來 regime 轉換。
   「CPI < 2%」不應機械視為 "Below target"，需看是「未達成」還是
   「達成後回歸中樞」。
4. **JILPT 均衡失業率 2005 → 2026: 5% → 2.8%**（-2.2 pp 結構下移）。
   用絕對數字判「歷史 tight」會錯；bands 應以均衡失業率 ± 0.3 pp
   相對 gap 設計。
5. **2025-12 升息到 0.75% 是 30 年來最高**，但野村 main scenario ターミナル
   1.50% 僅接近中立（r\* -0.25% + 2% 目標 ≈ 名目 1.75%）。2026-2027
   + 2 hikes 仍應解讀為「接近中立」而非明顯緊縮。

### JP integration decision

> **日本の regime call では日本語原典の數値を優先**。英語圏 r\*
> framework（HLW-US、Fed SEP）不可機械適用到日本 —
>
> 1. JP 是 G7 最低 r\*（唯一 -1% ~ +0.5% range），獨自 deflation regime，
>    獨自人口結構
> 2. BOJ WP/展望 20 年一貫方法論，針對日本特化，優於英語圈適用版
> 3. JILPT UV 分析針對日本獨特勞動市場（終身雇用殘滓、正規/非正規、
>    高齢者就業），英語圈 NAIRU 無法代替
> 4. 展望 政策委員中央値 是 BOJ 9 人投票分布，比 IMF/OECD 外部推計
>    政策含意直接

### JP 主要 sources

- [BOJ 物価安定の目標](https://www.boj.or.jp/mopo/outline/target.htm)
- [BOJ WP24-J-09 (2024-08)](https://www.boj.or.jp/research/wps_rev/wps_2024/wp24j09.htm)
- [BOJ 日銀レビュー rev26j05 (2026-03-27)](https://www.boj.or.jp/research/wps_rev/rev_2026/rev26j05.htm) — **最新 BOJ 公式 r\* 見解**
- [BOJ lab18j02 (2018-06)](https://www.boj.or.jp/research/wps_rev/lab/lab18j02.htm) — r\* 下降 4 pp 分解
- [BOJ 展望レポート 2025-10](https://www.boj.or.jp/mopo/outlook/highlight/ten202510.htm)
- [JILPT UV 分析 2026-02](https://www.jil.go.jp/kokunai/statistics/topics/uv/uv.html) — 均衡失業率 2.80%
- [野村 ウェルスタイル 0571 (2026-01-26)](https://www.nomura.co.jp/wealthstyle/article/0571/) — main ターミナル 1.50%
- [BOJ 総裁記者会見 2026-01-23](https://www.boj.or.jp/about/press/kaiken_2026/kk260126a.pdf)

---

## TW — Grounding 驗證結果

### Agent source

`grounding-taiwan` agent（2026-04-18，~3850 words，~48 tool uses）

### 關鍵修正（8 個 claim）

| # | 初稿主張 | 實際 | 狀態 |
|---|----------|------|------|
| 1 | CBC「具彈性的物價穩定定義」 | ✅ 2024-06-19 中央社原文一致；但**理監事決議新聞稿本身未使用「具彈性」字眼**，改稱「適時調整」。「彈性」是央行高層場外解釋語 | ⚠️ Partial |
| 2 | 燈號 5 色分數（紅 38-45 / 黃紅 32-37 / 綠 23-31 / 黃藍 17-22 / 藍 9-16）| ✅ NDC 官方確認 | ✅ Verified |
| 3 | 9 個構成指標 | **2 個錯**：①「非農業部門就業人數」→ 實際是 **工業及服務業加班工時**；②「製造業存貨率比率」→ 實際是 **製造業營業氣候測驗點 (TIER)** | 🔴 Wrong |
| 4 | CBC 貼現率 2.00% | ✅ 2025-12-18 理監事會維持 | ✅ Verified |
| 5 | CPI 2026-01 0.69% / 2026-02 1.75% / 2026-03 1.2% | 2026-03 DGBAS 公告 **1.20%** 精確；01/02 DGBAS 首頁未抓到原稿但與 macromicro 時序一致 | ⚠️ Partial |
| 6 | NAIRU 3.5-4.0% | ⚠️ CBC 季刊 NAIRU 論文存在（WebFetch 解析限制二進位 PDF），學術支撐 3.5-4.0% 區間但 **CBC/DGBAS 無官方單一 NAIRU 發布值**。應降級為「學術推估」 | ⚠️ Partial |
| 7 | TSMC 佔 TAIEX ~40% | **44.30%**（TWSE 2026-03-31；前 10 大合計 58.27%；5 年從 28% 暴升 +17 pp，歷史最高集中度）| 🔴 Wrong (低估) |
| 8 | 失業率 2009 GFC peak 6.1% | **月峰 2009-08 6.04%**，年均 5.85% | 🔴 Wrong (小) |

### 新發現

- **景氣對策信號 9 次修訂（1978/1984/1989/1995/2001/2007/2013/2018/**2024**）**。
  初稿隱含「現行版本 = 2013 修訂」錯誤；**2024 才是現行 vintage**
- **2014-2023 十年無紅燈** → **2024-02 首度破紅燈 + 創 31 年分數新高 40 分**
- 2026-02 再現紅燈 40 分（連續維持）

### 20-年軌跡（TW）

| 年 | 失業率年均 | CBC 利率 | TSMC 權重 |
|----|------------|----------|-----------|
| 2005 | 4.13% | 升息中 | ~10% |
| 2008 GFC | 4.14% (peak 6.04% 2009-08) | 3.625% peak | - |
| 2009 | 5.85% 年均 | 1.25% 降至 | - |
| 2015 | 3.78% | 1.875% | 16-18% |
| 2020 COVID | 3.85% | 1.125% | 27-30% |
| 2022-2023 | 3.48% | 升到 1.875% | 30-32% |
| **2024** | **3.38%（24 年新低）** | 2.00% 至今 | 34.39% (6 月) |
| **2026-Q1** | ~3.4% | 2.00% 連凍 | **44.30%**（2026-03-31）|

### 歷史視角歸納（TW）

1. **2005-2020 年均 CPI 僅 ~1.0%**。2% 對台灣是「警戒線」非「目標」。
   「正常區間」更接近 **0-2%**
2. **景氣燈號 9 次修訂**（早期歷史數據不可直接類比）。紅燈出現率
   ~8-10% 月份，是強訊號。2014-2023 **十年無紅燈**；2024-02 打破空窗
3. **TSMC 2020 → 2026 從 28% 暴升 44.30%（+17 pp）**。TAIEX 本質已近
   「TSMC ADR 代理」。regime 訊號必須意識到集中風險
4. **CBC 2.00% 在台灣歷史並非緊縮**（GFC 前峰 3.625%）。與 Fed 差
   300+ bp 是結構常態
5. **2024-Q1 失業率 3.38% 為 24 年新低**，**低於學術 NAIRU 下限 3.5%**。
   但台灣工資-通膨傳導弱（supply chain 主導）+ 少子化使 NAIRU 長期
   下行，**不宜機械套 Phillips Curve**

### TW 主要 sources

- [CBC 2025-Q4 理監事會新聞稿](https://www.cbc.gov.tw/tw/cp-971-189509-ee98e-1.html)
- [NDC 景氣對策信號簡介](https://www.ndc.gov.tw/nc_335_2236)
- [NDC 歷次修訂過程 nc_336_2245](https://www.ndc.gov.tw/nc_336_2245)
- [中央社 2024-06-19 「CBC：採彈性定義較妥適」](https://www.cna.com.tw/news/afe/202406190101.aspx)
- [CBC 季刊 NAIRU 論文 (PDF)](https://www.cbc.gov.tw/tw/public/Attachment/211121602471.pdf)
- [TWSE 加權指數成分股暨市值比重 (2026-03-31)](https://www.taifex.com.tw/cht/2/weightedPropertion) — TSMC 44.30%
- [DGBAS 「115 年 3 月 CPI 1.20％」](https://www.dgbas.gov.tw/News_Content.aspx?n=3602&s=236110)

---

## KR — Grounding 驗證結果

### Agent source

`grounding-korea` agent（2026-04-18，~3850 words，~31 tool uses）

### 關鍵修正（9 個 claim）

| # | 初稿主張 | 實際 | 狀態 |
|---|----------|------|------|
| 1 | BOK 2% 目標 2019 設定 | **2018-12-26 發表，2019 起適用**。「적용기간을 정하지 않고 계속 2.0%」；ex-3 年週期再設定 | ⚠️ Partial |
| 2 | 2016-2018 目標 = 2% | ✅ 2016 已轉單點 2%，2018-12 修正 = 維持 + 無期限化 | ✅ Verified |
| 3 | 2013-2015 = 2.5-3.5% | ✅ | ✅ Verified |
| 4 | 2010-2012 = 3% ± 1% | ✅ | ✅ Verified |
| 5 | **2007-2009 = 2.5-3.5% (core CPI)** | 🔴 **顛倒！** 2007-2009 是 **headline CPI 3% ± 0.5%**；2.5-3.5% core 是 **2004-2006** | 🔴 Wrong |
| 6 | 容認帶不存在、균형있게 | ✅ BOK 官方原文 confirmed | ✅ Verified |
| 7 | 2026 CPI 전망 2.1% | ✅ BOK 2025-11 發布 2.0%，2025-12-17 上修 2.1% | ✅ Verified |
| 8 | 기준금리 2.50% (2026-01-15 決定) | **降息日 2025-05-29**，2026-01-15 是 5 連凍結之一 | ⚠️ Partial |
| 9 | NAIRU 1980s 3.7-4.0% / 1988-97 2.6-3.2% / 1998-2000 4.0-5.3% / 現在 3.0-3.5% | 1979-87 / 1988-97 ✅；**1998-2000 錯** — 峰值區間 **1998-2004**。現在 3.0-3.5% 是「合意推定」非單一發布值 | ⚠️ Partial |
| 10 | 現在 실업률 2.7% | 2.7% 是 **2026-03 계절조정**；**原系列 2026-01 = 4.1%、2026-02 = 3.4%**（季節性 Q1 前半高點）；청년실업 2026-02 7.7%（5 년 최고）| ⚠️ Partial |
| 11 | BOK 無公式 r\*、nominal 2.25-2.75% | ✅ BOK 無公式。**BOK 연구원 Do/Ahn/Jung 2024 multi-model**: real **~0-1%**（下限近零可能），nominal 2-3% | ⚠️ Partial |
| 12 | 삼성전자 ~20% + SK하이닉스 ~10% = ~30% | **39.88%**（2026-02-27）→ **40.90%**（2026-04 中旬）。삼성그룹+SK그룹 **61.29%**（1 년前의 2 倍）| 🔴 Wrong (大幅低估) |
| 13 | 家庭負債/GDP ~105% | **89.4%**（2025-Q3 BIS）/ 92.3%（BOK 2025-09）。**105% 是 2021 峰**，已回落 ~10 pp。OECD 6 위 | 🔴 Wrong |
| 14 | - | **新發現**: KR 2026-01 起 BIS 重分類為 advanced economy（ex-emerging）| ✅ New |

### 20-年軌跡（KR）

| 期間 | 목표 | 기준금리 | 背景 |
|------|------|----------|------|
| 2004-2006 | core 2.5-3.5% | 변동 | - |
| 2007-2009 | headline 3% ± 0.5% | 3.25→5.25→2.00% (2008-2009) | GFC 대응 |
| 2010-2012 | 3% ± 1% | 2.00→3.25→2.75% | |
| 2013-2015 | 2.5-3.5% | 2.75→1.50% | |
| 2016-2018 | 2% point | 1.25→1.75% | 家庭부채 우려 |
| 2019-2024 | **2% 무기한** | 1.75→0.50 (2020)→3.50% (2023)→3.50 (2024) | COVID + 급등 |
| **2025** | 2% 유지 | 3.50→**2.50%** (2025-05-29) | - |
| **2026-Q1** | 2% 유지 | **2.50% 5 연속 凍結** | KRW 16 년 저점 + Fed 불확실성 |

### 歷史視角歸納（KR）

1. **NAIRU hysteresis 留存**：1997 外環위기 讓 NAIRU 從 2.6-3.2% 永久上移
   到 4-5.3%，花 20 年回落到 3.0-3.5%。**unemp > 3.6% 應視為結構警戒**
2. **KOSPI 集中度扭曲宏觀政策**：2026-Q1 삼성+SK하이닉스 40% 讓 BOK/기재부
   實質上「半導體政策 = 宏觀政策」。regime 訊號不能把 KOSPI 當 broad market
3. **家庭負債 99% 峰 → 90% 下降是 de-leveraging**。**變化率比 level 重要**；
   閾值應加「YoY 變化率」— 再加速 +2% 會觸發 BOK 鷹派
4. **BOK 2018-12「2% 無期限」是制度簡化完成**（3 年週期 → 無期限、band → point、
   core → headline），是世界最 lean IT 體制之一
5. **r\* 不透明是刻意選擇**（vs Fed SEP）— 閾值「real vs r\*」要靠市場共識
   (KTB-swap spread、KRW、前瞻金利曲線) 間接估

### KR 主要 sources

- [BOK 물가안정목표제 (menuNo=200291)](https://www.bok.or.kr/portal/main/contents.do?menuNo=200291)
- [BOK 2019 목표 설정 보도자료 (2018-12-26, nttId=10049381)](https://bok.or.kr/portal/bbs/B0000170/view.do?menuNo=200060&nttId=10049381)
- [BOK 통화정책방향 보도자료 (P0000559)](https://www.bok.or.kr/portal/bbs/P0000559/)
- [BOK 기준금리 추이](https://www.bok.or.kr/portal/singl/baseRate/progress.do?dataSeCd=01&menuNo=200656)
- [KDI JEP 26-2-3 신석하 2004](https://kdijep.org/assets/pdf/598/jep-26-2-3.pdf) — NAIRU 기본 학술
- [Do, Ahn, Jung (2024) BOK 연구원 r\* multi-model (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5009627)
- [Seoul Economic Daily 2026-02-27 — 삼성+SK 61% KOSPI share](https://en.sedaily.com/news/2026/02/27/samsung-sk-market-cap-hits-18t-doubling-share-to-61-percent)
- [BIS Total Credit Statistics](https://www.bis.org/statistics/totcredit.htm) — 가계부채/GDP
- [BOK 경제전망보고서 2025-11](https://www.bok.or.kr/portal/bbs/P0002359/view.do?nttId=10094817&menuNo=200066)

---

## CN — Grounding 驗證結果

### Agent source

`grounding-china` agent（2026-04-18，~3950 words，~44 tool uses）

### 關鍵修正（9 個 claim）

| # | 初稿主張 | 實際 | 狀態 |
|---|----------|------|------|
| 1 | **CPI 目標 3%** | **2% 左右**（2025、2026 政府工作報告連續兩年）。**2004 年以來首次下調**（從「防過熱 ceiling」變「促回升 中樞」）| 🔴 Wrong (重大) |
| 2 | LPR 1Y ~3.1% | **3.0%**（2026-Q1 連續多月未動）| ⚠️ Partial |
| 3 | LPR 5Y ~3.6% | **3.5%** | ⚠️ Partial |
| 4 | MLF 1Y ~2.5%（作為政策工具）| **PBOC 2024 已取消 MLF 政策利率**。**改以 7 天逆回購 1.40% 為主政策利率**。MLF 轉為數量工具 | 🔴 Wrong |
| 5 | RRR 大型銀行 ~9.5% | **9.0%**（2025-11 末調整）| ⚠️ Partial |
| 6 | 7 天逆回購 ~1.5% | **1.40%**（2025-09 下調後未動）| ⚠️ Partial |
| 7 | 2026 PBOC「適度寬松」 | ✅ 3-31 PBOC 第 112 次例會：「繼續實施適度寬鬆」。**GFC 以來首次回歸「適度寬鬆」** | ✅ Verified (+ 新 insight) |
| 8 | 2025 城鎮調查失業率 5.2% / 2026 目標 5.5% | ✅ NBS 王萍萍 2026-01-19 | ✅ Verified |
| 9 | 「中國無公開 r\* 估計」 | 🔴 **錯**。**BIS WP No 949 (Rees & Sun 2021)** Bayesian 估計 1995Q2-2019Q4：當前 r\* **real 2-3%**（95% CI 1.5-3%）。GFC 後持續下行，潛在增速下降貢獻 2/3 | 🔴 Wrong |
| 10 | nominal ~3.0-3.5% / real ~0.5-1.5% | Rees & Sun 的 r\* 為 **real 1.5-3%**（不是 0.5-1.5%）。nominal ≈ r\* + 2% CPI ≈ **3.5-5%** | 🔴 Wrong |
| 11 | 2026 CPI 預期 ≤ 1.5% | ⚠️ 方向正確但偏保守。中銀證券預測 **0.1-0.8% M 型**，中銀研究院預期「企穩回升」 | ⚠️ Partial |
| 12 | 房地產/GDP ~25-30% | ✅ Rogoff & Yang 2021：直接 23.6% / 含基建 **31%**（vs US 18%）| ✅ Verified |
| 13 | CSI300「金融+SOE 主導」 | 🔴 **過時**。2016 金融 **35.45%** / IT 9.22% → 2025 金融 **22.97%** / IT **20.38%**。已轉為金融/消費/新能源/AI 四分天下 | 🔴 Wrong |
| 14 | 核心 CPI 低於總體 CPI | 🔴 2026-Q1 **反轉**：總體 CPI 0.9% < 核心 CPI 1.1-1.3%。食品（豬肉 -11.5%）拖累總體 | 🔴 Wrong (當前) |

### 新發現

- **CPI 目標 20 年完整軌跡**（重大發現）：
  - 2005-2007: 3% / **2008: 4.8%** / 2009: 4% / 2010: 3% / **2011-2012: 4%** / 2013-2014: 3.5% / 2015-2019: 3% / **2020: 3.5%（COVID）** / 2021-2024: 3% / **2025-2026: 2%**
  - 2025 是 **自 2004 年以來首次 < 3%**；從「防過熱 ceiling」變「促回升 中樞」
- **「適度寬鬆」是 2010 以來首次**。PBOC 語言階梯：穩健 / 穩健略偏寬鬆 / 穩健偏松 / 適度寬鬆 / 寬鬆。
  2024 中央經濟工作會議 + 2025 正式定調。**與 1998-1999、2008-2009 兩段歷史同列**
- **PBOC 2024-07 正式確認 7 天逆回購為主政策利率**（MLF 退位）
- **青年失業率方法論斷裂**：2023-08 暫停 → 2024-01 換「不含在校生」口徑。
  2018-2023 vs 2024-2026 不可直接比較
- **r\* 研究狀態**：BIS WP 949 (Rees & Sun 2021) 是權威，但截至 2019Q4；
  post-2020 房市危機 + 通縮可能進一步下壓
- **Sun Guofeng (PBOC 原貨幣政策司長) 2023 因案被判刑**，PBOC 內部 r\* 研究能見度下降

### 20-年軌跡（CN）

| 期間 | CPI 目標 | 政策語言 | 主軸 |
|------|----------|----------|------|
| 2005-2007 | 3% | 穩健偏松 | 高速增長 |
| 2008-2009 | **4.8%/4%** | **適度寬鬆**（GFC）| 四萬億刺激 |
| 2010-2012 | 3-4% | 穩健 | 通膨壓力 |
| 2013-2019 | 3-3.5% | 穩健 | 長期穩定 |
| 2020 | 3.5% | 穩健略偏寬鬆 | COVID |
| 2021-2024 | 3% | 穩健 | 實際均值 0.8% |
| **2025-2026** | **2%** | **適度寬鬆**（GFC 以來首次）| 通縮 + 房市去槓桿 |

### 歷史視角歸納（CN）

1. **CPI 目標不是靜態 3%**。2004-2024 「3% 左右」，但 2008/2011/2012 曾
   4%、2020 為 3.5%。**2025 下調至 2% 是根本變化** — 從「防過熱 ceiling」
   轉「促回升 中樞」。初稿「3% 為 ceiling」假設已**完全失效**
2. **PBOC 2024 利率走廊改革完成**：7 天逆回購取代 MLF 為主政策利率。
   分析「制約性」必須以 **7D OMO (1.40%)** 為基準，MLF 已退
3. **「適度寬鬆」是 GFC 以來首次回歸**（2010 以來首次）。語言階梯有明確
   等級含意，必須讀原文（英文翻譯 "moderately loose" vs "accommodative"
   差異）
4. **CSI300 結構 2016→2025 質變**：金融 35%→23%、IT 9%→20%。把 CSI300
   當「銀行+SOE 寬基」會錯失 AI/新能源訊號
5. **青年失業率方法論斷裂**：2018-2023（含在校生）vs 2024-（不含在校生）
   不可直接比較。2023-06 峰 21.3% vs 2025-08 18.9% **不同口徑**

### CN 主要 sources

- [2025 政府工作報告（人民網 解讀）](http://lianghui.people.com.cn/2025/n1/2025/0310/c460142-40435010.html) — CPI 目標 **2% 左右**
- [2026 政府工作報告（新華網）](https://www.news.cn/politics/20260305/e5c6a09cba0f445b9ee6cc6f8973132a/c.html)
- [PBOC 2026-Q1 第 112 次例會 (2026-03-31)](https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/2026033115531475919/index.html)
- [NBS 王萍萍 2026-01-19《2025 就業形勢》](https://www.stats.gov.cn/sj/sjjd/202601/t20260119_1962339.html)
- [NBS 董莉娟 2026-04-10《2026-03 CPI 解讀》](https://www.stats.gov.cn/sj/zxfbhjd/202604/t20260410_1963265.html)
- [Rees & Sun (2021) BIS WP No 949 (PDF)](https://www.bis.org/publ/work949.pdf) — r\* Bayesian 估計
- [Rogoff (2024-12) IMF F&D](https://www.imf.org/zh/publications/fandd/issues/2024/12/chinas-real-estate-challenge-kenneth-rogoff) — 房地產 23.6%/31% GDP
- [上海金融委 2026-01 LPR](https://jrj.sh.gov.cn/SCGK194/20260120/75fac71eb01543ce96886e93f366f362.html) — 1Y 3.0% / 5Y 3.5%
- [人行公告〔2019〕第 15 號 LPR 改革](https://www.gov.cn/guowuyuan/2019-08/18/content_5422053.htm)

---

## 跨國 Grounding 原則（適用於所有 5 國）

### 1. Primary source = 該國官方原典 + 母語

| 國家 | 優先語言 | 核心權威 |
|------|----------|----------|
| US | English | Fed / CBO / NY Fed / Richmond Fed |
| JP | 日本語 | BOJ (WP/Review/展望) / JILPT / 統計局 |
| TW | 繁體中文 | CBC / NDC / DGBAS / TWSE |
| KR | 한국어 | BOK / KOSTAT / KDI / KRX |
| CN | 簡體中文 | PBOC / NBS / 國務院 / 中證指數 |

**英語二次報導 / sell-side 摘要不能替代** primary source 做載重性 claim。

### 2. 跨國不可機械類比

從這次 grounding 學到的**最重要教訓**：

- **Fed r\*（0.75%）≠ JP r\*（-0.25% mean）≠ CN r\*（2-3% real）**。
  把 Fed 框架套在日本會永遠判「極度緊縮」；套在中國會永遠判「極度寬鬆」
- **Fed 2% target ≠ BOJ 2%（達成後狀態）≠ PBOC 2%（首次下調、促回升中樞）≠
  CBC「彈性」（無明確數值）**。context 天差地別
- **US NAIRU 4.4% ≠ JP NAIRU 2.8% ≠ KR NAIRU 3.0-3.5%**。台灣沒有
  官方 NAIRU
- **US CSI300-equivalent（S&P）=  Mag-7 33% ≠ KR KOSPI Samsung+SK 40% ≠
  TW TAIEX TSMC 44%**。集中度對 regime 訊號解讀影響巨大

### 3. Recalibration 頻率

threshold 檔案**不是一次寫好永久使用**。主要 recalibration triggers：

- **季度**：FOMC SEP、BOJ 展望、BOK 통화정책방향、CBC 理監事、PBOC 例會
- **年度**：CBO Outlook、政府工作報告、중앙 경제공작 회의、국발회 景氣燈號修訂檢視
- **政策 regime 轉換**：ZLB 進出、YCC 啟動/結束、FAIT→FIT、目標值變化

詳見 `references/recalibration-protocol.md`。

### 4. 不確定性 Provenance

當多個原典推計**衝突**（例：US HLW 0.75% vs LM 1.68%；JP r\* range vs mean）：
- 不要任意挑一個
- 在 threshold 檔記錄**兩者**，並拉出**涵蓋兩者的 band**
- 在 grounding 註記「分歧仍在爭論」
- 下次 recalibration 時重訪 — 2-3 年新 data 可能澄清

### 5. Fabrication 風險警告

這次 grounding 發現的**虛假引用案例**：
- JP -0.386% 10Y real yield（引用伊藤忠コラム但本文不含）→ **刪除**
- US HLW 1.42%（引用 NY Fed 但實際是 LW-closure 或混淆）→ **修正為 0.75%**
- CN BIS WP 949 被誤報「無 r\* 估計」→ **補齊 2-3% real**

→ **primary-source 檢索的標準應該是：「原典 PDF/HTML 要能 WebFetch 並驗證該數字的文字出現」**，而不是「search snippet 提及該來源」

---

## JP integration decision（domain-teams 慣例項）

本 repo 已有「日本語整合」的先例（qa-team / docs-team 等）。本次 grounding 的
日本語整合判斷：

> **全面整合 (Full integration)**
>
> 證據：
> - BOJ 20 年 r\* 研究系列（WP03 → lab18 → WP24 → rev26）是日本特化，
>   英語翻譯版缺或滯後
> - JILPT 均衡失業率覆蓋日本獨特勞動市場特性，無英語代替
> - BOJ 展望 9 人政策委員中央值分佈優於 IMF/OECD 外部
> - 日本為 G7 最低 r\*（唯一範圍含負）— 誤套英語圈參數致命

**操作規則**：thresholds-japan.md 所有核心數值 MUST 從 BOJ 日本語原典導出，
英語 cross-check 僅作 tertiary 驗證。

---

## 誤診影響評估

若不做此次 grounding，**thresholds-*.md 會在實際 regime call 中產生
下列錯誤**：

1. **US**: 用 HLW 1.42% + LM 2.15% 校準 1.75% "Clearly Restrictive"；
   實際 HLW 0.75% + LM 1.68% 平均（~1.2%） + 50 bp term premium ≈ 1.7%，
   所以 1.75% 門檻仍 **大致合理**。但 FAIT→FIT 轉換讓 inflation 解釋
   方式不同
2. **JP**: 用錯誤 NAIRU 3.5% 會把當前 unemp 2.6% 判「~1 pp 低 → 極度
   Tight」，**實際僅 -0.2 pp**「軽度 Tight」。政策利率 0.5% 誤判會讓
   利率中立性判斷整個錯位
3. **TW**: 把 9 指標中「工業及服務業加班工時」換成「非農業就業」讓
   構成信號完全錯 → regime call 追蹤的是錯指標。TSMC 40% vs 44%
   讓集中風險警戒低估 4 pp
4. **KR**: NAIRU 1998-2000 vs 1998-2004 小差異可忽略；但**KOSPI 集中度
   30% vs 40% 是 1/3 誤差**，讓 semi-cycle 主導性大幅低估。105% vs
   90% 家庭負債讓 BOK 鷹派-鴿派判斷錯向
5. **CN**: **全份 "3% ceiling" 假設作廢** — 新目標 2% 讓 disinflation
   信號門檻重定位。MLF 不再是政策利率讓分析框架結構性錯誤

---

## 後續動作

本 grounding note 完成之後：

1. **5 個 thresholds-\*.md 套用修正** —— 每個檔案頭部加 Grounding Status
   block，body 套用 paste-ready 修正字串，底部更新 Sources
2. **SKILL.md 更新**：Step 1 Threshold reference 欄補註 grounding-v1.9.0.md
3. **ROADMAP.md**：v1.9.0 entry 加「Grounding audit」段落
4. **Recalibration protocol 已先寫**（獨立於本 note，見
   `references/recalibration-protocol.md`）

---

## Appendix — 各國 agent 執行統計

| Agent | Tokens | Tool uses | Duration | Critical errors found |
|-------|--------|-----------|----------|-----------------------|
| grounding-us | 90,760 | 48 | 6:07 min | 3 🔴 + 2 ⚠️ |
| grounding-japan | 69,586 | 30 | 5:41 min | 4 🔴 + 2 ⚠️ |
| grounding-taiwan | 83,211 | 48 | 5:44 min | 3 🔴 + 3 ⚠️ |
| grounding-korea | 74,645 | 31 | 6:05 min | 4 🔴 + 5 ⚠️ |
| grounding-china | 89,356 | 44 | 6:30 min | 5 🔴 + 4 ⚠️ |
| **Total** | **~407k** | **201** | **~30 min parallel** | **19 🔴 + 16 ⚠️** |

5 並行執行 ~6.5 分（非 sequential 的 30+ 分），節省 ~25 分鐘壁上時間。
405k tokens 投入產生 35 個具體修正 → **~12k tokens per correction**，
是可接受的 grounding 投入比。
