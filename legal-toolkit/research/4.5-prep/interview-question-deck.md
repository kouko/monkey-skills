# 上市櫃 in-house GC 訪談題庫

> **訪談對象**：3-5 位上市櫃 in-house 法務主管 / GC（mid-cap 為主），1-2 位 BigLaw 上市公司業務合夥人，1-2 位法令遵循部門主管。
>
> **訪談時長**：30 min compact（如果只能拿到一場短會）或 60-90 min full。
>
> **目的**：unblock legal-toolkit Phase 5 兩個 sub-skill（`legal-corporate-governance` + `legal-dd-quickscan`）設計決定。
>
> **匿名化保證**：受訪者公司 / 姓名不在 research note 出現；只引用 aggregated finding 或 anonymized 引述（"某 mid-cap 製造業 GC 表示…"）。

---

## 30-min compact 版（必問 5 題）

如果只拿到 30 分鐘，鎖死這 5 題 + 留 5 分鐘自由閒談（最痛點往往在閒談浮現）。

### Q1（5 min）— 一週工時分布
> 「您一週大致花多少比例時間在以下幾類？合約 review / 法令遵循 / 重大訊息揭露準備 / 股東會董事會準備 / 內部諮詢 / 外部律師協作 / 其他」

**為什麼**：直接決定 sub-skill 優先級。Hypothesis：合約 30-40%、Compliance 30-40%、其餘 20-40%。
**Probe**：哪一類最近幾個月最吃時間？

---

### Q2（5 min）— Compliance vs 一般合約的本質差異
> 「在您的工作經驗裡，重大訊息揭露 / 公司治理跟一般合約 review 最根本的差異是什麼？是『沒有對手在議價』的單方義務，還是其他？」

**為什麼**：驗證 legal-toolkit 第 5 種 abstraction（Compliance cluster = 法定義務場景）設計。
**Probe**：有沒有具體例子讓您覺得「這完全不像 contract review」？

---

### Q3（5 min）— 重大訊息「即時 / 重大 / 一般」的判斷依據
> 「公司內部判斷一個事件該歸到『即時公告（2 小時）』、『重大訊息（次一交易日）』、還是『一般申報（7 日）』，是有 SOP 還是 case-by-case？最容易判斷錯的場景是什麼？」

**為什麼**：`legal-corporate-governance` skill 核心 routing 邏輯 — 沒有可信決策樹，整個 skill 就站不起來。
**Probe**：有沒有遇過內部判斷跟證交所事後認定不一致的案例？

---

### Q4（5 min）— 跟法令遵循 / 內部稽核的分工
> 「您公司有沒有獨立的法令遵循主管 / 內部稽核部門？三道防線在您公司怎麼運作？哪些 task 是『法務做』哪些是『法遵做』？」

**為什麼**：避免 skill 設計越界。如果 Compliance Officer 是獨立部門，skill 不該侵入。
**Probe**：法務跟法遵的灰色地帶通常在哪裡？

---

### Q5（5 min）— 最痛的工具空缺
> 「如果您現在能給法務團隊變一個工具，您最想要什麼？或者反過來說，現在最讓您加班的『重複性 + 低判斷』的工作是什麼？」

**為什麼**：找 skill 真正的 ROI 出口（呼應 Harvey JTBD 方法論）。
**Probe**：現有 vendor（LegalSign.ai / 律果 / GoBitX）為什麼沒解決？

---

### 5 min 自由閒談
直接問：「除了上述，有沒有什麼我沒問到、但對您工作很關鍵的事？」

---

## 60-90 min full 版（10 題完整）

10 題完整版 = compact 5 題 + 下面 5 題。建議順序：先 Q1-Q5（compact 暖場），再 Q6-Q10（深問）。

### Q6（10 min）— 股東會 / 董事會法定流程
> 「公司法 §172 / §192 / §202 規範的股東會 / 董事會流程，您實務上有多少是 checklist 跑就完成、多少需要 case-by-case 判斷？」

