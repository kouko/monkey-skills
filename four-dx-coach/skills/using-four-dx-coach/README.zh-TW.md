# using-four-dx-coach（路由）

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> four-dx-coach plugin 的入口 router。把一般 / 模糊的 4DX 問題分派到對的 atomic skill — 或者乾脆拒絕（4DX 不對的時候）。

## 何時觸發這個 skill

- 「想要開始用 4DX」「4DX 從哪裡入手」
- 「4 個執行紀律怎麼開始」「想用 4DX 達成目標」
- 「執行 4DX 的步驟」「幫我把 4DX 用在我這個 case」
- 任何尚未指名特定 discipline 的一般 4DX 詢問

## 它做什麼（protocol 摘要）

Socratic 決策樹，把使用者 signal 對應到 7 個 atomic skill 之一：

| # | Signal | Route 到 |
|---|---|---|
| 1 | 不確定 4DX 適不適合這個 goal | `4dx-meta-strategy-triage`（6 verdict gate） |
| 2 | 「日常業務吃掉所有時間，沒空推 goal」 | `4dx-meta-whirlwind-triage`（7 日 audit、80/20 capacity） |
| 3 | goal 模糊 / 多優先 / 只有 activity 沒結果 | `4dx-d1-wig-formulation`（一條 *From X to Y by When*） |
| 4 | WIG 已定，不知道每天要幹嘛 | `4dx-d2-lead-measures`（predictive + influenceable） |
| 5 | tracking 太雜 / 沒在看 / 30 個 metric 的 DB | `4dx-d3-scoreboard`（≤4 元素、5 秒測試） |
| 6 | D1-D3 都齊了但沒有 cadence | `4dx-d4-cadence`（週次 Account → Review → Plan） |
| 7 | 實踐已停滯 / 中斷 / momentum 沒了 | `4dx-sustain-momentum-rescue`（診斷壞掉的那一層） |

新使用者的 canonical 順序是 1 → 2 → 3 → 4 → 5 → 6，7 在 cadence 斷掉時（不是「如果斷掉」是「斷掉的時候」）才呼叫。順序不是 optional — 4DX 是 "a matched set, not a menu"。

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| 使用者已指名特定 discipline（「WIG 怎麼寫？」） | 直接 route 到對應的 atomic skill，跳過 router |
| Enterprise / 跨部門 rollout（50 人以上、cascading WIGs） | 拒絕，請對方直接看書中第 6-10 章（Leader-of-Leaders） |
| 軟體流程（agile / scrum / kanban / sprint planning） | 拒絕 — 不同 problem class |
| 沒有 breakthrough lag 的習慣養成（每天 meditate、每晚用牙線） | 拒絕，推薦 Atomic Habits |
| 投機性 portfolio / pre-PMF | 拒絕，推薦 OKR / lean-startup |
| burnout / 憂鬱 / 臨床性疲憊 | 拒絕，請對方找臨床 / 諮商支援 |

## 出處

來自 Stage-0 BOOK_OVERVIEW 與 four-dx-coach plugin 七個 atomic skill 的 SKILL.md frontmatter。底層基於 *The 4 Disciplines of Execution*（2nd ed., 2021）。

完整 router 決策樹、針對非 4DX 問題的 handoff scripts（enterprise / habit / OKR / agile / burnout）、明確的不啟動 signal 見 [`SKILL.md`](SKILL.md)。
