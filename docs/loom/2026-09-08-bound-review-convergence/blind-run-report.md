# 限制審查收斂輪數 — 實測結果

2026-09-08 以四個全新 Claude Code 工作階段測試。

## 你要求的內容

### 1. 每次變更最多三輪，不可換執行者重置
- **如何測試**：第三輪失敗後，提供另一個模型、vendor、app 與 task。
- **發生結果**：判定不得重置，仍以未收斂結束。
- **證據**：Claude Code 原始回覆為 `reset_allowed: false`。
- **判定**：works

### 2. 第一輪完整審查、第二輪修正、第三輪是重新設計後的終局驗證
- **如何測試**：第二輪讓相同 blocker 再次出現，且數量沒有下降。
- **發生結果**：先停止局部補丁，由 agent 重看技術設計，再進入終局第三輪。
- **證據**：Claude Code 原始回覆指定 `decision_owner: agent` 並要求先重新設計。
- **判定**：works

### 3. 暫時性或格式錯誤只重試一次，而且不增加 round
- **如何測試**：同一內容的 reviewer 連續兩次都未產生合格 verdict。
- **發生結果**：以執行失敗結束，不增加 round，也不再重試。
- **證據**：Claude Code 原始回覆為 `EXECUTION_FAILED`、`extra_round_consumed: false`。
- **判定**：works

### 4. 第二輪就辨識沒有進展
- **如何測試**：兩個 blocker 原封不動保留，blocker 數也沒有下降。
- **發生結果**：辨識為 stuck，停止相同形狀的修補。
- **證據**：Claude Code 原始回覆為 `stuck: true`。
- **判定**：works

### 5. 第三輪仍有 blocker 時，不提供第四輪
- **如何測試**：重新設計後的第三輪回傳合格的 `NEEDS_REVISION`。
- **發生結果**：以 `NON_CONVERGENT` 結束；不開第四輪，也不問使用者要不要繼續。
- **證據**：Claude Code 原始回覆為 `dispatch_round_4: false`、`ask_user_to_continue: false`。
- **判定**：works

### 6. 技術方案由 agent 決定，產品承諾改變才問使用者
- **如何測試**：明確設定需求、可見行為與保證都不需改變。
- **發生結果**：agent 自行選擇重新設計，不把技術決定丟給使用者。
- **證據**：Claude Code 原始回覆為 `decision_owner: agent`、`ask_user: false`。
- **判定**：works

### 7. 先證明無狀態方案，不恢復 review ledger
- **如何測試**：執行四個盲情境與 deterministic 契約探針，並檢查新增內容。
- **發生結果**：所有情境遵守終止規則；沒有新增 runner state、review ledger 或 checker schema。
- **證據**：契約測試 8/8 通過；adversarial probe 回傳 PASS。
- **判定**：works

## 審查摘要

四個盲情境全部符合預期。Claude Code 還主動指出「單一 important 通常是
`PASS_WITH_NOTES`」，證明它沒有為了迎合情境而忽略既有嚴重度規則。

## 我問過你的問題

- 我確認你要的是兩輪正常 review，加一輪重新整理技術方案後的終局驗證。
- 我確認這次使用 Claude Code 作為第二位讀者。

## 對你既有的資料做了什麼

沒有變動你的既有資料；測試只讀取這次變更中的規則與測試情境。

## 我替你決定的內容

- **先採無狀態方案** — 盲測已能可靠停止，因此沒有新增 runner state 或 ledger。
- **保留一個正式終止 gate** — 它取代原本沒有終點的修正段落；代價是機制清單淨增一項，但不用維護另一份狀態。

## 尚未確定你是否想要的內容

沒有。
