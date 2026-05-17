---
name: page-fetch
purpose: Fetch a Notion page's content as Markdown.
---

## Inputs
- `page_url`: required.
- `--json`: optional.

## Output
Page rendered as Markdown — headings, paragraphs, lists, callouts (`> 💡 ...`), toggles (`▶ <title>`).

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Page content region | `[region] "Page content"` | `[region] "頁面內容"` | `[region] "ページコンテンツ"` |

## Procedure

1. ```bash
   abx open <page_url>
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Identify:
   - Title: `[heading]` level=1 (locale-agnostic)
   - Page content region (locale-dependent — see table)
   - Block children inside region: `[heading]`, `[paragraph]`, `[listitem]`, `[callout]`, `[toggle]` (roles locale-agnostic)

3. Iterate children of the page content region. Map block type → Markdown:
   - `[heading]` → `## <name>` (level-aware)
   - `[paragraph]` → text via `abx get text @eN`
   - `[listitem]` → `- <text>`
   - `[callout]` → `> 💡 <text>`
   - `[toggle]` → `▶ <name>` (click + re-snapshot to expand)

4. Concatenate into Markdown.

## Failure modes

- **Page content region missing** (in any of 3 locales) → wait longer + re-snapshot OR no permission.
- **Empty page** → `(page has no visible content blocks)`.

## Notes

- Embedded databases render as `[grid]` — use `protocols/database-query.md` for rows.
- Toggles collapsed by default — expand to capture nested content.
- Long pages lazy-load — scroll + re-snapshot.

## Examples

Input: `page_url = https://www.notion.so/workspace/Some-Page-abc123` → full Markdown.
