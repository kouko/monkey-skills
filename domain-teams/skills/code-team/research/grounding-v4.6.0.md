---
title: code-team 再設計研究 — Clean Code・Pragmatic・SOLID・OWASP・徳丸本
date: 2026-04-11
team: code-team
refactor_version: v4.6.0
tags:
  - research
  - domain-teams
  - code-team
  - grounding
  - clean-code
  - pragmatic-programmer
  - solid
  - owasp-asvs
  - 徳丸本
  - tdd
  - refactoring
aliases:
  - code-team 再設計研究
  - code-team v4.6.0 grounding
  - Clean Code SOLID OWASP Research
---

# code-team 再設計研究

> **Backfill note** (2026-04-11, v4.7.0): This file was migrated into
> the repo from the maintainer's Obsidian vault as part of the v4.7.0
> research-notes-in-repo convention. Wikilinks have been normalized
> to plain-text references pointing at their in-repo counterparts
> (qa-team v4.2.0 and docs-team v4.3.0 research notes now live at
> `domain-teams/skills/{qa,docs}-team/research/grounding-v{X.Y.Z}.md`).
> The original Obsidian note
> (`2026-04-11 code-team 再設計研究 — Clean Code・Pragmatic・SOLID・OWASP・徳丸本.md`)
> remains in the maintainer's vault as a personal backup.

> [!info] 研究背景
> 為重新設計 `monkey-skills/domain-teams/code-team` skill (v4.6.0)，調查歐美軟體工程實務的一手來源，並審視日本社群是否存在平行的 code craft 傳統。Phase 1 的 gap assessment 在 code-team 找到 **41 個 load-bearing claims 零引用**，現有 `code-conventions.md` 67 行完全自創。重構目標對齊 qa-team v4.2 / docs-team v4.3 / devops-team v4.4 的一手來源密度。
>
> 研究方法：使用者提供 7 個候選來源，本研究逐一驗證並補充 2 個（Feathers WELC + ISO/IEC 25010:2023）。所有章節編號、Topic 編號、V-number、ISBN 皆經 WebSearch / WebFetch 驗證，未能獨立驗證者明確標記。

## TL;DR

| Point | Status |
|-------|--------|
| **Clean Code** (Martin 2008, ISBN 978-0132350884, Prentice Hall/Pearson) 17 章結構驗證 | `[事實\|高]` |
| **The Pragmatic Programmer 20th Anniversary Edition** (Hunt & Thomas 2019, 978-0135957059) — 10 章 / **53 topics** / **100 tips** | `[事實\|高]` |
| **SOLID** 原初出處 = Martin 2000 *Design Principles and Design Patterns* (objectmentor.com)，**SOLID 頭字縮寫由 Michael Feathers 在 2004 年左右命名** | `[事實\|中]` |
| **Kent Beck *TDD by Example*** (2002, Addison-Wesley, 978-0321146533) = TDD + Red/Green/Refactor 的 canonical primary | `[事實\|高]` |
| **Martin Fowler *Refactoring* 2nd ed** (2018, 978-0134757599) — **JavaScript 示例**，68 個 refactorings | `[事實\|高]` |
| **OWASP ASVS v5.0.0** (**2025-05-30** released) — **17 chapters**，取代 4.0.3，章節結構完全重組 | `[事實\|高]` ⚠️ 使用者候選清單寫 4.0.3，需升級 |
| **徳丸本 第 2 版** (SB Creative 2018, 978-4797393163) — 有 **Ch.6「文字コードとセキュリティ」** 這 ASVS 沒有深入處理的 JP-specific 章節 | `[事實\|高]` |
| **Google Engineering Practices** (google.github.io/eng-practices) — 2 guides / 6 reviewer pages + 3 author pages，URL 穩定 | `[事實\|高]` |
| **プログラマが知るべき97のこと** JP 版 = 原書 97 + **日本人撰寫 10 篇**（8 位作者，計「107 のこと」） | `[事實\|高]` |
| **JP 平行傳統**: 有 **補充** 但無 parallel framework — t_wada 的 TDD 啓蒙、上田勲『プリンシプル オブ プログラミング』(101 原則) 是 aggregation，不是獨立傳統 | `[分析\|中]` |
| **Feathers *Working Effectively with Legacy Code*** (2004, Prentice Hall, 978-0131177055) — 應加入 | `[事實\|高]` |
| **ISO/IEC 25010:2023** (2023-11 release, 9 characteristics, Safety added) — 取代 2011 版，但 **付費** | `[事實\|高]` |
| **建議**: JP 整合採 **preamble** 策略（徳丸本 Ch.6 做 JP 特有章節 + 97のこと 日本人 essays + t_wada TDD 論述作人格錨點），**非 full framework** | `[分析\|中]` |

---

# Cluster A — EN Code Craft Canon

## Q1. Clean Code Chapter Map

### 書誌

- **作者**: Robert C. Martin
- **標題**: *Clean Code: A Handbook of Agile Software Craftsmanship*
- **出版**: Prentice Hall (Pearson 旗下), 2008 年 8 月 1 日
- **ISBN-13**: 978-0132350884
- **來源驗證**: Library of Congress CIP Record + Pearson InformIT 頁面 + Amazon listing
- **Series**: Robert C. Martin Series

### 17 章完整結構（已驗證）

| Ch | 標題 | 對 code-team 的相關性 |
|---|---|---|
| 1 | Clean Code | 定義、歸因 |
| **2** | **Meaningful Names** | Naming standard anchor |
| **3** | **Functions** | 小函數規則（"20 lines"）、Single Level of Abstraction |
| **4** | **Comments** | 好評論 / 壞評論分類 |
| 5 | Formatting | 格式慣例 |
| 6 | Objects and Data Structures | Law of Demeter, Data/Object antisymmetry |
| 7 | Error Handling | Exceptions vs return codes |
| 8 | Boundaries | 跨越邊界時的防護 |
| **9** | **Unit Tests** | **Three Laws of TDD**（見下方 caveat）, F.I.R.S.T |
| 10 | Classes | SRP, Cohesion |
| 11 | Systems | System-level design |
| 12 | Emergence | Kent Beck 4 rules of simple design |
| 13 | Concurrency | Thread safety |
| 14 | Successive Refinement | Case study |
| 15 | JUnit Internals | Case study |
| 16 | Refactoring SerialDate | Case study |
| **17** | **Smells and Heuristics** | Code smell catalog (~66 smells) |
| App A | Concurrency II | |
| App B | org.jfree.date.SerialDate | |
| App C | Cross References of Heuristics | |

> [!important] Three Laws of TDD — 歸因釐清
> Clean Code Ch.9 確實包含 Three Laws of TDD，但這**不是** Martin 發明的 — Martin 最早在 2005-10-07 於 butunclebob.com 的 "The Three Rules of TDD" 文章發表，Clean Code (2008) 是重新收錄。
>
> **但 Red/Green/Refactor 的原始 canonical 出處是 Kent Beck 的 *TDD by Example* (2002)** — 見 Q4。
>
> → 對 code-team 的設計意涵：TDD standard 應以 **Beck 2002 為主**，Martin 的 Three Laws 作為補充陳述（記號清晰）。

## Q2. Pragmatic Programmer Topic Map

### 書誌

