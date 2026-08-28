---
type: prototype
status: open
claim: null
---

（feasibility mode；風險前置——Riskiest Assumption Test：此假設若不成
立，整個搬遷即死）能否讓家族層腳本搬進 loom-workflow 之後，loom-code
的流程在「兩個 plugin 都各自安裝、互不含對方檔案」的 cold-install repo
裡仍然機械地呼叫到它們？成功判準（事前定義）：一個丟棄式測試 repo 中，
loom-code 的一個 hook／skill 流程可解析並執行 loom-workflow 所轄腳本，
不用寫死絕對路徑、不違反 plugin-boundary 測試等級的隔離。量測結果記
數字／pass-fail，於 prototype/family-relocation/feasibility-cross-plugin-store-access 分支上建。

## Resolution
