# 讓 push gate 先擋下不需執行測試的失敗 — 實際嘗試結果

於 2026-09-07 在專案的全新乾淨副本、版本 `537eebe7abb16211eab7c71ff09bed838bd7eff1` 上重新嘗試。依專案文件使用鎖定依賴的隔離環境；只執行本報告列明的行為檢查，完整 package suite 留給本機 push hook 執行。

## 你要求的每一項結果

### 1. 任一既有 deterministic preflight 條件失敗時，push gate 會阻擋且不啟動 package suite 或 adversarial probe；這包含 Task trailer、dispatch coverage、verdict、第二位讀者、frozen store、reviewer independence 與 finding closure 等後段條件。
- **如何嘗試**：建立一個真實的暫存 Git repository，刻意讓既有的角色獨立性條件失敗，並讓完整測試與三個攻擊探針在啟動時留下紀錄。
- **發生什麼**：檢查器以既有規則阻擋；執行紀錄保持空白，完整測試與攻擊探針都沒有啟動。
- **證據**：`test_push_lateblocker_noexecutables`，本次指定測試執行中通過。
- **判定**：works — 已知的 deterministic 阻擋發生在外部程式之前。

另重新觸發兩次版本讀取之間的 HEAD 移動，確認沒有外部程式啟動；`test_push_liveheadrace_noexecutables` 通過。既有的錯誤彙整、缺少任務紀錄與讀者不足三個整合案例也通過：`test_every_failure_is_reported_not_just_the_first`、`test_probes_extra_file_change_between_probe_and_head_still_blocks`、`test_push_gateonly_missing_package_tests_probe_still_blocked`。本次沒有逐一重建所有規則的每種失敗輸入。

### 2. 所有 preflight 條件通過時，push gate 仍執行既有解析出的完整 package suite 恰好一次，並執行既有 adversarial probes；兩者成功且 repository 未改變時才允許 push。
- **如何嘗試**：建立所有 preflight 都有效的真實暫存 Git repository，讓每個外部程式把自己的啟動順序寫入 Git 內部紀錄，再執行檢查器。
- **發生什麼**：檢查器允許繼續；紀錄依序只有一次完整測試，接著三個攻擊探針各一次。
- **證據**：`test_push_validpath_onceinorder`，本次指定測試執行中通過。
- **判定**：works — 成功路徑保留完整執行，且沒有重複執行。

### 3. package suite 或 adversarial probe 失敗、移動 HEAD 或改變 working tree 時，push gate 仍以既有 BLOCK 規則拒絕 push。
- **如何嘗試**：讓完整測試以非零狀態結束，同時改變所選 repository 的有效 Git 設定；之後觀察檢查器是否仍執行攻擊探針並回報原有阻擋。
- **發生什麼**：完整測試失敗與 repository 改變兩項阻擋都被保留，push 被拒絕；三個攻擊探針仍依序執行。
- **證據**：`test_push_failedmutation_blockpreserved`，本次指定測試執行中通過。
- **判定**：works — 外部程式失敗與 repository mutation 仍採 fail-closed。

另外實際執行完整測試移動 HEAD、改寫追蹤檔案，以及攻擊程式改動追蹤檔案、暫存區、未追蹤檔案、HEAD 和啟動另一個寫入程序的情境，全部被拒絕。證據：`test_push_packageheadmove_rejected`、`test_push_packagetrackedmutation_rejected`、`test_push_firstadversarymutation_rejected`、`test_push_lastadversarymutation_rejected` 的五個情境全部通過。分別讓完整測試與攻擊程式以非零狀態結束的兩個案例也通過：`test_a_probe_command_that_exits_one_blocks_despite_result_pass`、`test_an_adversarial_probe_that_no_longer_passes_does_not_count`。

### 4. 這項短路行為不依賴程式語言、框架、檔案副檔名或 Monkey Skills 專用路徑，其他採用 Loom 的 repository 可直接使用。
- **如何嘗試**：在通用暫存 Git repository 中，分別將應用程式來源命名為 TypeScript 與 SQL 檔案；每種名稱各試有效紀錄與角色衝突兩種情況，觀察 repository 自己宣告的外部命令。
- **發生什麼**：兩種有效情況都只執行一次完整命令與三個攻擊程式；兩種角色衝突情況都沒有啟動外部程式。檢查器自身仍需要 Python，這不限制採用專案的應用程式語言。
- **證據**：直接執行四個暫存 repository 情境；`application.ts` 與 `model.sql` 均得到有效時 `rc=0` 且順序為 `package, adversarial-1, adversarial-2, adversarial-3`，角色衝突時 `rc=1` 且 `execution=[]`。永久測試模組的 `test_push_lateblocker_noexecutables` 與 `test_push_validpath_onceinorder` 也使用通用 repository。
- **判定**：works — phase boundary 由既有規則結果與命令紀錄控制，而非採用 repository 的技術棧或路徑命名。

