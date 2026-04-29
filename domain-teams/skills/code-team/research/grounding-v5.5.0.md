---
title: code-team mindset standards 研究 — Hickey / Brooks / Moseley & Marks / Willison
date: 2026-04-29
team: code-team
refactor_version: v5.5.0
tags:
  - research
  - domain-teams
  - code-team
  - grounding
  - mindset
  - hickey
  - simple-made-easy
  - data-oriented-design
  - pagni
  - yagni
aliases:
  - code-team mindset 研究
  - code-team mindset standards grounding
  - design-philosophy mindsets
---

# code-team Mindset Standards 研究

> **背景** (2026-04-29, v5.4.1): 為 code-team 增補 4 個 philosophical
> mindset standards — `mindset-data-over-abstractions.md` /
> `mindset-design-is-taking-apart.md` /
> `mindset-expensive-to-add-later.md` /
> `mindset-simplicity-vs-easy.md`。動機是 code-team 既有 7 個 standards
> 全部走 *mechanical* / *prescriptive* 路線（Clean Code naming rules /
> Pragmatic 原則 / SOLID / TDD / Refactoring / OWASP / 徳丸本
> character-encoding），缺乏 *design-time philosophical anchor*。本研究
> 為 4 個 mindsets 各自建立一手來源溯源，並紀錄 curation lineage（外部
> MIT skill `softaworks/agent-toolkit/skills/reducing-entropy`，原作者
> @joshuadavidthomas）以維持 skill-team `grounding-principle.md` 的
> primary-source-anchored 規範。

## TL;DR

| Mindset | Title | Primary Source(s) | Status |
|---------|-------|-------------------|--------|
| `mindset-data-over-abstractions.md` | Data-Over-Abstractions | Perlis 1982 *Epigrams* #9; Hickey 2012 *Value of Values*; Fabian 2018 *DOD*; Acton 2014 CppCon | `[事實\|高]` |
| `mindset-design-is-taking-apart.md` | Design-Is-Taking-Apart | Hickey 2011 *Simple Made Easy*; Moseley & Marks 2006 *Out of the Tar Pit*; Ousterhout 2018 *A Philosophy of Software Design 2nd ed*; Brooks 1986 *No Silver Bullet* | `[事實\|高]` |
| `mindset-expensive-to-add-later.md` | Expensive-To-Add-Later (PAGNI) | Willison 2021 PAGNI post; Plant 2021 YAGNI Exceptions; Kaplan-Moss 2021 AppSec PAGNIs; Fowler bliki Yagni | `[事實\|高]` |
| `mindset-simplicity-vs-easy.md` | Simplicity-vs-Easy | Hickey 2011 *Simple Made Easy*; Hickey 2012 *Value of Values*; Moseley & Marks 2006 *Out of the Tar Pit* | `[事實\|高]` |

## Curation Lineage

4 個 mindsets 的 *選題* 來自外部 MIT skill：

```
@joshuadavidthomas/agent-skills (MIT)
  → softaworks/agent-toolkit/skills/reducing-entropy (MIT, fork)
    → monkey-skills/domain-teams/code-team mindset standards (this PR)
```

選題 inheritance 處理：
- code-team 採納 4 篇 mindset 的 *選題範圍* 與 *philosophical position*
- 但**重寫所有內文**並**直接引用一手來源**（Hickey 演講、Perlis epigram、
  Moseley & Marks 論文、Ousterhout 書、Willison / Plant / Kaplan-Moss 部
  落格、Fowler bliki），而非繼承 reducing-entropy skill 的解說文
- code-team standards 既有慣例：無 YAML frontmatter、`# Title` /
  `## Primary Sources` / 章節 / `## Anti-Patterns` — 4 個 mindsets 全部
  鏡像此格式
- 攻擊性差異：reducing-entropy 是 *manual-only deletion bias*；code-team
  mindsets 是 *design-time philosophical anchor*，跟既有 SOLID /
  Pragmatic 並列，無 verdict 角色

## Citation 驗證紀錄