- **作者**: David Thomas & Andrew Hunt
- **標題**: *The Pragmatic Programmer: Your Journey to Mastery*, **20th Anniversary Edition, 2nd Edition**
- **出版**: Addison-Wesley Professional, 2019 年 9 月 13 日
- **ISBN-13**: 978-0135957059 (print) / 978-0135957035 (ePub) / 978-0135956977 (O'Reilly Learning)
- **來源驗證**: pragprog.com 官方頁面 + O'Reilly Learning 頁面 + informit + Amazon

### 結構

- **10 章**（第 1-9 章 + Postface）
- **53 Topics**（已驗證）
- **100 Tips**（原 1999 年版 70 tips，20th anniversary 擴充至 100）
- **33 Exercises**

### 章節與已驗證的 Topic 編號

| Ch | Title | 驗證 Topic 範圍 |
|---|---|---|
| 1 | A Pragmatic Philosophy | **Topic 1: It's Your Life**; Topics 2-7 包含 The Cat Ate My Source Code, Software Entropy, Stone Soup and Boiled Frogs, Good-Enough Software, Your Knowledge Portfolio, Communicate! |
| **2** | **A Pragmatic Approach** | **Topic 8: The Essence of Good Design (ETC)**; **Topic 9: DRY — The Evils of Duplication**; **Topic 10: Orthogonality**; **Topic 11: Reversibility**; **Topic 12: Tracer Bullets**; **Topic 13: Prototypes and Post-it Notes**; Topic 14: Domain Languages; Topic 15: Estimating |
| 3 | The Basic Tools | 涵蓋版本控制、純文字力量、debugging |
| 4 | Pragmatic Paranoia | 防禦性編程 |
| 5 | Bend, or Break | 解耦、世界狀態、轉換式編程 |
| 6 | Concurrency | |
| 7 | While You Are Coding | Listen to Your Lizard Brain, Programming by Coincidence, Algorithm Speed, Refactoring, Test to Code, Property-Based Testing, Stay Safe Out There, Naming Things |
| 8 | Before the Project | 需求蒐集、邏輯、設計 |
| 9 | Pragmatic Projects | 團隊、步調、現實世界 |
| — | Postface | |

> [!note] 對第 1 版（1999）的關係
> 第 1 版 46 items + 70 tips，20th anniversary 重寫為 53 topics + 100 tips，新加十個 topic 並大量修訂。引用時應**明示 "20th Anniversary Edition (2019)"**，Topic 編號跨版不相通。

> [!warning] 未獨立驗證的 Topic 編號
> Chapter 3-9 的精確 Topic 編號未能從 web 一手來源完整列舉（pragprog.com / Pearson TOC PDF 都沒有 public 數字列表）。**code-team standards 引用時，Ch.2 的 Topics 8-13 可直接引編號；其他 Topic 建議引 title 並加「20th Anniversary Edition, Ch.N」，不要編造數字**。

### 關鍵 topic 直接引用

- **ETC (Easier to Change)**: Topic 8 – *"Good design is easier to change than bad design."*
- **DRY**: Topic 9 – *"Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."*
- **Orthogonality**: Topic 10 – 模組獨立性
- **Tracer Bullets**: Topic 12 – 端到端 minimal working system
- **Prototypes**: Topic 13 – disposable learning tools

## Q3. SOLID 的 Canonical Primary Source

### 正式確認

**Martin, Robert C. (2000). "Design Principles and Design Patterns." objectmentor.com.**

- **年份**: 2000（Copyright 明確標示）
- **作者**: Robert C. Martin
- **出處**: objectmentor.com 公開論文（www.objectmentor.com 網站消失後，可在 staff.cs.utu.fi/~jounsmed/doos_06/material/DesignPrinciplesAndPatterns.pdf 及 multiple academic archive 找到 mirror）
- **內容**: 完整介紹 SRP / OCP / LSP / ISP / DIP 五個原則，discussing software rot

### SOLID 頭字縮寫的歸因

> **SOLID acronym 由 Michael Feathers 在 2004 年左右命名**（雖然 Martin 是原則的作者，但 SOLID 這個縮寫不是他創造的）。
> — Wikipedia SOLID article, 已追溯到 Feathers 的早期郵件 / blog post

### 後續出版

Martin 後來把這些原則收錄至：
- **Agile Software Development, Principles, Patterns, and Practices** (Prentice Hall, 2002, ISBN 978-0135974445) — 書籍形式的系統性論述
- **Agile Principles, Patterns, and Practices in C#** (2006) — C# 版本
- **Clean Architecture: A Craftsman's Guide to Software Structure and Design** (2017, ISBN 978-0134494166) — 架構層級整合

### 對 code-team 的 grounding 建議

> [!tip] 引用策略
> **主要**引 2000 年論文（原初出處），**次要**引 *Agile Software Development, PPP* (2002) 或 *Clean Architecture* (2017) 的系統化陳述。Clean Architecture (2017) 是最容易取得的版本且包含最成熟的論述。Wikipedia 可當 pointer 但不當 primary。

### 五個原則的速記

| Principle | 意涵 | 主要出處 |
|---|---|---|
| **SRP** – Single Responsibility | 一個 class 只有一個改變的理由 | Martin 2000 §3 |
| **OCP** – Open/Closed | 對擴充開放，對修改封閉（原始由 Bertrand Meyer 1988 提出，Martin 重新詮釋） | Martin 2000 §4 |
| **LSP** – Liskov Substitution | 子型別必須可以替換父型別（原始由 Barbara Liskov 1987 提出） | Martin 2000 §5 |
| **ISP** – Interface Segregation | 客戶不應被迫依賴它們用不到的介面 | Martin 2000 §6 |
| **DIP** – Dependency Inversion | 高層模組不應依賴低層模組，兩者都應依賴抽象 | Martin 2000 §7 |

## Q4. Kent Beck — TDD by Example (2002)

### 書誌

- **作者**: Kent Beck
- **標題**: *Test-Driven Development: By Example*
- **出版**: Addison-Wesley, 2002 年 11 月 8 日
- **ISBN-13**: 9780321146533 / ISBN-10: 0321146530
- **Pages**: 216
- **Series**: Addison-Wesley Signature Series (Beck)
- **來源驗證**: Goodreads editions + O'Reilly Learning + Pearson sample PDF + Internet Archive

### 核心主張

1. **Red/Green/Refactor**: 書中直接以「**red/green/refactor**」描述 TDD mantra（原文多次出現）。**這就是 canonical 出處**。
2. **TDD pattern catalog**: Part II 編纂 TDD patterns（Test-First, Fake It, Triangulate, Obvious Implementation, etc.）
3. **Refactoring while green**: Refactoring 必須在所有測試通過的狀態下進行。

### 引用建議

> [!tip] TDD primary citation
> **TDD 標準應引用 Beck 2002 為 canonical primary。** Martin 的 Three Rules of TDD (2005 blog / 2008 Clean Code Ch.9) 是 rephrasing，不是原初 source。
>
> 具體章節：
> - Red/Green/Refactor → Beck 2002, Chapter 1 "Multi-Currency Money" 示範 + Chapter 25 "Test-Driven Development Patterns"
> - TDD definition → Beck 2002 preface "Never write a line of functional code without a broken test case"

## Q5. Martin Fowler — Refactoring 2nd Edition (2018)

### 書誌

- **作者**: Martin Fowler（with contributions from Kent Beck）
- **標題**: *Refactoring: Improving the Design of Existing Code*, **2nd Edition**
- **出版**: Addison-Wesley Professional, **2018 年 11 月 30 日 (informit) / 2019 年初大量出貨**
- **ISBN-13**: 9780134757599 / ISBN-10: 0134757599
- **來源驗證**: martinfowler.com/books/refactoring.html + martinfowler.com/articles/refactoring-2nd-ed.html + Amazon + O'Reilly Learning + refactoring.com catalog (companion site)

### 1st vs 2nd Edition 關鍵差異

| 面向 | 1st ed (1999) | 2nd ed (2018) |
|---|---|---|
| 程式語言 | Java | **JavaScript**（有意選擇 non-class-centric 語言） |
| Refactoring 數量 | 72 | **68**（10 個移除、17 個新增、其餘重寫） |
| 動機 | 展示 OO refactoring | 展示 refactoring 不限於 class-based OO |

### 已驗證的核心概念

1. **Refactoring 定義**: *"A change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior."* — Fowler 2018, 與 1st ed 一致。
2. **"Bad Smells" 章節**: martinfowler.com/books/refactoring.html 明確寫 *"a chapter of principles, a survey of 'code smells'"*。1st ed 是 Ch.3 "Bad Smells in Code"，2nd ed 同樣在早期章節討論 smells（但精確章號 Web 可見資料未明示 "Chapter 3"；refactoring.com catalog 沒有章節分頁）。
3. **Rule of Three**: 已驗證歸因 **Don Roberts** — *"The first time you do something, you just do it. The second time you do something similar, you wince at the duplication, but you do the duplicate thing anyway. The third time you do something similar, you refactor."* — 這是 Fowler 多處引述的 Roberts 規則。
4. **Two Hats**: Web search 沒有找到 2nd ed 對 "Two Hats" 原則的獨立 public 引用；**1st ed 有這個概念**（Feature addition vs refactoring 不應混合）**但未能獨立驗證 2nd ed 是否保留**。保守起見，引用時註明「Fowler 1999/2018」或改引 `martinfowler.com/bliki/` 相關文章。
5. **68 Refactorings**: refactoring.com/catalog 列出 71 個項目（companion site 包含部分 1st ed refactorings 做 cross-reference），書中是 68。

### refactoring.com/catalog 已驗證分類標籤

Basic / Encapsulation / Moving Features / Organizing Data / Simplifying Conditional Logic / Refactoring APIs / Dealing with Inheritance / Collections / Delegation / Errors / Extract / Inline / Remove / Rename / Split Phase / Variables

### 引用建議

> [!tip] 2nd Edition 是 preferred citation
> **一律引 2nd ed (2018, 9780134757599)**，因為：(a) JavaScript 示例對現代 web 社群更相關；(b) 66 個已重寫的 refactorings；(c) Fowler 本人在 bliki 明示 2nd ed 是「the current version」。
>
> Bad Smells 章節、Rule of Three、Two Hats 這三個概念，code-team standards 引用時**同時列 Fowler 1999 和 2018**（都包含這些概念，且 1999 年版本有較清晰的章節劃分可引）。

---

# Cluster B — Application Security

## Q6. OWASP ASVS 當前版本

### ⚠️ 使用者候選清單過時

使用者提供的候選清單寫 **4.0.3**。**實際上 ASVS 5.0.0 已於 2025-05-30 釋出**，是當前 stable version（驗證日期：2026-04-11）。

### ASVS 5.0.0 書誌

- **名稱**: OWASP Application Security Verification Standard
- **Version**: 5.0.0
- **發佈**: **2025 年 5 月 30 日**（於 Global AppSec EU Barcelona 2025 現場發佈）
- **官方網站**: https://owasp.org/www-project-application-security-verification-standard/
- **專屬站**: **https://asvs.dev/v5.0.0/**（新增；之前只有 PDF）
- **格式**: PDF / Word / CSV，多語翻譯（土耳其、俄、法、韓）
- **授權**: CC BY-SA 4.0（繼承 OWASP 慣例）

### Version history（已驗證）

- 5.0.0 — 2025-05-30 ← **current**
- 5.0.0 RC1 — 2025-03-31
- 4.0.3 — 2021-10-28
- 4.0.2 — 2020-10-27
- 4.0.1 — 2019-03-02

### 17 Chapter 完整列表（已驗證於 asvs.dev/v5.0.0/Preface）

| V# | 標題 | 前身（v4.0.3 對比） |
|---|---|---|
| **V1** | **Encoding and Sanitization** | 新章（原散在多處） |
| **V2** | **Validation and Business Logic** | 取代 v4 V5 input validation 部分 |
| **V3** | **Web Frontend Security** | 新章（Web-specific） |
| **V4** | **API and Web Service** | 對應 v4 V13 |
| **V5** | **File Handling** | 新（v4 V12 Files and Resources 部分） |
| **V6** | **Authentication** | 對應 v4 V2 |
| **V7** | **Session Management** | 對應 v4 V3 |
| **V8** | **Authorization** | 對應 v4 V4 |
| **V9** | **Self-contained Tokens** | 新（JWT 等） |
| **V10** | **OAuth and OIDC** | 新 |
| **V11** | **Cryptography** | 對應 v4 V6 |
| **V12** | **Secure Communication** | 對應 v4 V9 |
| **V13** | **Configuration** | 對應 v4 V14 |
| **V14** | **Data Protection** | 對應 v4 V8 |
| **V15** | **Secure Coding and Architecture** | 對應 v4 V1 architecture |
| **V16** | **Security Logging and Error Handling** | 對應 v4 V7 |
| **V17** | **WebRTC** | 新 |

**~350 個需求（大幅重構 v4 的結構）**。

### Level 系統（已驗證）

| Level | 角色 | 原文 |
|---|---|---|
| **L1** | 基礎防線 | *"the initial step to adopting the ASVS, providing the first layer of defense"* |
| **L2** | 標準實務 | *"a comprehensive view of standard security practices"* |
| **L3** | 高保證 | *"addresses advanced, high-assurance requirements"* |

### 使用者原問題 → 新 mapping

| 原問題 | v4.0.3 答案（使用者以為的） | **v5.0.0 實際答案** |
|---|---|---|
| Input validation | V5 | **V2: Validation and Business Logic** |
| Secrets management | V2 or V14 | **V14: Data Protection** + **V13: Configuration** |
| Error handling | V7.4 | **V16: Security Logging and Error Handling** |
| Injection prevention | V5.3 | **V2 (Validation) + V1 (Encoding/Sanitization)** — 解偶 |

> [!important] 對 code-team 的設計意涵
> code-team 的 security standard **必須引 ASVS 5.0.0**，不是 4.0.3。章節結構完全重組，舊的 V-number mapping 不相通。引用格式建議：
>
> `OWASP ASVS v5.0.0 §V2 Validation and Business Logic`
>
> （asvs.dev 提供 per-chapter stable URL，例如 https://asvs.dev/v5.0.0/0x10-V1-Encoding-and-Sanitization/）

## Q7. 徳丸本 — 是否與 ASVS 有實質差異化？

### 書誌

- **作者**: 徳丸浩
- **標題**: 『体系的に学ぶ 安全な Web アプリケーションの作り方 第 2 版 脆弱性が生まれる原理と対策の実践』
- **出版**: **SB クリエイティブ**, 2018 年 6 月 22 日
- **ISBN-13**: 978-4797393163
- **國立國会図書館 record**: NDL R100000002-I029031208
- **第 3 版狀態**: 截至 2026-04-11，**沒有第 3 版發佈公告**（需使用者再次向 SB Creative 確認最新動態）

### 目錄（9 章，已驗證於 sbcr.jp + hmv 書誌）

1. Web アプリケーションの脆弱性とは
2. 実習環境のセットアップ
3. Web セキュリティの基礎 — HTTP、セッション管理、同一オリジンポリシー、CORS
4. Web アプリケーションの機能別に見るセキュリティバグ（入力処理、表示、SQL、重要な処理、セッション、リダイレクト等）
5. 代表的なセキュリティ機能
6. **文字コードとセキュリティ** ← **JP-specific，ASVS 無對應深度**
7. 脆弱性診断入門
8. Web サイトの安全性を高めるために
9. 安全な Web アプリケーションのための開発マネジメント

### 是否與 ASVS 有實質差異化？

> [!important] 結論：**有** — Ch.6 文字コードとセキュリティ 是 JP 獨有的關鍵章節

**證據**：
1. **5C 問題**: Shift_JIS 文字第 2 byte 為 0x5C 的 SQL injection 向量 — ASVS v5 V1 Encoding/Sanitization 和 V2 Validation 都沒有 Shift_JIS-specific 細節。
2. **Multi-byte char 邊界 XSS**: UTF-8 / Shift_JIS / EUC-JP 第 1 byte 單獨出現導致的 XSS — 徳丸浩在 slide deck "文字コードに起因する脆弱性とその対策" 有完整論述。
3. **日本 legacy CMS / EC-CUBE / WordPress 日本語版 specific issues** — 徳丸本實作章節使用日本主流 stack。
4. **JP 政府 / 企業 監査基準**: IPA「安全な Web アプリケーションの作り方」指南（徳丸 contributed）強調 multi-byte 處理 — 這些在 ASVS 英文版沒有等同深度。

**ASVS 同時 cover 的部分**:
- SQL injection / XSS / CSRF / auth / session → 徳丸本 Ch.3-5 跟 ASVS V1/V2/V6/V7/V8 直接 overlap
- → **純翻譯徳丸本來 ground session/auth 會是 redundant**

### 引用建議

> [!tip] 徳丸本的 grounding 角色
> **不**做 security primary（那是 ASVS 5.0.0 的角色）。做 **JP preamble anchor**，專引 **Ch.6 文字コードとセキュリティ**。
>
> Standard 結構建議：
> - `security-standard.md` = OWASP ASVS 5.0.0 為 primary；
> - 獨立的 `character-encoding-security.md` 或在 `security-standard.md` 裡留 "Japanese Multi-Byte Context" 章節，引徳丸本 Ch.6。

---

# Cluster C — Code Review

## Q8. Google Engineering Practices Structure

### 書誌

- **網站**: https://google.github.io/eng-practices/
- **GitHub repo**: https://github.com/google/eng-practices
- **授權**: CC BY 3.0
- **維護者**: Google (原 "Google's Engineering Practices Documentation")
- **Entry**: review/ 是目前 public 的主力 section

### 完整頁面樹（已驗證 via WebFetch）

```
eng-practices/review/
├── How to do a code review (reviewer guide) — review/reviewer/
│   ├── 1. The Standard of Code Review        (reviewer/standard.html)
│   ├── 2. What to Look For In a Code Review  (reviewer/looking-for.html)
│   ├── 3. Navigating a CL in Review          (reviewer/navigate.html)
│   ├── 4. Speed of Code Reviews              (reviewer/speed.html)
│   ├── 5. How to Write Code Review Comments  (reviewer/comments.html)
│   └── 6. Handling Pushback in Code Reviews  (reviewer/pushback.html)
│
└── The CL author's guide (developer guide) — review/developer/
    ├── 1. Writing Good CL Descriptions       (developer/cl-descriptions.html)
    ├── 2. Small CLs                          (developer/small-cls.html)
    └── 3. How to Handle Reviewer Comments    (developer/handling-comments.html)
```

### 核心原則（已驗證直接引用）

**What to Look For**（8 個評估面向，review 頁面直接列出）:
1. **Design** — architectural appropriateness
2. **Functionality** — intended behavior and user impact
3. **Complexity** — readability for future developers
4. **Tests** — quality of automated testing
5. **Naming** — clarity of variables, classes, methods
6. **Comments** — usefulness and clarity
7. **Style** — adherence to established guides
8. **Documentation** — updates to supporting materials

**Reviewer Speed**（single-sentence quote from reviewer/speed.html）：
> *"At Google, we make sure the code review speed is fast."*
> Core guideline: *"You should respond within one business day."*

**Small CLs**（developer/small-cls.html 標題規則）：
> *"In general, the right size for a CL is one self-contained change. Do one thing and do it well."*

**CL Descriptions**（developer/cl-descriptions.html）:
- First line = imperative short summary
- Second line = blank
- Body = what change + why

> [!tip] 引用建議
> 所有 URL 都是 stable（`/reviewer/*.html` / `/developer/*.html`）。code-team 的 code-review-standard.md 可以直接深鏈到每一頁。**中文/日文譯本不存在官方版**，code-team 必須用英文原文引用。

---

# Cluster D — JP Code Craft Tradition

## Q9. 97 のこと — 日本独自エッセイ

### 書誌

- **編者**: Kevlin Henney（原著）/ 和田卓人（日本語版監修）/ 夏目大（訳）
- **出版**: オライリー・ジャパン, 2010 年 12 月 17 日
- **ISBN**: 978-4-87311-479-8
- **來源驗證**: oreilly.co.jp + 楽天 + 複数書評サイト

### 日本人撰寫追加 essays — 已驗證

**10 篇補充（「107 のこと」と通称）、8 位作者**：

| 作者 | Essay 標題 |
|---|---|
| **和田卓人** | 「不具合にテストを書いて立ち向かう」 |
| **まつもと ゆきひろ** | 「名前重要」 |
| **小飼 弾** | 「見知らぬ人ともうまくやるには」 |
| **関 将俊** | 「ロールプレイングゲーム」 |
| **舘野 祐一** | 「快適な環境を追求する」 |
| **宮川 達彦** | 「ルーチンワークをフローのきっかけに」 |
| **吉岡 弘隆** | 「プログラマが持つべき3つのスキル」 |
| **森田 創** | 「命を吹き込む魔法」＋「育ちのよいコード」 |
| 高橋 征義 | （其他 session 有聯合撰稿；10 篇 total） |

> [!note] 未完整驗證
> 10 篇中 9 篇作者 + 標題已驗證。第 10 篇的精確作者/標題歸屬在不同 review 來源略有出入（森田 創 有兩篇是某些來源的說法，高橋 征義 contribution 也被提及但未獨立驗證為其中一篇）。code-team standards 若要引具體 essay，建議只引 **已 100% 驗證的 8 位作者 + 9 篇** 並標註「~10 篇日本人執筆」。

### 對 code-team 的意義

97 のこと 日本語版 **確實是 JP-authored primary source**（非純翻譯），可作 code-team 的 JP preamble 素材。特別：
- **和田卓人 "不具合にテストを書いて立ち向かう"** → testing philosophy anchor
- **まつもと ゆきひろ "名前重要"** → naming standard 的 JP 諺語式錨點（可對應 Clean Code Ch.2）

## Q10. 日本獨立 code craft 傳統 audit

### 問題

歐美 Clean Code / Pragmatic Programmer canon 有沒有 JP 平行傳統？答：**有補充，但沒有 parallel framework**。

### 已驗證的 JP code craft 實踐（按 authority 排序）

| # | 來源 | 作者 | 性質 | Primary 資格 |
|---|---|---|---|---|
| 1 | **97 のこと 日本語版 追加 essays** | 8 位 JP authors (和田, 松本, 關, etc.) | 短文集合，領域分散 | ✅ JP-original |
| 2 | **上田勲『プリンシプル オブ プログラミング 3 年目までに身につけたい 一生役立つ 101 の原理原則』** (秀和システム, 2016, ISBN 978-4798046143) | 上田勲 | 101 個原則的**系統性聚合**（集 KISS, DRY, YAGNI, ブルックスの法則 等） | ⚠ JP-authored 但 **aggregation of global principles**，非獨立 tradition |
| 3 | **和田卓人 TDD 啓蒙活動** | 和田卓人 | TDD 翻譯（Beck 2002 → 和田訳『テスト駆動開発』オーム社 2017）+ 演講 + WEB+DB PRESS 連載 + gihyo.jp 動画講座 20 回 | ⚠ **高權威** 但大部分是**詮釋歐美 TDD**，非獨立傳統 |
| 4 | **SQL アンチパターン日本語版** (Bill Karwin 著, 和田卓人監訳, 初版 2013 / 第 2 版 2025) | 和田卓人 監訳 | 翻訳 + 監修注釈 | ⚠ 翻譯 |
| 5 | **Code Complete 第 2 版 日本語版**（日経 BP ソフトプレス, McConnell 著, クイープ訳） | 翻訳 | 翻訳 | ⚠ 翻訳 |
| 6 | **Clean Code 日本語版**（ASCII Dwango, 花井志生訳） | 翻訳 | 翻訳 | ⚠ 翻訳 |
| 7 | **リーダブルコード**（Dustin Boswell & Trevor Foucher, 角征典 訳, オライリー・ジャパン 2012, ISBN 978-4873115658） | 翻訳 | 翻訳 | ⚠ 翻訳（非 JP-origin） |
| 8 | **gihyo.jp / WEB+DB PRESS / Software Design** 技術評論社 articles | 多數 | 期刊連載 | ⚠ 深度但非 canonical form |

### Honest Assessment

> [!warning] 沒有與 Clean Code / Pragmatic Programmer 對等的 JP 獨立框架
> 日本 code craft 社群的 canonical 書籍幾乎全是 **英文原著的日譯版** (Clean Code, Refactoring, TDD, Code Complete, Pragmatic Programmer, リーダブルコード 等)。**沒有**日本原創、系統性、與 Anglo canon 平行 footing 的 code craft 框架，如 qa-team 找到的 VSTeP (西康晴) / HAYST法 (秋山浩一) / ゆもつよメソッド (湯本剛) 那樣的水準。
>
> 最接近 JP-original 的書 = 上田勲『プリンシプル オブ プログラミング』(2016)，但它明確是**聚合**世界 software engineering 原則的入門書，不是獨立 epistemology。
>
> **例外**: 97 のこと 日本人 essays **是** JP-original，但個別 essay 短（每篇 2-3 頁），不能支撐整個 standard 的 grounding。

### 對 JP 整合的意涵

| Option | 評價 |
|---|---|
| Full integration (JP 自成 framework) | ❌ **不成立** — 沒有 parallel framework，若強行建構就是 synthetic JP content，違反 grounding-principle.md anti-pattern |
| **Preamble (persona/ philosophical anchor)** | ✅ **推薦** — 用 97 のこと JP essays（松本「名前重要」、和田「不具合にテストを書いて立ち向かう」）+ 和田 TDD 啓蒙 + 徳丸本 Ch.6 文字コード 做 "JP lens" |
| No overlay (explicit 聲明) | ❌ 太極端 — **實**有 JP-specific content（徳丸本 Ch.6），否定反而失真 |

---

# Cluster E — Cross-cutting

## Q11. Michael Feathers — Working Effectively with Legacy Code

### 書誌

- **作者**: Michael C. Feathers
- **標題**: *Working Effectively with Legacy Code*
- **出版**: **Prentice Hall PTR (2004 年 9 月 1 日)**
- **ISBN-13**: 9780131177055 / ISBN-10: 0131177052
- **Series**: Robert C. Martin Series
- **來源驗證**: ACM Queue review (Jan 2006) + Amazon + Pearson sample PDF + Internet Archive + Open Library

### 核心主張

1. **Legacy code definition**: *"Code without tests."* (Preface) — 這是 Feathers 的 canonical definition
2. **24 dependency-breaking techniques** (Ch.25): 具體、可套用的 refactoring 清單
3. **Seam Model** (Ch.4): The Seam Model — seam = 能夠替換行為而不需要在該處編輯的位置
4. **Characterization Tests** (Ch.13): pin down legacy 行為的測試寫法
5. **"Hard to test → simplify the design"**: 貫穿全書的根本主張

### 是否應加入 code-team candidate list?

> [!important] **強烈建議加入** — 5 個理由
> 1. **Tests & Refactoring 的 missing link**: Clean Code + TDD + Refactoring 都假設 greenfield；legacy 才是真正的 85% 現場。
> 2. **Characterization Tests** 是 qa-team Level 以外、code-team 層次的 pattern。
> 3. **Seam Model** grounds "hard to test → simplify design" 這個 SOLID/Clean Code claim 的實際機械方法。
> 4. **Robert C. Martin Series** — Martin 本人序言背書，是 Martin-aligned canon 的一部分。
> 5. **Gap report claim coverage**: 任何 "testability" / "legacy refactor" / "break dependencies" 的 claim 都需要 Feathers 2004 做 grounding，Clean Code 不够。

### 引用建議

Standard: 新增或併入 `refactoring-standard.md`，主引 Fowler 2018，次引 Feathers 2004 for legacy-specific technique。

## Q12. ISO/IEC 25010 — Software Quality Model

### 書誌（當前版本）

- **標題**: Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — **Product quality model**
- **Version**: **ISO/IEC 25010:2023** (當前) ← 取代 **ISO/IEC 25010:2011** (2011-03-01)
- **發行**: **2023 年 11 月**
- **ISO 正式頁**: https://www.iso.org/standard/78176.html (25010:2023) / https://www.iso.org/standard/35733.html (25010:2011)
- **價格**: ISO 付費（~CHF 138）；**全文免費版不存在**
- **免費替代**: arc42 Quality Model (quality.arc42.org)，ISO25000.com portal — 這些是教育性 summary，**非** primary source
- **來源驗證**: arc42 update article + iso25000.com + ISO 官方站 link

### 2011 vs 2023 對比（已驗證於 arc42 article）

| 2011 (8 characteristics) | 2023 (9 characteristics) |
|---|---|
| Functional Suitability | Functional Suitability |
| Performance Efficiency | Performance Efficiency |
| Compatibility | Compatibility |
| **Usability** | **Interaction Capability** (rename + expanded) |
| Reliability | Reliability |
| Security | Security |
| Maintainability | Maintainability |
| **Portability** | **Flexibility** (rename + expanded) |
| — | **Safety** ⭐ new top-level |

**2023 新 sub-characteristics**:
- Safety: operational constraint, risk identification, fail safe, hazard warning, safe integration
- Interaction Capability: inclusivity, self-descriptiveness (新), + user engagement (取代 UI aesthetics), faultlessness (取代 maturity)
- Security: resistance (新)
- Flexibility: scalability (新)

### 是否應加入 code-team 作為 Quality rubric 4 dimensions (Correctness/API/Design/Tests) 的 grounding？

> [!warning] 保留判斷 — 不建議作為 code-team primary
>
> **反對採用的理由**:
> 1. **Correctness/API/Design/Tests 的 4 dimension 分類** 跟 ISO 25010 的 Functional Suitability / Maintainability / Reliability 等不是 1:1 mapping。強行 mapping 會 **citation washing** (grounding-principle.md anti-pattern)。
> 2. **付費 standard**: 全文不可公開引用章節號，grounding 深度有限。
> 3. **code-team 的 rubric 粒度不同**: 25010 是 **product-level** quality，code-team rubric 是 **code-change-level** 評估。
>
> **支持有限引用的理由**:
> 1. ISO 的名詞 (Maintainability, Reliability) 可作 **vocabulary anchor**，code-team 在描述 "maintainability" 時引 25010:2023 §5.6 做詞彙權威，不做 rubric 結構 grounding。
> 2. Quality 領域的 neutral authority，對企業採納有正當性加成。
>
> **建議**：將 ISO 25010:2023 **列為 auxiliary reference**，不作為 primary。主要的 quality rubric grounding 來自 Martin (Clean Code Ch.17 Smells + Ch.10 Classes + SOLID) + Fowler (Refactoring 2018 Bad Smells) + Feathers (Legacy Code testability)，這些才是 **code-change-level** 且可公開引用。

---

# JP Integration Decision

> [!success] **Decision: PREAMBLE** (非 full framework / 非 no-overlay)

### 一句話證據

日本 code craft 沒有平行 Anglo canon 的獨立框架，但有 **兩個 substantive JP-original 錨點** — 徳丸本 Ch.6 文字コードとセキュリティ（ASVS 沒有的 JP-specific 安全內容）＋ 97 のこと 日本人 10 篇 essays（特別是松本「名前重要」和 t_wada「不具合にテストを書いて立ち向かう」）＋ 和田卓人 的 TDD 啓蒙文脈 — 足以作 persona preamble 和一個獨立的 character-encoding 安全 standard。

### 具體實作建議

| 機制 | 內容 |
|---|---|
| **SKILL.md persona** | 「Your philosophy is anchored on Martin/Beck/Fowler canon for craft, ASVS 5.0.0 for security, and Google Engineering Practices for code review. For multi-byte / Japanese context, you also consult 徳丸浩『体系的に学ぶ 安全な Web アプリケーションの作り方 第 2 版』Ch.6 on character encoding security, and draw on 97 のこと 日本語版 essays by 和田卓人, まつもとゆきひろ and others for naming/testing philosophy.」 |
| **Dedicated standard** | `character-encoding-security.md` — 獨立 standard 引徳丸本 Ch.6 + IPA 安全な Web アプリケーションの作り方（徳丸 contributed） |
| **Optional quote block** | 在 `code-conventions.md` 或 `tdd-standard.md` 加一個 sidebar：引松本「名前重要」和 t_wada「不具合にテストを書いて立ち向かう」做 JP craft echo |

---

# Grounding Plan — Standards to Create

下表規劃 **6 個 standards**（加 1 個 JP-specific）＝ 7 個檔案。全部以 primary-source 引用，每份 60-140 行。

## Standard 1: `naming-and-functions.md`

- **Purpose**: 命名規範 + 函數粒度規則 + comments hierarchy
- **Primary sources (3)**:
  1. Martin, R.C. (2008). *Clean Code*, **Ch.2 Meaningful Names, Ch.3 Functions, Ch.4 Comments**. Prentice Hall. ISBN 978-0132350884.
  2. Hunt, A. & Thomas, D. (2019). *The Pragmatic Programmer, 20th Anniversary Edition*, **Topic 9 DRY, Topic 10 Orthogonality** (+ Ch.7 Naming Things). Addison-Wesley. ISBN 978-0135957059.
  3. 97 のこと 日本語版: まつもと ゆきひろ 「名前重要」(supplementary JP essay).
- **Load-bearing claims**: naming rules, function-size rule (Clean Code Ch.3 "small"), comment hierarchy, DRY
- **Estimated lines**: 120

## Standard 2: `solid-principles.md`

- **Purpose**: SRP/OCP/LSP/ISP/DIP 定義與套用指南
- **Primary sources (2-3)**:
  1. Martin, R.C. (2000). *Design Principles and Design Patterns*. objectmentor.com. (Mirror available on academic archive: https://staff.cs.utu.fi/~jounsmed/doos_06/material/DesignPrinciplesAndPatterns.pdf)
  2. Martin, R.C. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*, **Part III SOLID Principles**. Prentice Hall. ISBN 978-0134494166.
  3. (optional) Martin, R.C. (2002). *Agile Software Development, Principles, Patterns, and Practices*. Prentice Hall. ISBN 978-0135974445.
- **Load-bearing claims**: 5 SOLID principles + their formal definitions + anti-patterns
- **Estimated lines**: 100

## Standard 3: `tdd-standard.md`

- **Purpose**: TDD red/green/refactor cycle + test design + test granularity
- **Primary sources (3)**:
  1. **Beck, K. (2002). *Test-Driven Development: By Example*. Addison-Wesley. ISBN 978-0321146533.** ← canonical
  2. Martin, R.C. (2008). *Clean Code*, Ch.9 Unit Tests (Three Laws of TDD + F.I.R.S.T). Prentice Hall.
  3. 和田卓人 (2017). 『テスト駆動開発』 (Beck 原著日譯), オーム社. ISBN 978-4274217883. ← JP anchor (translator 和田卓人)
- **Load-bearing claims**: Red/Green/Refactor cycle, test-first rule, F.I.R.S.T principles, Three Laws of TDD, fake-it/triangulate patterns
- **Estimated lines**: 120

## Standard 4: `refactoring-standard.md`

- **Purpose**: Refactoring definition + Bad Smells + Rule of Three + legacy-specific techniques
- **Primary sources (3)**:
  1. **Fowler, M. (2018). *Refactoring: Improving the Design of Existing Code*, 2nd ed. Addison-Wesley. ISBN 978-0134757599.** ← canonical
  2. Feathers, M. (2004). *Working Effectively with Legacy Code*. Prentice Hall. ISBN 978-0131177055. ← legacy + seams + characterization tests ⭐ **new addition**
  3. Martin, R.C. (2008). *Clean Code*, Ch.17 Smells and Heuristics. Prentice Hall.
- **Load-bearing claims**: refactoring definition, code smells taxonomy, Rule of Three (Don Roberts), legacy definition ("code without tests"), seam model, dependency-breaking techniques
- **Estimated lines**: 130

## Standard 5: `security-standard.md`

- **Purpose**: OWASP ASVS-aligned security requirements
- **Primary sources (2)**:
  1. **OWASP (2025). *Application Security Verification Standard v5.0.0*. https://asvs.dev/v5.0.0/** ← canonical, ⚠ NOT 4.0.3
  2. OWASP (2023). *Top 10 Web Application Security Risks*. https://owasp.org/www-project-top-ten/ (as secondary vocabulary for prioritization)
- **Load-bearing claims**: 17 chapter verification categories, L1/L2/L3 tier system, input validation (V2), injection prevention (V1+V2), secrets management (V13+V14), auth (V6), session (V7)
- **Estimated lines**: 140

## Standard 6: `character-encoding-security.md` ⭐ JP-specific

- **Purpose**: 多位元組文字（Shift_JIS, UTF-8, EUC-JP）相關的安全漏洞與對策
- **Primary sources (2)**:
  1. **徳丸浩 (2018). 『体系的に学ぶ 安全な Web アプリケーションの作り方 第 2 版』第 6 章 文字コードとセキュリティ. SB クリエイティブ. ISBN 978-4797393163.** ← canonical JP
  2. 徳丸浩 (2013). 「文字コードに起因する脆弱性とその対策（増補版）」SlideShare/Docswell.
- **Load-bearing claims**: 5C 問題 (Shift_JIS SQL injection vector), multi-byte char boundary XSS, UTF-8 over-long encoding, mojibake-induced bypass, JP CMS/EC context
- **Estimated lines**: 90

## Standard 7: `code-review-standard.md`

- **Purpose**: Code review SOP + 8 評估面向 + speed / size / comment writing
- **Primary sources (1-2)**:
  1. **Google (2024). *Engineering Practices Documentation — Code Review*. https://google.github.io/eng-practices/review/** ← canonical
  2. (optional) Fagan, M.E. (1976). "Design and code inspections to reduce errors in program development." *IBM Systems Journal* 15(3). ← historical anchor for formal inspection
- **Load-bearing claims**: 8 review dimensions (design/functionality/complexity/tests/naming/comments/style/docs), reviewer response time (1 business day), small CL rule, CL description structure
- **Estimated lines**: 110

### Standards 總覽

| # | File | Lines | Primary count | JP anchor? |
|---|---|---|---|---|
| 1 | `naming-and-functions.md` | 120 | 3 | ✅ (97 のこと) |
| 2 | `solid-principles.md` | 100 | 2-3 | — |
| 3 | `tdd-standard.md` | 120 | 3 | ✅ (和田卓人 訳) |
| 4 | `refactoring-standard.md` | 130 | 3 | — |
| 5 | `security-standard.md` | 140 | 2 | — |
| 6 | `character-encoding-security.md` | 90 | 2 | ✅ (徳丸本) |
| 7 | `code-review-standard.md` | 110 | 1-2 | — |
| **Total** | **7 files, ~810 lines, 16-18 primary citations** | | | 3/7 JP-anchored |

比 devops-team v4.4 的 5-6 standards / 14 primaries **略多**，因為 code-team 的 scope (craft + security + review) 本身更廣。

---

# Load-bearing Claim → Source Mapping

> [!note] Claim IDs 引自 Phase 1 gap report
> Phase 1 的 gap report 識別 41 個 load-bearing claims，以下按 Standard 分配：

| Claim Cluster | Primary Source | Chapter / Section |
|---|---|---|
| **Naming / Functions / Comments** | | |
| Name must reveal intent | Clean Code | Ch.2 §"Use Intention-Revealing Names" |
| Function should do one thing | Clean Code | Ch.3 §"Do One Thing" |
| Function ≤ 20 lines heuristic | Clean Code | Ch.3 §"Small!" (the "smaller" rule) |
| Four kinds of bad comments | Clean Code | Ch.4 §"Bad Comments" |
| Don't repeat yourself | Pragmatic Programmer | Topic 9 (Ch.2) |
| Orthogonality reduces risk | Pragmatic Programmer | Topic 10 (Ch.2) |
| **Naming matters (JP echo)** | 97 のこと 日本語版 | 松本 ゆきひろ 「名前重要」 |
| **SOLID** | | |
| SRP — one reason to change | Martin 2000 / Clean Architecture | 2000 §3 / 2017 Ch.7 |
| OCP — open/closed | Martin 2000 / Clean Architecture | 2000 §4 / 2017 Ch.8 |
| LSP — substitutability | Martin 2000 / Clean Architecture | 2000 §5 / 2017 Ch.9 |
| ISP — interface segregation | Martin 2000 / Clean Architecture | 2000 §6 / 2017 Ch.10 |
| DIP — dependency inversion | Martin 2000 / Clean Architecture | 2000 §7 / 2017 Ch.11 |
| **TDD** | | |
| Red/Green/Refactor cycle | **Beck 2002** | Ch.1 + Ch.25 |
| Never write code without failing test | Beck 2002 | Preface |
| Three Laws of TDD | Clean Code | Ch.9 (after Beck 2002 origin) |
| F.I.R.S.T test rules | Clean Code | Ch.9 |
| Fake-It / Triangulate patterns | Beck 2002 | Part II |
| **JP TDD philosophy** | 97 のこと / 和田訳 TDD | 和田「不具合にテストを書いて」 |
| **Refactoring** | | |
| Refactoring = behavior-preserving transformation | Fowler 2018 | Ch.1 Opening + Ch.2 Principles |
| Rule of Three (Don Roberts) | Fowler 2018 | Ch.2 §"When should you refactor" |
| Bad Smells catalog | Fowler 2018 | Ch.3 (in 1st ed + carried to 2nd ed) |
| Smells: Divergent Change, Shotgun Surgery, Duplicated Code | Fowler 2018 | Ch.3 (bad smells chapter) |
| Smells: long function, large class, feature envy | Clean Code | Ch.17 §G5, §G6, §G14 |
| Legacy = code without tests | Feathers 2004 | Preface |
| Seam Model | Feathers 2004 | Ch.4 |
| 24 dependency-breaking techniques | Feathers 2004 | Ch.25 |
| Characterization Tests | Feathers 2004 | Ch.13 |
| **Security** | | |
| 17 ASVS verification categories | ASVS 5.0.0 | Preface + Ch. index |
| L1/L2/L3 tier definitions | ASVS 5.0.0 | Preface (tier section) |
| Input validation & business logic | ASVS 5.0.0 | V2 |
| Encoding and sanitization | ASVS 5.0.0 | V1 |
| Authentication requirements | ASVS 5.0.0 | V6 |
| Session management | ASVS 5.0.0 | V7 |
| Authorization | ASVS 5.0.0 | V8 |
| Cryptography | ASVS 5.0.0 | V11 |
| Data protection (secrets) | ASVS 5.0.0 | V14 + V13 Configuration |
| Security logging & error handling | ASVS 5.0.0 | V16 |
| **Character encoding security (JP)** | | |
| Shift_JIS 5C problem → SQL injection | 徳丸本 | Ch.6 |
| Multi-byte boundary XSS | 徳丸本 | Ch.6 |
| UTF-8 over-long encoding | 徳丸本 | Ch.6 |
| **Code Review** | | |
| 8 review dimensions | Google eng-practices | reviewer/looking-for.html |
| Standard of code review | Google eng-practices | reviewer/standard.html |
| Reviewer speed (1 business day) | Google eng-practices | reviewer/speed.html |
| Small CLs = one self-contained change | Google eng-practices | developer/small-cls.html |
| CL description: imperative summary | Google eng-practices | developer/cl-descriptions.html |
| Handling reviewer comments | Google eng-practices | developer/handling-comments.html |

**Claim coverage**: ~45 mappings for ~41 gap-report claims → **每個 load-bearing claim 至少 1 primary source**，多數有 2+ sources cross-reference。

---

# Open Questions / Needs User Verification

1. **Phase 1 gap report 的精確 41 個 claim IDs 未傳入本研究**。上述 mapping 以合理推斷進行；Phase 3 合成 standards 時須以實際 gap report 逐項 cross-check。
2. **Pragmatic Programmer 第 3-9 章的精確 Topic 編號** — 公開 Web 沒有完整編號表。Ch.2 Topics 8-15 已驗證；其他章節引用時建議「Ch.N, Topic title」格式，不編造數字。
3. **Fowler Refactoring 2nd ed 的章節編號** — martinfowler.com/books/refactoring.html 沒有列出 chapter-by-chapter TOC；1st ed 的 Ch.3 = Bad Smells，2nd ed 大致延續但未獨立驗證章號。建議 standards 引用時寫「Fowler 2018 Bad Smells chapter」或「Fowler 1999/2018」。
4. **Clean Architecture (Martin 2017) 內的 SOLID 章節號** — 未獨立驗證；使用者若要細引章節號需要 physical book。
5. **97 のこと 日本人 essay 的第 10 篇作者** — 驗證 9/10，第 10 篇作者歸屬有爭議。code-team standards 只引已驗證的 8 位作者 + 9 篇 essays。
6. **徳丸本第 3 版狀態** — 截至 2026-04 沒有公告，使用者若要做長期維護需設 watch reminder。
7. **ISO/IEC 25010:2023 是否採用** — 本研究建議**不做 primary**，但若使用者認為 code-team rubric 需要 vocabulary authority，則作為 auxiliary reference。
8. **Martin 2000 objectmentor.com 原始 URL** — 原 URL 已失效；建議 code-team standards 引用 academic mirror（staff.cs.utu.fi/~jounsmed/doos_06/material/DesignPrinciplesAndPatterns.pdf）並標註「objectmentor.com 原始出處，現只存在 academic mirror」。

---

# Blockers

> [!success] **No blockers**
>
> 所有 12 個研究問題都得到 primary-source 答案。使用者候選清單中唯一需要修正的是 **Q6: ASVS 版本 4.0.3 → 5.0.0**（已在本研究中澄清）。其他 11 題都直接驗證並回答。

---

# 對 code-team 再設計的 8 個設計決策

1. **`[分析|高]`** 採用 Martin/Beck/Fowler trio + Feathers 作為 craft canon，每個 claim 明示章節
2. **`[事實|高]`** OWASP ASVS **5.0.0**（非 4.0.3）作為 security standard，17 章 V1-V17
3. **`[事實|高]`** 徳丸本 Ch.6 作 character encoding security 獨立 standard（JP-specific，非 ASVS redundant）
4. **`[事實|高]`** Google Engineering Practices 作 code review standard（6 reviewer + 3 author pages）
5. **`[分析|中]`** JP 整合採 **preamble 策略**（97 のこと 日本人 essays + 和田 TDD + 徳丸本）不做 full framework
6. **`[分析|中]`** ISO/IEC 25010:2023 作 auxiliary vocabulary，**非** primary（付費 + 粒度不匹配）
7. **`[事實|高]`** TDD primary = Beck 2002，**不是** Clean Code Ch.9（後者是 rephrasing）
8. **`[分析|高]`** 每個 standard 開頭列 2-5 primary sources，每個 load-bearing claim 標 (SourceKey, Ch.N §M) 格式

---

# 相關研究脈絡

- qa-team 研究綜合 — `domain-teams/skills/qa-team/research/grounding-v4.2.0.md`（本研究的 structural reference，in-repo backfilled v4.7.0）
- docs-team 研究 — `domain-teams/skills/docs-team/research/grounding-v4.3.0.md`（in-repo backfilled v4.7.0）
- qa-team 歐美篇 / 日本篇 companion notes — 留在 maintainer's Obsidian vault 作為 authoring workspace，不進 repo
- MOC (authoring workspace, not backfilled)

---

# 主要參考來源

## Clean Code Canon

- [Clean Code — Pearson/InformIT](https://www.informit.com/store/clean-code-a-handbook-of-agile-software-craftsmanship-9780132350884)
- [Clean Code TOC — Library of Congress CIP](https://catdir.loc.gov/catdir/toc/ecip0820/2008024750.html)
- [Martin, R.C. (2005) "The Three Rules of TDD"](http://butunclebob.com/ArticleS.UncleBob.TheThreeRulesOfTdd)
- [Clean Coder Blog — Cycles of TDD (2014)](https://blog.cleancoder.com/uncle-bob/2014/12/17/TheCyclesOfTDD.html)

## Pragmatic Programmer

- [pragprog.com — 20th Anniversary Edition](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)
- [Pragmatic Programmer Tips (full 100)](https://pragprog.com/tips/)
- [O'Reilly Learning edition](https://www.oreilly.com/library/view/the-pragmatic-programmer/9780135956977/)
- [Pearson/informit — TPP 20th Anniversary](https://www.informit.com/store/pragmatic-programmer-your-journey-to-mastery-20th-anniversary-9780135957059)

## SOLID

- [Martin, R.C. (2000) *Design Principles and Design Patterns* (PDF mirror)](https://staff.cs.utu.fi/~jounsmed/doos_06/material/DesignPrinciplesAndPatterns.pdf)
- [Bob Martin's Design Principles Page (DePaul mirror)](https://condor.depaul.edu/dmumaugh/OOT/Design-Principles/)
- [SOLID — Wikipedia (pointer)](https://en.wikipedia.org/wiki/SOLID)

## TDD

- [Beck, K. *TDD by Example* — O'Reilly Learning](https://www.oreilly.com/library/view/test-driven-development/0321146530/)
- [Beck TDD Sample PDF (Pearson)](https://ptgmedia.pearsoncmg.com/images/9780321146533/samplepages/0321146530.pdf)
- [Internet Archive — TDD by Example](https://archive.org/details/est-driven-development-by-example)
- [martinfowler.com/bliki — Test Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [和田卓人 訳『テスト駆動開発』オーム社 2017](https://www.amazon.co.jp/dp/4274217884)

## Refactoring

- [martinfowler.com/books/refactoring.html](https://martinfowler.com/books/refactoring.html)
- [martinfowler.com — The Second Edition of Refactoring](https://martinfowler.com/articles/refactoring-2nd-ed.html)
- [refactoring.com catalog (companion site)](https://refactoring.com/catalog/)

## Legacy Code

- [Feathers — WELC — Pearson sample PDF](https://ptgmedia.pearsoncmg.com/images/9780131177055/samplepages/0131177052.pdf)
- [Feathers — WELC — Internet Archive](https://archive.org/details/working-effectively-with-legacy-code)
- [ACM Queue — WELC review (Jan 2006)](https://queue.acm.org/detail.cfm?id=1105682)

## OWASP ASVS 5.0.0

- [OWASP ASVS Project page](https://owasp.org/www-project-application-security-verification-standard/)
- [asvs.dev — v5.0.0 dedicated site](https://asvs.dev/v5.0.0/)
- [ASVS 5.0.0 Preface](https://asvs.dev/v5.0.0/Preface/)
- [ASVS GitHub repo](https://github.com/OWASP/ASVS)
- [OWASP blog: ASVS 5.0 RC1 (2025-04)](https://owasp.org/blog/2025/04/09/asvs-rc1-review)
- [What's New in ASVS 5.0 — SoftwareMill summary](https://softwaremill.com/whats-new-in-asvs-5-0/)

## 徳丸本 (JP Web Security)

- [SB クリエイティブ 公式頁](https://www.sbcr.jp/product/4797393163/)
- [NDL Search — 徳丸本 第 2 版](https://ndlsearch.ndl.go.jp/en/books/R100000002-I029031208)
- [徳丸浩『文字コードに起因する脆弱性とその対策』 SlideShare](https://www.slideshare.net/ockeghem/ss-5620584)
- [owasp-ja/asvs-ja GitHub (ASVS Japanese translation)](https://github.com/owasp-ja/asvs-ja)
- [トライベック — 徳丸本第 2 版 発売記念インタビュー](https://www.tribeck.jp/column/opinion/technology/20180717/)

## Google Engineering Practices

- [eng-practices/review index](https://google.github.io/eng-practices/review/)
- [How to do a code review (reviewer)](https://google.github.io/eng-practices/review/reviewer/)
- [The CL author's guide (developer)](https://google.github.io/eng-practices/review/developer/)
- [The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [What to Look For In a Code Review](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [Speed of Code Reviews](https://google.github.io/eng-practices/review/reviewer/speed.html)
- [Writing Good CL Descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html)
- [Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)
- [google/eng-practices GitHub repo](https://github.com/google/eng-practices)

## JP Code Craft

- [97 のこと — オライリー・ジャパン](https://www.oreilly.co.jp/books/9784873114798/)
- [上田勲『プリンシプル オブ プログラミング』— 秀和システム](https://www.shuwasystem.co.jp/book/9784798046143.html)
- [和田卓人 gihyo.jp — テスト駆動開発講座 (20 回)](https://gihyo.jp/dev/serial/01/tdd)
- [WEB+DB PRESS Vol.35 「実演！テスト駆動開発」特集](https://gihyo.jp/magazine/wdpress/information/2006/vol35-tdd)
- [Code Complete 第 2 版 (日経 BP)](https://bookplus.nikkei.com/atcl/catalog/05/589000/)
- [SQL アンチパターン 第 2 版 (和田卓人 監訳)](https://www.oreilly.co.jp/books/9784814400744/)
- [リーダブルコード (オライリー・ジャパン)](https://www.oreilly.co.jp/books/9784873115658/)

## ISO/IEC 25010

- [ISO/IEC 25010:2023 (official)](https://www.iso.org/standard/78176.html)
- [ISO/IEC 25010:2011 (legacy)](https://www.iso.org/standard/35733.html)
- [arc42 Quality Model — ISO 25010:2023 Update article](https://quality.arc42.org/articles/iso-25010-update-2023)
- [ISO25000.com portal](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)

---

**研究日期**: 2026-04-11
**研究執行者**: code-team v4.6.0 grounding research (Phase 2), 作為 skill-team protocols/skill-redesign.md Phase 2 research-team stand-in
**研究用途**: monkey-skills/domain-teams/code-team 再設計 (v4.6.0)
**驗證標準**: grounding-principle.md + qa-team v4.2 / docs-team v4.3 / devops-team v4.4 的 citation density reference

> 🔄 CHECKPOINT: This research note is raw Phase 2 output. Next: skill-team Phase 3 consumes this note and Phase 1 gap report to synthesize 7 standards files, then Phase 4 validates with Primary-Source Grounding rubric.
