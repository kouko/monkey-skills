---
type: delivery
status: open
claim: null
graduated-from: null
---

把 loom-code 的 family hooks（SessionStart 家族層 hook 群）搬遷到
loom-workflow，使 loom-code 的流程在「兩 plugin 各自安裝、互不含對方
檔案」的 cold-install repo 裡，經跨 plugin store 解析機制照常呼叫到它
們。本票由 feasibility 裁定（FEASIBLE-with-reservation，
tickets/feasibility-cross-plugin-store-access.md）解凍——hooks 第一刀
可動工；Codex 側對等（F-7）是搬遷整體的完成前提，不擋本票開工。

成功判準（事前定義）：一個 adopting repo（冷裝兩 plugin、無 patch）中，
loom-code 的 SessionStart hook 流程經 `installed_plugins.json` 指標解析
並執行 loom-workflow 所轄 hooks，端到端 exit 0；loom-workflow 缺席時
優雅 N/A；不寫死絕對路徑；不違反 plugin-boundary 測試等級的隔離。

承襲兩條件（feasibility Resolution，出處 research 報告 §Implications）：
- 解析器遇結構變異必須大聲失敗，且每次 session 重新解析（不吃快取）。
- CLI 大版本升級時重跑 feasibility probe 驗證結構未變。

介面方向守衛（F-6 精神，實作時機械化）：跨 plugin 呼叫只允許
loom-code → loom-workflow 單向；降級語意（F-5）在本票實作時一併寫成
可驗規則。F-4（queue 與 loom-memory 是否同批）不在本票範圍——維持
fog，待 hooks 搬遷的實測經驗進來後另案裁定。
