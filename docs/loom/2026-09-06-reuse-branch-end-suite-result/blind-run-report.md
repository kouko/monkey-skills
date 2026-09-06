# 讓本機推送檢查單次執行完整測試 — 我試了什麼、結果如何

於 2026-09-07，在專案的乾淨副本與指定版本上驗證。

## 你逐條要求的結果

### 1. 完整 branch-end review 與使用者接受完成後，支援的本機 host hook 在實際 push transition 內執行 repository 完整測試唯一一次；成功才允許 network push，Ship 不再另外預跑同一 checker。

- **如何驗證**：從發布動作開始重播同一個已接受版本，分別觀察舊流程與新流程實際啟動完整測試的次數；另外確認發布動作不再先行執行同一檢查，且缺少支援的本機攔截時會停止。
- **發生了什麼**：新流程的七次樣本每次都只啟動一次完整測試並作出放行決定；舊流程每次啟動兩次。發布流程沒有額外預跑，缺少或未啟用本機攔截時會阻擋。
- **Evidence**：`test_revisions_observe_different_execution_owners`、`test_candidate_one_call_faster_same_verdict`、`test_ship_issues_named_branch_without_explicit_checker_preflight`、`test_ship_supported_host_hook_is_sole_package_suite_owner`、`test_ship_missing_or_inactive_supported_host_hook_blocks`；輸出：`2 passed in 2.59s`、`8 passed, 1 warning in 0.07s`
- **Verdict**：works — 完整測試只有本機推送檢查這一個執行者。

### 2. push checker 仍從 Git 重新確認 branch-end checkpoint、reviewed commit 與 Loom 允許的 review-only／intent-close 紀錄；它只相信當次實際觀察到的完整測試 exit code，不相信 agent 寫入的歷史結果。

- **如何驗證**：用可放行、版本指向錯誤、偽造成功紀錄、額外內容修改及允許的結案紀錄逐一嘗試；每次都讓本機檢查實際執行當下命令。
- **發生了什麼**：正確且未變動的版本獲准；錯誤版本、偽造紀錄與額外內容都被阻擋；既有的純結案紀錄仍可通過。歷史上寫成成功但當次退出失敗的案例被阻擋。
- **Evidence**：`test_a_probe_command_that_exits_one_blocks_despite_result_pass`、`test_reviewed_sha_pointing_elsewhere_is_blocked`、`test_review_only_head_with_branch_form_status_line_passes`、`test_review_only_head_with_a_third_file_is_blocked`、`test_ship_push_review_only_head_admits_close_shape`；輸出包含於 `17 passed in 21.43s` 與 `8 passed, 1 warning in 0.07s`
- **Verdict**：works — 放行依據是當次觀察與版本內容，不是先前寫下的結果。

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

- **如何驗證**：讓測試或最後一個攻擊案例在成功退出前修改已追蹤、暫存、未追蹤內容或移動版本，再以完全未變動的同一版本連續重試兩次。
- **發生了什麼**：任何內容或版本變動都被阻擋並指示重新完成製作與審查；完全未變動的版本可連續重試並獲准，沒有消耗一次性憑證。
- **Evidence**：`test_push_packageheadmove_rejected`、`test_push_lastadversarymutation_rejected`、`test_push_firstadversarymutation_rejected`、`test_push_packagetrackedmutation_rejected`、`test_push_unchangedrepeat_released`、`test_push_existingguard_preserved`；輸出：`19 passed in 25.41s`
- **Verdict**：works — 是否需要重做審查由版本內容有沒有改變決定。

### 6. 實作途中以同一個已接受 checkpoint 重播從 Ship Push step 到本機 gate 阻擋或釋放 network push 的相同範圍，記錄 baseline 與 candidate 實際完整測試次數及 monotonic 等待秒數；candidate 恰好執行一次、少於 baseline、發布 verdict 相同且實測等待下降。

- **如何驗證**：對相同固定案例交替執行七組舊版與新版重播，以單調時鐘量測完整邊界，並以實際追加紀錄計算呼叫次數；流程在可能向外傳送前停止。
- **發生了什麼**：舊版共執行十四次，新版共執行七次；每組是二次對一次，兩者全部判定放行。舊版等待中位數為 0.240689416 秒，新版為 0.138872000 秒，下降 0.101817416 秒，約 42.3%。
- **Evidence**：`docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/measurement.md`、`test_candidate_one_call_faster_same_verdict`；輸出：`2 passed in 2.59s`
- **Verdict**：works — 固定案例的實測次數減半，判定不變且等待下降。

## Review summary

六條驗收全部可重現。功能上沒有阻擋或重要問題；英文規則稽核發現一項不影響執行的文字一致性問題。

| 可讀標籤 | 英文規則結果 | Evidence |
|---|---|---|
| 計畫 | 部分符合；工作拆分與風險為英文，逐字保留的使用者問題為繁體中文 | `docs/loom/2026-09-06-reuse-branch-end-suite-result/plan.md:33` |
| 規格 | 部分符合；需求與設計決定為英文，操作流程為繁體中文；七條需求皆使用規定格式 | `docs/loom/2026-09-06-reuse-branch-end-suite-result/spec.md:7`、`docs/loom/2026-09-06-reuse-branch-end-suite-result/spec.md:58`、`REQ-1`–`REQ-7` |
| 審查發現 | 符合；文字為英文且皆以允許的評論標籤開頭 | `review.json` 的八項 findings；標籤皆為 `issue (blocking)` |
| 驗證證據 | 符合；量測說明、程式說明與案例說明皆為英文 | `docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/measurement.md`、`docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py`、`docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_w002_mutation_boundary.py` |
| 測試名稱 | 符合；新增案例均使用三段式名稱 | `test_<unit>_<state>_<expected>`；32 個新增名稱經結構檢查皆符合 |
| 提交訊息 | 符合；本次變更的 27 則提交訊息皆為英文 | `git log --format='%h%x09%s' 4e158201..2591f9dd` |

非阻擋發現：規格的操作流程不是英文。若要完全符合規則，將該段翻成英文，同時保留已確認的行為不變。

## 對你既有的資料做了什麼

驗證只在乾淨副本與臨時建立的專案中讀取既有版本與設定，沒有接觸或遷移你的個人資料，也沒有發出真正的推送。若完整測試在實際使用時改動專案內容，檢查會阻擋推送但不替你復原，因此沒有自動備份；原有檔案格式沒有改變。

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
