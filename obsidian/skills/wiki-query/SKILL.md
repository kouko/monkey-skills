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
3. Verify `<skill-root>/scripts/query-frontmatter.py` exists. If missing, the skill is broken; tell the user to reinstall the plugin.

## STEP 1 — Tier 0: Hot cache

Read `wiki/hot.md` first.

If recent activity directly answers the user's query, return that and add a one-line attribution (`from hot cache, recently active`).

Skip to STEP 4 (update hot.md and report).

## STEP 2 — Tier 1: Frontmatter script

If hot.md doesn't suffice, delegate candidate selection + summary collection to `<skill-root>/scripts/query-frontmatter.py`. The script scans every page's frontmatter in one pass and returns ranked candidates with `summary:` already extracted, so you do **not** read `wiki/index.md` or any page bodies yourself in this tier.

1. Extract 2-5 keywords from the user's question (lowercase nouns/proper-nouns, drop stopwords). Combine into a single comma-separated string.
2. Decide whether to pass `--type <type>`:
   - Only when the user's query is explicitly type-scoped (e.g. "Who is TSMC?" → entities; "what does HHI mean?" → concepts).
   - Otherwise omit `--type` and let the script search all 6 type subdirectories.
   - Valid types: `entities`, `concepts`, `references`, `skills`, `synthesis`, `journal`.
3. Invoke the script:
   ```bash
   python3 <skill-root>/scripts/query-frontmatter.py \
     --keywords "<kw1,kw2,...>" \
     --top 5 \
     [--type <type>] \
     --vault-root <vault-root>
   ```
   `<vault-root>` is the directory containing `wiki/` (from Pre-flight step 1).
4. Parse the JSON array on stdout. Each candidate object already has `path`, `title`, `type`, `summary`, `tags`, `score` — no further file reads needed at this tier.

If 2-3 summaries together answer the question:
- Return synthesized answer with page-name attribution: "Per `entities/qlib`: ...; per `concepts/quant-investing`: ..."
- Skip to STEP 4.

**Fallback when the script returns an empty array (0 candidates):**
- Broaden: drop `--type` if you set one, try synonyms / translated keywords (e.g. add 中文 ↔ English variants), re-invoke.
- If still 0 candidates, do **not** fall through to Tier 2 (there is nothing to read). Suggest `/wiki-auto-research <topic>` per the "When the wiki has nothing" section.

## STEP 3 — Tier 2: Full page read

Only if Tier 1 was insufficient:

1. Pick top 1-3 from the script's ranked output (semantically re-rank only if the lexical score looks misleading)
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
- ❌ Reading the index, then full page, without the frontmatter script in between
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
