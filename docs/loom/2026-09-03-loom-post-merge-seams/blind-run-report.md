# loom 1.0 合併後的接縫 — 我實際試了什麼、發生了什麼

試跑日期 2026-09-03，在乾淨的 worktree（`git worktree add ... --detach 664159a8`）裡進行，
分支 `loom-post-merge-seams`，HEAD `664159a8`。

## 你要的東西，逐條試

### 1. 關 intent 這件事推得出去（Acceptance #1）
- **怎麼試的**：用這個分支自己的 checker（不是裝置端快取），在一個乾淨的臨時 repo 裡照 ship 站寫的順序走一遍——checkpoint review（R1）→ 只改 intent 狀態那一行的關閉 commit → 再一輪只審那一行的 review（R2，裁定的 `sha` 對到關閉 commit）→ 只動審查記錄的收尾 commit → `push`。另外試了三個反例：①跳過那輪審查、直接把審查記錄的 `reviewed_sha` 指到關閉 commit（裁定的 `sha` 沒有跟著移）；②關閉 commit 多改一個字；③對已關閉的 intent 跑 `write-plan` 的 intake 檢查。
- **發生了什麼**：正常順序 `push` 直接放行，不需要任何人手動繞過，也沒有新規則。①被 `push.reviewed-sha` 擋下（訊息：裁定的 sha 對到舊 commit，不是現在要推的那個）。②被 `push.review-only-head` 擋下（訊息：這個關閉 commit 的內容跟「只改狀態那一行」重算出來的版本不一樣）。③被 `intake.confirmed` 擋下，訊息明講「this change is closed (PR #999)」。另外核對了上一個 change（2026-09-02-simple-loom-flow）——它的狀態確實已經在這個分支的歷史裡被順手改成 `closed 2026-09-03 — PR #780`。
- **證據**：`witness_acceptance1.py`（見下方檔案清單），四段輸出：正例 `exit code: 0`；反例①`BLOCK push.reviewed-sha` ×2 條；反例②`BLOCK push.review-only-head`；intake 反例輸出完整擋下訊息。
- **驗收**：works — 四種情境（正例＋三個反例）都照 Acceptance 描述的行為發生。

### 2. 契約認得 `closed`，整包測試綠（Acceptance #2）
- **怎麼試的**：跑 `loom_checker.py --list-rules`，看 `intake.confirmed` 那行的說明；跑套件測試命令 `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q`。
- **發生了什麼**：`--list-rules` 的 `intake.confirmed` 說明裡完整寫著「`closed <date> — PR #<N>` is blocked -- that change is closed」；`push.review-only-head` 的說明也提到「When HEAD^ turns an intent's status to closed」。整包測試：**1061 通過、0 失敗，耗時 188.6 秒**。
- **CI 沒辦法在這裡驗**：CI 跑的是同一組路徑加 `-v`（`.github/workflows/loom-code-ci.yml`），但這次是本機乾淨 worktree，沒有觸發 GitHub Actions——這一段照實記為「沒有跑，本機測試通過不等於 CI 通過」。
- **證據**：`--list-rules` 輸出片段；`1061 passed in 188.62s (0:03:08)`。
- **驗收**：works（本機部分）／not-yet（CI 部分，需要 PR 開出後才看得到，理由已如實說明）。

### 3. 副本刷新不算 gate 工作，改動內容才算（Acceptance #3）
- **怎麼試的**：在乾淨臨時 repo 裡真的重跑 `codex_scaffold.py --repo .`（就是刷新 `.codex/hooks/` 那些檔案的指令）並 commit，不帶 `Task:` trailer；然後分別試五種反例：改一個位元組、多放一個檔、刪掉一個檔、只改權限（mode-only）。
- **發生了什麼**：純刷新（跟這個分支自己跑出來的正本逐位元組一樣）的 commit `push` 直接放行。五種反例全部被 `push.dispatch-covers-tasks` 擋下，訊息各自點名原因：位元組不同、「no canonical counterpart for this path」（多出的檔）、「deleted at this commit」（刪檔）、「mode mismatch」（權限）。
- **證據**：`witness_acceptance3.py` 六段輸出，逐條對應。
- **驗收**：works — 正例與四種反例（位元組／多檔／刪檔／權限）皆如描述發生。symlink 反例本次未另外手跑（前述已由這個分支自己套件測試裡的等價案例覆蓋，見 `test_a_plumbing_path_is_blocked_when_the_checker_copy_is_a_symlink`），這裡標注為 partly 靠套件測試佐證，非我本人親手一步步跑出。

### 4. 這次 checkpoint 到底花了多少（Acceptance #4）
- **怎麼試的**：從 `git log 160658c2..664159a8`（82 個 commit）與 `review.json` 的 `dispatch[]`／`verdicts[]`／`probes[]` 重新算一遍，寫成 `evidence/checkpoint-cost.md`，並且把 orchestrator 先前留下的觀察筆記（`checkpoint-cost-orchestrator-notes.md`）逐條核對——結果**推翻了它一條數字**（W0-04 記成「5 輪」，實際 `review.json` 只有 4 輪掛在 `after-task:W0-04` 這個 scope 下，另外 3 輪掛在 `spec` scope，因為修 W0-04 時連帶重開了設計討論）。
- **發生了什麼**：整分支 82 個 commit、30 個純審查記錄 commit（checkpoint）、37 筆裁定分佈在 18 輪、44 個探針、82 筆派工記錄。跟 #771 的 34／31 比，這次明顯貴很多，但貴的地方主要集中在一條「要讀檔案內容判斷」的規則（關閉 commit 形狀）——18 輪裡有 7 輪是為了同一條規則設計反覆修。建議（不是決定）：下次要盯的係數不是「每個 checkpoint 幾個 commit」，是「一條要讀內容的規則吃掉幾輪」；且已經有一次「連續兩輪修不好就換更強模型設計」有效的先例（opus 一次設計評審收掉了六輪 sonnet 修不完的問題），值得下次主動用而不是等 kouko 開口才用。
- **證據**：`docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost.md`（完整表格與逐條核對）。
- **驗收**：works。

### 5. 三個 plugin 都 bump 了版號（Acceptance #5）
- **怎麼試的**：`grep version */.claude-plugin/plugin.json`；檢查各自 CHANGELOG 是否點名這次 change；檢查 root README 版本欄。
- **發生了什麼**：loom-code 1.0.1、loom-design 1.0.1、loom-workflow 4.0.1，三個 CHANGELOG 都有對應條目、README 三列版號也同步更新。
- **裝置端 `claude plugin update` 之後 cache 目錄真的長出 1.0.1**：這件事只能在 PR 合併之後做，這裡沒辦法驗，如實記為「待合併後驗」。
- **證據**：`grep version` 輸出；CHANGELOG 片段；README 第 12–14 列。
- **驗收**：works（三表面已確認）／not-yet（裝置端驗證，需等合併）。

### 6. 上一輪五個測試瑕疵清乾淨了（Acceptance #6）
- **怎麼試的**：逐一開檔核對——`loom_checker.py` 的 docstring 是否改成「above」；`test_check_mechanisms.py` 的 RED 判準是否釘死字面 `5` 並附註解、以及是否用「模組原始碼裡沒有呼叫 `wc`」取代舊的跨 locale 測試；`test_session_start_words.py` 的 `_run` 是否改成先抓 bytes 再 decode；R28-O2 的「記為不需修」是否真的寫進了 W1-02 那個 commit 的訊息和 CHANGELOG。
- **發生了什麼**：五項全部確認到位。R28-O2 的 commit 訊息裡明確寫著「R28-O2: moot -- the wc skip-guard probe was deleted by the round-30 rewrite.」，CHANGELOG 也同步記錄；整包測試（見 Acceptance #2）綠。
- **證據**：`loom_checker.py:497`「HOST_PLUMBING_DIR_PREFIX above」；`test_check_mechanisms.py` 的 `test_matches_python_split_not_bsd_wc` 與 `test_no_wc_subprocess_in_module`；`test_session_start_words.py:49` 的 bytes 解碼；`git log --format=%B -1 f6f63a10` 的完整訊息。
- **驗收**：works。

## 對你既有的資料做了什麼

沒有動到你既有的資料——這次改的是 loom 自己的規則腳本、契約文法、和它自己 repo 裡的文件；唯一動到「既有」東西的地方，是把上一個已合併的 change（2026-09-02-simple-loom-flow）的 intent 檔狀態行從 `confirmed` 改成 `closed 2026-09-03 — PR #780`，以及把 `.codex/hooks/` 底下的 Codex 副本刷新成新版號——兩者都是這個分支自己說要做、你已經確認過的動作，不是意外碰到的資料。

## 我幫你決定的事

- **關 intent 改成合併前、在分支上做（spec Design decision，這是你 2026-09-03 自己拍板的設計，不是 agent 決定）**——只是提醒：這代表如果 PR 最後沒合併，那個 closed 狀態就留在死分支上，不會有人清。
- **`push.dispatch-covers-tasks` 和 `push.review-only-head` 兩條既有規則被加嚴（你選的 A 案）**——好處是補上了「裁定的 sha 沒跟緊被推的 commit」這個既有漏洞，不只補這次的流程；代價是以後每次收尾都多一輪只讀一行的審查。
- **一項 severity=important 的發現被駁回、沒有修**：`after-task:W0-04-12` — `loom_checker.py:1883` 的 `check_close_commit_shape` 函式本體約 66 行，超過 50 行的內部上限；駁回理由是「正確性已經在六輪修正裡窮舉驗證過，此時再拆分只是不改行為的重構，會重新打開一個使用者已經喊停的 task」。如果這個理由對你來說不成立（例如你在意的是可維護性而不是正不正確），這裡就是你該回頭看的地方。
- 另外三個 severity=nit 的發現被駁回（都是措辭／註解層級，不影響行為），不逐條列，細節在 `review.json` 的 `open_findings`。
- **REQ-1 的殘留**：CI 不會跑 `push` 閘（push 閘是本機端，CI 只重算 intake／standing／contract 規則與套件測試）——這是設計上就講明的邊界，不是漏掉。
- **REQ-2 的殘留**：如果有人偽造一個從沒 fetch 過的本機 `main`／`origin/main` ref，或者用 shallow clone 加上重寫過的歷史，reopen 檢查是繞得過去的——文件裡講明這屬於「單一使用者對自己閘的操弄」同一類，不在這次修的範圍。
- **REQ-3 的殘留**：Codex 端（`.codex/hooks/` 副本本身在跑 checker 時）沒有正本可比，每次刷新都還是要 trailer；另外如果使用者自己刻意裝了舊版 plugin cache，loom 不會偵測「這比最新版舊」。

## 我不確定你要不要的事

這個分支自己還開了六個新的 open intent（其中五個在 spec 通過之後、一個在 spec 審查期間開的；審查者以 spec 通過點為基準只會數到五個），記錄它在做這次 change 時撞到、但決定不在這次修的坑。是否要排進下一輪，由你決定：

- **對抗者要不要一律先寫探針、實作者後動手**：這次一個 checkpoint（W0-04）先做後審花了 5 輪修 6 次，另一個（W0-05）先寫 11 個探針再做只花 3 輪修 2 次——同一組人、同一個 change，順序不同差很多。
- **修正輪要不要設上限、卡住就自動換更強模型**：這次兩次卡住（同一規則連續修四輪找到四種不同解析邊界；spec 審到第 8 輪）都是你或 orchestrator 手動喊停換方向，機制本身不會自動停。
- **對抗者寫的探針要不要畢業成永久測試**：現在探針只活在這次 change 的 evidence 資料夾裡，合併後沒人會再跑；這次留下 21 個探針，約一半跟實作者自己的測試重疊。
- **第二家 vendor（Codex）要不要能整個 change 關掉**：現在是 repo 層級一次決定、每輪都跑，沒有「這次先不要」的開關。
- **squash merge 後 `needs-design` 那行會不見**：分支上關那行的 commit 訊息有帶 `needs-design:` 那行，但 PR squash 合併後主幹上「最後改到那行」的 commit 變成 squash commit，它沒帶，於是主幹上每個已合併 intent 跑 `loom_checker.py intent` 都會被擋——這次關 2026-09-02-simple-loom-flow 就撞到了。
- **`templates/**` glob 誤傷 loom 自己 repo 裡的 agent 樣板**：改一行樣板的註解會被誤判成「這是使用者介面，要走 product 流程」；這次改 `templates/intent.md` 撞到過，因為只有 `intent`／`intake` 子命令會檢查、`push` 跟 CI 不會，所以這次沒被真的卡住,但下次可能會。

## 檔案清單（供你或下一個 agent核對）

- 報告本身：`docs/loom/2026-09-03-loom-post-merge-seams/blind-run-report.md`
- 成本表：`docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost.md`
- 我自己寫的見證腳本（未 commit，供覆核）：
  `/private/tmp/claude-501/-Users-kouko--herdr-worktrees-monkey-skills-simple-loom-flow/eb96f6ca-ecaf-4959-8558-75f1ce5f470b/scratchpad/witness_acceptance1.py`、
  `/private/tmp/claude-501/-Users-kouko--herdr-worktrees-monkey-skills-simple-loom-flow/eb96f6ca-ecaf-4959-8558-75f1ce5f470b/scratchpad/witness_acceptance3.py`
- 整包測試完整輸出：`/private/tmp/claude-501/-Users-kouko--herdr-worktrees-monkey-skills-simple-loom-flow/eb96f6ca-ecaf-4959-8558-75f1ce5f470b/tasks/be9wac9id.output`
