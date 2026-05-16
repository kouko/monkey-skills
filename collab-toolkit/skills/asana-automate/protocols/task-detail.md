---
name: task-detail
purpose: Fetch full task detail — title, description, subtasks, comments, attachments, custom fields.
---

## Inputs
- `task_url`: required.
- `--json`: optional.

## Output
```
# <title>
**Assignee**: <name>
**Due**: <date>
**Status**: <incomplete | complete>

## Description
<body>

## Subtasks (N)
- [ ] <title>

## Comments (N)
**<author> (<date>)**: <text>

## Attachments (N)
- <filename>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Assignee button prefix | `Assignee, ` | `受指派者, ` | `担当者, ` |
| Due-date button prefix | `Due date, ` | `到期日, ` | `期日, ` |
| Description region | `[region] "Description"` | `[region] "說明"` | `[region] "説明"` |
| Subtasks list | `[list] "Subtasks"` | `[list] "子任務"` | `[list] "サブタスク"` |
| Attachments list | `[list] "Attachments"` | `[list] "附件"` | `[list] "添付ファイル"` |
| Show-all-subtasks button | `[button] "Show all subtasks"` | `[button] "顯示所有子任務"` | `[button] "すべてのサブタスクを表示"` |

## Procedure

1. Open task URL:
   ```bash
   abx open <task_url>
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Identify (per Localized labels):
   - Title: `[heading]` level=1 (locale-agnostic)
   - Assignee: `[button]` with locale-specific prefix
   - Due date: `[button]` with locale-specific prefix
   - Description: `[region]` with locale-specific name
   - Subtasks: `[list]` with locale-specific name + `[listitem]` children
   - Comments: `[article]` elements (role locale-agnostic)
   - Attachments: `[list]` with locale-specific name

3. Fetch rich content:
   ```bash
   abx get text @eN
   ```

4. For each subtask listitem: title + child-checkbox state.

5. Format Markdown. Omit empty sections.

## Failure modes

- **No level=1 heading** → login page → reauth.
- **Task URL 404** → invalid/deleted.
- **Missing Description** → valid empty → `(no description)`.

## Notes

- Lazy comment rendering — scroll + re-snapshot.
- Custom fields: `[button]` with `<field name>, <value>` (field names user-defined).
- Subtasks may be collapsed — click locale-specific Show-all-subtasks button before re-snapshotting.

## Examples

Input: `task_url = https://app.asana.com/0/1234/5678` → full Markdown.
