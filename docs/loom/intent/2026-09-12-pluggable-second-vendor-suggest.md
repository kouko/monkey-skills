# 讓第二供應商建議可抽換且不中斷流程
originator: kouko
kind: product
needs-design: yes — 使用者看到的決策提示與回覆時機會改變，而且此多狀態互動目前沒有規格
evidence: [docs/loom/KICKOFF-DEFAULTS.md, loom-code/skills/write-plan/SKILL.md, loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md, loom-code/contract/manifest.yaml, loom-code/hooks/session-start]
status: confirmed 2026-09-12
publication: automatic — authorized 2026-09-12 by kouko

## Problem
目前這個 repository 每個完整變更都會停下來詢問是否使用第二家 AI reviewer。相關規則分散在多份流程文字、設定與契約中，因此不但反覆打斷使用者，未來要修改風險條件或抽換建議策略也容易漏改。

## Proposed outcome
新增以不使用第二供應商為預設的 `suggest` 模式：Loom 根據已經產生的變更風險證據，必要時給一次不阻塞流程的建議；判斷由單一、可獨立測試與替換的策略模組負責。這個 repository 同時從 `ask` 切換到 `suggest`。

## Acceptance
1. 使用 `second-vendor: suggest` 時，Loom 不會為了第二供應商選擇而等待回答；沒有明確同意時，本次變更以 `none` 繼續。
2. full lane 只要異供應商 CLI 通過既有存在性檢查，Loom 就發出一次非阻塞訊息；高風險時訊息明確建議使用並說明風險原因，一般風險時只告知工具可用。
3. small lane 在異供應商 CLI 可用時只告知工具可用，但不允許為該次變更新增第二 reviewer；沒有可執行的異供應商 CLI 時不發出訊息，所有路徑都保留可檢查的決策原因。
4. 使用者在 Closing Review 開始前明確同意時，本次變更採用該第二供應商；拒絕或未回覆維持 `none`。Review 開始後的同意不改變本次 reviewer 身分，僅提示可套用到下一個變更。
5. `none`、`ask` 與固定 CLI 的既有語意保持不變；`suggest` 是獨立且向後相容的新模式。
6. `suggest` 的判斷核心是無 I/O、輸入輸出明確的單一模組；skill、hook 與 checker 不複製風險判斷，未來可替換策略而不重寫整條 Loom 流程。
7. `monkey-skills` 的 kickoff default 改為 `second-vendor: suggest`，之後的變更依上述規則運作。

## Constraints
- 不新增第四個人類決策關卡，也不在背景等待回覆。
- 不偷偷執行或安裝異供應商 CLI；只有使用者在 Review 前明確同意才可選用。
- 不把風險分數重新散落到 skill prose、hook、checker 或 provider adapter。
- 保持各 Loom plugin 可獨立安裝；不建立 sibling plugin 的私有 runtime 依賴。
- 不改變 full lane 與 small lane 原有的 reviewer 數量要求。

## Value case
GO — 可減少每個完整變更的一次阻塞詢問，同時在真正高風險時保留跨供應商提醒；單一純策略模組也讓未來調整訊號或供應商選擇不必同步重寫多份流程規則。

## Out of scope
- 自動授權資料傳給第三方模型。
- 自動安裝、登入或付費使用第二供應商工具。
- 建立通用 plugin policy engine 或通用工作排程器。
- 改變 reviewer verdict、Review round、attestation 或 publication gate。

## Open questions
- none
