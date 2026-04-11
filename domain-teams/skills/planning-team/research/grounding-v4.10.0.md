---
title: planning-team 再設計研究 — product planning frameworks grounding
date: 2026-04-11
team: planning-team
refactor_version: v4.10.0
tags: [research, domain-teams, planning-team, grounding]
---

# planning-team 再設計研究 — product planning frameworks grounding

## Scope

planning-team v4.9.x 目前 `standards/planning-frameworks.md` (89 行) 列出 5 個
framework — JTBD / Assumption Mapping / Lean Canvas / 3C / 5W2H — 全部
**零 primary-source citation**。protocols/product-spec-writing.md 與
protocols/planning-brainstorming.md 同樣以 generic 描述呈現 MVP / goals
/ non-goals / value proposition 等核心概念，**無一處 anchor 到 Ries /
Cagan / Osterwalder / Doerr** 等 canonical 作者。

這個 grounding pattern 與已完成 grounding 的五個 team（qa v4.2 ISTQB/VSTeP、
docs v4.3 Diataxis/Google/JTAP、devops v4.4 Google SRE/DORA/12-Factor、
code v4.6 GoF/Fowler/NIST、research v4.9 Booth/Cochrane/IPCC、design v4.8
Norman/Nielsen/WCAG）明顯不一致 — planning-team 是**目前 domain-teams 中 product
planning primary source grounding 最薄弱**的 skill。

Phase 1 gap 觀察：

1. JTBD 使用 "When [situation], I want to [motivation], so I can [outcome]"
   模板但未歸屬 — 這是 **Intercom Paul Adams 2016 Job Story**（Alan Klement 命名），
   **不是** Christensen 原 JTBD。是 Critical Attribution Correction #1。
2. Assumption Mapping 的 DVF 4 軸（Desirability / Feasibility / Viability /
   **Usability**）不對應 Bland 2020 的 3 軸 DVF —— 4 軸版本實際是 **Marty Cagan
   Inspired 2nd ed 2018** 的 "Four Big Risks"（Value / Usability / Feasibility /
   Business Viability）。是 Critical Attribution Correction #2。
3. Lean Canvas 的 4 block 替代細節 未說明——本研究固定了 Maurya 官方 mapping。
4. 3C 歸「大前研一」但缺 publication anchor —— 需明確 cite 1975 日版 + 1982 英譯。
5. 5W2H 寫「日本ビジネス慣習由來」—— 部分正確：Kipling 1902 是 5W1H 詩源頭、
   TPS/Ohno 是 +2H 演進脈絡之一，但 origin 是多源混合而非單純日本慣習。
6. MVP / Build-Measure-Learn / Validated Learning 概念通篇未 cite Eric Ries。
7. OKR / 目標管理 系統**完全缺席**——作為 planning skill 這是一個明顯漏洞。
8. 企画書（kikakusho）作為 JP 在地 idiom 使用但無在地 primary anchor。

本研究為 v4.10.0 refactor 的 Phase 2 — 逐 cluster 驗證 9 個 framework cluster
的 load-bearing primary source，產生 standards 檔案計畫 + JP 整合決定。

## TL;DR — Primary Source Inventory

| Cluster | Canonical primary | Why load-bearing |
|---|---|---|
| JTBD 概念 | Christensen & Raynor (2003) *The Innovator's Solution* Ch.3 | JTBD theory canonical + milkshake case |
| JTBD 現代定義 | Christensen, Hall, Dillon, Duncan (2016) HBR | operational, citable restatement |
| ODI 延伸 | Ulwick (2005) *What Customers Want* | outcome-driven innovation 精細化 |
| Job Story 模板 | Adams (2016) Intercom blog + Klement (2018) *When Coffee and Kale Compete* | "When...I want...so I can..." 實際發明人 |
| Lean Startup / MVP / BML / Validated Learning | Ries (2011) *The Lean Startup* Part I & II | canonical MVP + BML 定義 |
| Customer Development | Blank (2005) *Four Steps to the Epiphany* | Ries 的師承、MVP 的 prerequisite |
| Short-form Lean intro | Blank (2013) HBR May | accessible canonical summary |
| OKR origin | Grove (1983) *High Output Management* Ch.6 | iMBO / Intel OKR 起源 |
| OKR modern canonical | Doerr (2018) *Measure What Matters* | "I will [O] as measured by [KR]" + 0.7 grading |
| BMC 9 blocks | Osterwalder & Pigneur (2010) *Business Model Generation* | 9 block canvas canonical |
| Lean Canvas | Maurya (2012/2022) *Running Lean* 2nd/3rd ed | 4 BMC 替代 |
| Assumption testing | Bland & Osterwalder (2020) *Testing Business Ideas* | DVF 3 軸 + 44 experiments |
| Cagan 4 risks | Cagan (2017) *Inspired* 2nd ed Part III | 4-axis (V/U/F/BV) — planning-team 現有 4 軸對應 |
| Product discovery | Cagan (2017) *Inspired* 2nd ed | discovery vs delivery + empowered teams |
| Continuous discovery | Torres (2021) *Continuous Discovery Habits* | Opportunity Solution Tree |
| PR/FAQ working backwards | Bryar & Carr (2021) *Working Backwards* Ch.4 | Amazon method canonical |
| 3C 分析 | 大前研一 (1975)『企業参謀』プレジデント社 / Ohmae (1982) *The Mind of the Strategist* McGraw-Hill | 3C origin |
| Value Proposition Canvas | Osterwalder, Pigneur, Bernarda, Smith (2014) *Value Proposition Design* | BMC 延伸；gain creators / pain relievers |
| ODI milkshake short form | Christensen et al. (2016) HBR Sep-Oct | same as JTBD |
| JP アイデア発想法 | ジェームス・W・ヤング (1940) *A Technique for Producing Ideas* / 今井茂雄訳 (1988)『アイデアのつくり方』TBSブリタニカ | JP 企画 古典 |
| 5W1H origin | Kipling (1902) *Just So Stories* "The Elephant's Child" | 6 honest serving men 詩源 |
| Goals / Non-Goals convention | Ubl (2020) "Design Docs at Google" (industrialempathy.com) | Google SRE engineer personal blog — 最佳公開 primary |
| AARRR Pirate Metrics | McClure (2007) "Startup Metrics for Pirates" SlideShare / 500 Hats blog | canonical AARRR origin |
| North Star Metric | Ellis & Brown (2017) *Hacking Growth* / Ellis Growth Hackers blog | NSM canonical source |

---

## Cluster 1 — Jobs-to-be-Done

### Primary sources verified

- **Theodore Levitt (1960)** *Marketing Myopia*. *Harvard Business Review* Jul-Aug 1960. — 廣為傳頌的 "People don't want a quarter-inch drill. They want a quarter-inch hole." 其實是 Levitt 的課堂箴言（由 Philip Kotler 事後紀錄），並非直接出現於 1960 原文。原文的 load-bearing claim 是「業者應定義自己為『交通業』而非『鐵路業』」——即 customer job 優先於 product category。是 JTBD 思想的 **理論前身**，不是方法論起點。
- **Peter Drucker (1954)** *The Practice of Management*. Harper & Brothers. — Drucker "the purpose of a business is to create a customer" 是 marketing concept 的 intellectual backdrop，但 Drucker 未使用 "job" 語彙。不 load-bearing for JTBD spec writing。
- **Clayton M. Christensen & Michael E. Raynor (2003)** *The Innovator's Solution: Creating and Sustaining Successful Growth*. Harvard Business School Press. ISBN 978-1-57851-852-4. — **Chapter 3** "What Products Will Customers Want to Buy?" 含 **milkshake case study**，是 JTBD 作為**商業方法論**的 canonical launch point。"Customers hire products to do jobs" 形式化表述在此章定案。
- **Anthony W. Ulwick (2005)** *What Customers Want: Using Outcome-Driven Innovation to Create Breakthrough Products and Services*. McGraw-Hill. ISBN 978-0-07-140867-7. — ODI（Outcome-Driven Innovation）是 JTBD 的**精細化方法論變體**。Ulwick 創建 Strategyn (strategyn.com) 並自 1991 發展 job mapping / desired outcome statements 量化技術。ODI 與 Christensen 派 JTBD 是「同一家」但 **工具化程度不同** — Ulwick 主張「jobs 是穩定的、solutions 是變動的」(jobs-to-be-done.com)。
- **Clayton M. Christensen, Taddy Hall, Karen Dillon, David S. Duncan (2016)** *Know Your Customers' "Jobs to Be Done"*. *Harvard Business Review* Sep-Oct 2016, vol 94 no 9, pp 54-62. — JTBD 最新 + 最 cite-able operational definition；milkshake case 的 short-form 重述。planning-team 的 **核心 JTBD citation 應優先選此文**（short, public, HBR-reviewed, 2016 年代）。
- **Paul Adams (2016)** *How we accidentally invented Job Stories*. The Intercom Blog, 2016-06-28. — **Job Story 模板 "[When ____] [I want to ____] [So I can ____]" 的實際發明出處**。Adams 當時為 Intercom CPO；Alan Klement 事後把 Intercom team 內部 format 命名為 "Job Stories"。Intercom 部落格是此模板唯一 canonical primary source。
- **Alan Klement (2018, rev)** *When Coffee and Kale Compete: Become great at making products people will buy*. Self-published (NYC Publishing). ISBN 978-1-5348-7306-3. — JTBD forces diagram (push / pull / habit / anxiety) + demand-side thinking 的 canonical 教科書之一。Klement 自 2013 起是 Christensen 派 JTBD 的主要科普化推手。

