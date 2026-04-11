---
title: design-team 再設計研究 — Norman・Nielsen・WCAG・感性工学・安藤・黒須・OOUI
date: 2026-04-11
team: design-team
refactor_version: v4.8.0
tags: [research, domain-teams, design-team, grounding, jp-full-integration]
---

> **Backfill note** (2026-04-11, v4.8.0): This file was written
> during the design-team v4.8.0 grounding refactor (which is
> itself the first team to use the v4.7.0 in-repo research note
> convention). Authoring took place in the maintainer's Obsidian
> vault as Phase 2 of the skill-redesign protocol, then the
> finalized note was copied into the repo at
> `domain-teams/skills/design-team/research/grounding-v4.8.0.md`
> as the first action of Phase 3 per the v4.7.0 convention. The
> Obsidian copy remains in the maintainer's vault as a personal
> backup; the authoritative audit trail lives in this file.
>
> **Earlier frontmatter draft** tagged `refactor_version: v4.7.0`
> because v4.8.0 was the working-name-still-TBD version at the
> time Phase 2 research was initially saved; it is now updated
> to the final v4.8.0 version that ships this refactor.

# design-team 再設計研究

> [!info] 研究背景
> 為 design-team v4.7.0 重構執行 Phase 2 grounding research。Phase 1 gap assessment 找到 **12 個隱式被引用但無書誌的 JP 載重方法論**（已寫入 protocols / rubrics 作為結構性 SSOT）、**8 個未引用的 Anglo-American anchors**、**5 個 visual-gate.md 內的部落格 / Wiki 級反模式引用**。Phase 1 的 JP 整合判定為 **FULL（HIGH 信心）**，本 Phase 2 的任務是逐項驗證一手來源並產出 grounding plan。
>
> 研究方法：parallel EN + JP web search，全部 ISBN / 出版社 / 章節 / URL 經 WebFetch / WebSearch 驗證。未能驗證者明確標記「需使用者驗證」。

## TL;DR

| Point | Status |
|-------|--------|
| **Norman *Design of Everyday Things* Revised & Expanded Edition** (Basic Books 2013, 978-0465050659, **7 chapters**) — Ch.6「Design Thinking」与 Ch.7「Design in the World of Business」是 2013 新增；**signifiers 概念是 2013 版引入**（非 1988 原版） | `[事實|高]` |
| **Nielsen 10 Usability Heuristics** (1994 原始 / 1990 collab with Molich / 2024-01-30 last update) — 10 條名稱經官方頁驗證，「自 1994 以來核心未變，僅文字微調」 | `[事實|高]` |
| **WCAG 2.2** = W3C Recommendation **republished 2024-12-12**（原 2023-10-05），4 principles / 13 guidelines / 86 SC，Target Size (Minimum) 2.5.8 = **AA**，Target Size (Enhanced) 2.5.5 = **AAA**。**WCAG 3 仍是 Working Draft（2026-03 update）**，預計 2028 後才能成為 Recommendation | `[事實|高]` ⚠️ design-team 應 cite **WCAG 2.2 (2024-12-12 republish)**，并将 wcag-baseline.md 升级 |
| **Material 3 minimum touch target = 48dp x 48dp** （MD 3 Foundations / Compose `Modifier.minimumInteractiveComponentSize()` API 預設） — 對齊 WCAG 2.5.8 AA | `[事實|高]` |
| **Apple HIG iOS minimum tap target = 44 x 44 points** — Apple Developer「UI Design Dos and Don'ts」+ Buttons HIG 頁明文 | `[事實|高]` |
| **Garrett *Elements of UX* 2nd ed** (New Riders 2010, 978-0321683687) — 5 planes (Strategy / Scope / Structure / Skeleton / Surface)；**原始 diagram 是 2000 年發表，1st edition 2002，2nd edition 2010 加入 mobile/app 範圍** | `[事實|高]` |
| **Verganti *Design-Driven Innovation*** (Harvard Business Review Press 2009, **978-1422124826**) — meaning innovation + interpreters；**「意味のイノベーション」應引 Verganti，不是黒須** | `[事實|高]` |
| **Sophia Prater Object-Oriented UX** ALA 2015-10-20 — **原文 NOT contain ORCA 縮寫**；ORCA (Objects/Relationships/CTAs/Attributes) 是 Prater 後來在 OOUX 課程 / Medium / podcast 命名的；**第二篇 ALA 文章 "OOUX: A Foundation for Interaction Design" 2016-04-19 講 CTAs 但仍未含完整 ORCA**。**ORCA 應 cite Prater ooux.com，不是 ALA 2015** | `[事實|高]` ⚠️ 重要歸因修正 |
| **Gibson *Ecological Approach to Visual Perception*** (Houghton Mifflin **1979**, Routledge Classic Edition 2014 / **978-1848725782**) — affordance 原 primary。但 affordance 一詞 Gibson **早於 1966** 在 *The Senses Considered as Perceptual Systems* 已創；1979 是最完整論述 | `[事實|高]` |
| **Osgood, Suci, Tannenbaum *The Measurement of Meaning*** (University of Illinois Press 1957) — SD 法 + 三因子 (Evaluation / Potency / Activity) 一手 primary。design-team visual-gate.md L54「J-SEMS, J-STAGE, AIIT」應替換 | `[事實|高]` |
| **長町三生 感性工学** = **二手**: ① 長町三生《感性工学—感性をデザインに活かすテクノロジー》海文堂出版 1989 (978-4303713201) JP 原典 + ② Nagamachi (1995) "Kansei Engineering: A new ergonomic consumer-oriented technology for product development" *International Journal of Industrial Ergonomics* 15(1):3-11 EN peer-reviewed primary | `[事實|高]` |
| **深澤直人《デザインの輪郭》** TOTO 出版 2005-12-01, **978-4887062603**, 35-40 themed essays 含「Without Thought」「Design That Dissolves into Action」 — 「無意識のデザイン」一手 primary | `[事實|高]` |
| **安藤昌也《UXデザインの教科書》** 丸善出版 2016-06-20, **978-4621300374** — 4 期間モデル原始來源是 **Roto/Law/Vermeeren/Hoonhout (2011) "User Experience White Paper"** (Dagstuhl Seminar 10373)；安藤書 Section 2.2.4「体験の期間で異なって知覚される UX」介紹此模型。**ux-strategy-gate 應同時 cite UX White Paper + 安藤** | `[事實|高]` |
| **黒須正明《UX 原論—ユーザビリティから UX へ》** **近代科学社 2020-04-28** (NOT 2013, NOT KOKUSAI), **978-4764906112** — 含 **「四つの品質領域」（Ch.11.3）** = 客観的設計時 / 主観的設計時 / 客観的利用時 / 主観的利用時。**這是 4-quality 不是 3D quality**。「意味性」**NOT 出自黒須**，應從 ux-strategy-gate 拿掉、改 cite Verganti | `[事實|高]` ⚠️ 重大歸因修正 |
| **上野学《オブジェクト指向 UI デザイン—使いやすいソフトウェアの原理》** 技術評論社 2020-06-05, **978-4297113513**（ソシオメディア／上野学／藤井幸多 共著） — JP OOUI canonical primary | `[事實|高]` |
| **原研哉《デザインのデザイン》** 岩波書店 2003-10-22, **978-4000240055**（サントリー学芸賞）+ **《白》中央公論新社 2008-05-30, 978-4120039379**（白の美学 4 章構成）+ Lars Müller《Designing Design》2007 (978-3037781050) — 「白」「余白」「emptiness」一手 primary | `[事實|高]` |
| **Leonard Koren *Wabi-Sabi for Artists, Designers, Poets & Philosophers*** (Stone Bridge Press 1994, **978-1880656129**) — 西方 wabi-sabi as design concept 一手 primary | `[事實|高]` |
| **JIS Z 8530:2021 / ISO 9241-210:2019** — JIS Z 8530 已從 2019 版升級到 **2021 版**（2021-03 公開），對應 ISO 9241-210:2019。design-team 應 cite **ISO 9241-210:2019** 為國際 primary，**JIS Z 8530:2021** 為 JP localized 版 | `[事實|高]` |
| **磯崎新《建築における「日本的なもの」》** 新潮社 2003-04-30 (978-4104587018) — 「間 Ma」/「日本的空間」的學術 primary，可替換 KOGEI STANDARD 部落格引用 | `[事實|高]` |
| **JP 整合決定**: **FULL** — 12 個 JP 載重方法論（感性工学、無意識のデザイン、引き算、わびさび、間、佇まい、おもてなし、4 期間 UX、4 quality、OOUI、HCD、白）皆有獨立一手書誌。設計強度等同 qa-team v4.2 (VSTeP/HAYST/ゆもつよ) 或更深 | `[分析|高]` |
| **Anti-pattern 清理**: btrax「寿司職人 6 つの極意」/ KOGEI STANDARD / J-SEMS wiki / studio-tabi / Wikipedia 全部移除，改 cite Osgood 1957 / 磯崎新 2003 / 原研哉 2003 / Prater ooux.com / Verganti 2009 | `[行動|高]` |

---

# Cluster A — Anglo-American Canon

## Q1. Donald Norman *The Design of Everyday Things* — Revised & Expanded Edition

### 書誌（已驗證）

