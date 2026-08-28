---
type: prototype
status: claimed
claim: feasibility-probe session, 2026-08-28
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
