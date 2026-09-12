# 測試造假 repo 的時間比測試本身還長
originator: kouko
kind: engineering
needs-design: no — 只改測試內部產生測試資料的方式，不觸及任何使用者讀寫的介面
status: confirmed 2026-09-13
publication: automatic — authorized 2026-09-13 by kouko

## Problem
這個 repo 的完整測試套件在本機跑一次要 144.9 秒（2026-09-12 於 origin/main 89cf5d224 的乾淨 worktree 實測）。其中約 84 秒不是在測任何東西，而是在替測試準備假的 git 專案：三個地方各自用一次一個 commit 的方式，慢慢堆出兩千個、兩百個、兩百個 commit 的假歷史。

這套件在一次改動裡會被完整跑好幾次——每輪審查收尾跑一次，每次推送 CI 再跑一次——所以這段等待是每個改動都要付、而且付很多次的成本。

被拖慢的三處：
- `loom-workflow/tests/test-memory-grep-perf.sh`：整支 72.0 秒，其中 66.3 秒（92%）是在造那兩千個 commit
- `loom-workflow/skills/git-memory/scripts/test_probes_memory_grep_single_pass.py`：造測資 9.7 秒
- `loom-workflow/skills/git-memory/scripts/test_probes_memory_grep_render.py`：造測資 8.1 秒

## Proposed outcome
1. 完整測試套件在同一台機器上明顯變快。
2. 變快完全來自「準備測試資料」這件事，測試本身檢查的東西一條都不減。
3. 那支效能測試仍然是有意義的效能測試：它給被測腳本的仍是同樣規模、同樣形狀的兩千個 commit。

## Acceptance
1. 在乾淨 checkout 用這個 repo 自己宣告的完整測試指令跑一次，本機總時間 ≤ 95 秒（同機同指令的現況是 144.9 秒）。
2. 同一次執行裡，通過的測試數量不低於現況，失敗數為零。
3. `loom-workflow/tests/test-memory-grep-perf.sh` 單獨執行時仍印出 `12 PASS / 0 FAIL`，其中包含那三條確認測資形狀的斷言（300 筆紀錄、20 筆被標記為已取代、280 筆存活）。
4. `loom-workflow/skills/git-memory/scripts/` 的 pytest 群組單獨執行時仍是 64 passed。
5. 被測的程式碼檔案在這次改動的 diff 裡一個位元組都沒變。

## Constraints
- 只動測試檔裡準備測試資料的部分；任何被測的產品程式碼不得更動。
- 測試資料對被測程式而言的可觀察形狀不得改變：commit 總數、記憶紀錄數、被取代數、存活數、以及每個 commit 訊息的內容。
- 效能斷言的意義必須保留：被測腳本跑在兩千個 commit 的測資上，仍受既有的 2.0 秒本機上限與 5.0 秒 CI 容忍值約束。

## Out of scope
- 縮短 loom-code 主測試群組（它已經平行化，佔 20.6 秒）。
- 刪除任何測試、任何斷言，或降低任何既有的時間上限。
- 改動 CI 設定或這個 repo 宣告的測試指令本身。
- 其他沒有被實測指認為瓶頸的測試檔。

## Open questions
- none
