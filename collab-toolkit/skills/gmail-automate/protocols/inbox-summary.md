---
name: inbox-summary
purpose: Open Gmail Inbox, iterate Category tabs (Primary / Social / Promotions / Updates), count unread messages, and return first 5 subjects per category.
---

## Inputs

- `tabs`: optional. Comma-separated list of tabs to summarize. Default: `Primary,Social,Promotions,Updates`. If a tab is absent (account settings may show only Primary), it is silently skipped.
- `top_n`: optional. Number of rows to extract per tab. Default: `5`.
- `--json`: optional.

## Output

Default Markdown (v0.1.0 — row names extracted as raw strings):
```
## Gmail Inbox Summary

### Primary (3 unread)
1. alice@example.com — Q2 Budget Review — May 14
2. bob@example.com — Action needed: sign the doc — May 13
3. no-reply@service.com — Your subscription renews tomorrow — May 12

### Social (0 unread)
1. linkedin@email.linkedin.com — 5 new connections this week — May 13

### Promotions (12 unread)
1. deals@shop.com — Flash sale: 40% off — May 14
...

### Updates (2 unread)
1. alerts@bank.com — Transaction confirmed — May 14
```

`--json`: `{ tabs: [{ name, unread_count, rows: [{ from, subject, date }] }] }`.

> **Output spec note**: `unread_count` is derived by counting row elements whose name or accessible state indicates bold/unread status — a speculative heuristic (v0.1.0 unverified). v0.1.0 approximates unread count by looking for rows with `role=row` whose `.name // ""` contains an unread indicator; actual `.unread` or `.bold` AT field existence is unverified. If AT does not expose unread state, v0.1.0 reports `(unread count unknown)`. Row `from`, `subject`, `date` fields come from `.cells[n].name // ""` — speculative; fallback to full row `.name // "(unknown)"`. See `references/ui-patterns.md` AT-schema notes.

## Procedure

```bash
TABS="${1:-Primary,Social,Promotions,Updates}"
TOP_N="${2:-5}"

ABX_SERVICE=gmail abx open https://mail.google.com/mail/u/0/#inbox
ABX_SERVICE=gmail abx wait --load networkidle

# Login wall guard
SNAP=$(ABX_SERVICE=gmail abx snapshot -i --json)
TITLE_CHECK=$(echo "$SNAP" | jq -r '.title // ""')
if echo "$TITLE_CHECK" | grep -qiE "sign in|log in|accounts.google.com"; then
  echo "ERR: login wall detected — log into Gmail in Chrome (shared mode) or run /collab-setup --reauth gmail" >&2
  exit 1
fi

echo "## Gmail Inbox Summary"
echo

# Iterate tabs
IFS=',' read -ra TAB_LIST <<< "$TABS"

for TAB_NAME in "${TAB_LIST[@]}"; do
  TAB_NAME="$(echo "$TAB_NAME" | tr -d ' ')"

  # Find category tab — role=tab name="Primary" / "Social" / "Promotions" / "Updates"
  TAB_REF=$(echo "$SNAP" | jq -r --arg t "$TAB_NAME" '
    .elements[]
    | select(.role=="tab" and ((.name // "") | contains($t)))
    | .ref
  ' | head -1)

  if [ -z "$TAB_REF" ]; then
    # Tab may not exist (account without category tabs, or tab hidden)
    # Silently skip — document in output
    echo "### $TAB_NAME"
    echo "_Tab not present in this account (category tabs may be disabled)_"
    echo
    continue
  fi

  # Click tab and wait for content to load
  ABX_SERVICE=gmail abx click "$TAB_REF"
  ABX_SERVICE=gmail abx wait 800
  SNAP=$(ABX_SERVICE=gmail abx snapshot -i --json)

  # Pattern H: verify tab content loaded (at least one row visible)
  ROW_CHECK=$(echo "$SNAP" | jq -r '.elements[] | select(.role=="row") | .ref' | head -1)

  # Extract rows — role=row in mail list grid
  # NOTE: .parent.* dropped (Pattern F) — accept all role=row in snapshot
  # NOTE: (.cells // []) guarded against null (Pattern A)
  # NOTE: (.name // "") guarded before contains/test (Pattern G)
  ROWS=$(echo "$SNAP" | jq -r --argjson n "$TOP_N" '
    [
      .elements[]
      | select(.role=="row")
    ]
    | .[0:$n]
    | to_entries[]
    | "\(.key + 1). \(
        if (.value.cells // []) | length > 0
        then "\(.value.cells[0].name // "(unknown)") — \(.value.cells[1].name // "(unknown)") — \(.value.cells[2].name // "")"
        else (.value.name // "(unknown)")
        end
      )"
  ')

  # Approximate unread count: count rows where name does not start with "Re:" and appears bold
  # v0.1.0: use row count as proxy if .unread field absent
  # NOTE: .unread field existence is speculative; fallback to "(unread count unknown)"
  UNREAD_COUNT=$(echo "$SNAP" | jq -r '
    [
      .elements[]
      | select(
          .role=="row"
          and ((.unread // false) == true)
        )
    ] | length
  ')
  # If unread count is 0 and we have rows, .unread may not be exposed — report as unknown
  TOTAL_ROWS=$(echo "$SNAP" | jq -r '[.elements[] | select(.role=="row")] | length')
  if [ "$UNREAD_COUNT" = "0" ] && [ "${TOTAL_ROWS:-0}" -gt 0 ]; then
    UNREAD_LABEL="(unread count unknown — .unread field not in AT snapshot)"
  else
    UNREAD_LABEL="$UNREAD_COUNT unread"
  fi

  echo "### $TAB_NAME ($UNREAD_LABEL)"
  if [ -z "$ROW_CHECK" ]; then
    echo "_No messages visible or tab content did not load_"
  elif [ -z "$ROWS" ]; then
    echo "(no messages in $TAB_NAME)"
  else
    echo "$ROWS"
  fi
  echo
done
```

## Notes

- Category tabs (Primary / Social / Promotions / Updates) depend on account settings. If "Categories" is disabled in Gmail Settings → Inbox → Inbox type → Default, only the Primary tab is shown and others will report "Tab not present".
- In some Gmail configurations (Workspace or minimal inbox), tabs may appear as navigation links rather than `role=tab` elements. See `references/ui-patterns.md` AT-schema notes.
- Conversation view vs. individual message view affects row count: in conversation view, each thread counts as one row regardless of message count.

## Failure modes

- Login wall detected → auth expiry
- All tabs report "Tab not present" → category tabs disabled in account settings → manually check Gmail Settings → Inbox
- Tab click does not update row list → tab content load failure → wait + retry
- `unread_count` always 0 → `.unread` AT field not exposed in v0.1.0 snapshot; reported as unknown
- Row `.cells` absent → row cell extraction falls back to full `.name` string (less structured but still useful)
- First tab (Primary) is always attempted even if others are absent — at minimum Primary should exist
