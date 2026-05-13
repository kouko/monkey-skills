# 訪談前 ethics 與 corner case SOP

> 訪談 in-house GC 時可能撞到的 ethical / legal corner cases。先想清楚 SOP，現場才不會卡住。
>
> 適用對象：所有訪談（in-house GC / BigLaw 業務合夥人 / 法遵主管）。

---

## 1. 對方要求簽 NDA

**情境**：受訪者公司政策要求對外談話需先簽 NDA，或受訪者個人擔心訪談內容外流。

**SOP**：

- ✅ **可簽單向 NDA**（你保密受訪者公司資訊）— 你本來就對 research note 做匿名化承諾，這方向一致
- ⚠️ **避免簽雙向 / 互相保密 NDA** — 你的 research note 是公開 output，若 NDA 限制你發布 anonymized aggregated findings，整個研究目的失效
- ❌ **拒絕簽「禁止使用此次對話內容於任何 output」** — 那直接放棄訪談，沒用

**reframe 話術**：

```
您公司政策需要 NDA，完全理解。我本來的承諾就是 anonymized + 草稿
回送您過目 + 您可否決任何引述——事實上等於一份單向 NDA。如果貴司
有正式 NDA 模板我可以簽，**但需 review 條款是否允許我發布 anonymized
aggregated findings**；若條款禁止任何引述，那訪談就無法推進。
```

---

## 2. 受訪者揭露 confidential information

**情境**：訪談中 GC 不經意提到「我們公司前陣子被金管會約談 / 被罰 X 萬...」之類具體事件。

**SOP**：

- **訪談現場**：不打斷（強行打斷會破壞 rapport），但**心中標記為 "do not quote"**
- **逐字稿轉錄階段**：**直接刪除**該段（不要留在逐字稿裡，risk 電腦被竊或意外洩漏）
- **Research note**：**完全不出現**，即使 anonymized 都不行（細節能反推就是 PII）
- **不確定時**：事後 email 受訪者問「您 [關鍵字] 那段可以引用嗎」

**原則**：寧可資料少 10%，不要害到受訪者。

---

## 3. 利益衝突——你跟受訪者公司有商業關係

**情境**：你（kouko）或你 day job 公司是受訪者公司的供應商 / 客戶 / 競品。

**SOP**：

- **訪談開頭主動揭露**：「我目前 day job 在 X 公司，跟貴司可能有 [商業關係]。這個訪談是純個人開源研究，與我 day job 無關。如果這讓您不舒服，可以中止」
- 揭露後讓對方決定要不要繼續
- **不要 hide**——事後被發現破壞 trust + 可能違反受訪者公司倫理規範

---

## 4. 受訪者要求 paid output / 預期商業回報

**情境**：少數 GC 訪談後問「這個工具 launch 後會分潤嗎？」「我能成為 advisor 嗎？」

**SOP**：

- **重申** open-source MIT 授權、無 monetization model，因此沒有分潤可能
- ✅ 可以讓對方成為 **unpaid early tester / contributor**（如有意願）— research-to-product 階段也有助益
- ❌ **不要**承諾任何 future financial arrangement（含「公司化後分股」）— 即使空頭支票也會 distort 後續訪談 framing

---

## 5. 你 vs research note vs legal-toolkit 三層 separation

**重點 framing**：

| 層 | 你的角色 | 對外輸出 |
|---|---|---|
| L1 — kouko 個人 | 研究人員 / 工具開發者 | 訪談行為本身 |
| L2 — research note | 公開知識產出 | 1500-2000 行 anonymized GitHub markdown |
| L3 — legal-toolkit skill | 開源工具 | MIT-licensed plugin |

訪談時**只討論 L2 + L3**，避免混入 L1 個人 day-job 或商業意圖。受訪者最擔心的是 L1 模糊（「他到底是不是來挖角 / 對手做的偵察 / 收集 leads」），所以 disclosure 要明確：

> 「我做這份研究的個人動機是『想把法務工作流知識公開化』，沒有 day-job 利益、沒有顧問業務、沒有未來販售計畫。」

---

## 6. 訪談錄音 / 逐字稿保管 SOP

- ✅ 錄音前**明確徵得同意**（口頭即可，不必書面）
- ✅ 錄音檔存**個人本機加密磁區**（不放雲端 / 不放 GitHub）
- ✅ Whisper / metr 轉逐字稿後，**錄音檔保留 30 天**做 fact-check 用，30 天後刪除
- ✅ 逐字稿存個人本機，匿名化處理後才放入 research note 工作目錄
- ❌ 不寄錄音檔給任何第三方（包括 Claude / OpenAI API — 若用 Whisper 用 local model）

---

## 7. Done criteria — ethics 自查清單

訪談階段結束時逐條檢查：

- ☐ 每位受訪者都有書面（email）匿名化承諾紀錄
- ☐ 逐字稿中 confidential information 已清除
- ☐ Research note draft 中沒有任何可反推當事人的細節
- ☐ 受訪者過目 anonymized 引述後留有 confirm email
- ☐ 如有 NDA，NDA 條款允許 anonymized aggregated 發布
- ☐ 錄音檔已在 30 天 fact-check window 後刪除
- ☐ 利益衝突在訪談開頭主動揭露（如適用）

達成 7 條 → ethics 端 clean，可以放心 publish research note。
