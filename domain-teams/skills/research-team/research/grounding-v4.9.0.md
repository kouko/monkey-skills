---
title: research-team 再設計研究 — 学術リテラシー / 主要文献 / OSS評価 / JP情報リテラシー
date: 2026-04-11
team: research-team
refactor_version: v4.9.0
tags: [research, domain-teams, research-team, grounding]
---

# research-team 再設計研究

> [!info] 研究背景
> 為 research-team v4.9.0 重構執行 Phase 2 grounding research。Phase 1 gap
> assessment 發現 research-team 是目前 7 個 domain-teams 中 **最嚴重未 grounded**
> 的 skill — 13 個檔案（1042 行）**零 primary-source citation**。與其他已 grounded
> team（qa v4.2 / docs v4.3 / devops v4.4 / code v4.6 / design v4.8）形成明顯反差。
>
> Phase 1 另外發現 3 處結構 drift：
> 1. MAY Gates table 僅 2 欄（`Gate | File`），缺 `Trigger` 欄
> 2. `### Behavioral Rules` 與 `### Agents` 誤嵌套於 `## Resource Manifest` 之下
> 3. 每個 standards 檔案皆無 `## Primary Sources` 段
>
> 研究方法：parallel EN + JP web search，逐項驗證候選一手來源，章節 / 版本 /
> URL 經 WebSearch 驗證。未能獨立驗證者明確標記。本 Phase 2 的任務是：
> (a) 確認候選主文獻存在且年份 / 版本正確
> (b) 確認文獻實際包含我們預期的 load-bearing claim
> (c) 決定 JP 整合策略（full / preamble / none）
> (d) 產出 5-7 份 standards 檔案的 draft plan 給 Phase 4

## TL;DR

| Point | Status |
|-------|--------|
| **Booth / Colomb / Williams / Bizup / FitzGerald《The Craft of Research》5th ed** (University of Chicago Press, **2024-06-25**) — 2024 新版取代 Phase 1 預設的 4th ed; 2024 版新增 generative AI 章節 + presentations 章節 | `[事實\|高]` ⚠️ 使用 5th ed 非 4th ed |
| **Wayne C. Booth et al. 3-step argument structure** (Claim / Reason / Evidence / Warrant / Acknowledgment / Response) — 第 5 章（Acknowledging Audiences）至第 10 章（Warranting Your Argument）貫穿本書，是 research-team 論證 scaffolding 的 canonical anchor | `[事實\|高]` |
| **Cochrane Handbook for Systematic Reviews of Interventions v6.5** (Higgins, Thomas, Chandler, Cumpston, Li, Page, Welch eds., **updated 2024-08**) — 最新版; Cochrane 的 systematic review 流程（research question → protocol → search → appraisal → synthesis）是 academic-research protocol 的 grounding anchor | `[事實\|高]` |
| **Page, McKenzie, Bossuyt, et al. PRISMA 2020 Statement** (*BMJ* 2021;372:n71) — **27-item checklist + 7 sections + abstract checklist + revised flow diagram**。取代 2009 版，是 reporting systematic reviews 的 reference standard | `[事實\|高]` |
| **IPCC AR5/AR6 Guidance Note on Consistent Treatment of Uncertainties** (Mastrandrea et al., **2010**, applied AR5 2013-2014 → AR6 2021-2023) — **confidence 5 級 (very low / low / medium / high / very high)** + evidence (limited / medium / robust) + agreement (low / medium / high) 正交式 framework。research-team 的 高/中/低 confidence tag 應 ground 在這個 scale | `[事實\|高]` |
| **Sherman Kent (1964) "Words of Estimative Probability"** (*Studies in Intelligence*, CIA, republished openly on cia.gov) — 情報分析 WEP 起源; "poets vs mathematicians" distinction; Kent 主張把語言化的可能性對應到數值 odds | `[事實\|高]` |
| **Philip E. Tetlock & Dan Gardner (2015)《Superforecasting: The Art and Science of Prediction》** (Crown / Random House) — 校準（calibration）vs 解析度（resolution）兩軸，擴充 Kent 的 7-point verbal scale 到 0-1 probability 連續尺度；Good Judgment Project 是 empirical backing | `[事實\|高]` |
| **PRIMARY / SECONDARY / TERTIARY source definition** — source 的分類隨學科變化：歷史學 = 原始文件 / 工藝品；科學 = 原始研究數據集；藝術人文 = 原創作品。並非屬性而是「如何被使用」 — JMU / Cornell / UC Merced / Ohio State 等 academic libraries 均採用此共同 framework | `[事實\|高]` |
| **Porter (2008) "The Five Competitive Forces That Shape Strategy"** (*HBR* Jan 2008, vol 86 no 1) — 取代 1979 版 "How Competitive Forces Shape Strategy" 的 Porter 自己重寫版。包含 5 forces 的更新應用指引。Porter (1980)《Competitive Strategy》Free Press (978-0684841489) 是書籍 canonical primary。research-team 競爭分析應 cite **1980 書 + 2008 HBR update**，而非使用 implicit "Porter-style" 表述 | `[事實\|高]` ⚠️ 重要補 attribution |
| **Kim & Mauborgne (2005 / 2015 expanded)《Blue Ocean Strategy》** (Harvard Business Review Press, expanded ed 2015) — 4 Actions Framework (Eliminate / Reduce / Raise / Create); Strategy Canvas。research-team 目前無任何 market/competitive protocol cite 這個 framework 但 implicit 引用了「未被滿足的市場空間」概念 | `[事實\|高]` ⚠️ 重要補 attribution |
| **Damodaran (2012)《Investment Valuation》3rd ed** (Wiley Finance, 978-1118011522) + Damodaran (2018)《The Dark Side of Valuation》3rd ed (Pearson FT Press, 978-0134854106) — valuation 的 canonical primary。Damodaran 在 NYU Stern 提供開放教材（pages.stern.nyu.edu/~adamodar/）是少數 freely accessible 的 investment textbook | `[事實\|高]` |
| **Graham & Dodd (1934 / 2008 6th ed)《Security Analysis》** (McGraw-Hill 6th ed, foreword by Warren Buffett, 978-0071592536) — value investing canonical primary; research-team 目前 protocols/investment.md 完全無 cite | `[事實\|高]` |
| **Merrill Lynch (Greetham & Hartnett, 2004) "The Investment Clock"** (Merrill Lynch Global Asset Allocation report, 2004-11-10) — 4-phase macro regime model: Reflation / Recovery / Overheat / Stagflation，對應 Bonds / Stocks / Commodities / Cash。research-team 目前 protocols/investment.md L15 寫「expansion/slowdown/contraction/recovery」是 implicit 引用 Investment Clock 但 ungrounded | `[事實\|高]` ⚠️ 重要 attribution 修正（四期 naming 要對齊 Greetham 原文）|
| **Osterwalder & Pigneur (2010)《Business Model Generation》** (Wiley, 978-0470876411) — Business Model Canvas 9 blocks (CS / VP / CH / CR / RS / KR / KA / KP / C$)。research-team 目前 無 protocol cite 但 competitive-analysis 應 ground 在這 | `[事實\|高]` |
| **Aaker (1991)《Managing Brand Equity》** (Free Press, 978-0029001011) — 5 dimensions (brand loyalty / name awareness / perceived quality / brand associations / other proprietary assets)。品牌分析 canonical primary | `[事實\|高]` |
| **OpenSSF Scorecard** (scorecard.dev) — **18 checks across 3 themes**（Holistic Security / Source Code Risk / Build Process Risk）+ 0-10 scoring per check。research-team 目前 oss-safety.md 完全沒有 cite | `[事實\|高]` |
| **NIST SSDF SP 800-218 v1.1** (**2022-02 released**) — 4 practice groups (Prepare / Protect / Produce / Respond)。SP 800-218 Rev 1 (v1.2) 為 draft 狀態。**research-team 應 cite v1.1 作為 stable reference**，並附注 v1.2 為 draft | `[事實\|高]` |
| **SLSA v1.1** (slsa.dev, current as of 2026-04) — 4 levels L0-L3 (L0 no provenance → L3 forge-resistant)。Supply chain integrity canonical framework。research-team 目前 oss-safety.md 沒有引用 | `[事實\|高]` |
| **CVSS v4.0** (FIRST.org, **released 2023-11-01**) — 4 metric groups (Base / Threat / Environmental / Supplemental), 取代 v3.1 的 3-group model。Base score 是唯一 mandatory; 其他 optional。research-team oss-safety.md L24「No unpatched critical/high CVEs」是 implicit CVSS 表述但 ungrounded | `[事實\|高]` ⚠️ 應 cite CVSS v4.0 |
| **SPDX 3.0** (spdx.dev, **released 2024-04**) — ISO/IEC 5962:2021 原本 register 的是 SPDX 2.2.1，**v3.0 尚未 re-register**。v3.0.1 為 2025-08 current patch。research-team oss-safety.md L8 license list 是 implicit SPDX identifier 但未 cite | `[事實\|高]` |
| **CHAOSS Project** (chaoss.community, Linux Foundation project) — implementation-agnostic metrics for OSS community health; 多個 working groups (DEI / Evolution / Risk / Common Metrics / Value 等); GrimoireLab + Augur 兩套工具。research-team 目前 stack-evaluation.md 使用自創 threshold（>500 issues、>12 months 等）而未 cite CHAOSS metrics 框架 | `[事實\|高]` ⚠️ research-team 閾值需對齊 CHAOSS 或明確標為自創 |
| **OSI (Open Source Initiative) OSI-Approved Licenses List** (opensource.org/licenses) — 官方維護的 OSD-compliant 授權清單。是 SPDX license list 的 authoritative source | `[事實\|高]` |
| **ACRL Framework for Information Literacy for Higher Education** (**2016-01 filed, 2016-06 rescinded 2000 Standards; current framework approved 2016**) — **6 frames**: Authority Is Constructed and Contextual / Information Creation as a Process / Information Has Value / Research as Inquiry / Scholarship as Conversation / Searching as Strategic Exploration。資訊素養 higher education 的 canonical framework | `[事實\|高]` |
| **Society of Professional Journalists Code of Ethics** (spj.org/ethics, **2014-09-06 last revised**) — 4 pillars: Seek Truth and Report It / Minimize Harm / Act Independently / Be Accountable and Transparent。加上 digital era 對 hyperlinks 作為 attribution 的明文承認 | `[事實\|高]` |
| **Kovach & Rosenstiel (2021)《The Elements of Journalism》4th ed** (Crown, 978-0593239353) — 10 elements of journalism（Discipline of Verification 為核心）。journalism sourcing canonical primary | `[事實\|高]` |
| **AP Stylebook** (apstylebook.com, 年度更新) — attribution 與 sourcing 的 operational style guide。research-team 的 "according to" attribution format 應對齊 AP Stylebook 慣例 | `[事實\|中]` |
| **APA Publication Manual 7th ed** (APA 2020, 978-1433832178) — author-date in-text citation; et al. 用於 3+ authors。research-team protocols/academic-research.md L85 寫「APA format preferred」但未 cite 版本 | `[事實\|高]` ⚠️ 應明示 APA 7th (2020) |
| **Chicago Manual of Style 18th ed** (University of Chicago Press, **2024-09 released**) — 取代 17th ed (2017)。Author-Date + Notes-Bibliography 雙 system。**18th ed 廢除 place of publication requirement + inclusive page numbers for chapters**。research-team 目前無引用但 craft of research 的雙胞胎 | `[事實\|高]` ⚠️ 使用 18th ed 非 17th |
| **IEEE Reference Style Guide** (ieeeauthorcenter.ieee.org) — numeric [1] bracketed citation; journal article 格式 `[#] Author, "Title," Abbrev. Journal, vol, no, pp, month year`。工科論文 canonical | `[事實\|高]` |
| **JP — 倉田敬子 (2007)《学術情報流通とオープンアクセス》** 勁草書房 (4326000325) — 2008 年獲第 37 回 **日本図書館情報学会賞**。Keio 大學文學部教授。學術資訊流通的 JP primary | `[事實\|高]` |
| **JP — 国立国会図書館 リサーチ・ナビ** (ndlsearch.ndl.go.jp/rnavi, **launched 2009-05-11**) — 國立國會圖書館職員編纂的テーマ別 / 資料群別「調べ方案内」; 含一次資料 (primary source) / 二次資料 (secondary source) / 三次資料 (tertiary source) 的 JP-community 分類 | `[事實\|高]` |
| **JP — SIST 02-2007 参照文献の書き方** (科学技術振興機構 JST, 2007-03 published, **2012-03 事業終了**) — JP 科學技術論文 citation 標準。**事業已於 2012 年終了**，但多數 JP 學術期刊仍採用這個規範作為 de facto standard。WARP (NDL web archive) 保存完整 PDF | `[事實\|高]` ⚠️ 須加「已廢止但仍廣泛使用」的 caveat |
| **JP — 国立情報学研究所 CiNii Research** (cir.nii.ac.jp, 2022 整合 CiNii Articles / Books / Dissertations) — JP 最大學術資訊搜索服務，含研究論文 / 書籍 / 研究資料 / 研究者 / 研究案等。research-team 目前 academic-research.md L17 已 cite CiNii（但 URL 過時）| `[事實\|高]` |
| **JP 整合決定**: **PREAMBLE** — JP 有 NDL リサーチ・ナビ + 倉田敬子 + SIST 02 + CiNii 作為 information literacy 四柱，但這四柱 **不構成獨立方法論框架**（沒有 JP 版的 Cochrane/PRISMA/Booth/Craft of Research）。JP 對應的是「學術資訊基礎建設」(infrastructure) 而非「research methodology framework」。因此 preamble 級整合 — citation-standards 加 NDL / 倉田錨點，academic-research protocol 加 CiNii / J-Stage / NDL 的 JP database instructions，但主框架仍是 Booth / Cochrane / PRISMA | `[分析\|高]` |
| **反模式清理**: research-team 目前全文無一條 primary-source citation，反模式較少。但有 3 處 implicit framing 需補 attribution：(1) investment.md 4-phase regime 是 implicit Investment Clock; (2) research.md 的 6-month freshness threshold 是自創（IPCC/PRISMA 沒有這個 hard threshold）; (3) stack-evaluation.md 的 >500 issues / >12 months 等閾值是自創而非 CHAOSS 引用 | `[行動\|高]` |

