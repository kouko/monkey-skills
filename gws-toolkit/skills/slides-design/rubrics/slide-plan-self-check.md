# Slide-plan self-check rubric

**Purpose**: after drafting `slide-plan.json` and before handing it to `slides-builder` (or a Phase 2+ backend builder), run this binary checklist as an advisory self-check.

**Nature**: **Advisory only** — MVP does not hard-gate (does not block the pipeline). The goal is to catch common narrative / layout / asset problems before the deck is built, so you spend less time hand-fixing afterwards.

**When to run**:
- Right after the `slide-plan.json` draft is complete
- Before passing the plan to the builder
- When a deck feels inconsistent and you want to trace the cause

---

## Checklist (9 items, all binary)

### Narrative and information hierarchy

- [ ] **Each slide carries one main conclusion** (一主張 / 單一結論) — `replacements.{{title}}` or `{{headline}}` states exactly one claim. A slide with two conclusions dilutes both; split it (Minto 1987).
- [ ] **Title reads standalone** (独立して読める / 可獨立讀懂) — the title is understandable without narration or the chart. If it only says "Revenue breakdown", rewrite it as a conclusion (e.g. "APAC drives 45% of revenue").
- [ ] **Narrative has an SCQA opener and Minto Pyramid structure** (SCQA 導入 + ピラミッド構造 / SCQA 開場 + 金字塔結構) — slides 1–2 show Situation → Complication → Question → Answer; the body unfolds along Pyramid branches and sibling slides are MECE.

### Visual and layout

- [ ] **Chart type is appropriate** (図表選型 / 圖表選型) — every chart follows `references/chart-selection.md` (pie with > 5 slices is converted to bar; category comparison uses bar; time series uses line; part-to-whole with ≤ 5 slices may use pie).
- [ ] **`layout_hint` matches the content** — slides with an image use `headline-image`; pure-text conclusions use `title-body`; pull quotes use `quote`; the hint agrees with the actual `replacements` / `images`.

### Assets and placeholder alignment

- [ ] **Image paths exist** — every `slides[].images[].local_path` points to a file that actually exists (verify with `ls`); no broken paths.
- [ ] **Placeholder names match the template** — the `replacements` keys (e.g. `{{title}}`, `{{headline}}`, `{{date}}`) match the placeholders in the template deck; cross-reference `slides-builder/templates/registry.md`.

### Backend setup

- [ ] **`target` field is `"google-slides"`** — MVP supports only this backend; missing or set to `"html"` / `"pptx"` / `"marp"` causes the builder to exit 12 (Phase 2+ trigger not met).

### Security

- [ ] **No sensitive data** — `replacements` contains no credentials / API keys / PII / unredacted personal data; `images[].local_path` is not a screenshot of a credential / token.

---

## How to use

### For Claude

Walk through the checklist item by item; mark each PASS or record the concrete FAIL plus a suggested fix. Finish with a summary:

```
Self-check summary:
  PASS 8 / 9
  FAIL 1: "Title reads standalone" — slide 3 title "Revenue breakdown" names a topic, not a conclusion
  Suggested fix: "APAC drives Q1 45% YoY"
```

### For the user

After running:
- All pass: hand it to the builder.
- Any fail: decide whether to fix based on severity (MVP advisory, not a hard block).
- Sensitive-data fail: **strongly suggest blocking** (still not a hard gate, but fix before building).

---

## Relationship to hard gates

MVP has **no** hard gate (see PRODUCT-SPEC §3.2 Non-Goal "design-quality-gate"). kouko acts as the gate personally. Phase 2+, if this plugin ships to external users, this rubric may be promoted to a hard gate (trigger: external users who cannot rely on kouko's judgement).

---

## Primary sources behind this rubric

- Minto (1987) *The Pyramid Principle* — "one conclusion per slide", "title reads standalone", SCQA opener
- Cleveland & McGill (1984) — chart-type selection principles
- Few (2012) *Show Me the Numbers* 2nd ed. — chart-type mapping
- This plugin's PRODUCT-SPEC v0.2 §4.4 design principles — backend-agnostic, credentials never in repo
- This plugin's TECH-SPEC v0.2 §4.1 — schema v1.1 (`target` field)
