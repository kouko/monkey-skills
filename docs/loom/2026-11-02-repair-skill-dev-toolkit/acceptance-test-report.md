Tried on 2026-11-24, in a clean copy of the project at c8d6de0ad7357a50da276d7b92b7fc3a7deb7a. 逐項操作與結果：`docs/loom/2026-11-02-repair-skill-dev-toolkit/evidence/acceptance-test-evidence.md`。

# 分批修復 skill-dev-toolkit 已確認的缺陷 — 驗收測試報告

本報告以乾淨副本在 HEAD (c8d6de0ad) 上逐條走訪 11 項驗收準則，並檢視 W18 原生重播與兩份獨立盲審的存證。工具包 228 項測試、4 項隱藏描述標準測試、技能結構檢查、共用慣例漂移檢查、Codex 清單漂移檢查、以及倉庫級 715 項測試全部通過。W18 重播排除了預登記的過寬主張 (read-1.json F1)，確認了真正衝突 (simulate-1.json F1)，但 run-2 在 read-1.json F2 與 simulate-1.json F3 上產生不被來源支持的確認，且三次重播在這兩項候選上互相矛盾；先前 Claude 宿主失敗未經證實修復，完整宿主可用性仍未驗證。

## 你要求的結果，一條一條看

| # | 你要求的結果 | 判定 | 實際結果 | Re-run |
|---|---|---|---|---|
| 1 | 既有技能打包、評估彙整與描述優化入口可完成其已宣告的職責，不再因入口內容無法解析而中斷。 | works | 以宣告的 PYTHONPATH 前綴與絕對腳本路徑執行 `package_skill.py`、`aggregate_benchmark.py`、`run_loop.py` 三個入口，打包與彙整在乾淨副本完成；run_loop 需外部後端（離線測試以 mock 涵蓋）。 | carried over — fix only edits intent pin line; no Acceptance wording, code, test, or evidence changed |
| 2 | 結構等價檢查能拒絕不符合既定呼叫順序的結果，同時保留已定義的合法容許差異。 | works | `equivalence_check.py` 強制相同長度追蹤完全相同，長度差 ≤1 時允許刪除較長方的一個呼叫；14 項順序測試全部通過。 | carried over — fix only edits intent pin line; no Acceptance wording, code, test, or evidence changed |
| 3 | 盲測的截短顯示及選擇前全文檢視不會從工具附加資訊洩漏版本身分，選擇仍對應原來的盲標籤。 | works | `test_blind_harness.py` 涵蓋截短路徑、全文檔案、標籤鎖定與無效輸入的互動；無身分洩漏。 | carried over — fix only edits intent pin line; no Acceptance wording, code, test, or evidence changed |
| 4 | 有效的原始版本偏好可正確匯出；有效紀錄、衍生比較資料與準備條件的計數定義一致。 | works | `test_preference_export.py` 驗證 ADOPT/DROP 明確基準、可用單選 1000 筆門檻、配對計數與就緒度計數分離；計數定義一致。 | carried over — fix only edits intent pin line; no Acceptance wording, code, test, or evidence changed |
| 5 | 獨立複核保留的八項規則衝突或資訊不足已消除，同一適用情境不再產生相反要求。 | works | 獨立複核把原 20+ 項縮減到 8 項權威衝突，W18 重播與雙審均以逐條來源對照確認：read F1 過寬被排除、simulate F1 真實衝突被確認、其餘六項在各自來源範圍內可調和。 | carried over — fix only edits intent pin line; no Acceptance wording, code, test, or evidence changed |
| 6 | 大小警示與報告宣告的驗證範圍相符，保留既有分組政策並正確表達證據限制。 | works | 規劃器維持 30000 分組門檻、25000 名義提示界線；`test_plan_groups.py` 驗證約 25k 語料體的分組行為與警示輸出一致。 | carried over — fix only edits intent pin line; no Acceptance wording, code, test, or evidence changed |
| 7 | 驗證能實際檢出本次已確認的缺陷；過時的文件位置檢查不再取代行為檢查，相關套件與既有倉庫檢查通過。 | works | 工具包 228 測試 + 4 隱藏描述測試 + 技能結構檢查 (6 技能 PASS) + 共用慣例漂移 (0 失敗) + Codex 清單漂移 (0 失敗) + 倉庫級 715 測試全部通過；對抗程式併入工具包 CI 路徑。 | carried over — fix only edits intent pin line; suite re-ran at new HEAD and passed 715 |
| 8 | 新技能的建立及打包遵守同一套既有描述規則；不合格描述不能以有效封裝交付，合格的例外仍受支援。 | works | `package_skill.py` 呼叫 `quick_validate.py` 內含脈絡防護，268 字不合格描述被拒、含 `# KEEP:` / `# Role:` / `# Firing evidence:` 的合格例外通過封裝。 | carried over — fix only edits intent pin line; no Acceptance wording, code, test, or evidence changed |
| 9 | 在已確認的真實案例中，矛盾檢查不把明文例外當成衝突，報告也不把未觀測的模型身分寫成已驗證。 | partly | W18 重播正確排除 read F1 (把 `prose` 視為創作/非確定性類別的括號範例而非獨立觸發)、正確確認 simulate F1 (創作類別的真實衝突)；但 run-2 在 read F2、simulate F3 產生來源不支持的確認，兩審皆判定為語意缺陷，且三次重播在這兩項互相矛盾。報告誠實記載 `actual_backend_identity: not exposed in exec JSONL`，未宣稱模型身分已驗證。 | carried over — full re-test completed at prior re-run (HEAD 2a6f311cd); this fix edits only the intent pin line, no Acceptance wording, W18 evidence, code, or test changed |
| 10 | 首次使用及缺少歷史測例、模型身分或執行量測時，有可遵循的處理方式，不臆造必要輸入或測量結果。 | works | 缺 token 以 null 表達、缺時長停止比較並揭露限制、缺歷史案例以現有 setup 準備代表性案例與舊版基線、不支援模型時僅停用即時優化保留草稿準備；各分支均有測試覆蓋。 | carried over — fix only edits intent pin line; no Acceptance wording, code, test, or evidence changed |
| 11 | 代表性真實宿主流程可完成且產物符合其已宣告要求，能支持正確的修改或不修改決定；已確認的過寬主張誤報須在既有失敗案例中排除，同時保留真正衝突。原始失敗及尚未驗證的環境、模型與流程限制完整保留，不以提示文字或單純完成執行替代結果品質。 | partly | W18 排除預登記過寬 F1、確認真實衝突 simulate F1，達到否決條件「未重現同類過寬確認」；但 run-2 引入 read F2、simulate F3 的不受支持確認與跨輪不一致，先前 Claude 宿主失敗未證實修復，完整宿主可用性未驗證。所有已知限制（模型身分未觀測、原生成功≠Claude 修復、W15–W17 計數保留、無安裝/發布/合併授權）完整保留於紀錄。 | carried over — full re-test completed at prior re-run (HEAD 2a6f311cd); this fix edits only the intent pin line, no Acceptance wording, W18 evidence, code, or test changed |

