# ascii-graph-toolkit：開場 hook 的輸出改成 Codex 接受的格式
originator: kouko
kind: engineering
needs-design: no — a SessionStart hook's stdout is a `gate` artifact read by the host, not a declared interface surface in this repo
evidence: [ascii-graph-toolkit/hooks/session-start, ascii-graph-toolkit/scripts/test_trigger_card.py]
status: confirmed 2026-09-25
publication: automatic — authorized 2026-09-25 by kouko

## Problem
在 Codex CLI 0.157.0 啟用 ascii-graph-toolkit 之後，每次開 Codex 都會先跳出「Hook failed — hook returned invalid session start JSON output」，而且這個外掛的圖表觸發提示卡在 Codex 上完全不會載入。

原因是開場 hook 除了標準的 `hookSpecificOutput` 之外，最外層還多印了兩個備用欄位 `additional_context` 與 `additionalContext`。Codex 對開場 hook 的輸出採嚴格檢查（`codex-rs/hooks/src/schema.rs` 的 `deny_unknown_fields`），最外層多出任何欄位，整段輸出就判定無效。

## Proposed outcome
這個開場 hook 的輸出在 Codex 與 Claude Code 上都被接受，而且兩邊都讀得到提示卡的內容。

## Acceptance
1. 開場 hook 輸出的最外層只有 `hookSpecificOutput` 一個欄位。
2. 提示卡的內容仍然完整放在 `hookSpecificOutput.additionalContext` 裡。
3. 提示卡檔案不存在時，hook 仍然正常結束，輸出同樣格式的空內容。
4. 這個 repo 的測試會在最外層再出現其他欄位時失敗。

## Constraints
- 只改 ascii-graph-toolkit；loom-code 的開場 hook 已移到獨立的 loom-plugins repo，不在這裡改。

## Out of scope
- loom-code 開場 hook 的同一種寫法（目前在 Codex 上沒有執行，另行處理）。
- 提示卡本身的文字。

## Open questions
- none
