# 讓本機推送檢查單次執行完整測試 — 我試了什麼、結果如何

於 2026-09-07，在專案的乾淨副本與指定版本上驗證。

## 你逐條要求的結果

### 1. 完整 branch-end review 與使用者接受完成後，支援的本機 host hook 在實際 push transition 內執行 repository 完整測試唯一一次；成功才允許 network push，Ship 不再另外預跑同一 checker。

- **如何驗證**：把舊版與含安全修正的新版本 checker、hook 定義及完整 contract package 分別從 Git 取出，在同一個已接受 checkpoint 上執行舊版的明確 preflight 加 hook，以及新版的 hook-only 路徑；另用臨時本機 bare remote 驗證 hook 放行後真正發布的物件。
- **發生了什麼**：新版每次只由真實 hook 啟動完整測試一次並放行；舊版每次由真實 preflight 與 hook 各啟動一次。先前的反例證明 detached writer 可在 hook 回傳後移動本機 HEAD；新版沒有宣稱阻止這類後續寫入，而是以支援 shell 的標準 `command` builtin 作為 trust root，繞過 alias／function lookup 後呼叫 trusted absolute Git，再用 canonical quote-all command 綁定已驗證的完整 SHA，固定關閉隱含 tag／submodule 發布，並以 `--no-verify` 阻止 repository-configured pre-push hook 在 gate 放行後執行額外發布。
- **Evidence**：`test_revisions_execute_versioned_real_gate_entrypoints`、`test_candidate_one_call_faster_same_verdict`、`test_refspec_exacthead_accepted`、`test_gate_immutable_pinsreviewed`、`test_ship_issues_canonical_immutable_refspec_without_explicit_checker_preflight`、`test_ship_push_requires_quote_all_literal_command_and_fixed_containment_flags`、`test_ship_supported_host_hook_is_sole_package_suite_owner`、`test_ship_missing_or_inactive_supported_host_hook_blocks`；量測 probe：`2 passed in 26.58s`
- **Verdict**：works — 完整測試在最終 Ship 路徑只有 hook 這一個執行者，發布來源綁定已驗證物件且固定 flags 不發布隱含 refs；這不是 process-containment 保證。

### 2. push checker 仍從 Git 重新確認 branch-end checkpoint、reviewed commit 與 Loom 允許的 review-only／intent-close 紀錄；它只相信當次實際觀察到的完整測試 exit code，不相信 agent 寫入的歷史結果。

- **如何驗證**：用可放行、版本指向錯誤、可變或錯誤 refspec、偽造成功紀錄、額外內容修改及允許的結案紀錄逐一嘗試；每次都讓本機檢查實際執行當下命令。
- **發生了什麼**：正確 checkpoint 只有在整條命令採 canonical quote-all、以標準 `command` builtin 開頭、接著使用 trusted absolute Git、必要的 absolute `-C`、固定 flags、literal `origin`、完整目前 SHA 與完整目前 branch destination 時獲准。省略 `command`、shell expansion、命令替換、額外命令、可變或錯誤 refspec 及其他非 canonical 形式都在 suite 前被阻擋；偽造紀錄與額外內容也仍被阻擋。
- **Evidence**：`test_shell_wordsplit_rejected`、`test_shell_literal_publishesonlypinned`、`test_shell_absolutefunction_rejected`、`test_shell_commandbuiltin_publishesonlypinned`、`test_refspec_mutablesource_rejected`、`test_refspec_exacthead_accepted`、`test_a_probe_command_that_exits_one_blocks_despite_result_pass`、`test_reviewed_sha_pointing_elsewhere_is_blocked`、`test_review_only_head_with_a_third_file_is_blocked`、`test_ship_push_review_only_head_admits_close_shape`；shell-boundary suite：`90 passed in 89.23s`，change evidence：`7 passed in 19.35s`
- **Verdict**：works — 保證限於這一種 canonical invocation；它不把任意或僅語意等價的 shell command 宣稱為安全。

### 3. 這個行為不依賴程式語言、框架、副檔名或 Monkey Skills 專用的原始碼路徑，採用 Loom 且安裝支援 host hook 的其他 repository 也能使用。

