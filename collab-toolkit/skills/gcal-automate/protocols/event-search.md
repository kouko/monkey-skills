---
name: event-search
purpose: Search calendar events by title / attendee / location keyword.
---

## Inputs
- `query`: required.
- `--json`: optional.

## Output
```
## GCal search: "<query>" — N results

- <YYYY-MM-DD> <HH:MM>: <title> @ <location>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Search button | `[button] "Search"` | `[button] "搜尋"` | `[button] "検索"` |
| Search input | `[textbox] "Search"` or `[combobox]` | `[textbox] "搜尋"` or `[combobox]` | `[textbox] "検索"` or `[combobox]` |
| Search results region | `[region] "Search results"` | `[region] "搜尋結果"` | `[region] "検索結果"` |

## Procedure

1. ```bash
   abx open https://calendar.google.com
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find Search button (locale-dependent). May be magnifying-glass icon — check aria-label.

3. Click + re-snapshot:
   ```bash
   abx click @eN
   abx wait 500
   abx snapshot -i
   ```

4. **Find search input**. Fill + submit:
   ```bash
   abx fill @eM "<query>"
   abx press Enter
   abx wait --load networkidle
   abx snapshot -i
   ```

5. **Read results**. Inside Search results region (locale-dependent). Each result `[listitem]` / `[article]` with date / time / title / location.

6. Format Markdown.

## Failure modes

- **Search button missing** → toolbar restructured.
- **No results** → valid empty.

## Notes

- GCal search covers current account's primary + visible secondary calendars.
- Date filtering: append `before:YYYY-MM-DD` / `after:YYYY-MM-DD` to query.

## Examples

`query = "OKR review"` → matching events.