### Mindset 1: Data-Over-Abstractions

**關鍵 claim**：「100 functions on 1 data structure > 10 functions on
10 structures」常見歸給 Rich Hickey。實際出處：

- **Alan Perlis, "Epigrams on Programming"** (1982), *ACM SIGPLAN
  Notices* Vol.17 No.9, September 1982 — Epigram #9: *"It is better
  to have 100 functions operate on one data structure than 10
  functions on 10 data structures."*
- 文獻可在 ACM Digital Library 或多個鏡像上找到（e.g. Yale 大學鏡像）
- Hickey 在 *Value of Values* 引用過此 epigram，導致常被誤歸給他
- mindset standard 已正確標註 Perlis 為原始出處，Hickey 為 modern
  popularizer

**Hickey *Value of Values***：JaxConf 2012 / Strange Loop 變體；
InfoQ URL 穩定。

**Fabian *Data-Oriented Design***：self-published 2018；專屬網域
`dataorienteddesign.com/dodbook/` 提供完整內文線上版。

**Acton CppCon 2014**：YouTube 與 CppCon GitHub 雙渠道存檔。

### Mindset 2: Design-Is-Taking-Apart

**關鍵 quote**：「Design is about taking things apart.」— 出處驗證：

- Hickey, *Simple Made Easy* (Strange Loop 2011) — 原講中段討論
  *complect* / *compose* 區分時提出。具體 timestamp 約 33–35 分鐘區
  間（InfoQ 影片）
- Strange Loop 講義內容也有此句的轉錄；reducing-entropy skill 與
  code-team mindset 都正確 attribute

**Out of the Tar Pit** (Moseley & Marks 2006)：學術論文，作者個人
網域 (curtclifton.net 鏡像) 提供 PDF 下載；經常被當作 *essential vs
accidental complexity* 論述的學術錨點，回扣到 Brooks 1986 的原始
distinction。

**Ousterhout *A Philosophy of Software Design***：2018 1st ed
ISBN 978-1732102200；2021 2nd ed ISBN 978-1732102217。「deep modules
vs shallow modules」是其原創 framing。code-team mindset 引用 2nd ed。

**Brooks *No Silver Bullet***：UNC 大學 tech reports 提供 PDF；原
1986 IFIP 會議論文，後在 *Computer* 雜誌 (1987) 重發；
*The Mythical Man-Month* 20 週年紀念版 (1995) 也收錄。

### Mindset 3: Expensive-To-Add-Later (PAGNI)

**關鍵 claim**：PAGNI = "Probably Are Gonna Need It"，由 Simon
Willison 2021-07-01 在個人 blog 命名。

- **Willison post**: simonwillison.net/2021/Jul/1/pagnis/ (2021)
- **Plant 後續 essay**: lukeplant.me.uk/blog/posts/yagni-exceptions/
  (2021，跟 Willison 對話延伸)
- **Kaplan-Moss security PAGNI**: jacobian.org/2021/jul/8/
  appsec-pagnis/ (2021，把 PAGNI 應用到 application security)

三篇 blog 在 2021 年 7 月形成短暫對話串，PAGNI 作為新詞流通。Fowler
bliki 早就承認 YAGNI 不禁止 *thinking ahead*，PAGNI 是把那個 crack
明確命名。

**為何不歸類為 self-invented**：3 篇 blog 都是 industry 認可的
practitioner 寫的（Willison = Django co-creator, Datasette 作者；
Plant = Django core team；Kaplan-Moss = Django co-creator, 前
Heroku/Latacora 安全專家），且彼此引用，形成 small-but-grounded
canonical source set。

### Mindset 4: Simplicity-Vs-Easy

完全來自 Hickey *Simple Made Easy* (2011) 的核心論證。Etymology
讀法（*sim-plex* = "one fold"）也是 Hickey 在演講前 5 分鐘的開場。
*Out of the Tar Pit* 提供 essential-vs-accidental 的論文層 backing。

## Skill-Team grounding-principle.md 合規性

逐條檢查：

