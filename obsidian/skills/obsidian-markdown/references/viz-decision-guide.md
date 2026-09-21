# 視覺化選擇指引

> 用法：每次新增 diagram/table/callout 前，分析內容類型並自動選擇對應格式。

## 自動選擇決策邏輯（Agent 適用）

```
IF 內容 = 流程/決策/狀態機 → USE Mermaid flowchart
ELIF 內容 = 概念關係/層級 → USE Mermaid mindmap
  EXCEPT 大量文字 → USE 巢狂列表 + 標題層級
  NOTE: mindmap 屬非 flowchart 類型，實際使用時仍須委派 `obsidian:obsidian-mermaid-visualizer`
ELIF 內容 = 多維度比較 → USE Markdown 表格
  EXCEPT 維度 > 4 → USE 結構化文字
  NOTE: 可考慮轉置（項目為欄、維度為列）僅在 項目數 < 維度數 且 項目數 ≤ 4 時有效
  REFERENCE strategy-lever-and-cascade 3×N table 格式
ELIF 內容 = 關鍵洞察/警告 → USE Callout (`[!tip]`/`[!warning]`)
  EXCEPT callout > 2 → USE 章節標題
ELIF 內容 = 時間序列/演進 → USE Mermaid timeline
  EXCEPT 資料點 > 12 → USE 表格
ELIF 內容 = 空白草圖/構想 → USE Mermaid flowchart / Mermaid mindmap
  EXCEPT 匯入現有 Mermaid → KEEP Mermaid
ELIF 內容 = 2×2 分類 → USE Mermaid quadrant-chart
  EXCEPT 詳細紀錄 → USE 表格
ELIF 內容 = 純文字列清單 → USE 巢狀列表 / 區塊引用
  EXCEPT 項目 > 10 → USE 目錄
ELSE → USE 純文字 + 標題層級
```

## 快速對照表

| 內容訊息 | 推薦呈現 | 何時避免/改用 |
|----------|----------|---------------|
| 流程/決策/狀態機 | Mermaid flowchart | 節點超過 6 個 → 委派 `obsidian:obsidian-mermaid-visualizer` |
| 概念關係/層級 | Mermaid mindmap | 大量文字 → 巢狂列表 + 標題層級 |
| 多維度比較 | Markdown 表格 | 維度超過 4 → 結構化文字；可轉置僅在項目數 < 維度數 且 ≤ 4 時 |
| 關鍵洞察/警告 | Callout (`[!tip]`/`[!warning]`) | callout 超過 2 個 → 章節標題 |
| 時間序列/演進 | Mermaid timeline | 資料點超過 12 個 → 表格 |
| 空白草圖/構想 | Mermaid flowchart / Mermaid mindmap | 匯入現有 Mermaid → KEEP Mermaid |
| 2×2 分類 | Mermaid quadrant-chart | 詳細紀錄 → 表格 |
| 純文字列清單 | 巢狀列表 / 區塊引用 | 超過 10 項 → 目錄 |

> **專業領域參考**：多維度比較（策略槓桿 vs 情境）請參考 `systems-thinking-toolkit/skills/strategy-lever-and-cascade/SKILL.md` 的 3×N table 格式（欄位=槓桿、列=情境、儲存格=目標設定、分類=robust/contingent/bet）。

> [!abstract] 一句話結論
> 流程→Mermaid diagram，比較→表格，洞察→callout，草圖→Mermaid/列表。