---

# Research Questions Status

Phase 1 提出的 10 個 Q-* 研究問題，Phase 2 驗證結果：

| # | Question | Status | Key sources verified |
|---|---|---|---|
| Q-Primary-Source-Definition | canonical scholarly definition of primary/secondary/tertiary | ✓ verified | JMU / Cornell / UC Merced / Ohio State library guides + NDL リサーチ・ナビ JP 版 |
| Q-Confidence-Language | ground 高/中/低 in IPCC / Tetlock / Kent CIA | ✓ verified | IPCC AR5 Guidance Note (Mastrandrea et al. 2010); Kent 1964 Studies in Intelligence; Tetlock 2015 Superforecasting |
| Q-Systematic-Review-Standards | Cochrane / PRISMA / PRISMA-ScR | ✓ verified | Cochrane Handbook v6.5 (2024-08); PRISMA 2020 Statement (Page et al. BMJ 2021;372:n71, 27-item checklist) |
| Q-Booth-Argument | The Craft of Research, edition check | ✓ verified (5th ed, NOT 4th) | Booth/Colomb/Williams/Bizup/FitzGerald 5th ed (U Chicago Press 2024-06-25, 978-0226826677) |
| Q-Strategic-Frameworks-Canon | Porter / Blue Ocean / Osterwalder / Aaker | ✓ verified | Porter 1980 Competitive Strategy Free Press; Porter 2008 HBR; Kim & Mauborgne 2005/2015 HBR Press; Osterwalder 2010 Wiley; Aaker 1991 Free Press |
| Q-Investment-Analysis-Canon | Graham&Dodd / Damodaran / Merrill Lynch Investment Clock | ✓ verified | Graham & Dodd 2008 6th ed McGraw-Hill; Damodaran 2012 Investment Valuation 3rd ed Wiley; Greetham & Hartnett 2004 Merrill Lynch Investment Clock report |
| Q-OSS-Evaluation-Frameworks | OpenSSF / CHAOSS / OSI / SPDX / NIST SSDF / SLSA / CVSS | ✓ verified | OpenSSF Scorecard 18 checks; CHAOSS (LF project); OSI approved licenses; SPDX 3.0 (2024-04); NIST SP 800-218 v1.1 (2022-02); SLSA v1.1; CVSS v4.0 (2023-11) |
| Q-Journalism-Sourcing | SPJ / AP / ONA / Kovach&Rosenstiel | ✓ verified | SPJ Code 2014-09 revision; AP Stylebook current; ONA ethics code framework; Kovach & Rosenstiel 4th ed 2021 Crown |
| Q-JP-Information-Literacy-Canon | NDL / NII / 日本図書館情報学会 / SIST 02 / 倉田敬子 / 古賀崇 | 🟡 partial | 倉田 ✓; NDL リサーチ・ナビ ✓; SIST 02 ✓ (but 2012 discontinued); CiNii/NII ✓; 古賀崇 存在驗證但未找到 information literacy 一手專著; 日本図書館情報学会誌 有情報リテラシー研究論文但非 centralized framework |
| Q-Citation-Format-Manuals | APA 7th / Chicago 17th / SIST 02 / IEEE / Turabian | ✓ verified (Chicago 18th, NOT 17th) | APA 7th ed (2020); **Chicago 18th ed (2024-09, NOT 17th)**; SIST 02-2007; IEEE Reference Style Guide; Turabian 9th ed (2018) |

**Unverified / deferred**:
- 古賀崇 的 information literacy 單獨專著 — 雖然研究者存在且在天理大學活躍，但檢索到的主要是合著論文、事典章節、會議發表，無獨立一手專著。建議在 standards 裡改 cite 日本図書館情報学会誌上的代表性 review article (野末俊比古 CA1703「研究文獻レビュー：情報リテラシー教育」current.ndl.go.jp/ca1703) 作為 JP information literacy research trend 的 anchor。

---

# Cluster A — Primary Source Definition

## Q1. Primary / Secondary / Tertiary source taxonomy

### 書誌（已驗證 via multi-library cross-check）

- **Primary**: 原始證據 / 第一手資料，創作者親自撰寫 / 記錄 / 產生
  - 歷史學：日記、信件、演講稿、歷史文件、工藝品、訪談、原始報紙報導
  - 科學：原始研究論文 (peer-reviewed article with Methods + Results + Discussion)，會議論文，研究資料集
  - 藝術人文：原創藝術作品、文學原文、音樂樂譜、電影原片
- **Secondary**: 對 primary source 的分析、詮釋、重組
  - 教科書、綜述論文 (review articles)、學術專書、傳記、歷史分析專書
- **Tertiary**: 對 primary + secondary 的摘要或編纂
  - 百科全書、詞典、索引 / 目錄、手冊、事典

### 核心認知

> Source 的「primary / secondary / tertiary」分類不是固有屬性，而是**使用方式**決定的。
> 一份教科書本身是 secondary source，但若你研究的是「某教科書的內容如何演變」，
> 那該教科書對你而言就成為 primary source。
> — 見 JMU、UC Merced、Cornell 多家 library guide 共識

### 驗證來源

- **James Madison University Library Guide**: https://guides.lib.jmu.edu/sources
- **University of Minnesota Crookston Library**: https://crk.umn.edu/library/primary-secondary-and-tertiary-sources
- **UC Merced LibGuides**: https://libguides.ucmerced.edu/source-types
- **Ohio State — Choosing & Using Sources (Press book)**: https://ohiostate.pressbooks.pub/choosingsources/chapter/primary-secondary-tertiary-sources/
- **Cornell Library — Primary, Secondary, and Tertiary Sources: A Quick Guide**: https://guides.library.cornell.edu/sources/tertiary

### 對 research-team 的應用

→ 這是 **citation-standards.md** 的核心定義段落。目前 citation-standards.md L11-14
只說「Prefer primary sources: official docs, SEC filings, central bank reports,
peer-reviewed papers」— 範例式列舉而非結構化 taxonomy。應補上 primary/secondary/
tertiary 正式定義（**Tier 1 parametric knowledge** — 大學 library guide 是 LLM
訓練資料中高度飽和的內容）。

---

# Cluster B — Claim Classification & Confidence Language

## Q2. IPCC Calibrated Language (AR5 / AR6 Guidance Note)

### 書誌（已驗證）

- **作者**: Michael D. Mastrandrea et al. (IPCC Working Group I, II, III co-chairs)
- **標題**: *Guidance Note for Lead Authors of the IPCC Fifth Assessment Report on Consistent Treatment of Uncertainties*
- **年份**: 2010-07 (applied to AR5 2013-2014, continued to AR6 2021-2023)
- **發行**: IPCC Secretariat
- **canonical URL**: https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf
- **驗證來源**: ipcc.ch 官方 PDF + springer.com/article/10.1007/s10584-011-0178-6 (AR5 guidance note 描述論文)

### The Confidence Scale (5 levels)

| Level | Label | 定義 |
|---|---|---|
| 1 | **Very low** | Evidence limited AND agreement low |
| 2 | **Low** | Evidence limited, agreement mixed |
| 3 | **Medium** | Medium evidence + medium agreement |
| 4 | **High** | Robust evidence + high agreement |
| 5 | **Very high** | 同 High 但更強 |

### The Evidence × Agreement 正交格

IPCC 不只有一個 1D scale。Confidence 是 **兩個正交維度的 derived metric**:

|  | Agreement: Low | Agreement: Medium | Agreement: High |
|---|---|---|---|
| **Evidence: Robust** | Medium | High | Very High |
| **Evidence: Medium** | Low | Medium | High |
| **Evidence: Limited** | Very Low | Low | Medium |

### The Likelihood Scale（正交於 confidence）

| 機率範圍 | Likelihood 詞 |
|---|---|
| 99-100% | **Virtually certain** |
| 90-100% | **Very likely** |
| 66-100% | **Likely** |
| 33-66% | **About as likely as not** |
| 0-33% | **Unlikely** |
| 0-10% | **Very unlikely** |
| 0-1% | **Exceptionally unlikely** |

### 對 research-team 的應用

research-team 目前 citation-standards.md L27-31 的「高/中/低」3-tier
confidence scale 是 **未 ground 的簡化版**。建議：

1. **保留 3-tier 簡化** — IPCC 的 5-tier 對輕量 research task 太繁瑣
2. **Ground on IPCC** — 在 citation-standards 加一句「Confidence level 3-tier
   scheme is a simplified version of IPCC AR5 Guidance Note (Mastrandrea et al.
   2010) 5-level confidence scale」
3. **清楚區分 confidence vs likelihood** — 目前 research-team 把兩者混在一起。
   IPCC 明確區分：confidence 是 meta-level（對 claim 本身的把握度），likelihood
   是 object-level（某事件發生的機率）。research-team 應在 protocol 裡強制區分

**Tier**: 這是 **Tier 2** — LLM cold-query 能說出 IPCC 有 calibrated language 但
常把 confidence 5 級和 likelihood 7 級搞混，需要 body spell out。

---

## Q3. Sherman Kent (1964) Words of Estimative Probability

### 書誌（已驗證）

- **作者**: Sherman Kent (時任 CIA Office of National Estimates 主任)
- **標題**: "Words of Estimative Probability"
- **年份**: 1964 年（原文）; **正式 declassified & republished 2007**
- **發行**: *Studies in Intelligence*, CIA Center for the Study of Intelligence
- **canonical URL**: https://www.cia.gov/resources/csi/studies-in-intelligence/archives/vol-8-no-4/words-of-estimative-probability/
- **PDF archive**: https://www.cia.gov/readingroom/docs/CIA-RDP93T01132R000100020036-3.pdf

### 核心主張

- 情報分析師使用「probable」「likely」「may」等詞而沒有對應到數值機率 → 讀者
  會做不同解讀 → 決策失誤
- 提出 **numerical odds 對應表**（原文 Table）將語言表述映射到數值區間
- 區分 **"poets"（偏好語言化表述者）** vs **"mathematicians"（偏好量化表述者）**
  — 兩派在情報社群的對立
- Kent 的提案當時沒有被採用，但奠定了後續 NIC/IC 的 estimative probability
  discipline 傳統

### 後續發展

- **NIC Estimative Probability 7-point verbal scale** — 現代 IC 標準，對應 Kent
  的 table 但更精細
- **Tetlock Superforecasting** — 把 Kent 的 scale 從 7-point 擴充到 0-1 連續尺度
  基於 Good Judgment Project 的實證校準
- **IPCC likelihood 7-tier scale** — 獨立於 Kent 發展出的環境科學版本，結構
  相似（中央 "about as likely as not" 50% + 兩側對稱）

### 驗證來源

- **CIA.gov CSI article**: https://www.cia.gov/resources/csi/studies-in-intelligence/archives/vol-8-no-4/words-of-estimative-probability/
- **Wikipedia WEP article**: https://en.wikipedia.org/wiki/Words_of_estimative_probability（指向 CIA 官方）
- **Kesselman 2008 "Verbal Probability Expressions in National Intelligence Estimates"**: https://gwern.net/doc/statistics/bayes/2008-kesselman.pdf

### 對 research-team 的應用

research-team 目前 citation-standards.md 的「高/中/低」hedging discipline 沒有
歷史根源。加 Kent 1964 作為 anchor，說明「為什麼要強制 confidence tag」。

**Tier**: **Tier 2** — LLM cold-query 知道 Kent 1964 的存在和主題但常常把
"poets vs mathematicians" 歸錯、把 7-point scale 的具體對應弄錯。body 需要
spell out 核心主張。

---

## Q4. Tetlock Superforecasting

### 書誌（已驗證）

- **作者**: Philip E. Tetlock & Dan Gardner
- **標題**: *Superforecasting: The Art and Science of Prediction*
- **出版**: Crown Publishers / Random House, 2015-09-29
- **ISBN-13**: 978-0804136693
- **驗證來源**: Amazon, Penguin Random House, Good Judgment Project 頁面

### 核心概念

1. **Calibration + Resolution 雙軸**:
   - **Calibration**: 「我說 70% → 該事件應該 70% 發生」的對應度（meteorologist
     model）
   - **Resolution**: 「不只說 50%」的 decisiveness — 能把預測推離中間值的能力
2. **Brier score** 是衡量 calibration × resolution 的 composite metric
3. Tetlock 在 Good Judgment Project 中發現 top 2% forecasters（superforecasters）
   能持續 outperform CIA intelligence analysts with classified data
4. 反 "hedgehog" 傾向：superforecasters 是 "foxes" — 多理論雜食，抗 overcommitment
5. 學習循環：**預測 → 真實結果 → 計分 → 更新 → 再預測**，需時間尺度與 feedback loop

### 對 research-team 的應用

- citation-standards 的 confidence tagging 可以 cite Tetlock：「confidence tag 是
  calibration 的 externalization；高/中/低 是向 Brier-style 校準邁進的第一步」
- 在 quality rubric 加一個「calibration discipline」子項（是否在過往研究中使用
  confidence tag、事後是否檢視 calibration）

**Tier**: **Tier 1** — Tetlock Superforecasting 是暢銷書 + Good Judgment Project
是 Bridgewater / Long Now 等 high-profile 引用，LLM parametric knowledge 充足。

---

# Cluster C — Research Process (Booth / Cochrane / PRISMA)

## Q5. Booth Colomb Williams — The Craft of Research, 5th ed (2024)

### 書誌（已驗證）

