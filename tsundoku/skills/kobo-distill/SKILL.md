---
name: kobo-distill
description: >-
  Distill a book (already converted to chunked Markdown by kobo-extract) into
  a coherent set of executable agent skills. Use when the user wants to "拆書"
  / "蒸留する" / "turn this book into skills" — i.e. extract the book's
  frameworks, principles, decision rules, and methodologies into atomic,
  reusable Claude skills that an agent can invoke in real-world situations.
  NOT for simple summarization, book reviews, or author-as-persona role-play
  (the latter belongs in a separate persona-distillation pipeline). Pipeline:
  Adler analytical read → 5 parallel extractors → triple verification → RIA++
  rendering → Zettelkasten linking → adversarial pressure test. Adapted from
  kangarooking/cangjie-skill (MIT). Language-adaptive output.
  書籍 → エージェント skill 蒸留パイプライン。書籍を skill に蒸餾。
---

# kobo-distill — Distill a book into a coherent set of executable skills

## Mission

Turn the methodology buried in a book — frameworks, principles, decision
rules, mental models, named techniques — into a set of **atomic, reusable
skills that agents can invoke in real-world situations**, so the reader
actually uses what they read.

**Boundaries**:
- ✅ Distill: methodologies / decision frameworks / checklists / principles /
  conceptual systems
- ❌ Skip: book summaries / book reviews / author-persona role-play (the last
  is a separate concern; see ATTRIBUTION.md → nuwa-skill)

## Core methodology: RIA-TV++

A 4-stage + parallel-extract + triple-verify + adversarial-test pipeline.

```
Stage 0: Adler analytical read           → BOOK_OVERVIEW.md
Stage 1: 5 parallel sub-agent extractors → candidate pool
Stage 1.5: Triple verification filter    → verified units (~30-50% pass)
Stage 2: RIA++ render per skill          → SKILL.md per unit
Stage 3: Zettelkasten linking            → INDEX.md + cross-refs
Stage 4: Adversarial pressure test       → test-prompts.json + retry
```

See `methodology/00-overview.md` for the design rationale; `methodology/01-*`
through `06-*` for per-stage details.

## Output language rule (READ FIRST)

This skill is language-adaptive. Source books may be in English / Japanese /
Traditional Chinese / Simplified Chinese / mixed. Per-field rules:

