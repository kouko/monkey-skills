---
name: channel-read
purpose: Read recent N messages in a channel, with optional thread expansion.
---

## Inputs

- `channel`: required. Channel name (e.g., `engineering`) or full URL.
- `limit`: optional, default 20. Number of recent messages.
- `expand_threads`: optional bool, default false.
- `--json`: optional.

## Output

Default Markdown:
```
## #engineering (last 20 messages, 3 threads expanded)

**alice** · 2026-05-15 09:00
Standup starting in 5 minutes.
└─ 3 replies (expanded below)
    **bob**: On my way
    ...

**carol** · 2026-05-15 08:45
PR #234 ready for review.
```

`--json`: `[ { user, timestamp, text, thread_count, thread_messages?: [...] } ]`.

> **Output spec note**: `user`, `timestamp`, `text`, `thread_count` are extracted from AT snapshot `article` elements. These fields are speculative (v0.1.0 unverified) — see `references/ui-patterns.md` AT-schema notes. All are guarded with `// "(unknown)"` / `// 0` fallbacks.

## Procedure

```bash
CHANNEL="$1"
LIMIT="${2:-20}"
EXPAND="${3:-false}"

# Resolve channel — name or URL
case "$CHANNEL" in
  http*)
    ABX_SERVICE=slack abx open "$CHANNEL"
    ABX_SERVICE=slack abx wait --load networkidle
    ;;
  *)
    # Navigate to workspace, find channel in sidebar
    ABX_SERVICE=slack abx open https://app.slack.com
    ABX_SERVICE=slack abx wait --load networkidle
    SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)
    CHANNEL_REF=$(echo "$SNAP" | jq -r --arg c "$CHANNEL" '
      .elements[] | select(.role=="treeitem" and ((.name // "") | startswith($c))) | .ref
    ' | head -1)
    [ -z "$CHANNEL_REF" ] && { echo "ERR: Channel '$CHANNEL' not found in sidebar"; exit 1; }
    ABX_SERVICE=slack abx click "$CHANNEL_REF"
    ABX_SERVICE=slack abx wait --load networkidle
    ;;
esac

# Snapshot channel — interactive elements only for speed
SNAP=$(ABX_SERVICE=slack abx snapshot -i --json)

# Each message is role="article" within role="region" name="Conversation"
echo "$SNAP" | jq -r --argjson limit "$LIMIT" '
  [.elements[]
    | select(.role=="article")
    | {
        user: (.author // "(unknown)"),
        timestamp: (.timestamp // ""),
        text: (.text // ""),
        thread_count: (.thread_count // 0)
      }
  ]
  | .[-$limit:]
  | .[]
  | "**\(.user)** · \(.timestamp)\n\(.text)\n"
'

# Thread expansion (if requested) — iterate messages with thread_count > 0, click "N replies" button
# Click: role="link" name starts with "N reply" or "N replies" (see references/ui-patterns.md)
# Then snapshot the Thread complementary panel for replies
# (Full expand implementation: delegate to protocols/thread-read.md per-thread)
```

## Failure modes

- Channel not found in sidebar → user lacks access or channel is hidden under "More"
- Auth expiry → "Auth expiry"
