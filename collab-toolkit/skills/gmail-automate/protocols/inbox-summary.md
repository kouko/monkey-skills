---
name: inbox-summary
purpose: Summarize INBOX state — recent messages with unread flag.
allowed-tools: Bash(gws:*)
---

## Purpose

Return a Markdown summary of the most recent N messages in `INBOX`, with unread messages highlighted. Replaces v0.1.6's Category-tab scraping — Gmail Category tabs are a UI affordance, not an API concept, so v0.2.0 reports a flat INBOX list and (optionally) per-category breakdowns via additional `label:CATEGORY_*` filters.

## Input

- `limit`: optional. Number of messages to return. Default 20.
- `category`: optional. One of `primary` / `social` / `promotions` / `updates` / `forums`. Maps to Gmail system labels `CATEGORY_PERSONAL` / `CATEGORY_SOCIAL` / `CATEGORY_PROMOTIONS` / `CATEGORY_UPDATES` / `CATEGORY_FORUMS`.
- `--json`: optional. Skip Markdown formatting.

## Steps

1. Build the label list:
   - Always include `INBOX`.
   - If `category` is set, add the matching `CATEGORY_*` label.

2. Call:

   ```bash
   gws gmail messages list \
     --labels INBOX \
     --max-results <limit>
   ```

   Or with a category:

   ```bash
   gws gmail messages list \
     --labels INBOX,CATEGORY_PROMOTIONS \
     --max-results <limit>
   ```

3. Parse the JSON array. Each record exposes `labelIds[]`; `UNREAD` membership indicates an unread message.

4. Format Markdown:

   ```
   ## Inbox Summary (N messages, M unread)

   - [unread] <YYYY-MM-DD> <from>: <subject>
   - <YYYY-MM-DD> <from>: <subject>
   ```

   Prefix unread rows with `[unread]`. Date and from come from `payload.headers`.

## Common failure modes

- **Empty array** → valid, emit `Inbox empty.`
- **Unknown category** → surface `ERR: unknown category "<category>"; expected one of primary/social/promotions/updates/forums`.
- **Auth expired** → see `references/failure-modes.md` § `gws auth`.

## Examples

`limit = 10` → 10 most recent INBOX messages.

`limit = 5, category = "promotions"` → 5 most recent promotional messages.