- **如何驗證**：在臨時建立的獨立專案中，以該專案自己的設定和自動偵測結果執行，並讓攔截命令明確選擇另一個專案位置。
- **發生了什麼**：檢查在被選取的專案內執行；明確設定優先，缺少明確設定時可依既有標記找到命令，沒有使用語言、副檔名或專用來源目錄判斷。
- **Evidence**：`test_review_package_command_resolution_is_repository_neutral`、`test_pytest_is_detected_when_kickoff_declares_nothing`、`test_hook_mode_honours_git_dash_c_over_payload_cwd`、`test_hook_selectedrepomutation_rejected`；輸出包含於 `17 passed in 21.43s`、`8 passed, 1 warning in 0.07s`、`19 passed in 25.41s`
- **Verdict**：works — 選擇與執行都以目標專案自己的設定為準。

### 4. 完整測試命令維持既有解析結果：明確宣告優先、缺少宣告時可沿用既有偵測、完全無法解析則阻擋、明確 `none` 維持可見的免跑缺口；dirty tree、命令不可執行、逾時、中斷或非零退出都阻擋 push。

- **如何驗證**：逐一嘗試設定不一致、沒有可解析命令、明確免跑、自動偵測、找不到程式、格式錯誤、逾時、工作內容不乾淨及非零退出。
- **發生了什麼**：明確免跑與成功偵測維持原有結果；其餘不安全或無法執行的情況全部阻擋。中斷由相同的非成功退出路徑處理，未另行進行會向外送出的操作。
- **Evidence**：`test_a_package_test_probe_that_is_not_the_declared_command_blocks`、`test_a_repo_declaring_no_test_command_blocks`、`test_a_declared_none_waives_the_package_test_probe`、`test_pytest_is_detected_when_kickoff_declares_nothing`、`test_a_failing_detected_command_asks_for_a_kickoff_declaration`、`test_a_declared_command_with_shell_metacharacters_blocks`、`test_a_hung_package_tests_command_times_out_and_blocks`、`test_a_dirty_working_tree_blocks_the_probe`；輸出：`17 passed in 21.43s`
- **Verdict**：works — 可見免跑以外的無法確認情況都安全阻擋。

### 5. 完整測試失敗後，若修正會修改 tracked repository 內容，就回到 Build 並重新完成完整 branch-end review；若只修復本機環境且 Git 內容完全不變，可保留 checkpoint 並重試 push gate。

- **如何驗證**：讓測試或攻擊案例在 checker 回傳前修改已追蹤、暫存、未追蹤內容或移動版本；另重播 detached writer 在 hook 回傳後才移動 HEAD 的既知反例，並以本機 bare remote 觀察實際發布物件；最後以未變動版本連續重試兩次。
- **發生了什麼**：同步發生的內容或版本變動都被阻擋並要求回到 Build／review；完全未變動的版本可重試。舊版反例確實能在 hook 成功後改動本機 repository，所以先前「任何變動都被 gate 阻擋」的說法是錯的；最終版要求 canonical command、在 executable probes 前後核對同一 live HEAD，並用 immutable refspec 使後置變動無法取代已驗證的發布物件。
- **Evidence**：`test_push_packageheadmove_rejected`、`test_push_lastadversarymutation_rejected`、`test_push_firstadversarymutation_rejected`、`test_push_packagetrackedmutation_rejected`、`test_push_unchangedrepeat_released`、`test_gate_concurrent_reproduced`、`test_gate_immutable_pinsreviewed`
- **Verdict**：works — tracked 修正仍使 checkpoint 失效；環境修復且 Git 不變可重試；對 hook 回傳後的 detached writer，保證是「不發布未驗證 commit」，不是「阻止本機 mutation」。

### 6. 實作途中以同一個已接受 checkpoint 重播從 Ship Push step 到本機 gate 阻擋或釋放 network push 的相同範圍，記錄 baseline 與 candidate 實際完整測試次數及 monotonic 等待秒數；candidate 恰好執行一次、少於 baseline、發布 verdict 相同且實測等待下降。

- **如何驗證**：從 Git 取出兩個版本的真實 checker bundle 與 hook 定義，在同一個已接受 checkpoint 上交替執行七組；由 repository 宣告的 package command 以 monotonic clock 自行記錄每次執行時間，外層再量測直到真實 hook verdict，流程在 network transfer 前停止。
- **發生了什麼**：舊版實際走 preflight 加 hook，共執行十四次；最終新版用以 `command` 開頭且固定 `--no-verify` 的完整 canonical quote-all command 走 hook-only，共執行七次。兩者全部由真實 gate 判定放行。舊版完整邊界中位數為 2.090451084 秒，新版為 1.131370125 秒，下降 0.959080959 秒，約 45.9%。
- **Evidence**：`docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/measurement.md`、`test_revisions_execute_versioned_real_gate_entrypoints`、`test_candidate_one_call_faster_same_verdict`；輸出：`2 passed in 26.58s`
- **Verdict**：works — 固定案例的實測次數減半，判定不變且等待下降。

