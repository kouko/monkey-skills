---
name: thread-read
purpose: Read a single Gmail thread — all messages, headers, bodies, attachments.
allowed-tools: Bash(gws:*)
---

## Purpose

Return a Markdown rendering of a full Gmail thread: subject, each message's from / to / date / body, and attachment filenames.

## Input

- `thread_id` OR `thread_url`: required. Parse `thread_id` out of a Gmail URL if needed — the hex segment after `/thread/` (e.g. `https://mail.google.com/mail/u/0/#inbox/<thread_id>`).
- `--json`: optional. Skip Markdown formatting, return raw API record.

## Steps

1. Resolve `thread_id` from `thread_url` if needed.

2. Call:

   ```bash
   gws gmail threads get <thread_id>
   ```

   Returns a thread record with `messages: [...]`; each message has `payload.headers`, `payload.parts[]` (MIME), `payload.body`, and `snippet`.

3. For each message:
   - Headers: pull `From`, `To`, `Date`, `Subject` from `payload.headers`.
   - Body: walk `payload.parts[]`; prefer the `text/plain` part. If only `text/html` is present, surface the raw HTML or note `(HTML body — render not implemented in v0.2.0)`.
   - Attachments: any part with `filename != ""` is an attachment.

4. Format Markdown:

   ```
   # <subject>

   ## Message 1: <from> → <to> (<date>)
   <body>

   Attachments:
   - <filename>
   ```

   Subject is taken from the first message's `Subject` header. Omit `Attachments:` section if none.

## Common failure modes

- **404 / thread not found** → invalid `thread_id` or thread deleted. Surface `ERR: thread <thread_id> not found`.
- **HTML-only body** → emit raw HTML with a note; full HTML→text rendering is a v0.2.0 limitation.
- **Auth expired** → see `references/failure-modes.md` § `gws auth`.

## Examples

Input: `thread_id = "18f2c..."` → full thread Markdown.

Input: `thread_url = "https://mail.google.com/mail/u/0/#inbox/18f2c..."` → same, after parsing `thread_id`.
