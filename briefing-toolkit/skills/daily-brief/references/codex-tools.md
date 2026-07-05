# Codex CLI — tool name mapping for `daily-brief`

> The per-platform fan-out step phrases dispatch in host-neutral prose.
> For the verified detail on Codex's `multi_agent` primitive
> (`spawn_agent`/`wait_agent`/`close_agent`) see
> `loom-code/skills/using-loom-code/references/codex-tools.md`. This
> file only maps `daily-brief`'s per-platform fan-out onto it and is
> **doc-sourced, not session-exercised** against this plugin.

## Per-platform parallel fan-out

`spawn_agent` once per ready platform (each carrying that platform's
identity token + time window + search angles as its instructions), then
`wait_agent` for all, then `close_agent` once done. Codex's own runtime
handles the wait-for-all/consolidate step automatically once the spawn
instruction names all ready platforms — no "same assistant message"
rule to follow the way Claude Code requires.

## MCP tool availability caveat (applies regardless of host)

This skill's platform searches depend on **interactively-authenticated
MCP connections** (Slack / Asana / Notion via `claude.ai`-style OAuth).
Per this repo's own MCP-server guidance: these connections "may be
absent in headless/cron runs" on **either** host — this is an
interactive-vs-headless distinction, not a Claude-Code-vs-Codex one.
`.claude-plugin/plugin.json`'s description previously said "Claude Code
CLI only," which conflated the two axes; see the CHANGELOG entry for
the correction.
