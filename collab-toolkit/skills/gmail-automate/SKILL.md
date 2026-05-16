---
name: gmail-automate
description: Gmail automation via agent-browser browser-driving. Use for: mail-search with operators, thread-read, inbox-summary by Category tabs, label-read with nested labels. Read-only v0.1.6. Supports EN / zh-TW / ja UI labels. Gmail 自動化、メール読取、多言語UI対応。Gmail 自動化・郵件讀取・多語言介面支援。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*)
---

# gmail-automate

Follows agent-browser text-snapshot conventions. v0.1.6 supports EN / zh-TW / ja UI labels.

## Prerequisites

`/collab-setup` once. Login wall → reauth.

## Hero protocols

- `protocols/mail-search.md`
- `protocols/thread-read.md`
- `protocols/inbox-summary.md`
- `protocols/label-read.md`

## Workflow pattern

```bash
abx open https://mail.google.com
abx wait --load networkidle
abx snapshot -i
abx click @eN
abx snapshot -i
```

## Failure modes

See `references/failure-modes.md`.
