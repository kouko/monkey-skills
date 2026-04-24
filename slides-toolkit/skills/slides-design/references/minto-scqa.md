# Minto Pyramid & SCQA — narrative structure reference

**Primary source**：Barbara Minto (1987) *The Pyramid Principle: Logic in Writing and Thinking*. Pitman Publishing（初版）; later editions FT Pearson. SCQA 屬 Minto 體系內的 introduction template，**非**獨立 framework。

本 reference 提供 slide deck 的**敘事結構**選型與應用。對任何輸出格式（Google Slides / HTML / PPTX / Marp）通用。

---

## 1. Minto Pyramid — 核心規則

Minto 1987 提出的書寫 / 思考結構，適用於商業報告、提案、簡報、備忘錄。**結論在頂、支持論點往下延伸**，三條主規則：

1. **Answer first（結論在頂）** — 讀者先看到主結論，再看支持理由。違反：把鋪陳放前面、結論埋在底。
2. **MECE（Mutually Exclusive, Collectively Exhaustive）** — 同一層的 sibling ideas 彼此互斥、合起來窮盡該層議題。違反：分類重疊（同一事在兩個分支都出現）或遺漏（讀者想到的關鍵面向不在任何分支）。
3. **縱向 Q&A、橫向 deduction / induction** — 縱向：下層永遠在**回答**上層勾起的問題（why / how / what does this mean）。橫向：同層支持論點之間用 deduction（前提 → 前提 → 結論）或 induction（多個同類案例 → 通則）兩種邏輯之一組織。

### Minto Pyramid 示意

```
                    ┌─────────────────────┐
                    │  Main Conclusion    │  ← Answer（封面 slide 放這）
                    │  (Governing Idea)   │
                    └──────────┬──────────┘
                               │  縱向：下層回答「why / how」
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │ Support 1│    │ Support 2│    │ Support 3│  ← Sibling 須 MECE
        └────┬─────┘    └────┬─────┘    └────┬─────┘
             │               │                │
        ┌────┴───┐       ┌───┴────┐      ┌────┴───┐
        ▼        ▼       ▼        ▼      ▼        ▼
      [證據]  [證據]   [證據]  [證據]  [證據]  [證據]
```

---

## 2. SCQA — 開場結構（Minto 1987 introduction template）

Minto 1987 Ch.4 提出的 **introduction template**，用於文件 / 簡報**開場**（非整份結構）。Four elements：

| 元素 | 意義 | 例 |
|---|---|---|
| **S**ituation | 讀者已知的穩定背景 | 「公司過去三年在 APAC 市場穩定成長」 |
| **C**omplication | 打破穩定的變化 / 困境 | 「但 2026 年 APAC 競爭對手進入價格戰」 |
| **Q**uestion | 由 Complication 自然引出的問題 | 「我們該如何維持 market share？」 |
| **A**nswer | 本份簡報 / 文件的主結論 | 「聚焦高毛利垂直市場 + 產品差異化」 |

**何時用 SCQA**：所有非技術備忘錄以外的簡報開場。第 1–2 頁把讀者從「熟悉背景」帶到「需要答案」的心理狀態。

**SCQA 變體**（Minto 1987 §4.3）：
- **SCAQ**（先 Answer 再 Question）：讀者已急著要解法時倒裝
- **QSCA**（先丟問題）：演講 / 對話場景吸注意力
- MVP 預設用標準 SCQA。

---

## 3. 套到 slide deck 的 mapping

| Deck 元素 | Minto 對應 | 具體作法 |
|---|---|---|
| 封面 slide（cover） | **Answer**（主結論） | Title = 主結論本身，不是 deck 名稱。Example: 「Invest in APAC vertical expansion — $12M opportunity by 2027」，**不是**「2026 APAC 策略」 |
| 第 2 頁（opener / executive summary） | **SCQA** | 4 個短段對應 S/C/Q/A；或 4 個 bullet。也可拆 2 頁（S+C / Q+A） |
| 大綱 slide（agenda） | Pyramid 的**主幹分支** | 3–5 個 sibling ideas（MECE），對應深入展開的章節 |
| 章節 divider | 主幹分支節點 | 每個 divider 明示「本節回答上層的哪個問題」 |
| 內容 slide | 分支下的**支持證據** | 每張 slide 只負責 1 個結論 + 其證據；title 寫出結論 |
| 收尾 slide | 重申 Answer + CTA | 回到 Answer，明示下一步行動 |

