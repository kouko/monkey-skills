# Tiered Retrieval — Read-Order Contract

`wiki-query` minimizes context cost by reading wiki pages in **tiers**. Cheaper tiers first; load full pages only when cheaper tiers are insufficient.

## The 3 tiers

```
Tier 0: wiki/hot.md                       (~300 chars)
   ↓ if not enough
Tier 1: frontmatter.summary across pages  (≤200 chars × N pages)
   ↓ if not enough
Tier 2: full page body                    (full read)
```

## Tier 0 — Hot cache

`wiki/hot.md` contains:
- Recently queried topics (so repeat questions resolve instantly)
- Recently ingested pages (so freshly distilled knowledge is top of mind)

**Always read first.** If the answer is here, return immediately.

If hot.md doesn't have it, proceed to Tier 1.

## Tier 1 — Summary scan

Scan `wiki/index.md` to identify candidate pages by category and title match.

For each candidate, **read frontmatter only** (or use `head` to grab first ~15 lines).

The `summary:` field (≤200 chars) is the synthesized one-line answer the page provides. If a single summary or 2-3 summaries answer the user's question, return them with page-name attribution and stop.

**Do not load the full page body unless required.**

## Tier 2 — Full page read

Only when:
- Tier 1 summaries are insufficient (the answer needs `## Key Facts` detail)
- User explicitly asks for "the full breakdown" / "everything we know about X"
- Cross-page synthesis is requested

Load the minimum number of pages necessary. Prefer 1-2 deep reads over 5 shallow ones.

## Decision algorithm

```
query = user_question

# Tier 0
hot_content = read("wiki/hot.md")
if hot_content satisfies query:
    return hot_content with caveat "from hot cache (recent activity)"

# Tier 1
candidates = scan_index_for_matches(query)
summaries = [read_frontmatter_summary(p) for p in candidates]
if summaries satisfy query:
    return summaries with page-name attribution

# Tier 2
top_pages = rank_by_relevance(candidates, query)[:3]
bodies = [read_full(p) for p in top_pages]
return synthesized_answer(bodies)

# Always
update_hot_md(query, pages_used)
```

## Match heuristics for index scan

When scanning `wiki/index.md` for candidates:

1. **Exact title match** — highest priority (e.g., "qlib" → `entities/qlib.md`)
2. **Tag match** — frontmatter tags overlap with query keywords
3. **Filename slug match** — substring match on filename
4. **Domain match** — if user said "in finance", restrict to `domain: finance`

### Limitations of lexical heuristics

These heuristics are **lexical**, not semantic. They fail in 3 known cases:

1. **Synonym mismatch** — user asks about "Multi-Armed Bandits" but page is named `MAB.md`; pure title match misses unless user uses exact slug
2. **Conceptual subset query** — user asks "is qlib good for crypto trading?" — title-match on "qlib" hits, but the answer requires reading `## Key Facts` of multiple related pages
3. **Cross-language query** — user asks in 中文 but page slugs are English

**Mitigation**: when Tier-1 returns ≥1 candidate but the answer feels weak, fall through to Tier-2 (full page) on the **top-3 candidates** rather than just the top-1. Tier-2 body content has higher semantic surface area than the summary line.

If 0 matches → tell user "no wiki page matches this query" and offer:
- `/wiki-auto-research <topic>` to populate
- `/wiki-ingest` if they have new sources to feed

## Updating hot.md after each query

After answering, update `wiki/hot.md`'s "Recently queried" section:

```markdown
## Recently queried
- 2026-05-03: <user query topic> → entities/qlib, concepts/quant-investing
- 2026-05-02: ...
```

Keep the active section ≤300 chars. Truncate oldest entries first.

## When tiered retrieval fails

If after Tier 2 the answer is still incomplete:

1. **Honestly say so** — don't fabricate. Mark inferred conclusions clearly.
2. **Suggest** `/wiki-auto-research` to address the gap
3. **Suggest** `/wiki-ingest` if user has unfled source notes

The wiki is a living artifact. Gaps are expected and signal where to invest research effort, not failures.
