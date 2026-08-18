---
id: no_other_consumer_needs_edges
status: open
statement: 檢查點之前沒有其他 loom 或 think-orbit 工作把「loom 決策帶 inputs 邊」列為前置
breaks_if: 任一 plan 或 BACKLOG 條目把 loom 決策節點帶 inputs 列為自己的 start 條件或依賴
branch: b_defer
---
