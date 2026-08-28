---
type: grilling
status: closed
claim: check-wayfinder, 2026-08-28
---

搬遷的第一刀怎麼切：queue 層、loom-memory、family hooks 誰先動？還是
先整批評估、一次決定順序再動工？討論需要對齊「行為拉力、非打包」裁定
與 PURPOSE.md 的可攜性判準。

## Resolution

裁定：**hooks 先動**。family hooks 是純散文契約，canonical fan-out 機制
已就位（loom-workflow/hooks 本弧已成為同步目標），完全不依賴「跨
plugin 腳本解析」這個未驗證的死穴假設——最小真步進、風險隔離。queue
層與 loom-memory 的動工順序不在此票決定：掛在
tickets/feasibility-cross-plugin-store-access.md 的量測結果之後再裁。
整批評估先行被否決（前置成本最重，且盤點已由
tickets/task-inventory-consumers.md 獨立排程）。

user-ratified: kouko 2026-08-28 — 選項「hooks 先動」經 AskUserQuestion 裁定。
