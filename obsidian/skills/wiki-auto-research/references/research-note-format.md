# Auto-Research Note Format

Output of `wiki-auto-research` lands in `<vault-root>/research/` as one note per research session. The notes carry the `generated_by: wiki-auto-research` marker so they're distinguishable from hand-written research, and so re-running auto-research won't double-cover questions already answered.

## Filename

```
<vault-root>/research/YYYY-MM-DD <topic-slug>-auto-research.md
```

- `YYYY-MM-DD` — today's date in ISO format
- `<topic-slug>` — short slug derived from the primary question topic (e.g., `MAB-2025-empirical`)
- `-auto-research` suffix — distinguishes from manual research notes

## Frontmatter

```yaml
---
title: "Human-readable research topic"
type: research
generated_by: wiki-auto-research          # MUST: marks as auto-generated
date: YYYY-MM-DD
tags:
  - auto-research
  - <domain-tags-from-source-page>
source_questions:                          # MUST: questions this note answers
  - "Question text exactly as it appeared in Open Questions"
  - "Another question"
source_pages:                              # MUST: wiki pages that surfaced these questions (bare filename only)
  # These STAY as `[[wikilinks]]` — the pages already exist by construction
  # (they surfaced the Open Questions being researched), so they are NOT dangling.
  - "[[Thompson-Sampling]]"
  - "[[exploration-exploitation]]"
search_queries_used:                       # for audit / reproducibility
  - "Thompson Sampling 2025 empirical results"
  - "MAB performance benchmarks 2024-2025"
status: pending-review                     # pending-review | reviewed-accept | reviewed-reject
---
```

## Body structure

```markdown
## Question

> Verbatim question copied from the source wiki page's Open Questions section.

## Answer Synthesis

2–4 paragraphs synthesizing what was found across web searches.

- Lead with the bottom-line answer
- Note where sources disagree
- Note confidence (high / medium / low)

## Sources

Web sources cited, with URLs and a 1-line context per source:

- [Source title](https://...) — what this contributed
- [Source title](https://...) — ...

## Recommended wiki updates

What to update in the wiki when this research is accepted:

- Update `[[Thompson-Sampling]]` `## Key Facts`:
  - Add: "...new fact..." (cite [Source 2])
- Update `[[Thompson-Sampling]]` `## Open Questions`:
  - REMOVE: "Question that was answered above"
- (Optional) Create new page: `new-concept` — written as plain text / inline code, NOT a `[[wikilink]]`, because the page does not exist yet (emitting `[[new-concept]]` here is what leaks a dangling link into `research/`). `wiki-ingest` creates the page; once it exists, `wiki-cross-linker` promotes mentions to links.

## Reviewer notes

(Empty — for the human reviewer to fill in before /wiki-ingest)
```

## Per-question vs. per-topic batching

A single note can answer **multiple related questions** if they share a topic. Don't fragment one cluster of related questions into 5 tiny notes.

Bundle questions when:
- They appear on the same source wiki page
- They share a domain or are part of the same research thread
- A single set of web searches can answer all of them

Split questions when:
- They cover materially different topics
- Bundling would inflate the note past ~1500 words

## Status field lifecycle

```
pending-review        ← initial, set by wiki-auto-research
   ↓ user reviews
reviewed-accept       ← user agrees with synthesis, wants to ingest
reviewed-reject       ← user rejects (low source quality, off-target, etc.)
```

`wiki-ingest` only ingests notes with `status: reviewed-accept`. Notes with `pending-review` or `reviewed-reject` are skipped.

This decouples auto-research from the wiki — the user is the gate, not the auto-research skill.

## Idempotence — how re-runs avoid duplicating work

`wiki-auto-research` MUST check existing `research/*-auto-research.md` notes before launching a new search:

1. Build set of all `source_questions` across existing auto-research notes (any status)
2. For each candidate Open Question in the wiki, check membership in that set
3. Skip questions already covered

Exception: user can pass `--force <question>` to re-research a specific question (e.g., when sources have changed or initial research was rejected).

## Why output to `research/` and not `wiki/` directly

- Separates **gathering** (auto) from **distillation** (manual review + `/wiki-ingest`)
- Lets the user audit source quality before knowledge enters the wiki
- Reuses the existing manual-research workflow
- The `generated_by` marker preserves provenance after `/wiki-ingest`

## What the user does after wiki-auto-research

1. Open the generated note(s) in `research/`
2. Review synthesis and source quality
3. Edit if needed, set `status: reviewed-accept`
4. Run `/wiki-ingest` (typically with "Research notes only" scope) to merge findings into the wiki
5. The corresponding Open Questions are removed by `/wiki-ingest` based on the `Recommended wiki updates` block

> `/wiki-ingest` consumes the `Recommended wiki updates` block by *reading* it (STEP 4 `Read` + interpret the body — no regex parser keyed off `[[...]]` syntax). The non-link `` `new-concept` `` form above is read identically: the agent follows the human-language "Create new page:" instruction and the inline-code page name, so dropping the brackets does not break ingestion. Page-existence and category routing are decided downstream by `/wiki-ingest`'s own uniqueness check (STEP 4 §Filename uniqueness check), not by whether this bullet was a wikilink.
