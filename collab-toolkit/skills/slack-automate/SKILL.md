---
name: slack-automate
description: Slack automation via agent-browser browser-driving. Use for: search-messages with from/in/before/after operators, channel-read with thread expansion, thread-read with replies, find-user by name/email/handle. Read-only v0.2.0 — search and fetch only, no writes. Supports EN / zh-TW / ja UI labels. Slack 自動化、メッセージ読取、ヘッドレス、多言語UI対応。Slack 自動化・訊息讀取・無頭背景・多語言介面支援。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*)
---

# slack-automate

Inherits patterns from agent-browser's [official slack skill](https://github.com/vercel-labs/agent-browser/blob/main/skill-data/slack/SKILL.md). v0.2.0 extends with zh-TW / ja UI label support.

## Prerequisites

`/collab-setup` once. Login wall → reauth.

## Hero protocols

- `protocols/search-messages.md`
- `protocols/channel-read.md`
- `protocols/thread-read.md`
- `protocols/find-user.md`

## Workflow pattern

```bash
abx open https://app.slack.com
abx wait --load networkidle
abx snapshot -i
abx click @eN
abx snapshot -i
```

## Key elements (locale-dependent — see per-protocol Localized labels)

- Sidebar tabs (Home / DMs / Activity)
- Search button + input
- Channel treeitem
- "More unreads" button
- Conversation region + article messages
- Thread complementary panel

## Failure modes

See `references/failure-modes.md`.
