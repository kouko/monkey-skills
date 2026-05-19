---
name: project-overview
purpose: List projects the user can access. Flat list, workspace-scoped.
allowed-tools: mcp__asana__list_projects
---

## Purpose

Return a flat Markdown list of projects accessible to the authenticated user in a given workspace.

## Input

- `workspace`: optional. Workspace gid. If omitted, prompt user or default to the workspace cached from `/collab-setup`.
- `archived`: optional. Default `false` (exclude archived projects).
- `--json`: optional.

Mapping to MCP params:
- `workspace`: required by API.
- `archived`: pass `false` to hide archived; omit for all.
- `opt_fields: "name,archived,owner.name"` — minimal field set.

## Steps

1. Call:
   ```
   mcp__asana__list_projects({
     "workspace": "<workspace_gid>",
     "archived": false,
     "opt_fields": "name,owner.name"
   })
   ```

2. Handle pagination — if response includes `next_page.offset`, repeat with that offset until exhausted.

3. Format flat Markdown:
   ```
   ## Projects (N)
   - <name>
   - <name>
   ```

## Common failure modes

- **Empty array** → user has no project memberships in this workspace.
- **Missing workspace gid** → ask user.
- **Pagination dropped** → check `next_page.offset` in response; full enumeration required for accurate count.

## v0.2.0 scope

- **Section / task counts**: not fetched (would require N additional API calls). Deferred to v0.3.0 if needed.

## Examples

→ Flat Markdown list of project names.
