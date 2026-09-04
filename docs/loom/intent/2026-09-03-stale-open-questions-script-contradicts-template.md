# 舊的 Open questions 檢查腳本與 1.0 intent 模板打架
originator: kouko
kind: engineering
needs-design: no — 刪一支舊腳本、它的測試與命令面條目；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/review.json]
status: withdrawn — superseded by 2026-09-04-checker-seams

## Problem
`loom-code/scripts/check_open_questions.py` 要求 intent 的 `## Open questions` 寫成 `- OQ-<n> [OPEN|RESOLVED] — …` 或一行固定的 `N/A — no unresolved question: …`，而 loom 1.0 的模板（`loom-code/contract/templates/intent.md` 第 28 行）與 capture-intent 站都說沒問題時寫 `- none`。這支腳本沒接進 `loom_checker.py`、hook 或 CI，但 `AGENTS.md` 的命令面仍把它列為 write-spec／write-plan 的 intake 自檢；照 1.0 模板寫的每一份 intent 跑它都 exit 1。branch-end 第 4、5 輪各有一位 reviewer 拿它當閘，各產生一條 finding（那兩輪另有其他 finding，輪數不單獨歸因於它）。

## Proposed outcome
只留一個 SSOT：模板的 `- none` 與 `intent.schema` 的非空檢查。刪掉這支腳本、它的測試與 `AGENTS.md` 命令面的條目（agent-decided：1.0 沒有任何站呼叫它，保留就是第二個文法）。

## Acceptance
1. `loom-code/scripts/check_open_questions.py` 與它的測試檔不存在，repo 裡沒有任何命令面或站文字再指向它（`grep -rn check_open_questions` 只剩 CHANGELOG 與歷史記錄）。
2. `loom_checker.py --list-rules` 的規則數不變。
3. 整包測試綠。

## Constraints
- 規則數不增；不改模板文法；不改 `intent.schema`。

## Out of scope
- 其他 pre-1.0 殘留腳本的盤點（另立 intent）。

## Open questions
- none
