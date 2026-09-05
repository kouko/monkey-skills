# checker：修正輪只要提 finding 的讀者回來確認；探針與 verdict 的紀錄綁樹的內容，不綁 commit sha；關閉 intent 那一行與 review-only 同一個 commit
originator: kouko
kind: engineering
needs-design: no — 只改 checker 四條既有規則的重算方式、review 站一句與 ship 站 §6；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-artifact-language-policy/review.json, loom-code/scripts/loom_checker.py]
status: confirmed 2026-09-05

## Problem
#791 的 branch-end 審查跑了 11 輪。其中兩種浪費來自 checker 規則的重算方式，不是審查本身：
- **修正輪每輪都要兩位讀者**：只有 Codex 提了 finding，修好後 sonnet 也得再被叫來說「沒事」，否則 `push.verdicts-ge-2` 擋（它數的是每一輪的讀者數）。#791 至少三輪的第二位讀者只是來蓋章。
- **測試與探針紀錄綁 commit sha**：`push.probes-package-tests`、`push.probes-adversarial`、`push.reviewed-sha` 都要求紀錄的 sha 等於 reviewed commit。但只改 review.json 的 commit（派工紀錄、verdict）也會換 sha，於是整包測試（1368 個、45 秒）與四個探針檔重錄了約 8 次，內容根本沒變。改寫 commit 訊息補尾標那次，樹一個位元都沒動，也得再一輪雙讀者確認。

## Proposed outcome
1. `push.verdicts-ge-2`：checkpoint 的第一輪維持「≥2 位讀者」；之後的修正輪只要求**提出仍開放 finding 的讀者**回來給 verdict，沒提 finding 的讀者上一輪的 PASS 繼續有效——但條件是修正 delta 只碰到那些 finding 錨定的檔案；碰到別的檔案就仍要兩位。
2. `push.probes-package-tests`、`push.probes-adversarial`、`push.reviewed-sha`：紀錄的 sha 與 reviewed commit 的比對改成比「樹的內容」——`git rev-parse <sha>^{tree}` 相同即算同一個被審對象，且比對時排除 `docs/loom/<change-id>/review.json` 本身（它每輪都會變）。review-only commit、trailer-only 的歷史改寫都不再逼重錄。
3. review 站文字加一句說明新語意；`--list-rules` 的描述同步改。
4. **關閉 intent 不再自成一輪**（2026-09-05 決策點①追加，甲案）：`push.review-only-head` 允許最後那個 review-only commit 同時改 intent 的 `status:` 那一行；status 的關閉文法多接受 `closed <日期> — branch <分支名>`（PR 號在 squash commit 標題裡的 `(#N)` 找得回來，`intake.confirmed` 對 closed 的終態判定不變）。ship §6 改成：③ 之後一個 commit（review.json＋關閉行）→ push → PR → merge；不再有關閉輪、第二個 review-only、第二次推送。

## Acceptance
1. 拿 #791 的 review.json 當 fixture（round 3 只有 Codex 一位讀者確認自己的 finding 的那種情境），`loom_checker.py push` 不再以 `push.verdicts-ge-2` 擋；同一 fixture 若把修正 delta 改成碰了 finding 錨定以外的檔案，就仍會擋——兩種情境各一個測試。
2. 一個只改 review.json 的 commit 疊在已錄探針的 commit 上，`loom_checker.py push` 對 `push.probes-*` 與 `push.reviewed-sha` 都 exit 0，不需重錄；一個改了任何其他檔案的 commit 疊上去則照舊擋——各一個測試。
3. trailer-only 的歷史改寫（同樹、不同 sha）後，既有 verdict 與探針紀錄仍被接受——一個測試在沙盒 repo 用 filter-branch 重現。
4. `--list-rules` 規則數不變（27），三條規則的描述句更新且仍是「重算」語意。
5. 既有測試全綠，畢業探針不需改。
6. 一個 review-only commit 同時含 review.json 與 intent 的 `status: closed <日期> — branch <名>` 那一行時，`loom_checker.py push` 對 `push.review-only-head` exit 0；同一 commit 若改了 intent 的其他行、或改了任何第三個檔案，仍擋——各一個測試。`intake.confirmed` 對 `closed … — branch …` 與 `closed … — PR #N` 都判終態。ship 站文字的 §6 沒有「關閉輪」，有釘測試；這份 intent 自己就用甲案關閉，PR 內文列出 `git log <reviewed_sha>..HEAD` 只有一個 commit。

## Constraints
- 不加規則、不刪規則；改的是四條既有規則的重算方式（verdicts-ge-2、probes-*、reviewed-sha、review-only-head）與關閉文法。
- 「沒提 finding 的讀者 PASS 繼續有效」只在修正 delta 沒碰到其他檔案時成立，這是安全底線，不可放寬。

## Out of scope
- 站文字與契約的搬動（記憶步驟位置、散文釘規則、尾標命令）——另一份 intent。
- 減少第一輪的讀者數或小車道規則。

## Open questions
- none
