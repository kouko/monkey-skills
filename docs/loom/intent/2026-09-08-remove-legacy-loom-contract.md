# Remove legacy Loom contract compatibility
originator: kouko
kind: engineering
needs-design: no — internal checker, test, and workflow maintenance with no new user-facing interface
evidence: [docs/loom/intent/2026-09-08-simplify-loom-evidence-gates.md]
status: closed 2026-09-08 — PR #806

## Problem
上一輪已改用內容綁定的 attestation，但完整驗證與 CI 仍有不同測試範圍，隱私規則在入口與細部協議中說法不一致，部分測試仍靠整份文件雜湊，checker 也保留不再使用的舊 contract 路徑。結果是本機驗證通過後仍可能在 CI 才發現問題，維護者也必須分辨新舊兩套行為。

## Proposed outcome
Loom 只保留新版 attestation contract。本機 closing review 與 CI 共用完整測試入口；隱私入口清楚表達條件式語意判斷；契約測試驗證行為而非整份文件 bytes；舊 review ledger、probe replay 與相容分支全部移除。

## Acceptance
1. 在乾淨環境執行 closing review 的 package command，會涵蓋 GitHub CI 對 Loom family 執行的全部測試路徑。
2. 對不含模糊私人身分資訊的 commit 或 PR 文字執行 git-memory 流程，不會啟動語意 privacy judge；秘密掃描仍必定執行。
3. 合理修改 git-memory contract 文件時，不需要人工同步整份文件 SHA，破壞必要行為仍會被測試攔下。
4. 1.9 後的 checker 不再包含或接受舊 review.json、review-only HEAD、Task trailer、dispatch accounting、probe replay 或 package replay contract。
5. 新 attestation 的內容綁定、兩位 fresh-context reviewer、adversarial execution 與快速 publication validation 仍通過完整測試。

## Constraints
- 不支援舊 contract；採用舊流程的 repo 必須升級 plugin。
- 保留新版 attestation 的安全邊界，不以刪除驗證覆蓋換取簡化。
- 本輪不使用第二供應商 reviewer；closing review 使用兩位 fresh-context Codex reviewer。
- 保留 main checkout 未追蹤的 `work/`，不修改或刪除。

## Out of scope
- 重新設計 reviewer provider 或解決 Claude CLI 穩定性。
- 增加本機簽章或防範惡意 repo owner。
- 修改與 Loom family 無關的 plugin 或測試。

## Open questions
- none
