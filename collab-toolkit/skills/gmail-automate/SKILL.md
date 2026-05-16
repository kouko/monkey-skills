---
name: gmail-automate
description: Gmail automation via agent-browser browser-driving (Web mode, headless background after first login). Use for: full-text mail-search with Google operators (from:/to:/has:attachment/before:/after:/label:), thread-read with all messages and attachments, inbox-summary across Category tabs, label-read for nested labels. Read-only v0.1.0 — search and fetch only, no writes. Gmail 自動化、メール読取、ヘッドレス。Gmail 自動化・郵件讀取・無頭背景。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*), Bash(jq:*), Bash(mkdir:*)
---

# gmail-automate

Read-only browser automation for Gmail. Uses semantic-first selectors over the accessibility tree — never hardcode `@eN` refs.

## Prerequisites

Run `/collab-setup` once. After that:
- `~/.local/bin/abx` is installed and on PATH
- `~/.config/collab-toolkit/config.json` exists with mode + profile config
- Gmail is verified logged-in via your daily Chrome (shared mode) or dedicated profile

If any protocol fails with "config not found": run `/collab-setup`.
If any protocol fails with "login wall detected" in title: per setup mode, either log into Gmail in your daily Chrome (shared mode) or run `/collab-setup --reauth gmail` (dedicated mode).

## Hero protocols

- `protocols/mail-search.md` — open mail.google.com, use top-bar search combobox (role=combobox name="Search mail"), type query including Google operators (`from:` / `to:` / `has:attachment` / `before:` / `after:` / `label:`), extract result rows with from / subject / snippet / date
- `protocols/thread-read.md` — given `thread_url` or thread ID, open thread, expand all collapsed messages, extract per-message from / to / cc / date / body / attachments
- `protocols/inbox-summary.md` — open Inbox, iterate Category tabs (Primary / Social / Promotions / Updates), snapshot top N rows per tab, return unread counts and first 5 subjects per category
- `protocols/label-read.md` — given `label_name`, click label in sidebar (supports nested labels via `/` path), snapshot result list, return messages with that label

## Selector convention

See `references/ui-patterns.md`. All protocols MUST:
1. `ABX_SERVICE=gmail abx snapshot -i --json` → save to variable or /tmp
2. `jq '.elements[] | select(.role==X and .name==Y) | .ref' | head -1`
3. Empty result → exit with "UI changed: <role>+<name> not found"

## Failure modes

See `references/failure-modes.md`.

## Output mode

Default: human-readable Markdown summary.
`--json` (passthrough to abx): structured JSON for downstream chaining.
