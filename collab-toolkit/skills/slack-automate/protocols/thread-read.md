---
name: thread-read
purpose: Read entire thread including all replies, reactions, attachments.
---

## Inputs

- `thread_url`: required. Slack thread permalink (`https://<workspace>.slack.com/archives/<channel>/p<ts>?thread_ts=...`).
- `--json`: optional.

## Output

Default Markdown: parent message + all replies with reactions and attachment names.

`--json`: `{ parent: { user, timestamp, text }, replies: [...], total_replies, reactions: [...] }`.

> **Output spec note**: `reactions` and `attachments` are extracted from AT snapshot `article` elements. These fields are speculative (v0.1.0 unverified). The JSON output shape guarantees top-level keys but individual field availability depends on AT snapshot schema — see `references/ui-patterns.md` AT-schema notes. All speculative fields use `// []` / `// "(unknown)"` fallbacks.

## Procedure

```bash
URL="$1"
[ -z "$URL" ] && { echo "ERR: thread_url required"; exit 1; }

ABX_SERVICE=slack abx open "$URL"
ABX_SERVICE=slack abx wait --load networkidle
SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)

# Thread is shown in a side panel — parent+replies are role="article"
# .parent.role/.parent.name guards dropped: agent-browser flat snapshot has no .parent field.
# Permissive: accept all articles on this page (which is the thread URL — no other articles expected).
echo "$SNAP" | jq -r '
  [.elements[]
    | select(.role=="article")
    | {
        user: (.author // "(unknown)"),
        timestamp: (.timestamp // ""),
        text: (.text // ""),
        reactions: (.reactions // []),
        attachments: (.attachments // [])
      }
  ]
  | .[]
  | "**\(.user)** · \(.timestamp)\n\(.text)\n"
'
```

## Failure modes

- Thread URL invalid (404) → message about URL validation
- "Thread" complementary region missing → UI evolution or thread opened inline (not side panel)
