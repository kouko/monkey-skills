# ui-verification

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> **在分支收尾之前，把真正 render 出來的 app 逐一開進 `ui-flows.md` 列舉的每個狀態。** 起源於 2026-07-03 的 pipeline dogfood：測試套件 28/28 全綠，但 render 出來的那一半 **完全沒有行為驗證** 就出貨了（code station 自己的台帳寫著 "no live browser was used"）。Package 測試驗證的是邏輯；它驗證不了 empty state 有沒有畫出來、error toast 到不到得了。

[loom-code](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類看的。

## 這個 skill 做的事

為 UI 變更中測試套件看不見的那一半設的 runtime gate：用 host 的自動化工具（`chrome-devtools` MCP、Playwright 系、`agent-device` MCP）打開真正的 app（瀏覽器 / 模擬器），走遍 `ui-flows.md` 列舉的每一條 §1 inventory row、render-variant 旗標（empty / loading / error / success / …）、flow 與 entry/exit point，每個狀態記錄一筆觀察。`critic-found` 的列是一級 checklist 項目 — 正因為 writer 漏掉，design-critic 才補上的。每個狀態分類為 `verified` / `mismatch` / `unreachable` / `untestable`；對開不進去的狀態若用較弱的靜態檢查代替，必須標成 **half-measure**，永遠不能升格為 `verified`。

## 使用時機

這個 gate 是 **CONDITIONAL** — 先檢查兩個條件、缺一不可：

1. 這次變更存在對應的 `ui-flows.md`（正規位置 `docs/loom/<change-id>/ui-flows.md`）。它就是 checklist；列舉由 design station 擁有，這個 skill 只擁有 runtime 檢查。
2. 分支動到了 UI surface — HTML / JSX / template / style / DOM 接線。

任一條件為偽 → 輸出 **`ui-verification: N/A`** 並附理由。N/A 是一級的誠實結果，絕不是默默跳過。Host 沒有瀏覽器 / 裝置自動化時也一樣：說 N/A 並說明原因 — 絕不用重讀原始碼來偽裝 walkthrough。

由 `finishing-a-development-branch` 與 `verification-before-completion` 並列呼叫（驗證的兩半：套件 + UI）；最後一個動 UI 的 SDD 任務落地後也可隨需執行 — 較早的那次執行能給 whole-branch reviewer 觀察證據，而不是重新推導出來的 UI 主張。

## 不使用時機

- 純邏輯分支 — 即使 repo 有 UI，條件 2 不成立，N/A。
- 這次變更沒有 `ui-flows.md` — 條件 1 不成立，N/A（這個 skill 從不自行重新推導列舉）。
- TUI / CLI — v1 範圍之外（對齊 design station 的 phase-2 姿態）；註明後停止。

## Verdict — 兩值制、沒有 bare PASS

- **`NEEDS_REVISION`** — 有任何 `mismatch`，或有任何未在 `ui-flows.md` 標為 future / deferred 的 `unreachable` 狀態。修正路徑回到 implementer；若是列舉本身錯了，則轉給 design station — 要說清楚是哪一種。
- **`PASS_WITH_NOTES`** — 所有開得進去的列舉狀態皆 `verified`；`untestable` 項目連同條件列出（這是本 skill 的盲點區，允許非空）。

刻意不存在 bare `PASS`：覆蓋率是相對於 `ui-flows.md` 的列舉，而列舉本身就有盲點。覆蓋率要說成「列舉 M 個狀態中 verified N 個」— 絕不說「UI 已驗證完畢」。

## 這個 skill 不做的事

- **不是 package 測試 gate** — 它補足、絕不取代 `verification-before-completion`。
- **不是 DESIGN.md token 一致性檢查** — 比對顏色 / 間距 / 字體是否符合 token 明確處於擱置狀態（loom-interface-design README §Scope，PR #473）；這個 skill 驗證的是行為狀態，不是視覺 token 值。
- **不是 design critic** — 從不往 `ui-flows.md` 加狀態，也不評判列舉好不好；獵捕遺漏是上游 `loom-interface-design:design-critic` 的工作。
- **不是 code editor** — verdict-only 角色：只觀察與回報，修正一律經 implementer 回路。

## 參考

- [`SKILL.md`](SKILL.md) — Agent 載入的運作規格（條件式 gate + 工具解析 + 5 步流程 + verdict 規則）。
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — package 測試側的姊妹 gate。
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — 同時呼叫兩個 gate 的 orchestrator。
- `loom-interface-design:interaction-flows` — 產出這個 skill 要開的 `ui-flows.md`；`loom-interface-design:design-critic` — 用 `critic-found` 列增補它。
