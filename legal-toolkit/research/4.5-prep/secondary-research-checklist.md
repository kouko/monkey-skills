# Secondary research checklist（訪談前可獨自做）

> 訪談 lead-time 約 2-4 週；同期間可平行做這份 checklist，不依賴 GC。完成後訪談時可問更精準的問題（不用浪費時間問「重大訊息範圍是什麼？」這類有公開答案的事）。
>
> **動作者**：kouko 親自 / Claude subagent / 兩者協作均可。每項目給「估時」+「產出 location」+「done criteria」。

---

## 階段 1 — 法源原典通讀（2-3 天）

訪談前必須對主要法源「讀過至少一次」，否則 30-min 訪談會被基本問題吃掉。

| # | 法源 | URL | 估時 | done criteria |
|---|---|---|---|---|
| 1 | 證券交易法（重點：§14-1 內控 / §36 揭露 / §157-1 內線交易） | <https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=G0400001> | 4-6 h | 章節 mind map + 跟 legal-toolkit 對應點摘要 |
| 2 | 公司法（重點：§172 股東會 / §192 董事 / §202 董事會） | <https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=J0080001> | 3-4 h | 同上 |
| 3 | 對有價證券上市公司重大訊息之查證暨公開處理程序（TWSE） | TWSE 法規檢索系統 | 2-3 h | 「即時 / 重大 / 一般」3 層分類完整 mapping + 例外清單 |
| 4 | 上市上櫃公司治理實務守則 | TWSE / TPEx | 2-3 h | 公司治理 best practice 摘要 |
| 5 | 公開發行公司建立內部控制制度處理準則 | 金管會 | 1-2 h | 三道防線 framework + 法務 vs 法遵分工的法定依據 |

**儲存位置**：`legal-toolkit/research/4.5-prep/secondary/01-statute-reading-notes.md`（一份檔，分節）

---

## 階段 2 — 主管機關函令彙編（2-3 天）

| # | 來源 | 重點 | 估時 |
|---|---|---|---|
| 1 | 金管會函令檢索 — 重大訊息 + 內控 + ESG | filter by 2023-01-01 之後 | 4-6 h |
| 2 | TWSE 公告事項（公司治理 / 重大訊息範例） | 抓「重大訊息範例」案例集 | 3-4 h |
| 3 | TPEx 公告事項 | 同上但聚焦上櫃 / 興櫃差異 | 2 h |
| 4 | 公開資訊觀測站申報期限總表 | 抓所有申報項目 + deadline | 2-3 h |

**儲存位置**：`legal-toolkit/research/4.5-prep/secondary/02-regulator-letters.md` + 一份 `regulator-deadlines.csv`（用於 `legal-corporate-governance` skill 的 deadline tracker）

---

## 階段 3 — BigLaw newsletter / 法律期刊（1-2 天）

| # | 來源 | 抓什麼 | 估時 |
|---|---|---|---|
| 1 | 理律 Lee and Li Bulletin | 近 2 年上市櫃 compliance / M&A 主題 | 2-3 h |
| 2 | 寰瀛 Formosa Transnational publications | 同上 | 1-2 h |
| 3 | Jones Day Taipei publications | 同上（英文 — 國際視角） | 1-2 h |
| 4 | 月旦法學雜誌 / 台灣法學雜誌 | 搜「上市公司治理」「重大訊息」「內線交易」相關學術論文 | 3-4 h |
| 5 | KPMG / PwC / Deloitte / EY 法令遵循 publications | ESG / 公司治理 3.0 主題 | 2-3 h |

**儲存位置**：`legal-toolkit/research/4.5-prep/secondary/03-secondary-literature.md`（按主題分類）

**重點觀察**：
- 哪些議題 BigLaw 都在寫 → 高熱度，skill 必須涵蓋
- 哪些議題 BigLaw 沉默 → 可能（a）已成熟無爭議（b）冷門
- 學者論文 vs BigLaw 客戶通訊的觀點差距 → 揭示「實務 vs 理論」gap

---

## 階段 4 — Vendor / Tool survey（1 天，optional）

> 不阻塞 Phase 5；competitive analysis 用。可委派給 Claude subagent。

| Vendor | URL | 觀察點 |
|---|---|---|
| LegalSign.ai | <https://legalsign.ai/> | 是否有上市櫃模組 / 重大訊息揭露輔助 |
| 律果科技 | （搜尋） | 同上 |
| GoBitX | （搜尋） | 公司治理 / ESG SaaS |
| Diligent / GovernanceCloud | <https://www.diligent.com/> | 國際 best practice |
| ISS / Glass Lewis | （搜尋） | 機構投資人 governance scoring |

**儲存位置**：`legal-toolkit/research/4.5-prep/secondary/04-vendor-survey.md`（每個 vendor 一段，含 pricing / feature scope / 是否 TW localized）

---

## 階段 5 — 公開資訊觀測站 sample 申報抽樣（0.5-1 天）

抓 5-10 家上市櫃公司近 1 年的：
- 重大訊息公告（看判斷依據）
- 內控聲明書
- 公司治理年報
- 永續報告書

**儲存位置**：`legal-toolkit/research/4.5-prep/secondary/05-mops-samples/`（gitignored — 不必 commit，但可作為訪談 Q3 / Q8 的真實素材）

**重點**：「為什麼這家公司認為這個事件是『重大』，另一家認為是『一般』？」 — 訪談時可拿這個真實對比問。

---

## Done criteria（secondary research 整體）

- ✅ 階段 1（法源通讀）完成 → 訪談 Q1-Q10 有 baseline answer 草稿
- ✅ 階段 2（函令）完成 → Q3 + Q4 + Q9 的 deadline / threshold 表已建好
- ✅ 階段 3（newsletter）完成 → 學術 vs 實務的張力地圖
- ✅ （optional）階段 4 + 階段 5 補完 → 訪談題目更精準

**達成後**：訪談時你不再是 cold-start 學生，而是「我已經讀完法源 + 看了 5 家案例，想跟您 calibrate 我這個 hypothesis 對不對」的對等對話。這對訪談品質拉力極大。

---

## 委派建議

| 階段 | 適合 Claude subagent？ |
|---|---|
| 階段 1（法源通讀） | ⚠️ 可協助 mind-map 但 kouko 必須親自讀（不能省） |
| 階段 2（函令） | ✅ 適合 subagent 抓函令 + 整理 deadline 表 |
| 階段 3（newsletter） | ✅ 適合 subagent 摘要 + 主題分類 |
| 階段 4（vendor） | ✅ 完全可委派 subagent |
| 階段 5（MOPS sample） | ⚠️ subagent 可抓資料，但「為什麼判斷成這層」需要 kouko 法律判斷 |
