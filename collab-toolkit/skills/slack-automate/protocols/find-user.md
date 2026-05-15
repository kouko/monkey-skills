---
name: find-user
purpose: Search workspace users by name / email / handle, return profile + activity status.
---

## Inputs

- `query`: required. Name fragment, email, or handle.
- `--json`: optional.

## Output

Default Markdown:
```
## User search: "alice"

**Alice Chen** · @alice · alice@company.com · Active (last seen 2 min ago)
Title: Senior Engineer · Team: Platform
Timezone: PST

**Alice Lee** · @alicelee · alice@elsewhere.com · Away (idle 12 min)
...
```

`--json`: array of `{ name, handle, email, status, title, team, timezone }`.

> **Output spec note**: `handle`, `email`, `status`, `title`, `team`, `timezone` are extracted from AT snapshot `row` elements in the People grid. These fields are speculative (v0.1.0 unverified) — see `references/ui-patterns.md` AT-schema notes. All use `// "(unknown)"` / `// ""` fallbacks. `last_seen` is not included in v0.1.0 output (AT snapshot does not reliably expose it as a separate field).

## Procedure

```bash
QUERY="$1"
[ -z "$QUERY" ] && { echo "ERR: query required"; exit 1; }

ABX_SERVICE=slack abx open https://app.slack.com
ABX_SERVICE=slack abx wait --load networkidle

# Open People view — sidebar link or top bar People button
SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)
PEOPLE_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="link" and (.name=="People" or .name=="More")) | .ref' | head -1)
[ -z "$PEOPLE_REF" ] && { echo "ERR: People link not found — see failure-modes.md for free-tier fallback"; exit 1; }
ABX_SERVICE=slack abx click "$PEOPLE_REF"
ABX_SERVICE=slack abx wait --load networkidle

# Fill search in People view
SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)
SEARCH_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="textbox") | .ref' | head -1)
[ -n "$SEARCH_REF" ] && ABX_SERVICE=slack abx click "$SEARCH_REF"
ABX_SERVICE=slack abx fill --active "$QUERY"
ABX_SERVICE=slack abx wait 500
SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)

# User results are role="row" within People grid
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="row")
  | "\(.name // "(unknown)") · \(.handle // "") · \(.email // "") · \(.status // "")"
'
```

## Failure modes

- "People" view not accessible (free Slack tier may not have it) → graceful fallback: use @mention typeahead in any open channel. Navigate to a channel, type `@<query>` in the message input, snapshot the suggestion list:
  ```bash
  # Fallback: @-typeahead in message input
  ABX_SERVICE=slack abx fill --active "@$QUERY"
  ABX_SERVICE=slack abx wait 500
  SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)
  echo "$SNAP" | jq -r '.elements[] | select(.role=="option") | .name // "(unknown)"'
  ```
- Auth expiry → "Auth expiry"
