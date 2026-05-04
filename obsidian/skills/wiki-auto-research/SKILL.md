---
name: wiki-auto-research
description: Scan wiki/ for Open Questions and ambiguous claims; web-search gaps; write reviewable notes to research/ with generated_by marker. Manual one-shot. Do NOT use for general web research (use WebSearch). Obsidian wiki 知識穴埋め・知識補完・自動調査。
---

# Wiki Auto-Research — Fill Knowledge Gaps via Web Search

Scans the wiki for unanswered questions and low-confidence claims, runs targeted web searches, and writes structured research notes to `research/` for user review. Notes are NOT automatically merged — the user reviews and runs `/wiki-ingest` to integrate.

See [research-note-format.md](references/research-note-format.md) for the output contract.

## Trigger model

> [!important]
> This skill is **manual one-shot**. It does NOT auto-fire. It does NOT loop. It does NOT chain into `/wiki-ingest`. Each run is bounded and produces reviewable artifacts.

## Pre-flight

1. Read `.obsidian-wiki.config` for `OBSIDIAN_WIKI_VAULT_PATH` (defaults `wiki/`). If only legacy `.env` exists, instruct user to run `/wiki-setup` to migrate.
2. **Check `WebSearch` tool availability** — this skill is useless without it. Verify by:
   - Inspecting the tool list in this session (look for `WebSearch` in the available tools)
   - If absent, exit with this message:
     ```
     wiki-auto-research requires the WebSearch tool, which is not available in this session.

     Likely cause: this skill is running in a sandboxed environment (e.g., Cowork)
     where outbound URL fetches are blocked.

     Run this skill from Claude Code CLI, or use a different approach:
     - Hand-research the question and update wiki/ pages directly
     - /wiki-ingest after you write a manual research note
     ```
3. Confirm `<vault-root>/research/` exists; create with `mkdir -p` if missing.

## STEP 1 — Identify candidate gaps

Scan all wiki pages for:

### Open Questions
Body sections under `## Open Questions`. Each bullet is one candidate question.

### Low-confidence claims
- `## Key Facts` bullets ending in `^[ambiguous]` — these flag where sources disagree
- `## Summary` ending in `Confidence: unverified` — page-level low confidence
- `frontmatter.status: seed` pages older than 30 days — likely stalled at seed

### Contradictions
Pages with `## Contradictions` sections — research can adjudicate.

## STEP 2 — Filter by idempotence

For each candidate question:

1. Read all existing `research/*-auto-research.md` notes
2. Collect their `source_questions:` frontmatter values (any status, including pending-review)
3. **Skip** any candidate question that's already in that set

Unless user passes `--force <topic>` to override.

This prevents re-researching already-covered ground.

## STEP 3 — Show plan, get user OK

```
Found 12 unique gaps:

PRIORITY (with explicit Open Questions):
  1. entities/Thompson-Sampling — "Are there 2025 empirical benchmarks?"
  2. concepts/exploration-exploitation — "How does context-free MAB compare to contextual?"
  3. ...

LOW-CONFIDENCE (ambiguous facts):
  4. entities/qlib — Key Fact about supported brokers is ^[ambiguous]
  ...

CONTRADICTION:
  9. synthesis/finance-ai — "Source A says X; Source B says Y"

I'll batch related questions into research notes (likely 6–8 notes total).
Estimated web searches: ~25 (3–5 per topic cluster).

Proceed? (yes / select-specific / skip)
```

Wait for user response. Respect "select-specific" by asking which to research.

## STEP 4 — Cluster & batch

Group related questions into topic clusters per [research-note-format.md](references/research-note-format.md) "Per-question vs. per-topic batching" rules:
- Same source page → same cluster
- Same domain + thread → same cluster
- Single set of web searches answers them → same cluster

Each cluster becomes one research note.

## STEP 5 — Per-cluster research loop

For each cluster:

### 5a. Plan searches
Draft 3–5 targeted web search queries. Vary phrasing to surface different angles. Record queries for the note's `search_queries_used:` field.

### 5b. Execute searches
Use `WebSearch`. Record URLs, titles, key passages.

### 5c. Synthesize
Per [research-note-format.md](references/research-note-format.md):
- Lead with bottom-line answer
- Cite sources inline
- Note confidence + disagreements
- Recommend specific wiki updates

### 5d. Write the note
Output to `<vault-root>/research/YYYY-MM-DD <topic-slug>-auto-research.md` with full frontmatter (`generated_by: wiki-auto-research`, `status: pending-review`).

### 5e. Pause if scope is large
After every ~3 notes, give the user a progress update and option to pause:

```
Done with 3 of 8 clusters. Continue? (continue / pause)
```

This prevents long unchecked runs.

## STEP 6 — Append to log and report

Append to `wiki/log.md`:

```markdown
| YYYY-MM-DD | auto-research | <N> questions across <M> clusters | research/<filename1>, research/<filename2>, ... |
```

Final report:

```
Auto-research complete:
  Questions covered:  12
  Clusters → notes:    8
  Web searches:       29

Output:
  research/2026-05-03 thompson-sampling-2025-empirical-auto-research.md
  research/2026-05-03 mab-context-comparison-auto-research.md
  ...

Next steps:
  1. Review each note (set status to reviewed-accept or reviewed-reject)
  2. Run `/wiki-ingest` with scope "Research notes only" to merge accepted notes
  3. Or hand-edit notes first, then ingest

Notes are NOT merged into wiki/ until you run /wiki-ingest.
```

## Boundaries (what wiki-auto-research does NOT do)

- ❌ Does not modify any wiki page directly (output is `research/`, requires user review + `/wiki-ingest`)
- ❌ Does not loop / auto-trigger / chain into other skills
- ❌ Does not re-research already-covered questions (idempotence via `source_questions:` set)
- ❌ Does not exceed `~5 searches per cluster` without user OK
- ❌ Does not fabricate sources — every claim cites a URL or is marked low-confidence
- ❌ Does not delete Open Questions from wiki pages (that's `/wiki-ingest`'s job after user accepts)

## Failure modes to watch

| Symptom | Likely cause | Action |
|---|---|---|
| Web search returns no relevant results | Question too narrow or jargon-heavy | Mark cluster as "research-failed" in note, note query attempts, skip |
| Sources are all blogs / no primary | Domain has poor primary literature | Lower confidence to "low" in synthesis, suggest user finds primary sources |
| Sources directly contradict each other | Active controversy | Surface both sides; recommend `## Contradictions` update rather than `## Key Facts` |
| User keeps rejecting auto-research outputs | Source quality threshold too low | Adjust by tightening searches to .gov, .edu, peer-reviewed, etc. |

## Rate limit / cost awareness

Cap per run: ~30 web searches by default. If estimated count exceeds, batch and ask user to confirm before continuing.
