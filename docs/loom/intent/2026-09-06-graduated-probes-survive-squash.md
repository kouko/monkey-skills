# 畢業探針在壓過的 main 上仍然綠
originator: kouko
kind: engineering
needs-design: no — 只動 loom-code 的檢查腳本、排練腳本與測試，沒有任何使用者讀或輸入的介面改變
status: closed 2026-09-07 — branch graduated-probes-survive-squash

## Problem
畢業探針（change 結束時從 `evidence/probes/` 複製進 `loom-code/scripts/test_probes_*.py` 的常設測試）在分支上全綠，squash 合併之後在 main 上紅。今天 main 就有一支：`test_probes_charter_wave_end_2.py::test_charter_and_plan_edits_agree_the_real_change_id_resolves`，它請 checker 檢查「自己這個 change 的 plan 定稿後有沒有被亂改」，而 checker 是靠 `docs(loom): plan <change-id>` 這個 commit 訊息找基準點的——squash 把那顆 commit 壓掉了，於是它回 `BLOCK plan.edits-after-commit: no plan commit found`，測試就紅。

這不是那支測試寫錯，是一整類問題：**畢業之後的探針還在對「自己 change 的歷史」提問，而合併會把那段歷史刪掉**。1.6.1 加的排練（`rehearse_probes.py`）本來就是為了擋這一類，但它複製的是分支的歷史，plan commit 在裡面還活著，所以照樣綠燈放行。同一個 change 的 rebase 期間，另外三支探針也是踩同一顆地雷（釘死的 sha、被上游刪掉的 helper、釘死的版本號），都是靠人工發現的。

順帶暴露的第二件事：對一個已經出貨的 change 問 checker「plan 定稿後有沒有被亂改」，它今天一律回 BLOCK。這對任何採用 loom 的 repo 都成立——合併之後那個問題就變成無解，而 BLOCK 讀起來像「有人亂改了」，其實是「這個問題已經不適用了」。

## Proposed outcome
兩層一起補。第一層，畢業前的排練除了現在的乾淨 clone，再多跑一次「壓過的 main」形狀——把分支歷史壓成一顆 commit 的副本——任何依賴自己 change 歷史的探針在那裡就會紅，畢不了業。第二層，checker 對一個已經關閉的 intent 不再回誤導的 BLOCK，而是明說這個問題不適用。規則寫進 build 站的畢業段落，並有釘測試，讓下一個 change 不用重新學。

## Acceptance
1. 我在合併後的 main 上跑整包測試，沒有任何測試因為「找不到自己 change 的 commit」而紅；今天那支紅的測試變綠。
2. 我拿一支故意依賴自己 plan commit 的探針丟進畢業前的排練，排練是紅的，並指名是哪一支、為什麼；把那個依賴拿掉之後排練轉綠。
3. 我對一個已經出貨、intent 已關閉的 change 問 checker「plan 定稿後有沒有被亂改」，它不會給我一個看起來像「有人亂改了」的 BLOCK，而是說這個問題對已合併的 change 不適用。
4. build 站的畢業段落寫明這條規則（畢業探針不得依賴自己 change 的 commit 存在），而且有測試釘住那句話，改掉就紅。
5. 整包測試通過，改到的 SKILL.md 仍在字數帽內。

## Constraints
- 不放寬既有保證：排練現有的乾淨 clone 檢查照跑，只是多一種形狀；checker 對「還在進行中」的 change 該 BLOCK 的照樣 BLOCK。
- 不碰 `loom-workflow/skills/git-memory/scripts/memory-grep.sh`——那個檔案上有另一條分支 `memory-grep-single-pass` 正在改，等它合併再處理它的 broken pipe。
- 已經畢業的探針如果依賴自己的歷史，就地修好，不是刪掉了事。

## Out of scope
- main 上另一個紅（`memory verify-merged` 這個 CI job 的 broken pipe）——等 `memory-grep-single-pass` 合併後另開。
- plan 欄位字數帽換成形狀規則（先前擱置的提案）。
- 排練速度的最佳化（clone 佔 2.7 秒那件事）。

## Open questions
- checker 要怎麼知道一個 change 已經出貨？看 intent 的 `status: closed`，還是看 plan commit 找不到就退回「不適用」？兩種都可能誤判，實作時決定並寫下理由。
