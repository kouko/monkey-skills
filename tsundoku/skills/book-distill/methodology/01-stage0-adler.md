# Stage 0 — Whole-book comprehension (Adler analytical reading)

## Goal

**Read the book properly before extracting anything.** Without this, the
distilled skills are just a quote collection — they'll inherit the
author's blind spots without you noticing.

**Output**: `<distill-dir>/BOOK_OVERVIEW.md` (filled from
`templates/BOOK_OVERVIEW.md.template`).

## Four steps (first three are Adler's; step 4 is RIA-TV++'s addition)

### Step 1 — Structural

Identify the book's skeleton. Answer:

- **What kind of book is this?** (methodology / biography / philosophy /
  practical manual / ...)
- **What is the thesis in one sentence?** — must actually compress to one
- **How do the major parts compose into a whole?** — list 3-7 top-level
  arguments and label their relations (parallel / progressive /
  contrasting / refuting)
- **What problem is the author trying to solve?**

### Step 2 — Interpretive

- **Key terms (author's usage)**: list concept words the author repeatedly
  uses with a specific meaning. For each, write a one-line definition
  IN THE AUTHOR'S USAGE — not a dictionary definition
- **Core propositions**: restate 5-15 of the author's main claims in your
  own words
- **Argument chain**: how do these claims derive from each other? What
  evidence supports each?

### Step 3 — Critical ★ MOST OFTEN SKIPPED, MOST IMPORTANT

Adler's rule: *"You must not disagree with the author until you have
identified errors in the argument."* Inverse: **you must not fully agree
until you have identified the author's limits.**

You must answer:

- **Period limitations**: when was this written? Which premises may no
  longer hold?
- **Stance blind spots**: what does the author's identity / industry /
  cultural background cause them to miss?
- **Unproven assumptions**: what does the author treat as self-evident
  but actually requires argument?
- **Strongest opposing view**: if someone wanted to refute this book,
  what would their best argument be?

This step's output **directly populates the Boundary (B) field** of
every downstream skill. **If you skip this, every skill will be brittle.**

### Step 4 — Applicability (RIA-TV++ extension)

- **What's distillable as skills?** — frameworks / checklists /
  principles / decision procedures
- **What's NOT distillable?** — pure historical narrative / pure stories /
  pure emotion (these can serve as `example` material in other skills,
  but can't stand alone)
- **Estimated skill count**: give a rough range; don't pad
- **Priority ordering** (for "most empowering to ordinary users"
  perspective): rank candidate skills

## Quality gate (cannot proceed to Stage 1 unless ALL met)

- [ ] Thesis compresses to one sentence
- [ ] Skeleton has 3-7 top-level arguments
- [ ] Key-terms dictionary has ≥5 entries
- [ ] Critical phase has ≥3 author limits identified
- [ ] BOOK_OVERVIEW.md shown to user, confirmation received

## Output language rule for Stage 0

- BOOK_OVERVIEW.md content (sections 1-4 substance) — **match source book
  language**
- BOOK_OVERVIEW.md frontmatter / structural labels (e.g. "Step 1 —
  Structural") — keep English headers; fill body content in source
  language
- Author quotes — verbatim source language, no translation
- Audit metadata (timestamps, gate checkboxes) — English

Example: a Japanese book → BOOK_OVERVIEW.md has English section headers
("## 1. Structural"), but the actual thesis sentence, propositions,
critique are written in Japanese.

## Common failure modes

1. **Skipping the Critical step** — leads to skills that treat author
   bias as truth
2. **The skeleton is YOUR ideas, not the AUTHOR'S** — are you writing a
   summary or a book review? Stage 0 wants the former.
3. **Term definitions are dictionary / common-sense, not author's usage**
   — Munger's "circle of competence" is NOT what the dictionary says.
   The whole point of the term in his system is the gap from common
   usage.
4. **One-sentence thesis cheating** — concatenating three claims with
   semicolons isn't "one sentence"; it's an outline. Compress further.

## Trilingual glossary

| English | 日本語 | 繁體中文 |
|---|---|---|
| thesis | テーゼ / 主旨 | 主旨 / 中心論點 |
| skeleton | 骨格 | 骨架 |
| proposition | 命題 | 命題 |
| blind spot | 盲点 | 盲點 |
| argument chain | 論証の鎖 | 論證鏈 |
| applicability | 応用可能性 | 應用潛力 |
