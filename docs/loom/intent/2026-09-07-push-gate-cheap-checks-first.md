# 讓 push gate 先擋下不需執行測試的失敗
originator: kouko
kind: engineering
needs-design: yes — push gate 在不同檢查結果下是否執行外部程式的多狀態行為會改變，現有規格未定義短路順序
evidence: [docs/loom/2026-09-06-reuse-branch-end-suite-result/review.json, docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/measurement.md]
status: closed 2026-09-07 — branch codex/2026-09-07-push-gate-cheap-checks-first

## Problem
Loom 的 push gate 會先執行完整 package suite 與 adversarial probes，才檢查 Task trailer、dispatch、verdict、第二位讀者等不需執行外部程式就能判斷的條件。後段條件失敗時，發布者已經付出完整 suite 的等待成本，修正帳務或證據後還必須再次執行同一套完整測試；採用 Loom 的其他 repository 也會承受相同成本。

## Proposed outcome
push gate 先完成所有不執行 package suite 或 adversarial probe 的 deterministic 檢查；只要其中任何一項阻擋，就立即回報並停止。只有 preflight 全部通過時，才依既有順序各執行完整 package suite 與 adversarial probes，最後重新確認 HEAD 與 working tree 未被外部程式改變。

## Acceptance
1. 任一既有 deterministic preflight 條件失敗時，push gate 會阻擋且不啟動 package suite 或 adversarial probe；這包含 Task trailer、dispatch coverage、verdict、第二位讀者、frozen store、reviewer independence 與 finding closure 等後段條件。
2. 所有 preflight 條件通過時，push gate 仍執行既有解析出的完整 package suite 恰好一次，並執行既有 adversarial probes；兩者成功且 repository 未改變時才允許 push。
3. package suite 或 adversarial probe 失敗、移動 HEAD 或改變 working tree 時，push gate 仍以既有 BLOCK 規則拒絕 push。
4. 這項短路行為不依賴程式語言、框架、檔案副檔名或 Monkey Skills 專用路徑，其他採用 Loom 的 repository 可直接使用。

## Constraints
- 保留所有現有 push BLOCK 規則、命令解析、錯誤文字、adversarial probe 與執行後 repository mutation 檢查。
- 保留成功路徑的完整測試覆蓋；不以歷史結果、cache 或 CI 結果取代本機 push gate 的當次執行。
- 不修改 main checkout、既有未追蹤的 `work/`，或既有 `slim-plan-doc`、`loom-script-performance` worktree。
- 以失敗測試先證明目前會錯誤啟動昂貴程式，再修改實作。

## Out of scope
- 移除或重設計 `review.json`、dispatch、verdict 或 finding ledger。
- 改變 probe 的生命週期、重播模型或畢業機制。
- 改變 git-memory privacy gate、PR privacy gate、push／merge 所有權或 CI。
- 建立 package-suite cache、跨階段 attestation、affected-test 分析或合併既有 worktree 的實作。

## Open questions
- none
