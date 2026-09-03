# `**/templates/**` 預設被當成使用者介面，逼 engineering change 改成 product
originator: kouko
kind: engineering
needs-design: no — 只改 manifest 的預設 glob 與 checker 對它的解讀；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/evidence/]
status: open

## Problem
`loom-code/contract/manifest.yaml` 的 interface-surfaces 預設含 `**/templates/**`。在 loom 自己的 repo 裡，`loom-code/contract/templates/*.md` 是 agent 填的樣板，不是使用者讀或輸入的介面，但只要 diff 動到它，`intent.kind-recompute` 就拒絕 `kind: engineering`，要求改成 product（連帶 PRINCIPLES、白話 Problem、決策點②）。首例：change 2026-09-03-loom-post-merge-seams 的 W0-01 改 `templates/intent.md` 一行註解就被擋（只在 `intent`／`intake` 子命令，push 與 CI 不跑這條，所以那次沒被卡住）。KICKOFF-DEFAULTS 只能加 glob 不能減，repo 無法自救。

## Proposed outcome
一個只改 agent 樣板的 change 可以維持 `kind: engineering` 走完全程，而真正的使用者介面（CLI、API、tsx）照樣被 recompute 抓。

## Acceptance
1. 在一個乾淨 clone 裡，改 `loom-code/contract/templates/intent.md` 一行、intent 寫 `kind: engineering`：`loom_checker.py intent` 與 `intake write-plan` 都 exit 0。
2. 改 `src/cli/x.py` 一行、intent 寫 `kind: engineering`：兩者照樣被 `intent.kind-recompute` 擋（既有測試不動）。

## Constraints
- 不加規則、不加 waiver；解法可以是縮小預設 glob（例如 `**/templates/**` 改成前端樣板副檔名）、或讓 KICKOFF-DEFAULTS 可宣告「排除」但要說明為何不違反「只能加不能減」的原意。

## Out of scope
- 其他預設 glob 的重新檢討。

## Open questions
- 「只能加不能減」是為了防 agent 自己把介面排除掉；排除 agent 樣板要怎麼不開這個洞——可能的答案：以 artifact_types 的 `docs`／`skill` 型別先於 interface glob 判定。
