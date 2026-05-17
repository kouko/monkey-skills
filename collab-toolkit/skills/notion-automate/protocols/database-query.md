---
name: database-query
purpose: Query a Notion database with filter / sort. Return matching rows.
---

## Inputs
- `database_url`: required.
- `filters`: optional JSON array.
- `sort`: optional `property:direction`.
- `--json`: optional.

## Output
Markdown table of rows.

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Filter button | `[button] "Filter"` | `[button] "篩選"` | `[button] "フィルター"` |
| Sort button | `[button] "Sort"` | `[button] "排序"` | `[button] "並べ替え"` |
| Add-filter button | `[button] "Add filter"` | `[button] "新增篩選"` | `[button] "フィルターを追加"` |

## Procedure

1. ```bash
   abx open <database_url>
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find database `[grid]`. Rows = `[row]`, header = `[columnheader]`.

3. **Apply filters via UI** if specified (look for Filter button per Localized labels). Notion's filter dropdown may render in a portal — see Failure modes.

4. **Apply sort** similarly via Sort button.

5. **Read rows**. Extract `[cell]` children. Format as Markdown table.

## Failure modes

- **Filter UI in React portal** — dropdown not in accessibility tree → fetch all visible rows + filter in this protocol's logic instead.
- **Lazy-loaded rows** → scroll + re-snapshot.
- **Login wall** → reauth.

## Notes

- Different views (Table / Board / Calendar / Timeline / Gallery / List) render differently. Switch to Table view first for cleanest `[grid]`/`[row]`/`[cell]` structure.

## Examples

Input: `database_url = ...` → Markdown table of rows.
