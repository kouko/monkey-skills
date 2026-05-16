---
name: database-query
purpose: Query a Notion database with multi-property filters and sort, return matching rows.
---

## Inputs

- `database_url`: required.
- `filters`: optional JSON array, each `{ property, operator, value }`.
- `sort`: optional `property:direction`.
- `--json`: optional.

## Output

Default Markdown: table of rows with key properties.

`--json`: array of row objects.

> **Output spec note**: Row cells are extracted via `.cells[]?.text`. The `.cells[]` path is speculative (v0.1.0 unverified) — see `references/ui-patterns.md` AT-schema notes. Falls back to `""` per cell.

## Procedure

```bash
URL="$1"
[ -z "$URL" ] && { echo "ERR: database_url required"; exit 1; }

ABX_SERVICE=notion abx open "$URL"
ABX_SERVICE=notion abx wait --load networkidle
SNAP=$(ABX_SERVICE=notion abx snapshot -i --json)

# Database rows are role="row" within role="grid"
# NOTE: .parent.role filter dropped (Pattern F) — agent-browser flat snapshot has no .parent.
# Accept all role="row" elements; precision to be improved after live-snapshot verification (see ui-patterns.md).
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="row")
  | [.cells[]? | (.text // "")] | join(" | ")
'

# Filter / sort application:
# Notion's filter UI is interactive — implementer adds clicks on filter chip + property selector + value input.
# Reference role+name in references/ui-patterns.md.
```

## Failure modes

- Database not found → invalid URL
- Filter property doesn't exist → error message naming the bad property
- No `row` elements in snapshot → UI evolution or database is empty
