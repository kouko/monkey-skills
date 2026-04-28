# Stage 1 — Five parallel sub-agent extractors

## Goal

Don't read the book once from a single perspective. Instead, **scan the
whole book simultaneously from 5 different angles** to maximize coverage
of candidate units.

## Why parallel

- **Coverage**: a single perspective misses things. The framework
  extractor won't find a counter-example; the counter-example extractor
  will.
- **Speed**: Claude Code's `Agent` tool supports parallel sub-agent
  spawning. Use it.
- **Independence**: each extractor judges independently to avoid
  cross-pollution. Triple Verification's V1 (cross-domain) only works
  if sightings are genuinely independent.

## The 5 sub-agents

Each sub-agent receives:
- `BOOK_OVERVIEW.md` (Stage 0 output, for global context)
- The chapter markdown directory path (`$TSUNDOKU_MARKDOWN_DIR/<slug>/`)
- The corresponding extractor prompt (`extractors/<type>-extractor.md`)

Spawn all five **in a single Agent tool call with multiple invocations**
— do NOT run them sequentially.

| # | extractor | finds | writes |
|---|---|---|---|
| 1 | `framework-extractor` | mental models / decision frameworks / reasoning structures | `candidates/frameworks.md` |
| 2 | `principle-extractor` | principles / checklists / always-never rules / maxims | `candidates/principles.md` |
| 3 | `case-extractor` | author's documented applications | `candidates/cases.md` |
| 4 | `counter-example-extractor` | author-warned failure modes / traps | `candidates/counter-examples.md` |
| 5 | `glossary-extractor` | key terms with author-specific usage | `candidates/glossary.md` |

## Minimum required fields per candidate unit

Regardless of extractor, every candidate must include:

```yaml
id: f01                           # type prefix + sequence number
title: Inversion Thinking         # short label, in source language
type: framework                   # framework / principle / case / counter-example / term
source_chapter: Chapter 3         # verbatim from book's chapter labels
source_quote: |                   # verbatim source quote, ≤150 chars
  "Invert, always invert..."
summary: |                        # in your own words, 5-10 lines, source language
  ...
tags: [decision, mental-model]    # for downstream linking
```

## Output language for Stage 1

- `title`, `summary`, `source_quote` — match source book language
  (`source_quote` always verbatim)
- YAML field names (`id`, `title`, `type`, etc.) — English
- `tags` — English (machine-parseable taxonomy)
- File names (`frameworks.md`, etc.) — English

## Self-checks before each extractor submits

1. Is this unit grounded in the book? (Not paraphrased from training data)
2. Does it belong to MY job? (Don't trespass on other extractors' turf)
3. Has another extractor likely already found it? (Duplicates are fine —
   Stage 1.5 deduplicates)

## What NOT to do at Stage 1

- **Do not filter** — over-extract; let Stage 1.5 verify
- **Do not write SKILL.md** — only candidates, no full skills yet
- **Do not link units to each other** — that's Stage 3's job

## Quantity expectation per book

| Book type | frameworks | principles | cases | counter-examples | glossary |
|---|---|---|---|---|---|
| Methodology-dense (e.g. Munger) | 10-30 | 15-40 | 20-50 | 10-25 | 5-15 |
| Narrative non-fiction | 3-10 | 5-15 | 30-100 | 5-15 | 3-10 |
| Essay collection | 2-8 | 5-15 | 5-20 | 3-10 | 2-8 |
| Technical reference | 5-15 | 20-50 | 5-20 | 10-30 | 10-30 |

If your numbers are an order of magnitude off, suspect either: extractor
is broken, or this book isn't really methodology-dense (consider
rejecting before Stage 1.5).

## Trilingual glossary (Stage 1 — extraction)

| English | 日本語 | 繁體中文 | Note |
|---|---|---|---|
| candidate unit | 候補項目 | 候選條目 | NOT 候補単位 / 候選單元 — 単位/單元 carry wrong sense (physical unit / module) |
| extractor (sub-agent) | 抽出器 | 提取器 | software/research register |
| over-extract | 過剰抽出 | 過度提取 | 寧錯殺 is the principle name |
| trespass (cross extractor turf) | 越境 | 越界 | |
| dedupe | 重複排除 | 去重 | |
