---
name: asana-automate
description: Asana automation via agent-browser browser-driving (Web mode, headless background after first login). Use for: task-list across projects with filtering, task-detail with subtasks/comments/attachments, project-overview, search-global across tasks and portfolios. Read-only v0.1.6 — search and fetch only, no writes. Supports EN / zh-TW / ja UI labels. Asana 自動化、タスク読取、ヘッドレス、多言語UI対応。Asana 自動化・任務讀取・無頭背景・多語言介面支援。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*)
---

# asana-automate

Read-only browser automation for Asana. Follows agent-browser's official text-snapshot conventions — `abx snapshot -i` produces an indented text tree; read it, identify the ref, click by `@eN`.

## Supported UI languages

v0.1.6 supports **EN, zh-TW (繁體中文), ja (日本語)** UI labels. Each protocol has a `## Localized labels` section listing role+name patterns. Other locales not officially supported — refine via PR.

## Prerequisites

`/collab-setup` once. abx + config + logged-in profile. Login wall → `/collab-setup --reauth asana` (dedicated) or log into daily Chrome (shared).

## Hero protocols

- `protocols/task-list.md` — list My Tasks, filter by due-date / status / project
- `protocols/task-detail.md` — task content with subtasks / comments / attachments
- `protocols/project-overview.md` — list all projects (flat)
- `protocols/search-global.md` — full-text search across tasks / projects / portfolios

## Workflow pattern

```bash
abx open <url>
abx wait --load networkidle
abx snapshot -i           # text output, locale-dependent label names
abx click @eN             # ref from snapshot
abx snapshot -i           # re-snapshot after navigation
```

**Always re-snapshot after a click** — refs reassigned each time.

## Failure modes

See `references/failure-modes.md`.
