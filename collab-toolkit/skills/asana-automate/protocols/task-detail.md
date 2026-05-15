---
name: task-detail
purpose: Fetch full detail of a single task — title, description, subtasks, comments, attachments, custom field values.
---

## Inputs

- `task_url`: required. Full Asana task URL (e.g., `https://app.asana.com/0/<workspace>/<task_id>`).
- `--json`: optional.

## Output

Default Markdown:
```
# Refactor auth middleware
**Project**: Backend / Engineering
**Assignee**: kouko
**Due**: 2026-05-15
**Status**: incomplete

## Description
Replace the legacy session middleware with the new compliance-aligned implementation...

## Subtasks (3)
- [x] Write design doc
- [ ] Implement new middleware
- [ ] Migrate existing routes

## Comments (5)
**Alice (2026-05-14)**: Looks good, but check the rate-limiter integration.
...

## Attachments (2)
- design-doc.pdf
- arch-diagram.png
```

`--json` shape: full task object with all fields above as JSON.

## Procedure

```bash
TASK_URL="$1"
[ -z "$TASK_URL" ] && { echo "ERR: task_url required"; exit 1; }

ABX_SERVICE=asana abx open "$TASK_URL"
ABX_SERVICE=asana abx wait --load networkidle
SNAP=$(ABX_SERVICE=asana abx snapshot -i --json)

# Title — role="heading" level=1
TITLE=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="heading" and .level==1) | .name' | head -1)

# Assignee — element with aria label containing "Assignee"
ASSIGNEE=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and (.name|startswith("Assignee"))) | .name // ""' | head -1)

# Due date — element with aria label containing "Due date"
DUE=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and (.name|startswith("Due"))) | .name // ""' | head -1)

# Description — role="textbox" or role="region" with aria-label="Description"
DESC=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="region" and .name=="Description") | .text' | head -1)

# Subtasks — role="list" with aria-label="Subtasks" → children are role="listitem"
SUBTASKS=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="list" and .name=="Subtasks") | .children[]? | select(.role=="listitem") | "- [\(if (.checked // false) then "x" else " " end)] \(.name)"')

# Comments — role="article" elements within "Activity" section
COMMENTS=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="article") | "**\(.author // "(unknown author)") (\(.timestamp // "(unknown time)"))**: \(.text // "")"')

# Attachments — role="list" with aria-label="Attachments"
ATTACHMENTS=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="list" and .name=="Attachments") | .children[]? | .name' | sed 's/^/- /')

# Emit markdown
cat <<EOF
# $TITLE
**Assignee**: $(echo "${ASSIGNEE}" | sed -E 's/^Assignee[:, ]+//')
**Due**: $(echo "${DUE}" | sed -E 's/^Due date[:, ]+'//)

## Description
$DESC

## Subtasks
$SUBTASKS

## Comments
$COMMENTS

## Attachments
$ATTACHMENTS
EOF
```

## Failure modes

- Title missing → likely on login page → "Auth expiry"
- Task not found (404 title) → invalid URL → tell user to verify URL

## Examples

Input: `task_url=https://app.asana.com/0/1234/5678`

Expected: full task detail rendered as Markdown.
