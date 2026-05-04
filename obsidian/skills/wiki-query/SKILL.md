---
name: wiki-query
description: Query Obsidian wiki/ via tiered retrieval (hot.md → frontmatter summary → full page) to save context. Use when user asks a question wiki/ may answer. Do NOT use for repo-wiki:query or dbt-wiki:query. Obsidian wiki 検索・段階的取得・分層查詢。
---

# Wiki Query — Tiered Retrieval over wiki/

Answer the user's question by reading the wiki layer in cost-ordered tiers. Cheaper tiers first; full page reads only when summaries don't suffice.

See [retrieval-tiers.md](references/retrieval-tiers.md) for the full contract.

## Pre-flight

1. Read `<vault-root>/.obsidian-wiki.config` to find `OBSIDIAN_WIKI_VAULT_PATH` (defaults `wiki/`). If only legacy `.env` exists, instruct user to run `/wiki-setup` to migrate.
2. If `wiki/` does not exist, instruct user to run `/wiki-setup`.
3. If `wiki/index.md` is empty, instruct user to run `/wiki-ingest` first.

## STEP 1 — Tier 0: Hot cache

Read `wiki/hot.md` first.

If recent activity directly answers the user's query, return that and add a one-line attribution (`from hot cache, recently active`).

Skip to STEP 4 (update hot.md and report).

## STEP 2 — Tier 1: Summary scan

If hot.md doesn't suffice:

1. Read `wiki/index.md`
2. Identify candidate pages matching the query (see match heuristics in [retrieval-tiers.md](references/retrieval-tiers.md))
3. For each candidate, read **frontmatter only** (use `Read` with `limit: 15` to capture frontmatter without body)
4. Collect `summary:` values

If 2-3 summaries together answer the question:
- Return synthesized answer with page-name attribution: "Per `entities/qlib`: ...; per `concepts/quant-investing`: ..."
- Skip to STEP 4

## STEP 3 — Tier 2: Full page read

Only if Tier 1 was insufficient:

1. Rank top 1-3 candidates by relevance
2. Read full page body
3. Synthesize answer using `## Summary`, `## Key Facts`, `## Connections` content
4. Honor provenance markers — if a key fact is `^[ambiguous]` or `^[inferred]`, surface that uncertainty in your answer
5. If pages reference other wikilinks the user might want, mention them as follow-ups: "See also [[other-page]]"

If after Tier 2 the answer is still partial:
- Say so honestly
- Suggest `/wiki-auto-research <topic>` to populate the gap
- Suggest `/wiki-ingest` if the user has unfled source notes

## STEP 4 — Update hot.md and report

After every query (regardless of tier reached), update `wiki/hot.md` "Recently queried" section:

```markdown
## Recently queried
- YYYY-MM-DD: <one-line query topic> → <pages used>
```

Cap section ≤300 chars; truncate oldest first.

## Reporting style

- **Lead with the answer**, not the search process.
- **Cite pages** with wikilinks: `[[qlib]]` (bare filename, no path)
- **Surface uncertainty** when sources are ambiguous or inferred — don't sand it off
- **Show the tier reached** at the very end as a one-line tag: `(answered from Tier 0 / 1 / 2)` so the user can calibrate query patterns

## Anti-patterns

- ❌ Reading multiple full pages when frontmatter summaries would have answered
- ❌ Reading the index, then full page, without the summary scan in between
- ❌ Synthesizing without citing which page contributed which fact
- ❌ Hiding `^[ambiguous]` markers in synthesis (silently launders provenance)
- ❌ Falling through to Tier 2 too quickly (defeats the purpose of tiered retrieval)

## When the wiki has nothing

If 0 candidate pages match:

```
No wiki page matches this query.

Options:
  /wiki-auto-research <topic>  — fill the gap via web search
  /wiki-ingest                  — if you have source notes to add
  Or I can fall back to general knowledge (less authoritative)
```

Wait for user direction. Do not silently fall back to general knowledge — that masks coverage gaps the user wants to know about.