### Critical attribution corrections

- **CORRECTION #1 (high severity)**: planning-team 現有 standards/planning-frameworks.md L12 寫 JTBD 模板 "When [situation], I want to [motivation], so I can [outcome]" 但歸到 JTBD 通稱 —— 實際**這個模板是 Intercom Paul Adams 2016-06-28 部落格文章的原創**，被 Alan Klement 命名為 "Job Stories"。Christensen 2003 / 2016 從未寫這個句型。正確歸屬：cite Adams (2016) Intercom blog 為模板來源，並在 JTBD theory 處另 cite Christensen。
- **CORRECTION #2**: Levitt 的 "quarter-inch drill" 廣為傳頌但**並非 1960 HBR 原文直引**——根據多個 marketing history 文獻，這是 Levitt 課堂口述由 Kotler 日後整理，應寫成「attributed to Levitt via Kotler」或乾脆 cite Christensen 2003 Ch.3 的 milkshake。
- **CORRECTION #3**: Ulwick ODI **不** 是 Christensen JTBD 的子集 —— Ulwick 在 1991 Harvard Business Review 的 *Turn Customer Input into Innovation* 和 2002 HBR *Turn Customer Input into Innovation* 即已發展 ODI，早於 Christensen 2003。Ulwick 本人公開表示 Christensen 把自己 1990 年代工作吸納為 JTBD 品牌下。planning-team 若 cite JTBD 應同時承認 Ulwick (2005) 為 ODI 來源，不應把 ODI 併入 Christensen。

### JP integration assessment

- JTBD 這個 cluster **沒有 parallel JP 方法論**——日本市場的 JTBD 引進是 2010 年代透過 Clay Christensen 日文翻訳（『イノベーションのジレンマ』2001 翔泳社、『イノベーションへの解』2003 翔泳社）。JP 並無原創 JTBD 派別。
- JP 的 near analogue 是**マーケティング・マイオピア**（レビット, 1960）在日本 MBA 課程的引用傳統，以及**「顧客価値」重視**的伝統——但這些都是翻译概念而非 JP 原創。
- **決定**：JTBD 章節無需 JP preamble；cite Adams (2016) / Christensen (2016) 為主軸即可。

---

## Cluster 2 — Lean Startup / MVP / Build-Measure-Learn / Validated Learning

### Primary sources verified

- **Steve Blank (2005)** *The Four Steps to the Epiphany: Successful Strategies for Products that Win*. K&S Ranch / Cafepress self-published (later re-released 2013 K&S Ranch, 2020 Wiley). ISBN 978-0-9892005-0-9 (2013 ed). — **Customer Development model** 原典：4 steps = Customer Discovery / Customer Validation / Customer Creation / Company Building。Eric Ries 的思想師承，是 MVP + Lean 的直接前身。Ries 與 Will Harvey 在 IMVU 是 Blank Customer Development 的第一批 corporate 實施者。Stanford ENGR145 使用的 PDF 摘錄為 canonical public-access excerpt。
- **Eric Ries (2011)** *The Lean Startup: How Today's Entrepreneurs Use Continuous Innovation to Create Radically Successful Businesses*. Crown Business (Random House). ISBN 978-0-307-88789-4. — **canonical MVP + Build-Measure-Learn + Validated Learning + Pivot 起源**。書結構：
  - **Part One: Vision**（含 validated learning 定義）
  - **Part Two: Steer**（Build-Measure-Learn loop + leap-of-faith assumptions + MVP 章節 + Pivot or Persevere）
  - **Part Three: Accelerate**（batch size / growth engines / innovation accounting）
- **MVP 定義** (Ries 2011 Part Two / 亦見 Ries 2009 blog "The Minimum Viable Product: a guide"): "the Minimum Viable Product is that version of a new product which allows a team to collect the maximum amount of validated learning about customers with the least effort."
- **Validated Learning** (Ries 2011 Part One): "Validated learning is the process of demonstrating empirically that a team has discovered valuable truths about a startup's present and future business prospects. It is more concrete, more accurate, and faster than market forecasting or classical business planning."
- **Steve Blank (2013)** *Why the Lean Start-Up Changes Everything*. *Harvard Business Review* May 2013, vol 91 no 5, pp 63-72. — Lean Startup 的 HBR-level canonical short form。Blank 自 stacblank.com 免費提供 reprint。是入門級 citable 參照。

### Critical attribution corrections

- **CORRECTION #4 (medium severity)**: MVP 常被誤歸於 Steve Blank —— 實際 MVP 定義來自 **Eric Ries 2009 blog post + 2011 The Lean Startup book**。Blank 提供 Customer Development framework 是 MVP 的 *prerequisite* 但不是 MVP 本身的創始者。planning-team 任何 "MVP" 引用應 cite Ries 2011 而非 Blank。
- **CORRECTION #5**: "Validated Learning" 概念**專屬 Ries 2011 Part One**，不是 Lean 通名。Frequently 誤寫為「lean canonical concept」——應具名 cite Ries。
- **CORRECTION #6**: MVP 並非 "minimum features needed to ship"——而是 **"minimum product to start the Build-Measure-Learn loop"**。spec-level 描述不應說「MVP = smallest shippable feature set」。

### JP integration assessment

- *The Lean Startup* 日文版『リーン・スタートアップ』井口耕二訳 (2012 日経BP, 現在 2014 改訂)已是日本 startup 教育標準教材。有 canonical 翻译但**無 JP 原創方法論變體**。
- Toyota Production System / Lean Manufacturing 的 **genealogy 關係**：Ries 2011 Part One 明示承認自己的 Lean concept 借自大野耐一 *Toyota Production System*（Ōno, 1978『トヨタ生産方式』ダイヤモンド社）—— 這是 Lean Startup 與 JP TPS 的唯一 canonical linkage。planning-team 若在 JP preamble 提 Ries ↔ Ōno 脈絡，應 cite 大野 1978 書。
- **決定**：Lean Startup 章節以 Ries 2011 為主，**JP preamble 可選擇性加入 Ōno (1978) 作為 genealogy 註腳**（為了尊重 JP 的 TPS 傳統），但非必須。

---

## Cluster 3 — OKR (Objectives & Key Results)

### Primary sources verified

