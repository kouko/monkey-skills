---
name: using-slides-toolkit
description: Router skill for slides-toolkit. Route the user to the right skill based on intent (design consultation / onboarding / deck generation). MVP 僅支援 google-slides backend；html / pptx / marp 為 Phase 2+ trigger-gated。簡報・投影片・deck・プレゼン・slides・presentation・幻灯片。
---

# using-slides-toolkit

Entry router for the `slides-toolkit` plugin. Inspect the user's intent, read `slide-plan.json` `target` field（若已備），路由到正確 skill。**不**執行 shell、**不**呼叫 API、**不**做設計判斷——純 routing。

## When to use

- 使用者描述 vague（「幫我做簡報」/「プレゼン作って」/「做一份 deck」），尚未選定具體 skill
- 使用者手上有 `slide-plan.json` 但不確定下一步要呼叫哪個 builder
- 第一次使用 slides-toolkit、遇到 auth 或 setup 相關錯誤

## When NOT to use

- 使用者明確指定目標 skill（例：「跑 google-slides-builder」）→ 直接呼叫該 skill
- 任務不在 slides-toolkit 範圍（文案撰寫 → `copywriting-toolkit`；投資分析 → `investing-toolkit`）

## Routing table（intent → skill）

| Intent 訊號 | Route to |
|---|---|
| 「幫我想敘事結構」「這張該放什麼圖表」「Minto / SCQA / chart selection」「資訊層級怎麼安排」 | `slides-design` |
| 「第一次用」「401 / 403 / invalid_scope」「auth 失敗」「setup」「gws 還沒裝」「token 過期」 | `google-slides-setup` |
| 「生成 deck」「把 slide-plan 變 Google Slides」「匯出」「執行 pipeline」 | `google-slides-builder` |
| 「單一 API op 怎麼打」「debug Slides 錯誤」「學 batchUpdate」「想改 recipe」（低層）| `google-slides-api` |
| 模糊或「做 simple deck」無明確 target | 預設 `target: "google-slides"`（MVP 唯一 backend），繼續走 setup → builder |

**Example A**（設計諮詢）：
> User: 「我要做一份產品提案，開場怎麼鋪？」
> Route → `slides-design`（讀 `references/minto-scqa.md`），回 SCQA 建議，不生成 deck。

**Example B**（執行 pipeline）：
> User: 「這份 `slide-plan.json` 幫我跑」
> 檢查 `slide-plan.target == "google-slides"` → 確認 setup 完成 → Route `google-slides-builder`。

**Example C**（低層 API 學習 / debug，v0.3.2 新增）：
> User: 「gws 的 `createSlide` 到底怎麼帶 predefinedLayout？」
> Route → `google-slides-api`（讀 `protocols/recipe-create-slides.md` + `references/api-error-codes.md`）。不跑 pipeline、不生成 deck。

## Target backend detection

讀 `slide-plan.json` 頂層 `target` 欄位（schema v1.2, TECH-SPEC §4.1）：

```
target == "google-slides"  → 走 google-slides-setup / google-slides-builder
target missing             → 假設 "google-slides"（MVP 唯一 backend），明示告知 user
target ∈ {"html","pptx","marp"}  → 報錯並指向下方 Phase 2+ trigger
target == 其他字串         → 報錯：unsupported backend
```

若 user 已有 plan 但缺 `target`，router 可代填 `"google-slides"` 並提醒「Phase 2+ 才支援其他 backend」。

## Phase 2+ backends（trigger-gated，非承諾）

以下 backend **未在 MVP 實作**；列出僅供 forward-looking。trigger 條件見 PRODUCT-SPEC §3.5：

| Backend | Skill（未來） | Trigger |
|---|---|---|
| `html` | `html-builder` | 首次出現 HTML / reveal.js / remark 輸出需求 |
| `pptx` | `pptx-builder` | 首次 `.pptx` 輸出需求（e.g. 交付給 MS Office 收件人） |
| `marp` | `marp-builder` | 首次 Marp CLI 輸出需求（engineering tech talk / markdown-native） |

使用者若在 `target` 指定上述值，回訊：「backend `<value>` 尚未實作；MVP 僅支援 `google-slides`。trigger 條件見 PRODUCT-SPEC §3.5。」

## Out of scope — hand off

| Need | Target |
|---|---|
| 文案撰寫 / headline / PASONA / QUEST | `copywriting-toolkit:using-copywriting-toolkit` |
| 投資分析 / 簡報內含財報內容 | `investing-toolkit:using-investing-toolkit` |
| 技術文件 / API reference | `domain-teams:docs-team` |

---

> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
