# squash merge 後，intent 的 needs-design 檢查找不到帶那一行的 commit
originator: kouko
kind: engineering
needs-design: no — 只改一條 intent 規則讀哪個 commit；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/evidence/]
status: withdrawn — superseded by 2026-09-04-checker-seams

## Problem
`intent.needs-design-reason` 要求「最後改到 status／needs-design 那行的 commit」訊息逐字帶 `needs-design:` 行。分支上那個 commit 有帶，但 PR 以 squash 合併後，主幹上「最後改到那行的 commit」變成 squash commit（例如 #780 的 4e25360c），它的訊息沒有那一行，於是主幹上每個已合併 intent 跑 `loom_checker.py intent` 都被擋。W1-04 關閉 2026-09-02-simple-loom-flow 時撞到（實作者回報，2026-09-03）。

## Proposed outcome
已在主幹上的 intent 跑 `intent` 子命令不因 squash 而紅：規則改讀分支歷史裡帶那行的 commit，或接受 squash 訊息 body 內任一處出現該行（PR body 帶 trailer 時可能有）。

## Acceptance
1. 在乾淨 clone 的 main 上對 `docs/loom/intent/2026-09-02-simple-loom-flow.md` 跑 `loom_checker.py intent`：exit 0。
2. 分支上把 needs-design 改成 no 而 commit 訊息沒帶那行：照樣被擋（既有測試不動）。

## Constraints
- 不加規則、不加 waiver；只改該規則挑選 commit 的方式。

## Out of scope
- 其他讀 commit 訊息的規則（Task trailer）在 squash 後的行為——它們只看分支範圍，不受影響。

## Open questions
- 是否乾脆把 needs-design 行的責任交給 PR body（squash 保留 body），規則在主幹上讀 squash body、在分支上讀 commit。
