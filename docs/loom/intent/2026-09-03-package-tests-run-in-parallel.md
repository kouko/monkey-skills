# 整包測試平行跑
originator: kouko
kind: engineering
needs-design: no — 改一行測試命令與一個開發依賴；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost-orchestrator-notes.md]
status: open

## Problem
本 repo 的整包測試（1061 條）在本機要 200 秒，因為多數測試各自建臨時 git repo 並開子程序，而 macOS 開程序慢。每個 checkpoint 至少跑三次（reviewer 自跑、盲跑、push 閘重算），一輪 review 光等測試就十分鐘以上；subagent 也因此撞 Bash 工具 120 秒預設逾時五次。測試彼此獨立，卻全部串行跑在 16 核的機器上。

## Proposed outcome
`package-tests` 那一行改成用 pytest 的多程序外掛（`pytest-xdist`，`-n auto`）分到多核心跑，KICKOFF-DEFAULTS、CI 與 checker 逐字比對的命令三處同步改；外掛列為開發依賴。目標本機 60 秒以內。

## Acceptance
1. 在乾淨環境照 README 裝好開發依賴後，跑 KICKOFF-DEFAULTS 記的那行命令，1061 條全過，本機牆鐘時間低於原本的三分之一。
2. CI 用同一行命令且綠燈；`loom_checker.py push` 對 `package-tests` 探針的逐字比對仍通過。
3. 沒有測試因為平行而互相踩到（連跑三次結果一致）。

## Constraints
- 命令是契約的一部分：KICKOFF-DEFAULTS、CI workflow、checker 的比對三處同一個 change 一起改，不分批。
- 不改測試本身的寫法；共用 fixture／少開子程序另立 intent。
- 平行度（`-n auto` 或固定核心數）由 agent 依 CI runner 與本機的實測決定並記在 KICKOFF-DEFAULTS 那一行的註解裡，不問使用者。

## Out of scope
- 探針重跑的去重與平行（另一條 intent：2026-09-03-push-gate-reruns-probes-per-artifact）。

## Open questions
- none
