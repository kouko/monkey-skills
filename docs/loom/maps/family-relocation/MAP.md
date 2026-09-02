---
map-id: family-relocation
schema_version: 3
state: active
---

## Destination

決定 queue 層（backlog store＋plan ledger）、loom-memory、family hooks
的最終歸屬——搬進 loom-workflow、留在 loom-code、或部分搬——並把選定
路徑推進到「一個 adopting repo 能無 patch 採用」的程度。承接
north-star 備忘（queue 層概念上屬家族、實體上被 loom-code 持有，因為
跨 plugin 原語缺口）與 integration-seed 的「行為拉力、非打包」裁定。

user-ratified: kouko, 2026-08-29

- DA-1: queue 層／loom-memory／family hooks 的最終歸屬各有一個 user-ratified 裁定記在本圖 Decisions-so-far | state: open | kind: evaluative | user-ratified: kouko, 2026-08-31
- DA-2: 選定路徑下一個 adopting repo 無 patch 採用——以 kumiko-zaiku 或等價 repo 的 CI 綠 commit 為證 | state: open | kind: objective | user-ratified: kouko, 2026-08-31
- DA-3: Codex 側 F-7 對等解法落地或明文放棄 | state: open | kind: evaluative | user-ratified: kouko, 2026-08-31

## Notes

- 本圖是 decision-map 層的第一張 dogfood 圖（arc E 交付的實地驗證）。
- deep-research 類票的執行需使用者逐次授權（常設授權只涵蓋 Agent 工具）。
- loom 1.0 硬切換（2026-09-03）：delivery ticket 與 Brief 綁定已刪。本圖既有票原地封存、不轉換；`task-relocate-family-hooks`（type: delivery）維持可讀歷史，不再依它開工。新的交付片段改寫 `docs/loom/intent/<change-id>.md`（帶 `map: family-relocation`），並在本節列 `- delivery-intent: DA-<n> | <intent 路徑>`。無 DA 綁定舊 brief，故本圖沒有 `retired — 硬切換` 的 DA。

## Decisions-so-far

- 第一刀＝hooks 先動；queue 與 loom-memory 的順序掛 feasibility probe 量測後再裁。 (tickets/grilling-first-cut.md)
- 官方文件面查證完成：cache 佈局／placeholder 語意／路徑逃逸守衛／install-time plugin-dependencies 皆已是文件化表面，但 installed_plugins.json（現行版本唯一 oracle）與「執行期 sibling root 探索」兩者無任何文件化原語——量測基準交付 feasibility 票。 (tickets/research-plugin-root-primitives.md)
- feasibility 裁定（user-ratified 2026-08-29）：**FEASIBLE-with-reservation**——Claude Code 側機制夠格作地基，但 Codex 側對等解法（F-7）補齊前，搬遷不視為完成；hooks 第一刀解凍可動工。 (tickets/feasibility-cross-plugin-store-access.md)

## Not-yet-specified (fog)

- F-1: 搬遷後 loom-code 舊路徑的相容層要維持多久（deprecation 窗口與其守衛）？
- F-2: kumiko-zaiku 等 adopting repos 的遷移由誰觸發、排在搬遷的哪個階段？
- F-3: marketplace／manifest 對 plugin 間依賴的支援邊界（目前 manifest 測試明文禁止 mandatory sibling dependency）。
- F-4: loom-memory 的搬遷排序（已定：獨立於 hooks、於 feasibility probe 之後裁定）——殘餘問題只剩它與 queue 層是否同批。
- F-5: 跨 plugin 介面耦合的降級語意——loom-workflow 缺席時哪些閘變 N/A、哪些流程照跑，要寫成可驗規則而非散文；缺了它，「安裝獨立」會名存實亡（feasibility probe 的 exit-3 優雅降級只證明機制存在，未定義語意）。
- F-6: 跨 plugin 呼叫的單向性守衛——只允許 loom-code → loom-workflow，反向回呼即循環依賴；由哪個測試層（boundary 測試？contract-citation checker？）機械把守。
- F-7: Codex 側執行期 sibling-root 探索無任何機制（官方 docs 無 placeholder 變數、無安裝登記檔——research 票查證）；鏡射骨架現靠單版本 cache 目錄 glob，正式解法未定。（路由依據：擋的是本圖 Destination 的「adopting repo 無 patch 採用」跨 host 條件，故入本圖 fog 而非 backlog）

## Out-of-scope

- 三 plugin 全併（north-star fallback；本圖不重開此案）。
- decision-map 層本身的歸屬（已決：loom-workflow，admission rule 已入 README）。