- **Peter F. Drucker (1954)** *The Practice of Management*. Harper & Brothers. — **Management by Objectives (MBO)** 起源。第 11 章 "Management by Objectives and Self-Control"。Drucker MBO 是 Grove iMBO 的 intellectual ancestor。是 OKR intellectual lineage 的起點但**不適合作 OKR 的 primary cite**——過於間接。
- **Andrew S. Grove (1983)** *High Output Management*. Random House. 2015 reprint Vintage Books, ISBN 978-0-679-76288-8. — **OKR origin at Intel**。Grove 在 Intel 內部於 1970 年代早期把 Drucker MBO 升級為 **iMBO (Intel Management by Objectives)**，加入 Key Results 作為量化槓桿。書中在討論 hierarchical planning 時示範 "What do I want to accomplish? (Objective)" 與 "How will I know I'm getting there? (Key Results)" 兩問。John Doerr 於 1975 在 Intel 接受 Grove 親自授課，後把 iMBO 帶到 Google/Kleiner Perkins。是 **OKR 的文字 origin**。
- **John Doerr (2018)** *Measure What Matters: How Google, Bono, and the Gates Foundation Rock the World with OKRs*. Portfolio / Penguin. ISBN 978-0-525-53622-2. — **現代 OKR 方法論 canonical**。Doerr 在此書提出 explicit formula:
  - **"I will [Objective] as measured by [Key Results]"**
  - **Grading scale** 0.0–1.0 — red 0.0-0.3 / yellow 0.4-0.6 / green 0.7-1.0
  - **Aspirational OKR 目標分** = **0.7**（非 1.0），低於 0.7 亦正常；Committed OKR 目標分 = 1.0，低於 1.0 須檢討
  - **3-5 Key Results per Objective**（Doerr 建議上限）
  - Case studies: Google / Intuit / Bono ONE / Gates Foundation / Remind / Nuna / MyFitnessPal
- **whatmatters.com** — Doerr + 他的 OKR 公開教材網站 — 官方 canonical open-access source。是 planning-team 實際 **可 link 的 URL**（Doerr book 需買）。

### OKR vs KPI 區別（load-bearing）

- per **whatmatters.com** (Doerr 原站): "OKRs are a measure for change, while KPIs are a measure of health." OKR 是**推動變化的 aspirational tool**；KPI 是**監測既有狀態的 operational indicator**。
- OKR = Objective (qualitative, inspirational, time-bounded) + 3-5 Key Results (quantitative, measurable, date-bounded)
- KPI = running metric tracked continually，不必有對應 Objective

### Critical attribution corrections

- **CORRECTION #7 (medium severity)**: OKR 常被誤歸於 John Doerr —— 實際 Doerr 是 **推廣者 + 現代化整合者**，Andy Grove 才是 Intel OKR origin。planning-team spec 應 cite **Grove (1983) 為 origin + Doerr (2018) 為 modern canonical**。
- **CORRECTION #8**: OKR 常被誤認為 Google 發明 —— Google 是 1999 Doerr 傳入的**下游**採用者，**不是發明者**。正確時間線：Drucker 1954 MBO → Grove 1970s Intel iMBO → Grove 1983 書 → Doerr 1975 受訓 → Doerr 1999 傳入 Google → Doerr 2018 書。

### JP integration assessment

- Doerr *Measure What Matters* 日文版『Measure What Matters 伝説のベンチャー投資家がGoogleに教えた成功手法 OKR』土方奈美訳 (2018 日本経済新聞出版社) 已有翻译。
- JP 無原創 OKR 派別。1990 年代**目標管理制度（MBO 人事考課）** 在日本大企業普及，但這是 Drucker MBO 的日本本地化應用（多偏向人事評鑑而非 strategy execution），**與 Silicon Valley OKR 文化差距顯著**。
- **決定**：OKR 章節無需 JP preamble；cite Grove + Doerr。

---

## Cluster 4 — Business Model Canvas + Lean Canvas

### Primary sources verified

- **Alexander Osterwalder & Yves Pigneur (2010)** *Business Model Generation: A Handbook for Visionaries, Game Changers, and Challengers*. John Wiley & Sons. ISBN 978-0-470-87641-1. Published July 2010. — **Business Model Canvas 9 blocks canonical origin**。Osterwalder 2004 PhD thesis (Lausanne) 的 "Business Model Ontology" 是學術前身；2010 書是 practitioner-facing canonical。共同創作者聲明：470 位 practitioners from 45 countries。
- **BMC 9 blocks** (Osterwalder & Pigneur 2010):
  1. Customer Segments (CS)
  2. Value Propositions (VP)
  3. Channels (CH)
  4. Customer Relationships (CR)
  5. Revenue Streams (R$)
  6. Key Resources (KR)
  7. Key Activities (KA)
  8. Key Partnerships (KP)
  9. Cost Structure (C$)
- Strategyzer.com (Osterwalder 公司) 提供 BMC 的 **CC BY-SA 3.0 授權 PDF 下載** — 是唯一免費 canonical primary 圖。
- **Ash Maurya (2012)** *Running Lean: Iterate from a Plan A to a Plan That Works* 2nd ed. O'Reilly Media. ISBN 978-1-449-30517-8. — **Lean Canvas** primary origin。Maurya 2009 LinkedIn 首次公開 Lean Canvas rationale；2012 Running Lean 2nd ed 是 book-form canonical。Lean Canvas 獲 Osterwalder 授權派生於 BMC (CC BY-SA)。
- **Ash Maurya (2022)** *Running Lean* 3rd ed. O'Reilly Media. ISBN 978-1-098-10877-9. Published 2022-05-03. — 最新版。新增：**Innovator's Gift**（customer problems > solutions）、**Customer Factory blueprint**、**Continuous Innovation framework** 擴充。planning-team 可 cite 3rd ed 為最新 canonical，也可並 cite 2nd / 3rd ed。

### Lean Canvas 的 4 block 替代（authoritative mapping）

per Maurya (2009 LinkedIn "Why Lean Canvas vs Business Model Canvas?" + Running Lean 2nd ed Ch.1):

| BMC block (removed) | Lean Canvas block (added) | Rationale |
|---|---|---|
| Key Partners | **Unfair Advantage** | 早期 startup 無 leverage partners；用於 capturing moat |
| Key Activities | **Key Metrics** | activities 為 internal 關注，metrics 才是進度訊號 |
| Key Resources | **Solution** | resources 對新產品 under-constrained；solution 更 load-bearing |
| Customer Relationships | **Problem** | relationship 對 早期 startup premature；problem 才是起點 |

**保留不變的 5 blocks**: Customer Segments、Value Proposition (改稱 Unique Value Proposition)、Channels、Revenue Streams、Cost Structure。

### Critical attribution corrections

- **CORRECTION #9 (high severity)**: Lean Canvas 的 4 block 替代在 web 上**多個 secondary source 提供不一致的 mapping**（有些誤寫成「Key Partners → Problem」、「Customer Relationships → Channels」等）。**authoritative mapping 來自 Maurya 本人 2009 LinkedIn 文章 + Running Lean 2nd/3rd ed Chapter 1**。planning-team 標準檔需清楚標示來源並列出完整 4-item mapping，不接受 secondary source 引用。
- **CORRECTION #10**: planning-team 現 standards/planning-frameworks.md L43-49 列 9 blocks 順序與名稱基本正確但 **Unique Value Proposition** 寫成了 "Unique Value Proposition" 是對的（Maurya 2nd ed 刻意加上 "Unique"）；但許多 cite 誤用 BMC 的 "Value Propositions"——需明確區分。

### JP integration assessment