## Review summary

六條驗收目前都有可執行證據。detached-writer、shell expansion、executable-function shadowing 與 repository-configured pre-push hook 風險已由 `839f1884` 的 `command`-prefixed canonical immutable command 與固定 `--no-verify` 修正，量測也已重跑最終版本的真實入口；是否關閉 findings 仍由原 reviewer 在本輪複查決定。英文規則稽核另有一項不影響執行的文字一致性問題。

| 可讀標籤 | 英文規則結果 | Evidence |
|---|---|---|
| 計畫 | 部分符合；工作拆分與風險為英文，逐字保留的使用者問題為繁體中文 | `docs/loom/2026-09-06-reuse-branch-end-suite-result/plan.md:33` |
| 規格 | 部分符合；需求與設計決定為英文，操作流程為繁體中文；七條需求皆使用規定格式 | `docs/loom/2026-09-06-reuse-branch-end-suite-result/spec.md:7`、`docs/loom/2026-09-06-reuse-branch-end-suite-result/spec.md:58`、`REQ-1`–`REQ-7` |
| 審查發現 | 符合；文字為英文且以允許的評論標籤開頭 | `review.json` 的 findings |
| 驗證證據 | 符合；量測說明、程式說明與案例說明皆為英文 | `docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/measurement.md`、`docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py`、`docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_branch_end_shell_boundary.py`、`docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_w002_mutation_boundary.py` |
| 測試名稱 | 符合；新增案例均使用三段式名稱 | 對 `git diff --unified=0 4e158201 -- '*.py'` 的新增行套用 `^+def (test_[A-Za-z0-9_]+)\(`：65 個 test definitions、50 個 unique names；15 個重複名稱來自 evidence probe 與 graduated probe 的成對案例 |
| 提交訊息 | 符合；本次變更的 commit subjects 為英文 | `git log --format='%h%x09%s' 4e158201..HEAD` |

非阻擋發現：規格的操作流程不是英文。本輪不修改已確認的 `spec.md`，以免改變使用者已確認的 fingerprint；此 nit 留待 checkpoint 流程處理。

## 對你既有的資料做了什麼

驗證只在乾淨副本與臨時建立的專案中讀取既有版本與設定，沒有接觸或遷移你的個人資料，也沒有向外部或 network remote 推送。shell-boundary 與 immutable-source 攻擊案例會把 synthetic commit 推到臨時本機 bare remote。checker 回傳前發生的 repository mutation 會阻擋；detached writer 若在回傳後才動作，仍可能改變本機內容，但標準 `command` builtin 會先繞過 alias／function lookup，canonical command 綁定的已驗證 SHA 不會被替換成發布來源，固定 flags 不會帶出隱含 tag、submodule refs，也不會執行 repository-configured pre-push hook。流程不替你復原或備份這類本機變動，原有檔案格式沒有改變。

## 我替你決定的事

- **完整測試放在哪裡執行** — 我選擇讓阻擋推送的本機檢查直接執行，因為只有它能當場相信退出結果。日後改成沿用歷史結果，需要新增可信的證明機制。
- **如何找出完整測試命令** — 我保留原有順序：明確設定優先，否則沿用既有偵測；完全沒有命令就阻擋，明確免跑則保留可見缺口。日後改變順序會影響採用此流程的專案。
- **是否要求支援的本機攔截** — 我選擇要求它存在且已啟用，因為手動推送無法提供相同保證。改成允許手動推送會降低發布前的保護。
- **何時執行唯一一次完整測試** — 我選擇在所有可能改動專案內容的審查工作完成後才執行，只保留既有、可機械驗證的結案紀錄。放寬後會需要重新定義哪些修改不會使審查失效。
- **在哪個專案內確認狀態** — 我選擇以被攔截命令指定的專案為準，並在執行前後比較版本與乾淨狀態。若省略後置比較，成功退出的程式仍可能偷改待發布內容。
- **是否保留攻擊案例的重跑** — 我選擇保留，因為這次只移除重複的完整測試。日後取消會降低現有的邊界保護。
- **被審查者駁回的重要發現** — 沒有；紀錄中所有重要或致命發現都標示為已修正，沒有任何 dismissed 項目。

## 我不確定你是否還想要的事

沒有。
