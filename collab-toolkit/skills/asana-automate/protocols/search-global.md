---
name: search-global
purpose: Search across tasks / projects / portfolios in a workspace.
allowed-tools: mcp__asana__search
---

## Purpose

Return a grouped Markdown rendering of search hits across tasks, projects, and (where exposed) portfolios for a free-text query in a workspace.

## Input

- `query`: required. Free-text query. Asana operators (`assignee:`, `project:`, `due:today`) are honored server-side.
- `filter_type`: optional. `tasks` / `projects` / `portfolios` / `all`. Default `all`.
- `workspace`: optional. Workspace gid (use cached default if omitted).
- `--json`: optional.

Mapping to MCP params:
- `query`: pass through as `text` or `query` (per tool signature).
- `workspace`: required.
- `resource_type`: pass when `filter_type != all` (e.g., `task`, `project`, `portfolio`). Some Asana MCP versions expose this as separate tools — if so, call the type-specific search tool and merge results.

## Steps

1. Call:
   ```
   mcp__asana__search({
     "workspace": "<workspace_gid>",
     "query": "<query>",
     "opt_fields": "name,resource_type,projects.name"
   })
   ```

2. If `filter_type` is specified, restrict results by `resource_type` field client-side (or by calling type-scoped search if exposed).

3. Group results by `resource_type` and format Markdown:
   ```
   ## Search results for "<query>" (N)

   ### Tasks (M)
   - <name> — Project: <projects[0].name>

   ### Projects (K)
   - <name>

   ### Portfolios (L)
   - <name>
   ```

   Omit any group whose count is 0.

## Common failure modes

- **Empty array** → valid empty result.
- **Portfolios not returned** → may require separate scope or tool; see `references/failure-modes.md` § OAuth scope.
- **Operator syntax rejected** → Asana search operators are documented at developers.asana.com; passing unknown operators returns 400.

## Notes

- Asana search operators (`assignee:me`, `project:<gid>`, `due:today`) are locale-independent at the API layer — pass through verbatim.

## Examples

Input: `query = "OKR"` → grouped Markdown by resource type.
