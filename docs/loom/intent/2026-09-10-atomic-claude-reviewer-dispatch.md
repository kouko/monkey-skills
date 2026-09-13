# 讓 Claude reviewer 遵守原子 model 與 effort 分派
originator: kouko
kind: engineering
needs-design: yes — Claude reviewer runner 的 CLI 呼叫介面與可觀察執行參數會改變，目前沒有 ui-flow 文件涵蓋這個介面
evidence: [loom-code/scripts/claude_reviewer.py, loom-code/skills/review/SKILL.md, loom-code/references/dispatch-profile.md]
status: confirmed 2026-09-10

## Problem
新版 Claude reviewer runner 只能指定模型，不能把 resolver 決定的 model 與 effort 成對套用；當 resolver 要求 fallback 時，runner 仍會強制使用預設模型。這讓 Review 實際執行的 profile 與共享分派契約不一致，也阻止目前變更通過終局 Review。

## Proposed outcome
讓 Claude reviewer 路徑完整遵守共享分派結果：只有在 model 與 effort 都可驗證並可套用時才成對傳入；任何一項無法支援、無法驗證或 resolver 回傳 fallback 時，兩項都不覆寫並使用 host 預設。

## Acceptance
1. 在乾淨環境中執行 runner 的永久測試時，可以確認有效的 model 與 effort 配對會一起傳給 Claude Code。
2. 在乾淨環境中執行 runner 的永久測試時，可以確認缺少任一欄位、host 不支援或 resolver 回傳 fallback 時，不會傳入 model 或 effort 覆寫。
3. 在乾淨環境中執行 Review 契約與 dispatch regression tests 時，可以確認 Claude second-vendor 路徑與其他 subagent 路徑遵守同一套原子 fallback、retry 與無需使用者介入規則。

## Constraints
- model 與 effort 必須成對套用或成對省略，禁止 partial override。
- 只能使用經 Claude Code 實際 CLI surface 驗證的 effort 控制；無法驗證時必須安全 fallback，不得臆測參數。
- 保留既有單次 runner attempt、同 digest 最多一次 transient retry、stdin prompt、無 session persistence 與 sandbox 外窄權限邊界。
- 不讀取、複製或移動 Claude credentials，不新增登入 preflight。
- 不要求使用者在執行時選模型、effort 或處理 fallback。
- 不 push、不建立 PR、不 merge。

## Out of scope
- 重新設計共享模型階層、五階段 effort 政策或 redispatch 預算。
- 修改非 Claude second-vendor 的 host-native spawn 介面。
- 發布目前分支。

## Open questions
- none
