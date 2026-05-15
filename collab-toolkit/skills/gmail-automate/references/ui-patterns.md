# Gmail UI Patterns — Semantic Selector Reference

> **Source of truth for semantic selectors used in this skill's protocols.**
> When Gmail ships a UI change that breaks a protocol, update this file first,
> then re-derive the protocol's jq filter.

## Refresh playbook

When a protocol fails with "UI changed: ...":

1. Run `ABX_SERVICE=gmail abx snapshot -i --json > /tmp/gmail-snap.json` against `mail.google.com`
2. Inspect `/tmp/gmail-snap.json` for elements near the failing area
3. Identify the new role+name combination
4. Update the entry below
5. Update the failing protocol's jq filter

## Top bar

| Element | role | name | Notes |
|---|---|---|---|
| Search combobox | `combobox` | `Search mail` | Primary search input — used by mail-search; may also appear as `textbox` |
| Search button (icon) | `button` | `Search Mail` or `Search` | Fallback if combobox not initially visible |
| Settings gear | `button` | `Settings` | Top-right settings icon — not used in v0.1.0 read-only |
| Compose button | `button` | `Compose` | Write-only; not used in v0.1.0 |

## Mail list / inbox grid

| Element | role | name | Notes |
|---|---|---|---|
| Mail row | `row` | Concatenated from / subject / snippet / date | One per thread in list view — used by mail-search, inbox-summary, label-read |
| Mail row cell — from | `cell` / `gridcell` | Sender display name or email | `cells[0].name // ""` **— unverified, see "AT-schema notes"** |
| Mail row cell — subject+snippet | `cell` / `gridcell` | `Subject · snippet text` | `cells[1].name // ""` **— unverified, see "AT-schema notes"** |
| Mail row cell — date | `cell` / `gridcell` | `May 14` or `10:05 AM` (today) | `cells[2].name // ""` **— unverified, see "AT-schema notes"** |
| Star button | `button` | `Starred` or `Not starred` | Per-row star toggle — not used in v0.1.0 |
| Unread indicator | — | `.unread` field or bold cell text | Gmail may expose `.unread: true` on row AT node, or may not expose it at all **— unverified, see "AT-schema notes"** |

## Category tabs

| Element | role | name | Notes |
|---|---|---|---|
| Primary tab | `tab` | `Primary` | Default inbox tab |
| Social tab | `tab` | `Social` | Present only if Categories enabled in Settings → Inbox |
| Promotions tab | `tab` | `Promotions` | Present only if Categories enabled |
| Updates tab | `tab` | `Updates` | Present only if Categories enabled |
| Forums tab | `tab` | `Forums` | Present only if Categories enabled (less common) |

Tab presence depends on account settings. If "Categories" is disabled, only Primary is shown.

## Sidebar labels

| Element | role | name | Notes |
|---|---|---|---|
| Inbox link | `link` | `Inbox` | Standard inbox navigation |
| Starred link | `link` | `Starred` | System label |
| Sent link | `link` | `Sent` | System label |
| Label link | `link` | Display name of label | User-defined labels — used by label-read |
| Nested label link | `link` | `ParentLabel/ChildLabel` or just `ChildLabel` | Gmail may display nested name as full path or just child **— unverified, see "AT-schema notes"** |
| Label expand button | `button` or `treeitem` | Parent label name | Expands to show child labels — speculative role |
| More labels | `link` or `button` | `More` or `Show all labels` | Reveals labels below the visible fold |

## Thread view

| Element | role | name | Notes |
|---|---|---|---|
| Message body region | `region` | `Message body` or `Email body` | Container for email body text — used by thread-read **— unverified, see "AT-schema notes"** |
| Expand all button | `button` | `Expand all` | Visible when multiple messages are collapsed |
| Show trimmed content | `button` | `Show trimmed content` or `Show clipped message` | Expands quoted/trimmed content within a message |
| Attachment chip / link | `link` | `filename.ext (size)` | File attachment — used by thread-read **— unverified, see "AT-schema notes"** |
| Message header / from | `link` | Sender email or display name | From address in thread header |
| Thread subject heading | `heading` | Thread subject | Page heading for thread view |

## AT-schema notes (v0.1.0 unverified)

Some field paths used in the protocols above are educated guesses about agent-browser's AT-snapshot output. They have NOT been verified against a live snapshot yet (v0.1.0 ships with defensive `// ""` / `// "(unknown)"` fallbacks). Validate during first dogfood run:

| Field path | Used by | Status |
|---|---|---|
| `.elements[] \| select(.role=="combobox" and ((.name // "") \| contains("Search mail"))) \| .ref` | mail-search | ❓ unverified — Gmail search input role may be `textbox` not `combobox`; fallback to textbox included |
| `.elements[] \| select(.role=="row") \| .cells[0].name // ""` (from cell) | mail-search, inbox-summary, label-read | ❓ unverified — `.cells[]` sub-array may not exist in agent-browser flat AT snapshot; fallback to `.name // "(unknown)"` |
| `.elements[] \| select(.role=="row") \| .cells[1].name // ""` (subject+snippet cell) | mail-search, inbox-summary, label-read | ❓ unverified — same as above |
| `.elements[] \| select(.role=="row") \| .cells[2].name // ""` (date cell) | mail-search, inbox-summary, label-read | ❓ unverified — same as above |
| `.elements[] \| select(.role=="row") \| .unread // false` (unread indicator) | inbox-summary | ❓ unverified — Gmail may not expose `.unread` as AT field; v0.1.0 reports "(unread count unknown)" if always 0 on non-empty inbox |
| `.elements[] \| select(.role=="tab" and ((.name // "") \| contains("Primary")))` (category tab) | inbox-summary | ❓ unverified — Gmail may render category tabs as `link` or `button` instead of `tab`; only `tab` role tried in v0.1.0 |
| `.elements[] \| select(.role=="link" and ((.name // "") \| contains($label)))` (label link) | label-read | ❓ unverified — nested label links may appear only after parent expand; full path vs. child-name-only rendering unverified |
| `.elements[] \| select(.role=="treeitem" ...)` (label as tree navigation) | label-read | ❓ unverified — Gmail may use `role=treeitem` for label tree; fallback included |
| `.elements[] \| select(.role=="region" and ((.name // "") \| test("(?i)message body")))` | thread-read | ❓ unverified — Gmail message body region name may differ or may not exist if body is in an iframe not flattened by agent-browser |
| `.elements[] \| select(.role=="link" and ((.name // "") \| test("(?i)\\\\.(pdf\|xlsx?...)")))` (attachment chip) | thread-read | ❓ unverified — attachment chips may be `role=button` not `role=link`; name format (file.ext + size) is speculative |
| `.cells // []` sub-array on row elements (all row-cell paths above) | mail-search, inbox-summary, label-read | ❌ PROBABLY ABSENT — agent-browser AT snapshot is flat; `.cells[]` is a WCAG concept but may not appear as a sub-array on row elements. All protocols fall back to `.name // "(unknown)"` for full row text. |
| `.parent.*` filter (scoping rows to specific grid, labels to sidebar section) | all protocols | ❌ DROPPED — agent-browser flat snapshot does not expose `.parent`. All filters use permissive role+name `contains()` guards. Precision trade-off accepted until live-snapshot verification. |

Refresh playbook for these: run `ABX_SERVICE=gmail abx snapshot -i --json > /tmp/gmail-snap.json`, inspect the actual schema, update the jq filter, and remove the corresponding row from this table.
