# 從主分支推導 intent 交付狀態
originator: maintenance-loop
kind: product
needs-design: yes — intent 查詢與重複交付防護會新增 derived delivery state，目前沒有規格定義確認狀態與主分支交付證據的關係
status: confirmed 2026-09-09
publication: automatic — authorized 2026-09-09 by kouko

## Problem
變更已經合併後，對應的 intent 仍顯示為已確認，讓工作清單看起來還有待辦。使用者與 Agent 因此無法可靠區分真正尚未交付的工作和已經進入主分支的項目，也可能重複規劃已交付內容。

## Proposed outcome
Loom 不再於合併後補寫狀態，而是以主分支已包含該變更的交付證據推導 delivered。查詢工作清單時，只有已確認且主分支尚無交付證據的 intent 才算 active；PR 編號只在需要顯示時由 merge history 查出，不重複保存在 intent。這讓完成狀態與 merge 原子一致，不增加 commit、PR 或 CI。

## Acceptance
1. 當一個 current-contract intent 的交付證據進入目前遠端主分支後，Loom 會把它顯示為 delivered，不需要修改 intent 或建立後續 commit。
2. 已確認但交付證據只存在於 feature branch、未合併 PR 或本地工作樹時，Loom 仍會把它顯示為 active。
3. 查詢 active intents 時，PR #810、#811、#812、#813 對應的四份 intent 不再出現，而且不需要修改這四份歷史文件。
4. 一個已存在於主分支的 attestation 只有在 change-id 與 canonical intent 相符時才能作為交付證據；缺失、錯置或格式錯誤不得誤標 delivered。
5. 需要顯示 PR 編號或合併時間時，Loom 從實際 merge history 或 GitHub 查詢，不把衍生資訊重複寫回 intent；離線時可以只回報可由主分支證明的 delivered 狀態。
6. 既有的獨立 merge 授權、精確 HEAD 檢查、privacy gate 與 non-forced publication 行為維持不變。
7. 永久回歸測試會涵蓋已交付、未合併、僅本地證據、錯誤 change-id、缺少 attestation 與既有 legacy closed intent。

## Constraints
- 遠端主分支是交付狀態的唯一基準；feature branch 或 PR 狀態不能單獨證明 delivered。
- 不在 merge 前預寫 closed，也不在 merge 後補寫狀態 commit。
- 不新增 scheduler、ledger、review.json、probe replay、第二張 PR 或相容 shim。
- 既有 legacy `closed` 格式仍可讀，但 current contract 不再產生新的 close transition。

## Out of scope
- 自動合併未經使用者授權的 PR。
- 自動封存、刪除或改寫既有 intent、plan、spec、attestation。
- 清理與 PR #810～#813 無關的歷史文件。

## Open questions
- none
