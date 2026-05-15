# Slack UI Patterns — Semantic Selector Reference

> **Source of truth for semantic selectors used in this skill's protocols.**
> When Slack ships a UI change that breaks a protocol, update this file first,
> then re-derive the protocol's jq filter.

Inherits and extends patterns from agent-browser's own `skill-data/slack/SKILL.md`.

## Refresh playbook

When a protocol fails with "UI changed: ...":

1. Run `ABX_SERVICE=slack abx snapshot -i --json > /tmp/slack-snap.json` against the affected page
2. Inspect `/tmp/slack-snap.json` for elements near the failing area
3. Identify the new role+name combination
4. Update the entry below
5. Update the failing protocol's jq filter

## Sidebar

| Element | role | name | Notes |
|---|---|---|---|
| Home tab | `tab` | `Home` | Top of sidebar |
| DMs tab | `tab` | `DMs` | |
| Activity tab | `tab` | `Activity` | Has unread count badge |
| Channel item | `treeitem` | (channel name; level=2 nested under section) | Each channel — used by channel-read |
| DM item | `treeitem` | (user name; under Direct Messages section) | |
| More unreads button | `button` | `More unreads` | Visible when unread count > 0 |
| People nav link | `link` | `People` or `More` | Sidebar — used by find-user |

## Search

| Element | role | name | Notes |
|---|---|---|---|
| Search button | `button` | `Search` | Top bar — used by search-messages |
| Search input (after click) | `textbox` | `Search` | Modal — used by search-messages |

## Messages (Conversation region)

| Element | role | name | Notes |
|---|---|---|---|
| Conversation container | `region` | `Conversation` | All messages |
| Message | `article` | (none — has `.author` `.timestamp` `.text` props **— unverified, see "AT-schema notes"**) | Each msg is article — used by channel-read |
| Thread reply count link | `link` | starts with `N reply` or `N replies` | Click to expand thread side panel |

## Thread panel

| Element | role | name | Notes |
|---|---|---|---|
| Thread side panel | `complementary` | `Thread` | Slides in from right — used by thread-read |
| Thread message | `article` | (within complementary>Thread **— unverified, see "AT-schema notes"**) | Parent + replies — used by thread-read |

## Search results

| Element | role | name | Notes |
|---|---|---|---|
| Search results container | `list` or `region` | starts with `Search results` **— unverified, see "AT-schema notes"** | Wraps result listitems |
| Result item | `listitem` | (within Search results region **— unverified, see "AT-schema notes"**) | Each result — used by search-messages |

## People view

| Element | role | name | Notes |
|---|---|---|---|
| People grid | `grid` | `People` | Container |
| User row | `row` | (user display name — has `.handle` `.email` `.status` props **— unverified, see "AT-schema notes"**) | Each user — used by find-user |

## AT-schema notes (v0.1.0 unverified)

Some field paths used in the protocols above are educated guesses about agent-browser's AT-snapshot output. They have NOT been verified against a live snapshot yet (v0.1.0 ships with defensive `// "(unknown)"` fallbacks for these). Validate during first dogfood run:

| Field path | Used by | Status |
|---|---|---|
| `.elements[] \| select(.role=="article") \| .author` | channel-read, thread-read | ❓ unverified — may be nested in child element |
| `.elements[] \| select(.role=="article") \| .timestamp` | channel-read, thread-read | ❓ unverified — may be a child `time` element |
| `.elements[] \| select(.role=="article") \| .text` | channel-read, thread-read | ❓ unverified — message body may be nested |
| `.elements[] \| select(.role=="article") \| .thread_count` | channel-read | ❓ unverified |
| `.elements[] \| select(.role=="article") \| .reactions` | thread-read | ❓ unverified |
| `.elements[] \| select(.role=="article") \| .attachments` | thread-read | ❓ unverified |
| `.elements[] \| select(.role=="listitem") \| .channel / .user / .text` | search-messages | ❓ unverified — fields may be nested child elements rather than direct props |
| `.elements[] \| select(.role=="row") \| .handle / .email / .status` | find-user | ❓ unverified — user row props may be child cells not direct props |
| `.parent.name` / `.parent.role` filters | search-messages, thread-read | ❓ unverified — nested parent reference may not be in flat snapshot |

Refresh playbook for these: run `ABX_SERVICE=slack abx snapshot -i --json > /tmp/slack-snap.json`, inspect the actual schema, update the jq filter, and remove the corresponding row from this table.
