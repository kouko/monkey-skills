---
name: asana-automate
description: Asana automation via agent-browser browser-driving (Web mode, headless background after first login). Use for: task-list across projects with filtering, task-detail with subtasks/comments/attachments, project-overview with section counts, search-global across tasks and portfolios. Read-only v0.1.0 — search and fetch only, no writes. Asana 自動化、タスク読取、ヘッドレス。Asana 自動化・任務讀取・無頭背景。
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*), Bash(abx:*), Bash(jq:*), Bash(mkdir:*)
---

# asana-automate

Read-only browser automation for Asana. Uses semantic-first selectors over the accessibility tree — never hardcode `@eN` refs.

## Prerequisites

Run `/collab-setup` once. After that:
- `~/.local/bin/abx` is installed and on PATH
- `~/.config/collab-toolkit/config.json` exists with mode + profile config
- Asana is verified logged-in via your daily Chrome (shared mode) or dedicated profile

If any protocol fails with "config not found": run `/collab-setup`.
If any protocol fails with "login wall detected" in title: per setup mode, either log into Asana in your daily Chrome (shared mode) or run `/collab-setup --reauth asana` (dedicated mode).

## Hero protocols

- `protocols/task-list.md` — list My Tasks across projects, filterable by due-date, status, custom field
- `protocols/task-detail.md` — full task content with subtasks, comments, attachments, custom field values
- `protocols/project-overview.md` — list all projects with sections, task counts, recent activity
- `protocols/search-global.md` — full-text search across tasks, projects, portfolios with filters

## Selector convention

See `references/ui-patterns.md`. All protocols MUST:
1. `ABX_SERVICE=asana abx snapshot -i --json` → save to /tmp
2. `jq '.elements[] | select(.role==X and .name==Y) | .ref' | head -1`
3. Empty result → exit with "UI changed: <role>+<name> not found"

## Failure modes

See `references/failure-modes.md`.

## Output mode

Default: human-readable Markdown summary.
`--json` (passthrough to abx): structured JSON for downstream chaining.
