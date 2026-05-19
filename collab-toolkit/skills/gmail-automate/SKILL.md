---
name: gmail-automate
description: Gmail read access via Google Workspace CLI (gws). Read-only v0.2.0 — mail-search / thread-read / inbox-summary / label-read via gws gmail subcommands. Locale-independent. Supersedes the v0.1.6 browser-driving skill. Gmail CLI・公式 Workspace・読取専用。Gmail CLI・官方 Workspace・唯讀。
allowed-tools: Bash(gws:*)
---

# gmail-automate

Read-only Gmail access via the Google Workspace CLI (`gws`). Subcommands invoke the Gmail API and return structured JSON — no UI scraping, no locale tables, no browser daemon.

## Prerequisites

One-time setup:

1. Run `/collab-setup` and accept the gmail row (records intent + verifies the `gws` binary is installed).
2. Set `GOOGLE_CLOUD_PROJECT` in your shell environment (required by `gws` — see `references/failure-modes.md`).
3. Run `gws auth` once — opens a browser for Google OAuth consent. Token refresh is handled automatically thereafter. The same `gws` binary / OAuth grant is shared with `gcal-automate`.

If a protocol fails with an auth error, re-run `gws auth` to refresh the OAuth grant.

## Hero protocols

- `protocols/mail-search.md` — full-text mail search with Gmail operators (`from:`, `subject:`, `has:attachment`, …)
- `protocols/thread-read.md` — fetch a single thread's messages, headers, bodies, attachments
- `protocols/inbox-summary.md` — list recent INBOX messages with unread highlight
- `protocols/label-read.md` — enumerate labels (system + user-defined, including nested)

## Workflow pattern

A typical mail-search invocation:

```bash
gws gmail messages list \
  --query "from:alice@company.com has:attachment after:2026/05/01" \
  --max-results 20
```

Returns a JSON array of message records. Format per the protocol's `## Output` section.

## Failure modes

See `references/failure-modes.md` — OAuth 25-scope limit, `GOOGLE_CLOUD_PROJECT` env requirement, `gws auth` connection-refused timeout, Gmail API rate limits, tool-name verification status.
