# Codex CLI — tool name mapping for `report-equity-memo`

> Phase 2.5's peer-discovery step names Claude Code's `general-purpose`
> subagent type directly. This file maps that onto Codex and is
> **doc-sourced, not session-exercised** against this plugin. See
> `loom-code/skills/using-loom-code/references/codex-tools.md` for the
> verified detail on Codex's `multi_agent` primitive
> (`spawn_agent`/`wait_agent`/`close_agent`).

## Peer-discovery dispatch

`spawn_agent` with the Phase 2.5 prompt template (anchor_ticker +
company_name) as the agent's instructions, then `wait_agent` for the
JSON peer list, then `close_agent`.

## Agent-type mapping

Codex ships built-in agents `default` (general-purpose fallback),
`worker` (execution-focused), and `explorer` (read-heavy codebase
exploration). Peer discovery is judgment over external market/company
knowledge, not codebase exploration — spawn with `default` (or a custom
general-reasoning agent profile), **not** `explorer`; `explorer`'s
narrower framing risks refusing the reasoning role outright (this
mapping is this file's own inference, not manual-stated — the manual
documents the three built-ins generically, not this skill's specific
use case).
