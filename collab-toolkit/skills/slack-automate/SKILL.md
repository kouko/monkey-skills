---
name: slack-automate
description: Slack automation via agent-browser browser-driving (Web mode, headless background after first login). Use for: full-text search-messages with from/in/before/after operators, channel-read with thread expansion and reactions, thread-read with all replies/reactions/attachments, find-user by name/email/handle. Read-only v0.1.0 — search and fetch only, no writes. Slack 自動化、メッセージ読取、ヘッドレス。Slack 自動化・訊息讀取・無頭背景。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*), Bash(jq:*), Bash(mkdir:*)
---

# slack-automate

Read-only browser automation for Slack. Uses semantic-first selectors over the accessibility tree — never hardcode `@eN` refs.

## Prerequisites

Run `/collab-setup` once. After that:
- `~/.local/bin/abx` is installed and on PATH
- `~/.config/collab-toolkit/config.json` exists with mode + profile config
- Slack is verified logged-in

If protocol fails with "config not found" → run `/collab-setup`.
If protocol fails with "login wall detected" → shared: log into Slack in daily Chrome; dedicated: `/collab-setup --reauth slack`.

## Hero protocols

- `protocols/search-messages.md` — full-text search with from:/in:/before:/after: operators
- `protocols/channel-read.md` — recent N messages in a channel with thread expansion
- `protocols/thread-read.md` — entire thread including all replies, reactions, attachments
- `protocols/find-user.md` — user search by name / email / handle, returns profile + activity

## Selector convention

See `references/ui-patterns.md`. Inherits patterns from agent-browser's own slack skill (verified 2026-05 against Slack web). All protocols use `ABX_SERVICE=slack abx snapshot -i --json` then jq filter by role+name.

## Failure modes

See `references/failure-modes.md`.

## Output mode

Default Markdown. `--json` for structured output.
