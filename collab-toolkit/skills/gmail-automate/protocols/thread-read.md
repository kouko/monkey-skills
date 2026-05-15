---
name: thread-read
purpose: Open a Gmail thread by URL or thread ID, expand all collapsed messages, and extract per-message from / to / cc / date / body / attachments.
---

## Inputs

- `thread_url`: required. Full Gmail thread URL (e.g., `https://mail.google.com/mail/u/0/#inbox/FMfcgzQXJGZK...`) OR a Gmail thread ID (16-character hex, e.g., `FMfcgzQXJGZK`). If a bare ID is provided, the protocol constructs the URL as `https://mail.google.com/mail/u/0/#inbox/<id>`.
- `--json`: optional.

## Output

Default Markdown (v0.1.0 — body text is first visible text of message region):
```
## Thread: Re: Q2 Budget — 3 messages

### Message 1
- From: alice@example.com
- To: team@example.com
- Date: Thu, May 14, 2026 at 10:05 AM
- Body: Hi team, please find the updated budget attached...
- Attachments: Q2_budget.xlsx

### Message 2
- From: bob@example.com
- To: alice@example.com
- Date: Thu, May 14, 2026 at 11:30 AM
- Body: Thanks Alice, I'll review by EOD.
- Attachments: (none)
```

`--json`: `{ thread_url, subject, messages: [{ from, to, cc, date, body, attachments: [{ name }] }] }`.

> **Output spec note**: `body` is the accessible text of `role=region name="Message body"` — a speculative path (v0.1.0 unverified). Gmail renders message bodies inside a sandboxed iframe in the live DOM; the AT snapshot may expose only the outer region with partial text. Full body text extraction fidelity depends on agent-browser's iframe flattening behavior (unverified). All fields fall back to `// ""`. Attachment names are extracted from `role=link` elements within the attachment region — link `.name // ""` may include file size suffix. See `references/ui-patterns.md` AT-schema notes.

## Procedure

