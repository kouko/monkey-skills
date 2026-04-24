---
name: slides-design
description: Backend-agnostic design knowledge layer for slides-toolkit. Minto Pyramid / SCQA narrative structures + chart-type selection reference. 對所有 backend（Google Slides / HTML / PPTX / Marp）通用，不綁定特定執行層。簡報設計諮詢・敘事結構・圖表選型・information design。
---

# slides-design

Backend-agnostic design knowledge layer for slides-toolkit. This skill supplies narrative-structure and chart-selection references so that Claude can anchor its reasoning to named design principles when generating or reviewing a slide plan. The principles apply to **any output format** — Google Slides, HTML, PPTX, and Marp all share the same reference.

> Design knowledge and execution are decoupled (PRODUCT-SPEC §4.4 principle 3). This skill **does not** generate charts, write boilerplate, or call backend APIs. Execution belongs to `google-slides-builder` (or a Phase 2+ backend builder).

## When to use

Route to this skill when the user is asking about design, not execution:

- **Narrative structure** (ナラティブ構成 / 敘事結構) — how to open a deck, how to organize 30 pages, where the main conclusion belongs.
  - EN: "how should I open", "structure this deck", "where does the conclusion go"
  - JP: 「導入どう組む」「構成を組みたい」「結論はどこに」
  - ZH: 「開場怎麼鋪」「幫我組架構」「結論放哪頁」
- **Chart selection** (図表の選び方 / 圖表選型) — time series vs category vs part-to-whole data, deciding between bar chart (棒グラフ / 長條圖), line chart (折れ線 / 折線圖), pie chart (円グラフ / 圓餅圖), or scatter plot (散布図 / 散點圖).
  - EN: "which chart type", "should I use a pie", "compare categories"
  - JP: 「どの図表を使う」「円グラフでいい？」「カテゴリ比較」
  - ZH: 「哪種圖表」「用圓餅好嗎」「類別比較」
- **Information hierarchy** (情報階層 / 資訊層級) — confirming main conclusion → supporting arguments → evidence before filling the slide plan.
  - EN: "what's the main message", "information hierarchy"
  - JP: 「主結論は」「情報の階層」
  - ZH: 「主結論是什麼」「資訊層級」
- **Self-check on a draft plan** — `slide-plan.json` already drafted and you want narrative-flow / layout-hint sanity checks.

## When NOT to use

- The user wants to **execute** the pipeline (build the deck, export it) → `google-slides-builder`
- First-time setup or auth problems → `google-slides-setup`
- The user wants to **generate** a chart (CSV → PNG) → out of MVP scope (PRODUCT-SPEC §3.2 Non-Goal); produce the PNG in matplotlib / Excel, then pass it to the builder
- The user wants deep references (Tufte / Duarte / Takahashi method) → see Phase 2+ extensions below

## References (backend-agnostic)

This skill reads only the following references; it performs no I/O.

- `references/minto-scqa.md` — Minto Pyramid (Minto 1987) + SCQA opener (Minto 1987 introduction template). Used to decide **narrative structure** and **information hierarchy**.
- `references/chart-selection.md` — data-shape to chart-type table + decision tree. Used to decide **which chart or visual element** each slide should use (MVP **does not** generate charts).

**Example A** (narrative structure):
> User: "I have a 12-page SaaS proposal — how should I organize it?"
> → Read `references/minto-scqa.md` → suggest: cover = main conclusion (Answer), slide 2 = SCQA opener, slides 3–10 = Pyramid main branches, slide 11 = horizontal deduction, slide 12 = CTA.

**Example B** (chart selection):
> User: "I have revenue share across 8 categories — is a pie chart fine?"
> → Read `references/chart-selection.md` → more than 5 slices means switch to bar (pie is hard to read); if the point is part-to-whole, use stacked bar.

## Self-check rubric

Once `slide-plan.json` is drafted (or before handing it to a builder), run the 9-item binary checklist in `rubrics/slide-plan-self-check.md` to confirm narrative / layout / image paths / `target` fields are ready. MVP treats this as **advisory only** — it does not hard-gate the pipeline.

## Output

This skill produces **text recommendations** that the user or Claude can paste directly into `slide-plan.json`:

- Narrative flow → becomes `slides[].slide_index` ordering plus per-slide `replacements.{{headline}}`
- Chart type → becomes `slides[].layout_hint` (generic hint; backend-specific interpretation happens in the builder — examples: `title-body`, `headline-image`, `bullets`, `quote`)
- One main conclusion per slide → becomes `replacements.{{title}}` or `{{headline}}`

**Example output** (ready for the builder or the user):

```
Slide 3 suggestion:
- headline: "Q1 revenue 45% YoY growth driven by APAC expansion"
- layout_hint: "headline-image"
- chart type: horizontal bar (8 regions; pie would exceed the 5-slice threshold)
- narrative role: first-level supporting argument (evidence) in the Pyramid
```

## Backend-agnostic declaration

This skill **does not** contain any of the following (they belong to the execution layer or to specific backends):

- Google Slides API calls or the actual enum values for `layout_hint`
- gws CLI commands or OAuth scopes
- HTML / reveal.js / PPTX / Marp syntax
- Placeholder-object-ID mapping logic (that lives in `google-slides-builder`)

**Because** design principles stay stable across output formats (Minto 1987 applies equally to Google Slides and Marp), decoupling them from execution lets future backends be added without touching the knowledge layer.

## Phase 2+ extensions (trigger-gated)

The deep references below are **not in MVP**. They are added once the trigger condition fires (PRODUCT-SPEC §3.5):

| Extension | Primary source | Trigger |
|---|---|---|
| Visual display of quantitative info deep-dive | Tufte (2001) *The Visual Display of Quantitative Information* 2nd ed.; Cleveland & McGill (1984) | External feedback: "chart reference is not deep enough" |
| Presentation design deep-dive | Duarte (2008) *slide:ology*; Duarte (2010) *Resonate* | External feedback: "narrative flow is not deep enough" |
| Takahashi method (single-phrase style) | Takahashi Masayuki presentations, 2005–; public materials | Japanese technical talk scenario appears |
| Data dashboard design | Few (2012) *Show Me the Numbers* 2nd ed. | Dashboard-style deck request appears |

In MVP, if asked for a deeper reference, reply: "Phase 2 trigger not met; the current Minto + chart-selection baseline already covers ≥ 80% of scenarios", and point back to the existing references.

---

> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