### Mapping 圖

```
Cover         ──► Answer（主結論 = title）
    │
Opener        ──► SCQA（4 段 / 4 bullets / 2 slides）
    │
Agenda        ──► Pyramid 主幹分支（3–5 MECE sibling）
    │
├─ Section 1  ──► 分支 A
│    ├─ slide A.1    ──► A 的證據 1
│    ├─ slide A.2    ──► A 的證據 2
│    └─ slide A.3    ──► A 的證據 3
├─ Section 2  ──► 分支 B（與 A MECE）
└─ Section 3  ──► 分支 C
    │
Closing       ──► 重申 Answer + CTA
```

---

## 4. 實用 checklist（draft 後自檢）

draft 完 deck 大綱後，跑以下 7 項：

- [ ] **封面是 Answer，不是 deck 名稱** — 讀 cover title，能否獨立看出主結論？若只看到「2026 Q2 Review」則不合格。
- [ ] **每張 slide 1 個結論** — 一頁多結論 = 稀釋 + 強迫讀者自己找重點。拆頁。
- [ ] **Title 可獨立讀懂** — 不依賴口頭補充，不靠圖表解釋。Title 是該頁的 micro-Answer。
- [ ] **Sibling slides MECE** — 同一 agenda 分支下的 slides 彼此互斥、合起來窮盡該分支；拿分支 title 問「我還想到什麼沒被涵蓋？」
- [ ] **縱向 Q 回應** — 每頁 title 必須回應**上一層勾起的問題**；若無法指出「這頁回答的是哪個問題」，該頁可能是 orphan。
- [ ] **橫向邏輯一致** — 同層支持論點用 **deduction**（前提鏈）或 **induction**（案例歸納）其中之一；不混用。
- [ ] **開場是 SCQA，不是 self-intro** — 開場前 2 頁用 SCQA 把讀者推到「需要 Answer」的狀態，不要從「Hi I'm X」開始。

---

## 5. 常見錯誤與修法

| 錯誤 | 症狀 | 修法 |
|---|---|---|
| Cover 用 deck 名稱 | Title: 「2026 Q2 Strategy Review」 | 改寫為主結論：「Shift 40% of engineering to APAC vertical」 |
| 支持論點互相重疊 | 分支 A 的 slide 跟分支 B 的 slide 說同一件事 | 重畫 Pyramid；提升到共同 parent 或刪重複 |
| Slide title 只寫主題，不寫結論 | Title: 「Revenue breakdown」 | 改寫為結論：「APAC 占 45%，驅動 Q1 成長」 |
| SCQA 的 Question 太發散 | 4 頁 bullet 鋪陳，讀者還不知道 deck 要答什麼 | 砍 S/C 到各 1 行；讓 Question 自然從 Complication 跳出 |
| 橫向 deduction / induction 混用 | 同一 agenda 三個 section 一個是 case list、一個是 if-then、一個是 mixed | 選一種；通常商業簡報用 induction（case → pattern） |

---

## 6. Primary source 與擴展

**MVP 主錨**：Minto (1987) *The Pyramid Principle*。

**Phase 2+ 深化 reference**（trigger-gated；見 SKILL.md Phase 2+ 擴展點）：
- Duarte (2010) *Resonate*：加入「英雄旅程」敘事結構，適合 keynote / pitch deck
- Reynolds (2019) *Presentation Zen* 3rd ed.：加入極簡視覺原則
- 高橋征義 高橋メソッド：大字一行流，日文技術社群慣例

MVP 不展開以上 reference；Minto + SCQA 已足夠覆蓋商業 / 週報 / 提案 ≥ 80% 場景。
