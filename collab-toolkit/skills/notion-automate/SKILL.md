---
name: notion-automate
description: Notion automation via agent-browser browser-driving (Web mode, headless background after first login). Use for: full-text search across pages and databases, page content fetch with headings/paragraphs/callouts/toggles, database row queries with property extraction, page backlink discovery. Read-only v0.1.0 — search and fetch only, no writes. Notion 自動化、ページ読取、ヘッドレス。Notion 自動化・頁面讀取・無頭背景。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*), Bash(jq:*), Bash(mkdir:*)
---

# notion-automate

Read-only browser automation for Notion. Uses semantic-first selectors over the accessibility tree — never hardcode `@eN` refs.

## Prerequisites

Run `/collab-setup` once. After that:
- `~/.local/bin/abx` is installed and on PATH
- `~/.config/collab-toolkit/config.json` exists with mode + profile config
- Notion is verified logged-in via your daily Chrome (shared mode) or dedicated profile

If any protocol fails with "config not found": run `/collab-setup`.
If any protocol fails with "login wall detected" in title: per setup mode, either log into Notion in your daily Chrome (shared mode) or run `/collab-setup --reauth notion` (dedicated mode).

## Hero protocols

- `protocols/search-workspace.md` — full-text search across pages, databases, and content in the workspace
- `protocols/page-fetch.md` — fetch a page's full content: headings, paragraphs, lists, callouts, toggles
- `protocols/database-query.md` — open a database URL, extract rows with all property cells
- `protocols/page-backlinks.md` — find all pages that link to a target page

## Selector convention

See `references/ui-patterns.md`. All protocols MUST:
1. `ABX_SERVICE=notion abx snapshot -i --json` → save to variable or /tmp
2. `jq '.elements[] | select(.role==X and .name==Y) | .ref' | head -1`
3. Empty result → exit with "UI changed: <role>+<name> not found"

## Failure modes

See `references/failure-modes.md`.

## Output mode

Default: human-readable Markdown summary.
`--json` (passthrough to abx): structured JSON for downstream chaining.
