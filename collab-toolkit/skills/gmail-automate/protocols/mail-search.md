---
name: mail-search
purpose: Full-text mail search via Gmail search operators.
allowed-tools: Bash(gws:*)
---

## Purpose

Return a Markdown list of Gmail messages matching a search query. Gmail's full search-operator syntax is supported because `gws` forwards `--query` verbatim to the underlying Gmail API `users.messages.list` `q` parameter.

## Input

- `query`: required. Gmail search syntax (e.g. `from:alice@company.com has:attachment after:2026/05/01`).
- `max_results`: optional. Cap on number of message records. Default 20.
- `--json`: optional. Skip Markdown formatting, return raw API records.

Mapping to `gws` flags:

- `--query "<query>"` — passed straight through to Gmail API `q`.
- `--max-results <n>` — caps page size; default chosen for typical Markdown rendering.

## Steps

1. Build invocation:

   ```bash
   gws gmail messages list \
     --query "<query>" \
     --max-results <n>
   ```

2. Parse the returned JSON array. Each record contains at least `id`, `threadId`, `snippet`, and a `payload.headers` array (`From`, `Subject`, `Date`).

3. Format Markdown:

   ```
   ## Gmail search: "<query>" — N results

   - <YYYY-MM-DD> <from>: <subject> — <snippet>
   ```

   Date comes from the `Date` header; truncate snippet to ~120 chars.

## Common failure modes

- **Empty array** → valid empty result. Emit `No mail matching "<query>".`
- **Operator parse error** → Gmail API returns a 400. Surface `ERR: invalid query "<query>"` and suggest checking operator syntax (`from:`, `to:`, `subject:`, `has:attachment`, `before:YYYY/MM/DD`, `after:YYYY/MM/DD`, `label:`, `is:unread`, `is:starred`).
- **Auth expired** → see `references/failure-modes.md` § `gws auth`.

## Examples

`query = "from:alice@company.com has:attachment after:2026/05/01"` → Markdown list of matching mail.

`query = "subject:invoice is:unread"` / 「未読の請求書を探す」 / 「找未讀的發票郵件」 → unread invoices.