**為什麼**：判斷 Phase 5 corporate-governance skill 的 abstraction 是「checklist + template」還是「playbook」。
**Probe**：哪些步驟最容易踩雷？開會通知時程？議案送交期限？

---

### Q7（10 min）— 配合被併購 DD vs 主動投資 DD
> 「您公司有沒有經歷過被併購 DD（賣方視角）或主動投資 DD（買方視角）？兩種工作流差異多大？跨境投資（外資 / 對外投資）的申報要走多少程序？」

**為什麼**：`legal-dd-quickscan` 設計成「上市櫃配合被併購 DD」，但實際痛點可能在「對外投資 DD + 投審會申報」。
**Probe**：跟外部 M&A 律所怎麼分工？哪些東西您 in-house 不會自己跑、一定要外包？

---

### Q8（10 min）— ESG / 永續報告書 法務職責
> 「永續報告書（TCFD / IFRS S1 S2 / 永續發展行動方案）在您公司是 ESG / 永續部門主導，還是法務深度介入？法務 review 的範圍是 disclaimer + 揭露口徑，還是更廣？」

**為什麼**：決定要不要把 ESG 切成獨立 sub-skill（`legal-esg-disclosure`）。
**Probe**：如果未來 ESG disclosure 變強制（金管會 2027 timeline），您預期法務工時增加多少？

---

### Q9（10 min）— Template 更新節奏
> 「法令變動（如個資法 2025/11 修正）、證交所新函令、TWSE 公司治理評鑑指標更新等，內部 template / SOP / checklist 多久更新一次？是年度大更新還是即時跟進？」

**為什麼**：直接設計 `legal-regulation-watch` ↔ `legal-corporate-governance` 連動觸發機制。
**Probe**：上一次大法令變動是什麼？您是怎麼知道的（自己看 / 主管機關 email / vendor alert / 律師通知）？

---

### Q10（10 min）— Audit-trail / Litigation-ready 設計
> 「上市櫃文件您是否預設『明天可能被當訴訟證據』？哪些文件法定必須留下 timestamp / signature 元資料？skill 輸出（合約 review memo / 揭露文）該不該強制加 audit metadata？」

**為什麼**：[特殊議題 §5.1]。如果這是 hard requirement，skill 輸出格式要調整。
**Probe**：有沒有遇過審計時翻不到當初決策依據的窘境？

---

## 訪談技巧備忘

- **錄音 + 逐字稿**：徵得同意後錄音，事後 Whisper / metr 轉文字。匿名化在 research note 寫作階段做，不在訪談現場做。
- **不要強行 5 題壓 30 分鐘**：受訪者離題到痛點時順著走 — 痛點訊號比照表填答有價值 10 倍。
- **Hypothesis 不要先說**：問 Q2 / Q4 / Q9 時不要先洩漏「我預期答案是 X」，否則受訪者會配合（confirmation bias）。
- **數字 follow-up**：受訪者說「很多」「很常」時，追問「每月幾次？花多少小時？」— 量化才能進 research note。
- **取得後續聯繫權**：訪談結束問「未來有 follow-up 問題能 email 您嗎？」— 後續 research note 草稿可發回確認 anonymized 引述。

---

## Done criteria（訪談階段）

- ✅ 3-5 位 in-house GC 完成（30-min compact 至少 + 60-90 min full 至少 2 位）
- ✅ 1-2 位 BigLaw 上市公司業務合夥人完成（外部視角對照）
- ✅ 1-2 位法遵主管完成（分工邊界 Q4 深問）
- ✅ 每位受訪者錄音 + 逐字稿
- ✅ 10 個核心問題每個都有 ≥ 2 個 primary source（訪談 + 公開文獻），confidence MEDIUM 以上

達成後 → 寫 full research note → unblocks Phase 5。
