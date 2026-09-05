# 記憶步驟搬到 branch-end 審查之前；釘散文的測試規則與 Task 尾標檢查寫進契約
originator: kouko
kind: engineering
needs-design: no — 只改站文字（ship、build）與兩份 agent 契約，加對應的釘測試；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-artifact-language-policy/review.json, docs/loom/2026-09-04-codex-hook-trust-covers-every-definition-and-worktree/review.json, docs/loom/2026-09-04-positioning-paragraph-cap-redesign/review.json, docs/loom/memory/a-close-commit-sits-directly-under-a-checkpoint-so-any-late-fix-buys-its-own-round.md, docs/loom/memory/a-prose-pin-must-require-an-affirmative-un-negated-sentence.md]
status: closed 2026-09-05 — PR #792

## Problem
最近三個 change（#789、#790、#791）都在 branch-end 審查通過**之後**才做 ship 站的記憶步驟：探針畢業成永久測試、寫 `docs/loom/memory/` 條目。這些一定會產生新的 commit，而關閉 intent 的 commit 形狀規則要求最後三個 commit 長成固定樣子，於是每次都逼出一輪雙讀者確認、再重做關閉 commit。#791 為此重做關閉三次，收尾花的時間（約 6 小時）比實際改東西（約 4 小時）還多。這是流程排序的問題，不是誰做錯。

同一個 change 裡另外兩件重複發生的事：
- 用「關鍵字共現」寫的散文釘測試，被 Codex 讀者抓到三次同一類漏洞（否定句也能過），每次多一輪。教訓目前只在記憶庫，下一個寫釘的 agent 不一定看到。
- 修正輪的 implementer 漏寫 `Task:` 尾標，build 站雖有「回報 DONE 時檢查尾標」那句，但沒有給命令，我也漏做；等到 push 時才被擋，只能改寫歷史再確認一輪。

## Proposed outcome
1. ship 站的記憶步驟（探針畢業、記憶庫條目）改成在 **branch-end 審查之前**做——build 站在最後一個 wave 結束、呼叫 branch-end 審查之前，先做這兩件並 commit；branch-end 審查看到的就是最終的樹。ship 站在 branch-end PASS 後只剩：③、`questions[]` 追加、trailers、push、PR、關閉 intent（一行）與它的關閉輪。
2. adversary 契約與 engineering baseline（implementer 讀的那份）各加一句：釘散文的測試要求「肯定動詞在字面之前、同一句無否定詞、附正反兩個合成自測」。
3. build 站在 implementer 回報 DONE 時的檢查寫成命令，並在 wave 結束、合併 worktree 之後對整個 wave 的 commit 跑一次（`git log <reviewed_sha>..HEAD --format='%h %B' | grep -c '^Task: '` 之類），少一個尾標就不進 checkpoint。

## Acceptance
1. 一個新 change 的收尾分成兩個可觀察的點（2026-09-05 決策點①重確認時拆分——原條文把兩件事都要求在盲跑報告裡證明，但第二件在報告寫成時還不存在）：
   1a. 盲跑報告證明「記憶步驟（探針畢業、記憶庫條目）落在 closing review 之前，且該 change 的 wave 審查通過後沒有任何審後修正 commit」——列出 `git log <上一個 review-only commit>..<closing review 的派工紀錄 commit>`。
   1b. ship 在 PR 內文列出 `git log <branch-end reviewed_sha>..HEAD`，只有 review-only commit 與關閉 intent 的 commit（甲案落地後只剩一個）。
2. ship 站與 build 站各有一句寫明記憶步驟的位置（build：最後一個 wave 之後、branch-end 之前；ship：不再做畢業與記憶庫條目），並有站文字測試釘住。
3. `loom-code/agents/adversary.md` 與 `loom-code/references/engineering-baseline.md` 各有一句散文釘規則（肯定動詞、無否定詞、正反自測），有測試釘住；既有字數帽照既有授權處理（壓縮或調帽由 agent 決定並記錄）。
4. build 站 §4 與 §5 有可複製的尾標檢查命令；用一個故意漏尾標的測試 commit 在沙盒證明那條命令會抓到。
5. `loom_checker.py --list-rules` 規則數不變（27）。

## Constraints
- 不加 checker 規則；這個 change 只動站文字與契約（規則層的改動另開 intent）。
- 既有三個 change 的紀錄不回頭改。

## Out of scope
- checker 讓修正輪只要提 finding 的讀者回來、探針紀錄綁樹雜湊——另一份 intent。
- KICKOFF 的 package-tests 指令補 loom-design（候選，另開）。

## Open questions
- none
