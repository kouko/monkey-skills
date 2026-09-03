# 舊的 Open questions 檢查腳本與 1.0 intent 模板打架
originator: kouko
kind: engineering
needs-design: no — 刪一支舊腳本與它的命令面條目，或改它的文法對齊模板；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/review.json]
status: open

## Problem
`loom-code/scripts/check_open_questions.py` 要求 intent 的 `## Open questions` 寫成 `- OQ-<n> [OPEN|RESOLVED] — …` 或一行固定的 `N/A — no unresolved question: …`，而 loom 1.0 的模板（`loom-code/contract/templates/intent.md` 第 28 行）與 capture-intent 站都說沒問題時寫 `- none`。這支腳本沒接進 `loom_checker.py`、hook 或 CI，但 `AGENTS.md` 的命令面仍把它列為 write-spec／write-plan 的 intake 自檢；照 1.0 模板寫的每一份 intent 跑它都 exit 1。branch-end 第 4、5 輪各有一位 reviewer 拿它當閘，各多花一輪。

## Proposed outcome
只留一個 SSOT：模板的 `- none` 與 `intent.schema` 的非空檢查。刪掉這支腳本、它的測試與 `AGENTS.md` 的條目；若有人要保留「每條開放問題要有狀態」的檢查，改成讀模板文法並接進 checker 的既有規則，不另開規則。

## Acceptance
1. repo 裡不再有任何命令面或站文字指向 `check_open_questions.py`，或者它對照 1.0 模板寫的 intent 全部 exit 0。
2. `loom_checker.py --list-rules` 的規則數不變。
3. 整包測試綠。

## Constraints
- 規則數不增；不改模板文法。

## Out of scope
- 其他 pre-1.0 殘留腳本的盤點（另立 intent）。

## Open questions
- none
