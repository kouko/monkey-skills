# obsidian-viz-decision-guide：新增視覺化選擇指引
originator: kouko
kind: engineering
needs-design: no — 更新 skill 文件與參考指南；無需設計變更
evidence: []
status: confirmed 2026-09-22

## Problem
Obsidian Flavored Markdown skill 需要統一的視覺化選擇指引，以幫助使用者和代理人在筆記中選擇適當的呈現方式（圖、表格、callout 等）。目前缺乏明確的決策邏輯，導致視覺化選擇不一致。

## Proposed outcome
1. **新增 Visual Decision Guide**：在 `obsidian/skills/obsidian-markdown/references/viz-decision-guide.md` 提供呈現方式的選擇邏輯。
2. **更新 SKILL.md**：在寫內容步驟中引用這份指引（只有一個入口）。
3. **分工清楚**：指引只決定用圖、表、callout、清單還是文字；圖要自己寫還是委派、用哪種 Mermaid 圖，交給 SKILL.md §Diagrams 與 `obsidian:obsidian-mermaid-visualizer`；callout 類型交給 SKILL.md §Callouts。
4. **防止再次重複**：自動測試擋下指引重寫其他地方已負責的規則。

## Acceptance
1. Viz Decision Guide 檔案存在於 `obsidian/skills/obsidian-markdown/references/viz-decision-guide.md` 並包含選擇邏輯。
2. SKILL.md 只有一處引用這份指引。
3. 選擇邏輯涵蓋 5 種呈現方式：圖、表格、callout、清單、文字。
4. 每一步都是看內容就能回答的是非題，並指明交接給哪個段落或 skill。
5. 指引不出現任何 Mermaid 圖種名稱，由測試檢查。

## Constraints
- 不更改現有 skill 結構或強制要求。
- 指引是建議而非強制規則；使用者指定呈現方式時照使用者的。
- 保持向後相容。

## Out of scope
- 實作自動化工具來強制執行這些決策。
- 修改其他 skill 或 plugin。
- 新增視覺化類型。

## Open questions
- 初版指引曾提出數字門檻（比較維度超過 4 改文字、callout 超過 2 個改標題、時間資料點超過 12 改表格、清單超過 10 項）。這些沒有實際使用依據，已移除；日後若實際使用發現需要，再依證據補回。