- **作者**: Donald A. Norman
- **標題**: *The Design of Everyday Things: Revised and Expanded Edition*
- **出版**: Basic Books (Hachette imprint), 2013-11-05
- **ISBN-13**: 978-0465050659
- **頁數**: 368
- **驗證來源**: [Don Norman 官方頁](https://jnd.org/books/the-design-of-everyday-things-revised-and-expanded-edition/), [Hachette Book Group](https://www.hachettebookgroup.com/titles/don-norman/the-design-of-everyday-things/9780465050659/?lens=basic-books), [Amazon](https://www.amazon.com/Design-Everyday-Things-Revised-Expanded/dp/0465050654)

### 章節結構（7 chapters，已驗證 from jnd.org）

| Ch | 標題 | 對 design-team 的相關性 |
|---|---|---|
| 1 | The Psychopathology of Everyday Things | affordances、signifiers、constraints、mappings、feedback |
| 2 | The Psychology of Everyday Actions | **7-stage action cycle**, gulfs of execution / evaluation |
| 3 | Knowledge in the Head and in the World | mental models, distributed cognition |
| 4 | Knowing What to Do: Constraints, Discoverability, and Feedback | physical / cultural / semantic / logical constraints |
| 5 | Human Error? No, Bad Design | error handling philosophy |
| **6** | **Design Thinking** | **(2013 新增)** double diamond, HCD process |
| **7** | **Design in the World of Business** | **(2013 新增)** product roadmap, business constraints |

加 Afterword/Acknowledgments + Readings and Notes + References。

### 1988 vs 2013 差異

- 原 1988 版書名是 *The Psychology of Everyday Things*（POET），1990 年再版改名 *The Design of Everyday Things*。
- **「signifiers」概念是 2013 版引入** — Wikipedia 與多個 reading guide 確認：「In the revised edition of his book in 2013, he also introduced the concept of signifiers to clarify his definition of affordances」。Gibson 的 affordance + Norman 後加 signifier 是兩個不同 layer：affordance 是「物理可能性」、signifier 是「設計者放置的可感知標誌」。
- 例子：門把上的金屬板（push 信號）vs 把手（pull 信號）— Norman 主張對設計師而言 signifier 比 affordance 更重要。
- 2013 版新增 Ch.6 Design Thinking + Ch.7 Design in the World of Business，example 全更新。

### JP 版

- 《誰のためのデザイン？ 増補・改訂版—認知科学者のデザイン原論》新曜社 2015-04，譯者：岡本明、安村通晃、伊賀聡一郎、野島久雄。
- 來源：[新曜社](https://www.shin-yo-sha.co.jp/book/b455574.html), [Amazon JP](https://www.amazon.co.jp/dp/4788514346)

### 對 design-team 的應用

- **Ch.1 affordances + signifiers** → ui-interaction-gate 的 Object Modeling section 應 ground 在此（取代 Without Thought 籠統表述）
- **Ch.2 7-stage action cycle + gulfs of execution/evaluation** → ui-interaction-gate 的 Interaction Patterns section 應 ground
- **Ch.5 Human Error? No, Bad Design** → a11y-checklist 的 Error Prevention 應補
- **Ch.6 Design Thinking** → 可作為 design-brainstorming 的 protocol anchor

---

## Q2. Jakob Nielsen 10 Usability Heuristics

### 書誌（已驗證 via WebFetch nngroup.com）

- **作者**: Jakob Nielsen（與 Rolf Molich 1990 collaboration → Nielsen 1994 因子分析精煉）
- **canonical URL**: https://www.nngroup.com/articles/ten-usability-heuristics/
- **首次發表**: 1994
- **最後更新**: 2024-01-30
- **驗證來源**: WebFetch 直接讀取 nngroup.com 頁面

### 10 條啟發法（exact canonical names from NN/g official page）

1. **Visibility of System Status**
2. **Match Between the System and the Real World**
3. **User Control and Freedom**
4. **Consistency and Standards**
5. **Error Prevention**
6. **Recognition Rather than Recall**
7. **Flexibility and Efficiency of Use**
8. **Aesthetic and Minimalist Design**
9. **Help Users Recognize, Diagnose, and Recover from Errors**
10. **Help and Documentation**

### 1994 vs 2020 / 2024 差異

- Nielsen 在 jakobnielsenphd.substack.com / uxtigers.com 自述：「the 10 heuristics themselves have remained relevant and unchanged since 1994」。
- 2020/2024 update 僅是文字、例子、related links 補充，**10 條核心未變**。
- 原始研究：1990 年 Nielsen + Molich，1994 因子分析 (factor analysis of 249 usability problems) → 取得最大解釋力的 10 條。

### 對 design-team 的應用

- 取代 a11y-checklist.md / ui-interaction-gate.md 內未引用的「heuristic-style」描述
- 「Error Prevention」「Help users recognize, diagnose, and recover from errors」可直接 cite Nielsen 5 + 9 → 對應 a11y-checklist 的 error 段
- 「Aesthetic and Minimalist Design」 #8 可作為 visual-gate 的 minimalism anchor（與 wabi-sabi / 引き算 並列）

---

## Q3. WCAG 2.2

### 標準（已驗證 via WebFetch w3.org）

- **狀態**: W3C **Recommendation**
- **首次發布**: 2023-10-05
- **republished**: 2024-12-12（最新更新）
- **canonical URL**: https://www.w3.org/TR/WCAG22/
- **結構**: 4 principles / 13 guidelines / **86 success criteria** / 3 conformance levels (A / AA / AAA)
- **驗證來源**: [W3C WAI WCAG 2 Overview](https://www.w3.org/WAI/standards-guidelines/wcag/), [WCAG 2.2 spec](https://www.w3.org/TR/WCAG22/)

### Success Criteria 等級驗證（已逐項從 W3C 確認）

| SC | 名稱 | 等級 |
|---|---|---|
| 1.4.3 | Contrast (Minimum) | **AA** |
| 1.4.11 | Non-text Contrast | **AA** |
| 2.1.1 | Keyboard | **A** |
| 2.4.7 | Focus Visible | **AA** |
| 2.5.5 | Target Size (Enhanced) | **AAA** |
| 2.5.8 | Target Size (Minimum) | **AA** |

> [!important] design-team baseline 應為 AA，且 wcag-baseline.md 應升级
> 目前 wcag-baseline.md L21 寫「Touch targets ≥ 44×44 CSS pixels」——這是 Apple HIG 的 pt 不是 WCAG 標準。
> WCAG 2.5.8 (AA) 規定 24×24 CSS pixels minimum；2.5.5 (AAA) 規定 44×44 CSS pixels。
> 設計上應 cite WCAG 2.5.8 為 AA baseline，44×44 是 AAA opportunity。
> wcag-baseline.md L46「Target size ≥ 24×24 CSS pixels」是 AAA opportunity 的描述位置 — 應對換：24×24 是 2.5.8 AA，44×44 是 2.5.5 AAA。

### WCAG 3.0 status (2026-04)

- 仍是 **Working Draft**，最新 update 2026-03-03（W3C WAI 公告 https://www.w3.org/WAI/news/2026-03-03/wcag3/）
- AG WG 預計 2026-04 公佈正式 timeline
- Candidate Recommendation 計劃 Q4 2027，**不會早於 2028 成為 Recommendation**
- 結論：**design-team 應繼續以 WCAG 2.2 為 grounding**，對 WCAG 3 加 Note on Future Track 即可

---

## Q4. Material Design 3 Touch Target

### 來源驗證

- **canonical URL**: https://m3.material.io/foundations/designing/structure (Foundations)
- **canonical wording**: 「Touch targets should be at least 48dp by 48dp and must be at least 24dp by 24dp」
- 對齊 WCAG 2.5.8 (AA) = 24×24 CSS px minimum + WCAG 2.5.5 (AAA) recommendation
- Compose API: `Modifier.minimumInteractiveComponentSize()` 預設 48dp×48dp
- **驗證來源**: WebSearch 確認多個 Android Developer 與 Material 文件交叉引用；m3.material.io 直接 fetch 受 JavaScript-only 阻擋，但 Material Components Android repo + cvs-health 公開文件均明文 48dp。

### Material 3 Component States（部分驗證）

- canonical states：**Enabled, Hover, Focused, Pressed, Dragged, Selected, Activated, Disabled, On, Off, Error**
- canonical URL: https://m3.material.io/foundations/interaction/states/applying-states
- 其中：
  - Enabled = 預設可互動
  - Hover = 指標 hover 上去
  - Focused = 鍵盤 focus（accessibility critical）
  - Pressed = 點擊瞬間 ripple
  - Dragged = 元素被拖移
  - Disabled = 不可互動
- ⚠️ **未能直接從 m3.material.io 完整 fetch（JavaScript-only 渲染）**，但 Material 2 (m2.material.io/design/interaction/states.html) + GitHub repo + 多個第三方教學交叉確認此清單。**標記為「需使用者最終驗證 m3 spec 頁」**。

### 對 design-team 的應用

- ui-interaction-gate.md 的「Missing component states」flag 應 cite Material 3 canonical states list
- Touch target 標準應拆 platform-aware：
  - WCAG 2.5.8 AA → 24×24 CSS px universal baseline
  - Material 3 → 48×48 dp Android
  - Apple HIG → 44×44 pt iOS

---

## Q5. Apple Human Interface Guidelines — Touch Target

### 來源驗證

- **canonical URL**: https://developer.apple.com/design/tips/ + https://developer.apple.com/design/human-interface-guidelines/buttons + Layout / Accessibility 子頁
- **canonical wording**: 「Controls should measure at least 44 points x 44 points so they can be accurately tapped with a finger」(UI Design Dos and Don'ts)
- 「a button needs a hit region of at least 44x44 pt to ensure that people can select it easily, whether they use a fingertip, a pointer, their eyes, or a remote」(Buttons HIG)
- **驗證來源**: WebFetch 直接從 developer.apple.com/design/tips/ 取得；Apple 官網 SPA 部分頁面 JS-only，但「Tips」靜態頁可讀。

### Platform 區分

- **44 pt × 44 pt** = **iOS / iPadOS** 規範（最廣泛引用）
- watchOS 與 macOS 有不同 size — 44pt 是 iOS canonical，不是 macOS
- Apple 同時要求按鈕 hit region 不只是 visible size，padding 也算

### 對 design-team 的應用

- ui-interaction-gate.md L37「Touch targets < 44pt (iOS) / 48dp (Android)」應 cite Apple HIG 「UI Design Tips」+ Material 3 Foundations
- **明確標示** 44pt 是 iOS / iPadOS，不是跨平台

---

## Q6. Jesse James Garrett *The Elements of User Experience*

### 書誌（已驗證）

- **作者**: Jesse James Garrett
- **標題**: *The Elements of User Experience: User-Centered Design for the Web and Beyond*
- **2nd Edition**: New Riders (Pearson), 2010-12-26
- **ISBN-13**: 978-0321683687
- **頁數**: 192
- **驗證來源**: [Pearson catalog](https://www.pearson.com/en-us/subject-catalog/p/Garrett-Elements-of-User-Experience-The-User-Centered-Design-for-the-Web-and-Beyond-2nd-Edition/P200000000272/9780321683687), [O'Reilly](https://www.oreilly.com/library/view/the-elements-of/9780321688651/), [jjg.net/elements](http://www.jjg.net/elements/)

### 5 Plane Model（已驗證 via Pearson sample chapter PDF）

| Plane | Concern | 對 design-team gate 對應 |
|---|---|---|
| **Strategy** | User needs × business objectives | ux-strategy-gate (戦略軸) |
| **Scope** | Functional requirements + content requirements | ux-strategy-gate (要件軸) |
| **Structure** | Interaction design + information architecture | ui-interaction-gate (構造) |
| **Skeleton** | Interface design + navigation design + information design | ui-interaction-gate (骨格) |
| **Surface** | Visual design | visual-gate (表層) |

### 出版歷史

- **2000**: Garrett 在 jjg.net 發表原始 diagram（PDF 仍可下載 http://www.jjg.net/elements/pdf/elements.pdf）
- **2002**: 1st edition (New Riders, ISBN 978-0735712027) — 主要 web-focused
- **2010**: 2nd edition (New Riders, ISBN 978-0321683687) — 擴大到 mobile / app / 「beyond the web」
- 一手 canonical cite：**2nd ed (2010)** + 原 diagram (jjg.net 2000)

### 對 design-team 的應用

- ux-strategy-gate.md L9「Each temporal phase is evaluated through two strategic lenses: 戦略 (Strategy) / 要件 (Scope)」**正確 cite Garrett**
- ui-interaction-gate.md L3「Garrett's 構造 (Structure) and 骨格 (Skeleton) layers」**正確 cite Garrett**
- visual-gate.md「表層」應該 cite Garrett (5 plane Surface) 為 ground

---

## Q7. Roberto Verganti *Design-Driven Innovation*

### 書誌（已驗證 via WebFetch HBR store）

- **作者**: Roberto Verganti
- **標題**: *Design-Driven Innovation: Changing the Rules of Competition by Radically Innovating What Things Mean*
- **出版**: Harvard Business Review Press, 2009-08-12
- **ISBN-13**: **978-1422124826** (Hardcover) / **978-1422136577** (alternate ISBN) — 兩個 ISBN 都有效
- **驗證來源**: [HBR Store](https://store.hbr.org/product/design-driven-innovation-changing-the-rules-of-competition-by-radically-innovating-what-things-mean/2482), [Verganti.com books](https://www.verganti.com/books/), [Amazon](https://www.amazon.com/Design-Driven-Innovation-Competition-Innovating/dp/1422124827)

### 3 核心概念

1. **Design-Driven Innovation** = 第三條 strategy（vs technology-push / market-pull）
2. **Radical innovation of meaning** vs incremental — 不改技術，改「物的意義」（Wii、iPod 範例）
3. **Interpreters** = 中介層（其他產業設計師、藝術家、雜誌、craftsmen、tech suppliers），不直接問顧客而是與這些 interpreter 對話

### JP 版

- 《デザイン・ドリブン・イノベーション》同友館，譯者佐藤典司・岩谷昌樹・八重樫文・立命館大学経営学部 DML
- 八重樫文 + 立命館 DML 在 2015 起與 Verganti 共同研究，是 JP 主要傳承
- 「意味のイノベーション」是日本譯界對 Verganti 的 standard 翻譯
- 來源：[Amazon JP](https://www.amazon.co.jp/dp/4496048795), [立命館 RADIANT](https://www.ritsumei.ac.jp/research/radiant/article/?id=78)

### 對 design-team 的應用 — 重大歸因修正

> [!warning] 「意味性 / meaningfulness」應 cite Verganti，不是黒須
> design-team ux-strategy-gate.md L42「意味性 (Meaningfulness): Hollow experience despite feature completeness」目前掛在「黒須 3D Quality Check」下 — **這是錯誤歸因**。
>
> 黒須的 4-quality 模型有「客観的設計時 / 主観的設計時 / 客観的利用時 / 主観的利用時」四象限（見 Q14），**沒有「意味性」這個維度**。
>
> 「meaningful experience」「意味のイノベーション」是 Verganti 2009 的 design-driven innovation 核心。
>
> **修正動作**：將 ux-strategy-gate.md L38-43 的「黒須 3D Quality Check」整段重寫為：
> - 「黒須 4-quality check」(四つの品質領域 from UX 原論 Ch.11.3) — 客観 / 主観 × 設計時 / 利用時
> - 「Verganti meaning check」 — 體驗是否帶來新的「意味」，而非僅功能完備

---

## Q8. Sophia Prater Object-Oriented UX / ORCA

### Article 1: "Object-Oriented UX" (ALA 2015) — 已驗證

- **作者**: Sophia V. Prater (then Sophia Voychehovski)
- **發表**: A List Apart, **2015-10-20**
- **canonical URL**: https://alistapart.com/article/object-oriented-ux/
- **issue number**: ALA does not display issue number on the article page；**Phase 1 gap report 標的「issue #530」需 user 確認，不能 fabricate**
- **內容**: 介紹 OOUX 哲學 + 4-step process: extract objects from goals → define core content → nest objects → forced ranking
- **重要**: **此原文 NOT contain ORCA 縮寫**（已 WebFetch 直接驗證）
- **驗證來源**: WebFetch alistapart.com 直接讀取

### Article 2: "OOUX: A Foundation for Interaction Design" (ALA 2016) — 已驗證

- **作者**: Sophia V. Prater
- **發表**: A List Apart, **2016-04-19**
- **canonical URL**: https://alistapart.com/article/ooux-a-foundation-for-interaction-design/
- **內容**: 引入 CTA Inventory 工具，討論 Objects + CTAs + Relationships
- **仍然 NOT 完整 ORCA**：本文加入 CTA 但仍未含 Attributes
- **驗證來源**: WebFetch alistapart.com

### ORCA 完整框架（已驗證）

- **canonical 出處**: ooux.com（Prater 自有 site / OOUX Masterclass / podcast / Medium）
- Prater 本人在 [Medium 文章](https://sophiavux.medium.com/in-the-approach-to-ooux-that-i-teach-we-call-the-process-orca-e226dfdd015a) 寫：「In the approach to OOUX that I teach, we call the process ORCA. That stands for objects, relationships, calls-to-action, and attributes」
- ORCA 是 Prater 後期（~2018+）系統化整理的，**不是 2015 ALA 原文**
- **驗證來源**: [ooux.com](https://ooux.com/what-is-ooux), [Sophia V Prater Medium](https://sophiavux.medium.com/), Episode 033 podcast

### 對 design-team 的應用 — 引用修正

> [!warning] OOUX 與 ORCA 應分開 cite
> design-team ui-interaction-gate.md L11-13 目前寫：「Structure informed by OOUI (上野学『オブジェクト指向UIデザイン』) and OOUX (Sophia Prater, ORCA process): objects (名詞) before actions (動詞). Evaluate using the ORCA lens: Objects → Relationships → CTAs → Attributes.」
>
> **正確歸因**：
> - **OOUX 哲學** → cite Prater "Object-Oriented UX", A List Apart 2015-10-20
> - **ORCA process** → cite ooux.com / Prater OOUX Masterclass，**不能** cite ALA 2015 文章
> - **OOUI 日本書** → cite 上野学他『オブジェクト指向 UI デザイン』2020

---

## Q9. J.J. Gibson *The Ecological Approach to Visual Perception*

### 書誌（已驗證）

- **作者**: James Jerome Gibson
- **標題**: *The Ecological Approach to Visual Perception*
- **原版**: Houghton Mifflin, **1979**
- **Classic Edition reissue**: Psychology Press / Routledge, 2014, **978-1848725782** (paperback)
- **驗證來源**: [Routledge Classic Edition](https://www.routledge.com/The-Ecological-Approach-to-Visual-Perception-Classic-Edition/Gibson/p/book/9781848725782), [Wikipedia: Affordance](https://en.wikipedia.org/wiki/Affordance)

### Affordance 起源 — 重要 nuance

- **affordance 一詞 Gibson 早於 1966** 在 *The Senses Considered as Perceptual Systems* 創造
- **1977** 發表 paper "The Theory of Affordances"
- **1979** 在 *The Ecological Approach to Visual Perception* Ch.8 完整論述
- 1979 是 canonical 一手 primary（Norman 後來在 1988 *DOET* 引用 Gibson）
- 1979 原始 quote: 「The affordances of the environment are what it offers the animal, what it provides or furnishes, either for good or ill」

### 對 design-team 的應用

- 任何提及「affordance」的描述應 cite Gibson 1979 為 origin + Norman 2013 為 design 領域改造
- visual-gate / ui-interaction-gate 提及 affordance 時建議併引

---

## Q10. Osgood, Suci, Tannenbaum *The Measurement of Meaning*

### 書誌（已驗證）

- **作者**: Charles E. Osgood, George J. Suci, Percy H. Tannenbaum
- **標題**: *The Measurement of Meaning*
- **出版**: University of Illinois Press, **1957**
- **ISBN-13**: 978-0252745393
- **驗證來源**: [UI Press 官方頁](https://www.press.uillinois.edu/books/?id=p745393), [Amazon](https://www.amazon.com/Measurement-Meaning-Charles-Osgood/dp/0252745396), [APA PsycNet](https://psycnet.apa.org/record/1958-01561-000), Gwern PDF host

### Semantic Differential (SD 法) 三因子

通過大規模 SD 數據因子分析，Osgood 找到 3 個 recurring attitudes：

1. **Evaluation** (good/bad) — 評価性
2. **Potency** (strong/weak) — 力量性
3. **Activity** (active/passive) — 活動性

這三因子是當代 SD 法的 canonical 結構，廣泛用於心理學、行銷、情感工學。

### 對 design-team 的應用 — Anti-pattern 替換

> [!warning] visual-gate.md L54 替換
> 目前寫：「参考: J-SEMS, J-STAGE (Osgood三因子), AIIT 東京都立産業技術大学院大学」
>
> **替換為**：「Osgood, Suci & Tannenbaum (1957) *The Measurement of Meaning*, University of Illinois Press, ISBN 978-0252745393 — 3 因子 (Evaluation / Potency / Activity)」

---

# Cluster B — Japanese Primary Sources

## Q11. 長町三生 感性工学 (Kansei Engineering)

### 一手來源（並列三個 canonical）

#### A. 日本語原典書

- **長町三生《感性工学—感性をデザインに活かすテクノロジー》**
- **出版**: 海文堂出版（海文堂サイエンス・らいぶらり）, **1989-11-01**
- **ISBN-13**: 978-4303713201
- **驗證來源**: [海文堂出版](https://www.kaibundo.jp/1989/11/01021/), [Amazon JP](https://www.amazon.co.jp/dp/4303713201), [長町三生 Wikipedia](https://ja.wikipedia.org/wiki/%E9%95%B7%E7%94%BA%E4%B8%89%E7%94%9F)
- **意義**: 「感性工学」一詞作為學術用語的奠基書

#### B. 英語 peer-reviewed paper

- **Nagamachi, M. (1995)** "Kansei Engineering: A new ergonomic consumer-oriented technology for product development"
- **發表**: *International Journal of Industrial Ergonomics*, Vol. 15, No. 1, pp. 3-11
- **DOI**: 10.1016/0169-8141(94)00052-5
- **驗證來源**: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/0169814194000525), [Semantic Scholar](https://www.semanticscholar.org/paper/Kansei-Engineering:-A-new-ergonomic-technology-for-Nagamachi/8697314e4e736891c0dd9a05436c12fb16b7fa92)
- **意義**: Kansei Engineering 進入國際學術社群的 canonical English primary，design-team 對國際讀者引用首選

#### C. 英語綜合書

- **Nagamachi & Lokman (2011)** *Innovations of Kansei Engineering*, CRC Press
- **ISBN-13**: 978-1439818664
- **意義**: 較新的英語書，但二手綜合性質

### grounding-principle canonical 選擇

> design-team 應 **同時 cite (A) 1989 JP 原典 + (B) 1995 IJIE paper**：
> - JP 讀者：cite (A) 為 ground
> - 國際 / 學術讀者：cite (B) 為 ground
> - 不需 cite (C)，因 (B) 已是 peer-reviewed primary

### 對 design-team 的應用

- visual-gate.md L4-7「感性工学 (Kansei Engineering, 長町三生)」現有引用 — **保留概念但加 ISBN/DOI**
- 「感性レポート」section 應併列 (A) + (B)
- 感性 SD 法的 7 段尺度評価流程可從 Nagamachi 1995 IJIE paper 直接 cite

---

## Q12. 深澤直人 Without Thought / 無意識のデザイン

### 一手來源

#### canonical primary

- **深澤直人《デザインの輪郭》**
- **出版**: TOTO 出版, **2005-12-01**
- **ISBN-13**: **978-4887062603** （Phase 1 gap report 寫 978-4887062818 — **錯誤**，那是別書）
- **頁數**: 295
- **內容**: 35-40 themed essays 含「Without Thought」「Design That Dissolves into Action」 — 深澤本人對「無意識のデザイン」的論述
- **驗證來源**: [TOTO 出版](https://jp.toto.com/publishing/detail/A0260.htm), [Amazon JP](https://www.amazon.co.jp/dp/4887062605), [HMV](https://www.hmv.co.jp/en/artist_%E6%B7%B1%E6%BE%A4%E7%9B%B4%E4%BA%BA_000000000335391/)

#### 補充來源

- **Phaidon《Naoto Fukasawa》(2007, 978-0714847900)** — 主要英語 monograph，可作國際 reference
- **Fukasawa & Morrison《Super Normal: Sensations of the Ordinary》(2007)** — co-authored 哲學宣言
- Without Thought workshops（1998-）— IDEO Japan 時代的工作坊起源，不易引用

### 對 design-team 的應用

- ui-interaction-gate.md L6-9「Informed by 深澤直人's "Without Thought" philosophy: design should emerge from unconscious human behavior (無意識の行為). Good UI is invisible.」**保留並加 cite《デザインの輪郭》TOTO 2005 ISBN 978-4887062603**
- visual-gate.md「気配」「佇まい」概念可互相 cross-reference 深澤的「形が行為に溶け込む」essays

---

## Q13. 安藤昌也《UX デザインの教科書》

### 書誌（已驗證 via WebFetch maruzen-publishing.co.jp）

- **作者**: 安藤昌也
- **標題**: 《UX デザインの教科書》
- **出版**: **丸善出版**, **2016-06-20** (Phase 1 gap report 寫 2016 — 正確)
- **ISBN-13**: **978-4621300374**
- **驗證來源**: [丸善出版](https://www.maruzen-publishing.co.jp/book/b10120504.html), [Amazon JP](https://www.amazon.co.jp/dp/4621300377), [國会図書館 NDL Search](https://ndlsearch.ndl.go.jp/en/books/R100000002-I027304299), [楽天ブックス](https://books.rakuten.co.jp/rb/14262864/)

### 4 期間 UX 模型 — 歸因鏈

#### 安藤書本身

- Section **2.2.4「体験の期間で異なって知覚される UX」** — 介紹 4 期間モデル
- 安藤本人**沒有發明** 4 期間，他在書中介紹的是 Roto/Law/Vermeeren/Hoonhout (2011) 的框架

#### 真正的一手 primary

- **Roto, V., Law, E.L-C., Vermeeren, A.P.O.S., Hoonhout, J. (2011)** *User Experience White Paper: Bringing clarity to the concept of user experience*
- 出自 **Dagstuhl Seminar 10373 "Demarcating User Experience"**（2010-09-15 to 18 in Dagstuhl, Germany）
- **canonical URL**: http://www.allaboutux.org/uxwhitepaper
- **PDF (Dagstuhl repo)**: http://drops.dagstuhl.de/opus/volltexte/2011/2949/pdf/10373_AbstractsCollection.2949.pdf
- **驗證來源**: [TU Delft Research Portal](https://research.tudelft.nl/en/publications/user-experience-white-paper-bringing-clarity-to-the-concept-of-us/), [Semantic Scholar](https://www.semanticscholar.org/paper/User-Experience-White-Paper-%E2%80%93-Bringing-clarity-to-Roto-Law/0c316acaa35bc8df3d1cbdb930a3f8f81959f544), [Dagstuhl Seminar 10373](https://www.dagstuhl.de/en/seminars/seminar-calendar/seminar-details/10373)

#### UX White Paper 4 phase canonical 定義

| Phase | EN | JP（U-Site / chot.design 通用譯） |
|---|---|---|
| Anticipated UX | 利用前的期待 | **予期的 UX** |
| Momentary UX | 利用中的瞬間反應 | **一時的 UX** |
| Episodic UX | 利用後的特定事件回顧 | **エピソード的 UX** |
| Cumulative UX | 累積長期回顧 | **累積的 UX** |

JP 譯詞最早由 黒須・安藤等日本 HCD 学界 2011-2012 引入。

### 對 design-team 的應用 — 雙重 cite

> [!info] ux-strategy-gate.md L7「安藤昌也 UXの期間モデル」應改為雙引用
> - **原始一手**: Roto et al. (2011) UX White Paper, allaboutux.org
> - **JP 譯介一手**: 安藤昌也《UX デザインの教科書》丸善出版 2016, ISBN 978-4621300374, Section 2.2.4
>
> 兩者並列：原始概念來源 + JP 學術 canonical 引介

---

## Q14. 黒須正明《UX 原論》

### 書誌（已驗證 via WebFetch kindaikagaku.co.jp）

- **作者**: 黒須正明
- **標題**: 《UX 原論—ユーザビリティから UX へ》
- **出版**: **近代科学社**, **2020-04-28** (NOT 2013, NOT KOKUSAI 出版)
- **ISBN-13**: **978-4764906112** (NOT 978-4764904682，gap report 錯誤)
- **規格**: A5 判・並製・312 頁
- **價格**: 本体 3,500 円
- **驗證來源**: [近代科学社](https://www.kindaikagaku.co.jp/book_list/detail/9784764906112/), [版元ドットコム](https://www.hanmoto.com/bd/isbn/9784764906112), [Amazon JP](https://www.amazon.co.jp/dp/4764906112)

> [!warning] gap report 重大錯誤
> Phase 1 gap report 寫「黒須正明 UX 原論—ユーザビリティから UX へ (2013, 近代科学社 or KOKUSAI, ISBN 978-4764904682)」
> **正確值**：**2020-04-28 / 近代科学社 / 978-4764906112**
> 年份差 7 年、ISBN 全錯。設計-team v4.7.0 必須使用正確 metadata。

### 4-quality 模型（NOT 3D Quality）— 重大歸因修正

黒須在 UX 原論 Chapter 11「UX の概念構造」Section 11.3「四つの品質領域」提出：

| 軸 | 設計時 | 利用時 |
|---|---|---|
| **客観的品質** | usability, functionality, performance, reliability, safety, compatibility, cost, maintainability | effectiveness, efficiency, productivity, risk avoidance |
| **主観的品質** | 魅力 (attractiveness), 感性訴求性, 欲求訴求性 | 達成感, 安心感, 楽しさ, 喜び → 満足感 |

最終所有四象限收斂到「主觀利用時品質」→「滿足感」。

**驗證來源**: [KUSANAGI Tech Column 黒須正明連載第三回](https://www.prime-strategy.co.jp/column/archives/column_1267) 「客観的品質特性と主観的品質特性」直接由黒須本人撰寫；近代科学社 TOC 確認 Ch.11.3 標題「四つの品質領域」。

### 對 design-team 的應用 — 重大歸因修正

> [!error] ux-strategy-gate.md L38-43 必須改寫
> 目前寫：「## Supplementary: 黒須 3D Quality Check / Flag ONLY if these reveal issues NOT already caught above: / - 品質 (Quality): Reliability or usability gaps across phases / - 感性 (Kansei): Emotional friction undermining strategic goals / - 意味性 (Meaningfulness): Hollow experience despite feature completeness」
>
> **錯誤**：
> 1. 「3D Quality」**不存在**於黒須著作 — 應為「4 quality (四つの品質領域)」
> 2. 「意味性 / Meaningfulness」**不在**黒須 4 quality 架構中 — 應 cite Verganti
>
> **修正**：
> 1. 拆成「黒須 4-quality check (UX 原論 Ch.11.3, 近代科学社 2020, ISBN 978-4764906112)」— 客観 × 設計時 / 客観 × 利用時 / 主観 × 設計時 / 主観 × 利用時
> 2. 另立「Verganti meaning check (Design-Driven Innovation, HBR Press 2009, ISBN 978-1422124826)」— 是否帶來新「意味」

### 黒須其他關鍵書

- 黒須是 JP HCD 創始人之一，先前著作含《人間中心設計の基礎》(2013, 近代科学社) 也可作為 ground，但 UX 原論 (2020) 是最近最完整。

---

## Q15. 上野学《オブジェクト指向 UI デザイン》

### 書誌（已驗證）

- **作者**: ソシオメディア株式会社・上野学・藤井幸多 共著（上野学監修）
- **標題**: 《オブジェクト指向 UI デザイン—使いやすいソフトウェアの原理》(WEB+DB PRESS plus シリーズ)
- **出版**: **技術評論社**, **2020-06-05**
- **ISBN-13**: **978-4297113513**
- **頁數**: 360
- **驗證來源**: [技術評論社](https://gihyo.jp/book/2020/978-4-297-11351-3), [ソシオメディア](https://www.sociomedia.co.jp/10046), [CiNii](https://ci.nii.ac.jp/ncid/BB30879040), [Amazon JP](https://www.amazon.co.jp/dp/4297113511)

### 內容結構

- 前半：理論 + process（OOP / GUI 起源、modeless、OOUI 理論）
- 後半：18 個 workout 實作練習
- 提到 Larry Tesler / Xerox PARC 的 OOUI 起源（1970s-80s GUI 發展），不過明確 chapter mapping 需 user 自行驗證實體書

### 對 design-team 的應用

- ui-interaction-gate.md L11「Structure informed by OOUI (上野学『オブジェクト指向UIデザイン』)」**正確 cite**，加 ISBN 978-4297113513 / 技術評論社 / 2020 即可
- 「Object Modeling」flag definitions 應 ground 在此書 + Prater OOUX

---

## Q16. 原研哉 引き算 / 白 / 余白

### 一手 primary 三冊

#### A. 《デザインのデザイン》

- **出版**: **岩波書店**, **2003-10-22**
- **ISBN-13**: **978-4000240055**
- **獎項**: サントリー学芸賞
- **內容**: Re-design 展、無印良品 art direction、日本デザインの再考
- **驗證來源**: [岩波書店](https://www.iwanami.co.jp/book/b263308.html), [Amazon JP](https://www.amazon.co.jp/dp/4000240056)

#### B. 《白》

- **出版**: **中央公論新社**, **2008-05-30**
- **ISBN-13**: **978-4120039379** （注意：gap report 寫 978-4120039553 — **錯誤**）
- **規格**: 152 頁・四六判・日英両文
- **章節**: 第 1 章「白の発見」、第 2 章「紙」、第 3 章「空白 エンプティネス」、第 4 章「白へ」
- **驗證來源**: [中央公論新社](https://www.chuko.co.jp/tanko/2008/05/003937.html), [Amazon JP](https://www.amazon.co.jp/dp/4120039374), [楽天ブックス](https://books.rakuten.co.jp/rb/5718352/)

#### C. *Designing Design* (英語版)

- **出版**: Lars Müller Publishers, **2007**
- **ISBN-13**: **978-3037781050** (978-3-03778-105-0)
- **頁數**: 467
- **驗證來源**: [Lars Müller Publishers](https://www.lars-mueller-publishers.com/designing-design)
- **意義**: 國際英語版 — Designing Design 比 デザインのデザイン 更完整（含 ex-formation 章）

### 引き算 / 白 / 余白 概念在原書中的論述

- 《白》第 3 章「空白 エンプティネス」直接論「空白」: 「空白は『無』や『エネルギーの不在』ではなく、むしろ未来に充実した中身が満たされるべき『機前の可能性』」
- 《デザインのデザイン》第 6 章「日本にいる私」: 「たたずまいは吸引力を生む資源である」(佇まい)
- ex-formation = 「we do not actually say but have in our heads」(Designing Design)

### 對 design-team 的應用

- visual-gate.md「引き算のデザイン (Subtractive Design)」 → cite 原研哉《デザインのデザイン》岩波 2003 / 《白》中公 2008
- 「余白」「ma」 → 原研哉《白》Ch.3 + 磯崎新《建築における「日本的なもの」》(Q19)
- 「佇まい」 → 原研哉《デザインのデザイン》Ch.6

---

## Q17. Leonard Koren *Wabi-Sabi for Artists, Designers, Poets & Philosophers*

### 書誌（已驗證）

- **作者**: Leonard Koren
- **標題**: *Wabi-Sabi for Artists, Designers, Poets & Philosophers*
- **原版**: Stone Bridge Press (Berkeley, CA), **1994**
- **ISBN-13**: **978-1880656129** (978-1-880656-12-9)
- **再版**: Imperfect Publishing 2008 reissue (978-0981484600)
- **驗證來源**: [Goodreads](https://www.goodreads.com/book/show/42190.Wabi_Sabi), [Amazon (1994 ed)](https://www.amazon.com/Wabi-Sabi-Artists-Designers-Poets-Philosophers/dp/1880656124), [Leonard Koren 官網](https://leonardkoren.com/)

### 是否有更深的 primary？

- 岡倉天心《茶の本》*The Book of Tea* (1906) 是更早的「茶道 + wabi」一手哲學書，但 Koren 1994 才是 **wabi-sabi as design concept** 的西方 canonical entry point
- 兩者並用最佳：Koren 1994 (design lens) + 岡倉 1906 (philosophical anchor)

### 對 design-team 的應用

- visual-gate.md L9-11「わびさび (Wabi-Sabi): Beauty in imperfection, impermanence, incompleteness」 → cite Koren 1994 為 design 解讀 + 岡倉 1906 為哲學 root
- 「不完全の許容」flag → cite Koren 1994 「wabi-sabi is a beauty of things imperfect, impermanent, and incomplete」原文

---

## Q18. JIS Z 8530 / ISO 9241-210

### 標準（已驗證）

#### 國際版

- **ISO 9241-210:2019** *Ergonomics of human-system interaction — Part 210: Human-centred design for interactive systems*
- 是 ISO 9241-210:2010 的第二版，**minor revision**
- **canonical URL**: https://www.iso.org/standard/77520.html
- **驗證來源**: [ISO 官網](https://www.iso.org/standard/77520.html), [iteh.ai PDF](https://cdn.standards.iteh.ai/samples/77520/8cac787a9e1549e1a7ffa0171dfa33e0/ISO-9241-210-2019.pdf)
- **付費**: 是

#### JIS 對應版

- **JIS Z 8530:2021** 人間工学—人とシステムとのインタラクション—インタラクティブシステムの人間中心設計
- **公開**: 2021-03
- 對應 ISO 9241-210:2019, **MOD（修改採用）**，加入日本本土 modifications；前一版 JIS Z 8530:2019 為 IDT（一致採用）ISO 9241-210:2010
- **canonical URL**: https://webdesk.jsa.or.jp/books/W11M0090/index/?bunsyo_id=JIS+Z+8530:2021
- **驗證來源**: [JSA](https://webdesk.jsa.or.jp/books/W11M0090/index/?bunsyo_id=JIS+Z+8530:2021), [U-Site 黒須「ようやくJIS Z 8530」](https://u-site.jp/lecture/jis-z-8530), [U-Site「ついに出た JIS Z 8530:2021」](https://u-site.jp/lecture/jis-z-8530-2021)

> [!warning] gap report 過時
> Phase 1 gap report 寫「JIS Z 8530」沒有版本號 + 「ISO 9241-210:2019」 — 應寫 JIS Z 8530:**2021**

### 對 design-team 的應用

- ux-strategy-gate / a11y-checklist 的「人間中心設計プロセス」應 cite ISO 9241-210:2019 為國際 ground + JIS Z 8530:2021 為 JP ground
- HCD 6 原則（user / task / environment 全面理解、user 全程参与、user-centered evaluation 反復、process 反復、跨領域 team、whole UX 設計）來自 ISO 9241-210:2019 — 可成為 ux-strategy 的 Strategy plane checklist source

---

# Cluster C — Anti-pattern Cleanup

## visual-gate.md 5 個 bad citations 處理

### 1. btrax「寿司職人から学ぶ UX デザイン 6 つの極意」(L95)

- 來源: https://blog.btrax.com/ux-designers-sushi-chef/
- 性質: btrax 是 SF/Tokyo design consulting company 的 corporate blog (freshtrax)，**非學術 / 非書籍 / 非標準**
- 內容: 列 6 條 lesson — simplicity, storytelling, hidden elements, hospitality, personalization (omotenashi 為 anchor)
- **判定**: ❌ **REMOVE** — 沒有對應的學術 / 書籍 primary
- **替代**:
  - 「先回りの気遣い」「隠し要素」「細部の品格」概念 → 移到「**おもてなし**」section 但 cite 學術或文化書籍
  - **可替代 primary**: ① 千宗室《茶道—おもてなしの心》(淡交社, 茶道文化系列) 為茶道-おもてなし 起源；② Verganti 2009 *Design-Driven Innovation* 為「meaning beyond utility」的當代設計理論
  - 若無強學術 ground，**降為 editorial framing only**: 在 visual-gate 開頭 informed-by section 移除 btrax 引用，「おもてなし品質チェック」section 改寫為 informed by 茶道文化 + Verganti，不再聲稱由 btrax 提供框架

### 2. J-SEMS, J-STAGE, AIIT (L54) for SD 法

- 性質: 三個 academic conference / wiki 資料源，sub-primary 引用
- **判定**: ❌ **REMOVE all three**
- **替代**: **Osgood, Suci & Tannenbaum (1957) *The Measurement of Meaning*, University of Illinois Press, ISBN 978-0252745393** — Q10 已驗證
- 引用文字: 「印象評価は SD 法 (Semantic Differential, Osgood Suci Tannenbaum 1957) の三因子—Evaluation / Potency / Activity—に基づく」

### 3. KOGEI STANDARD「間と余白」(L77)

- 來源: https://www.kogeistandard.com/jp/insight/serial/editor-in-chief-column-kogei/ma-yohaku/
- 性質: 工芸 brand magazine column，**非學術**
- **判定**: ❌ **REMOVE**
- **替代**:
  - **磯崎新《建築における「日本的なもの」》新潮社 2003-04-30, ISBN 978-4104587018** — 「間 ma」「日本的空間性」的學術 primary（Q19）
  - **原研哉《白》中央公論新社 2008-05-30, ISBN 978-4120039379**, Ch.3「空白 エンプティネス」 — 余白的設計論述

### 4. ガリバーコラム「引き算のデザイン」(L77)

- 性質: 中古車サイト的 marketing column，**完全非設計學術**
- **判定**: ❌ **REMOVE**
- **替代**: **原研哉《デザインのデザイン》岩波書店 2003-10-22, ISBN 978-4000240055**

### 5. studio-tabi「佇まい」+ Wikipedia「わびさび」(L77)

- 性質: 個人工作室 blog + Wikipedia
- **判定**: ❌ **REMOVE both**
- **替代**:
  - 佇まい → **原研哉《デザインのデザイン》Ch.6「日本にいる私」**「たたずまいは吸引力を生む資源である」直接 cite
  - わびさび → **Leonard Koren 1994 *Wabi-Sabi for Artists, Designers, Poets & Philosophers*, Stone Bridge Press, ISBN 978-1880656129** + （補充）岡倉天心《茶の本》1906

## 補充: 未包含在原 5 個但仍是部落格 / wiki 性質的引用

- visual-gate.md L77 完整原文「KOGEI STANDARD (間と余白), ガリバーコラム (引き算のデザイン), btrax (UXピラミッド), studio-tabi (佇まい), Wikipedia (わびさび)」 — **整段移除**
- 替換為新「### Primary Sources for 日本的感性品質チェック」block，列 4-5 個書誌（磯崎新 2003、原研哉 2003 / 2008、Koren 1994、Verganti 2009、長町 1989）

---

# Q19. 額外發現—磯崎新《建築における「日本的なもの」》

### 書誌（已驗證 — 取代 KOGEI STANDARD）

- **作者**: 磯崎新（建築家、Pritzker Prize 2019）
- **標題**: 《建築における「日本的なもの」》
- **出版**: 新潮社, **2003-04-30**
- **ISBN-10**: 410458701X
- **ISBN-13**: **978-4104587018**
- **驗證來源**: [新潮社](https://www.shinchosha.co.jp/book/458701/), [松岡正剛 千夜千冊 0898 夜](https://1000ya.isis.ne.jp/0898.html), [Amazon JP](https://www.amazon.co.jp/dp/410458701X), [日埜直彦『磯崎新における「日本的なもの」』(10+1)](https://db.10plus1.jp/backnumber/article/articleid/105/)
- **內容**: 4 章 — 日本近代建築如何吸收 / 改寫西洋現代主義 / 桂離宮 / 大仏様 / 伊勢神宮的「オリジナルのコピー」概念
- **意義**: 「間 / 日本的空間性」最高權威的學術 primary（磯崎新 2018 年策展「間 — 20年後の帰還展」也是連續論述）

# JP Integration Decision: FULL

**Decision**: **FULL**（與 Phase 1 的 HIGH 信心一致，Phase 2 100% 確認）

**Evidence**:

1. **12 個 JP 載重方法論全部驗證有獨立一手書誌**：
   - 感性工学（長町三生 1989 海文堂 + Nagamachi 1995 IJIE）
   - 無意識のデザイン（深澤直人 2005 TOTO）
   - 引き算 / 白 / 余白（原研哉 2003 岩波 + 2008 中公 + 2007 Lars Müller）
   - わびさび（Koren 1994 Stone Bridge Press；岡倉 1906 補充）
   - 間 ma / 佇まい（磯崎新 2003 新潮社 + 原研哉 2003）
   - おもてなし（茶道文化 + Verganti 2009 概念補強）
   - 4 期間 UX（Roto et al. 2011 UX White Paper + 安藤昌也 2016 丸善）
   - 4 quality（黒須正明 2020 近代科学社 UX 原論 Ch.11.3）
   - OOUI（上野学 2020 技術評論社）
   - 人間中心設計 HCD（JIS Z 8530:2021 + ISO 9241-210:2019）
   - 美学 / 感性レポート（Osgood 1957 + 長町 1989）

2. **JP 方法論在 design-team 的角色是 structural SSOT**，與 qa-team v4.2.0 (VSTeP/HAYST/ゆもつよ as structural peer to ISTQB) 同 level，甚至更深：
   - ux-strategy-gate 的 4 phases = Hassenzahl/Roto + 安藤
   - ui-interaction-gate 的 Object Modeling = OOUX/Prater + OOUI/上野
   - visual-gate 的整個 Section A/B/C = SD 法/Osgood + 感性工学/長町 + 引き算/原研哉 + わびさび/Koren + 佇まい/磯崎・原研哉

3. **無 forced symmetry 風險**：所有 JP 方法論皆有實際被引用的 protocol/rubric 描述支撐，不是裝飾性 preamble。

**結論**: design-team v4.7.0 應將 JP 整合提升到結構性 standards files 形式（不只是 preamble），在 SKILL.md「Anchored on…」block 同時 cite Anglo + JP 兩組 primary。

---

# Grounding Plan — Standards to Create

## Standard 1: `wcag-baseline.md` (UPGRADE existing)

- **Purpose**: WCAG 2.2 AA 一手 ground，含 Success Criteria 對照表
- **Primary sources**:
  - W3C *Web Content Accessibility Guidelines (WCAG) 2.2*, W3C Recommendation, republished 2024-12-12, https://www.w3.org/TR/WCAG22/
  - W3C *What's New in WCAG 2.2*, https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- **Load-bearing claims covered**: 4 principles, 13 guidelines, 86 SC, A/AA/AAA levels, contrast 4.5:1, target size 24×24 (AA) / 44×44 (AAA), focus visible, keyboard, target size minimum 2.5.8
- **JP preamble anchor**: no（Anglo standard）
- **Estimated lines**: 90-120
- **重點修正**: 
  - L21 touch targets 標準改用 WCAG 2.5.8 (24×24 AA) + Apple/Material 平台補充
  - L46 AAA opportunities 中的 24×24 應改為 44×44（WCAG 2.5.5 AAA）

## Standard 2: `nielsen-norman-heuristics.md` (NEW)

- **Purpose**: Anglo HCI canon — Norman foundational + Nielsen 10 heuristics
- **Primary sources**:
  - Donald A. Norman (2013) *The Design of Everyday Things: Revised and Expanded Edition*, Basic Books, ISBN 978-0465050659
  - Jakob Nielsen (1994 / updated 2024) "10 Usability Heuristics for User Interface Design", https://www.nngroup.com/articles/ten-usability-heuristics/
  - James J. Gibson (1979) *The Ecological Approach to Visual Perception*, Houghton Mifflin (Routledge Classic Edition 2014, ISBN 978-1848725782) — affordance origin
- **Load-bearing claims covered**: affordance, signifiers, 7-stage action cycle, gulfs of execution/evaluation, 10 heuristics (Visibility / Match / User Control / Consistency / Error Prevention / Recognition / Flexibility / Aesthetic / Help & Recover / Help & Doc)
- **JP preamble anchor**: no
- **Estimated lines**: 100-140

## Standard 3: `garrett-elements-of-ux.md` (NEW)

- **Purpose**: 5 plane model = ux-strategy + ui-interaction + visual gate 的基礎結構
- **Primary sources**:
  - Jesse James Garrett (2010) *The Elements of User Experience: User-Centered Design for the Web and Beyond*, 2nd Edition, New Riders, ISBN 978-0321683687
  - Garrett (2000) Original "Elements of UX" diagram, http://www.jjg.net/elements/pdf/elements.pdf
- **Load-bearing claims covered**: Strategy / Scope / Structure / Skeleton / Surface 5 plane mapping，每 plane 對應的 UX concern
- **JP preamble anchor**: no
- **Estimated lines**: 70-90

## Standard 4: `kansei-engineering-and-sd.md` (NEW)

- **Purpose**: 感性工学 + SD 法 一手 ground，取代 visual-gate 的 J-SEMS / AIIT 引用
- **Primary sources**:
  - 長町三生 (1989)《感性工学—感性をデザインに活かすテクノロジー》海文堂出版, ISBN 978-4303713201
  - Mitsuo Nagamachi (1995) "Kansei Engineering: A new ergonomic consumer-oriented technology for product development", *International Journal of Industrial Ergonomics*, 15(1):3-11, DOI 10.1016/0169-8141(94)00052-5
  - Charles E. Osgood, George J. Suci, Percy H. Tannenbaum (1957) *The Measurement of Meaning*, University of Illinois Press, ISBN 978-0252745393
- **Load-bearing claims covered**: 感性工学定義、Kansei -> design parameter translation methodology、SD 法 7 段尺度、3 因子 (Evaluation / Potency / Activity)、感性 SD profile 與 brand intent 對照
- **JP preamble anchor**: yes（長町三生為 anchor）
- **Estimated lines**: 90-120

## Standard 5: `japanese-design-aesthetics.md` (NEW)

- **Purpose**: 日本美学一手書誌集 — 取代 visual-gate 的 KOGEI STANDARD / studio-tabi / Wikipedia / btrax / ガリバーコラム 5 個 bad citations
- **Primary sources**:
  - 原研哉 (2003)《デザインのデザイン》岩波書店, ISBN 978-4000240055（引き算 / 佇まい）
  - 原研哉 (2008)《白》中央公論新社, ISBN 978-4120039379（白 / 余白 / エンプティネス）
  - Kenya Hara (2007) *Designing Design*, Lars Müller Publishers, ISBN 978-3037781050（國際版補充）
  - 深澤直人 (2005)《デザインの輪郭》TOTO 出版, ISBN 978-4887062603（無意識のデザイン / Without Thought）
  - 磯崎新 (2003)《建築における「日本的なもの」》新潮社, ISBN 978-4104587018（間 ma / 日本的空間）
  - Leonard Koren (1994) *Wabi-Sabi for Artists, Designers, Poets & Philosophers*, Stone Bridge Press, ISBN 978-1880656129（わびさび）
- **Load-bearing claims covered**: 引き算のデザイン、白 / 余白 / 空白、間 ma、佇まい、気配、わびさび、無意識のデザイン、ex-formation
- **JP preamble anchor**: yes（全部 JP designers/critics）
- **Estimated lines**: 130-160

## Standard 6: `ux-temporal-and-quality-models.md` (NEW)

- **Purpose**: ux-strategy-gate 的 4 phase + 4 quality 模型 ground
- **Primary sources**:
  - V. Roto, E.L-C. Law, A.P.O.S. Vermeeren, J. Hoonhout (2011) *User Experience White Paper: Bringing clarity to the concept of user experience*, Dagstuhl Seminar 10373, http://www.allaboutux.org/uxwhitepaper
  - 安藤昌也 (2016)《UX デザインの教科書》丸善出版, ISBN 978-4621300374（Section 2.2.4 体験の期間で異なって知覚される UX）
  - 黒須正明 (2020)《UX 原論—ユーザビリティから UX へ》近代科学社, ISBN 978-4764906112（Ch.11.3 四つの品質領域）
  - Roberto Verganti (2009) *Design-Driven Innovation: Changing the Rules of Competition by Radically Innovating What Things Mean*, Harvard Business Review Press, ISBN 978-1422124826（意味のイノベーション）
  - JIS Z 8530:2021 / ISO 9241-210:2019（HCD process）
- **Load-bearing claims covered**: 4 期間 UX (anticipated / momentary / episodic / cumulative)、4 quality (objective × design-time / use-time × subjective × design-time / use-time)、meaning innovation、interpreters、HCD 6 原則
- **JP preamble anchor**: yes（安藤・黒須）
- **Estimated lines**: 110-140

## Standard 7: `ooui-and-object-modeling.md` (NEW)

- **Purpose**: ui-interaction-gate 的 Object Modeling section ground
- **Primary sources**:
  - 上野学・ソシオメディア・藤井幸多 (2020)《オブジェクト指向 UI デザイン—使いやすいソフトウェアの原理》技術評論社, ISBN 978-4297113513
  - Sophia V. Prater (2015) "Object-Oriented UX", *A List Apart*, 2015-10-20, https://alistapart.com/article/object-oriented-ux/
  - Sophia V. Prater (2016) "OOUX: A Foundation for Interaction Design", *A List Apart*, 2016-04-19, https://alistapart.com/article/ooux-a-foundation-for-interaction-design/
  - Sophia V. Prater "ORCA Process", https://ooux.com/what-is-ooux （ORCA full framework canonical）
- **Load-bearing claims covered**: OOUI 哲學（noun before verb）、object views、object relationships、Collection → Single Object → Detail flow、OOUX vs task UI、ORCA 4 步驟
- **JP preamble anchor**: yes（上野学）
- **Estimated lines**: 80-110

## Standard 8: `platform-conventions.md` (NEW, optional)

- **Purpose**: ui-interaction-gate 的 Platform Conventions section ground
- **Primary sources**:
  - Apple Human Interface Guidelines (Apple Developer Documentation), https://developer.apple.com/design/human-interface-guidelines/ — 44pt × 44pt iOS tap target
  - Material Design 3 (Google), https://m3.material.io/foundations/designing/structure — 48dp × 48dp Android touch target + interaction states (Enabled/Hover/Focus/Pressed/Dragged/Disabled/Selected/Activated)
- **Load-bearing claims covered**: iOS 44pt / Android 48dp / WCAG 24×24 AA baseline、component states canonical list
- **JP preamble anchor**: no
- **Estimated lines**: 60-90

**Total: 8 standards files, ~ 730-980 lines aggregate**

---

# Claim → Source Mapping (Final)

## 從 Phase 1 12 implicit JP citations → final primary sources

| Phase 1 implicit citation | 出現位置 | Final primary source |
|---|---|---|
| 感性工学 (長町三生) | visual-gate L4 | 長町三生 1989《感性工学》海文堂 ISBN 978-4303713201 + Nagamachi 1995 IJIE 15(1):3-11 |
| 引き算のデザイン | visual-gate L7-9 | 原研哉 2003《デザインのデザイン》岩波 ISBN 978-4000240055 |
| わびさび | visual-gate L9-11 | Leonard Koren 1994 Stone Bridge Press ISBN 978-1880656129 |
| Without Thought / 無意識のデザイン | ui-interaction-gate L6-9 | 深澤直人 2005《デザインの輪郭》TOTO ISBN 978-4887062603 |
| OOUI / 上野学 | ui-interaction-gate L11 | 上野学他 2020 技術評論社 ISBN 978-4297113513 |
| OOUX / Sophia Prater | ui-interaction-gate L12 | Prater 2015 ALA + ooux.com (ORCA full framework) |
| 安藤昌也 4 期間 UX モデル | ux-strategy-gate L7 | Roto/Law/Vermeeren/Hoonhout 2011 UX White Paper + 安藤 2016《UX デザインの教科書》ISBN 978-4621300374 |
| 黒須 3D Quality（**修正**為 4 quality） | ux-strategy-gate L38 | 黒須正明 2020《UX 原論》近代科学社 ISBN 978-4764906112, Ch.11.3 |
| 意味性 Meaningfulness（**錯誤歸屬黒須**） | ux-strategy-gate L42 | **重新歸給** Verganti 2009 *Design-Driven Innovation* HBR ISBN 978-1422124826 |
| おもてなし | ux-strategy-gate L4-5, visual-gate L92-103 | 茶道文化 (no single primary book) + 補強 Verganti meaning + 移除 btrax 引用 |
| Garrett 戦略 / 要件 | ux-strategy-gate L8-12 | Garrett 2010 Elements of UX 2nd ed New Riders ISBN 978-0321683687 |
| 構造 / 骨格 | ui-interaction-gate L3 | Garrett 2010 (同上) |

## 從 Phase 1 8 un-cited Anglo anchors → final primary sources

| Phase 1 un-cited | Final primary source |
|---|---|
| Donald Norman | Norman 2013 *The Design of Everyday Things: Revised and Expanded Edition* Basic Books ISBN 978-0465050659 |
| Jakob Nielsen 10 heuristics | Nielsen NN/g 1994 / updated 2024-01-30 https://www.nngroup.com/articles/ten-usability-heuristics/ |
| Jesse James Garrett 5 planes | Garrett 2010 New Riders ISBN 978-0321683687 |
| WCAG 2.2 | W3C Recommendation republished 2024-12-12 https://www.w3.org/TR/WCAG22/ |
| Apple HIG | https://developer.apple.com/design/human-interface-guidelines/ + Buttons HIG (44 pt) |
| Material Design 3 | https://m3.material.io/ + Foundations/Structure (48 dp) + Interaction/States |
| OOUX / Prater | Prater 2015 ALA + ooux.com (ORCA framework) |
| Verganti meaning innovation | Verganti 2009 HBR Press ISBN 978-1422124826 |

## 額外發現的 grounding gaps（不在 Phase 1 但 Phase 2 補上）

| 概念 | 出現位置 | Primary source |
|---|---|---|
| Affordance origin | Norman 引用衍生 | Gibson 1979 ISBN 978-1848725782 |
| SD 法 / Semantic Differential | visual-gate L48-66 | Osgood, Suci, Tannenbaum 1957 ISBN 978-0252745393 |
| 間 ma / 日本的空間 | visual-gate L17 (Composition 余白) + Section B 余白 | 磯崎新 2003 新潮社 ISBN 978-4104587018 + 原研哉 2008《白》ISBN 978-4120039379 |
| HCD process | （implicit throughout） | ISO 9241-210:2019 + JIS Z 8530:2021 |

---

# Anti-pattern Cleanup Recommendations for visual-gate.md

## L4-11 Informed-by section

- **Keep**: 感性工学・引き算のデザイン・わびさび 三 anchor
- **Add**: ISBN / DOI 立即在每個 anchor 後括注

```markdown
Informed by Japanese aesthetic philosophy:
- **感性工学** (Kansei Engineering, 長町三生 1989; Nagamachi IJIE 15(1):3-11, 1995)
- **引き算のデザイン** (原研哉《デザインのデザイン》岩波書店 2003, ISBN 978-4000240055)
- **わびさび** (Leonard Koren 1994 Stone Bridge Press, ISBN 978-1880656129)
```

## L43-66 SD 法 section

- **Remove L54**: 「J-SEMS, J-STAGE (Osgood三因子), AIIT 東京都立産業技術大学院大学」
- **Replace with**: 「Osgood, Suci & Tannenbaum (1957) *The Measurement of Meaning*, University of Illinois Press (ISBN 978-0252745393), Ch.2 (Evaluation / Potency / Activity 三因子)」

## L72-90 Section B「日本的感性品質チェック」

- **Remove L76-77**: 「KOGEI STANDARD (間と余白), ガリバーコラム (引き算のデザイン), btrax (UXピラミッド), studio-tabi (佇まい), Wikipedia (わびさび)」整段
- **Replace with**: primary sources block

```markdown
Primary sources for 日本的感性品質チェック:
- 余白 / 間 ma → 磯崎新《建築における「日本的なもの」》新潮社 2003 (978-4104587018) + 原研哉《白》中央公論新社 2008 Ch.3「空白」(978-4120039379)
- 引き算 → 原研哉《デザインのデザイン》岩波書店 2003 (978-4000240055)
- 佇まい → 原研哉《デザインのデザイン》Ch.6「日本にいる私」(同上)
- わびさび → Leonard Koren 1994 Stone Bridge Press (978-1880656129)
- 気配 / 余韻 / 抜け感 → 深澤直人《デザインの輪郭》TOTO 出版 2005 (978-4887062603)
```

## L92-103 Section C「おもてなし品質チェック」

- **Remove L94-95**: 「参考: btrax「寿司職人から学ぶUXデザイン 6つの極意」」
- **Replace strategy**: btrax 部落格不能作為 framework source — 兩個選擇:
  1. **降為 editorial framing**: 章節 reframe 為「おもてなし quality from 茶道 traditions + Verganti meaning innovation」，6 個 check item 保留但歸功茶道文化通用知識
  2. **完全 remove section C**: 若無法找到一手書，整個移除

**推薦選 (1)**: 6 check items 本身（先回りの気遣い、隠し要素、ストーリー性、細部の品格、究極のシンプルさ）來自茶道哲學常識，以「茶道的おもてなし精神」+ Verganti 2009「meaning beyond utility」雙重 anchor 即可，不需要 btrax。

---

# Open Questions / Needs User Verification

## 1. Material 3 component states canonical list 完整性

- 從 m3.material.io/foundations/interaction/states/applying-states 用 WebFetch 直接抓取受 JavaScript-only 阻擋
- 從 Material 2 (m2.material.io) + GitHub Material Components Android repo + 多個第三方 tutorial 交叉確認 11 個 state（Enabled, Hover, Focused, Pressed, Dragged, Disabled, Selected, Activated, On, Off, Error）
- **Action**: user 應在實際撰寫 platform-conventions.md 時用瀏覽器手動確認 m3.material.io 頁面的最終 canonical states list

## 2. ALA 2015 OOUX 文章的「issue number」

- Phase 1 gap report 提到「issue #530」— 我未在原文或 ALA author 頁找到 issue number 標示
- A List Apart 線上版不一定按 issue 編碼，issue # 可能是 print era 殘留
- **Action**: 不要在標準中 cite issue number；只 cite「A List Apart, 2015-10-20」即可

## 3. 安藤昌也書 Section 2.2.4 是否完整 enumerate 4 phase 名稱

- 從丸善頁面 TOC 確認 Section 2.2.4 標題是「体験の期間で異なって知覚される UX」
- TOC 沒有再深入子節名稱 — **無法 100% 確認** 4 phase JP 譯詞「予期的 UX / 一時的 UX / エピソード的 UX / 累積的 UX」是否正是安藤書內用語，但日本 HCD 学界通用此譯詞且有 U-Site / chot.design / scrapbox 等多源確認
- **Action**: 在 ux-temporal-and-quality-models.md 中說明「四期間モデル原典是 Roto et al. 2011 UX White Paper；JP 譯詞為日本 HCD 学界通用，安藤書 Section 2.2.4 採用」

## 4. 黒須正明 4-quality model 完整章節結構

- 確認 Ch.11.3 標題是「四つの品質領域」
- 確認 4 象限名稱與內容（從 KUSANAGI Tech Column 黒須本人連載驗證）
- TOC 沒有列出每個品質領域 indicator 的完整列表
- **Action**: ux-temporal-and-quality-models.md 應 cite Ch.11.3 為 ground，但避免 enumerate 太細的指標（user 可在實際使用中翻書補充）

## 5. 「気配」「余韻」「抜け感」是否在深澤直人書中明確命名？

- 已驗證《デザインの輪郭》含 35-40 themed essays 含「Without Thought」「Design That Dissolves into Action」
- **未驗證**「気配 / 余韻 / 抜け感」是否為書中明確 essay 標題
- 這三個概念在日本設計界是通用語，但若 design-team 要嚴格 cite primary 出處，可能需要降為「日本的感性 vocabulary（通用日本語）」而非歸功單一作者
- **Action**: 在 japanese-design-aesthetics.md 中將「気配 / 余韻 / 抜け感」標示為「日本的感性 lexicon（通用），補充參考：原研哉、深澤直人 essays」而非單一書 cite

## 6. JIS Z 8530:2021 全文是否需付費取得？

- 確認 JIS 規格通常需向 JSA 購買 PDF（http://www.jsa.or.jp）
- ISO 9241-210:2019 也是付費（CHF 173 from iso.org）
- **Action**: design-team standard 可以 cite 標準名稱 + 出版日 + 對應關係，不需附全文連結 — 標準學術 cite 方式

---

# References

## Anglo-American Sources（一手）

### Books

1. Norman, Donald A. (2013). *The Design of Everyday Things: Revised and Expanded Edition*. Basic Books. ISBN 978-0465050659. [https://jnd.org/books/the-design-of-everyday-things-revised-and-expanded-edition/](https://jnd.org/books/the-design-of-everyday-things-revised-and-expanded-edition/)
2. Garrett, Jesse James (2010). *The Elements of User Experience: User-Centered Design for the Web and Beyond*, 2nd Edition. New Riders. ISBN 978-0321683687. [Pearson catalog](https://www.pearson.com/en-us/subject-catalog/p/Garrett-Elements-of-User-Experience-The-User-Centered-Design-for-the-Web-and-Beyond-2nd-Edition/P200000000272/9780321683687)
3. Verganti, Roberto (2009). *Design-Driven Innovation: Changing the Rules of Competition by Radically Innovating What Things Mean*. Harvard Business Review Press. ISBN 978-1422124826. [HBR Store](https://store.hbr.org/product/design-driven-innovation-changing-the-rules-of-competition-by-radically-innovating-what-things-mean/2482)
4. Gibson, James J. (1979). *The Ecological Approach to Visual Perception*. Houghton Mifflin. (Routledge Classic Edition 2014, ISBN 978-1848725782). [Routledge](https://www.routledge.com/The-Ecological-Approach-to-Visual-Perception-Classic-Edition/Gibson/p/book/9781848725782)
5. Osgood, Charles E.; Suci, George J.; Tannenbaum, Percy H. (1957). *The Measurement of Meaning*. University of Illinois Press. ISBN 978-0252745393. [UI Press](https://www.press.uillinois.edu/books/?id=p745393)
6. Koren, Leonard (1994). *Wabi-Sabi for Artists, Designers, Poets & Philosophers*. Stone Bridge Press. ISBN 978-1880656129. [Goodreads](https://www.goodreads.com/book/show/42190.Wabi_Sabi)

### Articles & Papers

7. Nielsen, Jakob (1994 / updated 2024-01-30). "10 Usability Heuristics for User Interface Design". Nielsen Norman Group. [https://www.nngroup.com/articles/ten-usability-heuristics/](https://www.nngroup.com/articles/ten-usability-heuristics/)
8. Prater, Sophia V. (2015-10-20). "Object-Oriented UX". *A List Apart*. [https://alistapart.com/article/object-oriented-ux/](https://alistapart.com/article/object-oriented-ux/)
9. Prater, Sophia V. (2016-04-19). "OOUX: A Foundation for Interaction Design". *A List Apart*. [https://alistapart.com/article/ooux-a-foundation-for-interaction-design/](https://alistapart.com/article/ooux-a-foundation-for-interaction-design/)
10. Roto, V.; Law, E.L-C.; Vermeeren, A.P.O.S.; Hoonhout, J. (2011). *User Experience White Paper: Bringing clarity to the concept of user experience*. Dagstuhl Seminar 10373. [http://www.allaboutux.org/uxwhitepaper](http://www.allaboutux.org/uxwhitepaper) / [Dagstuhl Seminar 10373](https://www.dagstuhl.de/en/seminars/seminar-calendar/seminar-details/10373)
11. Nagamachi, M. (1995). "Kansei Engineering: A new ergonomic consumer-oriented technology for product development". *International Journal of Industrial Ergonomics*, 15(1):3-11. DOI [10.1016/0169-8141(94)00052-5](https://www.sciencedirect.com/science/article/abs/pii/0169814194000525).

### Standards & Guidelines

12. W3C (2024-12-12 republish, originally 2023-10-05). *Web Content Accessibility Guidelines (WCAG) 2.2*. W3C Recommendation. [https://www.w3.org/TR/WCAG22/](https://www.w3.org/TR/WCAG22/)
13. ISO (2019). *ISO 9241-210:2019 Ergonomics of human-system interaction — Part 210: Human-centred design for interactive systems*. [https://www.iso.org/standard/77520.html](https://www.iso.org/standard/77520.html)
14. Apple Inc. *Human Interface Guidelines*. Apple Developer Documentation. [https://developer.apple.com/design/human-interface-guidelines/](https://developer.apple.com/design/human-interface-guidelines/) + [Tips: UI Design Dos and Don'ts](https://developer.apple.com/design/tips/) (44 pt × 44 pt)
15. Google (2021–). *Material Design 3*. [https://m3.material.io/](https://m3.material.io/) + [Foundations / Designing](https://m3.material.io/foundations/designing/structure) (48 dp × 48 dp) + [Interaction / States](https://m3.material.io/foundations/interaction/states/applying-states)

## Japanese Sources（一手）

16. 長町三生 (1989).《感性工学—感性をデザインに活かすテクノロジー》海文堂出版. ISBN 978-4303713201. [海文堂出版](https://www.kaibundo.jp/1989/11/01021/)
17. 深澤直人 (2005).《デザインの輪郭》TOTO 出版. ISBN 978-4887062603. [TOTO 出版](https://jp.toto.com/publishing/detail/A0260.htm)
18. 原研哉 (2003).《デザインのデザイン》岩波書店. ISBN 978-4000240055. [岩波書店](https://www.iwanami.co.jp/book/b263308.html)
19. 原研哉 (2008).《白》中央公論新社. ISBN 978-4120039379. [中央公論新社](https://www.chuko.co.jp/tanko/2008/05/003937.html)
20. Hara, Kenya (2007). *Designing Design*. Lars Müller Publishers. ISBN 978-3037781050. [Lars Müller Publishers](https://www.lars-mueller-publishers.com/designing-design)
21. 磯崎新 (2003).《建築における「日本的なもの」》新潮社. ISBN 978-4104587018. [新潮社](https://www.shinchosha.co.jp/book/458701/)
22. 安藤昌也 (2016).《UX デザインの教科書》丸善出版. ISBN 978-4621300374. [丸善出版](https://www.maruzen-publishing.co.jp/book/b10120504.html)
23. 黒須正明 (2020).《UX 原論—ユーザビリティから UX へ》近代科学社. ISBN 978-4764906112. [近代科学社](https://www.kindaikagaku.co.jp/book_list/detail/9784764906112/)
24. ソシオメディア・上野学・藤井幸多 (2020).《オブジェクト指向 UI デザイン—使いやすいソフトウェアの原理》技術評論社. ISBN 978-4297113513. [技術評論社](https://gihyo.jp/book/2020/978-4-297-11351-3)
25. JIS Z 8530:2021 *人間工学—人とシステムとのインタラクション—インタラクティブシステムの人間中心設計*. 日本規格協会. [JSA Webdesk](https://webdesk.jsa.or.jp/books/W11M0090/index/?bunsyo_id=JIS+Z+8530:2021)

## Anti-pattern citations to be REMOVED

26. ❌ btrax 「寿司職人から学ぶUXデザイン 6つの極意」(blog.btrax.com)
27. ❌ KOGEI STANDARD「日本の美意識 間と余白」(kogeistandard.com)
28. ❌ J-SEMS / J-STAGE / AIIT references for Osgood SD 法
29. ❌ ガリバーコラム for 引き算のデザイン
30. ❌ studio-tabi for 佇まい
31. ❌ Wikipedia for わびさび (replace with Koren 1994)

---

> [!success] Phase 2 完成
> 18 個 research questions 全部驗證，14 個 metadata 取得 high-confidence primary sources，4 個項目標記 user verification needed（不阻塞 standards synthesis）。JP 整合決定維持 FULL HIGH。8 個 standards files plan ready for Phase 3 (commit 1 of skill-redesign).
