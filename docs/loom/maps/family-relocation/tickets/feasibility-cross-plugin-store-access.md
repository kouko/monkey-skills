---
type: prototype
status: closed
claim: kouko, 2026-08-28
---

（feasibility mode；風險前置——Riskiest Assumption Test：此假設若不成
立，整個搬遷即死）能否讓家族層腳本搬進 loom-workflow 之後，loom-code
的流程在「兩個 plugin 都各自安裝、互不含對方檔案」的 cold-install repo
裡仍然機械地呼叫到它們？成功判準（事前定義）：一個丟棄式測試 repo 中，
loom-code 的一個 hook／skill 流程可解析並執行 loom-workflow 所轄腳本，
不用寫死絕對路徑、不違反 plugin-boundary 測試等級的隔離。量測結果記
數字／pass-fail，於 prototype/family-relocation/feasibility-cross-plugin-store-access 分支上建。

進度（2026-08-28，probe 已跑完、結論待裁）：量測全數完成，工件在
prototype/family-relocation/feasibility-cross-plugin-store-access（commit
2aec80f1，`prototype-probe/PROTOTYPE_MEASUREMENTS.md`）。結果：冷裝 repo
中經 `~/.claude/plugins/installed_plugins.json` 指標檔解析並執行
loom-workflow 腳本全過（scaffold＋validate exit 0；真 headless session
SessionStart hook 端到端 exit 0；plugin 缺席優雅 N/A exit 3）；對照組
naive 版本 glob 有 7～33 路歧義，判不可用。kouko 2026-08-28 裁定：量測
承認，但 FEASIBLE 結論**保留至 tickets/research-plugin-root-primitives.md
查完官方文件面後再裁**——本票維持 claimed，不關。

## Resolution

user-ratified: kouko, 2026-08-29 — FEASIBLE-with-reservation

- 2026-08-29 kouko 裁定（user-ratified）：**FEASIBLE-with-reservation**。
  Claude Code 側機制夠格作為搬遷地基——量測全過，且文件面查證
  （tickets/research-plugin-root-primitives.md）僅 installed_plugins.json
  一項屬內部 API，其餘原語皆有文件。但 Codex 側尚無執行期 sibling-root
  探索的對等解法（F-7），補齊前列為搬遷完成的必要條件：hooks 第一刀
  可動工，搬遷整體不因 Claude Code 側走通即視為完成。
- 承襲兩條件（research 報告 §Implications）：解析器遇結構變異必須大聲
  失敗、每次 session 重新解析；CLI 大版本升級時重跑本 probe。