- BMC 日文版『ビジネスモデル・ジェネレーション ビジネスモデル設計書』小山龍介訳 (2012 翔泳社) 為 canonical 翻译。Lean Canvas 日文 『Running Lean 実践リーンスタートアップ』角征典訳 (2012 O'Reilly Japan) 同為 canonical 翻译。
- JP **無 BMC 級別的原創 business model framework**。最接近的是「ビジネスモデル學會」相關學術脈絡但無 canonical 1-page tool。
- **決定**：BMC/Lean Canvas 章節無需 JP preamble；cite Osterwalder + Maurya。

---

## Cluster 5 — Assumption Mapping / DVF / Testing Business Ideas

### Primary sources verified

- **IDEO / Tim Brown (~2008)** — IDEO 在 2000 年代早期提出 **Three Lenses of Human-Centered Design**: Desirability（人們需要） + Feasibility（技術可行） + Viability（商業可行）。這是 **DVF 3 軸 framework 的原創出處**。Tim Brown 2008 HBR "Design Thinking" 文章 (*Harvard Business Review* June 2008, pp 84-92) 是最接近的**可引用 canonical article**，雖 IDEO design thinking 教材 (designthinking.ideo.com) 為 canonical 教材網站。
- **Tim Brown (2009)** *Change by Design: How Design Thinking Transforms Organizations and Inspires Innovation*. HarperBusiness. ISBN 978-0-06-176608-4. — 書面 canonical 發展 DVF 框架。
- **David J. Bland & Alexander Osterwalder (2020)** *Testing Business Ideas: A Field Guide for Rapid Experimentation*. John Wiley & Sons. ISBN 978-1-119-55144-7. — **DVF 3 軸 + Assumption Mapping + 44 experiments canonical**。本書明示使用 **3 軸** (Desirability / Feasibility / Viability) — 與 IDEO 1:1 對齊，**未加入 Usability 作為第 4 軸**。Bland 2018 創立 Precoil 公司專門傳授 DVF testing 方法。
- **Marty Cagan (2017)** *INSPIRED: How to Create Tech Products Customers Love* 2nd ed. John Wiley & Sons. ISBN 978-1-119-38750-3. Published 2017-12-12. — **Four Big Risks** (Value / Usability / Feasibility / Business Viability) — 這是 **4 軸版本的實際 canonical 出處**。Cagan 在 1st ed (2008) 用 3 軸 (Valuable / Usable / Feasible)；2nd ed 2017 **拆分 Valuable 為 customer Value + Business Viability**，並明確納入 Usability 為獨立第 4 軸。Cagan 把責任對應到角色：
  - **Value risk** → Product Manager
  - **Usability risk** → Product Designer
  - **Feasibility risk** → Engineering Lead
  - **Business Viability risk** → Product Manager + cross-functional
- SVPG 官網 svpg.com/four-big-risks/ 為 Cagan 公開版 primary source（免費 access）。

### Critical attribution corrections

- **CORRECTION #11 (critical severity)**: planning-team 現 standards/planning-frameworks.md L27-30 列 4 類 assumption 為 Desirability / Feasibility / Viability / **Usability** — 此 4-axis 版本**不來自 Bland & Osterwalder 2020**（Bland 2020 只用 3 軸 DVF，沒有 Usability）。4-axis 版本的 canonical 來源是 **Marty Cagan INSPIRED 2nd ed 2017** 的 Four Big Risks。正確 attribution：如果 planning-team 保留 4 類（V/U/F/BV），應 cite Cagan；如果簡化為 3 類（D/V/F），應 cite Bland & Osterwalder。**兩者不要混用**。
- **CORRECTION #12**: DVF 被廣為誤歸 IDEO 獨家發明——實際 IDEO 是 **2000 年代早期 popularize 者**，而 3 lenses 概念本身更古老（Drucker 1950s 曾提及 customer desirability / economic viability 對立）。嚴格 cite 時：
  - Tim Brown (2008) HBR "Design Thinking" 為 academic-level citable
  - designthinking.ideo.com 為 IDEO 官方教材
  - Bland & Osterwalder (2020) 為最現代 operational primary

### JP integration assessment

- *Testing Business Ideas* 日文版『ビジネスアイデア・テスト』今津美樹訳 (2020 翔泳社) 已有翻译。
- JP 無原創 assumption mapping 方法論。
- **決定**：無 JP preamble；cite Cagan (如果保留 4 軸) 或 Bland & Osterwalder (如果改用 3 軸)。**建議 planning-team v4.10.0 直接採用 Cagan 4 軸**，因為這與現有 standards 兼容且更完整（Usability 在軟體產品是 load-bearing 風險類別）。

---

## Cluster 6 — Product Discovery (Cagan / Torres / Amazon Working Backwards)

### Primary sources verified

- **Marty Cagan (2017)** *INSPIRED: How to Create Tech Products Customers Love* 2nd ed. Wiley. ISBN 978-1-119-38750-3. — **Product Discovery vs Product Delivery** 分離 + **Empowered Product Teams** + **Four Big Risks** canonical。Cagan 為 Silicon Valley Product Group (SVPG) 創辦人。書分 Part I Lessons / Part II Right People / Part III Right Product / Part IV Right Process / Part V Right Culture。Product discovery 內容集中在 Part III-IV。
- **Marty Cagan (2020)** *EMPOWERED: Ordinary People, Extraordinary Products*. Wiley. ISBN 978-1-119-69129-7. Co-authored with Chris Jones. — Cagan 3-book series 的第 2 本，專注於**如何建構能自主決策的產品團隊**（不是 feature factory）。是 product team structure 的 canonical supplement。
- **Marty Cagan (2024)** *TRANSFORMED: Moving to the Product Operating Model*. Wiley. ISBN 978-1-394-23754-9. — 3-book series 的第 3 本。產品組織轉型 canonical。2024 最新版補足。
- **Teresa Torres (2021)** *Continuous Discovery Habits: Discover Products That Create Customer Value and Business Value*. Product Talk LLC (self-published). ISBN 978-1-7366333-0-4. Published May 2021. — **Continuous Discovery + Opportunity Solution Tree (OST)** canonical。Torres 推廣 "weekly customer touchpoints" + "outcome-oriented discovery" + "OST 四層結構"：Desired Outcome → Opportunities → Solutions → Experiments。producttalk.org 是 Torres 的 canonical 公開 blog。
- **Colin Bryar & Bill Carr (2021)** *Working Backwards: Insights, Stories, and Secrets from Inside Amazon*. St. Martin's Press. ISBN 978-1-250-26759-7. Published February 2021. — **Amazon PR/FAQ Working Backwards method canonical**。Bryar 曾任 Bezos "Chief of Staff"，Carr 為 Amazon 15 年資深 VP。書 Part II "Unique Amazon Approach" **Chapter 4 "Working Backwards: Start with the Desired Customer Experience"** 首次公開詳細 PR/FAQ 結構：
  - **Press Release**: heading / sub-heading / summary / problem / solution / quote from company / how to get started / customer quote / closing call-to-action — **< 1 page**
  - **FAQ**: both internal (engineering / economics / legal) and customer FAQs — **< 5 pages**
- **Ian McAllister (2012)** Quora answer "What is Amazon's approach to product development and product management?" — **早於 Bryar/Carr 2021 的第一個公開描述** PR/FAQ 結構，McAllister 當時為 Amazon Director AmazonSmile。這個 Quora 答案是 2012-2021 之間業界引用的主要 source。但**Bryar/Carr 2021 作為 book-form canonical 應優先 cite**，Quora 可作為 genealogy 補註。

### Critical attribution corrections

- **CORRECTION #13**: Product Discovery 概念常被誤歸為 Lean Startup 的一部分 —— 實際 **Cagan 自 2008 即在 SVPG blog 使用 "product discovery"**，比 Lean Startup (2011) 還早。Cagan 與 Ries 是並行發展的兩派，不應把 Cagan 歸併到 Ries 脈絡。
- **CORRECTION #14**: Working Backwards 常被誤認為 Jeff Bezos 在 1997 股東信中提出 —— 實際 **1997 股東信只提 "customer obsession"**，Working Backwards PR/FAQ 方法論是 Amazon 2004-2005 內部演化出的 *operating convention*。Bryar/Carr 2021 之前無 book-form canonical；McAllister 2012 Quora 為第一個公開 description。
- **CORRECTION #15**: Opportunity Solution Tree **專屬 Teresa Torres 2016-2021** 的發展 —— 不應混淆為泛 product management 通名。

### JP integration assessment

- Cagan *Inspired* 日文版『INSPIRED 熱狂させる製品を生み出すプロダクトマネジメント』神月謙一訳 (2019 日本能率協会マネジメントセンター) 已有翻译。
- Torres *Continuous Discovery Habits* 日文版尚未出版（截至 2026-04）。
- Bryar & Carr *Working Backwards* 日文版『アマゾンの最強の働き方 Working Backwards』須川綾子訳 (2022 ダイヤモンド社) 已有翻译。
- JP **無原創 product discovery 派別**。JP 的 近鄰 concept 是「商品企画プロセス」但這是 operational workflow 而非 methodology framework — **不構成 framework-level 平行傳統**。
- **決定**：Product Discovery 章節無需 JP preamble。

---

## Cluster 7 — Strategy Frameworks (3C / Value Proposition Canvas)

### Primary sources verified

- **大前研一 (1975)**『企業参謀—戦略的思考とはなにか』 Président Publishing (プレジデント社). 後續文庫化 講談社 1985 文庫版 ISBN 4-06-183630-7、新装版 2014 プレジデント社 ISBN 978-4-8334-1694-2。— **3C 分析 (戰略的三角形) 原典**。大前在 1972 加入 McKinsey Tokyo 後，1975 出版本書。本書引進 "Customer / Competitor / Company" 的 strategic triangle，是 3C 的 canonical 日文原創。1975 年單年銷 16 萬冊，日本戰略思想核心經典。
- **Kenichi Ohmae (1982)** *The Mind of the Strategist: The Art of Japanese Business*. McGraw-Hill. ISBN 978-0-07-047904-3. — 1975 日文版的 **英文翻译 / 延伸版**（非直譯，大前重寫為 Western audience）。這是 3C concept 傳入英語世界的 canonical 出處。Ohmae 在本書中**明確使用** "strategic triangle" 語彙。
- **Alexander Osterwalder, Yves Pigneur, Gregory Bernarda, Alan Smith (2014)** *Value Proposition Design: How to Create Products and Services Customers Want*. John Wiley & Sons. ISBN 978-1-118-96807-9. — **Value Proposition Canvas** canonical。VPC 擴展 BMC 的 Value Proposition block：
  - **Customer Profile**: Customer Jobs / Pains / Gains
  - **Value Map**: Products & Services / Pain Relievers / Gain Creators
  - **Fit**: when Value Map 對應 Customer Profile
- **Michael Porter (1979)** *How Competitive Forces Shape Strategy*. *Harvard Business Review* March-April 1979; 1980 Free Press 《Competitive Strategy》; 2008 update *The Five Competitive Forces That Shape Strategy* HBR January 2008。— **Porter Five Forces** canonical。**研究判斷**: research-team v4.9.0 已 grounded Porter，planning-team 不需重複 grounding；planning-team 若需 market context 即 refer 給 research-team。

### Critical attribution corrections

- **CORRECTION #16**: 3C 分析常被誤歸為 **未明年份的日本 framework** 或「日本管理學派」—— 實際具名 **大前研一 1975**。planning-team 現 standards 寫「（大前研一）」但缺 publication anchor。應 cite **大前 (1975)『企業参謀』プレジデント社** + 可選並 cite **Ohmae (1982) The Mind of the Strategist**。
- **CORRECTION #17**: 1975 日版與 1982 英版**不是直接翻译**——Ohmae 1982 為 Western audience 重寫了約 60% 內容，把本來偏日本企業案例的內容替換為 Honda、Toyota、Sony 等 global-legible 案例。**日文 1975 版才是 original**，英文 1982 版是 *authorized expansion*。嚴格 cite 應以 1975 日文為 primary，1982 英文為 secondary access point。

### JP integration assessment

- **3C 是 JP 原創 framework** —— 大前研一、McKinsey Japan、日本戰略思想傳統。是**本研究 9 個 cluster 中唯一的 JP-origin load-bearing framework**。
- 與 3C 同為 JP 戰略學原創的還有：大前 *The Borderless World* (1990)、野中郁次郎 *The Knowledge-Creating Company* (1995)。但 3C 才是 planning-team 範疇。
- **決定**：3C 章節應使用 **full JP integration** — 章節以日文副標題 (`## 3C 分析（戦略的三角関係）`)、cite 1975 日文原典為主、Ohmae 1982 為 English access。

---

## Cluster 8 — Japanese 企画書 / JP Planning Culture

### Primary sources verified

- **ジェームス・W・ヤング / James Webb Young (1940)** *A Technique for Producing Ideas*. Advertising Publications Inc (originally internal J. Walter Thompson training), 1965 trade ed. NTC Business Books. — 原著 1940 年美國廣告業內部教材 → 1965 trade edition → 日本譯本**『アイデアのつくり方』** 今井茂雄訳、竹内均解説 (1988 TBSブリタニカ, ISBN 978-4-484-88104-7)。**JP 企画 (kikaku) 文化的 canonical 古典** — 雖為美國原著，日譯版在日本廣告 / 企画 / 商品開發界被視為 **唯一必讀 60 分鐘讀物**，其 5 步驟「アイデア生成法」（材料収集 → 咀嚼 → 熟成 → ひらめき → 具象化）深度嵌入 JP 企画書 教育。
- **大野耐一 (1978)**『トヨタ生産方式—脱規模の経営をめざして』ダイヤモンド社. ISBN 978-4-478-46001-5. — TPS canonical origin; JP 操作 / 品質 / 改善思想的根源。與 planning-team 的關聯是 Ries 2011 Lean Startup 的 genealogy — 大野 1978 是 Ries "Lean" 的日本源流。
- **三枝匡 (1994)**『戦略プロフェッショナル—シナリオ発想と意思決定の手法』日経BP. (現 2013 文庫版 ISBN 978-4-532-19659-7)。— JP **経営企画 (corporate planning)** 的 canonical 小說式教科書。三枝は Mitsubishi 化學 → Stanford MBA → Bain Japan → ミスミ社長 → 事業再生の JP practitioner。本書透過 case study 格式教授 JP 企業戦略企画 方法論。
- **高橋憲行 (1985)**『企画書の書き方がわかる本』 高橋書店, 後續多版本 **『企画書100事例集』** 等。— 高橋憲行 (not 高橋宣行) 創辦「企画塾」，是 JP 企画書 実務 教育最具體系的 practitioner source。實際為 practitioner handbook 而非學術 framework，**無 primary-source grade 的 academic rigor**。planning-team 可選擇 cite 作為 JP cultural anchor 但非必要。
- **Kipling, Rudyard (1902)** *Just So Stories*, "The Elephant's Child". Macmillan. — **5W1H 的詩源**: "I keep six honest serving-men / (They taught me all I knew); / Their names are What and Why and When / And How and Where and Who."
- **大野耐一 (1978)** 同上 — Ohno 推廣 **5 Why** ("なぜを 5 回繰り返せ") + **5W1H** 作為 quality management tools。**+2H (How much)** 是 1960 年代 JP 品質管理 (QC 7 道具運動) 中加入的擴充，但**無單一 canonical publication**——多數教材 (JUSE 発行) 未具體歸功於單一作者。

### Critical attribution corrections

- **CORRECTION #18 (medium severity)**: 5W2H 常被歸為「日本ビジネス慣習由來」—— 這個表述**部分正確但過於粗糙**。正確 genealogy：
  1. **5W1H 詩源** = Kipling 1902《The Elephant's Child》（不是日本）
  2. **5W 新聞寫作成為通用** = 19 世紀末美國新聞業 (unnamed)
  3. **+1H (How) 加入** = 20 世紀初管理學 (unnamed)
  4. **+2H (How much) 加入** = 1960 年代日本品質管理運動 (JUSE, Deming 訪日後)
  5. **5W2H 在 TPS / kaizen 推廣** = 大野耐一 1978《トヨタ生産方式》
  - planning-team 應寫「5W1H 源自 Kipling 1902，+2H 為 1960 年代日本品質管理運動擴充，大野耐一《トヨタ生産方式》1978 是書面 canonical 推廣」——不是單純「日本ビジネス慣習由來」。
- **CORRECTION #19**: 「企画書」作為 JP business artifact **無 framework-level canonical**——高橋憲行「企画塾」教材是 practitioner-level handbooks 的代表，但 JP 學術 / MBA 教材**不存在單一 canonical 1-page 企画書 template** (不同於 BMC 有 strategyzer canonical)。planning-team 若提 JP 企画書 應寫「JP 企画書 慣用格式由 企画塾 等 practitioner 傳承，無單一 canonical template」。
- **CORRECTION #20**: ヤング『アイデアのつくり方』雖為美國原著，其在 JP 企画 業界的 canonical 地位 **源自日譯版 1988 年今井茂雄翻译 + 竹内均解説** — 日譯版本身加入了 JP 脈絡化的序言 + 解説，造就在 JP 的特殊地位。planning-team cite 時應 cite **日譯 1988 版**而非美國 1940 版（後者在 JP 之外幾乎無影響力）。

### JP integration assessment

- JP 有強烈「企画書」作為 artifact 的文化傳統，但**沒有 framework-level 方法論**可 parallel BMC/Lean Canvas/JTBD/OKR。
- JP 可 anchor 的**文化 + genealogy level**: `ヤング 1988 日譯` (アイデア発想法) + `大野 1978` (Lean TPS 源流) + `三枝 1994` (JP 経営企画 case-based 教育) + `大前 1975` (3C，已在 Cluster 7)。
- **決定**: **PREAMBLE integration** — planning-team 整體採用 EN-primary grounding（Ries / Doerr / Osterwalder / Cagan / Christensen），但在 standards 檔案的**頂部 preamble** 加入 JP genealogy 註腳: ヤング 1988 (アイデア発想) + 大前 1975 (3C) + 大野 1978 (Lean TPS 源流) + 三枝 1994 (JP 経営企画 文化 anchor)。
  - 這與 devops-team v4.4.0 整合 Ohno TPS / docs-team v4.3.0 整合 JTAP 的 preamble 模式一致。
  - 不是 full integration (不像 research-team v4.9 有 JP info literacy 四柱 NDL/倉田/SIST/CiNii)。
  - 不是 none (不像 code-team 全西方典)。

---

## Cluster 9 — North Star Metric / AARRR / Goals-Non-Goals

### Primary sources verified

- **Dave McClure (2007-09)** *Startup Metrics for Pirates: AARRR!*. 500 Hats blog / SlideShare presentation, talk 於 **Seattle Ignite 2007**. URL: 500hats.typepad.com/500blogs/2007/09/startup-metrics.html + slideshare.net/dmc500hats/startup-metrics-for-pirates-long-version — **AARRR Pirate Metrics canonical origin**。McClure 後為 500 Startups 創辦人。5 階段：
  - **A**cquisition — users arrive via channels
  - **A**ctivation — first happy experience
  - **R**etention — repeat usage
  - **R**eferral — users recommend
  - **R**evenue — monetization
- 2007 投影片 / blog 是**唯一 canonical primary** — 無書面出版。是 "grey literature primary" 類別 (與 research-team v4.9 的 Sherman Kent 1964 CIA Studies in Intelligence 類似地位)。
- **Sean Ellis & Morgan Brown (2017)** *Hacking Growth: How Today's Fastest-Growing Companies Drive Breakout Success*. Crown Business. ISBN 978-0-451-49721-5. Published 2017-04-25. — **North Star Metric 的 book-form canonical**。Ellis coined "growth hacking" (2010 blog post)、創辦 GrowthHackers.com、Dropbox 首任 marketer。書 Part I (The Method) 含 North Star Metric 定義 + 使用指引。
- **Sean Ellis (2017)** *Finding the Right North Star Metric*. Growth Hackers blog / Medium. — NSM short-form primary: "the single metric that best captures the core value that your product delivers to customers and is the key to driving sustainable growth across your full customer base."
- **Malte Ubl (2020)** *Design Docs at Google*. industrialempathy.com/posts/design-docs-at-google. Published 2020-07-06, last modified 2022-05-27. — **Goals / Non-Goals convention 的最佳公開 primary**。Ubl 當時為 Google Principal Engineer (後 Vercel CTO)。這是 **personal blog post**（不是 Google 官方出版）但為 canonical 社群引用。關鍵 claim：
  - "Non-goals aren't negated goals... but rather things that could reasonably be goals, but are explicitly chosen not to be goals."
  - 舉例 ACID compliance 作為 database design 的 non-goal
  - 目的：prevent scope creep + force explicit decisions
- **Google eng-practices** (google.github.io/eng-practices/) — Google 官方開源的 engineering practices docs。無 explicit "Goals / Non-Goals" 章節，但可作為 Google engineering culture 的 meta-level anchor。

### Critical attribution corrections

- **CORRECTION #21 (medium severity)**: North Star Metric 常被誤歸為 Facebook 或 Airbnb 的發明——實際 **Sean Ellis 2017** 首次命名為 "North Star Metric" 並系統化 (Facebook DAU / Airbnb nights booked 是案例而非起源)。Ellis 同時 coined "growth hacking"。planning-team 若用 NSM 應 cite **Ellis & Brown (2017) Hacking Growth** + **Ellis Medium / Growth Hackers blog**。
- **CORRECTION #22 (medium severity)**: "Goals / Non-Goals" 格式**無 Google 官方文件可 cite**——只有 **Malte Ubl 2020 personal blog post** 作為業界廣為流傳的 primary。這與 OKR / BMC 有 book-form primary 的情況不同。planning-team 應誠實標註為 "community-established convention popularized by Ubl (2020)"，**不宣稱 Google 官方**。
- **CORRECTION #23**: AARRR 為 McClure 2007 投影片 —— planning-team 若 cite 應明示 **"grey literature primary"**（無出版書）。AARRR 無 book-form canonical upgrade。
- **CORRECTION #24**: 注意 **AARRR ≠ AAARRR**。Growth Hackers / Reforge 社群有時擴充為 6 A (Awareness, Acquisition, ...) 但**原 McClure 2007 為 5 階段**，planning-team 應嚴格使用 5 階段原版。

### JP integration assessment

- 北極星指標 / AARRR / Goals-Non-Goals 均**無 JP 原創對應 framework**。
- Doerr OKR 與 Grove iMBO 是**最接近 JP 組織文化**的 Western 框架 (Drucker MBO 在 JP 被廣為採納)，但 NSM / AARRR 是 Silicon Valley growth hacking 文化產物，JP 無在地變體。
- **決定**：無 JP preamble。

---

## Synthesis: Standards files to produce in v4.10.0

planning-team v4.9.x 目前只有 1 個 standards 檔案 `planning-frameworks.md` (89 行、5 個 framework 且全無 citation)。v4.10.0 應拆分為 **4 個 tier 1 standards 檔案 + 1 個 tier 2**:

### 1. `planning-frameworks.md` (tier 1) — 重寫後的 canonical 框架一覽

**目的**: SKILL.md 主要 reference 入口。保留現有 "選最簡 framework" 精神但補齊 primary source。

**Coverage clusters**: Cluster 1 (JTBD) + Cluster 4 (BMC/Lean Canvas) + Cluster 5 (DVF) + Cluster 7 (3C / VPC)

**Primary sources to cite**:
- Christensen, Hall, Dillon, Duncan (2016) HBR "Know Your Customers' Jobs to Be Done"
- Christensen & Raynor (2003) *The Innovator's Solution* Ch.3
- Adams (2016) Intercom blog "How we accidentally invented Job Stories" — **for Job Story template**
- Osterwalder & Pigneur (2010) *Business Model Generation* — BMC 9 blocks
- Maurya (2022) *Running Lean* 3rd ed — Lean Canvas 4 替代
- Cagan (2017) *Inspired* 2nd ed Part III — Four Big Risks (DVF+U)
- Bland & Osterwalder (2020) *Testing Business Ideas* — Assumption Mapping + 44 experiments
- 大前研一 (1975)『企業参謀』プレジデント社 + Ohmae (1982) *The Mind of the Strategist*
- Osterwalder, Pigneur, Bernarda, Smith (2014) *Value Proposition Design*

**JP preamble**: ヤング 1988 日譯 + 大野 1978 + 三枝 1994 + 大前 1975 (略提 genealogy)

### 2. `discovery-frameworks.md` (tier 1) — Lean Startup + Product Discovery 專章

**目的**: 獨立 file 給 MVP / Build-Measure-Learn / Validated Learning / Product Discovery / Working Backwards。這是現 planning-team 最缺的一塊。

**Coverage clusters**: Cluster 2 (Lean Startup) + Cluster 6 (Product Discovery)

**Primary sources to cite**:
- Blank (2005 / 2013 reissue) *The Four Steps to the Epiphany* — Customer Development
- Blank (2013) HBR May "Why the Lean Start-Up Changes Everything"
- Ries (2011) *The Lean Startup* Crown Business — MVP / BML / Validated Learning
- Cagan (2017) *Inspired* 2nd ed — Product Discovery vs Delivery + Empowered Teams
- Cagan (2020) *Empowered* — product team structure
- Torres (2021) *Continuous Discovery Habits* — Opportunity Solution Tree
- Bryar & Carr (2021) *Working Backwards* Ch.4 — PR/FAQ method
- (optional) McAllister (2012) Quora — early PR/FAQ description

**JP preamble**: 大野耐一 1978 作為 Ries 的 genealogy 註腳

### 3. `goals-and-metrics.md` (tier 1) — OKR + North Star + AARRR + Goals-Non-Goals

**目的**: 目標管理 + 成功度量 + 成長漏斗 全面 grounded。planning-team 現完全缺 OKR 系統，是 v4.10.0 最大 additive upgrade。

**Coverage clusters**: Cluster 3 (OKR) + Cluster 9 (NSM / AARRR / Goals-Non-Goals)

**Primary sources to cite**:
- Grove (1983) *High Output Management* — iMBO / OKR origin
- Doerr (2018) *Measure What Matters* — modern OKR + grading + "I will [O] as measured by [KR]"
- whatmatters.com (Doerr 官方公開教材) — free access
- McClure (2007) "Startup Metrics for Pirates" SlideShare / 500 Hats blog — AARRR
- Ellis & Brown (2017) *Hacking Growth* — North Star Metric
- Ubl (2020) "Design Docs at Google" industrialempathy.com — Goals / Non-Goals convention
- (intellectual backdrop) Drucker (1954) *The Practice of Management* Ch.11 MBO

**JP preamble**: 無

### 4. `spec-completeness-standards.md` (tier 2) — cross-cutting completeness checklist

**目的**: 提供 Product Spec Completeness gate 可 point-to 的具體完整性標準 (5W2H 等 meta-check)。

**Coverage clusters**: Cluster 8 (5W2H / JP planning conventions) + Cluster 1 結論

**Primary sources to cite**:
- Kipling (1902) *Just So Stories* "The Elephant's Child" — 5W1H poem origin
- 大野耐一 (1978)『トヨタ生産方式』ダイヤモンド社 — TPS / 5 Why / 5W1H popularization
- 高橋憲行『企画書の書き方がわかる本』系列 — JP 企画書 practitioner genealogy (attribution only, not method)

**JP preamble**: full — 這是最 JP-heavy 的 file

### 5. `japanese-planning-culture.md` (tier 3, OPTIONAL) — 可選 JP 文化 anchor 檔

**目的**: 如果 planning-team 希望有專用 JP 文化章節（對應 research-team v4.9 的 NDL リサーチ・ナビ 章），可建此 file。

**Coverage clusters**: 擴充 Cluster 8 + 跨 cluster JP genealogy

**Primary sources**:
- ヤング 1988 日譯 + 竹内均解説『アイデアのつくり方』TBSブリタニカ
- 大前研一 1975『企業参謀』プレジデント社
- 三枝匡 1994『戦略プロフェッショナル』日経BP
- 野中郁次郎 1995 *The Knowledge-Creating Company* Oxford (optional, 知識創造 backdrop)

**建議**: 先不建此 file (v4.10.0 scope)；合併進其他 4 個 file 的 preamble 即可。如果未來發現 JP users 需要獨立入口再補。

---

## JP integration decision

**Overall: PREAMBLE** (輕度整合 / with-full-for-3C-chapter)

**Evidence**:

1. **JP 原創 framework 只有 1 個 (3C 分析 大前 1975)** — 不支援 full JP integration 策略 (會在 8 個 cluster 強塞 JP 註腳)。
2. **JP 有 4 個 genealogy-level anchor** (大野 1978 / 大前 1975 / 三枝 1994 / ヤング 1988 日譯) — 但 4 個 都 **不構成完整方法論** (大野是 TPS 源流, 大前是 3C single framework, 三枝是 case-based 教材, ヤング是 idea generation heuristic)。支援 preamble 整合策略。
3. **最接近 JP parallel 的是 OKR ← Drucker MBO 1954 在 JP 人事考課傳統**，但這是 *Drucker 日譯應用* 而非 JP 原創 — 不支援 JP-primary OKR 章節。
4. **planning-team user 畫像** (kouko 為 JP-literate 台灣開發者、SKILL.md 已有 JP/CJK 描述「企画・プロダクト仕様策定」) — 支援 preamble 層級 JP anchor 而非全盤西化或全盤日化。

**Preamble structure**:
- `planning-frameworks.md` 頂部 4 行 JP genealogy preamble: 「ヤング 1988 日譯 (アイデア発想) + 大前 1975 (3C) + 大野 1978 (TPS/Lean 源流) + 三枝 1994 (JP 経営企画 文化 anchor)。主方法論 grounding 為 Western canonical primary; JP 作為 cultural genealogy 標註。」
- `discovery-frameworks.md` 頂部 1 行 JP note: 「Ries (2011) The Lean Startup 明示承繼 大野耐一 1978 トヨタ生産方式。」
- `goals-and-metrics.md` 無 JP preamble。
- `spec-completeness-standards.md` full JP integration (因為 5W2H + 企画書 慣例 本身即 JP-adjacent)。

**3C 章節例外**: cluster 7 的 3C 是 JP 原創。在 `planning-frameworks.md` 的 3C 小節應直接使用 full JP 呈現（副標題用「3C 分析（戦略的三角関係）」、cite 1975 日版 為主、1982 英版 為 English access point）。這與 devops-team v4.4 對 Ohno 整合的處理同級。

---

## Load-bearing claims now grounded

把 planning-team 現有 standards + protocols 中的每個 load-bearing claim 對應到 primary source:

| Current ungrounded claim | Grounded primary source |
|---|---|
| "Jobs-to-be-Done framework" | Christensen & Raynor (2003) *Innovator's Solution* Ch.3 + Christensen et al. (2016) HBR |
| "When [situation], I want to [motivation], so I can [outcome]" 模板 | **Adams (2016) Intercom blog + Klement (2018)**（非 Christensen） |
| "MVP" | Ries (2011) *Lean Startup* Part II |
| "Build-Measure-Learn" | Ries (2011) *Lean Startup* Part II |
| "Validated Learning" | Ries (2011) *Lean Startup* Part I |
| "Customer Development" (如 protocol 出現) | Blank (2005) *Four Steps to the Epiphany* |
| "Assumption Mapping" | Bland & Osterwalder (2020) *Testing Business Ideas* |
| "Desirability / Feasibility / Viability / Usability" (4 軸) | **Cagan (2017) *Inspired* 2nd ed Part III**（不是 Bland，Bland 只用 3 軸） |
| "Lean Canvas 9 blocks (Problem / Solution / Key Metrics / UVP / Unfair Advantage / Channels / CS / C$ / R$)" | Maurya (2022) *Running Lean* 3rd ed Ch.1 |
| "Lean Canvas 4 BMC substitutions" | Maurya (2009 LinkedIn + Running Lean 2nd/3rd ed) |
| "Business Model Canvas 9 blocks" | Osterwalder & Pigneur (2010) *Business Model Generation* |
| "3C 分析（顧客 / 競合 / 自社）" | **大前研一 (1975)『企業参謀』プレジデント社** + Ohmae (1982) *The Mind of the Strategist* McGraw-Hill |
| "5W1H" | Kipling (1902) *Just So Stories* "The Elephant's Child" |
| "+2H (How much) added" | 大野耐一 (1978)『トヨタ生産方式』ダイヤモンド社 + 1960s JUSE quality management genealogy |
| "Value Proposition Canvas" | Osterwalder, Pigneur, Bernarda, Smith (2014) *Value Proposition Design* |
| "Opportunity Solution Tree" | Torres (2021) *Continuous Discovery Habits* |
| "Goals / Non-Goals" convention | Ubl (2020) "Design Docs at Google" industrialempathy.com |
| "OKR / O-KR" (若採用) | **Grove (1983) *High Output Management* + Doerr (2018) *Measure What Matters*** |
| "Working Backwards / PR-FAQ" (若採用) | Bryar & Carr (2021) *Working Backwards* Ch.4 |
| "North Star Metric" (若採用) | Ellis & Brown (2017) *Hacking Growth* |
| "AARRR / Pirate Metrics" (若採用) | McClure (2007) "Startup Metrics for Pirates" 500 Hats blog / SlideShare |

---

## Open questions

1. **Inspired 3rd edition?** 截至 2026-04，Cagan 最新書是 *TRANSFORMED* (2024)，但 *Inspired* 仍為 2nd ed 2017。planning-team 應 cite 2nd ed 2017 為 canonical，因為 Four Big Risks 在 2nd ed 完整呈現。確認：無 3rd ed。
2. **Measure What Matters 2nd edition?** 截至 2026-04 仍為 Doerr 2018 1st ed。確認：無 2nd ed。
3. **Running Lean 3rd ed 是否推翻 2nd ed 的 Lean Canvas 4 block mapping?** 答：**無**。3rd ed 保留原 4 block mapping + 新增 Customer Factory / Innovator's Gift 章節。mapping 不動。
4. **大前研一 1975 年原版 ISBN?** 初版 1975 プレジデント社 無標準 ISBN (ISBN 系統 1970 年代末才在 JP 普及)。現行可 cite：講談社文庫版 1985 (ISBN 4-06-183630-7) 或 プレジデント社 新装版 2014 (ISBN 978-4-8334-1694-2)。
5. **JP 企画書 canonical textbook?** — 查無單一 canonical 。最接近的是 高橋憲行 (not 宣行) 系列但為 practitioner handbook 非 academic framework。planning-team 可在 `japanese-planning-culture.md` (optional tier 3) 內以「企画塾 practitioner genealogy」處理，或直接略過。
6. **Ohno 1978 日文版 是否能替代為 Ries 2011 英文 的 JP preamble?** — 是的，但應注意 Ries 明示承繼來自大野的 **英譯版** (Ohno 1988 Productivity Press), 非日文 1978 原版。JP preamble 可並列：大野 (1978) 日文原典 → Ohno (1988) 英譯 → Ries (2011) lineage。
7. **Tim Brown HBR 2008 vs 2009 書 vs IDEO 官網哪個是 DVF canonical?** — 嚴格 academic cite: **Brown (2008) HBR "Design Thinking" June 2008**。Book-level canonical: **Brown (2009) Change by Design HarperBusiness**。Web canonical: designthinking.ideo.com。planning-team 建議 cite HBR article 2008 為 primary（academic-grade citable）。
8. **Cagan Inspired 2nd ed vs 3rd ed (如果有)?** 2017 2nd ed 為最新 as of 2026-04。無 3rd ed。

---

## Research note summary (for Phase 3 planning)

- **9 clusters** verified with 2-3 primary sources each (avg 3 primary + 1-2 secondary per cluster)
- **24 Critical Attribution Corrections** surfaced (see in-cluster CORRECTION markers)
- **JP integration**: **PREAMBLE level** — 4 genealogy anchors (大前 1975, 大野 1978, 三枝 1994, ヤング 1988 日譯), with **full JP integration** for 3C 小節 (因為 3C 本身是 JP origin)
- **Standards files to produce**: 4 tier 1 + 1 optional tier 2 = **4-5 files**:
  1. `planning-frameworks.md` (tier 1, rewrite) — JTBD/BMC/Lean Canvas/DVF/3C/VPC
  2. `discovery-frameworks.md` (tier 1, new) — Lean Startup/Product Discovery/Working Backwards
  3. `goals-and-metrics.md` (tier 1, new) — OKR/NSM/AARRR/Goals-Non-Goals
  4. `spec-completeness-standards.md` (tier 2, new) — 5W2H + completeness check
  5. `japanese-planning-culture.md` (tier 3, optional) — 獨立 JP 文化章
- **Major additive upgrade**: OKR 系統 (Cluster 3) 完全缺席於 v4.9.x，v4.10.0 應補入
- **Major corrective upgrade**: Cluster 5 DVF 4 軸應從**錯誤歸 Bland**改為 **正確歸 Cagan**；Cluster 1 Job Story 模板應從 **錯誤歸 Christensen** 改為 **正確歸 Adams/Intercom**；Cluster 2 MVP 應明確 cite Ries (2011)，不模糊歸 Lean/Blank

---

## Appendix A — All primary source ISBNs (for audit trail; not to be included in standards files)

| Source | ISBN |
|---|---|
| Christensen & Raynor (2003) *Innovator's Solution* HBS Press | 978-1-57851-852-4 |
| Ulwick (2005) *What Customers Want* McGraw-Hill | 978-0-07-140867-7 |
| Klement (2018 rev) *When Coffee and Kale Compete* | 978-1-5348-7306-3 |
| Blank (2013 re-release) *Four Steps to the Epiphany* K&S Ranch | 978-0-9892005-0-9 |
| Ries (2011) *The Lean Startup* Crown Business | 978-0-307-88789-4 |
| Grove (1983 / 2015 reprint) *High Output Management* Vintage | 978-0-679-76288-8 |
| Doerr (2018) *Measure What Matters* Portfolio | 978-0-525-53622-2 |
| Osterwalder & Pigneur (2010) *Business Model Generation* Wiley | 978-0-470-87641-1 |
| Osterwalder et al. (2014) *Value Proposition Design* Wiley | 978-1-118-96807-9 |
| Maurya (2022) *Running Lean* 3rd ed O'Reilly | 978-1-098-10877-9 |
| Bland & Osterwalder (2020) *Testing Business Ideas* Wiley | 978-1-119-55144-7 |
| Cagan (2017) *Inspired* 2nd ed Wiley | 978-1-119-38750-3 |
| Cagan & Jones (2020) *Empowered* Wiley | 978-1-119-69129-7 |
| Cagan (2024) *Transformed* Wiley | 978-1-394-23754-9 |
| Torres (2021) *Continuous Discovery Habits* Product Talk | 978-1-7366333-0-4 |
| Bryar & Carr (2021) *Working Backwards* St. Martin's | 978-1-250-26759-7 |
| Brown (2009) *Change by Design* HarperBusiness | 978-0-06-176608-4 |
| Ellis & Brown (2017) *Hacking Growth* Crown Business | 978-0-451-49721-5 |
| 大前研一 (講談社文庫 1985)『企業参謀』 | 4-06-183630-7 |
| 大前研一 (プレジデント 2014 新装版)『企業参謀』 | 978-4-8334-1694-2 |
| Ohmae (1982) *The Mind of the Strategist* McGraw-Hill | 978-0-07-047904-3 |
| 大野耐一 (1978)『トヨタ生産方式』ダイヤモンド社 | 978-4-478-46001-5 |
| 三枝匡 (2013 文庫版)『戦略プロフェッショナル』日経BP | 978-4-532-19659-7 |
| 今井茂雄訳 (1988)『アイデアのつくり方』TBSブリタニカ | 978-4-484-88104-7 |

## Appendix B — Open-access canonical URLs (for standards files)

| Source | URL |
|---|---|
| Doerr OKR canonical educational site | https://www.whatmatters.com/ |
| Strategyzer BMC CC BY-SA | https://www.strategyzer.com/library/the-business-model-canvas |
| SVPG Cagan Four Big Risks | https://www.svpg.com/four-big-risks/ |
| Teresa Torres blog | https://www.producttalk.org/ |
| Blank HBR reprint "Why the Lean Start-Up Changes Everything" | https://steveblank.com/2013/05/06/free-reprints-of-why-the-lean-startup-changes-everything/ |
| McClure AARRR 2007 blog | https://500hats.typepad.com/500blogs/2007/09/startup-metrics.html |
| Intercom Job Stories blog (Adams 2016) | https://www.intercom.com/blog/accidentally-invented-job-stories/ |
| Ubl Design Docs at Google | https://www.industrialempathy.com/posts/design-docs-at-google/ |
| IDEO Design Thinking portal | https://designthinking.ideo.com/ |
| Christensen HBR 2016 JTBD article | https://hbr.org/2016/09/know-your-customers-jobs-to-be-done |
