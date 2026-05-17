---
name: notion-automate
description: Notion automation via agent-browser browser-driving. Use for: search-workspace, page-fetch with embedded blocks, database-query with filter/sort, page-backlinks. Read-only v0.1.6 — search and fetch only, no writes. Supports EN / zh-TW / ja UI labels. Notion 自動化、ページ読取、多言語UI対応。Notion 自動化・頁面讀取・多語言介面支援。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*)
---

# notion-automate

Follows agent-browser text-snapshot conventions. v0.1.6 supports EN / zh-TW / ja UI labels (per-protocol Localized labels tables).

## Prerequisites

`/collab-setup` once. Login wall → reauth.

## Hero protocols

- `protocols/search-workspace.md`
- `protocols/page-fetch.md`
- `protocols/database-query.md`
- `protocols/page-backlinks.md`

## Workflow pattern

```bash
abx open <url>
abx wait --load networkidle
abx snapshot -i
abx click @eN
abx snapshot -i
```

## Failure modes

See `references/failure-modes.md`.
