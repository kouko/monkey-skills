# Stage 2 — RIA++ skill render

## Goal

For each unit that passed Stage 1.5, construct a Claude Code-compliant
`SKILL.md` using the six-section RIA++ schema.

Template: `templates/SKILL.md.template`.

## RIA++ six sections

### R — Reading (original quote)

- Verbatim source quote, ≤150 chars
- Must include a chapter / section / page citation
- If the source is in language X, the quote stays in language X — DO NOT
  translate. (Translation is the I section's job.)

### I — Interpretation (your own paraphrase)

- Rewrite the methodology's skeleton **in your own words**
- 5-15 lines
- **Self-check**: after reading the I section alone, can someone who
  hasn't read the source book understand what the methodology does? If
  no, rewrite.
- **Forbidden**: copying source phrasing; piling on rhetoric;
  paraphrasing line-by-line. The point is to compress and clarify, not
  echo.

### A1 — Past Application (book-cited examples)

- Cases the author **personally** applied this methodology to (or
  cases the author analyzed in detail)
- ≥1, ≤3 cases
- For each: problem encountered → how the methodology was applied →
  conclusion reached → actual outcome

This section gives the agent concrete analogues at runtime, so when the
skill is invoked the agent can pattern-match against precedent.

### A2 — Future Trigger ★ (the most critical section)

**This is what determines whether the skill ever gets invoked.**

Must specify:

1. **In what scenarios will the user need this?** (3-5 concrete situations,
   not abstractions)
2. **What language signals will the user actually use?** (real phrasings)
3. **How does this differ from neighboring skills?** (avoid trigger
   collisions)

A2's content goes directly into frontmatter `description` — Claude reads
that to decide whether to activate the skill.

**Good A2 example** (for an "inversion thinking" skill):
> Activate when: the user is wrestling with a decision, listing pros but
> not converging; or asking "how do I make X succeed?" Do NOT activate
> for: information lookup queries, daily trivia decisions.

**Bad A2 example**:
> Activate when the user needs to think. ← Too broad; will fire on
> everything.

### E — Execution (numbered runtime steps)

- Convert the methodology into 1-2-3 numbered steps
- Each step has a **verifiable completion criterion**
- If there's a halt condition (e.g. "after step 2, if X then jump to
  step 5"), state it explicitly

E gives the agent a deterministic execution path, not "freelancing".

### B — Boundary (when NOT to use)

- **Anti-scenarios**: "do not use when..."
- **Author-warned failure modes** (sourced from Stage 1's
  counter-example extractor)
- **Author blind spots** (sourced from Stage 0's Critical step)
- **Adjacent methodologies easily confused** (e.g. distinguish from
  the neighboring `forward-reasoning` skill)

B prevents the agent from over-firing the skill. A skill without B will
be invoked at the wrong time and degrade trust.

## Frontmatter design

```yaml
---
name: <skill-slug>                # kebab-case, English, machine identifier
description: |                    # condensed A2, ≤300 chars
  <when to use + when NOT to use + key trigger signals>
  In source-book language so user queries match natural triggers.
source_book: <Book Title> — <Author>      # frontmatter labels English; values verbatim
source_chapter: <chapter label verbatim>
tags: [decision, mental-model, ...]       # English (machine taxonomy)
related_skills: []                        # filled by Stage 3
---
```

## Output language for Stage 2 — full table

| Section | Language |
|---|---|
| `name` (slug) | English kebab-case |
| `description` | match source book language |
| `source_book` field key | English; value: title verbatim, "—" separator, author verbatim |
| `source_chapter` value | verbatim source |
| `tags` | English |
| H1 title | match source language; verbatim from `title` |
| **R section** body | verbatim source quote |
| **I section** body | match source language |
| **A1 section** body | match source language |
| **A2 section** body | match source language (so user query patterns match) |
| **E section** body | match source language |
| **B section** body | match source language |
| Audit footer (V1 ✓ / V2 ✓ / V3 ✓ / dates) | English |

## Common failure modes

1. **I reads as a book summary** — if it's "the author tells us X", you're
   transcribing, not interpreting. Rewrite.
2. **A2 too vague** — "when making decisions" never matches precisely.
   You must give recognizable language signals.
3. **E is philosophy, not action** — "stay objective" is not a step;
   "list 3 outcomes you most don't want" is.
4. **B missing** — without it, the skill over-fires. Always populate
   from the Stage 1 counter-example pool + Stage 0 critique.
5. **Skipping A1, going I → E directly** — without "the author actually
   applied this to X", the skill loses authority.

## Trilingual glossary

| English | 日本語 | 繁體中文 |
|---|---|---|
| paraphrase | 自分の言葉で言い換える | 自家話重述 |
| trigger signal | トリガー信号 | 觸發信號 |
| halt condition | 停止条件 / 中断条件 | 判停條件 |
| anti-scenario | 反シナリオ / 不適用例 | 反場景 |
| over-firing | 過剰発火 | 過度調用 / 亂激活 |
