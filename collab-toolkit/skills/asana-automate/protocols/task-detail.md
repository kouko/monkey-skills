---
name: task-detail
purpose: Fetch full task detail — title, description, subtasks, comments, attachments, custom fields.
allowed-tools: mcp__asana__get_task
---

## Purpose

Return a Markdown rendering of a single task: title, assignee, due date, description (HTML rendered as plain text), subtasks, comments (stories of type `comment_added`), attachments, and custom fields.

## Input

- `task_url` OR `task_gid`: required. Parse gid out of URL if needed — last numeric segment of `https://app.asana.com/0/<project>/<task_gid>` or new format `https://app.asana.com/1/<workspace>/project/<project>/task/<task_gid>`.
- `--json`: optional. Skip Markdown formatting, return raw API record.

## Steps

1. Resolve `task_gid` from `task_url` if needed.

2. Call:
   ```
   mcp__asana__get_task({
     "task_gid": "<gid>",
     "opt_fields": "name,notes,html_notes,due_on,completed,assignee.name,projects.name,custom_fields.name,custom_fields.display_value,num_subtasks"
   })
   ```

3. If `num_subtasks > 0`, fetch subtasks. The Asana V2 MCP exposes this either as a separate tool or via `opt_fields` expansion — assumed canonical: pass `opt_fields: "subtasks.name,subtasks.completed"` or call a dedicated subtasks tool if exposed. Fall back to documenting in failure-modes if neither works.

4. Fetch stories (comments) — call the stories endpoint if exposed by MCP (e.g., `mcp__asana__list_task_stories`); otherwise note as a v0.2.0 limitation.

5. Format Markdown:
   ```
   # <name>
   **Assignee**: <assignee.name>
   **Due**: <due_on>
   **Status**: <incomplete | complete>

   ## Description
   <notes>

   ## Subtasks (N)
   - [ ] <name>

   ## Comments (N)
   **<author> (<created_at>)**: <text>

   ## Attachments (N)
   - <name>

   ## Custom fields
   - <field.name>: <field.display_value>
   ```

   Omit any section whose count is 0.

## Common failure modes

- **404 / task not found** → invalid gid or task deleted.
- **Stories or attachments endpoint not exposed** → emit warning and skip section; see `references/failure-modes.md`.
- **Empty `notes`** → `(no description)`.

## Examples

Input: `task_url = https://app.asana.com/0/1234/5678` → full Markdown rendering of the task.
