# 同時符合 Codex 與 Claude Code 的 plugin 契約

originator: kouko
kind: engineering
needs-design: yes — plugin 與 hook 需在兩個宿主各自的載入、升級、事件與阻擋狀態間正確運作，目前沒有規格完整界定跨宿主行為
status: confirmed 2026-09-09
publication: automatic — authorized 2026-09-09 by kouko

## Problem
Loom 目前以偏向 Claude Code 的共用接線同時服務 Codex 與 Claude Code，沒有完整遵循兩邊各自的官方 plugin、skill 與 hook 開發規範。plugin 更新後，仍在執行的 Codex task 可能保留已消失的舊版 hook 路徑，導致普通唯讀命令也在執行前被阻擋。

## Proposed outcome
Loom 共用同一套核心規則，但為 Codex 與 Claude Code 分別提供符合各自官方規範的 manifest、skill 與 hook 接線。宿主差異由薄的專屬介面吸收；普通操作不因舊 plugin 路徑失效而中斷，發布操作仍維持 fail-closed。

## Acceptance
1. 我可以分別安裝 Loom 到 Codex 與 Claude Code，並由各自的官方 plugin、skill 與 hook 規範驗證其套件結構與執行契約。
2. 我可以在 Codex task 執行期間更新 plugin 或移除舊版 cache，之後的普通唯讀命令不會被舊 hook 路徑誤擋。
3. 我可以在相同情境下嘗試 push 或建立 PR，而發布檢查不會因 hook 或 checker 無法載入而被略過。
4. 新 session、resume、執行中升級與舊 cache 消失都有可重複執行的跨宿主驗證，且兩邊共用的核心發布規則得到相同結果。
5. Claude Code 作為第二位讀者，獨立檢查規格是否符合兩邊官方規範及是否遺漏宿主生命週期風險。

## Constraints
- 共用核心規則，宿主專屬層只處理 manifest、路徑、事件與輸入輸出契約差異。
- Codex 使用其官方 `PLUGIN_ROOT` 契約；Claude Code 使用其官方 `CLAUDE_PLUGIN_ROOT` 契約，不把相容變數當成跨宿主設計。
- 普通非發布操作在舊 plugin 路徑失效時必須可繼續；發布操作在無法驗證時必須 fail-closed。
- 解法需適用其他 repository，不得依賴 monkey-skills 的固定 checkout 或 cache 路徑。
- 先採用 plugin 內的最小宿主 adapter；除非實測證明不足，不新增全域 executable 或長期相容轉接檔。

## Out of scope
- model dispatch 與另一個進行中的 worktree。
- 修改 Codex Desktop、Codex CLI 或 Claude Code 本身的 cache 清理與 reload 行為。
- 重新設計 Loom 的 review、attestation、privacy 或 CI 機制。
- 合併本變更或其他內容。

## Open questions
- none