- **作者**: Wayne C. Booth, Gregory G. Colomb, Joseph M. Williams, Joseph Bizup, William T. FitzGerald
- **標題**: *The Craft of Research*
- **版次**: **Fifth Edition** — ⚠️ Phase 1 預設 4th ed 是**錯誤**，2024-06-25 發行第 5 版
- **出版**: University of Chicago Press (Chicago Guides to Writing, Editing, and Publishing series)
- **年份**: 2024-06-25
- **ISBN-13**: 978-0226826677 (paperback) / 978-0226833880 (hardcover)
- **銷售**: 前 4 版累積超過 1 百萬冊
- **驗證來源**: University of Chicago Press 官方頁 https://press.uchicago.edu/ucp/books/book/chicago/C/bo215874008.html; Amazon; Google Books

### 5th edition 新增內容

- **新增 generative AI 使用 guideline** 章節（2024 年重大 update）
- **新增 presentations 章節**
- **擴充 ethics 章節**
- 由 Joseph Bizup + William T. FitzGerald 全面修訂（Wayne Booth 2005 逝世;
  Gregory Colomb 2011 逝世; Joseph Williams 2008 逝世 — 3 位原作者皆已過世，
  後續版本由 Bizup + FitzGerald 接續）

### 核心 framework（跨 5 版穩定）

**4 Parts + 17 chapters**（已驗證 from Google Books TOC）:

| Part | 章節範圍 | 主題 |
|---|---|---|
| **I. Research, Researchers, and Readers** | Ch.1-3 | Thinking in print, connecting with your reader, from topics to questions |
| **II. Asking Questions, Finding Answers** | Ch.4-7 | From questions to problems, from problems to sources, engaging sources, planning your argument |
| **III. Making a Claim and Supporting It** | Ch.8-12 | Making good arguments, claims, reasons & evidence, acknowledgments & responses, warrants |
| **IV. Writing Your Argument** | Ch.13-17 | Planning a first draft, drafting, revising, communicating with presentations (NEW 5th ed), introductions and conclusions |

### Booth 的 Argument Structure（5-element model）

Ch.7-12 貫穿的 argument model:

| Element | 問法 |
|---|---|
| **Claim** | 你主張什麼？ |
| **Reason** | 為什麼該主張是對的？ |
| **Evidence** | Reason 基於什麼證據？ |
| **Warrant** | Evidence 與 Claim 之間的連結是什麼 general principle? |
| **Acknowledgment + Response** | 反對意見是什麼？你怎麼回應？ |

→ 這是 research-team 的 **論證 scaffolding 核心**。目前 research.md L35-41 的
fact/analysis/speculation tag 是同構於 Booth 的 Claim/Reason/Evidence 但沒有
cite。

### 對 research-team 的應用

- **citation-standards.md** 加 Booth 5th ed 作為 top-level primary source anchor
- **research-brainstorming.md** 加 Ch.3-4「from topics to questions」作為 framing
- **research.md** 加 Ch.7-12 的 argument 5-element 作為 output structure
- **academic-research.md** 加 Ch.5「from problems to sources」作為 literature
  map scaffolding

**Tier**: **Tier 1** — Craft of Research 是 U Chicago Press 前 4 版百萬銷量的
Anglo-American 學術寫作聖經，LLM parametric 充足。**但** 5th ed 的新 chapter
（AI guideline、presentations）是 2024 才出，**可能還沒完全 in LLM training data** —
這個具體點建議升級到 **Tier 2** 處理。

---

## Q6. Cochrane Handbook for Systematic Reviews of Interventions v6.5 (2024)

### 書誌（已驗證）

- **編者**: Higgins JPT, Thomas J, Chandler J, Cumpston M, Li T, Page MJ, Welch VA (eds.)
- **標題**: *Cochrane Handbook for Systematic Reviews of Interventions*
- **版次**: **Version 6.5** — **updated August 2024**（Phase 1 的 v6.5 預設是對的）
- **發行**: Cochrane, www.training.cochrane.org/handbook
- **canonical URL**: https://training.cochrane.org/handbook/current
- **驗證來源**: Cochrane Training 官方頁; Cochrane Methods release announcement; pubmed.ncbi.nlm.nih.gov/31643080/

### 版本演進

- v1.0: 2005
- v5.1.0: 2011（最後 Cochrane Collaboration imprint 版本）
- v6.0: 2019-09（Wiley + Cochrane 合作版）
- v6.4: 2023-08
- **v6.5: 2024-08 (current)** — 更新 Ch.4 technical supplement, Ch.10, Ch.13

### Systematic Review 8-step process（Cochrane framing）

1. **Formulate research question** (PICO: Population / Intervention / Comparator / Outcome)
2. **Write protocol** (PROSPERO pre-registration recommended)
3. **Search for studies** (systematic, reproducible search strategy + PRESS peer review)
4. **Select studies** (screening: title/abstract → full text, dual independent reviewers)
5. **Extract data** (standardized forms, dual extraction recommended)
6. **Assess risk of bias** (RoB 2 tool for RCTs; ROBINS-I for non-randomized)
7. **Synthesize results** (meta-analysis if appropriate; narrative synthesis if not; GRADE certainty assessment)
8. **Report findings** (PRISMA 2020 compliance for the written review)

### 對 research-team 的應用

**academic-research.md** 目前的 3-phase structure（Literature Collection → Analysis
→ Output）是 Cochrane 流程的 **嚴重簡化** — 沒有 protocol pre-registration、沒有
dual-reviewer screening、沒有 risk of bias assessment、沒有 GRADE certainty。

建議：不要強求 academic-research protocol 變成 full Cochrane — research-team 是
general-purpose 不是醫療 meta-analysis team。但 **加一句 reference**：
「For medical / clinical systematic review tasks, follow Cochrane Handbook v6.5
process rather than this general protocol; PRISMA 2020 applies in both cases.」

**Tier**: **Tier 2** — LLM 知道 Cochrane Handbook 存在和大致結構，但 8-step
process 的具體 naming、RoB 2 vs ROBINS-I 的區分、GRADE 的 4-level certainty
（high/moderate/low/very low）會搞混。body 需要 spell out 關鍵 terminology。

---

## Q7. PRISMA 2020 Statement

### 書誌（已驗證）

- **作者**: Page MJ, McKenzie JE, Bossuyt PM, Boutron I, Hoffmann TC, Mulrow CD, Shamseer L, Tetzlaff JM, Akl EA, Brennan SE, et al.
- **標題**: "The PRISMA 2020 statement: an updated guideline for reporting systematic reviews"
- **期刊**: *BMJ* 2021;372:n71
- **年份**: 2021-03-29（published online）
- **DOI**: 10.1136/bmj.n71
- **canonical URL**: https://www.prisma-statement.org/prisma-2020-statement
- **PubMed**: https://pubmed.ncbi.nlm.nih.gov/33782057/

### 內容結構

