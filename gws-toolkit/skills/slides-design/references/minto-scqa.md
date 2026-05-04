# Minto Pyramid & SCQA — narrative structure reference

**Primary source**: Minto, B. (1987) *The Pyramid Principle: Logic in Writing and Thinking*. Pitman Publishing (1st ed.); later editions FT Pearson. SCQA is an introduction template inside Minto's system — it is **not** an independent framework.

This reference offers narrative-structure choices for a slide deck. It applies across output formats (Google Slides / HTML / PPTX / Marp).

---

## 1. Minto Pyramid (ミントピラミッド / 金字塔原理) — core rules

Minto 1987 proposed this structure for business reports, proposals, presentations, and memos. **The conclusion sits on top; supporting ideas branch downward.** Three rules govern the shape:

1. **Answer first** (答えから / 結論優先) — the reader sees the main conclusion before the supporting reasons. Violation: burying the conclusion under a long setup.
2. **MECE — Mutually Exclusive, Collectively Exhaustive** (相互排他・網羅的 / 相互獨立・完全窮盡) — siblings at the same level do not overlap and together cover the whole question. Violation: overlapping categories (the same item shows up in two branches) or omission (a key angle the reader expects is missing).
3. **Vertical Q&A, horizontal deduction or induction** (縦はQ&A・横は演繹/帰納 / 縱向 Q&A・橫向演繹/歸納) — vertically, each level **answers** the question raised by the level above (why / how / what does this mean). Horizontally, siblings on the same level organize by **deduction** (premise → premise → conclusion) or **induction** (multiple cases → shared pattern).

### Minto Pyramid sketch

```
                    ┌─────────────────────┐
                    │  Main Conclusion    │  ← Answer (belongs on the cover)
                    │  (Governing Idea)   │
                    └──────────┬──────────┘
                               │  vertical: lower levels answer "why / how"
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │ Support 1│    │ Support 2│    │ Support 3│  ← Siblings must be MECE
        └────┬─────┘    └────┬─────┘    └────┬─────┘
             │               │                │
        ┌────┴───┐       ┌───┴────┐      ┌────┴───┐
        ▼        ▼       ▼        ▼      ▼        ▼
    [evidence][evidence][evidence][evidence][evidence][evidence]
```

### Top-down writing (トップダウン / 由上而下)

Minto insists the draft order is top-down: state the governing idea, then work out the supporting branches, then fill in evidence. Bottom-up drafting (collect facts first, hope the conclusion appears) produces decks where the reader has to reverse-engineer the point.

---

## 2. SCQA — opener structure (Minto 1987 introduction template)

Minto 1987 Ch.4 introduces the **SCQA** opener, used for the **first one or two slides** of a deck — not the whole structure. Four elements:

- **Situation** (状況 / 情境) — shared context the audience already agrees with. Example: "APAC revenue has grown steadily for the past three years."
- **Complication** (複雑化 / 變局) — a change or tension that disrupts the situation. Example: "In 2026, APAC competitors launched a price war."
- **Question** (問い / 疑問) — the implicit question the complication raises. Example: "How do we protect market share?"
- **Answer** (答え / 答案) — your thesis; the rest of the deck defends it. Example: "Focus on high-margin verticals and differentiate on product."

**When to use SCQA**: any non-memo deck opener. Slides 1–2 move the reader from "familiar ground" into "I need an answer" before the body begins.

**SCQA variants** (Minto 1987 §4.3):
- **SCAQ** — Answer before Question; use when the reader is already demanding a solution.
- **QSCA** — lead with the question; useful for keynote / dialogue formats that need to grab attention.
- MVP defaults to standard SCQA.

---

## 3. Mapping into a slide deck

| Deck element | Minto role | Concrete practice |
|---|---|---|
| Cover slide | **Answer** (主結論) | Title is the conclusion itself, not the deck name. Example: "Invest in APAC vertical expansion — $12M opportunity by 2027" instead of "2026 APAC Strategy". |
| Slide 2 (opener / executive summary) | **SCQA** | Four short paragraphs or four bullets mapped to S / C / Q / A. Can split into two slides (S+C then Q+A). |
| Agenda slide | Pyramid main branches | 3–5 sibling ideas, MECE, each mapping to a deeper section. |
| Section divider | Branch node | State which upper-level question this section answers. |
| Content slide | Evidence under a branch | One conclusion per slide plus its evidence; title carries the conclusion. |
| Closing slide | Restate Answer + CTA | Return to the Answer and name the next action. |

### Mapping diagram

