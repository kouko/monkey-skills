---
name: task-list
purpose: List My Tasks across all projects with optional filters (due-date / status / custom field).
---

## Inputs

- `filter_due`: optional. One of `today` / `this-week` / `overdue` / `all`. Default: `all`.
- `filter_status`: optional. One of `incomplete` / `complete` / `all`. Default: `incomplete`.
- `--json`: optional. Output structured JSON.

## Output

Default Markdown:
```
## My Tasks (15)

### Today (3)
- [ ] Refactor auth middleware — Project: Backend / Section: Engineering — Due: today
- [ ] Code review PR #234 — Project: Backend / Section: Reviews — Due: today
- [x] Standup notes — Project: Eng Ops / Section: Daily — Due: today (completed)

### This week (12)
- [ ] ... (truncated for plan; full output shows all tasks)
```

`--json` shape:
```json
{
  "total": 15,
  "tasks": [
    {
      "id": "extracted from data-task-id attribute",
      "title": "Refactor auth middleware",
      "project": "Backend",
      "section": "Engineering",
      "due_date": "2026-05-15",
      "status": "incomplete",
      "url": "https://app.asana.com/0/<workspace>/<task_id>"
    }
  ]
}
```

## Procedure (semantic-first, no hardcoded refs)

```bash
# Prerequisite: $HOME/.local/bin must be on PATH; /collab-setup ensures this.

# 1. Open My Tasks
ABX_SERVICE=asana abx open https://app.asana.com/0/inbox
ABX_SERVICE=asana abx wait --load networkidle

# 2. Navigate to My Tasks (via sidebar)
SNAP=$(ABX_SERVICE=asana abx snapshot -i --json)
MYTASKS_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="link" and .name=="My tasks") | .ref' | head -1)
[ -z "$MYTASKS_REF" ] && { echo "ERR: UI changed: 'My tasks' link not found in sidebar"; exit 1; }
ABX_SERVICE=asana abx click "$MYTASKS_REF"
ABX_SERVICE=asana abx wait --load networkidle

# 3. Snapshot task list
SNAP=$(ABX_SERVICE=asana abx snapshot -i --json)

# 4. Extract task rows
# Each task is role="row" within a role="grid" parent. Task title is in role="link" child.
echo "$SNAP" | jq -r '
  [.elements[]
    | select(.role=="row")
    | {
        title: ([.children[]? | select(.role=="link" and .name != "") | .name] | first // "(untitled)"),
        ref: .ref
      }
  ] | .[]
  | "- \(.title)"
'

# 5. (Optional --json mode) Emit JSON
# Replace the markdown step above with:
# echo "$SNAP" | jq '[.elements[] | select(.role=="row") | {title, ref, ...}]'
```

## Failure modes

- "UI changed: 'My tasks' link not found in sidebar" → references/failure-modes.md → "UI evolution"
- Login wall (title contains "Sign in") → references/failure-modes.md → "Auth expiry"
- Empty grid (no tasks) → valid empty result, output "No tasks matching filter"

## Examples

User invocation: "show my Asana tasks due this week"

Expected output (Markdown mode): list of tasks grouped by due-date with title / project / section / status.

`--json` mode returns structured JSON for downstream piping (e.g., to gmail-automate to email summary, or to notion-automate to log).
