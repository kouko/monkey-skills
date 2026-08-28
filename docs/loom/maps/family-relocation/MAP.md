---
map-id: family-relocation
schema_version: 1
state: active
---

## Destination

決定 queue 層（backlog store＋plan ledger）、loom-memory、family hooks
的最終歸屬——搬進 loom-workflow、留在 loom-code、或部分搬——並把選定
路徑推進到「一個 adopting repo 能無 patch 採用」的程度。承接
north-star 備忘（queue 層概念上屬家族、實體上被 loom-code 持有，因為
跨 plugin 原語缺口）與 integration-seed 的「行為拉力、非打包」裁定。

## Notes

- 本圖是 decision-map 層的第一張 dogfood 圖（arc E 交付的實地驗證）。
- deep-research 類票的執行需使用者逐次授權（常設授權只涵蓋 Agent 工具）。

## Decisions-so-far

- 第一刀＝hooks 先動；queue 與 loom-memory 的順序掛 feasibility probe 量測後再裁。 (tickets/grilling-first-cut.md)

## Not-yet-specified (fog)

- F-1: 搬遷後 loom-code 舊路徑的相容層要維持多久（deprecation 窗口與其守衛）？
- F-2: kumiko-zaiku 等 adopting repos 的遷移由誰觸發、排在搬遷的哪個階段？
- F-3: marketplace／manifest 對 plugin 間依賴的支援邊界（目前 manifest 測試明文禁止 mandatory sibling dependency）。
- F-4: loom-memory 的搬遷排序（已定：獨立於 hooks、於 feasibility probe 之後裁定）——殘餘問題只剩它與 queue 層是否同批。

## Out-of-scope

- 三 plugin 全併（north-star fallback；本圖不重開此案）。
- decision-map 層本身的歸屬（已決：loom-workflow，admission rule 已入 README）。

## Parts

| Part | Join key | Status |
|---|---|---|