## Review summary

- 四項 Acceptance 的上述行為都在精確版本的乾淨副本中通過；18 個指定測試與 4 個直接建立 repository 的情境成功。
- 先前讀者發現的版本競態已修正，本次重新觸發該競態，確認沒有外部程式啟動。
- 本次沒有發現新的功能問題；先前非阻擋建議仍保留於 review，並未宣稱全部已修正。
- 完整 package suite 未由這次盲跑執行；此份結果只涵蓋列明的行為，不是完整 suite 已通過的證明。

## Questions I asked you

- 「這次要不要用 Claude 當第二位讀者？」— 你選擇使用 Claude。
- Review 另記錄了「你接受這份第一階段結果，讓我繼續處理 nit batch、最終 push gate 與 PR 準備嗎？」；本次盲跑沒有新增問題，也不推定新的授權。

## 對你既有的資料做了什麼

沒有改動既有業務資料。盲跑讀取本次分支，所有破壞性情境只作用於新建的暫存 repository；來源 worktree 只更新這份報告。採用這項變更後，有效 push 仍執行 repository 原先宣告的測試與攻擊程式，並在它們改動資料時拒絕 push；檢查器不負責還原那些程式的改動。

## 我替你決定的事

- **先完成所有不執行外部程式的檢查，再設一個統一的提前返回點** — 我選擇單一 phase boundary，因為它能保留累積回報並避免分散條件。日後改成逐項短路會增加控制流程與測試成本。
- **保留完整測試先、攻擊探針後的順序，最後只做一次 repository 狀態複查** — 我選擇維持現有安全覆蓋，因為本次只移除已知阻擋後的浪費。日後改順序需要重新確認失敗與 mutation 的語意。
- **把要求 live HEAD 的檢查放在外部程式之前** — 我選擇把它視為不執行不受信任程式即可判斷的 preflight。日後移回去會再次支付可避免的外部程式成本。
- **保留既有錯誤文字與規則名稱** — 我選擇讓既有使用者與自動化仍能辨識相同阻擋。日後改名需要同步更新相依的檢查與操作文件。
- **遇到 deterministic 失敗時仍累積完整回報** — 我沒有改成第一項錯誤就停止，因為完整回報可減少反覆修正。改成 fail-fast 會縮短單次輸出，但可能增加重跑次數。
- **執行前再次核對實際版本** — 先前較早的檢查不足以阻止兩次讀取之間的版本移動；保留最後一次核對會增加一次便宜的版本讀取。
- **只把可重用案例加入永久測試，不新增重複的記憶條目** — 既有條目已記錄同一教訓；日後若出現新的教訓，再另行記錄。
- 沒有重要或更嚴重的 finding 被撤銷；先前阻擋問題以修正及測試證據結案。

## 英文規則檢查

| 使用者可讀的項目 | 結果 | 證據 |
|---|---|---|
| 計畫 | 符合英文規則；固定模板另要求任務、測試與風險欄位 | `docs/loom/2026-09-07-push-gate-cheap-checks-first/plan.md` |
| 規格 | 符合英文規則；固定模板另以 EARS 需求句型約束每項可見行為 | `docs/loom/2026-09-07-push-gate-cheap-checks-first/spec.md`、`REQ-1` 至 `REQ-4` |
| Review 記錄的 findings | 英文，且以固定模板要求的 Conventional Comments 標籤開頭；目前有歷史 findings，並非空白 | `review.json`、`issue`、`nitpick` |
| 證據 | 符合英文規則 | `docs/loom/2026-09-07-push-gate-cheap-checks-first/evidence/probes/test_push_preflight_before_executables.py` |
| 測試說明 | 符合英文規則 | `test_push_lateblocker_noexecutables`、`test_push_validpath_onceinorder`、`test_push_packageskip_adversarialruns`、`test_push_failedmutation_blockpreserved` 的 docstring |
| 測試名稱 | 符合 `test_<unit>_<state>_<expected>` 的固定命名規則 | 同上四個測試名稱 |
| Commit messages | 主旨英文；最初 intent commit 的 body 含一行中文原文，因此不是全部字句皆英文 | `7d1ec6a6`、`needs-design`；檢查至 `537eebe7` |

## 我不確定你是否想要的事

沒有。
