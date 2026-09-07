# 讓 push gate 先擋下不需執行測試的失敗 — 實際嘗試結果

於 2026-09-07 在專案的乾淨副本、版本 `80b9bd06` 上嘗試。

## 你要求的每一項結果

### 1. 任一既有 deterministic preflight 條件失敗時，push gate 會阻擋且不啟動 package suite 或 adversarial probe；這包含 Task trailer、dispatch coverage、verdict、第二位讀者、frozen store、reviewer independence 與 finding closure 等後段條件。
- **如何嘗試**：建立一個真實的暫存 Git repository，刻意讓既有的角色獨立性條件失敗，並讓完整測試與三個攻擊探針在啟動時留下紀錄。
- **發生什麼**：檢查器以既有規則阻擋；執行紀錄保持空白，完整測試與攻擊探針都沒有啟動。
- **證據**：`uv run --isolated --with-requirements requirements-package-tests.lock python -m pytest loom-code/scripts/test_push_preflight_before_executables.py::test_push_lateblocker_noexecutables -vv`；`test_push_lateblocker_noexecutables`，1 passed。
- **判定**：works — 已知的 deterministic 阻擋發生在外部程式之前。

### 2. 所有 preflight 條件通過時，push gate 仍執行既有解析出的完整 package suite 恰好一次，並執行既有 adversarial probes；兩者成功且 repository 未改變時才允許 push。
- **如何嘗試**：建立所有 preflight 都有效的真實暫存 Git repository，讓每個外部程式把自己的啟動順序寫入 Git 內部紀錄，再執行檢查器。
- **發生什麼**：檢查器允許繼續；紀錄依序只有一次完整測試，接著三個攻擊探針各一次。
- **證據**：`uv run --isolated --with-requirements requirements-package-tests.lock python -m pytest loom-code/scripts/test_push_preflight_before_executables.py::test_push_validpath_onceinorder -vv`；`test_push_validpath_onceinorder`，1 passed。
- **判定**：works — 成功路徑保留完整執行，且沒有重複執行。

### 3. package suite 或 adversarial probe 失敗、移動 HEAD 或改變 working tree 時，push gate 仍以既有 BLOCK 規則拒絕 push。
- **如何嘗試**：讓完整測試以非零狀態結束，同時改變所選 repository 的有效 Git 設定；之後觀察檢查器是否仍執行攻擊探針並回報原有阻擋。
- **發生什麼**：完整測試失敗與 repository 改變兩項阻擋都被保留，push 被拒絕；三個攻擊探針仍依序執行。
- **證據**：`uv run --isolated --with-requirements requirements-package-tests.lock python -m pytest loom-code/scripts/test_push_preflight_before_executables.py::test_push_failedmutation_blockpreserved -vv`；`test_push_failedmutation_blockpreserved`，1 passed。
- **判定**：works — 外部程式失敗與 repository mutation 仍採 fail-closed。

### 4. 這項短路行為不依賴程式語言、框架、檔案副檔名或 Monkey Skills 專用路徑，其他採用 Loom 的 repository 可直接使用。
- **如何嘗試**：在測試動態建立的通用 Git repository 中，使用 repository 自己宣告的 Python 命令作為可觀察的外部程式；另外走既有的明確略過完整測試分支，確認短路邊界不會綁死某種專案檔案分類。
- **發生什麼**：明確略過完整測試時，檢查器仍依 repository 的既有紀錄執行三個攻擊探針；行為由檢查結果與既有命令紀錄決定，沒有要求應用程式來源檔案、框架或副檔名。
- **證據**：`uv run --isolated --with-requirements requirements-package-tests.lock python -m pytest loom-code/scripts/test_push_preflight_before_executables.py::test_push_packageskip_adversarialruns -vv`；`test_push_packageskip_adversarialruns`，1 passed；同一永久測試模組的 `test_push_lateblocker_noexecutables` 與 `test_push_validpath_onceinorder` 也使用動態建立的通用 repository。
- **判定**：works — phase boundary 由既有規則結果與命令紀錄控制，而非採用 repository 的技術棧或路徑命名。

## Review summary

- 四項 Acceptance 都在精確版本的乾淨副本中以真實 checker 行為通過。
- 首次以系統 Python 執行時缺少 pytest；依專案文件改用鎖定依賴的隔離環境後，四個永久測試各自為 1 passed。
- 沒有發現需要修正的功能問題。
- 先前的非阻擋品質建議仍成立：記錄 memory dispatch 的 commit body 較著重描述執行順序，沒有同樣清楚地說明為什麼需要該順序；這不影響本次 Acceptance 結果。

## Questions I asked you

- 「這次要不要用 Claude 當第二位讀者？」— 你選擇使用 Claude。

## 對你既有的資料做了什麼

沒有。盲跑只使用這項變更所建立的乾淨副本與測試自行建立的暫存 repository；你原本的 checkout、未追蹤資料與其他 worktree 都未被讀寫或改動。

## 我替你決定的事

- **先完成所有不執行外部程式的檢查，再設一個統一的提前返回點** — 我選擇單一 phase boundary，因為它能保留累積回報並避免分散條件。日後改成逐項短路會增加控制流程與測試成本。
- **保留完整測試先、攻擊探針後的順序，最後只做一次 repository 狀態複查** — 我選擇維持現有安全覆蓋，因為本次只移除已知阻擋後的浪費。日後改順序需要重新確認失敗與 mutation 的語意。
- **把要求 live HEAD 的檢查放在外部程式之前** — 我選擇把它視為不執行不受信任程式即可判斷的 preflight。日後移回去會再次支付可避免的外部程式成本。
- **保留既有錯誤文字與規則名稱** — 我選擇讓既有使用者與自動化仍能辨識相同阻擋。日後改名需要同步更新相依的檢查與操作文件。
- **遇到 deterministic 失敗時仍累積完整回報** — 我沒有改成第一項錯誤就停止，因為完整回報可減少反覆修正。改成 fail-fast 會縮短單次輸出，但可能增加重跑次數。

## 英文規則檢查

| 使用者可讀的項目 | 結果 | 證據 |
|---|---|---|
| 計畫 | 符合英文規則；固定模板另要求任務、測試與風險欄位 | `docs/loom/2026-09-07-push-gate-cheap-checks-first/plan.md` |
| 規格 | 符合英文規則；固定模板另以 EARS 需求句型約束每項可見行為 | `docs/loom/2026-09-07-push-gate-cheap-checks-first/spec.md`、`REQ-1` 至 `REQ-4` |
| Review 記錄的 findings | 目前沒有 finding 文字可檢查；若新增，固定模板要求 Conventional Comments 標籤 | `docs/loom/2026-09-07-push-gate-cheap-checks-first/review.json`、`open_findings: []` |
| 證據 | 符合英文規則 | `docs/loom/2026-09-07-push-gate-cheap-checks-first/evidence/probes/test_push_preflight_before_executables.py` |
| 測試說明 | 符合英文規則 | `test_push_lateblocker_noexecutables`、`test_push_validpath_onceinorder`、`test_push_packageskip_adversarialruns`、`test_push_failedmutation_blockpreserved` 的 docstring |
| 測試名稱 | 符合 `test_<unit>_<state>_<expected>` 的固定命名規則 | 同上四個測試名稱 |
| Commit messages | 符合英文規則 | `7d1ec6a6..80b9bd06` 的 commit subject 與 body |

## 我不確定你是否想要的事

沒有。
