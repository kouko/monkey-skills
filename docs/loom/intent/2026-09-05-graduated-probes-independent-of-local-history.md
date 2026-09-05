# 畢業探針不得依賴本機分支歷史：畢業前在 CI 形狀的乾淨 clone 跑一遍
originator: kouko
kind: engineering
needs-design: no — 一支 repo 內的排練腳本加 build 站記憶步驟的幾行文字；沒有使用者讀或輸入的介面
evidence: [docs/loom/memory/pre-branch-end-ci-rehearsal-uses-full-history-without-a-local-main.md, .github/workflows/loom-code-ci.yml, loom-code/scripts/test_probes_complexity_wave_end.py]
status: confirmed 2026-09-05

## Problem
畢業探針（change 結束時從 `evidence/probes/` 複製進 `loom-code/scripts/test_probes_*.py` 的測試）在本機 worktree 全綠，合併後在 CI 才紅，已經發生三次（#789、#790、#794）。原因都一樣：探針讀了只有本機才有的東西——本機的 `main` 分支、或 change 自己分支上的某個 commit（squash merge 後就不存在）。每次都是 branch-end 過了才發現，代價是一輪修正加一個重做的關閉 commit；#794 那次還讓 main 的 CI 紅到下一個 change 順手修掉為止。

記憶條目已經寫了「在像 CI 的 clone 裡排練」，但那是散文，沒有東西逼人跑。而且現在 main 上有兩類畢業探針在 CI 裡永遠 skip（「那個 commit 不在這份 clone 的歷史」「那個 change 已經 shipped」），等於在 CI 什麼都沒驗，沒人看得到。

## Proposed outcome
一支 repo 自己的排練命令：在任何分支上跑，它自己做出一份像 CI 的乾淨 clone（完整歷史、有 `origin/main`、沒有本機 `main`），把畢業探針跑一遍，把 fail 與 skip（含理由）列出來，clone 裡紅就 exit 非 0。build 站的記憶步驟（探針畢業那段）寫明：畢業前先跑這命令，紅的不得畢業。現有兩類永遠 skip 的探針一併處理掉（刪除或改寫成不靠歷史），讓 main 在這命令下是 0 fail、0「歷史不在」類 skip。

## Acceptance
1. 我在本 repo 任一分支下一個命令，它自己建出像 CI 的乾淨 clone 跑畢業探針，輸出列出每支 fail 與每支 skip 的理由；本機綠、clone 紅時 exit 非 0，全綠 exit 0。
2. 我用一支故意讀本機 `main` 的合成探針試它：命令紅；把探針改成先讀 `origin/main`、都沒有就 skip，命令就綠。
3. build 站的記憶步驟文字寫明「畢業前跑這命令，紅的不得畢業」，且有釘測試守住那句話。
4. 這個 change 合併後，在 main 上跑這命令：0 fail，而且 skip 理由裡沒有「commit 不在歷史」「change 已 shipped」這兩類——現有的那幾支被刪掉或改寫了。

## Constraints
- 不加 checker 規則；排練是站文字＋腳本，不是 push gate。
- 命令只靠 git 與 pytest，不改 CI workflow 檔。
- loom-code patch 版本 bump（六處同步）。

## Out of scope
- 淺 clone（depth 1）那種比 CI 更嚴的環境——CI 用 fetch-depth 0，不排練它。
- 把排練搬進 checker 當 push rule。
- 其他 plugin 的測試。

## Open questions
- none