```bash
THREAD_INPUT="$1"
[ -z "$THREAD_INPUT" ] && { echo "ERR: thread_url or thread ID required"; exit 1; }

# Construct URL if bare ID given (no http prefix)
if echo "$THREAD_INPUT" | grep -q '^https'; then
  THREAD_URL="$THREAD_INPUT"
else
  THREAD_URL="https://mail.google.com/mail/u/0/#inbox/${THREAD_INPUT}"
fi

ABX_SERVICE=gmail abx open "$THREAD_URL"
ABX_SERVICE=gmail abx wait --load networkidle

# Login wall guard
SNAP=$(ABX_SERVICE=gmail abx snapshot -i --json)
TITLE_CHECK=$(echo "$SNAP" | jq -r '.title // ""')
if echo "$TITLE_CHECK" | grep -qiE "sign in|log in|accounts.google.com"; then
  echo "ERR: login wall detected — log into Gmail in Chrome (shared mode) or run /collab-setup --reauth gmail" >&2
  exit 1
fi

# Check for thread subject in page title or heading
SUBJECT=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="heading") | .name // ""' | head -1)
SUBJECT="${SUBJECT:-$(echo "$SNAP" | jq -r '.title // ""' | sed -E 's/^[Gg]mail[[:space:]]*[-–—][[:space:]]*//')}"

# Expand all collapsed messages if "Expand all" button is present
EXPAND_REF=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="button" and ((.name // "") | test("(?i)expand all"))) | .ref' | head -1)
if [ -n "$EXPAND_REF" ]; then
  ABX_SERVICE=gmail abx click "$EXPAND_REF"
  ABX_SERVICE=gmail abx wait 800
  SNAP=$(ABX_SERVICE=gmail abx snapshot -i --json)
fi

# Also look for individually collapsed message headers (role=button with collapsed/expand indicator)
# Gmail uses "Show trimmed content" or individual message collapse buttons
# Iterate up to 10 such buttons to expand nested messages
for _i in $(seq 1 10); do
  TRIMMED_REF=$(echo "$SNAP" | jq -r '
    .elements[]
    | select(
        .role=="button"
        and ((.name // "") | test("(?i)show trimmed|expand|clipped"))
      )
    | .ref
  ' | head -1)
  [ -z "$TRIMMED_REF" ] && break
  ABX_SERVICE=gmail abx click "$TRIMMED_REF"
  ABX_SERVICE=gmail abx wait 500
  SNAP=$(ABX_SERVICE=gmail abx snapshot -i --json)
done

# Pattern H: verify thread structure present (at least one message region)
BODY_CHECK=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="region" and ((.name // "") | test("(?i)message body|email body"))) | .ref' | head -1)
if [ -z "$BODY_CHECK" ]; then
  # Fallback: check for any region or article that could be a message container
  REGION_CHECK=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="region" or .role=="article") | .ref' | head -1)
  if [ -z "$REGION_CHECK" ]; then
    echo "ERR: UI changed: no message body region found in thread — Gmail thread structure may have changed" >&2
    exit 1
  fi
fi

# Extract per-message metadata from structural elements
# Gmail thread: each message has a role=region name="Message body" (or similar)
# From / to / cc / date appear as text nodes or heading-like elements near the message header

# Extract all message body regions
# NOTE: .parent.* dropped (Pattern F) — flat snapshot; accept all message body regions
# NOTE: ((.name // "") | test(...)) guarded against null (Pattern G)
MSG_BODIES=$(echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="region" and ((.name // "") | test("(?i)message body|email body")))
  | .name // "(no body text)"
')

# Extract from: fields — role=link or role=text within message header area (speculative)
# v0.1.0: extract by looking for elements whose name matches email address pattern
# NOTE: full per-message grouping (header→body→attachment per message) requires parent-child
# inference which is not available in v0.1.0 flat snapshot. All fields are extracted
# globally and listed sequentially.
FROM_LIST=$(echo "$SNAP" | jq -r '
  .elements[]
  | select(
      .role=="link"
      and ((.name // "") | test("@"))
    )
  | .name // ""
' | head -20)

# Extract attachment links — role=link within attachment region
# NOTE: attachment region name is speculative ("Attachments" region name may differ)
ATTACHMENTS=$(echo "$SNAP" | jq -r '
  .elements[]
  | select(
      .role=="link"
      and ((.name // "") | test("(?i)\\.(pdf|xlsx?|docx?|pptx?|zip|csv|txt|png|jpe?g|gif)"))
    )
  | .name // ""
')

# Output
echo "## Thread: ${SUBJECT:-(unknown subject)}"
echo

# Message count approximation from body regions
MSG_COUNT=$(echo "$MSG_BODIES" | grep -c . || true)
[ "$MSG_COUNT" -eq 0 ] && MSG_COUNT=1
echo "_${MSG_COUNT} message(s) detected_"
echo

# Per-message output: v0.1.0 emits sequential fields (per-message grouping deferred to v0.2.0)
# Full grouping requires inferring which from/body/attachment belong to the same message,
# which requires parent-child AT structure not available in v0.1.0 flat snapshot.
echo "### From addresses found in thread"
if [ -n "$FROM_LIST" ]; then
  echo "$FROM_LIST" | while IFS= read -r f; do
    echo "- $f"
  done
else
  echo "(none detected)"
fi
echo

echo "### Message bodies"
if [ -n "$MSG_BODIES" ]; then
  echo "$MSG_BODIES" | while IFS= read -r line; do
    echo "> $line"
  done
else
  echo "(body text not accessible — Gmail iframe may not be flattened in AT snapshot)"
fi
echo

echo "### Attachments"
if [ -n "$ATTACHMENTS" ]; then
  echo "$ATTACHMENTS" | while IFS= read -r att; do
    echo "- $att"
  done
else
  echo "(none)"
fi
```

## Notes

- Gmail collapses all but the last message in a thread by default. This protocol attempts "Expand all" then iterates "Show trimmed content" buttons; up to 10 expand clicks are attempted.
- Per-message grouping (from/to/cc/date/body/attachments mapped per-message) requires parent-child inference from the AT tree — not available in v0.1.0 flat snapshot. All fields are extracted globally and listed sequentially. Full per-message grouping is deferred to v0.2.0 after live AT-snapshot verification.
- Body text fidelity depends on whether agent-browser flattens Gmail's sandboxed message iframe into the AT snapshot. If iframe is not flattened, body region will contain only limited text. See `references/failure-modes.md` → "iframe body extraction".

## Failure modes

- Thread URL missing → validation error
- Login wall detected → auth expiry
- No message body region AND no region/article → UI evolution → exits 1 with `ERR: UI changed`
- No message body region but region/article present → valid thread with non-standard body structure → fallback output
- Expand all button absent → messages may already be expanded (no action needed) or Gmail changed button name
- Attachment extraction empty → no attachments or attachment link names don't match file extension pattern
- Gmail iframe not flattened → body text appears empty or partial; known v0.1.0 limitation
