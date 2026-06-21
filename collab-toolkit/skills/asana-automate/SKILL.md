---
name: asana-automate
description: |
  Asana automation via the official MCP V2 server. Read-only — task-list / task-detail / project-overview / search-global via MCP tool calls. Locale-independent (structured JSON, no UI scraping).
allowed-tools: mcp__asana__list_tasks, mcp__asana__get_task, mcp__asana__list_projects, mcp__asana__search
---

# asana-automate

Read-only Asana access via the official Asana MCP V2 server (`mcp.asana.com/v2/mcp`). Tool calls return structured JSON — no UI scraping, no locale tables, no browser daemon.

## Prerequisites

One-time setup:

1. Run `/collab-setup` and accept the asana row (records intent + verifies prerequisites).
2. Run `/mcp add asana` once — this triggers Claude Code's native OAuth pre-registration flow against `mcp.asana.com/v2/mcp`. Token refresh is handled automatically thereafter.

If a protocol fails with an auth error, re-run `/mcp add asana` to refresh the OAuth grant.

## Hero protocols

- `protocols/task-list.md` — list tasks (My Tasks or scoped to a project) with optional filters
- `protocols/task-detail.md` — full task content: description, subtasks, comments, attachments, custom fields
- `protocols/project-overview.md` — list accessible projects (workspace-scoped)
- `protocols/search-global.md` — typeahead / full-text search across tasks, projects, portfolios

## Workflow pattern

A typical task-list invocation:

```
mcp__asana__list_tasks({
  "assignee": "me",
  "workspace": "<workspace_gid>",
  "completed_since": "now",
  "opt_fields": "name,due_on,completed,projects.name"
})
```

Returns a JSON array of task records. Format per the protocol's `## Output` section.

## Failure modes

See `references/failure-modes.md` — OAuth scope, V2 lifecycle, rate limits, token refresh, tool-name verification status.
