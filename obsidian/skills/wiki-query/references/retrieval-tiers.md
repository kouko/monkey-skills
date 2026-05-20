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

## Tier 1 — Frontmatter script

Invoke the bundled frontmatter script (`<skill-root>/scripts/query-frontmatter.py`) to scan every page's YAML frontmatter in one pass and return the top-N ranked candidates as a JSON array. Each row already carries `path`, `title`, `type`, `summary`, `tags`, `score` — no further file reads required at this tier.

```bash
python3 <skill-root>/scripts/query-frontmatter.py \
  --keywords "<comma-separated-keywords>" \
  --top 5 \
  [--type <entities|concepts|references|skills|synthesis|journal>] \
  --vault-root <vault-root>
```

The `summary:` field (≤200 chars per page) is the synthesized one-line answer the page provides. If a single summary or 2-3 summaries answer the user's question, return them with page-name attribution and stop.

**Do not load the full page body unless required** — that is Tier 2.

The script replaces the older approach of reading `wiki/index.md` + grepping for candidates, which forced Claude to lexically scan an N-line text file from its own context. Moving the scan into deterministic Python keeps Tier 1 cost flat as the wiki grows.

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
keywords = extract_keywords(query)                            # LLM
type_hint = infer_type_if_explicit(query)                     # LLM; may be None
candidates = run_query_frontmatter_script(keywords, type_hint)  # deterministic Python
# each candidate already has path/title/type/summary/tags/score
if candidates satisfy query:
    return candidate summaries with page-name attribution

# Tier 2
top_pages = rank_by_relevance(candidates, query)[:3]
bodies = [read_full(p) for p in top_pages]
return synthesized_answer(bodies)

# Always
update_hot_md(query, pages_used)
```

## Match heuristics (implemented by the frontmatter script)

Both keywords and the parsed frontmatter values are NFKC-normalized and lowercased before matching. Per-keyword weights are summed across the parsed frontmatter fields (title=+3, tag=+2, summary=+1 per matched keyword):

1. **Title substring** — `+3` if the keyword appears anywhere inside the `title:` string (substring, not exact equality)
2. **Tag substring** — `+2` if the keyword appears inside any element of the `tags:` list
3. **Summary substring** — `+1` if the keyword appears inside the `summary:` field

Contributions accumulate across all keywords for a given page. Pages with total score `> 0` are sorted by `(score desc, path asc)` and truncated to `--top N`. The script does **not** match on filename, slug, or basename — only on parsed frontmatter fields.

Type filtering (`--type entities|concepts|references|skills|synthesis|journal`) restricts the scan to one subdir; omit it to search all 6.

### Limitations of lexical heuristics

The script's ranking is **lexical**, not semantic. It fails in 3 known cases:

1. **Synonym / abbreviation mismatch** — user queries `"MAB"` but the page's `title:` / `tags:` / `summary:` only contain the long form `"Multi-Armed Bandits"`; substring `"MAB"` does not occur inside `"multi-armed bandits"`, so the page scores 0 even though it is the right answer. (Symmetrically: querying `"Multi-Armed Bandits"` against a page whose frontmatter only carries the short form `"MAB"` also misses.)
2. **Conceptual subset query** — user asks "is qlib good for crypto trading?" — substring on `"qlib"` hits, but the answer requires reading `## Key Facts` of multiple related pages
3. **Cross-language query** — user asks in 中文 but frontmatter values are English

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