| 規範 | 狀態 |
|------|------|
| Primary source 必為 ISBN 書、學術論文、author bliki / 演講 official 錄影 | ✅ 4 個 mindsets 全合規 |
| Citation 不可 launder（不偽造章節號、Topic 編號）| ✅ 章節 / Topic 號全部來自 source 本身或標明「無獨立驗證」 |
| 二手摘要 / 部落格不可作 primary | ⚠️ Mindset 3 PAGNI 三篇 blog 為 primary — 因為 PAGNI 詞本身在 blog 命名，不在書/論文 |
| 引用必為網路可達 | ✅ 全部 URL 經人工確認 |
| 反 self-invention | ✅ 4 篇皆有 ≥2 個 independent primary sources |

特例 (Mindset 3 PAGNI): 此屬於 *practitioner-coined neologism*，與
*industry 文獻 grounded* 的標準不衝突 — 跟 Hickey「complect」也是
practitioner-coined 同類。書本不收錄是因為 PAGNI 在 2021 才命名。

## 整合方式

mindsets 在 code-team 中的角色：
- **不是 MUST gate** — 不上 quality-gate.md / arch-gate.md / security
  checklist
- **不在 worker 預設 standards 列表** — 避免 token 預算膨脹
- **作為 brainstorming protocol 的 reference** — `protocols/code-brainstorming.md`
  進行 design-time 討論時可主動載入
- **作為 refactoring protocol 的 reference** — `protocols/refactoring.md`
  進行重構決策時可主動載入
- **跨 plugin 開放** — `dev-workflow:complexity-critique` 透過跨 plugin
  delegation 引用 4 個 mindsets

## Cross-Plugin Delegation Pattern

第二個 cross-plugin delegation precedent（第一例：investing-toolkit →
investing-team）：

```
dev-workflow:complexity-critique skill
  → 讀 4 個 code-team mindsets via delegation
  → code-team mindsets 為 SoT，dev-workflow 不複製內文
```

合規規範（CLAUDE.md §Cross-Plugin Delegation Contract）：
- ✅ Pass paths + structured seed context
- ✅ Single source of truth (mindsets 只活在 code-team)
- ✅ Cross-plugin path 用 `domain-teams:code-team/standards/...`
- ✅ Graceful degradation: complexity-critique 三問 gate 在 code-team 未
  安裝時仍可運作（mindsets 是 advisory deepening）

## Modifications vs Upstream

`softaworks/agent-toolkit/skills/reducing-entropy` (MIT) 的取捨：

| 項目 | Upstream | code-team mindset 採納 |
|------|----------|----------------------|
| 4 個 mindset 選題範圍 | ✅ data-oriented / composition / PAGNI / simple-vs-easy | ✅ 採納 |
| Mindset YAML frontmatter | description 一行 | ❌ 改為 code-team standards 慣例（無 frontmatter，`# Title`） |
| Mindset 內文 | reducing-entropy 自寫摘要 | ❌ 重寫，改用 primary source 直接引用 + ISBN/URL |
| 三問 gate 機制 | ✅ skill 主體 | 不採納（不在 mindsets layer，而在 dev-workflow:complexity-critique） |
| LOC count 機制 | ✅ skill 主體 | 不採納（同上） |
| Manual-only 啟動 | ✅ description 中明示 | 不採納（mindsets 是 reference，無 trigger） |
| `references/` 目錄結構 | flat under skill | 不採納（CLAUDE.md 規定 one level deep） |

## 後續工作

- ☐ Commit 2: code-team SKILL.md `## Resource Manifest` 加入 4 個
  mindsets（worker / evaluator launch templates 不自動載入；mindsets 為
  on-demand reference）
- ☐ Commit 2: `code-team/standards/refactoring-standard.md` 加 cross-link
  到 4 個 mindsets
- ☐ Commit 3: `domain-teams/.claude-plugin/plugin.json` 5.4.0 → 5.5.0
- ☐ Commit 4-6: dev-workflow `complexity-critique` skill 跨 plugin
  delegation
