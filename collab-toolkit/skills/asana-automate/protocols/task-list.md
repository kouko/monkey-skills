---
name: task-list
purpose: List tasks (My Tasks by default, optionally scoped to a project) with filters.
allowed-tools: mcp__asana__list_tasks
---

## Purpose

Return a Markdown list of tasks for the current user, optionally filtered by due-date window, completion status, or project.

## Input

- `filter_due`: optional. `today` / `this-week` / `overdue` / `all`. Default: `all`.
- `filter_status`: optional. `incomplete` / `complete` / `all`. Default: `incomplete`.
- `filter_project`: optional. Project name substring or project gid.

Mapping to MCP params:
- `assignee: "me"` — defaults to the authenticated user.
- `workspace`: required by Asana API. If unknown, fetch via `mcp__asana__list_projects` first or accept user-supplied workspace gid.
- `completed_since: "now"` — returns only incomplete tasks (use when `filter_status = incomplete`).
- `project`: pass when `filter_project` resolves to a gid; otherwise client-side filter on `projects.name`.
- `opt_fields: "name,due_on,completed,projects.name,assignee.name"` — minimal field set.

## Steps

1. Resolve workspace gid (if not cached).

2. Call:
   ```
   mcp__asana__list_tasks({
     "assignee": "me",
     "workspace": "<workspace_gid>",
     "completed_since": "now",
     "opt_fields": "name,due_on,completed,projects.name"
   })
   ```

3. Apply client-side filters:
   - `filter_due`: compare `due_on` (ISO date) to today / week boundary.
   - `filter_status`: respect `completed` flag if `filter_status != incomplete`.
   - `filter_project`: substring match on `projects[].name` or exact gid match.

4. Format as Markdown:
   ```
   ## My Tasks (N)
   - [ ] <name> — Project: <projects[0].name> — Due: <due_on>
   - [x] <name> — Project: <projects[0].name> — Due: <due_on>
   ```

## Common failure modes

- **Empty array** → valid, emit `No tasks matching filter.`
- **Missing workspace gid** → ask user or call `mcp__asana__list_projects` to discover.
- **OAuth scope insufficient** → see `references/failure-modes.md` § OAuth scope.

## Examples

"show my Asana tasks this week" / 「列我這週的 Asana 任務」 / 「今週のAsanaタスク」 → Markdown list.
