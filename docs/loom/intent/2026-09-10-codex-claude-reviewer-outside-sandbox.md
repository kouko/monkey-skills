# Codex 使用 Claude 第二讀者時沿用既有登入
originator: maintenance-loop
kind: product
needs-design: yes — 第二讀者在受限環境內外會呈現不同登入狀態，現有規格尚未定義使用者可見的處理方式
evidence: [loom-code/skills/review/SKILL.md, loom-code/scripts/claude_reviewer.py, loom-code/scripts/test_simplified_station_text.py]
status: confirmed 2026-09-10

## Problem
使用者明明已登入 Claude Code，Codex 執行第二讀者時仍可能誤判成未登入，反覆要求使用者重新登入；同一個登入狀態在 Codex 的受限環境外其實可正常完成審查。

## Proposed outcome
Codex 使用 Claude Code 作為第二讀者時，標準使用能讀取既有 Claude 登入憑證的執行環境；受限環境內的未登入結果不再單獨作為要求使用者重新登入的依據。

## Acceptance
1. 已登入 Claude Code 的使用者可在 Codex 中直接完成 Claude 第二讀者審查，不必重複登入。
2. Codex 以允許讀取既有 Claude 認證的執行邊界呼叫既有單次 runner，仍保留原有 timeout、空輸出與一次重試行為。
3. 只有在該執行邊界仍明確回報未登入時，才要求使用者處理 Claude 登入。

## Constraints
- 不讓 runner 自行繞過 Codex sandbox；由 Codex 的工具授權邊界負責。
- 權限僅限既有 Claude reviewer runner，不建立廣泛 shell 或 Python 授權。
- 不新增 preflight、retry、ledger、背景服務或新的認證儲存。

## Value case
GO — 已實測同一台機器在 Codex sandbox 內回報未登入、sandbox 外則已登入且 review 成功；固定正確執行邊界可消除重複登入與錯誤診斷。

## Out of scope
- 修改 Claude Code 的登入、憑證格式或 macOS 認證儲存。
- 自動登入、讀取或搬移憑證。
- 擴大處理其他 Claude provider availability 問題。
- 改動既有 runner 的 empty-output、timeout 或 retry 契約。

## Open questions
- none
