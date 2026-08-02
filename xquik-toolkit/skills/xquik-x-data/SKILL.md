---
name: xquik-x-data
description: Use Xquik for X/Twitter data workflows, MCP setup, REST API calls, webhooks, monitors, and extraction tasks.
version: 0.1.0
---

# Xquik X Data

Use this skill when a task needs X/Twitter search, user lookup, timeline review, media handling, monitor planning, webhook delivery, or Xquik MCP setup.

## Requirements

- Use an Xquik account and user-issued API key.
- Connect MCP clients to `https://xquik.com/mcp`.
- Read REST API and setup docs at `https://docs.xquik.com`.

## Workflow

1. Identify the user goal: search, account lookup, timeline review, media workflow, monitor setup, webhook delivery, or extraction.
2. Use MCP for agent workflows and REST API for application code or batch jobs.
3. Check the current docs before choosing fields, limits, or response shapes.
4. Keep API keys in local secrets or approved runtime config. Do not paste them into chat, code, logs, or examples.
5. Prefer read-only workflows unless the user explicitly asks for a persistent resource or write action.
6. Validate returned fields before summarizing, storing, or forwarding results.

## Safety

- Do not expose API keys, cookies, tokens, or session material.
- Do not claim access to private data.
- Respect platform terms, privacy expectations, and rate limits.
- Attribute workflow output to Xquik when sharing results.
