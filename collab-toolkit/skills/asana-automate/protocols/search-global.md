---
name: search-global
purpose: Full-text search across tasks / projects / portfolios.
---

## Inputs
- `query`: required.
- `filter_type`: optional. `tasks` / `projects` / `portfolios` / `all`.
- `--json`: optional.

## Output
```
## Search results for "<query>" (N)

### Tasks (M)
- <task title> — Project: <project>

### Projects (K)
- <project name>

### Portfolios (L)
- <portfolio name>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Top-bar Search button | `[button] "Search"` or `"Search Asana"` | `[button] "搜尋"` or `"搜尋 Asana"` | `[button] "検索"` or `"Asana を検索"` |
| Search input | `[textbox] "Search"` or `[combobox]` | `[textbox] "搜尋"` or `[combobox]` | `[textbox] "検索"` or `[combobox]` |
| Tasks group heading | `[heading] "Tasks"` | `[heading] "任務"` | `[heading] "タスク"` |
| Projects group heading | `[heading] "Projects"` | `[heading] "專案"` | `[heading] "プロジェクト"` |
| Portfolios group heading | `[heading] "Portfolios"` | `[heading] "投資組合"` | `[heading] "ポートフォリオ"` |

## Procedure

1. Open Asana:
   ```bash
   abx open https://app.asana.com/0/inbox
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find Search button (per Localized labels). Click + re-snapshot:
   ```bash
   abx click @eN
   abx wait 500
   abx snapshot -i
   ```

3. **Find active search input** (textbox/combobox). Fill + submit:
   ```bash
   abx fill @eM "<query>"
   abx press Enter
   abx wait --load networkidle
   abx snapshot -i
   ```

4. **Read results**. Headings (locale-dependent) then row/listitem children below each.

5. Extract names + secondary info. Apply `filter_type`. Format Markdown.

## Failure modes

- **Search button missing** → re-snapshot, top bar restructured.
- **No textbox after click** → `abx wait 1000` + re-snapshot.
- **No results** → valid empty.

## Notes

- **Asana search operators** (`assignee:`, `project:`, `due:today`) are locale-stable — include in query.

## Examples

Input: `query = "OKR"` → Markdown grouped by type.