| Field | Language |
|---|---|
| **R (Reading) — original quotes** | VERBATIM source language; NEVER translate |
| **I (Interpretation), A1, A2 trigger signals, E, B** | Match source book's primary language |
| **YAML field names** (id, title, type, etc.) | English (machine-parsed) |
| **frontmatter `description`** | Match A2 trigger signal language (so Claude's activation matches user queries) |
| **frontmatter `name`** (slug) | English kebab-case (machine identifier) |
| **`source_chapter`** | Verbatim from book's chapter labeling |
| **audit metadata** (rejected reasons, V1/V2/V3 notes) | English (maintainer-facing) |

Rationale: instructions stay in English for portability, but the OUTPUT
(skills users will load) speaks the language of the source so A2 trigger
signals match natural user queries.

## Trilingual glossary — RIA-TV++ key terms

For cross-language readers; extractors and methodology files repeat the
relevant subset.

| English | 日本語 | 繁體中文 | Definition |
|---|---|---|---|
| **framework** | フレームワーク | 框架 | a transferable thinking structure (e.g. inversion, OODA) |
| **principle** | 原則 | 原則 | an "always / never / only when X" rule |
| **case** | 事例 | 案例 | author's documented application of a methodology |
| **counter-example** | 反例 | 反例 | failure mode the author explicitly warns about |
| **mental model** | メンタルモデル | 心智模型 | a stable representation of how X works |
| **decision rule** | 意思決定ルール | 決策規則 | an if-then heuristic for runtime |
| **trigger** | トリガー | 觸發信號 | a user-query pattern that should activate a skill |
| **boundary** | 境界 / 適用範囲 | 邊界 / 適用範圍 | when NOT to use the skill |
| **inversion** | 反転思考 | 逆向思維 | "what would cause failure?" instead of "how to succeed?" |
| **circle of competence** | 自分の理解圏 | 能力圈 | the boundary of where your judgment beats market average |

## When to invoke this skill

User says something like:
- "Distill *Poor Charlie's Almanack* into skills"
- "把《思考的快與慢》蒸餾成 skill"
- "この本の方法論を skill にして"
- "Turn this book's frameworks into reusable skills"

## Pre-conditions (HARD GATES — verify before starting)

1. **Book has been processed by kobo-extract.** Required artifacts:
   - `$TSUNDOKU_MARKDOWN_DIR/<slug-id8>/index.md`
   - `$TSUNDOKU_MARKDOWN_DIR/<slug-id8>/metadata.json`
   - `$TSUNDOKU_MARKDOWN_DIR/<slug-id8>/NN-chapter.md` (chapters)
   - If absent, route the user to **`kobo-library` → `kobo-extract`** first.
   - **Do NOT distill from memory** — stop and ask the user for the book.
2. **First-time pilot signal.** If this is the user's first time using
   `kobo-distill`, recommend processing **one book** to validate the pipeline
   before any batch run.

## Output structure

```
${TSUNDOKU_ROOT}/cache/distilled/<book-slug>/
├── BOOK_OVERVIEW.md            # Stage 0 output: thesis / skeleton / glossary / critique
├── INDEX.md                    # Stage 3 output: skill overview + reference graph
├── candidates/                 # Stage 1 raw candidate pool (audit trail)
│   ├── frameworks.md
│   ├── principles.md
│   ├── cases.md
│   ├── counter-examples.md
│   └── glossary.md
├── rejected/                   # Stage 1.5 cuts + reasons (audit trail)
│   └── <id>.md
├── verified.md                 # Stage 1.5 survivors
├── <skill-slug-1>/
│   ├── SKILL.md                # RIA++ render
│   └── test-prompts.json       # Stage 4 test cases
├── <skill-slug-2>/
└── ...
```

## Execution flow (strict order)

### Stage 0 — Whole-book comprehension

1. Resolve the book's markdown directory:
   ```bash
   bash ${CLAUDE_SKILL_DIR}/scripts/kobo_distill_init.sh <book-slug-id8>
   # writes: $TSUNDOKU_ROOT/cache/distilled/<book-slug>/{BOOK_OVERVIEW.md.template, metadata.snapshot.json}
   ```
2. Read `metadata.json` and all `NN-chapter.md` files in order. For very
   large books (>100K tokens total), read chapter-by-chapter; do NOT
   skim.
3. Execute Adler four-step procedure per `methodology/01-stage0-adler.md`
   (Structural / Interpretive / Critical / Applicability).
4. Fill `templates/BOOK_OVERVIEW.md.template` and write to
   `<distill-dir>/BOOK_OVERVIEW.md`.
5. **Show the user the BOOK_OVERVIEW** and ask: "Did I read the skeleton
   correctly? Anything you want emphasized?" Wait for confirmation
   before Stage 1.

### Stage 1 — Five parallel sub-agent extractors

Spawn 5 `Agent` tool calls **in parallel** (single message, multiple tool
uses):

| sub-agent | reads | writes |
|---|---|---|
| Framework Extractor | `extractors/framework-extractor.md` + book | `candidates/frameworks.md` |
| Principle Extractor | `extractors/principle-extractor.md` + book | `candidates/principles.md` |
| Case Extractor | `extractors/case-extractor.md` + book | `candidates/cases.md` |
| Counter-Example Extractor | `extractors/counter-example-extractor.md` + book | `candidates/counter-examples.md` |
| Glossary Extractor | `extractors/glossary-extractor.md` + book | `candidates/glossary.md` |

Each sub-agent gets:
- `BOOK_OVERVIEW.md` (Stage 0 output, for global context)
- The chapter markdown directory path
- The output language rule (above)

Sub-agents work **independently** to avoid cross-pollution; Triple
Verification's V1 (cross-domain) requires independent sightings.

### Stage 1.5 — Triple verification filter

Per `methodology/03-stage1.5-triple-verify.md`:

For each candidate unit, evaluate three checks:

- **V1 Cross-domain**: Does the book independently support this in ≥2
  contexts (different chapters / different objects / different
  conclusions)?
- **V2 Predictive power**: Can you use this unit to answer a NOVEL
  question (one the book doesn't explicitly address)?
- **V3 Exclusivity**: Is this *not* common-sense any smart person would
  state?

All three must pass. Survivors → `verified.md` → Stage 2. Failures →
`rejected/<id>.md` with explicit reason recorded (audit + recoverable).

Pass-rate expectation: 30-50% for methodology-dense books, 5-10% for
essay/narrative books. <5% or >80% suggests a calibration problem.

### Stage 2 — RIA++ skill render

Per `methodology/04-stage2-ria-plus.md`, fill `templates/SKILL.md.template`
for each verified unit:

- **R (Reading)**: original quote ≤150 chars, with chapter citation
- **I (Interpretation)**: methodology skeleton in your own words, 5-15 lines
- **A1 (Past Application)**: cases the author personally applied
- **A2 (Future Trigger)** ★: when will the user need this skill? this becomes
  the frontmatter `description`
- **E (Execution)**: numbered runtime steps with completion criteria
- **B (Boundary)**: when NOT to apply, sourced from Stage 0 critique +
  counter-examples

### Stage 3 — Zettelkasten linking

Per `methodology/05-stage3-zettelkasten.md`:

1. Find inter-skill relations: `depends-on` / `contrasts-with` /
   `composes-with`
2. Append "Related skills" section to each `SKILL.md`
3. Generate `INDEX.md` with mermaid reference graph

Discipline: **don't manufacture links**. A 10-skill book usually has 8-15
real relations. Sparser is fine; >25 means you're stretching.

### Stage 4 — Adversarial pressure test

Per `methodology/06-stage4-pressure-test.md`:

1. Design ≥6 test prompts per skill: ≥3 `should_trigger` + ≥2
   `should_not_trigger` (lures) + ≥1 `edge_case`. Lures are
   non-negotiable.
2. Run each test as an independent activation judgment.
3. Pass criteria:
   - 100% → ship
   - ≥80% → analyze failures; decide fix-skill vs fix-test (be skeptical
     of fix-test — risk of self-justification)
   - <80% → **redo Stage 2 A2/E/B**, not surface patches

## Quality red lines (block output if violated)

1. Every shipped skill must pass **all three** Triple Verification checks
2. Every shipped skill must have all six fields R / I / A1 / A2 / E / B
3. Every R quote ≤150 chars, with chapter citation
4. Every shipped skill must have a `test-prompts.json` containing lures
5. Frontmatter `description` must specify trigger conditions, not
   "a skill about X"
6. Output language rule must be honored (R verbatim source; I/A/E/B
   match source language)

## Calling conventions

- **Always pilot one book first** — unless the user explicitly says
  "batch"
- **Report progress between stages** — don't run silently and dump at
  the end
- **Never distill from memory** — if `metadata.json` is missing, stop and
  route to `kobo-extract`
- **Preserve audit trail** — keep `candidates/` and `rejected/`; don't
  delete to "clean up"

## Cross-skill placement in tsundoku

| skill | role |
|---|---|
| `kobo-auth` | one-time login |
| `kobo-library` | search + download EPUBs |
| `kobo-extract` | EPUB → chunked Markdown |
| **`kobo-distill`** (this) | **Markdown → atomic skill set** |

## Ecosystem positioning

- **kobo-distill** (this skill, books): distills *what the book teaches*
  — frameworks, decision rules
- **persona-distill** (separate, future): would distill *how a person
  thinks* — voice, mental models, biographical context
- **skill-creator-advance** (`dev-workflow:skill-creator-advance`):
  packages a hand-written skill draft into Claude Code spec; you can
  pipe a kobo-distill output through it for final QA

## Reference

- See `ATTRIBUTION.md` for upstream credits (cangjie-skill,
  nuwa-skill, Adler, Luhmann, RIA, Munger)
- See `methodology/00-overview.md` for the design rationale of every
  stage and every constraint
