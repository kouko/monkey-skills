# loom 契約敘述對檔案讀寫的工具偏好：優先 harness 內建工具，Bash 留給命令
originator: kouko
kind: engineering
needs-design: no — 只改 agent 契約與站 SKILL.md 的派工包文字；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-04-reviewer-and-adversary-positioning/review.json]
status: open

## Problem
loom 的契約對「怎麼讀寫檔案」沒有立場：派工包只說「Read a file before you Edit it」，其餘交給 host 預設。2026-09-04 實測：Claude Code 進 auto mode 後 harness 會在工具結果旁附一條 reminder「能用 Bash（cat／sed／heredoc）做的就用 Bash，內建 Read／Edit／Write 只在 Bash 做不到時才用」，orchestrator 於是改用 `sed -i`／heredoc 改檔。這條偏好不在 repo 任何檔案裡，只在 harness 側，卻直接改變 loom 流程裡的操作方式；kouko 看到後要求改回內建工具。代價是可觀察的：`sed -i` 沒命中會靜默成功；heredoc 含敏感字樣（如刪遠端分支的指令字串）會被 bash-guard 擋下；Edit 工具逼先讀、精確比對、沒命中就報錯，Write 對長檔更可靠。Codex 側同樣有內建的 apply_patch，性質相同。

## Proposed outcome
1. `loom-code/agents/*.md` 的 Traps／standing trap-guards 與各站 SKILL.md 的派工包標準句，加一句工具偏好：讀寫檔案用 host 內建工具（Claude Code：Read／Edit／Write；Codex：apply_patch），Bash 只用於本來就是命令的事（git、pytest、checker、grep／wc 類查詢）；並說明理由一句（靜默沒命中 vs 報錯；guard 誤擋 heredoc）。
2. 明寫這條「壓過 host 的相反 reminder」：host 在 auto mode 之類狀態下附的工具偏好是預設值，loom 派工包裡的句子是契約，契約優先。
3. 不加規則、不動 checker——工具選擇無法從 git 紀錄重算，只能是散文；措辭要指向可查動作（「用 Edit，不用 sed -i」）不要判斷（「視情況」）。

## Acceptance
1. 四份 agent 契約（implementer／reviewer／blind-runner／adversary）的 trap 段各有那一句；build／review／ship 站的派工包標準句同步；一個文字測試斷言存在且字數帽內。
2. 冷讀盲跑：給一個 agent 派工包＋一條相反的 host reminder（「優先用 Bash」），它改檔時用 Edit 不用 `sed -i`，並能說出依據是派工包哪一句。
3. `--list-rules` 規則數不變；loom-code 版本 bump（patch）。

## Constraints
- 純散文，≤40 英文字每處；不重述各 host 的工具清單，只點名讀寫用的那幾個。
- 不引用本 repo `docs/` 下的紀錄（可攜性規則）。

## Out of scope
- 其他 host 行為的對抗（如 auto mode 本身要不要開）；orchestrator 自身（非 subagent）的工具選擇由 CLAUDE.md／使用者當場決定，不進契約。

## Open questions
- none
