---
name: project-overview
purpose: List all projects user can access. Flat list only (section counts deferred to v0.2.0).
---

## Inputs
- None.
- `--json`: optional.

## Output
```
## Projects (N)
- <project name 1>
- <project name 2>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Sidebar Projects link | `[link] "Projects"` | `[link] "專案"` | `[link] "プロジェクト"` |
| Show-more button | `[button] "Show more"` | `[button] "顯示更多"` | `[button] "もっと表示"` |

## Procedure

1. Navigate:
   ```bash
   abx open https://app.asana.com/0/projects
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Projects appear as `[row]` (grid view) or `[treeitem]` (sidebar). Names are user-defined (no translation).

3. Extract project name (link / treeitem name).

4. Format as flat Markdown list.

## Failure modes

- **No projects in snapshot** → empty (valid) OR UI changed.
- **Login wall** → reauth.

## v0.1.5+ limitations

- **Section/task counts not fetched** — out of scope, deferred to v0.2.0.
- **Pagination** — only visible page captured.

## Examples

Flat list of project names.
