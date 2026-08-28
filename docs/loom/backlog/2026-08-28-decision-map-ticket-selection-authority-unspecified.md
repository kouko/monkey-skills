---
name: 2026-08-28-decision-map-ticket-selection-authority-unspecified
description: decision-map work-through never says who picks the ticket — agent inference vs explicit user choice is a protocol blank
status: open
origin: family-relocation map dogfood, 2026-08-28 — the session inferred the ticket from a worktree branch name matching a ticket slug; the user expected to be offered the choice
---

# decision-map：票的選擇權未規範

`loom-workflow:decision-map` 的 Work-through mode 規定「一個 session 走一
張票、動工前先 claim」，但**沒有規定誰來挑那張票**。首張 dogfood 圖
（family-relocation）就撞上：session 以「worktree 分支名 == ticket slug」
推斷使用者已選票而直接動工；使用者事後表示原以為會被問。

這與 on-ramp 顯性選擇閘弧（loom-code 0.87.0，PR#704）抓到的病灶同類：
推薦／選擇被 agent 代決，缺一個「記錄的選擇」時刻。

## 待決的設計問題

- 進 work-through 時，若開放票 >1 且沒有明確訊號（使用者點名、分支名
  對應 slug、唯一可行票），是否必須讓使用者明選？
- 「明確訊號」清單要不要寫進協定（哪些情況允許 agent 直接 claim）？
- claim marker 要不要記選票依據（user-named / branch-inferred /
  only-candidate），讓代選變成可審計的記錄？

## Start（再觸發條件）

下一次修訂 decision-map SKILL.md／map-format.md 時一併裁定；或下一次
work-through session 再度遇到多票無訊號的選擇時。
