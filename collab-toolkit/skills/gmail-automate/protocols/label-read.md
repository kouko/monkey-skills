---
name: label-read
purpose: Enumerate Gmail labels — system + user-defined, including nested.
allowed-tools: Bash(gws:*)
---

## Purpose

Return a Markdown list of every label visible to the authenticated account: system labels (`INBOX`, `UNREAD`, `STARRED`, `SENT`, `DRAFT`, `SPAM`, `TRASH`, `CATEGORY_*`) and user-defined labels (including nested paths like `Work/Projects/2026`).

## Input

- `filter`: optional. Substring match on label name. Default: no filter.
- `messages_for`: optional. A label name; if set, *also* fetch the recent messages tagged with that label (delegates to `mail-search.md` with `label:<name>` operator).
- `limit`: optional. When `messages_for` is set, cap on returned messages. Default 20.
- `--json`: optional. Skip Markdown formatting.

## Steps

1. Call:

   ```bash
   gws gmail labels list
   ```

   Returns a JSON array of label records, each with `id`, `name`, `type` (`system` | `user`), and message counts.

2. Apply `filter` (substring match on `name`) if set.

3. Format Markdown:

   ```
   ## Gmail labels (N total)

   ### System
   - INBOX
   - UNREAD
   - STARRED
   - …

   ### User-defined
   - Work
   - Work/Projects
   - Work/Projects/2026
   - Personal
   - …
   ```

   Nested labels are exposed by Gmail as `parent/child/grandchild` strings — no separate tree structure to traverse.

4. If `messages_for` is set, follow with a `mail-search.md`-style invocation:

   ```bash
   gws gmail messages list \
     --query "label:<messages_for>" \
     --max-results <limit>
   ```

   Append the messages section below the label list.

## Common failure modes

- **Empty array** → impossible (system labels always present). If observed, treat as auth error.
- **`messages_for` references a label that does not exist** → mail list comes back empty. Note in output: `(label "<name>" not found, or has no messages)`.
- **Auth expired** → see `references/failure-modes.md` § `gws auth`.

## Examples

`filter = "Work"` → all labels containing `Work` in the name.

`messages_for = "Work/Projects/2026", limit = 10` → label list + 10 most recent messages with that label.
