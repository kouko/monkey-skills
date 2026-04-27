# RIA-TV++ Methodology Overview

Design rationale for the `book-distill` pipeline. For per-stage execution
detail, read `01-stage0-adler.md` through `06-stage4-pressure-test.md`.

## Naming

**RIA-TV++** =
- **RIA** — 趙周's note-taking method from *《這樣讀書就夠了》*
  (Reading / Interpretation / Appropriation)
- **TV** — Triple Verification, adapted from
  [nuwa-skill](https://github.com/alchaincyf/nuwa-skill)
- **++** — agent-execution extensions: **E** (Execution steps) +
  **B** (Boundary)

## Intellectual lineage

| Source | Borrowed |
|---|---|
| Mortimer Adler — *How to Read a Book* | Stage 0: analytical reading (Structural / Interpretive / Critical) |
| 趙周 — RIA note-taking | Stage 2: R / I / A1 / A2 base schema; A2 → trigger insight |
| Niklas Luhmann — Zettelkasten | Atomicity + linking + "rewrite in your own words" |
| Tiago Forte — Progressive Summarization | Stage 4: verifiable compression chain |
| nuwa-skill | Stage 1 parallel extractors + Stage 1.5 triple verification |
| cangjie-skill | The whole pipeline (this is an English fork) |

## Core insight

> **Existing reading methodologies were designed to distill books for
> human readers, not for agent executors.**

| Dimension | For human reading | For agent execution (book-distill goal) |
|---|---|---|
| Key fields | story / quotable lines / emotional hook | trigger / executable steps / halt criteria |
| Failure mode | "I read it and forgot" | "trigger imprecise → never invoked or wrongly invoked" |
| Success criterion | reader feels enriched | a real problem gets solved |

Every "++" extension (TV / E / B / test-prompts) exists to address the
problems caused by retargeting from "reader" to "agent".

## Pipeline diagram

```
        ┌────────────────────────┐
        │ Stage 0: whole-book    │  Adler four-step
        │ comprehension          │
        └────────┬───────────────┘
                 │ BOOK_OVERVIEW.md
                 ▼
        ┌────────────────────────┐
        │ Stage 1: parallel      │  5 sub-agents in parallel
        │ extraction             │
        └────────┬───────────────┘
                 │ candidates/
                 ▼
        ┌────────────────────────┐
        │ Stage 1.5: triple      │  V1 cross-domain /
        │ verification filter    │  V2 predictive /
        │                        │  V3 exclusivity
        └────────┬───────────────┘
                 │ verified.md + rejected/
                 ▼
        ┌────────────────────────┐
        │ Stage 2: RIA++ render  │  R / I / A1 / A2 / E / B
        └────────┬───────────────┘
                 │ <skill>/SKILL.md
                 ▼
        ┌────────────────────────┐
        │ Stage 3: Zettelkasten  │  + INDEX.md w/ ref graph
        │ linking                │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │ Stage 4: adversarial   │  test-prompts.json
        │ pressure test          │  + retry on failure
        └────────────────────────┘
```

## Invariants (no iteration may violate these)

1. **Atomicity**: one skill = one methodology unit. No "comprehensive"
   skills.
2. **Traceability**: every skill must include a source quote pointing back
   to the book chapter.
3. **Verifiability**: every skill must pass all three TV checks AND its
   pressure test.
4. **Re-runnability**: every skill ships with `test-prompts.json` so future
   evolution / regression detection has a baseline.
5. **User in the loop**: after Stage 0 you MUST show the user
   `BOOK_OVERVIEW.md` and get confirmation before continuing.

## Trilingual glossary (key methodology terms)

| English | 日本語 | 繁體中文 |
|---|---|---|
| analytical reading | 分析的読書 | 分析閱讀 |
| atomicity | 原子性 | 原子化 |
| trigger | トリガー | 觸發信號 |
| boundary | 適用境界 | 適用邊界 |
| pressure test | プレッシャーテスト | 壓力測試 |
| audit trail | 監査トレイル | 審計軌跡 |
| canonical | 標準 / 正式版 | 標準 / 規範 |
