---
name: gcal-automate
description: Google Calendar automation via agent-browser browser-driving. Use for: agenda-view (today/week/range), event-search, find-free-slots, shared-calendar-read. Read-only v0.1.6. Supports EN / zh-TW / ja UI labels. Google カレンダー自動化、予定読取、多言語UI対応。Google 行事曆自動化・行程讀取・多語言介面支援。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*)
---

# gcal-automate

Follows agent-browser text-snapshot conventions. v0.1.6 supports EN / zh-TW / ja UI labels.

## Prerequisites

`/collab-setup` once. Login wall → reauth.

## Hero protocols

- `protocols/agenda-view.md`
- `protocols/event-search.md`
- `protocols/find-free-slots.md`
- `protocols/shared-calendar-read.md`

## Workflow pattern

```bash
abx open https://calendar.google.com
abx wait --load networkidle
abx snapshot -i
abx click @eN
abx snapshot -i
```

## Failure modes

See `references/failure-modes.md`.
