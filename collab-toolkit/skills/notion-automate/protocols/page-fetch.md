---
name: page-fetch
purpose: Fetch a Notion page's content — title, properties, block tree — and render as Markdown.
allowed-tools: mcp__notion__get_page
---

## Purpose

Return a Markdown rendering of a single Notion page: title, top-level properties, and block-tree content (headings, paragraphs, lists, callouts, toggles, embedded databases as references).

## Input

- `page_url` OR `page_id`: required. Parse the 32-char hex id out of the URL if needed — last segment of `https://www.notion.so/<workspace>/<slug>-<page_id>` (strip dashes, take final 32 hex chars).
- `--json`: optional. Skip Markdown formatting, return raw API record.

## Steps

1. Resolve `page_id` from `page_url` if needed.

2. Call:
   ```
   mcp__notion__get_page({
     "page_id": "<page_id>"
   })
   ```

   Returns page metadata + properties. Notion API version `2025-09-03` introduced `data_sources` as the primary abstraction — when the response includes `data_sources[]` (e.g., for database-style pages), prefer that wrapper over raw `properties` for typed value extraction. For plain content pages the `properties` and block tree remain unchanged.

3. Fetch block children — the get_page response may not embed full block content. If the MCP exposes a dedicated `mcp__notion__get_block_children` tool, call it with `block_id: <page_id>` and paginate via `start_cursor` / `has_more`. If only `mcp__notion__get_page` is exposed and it returns a `blocks` / `children` array inline, use that. Document the resolved approach in `references/failure-modes.md` after first verification.

4. Map block `type` → Markdown:
   - `heading_1` → `# <text>`
   - `heading_2` → `## <text>`
   - `heading_3` → `### <text>`
   - `paragraph` → plain text
   - `bulleted_list_item` → `- <text>`
   - `numbered_list_item` → `1. <text>` (Markdown renumbers)
   - `to_do` → `- [ ] <text>` / `- [x] <text>` per `checked`
   - `callout` → `> 💡 <text>` (use `icon.emoji` when present instead of 💡)
   - `toggle` → `▶ <text>` followed by indented children
   - `child_database` → `[Database: <title>](notion://<id>)` — use `protocols/database-query.md` for rows
   - `child_page` → `[Sub-page: <title>](notion://<id>)`
   - Unknown types → skip with a comment `<!-- unsupported block: <type> -->`

5. Concatenate Markdown:
   ```
   # <page title>

   **Properties**
   - <prop name>: <prop value>

   ---

   <block tree as Markdown>
   ```

   Omit Properties section if page has no surfaced properties beyond title.

## Common failure modes

- **404 / page not found** → invalid id or page not shared with the MCP integration.
- **Block children pagination dropped** → long pages silently truncate; always loop until `has_more: false`.
- **Rich text array** — each block's text content is a `rich_text[]` array; concatenate `plain_text` for the rendered string.
- **Empty page** → `(page has no content blocks)`.
- **data_sources vs properties divergence** → see `references/failure-modes.md` § API 2025-09-03 data-source abstraction.

## Examples

Input: `page_url = https://www.notion.so/workspace/Some-Page-abc123` → full Markdown rendering of the page.
