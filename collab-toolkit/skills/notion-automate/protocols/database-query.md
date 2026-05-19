---
name: database-query
purpose: Query a Notion database with filter / sort and return matching rows as a Markdown table.
allowed-tools: mcp__notion__query_database
---

## Purpose

Return a Markdown table of rows from a Notion database, optionally filtered and sorted server-side via the Notion API's structured filter/sort syntax.

## Input

- `database_url` OR `database_id`: required. Parse the 32-char hex id out of the URL if needed (same rules as page-fetch).
- `filters`: optional. Notion API filter object (e.g., `{ "property": "Status", "select": { "equals": "Done" } }`) or compound `{ "and": [...] }` / `{ "or": [...] }`. Pass through to the API.
- `sort`: optional. Either `property:direction` shorthand (e.g., `"Due:descending"`) — convert to API form `[{ "property": "Due", "direction": "descending" }]` — or the raw API sort array.
- `--json`: optional. Skip Markdown formatting, return raw API records.

## Steps

1. Resolve `database_id` from `database_url` if needed.

2. Call:
   ```
   mcp__notion__query_database({
     "database_id": "<database_id>",
     "filter": <filters or omit>,
     "sorts": <sort array or omit>,
     "page_size": 100
   })
   ```

   Note: Notion API version `2025-09-03` introduced `data_sources` as the canonical wrapper for database rows. The MCP tool may accept `data_source_id` instead of (or in addition to) `database_id` — pass whichever the tool signature documents. When both are present, the response shape is identical at the row level.

3. Handle pagination — loop on `has_more: true` / `start_cursor: <next_cursor>` until exhausted.

4. Discover columns from the first row's `properties` map. Render a Markdown table:
   ```
   ## <Database title> — N rows

   | <col 1> | <col 2> | <col 3> |
   |---------|---------|---------|
   | <val>   | <val>   | <val>   |
   ```

   Cell value extraction by property type (most common):
   - `title` → concatenate `title[].plain_text`
   - `rich_text` → concatenate `rich_text[].plain_text`
   - `select` → `select.name`
   - `multi_select` → comma-join `multi_select[].name`
   - `date` → `date.start` (append `→ date.end` if present)
   - `people` → comma-join `people[].name`
   - `checkbox` → `[x]` / `[ ]`
   - `number` → `number`
   - `url` / `email` / `phone_number` → literal string
   - `relation` → comma-join `relation[].id` (resolve to titles via page-fetch if needed; expensive)
   - `formula` / `rollup` → use the typed sub-object (`formula.string`, `formula.number`, etc.)

## Common failure modes

- **400 / invalid filter** → filter property name or operator wrong for column type. Notion returns the offending field in the error message.
- **404 / database not found** → invalid id or database not shared with the MCP integration.
- **Pagination dropped** → row count off; always loop until `has_more: false`.
- **Empty array** → valid empty result. Emit `No rows matching filter.`
- **Property type changed** → schema evolved since last query; surface raw value and warn.

## Examples

Input: `database_url = ..., filters = { "property": "Status", "select": { "equals": "Done" } }, sort = "Due:descending"` → Markdown table.
