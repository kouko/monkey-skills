---
name: search-workspace
purpose: Full-text search across pages and databases in the authenticated user's Notion workspace.
allowed-tools: mcp__notion__search
---

## Purpose

Return a grouped Markdown rendering of search hits across pages and databases for a free-text query.

## Input

- `query`: required. Free-text query string.
- `filter_type`: optional. `pages` / `databases` / `all`. Default `all`.
- `--json`: optional. Skip Markdown formatting, return raw API records.

Mapping to MCP params:
- `query`: pass through as the `query` field.
- `filter`: when `filter_type != all`, pass `{ "value": "page" | "database", "property": "object" }`. Omit for `all`.
- `page_size`: default 20 — bump to 100 if `--json` is set or caller asks for more results.

## Steps

1. Call:
   ```
   mcp__notion__search({
     "query": "<query>",
     "filter": { "value": "page", "property": "object" },   // omit when filter_type=all
     "page_size": 20
   })
   ```

2. Handle pagination — if response includes `has_more: true` and `next_cursor`, repeat with `start_cursor: <next_cursor>` until exhausted or caller-supplied limit reached.

3. Group results by `object` field (`page` vs `database`) and format Markdown:
   ```
   ## Notion search: "<query>" — N matches

   ### Pages (M)
   - **<page title>** — <parent.type>: <parent.title or id>

   ### Databases (K)
   - **<database title>** — <parent.type>: <parent.title or id>
   ```

   Omit any group whose count is 0. Page title lives at `properties.title.title[].plain_text` for pages, `title[].plain_text` for databases.

## Common failure modes

- **Empty array** → valid empty result. Emit `No matches for "<query>".`
- **Pagination dropped** → check `has_more` / `next_cursor`; full enumeration required for accurate count.
- **Title field missing** → page may be a child without a title property; fall back to `id`.
- **OAuth scope insufficient** → see `references/failure-modes.md` § OAuth scope. Notion's MCP grants vary by integration — workspace-wide search needs full read scope.

## Examples

"search notion for OKR" / 「在 Notion 搜尋 OKR」 / 「NotionでOKRを検索」 → grouped Markdown by object type.
