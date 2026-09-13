# Claude Code empty-output and timeout handling — plan
intent: 2026-09-10-stabilize-claude-second-reviewer@d511eb1c7d53b7fc0dd11be7705f8335c5bb2622
spec: docs/loom/2026-09-10-stabilize-claude-second-reviewer/spec.md@190512e00d1e353349597d8aad632e17f44441e1
charter: 1.0

## Task DAG

### Wave 1 — One bounded Claude invocation seam

**W1-01 Make one Claude review attempt observable**  after: none  acceptance: 1, 2, 3, 4
- Files: loom-code/scripts/claude_reviewer.py, loom-code/scripts/test_claude_reviewer.py, loom-code/scripts/test_simplified_station_text.py, loom-code/skills/review/SKILL.md, loom-code/CHANGELOG.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json
- Test: A1 positive: valid-output-passthrough; boundary: no-extra-preflight. A2 positive: nonempty-output; negative: whitespace-output. A3 positive: within-timeout; boundary: timeout-diagnostic. A4 positive: existing-single-retry; negative: no-runner-retry.
- Risk: agent-decided — add one single-attempt Claude-specific runner because prose cannot deterministically distinguish blank output or terminate a hung process; keep retry ownership in Review and add no parser, state, preflight, or generic executor framework.

## Questions asked

1 — what — 請確認：你要的是選擇 Claude Code 後，它能可靠完成真實唯讀審查；若失敗，能明確指出是登入、模型、權限、逾時、程序或格式問題，且最多只重試一次，不新增 ledger、背景服務或額外 review 輪次。對嗎？
1 — consequence — 回答「對」也代表：完成 Review 與發布檢查後可自動 non-forced push 並開 Ready PR；合併仍會另外等你授權，你也可以在發布前取消。
1 — what — 另外，這次 Closing Review 是否也要實際使用 Claude Code 作為第二讀者？
2 — behaviour — 你選擇 Claude Code 當第二讀者後，它會以唯讀方式完成審查並回傳有效結果；執行中不修改 repo；暫時失敗會在同一份內容上重試一次；登入、模型或讀取權限不可用時會直接說明原因；第二次失敗或輸出仍無效時，會回報具體錯誤並停止，不會無限重跑。受控 dogfood 也會比較審查前後的 repo 狀態。這樣的行為符合你的預期嗎？
2 — behaviour — 正式審查前的測試會使用相同的 Claude 執行檔、模型、登入來源、唯讀權限、repo 範圍、timeout 與結果格式；只有審查內容縮小。暫時性錯誤、逾時或格式錯誤才重試一次；已確定是登入、模型權限、讀取權限或固定設定錯誤時，立即說明修復方式並停止。dogfood 會刻意要求 Claude 建立一個測試檔案；Claude 必須沒有寫入工具或被拒絕寫入，且執行前後整個 working tree 的路徑與內容指紋完全一致。這樣的行為符合你的預期嗎？

## Risks

1. A fixed timeout can still terminate a legitimate slow review; the runner reports that boundary rather than hiding it or retrying internally.
2. Nonempty but malformed reviewer content remains owned by the existing reviewer-contract validation and executor retry; this change does not add a second parser.
3. A real Claude dogfood call spends external quota and can still expose provider-side variance; deterministic subprocess tests cover the two failure branches without network dependence.