```
Cover         ──► Answer (main conclusion = title)
    │
Opener        ──► SCQA (4 paragraphs / 4 bullets / 2 slides)
    │
Agenda        ──► Pyramid main branches (3–5 MECE siblings)
    │
├─ Section 1  ──► Branch A
│    ├─ slide A.1    ──► Evidence 1 for A
│    ├─ slide A.2    ──► Evidence 2 for A
│    └─ slide A.3    ──► Evidence 3 for A
├─ Section 2  ──► Branch B (MECE with A)
└─ Section 3  ──► Branch C
    │
Closing       ──► Restate Answer + CTA
```

---

## 4. Practical checklist (run after drafting)

After drafting the deck outline, run these seven checks:

- [ ] **Cover is the Answer, not the deck name** — read the cover title alone; can you state the main conclusion? If it only says "2026 Q2 Review", it fails.
- [ ] **One conclusion per slide** — a slide with two conclusions dilutes both and forces the reader to pick. Split it.
- [ ] **Title reads standalone** — the title should be understandable without the speaker's narration or the chart. It is the micro-Answer of that slide.
- [ ] **Sibling slides are MECE** — siblings under one agenda branch are mutually exclusive and together cover the branch. Ask "what else did I expect that is not here?"
- [ ] **Vertical Q&A holds** — each slide title answers a question raised one level above. If no upper question fits, the slide is probably an orphan.
- [ ] **Horizontal logic is consistent** — siblings use **deduction** (premise chain) or **induction** (case aggregation), not both in the same section.
- [ ] **Opener is SCQA, not self-intro** — slides 1–2 move the reader to "I need the Answer". Do not start with "Hi, I'm X".

---

## 5. Common mistakes and fixes

| Mistake | Symptom | Fix |
|---|---|---|
| Cover uses deck name | Title: "2026 Q2 Strategy Review" | Rewrite as a conclusion: "Shift 40% of engineering to APAC vertical" |
| Supporting ideas overlap | A slide in branch A restates a slide in branch B | Redraw the pyramid; promote to a common parent or delete the duplicate |
| Slide title names a topic, not a conclusion | Title: "Revenue breakdown" | Rewrite as a conclusion: "APAC is 45%, driving Q1 growth" |
| SCQA question is too broad | Four slides of setup, reader still does not know the deck's question | Trim S and C to one line each; let the Question fall out of the Complication |
| Horizontal deduction and induction mixed | Three agenda sections use case-list / if-then / mixed | Pick one; business decks usually prefer induction (case → pattern) |

---

## 6. Narrative patterns beyond Minto (reference only)

Minto 1987 is the MVP anchor. Three other patterns come up in requests — these are **noted here for recognition** but not expanded in MVP (see SKILL.md Phase 2+ extensions):

- **Hero's journey** (英雄の旅 / 英雄之旅) — Duarte (2010) *Resonate*. Fits keynote / pitch decks where the audience is meant to feel the stakes.
- **Zen-style minimalism** (禅スタイル / 禪式極簡) — Reynolds (2019) *Presentation Zen* 3rd ed. Minimal-visual design for talks where the speaker carries the narrative.
- **Takahashi method** (高橋メソッド / 高橋方法) — Takahashi Masayuki, 2005–. Single large phrase per slide; common in Japanese technical talks.

### Utterance triggers for narrative patterns

- **Pyramid / top-down** (ピラミッド / トップダウン / 金字塔 / 由上而下)
  - EN: "conclusion first", "top-down", "pyramid"
  - JP: 「結論から」「ピラミッド」「トップダウン」
  - ZH: 「結論先行」「金字塔」「由上而下」
- **SCQA opener** (SCQA 導入 / SCQA 開場)
  - EN: "how do I open", "set up the problem", "SCQA"
  - JP: 「導入の組み立て」「問題提起」「SCQA」
  - ZH: 「開場怎麼鋪」「問題鋪陳」「SCQA」
- **Hero's journey** (英雄の旅 / 英雄之旅)
  - EN: "story arc", "hero's journey", "pitch narrative"
  - JP: 「物語構成」「英雄の旅」「ピッチの流れ」
  - ZH: 「故事弧」「英雄之旅」「pitch 敘事」

MVP defaults to Minto + SCQA, which already covers ≥ 80% of business / weekly-report / proposal decks.

---

## 7. Primary source and extensions

**MVP anchor**: Minto (1987) *The Pyramid Principle*.

**Phase 2+ deep-dive references** (trigger-gated; see SKILL.md Phase 2+ extensions):
- Duarte (2010) *Resonate* — hero's-journey narrative for keynote / pitch decks.
- Reynolds (2019) *Presentation Zen* 3rd ed. — minimalist visual principles.
- Takahashi Masayuki — Takahashi method, canonical in Japanese technical communities.