## 對你既有的資料做了什麼

本次變更只讀取既有來源、原始候選與重播結果，產生測試輸出與更新驗收文件；沒有修改原始失敗紀錄、使用者偏好、目標技能或已安裝插件。歷史預覽報告另存原樣快照，其通過僅屬當時預覽承諾，非現行實際可用要求的通過。

## 我代你決定了什麼

- **保留爭議** — read-1.json F2 與 simulate-1.json F3 的確認/排除方向仍有跨輪不一致與兩份獨立審核判定為語意缺陷的記錄；狀態不視為固定正解，後續變更仍需核對原主張與適用條件。
- **驗證界線** — 使用既有 Python 執行乾淨原始碼副本，不安裝；這只能證明本機命令可載入與程式檢查通過，不能證明安裝後觸發行為或 Claude 判斷品質。
- **不宣告接受完成** — 程式檢查成功不替代實際品質，先前失敗、費用、輪次均保留。沒有被主代理駁回的重要發現。
- **保留獨立異議** — 第二份審核對 run-3 狀態的誤讀、第一份審核對較窄範圍的支持不足以解除完整範圍疑慮，兩份原判斷與 synthesis 的不一致均保留。
- **不宣稱模型身分** — 重播請求 `gpt-6.1-sol` 但執行器未觀測到實際後端身分，決策檔記載 `actual_backend_identity: not exposed in exec JSONL`，未推斷或認證。

## 你指示跳過的步驟

- **獨立外部代碼審查** — 2026-11-07 確認的意圖與 2026-11-24 授權均明確排除；intent Constraints 第 29、33、36、43、46 條。
- **完整付費宿主測試套件** — 僅授權三次 W18 原生重播 (US$2.4146)，無新增付費測試、換模型或自動重試；intent Constraints 第 29、33 條。
- **安裝、發布或合併** — 全部授權條款明確列為 out-of-scope；intent Constraints 第 29、31、32、33、36、43、46 條。

## 尚不確定你是否想要的事

- 完整宿主品質與先前 Claude 失敗是否修復：目前不能視為可發布，W18 重播文件與雙審 synthesis 已誠實揭露 run-2 的不受支持確認、跨輪不一致、模型身分未觀測、原生成功不等於 Claude 修復。
- 是否要針對 run-2 的 read F2 / simulate F3 不穩定再迭代修補：此決策屬變更擁有者，本驗收不預設方向。