---
name: slides-design
description: Backend-agnostic design knowledge layer for slides-toolkit. Minto Pyramid / SCQA narrative structures + chart-type selection reference. 對所有 backend（Google Slides / HTML / PPTX / Marp）通用，不綁定特定執行層。簡報設計諮詢・敘事結構・圖表選型・information design。
---

# slides-design

**Backend-agnostic design knowledge layer**。提供敘事結構與圖表選型 reference，讓 Claude 在生成 / 審視 slide plan 時有可錨定的設計原則。設計原則對**任何輸出格式**都適用——Google Slides、HTML、PPTX、Marp 共用同一份 reference。

> 設計知識層與執行層解耦（PRODUCT-SPEC §4.4 principle 3）：本 skill **不**產生圖表、**不**寫 boilerplate、**不**呼叫 backend API。執行歸 `google-slides-builder`（或 Phase 2+ 新 backend builder）。

## When to use

- 使用者要「敘事建議」：開場怎麼鋪、一份 30 頁 deck 怎麼組織、主結論該放哪頁
- 使用者問「哪種圖表」：手上是時序 / 類別比較 / 部分 vs 整體資料，問該選 Bar / Line / Pie / Scatter
- 使用者想先確認**資訊層級**（主結論 → 支持論點 → 證據）再動手填 slide plan
- `slide-plan.json` 已 draft 但要做敘事流 / layout hint self-check

## When NOT to use

- 使用者要**執行** pipeline（生成 deck / 匯出）→ `google-slides-builder`
- 首次設定、auth 問題 → `google-slides-setup`
- 使用者要**生成**圖表（CSV → PNG）→ 非 MVP scope（PRODUCT-SPEC §3.2 Non-Goal）；自行用 matplotlib / Excel 產好 PNG 再交給 builder
- 使用者要深度 reference（Tufte / Duarte / 高橋メソッド）→ 見下方 Phase 2+ 擴展點

## References（backend-agnostic）

本 skill 只讀以下 reference；不做 I/O。

- `references/minto-scqa.md` — Minto Pyramid（Minto 1987）+ SCQA 開場（Minto 1987 introduction template）。用於決定**敘事結構**與**資訊層級**
- `references/chart-selection.md` — 資料形態 → chart type 對照表 + decision tree。用於決定**每張 slide 該用哪種圖表 / 視覺元件**（MVP **不含**圖表生成）

**Example A**（敘事結構）：
> User: 「12 頁的 SaaS 提案，該怎麼組？」
> → 讀 `references/minto-scqa.md` → 建議：封面放主結論（Answer）、第 2 頁 SCQA 開場、第 3–10 頁依 Pyramid 主幹分支展開、第 11 頁橫向推論（deduction）、第 12 頁 CTA。

**Example B**（圖表選型）：
> User: 「我有 8 個類別的 revenue 佔比，用 pie chart 好嗎？」
> → 讀 `references/chart-selection.md` → 超過 5 slice 改 Bar（Pie 易誤判）；若強調「部分 vs 整體」可用 Stacked bar。

## Self-check rubric

draft 完 `slide-plan.json` 後（或要交給 builder 前），跑 `rubrics/slide-plan-self-check.md` 的 6–10 項 binary checklist，確認敘事 / layout / 圖片路徑 / target 欄位皆就緒。MVP 為 **advisory only**，不 hard-gate。

## Output

本 skill 產出**文字建議**，可被使用者或 Claude 直接 paste 進 `slide-plan.json` 的對應欄位：

- 敘事流 → 反映在 `slides[].slide_index` 的排序 + 每張的 `replacements.{{headline}}`
- 圖表型別 → 反映在 `slides[].layout_hint`（通用 hint，例：`title-body` / `headline-image` / `bullets` / `quote`；backend 自行解讀）
- 每張 slide 的 1 個主結論 → 反映在 `replacements.{{title}}` 或 `{{headline}}`

**Output 範例**（可交給 builder 或 user）：

```
Slide 3 建議：
- headline: "Q1 revenue 45% YoY growth driven by APAC expansion"
- layout_hint: "headline-image"
- chart type: horizontal bar（8 個地區比較，Pie 會超過 5 slice 門檻）
- narrative role: Pyramid 的第一層支持論點（證據）
```

## Backend-agnostic 聲明

本 skill **沒有**以下內容（皆屬執行層或特定 backend 知識）：

- ❌ Google Drive ID / template_ref 查詢
- ❌ gws CLI 指令、OAuth scope
- ❌ HTML / reveal.js / PPTX / Marp 語法
- ❌ Placeholder 命名 convention（此屬 `google-slides-builder/templates/registry.md`）

**Because** 設計原則跨輸出格式穩定（Minto 1987 對 Google Slides 跟 Marp 一樣適用），執行技術會演化——解耦讓未來新增 backend 不需改動知識層。

## Phase 2+ 擴展點（trigger-gated）

以下深度 reference **未在 MVP**，trigger 條件達成後才加（PRODUCT-SPEC §3.5）：

| 擴展 | Primary source | Trigger |
|---|---|---|
| Visual display of quantitative info 深化 | Tufte (2001) *The Visual Display of Quantitative Information* 2nd ed.; Cleveland & McGill (1984) | 外部使用者回饋「圖表 reference 不夠」 |
| Presentation design 深化 | Duarte (2008) *slide:ology*; Duarte (2010) *Resonate* | 外部使用者回饋「簡報 flow 不夠」 |
| 高橋メソッド（大字一行流） | 高橋征義 presentations 2005–; 公開資料 | 出現日文技術 talk 場景 |
| Data dashboard design | Few (2012) *Show Me the Numbers* 2nd ed. | 出現 dashboard-style deck 需求 |

MVP 若被問深度 reference，回「Phase 2 trigger 條件未達；現有 Minto + chart-selection baseline 已足以覆蓋 ≥ 80% 場景」並提供現有 reference。

---

> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
