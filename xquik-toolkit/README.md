# Xquik Toolkit

Source-aware X/Twitter workflows for Claude Code and Codex. The plugin ships a
shared Skill and auto-registers Xquik's first-party remote MCP server.

## Install

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install xquik-toolkit@monkey-skills
```

Use the repository's [Codex installation guide](../.codex/INSTALL.md) for Codex.

## Source Truth

- Docs: https://docs.xquik.com
- OpenAPI: https://xquik.com/openapi.json
- MCP manifest: https://xquik.com/.well-known/mcp.json
- MCP endpoint: https://xquik.com/mcp
- SDK guides: https://docs.xquik.com/sdks
- Source: https://github.com/Xquik-dev/x-twitter-scraper

The MCP server uses OAuth 2.1 discovery. Use a scoped Xquik API key only when a
client cannot complete OAuth. Never print, commit, or paste credentials into a
prompt.

## Workflow

Use `xquik-x-data` to select a current REST operation, remote MCP route, SDK,
extraction, monitor, or signed webhook. Bounded public reads stay narrow.
Private reads, persistent resources, metered bulk jobs, event delivery, media,
and account actions require exact user approval.

Xquik is an independent third-party service. Not affiliated with X Corp.
"Twitter" and "X" are trademarks of X Corp.
