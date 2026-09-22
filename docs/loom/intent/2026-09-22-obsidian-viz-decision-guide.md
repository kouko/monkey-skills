# obsidian-viz-decision-guide：新增視覺化選擇指引
> **已由 obsidian 3.20.4 取代**：本 intent 與同資料夾的 attestation 記錄的是初版指引，內容已改寫，見 `obsidian/CHANGELOG.md` 的 3.20.4。
originator: kouko
kind: engineering
needs-design: no — 更新 skill 文件與參考指南；無需設計變更
evidence: []  # 將在審核過程中填入
status: in-progress

## Problem
Obsidian Flavored Markdown skill 需要統一的視覺化選擇指引，以幫助使用者和代理人在筆記中選擇適當的視覺化格式（Mermaid diagram、表格、callout 等）。目前缺乏明確的決策邏輯，導致視覺化選擇不一致。

## Proposed outcome
1. **新增 Visual Decision Guide**：在 `obsidian/skills/obsidian-markdown/references/viz-decision-guide.md` 中提供自動選擇決策邏輯和快速對照表。
2. **更新 SKILL.md**：在寫內容步驟中引用視覺化選擇指引，並在文末添加「Visual Choice Guide」章節。
3. **決策邏輯清晰**：提供 IF/ELIF 决策树，基于内容类型（流程/决策/状态机、概念关系/层级、多维度比较等）自动选择推荐格式。
4. **边界条件处理**：明确何时应避免推荐格式并改用替代方案（例如：流程节点超过6个时委派可视化工具）。

## Acceptance
1. Viz Decision Guide 文件存在于 `obsidian/skills/obsidian-markdown/references/viz-decision-guide.md` 并包含决策逻辑。
2. SKILL.md 已更新以引用新指南。
3. 决策逻辑涵盖9种内容类型：流程/决策/状态机、概念关系/层级、多维度比较、关键洞察/警告、时间序列/演进、空白草图/构想、2×2分类、纯文字列表。
4. 每种内容类型都有明确的推荐格式和边界条件（何时改用其他格式）。
5. 包含快速对照表供快速参考。
6. 决策逻辑以代理人可用的 IF/ELIF 伪代码形式提供。

## Constraints
- 不更改现有 skill 结构或强制要求。
- 仅添加引用和参考文件。
- 决策逻辑作为建议而非强制规则。
- 保持向后兼容性。

## Out of scope
- 实现自动化工具来强制执行这些决策（保留为手动流程）。
- 修改其他 skill 或插件。
- 添加新的可视化类型（仅提供决策指南）。

## Open questions
- 是否应该添加更多内容类型或格式？
- 决策阈值（如6个节点、4个维度等）是否需要根据实际使用进行调整？