---
name: search-workspace
purpose: Full-text search across pages and databases.
---

## Inputs
- `query`: required.
- `filter_type`: optional. `pages` / `databases` / `all`.
- `--json`: optional.

## Output
```
## Notion search: "<query>" — N matches

### Pages (M)
- **<page title>** — <path or parent>

### Databases (K)
- **<database name>** — <owner>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Search trigger | `[button] "Search"` or `"Quick Find"` | `[button] "搜尋"` or `"快速尋找"` | `[button] "検索"` or `"クイック検索"` |
| Search input | `[textbox] "Search"` | `[textbox] "搜尋"` | `[textbox] "検索"` |

## Procedure

1. ```bash
   abx open https://www.notion.so
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find Search trigger. Or use keyboard shortcut: `abx press Cmd+P` (macOS) / `Ctrl+P` (others).

3. Click + re-snapshot:
   ```bash
   abx click @eN
   abx wait 500
   abx snapshot -i
   ```

4. **Find search input**. Fill (Notion search is real-time as you type):
   ```bash
   abx fill @eM "<query>"
   abx wait 1000
   abx snapshot -i
   ```

5. **Read results**. Each result `[listitem]` with name + path. Extract + filter + format.

## Failure modes

- **Search trigger missing** → top bar restructured.
- **Empty results** → valid empty.

## Notes

- Workspace switcher (top-left) matters for multi-workspace users.
- Pressing Enter sometimes optional (real-time search).

## Examples

`query = "OKR", filter_type = pages` → page results.