- **27-item checklist** (up from 2009 version's 27 — same count but 完全 reorganized)
- **7 sections** of the checklist: Title / Abstract / Introduction / Methods / Results / Discussion / Other information
- **Abstract checklist** (12 items, separate from main checklist — NEW in 2020)
- **PRISMA 2020 flow diagram** (revised, includes register/database/other-methods split)
- **Explanation and Elaboration paper** (companion, Page MJ et al. *BMJ* 2021;372:n160) — provides detailed guidance per item

### 取代 2009 版

- PRISMA 2009 Statement (Moher D et al. *BMJ* 2009;339:b2535) 是前版
- 2020 版是自 2009 以來首次大幅更新，reflect 2010 年代 systematic review 方法論
  演進 (e.g., living reviews, scoping reviews 的區分)
- **PRISMA-ScR** (for scoping reviews, Tricco AC et al. *Ann Intern Med* 2018;169:467)
  是 PRISMA 的 variant，不是 2020 的一部分但是相關姊妹標準

### 對 research-team 的應用

PRISMA 2020 是 **systematic review reporting 的 reference standard**。research-team
的 academic-research protocol 可以**不強制**要求 PRISMA compliance（因為不是所有
task 都是 systematic review），但應該：

1. **cite PRISMA 2020 作為 gold standard reference** — 「When producing systematic
   review artifacts, follow PRISMA 2020 (Page et al. BMJ 2021;372:n71)」
2. 在 Source Citation checklist 加 optional item「Is the output a systematic
   review? → Then PRISMA 2020 flow diagram required」

**Tier**: **Tier 2** — LLM 知道 PRISMA 存在和大致目的，但 **27-item checklist 的
具體 items、2020 版 vs 2009 版的差異、flow diagram 的 6 steps 都容易錯**。body
需要 spell out 關鍵 items（至少 Title / Abstract / Methods: eligibility criteria /
Methods: information sources / Methods: search strategy）。

---

# Cluster D — Strategic & Investment Canon

## Q8. Porter — Competitive Strategy (1980) + Five Forces That Shape Strategy (HBR 2008)

### 書誌（已驗證）

- **作者**: Michael E. Porter
- **原書**: *Competitive Strategy: Techniques for Analyzing Industries and Competitors*
- **出版**: Free Press, 1980（書）; reprinted 1998; currently in its 60th+ printing
- **ISBN-13**: 978-0684841489
- **HBR original article**: "How Competitive Forces Shape Strategy" *HBR* March-April 1979
- **HBR 2008 update**: "The Five Competitive Forces That Shape Strategy" *HBR* January 2008, vol 86 no 1, pp. 25-40
- **驗證來源**: https://hbr.org/2008/01/the-five-competitive-forces-that-shape-strategy; Harvard Business School faculty page https://www.hbs.edu/faculty/Pages/item.aspx?num=195

### The Five Forces（已驗證）

1. **Rivalry among existing competitors** (中心力)
2. **Threat of new entrants**
3. **Bargaining power of suppliers**
4. **Bargaining power of buyers**
5. **Threat of substitute products or services**

### Three Generic Strategies（原書 Ch.2）

1. **Cost leadership**
2. **Differentiation**
3. **Focus** (= cost focus / differentiation focus)

### 2008 HBR update 新增內容

- 對每個 force 的 operational questions 擴充
- 討論 industry 邊界界定的問題（"what is the industry?"）
- 批評 misapplications（把 government、complements、growth rate 等誤歸為 6th/7th
  force）— Porter 明確否定這些
- 加 strategic implications 段

### 對 research-team 的應用

- **competitive-analysis.md** protocol 目前完全無 framework cite，應 ground 在
  Porter 5 Forces
- research-team 的 competitive 評估 methodology 直接對齊 5 forces 結構
- 加 Porter 1980 書 + 2008 HBR update 為 primary source pair

**Tier**: **Tier 1** — Porter 5 Forces 是 MBA core 內容，LLM parametric 極充足。
body 只需 1-line bullet + Porter anchor 即可。

---

## Q9. Kim & Mauborgne — Blue Ocean Strategy (2005 / 2015 expanded)

### 書誌（已驗證）

- **作者**: W. Chan Kim & Renée Mauborgne (INSEAD professors)
- **標題**: *Blue Ocean Strategy: How to Create Uncontested Market Space and Make the Competition Irrelevant*
- **原版**: Harvard Business School Press, 2005-02-03, ISBN 978-1591396192
- **Expanded Edition**: Harvard Business Review Press, 2015-01-20, ISBN 978-1625274496
- **銷量**: 4M+ copies，48 語言翻譯
- **驗證來源**: blueoceanstrategy.com 官方頁; HBR; Wikipedia; academia.edu paper

### 核心框架

**Red Ocean vs Blue Ocean**:
- Red Ocean: 現有 industry，head-to-head competition，zero-sum
- Blue Ocean: 新創 market space，uncontested，demand-creation

**Strategy Canvas**: 2D 圖，X 軸 = competing factors, Y 軸 = level of offering

**4 Actions Framework** (Eliminate-Reduce-Raise-Create Grid):
1. **Eliminate** — which factors taken for granted should be eliminated?
2. **Reduce** — which factors should be reduced below industry standard?
3. **Raise** — which factors should be raised above industry standard?
4. **Create** — which factors should be created that industry has never offered?

**Value Innovation**: 同時追求 differentiation + low cost 的策略核心

**Six Paths Framework** (how to identify blue oceans):
1. Alternative industries
2. Strategic groups
3. Buyer chain
4. Complementary products
5. Functional-emotional orientation
6. Time (trends)

### 對 research-team 的應用

**competitive-analysis.md** protocol 應加 Blue Ocean 作為 **alternative framework**
—Porter 5 Forces 處理「如何在現有 industry 中競爭」，Blue Ocean 處理「如何脫離
既有 industry」。兩個互補不排他。

**⚠️ 重要 attribution 修正**: research-team 目前有些 implicit framing 談到
「未被滿足的市場」「藍海機會」但沒有 cite Kim & Mauborgne — 這是 Cluster E（Critical
Attribution Corrections）的一個項目。

**Tier**: **Tier 1** — Blue Ocean Strategy 是 HBR Press 暢銷書，LLM parametric 充足。

---

## Q10. Osterwalder — Business Model Canvas (2010)

### 書誌（已驗證）

- **作者**: Alexander Osterwalder & Yves Pigneur (with 470 BMC practitioners from 45 countries)
- **標題**: *Business Model Generation: A Handbook for Visionaries, Game Changers, and Challengers*
- **出版**: John Wiley & Sons, 2010-07
- **ISBN-13**: 978-0470876411
- **頁數**: 281 + iv
- **驗證來源**: Wiley; strategyzer.com (Osterwalder's company); Wikipedia Business Model Canvas article

### The 9 Building Blocks

```
┌──────────────┬──────────────┬─────────────────┬──────────────┬──────────────┐
│ Key          │ Key          │ Value           │ Customer     │ Customer     │
│ Partners     │ Activities   │ Propositions    │ Relationships│ Segments     │
│              ├──────────────┤                 ├──────────────┤              │
│              │ Key          │                 │ Channels     │              │
│              │ Resources    │                 │              │              │
├──────────────┴──────────────┴─────────────────┴──────────────┴──────────────┤
│ Cost Structure                 │ Revenue Streams                             │
└────────────────────────────────┴─────────────────────────────────────────────┘
```

1. **Customer Segments** (CS)
2. **Value Propositions** (VP)
3. **Channels** (CH)
4. **Customer Relationships** (CR)
5. **Revenue Streams** (R$)
6. **Key Resources** (KR)
7. **Key Activities** (KA)
8. **Key Partners** (KP)
9. **Cost Structure** (C$)

### 對 research-team 的應用

- **market-analysis.md** 或 **competitive-analysis.md** 加 Business Model Canvas
  作為 **company-level analysis framework**
- research-team 目前沒有這個層次的 framework；加它可以讓「公司 X 的商業模式是什麼」
  這種常見 research task 有結構化 output
- cite Osterwalder 2010 + strategyzer.com 官網

**Tier**: **Tier 1** — BMC 是 startup / MBA curricula 標配，LLM parametric 充足。

---

## Q11. Aaker — Managing Brand Equity (1991)

### 書誌（已驗證）

- **作者**: David A. Aaker
- **標題**: *Managing Brand Equity: Capitalizing on the Value of a Brand Name*
- **出版**: The Free Press (Simon & Schuster imprint), 1991-09
- **ISBN-13**: 978-0029001011
- **驗證來源**: Simon & Schuster; Internet Archive; Google Books

### Brand Equity 5 Dimensions

Aaker 的定義：brand equity = 一組與品牌相關的 assets and liabilities

1. **Brand Loyalty**
2. **Brand Awareness** (aided + top-of-mind)
3. **Perceived Quality**
4. **Brand Associations** (other than perceived quality)
5. **Other Proprietary Brand Assets** (trademarks, patents, channel relationships)

### 對 research-team 的應用

competitive-analysis 或 market-analysis protocol 加 Aaker 5 dimensions 作為
品牌分析 scaffolding。cite Aaker 1991。

**Tier**: **Tier 1** — Aaker 1991 是 brand management 領域標配 anchor。

---

## Q12. Graham & Dodd — Security Analysis (1934 / 2008 6th ed)

### 書誌（已驗證）

- **作者**: Benjamin Graham & David L. Dodd
- **標題**: *Security Analysis*
- **原版**: Whittlesey House (McGraw-Hill) 1934
- **6th edition**: McGraw-Hill 2008, foreword by Warren E. Buffett; introductions by Seth A. Klarman, James Grant, Jeffrey M. Laderman, Roger Lowenstein, Howard S. Marks
- **ISBN-13**: 978-0071592536
- **基礎**: 2008 6th ed 的 classic text 是 **1940 second edition** (not 1934 first);
  2008 版加 200 頁現代評論
- **驗證來源**: McGraw-Hill; amazon; Wikipedia; goodreads

### 核心概念

- **Intrinsic value** — 公司的 fundamentals 決定價值，而非市場情緒
- **Margin of safety** — 買入價須明顯低於 intrinsic value
- **Mr. Market metaphor** — 市場像情緒化交易對手，可利用他的 mispricing
- **Quantitative vs qualitative analysis** — 盈利記錄 + balance sheet + 流動性 +
  ROIC 等硬指標 vs 管理層品質 / 產業結構等軟判斷
- Graham 是 Warren Buffett 的老師（Columbia Business School）

### 對 research-team 的應用

**investment.md** protocol 目前 L5-12 寫「Business Model / Financials / Valuation
/ Catalysts / Risks」5-factor framework，這是 generic framework。加 Graham & Dodd
作為 **value investing canonical anchor**：

- 如果 user 的 task 是 "evaluate this stock as a value investor"，則 investment
  protocol 應切換到 margin of safety + intrinsic value 思路
- 為 Damodaran DCF 框架提供對照組（DCF vs value investing 是兩套互補框架）

**Tier**: **Tier 2** — LLM 知道 Graham & Dodd 存在，但「margin of safety」「Mr.
Market」「net-net」等 jargon 的 precise Graham-ian 定義會混淆（常跟後繼者如
Klarman 2009 *Margin of Safety*、Buffett letters 混）。body 需要 spell out。

---

## Q13. Damodaran — Investment Valuation (2012) / Dark Side of Valuation (2018)

### 書誌（已驗證）

#### Investment Valuation 3rd ed

- **作者**: Aswath Damodaran (NYU Stern 教授)
- **標題**: *Investment Valuation: Tools and Techniques for Determining the Value of Any Asset*
- **版次**: 3rd edition
- **出版**: Wiley Finance, 2012-03
- **ISBN-13**: 978-1118011522
- **pages**: 992
- **support site**: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/Inv3ed.htm

#### Dark Side of Valuation 3rd ed

- **作者**: Aswath Damodaran
- **標題**: *The Dark Side of Valuation: Valuing Young, Distressed, and Complex Businesses*
- **版次**: 3rd edition
- **出版**: Pearson FT Press, 2018-05-04
- **ISBN-13**: 978-0134854106
- **pages**: 800
- **support site**: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/DSV3ed.htm

### 核心 frameworks

1. **Discounted Cash Flow (DCF)** — intrinsic value = Σ (FCFF or FCFE) / (1+WACC)^t
2. **Relative valuation** — multiples (P/E, EV/EBITDA, P/B, P/S)
3. **Contingent claim valuation** — real options (Black-Scholes 應用到實物投資)
4. **Terminal value** — Gordon growth 或 exit multiple
5. **Risk premium** — equity risk premium estimation (historical, implied, country)

### 對 research-team 的應用

**investment.md** 應 ground 在 Damodaran 3rd ed + Dark Side 3rd ed。Damodaran
的關鍵優勢：**NYU Stern 開放教材完全 free** — pages.stern.nyu.edu/~adamodar/
提供 chapter PDFs、spreadsheets、datasets。research-team 的 investment report
應 cite Damodaran 公式（含具體 WACC 計算步驟、beta levering/unlevering 等）。

**Tier**: **Tier 2** — DCF 是 MBA core，LLM 知道，但 Damodaran 的具體 framework
（例如 "the dark side" 處理 distressed/cyclical/emerging market 的具體 adjustment
步驟）需要 body spell out。

---

## Q14. Merrill Lynch Investment Clock (Greetham & Hartnett 2004)

### 書誌（已驗證）

- **作者**: Trevor Greetham (Director of Global Asset Allocation, Merrill Lynch) + Michael Hartnett (co-author)
- **標題**: *The Investment Clock: Making money from the business cycle*
- **發行**: Merrill Lynch Global Asset Allocation report
- **日期**: 2004-11-10
- **類型**: Industry research report（非書籍）
- **Canonical URL**: 在 drwealth.com 與 medium 有 full PDF mirror（原 Merrill Lynch
  URL 已 dead；ks3-cn-beijing.ksyun.com mirror 存在）
- **back-test**: 30+ 年 macro data 回測

### The 4 Phases (Investment Clock model)

Greetham 定義兩軸：**growth vs trend**（up/down）× **inflation direction**（up/down）

|  | Inflation Down | Inflation Up |
|---|---|---|
| **Growth Up** | **Recovery** → Stocks outperform | **Overheat** → Commodities outperform |
| **Growth Down** | **Reflation** → Bonds outperform | **Stagflation** → Cash outperforms |

4 phases cycle: **Reflation → Recovery → Overheat → Stagflation → Reflation**

### 對 research-team 的應用

**⚠️ 重要 attribution 修正**: research-team 目前 protocols/investment.md L15 寫:

> "3. **Framework**: Identify regime (expansion/slowdown/contraction/recovery)"

這是 **implicit Investment Clock** 但：
1. 沒有 cite Greetham & Hartnett 2004
2. 命名錯誤 — Investment Clock 的 4 phase 不是「expansion/slowdown/contraction/
   recovery」，而是「Recovery / Overheat / Stagflation / Reflation」
3. 兩軸沒有明示（growth direction vs inflation direction）

**修正方案**: 
1. Primary Source 加 Greetham & Hartnett 2004
2. Body 重寫這段為 explicit Investment Clock model with 2×2 matrix
3. 或者替換為 more neutral macro regime framework（e.g., Bridgewater all weather）
   並改 cite

**Tier**: **Tier 3** — Merrill Lynch Investment Clock 是 **2004 report**，不是書
也不在 Google Scholar 高引用區。LLM cold-query 對 Investment Clock 的具體 4-phase
naming 和 2×2 matrix **會錯**（常把 4 phases 搞成「expansion/peak/contraction/
trough」business cycle 術語，而 Investment Clock 的 4 phases 是不同的）。body
需要 fully spell out 2×2 matrix 和對應資產類別。

---

# Cluster E — OSS Evaluation & Supply Chain Safety

## Q15. OpenSSF Scorecard

### 書誌（已驗證）

- **發起機構**: Open Source Security Foundation (OpenSSF, Linux Foundation sub-project)
- **名稱**: *Security Scorecards for Open Source Projects* / OpenSSF Scorecard
- **canonical URL**: https://scorecard.dev/
- **GitHub**: https://github.com/ossf/scorecard
- **首次 public release**: 2020-11（Google + GitHub + others 合作）
- **paper**: arxiv.org/pdf/2208.03412

### The 18 Checks (已驗證 via arXiv paper + GitHub docs/checks.md)

按 3 themes 分組：

#### Source Code Risk Assessment
1. **Binary-Artifacts** — 檢查 repo 有無 checked-in binary
2. **Branch-Protection** — 檢查 main branch protection 設定
3. **Code-Review** — 檢查 commits 是否經過 review
4. **Contributors** — 檢查 contributor 來源多樣性
5. **License** — 檢查是否有可辨識的授權檔
6. **Signed-Releases** — 檢查 releases 是否 cryptographically signed

#### Build Process Risk Assessment
7. **CI-Tests** — 檢查 CI 有沒有跑 tests
8. **CII-Best-Practices** — 檢查是否有 CII Best Practices Badge
9. **Dangerous-Workflow** — 檢查 GitHub Actions 有沒有危險 pattern
10. **Dependency-Update-Tool** — 檢查是否使用 Dependabot/Renovate
11. **Fuzzing** — 檢查是否整合 fuzzing framework
12. **Packaging** — 檢查是否發布到 package registry
13. **Pinned-Dependencies** — 檢查 deps 是否 pinned by hash
14. **SAST** — 檢查是否使用 static analysis
15. **Token-Permissions** — 檢查 workflow tokens 最小權限

#### Holistic / Project Risk Assessment
16. **Maintained** — 檢查 recent commit activity
17. **SBOM** — 檢查 release 是否含 SBOM
18. **Vulnerabilities** — 檢查是否有 open vulnerabilities (via OSV)

**Scoring**: Each check 0-10; total = weighted average

### 對 research-team 的應用

**stack-evaluation.md** 目前 Step 4 的 quantitative signals table 是 **自創
threshold**（>500 issues, >12 months 等）。應 replace with OpenSSF Scorecard 的
18 checks 作為 structured OSS health assessment。

**oss-safety.md** 目前完全沒 cite OpenSSF Scorecard — 應該作為 primary framework。

**⚠️ 重要 attribution 修正**: research-team 的 OSS quality thresholds 不是自創
標準（雖然目前 skill 沒 cite 任何外部來源），應 explicitly 對齊 OpenSSF Scorecard
或至少在 oss-safety.md 聲明「thresholds are internal conventions supplementing
OpenSSF Scorecard checks」。

**Tier**: **Tier 2** — OpenSSF Scorecard 在 LLM training data 中有覆蓋（2020-
2022 arXiv paper）但 **18 checks 的具體 naming 和 scoring 會混**。body 需要
list 18 checks 清單（至少 grouped by theme）。

---

## Q16. NIST SSDF SP 800-218 v1.1

### 書誌（已驗證）

- **作者機構**: NIST (National Institute of Standards and Technology)
- **名稱**: *Secure Software Development Framework (SSDF) Version 1.1: Recommendations for Mitigating the Risk of Software Vulnerabilities*
- **識別**: NIST Special Publication 800-218
- **版本**: v1.1 (final)
- **日期**: **2022-02 final release**
- **DOI**: 10.6028/NIST.SP.800-218
- **URL**: https://csrc.nist.gov/pubs/sp/800/218/final
- **PDF**: https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-218.pdf
- **驗證**: NIST CSRC 官方頁

### 4 Practice Groups

1. **Prepare the Organization (PO)** — 組織級準備工作（PO.1 to PO.5）
2. **Protect the Software (PS)** — 保護 in-flight 與 at-rest 軟體（PS.1 to PS.3）
3. **Produce Well-Secured Software (PW)** — 開發階段 secure coding（PW.1 to PW.9）
4. **Respond to Vulnerabilities (RV)** — 事件回應（RV.1 to RV.3）

Total: **19 practices** across 4 groups

### Related

- **NIST SP 800-218 Rev 1 (v1.2)** — draft 狀態（initial public draft available），
  尚未 final
- **NIST SP 800-218A** — Generative AI Community Profile of SSDF（final 狀態）
- **Executive Order 14028** (2021-05) — Biden 的 cybersecurity EO，driver for
  SSDF 制定

### 對 research-team 的應用

- **oss-safety.md** 目前沒 cite NIST SSDF；應加入作為 "secure development lifecycle"
  reference standard
- 為 research-team 評估 "這個 OSS 專案的開發流程是否 secure" 提供 framework
  結構，而不是自創 checklist
- 與 OpenSSF Scorecard 搭配：Scorecard 是 **operational metric collection**，SSDF
  是 **process framework** — 兩者互補

**Tier**: **Tier 2** — LLM 知道 NIST SSDF 存在，但 PO/PS/PW/RV 4-group naming +
19 practice count + EO 14028 的 cause-effect 關係容易混。body 需要 spell out
4 groups + 各 group 的核心 practices.

---

## Q17. SLSA v1.1

### 書誌（已驗證）

- **發起機構**: OpenSSF / SLSA framework
- **名稱**: *Supply-chain Levels for Software Artifacts (SLSA)*
- **canonical URL**: https://slsa.dev/
- **current version**: v1.1 (as of 2024+)
- **v1.0**: 2023-04 released
- **GitHub**: https://github.com/slsa-framework/slsa

### The 4 Levels (L0 - L3)

| Level | Provenance | Signing | Infrastructure | 攻擊抵抗度 |
|---|---|---|---|---|
| **L0** | ✗ None | ✗ | developer workstation OK | 基線 |
| **L1** | ✓ Available to consumer | ✗ | 任何 | 可 replay attack 但有資料 |
| **L2** | ✓ Digitally signed | ✓ Signed by build platform | Dedicated/protected infra (not dev workstation) | 可防偽造 provenance |
| **L3** | ✓ Signed + hardened | ✓ Signed + isolated build | Hardened build platform | 可防 insider threat + compromised credentials |

### 核心概念

- **Provenance** — verifiable records of how software was built
- **Tamper resistance** — 防止 artifact 未授權修改
- **Isolation + reproducibility** — build 在受控環境

### 對 research-team 的應用

**oss-safety.md** 應加 SLSA 作為 supply chain integrity reference。目前 oss-safety.md
L34-41 的 "Supply Chain Safety" 段講 typosquatting / lockfile 等戰術，但沒有
structural framework。加 SLSA 4 levels 作為 structural reference。

**Tier**: **Tier 2** — LLM 知道 SLSA 存在和大致目的，但 **4 levels 的具體 delta
和 L3 的 hardening requirements** 會混。body 需要 table spell out.

---

## Q18. CVSS v4.0

### 書誌（已驗證）

- **發起機構**: FIRST.org (Forum of Incident Response and Security Teams)
- **名稱**: *Common Vulnerability Scoring System v4.0 Specification Document*
- **版本**: v4.0 (current)
- **日期**: **2023-11-01 released**
- **URL**: https://www.first.org/cvss/v4.0/
- **specification PDF**: https://www.first.org/cvss/v4-0/cvss-v40-specification.pdf
- **user guide**: https://www.first.org/cvss/v4.0/user-guide

### 4 Metric Groups（取代 v3.1 的 3 groups）

1. **Base Metrics (B)** — 內在特徵，時間不變（必填）
2. **Threat Metrics (T)** — 當前威脅情報（選填）
3. **Environmental Metrics (E)** — 特定部署環境的修飾（選填）
4. **Supplemental Metrics (S)** — 新增；額外 context 不影響 score（選填）

### Score Variants

- **CVSS-B** — Base only
- **CVSS-BT** — Base + Threat
- **CVSS-BE** — Base + Environmental
- **CVSS-BTE** — Base + Threat + Environmental

### Severity ratings

| Score | Rating |
|---|---|
| 0.0 | None |
| 0.1-3.9 | Low |
| 4.0-6.9 | Medium |
| 7.0-8.9 | High |
| 9.0-10.0 | Critical |

### 對 research-team 的應用

**oss-safety.md** L31 寫「No unpatched critical/high CVEs」是 implicit CVSS
severity 表述 — 應明確 cite CVSS v4.0 severity rating scale.

**Tier**: **Tier 2** — LLM 知道 CVSS 並能解釋 base score，但 **v4.0 的 4-group
model vs v3.1 的 3-group model** 會混（LLM training cutoff 可能還停在 v3.1）。
body 需要 spell out v4.0 的新 Supplemental group.

---

## Q19. SPDX 3.0

### 書誌（已驗證）

- **發起機構**: Linux Foundation SPDX working group
- **名稱**: *System Package Data Exchange (SPDX) Specification*
- **current version**: **3.0 released 2024-04**; v3.0.1 patch 2025-08
- **ISO status**: ISO/IEC 5962:2021 對應的是 **SPDX 2.2.1**，v3.0 尚未 re-register
- **URL**: https://spdx.dev/
- **license list**: https://spdx.org/licenses/

### 關鍵概念

- **SPDX License Identifier** — 標準短 ID（e.g., "MIT", "Apache-2.0", "GPL-3.0-only"）
- **License Expression** — 用 AND / OR / WITH / `+` 組合多個 license
- **SBOM** — SPDX 是 SBOM 主流 format 之一（另一個是 CycloneDX）
- **SPDX 3.0 data model** — 以 RDF 為基礎，可用 JSON-LD / Turtle / RDF/XML 序列化

### 對 research-team 的應用

**oss-safety.md** L8-21 的 license list 使用了「MIT, ISC, BSD-2-Clause, ...」
等 identifier — 這些是 **SPDX License Identifiers**，應 explicitly cite SPDX。

**Tier**: **Tier 1** — SPDX License Identifier 是 LLM 日常接觸的 metadata，
parametric 充足。Primary Source 只需 anchor.

---

## Q20. CHAOSS Project

### 書誌（已驗證）

- **發起機構**: Linux Foundation CHAOSS project
- **名稱**: *Community Health Analytics in Open Source Software (CHAOSS)*
- **canonical URL**: https://chaoss.community/
- **metrics repo**: https://github.com/chaoss/metrics
- **software**: GrimoireLab (Bitergia) + Augur

### Metrics 分類（working groups）

- **Diversity, Equity, and Inclusion (DEI)**
- **Evolution** (code development patterns over time)
- **Risk** (project sustainability risk)
- **Common Metrics**
- **Value** (business value created)
- **App Ecosystem**
- **Scientific Software**

### 對 research-team 的應用

**stack-evaluation.md** 的 quantitative signals 目前是自創 table。可以：
1. 不強制對齊 CHAOSS — research-team 不是純 OSS analysis team
2. 但應 **explicit reference CHAOSS** 作為 "more rigorous alternative if OSS
   health is the core question"
3. 在 stack-evaluation.md 的 Rules 加一條：「Thresholds in Step 4 are internal
   operational heuristics. For formal OSS health assessment, align with CHAOSS
   metrics framework (chaoss.community).」

**Tier**: **Tier 2** — LLM 知道 CHAOSS 存在但 working groups 細分會混.

---

# Cluster F — Search / Information Literacy / Journalism

## Q21. ACRL Framework for Information Literacy (2016)

### 書誌（已驗證）

- **發行機構**: ACRL (Association of College & Research Libraries, a division of ALA)
- **名稱**: *Framework for Information Literacy for Higher Education*
- **正式通過**: **2016-01-11 filed by ACRL Board; 2016-06 rescinded 2000 Information Literacy Competency Standards**
- **URL**: https://www.ala.org/acrl/standards/ilframework
- **full PDF**: https://www.ala.org/sites/default/files/acrl/content/issues/infolit/Framework_ILHE.pdf

### The 6 Frames (exact canonical names)

1. **Authority Is Constructed and Contextual**
2. **Information Creation as a Process**
3. **Information Has Value**
4. **Research as Inquiry**
5. **Scholarship as Conversation**
6. **Searching as Strategic Exploration**

每個 frame 含：
- 一段 explanation
- **Knowledge practices** (what learners should be able to do)
- **Dispositions** (what mindsets learners should adopt)

### 關鍵 concept

"Threshold concepts" — ACRL Framework 的 theoretical base 是 Meyer & Land's
threshold concept theory: 某些 concepts 一旦理解就會 transform 學習者的思考方式，
且 irreversible。

### 對 research-team 的應用

- **citation-standards.md** 或一個新的 **information-literacy.md** standards 檔案
  應 ground 在 ACRL Framework
- 6 frames 對應 research-team 的 SELF check：
  - "Authority Is Constructed and Contextual" → primary source 評估 discipline
  - "Information Creation as a Process" → 對應 peer-review vs preprint 區分
  - "Information Has Value" → 對應 citation ethics
  - "Research as Inquiry" → 對應 research question formulation
  - "Scholarship as Conversation" → 對應 citation chain tracing
  - "Searching as Strategic Exploration" → 對應 multi-database search discipline

**Tier**: **Tier 2** — LLM 知道 ACRL Framework 存在但 6 frames 具體 naming 和
順序常錯（"Authority Is..." 的 canonical wording 常被簡化）。body 需要 list 6 frames
with exact wording.

---

## Q22. SPJ Code of Ethics (2014-09-06 revision)

### 書誌（已驗證）

- **發行機構**: Society of Professional Journalists
- **名稱**: *SPJ Code of Ethics*
- **current version**: **2014-09-06 revision** (1st major revision since 1996)
- **URL**: https://www.spj.org/spj-code-of-ethics/
- **PDF**: https://www.spj.org/pdf/spj-code-of-ethics.pdf

### The 4 Pillars (exact canonical names)

1. **Seek Truth and Report It**
2. **Minimize Harm**
3. **Act Independently**
4. **Be Accountable and Transparent**

### Key 2014 updates (關 sourcing/verification)

- **Verify information before releasing it** — explicit 要求
- **Use original sources whenever possible** — 定義 original sources 為「people,
  publications, historical documents, or other records that document events
  first-hand」
- **Hyperlinks as attribution** — 數位時代明文承認
- **Anonymous sources discipline** — be judicious; explain why anonymity granted;
  never pay for access

### 對 research-team 的應用

**citation-standards.md** 加 SPJ 作為 journalism sourcing anchor（即使 research-team
不是 journalism team，但 "primary source" 的 operational definition 在 SPJ 是最
明確的）。

**Tier**: **Tier 1** — SPJ Code 是 LLM 訓練資料高度覆蓋的 public document.

---

## Q23. Kovach & Rosenstiel — Elements of Journalism 4th ed (2021)

### 書誌（已驗證）

- **作者**: Bill Kovach & Tom Rosenstiel
- **標題**: *The Elements of Journalism: What Newspeople Should Know and the Public Should Expect*
- **版次**: **Revised and Updated 4th edition, 2021**
- **出版**: Crown (Penguin Random House), 2021-05-18
- **ISBN-13**: 978-0593239353
- **驗證**: Penguin Random House; Amazon; Tom Rosenstiel 官網

### The 10 Elements of Journalism

1. Journalism's first obligation is to **the truth**
2. Its first loyalty is to **citizens**
3. Its essence is a **discipline of verification**
4. Its practitioners must maintain **independence** from those they cover
5. It must serve as an **independent monitor of power**
6. It must provide a **forum for public criticism and compromise**
7. It must strive to make the **significant interesting and relevant**
8. It must keep the news **comprehensive and proportional**
9. Its practitioners must be allowed to exercise their **personal conscience**
10. Citizens, too, have **rights and responsibilities** when it comes to the news

### 對 research-team 的應用

"Discipline of verification" (element 3) 是 research-team **discipline 的核心
理論基礎**。目前 research-team 的 Source Citation gate 沒有這個 anchor。

建議在 citation-standards.md 加一句「The verification discipline enforced by the
Source Citation gate is grounded in Kovach & Rosenstiel's 'discipline of
verification' (The Elements of Journalism, 4th ed., 2021, element 3)」。

**Tier**: **Tier 1** — Elements of Journalism 是 journalism core curriculum 標配。

---

# Cluster G — Citation Format Manuals

## Q24. APA Publication Manual 7th ed (2020)

### 書誌（已驗證）

- **發行機構**: American Psychological Association
- **標題**: *Publication Manual of the American Psychological Association*
- **版次**: **7th Edition**
- **年份**: 2020
- **ISBN-13**: 978-1433832178 (softcover)
- **URL**: https://apastyle.apa.org/products/publication-manual-7th-edition

### Key rules

- **Author-date in-text citation**: (Author, Year) 或 Author (Year) 敘事式
- **et al. rule changed in 7th**: 3+ 作者就用 "et al." 首次引用起（6th ed 是 6+ 作者）
- **DOI 顯示**: 用 https:// 格式的 URL (not "doi:" prefix)
- **Reference list** 按作者姓氏字母排序

### 對 research-team 的應用

academic-research.md L85 已寫「APA format preferred」但沒 cite 版本。應明示
**APA 7th ed (2020)**。

**Tier**: **Tier 1** — APA 是 LLM 超熟的 citation style.

---

## Q25. Chicago Manual of Style 18th ed (2024-09)

### 書誌（已驗證）

- **發行機構**: University of Chicago Press
- **名稱**: *The Chicago Manual of Style*
- **版次**: **18th Edition** — **⚠️ 注意 Phase 1 預設 17th 是舊版，2024-09 已出 18th**
- **年份**: 2024-09
- **ISBN-13**: 978-0226817972 (hardcover)
- **online**: https://www.chicagomanualofstyle.org/

### 2 Documentation Systems

1. **Notes-Bibliography (NB) system** — humanities 偏好; footnotes + bibliography
2. **Author-Date system** — social sciences 偏好; (Author Year) 模式

### 18th edition changes (key ones)

- **Place of publication 不再必須** — 18th ed 廢除 books 的 city of publication
  要求
- **Inclusive page numbers for book chapters 不再必須** — bibliography entries for
  chapters in edited books 可省略 page range
- 其他小幅 updates to digital sources handling

### 對 research-team 的應用

**citation-standards.md** 應加 Chicago 18th ed 作為 **humanities research format**
primary source，與 APA 7th (social sciences) 形成完整對應。

**Tier**: **Tier 2** — 17 → 18 transition 是 2024-09 發生的，LLM training cutoff
可能還停在 17th ed 的規則（特別是「place of publication required」這種已廢止的
規則）。body 需要 spell out 18th ed 的關鍵改變以防 drift.

---

## Q26. SIST 02-2007 参照文献の書き方 (discontinued 2012-03)

### 書誌（已驗證）

- **發行機構**: 独立行政法人 科学技術振興機構 (Japan Science and Technology Agency, JST)
- **標題**: *科学技術情報流通技術基準 参照文献の書き方 SIST 02-2007*
- **版本**: 2007-03 published; merges SIST 02-1997 + SIST 02 suppl.-2003 into single document
- **業務終了**: **2012-03** (JST 第 2 期中期計画 2007-2011 の終了に伴い 2011-12-21 発表)
- **PDF (via NDL WARP archive)**: https://warp.ndl.go.jp/info:ndljp/pid/12003258/jipsti.jst.go.jp/sist/pdf/SIST02-2007.pdf
- **hand-off**: https://jipsti.jst.go.jp/sist/（現狀已移除實體 standards 但保留
  reference material）

### 關鍵事實

1. SIST 02 是 JP 科学技術論文 citation 的 **de facto standard** 2007-2012
2. JST 於 2011-12-21 宣布 SIST 事業 2012-03 終了
3. **但是** 多數 JP 學術期刊仍採用 SIST 02 的寫法（特別是 J-Stage 上的工程 / 理學
   期刊）— 因此這是 "discontinued but still widely used" 的特殊狀態
4. 京都大學圖書館機構 2017 出版《参考文献の役割と書き方: 科学技術情報流通技術基準
   (SIST) の活用》作為學習指南，承認 SIST 在後 SIST 時代仍是主流

### SIST 02 vs 國際標準

- SIST 02 大致對應 ISO 690-2010 的 JP-adapted 版本
- 與 APA / Chicago 不同點：SIST 02 使用數字 superscript in-text + 數字 bibliography
  order（更接近 Vancouver style）而非 author-date
- ISBN 格式 / 日付 format / 著者名 roma-ji vs kanji 等 JP-specific conventions

### 對 research-team 的應用

- **citation-standards.md** 加 SIST 02 作為 JP citation standard reference
- ⚠️ **必須加 "discontinued 2012-03 but still widely used" caveat** — 否則會誤導
  使用者以為這是 currently maintained
- 為 JP academic research task 提供 citation format fallback（不強制，只是有這個
  選項 when user 在 J-Stage 投稿）

**Tier**: **Tier 3** — SIST 02 是 JP niche standard，LLM cold-query **不會知道**
具體 format rules 或 2012 discontinuation。body 需要 spell out 核心特徵
（superscript number / 廃止日 / JST 出版）。

---

# Cluster H — JP Information Literacy Canon

## Q27. 倉田敬子 (2007)《学術情報流通とオープンアクセス》

### 書誌（已驗證）

- **作者**: 倉田 敬子 (くらた けいこ) — 慶應義塾大學文學部教授 (1958-)
- **書名**: 《学術情報流通とオープンアクセス》
- **出版**: 勁草書房, 2007-08
- **ISBN-13**: 978-4326000326 (10: 4326000325)
- **頁數**: ix + 196 頁
- **受賞**: **第 37 回 日本図書館情報学会賞 (2008-11)**

### 內容結構

- 學術コミュニケーションと学術情報の特性
- 学術情報流通モデル
- 印刷版学術雑誌
- 学術論文の機能と構成
- 電子ジャーナル
- オープンアクセス

### 核心貢獻

倉田 從 1990 年代就開始研究 JP 學術資訊流通與電子化，本書是她多年研究的集大成。
主張「印刷版 → 電子版」的 shift 不只是載體變化，而是整個學術 communication 生態的
重構。是 JP library & information science 界 open access 研究的 foundational
primary。

### 驗證來源

- **勁草書房官網**: https://www.keisoshobo.co.jp/book/b26520.html
- **J-Stage 書評**: https://www.jstage.jst.go.jp/article/jslis/56/1/56_KJ00006395191/_article/-char/ja/
- **HUSCAP 書評**: https://eprints.lib.hokudai.ac.jp/dspace/handle/2115/30206
- **Keio 研究者詳細**: https://www.k-ris.keio.ac.jp/html/100000241_ja.html

### 對 research-team 的應用

citation-standards 或新增 `information-infrastructure.md` standards file，加
倉田 2007 作為 JP information literacy primary anchor。

**Tier**: **Tier 3** — JP 図書館情報学 専門書，LLM cold-query 不會知道具體內容。
body 需要 spell out 核心概念.

---

## Q28. 国立国会図書館 リサーチ・ナビ

### 書誌（已驗證）

- **運営機構**: 国立国会図書館 (NDL, National Diet Library)
- **名稱**: リサーチ・ナビ (Research Navi) — 「調べ方案内」portal
- **launched**: 2009-05-11
- **URL**: https://ndlsearch.ndl.go.jp/rnavi
- **EN URL**: https://ndlsearch.ndl.go.jp/en/rnavi

### 核心功能

- **テーマ別「調べ方案内」** — 主題別 research guides（JP 近代史、医学、法律、音楽等）
- **資料群別案内** — 資料種類別指南（統計、地図、系譜、舊書等）
- **参考図書紹介** — NDL 職員選定的 reference books
- **データベース一覧** — 可搜尋資料庫目錄
- **人物情報** — 人物索引

### JP 一次資料 / 二次資料 / 三次資料 taxonomy (per NDL)

NDL リサーチ・ナビ 及其 協力的「レファレンス協同データベース」明確定義：

- **一次資料 (primary source)**: 論文、記事、それらを掲載している雑誌、図書など
- **二次資料 (secondary source)**: 「どんな一次資料があるか」を探すための資料。
  書誌、目録、抄録誌、索引誌 + 辞書、便覧、百科事典、ハンドブック、図鑑
- **三次資料 (tertiary source)**: 二次資料を更に抽象化したもの（e.g., 「書誌の書誌」）

⚠️ 注意：**JP 定義的「二次資料」跟 Anglo 定義的「secondary source」不完全一致**。
JP 定義更偏 "finding aid"（目錄、索引），Anglo 定義更偏 "interpretation / analysis"
（綜述、評論）。Research-team 跨語言使用時應 explicitly 標註哪一個傳統。

### 對 research-team 的應用

- **academic-research.md** protocol 目前 L17 列「CiNii, J-Stage, NDL」作為 JP DB
  但沒有結構。加 NDL リサーチ・ナビ 作為 **JP 調べ方案内 canonical entry point**
- 加 JP 一次/二次/三次資料 taxonomy 的 Anglo-JP 對照說明（作為 research-team
  跨語言 discipline 的一環）

**Tier**: **Tier 3** — 非 Anglo 系 canonical knowledge; LLM cold-query 對 NDL
リサーチ・ナビ 的存在有感但對具體結構、JP taxonomy 與 Anglo taxonomy 的差異
會錯。body 需要 spell out.

---

## Q29. CiNii Research (NII)

### 書誌（已驗證）

- **運営機構**: 国立情報学研究所 (NII, National Institute of Informatics)
- **名稱**: CiNii Research (整合版, 2022 launch)
- **URL**: https://cir.nii.ac.jp/
- **前身**: CiNii Articles (2005 launch) + CiNii Books + CiNii Dissertations; 2022 年整合
- **含**: 研究論文 / 書籍 / 研究資料 / 研究者 / 研究プロジェクト
- **支援**: NII 研究データ基盤 (NII RDC) — GakuNin RDM + WEKO3 + CiNii Research

### 對 research-team 的應用

- research-team 目前 academic-research.md L17 寫「CiNii」但連結不詳 — 更新為
  `https://cir.nii.ac.jp/`（新版 URL）
- 加為 JP academic information infrastructure 的 canonical entry point

**Tier**: **Tier 2** — LLM 知道 CiNii 存在但可能還用舊 URL (ci.nii.ac.jp 是舊版).

---

## Q30. 日本図書館情報学会 + 情報リテラシー研究動向

### 書誌狀態

- **日本図書館情報学会** 成立 1953（原名日本図書館学會），1998 更名
- **機関誌**: 《日本図書館情報学会誌》(年 4 回刊) — J-Stage 開放
- **研究領域**: 圖書館學、情報學、情報リテラシー、學術情報流通、デジタルアーカイブ、
  公共図書館、学校図書館、大学図書館
- **相關 review**: 野末俊比古 (2010) 「研究文献レビュー：情報リテラシー教育：
  図書館・図書館情報学を取り巻く研究動向」*カレントアウェアネス* CA1703 —
  https://current.ndl.go.jp/ca1703

### 古賀崇 狀態（partial verification）

- **古賀 崇 (こが たかし)** — 天理大學教授（驗證成立）
- **研究領域**: digital archive, MLA 連携, 情報リテラシー教育, 公共図書館
- **但**: 未找到古賀崇的單獨 information literacy 專著（一手 primary book）。
  他的 publications 多為合著論文、事典章節、會議發表
- **替代方案**: 用野末俊比古 2010 CA1703 作為 JP information literacy research
  trend 的 review anchor（這是 NDL 自己的 current awareness 系列，比個別學者專著
  更系統）

### 對 research-team 的應用

- citation-standards 或 information-infrastructure.md 加 野末俊比古 2010 CA1703
  作為 JP 情報リテラシー research trend anchor
- 不強求 JP information literacy 有 book-level primary — 承認這個領域 JP 以
  journal review 為主要輸出 format

**Tier**: **Tier 3** — JP niche research territory; LLM 完全不會 cold-query 出這些.

---

# Cluster I — Critical Attribution Corrections

Research-team 的 current 版本因為 **完全沒有 primary-source citation**，反模式
較少（不像 design-team 有 blog / wiki 引用）。但有 3 處 implicit framing 需明文
補 attribution:

## Correction 1: Investment Clock 4-phase naming

**Current**: `protocols/investment.md` L15 寫:

> "3. **Framework**: Identify regime (expansion/slowdown/contraction/recovery)"

**Issue**: 這是 implicit Merrill Lynch Investment Clock 但：
1. 沒有 cite Greetham & Hartnett (2004)
2. 命名錯誤 — Investment Clock 的 4 phases 是 **Reflation / Recovery / Overheat
   / Stagflation**，而非「expansion/slowdown/contraction/recovery」
3. 兩軸（growth direction × inflation direction）沒有明示

**Correct attribution**: Greetham & Hartnett (2004) "The Investment Clock,"
Merrill Lynch Global Asset Allocation report.

**Action**: 
- 將 investment.md 的 4 phase 重命名對齊 Investment Clock 原文
- 加 2×2 matrix (growth up/down × inflation up/down) 的完整說明
- 加 Primary Source: Greetham & Hartnett (2004)

## Correction 2: Data freshness 6-month threshold

**Current**: `standards/citation-standards.md` L17 + `protocols/research.md` L30 寫:

> "Flag sources older than 6 months for fast-moving topics"

**Issue**: 6-month threshold 是 **自創 heuristic**，沒有 ground 在任何 primary
source. IPCC、Cochrane、PRISMA 都沒有這個硬閾值。

**Resolution options**:
- **Option A**: 保留 6-month 但明文標為 "internal operational convention, not
  grounded in any external standard"
- **Option B**: Replace with source-quality + topic-velocity 兩個 dimension 的
  soft judgment framework
- **Recommendation**: Option A — the 6-month rule is operationally useful even
  without external ground; just don't pretend it's a primary-sourced standard

## Correction 3: Stack-evaluation thresholds

**Current**: `protocols/stack-evaluation.md` Step 4 table 的:

> "Open issues count | GitHub | >500 unresolved"
> "Last commit date | GitHub | >12 months ago"
> "Release frequency | GitHub releases | No release in 12 months"

**Issue**: 這些 threshold 是 **自創** — 不是 CHAOSS metrics、不是 OpenSSF
Scorecard 的 numbers. 標為 threshold 沒有 citation base.

**Resolution**:
- 保留 thresholds 但明文標為 "internal operational heuristics，作為 OpenSSF
  Scorecard + CHAOSS 形式評估的輕量前置 filter"
- Primary Sources 段加 OpenSSF Scorecard + CHAOSS reference
- 讓 user 知道「如果需要 rigorous OSS health assessment，用 OpenSSF Scorecard 不是
  這個 table」

## No historical "drift" corrections needed

Research-team 不像 design-team 那樣有顯著的「3D Quality → 4-quality」或「意味性
attribution Verganti」類型的 drift，因為 research-team 沒有既有 citation 需要
被 override。Phase 2 的 corrections 都是 **補充 implicit attribution**，不是
**fix 誤引用**。

---

# JP Integration Decision

> **Decision: PREAMBLE-level integration**

## 證據與推論

### Evidence for FULL integration

- ✓ 倉田敬子 2007 是日本図書館情報学会賞 獲賞 peer-reviewed primary
- ✓ NDL リサーチ・ナビ 是 government-backed 結構化 research portal，長期維護
- ✓ SIST 02 雖 2012 discontinued 但仍是 JP STEM 期刊 de facto standard
- ✓ CiNii Research 是 government-backed 學術 infrastructure（NII）
- ✓ JP 獨立的「一次資料 / 二次資料 / 三次資料」taxonomy，與 Anglo taxonomy 有
  細微差異（JP 偏 finding-aid orientation）

### Evidence AGAINST full integration

- ✗ **JP 沒有對應 Cochrane Handbook 的 systematic review 方法論專書**
- ✗ **JP 沒有對應 PRISMA 2020 的 systematic review reporting standard**
- ✗ **JP 沒有對應 Booth《Craft of Research》的學術寫作 scaffolding 專書**
  （上田恵訳 Booth 就是翻譯，不是 JP-native 平行框架）
- ✗ **JP 情報リテラシー 研究以 journal review 為主，無 canonical framework**
  (野末 2010 CA1703 是 review not framework)
- ✗ **JP 投資 analysis 沒有對應 Damodaran 的系統化 textbook** — 可能因為日本
  buy-side 以企業分析 (四季報 / 会社四季報) 文化為主，quantitative DCF 沒有普及
- ✗ **JP 沒有對應 Porter / Kim&Mauborgne 的 strategy framework 原創專書** —
  日本 strategy 論述多為 Anglo 翻譯 + 三品和広、伊丹敬之 等 JP-adapted 應用
  研究，無 framework 創始地位
- ✗ **JP 新聞 sourcing** — 日本新聞協会「新聞倫理綱領」(2000 年改訂) 存在但比
  SPJ 2014 狹窄，主要針對報社而非 general journalism

### 判斷基準（來自 grounding-principle.md）

> Scenario 判斷:
> - Parallel JP tradition with equivalent standing → **Full integration**
>   (qa-team VSTeP precedent)
> - Local JP principles but no full framework → **Preamble only**
>   (docs-team JTAP precedent)
> - No JP parallel tradition → **Explicit note**
>   (devops-team SRE precedent)

research-team 符合 **Middle scenario**: 有 local JP infrastructure（NDL、CiNii、
SIST 02、倉田）作為 information access 與 citation format 的 JP 特色，**但**
research methodology framework 層面沒有 JP-native 平行框架 — 主要方法論
（Cochrane / PRISMA / Booth / Damodaran / Porter）都是 Anglo canon 獨占。

## Strategy: Preamble + JP infrastructure section

1. **Persona 層**: 加一行 "Anchored on X, Y, Z (Anglo primary) with JP information
   infrastructure discipline from 倉田 2007 / NDL リサーチ・ナビ / SIST 02 /
   CiNii"

2. **Standards 層**:
   - `citation-standards.md` 主要 ground 在 APA 7 / Chicago 18 / IEEE，加一個
     "JP context" 段落 cite SIST 02 + 日本新聞協会
   - 新增 `information-infrastructure.md`（optional tier 3 standard）— 倉田 + NDL
     + CiNii 的 JP information literacy infrastructure
   - 或把 JP 內容 embed 到 `citation-standards.md` 不獨立檔案

3. **Protocols 層**:
   - `academic-research.md` 的 Phase 0 Step 2 的 JP database list 結構化
     （CiNii Research + J-Stage + NDL リサーチ・ナビ + JST PubMed JP + J-GLOBAL）
   - 保留 EN + JP 雙語 search discipline

4. **不做 full integration**:
   - 不新增 JP-only protocol file（不像 qa-team 的 test-viewpoint-extraction）
   - 不強制 standards 有 JP 段落
   - 不把 SIST 02 / 倉田 拉到 Tier 1 anchor — 它們是 Tier 3 auxiliary

## 對照 precedent

| Team | Decision | Evidence pattern | Research-team comparison |
|---|---|---|---|
| qa-team v4.2 | **Full** | VSTeP/HAYST/ゆもつよ 是 JP-native 獨立 framework | ✗ research-team 沒有對應 |
| docs-team v4.3 | **Preamble** | JTAP 3 原則存在但非 full framework | **✓ 最接近 research-team** |
| devops-team v4.4 | **No overlay** | SRE/DORA/12-Factor 是 Anglo 獨占 | ✗ research-team 不是純 Anglo |
| code-team v4.6 | **Preamble** | 徳丸本 + 97 のこと 存在但非主 framework | ✓ 類似 research-team |
| design-team v4.8 | **Full** | 12 個 JP methodology 載重方法論 | ✗ research-team 沒有這個密度 |

research-team 最類似 **docs-team + code-team** 的 preamble 模式 — 有 JP 存在
感但不足以支撐 full integration.

---

# Tier Classification per Planned Standard

Phase 4 將產出 5-7 份 standards files. 以下是每份 tentative tier assignment
+ 冷查詢測試判斷:

| Planned standard | Tier | Cold-query test | 核心理由 |
|---|---|---|---|
| `source-quality-standards.md` | **1** | LLM can correctly define primary/secondary/tertiary with discipline-specific examples | 這是 library science 基礎，LLM 訓練資料極充足 |
| `confidence-and-claim-language.md` | **2** | LLM knows IPCC has calibrated language + Kent WEP + Tetlock calibration but **gets specific scales wrong** (5-tier vs 7-tier confusion, likelihood vs confidence confusion) | Body must spell out IPCC 5-tier + 7-tier likelihood + Kent 's核心主張 |
| `systematic-review-methodology.md` | **2** | LLM knows Cochrane + PRISMA but **gets step count wrong** (8 vs 9 vs 10 steps) and **confuses PRISMA versions** (2009 vs 2020, specific items) | Body must spell out Cochrane 8-step + PRISMA 2020 27-item structure |
| `research-argument-structure.md` | **1** (with caveat) | LLM knows Booth Craft of Research argument model well; but 5th ed (2024) 新增 AI chapter **may not be in LLM training data** | Tier 1 for core 5-element model; flag 5th ed new sections if evaluator needs them |
| `strategic-frameworks.md` | **1** | Porter 5 Forces + Blue Ocean + BMC + Aaker 5 dims 都是 MBA core, LLM parametric 極充足 | Body 只需 1-line per framework + Primary Source anchor |
| `investment-analysis-canon.md` | **3** | LLM knows Damodaran + Graham & Dodd + **但 Investment Clock 4-phase 常錯成 business cycle 4-phase** | Tier 3 body must spell out Investment Clock 2×2 matrix + Damodaran DCF vs relative vs real option + Graham margin of safety |
| `oss-safety.md` (revise existing) | **2** | LLM knows OpenSSF Scorecard + CVSS + SLSA 存在但 **checks count + levels count + metric groups count 常混** | Body must list 18 Scorecard checks + 4 SLSA levels + 4 CVSS v4 metric groups + 4 NIST SSDF groups |
| `citation-standards.md` (revise existing) | **2** | LLM knows APA / Chicago / SIST 但 **Chicago 18th (2024-09) 的 changes from 17th 常錯** + **SIST 02 2012 discontinuation 不知** | Body must spell out APA 7 key changes + Chicago 18 place-of-publication 廢除 + SIST 02 discontinuation caveat |
| `information-infrastructure.md` (NEW, optional) | **3** | LLM does not know NDL リサーチ・ナビ, 倉田 2007, SIST 02, JP 一次/二次/三次 taxonomy with specific detail | If included, body must be fully self-contained — JP niche knowledge |

## Tier 分佈統計

- **Tier 1**: 2-3 standards (source-quality, strategic-frameworks, possibly
  research-argument-structure)
- **Tier 2**: 3-4 standards (confidence-language, systematic-review, oss-safety,
  citation-standards)
- **Tier 3**: 1-2 standards (investment-analysis-canon, possibly information-
  infrastructure)

→ 比 design-team v4.8 的 tier 分佈（3 tier 3 / 3 tier 2 / 3 tier 1）**偏向 tier
2 集中**，因為 research-team 的 primary sources 多數是 mainstream Anglo canon
（高 LLM parametric）而非 niche JP / post-2024 standards.

---

# Open Questions for Phase 3+

Phase 2 未完全解決的問題，需在 Phase 3（grounding plan）或後續 commits 處理：

## 1. Chicago 18th edition 具體規則變更細節

18th ed 2024-09 發行時間離現在（2026-04）不久，完整 errata / clarification 清單
可能還在演進。Phase 4 撰寫 citation-standards.md 時建議 **flag 18th ed as current
but monitor for errata via chicagomanualofstyle.org**.

## 2. CHAOSS metrics 與 research-team thresholds 的精確對應

Phase 2 確認 research-team stack-evaluation.md 的 thresholds 應「對齊 CHAOSS」
或「explicitly 標為 internal」。Phase 4 需要決定：是保留 current thresholds 加
caveat？還是 replace with CHAOSS-aligned metrics？建議**保留 + caveat** (less
disruptive).

## 3. 古賀崇 是否有單獨的 information literacy 專著

Phase 2 檢索未找到。若 Phase 3 / Phase 4 能直接聯絡古賀崇研究室確認，可決定是否
cite 他的單一作品。目前替代方案是 cite 野末俊比古 2010 CA1703 作為 JP information
literacy research trend anchor.

## 4. Booth 5th ed (2024) 的新章節 content

Phase 2 verified 5th ed 2024-06-25 發行，但 **2024-06 之後出版的 content 可能
LLM training cutoff 之前沒吸收**。Phase 4 撰寫 research-argument-structure.md 時
建議：
- 核心 5-element argument model (Ch.7-12) 用 Tier 1 (stable since 1st ed 1995)
- 若要 cite 5th ed 新 AI chapter，用 Tier 2 (可能 LLM 不知道)

## 5. Investment Clock 原文 PDF 可取得性

Greetham & Hartnett 2004 原 report 的 Merrill Lynch 官方 URL 已 dead. Phase 4
撰寫 investment-analysis-canon.md 時，Primary Source 可以 cite:
- 原 report 作為 canonical primary（標 "original URL defunct"）
- drwealth.com / medium mirror 作為 operational access path
- 或者 cite Greetham 後續 Royal London Asset Management 的 更新論述 作為 stable URL

## 6. Behavioral Rules + Agents nesting drift fix

Phase 1 發現 research-team SKILL.md 將 `### Behavioral Rules` 和 `### Agents`
誤嵌套於 `## Resource Manifest` 之下。這是結構 drift，在 Phase 4 commit 2（body
refactor）時一併修正。Phase 2 的 research 責任僅是識別，不是修復。

## 7. Research-team `description` 字數

Phase 1 gap assessment 標出 research-team 的 description 可能不足 40 字。
Phase 2 範圍外 — Phase 4 撰寫 SKILL.md frontmatter 時需測字數，必要時擴充.

---

# Recommended Standards Files for Phase 4 (Commit 1/3)

以下是 Phase 4 應建立 / 修訂的 standards files, 每份以 `{filename}.md` 格式列出:

## Standard 1: `source-quality-standards.md` (NEW)

**Tier**: 1  
**Purpose**: Define primary / secondary / tertiary source taxonomy + discipline-
specific examples + "usage determines classification" rule + peer-review vs
preprint discipline.

**Primary sources**:
- JMU Library (no specific author, ongoing) — https://guides.lib.jmu.edu/sources —
  discipline-specific examples across history/science/humanities
- Cornell Library — https://guides.library.cornell.edu/sources/tertiary — tertiary
  source canonical definition
- Kovach & Rosenstiel (2021) *The Elements of Journalism*, 4th ed. Crown.
  — Discipline of Verification as journalistic grounding
- SPJ (2014) *Code of Ethics* — https://www.spj.org/spj-code-of-ethics/ —
  "Use original sources whenever possible" operational definition
- ACRL (2016) *Framework for Information Literacy for Higher Education* —
  https://www.ala.org/acrl/standards/ilframework — "Authority Is Constructed and
  Contextual" frame

**Body outline**:
- Primary / Secondary / Tertiary definition (1 paragraph)
- Discipline-specific examples table (3 columns: history / science / humanities)
- Usage-determines-classification rule (1 paragraph)
- "Primary ≠ original language" clarification (avoid confusing translation
  secondary with analysis secondary)
- Authority construction in peer review context (1 paragraph)

**Estimated length**: 70-90 lines

**Load-bearing claims covered**:
- Primary source definition (currently implicit in research-team)
- "Prefer primary sources" rule (currently ungrounded)
- Source type hierarchy for source-citation-checklist.md
- Discipline of verification (currently unframed)

---

## Standard 2: `confidence-and-claim-language.md` (NEW)

**Tier**: 2  
**Purpose**: Ground the 高/中/低 confidence scale + 事實/分析/推測 claim
classification in IPCC calibrated language + Kent WEP + Tetlock calibration.

**Primary sources**:
- Mastrandrea, M.D., et al. (2010) *Guidance Note for Lead Authors of the IPCC
  Fifth Assessment Report on Consistent Treatment of Uncertainties*. IPCC. —
  https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf
  — Confidence 5-level + Likelihood 7-level + Evidence×Agreement 2D table
- Kent, S. (1964) "Words of Estimative Probability." *Studies in Intelligence*,
  CIA. — https://www.cia.gov/resources/csi/studies-in-intelligence/archives/vol-8-no-4/words-of-estimative-probability/
  — WEP taxonomy origin + poets vs mathematicians
- Tetlock, P. E., & Gardner, D. (2015) *Superforecasting: The Art and Science
  of Prediction*. Crown. — Calibration vs Resolution + Brier score + GJP empirical

**Body outline**:
- IPCC 5-level Confidence scale (explicit table)
- IPCC 7-level Likelihood scale (explicit table with percentages)
- IPCC Evidence × Agreement 2D grid (complete 3×3 table)
- Confidence vs Likelihood: they are orthogonal — explain distinction
- Kent 1964 context (1-paragraph intellectual history)
- Tetlock calibration + resolution (1-paragraph)
- research-team 3-tier scheme as 簡化版 IPCC 5-tier — explicit mapping
- 事實/分析/推測 taxonomy ground (Kovach & Rosenstiel discipline of verification
  + Booth argument structure)

**Estimated length**: 120-150 lines

**Load-bearing claims covered**:
- 高/中/低 confidence tag (currently ungrounded)
- 事實/分析/推測 tag (currently ungrounded)
- "Cross-verify 2+ sources" rule
- Hedging discipline in research reports
- Freshness flag threshold (6-month — retain as operational convention, flag
  as internal)

---

## Standard 3: `systematic-review-methodology.md` (NEW)

**Tier**: 2  
**Purpose**: Ground academic-research.md protocol in Cochrane Handbook v6.5 +
PRISMA 2020 + Booth argument structure.

**Primary sources**:
- Higgins, J.P.T., Thomas, J., Chandler, J., Cumpston, M., Li, T., Page, M.J.,
  & Welch, V.A. (eds.) (2024) *Cochrane Handbook for Systematic Reviews of
  Interventions*, Version 6.5. Cochrane. —
  https://training.cochrane.org/handbook/current — 8-step systematic review
  process
- Page, M.J., McKenzie, J.E., Bossuyt, P.M., et al. (2021) "The PRISMA 2020
  statement: an updated guideline for reporting systematic reviews." *BMJ*
  372:n71. — https://www.prisma-statement.org/prisma-2020-statement — 27-item
  checklist + 7 sections + flow diagram
- Booth, W.C., Colomb, G.G., Williams, J.M., Bizup, J., & FitzGerald, W.T.
  (2024) *The Craft of Research*, 5th ed. University of Chicago Press. —
  Argument 5-element model (Claim/Reason/Evidence/Warrant/Ack-Response)
- (Optional) ACRL (2016) *Framework for Information Literacy for Higher
  Education* — Research as Inquiry + Scholarship as Conversation frames

**Body outline**:
- Cochrane 8-step systematic review process (explicit numbered list)
- PICO / PICOC research question framing (1-paragraph)
- PRISMA 2020 27-item checklist 7-section structure (table)
- PRISMA 2020 flow diagram 6-step (ASCII art)
- Booth 5-element argument model (Ch.7-12 summary, 1-paragraph per element)
- When to use full Cochrane vs lightweight research (1-paragraph decision rule)

**Estimated length**: 150-180 lines

**Load-bearing claims covered**:
- academic-research protocol phase structure
- research.md argument output format
- source-citation-checklist evaluation criteria
- research-quality-gate rubric criteria

---

## Standard 4: `strategic-frameworks.md` (NEW)

**Tier**: 1  
**Purpose**: Ground competitive-analysis / market-analysis protocols in Porter /
Kim&Mauborgne / Osterwalder / Aaker canon.

**Primary sources**:
- Porter, M.E. (1980) *Competitive Strategy: Techniques for Analyzing Industries
  and Competitors*. Free Press. — 5 Forces + 3 Generic Strategies (Ch.2)
- Porter, M.E. (2008) "The Five Competitive Forces That Shape Strategy."
  *Harvard Business Review* 86(1): 25-40. —
  https://hbr.org/2008/01/the-five-competitive-forces-that-shape-strategy —
  2008 update with operational questions
- Kim, W.C., & Mauborgne, R. (2015) *Blue Ocean Strategy*, Expanded Edition.
  Harvard Business Review Press. — 4 Actions Framework + Strategy Canvas + Six Paths
- Osterwalder, A., & Pigneur, Y. (2010) *Business Model Generation*. Wiley. —
  Business Model Canvas 9 blocks
- Aaker, D.A. (1991) *Managing Brand Equity*. Free Press. — 5 dimensions of
  brand equity

**Body outline**:
- Porter 5 Forces (1-line each, anchor to 2008 HBR article)
- Porter 3 Generic Strategies (1-line each)
- Blue Ocean 4 Actions (Eliminate/Reduce/Raise/Create) + Strategy Canvas 1-line
- BMC 9 blocks (labeled diagram)
- Aaker 5 dimensions of brand equity (1-line each)
- Decision rule: when to use Porter vs Blue Ocean vs BMC vs Aaker

**Estimated length**: 80-100 lines

**Load-bearing claims covered**:
- competitive-analysis.md framework choice
- market-analysis.md framework choice
- research-quality-gate.md "framework application" criterion (if exists)

---

## Standard 5: `investment-analysis-canon.md` (NEW)

**Tier**: 3  
**Purpose**: Ground investment.md protocol in Damodaran + Graham&Dodd + Merrill
Lynch Investment Clock. **Tier 3 because Investment Clock 4-phase naming is
frequently mis-stated as business cycle 4-phase**.

**Primary sources**:
- Damodaran, A. (2012) *Investment Valuation: Tools and Techniques for
  Determining the Value of Any Asset*, 3rd ed. Wiley. —
  https://pages.stern.nyu.edu/~adamodar/New_Home_Page/Inv3ed.htm — DCF / relative
  / contingent claim valuation framework
- Damodaran, A. (2018) *The Dark Side of Valuation*, 3rd ed. Pearson FT Press. —
  Young / distressed / complex business valuation
- Graham, B., & Dodd, D.L. (2008) *Security Analysis*, 6th ed. (foreword by W.
  Buffett) McGraw-Hill. — Intrinsic value + Margin of safety + Mr. Market
- Greetham, T., & Hartnett, M. (2004) *The Investment Clock: Making money from
  the business cycle*. Merrill Lynch Global Asset Allocation report, 2004-11-10.
  — 4-phase macro regime model

**Body outline**:
- Damodaran 3-framework valuation taxonomy (DCF / relative / contingent claim)
- DCF formula outline (FCFF vs FCFE, WACC, terminal value)
- Graham margin of safety + intrinsic value (1-paragraph definition + Graham quote)
- Graham Mr. Market metaphor (1-paragraph)
- Investment Clock 2×2 matrix (growth direction × inflation direction) fully
  spelled out with all 4 phase names (Reflation/Recovery/Overheat/Stagflation)
  and corresponding asset classes (Bonds/Stocks/Commodities/Cash)
- Anti-drift note: "Do not conflate Investment Clock 4-phase with business cycle
  4-phase (expansion/peak/contraction/trough) — they are different models"

**Estimated length**: 180-220 lines (Tier 3)

**Load-bearing claims covered**:
- investment.md protocol 4-phase regime framework (currently incorrectly named)
- investment.md 5-factor stock analysis framework (currently ungrounded)
- Valuation methodology choice (currently absent)

---

## Standard 6: `oss-safety.md` (REVISE existing)

**Tier**: 2  
**Purpose**: Expand existing oss-safety.md to ground in OpenSSF Scorecard +
CHAOSS + OSI + SPDX + NIST SSDF + SLSA + CVSS canonical frameworks.

**Primary sources**:
- OpenSSF Scorecard (2020-current) — https://scorecard.dev/ — 18 checks across
  Source / Build / Holistic themes
- NIST SP 800-218 v1.1 (2022-02) *Secure Software Development Framework*. —
  https://csrc.nist.gov/pubs/sp/800/218/final — 4 practice groups (PO/PS/PW/RV)
- SLSA v1.1 (2024) *Supply-chain Levels for Software Artifacts*. —
  https://slsa.dev/ — 4 levels (L0-L3)
- FIRST.org (2023) *CVSS v4.0 Specification Document*. —
  https://www.first.org/cvss/v4.0/ — 4 metric groups (Base/Threat/Environmental/
  Supplemental)
- SPDX 3.0 (2024-04) — https://spdx.dev/ — License Identifier + SBOM format
- OSI — https://opensource.org/licenses — Approved license list
- (Optional) CHAOSS — https://chaoss.community/ — OSS community health metrics

**Body outline**:
- SPDX License Identifier ground (existing list stays, cite SPDX)
- License copyleft / permissive / source-available classification (existing logic
  stays, cite OSI approved list)
- OpenSSF Scorecard 18 checks listed by theme (grouped table)
- NIST SSDF 4 practice groups (1-paragraph each)
- SLSA 4 levels table (L0-L3 with provenance/signing/infra requirements)
- CVSS v4.0 4 metric groups + severity rating scale (explicit table)
- Anti-drift: "Thresholds like '>500 issues' are internal operational heuristics,
  not CHAOSS metrics or Scorecard values"

**Estimated length**: 180-220 lines (Tier 2)

**Load-bearing claims covered**:
- License acceptability logic
- CVE severity classification
- Supply chain safety checklist
- OSS due diligence gate criteria

---

## Standard 7: `citation-standards.md` (REVISE existing)

**Tier**: 2  
**Purpose**: Expand existing citation-standards.md to ground in APA 7 + Chicago
18 + IEEE + SIST 02 canonical citation manuals.

**Primary sources**:
- American Psychological Association (2020) *Publication Manual of the American
  Psychological Association*, 7th ed. APA. — Social sciences author-date system
- University of Chicago Press (2024) *The Chicago Manual of Style*, 18th ed. —
  https://www.chicagomanualofstyle.org/ — Humanities NB system + social sciences
  author-date system
- IEEE Editorial Style Manual (current) —
  https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/ieee-editorial-style-manual/
  — Engineering numeric [1] citation
- 科学技術振興機構 (2007) *SIST 02-2007 参照文献の書き方*. JST. —
  https://warp.ndl.go.jp/info:ndljp/pid/12003258/jipsti.jst.go.jp/sist/pdf/SIST02-2007.pdf
  — JP STEM citation standard (discontinued 2012-03 but still widely used)

**Body outline**:
- APA 7 author-date format (1-paragraph + example)
- Chicago 18 Notes-Bibliography vs Author-Date (1-paragraph)
- Chicago 18 key changes from 17: place-of-publication 廢除 + chapter page
  ranges 廢除 (warn LLM about training-data drift)
- IEEE numeric [1] format (1-paragraph)
- SIST 02-2007 superscript format + JP STEM convention + **discontinuation
  caveat** (2012-03 JST事業終了 但多數 JP 期刊仍採用)
- Style selection rule: discipline → preferred style table
- Search protocol (existing text ground in SPJ + ACRL + JP infrastructure)
- Data freshness rule (retain 6-month, flag as operational convention)
- Output language rule (existing)
- Confidence / fact-analysis-speculation rules (cross-reference
  confidence-and-claim-language.md)

**Estimated length**: 140-180 lines (Tier 2)

**Load-bearing claims covered**:
- Citation format for research outputs
- Search protocol (EN + JP parallel)
- Output language discipline
- Freshness flagging
- All existing citation-standards.md content preserved but grounded

---

## Optional Standard 8: `information-infrastructure.md` (NEW, optional)

**Tier**: 3  
**Purpose**: Ground JP information literacy infrastructure (NDL + CiNii + 倉田
2007 + SIST 02 + ACRL Framework).

**Primary sources**:
- 倉田敬子 (2007) *学術情報流通とオープンアクセス*. 勁草書房. — JP 学術情報流通
  研究の基礎
- 国立国会図書館 (2009-current) リサーチ・ナビ. — https://ndlsearch.ndl.go.jp/rnavi
  — JP 調べ方案内 portal
- 国立情報学研究所 (NII) (2022-current) CiNii Research. — https://cir.nii.ac.jp/
  — JP 学術情報 integrated search
- 野末俊比古 (2010) "研究文献レビュー：情報リテラシー教育" カレントアウェアネス
  CA1703. — https://current.ndl.go.jp/ca1703 — JP 情報リテラシー research trend
- ACRL (2016) *Framework for Information Literacy for Higher Education*. —
  Anglo-American information literacy canon for comparison

**Body outline**:
- Why this standard exists (JP information infrastructure as a distinct layer
  from global research methodology)
- NDL リサーチ・ナビ structure (テーマ別 + 資料群別 + 調べ方案内 entry points)
- JP 一次資料 / 二次資料 / 三次資料 taxonomy (note: JP 二次資料 偏 finding aid,
  Anglo secondary source 偏 analysis — distinction fully spelled out)
- CiNii Research (前身 + 2022 整合 + 含 content types)
- 倉田敬子 2007 core thesis (学術雑誌 print→electronic shift implications)
- SIST 02 status (2012 discontinued but still widely used, see citation-standards.md)
- ACRL Framework 6 frames as Anglo-American counterpart
- Decision rule: when to use JP DB vs Anglo DB (1-paragraph)

**Estimated length**: 150-200 lines (Tier 3)

**Load-bearing claims covered**:
- JP database list in academic-research.md (currently unstructured)
- JP tradition honest representation (preamble-level integration)
- JP 一次資料 vs Anglo primary source distinction

**Decision**: **Optional** — if Phase 4 line budget is tight, merge JP content
into citation-standards.md 的 "JP context" section. If budget allows, split
for clarity.

---

# Summary

**Phase 2 verified sources**: 30 primary sources verified across 7 clusters
+ JP integration decision.

| Cluster | Sources verified | Status |
|---|---:|---|
| A — Source quality taxonomy | 5 (JMU/Cornell/UC Merced/Ohio State/NDL) | ✓ all verified |
| B — Confidence / Claim language | 3 (IPCC/Kent/Tetlock) | ✓ all verified |
| C — Research process (Booth/Cochrane/PRISMA) | 3 (Booth 5th/Cochrane v6.5/PRISMA 2020) | ✓ all verified |
| D — Strategic & Investment canon | 7 (Porter×2/Kim&Mauborgne/Osterwalder/Aaker/Damodaran×2/Graham&Dodd/Greetham) | ✓ all verified |
| E — OSS Safety frameworks | 6 (Scorecard/SSDF/SLSA/CVSS/SPDX/CHAOSS/OSI) | ✓ all verified |
| F — Search / Info Literacy / Journalism | 4 (ACRL/SPJ/Kovach&Rosenstiel/AP Stylebook) | ✓ all verified (AP 中信心) |
| G — Citation format | 4 (APA 7/Chicago 18/IEEE/SIST 02) | ✓ all verified |
| H — JP Information Infrastructure | 4 (倉田 2007/NDL/CiNii/野末 2010 CA1703) | ✓ 4 verified; 古賀崇 partial |

**3 Critical attribution corrections identified**:
1. Investment Clock 4-phase naming error in investment.md L15
2. 6-month freshness threshold self-invented (retain as operational convention)
3. Stack-evaluation thresholds self-invented (retain with CHAOSS reference)

**JP integration decision**: **PREAMBLE** — 4 JP information infrastructure
sources (倉田 / NDL / CiNii / SIST 02) justify a JP preamble / section in
citation-standards.md, but JP has no parallel research methodology framework to
Cochrane / PRISMA / Booth, so no JP-native protocol file.

**Tier distribution** (across 7-8 planned standards):
- Tier 1: 2-3 (source-quality, strategic-frameworks, possibly research-argument)
- Tier 2: 3-4 (confidence-language, systematic-review, oss-safety, citation-standards)
- Tier 3: 1-2 (investment-analysis-canon, optional information-infrastructure)

**Phase 3 actions**:
1. Write `## Grounding Plan for research-team v4.9.0` output file per protocol
2. Pass tier classification + primary source list forward to Phase 4
3. Flag 3 critical attribution corrections for commit 1 /3

**Phase 4 deliverables**:
- 6 standards files created (source-quality / confidence-language / systematic-
  review / strategic-frameworks / investment-canon / [optional information-
  infrastructure])
- 2 existing standards revised (oss-safety / citation-standards)
- All with `tier: {1|2|3}` frontmatter declaration
- `## Critical Attribution Corrections` section where Phase 2 identified 3 items

**Total estimated standards line count**: 
- If 7 files: 70+150+180+100+200+220+180 = ~1100 lines
- If 8 files (with information-infrastructure): add +180 = ~1280 lines

**Worker BLOCKED reasons avoided**: All candidate sources verified; no source
was unavailable to web search. JP information literacy infrastructure verified
4 out of 5 candidates (古賀崇 single-author primary missing — acceptable fallback
to 野末 2010 CA1703).

---

> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
